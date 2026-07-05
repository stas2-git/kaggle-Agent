# Video Generation

This folder produces the Kaggle demo video: presentation slides, narration, subtitles, and
command-evidence cards, compiled into one synchronized `draft_demo_video.mp4`.

## Entry point

```text
generate_all.py       Primary orchestrator. Runs tests/evals, captures logs, draws slides,
                       renders evidence cards, generates/detects narration, and stitches the
                       final video. Everything below exists to feed this one script.
generate_video.py      Required sibling module (slide content + video/ffmpeg primitives).
                       Imported directly by generate_all.py - must stay next to it.
```

Run it from `project_build/`:

```bash
cd project_build
uv run python ../submission/02_video/generate_all.py
```

**Cost warning:** by default (`--audio-source auto`) the orchestrator prefers whatever
premium narration segments already exist under `assets/` (xtts > chattts > gemini), falling
back to free local macOS `say` only if none exist. **`assets/gemini_segments/` already
exists** — those are the actual segments behind the current `draft_demo_video.mp4`, made with
the Gemini TTS preview model, which has a small daily quota. Running the orchestrator with no
flags will reuse those cached segments (no new API cost). To explicitly force the free local
path instead (e.g. to test a change without touching any premium segments or quota):

```bash
uv run python ../submission/02_video/generate_all.py --audio-source say
```

Never run `scripts/generate_gemini_tts.py` directly unless you intend to spend quota
regenerating narration — see `docs/voice_options.md` and the note in `scripts/` below.

## Layout

```text
02_video/
├── README.md               This file
├── generate_all.py         Entry point (see above)
├── generate_video.py       Entry point's required sibling module
├── slide_narration_segments.yaml   Segment/slide data contract read by generate_all.py
│                                    and every script under scripts/
├── draft_demo_video.mp4    The current deliverable
├── captions.srt            Subtitles for the deliverable
│
├── scripts/                Standalone narration generators (run manually, not auto-invoked
│                            by generate_all.py - it only detects their output under assets/)
│   ├── generate_gemini_tts.py    Calls Gemini API TTS. COSTS QUOTA (~10/day). This produced
│   │                              the segments behind the current draft_demo_video.mp4.
│   ├── generate_chattts.py       Local ChatTTS model. Free, but needs `scipy` + model
│   │                              weights not installed in this environment.
│   ├── generate_xtts.py          Local XTTS v2 voice-cloning model. Free, but needs `torch`
│   │                              + model weights not installed in this environment.
│   └── generate_voiceover.sh     Free macOS `say` -> single narration.aiff/mp3 (the
│                                  non-segment-based fallback path).
│
├── docs/                   Planning and reference material (nothing here is read by code,
│                            except narration_script_plain.txt, read by generate_voiceover.sh)
│   ├── video_spec.md              Format, duration, and constraint guidelines
│   ├── narration_script.md        Timing-annotated narration with visual cues
│   ├── narration_script_plain.txt Clean narration text (input to generate_voiceover.sh)
│   ├── slide_outline.md           Slide-by-slide content outline
│   ├── video_script.md            Full shot/script draft
│   ├── video_asset_checklist.md   Visual/audio asset checklist
│   ├── video_timing_diagnostics.md
│   ├── voice_options.md           Recommended macOS voices/rates
│   ├── available_macos_voices.txt Local voice inventory
│   └── demo_runbook.md            Manual recording runbook
│
├── assets/                 Generated media actually used by the current deliverable
│   ├── slides/                    Rendered slide PNGs
│   ├── demo_cards/                Rendered command-evidence cards
│   ├── demo_outputs/               Captured pytest/eval/CLI run logs
│   ├── gemini_segments/           Narration segments behind draft_demo_video.mp4
│   ├── video_generation_report.md Latest pipeline execution report
│   └── narration.aiff / .mp3      Whole-track macOS `say` fallback output, if generated
│
└── archive/                Superseded experiments - not used by the current deliverable,
                             kept for reference. Regenerating anything here has no effect on
                             draft_demo_video.mp4.
    ├── chattts_segments/           Earlier ChatTTS attempt
    ├── xtts_segments/              Earlier XTTS voice-clone attempt
    ├── natural_voice/              Personal voice recordings + ChatTTS/XTTS cloning scripts
    │                                (formerly the separate submission/03_voice_lab/ folder;
    │                                 generate_xtts.py's --speaker lookup points here)
    ├── pronunciation_tests/        "Actuaries" pronunciation tuning samples
    ├── speed_tests/                Speech-rate tuning samples
    ├── test_chattts_output.*       One-off ChatTTS sample
    └── sample_gemini_3.1.*         One-off Gemini TTS sample
```

## How to verify no secrets are included

The pipeline scans generated files under `02_video/` for secrets before finishing. To scan
manually:

```bash
grep -rnw submission/02_video/ -e "GEMINI_API_KEY" -e "AIza" -e "password"
```
