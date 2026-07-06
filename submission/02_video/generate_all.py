import os
import sys
import re
import argparse
import subprocess
import yaml
import shutil
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Add current dir to path to import generate_video
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import generate_video

# Paths - organized by content type, not by pipeline role. See README.md.
VIDEO_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(VIDEO_DIR))
PROJECT_BUILD_DIR = os.path.join(WORKSPACE_ROOT, "project_build")
SLIDES_DIR = os.path.join(VIDEO_DIR, "slides", "rendered")
NARRATIVE_DIR = os.path.join(VIDEO_DIR, "narrative")
AUDIO_DIR = os.path.join(VIDEO_DIR, "audio")
EVIDENCE_DIR = os.path.join(VIDEO_DIR, "evidence")
OUTPUTS_DIR = os.path.join(EVIDENCE_DIR, "demo_outputs")
CARDS_DIR = os.path.join(EVIDENCE_DIR, "demo_cards")
TEMP_SEGMENTS_DIR = os.path.join(VIDEO_DIR, ".tmp", "temp_segments")

def create_directories():
    print("Creating required directories...")
    os.makedirs(SLIDES_DIR, exist_ok=True)
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    os.makedirs(CARDS_DIR, exist_ok=True)
    # Recreate clean temp segments dir
    if os.path.exists(TEMP_SEGMENTS_DIR):
        shutil.rmtree(TEMP_SEGMENTS_DIR)
    os.makedirs(TEMP_SEGMENTS_DIR, exist_ok=True)

def run_command(cmd, env_updates=None):
    env = os.environ.copy()
    if env_updates:
        env.update(env_updates)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env, cwd=PROJECT_BUILD_DIR)
    return res.stdout, res.stderr, res.returncode

def load_mono_font(size):
    font_paths = [
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "/System/Library/Fonts/Supplemental/Courier.dfont",
        "/System/Library/Fonts/Supplemental/Menlo.ttc",
        "/System/Library/Fonts/Monaco.dfont",
        "/Library/Fonts/Courier New.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()

def draw_log_card(title, text_lines, output_path, border_color=(59, 130, 246)):
    # 1920x1080 canvas (Sleek dark-mode slate)
    img = Image.new("RGB", (1920, 1080), color=(18, 24, 38))
    draw = ImageDraw.Draw(img)
    
    # Accent top border
    draw.rectangle([(0, 0), (1920, 15)], fill=border_color)
    
    # Title
    font_title = generate_video.load_system_font(48)
    draw.text((100, 80), title, fill=(255, 255, 255), font=font_title)
    
    # Divider line
    draw.line([(100, 155), (1820, 155)], fill=(100, 110, 120), width=2)
    
    # Monospace body
    font_body = load_mono_font(22)
    y = 200
    for line in text_lines:
        line = line.rstrip()
        # Truncate lines that are too long
        if len(line) > 115:
            line = line[:112] + "..."
        draw.text((100, y), line, fill=(210, 220, 230), font=font_body)
        y += 34
        if y > 950:
            break
            
    # Actuarial footer
    font_footer = generate_video.load_system_font(20)
    footer_text = "Actuarial Portfolio Monitoring Agent - Capstone Video Draft (Synthetic Data Only)"
    draw.text((100, 1010), footer_text, fill=(100, 110, 120), font=font_footer)
    
    img.save(output_path)
    print(f"Generated log card at: {output_path}")

def run_verification_commands():
    results = {}
    
    # 1. pytest run
    print("\nRunning pytest suite...")
    pytest_stdout, pytest_stderr, pytest_rc = run_command("uv run pytest")
    pytest_log_path = os.path.join(OUTPUTS_DIR, "pytest_output.txt")
    with open(pytest_log_path, "w", encoding="utf-8") as f:
        f.write(pytest_stdout + "\n" + pytest_stderr)
    print(f"Pytest output saved to: {pytest_log_path}")
    results["pytest_passed"] = (pytest_rc == 0)
    
    # Prepare Pytest Card Lines (take headers and last summary)
    pytest_lines = pytest_stdout.splitlines()
    pytest_card_lines = []
    if len(pytest_lines) > 20:
        pytest_card_lines.extend(pytest_lines[:6])
        pytest_card_lines.append("... [test cases running] ...")
        pytest_card_lines.extend(pytest_lines[-10:])
    else:
        pytest_card_lines = pytest_lines
    
    draw_log_card(
        "Pytest Automated Verification Suite",
        pytest_card_lines,
        os.path.join(CARDS_DIR, "pytest_card.png"),
        border_color=(16, 185, 129) # green
    )
    
    # 2. Offline evaluations run
    print("\nRunning offline evaluations...")
    eval_stdout, eval_stderr, eval_rc = run_command("FORCE_OFFLINE=1 uv run python3 -m tests.eval.run_eval")
    eval_log_path = os.path.join(OUTPUTS_DIR, "eval_output.txt")
    with open(eval_log_path, "w", encoding="utf-8") as f:
        f.write(eval_stdout + "\n" + eval_stderr)
    print(f"Eval scorecard output saved to: {eval_log_path}")
    results["eval_passed"] = (eval_rc == 0)
    
    # Extract scorecard block from stdout
    eval_lines = eval_stdout.splitlines()
    scorecard_started = False
    scorecard_lines = []
    for line in eval_lines:
        if "EVALUATION SCORECARD SUMMARY" in line:
            scorecard_started = True
        if scorecard_started:
            scorecard_lines.append(line)
            
    if not scorecard_lines:
        scorecard_lines = eval_lines[-20:]
        
    # Remove ANSI escape codes
    clean_scorecard_lines = [re.sub(r'\x1b\[[0-9;]*m', '', line) for line in scorecard_lines]
    
    draw_log_card(
        "Offline Evaluation Scorecard Results",
        clean_scorecard_lines,
        os.path.join(CARDS_DIR, "eval_card.png"),
        border_color=(139, 92, 246) # purple
    )

    # 3. Vertical slice run
    print("\nRunning vertical-slice orchestrator...")
    run_stdout, run_stderr, run_rc = run_command("uv run python3 -m portfolio_agent.run --input \"tests/golden/loss_ratio_spike.csv\" --latest-month \"2026-06\"")
    run_log_path = os.path.join(OUTPUTS_DIR, "run_output.txt")
    with open(run_log_path, "w", encoding="utf-8") as f:
        f.write(run_stdout + "\n" + run_stderr)
    print(f"Vertical slice run output saved to: {run_log_path}")
    results["run_passed"] = (run_rc == 0)
    
    # Prepare Run Card Lines
    run_lines = run_stdout.splitlines()
    run_card_lines = []
    # Filter log prints for key events and output block
    summary_block_started = False
    for line in run_lines:
        if "Run complete." in line or "===" in line:
            summary_block_started = True
        if summary_block_started or any(term in line for term in ["Starting Portfolio", "Loading data", "Validating", "Calculating", "Running anomaly", "Calling Gemini"]):
            run_card_lines.append(line)
            
    draw_log_card(
        "Live Demo: Underwriting Review Pipeline",
        run_card_lines,
        os.path.join(CARDS_DIR, "run_card.png"),
        border_color=(245, 158, 11) # amber
    )
    
    # Parse report file and trace paths
    report_match = re.search(r"Report:\s*(outputs/reports/portfolio_review_\S+\.md)", run_stdout)
    trace_match = re.search(r"Trace:\s*(outputs/traces/run_trace_\S+\.json)", run_stdout)
    
    # 4. Generate report excerpt card
    if report_match:
        actual_path = os.path.join(PROJECT_BUILD_DIR, report_match.group(1).strip())
        if not os.path.exists(actual_path):
            normalized_rel = report_match.group(1).strip().replace("/", os.sep)
            actual_path = os.path.join(PROJECT_BUILD_DIR, normalized_rel)
            
        print(f"Reading generated report: {actual_path}")
        try:
            with open(actual_path, "r", encoding="utf-8") as f:
                report_content = f.read()
            report_lines = report_content.splitlines()
            draw_log_card(
                "Compiled Actuarial Memo Excerpt",
                report_lines[:25],
                os.path.join(CARDS_DIR, "report_card.png"),
                border_color=(16, 185, 129)
            )
            results["report_path"] = actual_path
        except Exception as e:
            print(f"Failed to read report: {e}")
            draw_log_card(
                "Compiled Actuarial Memo Excerpt",
                ["[Error loading report file: " + str(e) + "]"],
                os.path.join(CARDS_DIR, "report_card.png")
            )
    else:
        print("Warning: Could not parse report path from run output.")
        draw_log_card(
            "Compiled Actuarial Memo Excerpt",
            ["[Report generation output not found in log]"],
            os.path.join(CARDS_DIR, "report_card.png")
        )

    # 5. Generate trace excerpt card
    if trace_match:
        trace_path = os.path.join(PROJECT_BUILD_DIR, trace_match.group(1).strip())
        print(f"Reading generated trace JSON: {trace_path}")
        try:
            with open(trace_path, "r", encoding="utf-8") as f:
                trace_content = f.read()
            trace_lines = trace_content.splitlines()
            draw_log_card(
                "Structured Observability Trace JSON",
                trace_lines[:25],
                os.path.join(CARDS_DIR, "trace_card.png"),
                border_color=(59, 130, 246)
            )
            results["trace_path"] = trace_path
        except Exception as e:
            print(f"Failed to read trace file: {e}")
            draw_log_card(
                "Structured Observability Trace JSON",
                ["[Error loading trace file: " + str(e) + "]"],
                os.path.join(CARDS_DIR, "trace_card.png")
            )
    else:
        print("Warning: Could not parse trace path from run output.")
        draw_log_card(
            "Structured Observability Trace JSON",
            ["[Trace JSON output not found in log]"],
            os.path.join(CARDS_DIR, "trace_card.png")
        )
        
    return results

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

def generate_segment_audios(segments, voice_name, speech_rate):
    print(f"\nGenerating segment-level voiceovers using macOS 'say' (Voice: {voice_name}, Rate: {speech_rate} WPM)...")
    durations = []
    
    for idx, seg in enumerate(segments, 1):
        text = seg["narration_text"]
        text_path = os.path.join(TEMP_SEGMENTS_DIR, f"seg_{idx}.txt")
        aiff_path = os.path.join(TEMP_SEGMENTS_DIR, f"seg_{idx}.aiff")
        mp3_path = os.path.join(TEMP_SEGMENTS_DIR, f"seg_{idx}.mp3")
        
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(text)
            
        cmd = f"say -v '{voice_name}' -r {speech_rate} -f '{text_path}' -o '{aiff_path}'"
        stdout, stderr, rc = run_command(cmd)
        if rc != 0:
            print(f"Error: say failed for segment {idx}: {stderr}")
            sys.exit(1)
            
        # Convert to MP3
        conv_cmd = f"ffmpeg -y -i '{aiff_path}' -codec:a libmp3lame -qscale:a 2 '{mp3_path}'"
        c_stdout, c_stderr, c_rc = run_command(conv_cmd)
        if c_rc != 0:
            print(f"Error: ffmpeg audio conversion failed for segment {idx}: {c_stderr}")
            sys.exit(1)
            
        dur = get_format_duration(mp3_path)
        print(f"Segment {idx} Audio Duration: {dur:.2f} seconds")
        durations.append(dur)
        
    return durations

def build_segment_videos(segments, durations, override_mode=False, override_ratio=1.0):
    print("\nRendering individual segment video clips...")
    segment_video_paths = []
    buffer = 0.30  # seconds padding for local tts pauses
    
    for idx, seg in enumerate(segments, 1):
        image_relative = seg["visual"]
        image_path = os.path.join(VIDEO_DIR, image_relative)
        audio_path = os.path.join(TEMP_SEGMENTS_DIR, f"seg_{idx}.mp3")
        video_path = os.path.join(TEMP_SEGMENTS_DIR, f"video_{idx}.mp4")
        
        if not os.path.exists(image_path):
            # Try workspace root fallback
            image_path = os.path.join(WORKSPACE_ROOT, image_relative)
            
        if override_mode:
            # Scaled silent video
            target_duration = durations[idx - 1] * override_ratio
            cmd = f"ffmpeg -y -loop 1 -r 25 -i '{image_path}' -c:v libx264 -pix_fmt yuv420p -t {target_duration:.3f} '{video_path}'"
        else:
            # Voiced video with apad + shortest to sync streams exactly
            target_duration = durations[idx - 1] + buffer
            cmd = f"ffmpeg -y -loop 1 -r 25 -i '{image_path}' -i '{audio_path}' -filter_complex \"[1:a]apad[a]\" -map 0:v -map \"[a]\" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest -t {target_duration:.3f} '{video_path}'"
            
        stdout, stderr, rc = run_command(cmd)
        if rc != 0:
            print(f"Error rendering segment {idx}: {stderr}")
            sys.exit(1)
            
        segment_video_paths.append(video_path)
        
    return segment_video_paths

def concatenate_videos(video_paths, output_path):
    concat_list_path = os.path.join(TEMP_SEGMENTS_DIR, "concat_segments.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for path in video_paths:
            f.write(f"file '{path}'\n")
            
    print(f"\nConcatenating {len(video_paths)} segment clips into {output_path}...")
    cmd = f"ffmpeg -y -f concat -safe 0 -i '{concat_list_path}' -c copy '{output_path}'"
    stdout, stderr, rc = run_command(cmd)
    if rc != 0:
        print(f"Error during concatenation: {stderr}")
        sys.exit(1)

def run_security_scan():
    print("\nRunning safety security scan on generated assets...")
    found_issues = []
    
    # Files to scan (only generated assets and captions)
    scan_paths = [
        os.path.join(VIDEO_DIR, "captions.srt"),
    ]
    # Also scan captured command outputs
    if os.path.exists(OUTPUTS_DIR):
        for entry in os.listdir(OUTPUTS_DIR):
            scan_paths.append(os.path.join(OUTPUTS_DIR, entry))
            
    for file_path in scan_paths:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            try:
                # Read file content
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Check for standard Google API Key pattern (masking value)
                aiza_match = re.search(r"AIzaSy[A-Za-z0-9_-]{35}", content)
                if aiza_match:
                    found_issues.append(f"{os.path.basename(file_path)}: Hardcoded Google AI API key: [MASKED]")
                
                # Check for explicit assignment of sensitive variables (masking value)
                sensitive_assign = re.search(r"(GEMINI_API_KEY|GOOGLE_API_KEY|password|secret|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]", content, re.IGNORECASE)
                if sensitive_assign:
                    found_issues.append(f"{os.path.basename(file_path)}: Exposed sensitive value assignment: [MASKED]")
                
                # Check for raw printed env contents (masking value)
                for line_idx, line in enumerate(content.splitlines(), 1):
                    if re.match(r"^[A-Z0-9_]+=[^\s]+", line) and not any(term in line for term in ["GOOGLE_API_KEY", "GEMINI_API_KEY", "PATH="]):
                        found_issues.append(f"{os.path.basename(file_path)}:L{line_idx} - Potential raw environment variable dump: [MASKED]")
                        
            except Exception as e:
                print(f"Skipping scan for {os.path.basename(file_path)}: {e}")
                
    if found_issues:
        print("\n" + "!" * 60)
        print("SECURITY AUDIT ALERT: Potential secret leak detected!")
        for issue in found_issues:
            print(f"  * {issue}")
        print("!" * 60 + "\n")
        return False, found_issues
    else:
        print("Security audit passed. No credentials, secret keys, or raw env leaks detected in generated assets.")
        return True, []

def write_generation_report(results, audio_source, model_used, voice_name, speech_rate, voiceover_generated, video_generated, scan_passed, scan_issues, final_video_path):
    report_path = os.path.join(EVIDENCE_DIR, "video_generation_report.md")
    
    status_emoji = "✅" if (results.get("pytest_passed") and results.get("eval_passed") and video_generated and scan_passed) else "❌"
    
    content = f"""# Video Generation Execution Report {status_emoji}

This report summaries the execution and outcomes of the audio-driven video generation pipeline.

## 1. Pipeline Execution Status
- **Pytest Suite**: {"PASS ✅" if results.get("pytest_passed") else "FAIL ❌"}
- **Offline Evaluations**: {"PASS ✅" if results.get("eval_passed") else "FAIL ❌"}
- **Vertical-Slice Review Run**: {"PASS ✅" if results.get("run_passed") else "FAIL ❌"}
- **Voiceover TTS Source**: `{audio_source}`
- **Model Used**: `{model_used}`
- **Voice / Config Name**: `{voice_name}`
- **Speech Rate (macOS Say only)**: `{speech_rate} WPM`
- **Final Video Assembler**: {"PASS ✅" if video_generated else "FAIL ❌"}
- **Security Secret Audit Scan**: {"PASS ✅" if scan_passed else "FAIL ❌"}

## 2. Timing Measurements & Bounds Checks
- **Narration Audio Duration**: {results.get("narration_duration"):.3f} seconds
- **Final Video Duration**: {results.get("video_duration"):.3f} seconds
- **Absolute Duration Difference**: {results.get("duration_diff"):.3f} seconds
- **Duration Boundary Status**: {"PASS (Within 1.0s limit) ✅" if results.get("duration_bounds_pass") else "FAIL (Exceeds 1.0s difference) ❌"}
- **Video Output Path**: `{final_video_path}`

## 3. Generated Outputs
- **Auditable Command Logs** (saved in `submission/02_video/evidence/demo_outputs/`):
  - Pytest Log: `pytest_output.txt`
  - Scorecard Log: `eval_output.txt`
  - Review Run Log: `run_output.txt`
- **Rendered Demo Cards** (saved in `submission/02_video/evidence/demo_cards/`):
  - `pytest_card.png`
  - `eval_card.png`
  - `run_card.png`
  - `report_card.png`
  - `trace_card.png`

## 4. Security Audit Findings
"""
    if scan_passed:
        content += "- **Result**: SUCCESS. No raw API keys, AIza key signatures, or un-scrubbed `.env` references were found.\n"
    else:
        content += "- **Result**: WARNING/FAIL. The following potential issues were found:\n"
        for issue in scan_issues:
            content += f"  - {issue}\n"
            
    content += """
## 5. Verification Commands
Confirm outputs locally using:
- Pytest passing verification: `uv run pytest`
- Check generated trace exists: `cd project_build && ls outputs/traces/`
- View generated reports: `cd project_build && ls outputs/reports/`
"""
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated final run summary report at: {report_path}")

def main():
    parser = argparse.ArgumentParser(description="Audio-Driven Video Automation Pipeline")
    parser.add_argument("--voice", default="Samantha", help="Voice override for macOS 'say' (default: Samantha)")
    parser.add_argument("--rate", type=int, default=170, help="Speech rate override in WPM (default: 170)")
    parser.add_argument("--audio-source", default="auto", choices=["auto", "xtts", "chattts", "gemini", "say"], help="Explicitly select audio segments source to use (default: auto)")
    args = parser.parse_args()
    
    create_directories()
    
    # 1. Draw all standard slides
    print("Drawing standard conceptual slide images...")
    for i, slide in enumerate(generate_video.SLIDES_DATA, 1):
        slide_path = os.path.join(SLIDES_DIR, f"slide{i}.png")
        generate_video.draw_slide(slide["title"], slide["bullets"], slide_path)
        
    # 2. Run verification suite commands & render card overlays
    results = run_verification_commands()
    
    # 3. Read narration segments from YAML
    yaml_path = os.path.join(NARRATIVE_DIR, "slide_narration_segments.yaml")
    if not os.path.exists(yaml_path):
        print(f"Error: YAML segments config not found at: {yaml_path}")
        sys.exit(1)

    with open(yaml_path, "r", encoding="utf-8") as f:
        seg_data = yaml.safe_load(f)
    segments = seg_data["segments"]

    # 4. Load premium segment audios (Gemini or local ChatTTS) if available, otherwise fall back to local macOS say
    # Note: xtts/chattts segment dirs are intentionally only checked under AUDIO_DIR (the live
    # location), not archive/ - archived attempts are not auto-detected, by design.
    xtts_segments_dir = os.path.join(AUDIO_DIR, "xtts_segments")
    xtts_metadata_path = os.path.join(xtts_segments_dir, "metadata.json")

    gemini_segments_dir = os.path.join(AUDIO_DIR, "gemini_segments")
    gemini_metadata_path = os.path.join(gemini_segments_dir, "metadata.json")

    chattts_segments_dir = os.path.join(AUDIO_DIR, "chattts_segments")
    chattts_metadata_path = os.path.join(chattts_segments_dir, "metadata.json")
    
    use_xtts_segments = False
    xtts_durations = []
    
    if (args.audio_source in ["auto", "xtts"]) and os.path.exists(xtts_metadata_path):
        try:
            with open(xtts_metadata_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            # Verify all expected segment files exist in xtts_segments
            all_files_exist = True
            temp_durations = []
            for i in range(1, len(segments) + 1):
                mp3_name = f"seg_{i}.mp3"
                wav_name = f"seg_{i}.wav"
                mp3_path = os.path.join(xtts_segments_dir, mp3_name)
                wav_path = os.path.join(xtts_segments_dir, wav_name)
                
                if os.path.exists(mp3_path):
                    dur = get_format_duration(mp3_path)
                    temp_durations.append((mp3_path, dur))
                elif os.path.exists(wav_path):
                    dur = get_format_duration(wav_path)
                    temp_durations.append((wav_path, dur))
                else:
                    all_files_exist = False
                    break
            
            if all_files_exist:
                use_xtts_segments = True
                xtts_durations = temp_durations
                print("\nPremium local XTTS v2 voice-cloned segment files detected and verified.")
        except Exception as e:
            print(f"Warning: Could not parse XTTS metadata: {e}")

    use_chattts_segments = False
    chattts_durations = []
    
    if not use_xtts_segments and (args.audio_source in ["auto", "chattts"]) and os.path.exists(chattts_metadata_path):
        try:
            with open(chattts_metadata_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            # Verify all expected segment files exist in chattts_segments
            all_files_exist = True
            temp_durations = []
            for i in range(1, len(segments) + 1):
                mp3_name = f"seg_{i}.mp3"
                wav_name = f"seg_{i}.wav"
                mp3_path = os.path.join(chattts_segments_dir, mp3_name)
                wav_path = os.path.join(chattts_segments_dir, wav_name)
                
                if os.path.exists(mp3_path):
                    dur = get_format_duration(mp3_path)
                    temp_durations.append((mp3_path, dur))
                elif os.path.exists(wav_path):
                    dur = get_format_duration(wav_path)
                    temp_durations.append((wav_path, dur))
                else:
                    all_files_exist = False
                    break
            
            if all_files_exist:
                use_chattts_segments = True
                chattts_durations = temp_durations
                print("\nPremium local ChatTTS segment files detected and verified.")
        except Exception as e:
            print(f"Warning: Could not parse ChatTTS metadata: {e}")

    use_gemini_segments = False
    gemini_durations = []
    
    if not use_xtts_segments and not use_chattts_segments and (args.audio_source in ["auto", "gemini"]) and os.path.exists(gemini_metadata_path):
        try:
            with open(gemini_metadata_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            # Verify all expected segment files exist in gemini_segments
            all_files_exist = True
            temp_durations = []
            for i in range(1, len(segments) + 1):
                mp3_name = f"seg_{i}.mp3"
                wav_name = f"seg_{i}.wav"
                mp3_path = os.path.join(gemini_segments_dir, mp3_name)
                wav_path = os.path.join(gemini_segments_dir, wav_name)
                
                if os.path.exists(mp3_path):
                    dur = get_format_duration(mp3_path)
                    temp_durations.append((mp3_path, dur))
                elif os.path.exists(wav_path):
                    dur = get_format_duration(wav_path)
                    temp_durations.append((wav_path, dur))
                else:
                    all_files_exist = False
                    break
            
            if all_files_exist:
                use_gemini_segments = True
                gemini_durations = temp_durations
                print("\nPremium Gemini TTS segment files detected and verified.")
        except Exception as e:
            print(f"Warning: Could not parse Gemini metadata: {e}")

    segment_durations = []
    audio_source = "local macOS say"
    model_used = "N/A"
    voice_used = args.voice
    
    use_premium_segments = use_xtts_segments or use_chattts_segments or use_gemini_segments
    
    if use_premium_segments:
        print("\nCopying premium segment audios to temp directory...")
        if use_xtts_segments:
            source_durations = xtts_durations
        elif use_chattts_segments:
            source_durations = chattts_durations
        else:
            source_durations = gemini_durations
            
        for idx, (src_path, dur) in enumerate(source_durations, 1):
            dst_mp3_path = os.path.join(TEMP_SEGMENTS_DIR, f"seg_{idx}.mp3")
            if src_path.endswith(".wav"):
                # Convert WAV to MP3 using ffmpeg
                conv_cmd = f"ffmpeg -y -i '{src_path}' -codec:a libmp3lame -qscale:a 2 '{dst_mp3_path}'"
                stdout, stderr, rc = run_command(conv_cmd)
                if rc != 0:
                    print(f"Error converting WAV to MP3 for segment {idx}: {stderr}")
                    sys.exit(1)
            else:
                shutil.copy2(src_path, dst_mp3_path)
            segment_durations.append(dur)
            
        # Parse metadata details for report
        if use_xtts_segments:
            try:
                with open(xtts_metadata_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                audio_source = meta.get("source", "Local XTTS v2 Cloned Voice")
                model_used = meta.get("model", "XTTS v2 Core")
                voice_used = meta.get("voice", "Combined Reference Voice")
            except Exception:
                audio_source = "Local XTTS v2 Cloned Voice"
                model_used = "XTTS v2 Core"
                voice_used = "Combined Reference Voice"
        elif use_chattts_segments:
            try:
                with open(chattts_metadata_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                audio_source = meta.get("source", "Local ChatTTS")
                model_used = meta.get("model", "ChatTTS Core v0.2")
                voice_used = meta.get("voice", "Seed 888")
            except Exception:
                audio_source = "Local ChatTTS"
                model_used = "ChatTTS Core v0.2"
                voice_used = "Seed 888"
        else:
            try:
                with open(gemini_metadata_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                audio_source = meta.get("source", "Gemini API TTS (Segment-Based)")
                model_used = meta.get("model", "gemini-3.1-flash-tts-preview")
                voice_used = meta.get("voice", "Kore")
            except Exception:
                audio_source = "Gemini API TTS (Segment-Based)"
                model_used = "gemini-3.1-flash-tts-preview"
                voice_used = "Kore"
            
    else:
        # Fall back to macOS 'say'
        say_durations = generate_segment_audios(segments, args.voice, args.rate)
        segment_durations = say_durations

    total_audio_duration = sum(segment_durations)
    
    # Check for manual single-file override narration audio (MP3 has priority, then WAV)
    # This is only active if we are NOT using the premium segment files
    override_mp3 = os.path.join(AUDIO_DIR, "narration_override.mp3")
    override_wav = os.path.join(AUDIO_DIR, "narration_override.wav")
    
    override_path = None
    if not use_premium_segments:
        if os.path.exists(override_mp3):
            override_path = override_mp3
        elif os.path.exists(override_wav):
            override_path = override_wav
        
    override_mode = (override_path is not None)
    
    final_video_out = os.path.join(VIDEO_DIR, "draft_demo_video.mp4")
    
    if override_mode:
        # Single-file manual override mode
        override_metadata_path = os.path.join(AUDIO_DIR, "narration_override_metadata.json")
        if os.path.exists(override_metadata_path):
            try:
                with open(override_metadata_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                audio_source = meta.get("source", "Gemini API TTS")
                model_used = meta.get("model", "gemini-3.1-flash-tts-preview")
                voice_used = meta.get("voice", "Kore")
            except Exception:
                audio_source = "Manual Override File"
                model_used = "N/A"
                voice_used = "N/A"
        else:
            audio_source = "Manual Override File"
            model_used = "N/A"
            voice_used = "N/A"
            
        print(f"\nPremium override narration audio detected at: {override_path}")
        override_total_duration = get_format_duration(override_path)
        print(f"Override Audio Duration: {override_total_duration:.2f} seconds")
        
        ratio = override_total_duration / total_audio_duration
        print(f"Scaling segments by ratio: {ratio:.4f} to fit override timeline.")
        
        # Build silent segment videos scaled to override timeline
        seg_videos = build_segment_videos(segments, segment_durations, override_mode=True, override_ratio=ratio)
        
        # Concatenate silent segment videos
        silent_concat_path = os.path.join(TEMP_SEGMENTS_DIR, "silent_concat.mp4")
        concatenate_videos(seg_videos, silent_concat_path)
        
        # Merge silent video with override audio
        print(f"Merging silent video with override narration audio...")
        merge_cmd = f"ffmpeg -y -i '{silent_concat_path}' -i '{override_path}' -c:v copy -c:a aac -shortest '{final_video_out}'"
        m_stdout, m_stderr, m_rc = run_command(merge_cmd)
        if m_rc != 0:
            print(f"Error merging override audio: {m_stderr}")
            sys.exit(1)
            
        narration_duration = override_total_duration
        
    else:
        # Segment-based mode (Gemini, ChatTTS or macOS say segments)
        if use_premium_segments:
            print(f"\nUsing premium segment-based narration mode ({audio_source})...")
        else:
            print("\nUsing standard macOS 'say' narration mode...")
            
        # Concatenate segment audios into narration.mp3 for fallback/reference
        seg_audios_list = [os.path.join(TEMP_SEGMENTS_DIR, f"seg_{i}.mp3") for i in range(1, len(segments) + 1)]
        
        # Write list of audios for concatenation
        audio_concat_list = os.path.join(TEMP_SEGMENTS_DIR, "audio_concat.txt")
        with open(audio_concat_list, "w", encoding="utf-8") as f:
            for path in seg_audios_list:
                f.write(f"file '{path}'\n")
                
        narration_mp3_path = os.path.join(AUDIO_DIR, "narration.mp3")
        print("Stitching segment audios together...")
        stitch_cmd = f"ffmpeg -y -f concat -safe 0 -i '{audio_concat_list}' -c copy '{narration_mp3_path}'"
        s_stdout, s_stderr, s_rc = run_command(stitch_cmd)
        if s_rc != 0:
            print(f"Warning: failed to stitch audio file narration.mp3: {s_stderr}")
            
        # Build voiced segment videos containing audio + padding
        seg_videos = build_segment_videos(segments, segment_durations, override_mode=False)
        
        # Concatenate voiced segment videos into the final video
        concatenate_videos(seg_videos, final_video_out)
        
    # 5. Retrieve final output stream durations
    final_video_duration = get_stream_duration(final_video_out, "v:0")
    final_audio_duration = get_stream_duration(final_video_out, "a:0")
    
    if not override_mode:
        narration_duration = final_audio_duration
        
    # Verify both streams exist
    if final_video_duration == 0.0:
        print("Error: Could not determine video stream duration of generated video.")
        sys.exit(1)
        
    print(f"\nFinal Video Track Duration: {final_video_duration:.3f} seconds")
    print(f"Final Audio Track Duration: {final_audio_duration:.3f} seconds")
    
    # Record diagnostics metrics
    results["video_duration"] = final_video_duration
    results["narration_duration"] = narration_duration
    duration_diff = abs(final_video_duration - narration_duration)
    results["duration_diff"] = duration_diff
    
    # strict validation constraint: difference must be less than 1.0s
    bounds_passed = (duration_diff <= 1.0)
    results["duration_bounds_pass"] = bounds_passed
    
    if not bounds_passed:
        print(f"\nERROR: Video duration ({final_video_duration:.3f}s) and narration duration ({narration_duration:.3f}s) differ by {duration_diff:.3f}s, which exceeds the 1.0 second limit!")
        sys.exit(1)
    else:
        print("Validation Success: Video and audio track alignment is within 1.0 second boundary.")
        
    # 6. Safety secret scan
    scan_passed, scan_issues = run_security_scan()
    
    # 7. Clean up temp segment directories
    print("Cleaning up temporary scratch files...")
    if os.path.exists(TEMP_SEGMENTS_DIR):
        shutil.rmtree(TEMP_SEGMENTS_DIR)
        
    # Write report
    write_generation_report(
        results=results,
        audio_source=audio_source,
        model_used=model_used,
        voice_name=voice_used,
        speech_rate=args.rate,
        voiceover_generated=True,
        video_generated=True,
        scan_passed=scan_passed,
        scan_issues=scan_issues,
        final_video_path=final_video_out
    )
    
    if not (results.get("pytest_passed") and results.get("eval_passed") and scan_passed):
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
