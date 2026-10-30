"""Episode 002 narration — Roly & Mango (Cymothoa exigua, the tongue-eating isopod).

Pauses are seconds of silence after each line. "|" marks a caption line break (never spoken).
Every claim is checked in facts.md; the hedges there are load-bearing:
  - never say where the pair mates, only who the mate is (the other one, on the gills)
  - never say Roly feeds for life — the blood-drinking belongs to the tongue-destroying phase only
  - the "she may feed better" ending is the scientists' hypothesis, and is framed as theirs
  - two isopods per fish, never a crowd (Brusca 1981)
"""
from engine.voice import Line

SCRIPT = [
    # ---- hook: the mouth, and something in it
    Line("hook1", "Open this fish's mouth...", 0.35),
    Line("hook2", "and something looks back.", 0.9),

    # ---- who they are
    Line("mango", "This is Mango. She's a spotted rose snapper.", 0.5),
    Line("roly", "And this is Roly. | She's an isopod — a crustacean, | more shrimp than insect.", 0.8),

    # ---- how she got here, and the sex change
    Line("arrive", "Roly arrived as a speck, | and slipped in | through Mango's gills.", 0.7),
    Line("two", "Two of them found Mango. | Every one of them starts out male.", 0.8),
    Line("change", "Roly grew faster. | And then Roly changed.", 0.5),
    Line("female", "She became female. | And the female gets the mouth.", 1.0),

    # ---- why a parasite can do this job (the owner's fact, placed as the reason)
    Line("tongue1", "Now, a fish's tongue is nothing like yours. | It's a bony pad. | No muscle of its own.", 0.6, take=1),  # take 0 started mid-sound
    Line("tongue2", "Its job is to press food | against the teeth in the roof of the mouth.", 0.9),

    # ---- the swap, drawn as a gentle fade
    Line("grip", "Roly clamps onto the base of Mango's tongue, | and drinks the blood that feeds it.", 0.8),
    Line("fade", "Without that blood, | the tongue slowly shrinks... | and falls away.", 1.0),
    Line("place", "She doesn't eat it. | She takes its place.", 1.0),
    Line("feet", "Fourteen hooked feet, | holding on to what's left.", 0.8),

    # ---- the payoff: the scratches on her back
    Line("eats", "And Mango? | Mango goes back to eating.", 0.9),
    Line("proof", "When scientists opened up fish like Mango, | they found the teeth above | had scuffed Roly's back.", 0.9),
    Line("press", "Mango had been pressing her food | against her.", 1.1),

    # ---- the honest ending
    Line("hedge1", "Is that bad for Mango? | Nobody's sure.", 0.5),
    Line("hedge2", "But a fish with Roly | may feed better than a fish | with no tongue at all.", 1.0),

    # ---- the cycle closes
    Line("pouch", "Under Roly's belly, a pouch. | More than four hundred eggs.", 0.5),
    Line("father", "And the father? | The other one who found Mango. | Still back on the gills.", 0.9),
    Line("hatch", "One day the pouch opens. | Hundreds of specks swim out, | each one looking for a mouth.", 1.1),
    Line("stay", "And Mango will carry Roly | for the rest of her life.", 0.9),
    Line("button", "She still has a tongue. | It just isn't hers.", 1.4),
]

# Sound effects anchored to the narration: (line id, word in that line or None = line start, effect, gain, offset s).
# Used by both the narration preview and the final video, so the timing is identical.
# Never anchor to a word that appears twice in its line.
SFX = [
    ("hook1", "mouth", "bubbles", 0.10, 0.0),
    ("hook2", "looks", "shimmer", 0.07, 0.0),
    ("hook2", "back", "blip", 0.13, 0.05),
    ("mango", "Mango", "sparkle", 0.10, 0.0),
    ("roly", "Roly", "shimmer", 0.08, 0.0),
    ("arrive", "speck", "blip", 0.11, 0.0),
    ("arrive", "slipped", "slurp", 0.10, 0.0),
    ("arrive", "gills", "bubbles", 0.12, 0.0),
    ("two", "Two", "pop", 0.12, 0.0),
    ("change", "changed", "riser", 0.07, -0.35),
    ("female", "became", "sparkle", 0.11, 0.0),   # "female" appears twice in the line
    ("tongue1", "pad", "pop", 0.09, 0.0),
    ("tongue2", "teeth", "click", 0.07, 0.0),
    ("grip", "clamps", "click", 0.13, 0.0),
    ("grip", "drinks", "slurp", 0.16, 0.0),
    ("fade", "shrinks", "shimmer", 0.09, 0.0),
    ("place", "place", "pop", 0.14, 0.0),
    ("feet", "feet", "click", 0.12, 0.0),
    ("feet", "feet", "click", 0.09, 0.14),
    ("eats", "eating", "crunch", 0.20, 0.0),
    ("eats", "eating", "crunch", 0.15, 0.30),
    ("proof", "scuffed", "scratch", 0.18, 0.0),
    ("press", "pressing", "crunch", 0.13, 0.0),
    ("pouch", "eggs", "sparkle", 0.12, 0.0),
    ("father", "gills", "bubbles", 0.10, 0.0),
    ("hatch", "opens", "pop", 0.11, 0.0),
    ("hatch", "swim", "bubbles", 0.13, 0.0),
    ("hatch", "mouth", "blip", 0.11, 0.15),
    ("stay", "life", "shimmer", 0.08, 0.0),
    ("button", "tongue", "pop", 0.11, 0.0),
    ("button", "hers", "sparkle", 0.12, 0.1),
]
