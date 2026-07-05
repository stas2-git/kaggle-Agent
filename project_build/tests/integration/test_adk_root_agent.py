from pathlib import Path

from portfolio_agent.support.config import load_config
from portfolio_agent.service import review_portfolio


def test_root_agent_and_app_import_with_expected_adk_shape():
    from portfolio_agent.agent import app, root_agent

    assert app.name == "portfolio_agent"
    assert app.root_agent is root_agent
    assert root_agent.name == "portfolio_monitoring_agent"
    assert root_agent.model == "gemini-2.5-flash"
    assert root_agent.output_schema is None

    tool_names = [getattr(tool, "name", getattr(tool, "__name__", str(tool))) for tool in root_agent.tools]
    assert tool_names == [
        "load_portfolio_data",
        "validate_portfolio_data",
        "calculate_portfolio_metrics",
        "detect_anomalies",
        "investigate_anomaly_drivers",
    ]

    assert root_agent.before_agent_callback is not None
    assert root_agent.before_model_callback is not None
    assert root_agent.before_tool_callback is not None
    assert root_agent.after_tool_callback is not None
    assert root_agent.after_model_callback is not None


def test_root_agent_instruction_contains_runtime_skill_rules():
    from portfolio_agent.agent import root_agent

    assert "Validate the dataset before analysis" in root_agent.instruction
    assert "Never invent numbers" in root_agent.instruction
    assert "Every numeric claim must come from a tool response" in root_agent.instruction


def test_clean_offline_review_skips_driver_investigation(tmp_path):
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
        input_path="tests/golden/clean_portfolio.csv",
        latest_month="2026-06",
        force_offline=True,
        run_id="clean-root-agent-boundary",
        config=config,
    )

    trace_text = Path(result.trace_path).read_text(encoding="utf-8")
    assert result.anomaly_count == 0
    assert "drivers_investigated" not in trace_text


def test_anomaly_offline_review_records_valid_driver_investigation(tmp_path):
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
        run_id="anomaly-root-agent-boundary",
        config=config,
    )

    trace_text = Path(result.trace_path).read_text(encoding="utf-8")
    assert result.anomaly_count > 0
    assert "drivers_investigated" in trace_text
    assert "ANOM_2026-06_Public_D&O_LR" in trace_text
