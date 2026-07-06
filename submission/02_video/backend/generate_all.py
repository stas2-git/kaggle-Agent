"""Convenience wrapper: runs the full pipeline in one shot (build_slides.py, then
assemble_video.py), for quick full-regeneration - e.g. `--audio-source say` iteration.

For the review-then-sign-off workflow this project is built around, prefer running the
stages separately instead:
  1. build_slides.py          - regenerate slides/rendered/slide_1.png ... slide_7.png
  2. audio_generation/*.py    - regenerate story/audio/current/ (Gemini) or
                                story/audio/previews/say/ (say)
  3. assemble_video.py        - combine whatever's currently on disk into the final video

Running them separately lets you review each spec folder before it's baked into
final_demo_video.mp4. This wrapper skips that pause by design - use it for fast iteration,
not for producing a final deliverable you haven't looked at yet.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import build_slides
import assemble_video

def main():
    build_slides.main()
    assemble_video.main()

if __name__ == "__main__":
    main()
