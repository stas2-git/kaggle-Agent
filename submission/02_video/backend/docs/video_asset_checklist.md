# Video Asset Checklist

This checklist tracks all required elements for compiling and publishing the final Kaggle capstone demo video, separated by automated and manual steps.

**Status as of 2026-07-06: all automated assets below are generated and present in
`../../slides/rendered/`, `../evidence/`, and `../../story/audio/current/`** (verified -
see `../../segment_tracker.md` for whether their *content* is still accurate, which is a
separate question from whether the file exists). The latest `draft_demo_video.mp4` uses
Gemini audio for all seven segments.

---

## 1. Automated Assets (Compiled by `build_slides.py` + `assemble_video.py`)

All 7 segment visuals now live uniformly in `../../slides/rendered/slide_1.png` ...
`slide_7.png`, regardless of whether they're hand-authored or built from real pipeline
evidence:

* [x] **Slide 1: Title Card** — Actuarial Portfolio Monitoring Agent (`slide_1.png`)
* [x] **Slide 2: Workflow Concept** — Beyond Dashboards (`slide_2.png`)
* [x] **Slide 3: Architecture Layers** — Five-Layer System Diagram (`slide_3.png`)
* [x] **Slide 4: Live Demo — Pipeline Execution** — Anomaly, metric movement, review-gate, and trace result (`slide_4.png`)
* [x] **Slide 5: Live Demo — Actuarial Memo** — Driver-concentration, follow-up, and audit-artifact summary (`slide_5.png`)
* [x] **Slide 6: Rigorous Safety & Verification** — Combined pytest and offline evaluation results (`slide_6.png`)
* [x] **Slide 7: Conclusion** — Real Business Impact & Roadmap (`slide_7.png`)
* [x] **Bonus evidence (not a segment visual)**: Pytest console output summary (`../evidence/demo_cards/pytest_card.png`), structured observability trace excerpt (`../evidence/demo_cards/trace_card.png`)
* [x] **Audio Voiceover files** — Current audio files exist (`story/audio/current/` mp3s + `story/audio/current/details/gemini_segments/` wav+metadata).
* [x] **Final all-Gemini voiceover** — Gemini TTS regenerated for segments 4-6 after the story rewrite.
* [x] **Subtitles** — Timing-aligned subtitle file (`captions.srt`)
* [x] **Video Compilation** — Stitched final video (`draft_demo_video.mp4`)
* [x] **Safety Audit** — Automated scanning report confirming no secrets, API keys, or un-redacted local paths are leaked (`evidence/video_generation_report.md`)

---

## 2. Optional Manual Polish Assets (Human-in-the-Loop)

* [x] **Custom AI Voiceover Finalization** — Latest draft uses Gemini audio for all seven segments (see `../../HANDOFF.md`).
  ChatTTS and XTTS v2 local-cloning alternatives were explored and archived, not adopted.
* [ ] **Terminal/UI Screen Recordings** — Optional replacement of text cards with actual captured MP4 clips:
  * Ingestion CSV file preview.
  * Command terminal running the pipeline.
  * Scrolling view of the compiled markdown review report.
  * Running pytest and evaluation scorecard.

---

## 3. Final YouTube Upload Settings

* [ ] **Privacy Setting**: Set to **Unlisted** (or Public as permitted).
* [ ] **Title**: *Kaggle AI Agents Capstone: Actuarial Portfolio Monitoring Agent*
* [ ] **Description**:
  * Include a short summary of the project.
  * Link to public repository (when ready).
  * Add the Actuarial Disclaimer: *"This video shows a capstone project using synthetic data only. It is not an official actuarial opinion or business advice."*
* [ ] **Subtitles**: Upload `captions.srt` to YouTube captions settings.
