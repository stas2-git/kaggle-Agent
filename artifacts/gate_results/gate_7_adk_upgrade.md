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
