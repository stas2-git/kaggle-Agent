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

## Suggested implementation prompts for coding agent

### Prompt 1: Create project skeleton

"Create a Python project for the Actuarial Portfolio Monitoring Agent using the specs in `specs/`. Set up the directory structure, pyproject, README, data folders, output folders, and test folders. Do not implement business logic yet."

### Prompt 2: Implement deterministic tools

"Implement the deterministic tools exactly according to `specs/05_tool_contracts.yaml`. Use Pydantic schemas for inputs and outputs. Add unit tests for each tool."

### Prompt 3: Implement agent workflow

"Implement the agent orchestration according to `specs/03_agent_architecture.md`. The LLM may only synthesize findings from tool outputs. Do not allow the LLM to calculate metrics."

### Prompt 4: Implement security

"Implement path allowlisting, prompt-injection detection, disabled external actions, and human review gates according to `specs/07_security_privacy_spec.md`. Add tests."

### Prompt 5: Implement evaluations

"Create local eval datasets and scripts according to `specs/09_evaluation_spec.yaml`. Generate traces and a scorecard."
