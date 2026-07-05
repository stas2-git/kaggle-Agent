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
    parser = argparse.ArgumentParser(description="OCR images or screen regions on macOS.")
    parser.add_argument("--activate-app", help="Bring this macOS app to the front before screen capture")
    parser.add_argument("--activate-delay", type=float, default=0.25)
    subparsers = parser.add_subparsers(dest="command", required=True)

    image_parser = subparsers.add_parser("ocr-image", help="OCR an existing image file")
    image_parser.add_argument("--image", required=True)
    image_parser.add_argument("--contains")
    image_parser.add_argument("--match-mode", choices=["contains", "exact"], default="contains")
    image_parser.add_argument("--confidence-threshold", type=float, default=0.0)
    image_parser.add_argument("--json", action="store_true")

    screen_parser = subparsers.add_parser("ocr-screen", help="Capture and OCR the full screen")
    screen_parser.add_argument("--contains")
    screen_parser.add_argument("--match-mode", choices=["contains", "exact"], default="contains")
    screen_parser.add_argument("--confidence-threshold", type=float, default=0.0)
    screen_parser.add_argument("--json", action="store_true")

    region_parser = subparsers.add_parser("ocr-region", help="Capture and OCR an exact screen region")
    region_parser.add_argument("--x", type=int, required=True)
    region_parser.add_argument("--y", type=int, required=True)
    region_parser.add_argument("--width", type=int, required=True)
    region_parser.add_argument("--height", type=int, required=True)
    region_parser.add_argument("--contains")
    region_parser.add_argument("--match-mode", choices=["contains", "exact"], default="contains")
    region_parser.add_argument("--confidence-threshold", type=float, default=0.0)
    region_parser.add_argument("--json", action="store_true")
    return parser


def resolve_records(args):
    if args.command == "ocr-image":
        image_path = Path(args.image).expanduser().resolve()
        return ocr_records(image_path, confidence_threshold=args.confidence_threshold)

    if args.activate_app:
        activate_app(args.activate_app, args.activate_delay)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as handle:
        image_path = Path(handle.name)

    if args.command == "ocr-screen":
        capture_screen_image(image_path)
        return ocr_records(image_path, confidence_threshold=args.confidence_threshold)

    capture_screen_image(image_path, args.x, args.y, args.width, args.height)
    return ocr_records(
        image_path,
        origin_x=args.x,
        origin_y=args.y,
        confidence_threshold=args.confidence_threshold,
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    records = resolve_records(args)

    if args.contains:
        records = [r for r in records if match_text(r["text"], args.contains, args.match_mode)]

    if args.json:
        print(json.dumps(records, indent=2))
        return 0

    for record in records:
        print(
            f'{record["text"]} | conf={record["confidence"]:.4f} | '
            f'image_bbox={record["image_bbox"]} | screen_bbox={record["screen_bbox"]}'
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
