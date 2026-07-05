# Code Review Rubric

## Severity

- Critical: data loss, auth bypass, secret exposure, external side effect, or crash in a core path.
- High: incorrect user-visible behavior, security weakness, serious regression, or missing validation.
- Medium: likely edge-case failure, weak tests, brittle design, or operational risk.
- Low: style or clarity issue that could cause confusion but not a likely defect.

## Output Shape

```text
Findings
- [severity] file:line - What is wrong, why it matters, and what should change.

Open Questions
- Only include if the answer changes review outcome.

Verification
- Commands/tests inspected or not run.
```

## AI-Generated Diff Red Flags

- Large unrelated edits.
- New abstraction that local code does not need.
- Tests changed to match the implementation instead of proving behavior.
- Hardcoded paths, sample credentials, fake IDs, or environment-specific values.
- Plausible imports or APIs not present in the repo.
- Error handling that logs and continues after a failed critical operation.
- Security checks in frontend only, with no backend enforcement.
