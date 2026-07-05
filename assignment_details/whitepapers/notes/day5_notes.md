# Day 5 Notes — Spec-Driven Production Dev

## Core Framing
AI agents removed implementation as the bottleneck, moving the real constraint to humans who must review and govern AI output. The fix: treat specs, not code, as the source of truth, and wrap agents in layered guardrails — SDD, sandboxing, tiered review, a hybrid Policy Server — so speed never replaces control.

## Key Mechanisms & Techniques
- **Spec-Driven Development (SDD)** — Code is disposable; a solid spec (Markdown/YAML in `specs/`) lets the codebase be regenerated or ported, serving as source of truth for humans and AI.
- **Gherkin/BDD specs** — Scenario / Given / When / Then syntax forces State > Action > Outcome reasoning, killing ambiguous "vibe coding."
- **Hybrid Markdown + YAML formatting** — Per the cited SkCC study, YAML parses nested config (depth >3) far more accurately (51.9% vs. 43.1% JSON, 33.8% XML) than flat Markdown, avoiding a reasoning "format tax."
- **Instruction hierarchy** — Chat (session-only), spec folder (repo-tracked), Agent Skills (`.agent/skills`), layered prompts (`GEMINI.md` global/project, cross-tool `AGENTS.md`).
- **Execution modes** — Project Generation (no YOLO mode), Feature Generation (diff review), Bug Fixing (Evidence Prompting, failing test first), Documentation, Data Engineering.
- **MCP** — One server (e.g., SQLite via `query_knowledge`/`add_knowledge`) is reusable by any MCP-compatible client, no custom integration.
- **Conditional LGTM & review culture** — PR risk-assessment summaries, No-Blame Culture, and auto-merge on green tests, backed by an agent-run review skill (`code-check.md`).
- **Three-tier review spectrum** — Tier 1 Managed (SaaS reviewer); Tier 2 Hybrid (skill + GitHub Action, recommended default); Tier 3 Custom (ADK agent on Agent Runtime with durable memory, optional knowledge graph + sub-agent pipeline for legacy refactors).
- **Zero-trust guardrails** — Sandboxing (low-privilege containers, "Terminal Sandboxing" toggle, `GEMINI_SANDBOX=docker`) confines the blast radius; HITL gates require sign-off on high-risk ops.
- **Hybrid Policy Server** — Structural Gating (`policies.yaml` role/env rules, e.g. viewer blocked from `send_email`) plus Semantic Gating (a secondary LLM checks intent for policy violations, e.g. unmasked PII); both must pass before a tool runs.
- **ContextResolver** — Regex utility resolves `[[VARIABLE_NAME]]` placeholders from runtime state or env vars, preventing "context hallucination" (agent inventing data to fill gaps).
- **AI-generated tests & Evaluation** — Agents produce a failing test/repro before fixing bugs; evaluation swaps binary assertions for LLM-as-judge scores and tolerance bands to catch behavioral drift.

## Terminology
- **SDD** — Spec-Driven Development.
- **BDD / Gherkin** — Behavior-Driven Development syntax (Scenario/Given/When/Then).
- **MCP** — Model Context Protocol, "USB-C for AI tools."
- **ADK** — Agent Development Kit; sub-agent pipeline framework.
- **A2A** — Agent-to-Agent protocol.
- **HITL** — Human-in-the-Loop checkpoint gate.
- **YOLO mode** — Auto-approve mode, no confirmation.
- **SkCC** — Skill Compiler; compiles instructions into a model's optimal format.

## Capstone Applicability
- Write requirements as Gherkin scenarios in a checked-in `specs/` folder before coding, so the agent builds against a blueprint, not a vague prompt.
- Store nested config as YAML and narrative instructions as Markdown to cut the format tax.
- Front any tool call touching external systems with a Policy Server (structural + semantic checks), especially PII-risk calls.
- Require a failing test before fixes, and add LLM-as-judge evaluation to catch behavioral drift.
- Start review/monitoring at Tier 2 (skill + CI) before a full Tier 3 runtime unless cross-run memory is needed.
