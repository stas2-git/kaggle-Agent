"""Credential-free ADK runner test for the deterministic graph branch."""

import json

import pytest
from google.adk.runners import InMemoryRunner
from google.genai import types

from app.agent import app


@pytest.mark.asyncio
async def test_low_value_path_bypasses_review_agent() -> None:
    runner = InMemoryRunner(app=app)
    session = await runner.session_service.create_session(
        app_name="app", user_id="test-user"
    )
    message = types.Content(
        role="user",
        parts=[
            types.Part.from_text(
                text=json.dumps(
                    {
                        "data": {
                            "amount": 50,
                            "submitter": "user@example.com",
                            "category": "meals",
                            "description": "Lunch",
                            "date": "2026-06-04",
                        }
                    }
                )
            )
        ],
    )
    events = [
        event
        async for event in runner.run_async(
            user_id="test-user", session_id=session.id, new_message=message
        )
    ]
    outputs = [event.output for event in events if event.output]
    assert outputs[-1]["status"] == "approved"
    assert all("review_agent" not in (event.node_info.path or "") for event in events)
