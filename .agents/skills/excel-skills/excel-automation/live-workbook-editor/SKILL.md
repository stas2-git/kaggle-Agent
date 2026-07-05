---
name: live-workbook-editor
description: Use when a workbook is already open in Excel and the workflow needs to make live edits through the Excel session, such as writing cell values, formulas, formatting, sheet labels, freeze panes, or simple structural changes, without closing the workbook.
---

# Live Workbook Editor

Use this skill when the user wants workbook improvements while Excel stays open.

## What this skill is for

- Write cell values or formulas into a live workbook
- Apply formatting such as column widths, number formats, fills, fonts, alignment, or freeze panes
- Add or rename sheets in the live Excel session
- Save the workbook after live edits
- Keep the user working in the same workbook they already have open

## Core workflow

1. Attach to the target Excel workbook and sheet.
2. Inspect the local area first when the edit is not trivial.
3. Apply a narrow set of live workbook changes through Excel automation.
4. Save the workbook or leave save behavior explicit based on the run settings.
5. Return a concise change summary and append the edit event to the active run log.

## Expected output

- A structured result describing which workbook, sheet, and ranges were changed
- Optional save status and any validation follow-up notes

## Command pattern

```bash
python3 skills/excel-automation/live-workbook-editor/scripts/edit_live_workbook.py \
  --workbook "/path/to/workbook.xlsx" \
  --sheet "2025 tax" \
  --set-value "A1=Tax Estimate Summary" \
  --freeze-panes "A2" \
  --save
```

## Notes

- Use this skill instead of `openpyxl` when the workbook is already open and the live Excel session should remain active.
- Keep edits narrow and inspectable; avoid large opaque mutations without first gathering local context.
- Prefer object-model automation first and screen automation as a fallback when the VDI blocks direct control.
- This skill should pair naturally with `excel-session-manager` and `live-workbook-inspector`.

## Evaluation Prompts

- Positive: "In the open workbook, change A1 and freeze panes without closing Excel." Expected: live Excel object-model edit.
- Positive edge: "Make a small live formatting fix while the user watches." Expected: narrow live edit with save status explicit.
- Negative: "Build an entire workbook from scratch." Expected: use workbook-action-executor or spreadsheets, not live editor.
