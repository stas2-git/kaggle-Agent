---
name: excel-skills-router
description: Use when deciding which bundled Excel, workbook, spreadsheet, live Excel automation, VBA, screen interaction, backup, planning, summarization, or validation skill to use.
---

# Excel Skills Router

Use this high-level skill to choose the smallest useful downstream Excel skill. Do not use this router as the operational workflow after a focused skill matches; load the selected focused skill's `SKILL.md` before acting.

## How To Route

1. Identify whether the user needs file-based spreadsheet authoring, existing-workbook edits, live Excel automation, VBA/macro work, workbook understanding, or screen validation.
2. Pick the smallest matching focused skill.
3. Name the focused skill and, when working inside this repo, its repo path.
4. If this package is installed as one grouped folder, focused skills live under this router folder, such as `excel-decompose/SKILL.md`.
5. If the skills are installed flat under `~/.codex/skills/`, focused skills usually live by skill name, such as `excel-decompose`.
6. Load the focused skill's `SKILL.md` before acting.

## Routing

### Spreadsheet Artifacts

- Use `spreadsheets` when creating or editing a new `.xlsx`, `.xls`, `.csv`, `.tsv`, or Google Sheets-targeted spreadsheet artifact with formulas, formatting, charts, tables, recalculation, or visual verification.
- Do not use `spreadsheets` for an already-open Excel workbook, VBA work, managed workbook backups, or deterministic action-plan edits when the Excel-specific skills fit.

### Workbook Understanding

- Use `excel-decompose` when turning an existing `.xlsx` or `.xlsm` workbook into an LLM-readable dump of sheets, formulas, values, named ranges, and VBA modules when available.
- Use `workbook-semantic-summarizer` when a decomposition is too large and the agent needs a compact workbook brief covering purpose, key sheets, inputs, outputs, VBA entry points, and likely change surfaces.

### File-Based Workbook Editing

- Use `workbook-action-executor` when building, editing, reorganizing, formatting, or cleaning up an Excel workbook through deterministic workbook actions instead of ad hoc `openpyxl` code.
- Use `workbook-backup-versioning` before autonomous workbook changes when timestamped backups, working copies, or rollback mapping are needed.
- Use `workbook-change-planner` before code or workbook mutation when the request needs affected sheets/modules, risk points, and validation checks planned first.
- Use `validation-checklist-builder` when a workbook change needs task-specific post-change checks for sheets, ranges, formulas, labels, charts, or OCR-visible UI text.

### Live Excel Automation

- Use `excel-session-manager` to attach to Excel, open or activate a workbook, switch sheets, save, or coordinate focus without editing workbook content.
- Use `live-workbook-inspector` to inspect values, formulas, formatting, tables, named ranges, or active workbook state in an already-open Excel session.
- Use `live-workbook-editor` for small live edits in an already-open workbook, such as changing cell values, formulas, formatting, sheet labels, freeze panes, or simple structure.
- Use `live-worksheet-builder` when building or substantially laying out a worksheet in an already-open workbook so the user can watch it appear live.

### VBA And Macros

- Use `vba-module-sync` to inspect, export, or screen-automate VBA module injection through the VBE path.
- Use `workbook-macro-runner` to open or attach to a workbook, run a named macro, capture success or failure, and report execution results.

### Screen Interaction Primitives

- Use `window-control` to activate apps/windows, inspect frontmost app state, move windows, or save/restore window state.
- Use `region-capture` to capture a full screen, window, or exact region without OCR.
- Use `region-ocr` to OCR an image, screen, or exact region without clicking.
- Use `text-target-actions` to locate visible text and optionally click the best target.
- Use `wait-and-assert` to poll visible screen text until it appears or disappears, or fail cleanly after timeout.

## Combination Patterns

- Existing workbook improvement: `excel-decompose` -> `workbook-semantic-summarizer` if needed -> `workbook-change-planner` -> `workbook-backup-versioning` -> `workbook-action-executor` -> `validation-checklist-builder`.
- Small live Excel fix: `excel-session-manager` -> `live-workbook-inspector` if context is unclear -> `live-workbook-editor`.
- Live tab build: `excel-session-manager` -> `live-worksheet-builder` -> screen validation with `region-capture`, `region-ocr`, or `wait-and-assert` when visual state matters.
- VBA update loop: `vba-module-sync` -> `workbook-macro-runner` -> `validation-checklist-builder` or live inspection.
- Dialog or VDI workflow: `window-control` -> `region-ocr` or `wait-and-assert` -> `text-target-actions` only when a click is actually needed.

## Rules

- Prefer the most specific skill that matches the current task.
- Use workbook backups before autonomous file mutation unless the task is clearly read-only or artifact-only.
- Use live Excel skills when the user cares about the currently open workbook or wants to watch changes happen.
- Use file-based workbook skills when repeatability, audit artifacts, backups, or plan validation matter more than live visual editing.
- Load only the focused skill and any references it explicitly routes to.

## Evaluation Prompts

- Positive: "Which Excel skill should I use to clean up this existing workbook and save it safely?" Expected: route to `excel-decompose` if context is unclear, then `workbook-backup-versioning` and `workbook-action-executor`.
- Positive: "The workbook is open in Excel; change this one formula while I watch." Expected: route to live Excel session/editor skills, not artifact creation.
- Positive: "Extract the VBA modules and then run RefreshModel." Expected: route to `vba-module-sync`, then `workbook-macro-runner`.
- Positive: "Create a brand-new polished spreadsheet with formulas and charts." Expected: route to `spreadsheets`.
- Positive edge: "Wait for the calculation complete dialog, then click OK." Expected: route to `wait-and-assert`, then `text-target-actions`.
- Negative: "Write a SQL query for incurred claims." Expected: no Excel skill unless a spreadsheet/workbook deliverable is requested.
- Negative: "Review this Python API design." Expected: no Excel skill.
