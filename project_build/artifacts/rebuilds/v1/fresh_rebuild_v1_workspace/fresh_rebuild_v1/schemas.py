from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class MetricsRecord(BaseModel):
    valuation_month: str
    business_segment: str
    written_premium: float
    earned_premium: float
    incurred_loss: float
    claim_count: int
    account_count: int
    loss_ratio: float
    rate_change_pct: float
    benchmark_adequacy: float
    avg_retention: float

class Anomaly(BaseModel):
    anomaly_id: str
    metric: str
    business_segment: str
    current_value: float
    prior_value: float
    absolute_change: float
    percent_change: float
    severity: Literal["low", "moderate", "high"]
    explanation: str
    requires_human_review: bool

class Contributor(BaseModel):
    value: str
    current_value: float
    prior_value: float
    contribution_to_change: float
    notes: Optional[str] = None

class DriverResult(BaseModel):
    anomaly_id: str
    dimension: str
    top_contributors: List[Contributor]

class ReviewMemo(BaseModel):
    executive_summary: List[str]
    findings: List[str]
    recommended_followups: List[str]
    confidence_score: float
    requires_human_review: bool
