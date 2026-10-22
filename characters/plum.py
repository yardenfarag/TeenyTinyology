"""PLUM — the bird. Plum-purple head and back, warm peach breast, teal wing tips; cheerful and fussy about her feathers.

draw(c, st, x, y, s, ...) — side view facing LEFT, (x, y) = where the feet touch the perch.
pose: ang (lean; negative tips forward), flap (None = folded, else wing angle), spread (0..1 wing fanned
      out sideways, as when 'anting'), fluff (0..1 feathers puffed), beak_open (0..1), blink, happy, tail_up
BEAK_TIP gives the local beak point; tip_world() maps it for the current pose.
"""
import math

import cairo

from engine.core import TAU, Palette, ellipse, hexc, rot_pt

NAME = "Plum"
SPECIES = "bird"
BACK = Palette("#7a3f8f", "#b886cc", "#3e1a4c")
HEADP = Palette("#8a4aa0", "#c79ad8", "#45205a")
BREAST = Palette("#ffb27a", "#ffe0c2", "#e07a4a")
WING = Palette("#6a3480", "#a070b8", "#331446")
TEAL = hexc("#2f9fa0")
BEAK = Palette("#3a3030", "#7a6a66", "#1a1414")
BEAK_TIP = (-142, -180)


def tip_world(x, y, s, ang):
    px, py = rot_pt(BEAK_TIP[0] * s, BEAK_TIP[1] * s, ang)
    return x + px, y + py


def draw(c, st, x, y, s, ang=0.0, flap=None, spread=0.0, fluff=0.0, beak_open=0.0, blink=False, happy=0.0,
         tail_up=0.0, alpha=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.push_group()
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    real = st.realistic
    puff = 1 + 0.12 * fluff
    if flap is None:
        st.shadow(c, 10, 4, 120, 12, 0.18)
        legc = hexc("#6a5a52")
        for lx in (-6, 14):
            st.line(c, [(lx, -62), (lx - 4, 0)], 6, legc)
            for d in (-16, -6, 10):
                st.line(c, [(lx - 4, 0), (lx - 4 + d, 6)], 4, legc)
    # tail
    c.save()
    c.translate(45, -85)
    c.rotate(-0.5 * tail_up)

    def tail(cc):
        cc.move_to(10, -10)
        cc.curve_to(65, 25, 105, 75, 133, 113)
        cc.line_to(105, 125)
        cc.curve_to(75, 85, 40, 45, -7, 15)
        cc.close_path()

    st.part(c, tail, WING, 60, 60, 80, seed=111)
    st.line(c, [(118, 100), (128, 118)], 8, TEAL)
    c.restore()
    # far wing when spread (anting pose) sits behind the body
    if spread > 0:
        c.save()
        c.translate(20, -150)
        c.rotate(-0.4 - 1.0 * spread)
        c.scale(1, 0.6 + 0.6 * spread)
        _wing(c, st, 0.6)
        c.restore()

    def body(cc):
        ellipse(cc, 15, -112, 88 * puff, 64 * puff, 0.5)

    st.part(c, body, BACK, 15, -112, 88, seed=112)
    st.ellipse(c, -30, -110, 50 * puff, 56 * puff, 0.2, BREAST, seed=113)
    if real:
        c.save()
        body(c)
        c.clip()
        for i in range(90):  # feather scallops
            fx = -60 + (i * 37) % 160
            fy = -170 + (i * 23) % 120
            c.arc(fx, fy, 7, 0.2, math.pi - 0.2)
            c.set_source_rgba(0.2, 0.1, 0.25, 0.18)
            c.set_line_width(1.2)
            c.stroke()
        c.restore()
    # near wing
    c.save()
    c.translate(15, -145)
    if spread > 0:
        c.rotate(0.3 + 0.9 * spread)
        c.scale(1, 1 + 0.4 * spread)
    else:
        c.rotate(flap if flap is not None else 0.0)
    _wing(c, st, 1.0)
    c.restore()
    # head
    st.ellipse(c, -48, -185, 46 * (0.9 if real else 1.06), 44 * (0.9 if real else 1.06), 0.0, HEADP, seed=114)
    st.shine(c, -60, -212, 16, 8, -0.3, 0.25)
    # beak (upper + lower)
    op = 10 * beak_open
    c.move_to(-84, -197)
    c.curve_to(-110, -199, -128, -191, -142, -182 - op * 0.3)
    c.curve_to(-122, -180, -104, -178, -86, -180)
    c.close_path()
    c.set_source_rgba(*BEAK.base)
    c.fill()
    c.move_to(-86, -178)
    c.curve_to(-104, -176, -122, -174 + op, -138, -176 + op)
    c.curve_to(-120, -168 + op, -102, -166, -84, -167)
    c.close_path()
    c.set_source_rgba(*BEAK.dark)
    c.fill()
    st.eye(c, -62, -193, 10 if not real else 11, 0.1 if blink else 1.0)
    st.blush(c, -50, -168, 10, 0.4)
    if st.faces and happy > 0.2:
        c.move_to(-74, -208)
        c.curve_to(-66, -214, -56, -214, -50, -208)
        c.set_source_rgba(*HEADP.dark)
        c.set_line_width(3)
        c.stroke()
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()


def _wing(c, st, shade_k):
    def wing(cc):
        cc.move_to(0, 0)
        cc.curve_to(40, -25, 110, -10, 142, 62)
        cc.curve_to(100, 52, 40, 42, -12, 24)
        cc.close_path()

    st.part(c, wing, WING, 60, 25, 75, seed=115)
    c.set_source_rgba(1, 1, 1, 0.18 * shade_k)
    c.set_line_width(2.5)
    for k in range(4):
        c.move_to(20 + k * 22, 8 + k * 6)
        c.curve_to(50 + k * 20, 10 + k * 8, 90 + k * 10, 30 + k * 6, 120 + k * 4, 52 + k * 2)
        c.stroke()
    c.set_source_rgba(*TEAL[:3], 0.9)
    c.set_line_width(7)
    for k in range(3):
        c.move_to(112 + k * 8, 40 + k * 6)
        c.line_to(138 + k * 4, 60 + k * 3)
        c.stroke()
