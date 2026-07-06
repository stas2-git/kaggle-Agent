import os
from PIL import Image, ImageDraw, ImageFont
from story_contract import get_static_slide_data

# Static slide content comes from story/slide_story.yaml. Segments 4/5/6 are evidence visuals
# rendered by build_slides.py from live output plus the stable story contract.
SLIDES_DATA = get_static_slide_data()

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

def wrap_text(draw, text, font, max_width):
    """Greedy word-wrap text to fit within max_width at the given font, using actual glyph
    measurement (not a character-count guess) since proportional fonts vary too much per
    character for a fixed-width heuristic to be reliable."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if not current or draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def draw_footer(draw):
    font_footer = load_system_font(20)
    footer_text = "Actuarial Portfolio Monitoring Agent - Capstone Submission (Synthetic Data Only)"
    draw.text((100, 1010), footer_text, fill=(78, 88, 104), font=font_footer)

def draw_header(draw, title, accent, border_top=False):
    font_title = load_system_font(52)
    draw.text((100, 78), title, fill=(255, 255, 255), font=font_title)
    draw.line([(100, 155), (1820, 155)], fill=accent, width=4)

def draw_wrapped(draw, text, xy, font, fill, max_width, line_height):
    x, y = xy
    for line in wrap_text(draw, text, font, max_width):
        draw.text((x, y), line, fill=fill, font=font)
        y += line_height
    return y

def draw_story_cue(draw, text, accent):
    box = (100, 875, 1820, 965)
    draw.rounded_rectangle(box, radius=18, fill=(25, 34, 50), outline=(55, 68, 88), width=2)
    draw.rectangle((100, 875, 112, 965), fill=accent)
    font_label = load_system_font(22)
    font_text = load_system_font(29)
    draw.text((135, 895), "Takeaway", fill=accent, font=font_label)
    draw_wrapped(draw, text, (135, 922), font_text, (220, 230, 240), 1620, 34)

def draw_idea_card(draw, rect, label, text, accent):
    x1, y1, x2, y2 = rect
    draw.rounded_rectangle(rect, radius=18, fill=(25, 34, 50), outline=(55, 68, 88), width=2)
    draw.rounded_rectangle((x1 + 24, y1 + 24, x1 + 82, y1 + 82), radius=12, fill=(21, 52, 48), outline=accent, width=2)
    font_label = load_system_font(30)
    draw.text((x1 + 53, y1 + 51), label, fill=accent, font=font_label, anchor="mm")
    font_text = load_system_font(39)
    draw_wrapped(draw, text, (x1 + 105, y1 + 32), font_text, (235, 241, 247), x2 - x1 - 135, 48)

def draw_arrow(draw, start, end, color, width=5):
    sx, sy = start
    ex, ey = end
    draw.line((sx, sy, ex, ey), fill=color, width=width)
    draw.polygon([(ex, ey), (ex - 18, ey - 11), (ex - 18, ey + 11)], fill=color)

def draw_slide(title, hook, bullets, output_path, slide_number=None, cue=None):
    # 1920x1080 Canvas (Sleek dark-mode)
    img = Image.new("RGB", (1920, 1080), color=(18, 24, 38))
    draw = ImageDraw.Draw(img)
    accent = (0, 220, 130)

    if slide_number is not None:
        font_watermark = load_system_font(420)
        wm_text = f"{slide_number:02d}"
        draw.text((1560, 560), wm_text, fill=(27, 35, 52), font=font_watermark, anchor="lm")

    draw_header(draw, title, accent)

    font_hook = load_system_font(62)
    draw_wrapped(draw, hook, (100, 230), font_hook, (245, 248, 252), 1500, 72)

    card_top = 520
    card_width = 530
    gap = 45
    for idx, bullet in enumerate(bullets):
        x = 100 + idx * (card_width + gap)
        draw_idea_card(draw, (x, card_top, x + card_width, card_top + 170), str(idx + 1), bullet, accent)

    if cue:
        draw_story_cue(draw, cue, accent)
    draw_footer(draw)

    img.save(output_path)
    print(f"Generated slide image at: {output_path}")

def draw_pipeline_card(title, headline, steps, metric_cards, review_text, cue, output_path, border_color=(245, 158, 11)):
    img = Image.new("RGB", (1920, 1080), color=(18, 24, 38))
    draw = ImageDraw.Draw(img)
    draw_header(draw, title, border_color, border_top=True)
    soft_accent = (20, 180, 125)

    font_headline = load_system_font(66)
    draw.text((100, 230), headline, fill=(238, 243, 249), font=font_headline)

    step_y = 390
    step_w = 260
    step_h = 120
    step_gap = 70
    font_step = load_system_font(31)
    for idx, step in enumerate(steps):
        x = 100 + idx * (step_w + step_gap)
        draw.rounded_rectangle((x, step_y, x + step_w, step_y + step_h), radius=16, fill=(25, 34, 50), outline=(75, 88, 110), width=2)
        draw.text((x + step_w / 2, step_y + 60), step, fill=(232, 238, 246), font=font_step, anchor="mm")
        if idx < len(steps) - 1:
            draw_arrow(draw, (x + step_w + 12, step_y + 60), (x + step_w + step_gap - 18, step_y + 60), border_color, width=4)

    font_card_label = load_system_font(28)
    font_card_value = load_system_font(48)
    metric_y = 610
    for idx, card in enumerate(metric_cards):
        x = 100 + idx * 570
        draw.rounded_rectangle((x, metric_y, x + 520, metric_y + 140), radius=18, fill=(28, 38, 56), outline=soft_accent, width=2)
        draw.text((x + 28, metric_y + 24), card["label"], fill=(170, 185, 205), font=font_card_label)
        draw.text((x + 28, metric_y + 70), card["value"], fill=(250, 253, 255), font=font_card_value)

    x = 1240
    draw.rounded_rectangle((x, metric_y, 1820, metric_y + 140), radius=18, fill=(20, 60, 54), outline=soft_accent, width=2)
    draw.text((x + 28, metric_y + 24), "Review gate", fill=(165, 240, 215), font=font_card_label)
    draw.text((x + 28, metric_y + 70), review_text, fill=(255, 255, 255), font=font_card_value)

    draw_story_cue(draw, cue, border_color)
    draw_footer(draw)
    img.save(output_path)
    print(f"Generated pipeline card at: {output_path}")

def draw_driver_card(title, headline, focus, left_cards, right_cards, cue, output_path, border_color=(16, 185, 129)):
    img = Image.new("RGB", (1920, 1080), color=(18, 24, 38))
    draw = ImageDraw.Draw(img)
    draw_header(draw, title, border_color, border_top=True)

    font_headline = load_system_font(60)
    draw_wrapped(draw, headline, (100, 215), font_headline, (245, 248, 252), 1650, 68)

    center = (710, 405, 1210, 725)
    draw.rounded_rectangle(center, radius=26, fill=(20, 60, 54), outline=border_color, width=4)
    font_focus_label = load_system_font(25)
    font_chip_label = load_system_font(19)
    font_chip_value = load_system_font(30)
    draw.text((960, 455), "Where to look first", fill=(165, 240, 215), font=font_focus_label, anchor="mm")
    focus_labels = ["State", "Coverage", "UW", "Policy year"]
    chip_w = 190
    chip_h = 68
    chip_positions = [(750, 505), (980, 505), (750, 600), (980, 600)]
    for idx, line in enumerate(focus[:4]):
        x, y = chip_positions[idx]
        draw.rounded_rectangle((x, y, x + chip_w, y + chip_h), radius=14, fill=(24, 77, 68), outline=(45, 152, 120), width=1)
        draw.text((x + 18, y + 13), focus_labels[idx], fill=(145, 210, 190), font=font_chip_label)
        draw.text((x + 18, y + 35), line, fill=(255, 255, 255), font=font_chip_value)

    font_label = load_system_font(28)
    font_value = load_system_font(38)
    for idx, card in enumerate(left_cards):
        y = 420 + idx * 155
        draw.rounded_rectangle((100, y, 575, y + 120), radius=18, fill=(28, 38, 56), outline=(55, 68, 88), width=2)
        draw.text((128, y + 22), card["label"], fill=(170, 185, 205), font=font_label)
        draw.text((128, y + 64), card["value"], fill=(245, 248, 252), font=font_value)
        draw_arrow(draw, (590, y + 60), (705, y + 60), border_color, width=4)

    for idx, card in enumerate(right_cards):
        y = 420 + idx * 126
        draw.rounded_rectangle((1345, y, 1820, y + 96), radius=18, fill=(28, 38, 56), outline=(55, 68, 88), width=2)
        draw.text((1375, y + 27), card, fill=(235, 241, 247), font=load_system_font(32))
        draw_arrow(draw, (1215, y + 48), (1320, y + 48), border_color, width=4)

    draw_story_cue(draw, cue, border_color)
    draw_footer(draw)
    img.save(output_path)
    print(f"Generated driver card at: {output_path}")

def draw_verification_card(title, headline, pillars, cue, output_path, border_color=(139, 92, 246)):
    img = Image.new("RGB", (1920, 1080), color=(18, 24, 38))
    draw = ImageDraw.Draw(img)
    draw_header(draw, title, border_color, border_top=True)

    font_headline = load_system_font(60)
    draw_wrapped(draw, headline, (100, 225), font_headline, (245, 248, 252), 1640, 68)

    card_w = 520
    gap = 55
    y = 430
    soft_accent = (20, 180, 125)
    for idx, pillar in enumerate(pillars):
        x = 100 + idx * (card_w + gap)
        draw.rounded_rectangle((x, y, x + card_w, y + 250), radius=22, fill=(28, 38, 56), outline=soft_accent, width=2)
        draw.text((x + 36, y + 34), pillar["value"], fill=(255, 255, 255), font=load_system_font(66))
        draw.text((x + 36, y + 112), pillar["label"], fill=(205, 215, 230), font=load_system_font(34))
        draw_wrapped(draw, pillar["note"], (x + 36, y + 165), load_system_font(27), (155, 170, 190), card_w - 72, 34)

    draw_story_cue(draw, cue, border_color)
    draw_footer(draw)
    img.save(output_path)
    print(f"Generated verification card at: {output_path}")

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
    footer_text = "Actuarial Portfolio Monitoring Agent - Capstone Submission (Synthetic Data Only)"
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
    footer_text = "Actuarial Portfolio Monitoring Agent - Capstone Submission (Synthetic Data Only)"
    draw.text((100, 1010), footer_text, fill=(100, 110, 120), font=font_footer)

    img.save(output_path)
    print(f"Generated stat card at: {output_path}")
