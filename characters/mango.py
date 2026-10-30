"""MANGO — the spotted rose snapper, Lutjanus guttatus. Roly's fish.

Pale rose flanks with horizontal rows of silvery-blue dots, a yellow belly, bluish spots and broken
lines across the cheek, and one blackish blotch high on the back under the rear dorsal spines (the
field mark for the species). Ten dorsal spines, then the soft rays. Placid and completely unbothered:
she keeps eating, which is the whole point of the episode.

draw(c, st, x, y, s, ...)                side view facing right, (x, y) = body centre
    pose: ang, phase (tail beat + fin flutter), mouth (0..1 gape), blink, happy, alpha
draw_front(c, st, x, y, s, ...)           head-on with the mouth open — the hook frame and the end card
    mouth (0..1), inside (callable drawn on the mouth floor, in mouth-local units), teeth (0..1 shows
    the vomerine tooth patch in the roof: the teeth that leave the scratches on Roly's back)
draw_gill_chamber(c, st, x, y, s, ...)    cutaway of the gill arches, the set for the gill scenes
MOUTH_FLOOR / GILL_SLOT                   local anchor points scenes place Roly on
"""
import math

import cairo

from engine.core import TAU, Palette, ellipse, hexc, lerp, rng, rot_pt, smooth_path

NAME = "Mango"
SPECIES = "spotted rose snapper"

ROSE = Palette("#e08c7c", "#f8cabb", "#a8584a", "#6a362c")
BELLY = Palette("#f2c75b", "#ffeaa6", "#c2942f", "#7a5c18")
FIN = Palette("#dd8574", "#f3b8a6", "#a6544a", "#6a362c")
DOT = hexc("#6f9fc4")
BLOTCH = hexc("#3a3340")
GILL = Palette("#d4545c", "#f08a90", "#8e3038", "#5a1c22")
ARCH = Palette("#e7d8bc", "#fff4e0", "#a8977c", "#6a5a44")
MOUTH = Palette("#9c5a52", "#c98078", "#4e2a26", "#2e1814")

# ---- local anchor points -------------------------------------------------
MOUTH_FLOOR = (168.0, 26.0)    # side view: where an isopod sits on the floor of the mouth
GILL_SLOT = (138.0, 34.0)      # side view: just inside the gill cover
SNOUT = (236.0, 0.0)

_TOP = ((224, -24), (200, -46), (168, -70), (120, -88), (60, -98), (0, -100), (-60, -94), (-120, -76), (-166, -48))
_BOT = ((-166, 48), (-120, 72), (-60, 90), (0, 96), (60, 92), (120, 74), (170, 48), (206, 26))


def to_world(x, y, s, ang, lx, ly):
    px, py = rot_pt(lx * s, ly * s, ang)
    return x + px, y + py


# ================================================================ side view
HINGE = (138.0, 18.0)     # where the lower jaw swings from: back under the eye, as in a snapper
JAW_SWING = 0.55          # radians the lower jaw drops at mouth=1


def _body_path(c):
    """Body and head, ending at the UPPER jaw. The front of the silhouette is the upper jaw's biting
    edge running back to the hinge, so when the lower jaw drops the outline really opens."""
    pts = [(240, -6)]
    pts += list(_TOP)
    pts += [(-180, -30), (-180, 30)]
    pts += list(_BOT[:-2])
    pts += [(134, 58), (HINGE[0] - 2, HINGE[1] + 8)]        # throat, up to the jaw corner
    pts += [(172, 8), (206, 0)]                             # the upper jaw's biting edge
    smooth_path(c, pts, closed=True)


def _jaw_path(c):
    """Lower jaw, drawn in place for a shut mouth; the caller rotates it about HINGE to open."""
    smooth_path(c, [(HINGE[0] - 4, HINGE[1] - 4), (174, 10), (208, 8), (233, 13),
                    (228, 27), (196, 41), (162, 42), (136, 35)], closed=True)


# The two biting edges, front to hinge. The gap between them IS the mouth, so the cavity is built from
# them at the current jaw angle and can never spill outside the head.
_UPPER_EDGE = ((240, -8), (206, 0), (172, 8), (138, 19))
_LOWER_EDGE = ((136, 15), (174, 9), (208, 7), (234, 12))


def _swing(p, a):
    """Rotate a point about the jaw hinge by a radians."""
    ca, sa = math.cos(a), math.sin(a)
    dx, dy = p[0] - HINGE[0], p[1] - HINGE[1]
    return (HINGE[0] + dx * ca - dy * sa, HINGE[1] + dx * sa + dy * ca)


def _mouth_cavity(c, mouth):
    """The wedge between the upper jaw and the dropped lower jaw — the open mouth itself."""
    a = mouth * JAW_SWING
    pts = list(_UPPER_EDGE) + [_swing(p, a) for p in reversed(_LOWER_EDGE)]
    smooth_path(c, pts, closed=True)


def _jaw_teeth(c, mouth):
    """Canines along both biting edges — Lutjanidae carry enlarged ones at the front."""
    if mouth < 0.2:
        return
    a = min(1.0, mouth * 1.6)
    for k in range(5):     # upper jaw, hanging down
        f = k / 4
        px, py = lerp(228, 152, f), lerp(-3, 12, f)
        big = 1.0 + 0.9 * math.exp(-((f - 0.22) * 4.0) ** 2)
        _tooth(c, px, py, 5.6 * big, 9.6 * big, 1.0, a)


def _jaw_teeth_lower(c, mouth):
    if mouth < 0.2:
        return
    a = min(1.0, mouth * 1.6)
    for k in range(4):     # lower jaw, standing up (rotates with the jaw)
        f = k / 3
        px, py = lerp(222, 160, f), lerp(10, 15, f)
        big = 1.0 + 0.8 * math.exp(-((f - 0.22) * 4.0) ** 2)
        _tooth(c, px, py, 5.0 * big, 7.6 * big, -1.0, a)


def draw(c, st, x, y, s, ang=0.0, phase=0.0, mouth=0.0, blink=False, happy=0.0, alpha=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.push_group()
    real = st.realistic
    bend = 0.055 * math.sin(phase * 1.9)       # whole-body swim bend
    c.save()
    c.translate(-120, 0)
    c.rotate(bend)
    c.translate(120, 0)
    _tail(c, st, phase)
    c.restore()
    _fins_far(c, st, phase)

    # ---- the dark mouth, then the lower jaw over it. Both go before the body so the body's edge
    # covers the hinge, and so the jaw reads as swinging out from under the head.
    if mouth > 0.02:
        _mouth_cavity(c, mouth)
        g = cairo.RadialGradient(170, 22, 4, 170, 22, 92)
        g.add_color_stop_rgba(0, *MOUTH.dark[:3], 1)
        g.add_color_stop_rgba(1, *MOUTH.base[:3], 1)
        c.set_source(g)
        c.fill()
    c.save()
    c.translate(*HINGE)
    c.rotate(mouth * JAW_SWING)
    c.translate(-HINGE[0], -HINGE[1])
    _jaw_teeth_lower(c, mouth)
    st.part(c, _jaw_path, ROSE, 186, 24, 56, seed=711)
    c.save()
    _jaw_path(c)
    c.clip()
    g = cairo.LinearGradient(0, 4, 0, 44)       # rose jaw, yellow only along the underside
    g.add_color_stop_rgba(0.0, *ROSE.dark[:3], 0.30)
    g.add_color_stop_rgba(0.55, *ROSE.base[:3], 0.0)
    g.add_color_stop_rgba(1.0, *BELLY.base[:3], 0.70)
    c.set_source(g)
    c.paint()
    c.restore()
    c.restore()

    st.part(c, _body_path, ROSE, 0, 0, 240, seed=701)
    _jaw_teeth(c, mouth)

    c.save()
    _body_path(c)
    c.clip()
    # yellow belly, blended up into the rose flank
    g = cairo.LinearGradient(0, -20, 0, 100)
    g.add_color_stop_rgba(0.0, *BELLY.base[:3], 0.0)
    g.add_color_stop_rgba(0.45, *BELLY.base[:3], 0.55)
    g.add_color_stop_rgba(1.0, *BELLY.light[:3], 0.95)
    c.set_source(g)
    c.paint()
    # back darkens
    g = cairo.LinearGradient(0, -100, 0, -10)
    g.add_color_stop_rgba(0.0, *ROSE.dark[:3], 0.45)
    g.add_color_stop_rgba(1.0, *ROSE.dark[:3], 0.0)
    c.set_source(g)
    c.paint()
    # the field mark: a blackish blotch high on the back, under the rear dorsal spines
    g = cairo.RadialGradient(-62, -62, 20, -62, -62, 54)     # soft bloom around the mark
    g.add_color_stop_rgba(0, *BLOTCH[:3], 0.34)
    g.add_color_stop_rgba(1, *BLOTCH[:3], 0.0)
    ellipse(c, -62, -62, 54, 40, -0.12)
    c.set_source(g)
    c.fill()
    smooth_path(c, [(-16, -66), (-30, -88), (-58, -96), (-88, -86), (-102, -62),
                    (-92, -40), (-62, -30), (-32, -40)], closed=True)   # the mark itself
    c.set_source_rgba(*BLOTCH[:3], 0.52)
    c.fill()
    ellipse(c, -64, -64, 26, 18, -0.2)
    c.set_source_rgba(*BLOTCH[:3], 0.30)
    c.fill()
    # horizontal rows of silvery-blue dots along the flanks
    for row in range(7):
        fy = row / 6
        for k in range(16):
            fx = k / 15
            px = lerp(196, -156, fx)
            py = lerp(-78, 72, fy) + 9 * math.sin(fx * 3.0 + row)
            rr = lerp(5.4, 3.4, fy) * (1.0 - 0.3 * fx)
            ellipse(c, px, py, rr, rr * 0.9)
            c.set_source_rgba(*DOT[:3], 0.40 - 0.16 * fy)
            c.fill()
            if not real:
                c.arc(px - rr * 0.3, py - rr * 0.3, rr * 0.34, 0, TAU)
                c.set_source_rgba(1, 1, 1, 0.45)
                c.fill()
    if real:
        r = rng(705)
        for _ in range(240):   # scale texture
            px, py = lerp(-170, 210, r.random()), lerp(-96, 92, r.random())
            c.arc(px, py, 2.2, 0, TAU)
            c.set_source_rgba(*ROSE.dark[:3], 0.10)
            c.fill()
    c.restore()

    _gill_cover(c, st, phase, real)
    _dorsal(c, st, phase)
    _fins_near(c, st, phase)
    _head(c, st, blink, happy, real, mouth)
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()


def _head(c, st, blink, happy, real, gape):
    # bluish spots and broken lines across the cheek
    for k in range(9):
        f = k / 8
        px, py = lerp(150, 212, f), lerp(-28, 16, f) + 10 * math.sin(f * 5)
        if k % 3 == 2:
            c.move_to(px, py)
            c.line_to(px + 14, py - 5)
            c.set_source_rgba(*DOT[:3], 0.45)
            c.set_line_width(3.4)
            c.set_line_cap(cairo.LINE_CAP_ROUND)
            c.stroke()
        else:
            ellipse(c, px, py, 4.4, 4.0)
            c.set_source_rgba(*DOT[:3], 0.45)
            c.fill()
    er = 15.0 if real else 21.0
    st.eye(c, 182, -40, er, 0.12 if blink else 1.0, iris=hexc("#c9a24a") if real else None)
    if not real:
        st.blush(c, 196, -8, 14, 0.30)
    if gape < 0.12:   # lip line where the two jaws meet
        c.move_to(234, 8)
        c.curve_to(206, 12, 176, 16, 140, 20)
        c.set_source_rgba(*ROSE.line[:3], 0.70)
        c.set_line_width(3.6)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.stroke()


def _gill_cover(c, st, phase, real):
    puff = 3.0 * math.sin(phase * 2.6)
    c.move_to(150, -66)
    c.curve_to(132 + puff, -30, 130 + puff, 14, 146, 46)
    c.set_source_rgba(*ROSE.dark[:3], 0.55)
    c.set_line_width(4.2)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.stroke()
    c.move_to(150, -66)   # the preopercle line in front of it
    c.curve_to(166 + puff * 0.5, -26, 164 + puff * 0.5, 10, 176, 34)
    c.set_source_rgba(*ROSE.dark[:3], 0.32)
    c.set_line_width(3.0)
    c.stroke()


def _dorsal(c, st, phase):
    """Ten spines, then the soft-rayed part behind them."""
    flut = 0.9 * math.sin(phase * 2.2)
    pts = [(118, -88)]
    for k in range(10):
        f = k / 9
        px = lerp(112, 16, f)
        pts.append((px, lerp(-104, -132, math.sin(f * math.pi) ** 0.6) + flut * f))
    pts.append((6, -118))
    smooth_path(c, pts + [(14, -96), (60, -96), (118, -88)], closed=True)
    c.set_source_rgba(*FIN.base[:3], 0.92)
    c.fill_preserve()
    c.set_source_rgba(*FIN.line[:3], 0.7)
    c.set_line_width(3.0)
    c.stroke()
    for k in range(10):   # the spines themselves
        f = k / 9
        px = lerp(112, 16, f)
        c.move_to(px, -92)
        c.line_to(px, lerp(-104, -130, math.sin(f * math.pi) ** 0.6) + flut * f)
        c.set_source_rgba(*FIN.line[:3], 0.55)
        c.set_line_width(2.6)
        c.stroke()
    # soft-rayed part, behind the spines
    smooth_path(c, [(6, -116), (-50, -124 + flut), (-104, -112 + flut), (-140, -86),
                    (-120, -78), (-60, -92), (0, -98)], closed=True)
    c.set_source_rgba(*FIN.base[:3], 0.88)
    c.fill_preserve()
    c.set_source_rgba(*FIN.line[:3], 0.65)
    c.set_line_width(3.0)
    c.stroke()
    for k in range(9):
        f = (k + 1) / 10
        c.move_to(lerp(2, -128, f), lerp(-100, -86, f))
        c.line_to(lerp(0, -132, f), lerp(-120, -104, f) + flut)
        c.set_source_rgba(*FIN.line[:3], 0.4)
        c.set_line_width(2.2)
        c.stroke()


def _tail(c, st, phase):
    sw = 14.0 * math.sin(phase * 2.4)
    smooth_path(c, [(-172, -30), (-214, -74 + sw), (-250, -92 + sw), (-240, -40 + sw * 0.4),
                    (-232, 0), (-240, 40 + sw * 0.4), (-250, 92 + sw), (-214, 74 + sw), (-172, 30)],
                closed=True)
    c.set_source_rgba(*FIN.base[:3], 0.92)
    c.fill_preserve()
    c.set_source_rgba(*FIN.line[:3], 0.7)
    c.set_line_width(3.2)
    c.stroke()
    for k in range(9):
        f = k / 8
        c.move_to(-176, lerp(-26, 26, f))
        c.line_to(lerp(-244, -244, f), lerp(-84, 84, f) + sw * (1 if f > 0.5 else 0.6))
        c.set_source_rgba(*FIN.line[:3], 0.38)
        c.set_line_width(2.2)
        c.stroke()


def _fins_far(c, st, phase):
    fl = 6.0 * math.sin(phase * 2.8)
    smooth_path(c, [(120, 30), (96, 70 + fl), (62, 86 + fl), (74, 50), (96, 32)], closed=True)
    c.set_source_rgba(*FIN.dark[:3], 0.55)
    c.fill()


def _fins_near(c, st, phase):
    fl = 7.0 * math.sin(phase * 2.8 + 0.7)
    # pectoral fin
    smooth_path(c, [(132, 16), (112, 62 + fl), (70, 82 + fl), (84, 40), (112, 18)], closed=True)
    c.set_source_rgba(*FIN.base[:3], 0.9)
    c.fill_preserve()
    c.set_source_rgba(*FIN.line[:3], 0.6)
    c.set_line_width(2.8)
    c.stroke()
    for k in range(5):
        f = (k + 1) / 6
        c.move_to(lerp(126, 100, f), lerp(18, 30, f))
        c.line_to(lerp(108, 74, f), lerp(60, 78, f) + fl)
        c.set_source_rgba(*FIN.line[:3], 0.38)
        c.set_line_width(2.0)
        c.stroke()
    # anal fin (three spines, then soft rays)
    smooth_path(c, [(-30, 92), (-64, 112 - fl), (-104, 104 - fl), (-130, 78), (-90, 84), (-50, 90)],
                closed=True)
    c.set_source_rgba(*FIN.base[:3], 0.88)
    c.fill_preserve()
    c.set_source_rgba(*FIN.line[:3], 0.6)
    c.set_line_width(2.8)
    c.stroke()


# ================================================================ head-on, mouth open
def draw_front(c, st, x, y, s, mouth=1.0, inside=None, teeth=1.0, blink=False, phase=0.0, alpha=1.0):
    """Head-on with the mouth open — the hook frame and the end card.

    Built as a real jaw rather than a hole: a snout and upper lip above the gape, a hinged lower jaw and
    chin below, snapper canines on both rims (Lutjanidae have enlarged canine teeth), and a throat that
    falls away into the dark so the opening reads as depth.

    `inside(cc)` is called clipped to the cavity, with (0, 0) at the centre of the gape; the floor sits
    at about y = +58, which is where an isopod the size of the tongue sits.
    `teeth` fades in the vomerine tooth patch on the roof — the teeth that score Roly's back.
    """
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.push_group()
    real = st.realistic
    breathe = 1.0 + 0.012 * math.sin(phase * 2.0)
    gw, gh = 150.0 * (0.40 + 0.60 * mouth), 96.0 * (0.14 + 0.86 * mouth)
    gy = 44.0                      # centre of the gape
    jaw = 26.0 * mouth             # how far the lower jaw has dropped

    def head(cc):
        smooth_path(cc, [(0, -188), (62, -172), (116, -128), (152, -58), (160, 18),
                         (138, 92), (92, 150), (42, 182), (0, 190), (-42, 182), (-92, 150),
                         (-138, 92), (-160, 18), (-152, -58), (-116, -128), (-62, -172)], closed=True)

    def gape(cc):
        smooth_path(cc, [(0, gy - gh), (gw * 0.60, gy - gh * 0.70), (gw, gy - gh * 0.06),
                         (gw * 0.72, gy + gh * 0.66 + jaw), (0, gy + gh + jaw),
                         (-gw * 0.72, gy + gh * 0.66 + jaw), (-gw, gy - gh * 0.06),
                         (-gw * 0.60, gy - gh * 0.70)], closed=True)

    c.save()
    c.scale(1.0, breathe)
    for sgn in (-1, 1):   # gill covers flaring behind the head
        smooth_path(c, [(sgn * 128, -74), (sgn * 178, -18), (sgn * 172, 70), (sgn * 118, 120),
                        (sgn * 126, 26)], closed=True)
        c.set_source_rgba(*ROSE.dark[:3], 0.70)
        c.fill_preserve()
        c.set_source_rgba(*ROSE.line[:3], 0.45)
        c.set_line_width(2.6)
        c.stroke()
    st.part(c, head, ROSE, 0, 0, 190, seed=731)
    c.save()
    head(c)
    c.clip()
    g = cairo.LinearGradient(0, -188, 0, 190)
    g.add_color_stop_rgba(0.0, *ROSE.dark[:3], 0.48)
    g.add_color_stop_rgba(0.40, *ROSE.light[:3], 0.28)
    g.add_color_stop_rgba(1.0, *BELLY.base[:3], 0.55)
    c.set_source(g)
    c.paint()
    for sgn in (-1, 1):   # bluish cheek spots and broken lines
        for k in range(7):
            f = k / 6
            px, py = sgn * lerp(76, 146, f), lerp(-104, 54, f)
            if k % 3 == 2:
                c.move_to(px, py)
                c.line_to(px + sgn * 16, py + 6)
                c.set_source_rgba(*DOT[:3], 0.42)
                c.set_line_width(3.6)
                c.set_line_cap(cairo.LINE_CAP_ROUND)
                c.stroke()
            else:
                ellipse(c, px, py, 5.0, 4.6)
                c.set_source_rgba(*DOT[:3], 0.42)
                c.fill()
    # the snout: a soft ridge running down to the upper lip, so the face has a front
    g = cairo.LinearGradient(0, -120, 0, gy - gh)
    g.add_color_stop_rgba(0.0, *ROSE.light[:3], 0.0)
    g.add_color_stop_rgba(1.0, *ROSE.light[:3], 0.42)
    ellipse(c, 0, lerp(-120, gy - gh, 0.55), 92, 76)
    c.set_source(g)
    c.fill()
    c.restore()

    # ---- the cavity
    gape(c)
    g = cairo.RadialGradient(0, gy - gh * 0.12, 4, 0, gy, max(gw, gh) * 1.25)
    g.add_color_stop_rgba(0.00, 0.30, 0.13, 0.11, 1)
    g.add_color_stop_rgba(0.42, 0.11, 0.05, 0.045, 1)
    g.add_color_stop_rgba(1.00, *MOUTH.base[:3], 1)
    c.set_source(g)
    c.fill()

    c.save()
    gape(c)
    c.clip()
    # The vomerine tooth patch on the roof: a chevron-shaped pad of tiny teeth, which is what scores
    # the parasite's back while the fish feeds (Brusca & Gilligan 1983). Drawn as a pad with teeth
    # standing on it, not as scattered dots, so it reads as a structure.
    if teeth > 0.02:
        _vomer(c, gw, gh, gy, teeth)
    # the throat closes in at the back — painted BEFORE the occupant, so it never dims them
    g = cairo.RadialGradient(0, gy, max(gw, gh) * 0.45, 0, gy, max(gw, gh) * 1.3)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.55)
    c.set_source(g)
    c.paint()
    if inside is not None:
        c.save()
        c.translate(0, gy)
        c.push_group()
        inside(c)
        c.pop_group_to_source()
        c.paint()
        c.restore()
    c.restore()

    # ---- lips and teeth
    _jaw_rims(c, st, gape, gw, gh, gy, jaw, mouth, real)

    er = 18.0 if real else 25.0
    for sgn in (-1, 1):
        st.eye(c, sgn * 100, -84, er, 0.12 if blink else 1.0,
               iris=hexc("#c9a24a") if real else None)
    c.restore()
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()


def _vomer(c, gw, gh, gy, a):
    """The chevron tooth patch on the palate. Its arms sweep back from a point at the front centre."""
    w, h = gw * 0.56, gh * 0.40
    cy = gy - gh * 0.60
    c.save()
    c.translate(0, cy)

    def pad(cc):
        smooth_path(cc, [(0, h * 0.52), (w * 0.52, -h * 0.10), (w, -h * 0.62),
                         (w * 0.80, -h * 0.90), (0, -h * 0.18),
                         (-w * 0.80, -h * 0.90), (-w, -h * 0.62), (-w * 0.52, -h * 0.10)],
                    closed=True)

    pad(c)
    c.set_source_rgba(0.80, 0.63, 0.58, 0.92 * a)
    c.fill_preserve()
    c.set_source_rgba(0.54, 0.38, 0.34, 0.70 * a)
    c.set_line_width(2.6)
    c.stroke()
    c.save()
    pad(c)
    c.clip()
    for row in range(3):                      # rows of little teeth following the chevron
        fr = row / 2
        for k in range(13):
            u = k / 12 * 2 - 1                # -1..1 across the patch
            px = u * w * (0.94 - 0.16 * fr)
            py = -abs(u) * h * 0.62 + h * (0.40 - 0.30 * fr)
            rr = lerp(4.6, 3.0, fr) * (1.0 - 0.25 * abs(u))
            c.move_to(px - rr * 0.6, py)
            c.line_to(px, py + rr * 1.5)
            c.line_to(px + rr * 0.6, py)
            c.close_path()
            c.set_source_rgba(0.99, 0.97, 0.93, 0.95 * a)
            c.fill_preserve()
            c.set_source_rgba(0.68, 0.56, 0.50, 0.50 * a)
            c.set_line_width(1.0)
            c.stroke()
    c.restore()
    c.restore()


def _jaw_rims(c, st, gape, gw, gh, gy, jaw, mouth, real):
    """A pale lip all the way round the gape, then the teeth standing on it. Snappers carry enlarged
    canines at the front of both jaws, which is what makes the open mouth read as a fish's."""
    gape(c)
    c.set_source_rgba(*ROSE.light[:3], 0.95)
    c.set_line_width(20.0)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.stroke()
    gape(c)
    c.set_source_rgba(*ROSE.line[:3], 0.55)
    c.set_line_width(4.0)
    c.stroke()

    if mouth < 0.25:
        return
    n = 11
    for k in range(n):       # upper jaw: teeth hang down from the roof rim
        f = k / (n - 1)
        a = lerp(-2.62, -0.52, f)
        px, py = gw * 0.96 * math.cos(a), gy + gh * 0.96 * math.sin(a)
        big = 1.0 + 1.15 * math.exp(-((f - 0.5) * 5.2) ** 2)   # canines at the front
        _tooth(c, px, py, 7.4 * big, 11.5 * big, 1.0, mouth)
    n = 9
    for k in range(n):       # lower jaw: teeth stand up from the floor rim
        f = k / (n - 1)
        a = lerp(0.60, 2.54, f)
        px = gw * 0.80 * math.cos(a)
        py = gy + (gh * 0.86 + jaw) * math.sin(a)
        big = 1.0 + 0.95 * math.exp(-((f - 0.5) * 5.2) ** 2)
        _tooth(c, px, py, 6.4 * big, 9.0 * big, -1.0, mouth)


def _tooth(c, px, py, w, h, dirn, a):
    c.move_to(px - w * 0.5, py)
    c.line_to(px, py + dirn * h)
    c.line_to(px + w * 0.5, py)
    c.close_path()
    c.set_source_rgba(0.99, 0.97, 0.92, 0.95 * min(1.0, a * 1.6))
    c.fill_preserve()
    c.set_source_rgba(0.75, 0.66, 0.58, 0.55 * min(1.0, a * 1.6))
    c.set_line_width(1.4)
    c.stroke()


# ================================================================ the gill chamber (a set)
def draw_gill_chamber(c, st, x, y, s, phase=0.0, alpha=1.0):
    """Cutaway of the gill arches: four curved bones, each with two rows of red filaments. Scenes place
    Roly on an arch with draw(..., grip=1). (x, y) = centre of the chamber; it fills roughly
    x -320..320, y -260..260 in local units."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.push_group()
    real = st.realistic
    for a in range(4):
        f = a / 3
        ax = lerp(-190, 150, f)
        sway = 5.0 * math.sin(phase * 1.6 + a * 0.8)
        arch = [(ax - 40, -230), (ax + 6 + sway, -120), (ax + 20 + sway, 0),
                (ax + 4 + sway, 120), (ax - 44, 230)]
        # filaments on both sides of the arch
        for side in (-1, 1):
            for k in range(26):
                t = k / 25
                i = min(int(t * 4), 3)
                lt = t * 4 - i
                px = lerp(arch[i][0], arch[min(i + 1, 4)][0], lt)
                py = lerp(arch[i][1], arch[min(i + 1, 4)][1], lt)
                ln = lerp(44, 62, math.sin(t * math.pi)) * (1.0 - 0.18 * f)
                wob = 3.0 * math.sin(phase * 2.2 + k * 0.7 + a)
                c.move_to(px, py)
                c.curve_to(px + side * ln * 0.5, py + wob, px + side * ln * 0.85,
                           py + wob * 1.5, px + side * ln, py + wob * 2.2)
                c.set_source_rgba(*GILL.base[:3], 0.85 if side > 0 else 0.6)
                c.set_line_width(5.0)
                c.set_line_cap(cairo.LINE_CAP_ROUND)
                c.stroke()
        st.limb(c, arch, 26.0 - 2.0 * a, ARCH)
        if not real:
            st.shine(c, ax + 10 + sway, -40, 7, 90, 0.04, 0.22)
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()
