# Five-Minute Demo Video Script

## Format
Screen recording with voiceover narration. No camera required.

## Target Length
4:30 to 5:00 minutes.

---

## Script Breakdown

### Segment 1: Problem and Business Value (0:00 - 0:30)
* **Visual**: Title slide with project name: *Actuarial Portfolio Monitoring Agent*.
* **Narration**:
  > "Hi everyone. Insurance portfolio monitoring is a critical but highly repetitive risk-management process. Analysts and actuaries spend hours every month extracting transactional data, validating it, calculating metrics, identifying anomalies, and writing review memos. Dashboards help visualize the trends, but they don't perform the initial triage or write the draft explanations. That's where our Actuarial Portfolio Monitoring Agent comes in. It automates this first-pass review, transforming raw aggregates into structured, actuary-ready memos."

---

### Segment 2: Why an Agent is the Right Solution (0:30 - 1:00)
* **Visual**: Flowchart diagram highlighting the conditional, multi-step nature of the workflow (Data Load -> Validation -> Metrics -> Anomaly? -> Driver Slices -> LLM Synthesis -> Report).
* **Narration**:
  > "Why use an agent instead of a simple static script? Because this workflow requires conditional reasoning and safety enforcement. The agent must check files for path traversals, inspect notes fields for prompt injections, decide which driver slicing tool to call based on the specific metric flagged, and synthesize the narrative. Crucially, the LLM is forbidden from calculating the numbers. Deterministic tools compute the metrics, while the LLM is restricted to narrative synthesis, ensuring absolute numerical correctness."

---

### Segment 3: System Architecture Overview (1:00 - 1:45)
* **Visual**: Architecture Diagram showing the 5 layers: Data, Security, Tools, Agent, and Output. Point to the portable `portfolio-monitoring` skill folder.
* **Narration**:
  > "Here is our system architecture. It is built in five isolated layers. The data layer handles synthetic aggregates. The security layer blocks path traversal and text injection. The deterministic tool layer aggregates premiums and losses and calculates weighted rate changes, retention, and benchmark adequacy index. If an anomaly is flagged, the driver tool calculates exact dimensional contributions. The agent reasoning layer handles structured LLM calls, guided by a portable agent skill that enforces professional language. Finally, the output layer generates a markdown report and a full JSON trace."

---

### Segment 4: Live Demo Walkthrough (1:45 - 3:45)
* **Visual**: Terminal window, followed by opening the generated Markdown report.
* **Demonstration Steps**:
  1. Show a quick view of `data/synthetic_portfolio_monthly.csv`.
  2. Run the orchestrator command in terminal:
     ```bash
     python3 -m portfolio_agent.run --input tests/golden/loss_ratio_spike.csv --latest-month 2026-06 --force-offline
     ```
  3. Show the generated report `portfolio_review_2026-06_<run_id>.md`.
  4. Highlight the loss ratio spike flag (rose from 50% to 85%), the driver decomposition (pointing to `state = NY`, `policy_year = 2025` as the 35% contributor), and the human review gate flag set to `Yes` due to high severity.
  5. Briefly display the trace JSON.
* **Narration**:
  > "Let's look at the agent in action. I will run the pipeline on a golden dataset with an aggregate loss ratio spike. The runner validates the schema, aggregates metrics, and flags a high-severity anomaly: the loss ratio in Public D&O rose from 50% to 85%. The agent immediately runs driver slicing, identifying that the entire 35-point increase is concentrated in state NY for policy year 2025. In the generated report, we see the executive summary, data quality checks, metric movement tables, and the NY state drivers. Because this is a high-severity movement, the human review gate is flagged as required, prompting the actuary with target questions."

---

### Segment 5: Security and Evaluations (3:45 - 4:30)
* **Visual**: Text editor showing `test_rebuild.py` or the terminal executing `uv run pytest`.
* **Narration**:
  > "Safety and verification are core to this project. The security layer traps path traversal attempts, and screens notes fields for prompt injections. In our test suite, we run deterministic golden tests verifying premiums, loss ratios, and driver calculations against YAML expectations. We also run evaluation cases simulating malformed CSVs, notes injections, secret disclosure requests, and report metric citations. Our automated pytest suite validates all 25 tests, verifying that the agent resists injections and maintains metric accuracy."

---

### Segment 6: Value & Closing (4:30 - 5:00)
* **Visual**: Slide of the generated report with the actuary disclaimer.
* **Narration**:
  > "This agent is not a replacement for actuarial judgment or formal reserving opinions. It is a repeatable, secure triage assistant that handles the tedious parts of portfolio monitoring. By automating data aggregation, trend checks, driver slicing, and draft writing, it allows actuaries to focus their time on deep analysis and pricing actions. The code, datasets, and specifications are fully open, reproducible, and ready for submission. Thank you."
