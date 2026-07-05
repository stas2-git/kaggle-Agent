"""ADK 2.0 graph workflow for secure, ambient expense approval."""

from __future__ import annotations

import base64
import json
import logging
import re
from collections.abc import Generator
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.agents.context import Context
from google.adk.apps import App, ResumabilityConfig
from google.adk.events.event import Event
from google.adk.events.request_input import RequestInput
from google.adk.workflow import Workflow
from google.genai import types
from pydantic import BaseModel, Field

from .config import config

logger = logging.getLogger(__name__)

_SSN_RE = re.compile(r"(?<!\d)(?:\d{3}[- ]?\d{2}[- ]?\d{4}|\d{9,12})(?!\d)")
_CARD_RE = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")
_INJECTION_PATTERNS = (
    re.compile(r"\bignore\b.{0,40}\b(instruction|prompt|rule)s?\b", re.I),
    re.compile(r"\bbypass\b.{0,40}\b(rule|policy|approval|control)s?\b", re.I),
    re.compile(r"\b(auto[- ]?approve|force\s+approval|override\s+approval)\b", re.I),
    re.compile(r"\b(system\s+prompt|developer\s+message|jailbreak)\b", re.I),
)


class ExpenseData(BaseModel):
    """Sanitized expense data passed between workflow nodes."""

    amount: float = Field(ge=0)
    submitter: str
    category: str
    description: str
    date: str
    redacted_categories: list[str] = Field(default_factory=list)
    injection_detected: bool = False


class RiskReview(BaseModel):
    """Structured output produced by the Gemini reviewer."""

    amount: float
    submitter: str
    category: str
    risk_level: str
    risk_factors: list[str]
    recommendation: str


def _content_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, types.Content):
        return "".join(part.text or "" for part in value.parts or [])
    return json.dumps(value)


def _decode_expense(node_input: Any) -> dict[str, Any]:
    """Decode direct JSON, ADK Content, or a normalized Pub/Sub event."""
    if isinstance(node_input, dict):
        event = node_input
    else:
        event = json.loads(_content_text(node_input))

    data: Any = event.get("data", event)
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            data = json.loads(base64.b64decode(data).decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Expense data must be a JSON object")
    return data


def redact_pii(description: str) -> tuple[str, list[str]]:
    """Redact supported PII without ever logging the original description."""
    categories: list[str] = []
    redacted, ssn_count = _SSN_RE.subn("[REDACTED_SSN]", description)
    if ssn_count:
        categories.append("ssn")
    redacted, card_count = _CARD_RE.subn("[REDACTED_CREDIT_CARD]", redacted)
    if card_count:
        categories.append("credit_card")
    return redacted, categories


def security_screen(node_input: Any) -> Event:
    """Parse input, redact PII, and identify prompt injection before persistence."""
    data = _decode_expense(node_input)
    description, categories = redact_pii(str(data.get("description", "")))
    injection_detected = any(p.search(description) for p in _INJECTION_PATTERNS)
    expense = ExpenseData(
        amount=float(data.get("amount", 0)),
        submitter=str(data.get("submitter", "unknown")),
        category=str(data.get("category", "other")),
        description=description,
        date=str(data.get("date", "")),
        redacted_categories=categories,
        injection_detected=injection_detected,
    ).model_dump()
    return Event(output=expense, state={"expense_data": expense})


def route_expense(node_input: dict[str, Any]) -> Event:
    """Apply deterministic safety and dollar-threshold routing."""
    if node_input.get("injection_detected"):
        return Event(output=node_input, route="SECURITY_REVIEW")
    if float(node_input["amount"]) >= config.review_threshold:
        return Event(output=node_input, route="LLM_REVIEW")
    return Event(output=node_input, route="AUTO_APPROVE")


def _visible_result(result: dict[str, Any]) -> Generator[Event, None, None]:
    text = json.dumps(result, sort_keys=True)
    yield Event(
        content=types.Content(role="model", parts=[types.Part.from_text(text=text)])
    )
    yield Event(output=result)


def auto_approve(node_input: dict[str, Any]) -> Generator[Event, None, None]:
    """Approve a safe low-value expense without an LLM call."""
    result = {"status": "approved", "route": "auto_approved", **node_input}
    logger.info(
        "Expense auto-approved amount=%.2f category=%s",
        node_input["amount"],
        node_input["category"],
    )
    yield from _visible_result(result)


review_agent = LlmAgent(
    name="review_agent",
    model=config.model,
    instruction="""You review sanitized corporate expenses of $100 or more.
Assess unusual categories, vague descriptions, round numbers, values over $1,000,
and likely policy violations. Return only the requested structured risk review.
Never make the approval decision: a human always decides high-value expenses.""",
    input_schema=ExpenseData,
    output_schema=RiskReview,
)


def request_approval(
    node_input: dict[str, Any], ctx: Context
) -> Generator[RequestInput, None, None]:
    """Pause the workflow until a human approves or rejects the expense."""
    expense = ctx.state.get("expense_data", {})
    payload = {
        "expense": expense,
        "security_event": bool(expense.get("injection_detected")),
    }
    if not payload["security_event"]:
        payload["risk_review"] = node_input
    yield RequestInput(
        interrupt_id="expense_approval",
        message="Expense requires manager approval. Respond approve or reject.",
        payload=payload,
    )


def process_decision(node_input: Any, ctx: Context) -> Generator[Event, None, None]:
    """Record and display the resumed human decision."""
    if isinstance(node_input, dict):
        decision = str(node_input.get("decision", "reject")).lower()
    else:
        decision = str(node_input).lower()
    approved = decision in {"approve", "approved", "yes"}
    expense = ctx.state.get("expense_data", {})
    result = {
        "status": "approved" if approved else "rejected",
        "route": "human_review",
        "security_event": bool(expense.get("injection_detected")),
        "expense": expense,
    }
    logger.info("Human expense decision=%s", result["status"])
    yield from _visible_result(result)


root_agent = Workflow(
    name="expense_processor",
    description="Secure ambient workflow for corporate expense triage.",
    edges=[
        ("START", security_screen),
        (security_screen, route_expense),
        (
            route_expense,
            {
                "AUTO_APPROVE": auto_approve,
                "LLM_REVIEW": review_agent,
                "SECURITY_REVIEW": request_approval,
            },
        ),
        (review_agent, request_approval),
        (request_approval, process_decision),
    ],
)

app = App(
    name="expense_agent",
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)
