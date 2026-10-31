"""Episode 003 narration — Biscuit, Poppy & Dilly (Dirofilaria immitis, the dog heartworm).

Pauses are seconds of silence after each line. "|" marks a caption line break (never spoken).
Every claim is checked in facts.md; the hedges there are load-bearing:
  - never "heartworms don't live in the heart": most settle in the lung arteries, heavy infections reach the heart
    (Dilly herself settles in the lung arteries — that's fine, she's one worm)
  - female length "up to thirty centimetres" (sources: 25–30 cm)
  - no counts of babies, no male length, no meaning for "immitis"
  - never "can't grow up without a dog": coyotes, foxes, wolves (and sometimes cats) are hosts too
  - no medicine / prevention talk (owner), no "L3/L4" in the narration (labels on the cycle card only)
"""
from engine.voice import Line

SCRIPT = [
    # ---- hook (owner picked option 2; reworded after judge pass 1, owner approved the new wording)
    Line("hook", "This worm grows up | inside two animals: | a dog... and a mosquito.", 0.9),  # judge pass 1: "can't grow up without a dog" overstated the host range

    # ---- meet them
    Line("biscuit", "This is Biscuit. He's a dog, | napping in the sun.", 0.5),
    Line("poppy", "This is Poppy. She's a mosquito. | Only females bite. | They need blood for their eggs.", 0.6),
    Line("dilly", "And Poppy is carrying someone. | This is Dilly. She's a heartworm.", 0.8),

    # ---- how Dilly got into Poppy
    Line("past", "Dilly began as a baby worm | in another dog's blood. | Poppy sipped her up.", 0.5),
    Line("grow", "Inside Poppy, she grew | for two weeks, then crawled down | to her mouthparts.", 0.8),

    # ---- the bite (the sound does it)
    Line("bite", "", 1.0, sfx="whine"),
    Line("drop", "Poppy doesn't inject her. | Dilly spills onto the skin | in a tiny drop... | and wriggles in through the bite.", 0.9),

    # ---- the long walk
    Line("walk", "Under the skin, she molts, | then travels for about two months. | Slowly. Quietly.", 0.7),

    # ---- the ride
    Line("ride", "One last molt, | and she slips into a blood vessel. | The blood carries her to the heart.", 0.6),

    # ---- the turn
    Line("turn", "But the heart is just a stop on the way.", 0.5),
    Line("home", "Dilly settles in the arteries | of the lungs, right next door.", 1.0),

    # ---- grown up
    Line("long", "Here, she grows to her full size: | up to thirty centimetres long.", 0.8),
    Line("male", "She isn't alone. | A male has made it here too.", 0.6),
    Line("babies", "Months later, Dilly has babies. | Tiny worms, drifting in Biscuit's blood.", 0.9),

    # ---- the problem
    Line("need", "But they can't grow up | inside Biscuit. | They need a mosquito.", 1.0),

    # ---- the cycle closes
    Line("again", "So they wait... | until a mosquito comes for a sip. | And the journey begins again.", 0.9),
    Line("button", "A dog. A mosquito. | And a worm that lives in both.", 1.4),
]

# Sound effects anchored to the narration: (line id, word in that line or None = line start, effect, gain, offset s).
# Used by both the narration preview and the final video, so the timing is identical.
# Never anchor to a word that appears twice in its line.
SFX = [
    ("hook", "worm", "shimmer", 0.07, 0.0),
    ("hook", "mosquito", "whine", 0.20, 0.1),
    ("poppy", "Poppy", "whine", 0.18, 0.0),
    ("dilly", "Dilly", "sparkle", 0.10, 0.0),
    ("past", "sipped", "slurp", 0.12, 0.0),
    ("grow", "crawled", "blip", 0.10, 0.0),
    ("bite", None, "tick", 0.12, 0.55),               # the tiny moment of the bite, after the whine
    ("drop", "drop", "blip", 0.11, 0.0),
    ("drop", "wriggles", "slurp", 0.09, 0.0),
    ("walk", "molts", "pop", 0.11, 0.0),
    ("walk", "Slowly", "tick", 0.07, 0.0),            # the day counter ticking (judge: footsteps on a legless worm)
    ("walk", "Quietly", "tick", 0.06, 0.0),
    ("ride", "molt", "pop", 0.11, 0.0),
    ("ride", "carries", "whoosh", 0.09, 0.0),
    ("ride", "heart", "chime", 0.08, 0.0),
    ("turn", "stop", "whoosh", 0.07, 0.0),
    ("home", "lungs", "sparkle", 0.11, 0.0),
    ("long", "full", "shimmer", 0.08, 0.0),
    ("male", "male", "pop", 0.10, 0.0),
    ("babies", "babies", "sparkle", 0.11, 0.0),
    ("need", "mosquito", "whine", 0.15, 0.1),
    ("again", "sip", "slurp", 0.11, 0.0),
    ("again", "begins", "shimmer", 0.08, 0.0),
    ("button", "both", "chime", 0.10, 0.1),
]
