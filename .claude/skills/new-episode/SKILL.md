---
name: new-episode
description: Turn the owner's idea into a finished TeenyTinyology episode (facts → script → storyboard → render → upload pack), with approval gates. Use when the owner describes a story idea or asks for a new video/episode.
---

# New TeenyTinyology episode

Read `CLAUDE.md` first — it holds the locked decisions (voice, music, cast, format, rules).
Then read `docs/judge-lessons.md` — mistakes earlier episodes made; design this one so the judge can't catch them again.
Every stage has a command: `python -m engine.ep <cmd> <ep>` (see CLAUDE.md). `python -m engine.ep status <ep>` says
where the episode is and what comes next. Record each owner approval with `engine.ep approve`.

**Review loop (every gate):** put the files in `for-review/<pkg>/<stage folder>/` and send the review-page link
(`python -m engine.ep review`, then `http://localhost:8765/#e006/2_narration`). Before the next round, read
`python -m engine.ep feedback <pkg>`, fix each comment, and close it with `engine.ep resolve <pkg> <id> "what was done"`.
The owner approves gates with the page's Approve buttons (or tells you; then run `engine.ep approve`). Confirm with
`engine.ep status <pkg>` before moving past a gate.

**Started from the review page (headless run):** the owner may start this skill with the page's New idea / Continue
buttons instead of the chat. Then nobody can answer questions mid-run: do the work up to the next owner gate and stop
(a new idea stops at the first gate: the script), make decisions you would normally ask about
yourself and flag them in the note, and end with a short plain-language note to the owner (≤ 6 sentences, no code):
what was done, which review-page tab to look at, any question. Never commit.

## 0. Set up
- `python -m engine.ep new <N> <slug>` creates `episodes/eNNN_slug/` (idea.md, facts.md, script.py templates) and
  the `for-review/eNNN_slug/` stage folders.
- When the script is approved, copy the most recent episode's `episode.py` as the starting point. Shared helpers
  (cameras incl. `keyed_cam`, `lens`, `brand_plate`, `blinking`, `drift`, `along`, `episode_audio`, …) come from
  `engine/kit.py`. Never import from another episode; move a reused helper into `engine/kit.py` instead.

## 1. Idea → facts (`idea.md`, `facts.md`)
- Restate the idea in 3–5 beats. Identify which cast members appear; propose new characters only if needed
  (then run the `new-character` skill first).
- Research every claim. `facts.md` lists each fact with a source URL. Prefer university, museum, government,
  veterinary and peer-reviewed sources. Flag anything uncertain.

## 2. Script (`script.py`) — **owner approves before animating**
- `SCRIPT = [Line(id, text, pause), ...]` (`engine.voice.Line`). Hook in the first line, ~140–150 wpm,
  one idea per line, explicit pauses (see CLAUDE.md narration rules).
- Show the owner the script as plain text with the beat each line belongs to. Wait for approval/edits, then
  `engine.ep approve <ep> script`.

## 2b. Narration preview — **owner approves by ear before any visuals**
- Add the episode's sound effects to `SFX` in `script.py` (word-anchored) — sounds are never spoken by the narrator.
- `python -m engine.ep preview <ep>` renders narration + theme + all sound effects into
  `for-review/<pkg>/2_narration/eNNN_narration_vN.mp3` (next version number) and runs the script checks (sound words
  spoken, SFX anchors, voice QA, absolute words in the hook / closing line, intros, pace). Fix every ERROR before
  sending; `voice_cache/qa.json` must be empty (flagged lines get a new `take`).
- Show the script text next to the MP3 and iterate on wording/pauses until approved, then `engine.ep approve <ep> narration`.

## 3. Voice + timing
- `narrate(SCRIPT, cache_dir)` → voice track, cues (word timestamps) and captions. Audio is cached by text,
  so only changed lines cost ElevenLabs credits.
- Derive every scene start/end and every SFX time from `cues[...]` — never hard-code seconds that the voice owns.

## 4. Look frames — **owner approves backgrounds / characters / text before the full render**
- Define `LOOK` / `look_times(Q)` in episode.py, then `engine.ep look <ep>` renders ~10–20 full-resolution frames
  (teaser, each setting, key moments, end card) plus an overview into `for-review/<pkg>/3_look_frames/`.
  Run `engine.ep check <ep> --only timeline,layout` first and check the frames against the UI/UX rules.
- Wait for the owner's feedback on backgrounds, characters, fonts, bubbles and layout; iterate on frames (cheap)
  rather than on rendered video (slow). Then `engine.ep approve <ep> look`.

## 4b. Storyboard (internal)
- Build the scenes in `episode.py`, render stills (one or two per scene) for the requested style(s) and a contact sheet.
- Self-review against the quality checklist, fix, then copy the sheet to `for-review/` and show it.

## 5. Score + mix
- `make_audio = kit.episode_audio(DUR, Q, SCRIPT, SFX, track, moods)` with a mood per story beat (`sleepy`, `cozy`,
  `curious`, `mystery`, `playful`, `wonder`, `finale`, `quiet`). It places every word-anchored SFX and silent beat
  exactly as in the preview, ducks the music under the voice and normalises to −14 LUFS.

## 6. Render + QA
- `engine.ep render <ep>` renders the MP4, writes the QA sheet from the encoded file and runs **all** automatic
  checks (`review/checks.md`). Fix every ERROR and read every WARN before the judge sees it; re-run with
  `engine.ep check <ep>` (add `--only script,timeline` for a fast pass while iterating).

## 6b. Judge — independent critique before the owner sees it
- Run the `video-judge` agent (`.claude/agents/video-judge.md`) on the rendered MP4. It builds its own review packet
  with `python -m engine.judge_kit episodes.<pkg> <mp4>` (includes checks.md) and returns a ranked critique +
  fact-check table.
- Save the full report as `episodes/<pkg>/judge_reports/passN.md` (N = 1, 2, …).
- Fix every "Must fix", consider the "Should fix" items, re-render, and include a short summary of the verdict when
  presenting the episode to the owner.
- **Learn from it:** add each new, generalisable lesson to `docs/judge-lessons.md` (cite the episode + pass). If the
  judge caught something already listed there, mark it **(repeat)** and turn it into an engine default or a check
  in `engine/checks.py` (plant the mistake in a tiny timeline to prove the check catches it).

## 7. Upload pack (`out/`)
- `NNN-slug.mp4`, `cover.png` (best frame + title), `post.md`: title (< 60 chars), description with 2–3 sentence
  summary + sources, 3–6 hashtags (#TeenyTinyology #ScienceForKids …).
- `engine.ep final <ep>` copies the deliverables to `for-review/<pkg>/4_final/`; report paths, length, loudness,
  the checks summary, and anything unverified. After the owner signs off: `engine.ep approve <ep> final`.
