"""Shared math, color, geometry and text helpers."""
import math
import random

import cairo

W, H = 1080, 1920
FPS = 30
TAU = 2 * math.pi


# ---------------------------------------------------------------- timing / easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def prog(t, a, b):
    """0..1 progress of t through [a, b]."""
    return clamp((t - a) / (b - a)) if b != a else float(t >= b)


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_in(t):
    t = clamp(t)
    return t * t * t


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def back_out(t, k=1.70158):
    t = clamp(t)
    return 1 + (k + 1) * (t - 1) ** 3 + k * (t - 1) ** 2


def elastic_out(t):
    t = clamp(t)
    if t in (0.0, 1.0):
        return t
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (TAU / 3)) + 1


def window(t, a, b, fi=0.25, fo=0.25):
    """Fade in over fi after a, fade out over fo before b."""
    return ease(prog(t, a, a + fi)) * (1 - ease(prog(t, b - fo, b)))


def squash(t, t0, dur=0.35, amt=0.25):
    """Squash & stretch scale pair (sx, sy) for a landing at t0."""
    k = prog(t, t0, t0 + dur)
    if k <= 0 or k >= 1:
        return 1.0, 1.0
    a = amt * math.sin(k * math.pi) * (1 - k)
    return 1 + a, 1 - a


# ---------------------------------------------------------------- color
def hexc(h, a=1.0):
    h = h.lstrip("#")
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


def mix(c1, c2, t):
    return tuple(lerp(a, b, t) for a, b in zip(c1, c2))


def with_alpha(c, a):
    return (c[0], c[1], c[2], a)


def shade(c, k):
    """k<0 darken, k>0 lighten."""
    if k < 0:
        return (c[0] * (1 + k), c[1] * (1 + k), c[2] * (1 + k), c[3])
    return (c[0] + (1 - c[0]) * k, c[1] + (1 - c[1]) * k, c[2] + (1 - c[2]) * k, c[3])


class Palette:
    """base / light / dark / line colors for one material."""

    def __init__(self, base, light=None, dark=None, line=None):
        self.base = hexc(base) if isinstance(base, str) else base
        self.light = hexc(light) if isinstance(light, str) else (light or shade(self.base, 0.45))
        self.dark = hexc(dark) if isinstance(dark, str) else (dark or shade(self.base, -0.5))
        self.line = hexc(line) if isinstance(line, str) else (line or shade(self.base, -0.65))


INK = hexc("#3a2a1a")
WHITE = (1, 1, 1, 1)


# ---------------------------------------------------------------- geometry
def ellipse(c, cx, cy, rx, ry, rot=0.0):
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    c.scale(max(rx, 0.01), max(ry, 0.01))
    c.new_sub_path()
    c.arc(0, 0, 1, 0, TAU)
    c.restore()


def rounded_rect(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()


def rot_pt(px, py, ang):
    ca, sa = math.cos(ang), math.sin(ang)
    return px * ca - py * sa, px * sa + py * ca


def smooth_path(c, pts, closed=False):
    """Catmull-Rom spline through points."""
    n = len(pts)
    if n < 2:
        return
    c.move_to(*pts[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[i - 1] if (i > 0 or closed) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (i + 2 < n or closed) else p2
        c.curve_to(p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6,
                   p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6, *p2)
    if closed:
        c.close_path()


def new_surface(w=W, h=H):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    return s, cairo.Context(s)


def camera(c, z, fx, fy, tx=0.0, ty=0.0):
    """Zoom z around screen focus (fx, fy), then pan by (tx, ty) in world units."""
    c.translate(fx, fy)
    c.scale(z, z)
    c.translate(-fx + tx, -fy + ty)


def group(c, alpha, fn):
    """Draw fn() into a group and composite with alpha."""
    if alpha <= 0:
        return
    if alpha >= 1:
        fn()
        return
    c.push_group()
    fn()
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)


# ---------------------------------------------------------------- text
# All text goes through engine.text (real font files). These wrappers keep the old call signatures.
def set_font(c, size, italic=False, bold=False, face=None):
    """Kept for compatibility with cairo show_text callers; prefer text_center / engine.text.draw."""
    c.select_font_face("Georgia", cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL,
                       cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)


def text_width(c, txt, size, italic=False, bold=False):
    from . import text
    return text.width(txt, size, bold=bold, italic=italic)


def text_center(c, txt, x, y, size, col=INK, italic=False, bold=False, alpha=1.0):
    from . import text
    text.center(c, txt, x, y, size, col, alpha=alpha, bold=bold, italic=italic)


def rng(seed):
    return random.Random(seed)
