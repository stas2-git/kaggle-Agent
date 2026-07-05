from pathlib import Path

from fastapi.testclient import TestClient

from portfolio_agent.config import load_config
from portfolio_agent.fast_api_app import app
from portfolio_agent.service import review_portfolio


def test_health_works_without_credentials_or_model_client(monkeypatch):
    import google.genai

    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(
        google.genai,
        "Client",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("healthz must not construct a model client")
        ),
    )

    response = TestClient(app).get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "application": "portfolio_agent"}


def test_readyz_reveals_no_environment_values(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "AIza-not-a-real-key")
    monkeypatch.setenv("PORTFOLIO_AGENT_MODEL", "gemini-2.5-flash")

    response = TestClient(app).get("/readyz")

    assert response.status_code == 200
    body = response.json()
    body_text = str(body)
    assert body["status"] == "ready"
    assert body["application"] == "portfolio_agent"
    assert body["model_configured"] is True
    assert "AIza-not-a-real-key" not in body_text
    assert "gemini-2.5-flash" not in body_text


def test_invalid_path_returns_controlled_error():
    response = TestClient(app).post(
        "/api/reviews",
        json={
            "dataset_ref": "portfolio_agent/agent.py",
            "latest_month": "2026-06",
            "mode": "offline",
        },
    )

    assert response.status_code == 403
    assert "Access Denied" in response.json()["detail"]


def test_offline_api_review_works_with_model_constructor_blocked(monkeypatch, tmp_path):
    import google.genai

    monkeypatch.setenv("PORTFOLIO_AGENT_REPORTS_DIR", str(tmp_path / "reports"))
    monkeypatch.setenv("PORTFOLIO_AGENT_TRACES_DIR", str(tmp_path / "traces"))
    monkeypatch.setattr(
        google.genai,
        "Client",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("offline API must not construct a model client")
        ),
    )

    response = TestClient(app).post(
        "/api/reviews",
        json={
            "dataset_ref": "loss_ratio_spike",
            "latest_month": "2026-06",
            "mode": "offline",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["execution_mode"] == "offline"
    assert body["anomaly_count"] > 0
    assert body["requires_human_review"] is True
    assert Path(body["report_path"]).exists()
    assert Path(body["trace_path"]).exists()


def test_cli_service_and_api_return_equivalent_offline_decisions(monkeypatch, tmp_path):
    monkeypatch.setenv("PORTFOLIO_AGENT_REPORTS_DIR", str(tmp_path / "api_reports"))
    monkeypatch.setenv("PORTFOLIO_AGENT_TRACES_DIR", str(tmp_path / "api_traces"))
    api_response = TestClient(app).post(
        "/api/reviews",
        json={
            "dataset_ref": "clean_portfolio",
            "latest_month": "2026-06",
            "mode": "offline",
        },
    )
    assert api_response.status_code == 200
    api_body = api_response.json()

    config = load_config(force_offline=True)
    config = type(config)(
        application_name=config.application_name,
        model_name=config.model_name,
        execution_mode=config.execution_mode,
        project_root=config.project_root,
        reports_dir=tmp_path / "cli_reports",
        traces_dir=tmp_path / "cli_traces",
        threshold_profile=config.threshold_profile,
    )
    cli_result = review_portfolio(
        input_path="tests/golden/clean_portfolio.csv",
        latest_month="2026-06",
        force_offline=True,
        run_id="api-cli-equivalence",
        config=config,
    )

    assert api_body["anomaly_count"] == cli_result.anomaly_count
    assert api_body["requires_human_review"] == cli_result.requires_human_review
    assert api_body["human_review_reasons"] == cli_result.human_review_reasons


def test_fastapi_adapter_contains_no_calculation_logic():
    source = Path("portfolio_agent/fast_api_app.py").read_text(encoding="utf-8")

    forbidden = [
        "calculate_portfolio_metrics",
        "detect_anomalies",
        "investigate_anomaly_drivers",
        "load_portfolio_data",
        "validate_portfolio_data",
    ]
    for token in forbidden:
        assert token not in source

    assert "review_portfolio" in source
