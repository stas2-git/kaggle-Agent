"""A credential-free ADK runner smoke test for the deterministic branch."""

import json

import pytest
from google.adk.runners import InMemoryRunner
from google.genai import types

from expense_agent.agent import app


@pytest.mark.asyncio
async def test_low_value_expense_completes_without_llm() -> None:
    runner = InMemoryRunner(app=app)
    session = await runner.session_service.create_session(
        app_name="expense_agent", user_id="test-user"
    )
    payload = {
        "amount": 45,
        "submitter": "bob@company.com",
        "category": "meals",
        "description": "Team lunch",
        "date": "2026-04-12",
    }
    message = types.Content(
        role="user", parts=[types.Part.from_text(text=json.dumps(payload))]
    )
    events = [
        event
        async for event in runner.run_async(
            user_id="test-user", session_id=session.id, new_message=message
        )
    ]
    outputs = [event.output for event in events if event.output]
    assert outputs[-1]["status"] == "approved"
    assert outputs[-1]["route"] == "auto_approved"
    assert all("review_agent" not in (event.node_info.path or "") for event in events)
