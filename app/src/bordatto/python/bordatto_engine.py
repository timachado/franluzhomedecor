import json, math, os
import pyembroidery
from pyembroidery import EmbPattern, STITCH, JUMP, TRIM, COLOR_CHANGE, END

def _cmd(v):
    return int(v) & 0xFF

def analyze(path):
    pattern = EmbPattern(path)
    points = []
    stitch_count = 0
    jumps = 0
    trims = 0
    color_changes = 0
    dist = 0.0
    prev = None

    for s in pattern.stitches:
        x, y, c = float(s[0]), float(s[1]), _cmd(s[2])
        if c == STITCH:
            stitch_count += 1
            points.append([x, y])
            if prev is not None:
                dist += math.hypot(x - prev[0], y - prev[1])
            prev = (x, y)
        elif c == JUMP:
            jumps += 1
            prev = None
        elif c == TRIM:
            trims += 1
            prev = None
        elif c == COLOR_CHANGE:
            color_changes += 1
            prev = None

    if points:
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        width_mm = (max(xs) - min(xs)) / 10.0
        height_mm = (max(ys) - min(ys)) / 10.0
    else:
        width_mm = 0.0
        height_mm = 0.0

    colors = []
    for t in pattern.threadlist:
        try:
            colors.append(t.hex_color())
        except Exception:
            colors.append("#2b1c17")

    step = max(1, len(points) // 18000)
    sampled = points[::step]
    thread_m = (dist / 10.0 / 1000.0) * 2.2

    return json.dumps({
        "stitches": stitch_count,
        "jumps": jumps,
        "trims": trims,
        "color_changes": color_changes,
        "width_mm": width_mm,
        "height_mm": height_mm,
        "thread_m": thread_m,
        "colors": colors,
        "points": sampled,
    })

def convert(src, dst):
    pyembroidery.convert(src, dst)
    return dst

def text_to_embroidery(text, font_path, width_mm, color_hex, out_path):
    from PIL import Image, ImageDraw, ImageFont

    text = (text or "").strip()
    if not text:
        raise ValueError("Digite um nome ou texto.")
    if not os.path.exists(font_path):
        raise FileNotFoundError("Fonte não encontrada.")

    font = ImageFont.truetype(font_path, 180)
    box = font.getbbox(text)
    w = max(8, box[2] - box[0] + 28)
    h = max(8, box[3] - box[1] + 28)

    img = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(img)
    draw.text((14 - box[0], 14 - box[1]), text, font=font, fill=255)

    target_w = max(100.0, float(width_mm) * 10.0)
    scale = target_w / float(w)
    px = img.load()

    p = EmbPattern()
    p.add_thread(color_hex or "#d7b46a")

    row_step = 4
    point_step = 7
    reverse = False
    started = False

    for y in range(0, h, row_step):
        runs = []
        x = 0
        while x < w:
            while x < w and px[x, y] < 96:
                x += 1
            if x >= w:
                break
            a = x
            while x < w and px[x, y] >= 96:
                x += 1
            b = x - 1
            if b - a >= 2:
                runs.append((a, b))

        if reverse:
            runs.reverse()

        for a, b in runs:
            xs = list(range(a, b + 1, point_step))
            if not xs or xs[-1] != b:
                xs.append(b)
            if reverse:
                xs.reverse()

            sx = xs[0] * scale
            sy = y * scale
            if started:
                p.trim()
            p.add_stitch_absolute(JUMP, sx, sy)

            for xi in xs:
                p.add_stitch_absolute(STITCH, xi * scale, y * scale)
            started = True

        reverse = not reverse

    p.add_command(END)
    pyembroidery.write(p, out_path)
    return out_path
