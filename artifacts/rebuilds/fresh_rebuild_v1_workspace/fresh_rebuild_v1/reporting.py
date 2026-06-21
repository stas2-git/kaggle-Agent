import os
from typing import Dict, Any, List, Optional, Tuple
from fresh_rebuild_v1.schemas import MetricsRecord, Anomaly, DriverResult

def fmt_premium(val: float) -> str:
    if val >= 0:
        return f"${val:,.0f}"
    else:
        return f"-${abs(val):,.0f}"

def fmt_pct(val: float) -> str:
    return f"{val * 100:.1f}%"

def fmt_adequacy(val: float) -> str:
    return f"{val:.2f}"

def fmt_val(metric: str, val: float) -> str:
    if metric in ["written_premium", "earned_premium", "incurred_loss", "avg_retention"]:
        return fmt_premium(val)
    elif metric in ["loss_ratio", "rate_change_pct"]:
        return fmt_pct(val)
    elif metric in ["benchmark_adequacy"]:
        return fmt_adequacy(val)
    elif metric == "claim_count":
        return f"{int(val)}"
    return str(val)

def fmt_chg(metric: str, curr: float, prior: float) -> str:
    diff = curr - prior
    if metric in ["written_premium", "earned_premium", "incurred_loss", "avg_retention"]:
        sign = "+" if diff >= 0 else "-"
        return f"{sign}{fmt_premium(abs(diff))}"
    elif metric in ["loss_ratio", "rate_change_pct"]:
        sign = "+" if diff >= 0 else ""
        return f"{sign}{diff * 100:.1f}%"
    elif metric in ["benchmark_adequacy"]:
        sign = "+" if diff >= 0 else ""
        return f"{sign}{diff:.2f}"
    elif metric in ["claim_count"]:
        sign = "+" if diff >= 0 else ""
        return f"{sign}{int(diff)}"
    sign = "+" if diff >= 0 else ""
    return f"{sign}{diff:.2f}"

def fmt_pct_chg(metric: str, curr: float, prior: float) -> str:
    if prior == 0:
        return "N/A"
    pct = (curr - prior) / prior
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct * 100:.1f}%"

def generate_report(
    valuation_month: str,
    latest_metrics: Optional[MetricsRecord],
    prior_metrics: Optional[MetricsRecord],
    anomalies: List[Anomaly],
    drivers: List[DriverResult],
    data_quality: Dict[str, Any],
    exec_summary: List[str],
    follow_ups: List[str],
    run_id: str,
    trace_path: str,
    dataset_path: str,
    workspace_root: str
) -> Tuple[str, str]:
    
    # Resolve status and severity
    severity_levels = [a.severity for a in anomalies]
    if "high" in severity_levels:
        status = "High"
    elif "moderate" in severity_levels:
        status = "Moderate"
    else:
        status = "Green"
        
    requires_review = "Yes" if (status in ["High", "Moderate"] or data_quality.get("status") == "fail" or any(a.requires_human_review for a in anomalies) or len(data_quality.get("injection_flags", [])) > 0) else "No"
    
    report_title = f"Monthly Portfolio Review Report - {valuation_month}"
    
    report_md = f"""# {report_title}

## Header

**Portfolio:** Synthetic Actuarial Book  
**Valuation month:** {valuation_month}  
**Run ID:** {run_id}  
**Status:** {status}  
**Human review required:** {requires_review}

## Executive summary

"""
    for finding in exec_summary:
        report_md += f"- {finding}\n"
    if not exec_summary:
        if status == "Green":
            report_md += "- No material anomalies detected. Portfolio is performing within historical ranges.\n"
        else:
            report_md += f"- Anomalies flagged in {valuation_month}. Overall severity: {status}.\n"
            
    # Data Quality summary
    dq_status = "PASS" if data_quality.get("status") == "pass" else ("WARNING" if data_quality.get("status") == "pass_with_warnings" else "FAIL")
    dq_notes = "; ".join(data_quality.get("warnings", [])) if data_quality.get("warnings") else "No issues detected"
    if data_quality.get("blocking_errors"):
        dq_notes = "BLOCKING ERRORS: " + "; ".join(data_quality.get("blocking_errors", []))
        
    report_md += f"""
## Data quality summary

| Check | Status | Notes |
|---|---|---|
| Required columns | {"PASS" if "Missing required columns" not in dq_notes else "FAIL"} | {dq_notes} |
| Numeric fields | {"PASS" if "must be numeric" not in dq_notes else "FAIL"} | |
| Missing values | {"PASS" if "Null values detected" not in dq_notes else "WARNING"} | |
| Suspicious text fields | {"PASS" if not data_quality.get("injection_flags") else "WARNING"} | {f"Flagged {len(data_quality.get('injection_flags', []))} rows" if data_quality.get("injection_flags") else "No suspicious text"} |
| Overall validation | {dq_status} | |

## Key metric movement

"""
    # Build Key metric movement table
    report_md += "| Metric | Current | Prior | Change | Severity |\n"
    report_md += "|---|---:|---:|---:|---|\n"
    
    metrics_to_show = [
        ("written_premium", "Written premium"),
        ("earned_premium", "Earned premium"),
        ("incurred_loss", "Incurred loss"),
        ("loss_ratio", "Loss ratio"),
        ("claim_count", "Claim count"),
        ("rate_change_pct", "Rate change"),
        ("benchmark_adequacy", "Benchmark adequacy"),
        ("avg_retention", "Average retention")
    ]
    
    for field_name, display_name in metrics_to_show:
        curr_val = getattr(latest_metrics, field_name, 0.0) if latest_metrics else 0.0
        prior_val = getattr(prior_metrics, field_name, 0.0) if prior_metrics else 0.0
        
        # Check severity from anomalies
        matching_anom = next((a for a in anomalies if a.metric == field_name), None)
        sev_display = matching_anom.severity.upper() if matching_anom else "NORMAL"
        
        val_curr = fmt_val(field_name, curr_val)
        val_prior = fmt_val(field_name, prior_val)
        val_chg = fmt_chg(field_name, curr_val, prior_val)
        
        # If premium, also add % change
        if field_name == "written_premium" and prior_val > 0:
            pct_chg = fmt_pct_chg(field_name, curr_val, prior_val)
            val_chg = f"{val_chg} ({pct_chg})"
            
        report_md += f"| {display_name} | {val_curr} | {val_prior} | {val_chg} | {sev_display} |\n"
        
    report_md += "\n## Material findings\n\n"
    
    for i, anom in enumerate(anomalies, 1):
        # Find matching drivers for this anomaly
        matching_drivers = [d for d in drivers if d.anomaly_id == anom.anomaly_id]
        
        report_md += f"### Finding {i}: Material movement in {anom.metric}\n\n"
        report_md += f"**Metric:** {anom.metric}  \n"
        report_md += f"**Severity:** {anom.severity}  \n"
        report_md += f"**Current:** {fmt_val(anom.metric, anom.current_value)}  \n"
        report_md += f"**Prior:** {fmt_val(anom.metric, anom.prior_value)}  \n"
        report_md += f"**Change:** {fmt_chg(anom.metric, anom.current_value, anom.prior_value)}  \n\n"
        
        report_md += "**Evidence:**  \n"
        report_md += f"{anom.explanation}\n\n"
        
        report_md += "**Driver investigation:**  \n"
        if matching_drivers:
            for drv in matching_drivers:
                report_md += f"- **Dimension: {drv.dimension}**\n"
                for tc in drv.top_contributors:
                    curr_str = fmt_val(anom.metric, tc.current_value)
                    prior_str = fmt_val(anom.metric, tc.prior_value)
                    contrib_str = fmt_chg(anom.metric, tc.current_value, tc.prior_value)
                    # If contribution is percentage or points
                    if anom.metric in ["loss_ratio", "rate_change_pct"]:
                        contrib_pct_pts = f"{tc.contribution_to_change * 100:.1f} pts"
                        report_md += f"  - Value: `{tc.value}` (Current: {curr_str}, Prior: {prior_str}, Contribution: {contrib_pct_pts})\n"
                    elif anom.metric in ["benchmark_adequacy"]:
                        contrib_pts = f"{tc.contribution_to_change:.2f} pts"
                        report_md += f"  - Value: `{tc.value}` (Current: {curr_str}, Prior: {prior_str}, Contribution: {contrib_pts})\n"
                    else:
                        contrib_pct = f"{tc.contribution_to_change * 100:.1f}%"
                        report_md += f"  - Value: `{tc.value}` (Current: {curr_str}, Prior: {prior_str}, Contribution: {contrib_pct})\n"
        else:
            report_md += "No drivers identified.\n"
            
        report_md += "\n**Interpretation:**  \n"
        # Deterministic interpretation based on metric
        if anom.metric == "loss_ratio":
            report_md += "The increase in loss ratio suggests higher claims emergence relative to earned premium, indicating a deterioration in underwriting profitability.\n"
        elif anom.metric == "written_premium":
            report_md += "The written premium movement indicates changes in overall business volume, potentially driven by pricing actions, retention rate changes, or new business acquisition.\n"
        elif anom.metric == "benchmark_adequacy":
            report_md += "The decrease in benchmark adequacy suggests rate adequacy is slipping relative to standard baseline expectations, indicating potential underwriting risk.\n"
        else:
            report_md += f"Material change in {anom.metric} detected. Underwriting should review pricing and exposure settings.\n"
            
        report_md += "\n**Caveats:**  \n"
        report_md += "- Results are based on synthetic data and should not be used as official projections.\n"
        if data_quality.get("warnings"):
            report_md += f"- Data quality warnings present: {'; '.join(data_quality.get('warnings'))}\n"
            
        report_md += "\n**Recommended follow-up:**\n"
        report_md += f"- Investigate underwriting changes in the primary driver slice(s).\n"
        report_md += f"- Verify claims reporting lag or timing differences.\n\n"
        
    report_md += "## Human review gate\n\n"
    report_md += f"**Review required:** {requires_review}\n\n"
    report_md += "**Reasons:**\n"
    if requires_review == "Yes":
        if "high" in severity_levels:
            report_md += "- High severity anomaly detected.\n"
        if data_quality.get("status") == "fail":
            report_md += "- Ingestion/schema validation failed.\n"
        if data_quality.get("injection_flags"):
            report_md += "- Prompt injection signature detected in dataset text.\n"
        if not anomalies and data_quality.get("warnings"):
            report_md += "- Warnings present on the dataset.\n"
    else:
        report_md += "- No high severity anomalies or security/quality triggers detected.\n"
        
    report_md += f"""
## Trace and reproducibility

- Trace file: `{trace_path}`
- Dataset: `{dataset_path}`
- Threshold profile: `default_mvp`

## Disclaimer

This report is generated from synthetic/demo data for a capstone project. It is a first-pass monitoring aid and does not represent a formal actuarial opinion, underwriting action, pricing decision, or reserving recommendation.
"""
    
    # Save the report
    reports_dir = os.path.join(workspace_root, "outputs", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_file_name = f"portfolio_review_{valuation_month}_{run_id}.md"
    report_path_resolved = os.path.join(reports_dir, report_file_name)
    
    with open(report_path_resolved, "w") as f:
        f.write(report_md)
        
    # Return path relative to workspace root
    rel_report_path = os.path.relpath(report_path_resolved, workspace_root)
    return rel_report_path, report_md
