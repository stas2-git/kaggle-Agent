# Video Generation

This folder produces the Kaggle demo video: presentation slides, narration, subtitles, and
command-evidence cards, compiled into one synchronized `draft_demo_video.mp4`.

**Three top-level folders are the spec you review and sign off on: `narrative/` (what's
said), `slides/` (what's shown), `audio/` (what's heard). `backend/` is the machinery that
produces and combines them - you only need to open it if something's broken.** The pipeline
is split into three stages that match that review workflow:

1. **`backend/build_slides.py`** - runs the real pytest suite, offline evaluations, and a
   live (real Gemini API) agent run, then renders all 7 segments' visuals into
   `slides/rendered/slide_1.png` ... `slide_7.png`. Slow (hits the real API); run it when the
   narration text or the agent code changes.
2. **Audio generation** (`backend/audio_generation/`) - regenerates `audio/` (the narration
   spec). Two engines, see below.
3. **`backend/assemble_video.py`** - reads whatever's *currently* in `slides/rendered/` and
   `audio/`, and just combines them into `captions.srt` + `draft_demo_video.mp4`. Fast,
   deterministic, no test suite, no API calls, no slide drawing - it only assembles specs you
   have already reviewed.

`backend/generate_all.py` is a thin convenience wrapper that runs stage 1 then stage 3 in one
shot, for quick full-regeneration (e.g. previewing wording changes with free `say` audio). It
skips the review pause by design - prefer the staged commands below when you actually want to
look at each spec before it's baked into the video.

**Before touching narration or deciding whether to re-record: read
[`segment_tracker.md`](segment_tracker.md) first.** It maps every one of
the 7 segments to its script, its audio, and the specific factual claims that segment makes
about the codebase — so you (or a future LLM session) can tell at a glance which segments are
still accurate and which drifted out of date as the agent changed.

**Current status (per the tracker, last audit 2026-07-05):** the script is correct for all
7 segments, but the canonical audio for segments 4-6 (`audio/seg_4.mp3` etc.) is stale (old
anomaly wording, old test count). `draft_demo_video.mp4` still has the old audio there.
Re-recording those three costs Gemini TTS quota, so it hasn't been done automatically — see
the tracker's "Bottom line" for the exact command.

## The narration workflow: mac for basic, Gemini for final

There is exactly **one** active way to generate narration audio, with two tiers:

1. **Basic / iterating on a change** — free, local, no quota, run as many times as you want.
   Writes to `audio/say_preview/`, never touches the canonical `audio/seg_N.mp3`:
   ```bash
   cd project_build
   uv run python ../submission/02_video/backend/audio_generation/generate_say_preview.py               # all 7
   uv run python ../submission/02_video/backend/audio_generation/generate_say_preview.py --segments 4,5,6  # just these
   uv run python ../submission/02_video/backend/assemble_video.py --segments 4,5,6                      # preview it in the video:
                                                                                                          # 4-6 use the fresh
                                                                                                          # say_preview audio,
                                                                                                          # 1,2,3,7 reuse the
                                                                                                          # canonical Gemini audio
   ```
2. **Final polish** — costs Gemini TTS quota (~10/day), only do this when the narration text
   in `narrative/slide_narration_segments.yaml` is actually final and you've previewed it with
   `say` above. Pass `--segments` to regenerate only the ones that changed — everything else is
   reused from the cached `.mp3`/`.wav` untouched, so you don't spend quota re-recording
   segments that are already correct. The old audio for any segment you do regenerate is never
   deleted — it's copied into `audio/details/previous_versions/` first:
   ```bash
   cd project_build
   uv run python ../submission/02_video/backend/audio_generation/generate_gemini_tts.py --segments 4,5,6
   uv run python ../submission/02_video/backend/assemble_video.py
   ```
   Omit `--segments` (or pass bare `--force`) only if you actually need to re-record every
   segment — every segment's prior version is still archived first either way.

`archive/generate_chattts.py`, `generate_xtts.py`, and `generate_voiceover.sh` were earlier
alternatives explored before settling on this two-tier workflow — archived, not active.

**Cost warning:** `assemble_video.py`'s default (`--audio-source auto`) prefers whatever
narration segments already exist as `audio/seg_*.mp3` (that's the current deliverable's
audio), falling back to free local macOS `say` only if none exist. Running it with no flags
reuses those cached segments — no new API cost.

## The visual workflow: one command, all 7 slides

`slides/rendered/` holds all 7 segment visuals, uniformly named `slide_1.png` ...
`slide_7.png` - review them all together here, regardless of how each one was produced:

```bash
cd project_build
uv run python ../submission/02_video/backend/build_slides.py
```

- **Segments 1, 2, 3, 7** are hand-authored bullet slides, drawn from
  `generate_video.SLIDES_DATA`. Edit that file to change their content/wording (the bullets
  are deliberately short keyword phrases, not full sentences - they play under narration
  audio, and a viewer can't read a full sentence and listen at the same time).
- **Segments 4, 5, 6** ("Live Demo") are evidence cards rendered from the *real* output of
  this run's pytest suite, offline evaluations, and live agent invocation - not hand-authored,
  and not reproducible without actually running the code. This is also why `build_slides.py`
  is the slow stage: it hits the real Gemini API once (with retries for transient upstream
  503s) to produce genuine agent output for segment 4/5's "Live Demo" cards.

Two extra evidence images are generated but not part of the 7-slide deck (no segment narrates
them): `backend/evidence/demo_cards/pytest_card.png` and `trace_card.png` - bonus proof for
anyone auditing the submission, not something to sign off on.

## Frontend — what you'd actually write or listen to

```text
02_video/
├── README.md               This file
├── segment_tracker.md      Staleness tracker - READ THIS FIRST (see above). A status
│                            dashboard about the whole video, not narration content itself,
│                            so it lives at the root next to README.md, not inside narrative/.
├── draft_demo_video.mp4    The current deliverable
├── captions.srt            Subtitles, auto-generated by backend/assemble_video.py - never
│                            hand-edit this, it will be overwritten on the next run
│
├── narrative/               THE SCRIPT - what's said, and about what. Just one file.
│   └── slide_narration_segments.yaml   The data contract: maps each of the 7 segments to
│                                        its slide/visual and its narration text. This is
│                                        what you edit to change what the video says.
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
└── audio/                   THE SOUND - just the 7 narration files, nothing else. The
                              generator code lives in backend/audio_generation/; reference
                              docs and the raw .wav/metadata.json live in audio/details/
                              if you're curious, but you don't need them to listen.
    ├── seg_1.mp3 ... seg_7.mp3    The canonical narration behind draft_demo_video.mp4
    │                                whenever you run assemble_video.py without --segments.
    │                                Never touched by a --segments say-preview run - see
    │                                say_preview/ below for what's actually driving the
    │                                video in that case.
    ├── say_preview/                 Only exists after a generate_say_preview.py run. Holds
    │                                 the exact fresh 'say' mp3s for whichever segments you
    │                                 just previewed (overwritten each such run) - so what
    │                                 draft_demo_video.mp4 plays for those segments is always
    │                                 something you can open and listen to directly, not just
    │                                 implied by console logs.
    └── details/
        ├── gemini_segments/            Raw .wav intermediates + metadata.json (which
        │                                voice/model made each segment) - implementation
        │                                detail assemble_video.py's audio resolution reads
        ├── previous_versions/           Every segment ever overwritten by
        │                                 generate_gemini_tts.py, timestamped
        │                                 (seg_4_20260706-143210.mp3). Nothing here is ever
        │                                 auto-deleted - prune by hand if it grows too large.
        ├── narration.mp3                Whole-track concat of the 7 segments, regenerated
        │                                 every run as a fallback/reference file
        ├── voice_options.md             Recommended macOS voices/rates (say-based generation)
        └── available_macos_voices.txt   Local voice inventory
```

## `backend/` — the machinery

```text
backend/
├── common.py               Shared path constants (VIDEO_DIR, AUDIO_DIR, SLIDES_DIR, ...) and
│                            small helpers (run_command, redact_workspace_paths, ffprobe
│                            duration helpers) - imported by every stage script below so a
│                            path or the PII-redaction logic can't drift between them.
├── generate_video.py       Pure rendering primitives: SLIDES_DATA (the 4 hand-authored
│                            slides, each tagged with its real segment_number), draw_slide,
│                            draw_log_card, draw_stat_card, font loaders. No orchestration.
├── build_slides.py         STAGE 1 - see "The visual workflow" above.
│
├── audio_generation/
│   ├── generate_gemini_tts.py    STAGE 2 (final). Calls Gemini API TTS. COSTS QUOTA
│   │                               (~10/day). Writes the front-facing mp3s to ../audio/ and
│   │                               the wav/metadata detail to
│   │                               ../audio/details/gemini_segments/. Archives any segment
│   │                               it overwrites to ../audio/details/previous_versions/ first.
│   └── generate_say_preview.py   STAGE 2 (iteration). Free local macOS 'say' audio into
│                                   ../audio/say_preview/. Never touches the canonical
│                                   ../audio/seg_N.mp3.
│
├── assemble_video.py       STAGE 3 - see intro above. Reads slides/rendered/ + audio/ (+
│                            audio/say_preview/ when --segments is passed) and
│                            narrative/slide_narration_segments.yaml; writes captions.srt +
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
