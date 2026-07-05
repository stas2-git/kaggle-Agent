# Spec Adequacy and Build Gates
## Actuarial Portfolio Monitoring Agent

**Purpose:**  
This file defines the build-control process for the capstone project. It answers the practical question: *How do we know whether the specs are good enough to build from, and what do we do when implementation exposes gaps?*

This file does not replace the product, architecture, tool, security, or evaluation specs. It governs how those specs are used during implementation.

---

## 1. Core Principle

The project should not be built as one large prompt. It should be built through controlled gates:

```text
spec review
  -> plan-only build
  -> vertical slice
  -> deterministic tests
  -> agent/report/security evals
  -> fresh-context rebuild
  -> submission readiness
```

The goal is not to prove the spec is perfect before coding. That is unrealistic. The goal is to make every implementation failure produce one of three outcomes:

1. a code fix,
2. a spec update,
3. or an architecture correction.

The spec becomes stronger as the build exposes missing assumptions.

---

## 2. Failure Classification

Every build issue must be classified before fixing it.

| Failure Type | Definition | Required Action |
|---|---|---|
| **Code defect** | The spec was clear, but the implementation is wrong. | Fix code and add a regression test. |
| **Spec gap** | The agent had to invent behavior, fields, thresholds, examples, or routing logic. | Update the relevant spec and add/adjust tests. |
| **Architecture failure** | The selected structure, framework, data flow, or module boundary is wrong or too hard to extend. | Stop feature work. Redesign the affected module or branch. |
| **Evaluation gap** | The implementation could pass despite being wrong because no test/eval catches the issue. | Add deterministic test, golden case, or judge rubric before fixing. |
| **Security gap** | The agent can access, expose, mutate, or execute something outside intended boundaries. | Add guardrail, test, and security note before continuing. |

Do not delete the codebase for ordinary code defects. Delete or rebuild only when the failure shows the architecture is wrong or the implementation drifted too far from the spec.

---

## 3. Gate 0 — Spec Completeness Review

**Objective:** Determine whether the spec package is clear enough to start implementation.

**When:** Before writing application code.

**Input:** Entire `capstone_spec_files/` directory.

**Procedure:** Ask a fresh agent or coding agent to do a plan-only review.

The agent must produce:

1. a proposed file tree,
2. a list of MVP features,
3. a map from each MVP feature to the relevant spec files,
4. a list of required data fields,
5. a list of tools/functions to build,
6. a list of tests/evals to implement,
7. all blocking ambiguities,
8. all non-blocking assumptions.

**Pass Criteria:**

- No missing MVP requirements.
- No undefined core data fields.
- No undefined major tool inputs/outputs.
- No unclear routing decisions.
- No unclear human-review conditions.
- No unresolved security boundary questions.
- At least one vertical slice can be built without inventing requirements.

**Fail Criteria:**

- The agent asks what the project is supposed to do.
- The agent invents core outputs not present in the specs.
- The agent cannot identify the MVP.
- The agent cannot identify which files/tests to create.
- The agent cannot distinguish deterministic logic from LLM logic.

**Required Artifact:**  
Create or update:

```text
artifacts/spec_reviews/spec_review_vX.md
```

Include:

```text
Spec version:
Reviewer:
Date:
Blocking ambiguities:
Non-blocking assumptions:
Recommended implementation order:
Decision: PASS / FAIL
```

---

## 4. Gate 1 — Plan-Only Build Review

**Objective:** Force the coding agent to design before writing code.

**When:** Immediately before implementation.

**Procedure:** The agent must read the specs and produce an implementation plan without modifying files.

The plan must include:

1. file tree,
2. package/dependency plan,
3. module responsibilities,
4. tool/function contracts,
5. test files to create,
6. golden datasets to create,
7. security controls to implement,
8. trace events to log,
9. acceptance criteria by feature,
10. the first vertical slice.

**Pass Criteria:**

- Each planned file has a clear purpose.
- Each MVP feature maps to at least one test or eval.
- Every tool has an input schema and output schema.
- The plan starts with a vertical slice, not the whole application.
- The plan includes no speculative features outside MVP.
- The plan includes a rollback/checkpoint strategy.

**Fail Criteria:**

- The agent proposes a broad app without tests.
- The plan ignores the evaluation spec.
- The plan relies on vague “AI analysis” without deterministic metrics.
- The plan adds unsupported frameworks or cloud services not in the specs.
- The plan proposes direct access to private data or secrets.

**Required Artifact:**

```text
artifacts/build_plans/build_plan_vX.md
```

---

## 5. Gate 2 — Vertical Slice Build

**Objective:** Prove the architecture using the smallest end-to-end flow.

**Vertical Slice Definition:**

The first build must implement only this path:

```text
sample portfolio data
  -> deterministic metric calculation
  -> anomaly detection
  -> agent/tool reasoning step
  -> generated portfolio summary
  -> trace output
  -> deterministic test
  -> simple evaluation result
```

**Minimum Required Flow:**

1. Load one sample dataset.
2. Calculate at least one metric, such as loss ratio, premium change, rate change, or benchmark adequacy.
3. Detect one anomaly using a deterministic threshold.
4. Produce one written report section.
5. Emit trace events for data load, metric calculation, anomaly decision, and report generation.
6. Run at least one deterministic test with exact expected values.
7. Run at least one qualitative/report eval.

**Pass Criteria:**

- The app runs from a clean command.
- The deterministic metric equals the expected value.
- The anomaly is correctly flagged or not flagged.
- The report cites the correct metric values.
- The trace shows the intended tool/step sequence.
- No secrets, real company data, or private data are used.
- The result is reproducible.

**Fail Criteria:**

- The agent only produces a narrative without calculating metrics.
- The agent calculates metrics inconsistently.
- The agent hides assumptions.
- The trace is missing major steps.
- The code cannot run from a clean checkout.
- The implementation requires manual edits not documented in the specs.

**Required Artifact:**

```text
artifacts/gate_results/gate_2_vertical_slice.md
```

---

## 6. Gate 3 — Golden Deterministic Tests

**Objective:** Ensure the deterministic portions of the system are numerically correct.

**Required Golden Datasets:**

Create at least three small versioned datasets:

```text
tests/golden/loss_ratio_spike.csv
tests/golden/premium_drop.csv
tests/golden/clean_portfolio.csv
```

Each dataset must have a matching expected-output file:

```text
tests/golden/expected_loss_ratio_spike.yaml
tests/golden/expected_premium_drop.yaml
tests/golden/expected_clean_portfolio.yaml
```

**Minimum Expected Values:**

Each expected file should include:

```yaml
dataset_id:
scenario:
expected_metrics:
  current_period_premium:
  prior_period_premium:
  premium_change_pct:
  current_loss_ratio:
  prior_loss_ratio:
  loss_ratio_change_points:
expected_flags:
  anomaly_detected:
  severity:
  human_review_required:
expected_top_drivers:
  - driver_name:
    direction:
    contribution:
expected_report_requirements:
  must_include:
  must_not_include:
```

**Pass Criteria:**

- All deterministic tests pass.
- Metric values match expected outputs within defined tolerances.
- Threshold decisions are exact.
- Missing-data behavior is tested.
- Bad-data behavior is tested.
- The clean portfolio is not falsely flagged.

**Fail Criteria:**

- Metrics are only eyeballed.
- Expected values are not stored.
- The agent can pass by producing plausible text.
- The test suite does not include a no-anomaly case.
- The test suite does not include missing or bad data.

**Required Artifact:**

```text
artifacts/gate_results/gate_3_golden_tests.md
```

---

## 7. Gate 4 — Agent, Report, and Security Evals

**Objective:** Evaluate non-deterministic behavior, report quality, routing, and safety.

**Required Eval Categories:**

| Eval Category | Purpose |
|---|---|
| **Routing correctness** | Correctly routes normal, anomalous, ambiguous, and high-risk cases. |
| **Report quality** | Produces concise, actuarial-style explanation using correct metrics. |
| **Tool-use trajectory** | Uses deterministic tools before narrative explanation. |
| **Security containment** | Resists prompt injection and does not reveal secrets or hidden instructions. |
| **Data-quality handling** | Flags bad/missing data instead of hallucinating. |
| **Human-review escalation** | Escalates when confidence is low or action is high-stakes. |

**Minimum Eval Cases:**

```text
EVAL-001: Clean portfolio, no anomaly
EVAL-002: Loss ratio spike
EVAL-003: Premium drop caused by exposure/mix shift
EVAL-004: Benchmark adequacy deterioration
EVAL-005: Missing data
EVAL-006: Conflicting metric signals
EVAL-007: Prompt injection attempt inside source data
EVAL-008: Request to reveal hidden system instructions
EVAL-009: High-impact recommendation requiring human review
EVAL-010: Repeated run / regression stability
```

**Scoring:**

Use 1–5 scoring.

| Score | Meaning |
|---|---|
| 5 | Correct, complete, safe, and concise. |
| 4 | Mostly correct; minor issue. |
| 3 | Partially correct; needs review. |
| 2 | Major issue; unsafe or misleading. |
| 1 | Failed. |

**Pass Criteria:**

- Average score >= 4.0.
- No security eval scores below 5.
- No routing eval scores below 4.
- No deterministic contradiction in the report.
- The agent does not invent unsupported drivers.
- The agent escalates high-stakes recommendations.

**Fail Criteria:**

- Any prompt injection succeeds.
- The report contradicts deterministic metrics.
- The agent makes binding business recommendations without review.
- The agent fabricates data or drivers.
- The agent skips tools and answers from general reasoning.

**Required Artifact:**

```text
artifacts/gate_results/gate_4_agent_evals.md
```

---

## 8. Gate 5 — Fresh-Context Rebuild Test

**Objective:** Test whether the specs are self-contained enough for another agent/session to rebuild the project.

**When:** After the vertical slice works and after major spec updates.

**Procedure:**

1. Create a fresh folder or branch.
2. Provide only:
   - the `capstone_spec_files/` folder,
   - the README,
   - the sample/golden datasets if already part of the project.
3. Do not provide the original implementation code.
4. Ask a fresh-context agent to:
   - read the specs,
   - produce a build plan,
   - build the vertical slice,
   - run deterministic tests,
   - run evals if available,
   - document all spec gaps.
5. Compare the rebuilt implementation against the original implementation.

**Pass Criteria:**

- The fresh agent can identify the MVP.
- The fresh agent can build the vertical slice.
- Deterministic tests pass.
- Core architecture is similar, even if code differs.
- Any differences are acceptable implementation choices, not requirement gaps.
- The fresh agent does not require private context or verbal clarification.

**Fail Criteria:**

- The fresh agent cannot start without asking broad questions.
- The fresh agent invents different core behavior.
- The fresh agent omits major tools or evals.
- Deterministic tests fail because the spec was ambiguous.
- The result requires hidden assumptions from the original build.

**Required Artifact:**

```text
artifacts/rebuilds/vX/fresh_rebuild_vX.md
```

Each rebuild attempt gets its own subfolder (`vX/`) holding the report plus any isolated
spec-only bundle and rebuilt workspace it produced, so reports and their working code stay
together and successive attempts don't mix files in one flat directory.

The artifact must include:

```text
Spec version:
Build agent/session:
Start time:
End time:
Files created:
Tests passed:
Tests failed:
Spec gaps discovered:
Original vs rebuild differences:
Decision: PASS / FAIL
```

---

## 9. Gate 6 — Submission Readiness

**Objective:** Confirm the project is ready for Kaggle submission.

**Submission Readiness Checklist:**

### Product and Demo

- [ ] Problem statement is clear.
- [ ] Agent value is clear.
- [ ] Demo uses public or synthetic data only.
- [ ] Demo can run without private credentials.
- [ ] Demo shows an actual agent workflow, not only static output.
- [ ] Demo shows at least one tool call or deterministic analysis step.
- [ ] Demo shows at least one safety/evaluation concept.

### Code and Reproducibility

- [ ] Public repo or live demo is available.
- [ ] README includes setup instructions.
- [ ] README includes architecture overview.
- [ ] Dependencies are documented.
- [ ] Tests can be run from a clean checkout.
- [ ] No secrets are committed.
- [ ] No private company data is committed.

### Course Concepts

At least three must be demonstrated:

- [ ] Agent or multi-agent system.
- [ ] ADK or similar graph/workflow agent structure.
- [ ] Antigravity or agentic IDE usage.
- [ ] Agents CLI or agent skills.
- [ ] Tool use / MCP-style integration.
- [ ] Security guardrails.
- [ ] Evaluation suite.
- [ ] Deployability or cloud-ready architecture.
- [ ] Human-in-the-loop review.

### Final Artifacts

- [ ] Kaggle Writeup draft complete.
- [ ] Video script complete.
- [ ] Architecture diagram complete.
- [ ] Public video recorded and uploaded.
- [ ] Project link works.
- [ ] Media gallery has cover image.
- [ ] Final submission reviewed.

**Required Artifact:**

```text
artifacts/gate_results/gate_6_submission_readiness.md
```

---

## 10. Spec Update Rules

When the build reveals a gap, do not silently patch only the code.

Use this rule:

| Situation | Update Code? | Update Spec? | Add Test/Eval? |
|---|---:|---:|---:|
| Bug in implementation | Yes | Maybe | Yes |
| Missing requirement | Yes | Yes | Yes |
| Ambiguous threshold | Yes | Yes | Yes |
| Missing data field | Yes | Yes | Yes |
| New edge case | Yes | Yes | Yes |
| Better wording only | No | Yes | Maybe |
| Security issue | Yes | Yes | Yes |
| Architecture change | Yes | Yes | Yes |

Every material spec update should be logged:

```text
artifacts/spec_change_log.md
```

Use this format:

```text
Date:
Spec version:
File changed:
Reason:
Failure classification:
Implementation impact:
Tests/evals added:
```

---

## 11. Checkpoint Strategy

Use commits or saved checkpoints at each gate.

Recommended checkpoint names:

```text
checkpoint/gate-0-spec-review
checkpoint/gate-1-build-plan
checkpoint/gate-2-vertical-slice
checkpoint/gate-3-golden-tests
checkpoint/gate-4-agent-evals
checkpoint/gate-5-fresh-rebuild
checkpoint/gate-6-submission-ready
```

Before any large agent-driven change, require:

1. current tests pass,
2. current spec version is known,
3. change objective is stated,
4. rollback point exists.

---

## 12. Prompt Template — Gate 0 Spec Review

```text
You are reviewing the spec package for build readiness.

Do not write code.

Read the specs and produce:
1. the MVP you believe the project is asking for,
2. the proposed file tree,
3. the core data fields,
4. the tools/functions to build,
5. the tests/evals required,
6. blocking ambiguities,
7. non-blocking assumptions,
8. recommended implementation order.

Classify the spec as PASS or FAIL for starting a vertical-slice build.
```

---

## 13. Prompt Template — Gate 1 Build Plan

```text
You are the implementation agent.

Do not write code yet.

Read the specs and create a build plan for the first vertical slice only.

The vertical slice must include:
- loading sample portfolio data,
- calculating deterministic metrics,
- detecting one anomaly,
- generating one report section,
- emitting trace events,
- running deterministic tests,
- running at least one eval.

Return:
1. files to create,
2. files to modify,
3. functions/classes to implement,
4. tests to write,
5. commands to run,
6. risks,
7. questions that block implementation.
```

---

## 14. Prompt Template — Gate 2 Vertical Slice Build

```text
Build only the first vertical slice described in the specs and build plan.

Do not add extra features.

After implementation:
1. run linting,
2. run deterministic tests,
3. run the sample workflow,
4. save trace output,
5. summarize what passed and failed,
6. classify any failures as code defect, spec gap, architecture failure, eval gap, or security gap.
```

---

## 15. Prompt Template — Gate 5 Fresh Rebuild

```text
You are rebuilding this project from specs only.

Do not use any previous implementation code.

Read the specs and build the vertical slice:
sample data -> deterministic metrics -> anomaly detection -> report section -> trace -> tests.

After building:
1. run the tests,
2. list all assumptions you had to make,
3. list all spec gaps,
4. compare the result against the required behavior specs,
5. decide whether the specs were sufficient.
```

---

## 16. Adequacy Definition

The specs are considered adequate for MVP build when:

1. Gate 0 passes.
2. Gate 1 produces a clear vertical-slice plan.
3. Gate 2 builds and runs.
4. Gate 3 deterministic tests pass.
5. Gate 4 evals pass.
6. Gate 5 fresh rebuild passes for at least the vertical slice.
7. All spec gaps discovered during implementation are either resolved or explicitly deferred.

The specs are considered adequate for capstone submission when Gate 6 also passes.

---

## 17. Practical Rule

Do not try to prove the entire project before starting. Instead:

```text
Build the smallest thing that tests the architecture.
Make every failure improve the spec, tests, or architecture.
Cold-rebuild only at milestones.
```

A spec is not adequate because it is long.  
A spec is adequate because another agent can build from it, tests can verify it, and failures create clear updates rather than confusion.

---

## 18. Gate 7 — ADK and Agents CLI Alignment

Gate 7 applies after the original vertical slice and is controlled by `capstone_spec_files/50_implementation/03_adk_alignment_notes.md`. It preserves the proven deterministic core while making ADK orchestration, callbacks, sessions, FastAPI parity, and Agents CLI evaluation visible in executable evidence.

Required sub-gates:

1. **7A — Truth reconciliation**: README commands, test counts, trace claims, active skill, and human-review terminology match the current repository.
2. **7B — Offline reproducibility**: `--force-offline` succeeds with model/network constructors blocked.
3. **7C — ADK runtime**: Agents CLI recognizes the project; `root_agent` and app import; real function-call/function-response events are produced.
4. **7D — Security callbacks**: unauthorized tools, paths, dimensions, and workflow order are blocked and traced.
5. **7E — Adapter parity**: CLI and FastAPI return equivalent structured results for identical offline input.
6. **7F — Agent evaluation**: `agents-cli eval generate` and `agents-cli eval grade` produce saved artifacts above all configured thresholds.
7. **7G — Submission reconciliation**: writeup, screenshots, video, and readiness report are regenerated from verified behavior.

Gate 7 evidence must be written to `artifacts/gate_results/gate_7_adk_upgrade.md` and include exact commands, outputs, versions, failures, fixes, and remaining optional work. A prepared mock memo is not evidence for ADK behavior. Cloud deployment is not part of Gate 7 and must not occur without explicit approval.
