"""Render the cast (or one character) in every art style for review.

Usage: python -m characters.model_sheet [out.png] [--only mochi,pip,...] [--t 1.0]
"""
import argparse
import math
import os

import cairo

from engine.core import hexc, set_font, text_center
from engine import style as styles
from characters import doodle, mango, mochi, noodle, peanut, pickle, pip, pixie, plum, roly

CELL_W, CELL_H = 560, 560


def _bg(c, st):
    g = cairo.LinearGradient(0, 0, 0, CELL_H)
    g.add_color_stop_rgba(0, *hexc("#fbf3e4"))
    g.add_color_stop_rgba(1, *hexc("#ecdcc0"))
    c.set_source(g)
    c.paint()


def cell_mochi(c, st, t):
    mochi.draw(c, st, 290, 430, 0.68, eyes=1.0, happy=1.0, breathe=math.sin(t * 2), tail=t)


def cell_mochi_sleep(c, st, t):
    mochi.draw(c, st, 290, 430, 0.68, eyes=0.0, breathe=math.sin(t * 2), tail=t)


def cell_pip(c, st, t):
    pip.draw(c, st, 280, 400, 1.15, phase=t * 3, happy=0.5)


def cell_pip_larva(c, st, t):
    pip.draw_larva(c, st, 470, 300, 1.05, t * 2)


def cell_peanut(c, st, t):
    peanut.draw(c, st, 270, 380, 1.55, phase=t * 4, wiggle=t * 3, happy=0.6)


def cell_noodle(c, st, t):
    pts = noodle.worm_curve((90, 420), (500, 160), t, amp=60, waves=2.0)
    noodle.draw(c, st, pts, 16, 1.0, size=0.8, happy=0.6)
    noodle.draw_egg_packet(c, st, 470, 430, 30, seed=3)
    noodle.draw_cyst(c, st, 380, 470, 22)


def cell_plum(c, st, t):
    c.set_source_rgba(*hexc("#6a4426"))
    c.set_line_width(14)
    c.move_to(120, 452)
    c.line_to(520, 440)
    c.stroke()
    plum.draw(c, st, 330, 445, 1.25, happy=1.0)


def cell_pickle(c, st, t):
    pickle.draw(c, st, 330, 420, 1.15, phase=t * 3, antenna=t * 2, happy=0.5)


def cell_pickle_xray(c, st, t):
    def inside(cc):
        doodle.draw_along(cc, st, doodle.coil_points(-72, -58, 60, 6, t, squash=0.55), 5, face=False)
    pickle.draw(c, st, 330, 420, 1.15, xray=inside, xray_alpha=1.0, antenna=t * 2)


def cell_pixie(c, st, t):
    pixie.draw(c, st, 360, 440, 1.0, happy=0.5)


def cell_pixie_rest(c, st, t):
    pixie.draw(c, st, 360, 420, 1.0, rest=1.0)
    pixie.draw_nymph(c, st, 330, 520, 1.1, t * 2)


def cell_doodle(c, st, t):
    doodle.draw_along(c, st, doodle.swim_points(470, 250, 380, t), 13, happy=0.5)
    doodle.draw_along(c, st, doodle.coil_points(170, 420, 90, 6, t), 7, face=False)
    doodle.draw_cyst(c, st, 420, 430, 34, t=t)


def cell_roly(c, st, t):
    roly.draw(c, st, 280, 300, 0.80, phase=t * 2, female=True, happy=0.5)
    roly.draw(c, st, 300, 470, 0.80 * roly.MALE_S / roly.FEMALE_S, phase=t * 2 + 1.4, female=False)
    roly.draw_manca(c, st, 462, 486, 0.26, phase=t * 3)


def cell_roly_facing(c, st, t):
    roly.draw_facing(c, st, 290, 300, 0.95, phase=t * 2, grip=0.0, happy=0.4, tilt=0.45)


def cell_roly_stages(c, st, t):
    roly.draw(c, st, 290, 200, 0.70, phase=t * 2, grip=1.0)
    roly.draw_underside(c, st, 290, 420, 0.70, eggs=1.0, phase=t * 2)


def cell_mango(c, st, t):
    mango.draw(c, st, 300, 300, 0.50, phase=t * 2, happy=0.6)
    mango.draw(c, st, 300, 460, 0.50, phase=t * 2 + 1.0, mouth=1.0)


def cell_mango_front(c, st, t):
    def inside(cc):
        roly.draw_facing(cc, st, 0, 40, 0.60, phase=t * 2, grip=1.0, happy=0.3, tilt=0.70)
    mango.draw_front(c, st, 280, 290, 0.80, mouth=1.0, inside=inside, teeth=1.0, phase=t * 2)


def cell_mango_front_shut(c, st, t):
    mango.draw_front(c, st, 280, 290, 0.80, mouth=0.12, teeth=0.0, phase=t * 2)


def cell_mango_gills(c, st, t):
    mango.draw_gill_chamber(c, st, 280, 300, 0.70, phase=t * 2)
    roly.draw(c, st, 250, 300, 0.30, ang=-0.4, phase=t * 2, female=False, grip=1.0)


CELLS = {
    "mochi": [("Mochi", cell_mochi), ("Mochi (napping)", cell_mochi_sleep)],
    "pip": [("Pip", cell_pip), ("Pip (larva)", cell_pip_larva)],
    "peanut": [("Peanut", cell_peanut)],
    "noodle": [("Noodle", cell_noodle)],
    "plum": [("Plum", cell_plum)],
    "pickle": [("Pickle", cell_pickle), ("Pickle (x-ray: Doodle coiled)", cell_pickle_xray)],
    "pixie": [("Pixie", cell_pixie), ("Pixie resting + as a nymph", cell_pixie_rest)],
    "doodle": [("Doodle (swimming, coiled, cyst)", cell_doodle)],
    "roly": [("Roly (female, male, manca)", cell_roly),
             ("Roly gripping + her brood pouch", cell_roly_stages),
             ("Roly head-on (looking back out at us)", cell_roly_facing)],
    "mango": [("Mango (swimming, mouth open)", cell_mango),
              ("Mango head-on: Roly in place, tooth patch", cell_mango_front),
              ("Mango head-on, mouth nearly shut", cell_mango_front_shut),
              ("Mango's gill chamber (Roly as a male)", cell_mango_gills)],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default="model_sheet.png")
    ap.add_argument("--only", default="")
    ap.add_argument("--t", type=float, default=1.0)
    a = ap.parse_args()
    keys = [k for k in CELLS if not a.only or k in a.only.split(",")]
    cells = [cell for k in keys for cell in CELLS[k]]
    names = ["cute", "real", "illustrated"]
    head = 70
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, CELL_W * len(names), head + CELL_H * len(cells))
    c = cairo.Context(surf)
    c.set_source_rgba(*hexc("#2b2622"))
    c.paint()
    for j, n in enumerate(names):
        text_center(c, {"cute": "A · Cute", "real": "B · Realistic", "illustrated": "C · Illustrated"}[n],
                    CELL_W * j + CELL_W / 2, 50, 40, (1, 1, 1), bold=True)
    for i, (label, fn) in enumerate(cells):
        for j, n in enumerate(names):
            st = styles.get(n)
            c.save()
            c.translate(CELL_W * j, head + CELL_H * i)
            c.rectangle(0, 0, CELL_W - 4, CELL_H - 4)
            c.clip()
            _bg(c, st)
            fn(c, st, a.t)
            if n == "illustrated":
                c.set_operator(cairo.OPERATOR_MULTIPLY)
                c.set_source_surface(styles._paper(), 0, 0)
                c.paint()
                c.set_operator(cairo.OPERATOR_OVER)
            set_font(c, 30, bold=True)
            text_center(c, label, CELL_W / 2, 44, 30, hexc("#3a2a1a"), bold=True)
            c.restore()
    surf.write_to_png(a.out)
    print("wrote", os.path.abspath(a.out))


if __name__ == "__main__":
    main()
