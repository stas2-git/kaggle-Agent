from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any

class MetricsRecord(BaseModel):
    valuation_month: str = Field(..., description="Month being reviewed YYYY-MM")
    business_segment: str = Field(..., description="Segment or product group name")
    written_premium: float = Field(..., description="Sum of written premium")
    earned_premium: float = Field(..., description="Sum of earned premium")
    incurred_loss: float = Field(..., description="Sum of incurred loss")
    claim_count: int = Field(..., description="Total claim count")
    account_count: int = Field(..., description="Total account count")
    loss_ratio: float = Field(..., description="Incurred loss / earned premium")
    rate_change_pct: float = Field(..., description="Weighted average rate change pct")
    benchmark_adequacy: float = Field(..., description="Weighted average benchmark adequacy index")
    avg_retention: float = Field(..., description="Weighted average retention deductible")

class AnomalyRecord(BaseModel):
    anomaly_id: str = Field(..., description="Unique identifier for the anomaly")
    metric: str = Field(..., description="Name of the affected metric (e.g., loss_ratio)")
    business_segment: str = Field(..., description="Segment where anomaly was detected")
    current_value: float = Field(..., description="Value in the latest valuation month")
    prior_value: float = Field(..., description="Value in the comparison month")
    absolute_change: float = Field(..., description="Absolute difference between current and prior")
    percent_change: float = Field(..., description="Percentage change from prior to current")
    severity: Literal["low", "moderate", "high"] = Field(..., description="Severity level of the anomaly")
    explanation: str = Field(..., description="Automatic description of the threshold breach")
    requires_human_review: bool = Field(..., description="True if anomaly meets severe conditions")

class DriverContributor(BaseModel):
    value: str = Field(..., description="Dimension value (e.g., 'NY', 'UW_A')")
    current_value: float = Field(..., description="Value in the current period")
    prior_value: float = Field(..., description="Value in the prior period")
    contribution_to_change: float = Field(..., description="Change in this segment's contribution to the overall metric")
    notes: Optional[str] = Field("", description="Optional comments or markers")

class DriverResult(BaseModel):
    anomaly_id: str = Field(..., description="Identifier of the related anomaly")
    dimension: str = Field(..., description="The sliced dimension name (e.g., 'state', 'underwriter')")
    top_contributors: List[DriverContributor] = Field(..., description="List of top contributor details")

class FindingDetail(BaseModel):
    anomaly_id: str = Field(..., description="ID of the investigated anomaly")
    metric: str = Field(..., description="Metric that changed")
    segment: str = Field(..., description="Affected business segment")
    observations: str = Field(..., description="Detailed observation of the trend and drivers")
    likely_cause_hypothesis: str = Field(..., description="Evidence-backed hypothesis of what caused the change")

class ReviewMemo(BaseModel):
    report_title: str = Field("Actuarial Portfolio Monitoring Memo", description="Title of the review memo")
    valuation_month: str = Field(..., description="Valuation month being reviewed")
    executive_summary: str = Field(..., description="Concise high-level summary of findings")
    finding_details: List[FindingDetail] = Field(..., description="Detailed notes on each investigated anomaly")
    recommended_followups: List[str] = Field(..., description="Concise follow-up questions for underwriters or managers")
    confidence: float = Field(..., description="Agent confidence score (1 to 5 scale)")
    requires_human_review: bool = Field(..., description="True if manual review or pricing adjustment is recommended")
