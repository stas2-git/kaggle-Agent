---
name: agent-incident-retrospective
description: Use after an agent mistake, unsafe action, bad answer, tool misuse, missed instruction, loop, user correction, production incident, or near miss to identify root cause, failed boundary, missing eval, missing guardrail, and the regression case that should prevent recurrence.
---

# Agent Incident Retrospective

Use this skill to turn agent failures into improved future behavior.

## Workflow

1. State the incident in one sentence.
2. Reconstruct expected behavior versus actual behavior.
3. Identify failure type:
   - intent misunderstanding,
   - context drift,
   - wrong/missing tool,
   - weak skill trigger,
   - missing verification,
   - unsafe authority,
   - prompt injection,
   - insufficient eval,
   - bad recovery.
4. Find the repair surface: instruction, skill, reference, script, tool schema, guardrail, approval gate, or eval.
5. Add a regression prompt/test that would have caught it.
6. Propose a small fix; avoid broad "be careful" rules.

## References

- Read `references/retrospective-template.md` for root-cause and action-item templates.

## Evaluation Prompts

- Positive: "The agent sent the wrong file; make a retro and prevention plan." Expected: root cause, boundary, regression eval.
- Positive edge: "Nothing bad happened, but the trace looked risky." Expected: near-miss retrospective.
- Negative: "Apologize for a typo." Expected: no incident retro unless future prevention is requested.
