# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "ChatTTS",
#     "scipy",
#     "numpy<2",
#     "pyyaml",
#     "requests",
# ]
# ///
import os
import sys
import argparse
import json
import subprocess
import yaml
import scipy.io.wavfile
import torch
import ChatTTS

# Paths
VIDEO_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(VIDEO_DIR, "assets")
CHATTTS_SEGMENTS_DIR = os.path.join(ASSETS_DIR, "chattts_segments")

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

def run_command(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return res.stdout, res.stderr, res.returncode

def add_breaths(text):
    # Add a short breath [uv_break] at commas, colons, and semicolons
    # Add a slightly longer pause [break_3] at periods, question marks, and exclamation marks
    text = text.replace(". ", " . [break_3] ")
    text = text.replace("? ", " ? [break_3] ")
    text = text.replace("! ", " . [break_3] ")
    text = text.replace(", ", " , [uv_break] ")
    text = text.replace("; ", " ; [uv_break] ")
    text = text.replace(": ", " : [uv_break] ")
    text = text.replace(" - ", " [uv_break] ")
    text = text.replace(" – ", " [uv_break] ")
    if text.endswith("."):
        text = text[:-1] + " . [break_3]"
    elif text.endswith("?"):
        text = text[:-1] + " ? [break_3]"
    elif text.endswith("!"):
        text = text[:-1] + " . [break_3]"
    return text

def main():
    parser = argparse.ArgumentParser(description="Generate natural local conversational segment voiceovers using ChatTTS")
    parser.add_argument("--seed", type=int, default=888, help="Speaker random seed for consistent voice")
    parser.add_argument("--temp", type=float, default=0.1, help="Temperature for inference (lower is more stable/consistent)")
    parser.add_argument("--speed", type=int, default=3, help="Speaking speed setting from 0 (slowest) to 9 (fastest)")
    args = parser.parse_args()

    # Read slide narration segments YAML
    yaml_path = os.path.join(VIDEO_DIR, "slide_narration_segments.yaml")
    if not os.path.exists(yaml_path):
        print(f"Error: YAML segments config not found at: {yaml_path}")
        sys.exit(1)

    with open(yaml_path, "r", encoding="utf-8") as f:
        seg_data = yaml.safe_load(f)
    segments = seg_data["segments"]

    print("Loading ChatTTS model...")
    chat = ChatTTS.Chat()
    chat.load()

    # Setup consistent speaker embedding using the seed
    print(f"Sampling consistent speaker with seed {args.seed}...")
    torch.manual_seed(args.seed)
    rand_spk = chat.sample_random_speaker()

    params_infer_code = chat.InferCodeParams()
    params_infer_code.spk_emb = rand_spk
    params_infer_code.temperature = args.temp
    params_infer_code.prompt = f"[speed_{args.speed}]"

    params_refine_text = chat.RefineTextParams()
    params_refine_text.prompt = f"[speed_{args.speed}][oral_2][laugh_0][break_6]"

    print(f"Preparing to generate {len(segments)} narration segments locally at speed_{args.speed}...")

    # Recreate clean chattts segments directory
    if os.path.exists(CHATTTS_SEGMENTS_DIR):
        import shutil
        try:
            shutil.rmtree(CHATTTS_SEGMENTS_DIR)
        except Exception:
            pass
    os.makedirs(CHATTTS_SEGMENTS_DIR, exist_ok=True)

    ffmpeg_available = check_ffmpeg()
    generated_info = []

    for idx, seg in enumerate(segments, 1):
        slide_num = seg["slide_number"]
        title = seg.get("title", f"Slide {slide_num}")
        text = seg["narration_text"]

        # Preprocess text to inject natural breaks and breaths
        clean_text = f"[speed_{args.speed}] " + add_breaths(text)

        print(f"\nGenerating Audio for Segment {idx}/{len(segments)}: '{title}' ({len(clean_text)} chars)...")

        try:
            wavs = chat.infer(
                [clean_text],
                params_infer_code=params_infer_code,
                params_refine_text=params_refine_text
            )

            if not wavs or len(wavs) == 0:
                print(f"Error: ChatTTS generation for segment {idx} was empty.")
                sys.exit(1)

            audio_data = wavs[0]
            
            wav_name = f"seg_{idx}.wav"
            mp3_name = f"seg_{idx}.mp3"
            wav_path = os.path.join(CHATTTS_SEGMENTS_DIR, wav_name)
            mp3_path = os.path.join(CHATTTS_SEGMENTS_DIR, mp3_name)

            # Write WAV file (24000Hz)
            scipy.io.wavfile.write(wav_path, 24000, audio_data)
            print(f"Saved ChatTTS WAV: {wav_name}")

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
            print(f"\nChatTTS Generation Failed for segment {idx}: {e}")
            sys.exit(1)

    # Write metadata JSON file
    metadata_path = os.path.join(CHATTTS_SEGMENTS_DIR, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump({
            "source": "Local ChatTTS",
            "model": "ChatTTS Core v0.2",
            "voice": f"Seed {args.seed}",
            "segments": generated_info
        }, f, indent=2)
        
    print("\n" + "="*60)
    print("Success: All segments generated locally using ChatTTS!")
    print(f"Metadata file written at: {metadata_path}")
    print("="*60)

if __name__ == "__main__":
    main()
