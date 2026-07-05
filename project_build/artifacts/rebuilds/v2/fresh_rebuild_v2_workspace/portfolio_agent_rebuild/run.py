"""Deterministic offline orchestrator (CLI adapter).

Per 10_core/02_agent_architecture.md the CLI/FastAPI adapters "invoke the same
application service" and "may not contain actuarial calculations, threshold
logic, prompt policy, or report-validation rules" -- those live in tools.py,
schemas.py, security.py. This module only sequences tool calls, matching the
workflow states table in 02_agent_architecture.md:

receive_request -> load_data -> validate_data -> calculate_metrics ->
detect_anomalies -> investigate_drivers -> synthesize_findings -> review_gate ->
generate_report -> record_trace

There is no live google-adk / LLM in this rebuild (offline_contract in
02_tool_contracts.yaml: "model_or_network_initialization_allowed: false",
"synthesis: deterministic_template"). `synthesize_review_findings` below is the
deterministic template stand-in for the ADK synthesis node.
"""

from __future__ import annotations

import argparse
import datetime
import os
import uuid
from typing import Any

from .reporting import generate_report, overall_severity
from .schemas import Anomaly, DriverResult, HumanReviewDecision, PortfolioReviewResult
from .tools import (
    RunContext,
    calculate_portfolio_metrics,
    calculate_portfolio_totals,
    detect_anomalies,
    investigate_anomaly_drivers,
    load_portfolio_data,
    validate_portfolio_data,
)
from .tracing import write_trace

APP_NAME = "portfolio_agent_rebuild"
ROOT_AGENT_NAME = "portfolio_monitor_agent"


def synthesize_review_findings(
    anomalies: list[Anomaly], driver_results_by_anomaly: dict[str, list[DriverResult]], data_quality: dict
) -> dict[str, Any]:
    """Deterministic-template stand-in for the LLM synthesis tool (offline mode)."""
    if not anomalies:
        summary = "No material findings were detected against configured thresholds."
    else:
        top = anomalies[0]
        summary = (
            f"{top.severity.title()} severity {top.metric.replace('_', ' ')} movement detected in "
            f"{top.business_segment} ({top.prior_value:.4f} -> {top.current_value:.4f})."
        )
    requires_human_review = any(a.severity == "high" for a in anomalies) or bool(
        data_quality.get("warnings")
    ) and any("suspicious_text" in w for w in data_quality.get("warnings", []))
    return {
        "executive_summary": summary,
        "confidence": 0.9 if len(anomalies) <= 1 else 0.6,
        "requires_human_review": requires_human_review or any(a.severity == "high" for a in anomalies),
    }


def human_review_gate(anomalies: list[Anomaly], data_quality: dict, security_flags: list[dict]) -> HumanReviewDecision:
    reasons = []
    if any(a.severity == "high" for a in anomalies):
        reasons.append("high_severity_anomaly")
    if security_flags:
        reasons.append("prompt_injection_detected")
    if data_quality.get("status") == "fail":
        reasons.append("blocking_data_quality_failure")
    moderate_count = sum(1 for a in anomalies if a.severity == "moderate")
    if moderate_count >= 2:
        reasons.append("multiple_moderate_anomalies_low_confidence")
    required = len(reasons) > 0
    return HumanReviewDecision(
        required=required,
        reasons=reasons,
        status="pending" if required else "not_required",
        recommended_reviewer="actuary_or_portfolio_owner" if required else None,
        review_questions=(
            [
                "Is the change driven by one-off large loss activity or a data artifact?",
                "Did exposure mix or segment composition change materially?",
            ]
            if required
            else []
        ),
    )


def run_review(
    workspace_root: str,
    input_path: str,
    latest_month: str | None,
    execution_mode: str = "offline",
    threshold_profile: str = "default",
    dimensions: list[str] | None = None,
) -> PortfolioReviewResult:
    run_id = uuid.uuid4().hex[:8]
    session_id = f"session_{run_id}"
    started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    ctx = RunContext(workspace_root=workspace_root)

    load_result = load_portfolio_data(input_path, ctx)
    dataframe_ref = load_result["dataframe_ref"]

    validation = validate_portfolio_data(dataframe_ref, ctx)
    data_quality = validation

    anomalies: list[Anomaly] = []
    driver_results_by_anomaly: dict[str, list[DriverResult]] = {}
    portfolio_totals: dict[str, Any] = {}
    final_status = "success"
    report_path = None
    trace_path_rel = f"outputs/traces/run_{run_id}.json"

    if validation["status"] == "fail":
        final_status = "validation_failed"
        human_review = HumanReviewDecision(required=False, status="not_required")
        summary = f"Validation failed: {validation['blocking_errors']}"
    else:
        segment_metrics = calculate_portfolio_metrics(
            dataframe_ref, ["valuation_month", "business_segment"], ctx
        )
        portfolio_totals = calculate_portfolio_totals(dataframe_ref, ctx)
        months = sorted(portfolio_totals.keys())
        latest = latest_month or months[-1]
        if latest not in months or months.index(latest) == 0:
            raise ValueError("no_comparison_period: need at least two valuation months before latest_month")
        prior = months[months.index(latest) - 1]

        # Portfolio-wide totals feed a synthetic metrics_ref so detect_anomalies
        # can operate on the headline comparison (see calculate_portfolio_totals docstring).
        totals_ref = ctx.new_ref("totals")
        ctx.metrics[totals_ref] = [portfolio_totals[m] for m in months]
        unique_segments = set(ctx.dataframes[dataframe_ref]["business_segment"].unique())
        segment_label = next(iter(unique_segments)) if len(unique_segments) == 1 else "ALL_SEGMENTS"

        anomaly_result = detect_anomalies(
            totals_ref, latest, ctx, business_segment_label=segment_label
        )
        anomalies = ctx.anomalies[anomaly_result["anomaly_ref"]]

        default_dims = dimensions or ["business_segment", "coverage", "state", "policy_year", "underwriter"]
        for anomaly in anomalies:
            driver_result = investigate_anomaly_drivers(
                dataframe_ref, anomaly, default_dims, ctx, latest, prior
            )
            driver_results_by_anomaly[anomaly.anomaly_id] = ctx.drivers[driver_result["driver_ref"]]

        synthesis = synthesize_review_findings(anomalies, driver_results_by_anomaly, data_quality)
        human_review = human_review_gate(anomalies, data_quality, ctx.security_flags)
        ctx.log_event(
            "review_gate",
            "human_review_gate",
            output_summary=human_review.to_dict(),
        )

        report_path_rel = f"outputs/reports/portfolio_review_{latest}_{run_id}.md"
        generate_report(
            run_id=run_id,
            valuation_month=latest,
            prior_month=prior,
            portfolio_current=portfolio_totals[latest],
            portfolio_prior=portfolio_totals[prior],
            data_quality=data_quality,
            anomalies=anomalies,
            driver_results_by_anomaly=driver_results_by_anomaly,
            human_review=human_review,
            trace_path=trace_path_rel,
            dataset_path=input_path,
            threshold_profile=threshold_profile,
            workspace_root=workspace_root,
            report_path=report_path_rel,
        )
        report_path = report_path_rel
        summary = synthesis["executive_summary"]

    completed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    trace_abs = write_trace(
        run_id=run_id,
        session_id=session_id,
        app_name=APP_NAME,
        root_agent=ROOT_AGENT_NAME,
        started_at=started_at,
        completed_at=completed_at,
        user_prompt="Run the monthly portfolio review.",
        input_dataset=input_path,
        config={
            "latest_month": latest_month,
            "threshold_profile": threshold_profile,
            "execution_mode": execution_mode,
            "model": None,
        },
        events=ctx.events,
        data_quality=data_quality,
        anomalies=[a.to_dict() for a in anomalies],
        driver_results=[d.to_dict() for lst in driver_results_by_anomaly.values() for d in lst],
        security_flags=ctx.security_flags,
        human_review=human_review.to_dict(),
        final_report_path=report_path,
        final_status=final_status,
        workspace_root=workspace_root,
        trace_path=trace_path_rel,
    )

    return PortfolioReviewResult(
        run_id=run_id,
        session_id=session_id,
        status=final_status,
        execution_mode=execution_mode,
        report_path=report_path,
        trace_path=trace_path_rel,
        anomalies=anomalies,
        human_review=human_review,
        summary=summary,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the rebuilt portfolio monitoring review (offline).")
    parser.add_argument("--input", required=True, help="Path to CSV, relative to workspace root or absolute.")
    parser.add_argument("--latest-month", default=None)
    parser.add_argument("--force-offline", action="store_true", default=True)
    args = parser.parse_args()

    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    result = run_review(workspace_root, args.input, args.latest_month)

    print("Run complete.")
    severity = overall_severity(result.anomalies)
    print(f"Severity: {severity.title()}")
    print(f"Human review required: {'Yes' if result.human_review.required else 'No'}")
    if result.anomalies:
        top = result.anomalies[0]
        print(
            f"Top finding: {top.metric.replace('_', ' ').title()} in {top.business_segment} "
            f"moved from {top.prior_value:.4f} to {top.current_value:.4f}."
        )
    else:
        print("Top finding: No material findings detected.")
    print(f"Report: {result.report_path}")
    print(f"Trace: {result.trace_path}")


if __name__ == "__main__":
    main()
