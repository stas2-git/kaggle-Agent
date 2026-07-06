# Video Generation

This folder produces the Kaggle demo video: presentation slides, narration, subtitles, and
command-evidence cards, compiled into one synchronized `draft_demo_video.mp4`. It's organized
by **what kind of thing each file is** (slides / narrative / audio / evidence), not by its
role in the generation pipeline.

**Before touching narration or deciding whether to re-record: read
[`narrative/segment_tracker.md`](narrative/segment_tracker.md) first.** It maps every one of
the 7 segments to its script, its audio, and the specific factual claims that segment makes
about the codebase — so you (or a future LLM session) can tell at a glance which segments are
still accurate and which drifted out of date as the agent changed.

## The narration workflow: mac for basic, Gemini for final

There is exactly **one** active way to generate narration audio, with two tiers:

1. **Basic / iterating on a change** — free, local, no quota, run as many times as you want:
   ```bash
   cd project_build
   uv run python ../submission/02_video/generate_all.py --audio-source say
   ```
2. **Final polish** — costs Gemini TTS quota (~10/day), only do this when the narration text
   in `narrative/slide_narration_segments.yaml` is actually final:
   ```bash
   cd project_build
   uv run python ../submission/02_video/audio/generate_gemini_tts.py
   uv run python ../submission/02_video/generate_all.py
   ```

`audio/generate_chattts.py`, `generate_xtts.py`, and `generate_voiceover.sh` were earlier
alternatives explored before settling on this two-tier workflow — they're archived (see
`archive/` below), not part of the active path.

## Entry point

```text
generate_all.py       Primary orchestrator. Runs tests/evals, captures logs, draws slides,
                       renders evidence cards, generates/detects narration, and stitches the
                       final video. Everything below exists to feed this one script.
generate_video.py      Required sibling module (slide content + video/ffmpeg primitives).
                       Imported directly by generate_all.py - must stay next to it. Its own
                       build_video() function is a legacy standalone whole-slideshow path
                       (runnable via `python generate_video.py --dry-run`) that generate_all.py
                       does NOT call - the segment-based pipeline above superseded it.
```

**Cost warning:** by default (`--audio-source auto`) the orchestrator prefers whatever
narration segments already exist under `audio/gemini_segments/` (that's the current
deliverable's audio), falling back to free local macOS `say` only if none exist. Running the
orchestrator with no flags reuses those cached segments — no new API cost. Never run
`audio/generate_gemini_tts.py` directly unless you intend to spend quota regenerating
narration — see `audio/voice_options.md`.

## Layout

```text
02_video/
├── README.md               This file
├── generate_all.py         Entry point (see above)
├── generate_video.py       Entry point's required sibling module
├── draft_demo_video.mp4    The current deliverable
├── captions.srt            Subtitles for the deliverable
│
├── slides/                 The VISUAL layer - what's shown on screen
│   ├── slide_outline.md          Slide-by-slide content outline (planning doc)
│   └── rendered/                 Rendered slide PNGs (slide1-6.png), drawn by
│                                   generate_all.py from generate_video.SLIDES_DATA
│
├── narrative/               The SCRIPT layer - what's said, and about what.
│                              Deliberately just two files: the one canonical script and its
│                              staleness tracker. Earlier draft scripts are archived (below).
│   ├── slide_narration_segments.yaml   THE data contract: maps each of the 7 segments to
│   │                                    its slide/visual and its narration text. Read by
│   │                                    generate_all.py and audio/generate_gemini_tts.py.
│   └── segment_tracker.md              Staleness tracker - READ THIS FIRST (see above)
│
├── audio/                   The SOUND layer. Deliberately just the two active generation
│                              paths (mac say via generate_all.py, Gemini via the script
│                              below) plus their reference material - see workflow above.
│   ├── generate_gemini_tts.py     Calls Gemini API TTS. COSTS QUOTA (~10/day). This produced
│   │                               the segments behind the current draft_demo_video.mp4.
│   ├── voice_options.md           Recommended macOS voices/rates (for --audio-source say)
│   ├── available_macos_voices.txt Local voice inventory
│   ├── gemini_segments/           Narration segments actually behind draft_demo_video.mp4
│   └── narration.aiff / .mp3      Whole-track macOS `say` fallback output, if generated
│
├── evidence/                 PROOF the demo works - not slides, not script, not audio;
│                              generated by running the real tests/eval/CLI, so this is what
│                              segment_tracker.md checks for staleness
│   ├── demo_cards/                Rendered command-evidence card images
│   ├── demo_outputs/              Captured pytest/eval/CLI run logs
│   ├── video_generation_report.md Latest pipeline execution report
│   └── video_timing_diagnostics.md
│
├── docs/                     Whole-project meta/planning docs that aren't specific to one
│                              of the buckets above
│   ├── video_spec.md              Format, duration, and constraint guidelines
│   ├── video_asset_checklist.md   Visual/audio asset checklist
│   └── demo_runbook.md            Manual recording runbook
│
└── archive/                  Superseded experiments and draft scripts - not used by the
                               current deliverable, kept for reference. Regenerating or
                               reading anything here has no effect on draft_demo_video.mp4.
    ├── narration_script.md         Earlier narration draft (6 segments, superseded by
    │                                narrative/slide_narration_segments.yaml's 7)
    ├── narration_script_plain.txt  Same content as narration_script.md, plain-text form
    ├── video_script.md             A third, independently-worded narration draft
    ├── generate_voiceover.sh       Superseded by generate_all.py --audio-source say
    │                                (same job, but whole-track instead of segment-based)
    ├── generate_chattts.py         Local ChatTTS model - explored, not adopted
    ├── generate_xtts.py            Local XTTS v2 voice-cloning model - explored, not adopted
    ├── chattts_segments/           Earlier ChatTTS attempt
    ├── xtts_segments/              Earlier XTTS voice-clone attempt
    ├── natural_voice/              Personal voice recordings + ChatTTS/XTTS cloning scripts
    │                                (formerly the separate submission/03_voice_lab/ folder)
    ├── pronunciation_tests/        "Actuaries" pronunciation tuning samples
    ├── speed_tests/                Speech-rate tuning samples
    ├── concat_list.txt             Leftover scratch file from generate_video.py's unused
    │                                 build_video() path
    ├── test_chattts_output.*       One-off ChatTTS sample
    └── sample_gemini_3.1.*         One-off Gemini TTS sample
```

A per-run `.tmp/` scratch directory is created and deleted automatically by
`generate_all.py` - it holds nothing meaningful and is not part of this layout.

## How to verify no secrets are included

The pipeline scans generated files under `02_video/` for secrets before finishing. To scan
manually:

```bash
grep -rnw submission/02_video/ -e "GEMINI_API_KEY" -e "AIza" -e "password"
```
