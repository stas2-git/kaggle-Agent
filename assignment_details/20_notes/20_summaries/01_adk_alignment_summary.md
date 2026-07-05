# ADK Alignment Summary

The long ADK plan records how the project moved from a local actuarial workflow toward a recognizable ADK/Agents CLI capstone shape. This summary is the version to read first.

## Goal

Preserve the working actuarial engine while making the agent structure visible to reviewers:

- ADK `root_agent` exists and is importable.
- Deterministic actuarial calculations remain in bounded tools.
- LLM behavior is limited to synthesis over trusted tool output.
- Security callbacks and trace events make tool use inspectable.
- Offline mode keeps the demo reproducible without credentials.
- CLI, FastAPI, Docker, Makefile, and Agents CLI metadata describe one coherent project.
- Pytest and Agents CLI evals show behavior, not just claims.

## Phase Summary

| Area | Purpose |
|---|---|
| Baseline protection | Record known-good tests and avoid losing the pre-ADK behavior. |
| Agents CLI structure | Make the repository recognizable without replacing domain logic. |
| Offline mode | Ensure reviewers can run the project without API keys. |
| Runtime skill | Move reusable portfolio-monitoring knowledge into a skill boundary. |
| ADK tool adapters | Expose deterministic calculations through JSON-safe interfaces. |
| Callbacks and tracing | Capture security, model, and tool events for auditability. |
| Root agent and service | Route agent, CLI, and API through shared behavior. |
| Packaging | Provide Makefile, Dockerfile, manifest, and dependency support. |
| Evals | Add agent-quality checks separate from deterministic unit tests. |
| Submission reconciliation | Update README, writeup, video, and gate artifacts only after verification. |

## Current Interpretation

For submission review, the important story is not that every optional cloud feature is deployed. The important story is that the local capstone demonstrates a production-minded agent pattern: spec-first design, safe tools, observable traces, reproducible runs, security boundaries, and evaluation evidence.

Full detail: [`../30_full_notes/01_capstone_adk_expansion_plan.md`](../30_full_notes/01_capstone_adk_expansion_plan.md)
