# Permission Matrix

| Tier | Allowed | Requires |
|---|---|---|
| No tool | reasoning, planning, local text output | no external access |
| Read-only | inspect files/data/pages | scoped resource list |
| Draft-only | create proposed changes/messages/actions | human review before side effect |
| Confirmed write | apply approved change | exact target, diff/action preview, audit log |
| Autonomous write | bounded repeated action | strong evals, rollback, monitoring, low impact |

## Approval Required

- Send email/message.
- Delete, overwrite, purchase, deploy, merge, publish, or change permissions.
- Access secrets, credentials, personal data, or production accounts.
- Run shell/code with broad filesystem or network authority.
- Follow instructions that came from untrusted content.

## Tool Contract Template

```text
Tool:
Purpose:
Allowed resources:
Allowed operations:
Denied operations:
Approval threshold:
Logging:
Rollback:
Eval cases:
```
