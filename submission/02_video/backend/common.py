"""Shared path constants and small helpers used by every pipeline stage
(build_slides.py, audio_generation/*.py, assemble_video.py). Kept in one place so a path
definition or the workspace-path redaction logic can't silently drift between stages."""

import os
import subprocess

# Paths - organized by frontend (content the user reviews/signs off on) vs backend (the
# machinery that produces it). See README.md. This module lives in backend/, one level under
# VIDEO_DIR.
VIDEO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(VIDEO_DIR, "backend")
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(VIDEO_DIR))
PROJECT_BUILD_DIR = os.path.join(WORKSPACE_ROOT, "project_build")
SLIDES_DIR = os.path.join(VIDEO_DIR, "slides", "rendered")
STORY_DIR = os.path.join(VIDEO_DIR, "story")
# Kept for older imports; narrative now lives inside STORY_DIR as narration_segments.yaml.
NARRATIVE_DIR = STORY_DIR
AUDIO_ROOT_DIR = os.path.join(STORY_DIR, "audio")
# Canonical narration files live under story/ with the story contract they voice.
# Keeping AUDIO_DIR as "current" preserves the existing call sites' meaning:
# seg_N.mp3 under the current audio folder is always the canonical version.
AUDIO_DIR = os.path.join(AUDIO_ROOT_DIR, "current")
AUDIO_VERSIONS_DIR = os.path.join(AUDIO_ROOT_DIR, "versions")
SAY_PREVIEW_DIR = os.path.join(AUDIO_ROOT_DIR, "previews", "say")
EVIDENCE_DIR = os.path.join(BACKEND_DIR, "evidence")
OUTPUTS_DIR = os.path.join(EVIDENCE_DIR, "demo_outputs")
CARDS_DIR = os.path.join(EVIDENCE_DIR, "demo_cards")
VERIFICATION_RESULTS_PATH = os.path.join(EVIDENCE_DIR, "verification_results.json")
TEMP_SEGMENTS_DIR = os.path.join(BACKEND_DIR, ".tmp", "temp_segments")

def redact_workspace_paths(text):
    """Strip the absolute workspace path (which embeds the user's email via the Google Drive
    sync folder name, e.g. GoogleDrive-name@gmail.com) out of anything captured from real
    command stdout/stderr before it can land in a log file or a rendered slide/card. Raw
    process output naturally includes cwd-relative absolute paths - without this, any card
    showing a real file path leaks local PII into the shipped video.
    """
    if not text:
        return text
    return text.replace(WORKSPACE_ROOT, "<workspace>")

def run_command(cmd, env_updates=None):
    env = os.environ.copy()
    if env_updates:
        env.update(env_updates)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env, cwd=PROJECT_BUILD_DIR)
    return res.stdout, res.stderr, res.returncode

def get_format_duration(file_path):
    cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 '{file_path}'"
    stdout, stderr, rc = run_command(cmd)
    if rc == 0:
        try:
            return float(stdout.strip())
        except ValueError:
            pass
    return 0.0

def get_stream_duration(file_path, stream_type):
    cmd = f"ffprobe -v error -select_streams {stream_type} -show_entries stream=duration -of default=noprint_wrappers=1:nokey=1 '{file_path}'"
    stdout, stderr, rc = run_command(cmd)
    if rc == 0:
        try:
            val = stdout.strip()
            if val:
                return float(val)
        except ValueError:
            pass
    return get_format_duration(file_path)

def ensure_persistent_dirs():
    """Create the durable (non-scratch) directories every stage may write into. Each stage
    owns the lifecycle of its own temp/scratch dir separately (create clean, use, delete)."""
    os.makedirs(SLIDES_DIR, exist_ok=True)
    os.makedirs(STORY_DIR, exist_ok=True)
    os.makedirs(AUDIO_ROOT_DIR, exist_ok=True)
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(AUDIO_VERSIONS_DIR, exist_ok=True)
    os.makedirs(SAY_PREVIEW_DIR, exist_ok=True)
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    os.makedirs(CARDS_DIR, exist_ok=True)
