"""Cover image for the upload pack: the teaser frame (Mochi asleep, the lens on the moving grain) with the title."""
import io
import os
from contextlib import redirect_stdout

import cairo

from engine import text as tx
from engine.core import H, W
from engine.scene import render_frame
from episodes.e005_mochi_noodle.episode import HERE, build

TITLE = ["The rice grain", "that's a tapeworm"]


def main():
    with redirect_stdout(io.StringIO()):
        tl, ctx, _, Q = build("illustrated")
    t = 0.5                            # the teaser, with its own label switched off (the title replaces it)
    ctx["teaser_labels"] = 0.0
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    render_frame(c, t, tl, ctx)
    g = cairo.LinearGradient(0, 1150, 0, 1700)    # title low, over the floor: the lens and Mochi stay clear
    g.add_color_stop_rgba(0, 0.12, 0.16, 0.23, 0.0)
    g.add_color_stop_rgba(0.35, 0.12, 0.16, 0.23, 0.62)
    g.add_color_stop_rgba(1, 0.12, 0.16, 0.23, 0.62)
    c.set_source(g)
    c.rectangle(0, 1150, W, H - 1150)
    c.fill()
    y = 1330
    for line in TITLE:
        tx.center(c, line, 480, y, 84, (1, 0.99, 0.96), 1.0, bold=True)
        y += 98
    out = os.path.join(HERE, "out", "cover.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    surf.write_to_png(out)
    print("cover", out)


if __name__ == "__main__":
    main()
