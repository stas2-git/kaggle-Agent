import os
import re

def validate_file_path(path: str, workspace_root: str) -> str:
    # Handle absolute paths or relative paths
    if os.path.isabs(path):
        abs_path = os.path.abspath(path)
    else:
        abs_path = os.path.abspath(os.path.join(workspace_root, path))
        
    abs_workspace = os.path.abspath(workspace_root)
    
    # Check if the resolved path starts with the workspace root
    if not abs_path.startswith(abs_workspace):
        raise ValueError(f"Path traversal detected: {path} is outside workspace")
        
    # Get the relative path from the workspace root
    rel_path = os.path.relpath(abs_path, abs_workspace)
    
    # Allowed subdirectories relative to workspace root
    allowed_subdirs = ["data", "examples", "tests/golden"]
    
    is_allowed = False
    for allowed in allowed_subdirs:
        # Check if the relative path is inside the allowed directory
        if rel_path == allowed or rel_path.startswith(allowed + os.sep):
            is_allowed = True
            break
            
    if not is_allowed:
        raise ValueError(f"Path not allowed under security policy: {path}")
        
    return abs_path

def scan_for_prompt_injection(text: str) -> bool:
    if not text or not isinstance(text, str):
        return False
        
    suspicious_patterns = [
        r"ignore\s+previous\s+instructions",
        r"system\s+prompt",
        r"developer\s+message",
        r"reveal\s+secrets",
        r"delete\s+files",
        r"mark\s+this\s+as\s+low\s+risk",
        r"do\s+not\s+tell\s+the\s+user"
    ]
    
    text_lower = text.lower()
    for pattern in suspicious_patterns:
        if re.search(pattern, text_lower):
            return True
            
    return False
