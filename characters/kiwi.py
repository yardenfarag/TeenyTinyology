"""KIWI — the shore crab / European green crab (Carcinus maenas), male.

Moss-green shell with a lighter speckle, five short teeth along the rim behind each eye and three low lobes
between the eyes (the species mark), eyes on short stalks, two claws, four walking legs a side. Yellow-olive
underside. Easy-going, a bit proud of his shell; becomes a doting carer once Toffee moves in.

His tail flap (abdomen) is the story: a male's is narrow, a "lighthouse" shape folded under the body; a
female's is wide and round, because that is where she carries her eggs. `flap` morphs between the two
(Kristensen et al. 2012: infected males grow a broader, longer, segmented abdomen; claws stay small).

draw(c, st, x, y, s, ...)             front view, eyes up, claws in front. (x, y) = shell centre.
    pose: ang, phase (idle sway, breathing, eye-stalk wiggle), walk (0..1 legs stepping sideways),
          blink, happy, look, pinch (0..1 claws open), raise_ (0..1 claws lifted), claw (claw size, 1.0 = a
          grown male's), sac (callable(c) drawn under the rear edge of the shell: Toffee's externa peeking out),
          xray (callable(c) drawn inside the shell), xray_alpha (0..1 how see-through the shell is), alpha
draw_underside(c, st, x, y, s, ...)   belly view: the tail flap folded over the sternum. flap 0 = narrow male,
          1 = wide female shape; lift (0..1 the flap folds back to show what is under it); under (callable(c)
          drawn between sternum and flap — the egg sac); eggs (0..1 a mother crab's own egg mass, for comparison)
to_world(...)                         local -> world
GROUND                                local y of the leg tips (for standing on things)
"""
import math

import cairo

from engine.core import TAU, Palette, ellipse, hexc, lerp, rng, rot_pt, smooth_path

NAME = "Kiwi"
SPECIES = "shore crab"

SHELL = Palette("#5c8a3a", "#8fb86a", "#3b5f24", "#243d16")
BELLY = Palette("#d8c86a", "#efe3a2", "#a39440", "#5e5420")
LEG = Palette("#6b9444", "#9dbf74", "#41611f", "#243d16")
TIP = Palette("#d8703a", "#f0a070", "#9a4a22", "#6a2e12")
EYE = hexc("#1e2419")

GROUND = 112.0
WIDTH = 150.0           # carapace half-width (local)

# Right half of the carapace rim, top (front, between the eyes) to bottom (rear). Mirrored for the left.
# Five teeth along the front-side margin: each tooth is an out-point followed by a notch.
_RIM_R = (
    (0.0, -80.0), (14.0, -82.0), (26.0, -78.0), (36.0, -82.0), (46.0, -76.0),      # three frontal lobes
    (58.0, -80.0), (66.0, -70.0),                                                   # tooth 1
    (80.0, -72.0), (88.0, -60.0),                                                   # tooth 2
    (102.0, -60.0), (108.0, -46.0),                                                 # tooth 3
    (122.0, -44.0), (126.0, -30.0),                                                 # tooth 4
    (140.0, -26.0), (142.0, -12.0),                                                 # tooth 5
    (150.0, 6.0), (146.0, 34.0), (130.0, 58.0), (102.0, 76.0), (60.0, 86.0), (0.0, 90.0),
)


def _rim(c, breathe=0.0):
    pts = [(x, y * (1 + breathe)) for x, y in _RIM_R]
    pts += [(-x, y * (1 + breathe)) for x, y in reversed(_RIM_R[1:])]
    # the teeth must stay sharp: a Catmull-Rom spline would round them, so draw straight along the toothed
    # margin and smooth only the rear curve
    c.move_to(*pts[0])
    n = len(pts)
    for i in range(1, n):
        x, y = pts[i]
        if 15 <= i <= 25 or 32 <= i <= 42:        # rear curve, both sides
            px, py = pts[i - 1]
            c.curve_to(px + (x - px) * 0.4, py + (y - py) * 0.05 + 8, x - (x - px) * 0.4, y - 2, x, y)
        else:
            c.line_to(x, y)
    c.close_path()


def to_world(x, y, s, ang, lx, ly):
    px, py = rot_pt(lx * s, ly * s, ang)
    return x + px, y + py


# ================================================================ front view
def draw(c, st, x, y, s, ang=0.0, phase=0.0, walk=0.0, blink=False, happy=0.0, look=(0.0, 0.0),
         pinch=0.0, raise_=0.0, claw=1.0, sac=None, xray=None, xray_alpha=0.0, alpha=1.0, night=False):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.push_group()
    real = st.realistic
    sway = 0.02 * math.sin(phase * 0.9)
    breathe = 0.012 * math.sin(phase * 1.7)
    c.rotate(sway)

    st.shadow(c, 0, GROUND - 6, 200, 26, 0.20)
    _legs(c, st, phase, walk)
    if sac is not None:                      # the externa hangs under the rear of the shell
        c.save()
        sac(c)
        c.restore()

    # ---- the shell
    st.part(c, lambda cc: _rim(cc, breathe), SHELL, 0, 0, 160, seed=701)
    c.save()
    _rim(c, breathe)
    c.clip()
    g = cairo.RadialGradient(-30, -40, 10, 0, 10, 180)
    g.add_color_stop_rgba(0.0, *SHELL.light[:3], 0.40)
    g.add_color_stop_rgba(0.6, *SHELL.light[:3], 0.06)
    g.add_color_stop_rgba(1.0, *SHELL.dark[:3], 0.45)
    c.set_source(g)
    c.paint()
    # the gastric grooves (the faint "H" every shore crab has) and a speckle of pale spots
    for pts in (((-44, -30), (-30, 10), (-40, 44)), ((44, -30), (30, 10), (40, 44)), ((-30, 10), (30, 10))):
        smooth_path(c, pts)
        c.set_source_rgba(*SHELL.dark[:3], 0.35)
        c.set_line_width(3.0)
        c.stroke()
    r = rng(703)
    for _ in range(26 if not real else 60):
        px, py = lerp(-140, 140, r.random()), lerp(-70, 80, r.random())
        c.arc(px, py, lerp(2.0, 5.0, r.random()), 0, TAU)
        c.set_source_rgba(*SHELL.light[:3], 0.35 if not real else 0.25)
        c.fill()
    if xray is not None and xray_alpha > 0:
        c.save()
        c.push_group()
        xray(c)
        c.pop_group_to_source()
        c.paint_with_alpha(xray_alpha)
        c.restore()
    c.restore()
    if not real:
        st.shine(c, -50, -50, 44, 12, 0.35, 0.28)
        st.shine(c, 70, -46, 22, 7, -0.6, 0.20)

    _claws(c, st, phase, pinch, raise_, claw, real)      # chelipeds are in front of the body
    _face(c, st, phase, blink, happy, look, real, night)
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()


def _face(c, st, phase, blink, happy, look, real, night):
    # eyes on short stalks rising from the front margin, just outside the frontal lobes
    wig = 0.06 * math.sin(phase * 2.3)
    for sgn in (-1, 1):
        bx, by = sgn * 50, -78
        tx, ty = sgn * (58 + 6 * wig), -104 + 3 * math.sin(phase * 2.3 + sgn)
        st.limb(c, [(bx, by), (lerp(bx, tx, 0.5), lerp(by, ty, 0.5) - 2), (tx, ty)], 12 if not real else 9, LEG)
        er = 15.0 if not real else 9.0
        if real:
            c.arc(tx, ty, er, 0, TAU)
            c.set_source_rgba(*EYE)
            c.fill()
        else:
            st.eye(c, tx, ty, er, 0.12 if blink else 1.0, look=look)
    if not real:
        st.blush(c, -78, -52, 12, 0.30)
        st.blush(c, 78, -52, 12, 0.30)
        st.smile(c, 0, -50, 26, SHELL.line, 0.6 + happy)
    else:  # mouthparts: a pair of small flaps under the front margin
        for sgn in (-1, 1):
            ellipse(c, sgn * 9, -66, 8, 5, sgn * 0.3)
            c.set_source_rgba(*SHELL.dark[:3], 0.7)
            c.fill()


def _legs(c, st, phase, walk):
    """Four walking legs a side, from the side margin, out and down to the ground. The hindmost pair is the
    slimmest and slightly flattened (Carcinus is a swimming crab only in name). Built right, mirrored left."""
    for i in range(4):
        f = i / 3.0
        rx, ry = lerp(138, 118, f), lerp(-6, 54, f)
        reach = lerp(86, 50, f)
        for sgn in (-1, 1):
            step = walk * 14 * math.sin(phase * 3.0 + i * 1.6 + (0 if sgn > 0 else math.pi))
            idle = 2.5 * math.sin(phase * 1.3 + i * 0.9 + (0.4 if sgn > 0 else 0))
            kx, ky = rx + reach * 0.62, ry - lerp(34, 12, f) + idle
            tx, ty = rx + reach + step, GROUND - max(0.0, step) * 0.5
            w = lerp(13.0, 9.0, f)
            pts = [(sgn * rx, ry), (sgn * kx, ky), (sgn * tx, ty)]
            st.limb(c, pts, w, LEG)
            c.arc(sgn * kx, ky, w * 0.36, 0, TAU)           # the knee joint
            c.set_source_rgba(*LEG.dark[:3], 0.45)
            c.fill()
            c.arc(sgn * tx, ty, w * 0.30, 0, TAU)           # the claw-like tip (dactyl)
            c.set_source_rgba(*LEG.dark[:3], 0.8)
            c.fill()


def _claws(c, st, phase, pinch, raise_, claw, real):
    """Chelipeds held in front: arm out to an elbow at the side, forearm back in to a plump hand whose two
    fingers point toward the middle. raise_ lifts both hands up beside the eyes (a wave / a guard pose);
    pinch opens the movable finger. claw scales the hand (a grown male's = 1.0; feminised males keep small ones)."""
    for sgn in (-1, 1):
        rx, ry = sgn * 112, 34
        bob = 3 * math.sin(phase * 1.5 + (0 if sgn > 0 else 1.1))
        ex, ey = lerp(sgn * 154, sgn * 178, raise_), lerp(68, 44, raise_) + bob
        hx, hy = lerp(sgn * 100, sgn * 176, raise_), lerp(98, -30, raise_) + bob
        d_rest = (math.pi - 0.35) if sgn > 0 else 0.35          # fingers toward the middle, a little down
        d_up = -math.pi / 2 - sgn * 0.30                         # fingers up, tilted inward
        d = lerp(d_rest, d_up, raise_)
        st.limb(c, [(rx, ry), (ex, ey)], 20, LEG)
        st.limb(c, [(ex, ey), (hx, hy)], 17, LEG)
        c.arc(ex, ey, 7.0, 0, TAU)
        c.set_source_rgba(*LEG.dark[:3], 0.45)
        c.fill()
        L = 54 * claw
        ux, uy = math.cos(d), math.sin(d)
        px, py = hx + ux * L * 0.12, hy + uy * L * 0.12
        st.ellipse(c, px, py, L * 0.56, L * 0.40, d, LEG, seed=710 + sgn)
        gap = 0.16 + 0.55 * pinch
        for k in range(2):                                   # k=0 fixed finger, k=1 movable finger (dactyl)
            a = d + (sgn * gap if k else -sgn * gap * 0.35)
            fx, fy = math.cos(a), math.sin(a)
            bx, by = hx + fx * L * 0.30, hy + fy * L * 0.30
            tx, ty = hx + fx * L * 1.08, hy + fy * L * 1.08
            st.limb(c, [(bx, by), (tx, ty)], L * 0.26, LEG)
            st.limb(c, [(lerp(bx, tx, 0.5), lerp(by, ty, 0.5)), (tx, ty)], L * 0.21, TIP)
        if not real:
            st.shine(c, px - ux * L * 0.1, py - L * 0.14, L * 0.26, L * 0.09, d, 0.25)


# ================================================================ belly view
def draw_underside(c, st, x, y, s, flap=0.0, lift=0.0, under=None, eggs=0.0, phase=0.0, ang=0.0,
                   alpha=1.0, blink=False):
    """Kiwi on his back / seen from below: the yellow-olive sternum with the tail flap folded over it.

    flap 0 → a male's narrow "lighthouse" (a slim triangle with a rounded tip), 1 → a female's wide, round,
    seven-segmented flap. The flap hinges at the rear (bottom) and its tip points forward (up). `under`
    draws between sternum and flap; `lift` swings the flap open on its hinge like a door (0.5 = edge-on,
    1 = folded right back below the body) so what is under it shows.
    `eggs` draws a mother crab's own orange-brown egg mass under the flap (for the comparison beat)."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.push_group()
    real = st.realistic
    st.shadow(c, 0, 96, 200, 24, 0.16)
    _legs(c, st, phase, 0.0)
    _claws(c, st, phase, 0.0, 0.0, 1.0, real)
    st.part(c, lambda cc: _rim(cc, 0.0), BELLY, 0, 0, 160, seed=721)
    c.save()
    _rim(c, 0.0)
    c.clip()
    g = cairo.RadialGradient(0, 0, 20, 0, 10, 170)
    g.add_color_stop_rgba(0.0, *BELLY.light[:3], 0.35)
    g.add_color_stop_rgba(1.0, *BELLY.dark[:3], 0.40)
    c.set_source(g)
    c.paint()
    # sternal plates: faint chevrons across the belly
    for k in range(5):
        yy = -50 + k * 28
        c.move_to(-70, yy + 10)
        c.curve_to(-30, yy, 30, yy, 70, yy + 10)
        c.set_source_rgba(*BELLY.dark[:3], 0.30)
        c.set_line_width(2.6)
        c.stroke()
    c.restore()
    # the eyes peek over the front rim (he is looking at us), so the belly view still has a face
    for sgn in (-1, 1):
        if not real:
            st.eye(c, sgn * 54, -90, 12, 0.12 if blink else 1.0)
    # what sits under the flap
    if eggs > 0:
        _egg_mass(c, st, eggs)
    if under is not None:
        c.save()
        under(c)
        c.restore()
    _flap(c, st, flap, lift, real)
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()


FLAP = Palette("#a9a94e", "#d2d088", "#6c6b26", "#3a3a14")
HINGE_Y = 84.0


def flap_outline(flap=0.0, lift=0.0):
    """Local points of the tail flap. It hinges on the rear edge of the body at y = HINGE_Y and lies folded
    forward over the belly, tip pointing up. Interpolates the male (slim, pointed) → female (wide, round)
    shape. lift swings it open on its hinge like a door: 0 closed over the belly, 0.5 edge-on, 1 folded
    right back below the body — so what was under it is uncovered."""
    male = ((0.0, -40.0), (14.0, -34.0), (22.0, 0.0), (28.0, 44.0), (30.0, HINGE_Y))
    female = ((0.0, -52.0), (52.0, -42.0), (84.0, 0.0), (92.0, 46.0), (94.0, HINGE_Y))
    k = 1.0 - 2.0 * lift                                   # signed foreshortening of the door
    pts = []
    for (mx, my), (fx, fy) in zip(male, female):
        px, py = lerp(mx, fx, flap), lerp(my, fy, flap)
        pts.append((px, HINGE_Y + (py - HINGE_Y) * k))
    right = pts
    left = [(-px, py) for px, py in reversed(pts[:-1])]
    return right + left


def _flap(c, st, flap, lift, real):
    pts = flap_outline(flap, lift)
    k = 1.0 - 2.0 * lift
    if abs(k) < 0.08:                                       # edge-on: just the hinge line
        st.line(c, [(pts[-1][0], HINGE_Y), (pts[4][0], HINGE_Y)], 6.0, FLAP.dark)
        return

    def path(cc):
        smooth_path(cc, pts, closed=True)

    # a soft shadow where it lies on (or hangs off) the belly
    st.shadow(c, 0, HINGE_Y + (pts[0][1] - HINGE_Y) * 0.5 + 6, abs(pts[2][0]) + 10,
              abs(pts[0][1] - HINGE_Y) * 0.5 + 8, 0.18)
    st.part(c, path, FLAP, 0, HINGE_Y + (pts[0][1] - HINGE_Y) * 0.5, 100, seed=731)
    c.save()
    path(c)
    c.clip()
    g = cairo.LinearGradient(0, pts[0][1], 0, HINGE_Y)
    g.add_color_stop_rgba(0.0, *FLAP.light[:3], 0.30)
    g.add_color_stop_rgba(1.0, *FLAP.dark[:3], 0.30)
    c.set_source(g)
    c.paint()
    # segments: a female's flap shows seven, a male's fewer (some fused). Drawn as plate boundaries.
    n = 7 if flap > 0.5 else 5
    top = pts[0][1]
    for i in range(1, n):
        yy = lerp(top, HINGE_Y, i / n)
        hw = 110
        c.move_to(-hw, yy + 4 * k)
        c.curve_to(-hw * 0.4, yy - 3 * k, hw * 0.4, yy - 3 * k, hw, yy + 4 * k)
        c.set_source_rgba(*FLAP.dark[:3], 0.55)
        c.set_line_width(3.0)
        c.stroke()
    c.restore()
    # a firm outline so the flap reads as a plate, not a stain
    path(c)
    c.set_source_rgba(*FLAP.line[:3], 0.85)
    c.set_line_width(3.6)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.stroke()
    # the hinge: a dark seam along the rear edge of the body
    st.line(c, [(pts[-1][0] - 4, HINGE_Y), (pts[4][0] + 4, HINGE_Y)], 5.0, FLAP.line, alpha=0.9)
    if flap > 0.5:                                          # the fringe of hairs a broadened flap grows
        for i in range(14):
            u = i / 13.0
            px, py = lerp(pts[1][0], pts[3][0], u), lerp(pts[1][1], pts[3][1], u)
            for sgn in (-1, 1):
                st.line(c, [(sgn * px, py), (sgn * (px + 9), py + 2 * k)], 1.8, FLAP.dark,
                        alpha=0.7 * (flap - 0.5) * 2)


def _egg_mass(c, st, eggs):
    EGG = Palette("#d98a4a", "#f2b57a", "#9a5a2a", "#5e3416")
    r = rng(741)
    for _ in range(int(140 * eggs)):
        px, py = lerp(-70, 70, r.random()), lerp(-30, 78, r.random())
        if (px / 80) ** 2 + ((py - 24) / 56) ** 2 > 1:
            continue
        c.arc(px, py, lerp(4.0, 6.5, r.random()), 0, TAU)
        c.set_source_rgba(*EGG.base[:3], 0.95)
        c.fill()
