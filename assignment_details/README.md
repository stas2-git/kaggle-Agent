# Assignment Details

This folder is the capstone assignment context pack. A human or LLM should be able to open this README and understand the assignment, the course depth behind it, the level of the course examples, and where to find supporting detail only when needed.

This is not the runnable app and it is not the public submission package. Use [`../project_build/`](../project_build/) for the implementation, [`../spec_files/`](../spec_files/) for canonical project specs, and [`../submission/`](../submission/) for Kaggle-facing assets.

## Assignment Brief

The Kaggle capstone asks participants to build an AI agent that solves a practical real-world problem and demonstrates concepts from the 5-day AI Agents: Intensive Vibe Coding course with Google.

For this repository, the project is the **Actuarial Portfolio Monitoring Agent**: an agentic actuarial triage assistant that reads synthetic insurance portfolio data, validates it, calculates deterministic monitoring metrics, detects material movements, investigates likely drivers, and drafts an actuary-ready review memo with traceable evidence.

The final public submission must include:

- a Kaggle Writeup of 2,500 words or fewer;
- a Media Gallery with a required cover image;
- an attached public YouTube video of 5 minutes or fewer;
- an attached public project link, preferably a working product or interactive demo, with a public code repository acceptable as fallback;
- a selected competition track;
- final submission before the deadline: **July 6, 2026 at 11:59 PM PT**.

The judging emphasis is split between pitch and implementation:

- **Pitch, problem, solution, and value:** why the problem matters, why agents are central to the solution, clarity of video, and clarity of writeup.
- **Implementation, architecture, and code:** meaningful agent design, tool use, code quality, documentation, reproducibility, safety, and evidence that the system works.

The capstone must visibly apply at least three course concepts. The local project is designed to show more than the minimum: ADK-style agent structure, deterministic tools, agent skills, security controls, evaluation, observability, reproducible local runs, and deployment awareness.

## Course Depth

The course was not just a prompt-writing overview. It moved from vibe-coded prototypes toward production-grade agent engineering across 5 days. See [`whitepapers/README.md`](whitepapers/README.md) for the day-by-day concepts and the specific protocols/frameworks each day introduced.

## Example Level From The Course

The codelabs set the expected project floor. They were more substantial than toy scripts and included runnable agent workspaces, tool boundaries, security checks, evaluation, deployment paths, and reviewer-facing workflows. See [`codelabs/README.md`](codelabs/README.md) for what each codelab covers and its capstone relevance.

For this capstone, that means the portfolio-monitoring agent should read as a small reviewable agent system: deterministic computation where facts matter, LLM synthesis only where reasoning adds value, explicit security boundaries, tests/evals, observable traces, and a clear README/demo story.

## Where To Find Details

This folder is organized by topic, not by document type. Each topic's dense, reusable material is pulled up next to `details/` rather than buried inside it — [`whitepapers/notes/`](whitepapers/notes/) and [`codelabs/specs/`](codelabs/specs/). `details/` holds the raw source text, original documents, and runnable code. Open `details/` only when the current task needs more evidence than the overview and its notes/specs already provide.

| Topic | Overview | Dense reference | Raw source |
|---|---|---|---|
| Course whitepapers (concepts, days 1-5) | [`whitepapers/README.md`](whitepapers/README.md) | [`whitepapers/notes/`](whitepapers/notes/) | [`whitepapers/details/`](whitepapers/details/) |
| Course codelabs (implementation patterns) | [`codelabs/README.md`](codelabs/README.md) | [`codelabs/specs/`](codelabs/specs/) | [`codelabs/details/`](codelabs/details/) - instructions and runnable projects |
| Capstone assignment (rules, baseline, submission) | [`capstone_project/README.md`](capstone_project/README.md) | - | [`capstone_project/details/`](capstone_project/details/) |

| Need | Read |
|---|---|
| Runnable app, commands, tests, and outputs | [`../project_build/README.md`](../project_build/README.md) |
| Canonical product, architecture, data, tool, quality, and submission specs | [`../spec_files/00_README_SPEC_INDEX.md`](../spec_files/00_README_SPEC_INDEX.md) |
| Kaggle writeup, video assets, and final checklist | [`../submission/README.md`](../submission/README.md) |
| This project's own build-session notes and architecture history (not course material) | [`../project_build/notes/README.md`](../project_build/notes/README.md) |
| Superseded or packaged artifacts | [`90_archive/README.md`](90_archive/README.md) |

## LLM Reading Rule

Do not review this whole folder by default.

1. Read this README first.
2. If judging capstone readiness, read [`capstone_project/README.md`](capstone_project/README.md).
3. If checking submission mechanics, read [`capstone_project/SUBMISSION_REQUIREMENTS.md`](capstone_project/SUBMISSION_REQUIREMENTS.md).
4. If checking course alignment, read [`whitepapers/README.md`](whitepapers/README.md) and [`codelabs/README.md`](codelabs/README.md).
5. Use the `details/` subfolder under any topic only to verify a specific claim or implementation pattern.

## Folder Map

```text
assignment_details/
|-- README.md           # This assignment brief and reading guide
|-- whitepapers/        # Course concept whitepapers: overview + notes/ (dense) + details/ (raw source/PDFs)
|-- codelabs/           # Course codelabs: overview + specs/ (dense) + details/ (instructions, runnable projects)
|-- capstone_project/   # Capstone assignment: overview + source text/PDFs
`-- 90_archive/         # Superseded or packaged artifacts
```
