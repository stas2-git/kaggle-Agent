import argparse
import os
import random
import time
import sys
from datetime import datetime
from typing import Dict, Any, List

from fresh_rebuild_v1.schemas import MetricsRecord, Anomaly, DriverResult
from fresh_rebuild_v1.security import validate_file_path
from fresh_rebuild_v1.tools import (
    load_portfolio_data,
    validate_portfolio_data,
    calculate_portfolio_metrics,
    detect_anomalies,
    investigate_anomaly_drivers
)
from fresh_rebuild_v1.agent import synthesize_review_findings
from fresh_rebuild_v1.reporting import generate_report
from fresh_rebuild_v1.tracing import TraceLogger

def run_pipeline(
    file_path: str,
    latest_month: str = None,
    force_offline: bool = False,
    workspace_root: str = "."
) -> int:
    # 1. Initialize Run ID
    run_id = f"{int(time.time() * 1000) % 1000:03d}"
    
    # 2. Setup Trace Logger
    logger = TraceLogger(
        run_id=run_id,
        user_prompt=f"Run actuarial review for {file_path}",
        input_dataset=file_path,
        config={"latest_month": latest_month or "auto", "threshold_profile": "default_mvp"}
    )
    
    # 3. Load Data
    logger.add_event("tool_call", "load_portfolio_data", {"file_path": file_path}, {}, "started")
    start_time = time.time()
    try:
        df = load_portfolio_data(file_path, workspace_root)
        duration = int((time.time() - start_time) * 1000)
        logger.add_event(
            "tool_result", 
            "load_portfolio_data", 
            {"file_path": file_path}, 
            {"row_count": len(df), "columns": list(df.columns)}, 
            "completed", 
            duration
        )
    except Exception as e:
        duration = int((time.time() - start_time) * 1000)
        logger.add_event("tool_result", "load_portfolio_data", {"file_path": file_path}, {"error": str(e)}, "failed", duration)
        logger.final_status = "error"
        logger.write_trace(workspace_root)
        print(f"Error loading portfolio data: {str(e)}")
        return 1
        
    # 4. Validate Data
    logger.add_event("tool_call", "validate_portfolio_data", {}, {}, "started")
    start_time = time.time()
    dq_result = validate_portfolio_data(df)
    duration = int((time.time() - start_time) * 1000)
    logger.data_quality = dq_result
    
    logger.add_event("tool_result", "validate_portfolio_data", {}, dq_result, "completed", duration)
    
    if dq_result["status"] == "fail":
        logger.final_status = "validation_failed"
        logger.human_review = {
            "required": True,
            "reasons": dq_result["blocking_errors"]
        }
        # Generate error report
        rel_report_path, _ = generate_report(
            valuation_month=latest_month or "unknown",
            latest_metrics=None,
            prior_metrics=None,
            anomalies=[],
            drivers=[],
            data_quality=dq_result,
            exec_summary=["Validation failed: " + "; ".join(dq_result["blocking_errors"])],
            follow_ups=["Fix source data file and rerun."],
            run_id=run_id,
            trace_path="",
            dataset_path=file_path,
            workspace_root=workspace_root
        )
        logger.final_report_path = rel_report_path
        rel_trace_path = logger.write_trace(workspace_root)
        print(f"Run complete.\nSeverity: High\nHuman review required: Yes\nTop finding: Ingestion validation failed.\nReport: {rel_report_path}\nTrace: {rel_trace_path}")
        return 0

    # Handle security / prompt injection flags
    if dq_result["injection_flags"]:
        for flag in dq_result["injection_flags"]:
            logger.add_security_flag(
                flag_type="prompt_injection",
                severity="high",
                source="data_field",
                description=f"Prompt injection detected in notes column at row {flag['row_index']}",
                action_taken="human_review_required"
            )
            
    # Determine valuation months
    if not latest_month:
        # Auto-detect latest month from data
        latest_month = str(df["valuation_month"].max())
        logger.config["latest_month"] = latest_month
        
    # 5. Calculate Metrics
    logger.add_event("tool_call", "calculate_portfolio_metrics", {}, {}, "started")
    start_time = time.time()
    metrics = calculate_portfolio_metrics(df)
    duration = int((time.time() - start_time) * 1000)
    logger.add_event("tool_result", "calculate_portfolio_metrics", {}, {"metrics_count": len(metrics)}, "completed", duration)
    
    # 6. Detect Anomalies
    logger.add_event("tool_call", "detect_anomalies", {"latest_month": latest_month}, {}, "started")
    start_time = time.time()
    anomalies = detect_anomalies(metrics, latest_month)
    duration = int((time.time() - start_time) * 1000)
    logger.anomalies = [a.model_dump() for a in anomalies]
    logger.add_event("tool_result", "detect_anomalies", {"latest_month": latest_month}, {"anomalies_count": len(anomalies)}, "completed", duration)
    
    # 7. Investigate Drivers
    drivers = []
    if anomalies:
        logger.add_event("tool_call", "investigate_anomaly_drivers", {"anomalies_count": len(anomalies)}, {}, "started")
        start_time = time.time()
        for anom in anomalies:
            drv_results = investigate_anomaly_drivers(df, anom, latest_month)
            drivers.extend(drv_results)
        duration = int((time.time() - start_time) * 1000)
        logger.driver_results = [d.model_dump() for d in drivers]
        logger.add_event("tool_result", "investigate_anomaly_drivers", {}, {"drivers_count": len(drivers)}, "completed", duration)
        
    # 8. Synthesize findings using LLM
    logger.add_event("tool_call", "synthesize_review_findings", {}, {}, "started")
    start_time = time.time()
    memo = synthesize_review_findings(anomalies, drivers, dq_result, force_offline)
    duration = int((time.time() - start_time) * 1000)
    logger.add_event("tool_result", "synthesize_review_findings", {}, memo.model_dump(), "completed", duration)
    
    # Determine human review triggers
    review_reasons = []
    if any(a.severity == "high" for a in anomalies):
        review_reasons.append("high_severity_anomaly")
    if dq_result["injection_flags"]:
        review_reasons.append("prompt_injection_detected")
    if dq_result["status"] == "pass_with_warnings":
        review_reasons.append("data_quality_warnings")
        
    review_required = len(review_reasons) > 0 or memo.requires_human_review
    logger.human_review = {
        "required": review_required,
        "reasons": review_reasons
    }
    
    # Get latest and prior metrics records for report
    all_months = sorted(list(set(df["valuation_month"])))
    try:
        latest_idx = all_months.index(latest_month)
        prior_month = all_months[latest_idx - 1] if latest_idx > 0 else None
    except ValueError:
        prior_month = None
        
    latest_rec = next((m for m in metrics if m.valuation_month == latest_month), None)
    prior_rec = next((m for m in metrics if m.valuation_month == prior_month), None) if prior_month else None
    
    # Generate Report
    logger.add_event("tool_call", "generate_report", {}, {}, "started")
    start_time = time.time()
    
    # We will write trace path to logger first
    trace_filename = f"run_{run_id}.json"
    trace_rel_path = os.path.join("outputs", "traces", trace_filename)
    
    rel_report_path, report_content = generate_report(
        valuation_month=latest_month,
        latest_metrics=latest_rec,
        prior_metrics=prior_rec,
        anomalies=anomalies,
        drivers=drivers,
        data_quality=dq_result,
        exec_summary=memo.executive_summary,
        follow_ups=memo.recommended_followups,
        run_id=run_id,
        trace_path=trace_rel_path,
        dataset_path=file_path,
        workspace_root=workspace_root
    )
    logger.final_report_path = rel_report_path
    duration = int((time.time() - start_time) * 1000)
    logger.add_event("tool_result", "generate_report", {}, {"report_path": rel_report_path}, "completed", duration)
    
    # Write Trace
    trace_path = logger.write_trace(workspace_root)
    
    # Print summary to stdout
    severity = "High" if any(a.severity == "high" for a in anomalies) else ("Moderate" if any(a.severity == "moderate" for a in anomalies) else "Green")
    top_finding = memo.executive_summary[0] if memo.executive_summary else "No material anomalies detected."
    
    print("Run complete.")
    print(f"Severity: {severity}")
    print(f"Human review required: {'Yes' if review_required else 'No'}")
    print(f"Top finding: {top_finding}")
    print(f"Report: {rel_report_path}")
    print(f"Trace: {trace_path}")
    
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Actuarial Portfolio Monitoring Agent Rebuild")
    parser.add_argument("--input", required=True, help="Input portfolio monthly CSV path")
    parser.add_argument("--latest-month", help="Latest month to review (YYYY-MM)")
    parser.add_argument("--force-offline", action="store_true", help="Force offline execution mode")
    args = parser.parse_args()
    
    sys.exit(run_pipeline(args.input, args.latest_month, args.force_offline, workspace_root="."))
