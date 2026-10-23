"""YouTube channel banner candidates (2560×1440, illustrated style).

YouTube crops the banner per device; only the centre 1546×423 (x 507–2053, y 508–931) is visible everywhere,
desktop shows the full-width 423-px strip, TV shows everything. Wordmark lives in the safe box, the cast
fills the wider strip, the rest is quiet background for TV.

Usage: python -m branding.banner [outdir]   → banner_<name>.png + banner_<name>_preview.png per concept
"""
import math
import os
import sys

import cairo

from engine import style as styles
from engine import text
from engine.core import TAU, ellipse, hexc, mix, rng
from characters import doodle, mochi, noodle, peanut, pickle, pip, pixie, plum

BW, BH = 2560, 1440
SAFE = (507, 508, 1546, 423)          # visible on every device
TABLET = (352, 508, 1855, 423)
DESK = (0, 508, 2560, 423)
CY = 720                              # vertical centre of the strip
INK = hexc("#3a2a1a")
CREAM = hexc("#fffaf2")
PEACH = hexc("#cc6b3d")
ST = styles.get("illustrated")


# ---------------------------------------------------------------- shared pieces
_PAPER = {}


def _paper_tex():
    """Banner-sized version of styles._paper (tiling the 1080×1920 one shows seams)."""
    if "p" not in _PAPER:
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, BW, BH)
        c = cairo.Context(s)
        c.set_source_rgba(*hexc("#f6eedd"))
        c.paint()
        r = rng(5)
        for _ in range(140):
            ellipse(c, r.uniform(0, BW), r.uniform(0, BH), r.uniform(60, 300), r.uniform(40, 220), r.uniform(0, 3))
            c.set_source_rgba(0.82, 0.74, 0.6, r.uniform(0.02, 0.05))
            c.fill()
        for _ in range(16000):
            x, y, a, ln = r.uniform(0, BW), r.uniform(0, BH), r.uniform(0, TAU), r.uniform(2, 9)
            c.move_to(x, y)
            c.line_to(x + math.cos(a) * ln, y + math.sin(a) * ln)
            c.set_source_rgba(0.55, 0.45, 0.3, 0.07)
            c.set_line_width(0.8)
            c.stroke()
        _PAPER["p"] = s
    return _PAPER["p"]


def paper(c, tint="#f6eedd"):
    c.set_source_rgba(*hexc(tint))
    c.paint()
    paper_overlay(c)


def paper_overlay(c):
    c.save()
    c.set_operator(cairo.OPERATOR_MULTIPLY)
    c.set_source_surface(_paper_tex(), 0, 0)
    c.paint()
    c.restore()


def grad(c, y0, y1, stops, x0=0, x1=0):
    g = cairo.LinearGradient(x0, y0, x1, y1)
    for off, col in stops:
        g.add_color_stop_rgba(off, *hexc(col))
    c.set_source(g)


def wash(c, x, y, rx, ry, col, a=0.18, seed=0, n=14):
    """Soft watercolor blot."""
    r = rng(seed)
    for _ in range(n):
        ellipse(c, x + r.uniform(-rx, rx) * 0.4, y + r.uniform(-ry, ry) * 0.4, rx * r.uniform(0.5, 1), ry * r.uniform(0.5, 1),
                r.uniform(0, 3))
        cc = hexc(col)
        c.set_source_rgba(cc[0], cc[1], cc[2], a / n * 3)
        c.fill()


def grass(c, x0, x1, y, n, seed, cols=("#7da35a", "#4f7a3a"), h=(30, 90), alpha=1.0):
    r = rng(seed)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for _ in range(n):
        x = r.uniform(x0, x1)
        hh = r.uniform(*h)
        lean = r.uniform(-0.4, 0.4)
        yy = y + r.uniform(-6, 10)
        c.move_to(x, yy)
        c.curve_to(x + lean * hh * 0.3, yy - hh * 0.5, x + lean * hh * 0.7, yy - hh * 0.8, x + lean * hh, yy - hh)
        col = mix(hexc(cols[0]), hexc(cols[1]), r.random())
        c.set_source_rgba(col[0], col[1], col[2], alpha)
        c.set_line_width(r.uniform(4, 8))
        c.stroke()


def flower(c, x, y, r, col, seed=0):
    rr = rng(seed)
    st = hexc("#4f7a3a")
    c.move_to(x, y)
    c.curve_to(x + 4, y + 30, x - 4, y + 60, x + rr.uniform(-8, 8), y + 90)
    c.set_source_rgba(*st)
    c.set_line_width(4)
    c.stroke()
    for k in range(5):
        a = k * TAU / 5 + rr.uniform(0, 1)
        ellipse(c, x + math.cos(a) * r * 0.6, y + math.sin(a) * r * 0.6, r * 0.55, r * 0.38, a)
        c.set_source_rgba(*hexc(col, 0.9))
        c.fill()
    c.arc(x, y, r * 0.32, 0, TAU)
    c.set_source_rgba(*hexc("#f2c14e"))
    c.fill()


def sparkle(c, x, y, s, col=(1, 0.93, 0.7), a=0.9):
    c.move_to(x, y - s)
    for k in range(4):
        ang = k * TAU / 4
        c.curve_to(x, y, x, y, x + math.cos(ang + TAU / 4) * s, y + math.sin(ang + TAU / 4) * s)
    c.set_source_rgba(col[0], col[1], col[2], a)
    c.fill()


def halo_text(c, txt, x, y, size, col, halo=CREAM, hw=10, bold=True, semibold=False, center=True, halo_a=1.0):
    """Text with a soft cream sticker outline so it reads over any background."""
    w = text.width(txt, size, bold=bold, semibold=semibold)
    x0 = x - w / 2 if center else x
    if hw:
        for k in range(24):
            a = k * TAU / 24
            text.draw(c, txt, x0 + math.cos(a) * hw, y + math.sin(a) * hw, size, halo, halo_a, bold=bold, semibold=semibold)
        for k in range(12):
            a = k * TAU / 12
            text.draw(c, txt, x0 + math.cos(a) * hw * 0.5, y + math.sin(a) * hw * 0.5, size, halo, halo_a,
                      bold=bold, semibold=semibold)
    text.draw(c, txt, x0, y, size, col, bold=bold, semibold=semibold)
    return w


def bouncy_word(c, word, x, y, size, cols, hw=12, tilt=0.06, bounce=10):
    """Wordmark letter by letter: each letter its own color, tiny tilt and bounce."""
    widths = [text.width(ch, size, bold=True) for ch in word]
    track = -size * 0.01
    total = sum(widths) + track * (len(word) - 1)
    xx = x - total / 2
    pos = []
    for i, ch in enumerate(word):
        pos.append((xx, ch, widths[i], (-1) ** i * tilt, -bounce * math.sin(i * 1.3)))
        xx += widths[i] + track
    for passes in ("halo", "ink"):
        for i, (px, ch, w, rot, dy) in enumerate(pos):
            c.save()
            c.translate(px + w / 2, y + dy)
            c.rotate(rot)
            if passes == "halo":
                for k in range(24):
                    a = k * TAU / 24
                    text.draw(c, ch, -w / 2 + math.cos(a) * hw, math.sin(a) * hw, size, CREAM, bold=True)
            else:
                col = cols[i % len(cols)]
                text.draw(c, ch, -w / 2 + 3, 5, size, (col[0] * 0.5, col[1] * 0.4, col[2] * 0.3), 0.35, bold=True)
                text.draw(c, ch, -w / 2, 0, size, col, bold=True)
            c.restore()
    return total


CAST_COLS = [hexc(h) for h in ("#c06a2e", "#e0a14a", "#6f9a3c", "#8a4f8c", "#d27a52", "#4f8a8a", "#c06a2e",
                                "#e0a14a", "#6f9a3c", "#8a4f8c")]


# ---------------------------------------------------------------- concept A: cast parade on a meadow
def concept_parade(c):
    grad(c, 0, BH, [(0, "#f9e9cf"), (0.45, "#fbf1de"), (0.62, "#eef0d2"), (1, "#c9d9a2")])
    c.paint()
    r = rng(4)
    wash(c, 380, 560, 300, 120, "#f4c6a0", 0.25, 1)
    wash(c, 2200, 580, 320, 120, "#f4c6a0", 0.25, 2)
    # far hills
    for k, (yy, col) in enumerate(((880, "#cfdcae"), (930, "#b7cc8c"))):
        c.move_to(0, BH)
        for x in range(0, BW + 40, 40):
            c.line_to(x, yy + 26 * math.sin(x / 260 + k * 2) + 14 * math.sin(x / 90 + k))
        c.line_to(BW, BH)
        c.close_path()
        c.set_source_rgba(*hexc(col))
        c.fill()
    ground = 905
    grad(c, ground - 20, BH, [(0, "#9fbf72"), (1, "#7aa257")])
    c.move_to(0, BH)
    for x in range(0, BW + 40, 40):
        c.line_to(x, ground + 8 * math.sin(x / 140))
    c.line_to(BW, BH)
    c.close_path()
    c.fill()
    grass(c, 0, BW, ground + 8, 900, 3, h=(18, 60))
    for i, x in enumerate((210, 690, 1880, 2380, 2470, 120)):
        flower(c, x, ground - 40 - r.uniform(0, 20), 13, ("#f2a7a0", "#f7d9e3", "#c9a7e0")[i % 3], i)
    # cast, left → right around the wordmark
    mochi.draw(c, ST, 330, ground + 6, 0.62, eyes=0.0, breathe=0.3, tail=0.8)
    pip.draw(c, ST, 330, ground - 205, 0.62, phase=0.5, happy=0.6)
    peanut.draw(c, ST, 720, ground + 4, 0.95, phase=1.0, wiggle=1.0, happy=0.6)
    plum.draw(c, ST, 1960, ground + 2, 0.85, happy=1.0)
    pickle.draw(c, ST, 2270, ground + 6, 0.85, antenna=1.0, happy=0.5)
    pixie.draw(c, ST, 1650, 600, 0.55, flap=1.2, happy=0.5)
    # wordmark
    bouncy_word(c, "TeenyTinyology", BW / 2, 735, 190, CAST_COLS, hw=14)
    halo_text(c, "Teeny creatures. Big stories.", BW / 2, 840, 62, INK, hw=8, semibold=True, bold=False)
    for (x, y, s) in ((800, 600, 18), (1760, 820, 14), (1745, 560, 10), (820, 820, 11)):
        sparkle(c, x, y, s)
    paper_overlay(c)


# ---------------------------------------------------------------- concept B: the magnifying glass
def concept_magnifier(c):
    paper(c, "#fbf3e4")
    wash(c, 900, 720, 520, 200, "#f6d7b8", 0.35, 5, 18)
    wash(c, 1800, 720, 380, 260, "#d8e6bf", 0.35, 6, 18)
    # small "real world" grass line under the lens
    gy = 900
    c.move_to(1250, gy)
    c.curve_to(1500, gy - 10, 2100, gy + 8, 2350, gy - 4)
    c.set_source_rgba(*hexc("#7d9a5a", 0.6))
    c.set_line_width(5)
    c.stroke()
    grass(c, 1260, 2340, gy, 140, 8, h=(10, 30), alpha=0.7)
    # lens
    lx, ly, lr = 1820, 712, 200
    c.save()
    c.arc(lx, ly, lr, 0, TAU)
    c.clip()
    grad(c, ly - lr, ly + lr, [(0, "#fbe9cc"), (0.6, "#e7efcf"), (1, "#a9c47f")])
    c.paint()
    grass(c, lx - lr, lx + lr, ly + 150, 160, 9, h=(30, 110))
    pip.draw(c, ST, lx - 40, ly + 120, 1.15, phase=0.4, happy=0.8)
    c.restore()
    # glass rim + handle (ink + wash)
    c.save()
    c.translate(lx, ly)
    c.rotate(0.75)
    c.rectangle(lr + 8, -24, 210, 48)
    ST.part(c, lambda cc: _handle(cc, lr), _Pal("#9a5b34", "#c8885a", "#5a2f14"), lr + 110, 0, 110, seed=3)
    c.restore()
    c.new_path()
    c.arc(lx, ly, lr + 14, 0, TAU)
    c.arc_negative(lx, ly, lr, TAU, 0)
    c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    c.set_source_rgba(*hexc("#7a8f8f"))
    c.fill()
    c.set_fill_rule(cairo.FILL_RULE_WINDING)
    ST.ink_path(c, lambda cc: cc.arc(lx, ly, lr + 14, 0, TAU), 4, w=4)
    ST.ink_path(c, lambda cc: cc.arc(lx, ly, lr, 0, TAU), 5, w=2.5)
    ellipse(c, lx - 90, ly - 110, 70, 26, -0.6)
    c.set_source_rgba(1, 1, 1, 0.45)
    c.fill()
    # tiny real-size Pip outside the lens (dot on the grass)
    pip.draw(c, ST, 1540, gy - 2, 0.12)
    # wordmark left
    tx = 1030
    halo_text(c, "TeenyTinyology", tx, 745, 178, INK, hw=0)
    text.center(c, "Teeny creatures.", tx - 150, 840, 58, PEACH, semibold=True)
    text.center(c, "Big stories.", tx + 245, 840, 58, hexc("#6f9a3c"), semibold=True)
    # side characters for the desktop strip
    peanut.draw(c, ST, 320, gy, 0.9, phase=0.6, happy=0.6)
    plum.draw(c, ST, 2330, 760, 0.7, happy=1.0)
    c.move_to(2180, 762)
    c.curve_to(2300, 755, 2420, 770, 2560, 750)
    c.set_source_rgba(*hexc("#6a4426"))
    c.set_line_width(12)
    c.stroke()
    paper_overlay(c)


class _Pal:
    def __init__(self, base, light, dark):
        self.base, self.light, self.dark = hexc(base), hexc(light), hexc(dark)


def _handle(c, lr):
    from engine.core import rounded_rect
    rounded_rect(c, lr + 8, -26, 220, 52, 24)


# ---------------------------------------------------------------- concept C: friends hanging off the letters
def concept_letters(c):
    paper(c, "#fbf3e4")
    for i, (x, y, col) in enumerate(((620, 640, "#f6d7b8"), (1280, 820, "#e9dcf0"), (1950, 640, "#d8e6bf"),
                                     (300, 820, "#f9e2b8"), (2280, 780, "#f6d7b8"))):
        wash(c, x, y, 360, 150, col, 0.32, 20 + i, 16)
    size = 215
    word = "TeenyTinyology"
    base = 772
    total = text.width(word, size, bold=True)
    x0 = BW / 2 - total / 2
    # letters in cast colors with a soft drop
    xx = x0
    for i, ch in enumerate(word):
        w = text.width(ch, size, bold=True)
        col = CAST_COLS[i]
        text.draw(c, ch, xx + 5, base + 7, size, (0.35, 0.22, 0.12), 0.18, bold=True)
        text.draw(c, ch, xx, base, size, col, bold=True)
        xx += w
    wT = text.width("T", size, bold=True)
    wTeeny = text.width("Teeny", size, bold=True)
    # Plum perched on the T
    plum.draw(c, ST, x0 + wT * 0.42, base - 152, 0.42, happy=1.0)
    # Pip mid-hop over the y
    c.set_dash([2, 14])
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(x0 + wTeeny - 140, base - 110)
    c.curve_to(x0 + wTeeny - 80, base - 240, x0 + wTeeny + 20, base - 230, x0 + wTeeny + 50, base - 190)
    c.set_source_rgba(*INK[:3], 0.45)
    c.set_line_width(5)
    c.stroke()
    c.set_dash([])
    pip.draw(c, ST, x0 + wTeeny + 80, base - 170, 0.40, ang=0.4, phase=0.2, happy=0.8)
    # Peanut marching along the baseline, Pickle at the end
    peanut.draw(c, ST, x0 - 110, base + 2, 0.62, phase=0.4, happy=0.6)
    pickle.draw(c, ST, x0 + total + 150, base + 4, 0.56, antenna=1.3, happy=0.5)
    # Doodle as a curly underline
    pts = [(x0 + 120 + u * (total - 240), base + 55 + 12 * math.sin(u * 14)) for u in [k / 300 for k in range(301)]]
    doodle.draw_along(c, ST, pts[::-1], 9, happy=0.6)
    text.center(c, "Teeny creatures. Big stories.", BW / 2, base + 128, 54, INK, semibold=True)
    # Mochi napping at the far left, Pixie far right (desktop / TV)
    mochi.draw(c, ST, 260, 905, 0.48, eyes=0.0, tail=0.5)
    pixie.draw(c, ST, 2330, 700, 0.5, flap=0.8, happy=0.5)
    for (x, y, s) in ((x0 + wT + 30, base - 190, 14), (x0 + total - 40, base - 190, 12), (2150, 600, 14)):
        sparkle(c, x, y, s, (0.95, 0.75, 0.45))
    paper_overlay(c)


# ---------------------------------------------------------------- concept D: golden-hour pond
def concept_pond(c):
    grad(c, 0, BH, [(0, "#f7c9a4"), (0.38, "#fbe3c2"), (0.55, "#f6dcb8"), (0.6, "#9cc3c2"), (1, "#5f9198")])
    c.paint()
    c.arc(1280, 610, 120, 0, TAU)
    c.set_source_rgba(1, 0.95, 0.8, 0.6)
    c.fill()
    r = rng(12)
    for k in range(40):  # far tree line
        x = r.uniform(-60, BW + 60)
        s = r.uniform(60, 130)
        c.arc(x, 860 - s * 0.2, s, 0, TAU)
        c.set_source_rgba(*mix(hexc("#9fae7e"), hexc("#7f9466"), r.random()))
        c.fill()
    wy = 862
    grad(c, wy, BH, [(0, "#a9cbc6"), (1, "#5f9198")])
    c.rectangle(0, wy, BW, BH - wy)
    c.fill()
    for k in range(60):  # shimmer
        x, y = r.uniform(0, BW), r.uniform(wy + 10, wy + 300)
        c.move_to(x, y)
        c.line_to(x + r.uniform(30, 90), y)
        c.set_source_rgba(1, 0.96, 0.85, 0.35)
        c.set_line_width(3)
        c.stroke()
    # reeds + Pickle on a lily pad
    for i, x in enumerate((180, 230, 290, 2300, 2360, 2430, 2480)):
        h = r.uniform(260, 420)
        c.move_to(x, BH)
        c.curve_to(x + 10, wy, x + 20, wy - h * 0.5, x + 30 * (1 if i % 2 else -1), wy - h * 0.6)
        c.set_source_rgba(*hexc("#5e7d3e"))
        c.set_line_width(9)
        c.stroke()
    ellipse(c, 2140, wy + 40, 150, 34)
    c.set_source_rgba(*hexc("#6f9a3c"))
    c.fill()
    ST.ink_path(c, lambda cc: ellipse(cc, 2140, wy + 40, 150, 34), 7, w=3)
    pickle.draw(c, ST, 2140, wy + 38, 0.75, antenna=0.8, happy=0.5)
    # Doodle swimming, Pixie dancing above the water
    doodle.draw_along(c, ST, doodle.swim_points(620, wy + 30, 340, 1.0, amp=16), 11, happy=0.6)
    pixie.draw(c, ST, 1900, 640, 0.6, flap=0.6, happy=0.6)
    pixie.draw(c, ST, 700, 640, 0.4, flap=2.3)
    c.save()
    c.translate(1280, 0)
    soft_card(c, -560, 610, 1120, 300)
    c.restore()
    bouncy_word(c, "TeenyTinyology", BW / 2, 765, 180, CAST_COLS, hw=0, tilt=0.04, bounce=8)
    text.center(c, "Teeny creatures. Big stories.", BW / 2, 860, 58, INK, semibold=True)
    for (x, y, s) in ((1940, 520, 14), (700, 500, 10), (1700, 650, 9)):
        sparkle(c, x, y, s)
    paper_overlay(c)


def soft_card(c, x, y, w, h):
    from engine.scene import soft_bubble
    soft_bubble(c, x, y, w, h, 1.0, r=80, shadow=0.3)


# ================================================================ round 2: gentle — just the name + a few friends
COCOA = hexc("#5e4636")
NAME = "TeenyTinyology"


def soft_bg(c, top, bottom, washes=()):
    grad(c, 0, BH, [(0, top), (1, bottom)])
    c.paint()
    for i, (x, y, rx, ry, col) in enumerate(washes):
        wash(c, x, y, rx, ry, col, 0.16, 40 + i, 16)


def name(c, x=BW / 2, y=772, size=178, col=COCOA):
    """The wordmark: one calm colour, no outline, no tagline. Shrinks to stay inside the phone-safe box."""
    size = min(size, size * 1300 / text.width(NAME, size, semibold=True))
    w = text.width(NAME, size, semibold=True)
    text.draw(c, NAME, x - w / 2, y, size, col, semibold=True)
    return x - w / 2, w


def haze(c, a=0.10):
    """Lay a thin cream veil over everything so the characters sit quietly in the page."""
    c.set_source_rgba(*CREAM[:3], a)
    c.paint()


def ground_line(c, x0, x1, y, seed, col="#8fa77a", blades=60):
    c.move_to(x0, y)
    c.curve_to(x0 + (x1 - x0) * 0.3, y - 5, x0 + (x1 - x0) * 0.7, y + 5, x1, y)
    c.set_source_rgba(*hexc(col, 0.55))
    c.set_line_width(4)
    c.stroke()
    grass(c, x0 + 20, x1 - 20, y + 2, blades, seed, cols=("#a9bf8e", "#7f9a6a"), h=(10, 34), alpha=0.75)


def concept_nap(c):
    """Mochi napping beside the name, Pip resting on the last letter."""
    soft_bg(c, "#fbf5ea", "#f4eadb", ((700, 760, 380, 150, "#f3d9c4"), (1900, 700, 320, 140, "#e6e2cf")))
    x0, w = name(c)
    ground_line(c, 150, 640, 880, 1)
    mochi.draw(c, ST, 400, 880, 0.5, eyes=0.0, breathe=0.2, tail=0.6)
    pip.draw(c, ST, 340, 800, 0.3, phase=0.3, happy=0.4)
    haze(c)
    paper_overlay(c)


def concept_stroll(c):
    """A quiet line of friends walking along a thin grass line under the name."""
    soft_bg(c, "#f9f6ee", "#eef0e2", ((900, 700, 420, 150, "#ece4d0"), (1800, 760, 420, 150, "#e2e9d6")))
    name(c, y=740, size=170)
    ground_line(c, 120, 2440, 900, 2, blades=220)
    peanut.draw(c, ST, 560, 900, 0.62, phase=0.8, happy=0.4)
    pip.draw(c, ST, 330, 898, 0.38, phase=0.2, happy=0.4)
    pickle.draw(c, ST, 1990, 902, 0.6, antenna=0.9, happy=0.4)
    pixie.draw(c, ST, 2300, 650, 0.42, flap=0.9, happy=0.3)
    haze(c)
    paper_overlay(c)


def concept_perch(c):
    """Pale sage page; Plum perched on the T, a mayfly drifting past the end of the name."""
    soft_bg(c, "#f3f4ea", "#e7ebdb", ((1280, 720, 700, 170, "#f6efe0"),))
    x0, w = name(c, y=800, size=180, col=hexc("#55503a"))
    plum.draw(c, ST, x0 + 46, 694, 0.4, happy=0.6)
    pixie.draw(c, ST, x0 + w + 170, 650, 0.45, flap=1.1, happy=0.3)
    haze(c, 0.12)
    paper_overlay(c)


def concept_peek(c):
    """Blush-cream page; Pip and Peanut meet in the middle of the strip below the name, Mochi dozes far left."""
    soft_bg(c, "#fcf4ee", "#f5e6dc", ((1280, 700, 650, 180, "#f7e3d6"),))
    name(c, y=735, size=175)
    ground_line(c, 1000, 1560, 880, 4, blades=50)
    pip.draw(c, ST, 1190, 878, 0.34, phase=0.1, happy=0.5)
    c.save()
    c.translate(1430, 0)
    c.scale(-1, 1)
    peanut.draw(c, ST, 0, 880, 0.5, walking=False, happy=0.5)
    c.restore()
    mochi.draw(c, ST, 330, 900, 0.42, eyes=0.0, tail=0.3)
    plum.draw(c, ST, 2250, 900, 0.55, happy=0.6)
    haze(c)
    paper_overlay(c)


# ================================================================ round 3: grown-up — serif name, quiet field-notebook characters
class _Quiet(styles.Illustrated):
    faces = False          # no blush / smiles — characters keep their eyes but lose the cartoon expressions


QUIET = _Quiet()
REAL = styles.get("real")
SEPIA = hexc("#4a3a2e")


def serif_name(c, fam, y, size=170, track=0.04, col=SEPIA, x=BW / 2, max_w=1250):
    """Letter-spaced serif wordmark, centred, shrunk to fit the phone-safe box."""
    def total(sz):
        return sum(text.width(ch, sz, fam=fam, semibold=True) for ch in NAME) + sz * track * (len(NAME) - 1)
    size = min(size, size * max_w / total(size))
    w = total(size)
    xx = x - w / 2
    for ch in NAME:
        text.draw(c, ch, xx, y, size, col, fam=fam, semibold=True)
        xx += text.width(ch, size, fam=fam, semibold=True) + size * track
    return x - w / 2, w, size


def flat(c, tint):
    """Plain page colour — the paper grain goes on once, at the end (paper_overlay)."""
    c.set_source_rgba(*hexc(tint))
    c.paint()


def ink_rule(c, x0, x1, y, a=0.35, seed=1):
    r = rng(seed)
    pts = [(x, y + r.uniform(-0.8, 0.8)) for x in range(int(x0), int(x1) + 1, 24)]
    QUIET.line(c, pts, 2.2, SEPIA, a)


def fine_grass(c, x0, x1, y, n, seed, h=(14, 44), a=0.55):
    """Sparse pen-line grass, not painted blades."""
    r = rng(seed)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for _ in range(n):
        x = r.uniform(x0, x1)
        hh = r.uniform(*h)
        lean = r.uniform(-0.35, 0.35)
        c.move_to(x, y)
        c.curve_to(x + lean * hh * 0.3, y - hh * 0.5, x + lean * hh * 0.7, y - hh * 0.8, x + lean * hh, y - hh)
        col = mix(hexc("#7d8f62"), hexc("#55603f"), r.random())
        c.set_source_rgba(col[0], col[1], col[2], a)
        c.set_line_width(r.uniform(1.6, 2.8))
        c.stroke()


def concept_notebook(c):
    """Field-notebook page: serif name, a single pen line with a few small residents spaced along it."""
    flat(c, "#f7f1e5")
    serif_name(c, "Cormorant Garamond", 760, 190)
    gy = 890
    ink_rule(c, 140, 2420, gy, 0.3)
    fine_grass(c, 140, 2420, gy, 70, 3)
    pip.draw(c, QUIET, 420, gy, 0.3, phase=0.4)
    peanut.draw(c, QUIET, 760, gy, 0.42, phase=0.8)
    pickle.draw(c, QUIET, 1880, gy, 0.42, antenna=0.9)
    pixie.draw(c, QUIET, 2230, 690, 0.32, flap=0.9)
    paper_overlay(c)


def concept_margin(c):
    """Editorial: name set left, one resident on a tall stem on the right, a mayfly passing."""
    flat(c, "#f5f2ea")
    x0, w, size = serif_name(c, "EB Garamond", 770, 150, track=0.02, x=1060, max_w=1100)
    # tall grass stem with Pickle on it
    sx, sy = 1880, 930
    c.move_to(sx, sy)
    c.curve_to(sx + 6, sy - 120, sx + 30, sy - 220, sx + 80, sy - 300)
    c.set_source_rgba(*hexc("#66724a", 0.8))
    c.set_line_width(4)
    c.stroke()
    ellipse(c, sx + 60, sy - 180, 70, 14, -0.9)
    c.set_source_rgba(*hexc("#8b9a6a", 0.6))
    c.fill()
    fine_grass(c, 1700, 2100, sy, 40, 5, h=(20, 70))
    pickle.draw(c, QUIET, sx + 10, sy - 120, 0.42, ang=-0.55, antenna=0.7)
    pixie.draw(c, QUIET, 2250, 640, 0.3, flap=1.4)
    peanut.draw(c, QUIET, 380, 905, 0.36, phase=0.5)
    paper_overlay(c)


def concept_plate(c):
    """Natural-history plate: realistic drawings of the residents in a calm row under the name."""
    flat(c, "#f6f0e2")
    serif_name(c, "Cormorant Garamond", 740, 180)
    gy = 895
    ink_rule(c, 900, 1660, gy + 12, 0.25)
    pip.draw(c, REAL, 1000, gy, 0.3)
    peanut.draw(c, REAL, 1250, gy, 0.42, walking=False)
    pickle.draw(c, REAL, 1530, gy, 0.4, antenna=0.6)
    paper_overlay(c)


def concept_dusk(c):
    """Soft evening wash, name in Lora, Plum on a bare twig and a mayfly — very still."""
    grad(c, 0, BH, [(0, "#efe6da"), (0.5, "#f3ebe0"), (1, "#e6e3d6")])
    c.paint()
    wash(c, 1280, 700, 900, 200, "#f2dccb", 0.12, 50, 18)
    serif_name(c, "Lora", 765, 150, track=0.03)
    # twig from the right edge
    QUIET.line(c, [(2560, 760), (2380, 772), (2240, 790), (2150, 800)], 9, hexc("#5e4a3a"), 0.9)
    QUIET.line(c, [(2300, 778), (2260, 740), (2245, 715)], 5, hexc("#5e4a3a"), 0.9)
    plum.draw(c, QUIET, 2330, 776, 0.55)
    pixie.draw(c, QUIET, 420, 650, 0.32, flap=0.6)
    paper_overlay(c)


# ================================================================ round 4: banner K in the logo's midnight palette (owner chose K + midnight logo)
NAVY, NAVY_LIFT, CREAM_M, GOLD = hexc("#1e2a3a"), hexc("#2a3a4f"), hexc("#f3ead8"), hexc("#f2b84b")


def midnight_name(c, y, hyphens=False, size=150, max_w=1250):
    """One-line logo wordmark: cream 'teeny tiny', gold 'ology' whose o is the logo's lens."""
    from branding.logo import lens   # logo.py imports this module, so import lazily
    fam, kw = "Outfit", dict(fam="Outfit", semibold=True)
    head = "teeny-tiny-" if hyphens else "teeny tiny "
    def total(sz):   # + room for the lens handle, which reaches down-left into the gap
        return text.width(head, sz, **kw) + sz * 0.22 + text.width("ology", sz, **kw)
    size = min(size, size * max_w / total(size))
    x = BW / 2 - total(size) / 2
    text.draw(c, head, x, y, size, CREAM_M, **kw)
    x += text.width(head, size, **kw) + size * 0.22
    ow = text.width("o", size, **kw)
    xh = size * 0.5
    r = ow * 0.42
    lens(c, x + ow / 2, y - xh / 2 - 2, r, size * 0.15, GOLD, handle=-1)
    text.draw(c, "logy", x + ow, y, size, GOLD, **kw)


def plate_row(c, gy):
    """K's residents on a soft lighter pool so the dark drawings still read on navy."""
    g = cairo.RadialGradient(1265, gy - 30, 10, 1265, gy - 30, 420)
    g.add_color_stop_rgba(0, *NAVY_LIFT[:3], 1)
    g.add_color_stop_rgba(1, *NAVY_LIFT[:3], 0)
    c.save()
    c.translate(0, gy - 30)
    c.scale(1, 0.32)
    c.translate(0, -(gy - 30))
    c.arc(1265, gy - 30, 420, 0, TAU)
    c.set_source(g)
    c.fill()
    c.restore()
    c.move_to(900, gy + 12)
    c.line_to(1660, gy + 12)
    c.set_source_rgba(*GOLD[:3], 0.35)
    c.set_line_width(2)
    c.stroke()
    pip.draw(c, REAL, 1000, gy, 0.3)
    peanut.draw(c, REAL, 1250, gy, 0.42, walking=False)
    pickle.draw(c, REAL, 1530, gy, 0.4, antenna=0.6)


def concept_midnight(c, hyphens=False):
    flat(c, "#1e2a3a")
    midnight_name(c, 750, hyphens)
    plate_row(c, 895)


CONCEPTS = {"m1_midnight": concept_midnight, "m2_midnight_hyphens": lambda c: concept_midnight(c, True)}
# round 3 (owner chose K): concept_notebook, concept_margin, concept_plate, concept_dusk

# round 1 (owner: too colourful / busy): concept_parade, concept_magnifier, concept_letters, concept_pond
# round 2 (owner: too childish): concept_nap, concept_stroll, concept_perch, concept_peek


# ---------------------------------------------------------------- previews
def preview(src, out):
    """Full banner with crop guides + how it looks on desktop / tablet / phone."""
    pw = 1600
    k = pw / BW
    full_h = int(BH * k)
    rows = [("TV / full image", None), ("Desktop", DESK), ("Tablet", TABLET), ("Phone (safe area)", SAFE)]
    strip_h = [full_h] + [int(r[3] * pw / r[2]) for _, r in rows[1:]]
    head = 56
    H = sum(strip_h) + head * len(rows) + 40
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, pw + 80, H)
    c = cairo.Context(s)
    c.set_source_rgba(*hexc("#1f1c1a"))
    c.paint()
    y = 20
    for (name, box), sh in zip(rows, strip_h):
        text.draw(c, name, 40, y + 40, 32, (0.9, 0.88, 0.85), semibold=True)
        y += head
        c.save()
        c.translate(40, y)
        if box is None:
            c.scale(k, k)
            c.set_source_surface(src, 0, 0)
            c.paint()
            for (bx, by, bw, bh), col in ((DESK, (0.3, 0.7, 1)), (TABLET, (1, 0.8, 0.2)), (SAFE, (1, 0.3, 0.4))):
                c.rectangle(bx, by, bw, bh)
                c.set_source_rgba(*col, 0.9)
                c.set_line_width(4 / k)
                c.stroke()
        else:
            kk = pw / box[2]
            c.scale(kk, kk)
            c.set_source_surface(src, -box[0], -box[1])
            c.rectangle(0, 0, box[2], box[3])
            c.fill()
        c.restore()
        y += sh
    s.write_to_png(out)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join("branding", "out")
    os.makedirs(out, exist_ok=True)
    text.set_family("Nunito")
    for name, fn in CONCEPTS.items():
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, BW, BH)
        c = cairo.Context(s)
        fn(c)
        p = os.path.join(out, f"banner_{name}.png")
        s.write_to_png(p)
        preview(s, os.path.join(out, f"banner_{name}_preview.png"))
        print("wrote", p, f"{os.path.getsize(p) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
