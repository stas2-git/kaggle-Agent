---
name: agent-observability-trace-review
description: Use when reviewing or debugging an agent run, trace, tool-call log, transcript, cost report, approval record, or suspicious final answer to inspect trajectory quality, context loaded, tool choices, retries, failures, cost, safety gates, and whether the final output is supported by the run.
---

# Agent Observability Trace Review

Use this skill to judge how an agent behaved, not just what it answered.

## Workflow

1. Reconstruct the run: user request, loaded context, tools, actions, outputs, approvals, and final response.
2. Identify the intended success criteria.
3. Inspect trajectory for:
   - wrong tool or missing tool,
   - untrusted content treated as instruction,
   - unnecessary authority,
   - loops/retries/cost spikes,
   - missing verification,
   - unsafe side effects,
   - drift from the latest user request.
4. Compare final answer to evidence in the trace.
5. Produce findings and recommended harness/eval fixes.

## References

- Read `references/trace-rubric.md` for review dimensions and output template.

## Evaluation Prompts

- Positive: "Review this agent transcript and tell me where it went wrong." Expected: trajectory findings.
- Positive edge: "The final answer was correct; was the run safe?" Expected: inspect tool path and approvals.
- Negative: "Summarize this normal meeting transcript." Expected: no trace review unless it is an agent run.
