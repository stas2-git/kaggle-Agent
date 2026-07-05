"""Fail-closed validator for Antigravity run_command tool calls."""

from __future__ import annotations

import json
import re
import sys

_DESTRUCTIVE_PATTERNS = (
    re.compile(r"(?:^|[;&|]\s*)rm\s+-(?:r\w*f|f\w*r)\s+/(?:\s|$)"),
    re.compile(r"(?:^|[;&|]\s*)mkfs(?:\.\w+)?(?:\s|$)"),
    re.compile(r"\bdd\b.*\bof=/dev/"),
    re.compile(r"(?:^|[;&|]\s*)(?:shutdown|reboot|halt)(?:\s|$)"),
    re.compile(r":\(\)\s*\{\s*:\|:\s*&\s*\}\s*;\s*:"),
)


def validate(command: str) -> tuple[bool, str]:
    normalized = " ".join(command.strip().split())
    if not normalized:
        return False, "Empty command"
    if any(pattern.search(normalized) for pattern in _DESTRUCTIVE_PATTERNS):
        return False, "Destructive command detected"
    return True, "Command validation passed"


def main() -> int:
    try:
        context = json.load(sys.stdin)
        tool_args = context.get("tool_args", {})
        command = tool_args.get("CommandLine") or tool_args.get("command") or ""
        approved, message = validate(command)
    except (json.JSONDecodeError, AttributeError, TypeError) as exc:
        print(f"BLOCKED: Invalid hook input: {exc}", file=sys.stderr)
        return 1

    stream = sys.stdout if approved else sys.stderr
    print(f"{'APPROVED' if approved else 'BLOCKED'}: {message}", file=stream)
    return 0 if approved else 1


if __name__ == "__main__":
    raise SystemExit(main())
