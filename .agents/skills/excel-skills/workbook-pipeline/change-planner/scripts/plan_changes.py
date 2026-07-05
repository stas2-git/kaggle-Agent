#!/usr/bin/env python3
"""Generate a workbook-specific change plan from a semantic workbook brief."""

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


KEYWORD_TO_REQUEST_TYPE = {
    "layout": "layout",
    "readability": "layout",
    "cleaner": "layout",
    "format": "layout",
    "diagnostic": "diagnostics",
    "diagnostics": "diagnostics",
    "chart": "diagnostics",
    "pivot": "diagnostics",
    "pricing": "pricing",
    "premium": "pricing",
    "calculator": "pricing",
    "automation": "automation",
    "macro": "automation",
    "vba": "automation",
    "refactor": "refactor",
    "formula": "formula_logic",
    "solver": "formula_logic",
    "model": "model_logic",
}


MODULE_HINTS = {
    "pricing": ["Step6PricingTab.bas", "Step4ModelFreq.bas"],
    "diagnostics": ["Step3Diagnostics.bas", "Step5FreqDiagnostics.bas"],
    "layout": ["Step2CreateModel.bas", "Step6PricingTab.bas"],
    "automation": ["BootstrapLoader.bas", "BootstrapRefresh.bas"],
    "model_logic": ["Step2CreateModel.bas", "Step4ModelFreq.bas"],
    "formula_logic": ["Step2CreateModel.bas", "Step4ModelFreq.bas", "Step6PricingTab.bas"],
    "refactor": ["BootstrapRefresh.bas", "Step2CreateModel.bas", "Step6PricingTab.bas"],
}


RISK_LEVELS = {
    "layout": "low",
    "diagnostics": "medium",
    "pricing": "medium",
    "automation": "high",
    "refactor": "high",
    "model_logic": "high",
    "formula_logic": "high",
}

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plan workbook changes from a semantic brief.")
    parser.add_argument("--brief", required=True, help="Path to semantic brief JSON.")
    parser.add_argument("--task", required=True, help="User task to plan for.")
    parser.add_argument("--output", help="Markdown path for the plan.")
    parser.add_argument("--json-output", help="Optional JSON path for structured plan output.")
    parser.add_argument(
        "--llm-work-root",
        help="Optional llm_work directory used to infer plan outputs when not passed explicitly.",
    )
    parser.add_argument(
        "--run-id",
        help="Optional run id used with --llm-work-root when the brief path is not already inside a run folder.",
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


def infer_plan_paths(
    brief_path: Path,
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
        for parent in brief_path.parents:
            if parent.name == "llm_work":
                llm_work_root = parent
                break

    if run_id is None and "runs" in brief_path.parts:
        run_index = brief_path.parts.index("runs")
        if run_index + 1 < len(brief_path.parts):
            run_id = brief_path.parts[run_index + 1]

    if llm_work_root is not None:
        run_id = run_id or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
        return artifact_path(llm_work_root, run_id, "plan.md"), artifact_path(llm_work_root, run_id, "plan.json")

    sibling_dir = brief_path.parent.parent / "artifacts" if brief_path.parent.name == "artifacts" else brief_path.parent
    return sibling_dir / "plan.md", sibling_dir / "plan.json"


def classify_request(task: str) -> list[str]:
    lowered = task.lower()
    found = []
    for keyword, request_type in KEYWORD_TO_REQUEST_TYPE.items():
        if keyword in lowered and request_type not in found:
            found.append(request_type)
    return found or ["layout"]


def choose_relevant_sheets(brief: dict, request_types: list[str], task: str) -> list[str]:
    sheet_roles = brief.get("sheet_roles", {})
    selected = []

    for request_type in request_types:
        if request_type == "layout":
            selected.extend(sheet_roles.get("pricing_output", []))
            selected.extend(sheet_roles.get("model_core", []))
        elif request_type == "diagnostics":
            selected.extend(sheet_roles.get("diagnostics", []))
        elif request_type == "pricing":
            selected.extend(sheet_roles.get("pricing_output", []))
            selected.extend(sheet_roles.get("reporting_view", []))
        elif request_type in {"model_logic", "formula_logic"}:
            selected.extend(sheet_roles.get("model_core", []))
            selected.extend(sheet_roles.get("pricing_output", []))
        elif request_type == "automation":
            selected.extend(sheet_roles.get("pricing_output", []))
        elif request_type == "refactor":
            selected.extend(sheet_roles.get("model_core", []))
            selected.extend(sheet_roles.get("pricing_output", []))
            selected.extend(sheet_roles.get("diagnostics", []))

    lowered_task = task.lower()
    for sheet in brief.get("all_sheets", []):
        if sheet["name"].lower() in lowered_task and sheet["name"] not in selected:
            selected.append(sheet["name"])

    if not selected:
        for sheet in brief.get("top_sheets", [])[:6]:
            selected.append(sheet["name"])

    deduped = []
    seen = set()
    for name in selected:
        if name not in seen:
            deduped.append(name)
            seen.add(name)
    return deduped[:10]


def choose_relevant_modules(request_types: list[str], task: str, brief: dict) -> list[str]:
    modules = []
    for request_type in request_types:
        modules.extend(MODULE_HINTS.get(request_type, []))

    lowered_task = task.lower()
    for module in brief.get("public_macro_modules", []):
        module_name = module["name"]
        if module_name.lower().replace(".bas", "") in lowered_task and module_name not in modules:
            modules.append(module_name)

    if not brief.get("public_macro_modules"):
        return []

    deduped = []
    seen = set()
    for name in modules:
        if name not in seen:
            deduped.append(name)
            seen.add(name)
    return deduped[:8]


def choose_relevant_defined_names(brief: dict, task: str) -> list[str]:
    lowered_task = task.lower()
    matches = []
    for item in brief.get("top_defined_names", []):
        if item["name"].lower() in lowered_task:
            matches.append(item["name"])

    if matches:
        return matches

    for item in brief.get("top_defined_names", []):
        if any(token in item["name"].lower() for token in ("beta", "gamma", "freq", "premium", "eps")):
            matches.append(item["name"])
        if len(matches) >= 6:
            break
    return matches


def build_plan_steps(request_types: list[str], relevant_sheets: list[str], relevant_modules: list[str]) -> list[str]:
    steps = []
    if relevant_sheets:
        steps.append(f"Inspect and update the target workbook surfaces: {', '.join(relevant_sheets)}.")
    if relevant_modules:
        steps.append(f"Review and adjust likely VBA modules: {', '.join(relevant_modules)}.")

    if "layout" in request_types:
        steps.append("Prefer layout and labeling improvements that preserve existing formulas where possible.")
    if "diagnostics" in request_types:
        steps.append("Add or refine diagnostics outputs in a way that keeps interpretation visible on-sheet.")
    if "pricing" in request_types:
        steps.append("Validate any pricing-facing changes against the model and reporting tabs that feed them.")
    if "automation" in request_types:
        steps.append("Treat workbook automation changes as high-risk and validate both macro execution and visible workbook state.")
    if "formula_logic" in request_types or "model_logic" in request_types:
        steps.append("Review formula-bearing sheets carefully and minimize business-logic changes unless they are explicitly requested.")

    steps.append("Generate a validation checklist before changing code so success criteria are explicit.")
    return steps


def build_validation_focus(request_types: list[str], relevant_sheets: list[str], relevant_modules: list[str]) -> list[str]:
    checks = []
    for sheet in relevant_sheets[:6]:
        checks.append(f"Confirm sheet `{sheet}` still exists and opens in the expected workbook order.")

    if "layout" in request_types:
        checks.append("Check that key labels and section headers remain visible and easier to read after the change.")
    if "diagnostics" in request_types:
        checks.append("Check that diagnostics tabs still populate rows, charts, or summary values after the macro run.")
    if "pricing" in request_types:
        checks.append("Check that pricing tabs still show technical premium and market premium fields.")
    if relevant_modules:
        checks.append(f"Verify the runner can still execute the likely entry-point modules or loader path tied to {', '.join(relevant_modules[:3])}.")
    else:
        checks.append("Verify the workbook still opens cleanly and that the updated sheets remain readable after the change.")
    return checks[:10]


def build_risks(request_types: list[str], relevant_sheets: list[str], relevant_modules: list[str]) -> list[dict[str, str]]:
    risks = []
    highest = "low"
    for request_type in request_types:
        level = RISK_LEVELS.get(request_type, "medium")
        if level == "high":
            highest = "high"
        elif level == "medium" and highest != "high":
            highest = "medium"

    if any(request_type in {"formula_logic", "model_logic"} for request_type in request_types):
        risks.append({"level": "high", "reason": "Requested work may touch model formulas or solver-driven logic."})
    if "automation" in request_types:
        risks.append({"level": "high", "reason": "Workbook automation or macro changes can break refresh and execution paths."})
    if relevant_modules:
        risks.append({"level": "medium", "reason": "VBA module edits require re-running macros and verifying workbook state."})
    if relevant_sheets:
        risks.append({"level": highest, "reason": "Sheet-level edits should preserve labels, formulas, and tab visibility."})
    if not relevant_modules:
        risks.append({"level": "low", "reason": "No VBA modules were identified, so the main risk is workbook layout or formula drift rather than macro execution."})
    return risks


def render_markdown(plan: dict[str, object]) -> str:
    lines = [
        "# Workbook Change Plan",
        "",
        f"- Task: {plan['task']}",
        f"- Request types: {', '.join(plan['request_types'])}",
        f"- Overall risk: {plan['overall_risk']}",
        "",
        "## Affected Surfaces",
        "",
        f"- Relevant sheets: {', '.join(plan['relevant_sheets']) if plan['relevant_sheets'] else 'none identified'}",
        f"- Relevant VBA modules: {', '.join(plan['relevant_modules']) if plan['relevant_modules'] else 'none identified'}",
        f"- Relevant defined names: {', '.join(plan['relevant_defined_names']) if plan['relevant_defined_names'] else 'none identified'}",
        "",
        "## Plan Steps",
        "",
    ]

    for step in plan["plan_steps"]:
        lines.append(f"- {step}")

    lines.extend(["", "## Validation Focus", ""])
    for item in plan["validation_focus"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Risks", ""])
    for risk in plan["risks"]:
        lines.append(f"- {risk['level']}: {risk['reason']}")

    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    started_at = datetime.now(timezone.utc)
    brief_path = Path(args.brief).expanduser().resolve()
    if not brief_path.exists():
        print(f"Brief not found: {brief_path}", file=sys.stderr)
        return 1

    brief = json.loads(brief_path.read_text(encoding="utf-8"))
    request_types = classify_request(args.task)
    relevant_sheets = choose_relevant_sheets(brief, request_types, args.task)
    relevant_modules = choose_relevant_modules(request_types, args.task, brief)
    relevant_defined_names = choose_relevant_defined_names(brief, args.task)
    risks = build_risks(request_types, relevant_sheets, relevant_modules)
    overall_risk = "low"
    if any(risk["level"] == "high" for risk in risks):
        overall_risk = "high"
    elif any(risk["level"] == "medium" for risk in risks):
        overall_risk = "medium"

    plan = {
        "task": args.task,
        "request_types": request_types,
        "overall_risk": overall_risk,
        "relevant_sheets": relevant_sheets,
        "relevant_modules": relevant_modules,
        "relevant_defined_names": relevant_defined_names,
        "plan_steps": build_plan_steps(request_types, relevant_sheets, relevant_modules),
        "validation_focus": build_validation_focus(request_types, relevant_sheets, relevant_modules),
        "risks": risks,
    }

    output_path, json_path = infer_plan_paths(
        brief_path=brief_path,
        output_value=args.output,
        json_output_value=args.json_output,
        llm_work_root_value=args.llm_work_root,
        run_id_value=args.run_id,
        no_mirror_current=args.no_mirror_current,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown(plan), encoding="utf-8")

    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

    llm_work_root, run_id = infer_run_context(output_path)
    run_log_path = None
    if llm_work_root and run_id:
        completed_at = datetime.now(timezone.utc)
        run_log_path = append_run_event(
            llm_work_root,
            run_id,
            {
                "event_type": "workbook-plan.completed",
                "timestamp_utc": completed_at.replace(microsecond=0).isoformat(),
                "started_at_utc": started_at.replace(microsecond=0).isoformat(),
                "duration_ms": int((completed_at - started_at).total_seconds() * 1000),
                "skill": "workbook-change-planner",
                "status": "completed",
                "source_file": str(brief_path),
                "task": args.task,
                "task_fingerprint": task_fingerprint(args.task),
                "artifacts": {
                    "plan_markdown": file_metadata(output_path),
                    "plan_json": file_metadata(json_path),
                },
                "summary": {
                    "request_types": request_types,
                    "relevant_sheet_count": len(relevant_sheets),
                    "relevant_module_count": len(relevant_modules),
                    "overall_risk": overall_risk,
                },
            },
            update_current=not args.no_mirror_current,
        )

    print(f"Wrote change plan: {output_path}")
    if json_path:
        print(f"Wrote JSON plan: {json_path}")
    if run_log_path:
        print(f"Wrote run log: {run_log_path}")
    print(f"Request types: {', '.join(request_types)}")
    print(f"Relevant sheets: {len(relevant_sheets)}")
    print(f"Relevant modules: {len(relevant_modules)}")
    print(f"Overall risk: {overall_risk}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
