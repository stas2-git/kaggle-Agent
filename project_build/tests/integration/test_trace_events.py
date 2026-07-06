import json
from pathlib import Path

from portfolio_agent.support.config import load_config
from portfolio_agent.service import review_portfolio
from portfolio_agent.observability.tracing import TraceLogger


def test_offline_trace_contains_enriched_event_schema(tmp_path):
    config = load_config(force_offline=True)
    config = type(config)(
        application_name=config.application_name,
        model_name=config.model_name,
        execution_mode=config.execution_mode,
        project_root=config.project_root,
        reports_dir=tmp_path / "reports",
        traces_dir=tmp_path / "traces",
        threshold_profile=config.threshold_profile,
    )

    result = review_portfolio(
        input_path="tests/golden/loss_ratio_spike.csv",
        latest_month="2026-06",
        force_offline=True,
        run_id="trace-schema-test",
        config=config,
    )

    trace = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))

    assert trace["app_name"] == "portfolio_agent"
    assert trace["session_id"] == "trace-schema-test"
    assert trace["config"]["execution_mode"] == "offline"
    assert trace["human_review"]["required"] is True
    assert trace["final_report_path"] == result.report_path
    assert trace["events"]
    assert all("event_id" in event for event in trace["events"])
    assert all("event_type" in event for event in trace["events"])
    assert all("status" in event for event in trace["events"])
    assert all(event["event_type"] != "model_call" for event in trace["events"])


def test_trace_logger_records_policy_decision_events(tmp_path):
    logger = TraceLogger(
        run_id="policy-trace-test", dataset_path="tests/golden/clean_portfolio.csv"
    )
    logger.set_metadata("execution_mode", "offline")
    logger.log_policy_decision(
        hook="before_tool",
        decision="block",
        policy="dimension_policy",
        reason_code="unauthorized_driver_dimension",
    )

    trace_path = logger.save_trace(str(tmp_path))
    trace = json.loads(trace_path.read_text(encoding="utf-8"))

    assert trace["events"][0]["event_type"] == "policy_decision"
    assert trace["events"][0]["details"]["hook"] == "before_tool"
    assert trace["events"][0]["details"]["decision"] == "block"
    assert (
        trace["events"][0]["details"]["reason_code"] == "unauthorized_driver_dimension"
    )
