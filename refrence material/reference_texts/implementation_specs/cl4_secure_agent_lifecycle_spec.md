# Secure Agent Lifecycle Implementation Spec

## 1. Purpose

This document extracts the reusable architecture and development logic from the secure shopping-assistant codelab. Its central lesson is broader than discount redemption:

> Secure an agent at multiple boundaries—planning, input validation, tool authorization, state mutation, developer actions, source control, testing, and evaluation—instead of relying on the model prompt as the security boundary.

The application is deliberately small so the secure-development lifecycle remains visible.

## 2. Security model

The system separates responsibilities into three layers:

| Layer | Responsibility | Security authority |
|---|---|---|
| Gemini agent | Understand intent and request the appropriate tool | Advisory only |
| Python tool | Validate, authorize, enforce policy, and mutate state | Application authority |
| Development gates | Prevent unsafe code and commands from entering the project | Local engineering controls |

The model can ask to redeem a code. It cannot decide that an unknown user is registered, reuse a spent code, or overwrite the tool result.

## 3. Runtime architecture

```text
User request
    |
    v
Gemini LlmAgent
    |
    | function call: redeem_discount(code, user_id)
    v
Pydantic validation
    |
    v
Registered-user authorization
    |
    v
Atomic code check and state mutation
    |
    v
Stable tool outcome
    |
    v
Gemini reports the result
```

ADK wraps the agent in a graph workflow:

```python
root_agent = Workflow(
    name="shopping_assistant_workflow",
    edges=[("START", shopping_agent)],
)
```

The graph currently has one LLM node. Using `Workflow` still establishes an extension point for future security screens, human approval, auditing, or specialized agents.

## 4. Domain contracts

### Tool input

```python
class DiscountRequest(BaseModel):
    code: str
    user_id: str
```

The actual schema applies:

- Code length: 4–20 characters.
- Code alphabet: uppercase letters and digits.
- User-ID length: 3–40 characters.
- User-ID alphabet: letters, digits, and underscore.
- Leading and trailing whitespace is removed.
- Codes are normalized to uppercase.
- Non-string values fail validation.

This is an important capstone pattern: validate at the tool boundary even if ADK or the model already produced a structured function call. Model-generated arguments are still untrusted input.

### Stable outcomes

The tool returns bounded, predictable outcomes:

```text
Success: Discount code CODE redeemed successfully for user USER.
Error: Invalid discount request format.
Error: Registered user account required to redeem discounts.
Error: Invalid discount code.
Error: Discount code has already been redeemed.
```

Stable outcomes help the LLM report results accurately and make deterministic tests straightforward.

For a larger capstone, prefer a typed result:

```python
class ToolResult(BaseModel):
    status: Literal["success", "error"]
    reason: Literal[
        "redeemed",
        "invalid_format",
        "unauthorized",
        "unknown_code",
        "already_redeemed",
    ]
    message: str
    transaction_id: str | None
```

## 5. Redemption algorithm

The tool performs checks in this order:

```text
1. Parse and normalize the request with Pydantic.
2. Reject malformed values.
3. Reject users outside the registered-user set.
4. Acquire the store lock.
5. Reject an unknown code.
6. Reject a previously redeemed code.
7. Mark the code redeemed.
8. Release the lock.
9. Return success.
```

Authorization runs before state access. The code check and mutation occur inside the same lock.

Equivalent pseudocode:

```python
request = validate(code, user_id)

if request.user_id not in registered_users:
    return unauthorized

with transaction_boundary:
    discount = load_discount(request.code)
    if not discount:
        return unknown_code
    if discount.redeemed:
        return already_redeemed
    discount.redeemed = True

return success
```

## 6. Concurrency and transaction boundary

The codelab uses a `threading.Lock` to protect this sequence:

```python
if DISCOUNT_STORE[code]:
    reject()
DISCOUNT_STORE[code] = True
```

Without a lock, two threads could both observe `False` before either writes `True`, allowing double redemption.

The lock is only process-local. It does not protect:

- Multiple web-server processes.
- Multiple containers.
- Restarts.
- Distributed workers.
- Direct database writers.

Production implementation should use a database constraint and transaction, for example:

```sql
UPDATE discounts
SET redeemed_by = :user_id,
    redeemed_at = CURRENT_TIMESTAMP
WHERE code = :code
  AND redeemed_at IS NULL;
```

Treat one affected row as success and zero affected rows as unknown/already redeemed. This provides atomicity at the shared persistence boundary.

## 7. Identity and authorization

The demo checks membership in:

```python
REGISTERED_USERS = {"user_123", "user_456"}
```

This enforces business policy but does not authenticate the caller. The user can type another registered ID into the prompt.

Capstone production rule:

```text
Do not let the model or prompt supply authoritative identity.
```

Instead:

1. Authenticate at the API/UI boundary.
2. Store verified identity in server-side session context.
3. Inject that identity into the tool from trusted context.
4. Ignore or reject a conflicting identity supplied in natural language.
5. Authorize the specific operation against roles and resource ownership.

## 8. Model configuration and limits

The Gemini model is selected from the environment:

```python
model = Gemini(
    model=os.getenv("SHOPPING_MODEL", "gemini-3.1-flash-lite"),
)
```

The API credential is not passed as a source-code literal. Authentication comes from the environment.

The LLM instruction defines behavioral boundaries:

- Call the tool only for explicit redemption requests.
- Require both code and user ID.
- Never invent an identity.
- Never override tool errors.
- Never claim redemption without tool evidence.
- Never expose internal configuration.

These are useful behavioral controls, but they are not authorization controls. All enforceable rules remain inside Python.

## 9. Secure-development control layers

```text
Task request
    |
    v
Persistent project context
    |
    v
Security-aware implementation plan
    |
    v
Code and tests
    |
    +--> Agent command hook
    |
    +--> Ruff and Pytest
    |
    +--> Semgrep/pre-commit
    |
    v
Behavior traces and evaluation
```

Each control catches a different failure class. None is sufficient alone.

## 10. Persistent project context

`.agents/CONTEXT.md` defines the project’s paved roads:

1. Validate every tool with strict Pydantic schemas.
2. Do not execute raw shell commands without hook approval.
3. Treat failed hooks as refactoring tasks.
4. Keep authorization and transaction rules deterministic.
5. Never embed secrets.

The file also requires every implementation plan to contain a `Security Boundaries & Assertions` section.

This is useful for a capstone because it converts architectural choices into persistent development constraints. It reduces the chance that a later feature quietly bypasses earlier security decisions.

## 11. Security-aware planning

`implementation_plan.md` describes both implementation stages and security assertions.

The important pattern is to define tests before implementation for:

- Unauthorized identities.
- Invalid and malformed inputs.
- Repeated operations.
- Concurrent state changes.
- Model attempts to override policy.
- Credential leakage.
- Dangerous development commands.

A reusable plan section:

```markdown
## Security Boundaries & Assertions

- Trust boundary:
- Sensitive operation:
- Authoritative identity source:
- Validation schema:
- Authorization rule:
- Atomicity/idempotency rule:
- Expected failure outcomes:
- Audit evidence:
- Tests proving each boundary:
```

## 12. Agent command hook

`.agents/hooks.json` registers a `PreToolUse` hook for `run_command`:

```json
{
  "matcher": "run_command",
  "command": "python3 .agents/scripts/validate_tool_call.py",
  "timeout": 10
}
```

The validator reads JSON from standard input, extracts the command, normalizes whitespace, and returns:

- Exit `0` for approved commands.
- Exit `1` for blocked or malformed input.

It detects examples including:

- Recursive deletion of `/`.
- Filesystem formatting.
- Raw writes to devices.
- Shutdown/reboot commands.
- Shell fork bombs.
- Destructive commands chained after an apparently safe command.

The validator fails closed: invalid hook input is rejected rather than silently allowed.

### Limitation

A denylist cannot enumerate every dangerous command or encoding. Production engineering environments should combine:

- Sandboxed execution.
- Minimal filesystem permissions.
- Command allowlists for sensitive workflows.
- Network egress policy.
- Human approval for privileged actions.
- Disposable build environments.

## 13. Semgrep secret gate

The custom rule searches Python source for a Google API-key-shaped prefix:

```yaml
pattern-regex: 'AIzaSy[A-Za-z0-9_\-]*'
severity: ERROR
```

The pre-commit configuration runs Semgrep with `--error`. This flag converts findings into a nonzero exit code so a commit is blocked.

The codelab lifecycle is:

```text
Introduce controlled vulnerable code
        |
        v
Semgrep finds it and fails
        |
        v
Move credential loading to the environment
        |
        v
Rerun tests and scan
        |
        v
Zero findings
```

The final project contains no credential-shaped mock value in runnable code.

### Capstone hardening

Local hooks can be bypassed. Repeat these gates in CI using:

- Secret scanning across the entire Git history.
- Semgrep or another SAST tool.
- Dependency and lockfile scanning.
- Infrastructure-as-code scanning.
- Container-image scanning.
- Branch protection that requires the security job.

## 14. STRIDE skill

The local `stride-threat-model` skill instructs the coding agent to inspect:

- Entry points.
- Prompts and workflow edges.
- Tool functions.
- Identity and authorization.
- State and persistence.
- Hooks and configuration.
- External dependencies.

It assesses:

| STRIDE category | Question for this project |
|---|---|
| Spoofing | Can a caller claim another registered user ID? |
| Tampering | Can two requests redeem the same code? |
| Repudiation | Can a user dispute redemption without an audit trail? |
| Information disclosure | Can credentials or internal configuration leak? |
| Denial of service | Can requests exhaust model quota or tool capacity? |
| Elevation of privilege | Can prompt text override authorization logic? |

The resulting `threat_model.md` records current controls and residual risks. A good threat model does not label local hooks or prompts as unbypassable production controls.

## 15. Outcome-based TDD

The tests assert externally meaningful results and state changes rather than internal function-call counts.

Covered outcomes include:

- First redemption succeeds.
- Second redemption fails.
- Unknown codes fail.
- Guest and unknown users fail.
- Malformed codes and user IDs fail.
- Rejected requests do not mutate state.
- Code normalization works.
- Safe development commands pass.
- Destructive commands fail.

An automatic fixture resets the store around every test, preventing state leakage between cases.

Capstone testing rule:

- Use pytest for deterministic schemas, authorization, policy, state, hooks, and transactions.
- Use agent evaluation for tool selection, instruction following, semantic quality, and faithful reporting of tool results.
- Do not assert exact model prose in pytest.

## 16. Behavioral evaluation

The project generates two complete ADK traces:

1. Registered-user redemption succeeds.
2. Guest redemption is rejected.

The evaluation rubrics judge:

- Whether the agent calls the correct tool with exact arguments.
- Whether it faithfully reports the tool outcome.
- Whether it avoids overriding deterministic policy.

Trace generation uses the real model and real tool. Managed LLM grading requires Google Cloud project credentials, while deterministic trace assertions can run locally.

## 17. Observability and audit requirements

The codelab’s stable return strings are enough for demonstration, but production needs structured audit records.

Recommended redemption event:

```json
{
  "event_id": "uuid",
  "request_id": "uuid",
  "actor_id": "verified-user-id",
  "discount_code_hash": "...",
  "decision": "redeemed | rejected",
  "reason": "already_redeemed",
  "decision_source": "policy",
  "agent_run_id": "...",
  "tool_version": "...",
  "policy_version": "...",
  "timestamp": "..."
}
```

Do not record credentials, raw prompts containing sensitive data, or unnecessary personal information.

## 18. Production gaps

The following are intentionally demo-grade:

- Caller identity is supplied in prompt text.
- User records and discount state are in memory.
- The lock is process-local.
- No idempotency key exists.
- No persistent audit trail exists.
- No API rate limiting exists.
- Command filtering uses a denylist.
- Local hooks are bypassable.
- The UI/API authorization boundary is not implemented.

These should be treated as capstone implementation surfaces, not completed controls.

## 19. Reusable capstone architecture

Replace discount concepts with your domain:

| Shopping codelab | Generic capstone concept |
|---|---|
| Discount request | Privileged domain action |
| Registered user | Authenticated principal |
| Discount code | Protected resource or entitlement |
| Redeemed flag | Transactional state transition |
| Gemini shopping helper | Intent interpreter/orchestrator |
| Redemption tool | Deterministic application service |
| Store lock | Transaction boundary |
| Semgrep rule | Static security policy |
| STRIDE skill | Repeatable threat-model workflow |

Recommended flow:

```text
Authenticated request
      |
      v
Input schema and normalization
      |
      v
Deterministic authorization
      |
      v
Idempotency check
      |
      v
Transactional state change
      |
      v
Immutable audit event
      |
      v
Structured result returned to agent
```

## 20. Capstone implementation checklist

```text
Domain action:
Authenticated actor source:
Protected resource:
Strict input schema:
Deterministic authorization rule:
State transition:
Transaction mechanism:
Idempotency key:
Stable error taxonomy:
Model’s allowed responsibility:
Model’s prohibited responsibility:
Human-approval boundary:
Audit event schema:
Rate-limit policy:
Secret source:
Local security gates:
CI security gates:
STRIDE threats and mitigations:
Deterministic tests:
Behavioral eval cases:
```

## 21. Source map

- Agent and redemption logic: `app/agent.py`
- Secure development rules: `.agents/CONTEXT.md`
- Command gate configuration: `.agents/hooks.json`
- Command validator: `.agents/scripts/validate_tool_call.py`
- STRIDE skill: `.agents/skills/stride-threat-model/SKILL.md`
- Threat assessment: `threat_model.md`
- Security-aware plan: `implementation_plan.md`
- Semgrep rule: `.semgrep/rules.yaml`
- Pre-commit gates: `.pre-commit-config.yaml`
- Deterministic tests: `tests/test_agent.py`, `tests/test_tool_hook.py`
- Evaluation dataset: `tests/eval/datasets/basic-dataset.json`
- Trace generator: `tests/eval/generate_traces.py`
- Judge rubrics: `tests/eval/eval_config.yaml`
