"""Run codelab scenarios through the local ADK workflow and save judgeable traces."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from google.adk.runners import InMemoryRunner
from google.genai import types

from expense_agent.agent import app

ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "tests/eval/datasets/basic-dataset.json"
OUTPUT = ROOT / "artifacts/traces/generated_traces.json"


def _trace_event(event: Any) -> dict[str, Any]:
    """Keep the complete ADK event inside a canonical text-bearing trace event."""
    payload = event.model_dump(mode="json", exclude_none=True)
    return {
        "author": event.author or "expense_processor",
        "content": {
            "role": "model" if event.author != "user" else "user",
            "parts": [{"text": json.dumps(payload, sort_keys=True)}],
        },
    }


async def run_case(case: dict[str, Any]) -> dict[str, Any]:
    runner = InMemoryRunner(app=app)
    user_id = f"eval-{case['eval_case_id']}"
    session = await runner.session_service.create_session(
        app_name="expense_agent", user_id=user_id
    )
    prompt_text = json.dumps(case["expense"], sort_keys=True)
    prompt = types.Content(role="user", parts=[types.Part.from_text(text=prompt_text)])
    events: list[dict[str, Any]] = []
    interrupted = False
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=prompt,
        yield_user_message=True,
    ):
        events.append(_trace_event(event))
        if "expense_approval" in (event.long_running_tool_ids or []):
            interrupted = True

    decision = case.get("human_decision")
    if interrupted:
        if decision not in {"approve", "reject"}:
            raise ValueError(f"{case['eval_case_id']} requires a human_decision")
        response_part = types.Part(
            function_response=types.FunctionResponse(
                id="expense_approval",
                name="adk_request_input",
                response={"decision": decision},
            )
        )
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=types.Content(role="user", parts=[response_part]),
            yield_user_message=True,
        ):
            events.append(_trace_event(event))

    return {
        "eval_case_id": case["eval_case_id"],
        "prompt": {"role": "user", "parts": [{"text": prompt_text}]},
        "agent_data": {
            "agents": {
                "expense_processor": {
                    "agent_id": "expense_processor",
                    "agent_type": "Workflow",
                    "instruction": "Deterministic expense routing with security screening and HITL.",
                }
            },
            "turns": [{"turn_index": 0, "events": events}],
        },
    }


async def main() -> None:
    source = json.loads(DATASET.read_text())
    traces = [await run_case(case) for case in source["eval_cases"]]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({"eval_cases": traces}, indent=2) + "\n")
    print(f"Wrote {len(traces)} traces to {OUTPUT}")


if __name__ == "__main__":
    asyncio.run(main())
