---
name: new-episode
description: Turn the owner's idea into a finished TeenyTinyology episode (facts → script → storyboard → render → upload pack), with approval gates. Use when the owner describes a story idea or asks for a new video/episode.
---

# New TeenyTinyology episode

Read `CLAUDE.md` first — it holds the locked decisions (voice, music, cast, format, rules).
Then read `docs/judge-lessons.md` — mistakes earlier episodes made; design this one so the judge can't catch them again.

## 0. Set up
- Pick the next number: `episodes/NNN-short-slug/` (lowercase, hyphens). Python package name: `eNNN_slug`
  (create `episodes/eNNN_slug/` with `__init__.py`; keep `idea.md`, `facts.md` beside the code).
- Copy the structure of the most recent episode's `episode.py` as the starting point — reuse its helpers.

## 1. Idea → facts (`idea.md`, `facts.md`)
- Restate the idea in 3–5 beats. Identify which cast members appear; propose new characters only if needed
  (then run the `new-character` skill first).
- Research every claim. `facts.md` lists each fact with a source URL. Prefer university, museum, government,
  veterinary and peer-reviewed sources. Flag anything uncertain.

## 2. Script (`script.py`) — **owner approves before animating**
- `SCRIPT = [Line(id, text, pause), ...]` (`engine.voice.Line`). Hook in the first line, ~140–150 wpm,
  one idea per line, explicit pauses (see CLAUDE.md narration rules).
- Show the owner the script as plain text with the beat each line belongs to. Wait for approval/edits.

## 2b. Narration preview — **owner approves by ear before any visuals**
- Add the episode's sound effects to `SFX` in `script.py` (word-anchored) — sounds are never spoken by the narrator.
- `python -m engine.preview episodes.<pkg>.script <out.mp3>` renders narration + theme + all sound effects.
- Copy the MP3 to the T3 workspace, show the script text next to it, and iterate on wording/pauses until approved.

## 3. Voice + timing
- `narrate(SCRIPT, cache_dir)` → voice track, cues (word timestamps) and captions. Audio is cached by text,
  so only changed lines cost ElevenLabs credits.
- Derive every scene start/end and every SFX time from `cues[...]` — never hard-code seconds that the voice owns.

## 4. Look frames — **owner approves backgrounds / characters / text before the full render**
- Render ~10 full-resolution frames (one per scene: teaser, each setting, key moments, end card) plus an overview
  sheet into the T3 workspace (`<episode>/look_frames/`). Check them against the UI/UX rules first.
- Wait for the owner's feedback on backgrounds, characters, fonts, bubbles and layout; iterate on frames (cheap)
  rather than on rendered video (slow).

## 4b. Storyboard (internal)
- Build the scenes in `episode.py`, render stills (one or two per scene) for the requested style(s) and a contact sheet.
- Self-review against the quality checklist, fix, then copy the sheet to the T3 workspace and show it.

## 5. Score + mix
- `music.score(duration, moods)` with a mood per story beat (`sleepy`, `cozy`, `curious`, `mystery`, `playful`,
  `wonder`, `finale`, `quiet`).
- SFX on a `Bus`, timed to word cues. `mix.mixdown` ducks music under the voice; `mix.loudnorm` → −14 LUFS.

## 6. Render + QA
- Render the MP4 (narrated) and, if asked, a music-only version. Sample frames from the encoded file and check
  every scene; measure loudness. Fix and re-render as needed.

## 6b. Judge — independent critique before the owner sees it
- Run the `video-judge` agent (`.claude/agents/video-judge.md`) on the rendered MP4. It builds its own review packet
  with `python -m engine.judge_kit episodes.<pkg> <mp4>` and returns a ranked critique + fact-check table.
- Save the full report as `episodes/<pkg>/judge_reports/passN.md` (N = 1, 2, …).
- Fix every "Must fix", consider the "Should fix" items, re-render, and include a short summary of the verdict when
  presenting the episode to the owner.
- **Learn from it:** add each new, generalisable lesson to `docs/judge-lessons.md` (cite the episode + pass). If the
  judge caught something already listed there, mark it **(repeat)** and turn it into an engine default or a check.

## 7. Upload pack (`out/`)
- `NNN-slug.mp4`, `cover.png` (best frame + title), `post.md`: title (< 60 chars), description with 2–3 sentence
  summary + sources, 3–6 hashtags (#TeenyTinyology #ScienceForKids …).
- Copy the deliverables to the T3 workspace folder and report paths, length, loudness, and anything unverified.
