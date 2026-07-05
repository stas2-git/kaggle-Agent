---
name: region-ocr
description: Use when a task needs OCR over an image, the full screen, or an exact screen region, returning structured text, confidence, and bounding boxes without bundling clicks into the same skill.
---

# Region OCR

Use this skill when you need to read text from pixels and return structured OCR results.

## What this skill is for

- OCR an existing image file
- OCR the full screen
- OCR an exact screen region
- Return text, confidence, image bounding boxes, and screen coordinates when available

## Command patterns

OCR an image file:

```bash
skills/screen-interaction/region-ocr/.venv/bin/python skills/screen-interaction/region-ocr/scripts/region_ocr.py ocr-image --image /tmp/region.png --json
```

OCR the full screen:

```bash
skills/screen-interaction/region-ocr/.venv/bin/python skills/screen-interaction/region-ocr/scripts/region_ocr.py ocr-screen --json
```

OCR a screen region:

```bash
skills/screen-interaction/region-ocr/.venv/bin/python skills/screen-interaction/region-ocr/scripts/region_ocr.py ocr-region --x 100 --y 100 --width 400 --height 200 --json
```

Filter results:

```bash
skills/screen-interaction/region-ocr/.venv/bin/python skills/screen-interaction/region-ocr/scripts/region_ocr.py ocr-screen --contains "Allow"
```

## Notes

- This skill reuses the Apple Vision OCR implementation that was first proven inside `screen-ocr-interaction`.
- Unlike `screen-ocr-interaction`, this skill does not click anything.
- Clicks belong in `text-target-actions`.

## Evaluation Prompts

- Positive: "OCR the visible Excel dialog and return the text boxes." Expected: OCR results with text/confidence/coordinates, no clicks.
- Positive edge: "OCR only this region and filter for the word Allow." Expected: region-limited OCR with filtered matches.
- Negative: "Click the Allow button." Expected: use text-target-actions after OCR targeting.
