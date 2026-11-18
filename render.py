#!/usr/bin/env python3
"""Render entry.png for the make.fun news-image-20261117 bounty.

Draws a 1024x1024 infographic summing up Tuesday 17 November 2026:
a big date header plus six panels, each with a flat icon drawn from
PIL primitives, a short headline and one factual sub-line.

Deterministic: fixed fonts, fixed geometry, no randomness, no timestamps.
Run: python3 render.py  ->  writes entry.png next to this file.
Requires Pillow (render-time only; the entry's main.py is stdlib-only).
"""

import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
REGULAR = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"

W = H = 1024
NAVY = (16, 35, 63)
GOLD = (242, 183, 5)
PANEL_BG = (247, 243, 234)
PANEL_EDGE = (216, 210, 196)
INK = (22, 35, 58)
SUB_INK = (69, 80, 98)
WHITE = (255, 255, 255)

HEADER_H = 148
MARGIN = 16
GAP = 14
PANEL_W = (W - 2 * MARGIN - GAP) // 2          # 489
PANEL_H = 277
ICON_STRIP = 110


def font(path, size):
    return ImageFont.truetype(path, size)


def mix(rgb, white_frac):
    """Blend an accent colour towards white (for the icon strip tint)."""
    return tuple(int(c + (255 - c) * white_frac) for c in rgb)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_spaced(draw, cx, y, text, fnt, fill, tracking):
    """Draw text centred on cx with extra letter tracking."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking


# ---------------------------------------------------------------- icons
# Each draws a simple flat icon in `color`, centred on (cx, cy),
# inside a ~76x76 box. PIL primitives only; no photos or assets.

def icon_bridge(d, cx, cy, c):
    d.line([(cx - 34, cy + 30), (cx + 34, cy + 30)], fill=c, width=3)
    d.rectangle([cx - 36, cy + 8, cx + 36, cy + 14], fill=c)
    d.rectangle([cx - 28, cy - 28, cx - 22, cy + 8], fill=c)
    d.rectangle([cx + 22, cy - 28, cx + 28, cy + 8], fill=c)
    d.line([(cx - 25, cy - 28), (cx, cy + 8)], fill=c, width=2)
    d.line([(cx + 25, cy - 28), (cx, cy + 8)], fill=c, width=2)
    d.line([(cx - 25, cy - 28), (cx - 36, cy + 8)], fill=c, width=2)
    d.line([(cx + 25, cy - 28), (cx + 36, cy + 8)], fill=c, width=2)


def icon_gate(d, cx, cy, c):
    d.rectangle([cx - 32, cy - 24, cx - 26, cy + 28], fill=c)
    d.rectangle([cx + 26, cy - 24, cx + 32, cy + 28], fill=c)
    d.line([(cx - 34, cy + 28), (cx + 34, cy + 28)], fill=c, width=3)
    # striped barrier bar across the gate
    d.rectangle([cx - 32, cy - 8, cx + 32, cy - 1], fill=c)
    for x in range(cx - 32, cx + 32, 12):
        d.rectangle([x, cy - 8, x + 6, cy - 1], fill=WHITE)


def icon_court(d, cx, cy, c):
    d.polygon([(cx - 36, cy - 2), (cx + 36, cy - 2), (cx, cy - 26)], fill=c)
    d.rectangle([cx - 34, cy - 2, cx + 34, cy + 4], fill=c)
    for x0 in (-26, -3, 20):
        d.rectangle([cx + x0, cy + 4, cx + x0 + 6, cy + 20], fill=c)
    d.rectangle([cx - 34, cy + 20, cx + 34, cy + 28], fill=c)


def icon_jet(d, cx, cy, c):
    # side view, nose to the right
    d.polygon([(cx + 38, cy), (cx - 16, cy - 9), (cx - 28, cy - 4),
               (cx - 28, cy + 4), (cx - 16, cy + 9)], fill=c)
    d.polygon([(cx + 4, cy - 2), (cx - 12, cy - 28), (cx - 22, cy - 28),
               (cx - 8, cy - 2)], fill=c)
    d.polygon([(cx - 20, cy - 2), (cx - 30, cy - 20), (cx - 36, cy - 20),
               (cx - 27, cy - 2)], fill=c)
    d.ellipse([cx + 22, cy - 5, cx + 30, cy + 1], fill=WHITE)


def icon_drone(d, cx, cy, c):
    for sx, sy in ((-30, -18), (30, -18), (-30, 18), (30, 18)):
        d.line([(cx, cy), (cx + sx, cy + sy)], fill=c, width=4)
        d.ellipse([cx + sx - 9, cy + sy - 9, cx + sx + 9, cy + sy + 9],
                  outline=c, width=3)
        d.ellipse([cx + sx - 2, cy + sy - 2, cx + sx + 2, cy + sy + 2], fill=c)
    d.rounded_rectangle([cx - 13, cy - 8, cx + 13, cy + 8], radius=4, fill=c)
    d.ellipse([cx - 3, cy + 8, cx + 3, cy + 14], fill=c)


def icon_parliament(d, cx, cy, c):
    d.pieslice([cx - 14, cy - 28, cx + 14, cy + 0], 180, 360, fill=c)
    d.line([(cx, cy - 28), (cx, cy - 40)], fill=c, width=2)
    d.polygon([(cx, cy - 40), (cx + 12, cy - 36), (cx, cy - 32)], fill=c)
    d.rectangle([cx - 30, cy - 6, cx + 30, cy + 16], fill=c)
    for x0 in (-24, -3, 18):
        d.rectangle([cx + x0, cy - 6, cx + x0 + 6, cy + 16], fill=WHITE)
    d.rectangle([cx - 34, cy + 16, cx + 34, cy + 28], fill=c)


ICONS = {
    "bridge": icon_bridge,
    "gate": icon_gate,
    "court": icon_court,
    "jet": icon_jet,
    "drone": icon_drone,
    "parliament": icon_parliament,
}

# ------------------------------------------------------------- stories
# Only verified 17 November 2026 stories. Headline <= 2 lines,
# sub-line <= 3 lines at the sizes below.
STORIES = [
    ("bridge", (46, 111, 163), "KERCH BRIDGE STRUCK",
     "Ukraine hits the Crimea link; Russia hits a bridge in Kyiv"),
    ("gate", (31, 138, 112), "GAZA AID CROSSINGS",
     "UK, Australia, Canada and Italy urge Israel to open the crossings"),
    ("court", (108, 79, 161), "DEPARDIEU DROPS APPEAL",
     "Actor admits a sexual-assault charge in Paris"),
    ("jet", (176, 58, 46), "JAPAN SCRAMBLES JETS",
     "Russian aircraft enters Japanese airspace"),
    ("drone", (201, 122, 26), "IRAN AND US TRADE STRIKES",
     "Iran hits a US base in Bahrain; US strikes Qeshm island"),
    ("parliament", (46, 125, 50), "MONGOLIA PRESIDENT RESIGNS",
     "President Khürelsükh quits amid a corruption scandal"),
]


def draw_panel(d, x, y, icon_name, accent, headline, sub):
    d.rounded_rectangle([x, y, x + PANEL_W, y + PANEL_H], radius=10,
                        fill=PANEL_BG, outline=PANEL_EDGE, width=2)
    # tinted icon strip on the left
    d.rounded_rectangle([x, y, x + ICON_STRIP, y + PANEL_H], radius=10,
                        fill=mix(accent, 0.86))
    # square off the strip's right edge (cover the rounded corners)
    d.rectangle([x + ICON_STRIP - 10, y, x + ICON_STRIP, y + PANEL_H],
                fill=mix(accent, 0.86))
    ICONS[icon_name](d, x + ICON_STRIP // 2, y + PANEL_H // 2, accent)

    tx = x + ICON_STRIP + 16
    tw = PANEL_W - ICON_STRIP - 16 - 16
    # headline: shrink until it fits on at most 2 lines
    head_f = None
    for size in (40, 38, 36, 34, 32):
        cand = font(BOLD, size)
        if len(wrap(d, headline, cand, tw)) <= 2:
            head_f = cand
            break
    head_f = head_f or font(BOLD, 32)
    lines = wrap(d, headline, head_f, tw)
    lh = head_f.size + 8
    hy = y + 20
    for line in lines:
        d.text((tx, hy), line, font=head_f, fill=INK)
        hy += lh
    # sub-line: shrink until it fits on at most 3 lines
    sub_f = None
    for size in (26, 24, 22):
        cand = font(REGULAR, size)
        if len(wrap(d, sub, cand, tw)) <= 3:
            sub_f = cand
            break
    sub_f = sub_f or font(REGULAR, 22)
    sub_lines = wrap(d, sub, sub_f, tw)
    sy = y + 126
    for line in sub_lines:
        d.text((tx, sy), line, font=sub_f, fill=SUB_INK)
        sy += sub_f.size + 8


def main():
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    # header
    d.rectangle([0, 0, W, HEADER_H], fill=NAVY)
    draw_spaced(d, W // 2, 20, "WORLD NEWS", font(BOLD, 40), GOLD, 10)
    d.text((W // 2, 66), "17 NOVEMBER 2026", font=font(BOLD, 68),
           fill=WHITE, anchor="ma")
    d.rectangle([0, HEADER_H - 4, W, HEADER_H], fill=GOLD)

    # six panels, 2 columns x 3 rows
    for i, (icon, accent, headline, sub) in enumerate(STORIES):
        col, row = i % 2, i // 2
        x = MARGIN + col * (PANEL_W + GAP)
        y = HEADER_H + MARGIN + row * (PANEL_H + GAP)
        draw_panel(d, x, y, icon, accent, headline, sub)

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG")
    print(f"wrote {out} {os.path.getsize(out)} bytes")


if __name__ == "__main__":
    main()
