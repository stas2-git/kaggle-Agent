"""ADK-boundary callback policies for the portfolio monitoring agent."""

from __future__ import annotations

import json
import math
from collections.abc import MutableMapping
from typing import Any
from uuid import uuid4

from portfolio_agent import adk_tools
from portfolio_agent.config import APPLICATION_NAME, DEFAULT_MODEL_NAME
from portfolio_agent.security import SecurityError, scan_text_for_injection, validate_file_path


TOOL_ALLOWLIST = {
    "load_portfolio_data",
    "validate_portfolio_data",
    "calculate_portfolio_metrics",
    "detect_anomalies",
    "investigate_anomaly_drivers",
}

REQUIRED_STATE_KEYS = {
    "review_request": None,
    "dataset_ref": None,
    "data_quality": None,
    "metrics": None,
    "anomalies": None,
    "driver_results": {},
    "security_flags": [],
    "review_decision": None,
    "report_result": None,
}

POLICY_EVENTS = "portfolio_agent.policy_events"


def _state(context: Any) -> MutableMapping[str, Any]:
    state = getattr(context, "state", None)
    if state is None:
        if isinstance(context, MutableMapping):
            state = context
        else:
            state = {}
            setattr(context, "state", state)
    return state


def _tool_name(tool: Any) -> str:
    return getattr(tool, "name", None) or getattr(tool, "__name__", None) or str(tool)


def _record(
    state: MutableMapping[str, Any],
    *,
    hook: str,
    decision: str,
    policy: str,
    reason_code: str,
    description: str,
) -> dict:
    event = {
        "hook": hook,
        "decision": decision,
        "policy": policy,
        "reason_code": reason_code,
        "description": description,
    }
    state.setdefault(POLICY_EVENTS, []).append(event)
    if decision == "block":
        state.setdefault("security_flags", []).append(
            {
                "flag_type": policy,
                "severity": "high",
                "source": hook,
                "description": description,
                "action_taken": "blocked",
            }
        )
    return event


def _blocked(reason_code: str, message: str) -> dict:
    return {"status": "blocked", "reason_code": reason_code, "message": message}


def _contains_unsafe_text(value: Any) -> bool:
    if isinstance(value, str):
        lowered = value.lower()
        return scan_text_for_injection(value) or "system prompt" in lowered or "developer message" in lowered
    if isinstance(value, list):
        return any(_contains_unsafe_text(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_unsafe_text(item) for item in value.values())
    return False


def _redact_text(value: Any) -> Any:
    if isinstance(value, str):
        return "[REDACTED_UNTRUSTED_TEXT]" if _contains_unsafe_text(value) else value
    if isinstance(value, list):
        return [_redact_text(item) for item in value]
    if isinstance(value, dict):
        return {key: _redact_text(item) for key, item in value.items()}
    return value


def _contains_corrupt_number(value: Any) -> bool:
    if isinstance(value, float):
        return math.isnan(value) or math.isinf(value)
    if isinstance(value, list):
        return any(_contains_corrupt_number(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_corrupt_number(item) for item in value.values())
    return False


def before_agent_callback(callback_context: Any) -> None:
    """Initialize safe run state before the portfolio agent starts."""

    state = _state(callback_context)
    for key, value in REQUIRED_STATE_KEYS.items():
        if key not in state:
            state[key] = value.copy() if isinstance(value, (dict, list)) else value
    state.setdefault("run_id", uuid4().hex)
    state.setdefault("session_id", uuid4().hex)
    state.setdefault("execution_mode", "online")
    state.setdefault("application", APPLICATION_NAME)
    state.setdefault("model", DEFAULT_MODEL_NAME)
    state.setdefault(POLICY_EVENTS, [])
    _record(
        state,
        hook="before_agent",
        decision="allow",
        policy="state_initialization",
        reason_code="state_ready",
        description="Initialized portfolio review callback state.",
    )


def before_model_callback(callback_context: Any, llm_request: Any) -> dict | None:
    """Block prompt-disclosure or instruction-override attempts before model use."""

    state = _state(callback_context)
    if _contains_unsafe_text(llm_request):
        _record(
            state,
            hook="before_model",
            decision="block",
            policy="model_context_safety",
            reason_code="unsafe_model_context",
            description="Blocked unsafe model context or prompt-disclosure request.",
        )
        return _blocked("unsafe_model_context", "Unsafe model context was blocked.")
    _record(
        state,
        hook="before_model",
        decision="allow",
        policy="model_context_safety",
        reason_code="model_context_allowed",
        description="Model context passed safety screening.",
    )
    return None


def before_tool_callback(tool: Any, args: dict, tool_context: Any) -> dict | None:
    """Enforce tool allowlist, path policy, workflow prerequisites, and dimensions."""

    state = _state(tool_context)
    name = _tool_name(tool)
    if name not in TOOL_ALLOWLIST:
        _record(
            state,
            hook="before_tool",
            decision="block",
            policy="forbidden_tool",
            reason_code="tool_not_allowlisted",
            description=f"Tool '{name}' is not in the portfolio review allowlist.",
        )
        return _blocked("tool_not_allowlisted", f"Tool '{name}' is not allowed.")

    if name == "load_portfolio_data":
        try:
            validate_file_path(str(args.get("file_path", "")))
        except SecurityError as exc:
            _record(
                state,
                hook="before_tool",
                decision="block",
                policy="forbidden_path",
                reason_code="path_not_allowed",
                description=str(exc),
            )
            return _blocked("path_not_allowed", str(exc))

    if name == "calculate_portfolio_metrics" and args.get("dataset_ref") not in state.get(adk_tools.STATE_VALIDATIONS, {}):
        _record(
            state,
            hook="before_tool",
            decision="block",
            policy="prerequisite",
            reason_code="validation_required",
            description="Metrics calculation requires prior validation.",
        )
        return _blocked("validation_required", "Validate the dataset before calculating metrics.")

    if name == "calculate_portfolio_metrics" and args.get("group_by") != adk_tools.CANONICAL_METRIC_GROUP_BY:
        _record(
            state,
            hook="before_tool",
            decision="block",
            policy="schema",
            reason_code="unsupported_metric_group_by",
            description="Metrics must use canonical valuation_month/business_segment grouping.",
        )
        return _blocked(
            "unsupported_metric_group_by",
            "Use group_by ['valuation_month', 'business_segment'] for portfolio metrics.",
        )

    if name == "detect_anomalies" and args.get("metrics_ref") not in state.get(adk_tools.STATE_METRICS, {}):
        _record(
            state,
            hook="before_tool",
            decision="block",
            policy="prerequisite",
            reason_code="metrics_required",
            description="Anomaly detection requires calculated metrics.",
        )
        return _blocked("metrics_required", "Calculate metrics before detecting anomalies.")

    if name == "investigate_anomaly_drivers":
        dimensions = args.get("dimensions", [])
        unauthorized = [
            dimension
            for dimension in dimensions
            if dimension not in adk_tools.ALLOWED_DRIVER_DIMENSIONS
        ]
        if unauthorized:
            _record(
                state,
                hook="before_tool",
                decision="block",
                policy="dimension_policy",
                reason_code="unauthorized_driver_dimension",
                description=f"Unauthorized driver dimension(s): {unauthorized}",
            )
            return _blocked("unauthorized_driver_dimension", "Unauthorized driver dimension requested.")

        anomaly_ref = args.get("anomaly_ref")
        anomaly_id = args.get("anomaly_id")
        anomaly_bundle = state.get(adk_tools.STATE_ANOMALIES, {}).get(anomaly_ref)
        if anomaly_bundle is None or anomaly_id not in anomaly_bundle.get("anomaly_ids", []):
            _record(
                state,
                hook="before_tool",
                decision="block",
                policy="prerequisite",
                reason_code="unknown_anomaly_id",
                description=f"Unknown anomaly_id '{anomaly_id}' for anomaly_ref '{anomaly_ref}'.",
            )
            return _blocked("unknown_anomaly_id", "Driver analysis requires a real anomaly ID.")

    _record(
        state,
        hook="before_tool",
        decision="allow",
        policy="tool_policy",
        reason_code="tool_allowed",
        description=f"Tool '{name}' passed callback policy checks.",
    )
    return None


def after_tool_callback(tool: Any, args: dict, tool_context: Any, tool_response: Any) -> dict | None:
    """Validate, redact, and record tool responses after execution."""

    state = _state(tool_context)
    name = _tool_name(tool)
    try:
        json.dumps(tool_response, allow_nan=False)
    except (TypeError, ValueError):
        _record(
            state,
            hook="after_tool",
            decision="block",
            policy="output_safety",
            reason_code="non_json_tool_response",
            description=f"Tool '{name}' returned a non-JSON-safe response.",
        )
        return _blocked("non_json_tool_response", "Tool response was not JSON-safe.")

    if _contains_corrupt_number(tool_response):
        _record(
            state,
            hook="after_tool",
            decision="block",
            policy="output_safety",
            reason_code="corrupt_numeric_output",
            description=f"Tool '{name}' returned NaN or infinite numeric output.",
        )
        return _blocked("corrupt_numeric_output", "Tool response contained corrupt numeric output.")

    sanitized = _redact_text(tool_response)
    _record(
        state,
        hook="after_tool",
        decision="allow",
        policy="output_safety",
        reason_code="tool_response_valid",
        description=f"Tool '{name}' returned a valid JSON-safe response.",
    )
    return sanitized if sanitized != tool_response else None


def after_model_callback(callback_context: Any, llm_response: Any) -> dict | None:
    """Reject unsafe model outputs before artifact generation."""

    state = _state(callback_context)
    response_text = json.dumps(llm_response, default=str).lower()
    forbidden_phrases = [
        "system prompt",
        "developer message",
        "bind coverage",
        "stop writing",
        "implement this rate change",
        "approved by manager",
    ]
    if any(phrase in response_text for phrase in forbidden_phrases):
        _record(
            state,
            hook="after_model",
            decision="block",
            policy="model_output_safety",
            reason_code="unsafe_model_output",
            description="Blocked unsupported or binding model output.",
        )
        return _blocked("unsafe_model_output", "Unsafe model output was blocked.")

    _record(
        state,
        hook="after_model",
        decision="allow",
        policy="model_output_safety",
        reason_code="model_output_allowed",
        description="Model output passed safety screening.",
    )
    return None
