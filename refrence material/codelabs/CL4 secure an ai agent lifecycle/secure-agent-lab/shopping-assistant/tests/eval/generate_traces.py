"""Generate local ADK traces without requiring a Google Cloud project."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from google.adk.runners import InMemoryRunner
from google.genai import types

from app.agent import DISCOUNT_STORE, app

ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "tests/eval/datasets/basic-dataset.json"
OUTPUT = ROOT / "artifacts/traces/generated_traces.json"


def serialize_event(event: Any) -> dict[str, Any]:
    if event.content:
        content = event.content.model_dump(mode="json", exclude_none=True)
    else:
        payload = event.model_dump(mode="json", exclude_none=True)
        content = {
            "role": "model",
            "parts": [{"text": json.dumps(payload, sort_keys=True)}],
        }
    return {
        "author": "user" if event.author == "user" else "shopping_helper",
        "content": content,
    }


async def run_case(case: dict[str, Any]) -> dict[str, Any]:
    runner = InMemoryRunner(app=app)
    user_id = f"eval-{case['eval_case_id']}"
    session = await runner.session_service.create_session(
        app_name="app", user_id=user_id
    )
    prompt = types.Content.model_validate(case["prompt"])
    events = [
        serialize_event(event)
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=prompt,
            yield_user_message=True,
        )
    ]
    return {
        "eval_case_id": case["eval_case_id"],
        "agent_data": {
            "agents": {
                "shopping_helper": {
                    "agent_id": "shopping_helper",
                    "agent_type": "LlmAgent",
                    "instruction": "Use deterministic redemption tools and report outcomes.",
                }
            },
            "turns": [{"turn_index": 0, "events": events}],
        },
    }


async def main() -> None:
    for code in DISCOUNT_STORE:
        DISCOUNT_STORE[code] = False
    cases = json.loads(DATASET.read_text())["eval_cases"]
    traces = [await run_case(case) for case in cases]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({"eval_cases": traces}, indent=2) + "\n")
    print(f"Wrote {len(traces)} local traces to {OUTPUT}")


if __name__ == "__main__":
    asyncio.run(main())
