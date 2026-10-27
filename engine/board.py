"""Whiteboard for the Lessons format: marker text that writes itself and strokes that draw
themselves. No marker sound (owner, 2026-10-26): lessons are voice only, except the logo intro jingle.

    b = Board()
    b.write("Bacteria shapes", 150, 190, 92, NAVY, t0=1.0, bold=True)
    b.stroke(circle(400, 560, 52), t0=4.7, dur=0.4, col=GREEN)
    b.hatch(circle(400, 560, 52), t0=8.0, dur=0.5, col=GREEN)
    b.render(c, t, tool="marker")        # tool: marker (owner pick) | hand | none

Bigger boards: Board(w=3840, h=2160) and move the camera with b.cam.move(...) / b.cam.frame(...).
Also: b.title(...), b.erase(...), b.logo(...) (the intro, with its sound: b.sound(duration)).

Every item knows where its pen tip is at time t, so the drawing and the marker can't drift apart.
"""
import math
import os

import cairo
import numpy as np

from . import text
from .audio import mix, music, sfx
from .audio.common import SR, Bus, hz
from .core import TAU, back_out, clamp, ease, hexc, lerp, prog, rng, rounded_rect, squash, with_alpha

W, H = 1920, 1080

NAVY = hexc("#1e2a3a")
BLUE = hexc("#2f6fb5")
RED = hexc("#d5483f")
GREEN = hexc("#2f9a5a")
GOLD = hexc("#f2b84b")
GOLD_DK = hexc("#d08a14")
PEACH = hexc("#f2a27a")
MUTED = hexc("#7a8290")

FONT = "Gochi Hand"   # owner pick, 2026-10-26 (sheet: Kalam / Patrick Hand / Caveat / Gochi Hand)


# ================================================================ geometry helpers
def spline(pts, closed=False, n=10):
    """Catmull-Rom through pts, sampled to a dense polyline."""
    out = []
    m = len(pts)
    segs = range(m) if closed else range(m - 1)
    for i in segs:
        p0 = pts[i - 1] if (i > 0 or closed) else pts[i]
        p1, p2 = pts[i], pts[(i + 1) % m]
        p3 = pts[(i + 2) % m] if (i + 2 < m or closed) else p2
        for k in range(n):
            u = k / n
            u2, u3 = u * u, u * u * u
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * u + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * u2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * u3) for j in (0, 1)))
    out.append(pts[0] if closed else pts[-1])
    return out


def wobble(pts, seed, amt=1.6):
    r = rng(seed)
    ph = [r.uniform(0, TAU) for _ in range(4)]
    out = []
    for i, (x, y) in enumerate(pts):
        k = i / max(1, len(pts) - 1)
        out.append((x + amt * math.sin(k * 7 + ph[0]) + amt * 0.5 * math.sin(k * 23 + ph[1]),
                    y + amt * math.sin(k * 9 + ph[2]) + amt * 0.5 * math.sin(k * 19 + ph[3])))
    return out


def circle(cx, cy, r, start=-2.2, overshoot=0.35, seed=1):
    """Hand-drawn circle: slightly uneven, the end overshoots the start a little."""
    rr = rng(seed)
    ph = rr.uniform(0, TAU)
    n = 64
    pts = []
    for i in range(n + 1):
        a = start + (TAU + overshoot) * i / n
        k = 1 + 0.025 * math.sin(2 * a + ph) - 0.03 * max(0, (a - start - TAU) / overshoot)
        pts.append((cx + r * k * math.cos(a), cy + r * k * math.sin(a)))
    return pts


def capsule(cx, cy, length, thick, ang=0.0, seed=2):
    """Rod / bacillus outline, drawn as one closed loop starting top-left."""
    r = thick / 2
    hl = length / 2 - r
    pts = []
    for i in range(9):                                   # top edge, left -> right
        pts.append((-hl + 2 * hl * i / 8, -r))
    for i in range(1, 16):                               # right cap
        a = -math.pi / 2 + math.pi * i / 15
        pts.append((hl + r * math.cos(a), r * math.sin(a)))
    for i in range(1, 9):                                # bottom edge, right -> left
        pts.append((hl - 2 * hl * i / 8, r))
    for i in range(1, 17):                               # left cap, a touch past the start
        a = math.pi / 2 + math.pi * i / 15
        pts.append((-hl + r * math.cos(a), r * math.sin(a)))
    ca, sa = math.cos(ang), math.sin(ang)
    return wobble([(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts], seed, 1.2)


def wavy_cell(cx, cy, length, amp, thick, waves=2.5, seed=3):
    """Spirillum outline: a wavy rod as one closed loop."""
    n = 60
    top, bot = [], []
    for i in range(n + 1):
        u = i / n
        x = cx - length / 2 + length * u
        y = cy + amp * math.sin(u * waves * TAU)
        # normal of the centre line
        dy = amp * waves * TAU / length * math.cos(u * waves * TAU)
        nl = math.hypot(1, dy)
        nx, ny = -dy / nl, 1 / nl
        top.append((x - nx * thick / 2, y - ny * thick / 2))
        bot.append((x + nx * thick / 2, y + ny * thick / 2))
    def cap(a, b, flip):
        # half circle from a to b around their midpoint, bulging along the centre line's tangent
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        phi = math.atan2(a[1] - m[1], a[0] - m[0])
        return [(m[0] + thick / 2 * math.cos(x), m[1] + thick / 2 * math.sin(x))
                for x in np.linspace(phi, phi + math.pi * flip, 7)[1:-1]]
    endc = cap(top[-1], bot[-1], 1)
    startc = cap(bot[0], top[0], 1)
    pts = top + endc + bot[::-1] + startc + [top[0], top[1]]
    return wobble(pts, seed, 1.0)


def star(cx, cy, r, seed=4):
    pts = []
    for i in range(11):
        a = -math.pi / 2 + i * TAU * 2 / 5
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return wobble(pts, seed, 1.5)


def line(x0, y0, x1, y1, sag=4.0, seed=5):
    n = 24
    return wobble([(lerp(x0, x1, i / n), lerp(y0, y1, i / n) + sag * math.sin(math.pi * i / n)) for i in range(n + 1)],
                  seed, 1.0)


def _cumlen(pts):
    d = [0.0]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        d.append(d[-1] + math.hypot(x1 - x0, y1 - y0))
    return d


def _point_at(pts, cum, s):
    """Point at arclength s, plus the index of the segment it falls in."""
    if s <= 0:
        return pts[0], 0
    if s >= cum[-1]:
        return pts[-1], len(pts) - 1
    i = int(np.searchsorted(cum, s)) - 1
    i = max(0, min(i, len(pts) - 2))
    k = (s - cum[i]) / max(1e-9, cum[i + 1] - cum[i])
    return (lerp(pts[i][0], pts[i + 1][0], k), lerp(pts[i][1], pts[i + 1][1], k)), i


def _poly(c, pts):
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)


def _marker_stroke(c, pts, col, width, alpha=1.0):
    """Marker ink: a solid core plus a faint wider edge, like felt on a whiteboard."""
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    _poly(c, pts)
    c.set_source_rgba(*with_alpha(col, 0.18 * alpha))
    c.set_line_width(width * 1.35)
    c.stroke_preserve()
    c.set_source_rgba(*with_alpha(col, 0.95 * alpha))
    c.set_line_width(width)
    c.stroke()


# ================================================================ board items
class Item:
    t0 = 0.0
    t1 = 0.0
    col = NAVY
    pen = True          # drawn with the marker (False: appears without a pen, e.g. a sticker)

    def draw(self, c, t):
        raise NotImplementedError

    def tip(self, t):
        """Pen tip (x, y) while the item is being drawn."""
        return None


class Stroke(Item):
    def __init__(self, pts, t0, dur, col, width=7.0, alpha=1.0, seed=0):
        self.pts = pts
        self.cum = _cumlen(pts)
        self.t0, self.t1 = t0, t0 + dur
        self.col, self.width, self.alpha = col, width, alpha

    def _s(self, t):
        u = prog(t, self.t0, self.t1)
        return self.cum[-1] * (0.5 * u + 0.5 * ease(u))  # mild ease in/out

    def draw(self, c, t):
        if t <= self.t0:
            return
        if t >= self.t1:
            _marker_stroke(c, self.pts, self.col, self.width, self.alpha)
            return
        s = self._s(t)
        p, i = _point_at(self.pts, self.cum, s)
        pts = self.pts[:i + 1] + [p]
        if len(pts) > 1:
            _marker_stroke(c, pts, self.col, self.width, self.alpha)

    def tip(self, t):
        if self.t0 <= t <= self.t1:
            return _point_at(self.pts, self.cum, self._s(t))[0]
        return None


class Hatch(Item):
    """Colour a closed shape in with quick zig-zag marker strokes (clipped to the shape)."""

    def __init__(self, outline, t0, dur, col, alpha=0.32, gap=17, ang=-0.7, width=20):
        self.outline = outline
        self.t0, self.t1 = t0, t0 + dur
        self.col, self.alpha, self.width = col, alpha, width
        xs = [p[0] for p in outline]
        ys = [p[1] for p in outline]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        R = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) / 2 + width
        ca, sa = math.cos(ang), math.sin(ang)
        pts = []
        n = int(2 * R / gap)
        for i in range(n + 1):
            v = -R + 2 * R * i / n
            a, b = (-R, R) if i % 2 == 0 else (R, -R)
            for u in (a, b):
                pts.append((cx + u * ca - v * sa, cy + u * sa + v * ca))
        self.pts = pts
        self.cum = _cumlen(self.pts)
        self.zig = len(pts) - 1

    def draw(self, c, t):
        if t <= self.t0:
            return
        s = self.cum[-1] * (prog(t, self.t0, self.t1) if t < self.t1 else 1.0)
        p, i = _point_at(self.pts, self.cum, s)
        c.save()
        _poly(c, self.outline)
        c.close_path()
        c.clip()
        c.push_group()
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        _poly(c, self.pts[:i + 1] + [p])
        c.set_source_rgba(*with_alpha(self.col, 1.0))
        c.set_line_width(self.width)
        c.stroke()
        c.pop_group_to_source()
        c.paint_with_alpha(self.alpha)
        c.restore()

    def tip(self, t):
        if self.t0 <= t <= self.t1:
            p, _ = _point_at(self.pts, self.cum, self.cum[-1] * prog(t, self.t0, self.t1))
            # the hand stays over the shape even when the zig-zag runs past its edge
            xs = [q[0] for q in self.outline]
            ys = [q[1] for q in self.outline]
            return clamp(p[0], min(xs), max(xs)), clamp(p[1], min(ys), max(ys))
        return None


class Text(Item):
    """Marker handwriting. Each letter is revealed by a quick up-down pen sweep, left to right."""

    def __init__(self, txt, x, y, size, col, t0, dur=None, cps=11.0, bold=False, fam=None, align="left",
                 semibold=False):
        self.txt, self.size, self.col, self.bold, self.semibold = txt, size, col, bold, semibold
        self.fam = fam or FONT
        wfull = text.width(txt, size, bold=bold, fam=self.fam, semibold=semibold)
        self.x = x - wfull / 2 if align == "center" else x
        self.y = y
        self.w = wfull
        # glyph spans (advance positions incl. kerning)
        self.spans = []
        for i, ch in enumerate(txt):
            if ch == " ":
                continue
            a = text.width(txt[:i], size, bold=bold, fam=self.fam, semibold=semibold)
            b = text.width(txt[:i + 1], size, bold=bold, fam=self.fam, semibold=semibold)
            self.spans.append((a, b))
        # time per glyph ~ its width; a space is a short pen lift
        weights = []
        for i, ch in enumerate(txt):
            weights.append(0.55 if ch == " " else max(0.6, text.width(ch, size, bold=bold, fam=self.fam, semibold=semibold) / (size * 0.45)))
        tot = sum(weights)
        dur = dur or max(0.35, len(txt.replace(" ", "")) / cps)
        self.t0, self.t1 = t0, t0 + dur
        acc, self.times = 0.0, []
        for i, ch in enumerate(txt):
            g0 = t0 + dur * acc / tot
            acc += weights[i]
            if ch != " ":
                self.times.append((g0, t0 + dur * acc / tot))
        self.top = y - size * 0.82
        self.bot = y + size * 0.28

    def _passes(self, gw):
        return max(2, int(round(gw / (self.size * 0.17))))

    def _sweep(self, k, u):
        """Pen-sweep polyline for glyph k up to progress u (0..1)."""
        a, b = self.spans[k]
        n = self._passes(b - a)
        pts = []
        for j in range(n + 1):
            x = self.x + a + (b - a) * j / n
            pts.append((x, self.top if j % 2 == 0 else self.bot))
        cum = _cumlen(pts)
        p, i = _point_at(pts, cum, cum[-1] * u)
        return pts[:i + 1] + [p], (b - a) / n

    def draw(self, c, t):
        if t <= self.t0:
            return
        if t >= self.t1:
            text.draw(c, self.txt, self.x, self.y, self.size, self.col, bold=self.bold, fam=self.fam, semibold=self.semibold)
            return
        done_x, cur = None, None
        for k, (g0, g1) in enumerate(self.times):
            if t >= g1:
                done_x = self.x + self.spans[k][1]
            elif t > g0:
                cur = k
                break
            else:
                break
        c.save()
        c.push_group()
        text.draw(c, self.txt, self.x, self.y, self.size, self.col, bold=self.bold, fam=self.fam, semibold=self.semibold)
        src = c.pop_group()
        c.push_group()
        c.set_source_rgba(1, 1, 1, 1)
        if done_x is not None:
            c.rectangle(self.x - self.size, self.top - self.size, done_x - self.x + self.size, self.size * 3)
            c.fill()
        if cur is not None:
            g0, g1 = self.times[cur]
            pts, step = self._sweep(cur, prog(t, g0, g1))
            c.set_line_cap(cairo.LINE_CAP_ROUND)
            c.set_line_join(cairo.LINE_JOIN_ROUND)
            c.set_line_width(step * 1.5 + self.size * 0.14)
            _poly(c, pts)
            c.stroke()
        mask = c.pop_group()
        c.set_source(src)
        c.mask(mask)
        c.restore()

    def tip(self, t):
        if not (self.t0 <= t <= self.t1):
            return None
        for k, (g0, g1) in enumerate(self.times):
            if t <= g1:
                a, b = self.spans[k]
                u = prog(t, g0, g1)
                bob = math.sin(u * math.pi * 2) * self.size * 0.12
                return self.x + lerp(a, b, u), self.y - self.size * 0.3 + bob
        return self.x + self.w, self.y - self.size * 0.3


# ================================================================ camera
class Camera:
    """Where the frame looks on a board that can be bigger than the frame. (cx, cy) = world point at the frame centre."""

    def __init__(self, cx, cy, zoom=1.0):
        self.start = (cx, cy, zoom)
        self.moves = []            # (t0, t1, from, to)

    def _last(self):
        return self.moves[-1][3] if self.moves else self.start

    def move(self, t0, dur, cx=None, cy=None, zoom=None):
        a = self._last()
        b = (a[0] if cx is None else cx, a[1] if cy is None else cy, a[2] if zoom is None else zoom)
        self.moves.append((t0, t0 + dur, a, b))
        return t0 + dur

    def frame(self, t0, dur, x0, y0, x1, y1, view=(W, H), margin=60):
        """Move so the board rectangle (x0, y0)-(x1, y1) fills the frame."""
        z = min(view[0] / (x1 - x0 + 2 * margin), view[1] / (y1 - y0 + 2 * margin))
        return self.move(t0, dur, (x0 + x1) / 2, (y0 + y1) / 2, z)

    def view(self, t):
        cur = self.start
        for t0, t1, a, b in self.moves:
            if t >= t1:
                cur = b
            elif t > t0:
                u = ease(prog(t, t0, t1))
                z = math.exp(lerp(math.log(a[2]), math.log(b[2]), u))      # zoom feels even in log space
                return lerp(a[0], b[0], u), lerp(a[1], b[1], u), z
            else:
                break
        return cur


# ================================================================ eraser
ERASER_IN = 0.35          # seconds the eraser takes to come in / leave


class Erase:
    """A felt eraser wiping a board rectangle back and forth. Everything drawn before t0 under its path disappears,
    leaving a faint ghost (residue) like a real whiteboard."""

    def __init__(self, x0, y0, x1, y1, t0, dur, height=120, residue=0.04):
        self.t0, self.t1 = t0, t0 + dur
        self.height, self.residue = height, residue
        rows = max(1, math.ceil((y1 - y0) / (height * 0.8)))
        pts = []
        for i in range(rows):
            y = (y0 + y1) / 2 if rows == 1 else y0 + height * 0.4 + (y1 - y0 - height * 0.8) * i / (rows - 1)
            xa, xb = (x0, x1) if i % 2 == 0 else (x1, x0)
            pts += [(xa, y), (xb, y)]
        self.pts = pts
        self.cum = _cumlen(pts)

    def _s(self, t):
        u = prog(t, self.t0, self.t1)
        return self.cum[-1] * (0.5 * u + 0.5 * ease(u))

    def wipe(self, c, t):
        """Cut the wiped area out of the ink layer drawn so far."""
        if t <= self.t0:
            return
        p, i = _point_at(self.pts, self.cum, self._s(t))
        pts = self.pts[:i + 1] + [p]
        c.save()
        c.set_operator(cairo.OPERATOR_DEST_OUT)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        _poly(c, pts)
        c.set_source_rgba(0, 0, 0, 1 - self.residue)
        c.set_line_width(self.height)
        c.stroke()
        c.restore()

    def tip(self, t):
        if self.t0 <= t <= self.t1:
            return _point_at(self.pts, self.cum, self._s(t))[0]
        return None


def draw_eraser(c, x, y, height, lift=0.0, tilt=0.0):
    """Felt board eraser seen from the front: navy back, cream felt edge, a small gold badge."""
    w, h = height * 0.5, height * 1.04
    c.save()
    c.translate(x, y)
    c.rotate(tilt)
    c.scale(1 + 0.05 * lift, 1 + 0.05 * lift)
    for i, a in enumerate((0.06, 0.04, 0.025)):          # soft shadow
        g = 4 * i
        rounded_rect(c, -w / 2 + 10 + 16 * lift - g, -h / 2 + 14 + 22 * lift - g, w + 2 * g, h + 2 * g, 16 + g)
        c.set_source_rgba(0.1, 0.12, 0.18, a)
        c.fill()
    rounded_rect(c, -w / 2, -h / 2, w, h, 16)
    c.set_source_rgba(*with_alpha(CUFF, 1))
    c.fill()
    rounded_rect(c, -w / 2 + 7, -h / 2 + 5, w - 14, h - 10, 13)
    c.set_source_rgba(*with_alpha(NAVY, 1))
    c.fill()
    rounded_rect(c, -w / 2 + 12, -h / 2 + 9, w * 0.22, h - 18, 8)     # sheen
    c.set_source_rgba(1, 1, 1, 0.10)
    c.fill()
    c.arc(0, 0, w * 0.16, 0, TAU)
    c.set_source_rgba(*with_alpha(GOLD, 1))
    c.fill()
    c.restore()


# ================================================================ logo intro
class PopText(Item):
    """Letters that pop onto the board one by one: drop in, overshoot, squash on landing."""
    pen = False

    def __init__(self, txt, x, y, size, col, t0, step=0.075, pop=0.34, **font):
        self.txt, self.x, self.y, self.size, self.col, self.font, self.pop = txt, x, y, size, col, font, pop
        self.letters = []            # (char, x offset, width, start time)
        t = t0
        for i, ch in enumerate(txt):
            if ch == " ":
                t += step * 0.8
                continue
            a = text.width(txt[:i], size, **font)
            self.letters.append((ch, a, text.width(ch, size, **font), t))
            t += step
        self.t0, self.t1 = t0, self.letters[-1][3] + pop
        self.w = text.width(txt, size, **font)

    def draw(self, c, t):
        for k, (ch, ox, w, ti) in enumerate(self.letters):
            if t <= ti:
                break
            u = prog(t, ti, ti + self.pop)
            s = back_out(u, 2.6)
            sx, sy = squash(t, ti + self.pop * 0.75, 0.3, 0.2)
            c.save()
            c.translate(self.x + ox + w / 2, self.y - (1 - ease(u)) * self.size * 0.45)
            c.rotate((1 - ease(u)) * (0.35 if k % 2 else -0.35))
            c.scale(s * sx, s * sy)
            text.draw(c, ch, -w / 2, 0, self.size, self.col, alpha=min(1.0, u * 3), **self.font)
            c.restore()


class LensSwoop(Item):
    """The magnifying-glass "o": swoops in spinning, lands with a squash, then a glint sweeps across the glass."""
    pen = False
    FLY = 0.45

    def __init__(self, ox, oy, r, width, col, t0, size):
        self.ox, self.oy, self.r, self.wd, self.col, self.size = ox, oy, r, width, col, size
        self.t0, self.land = t0, t0 + self.FLY
        self.glint = self.land + 0.22
        self.t1 = self.glint + 0.4

    def draw(self, c, t):
        u = prog(t, self.t0, self.land)
        if u <= 0:
            return
        e = ease(u)
        # arc in from the upper right, one turn of spin, growing to full size
        x = lerp(self.ox + self.size * 2.6, self.ox, e)
        y = lerp(self.oy - self.size * 1.4, self.oy, e) - math.sin(math.pi * e) * self.size * 0.5
        sx, sy = squash(t, self.land, 0.32, 0.22)
        k = 0.35 + 0.65 * e
        c.save()
        c.translate(x, y)
        c.rotate((1 - e) * TAU)
        c.scale(k * sx, k * sy)
        r, w = self.r, self.wd
        c.arc(0, 0, r, 0, TAU)                             # a hint of glass
        c.set_source_rgba(*with_alpha(GOLD, 0.12))
        c.fill()
        g = prog(t, self.glint, self.glint + 0.35)
        if 0 < g < 1:                                      # the glint
            c.save()
            c.arc(0, 0, r - w / 2, 0, TAU)
            c.clip()
            c.rotate(-0.7)
            gx = lerp(-r * 1.6, r * 1.6, ease(g))
            c.rectangle(gx - r * 0.18, -r * 2, r * 0.36, r * 4)
            c.set_source_rgba(1, 1, 1, 0.85 * math.sin(math.pi * g))
            c.fill()
            c.restore()
        c.arc(0, 0, r, 0, TAU)
        c.set_source_rgba(*with_alpha(self.col, 1))
        c.set_line_width(w)
        c.stroke()
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.move_to(-r * 0.78, r * 0.78)
        c.line_to(-r * 1.45, r * 1.45)
        c.stroke()
        c.restore()


class Veil(Item):
    """Fades everything drawn before it to a faint background (board colour over the whole board)."""
    pen = False

    def __init__(self, w, h, t0, dur=1.0, alpha=0.85):
        self.w, self.h, self.alpha = w, h, alpha
        self.t0, self.t1 = t0, t0 + dur

    def draw(self, c, t):
        c.rectangle(0, 0, self.w, self.h)
        c.set_source_rgba(0.975, 0.978, 0.98, self.alpha * ease(prog(t, self.t0, self.t1)))
        c.fill()


def _note_sound(name, f):
    if name == "marimba":
        return music.marimba(f, 0.9)
    if name == "celesta":
        return music.celesta(f, 1.6)
    return music.kalimba(f, 2.0)


# ================================================================ the board
class Board:
    """A whiteboard of any size (w, h) seen through a camera into a view-size frame. With the default size the
    board is exactly one frame and the camera never moves."""

    def __init__(self, w=W, h=H, seed=7, view=(W, H)):
        self.w, self.h = w, h
        self.vw, self.vh = view
        self.items = []
        self.erases = []
        self.cues = []               # (t, sound, freq, gain, pan) for sound()
        self.seed = seed
        self._bg = None
        self.cam = Camera(self.vw / 2, self.vh / 2)

    # ---- authoring ------------------------------------------------------------
    def write(self, txt, x, y, size, col, t0, **kw):
        it = Text(txt, x, y, size, col, t0, **kw)
        self.items.append(it)
        return it

    def stroke(self, pts, t0, dur, col, **kw):
        it = Stroke(pts, t0, dur, col, **kw)
        self.items.append(it)
        return it

    def hatch(self, outline, t0, dur, col, **kw):
        it = Hatch(outline, t0, dur, col, **kw)
        self.items.append(it)
        return it

    def erase(self, x0, y0, x1, y1, t0, dur=1.0, **kw):
        e = Erase(x0, y0, x1, y1, t0, dur, **kw)
        self.erases.append(e)
        self.erases.sort(key=lambda e: e.t0)
        return e

    def title(self, txt, x, y, t0, size=110, col=NAVY):
        """A section title written in marker with a gold underline. Returns the time it's finished."""
        tt = self.write(txt, x, y, size, col, t0, cps=11)
        u = self.stroke(line(x - 10, y + size * 0.3, x + tt.w + 10, y + size * 0.27, sag=5), tt.t1 + 0.1, 0.4, GOLD,
                        width=size * 0.1)
        return u.t1

    def veil(self, t0, dur=1.0, alpha=0.85):
        """Fade the board so far into a faint background, e.g. behind the outro logo."""
        it = Veil(self.w, self.h, t0, dur, alpha)
        self.items.append(it)
        return it

    def logo(self, cx, y, t0, size=130, sub="Lessons"):
        """The series intro (~2.8 s): "teeny tiny" pops in letter by letter on rising marimba notes, the
        magnifying-glass "o" swoops in and glints (whoosh, pop, sparkle), "logy" pops in on celesta, then the
        sub-title is written in marker over a soft closing chord. The sounds go to self.cues (see sound()).
        Returns the time it's finished."""
        kw = dict(fam="Outfit", semibold=True)
        head = "teeny tiny"
        wh = text.width(head + " ", size, **kw)
        ow = text.width("o", size, **kw)
        gap = size * 0.22
        tot = wh + gap + text.width("ology", size, **kw)
        x = cx - tot / 2
        pan = lambda px: clamp((px - cx) / (tot / 2), -1, 1) * 0.5

        h = PopText(head, x, y, size, NAVY, t0, step=0.085, **kw)
        self.items.append(h)
        for (ch, ox, w, ti), note in zip(h.letters, ["D5", "E5", "F#5", "A5", "B5", "A5", "B5", "D6", "E6"]):
            self.cues.append((ti + 0.04, "marimba", hz(note), 0.32, pan(x + ox)))

        lx = x + wh + gap + ow / 2
        lens = LensSwoop(lx, y - size * 0.25 - 2, ow * 0.42, size * 0.15, GOLD, h.letters[-1][3] + 0.2, size)
        self.items.append(lens)
        self.cues.append((lens.t0, "whoosh", None, 0.10, 0.4))
        self.cues.append((lens.land, "pop", 520.0, 0.22, pan(lx)))
        self.cues.append((lens.glint, "sparkle", None, 0.16, pan(lx)))

        lg = PopText("logy", x + wh + gap + ow, y, size, GOLD, lens.land + 0.12, step=0.07, **kw)
        self.items.append(lg)
        for (ch, ox, w, ti), note in zip(lg.letters, ["F#6", "A6", "B6", "D7"]):
            self.cues.append((ti + 0.04, "celesta", hz(note) / 2, 0.22, pan(lg.x + ox)))
        end = max(lg.t1, lens.t1)
        if sub:
            s = self.write(sub, cx, y + size * 1.02, size * 0.64, NAVY, end + 0.05, cps=14, align="center")
            ul = self.stroke(line(cx - s.w / 2 - 6, y + size * 1.19, cx + s.w / 2 + 6, y + size * 1.16, sag=4),
                             s.t1 + 0.06, 0.25, GOLD, width=8)
            for i, note in enumerate(["D4", "F#4", "A4", "D5"]):   # the closing chord, gently rolled
                self.cues.append((ul.t1 - 0.1 + i * 0.045, "kalimba", hz(note), 0.2, (i - 1.5) * 0.15))
            end = ul.t1
        return end

    def sound(self, dur):
        """Stereo track of the board's sound cues (the logo intro). Lessons are otherwise voice only."""
        bus = Bus(dur)
        for t, name, f, gain, pan in self.cues:
            if name in ("marimba", "celesta", "kalimba"):
                sig = _note_sound(name, f)
            elif name == "pop":
                sig = sfx.pop(f)
            else:
                sig = sfx.LIB[name]()
            bus.add(t, sig, pan, gain)
        return bus.buf


    # ---- background -------------------------------------------------------------
    def background(self):
        if self._bg is not None:
            return self._bg
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.w, self.h)
        c = cairo.Context(s)
        g = cairo.RadialGradient(self.w * 0.45, self.h * 0.4, 100, self.w * 0.5, self.h * 0.5, max(self.w, self.h) * 0.75)
        g.add_color_stop_rgb(0, 0.995, 0.995, 0.99)
        g.add_color_stop_rgb(1, 0.925, 0.935, 0.94)
        c.set_source(g)
        c.paint()
        r = rng(self.seed)
        # ghosts of old, erased marker
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        for _ in range(int(9 * self.w * self.h / (W * H))):
            x, y = r.uniform(0, self.w), r.uniform(0, self.h)
            pts = [(x + i * r.uniform(30, 60), y + 25 * math.sin(i * r.uniform(0.6, 1.2))) for i in range(r.randint(4, 9))]
            _poly(c, spline(pts, n=6))
            c.set_source_rgba(0.35, 0.4, 0.5, r.uniform(0.012, 0.03))
            c.set_line_width(r.uniform(6, 40))
            c.stroke()
        # broad soft sheen
        g = cairo.LinearGradient(0, 0, self.w, self.h)
        g.add_color_stop_rgba(0.30, 1, 1, 1, 0)
        g.add_color_stop_rgba(0.42, 1, 1, 1, 0.35)
        g.add_color_stop_rgba(0.55, 1, 1, 1, 0)
        c.set_source(g)
        c.paint()
        self._bg = s
        return s

    # ---- rendering ----------------------------------------------------------------
    def rest(self, t):
        """Where the marker / eraser wait between uses: just off the frame's bottom-right, in board coordinates."""
        cx, cy, z = self.cam.view(t)
        return cx + (self.vw / 2 + 260) / z, cy + (self.vh / 2 + 220) / z

    def tool_state(self, t):
        """(x, y, colour, lift 0..1) of the marker tip, or None when off-screen."""
        if any(e.t0 - ERASER_IN <= t <= e.t1 + ERASER_IN for e in self.erases):
            return None                                   # the marker steps aside while the eraser works
        for it in self.items:
            if it.pen:
                p = it.tip(t)
                if p is not None:
                    return p[0], p[1], it.col, 0.0
        prev = max((it for it in self.items if it.pen and it.t1 < t), key=lambda i: i.t1, default=None)
        nxt = min((it for it in self.items if it.pen and it.t0 > t), key=lambda i: i.t0, default=None)
        rest = self.rest(t)
        a = (prev.tip(prev.t1), prev.t1, prev.col) if prev else (rest, -9, NAVY)
        b = (nxt.tip(nxt.t0), nxt.t0, nxt.col) if nxt else (rest, t + 99, NAVY)
        gap = b[1] - a[1]
        travel = 0.45
        if gap <= 1.1:                                    # glide straight to the next item, slightly lifted
            u = ease(prog(t, a[1], b[1]))
            return lerp(a[0][0], b[0][0], u), lerp(a[0][1], b[0][1], u), (b[2] if u > 0.5 else a[2]), math.sin(math.pi * u)
        if t < a[1] + travel:                             # leave towards the rest position
            u = ease(prog(t, a[1], a[1] + travel))
            return lerp(a[0][0], rest[0], u), lerp(a[0][1], rest[1], u), a[2], min(1.0, u * 2)
        if t > b[1] - travel:                             # come back in
            u = ease(prog(t, b[1] - travel, b[1]))
            return lerp(rest[0], b[0][0], u), lerp(rest[1], b[0][1], u), b[2], min(1.0, (1 - u) * 2)
        return None

    def eraser_state(self, t):
        """(x, y, height, lift, tilt) of the eraser, or None when it's not in use."""
        for e in self.erases:
            if e.t0 - ERASER_IN <= t <= e.t1 + ERASER_IN:
                rest = self.rest(t)
                if t < e.t0:
                    u = ease(prog(t, e.t0 - ERASER_IN, e.t0))
                    p, lift = (lerp(rest[0], e.pts[0][0], u), lerp(rest[1], e.pts[0][1], u)), 1 - u
                elif t > e.t1:
                    u = ease(prog(t, e.t1, e.t1 + ERASER_IN))
                    p, lift = (lerp(e.pts[-1][0], rest[0], u), lerp(e.pts[-1][1], rest[1], u)), u
                else:
                    p, lift = e.tip(t), 0.0
                return p[0], p[1], e.height, lift, 0.06 * math.sin(t * 9)
        return None

    def _ink(self, c, t):
        """All items in authoring order; each eraser cuts out what was drawn before it started."""
        live = [e for e in self.erases if t > e.t0]
        if not live:
            for it in self.items:
                if t > it.t0:
                    it.draw(c, t)
            return
        c.push_group()
        prev = -1e9
        for e in live:
            for it in self.items:
                if prev < it.t0 <= e.t0 and t > it.t0:
                    it.draw(c, t)
            e.wipe(c, t)
            prev = e.t0
        for it in self.items:
            if it.t0 > prev and t > it.t0:
                it.draw(c, t)
        c.pop_group_to_source()
        c.paint()

    def render(self, c, t, tool="marker"):
        cx, cy, z = self.cam.view(t)
        c.set_source_rgb(0.86, 0.875, 0.89)               # the wall around the board
        c.paint()
        c.save()
        c.translate(self.vw / 2, self.vh / 2)
        c.scale(z, z)
        c.translate(-cx, -cy)
        fw = 30                                           # the board's frame, just outside its edge
        _rrect(c, -fw, -fw, self.w + 2 * fw, self.h + 2 * fw, fw * 1.5)
        c.set_source_rgb(0.72, 0.75, 0.79)
        c.fill()
        c.set_source_surface(self.background(), 0, 0)
        c.paint()
        self._ink(c, t)
        es = self.eraser_state(t)
        if es:
            draw_eraser(c, *es)
        if tool != "none":
            st = self.tool_state(t)
            if st:
                draw_tool(c, st[0], st[1], st[2], st[3], hand=(tool == "hand"))
        c.restore()


# ================================================================ the lesson mix
def _stem_lufs(x, path):
    """Integrated loudness of a stem (mono or stereo) at its own scale."""
    x = np.stack([x, x], 1) if x.ndim == 1 else x
    k = 0.5 / (np.abs(x).max() + 1e-9)
    mix.write_wav(path, x * k)
    v = mix.measure_lufs(path)
    os.remove(path)
    return v - 20 * math.log10(k)


def mixdown(b, voice, dur, path, jingle_lu=-4.0):
    """Lesson soundtrack: the narrator plus the board's sound cues (the logo jingle) set jingle_lu below the voice,
    normalised to -14 LUFS. No music, no marker sound."""
    n = int(dur * SR)
    fx = b.sound(dur)
    if b.cues and np.abs(fx).max() > 0:
        v, f = _stem_lufs(voice[:n] * 0.8, path + ".v.wav"), _stem_lufs(fx, path + ".f.wav")
        fx = fx * 10 ** ((v + jingle_lu - f) / 20)
    out = np.zeros((n, 2))
    out[: len(fx)] += fx[:n]
    vv = voice[:n] * 0.8
    out[: len(vv)] += vv[:, None]
    return mix.normalize_linear(out, path)


# ================================================================ the marker and the hand
SKIN = hexc("#f1c6a2")
SKIN_DK = hexc("#c98d6c")
SKIN_LINE = hexc("#8a5640")
SLEEVE = NAVY
CUFF = hexc("#f3ead8")


GRIP = -0.42      # the marker leans away from the forearm, so its barrel shows above the knuckles
TOOL_SCALE = 1.25
HAND_OFF = (-6, -34)   # the hand sits up on the barrel


def draw_tool(c, x, y, col, lift=0.0, hand=True, ang=0.95):
    """Marker (and optionally a right hand + sleeve) with its tip at (x, y). The hand comes in from the bottom-right.
    lift 0..1: raised off the board (between strokes)."""
    c.save()
    c.translate(x, y)
    k = TOOL_SCALE * (1 + 0.04 * lift)
    # soft shadow on the board (grows as the hand lifts)
    sx, sy = 12 + 24 * lift, 18 + 28 * lift
    c.save()
    c.translate(sx, sy)
    c.rotate(ang)
    c.scale(k, k)
    for i, a in enumerate((0.05, 0.04, 0.03)):
        c.save()
        grow = 1 + 0.03 * i
        c.scale(grow, grow)
        _tool_silhouette(c, hand)
        c.set_source_rgba(0.1, 0.12, 0.18, a * (1 - 0.4 * lift))
        c.fill()
        c.restore()
    c.restore()
    c.rotate(ang)
    c.scale(k, k)
    if hand:
        c.save()
        c.translate(*HAND_OFF)
        _sleeve_and_curled(c)
        c.restore()
    c.save()
    c.rotate(GRIP if hand else 0.0)
    _marker(c, col)
    c.restore()
    if hand:
        c.save()
        c.translate(*HAND_OFF)
        _hand_back(c)
        c.restore()
        c.save()
        c.rotate(GRIP)
        _fingers(c)
        c.restore()
    c.restore()


def _tool_silhouette(c, hand):
    c.new_path()
    c.save()
    c.rotate(GRIP if hand else 0.0)
    c.rectangle(0, -15, 280, 30)
    c.restore()
    if hand:
        c.save()
        c.translate(*HAND_OFF)
        _hand_shape(c)
        c.rectangle(230, -70, 700, 150)
        c.restore()


def _marker(c, col):
    # local frame: +x runs from the tip back along the barrel
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    # felt tip
    c.move_to(0, -4)
    c.line_to(12, -7)
    c.line_to(12, 7)
    c.line_to(0, 4)
    c.close_path()
    c.set_source_rgba(*col)
    c.fill()
    # cone
    c.move_to(12, -8)
    c.line_to(34, -15)
    c.line_to(34, 15)
    c.line_to(12, 8)
    c.close_path()
    c.set_source_rgb(0.86, 0.87, 0.88)
    c.fill_preserve()
    c.set_source_rgba(0.3, 0.32, 0.36, 0.8)
    c.set_line_width(2)
    c.stroke()
    # barrel
    _rrect(c, 34, -16, 230, 32, 6)
    g = cairo.LinearGradient(0, -16, 0, 16)
    g.add_color_stop_rgb(0, 0.99, 0.99, 0.99)
    g.add_color_stop_rgb(0.5, 0.93, 0.94, 0.95)
    g.add_color_stop_rgb(1, 0.8, 0.82, 0.85)
    c.set_source(g)
    c.fill_preserve()
    c.set_source_rgba(0.3, 0.32, 0.36, 0.8)
    c.set_line_width(2)
    c.stroke()
    # colour band (shows which marker it is) + end cap
    _rrect(c, 120, -16, 70, 32, 3)
    c.set_source_rgba(*col)
    c.fill()
    _rrect(c, 252, -15, 22, 30, 6)
    c.set_source_rgba(*col)
    c.fill()


def _hand_shape(c):
    # palm/back of hand wrapping the barrel
    c.new_sub_path()
    c.move_to(95, -30)
    c.curve_to(120, -62, 205, -78, 250, -58)
    c.curve_to(285, -42, 290, 40, 262, 62)
    c.curve_to(225, 88, 150, 80, 118, 52)
    c.curve_to(95, 32, 82, -5, 95, -30)
    c.close_path()


def _rrect(c, x, y, w, h, r):
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()


def _skin(c, w=3.0):
    c.set_source_rgba(*SKIN)
    c.fill_preserve()
    c.set_source_rgba(*SKIN_LINE)
    c.set_line_width(w)
    c.stroke()


def _sleeve_and_curled(c):
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    # sleeve + cuff (comes from off-screen)
    _rrect(c, 268, -68, 700, 146, 30)
    c.set_source_rgba(*SLEEVE)
    c.fill()
    _rrect(c, 252, -72, 46, 154, 18)
    c.set_source_rgba(*CUFF)
    c.fill_preserve()
    c.set_source_rgba(0.55, 0.5, 0.42, 0.6)
    c.set_line_width(2)
    c.stroke()
    # curled fingers under the barrel (behind it)
    for i, (u, v) in enumerate(((112, 30), (140, 50), (174, 62))):
        c.new_path()
        c.arc(u, v, 20 - i * 1.5, 0, TAU)
        _skin(c, 2.6)


def _hand_back(c):
    _hand_shape(c)
    g = cairo.LinearGradient(100, -60, 260, 70)
    g.add_color_stop_rgba(0, *SKIN)
    g.add_color_stop_rgba(1, *SKIN_DK)
    c.set_source(g)
    c.fill_preserve()
    c.set_source_rgba(*SKIN_LINE)
    c.set_line_width(3)
    c.stroke()
    for u, v in ((150, -40), (178, -46)):              # knuckle creases
        c.move_to(u, v)
        c.curve_to(u + 6, v + 6, u + 6, v + 14, u + 2, v + 20)
        c.set_source_rgba(*with_alpha(SKIN_LINE, 0.45))
        c.set_line_width(2)
        c.stroke()


def _fingers(c):
    """Index finger on top of the barrel and the thumb on the near side (in the marker's frame)."""
    c.move_to(150, -14)
    c.curve_to(110, -30, 64, -26, 46, -16)
    c.curve_to(38, -8, 46, 2, 58, -2)
    c.curve_to(80, -8, 110, -6, 140, 4)
    _skin(c, 3)
    c.move_to(50, -13)                                    # fingernail
    c.curve_to(54, -19, 63, -19, 65, -11)
    c.set_source_rgba(1, 0.93, 0.88, 0.9)
    c.set_line_width(5)
    c.stroke()
    c.move_to(120, 40)                                    # thumb
    c.curve_to(98, 34, 72, 28, 62, 20)
    c.curve_to(54, 12, 62, 4, 74, 8)
    c.curve_to(94, 14, 118, 16, 136, 18)
    _skin(c, 3)
