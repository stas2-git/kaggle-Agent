# Kaggle Writeup Draft

## Title

Actuarial Portfolio Monitoring Agent

## Subtitle

An agentic workflow for detecting portfolio trend changes, investigating drivers, and producing review-ready actuarial summaries.

## Track

Agents for Business

## Draft writeup

### 1. Problem

Insurance portfolio monitoring is a recurring business workflow that combines data processing, metric review, trend detection, and professional judgment. Analysts and actuaries often need to refresh data, compare the latest month to prior periods, identify material movements, investigate drivers, and write a summary for stakeholders.

Dashboards are useful, but they usually stop at visualization. They show that something changed, but they do not always perform the first-pass investigation or produce a consistent review memo. This creates a practical gap: important changes may be missed, routine reviews take time, and the documentation of why something was flagged can vary from person to person.

### 2. Solution

The Actuarial Portfolio Monitoring Agent turns this workflow into a bounded agentic process. The agent reads a synthetic insurance portfolio extract, validates the data, calculates key monitoring metrics, detects material changes, investigates likely drivers, and generates a concise review report.

The agent is designed as a first-pass triage assistant. It does not make underwriting, pricing, or reserving decisions. Instead, it identifies review-worthy signals and explains the supporting evidence.

### 3. Why agents?

This problem is well suited to an agent because the workflow is multi-step and conditional. A static dashboard can display metrics, but an agent can coordinate the next steps:

- Validate whether the data is usable.
- Decide which metrics changed materially.
- Choose the right driver investigation.
- Summarize evidence in business language.
- Escalate high-severity or uncertain findings to human review.
- Preserve a trace of the workflow.

The design separates deterministic calculations from LLM reasoning. Python tools calculate metrics and anomaly statistics. The LLM interprets tool outputs and drafts the narrative.

### 4. Architecture

The architecture has five layers:

1. **Synthetic data layer**: local CSV portfolio extracts.
2. **Tool layer**: deterministic tools for loading, validation, metrics, anomaly detection, and driver analysis.
3. **Agent layer**: coordinates the workflow and synthesizes findings.
4. **Safety layer**: path allowlists, prompt-injection detection, no external side effects, and human review gates.
5. **Output layer**: markdown report and JSON trace.

A reusable Agent Skill, `portfolio-monitoring`, defines the review procedure and output style. This keeps the agent focused without overloading every prompt with all procedural details.

### 5. Demo

The demo uses a synthetic portfolio dataset with an intentionally planted loss ratio spike. The agent detects the change, investigates the drivers, and generates a report showing that the movement is concentrated in specific portfolio slices. Because the severity is high, the agent marks the finding for human review and recommends follow-up questions.

The demo also shows a prompt-injection case where a text field in the dataset attempts to instruct the agent to ignore its rules. The agent treats the text as untrusted data, does not obey it, and flags the run for review.

### 6. Security and privacy

The project uses synthetic data only. The MVP does not connect to production databases, send emails, or perform external side effects. File access is limited to approved local directories. Report and trace outputs are written only to approved output folders.

Text fields in the data are treated as untrusted. The agent screens for injection-like language and avoids following instructions embedded in data. High-severity findings, low-confidence summaries, and security flags require human review.

### 7. Evaluation

The project includes local evaluation cases covering:

- A green portfolio with no material anomalies.
- A high-severity loss ratio spike.
- A severe premium decline.
- A missing required column.
- Prompt injection in a notes field.
- A forbidden request to read local secrets.
- A request for an unavailable metric.

Evaluations check routing correctness, report quality, security containment, calculation consistency, and trace completeness.

### 8. Course concepts demonstrated

This project demonstrates several course concepts:

- Agent workflow design with deterministic tools.
- Agent Skills for reusable procedural knowledge.
- Spec-driven development with product, behavior, security, and evaluation specs.
- Security controls, prompt-injection handling, and human-in-the-loop review.
- Local evaluation over traces and final outputs.
- Deployability through a reproducible public repository.

### 9. Value

The agent makes portfolio monitoring faster and more consistent. It does not replace the actuary; it gives the actuary a structured first-pass review with evidence, caveats, and follow-up questions. This is the kind of workflow where agents can create practical business value: not by making final decisions, but by coordinating repetitive analysis and producing a transparent starting point for expert review.

## Suggested screenshots

1. Architecture diagram.
2. Terminal run or app screen.
3. Generated report.
4. Evaluation scorecard.
5. Skill folder / specs folder.

## Word count target

Aim for 1,200-1,800 words. The limit is 2,500 words.
