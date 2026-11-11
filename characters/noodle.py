"""NOODLE — the tapeworm (Dipylidium caninum). A long ribbon of cream segments with a tiny head (scolex).
Calm, patient, always hungry. In cute/illustrated styles the scolex has a little face.

draw(c, st, pts, nseg, ...)    the whole worm laid along a polyline pts (pts[0] = head)
draw_scolex(...)               the head: suckers + crown of hooks (+ face in cute styles)
draw_segment / draw_grain      one proglottid (on the worm / shed, rice-grain look)
draw_egg_packet, draw_cyst     egg capsule, cysticercoid (young tapeworm)
worm_curve(anchor, end, t)     a gently swaying path between two points
"""
import math

from engine.core import TAU, Palette, clamp, ellipse, hexc, lerp, rng

NAME = "Noodle"
SPECIES = "tapeworm"
SEG = Palette("#fbf3e1", "#ffffff", "#dcc9a2", "#a88f62")
EGG = Palette("#f3dc9a", "#fff4cc", "#c9a24e", "#8a6a2e")
SEG_MAX = 22
NECK = 34       # head centre -> first segment (the head itself has radius ~20 * size)


def worm_curve(anchor, end, t, amp=150, n=400, waves=3.0):
    ax, ay = anchor
    ex, ey = end
    dx, dy = ex - ax, ey - ay
    ln = math.hypot(dx, dy) or 1
    nx, ny = -dy / ln, dx / ln
    pts = []
    for k in range(n + 1):
        u = k / n
        off = amp * math.sin(waves * math.pi * u - t * 1.6) * min(1, u * 3)
        pts.append((ax + dx * u + nx * off, ay + dy * u + ny * off))
    return pts


def _cum(pts):
    cum = [0.0]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        cum.append(cum[-1] + math.hypot(x1 - x0, y1 - y0))
    return cum


def _at(pts, cum, a):
    lo, hi = 0, len(cum) - 1
    while lo < hi - 1:
        m = (lo + hi) // 2
        if cum[m] <= a:
            lo = m
        else:
            hi = m
    f = clamp((a - cum[lo]) / ((cum[hi] - cum[lo]) or 1))
    (x0, y0), (x1, y1) = pts[lo], pts[hi]
    return lerp(x0, x1, f), lerp(y0, y1, f), math.atan2(y1 - y0, x1 - x0)


def segment_layout(pts, nseg, length_frac=1.0, size=1.0):
    cum = _cum(pts)
    total = cum[-1] * length_frac
    neck = (NECK - 6) * size        # segments start just before the neck ends, covering its end
    base = [lerp(12, 66, (i / (SEG_MAX - 1)) ** 1.1) * size for i in range(nseg)]
    scale = min((total - neck) / (sum(base) or 1), 1.25)
    out, a = [], neck
    for i in range(nseg):
        l = base[i] * scale
        px, py, ang = _at(pts, cum, a + l / 2)
        out.append((px, py, ang, l, lerp(11, 44, (i / (SEG_MAX - 1)) ** 0.8) * size))  # ripe ones longer than wide (cucumber seed)
        a += l
    return out


def _seed_shape(cc, l, w):
    """A proglottid: a soft barrel / cucumber-seed shape — sides bulge, ends narrower (joined to neighbours)."""
    L = l * 0.47
    e = w * 0.30
    cc.move_to(-L, -e)
    cc.curve_to(-L * 0.45, -w * 0.56, L * 0.45, -w * 0.56, L, -e)
    cc.curve_to(L + w * 0.08, -e * 0.5, L + w * 0.08, e * 0.5, L, e)
    cc.curve_to(L * 0.45, w * 0.56, -L * 0.45, w * 0.56, -L, e)
    cc.curve_to(-L - w * 0.08, e * 0.5, -L - w * 0.08, -e * 0.5, -L, -e)
    cc.close_path()


def draw_segment(c, st, l, w, mature, alpha=1.0, seed=0):
    path = lambda cc: _seed_shape(cc, l, w)  # noqa: E731
    st.part(c, path, SEG, 0, 0, max(l, w) * 0.6, seed=seed, alpha=alpha)
    if mature:
        # egg packets showing through the skin: a loose, irregular cluster of soft honey blobs (owner: a neat
        # 2x2 grid of dots read as dominoes)
        rnd = rng(seed * 7 + 3)
        c.save()
        path(c)
        c.clip()
        for _ in range(9):
            ex = rnd.uniform(-0.36, 0.36) * l
            ey = rnd.uniform(-0.3, 0.3) * w * (1 - abs(ex) / l)
            r = w * rnd.uniform(0.07, 0.12)
            ellipse(c, ex, ey, r, r * rnd.uniform(0.8, 1.0))
            c.set_source_rgba(*hexc("#e6b765")[:3], 0.42 * alpha)
            c.fill()
        c.restore()


def draw_scolex(c, st, x, y, ang, s, alpha=1.0, detail=False, blink=False, happy=0.0):
    """Hooked crown points along -x after rotation by ang."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.push_group()
    hook = hexc("#8a6a48")
    for row in range(3 if detail else 2):
        for k in range(7):
            a = math.pi + (k - 3) * 0.3
            r0 = 8 + row * 2.5
            rx0, ry0 = -25 + math.cos(a) * r0, math.sin(a) * r0
            dx, dy = math.cos(a), math.sin(a)
            c.move_to(rx0, ry0)
            c.curve_to(rx0 + dx * 3, ry0 + dy * 3, rx0 + dx * 5 - dy * 2, ry0 + dy * 5 + dx * 2,
                       rx0 + dx * 4 - dy * 3.5, ry0 + dy * 4 + dx * 3.5)
            c.set_source_rgba(*hook)
            c.set_line_width(1.4 if s < 2 else 2.6 / s)
            c.stroke()
    st.ellipse(c, -23, 0, 9, 8, 0.0, SEG, seed=81)          # rostellum (the hooked tip)
    st.ellipse(c, 0, 0, 25, 22, 0.0, SEG, seed=82)
    # suckers: shallow cups on the rim of the head, low contrast so they never read as a second pair of eyes
    for sy in (-1, 1):
        ellipse(c, -9, sy * 15, 8, 5, sy * 0.35)
        c.set_source_rgba(*hexc("#e8d6b2")[:3], 0.95)
        c.fill_preserve()
        c.set_source_rgba(*hexc("#b89c6c")[:3], 0.55)
        c.set_line_width(1.2 if s < 2 else 2.2 / s)
        c.stroke()
        ellipse(c, -9, sy * 15, 4, 2.4, sy * 0.35)
        c.set_source_rgba(*hexc("#cdb588")[:3], 0.8)
        c.fill()
    if st.faces and not detail:
        # a small, centred face so Noodle reads as a character (kept upright)
        c.save()
        c.translate(3, 0)
        c.rotate(-ang)
        st.eye(c, -6, -3, 3.6, 0.1 if blink else 1.0)
        st.eye(c, 7, -3, 3.6, 0.1 if blink else 1.0)
        st.blush(c, -10, 5, 3.2, 0.35)
        st.blush(c, 11, 5, 3.2, 0.35)
        st.smile(c, 0.5, 4, 7, k=1 + happy)
        c.restore()
    c.pop_group_to_source()
    c.paint_with_alpha(alpha)
    c.restore()


def draw(c, st, pts, nseg=SEG_MAX, length_frac=1.0, skip_tail=0, alpha=1.0, size=1.0, blink=False, happy=0.0):
    lay = segment_layout(pts, nseg, length_frac, size)
    cum = _cum(pts)
    # the neck: a short pale unsegmented stretch that tapers from the head into the first segment
    # (owner, e005: a thin dark stalk made the body look detached from the head)
    neck = [pts[0]] + [_at(pts, cum, NECK * size * k / 6)[:2] for k in range(1, 7)]
    w0, w1 = 13 * size, 6.5 * size

    def neck_path(cc):
        left, right = [], []
        for k, (x, y) in enumerate(neck):
            xa, ya = neck[max(0, k - 1)]
            xb, yb = neck[min(len(neck) - 1, k + 1)]
            dx, dy = xb - xa, yb - ya
            ln = math.hypot(dx, dy) or 1
            nx, ny = -dy / ln, dx / ln
            w = lerp(w0, w1, k / (len(neck) - 1))
            left.append((x + nx * w, y + ny * w))
            right.append((x - nx * w, y - ny * w))
        cc.move_to(*left[0])
        for p in left[1:]:
            cc.line_to(*p)
        for p in reversed(right):
            cc.line_to(*p)
        cc.close_path()
    st.part(c, neck_path, SEG, *neck[3], 20 * size, seed=89, alpha=alpha)
    # segments on top of the neck's far end (it disappears under the first one)
    for i in reversed(range(nseg - skip_tail)):
        px, py, ang, l, w = lay[i]
        c.save()
        c.translate(px, py)
        c.rotate(ang)
        draw_segment(c, st, l, w, i > 13, alpha, seed=90 + i)
        c.restore()
    x0, y0 = pts[0]
    xa, ya = pts[3]
    draw_scolex(c, st, x0, y0, math.atan2(ya - y0, xa - x0), 0.8 * size, alpha, blink=blink, happy=happy)  # a small head on a long body (owner, e005: the scolex is tiny)
    return lay


def draw_grain(c, st, x, y, s, ang, wiggle, alpha=1.0, split=0.0, seed=0):
    if alpha <= 0:
        return
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    stretch = 1 + 0.18 * math.sin(wiggle)
    halves = ((0, -1), (1, 1)) if split > 0 else ((0, 0),)
    for _, d in halves:
        c.save()
        c.translate(d * split * 10, d * split * 6)
        c.rotate(d * split * 0.5)
        st.ellipse(c, 0, 0, 24 * s * stretch, 10 * s / math.sqrt(stretch), 0.0, SEG, seed=seed,
                   alpha=alpha * (1 - 0.5 * split))
        c.restore()
    c.restore()


def draw_egg_packet(c, st, x, y, r, alpha=1.0, seed=1):
    if alpha <= 0 or r <= 0.5:
        return
    rnd = rng(seed)
    c.arc(x, y, r, 0, TAU)
    c.set_source_rgba(1, 1, 1, 0.35 * alpha)
    c.fill_preserve()
    c.set_source_rgba(*hexc("#b8a070")[:3], 0.8 * alpha)
    c.set_line_width(max(1.2, r * 0.07))
    c.stroke()
    for k in range(9):
        a = k * TAU / 7 + rnd.uniform(-0.2, 0.2)
        d = 0 if k == 0 else r * (0.5 if k < 8 else 0.25)
        st.ellipse(c, x + math.cos(a) * d, y + math.sin(a) * d, r * 0.24, r * 0.24, 0.0, EGG, seed=seed + k, alpha=alpha)


def draw_cyst(c, st, x, y, r, alpha=1.0, glow=1.0, blink=False):
    if alpha <= 0:
        return
    import cairo
    g = cairo.RadialGradient(x, y, 0, x, y, r * 2.6)
    g.add_color_stop_rgba(0, 1, 0.95, 0.6, 0.75 * alpha * glow)
    g.add_color_stop_rgba(1, 1, 0.95, 0.6, 0)
    c.arc(x, y, r * 2.6, 0, TAU)
    c.set_source(g)
    c.fill()
    st.line(c, [(x + r * 0.9, y), (x + r * 1.6, y + r * 0.3), (x + r * 2.4, y)], r * 0.25, hexc("#e9dcb8"), alpha)
    st.ellipse(c, x, y, r, r * 0.75, 0.0, SEG, seed=97, alpha=alpha)
    c.arc(x - r * 0.15, y, r * 0.32, 0, TAU)
    c.set_source_rgba(*hexc("#b0773a")[:3], alpha)
    c.fill()
    if st.faces and r > 10:
        st.eye(c, x + r * 0.25, y - r * 0.2, r * 0.13, 0.1 if blink else 1.0)
