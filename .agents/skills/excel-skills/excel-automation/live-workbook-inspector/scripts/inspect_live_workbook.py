#!/usr/bin/env python3
"""Inspect values, formulas, and basic formatting from a live Excel workbook."""

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
    parser = argparse.ArgumentParser(description="Inspect a live workbook range through Excel.")
    parser.add_argument("--workbook", required=True, help="Workbook path.")
    parser.add_argument("--sheet", help="Optional worksheet name. Defaults to the active sheet.")
    parser.add_argument("--range", dest="cell_range", help="Optional range such as A1:F20. Defaults to the used range.")
    parser.add_argument("--visible", action="store_true", help="Show Excel while inspecting.")
    parser.add_argument("--keep-open", action="store_true", help="Leave workbook and Excel open after inspection.")
    parser.add_argument("--include-formulas", action="store_true", help="Include formulas where present.")
    parser.add_argument("--include-formats", action="store_true", help="Include number formats, column widths, and freeze panes.")
    parser.add_argument("--max-rows", type=int, default=20, help="Maximum number of rows to include in the sample.")
    parser.add_argument("--max-cols", type=int, default=10, help="Maximum number of columns to include in the sample.")
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


def used_range_address(sheet: xw.Sheet) -> str:
    try:
        return sheet.used_range.address
    except Exception:
        return "A1"


def normalize_table(values: object) -> list[list[object]]:
    if values is None:
        return []
    if isinstance(values, list):
        if not values:
            return []
        if isinstance(values[0], list):
            return values
        return [values]
    return [[values]]


def trim_table(table: list[list[object]], max_rows: int, max_cols: int) -> list[list[object]]:
    return [row[:max_cols] for row in table[:max_rows]]


def read_formulas(rng: xw.Range) -> list[list[object]]:
    formulas = rng.formula
    return normalize_table(formulas)


def read_values(rng: xw.Range) -> list[list[object]]:
    values = rng.value
    return normalize_table(values)


def build_format_summary(sheet: xw.Sheet, rng: xw.Range, max_cols: int) -> dict[str, object]:
    summary: dict[str, object] = {}
    try:
        summary["freeze_panes"] = sheet.api.Parent.Application.ActiveWindow.FreezePanes
    except Exception:
        summary["freeze_panes"] = None
    try:
        summary["number_format"] = rng.number_format
    except Exception:
        summary["number_format"] = None
    try:
        widths = []
        for index in range(1, min(rng.columns.count, max_cols) + 1):
            widths.append(rng.columns[index].column_width)
        summary["column_widths"] = widths
    except Exception:
        summary["column_widths"] = []
    return summary


def main() -> int:
    args = parse_args()
    workbook_path = Path(args.workbook).expanduser().resolve()
    if not workbook_path.exists():
        print(json.dumps({"success": False, "error": f"Workbook not found: {workbook_path}"}), file=sys.stderr)
        return 1

    app, wb, created_app, opened_workbook = open_or_attach(workbook_path, visible=args.visible)
    try:
        sheet = wb.sheets[args.sheet] if args.sheet else wb.sheets.active
        target_address = args.cell_range or used_range_address(sheet)
        rng = sheet.range(target_address)

        value_table = trim_table(read_values(rng), args.max_rows, args.max_cols)
        payload: dict[str, object] = {
            "success": True,
            "workbook": str(workbook_path),
            "workbook_name": wb.name,
            "sheet": sheet.name,
            "target_range": target_address,
            "used_range": used_range_address(sheet),
            "max_rows": args.max_rows,
            "max_cols": args.max_cols,
            "values": value_table,
        }

        if args.include_formulas:
            payload["formulas"] = trim_table(read_formulas(rng), args.max_rows, args.max_cols)

        if args.include_formats:
            payload["formats"] = build_format_summary(sheet, rng, args.max_cols)

        print(json.dumps(payload, indent=2, default=str))
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
