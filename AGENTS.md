# Coding Agent Guide

## Project-Local Agent Skills

This repository has two different skill areas:

- `project_build/skills/` contains capstone runtime skills used by the portfolio-monitoring project itself.
- `.agents/skills/` contains project-local helper skills for coding agents working on this repo.

Use `.agents/skills/agent-skills/SKILL.md` as the router when a task touches agent design, ADK implementation, capstone planning, evaluation, security, deployment, coding-agent workflow, or skill design. After the router selects a focused skill, read that focused skill's `SKILL.md` before acting.

Use `.agents/skills/excel-skills/SKILL.md` as the router for Excel, workbook, spreadsheet, VBA, or live Excel automation work.

Use `.agents/skills/sql-skills/SKILL.md` as the router for actuarial or insurance SQL work, including writing queries, reviewing joins, building loss triangles, exploring schema, or executing database queries.

Do not confuse project-local coding-agent skills with the capstone runtime skill in `project_build/skills/portfolio_monitoring/`.

## Prerequisites

Install the CLI (one-time):
```bash
uv tool install google-agents-cli
```

---

## Development Phases

### Phase 1: Understand Requirements
Before writing any code, understand the project's requirements, constraints, and success criteria.

### Phase 2: Build and Implement
Implement agent logic in `project_build/portfolio_agent/`. Run project commands from `project_build/`. Use `agents-cli playground` for interactive testing. Iterate based on user feedback.

### Phase 3: The Evaluation Loop (Main Iteration Phase)
Start with 1-2 eval cases, run `agents-cli eval generate`, then `agents-cli eval grade`, iterate by making changes and rerunning both commands until satisfied. Expect 5-10+ iterations. Once you have a baseline, reach for `agents-cli eval compare` (regression diffs), `agents-cli eval analyze` (cluster failure modes), and `agents-cli eval optimize` (auto-tune prompts). See the **Evaluation Guide** for metrics, dataset schema, LLM-as-judge config, and common gotchas.

### Phase 4: Pre-Deployment Tests
From `project_build/`, run `uv run pytest tests/unit tests/integration`. Fix issues until all tests pass.

### Phase 5: Deploy to Dev
**Requires explicit human approval.** Run `agents-cli deploy` only after user confirms. See the **Deployment Guide** for details.

### Phase 6: Production Deployment
Ask the user: Option A (simple single-project) or Option B (full CI/CD pipeline with `agents-cli infra cicd`).

## Development Commands

| Command | Purpose |
|---------|---------|
| `cd project_build && agents-cli playground` | Interactive local testing |
| `cd project_build && uv run pytest tests/unit tests/integration` | Run unit and integration tests |
| `agents-cli eval dataset synthesize` | Synthesize multi-turn eval scenarios for your agent |
| `cd project_build && agents-cli eval generate` | Run agent on eval dataset, produce traces |
| `cd project_build && agents-cli eval grade` | Run agent evaluations on the traces |
| `cd project_build && agents-cli eval compare` | Compare two grade-results files (regression check) |
| `cd project_build && agents-cli eval analyze` | Cluster failure modes from grade results |
| `cd project_build && agents-cli eval metric list` | List built-in metrics available in the SDK |
| `cd project_build && agents-cli eval optimize` | Auto-tune agent prompts using eval data |
| `cd project_build && agents-cli lint` | Check code quality |
| `cd project_build && agents-cli infra single-project` | Set up project infrastructure (Terraform) |
| `cd project_build && agents-cli deploy` | Deploy to dev |
| `cd project_build && agents-cli scaffold enhance` | Add deployment target or CI/CD to project |
| `cd project_build && agents-cli scaffold upgrade` | Upgrade project to latest version |

---

## Operational Guidelines for Coding Agents

- **Code preservation**: Only modify code directly targeted by the user's request. Preserve all surrounding code, config values (e.g., `model`), comments, and formatting.
- **NEVER change the model** unless explicitly asked.
- **Model 404 errors**: Fix `GOOGLE_CLOUD_LOCATION` (e.g., `global` instead of `us-east1`), not the model name.
- **ADK tool imports**: Import the tool instance, not the module: `from google.adk.tools.load_web_page import load_web_page`
- **Run Python with `uv`**: `uv run python script.py`. Run `agents-cli install` first.
- **Stop on repeated errors**: If the same error appears 3+ times, fix the root cause instead of retrying.
- **Terraform conflicts** (Error 409): Use `terraform import` instead of retrying creation.
