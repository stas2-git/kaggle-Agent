---
name: validation-checklist-builder
description: Use when a workbook task needs task-specific post-change checks, such as expected sheet names, labels, formulas, tabs, charts, or OCR-visible text that downstream automation can verify.
---

# Validation Checklist Builder

Use this skill after planning and before validation execution.

## What this skill is for

- Turn a workbook task into explicit validation checks
- Define visible UI checks for screen OCR workflows
- Define workbook structure checks for post-run verification
- Separate must-pass checks from informative checks
- Produce a checklist that later validation steps can execute mechanically

## Core workflow

1. Read the user goal and the change plan.
2. Extract the user-visible and workbook-visible outcomes that should exist after the change.
3. Write checks for sheet names, labels, formulas, named ranges, charts, or VBA outputs.
4. Mark which checks are suitable for OCR, workbook automation, or both.
5. Save a structured checklist for downstream validation.
6. Append a checklist event to the run log.

## Expected output

- A task-specific validation checklist in JSON, YAML, or Markdown

## Command pattern

```bash
python3 skills/workbook-pipeline/validation-checklist-builder/scripts/build_checklist.py \
  --plan "/path/to/workbook-folder/llm_work/runs/<timestamp>/plans/change-plan.json"
```

## Notes

- Keep checks specific enough that automation can evaluate them.
- Prefer small must-pass checks over broad subjective review items.
- Route visible-text checks toward the existing screen-interaction skills.
- In normal interactive runs, assume the validation target is the original workbook after backup unless the run explicitly uses `working_copy`.
- If `--output` is omitted and the plan already lives under `llm_work/`, write to the matching run folder and mirror the latest checklist into `llm_work/current/checklists/`.
- Prefer saving checklists inside `llm_work/checklists/` beside the workbook so the checks and results stay with the workbook artifacts.
- Generate a fresh checklist for every new plan. Do not assume an older checklist still matches the latest requested change.
- Save each checklist under the active run folder and optionally mirror the latest one into `llm_work/current/`.
- Also write the step outcome into `llm_work/runs/<timestamp>/run_log.json`.

## Evaluation Prompts

- Positive: "Build validation checks for this workbook change plan." Expected: must-pass checks for sheets, ranges, formulas, labels, charts, or OCR-visible text.
- Positive edge: "Some checks need OCR and some need workbook inspection." Expected: checklist marks validation mechanism per item.
- Negative: "Run the checks now." Expected: use inspection/OCR/execution tools, not checklist builder alone.
