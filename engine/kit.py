"""Shared building blocks for the Shorts: cameras, the lens, the end-card plate, worm paths, the audio mix.

These used to live inside episodes (e002 and e003) and later episodes imported them from there or copied them.
New episodes import from here:

    from engine.kit import Cam, framed, keyed_cam, card_cam, blinking, paint, drift, lens, brand_plate, \
        along, poly_len, safe_x, episode_audio
"""
import math
import os

import cairo
import numpy as np

from .core import TAU, back_out, clamp, ease, hexc, lerp, prog, rounded_rect
from .scene import wordmark


# ================================================================ cameras
class Cam:
    """Show world point (wx, wy) at screen point (sx, sy), zoomed by z."""

    def __init__(self, z=1.0, wx=540.0, wy=960.0, sx=540.0, sy=960.0):
        self.z, self.wx, self.wy, self.sx, self.sy = z, wx, wy, sx, sy

    def apply(self, c):
        c.translate(self.sx, self.sy)
        c.scale(self.z, self.z)
        c.translate(-self.wx, -self.wy)

    def screen(self, x, y):
        return (x - self.wx) * self.z + self.sx, (y - self.wy) * self.z + self.sy


def framed(z, fx, fy, sx=540.0, sy=1130.0, bg_h=None):
    """Cam showing world point (fx, fy) at (sx, sy), clamped so the frame never runs off the background.
    Scenes are drawn STAGE_LIFT higher, so the visible world band is y 170..2090 (sy defaults to its middle)."""
    if bg_h is None:
        from . import backgrounds as bg
        bg_h = bg.HH
    z = max(1.0, z)
    wx = clamp(fx, sx / z, 1080 - (1080 - sx) / z)
    wy = clamp(fy, (sy - 170) / z, bg_h - (2090 - sy) / z)
    return Cam(z, wx, wy, sx, sy)


def keyed_cam(keys, bg_h=None):
    """One continuous camera for a whole setting (judge lessons: "one setting, one camera").

    keys = [(t, zoom, focus_x, focus_y), ...] in time order. Returns cam(t): eased between neighbouring keys,
    held before the first and after the last, always clamped onto the background by `framed`.
    """
    def cam(t):
        for (t0, z0, x0, y0), (t1, z1, x1, y1) in zip(keys, keys[1:]):
            if t < t1:
                k = ease(prog(t, t0, t1))
                return framed(lerp(z0, z1, k), lerp(x0, x1, k), lerp(y0, y1, k), bg_h=bg_h)
        _, z0, x0, y0 = keys[-1]
        return framed(z0, x0, y0, bg_h=bg_h)
    return cam


def card_cam(t, t0, t1, z0=0.94, z1=1.30, fx=540, fy=980):
    """A diagram card needs a big push-in (judge lessons: 1.0→1.17 over 11 s was invisible)."""
    z = lerp(z0, z1, ease(prog(t, t0, t1)))
    return Cam(z, fx, fy + 20 * ease(prog(t, t0, t1)), 540, 980)


# ================================================================ small motion helpers
def blinking(t, off=0.0, every=3.1):
    """True for the 0.13 s of a blink, every `every` seconds (offset per character so they don't blink together)."""
    return ((t + off) % every) < 0.13


def drift(t, x, y, ax=10, ay=6, sp=0.7):
    """Gentle idle float around (x, y)."""
    return x + ax * math.sin(t * sp), y + ay * math.sin(t * sp * 1.37 + 1.1)


def paint(c, surf):
    c.set_source_surface(surf, 0, 0)
    c.paint()


def safe_x(x, half_w, lo=60, hi=900):
    """Clamp a label's centre x so the whole label stays inside the safe zone (x 60..900)."""
    return clamp(x, lo + half_w, hi - half_w)


# ================================================================ worms on paths
def along(poly, head_d, length, n=60):
    """Points of a worm lying on a polyline: head at arc-length head_d, body trailing `length` behind it."""
    seg = [math.dist(p, q) for p, q in zip(poly, poly[1:])]

    def at(d):
        d = max(0.0, d)
        for (p, q), L in zip(zip(poly, poly[1:]), seg):
            if d <= L or L == seg[-1] and (p, q) == (poly[-2], poly[-1]):
                f = d / L if L else 0.0
                return lerp(p[0], q[0], min(f, 1.0)), lerp(p[1], q[1], min(f, 1.0))
            d -= L
        return poly[-1]

    return [at(head_d - length * k / (n - 1)) for k in range(n)]


def poly_len(poly):
    return sum(math.dist(p, q) for p, q in zip(poly, poly[1:]))


# ================================================================ series props
def lens(c, x, y, r, inner, a=1.0, t=0.0):
    """The channel's magnifying glass: a round window onto something tiny. inner(c) draws in world coords,
    clipped to the glass. The handle points down-left, away from the app's right rail."""
    if a <= 0:
        return
    from branding.banner import GOLD, NAVY
    k = back_out(min(1.0, a * 1.25))
    c.save()
    c.translate(x, y)
    c.scale(k, k)
    c.translate(-x, -y)
    c.push_group()
    hx, hy = x - r * 0.72, y + r * 0.72                        # handle
    c.move_to(hx, hy)
    c.line_to(hx - r * 0.42, hy + r * 0.42)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_source_rgba(*NAVY[:3], 1)
    c.set_line_width(r * 0.16)
    c.stroke()
    for dy, grow, al in ((10, 10, 0.08), (5, 5, 0.10)):           # soft shadow
        c.arc(x, y + dy, r + grow, 0, TAU)
        c.set_source_rgba(0.2, 0.1, 0.05, al)
        c.fill()
    c.save()
    c.arc(x, y, r, 0, TAU)
    c.clip()
    c.set_source_rgba(*hexc("#fbefe2"))
    c.paint()
    inner(c)
    g = cairo.RadialGradient(x - r * 0.4, y - r * 0.5, 0, x - r * 0.4, y - r * 0.5, r * 0.9)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.22)                    # glass glint
    g.add_color_stop_rgba(1, 1, 1, 1, 0)
    c.set_source(g)
    c.paint()
    c.restore()
    c.arc(x, y, r, 0, TAU)
    c.set_source_rgba(*GOLD[:3], 1)
    c.set_line_width(r * 0.09)
    c.stroke()
    c.arc(x, y, r * 0.955, 0, TAU)
    c.set_source_rgba(1, 0.97, 0.9, 0.7)
    c.set_line_width(3)
    c.stroke()
    c.pop_group_to_source()
    c.paint_with_alpha(min(1.0, a * 1.5))
    c.restore()
    from . import scene
    scene._record("lens", "", c, x - r, y - r, 2 * r, 2 * r, a)


def brand_plate(c, x, y, a, max_w=640):
    """Series logo plate for the end card (navy pill + the wordmark with the lens 'o'), centred at (x, y)."""
    if a <= 0:
        return
    from branding.banner import NAVY
    k = back_out(min(1.0, a * 1.3))
    size = 100
    c.save()
    c.translate(x, y)
    c.scale(0.9 + 0.1 * k, 0.9 + 0.1 * k)
    c.push_group()
    # measure through the shared wordmark helper by drawing it once into a scratch group
    c.push_group()
    tot = wordmark(c, 0, 0, size, alpha=0.0)
    c.pop_group()
    size *= min(1.0, max_w / tot)
    c.push_group()
    tot = wordmark(c, 0, 0, size, alpha=0.0)
    c.pop_group()
    pw, ph = tot + size * 0.9, size * 1.55
    rounded_rect(c, -pw / 2, -ph / 2 + 6, pw, ph, ph / 2)
    c.set_source_rgba(0.1, 0.08, 0.05, 0.18)
    c.fill()
    rounded_rect(c, -pw / 2, -ph / 2, pw, ph, ph / 2)
    c.set_source_rgba(*NAVY[:3], 1)
    c.fill()
    wordmark(c, 0, size * 0.3, size, alpha=1.0)
    c.pop_group_to_source()
    c.paint_with_alpha(a)
    from . import scene
    scene._record("plate", "brand plate", c, -pw / 2, -ph / 2, pw, ph, a)
    c.restore()


# ================================================================ audio
def episode_audio(dur, cues, script, sfx_list, voice, moods, music_gain=0.5, head=0.4, tail=0.8):
    """Returns make_audio(path) -> path: the series mix for one episode.

    Theme shaped by `moods` [(t, mood), ...], every word-anchored effect in `sfx_list`, every silent beat's
    `Line.sfx` (exactly as in the approved narration preview), music ducked under the voice, a faded tail,
    loudness-normalised to -14 LUFS. The theme is sliced from a longer score so there is music on frame 0
    and no digital silence under the end card (e002 judge pass 2).
    """
    from .audio import mix, music, sfx
    from .audio.common import SR, Bus
    from .voice import sfx_events

    def make_audio(path):
        full = music.score(dur + head + 8.0, moods)
        i0 = int(head * SR)
        bed = full[i0:i0 + int(dur * SR)]
        fx = Bus(dur, 5)
        for t0, name, gain in sfx_events(sfx_list, cues):
            fx.add(t0, sfx.LIB[name](), 0.0, gain)
        for ln in script:
            if ln.sfx:
                fx.add(cues[ln.id].start, sfx.LIB[ln.sfx](), 0.0, 0.5)
        n = int(dur * SR)
        out = mix.mixdown(n, music=bed, sfx=fx.buf, voice=voice, music_gain=music_gain)
        k = int(tail * SR)                   # ride the theme out under the end card instead of cutting
        out[-k:] *= np.linspace(1.0, 0.0, k)[:, None] ** 1.5
        raw = path.replace(".wav", "_raw.wav")
        mix.write_wav(raw, out)
        mix.loudnorm(raw, path)
        os.remove(raw)
        return path

    return make_audio
