"""STAGE 3 of 3: assemble the final video from whatever specs currently exist on disk.

Reads slides/rendered/slide_1.png ... slide_7.png, story/audio/current/seg_N.mp3 (the
canonical narration), and story/slide_story.yaml as fixed inputs, and produces captions.srt +
draft_demo_video.mp4. Does NOT run pytest/eval/the live agent, and does NOT draw slides -
that's build_slides.py's job (stage 1). This stage is fast and deterministic: it only
combines specs you've already reviewed, it never regenerates them.

--segments lets you preview a wording change on specific segments using the free local 'say'
voice (via audio_generation/generate_say_preview.py) mixed with the canonical Gemini audio
for the rest, without touching story/audio/current/seg_N.mp3 itself.
"""

import os
import sys
import re
import json
import argparse
import shutil

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio_generation"))
from common import (
    VIDEO_DIR, SLIDES_DIR, AUDIO_DIR, SAY_PREVIEW_DIR, EVIDENCE_DIR,
    OUTPUTS_DIR, VERIFICATION_RESULTS_PATH, TEMP_SEGMENTS_DIR, WORKSPACE_ROOT,
    run_command, redact_workspace_paths, get_format_duration, get_stream_duration,
)
from story_contract import build_narration_segments
from generate_say_preview import generate_say_preview

def create_temp_dir():
    if os.path.exists(TEMP_SEGMENTS_DIR):
        shutil.rmtree(TEMP_SEGMENTS_DIR)
    os.makedirs(TEMP_SEGMENTS_DIR, exist_ok=True)

def load_verification_results():
    if not os.path.exists(VERIFICATION_RESULTS_PATH):
        print(f"Warning: {VERIFICATION_RESULTS_PATH} not found - run build_slides.py at least once first. Treating pytest/eval/run status as unknown (fail-closed).")
        return {"pytest_passed": False, "eval_passed": False, "run_passed": False}
    with open(VERIFICATION_RESULTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _format_srt_timestamp(seconds):
    millis = int(round(seconds * 1000))
    hours, millis = divmod(millis, 3600000)
    minutes, millis = divmod(millis, 60000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def write_captions_srt(segments, segment_durations, output_path):
    """Generate captions.srt from segment narration text and actual audio durations.

    Captions are derived here, not hand-maintained, so they can never drift from
    story/slide_story.yaml the way a static file would.
    """
    entries = []
    current_time = 0.0
    for seg, duration in zip(segments, segment_durations):
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", seg["narration_text"]) if s.strip()]
        chunks = []
        for sentence in sentences:
            words = sentence.split()
            if len(words) <= 22:
                chunks.append(sentence)
            else:
                mid = len(words) // 2
                chunks.append(" ".join(words[:mid]))
                chunks.append(" ".join(words[mid:]))

        total_chars = sum(len(c) for c in chunks) or 1
        seg_time = current_time
        for chunk in chunks:
            chunk_duration = duration * (len(chunk) / total_chars)
            entries.append((seg_time, seg_time + chunk_duration, chunk))
            seg_time += chunk_duration
        current_time += duration

    with open(output_path, "w", encoding="utf-8") as f:
        for idx, (start, end, text) in enumerate(entries, 1):
            f.write(f"{idx}\n{_format_srt_timestamp(start)} --> {_format_srt_timestamp(end)}\n{text}\n\n")

    print(f"Generated captions at: {output_path}")

def build_segment_videos(segments, durations):
    print("\nRendering individual segment video clips...")
    segment_video_paths = []
    buffer = 0.30  # seconds padding for local tts pauses

    for idx, seg in enumerate(segments, 1):
        image_relative = seg["visual"]
        image_path = os.path.join(VIDEO_DIR, image_relative)
        audio_path = os.path.join(TEMP_SEGMENTS_DIR, f"seg_{idx}.mp3")
        video_path = os.path.join(TEMP_SEGMENTS_DIR, f"video_{idx}.mp4")

        if not os.path.exists(image_path):
            image_path = os.path.join(WORKSPACE_ROOT, image_relative)

        # Voiced video with apad + shortest to sync streams exactly. Force a fixed output
        # sample rate (44100) regardless of the source audio's native rate - Gemini TTS
        # segments are 24000 Hz, macOS 'say' segments are 22050 Hz, and concatenate_videos()
        # re-encodes audio on the final concat anyway, but keeping every segment clip at one
        # consistent rate here avoids relying on that as the only safety net.
        target_duration = durations[idx - 1] + buffer
        cmd = f"ffmpeg -y -loop 1 -r 25 -i '{image_path}' -i '{audio_path}' -filter_complex \"[1:a]apad[a]\" -map 0:v -map \"[a]\" -c:v libx264 -tune stillimage -c:a aac -ar 44100 -b:a 192k -pix_fmt yuv420p -shortest -t {target_duration:.3f} '{video_path}'"

        stdout, stderr, rc = run_command(cmd)
        if rc != 0:
            print(f"Error rendering segment {idx}: {stderr}")
            sys.exit(1)

        segment_video_paths.append(video_path)

    return segment_video_paths

def concatenate_videos(video_paths, output_path):
    concat_list_path = os.path.join(TEMP_SEGMENTS_DIR, "concat_segments.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for path in video_paths:
            f.write(f"file '{path}'\n")

    print(f"\nConcatenating {len(video_paths)} segment clips into {output_path}...")
    # Video is stream-copied (safe: every segment clip was encoded with identical libx264
    # settings above). Audio is NOT stream-copied - each segment .mp4 is a separately-encoded
    # AAC file with its own edit-list-encoded encoder priming samples, and raw concat demuxer
    # + '-c copy' just splices packets without reconciling those, corrupting playback after
    # the first segment in edit-list-strict players (QuickTime/Preview/AVFoundation) even
    # though ffmpeg's own decoder tolerates it. Re-encoding audio here decodes each segment
    # properly and produces one genuinely continuous track.
    cmd = f"ffmpeg -y -f concat -safe 0 -i '{concat_list_path}' -c:v copy -c:a aac -ar 44100 -b:a 192k '{output_path}'"
    stdout, stderr, rc = run_command(cmd)
    if rc != 0:
        print(f"Error during concatenation: {stderr}")
        sys.exit(1)

def run_security_scan():
    print("\nRunning safety security scan on generated assets...")
    found_issues = []

    scan_paths = [os.path.join(VIDEO_DIR, "captions.srt")]
    if os.path.exists(OUTPUTS_DIR):
        for entry in os.listdir(OUTPUTS_DIR):
            scan_paths.append(os.path.join(OUTPUTS_DIR, entry))

    for file_path in scan_paths:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                aiza_match = re.search(r"AIzaSy[A-Za-z0-9_-]{35}", content)
                if aiza_match:
                    found_issues.append(f"{os.path.basename(file_path)}: Hardcoded Google AI API key: [MASKED]")

                # Defense-in-depth: catch a leaked local workspace path even if some future
                # capture point forgets to call redact_workspace_paths() first. The Google
                # Drive sync folder name embeds the user's email (GoogleDrive-name@domain),
                # so an unredacted absolute path is a PII leak, not just noise.
                if WORKSPACE_ROOT in content:
                    found_issues.append(f"{os.path.basename(file_path)}: Un-redacted absolute workspace path (leaks local username/email via folder name): [MASKED]")

                sensitive_assign = re.search(r"(GEMINI_API_KEY|GOOGLE_API_KEY|password|secret|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]", content, re.IGNORECASE)
                if sensitive_assign:
                    found_issues.append(f"{os.path.basename(file_path)}: Exposed sensitive value assignment: [MASKED]")

                for line_idx, line in enumerate(content.splitlines(), 1):
                    if re.match(r"^[A-Z0-9_]+=[^\s]+", line) and not any(term in line for term in ["GOOGLE_API_KEY", "GEMINI_API_KEY", "PATH="]):
                        found_issues.append(f"{os.path.basename(file_path)}:L{line_idx} - Potential raw environment variable dump: [MASKED]")

            except Exception as e:
                print(f"Skipping scan for {os.path.basename(file_path)}: {e}")

    if found_issues:
        print("\n" + "!" * 60)
        print("SECURITY AUDIT ALERT: Potential secret leak detected!")
        for issue in found_issues:
            print(f"  * {issue}")
        print("!" * 60 + "\n")
        return False, found_issues
    else:
        print("Security audit passed. No credentials, secret keys, or raw env leaks detected in generated assets.")
        return True, []

def write_generation_report(results, audio_source, model_used, voice_name, speech_rate, scan_passed, scan_issues, final_video_path):
    report_path = os.path.join(EVIDENCE_DIR, "video_generation_report.md")

    status_emoji = "✅" if (results.get("pytest_passed") and results.get("eval_passed") and results.get("run_passed") and scan_passed) else "❌"

    content = f"""# Video Generation Execution Report {status_emoji}

This report summarizes the outcome of assemble_video.py (stage 3). Pytest/eval/live-demo
status below reflects the last build_slides.py (stage 1) run, not this run - assemble_video.py
does not re-verify the agent, it only combines already-reviewed specs.

## 1. Verification Status (from the last build_slides.py run)
- **Pytest Suite**: {"PASS ✅" if results.get("pytest_passed") else "FAIL ❌"} ({results.get("pytest_headline", "n/a")})
- **Offline Evaluations**: {"PASS ✅" if results.get("eval_passed") else "FAIL ❌"} ({results.get("eval_headline", "n/a")})
- **Vertical-Slice Review Run**: {"PASS ✅" if results.get("run_passed") else "FAIL ❌"}
- **Verification generated at**: `{results.get("generated_at", "unknown - run build_slides.py")}`

## 2. This Assembly Run
- **Voiceover TTS Source**: `{audio_source}`
- **Model Used**: `{model_used}`
- **Voice / Config Name**: `{voice_name}`
- **Speech Rate (macOS Say only)**: `{speech_rate} WPM`
- **Security Secret Audit Scan**: {"PASS ✅" if scan_passed else "FAIL ❌"}

## 3. Timing Measurements & Bounds Checks
- **Narration Audio Duration**: {results.get("narration_duration"):.3f} seconds
- **Final Video Duration**: {results.get("video_duration"):.3f} seconds
- **Absolute Duration Difference**: {results.get("duration_diff"):.3f} seconds
- **Duration Boundary Status**: {"PASS (Within 1.0s limit) ✅" if results.get("duration_bounds_pass") else "FAIL (Exceeds 1.0s difference) ❌"}
- **Video Output Path**: `{redact_workspace_paths(final_video_path)}`

## 4. Generated Outputs
- **Slides** (7 reviewable segment visuals, `submission/02_video/slides/rendered/`): `slide_1.png` ... `slide_7.png`
- **Auditable Command Logs** (from the last build_slides.py run, `submission/02_video/backend/evidence/demo_outputs/`):
  - Pytest Log: `pytest_output.txt`
  - Scorecard Log: `eval_output.txt`
  - Review Run Log: `run_output.txt`
- **Bonus Evidence** (not part of the 7-slide deck, `submission/02_video/backend/evidence/demo_cards/`): `pytest_card.png`, `trace_card.png`

## 5. Security Audit Findings
"""
    if scan_passed:
        content += "- **Result**: SUCCESS. No raw API keys, AIza key signatures, un-redacted workspace paths, or un-scrubbed `.env` references were found.\n"
    else:
        content += "- **Result**: WARNING/FAIL. The following potential issues were found:\n"
        for issue in scan_issues:
            content += f"  - {issue}\n"

    content += """
## 6. Verification Commands
Confirm outputs locally using:
- Pytest passing verification: `uv run pytest`
- Check generated trace exists: `cd project_build && ls outputs/traces/`
- View generated reports: `cd project_build && ls outputs/reports/`
"""
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated final run summary report at: {report_path}")

def main():
    parser = argparse.ArgumentParser(description="Assemble draft_demo_video.mp4 from the current slides/audio specs")
    parser.add_argument("--voice", default="Samantha", help="Voice override for macOS 'say' (default: Samantha)")
    parser.add_argument("--rate", type=int, default=170, help="Speech rate override in WPM (default: 170)")
    parser.add_argument("--audio-source", default="auto", choices=["auto", "gemini", "say"], help="Explicitly select audio source (default: auto - prefer canonical Gemini audio in story/audio/current/, fall back to macOS 'say' if no complete set exists)")
    parser.add_argument("--segments", default=None, help="Comma-separated 1-indexed segment numbers to preview with fresh macOS 'say' audio (e.g. '4,5,6'). All other segments use story/audio/current/seg_N.mp3 untouched - nothing in current audio is overwritten by this script.")
    args = parser.parse_args()

    target_segments = None
    if args.segments:
        try:
            target_segments = {int(s.strip()) for s in args.segments.split(",") if s.strip()}
        except ValueError:
            print(f"Error: --segments must be comma-separated integers, got: {args.segments}")
            sys.exit(1)

    create_temp_dir()

    segments = build_narration_segments()

    if target_segments is not None:
        unknown = target_segments - set(range(1, len(segments) + 1))
        if unknown:
            print(f"Error: --segments references segment(s) that don't exist: {sorted(unknown)} (valid range: 1-{len(segments)})")
            sys.exit(1)

    for slide_num in range(1, len(segments) + 1):
        slide_path = os.path.join(SLIDES_DIR, f"slide_{slide_num}.png")
        if not os.path.exists(slide_path):
            print(f"Error: {slide_path} does not exist. Run build_slides.py first.")
            sys.exit(1)

    gemini_metadata_path = os.path.join(AUDIO_DIR, "details", "gemini_segments", "metadata.json")

    def find_gemini_cached(idx):
        mp3_path = os.path.join(AUDIO_DIR, f"seg_{idx}.mp3")
        wav_path = os.path.join(AUDIO_DIR, "details", "gemini_segments", f"seg_{idx}.wav")
        if os.path.exists(mp3_path):
            return mp3_path
        if os.path.exists(wav_path):
            return wav_path
        return None

    use_gemini_segments = False
    gemini_paths = []
    if (args.audio_source in ["auto", "gemini"]) and os.path.exists(gemini_metadata_path):
        temp_paths = [find_gemini_cached(i) for i in range(1, len(segments) + 1)]
        if all(temp_paths):
            use_gemini_segments = True
            gemini_paths = temp_paths
            print("\nGemini TTS segment files detected and verified.")

    segment_durations = []
    audio_source = "local macOS say"
    model_used = "N/A"
    voice_used = args.voice

    def copy_or_convert(src_path, idx):
        dst_mp3_path = os.path.join(TEMP_SEGMENTS_DIR, f"seg_{idx}.mp3")
        if src_path.endswith(".wav"):
            conv_cmd = f"ffmpeg -y -i '{src_path}' -codec:a libmp3lame -qscale:a 2 '{dst_mp3_path}'"
            stdout, stderr, rc = run_command(conv_cmd)
            if rc != 0:
                print(f"Error converting cached WAV to MP3 for segment {idx}: {stderr}")
                sys.exit(1)
        else:
            shutil.copy2(src_path, dst_mp3_path)
        return get_format_duration(dst_mp3_path)

    if target_segments is not None:
        # Targeted mode: fresh 'say' preview for the named segments; everything else reuses
        # the canonical Gemini audio in story/audio/current/ untouched. Never writes into
        # story/audio/current/seg_N.mp3 - say output always lands in story/audio/previews/say/.
        print(f"\nTargeted segment mode: previewing segment(s) {sorted(target_segments)} with macOS 'say'; reusing canonical Gemini audio for the rest where available.")

        say_indices = list(target_segments)
        segment_durations_map = {}
        segment_labels = {}

        for idx in range(1, len(segments) + 1):
            if idx in target_segments:
                continue
            src_path = find_gemini_cached(idx)
            if src_path is None:
                print(f"No canonical Gemini audio found for segment {idx}; falling back to 'say' for it too.")
                say_indices.append(idx)
                continue
            segment_durations_map[idx] = copy_or_convert(src_path, idx)
            segment_labels[idx] = "Gemini API TTS (cached)"

        say_durations = generate_say_preview(segments, args.voice, args.rate, indices=sorted(say_indices))
        for idx, dur in say_durations.items():
            shutil.copy2(os.path.join(SAY_PREVIEW_DIR, f"seg_{idx}.mp3"), os.path.join(TEMP_SEGMENTS_DIR, f"seg_{idx}.mp3"))
            segment_durations_map[idx] = dur
            segment_labels[idx] = "local macOS say"

        segment_durations = [segment_durations_map[idx] for idx in range(1, len(segments) + 1)]

        by_label = {}
        for idx, label in segment_labels.items():
            by_label.setdefault(label, []).append(idx)
        audio_source = "Mixed: " + "; ".join(f"{label} (segments {sorted(idxs)})" for label, idxs in sorted(by_label.items()))
        model_used = "Mixed (see audio_source)"
        voice_used = f"Mixed (say={args.voice} for previewed segments)"

    elif use_gemini_segments:
        print("\nCopying canonical Gemini segment audios to temp directory...")
        for idx, src_path in enumerate(gemini_paths, 1):
            segment_durations.append(copy_or_convert(src_path, idx))

        try:
            with open(gemini_metadata_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            audio_source = meta.get("source", "Gemini API TTS (Segment-Based)")
            model_used = meta.get("model", "gemini-3.1-flash-tts-preview")
            voice_used = meta.get("voice", "Kore")
        except Exception:
            audio_source = "Gemini API TTS (Segment-Based)"
            model_used = "gemini-3.1-flash-tts-preview"
            voice_used = "Kore"

    else:
        # No complete canonical Gemini set exists - preview the whole thing with 'say'.
        say_durations = generate_say_preview(segments, args.voice, args.rate)
        for idx in range(1, len(segments) + 1):
            shutil.copy2(os.path.join(SAY_PREVIEW_DIR, f"seg_{idx}.mp3"), os.path.join(TEMP_SEGMENTS_DIR, f"seg_{idx}.mp3"))
        segment_durations = [say_durations[i] for i in range(1, len(segments) + 1)]

    write_captions_srt(segments, segment_durations, os.path.join(VIDEO_DIR, "captions.srt"))

    final_video_out = os.path.join(VIDEO_DIR, "draft_demo_video.mp4")

    if target_segments is not None:
        print(f"\nUsing mixed narration mode ({audio_source})...")
    elif use_gemini_segments:
        print(f"\nUsing Gemini segment-based narration mode ({audio_source})...")
    else:
        print("\nUsing standard macOS 'say' narration mode...")

    # Concatenate segment audios into narration.mp3 for fallback/reference
    seg_audios_list = [os.path.join(TEMP_SEGMENTS_DIR, f"seg_{i}.mp3") for i in range(1, len(segments) + 1)]
    audio_concat_list = os.path.join(TEMP_SEGMENTS_DIR, "audio_concat.txt")
    with open(audio_concat_list, "w", encoding="utf-8") as f:
        for path in seg_audios_list:
            f.write(f"file '{path}'\n")

    narration_mp3_path = os.path.join(AUDIO_DIR, "details", "narration.mp3")
    os.makedirs(os.path.dirname(narration_mp3_path), exist_ok=True)
    print("Stitching segment audios together...")
    stitch_cmd = f"ffmpeg -y -f concat -safe 0 -i '{audio_concat_list}' -c copy '{narration_mp3_path}'"
    s_stdout, s_stderr, s_rc = run_command(stitch_cmd)
    if s_rc != 0:
        print(f"Warning: failed to stitch audio file narration.mp3: {s_stderr}")

    seg_videos = build_segment_videos(segments, segment_durations)
    concatenate_videos(seg_videos, final_video_out)

    final_video_duration = get_stream_duration(final_video_out, "v:0")
    final_audio_duration = get_stream_duration(final_video_out, "a:0")
    narration_duration = final_audio_duration

    if final_video_duration == 0.0:
        print("Error: Could not determine video stream duration of generated video.")
        sys.exit(1)

    print(f"\nFinal Video Track Duration: {final_video_duration:.3f} seconds")
    print(f"Final Audio Track Duration: {final_audio_duration:.3f} seconds")

    results = load_verification_results()
    results["video_duration"] = final_video_duration
    results["narration_duration"] = narration_duration
    duration_diff = abs(final_video_duration - narration_duration)
    results["duration_diff"] = duration_diff
    bounds_passed = (duration_diff <= 1.0)
    results["duration_bounds_pass"] = bounds_passed

    if not bounds_passed:
        print(f"\nERROR: Video duration ({final_video_duration:.3f}s) and narration duration ({narration_duration:.3f}s) differ by {duration_diff:.3f}s, which exceeds the 1.0 second limit!")
        sys.exit(1)
    else:
        print("Validation Success: Video and audio track alignment is within 1.0 second boundary.")

    scan_passed, scan_issues = run_security_scan()

    print("Cleaning up temporary scratch files...")
    if os.path.exists(TEMP_SEGMENTS_DIR):
        shutil.rmtree(TEMP_SEGMENTS_DIR)

    write_generation_report(
        results=results,
        audio_source=audio_source,
        model_used=model_used,
        voice_name=voice_used,
        speech_rate=args.rate,
        scan_passed=scan_passed,
        scan_issues=scan_issues,
        final_video_path=final_video_out
    )

    if not (results.get("pytest_passed") and results.get("eval_passed") and results.get("run_passed") and scan_passed):
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
