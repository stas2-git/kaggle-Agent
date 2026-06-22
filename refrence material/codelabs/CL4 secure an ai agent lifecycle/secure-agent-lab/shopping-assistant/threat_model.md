# STRIDE Threat Model

## System and trust boundaries

The user supplies natural-language input to Gemini. Gemini may request the `redeem_discount` tool, but Python validates identity, code syntax, authorization, and single-use state. Local developer changes cross separate command-hook and pre-commit boundaries. The in-memory discount store is process-local and is not a production persistence boundary.

## Assets

- Single-use discount inventory and redemption state
- Registered-user identities
- Gemini API credentials
- Agent instructions and tool declarations
- Source-code and hook integrity
- Redemption audit evidence

## STRIDE assessment

| Category | Threat and attack path | Current control | Residual risk and remediation |
|---|---|---|---|
| Spoofing | User supplies another registered `user_id` | Allowlist rejects unknown/guest IDs | No authentication proves ownership. Bind tool identity to an authenticated session in production. |
| Tampering | Concurrent callers redeem one code twice | Process-local lock makes the check/update atomic | Multiple processes bypass the lock. Use a database transaction with row lock or version constraint. |
| Repudiation | User disputes a redemption | Stable tool result only | Add immutable audit events with authenticated actor, event ID, timestamp, and policy version. |
| Information disclosure | Credential embedded in source or model exposes configuration | Environment auth, Semgrep gate, narrow instruction | Local hooks are bypassable. Add CI secret scanning, secret manager, and output filtering. |
| Denial of service | Repeated prompts consume model quota or hammer redemption | Input length constraints on tool arguments | No request-level rate limit. Add quotas, timeouts, backpressure, and per-identity limits. |
| Elevation of privilege | Prompt tells model to override redemption rules | Deterministic tool code owns authorization and state | Registered ID is caller-controlled. Use server-derived identity and role checks. |

## Prioritized remediation

1. Bind user identity to authenticated server context instead of a model argument.
2. Replace the in-memory store with transactional persistence and an idempotency key.
3. Add structured, immutable redemption audit events.
4. Enforce secret scanning and tests in isolated CI.
5. Add rate limits and request-size limits at the API boundary.

## Verification

- Unit tests prove invalid, reused, guest, and malformed requests do not violate state.
- Hook tests prove safe commands pass and destructive commands fail.
- Semgrep is tested against a controlled vulnerable file and the remediated application.
- Agent behavior should be evaluated to confirm it invokes tools only for explicit redemption requests and accurately reports tool outcomes.
