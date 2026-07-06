"""Shared loader for the stable slide story contract.

The story file owns durable meaning and audio-safe narration. Volatile evidence such as
test counts, run IDs, and anomaly measurements stays in build-time evidence files and can
appear on slides without forcing a TTS re-record.
"""

import os
import sys
import yaml

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from common import STORY_DIR

STORY_PATH = os.path.join(STORY_DIR, "slide_story.yaml")


def load_story_segments():
    if not os.path.exists(STORY_PATH):
        raise FileNotFoundError(f"Story contract not found at: {STORY_PATH}")

    with open(STORY_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    segments = data.get("segments", [])
    if not segments:
        raise ValueError(f"Story contract has no segments: {STORY_PATH}")

    for expected, segment in enumerate(segments, 1):
        slide_number = segment.get("slide_number")
        if slide_number != expected:
            raise ValueError(f"Expected slide_number {expected}, got {slide_number!r}")
        for key in ("title", "visual", "takeaway", "audio_script"):
            if not segment.get(key):
                raise ValueError(f"Segment {expected} is missing required story key: {key}")

    return segments


def build_narration_segments():
    """Return the legacy narration shape consumed by audio/video assembly."""
    return [
        {
            "slide_number": segment["slide_number"],
            "title": segment["title"],
            "visual": segment["visual"],
            "narration_text": segment["audio_script"],
        }
        for segment in load_story_segments()
    ]


def get_static_slide_data():
    """Return hand-authored slide fields for non-evidence slides."""
    static = []
    for segment in load_story_segments():
        if segment.get("slide_type") != "static":
            continue
        static.append(
            {
                "segment_number": segment["slide_number"],
                "title": segment["title"],
                "hook": segment["hook"],
                "bullets": segment["cards"],
                "cue": segment["takeaway"],
            }
        )
    return static


def get_story_by_slide_number():
    return {segment["slide_number"]: segment for segment in load_story_segments()}
