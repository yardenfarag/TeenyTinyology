# E005 "Mochi, Pip & Noodle" — judge report, pass 3

## Verdict
Both pass-2 blockers fixed: the front villi fade into the wall (no hard rectangles, 54.5–78.1 s) and Noodle's head
stays above the caption band in every framing (head ~y 1110–1190 vs captions y 1340–1460). Ruler card, "Pip, grown up"
timing and the hatch lens read better. One new collision from the label-window change. Publishable, ideally after Should 1.

Scorecard: Facts 9 · Science visuals 8 · Story clarity 9 · Visual polish 8 · UI/UX 8 · Pacing & audio 8 · Overall 8

## Status of pass-2 items
Must 1 fixed · Must 2 fixed · Should 1 fixed (card opaque) · Should 2 fixed on timing (small overlap, Nice 1) ·
Should 3 fixed (card ~2.5 s; the extended parts label caused new Should 1) · Nice 1 improved · heat shimmer and the
0.87 s caption unchanged, not blockers.

## Must fix
None.

## Should fix
1. ~76.5–78.1 s: "each segment: two sets of male + female parts" sits on the worm's tail exactly where the segments
   break off. End it at `leave.word("break") - 0.2` (still ~2.1 s).

## Nice to have
1. 40.0–41.1 s: the "Pip, grown up / a cat flea" bubble sits on the emerging flea's back; raise ~40 px.
2. Optional: stronger heat shimmer; caption override joining "crawl out…" to the next piece.

## Lessons check
Repeats: "a fix is checked like new work" (×6) — when extending a label window, re-scrub its new END against the
camera framing at that moment; "a tag's bubble must not sit on the thing it names" (minor, "Pip, grown up").
Honoured: one camera per setting, characters above the caption band, no mask rectangles, labels ≥2 s, visual payoff
for every beat, props as rulers, true relative scale, captions, safe zones, watermark, overlaps, frame-0 hook,
−14.0 LUFS, true peak −1.7 dB, no silence.

## Fact-check
No narration or label wording changed; pass-1/pass-2 tables stand, every claim ✅.

## After this pass (applied before the final render)
Should 1: the parts label ends at "break" − 0.2 s. Nice 1: "Pip, grown up" anchored 40 px higher.
