import os
import sys
import argparse
import json
import subprocess
import shutil
import time
import wave
from google import genai
from google.genai import types

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import AUDIO_DIR, AUDIO_VERSIONS_DIR
from story_contract import build_narration_segments

# Paths - the final .mp3 files are the front-facing current audio in story/audio/current/;
# the raw .wav intermediates and metadata.json are implementation details tucked into
# current/details/gemini_segments/.
VIDEO_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GEMINI_MP3_DIR = AUDIO_DIR
GEMINI_DETAILS_DIR = os.path.join(AUDIO_DIR, "details", "gemini_segments")
# Every time a segment is about to be overwritten, its current file(s) are copied into a
# timestamped folder under story/audio/versions/. Regeneration never destroys a prior take,
# it only adds a new current one.
VERSIONS_DIR = AUDIO_VERSIONS_DIR

def archive_existing_segment(idx, version_dir):
    """Copy the current seg_{idx}.mp3/.wav (if present) into VERSIONS_DIR before it gets
    overwritten. Called right before a regeneration write, never on a cache-hit path, so a
    segment that's never touched is never archived either."""
    archived = []
    for src_dir, subdir, name in (
        (GEMINI_MP3_DIR, "segments", f"seg_{idx}.mp3"),
        (GEMINI_DETAILS_DIR, "gemini_wav", f"seg_{idx}.wav"),
    ):
        src_path = os.path.join(src_dir, name)
        if os.path.exists(src_path):
            dst_dir = os.path.join(version_dir, subdir)
            os.makedirs(dst_dir, exist_ok=True)
            dst_path = os.path.join(dst_dir, name)
            shutil.copy2(src_path, dst_path)
            archived.append(dst_path)
    if archived:
        print(f"Archived prior version(s) of segment {idx} to: {', '.join(archived)}")
    return archived

def write_archive_manifest(version_dir, args, target_segments, archived_segments):
    if not archived_segments:
        return
    os.makedirs(version_dir, exist_ok=True)
    with open(os.path.join(version_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump({
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "reason": "Prior current audio preserved before Gemini TTS regeneration",
            "model": args.model,
            "voice": args.voice,
            "target_segments": sorted(target_segments) if target_segments else "all",
            "archived_segments": sorted(archived_segments),
            "layout": {
                "segments": "Prior current MP3 files",
                "gemini_wav": "Prior Gemini WAV intermediates, when present"
            }
        }, f, indent=2)

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

def run_command(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return res.stdout, res.stderr, res.returncode

def write_wave_file(filename, pcm_data, channels=1, rate=24000, sample_width=2):
    """Writes raw PCM data into a valid WAV container with a proper RIFF header."""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)

def main():
    parser = argparse.ArgumentParser(description="Generate premium segment TTS voiceovers using Gemini API")
    parser.add_argument("--model", default="gemini-3.1-flash-tts-preview", help="Gemini model name")
    parser.add_argument("--voice", default="Kore", help="Prebuilt voice name config (e.g. Kore, Puck, etc.)")
    parser.add_argument("--instruction", default="Read in a calm, confident, professional demo narration style. Clear pacing. Not overly enthusiastic.", help="Narrator prompt instruction")
    parser.add_argument("--force", action="store_true", help="Force recreation of all segment files, bypassing cache")
    parser.add_argument("--segments", default=None, help="Comma-separated 1-indexed segment numbers to regenerate (e.g. '4,5,6'). Leaves all other cached segments untouched. Implies --force for just those segments.")
    args = parser.parse_args()

    target_segments = None
    if args.segments:
        try:
            target_segments = {int(s.strip()) for s in args.segments.split(",") if s.strip()}
        except ValueError:
            print(f"Error: --segments must be comma-separated integers, got: {args.segments}")
            sys.exit(1)

    # Load .env file if it exists in the project root
    project_root = os.path.dirname(os.path.dirname(VIDEO_DIR))
    env_path = os.path.join(project_root, ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ[k.strip()] = v.strip()
        except Exception:
            pass

    # Read API Key only from environment variables
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("="*60)
        print("Notice: No GEMINI_API_KEY or GOOGLE_API_KEY found in the environment.")
        print("To generate Gemini TTS narration, run:")
        print("    export GOOGLE_API_KEY=\"your_key_here\"")
        print("Then run: cd project_build && uv run python ../submission/02_video/backend/audio_generation/generate_gemini_tts.py")
        print("="*60)
        sys.exit(0)

    segments = build_narration_segments()
    archive_run_dir = os.path.join(VERSIONS_DIR, f"{time.strftime('%Y%m%d-%H%M%S')}-gemini-regeneration")
    archived_segments = set()

    print(f"Connecting to Gemini API using model '{args.model}' and voice '{args.voice}'...")
    print(f"Preparing to generate {len(segments)} narration segments...")

    # Full --force (no --segments given) wipes every cached segment upfront, same as before -
    # except now every segment is archived to VERSIONS_DIR first, so the wipe can't lose audio.
    # A targeted --segments run never does this upfront wipe - untargeted segments' files are
    # never touched, and targeted segments are simply overwritten in place once their new audio
    # is successfully generated (see force_this_segment below), so a mid-run API failure can't
    # delete audio you haven't replaced yet.
    if args.force and target_segments is None:
        import glob
        for idx in range(1, len(segments) + 1):
            if archive_existing_segment(idx, archive_run_dir):
                archived_segments.add(idx)
        for stale_mp3 in glob.glob(os.path.join(GEMINI_MP3_DIR, "seg_*.mp3")):
            try:
                os.remove(stale_mp3)
            except Exception:
                pass
        if os.path.exists(GEMINI_DETAILS_DIR):
            try:
                shutil.rmtree(GEMINI_DETAILS_DIR)
            except Exception:
                pass

    os.makedirs(GEMINI_MP3_DIR, exist_ok=True)
    os.makedirs(GEMINI_DETAILS_DIR, exist_ok=True)

    client = genai.Client(api_key=api_key)
    ffmpeg_available = check_ffmpeg()

    generated_info = []

    metadata_path = os.path.join(GEMINI_DETAILS_DIR, "metadata.json")

    if target_segments:
        unknown = target_segments - set(range(1, len(segments) + 1))
        if unknown:
            print(f"Error: --segments references segment(s) that don't exist: {sorted(unknown)} (valid range: 1-{len(segments)})")
            sys.exit(1)
        print(f"Targeted regeneration: only segment(s) {sorted(target_segments)} will call the API; all others are reused from cache untouched.")

    for idx, seg in enumerate(segments, 1):
        slide_num = seg["slide_number"]
        title = seg.get("title", f"Slide {slide_num}")
        text = seg["narration_text"]

        wav_name = f"seg_{idx}.wav"
        mp3_name = f"seg_{idx}.mp3"
        wav_path = os.path.join(GEMINI_DETAILS_DIR, wav_name)
        mp3_path = os.path.join(GEMINI_MP3_DIR, mp3_name)

        # A segment is force-regenerated if it was explicitly named via --segments, or if a
        # bare --force was given with no --segments (full-force regenerates everything).
        force_this_segment = (idx in target_segments) if target_segments is not None else args.force

        # Check Cache: if files exist, reuse them
        has_mp3 = os.path.exists(mp3_path)
        has_wav = os.path.exists(wav_path)

        # If cache hit
        if not force_this_segment and ((ffmpeg_available and has_mp3) or (not ffmpeg_available and has_wav)):
            print(f"Using cached audio for Segment {idx}/{len(segments)}: '{title}'")
            generated_info.append({
                "slide_number": slide_num,
                "title": title,
                "text_length": len(text),
                "wav_file": wav_name if has_wav else None,
                "mp3_file": mp3_name if has_mp3 else None
            })
            continue

        print(f"\nGenerating Audio for Segment {idx}/{len(segments)}: '{title}' ({len(text)} chars)...")

        # Configure request for audio modality
        config_args = {
            "response_modalities": ["AUDIO"],
            "speech_config": types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=args.voice
                    )
                )
            ),
            "temperature": 0.2
        }
        
        # Omit developer system instructions for dedicated TTS models that do not support them
        if "tts" not in args.model.lower():
            config_args["system_instruction"] = args.instruction
            
        config = types.GenerateContentConfig(**config_args)

        try:
            response = client.models.generate_content(
                model=args.model,
                contents=text,
                config=config
            )

            if not response.candidates or not response.candidates[0].content.parts:
                print(f"Error: Gemini API response for segment {idx} was empty.")
                sys.exit(1)

            part = response.candidates[0].content.parts[0]
            if not hasattr(part, "inline_data") or not part.inline_data or not part.inline_data.data:
                print(f"Error: Gemini API response part inline_data for segment {idx} was empty.")
                sys.exit(1)

            audio_bytes = part.inline_data.data
            mime_type = part.inline_data.mime_type.lower() if part.inline_data.mime_type else ""
            print(f"Received {len(audio_bytes)} bytes (MIME Type: {mime_type}).")

            # Archive whatever is currently at mp3_path/wav_path before overwriting it. No-op
            # if this segment has never been generated before (nothing to archive yet).
            if archive_existing_segment(idx, archive_run_dir):
                archived_segments.add(idx)

            # Determine format
            is_mp3 = "mp3" in mime_type
            if is_mp3:
                # Direct MP3 save
                with open(mp3_path, "wb") as f:
                    f.write(audio_bytes)
                print(f"Saved MP3 direct: {mp3_name}")
            else:
                # Save PCM audio bytes with proper WAV RIFF headers
                write_wave_file(wav_path, audio_bytes)
                print(f"Saved formatted WAV: {wav_name}")

                if ffmpeg_available:
                    print(f"Converting WAV segment {idx} to MP3 using ffmpeg...")
                    cmd = f"ffmpeg -y -i '{wav_path}' -codec:a libmp3lame -qscale:a 2 '{mp3_path}'"
                    stdout, stderr, rc = run_command(cmd)
                    if rc != 0:
                        print(f"Warning: ffmpeg conversion failed for segment {idx}: {stderr}")
                else:
                    print(f"Warning: ffmpeg is not available, MP3 file '{mp3_name}' could not be generated.")

            generated_info.append({
                "slide_number": slide_num,
                "title": title,
                "text_length": len(text),
                "wav_file": wav_name if not is_mp3 else None,
                "mp3_file": mp3_name if (is_mp3 or ffmpeg_available) else None
            })

        except Exception as e:
            print(f"\nGemini API TTS Call Failed for segment {idx}: {e}")
            # Save partial metadata so generate_all.py knows what we have so far
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump({
                    "source": "Gemini API TTS (Segment-Based - Partial)",
                    "model": args.model,
                    "voice": args.voice,
                    "segments": generated_info
                }, f, indent=2)
            write_archive_manifest(archive_run_dir, args, target_segments, archived_segments)
            print("Partial progress saved in metadata.json. Existing segment audio files preserved.")
            sys.exit(1)

    # Write final metadata JSON file
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump({
            "source": "Gemini API TTS (Segment-Based)",
            "model": args.model,
            "voice": args.voice,
            "segments": generated_info
        }, f, indent=2)
    write_archive_manifest(archive_run_dir, args, target_segments, archived_segments)
        
    print("\n" + "="*60)
    print("Success: All segments generated using Gemini API TTS!")
    print(f"Metadata file written at: {metadata_path}")
    print("="*60)

if __name__ == "__main__":
    main()
