# Story And Audio Package

This folder is the source package for the video's narration layer.

- `slide_story.yaml` is the canonical story contract: slide titles, visual ideas, takeaways,
  and the audio-safe script.
- `narration_segments.yaml` is a compatibility snapshot for humans or older tooling. Active
  scripts read `slide_story.yaml`.
- `audio/current/` is the current canonical audio used by `backend/assemble_video.py` when it
  runs without `--segments`.
- `audio/previews/say/` holds disposable local macOS `say` previews for iteration.
- `audio/versions/` holds prior audio snapshots. Nothing here is auto-deleted.

When regenerating Gemini TTS, `backend/audio_generation/generate_gemini_tts.py` archives any
current segment it is about to overwrite into `audio/versions/<timestamp>-gemini-regeneration/`
before writing the new current take.
