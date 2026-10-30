"""ROLY — Cymothoa exigua, the tongue-eating isopod (a crustacean, NOT a louse).

Tan shell, strongly vaulted; head partly sunk into the first body segment; well-developed dark eyes;
two pairs of widely separated antennae; seven pairs of hooked legs that get longer towards the back;
tail plate (pleotelson) wider than it is long. Calm, settled, unhurried — she finds one place and stays.

Every individual starts out male and may later become female (protandrous hermaphrodite), so one body
plan serves both stages: `female=True` is longer, broader, and has a concave rear margin on the tail
plate. Real sizes (Brusca 1981): female 8.0-29.0 mm long, male 7.5-15.0 mm — she ends up roughly twice
his length, and FEMALE_S / MALE_S keep that ratio when scenes draw the two together.

draw(c, st, x, y, s, ...)            dorsal view, head facing right, (x, y) = body centre
    pose: ang, phase (idle sway + leg motion), female, grip (0..1 legs tucked and clamped down),
          swim (0..1 legs sweeping as paddles), blink, happy, alpha
draw_manca(c, st, x, y, s, phase)    the newborn speck: six pairs of legs, not seven (that is what makes
                                     it a manca), big eyes, free-swimming
draw_underside(c, st, x, y, s, ...)  ventral view: the brood pouch, `eggs` = 0..1 how full
to_world(...)                        local -> world point, for tags and sound cues
HEAD / TAIL                          local anchor points other scenes need

In the "real" style Roly loses the cartoon face and gains tighter segment and coxal-plate detail.
"""
import math

import cairo

from engine.core import TAU, Palette, ellipse, hexc, lerp, rng, rot_pt, smooth_path

NAME = "Roly"
SPECIES = "tongue-eating isopod"

# Tan, back usually without scattered chromatophores (Brusca 1981: "Color tan"). Pulled cool so she does
# not read as Pip (warm amber) or Pixie (pale honey) in the sea.
BODY = Palette("#d8c4a0", "#f4e9d6", "#9a8a74", "#53453a")
LEG = Palette("#d7c4a4", "#f0e6d2", "#9a8a70", "#564838")
EGG = Palette("#e6d2a8", "#f6ebd2", "#b9a079", "#7d6a4e")
EYE = hexc("#2b2320")

# ---- local geometry ------------------------------------------------------
# Head faces +x. Body centre is (0, 0). The pereon (seven leg-bearing segments) runs from the head at
# x=+122 back to x=-54; pereonite I is the longest and V-VI are the widest (Brusca 1981).
HEAD = (150.0, 0.0)
TAIL = (-160.0, 0.0)
PEREON = (122.0, 84.0, 59.0, 34.0, 9.0, -14.0, -35.0, -54.0)   # 8 boundaries = 7 segments
PLEON = (-54.0, -112.0)                                        # five small segments
LEG_LEN = (56.0, 60.0, 65.0, 70.0, 75.0, 80.0, 86.0)           # increasing posteriorly

FEMALE_S = 1.0     # relative scale for the two sexes, from the real length ranges
MALE_S = 0.55

# Outline half-widths down one side, head to tail. Mirrored for the other side.
_SIDE = (
    (158.0, 30.0), (140.0, 48.0), (122.0, 56.0), (100.0, 62.0), (60.0, 70.0), (20.0, 76.0),
    (-20.0, 80.0), (-50.0, 78.0), (-62.0, 70.0), (-80.0, 62.0), (-100.0, 56.0), (-112.0, 54.0),
    (-126.0, 58.0), (-142.0, 50.0), (-156.0, 34.0), (-164.0, 16.0),
)


def _halfwidth(x):
    """Body half-width at local x, by interpolation along _SIDE."""
    if x >= _SIDE[0][0]:
        return lerp(0.0, _SIDE[0][1], max(0.0, (168.0 - x) / (168.0 - _SIDE[0][0])))
    for (x0, w0), (x1, w1) in zip(_SIDE, _SIDE[1:]):
        if x1 <= x <= x0:
            return lerp(w0, w1, (x0 - x) / (x0 - x1))
    return _SIDE[-1][1]


def _outline(c, female=True, wide=1.0):
    """Closed dorsal outline. The female's tail plate has a concave rear margin, the male's does not."""
    rear = -150.0 if female else -172.0
    pts = [(168.0, 0.0)]
    pts += [(x, -w * wide) for x, w in _SIDE]
    pts += [(rear, 0.0)]
    pts += [(x, w * wide) for x, w in reversed(_SIDE)]
    smooth_path(c, pts, closed=True)


def to_world(x, y, s, ang, lx, ly):
    px, py = rot_pt(lx * s, ly * s, ang)
    return x + px, y + py


# ================================================================ adult (male or female)
def draw(c, st, x, y, s, ang=0.0, phase=0.0, female=True, grip=0.0, swim=0.0,
         blink=False, happy=0.0, alpha=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.push_group()
    _body(c, st, phase, female, grip, swim, blink, happy)
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()


def _body(c, st, phase, female, grip, swim, blink, happy):
    real = st.realistic
    wide = 1.0 if female else 0.88
    # she is clamped down when gripping, so the shadow tightens under her
    st.shadow(c, -6, 18 + 10 * (1 - grip), 190, 34, 0.18 - 0.05 * grip)

    _legs(c, st, phase, grip, swim, wide)
    _antennae(c, st, phase, wide)

    st.part(c, lambda cc: _outline(cc, female, wide), BODY, -10, 0, 180, seed=601)

    # ---- vaulting: a raised ridge along the midline, dark at the margins
    c.save()
    _outline(c, female, wide)
    c.clip()
    g = cairo.LinearGradient(0, -80 * wide, 0, 80 * wide)
    g.add_color_stop_rgba(0.0, *BODY.dark[:3], 0.40)
    g.add_color_stop_rgba(0.34, *BODY.light[:3], 0.30)
    g.add_color_stop_rgba(0.5, *BODY.light[:3], 0.46)
    g.add_color_stop_rgba(0.66, *BODY.light[:3], 0.30)
    g.add_color_stop_rgba(1.0, *BODY.dark[:3], 0.40)
    c.set_source(g)
    c.paint()
    # ---- segment boundaries: seven pereonites, then five small pleonites
    for i, bx in enumerate(PEREON):
        hw = _halfwidth(bx) * wide
        c.move_to(bx, -hw)
        c.curve_to(bx - 7, -hw * 0.45, bx - 7, hw * 0.45, bx, hw)
        c.set_source_rgba(*BODY.dark[:3], 0.55 if i else 0.75)
        c.set_line_width(4.0 if i else 5.5)
        c.stroke()
    for k in range(1, 6):
        bx = lerp(PLEON[0], PLEON[1], k / 5)
        hw = _halfwidth(bx) * wide
        c.move_to(bx, -hw * 0.92)
        c.curve_to(bx - 4, -hw * 0.4, bx - 4, hw * 0.4, bx, hw * 0.92)
        c.set_source_rgba(*BODY.dark[:3], 0.42)
        c.set_line_width(3.0)
        c.stroke()
    # ---- coxal plates: short marks inside the margin of each leg-bearing segment
    for i in range(7):
        x0, x1 = PEREON[i], PEREON[i + 1]
        for sgn in (-1, 1):
            c.move_to(x0 - 2, sgn * _halfwidth(x0 - 2) * wide * 0.80)
            c.curve_to(lerp(x0, x1, 0.5), sgn * _halfwidth(lerp(x0, x1, 0.5)) * wide * 0.86,
                       lerp(x0, x1, 0.8), sgn * _halfwidth(lerp(x0, x1, 0.8)) * wide * 0.84,
                       x1 + 2, sgn * _halfwidth(x1 + 2) * wide * 0.78)
            c.set_source_rgba(*BODY.dark[:3], 0.30 if not real else 0.42)
            c.set_line_width(2.4)
            c.stroke()
    if real:  # micro-texture over the shell
        r = rng(607)
        for _ in range(90):
            px, py = lerp(-165, 165, r.random()), lerp(-80, 80, r.random())
            c.arc(px, py, 1.3, 0, TAU)
            c.set_source_rgba(*BODY.dark[:3], 0.16)
            c.fill()
    c.restore()

    if not real:
        st.shine(c, 46, -26 * wide, 78, 15, -0.06, 0.30)
        st.shine(c, -74, -20 * wide, 40, 9, 0.05, 0.20)

    _uropods(c, st, female, wide)
    _head(c, st, blink, happy, wide, real)


def _head(c, st, blink, happy, wide, real):
    # Cephalon weakly to moderately immersed into pereonite I, so it sits nestled into the front segment.
    def cap(cc):
        smooth_path(cc, [(167, 0), (158, -29 * wide), (142, -46 * wide), (124, -52 * wide),
                         (120, 0), (124, 52 * wide), (142, 46 * wide), (158, 29 * wide)], closed=True)

    st.part(c, cap, BODY, 143, 0, 52, seed=602)
    c.save()
    cap(c)
    c.clip()
    g = cairo.LinearGradient(0, -50 * wide, 0, 50 * wide)
    g.add_color_stop_rgba(0.0, *BODY.dark[:3], 0.34)
    g.add_color_stop_rgba(0.5, *BODY.light[:3], 0.34)
    g.add_color_stop_rgba(1.0, *BODY.dark[:3], 0.34)
    c.set_source(g)
    c.paint()
    c.restore()

    er = (7.0 if real else 11.0)
    for sgn in (-1, 1):
        st.eye(c, 143, sgn * 36 * wide, er, 0.12 if blink else 1.0)
    if not real:
        for sgn in (-1, 1):
            st.blush(c, 152, sgn * 50 * wide, 9, 0.34)
        st.smile(c, 160, 6 * wide, 11, BODY.line, 0.7 + happy)


def _antennae(c, st, phase, wide):
    """Two pairs, widely separated at the base (the genus mark), about eight short segments each."""
    for sgn in (-1, 1):
        for k, (y0, spread, n, w) in enumerate(((14.0, 0.30, 8, 5.0), (34.0, 0.78, 8, 4.4))):
            wig = 0.07 * math.sin(phase * 1.6 + k * 1.3 + (0 if sgn > 0 else 0.7))
            px, py, a = 150.0, sgn * y0 * wide, sgn * (spread + wig)
            pts = [(px, py)]
            step = 10.5
            for i in range(n):
                a += sgn * 0.045
                px += step * math.cos(a) * 1.5
                py += step * math.sin(a) * 1.5
                pts.append((px, py))
                step *= 0.93
            st.limb(c, pts, w, LEG)
            for i, (qx, qy) in enumerate(pts[1:-1]):  # segment joints
                c.arc(qx, qy, w * 0.34, 0, TAU)
                c.set_source_rgba(*LEG.dark[:3], 0.45)
                c.fill()


def _legs(c, st, phase, grip, swim, wide):
    """Seven pairs of pereopods, increasing in length posteriorly, each ending in a hook that curls back
    under her — that is how she holds on. The pairs fan: the front ones reach forward, the back ones
    sweep back, so she reads as an animal rather than a comb. Built on the right side, then mirrored."""
    def rot(v, a):
        ca, sa = math.cos(a), math.sin(a)
        return (v[0] * ca - v[1] * sa, v[0] * sa + v[1] * ca)

    for i in range(7):
        x0, x1 = PEREON[i], PEREON[i + 1]
        rx = lerp(x0, x1, 0.5)
        ln = LEG_LEN[i]
        f = i / 6.0
        fan = lerp(-0.62, 1.00, f)                 # front legs reach forward, rear legs sweep back
        spread = lerp(1.0, 0.46, grip)             # gripping folds them in tight under her
        curl = lerp(0.90, 1.35, grip)
        for sgn in (-1, 1):
            beat = math.sin(phase * 2.2 - i * 0.55 + (0 if sgn > 0 else math.pi))
            a = fan + 0.13 * swim * beat + 0.035 * math.sin(phase * 1.8 + i)
            u = (-math.sin(a), math.cos(a))
            ry = _halfwidth(rx) * wide * 0.88      # root just under the shell edge
            kx, ky = rx + u[0] * ln * 0.62 * spread, ry + u[1] * ln * 0.62 * spread
            v = rot(u, curl)
            tx, ty = kx + v[0] * ln * 0.46 * spread, ky + v[1] * ln * 0.46 * spread
            w = rot(u, curl + 1.0)
            hx, hy = tx + w[0] * ln * 0.22, ty + w[1] * ln * 0.22
            pts = [(rx, sgn * ry), (kx, sgn * ky), (tx, sgn * ty)]
            st.limb(c, pts, 8.0 - i * 0.18, LEG)
            st.limb(c, [(tx, sgn * ty), (hx, sgn * hy)], 4.8, LEG)
            c.arc(kx, sgn * ky, 2.6, 0, TAU)       # knee joint
            c.set_source_rgba(*LEG.dark[:3], 0.40)
            c.fill()


def _uropods(c, st, female, wide):
    """Two narrow, elongate rami on each side of the tail plate, NOT reaching past its rear margin
    (Brusca 1981). Drawn as slim paddles rather than limbs so they read at small sizes."""
    rear = -150.0 if female else -172.0
    for sgn in (-1, 1):
        for k, (ang, ln, w) in enumerate(((0.30, 30.0, 7.0), (0.62, 26.0, 6.0))):
            bx, by = -120.0, sgn * 38.0 * wide
            a = math.pi + sgn * ang
            cx2, cy2 = bx + math.cos(a) * ln, by + math.sin(a) * ln
            if cx2 < rear + 10:
                cx2 = rear + 10
            ellipse(c, (bx + cx2) / 2, (by + cy2) / 2, ln * 0.62, w * 0.5,
                    math.atan2(cy2 - by, cx2 - bx))
            c.set_source_rgba(*LEG.base[:3], 1.0)
            c.fill_preserve()
            c.set_source_rgba(*LEG.dark[:3], 0.55)
            c.set_line_width(1.8)
            c.stroke()


# ================================================================ manca (the newborn speck)
def draw_manca(c, st, x, y, s, phase=0.0, ang=0.0, alpha=1.0):
    """The stage released from the brood pouch: a miniature of the adult but with SIX pairs of legs
    instead of seven — the missing last pair is what makes it a manca. Free-swimming, looking for a fish."""
    c.save()
    c.translate(x, y)
    c.rotate(ang + 0.12 * math.sin(phase * 1.7))
    c.scale(s, s)
    c.push_group()
    real = st.realistic
    body = [(78, 0), (70, -20), (52, -31), (16, -36), (-22, -36), (-50, -31), (-68, -22), (-76, 0),
            (-68, 22), (-50, 31), (-22, 36), (16, 36), (52, 31), (70, 20)]
    # six pairs of legs, sweeping as paddles
    for i in range(6):
        rx = 44.0 - i * 18.0
        for sgn in (-1, 1):
            beat = math.sin(phase * 3.4 - i * 0.6 + (0 if sgn > 0 else math.pi))
            ry = sgn * 31.0
            st.limb(c, [(rx, ry), (rx - 13, ry + sgn * 15), (rx - 20 - 4 * beat, ry + sgn * (25 + 3 * beat))],
                    4.2, LEG)
    for sgn in (-1, 1):  # two short antennae
        st.limb(c, [(70, sgn * 11), (88, sgn * 19), (100, sgn * 26)], 3.4, LEG)
        st.limb(c, [(70, sgn * 20), (86, sgn * 31), (95, sgn * 41)], 3.0, LEG)
    st.part(c, lambda cc: smooth_path(cc, body, closed=True), BODY, 0, 0, 80, seed=611)
    c.save()
    smooth_path(c, body, closed=True)
    c.clip()
    for k in range(5):  # a few segment lines, so it reads as the same animal
        bx = 34.0 - k * 19.0
        c.move_to(bx, -34)
        c.curve_to(bx - 4, -14, bx - 4, 14, bx, 34)
        c.set_source_rgba(*BODY.dark[:3], 0.40)
        c.set_line_width(2.6)
        c.stroke()
    c.restore()
    if not real:
        st.shine(c, 14, -14, 34, 7, -0.05, 0.32)
    er = 6.0 if real else 9.0  # eyes are proportionally huge at this size
    for sgn in (-1, 1):
        st.eye(c, 58, sgn * 15, er, 1.0)
    if not real:
        st.smile(c, 70, 2, 8, BODY.line, 0.9)
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()


# ================================================================ underside (the brood pouch)
def draw_underside(c, st, x, y, s, eggs=1.0, phase=0.0, ang=0.0, blink=False, alpha=1.0):
    """Ventral view of the female: the brood pouch (marsupium) slung under her belly, `eggs` = 0..1 how
    full. More than four hundred eggs ride in there."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.push_group()
    real = st.realistic
    _legs(c, st, phase, 0.25, 0.0, 1.0)
    _antennae(c, st, phase, 1.0)
    st.part(c, lambda cc: _outline(cc, True, 1.0), BODY, -10, 0, 180, seed=621)

    c.save()
    _outline(c, True, 1.0)
    c.clip()
    g = cairo.LinearGradient(0, -80, 0, 80)   # underside is flatter and paler than the vaulted back
    g.add_color_stop_rgba(0.0, *BODY.dark[:3], 0.30)
    g.add_color_stop_rgba(0.5, *BODY.light[:3], 0.26)
    g.add_color_stop_rgba(1.0, *BODY.dark[:3], 0.30)
    c.set_source(g)
    c.paint()
    c.restore()

    # the pouch: overlapping plates (oostegites) bulging with eggs, between the leg bases
    def pouch(cc):
        smooth_path(cc, [(96, 0), (84, -44), (50, -60), (0, -64), (-44, -58), (-70, -42), (-80, 0),
                         (-70, 42), (-44, 58), (0, 64), (50, 60), (84, 44)], closed=True)

    bulge = 0.55 + 0.45 * eggs
    c.save()
    c.translate(0, 0)
    c.scale(1.0, bulge)
    st.part(c, pouch, EGG, 0, 0, 96, seed=622)
    c.save()
    pouch(c)
    c.clip()
    if eggs > 0.02:
        r = rng(623)
        for _ in range(int(150 * eggs)):
            px, py = lerp(-78, 94, r.random()), lerp(-62, 62, r.random())
            rr = lerp(7.0, 11.0, r.random())
            if abs(px) < 92 and abs(py) < 60:
                ellipse(c, px, py, rr, rr * 0.86)
                c.set_source_rgba(*EGG.dark[:3], 0.55)
                c.set_line_width(1.6)
                c.stroke_preserve()
                c.set_source_rgba(*EGG.light[:3], 0.92)
                c.fill()
                if not real:
                    c.arc(px - rr * 0.3, py - rr * 0.32, rr * 0.28, 0, TAU)
                    c.set_source_rgba(1, 1, 1, 0.7)
                    c.fill()
    g = cairo.RadialGradient(0, 0, 54, 0, 0, 104)   # inner shadow: the sac bulges out at us
    g.add_color_stop_rgba(0, *EGG.dark[:3], 0.0)
    g.add_color_stop_rgba(1, *EGG.dark[:3], 0.55)
    c.set_source(g)
    c.paint()
    for k in range(5):  # the overlapping plate edges
        bx = 60.0 - k * 30.0
        c.move_to(bx, -64)
        c.curve_to(bx - 8, -24, bx - 8, 24, bx, 64)
        c.set_source_rgba(*EGG.dark[:3], 0.30)
        c.set_line_width(3.0)
        c.stroke()
    c.restore()
    pouch(c)   # soft rim around the whole pouch
    c.set_source_rgba(*BODY.dark[:3], 0.50)
    c.set_line_width(5.0)
    c.stroke()
    c.restore()

    _uropods(c, st, True, 1.0)
    er = 7.0 if real else 10.0
    for sgn in (-1, 1):
        st.eye(c, 145, sgn * 31, er, 0.12 if blink else 1.0)
    if not real:
        st.smile(c, 160, 6, 11, BODY.line, 0.7)
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()


# ================================================================ head-on (seen from in front)
def draw_facing(c, st, x, y, s, phase=0.0, female=True, grip=1.0, blink=False, happy=0.0,
                tilt=0.62, ang=0.0, alpha=1.0):
    """Roly seen head-on, her body receding away from us — the view you get looking into an open mouth.
    Used for the hook frame and the end card, where she sits on the floor of Mango's mouth looking back
    out at the camera.

    Her head is drawn as the front lobe of ONE silhouette, not a separate shape stuck on the front,
    because the cephalon really is immersed into the first body segment: a suture line marks the join.

    (x, y) is the middle of her face. `tilt` is how far above her the camera sits: 0 looks straight down
    her length, 1 looks down on her from above and the shell foreshortens almost to the dorsal view.
    """
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.push_group()
    real = st.realistic
    wide = 1.0 if female else 0.86
    sway = 2.2 * math.sin(phase * 1.3)
    f_ = lerp(1.0, 0.38, tilt)       # foreshortening, baked into the shell's coordinates
    SH = 14.0 * f_                   # y of the shoulders, where the head lobe begins

    def shell(cc):
        smooth_path(cc, [
            (112 * wide, SH), (118 * wide, -38 * f_), (110 * wide, -92 * f_),
            (94 * wide, -146 * f_), (72 * wide, -190 * f_), (40 * wide, -218 * f_), (0, -228 * f_),
            (-40 * wide, -218 * f_), (-72 * wide, -190 * f_), (-94 * wide, -146 * f_),
            (-110 * wide, -92 * f_), (-118 * wide, -38 * f_), (-112 * wide, SH),
            (-104 * wide, SH + 16), (-86 * wide, SH + 34), (-46 * wide, SH + 46), (0, SH + 50),
            (46 * wide, SH + 46), (86 * wide, SH + 34), (104 * wide, SH + 16),
        ], closed=True)

    _legs_facing(c, st, phase, grip, wide, f_, SH)
    _antennae_facing(c, st, phase, wide, SH)
    st.part(c, shell, BODY, 0, -60 * f_, 130, seed=641)

    c.save()
    shell(c)
    c.clip()
    # vaulted: bright along the midline ridge, dark down both flanks
    g = cairo.LinearGradient(-118 * wide, 0, 118 * wide, 0)
    g.add_color_stop_rgba(0.00, *BODY.dark[:3], 0.46)
    g.add_color_stop_rgba(0.30, *BODY.light[:3], 0.26)
    g.add_color_stop_rgba(0.50, *BODY.light[:3], 0.48)
    g.add_color_stop_rgba(0.70, *BODY.light[:3], 0.26)
    g.add_color_stop_rgba(1.00, *BODY.dark[:3], 0.46)
    c.set_source(g)
    c.paint()
    # the far end falls into shadow, which is what sells the depth
    g = cairo.LinearGradient(0, -228 * f_, 0, SH)
    g.add_color_stop_rgba(0.0, *BODY.dark[:3], 0.66)
    g.add_color_stop_rgba(1.0, *BODY.dark[:3], 0.0)
    c.set_source(g)
    c.paint()
    # segment bands, bowed towards us and closing up as they recede
    for k in range(11):
        fr = k / 10
        by = lerp(SH - 20 * f_, -214 * f_, fr ** 0.86)
        hw = (116 - 74 * fr ** 1.3) * wide
        c.move_to(-hw, by)
        c.curve_to(-hw * 0.4, by + 13 * f_ * (1 - fr * 0.55), hw * 0.4, by + 13 * f_ * (1 - fr * 0.55), hw, by)
        c.set_source_rgba(*BODY.dark[:3], 0.50 - 0.16 * fr)
        c.set_line_width(4.4 - 1.9 * fr)
        c.stroke()
    # the suture where the head is sunk into the first segment
    c.move_to(-106 * wide, SH + 2)
    c.curve_to(-50 * wide, SH + 15, 50 * wide, SH + 15, 106 * wide, SH + 2)
    c.set_source_rgba(*BODY.dark[:3], 0.46)
    c.set_line_width(4.6)
    c.stroke()
    if real:
        r = rng(643)
        for _ in range(70):
            px, py = lerp(-112, 112, r.random()) * wide, lerp(-222 * f_, SH, r.random())
            c.arc(px, py, 1.3, 0, TAU)
            c.set_source_rgba(*BODY.dark[:3], 0.16)
            c.fill()
    c.restore()

    if not real:
        st.shine(c, -26 * wide, SH + 14, 26, 8, -0.14, 0.26)

    er = 9.0 if real else 14.0
    for sgn in (-1, 1):
        st.eye(c, sgn * 48 * wide + sway * 0.3, SH + 24, er, 0.12 if blink else 1.0)
    if not real:
        for sgn in (-1, 1):
            st.blush(c, sgn * 78 * wide, SH + 36, 11, 0.32)
        st.smile(c, 0, SH + 38, 16, BODY.line, 0.8 + happy)
        st.line(c, [(-11, SH + 46), (0, SH + 51), (11, SH + 46)], 3.0, BODY.dark, 0.6)
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()


def _antennae_facing(c, st, phase, wide, SH):
    """Two pairs sweeping forward and out towards us, from the sides of the sunken head."""
    for sgn in (-1, 1):
        for k, (x0, y0, out, down, n, w) in enumerate(
                ((42.0, SH + 40.0, 0.58, 0.26, 8, 5.2), (84.0, SH + 24.0, 1.00, 0.08, 8, 4.4))):
            wig = 0.07 * math.sin(phase * 1.6 + k * 1.3 + (0 if sgn > 0 else 0.7))
            px, py = sgn * x0 * wide, y0
            pts = [(px, py)]
            step = 15.0
            for i in range(n):
                px += sgn * step * (out + wig + i * 0.035)
                py += step * (down - i * 0.055)
                pts.append((px, py))
                step *= 0.93
            st.limb(c, pts, w, LEG)


def _legs_facing(c, st, phase, grip, wide, f_, SH):
    """Seven pairs splaying to both sides. The far pairs sit higher and shorter, which is the whole
    depth cue, and they are drawn first so the shell covers their roots."""
    for i in range(7):
        fr = i / 6.0
        ry = lerp(SH - 8 * f_, -190 * f_, fr ** 0.9)
        hw = (112 - 46 * fr ** 1.2) * wide
        ln = lerp(92.0, 88.0, fr) * lerp(1.0, 0.74, grip)
        drop = lerp(44.0, 16.0, fr) * f_
        for sgn in (-1, 1):
            beat = math.sin(phase * 2.2 - i * 0.55 + (0 if sgn > 0 else math.pi))
            kx = sgn * (hw + ln * 0.56)
            ky = ry + drop * 0.45 + 2.0 * beat
            tx = sgn * (hw + ln * 0.80)
            ty = ry + drop + 3.0 * beat
            st.limb(c, [(sgn * hw * 0.84, ry), (kx, ky), (tx, ty)], 8.6 - 0.66 * i, LEG)
            st.limb(c, [(tx, ty), (tx - sgn * ln * 0.18, ty + ln * 0.20 * f_)], 5.4 - 0.38 * i, LEG)
