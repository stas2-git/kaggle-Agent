---
name: live-workbook-inspector
description: Use when a workbook is already open in Excel and the workflow needs to inspect the live session state, such as active sheets, ranges, formulas, values, formatting, tables, or named ranges, without rewriting the file on disk.
---

# Live Workbook Inspector

Use this skill before making live workbook edits and after them when validation depends on the live Excel session rather than the closed workbook file.

## What this skill is for

- Read values, formulas, and formatting from an open workbook
- Inspect the active sheet, named sheet, or selected range
- Report sheet order, used ranges, named ranges, or table presence
- Help the LLM reason about what is visible in the live workbook session
- Confirm that later edits landed where expected

## Core workflow

1. Attach to the active Excel session or target workbook.
2. Identify the workbook, sheet, and range to inspect.
3. Read the live worksheet state through Excel automation.
4. Return a compact structured result that later planning or editing can consume.
5. Append an inspection event to the active run log when this becomes part of the workbook workflow.

## Expected output

- A structured JSON-like result with workbook name, sheet, range, values, formulas, and selected formatting details
- A compact markdown or plain-text inspection summary when useful for the user

## Command pattern

```bash
python3 skills/excel-automation/live-workbook-inspector/scripts/inspect_live_workbook.py \
  --workbook "/path/to/workbook.xlsx" \
  --sheet "2025 tax" \
  --range "A1:F20"
```

## Notes

- Prefer returning small targeted inspections rather than dumping whole-sheet contents.
- This skill complements decomposition and `openpyxl`; it is most useful when the workbook is already open and the live session matters.
- Use this skill before and after `live-workbook-editor` for safer iterative edits.

## Evaluation Prompts

- Positive: "Inspect the formulas and values in the active workbook range A1:F20." Expected: compact live-session inspection.
- Positive edge: "Before editing, tell me what sheet is active and whether this named range exists." Expected: live workbook state, not file rewrite.
- Negative: "Create a backup copy of this workbook." Expected: use backup-versioning, not live inspection.
