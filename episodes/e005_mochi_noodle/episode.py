"""Episode 005 — Mochi, Pip & Noodle: the flea tapeworm Dipylidium caninum, a cat flea and a cat.

Three settings, one continuous camera each (judge lessons): Mochi's room (cushion), down in the cushion's
fibres (magnified), inside Mochi's gut (magnified). The lens is the device for anything too small to see in
the room: it shows the same world, zoomed, so what is inside it moves with the story.
Run:
    .venv/Scripts/python -m episodes.e005_mochi_noodle.episode look                 # look frames for the owner
    .venv/Scripts/python -m episodes.e005_mochi_noodle.episode stills --style illustrated
    .venv/Scripts/python -m episodes.e005_mochi_noodle.episode render --style illustrated
"""
import argparse
import math
import os
import shutil

import cairo
import numpy as np

from characters import mochi, noodle, pip
from engine import backgrounds as bg
from engine import render
from engine import style as styles
from engine.audio import mix, music, sfx
from engine.audio.common import SR, Bus
from engine.core import TAU, back_out, clamp, ease, ellipse, hexc, lerp, prog, rng, window
from engine.scene import Timeline, label, leader, soft_bubble, sparkles, tag
from engine.voice import narrate, sfx_events
from episodes.e002_roly_mango.episode import Cam, blinking, brand_plate, paint
from episodes.e003_biscuit_dilly.episode import framed, lens
from episodes.e005_mochi_noodle.script import SCRIPT, SFX

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "005-mochi-pip-and-noodle"
INK = hexc("#3a2a1a")

# Mochi on her cushion (world coords; scenes are drawn STAGE_LIFT=170 higher on screen). Ground under her belly.
KX, KY = 500, bg.CUSHION_Y + 6
MS = 1.25
# Scene coordinates are screen + 170. Safe zone in scene coords: x 60..900, y 370..1630.
TOP_LABEL_Y = 560


def to_w(lx, ly):
    return KX + lx * MS, KY + ly * MS


GRAIN = to_w(-196, -128)          # where the segment sits on her fur (her hip, near the tail root)
BACK = to_w(*mochi.BACK_SPOT)     # where Pip lands and where her tongue reaches


def drift(t, x, y, ax=10, ay=6, sp=0.7):
    return x + ax * math.sin(t * sp), y + ay * math.sin(t * sp * 1.37 + 1.1)


def ruler(c, x, y, length, alpha=1.0, cm=30):
    """A plain wooden school ruler, `cm` centimetres long, laid from (x, y) to the right."""
    if alpha <= 0:
        return
    c.save()
    c.push_group()
    h = 54
    c.rectangle(x, y, length, h)
    c.set_source_rgba(*hexc("#e8c78e"))
    c.fill_preserve()
    c.set_source_rgba(*hexc("#8a6a3a"))
    c.set_line_width(3)
    c.stroke()
    for i in range(cm + 1):
        tx = x + length * i / cm
        tl = 22 if i % 5 == 0 else 12
        c.move_to(tx, y)
        c.line_to(tx, y + tl)
        c.set_source_rgba(*hexc("#5a4022"))
        c.set_line_width(2)
        c.stroke()
    from engine import text as tx_
    for i in (0, 10, 20, 30):
        if i <= cm:
            tx_.center(c, str(i), x + length * i / cm, y + 46, 18, hexc("#5a4022"))
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()


def build(style_name):
    st = styles.get(style_name)
    TEASER = 1.35
    track, Q, caps, end = narrate(SCRIPT, os.path.join(HERE, "voice_cache"), t0=TEASER + 0.15)
    DUR = end + 4.9                      # end card fully readable >= 4 s
    tl = Timeline(DUR, captions=caps)
    ctx = {"style": st, "vignette": bg.vignette(), "watermark": True, "fade_in": 0.0}
    q = Q

    # ------------------------------------------------------------------ Mochi's pose over the whole story
    LICK0 = q["itch"].word("licks") - 0.5
    SWAL = q["swallow"].word("swallows")

    def mochi_pose(t):
        """One continuous performance for every room shot: asleep -> awake for her intro -> dozing ->
        itch: ear flick, turn, lick the spot on her back -> swallow -> back to sleep."""
        awake = window(t, q["mochi"].start - 0.2, q["dry"].start, 0.5, 0.8)
        itch_wake = window(t, q["itch"].start - 0.2, q["swallow"].end + 0.6, 0.3, 0.8)
        eyes = max(awake, 0.75 * itch_wake)
        if blinking(t, 0.4, 3.3):
            eyes = min(eyes, 0.1)
        turn = ease(prog(t, LICK0 - 0.9, LICK0)) * (1 - ease(prog(t, SWAL + 0.5, SWAL + 1.5)))
        licking = window(t, LICK0, SWAL + 0.3, 0.2, 0.3)
        ph = max(0.0, math.sin((t - LICK0) * 7.5))
        lick = licking * (0.55 + 0.45 * ph)
        if licking > 0.2:
            eyes = 0.08
        flicks = (q["itch"].start, q["dry"].start + 1.0, q["warm"].start + 1.2, q["warm"].end - 0.4,
                  q["leave"].end + 0.2, q["cycle"].start + 0.8, q["cycle"].word("Pip") + 0.2)
        ear = sum(0.7 * math.sin(t * 10) * window(t, f, f + 0.5, 0.05, 0.1) for f in flicks)
        stir = window(t, q["cycle"].word("Waiting") - 0.2, q["cycle"].end + 0.8, 0.4, 0.6)   # half-opens an eye
        eyes = max(eyes, 0.45 * stir if not blinking(t, 0.4, 3.3) else 0.0)
        tail = t * 1.7 + 0.8 * math.sin(t * 0.37)
        # the swallow (judge pass 1): eyes shut, a chin dip on the gulp, then a lick of the lips, content
        gulp = window(t, SWAL + 0.1, SWAL + 0.7, 0.15, 0.3)
        lick += 0.45 * gulp
        lips = window(t, SWAL + 1.5, SWAL + 2.2, 0.15, 0.2)
        tng = licking * ph + 0.5 * lips * max(0.0, math.sin((t - SWAL - 1.5) * 9))
        after = window(t, SWAL + 0.1, q["swallow"].end + 0.6, 0.2, 0.6)
        if after > 0.3:
            eyes = 0.0
        return dict(eyes=eyes, turn=turn, lick=lick, tongue=tng, tail=tail, breathe=math.sin(t * 1.8),
                    ear=ear, happy=max(0.6 * awake, 0.8 * after))

    # ------------------------------------------------------------------ room camera (ONE shot, keyframed)
    GX, GY = GRAIN
    RKEYS = [
        (0.0, 1.06, 540, GY - 40),
        (q["mochi"].start, 1.0, 540, 1080),                     # all of Mochi for her intro
        (q["grain"].start, 1.0, 540, 1080),
        (q["dry"].start, 1.08, 520, GY),
        (q["dry"].end, 1.08, 520, GY),
        (q["warm"].start, 1.1, BACK[0] + 60, BACK[1] + 40),
        (q["swallow"].end, 1.1, BACK[0] + 60, BACK[1] + 40),
        (q["leave"].start + 0.5, 1.08, 520, GY),
        (q["cycle"].end + 2.0, 1.08, 520, GY),
    ]

    def room_cam(t):
        for (t0, z0, x0, y0), (t1, z1, x1, y1) in zip(RKEYS, RKEYS[1:]):
            if t < t1:
                k = ease(prog(t, t0, t1))
                return framed(lerp(z0, z1, k), lerp(x0, x1, k), lerp(y0, y1, k))
        _, z0, x0, y0 = RKEYS[-1]
        return framed(z0, x0, y0)

    def room(c, t, cam, extra=None):
        c.save()
        cam.apply(c)
        paint(c, bg.room())
        bg.motes(c, t, n=24, y0=360, y1=1200, seed=4, col=(1, 0.97, 0.88), a=0.35)
        mochi.draw(c, st, KX, KY, MS, **mochi_pose(t))
        if extra:
            extra(c)
        c.restore()

    def zoom_world(cc, cx, cy, z, sx, sy, t, extra=None):
        """Draw the room world again inside a lens: world point (cx, cy) at screen (sx, sy), zoom z."""
        cc.save()
        cc.translate(sx, sy)
        cc.scale(z, z)
        cc.translate(-cx, -cy)
        paint(cc, bg.room())
        mochi.draw(cc, st, KX, KY, MS, **mochi_pose(t))
        if extra:
            extra(cc)
        cc.restore()

    LENS = (330, 700, 175)            # room lens: upper left, over the wall (scene coords)

    def fur_lens(cc, t, x, y, r, patch=0.0, seed=1):
        """What the lens sees on Mochi: a close-up of her fur (soft cream strands, a caramel patch edge)."""
        rnd = rng(seed)
        cc.set_source_rgba(*hexc("#f2e2cc"))
        cc.paint()
        px0, py0, prx, pry = x - r * 0.7, y - r * 0.9, r * 1.1, r * 0.8
        if patch > 0:
            ellipse(cc, px0, py0, prx, pry, 0.3)
            cc.set_source_rgba(*hexc("#dca066")[:3], 0.85 * patch)
            cc.fill()
        cc.set_line_cap(cairo.LINE_CAP_ROUND)
        for i in range(150):
            px, py = x + rnd.uniform(-r, r), y + rnd.uniform(-r, r)
            sway = 3 * math.sin(t * 1.3 + i)
            L = rnd.uniform(26, 46)
            cc.move_to(px, py)
            cc.curve_to(px - L * 0.3, py - L * 0.2, px - L * 0.6 + sway, py - L * 0.45, px - L * 0.8 + sway, py - L * 0.75)
            tone = rnd.random()
            in_patch = patch > 0 and (px - px0) ** 2 / prx ** 2 + (py - py0) ** 2 / pry ** 2 < 1
            col = hexc("#c98a4c") if in_patch else (hexc("#fffaf2") if tone > 0.5 else hexc("#d9c3a6"))
            cc.set_source_rgba(*col[:3], 0.55)
            cc.set_line_width(rnd.uniform(2.5, 4.5))
            cc.stroke()

    def lens_seg(cc, t, x, y, s, dry=0.0, split=0.0, ripe=True):
        """A segment at lens scale: inches along (stretch + squeeze), dries into a grain, splits open."""
        cc.save()
        cc.translate(x + 6 * math.sin(t * 1.6), y)
        cc.rotate(-0.35 + 0.05 * math.sin(t * 1.6))
        stretch = 1 + 0.16 * math.sin(t * 3.2) * (1 - dry)
        # sized by its own l/w (not by scaling the context), so the ink stays a normal line width
        L = 24 * s * stretch * lerp(1.0, 0.62, dry)
        Wd = 15 * s / math.sqrt(stretch) * lerp(1.0, 0.8, dry)
        if split <= 0:
            noodle.draw_segment(cc, st, L, Wd, ripe and dry < 0.5, seed=7)
            if dry > 0:     # a harder, yellower grain
                noodle._seed_shape(cc, L, Wd)
                cc.set_source_rgba(*hexc("#e9d08a")[:3], 0.5 * dry)
                cc.fill()
        else:
            for d in (-1, 1):
                cc.save()
                cc.translate(d * 0.2 * L * split, d * 0.06 * L * split)
                cc.rotate(d * 0.35 * split)
                cc.rectangle(-L if d < 0 else 0, -Wd, L, 2 * Wd)
                cc.clip()
                noodle.draw_segment(cc, st, L, Wd, False, seed=7)
                noodle._seed_shape(cc, L, Wd)
                cc.set_source_rgba(*hexc("#e9d08a")[:3], 0.5)
                cc.fill()
                cc.restore()
        cc.restore()

    def lens_packets(cc, t, t0, x, y, n=4):
        for i in range(n):
            k = max(0.0, t - t0 - i * 0.2)
            if k <= 0:
                continue
            px = x + (i - 1.5) * 26 + 20 * math.sin(k * 3 + i)
            py = y + 10 + k * k * 260
            noodle.draw_egg_packet(cc, st, px, py, 16, alpha=clamp(1.8 - k * 0.6), seed=i + 2)

    def tongue(cc, x, y, k, reach):
        """Her tongue sweeping through the lens from the right (k = sweep 0..1, reach 0..1)."""
        if reach <= 0:
            return
        tx = lerp(x + 260, x - 140, k)
        cc.save()
        cc.translate(tx, y + 20)
        cc.rotate(-0.25)
        w = 120 * reach
        cc.move_to(0, -w * 0.45)
        cc.curve_to(-w * 0.6, -w * 0.5, -w * 0.8, w * 0.3, -w * 0.3, w * 0.45)
        cc.curve_to(w * 0.4, w * 0.6, w * 2.5, w * 0.4, w * 3, w * 0.2)
        cc.line_to(w * 3, -w * 0.4)
        cc.close_path()
        g = cairo.LinearGradient(-w, -w * 0.5, -w, w * 0.5)
        g.add_color_stop_rgba(0, *hexc("#f4a3ad"))
        g.add_color_stop_rgba(1, *hexc("#d9707e"))
        cc.set_source(g)
        cc.fill()
        for i in range(14):   # the papillae that make a cat tongue rough
            ellipse(cc, -w * 0.3 + i * w * 0.2, (i % 3 - 1) * w * 0.15, 3, 2)
            cc.set_source_rgba(1, 0.85, 0.85, 0.6)
            cc.fill()
        cc.restore()

    def segment_on_fur(cc, t, x, y, s, dry=0.0, split=0.0, eggs=1.0):
        """The fresh segment (cucumber-seed shape) inching on her fur; dries into a rice grain."""
        wig = t * 3.2
        cc.save()
        cc.translate(x + 3 * math.sin(t * 1.6), y)
        cc.rotate(-0.25 + 0.06 * math.sin(t * 1.6))
        stretch = 1 + 0.16 * math.sin(wig) * (1 - dry)
        cc.scale(s * stretch * lerp(1.0, 0.55, dry), s / math.sqrt(stretch) * lerp(1.0, 0.75, dry))
        if split <= 0:
            noodle.draw_segment(cc, st, 24, 15, eggs > 0.5, seed=7)
        else:
            for d in (-1, 1):
                cc.save()
                cc.translate(d * 6 * split, d * 2 * split)
                cc.rotate(d * 0.3 * split)
                cc.rectangle(-20 if d < 0 else 0, -12, 20, 24)
                cc.clip()
                noodle.draw_segment(cc, st, 24, 15, False, seed=7)
                cc.restore()
        cc.restore()

    def packets_fall(cc, t, t0, x, y, s, n=4):
        """Egg packets tumbling out of the split grain, down off her fur."""
        for i in range(n):
            k = max(0.0, t - t0 - i * 0.18)
            if k <= 0:
                continue
            px = x + (i - 1.5) * 9 * s + 12 * s * math.sin(k * 3 + i)
            py = y + k * k * 160 * s
            noodle.draw_egg_packet(cc, st, px, py, 4.5 * s, alpha=clamp(1.6 - k * 0.5), seed=i + 2)

    # ---------------------------------------------------------- 0. teaser + hook (frame 0 is the thumbnail)
    def s_hook(c, t, ctx):
        cam = room_cam(t)
        room(c, t, cam)
        lx, ly, lr = LENS

        def inner(cc):
            fur_lens(cc, t, lx, ly, lr, patch=1.0)
            lens_seg(cc, t, lx + 10, ly + 10, 7.0)
        a = 1.0
        sx, sy = cam.screen(GX, GY)
        leader(c, lx + lr * 0.55, ly + lr * 0.7, sx, sy, 0.8 * a)
        lens(c, lx, ly, lr, inner, a)
        fade = (1 - ease(prog(t, q["hook"].start - 0.2, q["hook"].start + 0.3))) * ctx.get("teaser_labels", 1.0)
        label(c, "Rice... that moves?", 540, TOP_LABEL_Y - 120, fade, size=50)

    tl.add(s_hook, 0.0, q["mochi"].start + 0.5, trans_dur=0.3)

    # ---------------------------------------------------------- 1. meet Mochi
    def s_mochi(c, t, ctx):
        cam = room_cam(t)
        room(c, t, cam)
        hx, hy = cam.screen(*to_w(212, -330))
        tag(c, "Mochi", min(hx, 760), hy, window(t, q["mochi"].word("Mochi") + 0.1, q["grain"].start, 0.3, 0.3),
            sub="this cushion is hers")

    tl.add(s_mochi, q["mochi"].start, q["grain"].start, transition="cut")

    # ---------------------------------------------------------- 2. the grain is a tapeworm segment
    def s_grain(c, t, ctx):
        cam = room_cam(t)
        room(c, t, cam)
        lx, ly, lr = LENS
        z = lerp(7.0, 8.5, ease(prog(t, q["grain"].start, q["grain"].word("tapeworm"))))

        def inner(cc):
            fur_lens(cc, t, lx, ly, lr, patch=1.0)
            lens_seg(cc, t, lx + 10, ly + 10, z)
        a = window(t, q["grain"].start - 0.3, q["dry"].start + 0.2, 0.35, 0.3)
        sx, sy = cam.screen(GX, GY)
        leader(c, lx + lr * 0.55, ly + lr * 0.7, sx, sy, 0.8 * a)
        lens(c, lx, ly, lr, inner, a)
        label(c, "about 1 cm long", lx, ly + lr + 60, window(t, q["grain"].word("piece") - 0.1, q["dry"].start, 0.3, 0.3),
              size=36)

    tl.add(s_grain, q["grain"].start, q["dry"].start, transition="cut")

    # ---------------------------------------------------------- 3. it dries and breaks open; packets spill
    SPILL = q["dry"].word("spill")

    def s_dry(c, t, ctx):
        cam = room_cam(t)
        d = q["dry"]
        dry = ease(prog(t, d.start, d.word("breaks")))
        split = ease(prog(t, d.word("breaks"), d.word("breaks") + 0.5))
        room(c, t, cam)
        lx, ly, lr = LENS

        def inner(cc):
            fur_lens(cc, t, lx, ly, lr, patch=1.0)
            lens_seg(cc, t, lx + 10, ly + 10, 8.5, dry=dry, split=split)
            if t > d.word("breaks") + 0.3:
                lens_packets(cc, t, d.word("breaks") + 0.3, lx + 10, ly + 10)
        sx, sy = cam.screen(GX, GY)
        leader(c, lx + lr * 0.55, ly + lr * 0.7, sx, sy, 0.8)
        lens(c, lx, ly, lr, inner, 1.0)
        label(c, "dried: hard, like rice", lx, ly + lr + 60, window(t, d.start + 0.2, SPILL - 0.1, 0.3, 0.3), size=36)
        label(c, "egg packets", lx, ly + lr + 60, window(t, SPILL, d.end + 0.6, 0.3, 0.3), size=36)

    tl.add(s_dry, q["dry"].start, q["dry"].end + 0.7, transition="cut")   # covers the iris (0.6 s)

    # ---------------------------------------------------------- down in the cushion: ONE shot, keyframed
    BKEYS = [
        (q["dry"].end, 1.0, 540, 1000),
        (q["pip"].start + 0.5, 1.3, 460, 1140),
        (q["eats"].word("egg") - 0.3, 1.55, 520, 1170),           # in on the egg
        (q["inside"].start, 1.55, 520, 1170),
        (q["inside"].end, 1.95, 470, 1190),                       # in on the glowing young worm
        (q["cocoon"].start + 0.3, 1.35, 480, 1120),
        (q["jump"].end + 0.3, 1.1, 480, 1000),
    ]

    def bed_cam(t):
        for (t0, z0, x0, y0), (t1, z1, x1, y1) in zip(BKEYS, BKEYS[1:]):
            if t < t1:
                k = ease(prog(t, t0, t1))
                return framed(lerp(z0, z1, k), lerp(x0, x1, k), lerp(y0, y1, k))
        _, z0, x0, y0 = BKEYS[-1]
        return framed(z0, x0, y0)

    PACKET = (640, bg.FIBRE_Y - 6)           # the egg packet Pip eats
    EAT = q["eats"].word("egg")
    LARVA_S = 0.9

    def larva_x(t):
        # crawls in from the left, stops with his head at the packet
        x = lerp(330, PACKET[0] - 40, ease(prog(t, q["pip"].start - 0.6, EAT - 0.2)))   # on screen (pass 1)
        return x + 90 * ease(prog(t, EAT + 0.6, q["cocoon"].start))

    def packets_in_bed(c, t):
        """The packets that fell from the grain settle on the fibres."""
        t0 = q["dry"].end - 0.3
        for i, (x, y) in enumerate(((PACKET[0], PACKET[1]), (380, 1230), (820, 1236), (250, 1250))):
            k = ease(prog(t, t0 + i * 0.25, t0 + i * 0.25 + 1.6))
            yy = lerp(300, y, k)
            xx = x + 30 * math.sin((1 - k) * 4 + i)
            if i == 0 and t > EAT + 0.25:
                continue                                          # eaten
            # about crumb size (pass 1: real packets are 0.12-0.2 mm against a 2-5 mm larva); the one he eats glints
            if i == 0 and k >= 1:
                glint = 0.5 + 0.5 * math.sin(t * 5)
                c.arc(xx, yy, 24 + 4 * glint, 0, TAU)
                c.set_source_rgba(1, 0.95, 0.7, 0.18 + 0.12 * glint)
                c.fill()
            noodle.draw_egg_packet(c, st, xx, yy, 16 if i == 0 else 11, seed=3 + i)

    def s_bed(c, t, ctx):
        cam = bed_cam(t)
        c.save()
        cam.apply(c)
        paint(c, bg.bedding())
        bg.motes(c, t, n=30, y0=300, y1=1200, seed=9, col=(1, 0.96, 0.85), a=0.4)
        packets_in_bed(c, t)
        cocoon_k = ease(prog(t, q["cocoon"].start, q["cocoon"].word("comes")))
        opened = ease(prog(t, q["cocoon"].word("grown") - 0.2, q["cocoon"].word("grown") + 0.4))
        lx = larva_x(t)
        ly = bg.FIBRE_Y - 22
        if opened < 0.5:
            munch = (t - EAT + 0.6) if EAT - 0.6 < t < EAT + 0.6 else (t * 0.7 if t < EAT else 0.0)

            def gut_xray(cc, spine):
                a = window(t, q["inside"].start, q["cocoon"].start + 0.3, 0.4, 0.4)
                if a <= 0:
                    return
                k = ease(prog(t, q["inside"].word("hatches"), q["inside"].word("slips") + 0.6))
                i = int(lerp(1, 5, k))
                gx, gy = spine[i]
                gy = gy + lerp(0, -10, k)
                noodle.draw_cyst(cc, st, gx, gy, lerp(5, 9, k), alpha=a, glow=1.0)
            fade_in = ease(prog(t, q["pip"].start - 0.6, q["pip"].start))
            pip.draw_larva(c, st, lx, ly, LARVA_S, phase=t * 2.2 if t < EAT else t * 0.8, munch=munch,
                           blink=blinking(t, 0.3), gut=gut_xray, alpha=fade_in * (1 - cocoon_k * 0.8))
        pip.draw_cocoon(c, st, lx - 170 * LARVA_S, ly + 6, 0.62, cocoon_k, opened=opened)
        if opened > 0.3:                                          # the grown-up flea, then the jump
            j = q["jump"]
            crouch = window(t, j.start - 0.5, j.start + 0.1, 0.3, 0.05)
            up = ease(prog(t, j.start + 0.05, j.start + 0.8))
            px = lx - 170 * LARVA_S + 40 * up
            py = ly + 14 - 1200 * up * up
            pip.draw(c, st, px, py, 0.55, ang=-0.4 * up, phase=t * 3, crouch=crouch, blink=blinking(t, 0.7),
                     happy=0.6, alpha=min(1.0, (opened - 0.3) * 3))
        c.restore()
        # tags and labels (screen space, after restore)
        sx, sy = cam.screen(lx - 60, ly - 50)
        tag(c, "Pip", clamp(sx, 200, 780), sy, window(t, max(q["pip"].word("Pip") + 0.1, q["pip"].start + 0.1),
                                                   q["eats"].start, 0.3, 0.3),
            sub="a flea larva: no legs yet")
        fx, fy = cam.screen(300, bg.FIBRE_Y + 40)
        label(c, "most crumbs: dried flea droppings", 480, TOP_LABEL_Y + 40,
              window(t, q["eats"].word("crumbs") - 0.1, EAT - 0.1, 0.3, 0.3), size=36)
        # x-ray lens over his middle: the egg hatches, the six-hooked young worm wriggles out and slips through
        # the gut wall (pass 1: a 10 px ring didn't read)
        hl = window(t, q["inside"].start - 0.2, q["cocoon"].start + 0.2, 0.35, 0.3)
        if hl > 0:
            HX, HY, HR = 560, 790, 175     # clear of the watermark badge; its tag sits at y ~600
            gx_, gy_ = cam.screen(lx - 110 * LARVA_S, ly)
            hatch = ease(prog(t, q["inside"].word("hatches"), q["inside"].word("hatches") + 0.6))
            move = ease(prog(t, q["inside"].word("slips") - 0.1, q["inside"].word("waits")))

            def inner(cc):
                cc.set_source_rgba(*hexc("#f3dcc4"))
                cc.paint()
                cc.move_to(HX - HR, HY + 40)                 # the larva's gut wall, a soft band across the lens
                cc.curve_to(HX - 60, HY + 10, HX + 60, HY + 70, HX + HR, HY + 40)
                cc.set_source_rgba(*hexc("#b8805e")[:3], 0.95)
                cc.set_line_width(30)
                cc.stroke_preserve()
                cc.set_source_rgba(*hexc("#e2b494")[:3], 1.0)
                cc.set_line_width(18)
                cc.stroke()
                ex_, ey_ = HX - 40, HY - 30
                for d in (-1, 1):                             # the egg shell, splitting
                    cc.save()
                    cc.translate(ex_ + d * 34 * hatch, ey_ - 12 * hatch)
                    cc.rotate(d * 0.5 * hatch)
                    cc.arc(0, 0, 66, math.pi / 2 if d > 0 else -math.pi / 2, -math.pi / 2 if d > 0 else math.pi / 2)
                    cc.set_source_rgba(*hexc("#e9d7a4")[:3], 0.9 * (1 - move * 0.8))
                    cc.set_line_width(9)
                    cc.stroke()
                    cc.restore()
                ox = lerp(ex_, HX + 50, move) + 6 * math.sin(t * 9) * hatch
                oy = lerp(ey_, HY + 95, move) + 4 * math.sin(t * 7)
                if move < 0.95:
                    cc.arc(ox, oy, 36, 0, TAU)                # the oncosphere and its six hooks
                    cc.set_source_rgba(*hexc("#fff6e2"))
                    cc.fill_preserve()
                    cc.set_source_rgba(*hexc("#5a4022"))
                    cc.set_line_width(3)
                    cc.stroke()
                    for k in range(6):
                        a = math.pi * 0.75 + (k // 2) * 0.35 * (1 if k % 2 else -1) + 0.15 * math.sin(t * 12 + k)
                        cc.move_to(ox + math.cos(a) * 20, oy + math.sin(a) * 20)
                        cc.line_to(ox + math.cos(a) * 34, oy + math.sin(a) * 34)
                        cc.set_line_width(3)
                        cc.stroke()
                if move > 0.6:
                    noodle.draw_cyst(cc, st, HX + 50, HY + 95, 24, alpha=ease(prog(move, 0.6, 1.0)), glow=1.0)
            leader(c, HX + HR * 0.55, HY + HR * 0.7, gx_, gy_, 0.8 * hl)
            lens(c, HX, HY, HR, inner, hl)
            tag(c, "a young tapeworm", HX, HY - HR - 12,
                window(t, q["inside"].word("slips") + 0.2, q["cocoon"].start + 0.2, 0.3, 0.3),
                sub="it grows up only once swallowed")
        ax, ay = cam.screen(lx - 170 * LARVA_S, ly - 130)        # pointer on his back, bubble clear of him (pass 3)
        tag(c, "Pip, grown up", clamp(ax, 240, 760), ay, window(t, q["cocoon"].word("grown"), q["jump"].start + 0.5, 0.3, 0.2),
            sub="a cat flea")

    tl.add(s_bed, q["dry"].end, q["warm"].start + 0.45, transition="iris", trans_dur=0.6,
           iris_center=lambda t: (540, 1100), iris_r0=60)

    # ---------------------------------------------------------- back in the room: Pip in her fur
    PIP_S = 0.05                     # Pip on Mochi, exaggerated ~2x so he reads inside the lens (labelled)
    LAND = q["warm"].start

    def pip_on_back(w, t):
        if t > SWAL + 0.15:
            return
        k = ease(prog(t, LAND - 0.3, LAND + 0.3))
        x = BACK[0] + 2
        y = BACK[1] - 4 - 60 * (1 - k)
        pip.draw(w, st, x, y, PIP_S, ang=-0.15, phase=t * 3, blink=blinking(t, 0.7), happy=0.5,
                 alpha=k)

    def s_fur(c, t, ctx):
        cam = room_cam(t)
        room(c, t, cam, extra=lambda w: pip_on_back(w, t))
        lx, ly, lr = LENS
        bx, by = BACK

        def inner(cc):
            fur_lens(cc, t, lx, ly, lr, patch=0.6, seed=3)
            if t < SWAL + 0.1:
                k = ease(prog(t, LAND - 0.2, LAND + 0.4))
                gone = ease(prog(t, SWAL - 0.15, SWAL + 0.1))
                px = lx + 10 + 50 * math.sin((t - LAND) * 0.9) + lerp(0, 220, gone)
                py = ly + 40 - 260 * (1 - k)
                bite = window(t, q["itch"].start - 0.1, q["itch"].word("itches") + 0.5, 0.15, 0.2)
                warm = window(t, q["warm"].start, q["itch"].start, 0.4, 0.4)
                for i in range(5):                    # warmth rising off her skin
                    yy = ly + lr - ((t * 60 + i * 70) % (2 * lr))
                    cc.move_to(lx - lr + 30 + i * 70, yy)
                    for k2 in range(1, 8):
                        cc.line_to(lx - lr + 30 + i * 70 + 8 * math.sin(k2 + t * 3), yy - k2 * 14)
                    cc.set_source_rgba(1, 0.75, 0.45, 0.22 * warm)
                    cc.set_line_width(4)
                    cc.stroke()
                pip.draw(cc, st, px, py, 0.42, ang=-0.1 + 0.2 * bite, phase=t * 3, blink=blinking(t, 0.7), happy=0.5,
                         bite=bite, alpha=k * (1 - gone))
                glow = window(t, q["warm"].word("worm") - 0.2, q["itch"].start, 0.4, 0.4)
                ready = window(t, q["warm"].word("ready") - 0.2, q["itch"].start, 0.2, 0.4)
                if glow > 0:
                    noodle.draw_cyst(cc, st, px - 8, py - 62, 15, alpha=glow * (1 - gone), glow=1.2 + 0.9 * ready)
            licking = window(t, LICK0, SWAL + 0.3, 0.2, 0.3)
            ph = (t - LICK0) * 7.5 / TAU
            tongue(cc, lx, ly, ph % 1.0, licking * (0.6 + 0.4 * math.sin(ph * TAU)))
        a = window(t, LAND - 0.4, SWAL + 0.9, 0.3, 0.4)
        sx, sy = cam.screen(bx, by)
        leader(c, lx + lr * 0.55, ly + lr * 0.7, sx, sy, 0.8 * a)
        lens(c, lx, ly, lr, inner, a)
        label(c, "skin warmth: 31-36 °C", lx, ly + lr + 60, window(t, q["warm"].word("warm") - 0.1, q["itch"].start, 0.3, 0.3),
              size=36)

    tl.add(s_fur, q["warm"].start, q["swallow"].end + 0.7, transition="cut")

    # ---------------------------------------------------------- inside Mochi: ONE shot, keyframed
    HEAD_AT = (190, bg.GUT_FLOOR + 100)          # down among the villi, gripping (pass 1)
    TAIL_AT = (880, 620)                          # where her body ends when she's full grown (in frame)
    GKEYS = [
        (q["swallow"].end, 1.5, 330, 1290),                  # pass 2: her head stays above the captions
        (q["noodle"].end, 1.5, 330, 1290),
        (q["hooks"].start + 0.6, 3.2, 210, 1380),            # in on her hooks
        (q["hooks"].end, 3.2, 210, 1380),
        (q["mouth"].start + 0.6, 1.5, 380, 1330),
        (q["grow"].start + 0.4, 1.0, 540, 1200),             # all of her, head well above the caption band
        (q["leave"].word("crawl"), 1.0, 540, 1200),
    ]

    def gut_cam(t):
        for (t0, z0, x0, y0), (t1, z1, x1, y1) in zip(GKEYS, GKEYS[1:]):
            if t < t1:
                k = ease(prog(t, t0, t1))
                return framed(lerp(z0, z1, k), lerp(x0, x1, k), lerp(y0, y1, k))
        _, z0, x0, y0 = GKEYS[-1]
        return framed(z0, x0, y0)

    def worm_pts(t, grip=0.0):
        head = (HEAD_AT[0], HEAD_AT[1] + 8 * grip)
        return noodle.worm_curve(head, TAIL_AT, t * 1.1, amp=80, waves=2.4)

    def front_villi(c, t):
        """A few villi in front of her head, so the hook crown sits IN the lining."""
        for i, (dx, h, w) in enumerate(((-95, 120, 48), (-40, 95, 44), (20, 70, 46), (75, 105, 50))):
            x = HEAD_AT[0] + dx + 3 * math.sin(t * 1.3 + i)
            tip = HEAD_AT[1] + 140 - h - 60
            base = bg.HH                   # pass 2: no flat bottoms — they run off the background like the wall's
            c.move_to(x - w / 2, base)
            c.curve_to(x - w / 2, tip + 40, x - w * 0.4, tip, x, tip)
            c.curve_to(x + w * 0.4, tip, x + w / 2, tip + 40, x + w / 2, base)
            c.close_path()
            g = cairo.LinearGradient(0, tip, 0, tip + 420)
            g.add_color_stop_rgba(0, *hexc("#f2b8b0"))
            g.add_color_stop_rgba(0.45, *hexc("#d8848a"))
            g.add_color_stop_rgba(1, *hexc("#d8848a")[:3], 0.0)
            c.set_source(g)
            c.fill()

    def ruler_card(c, t, a):
        """Her length against a 30 cm ruler, on a card of its own (pass 1: a ruler inside the gut made the gut
        look 35 cm wide). The worm is drawn ~40 cm long: inside the 10-70 cm range, longer than the ruler."""
        if a <= 0:
            return
        from engine import text as tx_
        k = back_out(min(1.0, a * 1.3))
        c.save()
        c.translate(480, 690)
        c.scale(0.9 + 0.1 * k, 0.9 + 0.1 * k)
        c.translate(-480, -600)   # drawn 90 px lower: clear of the watermark badge
        c.push_group()
        from engine.core import rounded_rect
        rounded_rect(c, 70, 430, 820, 330, 36)
        c.set_source_rgba(1.0, 0.982, 0.95, 1.0)
        c.fill()
        soft_bubble(c, 70, 430, 820, 330, 1.0, r=36)
        tx_.center(c, "adults: 10 to 70 cm long", 480, 492, 36, hexc("#3a2a1a"), semibold=True)
        ruler(c, 120, 530, 540, 1.0)
        pts = [(110 + 720 * u, 690 + 10 * math.sin(u * 9 + t * 2)) for u in [i / 200 for i in range(201)]]
        noodle.draw(c, st, pts, noodle.SEG_MAX, 1.0, size=0.55, blink=blinking(t, 1.1), happy=0.6)
        c.pop_group_to_source()
        c.paint_with_alpha(min(1.0, a))
        c.restore()

    def food(c, t, eat_from, to_x=None):
        rnd = rng(5)
        for i in range(26):
            sp = rnd.uniform(60, 120)
            x = (rnd.uniform(0, 1400) + t * sp) % 1300 - 110
            y = rnd.uniform(620, 1240) + 18 * math.sin(t + i)
            r = rnd.uniform(6, 14)
            a = 0.75
            if t > eat_from and to_x is not None and x < to_x and y > 900:
                a *= 0.3                                       # soaked up near her
            ellipse(c, x, y, r, r * 0.8)
            c.set_source_rgba(*hexc("#f6e6b8")[:3], a)
            c.fill()

    def s_gut(c, t, ctx):
        cam = gut_cam(t)
        c.save()
        cam.apply(c)
        paint(c, bg.gut())
        n = q["noodle"]
        # she arrives as a head, a neck and a few tiny segments, puts on a few while she settles in, then
        # really grows on "And she grows" (pass 1: she arrived already long)
        early = ease(prog(t, n.start, q["mouth"].end))
        grow = ease(prog(t, q["grow"].start, q["grow"].end + 0.4))
        frac = lerp(lerp(0.07, 0.22, early), 1.0, grow)
        food(c, t, q["mouth"].start, to_x=lerp(HEAD_AT[0], TAIL_AT[0], frac) if t > q["mouth"].start else None)
        # the flea's empty shell dissolving, the young worm coming out of it
        shell_a = 1 - ease(prog(t, n.start - 0.6, n.word("Noodle")))
        if shell_a > 0:
            pip.draw(c, st, HEAD_AT[0] + 80, HEAD_AT[1] - 20, 0.5, phase=0, alpha=0.5 * shell_a)
        out = ease(prog(t, n.start - 0.6, n.word("Noodle") + 0.2))
        nseg = int(lerp(lerp(3, 8, early), noodle.SEG_MAX, grow))
        grip = (window(t, q["hooks"].word("hooks") - 0.1, q["hooks"].word("hooks") + 0.5, 0.15, 0.3)
                + window(t, q["hooks"].word("suckers") - 0.1, q["hooks"].word("suckers") + 0.5, 0.15, 0.3))
        ripe = ease(prog(t, q["eggs"].word("fills") - 0.3, q["eggs"].end))
        BRK = q["leave"].word("break")
        shed = ease(prog(t, BRK, q["leave"].word("crawl") + 0.6))
        pts = worm_pts(t, grip)
        c.push_group()
        lay = noodle.draw(c, st, pts, nseg, frac, skip_tail=2 if t >= BRK else 0, size=1.3,
                          blink=blinking(t, 1.1), happy=0.6 + 0.3 * out)
        c.pop_group_to_source()
        c.paint_with_alpha(clamp(out * 1.5))
        front_villi(c, t)
        # the two oldest segments break off on "break" and wriggle away (pass 1: nothing broke off on screen)
        if t >= BRK:
            for i in range(2):
                px, py, ang, l, w = lay[nseg - 1 - i]
                k = shed * (1 - 0.2 * i)
                c.save()
                c.translate(px + 40 * k + 18 * i, py - 150 * k - 10 * i)
                c.rotate(ang + 0.5 * k + 0.15 * math.sin(t * 6 + i))
                sq = 1 + 0.12 * math.sin(t * 7 + i)
                noodle.draw_segment(c, st, l * sq, w / sq, True, seed=200 + i)
                c.restore()
        c.restore()
        ruler_card(c, t, window(t, q["grow"].word("ruler") - 0.2, q["eggs"].word("fills"), 0.35, 0.3))
        hx, hy = cam.screen(*HEAD_AT)
        # beside her, below the body (a tag on the head covered her neck)
        tag(c, "Noodle", clamp(hx + 330, 240, 740), hy - 10, window(t, n.word("Noodle") + 0.1, q["hooks"].start, 0.3, 0.3),
            sub="Dipylidium caninum", pointer=False)
        label(c, "4 suckers: 2 on this side", 480, TOP_LABEL_Y + 40,
              window(t, q["hooks"].word("suckers") - 0.3, q["mouth"].word("soaks"), 0.3, 0.3), size=36)
        label(c, "no stomach, no gut at all", 480, TOP_LABEL_Y + 40,
              window(t, q["mouth"].word("soaks") + 0.2, q["grow"].word("ruler") - 0.3, 0.3, 0.3), size=36)
        label(c, "each segment: two sets of male + female parts", 480, TOP_LABEL_Y + 40,
              window(t, q["eggs"].word("fills"), q["leave"].word("break") - 0.2, 0.3, 0.3), size=34)  # clear of the break-off (pass 3)

    tl.add(s_gut, q["swallow"].end, q["leave"].word("crawl") + 0.7, transition="iris", trans_dur=0.6,
           iris_center=lambda t: (540, 1100), iris_r0=60)
    BREAK_SCREEN = (880, 640)        # roughly where the broken-off segments are when the room irises in

    # ---------------------------------------------------------- back on her fur: grains, waiting
    def grains(w, t, t0):
        for i, (dx, dy) in enumerate(((0, 0), (-9, 6), (8, 9))):
            k = prog(t, t0 + i * 0.4, t0 + i * 0.4 + 0.5)
            if k <= 0:
                continue
            dry = ease(prog(t, q["cycle"].start, q["cycle"].word("rice") + 0.4))
            segment_on_fur(w, t + i, GX + dx, GY + dy, 1.0 * k, dry=dry)

    def s_after(c, t, ctx):
        cam = room_cam(t)
        t0 = q["leave"].word("crawl")
        room(c, t, cam)
        lx, ly, lr = LENS

        def inner(cc):
            fur_lens(cc, t, lx, ly, lr, patch=1.0)
            dry = ease(prog(t, q["cycle"].start, q["cycle"].word("rice") + 0.4))
            for i, (dx, dy) in enumerate(((0, 0), (-70, 60), (60, 80))):
                k = ease(prog(t, t0 + i * 0.4, t0 + i * 0.4 + 0.5))
                if k > 0:
                    lens_seg(cc, t + i * 1.3, lx + dx, ly + dy - 40, 5.5 * k, dry=dry)
        a = window(t, t0 - 0.2, DUR, 0.35, 0.3)
        sx, sy = cam.screen(GX, GY)
        leader(c, lx + lr * 0.55, ly + lr * 0.7, sx, sy, 0.8 * a)
        lens(c, lx, ly, lr, inner, a)
        label(c, "each full of egg packets", lx, ly + lr + 60,
              window(t, q["cycle"].start, q["cycle"].end + 0.5, 0.3, 0.3), size=36)

    tl.add(s_after, q["leave"].word("crawl"), q["cycle"].end + 1.2, transition="iris", trans_dur=0.6,
           iris_center=lambda t: BREAK_SCREEN, iris_r0=60)

    # ---------------------------------------------------------- the end card
    def s_end(c, t, ctx):
        from engine import text as tx
        t0 = q["cycle"].end + 0.5
        c.save()
        c.translate(0, ctx.get("lift", 170))
        paint(c, bg.parchment())
        ta = ease(prog(t, t0, t0 + 0.4))
        c.push_group()
        mochi.draw(c, st, 440, 560, 0.78, eyes=0.0, tail=t, breathe=math.sin(t * 1.8))
        pip.draw(c, st, 860, 470, 0.5, phase=t * 3, blink=blinking(t, 0.7), happy=0.7)
        noodle.draw(c, st, noodle.worm_curve((150, 690), (930, 650), t * 0.4, amp=26, waves=2.5), 18, 1.0, size=0.75,
                    happy=0.7, blink=blinking(t, 1.1))
        c.pop_group_to_source()
        c.paint_with_alpha(ta)
        tx.center(c, "Dipylidium caninum", 540, 830, 72, INK, alpha=ta, italic=True)
        tx.center(c, "the flea tapeworm", 540, 896, 40, hexc("#8a5a3a"), alpha=ta * 0.9, italic=True)
        tx.center(c, "carried by the cat flea, Ctenocephalides felis", 540, 950, 34, hexc("#8a5a3a"), alpha=ta * 0.9,
                  italic=True)
        brand_plate(c, 540, 1110, ease(prog(t, t0 + 0.2, t0 + 0.7)))
        c.restore()

    tl.add(s_end, q["cycle"].end + 0.5, DUR + 0.1, trans_dur=0.7)

    # ---------------------------------------------------------- audio
    def make_audio(path):
        moods = [(0.0, "curious"), (q["mochi"].start, "cozy"), (q["dry"].start, "mystery"), (q["pip"].start, "playful"),
                 (q["inside"].start, "mystery"), (q["cocoon"].start, "wonder"), (q["warm"].start, "cozy"),
                 (q["itch"].start, "playful"), (q["noodle"].start, "curious"), (q["grow"].start, "wonder"),
                 (q["leave"].start, "mystery"), (q["cycle"].start, "finale")]
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


LOOK = ["teaser", "mochi", "grain", "dry", "spill", "pip", "eats", "inside", "cocoon", "jump", "warm", "lick",
        "noodle", "hooks", "mouth", "grow", "eggs", "leave", "cycle", "end"]


def look_times(Q):
    q = Q
    return dict(zip(LOOK, [
        0.0, q["mochi"].word("cat") + 0.3, q["grain"].word("eggs") + 0.2, q["dry"].word("breaks") + 0.2,
        q["dry"].end + 0.8, q["pip"].word("baby") + 0.2, q["eats"].word("crumbs") + 0.3, q["inside"].word("waits"),
        q["cocoon"].word("grown") + 0.5, q["jump"].start + 0.3, q["warm"].word("ready"), q["itch"].word("clean") + 0.2,
        q["noodle"].word("tapeworm"), q["hooks"].word("suckers") + 0.3, q["mouth"].word("skin"), q["grow"].word("ruler") + 0.3,
        q["eggs"].end - 0.2, q["leave"].word("crawl") + 0.9, q["cycle"].word("Pip") + 0.2, q["cycle"].end + 2.5]))


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
        out = os.path.join(os.path.dirname(os.path.dirname(HERE)), "for-review", "e005_mochi_noodle", "3_look_frames")
        shutil.rmtree(out, ignore_errors=True)
        lt = look_times(Q)
        paths = render.stills(tl, ctx, list(lt.values()), out, prefix="look")
        named = []
        for (name, _), p in zip(lt.items(), paths):
            dst = os.path.join(out, f"{len(named) + 1:02d}_{name}.png")
            os.replace(p, dst)
            named.append(dst)
        sheet = render.contact_sheet(named, os.path.join(out, "00_overview.png"), cols=5, width=2800)
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
    os.makedirs(os.path.join(HERE, "review"), exist_ok=True)
    qa = render.sample_frames(mp4, os.path.join(HERE, "review", f"qa_{a.style}.png"), every=1.0, cols=10)
    if a.copy_to:
        shutil.copy(mp4, a.copy_to)
        shutil.copy(qa, a.copy_to)


if __name__ == "__main__":
    main()
