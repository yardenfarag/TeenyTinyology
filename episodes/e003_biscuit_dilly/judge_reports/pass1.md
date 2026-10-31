# e003 judge pass 1 — 003-biscuit-and-dilly_illustrated.mp4 (97.0 s)

## Verdict
A strong first cut that needs one fix pass before the owner sees it. The story reads in one watch: hook → cast →
labelled flashback → bite → walk under the skin → heart → lung arteries → mate → babies → cycle closing at dusk. The
parasitology is better than most pop-science on this worm: L3s are *not injected* but arrive in a drop of mosquito
haemolymph and crawl in through the bite wound. Audio is clean. Two things block publishing: (1) the hook and closing
line overstate the claim — "can't grow up without a dog" is false (coyotes, foxes and wolves are normal hosts; cats
and ferrets occasional), and it contradicts this episode's own facts.md row 15; (2) the science pictures get scale
badly wrong at the climax — the babies are drawn about 1/7 of their mother's length and as thick as she is (real:
about 1/1000 in length, 1/150 in thickness), a repeat of an e001 lesson. Several smaller picture/narration mismatches
under Should fix, two of them repeats (Dilly invisible in the heart; nothing on screen shows "doesn't inject her").

## Scorecard (1–10)
Facts 7 · Science visuals 5 · Story clarity 8 · Visual polish 7 · UI/UX 8 · Pacing & audio 8 · Overall 7

## Must fix
1. **Hook, frame-0 label and button overstate the host range.** Narration 1.65–5.3 s "This worm can't grow up without
   a dog… and a mosquito"; frame-0 label "This worm needs / a dog AND a mosquito" (the thumbnail); button 88–92 s
   "…a worm that needs them both". Merck: coyotes, along with dogs, are the most prominent definitive hosts; adults also
   develop in cats and ferrets. AHS: heartworms also live in wolves, coyotes, foxes, sea lions. Wikipedia lists the same.
   facts.md row 15 itself says "dogs are her main home". Repeats l001 ("an absolute opening claim and a later exception
   must meet") and e002 ("a label must not state what facts.md forbids"). Preferred fix: re-take the hook line (and
   label); minimum fix without new audio: change the label and put the exception on screen.
2. **Scale (repeat of e001 "true relative scale").** Microfilariae are 290–330 µm × 5–7 µm (≈1 red cell wide, ≈43
   cells long); the adult female ≈25–30 cm × ~1 mm. At 72–76 s the babies are ~250–300 px long and ~20 px thick — the
   same thickness as Dilly and ~1/7 of her length. The "about 1 foot" adult is ~33 red cells long and thinner than one
   cell (61–76 s). At 52–54 s the young adult (2.5–4 cm on arrival) is shorter than the microfilariae in the identical
   blood shot at 24.9 s. Fix: shrink the red cells to specks or drop them in the adult shots, draw the babies as
   hair-thin wisps, keep the cute baby close-ups inside the lens; let the young adult run long in the vessel.

## Should fix
1. 31.5–32.4 s: Dilly pokes out of Poppy's face into the air (straight-line move from the abdomen past the head); she
   never enters the proboscis. End her path at the proboscis base and continue along it; leader on "the mouthparts".
2. 53.8–56.6 s: Dilly invisible in the heart (repeat ×3 of "every narrated beat needs a visual payoff") — the worms
   callback draws under the heart. Draw her over it from 53.8 s and send her out at "stop".
3. 33.9–36.8 s: nothing shows "Poppy doesn't inject her" (repeat); Dilly appears only at ~35.9 s and exits ~100 px
   up the sheath. Show her inside the sheath from the start; Merck: larvae erupt through the tip of the labium.
4. Adult worm drawing bug 61–76 s: the ink line in `dilly.draw_along` uses `pts[::5]`, so it cuts chords across tight
   bends (faceted body). Use every point; sample `along(snake…)` more densely.
5. The male is ~25% of her length (real 60–77%) and his flat jagged coil sits on Dilly's face. Make him ~55–65% of her
   length, draw the coil as a side-view spring, keep it clear of her face.
6. Day counter: counts 56→70 while she floats in the blood (implies a two-week ride); "day 70" at the heart is outside
   Wikipedia's 75–120 days. Freeze during the ride; show "about 3 months after the bite" on arrival (facts.md row 6).
7. End card fully readable ~2.5 s only (repeat of e001 "≥ 4 s"). Add ~1.5 s to DUR / bring the plate in sooner. Plate
   at y≈1000 rather than the bible's ≈1400 — confirm it was the owner's choice.
8. Labels touch the watermark: "two weeks earlier · another dog" (22.3–27.4 s, ~2 px gap), "only while the weather is
   warm" (29.7–30.6 s), "microfilariae: the babies' name" (72.5–76.8 s, ~8 px). Move them to rendered y ≥ 370.
9. 12.0–16.8 s: the caption bubble covers Biscuit's tail, paws and lower muzzle (dog at y 1190–1410).
10. 37.6–38.6 s: "a drop of Poppy's own fluid" butts against the proboscis; the rod paints over "fluid".

## Nice to have
- First molt barely reads (42–45 s): the old skin sits on her own path at α 0.45.
- X-ray lung fills the whole trunk; real lungs are the front half.
- Units: "about 1 foot" under narration in centimetres → "up to 30 cm (1 ft)".
- "The heart is just a stop on the way" reads as a general rule; tag "the lung arteries: where most heartworms live".
- Caption breaks: "But the heart | is just a stop on the way."; "Dilly settles | in the arteries of the lungs,";
  "But they can't grow up | inside Biscuit."
- Hook label repeats the caption word for word (acceptable as the thumbnail title).
- SFX: `purr` on a dog (8.8 s) is a cat sound that Mochi owns; `footsteps` under "Slowly" on a legless worm — a soft
  tick matching the day counter fits better.
- Loop point: the last 0.5 s fades to black, then loops into a bright frame 0.
- 10.5–16.8 s: Poppy drawn bigger than Biscuit in the same plane.
- Microfilariae have faces in the lens but not in the artery — pick one.
- 17–22 s lens: a small "in her mouthparts" tag would orient viewers earlier.

## What works
Not-injected / drop-of-haemolymph / in-through-the-bite sequence is correct and well staged (mouthparts pull out
before she enters). "two weeks earlier · another dog" makes the flashback painless; the day counter is a good idea; the
dusk return mosquito matches the babies' night-time peak; her red, fed belly as she flies off; the lens bookends the
episode. Frame 0 is a real thumbnail, music from frame 0, voice at 1.65 s. Same-character transitions are hard cuts.
Captions: one bubble at a time, widest x 66–893, shortest 0.95 s, none in the app UI zones. Audio −14.0 LUFS,
−1.8 dBTP, LRA 2.2, no silent window, no black frames, no frozen run ≥ 1.5 s. Biscuit calm and healthy throughout, no
medical talk, species named on the end card.

## Fact-check table
| Claim | Verdict | Source |
|---|---|---|
| "can't grow up without a dog… and a mosquito" / "needs a dog AND a mosquito" / "needs them both" | ✗ overstated: coyotes (principal reservoir), foxes, wolves; less often cats, ferrets | Merck, AHS, Wikipedia |
| "Only females bite. They need blood for their eggs." | ✓ | CDC |
| "began as a baby worm in another dog's blood… Poppy sipped her up" | ✓ | AHS, Merck |
| "two weeks" + "only while the weather is warm" | ✓ 10–14 d at > 27 °C; 1–4 weeks by temperature | Merck, AHS |
| "crawled down to her mouthparts" | ✓ text; picture ✗ (exits the face) | Merck |
| not injected / drop on the skin / in through the bite / "a drop of Poppy's own fluid" / "the bite hole" | ✓ "erupt through the tip of the labium, with a small amount of hemolymph, onto the host's skin… migrate into the bite wound" | Merck, AHS |
| "Under the skin, she molts" / "day 3" | ✓ L3→L4 3–12 d (Wikipedia 1–2 weeks) | Merck, Wikipedia |
| "about two months" / counter to 55 | ✓ final molt d 50–70 (Wikipedia 45–60) | Merck, Wikipedia |
| "One last molt… a blood vessel" / "a young worm now" / "a vein" | ✓ | Merck |
| counter 56→70 in the blood; "day 70" at the heart | ⚠ arrival 70–120 d (Merck), 75–120 (Wikipedia) | Merck, Wikipedia |
| "The blood carries her to the heart" | ✓ | Merck, Wikipedia |
| "the heart is just a stop… settles in the arteries of the lungs" | ✓ for Dilly; ⚠ as a general rule | Merck, AHS |
| "up to thirty centimetres" / "about 1 foot" | ✓ | Merck, Wikipedia, AHS |
| "A male…" / "corkscrew tail" | ✓ text; picture ✗ male too short | Wikipedia, Merck |
| "Months later, Dilly has babies" / "microfilariae" | ✓ from 6 months, typically 7–9 | Merck, CAPC |
| "Tiny worms, drifting in Biscuit's blood" | ✓ text; picture ✗ scale (290–330 × 5–7 µm) | Parasites & Vectors 6:48 (2013); PMC3598535 |
| "can't grow up inside Biscuit. They need a mosquito." | ✓ | AHS |
| dusk sip | ✓ consistent with night-time peak | facts.md row 11 |
| End card *Dirofilaria immitis* · the dog heartworm | ✓ | Wikipedia |

Sources: merckvetmanual.com (heartworm disease in dogs, cats and ferrets) · heartwormsociety.org (heartworm basics) ·
en.wikipedia.org/wiki/Dirofilaria_immitis · cdc.gov (Aedes life cycle) · capcvet.org/guidelines/heartworm ·
Parasites & Vectors 6:48 (2013) · PMC3598535
