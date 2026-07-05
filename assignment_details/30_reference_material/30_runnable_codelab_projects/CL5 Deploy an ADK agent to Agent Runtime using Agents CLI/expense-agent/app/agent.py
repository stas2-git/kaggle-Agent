"""ADK 2.0 expense workflow shared by local and Agent Runtime entry points."""

from __future__ import annotations

import base64
import json
import logging
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


class ExpenseData(BaseModel):
    """Validated expense input passed through the workflow."""

    amount: float = Field(ge=0)
    submitter: str = Field(min_length=1, max_length=254)
    category: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=1, max_length=1000)
    date: str = Field(min_length=1, max_length=32)


class RiskReview(BaseModel):
    """Structured Gemini review for a high-value expense."""

    risk_level: str
    risk_factors: list[str]
    recommendation: str


def _content_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, types.Content):
        return "".join(part.text or "" for part in value.parts or [])
    return json.dumps(value)


def parse_expense(node_input: Any) -> dict[str, Any]:
    """Normalize direct JSON, ADK Content, or a data-wrapped event."""
    if isinstance(node_input, dict):
        envelope = node_input
    else:
        envelope = json.loads(_content_text(node_input))

    data: Any = envelope.get("data", envelope)
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            data = json.loads(base64.b64decode(data).decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Expense data must be a JSON object")
    return ExpenseData.model_validate(data).model_dump()


def route_by_amount(node_input: dict[str, Any]) -> Event:
    """Apply the deterministic $100 review threshold and save workflow state."""
    route = (
        "NEEDS_REVIEW"
        if float(node_input["amount"]) >= config.review_threshold
        else "AUTO_APPROVE"
    )
    return Event(output=node_input, route=route, state={"expense_data": node_input})


def _visible_result(result: dict[str, Any]) -> Generator[Event, None, None]:
    text = json.dumps(result, sort_keys=True)
    yield Event(
        content=types.Content(role="model", parts=[types.Part.from_text(text=text)])
    )
    yield Event(output=result)


def auto_approve(node_input: dict[str, Any]) -> Generator[Event, None, None]:
    """Approve an expense under $100 without invoking Gemini."""
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
    instruction="""Review this validated expense of $100 or more.
Assess vague descriptions, unusual categories, round numbers, values over $1,000,
and likely policy violations. Return the requested structured risk analysis.
Never approve the expense: a human must make every high-value decision.""",
    input_schema=ExpenseData,
    output_schema=RiskReview,
)


def request_approval(
    node_input: dict[str, Any], ctx: Context
) -> Generator[RequestInput, None, None]:
    """Pause the Agent Runtime invocation for a manager decision."""
    yield RequestInput(
        interrupt_id="expense_approval",
        message="Expense requires manager approval. Respond approve or reject.",
        payload={
            "expense": ctx.state.get("expense_data", {}),
            "risk_review": node_input,
        },
    )


def process_decision(node_input: Any, ctx: Context) -> Generator[Event, None, None]:
    """Apply the resumed human decision and complete the workflow."""
    if isinstance(node_input, dict):
        decision = str(node_input.get("decision", "reject")).lower()
    else:
        decision = str(node_input).lower()
    approved = decision in {"approve", "approved", "yes"}
    result = {
        "status": "approved" if approved else "rejected",
        "route": "human_review",
        "expense": ctx.state.get("expense_data", {}),
    }
    logger.info("Human expense decision=%s", result["status"])
    yield from _visible_result(result)


root_agent = Workflow(
    name="expense_processor",
    description="Expense triage workflow prepared for Agent Runtime.",
    edges=[
        ("START", parse_expense),
        (parse_expense, route_by_amount),
        (
            route_by_amount,
            {
                "AUTO_APPROVE": auto_approve,
                "NEEDS_REVIEW": review_agent,
            },
        ),
        (review_agent, request_approval),
        (request_approval, process_decision),
    ],
)

app = App(
    name="app",
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)
