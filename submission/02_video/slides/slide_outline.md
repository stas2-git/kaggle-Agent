# Slide Outline: Actuarial Portfolio Monitoring Agent

This document defines the visual layout and supporting ideas for the capstone video deck.
The canonical rendered visuals live in `rendered/slide_0.png` through `rendered/slide_7.png`.
Each slide is designed as a visual anchor for the narration: one large idea, a few easy-to-read
supporting cards, and a bottom takeaway for viewers who miss a word in the audio.

Canonical story text lives in `../story/slide_story.yaml`. Exact values on evidence slides
4-6 are generated from the latest `backend/build_slides.py` run; this outline should describe
the shape of those facts, not be treated as the source for current numbers.

---

### Slide 0: Title Card
* **Title**: Actuarial Portfolio Monitoring Agent
* **Subtitle**: Kaggle Agents Capstone
* **Date**: July 6, 2026
* **Purpose**: Give the viewer a clean opening beat before the problem setup appears.
* **Narration**: First portion of segment 1 audio.

---

### Slide 1: Title Card
* **Title**: Actuarial Portfolio Monitoring Agent
* **Hook**: The hard part isn't spotting movement. It's turning movement into judgment.
* **Supporting cards**:
  * Manual load
  * Metric movement
  * Memo bottleneck
* **Takeaway**: Monthly monitoring becomes an audit-ready first pass, not a scramble for explanation.
* **Purpose**: Establish the business problem and the core promise.
* **Narration**: Remainder of segment 1 audio.

---

### Slide 2: From Dashboard to Decision
* **Title**: From Dashboard to Decision
* **Hook**: Dashboards stop at awareness. Agents can carry the next step.
* **Supporting cards**:
  * Validate input
  * Choose tool
  * Escalate review
* **Takeaway**: The agent chooses the next tool, but every number still comes from deterministic code.
* **Purpose**: Explain why the workflow needs an agent rather than a static chart or script.
* **Narration**: Segment 2.

---

### Slide 3: Autonomy With Boundaries
* **Title**: Autonomy With Boundaries
* **Hook**: Autonomy only works when the boundaries are explicit.
* **Layer cards**:
  * Data intake
  * Security scan
  * Python tools
  * Gemini synthesis
  * Report and trace
* **Takeaway**: The system constrains what Gemini can do, so experts can trust what it says.
* **Purpose**: Show the architecture and course concepts: ADK-style agent orchestration, Gemini synthesis, deterministic tools, schemas, tracing, and security gates.
* **Narration**: Segment 3.

---

### Slide 4: From CSV to Review Gate
* **Title**: From CSV to Review Gate
* **Headline**: Example: June 2026 CSV triggers review.
* **Example case**:
  * File: `loss_ratio_spike.csv`
  * Latest month: `2026-06`
  * Question: Does this need human review?
* **Visual flow**: Example input -> Agent run -> Review decision
* **Metric callouts**:
  * Symptom 1: generated loss-ratio movement
  * Symptom 2: generated claim-count movement
  * Review gate: generated human-review decision
* **Takeaway**: The agent does not just flag noise: material signals cross thresholds and trigger human review.
* **Purpose**: Show the actual agent run path for this example, so the slide adds concrete execution evidence after the architecture slide.
* **Narration**: Segment 4.

---

### Slide 5: Two Symptoms, One Driver
* **Title**: Two Symptoms, One Driver
* **Headline**: The reveal: both signals point to the same slice.
* **Visual flow**:
  * Two anomalies detected: generated loss-ratio movement and claim-count movement
  * Agent decomposes both movements by state, coverage, underwriter, and policy year
  * Both paths converge on the same generated concentrated slice
  * Same slice -> focused review, better questions, auditable trace
* **Takeaway**: The reveal is convergence: both signals point to the same concentrated slice, then the memo frames what to review.
* **Purpose**: Show that the agent explains where to look first, not just that something crossed a threshold.
* **Narration**: Segment 5.

---

### Slide 6: Proof, Not Vibes
* **Title**: Proof, Not Vibes
* **Headline**: Tests, evals, and scans back the claim.
* **Verification pillars**:
  * generated deterministic-test headline
  * generated scenario-eval headline
  * generated secret-scan status
* **Takeaway**: The demo story is backed by deterministic tests, scenario evals, and generated-asset scanning.
* **Purpose**: Demonstrate reliability, security, and local evaluation discipline.
* **Narration**: Segment 6.

---

### Slide 7: Audit-Ready First Pass
* **Title**: Audit-Ready First Pass
* **Hook**: From monthly scramble to audit-ready first pass.
* **Closing claim**: Experts decide. Evidence travels with the memo.
* **Roadmap**:
  * Now: CSV triage
  * Next: BigQuery analytics
  * Next: Scheduled runs
  * Next: Email alerts
* **Takeaway**: This is a force multiplier for experts, not a substitute for actuarial judgment.
* **Purpose**: Close with practical value, professional boundaries, and next steps.
* **Narration**: Segment 7.
