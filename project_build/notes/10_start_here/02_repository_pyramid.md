# Repository Pyramid

The root `README.md` is the single entry point. This file is a lower-level map for humans or LLMs that need to understand where supporting material lives without reading every branch.

## Start Here

1. [`../../../README.md`](../../../README.md) - project goal, demo story, setup, and run commands.
2. [`../../../project_build/README.md`](../../../project_build/README.md) - runnable app, tests, data, runtime skills, and build config.
3. [`../../../spec_files/00_README_SPEC_INDEX.md`](../../../spec_files/00_README_SPEC_INDEX.md) - canonical product, architecture, contracts, quality, and submission specs.
4. [`../../../submission/README.md`](../../../submission/README.md) - Kaggle writeup and video package.
5. [`../../../assignment_details/README.md`](../../../assignment_details/README.md) - course, codelab, and capstone reference library.

## Root Branches

```text
README.md             # Start here
AGENTS.md             # Always-on coding-agent instructions
project_build/        # Runnable capstone implementation (includes these build notes)
spec_files/           # Canonical specs
submission/           # Public-facing Kaggle package
assignment_details/   # Course/codelab/capstone reference material and archive
.agents/              # Project-local helper skills
```

## Runnable Project Branch

Commands run from `project_build/`:

```text
project_build/
|-- portfolio_agent/          # Application package and ADK root agent
|-- tests/                    # Unit, integration, golden, and eval tests
|-- data/                     # Synthetic portfolio datasets
|-- skills/                   # Runtime Agent Skills
|-- artifacts/                # Gate results, eval traces, and build evidence
|-- outputs/                  # Generated demo reports and traces
|-- .agents-cli-spec.md       # Agents CLI source spec
|-- agents-cli-manifest.yaml  # Agents CLI project manifest
|-- pyproject.toml / uv.lock  # Python project and dependency lock
`-- Makefile / Dockerfile     # Local commands and container packaging
```

## Support Branches

```text
spec_files/                   # Numbered canonical specs
submission/                   # Kaggle submission package
project_build/notes/          # This project's own working notes, summaries, and maps
assignment_details/whitepapers/
                              # Course whitepapers: overview + source text/PDFs
assignment_details/codelabs/
                              # Course codelabs: overview + specs, instructions, runnable projects
assignment_details/capstone_project/
                              # Capstone assignment: overview + source text/PDFs
assignment_details/90_archive/
                              # Superseded packages and local caches
```

## Context Budget Rules

- Always read `README.md` first.
- Open `project_build/` when running or changing code.
- Open `spec_files/` when changing product behavior, architecture, contracts, quality gates, or submission claims.
- Open `project_build/notes/20_summaries/` before `project_build/notes/30_full_notes/`.
- Open the relevant `assignment_details/<topic>/README.md` before its `details/` subfolder.
- Treat `project_build/outputs/`, `project_build/artifacts/`, and `assignment_details/90_archive/` as evidence or archive branches, not primary instructions.
