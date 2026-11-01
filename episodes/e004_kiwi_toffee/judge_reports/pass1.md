# Judge pass 1 — E004 Kiwi & Toffee (2026-11-01)

## Verdict
Strong, well-hedged script on a hard topic, clear hook, good caption rhythm, correct larval anatomy, and a belly card
that makes the "tail flap" idea legible. Not publishable as-is: the key beat ("a sac pushes out") happened behind the
tag that named it; the needle close-up carried a rendering bug (a green block inside Kiwi for 6 s); and the narration
order taught that moulting stops at infection, then had Kiwi's body change shape months later, which a crab cannot do
without moulting (the literature places moult arrest *at* externa emergence).

Scorecard: Facts 7 · Science visuals 8 · Story clarity 8 · Visual polish 6 · UI/UX 7 · Pacing & audio 8 · Overall 7

## Must fix
1. [39.6–42.4 s] "a sac / under his tail flap" tag sat exactly over the sac while it emerged (repeat ×5 of "every
   narrated beat needs a visual payoff"; also "tags must add information, not repeat the caption").
   → **Fixed**: tag moved up-right of the sac, no pointer, sub "Toffee, grown up".
2. [30–38 s vs 46–53 s] "he'll never shed his shell again. Never grow." said at infection; then "Months later" his
   body changes shape. Moulting stops when the externa emerges; the crab moults (and feminises) during the internal
   phase. Sources: Zoological Studies 64:13 ("molting usually stops when an externa emerges"); Kristensen 2012;
   Høeg 1995 via Campos 2022. → **Needs owner decision** (re-voice two lines, see proposal in the chat log).
3. [18–24 s] Green block hanging inside Kiwi under the needle: the "push" mask rectangle stayed over the pink
   cut-away after the needle was in. → **Fixed**: the needle is drawn to length (`draw_kentrogon(needle=)`), no mask.

## Should fix
1. s_toffee below the motion baseline, speck invisible → **Fixed**: push-in, Kiwi's eyes follow her, glint on the speck.
2. Crossfades between two shots of the same crab at different positions (burst→turn, fine→months) → **Fixed**: cuts.
3. Four location switches in 19 s around the belly cards → **Fixed**: the claws beat stays on the card; one card
   from "body" to "males" with a continuous push (0.94→1.48) and cuts in/out.
4. Right dwarf male entered inside the app's right rail → **Fixed**: both start inside x 80–880.
5. Launch rock put Kiwi's right legs and a third of the larvae under the right rail → **Fixed**: climb target x 720,
   camera focus x 560 at z 1.0, spread 340.
6. "a mother crab's eggs" label on Kiwi's eye stalk; land lens over his eye → **Fixed**: label y 990, lens +50 px up.
7. Shelter label said "her" (narration: "the sac") → **Fixed**: "the wide flap shelters the sac".

## Nice to have
- Voice at 1.65 s → **Fixed**: teaser lead 1.35 s. Teaser label doubled with the caption → labels fade on "they".
- End card visually frozen (0.97→1.02 push) → **Fixed**: 0.94→1.12 push and Kiwi with the sac above the title.
- Larvae appeared as a heap below the sac → **Fixed**: they rise straight out of the opening.
- "off to find crabs of their own": nauplii moult into cyprids first (~5 days); fine as a simplification. Not changed.
- A 1 s belly inset at "under his tail flap" would settle where the sac sits earlier. Not done.

## What works
Hook on frame 0; captions carry the story; hedges in the voice; correct cypris/nauplius anatomy; the hinged flap
card is the clearest "tail flap" explanation the series has had; SFX modest and word-anchored; −14.0 LUFS,
true peak −1.7 dB, no silences, no black frames.

## Fact-check table
| Claim | Verdict | Source |
|---|---|---|
| Sacculina is a barnacle (Rhizocephala) | OK | WP-Sc; Campos 2022 |
| cypris lands, sheds shell, hollow needle, injects herself | OK | Glenner & Høeg 1995 via Campos; WP-Sc; ADW |
| "a soft spot in his shell" (site unnamed) | OK, hedged | facts #4 |
| roots through the body, feeds from his blood | OK | Campos 2022 |
| "never shed his shell again / never grow" said at infection | **Misleading by order** | Zool Stud 64:13; Kristensen 2012; Høeg 1995 |
| "never have babies of his own" | OK, hedged | Mouritsen 2018; Campos 2022 |
| months later, sac under the tail flap where a mother carries eggs | OK | MarLIN; Campos 2022 |
| tail flap wide and round; claws small | OK | Kristensen 2012 |
| "scientists think the wide flap shelters the sac" | OK, hedged | Kristensen 2012 |
| tiny males slip into the sac; it fills with eggs | OK | SeaLifeBase; Campos (Delage 1884) |
| still a boy; behaves like a mother; cleans, guards | OK | ADW; Campos (Høeg & Lützen 1995) |
| climbs, bobs, fans; cloud of larvae | OK | WP-Sc; ADW; Campos |
| "off to find crabs of their own" | fine, imprecise (cyprids do the finding) | ADW |
| brood after brood | OK | Campos (Thresher 2000) |
| "Toffee is part of him" for life | OK | Mouritsen 2018; Kristensen 2012 |
| end card species | OK | MarLIN |
| five teeth, three lobes, narrow→wide flap | OK | WP-Cm; WSG |
