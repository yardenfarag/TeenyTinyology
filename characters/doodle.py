"""DOODLE — the horsehair worm (male). A long, smooth, glossy dark-brown string with a pale whitish head tip
and a forked tail. Quiet, determined, a long-distance traveller.

draw_along(c, st, pts, w, ...)   the adult worm along a polyline (pts[0] = head)
coil_points(cx, cy, r, turns, t) tightly coiled ball (as inside the cricket)
swim_points(x, y, length, t)     sinuous swimming shape heading right
draw_larva(c, st, x, y, s)       tiny larva (spiny head proboscis)
draw_cyst(c, st, x, y, r, ...)   dormant cyst with the coiled larva inside
"""
import math

import cairo

from engine.core import TAU, Palette, ellipse, hexc, lerp, rng

NAME = "Doodle"
SPECIES = "horsehair worm"   # in e001: Paragordius varius (a cricket hairworm)
SKIN = Palette("#5a3a22", "#a8805a", "#2a180c", "#1a0c04")
TIP = hexc("#efe4cc")


def coil_points(cx, cy, r, turns=5.0, t=0.0, n=600, squash=0.55):
    """A wound-up ball: an elliptical spiral that wobbles slightly."""
    pts = []
    for k in range(n):
        u = k / (n - 1)
        a = u * turns * TAU + t * 0.6
        rr = r * (0.25 + 0.75 * (0.5 + 0.5 * math.sin(u * 7.3 + 1.1)))
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * squash + 4 * math.sin(u * 40 + t)))
    return pts


def swim_points(x, y, length, t, n=220, amp=34, waves=2.2):
    pts = []
    for k in range(n):
        u = k / (n - 1)
        px = x - u * length
        py = y + amp * math.sin(waves * TAU * u - t * 5) * (0.3 + 0.7 * u)
        pts.append((px, py))
    return pts


def draw_along(c, st, pts, w=12.0, alpha=1.0, face=True, blink=False, happy=0.0):
    if len(pts) < 2:
        return
    c.save()
    c.push_group()
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    # body: dark outline, base, top highlight (tapers at both ends)
    n = len(pts)
    for layer, (col, k, dy) in enumerate(((SKIN.line, 1.25, 0), (SKIN.base, 1.0, 0), (SKIN.light, 0.32, -0.25))):
        for i in range(n - 1):
            u = i / (n - 1)
            taper = min(1.0, u * 12, (1 - u) * 6 + 0.35)
            c.move_to(pts[i][0], pts[i][1] + dy * w)
            c.line_to(pts[i + 1][0], pts[i + 1][1] + dy * w)
            c.set_source_rgba(col[0], col[1], col[2], 0.55 if layer == 2 else 1.0)
            c.set_line_width(max(1.0, w * k * taper))
            c.stroke()
    if st.name == "illustrated":
        st.line(c, pts[::6], max(1.6, w * 0.18), st.ink, 0.6)
    hx, hy = pts[0]
    c.arc(hx, hy, w * 0.55, 0, TAU)
    c.set_source_rgba(*TIP)
    c.fill()
    # forked tail (male)
    tx, ty = pts[-1]
    px, py = pts[-4]
    ang = math.atan2(ty - py, tx - px)
    for d in (-0.5, 0.5):
        st.line(c, [(tx, ty), (tx + math.cos(ang + d) * w * 1.6, ty + math.sin(ang + d) * w * 1.6)], w * 0.5, SKIN.base)
    if face and st.faces and w >= 7:
        nx, ny = pts[min(6, n - 1)]
        ang = math.atan2(hy - ny, hx - nx)
        ox, oy = math.cos(ang) * w * 1.2, math.sin(ang) * w * 1.2
        ex, ey = hx - ox * 0.9, hy - oy * 0.9 - w * 0.25
        st.eye(c, ex, ey, w * 0.28, 0.1 if blink else 1.0)
        st.smile(c, ex + w * 0.3, ey + w * 0.55, w * 0.5, TIP, 1 + happy)
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()


def draw_larva(c, st, x, y, s, phase=0.0, alpha=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    pts = [(-i * 3, 2 * math.sin(phase - i * 0.4)) for i in range(14)]
    draw_along(c, st, pts, 4, alpha, face=False)
    for k in range(3):  # spiny proboscis
        a = -0.6 + k * 0.6
        st.line(c, [(2, 0), (2 + math.cos(a) * 6, math.sin(a) * 6)], 1.2, SKIN.dark, alpha)
    c.restore()


def draw_cyst(c, st, x, y, r, alpha=1.0, glow=1.0, t=0.0, blink=False):
    if alpha <= 0:
        return
    g = cairo.RadialGradient(x, y, 0, x, y, r * 2.4)
    g.add_color_stop_rgba(0, 1, 0.96, 0.7, 0.7 * alpha * glow)
    g.add_color_stop_rgba(1, 1, 0.96, 0.7, 0)
    c.arc(x, y, r * 2.4, 0, TAU)
    c.set_source(g)
    c.fill()
    st.ellipse(c, x, y, r, r * 0.85, 0.0, Palette("#f7efd9", "#ffffff", "#cdbb95"), seed=401, alpha=alpha * 0.9)
    pts = coil_points(x, y, r * 0.62, 2.2, t, n=160, squash=0.8)
    draw_along(c, st, pts, max(2.0, r * 0.14), alpha, face=False)
    if st.faces and r >= 14:
        hx, hy = pts[0]
        st.eye(c, hx, hy - r * 0.05, r * 0.08, 0.1 if blink else 1.0)
