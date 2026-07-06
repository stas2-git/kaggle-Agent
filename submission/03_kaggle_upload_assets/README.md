# Kaggle Upload Assets

Assets prepared for the Kaggle writeup form.

## 01_card_thumbnail

- `actuarial_portfolio_monitoring_master_crop_v4.svg`: editable source for a single upload image with two crop zones.
- `actuarial_portfolio_monitoring_master_crop_v4_560x560.png`: recommended single upload image. Use the top half for the 560 x 280 card crop and the lower-center square for the 280 x 280 thumbnail crop.
- `actuarial_portfolio_monitoring_master_crop_v4_card_preview_560x280.png`: local preview of the card crop from the master.
- `actuarial_portfolio_monitoring_master_crop_v4_thumbnail_preview_280x280.png`: local preview of the thumbnail crop from the master.

## 02_media_gallery

Slides 01-08 are the deck actually used in the final video (`submission/02_video/final_demo_video.mp4`), copied from `submission/02_video/slides/rendered/` so the gallery matches the video 1:1. Slides 09-11 are raw captured output (not designed cards) from the same real online run (Run ID 213 against `tests/golden/loss_ratio_spike.csv`), read top to bottom as CLI output -> the actual LLM-authored memo it produced -> the structured trace of that run.

- `01_title.png`: title card.
- `02_problem.png`: problem framing — manual monthly review is a scramble, not a monitoring workflow.
- `03_why_an_agent.png`: why an agent beats a dashboard (validate, choose tool, escalate review).
- `04_architecture.png`: five-layer bounded architecture (data, security, tools, Gemini synthesis, output).
- `05_live_demo_run.png`: live demo evidence — CSV in, agent run, high-severity human-review gate.
- `06_driver_decomposition.png`: driver decomposition evidence — two anomaly signals converge on one slice.
- `07_verification_scorecard.png`: verification evidence — deterministic checks, scenario evals, secret-leak scan.
- `08_closing_roadmap.png`: closing claim and roadmap.
- `09_raw_demo_run_output.png`: real captured CLI output from an online run against `tests/golden/loss_ratio_spike.csv` (real severity, real human-review flag, real report/trace paths).
- `10_raw_llm_generated_report.png`: excerpt of the actual Gemini-authored review memo from that same run (Run ID 213) — executive summary, interpretation, and hypothesis, grounded in the deterministic numbers above it.
- `11_raw_trace_output.png`: real captured JSON trace excerpt from that same run (run_id, timestamps, severity, review flags).
