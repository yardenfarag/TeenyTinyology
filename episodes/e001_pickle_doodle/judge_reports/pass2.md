# e001 judge pass 2: render v5, score 7.8

## Verdict
This re-render is a clear step up from the 6.5 pass. The opening teaser, the cream captions at y≈1400, the stage lift, Doodle leaving from the tip of Pickle's abdomen underwater, the tiny larvae, the egg strings and the end card all came out well. Facts are solid, and the new "Is Doodle steering her?" line is accurate and fits the hedging rule. Loudness is on target. Nothing blocks publishing. What's left is polish: the jump into the pond is still the weakest moment, some captions split sentences in awkward places, there is a one-frame caption overlap at every line change, and mayfly Pixie's wings are drawn the wrong way. **Publishable after a short round of should-fixes.**

## Scorecard (1–10)
Facts 9 · Science visuals 7 · Story clarity 8 · Visual polish 7 · UI/UX 7.5 · Pacing & audio 8.5 · **Overall 7.8**

## Must fix (blocks publishing)
None.

## Should fix (clearly better)
1. **[62.4–63.6s, key_063.16 / key_063.36] The jump is still flat.** Pickle crosses the pond in her standing pose: legs folded, no wind-up, no kick. She hangs mid-air over the lily pads (y≈450–720), then fades into the splash rings. This is the moment the teaser promised ("Why would a cricket jump into a pond?"), so it needs to land. → Add a crouch for anticipation (about 0.25s), stretch her hind legs out on take-off, give the arc ease-in/out and land her into the rings. Don't fade out while she's in the air.
2. **[every caption change, e.g. 12.58, 38.41, 45.75, 58.76, 62.06, 83.57] Two caption bubbles overlap for one frame.** The new bubble draws on top of the old one before it has faded, giving garbled text like "Until he' than she is, s longer" (key_038.41) and "Doo mate. And Pickle? nd a" (key_045.75). Faint "ghost" letters also show inside the bubble right after a change (key_021.93, key_034.28, key_054.05, key_084.68). It's one frame (I checked 38.2–38.6s frame by frame), but it shows up as a flicker on every line and breaks the "captions never overlap" rule. → Hide the old bubble before the new one appears, or cut instead of crossfading when the gap is under 0.1s.
3. **[44.26–47.89s, 54.08–56.90s, 60.55–63.97s, 77.87–81.84s] Captions break in the middle of a phrase.** Examples: "Doodle needs water to find a" / "mate. And Pickle?", then "until she finds the" / "water.", then "still a" / "mystery." (which then sits alone for about 1.9s), then "worm" / "eggs hatches". With the sound off these read badly. → Break at punctuation first, never end a line on a/the/of, and allow ~30 characters per line so that "Doodle needs water to find a mate." fits on one line.
4. **[8.5–19s and 86.5–90s; key_012.58, key_019.13, end card] Pixie's wings lie flat back over her abdomen.** Adult mayflies hold their wings upright, pressed together above the back like a butterfly. That pose is the trait that makes a mayfly recognisable, and flat wings read as a lacewing or caddisfly. → Add an upright-wing resting pose to `characters/pixie.py` for perched and dead adults, and use it on the end-card icon too. Flight poses can stay as they are.
5. **[64.0–69.9s] Lighting doesn't match the night.** She jumps under a full moon at 63s, but the underwater shot at 64s has bright teal water with sun rays, then 70s is full daylight. → Give the escape scene a moonlit tint (darker teal, cooler rays). The jump to daylight at 70s is fine, since "if she can scramble back…" implies time passing.
6. **[66.0–69.9s, key_067.06] Doodle looks too short when he leaves.** The "Doodle, unwound" diagram (38–39.5s) shows him about 6× Pickle's length. When he slides out he reaches only about 1.5–2× her body before swimming off. → Let more of him come out (draw the trail longer, or keep it unspooling until about 69s) so it matches "several times longer".
7. **[34.5–37.0s, sheet_05/06] The day/night tint during "week after week" reads as a dimming glitch.** The frame just goes grey-dark twice (around 35.0s and 36.5–37.0s), with no moon, stars or blue cast. → Either make real night beats (blue tint plus a moon or a few stars over the hills) or drop the tint.

## Nice to have
1. **[83.0–83.3s] The swallow is too small to see.** The nymph does eat a larva head-first, but the larva is about 25 px, so on a phone it just disappears. → Zoom in slightly on the nymph's head (about 1.3×) for 0.5s, or add a small squash and a gulp on its head at "swallowed".
2. **[key_091.86] The end-card arrow touches a label.** The arrowhead on the "Cricket eats" → "Cricket jumps in" arrow sits on the "w" of "swims" (around x 208, y 870). → Stop the arrow about 20 px lower. The end card is also fully readable for only about 2.4s (91.0–93.4s) before the fade. Holding it about 1.5s longer would give a 5-step diagram time to be read and suits replays.
3. **[50–63s] Pickle is next to the water the whole time.** The night scene starts with her already on the bank, so "until she finds the water" has no visual payoff. Her antennae also almost vanish against the night (dark ink on dark blue). → Start her further from the water, on grass, and lighten her outline or antennae at night.
4. **[84.7–86.4s] The tag repeats the caption.** The tag subtitle "like Pixie once was" is identical to the caption shown at the same time. → Change the tag to "mayfly nymph".
5. **[19.1–27.2s] The shot holds for about 8s on a still, dead Pixie with a small cyst.** → Give the cyst a slow pulse or wiggle, or push the camera in gently toward it.
6. **[70–77s] Pickle looks unchanged after the worm leaves.** Her abdomen is still full and round, though a cricket's abdomen is visibly emptier once the worm is out. → Shrink it slightly.

## What works (keep doing this)
- **The teaser on frame 0** (key_000.40): the night pond, the cream two-line question placed safely at y 260–430, and the "?" bubble make a strong thumbnail. Audio starts on the first frame (−23.9 dB mean over 0–0.5s), and the voice starts at 1.65s.
- **Captions**: cream bubbles with a peach highlight on the spoken word, centred at y≈1400 and inside the safe zone in every overlay I checked.
- **The split shot at 42–50s** ("Water: where worms find mates" above, Pickle on land below) explains the whole problem in one picture.
- **Doodle leaving from the tip of her abdomen** with bubbles, and the "Doodle, unwound" length comparison, are memorable and accurate.
- **The pond-life scene**: white egg strings, tiny haloed larvae, and a nymph carrying a cyst are correct and calm.
- **The end-card cycle diagram** shows the coiled worm inside the cricket icon, a nice callback.
- **Audio**: −14.0 LUFS integrated, true peak −1.6 dBFS, loudness range 3.3 LU, no dead air apart from the deliberate 1.4s tail into the fade.
- **The new 57s line** keeps the calm documentary tone and hedges properly, as the narration rules require.

## Fact-check table
| Claim (as narrated/shown) | Verdict | Source |
|---|---|---|
| Pixie grew up underwater in a pond; mayfly nymphs are aquatic and adults are short-lived | ✅ | standard entomology; [UC IPM](https://ipm.ucanr.edu/home-and-landscape/horsehair-worms/) |
| Doodle, "no bigger than a speck", is hiding inside Pixie after she reaches land (cyst survives metamorphosis) | ✅ | [Minnesota DNR](https://dnr.state.mn.us/mcvmagazine/issues/2017/jul-aug/horsehair-worm.html) |
| Pickle eats Pixie, and Doodle comes with her (crickets scavenge dead insects) | ✅ | [Minnesota DNR](https://dnr.state.mn.us/mcvmagazine/issues/2017/jul-aug/horsehair-worm.html) · [UF/IFAS IN274](https://edis.ifas.ufl.edu/publication/IN274/pdf) |
| Doodle grows "week after week" until he's several times longer than she is, wound up inside her | ✅ | [UC IPM Pest Note](https://ipm.ucanr.edu/PMG/PESTNOTES/pn7471.html) |
| Doodle needs water to find a mate | ✅ | [UC IPM](https://ipm.ucanr.edu/home-and-landscape/horsehair-worms/) |
| Infected crickets wander until they find water | ✅ | [Thomas et al. 2002 (via PMC1559948)](https://pmc.ncbi.nlm.nih.gov/articles/PMC1559948) |
| "Is Doodle steering her? Scientists think so… but how he does it is still a mystery." | ✅ fair simplification. The mechanism is not settled, though there are leads: attraction to light reflected off water, worm proteins acting on the host brain, and 2023 gene-transfer evidence in worms that infect mantises. "Still being worked out" would be slightly more precise. | [Ponton et al. 2011](https://academic.oup.com/beheco/article/22/2/392/208177) · [RIKEN 2023 (Mishina et al., Curr. Biol.)](https://www.riken.jp/en/news_pubs/research_news/pr/2023/20231020_1/index.html) · [BugBitten summary](https://blogs.biomedcentral.com/bugbitten/2023/11/10/horizontal-gene-transfer-explains-the-origin-of-parasite-molecules-that-manipulate-host-behaviour/) |
| In the water Doodle slides out of Pickle and swims off to find a mate | ✅ | [UC IPM](https://ipm.ucanr.edu/home-and-landscape/horsehair-worms/) |
| If she gets back to dry land she can survive | ✅ | [Ponton et al. (PMC3071748)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3071748) |
| New worm eggs hatch in the pond; tiny larvae are swallowed by young insects | ✅ | [UC IPM](https://ipm.ucanr.edu/home-and-landscape/horsehair-worms/) · [UF/IFAS IN274](https://edis.ifas.ufl.edu/publication/IN274/pdf) |
| They grow up, fly to land and wait for the next cricket | ✅ | [Minnesota DNR](https://dnr.state.mn.us/mcvmagazine/issues/2017/jul-aug/horsehair-worm.html) |
| Shown on screen: adult mayfly resting with wings flat over the abdomen | ❌ mayflies rest with wings upright, pressed together over the back | standard entomology (e.g. [Wikipedia: Mayfly](https://en.wikipedia.org/wiki/Mayfly)) |
| Shown on screen: female Pickle with an egg-laying spike and no chirping | ✅ | CLAUDE.md / general entomology |

I ran `judge_kit`, and the review packet is in `C:\Users\yarde\projects\teenyology\episodes\e001_pickle_doodle\review\judge\` (`packet.md`, 16 contact sheets, 79 key frames, 14 safe-zone overlays). I didn't change any project files. The temporary frame crops I made to check the caption overlap, the jump and the larva being eaten have been deleted.
