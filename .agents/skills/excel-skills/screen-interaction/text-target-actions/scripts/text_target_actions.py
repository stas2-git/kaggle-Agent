#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

def activate_app(app_name: str, settle_delay: float) -> None:
    subprocess.run(["osascript", "-e", f'tell application "{app_name}" to activate'], check=True)
    if settle_delay > 0:
        time.sleep(settle_delay)


def capture_screen_image(
    output_path: Path, x: int | None = None, y: int | None = None, width: int | None = None, height: int | None = None
) -> Path:
    cmd = ["screencapture", "-x"]
    if None not in (x, y, width, height):
        cmd.extend(["-R", f"{x},{y},{width},{height}"])
    cmd.append(str(output_path))
    subprocess.run(cmd, check=True)
    return output_path


def normalize_text(value: str) -> str:
    return " ".join(value.strip().lower().split())


def match_text(candidate: str, target: str, mode: str) -> bool:
    left = normalize_text(candidate)
    right = normalize_text(target)
    if mode == "exact":
        return left == right
    return right in left


def ocr_records(image_path: Path, origin_x: int = 0, origin_y: int = 0, confidence_threshold: float = 0.0):
    try:
        from PIL import Image
    except ModuleNotFoundError as exc:
        raise SystemExit("Pillow is required for OCR image loading. Install pillow in the active Python environment.") from exc
    try:
        from apple_vision_ocr import text_from_image, vision_bbox_to_pixels
    except ModuleNotFoundError as exc:
        raise SystemExit("Apple Vision OCR requires pyobjc. Install pyobjc in the active Python environment.") from exc

    image = Image.open(image_path)
    width, height = image.size
    records = []
    for item in text_from_image(image, confidence_threshold=confidence_threshold):
        x1, y1, x2, y2 = vision_bbox_to_pixels(item.bbox, width, height)
        records.append(
            {
                "text": item.text,
                "confidence": round(item.confidence, 4),
                "image_bbox": [x1, y1, x2, y2],
                "screen_bbox": [origin_x + x1, origin_y + y1, origin_x + x2, origin_y + y2],
                "center": [origin_x + round((x1 + x2) / 2), origin_y + round((y1 + y2) / 2)],
            }
        )
    return records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Find text on screen and act on the match.")
    parser.add_argument("--activate-app", help="Bring this macOS app to the front before capture")
    parser.add_argument("--activate-delay", type=float, default=0.25)
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name in ("find-text", "click-text"):
        sub = subparsers.add_parser(name)
        sub.add_argument("--text", required=True)
        sub.add_argument("--screen", action="store_true")
        sub.add_argument("--image")
        sub.add_argument("--x", type=int)
        sub.add_argument("--y", type=int)
        sub.add_argument("--width", type=int)
        sub.add_argument("--height", type=int)
        sub.add_argument("--match-mode", choices=["contains", "exact"], default="contains")
        sub.add_argument("--index", type=int, default=0)
        sub.add_argument("--confidence-threshold", type=float, default=0.0)
        sub.add_argument("--json", action="store_true")
        if name == "click-text":
            sub.add_argument("--dry-run", action="store_true")
            sub.add_argument("--move-duration", type=float, default=0.1)
            sub.add_argument("--button", choices=["left", "middle", "right"], default="left")
    return parser


def resolve_image(args) -> tuple[Path, int, int]:
    if args.image:
        return Path(args.image).expanduser().resolve(), 0, 0
    if not args.screen:
        raise SystemExit("Use --screen or --image.")

    if args.activate_app:
        activate_app(args.activate_app, args.activate_delay)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as handle:
        image_path = Path(handle.name)
    capture_screen_image(image_path, args.x, args.y, args.width, args.height)
    return image_path, args.x or 0, args.y or 0


def choose_match(records: list[dict], text: str, match_mode: str, index: int) -> dict:
    matches = [r for r in records if match_text(r["text"], text, match_mode)]
    matches.sort(key=lambda item: (-item["confidence"], item["center"][1], item["center"][0]))
    if not matches:
        raise SystemExit(f'No OCR match found for "{text}"')
    if index < 0 or index >= len(matches):
        raise SystemExit(f"Match index {index} is out of range for {len(matches)} match(es)")
    return matches[index]


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    image_path, origin_x, origin_y = resolve_image(args)
    records = ocr_records(
        image_path,
        origin_x=origin_x,
        origin_y=origin_y,
        confidence_threshold=args.confidence_threshold,
    )
    match = choose_match(records, args.text, args.match_mode, args.index)

    if args.command == "find-text":
        if args.json:
            print(json.dumps(match, indent=2))
        else:
            print(match)
        return 0

    if args.dry_run:
        if args.json:
            print(json.dumps(match, indent=2))
        else:
            print(match)
        return 0

    try:
        import pyautogui
    except ModuleNotFoundError as exc:
        raise SystemExit("pyautogui is required for click-text without --dry-run. Install pyautogui first.") from exc

    pyautogui.FAILSAFE = True
    pyautogui.moveTo(match["center"][0], match["center"][1], duration=args.move_duration)
    pyautogui.click(match["center"][0], match["center"][1], button=args.button)
    if args.json:
        print(json.dumps(match, indent=2))
    else:
        print(match)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
