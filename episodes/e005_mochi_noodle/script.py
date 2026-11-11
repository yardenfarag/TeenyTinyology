"""Episode 005 narration — Mochi, Pip & Noodle (the flea tapeworm Dipylidium caninum, a cat flea and a cat).

Pauses are seconds of silence after each line. "|" marks a caption line break (never spoken).
Every claim is checked in facts.md; the hedges there are load-bearing:
  - the warmth of Mochi's skin (not the blood meal) finishes the worm inside Pip (Pugh 1987) — never "the blood feeds it"
  - "longer than a ruler" with "can" — adult length 10–70 cm
  - no number of weeks for Noodle to mature (2–3 weeks vs ~1 month)
"""
from engine.voice import Line

SCRIPT = [
    # ---- hook
    Line("hook", "There's a grain of rice | on this cat's fur. | And it's moving.", 0.9),

    # ---- meet Mochi, reveal the grain
    Line("mochi", "This is Mochi. She's a cat.", 0.5),
    Line("grain", "That grain isn't rice. | It's a tiny piece of a tapeworm... | packed with eggs.", 0.8),
    Line("dry", "It dries, breaks open, | and the eggs spill into Mochi's bed.", 0.6),

    # ---- Pip the larva
    Line("pip", "Down in the bed lives Pip. | He's a flea. | Well... a baby flea.", 0.5),
    Line("eats", "Pip eats the crumbs he finds. | Including a tapeworm egg.", 0.8),
    Line("inside", "Inside Pip, the egg hatches. | A young worm slips into his body... | and waits.", 0.8),

    # ---- grown-up Pip (the sound does the jump)
    Line("cocoon", "Pip spins a cocoon, | and comes out a grown-up flea.", 0.4),
    Line("jump", "", 1.3, sfx="boing"),
    Line("warm", "In Mochi's warm fur, | the tiny worm inside him | gets ready.", 0.9),

    # ---- the swallow (owner: the "Itch... lick... lick..." + silent gulp beat felt weird -> plain sentences)
    Line("itch", "Pip's bite itches. | So Mochi licks her fur clean...", 0.4),
    Line("swallow", "and swallows Pip, | along with the worm inside him.", 0.9),

    # ---- Noodle
    Line("noodle", "This is Noodle. She's a tapeworm.", 0.5),
    Line("hooks", "She holds on to Mochi's gut | with a crown of tiny hooks | and four suckers.", 0.7),
    Line("mouth", "Noodle has no mouth. | She soaks up Mochi's food | through her skin.", 0.9),
    Line("grow", "And she grows. | Segment after segment. | She can get longer than a ruler.", 0.9),

    # ---- the cycle
    Line("eggs", "Each new segment | fills with eggs.", 0.5),
    Line("leave", "The oldest ones break off, | crawl out... and end up on Mochi's fur.", 0.8),
    Line("cycle", "Little grains of rice. | Waiting for the next Pip.", 1.4),  # owner: closing line (vet + "round and round" cut)
]

# Sound effects anchored to the narration: (line id, word in that line or None = line start, effect, gain, offset s).
# Never anchor to a word that appears twice in its line.
SFX = [
    ("hook", "moving", "blip", 0.09, 0.0),
    ("mochi", "Mochi", "purr", 0.06, 0.0),
    ("grain", "tapeworm", "sparkle", 0.08, 0.0),
    ("dry", "breaks", "crunch", 0.06, 0.0),
    ("dry", "spill", "pop", 0.08, 0.1),
    ("pip", "Pip", "blip", 0.09, 0.0),
    ("eats", "crumbs", "tick", 0.07, 0.0),
    ("eats", "egg", "slurp", 0.08, 0.0),
    ("inside", "hatches", "pop", 0.08, 0.0),
    ("inside", "slips", "whoosh", 0.05, 0.0),
    ("cocoon", "spins", "shimmer", 0.06, 0.0),
    ("cocoon", "grown", "sparkle", 0.08, 0.0),
    ("jump", None, "boing", 0.10, 0.1),
    ("warm", "ready", "chime", 0.07, 0.1),
    ("itch", "itches", "scratch", 0.06, 0.0),
    ("itch", "licks", "ruffle", 0.06, 0.0),
    ("swallow", "swallows", "gulp", 0.08, 0.15),
    ("noodle", "Noodle", "sparkle", 0.09, 0.0),
    ("hooks", "hooks", "click", 0.07, 0.0),
    ("hooks", "suckers", "pop", 0.07, 0.0),
    ("mouth", "soaks", "slurp", 0.07, 0.0),
    ("grow", "Segment", "blip", 0.07, 0.0),
    ("grow", "ruler", "pop", 0.07, 0.0),
    ("eggs", "fills", "sparkle", 0.08, 0.0),
    ("leave", "break", "pop", 0.08, 0.0),
    ("cycle", "grains", "sparkle", 0.08, 0.0),
    ("cycle", "Pip", "chime", 0.09, 0.1),
]
