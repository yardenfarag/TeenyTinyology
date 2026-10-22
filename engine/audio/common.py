"""Audio primitives shared by the music, sfx and mix modules."""
import numpy as np

SR = 44100


def ffmpeg_exe():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


NOTE = {"C": -9, "C#": -8, "Db": -8, "D": -7, "D#": -6, "Eb": -6, "E": -5, "F": -4, "F#": -3, "Gb": -3,
        "G": -2, "G#": -1, "Ab": -1, "A": 0, "A#": 1, "Bb": 1, "B": 2}


def hz(n):
    return 440.0 * 2 ** ((NOTE[n[:-1]] + 12 * (int(n[-1]) - 4)) / 12)


def up(n, octs=1):
    return n[:-1] + str(int(n[-1]) + octs)


def tv(d):
    return np.arange(int(max(d, 0) * SR)) / SR


def attack(t, a=0.004):
    return np.clip(t / a, 0, 1)


class Bus:
    """Stereo buffer you can drop signals into."""

    def __init__(self, dur, seed=1):
        self.dur = dur
        self.n = int(dur * SR)
        self.buf = np.zeros((self.n, 2))
        self.rng = np.random.default_rng(seed)

    def add(self, t0, sig, pan=0.0, gain=1.0):
        i0 = int(t0 * SR)
        if i0 >= self.n or len(sig) == 0:
            return
        if i0 < 0:
            sig, i0 = sig[-i0:], 0
        sig = sig[: self.n - i0] * gain
        self.buf[i0:i0 + len(sig), 0] += sig * np.sqrt(0.5 * (1 - pan))
        self.buf[i0:i0 + len(sig), 1] += sig * np.sqrt(0.5 * (1 + pan))

    def noise(self, d, lo, hi):
        n = int(d * SR)
        if n <= 0:
            return np.zeros(0)
        spec = np.fft.rfft(self.rng.standard_normal(n))
        f = np.fft.rfftfreq(n, 1 / SR)
        spec *= (f > lo) & (f < hi)
        out = np.fft.irfft(spec, n)
        return out / (np.abs(out).max() + 1e-9)

    def lowpass(self, cutoff):
        f = np.fft.rfftfreq(self.n, 1 / SR)
        h = 1 / np.sqrt(1 + (f / cutoff) ** 4)
        for ch in range(2):
            self.buf[:, ch] = np.fft.irfft(np.fft.rfft(self.buf[:, ch]) * h, self.n)

    def reverb(self, secs=2.2, wet=0.3, decay=3.0):
        n = int(secs * SR)
        ir = self.rng.standard_normal((n, 2)) * np.exp(-np.arange(n) / SR * decay)[:, None]
        ir[0] = 0
        L = self.n + n
        out = np.zeros_like(self.buf)
        for ch in range(2):
            out[:, ch] = np.fft.irfft(np.fft.rfft(self.buf[:, ch], L) * np.fft.rfft(ir[:, ch], L), L)[: self.n]
        peak = np.abs(self.buf).max() + 1e-9
        out /= np.abs(out).max() + 1e-9
        self.buf = self.buf + wet * out * peak
