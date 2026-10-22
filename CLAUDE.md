# Teenyology — series bible

Short, calm, cute educational videos (TikTok / YouTube Shorts) about tiny creatures and the animals they live with.
Tagline: *Teeny creatures. Big stories.*

Everything is generated in code: vector art (pycairo), original synthesized music + sound effects (numpy),
narration from ElevenLabs. No stock footage, no sampled audio, no other people's music or characters.

## Decisions (locked unless the owner changes them)
| | |
|---|---|
| Format | 1080×1920, 30 fps, H.264 + AAC, loudness −14 LUFS (true peak −1.5 dB) |
| Length | whatever the narration needs, usually 45–90 s; never squeeze the voice to hit a length |
| Narrator | ElevenLabs **Miles** (`uk7wwhXdWYHKKZ8KTCVw`), model `eleven_multilingual_v2`, speed 1.0 (Remi was tried in ep. 001 and dropped) |
| Music | the **Teenyology theme** (celesta + marimba, 74 BPM, D major) — `engine/audio/music.py`, shaped by moods |
| SFX | `engine/audio/sfx.py` (pop, boing, gulp, slurp, sparkle, whoosh, …) — the owner loves these, use generously but softly |
| Art style | **illustrated** (ink + watercolor, paper grain) — chosen after ep. 001 comparison. Use `--style illustrated` |
| Captions | soft cream one-line bubbles, peach highlight on the spoken word, centre y=1400 (`scene.CAP_Y`) |
| Font | **Nunito** (rounded, SIL OFL) via `engine/text.py` — alternatives on file: Quicksand, Fredoka, Baloo 2 |
| API key | `ELEVENLABS_API_KEY` in `.env` (git-ignored). Never print it, never commit it |

## The cast (permanent names — never rename)
| Name | Species | Look | Personality | File |
|---|---|---|---|---|
| **Mochi** | cat | cream fur, caramel patches, sea-green eyes | sleepy, gentle, a bit vain | `characters/mochi.py` |
| **Pip** | flea (+ larva, cocoon) | amber-brown, chubby | curious, cheeky, springy | `characters/pip.py` |
| **Peanut** | ant | glossy black-brown, big eyes | busy, brave | `characters/peanut.py` |
| **Noodle** | tapeworm (*Dipylidium caninum*) | cream segments, tiny face on the scolex | calm, patient, always hungry | `characters/noodle.py` |
| **Plum** | songbird | plum-purple, peach breast, teal wing tips | cheerful, fussy about feathers | `characters/plum.py` |
| **Pickle** | field cricket (female) | leafy green, olive folded wings, very long antennae, egg-laying spike | calm, careful, a little shy; doesn't chirp (only males do) | `characters/pickle.py` |
| **Pixie** | mayfly (female; + nymph) | pale honey body, brown bands, glassy wings, three tail threads | delicate, dreamy | `characters/pixie.py` |
| **Doodle** | horsehair worm (male) | long glossy dark-brown string, pale head tip, forked tail | quiet, determined traveller | `characters/doodle.py` |

New characters get a short, cute name in the same spirit (Biscuit, Toffee, Bean, Poppy, Button, Kiwi…) and are
added with the `new-character` skill. Every character draws through a `Style` (`engine/style.py`) so it works in all
three looks; the `real` style may switch to anatomically correct drawings and has no cartoon faces.

## Narration rules
- Write for the ear: short sentences, one idea each, ~140–150 words per minute.
- Avoid monotony: vary sentence length, use a hook, a turn ("There's just one problem."), questions, and
  short beats ("Waiting."). Calm documentary tone — never childish ("grew and grew", "secret passenger").
- Never have the narrator *say* a sound (splash, crunch, gulp, pop, buzz, boing…) — the sound effect does it.
  Silent beat: `Line(id, "", pause, sfx="splash")`.
- Every sound effect lives in the script module's `SFX` list, anchored to a word
  (`(line_id, word, effect, gain, offset)`), so the narration preview and the final video sound identical.
- Characters are introduced as "This is <Name>. <She/He>'s a <species>…" (owner preference).
- **The owner approves the narration by ear before any video work** — always send a voice+music preview MP3.
- Each script `Line` is synthesised separately (neighbouring lines passed as context) with an explicit `pause` after it:
  0.4–0.6 s normally, 0.8–1.0 s after a key fact or a joke, 0.3 s inside rhythmic beats ("Itch… lick… gulp!").
- Open with a hook in the first 2 seconds; end with the cycle/tagline. Name characters early and often.
- Facts must be checked against reliable sources and listed in the episode's `facts.md`; when unsure, soften ("scientists think…").
- Captions come from the ElevenLabs word timestamps automatically — never hand-time them.

## UI / UX rules (always — every frame is viewed on a phone, sound often off)
- Safe zones (1080×1920): keep text and key action inside **x 60–900, y 200–1460**. The TikTok/Shorts app covers the
  right rail (x > 930, y 700–1520), the bottom (y > 1520: username, description, progress bar) and the top bar (y < 170).
- Scenes are drawn with `scene.STAGE_LIFT` (170 px up) so characters stand above the captions; backgrounds are taller
  than the frame (`backgrounds.HH`) so nothing runs out at the bottom. Full-screen cards (diagrams) undo the lift.
- Captions: one line, never overlapping each other or a label; they carry the story with the sound off.
- Text UI is soft and gentle: cream bubbles with diffuse shadows (`scene.soft_bubble`, `tag`, `label`), warm dark
  ink, rounded font. No hard borders, no black boxes. Labels ≥ 34 px, captions 50 px.
- Frame 0 is the thumbnail: open on a hook card/teaser, music from the first frame, voice within ~1.5 s.
- Check every new layout with `judge_kit` safe-zone overlays.

## Animation rules ("really cute")
- Everything alive moves: blinking every 2–4 s, breathing, idle sway, antenna wiggle.
- Anticipation before big moves, squash & stretch on landings (`core.squash`), ease everything (`ease`, `back_out`).
- Tie sound effects and motion to word timestamps (`cue.word("gulp")`).
- One clear subject per moment; name-tags (`scene.tag`) the first time a character appears.
- Transitions: 0.45 s crossfade by default, iris into "inside the body" shots.

## Project layout
```
engine/          core.py (math/geometry/text) · style.py (3 looks) · scene.py (timeline, captions, tags)
                 render.py (stills, contact sheets, MP4) · voice.py (ElevenLabs + timing)
                 audio/ music.py (theme) · sfx.py · mix.py (ducking, loudness) · common.py
characters/      one module per cast member + model_sheet.py
episodes/NNN-slug/  idea.md · facts.md · script.py · episode.py · voice_cache/ · review/ · out/
.claude/skills/  new-episode · new-character
tests/           old experiments (not used by episodes)
```

## Commands (run from the project root with the project venv)
```
.venv/Scripts/python -m characters.model_sheet review.png [--only mochi,pip]
.venv/Scripts/python -m episodes.<pkg>.episode stills --style cute        # storyboard stills + contact sheet
.venv/Scripts/python -m episodes.<pkg>.episode render --style cute        # full MP4 (+ music-only variant)
```
The owner reviews files inside the T3 workspace folder (`C:\Users\yarde\.t3\scratch\...`), not inside this repo —
copy review images/videos there when asking for feedback.

## Quality checklist (before showing anything)
1. Contact sheet of the *encoded MP4* (`render.sample_frames`) — every scene, transition and caption checked by eye.
2. No text or key action outside the safe zone; no caption overlapping a label.
3. Characters on-model (compare with `model_sheet`), eyes blink, nothing frozen for > 2 s.
4. Loudness measured (`mix.measure_lufs`) ≈ −14 LUFS; voice clearly above music.
5. Facts re-read against `facts.md`. Report honestly what could not be verified (Claude cannot listen to audio).
6. The `video-judge` agent has reviewed the MP4 and its "Must fix" items are resolved.

## Backlog (owner feedback to address later)
- Mochi: nose and mouth look weird / out of place — redesign the muzzle (placement, size, shape) before Mochi's next episode.
