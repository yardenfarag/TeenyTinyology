"""DILLY — the dog heartworm, *Dirofilaria immitis* (female). A smooth, pearly white thread with a faint pink
blush, a blunt rounded head with a tiny face, and a gently tapered, blunt tail (the male's tail is coiled like a
corkscrew). No segments (that's Noodle). Curious, patient, a long-distance traveller like Doodle.

draw_along(c, st, pts, w, ...)       the worm along a polyline (pts[0] = head); any stage from larva to adult
wiggle_points(x, y, length, t, ...)  sinuous crawl/swim shape heading in direction `ang`
curl_points(cx, cy, r, t, ...)       a loose S-curl, as nestled in an artery
draw_microfilaria(c, st, x, y, s, t) a baby worm drifting in the blood (sharp tapered tail)
In the "real" style there is no face, and the head shows the small mouth papillae.
"""
import math

import cairo

from engine.core import TAU, Palette, hexc, lerp

NAME = "Dilly"
SPECIES = "dog heartworm"
SKIN = Palette("#f1e4e6", "#fffafb", "#d6b9c1", "#a3808c")
MALE = Palette("#ece6dc", "#fffcf6", "#cfc2ae", "#9a8a72")
FACE = hexc("#7a4a58")


def wiggle_points(x, y, length, t, n=160, amp=18, waves=1.6, ang=math.pi, speed=4.0):
    """Head at (x, y); the body trails behind in direction `ang` (default: head right, tail left)."""
    ca, sa = math.cos(ang), math.sin(ang)
    pts = []
    for k in range(n):
        u = k / (n - 1)
        a = u * length
        o = amp * math.sin(waves * TAU * u - t * speed) * (0.25 + 0.75 * u)
        pts.append((x + ca * a - sa * o, y + sa * a + ca * o))
    return pts


def resample(poly, n=120):
    """Evenly spaced points along a polyline (e.g. to lay Dilly along an artery)."""
    seg = [math.dist(a, b) for a, b in zip(poly, poly[1:])]
    total = sum(seg)
    out, i, acc = [], 0, 0.0
    for k in range(n):
        d = total * k / (n - 1)
        while i < len(seg) - 1 and acc + seg[i] < d:
            acc += seg[i]
            i += 1
        f = (d - acc) / seg[i] if seg[i] else 0.0
        out.append((lerp(poly[i][0], poly[i + 1][0], f), lerp(poly[i][1], poly[i + 1][1], f)))
    return out


def curl_points(cx, cy, r, t, n=220, turns=1.4):
    pts = []
    for k in range(n):
        u = k / (n - 1)
        a = u * turns * TAU + 0.3 * math.sin(t * 1.2)
        rr = r * (1.0 - 0.45 * u)
        pts.append((cx + math.cos(a) * rr * 1.5, cy + math.sin(a) * rr * 0.7 + 3 * math.sin(u * 18 + t)))
    return pts


def draw_along(c, st, pts, w=10.0, alpha=1.0, face=True, blink=False, happy=0.0, male=False, t=0.0):
    if len(pts) < 2:
        return
    pal = MALE if male else SKIN
    n = len(pts)
    c.save()
    c.push_group()
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    tail_end = n - 1
    for layer, (col, k, dy, a) in enumerate(((pal.line, 1.22, 0, 0.9), (pal.base, 1.0, 0, 1.0),
                                              (pal.light, 0.38, -0.22, 0.8))):
        for i in range(tail_end):
            u = i / (n - 1)
            taper = min(1.0, 0.75 + u * 6, (1 - u) * 5 + 0.3)
            c.move_to(pts[i][0], pts[i][1] + dy * w)
            c.line_to(pts[i + 1][0], pts[i + 1][1] + dy * w)
            c.set_source_rgba(col[0], col[1], col[2], a)
            c.set_line_width(max(1.0, w * k * taper))
            c.stroke()
    # faint gut line (pinkish) — a hint of the inside, as the real worm is translucent
    gut = [(p[0], p[1] + w * 0.12) for p in pts[4:-4]]
    if len(gut) >= 2:
        st.line(c, gut, max(1.0, w * 0.16), hexc("#d89aa6"), 0.45)
    if st.name == "illustrated":
        st.line(c, pts, max(1.4, w * 0.16), st.ink, 0.5)   # every point: a stride cut chords across bends
    if male:  # corkscrew tail, seen from the side like a little spring
        tx, ty = pts[-1]
        px, py = pts[-5]
        ang = math.atan2(ty - py, tx - px)
        ux, uy = math.cos(ang), math.sin(ang)
        spring = []
        for k in range(120):            # three loops seen from the side: a trochoid, so the coils really loop
            u = k / 119
            th = u * 3 * TAU
            r = w * 1.6 * (1 - 0.25 * u)
            d = w * 0.4 + u * w * 5.0 + r * 0.6 * (1 - math.cos(th))
            off = r * math.sin(th)
            spring.append((tx + ux * d - uy * off, ty + uy * d + ux * off))
        st.line(c, [pts[-1]] + spring, w * 0.40, pal.line)
        st.line(c, [pts[-1]] + spring, w * 0.27, pal.base)
    hx, hy = pts[0]
    nx, ny = pts[min(5, n - 1)]
    hang = math.atan2(hy - ny, hx - nx)
    if st.realistic and w >= 6:  # mouth papillae on the blunt head
        for d in (-0.6, 0.0, 0.6):
            px, py = hx + math.cos(hang + d) * w * 0.48, hy + math.sin(hang + d) * w * 0.48
            c.arc(px, py, max(0.8, w * 0.07), 0, TAU)
            c.set_source_rgba(*pal.line[:3], 0.7)
            c.fill()
    if face and st.faces and w >= 6:
        ox, oy = math.cos(hang), math.sin(hang)
        # eye sits just behind the head tip, on the upper side of the body
        up = -1 if ox >= 0 else 1
        ex = hx - ox * w * 0.7 + oy * w * 0.25 * up
        ey = hy - oy * w * 0.7 - abs(ox) * w * 0.25
        st.eye(c, ex, ey, w * 0.36, 0.1 if blink else 1.0)
        st.blush(c, ex - ox * w * 0.2, ey + w * 0.5, w * 0.24, 0.5)
        st.smile(c, ex + ox * w * 0.5, ey + w * 0.5, w * 0.46, FACE, 1 + happy)
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()


def draw_microfilaria(c, st, x, y, s, t=0.0, ang=0.0, face=False, alpha=1.0):
    """A baby worm (L1): a slender wriggle with a rounded head and a sharply pointed tail."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    pts = [(-k * 2.2, 4 * math.sin(k * 0.22 - t * 6) * (k / 40)) for k in range(41)]
    c.push_group()
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for col, k in ((SKIN.line, 1.3), (SKIN.base, 1.0)):
        for i in range(len(pts) - 1):
            u = i / (len(pts) - 1)
            c.move_to(*pts[i])
            c.line_to(*pts[i + 1])
            c.set_source_rgba(*col)
            c.set_line_width(max(0.6, 4.4 * k * (1.0 if u < 0.6 else (1 - u) / 0.4)))
            c.stroke()
    if face and st.faces:
        st.eye(c, -2.5, -1.2, 1.3, 1.0)
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()
