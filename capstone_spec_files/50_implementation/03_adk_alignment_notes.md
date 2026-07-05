# Codelab Alignment and ADK Upgrade Spec

Version: 0.2  
Status: Approved for incremental implementation  
Supersedes: The "simple orchestrator is sufficient" target in `03_agent_architecture.md`  
Preserves: Existing deterministic actuarial tools, schemas, security functions, reports, traces, datasets, and tests

## 1. Decision

The project will be upgraded in place from a fixed Python pipeline with direct Gemini synthesis to a recognizable Google ADK application. It will not be rebuilt from scratch.

The target boundary is:

```text
ADK controls investigation orchestration and tool selection.
Deterministic Python tools calculate and validate every number.
An LLM interprets only structured, trusted tool results.
CLI and FastAPI are adapters into the same ADK application.
```

The local CLI remains the canonical judge demo. FastAPI provides a deployable HTTP surface. Cloud deployment, ambient triggers, and a manager dashboard remain optional until explicitly authorized.

## 2. Why this change is required

The current implementation has strong deterministic tools, security tests, reports, and specifications, but its execution order is fixed and Gemini is used only for final prose. The upgrade makes course concepts visible in executable code:

- `google.adk` agent and app primitives;
- a canonical `root_agent`;
- schema-bound function tools;
- agent callbacks for policy and observability;
- session state and ADK event traces;
- Agent Skills used by the runtime;
- Agents CLI evaluation of tool trajectory and response quality; and
- FastAPI packaging consistent with the codelabs.

## 3. Current-to-target gap matrix

| Area | Current state | Target state | Priority |
|---|---|---|---|
| Orchestration | Fixed calls in `portfolio_agent/run.py` | ADK `root_agent` selects bounded investigation tools after deterministic validation | Required |
| Numerical truth | Deterministic functions | Preserved unchanged behind JSON-serializable ADK adapters | Required |
| LLM integration | Direct `google-genai` synthesis call | ADK `Agent`/`LlmAgent` with structured, trusted context | Required |
| Skill | Portfolio skill stored only in specs | Runtime skill at `skills/portfolio_monitoring/` and reflected in agent instruction | Required |
| Offline demo | Documented flag does not exist | `--force-offline` performs zero model/network calls and emits deterministic report | Required |
| HTTP surface | None | `portfolio_agent/fast_api_app.py` with health and review endpoints | Required |
| Security | Function-level checks | Existing checks plus before-model, before-tool, and after-tool callbacks | Required |
| Human review | Boolean flag | Deterministic review decision object; true pause/resume only if a consequential action is later added | Required |
| Evaluation | Pytest plus scenario-specific mock memos | Pytest for code; Agents CLI generate/grade for behavior; deterministic trace metrics | Required |
| Trace | Pipeline milestones | ADK session/run IDs, function calls/responses, duration, policy decisions, and artifacts | Required |
| Packaging | Minimal Python package | Makefile, Dockerfile, manifest, config module, ADK app, locked dependencies | Required |
| Cloud deployment | Documented future work | Optional after local eval gate and explicit deployment approval | Optional |
| Ambient execution | None | Optional Pub/Sub/Eventarc trigger through ADK FastAPI on Cloud Run/GKE | Optional |
| Manager dashboard | None | Optional only if a real approval/resume use case is added | Optional |

## 4. Target repository structure

```text
portfolio-monitoring-agent/
├── .agents-cli-spec.md
├── .env.example
├── agents-cli-manifest.yaml
├── Dockerfile
├── Makefile
├── README.md
├── pyproject.toml
├── uv.lock
├── portfolio_agent/
│   ├── __init__.py
│   ├── agent.py              # root_agent and ADK App
│   ├── callbacks.py          # ADK safety and trace callbacks
│   ├── config.py             # model, paths, thresholds, execution mode
│   ├── fast_api_app.py       # HTTP adapter only
│   ├── run.py                # CLI adapter only
│   ├── schemas.py
│   ├── security.py
│   ├── tools.py              # existing deterministic engine
│   ├── adk_tools.py          # JSON-safe wrappers exposed to the model
│   ├── reporting.py
│   └── tracing.py
├── skills/
│   └── portfolio_monitoring/
│       ├── SKILL.md
│       ├── references/
│       └── assets/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── eval/
│       ├── datasets/
│       └── eval_config.yaml
├── data/
├── outputs/
└── artifacts/
```

`agents-cli scaffold enhance .` is the preferred way to introduce standard Agents CLI files during implementation. Generated changes must be reviewed before they replace existing configuration.

Phase 1 scaffolding is a structure-recognition step only. If the scaffold generates placeholder tests, package imports, or server files that assume a completed `root_agent`, live ADK runner, Google Cloud credentials, or FastAPI review API before those phases are implemented, treat them as reference material and either remove them or quarantine them until the matching implementation phase. Phase 1 must preserve the existing deterministic test suite rather than forcing Phase 6/8 behavior early.

Package imports must remain side-effect-light during the transition. Importing `portfolio_agent.tools`, `portfolio_agent.security`, or other deterministic modules must not require importing a not-yet-built ADK `app`, initializing Google credentials, or constructing model/network clients.

## 5. Target agent design

### 5.1 Root agent

`portfolio_agent/agent.py` must export `root_agent`. The root agent owns the user-facing review task and may invoke only approved ADK tool wrappers.

Required behavior:

1. Accept a normalized review request.
2. Require validation before analytical tools.
3. Use deterministic results as the sole source of numeric facts.
4. Investigate only anomalies returned by the anomaly tool.
5. Select relevant dimensions rather than automatically slicing every dimension.
6. Separate observations from hypotheses.
7. Return a structured review result and user-facing summary.

### 5.2 Deterministic control boundary

Input path authorization, CSV loading, schema validation, metric calculation, threshold evaluation, report validation, and artifact paths must never depend on LLM judgment.

The LLM may decide which approved driver dimensions to inspect, but it may not:

- provide raw dataframe operations;
- change threshold values without an authorized configuration object;
- calculate or overwrite metrics;
- invent unavailable metrics;
- write arbitrary paths; or
- invoke external side effects.

### 5.3 ADK application and state

The application name must match the agent directory name: `portfolio_agent`.

Session state keys:

| Key | Purpose |
|---|---|
| `review_request` | Validated input request. |
| `dataset_ref` | Opaque reference to the authorized loaded dataset. |
| `data_quality` | Structured validation result. |
| `metrics` | Deterministic metrics records. |
| `anomalies` | Deterministic anomaly records. |
| `driver_results` | Results for selected dimensions. |
| `security_flags` | Sanitized policy events. |
| `review_decision` | Required/reasons/reviewer object. |
| `report_result` | Final artifact paths and status. |

State initialization must occur in a `before_agent_callback` so first-turn state references cannot fail.

## 6. Delivery adapters

### 6.1 CLI

The CLI must invoke the same ADK app used by FastAPI.

Required modes:

- Online: ADK runner with configured Gemini provider.
- Offline: deterministic orchestration and template synthesis with no network/model initialization.

Required command:

```bash
uv run python -m portfolio_agent.run \
  --input tests/golden/loss_ratio_spike.csv \
  --latest-month 2026-06 \
  --force-offline
```

### 6.2 FastAPI

`fast_api_app.py` is an adapter, not a business-logic module.

Required endpoints:

| Method and path | Contract |
|---|---|
| `GET /healthz` | Process liveness; no external dependency required. |
| `GET /readyz` | Configuration and runtime readiness without exposing secrets. |
| `POST /api/reviews` | Submit an approved local/demo dataset reference and return a structured review result. |

File upload is not required for the first upgrade. If later added, size, content type, filename, storage path, and cleanup must be validated.

### 6.3 Ambient triggers

Ambient execution is a later option. If implemented, use the ADK FastAPI trigger surface for Pub/Sub/Eventarc on Cloud Run or GKE. Agent Runtime is not the target for scheduled/event trigger endpoints. No ambient infrastructure may be provisioned without explicit approval.

## 7. Security callback contract

| Callback | Required responsibility |
|---|---|
| `before_agent_callback` | Initialize state, attach run metadata, and normalize execution mode. |
| `before_model_callback` | Ensure only sanitized tool results enter model context; block prompt disclosure and unsafe overrides. |
| `before_tool_callback` | Enforce tool allowlist, argument schema, path policy, and workflow prerequisites. |
| `after_tool_callback` | Validate JSON-safe response, redact unsafe text, attach timing/status, and reject numerical contract violations. |
| `after_model_callback` | Validate output safety and prevent unsupported/binding recommendations. |

Callbacks may block or replace unsafe operations. They must not silently convert failed calculations into successful results.

## 8. Human-review semantics

For the MVP, human review is an explicit structured decision—not a claim of interactive approval:

```yaml
required: true
reasons:
  - high_severity_loss_ratio_anomaly
status: pending
recommended_reviewer: actuary_or_portfolio_owner
```

The report may be generated while review is pending because it is an advisory artifact. No notification, database write, pricing change, or other consequential action is allowed.

If a consequential tool is added later, the application must enable ADK resumability and use tool confirmation or `request_input` with an exact interrupt ID. That is outside the current required upgrade.

## 9. Evaluation model

Testing is divided into non-overlapping layers:

| Layer | Purpose | Command |
|---|---|---|
| Pytest unit | Exact formulas, schemas, path policy, callbacks, and adapters | `make test` |
| Pytest integration | ADK runner/session events and offline network isolation | `make integration` |
| ADK inference | Produce genuine agent traces from eval prompts | `agents-cli eval generate` |
| ADK grading | Grade task success, tool use, trajectory, grounding, safety, and domain rules | `agents-cli eval grade` |
| Regression comparison | Detect improvement or regression after a change | `agents-cli eval compare` |

Pytest must not assert variable LLM prose. Scenario-specific mock memos may test report rendering, but they cannot be presented as evidence that agent behavior passed evaluation.

Minimum behavioral metrics:

- `multi_turn_task_success`;
- `multi_turn_tool_use_quality`;
- `multi_turn_trajectory_quality`;
- `final_response_quality`;
- `hallucination`;
- `safety`;
- custom deterministic metric-consistency and trace-completeness checks.

## 10. Implementation sequence

1. Reconcile README, test counts, trace claims, and unsupported flags.
2. Run `agents-cli info`; enhance the existing project rather than creating a replacement.
3. Add configuration and a true no-network offline mode.
4. Move the portfolio-monitoring skill into the runtime skill directory.
5. Add JSON-safe ADK tool adapters over existing deterministic functions.
6. Define callbacks and `root_agent`/ADK app.
7. Route the existing CLI through the app while preserving legacy regression tests.
8. Add FastAPI health/readiness/review endpoints.
9. Add ADK eval datasets and grading configuration.
10. Expand trace capture and run all gates.
11. Update submission materials only from verified results.

## 11. Acceptance gates

The upgrade is complete only when:

- the previous deterministic/golden tests still pass;
- `root_agent` imports from `google.adk` and is discoverable by Agents CLI;
- the agent trace contains actual function calls and responses;
- a high-severity scenario invokes driver analysis and produces a review-required result;
- a clean scenario does not invoke unnecessary driver tools;
- offline mode succeeds with model/network constructors blocked;
- FastAPI and CLI produce the same structured result for the same offline input;
- unsafe paths and injected notes are blocked before model/tool use;
- Agents CLI eval artifacts show all required metrics at their thresholds;
- README commands and reported test/eval counts are generated from current evidence; and
- no cloud resource is created or modified.

## 12. Explicit non-goals

- Replacing deterministic actuarial calculations with model reasoning.
- Adding production insurance data or credentials.
- Building a multi-agent hierarchy solely for appearance.
- Implementing a dashboard before the HTTP/runtime contract is stable.
- Claiming interactive human approval when only a review flag exists.
- Requiring a live model or cloud account for the core demo.
- Deploying, publishing, enabling APIs, or changing IAM during the local upgrade.
