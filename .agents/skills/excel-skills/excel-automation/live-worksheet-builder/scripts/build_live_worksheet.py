#!/usr/bin/env python3
"""Build worksheets through a live Excel session."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import xlwings as xw


STYLE_PRESETS: dict[str, dict[str, Any]] = {
    "title": {
        "font": {"bold": True, "size": 16, "color": "FFFFFF"},
        "fill": {"color": "1F4E78"},
        "alignment": {"horizontal": "center", "vertical": "center", "wrap_text": True},
    },
    "section_header": {
        "font": {"bold": True, "size": 12, "color": "FFFFFF"},
        "fill": {"color": "1F4E78"},
        "alignment": {"vertical": "center", "wrap_text": True},
    },
    "table_header": {
        "font": {"bold": True, "color": "FFFFFF"},
        "fill": {"color": "1F4E78"},
        "alignment": {"horizontal": "center", "vertical": "center", "wrap_text": True},
    },
    "input_cell": {"fill": {"color": "FFF2CC"}},
    "formula_cell": {"fill": {"color": "E2F0D9"}},
    "total": {"font": {"bold": True, "color": "FFFFFF"}, "fill": {"color": "1F4E78"}},
    "note": {"font": {"italic": True, "color": "44546A"}, "fill": {"color": "F3F4F6"}},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build worksheets in a live Excel workbook.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate-plan", help="Validate a live worksheet build plan.")
    validate.add_argument("--plan", required=True, help="Path to JSON plan.")

    build = subparsers.add_parser("build", help="Apply a live worksheet build plan.")
    build.add_argument("--workbook", required=True, help="Workbook path.")
    build.add_argument("--plan", required=True, help="Path to JSON plan.")
    build.add_argument("--visible", action="store_true", help="Show Excel while building.")
    build.add_argument("--hidden", action="store_true", help="Keep Excel hidden if it must be opened.")
    build.add_argument("--save", action="store_true", help="Save after applying the plan.")
    build.add_argument(
        "--close-if-opened",
        action="store_true",
        help="Close the workbook and app if this script had to open them.",
    )
    return parser.parse_args()


def load_plan(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {"actions": data}
    if not isinstance(data, dict):
        raise ValueError("Plan must be a JSON object or a list of actions.")
    return data


def rgb(value: str | tuple[int, int, int] | list[int] | None) -> tuple[int, int, int] | None:
    if value is None:
        return None
    if isinstance(value, (tuple, list)):
        if len(value) != 3:
            raise ValueError(f"RGB colors must have 3 parts: {value}")
        return tuple(int(part) for part in value)  # type: ignore[return-value]
    text = str(value).strip().lstrip("#")
    if len(text) != 6:
        raise ValueError(f"Expected 6-digit hex color, got: {value}")
    return int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16)


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


def open_or_attach(workbook_path: Path, visible: bool) -> tuple[xw.App, xw.Book, bool, bool]:
    app, wb = find_open_workbook(workbook_path)
    if app is not None and wb is not None:
        if visible:
            app.visible = True
        app.display_alerts = False
        return app, wb, False, False

    app = xw.App(visible=visible, add_book=False)
    app.display_alerts = False
    wb = app.books.open(str(workbook_path))
    return app, wb, True, True


def sheet_names(wb: xw.Book) -> list[str]:
    return [sheet.name for sheet in wb.sheets]


def get_sheet(wb: xw.Book, name: str | None) -> xw.Sheet:
    if not name:
        return wb.sheets.active
    return wb.sheets[name]


def delete_sheet(wb: xw.Book, name: str) -> None:
    if len(wb.sheets) <= 1:
        raise ValueError("Cannot replace the only sheet in a workbook.")
    wb.sheets[name].delete()


def ensure_sheet(wb: xw.Book, name: str, if_exists: str = "reuse") -> tuple[xw.Sheet, bool]:
    names = sheet_names(wb)
    if name in names:
        if if_exists == "reuse":
            return wb.sheets[name], False
        if if_exists == "replace":
            delete_sheet(wb, name)
        elif if_exists == "error":
            raise ValueError(f"Sheet already exists: {name}")
        else:
            raise ValueError(f"Unknown if_exists value for {name}: {if_exists}")
    return wb.sheets.add(name=name, after=wb.sheets[-1]), True


def normalize_2d(values: Any) -> list[list[Any]]:
    if not isinstance(values, list):
        raise ValueError("write_block values must be a 2D array.")
    if not values:
        return []
    if all(not isinstance(row, list) for row in values):
        return [values]
    if not all(isinstance(row, list) for row in values):
        raise ValueError("write_block values must use consistent row arrays.")
    return values


def normalize_column_target(target: str) -> str:
    text = target.strip()
    if re.fullmatch(r"[A-Za-z]+", text):
        return f"{text}:{text}"
    return text


def normalize_row_target(target: str) -> str:
    text = target.strip()
    if re.fullmatch(r"\d+", text):
        return f"{text}:{text}"
    return text


def merge_format(preset: str | None, action: dict[str, Any]) -> dict[str, Any]:
    style: dict[str, Any] = {}
    if preset:
        if preset not in STYLE_PRESETS:
            raise ValueError(f"Unknown style preset: {preset}")
        style.update(json.loads(json.dumps(STYLE_PRESETS[preset])))
    for key in ("font", "fill", "alignment", "number_format"):
        if key in action:
            style[key] = action[key]
    return style


def set_api_attr(obj: Any, attr: str, value: Any) -> None:
    try:
        setattr(obj, attr, value)
    except Exception:
        setattr(obj, attr.lower(), value)


def apply_font(rng: xw.Range, font: dict[str, Any]) -> None:
    if "bold" in font:
        rng.font.bold = bool(font["bold"])
    if "italic" in font:
        rng.font.italic = bool(font["italic"])
    if "size" in font:
        rng.font.size = float(font["size"])
    if "name" in font:
        rng.font.name = str(font["name"])
    if "color" in font:
        rng.font.color = rgb(font["color"])


def apply_alignment(rng: xw.Range, alignment: dict[str, Any]) -> None:
    horizontal_map = {"left": -4131, "center": -4108, "right": -4152}
    vertical_map = {"top": -4160, "center": -4108, "bottom": -4107}
    api = rng.api
    if "horizontal" in alignment:
        set_api_attr(api, "HorizontalAlignment", horizontal_map.get(str(alignment["horizontal"]).lower()))
    if "vertical" in alignment:
        set_api_attr(api, "VerticalAlignment", vertical_map.get(str(alignment["vertical"]).lower()))
    if "wrap_text" in alignment:
        set_api_attr(api, "WrapText", bool(alignment["wrap_text"]))


def apply_format(rng: xw.Range, action: dict[str, Any]) -> dict[str, Any]:
    style = merge_format(action.get("preset"), action)
    if "fill" in style and style["fill"].get("color"):
        rng.color = rgb(style["fill"]["color"])
    if "font" in style:
        apply_font(rng, style["font"])
    if "alignment" in style:
        apply_alignment(rng, style["alignment"])
    if "number_format" in style:
        rng.number_format = style["number_format"]
    return style


def apply_action(wb: xw.Book, action: dict[str, Any]) -> dict[str, Any]:
    action_type = action.get("type")
    if not action_type:
        raise ValueError(f"Action missing type: {action}")

    if action_type == "create_sheet":
        sheet, created = ensure_sheet(wb, str(action["name"]), str(action.get("if_exists", "reuse")))
        sheet.activate()
        return {"type": action_type, "sheet": sheet.name, "created": created}

    if action_type == "activate_sheet":
        sheet = get_sheet(wb, action.get("sheet"))
        sheet.activate()
        return {"type": action_type, "sheet": sheet.name}

    sheet = get_sheet(wb, action.get("sheet"))

    if action_type == "write_cells":
        cells = action.get("cells")
        if not isinstance(cells, dict):
            raise ValueError("write_cells requires a cells object.")
        for address, value in cells.items():
            sheet.range(address).value = value
        return {"type": action_type, "sheet": sheet.name, "cells": sorted(cells)}

    if action_type == "write_formulas":
        cells = action.get("cells")
        if not isinstance(cells, dict):
            raise ValueError("write_formulas requires a cells object.")
        for address, formula in cells.items():
            text = str(formula)
            sheet.range(address).formula = text if text.startswith("=") else f"={text}"
        return {"type": action_type, "sheet": sheet.name, "cells": sorted(cells)}

    if action_type == "write_block":
        values = normalize_2d(action.get("values"))
        start = str(action["start"])
        if values:
            sheet.range(start).options(expand=None).value = values
        return {"type": action_type, "sheet": sheet.name, "start": start, "rows": len(values)}

    if action_type in {"merge_cells", "unmerge_cells"}:
        target = str(action["range"])
        rng = sheet.range(target)
        if action_type == "merge_cells":
            rng.merge()
        else:
            rng.api.UnMerge()
        return {"type": action_type, "sheet": sheet.name, "range": target}

    if action_type == "format_range":
        target = str(action["range"])
        applied = apply_format(sheet.range(target), action)
        return {"type": action_type, "sheet": sheet.name, "range": target, "style": applied}

    if action_type == "set_column_widths":
        if not bool(wb.app.visible):
            raise ValueError("set_column_widths requires visible Excel; rerun the build with --visible.")
        widths = action.get("widths")
        if not isinstance(widths, dict):
            raise ValueError("set_column_widths requires a widths object.")
        for target, width in widths.items():
            sheet.range(normalize_column_target(str(target))).column_width = float(width)
        return {"type": action_type, "sheet": sheet.name, "targets": sorted(widths)}

    if action_type == "set_row_heights":
        if not bool(wb.app.visible):
            raise ValueError("set_row_heights requires visible Excel; rerun the build with --visible.")
        heights = action.get("heights")
        if not isinstance(heights, dict):
            raise ValueError("set_row_heights requires a heights object.")
        for target, height in heights.items():
            sheet.range(normalize_row_target(str(target))).row_height = float(height)
        return {"type": action_type, "sheet": sheet.name, "targets": sorted(heights)}

    if action_type == "autofit":
        if not bool(wb.app.visible):
            raise ValueError("autofit requires visible Excel; rerun the build with --visible.")
        target = sheet.range(str(action.get("range", "A1"))).expand() if action.get("range") else sheet.used_range
        if action.get("columns", True):
            target.columns.autofit()
        if action.get("rows", False):
            target.rows.autofit()
        return {"type": action_type, "sheet": sheet.name, "range": target.address}

    if action_type == "freeze_panes":
        cell = str(action["cell"])
        if not bool(wb.app.visible):
            raise ValueError("freeze_panes requires visible Excel; rerun the build with --visible.")
        sheet.activate()
        sheet.range(cell).select()
        app = wb.app
        app.api.ActiveWindow.FreezePanes = False
        app.api.ActiveWindow.SplitColumn = sheet.range(cell).column - 1
        app.api.ActiveWindow.SplitRow = sheet.range(cell).row - 1
        app.api.ActiveWindow.FreezePanes = True
        return {"type": action_type, "sheet": sheet.name, "cell": cell}

    if action_type == "set_sheet_view":
        sheet.activate()
        app = wb.app
        if "show_gridlines" in action:
            app.api.ActiveWindow.DisplayGridlines = bool(action["show_gridlines"])
        if "zoom" in action:
            app.api.ActiveWindow.Zoom = int(action["zoom"])
        if "tab_color" in action:
            sheet.api.Tab.Color = rgb(action["tab_color"])
        return {"type": action_type, "sheet": sheet.name}

    raise ValueError(f"Unsupported action type: {action_type}")


def validate_plan(plan: dict[str, Any]) -> dict[str, Any]:
    actions = plan.get("actions")
    if not isinstance(actions, list) or not actions:
        raise ValueError("Plan must contain a non-empty actions list.")
    for index, action in enumerate(actions, start=1):
        if not isinstance(action, dict):
            raise ValueError(f"Action {index} must be an object.")
        if "type" not in action:
            raise ValueError(f"Action {index} is missing type.")
    return {"success": True, "action_count": len(actions), "target_sheet": plan.get("target_sheet")}


def run_validate(args: argparse.Namespace) -> int:
    plan_path = Path(args.plan).expanduser().resolve()
    try:
        payload = validate_plan(load_plan(plan_path))
        payload["plan"] = str(plan_path)
        print(json.dumps(payload, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"success": False, "plan": str(plan_path), "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


def run_build(args: argparse.Namespace) -> int:
    workbook_path = Path(args.workbook).expanduser().resolve()
    plan_path = Path(args.plan).expanduser().resolve()
    if not workbook_path.exists():
        print(json.dumps({"success": False, "error": f"Workbook not found: {workbook_path}"}), file=sys.stderr)
        return 1

    try:
        plan = load_plan(plan_path)
        validate_plan(plan)
    except Exception as exc:
        print(json.dumps({"success": False, "plan": str(plan_path), "error": str(exc)}, indent=2), file=sys.stderr)
        return 1

    app = None
    wb = None
    created_app = False
    opened_workbook = False
    visible = args.visible or not args.hidden
    try:
        app, wb, created_app, opened_workbook = open_or_attach(workbook_path, visible=visible)
        changes = [apply_action(wb, action) for action in plan["actions"]]
        target_sheet = plan.get("target_sheet")
        if target_sheet and target_sheet in sheet_names(wb):
            wb.sheets[target_sheet].activate()
        if args.save:
            wb.save()
        payload = {
            "success": True,
            "workbook": str(workbook_path),
            "workbook_name": wb.name,
            "plan": str(plan_path),
            "saved": bool(args.save),
            "created_app": created_app,
            "opened_workbook": opened_workbook,
            "sheet_count": len(wb.sheets),
            "active_sheet": wb.sheets.active.name,
            "change_count": len(changes),
            "changes": changes,
        }
        print(json.dumps(payload, indent=2, default=str))
        return 0
    except Exception as exc:
        print(json.dumps({"success": False, "workbook": str(workbook_path), "error": str(exc)}, indent=2), file=sys.stderr)
        return 1
    finally:
        if args.close_if_opened:
            try:
                if wb is not None and opened_workbook:
                    wb.close()
            finally:
                if app is not None and created_app:
                    app.quit()


def main() -> int:
    args = parse_args()
    if args.command == "validate-plan":
        return run_validate(args)
    if args.command == "build":
        return run_build(args)
    raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    sys.exit(main())
