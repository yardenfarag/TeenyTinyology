"""Board bake: the same 20 s of a lesson, marker only, Gochi Hand, voice only.

Round 1 (2026-10-24) compared hand / marker / none and four fonts: the owner chose marker only + Gochi Hand.
Round 2 (2026-10-26) tried two rebuilt marker sounds: the owner dropped marker sound altogether.

    .venv/Scripts/python -m lessons.bake_board.bake stills
    .venv/Scripts/python -m lessons.bake_board.bake fonts
    .venv/Scripts/python -m lessons.bake_board.bake render
"""
import argparse
import os

import cairo

from engine import board as B
from engine import render, text
from engine.audio import mix
from engine.voice import narrate

from .script import SCRIPT

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "out")
TOOL = "marker"
TAG = "marker only · voice only"



def build():
    voice, cues, _, end = narrate(SCRIPT, os.path.join(HERE, "voice_cache"), t0=1.4)
    c = cues
    b = B.Board()

    # title + gold underline
    title = b.write("Bacteria shapes", 160, 200, 104, B.NAVY, c["l1"].start - 0.3, bold=True, cps=10)
    b.stroke(B.line(150, 232, 170 + title.w, 228, sag=5), title.t1 + 0.12, 0.4, B.GOLD, width=10)

    # cocci
    t = c["l2"].start - 0.2
    cocci = [(352, 500, 1), (470, 490, 2), (412, 600, 3)]
    for i, (x, y, s) in enumerate(cocci):
        b.stroke(B.circle(x, y, 60, seed=s), t + i * 0.36, 0.3, B.GREEN, width=7)
    b.write("cocci", 410, 800, 90, B.NAVY, c["l2"].word("cocci") - 0.05, align="center")
    b.write("= berry", 410, 885, 56, B.GREEN, c["l2"].word("berry") - 0.1, align="center")
    t = c["l2"].word("berry") + 0.65
    for i, (x, y, s) in enumerate(cocci):
        b.hatch(B.circle(x, y, 60, seed=s), t + i * 0.24, 0.22, B.GREEN, gap=15)

    # bacilli
    rod = B.capsule(960, 545, 340, 124, ang=-0.12)
    b.stroke(rod, c["l3"].start - 0.15, 0.7, B.BLUE, width=7)
    bac = b.write("bacilli", 960, 800, 90, B.NAVY, c["l3"].word("bacilli") - 0.05, align="center")
    b.hatch(rod, bac.t1 + 0.08, 0.38, B.BLUE)

    # spirilla
    sp = B.wavy_cell(1530, 545, 400, 46, 46, waves=2.0)
    b.stroke(sp, c["l4"].word("spirals") - 0.05, 0.95, B.RED, width=7)
    spl = b.write("spirilla", 1530, 800, 90, B.NAVY, c["l4"].word("spirilla") - 0.05, align="center")
    b.hatch(sp, spl.t1 + 0.1, 0.45, B.RED)

    # the joke lands; a little gold star for "never forget"
    b.stroke(B.star(220 + title.w, 168, 34), c["l5"].word("forget") - 0.25, 0.6, B.GOLD_DK, width=7)
    return b, voice, end + 1.2


def frame_fn(b, tool, tag):
    def fn(c, t):
        b.render(c, t, tool)
        text.draw(c, tag, 1880 - text.width(tag, 30, fam="Nunito"), 1040, 30, B.MUTED, fam="Nunito")
    return fn


def font_sheet(path):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
    c = cairo.Context(s)
    c.set_source_surface(B.Board().background(), 0, 0)
    c.paint()
    fams = ["Kalam", "Patrick Hand", "Caveat", "Gochi Hand"]
    for i, f in enumerate(fams):
        y = 200 + i * 230
        text.draw(c, f"{i + 1}. {f}", 90, y - 110, 30, B.MUTED, fam="Nunito")
        text.draw(c, "Bacteria shapes", 90, y, 84, B.NAVY, bold=True, fam=f)
        text.draw(c, "cocci · bacilli", 800, y, 70, B.BLUE, fam=f)
        text.draw(c, "facultative anaerobe", 1290, y, 56, B.RED, fam=f)
        text.draw(c, "Gram-positive cells keep the purple dye", 90, y + 70, 46, B.NAVY, fam=f)
    s.write_to_png(path)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["stills", "fonts", "render"])
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.cmd == "fonts":
        print(font_sheet(os.path.join(OUT, "fonts.png")))
        return
    b, voice, dur = build()
    if a.cmd == "stills":
        times = [1.6, 2.4, 3.6, 5.6, 6.6, 8.4, 9.0, 10.2, 11.0, 11.8, 12.7, 13.6, 17.8, dur - 0.1]
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
        paths = []
        for t in times:
            frame_fn(b, TOOL, TAG)(cairo.Context(s), t)
            p = os.path.join(OUT, f"still_{t:05.2f}.png")
            s.write_to_png(p)
            paths.append(p)
        render.contact_sheet(paths, os.path.join(OUT, "sheet.png"), cols=4, width=2400)
        print(os.path.join(OUT, "sheet.png"))
        return
    wav = B.mixdown(b, voice, dur, os.path.join(OUT, "bake_audio.wav"))
    p = os.path.join(OUT, "bake.mp4")
    render.encode(frame_fn(b, TOOL, TAG), dur, p, size=(1920, 1080), audio_wav=wav)
    print(p, f"{mix.measure_lufs(p):.1f} LUFS")


if __name__ == "__main__":
    main()
