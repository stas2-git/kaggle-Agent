---
name: context-harness-debugger
description: Use when an agent performs poorly, loops, calls the wrong tool, misses instructions, overuses context, hallucinates dependencies, or seems like it needs a better harness rather than a better model.
---

# Context Harness Debugger

Use this skill to diagnose agent failures as harness, context, tool, or evaluation problems before blaming the model.

## Failure Triage

1. Capture the symptom: wrong output, wrong tool, loop, stale assumption, security issue, high cost, or brittle self-repair.
2. Map it to a likely harness cause:
   - Missing or vague instructions
   - No skill or wrong skill trigger
   - Too much static context causing context rot
   - Missing tool, oversized tool list, or bad tool schema
   - No deterministic guardrail/hook
   - Weak sandbox or authority boundary
   - No observability trace for the trajectory
   - No eval case covering the failure
3. Decide the repair surface:
   - Static project rule: small, universal behavior
   - Skill: reusable procedural workflow
   - Reference file: large conditional knowledge
   - Script/hook: deterministic enforcement
   - Tool/MCP change: external capability or schema issue
   - Eval: failure should be caught next time
4. Prefer reducing active context over adding more instruction text.
5. After the fix, add a regression prompt or test case that would have caught the failure.

## References

- Read `references/day1_vibe_coding_intro.txt` for harness anatomy, context engineering, the 80% problem, and the factory model.
- Read `references/day3_agent_skills.txt` for context rot, progressive disclosure, skill composition, and context debt.
- Read `references/day4_security_evaluation.txt` for observability, trajectory quality, intent drift, and circuit breakers.

## Anti-Patterns

- Do not fix every failure by adding "ALWAYS" rules.
- Do not stuff large documents into static prompts.
- Do not let the LLM context window become the database or message bus.
- Do not accept a correct final answer if the tool trajectory was unsafe for an action-allowed workflow.

## Evaluation Prompts

- Positive: "My agent keeps looping and calling the wrong tool." Expected: diagnose context, tool list, instructions, guardrails, and eval gaps.
- Positive edge: "The answer is right but it used unsafe tool calls." Expected: trajectory/harness repair, not model praise.
- Negative: "The app has a runtime bug in this stack trace." Expected: normal debugging unless the failure is agent-harness behavior.
