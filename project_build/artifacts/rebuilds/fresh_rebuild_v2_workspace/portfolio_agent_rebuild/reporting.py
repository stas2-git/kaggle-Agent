"""Markdown report generation per spec_files/20_contracts/04_output_report_template.md."""

from __future__ import annotations

import os
from typing import Any

from .schemas import Anomaly, DriverResult, HumanReviewDecision, MetricsRecord
from .security import validate_report_path

SEVERITY_TO_STATUS = {"low": "Green", "moderate": "Moderate", "high": "High"}


def _fmt_money(v: float) -> str:
    return f"{v:,.0f}"


def _fmt_pct(v: float | None) -> str:
    if v is None:
        return "n/a"
    return f"{v * 100:.1f}%"


def overall_severity(anomalies: list[Anomaly]) -> str:
    if any(a.severity == "high" for a in anomalies):
        return "high"
    if any(a.severity == "moderate" for a in anomalies):
        return "moderate"
    return "low"


def generate_report(
    run_id: str,
    valuation_month: str,
    prior_month: str,
    portfolio_current: MetricsRecord,
    portfolio_prior: MetricsRecord,
    data_quality: dict[str, Any],
    anomalies: list[Anomaly],
    driver_results_by_anomaly: dict[str, list[DriverResult]],
    human_review: HumanReviewDecision,
    trace_path: str,
    dataset_path: str,
    threshold_profile: str,
    workspace_root: str,
    report_path: str,
) -> str:
    validate_report_path(report_path, workspace_root)
    severity = overall_severity(anomalies)
    status_label = SEVERITY_TO_STATUS[severity]

    lines: list[str] = []
    lines.append("# Monthly Portfolio Review Report")
    lines.append("")
    lines.append("## Header")
    lines.append("")
    lines.append("**Portfolio:** Synthetic Portfolio  ")
    lines.append(f"**Valuation month:** {valuation_month}  ")
    lines.append(f"**Run ID:** {run_id}  ")
    lines.append(f"**Status:** {status_label}  ")
    lines.append(f"**Human review required:** {'Yes' if human_review.required else 'No'}")
    lines.append("")
    lines.append("## Executive summary")
    lines.append("")
    if anomalies:
        for a in anomalies[:3]:
            lines.append(
                f"- {a.metric.replace('_', ' ').title()} moved from {a.prior_value:.4f} to "
                f"{a.current_value:.4f} in {a.business_segment} ({a.severity} severity)."
            )
    else:
        lines.append("- No material findings were detected against configured thresholds.")
    lines.append("")

    lines.append("## Data quality summary")
    lines.append("")
    lines.append("| Check | Status | Notes |")
    lines.append("|---|---|---|")
    lines.append(f"| Required columns | {data_quality.get('column_status', 'pass')} | |")
    lines.append(f"| Numeric fields | {data_quality.get('numeric_status', 'pass')} | |")
    warnings = data_quality.get("warnings", [])
    lines.append(
        f"| Missing values | {'warnings' if any('null' in w for w in warnings) else 'pass'} | "
        f"{'; '.join(w for w in warnings if 'null' in w)} |"
    )
    suspicious = [w for w in warnings if "suspicious_text" in w]
    lines.append(f"| Suspicious text fields | {'flagged' if suspicious else 'pass'} | {'; '.join(suspicious)} |")
    lines.append(f"| Overall validation | {data_quality.get('status', 'pass')} | |")
    lines.append("")

    lines.append("## Key metric movement")
    lines.append("")
    lines.append("| Metric | Current | Prior | Change | Severity |")
    lines.append("|---|---:|---:|---:|---|")

    def sev_for(metric_key: str) -> str:
        for a in anomalies:
            if a.metric == metric_key:
                return a.severity
        return "low"

    lines.append(
        f"| Written premium | {_fmt_money(portfolio_current.written_premium)} | "
        f"{_fmt_money(portfolio_prior.written_premium)} | "
        f"{_fmt_money(portfolio_current.written_premium - portfolio_prior.written_premium)} | "
        f"{sev_for('written_premium')} |"
    )
    lines.append(
        f"| Earned premium | {_fmt_money(portfolio_current.earned_premium)} | "
        f"{_fmt_money(portfolio_prior.earned_premium)} | "
        f"{_fmt_money(portfolio_current.earned_premium - portfolio_prior.earned_premium)} | - |"
    )
    lines.append(
        f"| Incurred loss | {_fmt_money(portfolio_current.incurred_loss)} | "
        f"{_fmt_money(portfolio_prior.incurred_loss)} | "
        f"{_fmt_money(portfolio_current.incurred_loss - portfolio_prior.incurred_loss)} | - |"
    )
    lines.append(
        f"| Loss ratio | {_fmt_pct(portfolio_current.loss_ratio)} | {_fmt_pct(portfolio_prior.loss_ratio)} | "
        f"{_fmt_pct(portfolio_current.loss_ratio - portfolio_prior.loss_ratio)} | {sev_for('loss_ratio')} |"
    )
    lines.append(
        f"| Claim count | {portfolio_current.claim_count:.0f} | {portfolio_prior.claim_count:.0f} | "
        f"{portfolio_current.claim_count - portfolio_prior.claim_count:.0f} | {sev_for('claim_count')} |"
    )
    lines.append(
        f"| Rate change | {_fmt_pct(portfolio_current.rate_change_pct)} | {_fmt_pct(portfolio_prior.rate_change_pct)} | "
        f"{_fmt_pct(portfolio_current.rate_change_pct - portfolio_prior.rate_change_pct)} | {sev_for('rate_change_pct')} |"
    )
    lines.append(
        f"| Benchmark adequacy | {portfolio_current.benchmark_adequacy:.2f} | {portfolio_prior.benchmark_adequacy:.2f} | "
        f"{portfolio_current.benchmark_adequacy - portfolio_prior.benchmark_adequacy:.2f} | {sev_for('benchmark_adequacy')} |"
    )
    lines.append(
        f"| Average retention | {_fmt_money(portfolio_current.avg_retention)} | {_fmt_money(portfolio_prior.avg_retention)} | "
        f"{_fmt_money(portfolio_current.avg_retention - portfolio_prior.avg_retention)} | {sev_for('avg_retention')} |"
    )
    lines.append("")

    lines.append("## Material findings")
    lines.append("")
    if not anomalies:
        lines.append("No material findings this period.")
    for i, a in enumerate(anomalies, start=1):
        lines.append(f"### Finding {i}: {a.metric.replace('_', ' ').title()} movement in {a.business_segment}")
        lines.append("")
        lines.append(f"**Metric:** {a.metric}  ")
        lines.append(f"**Severity:** {a.severity}  ")
        lines.append(f"**Current:** {a.current_value:.4f}  ")
        lines.append(f"**Prior:** {a.prior_value:.4f}  ")
        lines.append(f"**Change:** {a.absolute_change:.4f}  ")
        lines.append("")
        lines.append("**Evidence:**  ")
        lines.append(f"{a.explanation}")
        lines.append("")
        lines.append("**Driver investigation:**  ")
        drivers = driver_results_by_anomaly.get(a.anomaly_id, [])
        if drivers:
            for dr in drivers:
                for c in dr.top_contributors:
                    lines.append(
                        f"- By {dr.dimension}: `{c.value}` contributed {c.contribution_to_change:+.4f} "
                        f"(from {c.prior_value:.4f} to {c.current_value:.4f})."
                    )
        else:
            lines.append("- No driver investigation was performed for this finding.")
        lines.append("")
        lines.append("**Interpretation:**  ")
        lines.append(
            "This is a first-pass, conservative read of the deterministic tool outputs above; "
            "it is not a conclusion about cause without further review."
        )
        lines.append("")
        lines.append("**Caveats:**  ")
        lines.append("- Based on synthetic/demo data; small sample sizes reduce credibility of driver slices.")
        lines.append("")
        lines.append("**Recommended follow-up:**")
        lines.append("- Is the change driven by one-off large loss activity or a data artifact?")
        lines.append("- Did exposure mix or segment composition change materially?")
        lines.append("")

    lines.append("## Human review gate")
    lines.append("")
    lines.append(f"**Review required:** {'Yes' if human_review.required else 'No'}")
    lines.append("")
    lines.append("**Reasons:**")
    if human_review.reasons:
        for r in human_review.reasons:
            lines.append(f"- {r}")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Trace and reproducibility")
    lines.append("")
    lines.append(f"- Trace file: `{trace_path}`")
    lines.append(f"- Dataset: `{dataset_path}`")
    lines.append(f"- Threshold profile: `{threshold_profile}`")
    lines.append("")

    lines.append("## Disclaimer")
    lines.append("")
    lines.append(
        "This report is generated from synthetic/demo data for a capstone project. It is a "
        "first-pass monitoring aid and does not represent a formal actuarial opinion, "
        "underwriting action, pricing decision, or reserving recommendation."
    )
    lines.append("")

    content = "\n".join(lines)
    abs_path = report_path if os.path.isabs(report_path) else os.path.join(workspace_root, report_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w") as f:
        f.write(content)
    return content
