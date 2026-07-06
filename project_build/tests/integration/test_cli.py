import inspect
from pathlib import Path

from portfolio_agent import run
from portfolio_agent.core.schemas import PortfolioReviewResult, ReviewMemo


def _fake_result(mode: str = "offline") -> PortfolioReviewResult:
    return PortfolioReviewResult(
        run_id="cli-test-run",
        valuation_month="2026-06",
        execution_mode=mode,
        status="complete",
        requires_human_review=False,
        human_review_reasons=[],
        anomaly_count=0,
        report_path="outputs/reports/cli-test.md",
        trace_path="outputs/traces/cli-test.json",
        memo=ReviewMemo(
            valuation_month="2026-06",
            executive_summary="CLI test summary.",
            finding_details=[],
            recommended_followups=[],
            confidence=4.0,
            requires_human_review=False,
        ),
    )


def test_cli_adapter_calls_shared_service_for_online_mode(monkeypatch, capsys):
    calls = []

    def fake_review_portfolio(**kwargs):
        calls.append(kwargs)
        return _fake_result(mode="online")

    monkeypatch.setattr(run, "review_portfolio", fake_review_portfolio)
    monkeypatch.setattr(
        "sys.argv",
        [
            "portfolio_agent.run",
            "--input",
            "tests/golden/clean_portfolio.csv",
            "--latest-month",
            "2026-06",
        ],
    )

    run.main()

    assert calls == [
        {
            "input_path": "tests/golden/clean_portfolio.csv",
            "latest_month": "2026-06",
            "model_name": "gemini-2.5-flash-lite",
            "user_prompt": None,
            "force_offline": False,
        }
    ]
    assert "Mode: online" in capsys.readouterr().out


def test_cli_adapter_passes_force_offline_to_shared_service(monkeypatch, capsys):
    calls = []

    def fake_review_portfolio(**kwargs):
        calls.append(kwargs)
        return _fake_result(mode="offline")

    monkeypatch.setattr(run, "review_portfolio", fake_review_portfolio)
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

    assert calls[0]["force_offline"] is True
    assert "Mode: offline" in capsys.readouterr().out


def test_cli_contains_no_actuarial_calculation_imports():
    source = Path(run.__file__).read_text(encoding="utf-8")

    forbidden = [
        "from portfolio_agent.tools import",
        "load_portfolio_data",
        "validate_portfolio_data",
        "calculate_portfolio_metrics",
        "detect_anomalies",
        "investigate_anomaly_drivers",
    ]
    for token in forbidden:
        assert token not in source

    assert "review_portfolio" in source
    assert "argparse" in source


def test_cli_main_signature_stays_adapter_only():
    assert inspect.signature(run.main).parameters == {}
