---
name: agent-eval-case-builder
description: Use when creating evaluation cases, datasets, rubrics, golden prompts, red-team prompts, regression tests, LLM-as-judge criteria, or pass/fail checks for an agent workflow, skill, tool-using behavior, safety boundary, or production agent quality loop.
---

# Agent Eval Case Builder

Use this skill to turn desired behavior and known failures into reusable eval cases.

## Workflow

1. Define the behavior under test and the boundary of the agent's authority.
2. Collect source examples: specs, user corrections, incidents, edge cases, support tickets, traces, or known risks.
3. Create a balanced eval set:
   - happy path,
   - edge case,
   - ambiguous request,
   - negative/non-trigger,
   - adversarial or unsafe request,
   - regression from a real failure.
4. Write expected behavior and pass/fail rubric.
5. Include trajectory checks for tool-using or action-allowed agents.
6. Store failures as future regression cases.

## References

- Read `references/eval-case-template.md` for dataset shape and rubric patterns.

## Evaluation Prompts

- Positive: "Make eval cases for this agent before we deploy it." Expected: dataset with rubrics.
- Positive edge: "Turn these user corrections into regression evals." Expected: failure-mined cases.
- Negative: "Run the unit tests." Expected: no eval-case design unless creating evals.
