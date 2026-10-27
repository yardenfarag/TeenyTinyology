"""P1 engine demo (~22 s, no narration): the logo intro with its jingle, camera moves over a 2x2 board, titles,
the eraser, a zoom-out to the whole board; plus a 1280x720 thumbnail.

Round 1 (2026-10-26) also had chapter cards, cast stickers and a "pause and think" timer: the owner dropped all
three (a title is enough, no cast for now, no questions) and asked for a livelier intro with a cute sound.

    .venv/Scripts/python -m lessons.bake_p1.demo stills
    .venv/Scripts/python -m lessons.bake_p1.demo render
"""
import argparse
import os

import cairo
import numpy as np

from engine import board as B
from engine import render
from engine.audio import mix

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "out")
INTRO_LUFS = -18          # the jingle sits a little under the narrator (lessons are normalised to -14)


def build():
    b = B.Board(w=3840, h=2160)

    # A (top-left frame): the logo intro
    t = b.logo(960, 520, 0.3)

    # B (top-right frame): a title, cocci, the eraser, bacilli in the cleared space
    t = b.cam.move(t + 0.7, 1.1, cx=2880, cy=540)
    t = b.title("Three shapes", 2050, 230, t + 0.1)
    cocci = [(2200, 520, 1), (2318, 510, 2), (2260, 620, 3)]
    for i, (x, y, s) in enumerate(cocci):
        b.stroke(B.circle(x, y, 60, seed=s), t + 0.2 + i * 0.36, 0.3, B.GREEN, width=7)
    lab = b.write("cocci", 2260, 790, 90, B.NAVY, t + 1.4, align="center")
    e = b.erase(2080, 420, 2560, 830, lab.t1 + 1.2, 1.1)
    rod = B.capsule(2310, 560, 340, 124, ang=-0.12)
    b.stroke(rod, e.t1 + 0.55, 0.7, B.BLUE, width=7)
    bac = b.write("bacilli", 2310, 790, 90, B.NAVY, e.t1 + 1.35, align="center")
    b.hatch(rod, bac.t1 + 0.08, 0.38, B.BLUE)

    # C (bottom-left frame): a second title; the camera pans straight down so it never crosses empty board
    t = b.cam.move(bac.t1 + 0.9, 1.1, cx=2880, cy=1620)
    t = b.title("Spirals", 2050, 1310, t + 0.1)
    sp = B.wavy_cell(2500, 1640, 400, 46, 46, waves=2.0)
    b.stroke(sp, t + 0.2, 0.95, B.RED, width=7)
    spl = b.write("spirilla", 2500, 1880, 90, B.NAVY, t + 1.3, align="center")
    b.hatch(sp, spl.t1 + 0.1, 0.45, B.RED)

    # the whole board
    t = b.cam.frame(spl.t1 + 1.2, 1.6, 0, 0, 3840, 2160, margin=0)
    return b, t + 2.0


def frame_fn(b):
    return lambda c, t: b.render(c, t, "marker")


def audio(b, dur, path):
    x = b.sound(dur)
    mix.write_wav(path, x / (np.abs(x).max() + 1e-9) * 0.5)
    gain = 10 ** ((INTRO_LUFS - mix.measure_lufs(path)) / 20) * 0.5 / (np.abs(x).max() + 1e-9)
    mix.write_wav(path, x * gain)
    print(f"intro jingle {mix.measure_lufs(path):.1f} LUFS, peak {20 * np.log10(np.abs(x * gain).max()):.1f} dBFS")
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["stills", "render"])
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    b, dur = build()
    print(f"duration {dur:.1f} s")
    fn = frame_fn(b)
    print(render.thumbnail(fn, 3.5, os.path.join(OUT, "thumbnail.png")))
    if a.cmd == "stills":
        times = [0.35 + i * 0.2 for i in range(16)] + [dur * (i + 0.5) / 8 for i in range(8)]
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
        paths = []
        for t in times:
            fn(cairo.Context(s), t)
            p = os.path.join(OUT, f"still_{t:05.2f}.png")
            s.write_to_png(p)
            paths.append(p)
        print(render.contact_sheet(paths, os.path.join(OUT, "sheet.png"), cols=4, width=2400))
        return
    wav = audio(b, dur, os.path.join(OUT, "demo_audio.wav"))
    p = os.path.join(OUT, "p1_demo.mp4")
    render.encode(fn, dur, p, size=(1920, 1080), audio_wav=wav)
    print(p)


if __name__ == "__main__":
    main()
