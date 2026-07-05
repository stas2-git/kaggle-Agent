"""Shared review service for CLI, tests, and future ADK/FastAPI adapters."""

from __future__ import annotations

import random
from pathlib import Path

from portfolio_agent.config import PortfolioAgentConfig, load_config
from portfolio_agent.reporting import compile_markdown_report
from portfolio_agent.schemas import (
    AnomalyRecord,
    DriverResult,
    FindingDetail,
    PortfolioReviewResult,
    ReviewMemo,
)
from portfolio_agent.tracing import TraceLogger
from portfolio_agent.tools import (
    calculate_portfolio_metrics,
    detect_anomalies,
    investigate_anomaly_drivers,
    load_portfolio_data,
    validate_portfolio_data,
)


def _data_quality_summary(errors: list[str], warnings: list[str]) -> dict:
    return {
        "errors": len(errors),
        "warnings": len(warnings),
        "error_messages": errors,
        "warning_messages": warnings,
        "null_warnings": "Null cells present" if any("Null" in w for w in warnings) else None,
        "injection_warnings": (
            "Prompt injection signature detected"
            if any("injection" in w.lower() for w in warnings)
            else None
        ),
        "non_numeric": "Non-numeric types" if any("non-numeric" in w for w in warnings) else None,
    }


def _human_review_reasons(anomalies: list[AnomalyRecord], warnings: list[str]) -> list[str]:
    reasons: list[str] = []
    if any(a.severity == "high" for a in anomalies):
        reasons.append("high_severity_anomaly")
    if any(a.requires_human_review for a in anomalies):
        reasons.append("deterministic_threshold_requires_review")
    if warnings:
        reasons.append("data_quality_warnings")
    return list(dict.fromkeys(reasons))


def _offline_review_memo(
    *,
    valuation_month: str,
    anomalies: list[AnomalyRecord],
    driver_results: list[DriverResult],
    data_quality_summary: dict,
) -> ReviewMemo:
    """Create deterministic narrative text with no model/client call."""

    if anomalies:
        summary = (
            f"[OFFLINE MODE] Deterministic review for {valuation_month} detected "
            f"{len(anomalies)} anomaly/anomalies. The memo is generated from tool "
            "outputs only; no model call was made."
        )
    else:
        summary = (
            f"[OFFLINE MODE] Deterministic review for {valuation_month} found no "
            "threshold anomalies. The memo is generated from tool outputs only; "
            "no model call was made."
        )

    findings: list[FindingDetail] = []
    for anomaly in anomalies:
        related_drivers = [d for d in driver_results if d.anomaly_id == anomaly.anomaly_id]
        if related_drivers:
            driver_bits = []
            for driver in related_drivers:
                top = driver.top_contributors[0] if driver.top_contributors else None
                if top:
                    driver_bits.append(
                        f"{driver.dimension}={top.value} contributed "
                        f"{top.contribution_to_change:+.4f}"
                    )
            driver_text = "; ".join(driver_bits) or "No dominant driver was isolated."
        else:
            driver_text = "No granular drivers investigated."

        findings.append(
            FindingDetail(
                anomaly_id=anomaly.anomaly_id,
                metric=anomaly.metric,
                segment=anomaly.business_segment,
                observations=f"{anomaly.explanation} Driver evidence: {driver_text}",
                likely_cause_hypothesis=(
                    "Offline mode does not infer external causes. Treat the driver "
                    "pattern as a hypothesis requiring actuarial or underwriting review."
                ),
            )
        )

    followups = [
        "Review deterministic anomaly flags and driver slices with the portfolio owner.",
        "Confirm whether any data-quality warnings affect interpretation.",
    ]
    if data_quality_summary.get("injection_warnings"):
        followups.append("Investigate suspicious note fields before relying on narrative text.")

    return ReviewMemo(
        valuation_month=valuation_month,
        executive_summary=summary,
        finding_details=findings,
        recommended_followups=followups,
        confidence=4.0 if not data_quality_summary.get("warnings") else 3.0,
        requires_human_review=bool(
            any(a.requires_human_review for a in anomalies)
            or data_quality_summary.get("warnings")
        ),
    )


def review_portfolio(
    *,
    input_path: str,
    latest_month: str,
    model_name: str | None = None,
    user_prompt: str | None = None,
    force_offline: bool = False,
    run_id: str | None = None,
    config: PortfolioAgentConfig | None = None,
) -> PortfolioReviewResult:
    """Run a portfolio review through the shared service boundary."""

    cfg = config or load_config(model_name=model_name, force_offline=force_offline)
    run_id = run_id or f"{random.randint(100, 999)}"

    trace = TraceLogger(run_id=run_id, dataset_path=input_path)
    trace.log_event(
        "pipeline_start",
        {
            "valuation_month": latest_month,
            "model": cfg.model_name,
            "execution_mode": cfg.execution_mode,
            "threshold_profile": cfg.threshold_profile,
        },
    )
    trace.set_metadata("execution_mode", cfg.execution_mode)
    trace.set_metadata("application", cfg.application_name)

    df = load_portfolio_data(input_path, workspace_root=str(cfg.project_root))
    trace.log_event("data_loaded", {"row_count": len(df)})

    df, errors, warnings = validate_portfolio_data(df)
    trace.log_event("data_validated", {"errors": errors, "warnings": warnings})
    dq_summary = _data_quality_summary(errors, warnings)

    if errors:
        trace.set_metadata("run_status", "FAILED")
        trace.set_metadata("failure_reason", f"Validation errors: {errors}")
        saved_trace_file = trace.save_trace(str(cfg.traces_dir))
        raise ValueError(f"Validation errors: {errors}. Trace: {saved_trace_file}")

    metrics = calculate_portfolio_metrics(df)
    trace.log_event("metrics_calculated", {"metric_records_count": len(metrics)})

    anomalies = detect_anomalies(metrics, latest_month)
    trace.log_event("anomalies_detected", {"anomalies_count": len(anomalies)})

    driver_results: list[DriverResult] = []
    for anomaly in anomalies:
        drivers = investigate_anomaly_drivers(df, anomaly)
        driver_results.extend(drivers)
        trace.log_event(
            "drivers_investigated",
            {
                "anomaly_id": anomaly.anomaly_id,
                "dimensions_sliced": [d.dimension for d in drivers],
            },
        )

    if cfg.execution_mode == "offline":
        trace.log_event("offline_synthesis_started", {"model_call": False})
        memo = _offline_review_memo(
            valuation_month=latest_month,
            anomalies=anomalies,
            driver_results=driver_results,
            data_quality_summary=dq_summary,
        )
        trace.log_event(
            "findings_synthesized",
            {
                "mode": "offline",
                "confidence": memo.confidence,
                "requires_human_review": memo.requires_human_review,
            },
        )
    else:
        from portfolio_agent.agent import synthesize_review_findings

        trace.log_event("model_synthesis_started", {"model": cfg.model_name})
        memo = synthesize_review_findings(
            valuation_month=latest_month,
            anomalies=anomalies,
            driver_results=driver_results,
            data_quality_summary=dq_summary,
            model_name=cfg.model_name,
            user_prompt_override=user_prompt,
        )
        trace.log_event(
            "findings_synthesized",
            {
                "mode": "online",
                "confidence": memo.confidence,
                "requires_human_review": memo.requires_human_review,
            },
        )

    trace_path = Path(cfg.traces_dir) / f"run_trace_{run_id}.json"
    report_file = compile_markdown_report(
        memo=memo,
        anomalies=anomalies,
        driver_results=driver_results,
        data_quality_summary=dq_summary,
        run_id=run_id,
        dataset_path=input_path,
        trace_path=str(trace_path),
        metrics_records=metrics,
        output_dir=str(cfg.reports_dir),
    )
    trace.log_event("report_generated", {"report_path": str(report_file)})

    human_review_reasons = _human_review_reasons(anomalies, warnings)
    trace.set_metadata("run_status", "COMPLETE")
    trace.set_metadata("overall_severity", "High" if memo.requires_human_review else "Low")
    trace.set_metadata("requires_human_review", memo.requires_human_review)
    trace.set_metadata("human_review_reasons", human_review_reasons)
    trace.set_metadata("report_path", str(report_file))

    saved_trace_file = trace.save_trace(str(cfg.traces_dir))

    return PortfolioReviewResult(
        run_id=run_id,
        valuation_month=latest_month,
        execution_mode=cfg.execution_mode,
        status="complete",
        requires_human_review=memo.requires_human_review,
        human_review_reasons=human_review_reasons,
        anomaly_count=len(anomalies),
        report_path=str(report_file),
        trace_path=str(saved_trace_file),
        memo=memo,
    )
