#!/usr/bin/env python3
"""Validate the portable agent skill library without external dependencies."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
MAX_SKILL_LINES = 120
MAX_REFERENCE_LINES = 900
STALE_PATHS = (
    "agent/SKILL.md",
    "agent/coding-agent-workflow",
    "agent/scripts/validate_agent_skills.py",
    "agent/skills/",
    "agent/skills/core-methods",
    "agent/skills/self-improvement",
    "core-methods/",
    "self-improvement/",
)
DISALLOWED_ACTIVE_FILES = {
    "README.md",
    "FUTURE_IMPROVEMENTS.md",
    "GAME_PLAN.md",
    "RELATION_TO_OLDER_SKILL.md",
    "web-examples.md",
}


def fail(errors: list[str], path: Path, message: str) -> None:
    errors.append(f"{path.relative_to(ROOT)}: {message}")


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def code_fence_count(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.startswith("```"))


def parse_frontmatter(path: Path, errors: list[str]) -> tuple[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 4 or lines[0] != "---":
        fail(errors, path, "missing YAML frontmatter")
        return "", ""
    try:
        end = lines.index("---", 1)
    except ValueError:
        fail(errors, path, "frontmatter is not closed")
        return "", ""

    fields: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            fail(errors, path, f"invalid frontmatter line: {line}")
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()

    name = fields.get("name", "")
    description = fields.get("description", "")
    if not name:
        fail(errors, path, "missing name")
    if not description:
        fail(errors, path, "missing description")
    if description and "Use " not in description:
        fail(errors, path, "description should include a Use/Use when trigger")
    return name, description


def check_skill(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    name, _ = parse_frontmatter(path, errors)

    if path != ROOT / "SKILL.md" and name and path.parent.name != name:
        fail(errors, path, f"skill folder should match name {name!r}")

    if line_count(path) > MAX_SKILL_LINES:
        fail(errors, path, f"SKILL.md exceeds {MAX_SKILL_LINES} lines")

    if path != ROOT / "SKILL.md" and "## Evaluation Prompts" not in text:
        fail(errors, path, "missing ## Evaluation Prompts")

    if code_fence_count(text) % 2:
        fail(errors, path, "unbalanced code fences")

    for match in re.finditer(r"`(references/[^`]+)`", text):
        ref = path.parent / match.group(1)
        if not ref.exists():
            fail(errors, path, f"missing referenced file {match.group(1)}")


def check_text_file(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    if code_fence_count(text) % 2:
        fail(errors, path, "unbalanced code fences")
    if line_count(path) > MAX_REFERENCE_LINES:
        fail(errors, path, f"reference exceeds {MAX_REFERENCE_LINES} lines")


def check_stale_paths(errors: list[str]) -> None:
    for path in [ROOT / "SKILL.md", REPO / "README.md", REPO / "AGENTS.md"]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for stale in STALE_PATHS:
            if stale in text:
                fail(errors, path, f"stale path/group reference {stale!r}")


def check_active_tree(errors: list[str]) -> None:
    for path in sorted(ROOT.glob("**/*")):
        if path.is_file() and path.name in DISALLOWED_ACTIVE_FILES:
            fail(errors, path, "move package docs or development notes outside installable skills")


def main() -> int:
    errors: list[str] = []

    check_active_tree(errors)

    for path in sorted(ROOT.glob("**/SKILL.md")):
        check_skill(path, errors)

    for path in sorted(ROOT.glob("**/*")):
        if path.is_file() and path.suffix.lower() in {".md", ".txt"}:
            check_text_file(path, errors)

    check_stale_paths(errors)

    if errors:
        print("Agent skill validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Agent skill validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
