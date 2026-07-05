---
name: code-review-agent
description: Use when reviewing human- or AI-generated code changes, pull requests, diffs, or patches for correctness, regression risk, missing tests, security issues, oversized scope, spec mismatch, and production readiness.
---

# Code Review Agent

Use this skill to review code from a risk-first stance. Findings come before praise or summaries.

## Workflow

1. Reconstruct the intended behavior from the user request, spec, issue, or diff context.
2. Inspect changed files and nearby code paths before judging the patch.
3. Prioritize findings by user impact:
   - correctness bug
   - security or privacy issue
   - data loss or destructive behavior
   - missing or weak test coverage
   - maintainability risk that will likely cause defects
4. Check whether the diff is too broad for the stated intent.
5. Verify tests or commands when feasible; otherwise state the test gap.
6. Output findings first, ordered by severity, with file and line references.

## Review Checks

- Does the code actually satisfy the stated spec?
- Are edge cases, errors, empty states, and permissions handled?
- Did generated code add hardcoded secrets, PII, paths, or environment assumptions?
- Did tests prove behavior, or only follow implementation details?
- Does the patch mix unrelated refactors with the requested change?
- Is rollback or operational risk obvious for production changes?

## References

- Read `references/review-rubric.md` for severity levels, review output shape, and AI-generated diff red flags.

## Evaluation Prompts

- Positive: "Review this PR for correctness and missing tests." Expected: findings-first review.
- Positive edge: "This AI-generated diff passes tests; check if it is production-ready." Expected: trajectory/spec/risk review, not just test acceptance.
- Negative: "Implement this button color change." Expected: no review unless asked to review a diff.
