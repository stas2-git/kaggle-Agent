#!/usr/bin/env python3
"""Validate the Excel skill package without external dependencies."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
MAX_SKILL_LINES = 220
MAX_ACTIVE_REFERENCE_LINES = 900
ALLOWED_NAME_FOLDER_MISMATCH = {
    ("excel-skills", "excel-skills-router"),
    ("macro-runner", "workbook-macro-runner"),
    ("backup-versioning", "workbook-backup-versioning"),
    ("change-planner", "workbook-change-planner"),
    ("semantic-summarizer", "workbook-semantic-summarizer"),
}
SKIP_DIR_PARTS = {"examples", "example_codes", "__pycache__"}
DISALLOWED_ACTIVE_DIRS = {"decompose_drop", "example_codes", "examples", "output", "reconstruct_drop"}
DISALLOWED_ACTIVE_FILES = {
    "FUTURE_IMPROVEMENTS.md",
    "GAME_PLAN.md",
    "RELATION_TO_OLDER_SKILL.md",
    "web-examples.md",
}
STALE_PATTERNS = (
    "/Users/stan/Documents/actuarial",
    "/Users/stan/Documents/excel_llm_project",
    "excel/skills/",
    "excel/skills/SKILL.md",
    "excel/skills/scripts/validate_excel_skills.py",
    "skills/sync_excel_skills_to_codex.sh",
)


def rel(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def add(errors: list[str], path: Path, message: str) -> None:
    errors.append(f"{rel(path)}: {message}")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def count_fences(body: str) -> int:
    return sum(1 for line in body.splitlines() if line.startswith("```"))


def active_file(path: Path) -> bool:
    return not any(part in SKIP_DIR_PARTS for part in path.parts)


def parse_frontmatter(path: Path, errors: list[str]) -> tuple[str, str]:
    lines = read_text(path).splitlines()
    if len(lines) < 4 or lines[0] != "---":
        add(errors, path, "missing YAML frontmatter")
        return "", ""
    try:
        end = lines.index("---", 1)
    except ValueError:
        add(errors, path, "frontmatter is not closed")
        return "", ""

    fields: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            add(errors, path, f"invalid frontmatter line: {line}")
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"')

    name = fields.get("name", "")
    description = fields.get("description", "")
    if not name:
        add(errors, path, "missing name")
    if not description:
        add(errors, path, "missing description")
    if description and "Use " not in description:
        add(errors, path, "description should include a Use/Use when trigger")
    return name, description


def check_skill(path: Path, errors: list[str]) -> None:
    body = read_text(path)
    name, _ = parse_frontmatter(path, errors)
    folder = path.parent.name
    if name and folder != name and (folder, name) not in ALLOWED_NAME_FOLDER_MISMATCH:
        add(errors, path, f"skill folder {folder!r} does not match name {name!r}")
    if len(body.splitlines()) > MAX_SKILL_LINES:
        add(errors, path, f"SKILL.md exceeds {MAX_SKILL_LINES} lines")
    if "## Evaluation Prompts" not in body:
        add(errors, path, "missing ## Evaluation Prompts")
    if count_fences(body) % 2:
        add(errors, path, "unbalanced code fences")

    for match in re.finditer(r"`([^`]+)`", body):
        target = match.group(1)
        if target.startswith(("/", "~", "skills/")):
            continue
        if target.startswith(("scripts/", "references/", "routing/", "domain_guidance/")) or target in {
            "style_guidelines.md",
            "API_QUICK_START.md",
            "charts.md",
        }:
            if not (path.parent / target).exists():
                add(errors, path, f"missing linked resource {target}")


def check_file(path: Path, errors: list[str]) -> None:
    body = read_text(path)
    if count_fences(body) % 2:
        add(errors, path, "unbalanced code fences")
    if active_file(path) and path != Path(__file__).resolve():
        for stale in STALE_PATTERNS:
            if stale in body:
                add(errors, path, f"stale machine-local path {stale!r}")
    if active_file(path) and "/references/" in path.as_posix():
        if len(body.splitlines()) > MAX_ACTIVE_REFERENCE_LINES:
            add(errors, path, f"active reference exceeds {MAX_ACTIVE_REFERENCE_LINES} lines")


def check_active_tree(errors: list[str]) -> None:
    for path in sorted(ROOT.glob("**/*")):
        if path.is_dir() and path.name in DISALLOWED_ACTIVE_DIRS:
            add(errors, path, "move examples, research code, and generated artifacts outside installable skills")
        if path.is_file() and path.name in DISALLOWED_ACTIVE_FILES:
            add(errors, path, "move development notes to reference-material, not installable skills")


def main() -> int:
    errors: list[str] = []
    check_active_tree(errors)
    for path in sorted(ROOT.glob("**/SKILL.md")):
        check_skill(path, errors)
    for path in sorted(ROOT.glob("**/*")):
        if path.is_file() and path.suffix.lower() in {".md", ".txt", ".json", ".py"}:
            check_file(path, errors)

    if errors:
        print("Excel skill validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Excel skill validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
