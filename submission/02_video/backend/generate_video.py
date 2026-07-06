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

def draw_compact_card(draw, rect, label, text, accent):
    x1, y1, x2, y2 = rect
    draw.rounded_rectangle(rect, radius=16, fill=(25, 34, 50), outline=(55, 68, 88), width=2)
    draw.text((x1 + 28, y1 + 24), label, fill=accent, font=load_system_font(24))
    draw_wrapped(draw, text, (x1 + 28, y1 + 62), load_system_font(36), (235, 241, 247), x2 - x1 - 56, 42)

def draw_arrow(draw, start, end, color, width=5):
    sx, sy = start
    ex, ey = end
    draw.line((sx, sy, ex, ey), fill=color, width=width)
    draw.polygon([(ex, ey), (ex - 18, ey - 11), (ex - 18, ey + 11)], fill=color)

def draw_title_slide(output_path):
    img = Image.new("RGB", (1920, 1080), color=(18, 24, 38))
    draw = ImageDraw.Draw(img)
    accent = (0, 220, 130)

    draw.rectangle((0, 0, 1920, 1080), fill=(18, 24, 38))
    draw.rectangle((120, 165, 132, 690), fill=accent)
    draw.text((175, 175), "Actuarial Portfolio", fill=(245, 248, 252), font=load_system_font(92))
    draw.text((175, 285), "Monitoring Agent", fill=(245, 248, 252), font=load_system_font(92))
    draw.text((178, 445), "Kaggle Agents Capstone", fill=accent, font=load_system_font(34))
    draw.text((178, 500), "July 6, 2026", fill=(185, 200, 220), font=load_system_font(34))
    img.save(output_path)
    print(f"Generated title slide image at: {output_path}")

def draw_problem_slide(title, hook, bullets, output_path, slide_number=None, cue=None):
    img = Image.new("RGB", (1920, 1080), color=(18, 24, 38))
    draw = ImageDraw.Draw(img)
    accent = (0, 220, 130)

    if slide_number is not None:
        font_watermark = load_system_font(420)
        draw.text((1500, 560), f"{slide_number:02d}", fill=(27, 35, 52), font=font_watermark, anchor="lm")

    draw_header(draw, title, accent)
    draw_wrapped(draw, hook, (100, 235), load_system_font(64), (245, 248, 252), 1120, 76)

    y = 500
    labels = ["Pain point", "Analysis need", "Output burden"]
    for idx, bullet in enumerate(bullets):
        draw_compact_card(draw, (1180, y + idx * 130, 1820, y + idx * 130 + 104), labels[idx], bullet, accent)

    draw.rounded_rectangle((100, 545, 990, 735), radius=24, fill=(20, 60, 54), outline=(0, 160, 110), width=2)
    draw.text((145, 588), "Monthly review", fill=(165, 240, 215), font=load_system_font(28))
    draw_wrapped(draw, "The bottleneck is explanation, not charting.", (145, 632), load_system_font(46), (255, 255, 255), 780, 54)

    if cue:
        draw_story_cue(draw, cue, accent)
    draw_footer(draw)
    img.save(output_path)
    print(f"Generated problem slide image at: {output_path}")

def draw_agent_bridge_slide(title, hook, bullets, output_path, slide_number=None, cue=None):
    img = Image.new("RGB", (1920, 1080), color=(18, 24, 38))
    draw = ImageDraw.Draw(img)
    accent = (0, 220, 130)

    if slide_number is not None:
        font_watermark = load_system_font(420)
        draw.text((1500, 560), f"{slide_number:02d}", fill=(27, 35, 52), font=font_watermark, anchor="lm")

    draw_header(draw, title, accent)
    draw_wrapped(draw, hook, (100, 230), load_system_font(62), (245, 248, 252), 1540, 72)

    nodes = [
        ("Dashboard", "Shows movement"),
        ("Agent", "Chooses next tool"),
        ("Review", "Escalates judgment"),
    ]
    y = 470
    for idx, (label, text) in enumerate(nodes):
        x = 100 + idx * 610
        fill = (20, 60, 54) if idx == 1 else (25, 34, 50)
        outline = accent if idx == 1 else (55, 68, 88)
        draw.rounded_rectangle((x, y, x + 440, y + 165), radius=22, fill=fill, outline=outline, width=3 if idx == 1 else 2)
        draw.text((x + 32, y + 32), label, fill=accent if idx == 1 else (170, 185, 205), font=load_system_font(28))
        draw.text((x + 32, y + 84), text, fill=(245, 248, 252), font=load_system_font(38))
        if idx < len(nodes) - 1:
            draw_arrow(draw, (x + 465, y + 82), (x + 575, y + 82), accent, width=5)

    for idx, bullet in enumerate(bullets):
        x = 170 + idx * 550
        draw.text((x, 700), bullet, fill=(185, 200, 220), font=load_system_font(30))

    if cue:
        draw_story_cue(draw, cue, accent)
    draw_footer(draw)
    img.save(output_path)
    print(f"Generated bridge slide image at: {output_path}")

def draw_architecture_layers_slide(title, hook, bullets, output_path, slide_number=None, cue=None):
    img = Image.new("RGB", (1920, 1080), color=(18, 24, 38))
    draw = ImageDraw.Draw(img)
    accent = (0, 220, 130)

    if slide_number is not None:
        font_watermark = load_system_font(420)
        draw.text((1500, 560), f"{slide_number:02d}", fill=(27, 35, 52), font=font_watermark, anchor="lm")

    draw_header(draw, title, accent)
    draw_wrapped(draw, hook, (100, 225), load_system_font(58), (245, 248, 252), 1500, 68)

    layers = bullets[:5]
    layer_w = 316
    gap = 32
    y = 500
    for idx, layer in enumerate(layers):
        x = 100 + idx * (layer_w + gap)
        draw.rounded_rectangle((x, y, x + layer_w, y + 155), radius=18, fill=(25, 34, 50), outline=(55, 68, 88), width=2)
        draw.rounded_rectangle((x + 24, y + 24, x + 74, y + 74), radius=12, fill=(21, 52, 48), outline=accent, width=2)
        draw.text((x + 49, y + 49), str(idx + 1), fill=accent, font=load_system_font(25), anchor="mm")
        draw_wrapped(draw, layer, (x + 24, y + 92), load_system_font(28), (235, 241, 247), layer_w - 48, 34)
        if idx < len(layers) - 1:
            draw_arrow(draw, (x + layer_w + 8, y + 77), (x + layer_w + gap - 8, y + 77), accent, width=3)

    draw.text((100, 695), "Gemini writes from bounded tool outputs; it does not calculate the metrics.", fill=(185, 200, 220), font=load_system_font(34))

    if cue:
        draw_story_cue(draw, cue, accent)
    draw_footer(draw)
    img.save(output_path)
    print(f"Generated architecture slide image at: {output_path}")

def draw_closing_slide(title, hook, bullets, output_path, slide_number=None, cue=None):
    img = Image.new("RGB", (1920, 1080), color=(18, 24, 38))
    draw = ImageDraw.Draw(img)
    accent = (0, 220, 130)

    if slide_number is not None:
        font_watermark = load_system_font(420)
        draw.text((1500, 560), f"{slide_number:02d}", fill=(27, 35, 52), font=font_watermark, anchor="lm")

    draw_header(draw, title, accent)

    draw_wrapped(draw, hook, (100, 230), load_system_font(60), (245, 248, 252), 1640, 72)

    draw.rounded_rectangle((100, 500, 1010, 735), radius=26, fill=(20, 60, 54), outline=(0, 160, 110), width=2)
    draw.text((145, 548), "Closing claim", fill=(165, 240, 215), font=load_system_font(28))
    draw_wrapped(
        draw,
        "Experts decide. Evidence travels with the memo.",
        (145, 602),
        load_system_font(48),
        (255, 255, 255),
        780,
        58,
    )

    x1, y1 = 1160, 390
    draw.text((x1, y1), "Roadmap", fill=accent, font=load_system_font(32))
    for idx, item in enumerate(bullets):
        y = y1 + 70 + idx * 105
        draw.rounded_rectangle((x1, y, 1820, y + 78), radius=18, fill=(25, 34, 50), outline=(55, 68, 88), width=2)
        draw.rounded_rectangle((x1 + 24, y + 20, x1 + 62, y + 58), radius=10, fill=(21, 52, 48), outline=accent, width=2)
        draw.text((x1 + 43, y + 39), str(idx + 1), fill=accent, font=load_system_font(21), anchor="mm")
        draw.text((x1 + 88, y + 24), item, fill=(235, 241, 247), font=load_system_font(31))
        if idx < len(bullets) - 1:
            draw.line((x1 + 43, y + 78, x1 + 43, y + 105), fill=accent, width=3)

    if cue:
        draw_story_cue(draw, cue, accent)
    draw_footer(draw)
    img.save(output_path)
    print(f"Generated closing slide image at: {output_path}")

def draw_slide(title, hook, bullets, output_path, slide_number=None, cue=None):
    if slide_number == 1:
        return draw_problem_slide(title, hook, bullets, output_path, slide_number=slide_number, cue=cue)
    if slide_number == 2:
        return draw_agent_bridge_slide(title, hook, bullets, output_path, slide_number=slide_number, cue=cue)
    if slide_number == 3:
        return draw_architecture_layers_slide(title, hook, bullets, output_path, slide_number=slide_number, cue=cue)
    if slide_number == 7:
        return draw_closing_slide(title, hook, bullets, output_path, slide_number=slide_number, cue=cue)

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

def draw_agent_run_graph_card(title, headline, nodes, metric_cards, review_text, cue, output_path, border_color=(0, 220, 130), example=None):
    img = Image.new("RGB", (1920, 1080), color=(18, 24, 38))
    draw = ImageDraw.Draw(img)
    draw_header(draw, title, border_color, border_top=True)
    soft_accent = (20, 180, 125)

    draw_wrapped(draw, headline, (100, 220), load_system_font(60), (238, 243, 249), 1560, 68)

    example = example or {
        "file": "loss_ratio_spike.csv",
        "month": "2026-06",
        "description": "Synthetic portfolio CSV",
        "question": "Does this need human review?",
    }

    panel_y = 355
    panel_h = 430
    left = (100, panel_y, 620, panel_y + panel_h)
    middle = (700, panel_y, 1220, panel_y + panel_h)
    right = (1300, panel_y, 1820, panel_y + panel_h)

    draw.rounded_rectangle(left, radius=22, fill=(25, 34, 50), outline=soft_accent, width=2)
    draw.text((130, panel_y + 34), "Example input", fill=border_color, font=load_system_font(30))
    draw.text((130, panel_y + 88), example["file"], fill=(248, 251, 255), font=load_system_font(33))
    draw.text((130, panel_y + 138), f"Latest month: {example['month']}", fill=(185, 200, 220), font=load_system_font(29))
    draw.text((130, panel_y + 184), example["description"], fill=(185, 200, 220), font=load_system_font(29))
    draw.rounded_rectangle((130, panel_y + 250, 590, panel_y + 350), radius=18, fill=(20, 60, 54), outline=soft_accent, width=2)
    draw_wrapped(draw, example["question"], (158, panel_y + 276), load_system_font(35), (255, 255, 255), 405, 42)

    draw.rounded_rectangle(middle, radius=22, fill=(25, 34, 50), outline=(55, 68, 88), width=2)
    draw.text((730, panel_y + 34), "Agent run", fill=border_color, font=load_system_font(30))
    compact_nodes = [node for node in nodes if node["label"] not in ("Input", "Review gate")][:3]
    for idx, node in enumerate(compact_nodes):
        y = panel_y + 92 + idx * 76
        is_gate = node.get("kind") == "gate"
        draw.rounded_rectangle((730, y, 1190, y + 54), radius=14, fill=(20, 60, 54) if is_gate else (28, 38, 56), outline=border_color if is_gate else (55, 68, 88), width=2)
        draw.text((755, y + 14), node["label"], fill=border_color if is_gate else (205, 215, 230), font=load_system_font(23))
        if idx < len(compact_nodes) - 1:
            draw.line((960, y + 54, 960, y + 76), fill=border_color, width=3)

    draw.rounded_rectangle(right, radius=22, fill=(20, 60, 54), outline=border_color, width=3)
    draw.text((1330, panel_y + 34), "Review decision", fill=(165, 240, 215), font=load_system_font(30))
    draw.text((1330, panel_y + 104), review_text, fill=(255, 255, 255), font=load_system_font(58))
    draw_wrapped(draw, "The agent prepares the case for actuarial review.", (1330, panel_y + 190), load_system_font(33), (215, 235, 228), 425, 42)

    draw.text((730, panel_y + 312), "Observed movement", fill=(170, 185, 205), font=load_system_font(22))
    font_card_value = load_system_font(29)
    metric_y = panel_y + 338
    for idx, card in enumerate(metric_cards):
        y = metric_y + idx * 48
        label = card["label"].replace("Symptom 1: ", "").replace("Symptom 2: ", "")
        draw.rounded_rectangle((730, y, 1190, y + 40), radius=12, fill=(28, 38, 56), outline=soft_accent, width=2)
        draw.text((750, y + 10), label, fill=(170, 185, 205), font=load_system_font(19))
        value_width = draw.textlength(card["value"], font=font_card_value)
        draw.text((1170 - value_width, y + 6), card["value"], fill=(250, 253, 255), font=font_card_value)

    draw_story_cue(draw, cue, border_color)
    draw_footer(draw)
    img.save(output_path)
    print(f"Generated agent run graph card at: {output_path}")

def draw_pipeline_card(title, headline, steps, metric_cards, review_text, cue, output_path, border_color=(245, 158, 11)):
    nodes = [{"label": f"Step {idx + 1}", "detail": step, "kind": "gate" if idx == len(steps) - 1 else "tool"} for idx, step in enumerate(steps)]
    draw_agent_run_graph_card(title, headline, nodes, metric_cards, review_text, cue, output_path, border_color=border_color)

def draw_driver_card(title, headline, focus, left_cards, right_cards, cue, output_path, border_color=(16, 185, 129)):
    img = Image.new("RGB", (1920, 1080), color=(18, 24, 38))
    draw = ImageDraw.Draw(img)
    draw_header(draw, title, border_color, border_top=True)

    font_headline = load_system_font(60)
    draw_wrapped(draw, headline, (100, 215), font_headline, (245, 248, 252), 1650, 68)

    draw.text((100, 350), "1. Anomalies", fill=border_color, font=load_system_font(28))
    draw.text((595, 350), "2. Decompose by", fill=border_color, font=load_system_font(28))
    draw.text((975, 350), "3. Convergence", fill=border_color, font=load_system_font(28))
    draw.text((1415, 350), "4. Why it matters", fill=border_color, font=load_system_font(28))

    font_label = load_system_font(25)
    font_value = load_system_font(38)
    for idx, card in enumerate(left_cards):
        y = 410 + idx * 155
        draw.rounded_rectangle((100, y, 500, y + 120), radius=18, fill=(28, 38, 56), outline=(55, 68, 88), width=2)
        draw.text((128, y + 22), card["label"], fill=(170, 185, 205), font=font_label)
        draw.text((128, y + 62), card["value"], fill=(245, 248, 252), font=font_value)
        draw_arrow(draw, (515, y + 60), (570, y + 60), border_color, width=4)

    draw.rounded_rectangle((590, 405, 890, 700), radius=22, fill=(25, 34, 50), outline=(55, 68, 88), width=2)
    draw_wrapped(draw, "The agent slices each movement across driver fields.", (620, 432), load_system_font(25), (205, 215, 230), 240, 32)
    driver_labels = ["State", "Coverage", "Underwriter", "Policy year"]
    for idx, label in enumerate(driver_labels):
        y = 540 + idx * 38
        draw.rounded_rectangle((620, y, 860, y + 28), radius=10, fill=(28, 38, 56), outline=(55, 68, 88), width=1)
        draw.text((740, y + 14), label, fill=(230, 238, 246), font=load_system_font(20), anchor="mm")

    draw_arrow(draw, (905, 552), (955, 552), border_color, width=4)

    center = (970, 405, 1335, 700)
    draw.rounded_rectangle(center, radius=26, fill=(20, 60, 54), outline=border_color, width=4)
    draw.text((1152, 438), "Both paths land here", fill=(165, 240, 215), font=load_system_font(25), anchor="mm")
    focus_labels = ["State", "Coverage", "UW", "Policy year"]
    chip_positions = [(1015, 490), (1180, 490), (1015, 592), (1180, 592)]
    for idx, line in enumerate(focus[:4]):
        x, y = chip_positions[idx]
        draw.rounded_rectangle((x, y, x + 120, y + 66), radius=14, fill=(24, 77, 68), outline=(45, 152, 120), width=1)
        draw.text((x + 14, y + 12), focus_labels[idx], fill=(145, 210, 190), font=load_system_font(17))
        draw.text((x + 14, y + 34), line, fill=(255, 255, 255), font=load_system_font(27))

    draw_arrow(draw, (1348, 552), (1398, 552), border_color, width=4)

    right_notes = ["Focused review", "Better questions", "Auditable trace"]
    for idx, note in enumerate(right_notes):
        y = 420 + idx * 86
        draw.rounded_rectangle((1415, y, 1820, y + 68), radius=16, fill=(28, 38, 56), outline=(55, 68, 88), width=2)
        draw.text((1445, y + 19), note, fill=(235, 241, 247), font=load_system_font(29))

    draw_wrapped(draw, "The value is not the alert. It is knowing where to look first.", (970, 730), load_system_font(30), (185, 200, 220), 825, 36)

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
