# Slide Outline: Actuarial Portfolio Monitoring Agent

This document defines the visual layout and supporting ideas for the 7-slide capstone video deck.
The canonical rendered visuals live in `rendered/slide_1.png` through `rendered/slide_7.png`.
Each slide is designed as a visual anchor for the narration: one large idea, a few easy-to-read
supporting cards, and a bottom takeaway for viewers who miss a word in the audio.

Canonical story text lives in `../story/slide_story.yaml`. Exact values on evidence slides
4-6 are generated from the latest `backend/build_slides.py` run; this outline should describe
the shape of those facts, not be treated as the source for current numbers.

---

### Slide 1: Title Card
* **Title**: Actuarial Portfolio Monitoring Agent
* **Hook**: The hard part isn't spotting movement. It's turning movement into judgment.
* **Supporting cards**:
  * Signal
  * Investigation
  * Memo
* **Takeaway**: Monthly monitoring becomes an audit-ready first pass, not a scramble for explanation.
* **Purpose**: Establish the business problem and the core promise.
* **Narration**: Segment 1.

---

### Slide 2: From Dashboard to Decision
* **Title**: From Dashboard to Decision
* **Hook**: Dashboards stop at awareness. Agents can carry the next step.
* **Supporting cards**:
  * Validate
  * Investigate
  * Escalate
* **Takeaway**: The agent chooses the next tool, but every number still comes from deterministic code.
* **Purpose**: Explain why the workflow needs an agent rather than a static chart or script.
* **Narration**: Segment 2.

---

### Slide 3: Autonomy With Boundaries
* **Title**: Autonomy With Boundaries
* **Hook**: The architecture is a bargain: autonomy with boundaries.
* **Supporting cards**:
  * Code computes
  * Gemini explains
  * Human approves
* **Takeaway**: Security gates and Python tools constrain the workflow before Gemini writes the narrative.
* **Purpose**: Show the architecture and course concepts: ADK-style agent orchestration, Gemini synthesis, deterministic tools, schemas, tracing, and security gates.
* **Narration**: Segment 3.

---

### Slide 4: From CSV to Review Gate
* **Title**: From CSV to Review Gate
* **Headline**: A plain CSV becomes a review decision.
* **Visual flow**: CSV -> Validate -> Calculate -> Flag -> Escalate
* **Metric callouts**:
  * Symptom 1: generated loss-ratio movement
  * Symptom 2: generated claim-count movement
  * Review gate: generated human-review decision
* **Takeaway**: The agent does not just flag noise: material signals cross thresholds and trigger human review.
* **Purpose**: Prove the agent can run the workflow end to end.
* **Narration**: Segment 4.

---

### Slide 5: Two Symptoms, One Driver
* **Title**: Two Symptoms, One Driver
* **Headline**: The reveal: both signals point to the same slice.
* **Visual flow**:
  * Loss-ratio signal -> generated concentrated slice
  * Claim-count signal -> generated concentrated slice
  * Driver target -> memo, questions, trace
* **Takeaway**: The reveal is convergence: both signals point to the same concentrated slice, then the memo frames what to review.
* **Purpose**: Show that the agent explains the issue, not just flags it.
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
* **Supporting cards**:
  * Faster triage
  * Clear evidence
  * Human authority
* **Takeaway**: This is a force multiplier for experts, not a substitute for actuarial judgment.
* **Purpose**: Close with practical value, professional boundaries, and next steps.
* **Narration**: Segment 7.
