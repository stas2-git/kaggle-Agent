---
name: workbook-semantic-summarizer
description: Use when a decomposition text file is too large to reason over directly and the workflow needs a compact workbook brief covering purpose, key sheets, VBA entry points, inputs, outputs, and likely change surfaces.
---

# Workbook Semantic Summarizer

Use this skill between decomposition and planning.

## What this skill is for

- Read workbook decomposition text
- Summarize workbook purpose and likely business role
- Identify important sheets, named ranges, and VBA modules
- Highlight likely input tabs, output tabs, and risky dependencies
- Produce a compact brief for later planning and code generation

## Core workflow

1. Read the decomposition artifact.
2. Identify workbook purpose from sheet names, labels, formulas, and VBA sections.
3. Extract the most important structural elements.
4. Highlight probable change targets and risk areas.
5. Write a concise semantic brief for the LLM.
6. Append a summary event to the run log.

## Expected output

- A compact workbook summary suitable for prompt context
- Optional structured metadata such as key sheets and modules

## Command pattern

```bash
python3 skills/workbook-pipeline/semantic-summarizer/scripts/summarize_workbook.py \
  --input "/path/to/workbook-folder/llm_work/runs/<timestamp>/decomposition/workbook.txt"
```

## Notes

- This skill compresses, it does not replace the source decomposition.
- Prefer short, task-relevant summaries over full workbook restatement.
- When the workbook is extremely large, surface only the parts most relevant to the user's requested change.
- If `--output` is omitted and the decomposition already lives under `llm_work/`, write to the matching run folder and mirror the latest brief into `llm_work/current/summaries/`.
- Prefer saving the brief inside `llm_work/summaries/` beside the workbook so it can be reviewed with the source workbook and later plan artifacts.
- Reuse a prior summary only when the workbook has not changed since that summary was generated. Otherwise create a fresh summary in the new run folder.
- Optionally mirror the latest brief into `llm_work/current/` for convenience.
- Also write the step outcome into `llm_work/runs/<timestamp>/run_log.json`.

## Evaluation Prompts

- Positive: "This decomposition is too large; make a compact workbook brief." Expected: purpose, key sheets, inputs/outputs, VBA, and likely change surfaces.
- Positive edge: "Summarize only the parts relevant to adding a diagnostics tab." Expected: task-focused compression.
- Negative: "Change cell A1 now." Expected: use editor/executor, not semantic summarizer.
