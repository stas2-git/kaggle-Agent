#!/usr/bin/env python3
"""Run a named Excel macro and return structured results."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import xlwings as xw


REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_WORKBOOK = REPO_ROOT / "ActuarialPricingModel.xlsm"
DEFAULT_LOADER_MACRO = "BootstrapLoader.RunBootstrapRefresh"


def find_open_workbook(workbook_path: Path) -> tuple[xw.App | None, xw.Book | None]:
    for app in xw.apps:
        try:
            for book in app.books:
                try:
                    if Path(book.fullname).resolve() == workbook_path:
                        return app, book
                except Exception:
                    if book.name == workbook_path.name:
                        return app, book
        except Exception:
            continue
    return None, None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an Excel macro against a workbook.")
    parser.add_argument("--workbook", default=str(DEFAULT_WORKBOOK), help="Workbook path.")
    parser.add_argument(
        "--macro",
        help="Direct macro to run, such as Step6PricingTab.Step6PricingTab.",
    )
    parser.add_argument(
        "--use-loader",
        action="store_true",
        help="Run the workbook's loader macro instead of invoking a direct macro.",
    )
    parser.add_argument(
        "--loader-macro",
        default=DEFAULT_LOADER_MACRO,
        help=f"Loader macro to call when --use-loader is set. Default: {DEFAULT_LOADER_MACRO}",
    )
    parser.add_argument(
        "--macro-arg",
        action="append",
        default=[],
        help="Optional positional argument passed to the macro. Can be repeated.",
    )
    parser.add_argument("--visible", action="store_true", help="Show Excel while running.")
    parser.add_argument("--keep-open", action="store_true", help="Leave workbook and Excel open after execution.")
    parser.add_argument("--save", action="store_true", help="Save the workbook after a successful macro run.")
    return parser.parse_args()


def open_workbook(workbook_path: Path, visible: bool) -> tuple[xw.App, xw.Book, bool, bool]:
    created_app = False
    opened_workbook = False
    app, wb = find_open_workbook(workbook_path)

    if app is None or wb is None:
        app = xw.App(visible=visible, add_book=False)
        created_app = True
        app.display_alerts = False
        wb = app.books.open(str(workbook_path))
        opened_workbook = True
    else:
        app.visible = visible or app.visible
        app.display_alerts = False

    return app, wb, created_app, opened_workbook


def run_named_macro(wb: xw.Book, macro_name: str, args: list[str]) -> str:
    wb.macro(macro_name)(*args)
    return macro_name


def main() -> int:
    args = parse_args()
    workbook_path = Path(args.workbook).expanduser().resolve()
    if not workbook_path.exists():
        print(f"Workbook not found: {workbook_path}", file=sys.stderr)
        return 1

    if args.use_loader and args.macro:
        print("Use either --macro or --use-loader, not both.", file=sys.stderr)
        return 1

    if not args.use_loader and not args.macro:
        print("Provide --macro or pass --use-loader.", file=sys.stderr)
        return 1

    app, wb, created_app, opened_workbook = open_workbook(workbook_path, visible=args.visible)
    started = time.time()
    target_macro = args.loader_macro if args.use_loader else args.macro
    effective_args = args.macro_arg

    try:
        run_named_macro(wb, target_macro, effective_args)
        if args.save:
            wb.save()
        payload = {
            "success": True,
            "workbook": str(workbook_path),
            "macro": target_macro,
            "mode": "loader" if args.use_loader else "direct",
            "args": effective_args,
            "elapsed_seconds": round(time.time() - started, 3),
            "saved": args.save,
        }
        print(json.dumps(payload, indent=2))
        return 0
    except Exception as exc:
        payload = {
            "success": False,
            "workbook": str(workbook_path),
            "macro": target_macro,
            "mode": "loader" if args.use_loader else "direct",
            "args": effective_args,
            "elapsed_seconds": round(time.time() - started, 3),
            "error": str(exc),
        }
        print(json.dumps(payload, indent=2), file=sys.stderr)
        return 1
    finally:
        try:
            if not args.keep_open and opened_workbook:
                wb.close()
        finally:
            if not args.keep_open and created_app:
                app.quit()


if __name__ == "__main__":
    sys.exit(main())
