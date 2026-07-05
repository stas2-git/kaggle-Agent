"""Outcome-based security and business-rule tests."""

import pytest

from app.agent import DISCOUNT_STORE, redeem_discount


@pytest.fixture(autouse=True)
def reset_store() -> None:
    for code in DISCOUNT_STORE:
        DISCOUNT_STORE[code] = False
    yield
    for code in DISCOUNT_STORE:
        DISCOUNT_STORE[code] = False


def test_discount_code_can_only_be_redeemed_once() -> None:
    first = redeem_discount("WELCOME50", "user_123")
    second = redeem_discount("WELCOME50", "user_456")

    assert first.startswith("Success:")
    assert DISCOUNT_STORE["WELCOME50"] is True
    assert second == "Error: Discount code has already been redeemed."


def test_discount_redemption_rejects_invalid_code() -> None:
    result = redeem_discount("INVALID999", "user_123")

    assert result == "Error: Invalid discount code."


@pytest.mark.parametrize("user_id", ["guest_999", "", "unknown_user"])
def test_discount_redemption_rejects_unregistered_accounts(user_id: str) -> None:
    result = redeem_discount("SUMMER20", user_id)

    assert result in {
        "Error: Registered user account required to redeem discounts.",
        "Error: Invalid discount request format.",
    }
    assert DISCOUNT_STORE["SUMMER20"] is False


@pytest.mark.parametrize(
    "code,user_id",
    [
        ("WELCOME50; DROP TABLE discounts", "user_123"),
        ("WELCOME50", "user_123<script>"),
        ("", "user_123"),
    ],
)
def test_discount_redemption_rejects_malformed_input(code: str, user_id: str) -> None:
    result = redeem_discount(code, user_id)

    assert result == "Error: Invalid discount request format."
    assert not any(DISCOUNT_STORE.values())


def test_discount_code_is_normalized() -> None:
    result = redeem_discount(" welcome50 ", "user_123")

    assert result.startswith("Success:")
    assert DISCOUNT_STORE["WELCOME50"] is True
