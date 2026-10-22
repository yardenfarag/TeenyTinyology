"""PEANUT — the ant. Glossy black-brown with warm highlights, big curious eyes; busy and brave.

draw(c, st, x, y, s, ...) — side view facing right, (x, y) = feet line centre.
pose: ang, phase (walk cycle), walking, head_dip (radians), carry (None | 'seed' | 'crumb'),
      gcol (0 black .. 1 berry-red gaster), blink, happy, wiggle (antenna phase), look (eye offset)
Real style: correct worker-ant anatomy (elbowed antennae, three body parts, petiole node), no face.
"""
import math

from engine.core import TAU, Palette, ellipse, hexc, lerp, mix, rot_pt

NAME = "Peanut"
SPECIES = "ant"
SHELL = Palette("#2a1d16", "#7a5a48", "#0a0604", "#000000")
AMBER = Palette("#d98a1f", "#ffd889", "#7a3c04")
RED = Palette("#d3122c", "#ff9e9e", "#5a000f")
LEG = Palette("#1a110c", "#5a4436", "#050302")

GASTER = (-95, -58, 68, 48, -0.12)
PETIOLE = (-30, -54, 11, 13, 0.0)
THORAX = (18, -62, 44, 21, -0.22)
HEAD = (86, -80, 31, 27, 0.15)
NECK = (62, -70)
MANDIBLE = (128, -62)
LEGS = [((40, -54), 98, 30, 0), ((20, -50), 30, 34, 1), ((0, -52), -58, 36, 0)]


def gaster_pal(g):
    if g <= 0.5:
        a, b, t = SHELL, AMBER, g * 2
    else:
        a, b, t = AMBER, RED, (g - 0.5) * 2
    return Palette(mix(a.base, b.base, t), mix(a.light, b.light, t), mix(a.dark, b.dark, t))


def to_world(x, y, s, ang, lx, ly):
    px, py = rot_pt(lx * s, ly * s, ang)
    return x + px, y + py


def mandible_local(dip):
    mx, my = rot_pt(MANDIBLE[0] - NECK[0], MANDIBLE[1] - NECK[1], dip)
    return NECK[0] + mx, NECK[1] + my


def _legs(c, st, phase, far, walking):
    pal = Palette("#4a3a30", "#7a6050", "#2a1d16") if far else LEG
    for hip, fb, ku, grp in LEGS:
        g = grp if not far else 1 - grp
        ph = phase + g * math.pi
        fx, fy = (fb + 15 * math.sin(ph), -11 * max(0.0, math.cos(ph))) if walking else (fb, 0.0)
        if far:
            hip = (hip[0] + 6, hip[1] - 4)
            fx += 12
            fy -= 3
        hx, hy = hip
        kx, ky = hx + (fx - hx) * 0.45, min(hy, fy) - ku
        st.limb(c, [(hx, hy), (kx, ky), (fx, fy), (fx + (14 if fx >= hx else -14), fy + 1)], 7 if not far else 6, pal)


def draw(c, st, x, y, s, ang=0.0, phase=0.0, walking=True, head_dip=0.0, carry=None, gcol=0.0,
         blink=False, happy=0.0, wiggle=0.0, look=(0.0, 0.0), alpha=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.push_group()
    real = st.realistic
    st.shadow(c, -10, 4, 170, 14, 0.2)
    _legs(c, st, phase, True, walking)
    wig = math.sin(wiggle) * 6
    gx, gy, grx, gry, grot = GASTER
    st.ellipse(c, gx, gy, grx, gry, grot, gaster_pal(gcol), seed=101)
    if real:
        c.save()
        c.translate(gx, gy)
        c.rotate(grot)
        c.scale(grx, gry)
        for u in (-0.35, 0.05, 0.42):
            v = math.sqrt(1 - u * u)
            c.move_to(u, -v)
            c.curve_to(u - 0.2, -0.45, u - 0.2, 0.45, u, v)
        c.restore()
        c.set_source_rgba(0, 0, 0, 0.35)
        c.set_line_width(1.6)
        c.stroke()
        for k in range(10):  # fine hairs
            hx = gx - 60 + k * 12
            st.line(c, [(hx, gy - gry + 4), (hx - 5, gy - gry - 4)], 1.2, hexc("#c8a888"), 0.6)
    st.shine(c, gx - 18, gy - 26, 24, 9, -0.35, 0.3 + 0.3 * gcol)
    st.ellipse(c, *PETIOLE, SHELL, seed=102)
    if real:
        st.ellipse(c, PETIOLE[0], PETIOLE[1] - 12, 7, 9, 0.0, SHELL, seed=103)  # petiole node
    st.ellipse(c, *THORAX, SHELL, seed=104)
    _legs(c, st, phase, False, walking)
    c.save()
    c.translate(*NECK)
    c.rotate(head_dip)
    c.translate(-NECK[0], -NECK[1])
    if real:
        st.line(c, [(94, -100), (100, -150), (146, -140 + wig)], 3.0, hexc("#3b3b3b"))
    else:
        st.line(c, [(94, -100), (100, -150), (140, -150 + wig)], 3.4, hexc("#3b2a20"))
        c.arc(142, -150 + wig, 5, 0, TAU)
        c.set_source_rgba(*SHELL.base)
        c.fill()
    hs = 1.0 if real else 1.18
    st.ellipse(c, HEAD[0] + (0 if real else 4), HEAD[1] - (0 if real else 4), HEAD[2] * hs, HEAD[3] * hs, HEAD[4], SHELL, seed=105)
    st.shine(c, HEAD[0] - 6, HEAD[1] - 16, 12, 5, -0.1, 0.25)
    st.eye(c, 98, -88, 7.5 if not real else 9, 0.1 if blink else 1.0, look)
    st.blush(c, 104, -66, 6, 0.55)
    if not real:
        st.smile(c, 116, -70, 9, hexc("#f2d0c0"), 1 + happy)
    c.move_to(110, -70)
    c.curve_to(120, -72, 128, -66, 130, -58)
    c.curve_to(122, -60, 116, -60, 109, -62)
    c.close_path()
    c.set_source_rgba(*hexc("#1c1c1c"))
    c.fill()
    if real:
        st.line(c, [(100, -98), (112, -152), (162, -128 - wig)], 3.6, hexc("#111111"))
    else:
        st.line(c, [(100, -98), (114, -150), (158, -140 - wig)], 4.0, hexc("#1a110c"))
        c.arc(160, -140 - wig, 6, 0, TAU)
        c.set_source_rgba(*SHELL.base)
        c.fill()
    if carry:
        col = hexc("#6b4423") if carry == "seed" else hexc("#e8c48a")
        c.arc(MANDIBLE[0] + 4, MANDIBLE[1] + 4, 12, 0, TAU)
        c.set_source_rgba(*col)
        c.fill()
        st.shine(c, MANDIBLE[0], MANDIBLE[1], 4, 3, 0, 0.5)
    c.restore()
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()
