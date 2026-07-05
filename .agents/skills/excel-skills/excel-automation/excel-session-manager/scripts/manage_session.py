#!/usr/bin/env python3
"""Manage a live Excel workbook session."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import xlwings as xw


def find_open_workbook(workbook_path: Path) -> tuple[xw.App | None, xw.Book | None]:
    for app in xw.apps:
        try:
            for book in app.books:
                try:
                    if Path(book.fullname).expanduser().resolve() == workbook_path:
                        return app, book
                except Exception:
                    if book.name == workbook_path.name:
                        return app, book
        except Exception:
            continue
    return None, None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Open, activate, save, or inspect an Excel workbook session.")
    parser.add_argument("--workbook", required=True, help="Workbook path.")
    parser.add_argument(
        "--action",
        choices=("status", "open", "activate", "save"),
        default="status",
        help="Session action to perform.",
    )
    parser.add_argument("--sheet", help="Optional worksheet to activate.")
    parser.add_argument("--range", dest="cell_range", help="Optional range to select after sheet activation.")
    parser.add_argument("--visible", action="store_true", help="Show Excel while managing the session.")
    parser.add_argument("--keep-open", action="store_true", help="Leave workbook and app open after the action.")
    return parser.parse_args()


def open_or_attach(workbook_path: Path, visible: bool) -> tuple[xw.App, xw.Book, bool, bool]:
    created_app = False
    opened_workbook = False
    app, wb = find_open_workbook(workbook_path)
    if app is None or wb is None:
        app = xw.App(visible=visible, add_book=False)
        app.display_alerts = False
        created_app = True
        wb = app.books.open(str(workbook_path))
        opened_workbook = True
    else:
        app.visible = visible or app.visible
        app.display_alerts = False
    return app, wb, created_app, opened_workbook


def activate_targets(wb: xw.Book, sheet_name: str | None, cell_range: str | None) -> dict[str, object]:
    sheet = wb.sheets.active
    if sheet_name:
        sheet = wb.sheets[sheet_name]
        sheet.activate()
    if cell_range:
        sheet.range(cell_range).select()
    return {
        "active_sheet": sheet.name,
        "selected_range": cell_range,
    }


def build_payload(
    action: str,
    workbook_path: Path,
    wb: xw.Book,
    app: xw.App,
    opened_workbook: bool,
    created_app: bool,
    details: dict[str, object] | None = None,
) -> dict[str, object]:
    active_sheet_name = None
    try:
        active_sheet_name = wb.sheets.active.name
    except Exception:
        active_sheet_name = None

    return {
        "success": True,
        "action": action,
        "workbook": str(workbook_path),
        "workbook_name": wb.name,
        "sheet_count": len(wb.sheets),
        "active_sheet": active_sheet_name,
        "app_visible": bool(app.visible),
        "opened_workbook": opened_workbook,
        "created_app": created_app,
        "details": details or {},
    }


def main() -> int:
    args = parse_args()
    workbook_path = Path(args.workbook).expanduser().resolve()
    if not workbook_path.exists():
        print(json.dumps({"success": False, "error": f"Workbook not found: {workbook_path}"}), file=sys.stderr)
        return 1

    app, wb, created_app, opened_workbook = open_or_attach(workbook_path, visible=args.visible)
    try:
        details: dict[str, object] = {}
        if args.action in {"open", "activate"}:
            details = activate_targets(wb, args.sheet, args.cell_range)
        elif args.action == "save":
            if args.sheet or args.cell_range:
                details = activate_targets(wb, args.sheet, args.cell_range)
            wb.save()
            details["saved"] = True
        payload = build_payload(args.action, workbook_path, wb, app, opened_workbook, created_app, details)
        print(json.dumps(payload, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"success": False, "action": args.action, "workbook": str(workbook_path), "error": str(exc)}, indent=2), file=sys.stderr)
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
