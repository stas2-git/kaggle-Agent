import pandas as pd
import pytest
from portfolio_agent.core.tools import calculate_portfolio_metrics, detect_anomalies, investigate_anomaly_drivers
from portfolio_agent.core.schemas import MetricsRecord, AnomalyRecord

def test_calculate_portfolio_metrics():
    # 1. Mock DataFrame
    data = {
        "valuation_month": ["2026-06", "2026-06"],
        "business_segment": ["Public D&O", "Public D&O"],
        "written_premium": [100000.0, 50000.0],
        "earned_premium": [80000.0, 40000.0],
        "incurred_loss": [40000.0, 30000.0],
        "claim_count": [2, 1],
        "account_count": [5, 3],
        "avg_retention": [100000.0, 200000.0],
        "rate_change_pct": [0.05, 0.10],
        "benchmark_adequacy": [1.0, 1.1],
        "coverage": ["D&O", "D&O"],
        "state": ["NY", "NJ"],
        "underwriter": ["UW_A", "UW_B"],
        "policy_year": [2025, 2025]
    }
    df = pd.DataFrame(data)
    
    # 2. Execute
    records = calculate_portfolio_metrics(df)
    
    assert len(records) == 1
    m = records[0]
    
    # 3. Assertions
    assert m.valuation_month == "2026-06"
    assert m.business_segment == "Public D&O"
    assert m.written_premium == 150000.0
    assert m.earned_premium == 120000.0
    assert m.incurred_loss == 70000.0
    assert m.claim_count == 3
    assert m.account_count == 8
    
    # Loss ratio = 70k / 120k = 58.333%
    assert pytest.approx(m.loss_ratio) == 70000.0 / 120000.0
    
    # Weighted average rate change (weights: 100k and 50k, total 150k)
    # rate_change = (100k * 0.05 + 50k * 0.10) / 150k = (5000 + 5000) / 150k = 10000 / 150000 = 6.667%
    assert pytest.approx(m.rate_change_pct) == 10000.0 / 150000.0
    
    # Weighted average retention
    # retention = (100k * 100k + 50k * 200k) / 150k = (10B + 10B) / 150k = 20B / 150k = 133,333.33
    assert pytest.approx(m.avg_retention) == 133333.3333

def test_calculate_portfolio_metrics_rejects_noncanonical_grouping():
    df = pd.DataFrame(
        {
            "valuation_month": ["2026-06"],
            "business_segment": ["Public D&O"],
            "written_premium": [100000.0],
            "earned_premium": [80000.0],
            "incurred_loss": [40000.0],
            "claim_count": [2],
            "account_count": [5],
            "avg_retention": [100000.0],
            "rate_change_pct": [0.05],
            "benchmark_adequacy": [1.0],
        }
    )

    with pytest.raises(ValueError, match="requires group_by"):
        calculate_portfolio_metrics(df, group_by=["valuation_month"])

def test_detect_anomalies():
    # 1. Setup metrics list (May 2026 vs June 2026)
    m_may = MetricsRecord(
        valuation_month="2026-05",
        business_segment="Public D&O",
        written_premium=100000.0,
        earned_premium=100000.0,
        incurred_loss=50000.0,  # LR = 50%
        claim_count=1,
        account_count=10,
        loss_ratio=0.50,
        rate_change_pct=0.05,
        benchmark_adequacy=1.0,
        avg_retention=250000.0
    )
    m_june = MetricsRecord(
        valuation_month="2026-06",
        business_segment="Public D&O",
        written_premium=100000.0,
        earned_premium=100000.0,
        incurred_loss=85000.0,  # LR = 85% (+35 pts spike)
        claim_count=1,  # held flat so this test isolates the loss-ratio anomaly only
        account_count=10,
        loss_ratio=0.85,
        rate_change_pct=0.05,
        benchmark_adequacy=1.0,
        avg_retention=250000.0
    )
    
    # 2. Execute
    anomalies = detect_anomalies([m_may, m_june], "2026-06")
    
    # 3. Assertions
    assert len(anomalies) == 1
    anom = anomalies[0]
    assert anom.metric == "loss_ratio"
    assert anom.business_segment == "Public D&O"
    assert anom.severity == "high"  # +35 pts spike exceeds +20 pts severe threshold
    assert anom.requires_human_review is True

def test_investigate_anomaly_drivers():
    # 1. Setup mock DataFrame
    data = {
        "valuation_month": ["2026-05", "2026-05", "2026-06", "2026-06"],
        "business_segment": ["Public D&O", "Public D&O", "Public D&O", "Public D&O"],
        "written_premium": [50000.0, 50000.0, 50000.0, 50000.0],
        "earned_premium": [50000.0, 50000.0, 50000.0, 50000.0],
        "incurred_loss": [10000.0, 40000.0, 10000.0, 75000.0],  # Total May loss = 50k, June loss = 85k (spike +35k)
        "claim_count": [1, 1, 1, 2],
        "account_count": [5, 5, 5, 5],
        "avg_retention": [250000.0, 250000.0, 250000.0, 250000.0],
        "rate_change_pct": [0.05, 0.05, 0.05, 0.05],
        "benchmark_adequacy": [1.0, 1.0, 1.0, 1.0],
        "state": ["NY", "NJ", "NY", "NJ"]
    }
    df = pd.DataFrame(data)
    
    anomaly = AnomalyRecord(
        anomaly_id="ANOM_2026-06_Public_D&O_LR",
        metric="loss_ratio",
        business_segment="Public D&O",
        current_value=0.85,
        prior_value=0.50,
        absolute_change=0.35,
        percent_change=0.70,
        severity="high",
        explanation="Loss ratio spike",
        requires_human_review=True
    )
    
    # 2. Execute
    drivers = investigate_anomaly_drivers(df, anomaly, dimensions=["state"])
    
    # 3. Assertions
    assert len(drivers) == 1
    d_state = drivers[0]
    assert d_state.dimension == "state"
    
    # NJ has the spike (May loss=40k -> June loss=75k, total earned=100k)
    # NJ contribution: 75k/100k - 40k/100k = +35.0 pts
    # NY has no change (May loss=10k -> June loss=10k, total earned=100k)
    # NY contribution: 10k/100k - 10k/100k = +0.0 pts
    
    nj_contrib = next(c for c in d_state.top_contributors if c.value == "NJ")
    ny_contrib = next(c for c in d_state.top_contributors if c.value == "NY")
    
    assert pytest.approx(nj_contrib.contribution_to_change) == 0.35
    assert pytest.approx(ny_contrib.contribution_to_change) == 0.00
