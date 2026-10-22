"""Narration: ElevenLabs (Remi) with per-word timestamps, caching, natural pauses and caption timing.

Each script line is synthesised on its own (with the neighbouring lines passed as context so the
delivery still flows), trimmed, then laid out with an explicit pause after it. Word timings come
back from ElevenLabs, so captions and sound effects can lock to the exact spoken word.
"""
import base64
import hashlib
import json
import math
import os
import re
import subprocess
import urllib.request
from dataclasses import dataclass

import numpy as np

from .audio.common import SR, ffmpeg_exe
from .scene import Caption

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VOICE_ID = "uk7wwhXdWYHKKZ8KTCVw"  # Miles (series narrator since ep. 001 v2; Remi was 4quIIyCzGDA8dBVvcXKl)
MODEL = "eleven_multilingual_v2"
SETTINGS = {"stability": 0.55, "similarity_boost": 0.8, "style": 0.15, "use_speaker_boost": True, "speed": 1.0}


@dataclass
class Line:
    id: str
    text: str
    pause: float = 0.5        # silence after this line (seconds)
    caption: bool = True
    sfx: str = None           # sound-effect name for a silent beat (text == ""): the beat lasts `pause` seconds
    take: int = 0             # bump to get a fresh read of the same text (ElevenLabs seed)


@dataclass
class Cue:
    id: str
    start: float
    end: float
    words: list               # [(word, abs_start, abs_end)]
    breaks: tuple = ()        # word indices where a caption line must start (from "|" in the script text)

    def word(self, needle, which=0):
        """Absolute start time of the n-th word containing needle (case-insensitive)."""
        hits = [s for w, s, _ in self.words if needle.lower() in w.lower()]
        return hits[which] if len(hits) > which else self.start


def spoken_text(text):
    """Script text may contain "|" to force a caption line break; it is never sent to the voice."""
    return re.sub(r"\s*\|\s*", " ", text).strip()


def forced_breaks(text):
    out, n = [], 0
    for part in text.split("|")[:-1]:
        n += len(part.split())
        out.append(n)
    return tuple(out)


def api_key():
    key = os.environ.get("ELEVENLABS_API_KEY")
    env = os.path.join(ROOT, ".env")
    if not key and os.path.exists(env):
        for ln in open(env, encoding="utf8"):
            if ln.strip().startswith("ELEVENLABS_API_KEY="):
                key = ln.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        raise SystemExit("No ELEVENLABS_API_KEY (set env var or teenyology/.env)")
    return key


def _synth(text, prev, nxt, cache_dir, take=0, h=None):
    body = {"text": text, "model_id": MODEL, "previous_text": prev or None, "next_text": nxt or None,
            "voice_settings": SETTINGS}
    if take:
        body["seed"] = take
    h = h or hashlib.sha1(json.dumps([VOICE_ID, body], sort_keys=True).encode()).hexdigest()[:16]
    os.makedirs(cache_dir, exist_ok=True)
    jpath = os.path.join(cache_dir, f"{h}.json")
    if not os.path.exists(jpath):
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/with-timestamps?output_format=mp3_44100_128",
            data=json.dumps(body).encode(), method="POST",
            headers={"xi-api-key": api_key(), "Content-Type": "application/json"})
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())
        with open(jpath, "w", encoding="utf8") as f:
            json.dump({"text": text, "audio_base64": data["audio_base64"], "alignment": data["alignment"]}, f)
    with open(jpath, encoding="utf8") as f:
        data = json.load(f)
    mp3 = os.path.join(cache_dir, f"{h}.mp3")
    if not os.path.exists(mp3):
        with open(mp3, "wb") as f:
            f.write(base64.b64decode(data["audio_base64"]))
    pcm = subprocess.run([ffmpeg_exe(), "-v", "error", "-i", mp3, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, "<i2").astype(float) / 32768
    return audio, _words(data["alignment"]), h


def _words(al):
    words, cur, s, e = [], "", None, None
    for ch, cs, ce in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if ch.isspace():
            if cur:
                words.append((cur, s, e))
            cur, s = "", None
            continue
        if s is None:
            s = cs
        cur += ch
        e = ce
    if cur:
        words.append((cur, s, e))
    return words


def _trim(audio, thr=0.012, pad=0.03):
    idx = np.where(np.abs(audio) > thr)[0]
    if not len(idx):
        return audio, 0.0
    a = max(0, idx[0] - int(pad * SR))
    b = min(len(audio), idx[-1] + int(pad * SR))
    return audio[a:b], a / SR


def narrate(lines, cache_dir, t0=0.8):
    """Returns (voice_track, cues: dict id->Cue, captions: list[Caption], end_time)."""
    clips, t = [], t0
    cues = {}
    texts = [spoken_text(ln.text) for ln in lines]
    # Approved takes stay locked: once a line has audio, editing a neighbour (which changes the context sent to
    # ElevenLabs) must not silently re-voice it. Change the line's text or `take` to get a new read.
    lock_path = os.path.join(cache_dir, "takes.lock.json")
    lock = json.load(open(lock_path, encoding="utf8")) if os.path.exists(lock_path) else {}
    for i, ln in enumerate(lines):
        if not ln.text:  # silent beat (a sound effect says it instead of the narrator)
            cues[ln.id] = Cue(ln.id, t, t + ln.pause, [])
            t += ln.pause
            continue
        spoken = [x for x in texts if x]
        j = spoken.index(spoken_text(ln.text))
        prev = " ".join(spoken[max(0, j - 2):j])
        nxt = " ".join(spoken[j + 1:j + 2])
        hit = lock.get(VOICE_ID + ":" + ln.id)
        said = spoken_text(ln.text)
        hit = hit["hash"] if hit and hit["text"] == said and hit.get("take", 0) == ln.take and             os.path.exists(os.path.join(cache_dir, hit["hash"] + ".json")) else None
        audio, words, h = _synth(said, prev, nxt, cache_dir, ln.take, hit)
        lock[VOICE_ID + ":" + ln.id] = {"text": said, "take": ln.take, "hash": h}
        audio, off = _trim(audio)
        dur = len(audio) / SR
        # alignment can stretch the last word over trailing silence; clamp to the audible audio
        words = [(w, t + min(dur, max(0.0, s - off)), t + min(dur, max(0.0, e - off))) for w, s, e in words]
        cues[ln.id] = Cue(ln.id, t, t + dur, words, forced_breaks(ln.text))
        clips.append((t, audio, ln))
        t += dur + ln.pause
    end = t
    with open(lock_path, "w", encoding="utf8") as f:
        json.dump(lock, f, indent=1)
    track = np.zeros(int((end + 1) * SR))
    for start, audio, _ in clips:
        i0 = int(start * SR)
        track[i0:i0 + len(audio)] += audio
    caps = []
    for _, _, ln in clips:
        if ln.caption:
            caps += chunk_captions(cues[ln.id])
    return track, cues, finalize_captions(caps), end


WEAK_ENDS = {"a", "an", "the", "of", "to", "in", "on", "at", "for", "and", "or", "but", "with", "by", "from", "her",
             "his", "its", "their", "my", "your", "our", "is", "are", "was", "be", "that", "this", "as", "into", "so",
             "no", "can", "will", "get", "got", "she", "he", "it", "they", "we", "you", "i", "new", "next", "tiny"}


BOUND_STARTS = {"it", "up", "off", "out", "down", "away"}   # words that belong with the word before them


def chunk_captions(cue, max_w=None):
    """Split a line's words into ONE-LINE caption chunks: break at punctuation when sensible, otherwise when the
    next word would make the line wider than the caption bubble allows."""
    from . import text
    from .scene import CAP_MAX_W, CAP_SIZE
    max_w = max_w or CAP_MAX_W - 64
    words = cue.words

    def w_of(ws):
        return text.width(" ".join(x[0] for x in ws), CAP_SIZE, bold=True)

    # Best split by dynamic programming: lines must fit; prefer ending at sentence/clause punctuation, never end on
    # a little word ("a", "the", "of"...), avoid one-word orphans, keep lines roughly balanced.
    n = len(words)
    best = [0.0] + [math.inf] * n
    back = [0] * (n + 1)
    for j in range(1, n + 1):
        for i in range(j - 1, -1, -1):
            grp = words[i:j]
            wd = w_of(grp)
            if wd > max_w and j - i > 1:
                break
            last = grp[-1][0]
            cost = 1.0 + ((max_w - wd) / max_w) ** 2 * 0.6
            if i in cue.breaks:
                cost -= 6.0
            elif i > 0 and cue.breaks:
                cost += 4.0          # the script chose its breaks: don't add others unless a line won't fit
            cost += sum(6.0 for b in cue.breaks if i < b < j)
            if grp[-1][2] - grp[0][1] < 0.9:      # on screen too briefly to read
                cost += 1.2
            if j < n:
                if re.search(r"[.!?…]$", last):
                    cost -= 1.2
                elif re.search(r"[,:;]$", last) or last.endswith("..."):
                    cost -= 0.7
                elif last.lower().strip("\"'") in WEAK_ENDS:
                    cost += 3.0
                if words[j][0].lower().strip(".,!?…") in BOUND_STARTS:
                    cost += 2.5
                # a sentence end inside the line (not at its end) reads worse than breaking there
            cost += sum(2.0 for w in grp[:-1] if re.search(r"[.!?…]$", w[0]))
            if j - i == 1:
                cost += 1.5
            if best[i] + cost < best[j]:
                best[j], back[j] = best[i] + cost, i
    out, j = [], n
    while j > 0:
        out.append(words[back[j]:j])
        j = back[j]
    out.reverse()
    caps = []
    for i, grp in enumerate(out):
        end = out[i + 1][0][1] if i + 1 < len(out) else grp[-1][2] + 0.45
        caps.append(Caption(grp[0][1], end, grp))
    return caps


def finalize_captions(caps):
    """Across lines: never overlap; consecutive captions that touch swap instantly (no dip/fade)."""
    caps.sort(key=lambda c: c.start)
    for a, b in zip(caps, caps[1:]):
        if a.end > b.start - 0.02:
            a.end = b.start - 0.02
        if b.start - a.end < 0.12:
            a.chained_out = True
            b.chained_in = True
    return caps


def sfx_events(sfx_list, cues):
    """Resolve [(line_id, word|None, effect, gain, offset)] to [(time, effect, gain)]."""
    out = []
    for line_id, word, name, gain, off in sfx_list:
        cue = cues[line_id]
        t = cue.word(word) if word else cue.start
        out.append((t + off, name, gain))
    return out
