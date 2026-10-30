"""Episode 002 — Roly & Mango: the tongue-eating isopod (Cymothoa exigua).

Built on the same bones as e001: a Timeline of scenes whose starts and ends all come from the narration
cues, never from hard-coded seconds. Run:

    .venv/Scripts/python -m episodes.e002_roly_mango.episode stills --style illustrated
    .venv/Scripts/python -m episodes.e002_roly_mango.episode render --style illustrated
"""
import argparse
import math
import os
import shutil

import cairo
import numpy as np

from characters import mango, roly
from engine import backgrounds as bg
from engine import render
from engine import style as styles
from engine.audio import mix, music, sfx
from engine.audio.common import SR, Bus
from engine.core import (TAU, H, W, back_out, clamp, ease, ease_out, ellipse, hexc, lerp, prog,
                         rounded_rect, window)
from engine.scene import Timeline, tag, wordmark
from engine.voice import narrate, sfx_events
from episodes.e002_roly_mango.script import SCRIPT, SFX

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "002-roly-and-mango"


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


def blinking(t, off=0.0, every=3.1):
    return ((t + off) % every) < 0.13


def paint(c, surf):
    c.set_source_surface(surf, 0, 0)
    c.paint()


def drift(t, x, y, ax=16, ay=10, sp=0.7):
    """Everything in water sways a little, always."""
    return x + ax * math.sin(t * sp), y + ay * math.sin(t * sp * 1.37 + 1.1)


def brand_plate(c, x, y, a, max_w=640):
    """Series logo plate for the end card (navy pill + the wordmark with the lens 'o')."""
    if a <= 0:
        return
    from branding.banner import NAVY
    k = back_out(min(1.0, a * 1.3))
    size = 100
    c.save()
    c.translate(x, y)
    c.scale(0.9 + 0.1 * k, 0.9 + 0.1 * k)
    c.push_group()
    # measure through the shared wordmark helper by drawing it once into a scratch group
    c.push_group()
    tot = wordmark(c, 0, 0, size, alpha=0.0)
    c.pop_group()
    size *= min(1.0, max_w / tot)
    c.push_group()
    tot = wordmark(c, 0, 0, size, alpha=0.0)
    c.pop_group()
    pw, ph = tot + size * 0.9, size * 1.55
    rounded_rect(c, -pw / 2, -ph / 2 + 6, pw, ph, ph / 2)
    c.set_source_rgba(0.1, 0.08, 0.05, 0.18)
    c.fill()
    rounded_rect(c, -pw / 2, -ph / 2, pw, ph, ph / 2)
    c.set_source_rgba(*NAVY[:3], 1)
    c.fill()
    wordmark(c, 0, size * 0.3, size, alpha=1.0)
    c.pop_group_to_source()
    c.paint_with_alpha(a)
    c.restore()


def species_line(c, y, a):
    from engine import text as tx
    if a <= 0:
        return
    tx.center(c, "Cymothoa exigua", 480, y, 44, (1, 0.98, 0.95), a * 0.92, italic=True)
    tx.center(c, "on the spotted rose snapper · Gulf of California", 480, y + 54, 30, (1, 0.98, 0.95), a * 0.6)


# ================================================================ build
def build(style_name):
    st = styles.get(style_name)
    TEASER = 1.5
    track, Q, caps, end = narrate(SCRIPT, os.path.join(HERE, "voice_cache"), t0=TEASER + 0.15)
    DUR = end + 3.2
    tl = Timeline(DUR, captions=caps)
    ctx = {"style": st, "vignette": bg.vignette(), "watermark": True, "fade_in": 0.0}
    q = Q

    # ---------------------------------------------------------- 0. teaser: the mouth opens
    def s_teaser(c, t, ctx):
        from engine.scene import label
        paint(c, bg.sea())
        k = ease(prog(t, 0.35, q["hook1"].end))
        gape = 0.14 + 0.86 * k

        def inside(cc):
            roly.draw_facing(cc, st, 0, 42, 0.55, phase=t * 1.6, grip=1.0,
                             blink=blinking(t, 0.2), happy=0.25, tilt=0.70, alpha=k)

        x, y = drift(t, 540, 1010, 10, 8, 0.6)
        mango.draw_front(c, st, x, y, 2.05, mouth=gape, inside=inside, teeth=1.0,
                         blink=blinking(t, 1.1), phase=t * 1.4)
        label(c, "What is living", 480, 420, 1 - ease(prog(t, q["hook1"].end, q["hook2"].start + 0.25)), size=52)
        label(c, "in this fish's mouth?", 480, 510, 1 - ease(prog(t, q["hook1"].end, q["hook2"].start + 0.25)), size=52)

    tl.add(s_teaser, 0.0, q["mango"].start, trans_dur=0.3)

    # ---------------------------------------------------------- 1. meet Mango
    def s_mango(c, t, ctx):
        cam = Cam(1.0 + 0.04 * prog(t, q["mango"].start, q["roly"].start))
        c.save()
        cam.apply(c)
        paint(c, bg.sea())
        x = lerp(-320, 520, ease_out(prog(t, q["mango"].start - 0.2, q["mango"].start + 1.6)))
        y = 1000 + 16 * math.sin(t * 0.8)
        mango.draw(c, st, x, y, 1.58, phase=t * 1.5, blink=blinking(t, 0.5), happy=0.6)
        c.restore()
        hx, hy = cam.screen(x + 150, y - 190)
        tag(c, "Mango", hx, hy, window(t, q["mango"].word("Mango"), q["roly"].start, 0.3, 0.3),
            sub="spotted rose snapper")

    tl.add(s_mango, q["mango"].start, q["roly"].start)

    # ---------------------------------------------------------- 2. meet Roly
    def s_roly(c, t, ctx):
        from engine.scene import label
        paint(c, bg.sea())
        bg.motes(c, t, n=26, y0=400, y1=1500, col=(0.9, 0.97, 1.0), a=0.35)
        z = lerp(0.92, 1.26, ease(prog(t, q["roly"].start, q["arrive"].start)))
        x, y = drift(t, 500, 920, 14, 12, 0.55)
        c.save()
        c.translate(x, y)
        c.scale(z, z)
        c.rotate(0.05 * math.sin(t * 0.6))
        roly.draw(c, st, 0, 0, 1.45, phase=t * 1.5, female=True,
                  blink=blinking(t, 0.9), happy=0.45)
        c.restore()
        tag(c, "Roly", x + 170, y - 150, window(t, q["roly"].word("Roly"), q["arrive"].start, 0.3, 0.3),
            sub="a parasitic isopod")
        a = window(t, q["roly"].word("crustacean"), q["arrive"].start, 0.35, 0.3)
        label(c, "not an insect. not a louse.", 480, 1330, a, size=40)

    tl.add(s_roly, q["roly"].start, q["arrive"].start)

    # ---------------------------------------------------------- 3. arrival: a speck at the gills
    def s_arrive(c, t, ctx):
        paint(c, bg.sea())
        az = lerp(0.96, 1.22, ease(prog(t, q["arrive"].start, q["two"].start)))
        c.save()
        c.translate(540, 960)
        c.scale(az, az)
        c.translate(-540, -960)
        mx, my = drift(t, 650, 1000, 10, 8, 0.6)
        gx, gy = mango.to_world(mx, my, 1.42, 0.0, *mango.GILL_SLOT)
        w_gills = q["arrive"].word("gills")
        k1 = ease(prog(t, q["arrive"].start - 0.2, w_gills - 0.8))     # approach
        k2 = ease(prog(t, w_gills - 0.4, w_gills + 0.35))              # the slip under the gill cover
        hold = (gx - 40, gy + 160)                                     # behind and below the operculum
        ax, ay = lerp(-90, hold[0], k1), lerp(1450, hold[1], k1)
        sx = lerp(ax, gx + 30, k2) + 24 * math.sin(t * 2.6) * (1 - k1)
        sy = lerp(ay, gy - 10, k2) + 12 * math.sin(t * 3.1) * (1 - k1)
        # drawn BEFORE Mango, so the gill cover genuinely hides her as she goes in — no fade-out
        roly.draw_manca(c, st, sx, sy, 1.0, phase=t * 3.4, ang=lerp(-0.3, -1.25, k2))
        mango.draw(c, st, mx, my, 1.42, phase=t * 1.5, blink=blinking(t, 0.5), happy=0.4)
        bg.bubbles(c, t, gx, gy, n=6, seed=4, t0=w_gills)
        c.restore()

    tl.add(s_arrive, q["arrive"].start, q["two"].start)

    # ---------------------------------------------------------- 4. two of them, on the gills
    def gill_pair(c, t, grow=0.0, show_female=False, female_dx=0.0, female_fade=1.0):
        paint(c, bg.gill_chamber())
        mango.draw_gill_chamber(c, st, 540, 1010, 1.75, phase=t * 1.2)
        a_scale = lerp(0.52, 0.72, grow)
        roly.draw(c, st, 380 + female_dx, 850, a_scale, ang=-0.45, phase=t * 1.6, female=show_female,
                  grip=0.8 * female_fade, blink=blinking(t, 0.3), happy=0.3, alpha=female_fade)
        roly.draw(c, st, 740, 1210, 0.52, ang=-0.5, phase=t * 1.6 + 1.2, female=False,
                  grip=0.8, blink=blinking(t, 1.7))

    def s_two(c, t, ctx):
        from engine.scene import label
        gill_pair(c, t)
        label(c, "on the gills", 480, 560, window(t, q["two"].start + 0.3, q["change"].start, 0.3, 0.3), size=38)
        a = window(t, q["two"].word("male"), q["change"].start, 0.3, 0.3)
        tag(c, "male", 380, 690, a)
        tag(c, "male", 740, 1060, a)

    tl.add(s_two, q["two"].start, q["change"].start)

    # ---------------------------------------------------------- 5. Roly grows, and changes
    def s_change(c, t, ctx):
        grow = ease(prog(t, q["change"].start, q["change"].word("changed") + 0.5))
        gill_pair(c, t, grow=grow, show_female=grow > 0.55)
        if grow > 0.2:
            from engine.scene import sparkles
            sparkles(c, 380, 850, t, q["change"].word("changed") - 0.2, n=11, r=190)

    tl.add(s_change, q["change"].start, q["female"].start)

    # ---------------------------------------------------------- 6. she becomes female, and takes the mouth
    def s_female(c, t, ctx):
        from engine.scene import label
        leave = ease(prog(t, q["female"].word("gets") - 0.2, q["female"].end + 0.35))
        gill_pair(c, t, grow=1.0, show_female=True, female_dx=760 * leave, female_fade=1 - leave)
        a = window(t, q["female"].word("became"), q["female"].word("mouth"), 0.3, 0.3)
        tag(c, "she will never be male again", 380, 660, a)
        # she leaves the gills and swims forward towards the mouth (no wash, no ghost label:
        # a dark overlay with text on it read as a glitch in the first storyboard)
        k = ease(prog(t, q["female"].word("gets") - 0.2, q["female"].end + 0.35))
        if k > 0:
            label(c, "forward, into the mouth", 480, 1330, window(t, q["female"].word("gets"), q["female"].end + 0.3, 0.25, 0.25), size=40)

    tl.add(s_female, q["female"].start, q["tongue1"].start)

    # ---------------------------------------------------------- 7. what a fish's tongue actually is (card)
    # This card held for 10.5 s with almost no visual change in the first render. It is now drawn in
    # sentence order, word by word, under a slow push-in (docs/judge-lessons.md).
    def s_tongue(c, t, ctx):
        from engine.scene import label, leader
        c.save()
        c.translate(0, ctx.get("lift", 170))      # full-screen card: undo the stage lift
        paint(c, bg.parchment())
        cx, cy = 540, 780
        kz = prog(t, q["tongue1"].start, q["tongue2"].end)
        z = lerp(0.94, 1.40, kz)
        panx = lerp(40, -30, kz)
        pany = lerp(30, -26, kz)
        roof_k = ease(prog(t, q["tongue1"].start + 0.1, q["tongue1"].word("tongue") + 0.3))
        teeth_k = prog(t, q["tongue1"].word("tongue") + 0.1, q["tongue1"].word("bony") + 0.2)
        pad_k = back_out(prog(t, q["tongue1"].word("bony") - 0.25, q["tongue1"].word("pad") + 0.45))
        # At "no muscle of its own" the pad tries to move and can't — three decaying attempts, which
        # both fills the dead air before the food arrives and shows the fact instead of labelling it.
        tm = t - q["tongue1"].word("muscle")
        wob = 0.0
        if 0 < tm < 2.8:
            wob = 9.0 * (1 - tm / 2.8) * abs(math.sin(tm * 2.1)) * math.sin(tm * 16.0)
        food_k = prog(t, q["tongue2"].start - 0.15, q["tongue2"].start + 0.55)
        press = 0.5 - 0.5 * math.cos(max(0.0, t - q["tongue2"].start) * 3.4)
        tooth_pulse = 1.0 + 0.30 * max(0.0, 1 - prog(t, q["tongue2"].word("teeth"),
                                                     q["tongue2"].word("teeth") + 0.9))
        c.save()
        c.translate(cx + panx, cy + pany)
        c.scale(1.25 * z, 1.25 * z)
        # ---- roof of the mouth
        if roof_k > 0:
            c.save()
            c.scale(1.0, roof_k)
            c.move_to(-320, -150)
            c.curve_to(-140, -40, 140, -40, 320, -150)
            c.set_source_rgba(*hexc("#b8705e")[:3], 0.9 * roof_k)
            c.set_line_width(26)
            c.set_line_cap(cairo.LINE_CAP_ROUND)
            c.stroke()
            c.restore()
        n_teeth = 11
        for k in range(n_teeth):
            f = k / (n_teeth - 1)
            a = min(1.0, max(0.0, teeth_k * n_teeth - k))
            if a <= 0:
                continue
            px = lerp(-250, 250, f)
            py = -150 + 110 * (1 - (2 * f - 1) ** 2) - 18
            h = 26 * a * tooth_pulse
            c.move_to(px - 9 * a, py)
            c.line_to(px, py + h)
            c.line_to(px + 9 * a, py)
            c.close_path()
            c.set_source_rgba(0.99, 0.97, 0.92, 0.95)
            c.fill_preserve()
            c.set_source_rgba(0.62, 0.5, 0.42, 0.6)
            c.set_line_width(2)
            c.stroke()
        # ---- floor of the mouth, and the bony pad on it
        if pad_k > 0:
            c.move_to(-320, 210)
            c.curve_to(-140, 130, 140, 130, 320, 210)
            c.set_source_rgba(*hexc("#b8705e")[:3], 0.9 * min(1.0, pad_k * 1.4))
            c.set_line_width(26)
            c.stroke()
            c.save()
            c.translate(wob, 118)
            c.scale(min(1.15, pad_k), min(1.15, pad_k))
            ellipse(c, 0, 0, 150, 52, 0.0)
            c.set_source_rgba(*hexc("#e8d6b4")[:3], 1)
            c.fill_preserve()
            c.set_source_rgba(*hexc("#9a7e58")[:3], 0.85)
            c.set_line_width(5)
            c.stroke()
            c.restore()
        # ---- a mouthful of food, pressed up against the teeth
        if food_k > 0:
            fy = lerp(96, -104, press)
            ellipse(c, wob * 0.4, fy, 44 * food_k, 34 * food_k, 0.3)
            c.set_source_rgba(*hexc("#8fae6a")[:3], 0.95 * food_k)
            c.fill_preserve()
            c.set_source_rgba(*hexc("#5e7a42")[:3], 0.7 * food_k)
            c.set_line_width(4)
            c.stroke()
        c.restore()
        a1 = window(t, q["tongue1"].word("pad"), q["tongue2"].end + 0.3, 0.3, 0.3)
        label(c, "that is why something else can do the job", 480, 1210, a1, size=38)
        leader(c, 480, 1160, 540, 1040, a1, col=(0.3, 0.2, 0.1))
        a2 = window(t, q["tongue2"].word("teeth"), q["tongue2"].end + 0.3, 0.3, 0.3)
        label(c, "these are the vomerine teeth", 480, 420, a2, size=40)
        c.restore()

    tl.add(s_tongue, q["tongue1"].start, q["grip"].start, transition="iris",
           iris_center=lambda t: (540, 900))

    # ---------------------------------------------------------- 8-11. inside the mouth: grip, fade, place, feet
    TONGUE_X, TONGUE_Y = 540, 1270

    Z0, Z1 = 1.0, 1.38

    def mouth_cam(t, z=None):
        """One slow continuous push-in across grip -> fade -> place, so the heart of the episode is never
        a still picture (judge pass 1). The focus drifts onto the tongue only as the zoom comes in, so at
        z = 1 this is the identity: re-centring at z = 1 shifted the background and showed black bars."""
        z = lerp(Z0, Z1, ease(prog(t, q["grip"].start, q["feet"].start))) if z is None else z
        k = clamp((z - Z0) / (Z1 - Z0))     # clamped: past Z1 the focus overshot and clipped her
        return Cam(z, 540.0, lerp(960.0, TONGUE_Y - 40, k))

    def mouth_set(c, t, tongue_a=1.0, tongue_k=1.0, roly_a=0.0, roly_scale=1.15, grip=1.0):
        paint(c, bg.mouth_inside())
        if tongue_a > 0:    # the bony pad on the floor of the mouth
            c.save()
            c.translate(TONGUE_X, TONGUE_Y + 54)      # she grips the BASE, so the pad lies forward of her
            c.scale(lerp(0.35, 1.0, tongue_k), lerp(0.42, 1.0, tongue_k))
            ellipse(c, 0, 0, 300, 108, 0.0)
            c.set_source_rgba(*hexc("#edd9b4")[:3], tongue_a)
            c.fill_preserve()
            c.set_source_rgba(*hexc("#9a7e58")[:3], 0.8 * tongue_a)
            c.set_line_width(6)
            c.stroke()
            c.restore()
        if roly_a > 0:
            st.shadow(c, TONGUE_X, TONGUE_Y + 18, 210 * roly_scale, 34 * roly_scale, 0.20 * roly_a)
            roly.draw_facing(c, st, TONGUE_X, TONGUE_Y - 46, roly_scale, phase=t * 1.5,
                             grip=grip, blink=blinking(t, 0.7), happy=0.3, tilt=0.66, alpha=roly_a)

    def s_grip(c, t, ctx):
        from engine.scene import label
        k = ease(prog(t, q["grip"].start, q["grip"].word("clamps") + 0.6))
        c.save()
        mouth_cam(t).apply(c)
        # legs reach, then hook down with a squash as they bite
        sq = 1.0 + 0.12 * max(0.0, 1 - prog(t, q["grip"].word("clamps"), q["grip"].word("clamps") + 0.45))
        mouth_set(c, t, tongue_a=1.0, tongue_k=1.0, roly_a=k,
                  roly_scale=0.92 * sq, grip=lerp(0.0, 1.0, k))
        c.restore()
        a = window(t, q["grip"].word("drinks"), q["grip"].end + 0.3, 0.3, 0.3)
        label(c, "she drinks the blood that feeds the tongue", 480, 560, a, size=38)

    tl.add(s_grip, q["grip"].start, q["fade"].start, transition="iris",
           iris_center=lambda t: (TONGUE_X, TONGUE_Y - 120))

    def s_fade(c, t, ctx):
        # the gentle fade the owner asked for: no blood, no wound. It thins, shrinks, and is gone.
        k = ease(prog(t, q["fade"].word("blood") + 0.2, q["fade"].word("falls") + 0.5))
        c.save()
        mouth_cam(t).apply(c)
        mouth_set(c, t, tongue_a=1.0 - k, tongue_k=1.0 - 0.72 * k, roly_a=1.0, roly_scale=0.92, grip=1.0)
        c.restore()

    tl.add(s_fade, q["fade"].start, q["place"].start, transition="cut")

    def s_place(c, t, ctx):
        k = ease(prog(t, q["place"].start, q["place"].word("place") + 0.6))
        c.save()
        mouth_cam(t).apply(c)
        c.translate(540, 960)
        pz = lerp(1.0, 1.09, ease(prog(t, q["place"].start, q["feet"].start)))
        c.scale(pz, pz)
        c.translate(-540, -960)
        mouth_set(c, t, tongue_a=0.0, roly_a=1.0, roly_scale=lerp(0.92, 1.12, k), grip=1.0)
        c.restore()

    tl.add(s_place, q["place"].start, q["feet"].start, transition="cut")

    def s_feet(c, t, ctx):
        from engine.scene import label
        z = lerp(Z1, 1.76, ease(prog(t, q["feet"].start, q["feet"].end)))
        c.save()
        mouth_cam(t, z).apply(c)
        mouth_set(c, t, tongue_a=0.0, roly_a=1.0, roly_scale=1.18, grip=1.0)
        c.restore()
        label(c, "seven pairs of hooked feet", 480, 480,
              window(t, q["feet"].word("feet"), q["eats"].start, 0.3, 0.3), size=42)

    tl.add(s_feet, q["feet"].start, q["eats"].start, transition="cut")

    # ---------------------------------------------------------- 12. Mango goes back to eating
    def s_eats(c, t, ctx):
        paint(c, bg.sea())
        ke = ease(prog(t, q["eats"].start, q["proof"].start))
        mx, my = drift(t, lerp(380, 640, ke), 980, 12, 9, 0.7)
        chew = 0.5 + 0.5 * math.sin(t * 5.2)
        mango.draw(c, st, mx, my, 1.52, phase=t * 1.5, mouth=0.25 + 0.5 * chew,
                   blink=blinking(t, 0.5), happy=0.7)
        fx = mx + 330 - 70 * chew
        ellipse(c, fx, my + 26, 46, 36, 0.4)
        c.set_source_rgba(*hexc("#8fae6a")[:3], 0.95)
        c.fill()

    tl.add(s_eats, q["eats"].start, q["proof"].start)

    # ---------------------------------------------------------- 13. the proof: grooves on her back
    def s_proof(c, t, ctx):
        from engine.scene import label
        z = lerp(1.14, 1.62, ease(prog(t, q["proof"].start, q["proof"].end)))
        c.save()
        mouth_cam(t, z).apply(c)
        mouth_set(c, t, tongue_a=0.0, roly_a=1.0, roly_scale=1.18, grip=1.0)
        # the scratches the fish's tooth patch wore into her shell
        a = window(t, q["proof"].word("scuffed"), q["press"].end, 0.25, 0.4)
        if a > 0:
            c.save()
            c.translate(TONGUE_X, TONGUE_Y - 46)
            for k in range(4):     # light scuffs, only on the front two segments nearest her head
                f = k / 3
                x0 = lerp(-46, 46, f)
                c.move_to(x0 - 17, -44 + 5 * f)
                c.curve_to(x0 - 5, -52 + 5 * f, x0 + 5, -52 + 5 * f, x0 + 17, -44 + 5 * f)
                c.set_source_rgba(0.38, 0.29, 0.23, 0.42 * a)
                c.set_line_width(3.0)
                c.set_line_cap(cairo.LINE_CAP_ROUND)
                c.stroke()
            c.restore()
        c.restore()
        label(c, "only on her first two segments", 480, 470,
              window(t, q["proof"].word("scuffed"), q["press"].start, 0.3, 0.3), size=40)
        a2 = window(t, q["press"].word("pressing"), q["hedge1"].start, 0.3, 0.3)
        label(c, "the teeth in the roof, pressing down", 480, 1300, a2, size=40)

    tl.add(s_proof, q["proof"].start, q["hedge1"].start, transition="cut")

    # ---------------------------------------------------------- 14. the honest hedge
    def s_hedge(c, t, ctx):
        from engine.scene import label
        paint(c, bg.sea())
        sw = ease(prog(t, q["hedge1"].start, q["pouch"].start))
        mx, my = drift(t, lerp(300, 720, sw), lerp(1040, 960, sw), 14, 10, 0.55)
        mango.draw(c, st, mx, my, lerp(1.34, 1.62, sw), phase=t * 1.5, blink=blinking(t, 0.5), happy=0.5)
        label(c, "fish carrying several are often underweight", 480, 520,
              window(t, q["hedge1"].word("Nobody"), q["hedge2"].start, 0.3, 0.3), size=42)
        label(c, "the scientists' best guess", 480, 1330,
              window(t, q["hedge2"].word("better"), q["pouch"].start, 0.3, 0.3), size=40)

    tl.add(s_hedge, q["hedge1"].start, q["pouch"].start)

    # ---------------------------------------------------------- 15-16. the pouch, and the father
    def s_pouch(c, t, ctx):
        from engine.scene import label
        paint(c, bg.mouth_inside())
        x, y = drift(t, 500, 960, 8, 6, 0.5)
        z = lerp(1.30, 2.05, ease(prog(t, q["pouch"].start, q["father"].start)))
        c.save()
        c.translate(x, y)
        c.scale(z, z)
        c.rotate(0.035 * math.sin(t * 0.7))
        roly.draw_underside(c, st, 0, 0, 0.92, eggs=ease(prog(t, q["pouch"].start, q["pouch"].word("eggs") + 0.6)),
                            phase=t * 1.4, blink=blinking(t, 0.8))
        c.restore()
        label(c, "they leave as swimmers, not larvae", 480, 1330,
              window(t, q["pouch"].word("eggs"), q["father"].start, 0.3, 0.3), size=40)

    tl.add(s_pouch, q["pouch"].start, q["father"].start, transition="iris",
           iris_center=lambda t: (540, 1000))

    def s_father(c, t, ctx):
        # The owner wants the father visible in the same shot as the pouch. He lives on the gills and she
        # is in the mouth, so the frame has to say which is which: she holds the shot, he sits in an
        # inset labelled "on the gills" (judge pass 2 — drawing her inside the gill chamber read as both
        # of them living there, and contradicted "the female gets the mouth").
        from engine.scene import label, soft_bubble
        paint(c, bg.mouth_inside())
        pz = lerp(0.98, 1.52, ease(prog(t, q["father"].start, q["hatch"].start)))
        x, y = drift(t, 470, 1010, 8, 6, 0.5)
        c.save()
        c.translate(540, 960)
        c.scale(pz, pz)
        c.rotate(0.05 * math.sin(t * 0.55))
        c.translate(-540, -960)
        roly.draw_underside(c, st, x, y, 0.78, eggs=1.0, phase=t * 1.8, blink=blinking(t, 0.8))
        c.restore()
        a = window(t, q["father"].word("father"), q["hatch"].start, 0.3, 0.3)
        # --- the inset: his half of the fish
        ix, iy, iw, ih = 560, 404, 320, 250
        if a > 0:
            c.save()
            ka = back_out(min(1.0, a * 1.2))        # the inset eases in instead of popping
            c.translate(ix + iw / 2, iy + ih / 2)
            c.scale(0.82 + 0.18 * ka, 0.82 + 0.18 * ka)
            c.translate(-(ix + iw / 2), -(iy + ih / 2))
            rounded_rect(c, ix - 8, iy - 8, iw + 16, ih + 16, 28)
            c.set_source_rgba(1.0, 0.97, 0.92, 0.85 * a)
            c.fill()
            rounded_rect(c, ix, iy, iw, ih, 22)
            c.clip()
            c.save()
            c.translate(ix + iw / 2 - 540 * 0.42, iy + ih / 2 - 1010 * 0.42)
            c.scale(0.42, 0.42)
            paint(c, bg.gill_chamber())
            mango.draw_gill_chamber(c, st, 540, 1010, 1.5, phase=t * 1.2)
            roly.draw(c, st, 560, 1060, 0.62, ang=-0.5, phase=t * 1.6 + 1.2, female=False,
                      grip=0.85, blink=blinking(t, 1.7))
            c.restore()
            c.restore()
            label(c, "on the gills", ix + iw / 2, iy + ih + 36, a, size=34)
        tag(c, "the father", ix + iw / 2, iy + 86, a)

    tl.add(s_father, q["father"].start, q["hatch"].start)

    # ---------------------------------------------------------- 17. the cycle: four hundred specks
    def s_hatch(c, t, ctx):
        # Roly never leaves the mouth, so the brood has to come out of Mango, not out of open water
        # (judge pass 1: a free-swimming adult here contradicted the next line and the source).
        paint(c, bg.sea())
        bg.motes(c, t, n=30, y0=420, y1=1500, col=(0.92, 0.98, 1.0), a=0.3)
        swim = ease(prog(t, q["hatch"].start, q["stay"].start))
        mx, my = drift(t, lerp(250, 640, swim), lerp(1040, 950, swim), 12, 9, 0.55)
        gape = 0.30 + 0.45 * (0.5 + 0.5 * math.sin(t * 1.6))
        mango.draw(c, st, mx, my, lerp(1.16, 1.46, swim), phase=t * 1.6, mouth=gape,
                   blink=blinking(t, 0.5), happy=0.4)
        lipx, lipy = mango.to_world(mx, my, lerp(1.16, 1.46, swim), 0.0, 236.0, 14.0)  # just outside her lips
        k = ease(prog(t, q["hatch"].word("opens"), q["hatch"].end + 0.5))
        import random as _r
        rr = _r.Random(77)
        for i in range(46):
            f = rr.uniform(0.25, 1.0)
            kk = max(0.0, min(1.0, (k - rr.uniform(0.0, 0.55)) / 0.80))
            if kk <= 0:
                continue
            spread = rr.uniform(-0.55, 0.55)
            d = kk * rr.uniform(300, 700)
            px = lipx + d
            py = lipy + d * spread * 0.55 + 26 * math.sin(t * 3.1 + i)
            roly.draw_manca(c, st, px, py, lerp(0.46, 0.30, kk), phase=t * 4.2 + i,
                            ang=spread * 0.5, alpha=min(1.0, kk * 3.0) * (1 - 0.45 * kk))

    tl.add(s_hatch, q["hatch"].start, q["stay"].start)

    # ---------------------------------------------------------- 18. the button, then the end card
    def s_button(c, t, ctx):
        paint(c, bg.sea())
        k = ease(prog(t, q["stay"].start, q["stay"].end))
        gape = 0.30 + 0.70 * ease(prog(t, q["button"].start - 0.5, q["button"].word("tongue")))

        def inside(cc):
            roly.draw_facing(cc, st, 0, 42, 0.55, phase=t * 1.6, grip=1.0,
                             blink=blinking(t, 0.2), happy=0.35, tilt=0.70)

        x, y = drift(t, 540, 1010, 10, 8, 0.6)
        mango.draw_front(c, st, x, y, lerp(1.85, 2.10, k), mouth=gape, inside=inside, teeth=1.0,
                         blink=blinking(t, 1.1), phase=t * 1.4)

    tl.add(s_button, q["stay"].start, q["button"].end + 0.5)

    def s_end(c, t, ctx):
        paint(c, bg.sea())
        a = ease(prog(t, q["button"].end + 0.4, q["button"].end + 1.3))
        c.save()
        c.translate(0, ctx.get("lift", 170))
        breathe = 1.0 + 0.018 * math.sin(t * 1.5)
        c.save()
        c.translate(540, 760)
        c.scale(breathe, 1.0 / breathe)
        roly.draw_facing(c, st, 0, 0, 1.05, phase=t * 1.4, grip=0.0,
                         blink=blinking(t, 0.5, every=2.6), happy=0.5, tilt=0.45, alpha=a)
        c.restore()
        species_line(c, 1120, a)
        brand_plate(c, 540, 1400, a)
        c.restore()

    tl.add(s_end, q["button"].end + 0.3, DUR, trans_dur=0.6)

    # ---------------------------------------------------------- audio
    def make_audio(path):
        moods = [(0.0, "mystery"), (q["mango"].start, "curious"), (q["arrive"].start, "playful"),
                 (q["tongue1"].start, "wonder"), (q["grip"].start, "quiet"), (q["eats"].start, "cozy"),
                 (q["proof"].start, "wonder"), (q["hedge1"].start, "quiet"), (q["pouch"].start, "curious"),
                 (q["hatch"].start, "finale")]
        # The theme starts ~0.35 s in and resolves to digital silence before a long episode ends, which
        # left no music on frame 0 and 2.0 s of absolute silence over the end card (judge pass 2 #2).
        # Take a slice from the middle of a longer score instead, and fade it ourselves.
        HEAD = 0.4
        full = music.score(DUR + HEAD + 8.0, moods)
        i0 = int(HEAD * SR)
        bed = full[i0:i0 + int(DUR * SR)]
        fx = Bus(DUR, 5)
        for t0, name, gain in sfx_events(SFX, Q):
            fx.add(t0, sfx.LIB[name](), 0.0, gain)
        n = int(DUR * SR)
        out = mix.mixdown(n, music=bed, sfx=fx.buf, voice=track, music_gain=0.5)
        tail = int(0.8 * SR)                 # ride the theme out under the end card instead of cutting
        out[-tail:] *= np.linspace(1.0, 0.0, tail)[:, None] ** 1.5
        raw = path.replace(".wav", "_raw.wav")
        mix.write_wav(raw, out)
        mix.loudnorm(raw, path)
        os.remove(raw)
        return path

    return tl, ctx, make_audio, Q


def key_times(Q):
    q = Q
    return [0.9, q["hook2"].end - 0.2, q["mango"].word("Mango") + 0.9, q["roly"].word("crustacean") + 0.7,
            q["arrive"].word("gills") - 0.25, q["two"].word("male") + 0.6, q["change"].word("changed") + 0.5,
            q["female"].word("gets") + 0.3, q["tongue1"].word("pad") + 0.8, q["tongue2"].word("teeth") + 0.9,
            q["grip"].word("drinks") + 0.4, q["fade"].word("falls") + 0.3, q["place"].word("place") + 0.5,
            q["feet"].word("feet") + 0.9, q["eats"].word("eating") + 0.4, q["proof"].word("grooves") + 0.8,
            q["press"].word("pressing") + 0.7, q["hedge2"].word("better") + 0.8, q["pouch"].word("eggs") + 0.7,
            q["father"].word("father") + 1.1, q["hatch"].word("swim") + 1.4, q["button"].end + 0.2,
            q["button"].end + 2.4]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["stills", "render"])
    ap.add_argument("--style", default="illustrated", choices=list(styles.STYLES))
    ap.add_argument("--copy-to", default=None)
    ap.add_argument("--times", default=None, help="comma separated seconds (stills)")
    a = ap.parse_args()
    tl, ctx, make_audio, Q = build(a.style)
    review = os.path.join(HERE, "review", a.style)
    if a.cmd == "stills":
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
