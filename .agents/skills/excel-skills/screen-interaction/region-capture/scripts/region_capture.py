#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import tempfile
import time
from pathlib import Path


def activate_app(app_name: str, settle_delay: float) -> None:
    subprocess.run(["osascript", "-e", f'tell application "{app_name}" to activate'], check=True)
    if settle_delay > 0:
        time.sleep(settle_delay)


def validate_region(x: int, y: int, width: int, height: int) -> None:
    values = [x, y, width, height]
    if not all(isinstance(value, int) for value in values):
        raise SystemExit("Region values must be integers.")
    if width <= 0 or height <= 0:
        raise SystemExit("Region width and height must be positive.")


def capture(output_path: Path, region: tuple[int, int, int, int] | None = None) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["screencapture", "-x"]
    if region is not None:
        x, y, width, height = region
        validate_region(x, y, width, height)
        cmd.extend(["-R", f"{x},{y},{width},{height}"])
    cmd.append(str(output_path))
    subprocess.run(cmd, check=True)
    return output_path


def temp_output_path() -> Path:
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as handle:
        return Path(handle.name)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Capture the macOS screen or a region.")
    parser.add_argument("--activate-app", help="Bring an app to the front before capture")
    parser.add_argument("--activate-delay", type=float, default=0.25, help="Seconds to wait after activation")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fullscreen = subparsers.add_parser("capture-fullscreen", help="Capture the full screen")
    fullscreen.add_argument("--output", help="Output PNG path")

    region = subparsers.add_parser("capture-region", help="Capture an exact screen region")
    region.add_argument("--x", type=int, required=True)
    region.add_argument("--y", type=int, required=True)
    region.add_argument("--width", type=int, required=True)
    region.add_argument("--height", type=int, required=True)
    region.add_argument("--output", help="Output PNG path")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.activate_app:
        activate_app(args.activate_app, args.activate_delay)

    output_path = Path(args.output).expanduser().resolve() if args.output else temp_output_path()

    if args.command == "capture-fullscreen":
        print(capture(output_path))
        return 0

    region = (args.x, args.y, args.width, args.height)
    print(capture(output_path, region=region))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
