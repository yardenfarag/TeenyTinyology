"""Narration preview: the script read by the series narrator with the theme underneath (no visuals).

Usage: python -m engine.preview episodes.<pkg>.script out.mp3 [--mood cozy] [--no-music] [--batches]
Prints each line's timing so pauses can be tuned.

--batches also writes one short MP3 per group of lines (the letters before the number in the line id: a1..a8 → "a")
plus <out>_batches.md, a timestamped line list per batch, so the owner can review a long script piece by piece and
point at a line ("b · 0:42"). Lines flagged by the voice QA are marked there.
"""
import json
import re
import argparse
import importlib
import os

from engine.audio import mix, music
from engine.audio.common import SR
from engine.voice import narrate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script_module")
    ap.add_argument("out")
    ap.add_argument("--mood", default="cozy")
    ap.add_argument("--no-music", action="store_true")
    ap.add_argument("--batches", action="store_true")
    a = ap.parse_args()
    mod = importlib.import_module(a.script_module)
    cache = os.path.join(os.path.dirname(mod.__file__), "voice_cache")
    track, cues, caps, end = narrate(mod.SCRIPT, cache)
    dur = end + 1.5
    n = int(dur * SR)
    m = None if a.no_music else music.score(dur, [(0, a.mood)])
    from engine.audio import sfx as sfxlib
    from engine.audio.common import Bus
    fx = Bus(dur, 3)
    from engine.voice import sfx_events
    for ln in mod.SCRIPT:  # silent beats: the sound effect replaces the words
        if ln.sfx:
            fx.add(cues[ln.id].start, sfxlib.LIB[ln.sfx](), 0.0, 0.5)
    for t0, name, gain in sfx_events(getattr(mod, "SFX", []), cues):  # every word-anchored effect
        fx.add(t0, sfxlib.LIB[name](), 0.0, gain)
    out = mix.mixdown(n, music=m, sfx=fx.buf, voice=track, music_gain=0.5)
    raw = a.out.replace(".mp3", "_raw.wav")
    mix.write_wav(raw, out)
    wav = a.out.replace(".mp3", ".wav")
    mix.loudnorm(raw, wav)
    os.remove(raw)
    from engine.audio.common import ffmpeg_exe
    import subprocess
    subprocess.run([ffmpeg_exe(), "-v", "error", "-y", "-i", wav, "-b:a", "192k", a.out], check=True)
    if a.batches:
        batches(mod.SCRIPT, cues, wav, a.out, os.path.join(cache, "qa.json"))
    os.remove(wav)
    for c in cues.values():
        print(f"{c.id:10s} {c.start:6.2f}-{c.end:6.2f}  {' '.join(w for w, _, _ in c.words)}")
    print(f"total {dur:.1f}s -> {a.out}")


def batches(script, cues, wav, out, qa_path):
    from engine.audio.common import ffmpeg_exe
    import subprocess
    qa = json.load(open(qa_path, encoding="utf8")) if os.path.exists(qa_path) else {}
    groups = {}
    for ln in script:
        groups.setdefault(re.match(r"[a-zA-Z_]*", ln.id).group(0) or "main", []).append(ln)
    stem = out[:-4]
    md = [f"# Narration batches for {os.path.basename(out)}", "",
          "Listen to one batch at a time. Note problems as batch + time, e.g. \"b · 0:42 cut off\".", ""]
    for g, lines in groups.items():
        t0 = max(0.0, cues[lines[0].id].start - 0.6)
        t1 = cues[lines[-1].id].end + 1.0
        path = f"{stem}_{g}.mp3"
        subprocess.run([ffmpeg_exe(), "-v", "error", "-y", "-ss", f"{t0:.3f}", "-to", f"{t1:.3f}", "-i", wav,
                        "-af", "afade=t=in:d=0.05", "-b:a", "192k", path], check=True)
        md += [f"## Batch {g.upper()} · `{os.path.basename(path)}` · {t1 - t0:.0f} s", ""]
        for ln in lines:
            s = cues[ln.id].start - t0
            flag = f"  ⚠ {', '.join(qa[ln.id])}" if ln.id in qa else ""
            md.append(f"- `{int(s // 60)}:{s % 60:04.1f}` **{ln.id}** {ln.text}{flag}")
        md.append("")
    with open(f"{stem}_batches.md", "w", encoding="utf8") as f:
        f.write("\n".join(md))
    print(f"{len(groups)} batches -> {stem}_*.mp3, {stem}_batches.md")


if __name__ == "__main__":
    main()
