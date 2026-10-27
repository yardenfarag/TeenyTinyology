"""Build a review packet for the lesson-judge agent from a finished Lesson.

Usage: python -m engine.lesson_kit lessons.<pkg> <path/to/lesson.mp4>
The lesson package must have script.py (SCRIPT) and lesson.py with build() -> (board, voice, cues, duration).
Writes lessons/<pkg>/review/judge/ :
  sheet_XX.png      contact sheets, one frame per second of the ENCODED video (12 per sheet, timestamped)
  key_XXX.XX.png    full-resolution stills: the end of every narration line, every eraser, the final board
  packet.md         script with timings, board timeline (what is written / drawn / erased when, camera moves),
                    loudness and silence stats, facts.md
"""
import argparse
import importlib
import json
import os
import shutil

import cairo

from engine import board as B
from engine.judge_kit import frames_every, loudness


_COLOURS = {B.NAVY: "navy", B.BLUE: "blue", B.RED: "red", B.GREEN: "green", B.GOLD: "gold", B.GOLD_DK: "dark gold",
            B.MUTED: "grey"}


def _where(it):
    if hasattr(it, "x"):
        x, y = it.x, it.y
    elif getattr(it, "pts", None):
        x = sum(p[0] for p in it.pts) / len(it.pts)
        y = sum(p[1] for p in it.pts) / len(it.pts)
    else:
        return ""
    return f" at ({x:.0f}, {y:.0f}), {_COLOURS.get(tuple(it.col), 'colour ' + str(tuple(round(v, 2) for v in it.col)))}"


def _what(it):
    if isinstance(it, B.Text):
        return f'write "{it.txt}"'
    if isinstance(it, B.PopText):
        return f'pop "{it.txt}" (logo)'
    if isinstance(it, B.LensSwoop):
        return "lens swoop (logo)"
    if isinstance(it, B.Hatch):
        return "colour in (hatch)"
    return "draw stroke"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lesson_pkg")
    ap.add_argument("mp4")
    a = ap.parse_args()
    ls = importlib.import_module(a.lesson_pkg + ".lesson")
    sc = importlib.import_module(a.lesson_pkg + ".script")
    here = os.path.dirname(ls.__file__)
    out = os.path.join(here, "review", "judge")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)

    b, voice, cues, dur = ls.build()
    sheets = frames_every(a.mp4, out, step=1.0)

    keys = {dur - 0.3}
    for ln in sc.SCRIPT:
        keys.add(round(cues[ln.id].end + 0.1, 2))
    for e in b.erases:
        keys.add(round(e.t0 - 0.1, 2))
        keys.add(round(e.t1 + B.ERASER_IN + 0.1, 2))
    keys = sorted(k for k in keys if 0 <= k < dur)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, b.vw, b.vh)
    for k in keys:
        b.render(cairo.Context(s), k)
        s.write_to_png(os.path.join(out, f"key_{k:06.2f}.png"))

    summ, per_sec, gaps = loudness(a.mp4)
    lines = ["# Lesson review packet", "", f"Video: `{a.mp4}`", f"Duration: {dur:.2f}s ({dur / 60:.1f} min)",
             f"Board: {b.w}x{b.h}, frame {b.vw}x{b.vh}", "", "## Script (as narrated)"]
    for ln in sc.SCRIPT:
        cue = cues[ln.id]
        lines.append(f"- `{cue.start:7.2f}-{cue.end:7.2f}` **{ln.id}**: {ln.text or '[silent beat]'}")
    lines += ["", "## Board timeline (board coordinates)"]
    events = [(it.t0, it.t1, _what(it) + _where(it)) for it in b.items]
    events += [(e.t0, e.t1, f"ERASE rows {e.pts[0]} .. {e.pts[-1]}") for e in b.erases]
    events += [(t0, t1, f"CAMERA {tuple(round(v, 2) for v in fr)} -> {tuple(round(v, 2) for v in to)}")
               for t0, t1, fr, to in b.cam.moves]
    for t0, t1, txt in sorted(events, key=lambda e: e[0]):
        lines.append(f"- `{t0:7.2f}-{t1:7.2f}` {txt}")
    facts = os.path.join(here, "facts.md")
    lines += ["", "## Loudness (EBU R128)", "```", summ, "```",
              "Short-term loudness per second (LUFS): " + json.dumps(per_sec), "",
              "Silence gaps (< -45 dB, >= 1 s): " + json.dumps(gaps), "",
              "## Files", f"- contact sheets (one frame per second of the encoded MP4): "
              f"{', '.join(os.path.basename(p) for p in sheets)}",
              "- full-res key frames (end of each line, around each eraser, final board): key_*.png", "",
              "## Facts sheet", "", open(facts, encoding="utf8").read() if os.path.exists(facts) else "(missing)"]
    with open(os.path.join(out, "packet.md"), "w", encoding="utf8") as f:
        f.write("\n".join(lines))
    print("packet", os.path.join(out, "packet.md"))
    print(len(sheets), "sheets,", len(keys), "key frames")


if __name__ == "__main__":
    main()
