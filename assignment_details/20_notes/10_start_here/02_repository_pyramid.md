# Repository Pyramid

The root `README.md` is the single entry point. This file is a lower-level map for humans or LLMs that need to understand where supporting material lives without reading every branch.

## Start Here

1. [`../../../README.md`](../../../README.md) - project goal, demo story, setup, and run commands.
2. [`../../../project_build/README.md`](../../../project_build/README.md) - runnable app, tests, data, runtime skills, and build config.
3. [`../../../spec_files/00_README_SPEC_INDEX.md`](../../../spec_files/00_README_SPEC_INDEX.md) - canonical product, architecture, contracts, quality, and submission specs.
4. [`../../../submission/README.md`](../../../submission/README.md) - Kaggle writeup and video package.
5. [`../../30_reference_material/README.md`](../../30_reference_material/README.md) - course, codelab, and source reference library.

## Root Branches

```text
README.md             # Start here
AGENTS.md             # Always-on coding-agent instructions
project_build/        # Runnable capstone implementation
spec_files/           # Canonical specs
submission/           # Public-facing Kaggle package
assignment_details/   # Notes, course references, and archive
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
assignment_details/20_notes/  # Working notes, summaries, and maps
assignment_details/30_reference_material/
                              # Course/codelab/source references
assignment_details/90_archive/
                              # Superseded packages and local caches
```

## Context Budget Rules

- Always read `README.md` first.
- Open `project_build/` when running or changing code.
- Open `spec_files/` when changing product behavior, architecture, contracts, quality gates, or submission claims.
- Open `assignment_details/20_notes/20_summaries/` before `assignment_details/20_notes/30_full_notes/`.
- Open `assignment_details/30_reference_material/10_extracted_guides/` before raw course/codelab files.
- Treat `project_build/outputs/`, `project_build/artifacts/`, and `assignment_details/90_archive/` as evidence or archive branches, not primary instructions.
