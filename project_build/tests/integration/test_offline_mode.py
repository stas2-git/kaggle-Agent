import json
from pathlib import Path

import pytest

from portfolio_agent.support.config import load_config
from portfolio_agent.service import review_portfolio


def test_offline_loss_ratio_demo_completes_without_model_client(monkeypatch, tmp_path):
    import google.genai

    def fail_client_constructor(*args, **kwargs):
        raise AssertionError("offline mode must not construct a Gemini client")

    monkeypatch.setattr(google.genai, "Client", fail_client_constructor)

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
        run_id="offline-test",
        config=config,
    )

    assert result.execution_mode == "offline"
    assert result.status == "complete"
    assert result.anomaly_count > 0
    assert result.requires_human_review is True
    assert "deterministic_threshold_requires_review" in result.human_review_reasons

    report_path = Path(result.report_path)
    trace_path = Path(result.trace_path)
    assert report_path.exists()
    assert trace_path.exists()
    assert "[OFFLINE MODE]" in report_path.read_text(encoding="utf-8")

    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    assert trace["metadata"]["execution_mode"] == "offline"
    event_names = [event["event_name"] for event in trace["events"]]
    assert "offline_synthesis_started" in event_names
    assert "model_synthesis_started" not in event_names
    assert all("model_call" not in event["event_name"] for event in trace["events"])


def test_offline_cli_writes_report_and_trace(monkeypatch, tmp_path):
    import google.genai
    from portfolio_agent import run

    def fail_client_constructor(*args, **kwargs):
        raise AssertionError("offline CLI must not construct a Gemini client")

    monkeypatch.setattr(google.genai, "Client", fail_client_constructor)
    monkeypatch.setenv("PORTFOLIO_AGENT_REPORTS_DIR", str(tmp_path / "reports"))
    monkeypatch.setenv("PORTFOLIO_AGENT_TRACES_DIR", str(tmp_path / "traces"))
    monkeypatch.setattr(
        "sys.argv",
        [
            "portfolio_agent.run",
            "--input",
            "tests/golden/loss_ratio_spike.csv",
            "--latest-month",
            "2026-06",
            "--force-offline",
        ],
    )

    run.main()

    reports = list((tmp_path / "reports").glob("portfolio_review_2026_06_*.md"))
    traces = list((tmp_path / "traces").glob("run_trace_*.json"))
    assert reports
    assert traces
    assert "[OFFLINE MODE]" in reports[0].read_text(encoding="utf-8")


def test_online_mode_keeps_existing_model_synthesis_boundary(monkeypatch, tmp_path):
    from portfolio_agent.core.schemas import ReviewMemo

    calls = []

    def fake_synthesis(**kwargs):
        calls.append(kwargs)
        return ReviewMemo(
            valuation_month=kwargs["valuation_month"],
            executive_summary="Online synthesis boundary preserved.",
            finding_details=[],
            recommended_followups=[],
            confidence=4.0,
            requires_human_review=False,
        )

    import portfolio_agent.agent

    monkeypatch.setattr(portfolio_agent.agent, "synthesize_review_findings", fake_synthesis)
    config = load_config(force_offline=False)
    config = type(config)(
        application_name=config.application_name,
        model_name=config.model_name,
        execution_mode="online",
        project_root=config.project_root,
        reports_dir=tmp_path / "reports",
        traces_dir=tmp_path / "traces",
        threshold_profile=config.threshold_profile,
    )

    result = review_portfolio(
        input_path="tests/golden/clean_portfolio.csv",
        latest_month="2026-06",
        run_id="online-boundary-test",
        config=config,
    )

    assert result.execution_mode == "online"
    assert calls
    assert calls[0]["model_name"] == "gemini-2.5-flash-lite"
