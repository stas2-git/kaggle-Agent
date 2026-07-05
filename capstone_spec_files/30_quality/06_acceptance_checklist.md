# Acceptance Checklist

## Product readiness

- [ ] The project has a clear problem statement.
- [ ] The agent solves a real workflow problem.
- [ ] The demo can run in under 5 minutes.
- [ ] The final report is understandable to a business audience.
- [ ] The project does not claim to replace actuarial judgment.

## Implementation readiness

- [ ] Deterministic tools calculate all numeric metrics.
- [ ] The LLM does not invent numbers.
- [ ] Tool contracts are implemented or clearly documented.
- [ ] The agent produces a markdown report.
- [ ] The agent produces a JSON trace.
- [ ] The repo has setup instructions.
- [ ] The project runs from a clean checkout.
- [ ] `portfolio_agent.agent` exports a Google ADK `root_agent`.
- [ ] The ADK application name matches the `portfolio_agent` directory.
- [ ] Model-callable tools have typed parameters, clear docstrings, and JSON-serializable dictionary responses.
- [ ] A clean portfolio avoids unnecessary driver investigation calls.
- [ ] The portfolio-monitoring skill is present under `skills/portfolio_monitoring/` and used by the runtime.
- [ ] CLI and FastAPI invoke the same application service.
- [ ] `--force-offline` completes while model/network constructors are blocked.

## Security readiness

- [ ] Synthetic/deidentified data only.
- [ ] No API keys committed.
- [ ] `.env` is ignored.
- [ ] `.env.example` is provided.
- [ ] File reads are allowlisted.
- [ ] File writes are allowlisted.
- [ ] External side effects are disabled or require human approval.
- [ ] Prompt-injection test passes.
- [ ] High-severity anomalies require human review.

## Evaluation readiness

- [ ] Green portfolio eval passes.
- [ ] Loss ratio spike eval passes.
- [ ] Premium drop eval passes.
- [ ] Missing column eval passes.
- [ ] Prompt injection eval passes.
- [ ] Forbidden file read eval passes.
- [ ] No invented metrics eval passes.
- [ ] Evaluation scorecard is saved.
- [ ] Pytest is used for deterministic code and contracts, not exact LLM prose.
- [ ] Agents CLI evaluation traces were generated from the real ADK application.
- [ ] Agents CLI grading covers task success, trajectory, tool use, final response, hallucination, and safety.
- [ ] Numeric-consistency and trace-completeness custom metrics pass at 100%.
- [ ] A baseline/candidate comparison shows no unreviewed regression.

## Documentation readiness

- [ ] README explains setup.
- [ ] README explains architecture.
- [ ] Specs are included.
- [ ] Data dictionary is included.
- [ ] Security notes are included.
- [ ] Evaluation method is included.
- [ ] Screenshots are included.
- [ ] README commands execute exactly as written.
- [ ] Reported test/eval counts match current command output.
- [ ] Human review is described as advisory unless true ADK pause/resume is implemented.
- [ ] Offline results are not presented as live agent-quality evidence.

## FastAPI and packaging readiness

- [ ] `/healthz` and `/readyz` expose no secrets and require no live model call.
- [ ] `POST /api/reviews` validates the request and returns `PortfolioReviewResult`.
- [ ] FastAPI contains no actuarial calculations or duplicate policy logic.
- [ ] Makefile targets for install, offline run, API, test, integration, lint, and eval are documented.
- [ ] Dockerfile runs the service on `PORT`, default `8080`.
- [ ] No deployment, API enablement, IAM, or infrastructure change occurred without approval.

## Video readiness

- [ ] Video is under 5 minutes.
- [ ] Problem is explained in first 30 seconds.
- [ ] Architecture diagram is shown.
- [ ] Working demo is shown.
- [ ] Report output is shown.
- [ ] Security/evaluation is mentioned.
- [ ] Course concepts are explicitly named.
- [ ] No private information appears on screen.

## Kaggle submission readiness

- [ ] Writeup is under 2,500 words.
- [ ] Track selected.
- [ ] Cover image attached.
- [ ] YouTube video attached.
- [ ] Public project link attached.
- [ ] Final submission button clicked before deadline.
