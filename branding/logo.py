"""Profile-picture (avatar) candidates, 800×800, matching banner K (realistic drawings, serif, cream paper).

YouTube shows the avatar as a circle, often only 48–98 px wide, so each mark is one clear shape.

Usage: python -m branding.logo [outdir]            → logo_<name>.png per concept + logo_sizes.png (real sizes)
       python -m branding.logo outdir final      → the chosen profile picture (800 + 2048 px)
       python -m branding.logo outdir palettes   → palette comparison sheet
"""
import math
import os
import sys

import cairo

from engine import style as styles
from engine import text
from engine.core import TAU, ellipse, hexc, rng
from characters import peanut, pickle, pip
from branding.banner import SEPIA, flat

S = 800
REAL = styles.get("real")
PAPER = "#f6f0e2"
SERIF = "Cormorant Garamond"


def paper_grain(c):
    if "g" not in _G:
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, S, S)
        g = cairo.Context(s)
        g.set_source_rgba(*hexc("#f6eedd"))
        g.paint()
        r = rng(7)
        for _ in range(26):
            ellipse(g, r.uniform(0, S), r.uniform(0, S), r.uniform(60, 220), r.uniform(40, 160), r.uniform(0, 3))
            g.set_source_rgba(0.82, 0.74, 0.6, r.uniform(0.02, 0.04))
            g.fill()
        for _ in range(2600):
            x, y, a, ln = r.uniform(0, S), r.uniform(0, S), r.uniform(0, TAU), r.uniform(2, 8)
            g.move_to(x, y)
            g.line_to(x + math.cos(a) * ln, y + math.sin(a) * ln)
            g.set_source_rgba(0.55, 0.45, 0.3, 0.06)
            g.set_line_width(0.8)
            g.stroke()
        _G["g"] = s
    c.save()
    c.set_operator(cairo.OPERATOR_MULTIPLY)
    c.set_source_surface(_G["g"], 0, 0)
    c.paint()
    c.restore()


_G = {}


def ring(c, r, w=3.0, a=0.8):
    c.arc(S / 2, S / 2, r, 0, TAU)
    c.set_source_rgba(*SEPIA[:3], a)
    c.set_line_width(w)
    c.stroke()


def arc_text(c, txt, r, size, start_deg=-90, track=0.18, bottom=False):
    """Letters along a circle, centred on start_deg (top = -90). bottom=True reads left→right along the bottom."""
    widths = [text.width(ch, size, fam=SERIF, semibold=True) for ch in txt]
    total = sum(widths) + size * track * (len(txt) - 1)
    ang_total = total / r
    a = math.radians(start_deg) + (ang_total / 2 if bottom else -ang_total / 2)
    for ch, w in zip(txt, widths):
        da = (w + size * track) / r
        mid = a + (-1 if bottom else 1) * (w / 2) / r
        c.save()
        c.translate(S / 2 + math.cos(mid) * r, S / 2 + math.sin(mid) * r)
        c.rotate(mid + (-math.pi / 2 if bottom else math.pi / 2))
        text.draw(c, ch, -w / 2, size * 0.32, size, SEPIA, fam=SERIF, semibold=True)
        c.restore()
        a += (-1 if bottom else 1) * da


def sprig(c, x, y, s=1.0, flip=1):
    """Tiny ink grass sprig used as a divider."""
    for k, (dx, h, lean) in enumerate(((0, 34, -0.2), (8, 26, 0.35), (-8, 22, -0.5))):
        c.move_to(x + dx * flip * s, y)
        c.curve_to(x + (dx + lean * 8) * flip * s, y - h * 0.5 * s, x + (dx + lean * 14) * flip * s, y - h * 0.8 * s,
                   x + (dx + lean * 18) * flip * s, y - h * s)
        c.set_source_rgba(*hexc("#66724a", 0.85))
        c.set_line_width(2.4 * s)
        c.stroke()


# ---------------------------------------------------------------- concepts
def logo_flea(c):
    """Just Pip, drawn like a specimen plate, on cream."""
    flat(c, PAPER)
    REAL.shadow(c, 400, 560, 230, 20, 0.16)
    pip.draw(c, REAL, 400, 555, 1.55)
    paper_grain(c)


def logo_seal(c):
    """Specimen seal: name around the rim, Pip in the middle."""
    flat(c, PAPER)
    ring(c, 372, 3, 0.75)
    ring(c, 286, 1.6, 0.5)
    arc_text(c, "TEENY-TINY-OLOGY", 322, 60, start_deg=-90, track=0.3)
    for side in (-1, 1):
        c.arc(400 + side * 300, 400 + 120, 5, 0, TAU)
        c.set_source_rgba(*SEPIA[:3], 0.7)
        c.fill()
    sprig(c, 400, 676, 1.0)
    pip.draw(c, REAL, 400, 500, 0.95)
    paper_grain(c)


def logo_monogram(c):
    """Serif 'T' with Pip standing on the crossbar."""
    flat(c, PAPER)
    size = 600
    w = text.width("T", size, fam=SERIF, semibold=True)
    base = 690
    text.draw(c, "T", 400 - w / 2, base, size, SEPIA, fam=SERIF, semibold=True)
    top = base - size * 0.63
    pip.draw(c, REAL, 470, top + 6, 0.62)
    paper_grain(c)


def logo_lens(c):
    """Fine ink lens ring with Pip inside — 'looking closer'."""
    flat(c, PAPER)
    c.arc(400, 400, 300, 0, TAU)
    c.set_source_rgba(*hexc("#eef0e0", 1))
    c.fill()
    ring(c, 300, 7, 0.85)
    ring(c, 286, 1.4, 0.4)
    c.save()
    c.arc(400, 400, 286, 0, TAU)
    c.clip()
    pip.draw(c, REAL, 395, 540, 1.25)
    ellipse(c, 300, 240, 90, 26, -0.7)
    c.set_source_rgba(1, 1, 1, 0.35)
    c.fill()
    c.restore()
    paper_grain(c)


def logo_trio(c):
    """Three residents, small, side by side on a pen line (the banner in miniature)."""
    flat(c, PAPER)
    gy = 470
    QUIET_LINE = [(130, gy + 6), (670, gy + 6)]
    c.move_to(*QUIET_LINE[0])
    c.line_to(*QUIET_LINE[1])
    c.set_source_rgba(*SEPIA[:3], 0.3)
    c.set_line_width(2)
    c.stroke()
    pip.draw(c, REAL, 205, gy, 0.48)
    peanut.draw(c, REAL, 395, gy, 0.62, walking=False)
    pickle.draw(c, REAL, 610, gy, 0.55, antenna=0.6)
    w = text.width("TTO", 64, fam=SERIF, semibold=True)
    paper_grain(c)



# ================================================================ round 2: modern, flat, lettering + simple silhouettes
# (owner: round 1 too plain/old, realistic flea unpleasant, wants lettering)
SANS = "Outfit"
CREAM2 = hexc("#f7f0e3")
SAGE = hexc("#55684c")
TERRA = hexc("#c46f4c")
INKD = hexc("#2f3a2a")


def bg(c, col):
    c.set_source_rgba(*col)
    c.paint()


def ant(c, x, y, s, col, ang=0.0, step=0.0):
    """Flat ant silhouette, side view facing right; (x, y) = feet line centre, body length ~ 200*s."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.set_source_rgba(*col)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    ellipse(c, -62, -34, 40, 28, -0.25)       # gaster
    c.fill()
    ellipse(c, -16, -36, 9, 9)                # petiole
    c.fill()
    ellipse(c, 16, -40, 26, 13, 0.12)         # thorax
    c.fill()
    ellipse(c, 58, -46, 19, 17)               # head
    c.fill()
    c.set_line_width(5.5)
    for i, hx in enumerate((-2, 16, 32)):     # legs
        sw = 8 * math.sin(step + i * 2.1)
        c.move_to(hx, -36)
        c.line_to(hx - 18 + i * 10 + sw, -16)
        c.line_to(hx - 26 + i * 18 + sw, 0)
        c.stroke()
    c.set_line_width(4.5)                     # antennae (elbowed)
    c.move_to(66, -60)
    c.line_to(80, -88)
    c.line_to(104, -80)
    c.stroke()
    c.move_to(60, -61)
    c.line_to(68, -92)
    c.line_to(90, -96)
    c.stroke()
    c.restore()


def word(c, txt, x, y, size, col, fam=SANS, weight="semibold", center=True, track=0.0):
    kw = {"bold": weight == "bold", "semibold": weight == "semibold"}
    ws = [text.width(ch, size, fam=fam, **kw) for ch in txt]
    total = sum(ws) + size * track * (len(txt) - 1)
    xx = x - total / 2 if center else x
    x0 = xx
    for ch, w in zip(txt, ws):
        text.draw(c, ch, xx, y, size, col, fam=fam, **kw)
        xx += w + size * track
    return x0, total


def logo_lens_o(c):
    """'tto' — the o is a magnifying glass with a tiny ant inside."""
    bg(c, SAGE)
    size = 330
    tw = text.width("tt", size, fam=SANS, semibold=True) + size * 0.05
    r = 98
    gap = 26
    total = tw + gap + 2 * r
    x0 = 400 - total / 2 - 30
    base = 515
    word(c, "tt", x0, base, size, CREAM2, center=False, track=0.05)
    ox, oy = x0 + tw + gap + r, base - r - 4
    c.arc(ox, oy, r, 0, TAU)
    c.set_source_rgba(*CREAM2)
    c.set_line_width(34)
    c.stroke()
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(ox + r * 0.78, oy + r * 0.78)
    c.line_to(ox + r * 1.45, oy + r * 1.45)
    c.set_line_width(40)
    c.stroke()
    ant(c, ox + 4, oy + 30, 0.42, TERRA, step=0.6)


def logo_one_ant(c):
    """A big empty circle and one teeny ant crossing it, with its dotted trail."""
    bg(c, TERRA)
    r = rng(3)
    pts = [(170 + k * 22, 520 - 70 * math.sin(k * 0.22) + 6 * math.sin(k * 1.7)) for k in range(14)]
    for (x, y) in pts:
        c.arc(x, y, 5, 0, TAU)
        c.set_source_rgba(*CREAM2[:3], 0.6)
        c.fill()
    ant(c, 545, 520, 0.62, CREAM2, ang=-0.12, step=1.0)


def logo_stack(c):
    """Stacked name in clean sans; a tiny ant walks along the top of 'teeny'."""
    bg(c, CREAM2)
    size = 168
    lines = ["teeny", "tiny", "ology"]
    lh = size * 0.92
    y0 = 400 - lh + size * 0.32
    widths = [text.width(t, size, fam=SANS, semibold=True) for t in lines]
    x0 = 400 - max(widths) / 2
    cols = [SAGE, SAGE, TERRA]
    for i, t in enumerate(lines):
        word(c, t, x0, y0 + i * lh, size, cols[i], center=False)
    xh = size * 0.5
    ant(c, x0 + widths[0] * 0.55, y0 - xh + 2, 0.36, INKD, step=0.3)


def logo_leaf(c):
    """One flat leaf, one ant walking along the midrib."""
    bg(c, CREAM2)
    c.save()
    c.translate(400, 420)
    c.rotate(-0.42)
    c.move_to(-290, 0)
    c.curve_to(-150, -170, 150, -170, 290, 0)
    c.curve_to(150, 170, -150, 170, -290, 0)
    c.set_source_rgba(*SAGE)
    c.fill()
    c.move_to(-330, 18)
    c.line_to(250, 0)
    c.set_source_rgba(*hexc("#7f9470"))
    c.set_line_width(8)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.stroke()
    ant(c, 30, -4, 0.62, CREAM2, step=0.9)
    c.restore()


def logo_t_stem(c):
    """A capital T grown from a grass stem and a leaf; an ant climbing up."""
    bg(c, SAGE)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(400, 640)
    c.curve_to(396, 520, 404, 360, 400, 240)
    c.set_source_rgba(*CREAM2)
    c.set_line_width(58)
    c.stroke()
    c.move_to(200, 232)
    c.curve_to(300, 196, 500, 196, 600, 232)
    c.curve_to(500, 262, 300, 262, 200, 232)
    c.fill()
    ant(c, 380, 520, 0.36, TERRA, ang=-math.pi / 2 + 0.03, step=0.4)


# ================================================================ round 3: variations of A (tt + lens) and C (stacked name)
SEPIA2 = hexc("#4a3a2e")
PAPERC = hexc("#f6f0e2")
SERIF2 = "Cormorant Garamond"


def lens(c, ox, oy, r, w, col, handle=1, glass=None):
    """Magnifying-glass ring; handle=1 points down-right, -1 down-left."""
    if glass:
        c.arc(ox, oy, r, 0, TAU)
        c.set_source_rgba(*glass)
        c.fill()
    c.arc(ox, oy, r, 0, TAU)
    c.set_source_rgba(*col)
    c.set_line_width(w)
    c.stroke()
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(ox + handle * r * 0.78, oy + r * 0.78)
    c.line_to(ox + handle * r * 1.45, oy + r * 1.45)
    c.set_line_width(w * 1.18)
    c.stroke()


def tt_lens(bgc, fg, antc, fam=SANS, letters="tt", size=330, r=98, w=34, glass=None, track=0.05):
    def draw(c):
        bg(c, bgc)
        kw = dict(fam=fam, semibold=True)
        tw = sum(text.width(ch, size, **kw) for ch in letters) + size * track * (len(letters) - 1)
        gap = 26
        x0 = 400 - (tw + gap + 2 * r) / 2 - 30
        base = 515
        word(c, letters, x0, base, size, fg, fam=fam, center=False, track=track)
        ox, oy = x0 + tw + gap + r, base - r - 4
        lens(c, ox, oy, r, w, fg, glass=glass)
        ant(c, ox + 4, oy + 30, 0.42 * r / 98, antc, step=0.6)
    return draw


def stack(bgc, cols, antc, fam=SANS, ant_on="teeny", lens_o=False, size=168, hyphens=False, align="left", lens_ant=True):
    def draw(c):
        bg(c, bgc)
        kw = dict(fam=fam, semibold=True)
        lines = ["teeny-", "tiny-", "ology"] if hyphens else ["teeny", "tiny", "ology"]
        lh = size * 0.92
        y0 = 400 - lh + size * 0.32
        widths = [text.width(t, size, **kw) for t in lines]
        mw = max(widths)
        xs = [400 - mw / 2 + ((mw - w) if align == "right" else 0) for w in widths]
        xh = size * 0.5
        for i, t in enumerate(lines):
            y = y0 + i * lh
            if lens_o and t == "ology":
                ow = text.width("o", size, **kw)
                r = ow * 0.42
                lens(c, xs[i] + ow / 2, y - xh / 2 - 2, r, size * 0.15, cols[i], handle=-1)
                word(c, "logy", xs[i] + ow, y, size, cols[i], fam=fam, center=False)
                if lens_ant:
                    ant(c, xs[i] + ow / 2 + 3, y - xh / 2 + r * 0.3, r / 200, antc, step=0.4)
            else:
                word(c, t, xs[i], y, size, cols[i], fam=fam, center=False)
        if ant_on == "tiny_end":  # walking along the baseline in the space after "tiny"
            ant(c, xs[1] + widths[1] + size * 0.42, y0 + lh, 0.36 * size / 168, antc, step=0.3)
        elif ant_on:
            i = {"teeny": 0, "tiny": 1, "ology": 2}[ant_on]
            frac = {"teeny": 0.3, "tiny": 0.62, "ology": 0.62}[ant_on]
            top = y0 + i * lh - (xh if ant_on != "tiny" else xh) + 2
            ant(c, xs[i] + widths[i] * frac, top, 0.36 * size / 168, antc, step=0.3)
    return draw


CONCEPTS = {
    "a1_sage": tt_lens(SAGE, CREAM2, TERRA),
    "a2_paper": tt_lens(PAPERC, SEPIA2, TERRA),
    "a3_terracotta": tt_lens(TERRA, CREAM2, SAGE),
    "a4_serif": tt_lens(PAPERC, SEPIA2, TERRA, fam=SERIF2, size=360, w=26),
    "a5_caps": tt_lens(SAGE, CREAM2, TERRA, letters="TT", size=300, r=92),
    "a6_glass": tt_lens(INKD, CREAM2, TERRA, glass=hexc("#e9e2cf", 0.18)),
    "c1_ant_walking": stack(CREAM2, [SAGE, SAGE, TERRA], INKD, ant_on="tiny_end"),
    "c2_lens_o": stack(CREAM2, [SAGE, SAGE, TERRA], INKD, ant_on=None, lens_o=True),
    "c3_sage": stack(SAGE, [CREAM2, CREAM2, hexc("#f0b48f")], TERRA, ant_on=None, lens_o=True),
    "c4_serif": stack(PAPERC, [SEPIA2, SEPIA2, TERRA], INKD, fam=SERIF2, ant_on="tiny_end", size=190),
    "c5_hyphens": stack(CREAM2, [SAGE, SAGE, TERRA], INKD, ant_on="tiny_end", hyphens=True, size=150),
    "c6_terracotta": stack(TERRA, [CREAM2, CREAM2, INKD], CREAM2, ant_on=None, lens_o=True),
}
# round 2 (owner liked lens_o + stack): logo_lens_o, logo_one_ant, logo_stack, logo_leaf, logo_t_stem



def circle(src, d):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, d, d)
    c = cairo.Context(s)
    c.arc(d / 2, d / 2, d / 2, 0, TAU)
    c.clip()
    c.scale(d / S, d / S)
    c.set_source_surface(src, 0, 0)
    c.get_source().set_filter(cairo.FILTER_BEST)
    c.paint()
    return s


def sizes_sheet(surfs, out):
    """Every concept as YouTube shows it: channel page (160), watch page (98), comments (48), on light and dark."""
    ds = (160, 98, 48)
    cw = 300 + sum(ds) + 40 * len(ds)
    rowh = 200
    W, H = cw * 2, 80 + rowh * len(surfs)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(s)
    for half, bg, fg in ((0, (1, 1, 1), (0.1, 0.1, 0.1)), (1, (0.06, 0.06, 0.06), (0.95, 0.95, 0.95))):
        c.rectangle(half * cw, 0, cw, H)
        c.set_source_rgb(*bg)
        c.fill()
        text.draw(c, "light mode" if half == 0 else "dark mode", half * cw + 30, 50, 30, fg, fam="Nunito", semibold=True)
        for i, (name, src) in enumerate(surfs):
            y = 80 + i * rowh
            text.draw(c, name, half * cw + 30, y + 100, 30, fg, fam="Nunito", semibold=True)
            x = half * cw + 300
            for d in ds:
                c.set_source_surface(circle(src, d), x, y + (rowh - d) / 2 - 10)
                c.paint()
                x += d + 40
    s.write_to_png(out)


def _render(fn):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, S, S)
    fn(cairo.Context(s))
    return s


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join("branding", "out")
    os.makedirs(out, exist_ok=True)
    if len(sys.argv) > 2 and sys.argv[2] == "final":
        export_final(out)
        sizes_sheet([("final", _render(FINAL))], os.path.join(out, "profile_sizes.png"))
        print("wrote profile_800.png, profile_2048.png, profile_sizes.png to", out)
        return
    if len(sys.argv) > 2 and sys.argv[2] == "palettes":
        palette_sheet(os.path.join(out, "logo_palettes.png"))
        return
    surfs = []
    for name, fn in CONCEPTS.items():
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, S, S)
        fn(cairo.Context(s))
        s.write_to_png(os.path.join(out, f"logo_{name}.png"))
        surfs.append((name.split("_", 1)[1], s))
    sizes_sheet(surfs, os.path.join(out, "logo_sizes.png"))
    print("wrote", len(surfs), "logos + logo_sizes.png to", out)



# ================================================================ palette exploration (owner: didn't like sage/terracotta/cream)
PALETTES = {  # name: (background, letters, accent = ant / "ology")
    "ink & mustard": ("#fbf7ef", "#1f2a36", "#e0a33a"),
    "midnight": ("#1e2a3a", "#f3ead8", "#f2b84b"),
    "dusty blue": ("#b8cdd8", "#22364a", "#c8603f"),
    "blush": ("#f4dcd3", "#5e3436", "#3f6b5c"),
    "lavender": ("#dcd5ec", "#38305c", "#e0844f"),
    "mustard": ("#e8b84a", "#2a2723", "#fdf6e7"),
    "mint": ("#d3e8da", "#1f3f33", "#e06a55"),
    "deep teal": ("#1f5a5e", "#f6efe0", "#f4b19a"),
    "charcoal": ("#262626", "#f2efe6", "#c9dc72"),
    "black & white": ("#ffffff", "#111111", "#111111"),
}


def palette_sheet(out):
    cell, pad, lab = 300, 16, 260
    W = lab + 2 * (cell + pad) + pad
    H = 70 + len(PALETTES) * (cell + pad)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(s)
    c.set_source_rgb(0.93, 0.93, 0.93)
    c.paint()
    text.draw(c, "tt + lens", lab + pad, 48, 30, (0.2, 0.2, 0.2), fam="Nunito", semibold=True)
    text.draw(c, "stack + lens o", lab + 2 * pad + cell, 48, 30, (0.2, 0.2, 0.2), fam="Nunito", semibold=True)
    for i, (name, (b, f, a)) in enumerate(PALETTES.items()):
        y = 70 + i * (cell + pad)
        text.draw(c, f"{i + 1}. {name}", 24, y + cell / 2 + 12, 30, (0.2, 0.2, 0.2), fam="Nunito", semibold=True)
        b, f, a = hexc(b), hexc(f), hexc(a)
        for j, fn in enumerate((tt_lens(b, f, a), stack(b, [f, f, a], f, ant_on=None, lens_o=True))):
            src = cairo.ImageSurface(cairo.FORMAT_ARGB32, S, S)
            fn(cairo.Context(src))
            c.set_source_surface(circle(src, cell), lab + pad + j * (cell + pad), y)
            c.paint()
    s.write_to_png(out)


# ================================================================ chosen (owner, Oct 2026): stacked name + lens "o", midnight palette
MIDNIGHT = PALETTES["midnight"]
FINAL = stack(hexc(MIDNIGHT[0]), [hexc(MIDNIGHT[1]), hexc(MIDNIGHT[1]), hexc(MIDNIGHT[2])], hexc(MIDNIGHT[1]),
              ant_on=None, lens_o=True, lens_ant=False)   # owner: no ant in the lens


def export_final(out):
    for px in (800, 2048):
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, px, px)
        c = cairo.Context(s)
        c.scale(px / S, px / S)
        FINAL(c)
        s.write_to_png(os.path.join(out, f"profile_{px}.png"))


if __name__ == "__main__":
    main()
