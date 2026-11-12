"""L002 — Quorum sensing. A 3 x 2 board (5760 x 2160), one region per section (plan.md):

    A the glowing squid | B sensing a crowd  | C the circuit
    F jamming + limits  | E attack, or leave | D languages        camera: A → B → C → D → E → F → whole board

The gold signal dots are the throughline: they appear in every region.

    .venv/Scripts/python -m lessons.l002_quorum_sensing.lesson stills
    .venv/Scripts/python -m lessons.l002_quorum_sensing.lesson render
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
from lessons.l001_bacteria_shapes.lesson import Pen, arc_cl, blob, rod, tube

from .script import SCRIPT

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "out")
REGION = {"A": (0, 0), "B": (1920, 0), "C": (3840, 0), "D": (3840, 1080), "E": (1920, 1080), "F": (0, 1080)}
LABEL, NOTE, TITLE = 64, 52, 100
SIG = B.GOLD_DK          # the signal molecules


# ================================================================ drawings
def arrow(x0, y0, x1, y1, head=22, sag=0.0, seed=5):
    """A straight (or slightly sagging) marker arrow, drawn as one stroke ending in its head."""
    a = math.atan2(y1 - y0, x1 - x0)
    h1 = (x1 - head * math.cos(a - 0.45), y1 - head * math.sin(a - 0.45))
    h2 = (x1 - head * math.cos(a + 0.45), y1 - head * math.sin(a + 0.45))
    return B.line(x0, y0, x1, y1, sag=sag, seed=seed) + [h1, (x1, y1), h2]


def curve_arrow(pts, head=24):
    sp = B.spline(pts, n=10)
    (ax, ay), (bx, by) = sp[-3], sp[-1]
    a = math.atan2(by - ay, bx - ax)
    return sp + [(bx - head * math.cos(a - 0.45), by - head * math.sin(a - 0.45)), (bx, by),
                 (bx - head * math.cos(a + 0.45), by - head * math.sin(a + 0.45))]


def dot(x, y, seed=1):
    return B.circle(x, y, 5, seed=seed)


def ahl(x, y, s=1.0, seed=1):
    """An AHL: a five-sided ring with a zig-zag fatty tail. Returns (ring, tail)."""
    r = 24 * s
    ring = [(x + r * math.cos(-math.pi / 2 + k * TAU / 5 + math.pi), y + r * math.sin(-math.pi / 2 + k * TAU / 5 + math.pi))
            for k in range(6)]
    tail = [(x + r * 0.95 + k * 22 * s, y + (0 if k % 2 == 0 else -14 * s)) for k in range(7)]
    return B.wobble(ring, seed, 1.0), B.wobble(tail, seed + 1, 0.8)


def squid(cx, cy, s=1.0):
    """Side view of a bobtail squid swimming left: one body outline, the fin, the eye, the arms.
    Returns dict of polylines plus the light organ's centre."""
    P = lambda x, y: (cx + x * s, cy + y * s)              # noqa: E731
    body = B.spline([P(-170, 0), P(-150, -50), P(-95, -70), P(-40, -66), P(40, -92), P(150, -88), P(228, -40),
                     P(248, 12), P(208, 68), P(100, 92), P(0, 88), P(-60, 72), P(-140, 52)], closed=True, n=8)
    fin = B.spline([P(40, -90), P(80, -150), P(160, -148), P(196, -76)], n=10)
    eye = B.circle(*P(-108, -12), 30 * s, seed=41)
    pupil = B.circle(*P(-112, -10), 13 * s, seed=42)
    arms = []
    for k, dy in enumerate((-30, -12, 6, 24, 40)):
        x0, y0 = P(-166, dy * 0.8)
        pts = [(x0 - i * 26 * s, y0 + dy * 0.25 * i * s + 8 * s * math.sin(i * 1.3 + k)) for i in range(6)]
        arms.append(B.spline(pts, n=6))
    organ = B.wobble([(cx + 50 * s + 42 * s * math.cos(a), cy + 52 * s + 18 * s * math.sin(a))
                      for a in np.linspace(0, TAU * 1.04, 30)], 43, 1.0)
    return dict(body=body, fin=fin, eye=eye, pupil=pupil, arms=arms, organ=organ, belly=(cx + 50 * s, cy + 72 * s))


def comma(cx, cy, size=1.0, ang=0.0, seed=1):
    return tube(arc_cl(cx, cy, 80 * size, 1.6, ang), 30 * size, seed=seed)


def box(x0, y0, x1, y1, r=40, seed=3):
    pts = []
    for (qx, qy, a0) in ((x1 - r, y0 + r, -math.pi / 2), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, math.pi / 2),
                         (x0 + r, y0 + r, math.pi)):
        pts += [(qx + r * math.cos(a), qy + r * math.sin(a)) for a in np.linspace(a0, a0 + math.pi / 2, 6)]
    return B.wobble(pts + pts[:2], seed, 1.5)


# ================================================================ the lesson
class LPen(Pen):
    lags = []

    def _at(self, t):
        at = max(t, self.free + 0.08)
        self.lags.append((at - t, t, at))
        return at

    def title(self, txt, x, y, t, size=TITLE, cps=11):
        tt = self.write(txt, x, y, size, B.NAVY, t, cps=cps)
        return self.stroke(B.line(x - 10, y + size * 0.3, x + tt.w + 10, y + size * 0.27, sag=5), pen_free(self), 0.4,
                           B.GOLD, width=size * 0.1).t1

    def dots(self, pts, t, step=0.05, seed=0):
        for i, (x, y) in enumerate(pts):
            self.stroke(dot(x, y, seed + i), t if i == 0 else self.free, step, SIG, width=12)


def pen_free(p):
    return p.free


def build():
    b = B.Board(w=5760, h=2160)
    pen = LPen(b)
    rr = np.random.default_rng(2)

    def R(r, x, y):
        ox, oy = REGION[r]
        return ox + x, oy + y

    def RP(r, pts):
        ox, oy = REGION[r]
        return [(ox + x, oy + y) for x, y in pts]

    def step(r, t):
        b.write(str("ABCDEF".index(r) + 1), *R(r, 72, 190), NOTE + 10, B.GOLD_DK, t, cps=20)

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

    # ---- A: the glowing squid
    moon = B.circle(*R("A", 860, 330), 55, seed=9)
    pen.stroke(moon, w("a1", "moonlit"), 0.35, B.GOLD_DK, width=7)
    pen.hatch(moon, pen.free, 0.25, B.GOLD, alpha=0.45)
    sq = squid(*R("A", 470, 500))
    pen.stroke(sq["body"], w("a1", "squid"), 0.7, B.NAVY, width=7)
    pen.stroke(sq["fin"], pen.free, 0.2, B.NAVY, width=7)
    pen.stroke(sq["eye"], pen.free, 0.15, B.NAVY, width=6)
    pen.hatch(sq["pupil"], pen.free, 0.1, B.NAVY, alpha=0.9, gap=8, width=10)
    for arm in sq["arms"]:
        pen.stroke(arm, pen.free, 0.08, B.NAVY, width=6)
    sand = B.line(*R("A", 110, 915), *R("A", 960, 912), sag=-6, seed=8)
    pen.stroke(sand, w("a1", "shadow") - 0.3, 0.3, B.GOLD_DK, width=6)
    shadow = B.wobble([(R("A", 470, 880)[0] + 190 * math.cos(a), R("A", 470, 880)[1] + 16 * math.sin(a))
                       for a in np.linspace(0, TAU * 1.02, 40)], 12, 1.0)
    pen.hatch(shadow, pen.free, 0.4, B.MUTED, alpha=0.6, gap=10)
    pen.write("Hawaiian bobtail squid", *R("A", 1425, 305), LABEL, B.NAVY, w("a2", "Hawaiian"), align="center")
    pen.write("active at night", *R("A", 1425, 368), NOTE, B.MUTED, w("a2", "active"), align="center")
    ex, ey = R("A", 190, 735)                              # seen from below: an eye, looking up past the squid
    pen.stroke(B.spline([(ex - 40, ey), (ex, ey - 22), (ex + 40, ey)], n=6) + B.spline([(ex + 40, ey), (ex, ey + 22),
               (ex - 40, ey)], n=6), w("a2", "below"), 0.25, B.NAVY, width=5)
    pen.hatch(B.circle(ex, ey, 10, seed=17), pen.free, 0.08, B.NAVY, alpha=0.9, gap=6, width=8)
    for (x0, y0), (x1, y1) in (((230, 712), (420, 600)), ((740, 420), (815, 372))):
        n_ = int(math.hypot(x1 - x0, y1 - y0) / 34)
        for k in range(n_):
            u0, u1 = k / n_, (k + 0.5) / n_
            pen.stroke([R("A", x0 + (x1 - x0) * u0, y0 + (y1 - y0) * u0), R("A", x0 + (x1 - x0) * u1, y0 + (y1 - y0) * u1)],
                       pen.free, 0.02, B.MUTED, width=4)
    bx, by = sq["belly"]
    # the glow, aimed down: a soft cone of light fanning out under the belly (no outline, so it can't read as legs)
    cone = B.wobble([(bx - 55, by + 16), (bx + 55, by + 16), (bx + 125, by + 175), (bx - 125, by + 175),
                     (bx - 55, by + 16)], 21, 2.0)
    pen.hatch(cone, w("a3", "glows"), 0.6, B.GOLD, alpha=0.3, gap=14)
    inner = B.wobble([(bx - 30, by + 16), (bx + 30, by + 16), (bx + 60, by + 120), (bx - 60, by + 120),
                      (bx - 30, by + 16)], 22, 2.0)
    pen.hatch(inner, pen.free, 0.3, B.GOLD, alpha=0.35, gap=12)
    pen.erase(*R("A", 260, 850), *R("A", 680, 900), w("a3", "disappears"), 0.6, height=60, residue=0.05)
    pen.stroke(sand, pen.free, 0.2, B.GOLD_DK, width=6)    # the eraser nicked the sand: redraw it
    pen.write("counter-illumination", *R("A", 470, 840), NOTE, B.GOLD_DK, w("a4", "counter"), align="center")
    pen.title("The glowing squid", *R("A", 120, 190), c["a4"].end)
    step("A", pen.free)
    pen.hatch(sq["organ"], w("a5", "bacteria"), 0.3, B.GOLD, alpha=0.8, gap=8)
    pen.stroke(sq["organ"], w("a5b", "pouch"), 0.3, B.GOLD_DK, width=5)
    pen.stroke(arrow(*R("A", 720, 650), bx + 30, by - 10, head=18), w("a5b", "light"), 0.25, B.NAVY, width=5)
    pen.write("light organ", *R("A", 820, 690), NOTE, B.NAVY, pen.free, align="center")
    pen.write("reflector + lens", *R("A", 820, 760), NOTE, B.GOLD_DK, w("a5b", "reflector"), align="center")
    pen.write("its glowing bacteria:", *R("A", 1425, 432), NOTE, B.GOLD_DK, w("a6", "called"), align="center", cps=22)
    pen.write("Aliivibrio fischeri", *R("A", 1425, 497), LABEL, B.NAVY, w("a6", "Aliivibrio"), align="center")
    pen.write("Vibrio fischeri until 2007", *R("A", 1425, 560), NOTE, B.MUTED, w("a6", "2007"), align="center")
    v_w = b.items[-1].w
    pen.write("DNA: its own branch", *R("A", 1425, 620), NOTE, B.BLUE, w("a6b", "branch"), align="center")
    pen.stroke(curve_arrow(RP("A", [(1150, 548), (1125, 515), (1160, 480)]), head=14), w("a6b", "new"), 0.2,
               B.GOLD_DK, width=4)
    pen.write("= \"the other Vibrio\"", *R("A", 1425, 680), NOTE, B.GOLD_DK, w("a6b", "other"), align="center")
    pen.stroke(B.line(*R("A", 1425 - v_w / 2, 577), *R("A", 1425 + v_w / 2, 575), sag=3), w("a6c", "old"), 0.3,
               B.GOLD, width=7)
    crowd = [(1545, 805), (1605, 795), (1660, 808), (1555, 865), (1615, 872), (1665, 860)]
    glow = B.circle(*R("A", 1600, 835), 100, seed=31)
    pen.hatch(glow, w("a7", "lots"), 0.35, B.GOLD, alpha=0.5)
    for i, (x, y) in enumerate(crowd):
        pen.stroke(rod(*R("A", x, y), 56, 26, (0.25, -0.2, 0.3, -0.15, 0.2, -0.3)[i], seed=33 + i), pen.free, 0.08,
                   B.BLUE, width=5)
    pen.write("crowd: glow", *R("A", 1600, 965), NOTE, B.GOLD_DK, pen.free, align="center")
    pen.stroke(rod(*R("A", 1170, 835), 70, 30, 0.3, seed=40), w("a7", "Alone"), 0.15, B.MUTED, width=5)
    pen.write("alone: dark", *R("A", 1170, 965), NOTE, B.MUTED, pen.free, align="center")

    # ---- B: sensing a crowd (the section title is the question)
    go("B", c["a8"].start - 0.2)
    pen.title("How does one cell know it's in a crowd?", *R("B", 120, 190), w("a8", "single"), size=84, cps=17)
    step("B", pen.free)
    few = [(210, 440), (420, 380), (330, 540)]
    pen.stroke(rod(*R("B", *few[0]), 90, 40, 0.3, seed=50), w("b1", "cell"), 0.15, B.BLUE, width=6)
    pen.dots(RP("B", [(265, 420), (285, 470)]), w("b1", "leaks"))
    pen.write("signal", *R("B", 330, 300), NOTE, SIG, w("b1", "signal"), align="center")
    for i, (x, y) in enumerate(few[1:]):
        pen.stroke(rod(*R("B", x, y), 90, 40, -0.4 + i, seed=51 + i), w("b2", "few") + i * 0.05, 0.12, B.BLUE, width=6)
    for k, a in enumerate((0.2, 1.0, 2.6, 3.5, 5.7)):              # drifting away: dots far out, arrows outward
        x0, y0 = 330 + 150 * math.cos(a), 460 + 95 * math.sin(a)
        pen.dots(RP("B", [(x0, y0)]), w("b2", "drifts") + k * 0.04, seed=60 + k)
        pen.stroke(arrow(*R("B", x0 + 18 * math.cos(a), y0 + 18 * math.sin(a)),
                         *R("B", x0 + 70 * math.cos(a), y0 + 70 * math.sin(a)), head=12), pen.free, 0.07, SIG, width=4)
    pen.write("few: it drifts away", *R("B", 330, 680), NOTE, B.NAVY, pen.free, align="center")
    tank = box(*R("B", 690, 330), *R("B", 1110, 590))
    pen.stroke(tank, w("b3", "many"), 0.3, B.NAVY, width=5)
    b.hatch(tank, w("b3", "builds"), 0.4, B.GOLD, alpha=0.35)   # under the cells, so they stay blue
    t0 = pen.free                                          # the crowd appears in one quick burst
    for i in range(12):
        x, y = 745 + (i % 4) * 92 + (25 if (i // 4) % 2 else 0), 390 + (i // 4) * 80
        b.stroke(rod(*R("B", x, y), 80, 34, rr.uniform(-0.6, 0.6), seed=70 + i), t0 + i * 0.06, 0.12, B.BLUE, width=5)
    pen.wait(max(t0 + 0.8, w("b3", "builds")))
    t0 = pen.free
    for i in range(10):
        b.stroke(dot(*R("B", 720 + rr.uniform(0, 370), 350 + rr.uniform(0, 220)), 80 + i), t0 + i * 0.04, 0.06, SIG,
                 width=12)
    pen.wait(t0 + 0.5)
    pen.write("many, packed: it builds up", *R("B", 900, 680), NOTE, B.NAVY, pen.free, align="center", cps=24)
    gx, gy, gw, gh = 1340, 620, 450, 300                   # the graph: signal vs number of cells
    pen.stroke(B.line(*R("B", gx, gy), *R("B", gx, gy - gh), sag=0) + [R("B", gx - 12, gy - gh + 20), R("B", gx, gy - gh),
               R("B", gx + 12, gy - gh + 20)], c["b4"].start - 0.3, 0.2, B.NAVY, width=5)
    pen.stroke(B.line(*R("B", gx, gy), *R("B", gx + gw, gy), sag=0), pen.free, 0.2, B.NAVY, width=5)
    curve = [R("B", gx + gw * u, gy - 10 - (gh - 50) * (u ** 2.2)) for u in np.linspace(0, 1, 30)]
    pen.stroke(curve, w("b4", "certain"), 0.4, SIG, width=7)
    ty = gy - 0.45 * gh
    for k in range(7):
        x0 = gx + 10 + k * 64
        pen.stroke([R("B", x0, ty), R("B", x0 + 38, ty)], w("b4", "threshold") + k * 0.02, 0.04, B.RED, width=5)
    pen.write("threshold", *R("B", gx + 115, ty - 22), NOTE, B.RED, pen.free, align="center", cps=24)
    pen.write("genes ON", *R("B", gx + gw - 30, gy - gh - 10), NOTE, B.GREEN, w("b4", "switch"), align="center")
    pen.write("cells", *R("B", gx + gw - 40, gy + 60), NOTE, B.NAVY, pen.free, align="center", cps=20)
    pen.write("signal", *R("B", gx + 25, gy - gh - 10), NOTE, SIG, pen.free, cps=20)
    pen.write("quorum sensing", *R("B", 120, 830), LABEL + 16, B.NAVY, w("b5", "quorum"))
    qs_w = b.items[-1].w
    pen.stroke(B.line(*R("B", 110, 860), *R("B", 130 + qs_w, 857), sag=4), pen.free, 0.3, B.GOLD, width=9)
    pen.write("quorum: enough members present for a meeting to decide", *R("B", 120, 930), NOTE, B.NAVY,
              w("b6", "smallest"), cps=24)
    pen.write("Latin: \"of whom\"", *R("B", 200 + qs_w, 830), NOTE, B.MUTED, w("b7", "Latin"))
    pen.write("(autoinducer)", *R("B", gx + 25, gy - gh + 55), NOTE, SIG, w("b8", "autoinducer"))
    pen.write("first clue: 1970, glowing sea bacteria", *R("B", 1360, 760), NOTE, B.MUTED, w("b9", "1970"),
              align="center", cps=24)
    flask = B.wobble(RP("B", [(1640, 800), (1640, 840), (1590, 930), (1600, 945), (1760, 945), (1770, 930),
                             (1720, 840), (1720, 800)]), 300, 1.2)
    pen.stroke(flask, w("b9", "light"), 0.4, B.NAVY, width=5)
    broth = B.wobble(RP("B", [(1612, 895), (1748, 895), (1770, 930), (1760, 945), (1600, 945), (1590, 930),
                             (1612, 895)]), 301, 1.0)
    pen.hatch(broth, pen.free, 0.25, B.GOLD, alpha=0.25)
    pen.stroke(rod(*R("B", 1640, 922), 40, 18, 0.2, seed=302), pen.free, 0.08, B.BLUE, width=4)
    pen.dots(RP("B", [(1690, 912), (1720, 928), (1665, 935), (1735, 908), (1700, 935)]), w("b9", "broth"), 0.04, 303)
    pen.stroke(arrow(*R("B", 1655, 915), *R("B", 1685, 908), head=9), w("b9", "themselves"), 0.1, SIG, width=3)

    # ---- C: the circuit
    go("C", c["c1"].start - 0.4)
    pen.title("The circuit", *R("C", 120, 190), c["c1"].start)
    step("C", pen.free)
    cell = rod(*R("C", 700, 560), 1050, 440, 0.0, seed=90)
    pen.stroke(cell, w("c1", "inside"), 0.7, B.BLUE, width=9)
    luxi = B.circle(*R("C", 400, 530), 50, seed=91)
    pen.stroke(luxi, w("c2", "LuxI"), 0.3, B.GREEN, width=7)
    pen.hatch(luxi, pen.free, 0.2, B.GREEN)
    pen.write("LuxI", *R("C", 400, 450), LABEL, B.NAVY, pen.free, align="center")
    ring, tail = ahl(*R("C", 520, 520), 0.8, seed=92)
    pen.stroke(arrow(*R("C", 455, 530), *R("C", 495, 525), head=12), w("c2", "signal"), 0.1, B.NAVY, width=4)
    pen.stroke(ring, w("c2", "AHL"), 0.2, SIG, width=6)
    pen.stroke(tail, pen.free, 0.15, SIG, width=6)
    pen.write("AHL", *R("C", 1600, 300), LABEL + 6, B.NAVY, w("c2", "AHL"), align="center")
    pen.write("acyl-homoserine lactone", *R("C", 1585, 550), 50, B.MUTED, w("c2", "acyl"), align="center", cps=22)
    ring2, tail2 = ahl(*R("C", 1520, 390), 1.8, seed=93)
    pen.stroke(ring2, w("c2", "ring"), 0.3, SIG, width=8)
    pen.write("ring", *R("C", 1500, 480), NOTE, SIG, pen.free, align="center", cps=20)
    pen.stroke(tail2, w("c2", "fatty"), 0.3, SIG, width=8)
    pen.write("fatty tail", *R("C", 1680, 480), NOTE, SIG, pen.free, align="center", cps=20)
    # in and out through the membrane (top edge of the cell, y 340)
    pen.stroke(arrow(*R("C", 600, 420), *R("C", 600, 260), head=16), w("c3", "slip"), 0.2, SIG, width=5)
    pen.stroke(arrow(*R("C", 680, 260), *R("C", 680, 420), head=16), w("c3", "In", 1), 0.2, SIG, width=5)
    pen.dots(RP("C", [(560, 290), (720, 280), (500, 260), (790, 300), (640, 245)]), pen.free, 0.04, 100)
    cup = B.spline(RP("C", [(850, 490), (860, 560), (900, 580), (940, 560), (950, 490)]), n=8)
    pen.stroke(cup, w("c4", "LuxR"), 0.3, B.NAVY, width=8)
    pen.write("LuxR", *R("C", 900, 450), LABEL, B.NAVY, pen.free, align="center")
    pen.dots(RP("C", [(900, 545)]), w("c5", "grabs"), seed=110)
    dna = [B.spline(RP("C", [(330 + i * 60, 680 + (14 if (i + k) % 2 else -14)) for i in range(13)]), n=6)
           for k in (0, 1)]
    pen.stroke(dna[0], w("c5", "switches") - 0.4, 0.25, B.NAVY, width=4)
    pen.stroke(dna[1], pen.free, 0.25, B.NAVY, width=4)
    genes = box(*R("C", 780, 652), *R("C", 1020, 708), r=14, seed=111)
    pen.stroke(arrow(*R("C", 900, 595), *R("C", 900, 645), head=14), pen.free, 0.1, B.NAVY, width=4)
    pen.hatch(genes, w("c5", "light"), 0.3, B.GOLD, alpha=0.6)
    pen.write("light genes", *R("C", 900, 755), NOTE, B.GOLD_DK, pen.free, align="center", cps=22)
    loop = curve_arrow(RP("C", [(790, 715), (620, 760), (430, 720), (395, 590)]))
    pen.stroke(loop, w("c6", "luxI"), 0.5, B.GREEN, width=7)
    pen.write("more LuxI", *R("C", 560, 625), NOTE, B.GREEN, pen.free, align="center", cps=22)
    pen.write("loop: more signal makes more signal", *R("C", 175, 880), NOTE, B.GREEN, w("c7", "more"), cps=22)
    pen.write("auto = made by the cells themselves", *R("C", 175, 950), NOTE, B.NAVY, w("c7b", "themselves"), cps=22)
    pen.write("open sea: dark", *R("C", 1600, 640), NOTE, B.MUTED, w("c8", "open"), align="center")
    pen.write("light organ: glow", *R("C", 1600, 705), NOTE, B.GOLD_DK, w("c8", "Packed"), align="center")
    for k in range(5):                                     # the glow out of the cell's end, on "glow"
        a = -0.8 + k * 0.4
        x0, y0 = R("C", 1245, 560)
        pen.stroke(B.line(x0 + 20 * math.cos(a), y0 + 60 * math.sin(a), x0 + 68 * math.cos(a), y0 + 140 * math.sin(a),
                          sag=0, seed=120 + k), w("c8", "glow") + k * 0.03, 0.06, B.GOLD, width=9)
    pen.write("rent: paid in light", *R("C", 1600, 770), NOTE, B.GOLD_DK, w("c9", "rent"), align="center")
    sun = B.circle(*R("C", 1370, 835), 22, seed=130)
    pen.stroke(sun, w("c10", "dawn"), 0.15, B.GOLD_DK, width=6)
    pen.write("dawn:", *R("C", 1415, 855), NOTE, B.RED, pen.free)
    dw = b.items[-1].w
    pen.write("90%+ vented", *R("C", 1430 + dw, 855), NOTE, B.RED, w("c10", "Ninety"))
    mn = B.spline(RP("C", [(1385, 880), (1360, 905), (1370, 935), (1395, 945)]), n=6)
    pen.stroke(mn, w("c11", "regrow"), 0.12, B.NAVY, width=6)
    pen.write("nightfall: full again", *R("C", 1640, 930), NOTE, B.NAVY, pen.free, align="center")

    # ---- D: languages
    go("D", c["c11"].end + 0.3)
    pen.title("Different signals", *R("D", 120, 190), c["d1"].start)
    step("D", pen.free)
    ring, tail = ahl(*R("D", 280, 430), 1.4, seed=140)
    pen.write("squid bacteria,", *R("D", 330, 680), NOTE, B.NAVY, w("d2", "squid"), align="center")
    pen.stroke(ring, w("d2", "AHLs"), 0.25, SIG, width=8)
    pen.stroke(tail, pen.free, 0.2, SIG, width=8)
    pen.write("AHL", *R("D", 330, 600), LABEL, B.NAVY, pen.free, align="center")
    pen.write("Pseudomonas", *R("D", 330, 750), NOTE, B.NAVY, w("d2", "Pseudomonas"), align="center")
    pen.write("Staphylococcus,", *R("D", 960, 770), NOTE, B.NAVY, w("d3", "Staphylococcus"), align="center")
    pen.write("Streptococcus", *R("D", 960, 840), NOTE, B.NAVY, w("d3", "Streptococcus"), align="center")
    pep = [(840 + i * 50, 370 + (8 if i % 2 else -8)) for i in range(6)]
    pen.write("peptides", *R("D", 960, 600), LABEL, B.NAVY, w("d3", "short"), align="center")
    for i, (x, y) in enumerate(pep):
        pen.stroke(B.circle(*R("D", x, y), 20, seed=150 + i), pen.free, 0.06, B.GREEN, width=6)
    pen.write("amino-acid chains", *R("D", 960, 670), NOTE, B.GREEN, w("d3", "amino"), align="center", cps=22)
    mem = B.line(*R("D", 790, 500), *R("D", 1130, 500), sag=0, seed=151)
    pen.stroke(mem, w("d4", "pumps"), 0.3, B.BLUE, width=8)
    pen.stroke(arrow(*R("D", 830, 550), *R("D", 830, 445), head=14), pen.free, 0.15, B.GREEN, width=5)   # pumped out
    pen.stroke(B.spline(RP("D", [(940, 420), (960, 452), (960, 495)]), n=4) + B.spline(RP("D", [(980, 420), (960, 452)]), n=4),
               w("d4", "receptors"), 0.25, B.RED, width=6)
    pen.write("receptor", *R("D", 1080, 465), NOTE, B.RED, pen.free, align="center", cps=22)
    pen.write("AI-2", *R("D", 1590, 600), LABEL, B.NAVY, w("d5", "AI"), align="center")
    for k, (x, col) in enumerate(((1460, B.BLUE), (1590, B.GREEN), (1720, B.RED))):
        pen.stroke(rod(*R("D", x, 440), 110, 50, 0.4 * (k - 1), seed=160 + k), w("d5", "many") + k * 0.05, 0.15, col,
                   width=6)
        pen.dots(RP("D", [(x + 10, 380)]), pen.free, seed=165 + k)
    pen.write("made by many species", *R("D", 1590, 670), NOTE, B.NAVY, w("d5", "kinds"), align="center")
    pen.write("a shared signal?", *R("D", 1590, 770), NOTE, SIG, w("d6", "shared"), align="center")
    pen.write("still debated", *R("D", 1590, 840), NOTE, B.MUTED, w("d6", "debated"), align="center")

    # ---- E: attack, or leave
    go("E", c["d6"].end + 0.2)
    pen.title("Attack, or leave", *R("E", 120, 190), c["e1"].start)
    step("E", pen.free)
    pen.stroke(B.line(*R("E", 960, 270), *R("E", 960, 960), sag=0, seed=170), pen.free, 0.3, B.MUTED, width=4, alpha=0.5)
    pen.write("Pseudomonas aeruginosa", *R("E", 480, 300), LABEL, B.NAVY, w("e2", "Pseudomonas"), align="center")
    for i, (x, y) in enumerate(((180, 470), (290, 440), (260, 530))):
        pen.stroke(rod(*R("E", x, y), 80, 34, 0.5 * i, seed=180 + i), w("e3", "few") + i * 0.05, 0.1, B.BLUE, width=5)
    pen.write("few: holds back", *R("E", 250, 650), NOTE, B.NAVY, pen.free, align="center")
    pen.write("(most weapons)", *R("E", 240, 720), NOTE, B.MUTED, pen.free, align="center", cps=22)
    film = blob(*R("E", 620, 480), 135, seed=7)
    for i in range(9):
        x, y = 550 + (i % 3) * 70, 425 + (i // 3) * 55
        pen.stroke(rod(*R("E", x, y), 66, 28, rr.uniform(-0.7, 0.7), seed=190 + i),
                   w("e4", "enough") if i == 0 else pen.free, 0.04, B.BLUE, width=5)
    for k in range(6):                                     # toxins and enzymes: red spikes outward
        a = (1.3, 2.2, 3.1, 4.0, 4.9, 5.7)[k]
        x0, y0 = R("E", 620 + 125 * math.cos(a), 480 + 100 * math.sin(a))
        pen.stroke(B.line(x0, y0, x0 + 30 * math.cos(a), y0 + 30 * math.sin(a), sag=0, seed=200 + k),
                   w("e4", "toxins") + k * 0.03, 0.06, B.RED, width=7)
    pen.write("many: attack", *R("E", 620, 650), NOTE, B.RED, pen.free, align="center")
    pen.write("virulence factors", *R("E", 620, 720), NOTE, B.RED, w("e4", "Virulence"), align="center")
    pen.stroke(film, w("e5", "biofilm"), 0.5, B.MUTED, width=6, alpha=0.8)
    pen.hatch(film, pen.free, 0.3, B.MUTED, alpha=0.15)
    pen.write("biofilm", *R("E", 860, 490), NOTE, B.MUTED, pen.free, align="center")
    pen.write("scientists think: no early alarm", *R("E", 480, 820), NOTE, B.MUTED, w("e6", "Scientists"),
              align="center", cps=22)
    imm = blob(*R("E", 380, 395), 42, seed=11)            # attack with a few: an immune cell, and the few lose
    pen.stroke(imm, w("e6", "immune"), 0.3, B.NAVY, width=6)
    pen.hatch(B.circle(*R("E", 384, 395), 13, seed=12), pen.free, 0.1, B.NAVY, alpha=0.8, gap=6, width=8)
    xx, xy = R("E", 240, 490)
    pen.stroke(B.line(xx - 60, xy - 60, xx + 60, xy + 60, sag=0, seed=171), w("e6", "wins"), 0.12, B.RED, width=9)
    pen.stroke(B.line(xx + 60, xy - 60, xx - 60, xy + 60, sag=0, seed=172), pen.free, 0.12, B.RED, width=9)
    pen.write("patience = a virulence factor", *R("E", 480, 905), NOTE + 4, B.GOLD_DK, w("e7", "Patience"),
              align="center", cps=20)
    pen.write("Vibrio cholerae", *R("E", 1290, 300), LABEL, B.NAVY, w("e8", "Vibrio"), align="center")
    gut = B.spline(RP("E", [(1030 + i * 70, 520 + (12 if i % 2 else -6)) for i in range(12)]), n=6)
    pen.stroke(gut, c["e9"].start, 0.4, B.RED, width=6, alpha=0.7)
    for i, x in enumerate((1110, 1190, 1270)):
        pen.stroke(comma(*R("E", x, 480), 0.9, -0.3, seed=210 + i), w("e9", "stick") + i * 0.05, 0.1, B.BLUE, width=6)
    pen.write("gut wall", *R("E", 1100, 580), NOTE, B.RED, w("e9", "gut"), align="center", cps=22)
    for k, (x, y) in enumerate(((1120, 420), (1160, 400), (1215, 418), (1260, 398), (1305, 425))):   # toxin: red
        pen.stroke(B.line(*R("E", x - 9, y - 9), *R("E", x + 9, y + 9), sag=0, seed=215 + k), w("e9", "toxin") + k * 0.03,
                   0.04, B.RED, width=8)
    pen.write("few: stick + toxin", *R("E", 1200, 650), NOTE, B.NAVY, pen.free, align="center")
    for i, (x, y) in enumerate(((1590, 470), (1670, 430), (1750, 470), (1620, 380), (1720, 370), (1800, 410))):
        pen.stroke(comma(*R("E", x, y), 0.9, 0.4 * i, seed=220 + i), w("e10", "crowd") + i * 0.04, 0.08, B.BLUE, width=6)
    pen.dots(RP("E", [(1560, 410), (1690, 470), (1760, 330), (1840, 460), (1650, 345), (1700, 520)]), pen.free,
             0.04, 225)                                  # lots of signal around the crowd
    pen.write("toxin OFF", *R("E", 1680, 650), NOTE, B.RED, w("e10", "off"), align="center")
    for k, x in enumerate((1600, 1730)):
        pen.stroke(arrow(*R("E", x + 40, 330), *R("E", x + 80, 280), head=14), w("e10", "let") + k * 0.05, 0.1, B.NAVY,
                   width=5)
    pen.write("lets go (we think)", *R("E", 1660, 720), NOTE, B.MUTED, w("e10", "leave"), align="center")
    pen.write("its way out: the diarrhoea", *R("E", 1420, 820), NOTE, B.NAVY, w("e11", "way"), align="center")
    pen.write("caused by its own toxin", *R("E", 1420, 890), NOTE, B.RED, w("e11", "toxin"), align="center")
    pen.write("same switch, opposite decision", *R("E", 1420, 200), NOTE, B.GOLD_DK, w("e12", "Same"), align="center",
              cps=20)

    # ---- F: jamming, and where the picture breaks
    go("F", c["e12"].end + 0.3)
    pen.title("Jamming the signal", *R("F", 120, 190), c["f1"].start)
    step("F", pen.free)
    ring, tail = ahl(*R("F", 270, 400), 1.6, seed=230)
    pen.stroke(ring[:5], w("f2", "enzymes"), 0.2, SIG, width=8)        # the ring, broken open
    pen.stroke(tail, pen.free, 0.2, SIG, width=8)
    (ax_, ay_), (bx2, by2) = ring[4], ring[0]
    mx, my = (ax_ + bx2) / 2, (ay_ + by2) / 2
    pen.stroke([(mx - 26, my - 22), (mx - 6, my - 4), (mx - 18, my + 4), (mx + 4, my + 24)], w("f2", "ring"), 0.12,
               B.RED, width=7)
    pen.write("quorum quenching", *R("F", 330, 560), LABEL, B.NAVY, w("f2", "quenching"), align="center")
    pen.write("enzymes open the ring", *R("F", 330, 630), NOTE, B.RED, pen.free, align="center", cps=22)
    pen.write("Bacillus enzyme:", *R("F", 330, 730), NOTE, B.NAVY, w("f3", "Bacillus"), align="center")
    pen.write("plant rot much weaker", *R("F", 330, 800), NOTE, B.GREEN, w("f3", "weaker"), align="center")
    pen.stroke(B.spline(RP("F", [(800, 505), (850, 470), (970, 468), (1020, 505)]), n=8), w("f4", "red") - 0.3, 0.2,
               B.MUTED, width=6)                           # a rock, and a branching red seaweed on it
    # a bushy red alga: five fronds fanning from one holdfast, each with alternating side branchlets that
    # shorten towards the tip (Delisea's feathery, alternately branched fronds)
    t0 = w("f4", "seaweed")
    fronds = ((-70, 340, -0.5), (-30, 300, -0.2), (5, 285, 0.05), (40, 305, 0.3), (75, 345, 0.55))
    for k, (dx, top, bend) in enumerate(fronds):
        base = (910, 470)
        tip = (910 + dx * 1.6, top)
        mid = ((base[0] + tip[0]) / 2 + bend * 40, (base[1] + tip[1]) / 2)
        stem = B.spline(RP("F", [base, mid, tip]), n=14)
        tk = t0 + k * 0.12
        b.stroke(stem, tk, 0.25, B.RED, width=7)
        n = len(stem)
        for j, i in enumerate(range(int(n * 0.25), n - 2, 3)):
            (ax_, ay_), (bx2, by2) = stem[i - 1], stem[i + 1]
            a = math.atan2(by2 - ay_, bx2 - ax_)
            side = 1 if j % 2 else -1
            L = 34 * (1 - i / n) + 10
            ang = a + side * 0.75
            px, py = stem[i]
            twig = B.spline([(px, py), (px + L * 0.55 * math.cos(ang), py + L * 0.55 * math.sin(ang)),
                             (px + L * math.cos(ang + side * 0.25), py + L * math.sin(ang + side * 0.25))], n=4)
            b.stroke(twig, tk + 0.25 + j * 0.03, 0.06, B.RED, width=4)
    pen.wait(t0 + len(fronds) * 0.12 + 0.6)
    pen.hatch(B.circle(*R("F", 910, 470), 12, seed=290), pen.free, 0.1, B.RED, alpha=0.8, gap=6, width=8)
    pen.write("Delisea pulchra", *R("F", 910, 560), LABEL, B.NAVY, w("f4", "Delisea"), align="center")
    pen.write("jams the receiver", *R("F", 910, 630), NOTE, B.RED, w("f4", "jam"), align="center")
    pen.write("very clean surface", *R("F", 910, 700), NOTE, B.GREEN, w("f5", "clean"), align="center")
    pen.write("drugs that jam the signal:", *R("F", 620, 870), NOTE, B.NAVY, w("f6", "Drugs"), align="center")
    pen.write("studied, not a standard treatment yet", *R("F", 620, 940), NOTE, B.MUTED, w("f6", "studied"),
              align="center", cps=24)
    pen.stroke(B.line(*R("F", 1150, 270), *R("F", 1150, 960), sag=0, seed=240), w("f7", "last"), 0.3, B.MUTED,
               width=4, alpha=0.5)
    pen.write("not a headcount", *R("F", 1500, 320), LABEL, B.NAVY, w("f7", "count"), align="center")
    pen.write("they sense concentration", *R("F", 1500, 390), NOTE, SIG, w("f8", "concentrated"), align="center")
    small = box(*R("F", 1250, 450), *R("F", 1390, 560), r=20, seed=241)
    pen.stroke(small, w("f9", "tight"), 0.25, B.NAVY, width=5)
    pen.hatch(small, pen.free, 0.25, B.GOLD, alpha=0.45)
    for i, (x, y) in enumerate(((1290, 485), (1350, 500), (1300, 530))):
        pen.stroke(rod(*R("F", x, y), 50, 22, 0.6 * i, seed=245 + i), pen.free, 0.05, B.BLUE, width=4)
    pen.write("tight: ON", *R("F", 1320, 620), NOTE, B.GREEN, pen.free, align="center")
    for i in range(8):
        x, y = 1560 + (i % 4) * 75, 480 + (i // 4) * 80
        pen.stroke(rod(*R("F", x, y), 50, 22, rr.uniform(-0.6, 0.6), seed=250 + i), w("f9", "crowd") + i * 0.03, 0.05,
                   B.BLUE, width=4)
    for k in range(2):
        pen.stroke(arrow(*R("F", 1540, 445 + k * 80), *R("F", 1830, 445 + k * 80), head=14, sag=-6, seed=260 + k),
                   w("f9", "flowing") + k * 0.05, 0.2, B.BLUE, width=3)
    pen.write("open, flowing:", *R("F", 1680, 620), NOTE, B.RED, w("f9", "never"), align="center")
    pen.write("may stay OFF", *R("F", 1680, 682), NOTE, B.RED, pen.free, align="center")
    drop = B.circle(*R("F", 1290, 800), 62, seed=270)
    pen.stroke(B.circle(*R("F", 1290, 800), 14, seed=271), w("f10", "single"), 0.1, B.BLUE, width=6)
    pen.write("one S. aureus cell:", *R("F", 1610, 770), NOTE, B.NAVY, w("f10", "Staphylococcus"),
              align="center", cps=22)
    pen.stroke(drop, w("f10", "droplet"), 0.25, B.BLUE, width=5)
    pen.hatch(drop, w("f10", "switched"), 0.3, B.GOLD, alpha=0.45)
    pen.write("genes ON", *R("F", 1610, 830), NOTE, B.GREEN, w("f10", "genes"), align="center")
    pen.write("a very small room", *R("F", 1610, 890), NOTE, SIG, w("f11", "room"), align="center")
    pen.write("immune cells too? (maybe)", *R("F", 1500, 952), NOTE, B.MUTED, w("f12", "swallowed"),
              align="center", cps=24)

    # ---- wrap: the whole board, each region lights up in turn
    b.cam.frame(c["w1"].start - 0.6, 1.8, 0, 0, 5760, 2160, margin=220)
    pen.wait(c["w1"].start + 1.0)
    for reg, word in (("B", "quorum"), ("C", "small"), ("D", "molecule"), ("A", "dark"), ("E", "crowd"),
                      ("F", "time")):
        x0, y0 = REGION[reg]
        bx_ = [(x0 + 40, y0 + 40), (x0 + 1880, y0 + 40), (x0 + 1880, y0 + 1040), (x0 + 40, y0 + 1040), (x0 + 40, y0 + 40)]
        pen.stroke(B.wobble(bx_, 7, 3.0), w("w1", word), 0.4, B.GOLD, width=22, alpha=0.8)

    # ---- outro: the board fades to a background and the series logo plays over it, with its jingle
    t = b.veil(max(c["w1"].end + 0.6, pen.free + 0.3), 1.2).t1
    t = b.logo(2880, 960, t - 0.7, size=600, sub="@teenytinyology")
    dur = t + 2.5
    return b, voice, c, dur


def thumbnail(path):
    """1280x720 YouTube thumbnail: the lesson's question in big marker letters, a packed crowd of cells in a cloud of
    signal, the logo. (Not "count": the lesson's point is that they sense concentration, not heads.)"""
    b = B.Board()
    b.write("How bacteria", 110, 250, 150, B.NAVY, 0.0, dur=0.1)
    b.write("SENSE", 110, 450, 210, B.GOLD_DK, 0.0, dur=0.1)
    b.write("a crowd", 110, 610, 140, B.NAVY, 0.0, dur=0.1)
    b.stroke(B.line(100, 520, 700, 512, sag=6), 0.0, 0.1, B.GOLD, width=22)
    glow = B.circle(1500, 470, 330, seed=3)
    b.hatch(glow, 0.0, 0.1, B.GOLD, alpha=0.35)
    rr = np.random.default_rng(5)
    for i in range(12):                                   # separate, touching cells: 4 x 3, alternate rows offset
        x, y = 1290 + (i % 4) * 135 + (55 if (i // 4) % 2 else 0), 330 + (i // 4) * 140
        b.stroke(rod(x, y, 120, 54, rr.uniform(-0.35, 0.35), seed=10 + i), 0.0, 0.1, B.BLUE, width=10)
    for i in range(16):
        a, k = rr.uniform(0, TAU), rr.uniform(0.15, 0.95)
        b.stroke(B.circle(1500 + 300 * k * math.cos(a), 470 + 290 * k * math.sin(a), 8, seed=40 + i), 0.0, 0.1, SIG,
                 width=18)
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
    late = [(round(l, 1), round(t, 1)) for l, t, _ in LPen.lags if l > 1.5]
    print("items > 1.5 s after their cue:", late or "none")
    if a.cmd == "stills":
        for f in os.listdir(OUT):
            if f.startswith("still_"):
                os.remove(os.path.join(OUT, f))
        times = [c["a4"].end, b.cam.moves[0][0] - 0.05] + [m[0] - 0.05 for m in b.cam.moves[1:]] + [c["w1"].end, dur - 0.2]
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
        paths = []
        for t in times:
            fn(cairo.Context(s), t)
            p = os.path.join(OUT, f"still_{t:06.2f}.png")
            s.write_to_png(p)
            paths.append(p)
        print(render.contact_sheet(paths, os.path.join(OUT, "sheet.png"), cols=3, width=2700))
        return
    wav = B.mixdown(b, voice, dur, os.path.join(OUT, "l002_audio.wav"))
    p = os.path.join(OUT, "l002-quorum-sensing.mp4")
    render.encode(fn, dur, p, size=(1920, 1080), audio_wav=wav)
    print(p, f"{mix.measure_lufs(p):.1f} LUFS")
    print(thumbnail(os.path.join(OUT, "thumbnail.png")))


if __name__ == "__main__":
    main()
