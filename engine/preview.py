"""Narration preview: the script read by the series narrator with the theme underneath (no visuals).

Usage: python -m engine.preview episodes.<pkg>.script out.mp3 [--mood cozy] [--no-music]
Prints each line's timing so pauses can be tuned.
"""
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
    os.remove(wav)
    for c in cues.values():
        print(f"{c.id:10s} {c.start:6.2f}-{c.end:6.2f}  {' '.join(w for w, _, _ in c.words)}")
    print(f"total {dur:.1f}s -> {a.out}")


if __name__ == "__main__":
    main()
