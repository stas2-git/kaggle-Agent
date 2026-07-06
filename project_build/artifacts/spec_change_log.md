# Spec Change Log

Format per `spec_files/50_implementation/02_spec_adequacy_and_build_gates.md` Section 10.

---

Date: 2026-07-06
Spec version: 0.2 (no version bump; public repository polish only)
File changed:
- `project_build/artifacts/README.md`
- `project_build/artifacts/spec_change_log.md`
- `spec_files/50_implementation/02_spec_adequacy_and_build_gates.md`

Reason: Refresh public-facing spec and artifact documentation so GitHub file history uses a
descriptive commit message instead of an old placeholder commit label.

Failure classification: **documentation polish**. No behavior, architecture, evaluation, or
runtime contract changed.

Verification: no code verification required for this documentation-only refresh. The prior
public-repo cleanup commit already verified unit/integration tests and video backend compile.

---

Date: 2026-07-05
Spec version: 0.2 (no version bump; documentation and reconciliation pass on the existing v0.2 package)
File changed:
- `spec_files/20_contracts/01_data_spec_and_schemas.md`
- `spec_files/60_skills/portfolio_monitoring/references/anomaly_thresholds.md`
- `project_build/portfolio_agent/tools.py`
- `project_build/tests/test_tools.py`
- `project_build/tests/unit/test_extended_anomalies.py` (new)

Reason: Gate 5 fresh-context rebuild v2 (`project_build/artifacts/rebuilds/v2/fresh_rebuild_v2.md`)
found 8 spec ambiguities/drifts that a builder with no access to the real implementation had
to guess at. Reconciling the specs against the actual implementation surfaced one further,
more significant gap: the data spec's anomaly-threshold table documented six anomaly checks
(loss ratio, written premium, claim count, rate change, benchmark adequacy, retention), but
`detect_anomalies()` only implemented three (loss ratio, written premium, benchmark
adequacy/`rate_adequacy`). This was invisible to the existing golden-fixture suite because no
golden scenario was designed to isolate the other three metrics.

Failure classification (per Section 2's table):
- Driver contribution formula, field-name drift (`contribution`/`contribution_to_change`,
  `anomaly_type`/`metric`), threshold direction, golden tolerance, prior-month rule,
  confidence-scoring rule, dimension tie-break: **spec gap** (undefined behavior; spec updated
  to describe the actual, tested implementation rather than requiring a code change).
- Missing claim_count/rate_change/avg_retention anomaly detection: **missing requirement**
  (spec described intended behavior the code did not yet implement; code updated to match).

Implementation impact:
- `detect_anomalies()` now also fires on claim-count spikes, rate-change deterioration, and
  retention decreases, using the same delta-threshold pattern as the existing checks.
- `investigate_anomaly_drivers()` now has matching driver-decomposition branches for these
  three metrics (additive formula for claim_count; premium-weighted-share-diff formula for
  rate_change and avg_retention, reusing the existing rate_adequacy pattern).
- Behavior change for existing golden scenario `loss_ratio_spike.csv`: this fixture's claim
  count incidentally jumps from 1 to 3 (+200%) between the two months, which now also fires a
  `claim_count` anomaly (severity: high) in addition to the loss-ratio anomaly. The captured
  demo log at `submission/02_video/assets/demo_outputs/run_output.txt` (dated 2026-06-22,
  "Running driver investigations on 1 anomalies") is now stale and should be regenerated
  before finalizing video/screenshot assets — it will now show 2 anomalies for this scenario.
- `tests/test_tools.py::test_detect_anomalies` held `claim_count` flat (1 -> 1) so it
  continues to isolate the loss-ratio anomaly only; this was a fixture adjustment, not a
  weakened assertion.
- `01_data_spec_and_schemas.md`'s Output Schemas section was rewritten to match the live
  Pydantic models in `portfolio_agent/schemas.py` exactly (it had drifted: e.g. it still
  showed `portfolio_review_result.summary: string` and a `success | validation_failed | ...`
  status enum instead of the real `memo: review_memo` object and
  `complete | failed | security_blocked` enum).

Tests/evals added:
- `tests/unit/test_extended_anomalies.py`: 6 new tests covering moderate/severe boundaries
  for claim_count, rate_change, and avg_retention detection; a no-incidental-cross-metric-
  anomaly baseline check; and driver-contribution-formula checks for all three new metrics.
- Full suite verified: `uv run pytest` (59 passed, up from 53), `make integration` (23
  passed), `make run-offline` (completes, now reports 2 anomalies for the loss-ratio-spike
  demo as expected).

Follow-up not done in this pass (flagged, not blocking): no new golden CSV/YAML fixture pair
was added specifically to isolate claim_count/rate_change/retention as the *primary* anomaly
of a scenario (the new unit tests use in-memory `MetricsRecord`/`DataFrame` fixtures instead).
Regenerating `submission/02_video/assets/demo_outputs/run_output.txt` and any dependent
screenshots/video before final submission is recommended given the loss_ratio_spike scenario
now reports 2 anomalies instead of 1.

---

Date: 2026-07-05
Spec version: 0.2 (no version bump; internal module reorganization, no behavior change)
File changed:
- `project_build/portfolio_agent/*.py` moved into `core/`, `adk/`, `observability/`,
  `support/` subpackages (see `project_build/portfolio_agent/README.md` for the new map);
  `agent.py`, `run.py`, `fast_api_app.py`, `service.py`, `app_utils/` stay at the top level.
- Every import site across `portfolio_agent/`, `tests/`, and `tests/eval/run_eval.py`
  updated to the new module paths.
- `portfolio_agent/support/skill_context.py`: `PROJECT_ROOT = Path(__file__).resolve()
  .parents[1]` was depth-relative to the file's old location and silently pointed at the
  wrong directory after the move; changed to `.parents[2]`.
- New: `project_build/portfolio_agent/README.md` (entry-point/tier map) and a one-line
  pointer added from `project_build/README.md`.

Reason: user could not tell which file was the application entry point versus supporting
code in the previously flat 14-file `portfolio_agent/` directory. Chosen fix (of two
offered) was a physical subpackage reorg rather than a docs-only pyramid map, matching the
numbered-pyramid style already used by `spec_files/`.

Failure classification: not a spec/code defect — a structural clarity request. No behavior
was intended to change; the `skill_context.py` path-depth bug above was an unintended
regression introduced by the move itself, caught by the existing test suite before commit,
not a pre-existing gap.

Implementation impact: none intended; `agents-cli info`, `agents-cli` root-agent import
shape (`portfolio_agent.agent:root_agent`), and all three entry points (`agent.py`, `run.py`,
`fast_api_app.py`) were re-verified after the move and behave identically to before.

Tests/evals added: none new; full existing suite re-run after the move as the regression
gate: `uv run pytest` (59 passed), `make integration` (23 passed), `make lint` (clean),
`make run-offline` (completes, same output as before the move), `agents-cli info` (project
still recognized), and a direct `from portfolio_agent.agent import app, root_agent` shape
check (app name, root agent name, and all 5 registered tools unchanged).
