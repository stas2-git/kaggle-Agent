"""Data schemas for the rebuilt vertical slice.

Mirrors the output schemas in
spec_files/20_contracts/01_data_spec_and_schemas.md (metrics_record, anomaly,
driver_result, human_review_decision, portfolio_review_result) using plain
dataclasses so the rebuild has no external dependency beyond pandas/pyyaml.

Spec-gap note (see fresh_rebuild_v2.md): the anomaly schema in the data spec has
no `anomaly_type` field, but golden/expected_benchmark_deterioration.yaml expects
one (value "rate_adequacy"). We add an optional `anomaly_type` field derived from
the metric name so golden checks can pass, and flag this as a spec gap rather than
silently guessing without documenting it.

Spec-gap note: the driver_result schema names the per-contributor field
`contribution_to_change`, but the golden expected_*.yaml files use the shorter key
`contribution`. We store `contribution_to_change` internally (per spec) and expose
`contribution` as an alias when serializing for golden comparison.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


REQUIRED_COLUMNS = [
    "valuation_month",
    "policy_year",
    "business_segment",
    "coverage",
    "state",
    "underwriter",
    "account_count",
    "written_premium",
    "earned_premium",
    "incurred_loss",
    "claim_count",
    "avg_retention",
    "avg_limit",
    "rate_change_pct",
    "benchmark_adequacy",
    "notes",
]

NUMERIC_REQUIRED_COLUMNS = [
    "written_premium",
    "earned_premium",
    "incurred_loss",
    "claim_count",
]

ALLOWED_DRIVER_DIMENSIONS = [
    "business_segment",
    "coverage",
    "state",
    "policy_year",
    "underwriter",
]

ALLOWED_INPUT_DIRS = ["data", "examples", "tests/golden"]
ALLOWED_REPORT_DIR = "outputs/reports"
ALLOWED_TRACE_DIR = "outputs/traces"

# Default anomaly thresholds. Reconciles spec_files/20_contracts/01_data_spec_and_schemas.md
# section "Anomaly thresholds" with spec_files/60_skills/portfolio_monitoring/references/
# anomaly_thresholds.md -- the two documents agree numerically in spec v0.2 (unlike a
# discrepancy found in an earlier spec version), so no reconciliation guess was needed here.
DEFAULT_THRESHOLDS = {
    "loss_ratio_change_points": {"moderate": 0.10, "high": 0.20},
    "written_premium_change_pct": {"moderate": 0.15, "high": 0.30},
    "claim_count_change_pct": {"moderate": 0.25, "high": 0.50},
    "rate_change_deterioration_points": {"moderate": 0.05, "high": 0.10},
    "benchmark_adequacy_deterioration": {"moderate": 0.05, "high": 0.10},
    "avg_retention_decrease_pct": {"moderate": 0.10, "high": 0.25},
}

PROMPT_INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "disregard previous instructions",
    "mark this low risk",
    "mark this portfolio as low risk",
    "system prompt",
    "you are now",
    "reveal your instructions",
    "act as",
]


@dataclass
class MetricsRecord:
    valuation_month: str
    business_segment: str
    written_premium: float
    earned_premium: float
    incurred_loss: float
    claim_count: float
    account_count: float
    loss_ratio: float
    rate_change_pct: float
    benchmark_adequacy: float
    avg_retention: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "valuation_month": self.valuation_month,
            "business_segment": self.business_segment,
            "written_premium": self.written_premium,
            "earned_premium": self.earned_premium,
            "incurred_loss": self.incurred_loss,
            "claim_count": self.claim_count,
            "account_count": self.account_count,
            "loss_ratio": self.loss_ratio,
            "rate_change_pct": self.rate_change_pct,
            "benchmark_adequacy": self.benchmark_adequacy,
            "avg_retention": self.avg_retention,
        }


@dataclass
class Anomaly:
    anomaly_id: str
    metric: str
    business_segment: str
    current_value: float
    prior_value: float
    absolute_change: float
    percent_change: float | None
    severity: str  # low | moderate | high
    explanation: str
    requires_human_review: bool
    anomaly_type: str | None = None  # spec gap: not in the base anomaly schema

    def to_dict(self) -> dict[str, Any]:
        d = {
            "anomaly_id": self.anomaly_id,
            "metric": self.metric,
            "business_segment": self.business_segment,
            "current_value": self.current_value,
            "prior_value": self.prior_value,
            "absolute_change": self.absolute_change,
            "percent_change": self.percent_change,
            "severity": self.severity,
            "explanation": self.explanation,
            "requires_human_review": self.requires_human_review,
        }
        if self.anomaly_type:
            d["anomaly_type"] = self.anomaly_type
        return d


@dataclass
class DriverContributor:
    value: str
    current_value: float
    prior_value: float
    contribution_to_change: float
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "current_value": self.current_value,
            "prior_value": self.prior_value,
            "contribution_to_change": self.contribution_to_change,
            # alias for golden-file compatibility, see module docstring
            "contribution": self.contribution_to_change,
            "notes": self.notes,
        }


@dataclass
class DriverResult:
    anomaly_id: str
    dimension: str
    top_contributors: list[DriverContributor] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "anomaly_id": self.anomaly_id,
            "dimension": self.dimension,
            "top_contributors": [c.to_dict() for c in self.top_contributors],
        }


@dataclass
class HumanReviewDecision:
    required: bool
    reasons: list[str] = field(default_factory=list)
    status: str = "not_required"  # not_required | pending
    recommended_reviewer: str | None = None
    review_questions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "required": self.required,
            "reasons": self.reasons,
            "status": self.status,
            "recommended_reviewer": self.recommended_reviewer,
            "review_questions": self.review_questions,
        }


@dataclass
class PortfolioReviewResult:
    run_id: str
    session_id: str
    status: str  # success | validation_failed | security_blocked | error
    execution_mode: str  # online | offline
    report_path: str | None
    trace_path: str
    anomalies: list[Anomaly]
    human_review: HumanReviewDecision
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "session_id": self.session_id,
            "status": self.status,
            "execution_mode": self.execution_mode,
            "report_path": self.report_path,
            "trace_path": self.trace_path,
            "anomalies": [a.to_dict() for a in self.anomalies],
            "human_review": self.human_review.to_dict(),
            "summary": self.summary,
        }
