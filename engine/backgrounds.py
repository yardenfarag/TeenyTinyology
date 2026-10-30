"""Reusable painted backgrounds (cached). All original, drawn in code.

meadow()       sunny grass field, ground line ~ y 1360
pond(night)    pond seen from its bank: sky, far trees, water (y 820-1240), near bank ground ~ y 1400
underwater()   inside a pond: surface at y ~ 430, light rays, plants on the bottom
parchment()    field-guide paper for diagrams
Animated details (ripples, shimmer, floating motes) are separate functions drawn per frame.
"""
import math

import cairo

from .core import TAU, H, W, ellipse, hexc, mix, new_surface, rng

_cache = {}
EXTRA = 240          # backgrounds are taller than the frame so scenes can be lifted (see scene.STAGE_LIFT)
HH = H + EXTRA


def _cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


def _grad(c, y0, y1, stops):
    g = cairo.LinearGradient(0, y0, 0, y1)
    for off, col in stops:
        g.add_color_stop_rgba(off, *(hexc(col) if isinstance(col, str) else col))
    c.set_source(g)


def _blob_trees(c, r, y, cols, n=26, size=(70, 150)):
    for _ in range(n):
        x = r.uniform(-80, W + 80)
        s = r.uniform(*size)
        c.arc(x, y - s * 0.3 + r.uniform(-30, 30), s, 0, TAU)
        c.set_source_rgba(*mix(hexc(cols[0]), hexc(cols[1]), r.random()))
        c.fill()


def _grass_blades(c, r, y0, y1, n, cols, h=(40, 120), w=(4, 9), alpha=1.0):
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for _ in range(n):
        x = r.uniform(-20, W + 20)
        y = r.uniform(y0, y1)
        hh = r.uniform(*h)
        lean = r.uniform(-0.35, 0.35)
        c.move_to(x, y)
        c.curve_to(x + lean * hh * 0.3, y - hh * 0.5, x + lean * hh * 0.7, y - hh * 0.8, x + lean * hh, y - hh)
        col = mix(hexc(cols[0]), hexc(cols[1]), r.random())
        c.set_source_rgba(col[0], col[1], col[2], alpha)
        c.set_line_width(r.uniform(*w))
        c.stroke()


def meadow(seed=1):
    def build():
        s, c = new_surface(W, HH)
        r = rng(seed)
        _grad(c, 0, 900, [(0, "#fdf1d4"), (0.6, "#e9efc8"), (1, "#cfe0a8")])
        c.paint()
        g = cairo.RadialGradient(820, 260, 0, 820, 260, 700)
        g.add_color_stop_rgba(0, 1, 0.97, 0.82, 0.9)
        g.add_color_stop_rgba(1, 1, 0.97, 0.82, 0)
        c.set_source(g)
        c.paint()
        _blob_trees(c, r, 860, ("#b7cf96", "#9fbf82"), 30, (80, 170))
        _blob_trees(c, r, 930, ("#93b56f", "#7ea35e"), 26, (60, 130))
        _grad(c, 880, HH, [(0, "#a9c97a"), (0.35, "#8cb860"), (1, "#5e8a3c")])
        c.rectangle(0, 900, W, HH - 900)
        c.fill()
        _grass_blades(c, r, 920, 1200, 500, ("#9cc46e", "#7aa652"), (20, 60), (2, 4), 0.7)
        # soft dirt path where characters stand
        ellipse(c, 540, 1395, 760, 70)
        c.set_source_rgba(*hexc("#c9a978", 0.55))
        c.fill()
        for _ in range(60):
            ellipse(c, r.uniform(0, W), r.uniform(1350, 1440), r.uniform(4, 12), r.uniform(3, 7), r.uniform(0, 3))
            c.set_source_rgba(*hexc("#a08458", r.uniform(0.3, 0.6)))
            c.fill()
        _grass_blades(c, r, 1450, HH + 40, 420, ("#6f9e48", "#4f7d32"), (60, 180), (4, 9))
        for _ in range(26):  # little flowers
            x, y = r.uniform(0, W), r.uniform(1000, 1300)
            col = r.choice(("#fff6e0", "#ffd36b", "#f4a6b8"))
            for k in range(5):
                a = k * TAU / 5
                c.arc(x + math.cos(a) * 5, y + math.sin(a) * 5, 4, 0, TAU)
                c.set_source_rgba(*hexc(col))
                c.fill()
        return s

    return _cached(("meadow", seed), build)


def pond(night=False, seed=2):
    def build():
        s, c = new_surface(W, HH)
        r = rng(seed)
        if night:
            _grad(c, 0, 900, [(0, "#1b2347"), (0.7, "#2f3b6a"), (1, "#45507e")])
        else:
            _grad(c, 0, 900, [(0, "#fbefd2"), (0.6, "#e5efd2"), (1, "#cde2c6")])
        c.paint()
        if night:
            for _ in range(140):
                c.arc(r.uniform(0, W), r.uniform(0, 700), r.uniform(0.8, 2.2), 0, TAU)
                c.set_source_rgba(1, 1, 0.95, r.uniform(0.3, 0.9))
                c.fill()
            g = cairo.RadialGradient(760, 300, 0, 760, 300, 260)
            g.add_color_stop_rgba(0, 1, 0.98, 0.85, 0.5)
            g.add_color_stop_rgba(1, 1, 0.98, 0.85, 0)
            c.set_source(g)
            c.paint()
            c.arc(760, 300, 70, 0, TAU)
            c.set_source_rgba(*hexc("#fff6d6"))
            c.fill()
        trees = ("#2c3d4a", "#34505a") if night else ("#a9c894", "#8fb57c")
        _blob_trees(c, r, 840, trees, 34, (70, 160))
        # water
        if night:
            _grad(c, 800, 1260, [(0, "#2a3a62"), (1, "#16233f")])
        else:
            _grad(c, 800, 1260, [(0, "#bfe0e4"), (0.5, "#8ec4cc"), (1, "#5f9fac")])
        c.move_to(0, 800)
        c.line_to(W, 800)
        c.line_to(W, 1180)
        c.curve_to(760, 1290, 300, 1210, 0, 1260)
        c.close_path()
        c.fill()
        for _ in range(40):  # tree reflections
            x = r.uniform(0, W)
            ellipse(c, x, r.uniform(830, 900), r.uniform(40, 90), r.uniform(10, 26))
            c.set_source_rgba(*hexc(trees[0])[:3], 0.25)
            c.fill()
        for _ in range(7):  # lily pads
            x, y = r.uniform(80, 1000), r.uniform(900, 1150)
            rr = r.uniform(26, 46)
            ellipse(c, x, y, rr, rr * 0.38)
            c.set_source_rgba(*(hexc("#2f5a3a") if night else hexc("#6fae5a")))
            c.fill()
        # near bank
        bank = ("#2c3a26", "#1c2818") if night else ("#a2c672", "#6f9a48")
        _grad(c, 1180, HH, [(0, bank[0]), (1, bank[1])])
        c.move_to(0, 1270)
        c.curve_to(300, 1220, 760, 1300, W, 1190)
        c.line_to(W, HH)
        c.line_to(0, HH)
        c.close_path()
        c.fill()
        ellipse(c, 560, 1420, 640, 60)
        c.set_source_rgba(*(hexc("#3a3424", 0.6) if night else hexc("#c6a876", 0.5)))
        c.fill()
        reed = ("#22301c", "#2f4024") if night else ("#6f9a48", "#4f7a34")
        for side in (60, 1010):  # reeds
            for k in range(14):
                x = side + r.uniform(-60, 60)
                hh = r.uniform(220, 420)
                c.move_to(x, 1260)
                c.curve_to(x + 6, 1260 - hh * 0.5, x + r.uniform(-20, 20), 1260 - hh * 0.8, x + r.uniform(-30, 30), 1260 - hh)
                c.set_source_rgba(*mix(hexc(reed[0]), hexc(reed[1]), r.random()))
                c.set_line_width(r.uniform(4, 8))
                c.stroke()
        _grass_blades(c, r, 1480, HH + 40, 380, bank, (60, 170), (4, 9))
        return s

    return _cached(("pond", night, seed), build)


def water_shimmer(c, t, night=False, y0=820, y1=1220):
    """Animated glints on the pond surface (moon path at night)."""
    r = rng(7)
    for i in range(60):
        x = r.uniform(0, W)
        y = r.uniform(y0, y1)
        if night:
            x = 760 + (x - 540) * 0.25 + 20 * math.sin(t * 0.8 + i)
        ph = (t * 0.7 + r.random()) % 1
        a = math.sin(ph * math.pi) * (0.8 if night else 0.45)
        ln = r.uniform(14, 40)
        c.move_to(x - ln / 2, y)
        c.line_to(x + ln / 2, y)
        c.set_source_rgba(1, 0.97, 0.85, a)
        c.set_line_width(3)
        c.stroke()


def underwater(seed=3, night=False):
    """Pond seen from below. night=True: deep moonlit blue, a few faint cool moonbeams instead of sun rays."""
    def build():
        s, c = new_surface(W, HH)
        r = rng(seed)
        if night:
            _grad(c, 0, HH, [(0, "#4a6a86"), (0.22, "#24435e"), (0.6, "#16304a"), (1, "#0d1f33")])
        else:
            _grad(c, 0, HH, [(0, "#d9f0ec"), (0.22, "#8ccbc4"), (0.6, "#4f9a98"), (1, "#2a5f62")])
        c.paint()
        # surface band seen from below
        _grad(c, 0, 440, [(0, "#8aa4bc"), (1, "#4f6f8c")] if night else [(0, "#f6fbf2"), (1, "#bfe6dc")])
        c.rectangle(0, 0, W, 430)
        c.fill()
        c.move_to(0, 430)
        for x in range(0, W + 20, 20):
            c.line_to(x, 430 + 8 * math.sin(x / 50))
        c.line_to(W, 470)
        c.line_to(0, 470)
        c.close_path()
        c.set_source_rgba(1, 1, 1, 0.22 if night else 0.5)
        c.fill()
        for k in range(3 if night else 8):  # light rays (moonbeams at night)
            x0 = r.uniform(-100, W)
            c.move_to(x0, 430)
            c.line_to(x0 + 60, 430)
            c.line_to(x0 + 260, HH)
            c.line_to(x0 + 120, HH)
            c.close_path()
            g = cairo.LinearGradient(0, 430, 0, HH)
            g.add_color_stop_rgba(0, *((0.8, 0.9, 1, 0.12) if night else (1, 1, 0.92, 0.18)))
            g.add_color_stop_rgba(1, *((0.8, 0.9, 1, 0) if night else (1, 1, 0.92, 0)))
            c.set_source(g)
            c.fill()
        # bottom: sand, pebbles, plants
        _grad(c, 1650, HH, [(0, "#3a4a50"), (1, "#26323a")] if night else [(0, "#7f8a62"), (1, "#5a6044")])
        c.move_to(0, 1700)
        c.curve_to(300, 1650, 700, 1720, W, 1660)
        c.line_to(W, HH)
        c.line_to(0, HH)
        c.close_path()
        c.fill()
        for _ in range(40):
            ellipse(c, r.uniform(0, W), r.uniform(1690, HH - 20), r.uniform(8, 22), r.uniform(5, 12), r.uniform(0, 3))
            c.set_source_rgba(*mix(hexc("#8a8a7a"), hexc("#b0a88a"), r.random())[:3], 0.45 if night else 1)
            c.fill()
        for _ in range(18):
            x = r.uniform(0, W)
            hh = r.uniform(250, 600)
            c.move_to(x, 1720)
            c.curve_to(x + 40, 1720 - hh * 0.4, x - 40, 1720 - hh * 0.7, x + r.uniform(-30, 30), 1720 - hh)
            col = mix(hexc("#3f7a4a"), hexc("#5e9a5a"), r.random())
            c.set_source_rgba(*(mix(col, hexc("#16304a"), 0.55) if night else col))
            c.set_line_width(r.uniform(6, 12))
            c.stroke()
        return s

    return _cached(("underwater", seed, night), build)


def motes(c, t, n=40, y0=480, y1=1650, seed=5, col=(1, 1, 0.95), a=0.5):
    """Drifting particles (underwater bits / pollen)."""
    r = rng(seed)
    for _ in range(n):
        x0, yy, sp = r.uniform(0, W), r.uniform(y0, y1), r.uniform(6, 20)
        x = (x0 + sp * t) % W
        y = yy + 12 * math.sin(t * 0.6 + x0)
        c.arc(x, y, r.uniform(1.5, 3.5), 0, TAU)
        c.set_source_rgba(col[0], col[1], col[2], a * r.uniform(0.4, 1))
        c.fill()


def bubbles(c, t, x, y, n=8, seed=1, spread=40, speed=120, life=2.0, t0=0.0):
    r = rng(seed)
    for i in range(n):
        st = t0 + r.uniform(0, life)
        k = (t - st) / life
        if k < 0 or k > 1:
            continue
        bx = x + r.uniform(-spread, spread) + 8 * math.sin(t * 4 + i)
        by = y - k * speed * life
        c.arc(bx, by, r.uniform(4, 10) * (0.6 + 0.4 * k), 0, TAU)
        c.set_source_rgba(1, 1, 1, 0.6 * (1 - k))
        c.set_line_width(2)
        c.stroke()


def parchment(seed=9):
    def build():
        s, c = new_surface(W, HH)
        r = rng(seed)
        g = cairo.RadialGradient(W / 2, HH * 0.45, 100, W / 2, HH * 0.45, HH * 0.75)
        g.add_color_stop_rgba(0, *hexc("#f7ecd2"))
        g.add_color_stop_rgba(0.7, *hexc("#eadbb6"))
        g.add_color_stop_rgba(1, *hexc("#cbb185"))
        c.set_source(g)
        c.paint()
        for _ in range(70):
            ellipse(c, r.uniform(0, W), r.uniform(0, HH), r.uniform(40, 280), r.uniform(30, 200), r.uniform(0, 3))
            c.set_source_rgba(0.54, 0.42, 0.23, r.uniform(0.012, 0.03))
            c.fill()
        return s

    return _cached(("parchment", seed), build)


def vignette():
    def build():
        s, c = new_surface()
        g = cairo.RadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 0.72)
        g.add_color_stop_rgba(0, 0, 0, 0, 0)
        g.add_color_stop_rgba(1, 0, 0, 0, 0.32)
        c.set_source(g)
        c.paint()
        return s

    return _cached("vignette", build)


# ================================================================ the sea (episode 002)
def sea(seed=11, deep=False):
    """Shallow tropical sea, eastern Pacific: sunlit blue, surface at y~380, rippled sand on the bottom.
    Cymothoa exigua lives at 2-60 m, most records 2-20 m, so this is a bright, shallow, sandy place —
    not the green pond of `underwater()`. deep=True drops the light for the quieter beats."""
    def build():
        s, c = new_surface(W, HH)
        r = rng(seed)
        if deep:
            _grad(c, 0, HH, [(0, "#4e86a6"), (0.28, "#2f6788"), (0.65, "#1d4a68"), (1, "#123349")])
        else:
            _grad(c, 0, HH, [(0, "#bfe8f2"), (0.26, "#6fc0da"), (0.62, "#3b8fb4"), (1, "#1f5c80")])
        c.paint()
        # the surface, seen from below
        _grad(c, 0, 400, [(0, "#9fd6e4"), (1, "#5aa6c4")] if deep else [(0, "#eafaff"), (1, "#a6dcec")])
        c.rectangle(0, 0, W, 380)
        c.fill()
        c.move_to(0, 380)
        for x in range(0, W + 20, 20):
            c.line_to(x, 380 + 10 * math.sin(x / 46) + 4 * math.sin(x / 17))
        c.line_to(W, 430)
        c.line_to(0, 430)
        c.close_path()
        c.set_source_rgba(1, 1, 1, 0.26 if deep else 0.55)
        c.fill()
        for _ in range(4 if deep else 9):   # sun shafts
            x0 = r.uniform(-140, W)
            c.move_to(x0, 380)
            c.line_to(x0 + 70, 380)
            c.line_to(x0 + 300, HH)
            c.line_to(x0 + 130, HH)
            c.close_path()
            g = cairo.LinearGradient(0, 380, 0, HH)
            g.add_color_stop_rgba(0, 1, 1, 0.94, 0.07 if deep else 0.17)
            g.add_color_stop_rgba(1, 1, 1, 0.94, 0)
            c.set_source(g)
            c.fill()
        # sandy bottom with ripples
        _grad(c, 1620, HH, [(0, "#4a6272"), (1, "#36495a")] if deep else [(0, "#e2d2a6"), (1, "#bda87a")])
        c.move_to(0, 1690)
        c.curve_to(280, 1640, 720, 1716, W, 1656)
        c.line_to(W, HH)
        c.line_to(0, HH)
        c.close_path()
        c.fill()
        for k in range(14):     # ripple lines in the sand
            y = 1700 + k * 32
            c.move_to(0, y)
            for x in range(0, W + 30, 30):
                c.line_to(x, y + 7 * math.sin(x / 70 + k))
            c.set_source_rgba(0.42, 0.34, 0.22, (0.08 if deep else 0.16) * (1 - k / 18))
            c.set_line_width(5)
            c.stroke()
        for _ in range(26):     # shells and pebbles
            ellipse(c, r.uniform(0, W), r.uniform(1700, HH - 16), r.uniform(7, 19), r.uniform(4, 10), r.uniform(0, 3))
            c.set_source_rgba(*mix(hexc("#f0e6cc"), hexc("#c9b188"), r.random())[:3], 0.35 if deep else 0.85)
            c.fill()
        return s

    return _cached(("sea", seed, deep), build)


def gill_chamber(seed=12):
    """Inside Mango's gill cover: a warm dark chamber for the gill-arch scenes. The arches themselves are
    drawn per frame by characters.mango.draw_gill_chamber so they can move with the breathing."""
    def build():
        s, c = new_surface(W, HH)
        r = rng(seed)
        _grad(c, 0, HH, [(0, "#5d2a2c"), (0.4, "#45201f"), (1, "#2a1314")])
        c.paint()
        g = cairo.RadialGradient(W * 0.5, HH * 0.42, 80, W * 0.5, HH * 0.42, W * 0.95)
        g.add_color_stop_rgba(0, 0.78, 0.40, 0.36, 0.30)      # soft light from the gill slit
        g.add_color_stop_rgba(1, 0.30, 0.12, 0.12, 0.0)
        c.set_source(g)
        c.paint()
        for _ in range(40):    # damp tissue mottling
            ellipse(c, r.uniform(0, W), r.uniform(0, HH), r.uniform(60, 200), r.uniform(30, 110), r.uniform(0, 3))
            c.set_source_rgba(0.62, 0.26, 0.26, 0.05)
            c.fill()
        return s

    return _cached(("gill_chamber", seed), build)


def mouth_inside(seed=13):
    """Inside Mango's mouth, looking out: dark palate above, the tongue floor below, and a pale rim of
    daylight where the jaws open at the far end."""
    def build():
        s, c = new_surface(W, HH)
        r = rng(seed)
        _grad(c, 0, HH, [(0, "#3a1a18"), (0.34, "#5a2a26"), (0.58, "#7a4038"), (1, "#4a221e")])
        c.paint()
        g = cairo.RadialGradient(W * 0.5, HH * 0.46, 40, W * 0.5, HH * 0.46, W * 0.8)
        g.add_color_stop_rgba(0, 1.0, 0.86, 0.68, 0.34)       # daylight coming in through the gape
        g.add_color_stop_rgba(1, 0.4, 0.14, 0.12, 0.0)
        c.set_source(g)
        c.paint()
        # the palate arching overhead
        c.move_to(0, 0)
        c.line_to(W, 0)
        c.line_to(W, 470)
        c.curve_to(760, 640, 320, 640, 0, 470)
        c.close_path()
        _grad(c, 0, 620, [(0, "#24100e"), (1, "#7e3a30")])
        c.fill()
        c.move_to(0, 470)                                    # lit edge along the palate
        c.curve_to(320, 640, 760, 640, W, 470)
        c.set_source_rgba(1.0, 0.72, 0.58, 0.30)
        c.set_line_width(9)
        c.stroke()
        # the floor of the mouth
        c.move_to(0, HH)
        c.line_to(W, HH)
        c.line_to(W, 1420)
        c.curve_to(740, 1300, 340, 1300, 0, 1420)
        c.close_path()
        _grad(c, 1280, HH, [(0, "#a05c4c"), (1, "#361815")])
        c.fill()
        c.move_to(0, 1420)                                   # lit edge along the floor
        c.curve_to(340, 1300, 740, 1300, W, 1420)
        c.set_source_rgba(1.0, 0.76, 0.62, 0.34)
        c.set_line_width(9)
        c.stroke()
        for _ in range(34):    # wet mottling
            ellipse(c, r.uniform(0, W), r.uniform(0, HH), r.uniform(50, 180), r.uniform(26, 90), r.uniform(0, 3))
            c.set_source_rgba(0.95, 0.60, 0.48, 0.045)
            c.fill()
        return s

    return _cached(("mouth_inside", seed), build)
