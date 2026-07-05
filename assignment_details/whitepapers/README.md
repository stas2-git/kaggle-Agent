# Whitepapers

The 5-day course shipped a whitepaper each day. This page is the extracted, high-level summary; open [`details/`](details/) only to verify original wording or check a specific claim.

Read the capstone baseline first: [`../capstone_project/README.md`](../capstone_project/README.md)

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

- Specs in [`../../spec_files/`](../../spec_files/) are the source of truth.
- `portfolio_agent/` is the runnable implementation of those specs.
- Tests and eval files show measurable behavior instead of relying only on demo screenshots.
- Submission material explains the learning journey and points reviewers to the evidence.

## Details

| Day | Extracted text | Original PDF |
|---|---|---|
| 1 - Vibe coding intro | [`details/day1_vibe_coding_intro.txt`](details/day1_vibe_coding_intro.txt) | [`details/source_documents/day1 whitepaper.pdf`](details/source_documents/day1%20whitepaper.pdf) |
| 2 - Agent tools & interoperability | [`details/day2_agent_tools_interop.txt`](details/day2_agent_tools_interop.txt) | [`details/source_documents/day2 Agent Tools & Interoperability_Day_2.pdf`](details/source_documents/day2%20Agent%20Tools%20%26%20Interoperability_Day_2.pdf) |
| 3 - Agent skills | [`details/day3_agent_skills.txt`](details/day3_agent_skills.txt) | [`details/source_documents/day3 Agent Skills_Day_3.pdf`](details/source_documents/day3%20Agent%20Skills_Day_3.pdf) |
| 4 - Security & evaluation | [`details/day4_security_evaluation.txt`](details/day4_security_evaluation.txt) | [`details/source_documents/day4 Vibe Coding Agent Security and Evaluation_Day_4.pdf`](details/source_documents/day4%20Vibe%20Coding%20Agent%20Security%20and%20Evaluation_Day_4.pdf) |
| 5 - Spec-driven production dev | [`details/day5_spec_driven_production_dev.txt`](details/day5_spec_driven_production_dev.txt) | [`details/source_documents/Day5 Spec_Driven production grade dev.pdf`](details/source_documents/Day5%20Spec_Driven%20production%20grade%20dev.pdf) |
