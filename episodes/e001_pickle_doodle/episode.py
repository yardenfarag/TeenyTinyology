"""Episode 001 — Pickle & Doodle (horsehair worm life cycle).

  python -m episodes.e001_pickle_doodle.episode stills --style cute [--copy-to DIR]
  python -m episodes.e001_pickle_doodle.episode render --style cute [--copy-to DIR]
Every scene time and sound cue is derived from the narration word timestamps.
"""
import argparse
import math
import os
import shutil

import cairo

from characters import doodle, pickle, pixie
from engine import backgrounds as bg
from engine import render
from engine import style as styles
from engine.audio import mix, music, sfx
from engine.audio.common import SR, Bus
from engine.core import (INK, TAU, H, W, back_out, clamp, ease, ease_out, ellipse, hexc, lerp, prog, rounded_rect,
                         squash, text_center, window)
from engine.scene import Timeline, badge, sparkles, tag
from engine.voice import narrate, sfx_events
from episodes.e001_pickle_doodle.script import SCRIPT, SFX

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "001-pickle-and-doodle"


class Cam:
    """Show world point (wx, wy) at screen point (sx, sy), zoomed by z."""

    def __init__(self, z=1.0, wx=540.0, wy=960.0, sx=540.0, sy=960.0):
        self.z, self.wx, self.wy, self.sx, self.sy = z, wx, wy, sx, sy

    def apply(self, c):
        c.translate(self.sx, self.sy)
        c.scale(self.z, self.z)
        c.translate(-self.wx, -self.wy)

    def screen(self, x, y):
        return (x - self.wx) * self.z + self.sx, (y - self.wy) * self.z + self.sy


def blinking(t, off=0.0, every=3.3):
    return ((t + off) % every) < 0.13


def paint(c, surf):
    c.set_source_surface(surf, 0, 0)
    c.paint()


def pickle_head_top(x, y, s):
    return pickle.to_world(x, y, s, 0, 104, -150)


def lerp2(a, b, k):
    return lerp(a[0], b[0], k), lerp(a[1], b[1], k)


def pill(c, txt, x, y, alpha, col=None, size=36):
    from engine.scene import label
    label(c, txt, x, y, alpha, size=size)


def _think(c, x, y, a):
    """Soft '?' thought bubble (x, y = bubble centre)."""
    if a <= 0:
        return
    k = back_out(min(1, a * 1.5))
    c.save()
    c.translate(x, y)
    c.scale(k, k)
    for rr, dx, dy in ((12, -48, 58), (18, -30, 32)):
        c.arc(dx, dy, rr, 0, TAU)
        c.set_source_rgba(1, 0.98, 0.95, 0.92 * a)
        c.fill()
    ellipse(c, 20, -20, 70, 58)
    c.set_source_rgba(1, 0.98, 0.95, 0.94 * a)
    c.fill()
    text_center(c, "?", 20, 6, 80, INK, bold=True, alpha=a)
    c.restore()


# ================================================================ build
def build(style_name):
    st = styles.get(style_name)
    TEASER = 1.5
    track, Q, caps, end = narrate(SCRIPT, os.path.join(HERE, "voice_cache"), t0=TEASER + 0.15)
    DUR = end + 2.4
    tl = Timeline(DUR, captions=caps)
    ctx = {"style": st, "vignette": bg.vignette()}
    q = Q

    # ------------------------------------------------------------ 0. teaser hook (frame 0 = thumbnail)
    def s_teaser(c, t, ctx):
        from engine.scene import label
        paint(c, bg.pond(night=True))
        bg.water_shimmer(c, t, night=True)
        pickle.draw(c, st, 470, 1300, 1.25, antenna=t * 2, blink=False)
        c.set_source_rgba(0.08, 0.1, 0.25, 0.25)
        c.paint()
        bg.water_shimmer(c, t + 0.5, night=True)
        hx, hy = pickle_head_top(470, 1300, 1.25)
        _think(c, hx + 30, hy - 60, 1.0)
        label(c, "Why would a cricket", 540, 470, 1.0, size=50)
        label(c, "jump into a pond?", 540, 560, 1.0, size=50)

    tl.add(s_teaser, 0.0, TEASER + 0.2)

    # ------------------------------------------------------------ 1. meet Pickle (meadow)
    def s_pickle(c, t, ctx):
        cam = Cam(1.0 + 0.05 * prog(t, 0, q["pixie1"].start))
        c.save()
        cam.apply(c)
        paint(c, bg.meadow())
        x = lerp(470, 560, ease(prog(t, TEASER, TEASER + 1.2)))
        walking = TEASER < t < TEASER + 1.2
        pickle.draw(c, st, x, 1390, 1.5, phase=x / 14, walking=walking, antenna=t * 2.2,
                    blink=blinking(t, 0.4), happy=0.6)
        c.restore()
        hx, hy = cam.screen(*pickle_head_top(x, 1390, 1.5))
        tag(c, "Pickle", hx, hy - 12, window(t, q["pickle"].word("Pickle"), q["pixie1"].start, 0.3, 0.3), sub="cricket")

    tl.add(s_pickle, TEASER, q["pixie1"].start, trans_dur=0.3)

    # ------------------------------------------------------------ 2. meet Pixie (pond)
    w_pond = q["pixie2"].word("underwater")
    w_flown = q["pixie2"].word("Now")
    w_end = q["pixie2"].word("shore") + 0.2
    LAND = (650, 1415)

    def pixie_pose(t):
        """Pixie's world position/state for the pond scenes."""
        if t < q["pixie1"].end:
            k = ease_out(prog(t, q["pixie1"].start - 0.3, q["pixie1"].end))
            x, y = lerp(-220, 560, k), 600 + 18 * math.sin(t * 3)
            return x, y, 1.05, t * 34, 0.0
        if t < w_flown - 0.2:
            return 560 + 30 * math.sin(t * 0.9), 600 + 18 * math.sin(t * 3), 1.05, t * 34, 0.0
        k = ease(prog(t, w_flown - 0.2, q["pixie2"].word("landed") + 0.3))
        x0, y0 = 560 + 30 * math.sin((w_flown - 0.2) * 0.9), 600 + 18 * math.sin((w_flown - 0.2) * 3)
        x, y = lerp(x0, LAND[0], k), lerp(y0, LAND[1], k) - 60 * math.sin(math.pi * k)
        flap = t * 34 if k < 0.95 else None
        rest = ease(prog(t, w_end - 0.1, w_end + 1.3))
        return x, y, lerp(1.05, 1.0, k), flap, rest

    def s_pixie(c, t, ctx):
        paint(c, bg.pond())
        bg.water_shimmer(c, t)
        # her early life: a nymph under the pond surface
        na = window(t, w_pond - 0.4, w_flown + 0.2, 0.4, 0.5)
        if na > 0:
            c.save()
            c.move_to(0, 800)
            c.line_to(W, 800)
            c.line_to(W, 1180)
            c.curve_to(760, 1290, 300, 1210, 0, 1260)
            c.close_path()
            c.clip()
            pixie.draw_nymph(c, st, 520 + 40 * math.sin(t), 1080, 1.8, t * 3, alpha=0.75 * na)
            c.restore()
            pill(c, "young Pixie, in the pond", 540, 1270, na, size=32)
        x, y, s, flap, rest = pixie_pose(t)
        if flap is not None:
            st.shadow(c, x - 40, 1180 if y < 1000 else LAND[1] + 6, 120, 10, 0.12)
        pixie.draw(c, st, x, y, s, flap=flap, rest=rest, blink=blinking(t, 1.1), happy=0.4)
        hx, hy = x + 60 * s, y - 210 * s
        tag(c, "Pixie", hx, hy, window(t, q["pixie1"].word("Pixie"), w_flown - 0.3, 0.3, 0.3), sub="mayfly")

    tl.add(s_pixie, q["pixie1"].start - 0.35, q["doodle1"].start + 0.25)

    # ------------------------------------------------------------ 3. Doodle hidden inside Pixie (x-ray close-up)
    cyst_local = (-92, -80)

    def s_doodle(c, t, ctx):
        z = lerp(1.6, 2.4, ease(prog(t, q["doodle1"].start - 0.4, q["doodle1"].start + 1.4)))
        cam = Cam(z, LAND[0] + 10, LAND[1] - 90, 540, 1000)
        c.save()
        cam.apply(c)
        paint(c, bg.pond())
        bg.water_shimmer(c, t)
        xa = ease(prog(t, q["doodle1"].start + 0.2, q["doodle1"].start + 0.9))
        pulse = 1 + 0.25 * math.sin(max(0, t - q["doodle1"].word("speck")) * 9) * window(t, q["doodle1"].word("speck"), q["doodle1"].word("speck") + 1.2, 0.1, 0.4)

        def inside(cc):
            doodle.draw_cyst(cc, st, *cyst_local, 17 * pulse, 1.0, t=t, blink=blinking(t, 2.0))

        pixie.draw(c, st, LAND[0], LAND[1], 1.0, rest=1.0, xray=inside, xray_alpha=xa)
        c.restore()
        px, py = cam.screen(*pixie.to_world(LAND[0], LAND[1] + 34, 1.0, 0, *cyst_local))
        tag(c, "Doodle", px, py - 40, window(t, q["doodle1"].word("Doodle"), q["eat"].start, 0.3, 0.3), sub="horsehair worm")
        sparkles(c, px, py, t, q["doodle1"].word("Doodle"))

    tl.add(s_doodle, q["doodle1"].start - 0.25, q["eat"].start + 0.1)

    # ------------------------------------------------------------ 4. Pickle eats Pixie (and Doodle)
    w_eats = q["eat"].word("gobbles")
    w_swallow = q["eat"].word("included")
    PX = (700, 1415)

    def pickle_x4(t):
        return lerp(-150, 352, ease_out(prog(t, q["eat"].start - 0.2, w_eats - 0.2)))

    def s_eat(c, t, ctx):
        cam = Cam(1.25, 520, 1260, 540, 1100)
        c.save()
        cam.apply(c)
        paint(c, bg.pond())
        bg.water_shimmer(c, t)
        x = pickle_x4(t)
        mouth = pickle.to_world(x, 1415, 1.2, 0, 140, -46)
        k = ease(prog(t, w_eats, w_eats + 1.1))
        if k < 1:
            pxy = lerp2(PX, mouth, k)
            pixie.draw(c, st, pxy[0], pxy[1] - 34 * (1 - k), 0.95 * (1 - 0.7 * k), rest=1.0, alpha=1 - k)
        xa = window(t, w_swallow - 0.1, w_swallow + 1.6, 0.25, 0.5)
        drop = ease(prog(t, w_swallow - 0.1, w_swallow + 0.8))

        def inside(cc):
            doodle.draw_cyst(cc, st, lerp(10, -72, drop), lerp(-60, -58, drop), 12, 1.0, t=t)

        chew = prog(t, w_eats, w_eats + 1.4)
        pickle.draw(c, st, x, 1415, 1.2, phase=x / 14, walking=t < w_eats - 0.2, antenna=t * 2.2,
                    blink=blinking(t, 0.9), chew=chew if 0 < chew < 1 else 0, happy=0.3 * (t > w_eats + 1.4),
                    xray=inside, xray_alpha=xa)
        c.restore()

    tl.add(s_eat, q["eat"].start - 0.35, q["grow1"].start)

    # ------------------------------------------------------------ 5. Doodle grows (x-ray), unwinds to show his length
    w_several = q["grow2"].word("several")
    w_coiled = q["grow2"].word("wound")
    N = 420

    def serpentine():
        rows, x0, x1, y0, gap = 3, 270, 810, 1150, 105
        pts = []
        for rI in range(rows):
            xs = (x0, x1) if rI % 2 == 0 else (x1, x0)
            y = y0 + rI * gap
            for k in range(100):
                pts.append((lerp(xs[0], xs[1], k / 99), y))
            if rI < rows - 1:
                cx = xs[1]
                d = 1 if rI % 2 == 0 else -1
                for k in range(1, 30):
                    a = -math.pi / 2 + math.pi * k / 30
                    pts.append((cx + d * math.cos(a) * gap / 2, y + gap / 2 + math.sin(a) * gap / 2))
        # resample to N
        out = []
        for i in range(N):
            f = i / (N - 1) * (len(pts) - 1)
            j = int(f)
            j2 = min(j + 1, len(pts) - 1)
            out.append(lerp2(pts[j], pts[j2], f - j))
        return out[::-1]

    SERP = serpentine()

    def s_grow(c, t, ctx):
        u = ease(prog(t, w_several - 0.2, w_several + 1.0)) * (1 - ease(prog(t, w_coiled, w_coiled + 1.0)))
        s = lerp(1.9, 0.72, u)
        x, y = lerp(590, 560, u), lerp(1330, 980, u)
        paint(c, bg.meadow())
        g = ease(prog(t, q["grow1"].start, q["grow2"].start + 0.4))
        r, turns, w = 10 + 50 * g, 1.2 + 4.8 * g, 2.2 + 2.8 * g
        coil_local = doodle.coil_points(-72, -58, r, turns, t, n=N, squash=0.55)
        if u < 0.02:
            def inside(cc):
                doodle.draw_along(cc, st, coil_local, w, face=False)
            pickle.draw(c, st, x, y, s, antenna=t * 2, blink=blinking(t), xray=inside,
                        xray_alpha=ease(prog(t, q["grow1"].start - 0.3, q["grow1"].start + 0.3)))
        else:
            pickle.draw(c, st, x, y, s, antenna=t * 2, blink=blinking(t), xray=lambda cc: None, xray_alpha=1 - u)
            coil_world = [pickle.to_world(x, y, s, 0, px, py) for px, py in coil_local]
            pts = [lerp2(a, b, u) for a, b in zip(coil_world, SERP)]
            doodle.draw_along(c, st, pts, lerp(w * s, 9, u), face=u > 0.6, blink=blinking(t, 1.7), happy=0.4)
            la = window(t, w_several + 0.4, w_coiled + 0.3, 0.3, 0.3)
            pill(c, "Doodle, unwound", 540, 780, la, size=34)
        wk = prog(t, q["grow1"].word("Week") - 0.3, q["grow2"].start + 0.2)
        if 0 < wk < 1:  # days and nights passing
            c.set_source_rgba(0.08, 0.1, 0.3, 0.32 * (0.5 - 0.5 * math.cos(TAU * 3 * wk)))
            c.paint()
        sparkles(c, 540, 1250, t, w_several + 0.6, r=160)

    tl.add(s_grow, q["grow1"].start - 0.35, q["problem1"].start)

    # ------------------------------------------------------------ 6. water vs land
    def s_split(c, t, ctx):
        w_land = q["problem2"].word("land")
        ysplit = lerp(bg.HH, 960, ease(prog(t, w_land - 1.4, w_land - 0.7)))
        c.save()
        c.rectangle(0, 0, W, ysplit)
        c.clip()
        paint(c, bg.underwater())
        bg.motes(c, t)
        for k, (yy, ph) in enumerate(((700, 0.0), (780, 1.7))):
            hx = 860 - ((t * 60 + k * 140) % 1200) * 0.0 - 120 * math.sin(t * 0.5 + ph)
            doodle.draw_along(c, st, doodle.swim_points(hx, yy, 380, t + ph), 9, face=False, alpha=0.9)
        pill(c, "Water: where worms find mates", 540, 560, ease(prog(t, q["problem1"].start, q["problem1"].start + 0.4)), size=38)
        c.restore()
        if ysplit < bg.HH:
            c.save()
            c.rectangle(0, ysplit, W, bg.HH - ysplit)
            c.clip()
            paint(c, bg.meadow())
            pickle.draw(c, st, 560, 1395, 1.15, antenna=t * 2, blink=blinking(t))
            pill(c, "Land", 540, 1080, ease(prog(t, w_land - 0.2, w_land + 0.2)), size=42)
            c.restore()
            c.move_to(0, ysplit)
            for xx in range(0, W + 20, 20):
                c.line_to(xx, ysplit + 7 * math.sin(xx / 40 + t * 2))
            c.set_source_rgba(1, 1, 1, 0.9)
            c.set_line_width(6)
            c.stroke()

    tl.add(s_split, q["problem1"].start - 0.35, q["drawn"].start)

    # ------------------------------------------------------------ 7. night: drawn toward water
    w_how = q["how"].start

    WANDER = [(160, 1500), (330, 1440), (250, 1380), (420, 1350), (360, 1310), (520, 1290)]

    def walk7(t):
        k = prog(t, q["drawn"].word("wandering") - 0.2, q["drawn"].word("finds") + 0.2)
        f = k * (len(WANDER) - 1)
        i = min(int(f), len(WANDER) - 2)
        x, y = lerp2(WANDER[i], WANDER[i + 1], ease(f - i))
        return x, y, lerp(1.15, 0.85, k), 0 < k < 1

    def s_night(c, t, ctx):
        paint(c, bg.pond(night=True))
        bg.water_shimmer(c, t, night=True)
        x, y, s, walking = walk7(t)
        pickle.draw(c, st, x, y, s, phase=t * 6, walking=walking, antenna=t * 1.5, blink=blinking(t, 0.2))
        c.set_source_rgba(0.08, 0.1, 0.25, 0.28)
        c.paint()
        bg.water_shimmer(c, t + 0.5, night=True)
        qa = window(t, w_how, HOP0 + 0.3, 0.25, 0.3)
        if qa > 0:
            hx, hy = pickle_head_top(x, y, s)
            _think(c, hx + 40, hy - 70, qa)

    HOP0 = q["how"].end + 0.15        # the jump: close shot, anticipation, big splash on the silent beat
    tl.add(s_night, q["drawn"].start - 0.35, HOP0 + 0.3)

    # ------------------------------------------------------------ 8. splash + Doodle escapes (underwater)
    w_water = q["splash"].start
    w_slips = q["escape"].word("slides")
    w_swims = q["escape"].word("swims")
    UNDER_AT = w_water + 0.35

    def s_hop(c, t, ctx):
        cam = Cam(lerp(1.5, 1.7, prog(t, HOP0, w_water + 0.8)), 560, 1180, 540, 1000)
        c.save()
        cam.apply(c)
        paint(c, bg.pond(night=True))
        bg.water_shimmer(c, t, night=True)
        crouch = ease(prog(t, HOP0, w_water - 1.1)) * (1 - ease(prog(t, w_water - 1.1, w_water - 1.0)))
        k = ease(prog(t, w_water - 1.05, w_water))
        x, y = lerp(480, 640, k), lerp(1290, 1120, k) - 240 * math.sin(math.pi * k)
        if k < 1:
            sx, sy = (1 + 0.06 * crouch, 1 - 0.1 * crouch) if k <= 0 else (0.94, 1.08)
            pickle.draw(c, st, x, y, 0.85, ang=-0.45 * math.sin(math.pi * k), crouch=crouch,
                        antenna=t * 2, sx=sx, sy=sy, blink=False)
        sp = prog(t, w_water, w_water + 1.1)
        if 0 < sp < 1:
            for i in range(4):
                ellipse(c, 640, 1120, 40 + 230 * sp + i * 34, (16 + 70 * sp + i * 12) * 0.5)
                c.set_source_rgba(1, 1, 1, (1 - sp) * 0.85)
                c.set_line_width(5)
                c.stroke()
            for i in range(16):
                a_ = -math.pi * (0.08 + 0.84 * i / 15)
                d = 220 * sp
                c.arc(640 + math.cos(a_) * d, 1120 + math.sin(a_) * d * 1.3 + 300 * sp * sp, 9 * (1 - sp), 0, TAU)
                c.set_source_rgba(0.85, 0.95, 1, 1 - sp)
                c.fill()
        c.set_source_rgba(0.08, 0.1, 0.25, 0.25)
        c.paint()
        c.restore()

    tl.add(s_hop, HOP0, UNDER_AT + 0.3, trans_dur=0.3)

    REAR_LOCAL = (-160, -54)   # tip of the abdomen: where hairworms really exit
    PFLOAT = (620, 478)        # floating at the surface (y 430), rear tipped under water
    PANG = -0.35
    DIR = (-0.36, 0.93)        # out of the rear, down and back, into the pond

    def s_escape(c, t, ctx):
        paint(c, bg.underwater())
        c.set_source_rgba(0.08, 0.12, 0.3, 0.42)  # night-time pond, matching the scene before
        c.paint()
        bg.motes(c, t)
        bob = 5 * math.sin(t * 2)
        rear = pickle.to_world(PFLOAT[0], PFLOAT[1] + bob, 1.1, PANG, *REAR_LOCAL)
        L = 720
        e = ease(prog(t, w_slips - 0.1, w_slips + 1.6))
        away = max(0.0, t - (w_slips + 1.6)) * 230
        head = (rear[0] + DIR[0] * (L * e + away), rear[1] + DIR[1] * (L * e + away))
        n = 200
        pts = []
        shown = min(L, L * e + away)   # only the part that has already come out is visible
        for i in range(n):
            uu = i / (n - 1)
            along = uu * shown
            px, py = head[0] - DIR[0] * along, head[1] - DIR[1] * along
            amp = 26 * math.sin(uu * TAU * 2.0 - t * 6) * min(1.0, uu * 4)
            pts.append((px + DIR[1] * amp, py - DIR[0] * amp))
        if shown > 12:
            doodle.draw_along(c, st, pts, 9, face=True, blink=blinking(t, 0.3), happy=0.5)
        pickle.draw(c, st, PFLOAT[0], PFLOAT[1] + bob, 1.1, ang=PANG, phase=t * 9, walking=True,
                    antenna=t * 3, blink=blinking(t), wet=1.0)
        bg.bubbles(c, t, rear[0], rear[1], n=10, seed=4, t0=w_slips - 0.2, life=2.2)
        bg.bubbles(c, t, PFLOAT[0] + 80, PFLOAT[1] + 40, n=6, seed=9, t0=UNDER_AT, life=3.0)

    tl.add(s_escape, UNDER_AT, q["survive"].start + 0.1, transition="fade", trans_dur=0.3)

    # ------------------------------------------------------------ 9. Pickle survives
    w_dry = q["survive"].word("dry")

    def s_survive(c, t, ctx):
        paint(c, bg.pond())
        bg.water_shimmer(c, t)
        k = ease(prog(t, q["survive"].start, q["survive"].start + 1.4))
        x, y = lerp(380, 560, k), lerp(1260, 1405, k)
        wet = 1 - ease(prog(t, w_dry - 0.2, w_dry + 1.4))
        shake = 0.04 * math.sin(t * 40) * window(t, w_dry - 0.2, w_dry + 0.6, 0.1, 0.2)
        pickle.draw(c, st, x, y, 1.3, ang=shake, phase=x / 14, walking=0 < k < 1, antenna=t * 2.4,
                    blink=blinking(t, 0.5), happy=ease(prog(t, w_dry, w_dry + 0.5)), wet=wet)
        hx, hy = pickle_head_top(x, y, 1.3)
        sparkles(c, hx, hy + 60, t, w_dry + 0.3, r=120)

    tl.add(s_survive, q["survive"].start - 0.35, q["cycle1"].start)

    # ------------------------------------------------------------ 10. the cycle
    w_hatch = q["cycle1"].word("hatches")
    w_swallow2 = q["cycle2"].word("swallowed")
    w_fly = q["cycle3"].word("fly")
    w_cycle = q["cycle3"].word("cricket") + 0.4
    EGGS = (300, 1250)
    LARVA_T = (640, 1180)

    def s_pondlife(c, t, ctx):
        paint(c, bg.underwater())
        bg.motes(c, t)
        # gelatinous egg strings
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        for k in range(3):
            pts = [(EGGS[0] - 160 + i * 16, EGGS[1] + k * 26 + 14 * math.sin(i * 0.5 + k + t * 0.8)) for i in range(22)]
            c.move_to(*pts[0])
            for p_ in pts[1:]:
                c.line_to(*p_)
            c.set_source_rgba(1, 1, 1, 0.55)
            c.set_line_width(16)
            c.stroke()
            for p_ in pts[::2]:
                c.arc(p_[0], p_[1], 3.5, 0, TAU)
                c.set_source_rgba(*hexc("#e8dfc4"))
                c.fill()
        hk = prog(t, w_hatch - 0.1, w_hatch + 1.6)
        eaten = t >= w_swallow2 + 0.2
        for i in range(6):
            if hk <= 0:
                break
            a = -0.6 + i * 0.35
            d = 40 + 260 * ease_out(hk) * (0.5 + 0.12 * i)
            lx, ly = EGGS[0] + math.cos(a) * d, EGGS[1] + math.sin(a) * d * 0.6
            if i == 2:
                lx, ly = lerp2((lx, ly), LARVA_T, ease(prog(t, w_hatch + 1.0, w_swallow2)))
                if eaten:
                    continue
            c.arc(lx, ly, 13, 0, TAU)            # soft glow so a tiny speck is still visible
            c.set_source_rgba(1, 1, 0.9, 0.35)
            c.fill()
            doodle.draw_larva(c, st, lx, ly, 0.45, t * 6 + i)
        nk = ease(prog(t, q["cycle2"].start - 0.2, w_swallow2 + 0.1))
        # head (local x ~ +50 at scale 2.2) arrives at the larva: comes in from the left, head first
        nx, ny = lerp(-260, LARVA_T[0] - 105, nk), LARVA_T[1] + 22 + 8 * math.sin(t * 2)
        if q["cycle2"].start - 0.2 < t:
            pixie.draw_nymph(c, st, nx, ny, 2.2, t * 3)
            if eaten:
                doodle.draw_cyst(c, st, nx - 120, ny - 44, 13, ease(prog(t, w_swallow2 + 0.2, w_swallow2 + 0.6)), t=t)
            tag(c, "young mayfly", nx - 20, ny - 100, window(t, q["cycle2"].word("insects"), q["cycle3"].start, 0.3, 0.3),
                size=34, sub="like Pixie once was")

    tl.add(s_pondlife, q["cycle1"].start - 0.35, q["cycle3"].start + 0.2)

    def s_flyup(c, t, ctx):
        paint(c, bg.pond())
        bg.water_shimmer(c, t)
        k = ease(prog(t, w_fly - 0.4, w_fly + 1.2))
        x, y = lerp(420, 640, k), lerp(1050, 560, k)
        pixie.draw(c, st, x, y, 0.9, flap=t * 34, happy=0.4, alpha=ease(prog(t, w_fly - 0.6, w_fly - 0.2)))
        rk = prog(t, w_fly - 0.6, w_fly + 0.4)
        if 0 < rk < 1:
            ellipse(c, 420, 1050, 30 + 120 * rk, (30 + 120 * rk) * 0.3)
            c.set_source_rgba(1, 1, 1, 1 - rk)
            c.set_line_width(4)
            c.stroke()

    tl.add(s_flyup, q["cycle3"].start - 0.2, w_cycle + 0.3)

    CX, CY, CR = 495, 850, 290   # screen coords; right edge stays clear of the app buttons
    NODES = [("Eggs hatch\nin the pond", "eggs"), ("Mayfly nymph\nswallows a larva", "nymph"),
             ("Mayfly flies\nto land", "fly"), ("Cricket eats\nthe mayfly", "cricket"),
             ("Cricket jumps in,\nworm swims out", "worm")]

    def node_icon(c, kind, t):
        if kind == "eggs":
            for k in range(2):
                c.move_to(-70, k * 22)
                for i in range(10):
                    c.line_to(-70 + i * 16, k * 22 + 8 * math.sin(i * 0.6 + k))
                c.set_source_rgba(1, 1, 1, 0.8)
                c.set_line_width(12)
                c.stroke()
            doodle.draw_larva(c, st, 60, -30, 2.2, t * 5)
        elif kind == "nymph":
            pixie.draw_nymph(c, st, 80, 20, 1.2, t * 3)
            doodle.draw_cyst(c, st, -10, -6, 9, 1.0, t=t)
        elif kind == "fly":
            pixie.draw(c, st, 20, 60, 0.55, flap=t * 34)
        elif kind == "cricket":
            def inside(cc):
                doodle.draw_along(cc, st, doodle.coil_points(-72, -58, 55, 5, t, n=300), 5, face=False)
            pickle.draw(c, st, 10, 50, 0.55, xray=inside, xray_alpha=1.0, antenna=t * 2)
        else:
            doodle.draw_along(c, st, doodle.swim_points(90, 0, 200, t), 7, face=True)

    def s_cycle(c, t, ctx):
        from engine.scene import STAGE_LIFT
        c.translate(0, STAGE_LIFT)  # lay the end card out in screen coordinates
        paint(c, bg.parchment())
        t0 = w_cycle - 0.35
        ta = ease(prog(t, t0, t0 + 0.4))
        text_center(c, "The horsehair worm cycle", W / 2, 330, 58, INK, italic=True, bold=True, alpha=ta)
        step = TAU / len(NODES)
        for i, (label, kind) in enumerate(NODES):
            a = -math.pi / 2 + i * step
            nt = t0 + 0.15 + 0.22 * i
            k = prog(t, nt, nt + 0.3)
            nx, ny = CX + CR * math.cos(a), CY + CR * math.sin(a)
            if k > 0:
                c.save()
                c.translate(nx, ny - 20)
                s_ = back_out(k)
                c.scale(s_, s_)
                node_icon(c, kind, t)
                c.restore()
                for j, ln in enumerate(label.split("\n")):
                    text_center(c, ln, nx, ny + 74 + j * 40, 36, INK, alpha=ease(k))
            pa = ease(prog(t, nt + 0.2, nt + 0.55))
            if pa > 0:
                a0, a1 = a + 0.42, a + step - 0.42
                e_ = lerp(a0, a1, pa)
                c.new_path()
                c.arc(CX, CY, CR, a0, e_)
                c.set_source_rgba(*INK[:3], 0.8)
                c.set_line_width(5)
                c.stroke()
                if pa > 0.7:
                    hx, hy = CX + CR * math.cos(e_), CY + CR * math.sin(e_)
                    tx, ty = -math.sin(e_), math.cos(e_)
                    nx2, ny2 = math.cos(e_), math.sin(e_)
                    c.move_to(hx + tx * 14, hy + ty * 14)
                    c.line_to(hx - tx * 10 + nx2 * 12, hy - ty * 10 + ny2 * 12)
                    c.line_to(hx - tx * 10 - nx2 * 12, hy - ty * 10 - ny2 * 12)
                    c.close_path()
                    c.fill()
        ea = ease(prog(t, q["cycle3"].end + 0.55, q["cycle3"].end + 1.1))  # after the last caption has gone
        text_center(c, "Teenyology", W / 2, 1385, 64, INK, bold=True, alpha=ea)
        text_center(c, "Teeny creatures. Big stories.", W / 2, 1440, 34, INK, italic=True, alpha=ea * 0.8)

    tl.add(s_cycle, w_cycle - 0.35, DUR + 0.1)

    # ------------------------------------------------------------ audio
    moods = [(0, "cozy"), (q["pixie1"].start, "wonder"), (q["doodle1"].start, "curious"), (q["eat"].start, "playful"),
             (q["grow1"].start, "curious"), (q["problem1"].start, "mystery"), (q["splash"].start, "wonder"),
             (q["survive"].start, "cozy"), (q["cycle1"].start, "finale")]
    events = sfx_events(SFX, Q)  # word-anchored effects from the approved script (same as the preview)
    events += [(Q[ln.id].start, ln.sfx, 0.5) for ln in SCRIPT if ln.sfx]  # silent beats
    events += [(0.6, "birdsong", 0.05), (2.2, "birdsong", 0.04), (q["survive"].start + 0.5, "birdsong", 0.05),
               (q["doodle1"].word("Doodle"), "sparkle", 0.1)]
    walks = [(0.0, 1.2), (q["eat"].start, 1.6), (q["drawn"].start + 0.4, 4.0)]
    node_times = [w_cycle - 0.2 + 0.22 * i for i in range(len(NODES))]

    def make_audio(out_wav, narrated=True):
        n = int(DUR * SR)
        m = music.score(DUR, moods)
        fx = Bus(DUR, 5)
        for t0, name, gain in events:
            fx.add(t0, sfx.LIB[name](), 0.0, gain)
        for t0, d in walks:
            fx.add(t0, sfx.footsteps(d, 9), 0.0, 0.025)
        for i, t0 in enumerate(node_times):
            fx.add(t0, sfx.chime(1046.5 * 2 ** (i * 2 / 12)), -0.4 + 0.2 * i, 0.06)
        for k in range(int((q["pixie2"].word("landed") + 0.3 - q["pixie1"].start) * 8)):  # Pixie's wing flutter
            fx.add(q["pixie1"].start - 0.3 + k / 8, sfx.flap(), 0.2, 0.02)
        for k in range(int(1.6 * 8)):
            fx.add(w_fly - 0.4 + k / 8, sfx.flap(), 0.2, 0.02)
        out = mix.mixdown(n, music=m, sfx=fx.buf, voice=track if narrated else None, music_gain=0.5)
        raw = out_wav.replace(".wav", "_raw.wav")
        mix.write_wav(raw, out)
        mix.loudnorm(raw, out_wav)
        os.remove(raw)
        return out_wav

    return tl, ctx, make_audio, Q


# ================================================================ CLI
def key_times(Q):
    q = Q
    return [1.5, q["hook"].end - 0.3, q["pixie1"].end - 0.2, q["pixie2"].word("underwater") + 0.8, q["pixie2"].end,
            q["doodle2"].start + 0.5, q["eat"].word("gobbles") + 0.4, q["eat"].word("included") + 0.5, q["grow1"].end,
            q["grow2"].word("several") + 1.4, q["problem2"].end, q["drawn"].start + 3.0, q["how"].start + 1.0,
            q["splash"].start - 0.2, q["escape"].word("swims") + 0.4, q["survive"].word("dry") + 0.8, q["cycle1"].end,
            q["cycle2"].end - 0.3, q["cycle3"].word("fly") + 0.6, q["cycle3"].end + 1.2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["stills", "render"])
    ap.add_argument("--style", default="cute", choices=list(styles.STYLES))
    ap.add_argument("--copy-to", default=None)
    ap.add_argument("--times", default=None, help="comma separated seconds (stills)")
    a = ap.parse_args()
    tl, ctx, make_audio, Q = build(a.style)
    review = os.path.join(HERE, "review", a.style)
    if a.cmd == "stills":
        times = [float(x) for x in a.times.split(",")] if a.times else key_times(Q)
        paths = render.stills(tl, ctx, times, review)
        sheet = render.contact_sheet(paths, os.path.join(HERE, "review", f"storyboard_{a.style}.png"), cols=7, width=2800)
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
