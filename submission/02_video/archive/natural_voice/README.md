# Local AI Voice Generation & Cloning

This directory provides scripts to run state-of-the-art open-source text-to-speech models locally on your Mac using `uv` sandboxing.

---

## 1. Voice Cloning using XTTS v2

XTTS v2 can clone your voice using a short reference audio clip.

### Step 1: Record your voice
1. Record a **5 to 10 second** clean audio clip of you speaking.
2. Read a simple sentence like:
   > *"I am testing the XTTS v2 voice cloning model locally on my computer. I want to see how well it mimics my voice."*
3. Save it as **`my_voice.wav`** in the `submission/03_voice_lab/natural_voice/xtts_v2/` directory.
   *(Make sure there is no background noise or loud static.)*

### Step 2: Run the script
Run this command from the repository root:
```bash
cd project_build
uv run ../submission/03_voice_lab/natural_voice/xtts_v2/clone_voice.py --text "Hello! This is a completely custom AI voice model synthesized locally on my Mac."
```
* On the first run, it will automatically download the ~2GB model weights.
* The output will be saved as `submission/03_voice_lab/natural_voice/xtts_v2/cloned_output.wav`.

---

## 2. Conversational Speech using ChatTTS

ChatTTS is optimized for natural conversational dialogue, supporting realistic voice tones, laughter, and breaks.

### Run the script
Run this command from the repository root:
```bash
cd project_build
uv run ../submission/03_voice_lab/natural_voice/chattts/generate_chat.py --text "So, [laughter] we are actually running this model locally, which is, you know, [uv_break] pretty cool."
```
* Supported tags to modify speech flow:
  * `[laughter]` (Adds natural laughter/chuckle)
  * `[sigh]` (Adds a sigh)
  * `[uv_break]` (Adds a brief natural conversational pause)
* The output will be saved as `submission/03_voice_lab/natural_voice/chattts/chat_output.wav`.
