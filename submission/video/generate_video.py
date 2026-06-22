import os
import sys
import argparse
import subprocess
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
SLIDES_DIR = os.path.join(ASSETS_DIR, "slides")

SLIDES_DATA = [
    {
        "title": "Actuarial Portfolio Monitoring Agent",
        "bullets": [
            "Triage monitoring for monthly insurance books of business.",
            "Automates data ingestion, metrics calculation, and trend analysis.",
            "Bounded tool-first design separates math from narrative reasoning.",
            "Speeds up routine reviews while preserving complete audit trails."
        ],
        "duration": 30
    },
    {
        "title": "Why an Agent? Beyond Dashboards",
        "bullets": [
            "Coordinates multi-step validation and investigation logic.",
            "Applies dynamic triggers for human-in-the-loop review.",
            "Protects sensitive records from prompt-injection threats.",
            "Generates professional draft summaries to prepare human experts."
        ],
        "duration": 30
    },
    {
        "title": "Bounded Five-Layer System Design",
        "bullets": [
            "Data Layer: Ingests aggregate deidentified aggregates CSVs.",
            "Security Layer: Validates paths and blocks prompt injection.",
            "Tool Layer: Deterministic Pandas computations for metrics & drivers.",
            "Agent Layer: Schema-bound Gemini reasoning for findings synthesis.",
            "Output Layer: Compiled Markdown reports & observability JSON traces."
        ],
        "duration": 45
    },
    {
        "title": "Interactive Live Demo (Planted NY Spike)",
        "bullets": [
            "Run Pipeline: Ingests CSV data and checks dates/schemas.",
            "Anomaly Detection: Loss ratio flagged high severity (rose to 85%).",
            "Driver Investigation: NY state / policy year 2025 isolated as driver.",
            "Outputs Generated: Formatted review memo and structured JSON trace."
        ],
        "duration": 120
    },
    {
        "title": "Rigorous Safety & Verification",
        "bullets": [
            "Path Allowlist: Traps traversal attacks (e.g. reading .env secrets).",
            "Injection Shields: Blocks instruction overrides inside note fields.",
            "Golden Scenarios: Computes metrics & drivers against YAML expectations.",
            "Local Evaluations: 11 test cases validating logic and containment."
        ],
        "duration": 45
    },
    {
        "title": "Real Business Impact & Future Roadmap",
        "bullets": [
            "Reduces routine actuarial reporting overhead from hours to seconds.",
            "Guarantees numerical reproducibility with strict math stubs.",
            "Disclaimer: Ingestion data is synthetic; report is a triage aid.",
            "Future Work: BigQuery queries, GKE container runs, and automated alerts."
        ],
        "duration": 30
    }
]

def load_system_font(size):
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Courier New.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()

def draw_slide(title, bullets, output_path):
    # 1920x1080 Canvas (Sleek dark-mode)
    img = Image.new("RGB", (1920, 1080), color=(18, 24, 38))
    draw = ImageDraw.Draw(img)
    
    # Accent green line
    draw.line([(100, 160), (1820, 160)], fill=(0, 220, 130), width=5)
    
    # Title Text
    font_title = load_system_font(55)
    draw.text((100, 75), title, fill=(255, 255, 255), font=font_title)
    
    # Bullets
    font_body = load_system_font(38)
    y = 240
    for bullet in bullets:
        draw.text((140, y), "•", fill=(0, 220, 130), font=font_body)
        draw.text((180, y), bullet, fill=(200, 210, 220), font=font_body)
        y += 85
        
    # Actuarial footer disclaimer
    font_footer = load_system_font(20)
    footer_text = "Actuarial Portfolio Monitoring Agent - Capstone Video Draft (Synthetic Data Only)"
    draw.text((100, 1010), footer_text, fill=(100, 110, 120), font=font_footer)
    
    img.save(output_path)
    print(f"Generated slide image at: {output_path}")

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

def build_video(slides_list=None, dry_run=False):
    # Create output directories
    os.makedirs(SLIDES_DIR, exist_ok=True)
    
    # 1. Generate Slide Images
    if slides_list is None:
        slides_list = []
        for i, slide in enumerate(SLIDES_DATA, 1):
            slide_filename = f"slide{i}.png"
            slide_path = os.path.join(SLIDES_DIR, slide_filename)
            draw_slide(slide["title"], slide["bullets"], slide_path)
            slides_list.append((slide_path, slide["duration"]))
        
    if dry_run:
        print("\n[Dry Run] Slides generated. Video compilation skipped.")
        return 0
        
    # Check ffmpeg installation
    ffmpeg_available = check_ffmpeg()
    if not ffmpeg_available:
        print("\n" + "="*60)
        # Match capitalization in instruction: 'brew install ffmpeg'
        print("Warning: ffmpeg is missing from your system PATH.")
        print("To generate the video, please install ffmpeg via homebrew:")
        print("    brew install ffmpeg")
        print("="*60 + "\n")
        return 1
        
    # 2. Write Concat demuxer file
    concat_file_path = os.path.join(ASSETS_DIR, "concat_list.txt")
    with open(concat_file_path, "w") as f:
        for slide_path, duration in slides_list:
            # Escape path single quotes
            escaped_path = slide_path.replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")
            f.write(f"duration {duration}\n")
        if slides_list:
            f.write("file '{}'\n".format(slides_list[-1][0].replace("'", "'\\''")))
            
    print(f"Wrote concat instructions to: {concat_file_path}")
    
    # 3. Resolve Audio
    audio_path = os.path.join(ASSETS_DIR, "narration.mp3")
    audio_exists = os.path.exists(audio_path)
    if not audio_exists:
        # Check for aiff
        aiff_path = os.path.join(ASSETS_DIR, "narration.aiff")
        if os.path.exists(aiff_path):
            audio_path = aiff_path
            audio_exists = True
            
    video_out = os.path.join(SCRIPT_DIR, "draft_demo_video.mp4")
    
    # 4. Construct ffmpeg command
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file_path]
    
    if audio_exists:
        print(f"Found narration audio track at: {audio_path}. Merging audio...")
        cmd.extend(["-i", audio_path])
        # Join audio and loop slides to fit, stopping when audio ends
        cmd.extend(["-pix_fmt", "yuv420p", "-shortest", video_out])
    else:
        print("Narration audio file not found. Generating a silent slideshow draft video...")
        cmd.extend(["-pix_fmt", "yuv420p", video_out])
        
    print(f"Running ffmpeg command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\nSuccessfully generated draft demo video at: {video_out}")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error during ffmpeg video compilation: {str(e)}")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Capstone Presentation Slides & Video")
    parser.add_argument("--dry-run", action="store_true", help="Generate slide images only, skipping video merge")
    args = parser.parse_args()
    
    sys.exit(build_video(args.dry_run))
