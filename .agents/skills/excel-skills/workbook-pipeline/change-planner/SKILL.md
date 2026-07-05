---
name: workbook-change-planner
description: Use when a user has a workbook goal and the workflow needs a constrained implementation plan that maps the request to likely sheets, VBA modules, validation checks, and risk points before any code is generated.
---

# Workbook Change Planner

Use this skill before generating VBA or workbook edits.

## What this skill is for

- Translate a user goal into a workbook-specific plan
- Identify which sheets and modules are likely to change
- Separate safe layout work from risky business-logic changes
- Define validation checks before code generation begins
- Produce a scoped change plan for autonomous execution

## Core workflow

1. Read the user task plus the workbook semantic brief.
2. Classify the request as layout, diagnostics, automation, refactor, or formula logic work.
3. Identify likely sheets, modules, and named ranges involved.
4. Define validation checkpoints and rollback concerns.
5. Produce a narrow plan for implementation.
6. Append a planning event to the run log.

## Expected output

- A change plan with affected workbook surfaces
- A validation list that later skills can execute

## Command pattern

```bash
python3 skills/workbook-pipeline/change-planner/scripts/plan_changes.py \
  --brief "/path/to/workbook-folder/llm_work/runs/<timestamp>/summaries/workbook-brief.json" \
  --task "Add a cleaner diagnostics tab and improve readability of the model sheet"
```

## Notes

- Planning should happen before VBA generation.
- Mark high-risk formula or business-logic edits clearly.
- Prefer the smallest plan that can accomplish the user goal.
- Default interactive workbook improvement flows to editing the original workbook after backup. Treat working-copy runs as an explicit caution mode, not the everyday default.
- If `--output` is omitted and the brief already lives under `llm_work/`, write to the matching run folder and mirror the latest plan into `llm_work/current/plans/`.
- Prefer saving plans inside `llm_work/plans/` beside the workbook so they are easy to inspect before any edits run.
- Generate a fresh plan for every new user request, even if the workbook summary is reused.
- Save each plan under the active run folder and optionally copy the latest version into `llm_work/current/`.
- Also write the step outcome into `llm_work/runs/<timestamp>/run_log.json`.

## Evaluation Prompts

- Positive: "Plan the workbook changes before generating code." Expected: scoped plan with affected sheets/modules, risks, and validation checks.
- Positive edge: "Improve formulas but avoid breaking business logic." Expected: high-risk formula areas called out before edits.
- Negative: "Apply this already-approved action plan." Expected: use executor/editor, not planner.
