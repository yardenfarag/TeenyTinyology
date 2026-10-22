"""Final mix: music ducked under the narrator, sound effects on top, loudness-normalised for social."""
import json
import os
import subprocess
import wave

import numpy as np

from .common import SR, ffmpeg_exe


def duck_curve(voice, depth=0.45, smooth=0.25):
    env = np.abs(voice)
    k = max(1, int(smooth * SR))
    # moving average via cumulative sum (O(n); np.convolve with a long box kernel is far too slow)
    c = np.concatenate([[0.0], np.cumsum(env)])
    half = k // 2
    idx = np.arange(len(env))
    lo = np.clip(idx - half, 0, len(env))
    hi = np.clip(idx - half + k, 0, len(env))
    env = (c[hi] - c[lo]) / k
    active = np.clip(env / (env.max() * 0.08 + 1e-9), 0, 1)
    return 1 - depth * active


def mixdown(n, music=None, sfx=None, voice=None, music_gain=0.55, sfx_gain=1.0, voice_gain=0.8):
    out = np.zeros((n, 2))

    def fit(x):
        x = x[:n]
        return np.pad(x, [(0, n - len(x))] + [(0, 0)] * (x.ndim - 1))

    if music is not None:
        m = fit(music) / (np.abs(music).max() + 1e-9) * music_gain
        if voice is not None:
            m = m * fit(duck_curve(voice))[:, None]
        out += m
    if sfx is not None:
        out += fit(sfx) * sfx_gain
    if voice is not None:
        out += fit(voice)[:, None] * voice_gain
    peak = np.abs(out).max() + 1e-9
    return np.tanh(out / peak * 1.1) / np.tanh(1.1) * 0.9


def write_wav(path, x):
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


def loudnorm(src, dst, target=-14.0, tp=-1.8):  # aim below -1.5 dBTP: AAC encoding adds a little
    """Two-pass EBU R128 normalisation (TikTok / Shorts sit around -14 LUFS)."""
    ff = ffmpeg_exe()
    r = subprocess.run([ff, "-hide_banner", "-i", src, "-af", f"loudnorm=I={target}:TP={tp}:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    txt = r.stderr
    m = json.loads(txt[txt.rindex("{"):txt.rindex("}") + 1])
    af = (f"loudnorm=I={target}:TP={tp}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run([ff, "-v", "error", "-y", "-i", src, "-af", af, "-ar", str(SR), dst], check=True)
    return dst


def measure_lufs(path):
    r = subprocess.run([ffmpeg_exe(), "-hide_banner", "-i", path, "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True)
    for ln in r.stderr.splitlines()[::-1]:
        if ln.strip().startswith("I:"):
            return float(ln.split()[1])
    return None


def tmp_path(folder, name):
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, name)
