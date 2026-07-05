---
name: window-control
description: Use when a task needs macOS app or window activation, frontmost app inspection, window-title targeting, or saving and restoring app/window state before and after screen interaction work.
---

# Window Control

Use this skill when screen interaction depends on putting the right app or window in front before capture, OCR, or clicking.

## What this skill is for

- Get the current frontmost app
- Activate an app by name
- Activate a window by title match
- Save the current frontmost app and front window bounds
- Restore the saved app/window state after testing
- Move a window
- Resize a window
- Set exact window bounds
- Minimize, maximize, and restore a window

## Command patterns

Get the frontmost app:

```bash
skills/screen-interaction/window-control/.venv/bin/python skills/screen-interaction/window-control/scripts/window_control.py get-frontmost-app
```

Activate an app:

```bash
skills/screen-interaction/window-control/.venv/bin/python skills/screen-interaction/window-control/scripts/window_control.py activate-app --app "TextEdit"
```

Activate a window by title:

```bash
skills/screen-interaction/window-control/.venv/bin/python skills/screen-interaction/window-control/scripts/window_control.py activate-window --title "pricing_calculator"
```

Move a window:

```bash
skills/screen-interaction/window-control/.venv/bin/python skills/screen-interaction/window-control/scripts/window_control.py move-window --title "screen_ocr_test.txt" --x 80 --y 80
```

Resize a window:

```bash
skills/screen-interaction/window-control/.venv/bin/python skills/screen-interaction/window-control/scripts/window_control.py resize-window --title "screen_ocr_test.txt" --width 900 --height 700
```

Set exact bounds:

```bash
skills/screen-interaction/window-control/.venv/bin/python skills/screen-interaction/window-control/scripts/window_control.py set-window-bounds --title "screen_ocr_test.txt" --x 80 --y 80 --width 900 --height 700
```

Minimize or maximize:

```bash
skills/screen-interaction/window-control/.venv/bin/python skills/screen-interaction/window-control/scripts/window_control.py minimize-window --title "screen_ocr_test.txt"
skills/screen-interaction/window-control/.venv/bin/python skills/screen-interaction/window-control/scripts/window_control.py maximize-window --title "screen_ocr_test.txt"
skills/screen-interaction/window-control/.venv/bin/python skills/screen-interaction/window-control/scripts/window_control.py restore-window --title "screen_ocr_test.txt"
```

Save and later restore state:

```bash
skills/screen-interaction/window-control/.venv/bin/python skills/screen-interaction/window-control/scripts/window_control.py save-state
skills/screen-interaction/window-control/.venv/bin/python skills/screen-interaction/window-control/scripts/window_control.py restore-state
```

## Notes

- This is a macOS-specific skill built around AppleScript and System Events.
- It intentionally does not try to implement true always-on-top behavior.
- The reviewed example code remains in `example_codes/`.

## Evaluation Prompts

- Positive: "Activate Excel and move the workbook window to a known position." Expected: app/window activation and bounds operation.
- Positive edge: "Save the current frontmost window state and restore it after testing." Expected: save-state/restore-state sequence.
- Negative: "OCR the active window." Expected: use region-capture or region-ocr after window control.
