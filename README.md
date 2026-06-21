# Actuarial Portfolio Monitoring Agent

An agentic actuarial triage assistant designed to monitor synthetic insurance portfolios, calculate monitoring metrics, detect trend anomalies, decompose concentration drivers, and draft actuary-ready review memos with full trace logs and security containment.

---

## Short Project Summary
This agent automates the first-pass triage review of monthly insurance books of business. It runs deterministic calculations, flags material movements (such as premium drops or loss ratio spikes), decomposes these anomalies across available dimensions (like state or policy year), and utilizes LLM reasoning to synthesize the findings into a review report. The entire run is logged in a structured JSON trace for auditability.

---

## Problem Statement
Insurance portfolio monitoring is a critical but highly repetitive business process. Analysts and actuaries must:
1. Extract monthly transaction aggregates.
2. Validate columns and check data quality.
3. Compute metrics (such as loss ratios, rate changes, and retention levels).
4. Identify trend changes compared to prior periods.
5. Decompose changes across dimensions (slicing by state, coverage, or underwriter) to find drivers.
6. Write a summary memo outlining flags and recommended follow-ups.

Dashboards (like Tableau or PowerBI) visualize the data but do not perform the initial investigation or write draft reviews. The time spent on repetitive data extraction and first-draft report writing reduces the time experts can allocate to deeper analysis and strategic pricing.

---

## Why an Agent?
A static dashboard or script is insufficient for this workflow because the process is conditional and reasoning-based:
* **Validation & Security**: The agent must screen incoming data columns and notes fields for malicious text (e.g., prompt injections) and trap path traversal attempts.
* **Reasoning-Bound Investigation**: If a material anomaly is detected, the agent chooses to run specific driver tools, isolating the dimensions showing the highest concentration of change.
* **Actuarial Synthesis**: The agent translates mathematical outputs and driver contributions into conservative, professional language rather than marketing fluff, preparing the draft for final human sign-off.
* **Workflow Traceability**: The agent maintains a complete trace of its tool-use decisions, making the entire reasoning trajectory inspectable and testable.

The architecture enforces a strict boundary: **deterministic tools compute all numbers**, while the **LLM is restricted to synthesizing narratives** based on those calculated numbers. The agent cannot fabricate metrics.

---

## Architecture Overview

The system is organized into a modular pipeline:

```
[Synthetic CSV] 
       │
       ▼
[Load & Security Scan] ──► Path validations / Traversal check / Note Injection check
       │
       ▼
[Metrics Tool] ──────────► Sums & weighted average calculations (by month/segment)
       │
       ▼
[Anomaly Engine] ────────► Compares current vs prior month against configuration thresholds
       │
       ▼
[Driver Slicing Tool] ───► Calculates dimensional contribution to the metric change
       │
       ▼
[LLM synthesis] ─────────► Gemini-2.5-flash synthesizes review findings (using Pydantic models)
       │
       ▼
[Report & Trace Output] ─► Outputs outputs/reports/review.md & outputs/traces/run.json
```

### Components:
1. **Security Guardrails**: Traps path traversals and uses regex filters to scan input notes for instructions to override system logic.
2. **Deterministic Tools**: Python/Pandas functions to calculate premiums, incurred losses, loss ratios, weighted rate changes, retention, and benchmark adequacy.
3. **Driver Decomposition**: Computes the exact mathematical contribution of each category (e.g. `state = NY`) to the total segment movement.
4. **LLM Synthesis Node**: Invokes Gemini via `google-genai` with structured output schemas (or offline stubs for test environments) to compile summaries, interpretations, caveats, and follow-ups.
5. **Observability Trace**: Logs all tool calls, inputs, outputs, flags, and durations to a JSON trace.

---

## Course Concepts Demonstrated

This capstone project implements key agentic design patterns:
1. **Agent Tool Design**: Bound tools with schemas, strict inputs/outputs, and local file access policies.
2. **Agent Skills**: Defined custom skill boundaries (`skills/`) to separate procedural knowledge from model parameters.
3. **Security Guardrails**: Path containment, untrusted notes screening, and human-in-the-loop review triggers.
4. **Evaluation Methodology**: Built a parameterized test suite covering routing, security, data quality, and metrics.
5. **Deployability**: Structured package setups with `uv` virtual environments, allowing reproducible local execution.

---

## Setup Instructions

This project uses `uv` for python package and virtual environment management.

### Prerequisite
Install `uv` (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Sync Environment
Clone the repository and run sync to activate the virtual environment and install all dependencies:
```bash
uv sync
source .venv/bin/activate
```

---

## How to Run the Vertical Slice & Demo

To execute the portfolio monitoring workflow end-to-end for a monthly book:

```bash
uv run python3 -m portfolio_agent.run --input "data/synthetic_portfolio_monthly.csv" --latest-month "2026-06"
```

If you do not have a `GEMINI_API_KEY` set, or wish to bypass API rate limits, run the pipeline in offline mode:
```bash
uv run python3 -m portfolio_agent.run --input "data/synthetic_portfolio_monthly.csv" --latest-month "2026-06" --force-offline
```

### Outputs
* **Markdown Report**: Written to `outputs/reports/portfolio_review_<month>_<run_id>.md`
* **JSON Trace**: Written to `outputs/traces/run_trace_<run_id>.json`

---

## How to Run Tests

To execute the unit tests, golden tests, and security tests:
```bash
uv run pytest
```

This runs:
* **Unit Tests**: Calculations and tool outputs in `tests/test_tools.py`.
* **Security Tests**: Path traversal block and note injection scanners in `tests/test_security.py`.
* **Golden Scenario Tests**: Verifies metrics, driver concentrations, and report templates against expectations in `tests/test_golden.py`.

---

## How to Run Evals

To run the local evaluation script checking the 10 core evaluation scenarios:
```bash
FORCE_OFFLINE=1 uv run python3 -m tests.eval.run_eval
```

This runs scenarios covering:
* Green portfolios (stable metrics).
* Severe loss ratio spikes and premium drops.
* Ingestion of malformed CSVs (missing required columns).
* Prompt injections in note fields and secret disclosure containment.
* Quality checks of the generated report content.

---

## Security & Privacy Notes
* **Local Sandboxing**: No external HTTP requests are made during data processing or tool calls. The only network call is the optional outbound request to the Gemini API during LLM synthesis.
* **No committed secrets**: All API keys are loaded via the local environment or `.env` files (which are excluded from version control via `.gitignore`).
* **Path Validation Allowlist**: File access is strictly validated against an approved allowlist (`data`, `examples`, `tests/golden`), preventing path traversal or source code leaks.

---

## Synthetic Data Disclaimer
> [!IMPORTANT]
> This repository uses synthetic data only. All policy, premium, claim, underwriter, and broker data is generated programmatically for demonstration purposes. The reports generated by this agent represent first-pass triage aids only and do not constitute formal actuarial opinions, binding underwriting decisions, or pricing authorizations.

---

## Known Limitations
* **Local-First Scope**: The agent operates on flat CSV extracts. Production deployment would require database connectors (e.g. BigQuery) and workflow runners (e.g. Cloud Run).
* **API Rate Limits**: Real LLM calls can encounter rate limits on free-tier API keys. High-fidelity offline stubs are included to guarantee test reproducibility.
* **Actuarial Interpretations**: The interpretation of driver anomalies is based on default logic and does not replace the nuanced business context of a human underwriter or actuary.

---

## Next Steps & Future Work
1. **BigQuery Tooling**: Replace CSV file readers with structured SQL query tools.
2. **Cloud Run / GKE Deployment**: Package the agent into a container with automated trigger webhooks.
3. **Stakeholder Notifications**: Add human review verification gates before sending email/Slack notifications.
