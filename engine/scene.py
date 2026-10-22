"""Timeline, transitions, captions and on-screen labels."""
import math
from dataclasses import dataclass, field

import cairo

from .core import (INK, TAU, H, W, back_out, ease, ease_in, lerp, prog, rounded_rect, set_font, text_center,
                   text_width)


@dataclass
class Scene:
    fn: callable              # fn(c, t, ctx) draws the scene at global time t
    start: float
    end: float
    transition: str = "fade"  # fade | iris | cut
    trans_dur: float = 0.45
    iris_center: callable = None  # iris_center(t) -> (x, y) screen coords
    iris_r0: float = 120.0


@dataclass
class Timeline:
    duration: float
    scenes: list = field(default_factory=list)
    captions: list = field(default_factory=list)   # Caption objects
    overlays: list = field(default_factory=list)   # fn(c, t, ctx) drawn above scenes, below captions

    def add(self, *a, **kw):
        s = Scene(*a, **kw)
        self.scenes.append(s)
        return s


STAGE_LIFT = 170   # all scene content is drawn this many px higher, so the action sits above the captions
                   # (captions must stay out of the TikTok/Shorts description area at the bottom)


def render_frame(c, t, tl, ctx):
    style = ctx["style"]
    c.set_source_rgba(0, 0, 0, 1)
    c.paint()
    c.save()
    c.translate(0, -ctx.get("lift", STAGE_LIFT))
    first = True
    for sc in tl.scenes:
        if not (sc.start <= t < sc.end):
            continue
        if first or sc.transition == "cut":
            sc.fn(c, t, ctx)
            first = False
            continue
        if sc.transition == "iris":
            cx, cy = sc.iris_center(t)
            k = prog(t, sc.start, sc.start + sc.trans_dur)
            r = lerp(sc.iris_r0, 2300, ease_in(k))
            c.save()
            c.arc(cx, cy, max(r, 0.1), 0, TAU)
            c.clip()
            sc.fn(c, t, ctx)
            c.restore()
            c.arc(cx, cy, max(r, 0.1), 0, TAU)
            c.set_source_rgba(1, 1, 1, 0.9 * (1 - k))
            c.set_line_width(8)
            c.stroke()
        else:
            c.push_group()
            sc.fn(c, t, ctx)
            c.pop_group_to_source()
            c.paint_with_alpha(ease(prog(t, sc.start, sc.start + sc.trans_dur)))
    for ov in tl.overlays:
        ov(c, t, ctx)
    c.restore()
    style.frame_overlay(c, t)
    if "vignette" in ctx:
        c.set_source_surface(ctx["vignette"], 0, 0)
        c.paint()
    draw_captions(c, t, tl.captions)
    edge = max(1 - ease(prog(t, 0, 0.3)), ease(prog(t, tl.duration - 0.6, tl.duration)))
    if edge > 0:
        c.set_source_rgba(0, 0, 0, edge)
        c.paint()


# ================================================================ captions
@dataclass
class Caption:
    start: float
    end: float
    words: list            # [(word, t_start, t_end)]
    chained_in: bool = False   # previous caption ends right where this starts -> swap instantly, no fade
    chained_out: bool = False


# ---- gentle UI palette (series-wide) ----
UI_CREAM = (1.0, 0.982, 0.95)
UI_INK = (0.23, 0.17, 0.11)
UI_SOFT = (0.23, 0.17, 0.11, 0.55)     # not-yet-spoken words
UI_HILITE = (1.0, 0.84, 0.72)          # soft peach behind the word being spoken
UI_ACCENT = (0.80, 0.42, 0.24)

# Safe zones for TikTok / YouTube Shorts (1080x1920): keep text + key action inside x 60..900, y 200..1460.
CAP_X = 480               # caption bubble centre x = middle of the safe zone (x 60..900; the app buttons sit right)
CAP_Y = 1400              # caption bubble centre (clear of the app description area that starts ~y 1520)
CAP_SIZE = 46
CAP_MAX_W = 840           # one line only (= safe-zone width x 60..900); voice.chunk_captions splits by this width


def soft_bubble(c, x, y, w, h, alpha, r=None, fill=UI_CREAM, shadow=0.16):
    """Rounded cream bubble with a soft, diffuse drop shadow."""
    r = h / 2 if r is None else r
    for i, (dy, grow, a) in enumerate(((10, 10, 0.05), (7, 6, 0.07), (4, 3, 0.09))):
        rounded_rect(c, x - grow / 2, y + dy - grow / 2, w + grow, h + grow, r + grow / 2)
        c.set_source_rgba(0.25, 0.15, 0.05, a * alpha * shadow / 0.16)
        c.fill()
    rounded_rect(c, x, y, w, h, r)
    c.set_source_rgba(fill[0], fill[1], fill[2], 0.94 * alpha)
    c.fill()


def draw_captions(c, t, caps):
    from . import text
    # Exactly one caption bubble at a time: the latest one that has started. Two bubbles must never overlap,
    # not even for a frame (a fading old line under a new one reads as garbled text).
    live = [c for c in caps if (c.start if c.chained_in else c.start - 0.06) <= t]
    for cap in live[-1:]:
        if t > cap.end:
            continue
        fi = 1.0 if cap.chained_in else ease(prog(t, cap.start - 0.06, cap.start + 0.14))
        fo = 1.0 if cap.chained_out else 1 - ease(prog(t, cap.end - 0.16, cap.end))
        al = fi * fo
        if al <= 0:
            continue
        words = [w for w, _, _ in cap.words]
        space = text.width(" ", CAP_SIZE, bold=True)
        ws_ = [text.width(w, CAP_SIZE, bold=True) for w in words]
        tw = sum(ws_) + space * (len(words) - 1)
        bh = CAP_SIZE * 1.7
        bw = tw + 64
        cy = CAP_Y + (1 - fi) * 14
        soft_bubble(c, CAP_X - bw / 2, cy - bh / 2, bw, bh, al)
        x = CAP_X - tw / 2
        base = cy + CAP_SIZE * 0.36
        for (w, ws, we), wd in zip(cap.words, ws_):
            active = ws - 0.02 <= t < we + 0.06
            spoken = t >= ws
            if active:
                rounded_rect(c, x - 8, cy - CAP_SIZE * 0.62, wd + 16, CAP_SIZE * 1.24, CAP_SIZE * 0.4)
                c.set_source_rgba(*UI_HILITE, 0.95 * al)
                c.fill()
            col = UI_INK if spoken else UI_SOFT
            text.draw(c, w, x, base, CAP_SIZE, col, alpha=al * (1.0 if spoken else 0.6), bold=True)
            x += wd + space


# ================================================================ labels
def tag(c, txt, x, y, alpha, size=40, sub=None, pointer=True):
    """Soft cream name tag that pops in; (x, y) is the pointer tip."""
    from . import text
    if alpha <= 0:
        return
    k = back_out(min(1.0, alpha * 1.4))
    c.save()
    c.translate(x, y)
    c.scale(k, k)
    w = text.width(txt, size, bold=True)
    sub_size = size * 0.62
    if sub:
        w = max(w, text.width(sub, sub_size, italic=True))
    bh = size * (2.05 if sub else 1.55)
    bw = w + 56
    top = -bh - (14 if pointer else 0)
    soft_bubble(c, -bw / 2, top, bw, bh, alpha, r=min(bh / 2, 30))
    if pointer:
        c.move_to(-13, -15.5)
        c.curve_to(-5, -10, -2, -3, 0, 0)
        c.curve_to(2, -3, 5, -10, 13, -15.5)
        c.close_path()
        c.set_source_rgba(*UI_CREAM, 0.94 * alpha)
        c.fill()
    text.center(c, txt, 0, top + size * 1.12, size, UI_INK, alpha=alpha, bold=True)
    if sub:
        text.center(c, sub, 0, top + size * 1.12 + sub_size * 1.15, sub_size, UI_ACCENT, alpha=alpha, italic=True)
    c.restore()


def label(c, txt, x, y, alpha, size=36):
    """Small soft pill with centred text (scene labels like 'Water', 'Doodle, unwound'); (x, y) = centre."""
    from . import text
    if alpha <= 0:
        return
    w = text.width(txt, size, semibold=True) + 48
    h = size * 1.6
    soft_bubble(c, x - w / 2, y - h / 2, w, h, alpha, shadow=0.12)
    text.center(c, txt, x, y + size * 0.36, size, UI_INK, alpha=alpha, semibold=True)


def leader(c, x0, y0, x1, y1, alpha, col=(1, 1, 1)):
    if alpha <= 0:
        return
    c.set_source_rgba(col[0], col[1], col[2], alpha)
    c.set_line_width(3)
    c.move_to(x0, y0)
    c.curve_to(x0, (y0 + y1) / 2, x1, (y0 + y1) / 2, x1, y1)
    c.stroke()
    c.arc(x1, y1, 7, 0, TAU)
    c.fill()


def badge(c, x, y, ok, k, r=58):
    if k <= 0:
        return
    s = back_out(k)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.arc(0, 0, r, 0, TAU)
    c.set_source_rgba(*((0.23, 0.64, 0.34, 1) if ok else (0.83, 0.23, 0.23, 1)))
    c.fill()
    c.set_source_rgba(1, 1, 1, 1)
    c.set_line_width(r * 0.22)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    if ok:
        c.move_to(-r * 0.4, 0)
        c.line_to(-r * 0.1, r * 0.35)
        c.line_to(r * 0.45, -r * 0.3)
    else:
        c.move_to(-r * 0.35, -r * 0.35)
        c.line_to(r * 0.35, r * 0.35)
        c.move_to(r * 0.35, -r * 0.35)
        c.line_to(-r * 0.35, r * 0.35)
    c.stroke()
    c.restore()


def sparkles(c, x, y, t, t0, n=7, r=90, col=(1, 0.95, 0.6)):
    k = prog(t, t0, t0 + 0.7)
    if k <= 0 or k >= 1:
        return
    for i in range(n):
        a = i * TAU / n + 0.3
        d = r * ease(k)
        s = 10 * (1 - k)
        px, py = x + math.cos(a) * d, y + math.sin(a) * d
        c.move_to(px - s, py)
        c.line_to(px + s, py)
        c.move_to(px, py - s)
        c.line_to(px, py + s)
        c.set_source_rgba(col[0], col[1], col[2], 1 - k)
        c.set_line_width(3)
        c.stroke()
