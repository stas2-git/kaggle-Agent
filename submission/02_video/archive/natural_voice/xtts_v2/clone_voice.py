# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "TTS",
#     "numpy<2",
#     "scipy",
#     "transformers<=4.44.2",
#     "soundfile",
#     "torchcodec",
# ]
# ///
import os
import argparse
import torch

# Monkey-patch torch.load for PyTorch 2.6 compatibility with Coqui TTS
original_load = torch.load
def custom_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return original_load(*args, **kwargs)
torch.load = custom_load

from TTS.api import TTS

def main():
    parser = argparse.ArgumentParser(description="Clone voice using XTTS v2")
    parser.add_argument("--text", required=True, help="Text to speak")
    parser.add_argument("--speaker", default="my_voice.wav", help="Path to reference speaker WAV file (3-10 seconds of clear speech)")
    parser.add_argument("--output", default="cloned_output.wav", help="Output WAV path")
    args = parser.parse_args()

    # Resolve paths relative to script directory if needed
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    speaker_path = args.speaker
    if not os.path.isabs(speaker_path):
        speaker_path = os.path.join(script_dir, speaker_path)

    output_path = args.output
    if not os.path.isabs(output_path):
        output_path = os.path.join(script_dir, output_path)

    if not os.path.exists(speaker_path):
        print(f"Error: Reference speaker file not found: {speaker_path}")
        print("\nTo fix this:")
        print("1. Record a 5-10 second WAV file of your own voice.")
        print("2. Make sure it is clean and has no background noise.")
        print(f"3. Save it to: {speaker_path}")
        return

    print("Loading XTTS v2 model (this will download model weights on the first run, ~2GB)...")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

    print(f"\nGenerating cloned voiceover for text:\n\"{args.text}\"\n")
    tts.tts_to_file(
        text=args.text,
        speaker_wav=speaker_path,
        language="en",
        file_path=output_path
    )
    print(f"\nSuccess! Saved cloned audio to: {output_path}")

if __name__ == "__main__":
    main()
