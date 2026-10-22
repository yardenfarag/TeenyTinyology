# e001 judge pass 3: render after the pass-2 fixes, score 8.6. Verdict: publishable as is.

Scorecard: Facts 9 · Science visuals 8.5 · Story clarity 8.5 · Visual polish 8.5 · UI/UX 8 · Pacing & audio 8.5 · **Overall 8.6**
Loudness −14.0 LUFS, true peak −1.4 dBFS, LRA 3.3 LU. No must-fix items. All facts checked ✅ (same sources as pass 2).

## Pass-2 items
Fixed: the jump (crouch, kick, arc, dive), the caption overlap, the night-lit escape, the "week after week" nights,
Pixie's upright wings in scenes, the swallow zoom, the end-card arrows and hold, the tag text, the cyst push-in,
the slimmer tummy, and pale antennae at night.
Partly fixed: Doodle's length at exit (about 3.5–4× her body, not 6×; "several times longer" still holds), and the
caption line breaks.
Still open: the end-card mayfly icon had flat wings; Pickle's walk at 50–56 s still starts on the bank.

## Should fix → resolution (v6)
1. Two caption bubbles reached the right rail (x≈941): "Doodle needs water to find a mate." and "restless... until
   she finds the water." → captions are now centred in the safe zone (`scene.CAP_X = 480`). Every bubble fits in
   x 60–900. ✅
2. "and wait" flashed for 0.41 s, and "of worm eggs" split a noun phrase → the `|` breaks were fixed and the
   engine now honours script breaks only. The shortest caption is now 0.9 s. ✅
3. The end-card mayfly had flat wings and read as a lacewing → the icon now uses the upright-wing pose. ✅

## Nice to have → resolution
- The nights were short blinks → each night now holds longer (plateau curve). ✅
- Bubbles appeared above the waterline → they are clipped to below the surface. ✅
- The swallow zoom cropped the nymph → the zoom centre was shifted 120 px left. ✅
- Two Pickles showed in the crossfade into the hop → it is now a hard cut. ✅
- Pickle still starts on the bank at 50 s → open. It is limited by the background height; fix this in a future
  background pass.
- 3.2 s of silence under the end card → open (optional; it suits a loop).
