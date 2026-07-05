---
name: region-capture
description: Use when a task needs a clean screenshot primitive such as full-screen capture or exact region capture, without bundling OCR or action logic into the same skill.
---

# Region Capture

Use this skill when you need pixels from the screen, not OCR or clicking.

## What this skill is for

- Capture the full screen to a PNG
- Capture an exact rectangle defined by `x`, `y`, `width`, and `height`
- Optionally activate an app just before capture for more stable testing

## Command patterns

Capture the full screen:

```bash
skills/screen-interaction/region-capture/.venv/bin/python skills/screen-interaction/region-capture/scripts/region_capture.py capture-fullscreen --output /tmp/full.png
```

Capture a region:

```bash
skills/screen-interaction/region-capture/.venv/bin/python skills/screen-interaction/region-capture/scripts/region_capture.py capture-region --x 100 --y 100 --width 400 --height 200 --output /tmp/region.png
```

Capture a region after activating an app:

```bash
skills/screen-interaction/region-capture/.venv/bin/python skills/screen-interaction/region-capture/scripts/region_capture.py --activate-app "TextEdit" capture-region --x 100 --y 100 --width 400 --height 200 --output /tmp/region.png
```

## Notes

- This skill is intentionally capture-only.
- OCR belongs in `region-ocr`.
- Clicks belong in `text-target-actions`.

## Evaluation Prompts

- Positive: "Capture this exact screen region for later OCR." Expected: screenshot artifact or JSON path, no OCR.
- Positive edge: "Capture the active Excel window before validation." Expected: window/app-aware capture when requested.
- Negative: "Read the text in this image." Expected: use region-ocr, not capture only.
