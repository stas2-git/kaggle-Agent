import os
from PIL import Image, ImageDraw, ImageFont

# Only the 4 segments with hand-authored (not live-pipeline-evidence) visuals live here.
# Segments 4/5/6 ("Live Demo") are rendered by build_slides.py from real pytest/eval/agent-run
# output instead - see draw_log_card/draw_stat_card below. Each entry is tagged with its real
# segment_number so build_slides.py can write it straight to slides/rendered/slide_N.png
# without relying on list position (which no longer runs 1..7 contiguously).
SLIDES_DATA = [
    {
        # Bullets here are deliberately short keyword phrases, not full sentences: these
        # slides play under narration audio, and full-sentence bullets make the viewer choose
        # between reading and listening. The slide is a visual anchor, not a transcript - the
        # audio carries the actual explanation.
        "segment_number": 1,
        "title": "Actuarial Portfolio Monitoring Agent",
        "bullets": [
            "Monthly portfolio triage",
            "Automated ingestion & metrics",
            "Tool-first, not LLM math",
            "Faster reviews, full audit trail"
        ]
    },
    {
        "segment_number": 2,
        "title": "Why an Agent? Beyond Dashboards",
        "bullets": [
            "Multi-step validation & investigation",
            "Human-in-the-loop triggers",
            "Prompt-injection protection",
            "Draft summaries for experts"
        ]
    },
    {
        "segment_number": 3,
        "title": "Bounded Five-Layer System Design",
        "bullets": [
            "Data Layer — CSV ingestion",
            "Security Layer — path & injection checks",
            "Tool Layer — deterministic math",
            "Agent Layer — schema-bound Gemini",
            "Output Layer — reports & traces"
        ]
    },
    {
        "segment_number": 7,
        "title": "Real Business Impact & Future Roadmap",
        "bullets": [
            "Hours of review -> seconds",
            "Reproducible, deterministic math",
            "Synthetic data — triage aid only",
            "Next: BigQuery, GKE, alerts"
        ]
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

def draw_slide(title, bullets, output_path, slide_number=None):
    # 1920x1080 Canvas (Sleek dark-mode)
    img = Image.new("RGB", (1920, 1080), color=(18, 24, 38))
    draw = ImageDraw.Draw(img)
    accent = (0, 220, 130)

    # Large faint slide-number watermark, bottom-right - fills what was previously a large
    # empty void below short bullet lists and gives each slide a visual anchor point.
    if slide_number is not None:
        font_watermark = load_system_font(420)
        wm_text = f"{slide_number:02d}"
        draw.text((1560, 560), wm_text, fill=(27, 35, 52), font=font_watermark, anchor="lm")

    # Title Text
    font_title = load_system_font(55)
    draw.text((100, 75), title, fill=(255, 255, 255), font=font_title)

    # Accent green line
    draw.line([(100, 160), (1820, 160)], fill=accent, width=5)

    # Bullets - vertically centered in the space between the divider and the footer, rather
    # than top-anchored, so 3-4 bullet slides don't leave the bottom half of the canvas empty.
    # Sized large: bullets are short keyword phrases meant to be read at a glance while the
    # narration audio carries the actual explanation, not a transcript to read in full.
    font_body = load_system_font(52)
    line_height = 120
    content_top, content_bottom = 200, 960
    block_height = len(bullets) * line_height
    y = content_top + max(0, (content_bottom - content_top - block_height) // 2)
    bullet_radius = 8
    for bullet in bullets:
        cy = y + 33
        draw.ellipse([140 - bullet_radius, cy - bullet_radius, 140 + bullet_radius, cy + bullet_radius], fill=accent)
        draw.text((180, y), bullet, fill=(210, 220, 230), font=font_body)
        y += line_height

    # Actuarial footer disclaimer
    font_footer = load_system_font(20)
    footer_text = "Actuarial Portfolio Monitoring Agent - Capstone Video Draft (Synthetic Data Only)"
    draw.text((100, 1010), footer_text, fill=(100, 110, 120), font=font_footer)

    img.save(output_path)
    print(f"Generated slide image at: {output_path}")

def draw_log_card(title, text_lines, output_path, border_color=(59, 130, 246)):
    # 1920x1080 canvas (Sleek dark-mode slate) - used for content meant to be read in some
    # detail (a report excerpt, a JSON trace), unlike draw_stat_card below.
    img = Image.new("RGB", (1920, 1080), color=(18, 24, 38))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (1920, 15)], fill=border_color)

    font_title = load_system_font(48)
    draw.text((100, 80), title, fill=(255, 255, 255), font=font_title)

    draw.line([(100, 155), (1820, 155)], fill=(100, 110, 120), width=2)

    font_body = load_mono_font(22)
    y = 200
    for line in text_lines:
        line = line.rstrip()
        if len(line) > 115:
            line = line[:112] + "..."
        draw.text((100, y), line, fill=(210, 220, 230), font=font_body)
        y += 34
        if y > 950:
            break

    font_footer = load_system_font(20)
    footer_text = "Actuarial Portfolio Monitoring Agent - Capstone Video Draft (Synthetic Data Only)"
    draw.text((100, 1010), footer_text, fill=(100, 110, 120), font=font_footer)

    img.save(output_path)
    print(f"Generated log card at: {output_path}")

def draw_stat_card(title, headline, sub_lines, output_path, border_color=(59, 130, 246)):
    """Headline-first evidence card: one big glanceable result, plus a few short supporting
    lines - not a raw stdout dump. Used where the underlying data is naturally a single pass/
    fail stat (pytest, eval scorecard) rather than content meant to be read in detail."""
    img = Image.new("RGB", (1920, 1080), color=(18, 24, 38))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (1920, 15)], fill=border_color)

    font_title = load_system_font(48)
    draw.text((100, 80), title, fill=(255, 255, 255), font=font_title)
    draw.line([(100, 155), (1820, 155)], fill=(100, 110, 120), width=2)

    font_headline = load_system_font(72)
    draw.text((100, 260), headline, fill=(210, 220, 230), font=font_headline)

    font_body = load_mono_font(26)
    y = 430
    for line in sub_lines:
        line = line.rstrip()
        if len(line) > 100:
            line = line[:97] + "..."
        draw.text((100, y), line, fill=(160, 175, 190), font=font_body)
        y += 42
        if y > 950:
            break

    font_footer = load_system_font(20)
    footer_text = "Actuarial Portfolio Monitoring Agent - Capstone Video Draft (Synthetic Data Only)"
    draw.text((100, 1010), footer_text, fill=(100, 110, 120), font=font_footer)

    img.save(output_path)
    print(f"Generated stat card at: {output_path}")
