# Video Generation Execution Report ✅

This report summarizes the outcome of assemble_video.py (stage 3). Pytest/eval/live-demo
status below reflects the last build_slides.py (stage 1) run, not this run - assemble_video.py
does not re-verify the agent, it only combines already-reviewed specs.

## 1. Verification Status (from the last build_slides.py run)
- **Pytest Suite**: PASS ✅ (59 passed, 6 warnings in 0.77s)
- **Offline Evaluations**: PASS ✅ (11/11 evaluation cases passed)
- **Vertical-Slice Review Run**: PASS ✅
- **Verification generated at**: `2026-07-06T13:46:11`

## 2. This Assembly Run
- **Voiceover TTS Source**: `Mixed: Gemini API TTS (cached) (segments [1, 2, 3, 7]); local macOS say (segments [4, 5, 6])`
- **Model Used**: `Mixed (see audio_source)`
- **Voice / Config Name**: `Mixed (say=Samantha for previewed segments)`
- **Speech Rate (macOS Say only)**: `170 WPM`
- **Security Secret Audit Scan**: PASS ✅

## 3. Timing Measurements & Bounds Checks
- **Narration Audio Duration**: 193.585 seconds
- **Final Video Duration**: 193.531 seconds
- **Absolute Duration Difference**: 0.054 seconds
- **Duration Boundary Status**: PASS (Within 1.0s limit) ✅
- **Video Output Path**: `<workspace>/submission/02_video/draft_demo_video.mp4`

## 4. Generated Outputs
- **Slides** (7 reviewable segment visuals, `submission/02_video/slides/rendered/`): `slide_1.png` ... `slide_7.png`
- **Auditable Command Logs** (from the last build_slides.py run, `submission/02_video/backend/evidence/demo_outputs/`):
  - Pytest Log: `pytest_output.txt`
  - Scorecard Log: `eval_output.txt`
  - Review Run Log: `run_output.txt`
- **Bonus Evidence** (not part of the 7-slide deck, `submission/02_video/backend/evidence/demo_cards/`): `pytest_card.png`, `trace_card.png`

## 5. Security Audit Findings
- **Result**: SUCCESS. No raw API keys, AIza key signatures, un-redacted workspace paths, or un-scrubbed `.env` references were found.

## 6. Verification Commands
Confirm outputs locally using:
- Pytest passing verification: `uv run pytest`
- Check generated trace exists: `cd project_build && ls outputs/traces/`
- View generated reports: `cd project_build && ls outputs/reports/`
