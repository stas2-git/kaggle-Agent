---
name: workbook-macro-runner
description: Use when a workflow needs to open or attach to an Excel workbook, run a named macro, capture success or failure, and return structured execution results for autonomous workbook iteration.
---

# Workbook Macro Runner

Use this skill after VBA sync or workbook preparation.

## What this skill is for

- Open or reuse a target workbook
- Run a named macro
- Wait for completion
- Capture runtime errors and execution status
- Return a structured result for downstream validation

## Core workflow

1. Open or attach to the target workbook.
2. Confirm the macro target.
3. Run the macro.
4. Capture success, failure, and any visible error message.
5. Return a structured execution result.

## Command pattern

```bash
python3 skills/excel-automation/macro-runner/scripts/run_macro.py \
  --workbook "/path/to/model.xlsm" \
  --macro "Step6PricingTab.Step6PricingTab"
```

## Notes

- Prefer explicit workbook and macro names.
- If Excel prompts for file or automation access, capture that state for downstream reporting.
- Keep this skill focused on execution, not screen validation.

## Evaluation Prompts

- Positive: "Run the RefreshModel macro and capture whether it succeeded." Expected: macro execution result with errors captured.
- Positive edge: "After syncing VBA, run this macro and report any Excel prompt." Expected: attach/open, run, capture prompt or failure.
- Negative: "Inspect VBA modules without running anything." Expected: use vba-module-sync, not macro runner.
