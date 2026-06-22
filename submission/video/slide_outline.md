# Slide Outline: Actuarial Portfolio Monitoring Agent

This document defines the visual layout and bullets for the video presentation slides.

---

### Slide 1: Title Card
* **Title**: Actuarial Portfolio Monitoring Agent
* **Subtitle**: Streamlining Book of Business Triage with AI Agents
* **Bullets**:
  * Track: Agents for Business
  * Bounded Multi-Step Agentic Workflow
  * Bounded Tool-First Implementation
* **Suggested Visual**: Slick dark-mode design with clean typography and modern gradients.
* **Narration**: Segment 1 ("Routine monthly monitoring of insurance books of business...")

---

### Slide 2: Why an Agent?
* **Title**: Why an Agent? Beyond Dashboards
* **Bullets**:
  * Automates conditional multi-step workflows (Data Load -> Validation -> Metrics -> Drivers -> Report)
  * Restricts LLMs to narrative explanation (Zero numerical hallucination)
  * Screens note fields for prompt-injection threats
  * Human-in-the-loop triggers for high severity findings
* **Suggested Visual**: Visual flowchart showing how dashboards stop at charts, whereas agents take actions.
* **Narration**: Segment 2 ("This workflow is highly suited to an agentic approach...")

---

### Slide 3: Five-Layer Architecture
* **Title**: Bounded Five-Layer System Design
* **Bullets**:
  * **Data Layer**: Aggregate aggregate aggregates CSVs
  * **Security Layer**: Path traversal checks & injection signature scanning
  * **Deterministic Tools**: Python math engines for ratios & weighted averages
  * **Agent Reasoning Layer**: Pydantic schema-bound Gemini synthesis
  * **Output Layer**: Observability traces & markdown review reports
* **Suggested Visual**: Simplified diagram of the 5-layer architecture.
* **Narration**: Segment 3 ("The agent's architecture consists of five modular layers...")

---

### Slide 4: Interactive Live Demo (NY Spike Case)
* **Title**: Live Demo: Underwriting Triage Walkthrough
* **Bullets**:
  * Ingested: `loss_ratio_spike.csv`
  * Anomaly Engine: Flagged high severity Loss Ratio increase (+35.0% points)
  * Driver Slicer: Decomposed movement to `state = NY`, `policy_year = 2025`
  * Synthesis memo generated: Cites drivers, caveats, follow-up questions
* **Suggested Visual**: Screenshot of terminal command execution or side-by-side view of CSV and generated markdown memo.
* **Narration**: Segment 4 ("Let's look at the pipeline in action...")

---

### Slide 5: Security & Verification
* **Title**: Rigorous Verification & Safety Policies
* **Bullets**:
  * **Path Constraints**: Restricts reads to approved directories (`data`, `examples`, `tests/golden`)
  * **Injection Filters**: Traps instruction overrides in untrusted text fields
  * **Golden Tests**: Compares math results to YAML benchmarks
  * **Trace Scorecards**: Evaluates agent behavior across 10 security/logic cases
* **Suggested Visual**: Pytest run results showing all 25 tests passing.
* **Narration**: Segment 5 ("Security and privacy are vital...")

---

### Slide 6: Business Value & Roadmap
* **Title**: Real Business Impact & Next Steps
* **Bullets**:
  * **Efficiency**: Speeds up rutin reviews from hours to seconds
  * **Auditability**: Complete trace trail of tool steps and decisions
  * **Roadmap**: Direct BigQuery connections, automated Cloud Run triggers, and email triggers
* **Suggested Visual**: Summary list of next steps and actuarial disclaimer.
* **Narration**: Segment 6 ("The Actuarial Portfolio Monitoring Agent is not a replacement...")
