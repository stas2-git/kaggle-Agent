from typing import List
from artifacts.rebuilds.fresh_rebuild_v1_same_session_workspace.portfolio_agent.schemas import ReviewMemo, AnomalyRecord, DriverResult, FindingDetail

def synthesize_review_findings(
    valuation_month: str,
    anomalies: List[AnomalyRecord],
    driver_results: List[DriverResult],
    data_quality_summary: dict,
    model_name: str = "gemini-2.5-flash",
    user_prompt_override: str = None
) -> ReviewMemo:
    finding_details = []
    recommended_followups = []
    requires_human_review = False
    
    for anomaly in anomalies:
        if anomaly.requires_human_review or anomaly.severity == "high":
            requires_human_review = True
            
        metric_name = anomaly.metric.replace("_", " ").title()
        
        drivers_for_anom = [d for d in driver_results if d.anomaly_id == anomaly.anomaly_id]
        obs_text = f"We detected a {anomaly.severity} severity anomaly in {anomaly.business_segment} where the {metric_name} changed from {anomaly.prior_value:.2f} to {anomaly.current_value:.2f} (change: {anomaly.absolute_change:+.2f})."
        
        driver_details_list = []
        for d in drivers_for_anom:
            top_contrib = d.top_contributors[0] if d.top_contributors else None
            if top_contrib:
                driver_details_list.append(f"sliced by {d.dimension}, the main contributor was '{top_contrib.value}' with a change contribution of {top_contrib.contribution_to_change*100:+.1f} pts")
        
        if driver_details_list:
            obs_text += " Specifically, " + ", and ".join(driver_details_list) + "."
            
        finding_details.append(
            FindingDetail(
                anomaly_id=anomaly.anomaly_id,
                metric=anomaly.metric,
                segment=anomaly.business_segment,
                observations=obs_text,
                likely_cause_hypothesis=f"Hypothesis: the change in {anomaly.metric} was driven by recent changes in key drivers, specifically concentration in top contributing segments. Further underwriter review required."
            )
        )
        recommended_followups.append(f"Investigate key drivers for {anomaly.business_segment} {metric_name} anomaly.")
        
    if not anomalies:
        exec_summary = "No material anomalies detected. The portfolio is green and performing stably."
        recommended_followups.append("Continue routine monthly monitoring.")
    else:
        exec_summary = f"Actuarial monitoring flagged {len(anomalies)} anomalies in valuation month {valuation_month}. Main findings are: " + " ".join([f.observations for f in finding_details])
        
    if data_quality_summary.get("errors") or data_quality_summary.get("warnings"):
        requires_human_review = True
        
    return ReviewMemo(
        report_title="Actuarial Portfolio Review Memo",
        valuation_month=valuation_month,
        executive_summary=exec_summary,
        finding_details=finding_details,
        recommended_followups=recommended_followups,
        confidence=5.0,
        requires_human_review=requires_human_review
    )
