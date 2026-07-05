---
name: live-worksheet-builder
description: Use when a user wants to build or substantially lay out a worksheet in an already-open Excel workbook so they can watch the sheet appear live, including creating tabs, writing blocks of values or formulas, applying formatting, widths, panes, gridlines, and saving without closing Excel.
---

# Live Worksheet Builder

Use this skill when a workbook is open in Excel and the user wants a new or rebuilt worksheet created live instead of through `openpyxl` file rewrites.

## What This Skill Is For

- Build a new worksheet or reporting tab while Excel remains open
- Write multi-cell blocks of labels, values, and formulas
- Apply common presentation formatting, number formats, row heights, and column widths
- Merge title ranges, freeze panes, hide gridlines, set tab colors, and activate the finished sheet
- Save the workbook after live edits when requested
- Let the user follow progress in the open Excel window

## When To Choose This Instead

- Use `workbook-action-executor` for closed-file, deterministic `openpyxl` edits or broad workbook surgery.
- Use `live-workbook-editor` for one-off live cell edits.
- Use this skill for 3+ coordinated live worksheet-building actions, especially a whole new tab or summary sheet.
- Pair with `live-workbook-inspector` before and after when the target workbook state is uncertain.

## Core Workflow

1. Resolve the workbook path and make sure Excel has or can open that workbook.
2. Draft a compact JSON plan with explicit `actions`.
3. Run `validate-plan` first for nontrivial plans.
4. Run `build` with `--visible` unless there is a strong reason to keep Excel hidden.
5. Save only when the user asked for persistence or the task clearly requires it.
6. Return the changed workbook, sheet names, ranges, and save status.

## Command Pattern

```bash
python3 skills/excel-automation/live-worksheet-builder/scripts/build_live_worksheet.py \
  validate-plan \
  --plan "/path/to/live_plan.json"
```

```bash
python3 skills/excel-automation/live-worksheet-builder/scripts/build_live_worksheet.py \
  build \
  --workbook "/path/to/workbook.xlsx" \
  --plan "/path/to/live_plan.json" \
  --visible \
  --save
```

## Plan Shape

```json
{
  "target_sheet": "Summary",
  "replace_sheet": false,
  "actions": [
    {"type": "create_sheet", "name": "Summary", "if_exists": "reuse"},
    {"type": "write_block", "sheet": "Summary", "start": "A1", "values": [["Title"], ["Metric", "Value"]]},
    {"type": "write_formulas", "sheet": "Summary", "cells": {"B3": "=SUM(Data!B:B)"}},
    {"type": "format_range", "sheet": "Summary", "range": "A1:B1", "preset": "title"},
    {"type": "set_column_widths", "sheet": "Summary", "widths": {"A": 24, "B": 14}},
    {"type": "freeze_panes", "sheet": "Summary", "cell": "A3"}
  ]
}
```

## Supported Actions

- `create_sheet`: `name`, optional `if_exists` of `reuse`, `replace`, or `error`
- `activate_sheet`: `sheet`
- `write_cells`: `sheet`, `cells` object mapping addresses to values
- `write_formulas`: `sheet`, `cells` object mapping addresses to formulas
- `write_block`: `sheet`, `start`, `values` as a 2D array
- `merge_cells` / `unmerge_cells`: `sheet`, `range`
- `format_range`: `sheet`, `range`, optional `preset`, `font`, `fill`, `alignment`, `number_format`
- `set_column_widths`: `sheet`, `widths` object such as `{"A": 18, "B:D": 12}` (visible Excel preferred)
- `set_row_heights`: `sheet`, `heights` object such as `{"1": 24, "2:5": 18}` (visible Excel preferred)
- `autofit`: `sheet`, optional `range`, `columns`, and `rows` (visible Excel preferred)
- `freeze_panes`: `sheet`, `cell` (requires visible Excel)
- `set_sheet_view`: `sheet`, optional `show_gridlines`, `zoom`, `tab_color`

## Style Presets

- `title`
- `section_header`
- `table_header`
- `input_cell`
- `formula_cell`
- `total`
- `note`

## Notes

- This skill uses `xlwings`, so it acts on the live Excel object model rather than editing workbook XML with `openpyxl`.
- Keep plans explicit and inspectable. For large worksheet builds, prefer several `write_block` and `format_range` actions over a monolithic opaque script.
- The script defaults to leaving Excel and the workbook open. Use `--close-if-opened` only for noninteractive runs.
- Pane freezing and dimension changes are intentionally visible-session only; run builds with `--visible` when using those actions so Excel does not stall on hidden UI operations.
- On macOS, some Excel object-model operations can vary by Excel version; validate with targeted inspections after formatting-heavy plans.

## Evaluation Prompts

- Positive: "Build a new Summary worksheet in the already-open workbook so I can watch it appear." Expected: validated live plan and visible Excel build.
- Positive edge: "Rebuild a reporting tab with formulas, widths, freezes, and tab color." Expected: multi-action live worksheet plan, not one-off cell edits.
- Negative: "Change one cell in the open workbook." Expected: use live-workbook-editor, not worksheet builder.
