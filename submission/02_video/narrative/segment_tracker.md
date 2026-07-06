# Segment Tracker

Read this before deciding whether `draft_demo_video.mp4` needs to be regenerated. It maps
every segment of the video to its script, its audio, and — critically — the specific factual
claims that segment makes about the codebase, so a human or an LLM working on the project
later can tell at a glance which segments drift out of date as the agent changes.

**Last full content audit: 2026-07-05.** Re-run the audit (see "How to re-verify" below)
after any change to anomaly detection, test count, tool/metric behavior, or architecture.

## Quick status

| # | Title | Status | Why |
|---|---|---|---|
| 1 | Title Card | 🟢 CURRENT | Generic problem statement, no implementation-specific claims. |
| 2 | Why an Agent | 🟢 CURRENT | Describes the tool-first/deterministic-vs-LLM design principle, still true. |
| 3 | Five-Layer Architecture | 🟢 CURRENT | Describes data/security/tools/agent/output layers, still accurate. |
| 4 | Live Demo: Pipeline Execution | 🟡 INCOMPLETE | True as far as it goes, but only describes the loss-ratio anomaly. The same demo run now also fires a claim-count anomaly (see [spec_change_log.md](../../../project_build/artifacts/spec_change_log.md)) that the narration doesn't mention. |
| 5 | Live Demo: Actuarial Memo Output | 🟡 INCOMPLETE | Same cause as #4 — describes the loss-ratio driver breakdown correctly, but not the second anomaly's. |
| 6 | Rigorous Safety & Verification | 🔴 STALE | Says "all twenty-five tests pass." Current count is **59**. |
| 7 | Conclusion & Future Roadmap | 🟢 CURRENT | Generic closing + future-work list, no numbers that can go stale. |

**Bottom line right now:** segment 6's audio needs to be re-recorded (wrong test count).
Segments 4/5 are not *wrong*, just incomplete — re-recording is optional polish, not a
correctness fix. This same incompleteness also exists in
`submission/01_writeup/kaggle_writeup_draft.md` section 8 ("Demo Description") — fix both
together if you fix either.

## Per-segment detail

### Segment 1 — Title Card
- **Script source:** `slide_narration_segments.yaml`, `slide_number: 1`
- **Visual:** `slides/rendered/slide1.png`
- **Audio:** `audio/gemini_segments/seg_1.mp3` / `.wav` — generated 2026-06-22, Gemini `gemini-3.1-flash-tts-preview`, voice `Kore`
- **Narration text:** "Routine monthly monitoring of insurance books of business is a critical but repetitive risk-management process. Actuaries and analysts must manually load transactional aggregates, compute key metrics, detect anomalies, decompose them by concentration drivers, and compile explanatory reports. Traditional business intelligence dashboards visualize these trends, but they stop at charts. They do not write the explanation or perform the initial triage, creating a time-consuming bottleneck for risk teams."
- **Claims that could go stale:** none — pure problem framing.

### Segment 2 — Why an Agent
- **Script source:** `slide_narration_segments.yaml`, `slide_number: 2`
- **Visual:** `slides/rendered/slide2.png`
- **Audio:** `audio/gemini_segments/seg_2.mp3` / `.wav` — 2026-06-22, same model/voice as above
- **Narration text:** "This workflow is highly suited to an agentic approach because it is multi-step, reasoning-driven, and requires strict security checks. A simple static script cannot dynamically decide how to triage issues. Our agent validates input schema quality, runs safety scans, identifies anomalies, selects the correct driver slicing tools, and compiles findings. To guarantee absolute mathematical correctness, we use a tool-first architecture where deterministic Python tools compute all metrics, and the LLM is restricted only to narrative synthesis."
- **Claims that could go stale:** "tool-first architecture... LLM restricted to narrative synthesis" — this is the core design invariant enforced by `portfolio_agent/adk/callbacks.py`. Re-check this segment only if that invariant is ever relaxed.

### Segment 3 — Five-Layer Architecture
- **Script source:** `slide_narration_segments.yaml`, `slide_number: 3`
- **Visual:** `slides/rendered/slide3.png`
- **Audio:** `audio/gemini_segments/seg_3.mp3` / `.wav` — 2026-06-22
- **Narration text:** "The agent's architecture consists of five modular layers. First, a data layer that ingests synthetic CSV aggregations. Second, a security layer that checks paths and text notes for prompt injections. Third, a deterministic tool layer that calculates premiums, loss ratios, and written-premium-weighted averages for rate changes, retention, and benchmark adequacy. Fourth, an agent reasoning layer that manages Gemini calls and structured schemas. And fifth, an output layer writing a markdown review memo and a complete JSON trace file."
- **Claims that could go stale:** the "five layers" description maps directly onto `portfolio_agent/core/` (data+tools), `core/security.py`, `adk/` (agent reasoning), and `core/reporting.py` + `observability/tracing.py` (output) after the pyramid reorg — still accurate. Re-check if the module structure changes again.

### Segment 4 — Live Demo: Pipeline Execution 🟡
- **Script source:** `slide_narration_segments.yaml`, `slide_number: 4`
- **Visual:** `evidence/demo_cards/run_card.png`
- **Audio:** `audio/gemini_segments/seg_4.mp3` / `.wav` — 2026-06-22
- **Narration text:** "Let's look at the pipeline in action. We run the orchestrator tool on a synthetic dataset containing an aggregate loss ratio spike in the Public D&O segment. The tool validates the columns, calculates metrics, and triggers a high-severity flag because the loss ratio rose from fifty percent to eighty-five percent. The agent immediately calls the driver investigation tool to slice the segment by available dimensions."
- **Current truth (verified 2026-07-05):** the `loss_ratio_spike.csv` demo run still shows exactly this (50.0% → 85.0%, high severity) — **true, not wrong**. But the same run *also* now fires a `claim_count` anomaly (claim count 1→3, +200%, also high severity) that this segment doesn't mention. See `project_build/tests/golden/expected_loss_ratio_spike.yaml` and `evidence/demo_outputs/run_output.txt`.
- **To fix:** either leave as-is (it's not false, just a partial description) or add one sentence acknowledging the second anomaly, then re-record with `audio/generate_gemini_tts.py` (costs Gemini TTS quota — see `02_video/README.md`).

### Segment 5 — Live Demo: Actuarial Memo Output 🟡
- **Script source:** `slide_narration_segments.yaml`, `slide_number: 5`
- **Visual:** `evidence/demo_cards/report_card.png`
- **Audio:** `audio/gemini_segments/seg_5.mp3` / `.wav` — 2026-06-22
- **Narration text:** "The mathematical breakdown shows that this spike is entirely concentrated in state New York for the two thousand twenty-five policy year. In the compiled report, we see the executive summary, metrics tables, NY drivers, actuary-facing recommended follow-up questions, and the human review gate flag set to required due to severity. A full trace JSON is saved for auditability."
- **Current truth (verified 2026-07-05):** still true for the loss-ratio anomaly's driver breakdown specifically. Same incompleteness as segment 4 — doesn't mention the claim-count anomaly's own driver breakdown.
- **To fix:** same as segment 4 — bundle any re-recording together since both describe the same demo run.

### Segment 6 — Rigorous Safety & Verification 🔴
- **Script source:** `slide_narration_segments.yaml`, `slide_number: 6`
- **Visual:** `evidence/demo_cards/eval_card.png`
- **Audio:** `audio/gemini_segments/seg_6.mp3` / `.wav` — 2026-06-22
- **Narration text:** "Security and privacy are vital. The security layer blocks path traversals and screens note fields for prompt-injection attacks. In our test suite, we run deterministic tests to match metric and driver math against YAML expectations. We also run evaluation cases validating CSV checks, prompt injections, secret disclosure requests, and report quality criteria. Our pytest suite verifies all twenty-five tests pass successfully."
- **Current truth (verified 2026-07-05):** `uv run pytest -q` now reports **59 passed**, not 25. This grew across the ADK upgrade (Phase 1-9), the spec-reconciliation pass (+6 tests for the newly implemented claim_count/rate_change/retention anomalies), and is otherwise unrelated to this segment's other claims (security layer, evaluation cases), which remain accurate.
- **To fix:** update the narration text in `slide_narration_segments.yaml` (change "twenty-five" to "fifty-nine," or drop the exact number and say "our full pytest suite passes" to avoid re-recording every time the count changes), then re-run `audio/generate_gemini_tts.py --force` for segment 6 only if the script supports per-segment regeneration, or accept the small quota cost of a full re-run.

### Segment 7 — Conclusion & Future Roadmap
- **Script source:** `slide_narration_segments.yaml`, `slide_number: 7`
- **Visual:** `slides/rendered/slide6.png` (verified: `generate_video.SLIDES_DATA` has exactly 6 entries — "Real Business Impact & Future Roadmap" is the 6th. Segments 1-3 use `slide1-3.png`; segments 4-6 use `demo_cards/*` instead of `slide4.png`/`slide5.png`; segment 7 reuses `slide6.png` as its closing visual. `slide4.png` and `slide5.png` are still drawn by `generate_all.py`'s slide loop but are not referenced by any segment — harmless orphaned byproducts, not a bug.)
- **Audio:** `audio/gemini_segments/seg_7.mp3` / `.wav` — 2026-06-22
- **Narration text:** "The Actuarial Portfolio Monitoring Agent is not a replacement for professional actuarial opinion or underwriting authority. Instead, it serves as a robust triage assistant that makes routine reviews faster, safer, and thoroughly documented. For future work, we plan to transition from flat CSVs to running direct BigQuery analytical queries, GKE-run containerized scheduling, and email alerts. Thank you."
- **Claims that could go stale:** none — matches `submission/01_writeup/kaggle_writeup_draft.md` section 9 "Future Work" (BigQuery Tooling), which is a forward-looking statement, not a current-state claim.

## How to re-verify (for a human or a future LLM session)

Run these and compare against the "Current truth" lines above:

```bash
cd project_build
uv run pytest -q                                                          # segment 6: test count
uv run python3 -m portfolio_agent.run \
  --input tests/golden/loss_ratio_spike.csv --latest-month 2026-06 \
  --force-offline                                                          # segments 4/5: anomaly count/severity
```

If any number changes, update `submission/02_video/narrative/slide_narration_segments.yaml`
first (it's the single source of truth all narration is generated from — see
`02_video/README.md`), mark the segment 🔴 or 🟡 above, then re-record with the two-tier
workflow: test the wording cheaply first with `generate_all.py --audio-source say` (free,
local, unlimited), and only run `audio/generate_gemini_tts.py` once the text is actually
final, since that one costs quota (~10/day).
