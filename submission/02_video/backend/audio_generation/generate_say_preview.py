"""STAGE 2b of 3: free/local audio spec preview via macOS 'say'.

Generates audio/say_preview/seg_N.mp3 for the given segments (default: all 7) using the free,
unlimited, local macOS 'say' voice - no quota, no API key, no cost. Use this to iterate on
narration wording before spending Gemini TTS quota (generate_gemini_tts.py) on the final
canonical audio/seg_N.mp3 files.

This never touches audio/seg_N.mp3 - say_preview/ is scratch space for listening, not a spec
you sign off on. assemble_video.py's --segments flag will use these previews for the named
segments and the canonical audio/seg_N.mp3 for the rest, so you can watch/listen to a mixed
draft before deciding the wording is final.
"""

import os
import sys
import shutil
import argparse
import yaml

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import NARRATIVE_DIR, AUDIO_DIR, SAY_PREVIEW_DIR, BACKEND_DIR, run_command, get_format_duration

SCRATCH_DIR = os.path.join(BACKEND_DIR, ".tmp", "say_preview_scratch")

def generate_say_preview(segments, voice_name, speech_rate, indices=None):
    """Generate macOS 'say' audio for the given 1-indexed segment numbers (default: all of
    them), writing the result straight to audio/say_preview/seg_N.mp3. Returns {idx: duration}.
    """
    target_indices = indices if indices is not None else list(range(1, len(segments) + 1))
    if not target_indices:
        return {}

    os.makedirs(SAY_PREVIEW_DIR, exist_ok=True)
    if os.path.exists(SCRATCH_DIR):
        shutil.rmtree(SCRATCH_DIR)
    os.makedirs(SCRATCH_DIR, exist_ok=True)

    print(f"Generating segment-level voiceovers using macOS 'say' (Voice: {voice_name}, Rate: {speech_rate} WPM) for segment(s) {target_indices}...")
    durations = {}

    for idx in target_indices:
        seg = segments[idx - 1]
        text = seg["narration_text"]
        text_path = os.path.join(SCRATCH_DIR, f"seg_{idx}.txt")
        aiff_path = os.path.join(SCRATCH_DIR, f"seg_{idx}.aiff")
        mp3_path = os.path.join(SAY_PREVIEW_DIR, f"seg_{idx}.mp3")

        with open(text_path, "w", encoding="utf-8") as f:
            f.write(text)

        cmd = f"say -v '{voice_name}' -r {speech_rate} -f '{text_path}' -o '{aiff_path}'"
        stdout, stderr, rc = run_command(cmd)
        if rc != 0:
            print(f"Error: say failed for segment {idx}: {stderr}")
            sys.exit(1)

        conv_cmd = f"ffmpeg -y -i '{aiff_path}' -codec:a libmp3lame -qscale:a 2 '{mp3_path}'"
        c_stdout, c_stderr, c_rc = run_command(conv_cmd)
        if c_rc != 0:
            print(f"Error: ffmpeg audio conversion failed for segment {idx}: {c_stderr}")
            sys.exit(1)

        dur = get_format_duration(mp3_path)
        print(f"Segment {idx} audio duration: {dur:.2f}s -> {mp3_path}")
        durations[idx] = dur

    shutil.rmtree(SCRATCH_DIR)
    return durations

def main():
    parser = argparse.ArgumentParser(description="Generate free local macOS 'say' audio previews into audio/say_preview/")
    parser.add_argument("--voice", default="Samantha", help="Voice override for macOS 'say' (default: Samantha)")
    parser.add_argument("--rate", type=int, default=170, help="Speech rate override in WPM (default: 170)")
    parser.add_argument("--segments", default=None, help="Comma-separated 1-indexed segment numbers to preview (default: all 7)")
    args = parser.parse_args()

    yaml_path = os.path.join(NARRATIVE_DIR, "slide_narration_segments.yaml")
    if not os.path.exists(yaml_path):
        print(f"Error: YAML segments config not found at: {yaml_path}")
        sys.exit(1)
    with open(yaml_path, "r", encoding="utf-8") as f:
        segments = yaml.safe_load(f)["segments"]

    indices = None
    if args.segments:
        try:
            indices = sorted({int(s.strip()) for s in args.segments.split(",") if s.strip()})
        except ValueError:
            print(f"Error: --segments must be comma-separated integers, got: {args.segments}")
            sys.exit(1)
        unknown = [i for i in indices if i not in range(1, len(segments) + 1)]
        if unknown:
            print(f"Error: --segments references segment(s) that don't exist: {unknown} (valid range: 1-{len(segments)})")
            sys.exit(1)

    generate_say_preview(segments, args.voice, args.rate, indices=indices)
    print(f"\nDone - listen to the results directly in: {AUDIO_DIR}/say_preview/")

if __name__ == "__main__":
    main()
