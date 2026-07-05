---
name: excel-session-manager
description: Use when a workflow needs to attach to a live Excel session, open or activate a workbook, switch sheets, save the workbook, or coordinate focus between Excel, the VDI, and later live-editing steps.
---

# Excel Session Manager

Use this skill at the start of live Excel automation and whenever the workflow needs to stabilize which workbook and sheet are active.

## What this skill is for

- Attach to a running Excel application
- Open or activate a target workbook
- Bring a workbook or sheet to the foreground
- Save the active workbook or a named workbook
- Coordinate with screen automation when Excel focus is unreliable
- Record which workbook session later skills should inspect or edit

## Core workflow

1. Resolve the target workbook path or workbook title.
2. Attach to the live Excel app or bring Excel to the foreground.
3. Open the workbook if it is not already open.
4. Activate the workbook, worksheet, or range the next step needs.
5. Save or confirm session state before handing off to inspector or editor skills.
6. Append a session event to the active run log when this becomes part of the workbook workflow.

## Expected output

- A structured session result including workbook title, sheet title, and whether Excel is frontmost
- Optional save/open status for later logging

## Command pattern

```bash
python3 skills/excel-automation/excel-session-manager/scripts/manage_session.py \
  --workbook "/path/to/workbook.xlsx" \
  --sheet "Summary" \
  --action activate
```

## Notes

- Prefer object-model automation first, then fall back to screen automation when the VDI or Excel focus is unreliable.
- This skill should not make business edits itself; it should prepare the live Excel context for other skills.
- In interactive runs, favor keeping the user on the same workbook they already have open.

## Evaluation Prompts

- Positive: "Open this workbook in Excel and activate the Summary sheet." Expected: session activation result, no workbook content edits.
- Positive edge: "Excel is already open on the wrong workbook; switch to this target and report state." Expected: attach/open/activate with structured session result.
- Negative: "Write values into A1:B2." Expected: route to live workbook editor or worksheet builder, not session manager alone.
