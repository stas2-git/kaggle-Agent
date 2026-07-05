---
name: context-budget-planner
description: Use when a task has too much source material, long documents, many references, noisy context, overlapping instructions, or repeated context rot; plans what belongs in static instructions, skills, references, scripts, retrieval, summaries, or not in context.
---

# Context Budget Planner

Use this skill to reduce context load while preserving the behavior the agent needs.

## Workflow

1. List the materials and their purpose.
2. Classify each item:
   - always-on rule,
   - on-demand procedure,
   - detailed reference,
   - deterministic repeated step,
   - source archive,
   - irrelevant/noisy.
3. Move material to the right layer.
4. Create summaries only as routers or intermediate maps.
5. Keep operating references short, concrete, and task-specific.
6. Add eval prompts to prove the agent loads the right material.

## References

- Read `references/context-layering.md` for the placement matrix and compression rules.

## Evaluation Prompts

- Positive: "This folder has huge docs; decide what should become skills versus references." Expected: context layer plan.
- Positive edge: "The agent keeps loading all references and getting worse." Expected: reduce static context and add routing.
- Negative: "Summarize this one short article." Expected: ordinary summary unless context architecture is the task.
