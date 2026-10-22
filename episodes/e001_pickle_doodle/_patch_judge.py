"""One-off: apply the video-judge fixes to episode.py (kept for history)."""
import os

p = os.path.join(os.path.dirname(__file__), "episode.py")
s = open(p, encoding="utf8").read()


def R(a, b):
    global s
    assert a in s, "missing: " + a[:90]
    s = s.replace(a, b)


# --- opening teaser + voice starts after it
R('''    track, Q, caps, end = narrate(SCRIPT, os.path.join(HERE, "voice_cache"))''',
  '''    TEASER = 1.5
    track, Q, caps, end = narrate(SCRIPT, os.path.join(HERE, "voice_cache"), t0=TEASER + 0.15)''')
R('''    # ------------------------------------------------------------ 1. meet Pickle (meadow)''',
  '''    # ------------------------------------------------------------ 0. teaser hook (frame 0 = thumbnail)
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

    # ------------------------------------------------------------ 1. meet Pickle (meadow)''')
R('''    tl.add(s_pickle, 0.0, q["pixie1"].start)''', '''    tl.add(s_pickle, TEASER, q["pixie1"].start, trans_dur=0.3)''')
R('''        x = lerp(470, 560, ease(prog(t, 0.0, 1.2)))
        walking = t < 1.2''', '''        x = lerp(470, 560, ease(prog(t, TEASER, TEASER + 1.2)))
        walking = TEASER < t < TEASER + 1.2''')

# --- Pixie close-up: shift left out of the app-button zone
R('''        cam = Cam(z, LAND[0] - 110, LAND[1] - 90, 540, 1000)''', '''        cam = Cam(z, LAND[0] + 10, LAND[1] - 90, 540, 1000)''')

# --- grow: day/night cycles for "week after week"
R('''        sparkles(c, 540, 1250, t, w_several + 0.6, r=160)''', '''        wk = prog(t, q["grow1"].word("Week") - 0.3, q["grow2"].start + 0.2)
        if 0 < wk < 1:  # days and nights passing
            c.set_source_rgba(0.08, 0.1, 0.3, 0.32 * (0.5 - 0.5 * math.cos(TAU * 3 * wk)))
            c.paint()
        sparkles(c, 540, 1250, t, w_several + 0.6, r=160)''')

# --- split: water label from the start of the beat, generic worms (not Doodle)
R('''            doodle.draw_along(c, st, doodle.swim_points(hx, yy, 380, t + ph), 9, face=k == 0,
                              blink=blinking(t, 0.6), alpha=1.0 if k == 0 else 0.85)
        pill(c, "Water", 540, 560, ease(prog(t, q["problem2"].word("water") - 0.2, q["problem2"].word("water") + 0.2)), size=42)''',
  '''            doodle.draw_along(c, st, doodle.swim_points(hx, yy, 380, t + ph), 9, face=False, alpha=0.9)
        pill(c, "Water: where worms find mates", 540, 560, ease(prog(t, q["problem1"].start, q["problem1"].start + 0.4)), size=38)''')

# --- night: restless wandering until she finds the water
R('''    def walk7(t):
        k = ease(prog(t, q["drawn"].start + 0.4, q["drawn"].end + 0.4))
        return lerp(150, 520, k), lerp(1520, 1300, k), lerp(1.15, 0.85, k), k < 1 and k > 0''',
  '''    WANDER = [(160, 1500), (330, 1440), (250, 1380), (420, 1350), (360, 1310), (520, 1290)]

    def walk7(t):
        k = prog(t, q["drawn"].word("wandering") - 0.2, q["drawn"].word("finds") + 0.2)
        f = k * (len(WANDER) - 1)
        i = min(int(f), len(WANDER) - 2)
        x, y = lerp2(WANDER[i], WANDER[i + 1], ease(f - i))
        return x, y, lerp(1.15, 0.85, k), 0 < k < 1''')
a = s[s.index('        qa = window(t, w_how, q["splash"].start - 0.6, 0.25, 0.3)'):s.index('    # ------------------------------------------------------------ 8. splash')]
R(a, '''        qa = window(t, w_how, HOP0 + 0.3, 0.25, 0.3)
        if qa > 0:
            hx, hy = pickle_head_top(x, y, s)
            _think(c, hx + 40, hy - 70, qa)

    HOP0 = q["how"].end + 0.15        # the jump: close shot, anticipation, big splash on the silent beat
    tl.add(s_night, q["drawn"].start - 0.35, HOP0 + 0.3)

''')

# --- the jump: closer, slower, bigger
a = s[s.index("    def s_hop(c, t, ctx):"):s.index("    REAR_LOCAL = (-150, -56)")]
R(a, '''    def s_hop(c, t, ctx):
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

''')

# --- emergence from the abdomen tip, underwater, behind her body
R('''    REAR_LOCAL = (-150, -56)
    PFLOAT = (600, 520)
    DIR = (-0.55, 0.835)''', '''    REAR_LOCAL = (-160, -54)   # tip of the abdomen: where hairworms really exit
    PFLOAT = (620, 478)        # floating at the surface (y 430), rear tipped under water
    PANG = -0.35
    DIR = (-0.36, 0.93)        # out of the rear, down and back, into the pond''')
R('''        c.set_source_rgba(0.1, 0.18, 0.35, 0.25)
        c.paint()
        bg.motes(c, t)
        bob = 6 * math.sin(t * 2)
        rear = pickle.to_world(PFLOAT[0], PFLOAT[1] + bob, 1.1, -0.12, *REAR_LOCAL)''', '''        c.set_source_rgba(0.08, 0.12, 0.3, 0.42)  # night-time pond, matching the scene before
        c.paint()
        bg.motes(c, t)
        bob = 5 * math.sin(t * 2)
        rear = pickle.to_world(PFLOAT[0], PFLOAT[1] + bob, 1.1, PANG, *REAR_LOCAL)''')
R('''        e = ease(prog(t, w_slips - 0.3, w_swims + 0.2))''', '''        e = ease(prog(t, w_slips - 0.1, w_slips + 1.6))''')
R('''        away = max(0.0, t - (w_swims + 0.2)) * 260''', '''        away = max(0.0, t - (w_slips + 1.6)) * 230''')
R('''        for i in range(n):
            uu = i / (n - 1)
            along = uu * L''', '''        shown = min(L, L * e + away)   # only the part that has already come out is visible
        for i in range(n):
            uu = i / (n - 1)
            along = uu * shown''')
R('''        if e > 0:
            doodle.draw_along(c, st, pts, 9, face=True, blink=blinking(t, 0.3), happy=0.5)
        pickle.draw(c, st, PFLOAT[0], PFLOAT[1] + bob, 1.1, ang=-0.12,''', '''        if shown > 12:
            doodle.draw_along(c, st, pts, 9, face=True, blink=blinking(t, 0.3), happy=0.5)
        pickle.draw(c, st, PFLOAT[0], PFLOAT[1] + bob, 1.1, ang=PANG,''')

# --- larvae: microscopic specks; nymph comes in head-first and visibly swallows one
R('''            doodle.draw_larva(c, st, lx, ly, 3.0, t * 6 + i)''', '''            c.arc(lx, ly, 13, 0, TAU)            # soft glow so a tiny speck is still visible
            c.set_source_rgba(1, 1, 0.9, 0.35)
            c.fill()
            doodle.draw_larva(c, st, lx, ly, 0.45, t * 6 + i)''')
R('''        nx, ny = lerp(1300, LARVA_T[0] + 150, nk), LARVA_T[1] - 6 + 10 * math.sin(t * 2)''',
  '''        # head (local x ~ +50 at scale 2.2) arrives at the larva: comes in from the left, head first
        nx, ny = lerp(-260, LARVA_T[0] - 105, nk), LARVA_T[1] + 22 + 8 * math.sin(t * 2)''')
R('''                doodle.draw_cyst(c, st, nx - 130, ny - 44, 13,''', '''                doodle.draw_cyst(c, st, nx - 120, ny - 44, 13,''')
R('''            tag(c, "young mayfly", nx - 60, ny - 110,''', '''            tag(c, "young mayfly", nx - 20, ny - 100,''')

# --- end card: screen coordinates (undo the stage lift), clear of app UI, complete cycle
R('''    CX, CY, CR = 540, 1000, 330''', '''    CX, CY, CR = 495, 850, 290   # screen coords; right edge stays clear of the app buttons''')
R('''("Worm swims out\\nin the water", "worm")''', '''("Cricket jumps in,\\nworm swims out", "worm")''')
R('''    def s_cycle(c, t, ctx):
        paint(c, bg.parchment())''', '''    def s_cycle(c, t, ctx):
        from engine.scene import STAGE_LIFT
        c.translate(0, STAGE_LIFT)  # lay the end card out in screen coordinates
        paint(c, bg.parchment())''')
R('''                    text_center(c, ln, nx, ny + 70 + j * 36, 30, INK, alpha=ease(k))''',
  '''                    text_center(c, ln, nx, ny + 74 + j * 40, 36, INK, alpha=ease(k))''')
R('''        text_center(c, "Teenyology", W / 2, 1640, 64, INK, bold=True, alpha=ea)
        text_center(c, "Teeny creatures. Big stories.", W / 2, 1705, 34, INK, italic=True, alpha=ea * 0.8)''',
  '''        text_center(c, "Teenyology", W / 2, 1385, 64, INK, bold=True, alpha=ea)
        text_center(c, "Teeny creatures. Big stories.", W / 2, 1440, 34, INK, italic=True, alpha=ea * 0.8)''')

# --- shared thought bubble
R('''# ================================================================ build''', '''def _think(c, x, y, a):
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


# ================================================================ build''')

open(p, "w", encoding="utf8").write(s)
print("patched")
