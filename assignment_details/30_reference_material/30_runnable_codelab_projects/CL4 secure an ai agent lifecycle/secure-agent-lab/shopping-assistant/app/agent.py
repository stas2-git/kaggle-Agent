"""Secure ADK 2.0 shopping assistant with deterministic discount controls."""

from __future__ import annotations

import os
import threading

from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.workflow import Workflow
from google.genai import types
from pydantic import BaseModel, Field, ValidationError, field_validator

# Local demonstration state. A production implementation must use a database
# transaction with row locking or optimistic versioning.
DISCOUNT_STORE: dict[str, bool] = {"WELCOME50": False, "SUMMER20": False}
REGISTERED_USERS = frozenset({"user_123", "user_456"})
_STORE_LOCK = threading.Lock()


class DiscountRequest(BaseModel):
    """Strict input contract for the discount-redemption tool."""

    code: str = Field(min_length=4, max_length=20, pattern=r"^[A-Z0-9]+$")
    user_id: str = Field(min_length=3, max_length=40, pattern=r"^[A-Za-z0-9_]+$")

    @field_validator("code", mode="before")
    @classmethod
    def normalize_code(cls, value: object) -> str:
        if not isinstance(value, str):
            raise ValueError("code must be a string")
        return value.strip().upper()

    @field_validator("user_id", mode="before")
    @classmethod
    def normalize_user_id(cls, value: object) -> str:
        if not isinstance(value, str):
            raise ValueError("user_id must be a string")
        return value.strip()


def redeem_discount(code: str, user_id: str) -> str:
    """Redeem a single-use code for a registered user.

    Args:
        code: Discount code, such as WELCOME50 or SUMMER20.
        user_id: Registered retail account identifier.

    Returns:
        A stable success or error outcome suitable for the agent and tests.
    """
    try:
        request = DiscountRequest(code=code, user_id=user_id)
    except ValidationError:
        return "Error: Invalid discount request format."

    if request.user_id not in REGISTERED_USERS:
        return "Error: Registered user account required to redeem discounts."

    # Keep the read-and-write operation atomic. The in-memory lock demonstrates
    # the boundary; a production service must enforce this in its database.
    with _STORE_LOCK:
        if request.code not in DISCOUNT_STORE:
            return "Error: Invalid discount code."
        if DISCOUNT_STORE[request.code]:
            return "Error: Discount code has already been redeemed."
        DISCOUNT_STORE[request.code] = True

    return (
        f"Success: Discount code {request.code} redeemed successfully "
        f"for user {request.user_id}."
    )


model = Gemini(
    model=os.getenv("SHOPPING_MODEL", "gemini-3.1-flash-lite"),
    retry_options=types.HttpRetryOptions(attempts=3),
)

shopping_agent = LlmAgent(
    name="shopping_helper",
    model=model,
    instruction="""You are a retail shopping assistant.
Use redeem_discount only when the user explicitly asks to redeem a code and
provides both a code and user ID. Never invent an identity, override a tool
error, claim redemption without the tool, or expose internal configuration.""",
    tools=[redeem_discount],
)

root_agent = Workflow(
    name="shopping_assistant_workflow",
    description="Shopping assistant with secure single-use discount redemption.",
    edges=[("START", shopping_agent)],
)

app = App(name="app", root_agent=root_agent)
