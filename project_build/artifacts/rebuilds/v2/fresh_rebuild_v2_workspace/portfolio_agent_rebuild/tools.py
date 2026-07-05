"""Deterministic tool layer.

Implements the tools defined in spec_files/20_contracts/02_tool_contracts.yaml:
load_portfolio_data, validate_portfolio_data, calculate_portfolio_metrics,
detect_anomalies, investigate_anomaly_drivers.

Per the contract rule `opaque_refs_resolve_only_inside_authorized_runtime_state`,
data never crosses tool boundaries as raw values the "model" could fabricate --
callers pass around opaque string refs that resolve inside a RunContext registry.
This rebuild has no live ADK/LLM, so RunContext stands in for ADK's ToolContext
(10_core/02_agent_architecture.md, "ToolContext: hold opaque dataset references").
"""

from __future__ import annotations

import itertools
import os
import uuid
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from .schemas import (
    ALLOWED_DRIVER_DIMENSIONS,
    DEFAULT_THRESHOLDS,
    NUMERIC_REQUIRED_COLUMNS,
    REQUIRED_COLUMNS,
    Anomaly,
    DriverContributor,
    DriverResult,
    MetricsRecord,
)
from .security import scan_for_prompt_injection, validate_input_path


@dataclass
class RunContext:
    """Stand-in for ADK ToolContext: holds opaque refs -> real objects."""

    workspace_root: str
    dataframes: dict[str, pd.DataFrame] = field(default_factory=dict)
    metrics: dict[str, list[MetricsRecord]] = field(default_factory=dict)
    anomalies: dict[str, list[Anomaly]] = field(default_factory=dict)
    drivers: dict[str, list[DriverResult]] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)
    security_flags: list[dict[str, Any]] = field(default_factory=list)
    _event_counter: itertools.count = field(default_factory=lambda: itertools.count(1))

    def new_ref(self, prefix: str) -> str:
        return f"{prefix}_{uuid.uuid4().hex[:8]}"

    def log_event(
        self,
        event_type: str,
        name: str,
        input_summary: dict | None = None,
        output_summary: dict | None = None,
        status: str = "completed",
        duration_ms: int = 0,
        invocation_id: str = "invocation_0",
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        event = {
            "event_id": next(self._event_counter),
            "invocation_id": invocation_id,
            "correlation_id": correlation_id,
            "timestamp": _now_iso(),
            "event_type": event_type,
            "name": name,
            "input_summary": input_summary or {},
            "output_summary": output_summary or {},
            "status": status,
            "duration_ms": duration_ms,
        }
        self.events.append(event)
        return event


def _now_iso() -> str:
    import datetime

    return datetime.datetime.now(datetime.timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Tool: load_portfolio_data
# ---------------------------------------------------------------------------

def load_portfolio_data(file_path: str, ctx: RunContext) -> dict[str, Any]:
    call_id = ctx.new_ref("call")
    ctx.log_event(
        "function_call", "load_portfolio_data", {"file_path": file_path}, invocation_id=call_id
    )
    try:
        validate_input_path(file_path, ctx.workspace_root)
    except Exception as exc:
        ctx.log_event(
            "function_response",
            "load_portfolio_data",
            output_summary={"error": "path_not_allowed", "detail": str(exc)},
            status="failed",
            invocation_id=call_id,
        )
        ctx.security_flags.append(
            {
                "flag_type": "forbidden_path",
                "severity": "high",
                "source": "tool_output",
                "description": str(exc),
                "action_taken": "blocked",
            }
        )
        raise

    abs_path = file_path if os.path.isabs(file_path) else os.path.join(ctx.workspace_root, file_path)
    if not os.path.exists(abs_path):
        ctx.log_event(
            "function_response",
            "load_portfolio_data",
            output_summary={"error": "file_not_found"},
            status="failed",
            invocation_id=call_id,
        )
        raise FileNotFoundError(f"file_not_found: {file_path}")

    try:
        df = pd.read_csv(abs_path)
    except Exception as exc:  # pragma: no cover - defensive
        ctx.log_event(
            "function_response",
            "load_portfolio_data",
            output_summary={"error": "csv_parse_error", "detail": str(exc)},
            status="failed",
            invocation_id=call_id,
        )
        raise

    dataframe_ref = ctx.new_ref("df")
    ctx.dataframes[dataframe_ref] = df
    result = {
        "dataset_id": os.path.basename(file_path),
        "row_count": int(len(df)),
        "columns": list(df.columns),
        "dataframe_ref": dataframe_ref,
    }
    ctx.log_event(
        "function_response",
        "load_portfolio_data",
        output_summary=result,
        invocation_id=call_id,
    )
    return result


# ---------------------------------------------------------------------------
# Tool: validate_portfolio_data
# ---------------------------------------------------------------------------

def validate_portfolio_data(dataframe_ref: str, ctx: RunContext) -> dict[str, Any]:
    call_id = ctx.new_ref("call")
    ctx.log_event(
        "function_call", "validate_portfolio_data", {"dataframe_ref": dataframe_ref}, invocation_id=call_id
    )
    df = ctx.dataframes[dataframe_ref]
    blocking_errors: list[str] = []
    warnings: list[str] = []
    injection_flags: list[dict[str, Any]] = []

    if df.empty:
        blocking_errors.append("empty_dataset")

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        blocking_errors.append(f"missing_required_column: {missing_cols}")

    if not missing_cols and not df.empty:
        # valuation_month parseable as YYYY-MM
        try:
            pd.to_datetime(df["valuation_month"], format="%Y-%m")
        except Exception:
            blocking_errors.append("valuation_month_unparseable")

        for col in NUMERIC_REQUIRED_COLUMNS:
            if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
                coerced = pd.to_numeric(df[col], errors="coerce")
                if coerced.isna().any():
                    blocking_errors.append(f"non_numeric_values_in_{col}")

        grouping_cols = ["business_segment", "coverage", "state", "underwriter"]
        for col in grouping_cols:
            if col in df.columns and df[col].isna().any():
                warnings.append(f"null_values_in_{col}")

        if (df["written_premium"] < 0).any() or (df["claim_count"] < 0).any():
            warnings.append("negative_premium_or_claim_count")

        if ((df["earned_premium"] == 0) & (df["incurred_loss"] != 0)).any():
            warnings.append("earned_premium_zero_with_incurred_loss")

        if "notes" in df.columns:
            for idx, note in df["notes"].items():
                matches = scan_for_prompt_injection(note)
                if matches:
                    warnings.append(f"suspicious_text_in_notes_row_{idx}")
                    flag = {
                        "flag_type": "prompt_injection",
                        "severity": "high",
                        "source": "data_field",
                        "description": f"row {idx} notes matched pattern(s): {matches}",
                        "action_taken": "human_review_required",
                    }
                    injection_flags.append(flag)
                    ctx.security_flags.append(flag)

    status = "fail" if blocking_errors else ("pass_with_warnings" if warnings else "pass")
    result = {
        "status": status,
        "blocking_errors": blocking_errors,
        "warnings": warnings,
        "row_count": int(len(df)),
        "valid_row_count": int(len(df)) if status != "fail" else 0,
        "injection_flags": injection_flags,
    }
    ctx.log_event("function_response", "validate_portfolio_data", output_summary=result, invocation_id=call_id)
    return result


# ---------------------------------------------------------------------------
# Tool: calculate_portfolio_metrics
# ---------------------------------------------------------------------------

def _weighted_avg(group: pd.DataFrame, value_col: str, weight_col: str = "written_premium") -> float:
    weights = group[weight_col]
    total_weight = weights.sum()
    if total_weight == 0:
        return float(group[value_col].mean()) if len(group) else 0.0
    return float((group[value_col] * weights).sum() / total_weight)


def _metrics_for_group(month: str, segment: str, group: pd.DataFrame) -> MetricsRecord:
    written_premium = float(group["written_premium"].sum())
    earned_premium = float(group["earned_premium"].sum())
    incurred_loss = float(group["incurred_loss"].sum())
    claim_count = float(group["claim_count"].sum())
    account_count = float(group["account_count"].sum())
    loss_ratio = incurred_loss / earned_premium if earned_premium else 0.0
    rate_change_pct = _weighted_avg(group, "rate_change_pct")
    benchmark_adequacy = _weighted_avg(group, "benchmark_adequacy")
    avg_retention = _weighted_avg(group, "avg_retention")
    return MetricsRecord(
        valuation_month=month,
        business_segment=segment,
        written_premium=written_premium,
        earned_premium=earned_premium,
        incurred_loss=incurred_loss,
        claim_count=claim_count,
        account_count=account_count,
        loss_ratio=loss_ratio,
        rate_change_pct=rate_change_pct,
        benchmark_adequacy=benchmark_adequacy,
        avg_retention=avg_retention,
    )


def calculate_portfolio_metrics(
    dataframe_ref: str, group_by: list[str], ctx: RunContext
) -> dict[str, Any]:
    call_id = ctx.new_ref("call")
    ctx.log_event(
        "function_call",
        "calculate_portfolio_metrics",
        {"dataframe_ref": dataframe_ref, "group_by": group_by},
        invocation_id=call_id,
    )
    df = ctx.dataframes[dataframe_ref]
    calculation_warnings: list[str] = []

    records: list[MetricsRecord] = []
    if "business_segment" in group_by:
        for (month, segment), group in df.groupby(["valuation_month", "business_segment"]):
            records.append(_metrics_for_group(month, segment, group))
    else:
        for month, group in df.groupby("valuation_month"):
            records.append(_metrics_for_group(month, "ALL", group))

    metrics_ref = ctx.new_ref("metrics")
    ctx.metrics[metrics_ref] = records
    result = {
        "metrics_ref": metrics_ref,
        "metrics_records": [r.to_dict() for r in records],
        "calculation_warnings": calculation_warnings,
    }
    ctx.log_event(
        "function_response",
        "calculate_portfolio_metrics",
        output_summary={"metrics_ref": metrics_ref, "record_count": len(records)},
        invocation_id=call_id,
    )
    return result


def calculate_portfolio_totals(dataframe_ref: str, ctx: RunContext) -> dict[str, MetricsRecord]:
    """Portfolio-wide (all segments combined) metrics keyed by valuation_month.

    Spec-gap note (see fresh_rebuild_v2.md): the data spec's derived-metrics table
    computes sums "by month/segment" (segment grain), but the "Key metric movement"
    table in 20_contracts/04_output_report_template.md and the comparison-metrics
    section ("Latest month vs previous month") show a single portfolio-wide row with
    no segment dimension. We compute both grains: this function for the headline
    portfolio comparison, and calculate_portfolio_metrics(group_by=[...,'business_segment'])
    for the canonical per-segment grain used in driver decomposition.
    """
    df = ctx.dataframes[dataframe_ref]
    totals: dict[str, MetricsRecord] = {}
    for month, group in df.groupby("valuation_month"):
        totals[str(month)] = _metrics_for_group(str(month), "ALL", group)
    return totals


# ---------------------------------------------------------------------------
# Tool: detect_anomalies
# ---------------------------------------------------------------------------

# metric_key -> (compute_delta(current, prior) -> float, direction, severity_key)
def _metric_configs():
    return {
        "loss_ratio": {
            "delta": lambda cur, pri: cur.loss_ratio - pri.loss_ratio,
            "direction": "increase_only",
            "threshold_key": "loss_ratio_change_points",
            "label": "Loss ratio",
        },
        "written_premium": {
            "delta": lambda cur, pri: (
                (cur.written_premium - pri.written_premium) / pri.written_premium
                if pri.written_premium
                else 0.0
            ),
            "direction": "both",
            "threshold_key": "written_premium_change_pct",
            "label": "Written premium",
        },
        "claim_count": {
            "delta": lambda cur, pri: (
                (cur.claim_count - pri.claim_count) / pri.claim_count if pri.claim_count else 0.0
            ),
            "direction": "increase_only",
            "threshold_key": "claim_count_change_pct",
            "label": "Claim count",
        },
        "rate_change_pct": {
            "delta": lambda cur, pri: cur.rate_change_pct - pri.rate_change_pct,
            "direction": "decrease_only",
            "threshold_key": "rate_change_deterioration_points",
            "label": "Rate change",
        },
        "benchmark_adequacy": {
            "delta": lambda cur, pri: cur.benchmark_adequacy - pri.benchmark_adequacy,
            "direction": "decrease_only",
            "threshold_key": "benchmark_adequacy_deterioration",
            "label": "Benchmark adequacy",
            "anomaly_type": "rate_adequacy",
        },
        "avg_retention": {
            "delta": lambda cur, pri: (
                (cur.avg_retention - pri.avg_retention) / pri.avg_retention if pri.avg_retention else 0.0
            ),
            "direction": "decrease_only",
            "threshold_key": "avg_retention_decrease_pct",
            "label": "Average retention",
        },
    }


def _severity_for(delta: float, direction: str, thresholds: dict[str, float]) -> str | None:
    moderate = thresholds["moderate"]
    high = thresholds["high"]
    if direction == "increase_only":
        magnitude = delta
    elif direction == "decrease_only":
        magnitude = -delta
    else:  # both
        magnitude = abs(delta)
    if magnitude >= high:
        return "high"
    if magnitude >= moderate:
        return "moderate"
    return None


def detect_anomalies(
    metrics_ref: str,
    latest_month: str,
    ctx: RunContext,
    threshold_config: dict | None = None,
    business_segment_label: str | None = None,
) -> dict[str, Any]:
    call_id = ctx.new_ref("call")
    ctx.log_event(
        "function_call",
        "detect_anomalies",
        {"metrics_ref": metrics_ref, "latest_month": latest_month},
        invocation_id=call_id,
    )
    thresholds = threshold_config or DEFAULT_THRESHOLDS
    records = ctx.metrics[metrics_ref]
    months = sorted({r.valuation_month for r in records})
    if latest_month not in months:
        ctx.log_event(
            "function_response",
            "detect_anomalies",
            output_summary={"error": "no_comparison_period"},
            status="failed",
            invocation_id=call_id,
        )
        raise ValueError("no_comparison_period: latest_month not present in metrics")
    idx = months.index(latest_month)
    if idx == 0:
        ctx.log_event(
            "function_response",
            "detect_anomalies",
            output_summary={"error": "no_comparison_period"},
            status="failed",
            invocation_id=call_id,
        )
        raise ValueError("no_comparison_period: no prior month available before latest_month")
    prior_month = months[idx - 1]

    current = next(r for r in records if r.valuation_month == latest_month)
    prior = next(r for r in records if r.valuation_month == prior_month)
    segment_label = business_segment_label or current.business_segment

    anomalies: list[Anomaly] = []
    for metric_key, cfg in _metric_configs().items():
        delta = cfg["delta"](current, prior)
        severity = _severity_for(delta, cfg["direction"], thresholds[cfg["threshold_key"]])
        if severity is None:
            continue
        cur_val = getattr(current, metric_key)
        pri_val = getattr(prior, metric_key)
        pct_change = (cur_val - pri_val) / pri_val if pri_val else None
        anomaly = Anomaly(
            anomaly_id=ctx.new_ref("anomaly"),
            metric=metric_key,
            business_segment=segment_label,
            current_value=cur_val,
            prior_value=pri_val,
            absolute_change=cur_val - pri_val,
            percent_change=pct_change,
            severity=severity,
            explanation=(
                f"{cfg['label']} moved from {pri_val:.4f} to {cur_val:.4f} "
                f"({latest_month} vs {prior_month}), a {severity} severity movement."
            ),
            requires_human_review=(severity == "high"),
            anomaly_type=cfg.get("anomaly_type"),
        )
        anomalies.append(anomaly)

    anomaly_ref = ctx.new_ref("anom")
    ctx.anomalies[anomaly_ref] = anomalies
    summary_counts = {
        "total": len(anomalies),
        "moderate": sum(1 for a in anomalies if a.severity == "moderate"),
        "high": sum(1 for a in anomalies if a.severity == "high"),
    }
    result = {
        "anomaly_ref": anomaly_ref,
        "anomalies": [a.to_dict() for a in anomalies],
        "summary_counts": summary_counts,
        "latest_month": latest_month,
        "prior_month": prior_month,
    }
    ctx.log_event(
        "function_response",
        "detect_anomalies",
        output_summary={"anomaly_ref": anomaly_ref, "summary_counts": summary_counts},
        invocation_id=call_id,
    )
    return result


# ---------------------------------------------------------------------------
# Tool: investigate_anomaly_drivers
# ---------------------------------------------------------------------------

def investigate_anomaly_drivers(
    dataframe_ref: str,
    anomaly: Anomaly,
    dimensions: list[str],
    ctx: RunContext,
    latest_month: str,
    prior_month: str,
    top_n: int = 5,
) -> dict[str, Any]:
    call_id = ctx.new_ref("call")
    ctx.log_event(
        "function_call",
        "investigate_anomaly_drivers",
        {"anomaly_id": anomaly.anomaly_id, "dimensions": dimensions},
        invocation_id=call_id,
    )
    bad_dims = [d for d in dimensions if d not in ALLOWED_DRIVER_DIMENSIONS]
    if bad_dims:
        ctx.log_event(
            "policy_decision",
            "before_tool",
            output_summary={"decision": "block", "policy": "path_and_dimension_allowlist", "reason_code": "dimension_not_available"},
            invocation_id=call_id,
        )
        ctx.log_event(
            "function_response",
            "investigate_anomaly_drivers",
            output_summary={"error": "dimension_not_available", "bad_dims": bad_dims},
            status="failed",
            invocation_id=call_id,
        )
        raise ValueError(f"dimension_not_available: {bad_dims}")

    df = ctx.dataframes[dataframe_ref]
    metric_key = anomaly.metric
    cur_df = df[df["valuation_month"] == latest_month]
    pri_df = df[df["valuation_month"] == prior_month]

    driver_results: list[DriverResult] = []
    caveats: list[str] = []
    if len(cur_df["business_segment"].unique()) <= 1 and len(dimensions) > 0:
        caveats.append(
            "Only one business_segment present in the source data; driver slices are not credibility-weighted."
        )

    for dim in dimensions:
        contributors: list[DriverContributor] = []
        cur_group = cur_df.groupby(dim)
        pri_group = pri_df.groupby(dim)
        values = set(cur_df[dim].unique()) | set(pri_df[dim].unique())

        if metric_key == "loss_ratio":
            pri_earned_total = pri_df["earned_premium"].sum()
            cur_earned_total = cur_df["earned_premium"].sum()
            for v in values:
                cur_slice = cur_group.get_group(v) if v in cur_group.groups else cur_df.iloc[0:0]
                pri_slice = pri_group.get_group(v) if v in pri_group.groups else pri_df.iloc[0:0]
                cur_share = (
                    cur_slice["incurred_loss"].sum() / cur_earned_total if cur_earned_total else 0.0
                )
                pri_share = (
                    pri_slice["incurred_loss"].sum() / pri_earned_total if pri_earned_total else 0.0
                )
                contribution = cur_share - pri_share
                contributors.append(
                    DriverContributor(
                        value=str(v),
                        current_value=float(cur_slice["incurred_loss"].sum() / cur_slice["earned_premium"].sum())
                        if len(cur_slice) and cur_slice["earned_premium"].sum()
                        else 0.0,
                        prior_value=float(pri_slice["incurred_loss"].sum() / pri_slice["earned_premium"].sum())
                        if len(pri_slice) and pri_slice["earned_premium"].sum()
                        else 0.0,
                        contribution_to_change=float(contribution),
                        notes="Contribution = change in (segment incurred loss / total earned premium).",
                    )
                )
        elif metric_key == "written_premium":
            pri_total = pri_df["written_premium"].sum()
            for v in values:
                cur_slice = cur_group.get_group(v) if v in cur_group.groups else cur_df.iloc[0:0]
                pri_slice = pri_group.get_group(v) if v in pri_group.groups else pri_df.iloc[0:0]
                cur_wp = float(cur_slice["written_premium"].sum())
                pri_wp = float(pri_slice["written_premium"].sum())
                contribution = (cur_wp - pri_wp) / pri_total if pri_total else 0.0
                contributors.append(
                    DriverContributor(
                        value=str(v),
                        current_value=cur_wp,
                        prior_value=pri_wp,
                        contribution_to_change=float(contribution),
                        notes="Contribution = segment premium change / prior total portfolio premium.",
                    )
                )
        else:
            # weighted-average style metrics: benchmark_adequacy, rate_change_pct, claim_count, avg_retention
            weight_col = "written_premium"
            cur_total_w = cur_df[weight_col].sum()
            pri_total_w = pri_df[weight_col].sum()
            for v in values:
                cur_slice = cur_group.get_group(v) if v in cur_group.groups else cur_df.iloc[0:0]
                pri_slice = pri_group.get_group(v) if v in pri_group.groups else pri_df.iloc[0:0]
                if metric_key == "claim_count":
                    cur_val = float(cur_slice["claim_count"].sum())
                    pri_val = float(pri_slice["claim_count"].sum())
                    pri_metric_total = pri_df["claim_count"].sum()
                    contribution = (cur_val - pri_val) / pri_metric_total if pri_metric_total else 0.0
                else:
                    cur_val = _weighted_avg(cur_slice, metric_key, weight_col) if len(cur_slice) else 0.0
                    pri_val = _weighted_avg(pri_slice, metric_key, weight_col) if len(pri_slice) else 0.0
                    cur_w_share = (cur_slice[weight_col].sum() / cur_total_w) if cur_total_w else 0.0
                    pri_w_share = (pri_slice[weight_col].sum() / pri_total_w) if pri_total_w else 0.0
                    contribution = (cur_val * cur_w_share) - (pri_val * pri_w_share)
                contributors.append(
                    DriverContributor(
                        value=str(v),
                        current_value=float(cur_val),
                        prior_value=float(pri_val),
                        contribution_to_change=float(contribution),
                        notes="Contribution = premium-weighted current share minus premium-weighted prior share.",
                    )
                )

        contributors.sort(key=lambda c: abs(c.contribution_to_change), reverse=True)
        driver_results.append(
            DriverResult(anomaly_id=anomaly.anomaly_id, dimension=dim, top_contributors=contributors[:top_n])
        )

    driver_ref = ctx.new_ref("driver")
    ctx.drivers[driver_ref] = driver_results
    result = {
        "driver_ref": driver_ref,
        "driver_results": [d.to_dict() for d in driver_results],
        "caveats": caveats,
    }
    ctx.log_event(
        "function_response",
        "investigate_anomaly_drivers",
        output_summary={"driver_ref": driver_ref, "dimensions": dimensions},
        invocation_id=call_id,
    )
    return result
