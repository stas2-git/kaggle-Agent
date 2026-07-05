# Approval Gate Patterns

## Risk Tiers

- Low: reversible local change, no external side effect. May auto-approve after tests.
- Medium: write action with limited scope. Require diff/action preview.
- High: external communication, production change, sensitive data, account permission, payment. Require explicit approval.
- Blocked: unclear user intent, missing target, prompt-injection source, impossible rollback, or policy violation.

## Decision Model

```text
Pending action:
Reviewer:
Decision: approve | deny | edit | clarify | escalate
Reason:
Applied action:
Audit id:
Rollback:
```

## Anti-Patterns

- Asking for approval without showing exact target and payload.
- Bundling many risky actions into one approval.
- Letting approval expire silently but still execute later.
- Treating user silence as approval.
- Allowing untrusted content to define approval text or target.
