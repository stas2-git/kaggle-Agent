# Demo Evidence Capture Runbook

This document defines the process for capturing visual demonstration evidence. The primary, automated method captures stdout and markdown/JSON logs directly to image cards. Manual screen recording is supported as an optional polish step.

---

## 1. Primary Automated Evidence (Default)

`build_slides.py` (stage 1 of the pipeline - see `../../README.md`) automatically runs the
verification steps and captures the console output. It extracts the logs and generates visual
card overlays - the three that narrate real pipeline evidence go straight into the 7-slide
deck reviewers look at; the other two are bonus proof not shown in the video:
- **Pipeline execution card** (segment 4 visual): Runs the pipeline on `tests/golden/loss_ratio_spike.csv` and renders the anomaly, metric movement, review-gate, and trace result to `../../slides/rendered/slide_4.png`.
- **Memo output card** (segment 5 visual): Extracts the generated markdown review memo into a driver-concentration, follow-up, and audit-artifact summary at `../../slides/rendered/slide_5.png`.
- **Safety and verification card** (segment 6 visual): Automatically runs pytest and the 11-case offline scorecard, then renders a combined headline pass count to `../../slides/rendered/slide_6.png`.
- **Pytest result card** (bonus, not a segment visual): Automatically runs `uv run pytest` and places a headline summary in `../evidence/demo_cards/pytest_card.png`.
- **Trace excerpt card** (bonus, not a segment visual): Exposes the start of the structured trace file to `../evidence/demo_cards/trace_card.png`.

No manual CLI command runs or screenshot actions are required when using `build_slides.py`.

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
* **Private paths**: Do not expose absolute directories showing personal usernames (e.g. `/Users/username/...`). Enforced automatically for the primary path: `common.redact_workspace_paths()` strips the local workspace prefix from every captured command output and file read before it reaches a log or a slide, and `assemble_video.py`'s security scan fails the build if one slips through anyway. Manual recordings still need to self-police this.
* **Local Brain files**: Do not display hidden system prompts or agent run memories from your application data directories.
* **Real Company Data**: Ensure only synthetic books of business are displayed.
