---
name: human-approval-gate-designer
description: Use when designing human-in-the-loop approval flows for agent actions, including pending approvals, review payloads, allow/deny decisions, escalation rules, audit records, session resume, and what can be auto-approved versus blocked.
---

# Human Approval Gate Designer

Use this skill to make approval meaningful instead of a vague "Are you sure?"

## Workflow

1. Identify actions that need approval: external write, irreversible change, sensitive data, production action, payment, or ambiguous intent.
2. Define what the reviewer must see before deciding.
3. Define allowed decisions: approve, deny, edit, request clarification, escalate.
4. Define what happens after each decision.
5. Add audit fields and replay/session-resume requirements.
6. Set auto-approval only for low-risk, bounded, reversible actions.

## Approval Payload

Include:

- action summary,
- exact target,
- proposed payload or diff,
- reason the agent thinks it is needed,
- risk level,
- data sources used,
- policy checks passed/failed,
- rollback or undo path,
- expiration/time limit.

## References

- Read `references/gate-patterns.md` for payload templates, risk tiers, and anti-patterns.

## Evaluation Prompts

- Positive: "Design an approval flow before this agent sends customer emails." Expected: payload, decisions, audit, send boundary.
- Positive edge: "Some deploys should auto-approve." Expected: tiered gates and rollback criteria.
- Negative: "Make a UI button say Approve." Expected: no skill unless approval policy/flow is being designed.
