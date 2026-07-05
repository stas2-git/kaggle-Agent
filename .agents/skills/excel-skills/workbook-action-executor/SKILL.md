---
name: workbook-action-executor
description: Use when a user wants to build, edit, reorganize, or clean up an Excel workbook through deterministic workbook actions instead of writing a one-off openpyxl script. Best for creating sheets, writing values or formulas, copying ranges, formatting ranges, sizing rows or columns, freezing panes, and other repeatable workbook edits.
---

# Workbook Action Executor

Use this skill when the task is to make workbook edits through a stable action layer rather than inventing custom workbook-manipulation code.

## What This Skill Is For

- Create, rename, reorder, or delete sheets
- Check workbook status before editing
- Write cell values or formulas
- Fill formulas across a target range with adjusted references
- Copy ranges within a workbook
- Validate multi-step action plans before mutation
- Create workbook tables
- Define workbook-level names
- Insert or delete rows and columns
- Set column widths and row heights
- Apply common formatting such as fills, bold text, alignment, and number formats
- Apply consolidated styles through one style action
- Apply styles to multiple disjoint ranges in one action
- Use reusable style presets and theme tokens
- Control sheet presentation such as gridlines, tab color, zoom, and print settings
- Run a higher-level `cleanup-sheet` command for cosmetic cleanup and presentation polish
- Freeze panes
- Merge or unmerge cells
- Save workbook-local audit output into `llm_work/runs/<timestamp>/artifacts/`
- Manage workbook backups through the shared backup system when saving edits

## Trigger Guidance

Use this skill when the user asks to:

- build a workbook or sheet from scratch
- add a summary tab or reporting block
- clean up or reorganize a workbook tab
- standardize workbook formatting
- add sections, labels, formulas, or summary blocks
- apply repeatable formatting or polish across several workbook areas
- make workbook edits that are broader than a tiny live Excel change

Prefer this skill over ad hoc `openpyxl` scripts when the requested edits fit the supported actions.

## Runtime Notes

- This skill is designed to run with `python3`; it does not require a skill-local `.venv`.
- The script depends on `openpyxl` being available in the Codex Python environment.
- Keep the installed `.codex/skills` copy aligned with the repo version when the skill changes, especially the shared support folder and workbook-pipeline helper folders.
- Command examples assume the skill has been installed under `~/.codex/skills/`. When working from this repo, prefix paths with `excel/`.

## Core Workflow

1. Resolve the workbook path and decide whether the edit target is the original workbook or a backup/working copy.
2. Check workbook-local context in `llm_work/current/state.json` and `context.md` when that history would help.
3. Choose the narrowest subcommand that matches the requested edit.
4. Run the action executor script with explicit arguments.
5. Save the workbook using managed backup behavior unless there is a strong reason to skip it.
6. Write an action result artifact under `llm_work/runs/<timestamp>/artifacts/` and append a compact run-log event.
7. If the edit is substantial, follow with diff or checklist-based validation.

## Command Pattern

```bash
python3 skills/workbook-action-executor/scripts/workbook_action_executor.py \
  --workbook "/path/to/workbook.xlsx" \
  create-sheet \
  --sheet "Summary"
```

```bash
python3 skills/workbook-action-executor/scripts/workbook_action_executor.py \
  --workbook "/path/to/workbook.xlsx" \
  --save \
  write-cells \
  --sheet "Summary" \
  --set "A1=Tax Summary" \
  --set "B2=209000"
```

```bash
python3 skills/workbook-action-executor/scripts/workbook_action_executor.py \
  --workbook "/path/to/workbook.xlsx" \
  --save \
  set-style \
  --sheet "Summary" \
  --range "A1:D1" \
  --range "F1:H1" \
  --preset "table_header"
```

```bash
python3 skills/workbook-action-executor/scripts/workbook_action_executor.py \
  --workbook "/path/to/workbook.xlsx" \
  --save \
  set-style \
  --sheet "Summary" \
  --range "A1:D3" \
  --preset "section_header" \
  --theme '{"accent_fill":"1F4E78","header_font_color":"FFFFFF"}' \
  --alignment '{"horizontal": "center", "wrap_text": true}'
```

```bash
python3 skills/workbook-action-executor/scripts/workbook_action_executor.py \
  --workbook "/path/to/workbook.xlsx" \
  --save \
  set-sheet-view \
  --sheet "Summary" \
  --no-show-gridlines \
  --tab-color "1F4E78" \
  --zoom 90 \
  --page-orientation landscape
```

```bash
python3 skills/workbook-action-executor/scripts/workbook_action_executor.py \
  --workbook "/path/to/workbook.xlsx" \
  --save \
  cleanup-sheet \
  --sheet "Summary" \
  --title-range "A1:H2" \
  --section-header-range "A4:H4" \
  --table-header-range "A6:H6" \
  --numeric-range "B7:H20" \
  --autofit-columns "A:H" \
  --freeze-cell "A6" \
  --no-show-gridlines \
  --tab-color "1F4E78"
```

```bash
python3 skills/workbook-action-executor/scripts/workbook_action_executor.py \
  --workbook "/path/to/workbook.xlsx" \
  validate-plan \
  --plan "skills/workbook-action-executor/references/action-plan-template.json"
```

```bash
python3 skills/workbook-action-executor/scripts/workbook_action_executor.py \
  --workbook "/path/to/workbook.xlsx" \
  --backup-policy managed \
  --save \
  run-plan \
  --plan "skills/workbook-action-executor/references/action-plan-template.json"
```

## Plan Authoring Notes

- `run-plan` accepts normal nested JSON objects for style fields such as `font`, `fill`, `border`, `alignment`, and `theme`.
- `set-style` and `format-range` can target multiple disjoint ranges through a `ranges` array in plans.
- `style` blocks inside plan steps are supported and are expanded into the expected executor fields.
- Use `validate-plan` before `run-plan` when the job is high-stakes or formatting-heavy.
- See `references/action-plan-template.json` for a small reusable example plan.

## Supported Subcommands

- `check-workbook-status`
- `create-sheet`
- `rename-sheet`
- `reorder-sheet`
- `delete-sheet`
- `write-cells`
- `write-formulas`
- `fill-formula`
- `copy-range`
- `validate-plan`
- `define-name`
- `create-table`
- `insert-rows`
- `delete-rows`
- `insert-cols`
- `delete-cols`
- `set-column-widths`
- `set-row-heights`
- `set-style`
- `format-range`
- `set-sheet-view`
- `cleanup-sheet`
- `freeze-panes`
- `merge-cells`
- `unmerge-cells`
- `run-plan`

## Style Presets

- `section_header`
- `table_header`
- `input_cell`
- `formula_cell`
- `final_total`
- `note_cell`

Use presets when the user intent is presentation-oriented and does not need a fully bespoke style payload.

## Notes

- This skill is deterministic workbook execution, not workbook understanding. Use `excel-decompose` first when workbook context is unclear.
- Keep edits explicit and inspectable; prefer multiple small actions over one opaque mutation.
- The script writes workbook-local action artifacts and appends to `llm_work/runs/<timestamp>/run_log.json`.
- Current state is tracked in `llm_work/current/state.json`, `latest_run.json`, and `context.md` instead of mirrored per-command files.
- Use this skill instead of a one-off `openpyxl` script when the needed edit is already covered by the supported action set.
- When saving workbook edits, prefer the managed backup path instead of creating one-off backup files outside the skill stack.
- Prefer `set-style` when multiple formatting properties should be applied together; it is more compact and closer to how this skill should evolve.
- Prefer `cleanup-sheet` when the user asks for “clean up,” “polish,” or “make this tab easier to scan.”
- Prefer `run-plan` when the requested work is naturally a sequence of 3+ workbook actions; this keeps execution auditable and reduces one-off scripting pressure.
- Prefer `validate-plan` before `run-plan` when a multi-step edit is high-stakes or likely to touch many workbook surfaces.
- Prefer explicit `copy-range` flags when the request only needs formulas, only values, or layout/style replication; this keeps range copies more intentional.

## Evaluation Prompts

- Positive: "Create a summary tab, write formulas, format it, and save the workbook." Expected: use deterministic workbook actions or a validated action plan.
- Positive edge: "Clean up three tabs with repeatable formatting and backup first." Expected: managed backup plus explicit multi-step plan, not ad hoc openpyxl code.
- Negative: "Analyze what this workbook does before editing." Expected: use decomposition/summarizer first, not action execution.
