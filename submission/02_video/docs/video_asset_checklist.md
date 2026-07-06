# Video Asset Checklist

This checklist tracks all required elements for compiling and publishing the final Kaggle capstone demo video, separated by automated and manual steps.

---

## 1. Automated Assets (Compiled by `generate_all.py`)

* [ ] **Slide 1: Title Card** — Actuarial Portfolio Monitoring Agent (Slide Image)
* [ ] **Slide 2: Workflow Concept** — Beyond Dashboards (Why an Agent Slide)
* [ ] **Slide 3: Architecture Layers** — Five-Layer System Diagram (Slide Image)
* [ ] **Slide 4: Live Demo Title** — Underwriting Triage Walkthrough (Slide Image)
* [ ] **Card 1: Pipeline Execution** — Orchestration CLI output summary (Demo Card)
* [ ] **Card 2: Actuarial Memo** — Generated markdown report excerpt (Demo Card)
* [ ] **Card 3: Observability Trace** — Structured JSON trace excerpt (Demo Card)
* [ ] **Slide 5: Verification Title** — Rigorous Verification & Safety Policies (Slide Image)
* [ ] **Card 4: Pytest Logs** — Console output of passing unit/integration tests (Demo Card)
* [ ] **Card 5: Scorecard Logs** — Scorecard table of passing evaluation cases (Demo Card)
* [ ] **Slide 6: Conclusion** — Real Business Impact & Roadmap (Slide Image)
* [ ] **Audio Voiceover** — macOS native voice narration track (`audio/narration.mp3`)
* [ ] **Subtitles** — Approximate timing-aligned subtitle file (`captions.srt`)
* [ ] **Video Compilation** — Stitched slideshow draft video (`draft_demo_video.mp4`)
* [ ] **Safety Audit** — Automated scanning report confirming no secrets or API keys are leaked (`video_generation_report.md`)

---

## 2. Optional Manual Polish Assets (Human-in-the-Loop)

* [ ] **Custom AI Voiceover** — Optional replacement of macOS Samantha voice with high-fidelity ElevenLabs/Google Cloud voice.
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
