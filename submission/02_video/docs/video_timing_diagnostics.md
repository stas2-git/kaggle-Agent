# Video Timing Diagnostics

This document records the measured durations of the narration audio and the generated video in the initial draft.

## Initial Measurements
- **Narration Audio Duration**: 208.96 seconds (03:28.96)
- **Generated Video Duration**: 270.04 seconds (04:30.04)
- **Timing Mismatch**: 61.08 seconds (Video runs 61.08 seconds longer than narration)

## Cause of Mismatch
1. **Fixed Slide Timings**: The visual slides were mapped to static durations in `concat_list.txt` (totaling 300 seconds), which did not correspond to the actual time taken by the macOS text-to-speech engine to read each slide's narration.
2. **FFmpeg Concat/Shortest Quirk**: When combining very low frame-rate static images with a audio track, FFmpeg's `-shortest` flag does not truncate the video correctly at the end of the audio, causing the last slide to display silently for the remaining duration.
