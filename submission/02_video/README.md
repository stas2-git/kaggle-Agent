# Video Generation

This folder produces the Kaggle demo video: presentation slides, narration, subtitles, and
command-evidence cards, compiled into one synchronized `draft_demo_video.mp4`.

**Two top-level folders are the spec you review and sign off on: `story/` (the stable
slide-by-slide meaning, visual copy, audio-safe narration, current audio, and prior audio
versions) and `slides/` (what's shown). `backend/` is the machinery that produces and combines
everything - you only need to open it if something's broken.** The
pipeline is split into three stages that match that review workflow:

1. **`backend/build_slides.py`** - runs the real pytest suite, offline evaluations, and a
   live (real Gemini API) agent run, then renders all 7 segments' visuals into
   `slides/rendered/slide_1.png` ... `slide_7.png`. Slow (hits the real API); run it when the
   visual story or the agent code changes.
2. **Audio generation** (`backend/audio_generation/`) - regenerates `story/audio/current/`
   (the current narration spec). Two engines, see below.
3. **`backend/assemble_video.py`** - reads whatever's *currently* in `slides/rendered/` and
   `story/audio/current/`, and just combines them into `captions.srt` +
   `draft_demo_video.mp4`. Fast,
   deterministic, no test suite, no API calls, no slide drawing - it only assembles specs you
   have already reviewed.

`backend/generate_all.py` is a thin convenience wrapper that runs stage 1 then stage 3 in one
shot, for quick full-regeneration (e.g. previewing wording changes with free `say` audio). It
skips the review pause by design - prefer the staged commands below when you actually want to
look at each spec before it's baked into the video.

**Before touching narration or deciding whether to re-record: read
[`HANDOFF.md`](HANDOFF.md), then [`segment_tracker.md`](segment_tracker.md).** The handoff
states the current audio/video status; the tracker maps every one of
the 7 segments to its stable story, its audio, and the volatile facts shown visually — so you
(or a future LLM session) can tell at a glance which changes require slide regeneration versus
actual TTS re-recording.

**Current status:** `story/slide_story.yaml` is the canonical story contract. Segments 4-6 use
audio-safe wording that avoids brittle counts and exact demo metrics; those volatile facts are
kept on the rendered slides instead. The latest `draft_demo_video.mp4` is an all-Gemini
draft: Gemini audio is now present for all seven segments. See the tracker for the current
segment status.

## The narration workflow: mac for basic, Gemini for final

There is exactly **one** active way to generate narration audio, with two tiers:

1. **Basic / iterating on a change** — free, local, no quota, run as many times as you want.
   Writes to `story/audio/previews/say/`, never touches the canonical
   `story/audio/current/seg_N.mp3`:
   ```bash
   cd project_build
   uv run python ../submission/02_video/backend/audio_generation/generate_say_preview.py               # all 7
   uv run python ../submission/02_video/backend/audio_generation/generate_say_preview.py --segments 5,6    # example: just these
   uv run python ../submission/02_video/backend/assemble_video.py --segments 5,6                        # preview it in the video:
                                                                                                          # changed segments use fresh
                                                                                                          # preview audio,
                                                                                                          # the rest reuse the
                                                                                                          # canonical Gemini audio
   ```
2. **Final polish** — costs Gemini TTS quota (~10/day), only do this when the narration text
   in `story/slide_story.yaml` is actually final and you've previewed it with
   `say` above. Pass `--segments` to regenerate only the ones that changed — everything else is
   reused from the cached `.mp3`/`.wav` untouched, so you don't spend quota re-recording
   segments that are already correct. The old audio for any segment you do regenerate is never
   deleted — it's copied into a dated folder under `story/audio/versions/` first:
   ```bash
   cd project_build
   uv run python ../submission/02_video/backend/audio_generation/generate_gemini_tts.py --segments 5,6
   uv run python ../submission/02_video/backend/assemble_video.py
   ```
   Omit `--segments` (or pass bare `--force`) only if you actually need to re-record every
   segment — every segment's prior version is still archived first either way.

`archive/generate_chattts.py`, `generate_xtts.py`, and `generate_voiceover.sh` were earlier
alternatives explored before settling on this two-tier workflow — archived, not active.

**Cost warning:** `assemble_video.py`'s default (`--audio-source auto`) prefers whatever
narration segments already exist as `story/audio/current/seg_*.mp3`, falling back to free
local macOS `say` only if none exist. Running it with no flags reuses cached segments — no
new API cost. Running it with `--segments` creates a mixed preview video where those segments
use fresh `say` audio from `story/audio/previews/say/`.

## The visual workflow: one command, all 7 slides

`slides/rendered/` holds all 7 segment visuals, uniformly named `slide_1.png` ...
`slide_7.png` - review them all together here, regardless of how each one was produced:

```bash
cd project_build
uv run python ../submission/02_video/backend/build_slides.py
```

- **Segments 1, 2, 3, 7** are hand-authored story slides, drawn from
  `story/slide_story.yaml`. Edit that file to change their titles, hooks, cards, takeaways,
  or audio-safe narration.
- **Segments 4, 5, 6** are evidence cards rendered from the *real* output of this run's
  pytest suite, offline evaluations, generated report, and live agent invocation - not
  hand-authored, and not reproducible without actually running the code. Segment 4 shows the
  pipeline result, segment 5 summarizes the generated actuarial memo and driver
  concentration, and segment 6 combines pytest plus offline-eval verification. This is also
  why `build_slides.py` is the slow stage: it hits the real Gemini API once (with retries for
  transient upstream 503s) to produce genuine agent output for segment 4/5's demo cards.

Two extra evidence images are generated but not part of the 7-slide deck (no segment narrates
them): `backend/evidence/demo_cards/pytest_card.png` and `trace_card.png` - bonus proof for
anyone auditing the submission, not something to sign off on.

## Frontend — what you'd actually write or listen to

```text
02_video/
├── README.md               This file
├── HANDOFF.md              Current-state note for the next LLM/context window.
├── segment_tracker.md      Staleness tracker - READ THIS FIRST (see above). A status
│                            dashboard about the whole video, not narration content itself,
│                            so it lives at the root next to README.md, not inside story/.
├── draft_demo_video.mp4    The current deliverable
├── captions.srt            Subtitles, auto-generated by backend/assemble_video.py - never
│                            hand-edit this, it will be overwritten on the next run
│
├── story/                   THE STORY + AUDIO PACKAGE. Edit/listen here first.
│   ├── README.md             Explains the package layout and audio versioning rules.
│   ├── slide_story.yaml      Source of truth: stable slide story, visual copy, and
│   │                          audio-safe narration.
│   ├── narration_segments.yaml
│   │                          Compatibility snapshot for older tooling/humans. Active
│   │                          scripts read `slide_story.yaml` directly.
│   └── audio/
│       ├── current/          Current canonical audio used by assemble_video.py without
│       │                      --segments.
│       │   ├── seg_1.mp3 ... seg_7.mp3
│       │   └── details/
│       │       ├── gemini_segments/       Raw Gemini .wav intermediates + metadata.json.
│       │       ├── narration.mp3          Whole-track concat regenerated by assembly.
│       │       ├── voice_options.md
│       │       └── available_macos_voices.txt
│       ├── previews/
│       │   └── say/          Disposable local preview takes from generate_say_preview.py.
│       └── versions/         Prior audio snapshots, including the preserved pre-story
│                              contract Gemini set. Nothing here is auto-deleted.
│
├── slides/                  THE VISUALS - what's shown on screen. All 7 segments, always,
│   │                          regardless of whether a slide is hand-authored or built from
│   │                          real pipeline evidence - see "The visual workflow" above.
│   ├── slide_outline.md          Slide-by-slide content outline (planning doc, edit this)
│   ├── graphics/                  Source icons/images to composite into slides (empty until
│   │                               you add some - see backend/generate_video.py's draw_slide)
│   └── rendered/                  slide_1.png ... slide_7.png, regenerated by
│                                    backend/build_slides.py
│
```

The important audio version rule: `story/audio/current/` is the version the assembler uses;
`story/audio/versions/` is history. The folder
`story/audio/versions/20260706-pre-story-contract-gemini/` preserves the prior Gemini take
so it cannot be lost when segments are regenerated.

## `backend/` — the machinery

```text
backend/
├── common.py               Shared path constants (VIDEO_DIR, AUDIO_DIR, SLIDES_DIR, ...) and
│                            small helpers (run_command, redact_workspace_paths, ffprobe
│                            duration helpers) - imported by every stage script below so a
│                            path or the PII-redaction logic can't drift between them.
├── story_contract.py       Loads story/slide_story.yaml and exposes the stable story fields
│                            to slide rendering, captions, and TTS generation.
├── generate_video.py       Pure rendering primitives: hand-authored slide data from
│                            story/slide_story.yaml, draw_slide, draw_log_card,
│                            draw_stat_card, font loaders. No orchestration.
├── build_slides.py         STAGE 1 - see "The visual workflow" above.
│
├── audio_generation/
│   ├── generate_gemini_tts.py    STAGE 2 (final). Calls Gemini API TTS. COSTS QUOTA
│   │                               (~10/day). Writes current mp3s to
│   │                               ../story/audio/current/ and wav/metadata details to
│   │                               ../story/audio/current/details/gemini_segments/.
│   │                               Archives overwritten segments to
│   │                               ../story/audio/versions/<timestamp>-gemini-regeneration/.
│   └── generate_say_preview.py   STAGE 2 (iteration). Free local macOS 'say' audio into
│                                   ../story/audio/previews/say/. Never touches the canonical
│                                   ../story/audio/current/seg_N.mp3.
│
├── assemble_video.py       STAGE 3 - see intro above. Reads slides/rendered/ +
│                            story/audio/current/ (+ story/audio/previews/say/ when
│                            --segments is passed) and
│                            story/slide_story.yaml; writes captions.srt +
│                            draft_demo_video.mp4; runs the secret/PII scan; writes
│                            evidence/video_generation_report.md.
│
├── generate_all.py         Thin wrapper: build_slides.main() then assemble_video.main(),
│                            for one-shot full regeneration. See intro above for when to
│                            prefer the staged commands instead.
│
├── evidence/                PROOF the demo works - generated by running the real
│                              tests/eval/CLI, not something you write by hand
│   ├── demo_cards/                pytest_card.png, trace_card.png - bonus evidence not
│   │                                referenced by any segment (the 3 that are - run/report/
│   │                                eval cards - live in slides/rendered/slide_4,5,6.png
│   │                                instead, since those ARE part of the 7-slide deck)
│   ├── demo_outputs/              Captured pytest/eval/CLI run logs (PII-redacted)
│   ├── verification_results.json  Pass/fail + headline stats from the last build_slides.py
│   │                                run - assemble_video.py reads this instead of
│   │                                re-running verification
│   └── video_generation_report.md Latest assemble_video.py execution report
│
├── docs/                     Whole-project meta/planning docs
│   ├── video_spec.md              Format, duration, and constraint guidelines
│   ├── video_asset_checklist.md   Visual/audio asset checklist
│   └── demo_runbook.md            Manual recording runbook
│
└── .tmp/                    Per-run scratch directories (temp_segments/,
                              say_preview_scratch/), created and deleted automatically by
                              whichever stage owns them - hold nothing meaningful, not part
                              of this layout
```

## `archive/` — superseded, kept for reference

Not frontend or backend — has zero effect on the current deliverable. Two abandoned local
TTS engines (ChatTTS, XTTS) and their generated segments, the personal voice-cloning
recordings (`natural_voice/`, formerly the separate `submission/03_voice_lab/`), three
earlier narration drafts that got replaced by the yaml, one dead shell script, orphaned
whole-track audio byproducts, a superseded timing-bug diagnosis, and assorted one-off
tuning samples. See inline comments in the folder itself if you need archaeology.

## How to verify no secrets are included

The pipeline scans generated files under `02_video/` for secrets and un-redacted local
workspace paths (which embed your email via the Google Drive sync folder name) before
finishing. To scan manually:

```bash
grep -rnw submission/02_video/ -e "GEMINI_API_KEY" -e "AIza" -e "password"
```
