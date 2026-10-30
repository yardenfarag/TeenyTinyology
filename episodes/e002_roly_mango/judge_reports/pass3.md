# Episode 002 — video-judge, pass 3

**Verdict: PUBLISHABLE.** Facts 9 · Science visuals 8 · Story clarity 9 · Visual polish 8 ·
UI/UX 8 · Pacing & audio 9 · **Overall 8.5/10**

> "Every pass-1 and pass-2 must-fix is genuinely resolved, and I could not break any of them… Nothing I
> found is a factual error, a lost caption, a clip, a freeze over 2 s, or a safe-zone failure that costs
> the viewer information."

**Must fix: none.**

The judge re-measured the audio independently (decoded f32, 4× oversampled true peak) and confirmed every
figure: −14.0 LUFS, sample peak −1.499 dBFS, true peak −1.498 dBTP, 0 samples over, **0 exact-zero samples
in the whole track**, music present on frame 0.

## Should-fix items, all actioned

- **The label "the gills are his home" floated under the brooding female** — the animal who is in the
  *mouth* — with no pointer. "The single change I'd make before uploading." → dropped; the inset already
  says it.
- **Seven labels repeated their own caption word for word** (repeat of the e001 lesson "tags must add
  information"). Rewritten so each adds a second fact:
  "that is why something else can do the job" · "she will never be male again" ·
  "only on her first two segments" · "fish carrying several are often underweight" ·
  "they leave as swimmers, not larvae" · "these are the vomerine teeth".
- **The `s_father` inset broke the top safe zone** (keyline at y = 152; rule is y ≥ 200) → moved down 74 px.
- **A caption broke after the preposition "through"** → forced break after "slipped in".
- Nice-to-have: `s_place` given a push; Wikipedia's "completely consume" contradiction answered in the
  upload pack with a link to Brusca & Gilligan 1983 so the correction has a receipt.

## It audited `verify.py` again, and found a real bug

- **The watermark mask box masked empty sky.** I had `rows 0–200, cols 0–320`; the badge is at
  `rows 202–315, cols 60–165`. It had never been masked — through two passes of me trusting it.
- **I printed a decoded-sample peak and called it true peak.** Now read from ffmpeg's `ebur128`.
- **A per-scene mean cannot see a freeze**, and "nothing frozen > 2 s" is a run-length rule → added a
  run-length detector at a 0.25 s step.
- Silence windows did not overlap (so the real resolution was 0.8 s, not 0.75) → 50 % overlap, and the
  gate raised from −60 to −50 dB.
- The black-frame test ran on the **masked** array, biasing the very statistics it tested → now on the raw
  frame.
- Per-scene means were inflated by the 0.45 s crossfade at each boundary → ±0.5 s excluded.

## Final state

LUFS −14.0 · true peak −1.5 dBFS · 0 samples over · 0 exact-zero samples · no quiet run ≥ 0.5 s ·
**no frozen run ≥ 1 s** · no black frames · no timeline holes.

Two scenes sit below 0.45× the episode's own p75: `s_tongue` (0.31) and `s_father` (0.35, lifted from 0.19
after this pass). `s_tongue` is the flat-parchment card where the metric is known to under-report a
push-in — verified by eye that it grows from a thin line to filling the frame. Neither contains a frozen
run.
