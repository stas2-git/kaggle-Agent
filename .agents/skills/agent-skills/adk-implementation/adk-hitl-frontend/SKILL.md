---
name: adk-hitl-frontend
description: Use when designing or building a human-in-the-loop frontend for an ADK/Agent Runtime app, including pending approval queues, event correlation, session resume, function responses, manager dashboards, auth, audit, and Cloud Run/Pub/Sub wiring.
---

# ADK HITL Frontend

Use this skill when an agent pauses for human review and a user interface must list, inspect, decide, and resume the exact agent session.

## Workflow

1. Define the interrupt payload, reviewer role, decision schema, and final resume behavior.
2. Read `references/cl5_agent_frontend_spec.md` for event resolution, adapters, endpoints, UI behavior, and production gaps.
3. Read `references/cl5_vibecode_deploy_frontend.txt` only for exact lab steps or command details.
4. Correlate pending function calls and responses by stable IDs.
5. Persist approval records before resuming the agent.
6. Resume the exact session with the matching function response.
7. Add authentication, authorization, idempotency, optimistic concurrency, and audit logs before production use.

## Required Views And Endpoints

- Pending decision list
- Decision detail with risk context
- Approve/reject or structured decision action
- Final result/status view
- Duplicate/stale decision handling
- Error state for missing session, failed resume, or unauthorized reviewer

## Evaluation Prompts

- Positive: "Design the manager approval UI for this ADK agent." Expected: pending queue, detail view, correlated response, audit, auth, and resume behavior.
- Positive edge: "Approvals sometimes duplicate or arrive late." Expected: idempotency, stale decision handling, and stable IDs.
- Negative: "Make a static marketing page." Expected: no HITL frontend skill unless agent approvals/session resume are involved.
