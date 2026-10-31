"""Cover image for the upload pack: the hook frame (lens on Dilly, Biscuit napping, Poppy) with the title over it."""
import io
import os
from contextlib import redirect_stdout

import cairo

from engine import text as tx
from engine.core import H, W
from engine.scene import render_frame
from episodes.e003_biscuit_dilly.episode import HERE, build

TITLE = ["How a worm", "gets into a dog"]


def main():
    with redirect_stdout(io.StringIO()):
        tl, ctx, _, Q = build("illustrated")
    t = Q["biscuit"].start - 0.1          # the hook labels have faded and no caption is up
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    render_frame(c, t, tl, ctx)
    # a soft dark band at the top so the title sits on something, without hiding the lens
    g = cairo.LinearGradient(0, 170, 0, 640)
    g.add_color_stop_rgba(0, 0.12, 0.16, 0.23, 0.62)
    g.add_color_stop_rgba(1, 0.12, 0.16, 0.23, 0.0)
    c.set_source(g)
    c.rectangle(0, 0, W, 640)
    c.fill()
    y = 262                               # above the lens, centred on the frame, clear of the badge
    for line in TITLE:
        tx.center(c, line, 540, y, 88, (1, 0.99, 0.96), 1.0, bold=True)
        y += 100
    out = os.path.join(HERE, "out", "cover.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    surf.write_to_png(out)
    print("cover", out)


if __name__ == "__main__":
    main()
