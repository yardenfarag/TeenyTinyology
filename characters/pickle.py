"""PICKLE — the cricket (female). Leafy green with olive wings, big dark eyes, very long antennae.
Calm, careful, a little shy. As a female she has an ovipositor (long egg-laying spike) and does not chirp.

draw(c, st, x, y, s, ...) — side view facing right, (x, y) = feet line centre.
pose: ang, phase (walk), walking, crouch (0..1 before a hop), antenna (wiggle phase), blink, happy,
      chew (0..1 mouth moving), wet (0..1 droopy/damp look), xray (callable(c) drawn inside the abdomen),
      xray_alpha (how see-through the abdomen is, 0..1), kick (0..1 hind legs thrust straight back on take-off,
      other legs tucked), slim (0..1 emptier, flatter tummy — e.g. after a worm has left),
      night (pale antennae so they still read against a dark sky)
ABDOMEN gives the abdomen ellipse (local) for x-ray effects; to_world() maps local points.
"""
import math

from engine.core import TAU, Palette, ellipse, hexc, rot_pt, smooth_path

NAME = "Pickle"
SPECIES = "cricket"
BODY = Palette("#7fae4a", "#c4e08a", "#3f6a22", "#2c4a16")
WING = Palette("#9aa85a", "#d6dfa0", "#5a6a2a", "#3a4a1a")
LEG = Palette("#6a9a3e", "#b0d27a", "#355a1c")
DARK = hexc("#2a3a14")
ABDOMEN = (-72, -58, 94, 50, -0.04)


def to_world(x, y, s, ang, lx, ly):
    px, py = rot_pt(lx * s, ly * s, ang)
    return x + px, y + py


def draw(c, st, x, y, s, ang=0.0, phase=0.0, walking=False, crouch=0.0, antenna=0.0, blink=False, happy=0.0,
         chew=0.0, wet=0.0, xray=None, xray_alpha=0.0, alpha=1.0, sx=1.0, sy=1.0, kick=0.0, slim=0.0, night=False):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s * sx, s * sy)
    c.push_group()
    real = st.realistic
    sh = 8 * math.sin(phase) if walking else 0.0
    st.shadow(c, -30, 4, 210, 16, 0.2)
    far = Palette("#5f8a38", "#94b866", "#2f4a18")
    tk = 22 * kick   # small legs tuck forward/up while airborne
    # far legs
    st.limb(c, [(40, -48), (60 + tk, -24 - tk * 0.6), (74 - sh + tk * 1.6, -tk)], 7, far)
    st.limb(c, [(10, -46), (14 + tk, -22 - tk * 0.6), (26 + sh + tk * 1.4, -tk)], 7, far)
    fk = (-140 + 10 * crouch, -124 + 34 * crouch)
    st.limb(c, [(-24, -58), (fk[0] + (-128 - fk[0]) * kick, fk[1] + (-62 - fk[1]) * kick),
                (-108 + sh + (-236 + 108) * kick, -2 + 26 * kick)], 12, far)
    # antennae (long, sweeping back over the body)
    wig = 10 * math.sin(antenna)
    droop = 30 * wet
    for k, (dx, w) in enumerate(((0, 2.4), (8, 3.0))):
        pts = [(118 + dx, -104), (150 + dx, -170 + droop), (60 + dx, -230 + wig + droop * 2),
               (-90 + dx, -215 - wig + droop * 2), (-200 + dx, -170 + wig * 0.6 + droop * 2)]
        smooth_path(c, pts)  # one continuous curve (no kink)
        c.set_source_rgba(*((0.78, 0.88, 0.6) if night else DARK[:3]), 0.9 if k else 0.6)  # pale at night
        c.set_line_width(w)
        c.stroke()
    # ovipositor + cerci
    st.line(c, [(-150, -54), (-238, -40)], 5, hexc("#3a3020"))
    st.line(c, [(-152, -70), (-198, -96)], 3, DARK)
    st.line(c, [(-150, -60), (-200, -66)], 3, DARK)
    # abdomen
    ax, ay, arx, ary, arot = ABDOMEN
    ary *= 1 - 0.2 * slim
    ay -= 0.2 * 50 * slim * 0.5
    arx *= 1 - 0.05 * slim
    st.ellipse(c, ax, ay, arx, ary, arot, BODY, seed=201)
    if xray is not None and xray_alpha > 0:
        # x-ray: contents seen *through* the green skin; the tummy keeps its shape and outline
        c.save()
        ellipse(c, ax, ay, arx * 0.86, ary * 0.78, arot)
        c.clip()
        c.set_source_rgba(0.78, 0.9, 0.58, 0.6 * xray_alpha)
        c.paint()
        c.push_group()
        xray(c)
        c.pop_group_to_source()
        c.paint_with_alpha(1.0 * xray_alpha)
        c.restore()
        st.ellipse(c, ax, ay, arx, ary, arot, BODY, seed=201, alpha=0.55 * xray_alpha)  # skin over the top
        ellipse(c, ax, ay, arx, ary, arot)
        c.set_source_rgba(*BODY.line[:3], 0.8 * xray_alpha)
        c.set_line_width(3.5)
        c.stroke()
        st.shine(c, ax - 24, ay - 30, 46, 10, -0.1, 0.35 * xray_alpha)
    for u in (-50, -10, 30) if not real else (-60, -35, -10, 15, 40):  # segment rings on the belly
        c.move_to(ax + u, ay + 6)
        c.curve_to(ax + u - 6, ay + 20, ax + u - 6, ay + 34, ax + u, ay + ary - 2)
        c.set_source_rgba(*BODY.dark[:3], 0.35 * (1 - 0.6 * xray_alpha))
        c.set_line_width(2.2)
        c.stroke()
    # folded wings over the back (also see-through in x-ray)

    def wing(cc):
        # folded wings sit high on the back so the round tummy shows below
        cc.move_to(8, -100)
        cc.curve_to(-40, -116, -112, -112, -150, -94)
        cc.curve_to(-110, -86, -40, -84, 10, -86)
        cc.close_path()

    st.part(c, wing, WING, -70, -88, 90, seed=202, alpha=1 - 0.35 * xray_alpha)
    c.set_source_rgba(*WING.dark[:3], 0.45 * (1 - 0.35 * xray_alpha))
    c.set_line_width(1.6)
    for k in range(3):
        c.move_to(0 - k * 8, -96 + k * 2)
        c.curve_to(-50, -106 + k * 2, -100, -102 + k * 2, -140, -94 + k)
        c.stroke()
    # thorax (pronotum)
    def pronotum(cc):
        cc.move_to(4, -104)
        cc.curve_to(30, -116, 58, -112, 70, -100)
        cc.curve_to(76, -80, 72, -56, 62, -48)
        cc.curve_to(40, -44, 18, -46, 6, -52)
        cc.curve_to(-2, -70, -2, -92, 4, -104)
        cc.close_path()

    st.part(c, pronotum, Palette("#6f9e3e", "#b4d67a", "#36601c", "#2c4a16"), 36, -78, 42, seed=203)
    st.shine(c, 30, -100, 18, 6, -0.15, 0.28)
    # near middle + front legs
    st.limb(c, [(48, -46), (70 + tk, -22 - tk * 0.6), (84 + sh + tk * 1.6, -tk)], 8, LEG)
    st.limb(c, [(16, -44), (22 + tk, -20 - tk * 0.6), (36 - sh + tk * 1.4, -tk)], 8, LEG)
    # head
    hr = (40, 40) if real else (46, 46)
    st.ellipse(c, 100, -86, hr[0], hr[1], 0.0, BODY, seed=204)
    st.shine(c, 92, -112, 16, 7, -0.2, 0.3)
    st.eye(c, 114, -96, 11 if not real else 13, 0.1 if blink else 1.0)
    st.blush(c, 120, -66, 9, 0.45)
    if not real:
        st.smile(c, 134, -72, 10, DARK, 1 + happy)
    # palps / mouth
    cy = 4 * math.sin(chew * TAU * 3) if chew > 0 else 0
    st.line(c, [(132, -58), (142, -40 + cy)], 3.5, DARK)
    st.line(c, [(124, -56), (128, -38 - cy)], 3.0, DARK)
    # big jumping hind leg (near side): thick femur angled up-back, tibia dropping behind the body
    hip = (-30, -52)
    kx, ky = -150 + 10 * crouch, -128 + 34 * crouch
    kx, ky = kx + (-136 - kx) * kick, ky + (-60 - ky) * kick   # take-off: leg straightens back

    fem = Palette("#5f9436", "#a8d070", "#2f5418", "#24420f")
    L = math.hypot(kx - hip[0], ky - hip[1])
    fa = math.atan2(ky - hip[1], kx - hip[0])

    def femur(cc):
        # drumstick: thick near the hip, slim at the knee
        cc.save()
        cc.translate(hip[0], hip[1])
        cc.rotate(fa)
        cc.move_to(0, -18)
        cc.curve_to(L * 0.35, -22, L * 0.75, -9, L, -6)
        cc.curve_to(L + 8, -4, L + 8, 4, L, 5)
        cc.curve_to(L * 0.75, 8, L * 0.35, 20, 0, 16)
        cc.curve_to(-10, 10, -10, -12, 0, -18)
        cc.close_path()
        cc.restore()

    st.part(c, femur, fem, (kx + hip[0]) / 2, (ky + hip[1]) / 2, L * 0.5, seed=205)
    c.set_source_rgba(*fem.dark[:3], 0.45)
    c.set_line_width(1.4)
    for k in range(7):  # herringbone muscle pattern
        f = (k + 1) / 8
        fx, fy = hip[0] + (kx - hip[0]) * f, hip[1] - 4 + (ky - hip[1]) * f
        c.move_to(fx - 5, fy - 7)
        c.line_to(fx + 5, fy + 3)
        c.stroke()
    footx = -122 - sh + (-250 + 122) * kick
    footy = -6 + 30 * kick
    st.limb(c, [(kx, ky), (footx, footy), (footx + 26 - 40 * kick, footy + 6 + 8 * kick)], 7, LEG)
    for k in range(4):  # tibia spines
        f = (k + 1) / 5
        px, py = kx + (footx - kx) * f, ky + (footy - ky) * f
        st.line(c, [(px, py), (px - 9, py - 2)], 2, DARK)
    if wet > 0:
        for k in range(4):
            dx, dy = -120 + k * 70, -40 + 10 * math.sin(k)
            ellipse(c, dx, dy + 12 * wet, 4, 6)
            c.set_source_rgba(0.75, 0.9, 1.0, 0.8 * wet)
            c.fill()
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()
