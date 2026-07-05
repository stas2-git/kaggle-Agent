#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
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
            }
        )
    return records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Wait for OCR text conditions on macOS.")
    parser.add_argument("--activate-app", help="Bring this macOS app to the front before screen capture")
    parser.add_argument("--activate-delay", type=float, default=0.25)
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name in ("text-exists", "wait-for-text", "wait-for-no-text", "assert-text"):
        sub = subparsers.add_parser(name)
        sub.add_argument("--text", required=True)
        sub.add_argument("--screen", action="store_true")
        sub.add_argument("--image")
        sub.add_argument("--x", type=int)
        sub.add_argument("--y", type=int)
        sub.add_argument("--width", type=int)
        sub.add_argument("--height", type=int)
        sub.add_argument("--match-mode", choices=["contains", "exact"], default="contains")
        sub.add_argument("--confidence-threshold", type=float, default=0.0)
        sub.add_argument("--timeout", type=float, default=5.0)
        sub.add_argument("--poll-interval", type=float, default=0.25)
        sub.add_argument("--json", action="store_true")
    return parser


def resolve_records(args):
    if args.image:
        image_path = Path(args.image).expanduser().resolve()
        return ocr_records(image_path, confidence_threshold=args.confidence_threshold)

    if not args.screen:
        raise SystemExit("Use --screen or --image.")

    if args.activate_app:
        activate_app(args.activate_app, args.activate_delay)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as handle:
        image_path = Path(handle.name)
    capture_screen_image(image_path, args.x, args.y, args.width, args.height)
    return ocr_records(
        image_path,
        origin_x=args.x or 0,
        origin_y=args.y or 0,
        confidence_threshold=args.confidence_threshold,
    )


def matching_records(records: list[dict], text: str, match_mode: str) -> list[dict]:
    return [record for record in records if match_text(record["text"], text, match_mode)]


def wait_until(args, want_present: bool) -> tuple[bool, list[dict], float]:
    start = time.time()
    last_matches: list[dict] = []
    while True:
        records = resolve_records(args)
        last_matches = matching_records(records, args.text, args.match_mode)
        found = bool(last_matches)
        if found == want_present:
            return True, last_matches, time.time() - start
        if time.time() - start >= args.timeout:
            return False, last_matches, time.time() - start
        time.sleep(args.poll_interval)


def emit_result(success: bool, matches: list[dict], elapsed: float, as_json: bool) -> None:
    payload = {
        "success": success,
        "elapsed_seconds": round(elapsed, 3),
        "match_count": len(matches),
        "matches": matches,
    }
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(payload)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "text-exists":
        records = resolve_records(args)
        matches = matching_records(records, args.text, args.match_mode)
        emit_result(bool(matches), matches, 0.0, args.json)
        return 0 if matches else 1

    if args.command == "assert-text":
        records = resolve_records(args)
        matches = matching_records(records, args.text, args.match_mode)
        emit_result(bool(matches), matches, 0.0, args.json)
        return 0 if matches else 1

    if args.command == "wait-for-text":
        success, matches, elapsed = wait_until(args, want_present=True)
        emit_result(success, matches, elapsed, args.json)
        return 0 if success else 1

    success, matches, elapsed = wait_until(args, want_present=False)
    emit_result(success, matches, elapsed, args.json)
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
