"""The Teenyology theme ("Theme C": celesta + marimba), arranged to any length with mood changes.

score(duration, moods) builds the 16-bar form (intro, looping theme, cadence) to fit the episode,
renders each instrument layer once, then shapes the layers with a smooth per-mood mix so the
music follows the story without ever changing tune.
"""
import math

import numpy as np

from .common import SR, Bus, attack, hz, tv, up

BPM = 74
B = 60 / BPM
BAR = 4 * B
START = 0.4

# bar index -> (bass root, chord tones)
FORM = [
    ("D2", ["D3", "F#3", "A3"]), ("G2", ["D3", "G3", "B3"]),
    ("D2", ["D3", "F#3", "A3"]), ("B1", ["D3", "F#3", "A3"]), ("G1", ["D3", "F#3", "B3"]), ("A1", ["C#3", "E3", "A3"]),
    ("D2", ["D3", "F#3", "A3"]), ("B1", ["D3", "F#3", "B3"]), ("G1", ["D3", "G3", "B3"]), ("A1", ["D3", "E3", "A3"]),
    ("E2", ["D3", "G3", "B3"]), ("G1", ["D3", "G3", "B3"]), ("F#1", ["D3", "F#3", "A3"]), ("A1", ["C#3", "E3", "A3"]),
    ("D2", ["D3", "F#3", "A3"]), ("D2", ["D3", "F#3", "A3"]),
]
# original melody, keyed by form bar: (beat, beats, note)
MELODY = {
    2: [(0, 2, "F#4"), (2, 1, "A4"), (3, 1, "B4")], 3: [(0, 3, "A4")],
    4: [(0, 1, "B4"), (1, 1, "A4"), (2, 2, "F#4")], 5: [(0, 3, "E4")],
    6: [(0, 1, "F#4"), (1, 1, "G4"), (2, 2, "A4")], 7: [(0, 2, "D5"), (2, 1, "C#5"), (3, 1, "B4")],
    8: [(0, 4, "A4")], 9: [(0, 1, "G4"), (1, 1, "F#4"), (2, 2, "E4")],
    10: [(0, 2, "G4"), (2, 2, "B4")], 11: [(0, 1, "A4"), (1, 1, "B4"), (2, 2, "D5")],
    12: [(0, 3, "A4")], 13: [(0, 1, "B4"), (1, 1, "A4"), (2, 2, "E4")], 14: [(0, 4, "F#4")],
}
ECHOES = {3: [(2.5, "B4"), (3, "A4")], 5: [(2.5, "A4"), (3, "F#4")], 8: [(2.5, "C#5"), (3, "B4")],
          12: [(2.5, "D5"), (3, "C#5")], 14: [(2, "A4"), (2.5, "D5")], 15: [(0, "F#5"), (1, "A5")]}

LAYERS = ["pad", "bass", "marimba", "melody", "echo", "brush", "low"]
MOODS = {
    #            pad   bass  mar   mel   echo  brush low
    "sleepy":   (0.34, 0.22, 0.05, 0.22, 0.07, 0.00, 0.06),
    "cozy":     (0.30, 0.35, 0.10, 0.34, 0.08, 0.03, 0.12),
    "curious":  (0.26, 0.35, 0.13, 0.30, 0.10, 0.03, 0.10),
    "mystery":  (0.36, 0.30, 0.06, 0.00, 0.12, 0.00, 0.00),
    "playful":  (0.22, 0.38, 0.15, 0.34, 0.10, 0.05, 0.10),
    "wonder":   (0.32, 0.30, 0.12, 0.36, 0.15, 0.02, 0.12),
    "finale":   (0.32, 0.38, 0.13, 0.38, 0.12, 0.04, 0.12),
    "quiet":    (0.20, 0.15, 0.03, 0.00, 0.04, 0.00, 0.00),
}


# ---------------------------------------------------------------- instruments
def felt_piano(f, d=3.0, vel=0.5):
    t = tv(d)
    s = np.zeros_like(t)
    for k, a in ((1, 1.0), (2, 0.42), (3, 0.2), (4, 0.1), (5, 0.05)):
        fk = f * k * (1 + 0.0004 * k * k)
        s += a * np.sin(2 * np.pi * fk * t) * np.exp(-t * (1.1 + 0.9 * k) * (f / 400) ** 0.3)
    return s * vel * (1 - np.exp(-t / 0.012))


def celesta(f, d=2.2):
    t = tv(d)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 2.4) + 0.3 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 5)
    return s * attack(t, 0.002)


def marimba(f, d=1.0):
    t = tv(d)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 6) + 0.3 * np.sin(2 * np.pi * f * 3.98 * t) * np.exp(-t * 20)
    return s * attack(t)


def kalimba(f, d=2.0):
    t = tv(d)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 2.2) + 0.25 * np.sin(2 * np.pi * f * 5.95 * t) * np.exp(-t * 14)
    return s * attack(t, 0.003)


def pad(freqs, d, rng, fade=0.8):
    t = tv(d)
    s = np.zeros_like(t)
    for f in freqs:
        for det in (-0.005, -0.0015, 0.002, 0.0055):
            s += np.sin(2 * np.pi * f * (1 + det) * t + rng.uniform(0, 6.3)) + 0.06 * np.sin(4 * np.pi * f * (1 + det) * t)
    env = np.minimum(np.clip(t / fade, 0, 1), np.clip((d - t) / fade, 0, 1))
    return s * env * (1 + 0.1 * np.sin(2 * np.pi * 0.2 * t)) / (4 * len(freqs))


# ---------------------------------------------------------------- arrangement
def bar_plan(duration):
    """Sequence of form-bar indices that fills the duration and ends on the cadence."""
    n = max(4, math.ceil((duration - START) / BAR) + 1)
    plan = [0, 1]
    theme = list(range(2, 14))
    i = 0
    while len(plan) < n - 2:
        plan.append(theme[i % len(theme)])
        i += 1
    return plan + [14, 15]


def _layers(duration, seed):
    plan = bar_plan(duration)
    total = START + len(plan) * BAR + 3
    L = {k: Bus(total, seed + i) for i, k in enumerate(LAYERS)}
    for slot, fb in enumerate(plan):
        t0 = START + slot * BAR
        root, ch = FORM[fb]
        L["pad"].add(t0, pad([hz(n) for n in ch], BAR + 1.0, L["pad"].rng), 0, 1.0)
        L["bass"].add(t0, felt_piano(hz(root), BAR, 0.5), 0, 1.0)
        for j in range(8):
            n = ch[[0, 1, 2, 1][j % 4] % len(ch)]
            L["marimba"].add(t0 + j * B / 2, marimba(hz(up(n))), 0.35 * (-1) ** j, 1.0)
        for j in (1, 3):
            br = L["brush"].noise(0.25, 1500, 7000) * np.exp(-tv(0.25) * 10)
            L["brush"].add(t0 + j * B, br, -0.15, 1.0)
        for beat, beats, n in MELODY.get(fb, []):
            d = beats * B + 1.2
            L["melody"].add(t0 + beat * B, celesta(hz(n), min(d, 2.5)), 0.1, 1.0)
            L["low"].add(t0 + beat * B, felt_piano(hz(up(n, -1)), d, 0.4), -0.1, 1.0)
        for beat, n in ECHOES.get(fb, []):
            L["echo"].add(t0 + beat * B, kalimba(hz(up(n)), 1.8), 0.45, 1.0)
    return L, total


def _envelopes(moods, total, n):
    """moods: [(time, mood_name)] -> per-layer gain curves, with ~1.2 s crossfades."""
    t = np.arange(n) / SR
    moods = sorted(moods)
    env = np.zeros((n, len(LAYERS)))
    for i, (t0, m) in enumerate(moods):
        t1 = moods[i + 1][0] if i + 1 < len(moods) else total + 10
        w = np.clip((t - t0 + 0.6) / 1.2, 0, 1) * np.clip((t1 - t + 0.6) / 1.2, 0, 1)
        env += w[:, None] * np.array(MOODS[m])[None, :]
    return env


def score(duration, moods=None, seed=7):
    """Return stereo float array (len = duration*SR) of the theme for this episode."""
    moods = moods or [(0, "cozy")]
    L, total = _layers(duration, seed)
    n = L["pad"].n
    env = _envelopes(moods, total, n)
    mix = Bus(total, seed)
    for i, k in enumerate(LAYERS):
        mix.buf += L[k].buf * env[:, i:i + 1]
    mix.lowpass(4000)
    mix.reverb(2.6, 0.38)
    out = mix.buf[: int(duration * SR)]
    fade = np.ones(len(out))
    k = int(min(2.5, duration / 4) * SR)
    fade[-k:] = np.linspace(1, 0, k) ** 1.5
    return out * fade[:, None]
