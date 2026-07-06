# Capstone Project

Read this before judging or changing the project. The course examples establish the expected baseline: the capstone should be more than a script plus a writeup. It should look like a small, reviewable agent system.

For final-submission mechanics (Writeup, media, deadline), see [`SUBMISSION_REQUIREMENTS.md`](SUBMISSION_REQUIREMENTS.md). For how the course whitepapers and codelabs back up this baseline, see [`../whitepapers/README.md`](../whitepapers/README.md) and [`../codelabs/README.md`](../codelabs/README.md).

## Minimum Project Bar

The capstone should demonstrate:

- a clear agent purpose and problem statement;
- a spec-first structure that explains requirements, architecture, contracts, quality, and submission;
- a public README that a reviewer can follow;
- a video/writeup story that shows the agent working, not only describes it.

The implementation-level bar — tools, deterministic/LLM split, guardrails, evaluation, observability, reproducibility, deployment awareness — is the table below, with a concrete codelab-sourced example for each so "the bar" isn't abstract.

## Expected Agent-Level Features & Low-Hanging Fruit

Based on the codelabs, a strong submission should make these patterns visible where relevant. The third column is not aspirational — it's what a codelab already built, so it's a low-cost addition, not a research problem.

| Pattern | Baseline expectation | Codelab-sourced example |
|---|---|---|
| ADK or agent structure | A recognizable root agent or equivalent orchestration boundary. | The workflow is declared as a graph of single-responsibility nodes (`security_screen → route_expense → auto_approve` / `review_agent → request_approval`), not nested control flow. (CL4 Ambient Agent, CL5 Deployment) |
| Tools & data contracts | Tools have bounded inputs/outputs and do the factual work. | Typed Pydantic schemas at every tool/model boundary, including LLM output; one input-normalization function that collapses every transport (dict / JSON string / base64-in-Pub/Sub) into a single internal schema at the boundary. (CL4 Ambient Agent, CL5 Deployment) |
| Deterministic/LLM split | The model reasons or synthesizes; code owns anything that must be reproducible and auditable. | Code owns thresholds/routing/auto-approval eligibility and the LLM can never downgrade a route; a cheap deterministic filter runs before every LLM call (cost-aware gating). (CL4 both, CL5 Deployment) |
| Guardrails | The project has validation, policy checks, or human-review triggers. | Safety-precedence routing (security checks evaluated before business-value routing); "never let the model supply authoritative identity"; a secret-scanning pre-commit gate; a STRIDE threat-model pass producing `threat_model.md`. (CL4 Ambient Agent, CL4 Secure Lifecycle) |
| Human-in-the-loop | Sensitive actions pause for an authorized human decision. | `RequestInput`/interrupt pattern with a unique `interrupt_id`, resumed only on exact interrupt-ID match — never on session/timestamp/"latest event," which is the #1 failure mode both specs call out. (CL4 Ambient Agent, CL5 Frontend) |
| Evaluation | There are tests and eval cases that can fail for meaningful reasons. | 4-5 named scenarios (clean/auto path, threshold edge, high-risk path, malformed/injected input, security containment) graded by LLM-as-judge rubrics, kept separate from deterministic pytest. (CL4 both) |
| Observability | Runs produce traceable evidence, not only final prose. | Structured per-decision log fields (event/run ID, decision path, `decision_source`, latency, final status) — never raw prompts or PII. (CL4 Ambient Agent, CL4 Secure Lifecycle) |
| Reproducibility | The project can run locally with synthetic or safe data. | Every codelab ships local run instructions and a synthetic dataset; no live credentials required to exercise the core logic. |
| Deployment awareness | Even if not deployed, packaging and deployment constraints are documented. | A pre-deploy gate checklist (tests pass, evals meet threshold, region/identity/secrets reviewed, explicit human approval) plus a documented fix-forward rollback plan, since Agent Runtime has no traffic-shifting rollback. (CL5 Deployment) |

For the full reasoning behind each example — algorithms, code shapes, and each spec's extended "production gaps" and fill-in-the-blank "capstone adaptation" worksheet — go straight to the spec:

- [`../codelabs/specs/cl4_ambient_agent_spec.md`](../codelabs/specs/cl4_ambient_agent_spec.md)
- [`../codelabs/specs/cl4_secure_agent_lifecycle_spec.md`](../codelabs/specs/cl4_secure_agent_lifecycle_spec.md)
- [`../codelabs/specs/cl5_agent_runtime_deployment_spec.md`](../codelabs/specs/cl5_agent_runtime_deployment_spec.md)
- [`../codelabs/specs/cl5_agent_frontend_spec.md`](../codelabs/specs/cl5_agent_frontend_spec.md)

Live build status (what's already implemented vs. still open) belongs in [`../../project_build/notes/`](../../project_build/notes/), not here — this checklist documents what the course demonstrated is feasible, not this project's current state.

## Capstone-Specific Interpretation

For the Actuarial Portfolio Monitoring Agent, the baseline is:

- synthetic insurance data is loaded safely;
- actuarial metrics are computed deterministically;
- anomalies are detected against documented thresholds;
- drivers are decomposed by relevant dimensions;
- the LLM writes a conservative review memo from computed facts;
- prompt-injection and path-traversal risks are handled;
- outputs include both a markdown report and structured trace;
- tests/evals prove the workflow across green, anomaly, malformed-data, and security scenarios.

## LLM Instruction

Do not treat the shallowest runnable demo as sufficient. Before recommending changes or judging readiness, check whether the project shows the baseline above and whether the README, specs, tests, traces, writeup, and video all tell the same story.

## Details

Original capstone wording, rules, and timeline: [`details/`](details/)

| Document | Purpose |
|---|---|
| [`details/highlevel_summary.txt`](details/highlevel_summary.txt) | Course outline, daily topics, and learning goals. |
| [`details/capstone_project_spec.txt`](details/capstone_project_spec.txt) | Tracks, required deliverables, evaluation rubric, judges, and timeline. |
| [`details/capstone_rules.txt`](details/capstone_rules.txt) | Competition legal terms: eligibility, data use, prizes, and IP/winner obligations. |
| [`details/extra_notes.txt`](details/extra_notes.txt) | Codelab excerpt on automated linting and local Agents CLI evaluation (not writeup/demo advice). |
| [`details/agent_building_methods_extraction.txt`](details/agent_building_methods_extraction.txt) | Agent architecture, prompting, routing, and coordination patterns. |
| Original PDF/RTF files | Local-only source documents, excluded from the public repo. |
