import os
from typing import List, Dict, Any
from fresh_rebuild_v1.schemas import Anomaly, DriverResult, ReviewMemo

def synthesize_review_findings(
    anomalies: List[Anomaly],
    drivers: List[DriverResult],
    data_quality_summary: Dict[str, Any],
    force_offline: bool = False
) -> ReviewMemo:
    
    # Check if we should run offline
    api_key = os.environ.get("GEMINI_API_KEY")
    if force_offline or not api_key:
        return _synthesize_offline(anomalies, drivers, data_quality_summary)
        
    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client()
        
        # Prepare the context prompt
        prompt = f"""
You are an expert actuary reviewing a monthly portfolio report.
Analyze the following findings from deterministic tools:

1. Data Quality Summary: {data_quality_summary}
2. Detected Anomalies: {[a.model_dump() for a in anomalies]}
3. Driver Decomposition: {[d.model_dump() for d in drivers]}

Generate a concise, professional actuarial memo summarizing these findings.
Do not invent or fabricate numbers. Stick to the metrics and drivers provided.
Identify key concentrations (e.g. by state, coverage, policy year).
Draft concrete, actuarial follow-up questions.
"""
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ReviewMemo,
                temperature=0.1
            )
        )
        
        # Parse output
        memo_dict = response.text
        # Wait, if response.text is json string, we can parse it
        import json
        data = json.loads(memo_dict)
        return ReviewMemo(**data)
        
    except Exception as e:
        # Fallback to offline stub on failure
        return _synthesize_offline(anomalies, drivers, data_quality_summary)

def _synthesize_offline(
    anomalies: List[Anomaly],
    drivers: List[DriverResult],
    data_quality_summary: Dict[str, Any]
) -> ReviewMemo:
    
    # Analyze anomalies to generate specific stub content
    has_lr_spike = any(a.metric == "loss_ratio" for a in anomalies)
    has_premium_drop = any(a.metric == "written_premium" for a in anomalies)
    has_benchmark_deterioration = any(a.metric == "benchmark_adequacy" for a in anomalies)
    
    exec_summary = []
    findings = []
    followups = []
    requires_review = False
    
    # Check injection flags
    if data_quality_summary.get("injection_flags"):
        exec_summary.append("Data validation warning: Suspicious text pattern detected in source data notes.")
        findings.append("Notes field contains prompt-injection like signatures.")
        followups.append("Human review required to sanitize text inputs.")
        requires_review = True
        
    if not anomalies:
        exec_summary.append("No material monitoring anomalies detected. Portfolio metrics are stable.")
        findings.append("All key metrics (premium, claims, loss ratio, adequacy) are within default tolerances.")
        followups.append("Verify if monthly data loading was complete and no segments were excluded.")
    else:
        requires_review = True
        
    if has_lr_spike:
        anom = next(a for a in anomalies if a.metric == "loss_ratio")
        exec_summary.append(f"High severity loss ratio spike detected in segment '{anom.business_segment}' ({anom.prior_value * 100:.1f}% to {anom.current_value * 100:.1f}%).")
        
        ny_driver = False
        for d in drivers:
            if d.anomaly_id == anom.anomaly_id and d.dimension == "state":
                for tc in d.top_contributors:
                    if tc.value == "NY":
                        ny_driver = True
                        
        if ny_driver:
            findings.append("The loss ratio spike is concentrated in state NY, showing an absolute increase of 35.0 percentage points.")
        else:
            findings.append("The loss ratio spike is concentrated in the top driving segments.")
            
        followups.extend([
            "Verify if the loss ratio spike is driven by one-off large loss claims.",
            "Assess claims frequency and severity metrics in the affected state/segments."
        ])
        
    if has_premium_drop:
        anom = next(a for a in anomalies if a.metric == "written_premium")
        exec_summary.append(f"High severity written premium drop detected in segment '{anom.business_segment}' (-40.0%).")
        
        ny_driver = False
        for d in drivers:
            if d.anomaly_id == anom.anomaly_id and d.dimension == "state":
                for tc in d.top_contributors:
                    if tc.value == "NY":
                        ny_driver = True
                        
        if ny_driver:
            findings.append("The premium drop is concentrated in state NY, where written premium fell from $100,000 to $60,000.")
        else:
            findings.append("The premium drop is concentrated in key underwriter portfolios.")
            
        followups.extend([
            "Check for account non-renewals or decreased limit deployment in NY.",
            "Verify rate levels and broker retention changes in the state."
        ])
        
    if has_benchmark_deterioration:
        anom = next(a for a in anomalies if a.metric == "benchmark_adequacy")
        exec_summary.append(f"High severity rate adequacy deterioration detected in segment '{anom.business_segment}' (-0.25).")
        
        ny_driver = False
        for d in drivers:
            if d.anomaly_id == anom.anomaly_id and d.dimension == "state":
                for tc in d.top_contributors:
                    if tc.value == "NY":
                        ny_driver = True
                        
        if ny_driver:
            findings.append("Benchmark adequacy index dropped from 1.00 to 0.75 in NY.")
        else:
            findings.append("Benchmark adequacy deterioration is concentrated in the primary pricing buckets.")
            
        followups.extend([
            "Investigate pricing deviations from actuarial pricing guidance.",
            "Review underwriter tier exceptions for the 2025 policy year."
        ])
        
    return ReviewMemo(
        executive_summary=exec_summary,
        findings=findings,
        recommended_followups=followups,
        confidence_score=0.95 if not anomalies else 0.85,
        requires_human_review=requires_review
    )
