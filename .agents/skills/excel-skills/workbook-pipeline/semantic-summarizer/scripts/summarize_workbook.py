#!/usr/bin/env python3
"""Turn a workbook decomposition text file into a concise workbook brief."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from _shared.llm_work_audit import (  # type: ignore  # noqa: E402
    append_run_event,
    artifact_path,
    file_metadata,
    infer_run_context,
    task_fingerprint,
)


SECTION_SHEET_PREFIX = "SHEET: "
SECTION_DEFINED_NAMES = "DEFINED NAMES"
SECTION_VBA_MODULES = "VBA MODULES"
SECTION_WORKBOOK_SUMMARY = "WORKBOOK SUMMARY"

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize a workbook decomposition artifact.")
    parser.add_argument("--input", required=True, help="Path to decomposition text file.")
    parser.add_argument("--output", help="Markdown path for the workbook brief.")
    parser.add_argument("--json-output", help="Optional JSON path for structured summary output.")
    parser.add_argument(
        "--llm-work-root",
        help="Optional llm_work directory used to infer summary outputs when not passed explicitly.",
    )
    parser.add_argument(
        "--run-id",
        help="Optional run id used with --llm-work-root when the input path is not already inside a run folder.",
    )
    parser.add_argument(
        "--no-mirror-current",
        action="store_true",
        help="Do not update llm_work/current state files for this run.",
    )
    return parser.parse_args()


def resolve_output_path(value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return path.resolve()


def infer_summary_paths(
    input_path: Path,
    output_value: str | None,
    json_output_value: str | None,
    llm_work_root_value: str | None,
    run_id_value: str | None,
    no_mirror_current: bool,
) -> tuple[Path, Path | None]:
    if output_value:
        output_path = resolve_output_path(output_value)
        json_path = resolve_output_path(json_output_value) if json_output_value else None
        return output_path, json_path

    llm_work_root = resolve_output_path(llm_work_root_value) if llm_work_root_value else None
    run_id = run_id_value

    if llm_work_root is None:
        for parent in input_path.parents:
            if parent.name == "llm_work":
                llm_work_root = parent
                break

    if run_id is None and "runs" in input_path.parts:
        run_index = input_path.parts.index("runs")
        if run_index + 1 < len(input_path.parts):
            run_id = input_path.parts[run_index + 1]

    if llm_work_root is not None:
        run_id = run_id or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
        return artifact_path(llm_work_root, run_id, "summary.md"), artifact_path(llm_work_root, run_id, "summary.json")

    sibling_dir = input_path.parent.parent / "artifacts" if input_path.parent.name == "artifacts" else input_path.parent
    return sibling_dir / "summary.md", sibling_dir / "summary.json"


def find_section_indices(lines: list[str]) -> dict[str, int]:
    indices = {}
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped in {SECTION_WORKBOOK_SUMMARY, SECTION_DEFINED_NAMES, SECTION_VBA_MODULES}:
            indices[stripped] = idx
        elif stripped.startswith(SECTION_SHEET_PREFIX):
            indices.setdefault("__sheet_indices__", [])
            indices["__sheet_indices__"].append(idx)
    return indices


def parse_workbook_summary(lines: list[str], start: int, end: int) -> dict[str, object]:
    summary: dict[str, object] = {"sheet_order": []}
    idx = start + 1
    while idx < end:
        line = lines[idx].rstrip("\n")
        stripped = line.strip()
        if not stripped:
            idx += 1
            continue
        if stripped.startswith("sheet_count:"):
            summary["sheet_count"] = int(stripped.split(":", 1)[1].strip())
        elif stripped == "sheet_order:":
            idx += 1
            while idx < end:
                order_line = lines[idx].strip()
                if not order_line.startswith(tuple(str(n) + "." for n in range(1, 1000))):
                    idx -= 1
                    break
                match = re.match(r"\d+\.\s+(.*)", order_line)
                if match:
                    summary["sheet_order"].append(match.group(1).strip())
                idx += 1
        idx += 1
    return summary


def parse_defined_names(lines: list[str], start: int, end: int) -> list[dict[str, str]]:
    items = []
    for idx in range(start + 1, end):
        stripped = lines[idx].strip()
        if not stripped.startswith("- "):
            continue
        body = stripped[2:]
        if ":" not in body:
            continue
        name, value = body.split(":", 1)
        items.append({"name": name.strip(), "value": value.strip()})
    return items


def parse_sheet_section(lines: list[str], start: int, end: int) -> dict[str, object]:
    header = lines[start].strip()
    sheet_name = header.split(":", 1)[1].strip()
    summary = {
        "name": sheet_name,
        "dimension": None,
        "non_empty_cell_count": 0,
        "sample_labels": [],
        "sample_formulas": [],
    }
    in_cells = False
    for idx in range(start + 1, end):
        stripped = lines[idx].rstrip("\n")
        clean = stripped.strip()
        if not clean:
            continue
        if clean.startswith("dimension:"):
            summary["dimension"] = clean.split(":", 1)[1].strip()
        elif clean.startswith("non_empty_cell_count:"):
            summary["non_empty_cell_count"] = int(clean.split(":", 1)[1].strip())
        elif clean == "cells:":
            in_cells = True
        elif in_cells and clean.startswith("- "):
            cell_text = clean[2:]
            if "formula=" in cell_text and len(summary["sample_formulas"]) < 5:
                summary["sample_formulas"].append(cell_text)
            elif "value=" in cell_text and len(summary["sample_labels"]) < 8:
                summary["sample_labels"].append(cell_text)
            if len(summary["sample_labels"]) >= 8 and len(summary["sample_formulas"]) >= 5:
                break
        elif in_cells:
            break
    return summary


def parse_vba_modules(lines: list[str], start: int, end: int) -> list[dict[str, object]]:
    modules = []
    current: dict[str, object] | None = None
    for idx in range(start + 1, end):
        stripped = lines[idx].strip()
        if stripped.startswith("MODULE: "):
            if current:
                modules.append(current)
            current = {"name": stripped.split(":", 1)[1].strip(), "public_subs": []}
        elif current and stripped.startswith("Public Sub "):
            match = re.match(r"Public Sub ([^(]+)", stripped)
            if match:
                current["public_subs"].append(match.group(1).strip())
    if current:
        modules.append(current)
    return modules


def infer_role(sheet_name: str, sample_labels: list[str]) -> str:
    name = sheet_name.lower()
    joined_labels = " ".join(sample_labels).lower()
    if any(token in name or token in joined_labels for token in ("input", "raw", "source", "data", "sample")):
        return "input_data"
    if any(token in name or token in joined_labels for token in ("summary", "overview", "landing", "quick summary")):
        return "summary"
    if any(token in name or token in joined_labels for token in ("note", "notes", "instruction", "read me")):
        return "notes"
    if any(token in name or token in joined_labels for token in ("tax", "federal", "state", "income", "deduction", "bonus", "salary")):
        return "tax_workpaper"
    if "sample" in name or "data" in name:
        return "input_data"
    if "calculator" in name or "pricing" in name:
        return "pricing_output"
    if "diagnostic" in name or "qq" in name or "pit" in name or "survival" in name or "hist" in name:
        return "diagnostics"
    if "model" in name:
        return "model_core"
    if "view" in name:
        return "reporting_view"
    if "premium" in joined_labels or "retention" in joined_labels:
        return "pricing_output"
    return "general"


def infer_workbook_purpose(summary: dict[str, object]) -> str:
    roles = summary["sheet_roles"]
    all_labels = " ".join(
        label.lower()
        for sheet in summary["all_sheets"]
        for label in sheet.get("sample_labels", [])
    )
    sheet_names = " ".join(sheet["name"].lower() for sheet in summary["all_sheets"])

    if "tax_workpaper" in roles or any(
        token in all_labels or token in sheet_names
        for token in ("tax", "federal", "state", "deduction", "income", "bonus", "salary")
    ):
        return (
            "This workbook appears to be a personal or household tax workpaper with year-specific tabs, "
            "manual inputs, and calculated comparisons for federal and state estimates."
        )

    if "pricing_output" in roles or "model_core" in roles or "diagnostics" in roles:
        return (
            "This workbook appears to be a model-driven workbook with separate areas for source data, "
            "core model logic, pricing or output views, and supporting diagnostics."
        )

    if "summary" in roles and "input_data" in roles:
        return (
            "This workbook appears to combine raw or input sheets with one or more summary/reporting tabs "
            "that help a user navigate or interpret the file."
        )

    if len(summary["all_sheets"]) <= 5:
        return (
            "This workbook appears to be a compact multi-sheet workbook with manually curated tabs and light "
            "formula-driven calculations."
        )

    return (
        "This workbook appears to be a structured spreadsheet with multiple tabs that mix inputs, calculated "
        "outputs, and supporting notes or reporting surfaces."
    )


def build_summary(input_path: Path) -> dict[str, object]:
    text = input_path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    section_indices = find_section_indices(lines)
    sheet_starts = section_indices.get("__sheet_indices__", [])
    workbook_summary_start = section_indices.get(SECTION_WORKBOOK_SUMMARY)
    defined_names_start = section_indices.get(SECTION_DEFINED_NAMES)
    vba_start = section_indices.get(SECTION_VBA_MODULES)

    if workbook_summary_start is None:
        raise ValueError("Could not find WORKBOOK SUMMARY section in decomposition artifact.")

    workbook_summary_end = defined_names_start or (sheet_starts[0] if sheet_starts else len(lines))
    workbook_summary = parse_workbook_summary(lines, workbook_summary_start, workbook_summary_end)

    defined_names = []
    if defined_names_start is not None:
        defined_names_end = sheet_starts[0] if sheet_starts else (vba_start or len(lines))
        defined_names = parse_defined_names(lines, defined_names_start, defined_names_end)

    sheet_summaries = []
    for index, sheet_start in enumerate(sheet_starts):
        end = sheet_starts[index + 1] if index + 1 < len(sheet_starts) else (vba_start or len(lines))
        sheet_summary = parse_sheet_section(lines, sheet_start, end)
        sheet_summary["role"] = infer_role(sheet_summary["name"], sheet_summary["sample_labels"])
        sheet_summaries.append(sheet_summary)

    vba_modules = []
    if vba_start is not None:
        vba_modules = parse_vba_modules(lines, vba_start, len(lines))

    top_defined_names = defined_names[:15]
    sheets_by_size = sorted(sheet_summaries, key=lambda item: item["non_empty_cell_count"], reverse=True)
    top_sheets = sheets_by_size[:8]
    roles = {}
    for sheet in sheet_summaries:
        roles.setdefault(sheet["role"], []).append(sheet["name"])

    summary = {
        "source_file": str(input_path),
        "workbook_summary": workbook_summary,
        "defined_name_count": len(defined_names),
        "top_defined_names": top_defined_names,
        "sheet_count": len(sheet_summaries),
        "top_sheets": top_sheets,
        "all_sheets": sheet_summaries,
        "sheet_roles": roles,
        "purpose_summary": "",
        "vba_modules": vba_modules,
        "public_macro_modules": [m for m in vba_modules if m["public_subs"]],
    }
    summary["purpose_summary"] = infer_workbook_purpose(summary)
    return summary


def render_markdown(summary: dict[str, object]) -> str:
    workbook_summary = summary["workbook_summary"]
    purpose = summary.get("purpose_summary") or infer_workbook_purpose(summary)
    lines = [
        "# Workbook Semantic Brief",
        "",
        f"- Source decomposition: `{summary['source_file']}`",
        f"- Sheet count: {workbook_summary.get('sheet_count', summary['sheet_count'])}",
        f"- Defined names: {summary['defined_name_count']}",
        f"- VBA modules: {len(summary['vba_modules'])}",
        "",
        "## Likely Purpose",
        "",
        purpose,
        "",
        "## Key Sheets",
        "",
    ]

    for sheet in summary["top_sheets"]:
        sample = "; ".join(sheet["sample_labels"][:3]) if sheet["sample_labels"] else "no sample labels extracted"
        lines.append(
            f"- {sheet['name']} ({sheet['role']}): {sheet['non_empty_cell_count']} non-empty cells, "
            f"dimension {sheet['dimension'] or 'unknown'}, sample labels: {sample}"
        )

    lines.extend(["", "## Sheet Roles", ""])
    for role, names in sorted(summary["sheet_roles"].items()):
        lines.append(f"- {role}: {', '.join(names[:8])}")

    lines.extend(["", "## Important Defined Names", ""])
    for item in summary["top_defined_names"]:
        lines.append(f"- {item['name']}: {item['value']}")

    lines.extend(["", "## VBA Entry Points", ""])
    if summary["public_macro_modules"]:
        for module in summary["public_macro_modules"][:12]:
            macros = ", ".join(module["public_subs"][:6])
            lines.append(f"- {module['name']}: {macros}")
    else:
        lines.append("- No public macro procedures detected in the decomposition artifact.")

    lines.extend(["", "## Likely Change Surfaces", ""])
    if summary["sheet_roles"].get("summary"):
        lines.append(
            f"- Summary or landing tabs likely live in: {', '.join(summary['sheet_roles']['summary'])}"
        )
    if summary["sheet_roles"].get("tax_workpaper"):
        lines.append(
            f"- Tax workpaper tabs likely live in: {', '.join(summary['sheet_roles']['tax_workpaper'])}"
        )
    if summary["sheet_roles"].get("pricing_output"):
        lines.append(
            f"- Pricing-facing tabs likely live in: {', '.join(summary['sheet_roles']['pricing_output'])}"
        )
    if summary["sheet_roles"].get("model_core"):
        lines.append(
            f"- Core model logic likely lives in: {', '.join(summary['sheet_roles']['model_core'])}"
        )
    if summary["sheet_roles"].get("diagnostics"):
        lines.append(
            f"- Diagnostics surfaces likely live in: {', '.join(summary['sheet_roles']['diagnostics'][:10])}"
        )
    if summary["vba_modules"]:
        lines.append("- Workbook behavior is partly driven by VBA modules, so layout and automation changes should check both sheets and macros.")
    else:
        lines.append("- No VBA modules were detected, so workbook changes are likely concentrated in sheets, formulas, and formatting.")

    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    started_at = datetime.now(timezone.utc)
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"Input decomposition not found: {input_path}", file=sys.stderr)
        return 1

    summary = build_summary(input_path)
    output_path, json_path = infer_summary_paths(
        input_path=input_path,
        output_value=args.output,
        json_output_value=args.json_output,
        llm_work_root_value=args.llm_work_root,
        run_id_value=args.run_id,
        no_mirror_current=args.no_mirror_current,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown(summary), encoding="utf-8")

    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    llm_work_root, run_id = infer_run_context(output_path)
    run_log_path = None
    if llm_work_root and run_id:
        completed_at = datetime.now(timezone.utc)
        run_log_path = append_run_event(
            llm_work_root,
            run_id,
            {
                "event_type": "workbook-summary.completed",
                "timestamp_utc": completed_at.replace(microsecond=0).isoformat(),
                "started_at_utc": started_at.replace(microsecond=0).isoformat(),
                "duration_ms": int((completed_at - started_at).total_seconds() * 1000),
                "skill": "workbook-semantic-summarizer",
                "status": "completed",
                "source_file": str(input_path),
                "artifacts": {
                    "summary_markdown": file_metadata(output_path),
                    "summary_json": file_metadata(json_path),
                },
                "summary": {
                    "sheet_count": summary["sheet_count"],
                    "defined_name_count": summary["defined_name_count"],
                    "vba_module_count": len(summary["vba_modules"]),
                },
            },
            update_current=not args.no_mirror_current,
        )

    print(f"Wrote workbook brief: {output_path}")
    if json_path:
        print(f"Wrote JSON summary: {json_path}")
    if run_log_path:
        print(f"Wrote run log: {run_log_path}")
    print(f"Sheets summarized: {summary['sheet_count']}")
    print(f"Defined names: {summary['defined_name_count']}")
    print(f"VBA modules: {len(summary['vba_modules'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
