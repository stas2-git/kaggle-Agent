---
name: least-privilege-tool-planner
description: Use before giving an agent tools, MCP servers, file access, credentials, browser/session access, shell commands, write permissions, deployment authority, or any external action capability; plans scopes, read/write limits, approval gates, logging, and rollback.
---

# Least Privilege Tool Planner

Use this skill to design the minimum authority needed for an agent task.

## Workflow

1. Name the task and required outcome.
2. List required resources: files, APIs, accounts, databases, services, browser sessions, shell commands.
3. Choose the least authority level:
   - no tool
   - read-only
   - draft-only
   - write with confirmation
   - autonomous write
4. Add human approval for irreversible, external, expensive, sensitive, or ambiguous actions.
5. Define logging and rollback before write authority.
6. Remove unused tools or credentials from the active context.

## Permission Questions

- Can the task be completed with read-only access?
- Can the agent draft a change instead of applying it?
- What action would be harmful if the agent misunderstood intent?
- What should be impossible even if prompt injection appears?
- What audit record proves the action was authorized?

## References

- Read `references/permission-matrix.md` for authority tiers and approval rules.

## Evaluation Prompts

- Positive: "Plan what tools this agent should have to manage Gmail drafts." Expected: draft-only/send approval boundary.
- Positive edge: "Give an agent deployment access for production." Expected: staged scopes, approvals, logs, rollback.
- Negative: "Use the existing read-only file search to find TODOs." Expected: no planner unless authority is being designed.
