---
name: vba-module-sync
description: Use when a workflow needs to inspect or export VBA modules from an Excel workbook, and when write-side VBA injection must happen through Excel screen automation in the VBE rather than direct Python-to-VBProject automation.
---

# VBA Module Sync

Use this skill when VBA code needs to move between disk and a workbook, especially in environments where write-side injection has to happen through the Excel VBA editor.

## What this skill is for

- Export workbook modules to disk
- List workbook VBA modules
- Remove a target module before reimport when needed
- Verify that the expected modules exist after sync
- Define the screen-automation path for opening the VBE, creating a module, pasting code, and running it

## Core workflow

1. Export or inspect workbook VBA from the workbook file when read-only access is enough.
2. If the workflow needs write-side injection, open the workbook in Excel.
3. Use screen automation to open the VBE, insert a module, paste code, and save.
4. Run the target macro or loader path to verify the workbook accepts the injected code.
5. Export or verify modules again when a post-change check is needed.

## Command patterns

List workbook modules:

```bash
python3 skills/excel-automation/vba-module-sync/scripts/module_sync.py list-modules \
  --workbook "/path/to/model.xlsm"
```

Export workbook modules:

```bash
python3 skills/excel-automation/vba-module-sync/scripts/module_sync.py export-modules \
  --workbook "/path/to/model.xlsm" \
  --output-dir "/path/to/workbook-folder/llm_work/exported_vba"
```

Verify a module exists:

```bash
python3 skills/excel-automation/vba-module-sync/scripts/module_sync.py verify-module \
  --workbook "/path/to/model.xlsm" \
  --module-name "Step6PricingTab"
```

Screen-automation write path:

```text
Open workbook in Excel -> open VBE -> insert module -> paste VBA -> save workbook -> run macro
```

## Notes

- Prefer the workbook's own bootstrap/import macro path when it exists.
- Preserve workbook macros by working with `.xlsm` files when modules are involved.
- Treat module replacement as a deliberate action, not a default guess.
- Current first pass: `list-modules`, `verify-module`, and `export-modules` work from the workbook file itself.
- Prefer exporting VBA into `llm_work/exported_vba/` beside the workbook so the extracted code stays easy to inspect.
- On follow-up runs, export VBA into the active run folder so you can compare revisions instead of overwriting the prior export silently.
- Current write-side direction: use screen automation in Excel/VDI for opening the VBE, creating modules, pasting code, and running macros.
- Direct Python-to-`VBProject` import is not the intended write path for this setup.

## Evaluation Prompts

- Positive: "Export the VBA modules from this `.xlsm` workbook." Expected: module listing/export artifacts, no workbook mutation.
- Positive edge: "Inject this module through the VBE path and verify it exists." Expected: screen automation write path plus verification/export.
- Negative: "Run the existing macro now." Expected: use macro-runner unless module sync is also needed.
