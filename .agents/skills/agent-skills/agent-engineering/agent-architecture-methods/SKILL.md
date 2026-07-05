---
name: agent-architecture-methods
description: Use when designing an agent architecture, choosing between tools/MCP/skills/multi-agent patterns, writing a production spec, planning evaluation, or turning a vague agent idea into a buildable system design.
---

# Agent Architecture Methods

Use this skill to choose practical agent architecture patterns and convert intent into a buildable specification.

## Workflow

1. Clarify the target outcome, user workflow, risk level, and available tools.
2. Choose the smallest architecture that can satisfy the goal:
   - single agent with tools
   - agent with skills
   - orchestrated workflow
   - multi-agent handoff
   - event-driven or human-in-the-loop system
3. Read references based on the design question:
   - Broad architecture patterns: `references/agent_building_methods_extraction.txt`
   - Intent-driven development and harness engineering: `references/day1_vibe_coding_intro.txt`
   - Tools, MCP, and interoperability: `references/day2_agent_tools_interop.txt`
   - Spec-driven production development: `references/day5_spec_driven_production_dev.txt`
4. Produce a system design with boundaries, contracts, state, tools, evaluation, security, and deployment assumptions.
5. Prefer a concrete spec over abstract advice.

## Design Checklist

- Inputs, outputs, and user-visible success criteria
- Tool and data authority boundaries
- Deterministic code versus model judgment
- State and memory model
- Human approval points
- Observability and evaluation cases
- Failure modes and rollback path

## Evaluation Prompts

- Positive: "Design an agent that reviews expense events and asks a manager for approval above a threshold." Expected: architecture with events, policy, LLM role, HITL, state, and evals.
- Positive edge: "I have a vague idea for a research agent with web tools; make it production-ready." Expected: clarify boundaries, tool authority, safety, and evals before implementation.
- Negative: "Write the Python function for this already-designed helper." Expected: no architecture skill unless design choices are still open.
