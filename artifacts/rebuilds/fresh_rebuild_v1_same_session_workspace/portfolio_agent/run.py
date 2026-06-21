import os
import sys
import argparse
import random
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s %(message)s")
log = logging.getLogger("rebuilt_portfolio_agent")

from artifacts.rebuilds.fresh_rebuild_v1_same_session_workspace.portfolio_agent.security import SecurityError
from artifacts.rebuilds.fresh_rebuild_v1_same_session_workspace.portfolio_agent.tools import (
    load_portfolio_data,
    validate_portfolio_data,
    calculate_portfolio_metrics,
    detect_anomalies,
    investigate_anomaly_drivers
)
from artifacts.rebuilds.fresh_rebuild_v1_same_session_workspace.portfolio_agent.agent import synthesize_review_findings
from artifacts.rebuilds.fresh_rebuild_v1_same_session_workspace.portfolio_agent.reporting import compile_markdown_report
from artifacts.rebuilds.fresh_rebuild_v1_same_session_workspace.portfolio_agent.tracing import TraceLogger

def parse_args():
    parser = argparse.ArgumentParser(description="Rebuilt Actuarial Portfolio Monitoring Agent")
    parser.add_argument("--input", required=True, help="Path to monthly portfolio CSV")
    parser.add_argument("--latest-month", required=True, help="Valuation month to review YYYY-MM")
    parser.add_argument("--model", default="gemini-2.5-flash")
    parser.add_argument("--user-prompt", default=None)
    return parser.parse_args()

def main():
    args = parse_args()
    run_id = f"rebuild_{random.randint(100, 999)}"
    
    workspace_root = str(Path(__file__).parent.parent)
    
    trace = TraceLogger(run_id=run_id, dataset_path=args.input)
    trace.log_event("pipeline_start", {"valuation_month": args.latest_month, "model": args.model})
    
    try:
        df = load_portfolio_data(args.input, workspace_root=workspace_root)
        trace.log_event("data_loaded", {"row_count": len(df)})
        
        df, errors, warnings = validate_portfolio_data(df)
        trace.log_event("data_validated", {"errors": errors, "warnings": warnings})
        
        if errors:
            trace.set_metadata("run_status", "FAILED")
            trace.set_metadata("failure_reason", f"Validation errors: {errors}")
            trace.save_trace(output_dir=str(Path(workspace_root) / "outputs/traces"))
            sys.exit(1)
            
        dq_summary = {
            "errors": len(errors),
            "warnings": len(warnings),
            "null_warnings": "Null cells present" if any("Null" in w for w in warnings) else None,
            "injection_warnings": "Prompt injection signature detected" if any("injection" in w for w in warnings) else None,
            "non_numeric": "Non-numeric types" if any("non-numeric" in w for w in warnings) else None
        }
        
        metrics = calculate_portfolio_metrics(df)
        trace.log_event("metrics_calculated", {"metric_records_count": len(metrics)})
        
        anomalies = detect_anomalies(metrics, args.latest_month)
        trace.log_event("anomalies_detected", {"anomalies_count": len(anomalies)})
        
        driver_results = []
        for anomaly in anomalies:
            drivers = investigate_anomaly_drivers(df, anomaly)
            driver_results.extend(drivers)
            trace.log_event("drivers_investigated", {
                "anomaly_id": anomaly.anomaly_id,
                "dimensions_sliced": [d.dimension for d in drivers]
            })
            
        memo = synthesize_review_findings(
            valuation_month=args.latest_month,
            anomalies=anomalies,
            driver_results=driver_results,
            data_quality_summary=dq_summary,
            model_name=args.model,
            user_prompt_override=args.user_prompt
        )
        trace.log_event("findings_synthesized", {
            "confidence": memo.confidence,
            "requires_human_review": memo.requires_human_review
        })
        
        trace_path = f"outputs/traces/run_trace_{run_id}.json"
        
        report_file = compile_markdown_report(
            memo=memo,
            anomalies=anomalies,
            driver_results=driver_results,
            data_quality_summary=dq_summary,
            run_id=run_id,
            dataset_path=args.input,
            trace_path=trace_path,
            metrics_records=metrics,
            output_dir=str(Path(workspace_root) / "outputs/reports")
        )
        trace.log_event("report_generated", {"report_path": str(report_file)})
        
        trace.set_metadata("run_status", "COMPLETE")
        trace.set_metadata("overall_severity", "High" if memo.requires_human_review else "Low")
        trace.set_metadata("requires_human_review", memo.requires_human_review)
        trace.set_metadata("report_path", str(report_file))
        
        saved_trace_file = trace.save_trace(output_dir=str(Path(workspace_root) / "outputs/traces"))
        
        print("\n" + "=" * 50)
        print("Run complete.")
        print(f"Severity: {'High' if memo.requires_human_review else 'Low'}")
        print(f"Human review required: {'Yes' if memo.requires_human_review else 'No'}")
        print(f"Top finding: {memo.executive_summary.split('.')[0]}.")
        print(f"Report: {report_file}")
        print(f"Trace: {saved_trace_file}")
        print("=" * 50 + "\n")
        
    except SecurityError as se:
        trace.set_metadata("run_status", "SECURITY_BLOCKED")
        trace.set_metadata("failure_reason", str(se))
        trace.save_trace(output_dir=str(Path(workspace_root) / "outputs/traces"))
        log.error(f"Security error: {se}")
        sys.exit(1)
    except Exception as e:
        trace.set_metadata("run_status", "FAILED")
        trace.set_metadata("failure_reason", str(e))
        trace.save_trace(output_dir=str(Path(workspace_root) / "outputs/traces"))
        log.error(f"Execution error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
