#!/usr/bin/env python3
"""Validate the portable SQL skill package without external dependencies."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
MAX_SKILL_LINES = 180
MAX_REFERENCE_LINES = 900
ALLOWED_NAME_FOLDER_MISMATCH = {
    ("sql-skills", "sql-router"),
}
DISALLOWED_ACTIVE_FILES = {
    "README.md",
    "FUTURE_IMPROVEMENTS.md",
    "GAME_PLAN.md",
    "RELATION_TO_OLDER_SKILL.md",
    "web-examples.md",
}
DISALLOWED_ACTIVE_DIRS = {
    "__pycache__",
    ".git",
    "examples",
    "example_codes",
}
STALE_PATTERNS = (
    "sql/skills/",
    "sql/skills/SKILL.md",
    "sql/skills/actuarial-sql",
    "sql/skills/odbc-connector",
)
GENERATED_LOCAL_FILES = {
    "config.json",
    "query_log.jsonl",
}


def rel(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def add(errors: list[str], path: Path, message: str) -> None:
    errors.append(f"{rel(path)}: {message}")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def count_fences(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.startswith("```"))


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
    text = read_text(path)
    name, _ = parse_frontmatter(path, errors)
    folder = path.parent.name
    if name and folder != name and (folder, name) not in ALLOWED_NAME_FOLDER_MISMATCH:
        add(errors, path, f"skill folder {folder!r} does not match name {name!r}")
    if len(text.splitlines()) > MAX_SKILL_LINES:
        add(errors, path, f"SKILL.md exceeds {MAX_SKILL_LINES} lines")
    if "## Evaluation Prompts" not in text:
        add(errors, path, "missing ## Evaluation Prompts")
    if count_fences(text) % 2:
        add(errors, path, "unbalanced code fences")

    for match in re.finditer(r"`([^`]+)`", text):
        target = match.group(1)
        if target.startswith(("/", "~")):
            continue
        if target in GENERATED_LOCAL_FILES:
            continue
        if target.endswith((".md", ".py", ".json")) and "/" not in target:
            if not (path.parent / target).exists() and not list(ROOT.glob(f"**/{target}")):
                add(errors, path, f"missing linked resource {target}")


def check_file(path: Path, errors: list[str]) -> None:
    text = read_text(path)
    if count_fences(text) % 2:
        add(errors, path, "unbalanced code fences")
    if path.name != "validate_sql_skills.py":
        for stale in STALE_PATTERNS:
            if stale in text:
                add(errors, path, f"stale package path {stale!r}")
    if path.suffix.lower() in {".md", ".txt"} and len(text.splitlines()) > MAX_REFERENCE_LINES:
        add(errors, path, f"reference exceeds {MAX_REFERENCE_LINES} lines")


def check_active_tree(errors: list[str]) -> None:
    for path in sorted(ROOT.glob("**/*")):
        if path.is_dir() and path.name in DISALLOWED_ACTIVE_DIRS:
            add(errors, path, "move examples, cloned repos, or generated artifacts outside installable skills")
        if path.is_file() and path.name in DISALLOWED_ACTIVE_FILES:
            add(errors, path, "move package docs or development notes outside installable skills")


def main() -> int:
    errors: list[str] = []
    check_active_tree(errors)
    for path in sorted(ROOT.glob("**/SKILL.md")):
        check_skill(path, errors)
    for path in sorted(ROOT.glob("**/*")):
        if path.is_file() and path.suffix.lower() in {".md", ".txt", ".json", ".py"}:
            check_file(path, errors)

    if errors:
        print("SQL skill validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("SQL skill validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
