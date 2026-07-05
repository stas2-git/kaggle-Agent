"""Configuration for the portfolio monitoring agent.

This module centralizes values that were previously scattered across the CLI.
It intentionally avoids constructing external clients so it is safe to import in
offline tests and local tooling.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


ExecutionMode = Literal["online", "offline"]

DEFAULT_MODEL_NAME = "gemini-2.5-flash"
APPLICATION_NAME = "portfolio_agent"
DEFAULT_THRESHOLD_PROFILE = "default_actuarial_config"


@dataclass(frozen=True)
class PortfolioAgentConfig:
    application_name: str = APPLICATION_NAME
    model_name: str = DEFAULT_MODEL_NAME
    execution_mode: ExecutionMode = "online"
    project_root: Path = Path.cwd()
    reports_dir: Path = Path("outputs/reports")
    traces_dir: Path = Path("outputs/traces")
    threshold_profile: str = DEFAULT_THRESHOLD_PROFILE

    @property
    def approved_roots(self) -> tuple[Path, ...]:
        root = self.project_root.resolve()
        return (
            root,
            (root / "tests" / "golden").resolve(),
            (root / "data").resolve(),
        )


def load_config(
    *,
    model_name: str | None = None,
    force_offline: bool = False,
    project_root: str | Path | None = None,
) -> PortfolioAgentConfig:
    """Load runtime configuration from explicit values and environment."""

    root = Path(project_root or os.environ.get("PORTFOLIO_AGENT_PROJECT_ROOT", ".")).resolve()
    env_mode = os.environ.get("PORTFOLIO_AGENT_EXECUTION_MODE", "online").strip().lower()
    execution_mode: ExecutionMode = "offline" if force_offline or env_mode == "offline" else "online"

    return PortfolioAgentConfig(
        model_name=model_name or os.environ.get("PORTFOLIO_AGENT_MODEL", DEFAULT_MODEL_NAME),
        execution_mode=execution_mode,
        project_root=root,
        reports_dir=Path(os.environ.get("PORTFOLIO_AGENT_REPORTS_DIR", "outputs/reports")),
        traces_dir=Path(os.environ.get("PORTFOLIO_AGENT_TRACES_DIR", "outputs/traces")),
        threshold_profile=os.environ.get(
            "PORTFOLIO_AGENT_THRESHOLD_PROFILE", DEFAULT_THRESHOLD_PROFILE
        ),
    )
