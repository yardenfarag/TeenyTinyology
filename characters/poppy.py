"""POPPY — the mosquito (female: only females bite; they need blood to make eggs). Slate-grey body with cream bands,
long banded legs, narrow glassy wings, a long straight proboscis, short palps and thin, lightly haired antennae
(males have bushy ones). Busy, businesslike, polite about it.

draw(c, st, x, y, s, **pose) — side view facing right, (x, y) = middle of the thorax.
pose: fly (0 landed..1 flying: wings beat, legs dangle), phase (wing/leg time), fed (0..1 belly fills with blood),
      body (a Palette to draw a different mosquito),
      probe (0..1 proboscis tilts down to bite), blink, happy, ang, alpha
helpers: tip_world(...) where the proboscis ends; feet sit on y + FEET_Y when landed.
In the "real" style Poppy has a compound eye, scaled wing veins and no face.
"""
import math

import cairo

from engine.core import TAU, Palette, ellipse, hexc, lerp, smooth_path

NAME = "Poppy"
SPECIES = "mosquito"
BODY = Palette("#5b5f74", "#9aa0b8", "#3a3d4e", "#25273a")
BAND = hexc("#eae4d6")
LEG = hexc("#4a4d60")
WING = hexc("#dfe6f2")
BLOOD = hexc("#d2404a")
EYE = Palette("#2a2c3e", "#5a6080", "#15161f")
FEET_Y = 120

PROB_BASE = (52, 14)
PROB_LEN = 112


def _prob_angle(probe):
    return lerp(0.55, 1.25, probe)


def tip_world(x, y, s, probe=0.0, ang=0.0):
    a = _prob_angle(probe)
    lx = PROB_BASE[0] + math.cos(a) * PROB_LEN
    ly = PROB_BASE[1] + math.sin(a) * PROB_LEN
    ca, sa = math.cos(ang), math.sin(ang)
    return x + (lx * ca - ly * sa) * s, y + (lx * sa + ly * ca) * s


def _abdomen_pts(fed):
    n = 8
    pts = []
    for i in range(n):
        u = i / (n - 1)
        px = -26 - u * 150
        py = 10 + 22 * u + 8 * fed * math.sin(math.pi * u)
        r = 15 * (1 + 0.55 * fed) * (1 - 0.6 * u) + 5 * math.sin(math.pi * u) * (1 + 0.6 * fed)
        pts.append((px, py, r))
    return pts


def _wing(c, st, fly, phase, side, real):
    beat = math.sin(phase * 14 + side) if fly > 0 else 0.0
    rest = -0.12 if side == 0 else -0.04
    a = lerp(rest, -0.9 + 0.75 * beat, fly)
    ghosts = 3 if fly > 0.5 else 1
    for g in range(ghosts):
        aa = a + (g - 1) * 0.28 * fly if ghosts > 1 else a
        c.save()
        c.translate(-6, -26)
        c.rotate(math.pi + aa)
        ellipse(c, 78, 0, 82, 15, 0.0)
        c.set_source_rgba(*WING[:3], (0.42 if ghosts == 1 else 0.2) * (0.75 if side == 0 else 1.0))
        c.fill_preserve()
        c.set_source_rgba(*BODY.dark[:3], 0.35)
        c.set_line_width(1.6)
        c.stroke()
        if real or st.name == "illustrated":
            for k, (vy0, vy1) in enumerate(((-4, -10), (0, 0), (4, 9))):
                st.line(c, [(8, vy0 * 0.4), (150, vy1)], 1.0, BODY.dark, 0.35)
            for k in range(14):  # scale fringe on the trailing edge
                fx = 14 + k * 10
                st.line(c, [(fx, 13 - abs(fx - 78) / 12), (fx - 4, 17 - abs(fx - 78) / 12)], 1.2, BODY.dark, 0.3)
        c.restore()


def _legs(c, st, fly, phase, far):
    sh = 4 * math.sin(phase * 2)
    alpha = 0.6 if far else 1.0
    hips = [(18, 18), (2, 22), (-14, 22)]
    for i, (hx, hy) in enumerate(hips):
        dx = (12 if far else 0)
        if i == 0:
            land = [(hx + dx, hy), (hx + 46 + dx, hy + 40), (hx + 78 + dx, FEET_Y)]
        elif i == 1:
            land = [(hx + dx, hy), (hx + 10 + dx, hy + 54), (hx + 26 + dx, FEET_Y)]
        else:  # hind legs held up and back — a resting mosquito's habit
            land = [(hx + dx, hy), (hx - 56 + dx, hy + 46), (hx - 128 + dx, hy - 30)]
        dang = [(hx + dx, hy), (hx - 10 - 18 * i + dx, hy + 60 + sh), (hx - 46 - 30 * i + dx, hy + 112 + sh * (i + 1))]
        pts = [(lerp(a[0], b[0], fly), lerp(a[1], b[1], fly)) for a, b in zip(land, dang)]
        st.line(c, pts, 4.2, LEG, alpha)
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):  # pale rings
            for f in (0.35, 0.7):
                px, py = lerp(ax, bx, f), lerp(ay, by, f)
                c.arc(px, py, 2.6, 0, TAU)
                c.set_source_rgba(*BAND[:3], 0.9 * alpha)
                c.fill()


def draw(c, st, x, y, s, fly=1.0, phase=0.0, fed=0.0, probe=0.0, blink=False, happy=0.0, ang=0.0, alpha=1.0,
         body=None):
    pal = body or BODY            # body: another mosquito's colours (e003: not Poppy, months later)
    real = st.realistic
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.push_group()
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    bob = 3 * math.sin(phase * 3) * fly
    c.translate(0, bob)
    _legs(c, st, fly, phase, far=True)
    _wing(c, st, fly, phase, 0, real)
    # abdomen: one smooth tapering shape with cream bands; swells and reddens with the blood meal
    ab = _abdomen_pts(fed)
    top = [(px, py - r) for px, py, r in ab]
    bot = [(px, py + r) for px, py, r in reversed(ab)]

    def abdomen(cc):
        smooth_path(cc, top + [(ab[-1][0] - ab[-1][2], ab[-1][1])] + bot, closed=True)

    st.part(c, abdomen, pal, -100, 30, 90, seed=301)
    c.save()
    abdomen(c)
    c.clip()
    if fed > 0:
        abdomen(c)
        c.set_source_rgba(*BLOOD[:3], 0.7 * fed)
        c.fill()
    for px, py, r in ab[1:-1]:  # pale band at each segment's front edge
        c.move_to(px + 6, py - r - 4)
        c.curve_to(px + 14, py - r * 0.3, px + 14, py + r * 0.3, px + 6, py + r + 4)
        c.set_source_rgba(*BAND[:3], 0.85)
        c.set_line_width(5 + 2 * fed)
        c.stroke()
    c.restore()
    # thorax: humped
    def thorax(cc):
        ellipse(cc, 0, 0, 36, 32, -0.2)

    st.part(c, thorax, pal, 0, 0, 36, seed=310)
    c.save()
    thorax(c)
    c.clip()
    st.line(c, [(-20, -22), (10, -30), (30, -14)], 4, BAND, 0.8)  # pale scale stripes on the back
    c.restore()
    c.arc(-22, -18, 5, 0, TAU)  # haltere knob
    c.set_source_rgba(*BAND[:3], 0.9)
    c.fill()
    # proboscis + palps (short in females)
    pa = _prob_angle(probe)
    ex, ey = PROB_BASE[0] + math.cos(pa) * PROB_LEN, PROB_BASE[1] + math.sin(pa) * PROB_LEN
    st.line(c, [PROB_BASE, (ex, ey)], 4.6, pal.dark)
    st.line(c, [(lerp(PROB_BASE[0], ex, 0.82), lerp(PROB_BASE[1], ey, 0.82)), (ex, ey)], 3, BAND, 0.8)
    st.line(c, [(PROB_BASE[0] - 2, PROB_BASE[1] - 4), (PROB_BASE[0] + 16, PROB_BASE[1] + 6)], 3.4, pal.base)
    # head
    st.ellipse(c, 42, -2, 22, 20, 0.0, pal, seed=311)
    # antennae: thin, lightly haired (female)
    for k, (bx, tx, ty) in enumerate(((54, 112, -50), (48, 100, -64))):
        pts = [(bx, -14), (lerp(bx, tx, 0.5), -38 + k * 4), (tx, ty)]
        st.line(c, pts, 2.2, pal.dark, 0.85 if k == 0 else 0.55)
        for f in (0.3, 0.5, 0.7, 0.88):
            (ax, ay), (bx2, by2) = (pts[0], pts[1]) if f < 0.5 else (pts[1], pts[2])
            g = (f / 0.5) if f < 0.5 else ((f - 0.5) / 0.5)
            px, py = lerp(ax, bx2, g), lerp(ay, by2, g)
            for d in (-1, 1):
                st.line(c, [(px, py), (px + 4 * d, py - 6)], 1.0, pal.dark, 0.6)
    if real:
        st.ellipse(c, 44, -4, 15, 16, 0.0, EYE, seed=312)
        c.save()
        ellipse(c, 44, -4, 15, 16)
        c.clip()
        for i in range(30):
            c.arc(32 + (i % 6) * 5, -18 + (i // 6) * 6, 1.3, 0, TAU)
            c.set_source_rgba(1, 1, 1, 0.12)
            c.fill()
        c.restore()
    else:
        st.eye(c, 46, -6, 12, 0.1 if blink else 1.0)
        st.blush(c, 54, 8, 7, 0.45)
        st.smile(c, 58, 6, 9, BAND, 1 + happy)
    _wing(c, st, fly, phase + 0.4, 1, real)
    _legs(c, st, fly, phase, far=False)
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()
