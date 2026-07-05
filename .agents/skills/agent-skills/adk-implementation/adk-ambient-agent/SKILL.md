---
name: adk-ambient-agent
description: Use when building or adapting an ADK ambient/event-driven agent with scheduled work, Pub/Sub or event ingestion, normalized inputs, deterministic routing, LLM judgment, human review, state, traces, and evaluations.
---

# ADK Ambient Agent

Use this skill for ambient agents that react to events or scheduled triggers instead of only direct chat input.

## Workflow

1. Define the event source, trigger cadence, input schema, output schema, and authority boundary.
2. Read `references/cl4_ambient_agent_spec.md` for architecture, data contracts, routing, state, HITL lifecycle, observability, and implementation sequence.
3. Read `references/cl4_ambient_agent.txt` only when exact codelab instructions or command details are needed.
4. Normalize every transport into one domain input object before any policy or model call.
5. Put deterministic policy before LLM judgment where possible.
6. Add human review at irreversible or high-authority decisions.
7. Add traceable outputs, evaluation cases, and replay-friendly test fixtures.

## Required Design Elements

- Transport normalization
- Sanitization of untrusted event content
- Deterministic route names
- Structured model outputs
- Persistent or resumable session state when using HITL
- Audit events for decision points
- Tests for automatic, review, rejection, and injection cases

## Evaluation Prompts

- Positive: "Build an ADK agent that reacts to Pub/Sub events and pauses for human review." Expected: ambient/event-driven design with normalized input, policy, HITL, traces, and evals.
- Positive edge: "Adapt this chat-only ADK agent to run on a schedule." Expected: trigger/cadence, transport normalization, replay, state, and authority boundaries.
- Negative: "Write a regular FastAPI endpoint." Expected: no ambient-agent skill unless ADK event/scheduled behavior is involved.
