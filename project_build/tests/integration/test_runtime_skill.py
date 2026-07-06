from pathlib import Path

import pytest

from portfolio_agent.core.security import SecurityError, validate_file_path
from portfolio_agent.support.skill_context import (
    PORTFOLIO_SKILL_DIR,
    SkillContextError,
    build_review_instruction_context,
    load_portfolio_monitoring_reference,
)
from portfolio_agent.core.tools import (
    calculate_portfolio_metrics,
    detect_anomalies,
    load_portfolio_data,
    validate_portfolio_data,
)


def test_portfolio_monitoring_skill_files_exist_at_runtime_path():
    expected_files = [
        PORTFOLIO_SKILL_DIR / "SKILL.md",
        PORTFOLIO_SKILL_DIR / "references" / "actuarial_review_principles.md",
        PORTFOLIO_SKILL_DIR / "references" / "anomaly_thresholds.md",
        PORTFOLIO_SKILL_DIR / "assets" / "monthly_review_report_template.md",
    ]

    for file_path in expected_files:
        assert file_path.is_file(), f"Missing runtime skill file: {file_path}"


def test_runtime_instruction_context_contains_core_workflow_without_eager_references():
    context = build_review_instruction_context()

    assert "Validate the dataset before analysis" in context
    assert "Numeric calculations must still come from deterministic tools" in context
    assert "Never invent numbers" in context
    assert "Loss ratio increases by at least 20 points" not in context
    assert "# Monthly Portfolio Review Report" not in context


def test_optional_skill_references_fail_clearly_for_unknown_name():
    with pytest.raises(
        SkillContextError, match="Unknown portfolio-monitoring reference"
    ):
        load_portfolio_monitoring_reference("not_a_real_reference")


def test_skill_guidance_does_not_override_deterministic_results_or_path_policy():
    df = load_portfolio_data("tests/golden/loss_ratio_spike.csv")
    df, errors, warnings = validate_portfolio_data(df)
    assert errors == []
    assert warnings == []

    metrics = calculate_portfolio_metrics(df)
    anomalies = detect_anomalies(metrics, "2026-06")

    assert any(
        anomaly.metric == "loss_ratio"
        and anomaly.severity == "high"
        and anomaly.requires_human_review
        for anomaly in anomalies
    )

    with pytest.raises(SecurityError):
        validate_file_path(str(Path("skills/portfolio_monitoring/SKILL.md")))
