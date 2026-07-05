# Implementation Backlog

## Milestone 0: Repository setup

- [ ] Create public repository.
- [ ] Add README.
- [ ] Add `.gitignore`.
- [ ] Add `.env.example`.
- [ ] Add `pyproject.toml`.
- [ ] Add specs folder.
- [ ] Add `.agents/CONTEXT.md` and `AGENTS.md`.

## Milestone 1: Synthetic data

- [ ] Create `data/synthetic_portfolio_monthly.csv`.
- [ ] Create `data/eval/green_portfolio.csv`.
- [ ] Create `data/eval/loss_ratio_spike.csv`.
- [ ] Create `data/eval/premium_drop.csv`.
- [ ] Create `data/eval/missing_earned_premium.csv`.
- [ ] Create `data/eval/prompt_injection_notes.csv`.
- [ ] Document data fields in README.

## Milestone 2: Deterministic tools

- [ ] Implement `load_portfolio_data`.
- [ ] Implement `validate_portfolio_data`.
- [ ] Implement `calculate_portfolio_metrics`.
- [ ] Implement `detect_anomalies`.
- [ ] Implement `investigate_anomaly_drivers`.
- [ ] Implement `generate_report`.
- [ ] Implement `write_trace`.

## Milestone 3: Agent workflow

- [ ] Implement main orchestration flow.
- [ ] Add agent instructions.
- [ ] Add tool-calling logic.
- [ ] Add human review gate.
- [ ] Add final response format.
- [ ] Add error handling.

## Milestone 4: Skill packaging

- [ ] Add `portfolio-monitoring` skill folder.
- [ ] Add `SKILL.md`.
- [ ] Add references.
- [ ] Add report template.
- [ ] Test prompts that should trigger the skill.
- [ ] Test prompts that should not trigger the skill.

## Milestone 5: Security controls

- [ ] Add path allowlist.
- [ ] Add prompt-injection detector.
- [ ] Add secret scanning rule or pre-commit hook.
- [ ] Add disabled external-action handling.
- [ ] Add data text sanitization.
- [ ] Add security tests.

## Milestone 6: Evaluation

- [ ] Add eval case JSON.
- [ ] Add trace generator.
- [ ] Add deterministic eval checks.
- [ ] Add LLM-as-judge config if available.
- [ ] Add `make eval`.
- [ ] Save sample evaluation scorecard.

## Milestone 7: Demo outputs

- [ ] Generate sample report for loss ratio spike.
- [ ] Generate trace JSON for demo run.
- [ ] Generate screenshot of report.
- [ ] Generate architecture diagram.
- [ ] Create cover image.

## Milestone 8: Optional UI

- [ ] Build Streamlit or static HTML report viewer.
- [ ] Add run button or sample report selector.
- [ ] Add human review flag display.
- [ ] Add screenshots.

## Milestone 9: Submission assets

- [ ] Finalize Kaggle writeup.
- [ ] Record YouTube video under 5 minutes.
- [ ] Attach media gallery.
- [ ] Attach public project link.
- [ ] Submit before deadline.

## Milestone 10: Build Governance and Gates (50_implementation/02_spec_adequacy_and_build_gates.md)

- [ ] Gate 0: Create and complete spec completeness review artifact (`artifacts/spec_reviews/spec_review_vX.md`) before coding.
- [ ] Gate 1: Create and complete plan-only build review artifact (`artifacts/build_plans/build_plan_vX.md`) detailing MVP implementation.
- [ ] Gate 2: Implement and verify the vertical-slice build, producing `artifacts/gate_results/gate_2_vertical_slice.md`.
- [ ] Gate 3: Create golden datasets and expected-output YAML files for deterministic metrics, producing `artifacts/gate_results/gate_3_golden_tests.md`.
- [ ] Gate 4: Set up and run the agent/report/security evaluation suite, producing `artifacts/gate_results/gate_4_agent_evals.md`.
- [ ] Gate 5: Perform the fresh-context rebuild test to verify spec completeness, producing `artifacts/rebuilds/fresh_rebuild_vX.md`.
- [ ] Gate 6: Complete the submission readiness checklist, producing `artifacts/gate_results/gate_6_submission_readiness.md`.

## Suggested implementation prompts for coding agent

### Prompt 1: Create project skeleton

"Create a Python project for the Actuarial Portfolio Monitoring Agent using the specs in `capstone_spec_files/`. Set up the directory structure, pyproject, README, data folders, output folders, and test folders. Do not implement business logic yet."

### Prompt 2: Implement deterministic tools

"Implement the deterministic tools exactly according to `capstone_spec_files/20_contracts/02_tool_contracts.yaml`. Use Pydantic schemas for inputs and outputs. Add unit tests for each tool."

### Prompt 3: Implement agent workflow

"Implement the agent orchestration according to `capstone_spec_files/10_core/02_agent_architecture.md`. The LLM may only synthesize findings from tool outputs. Do not allow the LLM to calculate metrics."

### Prompt 4: Implement security

"Implement path allowlisting, prompt-injection detection, disabled external actions, and human review gates according to `capstone_spec_files/30_quality/01_security_privacy_spec.md`. Add tests."

### Prompt 5: Implement evaluations

"Create local eval datasets and scripts according to `capstone_spec_files/30_quality/03_evaluation_spec.yaml`. Generate traces and a scorecard."

## Milestone 11: ADK and Agents CLI alignment

This milestone is controlled by `capstone_spec_files/50_implementation/03_adk_alignment_notes.md` and preserves the deterministic monitoring engine while making the ADK runtime, callbacks, skill usage, FastAPI adapter, and Agents CLI evaluation explicit.

- [ ] Reconcile README commands, test counts, trace claims, and human-review terminology.
- [ ] Run `agents-cli info` and record whether `agents-cli scaffold enhance .` is required.
- [ ] Add `.agents-cli-spec.md` and reviewed Agents CLI project artifacts.
- [ ] Add `config.py` and a true zero-network `--force-offline` mode.
- [ ] Copy the portfolio-monitoring skill to `skills/portfolio_monitoring/` and verify runtime use.
- [ ] Add JSON-safe ADK wrappers around existing deterministic tools.
- [ ] Add ADK safety/trace callbacks.
- [ ] Export `root_agent` and create the `portfolio_agent` ADK application.
- [ ] Route the CLI through the shared application service.
- [ ] Add `fast_api_app.py` with health, readiness, and review endpoints.
- [ ] Add Makefile, Dockerfile, manifest, and dependency updates.
- [ ] Add unit/integration tests for callbacks, offline isolation, sessions, events, and adapter parity.
- [ ] Add Agents CLI eval datasets and `eval_config.yaml`.
- [ ] Generate and grade real ADK traces; compare results after fixes.
- [ ] Regenerate the readiness report, writeup, screenshots, and video from verified behavior.

### ADK alignment implementation prompts

#### Prompt 6: Reproducibility and scaffold enhancement

"Read `capstone_spec_files/50_implementation/03_adk_alignment_notes.md`, preserve all deterministic tools, inspect the existing Agents CLI state, add the reviewed project structure, and implement a zero-network offline path. Do not add ADK orchestration until the existing test suite and offline integration tests pass."

#### Prompt 7: ADK runtime

"Implement `root_agent`, the ADK application, tool adapters, callbacks, and runtime skill integration exactly as specified. Preserve deterministic calculations. Produce genuine function-call/function-response events and add integration tests without asserting LLM prose."

#### Prompt 8: FastAPI and evaluation

"Add the thin FastAPI adapter, verify CLI/API offline parity, create Agents CLI eval datasets/config, run generate and grade, and record actual scores. Do not deploy or modify cloud resources."
