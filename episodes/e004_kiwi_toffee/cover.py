"""Cover image for the upload pack: the teaser frame (Kiwi guarding the sac) with the title over it."""
import io
import os
from contextlib import redirect_stdout

import cairo

from engine import text as tx
from engine.core import H, W
from engine.scene import render_frame
from episodes.e004_kiwi_toffee.episode import HERE, build

TITLE = ["The barnacle that", "makes a crab a mum"]


def main():
    with redirect_stdout(io.StringIO()):
        tl, ctx, _, Q = build("illustrated")
    t = 0.5                            # the teaser, with its own labels switched off (the title replaces them)
    ctx["teaser_labels"] = 0.0
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    render_frame(c, t, tl, ctx)
    g = cairo.LinearGradient(0, 300, 0, 760)
    g.add_color_stop_rgba(0, 0.10, 0.18, 0.20, 0.62)
    g.add_color_stop_rgba(1, 0.10, 0.18, 0.20, 0.0)
    c.set_source(g)
    c.rectangle(0, 0, W, 760)
    c.fill()
    y = 420                               # below the badge, above Kiwi
    for line in TITLE:
        tx.center(c, line, 540, y, 84, (1, 0.99, 0.96), 1.0, bold=True)
        y += 98
    out = os.path.join(HERE, "out", "cover.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    surf.write_to_png(out)
    print("cover", out)


if __name__ == "__main__":
    main()
