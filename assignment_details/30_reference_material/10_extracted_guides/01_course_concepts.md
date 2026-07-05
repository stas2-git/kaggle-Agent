# Course Concepts

This course centered on building agentic systems from clear intent, strong context, and measurable behavior. For this capstone, these concepts define the expected quality floor, not optional polish.

Read the baseline first: [`00_capstone_baseline_expectations.md`](00_capstone_baseline_expectations.md)

## Main Ideas Covered

- Vibe coding as intent-driven development: use natural-language goals, specs, and iterative review to shape software.
- Agent architecture: define the role, tools, instructions, data contracts, and boundaries before treating code as final.
- Tool interoperability: agents become useful when they can call reliable tools and exchange structured context.
- Skills and progressive disclosure: keep reusable domain knowledge in small, loadable units instead of flooding every prompt.
- Security and evaluation: guardrails, human gates, prompt-injection defenses, tests, and evals are part of the agent design.
- Production readiness: deployment, observability, traces, rollback, and documentation turn a demo into a reviewable system.

## Baseline Capstone Signals

- The project has a readable spec hierarchy and does not rely on code alone to explain behavior.
- Tools perform the deterministic work and expose structured outputs.
- The agent has explicit boundaries around when it reasons, when it calls tools, and when it flags human review.
- Safety and evaluation are visible in the project files, not only mentioned in the writeup.
- A reviewer can run or inspect evidence without private data or credentials.

## How This Project Uses Those Ideas

- Specs in `capstone_spec_files/` are the source of truth.
- `portfolio_agent/` is the runnable implementation of those specs.
- Tests and eval files show measurable behavior instead of relying only on demo screenshots.
- Submission material explains the learning journey and points reviewers to the evidence.
