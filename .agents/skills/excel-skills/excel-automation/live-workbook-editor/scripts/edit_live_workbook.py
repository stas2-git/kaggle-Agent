#!/usr/bin/env python3
"""Apply narrow live edits to an open Excel workbook."""

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
    parser = argparse.ArgumentParser(description="Apply narrow live edits to an Excel workbook.")
    parser.add_argument("--workbook", required=True, help="Workbook path.")
    parser.add_argument("--sheet", help="Optional sheet name. Defaults to active sheet.")
    parser.add_argument("--visible", action="store_true", help="Show Excel while editing.")
    parser.add_argument("--keep-open", action="store_true", help="Leave workbook and app open after editing.")
    parser.add_argument("--save", action="store_true", help="Save the workbook after applying edits.")
    parser.add_argument("--add-sheet", action="append", default=[], help="Add a sheet with this name if it does not already exist.")
    parser.add_argument("--activate-sheet", help="Activate this sheet before applying range edits.")
    parser.add_argument("--set-value", action="append", default=[], help="Set a cell value, like A1=Hello.")
    parser.add_argument("--set-formula", action="append", default=[], help="Set a cell formula, like B2==SUM(A1:A10).")
    parser.add_argument("--set-number-format", action="append", default=[], help="Set number format, like C:C=$#,##0.00.")
    parser.add_argument("--set-column-width", action="append", default=[], help="Set column width, like A=18 or B:D=24.")
    parser.add_argument("--freeze-panes", help="Freeze panes at a cell, like A2.")
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


def split_assignment(raw: str) -> tuple[str, str]:
    if "=" not in raw:
        raise ValueError(f"Expected assignment like A1=value, got: {raw}")
    left, right = raw.split("=", 1)
    left = left.strip()
    if not left:
        raise ValueError(f"Missing left-hand target in assignment: {raw}")
    return left, right


def ensure_sheet(wb: xw.Book, name: str) -> tuple[xw.Sheet, bool]:
    for sheet in wb.sheets:
        if sheet.name == name:
            return sheet, False
    return wb.sheets.add(name=name, after=wb.sheets[-1]), True


def main() -> int:
    args = parse_args()
    workbook_path = Path(args.workbook).expanduser().resolve()
    if not workbook_path.exists():
        print(json.dumps({"success": False, "error": f"Workbook not found: {workbook_path}"}), file=sys.stderr)
        return 1

    app, wb, created_app, opened_workbook = open_or_attach(workbook_path, visible=args.visible)
    try:
        changes: list[dict[str, object]] = []

        for sheet_name in args.add_sheet:
            _, created = ensure_sheet(wb, sheet_name)
            changes.append({"type": "add_sheet", "sheet": sheet_name, "created": created})

        target_sheet = wb.sheets[args.activate_sheet] if args.activate_sheet else (wb.sheets[args.sheet] if args.sheet else wb.sheets.active)
        target_sheet.activate()

        for raw in args.set_value:
            target, value = split_assignment(raw)
            target_sheet.range(target).value = value
            changes.append({"type": "set_value", "sheet": target_sheet.name, "target": target, "value": value})

        for raw in args.set_formula:
            target, formula = split_assignment(raw)
            if not formula.startswith("="):
                formula = "=" + formula
            target_sheet.range(target).formula = formula
            changes.append({"type": "set_formula", "sheet": target_sheet.name, "target": target, "formula": formula})

        for raw in args.set_number_format:
            target, number_format = split_assignment(raw)
            target_sheet.range(target).number_format = number_format
            changes.append({"type": "set_number_format", "sheet": target_sheet.name, "target": target, "number_format": number_format})

        for raw in args.set_column_width:
            target, width_text = split_assignment(raw)
            width = float(width_text)
            target_sheet.range(target).column_width = width
            changes.append({"type": "set_column_width", "sheet": target_sheet.name, "target": target, "column_width": width})

        if args.freeze_panes:
            target_sheet.activate()
            target_sheet.range(args.freeze_panes).select()
            app.api.ActiveWindow.FreezePanes = False
            app.api.ActiveWindow.SplitColumn = target_sheet.range(args.freeze_panes).column - 1
            app.api.ActiveWindow.SplitRow = target_sheet.range(args.freeze_panes).row - 1
            app.api.ActiveWindow.FreezePanes = True
            changes.append({"type": "freeze_panes", "sheet": target_sheet.name, "target": args.freeze_panes})

        if args.save:
            wb.save()

        payload = {
            "success": True,
            "workbook": str(workbook_path),
            "workbook_name": wb.name,
            "active_sheet": target_sheet.name,
            "saved": args.save,
            "opened_workbook": opened_workbook,
            "created_app": created_app,
            "change_count": len(changes),
            "changes": changes,
        }
        print(json.dumps(payload, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"success": False, "workbook": str(workbook_path), "error": str(exc)}, indent=2), file=sys.stderr)
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
