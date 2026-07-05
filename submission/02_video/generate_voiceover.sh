#!/bin/bash
# MacOS-safe voiceover generator script

# Define paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLAIN_SCRIPT="$SCRIPT_DIR/narration_script_plain.txt"
ASSETS_DIR="$SCRIPT_DIR/assets"
AIFF_OUT="$ASSETS_DIR/narration.aiff"
MP3_OUT="$ASSETS_DIR/narration.mp3"

# Create assets directory
mkdir -p "$ASSETS_DIR"

# Check narration script exists
if [ ! -f "$PLAIN_SCRIPT" ]; then
    echo "Error: Narration script plain text file not found at: $PLAIN_SCRIPT"
    exit 1
fi

# Set Voice (default to Samantha)
VOICE_NAME=${VOICE:-Samantha}

echo "Generating voiceover using macOS 'say' (Voice: $VOICE_NAME)..."
# Execute say
say -v "$VOICE_NAME" -f "$PLAIN_SCRIPT" -o "$AIFF_OUT"

if [ $? -eq 0 ]; then
    echo "Successfully generated AIFF voiceover at: $AIFF_OUT"
else
    echo "Error: Failed to generate AIFF voiceover."
    exit 1
fi

# Check if ffmpeg is installed
if command -v ffmpeg &> /dev/null; then
    echo "Converting AIFF to MP3 using ffmpeg..."
    ffmpeg -y -i "$AIFF_OUT" -codec:a libmp3lame -qscale:a 2 "$MP3_OUT"
    if [ $? -eq 0 ]; then
        echo "Successfully converted to MP3 at: $MP3_OUT"
    else
        echo "Error: ffmpeg conversion failed."
    fi
else
    echo "Warning: ffmpeg not found in PATH."
    echo "To convert the audio to MP3, please install ffmpeg: 'brew install ffmpeg'"
fi
