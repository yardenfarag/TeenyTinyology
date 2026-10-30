# Episode 002 — video-judge, pass 2

**Verdict: not publishable.** Facts 7 · Science visuals 5 · Story clarity 7 · Visual polish 7 ·
UI/UX 6 · Pacing & audio 5 · **Overall 6/10**

> "Pass 1's four must-fixes are two fixed, one fixed-but-regressed, one fixed-and-moved, and the fixing
> introduced one new factual error and left two measurable defects your automated checks did not see."

Pass 1's camera bugs were confirmed gone ("no letterboxing, no drift off the background, no clipped
subject anywhere in 45–62 s — I checked every edge of every 0.25 s frame").

## Must fix — all five resolved

| # | Finding | Resolution |
|---|---|---|
| 1 | **Hard clip: +1.97 dBFS sample peak / +3.0 dBFS true peak at 42.689 s**, three samples over full scale, from the `click` cue on `tongue2` stacking on the voice. The series rule is ≤ −1.5 dB; loudness normalisation does not remove it. | `click` gain 0.13 → 0.07. Now −1.50 dBFS, zero samples over. |
| 2 | **2.0 s of exact digital zero** under a frozen end card — worse than the 1.5 s it replaced in pass 1. | **Engine bug.** `mix.mixdown` padded the voice-derived ducking curve with `fit()`, which pads with **0.0**, so music was multiplied by zero wherever the picture outlasts the narration. Now padded with 1.0. Also took the music from a slice of a longer score so there is sound on frame 0. |
| 3 | Label **"he never moves in"** is the exact phrasing this episode's own `facts.md` forbids (Brusca 1981 records males in the mouth "in copula"). And the gravid female was drawn **inside the gill chamber**, so both isopods read as living on the gills — contradicting "the female gets the mouth". | Label → "the gills are his home". Shot recomposed: she holds the frame (in the mouth), he sits in a bordered inset labelled "on the gills". Keeps the owner's requirement that both are in one shot. |
| 4 | Pass-1 fix **moved, not fixed**: the manca held at x ≈ 969–1021 — forward of the **mouth**, not the gill cover, and squarely under the app's right rail — then dissolved on the surface of the cheek. At 0.62 scale she was ~70 px, "a crumb". | Hold moved to behind/below the operculum, inside x < 900; scale 0.62 → 1.0; she is now drawn **before** Mango so the gill cover genuinely occludes her instead of fading out. |
| 5 | "Fourteen hooked feet / seven pairs" over a pose where **only four legs a side** cleared the dome — eight visible. Adding the label made it an invitation to catch the error. | `_legs_facing` reworked: rear pereopods are the longest (Brusca 1981 p. 187), so they now reach past the silhouette even foreshortened. Seven a side count cleanly. |

## Should fix — resolved

- **#7** pouch frame ~90 % empty brown → push-in 1.30 → 2.05.
- **#8** label "Mango had been using her as a tongue" overstated the authors' *hypothesis* as observation
  and echoed its own caption → "the teeth in the roof, pressing down".
- **#9** "clamps onto the **base**" but she was drawn mid-pad → the pad now lies forward of her.
- **#13** specks read as crumbs and vanished before the line ended → more of them, larger, longer-lived.
- **#14** "Every one of them" was an 0.88 s bubble, under the 0.9 s floor → re-chunked.
- **#6** painted scenes that barely moved → `s_roly`, `s_hedge` and `s_eats` given real camera motion.
- Nice-to-have: end card no longer drops to deep water out of a bright shallow scene.

## Not actioned

`s_roly` as a free-swimming portrait (#10) — defensible as an intro plate; `s_place` sits at 0.45×, on the
boundary; a scale tag for Roly (#11) is a good idea but adds narration the owner has approved by ear.

## The judge audited my own checks, and was right three times

1. **Loudness without true peak** — I reported −14.0 LUFS and stopped, and would have shipped a clip.
2. **No silence detection** — 2.0 s of all-zero samples passed.
3. **Motion differenced over the whole frame** — my own caption band churns every ~1.5 s and lifted dead
   scenes over a fixed threshold, so "no static stretches" was partly an artefact. Nine of twenty scenes
   were near-dead once captions were masked.

All three are now in `episodes/e002_roly_mango/verify.py`, which masks the captions and the watermark and
compares each scene against this episode's own 75th percentile.

## After the fixes

LUFS −14.0 · peak −1.50 dBFS · 0 samples over · no silent run ≥ 0.75 s · no black frames ·
scenes below 0.45× p75: 2 of 20 (`s_end` 0.38, the deliberate end-card hold; `s_place` 0.45), down from 9.
