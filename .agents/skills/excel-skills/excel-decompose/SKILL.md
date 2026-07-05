---
name: excel-decompose
description: Use when a user wants to turn an Excel workbook such as .xlsx or .xlsm into an LLM-readable text dump that summarizes workbook structure, sheet names, formulas, values, and named ranges. Best for auditing workbook logic, preparing workbook context for model analysis, or comparing workbook versions.
---

# Excel Decompose

Use this skill when the task is to convert an Excel workbook into a text artifact that an LLM can read more easily than the raw file.

## What this skill is for

- Decompose `.xlsx` and `.xlsm` files into a structured text summary
- Reconstruct a workbook `.xlsx` from a decomposition text file
- Reconstruct a workbook inside an `.xlsm` macro shell so custom VBA functions can still work
- Preserve workbook-level context such as sheet order and defined names
- Preserve cell-level formulas and visible values for non-empty cells
- Preserve lightweight readability metadata such as column widths, merged cells, freeze panes, hidden rows/columns, and tab colors
- Extract VBA modules from `.xlsm` workbooks into the text artifact
- Write a single primary run artifact into `llm_work/runs/<timestamp>/artifacts/decomposition.txt`
- Optionally write a separate custom export only when `--output` is explicitly provided
- Update `llm_work/current/state.json`, `latest_run.json`, and `context.md`
- Append compact decomposition events to `llm_work/runs/<timestamp>/run_log.json`
- Optionally trigger workbook-pipeline helpers from the same run folder with explicit `--include` options

## Core workflow

1. Choose the workbook path to decompose.
2. Before rerunning work, check workbook-local audit context such as `llm_work/current/state.json`, `latest_run.json`, and `context.md` to see whether fresh artifacts already exist for the workbook and task.
3. Reuse current artifacts when they still match the workbook state and request; rerun the needed steps when the workbook changed, the request changed, or the prior artifact is missing.
4. Run the decomposition script in `scripts/`.
5. Save the primary output into `llm_work/runs/<timestamp>/artifacts/decomposition.txt`.
6. Only write a separate export when an explicit `--output` path is actually useful.
7. Update `llm_work/current/` state files and append a compact `run_log.json` event.
8. Optionally trigger downstream helpers such as semantic summary, change plan, checklist, or backup from the same run context.
9. Read the generated text file rather than the workbook binary when giving the LLM workbook context.
10. If needed, run the reconstruction script to build an `.xlsx` back from the text artifact.
11. If VBA/UDFs need to keep working, run the macro-preserving reconstruction mode with an `.xlsm` shell.
12. If the workbook changes, rerun the script to refresh the text artifact.

## Command pattern

```bash
skills/excel-decompose/.venv/bin/python skills/excel-decompose/scripts/decompose_excel.py \
  --workbook "ActuarialPricingModel.xlsm"
```

```bash
skills/excel-decompose/.venv/bin/python skills/excel-decompose/scripts/decompose_excel.py \
  --workbook "/path/to/workbook.xlsx" \
  --output "skills/excel-decompose/output/workbook.txt" \
  --llm-work-root "/path/to/llm_work"
```

```bash
skills/excel-decompose/.venv/bin/python skills/excel-decompose/scripts/decompose_excel.py \
  --workbook "/path/to/workbook.xlsx" \
  --include summary
```

```bash
skills/excel-decompose/.venv/bin/python skills/excel-decompose/scripts/decompose_excel.py \
  --workbook "/path/to/workbook.xlsx" \
  --include backup,summary,plan,checklist \
  --task "Improve readability of the tax summary tab"
```

```bash
skills/excel-decompose/.venv/bin/python skills/excel-decompose/scripts/reconstruct_excel.py \
  --input "skills/excel-decompose/output/ActuarialPricingModel.txt" \
  --output "skills/excel-decompose/output/ActuarialPricingModel_rebuilt.xlsx"
```

```bash
skills/excel-decompose/.venv/bin/python skills/excel-decompose/scripts/reconstruct_excel.py \
  --input "skills/excel-decompose/output/ActuarialPricingModel.txt" \
  --macro-shell "ActuarialPricingModel.xlsm" \
  --output "skills/excel-decompose/output/ActuarialPricingModel_rebuilt.xlsm"
```

## Drop-folder workflow

- Put a workbook into `skills/excel-decompose/decompose_drop/` and run `decompose_here.command`
- Put a decomposition text file into `skills/excel-decompose/reconstruct_drop/` and run `reconstruct_here.command`
- `reconstruct_here.command` always writes a rebuilt `.xlsx`
- If the text file contains a `VBA MODULES` section, `reconstruct_here.command` also writes a rebuilt `.xlsm` when a macro shell `.xlsm` is present in the same folder
- Put a decomposition text file plus a macro shell `.xlsm` into `skills/excel-decompose/reconstruct_drop/` and run `reconstruct_macro_here.command`
- Each command file uses the newest matching source file in its folder and writes the result back into that same folder

## Notes

- The scripts use the skill-local Python environment with `openpyxl`.
- `.xlsm` decomposition also uses `oletools` to extract VBA module code.
- The output is optimized for inspection, not for perfect workbook recreation.
- Decomposition now writes one primary run artifact under `llm_work/runs/<timestamp>/artifacts/decomposition.txt` unless you override the root with `--llm-work-root`.
- Treat `llm_work/current/state.json` as the first place to look for prior workbook-processing context.
- Use `state.json`, `latest_run.json`, `context.md`, and compact run logs to discover the latest decomposition, summary, plan, checklist, and backup artifacts before deciding to rerun helpers.
- Reuse current artifacts only when they still match the workbook state and the user request; otherwise create a fresh run artifact instead of silently relying on stale context.
- Use `--force-refresh` when you intentionally want to bypass reuse logic and regenerate the artifacts.
- Supported orchestration options are `backup`, `summary`, `plan`, and `checklist`.
- `plan` and `checklist` require `--task` because they need the user request text.
- When `summary`, `plan`, or `checklist` are included, the downstream workbook-pipeline scripts run in the same `llm_work/runs/<timestamp>/` context so all artifacts land together.
- Shared strings, formulas, defined names, and sheet ordering are included because those are usually the most useful parts for LLM reasoning.
- VBA modules are appended in a separate `VBA MODULES` section.
- Formatting is intentionally lightweight and readability-first: column widths, merged cells, freeze panes, hidden rows/columns, and tab colors are preserved, while numeric display is rebuilt with generic heuristics instead of exact per-cell Excel formats.
- Plain reconstruction targets `.xlsx`.
- Macro-preserving reconstruction keeps the VBA project from the shell workbook and writes a rebuilt `.xlsm`.

## Evaluation Prompts

- Positive: "Turn this `.xlsm` workbook into an LLM-readable text dump." Expected: decomposition artifact with sheets, formulas, values, names, and VBA modules when available.
- Positive edge: "Compare these workbook versions by first decomposing them." Expected: fresh decomposition artifacts for each workbook.
- Negative: "Edit cell A1 in this workbook." Expected: use workbook-action-executor or live editor, not decomposition alone.
