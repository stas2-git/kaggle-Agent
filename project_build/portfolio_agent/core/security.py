import os
import re
from pathlib import Path

# Approved base directories relative to the workspace root
ALLOWED_SUBDIRS = ["data", "examples", "tests/golden"]

# Keywords indicative of prompt injection or system instruction overrides
INJECTION_KEYWORDS = [
    r"ignore\s+previous\s+instructions",
    r"ignore\s+system\s+rules",
    r"override\s+system",
    r"you\s+are\s+now",
    r"system\s+prompt",
    r"mark\s+as\s+low\s+risk",
    r"ignore\s+rules",
    r"bypass\s+check",
]


class SecurityError(Exception):
    """Raised when security validation fails."""

    pass


def validate_file_path(file_path: str, workspace_root: str = None) -> Path:
    """
    Validate that file_path resides strictly within approved subdirectories.
    Fails if the resolved absolute path goes outside.
    """
    if workspace_root is None:
        # Default to current directory if not specified
        workspace_root = os.getcwd()

    workspace_path = Path(workspace_root).resolve()
    target_path = Path(file_path).resolve()

    # Verify that the target starts with the workspace root to prevent system-wide traversal
    if not str(target_path).startswith(str(workspace_path)):
        raise SecurityError(
            f"Access Denied: Path traversal detected outside workspace for {file_path}"
        )

    # Verify it lies inside one of the allowed subdirectories
    is_allowed = False
    for subdir in ALLOWED_SUBDIRS:
        allowed_dir = (workspace_path / subdir).resolve()
        if str(target_path).startswith(str(allowed_dir)):
            is_allowed = True
            break

    if not is_allowed:
        raise SecurityError(
            f"Access Denied: Path '{file_path}' must reside under one of the allowed folders: {ALLOWED_SUBDIRS}"
        )

    return target_path


def scan_text_for_injection(text: str) -> bool:
    """
    Scan a string (e.g. text from notes column) for known prompt injection signatures.
    Returns True if suspicious text is found, False otherwise.
    """
    if not text or not isinstance(text, str):
        return False

    for pattern in INJECTION_KEYWORDS:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False
