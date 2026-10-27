"""L001 — The shapes of bacteria. A 3 x 2 board (5760 x 2160), one region per section (plan.md):

    A basic shapes | B cocci together | C rods
    F why shape    | E odd ones       | D curves          camera: A → B → C → D → E → F → whole board

    .venv/Scripts/python -m lessons.l001_bacteria_shapes.lesson stills
    .venv/Scripts/python -m lessons.l001_bacteria_shapes.lesson render
"""
import argparse
import math
import os

import cairo
import numpy as np

from engine import board as B
from engine import render
from engine.audio import mix
from engine.core import TAU
from engine.voice import narrate

from .script import SCRIPT

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "out")
REGION = {"A": (0, 0), "B": (1920, 0), "C": (3840, 0), "D": (3840, 1080), "E": (1920, 1080), "F": (0, 1080)}
LABEL, NOTE, TITLE = 64, 52, 100


# ================================================================ shapes
def _normals(cl):
    out = []
    for i in range(len(cl)):
        a, b = cl[max(i - 1, 0)], cl[min(i + 1, len(cl) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        out.append((-dy / d, dx / d))
    return out


def tube(cl, thick, seed=1):
    """Closed outline of a cell of width `thick` around a centre line, with round ends."""
    r = thick / 2
    ns = _normals(cl)
    left = [(p[0] + n[0] * r, p[1] + n[1] * r) for p, n in zip(cl, ns)]
    right = [(p[0] - n[0] * r, p[1] - n[1] * r) for p, n in zip(cl, ns)]

    def cap(p, n, start):
        phi = math.atan2(n[1], n[0]) + (math.pi if start else 0)
        return [(p[0] + r * math.cos(a), p[1] + r * math.sin(a)) for a in np.linspace(phi, phi - math.pi, 9)[1:-1]]
    loop = left + cap(cl[-1], ns[-1], False) + right[::-1] + cap(cl[0], ns[0], True) + [left[0], left[1]]
    return B.wobble(loop, seed, 1.0)


def line_cl(cx, cy, length, ang=0.0, n=12):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + (u - 0.5) * length * ca, cy + (u - 0.5) * length * sa) for u in np.linspace(0, 1, n)]


def arc_cl(cx, cy, length, bend, ang=0.0, n=30):
    """Centre line bent along an arc (bend = total turn in radians): a comma, a crescent."""
    R = length / bend
    pts = [(R * math.sin(u), R * (1 - math.cos(u))) for u in np.linspace(-bend / 2, bend / 2, n)]
    my = sum(p[1] for p in pts) / n
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + x * ca - (y - my) * sa, cy + x * sa + (y - my) * ca) for x, y in pts]


def sine_cl(cx, cy, length, amp, waves, n=90):
    return [(cx - length / 2 + length * u, cy + amp * math.sin(u * waves * TAU)) for u in np.linspace(0, 1, n)]


def rod(cx, cy, length, thick, ang=0.0, seed=1):
    return tube(line_cl(cx, cy, length - thick, ang), thick, seed)


def star6(cx, cy, r, seed=4):
    pts = [(cx + (r if i % 2 == 0 else r * 0.42) * math.cos(-math.pi / 2 + i * TAU / 12),
            cy + (r if i % 2 == 0 else r * 0.42) * math.sin(-math.pi / 2 + i * TAU / 12)) for i in range(13)]
    return B.wobble(pts, seed, 1.5)


def blob(cx, cy, r, seed=5):
    rr = np.random.default_rng(seed)
    pts = [(cx + r * k * math.cos(a), cy + r * k * 0.85 * math.sin(a))
           for a, k in zip(np.linspace(0, TAU, 9)[:-1], rr.uniform(0.7, 1.2, 8))]
    return B.spline(pts, closed=True, n=8)


def square(cx, cy, s, seed=6):
    h, r, pts = s / 2, s * 0.14, []
    for k, (qx, qy) in enumerate(((1, -1), (1, 1), (-1, 1), (-1, -1))):
        a0 = -math.pi / 2 + k * math.pi / 2
        ox, oy = cx + qx * (h - r), cy + qy * (h - r)
        pts += [(ox + r * math.cos(a), oy + r * math.sin(a)) for a in np.linspace(a0, a0 + math.pi / 2, 5)]
    return B.wobble(pts + pts[:2], seed, 1.0)


# ================================================================ the pen: one stroke at a time
class Pen:
    """Board items in sequence: each starts when it is due AND the marker is free."""

    def __init__(self, b):
        self.b, self.free = b, 0.0

    def _at(self, t):
        return max(t, self.free + 0.08)

    def write(self, txt, x, y, size, col, t, **kw):
        kw.setdefault("cps", 15)
        it = self.b.write(txt, x, y, size, col, self._at(t), **kw)
        self.free = it.t1
        return it

    def stroke(self, pts, t, dur, col, **kw):
        it = self.b.stroke(pts, self._at(t), dur, col, **kw)
        self.free = it.t1
        return it

    def hatch(self, pts, t, dur, col, **kw):
        it = self.b.hatch(pts, self._at(t), dur, col, **kw)
        self.free = it.t1
        return it

    def title(self, txt, x, y, t):
        self.free = self.b.title(txt, x, y, self._at(t), size=TITLE)
        return self.free

    def erase(self, x0, y0, x1, y1, t, dur, **kw):
        e = self.b.erase(x0, y0, x1, y1, self._at(t), dur, **kw)
        self.free = e.t1 + B.ERASER_IN
        return e

    def wait(self, t):
        self.free = max(self.free, t)


# ================================================================ the lesson
def build():
    b = B.Board(w=5760, h=2160)
    pen = Pen(b)

    def R(r, x, y):
        ox, oy = REGION[r]
        return ox + x, oy + y

    def go(r, t, dur=1.1):
        ox, oy = REGION[r]
        end = b.cam.move(t, dur, cx=ox + 960, cy=oy + 540)
        pen.wait(end)
        return end

    # ---- intro: the logo, wiped off before the hook
    t = b.logo(*R("A", 960, 470), 0.3)
    pen.wait(t + 0.5)
    e = pen.erase(*R("A", 330, 330), *R("A", 1590, 700), t + 0.5, 1.0, height=130, residue=0.0)
    voice, c, _, end = narrate(SCRIPT, os.path.join(HERE, "voice_cache"), t0=e.t1 + B.ERASER_IN + 0.3)
    w = lambda lid, word, k=0: c[lid].word(word, k)          # noqa: E731

    # ---- A: the hook, then the basic shapes
    cell = B.circle(*R("A", 960, 540), 150, seed=11)
    pen.stroke(cell, w("a1", "single"), 0.5, B.GREEN, width=8)
    pen.hatch(cell, w("a1", "cell"), 0.4, B.GREEN, gap=18)
    pen.write("about 1 micrometre", *R("A", 960, 800), NOTE, B.NAVY, w("a2", "micrometre"), align="center")
    for i, pts in enumerate([rod(*R("A", 400, 470), 170, 64, -0.3, seed=3),
                             tube(arc_cl(*R("A", 1520, 470), 150, 1.6, 0.2), 52, seed=4),
                             tube(sine_cl(*R("A", 400, 760), 200, 22, 2.0), 34, seed=5),
                             star6(*R("A", 1520, 760), 70)]):
        pen.stroke(pts, w("a3", "shapes") + i * 0.1, 0.35, [B.BLUE, B.RED, B.RED, B.GOLD_DK][i], width=7)
    pen.title("The basic shapes", *R("A", 120, 190), w("a4", "clue"))
    pen.erase(*R("A", 120, 330), *R("A", 1800, 930), c["a4"].end + 0.1, 1.1, height=200, residue=0.0)

    cx = {"co": 380, "ba": 960, "sp": 1540}
    coc = B.circle(*R("A", cx["co"], 520), 105, seed=12)
    pen.stroke(coc, w("a5", "Round"), 0.35, B.GREEN, width=8)
    pen.write("cocci", *R("A", cx["co"], 760), LABEL + 10, B.NAVY, w("a5", "cocci"), align="center")
    pen.write("kokkos: grain, berry", *R("A", cx["co"], 850), NOTE, B.GREEN, w("a5", "kokkos"), align="center")
    pen.hatch(coc, pen.free, 0.3, B.GREEN, gap=16)
    bac = rod(*R("A", cx["ba"], 520), 330, 120, -0.1, seed=13)
    pen.stroke(bac, w("a6", "Rod"), 0.45, B.BLUE, width=8)
    pen.write("bacilli", *R("A", cx["ba"], 760), LABEL + 10, B.NAVY, w("a6", "bacilli"), align="center")
    pen.write("little rod", *R("A", cx["ba"], 850), NOTE, B.BLUE, w("a6", "Latin"), align="center")
    pen.hatch(bac, pen.free, 0.3, B.BLUE)
    spi = tube(sine_cl(*R("A", cx["sp"], 520), 380, 44, 2.0), 46, seed=14)
    pen.stroke(spi, w("a7", "spirals"), 0.8, B.RED, width=8)
    pen.write("spirals", *R("A", cx["sp"], 760), LABEL + 10, B.NAVY, pen.free, align="center")
    pen.hatch(spi, pen.free, 0.4, B.RED)

    # ---- B: cocci that stick together
    go("B", c["a8"].end - 0.3)
    pen.title("Cocci that stick together", *R("B", 120, 190), c["b1"].start)
    G = B.GREEN
    one = B.circle(*R("B", 1330, 160), 46, seed=19)               # a cell splits in two... and the halves stay
    pen.stroke(one, w("b1", "splitting"), 0.3, G, width=7)
    pen.stroke(B.line(*R("B", 1330, 104), *R("B", 1330, 216), sag=0), pen.free, 0.2, B.GOLD_DK, width=5)
    pen.stroke([R("B", 1400, 160), R("B", 1470, 160), R("B", 1452, 146), R("B", 1470, 160), R("B", 1452, 174)],
               w("b1", "halves"), 0.2, B.NAVY, width=5)
    pen.stroke(B.circle(*R("B", 1530, 160), 40, seed=20), pen.free, 0.2, G, width=7)
    pen.stroke(B.circle(*R("B", 1610, 160), 40, seed=23), pen.free, 0.2, G, width=7)
    col = {"di": 210, "st": 570, "te": 960, "sa": 1300, "sf": 1650}

    def tag(key, txt, t):
        pen.write(txt, *R("B", col[key], 720), NOTE, B.GOLD_DK, t, align="center", cps=20)

    tag("di", "1 way", w("b2", "once"))
    pen.stroke(B.circle(*R("B", col["di"] - 42, 420), 42, seed=21), w("b2", "pair"), 0.25, G, width=7)
    pen.stroke(B.circle(*R("B", col["di"] + 42, 420), 42, seed=22), pen.free, 0.25, G, width=7)
    pen.write("diplo-", *R("B", col["di"], 580), LABEL, B.NAVY, w("b2", "diplococcus"), align="center")
    pen.write("double", *R("B", col["di"], 650), NOTE, G, w("b2", "double"), align="center")
    tag("st", "1 way", w("b3", "same"))
    for i in range(5):
        x = col["st"] - 150 + i * 75
        pen.stroke(B.circle(*R("B", x, 420 + 14 * math.sin(i * 1.3)), 36, seed=30 + i),
                   w("b3", "chains") + i * 0.05, 0.2, G, width=7)
    pen.write("strepto-", *R("B", col["st"], 580), LABEL, B.NAVY, w("b3", "streptococci"), align="center")
    pen.write("pliant, twisted", *R("B", col["st"], 650), NOTE, G, w("b4", "pliant"), align="center")
    pen.write("S. pyogenes: strep throat,", *R("B", 150, 810), NOTE, B.RED, w("b5", "pyogenes"))
    pen.write("rarely flesh-eating", *R("B", 150, 880), NOTE, B.RED, w("b5", "rarely"))
    tag("te", "2 ways", w("b6", "directions"))
    for i, (dx, dy) in enumerate(((-40, -40), (40, -40), (-40, 40), (40, 40))):
        pen.stroke(B.circle(*R("B", col["te"] + dx, 420 + dy), 38, seed=40 + i), w("b6", "square") + i * 0.05,
                   0.2, G, width=7)
    pen.write("tetrad: 4", *R("B", col["te"], 580), LABEL, B.NAVY, w("b6", "tetrad"), align="center")
    tag("sa", "3 ways", w("b7", "directions"))
    for i, (dx, dy) in enumerate(((-12, -68), (68, -68), (-12, 12), (68, 12))):   # the back layer of the cube
        pen.stroke(B.circle(*R("B", col["sa"] + dx, 430 + dy), 36, seed=50 + i), w("b7", "package") + i * 0.04,
                   0.18, G, width=5, alpha=0.45)
    for i, (dx, dy) in enumerate(((-40, -40), (40, -40), (-40, 40), (40, 40))):
        pen.stroke(B.circle(*R("B", col["sa"] + dx - 20, 430 + dy), 36, seed=54 + i), pen.free, 0.18, G, width=7)
    pen.write("sarcina: 8", *R("B", col["sa"], 580), LABEL, B.NAVY, w("b7", "sarcina"), align="center")
    tag("sf", "any way", w("b8", "any"))
    grapes = [(-66, -50), (0, -56), (66, -50), (-34, 4), (34, 4), (-66, 58), (0, 58), (66, 58), (0, 112)]
    for i, (dx, dy) in enumerate(grapes):
        pen.stroke(B.circle(*R("B", col["sf"] + dx, 380 + dy * 0.8), 32, seed=60 + i),
                   w("b8", "grapes") + i * 0.03, 0.13, G, width=7)
    pen.write("staphylo-", *R("B", col["sf"], 580), LABEL, B.NAVY, w("b9", "Staphylococcus"), align="center")
    pen.write("bunch of grapes", *R("B", col["sf"], 650), NOTE, G, w("b9", "Staphyle"), align="center")
    pen.write("S. aureus = golden grape-bunch berry", *R("B", 1010, 810), NOTE, B.GOLD_DK, w("b10", "aureus"))
    pen.write("skin infections; up 1 nose in 4", *R("B", 1010, 880), NOTE, B.RED, w("b12", "skin"))
    pen.write("(maybe yours)", *R("B", 1010, 950), NOTE, B.MUTED, w("b13", "Possibly"))
    for key, word in (("st", "Strepto"), ("sf", "Staphylo")):
        x = col[key]
        pen.stroke(B.line(*R("B", x - 110, 605), *R("B", x + 110, 603), sag=3), w("b14", word), 0.25, B.GOLD, width=9)

    # ---- C: rods
    go("C", c["b14"].end - 0.2)
    pen.title("Rods", *R("C", 120, 190), c["c1"].start)
    Bl = B.BLUE
    for i in range(3):
        pen.stroke(rod(*R("C", 230 + i * 140, 420 + 18 * (i % 2)), 130, 58, 0.12 * (i - 1), seed=70 + i),
                   w("c1", "chains") + i * 0.05, 0.2, Bl, width=7)
    pen.write("streptobacilli", *R("C", 370, 580), LABEL, B.NAVY, w("c1", "streptobacilli"), align="center")
    pen.write("Corynebacterium", *R("C", 960, 580), LABEL, B.NAVY, w("c2", "Corynebacterium"), align="center")
    for i in range(4):
        pen.stroke(rod(*R("C", 860 + i * 50, 420), 150, 40, math.pi / 2, seed=80 + i), w("c2", "side") + i * 0.05,
                   0.18, Bl, width=6)
    pen.stroke(rod(*R("C", 1100, 400), 130, 40, 1.1, seed=85), w("c2", "Vs"), 0.18, Bl, width=6)
    pen.stroke(rod(*R("C", 1150, 400), 130, 40, -1.1 + math.pi, seed=86), pen.free, 0.18, Bl, width=6)
    pen.stroke(rod(*R("C", 1270, 470), 100, 40, math.pi / 2, seed=87), w("c2", "Ys"), 0.15, Bl, width=6)
    pen.stroke(rod(*R("C", 1243, 385), 100, 40, -2.1, seed=88), pen.free, 0.15, Bl, width=6)
    pen.stroke(rod(*R("C", 1297, 385), 100, 40, -1.04, seed=89), pen.free, 0.15, Bl, width=6)
    pen.write("a fence, Vs and Ys", *R("C", 960, 650), NOTE, Bl, w("c2", "angles"), align="center")
    pen.stroke(rod(*R("C", 1560, 420), 240, 70, 0.05, seed=90), w("c4", "Clostridium"), 0.35, Bl, width=7)
    pen.write("C. botulinum", *R("C", 1560, 580), LABEL, B.NAVY, w("c4", "botulinum"), align="center")
    pen.write("most lethal toxin known", *R("C", 1560, 650), NOTE, B.RED, w("c4", "lethal"), align="center")
    pen.write("= Botox", *R("C", 1560, 720), NOTE, B.GOLD_DK, w("c5", "Botox"), align="center")
    cb = rod(*R("C", 330, 830), 110, 80, 0.0, seed=95)
    pen.stroke(cb, w("c6", "coccobacillus"), 0.3, Bl, width=7)
    pen.write("coccobacillus", *R("C", 330, 935), NOTE, B.NAVY, pen.free, align="center")
    pen.stroke(rod(*R("C", 760, 812), 70, 50, 0.0, seed=96), w("c7", "Haemophilus"), 0.2, Bl, width=6)
    pen.write("H. influenzae", *R("C", 980, 830), NOTE, B.NAVY, pen.free, align="center")
    pen.write("not the flu (a virus)", *R("C", 980, 900), NOTE, B.RED, w("c8", "doesn't"), align="center")
    pen.stroke(rod(*R("C", 1290, 812), 70, 50, 0.0, seed=97), w("c9", "Yersinia"), 0.2, Bl, width=6)
    pen.write("Y. pestis: Black Death", *R("C", 1580, 830), NOTE, B.NAVY, pen.free, align="center")
    pen.write("roughly 1/3 of Europe", *R("C", 1580, 900), NOTE, B.RED, w("c10", "third"), align="center")

    # ---- D: curves
    go("D", c["c10"].end + 0.1)
    pen.title("Curves", *R("D", 120, 190), c["d1"].start)
    Rd = B.RED
    vib = tube(arc_cl(*R("D", 330, 420), 200, 1.7, 0.15), 70, seed=101)
    pen.write("vibrio", *R("D", 330, 580), LABEL, B.NAVY, w("d2", "vibrio"), align="center")
    pen.stroke(vib, w("d2", "curved"), 0.4, Rd, width=8)
    pen.hatch(vib, w("d2", "comma"), 0.25, Rd)
    pen.write("= vibrates", *R("D", 330, 650), NOTE, Rd, w("d3", "vibrate"), align="center")
    pen.write("V. cholerae: cholera", *R("D", 330, 760), NOTE, B.NAVY, w("d4", "cholerae"), align="center")
    pen.write("tens of thousands a year", *R("D", 330, 830), NOTE, Rd, w("d5", "tens"), align="center")
    spl = tube(sine_cl(*R("D", 960, 420), 330, 40, 1.5), 50, seed=102)
    pen.write("spirillum: stiff", *R("D", 960, 580), LABEL, B.NAVY, w("d6", "spirillum"), align="center")
    pen.stroke(spl, w("d6", "spiral"), 0.7, Rd, width=8)
    for sx in (-1, 1):                                    # tufts of flagella at each end
        for k in range(3):
            x0, y0 = R("D", 960 + sx * 190, 420 + (k - 1) * 14)
            pen.stroke(B.spline([(x0, y0), (x0 + sx * 40, y0 - 18 + k * 18), (x0 + sx * 80, y0 + 8)], n=6),
                       w("d6", "tufts") + k * 0.04, 0.12, B.NAVY, width=4)
    pen.write("flagella = spinning tails", *R("D", 960, 650), NOTE, B.NAVY, w("d6", "flagella"), align="center",
              cps=20)
    sch = sine_cl(*R("D", 1590, 420), 380, 16, 7.0, n=200)
    pen.write("spirochete", *R("D", 1590, 580), LABEL, B.NAVY, w("d7", "spirochete"), align="center")
    pen.stroke(sch, w("d7", "corkscrew"), 0.8, Rd, width=9)
    pen.stroke(sine_cl(*R("D", 1590, 420), 380, 4, 7.0, n=200), w("d7", "inside"), 0.5, B.GOLD_DK, width=3)
    pen.write("flagella inside", *R("D", 1590, 650), NOTE, B.GOLD_DK, w("d7", "flagella"), align="center")
    pen.write("good in gels", *R("D", 1590, 760), NOTE, B.NAVY, w("d8", "gel"), align="center")
    pen.write("syphilis, Lyme disease", *R("D", 1590, 830), NOTE, Rd, w("d9", "syphilis"), align="center")

    # ---- E: the odd ones
    go("E", c["d9"].end + 0.1)
    pen.title("The odd ones", *R("E", 120, 190), c["e1"].start)
    trunk = B.spline([R("E", 210, 400), R("E", 290, 340), R("E", 370, 380), R("E", 450, 320)], n=8)
    pen.write("Streptomyces", *R("E", 330, 500), LABEL, B.NAVY, w("e2", "Streptomyces"), align="center")
    pen.stroke(trunk, w("e2", "threads"), 0.4, B.GREEN, width=7)
    for (x0, y0), (x1, y1) in (((260, 355), (240, 270)), ((330, 360), (360, 440)), ((400, 360), (430, 270))):
        pen.stroke(B.line(*R("E", x0, y0), *R("E", x1, y1), sag=6), pen.free, 0.15, B.GREEN, width=6)
    pen.write("exception: many cells", *R("E", 330, 640), NOTE, B.RED, pen.free, align="center", cps=20)
    pen.write("smell of rain, antibiotics", *R("E", 330, 570), NOTE, B.GREEN, w("e3", "geosmin"), align="center")
    st = star6(*R("E", 960, 350), 95)
    pen.stroke(st, w("e4", "stars"), 0.5, B.GOLD_DK, width=8)
    pen.hatch(st, pen.free, 0.3, B.GOLD)
    pen.write("star-shaped", *R("E", 960, 500), LABEL, B.NAVY, pen.free, align="center")
    cr = tube(arc_cl(*R("E", 1560, 320), 170, 1.3, 0.0), 56, seed=110)
    pen.write("Caulobacter", *R("E", 1590, 500), LABEL, B.NAVY, w("e5", "Caulobacter"), align="center")
    pen.stroke(cr, pen.free, 0.35, B.BLUE, width=7)
    pen.stroke(B.line(*R("E", 1645, 345), *R("E", 1720, 410), sag=2), w("e5", "stalk"), 0.2, B.BLUE, width=5)
    pen.stroke(B.circle(*R("E", 1730, 420), 13, seed=111), w("e5", "glue"), 0.15, B.GOLD_DK, width=7)
    pen.write("super-strong glue", *R("E", 1590, 570), NOTE, B.GOLD_DK, w("e5", "strongest"), align="center")
    pen.write("one swims, one stays", *R("E", 1590, 640), NOTE, B.BLUE, w("e6", "swims"), align="center")
    bl = blob(*R("E", 330, 760), 80)
    pen.stroke(bl, w("e7", "Mycoplasma"), 0.4, B.RED, width=7)
    pen.write("Mycoplasma", *R("E", 330, 890), LABEL, B.NAVY, pen.free, align="center")
    pen.write("no wall, no shape", *R("E", 330, 955), NOTE, B.RED, w("e7", "shape"), align="center")
    gi = tube(sine_cl(*R("E", 960, 760), 460, 10, 0.6), 34, seed=112)
    pen.stroke(gi, w("e8", "giants"), 0.7, B.GREEN, width=7)
    pen.write("Thiomargarita", *R("E", 960, 890), LABEL, B.NAVY, w("e9", "Thiomargarita"), align="center")
    pen.write("about 1 cm long!", *R("E", 960, 955), NOTE, B.GREEN, w("e9", "centimetre"), align="center")
    pen.write("(not to scale!)", *R("E", 960, 705), NOTE, B.MUTED, pen.free, align="center", cps=20)
    sq = square(*R("E", 1590, 760), 140)
    pen.write("Haloquadratum", *R("E", 1590, 890), LABEL, B.NAVY, w("e11", "Haloquadratum"), align="center")
    pen.stroke(sq, w("e11", "square"), 0.4, B.NAVY, width=7)
    pen.stroke(B.line(*R("E", 1515, 690), *R("E", 1665, 830), sag=0), w("e11", "not"), 0.2, B.RED, width=12)
    pen.stroke(B.line(*R("E", 1665, 690), *R("E", 1515, 830), sag=0), pen.free, 0.2, B.RED, width=12)
    pen.write("not a bacterium!*", *R("E", 1590, 955), NOTE, B.RED, w("e11", "bacterium"), align="center", cps=20)
    pen.write("*archaea: another domain of life", *R("E", 860, 190), NOTE, B.RED, w("e11", "archaeon"), cps=24)

    # ---- F: why shape matters
    go("F", c["e11"].end + 2.2)
    pen.title("Why shape matters", *R("F", 120, 190), c["f1"].start)
    wall = rod(*R("F", 330, 400), 300, 120, 0.0, seed=120)
    pen.stroke(wall, w("f2", "cell"), 0.45, B.GOLD_DK, width=16)
    pen.stroke(rod(*R("F", 330, 400), 270, 92, 0.0, seed=121), pen.free, 0.35, B.BLUE, width=6)
    pen.write("1. the wall", *R("F", 330, 580), LABEL, B.NAVY, pen.free, align="center")
    pen.write("no wall: no shape", *R("F", 330, 650), NOTE, B.RED, w("f3", "wall"), align="center")
    food = B.circle(*R("F", 960, 400), 70, seed=122)
    pen.stroke(food, w("f4", "food"), 0.3, B.GREEN, width=7)
    for k in range(8):
        a = k * TAU / 8
        x0, y0 = R("F", 960 + 140 * math.cos(a), 400 + 140 * math.sin(a))
        x1, y1 = R("F", 960 + 90 * math.cos(a), 400 + 90 * math.sin(a))
        h1 = (x1 + 22 * math.cos(a + 0.45), y1 + 22 * math.sin(a + 0.45))   # arrow pointing in: food goes in
        h2 = (x1 + 22 * math.cos(a - 0.45), y1 + 22 * math.sin(a - 0.45))
        pen.stroke([(x0, y0), (x1, y1), h1, (x1, y1), h2], w("f4", "surface") + k * 0.02, 0.1, B.GREEN, width=5)
    pen.write("2. food", *R("F", 960, 580), LABEL, B.NAVY, pen.free, align="center")
    pen.write("small = more surface per volume", *R("F", 960, 650), NOTE, B.GREEN, w("f4", "small"), align="center")
    pen.write("long threads: more surface", *R("F", 960, 720), NOTE, B.GREEN, w("f5", "threads"), align="center")
    pen.write("3. moving", *R("F", 1590, 580), LABEL, B.NAVY, w("f6", "getting"), align="center")
    pen.write("H. pylori", *R("F", 1590, 650), NOTE, B.NAVY, w("f6", "Helicobacter"), align="center")
    for k in range(3):                                    # mucus: wavy gold lines
        pen.stroke(sine_cl(*R("F", 1590, 330 + k * 70), 420, 8, 3.0, n=60), w("f6", "mucus") + k * 0.05, 0.2,
                   B.GOLD, width=5, alpha=0.6)
    pen.stroke(tube(sine_cl(*R("F", 1590, 400), 200, 18, 2.0), 30, seed=123), w("f6", "spiral"), 0.4, B.RED, width=7)
    pen.write("a bit faster in mucus", *R("F", 1590, 720), NOTE, B.RED, w("f6", "faster"), align="center")
    pen.write("scientists think: sticking, not being eaten", *R("F", 960, 860), NOTE, B.MUTED, w("f7", "scientists"),
              align="center")

    # ---- wrap: the whole board
    b.cam.frame(c["w1"].start - 0.6, 1.8, 0, 0, 5760, 2160, margin=150)   # the whole board, inside the safe area
    pen.wait(c["w1"].start + 1.2)
    for reg, word in (("A", "Spheres"), ("C", "rods"), ("D", "commas"), ("E", "stars")):
        x0, y0 = REGION[reg]
        box = [(x0 + 40, y0 + 40), (x0 + 1880, y0 + 40), (x0 + 1880, y0 + 1040), (x0 + 40, y0 + 1040), (x0 + 40, y0 + 40)]
        pen.stroke(B.wobble(box, 7, 3.0), w("w1", word), 0.4, B.GOLD, width=22, alpha=0.8)
    for reg in ("B", "F"):                               # "Every one of them": the rest of the board lights up
        x0, y0 = REGION[reg]
        box = [(x0 + 40, y0 + 40), (x0 + 1880, y0 + 40), (x0 + 1880, y0 + 1040), (x0 + 40, y0 + 1040), (x0 + 40, y0 + 40)]
        pen.stroke(B.wobble(box, 9, 3.0), w("w1", "Every"), 0.4, B.GOLD, width=22, alpha=0.8)

    # ---- outro: the board fades to a background and the series logo plays over it, with its jingle
    t = b.veil(c["w1"].end + 0.6, 1.2).t1
    t = b.logo(2880, 960, t - 0.3, size=600, sub="@teenytinyology")
    dur = t + 2.5
    return b, voice, c, dur


def thumbnail(path):
    """1280x720 YouTube thumbnail: the question in big marker letters, a row of shapes, the series logo."""
    b = B.Board()
    b.write("Bacteria come in", 110, 250, 150, B.NAVY, 0.0, dur=0.1)
    b.write("MORE shapes", 110, 440, 190, B.RED, 0.0, dur=0.1)
    b.write("than you think", 110, 600, 130, B.NAVY, 0.0, dur=0.1)
    b.stroke(B.line(100, 515, 1260, 507, sag=6), 0.0, 0.1, B.GOLD, width=22)
    shapes = [(B.circle(1440, 250, 85, seed=1), B.GREEN), (rod(1710, 250, 260, 100, -0.2, seed=2), B.BLUE),
              (tube(arc_cl(1460, 520, 220, 1.6, 0.1), 80, seed=3), B.RED), (star6(1730, 520, 110), B.GOLD_DK),
              (tube(sine_cl(1590, 790, 420, 46, 2.0), 54, seed=4), B.RED)]
    for pts, col in shapes:
        b.stroke(pts, 0.0, 0.1, col, width=12)
        b.hatch(pts, 0.0, 0.1, col)
    b.logo(560, 900, 0.0, size=90, sub="Lessons")
    return render.thumbnail(lambda c, t: b.render(c, t, "none"), 30.0, path)


def frame_fn(b):
    return lambda cc, t: b.render(cc, t, "marker")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["stills", "render"])
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    b, voice, c, dur = build()
    fn = frame_fn(b)
    print(f"duration {dur:.1f} s")
    if a.cmd == "stills":
        # each region finished (just before the camera leaves), plus the hook and the final board
        times = [c["a3"].end + 0.4, b.cam.moves[0][0] - 0.05] + [m[0] - 0.05 for m in b.cam.moves[1:]] + [dur - 0.2]
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
        paths = []
        for t in times:
            fn(cairo.Context(s), t)
            p = os.path.join(OUT, f"still_{t:06.2f}.png")
            s.write_to_png(p)
            paths.append(p)
        print(render.contact_sheet(paths, os.path.join(OUT, "sheet.png"), cols=3, width=2700))
        return
    wav = B.mixdown(b, voice, dur, os.path.join(OUT, "l001_audio.wav"))
    p = os.path.join(OUT, "l001-bacteria-shapes.mp4")
    render.encode(fn, dur, p, size=(1920, 1080), audio_wav=wav)
    print(p, f"{mix.measure_lufs(p):.1f} LUFS")
    print(thumbnail(os.path.join(OUT, "thumbnail.png")))


if __name__ == "__main__":
    main()
