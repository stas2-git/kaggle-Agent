# Capstone Baseline Expectations

Read this before judging or changing the project. The course examples establish the expected baseline: the capstone should be more than a script plus a writeup. It should look like a small, reviewable agent system.

## Minimum Project Bar

The capstone should demonstrate:

- a clear agent purpose and problem statement;
- a spec-first structure that explains requirements, architecture, contracts, quality, and submission;
- deterministic tools for factual or numeric work;
- an LLM role limited to reasoning, routing, or synthesis where it adds value;
- security boundaries for file paths, untrusted text, secrets, and risky actions;
- observable traces or logs that show what the agent did;
- tests for deterministic behavior and evals for agent behavior;
- reproducible local setup and run commands;
- a public README that a reviewer can follow;
- a video/writeup story that shows the agent working, not only describes it.

## Expected Agent-Level Features

Based on the codelabs, a strong submission should make these patterns visible where relevant:

| Pattern | Baseline expectation |
|---|---|
| ADK or agent structure | There is a recognizable root agent or equivalent orchestration boundary. |
| Tools | Tools have bounded inputs/outputs and do the factual work. |
| Guardrails | The project has validation, policy checks, or human-review triggers. |
| Evaluation | There are tests and eval cases that can fail for meaningful reasons. |
| Observability | Runs produce traceable evidence, not only final prose. |
| Reproducibility | The project can run locally with synthetic or safe data. |
| Deployment awareness | Even if not deployed, packaging and deployment constraints are documented. |

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
