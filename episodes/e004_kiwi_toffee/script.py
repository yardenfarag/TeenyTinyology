"""Episode 004 narration — Kiwi & Toffee (the parasitic barnacle Sacculina carcini, on a shore crab).

Pauses are seconds of silence after each line. "|" marks a caption line break (never spoken).
Every claim is checked in facts.md; the hedges there are load-bearing:
  - never name where the larva settles (antenna / seta / joint: sources differ) — "a soft spot in his shell"
  - never a number of months for the hidden phase (5–34 months; "at least 33 months") — "months later"
  - "never have babies of his own", never a mechanism (male testes were found intact in one study)
  - the "never shed his shell again" line comes AFTER the sac is out: the crab keeps moulting (and its flap widens)
    during the hidden months; moulting stops at externa emergence (judge pass 1)
  - the change is BOTH: his body really changes shape (wide abdomen, small claws: Kristensen 2012) AND he behaves
    like a brooding mother (Høeg & Lützen 1995). He is not turned into a female — "He's still a boy."
  - "the wide flap shelters the sac" is the authors' hypothesis — always "scientists think"
  - no egg counts, no number of dwarf males, no prevalence, no "controls his brain" / "mating dance"
  - "tail flap" = the crab's abdomen; "sac" = the externa; "shed his shell" = moult (owner: never "moult")
  - "Toffee is part of him" for life: the roots are permanent; the sac itself can drop off and leave a scar (#14),
    so the line names Toffee, not the sac
"""
from engine.voice import Line

SCRIPT = [
    # ---- hook
    Line("hook", "This crab is guarding a clutch of eggs. | And they aren't even his.", 0.9),  # owner: "his" already says he's a boy

    # ---- meet them
    Line("kiwi", "This is Kiwi. He's a shore crab.", 0.5),
    Line("toffee", "And this speck is Toffee. | She's a barnacle. | Not that you'd ever guess.", 0.8),

    # ---- the needle (the sound does the injection)
    Line("land", "She lands on Kiwi | and finds a soft spot in his shell.", 0.5),
    Line("needle", "She sheds her own shell, | pushes a tiny hollow needle | through... and injects herself.", 1.0),

    # ---- roots
    Line("roots", "Inside Kiwi, she grows roots. | Through his whole body. | And drinks from his blood.", 0.8),
    Line("fine", "Kiwi looks fine. | But he'll never have babies of his own.", 0.9),  # judge pass 1: the shell beat moved after the sac (moulting stops when the sac is out)

    # ---- the sac
    Line("months", "Months later, a sac pushes out | under his tail flap. | Right where a mother crab | carries her eggs.", 0.9),

    # ---- the change: his BODY changes shape...
    Line("body", "And Kiwi's body changes. | His narrow tail flap grows wide and round, | the shape a mother crab has.", 0.6),
    Line("claws", "His claws stay small. | Scientists think the wide flap | shelters the sac.", 0.9),
    Line("shell", "And now the sac is out, | he'll never shed his shell again. | Never grow.", 0.9),  # owner: not "moult"; judge pass 1 placed it here

    # ---- her babies
    Line("males", "Tiny male larvae slip into the sac... | and it fills with eggs. | Toffee's eggs.", 0.8),

    # ---- ...and he BEHAVES like a mother
    Line("still", "Kiwi is still a boy. | But now he behaves like a mother.", 0.7),
    Line("care", "He cleans the sac. He guards it. | He treats Toffee's eggs as his own.", 0.8),

    # ---- the launch (the sound does the hatching)
    Line("launch", "When the larvae are ready, | he climbs up high... | and bobs... and fans.", 0.3),
    Line("burst", "", 1.3, sfx="bubbles"),
    Line("cloud", "A cloud of baby barnacles, | off to find crabs of their own.", 0.9),

    # ---- the turn + cycle
    Line("turn", "Toffee doesn't just take Kiwi's food. | She takes his whole job of making babies... | and hands him hers.", 1.0),
    Line("end", "And Kiwi raises them all. | Brood after brood.", 0.9),  # owner: the "a family that isn't his" line sounded weird
    Line("life", "For the rest of his life, | Toffee is part of him.", 1.4),  # owner asked for this beat (facts #6, #14)
]

# Sound effects anchored to the narration: (line id, word in that line or None = line start, effect, gain, offset s).
# Used by both the narration preview and the final video, so the timing is identical.
# Never anchor to a word that appears twice in its line.
SFX = [
    ("hook", "eggs", "sparkle", 0.09, 0.0),
    ("hook", "even", "blip", 0.10, 0.1),
    ("kiwi", "Kiwi", "click", 0.07, 0.0),
    ("toffee", "speck", "blip", 0.10, 0.0),
    ("toffee", "barnacle", "sparkle", 0.09, 0.0),
    ("land", "lands", "tick", 0.09, 0.0),
    ("needle", "sheds", "pop", 0.09, 0.0),
    ("needle", "needle", "click", 0.08, 0.1),
    ("needle", "injects", "slurp", 0.11, 0.1),
    ("roots", "roots", "scratch", 0.07, 0.0),
    ("roots", "drinks", "slurp", 0.08, 0.0),
    ("months", "pushes", "pop", 0.10, 0.1),
    ("months", "sac", "chime", 0.07, 0.0),
    ("body", "wide", "boing", 0.07, 0.0),
    ("claws", "small", "blip", 0.07, 0.0),
    ("shell", "shell", "tick", 0.07, 0.0),
    ("shell", "grow", "tick", 0.06, 0.0),
    ("males", "slip", "blip", 0.10, 0.0),
    ("males", "fills", "sparkle", 0.10, 0.0),
    ("still", "mother", "chime", 0.07, 0.0),
    ("care", "cleans", "ruffle", 0.09, 0.0),
    ("launch", "climbs", "footsteps", 0.07, 0.0),   # a crab has legs — footsteps are allowed here
    ("launch", "bobs", "bubbles", 0.08, 0.0),
    ("burst", None, "whoosh", 0.10, 0.0),
    ("burst", None, "shimmer", 0.09, 0.2),
    ("cloud", "cloud", "sparkle", 0.09, 0.0),
    ("turn", "hers", "chime", 0.09, 0.1),
    ("end", "all", "sparkle", 0.09, 0.0),
    ("life", "him", "chime", 0.10, 0.1),
]
