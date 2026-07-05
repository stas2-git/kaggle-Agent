"""Trace writer per spec_files/30_quality/05_observability_trace_spec.md."""

from __future__ import annotations

import json
import os
from typing import Any

from .security import validate_trace_path


def write_trace(
    run_id: str,
    session_id: str,
    app_name: str,
    root_agent: str,
    started_at: str,
    completed_at: str,
    user_prompt: str,
    input_dataset: str,
    config: dict[str, Any],
    events: list[dict[str, Any]],
    data_quality: dict[str, Any],
    anomalies: list[dict[str, Any]],
    driver_results: list[dict[str, Any]],
    security_flags: list[dict[str, Any]],
    human_review: dict[str, Any],
    final_report_path: str | None,
    final_status: str,
    workspace_root: str,
    trace_path: str,
) -> str:
    validate_trace_path(trace_path, workspace_root)
    trace = {
        "run_id": run_id,
        "session_id": session_id,
        "app_name": app_name,
        "root_agent": root_agent,
        "started_at": started_at,
        "completed_at": completed_at,
        "user_prompt": user_prompt,
        "input_dataset": input_dataset,
        "config": config,
        "events": events,
        "data_quality": data_quality,
        "anomalies": anomalies,
        "driver_results": driver_results,
        "security_flags": security_flags,
        "human_review": human_review,
        "final_report_path": final_report_path,
        "final_status": final_status,
    }
    abs_path = trace_path if os.path.isabs(trace_path) else os.path.join(workspace_root, trace_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w") as f:
        json.dump(trace, f, indent=2, default=str)
    return abs_path
