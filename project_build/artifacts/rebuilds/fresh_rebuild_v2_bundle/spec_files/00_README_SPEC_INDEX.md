# Capstone Spec Package: Actuarial Portfolio Monitoring Agent

Prepared: 2026-06-20
Current spec version: 0.2
Agents CLI source of truth: `../project_build/.agents-cli-spec.md`

This package defines the product, architecture, contracts, quality gates, and submission story for the **Actuarial Portfolio Monitoring Agent**, an Agents for Business capstone project.

The project monitors a synthetic insurance portfolio, calculates deterministic metrics, detects material movement, investigates likely drivers, and produces an actuary-ready review memo with traceable evidence and advisory human-review status.

## Reader Path

For a reviewer or AI judge, read in this order:

1. `00_README_SPEC_INDEX.md` - package map and reviewer path.
2. `10_core/01_product_requirements.md` - what the product must do.
3. `10_core/02_agent_architecture.md` - how the agent, tools, skill, safety controls, and outputs fit together.
4. `20_contracts/01_data_spec_and_schemas.md` and `20_contracts/02_tool_contracts.yaml` - the deterministic implementation boundary.
5. `30_quality/01_security_privacy_spec.md` and `30_quality/03_evaluation_spec.yaml` - how behavior, safety, and correctness are verified.
6. `40_submission/01_capstone_submission_strategy.md`, `40_submission/02_kaggle_writeup_draft.md`, and `40_submission/03_demo_video_script.md` - the public submission narrative.

The implementation support files are useful for coding agents, but they are not the primary reviewer story.

## One-Sentence Pitch

An agentic workflow that reads a synthetic insurance portfolio extract, calculates key monitoring metrics, detects unusual trend changes, investigates drivers, and generates a concise actuarial review memo with flagged exceptions and recommended follow-up questions.

## Spec Pyramid

```text
spec_files/
|-- 00_README_SPEC_INDEX.md          # Start here
|-- 10_core/                         # Product intent and architecture
|-- 20_contracts/                    # Data, tool, behavior, and report contracts
|-- 30_quality/                      # Security, evaluation, observability, risks, readiness
|-- 40_submission/                   # Kaggle writeup, demo, deployment, reproducibility
|-- 50_implementation/               # Build governance, backlog, ADK alignment, agent instructions
|-- 60_skills/                       # Portfolio-monitoring Agent Skill package
`-- 90_archive/                      # Notes on removed superseded artifacts
```

Branch numbers intentionally leave gaps. Add future product/contract/quality/submission material inside the matching branch without renumbering the whole package.

## Canonical Files

### Core

| File | Purpose |
|---|---|
| `10_core/01_product_requirements.md` | Product requirements, users, goals, MVP, non-goals, and success metrics. |
| `10_core/02_agent_architecture.md` | Agent workflow, deterministic boundaries, ADK responsibilities, data flow, and output contract. |

### Contracts

| File | Purpose |
|---|---|
| `20_contracts/01_data_spec_and_schemas.md` | Synthetic dataset design, columns, validation rules, metrics, and result schemas. |
| `20_contracts/02_tool_contracts.yaml` | Machine-readable tool contracts, permissions, inputs, outputs, and safety rules. |
| `20_contracts/03_behavior_spec.feature` | BDD scenarios for expected portfolio-monitoring behavior. |
| `20_contracts/04_output_report_template.md` | Expected final monthly review report format. |

### Quality

| File | Purpose |
|---|---|
| `30_quality/01_security_privacy_spec.md` | Security and privacy controls, prompt-injection handling, and human-review terminology. |
| `30_quality/02_threat_model_stride.md` | STRIDE threat model and mitigations. |
| `30_quality/03_evaluation_spec.yaml` | Evaluation cases, judge criteria, metrics, pass thresholds, and Agents CLI eval expectations. |
| `30_quality/04_synthetic_eval_cases.json` | Example evaluation case definitions. |
| `30_quality/05_observability_trace_spec.md` | Trace schema, ADK event preservation, logs, and evaluation trace requirements. |
| `30_quality/06_acceptance_checklist.md` | Final readiness checklist before submission. |
| `30_quality/07_risk_register.md` | Project risks and mitigations. |

### Submission

| File | Purpose |
|---|---|
| `40_submission/01_capstone_submission_strategy.md` | Track, scoring strategy, required assets, and positioning. |
| `40_submission/02_kaggle_writeup_draft.md` | Draft writeup structure under the capstone word limit. |
| `40_submission/03_demo_video_script.md` | Five-minute video structure and narration. |
| `40_submission/04_reproducibility_and_repo_spec.md` | README, setup, command, and public repo requirements. |
| `40_submission/05_deployment_spec.md` | Local-first deployment plan and optional cloud path. |

### Implementation Support

| File | Purpose |
|---|---|
| `50_implementation/01_implementation_backlog.md` | Build milestones and coding-agent prompts. |
| `50_implementation/02_spec_adequacy_and_build_gates.md` | Build governance, gates, golden tests, eval gates, and submission readiness. |
| `50_implementation/03_adk_alignment_notes.md` | Version 0.2 ADK/FastAPI/Agents CLI alignment notes. |
| `50_implementation/04_AGENTS.md` | Candidate project-level coding-agent instructions. |
| `50_implementation/05_CONTEXT.md` | Candidate secure coding context. |

### Skills And Archive

| File | Purpose |
|---|---|
| `60_skills/portfolio_monitoring/` | Agent Skill folder with `SKILL.md`, references, and report template. |
| `90_archive/README.md` | Notes on removed superseded artifacts. |

## Design Principles

- Specs are the source of truth for behavior; code is implementation.
- Deterministic Python tools calculate every numeric portfolio metric.
- ADK coordinates bounded workflow, tool selection, callbacks, sessions, and traces.
- The LLM may synthesize and explain trusted tool outputs, but it may not invent metrics, thresholds, paths, or business actions.
- The core demo must run locally with synthetic data and no credentials.
- Human review is advisory in the MVP; it is not an interactive approval or pause/resume flow.
- Cloud deployment is optional and requires explicit approval.

## Course Concepts Demonstrated

1. Agent workflow with ADK orchestration and deterministic tools.
2. Schema-bound agent tools for loading, validating, calculating, detecting, investigating, and reporting.
3. Agent Skill packaging through `project_build/skills/portfolio_monitoring/`.
4. Security controls: path allowlists, synthetic data, prompt-injection handling, no external side effects, and advisory human-review gates.
5. Evaluation: deterministic tests, trace checks, and Agents CLI generate/grade behavior evaluation.
6. Deployability: local-first CLI/FastAPI structure with optional cloud path.

## Submission-Safe Interpretation

The version 0.2 ADK alignment file is implementation support, not a signal that the capstone is unfinished. The public story should emphasize the stable product architecture:

```text
synthetic portfolio data
  -> deterministic validation and metrics
  -> bounded ADK tool orchestration
  -> driver investigation
  -> grounded actuarial memo
  -> trace, evals, and safety evidence
```

Use verified command output, generated traces, and passing eval artifacts when finalizing the README, writeup, screenshots, and video.
