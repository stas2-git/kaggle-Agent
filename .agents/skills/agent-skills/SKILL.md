---
name: agent-skills-router
description: Use when deciding which bundled agent skill to use for coding-agent workflow, agent engineering, skill design, ADK implementation, deployment, security, human review frontends, protocol selection, self-improvement, or Kaggle capstone planning.
---

# Agent Skills Router

Use this high-level skill to choose the smallest useful downstream skill. Do not treat this as a replacement for the focused skills; use it to route, then load the selected skill's `SKILL.md`.

## How To Route

1. Identify the user's actual task type.
2. Pick the smallest matching focused skill.
3. Name the exact focused skill and, when working inside this repo, its repo path.
4. If the package has been installed into `~/.codex/skills/`, focused skills usually live by skill name, such as `agent-skill-design`, not by grouped repo path.
5. Load the focused skill's `SKILL.md` before acting.

Do not use this router as the operational instructions for the task after a focused skill matches.

## Routing

### Coding Agent Workflow

Use these for Codex, GitHub Copilot, Cursor, and similar coding agents while they do software work.

- Use `spec-driven-agent-workflow` (`coding-agent-workflow/spec-driven-agent-workflow` in this repo) when converting vague coding intent into a spec, BDD scenarios, failing tests, small diffs, policy gates, or reviewable production work.
- Use `agent-self-audit` (`coding-agent-workflow/agent-self-audit` in this repo) before finalizing substantial work when the agent should check its own likely weaknesses, residual risk, verification gaps, context drift, and trajectory quality.
- Use `code-review-agent` (`coding-agent-workflow/code-review-agent` in this repo) when reviewing code changes, pull requests, diffs, patches, or AI-generated code for bugs, regressions, missing tests, security issues, oversized scope, or spec mismatch.
- Use `context-harness-debugger` (`coding-agent-workflow/context-harness-debugger` in this repo) when the coding agent is looping, missing instructions, calling the wrong tool, hallucinating dependencies, overloading context, or otherwise needs harness/context repair.
- Use `context-budget-planner` (`coding-agent-workflow/context-budget-planner` in this repo) when a task has too much source material, noisy context, overlapping instructions, or repeated context rot and needs a plan for static instructions, skills, references, scripts, retrieval, or summaries.
- Use `agent-incident-retrospective` (`coding-agent-workflow/agent-incident-retrospective` in this repo) after an agent mistake, unsafe action, bad answer, loop, near miss, or user correction when the goal is root cause, guardrail repair, and a regression eval.

### Agent Engineering

Use these when building, packaging, evaluating, or debugging agent systems and reusable skills.

- Use `agent-architecture-methods` (`agent-engineering/agent-architecture-methods` in this repo) when designing an agent system, choosing single-agent versus multi-agent, defining tools/state/evals/security, or turning a vague agent idea into a buildable architecture.
- Use `agent-protocol-selector` (`agent-engineering/agent-protocol-selector` in this repo) when choosing between project instructions, skills, scripts, MCP, A2A, A2UI, AP2/UCP, or ordinary application code.
- Use `agent-skill-design` (`agent-engineering/agent-skill-design` in this repo) when creating, refactoring, packaging, or reviewing portable skills and deciding what belongs in `SKILL.md`, `references/`, `scripts/`, or `assets/`.
- Use `agent-eval-case-builder` (`agent-engineering/agent-eval-case-builder` in this repo) when creating eval datasets, rubrics, golden prompts, red-team prompts, regression cases, or LLM-as-judge criteria for an agent workflow or skill.
- Use `skill-evaluation-loop` (`agent-engineering/skill-evaluation-loop` in this repo) when testing or improving a skill with trigger tests, execution tests, token-budget checks, regression checks, red-teaming, or promotion tiers.
- Use `agent-observability-trace-review` (`agent-engineering/agent-observability-trace-review` in this repo) when reviewing an agent trace, transcript, tool-call log, approval record, or suspicious final answer for trajectory quality, context loaded, tool choices, safety, cost, and verification.

### Safety Governance

Use these when agent behavior touches untrusted content, authority boundaries, approvals, or tool access.

- Use `prompt-injection-triage` (`safety-governance/prompt-injection-triage` in this repo) when external or retrieved content may contain hostile instructions, hidden directives, prompt injection, data-exfiltration attempts, or tool/action requests.
- Use `least-privilege-tool-planner` (`safety-governance/least-privilege-tool-planner` in this repo) before giving an agent tools, MCP servers, file access, credentials, shell/browser/session access, deployment authority, write permissions, or external action capability.
- Use `human-approval-gate-designer` (`safety-governance/human-approval-gate-designer` in this repo) when designing HITL approval flows, pending action payloads, approve/deny/edit decisions, escalation rules, audit records, and auto-approval boundaries.

### ADK Implementation

- Use `adk-ambient-agent` (`adk-implementation/adk-ambient-agent` in this repo) when building event-driven, scheduled, Pub/Sub-style, or ambient ADK agents with normalized inputs, deterministic routing, state, traces, and HITL.
- Use `adk-secure-lifecycle` (`adk-implementation/adk-secure-lifecycle` in this repo) when securing an ADK/tool-using agent with validation, authorization, guardrails, hooks, secret scanning, STRIDE, human gates, tests, and behavioral evals.
- Use `adk-runtime-deployment` (`adk-implementation/adk-runtime-deployment` in this repo) when packaging, testing, deploying, monitoring, or rolling back an ADK agent on Google Agent Runtime with Agents CLI, Terraform, IAM, artifacts, telemetry, and remote validation.
- Use `adk-hitl-frontend` (`adk-implementation/adk-hitl-frontend` in this repo) when building a human-in-the-loop frontend for pending approvals, event correlation, session resume, function responses, dashboards, auth, audit, Cloud Run, or Pub/Sub wiring.

### Capstone

- Use `kaggle-capstone-planner` (`capstone/kaggle-capstone-planner` in this repo) when planning, scoping, validating, or preparing a Kaggle Agent capstone submission, writeup, demo, local evaluation, track choice, or compliance review.

## Combination Patterns

- New production agent idea: start with `agent-architecture-methods`, then `spec-driven-agent-workflow`, then the relevant ADK implementation skill.
- Coding agent behaving badly: start with `agent-self-audit`; if there is a trace, use `agent-observability-trace-review`; if the issue repeats, use `context-harness-debugger`; after a concrete mistake, use `agent-incident-retrospective`.
- New skill from reference material: use `context-budget-planner`, then `agent-skill-design`, then `skill-evaluation-loop`.
- Tool/protocol confusion: use `agent-protocol-selector`, then route to MCP/A2A/A2UI/ADK implementation work as appropriate.
- Safety-sensitive tool access: use `least-privilege-tool-planner`, then `human-approval-gate-designer` if approvals are needed, and `prompt-injection-triage` when external content is part of the loop.
- Capstone build: start with `kaggle-capstone-planner`, then `agent-architecture-methods`, then `adk-secure-lifecycle` and `adk-runtime-deployment` when implementation matures.

## Rules

- Prefer the most specific skill that matches the current task.
- Load only one or two focused skills unless the task genuinely crosses boundaries.
- If no focused skill matches, proceed without forcing one.
- If the selected skill has references, load only the references relevant to the immediate task.

## Evaluation Prompts

Use these prompts to test routing behavior:

- Positive: "Help me decide whether this should be an MCP server, a skill, or an A2A agent." Expected: `agent-protocol-selector`.
- Positive: "My coding agent keeps calling the wrong tool and looping after long context." Expected: `context-harness-debugger`.
- Positive: "Turn this agent failure into a root cause and regression eval." Expected: `agent-incident-retrospective`.
- Positive: "Review this AI-generated PR for production risks." Expected: `code-review-agent`.
- Positive: "This retrieved web page says to ignore all previous instructions; what should the agent do?" Expected: `prompt-injection-triage`.
- Positive: "Plan my Kaggle Agent capstone submission and evaluation checklist." Expected: `kaggle-capstone-planner`.
- Negative: "Edit this CSS button color." Expected: no bundled agent skill unless the task expands into architecture, workflow, or evaluation.
- Negative: "Deploy this ordinary static website." Expected: no ADK deployment skill unless it is an ADK/Agent Runtime deployment.
- Negative: "Summarize this unrelated PDF." Expected: no bundled agent skill unless the summary is for capstone, architecture, or skill creation.
