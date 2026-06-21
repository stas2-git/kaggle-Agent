import os
import sys
import argparse
import random
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s %(message)s")
log = logging.getLogger("portfolio_agent")

from portfolio_agent.security import SecurityError
from portfolio_agent.tools import (
    load_portfolio_data,
    validate_portfolio_data,
    calculate_portfolio_metrics,
    detect_anomalies,
    investigate_anomaly_drivers
)
from portfolio_agent.agent import synthesize_review_findings
from portfolio_agent.reporting import compile_markdown_report
from portfolio_agent.tracing import TraceLogger

def parse_args():
    parser = argparse.ArgumentParser(description="Actuarial Portfolio Monitoring Agent")
    parser.add_argument("--input", required=True, help="Path to synthetic monthly portfolio CSV")
    parser.add_argument("--latest-month", required=True, help="Valuation month to review (YYYY-MM)")
    parser.add_argument("--model", default="gemini-2.5-flash", help="Gemini LLM model name")
    parser.add_argument("--user-prompt", default=None, help="Custom prompt or override instruction for the agent")
    return parser.parse_args()

def main():
    args = parse_args()
    
    # 1. Initialize run metadata
    run_id = f"{random.randint(100, 999)}"
    log.info(f"Starting Portfolio Review (Run ID: {run_id}, Valuation Month: {args.latest_month})")
    
    trace = TraceLogger(run_id=run_id, dataset_path=args.input)
    trace.log_event("pipeline_start", {"valuation_month": args.latest_month, "model": args.model})

    try:
        # 2. Load Portfolio Data
        log.info(f"Loading data from {args.input}")
        df = load_portfolio_data(args.input)
        trace.log_event("data_loaded", {"row_count": len(df)})
        
        # 3. Validate Data
        log.info("Validating dataset schema and quality")
        df, errors, warnings = validate_portfolio_data(df)
        trace.log_event("data_validated", {"errors": errors, "warnings": warnings})
        
        if errors:
            log.error(f"Blocking data quality errors found: {errors}")
            trace.set_metadata("run_status", "FAILED")
            trace.set_metadata("failure_reason", f"Validation errors: {errors}")
            trace.save_trace()
            sys.exit(1)
            
        dq_summary = {
            "errors": len(errors),
            "warnings": len(warnings),
            "null_warnings": "Null cells present" if any("Null" in w for w in warnings) else None,
            "injection_warnings": "Prompt injection signature detected" if any("injection" in w for w in warnings) else None,
            "non_numeric": "Non-numeric types" if any("non-numeric" in w for w in warnings) else None
        }

        # 4. Calculate Metrics
        log.info("Calculating portfolio metrics")
        metrics = calculate_portfolio_metrics(df)
        trace.log_event("metrics_calculated", {"metric_records_count": len(metrics)})

        # 5. Detect Anomalies
        log.info("Running anomaly thresholds checks")
        anomalies = detect_anomalies(metrics, args.latest_month)
        trace.log_event("anomalies_detected", {"anomalies_count": len(anomalies)})

        # 6. Investigate Drivers
        log.info(f"Running driver investigations on {len(anomalies)} anomalies")
        driver_results = []
        for anomaly in anomalies:
            drivers = investigate_anomaly_drivers(df, anomaly)
            driver_results.extend(drivers)
            trace.log_event("drivers_investigated", {
                "anomaly_id": anomaly.anomaly_id, 
                "dimensions_sliced": [d.dimension for d in drivers]
            })

        # 7. LLM Synthesis
        log.info("Calling Gemini for review synthesis and follow-ups")
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

        # 8. Generate Reports & Trace File
        trace_path = f"outputs/traces/run_trace_{run_id}.json"
        
        log.info("Compiling markdown report")
        report_file = compile_markdown_report(
            memo=memo,
            anomalies=anomalies,
            driver_results=driver_results,
            data_quality_summary=dq_summary,
            run_id=run_id,
            dataset_path=args.input,
            trace_path=trace_path,
            metrics_records=metrics
        )
        trace.log_event("report_generated", {"report_path": str(report_file)})

        trace.set_metadata("run_status", "COMPLETE")
        trace.set_metadata("overall_severity", "High" if memo.requires_human_review else "Low")
        trace.set_metadata("requires_human_review", memo.requires_human_review)
        trace.set_metadata("report_path", str(report_file))
        
        saved_trace_file = trace.save_trace()
        log.info("Review pipeline finished successfully.")

        # Print final output contract
        print("\n" + "=" * 50)
        print("Run complete.")
        print(f"Severity: {'High' if memo.requires_human_review else 'Low'}")
        print(f"Human review required: {'Yes' if memo.requires_human_review else 'No'}")
        print(f"Top finding: {memo.executive_summary.split('.')[0]}.")
        print(f"Report: {report_file}")
        print(f"Trace: {saved_trace_file}")
        print("=" * 50 + "\n")

    except SecurityError as se:
        log.error(f"Security boundary breach blocked: {se}")
        trace.set_metadata("run_status", "SECURITY_BLOCKED")
        trace.set_metadata("failure_reason", str(se))
        trace.save_trace()
        sys.exit(1)
    except Exception as e:
        log.error(f"Orchestration failure: {e}", exc_info=True)
        trace.set_metadata("run_status", "FAILED")
        trace.set_metadata("failure_reason", str(e))
        trace.save_trace()
        sys.exit(1)

if __name__ == "__main__":
    main()
