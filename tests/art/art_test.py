"""Art-direction test: one flea drawn three ways (cute storybook / realistic / illustrated).

Usage: python art_test.py [t]   -> style_test.png (t = animation time for idle pose)
"""
import math
import os
import random
import sys

import cairo

HERE = os.path.dirname(os.path.abspath(__file__))
PW, PH = 900, 1150
TAU = 2 * math.pi


def hexc(h, a=1.0):
    h = h.lstrip("#")
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


def ellipse(c, cx, cy, rx, ry, rot=0.0):
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    c.scale(rx, ry)
    c.new_sub_path()
    c.arc(0, 0, 1, 0, TAU)
    c.restore()


def radial_fill(c, cx, cy, r, stops, hx=-0.3, hy=-0.45):
    g = cairo.RadialGradient(cx + hx * r, cy + hy * r, 0, cx, cy, r * 1.05)
    for off, col in stops:
        g.add_color_stop_rgba(off, *col)
    c.set_source(g)
    c.fill()


def stroke_path(c, pts, w, col, cap=cairo.LINE_CAP_ROUND):
    c.set_line_cap(cap)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.set_source_rgba(*col)
    c.set_line_width(w)
    c.stroke()


def shadow(c, x, y, rx, ry, a=0.22):
    g = cairo.RadialGradient(x, y, 0, x, y, rx)
    g.add_color_stop_rgba(0, 0, 0, 0, a)
    g.add_color_stop_rgba(1, 0, 0, 0, 0)
    c.save()
    c.translate(x, y)
    c.scale(1, ry / rx)
    c.translate(-x, -y)
    c.arc(x, y, rx, 0, TAU)
    c.set_source(g)
    c.fill()
    c.restore()


# ================================================================ A: cute storybook
def flea_cute(c, t):
    blink = 1.0 if (t % 3.2) > 0.12 else 0.1
    breathe = 1 + 0.025 * math.sin(t * 3)
    shadow(c, 0, 8, 210, 26)
    base, light, dark = hexc("#c06a2e"), hexc("#ffb878"), hexc("#6a2f10")
    leg = hexc("#7a3a16")
    # far legs
    for pts in ([(40, -70), (62, -35), (70, 0)], [(-5, -65), (-2, -32), (8, 0)]):
        stroke_path(c, pts, 15, hexc("#a0592a"))
    stroke_path(c, [(-60, -80), (-125, -95), (-95, 0)], 24, hexc("#a0592a"))
    # body
    c.save()
    c.translate(-10, -128)
    c.scale(1, breathe)
    ellipse(c, 0, 0, 128, 100, -0.08)
    radial_fill(c, 0, 0, 128, [(0, light), (0.5, base), (1, dark)])
    # segment stripes
    c.save()
    ellipse(c, 0, 0, 128, 100, -0.08)
    c.clip()
    c.set_source_rgba(*dark[:3], 0.28)
    c.set_line_width(5)
    for u in (-70, -30, 10, 50):
        c.move_to(u, -110)
        c.curve_to(u + 18, -40, u + 18, 40, u, 110)
        c.stroke()
    c.restore()
    ellipse(c, -40, -58, 46, 16, -0.25)
    c.set_source_rgba(1, 1, 1, 0.35)
    c.fill()
    c.restore()
    # tufts
    c.set_source_rgba(*dark[:3], 0.9)
    c.set_line_width(4)
    for k in range(5):
        x = -95 + k * 34
        y = -128 - 100 * math.sqrt(max(0, 1 - ((x + 10) / 128) ** 2)) * breathe + 6
        c.move_to(x, y)
        c.curve_to(x - 6, y - 10, x - 14, y - 14, x - 20, y - 14)
        c.stroke()
    # head
    ellipse(c, 98, -128, 66, 62)
    radial_fill(c, 98, -128, 66, [(0, light), (0.55, base), (1, dark)])
    # antenna
    c.set_source_rgba(*leg)
    c.set_line_width(5)
    c.move_to(80, -182)
    c.curve_to(76, -200, 68, -210, 60, -214)
    c.stroke()
    c.arc(58, -216, 8, 0, TAU)
    c.fill()
    # eye
    if blink > 0.5:
        ellipse(c, 118, -138, 20, 25)
        c.set_source_rgba(0.08, 0.04, 0.02, 1)
        c.fill()
        c.arc(111, -148, 8, 0, TAU)
        c.set_source_rgba(1, 1, 1, 1)
        c.fill()
        c.arc(124, -128, 4, 0, TAU)
        c.fill()
    else:
        c.move_to(100, -136)
        c.curve_to(110, -126, 126, -126, 136, -136)
        c.set_source_rgba(0.08, 0.04, 0.02, 1)
        c.set_line_width(5)
        c.stroke()
    ellipse(c, 122, -104, 15, 8)
    c.set_source_rgba(*hexc("#ff7f8a", 0.55))
    c.fill()
    c.move_to(140, -110)
    c.curve_to(146, -100, 154, -100, 158, -108)
    c.set_source_rgba(*hexc("#4a1d08"))
    c.set_line_width(4)
    c.stroke()
    stroke_path(c, [(160, -108), (166, -84)], 6, leg)
    # near legs with rounded "boots"
    for pts in ([(70, -78), (96, -40), (108, -4)], [(10, -70), (16, -34), (30, -4)]):
        stroke_path(c, pts, 17, leg)
        ellipse(c, pts[-1][0] + 8, pts[-1][1], 16, 9)
        c.set_source_rgba(*hexc("#5a2a0e"))
        c.fill()
    ellipse(c, -78, -76, 50, 30, 0.35)
    radial_fill(c, -78, -76, 50, [(0, light), (0.5, base), (1, dark)])
    stroke_path(c, [(-110, -66), (-72, -6)], 18, leg)
    ellipse(c, -60, -4, 20, 10)
    c.set_source_rgba(*hexc("#5a2a0e"))
    c.fill()


# ================================================================ B: realistic (cat flea, lateral view)
def flea_real(c, t):
    rnd = random.Random(4)
    shadow(c, -10, 8, 230, 22, 0.28)
    chitin = hexc("#4a200c")
    amber = hexc("#b8702e")

    def leg(pts, widths, spines=0):
        for (a, b), w in zip(zip(pts, pts[1:]), widths):
            stroke_path(c, [a, b], w, chitin)
            stroke_path(c, [(a[0], a[1] - w * 0.2), (b[0], b[1] - w * 0.2)], w * 0.3, hexc("#c07a3a", 0.45))
        for i in range(spines):
            (ax, ay), (bx, by) = pts[-3], pts[-2]
            f = (i + 1) / (spines + 1)
            px, py = ax + (bx - ax) * f, ay + (by - ay) * f
            stroke_path(c, [(px, py), (px + 10, py - 4)], 2, chitin)
        # tarsus segments + claw
        x, y = pts[-1]
        for k in range(5):
            c.arc(x + k * 6, y - 1, 3.2 - k * 0.3, 0, TAU)
            c.set_source_rgba(*chitin)
            c.fill()
        stroke_path(c, [(x + 28, y - 1), (x + 36, y + 3), (x + 33, y + 6)], 2, chitin)

    # far legs (lighter)
    c.push_group()
    leg([(60, -78), (78, -48), (110, -36), (118, -8), (122, -4)], [12, 9, 6, 4])
    leg([(0, -76), (-4, -48), (34, -34), (26, -8), (30, -4)], [12, 9, 6, 4])
    c.pop_group_to_source()
    c.paint_with_alpha(0.55)
    # body silhouette: laterally flattened oval with a tapered head
    body = [(-175, -112), (-160, -170), (-100, -205), (-20, -212), (50, -200), (95, -182),
            (130, -168), (160, -140), (168, -112), (150, -82), (110, -72), (60, -64),
            (-20, -56), (-100, -60), (-160, -78)]

    def body_path():
        c.move_to(*body[0])
        n = len(body)
        for i in range(n):
            p0, p1, p2 = body[i], body[(i + 1) % n], body[(i + 2) % n]
            c.curve_to(p0[0] + (p1[0] - body[i - 1][0]) / 6, p0[1] + (p1[1] - body[i - 1][1]) / 6,
                       p1[0] - (p2[0] - p0[0]) / 6, p1[1] - (p2[1] - p0[1]) / 6, *p1)
        c.close_path()

    body_path()
    g = cairo.LinearGradient(0, -215, 0, -55)
    g.add_color_stop_rgba(0, *hexc("#7a3a16"))
    g.add_color_stop_rgba(0.45, *hexc("#5a2810"))
    g.add_color_stop_rgba(1, *hexc("#2e1206"))
    c.set_source(g)
    c.fill()
    c.save()
    body_path()
    c.clip()
    # translucent amber rim (thin chitin edges)
    body_path()
    c.set_source_rgba(*amber[:3], 0.55)
    c.set_line_width(22)
    c.stroke()
    # sclerite plates: 3 thoracic + 8 abdominal tergites
    xs = [118, 92, 62] + [30 - k * 26 for k in range(8)]
    for i, x in enumerate(xs):
        c.move_to(x, -220)
        c.curve_to(x - 14, -150, x - 14, -100, x - 4, -50)
        c.set_source_rgba(0.12, 0.04, 0.0, 0.75)
        c.set_line_width(3)
        c.stroke()
        c.move_to(x - 6, -218)
        c.curve_to(x - 20, -150, x - 20, -100, x - 10, -50)
        c.set_source_rgba(*hexc("#d08a4a")[:3], 0.18)
        c.set_line_width(6)
        c.stroke()
        # posterior row of setae
        for k in range(4):
            yy = -195 + k * 32 + rnd.uniform(-6, 6)
            c.move_to(x - 8, yy)
            c.line_to(x - 30, yy + 6)
            c.set_source_rgba(0.1, 0.03, 0, 0.9)
            c.set_line_width(2)
            c.stroke()
    for _ in range(500):  # micro texture
        c.arc(rnd.uniform(-180, 170), rnd.uniform(-215, -55), rnd.uniform(0.5, 1.5), 0, TAU)
        c.set_source_rgba(1, 0.8, 0.6, rnd.uniform(0.03, 0.09))
        c.fill()
    c.move_to(-120, -190)
    c.curve_to(-40, -214, 40, -206, 110, -176)
    c.set_source_rgba(1, 0.92, 0.8, 0.35)
    c.set_line_width(5)
    c.stroke()
    c.restore()
    # genal comb (under the head) and pronotal comb (behind the head)
    for k in range(8):
        x = 150 - k * 7
        stroke_path(c, [(x, -86 + k * 1.5), (x - 14, -70 + k * 2)], 3.2, hexc("#140500"))
    for k in range(14):
        y = -205 + k * 9
        stroke_path(c, [(112 - k * 0.6, y), (98 - k * 0.6, y + 5)], 3.2, hexc("#140500"))
    # head details
    ellipse(c, 132, -138, 7, 6)
    c.set_source_rgba(0.02, 0.01, 0, 1)
    c.fill()
    c.arc(130, -140, 1.8, 0, TAU)
    c.set_source_rgba(1, 1, 1, 0.6)
    c.fill()
    ellipse(c, 118, -160, 12, 7, -0.6)
    c.set_source_rgba(*hexc("#8a4a1e"))
    c.fill()
    stroke_path(c, [(152, -96), (160, -60), (162, -40)], 3, chitin)
    stroke_path(c, [(146, -94), (150, -66)], 2.4, chitin)
    for x0 in range(-150, 100, 50):  # long dorsal bristles
        y0 = -200 + abs(x0) * 0.05
        stroke_path(c, [(x0, y0), (x0 - 24, y0 - 10)], 2, hexc("#1a0800"))
    # near legs
    leg([(76, -74), (92, -46), (126, -36), (134, -8), (138, -4)], [16, 11, 7, 5], spines=2)
    leg([(14, -72), (8, -44), (48, -30), (40, -8), (44, -4)], [16, 11, 7, 5], spines=2)
    ellipse(c, -62, -88, 46, 30, 0.6)  # big hind coxa
    c.set_source_rgba(*hexc("#4a200c"))
    c.fill_preserve()
    c.set_source_rgba(*amber[:3], 0.4)
    c.set_line_width(3)
    c.stroke()
    leg([(-62, -70), (-118, -48), (-70, -12), (-30, -4)], [24, 14, 7], spines=4)


# ================================================================ C: illustrated (ink + watercolor)
def wobble_ellipse(c, cx, cy, rx, ry, rot, seed, amt=5.0):
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, TAU) for _ in range(3)]
    pts = []
    for k in range(96):
        a = k / 96 * TAU
        # low-frequency wobble reads as a hand-drawn line, not fuzz
        r = 1 + (amt / max(rx, ry)) * (math.sin(2 * a + ph[0]) + 0.6 * math.sin(3 * a + ph[1]) + 0.3 * math.sin(5 * a + ph[2])) / 1.9
        x, y = math.cos(a) * rx * r, math.sin(a) * ry * r
        pts.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
    return pts


def poly(c, pts):
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.close_path()


def watercolor(c, pts, col, seed):
    rnd = random.Random(seed)
    poly(c, pts)
    c.set_source_rgba(*col[:3], 0.55)
    c.fill()
    c.save()
    poly(c, pts)
    c.clip()
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    for _ in range(40):
        ellipse(c, rnd.uniform(min(xs), max(xs)), rnd.uniform(min(ys), max(ys)), rnd.uniform(15, 60), rnd.uniform(10, 40), rnd.uniform(0, 3))
        shade = rnd.uniform(-0.15, 0.1)
        c.set_source_rgba(*(max(0, min(1, v + shade)) for v in col[:3]), 0.1)
        c.fill()
    g = cairo.LinearGradient(0, min(ys), 0, max(ys))
    g.add_color_stop_rgba(0, 1, 1, 1, 0.25)
    g.add_color_stop_rgba(1, 0.2, 0.05, 0, 0.25)
    c.set_source(g)
    c.paint()
    c.restore()
    poly(c, pts)
    c.set_source_rgba(*(v * 0.7 for v in col[:3]), 0.35)
    c.set_line_width(8)
    c.stroke()


def ink(c, pts, w=3.5, closed=True, seed=0):
    rnd = random.Random(seed)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    seq = pts + ([pts[0]] if closed else [])
    for i, (a, b) in enumerate(zip(seq, seq[1:])):
        c.move_to(*a)
        c.line_to(*b)
        c.set_source_rgba(0.16, 0.09, 0.05, 0.92)
        c.set_line_width(w * (0.75 + 0.45 * abs(math.sin(i * 0.12))))
        c.stroke()


def flea_illustrated(c, t):
    blink = 1.0 if (t % 3.6) > 0.12 else 0.1
    shadow(c, 0, 8, 200, 20, 0.15)
    col = hexc("#b9703a")
    for k, pts in enumerate(([(40, -70), (62, -35), (72, 0)], [(-5, -65), (-2, -32), (8, 0)], [(-60, -80), (-122, -92), (-92, 0)])):
        ink(c, pts, 3, False, 10 + k)
    body = wobble_ellipse(c, -10, -126, 126, 92, -0.08, 1)
    watercolor(c, body, col, 2)
    head = wobble_ellipse(c, 98, -126, 60, 56, 0, 3)
    watercolor(c, head, col, 4)
    ink(c, body, 3.4, True, 5)
    ink(c, head, 3.4, True, 6)
    rnd = random.Random(7)
    for k in range(9):  # hatching on the belly
        x = -100 + k * 20
        ink(c, [(x, -60), (x + 14, -45)], 1.6, False, 20 + k)
    for u in (-70, -30, 10, 50):
        c.move_to(u, -205)
        c.curve_to(u + 14, -150, u + 14, -100, u + 2, -42)
        c.set_source_rgba(0.16, 0.09, 0.05, 0.35)
        c.set_line_width(2)
        c.stroke()
    for k in range(6):
        x = -100 + k * 34
        ink(c, [(x, -212 + abs(x) * 0.08), (x - 16, -224 + abs(x) * 0.08)], 1.8, False, 30 + k)
    ink(c, [(80, -176), (72, -200), (60, -208)], 2.4, False, 40)
    if blink > 0.5:
        ellipse(c, 116, -136, 10, 13)
        c.set_source_rgba(0.12, 0.06, 0.03, 1)
        c.fill()
        c.arc(112, -141, 4, 0, TAU)
        c.set_source_rgba(1, 1, 1, 1)
        c.fill()
    else:
        ink(c, [(104, -134), (116, -128), (128, -134)], 3, False, 41)
    ellipse(c, 120, -106, 12, 6)
    c.set_source_rgba(*hexc("#e8707a", 0.35))
    c.fill()
    ink(c, [(152, -110), (158, -86)], 3, False, 42)
    for k, pts in enumerate(([(70, -78), (96, -40), (110, -2)], [(10, -70), (16, -34), (32, -2)])):
        ink(c, pts, 4.2, False, 50 + k)
    thigh = wobble_ellipse(c, -78, -76, 48, 28, 0.35, 8)
    watercolor(c, thigh, col, 9)
    ink(c, thigh, 3, True, 10)
    ink(c, [(-108, -66), (-70, -4), (-46, -2)], 4.2, False, 55)


# ================================================================ sheet
def panel_bg(c, kind):
    if kind == "paper":
        c.set_source_rgba(*hexc("#f3ead6"))
        c.paint()
        rnd = random.Random(1)
        for _ in range(600):
            x, y = rnd.uniform(0, PW), rnd.uniform(0, PH)
            c.move_to(x, y)
            c.line_to(x + rnd.uniform(-8, 8), y + rnd.uniform(-8, 8))
            c.set_source_rgba(0.4, 0.3, 0.15, 0.06)
            c.set_line_width(1)
            c.stroke()
        return
    g = cairo.LinearGradient(0, 0, 0, PH)
    stops = {"warm": ("#fbf1df", "#efd9b8"), "cool": ("#eef0ea", "#cfd6cc")}[kind]
    g.add_color_stop_rgba(0, *hexc(stops[0]))
    g.add_color_stop_rgba(1, *hexc(stops[1]))
    c.set_source(g)
    c.paint()


def main():
    t = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
    gap = 30
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, PW * 3 + gap * 4, PH + 220)
    c = cairo.Context(s)
    c.set_source_rgba(*hexc("#2b2622"))
    c.paint()
    panels = [("A  Cute storybook", "warm", flea_cute, 1.55),
              ("B  Realistic", "cool", flea_real, 1.45),
              ("C  Illustrated (hybrid look)", "paper", flea_illustrated, 1.55)]
    for i, (title, bg, fn, sc) in enumerate(panels):
        x0 = gap + i * (PW + gap)
        c.save()
        c.translate(x0, 150)
        c.rectangle(0, 0, PW, PH)
        c.clip()
        panel_bg(c, bg)
        c.translate(PW / 2 + 10, PH * 0.66)
        c.scale(sc, sc)
        fn(c, t)
        c.restore()
        c.select_font_face("Georgia", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        c.set_font_size(54)
        ext = c.text_extents(title)
        c.move_to(x0 + PW / 2 - ext.x_advance / 2, 105)
        c.set_source_rgba(1, 1, 1, 0.92)
        c.show_text(title)
    s.write_to_png(os.path.join(HERE, "style_test.png"))
    print("wrote style_test.png")


if __name__ == "__main__":
    main()
