# Video Generation Execution Report ✅

This report summaries the execution and outcomes of the audio-driven video generation pipeline.

## 1. Pipeline Execution Status
- **Pytest Suite**: PASS ✅
- **Offline Evaluations**: PASS ✅
- **Vertical-Slice Review Run**: PASS ✅
- **Voiceover TTS Source**: `Gemini API TTS (Segment-Based)`
- **Model Used**: `gemini-3.1-flash-tts-preview`
- **Voice / Config Name**: `Kore`
- **Speech Rate (macOS Say only)**: `170 WPM`
- **Final Video Assembler**: PASS ✅
- **Security Secret Audit Scan**: PASS ✅

## 2. Timing Measurements & Bounds Checks
- **Narration Audio Duration**: 213.463 seconds
- **Final Video Duration**: 213.400 seconds
- **Absolute Duration Difference**: 0.063 seconds
- **Duration Boundary Status**: PASS (Within 1.0s limit) ✅
- **Video Output Path**: `/Users/stan/Library/CloudStorage/GoogleDrive-staskhalitov@gmail.com/My Drive/keggle Agent/submission/02_video/draft_demo_video.mp4`

## 3. Generated Outputs
- **Auditable Command Logs** (saved in `submission/02_video/evidence/demo_outputs/`):
  - Pytest Log: `pytest_output.txt`
  - Scorecard Log: `eval_output.txt`
  - Review Run Log: `run_output.txt`
- **Rendered Demo Cards** (saved in `submission/02_video/evidence/demo_cards/`):
  - `pytest_card.png`
  - `eval_card.png`
  - `run_card.png`
  - `report_card.png`
  - `trace_card.png`

## 4. Security Audit Findings
- **Result**: SUCCESS. No raw API keys, AIza key signatures, or un-scrubbed `.env` references were found.

## 5. Verification Commands
Confirm outputs locally using:
- Pytest passing verification: `uv run pytest`
- Check generated trace exists: `cd project_build && ls outputs/traces/`
- View generated reports: `cd project_build && ls outputs/reports/`
