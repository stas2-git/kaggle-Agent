"""Path allowlisting and prompt-injection screening.

Per spec_files/20_contracts/02_tool_contracts.yaml (`load_portfolio_data.allowed_paths`,
`generate_report.allowed_paths`, `write_trace.allowed_paths`) and
spec_files/20_contracts/01_data_spec_and_schemas.md ("Prompt-injection fields").
"""

from __future__ import annotations

import os

from .schemas import ALLOWED_INPUT_DIRS, ALLOWED_REPORT_DIR, ALLOWED_TRACE_DIR, PROMPT_INJECTION_PATTERNS


class PathNotAllowedError(Exception):
    pass


def _is_within(path: str, workspace_root: str, allowed_subdirs: list[str]) -> bool:
    abs_path = os.path.realpath(os.path.join(workspace_root, path) if not os.path.isabs(path) else path)
    for sub in allowed_subdirs:
        allowed_abs = os.path.realpath(os.path.join(workspace_root, sub))
        if abs_path == allowed_abs or abs_path.startswith(allowed_abs + os.sep):
            return True
    return False


def validate_input_path(path: str, workspace_root: str) -> str:
    """Raise PathNotAllowedError if `path` is not under an approved input directory."""
    if not _is_within(path, workspace_root, ALLOWED_INPUT_DIRS):
        raise PathNotAllowedError(
            f"path_not_allowed: '{path}' is outside approved input directories {ALLOWED_INPUT_DIRS}"
        )
    return path


def validate_report_path(path: str, workspace_root: str) -> str:
    if not _is_within(path, workspace_root, [ALLOWED_REPORT_DIR]):
        raise PathNotAllowedError(f"output_path_not_allowed: '{path}' is outside {ALLOWED_REPORT_DIR}")
    return path


def validate_trace_path(path: str, workspace_root: str) -> str:
    if not _is_within(path, workspace_root, [ALLOWED_TRACE_DIR]):
        raise PathNotAllowedError(f"output_path_not_allowed: '{path}' is outside {ALLOWED_TRACE_DIR}")
    return path


def scan_for_prompt_injection(text: str) -> list[str]:
    """Return the list of injection-like patterns matched inside `text`.

    This is a deterministic, non-LLM screen: the agent must not obey instructions
    found in untrusted data fields such as `notes` (data spec, "Prompt-injection fields").
    """
    if not text:
        return []
    lowered = str(text).lower()
    return [p for p in PROMPT_INJECTION_PATTERNS if p in lowered]
