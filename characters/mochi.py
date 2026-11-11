"""MOCHI — the cat. Cream fur, caramel patches, sea-green eyes, pink nose. Sleepy, gentle, a bit vain.

draw(c, st, x, y, s, **pose) — lying "sphinx" pose facing right, (x, y) = ground under the middle of the belly.
pose: eyes (0 closed..1 open), turn (0 looking forward .. 0.5 looking at the camera .. 1 looking back over her
      shoulder), lick (0..1 head dips to the fur), tongue (0..1), tail (phase), ear (twitch -1..1),
      breathe (-1..1), happy (0..1 smile)

Built as a rig (v2, e005 — owner: "she looks like a pile of lumps"): torso, haunch, neck and head anchors; the torso,
haunch and neck are drawn as ONE silhouette (`Style.silhouette`), so the neck bends without seams. The head turns
by yaw (its outline and face morph from 3/4 right through front to 3/4 left) instead of being squashed flat.
"""
import math

import cairo

from engine.core import TAU, Palette, ease, ellipse, hexc, lerp, shade

NAME = "Mochi"
SPECIES = "cat"
FUR = Palette("#f4e6d2", "#fffaf2", "#cfb397", "#8a6a50")
FUR_FAR = Palette("#e2d0b8", "#f4e8d8", "#bba084", "#7a5c44")   # far-side legs, in shadow
PATCH = Palette("#d99a5b", "#f2c08a", "#a8682f")
PINK = hexc("#f2a2a6")
NOSE = hexc("#e9818a")
IRIS = hexc("#5fbfa3")
CREAM = hexc("#fffaf2")
MOUTH = hexc("#6a4030")

NECK_ROOT = (150, -150)
BACK_SPOT = (-30, -168)   # a point on Mochi's back (local) — where her mouth lands at turn=1, lick=1
BELLY = (-20, -90)


# ------------------------------------------------------------------ geometry helpers
def capsule(c, p0, r0, p1, r1):
    """Closed tapered capsule: two circles joined by their outer tangents."""
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    d = math.hypot(dx, dy)
    c.new_sub_path()
    if d <= abs(r0 - r1) + 1e-6:
        r = max(r0, r1)
        c.arc(x0 if r0 >= r1 else x1, y0 if r0 >= r1 else y1, r, 0, TAU)
        c.close_path()
        return
    phi = math.atan2(dy, dx)
    beta = math.acos(max(-1.0, min(1.0, (r0 - r1) / d)))
    c.arc(x0, y0, r0, phi + beta, phi - beta + TAU)
    c.arc(x1, y1, r1, phi - beta, phi + beta)
    c.close_path()


def _bez(c, segs, mirror=False):
    """segs = [P0, (c1, c2, p), ...] — a closed bezier outline."""
    m = -1 if mirror else 1
    x, y = segs[0]
    c.move_to(m * x, y)
    for c1, c2, p in segs[1:]:
        c.curve_to(m * c1[0], c1[1], m * c2[0], c2[1], m * p[0], p[1])
    c.close_path()


def _lerp_segs(a, b, k):
    def lp(p, q):
        return (lerp(p[0], q[0], k), lerp(p[1], q[1], k))
    out = [lp(a[0], b[0])]
    for sa, sb in zip(a[1:], b[1:]):
        out.append(tuple(lp(p, q) for p, q in zip(sa, sb)))
    return out


# ------------------------------------------------------------------ head (local units, centre 0,0)
# 3/4 view facing right (yaw 1) and front view (yaw 0); same structure so they morph. yaw < 0 mirrors.
HEAD_R = [(0, -66),
          ((30, -68), (55, -60), (66, -40)),
          ((74, -22), (79, -4), (82, 10)),     # far cheek, down to the muzzle
          ((88, 24), (80, 40), (60, 46)),      # muzzle + chin
          ((40, 56), (10, 58), (-10, 54)),
          ((-40, 52), (-66, 42), (-80, 32)),   # near cheek
          ((-90, 28), (-90, 20), (-85, 14)),   # cheek fluff
          ((-90, -8), (-78, -40), (-56, -56)),
          ((-38, -66), (-18, -68), (0, -66))]
HEAD_F = [(0, -64),
          ((28, -66), (52, -58), (64, -42)),
          ((76, -24), (84, -2), (86, 14)),
          ((90, 26), (84, 36), (68, 42)),
          ((48, 54), (22, 58), (0, 58)),
          ((-22, 58), (-48, 54), (-68, 42)),
          ((-84, 36), (-90, 26), (-86, 14)),
          ((-84, -2), (-76, -24), (-64, -42)),
          ((-52, -58), (-28, -66), (0, -64))]
# features: (x, y, r) at yaw 1 and yaw 0
EYE_A = ((8, -12, 16.0), (-31, -10, 15.0))    # the near eye at yaw 1 (left eye in the front view)
EYE_B = ((57, -14, 12.5), (31, -10, 15.0))
NOSE_P = ((54, 12), (0, 14))
EAR_A = (((-66, -38), (-20, -62), (-62, -112)), ((-68, -36), (-24, -60), (-66, -110)))   # base1, base2, tip
EAR_B = (((14, -66), (58, -46), (48, -110)), ((24, -60), (68, -36), (66, -110)))
CAP = ((-24, -48, 58, 30, -0.3), (0, -50, 52, 28, 0.0))
BLUSH_A = ((-36, 22, 14), (-52, 24, 13))
BLUSH_B = ((80, 20, 8), (52, 24, 13))


def _f(pair, yaw):
    """Feature value at |yaw| (lerp front -> 3/4)."""
    a, b = pair
    k = abs(yaw)
    return tuple(lerp(q, p, k) for p, q in zip(a, b))


def head_path_fn(yaw):
    segs = _lerp_segs(HEAD_F, HEAD_R, abs(yaw))
    return lambda cc: _bez(cc, segs, mirror=yaw < 0)


def draw_head(c, st, x, y, s, yaw=1.0, eyes=1.0, tongue=0.0, ear=0.0, happy=0.0):
    """Head centred at (x, y). yaw 1 = 3/4 facing right, 0 = facing the camera, -1 = 3/4 facing left."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.push_group()
    real = st.realistic
    m = -1 if yaw < 0 else 1

    def X(v):
        return m * v

    # ears (behind the head)
    for i, (pair, twitch) in enumerate(((EAR_A, 0.0), (EAR_B, ear))):
        b1x, b1y, b2x, b2y, tx, ty = _f(((*pair[0][0], *pair[0][1], *pair[0][2]),
                                         (*pair[1][0], *pair[1][1], *pair[1][2])), yaw)
        b1x, b2x, tx = X(b1x), X(b2x), X(tx)
        mx, my = (b1x + b2x) / 2, (b1y + b2y) / 2
        c.save()
        c.translate(mx, my)
        c.rotate(twitch * 0.25 * m)
        c.translate(-mx, -my)

        def ear_path(cc, b1x=b1x, b1y=b1y, b2x=b2x, b2y=b2y, tx=tx, ty=ty):
            cc.move_to(b1x, b1y)
            cc.curve_to(lerp(b1x, tx, 0.45) - 4 * m, lerp(b1y, ty, 0.5), tx - 6 * m, ty + 10, tx, ty)
            cc.curve_to(tx + 6 * m, ty + 10, lerp(b2x, tx, 0.45) + 4 * m, lerp(b2y, ty, 0.5), b2x, b2y)
            cc.close_path()

        st.part(c, ear_path, PATCH, mx, (my + ty) / 2, 46, seed=11 + i)
        ix, iy = lerp(mx, tx, 0.18), lerp(my, ty, 0.18)
        c.move_to(lerp(b1x, mx, 0.35), lerp(b1y, my, 0.35))
        c.curve_to(lerp(b1x, tx, 0.5), lerp(b1y, ty, 0.5), lerp(ix, tx, 0.6) - 3 * m, lerp(iy, ty, 0.6),
                   lerp(ix, tx, 0.78), lerp(iy, ty, 0.78))
        c.curve_to(lerp(ix, tx, 0.6) + 3 * m, lerp(iy, ty, 0.6), lerp(b2x, tx, 0.5), lerp(b2y, ty, 0.5),
                   lerp(b2x, mx, 0.35), lerp(b2y, my, 0.35))
        c.close_path()
        c.set_source_rgba(*PINK[:3], 0.85)
        c.fill()
        c.restore()

    hp = head_path_fn(yaw)
    _erase(c, [hp])   # the ear bases must not show through the translucent wash
    st.part(c, hp, FUR, 0, -4, 80, seed=21)
    c.save()
    hp(c)
    c.clip()
    cx_, cy_, crx, cry, crot = _f(CAP, yaw)
    st.fill_only(c, lambda cc: ellipse(cc, X(cx_), cy_, crx, cry, m * crot), PATCH, X(cx_), cy_, 60, seed=22)
    if real:  # fur texture
        c.set_line_width(1.4)
        for i in range(60):
            a = i * 2.39996
            r = 10 + (i * 37) % 62
            px, py = math.cos(a) * r, math.sin(a) * r * 0.8
            c.move_to(px, py)
            c.line_to(px - 6 * m, py + 4)
            c.set_source_rgba(0.45, 0.32, 0.2, 0.2)
            c.stroke()
    # muzzle: two soft whisker pads under the nose (no outline)
    nx, ny = _f(NOSE_P, yaw)
    nx = X(nx)
    spread = lerp(1.0, 0.82, abs(yaw))
    for px, py, rx, ry in ((nx - 12 * spread, ny + 16, 17, 13), (nx + 12 * spread, ny + 16, 17, 13)):
        g = cairo.RadialGradient(px - 2, py - 3, 0, px, py, rx * 1.15)
        g.add_color_stop_rgba(0, 1, 1, 1, 0.95)
        g.add_color_stop_rgba(0.7, *CREAM[:3], 0.85)
        g.add_color_stop_rgba(1, *CREAM[:3], 0.0)
        c.set_source(g)
        ellipse(c, px, py, rx * 1.15, ry * 1.15)
        c.fill()
    c.restore()

    for pair in (EYE_A, EYE_B):
        ex, ey, er = _f(pair, yaw)
        st.eye(c, X(ex), ey, er, eyes, iris=IRIS, slit=real)
    for pair in (BLUSH_A, BLUSH_B):
        bx, by_, br = _f(pair, yaw)
        st.blush(c, X(bx), by_, br, 0.4)
    if tongue > 0:
        ellipse(c, nx + 1, ny + 26 + 8 * tongue, 8, 4 + 11 * tongue)
        c.set_source_rgba(*hexc("#ec7f8c"))
        c.fill()
    # nose
    c.move_to(nx - 8, ny - 3)
    c.curve_to(nx - 4, ny - 7, nx + 4, ny - 7, nx + 8, ny - 3)
    c.curve_to(nx + 8, ny + 1, nx + 3, ny + 6, nx, ny + 7)
    c.curve_to(nx - 3, ny + 6, nx - 8, ny + 1, nx - 8, ny - 3)
    c.close_path()
    c.set_source_rgba(*NOSE)
    c.fill()
    ellipse(c, nx - 2, ny - 3, 3, 1.6)
    c.set_source_rgba(1, 1, 1, 0.55)
    c.fill()
    st.line(c, [(nx, ny + 7), (nx, ny + 13)], 2.4, MOUTH)
    if happy > 0.3 and st.faces:
        st.smile(c, nx - 6, ny + 14, 12, MOUTH, 1.1)
        st.smile(c, nx + 6, ny + 14, 12, MOUTH, 1.1)
    else:
        c.move_to(nx, ny + 13)
        c.curve_to(nx - 2, ny + 18, nx - 8, ny + 19, nx - 12, ny + 15)
        c.move_to(nx, ny + 13)
        c.curve_to(nx + 2, ny + 18, nx + 8, ny + 19, nx + 12, ny + 15)
        c.set_source_rgba(*MOUTH)
        c.set_line_width(2.4)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.stroke()
    # whiskers: the muzzle side always; the other side fades in as she faces the camera
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    wa = 0.85 if not real else 0.7
    for side, a in ((1, wa), (-1, wa * (1 - abs(yaw)))):
        if a < 0.03:
            continue
        sd = side * m
        c.set_source_rgba(1, 1, 1, a)
        c.set_line_width(2.2)
        ox, oy = nx + sd * 18 * spread, ny + 16
        for ex_, ey_ in ((70, -10), (76, 6), (68, 22)):
            c.move_to(ox, oy)
            c.curve_to(ox + sd * 30, oy + ey_ * 0.3, ox + sd * (ex_ - 24), oy + ey_, ox + sd * ex_, oy + ey_)
            c.stroke()
    c.pop_group_to_source()
    c.paint()
    c.restore()


# ------------------------------------------------------------------ pose
def head_pose(turn, lick):
    """Head centre (local) and yaw for a turn 0..1 and a lick dip 0..1."""
    k = ease(turn)
    hx = lerp(212, 58, k)
    hy = lerp(-222, -212, k) - 34 * math.sin(math.pi * k) + 30 * lick
    yaw = math.cos(math.pi * k)
    return hx, hy, yaw


def to_world(x, y, s, lx, ly):
    return x + lx * s, y + ly * s


def mouth_world(x, y, s, turn=0.0, lick=0.0):
    hx, hy, yaw = head_pose(turn, lick)
    nx, ny = _f(NOSE_P, yaw)
    return to_world(x, y, s, hx + (nx if yaw >= 0 else -nx), hy + ny + 16)


def _torso(cc, br):
    def P(x, y):
        return x, y * br
    cc.move_to(*P(180, -8))
    cc.curve_to(*P(80, -2), *P(-80, -2), *P(-170, -6))
    cc.curve_to(*P(-236, -10), *P(-252, -60), *P(-240, -102))       # rump
    cc.curve_to(*P(-226, -152), *P(-190, -184), *P(-140, -184))     # hips
    cc.curve_to(*P(-90, -184), *P(-50, -168), *P(0, -168))          # back (slight dip)
    cc.curve_to(*P(50, -168), *P(80, -186), *P(120, -186))          # shoulders
    cc.curve_to(*P(168, -186), *P(204, -152), *P(208, -108))        # chest
    cc.curve_to(*P(211, -62), *P(202, -22), *P(180, -8))
    cc.close_path()


def _tail_pts(tail):
    """Tail centreline: out from the rump, round the haunch along the ground, tip curling up and swaying."""
    wob = math.sin(tail)
    p0, p1, p2, p3 = (-226, -92), (-270, -62), (-262, -8), (-196, -8)
    pts = []
    for i in range(6):   # smooth bend round the rump
        t = i / 5
        u = 1 - t
        pts.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    pts += [(-146, -9), (-96, -10)]
    tip_a = -0.5 + 0.25 * wob
    x, y = pts[-1]
    for i, L in enumerate((26, 22, 18)):
        a = tip_a * (i + 1) / 2
        x, y = x + L * math.cos(a), y + L * math.sin(a)
        pts.append((x, y))
    return pts


def _erase(c, parts):
    """Remove what these shapes cover inside the current group (the part in front is drawn next)."""
    c.save()
    c.set_operator(cairo.OPERATOR_DEST_OUT)
    c.set_source_rgba(0, 0, 0, 1)
    for p in parts:
        p(c)
        c.fill()
    c.restore()


def draw(c, st, x, y, s, eyes=0.0, turn=0.0, lick=0.0, tongue=0.0, tail=0.0, ear=0.0, breathe=0.0, happy=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    st.shadow(c, 10, 6, 290, 24, 0.18)
    br = 1.0 + 0.018 * breathe
    hx, hy, yaw = head_pose(turn, lick)

    c.push_group()  # the whole cat in one group: parts in front erase what they cover (watercolour is translucent)

    # far front leg (behind the body, a little further forward, in shadow)
    far_leg = [lambda cc: capsule(cc, (150, -46), 28, (240, -30), 21),
               lambda cc: ellipse(cc, 268, -26, 30, 19)]
    st.silhouette(c, far_leg, FUR_FAR, 220, -34, 60, seed=41)

    # body: torso + haunch + neck as ONE silhouette
    def torso(cc):
        _torso(cc, br)

    def haunch(cc):
        ellipse(cc, -142, -88 * br, 94, 80 * br, -0.08)

    nr = (NECK_ROOT[0], NECK_ROOT[1] * br)

    def neck(cc):
        capsule(cc, nr, 66, (hx, hy + 24), 50)

    def nape(cc):  # blends the back line into the neck (no step where they meet)
        capsule(cc, (30, -160 * br), 10, (hx, hy + 24), 46)

    body = [torso, haunch, neck, nape]
    _erase(c, body)
    st.silhouette(c, body, FUR, 0, -110, 250, seed=31)

    # markings, clipped to the body (soft-edged wash, no ink)
    c.save()
    torso(c)
    c.clip()
    st.fill_only(c, lambda cc: ellipse(cc, -96, -176 * br, 128, 52, 0.06), PATCH, -96, -170, 120, seed=32)
    st.fill_only(c, lambda cc: ellipse(cc, -214, -124 * br, 46, 40, 0.3), PATCH, -214, -124, 46, seed=33)
    g = cairo.RadialGradient(196, -112, 0, 192, -104, 78)   # cream bib
    g.add_color_stop_rgba(0, 1, 1, 1, 0.9)
    g.add_color_stop_rgba(0.65, *CREAM[:3], 0.7)
    g.add_color_stop_rgba(1, *CREAM[:3], 0.0)
    c.set_source(g)
    ellipse(c, 192, -104, 70, 90)
    c.fill()
    c.restore()
    # thigh crease (interior line, lighter than the outline)
    ink = getattr(st, "ink", FUR.line)
    pts = [(-142 + 94 * math.cos(a), -88 * br + 80 * br * math.sin(a))
           for a in [math.radians(v) for v in range(205, 318, 6)]]
    st.line(c, pts, 2.6, ink, alpha=0.5, seed=5)

    # hind paw tucked forward under the belly (the tail lies over it)
    hind = [lambda cc: ellipse(cc, -78, -16, 30, 13)]
    _erase(c, hind)
    st.silhouette(c, hind, FUR, -78, -16, 30, seed=44)

    # tail (in front of the haunch and the hind paw, along the ground)
    tp = _tail_pts(tail)
    n = len(tp)
    radii = [lerp(19, 12, i / (n - 1)) for i in range(n)]
    tail_parts = [(lambda cc, i=i: capsule(cc, tp[i], radii[i], tp[i + 1], radii[i + 1])) for i in range(n - 1)]
    _erase(c, tail_parts)
    st.silhouette(c, tail_parts, PATCH, -150, -20, 120, seed=51)
    c.save()  # cream tip
    for p in tail_parts[-2:]:
        p(c)
    c.clip()
    ex, ey = tp[-1]
    g = cairo.RadialGradient(ex, ey, 0, ex, ey, 30)
    g.add_color_stop_rgba(0, *CREAM[:3], 1)
    g.add_color_stop_rgba(0.75, *CREAM[:3], 1)
    g.add_color_stop_rgba(1, *CREAM[:3], 0)
    c.set_source(g)
    c.paint()
    c.restore()

    # near front leg on top
    near_leg = [lambda cc: capsule(cc, (128, -40), 32, (226, -24), 23),
                lambda cc: ellipse(cc, 252, -20, 32, 20)]
    _erase(c, near_leg)
    st.silhouette(c, near_leg, FUR, 200, -30, 60, seed=45)
    for tx in (262, 274):   # toes
        st.line(c, [(tx, -32), (tx + 3, -14)], 2.2, shade(FUR.dark, -0.1), alpha=0.8)

    # head (erase what it covers, then draw it)
    hp = head_path_fn(yaw)
    c.save()
    c.translate(hx, hy)
    _erase(c, [hp])
    c.restore()
    draw_head(c, st, hx, hy, 1.0, yaw, eyes, tongue, ear, happy)

    c.pop_group_to_source()
    c.paint()
    c.restore()
