"""BISCUIT — the dog (male). Honey-tan fur, chocolate floppy ears, cream belly and muzzle (no blaze around the eyes),
teal collar with a little gold tag. Happy, sun-loving, a bit lazy.

draw(c, st, x, y, s, **pose) — lying down facing right, (x, y) = middle of the belly on the ground.
draw_curled(c, st, x, y, s, eyes, breathe, tail, ear) — napping curled up (nose to tail); CURL_SKIN_SPOT.
pose: eyes (0 closed..1 open), head (0 chin on paws..1 head up), tail (wag phase), wag (0..1 amount),
      ear (twitch -1..1), breathe (-1..1), happy (0..1 smile), tongue (0..1 happy pant),
      xray (callable(c) drawn in local coords, clipped to the trunk), xray_alpha (0..1)
X-ray: draw(..., xray=lambda c: draw_chest(c, st, t, worms)) — lung, heart, ARTERY/BRANCHES points.
Other helpers: draw_paw, SKIN_SPOT (where Poppy bites), to_world(...), nose_world(...)
In the "real" style Biscuit has natural eyes, fur strokes and no cartoon smile or blush.
"""
import math
import random

import cairo

from engine.core import TAU, Palette, ease, ellipse, hexc, lerp, smooth_path

NAME = "Biscuit"
SPECIES = "dog"
FUR = Palette("#dba468", "#f4cc98", "#a8703c", "#6e4420")
EAR = Palette("#8a5530", "#b37a4c", "#5a3418", "#3e2210")
CREAM = Palette("#fff4e2", "#ffffff", "#ead6b8")
NOSE = hexc("#3a2418")
COLLAR = Palette("#3fa3a0", "#7fd0c8", "#2a706e")
TAG = Palette("#f2b84b", "#ffe2a0", "#b88420")
IRIS = hexc("#6a3e1e")

SKIN_SPOT = (-40, -186)  # on the back, where the mosquito lands
HEAD_S = 1.2


def to_world(x, y, s, lx, ly):
    return x + lx * s, y + ly * s


def head_pos(head):
    k = ease(head)
    return lerp(262, 222, k), lerp(-92, -220, k)


def nose_world(x, y, s, head=1.0):
    hx, hy = head_pos(head)
    return to_world(x, y, s, hx + 128 * HEAD_S, hy + 14 * HEAD_S)


def _trunk_path(cc, by, breathe, hx, hy):
    """Body and neck as one smooth outline: the ellipse of the body, with its front-top replaced by a neck
    that runs up under the head (the head covers the top of the neck)."""
    ry = 98 + 3 * breathe
    pts = []
    a0, a1 = 0.3, TAU - 1.25
    for k in range(14):
        a = lerp(a0, a1, k / 13)
        pts.append((-20 + 196 * math.cos(a), by + ry * math.sin(a)))
    pts.append((hx - 70, hy + 30))        # back of the neck, under the head
    pts.append((hx + 20, hy + 72))        # throat
    fx, fy = pts[0]
    pts.append((lerp(hx + 20, fx, 0.5) + 16, lerp(hy + 72, fy, 0.5)))   # front of the chest
    smooth_path(cc, pts, closed=True)


def draw_head(c, st, hx, hy, eyes=1.0, ear=0.0, happy=0.0, tongue=0.0):
    real = st.realistic
    c.save()
    c.translate(hx, hy)
    # far ear (peeks behind the skull)
    st.ellipse(c, -36, -40, 34, 62, 0.5, EAR, seed=81)
    st.ellipse(c, 0, 0, 92, 82, 0.0, FUR, seed=82)
    if real:  # short fur strokes
        c.save()
        ellipse(c, 0, 0, 92, 82)
        c.clip()
        c.set_line_width(1.5)
        for i in range(60):
            a = i * 2.39996
            r = 10 + (i * 37) % 72
            px, py = math.cos(a) * r, math.sin(a) * r * 0.85
            c.move_to(px, py)
            c.line_to(px - 7, py + 3)
            c.set_source_rgba(0.42, 0.26, 0.12, 0.22)
            c.stroke()
        c.restore()
    # muzzle: a soft rounded snout reaching forward; the nose sits on its tip
    st.ellipse(c, 78, 22, 58, 40, 0.05, CREAM, seed=84)
    if tongue > 0:
        ellipse(c, 96, 58 + 10 * tongue, 15, 6 + 20 * tongue, 0.1)
        c.set_source_rgba(*hexc("#ec7f8c"))
        c.fill()
        st.line(c, [(96, 52), (96, 56 + 22 * tongue)], 2, hexc("#c25c6a"))
    # nose: rounded and broad, on the very tip of the snout
    c.move_to(112, 4)
    c.curve_to(118, -6, 138, -6, 140, 6)
    c.curve_to(141, 16, 132, 22, 126, 22)
    c.curve_to(118, 22, 110, 14, 112, 4)
    c.set_source_rgba(*NOSE)
    c.fill()
    c.arc(122, 3, 4, 0, TAU)
    c.set_source_rgba(1, 1, 1, 0.55)
    c.fill()
    mouth = hexc("#5a3420")
    st.line(c, [(128, 22), (126, 34)], 3, mouth)
    c.move_to(126, 34)
    if happy > 0.3 and st.faces:
        c.curve_to(118, 48, 98, 50, 86, 38)
    else:
        c.curve_to(118, 42, 102, 44, 90, 38)
    c.set_source_rgba(*mouth)
    c.set_line_width(3)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.stroke()
    st.eye(c, 34, -14, 15, eyes, iris=IRIS if real else None)
    if st.faces and eyes > 0.15:  # soft brow dot
        ellipse(c, 30, -40, 8, 5, -0.2)
        c.set_source_rgba(*FUR.dark[:3], 0.7)
        c.fill()
    st.blush(c, 46, 22, 14, 0.4)
    # near ear: floppy, hanging from the top of the skull, swings with `ear`
    c.save()
    c.translate(-30, -56)
    c.rotate(0.18 * ear)

    def ear_path(cc):
        cc.move_to(-10, 0)
        cc.curve_to(30, -14, 44, 10, 36, 60)
        cc.curve_to(30, 100, 6, 116, -14, 104)
        cc.curve_to(-32, 90, -34, 40, -10, 0)
        cc.close_path()

    st.part(c, ear_path, EAR, 6, 50, 60, seed=85)
    c.restore()
    c.restore()


def draw_paw(c, st, x, y, s=1.0, seed=0):
    """A paw resting on the ground, toes pointing right; (x, y) = where it touches the ground, middle."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    st.ellipse(c, -6, -18, 40, 18, 0.0, CREAM, seed=seed)                  # foot
    for k, (tx, ty, r) in enumerate(((18, -30, 13), (30, -22, 13), (38, -12, 12))):
        st.ellipse(c, tx, ty, r, r * 0.9, 0.0, CREAM, seed=seed + 10 + k)   # toes, stacked to the front
    for tx, ty in ((24, -18), (33, -8)):                                     # creases between toes
        st.line(c, [(tx - 4, ty - 12), (tx, ty)], 2.2, hexc("#c9a882"))
    c.restore()


# ---------------------------------------------------------------- chest cutaway (local coords)
LUNG = [(128, -168), (80, -186), (10, -184), (-56, -166), (-82, -128), (-72, -84), (-30, -60), (30, -54),
        (82, -62), (120, -88), (136, -128)]
HEART_C = (96, -84)
# pulmonary artery: leaves the top of the heart, arches up, then branches back into the lung (Dilly lives here)
ARTERY = [(100, -108), (96, -134), (72, -148), (40, -146), (6, -136), (-30, -120)]
BRANCHES = [[(40, -146), (24, -168), (4, -174)], [(6, -136), (-14, -156), (-40, -158)],
            [(6, -136), (-6, -112), (-30, -96)], [(72, -148), (66, -170)], [(-30, -120), (-58, -126)],
            [(40, -146), (30, -118), (12, -96)]]
LUNG_PAL = Palette("#f2b0b4", "#ffd8da", "#c97c84", "#9a4e58")
HEART_PAL = Palette("#d0505c", "#f08a92", "#902430", "#6a1820")
ART_PAL = hexc("#c4485a")


def draw_chest(c, st, t=0.0, worms=None):
    """Lung (side view), heart low in front, and the pulmonary artery branching into the lung.
    worms: callable(c) drawn last, over the arteries AND the heart, so a worm passing through the heart is seen
    (e003 judge pass 1: she vanished under it). Use HEART_C / ARTERY / BRANCHES points to place Dilly."""
    breathe = 1 + 0.02 * math.sin(t * 2)

    def lung(cc):
        smooth_path(cc, [(26 + (px - 26) * breathe, -120 + (py + 120) * breathe) for px, py in LUNG], closed=True)

    st.part(c, lung, LUNG_PAL, 26, -120, 110, seed=120)
    c.save()
    lung(c)
    c.clip()
    rr = random.Random(7)
    for _ in range(70):  # spongy texture: tiny air sacs
        px, py = rr.uniform(-80, 135), rr.uniform(-186, -54)
        c.arc(px, py, rr.uniform(3, 7), 0, TAU)
        c.set_source_rgba(1, 1, 1, 0.22)
        c.fill()
    st.line(c, [(60, -186), (40, -130), (-10, -62)], 2.4, LUNG_PAL.line, 0.45)   # lobe fissures
    st.line(c, [(-70, -150), (-20, -128), (20, -100)], 2.0, LUNG_PAL.line, 0.35)
    c.restore()
    for br in BRANCHES:
        st.line(c, br, 9, ART_PAL, 0.9)
    st.line(c, ARTERY, 15, ART_PAL)
    st.line(c, ARTERY, 6, hexc("#e88a96"), 0.6)
    beat = 1 + 0.06 * max(0.0, math.sin(t * 7)) ** 4

    def heart(cc):
        cx, cy = HEART_C
        cc.save()
        cc.translate(cx, cy)
        cc.scale(beat, beat)
        cc.move_to(-30, -24)
        cc.curve_to(-6, -44, 34, -36, 36, -6)
        cc.curve_to(36, 18, 10, 40, -10, 44)
        cc.curve_to(-30, 30, -44, 0, -30, -24)
        cc.close_path()
        cc.restore()

    st.part(c, heart, HEART_PAL, HEART_C[0], HEART_C[1], 44, seed=121)
    if worms:
        worms(c)


CURL_SKIN_SPOT = (-120, -170)   # top of the back in the curled pose (where Poppy lands)


def draw_curled(c, st, x, y, s, eyes=0.0, breathe=0.0, tail=0.0, ear=0.0, alpha=1.0):
    """Napping curled up like a doughnut: round back, head tucked in at the front with the nose pointing back
    toward the rump, tail wrapped around the front under the nose. (x, y) = middle of the body on the ground."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.push_group()
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    st.shadow(c, 0, 4, 250, 26, 0.2)
    ry = 92 + 4 * breathe
    st.ellipse(c, -14, -ry, 192, ry, 0.0, FUR, seed=130)                       # the curled back
    st.ellipse(c, -118, -66, 82, 64, -0.25, FUR, seed=131)                     # haunch
    draw_paw(c, st, -66, -2, 0.9, seed=132)                                    # hind paw tucked forward
    flick = 0.15 * math.sin(tail * 1.3)

    def tail_path(cc):                                                         # wraps around the front
        cc.move_to(-196, -44)
        cc.curve_to(-214, 4, -130, 2, -60, -6)
        cc.curve_to(-20, -10, 6, -16, 22, -30 - 14 * flick)

    for col, w in ((FUR.line, 36), (FUR.base, 30)):
        tail_path(c)
        c.set_source_rgba(*col)
        c.set_line_width(w)
        c.stroke()
    # head resting low at the front, turned back toward the tail, chin on the ground
    c.save()
    c.translate(96, -86)
    c.rotate(0.12)
    c.scale(-1.05, 1.05)
    draw_head(c, st, 0, 0, eyes, ear, 0.0, 0.0)
    c.restore()
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()


def draw(c, st, x, y, s, eyes=1.0, head=1.0, tail=0.0, wag=0.5, ear=0.0, breathe=0.0, happy=0.0,
         tongue=0.0, xray=None, xray_alpha=0.0, alpha=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.push_group()
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    st.shadow(c, 20, 6, 320, 26, 0.18)
    by = -96 - 4 * breathe
    # tail: from the rump, swishing with `tail` (phase) scaled by `wag`
    sw = wag * math.sin(tail * 2.4)

    def tail_path(cc):
        cc.move_to(-196, by - 30)
        cc.curve_to(-256, by - 70 - 30 * sw, -296 + 20 * sw, by - 130 - 20 * sw, -280 + 50 * sw, by - 180)

    for col, w in ((FUR.line, 38), (FUR.base, 32)):
        tail_path(c)
        c.set_source_rgba(*col)
        c.set_line_width(w)
        c.stroke()
    hx, hy = head_pos(head)
    st.part(c, lambda cc: _trunk_path(cc, by, breathe, hx, hy), FUR, -20, by, 196, seed=86)
    c.save()
    _trunk_path(c, by, breathe, hx, hy)
    c.clip()
    st.ellipse(c, 20, by + 70, 200, 40, 0.0, CREAM, seed=87)       # pale belly
    if st.realistic:
        c.set_line_width(1.6)
        for i in range(240):
            px = -230 + (i * 53) % 460
            py = by - 90 + (i * 29) % 180
            c.move_to(px, py)
            c.line_to(px - 12, py + 3 * math.sin(i * 2.4))
            c.set_source_rgba(0.42, 0.26, 0.12, 0.18)
            c.stroke()
    c.restore()
    if xray and xray_alpha > 0:  # see-through trunk (body + neck); organs come from the caller (draw_chest)
        c.save()
        _trunk_path(c, by, breathe, hx, hy)
        c.clip()
        c.push_group()
        c.set_source_rgba(*hexc("#f6dcd2"))
        c.paint()
        xray(c)
        c.pop_group_to_source()
        c.paint_with_alpha(xray_alpha)
        c.restore()
    # haunch (hind leg folded under) and its paw
    st.ellipse(c, -132, by + 18, 80, 66, -0.2, FUR, seed=88)
    draw_paw(c, st, -66, -4, 0.9, seed=89)
    # neck and collar
    ny = lerp(-112, -150, ease(head))
    cx, cy = lerp(150, hx - 20, 0.12), lerp(ny, hy + 20, 0.12)
    ang = math.atan2(hy + 20 - ny, hx - 20 - 150)
    c.save()
    c.translate(cx, cy)
    c.rotate(ang)
    st.part(c, lambda cc: ellipse(cc, 0, 0, 14, 62), COLLAR, 0, 0, 62, seed=91)
    c.restore()
    tx, ty = cx + math.cos(ang + 1.57) * 58, cy + math.sin(ang + 1.57) * 58
    st.ellipse(c, tx + 4, ty + 10, 12, 12, 0.0, TAG, seed=92)
    # front legs lying forward along the ground, paws out front
    for i, (ex_, px) in enumerate(((112, 176), (148, 238))):
        ax, ay, bx, by_ = ex_, -64, px - 10, -22
        st.ellipse(c, (ax + bx) / 2, (ay + by_) / 2, math.hypot(bx - ax, by_ - ay) / 2 + 22, 22,
                   math.atan2(by_ - ay, bx - ax), FUR, seed=95 + i)
    for i, px in enumerate((176, 238)):
        draw_paw(c, st, px, -4, 1.0, seed=93 + i)
    c.save()
    c.translate(hx, hy)
    c.scale(HEAD_S, HEAD_S)
    draw_head(c, st, 0, 0, eyes, ear, happy, tongue)
    c.restore()
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()
