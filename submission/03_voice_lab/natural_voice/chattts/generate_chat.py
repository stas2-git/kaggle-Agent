# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "ChatTTS",
#     "scipy",
#     "numpy<2",
# ]
# ///
import os
import argparse
import ChatTTS
import scipy.io.wavfile

def main():
    parser = argparse.ArgumentParser(description="Generate natural speech using ChatTTS")
    parser.add_argument("--text", required=True, help="Text to speak (supports tags like [laughter], [sigh], [uv_break])")
    parser.add_argument("--output", default="chat_output.wav", help="Output WAV path")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = args.output
    if not os.path.isabs(output_path):
        output_path = os.path.join(script_dir, output_path)

    print("Loading ChatTTS model...")
    chat = ChatTTS.Chat()
    chat.load()

    print(f"\nGenerating conversational audio for text:\n\"{args.text}\"\n")
    wavs = chat.infer([args.text])
    
    scipy.io.wavfile.write(output_path, 24000, wavs[0][0])
    print(f"\nSuccess! Saved conversational audio to: {output_path}")

if __name__ == "__main__":
    main()
