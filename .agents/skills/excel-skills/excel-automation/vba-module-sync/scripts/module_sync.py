#!/usr/bin/env python3
"""Sync VBA modules between disk and Excel workbooks."""

from __future__ import annotations

import argparse
import json
import platform
import re
import subprocess
import sys
from pathlib import Path

import xlwings as xw


VBEXT_COMPONENT_STD_MODULE = 1
VBEXT_COMPONENT_CLASS_MODULE = 2
VBEXT_COMPONENT_MS_FORM = 3
VBEXT_COMPONENT_DOCUMENT = 100


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import, export, and verify VBA modules.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    import_parser = subparsers.add_parser("import-module", help="Import one VBA module into a workbook.")
    import_parser.add_argument("--workbook", required=True, help="Target workbook path.")
    import_parser.add_argument("--module-file", required=True, help="Path to a .bas/.cls/.frm file.")
    import_parser.add_argument("--replace", action="store_true", help="Replace an existing module with the same name first.")
    import_parser.add_argument("--visible", action="store_true", help="Show Excel while running.")
    import_parser.add_argument("--keep-open", action="store_true", help="Leave Excel/workbook open after the operation.")

    export_parser = subparsers.add_parser("export-modules", help="Export workbook VBA modules to disk.")
    export_parser.add_argument("--workbook", required=True, help="Workbook path.")
    export_parser.add_argument("--output-dir", required=True, help="Directory to write exported modules into.")
    export_parser.add_argument("--visible", action="store_true", help="Show Excel while running.")
    export_parser.add_argument("--keep-open", action="store_true", help="Leave Excel/workbook open after the operation.")
    export_parser.add_argument("--include-document-modules", action="store_true", help="Also include ThisWorkbook and sheet modules in the listing.")

    verify_parser = subparsers.add_parser("verify-module", help="Check whether a workbook contains a module.")
    verify_parser.add_argument("--workbook", required=True, help="Workbook path.")
    verify_parser.add_argument("--module-name", required=True, help="Module name to check.")
    verify_parser.add_argument("--visible", action="store_true", help="Show Excel while running.")
    verify_parser.add_argument("--keep-open", action="store_true", help="Leave Excel/workbook open after the operation.")

    list_parser = subparsers.add_parser("list-modules", help="List modules in a workbook.")
    list_parser.add_argument("--workbook", required=True, help="Workbook path.")
    list_parser.add_argument("--visible", action="store_true", help="Show Excel while running.")
    list_parser.add_argument("--keep-open", action="store_true", help="Leave Excel/workbook open after the operation.")
    list_parser.add_argument("--include-document-modules", action="store_true", help="Include ThisWorkbook and sheet modules.")

    return parser.parse_args()


def resolve_path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def olevba_python() -> Path:
    candidate = repo_root() / "skills" / "excel-decompose" / ".venv" / "bin" / "python"
    if not candidate.exists():
        raise FileNotFoundError(
            f"Could not find oletools runtime at {candidate}. Expected the excel-decompose venv to exist."
        )
    return candidate


def parse_vb_name(module_file: Path) -> str:
    content = module_file.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r'Attribute\s+VB_Name\s*=\s*"([^"]+)"', content)
    return match.group(1) if match else module_file.stem


def component_type_name(component_type: int) -> str:
    mapping = {
        VBEXT_COMPONENT_STD_MODULE: "standard",
        VBEXT_COMPONENT_CLASS_MODULE: "class",
        VBEXT_COMPONENT_MS_FORM: "form",
        VBEXT_COMPONENT_DOCUMENT: "document",
    }
    return mapping.get(component_type, f"unknown:{component_type}")


def classify_module_name(name: str) -> tuple[str, int]:
    suffix = Path(name).suffix.lower()
    stem = Path(name).stem
    if stem == "ThisWorkbook" or stem.startswith("Sheet"):
        return "document", VBEXT_COMPONENT_DOCUMENT
    if suffix == ".bas":
        return "standard", VBEXT_COMPONENT_STD_MODULE
    if suffix == ".cls":
        return "class", VBEXT_COMPONENT_CLASS_MODULE
    if suffix == ".frm":
        return "form", VBEXT_COMPONENT_MS_FORM
    return "unknown", 0


def extract_modules_from_workbook(workbook_path: Path) -> list[dict[str, object]]:
    inline = r"""
import json
import sys
from pathlib import Path
from oletools.olevba3 import VBA_Parser

workbook = Path(sys.argv[1])
parser = VBA_Parser(str(workbook))
modules = []
for (_, _, filename, code) in parser.extract_macros():
    modules.append({"filename": filename, "code": code})
print(json.dumps(modules))
"""
    result = subprocess.run(
        [str(olevba_python()), "-c", inline, str(workbook_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    modules = []
    for item in payload:
        module_type, type_code = classify_module_name(item["filename"])
        modules.append(
            {
                "name": Path(item["filename"]).stem,
                "filename": item["filename"],
                "type": module_type,
                "type_code": type_code,
                "code": item["code"],
            }
        )
    return modules


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


def list_components(wb: xw.Book, include_document_modules: bool) -> list[dict[str, object]]:
    components = []
    vb_components = wb.api.VBProject.VBComponents
    for index in range(1, vb_components.Count + 1):
        component = vb_components.Item(index)
        component_type = int(component.Type)
        if not include_document_modules and component_type == VBEXT_COMPONENT_DOCUMENT:
            continue
        components.append(
            {
                "name": str(component.Name),
                "type": component_type_name(component_type),
                "type_code": component_type,
            }
        )
    return components


def list_modules_from_file(workbook_path: Path, include_document_modules: bool) -> list[dict[str, object]]:
    components = []
    for module in extract_modules_from_workbook(workbook_path):
        if not include_document_modules and module["type_code"] == VBEXT_COMPONENT_DOCUMENT:
            continue
        components.append(
            {
                "name": module["name"],
                "filename": module["filename"],
                "type": module["type"],
                "type_code": module["type_code"],
            }
        )
    return components


def get_component_by_name(wb: xw.Book, module_name: str):
    vb_components = wb.api.VBProject.VBComponents
    for index in range(1, vb_components.Count + 1):
        component = vb_components.Item(index)
        if str(component.Name) == module_name:
            return component
    return None


def ensure_importable_module(module_file: Path) -> None:
    if module_file.suffix.lower() not in {".bas", ".cls", ".frm"}:
        raise ValueError(f"Unsupported module extension: {module_file.suffix}")


def import_module(wb: xw.Book, module_file: Path, replace: bool) -> dict[str, object]:
    ensure_importable_module(module_file)
    module_name = parse_vb_name(module_file)
    existing = get_component_by_name(wb, module_name)
    if existing is not None:
        if not replace:
            raise ValueError(f"Module already exists: {module_name}. Pass --replace to overwrite it.")
        existing_type = int(existing.Type)
        if existing_type == VBEXT_COMPONENT_DOCUMENT:
            raise ValueError(f"Refusing to replace document module: {module_name}")
        wb.api.VBProject.VBComponents.Remove(existing)

    imported = wb.api.VBProject.VBComponents.Import(str(module_file))
    wb.save()
    return {
        "module_name": module_name,
        "imported_name": str(imported.Name),
        "source_file": str(module_file),
        "replaced": existing is not None,
    }


def export_modules(wb: xw.Book, output_dir: Path, include_document_modules: bool) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    exported = []
    skipped = []

    vb_components = wb.api.VBProject.VBComponents
    for index in range(1, vb_components.Count + 1):
        component = vb_components.Item(index)
        component_type = int(component.Type)
        component_name = str(component.Name)

        if component_type == VBEXT_COMPONENT_DOCUMENT and not include_document_modules:
            skipped.append({"name": component_name, "reason": "document_module"})
            continue

        extension = {
            VBEXT_COMPONENT_STD_MODULE: ".bas",
            VBEXT_COMPONENT_CLASS_MODULE: ".cls",
            VBEXT_COMPONENT_MS_FORM: ".frm",
            VBEXT_COMPONENT_DOCUMENT: ".cls",
        }.get(component_type, ".txt")

        destination = output_dir / f"{component_name}{extension}"
        component.Export(str(destination))
        exported.append(
            {
                "name": component_name,
                "type": component_type_name(component_type),
                "path": str(destination),
            }
        )

    return {"exported": exported, "skipped": skipped}


def export_modules_from_file(workbook_path: Path, output_dir: Path, include_document_modules: bool) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    exported = []
    skipped = []

    for module in extract_modules_from_workbook(workbook_path):
        if not include_document_modules and module["type_code"] == VBEXT_COMPONENT_DOCUMENT:
            skipped.append({"name": module["name"], "reason": "document_module"})
            continue

        destination = output_dir / module["filename"]
        destination.write_text(module["code"], encoding="utf-8")
        exported.append(
            {
                "name": module["name"],
                "filename": module["filename"],
                "type": module["type"],
                "path": str(destination),
            }
        )

    return {"exported": exported, "skipped": skipped}


def verify_module(wb: xw.Book, module_name: str) -> dict[str, object]:
    component = get_component_by_name(wb, module_name)
    if component is None:
        return {"module_name": module_name, "exists": False}
    return {
        "module_name": module_name,
        "exists": True,
        "type": component_type_name(int(component.Type)),
    }


def verify_module_from_file(workbook_path: Path, module_name: str) -> dict[str, object]:
    for module in extract_modules_from_workbook(workbook_path):
        if module["name"] == module_name:
            return {"module_name": module_name, "exists": True, "type": module["type"]}
    return {"module_name": module_name, "exists": False}


def run_command(args: argparse.Namespace) -> tuple[int, dict[str, object]]:
    workbook_path = resolve_path(args.workbook)
    if not workbook_path.exists():
        raise FileNotFoundError(f"Workbook not found: {workbook_path}")

    if args.command == "export-modules":
        result = export_modules_from_file(
            workbook_path,
            output_dir=resolve_path(args.output_dir),
            include_document_modules=args.include_document_modules,
        )
        return 0, result

    if args.command == "verify-module":
        result = verify_module_from_file(workbook_path, args.module_name)
        return (0 if result["exists"] else 1), result

    if args.command == "list-modules":
        return 0, {
            "modules": list_modules_from_file(
                workbook_path,
                include_document_modules=args.include_document_modules,
            )
        }

    if args.command == "import-module" and platform.system() == "Darwin":
        raise RuntimeError(
            "Direct VBProject import is not currently supported on this macOS Excel automation path. "
            "Use a workbook-native loader macro or Excel screen automation in the VBE for write-side sync."
        )

    app, wb, created_app, opened_workbook = open_workbook(workbook_path, visible=getattr(args, "visible", False))
    keep_open = getattr(args, "keep_open", False)

    try:
        if args.command == "import-module":
            result = import_module(wb, resolve_path(args.module_file), replace=args.replace)
        elif args.command == "export-modules":
            result = export_modules(
                wb,
                output_dir=resolve_path(args.output_dir),
                include_document_modules=args.include_document_modules,
            )
        elif args.command == "verify-module":
            result = verify_module(wb, args.module_name)
            if not result["exists"]:
                return 1, result
        elif args.command == "list-modules":
            result = {
                "modules": list_components(
                    wb,
                    include_document_modules=args.include_document_modules,
                )
            }
        else:
            raise ValueError(f"Unknown command: {args.command}")
        return 0, result
    finally:
        try:
            if not keep_open and opened_workbook:
                wb.close()
        finally:
            if not keep_open and created_app:
                app.quit()


def main() -> int:
    args = parse_args()
    try:
        exit_code, payload = run_command(args)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        print(
            "If Excel blocks VBA project access, confirm Trust Access to the VBA project object model is enabled.",
            file=sys.stderr,
        )
        return 1

    print(json.dumps(payload, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
