# Capstone Implementation Spec: Human-in-the-Loop Agent Frontend

## 1. What this codelab demonstrates

This project adds an operational frontend to an ADK workflow that can pause for a human decision. The dashboard is not the agent itself. It is a small control plane that:

1. discovers Agent Runtime sessions containing unresolved `adk_request_input` calls;
2. presents the request and its risk context to a manager;
3. sends a matching function response back to the same session; and
4. displays the agent's final response after execution resumes.

The reusable capstone pattern is **agent interrupt -> durable session state -> reviewer UI -> correlated response -> resumed workflow**.

## 2. Runtime architecture

```text
Expense producer
      |
      v
 Pub/Sub topic ----OIDC push----> Agent Runtime / ADK workflow
                                      |
                                      | adk_request_input call
                                      v
                              Agent Platform session
                                      ^
                                      |
Manager browser -> Cloud Run dashboard -> session scan / correlated response
```

The repository separates the concerns cleanly:

- `static/index.html`: browser UI, polling, cards, modal, and actions.
- `dashboard/main.py`: HTTP API, interrupt extraction, and runtime adapters.
- `infra/`: Cloud Run, IAM, Pub/Sub, retry, and dead-letter resources.
- `tests/`: deterministic checks for interrupt matching and API behavior.

## 3. Application contract

### HTTP endpoints

| Route | Purpose |
|---|---|
| `GET /` | Serve the manager dashboard. |
| `GET /api/pending` | Return unresolved approval requests. |
| `POST /api/action/{session_id}` | Approve or reject one interrupt. |
| `GET /healthz` | Report liveness and configured mode. |

Action request:

```json
{
  "approved": true,
  "interrupt_id": "expense-alice"
}
```

The URL identifies the conversation; `interrupt_id` identifies the exact paused tool call inside it. Both are required because a session may contain many calls over time.

### Pending item view model

```json
{
  "session_id": "session-alice",
  "interrupt_id": "expense-alice",
  "message": "Expense requires manager approval.",
  "expense": {
    "amount": 250,
    "submitter": "alice@company.com",
    "category": "travel",
    "description": "NYC flight tickets",
    "date": "2026-04-12"
  },
  "risk_review": {
    "risk_level": "medium",
    "risk_factors": ["High-value travel"],
    "recommendation": "Approve after confirming itinerary"
  }
}
```

This is deliberately a UI-facing model. Do not make the frontend understand raw ADK event histories.

## 4. Core event-resolution logic

`extract_pending(session)` is the most reusable logic in the project. It performs a correlation join over the event stream:

1. iterate through every event and content part;
2. collect each `adk_request_input` function call by its ID;
3. collect each `adk_request_input` function response by its ID;
4. return calls whose IDs are absent from the response set.

In compact form:

```text
pending = request_calls_by_id - response_ids
```

The parser accepts both `function_call`/`function_response` and `functionCall`/`functionResponse`, which makes it tolerant of Python-model and JSON-API representations. It also accepts an object with `model_dump()` or an ordinary dictionary and parses stringified payload JSON.

Important invariant: a response resolves a request only when the function name and interrupt ID match. Matching merely on session, timestamp, expense, or latest event can resume the wrong operation.

## 5. Resuming the agent

The Vertex adapter submits a function response as a new user message to the original runtime session:

```python
message = {
    "role": "user",
    "parts": [{
        "function_response": {
            "id": interrupt_id,
            "name": "adk_request_input",
            "response": {
                "approved": approved,
                "decision": "approve" if approved else "reject",
            },
        }
    }],
}
```

The adapter calls `async_stream_query` using the original `session_id` and the same `user_id` that owns the session. It consumes the stream and chooses the last textual event as the manager-facing result.

For a capstone implementation, preserve all four correlation fields:

- runtime resource;
- application/user ownership;
- session ID;
- interrupt/function-call ID.

Changing any of these can create a new conversation or leave the original workflow paused.

## 6. Adapter pattern

`SessionGateway` isolates the application from its storage/runtime provider:

```python
async def pending() -> list[dict]: ...
async def act(session_id, interrupt_id, approved) -> dict: ...
```

Two implementations use the same contract:

- `MockSessionGateway` provides production-shaped local data and removes an item after a decision.
- `VertexSessionGateway` reads Agent Platform sessions and resumes Agent Runtime.

This boundary lets the UI and HTTP tests run without Google Cloud credentials. In a capstone, it also provides a seam for a database-backed approval queue, test double, or different agent host.

## 7. Frontend behavior

The frontend is intentionally framework-free. It:

- polls `/api/pending` every five seconds;
- renders expense and security context as review cards;
- disables actions and shows progress while a request is running;
- posts the manager decision with the interrupt ID;
- refreshes the pending list after success; and
- opens a result modal containing the resumed workflow summary.

Treat the browser as an untrusted client. The backend must independently verify that the session and interrupt are still pending and that the signed-in reviewer is authorized to decide them.

## 8. Cloud and delivery logic

### Dashboard deployment

The FastAPI service is containerized and configured for port `8080`. Terraform deploys it to Cloud Run using a dedicated service account with `roles/aiplatform.user`. Runtime configuration is injected through environment variables:

- `DASHBOARD_MODE=vertex`
- `GOOGLE_CLOUD_PROJECT`
- `GOOGLE_CLOUD_LOCATION`
- `AGENT_RUNTIME_ID`

The default Terraform setting keeps Cloud Run private. That is the correct baseline for a manager console.

### Event delivery

Terraform creates:

- an expense topic;
- a push subscription;
- an OIDC identity permitted to call Vertex AI;
- a ten-minute acknowledgement deadline;
- exponential retry backoff; and
- a dead-letter topic after five delivery attempts.

The push subscription uses `no_wrapper`, so the published bytes become the HTTP request body instead of the normal Pub/Sub envelope. Therefore the producer must publish the exact JSON body expected by the Agent Runtime `:query` endpoint. OIDC authentication only proves caller identity; it does not translate the payload into an Agent Runtime query.

Before using this pattern in a capstone, validate the runtime endpoint's response time and request schema. A safer production alternative is a small ingestion service that validates the event, creates an idempotency key, invokes the runtime API, and returns a prompt acknowledgement to Pub/Sub.

## 9. Production gaps to address

### Authentication and authorization

Do not expose the manager dashboard with `allUsers`. Put it behind IAP, an identity-aware reverse proxy, or application authentication. Authorize by role and approval scope, not just successful login.

### Decision integrity

Add:

- one-time/idempotent decision records keyed by session and interrupt ID;
- compare-and-set semantics so two reviewers cannot both decide;
- CSRF protection for browser actions;
- immutable audit entries for reviewer, decision, reason, timestamp, and request hash;
- optional rejection/approval comments; and
- server-side revalidation immediately before resume.

### Scale

The sample lists every session and then fetches each full history concurrently. This is acceptable for a lab but becomes expensive as sessions and event histories grow. For production, write approval requests into an indexed queue/table when the interrupt is created, and update that record when it is resolved. The dashboard should query this read model rather than reconstructing state from all sessions every five seconds.

### Ownership model

The sample hard-codes `user_id="default-user"`. A capstone should define whether sessions belong to the submitter, an organization, or a service principal. Persist that ownership with the approval record and use it consistently during lookup and resume.

### Failure handling

Distinguish these cases in the API and UI:

- pending request no longer exists;
- another reviewer already decided it;
- runtime invocation failed before acceptance;
- runtime accepted the decision but streaming disconnected;
- agent resumed but downstream work failed.

Avoid blindly retrying a decision unless resume is idempotent.

## 10. Suggested capstone data model

```text
ApprovalRequest
  id                    internal stable ID
  runtime_resource      target deployed agent
  app_name / user_id    session ownership
  session_id            conversation to resume
  interrupt_id          paused function-call ID
  request_type          expense_approval, access_review, etc.
  payload_json          normalized review data
  status                pending | approved | rejected | expired | failed
  requested_at
  decided_at
  decided_by
  decision_reason
  version               optimistic concurrency token
```

Store only the normalized data needed by the reviewer plus references to the authoritative event/session. Sensitive prompt or tool content should be minimized and redacted before display.

## 11. Testing strategy

The included tests verify the central behavior:

- a matching response removes only the correlated interrupt;
- the page and pending endpoint are reachable;
- approval removes the mock item; and
- an unknown action returns `404`.

Add these capstone tests:

- multiple unresolved interrupts in one session;
- duplicate calls/responses and out-of-order events;
- malformed or stringified payloads;
- rejection path and runtime stream failure;
- two simultaneous reviewers;
- authentication, authorization, and CSRF;
- Pub/Sub duplicate delivery and dead-letter behavior;
- full browser flow from pending card to result modal; and
- contract tests against a staging Agent Runtime.

## 12. Implementation sequence for the capstone

1. Define the interrupt payload and decision response schemas.
2. Make the agent emit `adk_request_input` with a stable unique ID.
3. Persist an indexed approval record when the agent pauses.
4. Implement a provider-neutral approval gateway.
5. Build authenticated list/detail/decision endpoints.
6. Resume the exact session with a matching function response.
7. Add idempotency, optimistic concurrency, and audit logging.
8. Build the reviewer UI and accessible status/error states.
9. Test duplicate, stale, unauthorized, and partial-failure cases.
10. Deploy privately, monitor latency/errors, and rehearse rollback.

## 13. Source map

- `dashboard/main.py`: settings, event parsing, gateways, and FastAPI routes.
- `static/index.html`: review experience and client-side state transitions.
- `tests/test_dashboard.py`: executable examples of the event and API contracts.
- `Dockerfile`: portable service packaging.
- `infra/main.tf`: runtime IAM, Cloud Run, Pub/Sub delivery, retry, and dead-letter wiring.
- `infra/variables.tf`: deploy-time inputs and secure unauthenticated default.
- `DEPLOYMENT_READINESS.md`: deployment boundary and prerequisites.

## 14. Key takeaway

The frontend is the visible part, but the essential engineering idea is correlation. A human decision is safe only when it is authorized, recorded once, and returned as the exact function response for the exact paused call in the exact session. Build that invariant first; the dashboard can then evolve independently around it.
