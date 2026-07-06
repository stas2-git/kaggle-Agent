# Demo Evidence Capture Runbook

This document defines the process for capturing visual demonstration evidence. The primary, automated method captures stdout and markdown/JSON logs directly to image cards. Manual screen recording is supported as an optional polish step.

---

## 1. Primary Automated Evidence (Default)

The orchestrator script `generate_all.py` automatically runs the verification steps and captures the console output. It extracts the logs and generates visual card overlays:
- **Pytest result card**: Automatically runs `uv run pytest` and places stdout summary in `evidence/demo_cards/pytest_card.png`.
- **Evaluation scorecard card**: Automatically runs the 11-case test scorecard in offline mode and renders the scorecard summary table to `evidence/demo_cards/eval_card.png`.
- **Pipeline Orchestrator execution**: Runs the pipeline on `tests/golden/loss_ratio_spike.csv` and renders logs to `evidence/demo_cards/run_card.png`.
- **Report excerpt card**: Exposes the top section of the generated markdown review memo to `evidence/demo_cards/report_card.png`.
- **Trace excerpt card**: Exposes the start of the structured trace file to `evidence/demo_cards/trace_card.png`.

No manual CLI command runs or screenshot actions are required when using the automated orchestrator.

---

## 2. Optional Manual Screen Recordings (Polish Only)

If you prefer to capture actual screen movement, follow these guidelines:

### Setup & Pre-recording Checks
1. **Increase font sizes**: Set terminal and VS Code font sizes to at least 16pt for readability.
2. **Clear state**: Clear terminal history and run `clear`.
3. **Clean workspace**: Hide personal files, paths, and tabs.

### Capture Steps & Commands
1. **Ingest Data Preview**:
   ```bash
   head -n 5 tests/golden/loss_ratio_spike.csv
   ```
2. **Execute Pipeline Run**:
   ```bash
   uv run python3 -m portfolio_agent.run --input "tests/golden/loss_ratio_spike.csv" --latest-month "2026-06"
   ```
3. **Show Generated Actuarial Report**: Open the compiled markdown memo from the path shown in the execution output.
4. **Show Automated Pytest Verification**:
   ```bash
   uv run pytest
   ```
5. **Show Local Evaluation Scorecard**:
   ```bash
   FORCE_OFFLINE=1 uv run python3 -m tests.eval.run_eval
   ```

---

## 3. Security Boundaries & Forbidden Elements

Whether using automated output cards or manual recordings, you must guarantee that the following are **never shown**:
* **`.env` files**: Never open `.env` or display configuration keys.
* **Credentials**: Never show `GEMINI_API_KEY`, GCP service keys, or passwords.
* **Private paths**: Do not expose absolute directories showing personal usernames (e.g. `/Users/username/...`).
* **Local Brain files**: Do not display hidden system prompts or agent run memories from your application data directories.
* **Real Company Data**: Ensure only synthetic books of business are displayed.
