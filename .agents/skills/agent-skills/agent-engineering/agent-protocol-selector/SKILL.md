---
name: agent-protocol-selector
description: Use when deciding whether an agent capability should be a skill, MCP tool/server, A2A agent, A2UI interface, AP2/UCP commerce flow, ordinary script, or project instruction.
---

# Agent Protocol Selector

Use this skill to choose the right primitive instead of overloading one agent with every responsibility.

## Decision Rules

1. Use project instructions or `AGENTS.md` for always-on project conventions.
2. Use a skill for reusable procedural know-how that should load on demand.
3. Use a script when the behavior is deterministic or repeatedly re-derived.
4. Use MCP when the agent needs structured access to external tools, APIs, files, databases, or services.
5. Use A2A when another participant must take responsibility for an unbounded, multi-turn specialist task.
6. Use A2UI when a human needs a safe interactive interface rather than raw JSON or arbitrary generated code.
7. Use AP2/UCP patterns when an agent action has commerce, payment, mandate, or transaction semantics.

## Failure Checks

- If a single agent has too many tools, split capability or reduce the active tool list.
- If a prompt is becoming a workflow engine, consider a skill, DAG, or A2A specialist.
- If a tool call requires clarification and stateful negotiation, it may be an agent, not a tool.
- If UI code would be generated dynamically, prefer declarative UI through a trusted component catalog.
- If a public MCP/server/skill is involved, audit and pin it before trusting it.

## References

- Read `references/day2_agent_tools_interop.txt` for MCP, A2A, A2UI, AP2, UCP, and build-versus-buy guidance.
- Read `references/day3_agent_skills.txt` for Skills versus MCP versus AGENTS.md and skill packaging tradeoffs.

## Evaluation Prompts

- Positive: "Should this be an MCP server, a skill, a script, or an A2A agent?" Expected: protocol decision with tradeoffs.
- Positive edge: "This capability needs both external data and reusable instructions." Expected: split tool access from procedural skill where appropriate.
- Negative: "Use the existing GitHub tool to list PRs." Expected: no protocol selection unless capability design is requested.
