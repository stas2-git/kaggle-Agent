# Kaggle Upload Assets

Assets prepared for the Kaggle writeup form.

## 01_card_thumbnail

- `actuarial_portfolio_monitoring_cover_560x280.png`: primary custom cover/card thumbnail image sized to Kaggle's 560 x 280 guidance.
- `actuarial_portfolio_monitoring_cover_custom.svg`: editable source for the custom cover.
- `actuarial_portfolio_monitoring_cover_custom_560x280.png`: rendered copy of the custom cover.
- `actuarial_portfolio_monitoring_cover_square_v2.svg`: editable source for the square thumbnail variant.
- `actuarial_portfolio_monitoring_cover_square_v2_280x280.png`: square-native thumbnail variant for 280 x 280 box previews.
- `actuarial_portfolio_monitoring_cover_square_safe_v3.svg`: editable source for the wide cover designed around a center 280 x 280 crop.
- `actuarial_portfolio_monitoring_cover_square_safe_v3_560x280.png`: recommended wide cover that still works when center-cropped to a square.
- `actuarial_portfolio_monitoring_cover_square_safe_v3_center_crop_preview_280x280.png`: preview of the exact centered 280 x 280 crop from the recommended wide cover.
- `actuarial_portfolio_monitoring_master_crop_v4.svg`: editable source for a single upload image with two crop zones.
- `actuarial_portfolio_monitoring_master_crop_v4_560x560.png`: recommended single upload image. Use the top half for the 560 x 280 card crop and the lower-center square for the 280 x 280 thumbnail crop.
- `actuarial_portfolio_monitoring_master_crop_v4_card_preview_560x280.png`: local preview of the card crop from the master.
- `actuarial_portfolio_monitoring_master_crop_v4_thumbnail_preview_280x280.png`: local preview of the thumbnail crop from the master.

## 02_media_gallery

The 8 slides actually used in the final video (`submission/02_video/final_demo_video.mp4`), copied from `submission/02_video/slides/rendered/` so the gallery matches the video 1:1.

- `01_title.png`: title card.
- `02_problem.png`: problem framing — manual monthly review is a scramble, not a monitoring workflow.
- `03_why_an_agent.png`: why an agent beats a dashboard (validate, choose tool, escalate review).
- `04_architecture.png`: five-layer bounded architecture (data, security, tools, Gemini synthesis, output).
- `05_live_demo_run.png`: live demo evidence — CSV in, agent run, high-severity human-review gate.
- `06_driver_decomposition.png`: driver decomposition evidence — two anomaly signals converge on one slice.
- `07_verification_scorecard.png`: verification evidence — deterministic checks, scenario evals, secret-leak scan.
- `08_closing_roadmap.png`: closing claim and roadmap.
