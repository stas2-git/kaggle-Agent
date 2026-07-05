---
name: adk-secure-lifecycle
description: Use when securing an ADK or tool-using agent with validation, authorization, guardrails, command hooks, secret scanning, STRIDE threat modeling, human gates, tests, and behavioral evaluation.
---

# ADK Secure Lifecycle

Use this skill when agent behavior touches real authority, sensitive data, user identity, payments, account changes, code execution, or deployment.

## Workflow

1. Identify assets, actors, trust boundaries, and irreversible actions.
2. Read `references/cl4_secure_agent_lifecycle_spec.md` for the control layers and implementation checklist.
3. Read `references/day4_security_evaluation.txt` for broader security/evaluation principles.
4. Read `references/cl4_secure_ai_agent_lifecycle.txt` only for exact lab steps or implementation examples.
5. Enforce deterministic validation and authorization outside the model.
6. Add human gates for ambiguous, high-impact, or irreversible operations.
7. Create outcome-based tests and adversarial evaluation cases.

## Security Checklist

- Strict schemas at every tool boundary
- Trusted identity from server/session context, not natural language
- Authorization per operation and resource
- Prompt-injection and secret handling controls
- Command/tool call approval hooks where code or shell execution is involved
- STRIDE review for new capabilities
- Audit logs for approvals, denials, and state changes

## Evaluation Prompts

- Positive: "Secure this ADK tool-using agent before deployment." Expected: trust boundaries, validation, authorization, prompt-injection controls, tests, and human gates.
- Positive edge: "The agent can run shell commands and access user data." Expected: least privilege, hooks, audit, secret handling, and adversarial evals.
- Negative: "Explain STRIDE at a high level." Expected: explanation only, not a full secure lifecycle plan.
