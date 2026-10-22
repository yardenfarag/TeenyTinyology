"""Frame rendering, previews and MP4 export."""
import os
import subprocess

import cairo

from .audio.common import ffmpeg_exe
from .core import FPS, H, W
from .scene import render_frame


def stills(tl, ctx, times, folder, prefix="still"):
    os.makedirs(folder, exist_ok=True)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    paths = []
    for t in times:
        render_frame(cairo.Context(s), t, tl, ctx)
        p = os.path.join(folder, f"{prefix}_{t:06.2f}.png")
        s.write_to_png(p)
        paths.append(p)
    return paths


def contact_sheet(paths, out, cols=6, width=2000):
    """Tile PNGs into one review image."""
    n = len(paths)
    if not n:
        return None
    args = []
    for p in paths:
        args += ["-i", p]
    rows = (n + cols - 1) // cols
    filt = "".join(f"[{i}]scale={width // cols}:-1[s{i}];" for i in range(n))
    cells = [f"[s{i}]" for i in range(n)]
    blank = rows * cols - n
    if blank:
        filt += f"color=c=black:s={width // cols}x{int(width // cols * H / W)}:d=1,split={blank}" + "".join(
            f"[b{i}]" for i in range(blank)) + ";"
        cells += [f"[b{i}]" for i in range(blank)]
    row_out = []
    for r in range(rows):
        row = cells[r * cols:(r + 1) * cols]
        filt += "".join(row) + f"hstack={cols}[r{r}];"
        row_out.append(f"[r{r}]")
    filt += "".join(row_out) + (f"vstack={rows}" if rows > 1 else "null")
    subprocess.run([ffmpeg_exe(), "-v", "error", "-y", *args, "-filter_complex", filt, "-frames:v", "1", out], check=True)
    return out


def video(tl, ctx, out, audio_wav=None, crf=17, log_every=150):
    """Render every frame and encode H.264 (+AAC audio if given)."""
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    cmd = [ffmpeg_exe(), "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-"]
    if audio_wav:
        cmd += ["-i", audio_wav, "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    n = int(tl.duration * FPS)
    for i in range(n):
        render_frame(cairo.Context(s), i / FPS, tl, ctx)
        s.flush()
        proc.stdin.write(bytes(s.get_data()))
        if log_every and i % log_every == 0:
            print(f"  frame {i}/{n}", flush=True)
    proc.stdin.close()
    proc.wait()
    return out


def sample_frames(mp4, out_png, every=1.0, cols=10, width=2000):
    """Contact sheet straight from the encoded MP4 (final QA)."""
    subprocess.run([ffmpeg_exe(), "-v", "error", "-y", "-i", mp4, "-vf",
                    f"fps={1 / every},scale={width // cols}:-1,tile={cols}x8", "-frames:v", "1", out_png], check=True)
    return out_png
