---
name: text-target-actions
description: Use when a task needs to locate visible text on screen and act on it, such as finding a match, returning the best target, or clicking the matched text box center.
---

# Text Target Actions

Use this skill when OCR results should drive an action.

## What this skill is for

- Find text on screen
- Return the best matching target
- Click the center of a matched text box
- Dry-run a target selection before clicking

## Command patterns

Find text:

```bash
skills/screen-interaction/text-target-actions/.venv/bin/python skills/screen-interaction/text-target-actions/scripts/text_target_actions.py find-text --screen --text "Allow" --json
```

Click text:

```bash
skills/screen-interaction/text-target-actions/.venv/bin/python skills/screen-interaction/text-target-actions/scripts/text_target_actions.py --activate-app "TextEdit" click-text --screen --text "SCREEN OCR TARGET"
```

Dry-run a click target:

```bash
skills/screen-interaction/text-target-actions/.venv/bin/python skills/screen-interaction/text-target-actions/scripts/text_target_actions.py --activate-app "TextEdit" click-text --screen --text "SCREEN OCR TARGET" --dry-run
```

## Notes

- This skill reuses the same Apple Vision OCR helper code that was proven in the older composed OCR skill.
- It is intentionally action-focused.
- OCR-only extraction belongs in `region-ocr`.

## Evaluation Prompts

- Positive: "Find and click the visible text 'Allow'." Expected: OCR target selection followed by click.
- Positive edge: "Dry-run the click target before clicking." Expected: target coordinates without side effect.
- Negative: "Tell me what text is visible on screen." Expected: use region-ocr, not action skill.
