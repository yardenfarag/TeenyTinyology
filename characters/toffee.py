"""TOFFEE — the crab-hacker barnacle (Sacculina carcini), female.

A barnacle that looks nothing like one. Four looks, one character:
  larva (cypris)   a toffee-coloured speck: a bean-shaped two-valved shell, one dark eye, six pairs of tiny
                   swimming legs that flick out under the shell, two short feelers in front
  kentrogon        the larva's empty shell on the crab, and under it a dome with a hollow needle (stylet) that
                   injects the soft "vermigon" into the crab's blood
  roots (interna)  pale pink-cream rootlets branching through the crab
  sac (externa)    a cream-brown oval, up to 2.5 cm wide, hanging from a stalk under the crab's tail flap; the
                   mantle opening sits at the far end from the stalk. Her tiny face is beside the opening.
Patient, quiet, makes herself at home.

draw_larva(c, st, x, y, s, phase, ang, blink, happy, alpha)
draw_kentrogon(c, st, x, y, s, inject=0..1, phase)        (x, y) = where the needle enters, needle points +y
draw_roots(c, st, x, y, s, grow=0..1, seed, ang, alpha)    branching from (x, y)
draw_sac(c, st, x, y, s, eggs=0..1, phase, ang, blink, happy, males=0..1, hatch=0..1, alpha)
                                                            (x, y) = sac centre; stalk goes up (-y)
draw_nauplius(c, st, x, y, s, phase, ang, alpha)           a hatched larva (the cloud)
draw_male(c, st, x, y, s, phase, ang)                      a male cypris: a smaller, darker larva
SAC_RX / SAC_RY                                             local half-sizes of the sac
"""
import math

import cairo

from engine.core import TAU, Palette, ellipse, hexc, lerp, rng, rot_pt, smooth_path

NAME = "Toffee"
SPECIES = "crab-hacker barnacle"

SAC = Palette("#dcc39a", "#f3e6cc", "#a8845a", "#6b5236")
LARVA = Palette("#ecd39c", "#f9edcf", "#b2924e", "#6d5a34")
MALE = Palette("#c9a66e", "#e8d2a6", "#8c6c3c", "#5a4424")
ROOT = Palette("#e9bcae", "#f9e0d6", "#b8826f", "#86564a")
EGG = Palette("#c89a5c", "#e6c48e", "#8f6a36", "#5e4320")
EYE = hexc("#2a211a")

SAC_RX, SAC_RY = 60.0, 44.0


# ================================================================ larva (cypris)
def _bean(cc, L=30.0, H=13.0):
    smooth_path(cc, [(L, 0), (L * 0.8, -H * 0.8), (0, -H), (-L * 0.8, -H * 0.85), (-L, -H * 0.2),
                     (-L * 0.85, H * 0.6), (0, H), (L * 0.8, H * 0.7)], closed=True)


def draw_larva(c, st, x, y, s, phase=0.0, ang=0.0, blink=False, happy=0.0, alpha=1.0, pal=LARVA,
               eye_r=4.2):
    """The cypris: a speck with a two-valved shell, drawn side-on facing right."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.push_group()
    real = st.realistic
    # swimming legs: six pairs, flicking out below the shell edge
    for i in range(6):
        px = lerp(14, -18, i / 5.0)
        k = math.sin(phase * 7 + i * 0.8)
        pts = [(px, 8), (px - 4 + 3 * k, 16), (px - 8 + 6 * k, 22)]
        st.limb(c, pts, 1.8, pal, alpha=0.9)
    # feelers (antennules) in front — they are what she walks and sticks on with
    for sgn in (-1, 1):
        st.limb(c, [(26, 2), (34, 4 + sgn * 3), (38, 2 + sgn * 6)], 1.8, pal)
    st.part(c, _bean, pal, 0, 0, 32, seed=801)
    c.save()
    _bean(c)
    c.clip()
    g = cairo.LinearGradient(0, -13, 0, 13)
    g.add_color_stop_rgba(0.0, *pal.light[:3], 0.45)
    g.add_color_stop_rgba(1.0, *pal.dark[:3], 0.40)
    c.set_source(g)
    c.paint()
    # the hinge line between the two valves, along the back
    c.move_to(-26, -8)
    c.curve_to(-8, -13, 10, -13, 24, -7)
    c.set_source_rgba(*pal.dark[:3], 0.5)
    c.set_line_width(1.6)
    c.stroke()
    c.restore()
    if real:
        c.arc(16, -2, 3.0, 0, TAU)     # the single nauplius eye
        c.set_source_rgba(*EYE)
        c.fill()
    else:
        st.eye(c, 16, -2, eye_r, 0.12 if blink else 1.0)
        st.smile(c, 22, 5, 7, pal.line, 0.6 + happy)
        st.shine(c, -4, -7, 12, 3, 0.1, 0.35)
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()


def draw_male(c, st, x, y, s, phase=0.0, ang=0.0, alpha=1.0):
    """A male cypris: the same body plan, smaller and darker, no name."""
    draw_larva(c, st, x, y, s * 0.72, phase, ang, alpha=alpha, pal=MALE, eye_r=3.6)


# ================================================================ kentrogon: the needle
def draw_kentrogon(c, st, x, y, s, inject=0.0, phase=0.0, ang=0.0, alpha=1.0):
    """(x, y) is the point on the crab's shell where the needle goes in; the needle points down (+y).
    inject 0: the dome sits on the shell with the needle just in; 0..1: the soft parasite (a pale droplet)
    travels down the needle and the dome empties."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.push_group()
    # the shed larval shell, empty and glassy, tipped over beside the dome
    c.save()
    c.translate(-36, -8)
    c.rotate(0.25)
    _bean(c, 26, 11)
    c.set_source_rgba(*LARVA.light[:3], 0.45)
    c.fill_preserve()
    c.set_source_rgba(*LARVA.dark[:3], 0.6)
    c.set_line_width(1.8)
    c.stroke()
    c.restore()
    # the dome (kentrogon), shrinking as it empties
    k = 1.0 - 0.45 * inject
    st.ellipse(c, 0, -10 * k, 16 * k, 11 * k, 0.0, LARVA, seed=811)
    # the hollow needle: a thin tube, pushed through the shell
    st.line(c, [(0, -4), (0, 26)], 3.4, LARVA.dark)
    st.line(c, [(0, -4), (0, 26)], 1.4, LARVA.light, alpha=0.8)
    # the droplet travelling down: the soft body being injected
    if inject > 0:
        dy = lerp(-8, 34, inject)
        ellipse(c, 0, dy, 5.5, 7.5)
        c.set_source_rgba(*ROOT.base[:3], 0.95)
        c.fill_preserve()
        c.set_source_rgba(*ROOT.line[:3], 0.7)
        c.set_line_width(1.2)
        c.stroke()
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()


# ================================================================ roots (interna)
def _branch(c, st, x0, y0, a, L, w, depth, grow, r, budget):
    """Recursive rootlet. grow (0..1) reveals the network from the origin outward; each level needs more."""
    need = depth * 0.16
    if grow <= need or L < 6:
        return
    f = min(1.0, (grow - need) / 0.22)
    pts = [(x0, y0)]
    px, py, aa = x0, y0, a
    n = 4
    for i in range(n):
        aa += (r.random() - 0.5) * 0.5
        px += math.cos(aa) * L / n * f
        py += math.sin(aa) * L / n * f
        pts.append((px, py))
    st.limb(c, pts, w, ROOT, alpha=0.95)
    if depth < 5 and f >= 1.0:
        for sgn in (-1, 1):
            if depth < 2 or r.random() < budget:
                _branch(c, st, px, py, aa + sgn * lerp(0.35, 0.9, r.random()), L * 0.72, w * 0.72,
                        depth + 1, grow, r, budget * 0.92)


def draw_roots(c, st, x, y, s, grow=1.0, seed=0, ang=0.0, alpha=1.0, arms=6, length=90.0, width=7.5):
    """A pale network branching from (x, y). grow 0..1 is how far it has spread."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.push_group()
    r = rng(820 + seed)
    for i in range(arms):
        a = TAU * i / arms + (r.random() - 0.5) * 0.6
        _branch(c, st, 0, 0, a, length, width, 0, grow, r, 0.95)
    # the knot where she first arrived
    ellipse(c, 0, 0, 9 * min(1.0, grow * 4), 7 * min(1.0, grow * 4))
    c.set_source_rgba(*ROOT.base[:3], 1.0)
    c.fill_preserve()
    c.set_source_rgba(*ROOT.line[:3], 0.6)
    c.set_line_width(1.5)
    c.stroke()
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()


# ================================================================ sac (externa)
def _oval(cc, k=1.0):
    smooth_path(cc, [(SAC_RX * k, 0), (SAC_RX * 0.78 * k, -SAC_RY * 0.78), (0, -SAC_RY * 0.9), (-SAC_RX * 0.78 * k, -SAC_RY * 0.78),
                     (-SAC_RX * k, 0), (-SAC_RX * 0.74 * k, SAC_RY * 0.8), (0, SAC_RY), (SAC_RX * 0.74 * k, SAC_RY * 0.8)],
                closed=True)


def draw_sac(c, st, x, y, s, eggs=0.0, phase=0.0, ang=0.0, blink=False, happy=0.0, males=0.0, hatch=0.0,
             alpha=1.0, stalk=True, grow=1.0):
    """The externa. Stalk up (-y) to the crab; mantle opening at the bottom, with her face beside it.
    eggs fills her with a stipple of eggs; hatch pulses the sac and streams larvae out of the opening;
    males puts one or two male larvae at the opening; grow scales her from a new bud (0.3) to full size."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s * grow, s * grow)
    c.push_group()
    real = st.realistic
    pulse = 1.0 + 0.025 * math.sin(phase * 1.4) + 0.06 * hatch * max(0.0, math.sin(phase * 5.0))
    c.scale(pulse, 1.0 / pulse)
    if stalk:
        st.limb(c, [(0, -SAC_RY * 0.8), (2, -SAC_RY - 14)], 14, SAC)
    st.part(c, _oval, SAC, 0, 0, SAC_RX, seed=831)
    c.save()
    _oval(c)
    c.clip()
    g = cairo.RadialGradient(-18, -16, 6, 0, 4, SAC_RX * 1.3)
    g.add_color_stop_rgba(0.0, *SAC.light[:3], 0.55)
    g.add_color_stop_rgba(0.7, *SAC.base[:3], 0.0)
    g.add_color_stop_rgba(1.0, *SAC.dark[:3], 0.45)
    c.set_source(g)
    c.paint()
    if eggs > 0:
        r = rng(833)
        for _ in range(int(220 * eggs)):
            px, py = lerp(-SAC_RX, SAC_RX, r.random()), lerp(-SAC_RY, SAC_RY, r.random())
            if (px / (SAC_RX * 0.92)) ** 2 + (py / (SAC_RY * 0.9)) ** 2 > 1:
                continue
            c.arc(px, py, lerp(2.4, 3.6, r.random()), 0, TAU)
            c.set_source_rgba(*EGG.base[:3], 0.75)
            c.fill()
    # faint ridges: the mantle is a bit wrinkled
    for k in range(3):
        yy = -22 + k * 20
        c.move_to(-50, yy + 6)
        c.curve_to(-20, yy, 20, yy, 50, yy + 6)
        c.set_source_rgba(*SAC.dark[:3], 0.14)
        c.set_line_width(2.0)
        c.stroke()
    c.restore()
    # the mantle opening: a small raised ring at the far end from the stalk
    oy = SAC_RY * 0.78
    gape = 1.0 + 0.6 * hatch
    ellipse(c, 0, oy, 9 * gape, 5.5 * gape)
    c.set_source_rgba(*SAC.dark[:3], 0.85)
    c.fill()
    ellipse(c, 0, oy, 9 * gape, 5.5 * gape)
    c.set_source_rgba(*SAC.light[:3], 0.9)
    c.set_line_width(2.4)
    c.stroke()
    if not real:
        st.shine(c, -22, -20, 18, 7, 0.4, 0.30)
        # her face sits beside the opening, looking out
        for sgn in (-1, 1):
            st.eye(c, sgn * 17, oy - 14, 6.0, 0.12 if blink else 1.0)
        st.blush(c, -26, oy - 6, 6, 0.3)
        st.blush(c, 26, oy - 6, 6, 0.3)
        st.smile(c, 0, oy - 9, 10, SAC.line, 0.6 + happy)
    if males > 0:
        for k, (mx, my, ma) in enumerate(((-14, oy + 12, -0.9), (16, oy + 10, -2.3))):
            if males > k * 0.5:
                draw_male(c, st, mx, my, 0.45, phase=phase + k, ang=ma, alpha=min(1.0, (males - k * 0.5) * 2))
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()


# ================================================================ nauplius (hatched larva)
def draw_nauplius(c, st, x, y, s, phase=0.0, ang=0.0, alpha=1.0):
    """A hatched larva: a pear-shaped speck with one eye and three pairs of swimming limbs. It does not
    feed; it swims on what it was born with and moults into a cypris within days."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.push_group()
    for i in range(3):
        px = lerp(8, -6, i / 2.0)
        k = math.sin(phase * 9 + i)
        for sgn in (-1, 1):
            st.limb(c, [(px, sgn * 4), (px - 6 + 3 * k, sgn * (13 + 2 * k)), (px - 14 + 5 * k, sgn * 17)], 1.6, LARVA)
    smooth_path(c, [(16, 0), (10, -8), (-4, -9), (-16, -4), (-16, 4), (-4, 9), (10, 8)], closed=True)
    c.set_source_rgba(*LARVA.base[:3], 1.0)
    c.fill_preserve()
    c.set_source_rgba(*LARVA.line[:3], 0.7)
    c.set_line_width(1.4)
    c.stroke()
    c.arc(8, 0, 2.6, 0, TAU)
    c.set_source_rgba(*EYE)
    c.fill()
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()
