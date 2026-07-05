# Agent Runtime Deployment Implementation Spec

## 1. Purpose

This document extracts the reusable code and deployment architecture from the CL5 Agent Runtime codelab. It covers two related systems:

1. The ADK expense workflow and its deterministic/LLM/HITL logic.
2. The production boundary that packages that workflow for Google Agent Runtime.

The reusable principle is:

> Keep business behavior deployment-neutral, wrap it at the platform boundary, validate it locally, and deploy the exact tested application through reproducible configuration.

## 2. End-to-end architecture

```text
Client or frontend
       |
       v
Agent Runtime endpoint
       |
       v
AgentEngineApp (AdkApp wrapper)
       |
       v
ADK App
       |
       v
Expense Workflow
       |
       +-- under $100 ------> Python auto-approval
       |
       +-- $100 or more ----> Gemini risk review
                                  |
                                  v
                              RequestInput
                                  |
                                  v
                            Human decision
```

Supporting platform components:

```text
Source package ----> Agent Runtime
                         |
                         +--> Runtime service account
                         +--> Cloud Logging / Trace
                         +--> GCS artifact bucket
                         +--> BigQuery telemetry dataset
                         +--> Feedback operation
```

## 3. Separation of core and deployment code

The project keeps business behavior in:

```text
app/agent.py
```

Agent Runtime integration lives in:

```text
app/agent_runtime_app.py
```

The runtime wrapper imports the tested ADK app:

```python
from app.agent import app as adk_app

agent_runtime = AgentEngineApp(app=adk_app)
```

This means local execution and cloud execution share the same workflow object. The deployment layer does not duplicate the threshold, routing, prompt, or approval logic.

Capstone rule: do not maintain separate “local agent” and “production agent” implementations. Use one core application with thin environment-specific adapters.

## 4. Core workflow graph

```python
Workflow(
    edges=[
        ("START", parse_expense),
        (parse_expense, route_by_amount),
        (
            route_by_amount,
            {
                "AUTO_APPROVE": auto_approve,
                "NEEDS_REVIEW": review_agent,
            },
        ),
        (review_agent, request_approval),
        (request_approval, process_decision),
    ]
)
```

| Node | Type | Responsibility | Model call |
|---|---|---|---|
| `parse_expense` | Python | Decode and validate transport data | No |
| `route_by_amount` | Python | Enforce the $100 policy | No |
| `auto_approve` | Python | Finish low-value requests | No |
| `review_agent` | `LlmAgent` | Analyze qualitative risk | Yes |
| `request_approval` | Python generator | Interrupt for a manager | No |
| `process_decision` | Python generator | Apply the resumed human response | No |

## 5. Input normalization

The workflow accepts:

- Direct dictionaries.
- JSON strings.
- ADK `Content` objects.
- A `data`-wrapped payload.
- Base64-encoded JSON inside `data`.

Normalization algorithm:

```text
Convert ADK Content to text if necessary.
Parse the outer JSON object.
Use outer["data"] when present; otherwise use outer.
If data is text, try JSON parsing.
If that fails, base64-decode and parse JSON.
Validate the resulting object with ExpenseData.
Emit one normalized dictionary.
```

Internal workflow nodes therefore do not care how the request arrived.

## 6. Typed data contracts

### Expense input

```python
class ExpenseData(BaseModel):
    amount: float
    submitter: str
    category: str
    description: str
    date: str
```

The schema enforces nonnegative amounts and field length limits.

### Model output

```python
class RiskReview(BaseModel):
    risk_level: str
    risk_factors: list[str]
    recommendation: str
```

Structured model output prevents downstream HITL code from parsing arbitrary prose.

For a capstone, improve these string fields with enums and bounded collections:

```python
class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
```

## 7. Deterministic routing

The amount threshold is configuration-backed Python logic:

```python
route = (
    "NEEDS_REVIEW"
    if amount >= review_threshold
    else "AUTO_APPROVE"
)
```

The router emits both:

- `output`: normalized expense data for the next node.
- `state`: a durable workflow copy for the approval and final-decision nodes.

The LLM cannot change the route or lower the threshold.

Capstone rule: policies with exact, auditable semantics belong in deterministic code. The model should handle ambiguity, not authority.

## 8. Cost-aware LLM use

Expenses under $100 never invoke Gemini. The low-value path is:

```text
parse -> route -> auto_approve -> complete
```

Only high-value expenses pay model latency and token cost:

```text
parse -> route -> review_agent -> human approval
```

This is a reusable optimization pattern: place inexpensive deterministic filters before costly probabilistic nodes.

## 9. Human-in-the-loop lifecycle

`RequestInput` interrupts execution:

```python
RequestInput(
    interrupt_id="expense_approval",
    message="Expense requires manager approval.",
    payload={
        "expense": saved_expense,
        "risk_review": structured_review,
    },
)
```

The `App` enables resumability:

```python
ResumabilityConfig(is_resumable=True)
```

On resume, `process_decision` reads the human response and produces the final status.

Production improvements:

- Use an interrupt ID unique to the business case.
- Authenticate and authorize the reviewer.
- Record reviewer identity and timestamp.
- Make decisions idempotent.
- Reject duplicate or conflicting responses.
- Define expiration, reassignment, and escalation.
- Persist session state across instances and restarts.

## 10. ADK event outputs

Function nodes emit two kinds of events:

1. `Event.content` for a human-visible response.
2. `Event.output` for graph propagation and machine-readable state.

```python
yield Event(content=Content(...))
yield Event(output=result)
```

Without `content`, a function node may execute correctly but appear blank in a playground or client UI.

## 11. Agent Runtime adapter

`AgentEngineApp` subclasses `AdkApp` and provides the production integration surface.

### `set_up`

Initializes:

- Vertex AI client state.
- OpenTelemetry instrumentation.
- Base `AdkApp` services.
- Standard Python logging.
- Cloud Logging client.
- Gemini location environment.

### `register_operations`

Extends the operations exposed by Agent Runtime with:

```text
register_feedback
```

### `register_feedback`

Validates feedback using a Pydantic `Feedback` schema and writes a structured Cloud Logging entry.

### `clone`

Returns the application instance required by the runtime template’s lifecycle.

## 12. Artifact service selection

The wrapper selects artifact storage dynamically:

```python
GcsArtifactService(bucket_name=LOGS_BUCKET_NAME)
if LOGS_BUCKET_NAME
else InMemoryArtifactService()
```

This supports:

- In-memory local behavior without cloud dependencies.
- Persistent GCS artifacts when the runtime injects a bucket name.

Capstone rule: use in-memory services only as development fallbacks. Production artifacts need persistence, retention, encryption, access control, and lifecycle policy.

## 13. Source-based deployment

Agent Runtime uses source deployment rather than a Docker image.

Packaging flow:

```text
pyproject.toml + uv.lock
          |
          v
uv export -> requirements file
          |
          v
Source archive
          |
          v
Agent Runtime create/update
          |
          v
deployment_metadata.json
```

The runtime Python entrypoint is:

```text
module: app.agent_runtime_app
object: agent_runtime
```

The Terraform scaffold uses Python 3.12 for Agent Runtime even though local development currently runs Python 3.11. This makes dependency compatibility across both versions a release requirement.

## 14. Agents CLI manifest

`agents-cli-manifest.yaml` tells the CLI:

```yaml
name: expense-agent
agent_directory: app
region: us-west1
deployment_target: agent_runtime
cicd_runner: skip
```

The manifest is operational configuration, not documentation. Agents CLI reads it to select packaging and deployment behavior.

The ADK `App` name still must match the agent directory:

```python
App(name="app", ...)
```

## 15. Deployment metadata

Before deployment:

```json
{
  "remote_agent_runtime_id": "None",
  "deployment_timestamp": "None"
}
```

After deployment, Agents CLI writes the remote reasoning-engine resource name and timestamp. Subsequent deployments use that ID to update rather than create a second engine.

Capstone safeguards:

- Treat the metadata file as environment-specific state.
- Do not copy production engine IDs into unrelated environments.
- Verify the target project and region encoded in the resource name.
- If a deployment times out, check operation status before retrying creation.

## 16. Terraform Agent Runtime resource

The generated resource is:

```text
google_vertex_ai_reasoning_engine
```

It configures:

- Display name and region.
- ADK framework.
- Runtime service account.
- Scaling and resource limits.
- Environment variables.
- Inline bootstrap source.
- Python entrypoint and requirements.

Terraform intentionally ignores later changes to `source_code_spec`:

```hcl
lifecycle {
  ignore_changes = [spec[0].source_code_spec]
}
```

This avoids Terraform overwriting source deployed by Agents CLI or CI/CD. Terraform owns infrastructure; the deployment pipeline owns application source.

## 17. Bootstrap source pattern

Terraform creates the reasoning-engine resource using a small base64-encoded dummy archive. The actual application source is uploaded later by the deployment command.

This separates:

- Infrastructure creation.
- Application release.

The separation is useful, but ownership must be documented clearly to avoid two systems repeatedly overwriting each other.

## 18. Runtime identity and IAM

Terraform creates an application service account:

```text
expense-agent-app@PROJECT.iam.gserviceaccount.com
```

It grants configured application roles to:

- The application service account.
- The Vertex AI platform service identity.

Production guidance:

- Review the exact `app_sa_roles` list before applying.
- Remove wildcard or unnecessary project-wide roles.
- Separate deployment identity from runtime identity.
- Grant `iam.serviceAccountUser` only to approved deployers.
- Grant Secret Manager access only for required secrets.
- Use separate service accounts for dev, staging, and production.

## 19. Storage and artifacts

Terraform creates a regional GCS bucket:

```text
PROJECT-expense-agent-logs
```

It enables uniform bucket-level access and passes the bucket name to Agent Runtime through `LOGS_BUCKET_NAME`.

Capstone additions:

- Public-access prevention.
- Customer-managed encryption key if required.
- Retention and lifecycle rules.
- Separate raw, sanitized, and derived-data prefixes.
- Access logging and data-classification labels.
- Region aligned with data-residency requirements.

## 20. Telemetry architecture

The generated infrastructure creates:

- Cloud Logging sinks.
- BigQuery telemetry dataset.
- BigQuery connection to GCS.
- External completions table.
- GenAI log table.
- A view joining logs and completion content.
- Feedback export.

Data flow:

```text
Agent/model telemetry
       |
       +--> Cloud Logging
       |        |
       |        v
       |     BigQuery sink
       |
       +--> GCS completion records
                |
                v
        BigQuery external table
                |
                v
        Joined analytics view
```

## 21. Message-content capture risk

The generated runtime configuration sets:

```text
OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
```

This can make prompts and model outputs available to telemetry pipelines. That is valuable for debugging and evaluation, but it may capture:

- Personal information.
- Financial details.
- Customer data.
- Internal instructions.
- Tool arguments and outputs.

Before production, decide explicitly whether message capture is permitted. If enabled:

- Redact before logging.
- Limit IAM access.
- Define retention and deletion.
- Document user consent and legal basis.
- Separate production analytics from developer access.
- Test that secrets and sensitive fields never enter spans.

## 22. Configuration drift: CLI versus Terraform

The verified Agents CLI dry run uses defaults:

| Setting | CLI dry run |
|---|---:|
| CPU | 1 |
| Memory | 4 GiB |
| Minimum instances | 1 |
| Maximum instances | 10 |
| Concurrency | 8 |
| Workers | 1 |

The generated Terraform service currently declares:

| Setting | Terraform |
|---|---:|
| CPU | 4 |
| Memory | 8 GiB |
| Minimum instances | 1 |
| Maximum instances | 10 |
| Concurrency | 9 |

This is configuration drift. The effective values depend on which deployment path owns the runtime spec.

Capstone rule: define one sizing source of truth or enforce an automated comparison before deployment. Do not assume a successful dry run validates optional Terraform values.

## 23. Scaling relationships

Runtime sizing parameters are coupled:

- More workers generally require more CPU.
- Higher concurrency increases peak memory.
- Minimum instances affect readiness and cost behavior.
- Maximum instances cap throughput and spending.
- LLM waiting time means async concurrency can be useful, but every active request retains state and buffers.

Tune with load tests and measure:

- Median, p95, and maximum latency.
- Memory high-water mark.
- OOM/restart count.
- Model-call latency.
- Concurrent HITL/session count.
- Error and throttling rate.
- Cost per completed task.

## 24. Region model

The runtime target is `us-west1`. Gemini model routing may use `global`.

These are distinct settings:

```text
Runtime region: where the Agent Runtime service executes.
Model location: where Gemini API requests are routed.
Telemetry/storage region: where logs and artifacts reside.
```

For regulated or residency-sensitive workloads, confirm that all three satisfy the same policy. “Global” model routing may not be acceptable even when runtime storage is regional.

## 25. Deployment workflow

Safe sequence:

```text
1. Validate project specification.
2. Run unit and integration tests.
3. Run behavioral evaluation.
4. Lock dependencies.
5. Validate Agent Runtime wrapper import.
6. Run deployment dry run.
7. Review project, region, identity, secrets, sizing, and telemetry.
8. Obtain explicit deployment approval.
9. Deploy with --no-wait.
10. Poll deployment status.
11. Record deployment metadata.
12. Test remote low- and high-value paths.
13. Inspect logs and traces.
```

Actual deployment command:

```bash
agents-cli deploy \
  --project YOUR_PROJECT_ID \
  --region us-west1 \
  --no-wait
```

Status check:

```bash
agents-cli deploy --status \
  --project YOUR_PROJECT_ID \
  --region us-west1
```

Do not retry a timed-out deployment blindly. The operation may still be creating the engine.

## 26. Deployment gates

Do not deploy until all are true:

- Tests pass.
- Behavioral evaluations meet thresholds.
- Dependency lock is current.
- Project and billing account are confirmed.
- Runtime and model regions are approved.
- Service-account roles are reviewed.
- Secret sources are configured.
- Message-content telemetry is approved or disabled.
- Runtime sizing is reconciled.
- Rollback/fix-forward procedure is documented.
- A human explicitly approves the external deployment.

## 27. Remote testing

After deployment, test both policy paths against the returned Agent Runtime resource:

```bash
agents-cli run \
  --url RESOURCE_URL \
  --mode adk \
  '{"data":{"amount":50,...}}'
```

High-value testing must confirm:

- `NEEDS_REVIEW` route.
- Structured model review.
- `RequestInput` interruption.
- Session can resume.
- Human response controls final status.
- Trace and logs contain the expected node sequence.

## 28. Evaluation strategy

The project preserves two complete local traces:

1. $50 automatic approval.
2. $150 Gemini review followed by HITL approval.

Direct assertions verify node paths and route events. LLM-as-judge rubrics assess:

- Routing correctness.
- Human decision authority.

Pytest covers deterministic policy and wrapper structure. It does not assert model wording.

## 29. Agent Runtime versus ambient triggers

Despite the “ambient expense agent” name, Agent Runtime is request-driven and does not expose Pub/Sub, Eventarc, or Cloud Scheduler trigger endpoints.

Deployment choices:

| Requirement | Recommended target |
|---|---|
| Managed conversational agent and sessions | Agent Runtime |
| Pub/Sub/Eventarc/Cloud Scheduler triggers | Cloud Run |
| Kubernetes control or custom jobs | GKE |

Possible split architecture:

```text
Pub/Sub -> Cloud Run ingestion service -> Agent Runtime
```

Use that split only when managed Agent Runtime capabilities justify the extra network hop, identity boundary, failure mode, and cost.

## 30. Rollback model

Agent Runtime does not provide Cloud Run-style revision traffic shifting. The primary recovery path is fix-forward:

1. Identify the failing deployment and preserve evidence.
2. Revert or fix application source.
3. Rerun tests and evaluation.
4. Redeploy to the existing runtime ID.

For high-risk releases, consider a second reasoning engine for blue/green testing and switch clients only after validation.

## 31. Capstone adaptation map

| Expense codelab | Generic capstone concept |
|---|---|
| Expense JSON | Domain request |
| $100 threshold | Deterministic policy gate |
| Risk reviewer | Semantic analysis node |
| Manager approval | Human authority boundary |
| `AdkApp` wrapper | Managed-platform adapter |
| Runtime service account | Workload identity |
| GCS logs bucket | Persistent artifacts |
| BigQuery telemetry | Operational analytics |
| Deployment metadata | Environment release state |

## 32. Capstone implementation checklist

```text
Core domain workflow:
Deterministic policy gates:
Model-only responsibilities:
Human decision boundaries:
Input and output schemas:
State and resumability model:
Local application name/directory:
Runtime adapter entrypoint:
Deployment target and region:
Model location:
Runtime service account:
Required IAM roles:
Secret source and bindings:
Artifact service:
Session service:
Telemetry fields:
Message-content capture policy:
Retention policy:
Runtime sizing source of truth:
Dependency lock and Python versions:
Unit/integration tests:
Behavioral eval thresholds:
Dry-run evidence:
Remote test cases:
Rollback/fix-forward plan:
Deployment approval owner:
```

## 33. Source map

- Core graph: `app/agent.py`
- Runtime configuration: `app/config.py`
- Agent Runtime wrapper: `app/agent_runtime_app.py`
- Telemetry setup: `app/app_utils/telemetry.py`
- CLI project manifest: `agents-cli-manifest.yaml`
- Remote runtime state: `deployment_metadata.json`
- Runtime Terraform: `deployment/terraform/single-project/service.tf`
- IAM: `deployment/terraform/single-project/iam.tf`
- Storage: `deployment/terraform/single-project/storage.tf`
- Telemetry and analytics: `deployment/terraform/single-project/telemetry.tf`
- Terraform environment values: `deployment/terraform/single-project/vars/env.tfvars`
- Deterministic tests: `tests/unit/test_expense_policy.py`
- Local graph test: `tests/integration/test_low_value_runner.py`
- Wrapper tests: `tests/integration/test_agent_runtime_app.py`
- Evaluation traces: `tests/eval/generate_traces.py`
- Judge rubrics: `tests/eval/eval_config.yaml`
- Deployment runbook: `README.md`
- Readiness checklist: `DEPLOYMENT_READINESS.md`
