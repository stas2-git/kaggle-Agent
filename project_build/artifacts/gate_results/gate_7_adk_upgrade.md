# Gate 7 — ADK Codelab-Alignment Upgrade

## Phase 0: Protected working baseline

Date: 2026-06-22
Branch: `main`
Specification baseline commit: `2de040a6139eef2b172ea2e46d601595b17315ee`
Checkpoint tag: `gate7-baseline-v0.2`
Decision: PASS

## Scope

This phase records the known-good state before Agents CLI scaffolding or application-code changes. It does not deploy, publish, enable APIs, alter IAM, or modify infrastructure.

## Worktree review

Before creating this evidence, `git status --short` contained only:

```text
?? docs/CAPSTONE_ADK_EXPANSION_PLAN.md
```

The updated version 0.2 specifications were already present in the baseline commit, including:

```text
.agents-cli-spec.md
capstone_spec_files/24_codelab_alignment_upgrade.md
artifacts/spec_reviews/spec_review_v2_adk_upgrade.md
```

No unrelated project, video, natural-voice, model-asset, or reference-material changes were included in the Phase 0 checkpoint.

## Tool versions

```text
uv 0.11.21 (Homebrew 2026-06-11 aarch64-apple-darwin)
Python 3.11.15
git version 2.50.1 (Apple Git-155)
Google Agents CLI 0.5.0
macOS 26.5.1 arm64
```

Agents CLI install path:

```text
[google-agents-cli install path]
```

## Agents CLI project status

`agents-cli info` reported:

```text
No agent project found in the current directory or any parent.
```

This is expected before Phase 1. Agents CLI is installed, but `agents-cli-manifest.yaml` and the recognized project scaffold do not yet exist.

## Dependency synchronization

Command:

```bash
uv sync
```

Result:

```text
Resolved 45 packages in 3ms
Checked 42 packages in 0.60ms
```

No dependency or lock-file change was produced.

## Baseline tests

Command:

```bash
uv run pytest -q
```

Result:

```text
...............                                                          [100%]
15 passed in 0.16s
```

## Known baseline limitations

- The repository is not yet recognized as an Agents CLI project.
- `portfolio_agent.agent` does not yet export an ADK `root_agent`.
- The root Makefile, Dockerfile, and `agents-cli-manifest.yaml` are not yet present.
- The portfolio-monitoring skill is not yet installed under `skills/portfolio_monitoring/`.
- The documented `--force-offline` behavior is not yet implemented.
- FastAPI, ADK callbacks, ADK tool wrappers, and Agents CLI behavioral evals are not yet implemented.

These are planned Phase 1–10 changes, not Phase 0 failures.

## Gate decision

PASS. The known-good deterministic baseline is reproducible, all 15 tests pass, and the worktree was cleanly separated before structural changes. Phase 1 may begin from tag `gate7-baseline-v0.2`.

---

## Phase 1 attempt: Agents CLI project structure

Date: 2026-06-22
Decision: STOPPED — test gate failed

## Commands run

Preview scaffold outside the repository:

```bash
rm -rf /tmp/capstone-adk-ref
agents-cli scaffold create capstone-adk-ref \
  --output-dir /tmp \
  --agent adk \
  --prototype \
  --deployment-target none \
  --cicd-runner skip \
  --agent-directory portfolio_agent \
  --agent-guidance-filename AGENTS.md
```

Enhance existing repository:

```bash
agents-cli scaffold enhance . \
  --adk \
  --prototype \
  --deployment-target none \
  --cicd-runner skip \
  --agent-directory portfolio_agent \
  --agent-guidance-filename AGENTS.md
```

Agents CLI recognition check:

```bash
agents-cli info
```

Result:

```text
Project root:       [local project root]
Project name:       kaggle agent
Deployment target:  none
Agent directory:    portfolio_agent
Region:             us-east1
```

Test gate:

```bash
uv sync && uv run pytest -q
```

Result:

```text
5 errors during collection
```

## Failure details

The generated scaffold introduced test/import expectations before the project has the ADK dependency and expected exports:

```text
ModuleNotFoundError: No module named 'google.adk'
ImportError: cannot import name 'app' from 'portfolio_agent.agent'
```

The failure appeared during collection for:

```text
tests/integration/test_agent.py
tests/test_eval_security.py
tests/test_golden.py
tests/test_security.py
tests/test_tools.py
```

## Generated files present at stop point

```text
AGENTS.md
Dockerfile
agents-cli-manifest.yaml
portfolio_agent/__init__.py
portfolio_agent/app_utils/
portfolio_agent/fast_api_app.py
tests/eval/
tests/integration/
tests/unit/
```

## Additional worktree note

Four reference-material implementation spec links were reported as file-type changes after scaffolding:

```text
T refrence material/codelabs/CL4 ambient agent/ambient-expense-agent/CAPSTONE_IMPLEMENTATION_SPEC.md
T refrence material/codelabs/CL4 secure an ai agent lifecycle/secure-agent-lab/shopping-assistant/CAPSTONE_IMPLEMENTATION_SPEC.md
T refrence material/codelabs/CL5 Deploy an ADK agent to Agent Runtime using Agents CLI/expense-agent/CAPSTONE_IMPLEMENTATION_SPEC.md
T refrence material/codelabs/CL5 Vibecode and Deploy a Frontend for an ADK agent/submission_frontend/CAPSTONE_IMPLEMENTATION_SPEC.md
```

## Stop decision

Per the build rule, work stopped at Phase 1 because the full test suite did not pass. Do not begin Phase 2 until Phase 1 is repaired or the generated scaffold changes are reverted.

---

## Phase 1 rerun: repaired Agents CLI project structure

Date: 2026-06-22
Decision: PASS

## Spec update

The Phase 1 scope was clarified in:

```text
capstone_spec_files/24_codelab_alignment_upgrade.md
docs/CAPSTONE_ADK_EXPANSION_PLAN.md
```

Clarification: Phase 1 is a structure-recognition phase. Generated scaffold tests or imports that require a completed ADK `root_agent`, live ADK runner, Google Cloud credentials, or FastAPI review API are later-phase material and should be removed or quarantined until Phase 6/8.

## Repairs

- Made `portfolio_agent/__init__.py` side-effect-light so deterministic module imports do not require a not-yet-built ADK app.
- Removed generated placeholder ADK runner/server tests that belonged to later phases:

```text
tests/integration/test_agent.py
tests/integration/test_server_e2e.py
tests/unit/test_dummy.py
```

- Restored reference-material implementation spec links as symlinks after scaffold enhancement dereferenced them.

## Verification

Command:

```bash
agents-cli info && uv sync && uv run pytest -q
```

Result:

```text
Project root:       [local project root]
Project name:       kaggle agent
Deployment target:  none
Agent directory:    portfolio_agent
Region:             us-east1
Resolved 45 packages in 3ms
Checked 42 packages in 0.69ms
...............                                                          [100%]
15 passed in 0.18s
```

## Phase 1 gate decision

PASS. Agents CLI recognizes the repository, the existing deterministic project behavior is preserved, and the full current test suite passes. Phase 2 may begin after this checkpoint is saved.

---

## Phase 2: Offline configuration and shared review service

Date: 2026-06-22
Decision: PASS

## Scope

Phase 2 introduced a genuine credential-free offline path before ADK orchestration. The CLI now routes through a shared service boundary and supports `--force-offline`.

## Files changed

```text
.env.example
docs/CAPSTONE_ADK_EXPANSION_PLAN.md
artifacts/gate_results/gate_7_adk_upgrade.md
portfolio_agent/config.py
portfolio_agent/run.py
portfolio_agent/schemas.py
portfolio_agent/service.py
tests/integration/test_offline_mode.py
```

## Verification

Offline command:

```bash
uv run python -m portfolio_agent.run \
  --input tests/golden/loss_ratio_spike.csv \
  --latest-month 2026-06 \
  --force-offline
```

Result:

```text
Run complete.
Mode: offline
Severity: High
Human review required: Yes
Human review reasons: high_severity_anomaly, deterministic_threshold_requires_review
```

Targeted tests:

```bash
uv run pytest tests/integration/test_offline_mode.py -q
```

Result:

```text
3 passed
```

Full test suite:

```bash
uv run pytest -q
```

Result:

```text
18 passed in 0.51s
```

## Confirmed behaviors

- Offline loss-ratio demo completes.
- Offline path reuses real deterministic loading, validation, metrics, anomaly, driver, report, and trace functions.
- Offline mode does not construct a Gemini client when the constructor is patched to raise.
- Offline trace records `execution_mode: offline`.
- Offline trace contains `offline_synthesis_started` and does not contain `model_synthesis_started`.
- Report and trace artifacts are produced.
- Existing online synthesis boundary remains callable through the shared service.

## Phase 2 gate decision

PASS. Offline reproducibility is implemented and tested, and all previously passing tests still pass.

---

## Phase 3: Runtime portfolio-monitoring Agent Skill

Date: 2026-06-29
Decision: PASS

## Scope

Phase 3 moved the portfolio-monitoring skill from the specification package into the runtime skill directory and added a small source-level loader that can be reused by the later ADK root agent. The integration does not change deterministic calculations, path policy, or the configured model.

## Files changed

```text
portfolio_agent/agent.py
portfolio_agent/skill_context.py
skills/portfolio_monitoring/
tests/integration/test_runtime_skill.py
artifacts/gate_results/gate_7_adk_upgrade.md
```

## Verification

Runtime skill files:

```bash
find skills/portfolio_monitoring -maxdepth 3 -type f -print | sort
```

Result:

```text
skills/portfolio_monitoring/SKILL.md
skills/portfolio_monitoring/assets/monthly_review_report_template.md
skills/portfolio_monitoring/references/actuarial_review_principles.md
skills/portfolio_monitoring/references/anomaly_thresholds.md
skills/portfolio_monitoring/scripts/README.md
```

Targeted tests:

```bash
uv run pytest tests/integration/test_runtime_skill.py -q
```

Result:

```text
4 passed in 0.15s
```

Full test suite:

```bash
uv run pytest -q
```

Result:

```text
22 passed in 0.58s
```

## Confirmed behaviors

- The runtime copy exists at `skills/portfolio_monitoring/` with `SKILL.md`, references, assets, and script notes.
- The instruction context includes core workflow and safety rules.
- Threshold and report-template references are not loaded eagerly.
- Unknown optional references fail clearly.
- Deterministic anomaly detection and path policy remain authoritative after skill loading.

## Phase 3 gate decision

PASS. The runtime skill is active as source-loadable guidance, the online synthesis prompt includes the core workflow/principles context, and all tests pass.

---

## Phase 4: JSON-safe ADK tool adapters

Date: 2026-06-29
Decision: PASS

## Scope

Phase 4 added model-callable adapter functions in `portfolio_agent/adk_tools.py` without moving actuarial formulas out of the deterministic engine. The adapters use opaque references in runtime state, return JSON-serializable dictionaries, require validation before analysis, refuse unknown anomaly IDs and unauthorized dimensions, and do not expose report/trace/output paths.

## Files changed

```text
portfolio_agent/adk_tools.py
tests/unit/test_adk_tools.py
artifacts/gate_results/gate_7_adk_upgrade.md
```

## Verification

Targeted tests:

```bash
uv run pytest tests/unit/test_adk_tools.py -q
```

Result:

```text
6 passed in 0.16s
```

Full test suite:

```bash
uv run pytest -q
```

Result:

```text
28 passed in 0.57s
```

## Confirmed behaviors

- Adapter outputs serialize through `json.dumps`.
- Loss-ratio anomaly values and severity remain produced by deterministic tools.
- Metrics calculation fails closed until validation has run.
- Driver analysis refuses unknown anomaly IDs.
- Driver dimensions are allowlisted.
- Model-facing adapter signatures have typed required parameters and expose no artifact path controls.

## Phase 4 gate decision

PASS. ADK-ready adapters are present, deterministic behavior is preserved, and all tests pass.

---

## Phase 5: Callbacks and richer trace events

Date: 2026-06-29
Decision: PASS

## Scope

Phase 5 added import-safe callback policy functions and enriched trace events without requiring a live ADK runtime yet. The callbacks initialize required run state, enforce tool/path/prerequisite/dimension/anomaly policy, validate JSON-safe tool responses, redact unsafe text, and block unsafe model output. The trace logger now preserves existing event names while also recording event IDs, event types, status, summaries, app/session metadata, human-review metadata, and policy-decision events.

## Files changed

```text
portfolio_agent/callbacks.py
portfolio_agent/tracing.py
tests/unit/test_callbacks.py
tests/integration/test_trace_events.py
artifacts/gate_results/gate_7_adk_upgrade.md
```

## Verification

Callback tests:

```bash
uv run pytest tests/unit/test_callbacks.py -q
```

Result:

```text
7 passed in 0.18s
```

Trace tests:

```bash
uv run pytest tests/integration/test_trace_events.py -q
```

Result:

```text
2 passed in 0.19s
```

Full test suite:

```bash
uv run pytest -q
```

Result:

```text
37 passed in 0.59s
```

## Confirmed behaviors

- `before_agent_callback` initializes run/session/mode/security state.
- `before_model_callback` blocks prompt-disclosure and instruction-override attempts.
- `before_tool_callback` enforces tool allowlist, file path policy, workflow prerequisites, driver dimensions, and anomaly correlation.
- `after_tool_callback` rejects non-JSON-safe/corrupt numeric responses and redacts unsafe text.
- `after_model_callback` blocks unsupported or binding business recommendations.
- Offline traces include enriched schema fields and no model-call events.
- Policy-decision events can be recorded in trace output.

## Phase 5 gate decision

PASS. Callback policy and richer trace evidence are implemented and tested, and all tests pass.

---

## Phase 6: ADK root agent and application

Date: 2026-06-29
Decision: PASS

## Scope

Phase 6 added the real Google ADK dependency, exported `portfolio_agent.agent.root_agent`, and created `app = App(name="portfolio_agent", root_agent=root_agent)`. The tool-calling agent uses the Phase 4 adapters and Phase 5 callbacks. No `output_schema` is attached to the tool-calling agent, preserving ADK tool calls.

## Files changed

```text
portfolio_agent/agent.py
portfolio_agent/adk_tools.py
portfolio_agent/callbacks.py
pyproject.toml
uv.lock
tests/integration/test_adk_root_agent.py
tests/unit/test_adk_tools.py
tests/unit/test_callbacks.py
artifacts/gate_results/gate_7_adk_upgrade.md
```

## Dependency update

Command:

```bash
uv add 'google-adk>=2.0.0,<3.0.0'
```

Result included:

```text
+ google-adk==2.3.0
```

## Verification

Root import check:

```bash
uv run python - <<'PY'
from portfolio_agent.agent import app, root_agent
print(app.name)
print(root_agent.name)
print([getattr(tool, 'name', getattr(tool, '__name__', str(tool))) for tool in root_agent.tools])
PY
```

Result:

```text
portfolio_agent
portfolio_monitoring_agent
['load_portfolio_data', 'validate_portfolio_data', 'calculate_portfolio_metrics', 'detect_anomalies', 'investigate_anomaly_drivers']
```

Agents CLI recognition:

```bash
agents-cli info
```

Result:

```text
Project root:       [local project root]
Project name:       kaggle agent
Deployment target:  none
Agent directory:    portfolio_agent
Region:             us-east1
```

Targeted tests:

```bash
uv run pytest tests/integration/test_adk_root_agent.py -q
```

Result:

```text
4 passed
```

Full test suite:

```bash
uv run pytest -q
```

Result:

```text
43 passed in 0.74s
```

## ADK smoke tests

Anomaly scenario command:

```bash
agents-cli run -v "Review the approved loss-ratio-spike demo portfolio for 2026-06."
```

Confirmed behavior:

- Real ADK `functionCall` and matching `functionResponse` events were emitted.
- Tool sequence included `load_portfolio_data`, `validate_portfolio_data`, `calculate_portfolio_metrics`, `detect_anomalies`, and `investigate_anomaly_drivers`.
- The detected anomaly was `ANOM_2026-06_Public_D&O_LR`.
- The agent used allowed driver dimensions: `coverage`, `state`, `underwriter`, and `policy_year`.

Clean scenario command:

```bash
agents-cli run -v "Review the approved clean demo portfolio for 2026-06."
```

Confirmed behavior:

- Real ADK `functionCall` and matching `functionResponse` events were emitted.
- Tool sequence included loading, validation, metrics, and anomaly detection.
- `detect_anomalies` returned an empty anomaly list.
- No `investigate_anomaly_drivers` call occurred.

## Failures and fixes

First anomaly smoke attempt:

- Failure: the model passed the alias string `"loss-ratio-spike demo portfolio"` as a path.
- Fix: added explicit approved demo dataset aliases to the root-agent instruction.

Second anomaly smoke attempt:

- Failure: a Pandas DataFrame was stored in ADK session state and ADK attempted to JSON-serialize it.
- Fix: moved non-JSON runtime objects into module-local controlled stores and kept only opaque refs/summaries in ADK state.

Third anomaly smoke attempt:

- Failure: the model selected `group_by=["policy_year", "valuation_month"]`, which violated the deterministic metric schema.
- Fix: enforced canonical metric grouping `["valuation_month", "business_segment"]` in both adapter and callback policy, and added regression tests.

Clean smoke attempt:

- One run failed with an ADK loader/import race during server startup. A rerun succeeded without code changes and produced the expected clean trajectory.

## Phase 6 gate decision

PASS. The repository exports a real ADK root agent/application, Agents CLI discovers the project, smoke tests produce genuine function-call/function-response events, clean and anomaly routing behave as expected, and all tests pass.

---

## Phase 7: Shared CLI adapter

Date: 2026-06-29
Decision: PASS

## Scope

Phase 7 verified the CLI as a thin adapter over `portfolio_agent.service.review_portfolio`. No actuarial calculation, threshold logic, prompt policy, or report-validation logic lives in `portfolio_agent/run.py`.

## Files changed

```text
tests/integration/test_cli.py
artifacts/gate_results/gate_7_adk_upgrade.md
```

## Verification

Offline CLI command:

```bash
uv run python -m portfolio_agent.run \
  --input tests/golden/loss_ratio_spike.csv \
  --latest-month 2026-06 \
  --force-offline
```

Result:

```text
Run complete.
Mode: offline
Severity: High
Human review required: Yes
Human review reasons: high_severity_anomaly, deterministic_threshold_requires_review
```

Targeted CLI tests:

```bash
uv run pytest tests/integration/test_cli.py -q
```

Result:

```text
4 passed in 0.17s
```

Full test suite:

```bash
uv run pytest -q
```

Result:

```text
47 passed in 0.77s
```

## Confirmed behaviors

- Online CLI mode calls the shared service with `force_offline=False`.
- Offline CLI mode calls the shared service with `force_offline=True`.
- CLI returns structured `PortfolioReviewResult` data through the shared service boundary.
- `portfolio_agent/run.py` imports no deterministic actuarial tool functions.

## Phase 7 gate decision

PASS. The CLI is a parsing/formatting adapter over the shared review service, and all tests pass.

---

## Phase 8: FastAPI adapter

Date: 2026-06-29
Decision: PASS

## Scope

Phase 8 replaced the scaffolded cloud-auth FastAPI file with a local transport adapter over the shared review service. The API exposes liveness, sanitized readiness, and offline/online review creation without duplicating actuarial calculations or threshold logic.

## Files changed

```text
portfolio_agent/fast_api_app.py
tests/integration/test_fast_api_app.py
artifacts/gate_results/gate_7_adk_upgrade.md
```

## Verification

Targeted FastAPI tests:

```bash
uv run pytest tests/integration/test_fast_api_app.py -q
```

Result:

```text
6 passed in 0.66s
```

Full test suite:

```bash
uv run pytest -q
```

Result:

```text
53 passed in 0.85s
```

Live server smoke:

```bash
uv run uvicorn portfolio_agent.fast_api_app:app --host 127.0.0.1 --port 8080
curl -fsS http://127.0.0.1:8080/healthz
curl -fsS http://127.0.0.1:8080/readyz
```

Results:

```text
{"status":"ok","application":"portfolio_agent"}
{"status":"ready","application":"portfolio_agent","execution_mode":"online","model_configured":true,"approved_dataset_aliases":["benchmark_deterioration","clean_portfolio","loss_ratio_spike","premium_drop"]}
```

## Confirmed behaviors

- `/healthz` works without credentials or model construction.
- `/readyz` exposes sanitized readiness information and no environment values.
- Invalid paths return controlled HTTP errors.
- Offline API reviews work with model constructors blocked.
- API and CLI/shared-service offline decisions match for the same clean portfolio input.
- `portfolio_agent/fast_api_app.py` contains no actuarial calculation or threshold logic.

## Phase 8 gate decision

PASS. The FastAPI adapter is implemented, live health/readiness endpoints work, and all tests pass.

---

## Phase 9: Packaging and developer commands

Date: 2026-06-29
Decision: PASS

## Scope

Phase 9 added the root Makefile and updated packaging metadata/container configuration for the local ADK/FastAPI project. Runtime dependencies now explicitly include ADK, FastAPI, Uvicorn, Google GenAI, Pandas, Pydantic, and existing document/PDF helpers. Development dependencies include pytest, PyYAML, Ruff, and mypy.

## Files changed

```text
Makefile
Dockerfile
pyproject.toml
uv.lock
portfolio_agent/fast_api_app.py
artifacts/gate_results/gate_7_adk_upgrade.md
```

## Makefile targets

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

## Verification

Install:

```bash
make install
```

Result:

```text
uv sync
Resolved 73 packages in 5ms
Checked 70 packages in 1ms
```

Lint:

```bash
make lint
```

Result:

```text
uv run python -m compileall -q portfolio_agent tests
```

Test:

```bash
make test
```

Result:

```text
53 passed in 0.86s
```

Integration:

```bash
make integration
```

Result:

```text
23 passed in 0.80s
```

Offline run:

```bash
make run-offline
```

Result:

```text
Run complete.
Mode: offline
Severity: High
Human review required: Yes
Human review reasons: high_severity_anomaly, deterministic_threshold_requires_review
```

Docker check:

```bash
docker --version
```

Result:

```text
zsh:1: command not found: docker
```

Docker build was not run because Docker is not installed in this environment.

## Confirmed behaviors

- Root Makefile provides the required developer targets.
- Dockerfile installs from `uv.lock`, copies runtime data/skills, creates a non-root user, binds to `0.0.0.0`, and reads `PORT` with default `8080`.
- No credentials are baked into the image configuration.
- Runtime API aliases now point to `data/eval` CSVs, which match the golden CSVs byte-for-byte.

## Phase 9 gate decision

PASS. Packaging commands work locally, Dockerfile is updated for runtime use, and the only skipped verification is the optional Docker build due to Docker not being installed.

---

## Phase 10: Agents CLI evaluation suite

Date: 2026-06-29
Decision: BLOCKED — Google Cloud ADC required by `agents-cli eval generate`

## Scope attempted

Phase 10 replaced the scaffolded generic greeting/weather eval dataset with the two required core portfolio cases and configured the required built-in/custom metric set.

## Files changed

```text
tests/eval/datasets/basic-dataset.json
tests/eval/eval_config.yaml
pyproject.toml
uv.lock
artifacts/gate_results/gate_7_adk_upgrade.md
```

## Dataset cases

```text
clean_portfolio_no_driver
loss_ratio_spike_driver_review
```

## Metrics configured

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

The final two are local deterministic custom metrics in `tests/eval/eval_config.yaml`.

## Eval dependency repair

Initial command:

```bash
GOOGLE_CLOUD_PROJECT=local-eval GOOGLE_CLOUD_LOCATION=global agents-cli eval generate
```

First failure:

```text
Extra `eval` is not defined in the project's `optional-dependencies` table
```

Repair:

```text
Added [project.optional-dependencies].eval with google-adk[eval] and google-cloud-aiplatform[evaluation].
```

## Blocking failure

Command:

```bash
GOOGLE_CLOUD_PROJECT=local-eval GOOGLE_CLOUD_LOCATION=global agents-cli eval generate
```

Result:

```text
[generate] loaded 2 eval case(s)
[generate] inference 1/2
[generate] inference 1 FAILED: Your default credentials were not found.
[generate] inference 2/2
[generate] inference 2 FAILED: Your default credentials were not found.
[generate] Inference summary: 0/2 succeeded, 2 failed.
[generate] No artifact written: 0 of 2 cases produced output.
Error: Inference failed (exit code 1)
```

Traceback root cause:

```text
google.auth.exceptions.DefaultCredentialsError:
Your default credentials were not found.
```

## Source confirmation

`agents-cli eval generate --help` exposes only:

```text
--dataset
--output
--project
--region
```

The installed command source at:

```text
[google-agents-cli install path]/eval/cmd_generate.py
```

requires a GCP project and stages `_inference_runner.py`; the runner calls:

```text
client.evals.run_inference(src=single, agent=agent)
```

That path initializes Google Cloud clients and requires Application Default Credentials. `agents-cli 0.5.0` does not expose a local/API-key-only `eval generate` flag.

## Regression gate after eval-file changes

Command:

```bash
uv run pytest -q
```

Result:

```text
53 passed in 0.93s
```

## Phase 10 gate decision

BLOCKED. The eval dataset and metric configuration are prepared, but `agents-cli eval generate` and therefore `agents-cli eval grade` cannot complete in this environment until Google Cloud Application Default Credentials and a real project are configured. No cloud resources were created or modified.
