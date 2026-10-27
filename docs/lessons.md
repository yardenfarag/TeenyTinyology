# TeenyTinyology Lessons — format bible

The second format on the channel: longer landscape whiteboard lessons (3–4 min or more) that **teach** one
microbiology idea, in a "Lessons" playlist. `CLAUDE.md` covers the Shorts; this file covers the Lessons. Where the two
differ, this file wins for Lessons (no music, no captions, no cast, landscape). Shared rules from `CLAUDE.md` still
apply: facts sourced in `facts.md`, narration written for the ear, the owner approves the narration by ear first,
`ELEVENLABS_API_KEY` handling, review files in `for-review/`.
The workflow is the `new-lesson` skill; the critic is the `lesson-judge` agent.

## Decisions (locked unless the owner changes them)
| | |
|---|---|
| Audience | anyone who likes to learn microbiology: real terms, each defined once, never dumbed down |
| Format | 1920×1080 landscape, 30 fps, H.264 + AAC, −14 LUFS (`board.mixdown`); thumbnail 1280×720 (`render.thumbnail`) |
| Look | clean white board (`engine/board.py`); marker text written in sync with the narrator; simple teacher-style marker drawings |
| Tool | the marker alone, no hand (`b.render(c, t, "marker")`) |
| Handwriting | **Gochi Hand** (`board.FONT`) |
| Colours | navy `#1e2a3a` is the "black" marker; blue, red, green for diagrams; brand gold `#f2b84b` for highlights, underlines, fills |
| Sound | **voice only.** No music and no marker sound (two synthesized marker sounds were tried and dropped). The one exception is the logo jingle |
| Opening | the logo intro `b.logo(...)` (~3 s): letters pop in on rising marimba notes, the magnifying-glass "o" swoops in and glints, "Lessons" is written over a soft chord. The jingle sits 4 LU under the voice. Then the hook |
| Ending | the recap over the zoomed-out board (each region lights up as it is named), then the outro: the board fades to a faint background (`b.veil`) and the logo plays again over it, large, with its jingle and `@teenytinyology` written underneath. No "next time" teaser (owner, 2026-10-27) |
| Sections | a section title (`b.title`) with a gold underline. No chapter cards, no YouTube chapter timestamps |
| Questions | the lesson explains; it never asks the viewer to pause, predict or answer |
| Cast | none for now. Bring a character in only when the owner asks |
| Captions | none burned in, no SRT: YouTube auto-subtitles plus the board text |
| Narrator | Miles. Before the pilot's narration preview, ask the owner whether to try other voices |

## The board
- One lesson = one big board (`Board(w=3840, h=2160)` or larger) and a camera (`b.cam.move`, `b.cam.frame`).
  Each section owns a region of the board; the camera travels between regions and zooms out at the end to show the
  whole map. Plan the moves so the frame always holds content: pan straight between neighbouring regions.
- Keep text and key drawings inside x 60–1860, y 60–980 of the frame: YouTube's player controls and progress bar
  cover the bottom when the viewer hovers or pauses.
- The eraser (`b.erase`) clears space for the next idea and leaves a faint ghost, like a real board.
- Board text is key words, not prose: labels sit next to what they label. Narration and writing are tied to word
  cues (`cues[id].word("cocci")`), never hard-coded seconds.

## Teaching
Start every lesson from its **objective**: "after this, you can explain / do X". Design the **final board** first,
as a map of how the ideas connect, then build towards it.

Pick the lesson type (a default, not a cage):
- **Mechanism** (secretion systems, host manipulation): trace cause → effect on one persistent diagram that changes.
- **Categories** (shapes, oxygen needs, protozoa): examples, non-examples, borderline cases side by side.
- **Procedure** (Gram stain): a worked example step by step, then a second case where the result is explained.
- **Story** (vaccine history): a timeline where each event answers "why did this work?"
- **Misconception** (autoimmunity): the common belief → conflicting evidence → replacement explanation.

Rules:
- The hook is the real question the lesson answers, not a word puzzle that later needs repair.
- Connect to what the viewer already knows with a short bridge.
- Each step answers one meaningful question and visibly connects to the previous one.
- Define a term at first use, in context.
- Metaphors are optional; when used, say what maps to what and where the comparison breaks. Fact-check a metaphor
  as carefully as a fact (an early draft compared facultative bacteria to a hybrid car with oxygen as "fuel"; oxygen
  is the final electron acceptor, so the metaphor taught something false).
- Handle a misconception where it arises, always with the replacement explanation.
- Every fact is sourced in `facts.md`, as for the Shorts; when unsure, soften ("scientists think…").

## Humour
**Dark and dry** (owner, 2026-10-26): microbiology is full of bodies, plagues and poisons, and the humour comes from
saying that calmly. A joke lands on a pause plus a visual, and every dark line is a fact sourced in `facts.md`.
- deadpan after the grim fact: a comma-shaped cell "has ended a great many sentences" (*Vibrio cholerae*); the
  deadliest toxin known, "which people now pay to have injected into their faces" (botulinum, Botox)
- understatement ("does not like oxygen" … "oxygen kills it")
- the narrator knows the drawings aren't great ("This is a bacterium. You'll have to trust me.")
- Laugh at the microbes and at history's mistakes, never at patients or victims.
- Cut a joke that only describes the material. "Not the most imaginative names. But you'll never forget them" was
  cut by the owner as "not funny at all": a punchline needs a twist (a reveal, a grim fact said lightly), not a
  comment.

## Topic order (each builds on the last)
1. Bacteria shapes and names (pilot)
2. Gram staining
3. Oxygen and bacteria (aerobes, obligate anaerobes, facultative anaerobes)
4. Toxins and secretion systems
5. Parasites: nematodes, protozoa, ectoparasites, how parasites control their hosts (cross-links Doodle's Short)
6. Immunology arc: history of vaccines, autoimmune diseases

## Status
| | What | Status |
|---|---|---|
| P0 | Bake (`lessons/bake_board`): tool, handwriting, look, sound | done |
| P1 | Board engine: camera, eraser, titles, logo intro + jingle, voice-only mix, thumbnail (demo `lessons/bake_p1`) | done, approved 2026-10-26 |
| P2 | These rules, the `new-lesson` skill, the `lesson-judge` agent + `engine/lesson_kit.py` | done 2026-10-26 |
| P3 | Pilot lesson: **Bacteria shapes and names** (`lessons/l001_bacteria_shapes/`) | next |
