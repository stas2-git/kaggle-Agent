import os
from pathlib import Path
from typing import List, Dict, Any
from portfolio_agent.core.schemas import ReviewMemo, AnomalyRecord, DriverResult, MetricsRecord

def compile_markdown_report(
    memo: ReviewMemo,
    anomalies: List[AnomalyRecord],
    driver_results: List[DriverResult],
    data_quality_summary: Dict[str, Any],
    run_id: str,
    dataset_path: str,
    trace_path: str,
    metrics_records: List[MetricsRecord],
    output_dir: str = "outputs/reports"
) -> Path:
    """
    Compile the synthesized memo and tool findings into a formal Markdown report.
    Saves the file in outputs/reports/ and returns the Path.
    """
    # 1. Create output folder
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    filename = f"portfolio_review_{memo.valuation_month.replace('-', '_')}_{run_id}.md"
    report_file = out_path / filename

    # 2. Determine overall run status based on anomalies
    severities = [a.severity for a in anomalies]
    overall_status = "Green"
    if "high" in severities:
        overall_status = "High Anomaly"
    elif "moderate" in severities:
        overall_status = "Moderate Anomaly"

    # 3. Find latest metrics for the summary table
    latest_metrics = [m for m in metrics_records if m.valuation_month == memo.valuation_month]
    # We aggregate all segments for the summary table (or take the primary segment if only one)
    if len(latest_metrics) == 1:
        m_cur = latest_metrics[0]
    else:
        # If multiple, take the first one or sum/average them. For the vertical slice, it's just one segment.
        m_cur = latest_metrics[0] if latest_metrics else None

    # Find prior metrics for comparison
    prior_month = ""
    try:
        yr, mo = map(int, memo.valuation_month.split("-"))
        prior_month = f"{yr - 1:04d}-12" if mo == 1 else f"{yr:04d}-{mo - 1:02d}"
    except Exception:
        pass
    prior_metrics = [m for m in metrics_records if m.valuation_month == prior_month]
    m_pri = prior_metrics[0] if prior_metrics else None

    # Helper function to print values
    def fmt_val(v: Any, is_pct: bool = False, is_curr: bool = False) -> str:
        if v is None:
            return "N/A"
        if is_pct:
            return f"{v * 100:.1f}%"
        if is_curr:
            return f"${v:,.0f}"
        if isinstance(v, float):
            return f"{v:.2f}"
        return str(v)

    # Helper function to print changes
    def fmt_chg(cur_val: Any, pri_val: Any, is_pct: bool = False, is_curr: bool = False) -> str:
        if cur_val is None or pri_val is None:
            return "N/A"
        diff = cur_val - pri_val
        sign = "+" if diff >= 0 else "-"
        abs_diff = abs(diff)
        if is_pct:
            return f"{sign}{abs_diff * 100:.1f}%"
        if is_curr:
            return f"{sign}${abs_diff:,.0f}"
        return f"{sign}{abs_diff:.2f}"

    # Build data quality table values
    dq_overall = "PASS" if not data_quality_summary.get("errors") else "FAIL"
    if data_quality_summary.get("warnings") and dq_overall == "PASS":
        dq_overall = "PASS WITH WARNINGS"

    # Start writing markdown string
    md = f"""# Monthly Portfolio Review Report

## Header

**Portfolio:** Actuarial Commercial Book  
**Valuation month:** {memo.valuation_month}  
**Run ID:** {run_id}  
**Status:** {overall_status}  
**Human review required:** {"Yes" if memo.requires_human_review else "No"}

## Executive summary

{memo.executive_summary}

## Data quality summary

| Check | Status | Notes |
|---|---|---|
| Required columns | {"PASS" if "missing_cols" not in data_quality_summary else "FAIL"} | {", ".join(data_quality_summary.get("missing_cols", [])) or "All columns present."} |
| Numeric fields | {"PASS" if not data_quality_summary.get("non_numeric") else "FAIL"} | {data_quality_summary.get("non_numeric", "Valid formats.")} |
| Missing values | {"WARNING" if data_quality_summary.get("null_warnings") else "PASS"} | {data_quality_summary.get("null_warnings") or "No nulls in key fields."} |
| Suspicious text fields | {"WARNING" if data_quality_summary.get("injection_warnings") else "PASS"} | {data_quality_summary.get("injection_warnings") or "No injections found."} |
| Overall validation | {dq_overall} | See validation detail logs. |

## Key metric movement

| Metric | Current ({memo.valuation_month}) | Prior ({prior_month}) | Change | Severity |
|---|---:|---:|---:|---|
"""
    if m_cur and m_pri:
        md += f"| Written premium | {fmt_val(m_cur.written_premium, is_curr=True)} | {fmt_val(m_pri.written_premium, is_curr=True)} | {fmt_chg(m_cur.written_premium, m_pri.written_premium, is_curr=True)} | - |\n"
        md += f"| Earned premium | {fmt_val(m_cur.earned_premium, is_curr=True)} | {fmt_val(m_pri.earned_premium, is_curr=True)} | {fmt_chg(m_cur.earned_premium, m_pri.earned_premium, is_curr=True)} | - |\n"
        md += f"| Incurred loss | {fmt_val(m_cur.incurred_loss, is_curr=True)} | {fmt_val(m_pri.incurred_loss, is_curr=True)} | {fmt_chg(m_cur.incurred_loss, m_pri.incurred_loss, is_curr=True)} | - |\n"
        md += f"| Loss ratio | {fmt_val(m_cur.loss_ratio, is_pct=True)} | {fmt_val(m_pri.loss_ratio, is_pct=True)} | {fmt_chg(m_cur.loss_ratio, m_pri.loss_ratio, is_pct=True)} | {overall_status} |\n"
        md += f"| Claim count | {fmt_val(m_cur.claim_count)} | {fmt_val(m_pri.claim_count)} | {fmt_chg(m_cur.claim_count, m_pri.claim_count)} | - |\n"
        md += f"| Rate change | {fmt_val(m_cur.rate_change_pct, is_pct=True)} | {fmt_val(m_pri.rate_change_pct, is_pct=True)} | {fmt_chg(m_cur.rate_change_pct, m_pri.rate_change_pct, is_pct=True)} | - |\n"
        md += f"| Benchmark adequacy | {fmt_val(m_cur.benchmark_adequacy)} | {fmt_val(m_pri.benchmark_adequacy)} | {fmt_chg(m_cur.benchmark_adequacy, m_pri.benchmark_adequacy)} | - |\n"
        md += f"| Average retention | {fmt_val(m_cur.avg_retention, is_curr=True)} | {fmt_val(m_pri.avg_retention, is_curr=True)} | {fmt_chg(m_cur.avg_retention, m_pri.avg_retention, is_curr=True)} | - |\n"
    else:
        md += "| No metrics available for comparison. | | | | |\n"

    md += """
## Material findings
"""

    for i, detail in enumerate(memo.finding_details, 1):
        anomaly = next((a for a in anomalies if a.anomaly_id == detail.anomaly_id), None)
        drivers = [d for d in driver_results if d.anomaly_id == detail.anomaly_id]
        
        md += f"""
### Finding {i}: {detail.segment} {detail.metric.replace('_', ' ').title()} Anomaly

**Metric:** {detail.metric}  
**Severity:** {anomaly.severity if anomaly else "unknown"}  
**Current:** {fmt_val(anomaly.current_value, is_pct=(anomaly.metric=='loss_ratio')) if anomaly else "N/A"}  
**Prior:** {fmt_val(anomaly.prior_value, is_pct=(anomaly.metric=='loss_ratio')) if anomaly else "N/A"}  
**Change:** {fmt_chg(anomaly.current_value, anomaly.prior_value, is_pct=(anomaly.metric=='loss_ratio')) if anomaly else "N/A"}  

**Evidence:**  
{anomaly.explanation if anomaly else "Calculated threshold breach flagged by tools."}

**Driver investigation:**  
"""
        if drivers:
            for d in drivers:
                md += f"* **By {d.dimension}**:\n"
                for c in d.top_contributors[:3]:
                    # Format value contribution
                    md += f"  * `{c.value}`: contrib={c.contribution_to_change*100:+.1f} pts (current={fmt_val(c.current_value, is_pct=(anomaly.metric=='loss_ratio'))}, prior={fmt_val(c.prior_value, is_pct=(anomaly.metric=='loss_ratio'))})\n"
        else:
            md += "No granular drivers investigated.\n"

        md += f"""
**Interpretation:**  
{detail.observations}

**Hypothesis:**  
{detail.likely_cause_hypothesis}
"""

    md += f"""
## Recommended follow-up
"""
    for q in memo.recommended_followups:
        md += f"- {q}\n"

    md += f"""
## Human review gate

**Review required:** {"Yes" if memo.requires_human_review else "No"}

**Reasons:**
"""
    if memo.requires_human_review:
        if "high" in severities:
            md += "- Severe anomaly threshold breach detected.\n"
        if data_quality_summary.get("warnings"):
            md += "- Data quality warnings present (e.g. potential prompt injections or negative columns).\n"
        if memo.confidence < 3.0:
            md += "- Agent confidence is below target threshold.\n"
        if not severities and not data_quality_summary.get("warnings"):
            md += "- Escalated due to high-impact recommendation logic.\n"
    else:
        md += "- Metrics are within normal threshold parameters. Data quality is clean.\n"

    md += f"""
## Trace and reproducibility

- Trace file: `{trace_path}`
- Dataset: `{dataset_path}`
- Threshold profile: Default Actuarial Config

## Disclaimer

This report is generated from synthetic/demo data for a capstone project. It is a first-pass monitoring aid and does not represent a formal actuarial opinion, underwriting action, pricing decision, or reserving recommendation.
"""

    report_file.write_text(md.strip(), encoding="utf-8")
    return report_file
