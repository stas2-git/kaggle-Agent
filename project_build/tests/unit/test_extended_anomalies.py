"""
Coverage for the claim_count, rate_change, and avg_retention anomaly/driver logic.

These three checks are defined in spec_files/20_contracts/01_data_spec_and_schemas.md
("Anomaly thresholds") and spec_files/60_skills/portfolio_monitoring/references/
anomaly_thresholds.md, but were not implemented in tools.py until this test was added
alongside the implementation (Gate 5 v2 spec-reconciliation pass).
"""

import pandas as pd
import pytest

from portfolio_agent.core.schemas import AnomalyRecord, MetricsRecord
from portfolio_agent.core.tools import detect_anomalies, investigate_anomaly_drivers


def _baseline_kwargs(**overrides):
    """A MetricsRecord that trips no anomaly on its own; callers override one field."""
    base = dict(
        valuation_month="2026-05",
        business_segment="Public D&O",
        written_premium=100000.0,
        earned_premium=100000.0,
        incurred_loss=50000.0,
        claim_count=10,
        account_count=10,
        loss_ratio=0.50,
        rate_change_pct=0.05,
        benchmark_adequacy=1.00,
        avg_retention=250000.0,
    )
    base.update(overrides)
    return base


def test_claim_count_anomaly_moderate_and_severe():
    m_pri = MetricsRecord(**_baseline_kwargs(valuation_month="2026-05", claim_count=10))

    # +30% -> moderate (>= 25%, < 50%)
    m_cur_moderate = MetricsRecord(**_baseline_kwargs(valuation_month="2026-06", claim_count=13))
    anomalies = detect_anomalies([m_pri, m_cur_moderate], "2026-06")
    cc = next(a for a in anomalies if a.metric == "claim_count")
    assert cc.severity == "moderate"
    assert cc.requires_human_review is False

    # +60% -> severe (>= 50%)
    m_cur_severe = MetricsRecord(**_baseline_kwargs(valuation_month="2026-06", claim_count=16))
    anomalies = detect_anomalies([m_pri, m_cur_severe], "2026-06")
    cc = next(a for a in anomalies if a.metric == "claim_count")
    assert cc.severity == "high"
    assert cc.requires_human_review is True


def test_rate_change_deterioration_moderate_and_severe():
    m_pri = MetricsRecord(**_baseline_kwargs(valuation_month="2026-05", rate_change_pct=0.05))

    # delta = -0.07 -> moderate (<= -0.05, > -0.10)
    m_cur_moderate = MetricsRecord(**_baseline_kwargs(valuation_month="2026-06", rate_change_pct=-0.02))
    anomalies = detect_anomalies([m_pri, m_cur_moderate], "2026-06")
    rc = next(a for a in anomalies if a.metric == "rate_change")
    assert rc.severity == "moderate"

    # delta = -0.11 -> severe (<= -0.10)
    m_cur_severe = MetricsRecord(**_baseline_kwargs(valuation_month="2026-06", rate_change_pct=-0.06))
    anomalies = detect_anomalies([m_pri, m_cur_severe], "2026-06")
    rc = next(a for a in anomalies if a.metric == "rate_change")
    assert rc.severity == "high"
    assert rc.requires_human_review is True


def test_retention_decrease_moderate_and_severe():
    m_pri = MetricsRecord(**_baseline_kwargs(valuation_month="2026-05", avg_retention=250000.0))

    # delta% = -12% -> moderate (<= -10%, > -25%)
    m_cur_moderate = MetricsRecord(**_baseline_kwargs(valuation_month="2026-06", avg_retention=220000.0))
    anomalies = detect_anomalies([m_pri, m_cur_moderate], "2026-06")
    ret = next(a for a in anomalies if a.metric == "avg_retention")
    assert ret.severity == "moderate"

    # delta% = -28% -> severe (<= -25%)
    m_cur_severe = MetricsRecord(**_baseline_kwargs(valuation_month="2026-06", avg_retention=180000.0))
    anomalies = detect_anomalies([m_pri, m_cur_severe], "2026-06")
    ret = next(a for a in anomalies if a.metric == "avg_retention")
    assert ret.severity == "high"
    assert ret.requires_human_review is True


def test_no_incidental_cross_metric_anomalies():
    """Baseline-vs-baseline (no change) must fire zero anomalies across all six metrics."""
    m_pri = MetricsRecord(**_baseline_kwargs(valuation_month="2026-05"))
    m_cur = MetricsRecord(**_baseline_kwargs(valuation_month="2026-06"))
    assert detect_anomalies([m_pri, m_cur], "2026-06") == []


def _two_dimension_df():
    return pd.DataFrame(
        {
            "valuation_month": ["2026-05", "2026-05", "2026-06", "2026-06"],
            "business_segment": ["Public D&O"] * 4,
            "written_premium": [50000.0, 50000.0, 50000.0, 50000.0],
            "earned_premium": [50000.0, 50000.0, 50000.0, 50000.0],
            "incurred_loss": [25000.0, 25000.0, 25000.0, 25000.0],
            "claim_count": [2, 3, 2, 6],
            "account_count": [5, 5, 5, 5],
            "avg_retention": [250000.0, 250000.0, 250000.0, 150000.0],
            "rate_change_pct": [0.05, 0.05, 0.05, -0.10],
            "benchmark_adequacy": [1.0, 1.0, 1.0, 1.0],
            "state": ["NY", "NJ", "NY", "NJ"],
        }
    )


def test_claim_count_driver_contribution_is_additive():
    df = _two_dimension_df()
    anomaly = AnomalyRecord(
        anomaly_id="ANOM_2026-06_Public_D&O_CC",
        metric="claim_count",
        business_segment="Public D&O",
        current_value=8,
        prior_value=5,
        absolute_change=3,
        percent_change=0.6,
        severity="high",
        explanation="Claim count spike",
        requires_human_review=True,
    )
    drivers = investigate_anomaly_drivers(df, anomaly, dimensions=["state"])
    d_state = next(d for d in drivers if d.dimension == "state")

    ny = next(c for c in d_state.top_contributors if c.value == "NY")
    nj = next(c for c in d_state.top_contributors if c.value == "NJ")

    # contribution_k = (cur_k - pri_k) / pri_total ; pri_total = 5
    assert pytest.approx(ny.contribution_to_change) == 0.0
    assert pytest.approx(nj.contribution_to_change) == (6 - 3) / 5


def test_rate_change_and_retention_driver_contribution_is_premium_weighted():
    df = _two_dimension_df()

    rc_anomaly = AnomalyRecord(
        anomaly_id="ANOM_2026-06_Public_D&O_RC",
        metric="rate_change",
        business_segment="Public D&O",
        current_value=-0.025,
        prior_value=0.05,
        absolute_change=-0.075,
        percent_change=-1.5,
        severity="high",
        explanation="Rate change deterioration",
        requires_human_review=True,
    )
    drivers = investigate_anomaly_drivers(df, rc_anomaly, dimensions=["state"])
    d_state = next(d for d in drivers if d.dimension == "state")
    ny = next(c for c in d_state.top_contributors if c.value == "NY")
    nj = next(c for c in d_state.top_contributors if c.value == "NJ")

    # equal 50/50 premium shares both periods -> contribution = 0.5*cur - 0.5*pri
    assert pytest.approx(ny.contribution_to_change) == (0.5 * 0.05) - (0.5 * 0.05)
    assert pytest.approx(nj.contribution_to_change) == (0.5 * -0.10) - (0.5 * 0.05)

    ret_anomaly = AnomalyRecord(
        anomaly_id="ANOM_2026-06_Public_D&O_RET",
        metric="avg_retention",
        business_segment="Public D&O",
        current_value=200000.0,
        prior_value=250000.0,
        absolute_change=-50000.0,
        percent_change=-0.20,
        severity="high",
        explanation="Retention decrease",
        requires_human_review=True,
    )
    drivers = investigate_anomaly_drivers(df, ret_anomaly, dimensions=["state"])
    d_state = next(d for d in drivers if d.dimension == "state")
    ny = next(c for c in d_state.top_contributors if c.value == "NY")
    nj = next(c for c in d_state.top_contributors if c.value == "NJ")

    assert pytest.approx(ny.contribution_to_change) == (0.5 * 250000.0) - (0.5 * 250000.0)
    assert pytest.approx(nj.contribution_to_change) == (0.5 * 150000.0) - (0.5 * 250000.0)
