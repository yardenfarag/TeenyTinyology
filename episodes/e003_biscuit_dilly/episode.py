"""Episode 003 — Biscuit, Poppy & Dilly: the dog heartworm (Dirofilaria immitis).

Same bones as e001/e002: a Timeline of scenes whose starts and ends all come from the narration cues.
The magnifying-glass "lens" (the channel's own mark) is the device for anything too small to see.
Run:
    .venv/Scripts/python -m episodes.e003_biscuit_dilly.episode stills --style illustrated
    .venv/Scripts/python -m episodes.e003_biscuit_dilly.episode look            # look frames for the owner
    .venv/Scripts/python -m episodes.e003_biscuit_dilly.episode render --style illustrated
"""
import argparse
import math
import os
import random
import shutil

import cairo
import numpy as np

from characters import biscuit, dilly, poppy
from engine import backgrounds as bg
from engine import render
from engine import style as styles
from engine.audio import mix, music, sfx
from engine.audio.common import SR, Bus
from engine.core import TAU, Palette, back_out, clamp, ease, ease_out, ellipse, hexc, lerp, prog, window
from engine.scene import Timeline, label, leader, sparkles, tag
from engine.voice import narrate, sfx_events
from episodes.e002_roly_mango.episode import Cam, blinking, brand_plate, paint
from episodes.e003_biscuit_dilly.script import SCRIPT, SFX

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "003-biscuit-and-dilly"
INK = hexc("#3a2a1a")

# the dusk mosquito is a different one: browner than Poppy (mosquitoes live weeks; this is months later)
DUSK_MOSQ = Palette("#7a6852", "#ad9a80", "#4e4030", "#33281c")

# Biscuit's spot on the meadow path (world coords; the scene is drawn STAGE_LIFT higher on screen)
BX, BY = 430, 1400


def framed(z, fx, fy, sx=540.0, sy=1130.0, bg_h=None):
    """Cam showing world point (fx, fy) at (sx, sy), clamped so the frame never runs off the background.
    Scenes are drawn STAGE_LIFT higher, so the visible world band is y 170..2090 (sy defaults to its middle)."""
    bg_h = bg.HH if bg_h is None else bg_h
    z = max(1.0, z)
    wx = clamp(fx, sx / z, 1080 - (1080 - sx) / z)
    wy = clamp(fy, (sy - 170) / z, bg_h - (2090 - sy) / z)
    return Cam(z, wx, wy, sx, sy)


def lens(c, x, y, r, inner, a=1.0, t=0.0):
    """The channel's magnifying glass: a round window onto something tiny. inner(c) draws in world coords,
    clipped to the glass. The handle points down-left, away from the app's right rail."""
    if a <= 0:
        return
    from branding.banner import GOLD, NAVY
    k = back_out(min(1.0, a * 1.25))
    c.save()
    c.translate(x, y)
    c.scale(k, k)
    c.translate(-x, -y)
    c.push_group()
    hx, hy = x - r * 0.72, y + r * 0.72                        # handle
    c.move_to(hx, hy)
    c.line_to(hx - r * 0.42, hy + r * 0.42)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_source_rgba(*NAVY[:3], 1)
    c.set_line_width(r * 0.16)
    c.stroke()
    for dy, grow, al in ((10, 10, 0.08), (5, 5, 0.10)):           # soft shadow
        c.arc(x, y + dy, r + grow, 0, TAU)
        c.set_source_rgba(0.2, 0.1, 0.05, al)
        c.fill()
    c.save()
    c.arc(x, y, r, 0, TAU)
    c.clip()
    c.set_source_rgba(*hexc("#fbefe2"))
    c.paint()
    inner(c)
    g = cairo.RadialGradient(x - r * 0.4, y - r * 0.5, 0, x - r * 0.4, y - r * 0.5, r * 0.9)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.22)                    # glass glint
    g.add_color_stop_rgba(1, 1, 1, 1, 0)
    c.set_source(g)
    c.paint()
    c.restore()
    c.arc(x, y, r, 0, TAU)
    c.set_source_rgba(*GOLD[:3], 1)
    c.set_line_width(r * 0.09)
    c.stroke()
    c.arc(x, y, r * 0.955, 0, TAU)
    c.set_source_rgba(1, 0.97, 0.9, 0.7)
    c.set_line_width(3)
    c.stroke()
    c.pop_group_to_source()
    c.paint_with_alpha(min(1.0, a * 1.5))
    c.restore()


def along(poly, head_d, length, n=60):
    """Points of a worm lying on a polyline: head at arc-length head_d, body trailing `length` behind it."""
    seg = [math.dist(p, q) for p, q in zip(poly, poly[1:])]

    def at(d):
        d = max(0.0, d)
        for (p, q), L in zip(zip(poly, poly[1:]), seg):
            if d <= L or L == seg[-1] and (p, q) == (poly[-2], poly[-1]):
                f = d / L if L else 0.0
                return lerp(p[0], q[0], min(f, 1.0)), lerp(p[1], q[1], min(f, 1.0))
            d -= L
        return poly[-1]

    return [at(head_d - length * k / (n - 1)) for k in range(n)]


def poly_len(poly):
    return sum(math.dist(p, q) for p, q in zip(poly, poly[1:]))


def evening(c, k):
    """Warm late-afternoon light (multiply, never a grey dim — docs/judge-lessons.md)."""
    if k <= 0:
        return
    c.save()
    c.set_operator(cairo.OPERATOR_MULTIPLY)
    c.set_source_rgba(1.0, lerp(1.0, 0.78, k), lerp(1.0, 0.62, k), 1.0)
    c.paint()
    c.restore()


def proboscis_rod(c, x0, y0, x1, y1, w=16):
    """A mosquito's mouthparts seen up close: a long slate tube with a pale tip."""
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for col, ww in ((poppy.BODY.line, w + 5), (poppy.BODY.dark, w), (poppy.BODY.light, w * 0.3)):
        c.move_to(x0, y0)
        c.line_to(x1, y1)
        c.set_source_rgba(*col)
        c.set_line_width(ww)
        c.stroke()


# ================================================================ build
def build(style_name):
    st = styles.get(style_name)
    TEASER = 1.5
    track, Q, caps, end = narrate(SCRIPT, os.path.join(HERE, "voice_cache"), t0=TEASER + 0.15)
    DUR = end + 4.9                      # end card fully readable >= 4 s (judge lessons)
    tl = Timeline(DUR, captions=caps)
    ctx = {"style": st, "vignette": bg.vignette(), "watermark": True, "fade_in": 0.0}
    q = Q

    def meadow(c, t, warm=0.0):
        paint(c, bg.meadow())
        bg.sunrays(c, t, a=0.10 * (1 - warm))

    def biscuit_nap(c, t, s=1.0, x=BX, y=BY):
        biscuit.draw_curled(c, st, x, y, s, eyes=0.0, breathe=math.sin(t * 1.6), tail=t, ear=0.4 * math.sin(t * 0.7) ** 9)

    def poppy_on_back(x, y, s_dog, s_p):
        """Where Poppy's thorax goes so her feet stand on the curled Biscuit's back."""
        px, py = biscuit.to_world(x, y, s_dog, *biscuit.CURL_SKIN_SPOT)
        return px, py - poppy.FEET_Y * s_p

    # ---------------------------------------------------------- 0. teaser (frame 0 is the thumbnail)
    def s_teaser(c, t, ctx):
        cam = framed(lerp(1.0, 1.10, ease(prog(t, 0.0, q["biscuit"].start))), 520, 1250)
        c.save()
        cam.apply(c)
        meadow(c, t)
        biscuit_nap(c, t, 0.82, 300, 1420)
        poppy.draw(c, st, 740 + 40 * math.sin(t * 0.9), 1150 + 14 * math.sin(t * 2.2), 0.95, fly=1.0, phase=t,
                   blink=blinking(t, 0.6))
        c.restore()

        def worm(cc):
            cc.save()
            cc.translate(480, 800)
            dilly.draw_along(cc, st, dilly.wiggle_points(150, -10, 330, t, amp=34, waves=1.4), 30,
                             blink=blinking(t, 1.2), happy=0.6)
            cc.restore()

        lens(c, 480, 800, 215, worm, 1.0)
        fade = 1 - ease(prog(t, q["hook"].end, q["biscuit"].start))
        label(c, "This worm grows up inside", 540, 430, fade, size=52)   # x 540: clear of the badge
        label(c, "a dog AND a mosquito", 540, 520, fade, size=52)

    tl.add(s_teaser, 0.0, q["biscuit"].start, trans_dur=0.3)

    # ---------------------------------------------------------- 1. meet Biscuit
    def s_biscuit(c, t, ctx):
        k = ease(prog(t, q["biscuit"].start, q["poppy"].start + 0.5))
        cam = framed(lerp(1.0, 1.22, k), BX, 1260)
        c.save()
        cam.apply(c)
        meadow(c, t)
        biscuit_nap(c, t)
        c.restore()
        hx, hy = cam.screen(BX - 10, BY - 210)
        tag(c, "Biscuit", hx, hy, window(t, q["biscuit"].word("Biscuit"), q["poppy"].start, 0.3, 0.3), sub="a dog")

    tl.add(s_biscuit, q["biscuit"].start, q["poppy"].start)

    # ---------------------------------------------------------- 2. meet Poppy
    def poppy_path(t):
        k = ease_out(prog(t, q["poppy"].start - 0.3, q["poppy"].start + 1.8))
        x = lerp(1180, 620, k) + 20 * math.sin(t * 1.3)
        y = lerp(620, 900, k) + 26 * math.sin(t * 2.1)
        return x, y

    def s_poppy(c, t, ctx):
        k = ease(prog(t, q["poppy"].start, q["dilly"].start))
        cam = framed(lerp(1.0, 1.18, k), 560, 1100)
        c.save()
        cam.apply(c)
        meadow(c, t)
        biscuit_nap(c, t)
        px, py = poppy_path(t)
        poppy.draw(c, st, px, py, 1.5, fly=1.0, phase=t, blink=blinking(t, 0.4), happy=0.4)
        c.restore()
        sx, sy = cam.screen(px - 10, py - 90)
        tag(c, "Poppy", sx, sy, window(t, q["poppy"].word("Poppy"), q["dilly"].start, 0.3, 0.3), sub="a mosquito")
        a = window(t, q["poppy"].word("eggs"), q["dilly"].start, 0.3, 0.3)
        if a > 0:                       # her eggs, the reason she needs blood
            ex, ey = cam.screen(px - 140, py + 150)
            for i in range(5):
                ellipse(c, ex + i * 22 - 44, ey + 6 * (i % 2), 9 * back_out(min(1, a * 1.3)), 15 * back_out(min(1, a * 1.3)), 0.3)
                c.set_source_rgba(0.98, 0.95, 0.86, a)
                c.fill_preserve()
                c.set_source_rgba(0.55, 0.45, 0.32, a)
                c.set_line_width(2)
                c.stroke()

    tl.add(s_poppy, q["poppy"].start, q["dilly"].start)

    # ---------------------------------------------------------- 3. who Poppy is carrying
    def s_dilly(c, t, ctx):
        k = ease(prog(t, q["dilly"].start, q["past"].start))
        meadow(c, t)
        px, py = 360 + 14 * math.sin(t * 1.3), 1110 + 18 * math.sin(t * 2.1)
        s_p = lerp(2.3, 2.5, k)
        poppy.draw(c, st, px, py, s_p, fly=1.0, phase=t, blink=blinking(t, 0.4), happy=0.3)
        base = (px + poppy.PROB_BASE[0] * s_p, py + poppy.PROB_BASE[1] * s_p)
        a = ease(prog(t, q["dilly"].start + 0.2, q["dilly"].start + 0.9))

        def inner(cc):
            proboscis_rod(cc, 330, 330, 820, 820, w=120)
            cc.save()
            cc.translate(560, 560)
            cc.rotate(math.pi / 4)
            dilly.draw_along(cc, st, dilly.wiggle_points(110, 0, 230, t, amp=10, waves=1.2), 26,
                             blink=blinking(t, 2.0), happy=0.5)
            cc.restore()

        lx, ly, lr = 650, 700, 185
        leader(c, lx - lr * 0.45, ly + lr * 0.9, base[0] + 30, base[1] + 20, a, col=(1, 0.97, 0.9))

        def inner_at(cc):
            cc.save()
            cc.translate(lx - 560, ly - 560)
            inner(cc)
            cc.restore()

        lens(c, lx, ly, lr, inner_at, a)
        tag(c, "Dilly", lx, ly - lr - 10, window(t, q["dilly"].word("Dilly"), q["past"].start, 0.3, 0.3),
            sub="a dog heartworm")

    tl.add(s_dilly, q["dilly"].start, q["past"].start)

    # ---------------------------------------------------------- 4. flashback: a baby in another dog's blood
    def s_past(c, t, ctx):
        cam = framed(lerp(1.0, 1.10, ease(prog(t, q["past"].start, q["grow"].start))), 540, 1000)
        c.save()
        cam.apply(c)
        paint(c, bg.vessel())
        bg.blood_cells(c, t, n=110, speed=120, rad=(7, 10))
        w_sip = q["past"].word("sipped")
        up = ease(prog(t, w_sip + 0.1, q["past"].end + 0.4))
        dx, dy = 540 + 60 * math.sin(t * 0.7), lerp(1000, 560, up)
        rr = random.Random(5)
        for i in range(5):                                       # her siblings, drifting by
            dilly.draw_microfilaria(c, st, (rr.uniform(0, 1080) + 90 * t) % 1180 - 50, rr.uniform(650, 1400),
                                    3.2, t + i, ang=rr.uniform(-0.3, 0.3), alpha=0.8)
        dn = ease(prog(t, w_sip - 0.6, w_sip))                   # the mouthparts come down, then rise with her
        tip_y = lerp(380, 900, dn) - lerp(0, 340, up)
        proboscis_rod(c, 540, -100, 540, tip_y, w=30)
        dilly.draw_microfilaria(c, st, dx if up == 0 else 540, dy if up > 0 else 1000, 5.0,
                                t, ang=-math.pi / 2 * up, face=True)
        c.restore()
        label(c, "two weeks earlier · another dog", 480, 1420,
              window(t, q["past"].start + 0.2, q["grow"].start, 0.3, 0.3), size=40)

    tl.add(s_past, q["past"].start, q["grow"].start)

    # ---------------------------------------------------------- 5. growing inside Poppy, then to her mouthparts
    def s_grow(c, t, ctx):
        meadow(c, t)
        c.set_source_rgba(1, 0.98, 0.94, 0.35)                   # a soft "look inside" wash, not a dim
        c.paint()
        s_p = 2.4
        px, py = 470 + 10 * math.sin(t * 1.1), 980 + 14 * math.sin(t * 1.9)
        poppy.draw(c, st, px, py, s_p, fly=1.0, phase=t, blink=blinking(t, 0.4))
        g = ease(prog(t, q["grow"].start, q["grow"].word("weeks") + 0.6))
        mv = ease(prog(t, q["grow"].word("crawled") - 0.2, q["grow"].end + 0.4))
        # judge pass 1: a straight move carried her out through Poppy's face. Now she runs along the body, under
        # the head, to the base of the proboscis and a third of the way down it.
        pa = poppy._prob_angle(0.0)
        route = [(-170, 16), (-100, 12), (-30, 8), (14, 12), poppy.PROB_BASE,
                 (poppy.PROB_BASE[0] + math.cos(pa) * poppy.PROB_LEN * 0.4,
                  poppy.PROB_BASE[1] + math.sin(pa) * poppy.PROB_LEN * 0.4)]
        route = [(px + x * s_p, py + y * s_p) for x, y in route]
        L = lerp(90, 170, g)
        head = lerp(poly_len(route[:2]), poly_len(route), mv)
        pts = along(route, head, L, n=50)
        pts = [(x, y + 5 * math.sin(t * 5 + i * 0.4) * (1 - mv)) for i, (x, y) in enumerate(pts)]
        wx, wy = pts[len(pts) // 3]
        glow = cairo.RadialGradient(wx, wy, 0, wx, wy, 150)
        glow.add_color_stop_rgba(0, 1, 0.97, 0.9, 0.72)
        glow.add_color_stop_rgba(0.55, 1, 0.97, 0.9, 0.45)
        glow.add_color_stop_rgba(1, 1, 0.98, 0.92, 0)
        c.arc(wx, wy, 150, 0, TAU)
        c.set_source(glow)
        c.fill()
        dilly.draw_along(c, st, pts, lerp(10, 16, g) * (1 - 0.3 * mv), face=g > 0.5, blink=blinking(t, 1.3))
        label(c, "only while the weather is warm", 480, 1420,
              window(t, q["grow"].word("weeks") - 0.4, q["grow"].word("mouthparts"), 0.3, 0.3), size=40)
        am = window(t, q["grow"].word("mouthparts"), q["grow"].end + 0.6, 0.3, 0.3)
        label(c, "the mouthparts", 330, 620, am, size=40)
        mx_, my_ = route[-1]
        leader(c, 330, 660, mx_ + 20, my_ + 10, am, col=(1, 0.97, 0.9))

    tl.add(s_grow, q["grow"].start, q["bite"].start - 0.5)

    # ---------------------------------------------------------- 6. she lands on Biscuit (the bite: sound only)
    def s_land(c, t, ctx):
        k = ease(prog(t, q["bite"].start - 0.5, q["drop"].start))
        cam = framed(lerp(1.15, 1.6, k), BX - 120, 1220)
        c.save()
        cam.apply(c)
        meadow(c, t)
        biscuit_nap(c, t)
        s_p = 0.7
        lx, ly = poppy_on_back(BX, BY, 1.0, s_p)
        land = ease_out(prog(t, q["bite"].start - 0.5, q["bite"].start + 0.35))
        probe = ease(prog(t, q["bite"].start + 0.35, q["bite"].start + 0.75))
        x = lerp(lx + 260, lx, land)
        y = lerp(ly - 300, ly, land)
        poppy.draw(c, st, x, y, s_p, fly=1.0 - land, phase=t, probe=probe, blink=blinking(t, 0.4))
        c.restore()

    tl.add(s_land, q["bite"].start - 0.5, q["drop"].start)

    # ---------------------------------------------------------- 7. the bite, close up — one step at a time
    # Owner: the first version was unclear (a huge Poppy and busy fur). Now: a clean cut through the skin, only
    # her head and mouthparts, and each step on its own word — mouthparts in, a drop, Dilly in the drop,
    # mouthparts out, Dilly into the hole (AHS: larvae burst out in a drop of haemolymph on the skin, then
    # enter through the puncture wound).
    SURF = bg.CLOSE_Y
    HOLE = (430, SURF)
    HEAD = (760, 560)
    ROD_DIR = (HOLE[0] - (HEAD[0] - 40), HOLE[1] - (HEAD[1] + 50))
    ROD_LEN = math.hypot(*ROD_DIR)
    ROD_U = (ROD_DIR[0] / ROD_LEN, ROD_DIR[1] / ROD_LEN)

    def s_drop(c, t, ctx):
        w_drop, w_wrig = q["drop"].word("drop"), q["drop"].word("wriggles")
        cam = framed(lerp(1.40, 1.50, ease(prog(t, q["drop"].start, q["walk"].start))), 520, 880, 540, 960)
        c.save()
        cam.apply(c)
        paint(c, bg.skin_closeup())
        out = ease(prog(t, w_wrig - 0.5, w_wrig + 0.2))         # the mouthparts pull back out
        back = 230 * out + 16 * math.sin(t * 5.0) * (1 - out)   # probing while she drinks
        bx0, by0 = HEAD[0] - 40 - ROD_U[0] * back, HEAD[1] + 50 - ROD_U[1] * back
        tipx, tipy = HOLE[0] + ROD_U[0] * (110 - back), HOLE[1] + ROD_U[1] * (110 - back)
        # the puncture: a fine track through the outer skin, left behind when she pulls out
        if out > 0:
            c.move_to(HOLE[0], HOLE[1] - 2)
            c.line_to(HOLE[0] + ROD_U[0] * 110, HOLE[1] + ROD_U[1] * 110)
            c.set_source_rgba(0.62, 0.22, 0.24, 0.55 * out)
            c.set_line_width(10)
            c.set_line_cap(cairo.LINE_CAP_ROUND)
            c.stroke()
            ellipse(c, HOLE[0], HOLE[1] + 1, 18, 7, 0.0)
            c.set_source_rgba(0.55, 0.2, 0.2, 0.7 * out)
            c.fill()
        # inside the skin: the thin piercing stylets (seen through the cut)
        if back < 110:
            proboscis_rod(c, HOLE[0], HOLE[1], tipx, tipy, w=12)
        # the sheath (above the skin), with a see-through window while Dilly is still inside it
        sx1, sy1 = HOLE[0] - ROD_U[0] * back, HOLE[1] - ROD_U[1] * back
        proboscis_rod(c, bx0, by0, sx1, sy1, w=40)
        w_spill = q["drop"].word("spills")
        win = 1 - ease(prog(t, w_drop - 0.2, w_drop + 0.4))
        if win > 0:
            c.move_to(HOLE[0] - ROD_U[0] * 360, HOLE[1] - ROD_U[1] * 360)
            c.line_to(HOLE[0] - ROD_U[0] * 14, HOLE[1] - ROD_U[1] * 14)
            c.set_source_rgba(1, 0.97, 0.92, 0.55 * win)
            c.set_line_width(30)
            c.set_line_cap(cairo.LINE_CAP_ROUND)
            c.stroke()
        # Dilly: down inside the sheath, out of its very tip (Merck: "erupt through the tip of the labium"),
        # into the drop, then down into the hole
        P = [(HOLE[0] - ROD_U[0] * 340, HOLE[1] - ROD_U[1] * 340), (HOLE[0] - ROD_U[0] * 16, HOLE[1] - ROD_U[1] * 16),
             (HOLE[0] + 40, SURF - 28), (HOLE[0] + 130, SURF - 48), (HOLE[0] + 210, SURF - 46),
             (HOLE[0] + 120, SURF - 34), (HOLE[0] + 14, SURF - 8), (HOLE[0], SURF + 40), (HOLE[0] - 20, SURF + 120),
             (HOLE[0] - 60, SURF + 175)]
        L = 200
        d1, d_drop = poly_len(P[:2]), poly_len(P[:5])
        k0 = ease(prog(t, q["drop"].start, w_spill))
        k1 = ease(prog(t, w_spill, w_drop + 0.3))
        k2 = ease(prog(t, w_wrig - 0.1, q["drop"].end + 0.7))
        head = L + (d1 - L) * k0 + (d_drop - d1) * k1 + (poly_len(P) - d_drop) * k2
        pts = along(P, head, L, n=80)
        inside = k1 == 0
        pts = [(x + (0 if inside else 6 * math.sin(t * 5.5 + i * 0.3)),
                y + (3 * math.sin(t * 4 + i * 0.4) if 0 < k1 and k2 == 0 else 0)) for i, (x, y) in enumerate(pts)]
        dilly.draw_along(c, st, pts, 18 if inside else 20, blink=blinking(t, 1.1), happy=0.5)
        hx, hy = HEAD[0] - ROD_U[0] * back * 0.6, HEAD[1] - ROD_U[1] * back * 0.6 + 6 * math.sin(t * 2.6)
        for k, (ax, ay) in enumerate(((150, -170), (110, -200))):
            st.line(c, [(hx + 20, hy - 50), (hx + ax * 0.5, hy + ay * 0.55), (hx + ax, hy + ay)], 5, poppy.BODY.dark,
                    0.85 if k == 0 else 0.55)
        st.ellipse(c, hx, hy, 92, 84, 0.0, poppy.BODY, seed=311)
        st.eye(c, hx - 10, hy - 10, 30, 0.1 if blinking(t, 0.4) else 1.0)
        st.blush(c, hx - 34, hy + 34, 16, 0.5)
        st.smile(c, hx - 50, hy + 30, 26, poppy.BAND, 1.4)
        # the drop of her own fluid, sitting on the skin (drawn over Dilly: she is inside it)
        da = ease(prog(t, w_drop - 0.6, w_drop + 0.2)) * (1 - 0.6 * ease(prog(t, w_wrig + 0.6, q["drop"].end + 1.2)))
        if da > 0:
            cx, cy, rx, ry = HOLE[0] + 130, SURF, 175 * da, 82 * da
            c.save()
            c.move_to(cx - rx, cy)
            c.save()
            c.translate(cx, cy)
            c.scale(rx, ry)
            c.arc(0, 0, 1, math.pi, TAU)
            c.restore()
            c.close_path()
            c.set_source_rgba(0.92, 0.96, 1.0, 0.42)
            c.fill_preserve()
            c.set_source_rgba(0.55, 0.66, 0.78, 0.75)
            c.set_line_width(4)
            c.stroke()
            ellipse(c, cx - rx * 0.35, cy - ry * 0.62, rx * 0.25, ry * 0.12, -0.2)
            c.set_source_rgba(1, 1, 1, 0.75)
            c.fill()
            c.restore()
        c.restore()
        a1 = window(t, q["drop"].start + 0.15, w_drop - 0.4, 0.3, 0.3)
        label(c, "Poppy's mouthparts", 330, 640, a1, size=42)
        leader(c, 330, 680, *cam.screen(HOLE[0] + 150, SURF - 230), a1, col=(1, 0.97, 0.9))
        a2 = window(t, w_drop - 0.5, w_wrig + 0.5, 0.3, 0.25)
        label(c, "a drop of Poppy's own fluid", 400, 1440, a2, size=42)
        leader(c, 400, 1400, *cam.screen(HOLE[0] + 170, SURF - 10), a2, col=(1, 0.97, 0.9))
        a3 = window(t, w_wrig + 0.75, q["walk"].start + 0.2, 0.3, 0.3)
        label(c, "the bite hole", 260, 1440, a3, size=42)
        leader(c, 260, 1400, *cam.screen(HOLE[0] - 4, SURF + 10), a3, col=(1, 0.97, 0.9))

    tl.add(s_drop, q["drop"].start, q["walk"].start, transition="iris",
           iris_center=lambda t: (410, 1036))

    # ---------------------------------------------------------- 8. the long walk under the skin
    # in skin_section() coordinates: just under the skin, through the dermis and the top of the fat, always
    # above the vein: she must not look as if she were already in the blood before "slips into a blood vessel"
    WALK = [(560, 610), (500, 700), (420, 790), (350, 880), (400, 960), (560, 1000), (740, 985), (860, 935)]
    SK0, SK1 = -120, -80          # the shot pans down a little; the ride shot continues from SK1

    WALK_Z = 1.3

    def follow(pts, ty):
        """A camera on the middle of her body (smoother than the head), in the shifted skin's coordinates."""
        mx, my = pts[len(pts) // 2]
        return framed(WALK_Z, mx, my + ty, bg_h=bg.SKIN_H + ty)

    def s_walk(c, t, ctx):
        k = ease(prog(t, q["walk"].start, q["ride"].start))
        ty = lerp(SK0, SK1, k)
        w_molt = q["walk"].word("molts")
        go = ease(prog(t, w_molt + 0.5, q["ride"].start))
        L = 160
        head = lerp(L, poly_len(WALK), go)
        pts = along(WALK, head, L)
        pts = [(x + 6 * math.sin(t * 5 + i * 0.35), y + 4 * math.cos(t * 4 + i * 0.3)) for i, (x, y) in enumerate(pts)]
        cam = follow(along(WALK, head, L), ty)
        c.save()
        cam.apply(c)
        c.translate(0, ty)
        paint(c, bg.skin_section())
        shed = prog(t, w_molt, w_molt + 3.5)
        if 0 < shed < 1:                                         # the old skin, left behind (clearly visible)
            dilly.draw_along(c, st, along(WALK, L, L), 17, alpha=0.75 * (1 - shed ** 2), face=False)
        sparkles(c, pts[0][0], pts[0][1], t, w_molt, n=8, r=80)
        dilly.draw_along(c, st, pts, 16, blink=blinking(t, 0.9), happy=0.3)
        c.restore()
        day = int(lerp(3, 55, prog(t, w_molt, q["ride"].start)))
        label(c, f"day {day}", 480, 430, window(t, w_molt - 0.2, q["ride"].start + 0.2, 0.3, 0.2), size=46)
        label(c, "a molt: she sheds her old skin", 480, 1420,
              window(t, w_molt, w_molt + 2.2, 0.3, 0.3), size=38)

    tl.add(s_walk, q["walk"].start, q["ride"].start, transition="cut")

    # ---------------------------------------------------------- 9. the last molt, into a vein, carried away
    def s_ride_in(c, t, ctx):
        vy = bg.VEIN_Y
        w_molt, w_slip = q["ride"].word("molt"), q["ride"].word("slips")
        grow = ease(prog(t, w_molt, w_molt + 0.6))
        go = ease(prog(t, w_slip - 0.2, q["ride"].word("carries") + 0.2))
        path = WALK[-4:] + [(640, 1030), (600, vy), (760, vy + 6), (1000, vy - 4), (1300, vy - 8)]
        L = lerp(160, 210, grow)
        head = lerp(poly_len(WALK[-4:]), poly_len(path) - 40, go)
        pts = along(path, head, L)
        pts = [(x + 5 * math.sin(t * 5 + i * 0.35), y) for i, (x, y) in enumerate(pts)]
        cam = follow(along(path, head, L), SK1)
        c.save()
        cam.apply(c)
        c.translate(0, SK1)
        paint(c, bg.skin_section())
        sparkles(c, pts[0][0], pts[0][1], t, w_molt, n=9, r=90)
        dilly.draw_along(c, st, pts, lerp(16, 20, grow), blink=blinking(t, 0.9), happy=0.4)
        c.restore()
        hx, hy = cam.screen(pts[0][0], pts[0][1] + SK1)
        tag(c, "a young worm now", hx - 40, hy - 40, window(t, w_molt + 0.2, q["ride"].word("carries"), 0.3, 0.3))
        vx, vys = cam.screen(380, vy + SK1 + 30)
        tag(c, "a vein", vx, vys, window(t, w_slip - 0.3, q["ride"].word("carries"), 0.3, 0.3))

    tl.add(s_ride_in, q["ride"].start, q["ride"].word("carries") - 0.1, transition="cut")

    def s_ride(c, t, ctx):
        paint(c, bg.vessel())
        bg.blood_cells(c, t, n=90, speed=420, rad=(3, 5))
        t0 = q["ride"].word("carries") - 0.1
        hx = lerp(560, 880, ease(prog(t, t0, q["turn"].start)))
        pts = dilly.wiggle_points(hx, 1000 + 30 * math.sin(t * 1.4), 720, t, amp=30, waves=1.8, speed=6.0)
        dilly.draw_along(c, st, pts, 18, blink=blinking(t, 0.7), happy=0.8)
        ha = ease(prog(t, q["ride"].word("heart") - 0.6, q["ride"].word("heart") + 0.2))
        if ha > 0:                                               # the heart ahead, beating
            beat = 1 + 0.08 * max(0.0, math.sin(t * 7)) ** 4
            c.save()
            c.translate(840, 1000)
            c.scale(beat * ha, beat * ha)
            g = cairo.RadialGradient(0, 0, 10, 0, 0, 330)
            g.add_color_stop_rgba(0, 0.85, 0.22, 0.28, 0.75)
            g.add_color_stop_rgba(1, 0.85, 0.22, 0.28, 0)
            c.arc(0, 0, 330, 0, TAU)
            c.set_source(g)
            c.fill()
            c.restore()
        label(c, "about 3 months after the bite", 480, 560,
              window(t, q["ride"].word("heart") - 0.3, q["turn"].start + 0.6, 0.3, 0.3), size=42)

    tl.add(s_ride, q["ride"].word("carries") - 0.1, q["turn"].start)

    # ---------------------------------------------------------- 10. through the heart, into the lung arteries
    CH_S = 1.25
    CH_X, CH_Y = 360, 1420
    HX_, HY_ = biscuit.HEART_C
    IN_HEART = [(HX_ - 18, HY_ + 22), (HX_ - 4, HY_ + 26), (HX_ + 12, HY_ + 12), (HX_ + 10, HY_ - 8), (HX_, HY_ - 18)]
    path_local = IN_HEART + biscuit.ARTERY[:4] + biscuit.BRANCHES[0][1:]

    def s_home(c, t, ctx):
        k = ease(prog(t, q["turn"].start, q["long"].start))
        fx, fy = biscuit.to_world(CH_X, CH_Y, CH_S, 40, -125)
        cam = framed(lerp(2.5, 2.9, k), fx, fy, 470, 930)
        w_stop, w_art = q["turn"].word("stop"), q["home"].word("arteries")
        stay = ease(prog(t, q["turn"].start - 0.2, w_stop + 0.2))     # in the heart: seen, wriggling
        go = ease(prog(t, q["turn"].word("way") - 0.1, w_art + 0.6))
        total = poly_len(path_local)
        d_in = poly_len(IN_HEART)
        head = lerp(30, d_in, stay) + (total - 4 - d_in) * go

        def worms(cc):
            pts = along(path_local, head, 44, n=40)
            pts = [(x + 1.2 * math.sin(t * 6 + i * 0.5), y) for i, (x, y) in enumerate(pts)]
            cc.save()
            dilly.draw_along(cc, st, pts, 9, face=False)
            cc.restore()

        c.save()
        cam.apply(c)
        meadow(c, t)
        biscuit.draw(c, st, CH_X, CH_Y, CH_S, eyes=0.0 if blinking(t, 0.3) else 1.0, head=1.0, tail=t * 2,
                     wag=0.3, breathe=math.sin(t * 1.6),
                     xray=lambda cc: biscuit.draw_chest(cc, st, t, worms), xray_alpha=1.0)
        c.restore()
        hx, hy = cam.screen(*biscuit.to_world(CH_X, CH_Y, CH_S, *biscuit.HEART_C))
        tag(c, "heart", hx + 75 * cam.z / 2.5, hy - 5, window(t, q["turn"].word("heart"), q["home"].start + 0.4, 0.3, 0.3))
        ax, ay = cam.screen(*biscuit.to_world(CH_X, CH_Y, CH_S, 0, -170))
        tag(c, "the lung arteries", ax, ay - 20, window(t, w_art, q["long"].start, 0.3, 0.3),
            sub="where most heartworms live")
        label(c, "about 3 months after the bite", 480, 560,
              window(t, q["turn"].start - 0.5, q["turn"].start + 1.4, 0.3, 0.3), size=42)

    tl.add(s_home, q["turn"].start, q["long"].start)

    # ---------------------------------------------------------- 11-13. grown up in the artery: long, a mate, babies
    snake = []
    for k in range(400):
        u = k / 399
        snake.append((470 + 300 * math.sin(u * 3.3 * math.pi) * (0.9 + 0.1 * u), 640 + 620 * u))

    # the male: head at the right, along the top run, a gentle U-turn on the left, back along the bottom run to his
    # coil (~60% of her length: Merck 15 vs 25 cm, Wikipedia 23 vs 30)
    male_path = ([(720 - 530 * k / 59, 1225) for k in range(60)] +
                 [(190 - 60 * math.sin(math.pi * k / 19), 1225 + 125 * (1 - math.cos(math.pi * k / 19)) / 2)
                  for k in range(1, 20)] +
                 [(190 + 450 * k / 59, 1350) for k in range(1, 60)])

    def s_artery(c, t, ctx):
        # a slow push-in across the stay, panning to her head end where the babies leave (motion + judge pass 2)
        kz = ease(prog(t, q["long"].start, q["need"].start))
        kb = ease(prog(t, q["babies"].start - 0.5, q["babies"].word("Tiny")))
        cam = framed(lerp(1.0, 1.28, kz), lerp(500, 480, kb), lerp(1080, 960, kb))
        c.save()
        cam.apply(c)
        paint(c, bg.vessel(tint="#eeaea4"))
        bg.blood_cells(c, t, n=110, speed=110, a=0.85, rad=(2.5, 4))
        g = ease(prog(t, q["long"].start, q["long"].word("long") + 0.4))
        L = lerp(260, poly_len(snake) * 0.98, g)
        # she grows from the bottom up, so her head (pts[0]) ends at the TOP of the S, far from the male and the
        # captions; the babies leave from there and the camera pans up to it
        pts = along(snake[::-1], L, L, n=320)
        pts = [(x + 14 * math.sin(t * 2.2 - i * 0.05), y + 6 * math.cos(t * 1.7 - i * 0.04))   # a slow ripple
               for i, (x, y) in enumerate(pts)]
        # the male first, so he lies BEHIND her and can never cover her face (judge pass 2)
        mk = ease_out(prog(t, q["male"].start - 0.2, q["male"].word("male") + 0.4))
        coil = None
        if mk > 0:
            dx = lerp(900, 0, mk)
            mpts = [(x + dx, y + 8 * math.sin(i * 0.12 + 0.2 * t)) for i, (x, y) in enumerate(male_path)]
            dilly.draw_along(c, st, mpts, 16, male=True, blink=blinking(t, 1.9), happy=0.5)
            coil = (mpts[-1][0] + 45, mpts[-1][1])
        dilly.draw_along(c, st, pts, lerp(16, 24, g), blink=blinking(t, 0.8), happy=0.6)
        # babies, set loose into the blood near her head end
        w_bab = q["babies"].word("babies")
        if t > w_bab - 0.3:
            rr = random.Random(11)
            hx, hy = pts[0]
            for i in range(40):
                born = w_bab - 0.3 + i * 0.06
                kk = t - born
                if kk < 0:
                    continue
                d = 50 + kk * rr.uniform(55, 110)
                ang = rr.uniform(-0.5, 1.5)                      # down and along the flow, inside the blood
                x = hx + math.cos(ang) * d + kk * 45
                y = max(600.0, hy + math.sin(ang) * d * 0.9)
                dilly.draw_microfilaria(c, st, x, y, 0.85, t + i, ang=rr.uniform(-0.4, 0.4), face=False,
                                        alpha=min(1.0, kk * 3))
        c.restore()
        # labels in screen space, after the camera (inside it they grew and drifted past the safe line)
        label(c, "up to 30 cm (1 ft)", 480, 470, window(t, q["long"].word("thirty"), q["male"].start + 0.3, 0.3, 0.3),
              size=44)
        if coil:
            cx_, cy_ = cam.screen(*coil)
            tag(c, "a male", min(cx_, 760), cy_ - 30, window(t, q["male"].word("male"), q["babies"].start + 0.3, 0.3, 0.3),
                sub="corkscrew tail")
        label(c, "6 months or more after the bite", 480, 570,
              window(t, q["babies"].start - 0.1, q["babies"].word("Tiny") - 0.1, 0.3, 0.25), size=42)
        label(c, "microfilariae: the babies' name", 480, 570,
              window(t, q["babies"].word("Tiny") + 0.1, q["need"].start + 0.2, 0.3, 0.3), size=40)

    tl.add(s_artery, q["long"].start, q["need"].start, transition="iris", iris_center=lambda t: (470, 760))

    # ---------------------------------------------------------- 14. stuck: they can't grow up in Biscuit
    def s_need(c, t, ctx):
        cam = framed(lerp(1.0, 1.14, ease(prog(t, q["need"].start, q["again"].start))), BX, 1250)
        c.save()
        cam.apply(c)
        meadow(c, t)
        biscuit.draw(c, st, BX - 30, BY, 1.05, eyes=0.0 if blinking(t, 0.2) else 1.0, head=1.0, tail=t * 2.2,
                     wag=0.6, happy=0.8, breathe=math.sin(t * 1.6))
        c.restore()

        def inner(cc):
            cc.save()
            cc.translate(480 - 540, 690 - 1000)
            cc.set_source_surface(bg.vessel(), 0, 0)
            cc.paint()
            bg.blood_cells(cc, t, n=90, speed=120, rad=(6, 8))
            rr = random.Random(3)
            for i in range(6):
                dilly.draw_microfilaria(cc, st, (rr.uniform(0, 1080) + 70 * t) % 900 + 90, rr.uniform(820, 1180),
                                        2.6, t + i, ang=rr.uniform(-0.4, 0.4), face=True)
            cc.restore()

        a = ease(prog(t, q["need"].start, q["need"].start + 0.5))
        bxw, byw = cam.screen(*biscuit.to_world(BX - 30, BY, 1.05, 20, -170))
        leader(c, 480, 690 + 220, bxw, byw, a, col=(1, 0.97, 0.9))
        lens(c, 480, 690, 220, inner, a)
        ma = window(t, q["need"].word("mosquito") - 0.1, q["again"].start + 0.4, 0.3, 0.3)
        if ma > 0:
            poppy.draw(c, st, 800, 520 + 10 * math.sin(t * 2), 0.6, fly=1.0, phase=t, alpha=0.45 * ma)

    tl.add(s_need, q["need"].start, q["again"].start)

    # ---------------------------------------------------------- 15. evening: a mosquito comes for a sip
    def s_again(c, t, ctx):
        warm = ease(prog(t, q["again"].start - 0.4, q["again"].start + 1.2))
        b = q["button"]
        cam = framed(lerp(1.0, 1.12, ease(prog(t, q["again"].start, b.end))), BX + 60, 1180)
        c.save()
        cam.apply(c)
        meadow(c, t, warm)
        biscuit.draw_curled(c, st, BX, BY, 1.0, eyes=0.0, breathe=math.sin(t * 1.6), tail=t,
                            ear=0.8 if 0 < t - b.word("dog") < 0.5 else 0.4 * math.sin(t * 0.7) ** 9)
        s_p = 0.8
        lx, ly = poppy_on_back(BX, BY, 1.0, s_p)
        w_sip, w_jrn = q["again"].word("sip"), q["again"].word("journey")
        land = ease_out(prog(t, q["again"].start, w_sip - 0.2))
        probe = ease(prog(t, w_sip - 0.3, w_sip + 0.2)) * (1 - ease(prog(t, w_jrn - 0.3, w_jrn + 0.1)))
        fed = ease(prog(t, w_sip, w_sip + 1.6))
        off = ease(prog(t, w_jrn - 0.2, b.start + 0.4))        # "the journey begins again": she flies off, full
        x = lerp(lerp(lx + 420, lx, land), 760, off)
        y = lerp(lerp(ly - 380, ly, land), 610, off) + 14 * math.sin(t * 2.2) * off
        poppy.draw(c, st, x, y, s_p, fly=max(1.0 - land, off), phase=t, probe=probe, fed=fed,
                   blink=blinking(t, 0.4), body=DUSK_MOSQ)
        evening(c, warm)
        # the closing line names the three of them; each gets a sparkle on its word
        sparkles(c, BX, BY - 170, t, b.word("dog"), n=9, r=150)
        sparkles(c, x, y, t, b.word("mosquito"), n=9, r=110)
        c.restore()

        def babies_up(cc):
            cc.save()
            cc.translate(480 - 540, 640 - 1000)
            cc.set_source_surface(bg.vessel(), 0, 0)
            cc.paint()
            bg.blood_cells(cc, t, n=90, speed=90, rad=(6, 8))
            up = prog(t, w_sip, w_sip + 1.8)
            proboscis_rod(cc, 540, 600, 540, lerp(700, 980, ease(prog(t, w_sip - 0.4, w_sip))), w=36)
            for i in range(4):
                kk = clamp((up - i * 0.12) / 0.6)
                dilly.draw_microfilaria(cc, st, lerp(400 + i * 90, 540, kk), lerp(1060 + 40 * (i % 2), 760, kk),
                                        2.4, t + i, ang=lerp(0.2 * i, -math.pi / 2, kk), face=True,
                                        alpha=1 - 0.8 * max(0.0, kk - 0.85) / 0.15 if kk > 0.85 else 1.0)
            cc.restore()

        def worm(cc):                                             # the teaser's lens, answered
            cc.save()
            cc.translate(420, 660)
            dilly.draw_along(cc, st, dilly.wiggle_points(150, -10, 330, t, amp=34, waves=1.4), 30,
                             blink=blinking(t, 1.2), happy=0.7)
            cc.restore()

        lens(c, 480, 640, 220, babies_up, window(t, w_sip - 0.2, w_jrn - 0.25, 0.35, 0.3))
        lens(c, 420, 660, 210, worm, window(t, b.word("worm") - 0.15, b.end + 0.6, 0.35, 0.3))

    tl.add(s_again, q["again"].start, q["button"].end + 0.45)

    # ---------------------------------------------------------- 16. the end card: the species and the logo
    # Owner (look frames): no cycle diagram at the end, just the title with the scientific name, and the logo,
    # centred on the frame (x 540), not on the caption column (x 480): at 480 it read as off-centre.
    def s_end(c, t, ctx):
        from engine import text as tx
        t0 = q["button"].end + 0.15
        c.save()
        c.translate(0, ctx.get("lift", 170))                    # full-screen card: undo the stage lift
        paint(c, bg.parchment())
        z = lerp(0.97, 1.02, ease(prog(t, t0, DUR)))
        c.translate(540, 900)
        c.scale(z, z)
        c.translate(-540, -900)
        ta = ease(prog(t, t0, t0 + 0.4))
        tx.center(c, "Dirofilaria immitis", 540, 720, 76, INK, alpha=ta, italic=True)
        tx.center(c, "the dog heartworm", 540, 790, 40, hexc("#8a5a3a"), alpha=ta * 0.9, italic=True)
        brand_plate(c, 540, 1000, ease(prog(t, t0 + 0.2, t0 + 0.7)))
        c.restore()

    tl.add(s_end, q["button"].end + 0.15, DUR + 0.1, trans_dur=0.5)

    # ---------------------------------------------------------- audio
    def make_audio(path):
        moods = [(0.0, "curious"), (q["biscuit"].start, "sleepy"), (q["poppy"].start, "playful"),
                 (q["past"].start, "mystery"), (q["grow"].start, "curious"), (q["bite"].start, "playful"),
                 (q["walk"].start, "quiet"), (q["ride"].start, "wonder"), (q["turn"].start, "curious"),
                 (q["long"].start, "wonder"), (q["need"].start, "mystery"), (q["again"].start, "finale")]
        HEAD = 0.4                                     # slice from a longer score: music on frame 0, none of the
        full = music.score(DUR + HEAD + 8.0, moods)    # end-card silence e002 shipped (judge lessons)
        i0 = int(HEAD * SR)
        bed = full[i0:i0 + int(DUR * SR)]
        fx = Bus(DUR, 5)
        for t0, name, gain in sfx_events(SFX, Q):
            fx.add(t0, sfx.LIB[name](), 0.0, gain)
        for ln in SCRIPT:                              # silent beats, exactly as in the approved preview
            if ln.sfx:
                fx.add(Q[ln.id].start, sfx.LIB[ln.sfx](), 0.0, 0.5)
        n = int(DUR * SR)
        out = mix.mixdown(n, music=bed, sfx=fx.buf, voice=track, music_gain=0.5)
        tail = int(0.8 * SR)
        out[-tail:] *= np.linspace(1.0, 0.0, tail)[:, None] ** 1.5
        raw = path.replace(".wav", "_raw.wav")
        mix.write_wav(raw, out)
        mix.loudnorm(raw, path)
        os.remove(raw)
        return path

    return tl, ctx, make_audio, Q


def key_times(Q):
    q = Q
    return [0.0, q["biscuit"].word("Biscuit") + 0.8, q["poppy"].word("Poppy") + 0.8, q["poppy"].word("eggs") + 0.5,
            q["dilly"].word("Dilly") + 0.7, q["past"].word("sipped") - 0.2, q["past"].end,
            q["grow"].word("weeks") + 0.3, q["grow"].end, q["bite"].start + 0.6,
            q["drop"].word("drop") + 0.4, q["drop"].word("wriggles") + 0.6, q["walk"].word("molts") + 0.6,
            q["walk"].end, q["ride"].word("molt") + 0.6, q["ride"].word("slips") + 0.6, q["ride"].word("heart") + 0.2,
            q["turn"].word("stop") + 0.3, q["home"].word("arteries") + 0.6, q["long"].word("thirty") + 0.5,
            q["male"].word("male") + 0.6, q["babies"].word("Tiny") + 0.8, q["need"].word("mosquito") + 0.4,
            q["again"].word("sip") + 0.8, q["button"].start + 0.5, q["button"].end + 2.0]


LOOK = ["teaser", "biscuit", "poppy", "dilly", "past", "grow", "land", "drop", "walk", "ride", "home",
        "long", "male", "babies", "need", "again", "button", "end"]


def look_times(Q):
    q = Q
    return dict(zip(LOOK, [0.0, q["biscuit"].word("Biscuit") + 0.8, q["poppy"].word("Poppy") + 0.9,
                           q["dilly"].word("Dilly") + 0.7, q["past"].word("sipped") - 0.1,
                           q["grow"].word("weeks") + 0.3, q["bite"].start + 0.6, q["drop"].word("wriggles") + 0.5,
                           q["walk"].word("molts") + 0.8, q["ride"].word("heart") + 0.1,
                           q["home"].word("arteries") + 0.7, q["long"].word("thirty") + 0.5,
                           q["male"].word("male") + 0.7, q["babies"].word("Tiny") + 1.0,
                           q["need"].word("mosquito") + 0.5, q["again"].word("sip") + 0.9,
                           q["button"].word("worm") + 0.6, q["button"].end + 2.2]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["stills", "look", "render", "captions"])
    ap.add_argument("--style", default="illustrated", choices=list(styles.STYLES))
    ap.add_argument("--copy-to", default=None)
    ap.add_argument("--times", default=None, help="comma separated seconds (stills)")
    a = ap.parse_args()
    tl, ctx, make_audio, Q = build(a.style)
    if a.cmd == "captions":
        for cap in tl.captions:
            print(f"{cap.start:6.2f}-{cap.end:6.2f} ({cap.end - cap.start:4.2f}s)  {' '.join(w for w, _, _ in cap.words)}")
        return
    if a.cmd == "look":
        out = os.path.join(os.path.dirname(os.path.dirname(HERE)), "for-review", "e003_look_frames")
        shutil.rmtree(out, ignore_errors=True)
        lt = look_times(Q)
        paths = render.stills(tl, ctx, list(lt.values()), out, prefix="look")
        named = []
        for (name, _), p in zip(lt.items(), paths):
            dst = os.path.join(out, f"{len(named) + 1:02d}_{name}.png")
            os.replace(p, dst)
            named.append(dst)
        sheet = render.contact_sheet(named, os.path.join(out, "00_overview.png"), cols=6, width=2800)
        print("look frames", out, "sheet", sheet)
        return
    review = os.path.join(HERE, "review", a.style)
    if a.cmd == "stills":
        shutil.rmtree(review, ignore_errors=True)
        times = [float(x) for x in a.times.split(",")] if a.times else key_times(Q)
        paths = render.stills(tl, ctx, times, review)
        sheet = render.contact_sheet(paths, os.path.join(HERE, "review", f"storyboard_{a.style}.png"),
                                     cols=6, width=2800)
        print("sheet", sheet)
        if a.copy_to:
            shutil.copy(sheet, a.copy_to)
        return
    outdir = os.path.join(HERE, "out")
    os.makedirs(outdir, exist_ok=True)
    wav = make_audio(os.path.join(outdir, f"audio_{a.style}.wav"))
    mp4 = os.path.join(outdir, f"{SLUG}_{a.style}.mp4")
    render.video(tl, ctx, mp4, wav)
    os.remove(wav)
    print("video", mp4, "LUFS", mix.measure_lufs(mp4))
    qa = render.sample_frames(mp4, os.path.join(HERE, "review", f"qa_{a.style}.png"), every=1.0, cols=10)
    if a.copy_to:
        shutil.copy(mp4, a.copy_to)
        shutil.copy(qa, a.copy_to)


if __name__ == "__main__":
    main()
