"""Runtime loading for the portfolio-monitoring Agent Skill."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PORTFOLIO_SKILL_DIR = PROJECT_ROOT / "skills" / "portfolio_monitoring"
SKILL_FILE = PORTFOLIO_SKILL_DIR / "SKILL.md"

REFERENCE_FILES = {
    "actuarial_review_principles": Path("references/actuarial_review_principles.md"),
    "anomaly_thresholds": Path("references/anomaly_thresholds.md"),
    "monthly_review_report_template": Path("assets/monthly_review_report_template.md"),
}


class SkillContextError(RuntimeError):
    """Raised when required runtime skill content is unavailable."""


def _read_required(path: Path) -> str:
    if not path.is_file():
        raise SkillContextError(f"Required portfolio-monitoring skill file is missing: {path}")
    return path.read_text(encoding="utf-8")


def load_portfolio_monitoring_skill() -> str:
    """Load the core runtime skill guidance for portfolio review requests."""

    return _read_required(SKILL_FILE)


def load_portfolio_monitoring_reference(name: str) -> str:
    """Load an optional portfolio-monitoring reference by known name."""

    relative_path = REFERENCE_FILES.get(name)
    if relative_path is None:
        allowed = ", ".join(sorted(REFERENCE_FILES))
        raise SkillContextError(f"Unknown portfolio-monitoring reference '{name}'. Allowed: {allowed}")
    return _read_required(PORTFOLIO_SKILL_DIR / relative_path)


def build_review_instruction_context(*, include_actuarial_principles: bool = False) -> str:
    """Build instruction context without loading threshold/template files prematurely."""

    parts = [load_portfolio_monitoring_skill()]
    if include_actuarial_principles:
        parts.append(load_portfolio_monitoring_reference("actuarial_review_principles"))
    return "\n\n".join(parts)
