# Episode 002 — video-judge, pass 1

**Verdict: not publishable as-is.** Facts 9 · Science visuals 6 · Story clarity 8 · Visual polish 7 ·
UI/UX 6 · Pacing & audio 6 · **Overall 7/10**

> "This is the strongest thing the channel has made… the narration survives an independent read of
> Brusca & Gilligan 1983 almost word for word. But it is not publishable as-is."

## Must fix — all four resolved

| # | Finding | Resolution |
|---|---|---|
| 1 | Label "better than no tongue at all — the scientists' best guess" ran x 8–975: clipped by the left frame edge and into the right-rail zone (safe zone is x 60–900). The one line that makes the ending honest was the one a phone viewer could not read. | Shortened to "the scientists' best guess", size 40, centred on CAP_X. |
| 2 | The brood was released by an adult Roly **free-swimming in open water**, contradicting the next line ("Mango will carry Roly for the rest of her life") and Brusca & Gilligan. A sound-off viewer concludes the adult swims out to breed. Repeat of the lesson *"Exits and entrances happen where they really do."* | `s_hatch` rebuilt: Mango is on screen, the specks stream out past her lips. Roly never leaves. |
| 3 | The manca was drawn at the **pelvic fin** while the narration said "slipped in through Mango's gills" — reads as entering the belly. | `s_arrive` rebuilt: she approaches low and forward, holds just outside the operculum, then slips up under the gill cover. |
| 4 | **14 s of near-dead picture** (45–59 s) across grip → fade → place — the heart of the episode. Mean grey change 0.5–0.9 against a live-scene baseline of 5–12. | One continuous push-in (`mouth_cam`, z 1.0 → 1.38) across the whole sequence, plus a squash on the clamp. |

## Should fix — resolved

- **#5 "Both male" was an unrecorded inference.** Brusca 1981 p. 190: no multiple infestation of two males
  has ever been recorded. The *number* two is sourced; the *simultaneity* was not. → rewritten to
  "Two of them found Mango. Every one of them starts out male." **This was a claim I had asked the judge
  to attack, and it did not survive.**
- **#6** The name tag read "a tongue-eating isopod" — teaching the misnomer the episode exists to correct
  → "a parasitic isopod".
- **#7** End card read as if "spotted rose snapper" were the isopod's common name → "on the spotted rose
  snapper · Gulf of California".
- **#8** "Four hundred specks swim out" silently converted *eggs in the pouch* into *released young*
  (~200 estimated to reach maturity) → "Hundreds of specks swim out."
- **#9** Grooves were a deep scribble across the whole dome; the paper says "**minor abrasion** … on the
  **first two thoracic segments**" → light scuffs on the front two segments only, and the narration
  softened from "had worn grooves into Roly's back" to "had scuffed Roly's back".
- **#10** The pouch shot was the weakest in the video → pushes in to 1.62, eggs read individually.
- **#11** End card was literally frozen (motion 0.02) → idle breathing and blinking added.
- **#12** 3.4 s of dead air at the end, last 1.5 s at digital zero → tail trimmed (DUR end+4.4 → end+3.2).
- **#13** Lighting discontinuity: Roly's intro used the deep-water background between two bright shallow
  scenes, same moment and place → shallow variant.
- **#14** Label "still back on the gills" was word-for-word its caption → "he never moves in".
- **#18** Roly reached near-brooding size on the gills; the paper argues the growth happens in the mouth
  → she stays nearer male size at the hand-off.
- **#20** Label repeated the caption's "a crustacean" → "not an insect. not a louse."

## Not actioned (deliberate, or within tolerance)

- #15 a 0.80 s caption, #16 overlapping legs in the head-on "fourteen feet" pose, #17 "bony pad" vs
  "a pad over bone" (fact-checked ✅ with slight imprecision), #19 ~1 s of gill chamber before the iris,
  #21 voice at 1.65 s vs the 1.5 s target, #22 true peak −1.4 dB vs the −1.5 dB rule.

## Bugs introduced while fixing, and caught

- The new push-in started at z 0.95, zooming *out* past the edge of the background and showing black bars.
- The camera re-centred on the tongue even at z = 1, shifting the background up and showing bars again.
  Fixed by making the focus drift with the zoom so the camera is the identity at z = 1.
- The focus interpolation was unclamped, so above z = 1.38 it overshot and clipped Roly's shell.

## What the judge said works

The hook and thumbnail; Roly and Mango both genuinely on-model against Brusca 1981 and FishBase; the
"proof" beat called "the best piece of science storytelling the channel has done"; the hedge honest and
near-verbatim from the authors; 48 caption bubbles with zero overlaps and a complete sound-off read;
−14.0 LUFS; the no-blood tongue fade.
