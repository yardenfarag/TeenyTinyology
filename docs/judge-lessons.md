# Judge lessons: what the video-judge keeps catching

A running list of lessons from every judge pass, written as general rules for **future** episodes.
Read it before writing a script (step 2), before the look frames (step 4) and before rendering (step 6).
After every judge pass: save the full report in `episodes/<ep>/judge_reports/passN.md`, then add or strengthen
lessons here (cite the episode). When a lesson is caught a second time, mark it **(repeat)**. It should
probably become an engine default or a checklist item.

## Story & script
- **Hook in the first 2 s.** Open on a teaser frame with the episode's big question on screen before the narrator
  starts (e001 pass 1).
- **Narration about mystery should be a question, not a flat statement.** "How the worm pulls this off… scientists
  are still figuring out" was flat. A question with a hedged answer works better (owner, e001).
- **Hedge open science honestly.** "Scientists think so… but how is still a mystery" is fine. Never state a
  hypothesis as settled (e001 pass 1: an overstated claim had to be reworded).
- **Every narrated beat needs a visual payoff.** If the narrator says "until she finds the water", start her far
  away from the water (e001 pass 2).
- **On-screen tags must add information, not repeat the caption** (e001 pass 2: the tag "like Pixie once was"
  repeated the caption).

## Science in the pictures
- **Check each insect's resting posture, not just its anatomy.** Mayflies rest with their wings *upright*, pressed
  together over the back (e001 pass 2). Look up a photo of the resting pose for every new character.
- **Exits and entrances happen where they really do.** The worm leaves through the tip of the abdomen,
  underwater, not out of the back (e001 pass 1).
- **Keep scale consistent across scenes.** If a diagram says "several times longer", every later shot must show
  that length (e001 pass 2). Larvae are tiny; draw them at true relative scale (e001 pass 1).
- **Show consequences on the body.** After a parasite leaves, the host looks emptier (e001 pass 2).
- **Tiny key actions need a close-up.** A 25 px swallow reads as nothing on a phone. Zoom in or exaggerate
  (e001 pass 2).

## Animation & polish
- **The climax needs real animation:** anticipation (crouch), action (leg kick, stretch), an eased arc, a landing
  into the effect. A pose sliding along a path looks flat **(repeat: e001 pass 1 + pass 2)**.
  Root cause in e001: the action had no time. Its window was squeezed between the end of a line and a sound cue, so
  it began before the scene did. **Budget the silence for a big action in the script** (the pause before the
  silent beat). A jump needs ≥ 1.3 s: 0.5 s crouch, 0.8 s airborne. Then check the scene's start and end times
  against the action's start and end. Pickle now has `kick=` (take-off pose).
- **End-card icons are held to the same standard as scenes.** A fix in a character's pose must reach every place
  she is drawn, including the icons (e001 pass 3: flat-winged mayfly icon).
- **Effects respect the medium.** Bubbles only under water, splashes at the waterline (e001 pass 3).
- **Use a cut, not a crossfade, between two shots of the same character at different positions or zoom.** A
  crossfade shows two copies of her (e001 pass 3).
- **Lighting stays continuous within a sequence.** A night jump means a moonlit underwater shot (e001 pass 2).
  Use `bg.underwater(night=True)` for that, plus `pickle.draw(..., night=True)` for pale antennae.
- **Time-passing effects must read as intentional.** A grey dim looks like a glitch. Use a moon, stars and a blue
  cast, or skip the effect (e001 pass 2). Tint with cairo `OPERATOR_MULTIPLY` (blue), not a semi-transparent
  dark paint (which turns grey).
- **Don't hold a still frame > 5 s.** Add a slow push-in or a small idle motion (e001 pass 2).
- **Night scenes:** dark ink outlines vanish on dark blue. Lighten antennae and outlines at night (e001 pass 2).

## UI / UX
- **Captions never overlap, not even for one frame** **(repeat: e001 pass 1 + pass 2)**. Now an engine default:
  `scene.draw_captions` draws exactly one bubble at a time.
- **Captions break at natural phrase boundaries,** never ending a line on a/the/of/to. A one-word orphan
  ("mystery.") should not sit alone on screen (e001 pass 2). Now an engine default: `voice.chunk_captions` picks
  breaks by cost, preferring punctuation and avoiding weak endings and orphans. Where it still splits a phrase
  badly, put `|` in the script text to force a break there. The `|` is never spoken.
- **Centre captions in the safe zone, not the frame.** A line that fits the frame can still run under the app's
  right rail (e001 pass 3). `CAP_X = 480` is the middle of x 60–900.
- **No caption shorter than ~0.9 s on screen.** A 0.4 s bubble reads as a flicker with the sound off (e001 pass 3).
  If you force a break with `|`, check the timing of the piece it creates.
- **Read the full caption list before the look frames.** Print it with `narrate(...)` and check every line.
- **Safe zones:** content in x 60–900, y 200–1460; captions centred at y=1400 (e001 pass 1).
- **End card:** arrows must not touch labels, and the card stays fully readable for at least 4 s (e001 pass 2).
