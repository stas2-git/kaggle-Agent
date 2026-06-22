# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "TTS",
#     "numpy<2",
#     "scipy",
#     "pyyaml",
#     "transformers<=4.44.2",
#     "soundfile",
#     "torchcodec",
# ]
# ///
import os
import sys
import argparse
import json
import subprocess
import shutil
import yaml
import torch

# Monkey-patch torch.load for PyTorch 2.6 compatibility with Coqui TTS
original_load = torch.load
def custom_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return original_load(*args, **kwargs)
torch.load = custom_load

from TTS.api import TTS

# Paths
VIDEO_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(VIDEO_DIR, "assets")
XTTS_SEGMENTS_DIR = os.path.join(ASSETS_DIR, "xtts_segments")

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

def run_command(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return res.stdout, res.stderr, res.returncode

def main():
    parser = argparse.ArgumentParser(description="Generate natural local conversational segment voiceovers using XTTS v2 cloned voice")
    parser.add_argument("--speaker", default="my_voice_combined.wav", help="Speaker reference wav filename")
    args = parser.parse_args()

    # Read slide narration segments YAML
    yaml_path = os.path.join(VIDEO_DIR, "slide_narration_segments.yaml")
    if not os.path.exists(yaml_path):
        print(f"Error: YAML segments config not found at: {yaml_path}")
        sys.exit(1)

    with open(yaml_path, "r", encoding="utf-8") as f:
        seg_data = yaml.safe_load(f)
    segments = seg_data["segments"]

    project_root = os.path.dirname(os.path.dirname(VIDEO_DIR))
    natural_voice_dir = os.path.join(project_root, "natural_voice", "xtts_v2")
    speaker_path = os.path.join(natural_voice_dir, args.speaker)
    if not os.path.exists(speaker_path):
        # Fallback to check natural_voice root
        speaker_path = os.path.join(project_root, "natural_voice", args.speaker)
        if not os.path.exists(speaker_path):
            print(f"Error: Speaker reference audio file not found at: {speaker_path}")
            sys.exit(1)

    print(f"Using speaker reference audio: {speaker_path}")

    # Recreate clean xtts segments directory
    if os.path.exists(XTTS_SEGMENTS_DIR):
        try:
            shutil.rmtree(XTTS_SEGMENTS_DIR)
        except Exception:
            pass
    os.makedirs(XTTS_SEGMENTS_DIR, exist_ok=True)

    print("Loading XTTS v2 model (multi-lingual multi-dataset)...")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

    ffmpeg_available = check_ffmpeg()
    generated_info = []

    print(f"Preparing to generate {len(segments)} narration segments using your cloned voice...")

    for idx, seg in enumerate(segments, 1):
        slide_num = seg["slide_number"]
        title = seg.get("title", f"Slide {slide_num}")
        text = seg["narration_text"]

        # If needed, we can preprocess or tweak words here.
        # Let's keep it clean since XTTS generally pronounces words correctly.
        clean_text = text

        print(f"\nGenerating Cloned Audio for Segment {idx}/{len(segments)}: '{title}' ({len(clean_text)} chars)...")

        try:
            wav_name = f"seg_{idx}.wav"
            mp3_name = f"seg_{idx}.mp3"
            wav_path = os.path.join(XTTS_SEGMENTS_DIR, wav_name)
            mp3_path = os.path.join(XTTS_SEGMENTS_DIR, mp3_name)

            # Generate WAV file
            tts.tts_to_file(
                text=clean_text,
                speaker_wav=speaker_path,
                language="en",
                file_path=wav_path
            )
            print(f"Saved XTTS WAV: {wav_name}")

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
                "wav_file": wav_name,
                "mp3_file": mp3_name if ffmpeg_available else None
            })

        except Exception as e:
            print(f"\nXTTS Voice Cloning Failed for segment {idx}: {e}")
            sys.exit(1)

    # Write metadata JSON file
    metadata_path = os.path.join(XTTS_SEGMENTS_DIR, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump({
            "source": "Local XTTS v2 Cloned Voice",
            "model": "XTTS v2 Core",
            "voice": f"Reference: {args.speaker}",
            "segments": generated_info
        }, f, indent=2)
        
    print("\n" + "="*60)
    print("Success: All segments generated locally using XTTS v2 Cloned Voice!")
    print(f"Metadata file written at: {metadata_path}")
    print("="*60)

if __name__ == "__main__":
    main()
