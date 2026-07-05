import argparse
import logging
import sys

from portfolio_agent.core.security import SecurityError
from portfolio_agent.service import review_portfolio


logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s %(message)s")
log = logging.getLogger("portfolio_agent")


def parse_args():
    parser = argparse.ArgumentParser(description="Actuarial Portfolio Monitoring Agent")
    parser.add_argument("--input", required=True, help="Path to synthetic monthly portfolio CSV")
    parser.add_argument("--latest-month", required=True, help="Valuation month to review (YYYY-MM)")
    parser.add_argument("--model", default="gemini-2.5-flash", help="Gemini LLM model name")
    parser.add_argument("--user-prompt", default=None, help="Custom prompt or override instruction for the agent")
    parser.add_argument(
        "--force-offline",
        action="store_true",
        help="Use deterministic no-network synthesis and do not construct model clients.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    log.info(
        "Starting Portfolio Review (Valuation Month: %s, Mode: %s)",
        args.latest_month,
        "offline" if args.force_offline else "online",
    )

    try:
        result = review_portfolio(
            input_path=args.input,
            latest_month=args.latest_month,
            model_name=args.model,
            user_prompt=args.user_prompt,
            force_offline=args.force_offline,
        )

        log.info("Review pipeline finished successfully.")
        print("\n" + "=" * 50)
        print("Run complete.")
        print(f"Mode: {result.execution_mode}")
        print(f"Run ID: {result.run_id}")
        print(f"Severity: {'High' if result.requires_human_review else 'Low'}")
        print(f"Human review required: {'Yes' if result.requires_human_review else 'No'}")
        print(f"Human review reasons: {', '.join(result.human_review_reasons) or 'None'}")
        print(f"Top finding: {result.memo.executive_summary.split('.')[0]}.")
        print(f"Report: {result.report_path}")
        print(f"Trace: {result.trace_path}")
        print("=" * 50 + "\n")

    except SecurityError as se:
        log.error("Security boundary breach blocked: %s", se)
        sys.exit(1)
    except Exception as e:
        log.error("Orchestration failure: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
