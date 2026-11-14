# Judge lessons: what the video-judge keeps catching

A running list of lessons from every judge pass, written as general rules for **future** episodes.
Read it before writing a script (step 2), before the look frames (step 4) and before rendering (step 6).
After every judge pass: save the full report in `episodes/<ep>/judge_reports/passN.md`, then add or strengthen
lessons here (cite the episode). When a lesson is caught a second time, mark it **(repeat)**. It should
probably become an engine default or a checklist item.

## Now automatic (`python -m engine.ep check <ep>`, runs after every render)
`engine/checks.py` catches these lessons by itself. They are still listed below so the reasons stay on record.
A failing check cites its lesson. When a new lesson can be measured, add a check rather than another paragraph,
and plant the mistake in a tiny timeline to prove the check catches it.

| Lesson below | Check |
|---|---|
| Never say a sound; SFX anchored to words in the line | script · spoken sound, sfx |
| ElevenLabs stray sound (voice QA must be empty) | script · voice QA |
| Hooks and closing lines must survive the host list | script · absolute claim (WARN: re-read facts.md hedges) |
| Introduce characters as "This is <Name>." | script · intro |
| Assert the timeline has no holes | timeline · hole |
| A transition needs an overlap or it is a cut | timeline · transition |
| End card readable for at least 4 s | timeline · end card |
| Frame 0 must not be black | timeline / layout / mp4 · frame 0 |
| No caption < 0.9 s; no weak line endings; no one-word orphans | timeline · caption |
| Safe zones; nothing under the app UI | layout · app UI (ERROR), safe zone (WARN) |
| No caption overlapping a label; top labels vs the watermark; tag/label collisions | layout · on caption, on watermark, overlap |
| A label beside a caption needs about 2 s | layout · label time |
| On-screen labels must not repeat the caption | layout · echo (labels only; name tags are exempt) |
| Draw labels after `c.restore()` | layout · zoomed label |
| Labels ≥ 34 px | layout · text size |
| A camera must never show past its background | layout · black edge |
| Black frames; frozen > 2 s (captions + badge masked; the still end card is exempt) | layout / mp4 · black frame, frozen |
| Judge a scene against the episode's own baseline | layout · still scene |
| Loudness, true peak, sample peak, silence | mp4 · loudness, true peak, clipping, silence |
| Format (1080×1920, 30 fps, H.264 + AAC); an MP4 older than the code | mp4 · format, stale |

Not automatic (still the judge's and your job): facts, anatomy, "every narrated verb has a visual payoff", a tag
pointing at the wrong thing, faces under the caption band, scale consistency, story clarity.
The per-episode `verify.py` scripts in e002/e004 are superseded by `engine.checks`.

## Story & script
- **Hook in the first 2 s.** Open on a teaser frame with the episode's big question on screen before the narrator
  starts (e001 pass 1).
- **Narration about mystery should be a question, not a flat statement.** "How the worm pulls this off… scientists
  are still figuring out" was flat. A question with a hedged answer works better (owner, e001).
- **Name the exact species when a story follows one life cycle.** A group name ("horsehair worm", "flea",
  "tapeworm") covers many species with different hosts and cycles. Put the scientific name (italic) on the end
  card, and record in `facts.md` which species the story follows (owner, e001: the end card said "horsehair worm";
  it is *Paragordius varius*). The judge missed this, so check it explicitly.
- **Hedge open science honestly.** "Scientists think so… but how is still a mystery" is fine. Never state a
  hypothesis as settled (e001 pass 1: an overstated claim had to be reworded).
- **Every narrated beat needs a visual payoff** **(repeat ×6: e001 pass 2, l001 pass 1, e003 pass 1 twice, e004 pass 1, e005 pass 1 three times)**. e005: "holds on with a crown of hooks" over a head floating in open gut (now sunk among villi drawn IN FRONT of the crown, with a tug on "hooks"/"suckers"); "the oldest ones break off" while the tail was off frame (now the body ends inside the frame and the last two segments pop free on "break"); "swallows Pip" with no swallow (now eyes shut, chin dip on the gulp, a lip lick). Verbs of action (holds, breaks, swallows, hatches) are the ones that go missing: list every verb in the script and name the frame that shows it.
  e004: the "a sac" tag was placed *at* the sac's own coordinates, so the sac grew out behind its own name tag.
  A tag's pointer tip goes at the thing; the bubble must not sit on it. When the thing is the beat, use
  `pointer=False` and put the bubble beside it, and make the sub-line add a fact the caption does not say.
  e003: "the heart is just a stop" played over nothing (Dilly was drawn *under* the heart), and "Poppy doesn't
  inject her" had no Dilly on screen at all. Root cause both times: drawing order and late entrances, not the
  idea. Engine fix: `biscuit.draw_chest` now draws the worm callback last. Check: for each line, name the thing
  the viewer should see move on its key word, then scrub to that word. If the narrator says
  "until she finds the water", start her far away from the water (e001). On a whiteboard: when the narrator states a
  rule ("split in two directions, and you get…"), draw the rule, not just its result (l001: "1 way / 2 ways / 3 ways"
  tags; a dividing cell). Before rendering, list every line whose time on screen adds nothing new to the board.
- **An etymology must fit the history, not just the mechanism** (l002 pass 1). "That loop is the 'auto' in
  autoinducer" sounded right and was false: "autoinduction" was named in 1970 because the cells make their own
  inducer; the *luxI* feedback loop was found in the 1980s. A name can't come from a mechanism discovered after it.
  facts.md had marked it "confirmed" from sources that only supported the loop. Check every "that's why it's called…"
  against a source about the *naming*, with its date.
- **Closing summaries are claims too.** "All of them, single cells" was false for one item in its own list
  (*Streptomyces* threads, l001 pass 1). Re-check every word of the recap against facts.md.
- **An absolute "never" is true only from the moment it becomes true** (e004 pass 1). "He'll never shed his shell
  again" was said at infection; the crab keeps moulting (and changes shape) for months until the sac emerges, and
  only then stops. Place each "never / no more" line at the point in the story where it starts to hold, and check
  the order of the beats against the timeline in facts.md, not just each claim on its own.
- **Hooks and closing lines must survive the host list on Wikipedia** **(repeat of the l001 "absolute claim" lesson:
  e003 pass 1)**. "This worm can't grow up without a dog" was the owner-approved hook, and false: coyotes, foxes and
  wolves are normal hosts, cats occasional. The same overstatement sat in the thumbnail label and the closing line,
  and the episode's own facts.md already said "dogs are her main home". Re-voicing cost two lines and one more
  owner approval. **Checklist item before the narration preview:** read every can't / only / always / never /
  needs in the hook, the thumbnail text and the closing line against the hedge column of facts.md. Describe the
  story's own animal ("grows up inside two animals: a dog… and a mosquito") instead of a rule for the species.
- **An absolute opening claim and a later exception must meet on screen** (l001 pass 3). "Every bacterium is a
  single cell" plus a later "threads of many cells" label reads as a contradiction unless the label says
  "exception". Better: soften the opening ("almost every").
- **Name every example, or say why you can't.** In a list of examples, one unnamed item stands out: the owner
  asked why the star-shaped bacterium alone had no name (l001). It had been renamed (*Stella* to *Allostella*,
  2025) and we had quietly dropped the name. Use the current name and keep the old one in a note, since that is
  what viewers search for.
- **A board note must mean something to a viewer.** "(not to scale!)" is a note to ourselves; "really thousands of
  times bigger" is the fact it stands for (owner, l001).
- **Board labels are shorter than the narration, so they lose qualifiers** **(repeat ×3: l001 passes 1–3: "more
  surface", "strongest glue", "a third of Europe")**. "small = more surface" dropped "per
  volume" and became false (l001 pass 1). Check each label as a stand-alone claim.
- **Define every term at first use, on the board if the script doesn't** (l001 pass 1: flagella, archaeon).
- **On a big board, draw in sentence order.** When the narrator names a thing before describing its shape
  ("A vibrio is a curved rod"), write the label first. Otherwise the label waits behind the drawing and lands
  seconds late (l001: up to 10 s) **(repeat ×3: l001 passes 1–3)**. Check with the lag test: board item start minus
  its cue word, and run it over the whole lesson, not just the start and end (mid-lesson stills of 6–10 s, pass 3).
- **On-screen tags must add information, not repeat the caption** (e001 pass 2: the tag "like Pixie once was"
  repeated the caption) **(repeat: e004 pass 2, ~15 labels)**. A label written as "the key words of the line" is an
  echo by construction; write each label as the one fact the line did *not* say, or leave the line alone.

## Narration audio
- **ElevenLabs clips carry stray sound at their edges** (l001 preview, owner: "cut midway", "missed heartbeats", "a
  sound like he is going to speak"). With neighbouring lines sent as context, a clip often ends with 0.5–0.9 s of
  silence and then the first ~50 ms of the NEXT sentence, cut hard. Some start with the previous sentence's tail.
  Now an engine default: `voice.clean` strips edge fragments, caps silences inside a line at 0.6 s, fades the edges,
  and writes lines that still sound wrong to `voice_cache/qa.json`. Re-take those before the owner listens.
- **ffmpeg `loudnorm` silently stops being linear** when the gain would push peaks past its true-peak limit. It then
  compresses dynamically, lifting quiet parts: the l001 jingle came out at the voice's level, whatever gain it was
  given (l001 pass 1). Lessons now use `mix.normalize_linear`: one gain plus a soft limiter on the few peaks. The
  Shorts still go through `mix.loudnorm`, so check their quiet passages after the next render.
- **Long narrations go to the owner in batches** (`engine.preview ... --batches`), one per section, with a
  timestamped line list. Nobody can review six minutes in one pass.

## Audio (engine defaults and checks)
- **`mix.mixdown` padded the ducking curve with zeros.** The music is multiplied by a curve derived from
  the voice; `fit()` pads with 0.0, so any stretch where the picture outlasts the narration — i.e. every
  end card — had its music multiplied by zero. e002 shipped 2.0 s of *absolute digital silence* under its
  end card before this was found. Now padded with 1.0 (engine fix, e002 judge pass 2).
- **Measure true peak and sample peak, not just LUFS.** e002 passed at −14.0 LUFS while carrying a
  **+1.97 dBFS** clip from one sound cue stacking on the voice. Loudness normalisation does not remove it.
  Decode to f32 and assert `max|x| <= 1.0` and peak ≤ −1.5 dBFS.
- **Check for silence explicitly.** Decode and assert no window ≥ 0.75 s has RMS < −60 dB. A silent tail
  under a still end card is the Shorts loop point.
- **One loud cue can clip the whole mix.** Keep SFX gains low where they land on a stressed word under the
  voice; e002's `click` at 0.13 had to come down to 0.07.

## Facts against what viewers will check
- **Viewers check Wikipedia, so facts must survive it** (owner, l001: Wikipedia dates the Black Death 1346–1353; we
  said "1347 to 1351" from peer-reviewed sources). Where reliable sources disagree, write what is true under all of
  them: "mid-1300s", "at least a third", "the 1890s", "thought to kill" for estimates. An adversarial fact audit
  before the final render found 12 such fragile claims that five judge passes had accepted.

- **A colour that means one thing across the board must mean it in every region** (l002 pass 1). Gold dots were
  the signal in five regions and cholera toxin in one, so that region showed "few cells: lots of dots, many: none",
  the opposite of the lesson. Before drawing a region, list the throughline symbols and their meaning; a new thing
  gets a new mark.
- **Draw fills before the outlines they sit under** (l002 pass 2). A gold hatch drawn after blue cells tinted them
  slate grey, the colour that meant "dark, alone" elsewhere on the board. Hatch the area first, then the cells.
- **A re-voiced line that gets longer needs new board content** (l002 pass 2, repeat of "a fix is checked like new
  work"). Correcting b9 added 3 s and left 8.6 s with a still board. After any re-voice, re-run the still-stretch check.
- **The thumbnail must not contradict the lesson** (l002, own QA). "How bacteria COUNT themselves" for a lesson whose
  point is "they don't count heads". Read the thumbnail text against the misconception step.
- **Re-check the cue order after inserting an item** (l002 pass 1 fixes). A new underline cued to a later line was
  queued before two earlier labels and held them back 10 s. Run the lag test after every fix pass.

## Science in the pictures
- **Check each insect's resting posture, not just its anatomy.** Mayflies rest with their wings *upright*, pressed
  together over the back (e001 pass 2). Look up a photo of the resting pose for every new character.
- **Exits and entrances happen where they really do.** The worm leaves through the tip of the abdomen,
  underwater, not out of the back (e001 pass 1).
- **Keep scale consistent across scenes.** If a diagram says "several times longer", every later shot must show
  that length (e001 pass 2). Larvae are tiny; draw them at true relative scale (e001 pass 1).
- **Background props are rulers too** **(repeat of true relative scale: e003 pass 1; repeat e005 pass 1 twice)**. e005: a 30 cm ruler drawn inside the magnified gut made the gut ~35 cm wide (a cat's is ~1 cm): a size comparison goes on a card of its own, never inside a magnified setting. And egg packets drawn 1/7 of the larva and 4x the crumbs reversed real sizes (120-200 µm vs a 2-5 mm larva): keep one hero item with a glint instead of drawing everything big. Red blood cells drawn at
  one size in every blood shot made the babies 1/7 of their mother's length and as thick as her, made the foot-long
  adult thinner than one cell, and made the young adult shorter than the babies. Set the prop's size per shot from
  the subject's real size: a red cell is about as wide as a microfilaria and a speck next to an adult worm.
  Engine default now: `bg.blood_cells(rad=...)`. Keep the cute close-ups inside a lens, where a new scale is
  obvious. And when the props shrink, the shot loses motion: give it a camera move (e003, motion scan).
- **Show consequences on the body.** After a parasite leaves, the host looks emptier (e001 pass 2).
- **Tiny key actions need a close-up.** A 25 px swallow reads as nothing on a phone. Zoom in or exaggerate
  (e001 pass 2).

## Drawing bugs that only show at some parameter values
*(found in e002's own storyboard pass, before the judge — the same class of error will recur)*
- **Never size an interior shape for the extreme pose and rely on another shape to cover the excess.**
  Mango's mouth cavity was drawn deep enough to sit behind a fully-dropped jaw, so at every smaller gape
  the uncovered part hung outside her head as a dark smear (e002). It read as a shadow, and two rounds of
  hunting `st.shadow` went nowhere. Build the shape **from** the live parameter instead — the cavity is now
  the wedge between the two biting edges at the current jaw angle, so it cannot leak at any value.
- **Never hide a growing thing with a mask rectangle** (e004 pass 1: the needle "pushed in" by sliding a
  shell-coloured rectangle down over it; once in, the rectangle sat inside the crab as a green pillar for 6 s).
  Draw the thing to its current length from the live parameter instead.
- **Never stride an outline polyline.** Dilly's ink line used every 5th point, so it cut straight chords across
  tight bends and the long worm looked faceted (e003 pass 1). Draw outlines through every point.
- **Paint occlusion before the occupant, never after.** The throat vignette inside Mango's mouth was painted
  after the `inside()` callback, so it dimmed the parasite in the one shot the whole episode is built around
  (e002). Anything that darkens a cavity goes down first.
- **A character scaled to fill its container reads as texture, not an animal.** Roly at full gape width
  became a striped wall with eyes at the bottom (e002). Leave margin on all four sides so the silhouette
  still reads.
- **Ground shadows need ground.** `st.shadow` under a swimming fish is a grey smudge that never connects
  (owner, e002). Characters in open water or in flight get no contact shadow; characters resting on a
  surface do.
- **A head drawn as a separate outlined shape reads as a mask.** Roly's cephalon is immersed in her first
  body segment, so the head-on view is one continuous silhouette with a suture line, not a face plate stuck
  on the front (e002). Check what is anatomically continuous before splitting a drawing into parts.
- **Foreshorten a body seen end-on.** Drawn at its true length, a head-on isopod is a tall cone; it needs a
  `tilt` that says how far above it the camera sits (e002).

- **Build animals that move on a structure, not out of stacked ovals** (owner, e005 Mochi). A body made of separately
  outlined ellipses (torso, chest, neck stroke, head) looked like "a pile of lumps", and every pose that moved the
  head exposed a bulge or a floating head; three patch rounds failed. Fix: a rig (anchor points for neck root, head,
  legs, tail) whose body parts are drawn as one `Style.silhouette`, and a head that turns by yaw (face morphs 3/4 →
  front → 3/4) instead of a squashed `scale(fx)`. Check every new pose in a short motion test, not only stills.

## Animation & polish
- **One setting, one camera** (owner, e004 v1: "a lot of scenes put together, not smooth"). Each scene had its own
  `framed(...)` with its own zoom and focus, so every scene boundary re-framed the same crab and read as a jump even
  with nothing moving in the story. Drive the camera from a keyframe list for the whole setting (`cam_at(t)` in e004)
  and let scenes only change what is drawn; then boundaries can be plain cuts. Keep the character where he is
  (Kiwi stays on the rock after the launch instead of jumping home). Measure it: mean grey change per 0.1 s on the
  encoded file, captions masked, and list the biggest steps; anything that is not a planned transition is a jump.
- **A transition needs an overlap or it is a cut.** `render_frame` draws the first live scene plainly; an iris or fade
  only plays while the previous scene is still live, so extend the previous scene's end by `trans_dur` (e004:
  both irises and the end-card fade were silently cuts).
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
- **A dark wash with a caption on it reads as a rendering glitch**, the same way a grey dim does. e002's
  sex-change beat darkened the frame and wrote "forward, into the mouth" over it; it looked like a fault.
  Move the character instead and let a normal label carry the words.
- **Time-passing effects must read as intentional.** A grey dim looks like a glitch. Use a moon, stars and a blue
  cast, or skip the effect (e001 pass 2). Tint with cairo `OPERATOR_MULTIPLY` (blue), not a semi-transparent
  dark paint (which turns grey).
- **Don't hold a still frame > 5 s** **(repeat ×3: e001 pass 2, l001 pass 1 and pass 2)**. Add a slow push-in or a
  small idle motion (e001). On a lesson's final zoom-out, give every recap word and the teaser something new on the
  board: light up each region as it is named, underline, draw the teaser (l001). **Checklist item:** before
  rendering, list the stretches where nothing new appears on the board (board item starts, camera moves, erasers)
  and fix every one over 5 s at the start or end of a lesson.
- **A fix is checked like new work** **(repeat ×6: e003 pass 2, e004 passes 2 and 3, e005 passes 2 and 3)**. e005 pass 3: lengthening a label window (to reach 2 s) parked it on the worm's tail exactly when the segments broke off. When you extend a label, re-scrub its new END against the camera framing at that moment, not just its start. e005: sinking Noodle's head among villi (to show her grip) put her face behind the caption bubble in every wide shot and gave the new foreground villi flat rectangular bottoms. **Check after moving a character:** scrub the whole setting and make sure its face stays out of the caption band (y 1340–1460 screen) in every frame; foreground props run off the background or fade out, never end in a straight edge. e004: the pass-1 push-in carried a
  label off the frame; the pass-2 parked label then collided with a tag that still drifted with the camera. After a
  fix, re-scrub the whole window the fix lives in, with every other moving element in it, not just the fixed item. e003 moved two labels away from the badge but kept
  their 0.8 s windows, and a new "heart" tag covered the very worm the fix was meant to show. After every fix pass,
  re-time what moved and re-scrub the shot it lives in.
- **A label beside a caption needs about 2 s** (e003 pass 2: three labels read for 0.8–1 s) **(repeat ×3: e004, e005 pass 1: five labels 0.6–1.5 s)**. Measure on the MP4. Root cause every time: a window from one word to the next line's start. Run a label from its cue to the NEXT label's cue (chain them), not to the end of its own line.
- **A tag must not appear before its subject is on screen** (e005 pass 1). The "Pip" tag was anchored to the larva's x and clamped to the screen edge while he was still off frame, so for 2 s it pointed at an egg packet. Start the character on screen (or start the tag when he enters), never clamp a pointer onto something else.
- **Draw labels after `c.restore()`** (e003 pass 2). Inside a camera push they grow, drift and can leave the safe zone.
  **(repeat: e004 pass 2)** A label anchored to a *world* point through `cam.screen()` drifts with the push just the
  same: the pass-1 push-in carried "rock barnacles" off the left edge. Park labels at fixed scene coordinates, or clamp
  the anchored centre into x 60+half-width .. 900-half-width.
- **A second character on a travelling wave sweeps across the hero** (e003 pass 2: the male covered Dilly's face at
  the babies beat). Scan the whole window, not one still; draw the newcomer behind the hero. And know which end of a
  path is the head: `along(path, d, L)` puts the head at distance d, i.e. the far end when a worm "grows" along it.
- **A fix is checked like new work** (l001 pass 2). Pass-1 fixes brought in a new overstated label ("strongest
  glue") and late tags (queued after the drawings). Re-run the lag test and re-read every new label against
  facts.md before re-rendering.
- **Night scenes:** dark ink outlines vanish on dark blue. Lighten antennae and outlines at night (e001 pass 2).

## Measuring pacing (checks worth running before the judge)
- **Mask the caption band and the watermark before differencing.** Captions change every ~1.5 s and add
  roughly +0.5 to +1.0 of mean grey change on their own — enough to lift a frozen scene over a fixed
  threshold. e002 reported "no static stretches" while nine of twenty scenes were visually near-dead
  (judge pass 2). Mask y 1300–1500 and the watermark corner, then compare each scene's mean against
  **this episode's own 75th percentile**, flagging below ~0.45×.
- **Scan the encoded MP4 for frozen stretches**, don't eyeball the contact sheet. Sample every 0.5 s,
  downscale to greyscale and take the mean absolute difference between neighbours. e002's first render had
  a **10.5 s** dead stretch on its diagram card that the contact sheet did not make obvious.
- **Judge a scene against this episode's own baseline, not an absolute number.** A live e002 scene moves
  ~5–15 (mean abs grey change per 0.5 s); the diagram card moved ~0.9. The ratio is the signal.
- **But the measure under-reports camera motion on a flat background.** Zooming uniform parchment changes
  almost no pixels, so a card can read as frozen to the metric while visibly growing on screen (e002).
  On a card, confirm by eye across the span; on a painted scene, trust the number.
- **A diagram card needs a big push-in, not a polite one.** 1.0 → 1.17 over 11 s was invisible; 0.94 → 1.40
  with a slow pan reads clearly (e002).
- **Check for black frames too** (mean < 12 and std < 6). It catches both an uncovered timeline and an
  unwanted fade. **Frame 0 must not be black** — it is the thumbnail, so an episode opts out of the
  opening fade with `ctx["fade_in"] = 0`.
- **Assert the timeline has no holes before rendering.** Walk 0 → duration and check every moment has a
  live scene. e002 once lost a `tl.add()` during an edit and rendered **12 s of black** — the run still
  exited 0 and still reported −14 LUFS, so nothing downstream caught it.
- **Clear the stills folder before each run.** Stale frames get swept into the contact sheet and look like
  a timing bug (e002, cost a debugging cycle).

## Labels and tags (they outlive their qualifiers)
- **A label must not state what the episode's own `facts.md` forbids.** e002's `facts.md` says in writing
  that "back on the gills" is safe but "he never left the gills" is not, because males are recorded in the
  mouth in copula — and the episode then shipped the label **"he never moves in"** (judge pass 2). Before
  writing a label, re-read the hedge section, not just the fact rows.
- **A label must not restate the authors' hypothesis as observation.** "Mango had been using her as a
  tongue" is the hypothesis; the evidence is the abrasion. The narration hedged and the label did not.
- **Two places in one frame need to be drawn as two places.** The owner wanted the brooding female and the
  male visible together; drawing both inside the gill chamber read as "they both live on the gills" and
  contradicted an earlier beat. An inset with its own label fixed it (e002).
- **On-screen counters are claims, and they must not tick through fast transport** (e003 pass 1). A "day 56 → 70"
  counter running while she rode the bloodstream implied a two-week float, and "day 70" at the heart sat outside
  Wikipedia's 75–120 days. Freeze counters when the action is quick, and show the hedged range ("about 3 months
  after the bite") on arrival.
- **Top labels collide with the watermark** (e003 pass 1: three labels within 2–8 px of the badge). Labels centred
  at x 480 that are wider than ~600 px reach the badge's x range (60–164). Keep top labels at rendered y ≥ 370, or
  centre wide ones at x 540.
- **If a line asks the viewer to count, the pose must let them.** "Fourteen hooked feet / seven pairs" over
  a head-on pose where only four legs a side cleared the silhouette (e002). Rear pereopods are the longest,
  so they should reach past the body even foreshortened.

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
- **End card:** arrows must not touch labels, and the card stays fully readable for at least 4 s (e001 pass 2)
  **(repeat: e003 pass 1, 2.5 s)**. When the card follows the last line, `DUR = end + ~4.9` and bring the plate
  in within 0.7 s of the card.
- **A camera must never show past its background** (e003, own QA). A `Cam` whose focus point is not its screen
  point at z ≈ 1 slid the meadow sideways and showed black strips. e003's `framed()` clamps the focus so the
  frame stays on the painted background; scan every 0.25 s for black edge columns before rendering.
- **Owner on sounds (e003):** the cartoon `buzz` (square wave) is not a mosquito. Use `sfx.whine` (wingbeat tone,
  fly-by). `purr` belongs to cats (Mochi); don't put it on a dog. Footsteps don't go on legless animals.

- **Slow drifts on a cached bitmap tick.** A very slow zoom or push (e.g. 0.94→1.12 over 5 s) on a cached background
  surface steps visibly at 30 fps ("moving in ticks", owner, E004). Either hold the camera still, or move fast enough
  that the step per frame is well over a pixel. Never drift a static card.
