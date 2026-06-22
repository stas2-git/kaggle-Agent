# Spec Review v2 — ADK Codelab-Alignment Upgrade

Spec version: 0.2  
Reviewer: Codex  
Date: 2026-06-22  
Decision: PASS FOR IMPLEMENTATION PLANNING

## Scope reviewed

- In-place migration from direct Gemini synthesis/fixed orchestration to Google ADK.
- Preservation of deterministic actuarial calculations and existing tests.
- Active portfolio-monitoring Agent Skill.
- True zero-network offline demo.
- Shared CLI and FastAPI application service.
- ADK callbacks, sessions, events, and trace correlation.
- Separation of pytest correctness from Agents CLI behavioral evaluation.
- Packaging and governance aligned with the four completed codelabs.

## Blocking ambiguities

None for the specification phase.

The installed Agents CLI and ADK versions must be inspected before implementation. Scaffold-generated files must be reviewed before replacing existing configuration. These are implementation checks, not missing product decisions.

## Non-blocking assumptions

- Preserve the existing `gemini-2.5-flash` model until the user requests a change.
- Use `portfolio_agent` as both application and agent-directory name.
- Keep the core demo local and credential-free.
- Treat human review as advisory because the MVP has no consequential external action.
- Keep cloud deployment, ambient triggers, and a manager dashboard optional.
- Add FastAPI as an API adapter first; a visual UI is not required for Gate 7.

## Required implementation order

1. Reconcile existing documentation with executable behavior.
2. Inspect/enhance Agents CLI structure.
3. Implement and test offline isolation.
4. Activate the runtime skill.
5. Add ADK tool adapters and callbacks.
6. Add `root_agent`, App, and shared application service.
7. Add CLI and FastAPI adapters.
8. Add ADK eval datasets/config and complete the quality flywheel.
9. Regenerate submission assets from verified evidence.

## Acceptance-test coverage

The updated specifications cover:

- ADK import/discovery and app naming;
- deterministic numerical provenance;
- clean/anomalous routing behavior;
- function-call/function-response correlation;
- callback policy enforcement;
- offline model/network isolation;
- CLI/FastAPI parity;
- human-review terminology;
- pytest versus Agents CLI eval responsibilities;
- deployment authorization boundaries; and
- documentation truthfulness.

## Files changed

- `.agents-cli-spec.md`
- `capstone_spec_files/00_README_SPEC_INDEX.md`
- `capstone_spec_files/02_product_requirements.md`
- `capstone_spec_files/03_agent_architecture.md`
- `capstone_spec_files/04_data_spec_and_schemas.md`
- `capstone_spec_files/05_tool_contracts.yaml`
- `capstone_spec_files/06_behavior_spec.feature`
- `capstone_spec_files/07_security_privacy_spec.md`
- `capstone_spec_files/08_threat_model_stride.md`
- `capstone_spec_files/09_evaluation_spec.yaml`
- `capstone_spec_files/10_observability_trace_spec.md`
- `capstone_spec_files/11_skill_portfolio_monitoring/SKILL.md`
- `capstone_spec_files/12_deployment_spec.md`
- `capstone_spec_files/15_implementation_backlog.md`
- `capstone_spec_files/16_acceptance_checklist.md`
- `capstone_spec_files/17_AGENTS.md`
- `capstone_spec_files/19_reproducibility_and_repo_spec.md`
- `capstone_spec_files/23_spec_adequacy_and_build_gates.md`
- `capstone_spec_files/24_codelab_alignment_upgrade.md`

`ALL_SPECS_COMBINED.md` is explicitly archived at version 0.1 to prevent stale compiled content from overriding the canonical version 0.2 files.

## Implementation authorization boundary

This review approves moving to the plan-only implementation gate. It does not authorize cloud deployment, API enablement, IAM changes, publication, or infrastructure application.
