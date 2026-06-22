# Implementation Plan

1. Scaffold the local ADK prototype and preserve Agents CLI project conventions.
2. Implement the validated, atomic discount tool and graph-wrapped shopping agent.
3. Add security context, command hook, Semgrep gate, and STRIDE skill.
4. Add outcome-based tests and demonstrate scanner failure/remediation.
5. Run formatting, lint, tests, security scans, skill validation, and a Gemini smoke test.

## Security Boundaries & Assertions

- Unregistered and malformed identities never mutate discount state.
- Unknown, malformed, and previously redeemed codes fail closed.
- The code check and state mutation are atomic within this local process.
- The model cannot override deterministic tool outcomes.
- Credentials are sourced from the environment and never embedded in source.
- Destructive command input is rejected, including chained commands.
- Static scanning returns a nonzero exit code for credential-shaped Python source.
- Local hooks are treated as developer guardrails, not production authorization controls.
