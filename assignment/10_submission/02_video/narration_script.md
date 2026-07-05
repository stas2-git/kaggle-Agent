# Narration Script

This document holds the complete narration script and corresponding visual cues for the 5-minute capstone demo video.

---

### Segment 1: The Business Problem (0:00 - 0:30)
* **Visual Cue**: Slide 1: *Actuarial Portfolio Monitoring Agent - Streamlining Book of Business Review*
* **Voiceover**:
  > "Routine monthly monitoring of insurance books of business is a critical but repetitive risk-management process. Actuaries and analysts must manually load transactional aggregates, compute key metrics, detect anomalies, decompose them by concentration drivers, and compile explanatory reports. Traditional business intelligence dashboards visualize these trends, but they stop at charts. They do not write the explanation or perform the initial triage, creating a time-consuming bottleneck for risk teams."

---

### Segment 2: Why an Agent is the Right Solution (0:30 - 1:00)
* **Visual Cue**: Slide 2: *Why an Agent? Bounded Tool-First Design*
* **Voiceover**:
  > "This workflow is highly suited to an agentic approach because it is multi-step, reasoning-driven, and requires strict security checks. A simple static script cannot dynamically decide how to triage issues. Our agent validates input schema quality, runs safety scans, identifies anomalies, selects the correct driver slicing tools, and compiles findings. To guarantee absolute mathematical correctness, we use a tool-first architecture where deterministic Python tools compute all metrics, and the LLM is restricted only to narrative synthesis."

---

### Segment 3: System Architecture (1:00 - 1:45)
* **Visual Cue**: Slide 3: *Five-Layer Modular Architecture* (Mermaid Flowchart)
* **Voiceover**:
  > "The agent's architecture consists of five modular layers. First, a data layer that ingests synthetic CSV aggregations. Second, a security layer that checks paths and text notes for prompt injections. Third, a deterministic tool layer that calculates premiums, loss ratios, and written-premium-weighted averages for rate changes, retention, and benchmark adequacy. Fourth, an agent reasoning layer that manages Gemini calls and structured schemas. And fifth, an output layer writing a markdown review memo and a complete JSON trace file."

---

### Segment 4: Live Demo Walkthrough (1:45 - 3:45)
* **Visual Cue**: Video Screen: Recording of running the command line pipeline, followed by showing the output markdown report and trace JSON.
* **Voiceover**:
  > "Let's look at the pipeline in action. We run the orchestrator tool on a synthetic dataset containing an aggregate loss ratio spike in the Public D&O segment. The tool validates the columns, calculates metrics, and triggers a high-severity flag because the loss ratio rose from fifty percent to eighty-five percent. The agent immediately calls the driver investigation tool to slice the segment by available dimensions. The mathematical breakdown shows that this spike is entirely concentrated in state New York for the two thousand twenty-five policy year. In the compiled report, we see the executive summary, metrics tables, NY drivers, actuary-facing recommended follow-up questions, and the human review gate flag set to required due to severity. A full trace JSON is saved for auditability."

---

### Segment 5: Security & Evaluations (3:45 - 4:30)
* **Visual Cue**: Slide 4: *Security Controls & Robust Local Evaluation*
* **Voiceover**:
  > "Security and privacy are vital. The security layer blocks path traversals and screens note fields for prompt-injection attacks. In our test suite, we run deterministic tests to match metric and driver math against YAML expectations. We also run evaluation cases simulating malformed CSVs, notes prompt injections, secret disclosure requests, and report quality criteria. Our pytest suite verifies all twenty-five tests pass successfully. Additionally, we run a Gate 5 rebuild test to ensure a fresh agent can recreate this vertical slice from specifications alone, confirming that our specs are complete and self-contained."

---

### Segment 6: Business Value & Next Steps (4:30 - 5:00)
* **Visual Cue**: Slide 5: *Conclusion & Future Work*
* **Voiceover**:
  > "The Actuarial Portfolio Monitoring Agent is not a replacement for professional actuarial opinion or underwriting authority. Instead, it serves as a robust triage assistant that makes routine reviews faster, safer, and thoroughly documented. For future work, we plan to transition from flat CSVs to running direct BigQuery analytical queries, GKE-run containerized scheduling, and email alerts. Thank you."
