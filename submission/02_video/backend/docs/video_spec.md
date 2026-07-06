# Video Specification: Actuarial Portfolio Monitoring Agent

This document defines the specification and quality gates for the automated capstone demo video.

---

## 1. Core Metadata

* **Project Title**: Actuarial Portfolio Monitoring Agent
* **Sub-track**: Agents for Business
* **Target Video Length**: Under 5 minutes (ideal: 4:30 - 4:50)
* **Visual Format**: Slides/title cards and screen-recording evidence (no camera required)
* **Audio Format**: Text-to-speech voiceover narration (no human voice required)
* **TTS workflow**: two-tier - macOS native `say` (free, unlimited) for iterating on wording,
  Gemini API TTS (`gemini-3.1-flash-tts-preview`, voice `Kore`, ~10/day quota) for the final
  recording. See `../../README.md` for the exact commands. The current `draft_demo_video.mp4`
  uses the Gemini tier.

---

## 2. Required Sections

The video script and slides must cover the following sections in order. This is now 7
segments (the canonical breakdown lives in `../../narrative/slide_narration_segments.yaml`;
the two Live Demo segments below used to be one, split for pacing):

1. **Problem (segment 1)**: Explains the manual overhead of routine monthly portfolio monitoring and the limitations of static dashboards.
2. **Solution (segment 2)**: Explains how the agent automates validation, metrics calculation, anomaly detection, and review synthesis.
3. **Architecture (segment 3)**: Visualizes the 5 bounded layers of the system (Data, Security, Tools, Agent, Output).
4. **Live Demo: Pipeline Execution (segment 4)**: Demonstrates running the pipeline and explains the detected anomaly flag(s).
5. **Live Demo: Actuarial Memo Output (segment 5)**: Shows the driver decomposition, compiled report, and human review gate trigger.
6. **Security & Evaluations (segment 6)**: Walks through path traversal prevention, notes prompt injection scanners, golden tests, and eval scorecards.
7. **Business Value & Close (segment 7)**: Highlights how the agent speeds up actuarial triage while preserving auditable trace trails.

---

## 3. Security & Content Constraints

To prevent data leakage and maintain security compliance, the video and assets must adhere to these rules:

* **No Real Company Data**: Only synthetic deidentified books of business may be shown.
* **No committed secrets**: Never display `GEMINI_API_KEY`, credential strings, or passwords.
* **Do not expose `.env`**: Never read or display `.env` files.
* **No Private Paths**: Ensure terminal commands and file paths hide local usernames or Google Drive sync directories (use generic relative paths).
* **No Local Brain Files**: Do not reference or show local Agent App directories or hidden system prompts.

---

## 4. Final Video Acceptance Criteria

To pass the submission gate, the generated video must satisfy:
1. **Duration**: Exactly under 5:00 minutes.
2. **Audio Quality**: Clear, understandable pronunciation with no stuttering.
3. **Visual Quality**: Readable text sizes (minimum 1080p resolution).
4. **Metric Citations**: Narrative numbers (e.g. 85.0% loss ratio) must match the visual report metric tables exactly.
5. **Synchronization**: Subtitle captions and slide visuals must sync with the narration voiceover.
