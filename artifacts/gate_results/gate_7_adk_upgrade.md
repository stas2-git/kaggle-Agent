# Gate 7 — ADK Codelab-Alignment Upgrade

## Phase 0: Protected working baseline

Date: 2026-06-22  
Branch: `main`  
Specification baseline commit: `2de040a6139eef2b172ea2e46d601595b17315ee`  
Checkpoint tag: `gate7-baseline-v0.2`  
Decision: PASS

## Scope

This phase records the known-good state before Agents CLI scaffolding or application-code changes. It does not deploy, publish, enable APIs, alter IAM, or modify infrastructure.

## Worktree review

Before creating this evidence, `git status --short` contained only:

```text
?? docs/CAPSTONE_ADK_EXPANSION_PLAN.md
```

The updated version 0.2 specifications were already present in the baseline commit, including:

```text
.agents-cli-spec.md
capstone_spec_files/24_codelab_alignment_upgrade.md
artifacts/spec_reviews/spec_review_v2_adk_upgrade.md
```

No unrelated project, video, natural-voice, model-asset, or reference-material changes were included in the Phase 0 checkpoint.

## Tool versions

```text
uv 0.11.21 (Homebrew 2026-06-11 aarch64-apple-darwin)
Python 3.11.15
git version 2.50.1 (Apple Git-155)
Google Agents CLI 0.5.0
macOS 26.5.1 arm64
```

Agents CLI install path:

```text
/Users/stan/.local/share/uv/tools/google-agents-cli/lib/python3.11/site-packages/google/agents/cli
```

## Agents CLI project status

`agents-cli info` reported:

```text
No agent project found in the current directory or any parent.
```

This is expected before Phase 1. Agents CLI is installed, but `agents-cli-manifest.yaml` and the recognized project scaffold do not yet exist.

## Dependency synchronization

Command:

```bash
uv sync
```

Result:

```text
Resolved 45 packages in 3ms
Checked 42 packages in 0.60ms
```

No dependency or lock-file change was produced.

## Baseline tests

Command:

```bash
uv run pytest -q
```

Result:

```text
...............                                                          [100%]
15 passed in 0.16s
```

## Known baseline limitations

- The repository is not yet recognized as an Agents CLI project.
- `portfolio_agent.agent` does not yet export an ADK `root_agent`.
- The root Makefile, Dockerfile, and `agents-cli-manifest.yaml` are not yet present.
- The portfolio-monitoring skill is not yet installed under `skills/portfolio_monitoring/`.
- The documented `--force-offline` behavior is not yet implemented.
- FastAPI, ADK callbacks, ADK tool wrappers, and Agents CLI behavioral evals are not yet implemented.

These are planned Phase 1–10 changes, not Phase 0 failures.

## Gate decision

PASS. The known-good deterministic baseline is reproducible, all 15 tests pass, and the worktree was cleanly separated before structural changes. Phase 1 may begin from tag `gate7-baseline-v0.2`.

---

## Phase 1 attempt: Agents CLI project structure

Date: 2026-06-22  
Decision: STOPPED — test gate failed

## Commands run

Preview scaffold outside the repository:

```bash
rm -rf /tmp/capstone-adk-ref
agents-cli scaffold create capstone-adk-ref \
  --output-dir /tmp \
  --agent adk \
  --prototype \
  --deployment-target none \
  --cicd-runner skip \
  --agent-directory portfolio_agent \
  --agent-guidance-filename AGENTS.md
```

Enhance existing repository:

```bash
agents-cli scaffold enhance . \
  --adk \
  --prototype \
  --deployment-target none \
  --cicd-runner skip \
  --agent-directory portfolio_agent \
  --agent-guidance-filename AGENTS.md
```

Agents CLI recognition check:

```bash
agents-cli info
```

Result:

```text
Project root:       /Users/stan/Library/CloudStorage/GoogleDrive-staskhalitov@gmail.com/My Drive/keggle Agent
Project name:       keggle agent
Deployment target:  none
Agent directory:    portfolio_agent
Region:             us-east1
```

Test gate:

```bash
uv sync && uv run pytest -q
```

Result:

```text
5 errors during collection
```

## Failure details

The generated scaffold introduced test/import expectations before the project has the ADK dependency and expected exports:

```text
ModuleNotFoundError: No module named 'google.adk'
ImportError: cannot import name 'app' from 'portfolio_agent.agent'
```

The failure appeared during collection for:

```text
tests/integration/test_agent.py
tests/test_eval_security.py
tests/test_golden.py
tests/test_security.py
tests/test_tools.py
```

## Generated files present at stop point

```text
AGENTS.md
Dockerfile
agents-cli-manifest.yaml
portfolio_agent/__init__.py
portfolio_agent/app_utils/
portfolio_agent/fast_api_app.py
tests/eval/
tests/integration/
tests/unit/
```

## Additional worktree note

Four reference-material implementation spec links were reported as file-type changes after scaffolding:

```text
T refrence material/codelabs/CL4 ambient agent/ambient-expense-agent/CAPSTONE_IMPLEMENTATION_SPEC.md
T refrence material/codelabs/CL4 secure an ai agent lifecycle/secure-agent-lab/shopping-assistant/CAPSTONE_IMPLEMENTATION_SPEC.md
T refrence material/codelabs/CL5 Deploy an ADK agent to Agent Runtime using Agents CLI/expense-agent/CAPSTONE_IMPLEMENTATION_SPEC.md
T refrence material/codelabs/CL5 Vibecode and Deploy a Frontend for an ADK agent/submission_frontend/CAPSTONE_IMPLEMENTATION_SPEC.md
```

## Stop decision

Per the build rule, work stopped at Phase 1 because the full test suite did not pass. Do not begin Phase 2 until Phase 1 is repaired or the generated scaffold changes are reverted.

---

## Phase 1 rerun: repaired Agents CLI project structure

Date: 2026-06-22  
Decision: PASS

## Spec update

The Phase 1 scope was clarified in:

```text
capstone_spec_files/24_codelab_alignment_upgrade.md
docs/CAPSTONE_ADK_EXPANSION_PLAN.md
```

Clarification: Phase 1 is a structure-recognition phase. Generated scaffold tests or imports that require a completed ADK `root_agent`, live ADK runner, Google Cloud credentials, or FastAPI review API are later-phase material and should be removed or quarantined until Phase 6/8.

## Repairs

- Made `portfolio_agent/__init__.py` side-effect-light so deterministic module imports do not require a not-yet-built ADK app.
- Removed generated placeholder ADK runner/server tests that belonged to later phases:

```text
tests/integration/test_agent.py
tests/integration/test_server_e2e.py
tests/unit/test_dummy.py
```

- Restored reference-material implementation spec links as symlinks after scaffold enhancement dereferenced them.

## Verification

Command:

```bash
agents-cli info && uv sync && uv run pytest -q
```

Result:

```text
Project root:       /Users/stan/Library/CloudStorage/GoogleDrive-staskhalitov@gmail.com/My Drive/keggle Agent
Project name:       keggle agent
Deployment target:  none
Agent directory:    portfolio_agent
Region:             us-east1
Resolved 45 packages in 3ms
Checked 42 packages in 0.69ms
...............                                                          [100%]
15 passed in 0.18s
```

## Phase 1 gate decision

PASS. Agents CLI recognizes the repository, the existing deterministic project behavior is preserved, and the full current test suite passes. Phase 2 may begin after this checkpoint is saved.
