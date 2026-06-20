# Capstone Submission Strategy

## Recommended track

**Agents for Business**

This is the best fit because the project solves a business workflow problem with direct cost, quality, and decision-support value. The problem is not generic data analysis. It is a repeatable actuarial monitoring workflow that normally requires manual extraction, spreadsheet review, and judgment.

## Project title

**Actuarial Portfolio Monitoring Agent**

## Subtitle

An agentic workflow for detecting portfolio trend changes, investigating drivers, and producing an actuary-ready review memo.

## Problem statement

Actuaries and portfolio managers often review book performance through monthly dashboards, SQL extracts, spreadsheets, and ad hoc notes. This process is slow and uneven. The same portfolio metrics must be refreshed repeatedly, material changes can be missed, and the first-pass investigation often depends on a person remembering where to look.

The agent addresses this by turning the monitoring process into a repeatable workflow:

1. Load portfolio data.
2. Validate data quality.
3. Calculate monitoring metrics.
4. Detect material changes.
5. Investigate likely drivers.
6. Draft a concise review memo.
7. Route high-severity or low-confidence findings to human review.

## Why an agent?

A static dashboard can show that a metric changed. An agent can coordinate the workflow around the change:

- Decide which metrics deserve attention.
- Call tools to investigate changes by segment, state, year, attachment, layer, or underwriter.
- Summarize evidence in plain language.
- Distinguish normal movement from review-worthy exceptions.
- Escalate uncertain or high-risk findings to a human.
- Preserve a trace of how it reached its conclusion.

## Required submission assets

The final submission should include:

1. **Kaggle Writeup**
   - 2,500 words or fewer.
   - Track selected: Agents for Business.
   - Include problem, solution, architecture, demo screenshots, and implementation notes.

2. **Media Gallery**
   - Cover image required.
   - Include architecture diagram and one or two screenshots of the agent output.

3. **Public YouTube video**
   - 5 minutes or less.
   - Screen recording with voiceover is enough; no camera required.

4. **Public project link**
   - Preferred: public GitHub repository with setup instructions.
   - Optional: live demo if deployable without login/paywall.

## Scoring strategy

### Category 1: Pitch, problem, solution, value

The submission should make the problem intuitive even to a non-actuary:

- A portfolio has many moving pieces.
- Dashboards show numbers, but not always what changed or why.
- A monitoring agent can perform the first-pass review and produce a consistent memo.

### Category 2: Implementation and architecture

The implementation should show:

- Meaningful agent behavior, not just a chatbot.
- Tool calls with structured inputs/outputs.
- Deterministic calculation tools separate from LLM reasoning.
- Security controls and human review gates.
- Evaluation cases and trace logs.
- Clear documentation and reproducibility.

## Three strongest course concepts to highlight

1. **Spec-driven development**
   - Show that the project was designed from specs before implementation.
   - Include product, behavior, security, evaluation, and deployment specs.

2. **Agent tools and skills**
   - Tools perform deterministic work.
   - A skill teaches the agent the procedural logic of actuarial trend investigation.

3. **Security and evaluation**
   - Use synthetic data.
   - Add prompt-injection tests.
   - Evaluate routing correctness, trend detection, data validation, and report quality.

## Ideal demo story

A monthly portfolio extract arrives. The agent detects that loss ratio increased materially in one segment. It investigates and finds that the change is concentrated in a specific business segment and policy year, with premium decreasing while incurred losses increased. The agent creates a review note, flags the issue as high priority, and recommends human follow-up.

## Submission positioning

Do not present the project as an actuarial model that replaces actuaries. Present it as a monitoring and triage workflow that makes actuarial review more consistent, faster, and better documented.
