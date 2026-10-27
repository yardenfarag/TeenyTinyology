---
name: new-lesson
description: Turn a microbiology topic into a finished TeenyTinyology Lesson, the landscape whiteboard video (objective → facts → script → voice preview → board frames → render → judge → upload pack), with owner approval gates. Use when the owner asks for a lesson, a whiteboard video, or a topic to teach.
---

# New TeenyTinyology Lesson

Read `docs/lessons.md` first: the locked decisions, board rules, teaching and humour rules for this format. Then
read `docs/judge-lessons.md` (mistakes earlier videos made) and every report in `lessons/*/judge_reports/`.

Each gate below ends when the owner has approved; show them files through `for-review/` and wait.

## 0. Set up
- Next number: `lessons/lNNN_slug/` (Python package, with `__init__.py`). Files: `plan.md`, `facts.md`,
  `script.py`, `lesson.py`, `voice_cache/`, `judge_reports/`, `out/`.
- `lesson.py` must expose `build() -> (board, voice, cues, duration)` and the commands `stills` and `render`
  (start from `lessons/bake_p1/demo.py` for the board calls and `lessons/bake_board/bake.py` for the voice).

## 1. Objective and board map (`plan.md`) — **owner approves**
- Write the objective ("after this, you can explain / do X"), the lesson type (mechanism, categories, procedure,
  story, misconception) and 4–7 steps, each answering one question.
- Sketch the **final board**: which region of the big board holds each step, what is written and drawn there, and
  the camera route between regions. Done when every step has a region, a title (if it opens a section) and a
  camera move that never crosses empty board.

## 2. Facts (`facts.md`)
- Every claim the narration or the board will make, each with a source URL (university, government,
  peer-reviewed, textbook). Etymologies and metaphors count as claims. Done when no line of the plan rests on an
  unsourced claim; flag anything uncertain to the owner.
- Viewers check Wikipedia. Every date, number and superlative must also hold against Wikipedia and Britannica.
  Where reliable sources disagree (spans, percentages, "first described in"), use wording that is true under all of
  them ("mid-1300s", "at least a third", "the 1890s"). Before the final render, run a separate adversarial fact audit
  of everything said and written (`review/all_claims.md` → `review/fact_audit.md`).

## 3. Script (`script.py`) — **owner approves the text**
- `SCRIPT = [Line(id, text, pause), ...]` (`engine.voice.Line`). Teaching voice: short sentences, one idea per line,
  ~140 wpm, explicit pauses (longer after a key definition or a joke). The hook line comes right after the logo.
- Show the script as plain text grouped by plan step. Before the **pilot's** first preview, ask whether to try
  narrators other than Miles (the narrator lives in `engine/voice.py` `VOICE_ID`).

## 4. Narration preview — **owner approves by ear**
- `.venv/Scripts/python -m engine.preview lessons.<pkg>.script for-review/<pkg>_narration.mp3 --no-music --batches`
  writes one short MP3 per board region plus `<pkg>_narration_batches.md` (timestamped lines). The owner reviews
  batch by batch and points at problems as "b · 0:42". Before sending, `voice_cache/qa.json` must be empty: give
  any line it flags a new `take` and re-run. Cached lines cost nothing; approved takes stay locked.

## 5. Board frames — **owner approves the look**
- Build `lesson.py`: `b = Board(w, h)`, `t = b.logo(...)`, `narrate(SCRIPT, cache, t0=t + 0.4)`, then for each step
  `b.title`, `b.write`, `b.stroke`, `b.hatch`, `b.erase`, `b.cam.move` timed from `cues[id].word(...)`.
- Render `stills` for each step's finished region plus the final zoomed-out board; check the board rules in
  `docs/lessons.md` (frame-safe area, text size ≥ 50 px on screen, labels next to their drawing) before showing.

## 6. Render + QA
- `render` builds the MP4 with `render.encode(..., size=(1920, 1080))` and the sound from
  `board.mixdown(b, voice, dur, wav)` (voice + logo jingle, −14 LUFS).
- `render.sample_frames` on the encoded MP4: every step, eraser and camera move checked by eye; measure loudness.

## 7. Judge
- Run the `lesson-judge` agent on the MP4. Save its report as `lessons/<pkg>/judge_reports/passN.md`.
- Fix every "Must fix", weigh the "Should fix", re-render, and re-run until no "Must fix" remains. Add each new,
  general lesson to `docs/judge-lessons.md` (cite the lesson and pass).

## 8. Upload pack (`out/`)
- `lNNN-slug.mp4`, `thumbnail.png` (1280×720, `render.thumbnail` on the clearest board moment, with the lesson
  title large and legible at small size), `post.md`: title (< 70 chars), a 2–3 sentence description, the sources
  from `facts.md`, 3–6 hashtags including #TeenyTinyology. Copy to `for-review/` and report length, loudness and
  anything unverified.
