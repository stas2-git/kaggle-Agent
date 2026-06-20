# Capstone Spec Package: Actuarial Portfolio Monitoring Agent

Prepared: 2026-06-20

This package is a full set of specification files for a Kaggle AI Agents Intensive Vibe Coding capstone project.
The project is framed as an **Agents for Business** submission: an AI agent that monitors a portfolio or book of business, detects material changes, investigates likely drivers, and produces an actuary-ready review note.

The specs are intentionally written before implementation. Treat them as the source of truth. Code can be regenerated, but the agent's required behavior, safety limits, evaluation criteria, and demo story should stay anchored here.

## Working project name

**Actuarial Portfolio Monitoring Agent**

Alternative names:
- Portfolio Signal Agent
- Actuarial Trend Review Agent
- Book Monitoring Copilot
- Underwriting Portfolio Watchtower

## One-sentence pitch

An agentic workflow that reads a synthetic insurance portfolio extract, calculates key monitoring metrics, detects unusual trend changes, investigates drivers, and generates a concise actuarial review memo with flagged exceptions and recommended follow-up questions.

## Course concepts intentionally demonstrated

The capstone should explicitly demonstrate at least three course concepts. This package is designed to show more than three:

1. **Agent / graph workflow**: a multi-step agent workflow with deterministic tools, LLM reasoning, and human review gates.
2. **Agent tools**: schema-bound tools for loading data, validating data, calculating metrics, detecting changes, investigating drivers, and generating a report.
3. **Agent skills**: a portable `SKILL.md` skill that teaches the agent how to perform portfolio trend investigation.
4. **Security features**: tool allowlists, no secrets, local/synthetic data, prompt-injection handling, risk-based human-in-the-loop gates, and output safety checks.
5. **Evaluation**: deterministic tests and LLM-as-judge evaluation over trace outputs.
6. **Deployability**: local-first MVP with optional cloud deployment path.
7. **Antigravity / Agents CLI workflow**: specs are structured so a coding agent can implement the project through stepwise prompts.

## File map

| File | Purpose |
|---|---|
| `01_capstone_submission_strategy.md` | Track, scoring strategy, assets, and positioning. |
| `02_product_requirements.md` | Product requirements, users, goals, MVP, non-goals. |
| `03_agent_architecture.md` | Agent workflow, components, data flow, human review gates. |
| `04_data_spec_and_schemas.md` | Synthetic dataset design, columns, validation rules, metric definitions. |
| `05_tool_contracts.yaml` | Machine-readable tool contracts for implementation. |
| `06_behavior_spec.feature` | BDD / Gherkin behavior scenarios. |
| `07_security_privacy_spec.md` | Security and privacy controls. |
| `08_threat_model_stride.md` | STRIDE threat model and mitigations. |
| `09_evaluation_spec.yaml` | Evaluation cases, judge criteria, metrics, pass thresholds. |
| `10_observability_trace_spec.md` | Trace schema, logs, trust indicators, debugging views. |
| `11_skill_portfolio_monitoring/` | Agent Skill folder with `SKILL.md`, references, and report template. |
| `12_deployment_spec.md` | Local MVP and optional cloud deployment plan. |
| `13_demo_video_script.md` | Five-minute video structure and narration. |
| `14_kaggle_writeup_draft.md` | Draft writeup structure under the capstone word limit. |
| `15_implementation_backlog.md` | Build plan organized into milestones. |
| `16_acceptance_checklist.md` | Final readiness checklist before submission. |
| `17_AGENTS.md` | Candidate project-level coding-agent instructions. |
| `18_CONTEXT.md` | Candidate project-level secure coding context. |
| `19_reproducibility_and_repo_spec.md` | README/setup/reproducibility requirements. |
| `20_synthetic_eval_cases.json` | Example evaluation case definitions. |
| `21_risk_register.md` | Project risks and mitigations. |
| `22_output_report_template.md` | Expected final report format. |

## Recommended implementation style

Start local. Use synthetic CSV files and deterministic Python tools first. Then add the LLM layer for reasoning and narrative generation. This keeps the demo reliable and makes the agent's value clear without depending on private data or external systems.

Suggested MVP stack:
- Python 3.11+
- Pandas for deterministic metric calculation
- A graph-style agent workflow using ADK or an equivalent agent framework
- JSON/YAML schemas for tool inputs and outputs
- Markdown report output
- Local evaluation scripts
- Optional web dashboard or static HTML report

## Suggested build order

1. Create synthetic portfolio data.
2. Implement deterministic tools.
3. Implement the agent workflow.
4. Add the portfolio-monitoring skill.
5. Add behavior tests and evaluation cases.
6. Add security checks and prompt-injection tests.
7. Generate demo report.
8. Record video.
9. Submit Kaggle writeup, video, and public project link.
