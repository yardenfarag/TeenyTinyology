"""Art direction. Characters draw through a Style so the same scene renders in any look.

  cute         glossy storybook shapes, big shiny eyes, blush, soft outline
  real         natural proportions, small eyes, no cartoon faces, micro-texture + rim light
  illustrated  watercolor washes, wobbly ink lines, paper grain over the whole frame
"""
import math

import cairo

from .core import TAU, H, W, ellipse, hexc, new_surface, rng, shade, with_alpha


class Style:
    name = "base"
    faces = True          # draw smiles / blush / expressive brows
    eye_scale = 1.0       # multiplier on eye radius
    realistic = False     # characters may switch to anatomical drawings

    # ---- fills -------------------------------------------------------
    def part(self, c, path, pal, cx, cy, r, seed=0, alpha=1.0):
        """Fill the path produced by path(c) with material pal."""
        raise NotImplementedError

    def ellipse(self, c, cx, cy, rx, ry, rot, pal, seed=0, alpha=1.0):
        self.part(c, lambda cc: ellipse(cc, cx, cy, rx, ry, rot), pal, cx, cy, max(rx, ry), seed, alpha)

    def shine(self, c, cx, cy, rx, ry, rot=0.0, a=0.35):
        ellipse(c, cx, cy, rx, ry, rot)
        c.set_source_rgba(1, 1, 1, a)
        c.fill()

    # ---- lines -------------------------------------------------------
    def limb(self, c, pts, w, pal, alpha=1.0):
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.move_to(*pts[0])
        for p in pts[1:]:
            c.line_to(*p)
        c.set_source_rgba(*with_alpha(pal.base, alpha))
        c.set_line_width(w)
        c.stroke()

    def line(self, c, pts, w, col, alpha=1.0, seed=0):
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.move_to(*pts[0])
        for p in pts[1:]:
            c.line_to(*p)
        c.set_source_rgba(col[0], col[1], col[2], alpha)
        c.set_line_width(w)
        c.stroke()

    # ---- faces -------------------------------------------------------
    def eye(self, c, x, y, r, open_=1.0, look=(0.0, 0.0), iris=None, slit=False):
        r *= self.eye_scale
        if open_ < 0.15:
            c.move_to(x - r, y)
            c.curve_to(x - r * 0.4, y + r * 0.6, x + r * 0.4, y + r * 0.6, x + r, y)
            c.set_source_rgba(0.12, 0.06, 0.03, 1)
            c.set_line_width(max(2.0, r * 0.22))
            c.set_line_cap(cairo.LINE_CAP_ROUND)
            c.stroke()
            return
        ry = r * 1.18 * open_
        lx, ly = look[0] * r * 0.25, look[1] * r * 0.25
        if iris:
            g = cairo.RadialGradient(x - r * 0.2, y - ry * 0.3, 1, x, y, max(r, ry))
            g.add_color_stop_rgba(0, *shade(iris, 0.5))
            g.add_color_stop_rgba(1, *iris)
            ellipse(c, x, y, r, ry)
            c.set_source(g)
            c.fill_preserve()
            c.set_source_rgba(0.2, 0.1, 0.05, 1)
            c.set_line_width(max(1.5, r * 0.12))
            c.stroke()
            ellipse(c, x + lx, y + ly, r * (0.28 if slit else 0.5), ry * (0.85 if slit else 0.55))
        else:
            ellipse(c, x + lx, y + ly, r, ry)
        c.set_source_rgba(0.06, 0.03, 0.02, 1)
        c.fill()
        self.catchlights(c, x + lx, y + ly, r, ry)

    def catchlights(self, c, x, y, r, ry):
        c.arc(x - r * 0.32, y - ry * 0.36, r * 0.34, 0, TAU)
        c.set_source_rgba(1, 1, 1, 0.95)
        c.fill()
        c.arc(x + r * 0.28, y + ry * 0.3, r * 0.15, 0, TAU)
        c.fill()

    def blush(self, c, x, y, r, a=0.5):
        if not self.faces:
            return
        ellipse(c, x, y, r, r * 0.55)
        c.set_source_rgba(1.0, 0.5, 0.55, a)
        c.fill()

    def smile(self, c, x, y, w, col=None, k=1.0):
        if not self.faces:
            return
        col = col or hexc("#4a1d08")
        c.move_to(x - w / 2, y)
        c.curve_to(x - w / 4, y + w * 0.45 * k, x + w / 4, y + w * 0.45 * k, x + w / 2, y)
        c.set_source_rgba(*col)
        c.set_line_width(max(2.0, w * 0.16))
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.stroke()

    def shadow(self, c, x, y, rx, ry, a=0.22):
        g = cairo.RadialGradient(x, y, 0, x, y, rx)
        g.add_color_stop_rgba(0, 0, 0, 0, a)
        g.add_color_stop_rgba(1, 0, 0, 0, 0)
        c.save()
        c.translate(x, y)
        c.scale(1, ry / max(rx, 1))
        c.translate(-x, -y)
        c.arc(x, y, rx, 0, TAU)
        c.set_source(g)
        c.fill()
        c.restore()

    # ---- whole frame -------------------------------------------------
    def frame_overlay(self, c, t):
        """Applied after the scene, before captions."""


# ================================================================ cute storybook
class Cute(Style):
    name = "cute"
    eye_scale = 1.25

    def part(self, c, path, pal, cx, cy, r, seed=0, alpha=1.0):
        path(c)
        g = cairo.RadialGradient(cx - r * 0.3, cy - r * 0.42, 0, cx, cy, r * 1.08)
        g.add_color_stop_rgba(0, *with_alpha(pal.light, alpha))
        g.add_color_stop_rgba(0.5, *with_alpha(pal.base, alpha))
        g.add_color_stop_rgba(1, *with_alpha(pal.dark, alpha))
        c.set_source(g)
        c.fill_preserve()
        c.set_source_rgba(*with_alpha(pal.line, 0.28 * alpha))
        c.set_line_width(max(1.5, r * 0.035))
        c.stroke()

    def limb(self, c, pts, w, pal, alpha=1.0):
        super().limb(c, pts, w, pal, alpha)
        c.move_to(pts[0][0], pts[0][1] - w * 0.18)
        for p in pts[1:]:
            c.line_to(p[0], p[1] - w * 0.18)
        c.set_source_rgba(*with_alpha(pal.light, 0.35 * alpha))
        c.set_line_width(w * 0.28)
        c.stroke()


# ================================================================ realistic
class Real(Style):
    name = "real"
    faces = False
    eye_scale = 0.55
    realistic = True

    def part(self, c, path, pal, cx, cy, r, seed=0, alpha=1.0):
        path(c)
        g = cairo.RadialGradient(cx - r * 0.25, cy - r * 0.5, 0, cx, cy, r * 1.15)
        g.add_color_stop_rgba(0, *with_alpha(shade(pal.base, 0.18), alpha))
        g.add_color_stop_rgba(0.6, *with_alpha(pal.base, alpha))
        g.add_color_stop_rgba(1, *with_alpha(shade(pal.dark, -0.2), alpha))
        c.set_source(g)
        c.fill_preserve()
        c.save()
        c.clip_preserve()
        rnd = rng(seed + 7)
        for _ in range(int(min(400, r * 2.2))):  # micro texture
            c.new_path()
            c.arc(cx + rnd.uniform(-r, r), cy + rnd.uniform(-r, r), rnd.uniform(0.6, 1.8), 0, TAU)
            c.set_source_rgba(*(shade(pal.base, rnd.choice((-0.4, 0.3)))[:3]), 0.08 * alpha)
            c.fill()
        path(c)
        c.set_source_rgba(*with_alpha(shade(pal.light, 0.2), 0.35 * alpha))  # rim light
        c.set_line_width(max(2.0, r * 0.08))
        c.stroke()
        c.restore()
        c.new_path()

    def limb(self, c, pts, w, pal, alpha=1.0):
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        for i, (a, b) in enumerate(zip(pts, pts[1:])):
            ww = w * (1 - 0.22 * i)
            c.move_to(*a)
            c.line_to(*b)
            c.set_source_rgba(*with_alpha(pal.dark, alpha))
            c.set_line_width(ww)
            c.stroke()
            c.move_to(a[0], a[1] - ww * 0.2)
            c.line_to(b[0], b[1] - ww * 0.2)
            c.set_source_rgba(*with_alpha(pal.light, 0.3 * alpha))
            c.set_line_width(ww * 0.25)
            c.stroke()
        for p in pts[1:-1]:  # joints
            c.arc(p[0], p[1], w * 0.42, 0, TAU)
            c.set_source_rgba(*with_alpha(shade(pal.dark, -0.3), alpha))
            c.fill()

    def catchlights(self, c, x, y, r, ry):
        c.arc(x - r * 0.3, y - ry * 0.35, r * 0.22, 0, TAU)
        c.set_source_rgba(1, 1, 1, 0.6)
        c.fill()

    def frame_overlay(self, c, t):
        c.set_source_surface(_grain(0.035, 11 + int(t * 12) % 4), 0, 0)
        c.paint()


# ================================================================ illustrated (ink + watercolor)
def _flat_points(c, path):
    c.save()
    c.set_tolerance(0.5)
    path(c)
    pts = []
    for kind, p in c.copy_path_flat():
        if kind in (cairo.PATH_MOVE_TO, cairo.PATH_LINE_TO):
            pts.append(p)
    c.new_path()
    c.restore()
    return pts


def _wobble(pts, seed, amt):
    rnd = rng(seed)
    ph = [rnd.uniform(0, TAU) for _ in range(3)]
    n = max(len(pts), 1)
    out = []
    for i, (x, y) in enumerate(pts):
        a = i / n * TAU
        d = amt * (math.sin(2 * a + ph[0]) + 0.6 * math.sin(5 * a + ph[1]) + 0.3 * math.sin(9 * a + ph[2])) / 1.9
        x0, y0 = pts[i - 1]
        x1, y1 = pts[(i + 1) % n]
        nx, ny = -(y1 - y0), x1 - x0
        ln = math.hypot(nx, ny) or 1
        out.append((x + nx / ln * d, y + ny / ln * d))
    return out


class Illustrated(Style):
    name = "illustrated"
    eye_scale = 0.9
    ink = hexc("#2a1a10")

    def part(self, c, path, pal, cx, cy, r, seed=0, alpha=1.0):
        rnd = rng(seed + 3)
        path(c)
        c.set_source_rgba(*with_alpha(shade(pal.base, 0.08), 0.88 * alpha))
        c.fill_preserve()
        c.save()
        c.clip()
        for _ in range(int(min(46, 10 + r * 0.25))):  # pigment blooms
            ellipse(c, cx + rnd.uniform(-r, r), cy + rnd.uniform(-r, r), rnd.uniform(r * 0.15, r * 0.55),
                    rnd.uniform(r * 0.1, r * 0.4), rnd.uniform(0, 3))
            c.set_source_rgba(*shade(pal.base, rnd.uniform(-0.35, 0.15))[:3], 0.12 * alpha)
            c.fill()
        g = cairo.LinearGradient(cx, cy - r, cx, cy + r)
        g.add_color_stop_rgba(0, 1, 1, 1, 0.22 * alpha)
        g.add_color_stop_rgba(1, 0.25, 0.08, 0.0, 0.22 * alpha)
        c.set_source(g)
        c.paint()
        c.restore()
        path(c)  # pigment pooling at the edge
        c.set_source_rgba(*with_alpha(pal.dark, 0.3 * alpha))
        c.set_line_width(max(3.0, r * 0.07))
        c.stroke()
        self.ink_path(c, path, seed, alpha, w=max(2.2, min(4.2, r * 0.05)), amt=max(1.5, r * 0.025))

    def ink_path(self, c, path, seed, alpha=1.0, w=3.2, amt=2.5):
        pts = _wobble(_flat_points(c, path), seed, amt)
        if len(pts) < 2:
            return
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        n = len(pts)
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            c.move_to(*a)
            c.line_to(*b)
            c.set_source_rgba(*self.ink[:3], 0.9 * alpha)
            c.set_line_width(w * (0.7 + 0.5 * abs(math.sin(i * 0.09 + seed))))
            c.stroke()

    def limb(self, c, pts, w, pal, alpha=1.0):
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.move_to(*pts[0])
        for p in pts[1:]:
            c.line_to(*p)
        c.set_source_rgba(*with_alpha(pal.base, 0.55 * alpha))
        c.set_line_width(w)
        c.stroke()
        self.line(c, pts, max(2.4, w * 0.28), self.ink, 0.9 * alpha)

    def line(self, c, pts, w, col, alpha=1.0, seed=0):
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        for i, (a, b) in enumerate(zip(pts, pts[1:])):
            c.move_to(*a)
            c.line_to(*b)
            c.set_source_rgba(col[0], col[1], col[2], alpha)
            c.set_line_width(w * (0.8 + 0.35 * math.sin(i * 1.3 + seed)))
            c.stroke()

    def catchlights(self, c, x, y, r, ry):
        c.arc(x - r * 0.3, y - ry * 0.35, r * 0.3, 0, TAU)
        c.set_source_rgba(1, 1, 1, 0.95)
        c.fill()

    def frame_overlay(self, c, t):
        c.save()
        c.set_operator(cairo.OPERATOR_MULTIPLY)
        c.set_source_surface(_paper(), 0, 0)
        c.paint()
        c.restore()


# ---------------------------------------------------------------- cached textures
_cache = {}


def _grain(a, seed):
    key = ("grain", a, seed)
    if key not in _cache:
        s, c = new_surface()
        rnd = rng(seed)
        for _ in range(26000):
            x, y = rnd.uniform(0, W), rnd.uniform(0, H)
            c.rectangle(x, y, 1.6, 1.6)
            v = rnd.random()
            c.set_source_rgba(v, v, v, a)
            c.fill()
        _cache[key] = s
    return _cache[key]


def _paper():
    if "paper" not in _cache:
        s, c = new_surface()
        c.set_source_rgba(*hexc("#f6eedd"))
        c.paint()
        rnd = rng(5)
        for _ in range(90):
            ellipse(c, rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(60, 300), rnd.uniform(40, 220), rnd.uniform(0, 3))
            c.set_source_rgba(0.82, 0.74, 0.6, rnd.uniform(0.03, 0.08))
            c.fill()
        for _ in range(9000):
            x, y = rnd.uniform(0, W), rnd.uniform(0, H)
            a = rnd.uniform(0, TAU)
            ln = rnd.uniform(2, 9)
            c.move_to(x, y)
            c.line_to(x + math.cos(a) * ln, y + math.sin(a) * ln)
            c.set_source_rgba(0.55, 0.45, 0.3, 0.07)
            c.set_line_width(0.8)
            c.stroke()
        _cache["paper"] = s
    return _cache["paper"]


STYLES = {"cute": Cute(), "real": Real(), "illustrated": Illustrated()}


def get(name):
    return STYLES[name]
