"""FastAPI dashboard for Agent Runtime human-in-the-loop approvals."""

from __future__ import annotations

import asyncio
import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = ROOT / "static/index.html"


@dataclass(frozen=True)
class Settings:
    mode: str = os.getenv("DASHBOARD_MODE", "mock").lower()
    project: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-west1")
    agent_runtime_id: str = os.getenv("AGENT_RUNTIME_ID", "")
    user_id: str = "default-user"


class ActionRequest(BaseModel):
    approved: bool
    interrupt_id: str


def _dump(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", exclude_none=True)
    raise TypeError(f"Unsupported session value: {type(value)!r}")


def _field(data: dict[str, Any], snake: str, camel: str) -> Any:
    return data.get(snake, data.get(camel))


def extract_pending(session_value: Any) -> list[dict[str, Any]]:
    """Return RequestInput calls that have no matching function response."""
    session = _dump(session_value)
    calls: dict[str, dict[str, Any]] = {}
    responses: set[str] = set()

    for raw_event in session.get("events", []):
        event = _dump(raw_event)
        content = event.get("content") or {}
        for raw_part in content.get("parts") or []:
            part = _dump(raw_part)
            call = _field(part, "function_call", "functionCall")
            if call and call.get("name") == "adk_request_input":
                args = call.get("args") or {}
                payload = args.get("payload") or {}
                if isinstance(payload, str):
                    try:
                        payload = json.loads(payload)
                    except json.JSONDecodeError:
                        payload = {"raw": payload}
                interrupt_id = (
                    call.get("id")
                    or args.get("interrupt_id")
                    or args.get("interruptId")
                )
                if interrupt_id:
                    calls[interrupt_id] = {
                        "session_id": session.get("id", ""),
                        "interrupt_id": interrupt_id,
                        "message": args.get("message", "Manager review required"),
                        "expense": payload.get("expense", payload),
                        "risk_review": payload.get("risk_review"),
                    }

            response = _field(part, "function_response", "functionResponse")
            if response and response.get("name") == "adk_request_input":
                response_id = response.get("id")
                if response_id:
                    responses.add(response_id)

    return [
        item for interrupt_id, item in calls.items() if interrupt_id not in responses
    ]


class SessionGateway(ABC):
    @abstractmethod
    async def pending(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def act(
        self, session_id: str, interrupt_id: str, approved: bool
    ) -> dict[str, Any]: ...


class MockSessionGateway(SessionGateway):
    """In-memory local gateway with production-shaped data."""

    def __init__(self) -> None:
        self.items = {
            "session-alice": {
                "session_id": "session-alice",
                "interrupt_id": "expense-alice",
                "message": "Expense requires manager approval.",
                "expense": {
                    "amount": 250,
                    "submitter": "alice@company.com",
                    "category": "travel",
                    "description": "NYC flight tickets",
                    "date": "2026-04-12",
                },
                "risk_review": {
                    "risk_level": "medium",
                    "risk_factors": ["High-value travel", "Documentation required"],
                    "recommendation": "Approve after confirming itinerary",
                },
            },
            "session-security": {
                "session_id": "session-security",
                "interrupt_id": "expense-security",
                "message": "Security event requires manager review.",
                "expense": {
                    "amount": 1_000_000,
                    "submitter": "attacker@company.com",
                    "category": "luxury",
                    "description": "[Security-filtered instruction] Luxury car",
                    "date": "2026-04-12",
                },
                "risk_review": {
                    "risk_level": "critical",
                    "risk_factors": ["Prompt-injection pattern", "Extreme amount"],
                    "recommendation": "Reject and investigate",
                },
            },
        }

    async def pending(self) -> list[dict[str, Any]]:
        return list(self.items.values())

    async def act(
        self, session_id: str, interrupt_id: str, approved: bool
    ) -> dict[str, Any]:
        item = self.items.get(session_id)
        if not item or item["interrupt_id"] != interrupt_id:
            raise KeyError("Pending approval not found")
        self.items.pop(session_id)
        decision = "approved" if approved else "rejected"
        return {
            "status": decision,
            "session_id": session_id,
            "summary": (
                f"Expense for {item['expense']['submitter']} was {decision} "
                "by the manager. The workflow resumed successfully."
            ),
        }


class VertexSessionGateway(SessionGateway):
    """Lazy cloud adapter for Agent Platform sessions and Agent Runtime."""

    def __init__(self, settings: Settings) -> None:
        if not settings.project or not settings.agent_runtime_id:
            raise ValueError(
                "GOOGLE_CLOUD_PROJECT and AGENT_RUNTIME_ID are required in vertex mode"
            )
        self.settings = settings
        self.engine_id = settings.agent_runtime_id.rsplit("/", 1)[-1]

    def _session_service(self):  # type: ignore[no-untyped-def]
        from google.adk.sessions import VertexAiSessionService

        return VertexAiSessionService(
            project=self.settings.project,
            location=self.settings.location,
            agent_engine_id=self.engine_id,
        )

    async def pending(self) -> list[dict[str, Any]]:
        service = self._session_service()
        response = await service.list_sessions(
            app_name=self.engine_id, user_id=self.settings.user_id
        )
        full_sessions = await asyncio.gather(
            *(
                service.get_session(
                    app_name=self.engine_id,
                    user_id=self.settings.user_id,
                    session_id=session.id,
                )
                for session in response.sessions
            )
        )
        pending: list[dict[str, Any]] = []
        for session in full_sessions:
            if session is not None:
                pending.extend(extract_pending(session))
        return pending

    def _resource_name(self) -> str:
        if self.settings.agent_runtime_id.startswith("projects/"):
            return self.settings.agent_runtime_id
        return (
            f"projects/{self.settings.project}/locations/{self.settings.location}/"
            f"reasoningEngines/{self.engine_id}"
        )

    async def act(
        self, session_id: str, interrupt_id: str, approved: bool
    ) -> dict[str, Any]:
        import vertexai

        client = vertexai.Client(
            project=self.settings.project, location=self.settings.location
        )
        remote_agent = client.agent_engines.get(name=self._resource_name())
        decision = "approve" if approved else "reject"
        message = {
            "role": "user",
            "parts": [
                {
                    "function_response": {
                        "id": interrupt_id,
                        "name": "adk_request_input",
                        "response": {
                            "approved": approved,
                            "decision": decision,
                        },
                    }
                }
            ],
        }
        events = []
        async for event in remote_agent.async_stream_query(
            message=message,
            user_id=self.settings.user_id,
            session_id=session_id,
        ):
            events.append(event)

        summary = "Workflow resumed."
        for event in reversed(events):
            content = event.get("content") or {}
            for part in reversed(content.get("parts") or []):
                if part.get("text"):
                    summary = part["text"]
                    break
        return {"status": decision, "session_id": session_id, "summary": summary}


def build_gateway(settings: Settings | None = None) -> SessionGateway:
    settings = settings or Settings()
    if settings.mode == "mock":
        return MockSessionGateway()
    if settings.mode == "vertex":
        return VertexSessionGateway(settings)
    raise ValueError("DASHBOARD_MODE must be 'mock' or 'vertex'")


def create_app(gateway: SessionGateway | None = None) -> FastAPI:
    service = gateway or build_gateway()
    application = FastAPI(title="Expense Manager Dashboard", version="0.1.0")

    @application.get("/", response_class=HTMLResponse)
    async def dashboard() -> HTMLResponse:
        return HTMLResponse(INDEX_HTML.read_text())

    @application.get("/healthz")
    async def health() -> dict[str, str]:
        return {"status": "ok", "mode": Settings().mode}

    @application.get("/api/pending")
    async def pending() -> list[dict[str, Any]]:
        try:
            return await service.pending()
        except Exception as exc:
            raise HTTPException(
                status_code=502, detail="Session service unavailable"
            ) from exc

    @application.post("/api/action/{session_id}")
    async def action(session_id: str, body: ActionRequest) -> dict[str, Any]:
        try:
            return await service.act(session_id, body.interrupt_id, body.approved)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=502, detail="Agent Runtime resume failed"
            ) from exc

    return application


app = create_app()
