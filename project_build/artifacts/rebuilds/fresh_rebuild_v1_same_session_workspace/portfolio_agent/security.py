import os
import re
from pathlib import Path

ALLOWED_SUBDIRS = ["data", "examples", "tests/golden"]

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
    pass

def validate_file_path(file_path: str, workspace_root: str = None) -> Path:
    if workspace_root is None:
        workspace_root = os.getcwd()
    
    workspace_path = Path(workspace_root).resolve()
    target_path = Path(file_path).resolve()
    
    # Check traversal
    if not str(target_path).startswith(str(workspace_path)):
        raise SecurityError(f"Access Denied: Path traversal detected outside workspace for {file_path}")
        
    is_allowed = False
    for subdir in ALLOWED_SUBDIRS:
        allowed_dir = (workspace_path / subdir).resolve()
        if str(target_path).startswith(str(allowed_dir)):
            is_allowed = True
            break
            
    if not is_allowed:
        raise SecurityError(f"Access Denied: Path '{file_path}' must reside under one of the allowed folders: {ALLOWED_SUBDIRS}")
        
    return target_path

def scan_text_for_injection(text: str) -> bool:
    if not text or not isinstance(text, str):
        return False
    for pattern in INJECTION_KEYWORDS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False
