# Ambient Agent Implementation Spec

## 1. Purpose

This document extracts the reusable architecture and logic from the CL4 ambient expense agent. It is intended as a design reference for a capstone project rather than an expense-specific product specification.

The core pattern is:

> Accept an event, sanitize it, apply deterministic policy, invoke an LLM only for ambiguous analysis, pause for a human when authority is required, then resume and record the decision.

The LLM advises. Python policy code and humans retain decision authority.

## 2. System boundaries

### Inputs

The agent accepts the same logical payload in three forms:

1. Direct Python dictionary.
2. JSON text from the ADK playground.
3. Pub/Sub-style event whose `data` field contains plain JSON or base64-encoded JSON.

Expense input schema:

```json
{
  "amount": 150.0,
  "submitter": "alice@company.com",
  "category": "software",
  "description": "IDE license",
  "date": "2026-06-06"
}
```

### Outputs

Low-risk deterministic branch:

```json
{
  "status": "approved",
  "route": "auto_approved"
}
```

Human-review branch:

```json
{
  "status": "approved | rejected",
  "route": "human_review",
  "security_event": false,
  "expense": {}
}
```

### External dependencies

- Google ADK 2.x `Workflow` graph API.
- Gemini for risk analysis on clean, high-value cases only.
- ADK/FastAPI server for local UI and Pub/Sub triggers.
- ADK session state for carrying sanitized data across nodes and pauses.

## 3. Architectural pattern

```text
Event / Pub/Sub
      |
      v
Security screen
  - decode and validate
  - redact PII
  - detect injection
      |
      v
Deterministic router
      |
      +-- injection detected ----------> Human approval
      |
      +-- amount < $100 ---------------> Auto-approve -> Complete
      |
      +-- amount >= $100 -> Gemini review -> Human approval
                                              |
                                              v
                                      Resume and record
```

The order is important. Security runs before routing and before the model. This creates one sanitized representation that all downstream nodes use.

## 4. Graph definition

The ADK graph is declared as data rather than implemented as nested control flow:

```python
Workflow(
    edges=[
        ("START", security_screen),
        (security_screen, route_expense),
        (
            route_expense,
            {
                "AUTO_APPROVE": auto_approve,
                "LLM_REVIEW": review_agent,
                "SECURITY_REVIEW": request_approval,
            },
        ),
        (review_agent, request_approval),
        (request_approval, process_decision),
    ]
)
```

Each node has one responsibility:

| Node | Type | Responsibility | Uses LLM |
|---|---|---|---|
| `security_screen` | Python function | Decode, validate, redact, detect injection | No |
| `route_expense` | Python function | Apply safety precedence and amount policy | No |
| `auto_approve` | Python function | Produce the low-value decision | No |
| `review_agent` | `LlmAgent` | Produce structured risk analysis | Yes |
| `request_approval` | Python generator | Emit `RequestInput` and pause | No |
| `process_decision` | Python generator | Interpret the human response and finish | No |

## 5. Data contracts

### Sanitized domain object

`ExpenseData` is the contract between input handling, policy, the model, and HITL:

```python
class ExpenseData(BaseModel):
    amount: float
    submitter: str
    category: str
    description: str
    date: str
    redacted_categories: list[str]
    injection_detected: bool
```

Using a typed schema provides validation, predictable serialization, and a defined boundary for model input.

### Model output

The LLM must return `RiskReview` rather than free text:

```python
class RiskReview(BaseModel):
    amount: float
    submitter: str
    category: str
    risk_level: str
    risk_factors: list[str]
    recommendation: str
```

This lets downstream code consume the review without parsing prose. In a capstone, replace free-form strings such as `risk_level` and `recommendation` with enums when possible.

## 6. Input normalization

The decoder follows this algorithm:

```text
if input is a dictionary:
    use it
else:
    extract text from ADK Content and parse JSON

if object contains "data":
    use object["data"]
else:
    treat the object itself as domain data

if data is a string:
    first try JSON parsing
    otherwise base64-decode it and parse JSON

require a JSON object
```

Capstone rule: normalize every transport into one internal domain schema at the system boundary. Workflow nodes should not need to know whether input arrived through Pub/Sub, HTTP, a scheduler, or the playground.

## 7. Security logic

### PII redaction

Regex patterns replace detected SSNs and card-like numbers with stable markers:

- `[REDACTED_SSN]`
- `[REDACTED_CREDIT_CARD]`

The code also records which categories were redacted. Downstream components receive only the sanitized object.

### Prompt-injection detection

The demo uses case-insensitive patterns for phrases such as:

- Ignore instructions or rules.
- Bypass a policy or approval control.
- Auto-approve or override approval.
- Reveal a system prompt or jailbreak.

### Safety precedence

Routing evaluates injection before business value:

```python
if injection_detected:
    route = "SECURITY_REVIEW"
elif amount >= threshold:
    route = "LLM_REVIEW"
else:
    route = "AUTO_APPROVE"
```

Therefore, even a low-value injection attempt cannot reach the automatic path.

### Capstone hardening

The regex controls are demonstrations, not production security. A capstone should consider:

- A dedicated DLP service for PII detection.
- Unicode normalization and obfuscation-resistant injection detection.
- Allowlisted input fields and strict maximum lengths.
- Authentication and authorization on trigger and approval endpoints.
- Secret-manager-backed credentials.
- Immutable audit records that contain sanitized data only.
- Security policy version recorded with each decision.

## 8. Deterministic policy versus model judgment

The project deliberately separates two kinds of reasoning.

### Deterministic code owns

- Threshold comparisons.
- Security precedence.
- Route selection.
- Automatic approval eligibility.
- Whether a human is required.
- Final application of the human decision.

### The LLM owns

- Identification of qualitative risk factors.
- Risk summary and recommendation.
- Analysis of vague or context-dependent descriptions.

The LLM cannot auto-approve high-value expenses. Its output always flows into `request_approval`.

Capstone rule: use code for rules that must be reproducible, testable, and auditable. Use the LLM for semantic ambiguity. Do not ask a prompt to enforce a rule that can be expressed in code.

## 9. State management

The security node emits:

```python
Event(
    output=sanitized_object,
    state={"expense_data": sanitized_object},
)
```

The event output feeds the next node. The state copy survives until the HITL and final-decision nodes need it.

Using an `Event` state delta is preferable to an untracked in-memory mutation because it is represented in workflow history and is replayable by the runtime.

For a capstone, define a state schema containing at least:

- Correlation/event ID.
- Sanitized request.
- Policy and prompt versions.
- Selected route.
- Model review, if any.
- Active interrupt ID.
- Human identity and decision.
- Timestamps and final status.

## 10. Human-in-the-loop lifecycle

`request_approval` yields a `RequestInput` event:

```python
RequestInput(
    interrupt_id="expense_approval",
    message="Expense requires manager approval.",
    payload={
        "expense": sanitized_expense,
        "security_event": boolean,
        "risk_review": optional_review,
    },
)
```

The runtime persists the interruption and stops the workflow. A UI or API later sends a function response with the same interrupt ID:

```json
{
  "decision": "approve"
}
```

The workflow resumes at `process_decision`.

The `App` must enable resumability:

```python
App(
    name="expense_agent",
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)
```

Capstone hardening:

- Use a unique interrupt ID per business object, not a single constant.
- Authenticate the reviewer and verify authorization for that object.
- Make resume operations idempotent.
- Reject duplicate or conflicting decisions.
- Define timeout, escalation, cancellation, and reassignment behavior.
- Persist sessions outside process memory.

## 11. Ambient trigger layer

The FastAPI entry point mounts the ADK application with Pub/Sub enabled:

```python
get_fast_api_app(
    agents_dir=AGENTS_DIR,
    web=True,
    trigger_sources=["pubsub"],
    otel_to_cloud=False,
)
```

ADK exposes:

```text
POST /apps/expense_agent/trigger/pubsub
```

Every event starts or associates a workflow session. Middleware converts a fully qualified subscription path such as:

```text
projects/acme/subscriptions/expense-review
```

into the short user/session identifier:

```text
expense-review
```

Capstone hardening:

- Validate Pub/Sub push authentication.
- Preserve a globally unique event ID for deduplication.
- Return quickly and process asynchronously when work may exceed push deadlines.
- Add retry and dead-letter behavior.
- Avoid rewriting private request attributes such as `request._body`; use a supported request/ASGI transformation.
- Separate transport identity from application user identity.

## 12. Observability

The implementation logs only decision metadata:

- Amount and category for automatic approval.
- Final human decision.

It avoids logging the original description. The workflow emits both:

1. `Event.content`, which is visible in the ADK UI.
2. `Event.output`, which feeds the graph and becomes the machine-readable result.

Recommended capstone fields:

- `event_id`
- `workflow_run_id`
- `node_name`
- `route`
- `latency_ms`
- `model_name`
- `model_called`
- `security_event`
- `decision_source` (`policy`, `model_advice`, or `human`)
- `final_status`

Never record raw secrets, PII, full model prompts, or unsanitized event payloads.

## 13. Evaluation strategy

The project tests five behavioral classes:

1. Low-value automatic approval.
2. Exact-threshold human review.
3. High-value manual approval.
4. PII redaction before model/HITL output.
5. Prompt-injection containment and model bypass.

The trace generator uses the real `InMemoryRunner`. When it encounters `expense_approval`, it resumes with a synthetic human response. It then serializes the complete execution trajectory.

Two LLM-as-judge metrics read the whole trace:

- `routing_correctness`
- `security_containment`

Deterministic unit tests separately verify exact thresholds, regex behavior, route precedence, and the no-LLM low-value path.

Capstone rule: use unit tests for deterministic code and trace evaluation for semantic agent behavior. Do not use brittle pytest assertions against model prose.

## 14. Reusable implementation sequence

For a different capstone domain, implement in this order:

1. Define the domain input and output schemas.
2. Normalize all transports into the input schema.
3. Sanitize untrusted content before persistence or model access.
4. Write deterministic policy and route names.
5. Implement non-LLM terminal branches.
6. Add narrowly scoped LLM nodes with structured outputs.
7. Add HITL at authority boundaries.
8. Add resumable application configuration and persistent sessions.
9. Mount event triggers.
10. Add idempotency, authentication, authorization, audit, and retry controls.
11. Test deterministic paths.
12. Generate full traces and grade behavioral requirements.

## 15. Capstone adaptation template

Replace the expense concepts using this mapping:

| Expense example | Generic capstone concept |
|---|---|
| Expense event | Domain event or job |
| Amount threshold | Deterministic policy boundary |
| PII screen | Input trust/safety boundary |
| Risk reviewer | Semantic analysis agent |
| Manager approval | Authorized human decision |
| Pub/Sub trigger | Event source or scheduler |
| Expense state | Typed workflow case state |

Fill in these decisions before coding:

```text
Domain event:
Trusted and untrusted fields:
Sanitization rules:
Deterministic routes:
Conditions that permit automation:
Conditions that require an LLM:
Conditions that require a human:
Structured model output:
Human roles and authorization:
Persistence/session service:
Idempotency key:
Retry and dead-letter behavior:
Audit fields:
Evaluation scenarios and pass criteria:
```

## 16. Source map

- Core workflow and policy: `expense_agent/agent.py`
- Model and threshold configuration: `expense_agent/config.py`
- Ambient server: `expense_agent/fast_api_app.py`
- Deterministic tests: `tests/unit/test_expense_workflow.py`
- Runner smoke test: `tests/integration/test_low_value_runner.py`
- Evaluation cases: `tests/eval/datasets/basic-dataset.json`
- Trace automation: `tests/eval/generate_traces.py`
- Judge rubrics: `tests/eval/eval_config.yaml`
