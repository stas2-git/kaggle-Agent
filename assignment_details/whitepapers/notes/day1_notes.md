# Day 1 Notes — Vibe Coding Intro

## Core Framing
Software development is shifting from syntax (how) to intent (what): AI implements while humans keep architecture and judgment. The paper treats "vibe coding" (accepting whatever AI returns) and "agentic engineering" (AI implementing inside human-designed constraints, tests, feedback loops) as spectrum endpoints, with verification — not tool usage — as the real differentiator, and argues the SDLC is restructuring around a "factory model": the developer builds the system that produces code, not the code itself.

## Key Mechanisms & Techniques
- **Agent loop / five parts** — model (reasoning), tools, memory (state across sessions), orchestration (runs the loop), deployment (hosting, observability).
- **Vibe-to-agentic spectrum (Table 1)** — scored on intent specification, verification, codebase understanding, error handling, scope, risk; verification ranges from "does it seem to work" to test suites + CI/CD gates + LM judges.
- **Tests vs. Evals** — tests check deterministic input→output correctness; evals check non-deterministic trajectory/tool-choice/quality via labeled datasets, rubrics, and LM judges. Missing either means it's still vibe coding.
- **Six context types** — instructions, knowledge, memory, examples, tools, guardrails: the raw material of "context engineering."
- **Static vs. dynamic context** — static (AGENTS.md/CLAUDE.md/GEMINI.md, system prompt) is always loaded, token-costly; dynamic (skills, RAG, tool results, session history) loads only on demand.
- **Agent Skills** — procedural-knowledge packages via progressive disclosure (metadata at startup → full instructions on task match → deep reference when needed); fixes context rot, missing procedural memory, multi-agent overhead, portability.
- **The Factory Model** — developer designs specs, agents, tests/quality gates, feedback loops, guardrails; success comes from success criteria, not step-by-step instructions.
- **Harness = Model + Harness** — rule files, tools, sandboxes, orchestration logic, hooks, observability drive most behavior, not the model; harness-only tuning moved an agent from outside Top 30 to Top 5 on Terminal Bench 2.0.
- **Conductor vs. Orchestrator** — conductor: real-time, in-IDE, line-by-line direction; orchestrator: async, delegates to parallel agents, reviews results — needs specification, decomposition, evaluation, system-design skill.
- **The 80% problem** — AI generates ~80% of a feature fast; the remaining 20% (edge cases, error handling, integration, subtle correctness) needs human judgment.
- **CapEx/OpEx economics** — vibe coding: low CapEx, high OpEx (token-burn fix-loops, maintenance tax, security remediation); agentic engineering: high CapEx, low OpEx, plus routing deterministic subtasks to cheaper models.

## Terminology
- **AGENTS.md/CLAUDE.md/GEMINI.md** — rule files defining agent role and hard constraints.
- **MCP** — Model Context Protocol; standard for tool access.
- **A2A** — Agent2Agent protocol; standard for cross-agent delegation.
- **ADK** — Agent Development Kit; Google's scaffold/code/evaluate/deploy/observe lifecycle.
- **Agents CLI** — terminal tool bundling ADK-lifecycle skills into any coding agent.
- **TCO** — Total Cost of Ownership; the CapEx+OpEx framing.
- **LM judge** — model scoring agent output/trajectory in evals.

## Capstone Applicability
- Tests+evals, not prompts, separate agentic engineering from vibe coding — write the capstone's eval suite and rubrics before generating agent code.
- Static context is token-expensive — keep the capstone's system prompt/AGENTS.md lean and push specialist knowledge into Agent Skills loaded on demand.
- The harness, not the model, explains most agent behavior and failures — invest in tools, sandboxing, hooks, and observability.
- The 80% problem means budgeting explicit review time for edge cases and integration points instead of trusting a passing demo.
- Agentic engineering trades upfront CapEx for lower OpEx — front-load spec/context work and route deterministic subtasks to cheaper models.
