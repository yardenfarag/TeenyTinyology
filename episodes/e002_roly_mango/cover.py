"""Cover image for the upload pack: the hook frame with the episode title over it."""
import os

import cairo

from engine import text as tx
from engine.core import H, W, rounded_rect
from engine.scene import render_frame
from episodes.e002_roly_mango.episode import HERE, build

TITLE = ["Its tongue", "is alive"]


def main():
    tl, ctx, _, Q = build("illustrated")
    t = Q["hook2"].end - 0.2
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    render_frame(c, t, tl, ctx)
    # darken the top so the title sits on something, without hiding the fish
    g = cairo.LinearGradient(0, 180, 0, 760)
    g.add_color_stop_rgba(0, 0.05, 0.10, 0.16, 0.55)
    g.add_color_stop_rgba(1, 0.05, 0.10, 0.16, 0.0)
    c.set_source(g)
    c.rectangle(0, 0, W, 760)
    c.fill()
    y = 360
    for line in TITLE:
        tx.center(c, line, 480, y, 118, (1, 0.99, 0.96), 1.0, bold=True)
        y += 134
    out = os.path.join(HERE, "out", "cover.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    surf.write_to_png(out)
    print("cover", out)


if __name__ == "__main__":
    main()
