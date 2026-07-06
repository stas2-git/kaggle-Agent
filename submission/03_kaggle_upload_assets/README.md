# Kaggle Upload Assets

Assets prepared for the Kaggle writeup form.

## 01_card_thumbnail

- `actuarial_portfolio_monitoring_master_crop_v4.svg`: editable source for a single upload image with two crop zones.
- `actuarial_portfolio_monitoring_master_crop_v4_560x560.png`: recommended single upload image. Use the top half for the 560 x 280 card crop and the lower-center square for the 280 x 280 thumbnail crop.
- `actuarial_portfolio_monitoring_master_crop_v4_card_preview_560x280.png`: local preview of the card crop from the master.
- `actuarial_portfolio_monitoring_master_crop_v4_thumbnail_preview_280x280.png`: local preview of the thumbnail crop from the master.

## 02_media_gallery

Slides 01-08 are the deck actually used in the final video (`submission/02_video/final_demo_video.mp4`), copied from `submission/02_video/slides/rendered/` so the gallery matches the video 1:1. Slides 09-12 are raw captured tool output (not designed cards), backing the verification claim with literal command output rather than a styled summary — 09-10 come from `submission/02_video/backend/evidence/demo_cards/`; 11-12 were rendered from the same real captured logs using the project's own card renderer (`generate_video.draw_log_card` / `draw_stat_card`).

- `01_title.png`: title card.
- `02_problem.png`: problem framing — manual monthly review is a scramble, not a monitoring workflow.
- `03_why_an_agent.png`: why an agent beats a dashboard (validate, choose tool, escalate review).
- `04_architecture.png`: five-layer bounded architecture (data, security, tools, Gemini synthesis, output).
- `05_live_demo_run.png`: live demo evidence — CSV in, agent run, high-severity human-review gate.
- `06_driver_decomposition.png`: driver decomposition evidence — two anomaly signals converge on one slice.
- `07_verification_scorecard.png`: verification evidence — deterministic checks, scenario evals, secret-leak scan.
- `08_closing_roadmap.png`: closing claim and roadmap.
- `09_raw_pytest_output.png`: real captured `uv run pytest` terminal output (60 passed, exit code 0).
- `10_raw_trace_output.png`: real captured JSON trace excerpt from an actual run (run_id, timestamps, severity, review flags).
- `11_raw_demo_run_output.png`: real captured CLI output from an online run against `tests/golden/loss_ratio_spike.csv` (real severity, real human-review flag, real report/trace paths).
- `12_raw_eval_scorecard.png`: real captured offline eval run output (11/11 cases passed, exit code 0).
