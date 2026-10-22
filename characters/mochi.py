"""MOCHI — the cat. Cream fur, caramel patches, sea-green eyes, pink nose. Sleepy, gentle, a bit vain.

draw(c, st, x, y, s, **pose) — lying "loaf" pose facing right, (x, y) = middle of the belly on the ground.
pose: eyes (0 closed..1 open), turn (0 facing forward..1 head turned back to lick its back),
      lick (0..1 head dips to the fur), tongue (0..1), tail (phase), ear (twitch -1..1),
      breathe (-1..1), happy (0..1 smile)
"""
import math

import cairo

from engine.core import TAU, Palette, ease, ellipse, hexc, lerp

NAME = "Mochi"
SPECIES = "cat"
FUR = Palette("#f4e6d2", "#fffaf2", "#cfb397", "#8a6a50")
PATCH = Palette("#d99a5b", "#f2c08a", "#a8682f")
PINK = hexc("#f2a2a6")
IRIS = hexc("#5fbfa3")
CREAM = hexc("#fffaf2")


def head_pose(turn, lick):
    k = ease(turn)
    hx = lerp(222, -60, k)
    hy = lerp(-215, -235, k) - 55 * math.sin(math.pi * k) + 45 * lick
    fx = math.cos(math.pi * k)
    fx = math.copysign(max(abs(fx), 0.12), fx)
    return hx, hy, fx


def to_world(x, y, s, lx, ly):
    return x + lx * s, y + ly * s


def mouth_world(x, y, s, turn=0.0, lick=0.0):
    hx, hy, fx = head_pose(turn, lick)
    return to_world(x, y, s, hx + fx * 80, hy + 40)


BACK_SPOT = (-125, -218)  # a point on Mochi's back (local)
BELLY = (-20, -105)


def draw_head(c, st, x, y, s, fx=1.0, eyes=1.0, tongue=0.0, ear=0.0, happy=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s * fx, s)
    real = st.realistic
    hr = (88, 76) if real else (96, 82)
    # ears
    for i, ((bx, by, tx, ty, ex, ey), tw) in enumerate(((((-62, -40, -80, -140, -12, -70)), 0.0),
                                                        (((2, -74, 30, -152, 66, -52)), ear))):
        c.save()
        c.translate(bx, by)
        c.rotate(tw * 0.25)
        c.translate(-bx, -by)

        def ear_path(cc, bx=bx, by=by, tx=tx, ty=ty, ex=ex, ey=ey):
            cc.move_to(bx, by)
            cc.curve_to(tx - 6, ty + 30, tx - 4, ty + 4, tx, ty)
            cc.curve_to(tx + 8, ty + 10, ex, ey - 30, ex, ey)
            cc.close_path()

        st.part(c, ear_path, PATCH, (bx + ex) / 2, (by + ty) / 2, 50, seed=11 + i)
        c.move_to(lerp(bx, ex, 0.22), lerp(by, ey, 0.22) - 6)
        c.line_to(lerp(tx, (bx + ex) / 2, 0.28), lerp(ty, (by + ey) / 2, 0.28))
        c.line_to(lerp(ex, bx, 0.22), lerp(ey, by, 0.22) - 6)
        c.close_path()
        c.set_source_rgba(*PINK[:3], 0.85)
        c.fill()
        c.restore()
    st.ellipse(c, 0, 0, hr[0], hr[1], 0.0, FUR, seed=21)
    # caramel cap patch
    c.save()
    ellipse(c, 0, 0, hr[0], hr[1])
    c.clip()
    st.ellipse(c, -40, -70, 70, 48, -0.3, PATCH, seed=22)
    c.restore()
    if real:  # fur texture
        c.save()
        ellipse(c, 0, 0, hr[0], hr[1])
        c.clip()
        c.set_line_width(1.6)
        for i in range(70):
            a = i * 2.39996
            r = 12 + (i * 37) % 70
            px, py = math.cos(a) * r, math.sin(a) * r * 0.85
            c.move_to(px, py)
            c.line_to(px - 7, py + 4)
            c.set_source_rgba(0.45, 0.32, 0.2, 0.22)
            c.stroke()
        c.restore()
    # muzzle
    st.ellipse(c, 50, 24, 48 if not real else 40, 32 if not real else 26, 0.0, Palette("#fffaf2", "#ffffff", "#e8d8c4"), seed=23)
    st.eye(c, 2, -18, 17, eyes, iris=IRIS, slit=real)
    st.eye(c, 56, -20, 15, eyes, iris=IRIS, slit=real)
    st.blush(c, 4, 18, 15, 0.45)
    st.blush(c, 84, 22, 10, 0.35)
    if tongue > 0:
        ellipse(c, 80, 44 + 10 * tongue, 14, 8 + 16 * tongue, -0.2)
        c.set_source_rgba(*hexc("#ec7f8c"))
        c.fill()
    c.move_to(74, 4)
    c.curve_to(78, 0, 90, 0, 93, 4)
    c.line_to(84, 15)
    c.close_path()
    c.set_source_rgba(*hexc("#e9818a"))
    c.fill()
    mouth = hexc("#6a4030")
    st.line(c, [(84, 15), (84, 23)], 3, mouth)
    if happy > 0.3 and st.faces:
        st.smile(c, 76, 24, 16, mouth, 1.2)
        st.smile(c, 92, 24, 16, mouth, 1.2)
    else:
        c.move_to(84, 23)
        c.curve_to(81, 29, 73, 29, 69, 25)
        c.move_to(84, 23)
        c.curve_to(87, 29, 95, 29, 98, 25)
        c.set_source_rgba(*mouth)
        c.set_line_width(3)
        c.stroke()
    c.set_source_rgba(1, 1, 1, 0.85 if not real else 0.7)
    c.set_line_width(2.4)
    for ex, ey in ((168, 2), (172, 22), (162, 42)):
        c.move_to(72, 24)
        c.curve_to(110, ey + 4, 140, ey, ex, ey)
        c.stroke()
    c.restore()


def draw(c, st, x, y, s, eyes=0.0, turn=0.0, lick=0.0, tongue=0.0, tail=0.0, ear=0.0, breathe=0.0, happy=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    st.shadow(c, 20, 8, 300, 26, 0.18)
    by = -110 - 4 * breathe
    # tail (behind the paws, in front of the belly)
    wob = 8 * math.sin(tail)

    def tail_path(cc):
        cc.move_to(-228, -62)
        cc.curve_to(-262, -10, -200, 22, -80, 26)
        cc.curve_to(0, 30, 60, 18 + wob, 110, 6 + wob)

    def body_path(cc):
        ellipse(cc, 0, by, 242, 112 + 3 * breathe)

    st.part(c, body_path, FUR, 0, by, 242, seed=31)
    c.save()
    body_path(c)
    c.clip()
    st.ellipse(c, -90, by - 70, 150, 70, -0.15, PATCH, seed=32)   # caramel saddle
    st.ellipse(c, 120, by - 85, 60, 40, 0.2, PATCH, seed=33)
    if st.realistic:
        c.set_line_width(1.6)
        for i in range(260):
            a = i * 2.39996
            px = -230 + (i * 53) % 460
            py = by - 100 + (i * 29) % 200
            c.move_to(px, py)
            c.line_to(px - 12, py + 4 * math.sin(a))
            c.set_source_rgba(0.45, 0.32, 0.2, 0.18)
            c.stroke()
    c.restore()
    st.ellipse(c, 150, -112, 66, 78, 0.0, Palette("#fffaf2", "#ffffff", "#e8d8c4"), seed=34)  # chest
    # tail
    c.save()
    tail_path(c)
    c.set_source_rgba(*PATCH.dark)
    c.set_line_width(46)
    c.stroke()
    tail_path(c)
    c.set_source_rgba(*PATCH.base)
    c.set_line_width(40)
    c.stroke()
    c.arc(110, 6 + wob, 21, 0, TAU)
    c.set_source_rgba(*CREAM)
    c.fill()
    c.restore()
    for i, px in enumerate((178, 236)):
        st.ellipse(c, px, -18, 50, 22, 0.0, Palette("#fffaf2", "#ffffff", "#e3d2bd"), seed=40 + i)
        st.line(c, [(px + 26, -30), (px + 30, -12)], 2.4, hexc("#c9a98a"))
        st.line(c, [(px + 38, -28), (px + 41, -12)], 2.4, hexc("#c9a98a"))
    hx, hy, fx = head_pose(turn, lick)
    c.move_to(150, -165)
    c.line_to(hx, hy + 30)
    c.set_source_rgba(*FUR.base)
    c.set_line_width(118)
    c.stroke()
    draw_head(c, st, hx, hy, 1.0, fx, eyes, tongue, ear, happy)
    c.restore()
