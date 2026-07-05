# Project Build

This folder is the runnable capstone project. Run Python, pytest, Agents CLI, Docker, and local eval commands from here.

## Contents

```text
project_build/
|-- portfolio_agent/          # ADK/Python implementation
|-- tests/                    # Unit, integration, golden, and eval tests
|-- data/                     # Synthetic portfolio datasets
|-- skills/                   # Runtime Agent Skills
|-- artifacts/                # Build gates and evidence
|-- outputs/                  # Generated reports and traces
|-- .agents-cli-spec.md       # Agents CLI source spec
|-- agents-cli-manifest.yaml  # Agents CLI manifest
|-- pyproject.toml            # Python project config
`-- uv.lock                   # Locked dependency graph
```

## Setup

```bash
uv sync
```

## Run

```bash
uv run python3 -m portfolio_agent.run --input "data/synthetic_portfolio_monthly.csv" --latest-month "2026-06" --force-offline
```

## Test

```bash
uv run pytest tests/unit tests/integration
```

## Evaluate

```bash
FORCE_OFFLINE=1 uv run python3 -m tests.eval.run_eval
```

Use [`../spec_files/00_README_SPEC_INDEX.md`](../spec_files/00_README_SPEC_INDEX.md) as the source of truth for product behavior and quality gates.
