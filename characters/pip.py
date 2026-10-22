"""PIP — the flea. Warm amber-brown, chubby, springy; curious and a little cheeky.

Stages:
  draw(c, st, x, y, s, ...)        adult flea, side view facing right, (x, y) = feet line centre
  draw_larva(c, st, x, y, s, ...)  wormlike larva, head at (x, y) facing right
  draw_cocoon(c, st, x, y, s, k)   silk cocoon (k = 0..1 how wrapped)
In the "real" style Pip is drawn anatomically (cat flea: combs, plates, bristles) and has no face.
"""
import math

import cairo

from engine.core import TAU, Palette, ellipse, hexc, lerp, rng, smooth_path

NAME = "Pip"
SPECIES = "flea"
BODY = Palette("#c06a2e", "#ffb878", "#6a2f10", "#4a1d08")
LEG = Palette("#8a4518", "#c8814a", "#4a1f08")
LARVA = Palette("#f6ead2", "#fffaf0", "#d4bd93", "#a88a5e")
HEADCAP = Palette("#a5652c", "#e5ab70", "#55290a")


# ================================================================ adult
def draw(c, st, x, y, s, ang=0.0, phase=0.0, crouch=0.0, blink=False, happy=0.0, bite=0.0, alpha=1.0, sx=1.0, sy=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s * sx, s * sy)
    c.push_group()
    if st.realistic:
        _real(c, st, phase, bite)
    else:
        _cute(c, st, phase, crouch, blink, happy, bite)
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()


def _cute(c, st, phase, crouch, blink, happy, bite):
    sh = 6 * math.sin(phase)
    st.shadow(c, 0, 6, 200, 24)
    far = Palette("#a0592a", "#c8814a", "#6a3010")
    st.limb(c, [(40, -70), (62, -35), (70 - sh, 0)], 15, far)
    st.limb(c, [(-5, -65), (-2, -32), (8 + sh, 0)], 15, far)
    st.limb(c, [(-60, -80), (-125, -95 + crouch * 20), (-95 - sh, 0)], 24, far)
    breathe = 1 + 0.025 * math.sin(phase * 0.5)

    def body(cc):
        ellipse(cc, -10, -128, 128, 100 * breathe, -0.08)

    st.part(c, body, BODY, -10, -128, 128, seed=51)
    c.save()
    body(c)
    c.clip()
    c.set_source_rgba(*BODY.dark[:3], 0.25)
    c.set_line_width(5)
    for u in (-70, -30, 10, 50):
        c.move_to(u, -230)
        c.curve_to(u + 18, -160, u + 18, -90, u, -20)
        c.stroke()
    c.restore()
    st.shine(c, -50, -186, 46, 16, -0.25, 0.32)
    for k in range(5):  # little back tufts
        bx = -95 + k * 34
        byy = -128 - 100 * math.sqrt(max(0, 1 - ((bx + 10) / 128) ** 2)) + 6
        st.line(c, [(bx, byy), (bx - 10, byy - 12), (bx - 20, byy - 14)], 4, BODY.dark)
    st.ellipse(c, 98, -128, 66, 62, 0.0, BODY, seed=52)
    st.line(c, [(80, -182), (72, -204), (60, -214)], 5, LEG.base)
    c.arc(58, -216, 8, 0, TAU)
    c.set_source_rgba(*LEG.base)
    c.fill()
    st.eye(c, 118, -138, 17, 0.1 if blink else 1.0)
    st.blush(c, 124, -102, 14, 0.5)
    st.smile(c, 148, -108, 18, k=1 + happy)
    st.line(c, [(160, -106), (166, -84 + bite * 16)], 6, LEG.base)
    for pts in ([(70, -78), (96, -40), (108 + sh, -4)], [(10, -70), (16, -34), (30 - sh, -4)]):
        st.limb(c, pts, 17, LEG)
        st.ellipse(c, pts[-1][0] + 8, pts[-1][1], 16, 9, 0.0, Palette("#5a2a0e"), seed=53)
    st.ellipse(c, -78, -76, 50, 30, 0.35, BODY, seed=54)
    st.limb(c, [(-110, -66), (-72 + sh, -6)], 18, LEG)
    st.ellipse(c, -60 + sh, -4, 20, 10, 0.0, Palette("#5a2a0e"), seed=55)


def _real(c, st, phase, bite):
    r = rng(4)
    st.shadow(c, -10, 6, 230, 22, 0.28)
    chitin = hexc("#4a200c")
    amber = hexc("#b8702e")
    sh = 4 * math.sin(phase)

    def leg(pts, widths, spines=0, alpha=1.0):
        for (a, b), w in zip(zip(pts, pts[1:]), widths):
            st.line(c, [a, b], w, chitin, alpha)
            st.line(c, [(a[0], a[1] - w * 0.2), (b[0], b[1] - w * 0.2)], w * 0.3, hexc("#c07a3a"), 0.45 * alpha)
        for i in range(spines):
            (ax, ay), (bx, by) = pts[-3], pts[-2]
            f = (i + 1) / (spines + 1)
            px, py = ax + (bx - ax) * f, ay + (by - ay) * f
            st.line(c, [(px, py), (px + 10, py - 4)], 2, chitin, alpha)
        x0, y0 = pts[-1]
        for k in range(5):
            c.arc(x0 + k * 6, y0 - 1, 3.2 - k * 0.3, 0, TAU)
            c.set_source_rgba(*chitin[:3], alpha)
            c.fill()
        st.line(c, [(x0 + 28, y0 - 1), (x0 + 36, y0 + 3), (x0 + 33, y0 + 6)], 2, chitin, alpha)

    leg([(60, -78), (78, -48), (110, -36), (118 + sh, -8), (122 + sh, -4)], [12, 9, 6, 4], alpha=0.55)
    leg([(0, -76), (-4, -48), (34, -34), (26 - sh, -8), (30 - sh, -4)], [12, 9, 6, 4], alpha=0.55)
    body = [(-175, -112), (-160, -170), (-100, -205), (-20, -212), (50, -200), (95, -182), (130, -168),
            (160, -140), (168, -112), (150, -82), (110, -72), (60, -64), (-20, -56), (-100, -60), (-160, -78)]

    def body_path(cc):
        smooth_path(cc, body, closed=True)

    st.part(c, body_path, Palette("#5a2810", "#8a4a20", "#2e1206"), 0, -130, 175, seed=56)
    c.save()
    body_path(c)
    c.clip()
    body_path(c)
    c.set_source_rgba(*amber[:3], 0.45)
    c.set_line_width(22)
    c.stroke()
    xs = [118, 92, 62] + [30 - k * 26 for k in range(8)]
    for x in xs:  # sclerite plates with posterior bristle rows
        c.move_to(x, -220)
        c.curve_to(x - 14, -150, x - 14, -100, x - 4, -50)
        c.set_source_rgba(0.12, 0.04, 0.0, 0.7)
        c.set_line_width(3)
        c.stroke()
        for k in range(4):
            yy = -195 + k * 32 + r.uniform(-6, 6)
            c.move_to(x - 8, yy)
            c.line_to(x - 30, yy + 6)
            c.set_source_rgba(0.1, 0.03, 0, 0.85)
            c.set_line_width(2)
            c.stroke()
    c.restore()
    for k in range(8):  # genal comb
        gx = 150 - k * 7
        st.line(c, [(gx, -86 + k * 1.5), (gx - 14, -70 + k * 2)], 3.2, hexc("#140500"))
    for k in range(14):  # pronotal comb
        yy = -205 + k * 9
        st.line(c, [(112 - k * 0.6, yy), (98 - k * 0.6, yy + 5)], 3.2, hexc("#140500"))
    st.eye(c, 132, -138, 12, 1.0)
    st.line(c, [(152, -96), (160, -60), (162, -40 + bite * 14)], 3, chitin)
    leg([(76, -74), (92, -46), (126, -36), (134 + sh, -8), (138 + sh, -4)], [16, 11, 7, 5], spines=2)
    leg([(14, -72), (8, -44), (48, -30), (40 - sh, -8), (44 - sh, -4)], [16, 11, 7, 5], spines=2)
    st.ellipse(c, -62, -88, 46, 30, 0.6, Palette("#4a200c", "#7a3a16", "#2a0e02"), seed=57)
    leg([(-62, -70), (-118, -48), (-70 + sh, -12), (-30 + sh, -4)], [24, 14, 7], spines=4)


# ================================================================ larva
def draw_larva(c, st, x, y, s, phase=0.0, munch=0.0, blink=False, gut=None, alpha=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.push_group()
    n = 13
    spine = [(-26 - i * 27 + 3 * math.sin(phase * 2 - i * 0.7), 9 * math.sin(phase - i * 0.55)) for i in range(n)]
    radii = [17 + 4 * math.sin(math.pi * (i + 1) / (n + 1)) - (5 if i > n - 3 else 0) for i in range(n)]
    st.shadow(c, -170, 30, 220, 14, 0.15)
    for i in reversed(range(n)):
        px, py = spine[i]
        rr = radii[i]
        for d in (-1, 1):
            st.line(c, [(px, py + d * rr * 0.8), (px - 12, py + d * (rr + 12))], 2.2, LARVA.line)
        st.ellipse(c, px, py, rr, rr, 0.0, LARVA, seed=60 + i)
    c.move_to(*spine[0])
    for p in spine[1:-1]:
        c.line_to(*p)
    c.set_source_rgba(*hexc("#7a4a2a", 0.25))
    c.set_line_width(10)
    c.stroke()
    if gut:
        gut(c, spine)
    tx, ty = spine[-1]
    for d in (-1, 1):
        st.line(c, [(tx - 8, ty + d * 6), (tx - 22, ty + d * 12)], 3, LARVA.line)
    c.save()
    c.translate(-12, 0)
    c.rotate(0.25 * math.sin(munch * TAU * 2) if munch > 0 else 0)
    st.ellipse(c, 16, 0, 24, 20, 0.0, HEADCAP, seed=70)
    st.line(c, [(36, 6), (46, 12)], 3, hexc("#3a1a06"))
    st.line(c, [(36, 12), (44, 18)], 3, hexc("#3a1a06"))
    st.line(c, [(28, -16), (40, -26)], 3, hexc("#3a1a06"))
    if st.faces:
        st.eye(c, 22, -4, 6, 0.1 if blink else 1.0)
        st.blush(c, 30, 8, 5, 0.5)
    c.restore()
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()
    return spine


def draw_cocoon(c, st, x, y, s, k, opened=0.0, seed=5):
    if k <= 0 or opened >= 1:
        return
    r = rng(seed)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    a = 1 - opened
    st.ellipse(c, 0, 0, 290 * k, 120 * k, 0.0, Palette("#efe4cc", "#fffaf0", "#cdbb98"), seed=seed, alpha=0.92 * a)
    c.set_line_width(1.6)
    for _ in range(int(70 * k)):
        a0 = r.uniform(0, TAU)
        c.new_path()
        c.save()
        c.scale(290 * k * r.uniform(0.7, 1.0), 120 * k * r.uniform(0.7, 1.0))
        c.arc(0, 0, 1, a0, a0 + r.uniform(1, 2.5))
        c.restore()
        c.set_source_rgba(0.72, 0.64, 0.48, 0.5 * a)
        c.stroke()
    for _ in range(10):
        c.arc(r.uniform(-240, 240) * k, r.uniform(-80, 80) * k, r.uniform(4, 9), 0, TAU)
        c.set_source_rgba(0.48, 0.35, 0.22, 0.7 * a)
        c.fill()
    c.restore()
