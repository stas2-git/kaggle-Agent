# Voice and Speech Rate Options

This document lists recommended native macOS voices and rate configurations to optimize local text-to-speech quality for the Capstone video.

## Recommended Voices (en_US / en_GB)

1. **Samantha (Default)**
   - **Language**: English (US)
   - **Characteristics**: Clear, standard professional female voice. Works best at a moderate rate (165–175 WPM).
   - **Usage**: `--voice Samantha --rate 170`

2. **Daniel**
   - **Language**: English (UK)
   - **Characteristics**: Clear British male voice. Very crisp articulation and natural phrasing.
   - **Usage**: `--voice Daniel --rate 170`

3. **Alex**
   - **Language**: English (US)
   - **Characteristics**: Advanced high-quality male voice with natural breathing sounds and intonation. Requires local download via macOS Settings in some versions.
   - **Usage**: `--voice Alex --rate 170`

4. **Sandy (English (US))**
   - **Language**: English (US)
   - **Characteristics**: Modern female voice with conversational intonation.
   - **Usage**: `--voice "Sandy (English (US))" --rate 170`

5. **Reed (English (US))**
   - **Language**: English (US)
   - **Characteristics**: Modern male voice with clear tone.
   - **Usage**: `--voice "Reed (English (US))" --rate 170`

## Optimization Guidelines
* **Speech Rate**: Standard macOS `say` reads at roughly 185–200 WPM, which sounds rushed and robotic. Slowing the rate down to **165–175 WPM** significantly increases comprehension and makes the voice sound smoother and less mechanical.
* **Overrides**: To run the pipeline with an alternate voice or rate:
  ```bash
  uv run python submission/video/generate_all.py --voice Daniel --rate 165
  ```
