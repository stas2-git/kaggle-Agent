# Automated Video Generation Tooling

This directory provides automated scripts and specifications to compile the presentation slides, macOS voiceover, subtitles, and command evidence cards into a synchronized draft demo video for the Kaggle Capstone.

---

## Folder Structure

* `video_spec.md`: Video guidelines, durations, and constraints.
* `narration_script.md`: Timing-annotated visual cues and narration text.
* `narration_script_plain.txt`: Clean, unformatted narration text.
* `slide_narration_segments.yaml`: **Segment Mapping**. Maps slide titles, visuals, and segment narration.
* `available_macos_voices.txt`: List of all installed voices on your system.
* `voice_options.md`: Guide to optimizing local macOS voice quality and rates.
* `video_asset_checklist.md`: Visual and audio assets checklist.
* `captions.srt`: Subtitle tracks.
* `generate_gemini_tts.py`: **Gemini TTS Generator**. Calls Gemini API TTS to produce a premium narration file.
* `generate_chattts.py`: **ChatTTS Generator**. Calls ChatTTS locally to generate premium narration files for all slides.
* `generate_all.py`: **Primary Orchestrator**. Runs tests/evals, compiles segment audios, renders segment-specific video clips matching audio lengths, and stitches them.
* `assets/`: Contains generated slides, output logs, and compiled narration.

---

## 1. Primary Entrance: Automated Video Pipeline

To run the entire automated video-generation process—including executing verification tests and evaluations, drawing slide cards, capturing logs, rendering cards, generating narration, and merging them into the final draft:

```bash
uv run python submission/video/generate_all.py
```

### Voice and Rate Customization (macOS say fallback)
Standard macOS `say` reads at roughly 185–200 words per minute (WPM), which sounds rushed. The orchestrator defaults to a slower, clearer **170 WPM** to improve local voice quality.

To run with a different voice or speech rate:
```bash
uv run python submission/video/generate_all.py --voice Daniel --rate 165
```
*(See [voice_options.md](file:///Users/stan/Library/CloudStorage/GoogleDrive-staskhalitov%20@gmail.com/My%20Drive/keggle%20Agent/submission/video/voice_options.md) for recommended local voices.)*

---

## 2. Premium Local Voiceover Generation using ChatTTS (Recommended)

To compile the video using the highly realistic, open-source ChatTTS model running locally on your Mac:

### Step 1: Generate ChatTTS Voice Segments
Run the local generation script:
```bash
uv run python submission/video/generate_chattts.py
```
*This will load the model, generate all 7 slide segments locally with a consistent speaker voice (locked using seed 888), and save them under `assets/chattts_segments/`.*

### Step 2: Run the Orchestrator
Run the primary compiler script:
```bash
uv run python submission/video/generate_all.py
```
*The orchestrator automatically detects these premium segments, measures their durations, renders the slides to match their lengths exactly, and stitches the final video.*

---

## 3. Optional Gemini API TTS

You can generate a premium voiceover narration track using the Gemini API. 

### Step 1: Export API Key Temporarily
To avoid writing or storing your API key in workspace files, export it temporarily in your terminal session:
```bash
export GOOGLE_API_KEY="your_api_key_here"
# or
export GEMINI_API_KEY="your_api_key_here"
```
> [!WARNING]
> Do NOT commit your API key or write it into `.env` or any other tracked workspace files.

### Step 2: Generate Gemini TTS Narration Segments
Run the TTS generator script:
```bash
uv run python submission/video/generate_gemini_tts.py
```
This script calls `gemini-3.1-flash-tts-preview` to generate individual audio segment files under `assets/gemini_segments/` for each slide. 
*Generating slide-by-slide prevents the preview model from drifting or looping on long scripts, ensuring high-quality, stable, and perfectly timed audio.*
If the API is unavailable or the key is missing, the generation will fail gracefully and fall back to macOS `say` voiceover.

### Step 3: Run the Orchestrator
Run the primary script to compile the final video using the generated premium narration segments:
```bash
uv run python submission/video/generate_all.py
```
*The orchestrator automatically detects the files in `assets/gemini_segments/`, measures their durations, renders segment-specific video clips matching those lengths exactly, and stitches them into a final synchronized draft video.*

---

## 3. How to Verify No Secrets Are Included

The pipeline automatically scans generated files in `submission/video/` for secrets before finishing. You can manually run a scan using:
```bash
grep -rnw submission/video/ -e "GEMINI_API_KEY" -e "AIza" -e "password"
```
Ensure no `.env` values or private file paths are visible in screenshots or logs.
