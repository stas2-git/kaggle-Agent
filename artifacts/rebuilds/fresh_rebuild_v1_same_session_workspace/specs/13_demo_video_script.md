# Five-Minute Demo Video Script

## Format

Screen recording with voiceover. No camera required.

## Target length

4:30 to 5:00 minutes.

## Video objective

Convince judges that:

1. The problem is real.
2. An agent is the right solution.
3. The project actually works.
4. The implementation uses course concepts.
5. The project is safe, evaluated, and reproducible.

## Segment 1: Problem and value, 0:00-0:35

Show: title slide.

Narration:

"This project is an Actuarial Portfolio Monitoring Agent. Portfolio review is usually a manual process: analysts refresh data, check dashboards, compare periods, investigate drivers, and write notes. Dashboards show what changed, but they do not reliably perform the first-pass investigation or create a review-ready memo. This agent automates that first-pass triage using synthetic insurance portfolio data."

## Segment 2: Why an agent, 0:35-1:05

Show: simple workflow diagram.

Narration:

"An agent is useful here because the workflow is multi-step. It needs to validate the data, calculate metrics, decide whether something changed materially, investigate drivers, summarize evidence, and decide when a human should review. The LLM does not calculate the numbers. Deterministic tools calculate the numbers, and the agent coordinates the review."

## Segment 3: Architecture, 1:05-1:45

Show: architecture diagram from `03_agent_architecture.md`.

Narration:

"The architecture has five layers: a data layer with synthetic CSV extracts, a deterministic tool layer, an agent reasoning layer, a security and review gate, and an output layer that writes a report and trace. The agent also uses a portfolio-monitoring skill that defines the review procedure and output style."

## Segment 4: Live demo, 1:45-3:25

Show: terminal or app.

Steps:

1. Show synthetic dataset quickly.
2. Run command:
   ```bash
   python -m portfolio_agent.run --input data/eval/loss_ratio_spike.csv --latest-month 2026-06
   ```
3. Show terminal output.
4. Open generated markdown report.
5. Highlight top finding, driver analysis, human review flag.
6. Open trace JSON briefly.

Narration:

"Here I run the agent on a synthetic dataset with an intentionally planted loss ratio spike. The agent validates the data, calculates metrics, detects the anomaly, investigates the drivers, and creates a report. The finding is marked high severity and requires human review. The trace shows the tool calls and review gate, so the result is auditable."

## Segment 5: Security and evaluation, 3:25-4:20

Show: evaluation scorecard and security test cases.

Narration:

"The project includes local evaluations. The eval set covers a green portfolio, a loss ratio spike, a premium drop, missing columns, prompt injection in a notes field, forbidden file reads, and requests for unavailable metrics. Security controls include synthetic data only, no committed secrets, path allowlists, disabled external actions, and prompt-injection detection."

## Segment 6: Build process and course concepts, 4:20-4:50

Show: repo structure and specs folder.

Narration:

"I built this using spec-driven development. The repository includes product specs, behavior specs, tool contracts, security specs, evaluation specs, and a reusable Agent Skill. This demonstrates agent workflow design, tools, skills, security, evaluation, and deployability."

## Segment 7: Close, 4:50-5:00

Show: final report.

Narration:

"The result is not a replacement for actuarial judgment. It is a repeatable monitoring assistant that makes first-pass portfolio review faster, safer, and better documented."

## Recording checklist

Before recording:
- Run the demo once successfully.
- Clear terminal clutter.
- Increase font size.
- Keep the repo open to the key files.
- Prepare the output report in advance in case the live run takes too long.
- Keep the video under 5 minutes.

## Visual assets to create

1. Title slide.
2. Architecture diagram.
3. Screenshot of report output.
4. Screenshot of evaluation scorecard.
5. Optional screenshot of skill folder.
