"""The TeenyTinyology sound-effect library (all synthesised). Each function returns a mono array.

Use with a Bus:  fx.add(t, sfx.pop(), pan, gain)  or the helper  play(bus, "pop", t, ...).
"""
import numpy as np

from .common import SR, attack, tv

_rng = np.random.default_rng(99)


def _noise(d, lo, hi):
    n = int(d * SR)
    spec = np.fft.rfft(_rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    spec *= (f > lo) & (f < hi)
    out = np.fft.irfft(spec, n)
    return out / (np.abs(out).max() + 1e-9)


def _sweep(f0, f1, d, curve=1.0):
    t = tv(d)
    f = f0 + (f1 - f0) * (t / d) ** curve
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def pop(f=900):
    t = tv(0.12)
    fr = f * np.exp(-t * 25) + 300
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 35)


def blip(f=800):
    t = tv(0.09)
    return _sweep(f, f * 1.8, 0.09) * np.exp(-t * 30)


def whoosh(d=0.7, lo=300, hi=2500):
    t = tv(d)
    return _noise(d, lo, hi) * np.sin(np.pi * t / d) ** 3


def crunch():
    t = tv(0.07)
    return _noise(0.07, 1500, 7000) * np.exp(-t * 60)


def boing():
    t = tv(0.5)
    return _sweep(180, 900, 0.5, 0.6) * (1 + 0.5 * np.sin(2 * np.pi * 18 * t)) * np.exp(-t * 3) * attack(t, 0.01)


def scratch():
    out = np.zeros(int(0.42 * SR))
    for k in range(4):
        d = 0.06
        t = tv(d)
        s = _noise(d, 2000, 6000) * np.sin(np.pi * t / d)
        i0 = int(k * 0.1 * SR)
        out[i0:i0 + len(s)] += s
    return out


def slurp(d=0.4):
    t = tv(d)
    return _noise(d, 200, 1800) * np.sin(2 * np.pi * (6 + 14 * t / d) * t) ** 2 * np.sin(np.pi * t / d)


def gulp():
    t = tv(0.35)
    return _sweep(320, 70, 0.35, 0.7) * np.exp(-t * 7) * attack(t, 0.01)


def riser(d=1.2):
    t = tv(d)
    s = _sweep(240, 960, d, 1.5) * (t / d) ** 2 + 0.5 * _noise(d, 2500, 8000) * (t / d) ** 3
    return s * (1 + 0.4 * np.sin(2 * np.pi * (4 + 10 * t / d) * t))


def buzz():
    out = np.zeros(int(0.45 * SR))
    for k, f in enumerate((220, 165)):
        t = tv(0.22)
        s = (np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + np.sin(2 * np.pi * f * t)) * np.exp(-t * 6) * attack(t, 0.01)
        i0 = int(k * 0.2 * SR)
        out[i0:i0 + len(s)] += s
    return out


def whine(d=1.2, f0=640, f1=520, shape="flyby", vib=0.018, bright=1.0, soft=0.45):
    """A mosquito's wingbeat whine (females beat their wings ~400-700 times a second): a high tone with soft
    harmonics, a slight wobble and flutter. shape "flyby" swells and fades with a falling pitch (passing by),
    "hover" holds steady with short soft edges. Much gentler than buzz(), which is a cartoon buzzer."""
    t = tv(d)
    f = (f0 + (f1 - f0) * t / d) * (1 + vib * np.sin(2 * np.pi * 6.3 * t) + 0.5 * vib * np.sin(2 * np.pi * 2.1 * t + 1))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = (np.sin(ph) + 0.42 * bright * np.sin(2 * ph + 0.4) + 0.18 * bright * np.sin(3 * ph + 1.1)
         + 0.07 * bright * np.sin(4 * ph + 2.0))
    s *= 1 + 0.12 * np.sin(2 * np.pi * 11 * t)                 # wing flutter
    if shape == "flyby":
        env = np.sin(np.pi * t / d) ** 1.6
    else:
        env = np.clip(t / 0.18, 0, 1) * np.clip((d - t) / 0.25, 0, 1)
    s *= env
    return soft * s / (np.abs(s).max() + 1e-9)


def click():
    t = tv(0.03)
    return np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 200)


def chime(f=1046.5):
    t = tv(1.6)
    s = sum(a * np.sin(2 * np.pi * f * p * t) * np.exp(-t * k) for p, a, k in ((1, 1, 1.8), (2.76, 0.4, 3.5), (5.4, 0.2, 7)))
    return s * attack(t, 0.002)


def sparkle():
    out = np.zeros(int(1.2 * SR))
    for i, f in enumerate((1568, 2093, 2637, 3136, 2637)):
        s = chime(f)[: int(0.9 * SR)] * 0.5
        i0 = int(i * 0.06 * SR)
        out[i0:i0 + len(s)] += s[: len(out) - i0]
    return out


def purr(d=3.0):
    t = tv(d)
    am = 0.55 + 0.45 * np.sin(2 * np.pi * 24 * t)
    env = np.minimum(np.clip(t / 0.6, 0, 1), np.clip((d - t) / 0.6, 0, 1))
    return _noise(d, 40, 260) * am * env


def flap():
    t = tv(0.11)
    return _noise(0.11, 150, 1400) * np.exp(-t * 28) * attack(t, 0.01)


def snap():
    a = _noise(0.04, 2500, 9000) * np.exp(-tv(0.04) * 120)
    t = tv(0.35)
    b = np.sin(2 * np.pi * np.cumsum(160 * np.exp(-t * 8) + 50) / SR) * np.exp(-t * 10)
    out = np.zeros(len(b))
    out[: len(a)] += a * 0.8
    return out + b * 0.7


def tick():
    t = tv(0.02)
    return _noise(0.02, 3000, 9000) * np.exp(-t * 300)


def chirp(f0=3000, f1=4200, d=0.08):
    t = tv(d)
    return _sweep(f0, f1, d) * np.sin(np.pi * t / d) ** 2


def birdsong():
    out = np.zeros(int(0.6 * SR))
    for k in range(3):
        f0 = _rng.uniform(2600, 3800)
        s = chirp(f0, f0 * _rng.uniform(1.2, 1.5), _rng.uniform(0.05, 0.09))
        i0 = int(k * 0.12 * SR)
        out[i0:i0 + len(s)] += s
    return out


def bubbles(d=1.5, rate=8):
    out = np.zeros(int(d * SR))
    t = 0.0
    while t < d - 0.1:
        s = blip(_rng.uniform(500, 1400)) * 0.6
        i0 = int(t * SR)
        out[i0:i0 + len(s)] += s[: len(out) - i0]
        t += _rng.exponential(1 / rate)
    return out


def footsteps(d=1.5, rate=9):
    out = np.zeros(int(d * SR))
    for k in range(int(d * rate)):
        s = tick()
        i0 = int(k / rate * SR)
        out[i0:i0 + len(s)] += s[: len(out) - i0]
    return out


def ruffle(d=0.6):
    t = tv(d)
    return _noise(d, 400, 5000) * (0.5 + 0.5 * np.sin(2 * np.pi * 14 * t)) * np.sin(np.pi * t / d)


def splash():
    t = tv(0.9)
    body = _noise(0.9, 300, 6000) * np.exp(-t * 5) * attack(t, 0.005)
    plop = np.sin(2 * np.pi * np.cumsum(500 * np.exp(-t * 18) + 120) / SR) * np.exp(-t * 14)
    return body * 0.8 + plop * 0.6


def shimmer(d=1.2):
    out = np.zeros(int(d * SR))
    for i in range(10):
        f = 1800 + 180 * i
        s = chime(f)[: int(0.7 * SR)] * 0.25
        i0 = int(i * d / 12 * SR)
        out[i0:i0 + len(s)] += s[: len(out) - i0]
    return out


LIB = {k: v for k, v in globals().items() if callable(v) and not k.startswith("_") and k not in ("tv", "attack")}


def play(bus, name, t, gain=0.3, pan=0.0, **kw):
    bus.add(t, LIB[name](**kw), pan, gain)
