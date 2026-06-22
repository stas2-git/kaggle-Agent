"""Deterministic policy and parsing tests."""

import base64
import json

from app.agent import parse_expense, route_by_amount


def expense(amount: float) -> dict[str, object]:
    return {
        "amount": amount,
        "submitter": "user@example.com",
        "category": "meals",
        "description": "Client meal",
        "date": "2026-06-04",
    }


def test_expense_under_threshold_auto_approves() -> None:
    event = route_by_amount(expense(99.99))
    assert event.actions.route == "AUTO_APPROVE"


def test_expense_at_threshold_requires_review() -> None:
    event = route_by_amount(expense(100))
    assert event.actions.route == "NEEDS_REVIEW"


def test_parses_plain_data_envelope() -> None:
    assert parse_expense({"data": expense(50)})["amount"] == 50


def test_parses_base64_data_envelope() -> None:
    encoded = base64.b64encode(json.dumps(expense(50)).encode()).decode()
    assert parse_expense({"data": encoded})["amount"] == 50
