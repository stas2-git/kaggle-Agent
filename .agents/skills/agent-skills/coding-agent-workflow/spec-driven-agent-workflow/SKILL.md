---
name: spec-driven-agent-workflow
description: Use when converting vague intent into production-grade agent/coding work with specs, BDD scenarios, failing tests first, small diffs, evidence-based debugging, review summaries, policy gates, and human approval boundaries.
---

# Spec-Driven Agent Workflow

Use this skill to move from "vibe" to production-grade agentic engineering.

## Workflow

1. Turn the request into a lightweight spec before implementation:
   - purpose
   - non-goals
   - contracts and schemas
   - scenarios and edge cases
   - success criteria
   - risk and approval boundaries
2. Use BDD shape for behavior:
   - Given state
   - When action
   - Then observable outcome
3. For bug fixes, demand evidence before edits:
   - reproduction command
   - failing test
   - relevant logs
   - root-cause hypothesis
4. Keep implementation small and reviewable. Avoid mixing refactors with fixes.
5. Verify with tests/evals and summarize risk in the final handoff.

## References

- Read `references/day5_spec_driven_production_dev.txt` for SDD, BDD, prompt modes, review process, guardrails, policy servers, and context hygiene.
- Read `references/day1_vibe_coding_intro.txt` for agentic engineering, tests/evals as contracts, and the factory model.

## Prompt Modes

- Architect: propose structure and tradeoffs before coding.
- Builder: implement against existing conventions.
- Forensic specialist: reproduce, isolate root cause, and patch surgically.
- Reviewer: summarize change, risk, and verification.

## Evaluation Prompts

- Positive: "Build this feature, but make it production-ready." Expected: lightweight spec, acceptance checks, scoped implementation, and verification.
- Positive edge: "Fix this bug without guessing." Expected: reproduction/failing evidence before patching.
- Negative: "What is BDD?" Expected: explanation only, not a full spec workflow.
