# Reference Material

This is the course and codelab reference pyramid for the Kaggle capstone. It exists so reviewers and coding agents can answer targeted questions about the assignment without loading every source document or copied codelab.

For the shortest assignment overview, start one level up at [`../README.md`](../README.md). Stay on this page when you need to know what is inside the reference library and how deep to go.

## What This Library Establishes

The assignment expects a real agent project, not a script wrapped in a writeup. The course examples make the expected baseline visible:

- define the problem, user value, agent role, architecture, and reproducible run path;
- use tools for bounded deterministic work and reserve the LLM for routing, judgment, or synthesis;
- include security controls for untrusted inputs, secrets, file paths, and sensitive actions;
- include tests, local evals, traces, or other evidence that behavior can be inspected;
- document a deployment or packaging path even when the final demo runs locally;
- tell the same story across README, specs, code, video, and writeup.

For the Actuarial Portfolio Monitoring Agent, the reference standard is: safe synthetic data loading, deterministic actuarial metrics, documented anomaly thresholds, driver decomposition, conservative LLM memo drafting, prompt-injection/path-traversal controls, markdown report output, structured traces, and tests/evals across normal, anomaly, malformed-data, and security cases.

## Course And Example Depth

The course covered five layers of agent engineering:

| Layer | Reference depth |
|---|---|
| Vibe coding and context engineering | Intent-driven development, context harnesses, and review loops. |
| Agent tools and interoperability | MCP, A2A, A2UI, commerce protocols, and structured tool use. |
| Agent skills | Portable `SKILL.md`-centered context bundles and progressive disclosure. |
| Security and evaluation | Human gates, prompt-injection defenses, threat scans, local evals, and trajectory evidence. |
| Production readiness | Spec-driven development, deployability, Cloud Run, Agent Runtime, frontends, and observability. |

The runnable codelabs reached implementation-level detail: ADK agents, FastAPI surfaces, scheduled/event-driven workflows, policy checks, test suites, Terraform deployment scaffolds, Pub/Sub-style flows, and frontend integration. Use those examples as a quality floor when judging whether the capstone is sufficiently agentic and reviewable.

## Start Here

1. [`10_extracted_guides/README.md`](10_extracted_guides/README.md) - read order for the compact guide layer.
2. [`10_extracted_guides/00_capstone_baseline_expectations.md`](10_extracted_guides/00_capstone_baseline_expectations.md) - minimum expected capstone quality bar.
3. [`10_extracted_guides/01_course_concepts.md`](10_extracted_guides/01_course_concepts.md) - what the course covered.
4. [`10_extracted_guides/02_codelab_lessons.md`](10_extracted_guides/02_codelab_lessons.md) - what the codelabs taught and what this project reused.
5. [`10_extracted_guides/03_submission_requirements.md`](10_extracted_guides/03_submission_requirements.md) - what Kaggle expects for the final submission.
6. [`20_searchable_reference_texts/SUMMARY_INDEX.md`](20_searchable_reference_texts/SUMMARY_INDEX.md) - router into extracted source material.
7. [`30_runnable_codelab_projects/README.md`](30_runnable_codelab_projects/README.md) - runnable codelab copies and implementation specs.

## When To Drill Down

| Task | Smallest useful source |
|---|---|
| Understand the capstone quality bar | `10_extracted_guides/00_capstone_baseline_expectations.md` |
| Check course concept coverage | `10_extracted_guides/01_course_concepts.md` |
| Compare against codelab implementation level | `10_extracted_guides/02_codelab_lessons.md` |
| Confirm submission mechanics | `10_extracted_guides/03_submission_requirements.md` |
| Find original capstone wording, rules, or timeline | `20_searchable_reference_texts/capstone/` |
| Adapt an implementation pattern from a codelab | `20_searchable_reference_texts/implementation_specs/` |
| Inspect actual copied codelab code | `30_runnable_codelab_projects/` |
| Verify formatting, images, or extraction fidelity | `90_source_documents/` |

## Directory Map

```text
assignment_details/30_reference_material/
|-- 10_extracted_guides/           # Human-readable course and submission summaries
|-- 20_searchable_reference_texts/ # Searchable extracted text for targeted retrieval
|-- 30_runnable_codelab_projects/  # Runnable codelab workspaces and lab originals
`-- 90_source_documents/           # PDF and rich-text originals
```

## LLM Retrieval Order

1. Start with `../README.md` for assignment context.
2. Read `10_extracted_guides/00_capstone_baseline_expectations.md` if judging readiness.
3. Read only the relevant guide from `10_extracted_guides/` for course, codelab, or submission questions.
4. For code or architecture work, read `20_searchable_reference_texts/implementation_specs/README.md`.
5. Read the relevant implementation spec.
6. Inspect only the source files named by that spec.
7. Use `20_searchable_reference_texts/SUMMARY_INDEX.md` for supporting course material.
8. Open originals in `90_source_documents/` only when formatting or images matter.

## Search Guidance

Prefer `20_searchable_reference_texts/` for conceptual searches and `30_runnable_codelab_projects/` for code searches. Exclude generated or dependency directories:

```bash
rg "search term" "assignment_details/30_reference_material/20_searchable_reference_texts"
rg "search term" "assignment_details/30_reference_material/30_runnable_codelab_projects" \
  -g '!**/.venv/**' -g '!**/__pycache__/**' \
  -g '!**/.pytest_cache/**' -g '!**/.ruff_cache/**'
```
