---
name: wait-and-assert
description: Use when a task needs to poll screen state until text appears or disappears, assert that text exists, or fail cleanly after a timeout.
---

# Wait And Assert

Use this skill when reliability matters more than acting immediately.

## What this skill is for

- Check whether text currently exists on screen
- Wait until text appears
- Wait until text disappears
- Assert text presence with a nonzero exit on failure

## Command patterns

Check whether text exists:

```bash
skills/screen-interaction/wait-and-assert/.venv/bin/python skills/screen-interaction/wait-and-assert/scripts/wait_and_assert.py --activate-app "TextEdit" text-exists --screen --text "SCREEN OCR TARGET"
```

Wait for text to appear:

```bash
skills/screen-interaction/wait-and-assert/.venv/bin/python skills/screen-interaction/wait-and-assert/scripts/wait_and_assert.py --activate-app "TextEdit" wait-for-text --screen --text "SCREEN OCR TARGET" --timeout 5
```

Wait for text to disappear:

```bash
skills/screen-interaction/wait-and-assert/.venv/bin/python skills/screen-interaction/wait-and-assert/scripts/wait_and_assert.py --activate-app "TextEdit" wait-for-no-text --screen --text "Loading..." --timeout 10
```

Assert text:

```bash
skills/screen-interaction/wait-and-assert/.venv/bin/python skills/screen-interaction/wait-and-assert/scripts/wait_and_assert.py --activate-app "TextEdit" assert-text --screen --text "SCREEN OCR TARGET"
```

## Notes

- This first pass is text-only and OCR-based.
- It intentionally does not wait on image templates yet.
- The command exits nonzero when assertions or waits fail.

## Evaluation Prompts

- Positive: "Wait until the Excel dialog shows Calculation complete." Expected: poll OCR until text appears or timeout.
- Positive edge: "Assert Loading disappeared before continuing." Expected: wait-for-no-text with nonzero failure on timeout.
- Negative: "Click the OK button immediately." Expected: use text-target-actions, not wait/assert alone.
