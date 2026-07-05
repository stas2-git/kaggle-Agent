"""Local structure checks for the generated Agent Runtime wrapper."""

import os

import vertexai
from google.auth.credentials import AnonymousCredentials

# AdkApp resolves a project during construction. These non-deploying placeholders
# let the module be inspected offline; no client method is invoked by these tests.
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "local-test-project")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
vertexai.init(
    project="local-test-project",
    location="global",
    credentials=AnonymousCredentials(),
)

from app.agent import app  # noqa: E402
from app.agent_runtime_app import AgentEngineApp, agent_runtime  # noqa: E402


def test_runtime_wrapper_reuses_core_adk_app() -> None:
    assert isinstance(agent_runtime, AgentEngineApp)
    assert agent_runtime._tmpl_attrs["app"] is app


def test_runtime_wrapper_registers_feedback_operation() -> None:
    operations = agent_runtime.register_operations()
    assert "register_feedback" in operations[""]
