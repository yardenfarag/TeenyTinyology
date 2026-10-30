"""Pre-judge checks on the ENCODED mp4. Written after judge pass 2 showed the earlier checks were
measuring the wrong thing in three ways:

  * loudness was read without a true-peak / sample-peak gate, so a +1.97 dBFS clip passed;
  * silence was never checked, so 2.0 s of digital zero under the end card passed;
  * motion was differenced over the whole frame, and the caption band churning every ~1.5 s lifted
    dead scenes over a fixed threshold. Mask the captions and the watermark, and compare each scene
    against THIS episode's own 75th percentile rather than an absolute number.
"""
import subprocess
import sys

import numpy as np
from PIL import Image

from engine.audio.mix import ffmpeg_exe, measure_lufs

SR = 48000
CAP_BAND = (1300, 1500)     # caption bubbles live here
# scene.WM_X/WM_Y = 60/242, WM_R = 52 -> centre (112, 254). The first version of this box masked rows
# 0-200 / cols 0-320, i.e. empty sky, and never touched the badge at all (judge pass 3).
WM = (190, 325, 45, 180)    # rows, cols covering the badge and its shadow


def audio(mp4):
    r = subprocess.run([ffmpeg_exe(), "-v", "error", "-i", mp4, "-map", "0:a", "-f", "f32le",
                        "-acodec", "pcm_f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True)
    a = np.frombuffer(r.stdout, dtype=np.float32).reshape(-1, 2)
    peak = float(np.abs(a).max())
    over = int((np.abs(a) > 1.0).sum())
    # true peak: a decoded-sample max is NOT inter-sample peak, which is what the series rule is about.
    # Read ffmpeg's own figure rather than guessing (judge pass 3).
    r2 = subprocess.run([ffmpeg_exe(), "-hide_banner", "-i", mp4, "-map", "0:a",
                         "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    tp = None
    for ln in r2.stderr.splitlines():
        if "Peak:" in ln:
            try:
                tp = float(ln.split("Peak:")[1].split()[0])
            except (ValueError, IndexError):
                pass
    # 50% overlap, so a run shorter than two whole windows is still resolvable
    step = SR // 20
    w = SR // 10
    starts = list(range(0, max(1, len(a) - w), step))
    db = np.array([20 * np.log10(float(np.sqrt((a[i:i + w] ** 2).mean()) + 1e-12)) for i in starts])
    runs, s = [], None
    for i, v in enumerate(db):
        ts = starts[i] / SR
        if v < -50 and s is None:
            s = ts
        elif v >= -50 and s is not None:
            if ts - s >= 0.5:
                runs.append((round(s, 2), round(ts, 2)))
            s = None
    if s is not None and len(a) / SR - s >= 0.5:
        runs.append((round(s, 2), round(len(a) / SR, 2)))
    return dict(lufs=measure_lufs(mp4), peak_db=20 * np.log10(peak + 1e-12), true_peak=tp,
                over=over, quiet_runs=runs, zeros=int((a == 0).all(axis=1).sum()))


def frames(mp4, step=0.25):
    ff, out, t = ffmpeg_exe(), [], 0.0
    while True:
        r = subprocess.run([ff, "-v", "error", "-ss", str(t), "-i", mp4, "-frames:v", "1",
                            "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
        if not r.stdout:
            break
        im = np.asarray(Image.open(__import__("io").BytesIO(r.stdout)).convert("L"), dtype=float)
        raw = im[::8, ::8].copy()                   # unmasked, for the black-frame test
        im = im.copy()
        im[CAP_BAND[0]:CAP_BAND[1], :] = 0          # mask the captions
        im[WM[0]:WM[1], WM[2]:WM[3]] = 0            # mask the watermark
        out.append((t, im[::8, ::8], raw))
        t += step
    return out


def picture(mp4, scenes, step=0.25):
    fr = frames(mp4, step)
    ts = [t for t, _, _ in fr]
    black = [t for t, _, raw in fr if raw.mean() < 12 and raw.std() < 6]   # on the UNMASKED frame
    d = np.array([np.abs(fr[i + 1][1] - fr[i][1]).mean() for i in range(len(fr) - 1)])
    p75 = float(np.percentile(d, 75))
    # "nothing frozen > 2 s" is a run-length rule; a per-scene mean averages a freeze away entirely.
    frozen, s = [], None
    for i, v in enumerate(d):
        if v < 0.02 and s is None:
            s = ts[i]
        elif v >= 0.02 and s is not None:
            if ts[i] - s >= 1.0:
                frozen.append((round(s, 2), round(ts[i], 2)))
            s = None
    rows = []
    for name, s0, s1 in scenes:
        # exclude +-0.5 s around a boundary: the crossfade inflates a short scene's mean
        v = [d[i] for i, t in enumerate(ts[:-1]) if s0 + 0.5 <= t < s1 - 0.5]
        if v:
            rows.append((name, s0, s1, float(np.mean(v)), float(np.mean(v)) / p75))
    return black, p75, sorted(rows, key=lambda r: r[4]), frozen


if __name__ == "__main__":
    mp4 = sys.argv[1]
    from episodes.e002_roly_mango.episode import build
    tl, _, _, _ = build("illustrated")
    scenes = [(s.fn.__name__, s.start, s.end) for s in tl.scenes]
    a = audio(mp4)
    print(f"LUFS {a['lufs']}  sample peak {a['peak_db']:+.2f} dBFS  true peak {a['true_peak']} dBFS"
          f"  samples>1.0: {a['over']}  exact-zero samples: {a['zeros']}")
    print(f"runs >=0.5s below -50 dB RMS: {a['quiet_runs'] or 'none'}")
    black, p75, rows, frozen = picture(mp4, scenes)
    print(f"frozen runs >=1.0s: {frozen or 'none'}  (rule: nothing frozen > 2 s)")
    print(f"black frames: {black or 'none'}   picture p75 = {p75:.2f}")
    print("scenes below 0.45x the episode's own p75 (captions + watermark masked):")
    flagged = [r for r in rows if r[4] < 0.45]
    for n, s0, s1, m, ratio in flagged:
        print(f"   {n:12} {s0:6.1f}-{s1:6.1f} ({s1-s0:4.1f}s)  mean {m:5.2f}  ratio {ratio:.2f}")
    print("   none" if not flagged else "")
