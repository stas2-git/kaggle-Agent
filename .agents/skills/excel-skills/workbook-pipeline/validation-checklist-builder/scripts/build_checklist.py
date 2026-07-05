#!/usr/bin/env python3
"""Build a structured validation checklist from a workbook change plan."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from _shared.llm_work_audit import (  # type: ignore  # noqa: E402
    append_run_event,
    artifact_path,
    file_metadata,
    infer_run_context,
)



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a validation checklist from a change plan.")
    parser.add_argument("--plan", required=True, help="Path to change-plan JSON.")
    parser.add_argument("--output", help="Path to checklist JSON output.")
    parser.add_argument("--markdown-output", help="Optional markdown rendering of the checklist.")
    parser.add_argument(
        "--llm-work-root",
        help="Optional llm_work directory used to infer checklist outputs when not passed explicitly.",
    )
    parser.add_argument(
        "--run-id",
        help="Optional run id used with --llm-work-root when the plan path is not already inside a run folder.",
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


def infer_checklist_paths(
    plan_path: Path,
    output_value: str | None,
    markdown_output_value: str | None,
    llm_work_root_value: str | None,
    run_id_value: str | None,
    no_mirror_current: bool,
) -> tuple[Path, Path | None]:
    if output_value:
        output_path = resolve_output_path(output_value)
        markdown_path = resolve_output_path(markdown_output_value) if markdown_output_value else None
        return output_path, markdown_path

    llm_work_root = resolve_output_path(llm_work_root_value) if llm_work_root_value else None
    run_id = run_id_value

    if llm_work_root is None:
        for parent in plan_path.parents:
            if parent.name == "llm_work":
                llm_work_root = parent
                break

    if run_id is None and "runs" in plan_path.parts:
        run_index = plan_path.parts.index("runs")
        if run_index + 1 < len(plan_path.parts):
            run_id = plan_path.parts[run_index + 1]

    if llm_work_root is not None:
        run_id = run_id or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
        return artifact_path(llm_work_root, run_id, "checklist.json"), artifact_path(llm_work_root, run_id, "checklist.md")

    sibling_dir = plan_path.parent.parent / "artifacts" if plan_path.parent.name == "artifacts" else plan_path.parent
    return sibling_dir / "checklist.json", sibling_dir / "checklist.md"


def make_check(
    check_id: str,
    title: str,
    method: str,
    priority: str,
    target: str,
    expectation: str,
    automation_hint: str,
    kind: str,
) -> dict[str, str]:
    return {
        "id": check_id,
        "title": title,
        "method": method,
        "priority": priority,
        "target": target,
        "expectation": expectation,
        "automation_hint": automation_hint,
        "kind": kind,
    }


def build_sheet_checks(plan: dict) -> list[dict[str, str]]:
    checks = []
    for idx, sheet in enumerate(plan.get("relevant_sheets", [])[:8], start=1):
        checks.append(
            make_check(
                check_id=f"sheet-exists-{idx}",
                title=f"Sheet exists: {sheet}",
                method="workbook_structure",
                priority="must_pass",
                target=sheet,
                expectation=f"Worksheet `{sheet}` is present after the change.",
                automation_hint="Use workbook inspection or sheet activation by name.",
                kind="sheet_presence",
            )
        )
    return checks


def build_module_checks(plan: dict) -> list[dict[str, str]]:
    checks = []
    for idx, module in enumerate(plan.get("relevant_modules", [])[:4], start=1):
        checks.append(
            make_check(
                check_id=f"module-run-{idx}",
                title=f"Macro path still valid for {module}",
                method="macro_runner",
                priority="must_pass",
                target=module,
                expectation=f"Workbook automation tied to `{module}` can still run without error.",
                automation_hint="Use macro-runner on the loader path or direct entry point.",
                kind="macro_execution",
            )
        )
    return checks


def build_request_type_checks(plan: dict) -> list[dict[str, str]]:
    checks = []
    request_types = plan.get("request_types", [])

    if "layout" in request_types:
        checks.append(
            make_check(
                check_id="layout-visible-labels",
                title="Readable labels remain visible",
                method="screen_ocr",
                priority="must_pass",
                target="key workbook surfaces",
                expectation="Key section headers and labels remain visible and easier to scan after the change.",
                automation_hint="Use OCR on the affected tabs after macro execution.",
                kind="ui_readability",
            )
        )

    if "diagnostics" in request_types:
        checks.append(
            make_check(
                check_id="diagnostics-populated",
                title="Diagnostics outputs populate",
                method="screen_ocr_or_workbook_structure",
                priority="must_pass",
                target="diagnostics sheets",
                expectation="Diagnostics sheets still populate rows, labels, charts, or summary outputs.",
                automation_hint="Use OCR for visible labels and workbook checks for sheet existence.",
                kind="diagnostics_output",
            )
        )

    if "pricing" in request_types:
        checks.append(
            make_check(
                check_id="pricing-fields-present",
                title="Pricing fields remain present",
                method="screen_ocr",
                priority="must_pass",
                target="pricing sheets",
                expectation="Pricing-facing sheets still show technical premium, market premium, and related labels.",
                automation_hint="Use OCR on pricing tabs such as pricing_calculator or market_vs_technical.",
                kind="pricing_output",
            )
        )

    if "model_logic" in request_types or "formula_logic" in request_types:
        checks.append(
            make_check(
                check_id="model-formulas-intact",
                title="Model surfaces still calculate",
                method="workbook_structure_or_screen_ocr",
                priority="must_pass",
                target="model sheets",
                expectation="Model sheets still show populated formula-driven outputs after the macro run.",
                automation_hint="Open model tabs and confirm visible outputs or summary values are present.",
                kind="model_integrity",
            )
        )

    return checks


def build_defined_name_checks(plan: dict) -> list[dict[str, str]]:
    checks = []
    for idx, name in enumerate(plan.get("relevant_defined_names", [])[:4], start=1):
        checks.append(
            make_check(
                check_id=f"defined-name-{idx}",
                title=f"Named item still relevant: {name}",
                method="workbook_structure",
                priority="informational",
                target=name,
                expectation=f"Defined name `{name}` is still present or intentionally changed.",
                automation_hint="Use workbook inspection if named-range validation is available later.",
                kind="defined_name",
            )
        )
    return checks


def build_risk_checks(plan: dict) -> list[dict[str, str]]:
    checks = []
    for idx, risk in enumerate(plan.get("risks", [])[:3], start=1):
        priority = "must_pass" if risk["level"] == "high" else "informational"
        checks.append(
            make_check(
                check_id=f"risk-{idx}",
                title=f"Risk follow-up: {risk['level']}",
                method="manual_or_structured_review",
                priority=priority,
                target="risk review",
                expectation=risk["reason"],
                automation_hint="Use this as a review reminder when interpreting validation results.",
                kind="risk_note",
            )
        )
    return checks


def build_checklist(plan: dict) -> dict[str, object]:
    checks = []
    checks.extend(build_sheet_checks(plan))
    checks.extend(build_module_checks(plan))
    checks.extend(build_request_type_checks(plan))
    checks.extend(build_defined_name_checks(plan))
    checks.extend(build_risk_checks(plan))

    return {
        "task": plan["task"],
        "overall_risk": plan.get("overall_risk", "unknown"),
        "check_count": len(checks),
        "checks": checks,
    }


def render_markdown(checklist: dict[str, object]) -> str:
    lines = [
        "# Validation Checklist",
        "",
        f"- Task: {checklist['task']}",
        f"- Overall risk: {checklist['overall_risk']}",
        f"- Check count: {checklist['check_count']}",
        "",
    ]

    for check in checklist["checks"]:
        lines.append(
            f"- [{check['priority']}] {check['title']} | method={check['method']} | target={check['target']} | expectation={check['expectation']}"
        )

    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    started_at = datetime.now(timezone.utc)
    plan_path = Path(args.plan).expanduser().resolve()
    if not plan_path.exists():
        print(f"Plan not found: {plan_path}", file=sys.stderr)
        return 1

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    checklist = build_checklist(plan)

    output_path, markdown_path = infer_checklist_paths(
        plan_path=plan_path,
        output_value=args.output,
        markdown_output_value=args.markdown_output,
        llm_work_root_value=args.llm_work_root,
        run_id_value=args.run_id,
        no_mirror_current=args.no_mirror_current,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(checklist, indent=2) + "\n", encoding="utf-8")

    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_markdown(checklist), encoding="utf-8")

    llm_work_root, run_id = infer_run_context(output_path)
    run_log_path = None
    if llm_work_root and run_id:
        completed_at = datetime.now(timezone.utc)
        run_log_path = append_run_event(
            llm_work_root,
            run_id,
            {
                "event_type": "workbook-checklist.completed",
                "timestamp_utc": completed_at.replace(microsecond=0).isoformat(),
                "started_at_utc": started_at.replace(microsecond=0).isoformat(),
                "duration_ms": int((completed_at - started_at).total_seconds() * 1000),
                "skill": "validation-checklist-builder",
                "status": "completed",
                "source_file": str(plan_path),
                "artifacts": {
                    "checklist_json": file_metadata(output_path),
                    "checklist_markdown": file_metadata(markdown_path),
                },
                "summary": {
                    "overall_risk": checklist["overall_risk"],
                    "check_count": checklist["check_count"],
                },
            },
            update_current=not args.no_mirror_current,
        )

    print(f"Wrote checklist JSON: {output_path}")
    if markdown_path:
        print(f"Wrote checklist markdown: {markdown_path}")
    if run_log_path:
        print(f"Wrote run log: {run_log_path}")
    print(f"Checks built: {checklist['check_count']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
