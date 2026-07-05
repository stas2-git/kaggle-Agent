# Video Specification: Actuarial Portfolio Monitoring Agent

This document defines the specification and quality gates for the automated capstone demo video.

---

## 1. Core Metadata

* **Project Title**: Actuarial Portfolio Monitoring Agent
* **Sub-track**: Agents for Business
* **Target Video Length**: Under 5 minutes (ideal: 4:30 - 4:50)
* **Visual Format**: Slides/title cards and screen-recording evidence (no camera required)
* **Audio Format**: Text-to-speech voiceover narration (no human voice required)
* **Default TTS engine**: macOS native `say` command (Voice: `Samantha` or `Daniel`)

---

## 2. Required Sections

The video script and slides must cover the following sections in order:

1. **Problem (0:00 - 0:30)**: Explains the manual overhead of routine monthly portfolio monitoring and the limitations of static dashboards.
2. **Solution (0:30 - 1:00)**: Explains how the agent automates validation, metrics calculation, anomaly detection, and review synthesis.
3. **Architecture (1:00 - 1:45)**: Visualizes the 5 bounded layers of the system (Data, Security, Tools, Agent, Output).
4. **Live Demo (1:45 - 3:45)**: Demonstrates running the pipeline, explaining the loss ratio spike flag, driver slicing, and the human gate trigger.
5. **Security & Evaluations (3:45 - 4:30)**: Walks through path traversal prevention, notes prompt injection scanners, golden tests, and eval scorecards.
6. **Business Value & Close (4:30 - 5:00)**: Highlights how the agent speeds up actuarial triage while preserving auditable trace trails.

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
