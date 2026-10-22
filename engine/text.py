"""Text rendering with real font files (assets/fonts, SIL Open Font License) via Pillow, composited into cairo.

cairo's toy font API on Windows only sees system-installed fonts, so text is rasterised with Pillow at the
current device scale (stays crisp when zoomed/popped) and cached.

    text.set_family("Nunito")           # series font (see CLAUDE.md)
    text.width("Hello", 52, bold=True)
    text.draw(c, "Hello", x, baseline_y, 52, col, alpha=1, bold=True)
"""
import math
import os
from collections import OrderedDict
from functools import lru_cache

import cairo
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "fonts"))
FAMILIES = {
    "Nunito": {"regular": "nunito-400-normal.ttf", "semibold": "nunito-700-normal.ttf",
               "bold": "nunito-800-normal.ttf", "italic": "nunito-400-italic.ttf"},
    "Quicksand": {"regular": "quicksand-500-normal.ttf", "semibold": "quicksand-700-normal.ttf",
                  "bold": "quicksand-700-normal.ttf"},
    "Fredoka": {"regular": "fredoka-400-normal.ttf", "semibold": "fredoka-600-normal.ttf",
                "bold": "fredoka-600-normal.ttf"},
    "Baloo 2": {"regular": "baloo-2-500-normal.ttf", "semibold": "baloo-2-700-normal.ttf",
                "bold": "baloo-2-700-normal.ttf"},
}
_state = {"family": "Nunito"}


def set_family(name):
    if name not in FAMILIES:
        raise ValueError(f"unknown font family {name}; have {list(FAMILIES)}")
    _state["family"] = name


def family():
    return _state["family"]


def _file(fam, bold, italic, semibold=False):
    f = FAMILIES[fam or _state["family"]]
    if italic and "italic" in f and not bold:
        return f["italic"]
    if bold:
        return f["bold"]
    if semibold:
        return f["semibold"]
    return f["regular"]


@lru_cache(maxsize=256)
def _font(path, px):
    return ImageFont.truetype(os.path.join(FONT_DIR, path), max(4, px))


def width(txt, size, bold=False, italic=False, fam=None, semibold=False):
    return _font(_file(fam, bold, italic, semibold), int(round(size * 4))).getlength(txt) / 4


_cache = OrderedDict()


def _raster(txt, path, px, rgb):
    key = (txt, path, px, rgb)
    hit = _cache.get(key)
    if hit is not None:
        _cache.move_to_end(key)
        return hit
    f = _font(path, px)
    asc, desc = f.getmetrics()
    w = int(math.ceil(f.getlength(txt))) + 8
    h = asc + desc + 8
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((4, 4), txt, font=f, fill=255)
    a = np.asarray(mask, dtype=np.float32) / 255.0
    bgra = np.zeros((h, w, 4), dtype=np.uint8)
    bgra[..., 0] = (a * rgb[2] * 255).astype(np.uint8)
    bgra[..., 1] = (a * rgb[1] * 255).astype(np.uint8)
    bgra[..., 2] = (a * rgb[0] * 255).astype(np.uint8)
    bgra[..., 3] = (a * 255).astype(np.uint8)
    stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_ARGB32, w)
    buf = np.zeros((h, stride // 4, 4), dtype=np.uint8)
    buf[:, :w] = bgra
    surf = cairo.ImageSurface.create_for_data(memoryview(buf), cairo.FORMAT_ARGB32, w, h, stride)
    item = (surf, buf, asc)
    _cache[key] = item
    if len(_cache) > 3000:
        _cache.popitem(last=False)
    return item


def draw(c, txt, x, y, size, col, alpha=1.0, bold=False, italic=False, fam=None, semibold=False):
    """Draw txt with its left baseline at (x, y) in user space."""
    if alpha <= 0 or not txt:
        return
    m = c.get_matrix()
    k = max(0.05, math.hypot(m.xx, m.yx))
    px = int(round(size * k))
    rgb = (round(col[0], 3), round(col[1], 3), round(col[2], 3))
    surf, _, asc = _raster(txt, _file(fam, bold, italic, semibold), px, rgb)
    c.save()
    c.translate(x, y)
    c.scale(1 / k * (size * k / px if px else 1), 1 / k * (size * k / px if px else 1))
    c.set_source_surface(surf, -4, -asc - 4)
    c.paint_with_alpha(alpha)
    c.restore()


def center(c, txt, x, y, size, col, alpha=1.0, bold=False, italic=False, fam=None, semibold=False):
    draw(c, txt, x - width(txt, size, bold, italic, fam, semibold) / 2, y, size, col, alpha, bold, italic, fam, semibold)
