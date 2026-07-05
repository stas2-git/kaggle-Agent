# Agent Incident Retrospective Template

```text
Incident:
Expected behavior:
Actual behavior:
Impact:
Evidence:
Failure type:
Root cause:
Failed boundary:
Repair surface:
Specific fix:
Regression eval:
Owner / follow-up:
Residual risk:
```

## Repair Surface Guide

- Prompt vague: add spec/checklist behavior.
- Skill missed: sharpen description or router entry.
- Reference too bulky: shorten or split.
- Tool misuse: narrow schema, permissions, or active tool list.
- Unsafe action: add approval gate or least-privilege plan.
- Missing proof: add test, eval, or required verification.
- Loop/cost issue: add stopping rule, timeout, or circuit breaker.

## Regression Eval Pattern

```text
Prompt that reproduces the failure:
Context/setup:
Expected safe behavior:
Forbidden behavior:
Pass/fail check:
```
