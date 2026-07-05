"""JSON-safe ADK tool adapters over the deterministic portfolio engine."""

from __future__ import annotations

from typing import Any, MutableMapping
from uuid import uuid4

from google.adk.tools import ToolContext
from pydantic import BaseModel

from portfolio_agent.support.config import load_config
from portfolio_agent.core.tools import (
    calculate_portfolio_metrics as calculate_metrics_engine,
    detect_anomalies as detect_anomalies_engine,
    investigate_anomaly_drivers as investigate_drivers_engine,
    load_portfolio_data as load_data_engine,
    validate_portfolio_data as validate_data_engine,
)


ALLOWED_DRIVER_DIMENSIONS = {
    "business_segment",
    "coverage",
    "state",
    "policy_year",
    "underwriter",
}
CANONICAL_METRIC_GROUP_BY = ["valuation_month", "business_segment"]

STATE_DATASETS = "portfolio_agent.datasets"
STATE_VALIDATIONS = "portfolio_agent.validations"
STATE_METRICS = "portfolio_agent.metrics"
STATE_ANOMALIES = "portfolio_agent.anomalies"
STATE_DRIVERS = "portfolio_agent.drivers"
STATE_CURRENT_DATASET = "portfolio_agent.current_dataset_ref"
STATE_CURRENT_METRICS = "portfolio_agent.current_metrics_ref"
STATE_CURRENT_ANOMALIES = "portfolio_agent.current_anomaly_ref"

_RUNTIME_DATASETS: dict[str, Any] = {}
_RUNTIME_METRICS: dict[str, Any] = {}
_RUNTIME_ANOMALIES: dict[str, Any] = {}
_RUNTIME_DRIVERS: dict[str, Any] = {}


def _state(tool_context: Any) -> MutableMapping[str, Any]:
    state = getattr(tool_context, "state", None)
    if state is None:
        if isinstance(tool_context, MutableMapping):
            state = tool_context
        else:
            raise TypeError("ADK tool adapters require a tool_context with mutable state.")
    for key in (STATE_DATASETS, STATE_VALIDATIONS, STATE_METRICS, STATE_ANOMALIES, STATE_DRIVERS):
        state.setdefault(key, {})
    return state


def _model_dump(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [_model_dump(item) for item in value]
    if isinstance(value, dict):
        return {key: _model_dump(item) for key, item in value.items()}
    return value


def _error(message: str, reason_code: str) -> dict:
    return {"status": "error", "reason_code": reason_code, "message": message}


def load_portfolio_data(file_path: str, tool_context: ToolContext) -> dict:
    """Load an approved synthetic portfolio CSV and return an opaque dataset reference."""

    state = _state(tool_context)
    cfg = load_config()
    df = load_data_engine(file_path, workspace_root=str(cfg.project_root))
    dataset_ref = f"dataset:{uuid4().hex}"
    _RUNTIME_DATASETS[dataset_ref] = df
    state[STATE_DATASETS][dataset_ref] = {
        "row_count": int(len(df)),
        "columns": [str(column) for column in df.columns],
    }
    state[STATE_CURRENT_DATASET] = dataset_ref
    return {
        "status": "success",
        "dataset_ref": dataset_ref,
        "row_count": int(len(df)),
        "columns": [str(column) for column in df.columns],
    }


def validate_portfolio_data(dataset_ref: str, tool_context: ToolContext) -> dict:
    """Validate a loaded dataset before any portfolio calculations are performed."""

    state = _state(tool_context)
    df = _RUNTIME_DATASETS.get(dataset_ref)
    if df is None:
        return _error(f"Unknown dataset_ref: {dataset_ref}", "unknown_dataset_ref")

    clean_df, errors, warnings = validate_data_engine(df)
    validation_status = "fail" if errors else "pass_with_warnings" if warnings else "pass"
    _RUNTIME_DATASETS[dataset_ref] = clean_df
    state[STATE_VALIDATIONS][dataset_ref] = {
        "status": validation_status,
        "blocking_errors": errors,
        "warnings": warnings,
        "row_count": int(len(df)),
        "valid_row_count": 0 if errors else int(len(clean_df)),
    }
    return {
        "status": "success",
        "dataset_ref": dataset_ref,
        "validation_status": validation_status,
        "blocking_errors": errors,
        "warnings": warnings,
        "row_count": int(len(df)),
        "valid_row_count": 0 if errors else int(len(clean_df)),
    }


def calculate_portfolio_metrics(dataset_ref: str, group_by: list[str], tool_context: ToolContext) -> dict:
    """Calculate deterministic portfolio metrics for a validated dataset."""

    state = _state(tool_context)
    df = _RUNTIME_DATASETS.get(dataset_ref)
    if df is None:
        return _error(f"Unknown dataset_ref: {dataset_ref}", "unknown_dataset_ref")

    validation = state[STATE_VALIDATIONS].get(dataset_ref)
    if validation is None:
        return _error("Dataset must be validated before calculating metrics.", "validation_required")
    if validation["status"] == "fail":
        return _error("Dataset validation failed; metrics were not calculated.", "validation_failed")

    if group_by != CANONICAL_METRIC_GROUP_BY:
        return _error(
            "Metrics must use canonical grouping: ['valuation_month', 'business_segment'].",
            "unsupported_metric_group_by",
        )

    missing_dimensions = [dimension for dimension in group_by if dimension not in df.columns]
    if missing_dimensions:
        return _error(
            f"Unknown group_by dimension(s): {missing_dimensions}",
            "unknown_group_by_dimension",
        )

    metrics = calculate_metrics_engine(df, group_by=group_by)
    metrics_ref = f"metrics:{uuid4().hex}"
    _RUNTIME_METRICS[metrics_ref] = metrics
    state[STATE_METRICS][metrics_ref] = {
        "dataset_ref": dataset_ref,
        "record_count": len(metrics),
        "group_by": group_by,
    }
    state[STATE_CURRENT_METRICS] = metrics_ref
    return {
        "status": "success",
        "dataset_ref": dataset_ref,
        "metrics_ref": metrics_ref,
        "metrics_records": _model_dump(metrics),
        "calculation_warnings": [],
    }


def detect_anomalies(metrics_ref: str, latest_month: str, tool_context: ToolContext) -> dict:
    """Detect threshold anomalies from deterministic metrics for the latest month."""

    state = _state(tool_context)
    metrics = _RUNTIME_METRICS.get(metrics_ref)
    if metrics is None:
        return _error(f"Unknown metrics_ref: {metrics_ref}", "unknown_metrics_ref")

    anomalies = detect_anomalies_engine(metrics, latest_month)
    anomaly_ref = f"anomalies:{uuid4().hex}"
    anomaly_map = {anomaly.anomaly_id: anomaly for anomaly in anomalies}
    _RUNTIME_ANOMALIES[anomaly_ref] = {
        "metrics_ref": metrics_ref,
        "anomalies": anomalies,
        "anomaly_map": anomaly_map,
    }
    state[STATE_ANOMALIES][anomaly_ref] = {
        "metrics_ref": metrics_ref,
        "anomaly_ids": list(anomaly_map),
        "count": len(anomalies),
    }
    state[STATE_CURRENT_ANOMALIES] = anomaly_ref
    return {
        "status": "success",
        "metrics_ref": metrics_ref,
        "anomaly_ref": anomaly_ref,
        "anomalies": _model_dump(anomalies),
        "summary_counts": {
            "total": len(anomalies),
            "high": sum(1 for anomaly in anomalies if anomaly.severity == "high"),
            "moderate": sum(1 for anomaly in anomalies if anomaly.severity == "moderate"),
        },
    }


def investigate_anomaly_drivers(
    dataset_ref: str,
    anomaly_ref: str,
    anomaly_id: str,
    dimensions: list[str],
    top_n: int,
    tool_context: ToolContext,
) -> dict:
    """Investigate allowed driver dimensions for an anomaly returned by anomaly detection."""

    state = _state(tool_context)
    df = _RUNTIME_DATASETS.get(dataset_ref)
    if df is None:
        return _error(f"Unknown dataset_ref: {dataset_ref}", "unknown_dataset_ref")

    anomaly_bundle = _RUNTIME_ANOMALIES.get(anomaly_ref)
    if anomaly_bundle is None:
        return _error(f"Unknown anomaly_ref: {anomaly_ref}", "unknown_anomaly_ref")

    anomaly = anomaly_bundle["anomaly_map"].get(anomaly_id)
    if anomaly is None:
        return _error(f"Unknown anomaly_id: {anomaly_id}", "unknown_anomaly_id")

    unauthorized = [dimension for dimension in dimensions if dimension not in ALLOWED_DRIVER_DIMENSIONS]
    if unauthorized:
        return _error(
            f"Unauthorized driver dimension(s): {unauthorized}",
            "unauthorized_driver_dimension",
        )

    unavailable = [dimension for dimension in dimensions if dimension not in df.columns]
    if unavailable:
        return _error(
            f"Driver dimension(s) unavailable in dataset: {unavailable}",
            "unavailable_driver_dimension",
        )

    if top_n < 1:
        return _error("top_n must be at least 1.", "invalid_top_n")

    driver_results = investigate_drivers_engine(df, anomaly, dimensions=dimensions)
    trimmed_results = []
    for result in driver_results:
        result_copy = result.model_copy(update={"top_contributors": result.top_contributors[:top_n]})
        trimmed_results.append(result_copy)

    driver_ref = f"drivers:{uuid4().hex}"
    _RUNTIME_DRIVERS[driver_ref] = trimmed_results
    state[STATE_DRIVERS][driver_ref] = {
        "anomaly_id": anomaly_id,
        "dimensions": dimensions,
        "result_count": len(trimmed_results),
    }
    return {
        "status": "success",
        "dataset_ref": dataset_ref,
        "anomaly_ref": anomaly_ref,
        "anomaly_id": anomaly_id,
        "driver_ref": driver_ref,
        "driver_results": _model_dump(trimmed_results),
        "caveats": [],
    }
