import yaml
import pytest
import pandas as pd
from pathlib import Path
from portfolio_agent.core.tools import (
    load_portfolio_data,
    calculate_portfolio_metrics,
    detect_anomalies,
    investigate_anomaly_drivers
)
from portfolio_agent.core.schemas import MetricsRecord, AnomalyRecord

GOLDEN_DIR = Path(__file__).parent / "golden"

@pytest.mark.parametrize("scenario", [
    "loss_ratio_spike",
    "premium_drop",
    "clean_portfolio",
    "benchmark_deterioration"
])
def test_golden_scenario(scenario: str):
    csv_path = GOLDEN_DIR / f"{scenario}.csv"
    yaml_path = GOLDEN_DIR / f"expected_{scenario}.yaml"
    
    # 1. Load expected YAML definition
    with open(yaml_path, "r", encoding="utf-8") as f:
        expected = yaml.safe_load(f)

    # 2. Ingest CSV data
    # Pass workspace root relative to tests folder (the project root is parent of parent)
    workspace_root = str(Path(__file__).parent.parent)
    df = load_portfolio_data(str(csv_path), workspace_root=workspace_root)
    assert not df.empty
    
    # 3. Calculate portfolio metrics
    metrics = calculate_portfolio_metrics(df)
    assert len(metrics) > 0
    
    # Index metrics by month
    metric_map = {m.valuation_month: m for m in metrics}
    m_cur = metric_map.get("2026-06")
    m_pri = metric_map.get("2026-05")
    
    assert m_cur is not None
    assert m_pri is not None
    
    exp_metrics = expected["expected_metrics"]
    
    # Verify calculated core metrics
    assert pytest.approx(m_cur.written_premium, abs=1e-2) == exp_metrics["current_period_premium"]
    assert pytest.approx(m_pri.written_premium, abs=1e-2) == exp_metrics["prior_period_premium"]
    assert pytest.approx(m_cur.loss_ratio, abs=1e-4) == exp_metrics["current_loss_ratio"]
    assert pytest.approx(m_pri.loss_ratio, abs=1e-4) == exp_metrics["prior_loss_ratio"]
    
    # Verify calculated premium change %
    calc_wp_change = (m_cur.written_premium - m_pri.written_premium) / m_pri.written_premium if m_pri.written_premium > 0 else 0.0
    assert pytest.approx(calc_wp_change, abs=1e-4) == exp_metrics["premium_change_pct"]
    
    # Verify loss ratio change points
    calc_lr_change = m_cur.loss_ratio - m_pri.loss_ratio
    assert pytest.approx(calc_lr_change, abs=1e-4) == exp_metrics["loss_ratio_change_points"]

    # Verify benchmark adequacy if present
    if "current_benchmark_adequacy" in exp_metrics:
        assert pytest.approx(m_cur.benchmark_adequacy, abs=1e-4) == exp_metrics["current_benchmark_adequacy"]
        assert pytest.approx(m_pri.benchmark_adequacy, abs=1e-4) == exp_metrics["prior_benchmark_adequacy"]
        calc_ba_change = m_cur.benchmark_adequacy - m_pri.benchmark_adequacy
        assert pytest.approx(calc_ba_change, abs=1e-4) == exp_metrics["benchmark_adequacy_change"]

    # 4. Detect anomalies
    anomalies = detect_anomalies(metrics, "2026-06")
    exp_flags = expected["expected_flags"]
    
    if exp_flags["anomaly_detected"]:
        assert len(anomalies) > 0
        # Find the primary anomaly matching the expected type if specified
        exp_type = exp_flags.get("anomaly_type")
        if exp_type:
            anomaly = next((a for a in anomalies if a.metric == exp_type), None)
            assert anomaly is not None, f"Expected anomaly of type {exp_type} not found."
        else:
            anomaly = anomalies[0]
            
        assert anomaly.severity == exp_flags["severity"]
        
        # Verify human review escalation flag
        any_requires_review = any(a.requires_human_review for a in anomalies)
        assert any_requires_review == exp_flags["human_review_required"]
        
        # 5. Verify Driver Investigation Contributions
        if expected.get("expected_top_drivers"):
            for exp_driver in expected["expected_top_drivers"]:
                dim = exp_driver["dimension"]
                val = exp_driver["value"]
                contrib = exp_driver["contribution"]
                
                drivers = investigate_anomaly_drivers(df, anomaly, dimensions=[dim])
                d_res = next((d for d in drivers if d.dimension == dim), None)
                assert d_res is not None
                
                c_res = next((c for c in d_res.top_contributors if c.value == val), None)
                assert c_res is not None
                assert pytest.approx(c_res.contribution_to_change, abs=1e-4) == contrib
    else:
        # For clean portfolio scenario
        assert len(anomalies) == 0
        assert exp_flags["anomaly_detected"] is False
