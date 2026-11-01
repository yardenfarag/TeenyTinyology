"""Episode 004 — Kiwi & Toffee: the crab-hacker barnacle (Sacculina carcini) on a shore crab.

Same bones as e001–e003: a Timeline of scenes whose starts and ends all come from the narration cues.
The magnifying-glass "lens" is the device for anything too small to see; the parchment card is the device
for the belly-view comparisons (a diagram, so it gets a big push-in).
Run:
    .venv/Scripts/python -m episodes.e004_kiwi_toffee.episode look                 # look frames for the owner
    .venv/Scripts/python -m episodes.e004_kiwi_toffee.episode stills --style illustrated
    .venv/Scripts/python -m episodes.e004_kiwi_toffee.episode render --style illustrated
"""
import argparse
import math
import os
import shutil

import cairo
import numpy as np

from characters import kiwi, toffee
from engine import backgrounds as bg
from engine import render
from engine import style as styles
from engine.audio import mix, music, sfx
from engine.audio.common import SR, Bus
from engine.core import TAU, back_out, clamp, ease, ease_out, ellipse, hexc, lerp, prog, rng, window
from engine.scene import Timeline, label, sparkles, tag
from engine.voice import narrate, sfx_events
from episodes.e002_roly_mango.episode import Cam, blinking, brand_plate, paint
from episodes.e003_biscuit_dilly.episode import framed, lens
from episodes.e004_kiwi_toffee.script import SCRIPT, SFX

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "004-kiwi-and-toffee"
INK = hexc("#3a2a1a")

# Kiwi's spot on the sand (world coords; the scene is drawn STAGE_LIFT higher on screen). Shell centre.
KX, KY = 440, 1240
KS = 1.3                           # Kiwi's scale on the shore: he has to fill a phone screen
ROCK_TOP = (820, 1060)            # the climbable rock (engine/backgrounds.shore)
# Scene coordinates are screen + 170 (STAGE_LIFT). Safe zone in scene coords: x 60..900, y 370..1630.
TOP_LABEL_Y = 560                 # top labels (true y 390): clear of the watermark badge and the app's top bar


def drift(t, x, y, ax=10, ay=6, sp=0.7):
    return x + ax * math.sin(t * sp), y + ay * math.sin(t * sp * 1.37 + 1.1)


def card_cam(t, t0, t1, z0=0.94, z1=1.30, fx=540, fy=980):
    """A diagram card needs a big push-in (judge lessons: 1.0→1.17 over 11 s was invisible)."""
    z = lerp(z0, z1, ease(prog(t, t0, t1)))
    return Cam(z, fx, fy + 20 * ease(prog(t, t0, t1)), 540, 980)


def build(style_name):
    st = styles.get(style_name)
    TEASER = 1.5
    track, Q, caps, end = narrate(SCRIPT, os.path.join(HERE, "voice_cache"), t0=TEASER + 0.15)
    DUR = end + 4.9                      # end card fully readable >= 4 s
    tl = Timeline(DUR, captions=caps)
    ctx = {"style": st, "vignette": bg.vignette(), "watermark": True, "fade_in": 0.0}
    q = Q

    def shore(c, t):
        paint(c, bg.shore())
        bg.motes(c, t, n=30, y0=480, y1=1380, seed=7, col=(0.9, 1, 0.95), a=0.35)

    def sac_under(cc, t, eggs=1.0, happy=0.4, grow=1.0, hatch=0.0, males=0.0, blink=None):
        """Toffee's sac where it hangs: under the rear edge of Kiwi's shell (front view), local coords."""
        toffee.draw_sac(cc, st, 0, 108, 0.62, eggs=eggs, phase=t * 2, happy=happy, stalk=False, grow=grow,
                        hatch=hatch, males=males, blink=blinking(t, 1.7) if blink is None else blink)

    # ---------------------------------------------------------- 0. teaser (frame 0 is the thumbnail)
    def s_teaser(c, t, ctx):
        cam = framed(lerp(1.15, 1.22, ease(prog(t, 0.0, q["kiwi"].start))), KX + 40, KY - 20)
        c.save()
        cam.apply(c)
        shore(c, t)
        kiwi.draw(c, st, KX, KY, KS, phase=t, blink=blinking(t, 0.6), happy=0.8, raise_=0.85, pinch=0.5,
                  claw=0.8, sac=lambda cc: sac_under(cc, t), look=(0.1, 0.2))
        c.restore()
        fade = (1 - ease(prog(t, q["hook"].end, q["kiwi"].start))) * ctx.get("teaser_labels", 1.0)
        label(c, "A crab, raising babies...", 540, TOP_LABEL_Y, fade, size=52)
        label(c, "that aren't even his", 540, TOP_LABEL_Y + 90, fade, size=52)

    tl.add(s_teaser, 0.0, q["kiwi"].start, trans_dur=0.3)

    # ---------------------------------------------------------- 1. meet Kiwi (he sidles in from the left)
    def s_kiwi(c, t, ctx):
        k = ease_out(prog(t, q["kiwi"].start - 0.2, q["kiwi"].start + 1.6))
        x = lerp(-120, KX, k)
        cam = framed(1.08, KX, 1180)
        c.save()
        cam.apply(c)
        shore(c, t)
        kiwi.draw(c, st, x, KY, KS, phase=t, walk=1.0 - k, blink=blinking(t, 0.6), happy=0.5, pinch=0.3)
        c.restore()
        hx, hy = cam.screen(x, KY - 150)
        tag(c, "Kiwi", hx, hy, window(t, q["kiwi"].word("Kiwi") + 0.1, q["toffee"].start, 0.3, 0.3), sub="a shore crab")

    tl.add(s_kiwi, q["kiwi"].start, q["toffee"].start)

    # ---------------------------------------------------------- 2. meet Toffee: a speck, then the lens
    def toffee_path(t, t0, t1):
        k = ease(prog(t, t0, t1))
        x = lerp(760, 560, k) + 10 * math.sin(t * 1.7)
        y = lerp(700, 1000, k) + 8 * math.sin(t * 2.3)
        return x, y

    def s_toffee(c, t, ctx):
        cam = framed(1.08, KX, 1180)
        c.save()
        cam.apply(c)
        shore(c, t)
        kiwi.draw(c, st, KX, KY, KS, phase=t, blink=blinking(t, 0.6), happy=0.4, look=(0.6, -0.4))
        px, py = toffee_path(t, q["toffee"].start, q["land"].start)
        toffee.draw_larva(c, st, px, py, 0.22, phase=t, ang=0.5, blink=blinking(t, 1.0))   # a true speck
        c.restore()
        sx, sy = cam.screen(px, py)
        # the lens shows who the speck is
        def inner(cc):
            cc.save()
            cc.translate(sx + 20, sy - 330)
            toffee.draw_larva(cc, st, 0, 0, 3.0, phase=t, ang=0.15, blink=blinking(t, 1.0), happy=0.6)
            cc.restore()
        a_lens = window(t, q["toffee"].word("speck") - 0.1, q["land"].start + 0.2, 0.35, 0.3)
        lens(c, sx + 20, sy - 330, 170, inner, a_lens)
        tag(c, "Toffee", sx, sy - 16, window(t, q["toffee"].word("Toffee") + 0.1, q["land"].start, 0.3, 0.3),
            sub="a barnacle")
        # the rock barnacles on the left rock: what people think a barnacle is
        bx, by = cam.screen(150, 1200)
        label(c, "rock barnacles", bx + 60, by - 120, window(t, q["toffee"].word("guess") - 0.2, q["land"].start, 0.3, 0.3), size=34)

    tl.add(s_toffee, q["toffee"].start, q["land"].start)

    # ---------------------------------------------------------- 3. she lands on Kiwi and walks to a soft spot
    SPOT = (-96, -34)     # local shell point where she settles: the rim just behind the side teeth

    def s_land(c, t, ctx):
        k = ease(prog(t, q["land"].start, q["needle"].start))
        cam = framed(lerp(1.15, 1.55, k), KX - 60, KY - 80)
        c.save()
        cam.apply(c)
        shore(c, t)
        # her landing: from above-right down onto the shell, then a short walk along the rim to the spot
        k1 = ease(prog(t, q["land"].start, q["land"].word("lands") + 0.2))
        k2 = ease(prog(t, q["land"].word("finds") - 0.2, q["land"].word("spot") + 0.3))
        lx0, ly0 = kiwi.to_world(KX, KY, KS, 0.0, 20, -90)
        lx1, ly1 = kiwi.to_world(KX, KY, KS, 0.0, *SPOT)
        px = lerp(lerp(KX + 160, lx0, k1), lx1, k2)
        py = lerp(lerp(KY - 320, ly0, k1), ly1, k2)
        kiwi.draw(c, st, KX, KY, KS, phase=t, blink=blinking(t, 0.6), happy=0.3, look=(-0.3, -0.6))
        toffee.draw_larva(c, st, px, py, 0.22, phase=t, ang=lerp(0.9, 0.0, k1) + 0.2 * k2, blink=blinking(t, 1.0))
        c.restore()
        sx, sy = cam.screen(px, py)

        def inner(cc):
            cc.save()
            cc.translate(sx, sy - 250)
            cc.set_source_rgba(*kiwi.SHELL.base)
            cc.paint()
            toffee.draw_larva(cc, st, 0, 10, 3.0, phase=t * (1 + 2 * (1 - k2)), ang=0.1, blink=blinking(t, 1.0), happy=0.4)
            cc.restore()

        lens(c, sx, sy - 250, 170, inner, window(t, q["land"].start + 0.4, q["needle"].start + 0.3, 0.35, 0.3))
        label(c, "a soft spot in his shell", sx, sy - 250 - 170 - 70, window(t, q["land"].word("soft") - 0.1, q["needle"].start, 0.3, 0.3), size=36)

    tl.add(s_land, q["land"].start, q["needle"].start)

    # ---------------------------------------------------------- 4. the needle (inside the lens, big)
    def s_needle(c, t, ctx):
        n = q["needle"]
        cam = framed(1.55, KX - 60, KY - 80)
        c.save()
        cam.apply(c)
        shore(c, t)
        kiwi.draw(c, st, KX, KY, KS, phase=t, blink=blinking(t, 0.6), happy=0.1, look=(-0.3, -0.6))
        c.restore()
        lx, ly = kiwi.to_world(KX, KY, KS, 0.0, *SPOT)
        sx, sy = cam.screen(lx, ly)
        shed = ease(prog(t, n.word("sheds") - 0.1, n.word("sheds") + 0.6))
        push = ease(prog(t, n.word("needle") - 0.2, n.word("needle") + 0.5))
        inject = ease(prog(t, n.word("injects") - 0.1, n.end + 0.5))

        def inner(cc):
            cc.save()
            cc.translate(sx, sy - 250)
            # the shell surface: green above a cut-away of his inside (pale pink) below the surface line
            cc.set_source_rgba(*kiwi.SHELL.light)
            cc.paint()
            cc.rectangle(-300, 20, 600, 400)
            cc.set_source_rgba(*hexc("#f2cfc0"))
            cc.fill()
            cc.rectangle(-300, 0, 600, 20)
            cc.set_source_rgba(*kiwi.SHELL.dark)
            cc.fill()
            if shed < 1:            # the larva, still whole, crouched on the shell
                toffee.draw_larva(cc, st, 0, -20, 4.2 * (1 - 0.3 * shed), phase=t, ang=0.1, blink=blinking(t, 1.0),
                                  alpha=1 - shed)
            toffee.draw_kentrogon(cc, st, 0, 0, 4.2, inject=inject, phase=t, alpha=min(1.0, shed * 1.5))
            if push < 1:            # the needle pushes down as the word lands
                cc.set_source_rgba(*kiwi.SHELL.light)
                cc.rectangle(-16, lerp(4, 120, push), 32, 140)
                cc.fill()
            cc.restore()

        lens(c, sx, sy - 250, 210, inner, 1.0)
        label(c, "a tiny hollow needle", sx, sy - 250 - 210 - 70, window(t, n.word("needle") - 0.1, n.end + 0.6, 0.3, 0.3), size=36)

    tl.add(s_needle, q["needle"].start, q["roots"].start, transition="cut")

    # ---------------------------------------------------------- 5. roots: x-ray
    def s_roots(c, t, ctx):
        r_ = q["roots"]
        k = ease(prog(t, r_.start, q["fine"].start))
        cam = framed(lerp(1.35, 1.15, k), KX, KY - 40)
        grow = ease(prog(t, r_.word("roots") - 0.2, r_.word("body") + 0.8))
        pulse = 0.5 + 0.5 * math.sin(t * 6) if t > r_.word("drinks") else 0.0
        c.save()
        cam.apply(c)
        shore(c, t)

        def roots(cc):
            cc.set_source_rgba(*hexc("#f4d9cc")[:3], 0.55)      # his inside, seen through the shell
            cc.paint()
            toffee.draw_roots(cc, st, SPOT[0], SPOT[1], 1.0, grow=grow, seed=1, arms=6, length=105, width=7.5)
            if pulse > 0:
                ellipse(cc, SPOT[0], SPOT[1], 14 + 4 * pulse, 11 + 3 * pulse)
                cc.set_source_rgba(*toffee.ROOT.light[:3], 0.8)
                cc.fill()

        kiwi.draw(c, st, KX, KY, KS, phase=t, blink=blinking(t, 0.6), happy=0.2, xray=roots,
                  xray_alpha=ease(prog(t, r_.start, r_.start + 0.7)) * 0.95)
        c.restore()
        sx, sy = cam.screen(KX, KY - 220)
        label(c, "roots, through his whole body", sx, sy, window(t, r_.word("Through") - 0.1, q["fine"].start, 0.3, 0.3), size=36)

    tl.add(s_roots, q["roots"].start, q["fine"].start)

    # ---------------------------------------------------------- 6. Kiwi looks fine (but...)
    def s_fine(c, t, ctx):
        f = q["fine"]
        k = ease(prog(t, f.start, q["months"].start))
        cam = framed(lerp(1.25, 1.1, k), KX, KY - 60)
        c.save()
        cam.apply(c)
        shore(c, t)
        kiwi.draw(c, st, KX, KY, KS, phase=t, blink=blinking(t, 0.6), happy=0.7, pinch=0.3)
        c.restore()
        sx, sy = cam.screen(KX, KY - 230)
        for i, (w, txt) in enumerate((("shed", "no more shell-shedding"), ("grow", "no more growing"),
                                       ("babies", "no babies of his own"))):
            a = window(t, f.word(w) - 0.1, q["months"].start, 0.3, 0.3)
            label(c, txt, 480, sy - 100 + i * 70, a, size=36)

    tl.add(s_fine, q["fine"].start, q["months"].start)

    # ---------------------------------------------------------- 7. months later: the sac pushes out
    def s_months(c, t, ctx):
        m = q["months"]
        k = ease(prog(t, m.start, q["body"].start))
        cam = framed(lerp(1.1, 1.35, k), KX, KY + 30)
        grow = lerp(0.25, 1.0, ease(prog(t, m.word("pushes") - 0.2, m.word("flap") + 0.3)))
        c.save()
        cam.apply(c)
        shore(c, t)
        kiwi.draw(c, st, KX, KY, KS, phase=t, blink=blinking(t, 0.6), happy=0.3, look=(0.0, 0.5),
                  sac=lambda cc: sac_under(cc, t, eggs=0.0, happy=0.3, grow=grow))
        c.restore()
        a_m = window(t, m.start, m.word("sac") - 0.1, 0.3, 0.3)
        label(c, "months later", 540, TOP_LABEL_Y, a_m, size=44)
        sx, sy = cam.screen(KX, KY + 180)
        tag(c, "a sac", sx, sy, window(t, m.word("sac") - 0.1, m.word("Right"), 0.3, 0.3), sub="under his tail flap")
        # inset: a mother crab, belly up, her eggs under her wide tail flap

        def mother(cc):
            cc.save()
            cc.translate(300, 700)
            kiwi.draw_underside(cc, st, 0, 0, 0.62, flap=1.0, lift=0.85, eggs=1.0, phase=t, blink=blinking(t, 2.0))
            cc.restore()

        a_mo = window(t, m.word("mother") - 0.3, q["body"].start + 0.2, 0.35, 0.3)
        lens(c, 300, 700, 200, mother, a_mo)
        label(c, "a mother crab's eggs", 300, 940, a_mo, size=34)

    tl.add(s_months, q["months"].start, q["body"].start)

    # ---------------------------------------------------------- 8. his body changes: the belly card
    def belly_card(c, t, t0, t1, flap, lift, under=None, eggs=0.0, push=(0.94, 1.30)):
        cam = card_cam(t, t0, t1, *push)
        c.save()
        c.translate(0, ctx.get("lift", 170))                      # full-screen card: undo the stage lift
        paint(c, bg.parchment())
        cam.apply(c)
        kiwi.draw_underside(c, st, 540, 900, 1.9, flap=flap, lift=lift, under=under, eggs=eggs, phase=t,
                            blink=blinking(t, 0.6))
        c.restore()
        return cam

    def s_body(c, t, ctx):
        b = q["body"]
        flap = ease(prog(t, b.word("grows") - 0.2, b.word("round") + 0.4))
        belly_card(c, t, b.start, q["claws"].start, flap, 0.0)
        label(c, "his tail flap", 540, TOP_LABEL_Y, window(t, b.word("tail") - 0.2, b.word("round") + 0.2, 0.3, 0.3), size=44)
        label(c, "wide and round, like a mother's", 540, TOP_LABEL_Y, window(t, b.word("round") + 0.3, q["claws"].start, 0.3, 0.3), size=40)

    tl.add(s_body, q["body"].start, q["claws"].start, transition="cut")

    # ---------------------------------------------------------- 9. small claws; the wide flap shelters the sac
    def s_claws(c, t, ctx):
        cl = q["claws"]
        t_sci = cl.word("Scientists") - 0.2
        if t < t_sci:
            k = ease(prog(t, cl.start, t_sci))
            cam = framed(lerp(1.15, 1.3, k), KX, KY - 20)
            c.save()
            cam.apply(c)
            shore(c, t)
            kiwi.draw(c, st, KX, KY, KS, phase=t, blink=blinking(t, 0.6), happy=0.4, claw=0.72, raise_=0.6,
                      pinch=0.5, sac=lambda cc: sac_under(cc, t, eggs=0.0, happy=0.3))
            c.restore()
            sx, sy = cam.screen(KX + 150, KY - 50)
            tag(c, "small claws", sx, sy, window(t, cl.word("claws") - 0.1, t_sci, 0.3, 0.3))
        else:
            def sac(cc):
                toffee.draw_sac(cc, st, 0, 26, 1.0, eggs=0.0, phase=t * 2, stalk=False, happy=0.3, blink=blinking(t, 1.7))
            belly_card(c, t, t_sci, q["males"].start, 1.0, 0.85, under=sac, push=(1.0, 1.28))
            label(c, "scientists think: the wide flap shelters her", 540, TOP_LABEL_Y, window(t, t_sci + 0.2, q["males"].start, 0.3, 0.3), size=36)

    tl.add(s_claws, q["claws"].start, q["males"].start)

    # ---------------------------------------------------------- 10. tiny males slip in; the sac fills with eggs
    def s_males(c, t, ctx):
        m = q["males"]
        t_fill = m.word("fills") - 0.3
        mk = ease(prog(t, m.start + 0.1, m.word("slip") + 0.4))
        eggs = ease(prog(t, t_fill, m.word("eggs") + 0.4))

        def sac(cc):
            toffee.draw_sac(cc, st, 0, 26, 1.0, eggs=eggs, phase=t * 2, stalk=False, happy=0.5 + 0.4 * eggs,
                            males=ease(prog(t, m.word("slip") - 0.2, m.word("slip") + 0.8)), blink=blinking(t, 1.7))
            # two male larvae swim in from the sides to the opening (local coords of the belly view)
            for i, (x0, y0, x1, y1) in enumerate(((-230, 120, -16, 72), (240, 140, 18, 70))):
                kk = ease(prog(t, m.start + 0.1 + 0.2 * i, m.word("slip") + 0.1 + 0.2 * i))
                if kk < 1:
                    toffee.draw_male(cc, st, lerp(x0, x1, kk), lerp(y0, y1, kk), 0.7, phase=t + i,
                                     ang=math.atan2(y1 - y0, x1 - x0), alpha=1 - ease(prog(kk, 0.85, 1.0)))

        belly_card(c, t, m.start, q["still"].start, 1.0, 0.85, under=sac, push=(1.28, 1.42))
        label(c, "tiny males", 540, TOP_LABEL_Y, window(t, m.word("male") - 0.1, t_fill, 0.3, 0.3), size=44)
        label(c, "Toffee's eggs", 540, TOP_LABEL_Y, window(t, t_fill + 0.2, q["still"].start, 0.3, 0.3), size=44)

    tl.add(s_males, q["males"].start, q["still"].start, transition="cut")

    # ---------------------------------------------------------- 11. still a boy; behaves like a mother
    def s_still(c, t, ctx):
        s_ = q["still"]
        k = ease(prog(t, s_.start, q["care"].start))
        cam = framed(lerp(1.3, 1.2, k), KX, KY)
        c.save()
        cam.apply(c)
        shore(c, t)
        kiwi.draw(c, st, KX, KY, KS, phase=t, blink=blinking(t, 0.6), happy=0.6, claw=0.72, pinch=0.3,
                  sac=lambda cc: sac_under(cc, t, eggs=1.0, happy=0.6))
        c.restore()
        label(c, "still a boy", 540, TOP_LABEL_Y, window(t, s_.word("boy") - 0.3, s_.word("But") - 0.1, 0.3, 0.3), size=44)
        label(c, "but he behaves like a mother", 540, TOP_LABEL_Y, window(t, s_.word("behaves") - 0.2, q["care"].start, 0.3, 0.3), size=40)

    tl.add(s_still, q["still"].start, q["care"].start)

    # ---------------------------------------------------------- 12. he cleans the sac, guards it
    def s_care(c, t, ctx):
        cr = q["care"]
        cam = framed(1.3, KX, KY + 20)
        clean = window(t, cr.word("cleans") - 0.2, cr.word("guards") - 0.2, 0.3, 0.3)
        guard = ease(prog(t, cr.word("guards") - 0.2, cr.word("guards") + 0.5))
        c.save()
        cam.apply(c)
        shore(c, t)
        # cleaning: he rocks and brushes with his claws (pinch opens and closes); guarding: claws up
        rock_ = 0.05 * math.sin(t * 7) * clean
        kiwi.draw(c, st, KX, KY, KS, ang=rock_, phase=t, blink=blinking(t, 0.6), happy=0.8, claw=0.72,
                  pinch=0.5 + 0.5 * math.sin(t * 9) * clean, raise_=guard * 0.85,
                  sac=lambda cc: sac_under(cc, t, eggs=1.0, happy=0.7))
        c.restore()
        sx, sy = cam.screen(KX, KY + 130)
        if clean > 0:
            sparkles(c, sx - 40, sy, t, cr.word("cleans") + 0.1, n=6, r=70)
            sparkles(c, sx + 50, sy + 10, t, cr.word("cleans") + 0.7, n=6, r=70)
        label(c, "like his own eggs", 540, TOP_LABEL_Y, window(t, cr.word("treats") - 0.1, q["launch"].start, 0.3, 0.3), size=40)

    tl.add(s_care, q["care"].start, q["launch"].start)

    # ---------------------------------------------------------- 13. the launch: up the rock, bob and fan
    def climb_pos(t):
        la = q["launch"]
        k = ease(prog(t, la.word("climbs") - 0.3, la.word("high") + 0.4))
        # a curved path from the sand up the rock's left face to its top
        x = lerp(KX, ROCK_TOP[0] - 30, k)
        y = lerp(KY, ROCK_TOP[1] - 112 * KS, k) - 60 * math.sin(k * math.pi)
        return x, y, k

    def bob_fan(t):
        la = q["launch"]
        b = window(t, la.word("bobs") - 0.2, q["cloud"].end, 0.3, 0.6)
        return b

    def s_launch(c, t, ctx):
        x, y, k = climb_pos(t)
        b = bob_fan(t)
        cam = framed(lerp(1.3, 1.05, ease(prog(t, q["launch"].start, q["launch"].word("high")))), lerp(KX, 620, k), lerp(KY, 1120, k))
        c.save()
        cam.apply(c)
        shore(c, t)
        bobbing = 18 * math.sin(t * 5.5) * b
        kiwi.draw(c, st, x, y + bobbing, KS, ang=0.06 * math.sin(t * 5.5) * b - 0.12 * k * (1 - k) * 4,
                  phase=t * (1 + 2 * (1 - k)), walk=1.0 - k, blink=blinking(t, 0.6), happy=0.6, claw=0.72,
                  raise_=0.5 + 0.5 * math.sin(t * 5.5 + 1) * b if b > 0 else 0.0, pinch=0.4,
                  sac=lambda cc: sac_under(cc, t, eggs=1.0, happy=0.8))
        c.restore()
        sx, sy = cam.screen(x, y - 160)
        label(c, "bobbing and fanning, like a mother hatching her eggs", 540, TOP_LABEL_Y, window(t, q["launch"].word("bobs") - 0.1, q["burst"].end, 0.3, 0.3), size=32)

    tl.add(s_launch, q["launch"].start, q["burst"].start)

    # ---------------------------------------------------------- 14. the burst + 15. the cloud
    def larvae(c, t, t0, x, y, n=90, seed=3, up=520, spread=420, life=4.5, s=0.9):
        """A cloud of hatchlings streaming out of the sac and drifting up and away."""
        r = rng(seed)
        for i in range(n):
            st_ = t0 + r.uniform(0, 1.6)
            k = (t - st_) / life
            if k < 0 or k > 1:
                continue
            ax, ay = r.uniform(-spread, spread), r.uniform(-up, -up * 0.3)
            # out of the opening first (sideways and a little down), then up and away around the crab
            px = x + ax * ease_out(k) + 14 * math.sin(t * 3 + i)
            py = y + 60 * math.sin(min(1.0, k * 3) * math.pi / 2) * (1 - k) + ay * ease(k) - 40 * k
            toffee.draw_nauplius(c, st, px, py, s * (0.7 + 0.3 * r.random()), phase=t + i, ang=r.uniform(-1.2, 1.2),
                                 alpha=min(1.0, (1 - k) * 2.5))

    def s_burst(c, t, ctx):
        x, y, k = climb_pos(t)
        b = bob_fan(t)
        cam = framed(1.05, 620, 1120)
        c.save()
        cam.apply(c)
        shore(c, t)
        hatch = window(t, q["burst"].start - 0.1, q["cloud"].word("barnacles"), 0.2, 0.8)
        larvae(c, t, q["burst"].start, x, y + 150 * KS)
        kiwi.draw(c, st, x, y + 18 * math.sin(t * 5.5) * b, KS, ang=0.06 * math.sin(t * 5.5) * b, phase=t,
                  blink=blinking(t, 0.6), happy=0.9, claw=0.72, raise_=0.5 + 0.5 * math.sin(t * 5.5 + 1) * b, pinch=0.4,
                  sac=lambda cc: sac_under(cc, t, eggs=1.0 - 0.8 * ease(prog(t, q["burst"].start, q["cloud"].end)),
                                           happy=0.9, hatch=hatch))
        bg.bubbles(c, t, x, y + 150, n=10, seed=4, spread=60, speed=150, life=2.5, t0=q["burst"].start)
        c.restore()
        label(c, "off to find crabs of their own", 540, TOP_LABEL_Y, window(t, q["cloud"].word("off") - 0.1, q["turn"].start, 0.3, 0.3), size=40)

    tl.add(s_burst, q["burst"].start, q["turn"].start)

    # ---------------------------------------------------------- 16. the turn: food, babies, hers
    def s_turn(c, t, ctx):
        tu = q["turn"]
        k = ease(prog(t, tu.start, q["end"].start))
        cam = framed(lerp(1.1, 1.3, k), KX, KY - 20)
        food = window(t, tu.word("food") - 0.5, tu.word("whole") - 0.2, 0.4, 0.4)
        c.save()
        cam.apply(c)
        shore(c, t)

        def roots(cc):
            cc.set_source_rgba(*hexc("#f4d9cc")[:3], 0.55)
            cc.paint()
            toffee.draw_roots(cc, st, SPOT[0], SPOT[1], 1.0, grow=1.0, seed=1, arms=6, length=105, width=7.5)

        kiwi.draw(c, st, KX, KY, KS, phase=t, blink=blinking(t, 0.6), happy=0.4, claw=0.72,
                  xray=roots, xray_alpha=0.95 * food,
                  sac=lambda cc: sac_under(cc, t, eggs=ease(prog(t, tu.word("babies") - 0.3, tu.word("hers"))), happy=0.6))
        c.restore()
        sx, sy = cam.screen(KX, KY + 190)
        if t > tu.word("hers"):
            sparkles(c, sx, sy, t, tu.word("hers"), n=8, r=110)
        label(c, "his food", 540, TOP_LABEL_Y, food, size=44)
        label(c, "his job: making babies", 540, TOP_LABEL_Y, window(t, tu.word("whole") - 0.1, tu.word("hers") - 0.2, 0.3, 0.3), size=40)
        label(c, "...now hers", 540, TOP_LABEL_Y, window(t, tu.word("hers") - 0.1, q["end"].start, 0.3, 0.3), size=44)

    tl.add(s_turn, q["turn"].start, q["end"].start)

    # ---------------------------------------------------------- 17. brood after brood + 18. for life
    def s_end_lines(c, t, ctx):
        e = q["end"]
        li = q["life"]
        k = ease(prog(t, e.start, li.end))
        cam = framed(lerp(1.3, 1.15, k), KX, KY - 10)
        # the sac empties and refills, twice, during "brood after brood"
        cyc = (t - e.start) / max(0.1, (li.start - e.start)) * 2.0
        eggs = 0.5 + 0.5 * math.cos(cyc * TAU) if e.start <= t < li.start else 1.0
        c.save()
        cam.apply(c)
        shore(c, t)

        def roots(cc):
            cc.set_source_rgba(*hexc("#f4d9cc")[:3], 0.55)
            cc.paint()
            toffee.draw_roots(cc, st, SPOT[0], SPOT[1], 1.0, grow=1.0, seed=1, arms=6, length=105, width=7.5)

        if e.start <= t < li.start:
            larvae(c, t, e.start + 0.4, KX, KY + 150 * KS, n=40, seed=5, up=400, spread=300, life=3.0, s=0.8)
        kiwi.draw(c, st, KX, KY, KS, phase=t, blink=blinking(t, 0.6), happy=0.7, claw=0.72,
                  xray=roots, xray_alpha=0.7 * ease(prog(t, li.word("part") - 0.2, li.word("him") + 0.3)),
                  sac=lambda cc: sac_under(cc, t, eggs=eggs, happy=0.7))
        c.restore()
        label(c, "brood after brood", 540, TOP_LABEL_Y, window(t, e.word("Brood") - 0.1, li.start, 0.3, 0.3), size=44)
        label(c, "for the rest of his life", 540, TOP_LABEL_Y, window(t, li.start, li.end + 0.6, 0.3, 0.3), size=44)

    tl.add(s_end_lines, q["end"].start, q["life"].end + 0.5)

    # ---------------------------------------------------------- 19. the end card
    def s_end(c, t, ctx):
        from engine import text as tx
        t0 = q["life"].end + 0.15
        c.save()
        c.translate(0, ctx.get("lift", 170))
        paint(c, bg.parchment())
        z = lerp(0.97, 1.02, ease(prog(t, t0, DUR)))
        c.translate(540, 900)
        c.scale(z, z)
        c.translate(-540, -900)
        ta = ease(prog(t, t0, t0 + 0.4))
        tx.center(c, "Sacculina carcini", 540, 700, 76, INK, alpha=ta, italic=True)
        tx.center(c, "the crab-hacker barnacle", 540, 770, 40, hexc("#8a5a3a"), alpha=ta * 0.9, italic=True)
        tx.center(c, "on the shore crab, Carcinus maenas", 540, 826, 34, hexc("#8a5a3a"), alpha=ta * 0.9, italic=True)
        brand_plate(c, 540, 1000, ease(prog(t, t0 + 0.2, t0 + 0.7)))
        c.restore()

    tl.add(s_end, q["life"].end + 0.5, DUR + 0.1, trans_dur=0.5)

    # ---------------------------------------------------------- audio
    def make_audio(path):
        moods = [(0.0, "curious"), (q["kiwi"].start, "cozy"), (q["toffee"].start, "playful"),
                 (q["land"].start, "mystery"), (q["roots"].start, "quiet"), (q["months"].start, "curious"),
                 (q["body"].start, "wonder"), (q["males"].start, "playful"), (q["still"].start, "cozy"),
                 (q["launch"].start, "wonder"), (q["turn"].start, "mystery"), (q["end"].start, "finale")]
        HEAD = 0.4
        full = music.score(DUR + HEAD + 8.0, moods)
        i0 = int(HEAD * SR)
        bed = full[i0:i0 + int(DUR * SR)]
        fx = Bus(DUR, 5)
        for t0, name, gain in sfx_events(SFX, Q):
            fx.add(t0, sfx.LIB[name](), 0.0, gain)
        for ln in SCRIPT:
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


LOOK = ["teaser", "kiwi", "toffee", "land", "needle", "roots", "fine", "months", "mother", "body", "claws",
        "shelter", "males", "still", "care", "launch", "burst", "turn", "brood", "life", "end"]


def look_times(Q):
    q = Q
    return dict(zip(LOOK, [
        0.0, q["kiwi"].word("Kiwi") + 0.9, q["toffee"].word("barnacle") + 0.3, q["land"].word("spot") + 0.3,
        q["needle"].word("injects") + 0.4, q["roots"].word("body") + 0.6, q["fine"].word("babies") + 0.3,
        q["months"].word("flap") + 0.2, q["months"].word("mother") + 0.6, q["body"].word("round") + 0.5,
        q["claws"].word("small") + 0.3, q["claws"].word("shelters") + 0.3, q["males"].word("eggs") + 0.3,
        q["still"].word("behaves") + 0.4, q["care"].word("guards") + 0.5, q["launch"].word("bobs") + 0.3,
        q["burst"].start + 0.9, q["turn"].word("hers") + 0.4, q["end"].word("Brood") + 0.4,
        q["life"].word("him") + 0.2, q["life"].end + 2.2]))


def key_times(Q):
    return list(look_times(Q).values())


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
        out = os.path.join(os.path.dirname(os.path.dirname(HERE)), "for-review", "e004_look_frames")
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
