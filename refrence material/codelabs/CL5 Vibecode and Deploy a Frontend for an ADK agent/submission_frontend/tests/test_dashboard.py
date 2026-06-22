"""Dashboard API and session-resolution tests."""

from fastapi.testclient import TestClient

from dashboard.main import MockSessionGateway, create_app, extract_pending


def request_event(interrupt_id: str) -> dict:
    return {
        "content": {
            "parts": [
                {
                    "functionCall": {
                        "id": interrupt_id,
                        "name": "adk_request_input",
                        "args": {
                            "message": "Review expense",
                            "payload": {"expense": {"amount": 250}},
                        },
                    }
                }
            ]
        }
    }


def response_event(interrupt_id: str) -> dict:
    return {
        "content": {
            "parts": [
                {
                    "functionResponse": {
                        "id": interrupt_id,
                        "name": "adk_request_input",
                        "response": {"approved": True},
                    }
                }
            ]
        }
    }


def test_extracts_only_unresolved_interrupts() -> None:
    session = {
        "id": "session-1",
        "events": [
            request_event("resolved"),
            response_event("resolved"),
            request_event("pending"),
        ],
    }
    result = extract_pending(session)
    assert [item["interrupt_id"] for item in result] == ["pending"]
    assert result[0]["expense"]["amount"] == 250


def test_dashboard_and_pending_api() -> None:
    client = TestClient(create_app(MockSessionGateway()))
    assert client.get("/").status_code == 200
    pending = client.get("/api/pending")
    assert pending.status_code == 200
    assert len(pending.json()) == 2


def test_approval_removes_pending_item() -> None:
    client = TestClient(create_app(MockSessionGateway()))
    response = client.post(
        "/api/action/session-alice",
        json={"approved": True, "interrupt_id": "expense-alice"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "approved"
    assert len(client.get("/api/pending").json()) == 1


def test_unknown_action_returns_404() -> None:
    client = TestClient(create_app(MockSessionGateway()))
    response = client.post(
        "/api/action/missing",
        json={"approved": False, "interrupt_id": "missing"},
    )
    assert response.status_code == 404
