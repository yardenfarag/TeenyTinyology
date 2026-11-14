"""Automatic pre-judge checks for a Short: the mistakes in docs/judge-lessons.md that a program can catch.

Usage:
    python -m engine.checks episodes.<pkg> [--mp4 PATH] [--style illustrated] [--fps 4] [--only script,timeline]

Groups (all run by default; `layout` renders frames and takes ~1-2 min):
  script    narration text: spoken sound words, SFX anchors, voice QA leftovers, absolute claims in the hook /
            closing line, character intros, pace, the old channel name
  timeline  holes, transitions that silently play as cuts, end-card hold, caption length / width / weak endings
  layout    renders the timeline (--fps samples per second) with the scene recorder on: tags / labels / lens /
            plate inside the safe zone, not on a caption or the watermark or each other, on screen >= 2 s, not
            echoing the caption, not drawn inside a camera zoom, size >= 34 px; black frames, frame 0, black edges
            (camera past its background), frozen stretches, scenes far stiller than the rest
  mp4       the encoded file (newest out/*.mp4 unless --mp4): format, duration, loudness, true / sample peak,
            silence, black and frozen frames, and whether the file is older than the code

Writes episodes/<pkg>/review/checks.md and checks.json. Exit code 1 when anything is an ERROR.
Every check cites the lesson it automates, so a failure says why it matters.
"""
import argparse
import glob
import importlib
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass

import numpy as np

SAFE = (60, 200, 900, 1460)          # x0, y0, x1, y1 (CLAUDE.md UI rules) — outside it: WARN
APP_UI = [(0, 0, 1080, 170, "app top bar"), (930, 700, 1080, 1520, "app button rail"),
          (0, 1520, 1080, 1920, "app description area")]     # covered by TikTok / Shorts UI: ERROR
CAP_BAND = (1300, 1500)              # caption rows, masked when measuring motion
WM_BOX = (45, 190, 180, 325)         # x0, y0, x1, y1 around the watermark badge (masked when measuring motion)
MIN_LABEL_S = 2.0
MIN_CAPTION_S = 0.9
END_HOLD_S = 4.0
MIN_TEXT_PX = 34

SOUND_WORDS = {"splash", "crunch", "gulp", "pop", "buzz", "boing", "slurp", "whoosh", "plop", "splat", "thud", "boom",
               "bang", "squeak", "chirp", "munch", "chomp", "zap", "poof", "purr", "hiss", "whir", "ding", "squelch",
               "zip", "fizz", "sploosh", "boop", "plink", "swoosh"}
ABSOLUTES = {"never", "only", "always", "can't", "cannot", "every", "all", "needs", "must", "nothing", "nobody",
             "none", "everyone", "everything", "no one"}
STOP = {"the", "a", "an", "of", "to", "in", "on", "at", "for", "and", "or", "but", "with", "by", "from", "her", "his",
        "its", "their", "is", "are", "was", "be", "that", "this", "as", "into", "so", "it", "she", "he", "they", "you",
        "not", "just", "out", "up", "one", "now", "then", "here", "there", "has", "have", "who", "what"}


@dataclass
class Finding:
    sev: str            # ERROR | WARN
    group: str
    check: str
    msg: str
    t0: float = None
    t1: float = None
    lesson: str = ""

    def when(self):
        if self.t0 is None:
            return ""
        return f"{self.t0:6.2f}s" if self.t1 is None or abs(self.t1 - self.t0) < 1e-6 else f"{self.t0:6.2f}-{self.t1:.2f}s"


def words_of(text):
    return re.findall(r"[a-z][a-z']*", text.lower().replace("’", "'"))


# ================================================================ script
def check_script(sc, cues, here):
    from engine.audio import sfx as sfxlib
    out = []
    F = lambda sev, check, msg, t0=None, lesson="": out.append(Finding(sev, "script", check, msg, t0, None, lesson))
    spoken = [ln for ln in sc.SCRIPT if ln.text]
    ids = {ln.id for ln in sc.SCRIPT}

    for ln in spoken:
        for w in words_of(ln.text):
            base = re.sub(r"(ed|ing|es|s)$", "", w)
            if w in SOUND_WORDS:
                F("ERROR", "spoken sound", f"line `{ln.id}` says \"{w}\" — let the sound effect say it "
                  f"(silent beat: Line(id, \"\", pause, sfx=...))", cues[ln.id].start, "CLAUDE.md narration rules")
            elif base in SOUND_WORDS or base + "e" in SOUND_WORDS:
                F("WARN", "spoken sound", f"line `{ln.id}` says \"{w}\" — a sound word? the sound effect should "
                  f"carry it", cues[ln.id].start, "CLAUDE.md narration rules")

    for row in getattr(sc, "SFX", []):
        lid, word, name, gain, off = row
        if name not in sfxlib.LIB:
            F("ERROR", "sfx", f"SFX {row}: no effect named \"{name}\" in engine/audio/sfx.py")
        if lid not in ids:
            F("ERROR", "sfx", f"SFX {row}: no script line \"{lid}\"")
            continue
        if word:
            text = next(ln.text for ln in sc.SCRIPT if ln.id == lid)
            if word.lower() not in text.lower():
                F("ERROR", "sfx", f"SFX {row}: anchor word \"{word}\" is not in line `{lid}` — it would fire at "
                  f"the line's start instead", cues[lid].start)
        if gain > 0.6:
            F("WARN", "sfx", f"SFX {row}: gain {gain} — one loud cue on a stressed word can clip the mix",
              cues[lid].start, "judge-lessons: one loud cue can clip the whole mix")
    for ln in sc.SCRIPT:
        if ln.sfx and ln.sfx not in sfxlib.LIB:
            F("ERROR", "sfx", f"line `{ln.id}`: no effect named \"{ln.sfx}\"")
        if ln.text and ln is not spoken[-1] and not (0.25 <= ln.pause <= 1.3):
            F("WARN", "pause", f"line `{ln.id}`: pause {ln.pause}s (normal 0.4-0.6, after a key fact 0.8-1.0, "
              f"rhythmic beats 0.3)", cues[ln.id].start, "CLAUDE.md narration rules")

    qa = os.path.join(here, "voice_cache", "qa.json")
    if os.path.exists(qa):
        flagged = json.load(open(qa, encoding="utf8"))
        for lid, probs in flagged.items():
            F("ERROR", "voice QA", f"line `{lid}` still sounds wrong ({', '.join(probs)}) — bump its `take`",
              cues[lid].start if lid in cues else None, "judge-lessons: ElevenLabs clips carry stray sound")

    if spoken:
        for ln, where in ((spoken[0], "hook"), (spoken[-1], "closing line")):
            txt = " " + " ".join(words_of(ln.text)) + " "
            hits = sorted(a for a in ABSOLUTES if f" {a} " in txt)
            if hits:
                F("WARN", "absolute claim", f"{where} `{ln.id}` uses {', '.join(hits)} — read it against the hedges "
                  f"in facts.md (hosts, exceptions, timing)", cues[ln.id].start,
                  "judge-lessons: hooks and closing lines must survive the host list on Wikipedia")
        if cues[spoken[0].id].start > 1.6:
            F("WARN", "hook", f"the voice starts at {cues[spoken[0].id].start:.2f}s (rule: within ~1.5 s)",
              cues[spoken[0].id].start, "CLAUDE.md UI rules: frame 0 is the thumbnail")
        n = sum(len(words_of(ln.text)) for ln in spoken)
        talk = sum(cues[ln.id].end - cues[ln.id].start for ln in spoken)
        wpm = 60 * n / max(talk, 1e-6)
        if not 120 <= wpm <= 175:
            F("WARN", "pace", f"{wpm:.0f} words per minute while talking (aim ~140-150)")

    cast = [os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join("characters", "*.py"))]
    cast = [n.capitalize() for n in cast if n not in ("__init__", "model_sheet")]
    for name in cast:
        first = next((ln for ln in spoken if re.search(rf"\b{name}\b", ln.text)), None)
        if first and not re.search(rf"\bThis is {name}\b", first.text):
            F("WARN", "intro", f"{name} is first named in `{first.id}` without \"This is {name}.\" "
              f"(owner preference: \"This is <Name>. <She/He>'s a <species>\")", cues[first.id].start)

    texts = [ln.text for ln in sc.SCRIPT]
    post = os.path.join(here, "out", "post.md")
    if os.path.exists(post):
        texts.append(open(post, encoding="utf8").read())
    if any(re.search(r"teenyology", t, re.I) for t in texts):
        F("ERROR", "name", "the old channel name \"Teenyology\" appears — it is TeenyTinyology")
    return out


# ================================================================ timeline
def check_timeline(tl, ctx, caps):
    from engine import text
    from engine.scene import CAP_MAX_W, CAP_SIZE
    from engine.voice import WEAK_ENDS
    out = []
    F = lambda sev, check, msg, t0=None, t1=None, lesson="": out.append(
        Finding(sev, "timeline", check, msg, t0, t1, lesson))

    step, t, hole = 1 / 30, 0.0, None
    while t < tl.duration:
        live = any(s.start <= t < s.end for s in tl.scenes)
        if not live and hole is None:
            hole = t
        if live and hole is not None:
            F("ERROR", "hole", "no scene is live (renders black)", hole, t, "judge-lessons: assert the timeline has no holes")
            hole = None
        t += step
    if hole is not None:
        F("ERROR", "hole", "no scene is live (renders black)", hole, tl.duration)

    for i, s in enumerate(tl.scenes):
        if s.transition == "cut" or s.start <= 0.01:
            continue
        before = [o for o in tl.scenes[:i] if o.start <= s.start < o.end]
        if not before:
            F("WARN", "transition", f"scene {s.fn.__name__} has a {s.transition} but no earlier scene is still live "
              f"at {s.start:.2f}s, so it plays as a plain cut — extend the previous scene by trans_dur",
              s.start, None, "judge-lessons: a transition needs an overlap or it is a cut")
        else:
            ov = max(o.end for o in before) - s.start
            if ov < s.trans_dur - 0.02:
                F("WARN", "transition", f"scene {s.fn.__name__}: {s.transition} lasts {s.trans_dur:.2f}s but the "
                  f"previous scene ends {ov:.2f}s in — the transition is cut short", s.start, None,
                  "judge-lessons: a transition needs an overlap or it is a cut")

    if caps:
        hold = tl.duration - caps[-1].end
        if hold < END_HOLD_S:
            F("ERROR", "end card", f"only {hold:.1f}s after the last caption (end card must read for >= {END_HOLD_S:.0f} s)",
              caps[-1].end, tl.duration, "judge-lessons: end card stays fully readable for at least 4 s")
    if ctx.get("fade_in", 0.3) > 0:
        F("WARN", "frame 0", "the episode fades in from black — frame 0 is the thumbnail; set ctx[\"fade_in\"] = 0",
          0.0, None, "judge-lessons: frame 0 must not be black")

    for cp in caps:
        words = [w for w, _, _ in cp.words]
        line = " ".join(words)
        d = cp.end - cp.start
        if d < MIN_CAPTION_S:
            F("WARN", "caption", f"\"{line}\" is on screen {d:.2f}s (min {MIN_CAPTION_S}s)", cp.start, cp.end,
              "judge-lessons: no caption shorter than ~0.9 s")
        last = re.sub(r"[^\w']", "", words[-1].lower()) if words else ""
        if last in WEAK_ENDS and not re.search(r"[.!?,…]$", words[-1]):
            F("WARN", "caption", f"\"{line}\" ends on \"{words[-1]}\" — break with | in the script", cp.start, cp.end,
              "judge-lessons: captions break at natural phrase boundaries")
        if len(words) == 1:
            F("WARN", "caption", f"one-word caption \"{line}\"", cp.start, cp.end,
              "judge-lessons: a one-word orphan should not sit alone")
        w = sum(text.width(x, CAP_SIZE, bold=True) for x in words) + text.width(" ", CAP_SIZE, bold=True) * (len(words) - 1)
        if w + 64 > CAP_MAX_W + 2:
            F("ERROR", "caption", f"\"{line}\" is {w + 64:.0f}px wide (max {CAP_MAX_W})", cp.start, cp.end)
    return out


# ================================================================ layout (rendered)
def _iou_touch(a, b, pad=0.0):
    return not (a[2] + pad <= b[0] or b[2] + pad <= a[0] or a[3] + pad <= b[1] or b[3] + pad <= a[1])


def _circle(r):
    x0, y0, x1, y1 = r["box"]
    if r["kind"] == "watermark":             # box includes the shadow below the badge
        return (x0 + x1) / 2, y0 + (x1 - x0) / 2, (x1 - x0) / 2
    return (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2


def _touch(a, b, pad=0.0):
    """Boxes for labels / tags / captions, circles for the lens and the watermark badge."""
    ca, cb = a["kind"] in ("lens", "watermark"), b["kind"] in ("lens", "watermark")
    if ca and cb:
        (x, y, r), (u, v, q) = _circle(a), _circle(b)
        return np.hypot(x - u, y - v) < r + q + pad
    if ca or cb:
        circ, box = (a, b) if ca else (b, a)
        x, y, r = _circle(circ)
        bx0, by0, bx1, by1 = box["box"]
        return np.hypot(x - min(max(x, bx0), bx1), y - min(max(y, by0), by1)) < r + pad
    return _iou_touch(a["box"], b["box"], pad)


def _merge(hits, step, group, sev, check, lesson):
    """hits: {key: [(t, msg)]} -> Findings with consecutive sample times merged into ranges."""
    out = []
    for key, rows in hits.items():
        rows.sort()
        s, prev, msg = rows[0][0], rows[0][0], rows[0][1]
        for t, m in rows[1:] + [(None, None)]:
            if t is not None and t - prev <= step * 1.5:
                prev = t
                continue
            out.append(Finding(sev, group, check, msg, s, prev, lesson))
            if t is not None:
                s, prev, msg = t, t, m
    return out


def check_layout(tl, ctx, fps=4.0):
    import cairo
    from engine import scene
    from engine.core import H, W
    out = []
    step = 1.0 / fps
    times = [round(i * step, 4) for i in range(int(tl.duration * fps))]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    frames, greys = [], []
    for t in times:
        scene._REC = []
        try:
            scene.render_frame(cairo.Context(surf), t, tl, ctx)
        finally:
            rec, scene._REC = scene._REC, None
        surf.flush()
        px = np.ndarray((H, W, 4), np.uint8, surf.get_data())
        g = px[:, :, :3].mean(axis=2)
        greys.append(g[::8, ::8].copy())
        edge = (g[:, :6].mean(), g[:, -6:].mean(), g[200:1460].mean())
        frames.append((t, rec, edge))
        if len(frames) % 100 == 0:
            print(f"  layout {t:.0f}/{tl.duration:.0f}s", flush=True)

    scenes_at = lambda t: ", ".join(s.fn.__name__ for s in tl.scenes if s.start <= t < s.end)
    safe, on_ui, on_cap, on_wm, overlap, small, zoomed, edges = {}, {}, {}, {}, {}, {}, {}, {}
    vis = {}                                  # (kind, text) -> [t]   (alpha >= 0.5)
    caps_at = {}
    for t, rec, edge in frames:
        caps_ = [r for r in rec if r["kind"] == "caption" and r["alpha"] > 0.3]
        caps_at[t] = " ".join(r["text"] for r in caps_)
        wm = [r for r in rec if r["kind"] == "watermark"]
        items = [r for r in rec if r["kind"] in ("tag", "label", "lens", "plate")]
        for r in items:
            if r["alpha"] >= 0.5 and r["kind"] in ("tag", "label"):
                vis.setdefault((r["kind"], r["text"]), []).append(t)
            if r["alpha"] < 0.75:
                continue
            x0, y0, x1, y1 = r["box"]
            name = f"{r['kind']} \"{r['text']}\"" if r["text"] else r["kind"]
            key = (r["kind"], r["text"])
            ui = [n for ux0, uy0, ux1, uy1, n in APP_UI if _iou_touch(r["box"], (ux0, uy0, ux1, uy1), -2)]
            if x0 < 0 or x1 > 1080:
                ui.append("off the frame")
            if ui:
                on_ui.setdefault(key, []).append((t, f"{name} is under the {' / '.join(ui)} (box {x0:.0f},{y0:.0f}-"
                                                     f"{x1:.0f},{y1:.0f}) in {scenes_at(t)}"))
            elif x0 < SAFE[0] - 2 or x1 > SAFE[2] + 2 or y0 < SAFE[1] - 2 or y1 > SAFE[3] + 2:
                side = [n for n, bad in (("left", x0 < SAFE[0] - 2), ("right", x1 > SAFE[2] + 2),
                                         ("top", y0 < SAFE[1] - 2), ("bottom", y1 > SAFE[3] + 2)) if bad]
                safe.setdefault(key, []).append((t, f"{name} leaves the safe zone ({'/'.join(side)}: box "
                                                    f"{x0:.0f},{y0:.0f}-{x1:.0f},{y1:.0f}) in {scenes_at(t)}"))
            for cp in caps_:
                if _touch(r, cp, 4):
                    on_cap.setdefault(key, []).append((t, f"{name} touches the caption bubble in {scenes_at(t)}"))
            for w in wm:
                if _touch(r, w, 2):
                    on_wm.setdefault(key, []).append((t, f"{name} touches the watermark badge in {scenes_at(t)}"))
            if r["kind"] in ("tag", "label") and r["size"] and r["size"] * r["zoom"] < MIN_TEXT_PX - 0.5:
                small.setdefault(key, []).append((t, f"{name} text is {r['size'] * r['zoom']:.0f}px (min {MIN_TEXT_PX})"))
            if r["kind"] in ("tag", "label") and abs(r["zoom"] - 1) > 0.02:
                zoomed.setdefault(key, []).append((t, f"{name} is drawn inside a camera zoom (x{r['zoom']:.2f}): it "
                                                      f"grows and drifts with the push — draw it after c.restore()"))
        for i, a in enumerate(items):
            for b in items[i + 1:]:
                if a["alpha"] < 0.75 or b["alpha"] < 0.75 or "lens" in (a["kind"], b["kind"]):
                    continue
                if a["text"] == b["text"] or not _iou_touch(a["box"], b["box"], 0):
                    continue
                pair = tuple(sorted((f"{a['kind']} \"{a['text']}\"", f"{b['kind']} \"{b['text']}\"")))
                overlap.setdefault(pair, []).append((t, f"{pair[0]} overlaps {pair[1]} in {scenes_at(t)}"))
        dark_edge = [n for n, v in zip(("left", "right"), edge[:2]) if v < 4] if edge[2] > 25 else []
        if dark_edge and step < t < tl.duration - 0.8:
            edges.setdefault(tuple(dark_edge), []).append((t, f"black strip at the {'/'.join(dark_edge)} edge in "
                                                             f"{scenes_at(t)} — the camera shows past its background"))

    out += _merge(on_ui, step, "layout", "ERROR", "app UI", "CLAUDE.md UI rules: the app covers the right rail, top bar and bottom")
    out += _merge(safe, step, "layout", "WARN", "safe zone", "CLAUDE.md UI rules: keep text inside x 60-900, y 200-1460")
    out += _merge(on_cap, step, "layout", "ERROR", "on caption", "CLAUDE.md UI rules: no caption overlapping a label")
    out += _merge(on_wm, step, "layout", "ERROR", "on watermark", "judge-lessons: top labels collide with the watermark")
    out += _merge(overlap, step, "layout", "ERROR", "overlap", "judge-lessons: e004 tag/label collisions")
    out += _merge(small, step, "layout", "WARN", "text size", "CLAUDE.md UI rules: labels >= 34 px")
    out += _merge(zoomed, step, "layout", "WARN", "zoomed label", "judge-lessons: draw labels after c.restore()")
    out += _merge(edges, step, "layout", "ERROR", "black edge", "judge-lessons: a camera must never show past its background")

    for (kind, txt), ts in vis.items():
        runs, s, prev = [], ts[0], ts[0]
        for t in ts[1:] + [None]:
            if t is not None and t - prev <= step * 1.5:
                prev = t
                continue
            runs.append((s, prev + step))
            if t is not None:
                s = prev = t
        for s, e in runs:
            if e - s < MIN_LABEL_S - 1e-6 and s > step and e < tl.duration - step:
                out.append(Finding("WARN", "layout", "label time", f"{kind} \"{txt}\" is readable for only {e - s:.1f}s "
                                   f"(min {MIN_LABEL_S:.0f}s beside a caption) — chain it to the next label's cue",
                                   s, e, "judge-lessons: a label beside a caption needs about 2 s"))
            if kind == "label":
                lw = [w for w in words_of(txt) if w not in STOP and len(w) > 2]
                cw = set(words_of(" ".join(caps_at.get(round(x, 4), "") for x in np.arange(s - 1.5, e + 1.5, step)
                                         if round(x, 4) in caps_at)))
                if len(lw) >= 2 and sum(w in cw or w.rstrip("s") in cw for w in lw) / len(lw) >= 0.75:
                    out.append(Finding("WARN", "layout", "echo", f"label \"{txt}\" repeats the caption — write the one "
                                       f"fact the line did not say, or drop it", s, e,
                                       "judge-lessons: on-screen tags must add information, not repeat the caption"))

    # ---- pixels: frame 0, black frames, frozen stretches, still scenes
    raw0 = greys[0]
    if raw0.mean() < 12 and raw0.std() < 6:
        out.append(Finding("ERROR", "layout", "frame 0", "frame 0 is black — it is the thumbnail", 0.0, None,
                           "judge-lessons: frame 0 must not be black"))
    black = {}
    for (t, _, _), g in zip(frames, greys):
        if 0 < t < tl.duration - 0.8 and g.mean() < 12 and g.std() < 6:
            black.setdefault("black", []).append((t, f"black frame in {scenes_at(t) or 'no scene'}"))
    out += _merge(black, step, "layout", "ERROR", "black frame", "judge-lessons: check for black frames")
    out += motion_findings([t for t, _, _ in frames], greys, tl, "layout", masked=True, scale=8)
    return out


def motion_findings(ts, greys, tl, group, masked=True, scale=8, freeze=0.02):
    """Frozen runs > 2 s and scenes far stiller than the episode's own 75th percentile (captions + badge masked)."""
    out = []
    gs = []
    for g in greys:
        g = g.copy()
        if masked:
            g[CAP_BAND[0] // scale:CAP_BAND[1] // scale, :] = 0
            g[WM_BOX[1] // scale:WM_BOX[3] // scale, WM_BOX[0] // scale:WM_BOX[2] // scale] = 0
        gs.append(g)
    if len(gs) < 3:
        return out
    d = np.array([np.abs(gs[i + 1] - gs[i]).mean() for i in range(len(gs) - 1)])
    s = None
    for i, v in enumerate(d):
        if v < freeze and s is None:
            s = ts[i]
        elif (v >= freeze or i == len(d) - 1) and s is not None:
            e = min(ts[i + 1] if v < freeze else ts[i], tl.duration - 0.8)     # the closing fade is not a freeze
            end_card = tl.captions and s >= tl.captions[-1].end - 0.1     # owner prefers a still end card (e004)
            if e - s > 2.0 and not end_card:
                out.append(Finding("WARN", group, "frozen", f"nothing moves for {e - s:.1f}s — add idle motion, a "
                                   f"blink or a push-in", s, e, "CLAUDE.md animation rules: nothing frozen for > 2 s"))
            s = None
    p75 = float(np.percentile(d, 75)) or 1e-6
    if group == "layout":
        for sc in tl.scenes:
            v = [d[i] for i, t in enumerate(ts[:-1]) if sc.start + 0.5 <= t < min(sc.end, tl.duration) - 0.5]
            if len(v) >= 4 and np.mean(v) / p75 < 0.45:
                out.append(Finding("WARN", group, "still scene", f"scene {sc.fn.__name__} moves {np.mean(v) / p75:.2f}x "
                                   f"this episode's usual amount — near-dead on a phone (on a flat card, confirm by eye)",
                                   sc.start, min(sc.end, tl.duration),
                                   "judge-lessons: judge a scene against this episode's own baseline"))
    return out


# ================================================================ mp4
def check_mp4(mp4, tl, here):
    from engine.audio.common import ffmpeg_exe
    from engine.audio.mix import measure_lufs
    out = []
    F = lambda sev, check, msg, t0=None, t1=None, lesson="": out.append(Finding(sev, "mp4", check, msg, t0, t1, lesson))
    ff = ffmpeg_exe()

    newest = max(os.path.getmtime(p) for p in glob.glob(os.path.join(here, "*.py")))
    if os.path.getmtime(mp4) < newest:
        F("WARN", "stale", f"{os.path.basename(mp4)} is older than the episode's code — re-render before judging")

    info = subprocess.run([ff, "-hide_banner", "-i", mp4], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", info)
    dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 0
    if abs(dur - tl.duration) > 0.25:
        F("WARN", "duration", f"file is {dur:.2f}s, timeline is {tl.duration:.2f}s — stale render?")
    v = re.search(r"Video: (\w+).*?, (\d+)x(\d+).*?, ([\d.]+) fps", info)
    if not v or v.group(1) != "h264" or (v.group(2), v.group(3)) != ("1080", "1920") or abs(float(v.group(4)) - 30) > 0.01:
        F("ERROR", "format", f"video stream is {v.group(0) if v else 'missing'} (need h264 1080x1920 30 fps)")
    if not re.search(r"Audio: aac", info):
        F("ERROR", "format", "no AAC audio stream")

    SR = 48000
    r = subprocess.run([ff, "-v", "error", "-i", mp4, "-map", "0:a", "-f", "f32le", "-acodec", "pcm_f32le",
                        "-ac", "2", "-ar", str(SR), "-"], capture_output=True)
    a = np.frombuffer(r.stdout, dtype=np.float32).reshape(-1, 2)
    lufs = measure_lufs(mp4)
    if lufs is None or abs(lufs + 14) > 1.0:
        F("ERROR", "loudness", f"{lufs} LUFS (target -14)", lesson="CLAUDE.md format: -14 LUFS")
    r2 = subprocess.run([ff, "-hide_banner", "-i", mp4, "-map", "0:a", "-af", "ebur128=peak=true", "-f", "null", "-"],
                        capture_output=True, text=True).stderr
    tp = re.findall(r"Peak:\s*(-?[\d.]+|-inf)", r2)
    tp = float(tp[-1]) if tp and tp[-1] != "-inf" else None
    if tp is not None and tp > -1.0:
        F("ERROR", "true peak", f"true peak {tp:+.1f} dBFS (limit -1.5)", lesson="judge-lessons: measure true peak and sample peak")
    elif tp is not None and tp > -1.5:
        F("WARN", "true peak", f"true peak {tp:+.1f} dBFS (limit -1.5; AAC adds a little)")
    over = int((np.abs(a) > 1.0).sum())
    if over:
        F("ERROR", "clipping", f"{over} decoded samples beyond full scale", lesson="judge-lessons: one loud cue can clip the whole mix")
    w, hop = SR // 10, SR // 20
    starts = range(0, max(1, len(a) - w), hop)
    db = np.array([20 * np.log10(float(np.sqrt((a[i:i + w] ** 2).mean())) + 1e-12) for i in starts])
    s = None
    for i, x in enumerate(list(db) + [0.0]):
        t = i * hop / SR
        if x < -50 and s is None:
            s = t
        elif x >= -50 and s is not None:
            if t - s >= 0.75:
                F("ERROR", "silence", f"audio below -50 dB for {t - s:.1f}s", s, t,
                  "judge-lessons: check for silence explicitly (e002 shipped 2 s of digital zero)")
            s = None

    fps, sw, sh = 4, 135, 240
    r = subprocess.run([ff, "-v", "error", "-i", mp4, "-vf", f"fps={fps},scale={sw}:{sh},format=gray",
                        "-f", "rawvideo", "-"], capture_output=True)
    fr = np.frombuffer(r.stdout, np.uint8).reshape(-1, sh, sw).astype(float)
    ts = [i / fps for i in range(len(fr))]
    blk = [t for t, g in zip(ts, fr) if g.mean() < 12 and g.std() < 6 and t < tl.duration - 0.8]
    if fr.size and fr[0].mean() < 12 and fr[0].std() < 6:
        F("ERROR", "frame 0", "frame 0 of the file is black (it is the thumbnail)")
    if blk:
        F("ERROR", "black frame", f"{len(blk)} black frames in the file, first at {blk[0]:.2f}s", blk[0], blk[-1])
    out += motion_findings(ts, list(fr), tl, "mp4", masked=True, scale=8, freeze=0.15)
    out.append(Finding("INFO", "mp4", "stats", f"{dur:.1f}s, {lufs} LUFS, true peak {tp} dBFS, sample peak "
                       f"{20 * np.log10(float(np.abs(a).max()) + 1e-12):+.2f} dBFS"))
    return out


# ================================================================ main
def run(pkg, mp4=None, style="illustrated", fps=4.0, only=None):
    groups = set(only or ("script", "timeline", "layout", "mp4"))
    from engine.ep import resolve
    pkg = "episodes." + resolve(pkg)
    ep = importlib.import_module(pkg + ".episode")
    sc = importlib.import_module(pkg + ".script")
    here = os.path.dirname(ep.__file__)
    tl, ctx, _, Q = ep.build(style)
    found = []
    if "script" in groups:
        found += check_script(sc, Q, here)
    if "timeline" in groups:
        found += check_timeline(tl, ctx, tl.captions)
    if "layout" in groups:
        print(f"rendering {tl.duration * fps:.0f} sample frames for the layout checks...", flush=True)
        found += check_layout(tl, ctx, fps)
    if "mp4" in groups:
        if mp4 is None:
            mp4s = sorted(glob.glob(os.path.join(here, "out", "*.mp4")), key=os.path.getmtime)
            mp4 = mp4s[-1] if mp4s else None
        if mp4:
            found += check_mp4(mp4, tl, here)
        else:
            found.append(Finding("INFO", "mp4", "skipped", "no MP4 in out/ yet"))
    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    found.sort(key=lambda f: (order[f.sev], f.group, f.t0 if f.t0 is not None else -1))
    write_report(here, pkg, found, groups, mp4)
    return found


def write_report(here, pkg, found, groups, mp4):
    rv = os.path.join(here, "review")
    os.makedirs(rv, exist_ok=True)
    n = {s: sum(f.sev == s for f in found) for s in ("ERROR", "WARN")}
    lines = [f"# Automatic checks — {pkg}", "",
             f"Groups: {', '.join(sorted(groups))}" + (f" · MP4: `{os.path.basename(mp4)}`" if mp4 else ""),
             f"**{n['ERROR']} errors, {n['WARN']} warnings.** Errors must be fixed before the judge; read every "
             f"warning and fix it or note why it is fine.", ""]
    for sev in ("ERROR", "WARN", "INFO"):
        rows = [f for f in found if f.sev == sev]
        if not rows:
            continue
        lines += [f"## {sev}", ""]
        for f in rows:
            why = f" _({f.lesson})_" if f.lesson else ""
            lines.append(f"- `{f.when():>14}` **{f.group} · {f.check}** — {f.msg}{why}")
        lines.append("")
    if not found:
        lines.append("Nothing found.")
    with open(os.path.join(rv, "checks.md"), "w", encoding="utf8") as fh:
        fh.write("\n".join(lines))
    with open(os.path.join(rv, "checks.json"), "w", encoding="utf8") as fh:
        json.dump([asdict(f) for f in found], fh, indent=1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode_pkg")
    ap.add_argument("--mp4")
    ap.add_argument("--style", default="illustrated")
    ap.add_argument("--fps", type=float, default=4.0, help="layout samples per second")
    ap.add_argument("--only", help="comma list of groups: script,timeline,layout,mp4")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    found = run(a.episode_pkg, a.mp4, a.style, a.fps, a.only.split(",") if a.only else None)
    for f in found:
        print(f"{f.sev:5} {f.when():>15}  {f.group}/{f.check}: {f.msg}")
    n = sum(f.sev == "ERROR" for f in found)
    print(f"\n{n} errors, {sum(f.sev == 'WARN' for f in found)} warnings -> review/checks.md")
    sys.exit(1 if n else 0)


if __name__ == "__main__":
    main()
