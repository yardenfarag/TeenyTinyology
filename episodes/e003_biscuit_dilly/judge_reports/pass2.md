# e003 judge pass 2 — re-render after pass-1 fixes (~98.5 s)

## Verdict
A clear step up; nothing blocks publishing. Both pass-1 Must fixes hold: the hook and closing line now describe this
worm's own story ("grows up inside two animals: a dog… and a mosquito" / "a worm that lives in both") and survive
Merck and Wikipedia; the scale props are re-scaled per shot (red cells 1:1 with a microfilaria in the flashback,
specks beside the adult, babies hair-thin). Seven of ten pass-1 Should fixes fully land. Three items deserve one
short code-only polish pass: the new male sweeps across Dilly's face and his tag points at her; three labels are on
screen < 1 s; the new "heart" tag covers Dilly exactly when the fix was meant to show her. Two of these repeat
"a fix is checked like new work". Audio: −14.0 LUFS, −1.5 dBTP, sample peak −1.54 dBFS, LRA 2.6, no window ≥ 0.75 s
below −60 dB; no black frames or edges.

## Scorecard (1–10)
Facts 9 · Science visuals 8 · Story clarity 9 · Visual polish 7 · UI/UX 8 · Pacing & audio 9 · Overall 8

## Must fix
None.

## Should fix
1. 67.5–77.2 s, the male (`s_artery`): a high-amplitude travelling sine drawn after Dilly sweeps over her face in
   ~8 of 20 samples (eye fully covered ~70.5 s and ~76.5 s — the "Dilly has babies" climax). The tag pointer lands on
   Dilly's lower loop, not his coil; his zigzag body reads as "the corkscrew" while the real coil is a flat squiggle.
   Fix: draw him before Dilly, amplitude 110 → ~40, freeze the wave phase, a 3-loop ~60×90 px spring tail at x ≈ 760,
   tag tip on the coil (bubble right edge ≤ 900). Length is right now (63%; Merck 60%, Wikipedia 77%).
2. Labels too short to read (measured on the MP4): "only while the weather is warm" ~0.8 s, "a drop of Poppy's own
   fluid" ~0.8 s, "a young worm now" ~1 s. Re-time: weather (weeks − 0.4 → "mouthparts"); drop (w_drop − 0.5 →
   w_wrig + 0.6); bite hole from w_wrig + 0.6; young worm (w_molt + 0.2 → "carries").
3. 55.3–57.8 s: the "heart" tag sits on the heart and hides Dilly; its pointer lands on the foreleg. Put the tip on
   the heart's right edge from outside (bubble above-right over the shoulder); widen her to ~9 world px.

## Nice to have
- `s_artery` labels drawn inside the camera grow and drift with the push-in; "microfilariae: the babies' name"
  reaches x 933 at 77.2 s. Draw them after `c.restore()`.
- "Months later" has no time marker although the device was set up twice: add "about 6 months after the bite".
- End-card plate reaches x 916 at the end of its 0.97 → 1.05 zoom; cap the zoom.
- Artery shot is the longest composition (15.3 s); masked motion 0.54× the p75 — a bigger push (1.0 → 1.3) with a pan
  toward her head at "babies" would read better.
- The dusk mosquito is drawn as Poppy 6+ months later (most females live weeks); a palette swap would read as new.
- 32.5–33.0 s: her crawl hugs the underside outline of thorax and head; raise the route.
- Still open: caption breaks ("But they can't" 1.08 s; "But the heart is just | a stop…"; "…in the arteries | of
  the lungs,"), loop-point fade to black, X-ray lung fills the trunk, Poppy bigger than Biscuit, no "in her
  mouthparts" tag in the 17–22 s lens.

## What works
The bite sequence is complete and correct (in the labium from 34.9 s, out of its tip at 37.8 s, in the drop, then
into the hole — Merck step for step). The day counter stops before the bloodstream and hands over to a hedged
"about 3 months after the bite". Babies leave near her head end (vulva ~2.4–2.7 mm from the anterior end). First molt
reads; smooth outline; "where most heartworms live"; clean same-character cuts; each named thing in the closing line
gets its own visual; end card ~4.9 s; thumbnail clear of the watermark.

## Pass-1 status
| Pass-1 item | Status |
|---|---|
| Must 1 hook/label/button host range | Fixed |
| Must 2 scale | Fixed, within phone limits |
| S1 exit through the face | Fixed (minor nit) |
| S2 Dilly invisible in the heart | Partly — visible, but covered by the new tag |
| S3 nothing shows "doesn't inject" | Fixed |
| S4 faceted outline | Fixed |
| S5 male length / coil on her face | Partly — 63% length; body now crosses her face; flat coil; tag on her |
| S6 day counter | Fixed |
| S7 end card 2.5 s | Fixed (~4.9 s; y≈1000 is the owner's centred layout) |
| S8 labels touching the watermark | Fixed (drift at 77.2 s) |
| S9 caption covers Biscuit | Fixed |
| S10 drop label vs rod | Position fixed; ~0.8 s on screen |

## Fact-check (new or changed wording)
| Claim | Verdict | Source |
|---|---|---|
| "This worm grows up inside two animals: a dog… and a mosquito" + thumbnail | ✓ | Merck |
| "A dog. A mosquito. And a worm that lives in both." | ✓ | Merck; Wikipedia |
| "about 3 months after the bite" | ✓ Merck 70–120 d; Wikipedia 75–120 d | Merck; Wikipedia |
| day counter 3 → ~55, frozen for the ride | ✓ | Merck; Wikipedia |
| "the lung arteries · where most heartworms live" | ✓ | Merck; Wikipedia |
| "up to 30 cm (1 ft)" | ✓ | Wikipedia; Merck |
| "a male · corkscrew tail", 63% length | ✓ text and length; ⚠ pointer on Dilly | Wikipedia; Merck |
| out through the labium tip into a drop of haemolymph, then the bite wound | ✓ | Merck |
| babies released near her head end | ✓ | Türkiye Parazitol Derg 2025 case report |

## Lessons proposed
- (repeat) A fix is checked like new work — moved labels kept their 0.8 s windows; the new tag hid the fixed worm.
- A label beside a caption needs ≥ ~2 s; measure on the encoded MP4.
- Draw labels after `c.restore()`: inside a camera push they grow, drift and can leave the safe zone.
- A second character on a travelling wave sweeps across the hero; scan the whole window and draw the newcomer behind.
