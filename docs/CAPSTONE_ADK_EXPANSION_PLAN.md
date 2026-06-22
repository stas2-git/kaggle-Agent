# Personal Build Plan: Expand the Capstone into an ADK Project

Prepared: 2026-06-22  
Plan status: Ready to follow  
Implementation status: Not started  
Controlling specifications: `.agents-cli-spec.md` and `capstone_spec_files/24_codelab_alignment_upgrade.md`

## What this plan is for

Use this document as the practical build checklist for upgrading the existing Actuarial Portfolio Monitoring Agent. The goal is not to rebuild the project. The goal is to preserve the working actuarial engine and add the recognizable Google ADK structure demonstrated in the codelabs.

The finished project should have:

- a Google ADK `root_agent`;
- deterministic actuarial functions exposed through safe tool adapters;
- security and observability callbacks;
- an active portfolio-monitoring Agent Skill;
- a real credential-free offline mode;
- CLI and FastAPI entrypoints using one shared application service;
- standard Makefile, Dockerfile, manifest, and `pyproject.toml` support;
- pytest coverage for deterministic behavior;
- Agents CLI evaluation for agent behavior; and
- documentation that matches what the project actually does.

## Current starting point

Verified before this plan was written:

| Item | Current status |
|---|---|
| Agents CLI | Installed, version `0.5.0` |
| Agents CLI project recognition | Not recognized yet |
| `.agents-cli-spec.md` | Present |
| Existing tests | `15 passed` |
| Existing deterministic tools | Present and working |
| Existing direct Gemini synthesis | Present in `portfolio_agent/agent.py` |
| Runtime portfolio skill | Missing; only specification copy exists |
| `Makefile` | Missing at project root |
| `Dockerfile` | Missing at project root |
| `agents-cli-manifest.yaml` | Missing |
| FastAPI application | Missing |
| True `--force-offline` option | Missing |

## Rules for the entire upgrade

1. Work on one phase at a time.
2. Preserve the existing deterministic formulas and golden tests.
3. Stop immediately if a previously passing test fails.
4. Do not change `gemini-2.5-flash` unless deliberately updating the specification first.
5. Do not claim a human approval workflow when the project only produces a review-required flag.
6. Do not assert exact LLM prose in pytest.
7. Do not deploy, enable APIs, change IAM, or publish anything during this plan.
8. Commit or create a reversible checkpoint after every passing phase.
9. Do not update the video or write-up until the upgraded implementation is verified.

## Specification reading order

Before beginning, read these in order:

1. [Agents CLI source spec](../.agents-cli-spec.md)
2. [ADK upgrade specification](../capstone_spec_files/24_codelab_alignment_upgrade.md)
3. [Agent architecture](../capstone_spec_files/03_agent_architecture.md)
4. [Tool contracts](../capstone_spec_files/05_tool_contracts.yaml)
5. [Behavior scenarios](../capstone_spec_files/06_behavior_spec.feature)
6. [Security specification](../capstone_spec_files/07_security_privacy_spec.md)
7. [Evaluation specification](../capstone_spec_files/09_evaluation_spec.yaml)
8. [Trace specification](../capstone_spec_files/10_observability_trace_spec.md)
9. [Deployment and packaging](../capstone_spec_files/12_deployment_spec.md)
10. [Gate 7](../capstone_spec_files/23_spec_adequacy_and_build_gates.md#18-gate-7--adk-codelab-alignment-upgrade)

---

## Phase 0 — Protect the working baseline

### Objective

Create a known-good checkpoint before any structural work.

### Actions

- [x] Review `git status` and separate unrelated work from this upgrade.
- [x] Save or commit the current specifications and working project state.
- [x] Record the installed tool versions.
- [x] Run the existing test suite.
- [x] Save the output as the Gate 7 baseline.

### Commands

```bash
git status --short
uv --version
agents-cli info
uv sync
uv run pytest -q
```

### Expected result

```text
15 passed
```

### Evidence

Create or update:

```text
artifacts/gate_results/gate_7_adk_upgrade.md
```

Record command output, versions, current limitations, and the checkpoint identifier.

### Stop condition

Do not continue if the existing 15 tests do not pass.

---

## Phase 1 — Introduce the Agents CLI project structure

### Objective

Make Agents CLI recognize the existing repository without replacing the actuarial implementation.

### Important caution

This is an existing project. Use scaffold enhancement, not `scaffold create` in the project directory. Never use `--force` during the first enhancement.

### Optional reference preview

If you want to inspect generated conventions before touching the project, create a temporary prototype outside the repository:

```bash
agents-cli scaffold create capstone-adk-ref \
  --output-dir /tmp \
  --agent adk \
  --prototype \
  --deployment-target none \
  --cicd-runner skip \
  --agent-directory portfolio_agent \
  --agent-guidance-filename AGENTS.md
```

Inspect the temporary manifest, Makefile, test layout, and agent package. Do not copy generated agent logic over the existing project.

### Project enhancement

Run from the repository root:

```bash
agents-cli scaffold enhance . \
  --adk \
  --prototype \
  --deployment-target none \
  --cicd-runner skip \
  --agent-directory portfolio_agent \
  --agent-guidance-filename AGENTS.md
```

### Review before accepting generated changes

- [ ] `portfolio_agent/tools.py` was not replaced.
- [ ] `portfolio_agent/schemas.py` was not replaced.
- [ ] The model configuration was not silently changed.
- [ ] `.env` values were preserved.
- [ ] Existing tests and datasets remain present.
- [ ] `agents-cli-manifest.yaml` points to `portfolio_agent`.
- [ ] `App`/application naming matches `portfolio_agent`.
- [ ] No deployment or CI/CD infrastructure was introduced.

### Verification

```bash
agents-cli info
uv sync
uv run pytest -q
```

### Exit criteria

- Agents CLI recognizes the repository.
- The original 15 tests still pass.
- No existing actuarial behavior changed.

### Checkpoint

Suggested name:

```text
gate7-phase1-agents-cli-structure
```

---

## Phase 2 — Repair configuration and offline reproducibility

### Objective

Implement a genuine offline mode before introducing agent orchestration.

### Files

Create:

```text
portfolio_agent/config.py
portfolio_agent/service.py
tests/integration/test_offline_mode.py
```

Modify carefully:

```text
portfolio_agent/run.py
portfolio_agent/agent.py
.env.example
pyproject.toml
```

### Required design

`config.py` should centralize:

- execution mode;
- existing model name;
- approved input/output roots;
- threshold profile;
- application name; and
- environment-variable parsing.

`service.py` should define one review-service interface that both online and offline adapters will eventually call.

Add this CLI option:

```text
--force-offline
```

Offline mode must:

- reuse the real deterministic loading, validation, metric, anomaly, driver, report, and trace functions;
- use a deterministic template for narrative text;
- avoid constructing any Gemini, Vertex AI, or HTTP client;
- clearly label the report and trace as offline; and
- return the same structured result schema planned for online mode.

### Required tests

- [ ] Offline loss-ratio demo completes.
- [ ] Model/client constructors patched to raise are never called.
- [ ] No model-call event appears in the trace.
- [ ] Report and trace artifacts exist.
- [ ] Existing online behavior is preserved.

### Verification

```bash
uv run python -m portfolio_agent.run \
  --input tests/golden/loss_ratio_spike.csv \
  --latest-month 2026-06 \
  --force-offline

uv run pytest -q
```

### Exit criteria

The command succeeds with all credentials removed and network/model constructors blocked in the test.

### Checkpoint

```text
gate7-phase2-offline-mode
```

---

## Phase 3 — Activate the portfolio-monitoring Agent Skill

### Objective

Turn the skill from a specification artifact into runtime procedural guidance.

### Create the runtime skill

Copy the complete skill package from:

```text
capstone_spec_files/11_skill_portfolio_monitoring/
```

to:

```text
skills/portfolio_monitoring/
├── SKILL.md
├── references/
└── assets/
```

Keep `skills/extract_pdf_text/` separate; it is unrelated to portfolio monitoring.

### Required runtime integration

- [ ] Core workflow guidance is included in the root agent's instruction/context.
- [ ] Anomaly thresholds are loaded only when needed.
- [ ] Actuarial review principles are used during synthesis.
- [ ] The report template is used only during artifact generation.
- [ ] Skill guidance cannot override tool results or path policy.

### Required tests

- Skill files exist at the runtime path.
- Runtime instruction/context contains the core workflow rules.
- Numeric calculations still come only from deterministic tools.
- Missing optional references fail clearly rather than silently changing behavior.

### Verification

```bash
find skills/portfolio_monitoring -type f -maxdepth 3 -print
uv run pytest -q
```

### Checkpoint

```text
gate7-phase3-runtime-skill
```

---

## Phase 4 — Add JSON-safe ADK tool adapters

### Objective

Expose the existing actuarial functions to ADK without moving business logic into prompts or wrappers.

### Create

```text
portfolio_agent/adk_tools.py
tests/unit/test_adk_tools.py
```

### Preserve

Do not rewrite these unless a failing regression test proves a contract issue:

```text
portfolio_agent/tools.py
portfolio_agent/security.py
portfolio_agent/reporting.py
```

### Adapter requirements

Each model-callable adapter must:

- have typed parameters;
- avoid default parameter values in the model-facing signature;
- have a clear docstring describing when it should be called;
- return a JSON-serializable dictionary;
- use opaque dataset/metrics/anomaly references instead of passing dataframes;
- store/retrieve intermediate values through controlled runtime state;
- refuse unknown anomaly IDs or dimensions; and
- never accept an output/report path from the model.

### Required adapters

```text
load_portfolio_data
validate_portfolio_data
calculate_portfolio_metrics
detect_anomalies
investigate_anomaly_drivers
```

Report and trace writers should remain runtime-only, not model-callable.

### Required tests

- [ ] Adapter results serialize to JSON.
- [ ] Existing deterministic result values remain unchanged.
- [ ] Validation is required before calculations.
- [ ] Driver analysis requires a real anomaly ID.
- [ ] Dimensions are allowlisted.
- [ ] Model cannot select artifact paths.

### Verification

```bash
uv run pytest tests/unit/test_adk_tools.py -q
uv run pytest -q
```

### Checkpoint

```text
gate7-phase4-adk-tool-adapters
```

---

## Phase 5 — Add callbacks and richer trace events

### Objective

Enforce cross-cutting security and observability at the ADK boundary.

### Create or modify

```text
portfolio_agent/callbacks.py
portfolio_agent/tracing.py
tests/unit/test_callbacks.py
tests/integration/test_trace_events.py
```

### Callback responsibilities

#### `before_agent_callback`

- Initialize required state keys.
- Assign run ID, session ID, and execution mode.
- Create an empty security-flags collection.

#### `before_model_callback`

- Permit only sanitized structured tool results.
- Block system-prompt disclosure and instruction-override attempts.

#### `before_tool_callback`

- Enforce the exact tool allowlist.
- Validate workflow prerequisites.
- Apply path and dimension policy.
- Correlate anomaly IDs with session state.

#### `after_tool_callback`

- Validate the returned dictionary/schema.
- Redact unsafe text.
- Record status, timing, arguments summary, and response summary.
- Fail closed on corrupt numeric output.

#### `after_model_callback`

- Reject unsupported numeric claims.
- Reject binding pricing/underwriting recommendations.
- Preserve fact-versus-hypothesis separation.

### Trace requirements

Capture:

- application, agent, run, session, and invocation IDs;
- function-call and matching function-response IDs;
- callback policy decisions;
- model and execution mode;
- sanitized inputs/outputs;
- durations, errors, and retries;
- review reasons; and
- report/trace artifact status.

Never capture credentials, full datasets, hidden prompts, or chain-of-thought.

### Verification

```bash
uv run pytest tests/unit/test_callbacks.py -q
uv run pytest tests/integration/test_trace_events.py -q
uv run pytest -q
```

### Checkpoint

```text
gate7-phase5-callbacks-and-traces
```

---

## Phase 6 — Build the ADK root agent and application

### Objective

Replace direct final-only Gemini usage with bounded ADK orchestration while preserving all deterministic computation.

### Modify

```text
portfolio_agent/agent.py
portfolio_agent/__init__.py
portfolio_agent/service.py
pyproject.toml
```

### Required exports

```python
root_agent = ...
app = ...
```

The application name must match the directory:

```text
portfolio_agent
```

### Required agent behavior

1. Validate before analysis.
2. Calculate metrics through tools.
3. Detect anomalies through tools.
4. Skip driver tools for a clean portfolio.
5. Select relevant allowed dimensions for actual anomalies.
6. Ground every number in tool responses.
7. Separate evidence from hypotheses.
8. Return a structured review result.
9. Set advisory human-review reasons deterministically.

### Structured-output caution

Do not attach an ADK `output_schema` directly to a tool-calling agent if the installed ADK version disables tool calling when `output_schema` is present. Use either:

- a separate structured synthesis agent/node after tool execution; or
- final response parsing/validation outside the tool-calling agent.

### Required tests

- [ ] `portfolio_agent.agent.root_agent` imports.
- [ ] Agents CLI discovers the project.
- [ ] Clean scenario contains no driver function call.
- [ ] Anomaly scenario contains a valid driver function call.
- [ ] Every function call has a matching function response.
- [ ] Existing deterministic tests still pass.

### Smoke test

```bash
agents-cli info
agents-cli run -v \
  "Review the approved loss-ratio-spike demo portfolio for 2026-06."
```

Use this only as a smoke test. It is not the final evaluation gate.

### Checkpoint

```text
gate7-phase6-adk-root-agent
```

---

## Phase 7 — Route the CLI through the shared service

### Objective

Keep the familiar CLI while removing duplicate orchestration logic.

### Modify

```text
portfolio_agent/run.py
portfolio_agent/service.py
tests/integration/test_cli.py
```

### Required behavior

- Online mode invokes the ADK application.
- Offline mode invokes deterministic orchestration without model initialization.
- Both modes return `PortfolioReviewResult`.
- The CLI only parses arguments, calls the service, and formats the final console summary.
- No actuarial calculation remains in `run.py`.

### Verification

```bash
uv run python -m portfolio_agent.run \
  --input tests/golden/loss_ratio_spike.csv \
  --latest-month 2026-06 \
  --force-offline

uv run pytest tests/integration/test_cli.py -q
uv run pytest -q
```

### Checkpoint

```text
gate7-phase7-shared-cli
```

---

## Phase 8 — Add the FastAPI adapter

### Objective

Expose the shared review service over HTTP without duplicating business logic.

### Create

```text
portfolio_agent/fast_api_app.py
tests/integration/test_fast_api_app.py
```

### Required endpoints

| Endpoint | Required behavior |
|---|---|
| `GET /healthz` | Fixed liveness response; no model call. |
| `GET /readyz` | Sanitized configuration/readiness result. |
| `POST /api/reviews` | Validate request, call shared service, return `PortfolioReviewResult`. |

Do not add file uploads yet. Accept approved demo dataset references.

### Required tests

- [ ] Health works without credentials.
- [ ] Readiness reveals no environment values.
- [ ] Invalid paths return controlled errors.
- [ ] Offline API review works with model/network constructors blocked.
- [ ] CLI and API return equivalent anomalies and human-review reasons.
- [ ] FastAPI contains no calculations or threshold logic.

### Verification

```bash
uv run uvicorn portfolio_agent.fast_api_app:app \
  --host 127.0.0.1 \
  --port 8080

curl -fsS http://127.0.0.1:8080/healthz
curl -fsS http://127.0.0.1:8080/readyz
uv run pytest tests/integration/test_fast_api_app.py -q
uv run pytest -q
```

### Checkpoint

```text
gate7-phase8-fastapi-adapter
```

---

## Phase 9 — Complete packaging and developer commands

### Objective

Provide the familiar codelab project structure and reproducible commands.

### Required files

```text
Makefile
Dockerfile
agents-cli-manifest.yaml
.env.example
pyproject.toml
uv.lock
```

### Required Makefile targets

```text
install
run
run-offline
api
test
integration
lint
generate-traces
grade
eval
```

### Dependency groups

Runtime dependencies should include only packages used by the running application. Put pytest, linting, type checking, and evaluation helpers in development groups.

Add the packages actually required by the implementation, expected to include:

- Google ADK;
- Agents CLI-compatible dependencies;
- FastAPI and Uvicorn;
- existing Google GenAI, Pandas, Pydantic, and dotenv dependencies; and
- development tooling such as pytest, Ruff, mypy, and PyYAML.

Do not change the configured model as part of dependency cleanup.

### Docker requirements

- Python 3.11+.
- Reproducible install from `uv.lock`.
- Non-root runtime user where practical.
- Bind to `0.0.0.0`.
- Read `PORT`, defaulting to `8080`.
- Run the FastAPI adapter.
- No credentials baked into the image.

### Verification

```bash
make install
make lint
make test
make integration
make run-offline
```

If Docker is installed:

```bash
docker build -t portfolio-agent:local .
docker run --rm -p 8080:8080 \
  -e PORT=8080 \
  portfolio-agent:local
```

### Checkpoint

```text
gate7-phase9-packaging
```

---

## Phase 10 — Build the real Agents CLI evaluation suite

### Objective

Replace prepared scenario memos as the primary behavioral evidence with real ADK inference traces and grading.

### Create or reorganize

```text
tests/eval/datasets/
tests/eval/eval_config.yaml
artifacts/traces/
artifacts/grade_results/
```

### Keep the evaluation layers separate

#### Pytest

Use for:

- formulas and thresholds;
- schema validation;
- security/path policy;
- callbacks;
- API contracts;
- offline isolation; and
- ADK session/event integration.

Do not assert LLM tone, keywords, or exact narrative text.

#### Agents CLI eval

Use for:

- task success;
- trajectory quality;
- tool-use quality;
- final response quality;
- hallucination;
- safety; and
- domain-specific grounding.

### Start with two cases

1. Clean portfolio: no unnecessary driver tool.
2. Loss-ratio spike: relevant driver tool and human review.

Once those pass, expand to validation failure, premium drop, prompt injection, forbidden file request, unavailable metric, conflicting signals, and high-impact recommendation.

### Required metrics

```text
multi_turn_task_success
multi_turn_tool_use_quality
multi_turn_trajectory_quality
final_response_quality
hallucination
safety
actuarial_metric_consistency
portfolio_trace_completeness
```

The final two should be deterministic local custom metrics.

### Quality flywheel

```bash
agents-cli eval generate
agents-cli eval grade
```

Inspect the JSON/HTML results. Fix the agent, prompt, callback, or tool description—not the threshold—then rerun:

```bash
agents-cli eval compare \
  artifacts/grade_results/<baseline>.json \
  artifacts/grade_results/<candidate>.json
```

Expect several iterations. Do not expand the dataset until the two core cases pass.

### Exit criteria

- All configured metrics meet the specification threshold.
- Deterministic metric consistency is 100%.
- Trace completeness is 100%.
- Results are saved under `artifacts/grade_results/`.
- No regression is accepted without explanation.

### Checkpoint

```text
gate7-phase10-agent-evaluation
```

---

## Phase 11 — Reconcile documentation and submission assets

### Objective

Update claims only after the upgraded project has passed all checks.

### Update

```text
README.md
submission/kaggle_writeup_draft.md
submission/video_script.md
submission/video/
artifacts/gate_results/gate_7_adk_upgrade.md
artifacts/gate_results/gate_6_submission_readiness.md
capstone_spec_files/ALL_SPECS_COMBINED.md
```

### Required corrections

- Replace hardcoded historical test counts with current verified counts.
- Document working commands only.
- Explain that offline mode demonstrates reproducibility.
- Present Agents CLI grades as agent-quality evidence.
- Show genuine function-call/function-response trace evidence.
- Describe human review as advisory unless real resumability was implemented.
- Update the architecture diagram to show ADK, tools, callbacks, CLI, and FastAPI.
- Regenerate screenshots and video cards from the current build.

### Final commands

```bash
make lint
make test
make integration
make run-offline
agents-cli eval generate
agents-cli eval grade
```

### Submission checks

- [ ] Write-up remains under 2,500 words.
- [ ] Video remains under five minutes.
- [ ] Cover image exists.
- [ ] Public repository contains no secrets, model weights, private audio, or unnecessary reference environments.
- [ ] All README commands work from a clean checkout.
- [ ] Gate 7 evidence is complete.

### Checkpoint

```text
gate7-phase11-submission-reconciled
```

---

## Phase 12 — Optional work after the local capstone is complete

Do not begin these until the required local project passes Gate 7.

### Optional Agent Runtime deployment

Use for an interactive/session-based deployed ADK agent. This requires a separate deployment decision and explicit approval.

### Optional Cloud Run ambient execution

Use Cloud Run or GKE—not Agent Runtime—for ADK Pub/Sub/Eventarc trigger endpoints. This also requires explicit approval and infrastructure review.

### Optional manager dashboard and true HITL

Add only when the agent has a consequential action that genuinely needs approval. At that point, specify ADK resumability, interrupt IDs, authorization, idempotency, audit history, and exact session correlation before implementation.

---

## Final Gate 7 checklist

### Existing behavior preserved

- [ ] All original deterministic/golden tests pass.
- [ ] Metrics and driver calculations are unchanged unless a documented defect was fixed.
- [ ] Reports remain reproducible.

### ADK project

- [ ] Agents CLI recognizes the repository.
- [ ] `portfolio_agent.agent.root_agent` imports.
- [ ] The app name matches `portfolio_agent`.
- [ ] Real ADK function-call/function-response events are visible.

### Safety and truth

- [ ] Every number maps to deterministic tool output.
- [ ] Callbacks enforce tools, paths, prerequisites, and dimensions.
- [ ] Offline mode performs no model/network call.
- [ ] Human review is described accurately.

### Interfaces and packaging

- [ ] CLI and FastAPI share one application service.
- [ ] Health/readiness endpoints reveal no secrets.
- [ ] Makefile and Dockerfile work.
- [ ] Dependencies are locked and organized.

### Evaluation

- [ ] Pytest passes.
- [ ] Agents CLI traces are generated from the real agent.
- [ ] Agents CLI grading meets every threshold.
- [ ] Baseline/candidate comparison shows no unexplained regression.

### Submission

- [ ] README reflects verified behavior.
- [ ] Write-up, screenshots, and video were regenerated.
- [ ] Gate 7 evidence contains exact commands and results.
- [ ] No deployment or cloud mutation occurred without approval.

## If something fails

Use this loop:

```text
Reproduce the exact failure.
Localize it to config, deterministic tool, adapter, callback, agent, API, or eval.
Change one thing.
Rerun the exact failing command.
Add a regression test or eval case.
Continue only after the phase is green again.
```

If the same error occurs three times, stop trying variations. Re-read the relevant specification and the appropriate Agents CLI skill/reference before continuing.
