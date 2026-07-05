---
name: agent-self-audit
description: Use before finishing substantial agent/coding work to audit the agent's likely weaknesses: misunderstood intent, missing verification, weak trajectory, context drift, hidden security risk, cost/loop inefficiency, and poor self-repair.
---

# Agent Self Audit

Use this skill as a pre-final or pre-commit self-check for non-trivial work. Its job is to make the agent name what could be wrong with its own result before presenting it as done.

## Workflow

1. Reconstruct the user intent from the first user request plus any later corrections.
2. Score the work against seven dimensions:
   - intent satisfaction
   - functional correctness
   - visual/behavioral correctness when UI is involved
   - cost and efficiency
   - code quality and convention matching
   - trajectory quality
   - self-repair behavior
3. Check for common agent failure modes:
   - The output looks plausible but misses an unstated requirement.
   - The agent verified the final artifact but not the path taken.
   - Tests were changed to fit the implementation instead of proving behavior.
   - Context drift occurred after many turns or tool outputs.
   - A tool, dependency, or package name may have been hallucinated.
   - Security boundaries or authority levels were assumed rather than checked.
4. For each risk, either verify it, fix it, or state residual risk plainly.
5. Only then produce the final answer.

## References

- Read `references/day4_security_evaluation.txt` for evaluation dimensions, trajectory inspection, intent satisfaction, session convergence, and security/evaluation separation.
- Read `references/day1_vibe_coding_intro.txt` for the 80% problem, harness failures, context engineering, and agentic engineering versus vibe coding.

## Output

When useful, include a compact audit:

```text
Intent: ...
Verified: ...
Weak Spots Checked: ...
Residual Risk: ...
```

## Evaluation Prompts

- Positive: "Before you finish, audit your work for likely mistakes." Expected: compact intent, verification, weak spots, and residual risk.
- Positive edge: "You changed code and tests after a long thread; sanity check before final." Expected: context drift, trajectory, and verification review.
- Negative: "Explain what a self-audit is." Expected: ordinary explanation, not a pre-final audit unless work is being finalized.
