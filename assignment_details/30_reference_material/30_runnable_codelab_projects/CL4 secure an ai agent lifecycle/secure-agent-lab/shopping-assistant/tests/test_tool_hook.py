"""Tests for the local agent command gate."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / ".agents/scripts/validate_tool_call.py"
SPEC = spec_from_file_location("validate_tool_call", SCRIPT)
assert SPEC and SPEC.loader
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_hook_allows_safe_development_command() -> None:
    approved, _ = MODULE.validate("uv run pytest tests/test_agent.py")
    assert approved is True


def test_hook_blocks_recursive_root_deletion() -> None:
    approved, _ = MODULE.validate("rm -rf /")
    assert approved is False


def test_hook_blocks_chained_destructive_command() -> None:
    approved, _ = MODULE.validate("echo ok; mkfs.ext4 /dev/sda")
    assert approved is False
