"""Build a review packet for the video-judge agent from a finished episode.

Usage: python -m engine.judge_kit episodes.<pkg> <path/to/episode.mp4> [--style illustrated]
Writes episodes/<pkg>/review/judge/ :
  sheet_XX.png        contact sheets, one frame every 0.5 s from the ENCODED video (12 frames per sheet, timestamped)
  key_XXX.XX.png      full-resolution stills: every scene start/middle, caption handoffs, first/last second
  safezone_XXX.png    the same stills with TikTok / YouTube Shorts UI overlays drawn on top
  packet.md           script, SFX list, scene + caption timeline, loudness / silence stats, facts.md
"""
import argparse
import importlib
import json
import os
import re
import shutil
import subprocess

import cairo

from engine.audio.common import ffmpeg_exe
from engine.core import H, W
from engine.render import render_frame


def _run(args):
    return subprocess.run([ffmpeg_exe(), "-hide_banner", *args], capture_output=True, text=True)


def frames_every(mp4, out_dir, step=0.5, per_sheet=12):
    tmp = os.path.join(out_dir, "_frames")
    os.makedirs(tmp, exist_ok=True)
    _run(["-v", "error", "-y", "-i", mp4, "-vf", f"fps={1 / step},scale=360:-1", os.path.join(tmp, "f_%05d.png")])
    files = sorted(os.listdir(tmp))
    sheets = []
    for k in range(0, len(files), per_sheet):
        chunk = files[k:k + per_sheet]
        args, filt = [], ""
        for i, f in enumerate(chunk):
            t = (k + i) * step
            args += ["-i", os.path.join(tmp, f)]
            filt += (f"[{i}]drawtext=text='{t:.1f}s':x=8:y=8:fontsize=26:fontcolor=white:box=1:boxcolor=black@0.6[d{i}];")
        n = len(chunk)
        filt += "".join(f"[d{i}]" for i in range(n)) + (f"hstack={n}" if n > 1 else "null")
        out = os.path.join(out_dir, f"sheet_{k // per_sheet:02d}.png")
        _run(["-v", "error", "-y", *args, "-filter_complex", filt, "-frames:v", "1", out])
        sheets.append(out)
    shutil.rmtree(tmp, ignore_errors=True)
    return sheets


def safe_zone_overlay(c):
    """Approximate TikTok + YouTube Shorts UI (1080x1920): right action rail, bottom caption/description, top bar."""
    c.set_source_rgba(1, 0, 0, 0.22)
    c.rectangle(930, 700, 150, 820)     # like / comment / share / profile rail
    c.fill()
    c.set_source_rgba(1, 0.4, 0, 0.22)
    c.rectangle(0, 1520, 1080, 400)     # username, description, music ticker, progress bar
    c.fill()
    c.set_source_rgba(0, 0.3, 1, 0.18)
    c.rectangle(0, 0, 1080, 170)        # top tabs / search
    c.fill()
    c.set_source_rgba(1, 1, 1, 0.9)
    c.select_font_face("Georgia")
    c.set_font_size(26)
    for x, y, txt in ((940, 690, "app buttons"), (20, 1510, "app description / username"), (20, 200, "app top bar")):
        c.move_to(x, y)
        c.show_text(txt)


def loudness(mp4):
    r = _run(["-i", mp4, "-af", "ebur128=peak=true", "-f", "null", "-"])
    txt = r.stderr
    summ = txt[txt.rfind("Summary:"):]
    short = re.findall(r"t:\s*([\d.]+).*?S:\s*(-?[\d.]+)", txt)
    per_sec = {}
    for t, sv in short:
        per_sec[int(float(t))] = float(sv)
    sil = _run(["-i", mp4, "-af", "silencedetect=n=-45dB:d=1.0", "-f", "null", "-"]).stderr
    gaps = re.findall(r"silence_start: ([\d.]+)|silence_end: ([\d.]+)", sil)
    return summ.strip(), per_sec, gaps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode_pkg")
    ap.add_argument("mp4")
    ap.add_argument("--style", default="illustrated")
    a = ap.parse_args()
    ep = importlib.import_module(a.episode_pkg + ".episode")
    sc = importlib.import_module(a.episode_pkg + ".script")
    here = os.path.dirname(ep.__file__)
    out = os.path.join(here, "review", "judge")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)

    tl, ctx, _, Q = ep.build(a.style)
    sheets = frames_every(a.mp4, out)

    keys = {0.4, tl.duration - 0.8}
    for s in tl.scenes:
        keys.add(round(s.start + 0.5, 2))
        keys.add(round((s.start + min(s.end, tl.duration)) / 2, 2))
    caps = tl.captions
    for x, y in zip(caps, caps[1:]):
        if abs(y.start - x.end) < 0.25:
            keys.add(round(y.start - 0.03, 2))
    keys = sorted(k for k in keys if 0 <= k < tl.duration)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    for k in keys:
        render_frame(cairo.Context(surf), k, tl, ctx)
        surf.write_to_png(os.path.join(out, f"key_{k:06.2f}.png"))
    for i, s in enumerate(tl.scenes):
        k = round((s.start + min(s.end, tl.duration)) / 2, 2)
        c = cairo.Context(surf)
        render_frame(c, k, tl, ctx)
        safe_zone_overlay(c)
        surf.write_to_png(os.path.join(out, f"safezone_{i:02d}_{k:06.2f}.png"))

    summ, per_sec, gaps = loudness(a.mp4)
    facts = os.path.join(here, "facts.md")
    lines = ["# Review packet", "", f"Video: `{a.mp4}`", f"Duration: {tl.duration:.2f}s, style: {a.style}", "",
             "## Script (as narrated)"]
    for ln in sc.SCRIPT:
        cue = Q[ln.id]
        txt = ln.text or f"[silent beat — sound effect: {ln.sfx}]"
        lines.append(f"- `{cue.start:6.2f}-{cue.end:6.2f}` **{ln.id}**: {txt}")
    lines += ["", "## Sound effects (word-anchored)"]
    for row in getattr(sc, "SFX", []):
        lines.append(f"- {row}")
    lines += ["", "## Scenes"]
    for i, s in enumerate(tl.scenes):
        lines.append(f"- {i:02d} `{s.start:6.2f}-{min(s.end, tl.duration):6.2f}` {s.fn.__name__} ({s.transition})")
    lines += ["", "## Captions"]
    for cp in caps:
        lines.append(f"- `{cp.start:6.2f}-{cp.end:6.2f}` " + " ".join(w for w, _, _ in cp.words))
    lines += ["", "## Loudness (EBU R128)", "```", summ, "```",
              "Short-term loudness per second (LUFS): " + json.dumps(per_sec), "",
              "Silence gaps (< -45 dB, >= 1 s): " + json.dumps(gaps), "",
              "## Files", f"- contact sheets (every 0.5 s of the encoded MP4): {', '.join(os.path.basename(p) for p in sheets)}",
              "- full-res key frames: key_*.png ; safe-zone overlays: safezone_*.png", "",
              "## Facts sheet", "", open(facts, encoding="utf8").read() if os.path.exists(facts) else "(missing)"]
    with open(os.path.join(out, "packet.md"), "w", encoding="utf8") as f:
        f.write("\n".join(lines))
    print("packet", os.path.join(out, "packet.md"))
    print(len(sheets), "sheets,", len(keys), "key frames,", len(tl.scenes), "safe-zone frames")


if __name__ == "__main__":
    main()
