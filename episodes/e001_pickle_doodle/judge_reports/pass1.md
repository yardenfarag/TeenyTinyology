# e001 judge pass 1: render v3, score 6.5 (all must/should fixes applied before v5)

## Verdict
This is a charming, mostly accurate first episode with a strong premise. The narration is well paced, the art is consistent, and loudness is on target. I would publish it only after fixes. Two things block it. First, the emergence shot (≈62.7–64.0 s) teaches something false: the worm comes out of the middle of Pickle's back, drawn on top of her wing, and its tail sticks up into the air above the water. Second, the captions overlap and double-stack at about 13 line boundaries. On top of that, the payoff of the hook (Pickle jumping into the water) is a tiny, dark hop of about 0.6 s, the first second has no audio and no hook, and the captions and end card sit partly under the app UI. One script line slightly overstates what is known ("heading for the water"). Everything else holds up against university and peer-reviewed sources.

## Scorecard (1–10)
Facts 8 · Science visuals 6 · Story clarity 7 · Visual polish 6 · UI/UX 5 · Pacing &amp; audio 8 · **Overall 6.5**

## Must fix (blocks publishing)
1. **[62.7–64.0 s / safezone_08_063.96.png, my extra strip judge_extra/emerge.png] The worm comes out of Pickle's back, and its tail pokes into the air.** At 63.0 s the worm's forked tail runs from Pickle's back straight up out of the frame, above the water line (y≈430). At 63.96 it is drawn on top of her wing and abdomen, going from (610,185) to (215,805), so it looks like it pierces her back.
 - Why it matters: real hairworms leave through the rear end of the host's abdomen, into the water. This is the central science shot of the episode.
 - Fix: anchor the exit point at the abdomen tip, roughly Pickle local (-150,-60) via `pickle.to_world`. Start the worm pointing down and backwards (about 110–140° from facing). Draw it behind Pickle's body layer, or clip it below the water line, and keep every worm point at y &gt; 450. Let it slide out over about 1.5 s, starting at "slides".
2. **[3.0, 9.9–10.4, 18.0–18.5, 23.2, 31.0, 37.5, 43.2, 44.9–45.4, 50.9, 55.5–56.2, 67.2–67.4, 77.7–78.2, 82.5–83.4 s / sheet_00, 03, 06, 07, 09, 11, 12, 13; safezone_10_078.16.png] Two caption pills draw on top of each other.**
 - Cause: each script line's first caption starts before the previous line's last caption ends. For example, "She's a cricket…" runs 2.03–3.71 and "and she's about to do…" starts at 3.18.
 - Effect: two unreadable lines of text stacked in the same spot, up to 0.8 s at 82.5–83.3 ("like Pixie once was" under "They fly to land…"). With the sound off, that is the story text.
 - Fix: in the caption builder, clamp each caption's end to the next caption's start (`end = min(end, next.start)`). Also replace the fade-out/fade-in between chunks of the same pill with a hard swap or a ≤2-frame crossfade. Right now the pill dips almost to nothing between chunks (judge_extra/capgap.png, about 1.95–2.05 s; also visible at 40.10, 47.0, 80.78).

## Should fix (clearly better)
1. **[59.6–60.4 s / judge_extra/hop.png, key_060.19.png] The climax is undersold.** The hook promises "something no cricket should ever do", and the payoff is a hop by a roughly 150 px cricket in a dark night scene, lasting about 0.6 s, under the "scientists are still figuring out" caption. The narration never says she jumps in. Fix:
 - Push in, or cut to a closer shot with Pickle at about 2× scale, centred near y≈1000.
 - Give the hop anticipation and slow it to about 1.2–1.5 s, starting at `q["splash"].start - 1.2`.
 - Let the existing boing → splash pair carry it.
 - Make the ripple bigger. Optionally add a short on-screen word ("Splash" is fine as a graphic, not spoken).
2. **[50.85–55 s script "drawn"] "Pickle starts heading for the water" overstates the science.**
 - Thomas et al. (2002) found no support for long-range water detection: infected crickets wander erratically and jump in when they meet water.
 - Coates et al. (2025) found infected crickets showed no Y-maze preference for water but entered it once they met it.
 - Suggested line: "Pickle starts wandering… restless… until she finds the water." The visual (walking along the shore) already fits this.
3. **[0.0–0.8 s / sheet_00, short-term LUFS −120 at 0–1 s] Silent, static opening.** For about 0.8 s there is no voice, no music, no caption and no tag, and the hook sentence only arrives at 3.2–7.2 s. That breaks the "hook in the first 2 seconds" rule in CLAUDE.md, and the first frame (a plain cricket in a meadow) is a weak thumbnail. Fix:
 - Start the music and a soft sparkle at 0.0, and the voice at about 0.3 s.
 - Add a frame-0 visual teaser, e.g. a 0.8 s flash of Pickle at the moonlit water's edge with the "?" bubble, or a title card "Why do crickets jump into ponds?", inside y 250–1400. Then cut to the meadow intro.
4. **[all scenes / every safezone_*.png] Captions sit in the app's description/username zone.** The pills span about y 1470–1650 (two-line pills reach about 1650), while the overlay's bottom UI zone starts at y=1520. The caption centre y=1560 is a locked CLAUDE.md decision, so this needs the owner's call. Recommendation: move the centre to about y=1400 and cap pills at one line of about 28 characters (two-liners at 3.7, 44.9, 53.2, 57.6, 68.4, 73.9, 77.7, 84.0 s).
5. **[85.4–89.4 s / safezone_12_087.43.png] End-card layout.**
 - (a) The "Mayfly nymph" icon (x≈930–1000) and the word "larva" sit under the right-hand app buttons. Shift the cycle diagram's centre about 60 px left, or cut its radius about 10 %.
 - (b) "Teenyology / Teeny creatures. Big stories." at y≈1620–1700 is fully inside the description zone. Move it to about y 1380–1460.
 - (c) The diagram skips the defining step: it goes "Cricket eats the mayfly" → "Worm swims out in the water". Relabel the left node "Cricket jumps in → worm swims out", or add a node.
 - (d) The node labels are about 30 px high on 1080 width. Raise them to about 40 px so they are readable on a phone.
6. **[73.9–82.0 s / safezone_10_078.16.png, key_080.78.png] Larvae are drawn as mini adult worms, a third of the nymph's length.** The narration earlier stressed "no bigger than a speck". Real larvae are microscopic, roughly a tenth of a millimetre. Fix: draw them as tiny pale specks (≤12 px) with the spiny proboscis (`doodle.draw_larva` at small scale), and drop the forked "male" tail.
 - Same scene, at 77.5–78.2: the nymph enters tail-first toward the larvae with its head off-screen right (x&gt;1080, under the app buttons), so you never see a larva being swallowed. Bring the nymph in head-first from the left, or mirror it so its mouth meets a larva, then show the cyst appear in its abdomen (the cyst at 80.78 is good).
7. **[43–50 s / safezone_05_046.85.png] Two free-swimming worms appear while Doodle is still inside Pickle, with no label saying which is which.** It can read as "Doodle is already in the water". Tag one worm "a mate?" or show a single worm with a heart or "?", and show the "Water" label from 43.2 instead of 45.5.
8. **[22.08 s / safezone_02_022.08.png] In the Pixie close-up, her head and front leg sit inside the app-buttons zone (x≈890–1070).** Shift the Pixie close-up about 120 px left. The Doodle cyst and tag stay central.

## Nice to have
1. **[82.5 s cycle3]** "They fly to land…" follows "young insects", but nymphs don't fly. Change to "They grow up, fly to land… and wait for the next hungry cricket."
2. **[31–37 s s_grow]** About 6 s of nearly static meadow before the coil becomes clear. To sell "Week after week", add a quick sun/moon or day-night tint cycle (2–3 cycles) behind Pickle, with the coil visible from 31.5 s.
3. **[60.9 s]** The night scene cuts to a bright, sunlit underwater scene with Pickle at the surface, and the survive scene is also daytime. Tint the escape scene to dusk or night for continuity, or fade through blue.
4. **[Loudness]** True peak is −1.4 dBFS. That passes the judge's ≤ −1 dB but is 0.1 dB over the locked −1.5 dB in CLAUDE.md. Lower the limiter ceiling by about 0.2 dB.
5. **[73.9 s cycle1]** "Soon, a new batch of worm eggs hatches" compresses the timeline: adults mate (often after overwintering), then the eggs hatch about 3–4 weeks later (UC IPM). It's acceptable, but "Later," is more accurate than "Soon,".
6. **[Pickle across scenes]** The near antenna is drawn as a sharp kink plus a straight line (e.g. safezone_00 at x≈640–760, y≈1060). It looks like a wire handle. A smoother continuous curve would read more like an antenna.

## What works (keep doing this)
- **"Doodle, unwound" (38.5–40.5 s, key_040.10.png):** shrinking Pickle and laying out the worm at about 7× her length is a superb, instantly clear scale gag.
- **Introductions and tags:** the "This is X. She's a Y…" intros with name tags, and the "young Pixie, in the pond" nymph label, show both life stages and set up the cycle.
- **Night scene and "?" bubble:** these honestly flag the unknown mechanism.
- **Cyst inside Pixie (22 s) and inside the nymph (80 s):** correct life-cycle biology, and cute.
- **Egg strings (74 s):** drawn as gelatinous strands, which is accurate.
- **Sound design:** effects line up with on-screen action: crunch×3 + gulp on "gobbles", boing on the hop take-off, splash on the ripple, the "?" pop at 55.7 s.
- **Loudness:** −14.0 LUFS integrated with LRA 2.9 is steady, and there is no dead air except the intended end-card tail.
- **Script:** calm tone, good turns ("There's just one problem."), no spoken sound words, about 140 wpm, and a hopeful ending (Pickle survives).

## Fact-check table
| Claim (as narrated/shown) | Verdict | Source |
|---|---|---|
| Pickle is a cricket; female, doesn't chirp (series bible) | ✅ Not narrated; design is fine | general entomology |
| Pixie the mayfly "grew up underwater, in a pond" | ✅ Nymphs are aquatic, living weeks to years | [GNWT – Mayflies](https://www.gov.nt.ca/ecc/en/services/biodiversity/mayflies) |
| "at the very end of her short life" | ✅ Adults live hours to a few days | [GNWT – Mayflies](https://www.gov.nt.ca/ecc/en/services/biodiversity/mayflies) |
| Horsehair worm "no bigger than a speck… hiding inside Pixie" | ✅ Larvae encyst in aquatic insects such as mayflies, mosquitoes and midges; cysts survive the insect's metamorphosis (shown for midges; mayflies *Callibaetis* found naturally infected) | [UC IPM](https://ipm.ucanr.edu/home-and-landscape/horsehair-worms/) · [Hanelt &amp; Janovy 2004, J. Parasitol.](https://bioone.org/journals/journal-of-parasitology/volume-90/issue-2/GE-78R/LIFE-CYCLE-AND-PARATENESIS-OF-AMERICAN-GORDIIDS-NEMATOMORPHA-GORDIIDA/10.1645/GE-78R.full) |
| Pickle eats Pixie, "Doodle included" (infection by eating a carrier host) | ✅ | [UC IPM](https://ipm.ucanr.edu/home-and-landscape/horsehair-worms/) |
| "Inside Pickle, Doodle grows… Week after week" | ✅ About 3 months until the host seeks water | [UC IPM](https://ipm.ucanr.edu/home-and-landscape/horsehair-worms/) |
| "several times longer than she is, wound up tight" | ✅ Conservative: adults reach 10–15 cm (*P. tricuspidatus*) up to 30 cm+, vs crickets of about 1–2.5 cm | [UC IPM](https://ipm.ucanr.edu/home-and-landscape/horsehair-worms/) · [Wikipedia – P. tricuspidatus](https://en.wikipedia.org/wiki/Paragordius_tricuspidatus) |
| "Doodle needs water to find a mate"; "Pickle lives on land" | ✅ Adults are free-living in water and mate there | [UC IPM](https://ipm.ucanr.edu/home-and-landscape/horsehair-worms/) |
| "Pickle starts heading for the water" | ⚠️ Overstated: no evidence of long-range water seeking; erratic wandering, then entering water on contact | [Coates et al. 2025, PLoS One (reviews Thomas 2002, Sanchez 2008)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12456768/) |
| "How the worm pulls this off… scientists are still figuring out" | ✅ The mechanism is "poorly understood"; light, erratic movement and dehydration have all been tested | [Ponton et al. 2011 (PMC3071748)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3071748) · [Coates et al. 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12456768/) |
| Silent splash: the cricket jumps into the water | ✅ | [Wikipedia – P. tricuspidatus](https://en.wikipedia.org/wiki/Paragordius_tricuspidatus) |
| "In the water, Doodle slides out… swims off to find a mate" | ✅ Worm emerges in water. ⚠️ The **visual** exit point (back, into the air) is wrong; see Must fix 1 | [UC IPM](https://ipm.ucanr.edu/home-and-landscape/horsehair-worms/) |
| "If she can scramble back to dry land… she can actually survive" | ✅ "Emergence… is not lethal per se"; crickets that don't drown can live months (up to 130 days) | [Ponton et al. 2011 (PMC3071748)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3071748) |
| "a new batch of worm eggs hatches in the pond" | ✅ Egg strings laid in water hatch in about 3 weeks to a month ("Soon" is a little compressed) | [UC IPM](https://ipm.ucanr.edu/home-and-landscape/horsehair-worms/) |
| "tiny larvae get swallowed by young insects, like Pixie once was" | ✅ | [UC IPM](https://ipm.ucanr.edu/home-and-landscape/horsehair-worms/) · [Hanelt &amp; Janovy 2004](https://bioone.org/journals/journal-of-parasitology/volume-90/issue-2/GE-78R/LIFE-CYCLE-AND-PARATENESIS-OF-AMERICAN-GORDIIDS-NEMATOMORPHA-GORDIIDA/10.1645/GE-78R.full) |
| "They fly to land… and wait for the next hungry cricket" | ✅ Cysts survive metamorphosis into the winged adult (wording: it's the grown-up insects that fly) | [Hanelt &amp; Janovy 2004](https://bioone.org/journals/journal-of-parasitology/volume-90/issue-2/GE-78R/LIFE-CYCLE-AND-PARATENESIS-OF-AMERICAN-GORDIIDS-NEMATOMORPHA-GORDIIDA/10.1645/GE-78R.full) |

I did not edit the project. To check the hop, the emergence and the caption gaps, I pulled extra frame strips with ffmpeg and saved them outside the repo, in `C:\Users\yarde\.t3\scratch\2026-10-22-ant-worm-berry-mp4-t3-f8b9242e\judge_extra\` (hop.png, emerge.png, land.png, capgap.png).</result>
