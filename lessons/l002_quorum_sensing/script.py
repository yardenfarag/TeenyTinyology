"""L002 — Quorum sensing. Narrator: Miles. Every claim is sourced in facts.md.

Line ids are grouped by board region (plan.md): a the glowing squid · b sensing a crowd · c the circuit ·
d languages · e attack, or leave · f jamming, and where the picture breaks · w wrap-up.
"""
from engine.voice import Line

SCRIPT = [
    # A — the glowing squid (hook)
    Line("a1", "On a moonlit night, this squid has a problem: its own shadow.", 0.5),
    Line("a2", "This is the Hawaiian bobtail squid. It's active at night. "
               "And seen from below, it would be a dark shape against the moon.", 0.5),
    Line("a3", "So it glows from underneath, matching the moonlight above. And the shadow disappears.", 0.6),
    Line("a4", "Biologists call this counter-illumination.", 0.6),
    Line("a5", "But the light isn't made by the squid. It's made by bacteria.", 0.5),
    Line("a5b", "They live in a pouch on the squid's underside, called the light organ. "
                "It even has a reflector, and a lens, to aim their glow downwards.", 0.5),
    Line("a6", "They're called Aliivibrio fischeri. Until 2007, they were Vibrio fischeri.", 0.4),
    Line("a6b", "Then a study of their DNA showed they sit on a branch of their own, so they got a new name: "
                "Aliivibrio. The other Vibrio.", 0.5),
    Line("a6c", "Many researchers still use the old one.", 0.6),
    Line("a7", "And here's the strange part. These bacteria only glow when there are lots of them. "
               "Alone in the open sea, they stay dark.", 0.8),
    Line("a8", "So how does a single cell know it's in a crowd?", 0.9),

    # B — sensing a crowd
    Line("b1", "Each cell leaks a little signal molecule into the water around it.", 0.4),
    Line("b2", "When cells are few, the signal drifts away.", 0.4),
    Line("b3", "When many cells are packed together, it builds up.", 0.5),
    Line("b4", "And past a certain level, a threshold, the genes switch on across the whole crowd.", 0.8),
    Line("b5", "This is called quorum sensing.", 0.4),
    Line("b6", "A quorum is the smallest number of members who must be present before a meeting can make decisions.", 0.4),
    Line("b7", "The word is Latin, for 'of whom'.", 0.6),
    Line("b8", "The signal itself is called an autoinducer.", 0.4),
    Line("b9", "The first clue came in 1970, from glowing marine bacteria. "
               "Their light only switched on once the cells had built up something in their own broth: "
               "a substance they made themselves.", 0.7),

    # C — the circuit
    Line("c1", "So what's going on inside one of those cells?", 0.4),
    Line("c2", "An enzyme called LuxI makes the signal. It's called an AHL, short for acyl-homoserine lactone: "
               "a small ring, with a fatty tail.", 0.5),
    Line("c3", "In the squid's bacteria, it's small enough to slip straight through the cell's membrane. In and out.", 0.5),
    Line("c4", "Inside, a protein called LuxR waits.", 0.4),
    Line("c5", "When enough signal has built up, LuxR grabs it, and switches on the light genes.", 0.4),
    Line("c6", "And one of those genes is luxI itself.", 0.4),
    Line("c7", "So the more signal there is, the more signal gets made.", 0.5),
    Line("c7b", "And the cells make this inducer themselves. That's the 'auto' in autoinducer.", 0.8),
    Line("c8", "In the open sea, the signal never builds up. Packed into the squid's light organ, it does. And they glow.", 0.6),
    Line("c9", "The bacteria pay their rent in light.", 0.5),
    Line("c10", "Every dawn, the squid evicts most of them anyway. Ninety percent or more, vented into the sea.", 0.8),
    Line("c11", "The rest regrow by nightfall.", 0.8),

    # D — languages
    Line("d1", "Not every bacterium speaks the same chemical language.", 0.4),
    Line("d2", "The squid's bacteria use AHLs. So does Pseudomonas aeruginosa.", 0.5),
    Line("d3", "Staphylococcus and Streptococcus use something else: "
               "short chains of amino acids. Tiny protein fragments.", 0.4),
    Line("d4", "The cell pumps them out, and they're mostly caught by receptors on the cell's surface.", 0.5),
    Line("d5", "And one signal, called AI-2, is made by many different kinds of bacteria.", 0.4),
    Line("d6", "Some scientists think it may work as a shared word between species. That's still debated.", 0.8),

    # E — attack, or leave
    Line("e1", "So what do bacteria do, once they know they're a crowd?", 0.5),
    Line("e2", "Pseudomonas aeruginosa uses its count to time an attack.", 0.4),
    Line("e3", "While it's few, it holds back most of its weapons.", 0.4),
    Line("e4", "Once there are enough, it switches on toxins, and enzymes that damage tissue. "
               "Virulence factors: the tools a microbe uses to cause disease.", 0.5),
    Line("e5", "And it builds a biofilm: a slimy, protected city of cells.", 0.6),
    Line("e6", "Scientists think waiting may keep it from being noticed too early. "
               "Attack with a few cells, and the immune system wins.", 0.5),
    Line("e7", "Patience, it turns out, is a virulence factor.", 1.0),
    Line("e8", "Vibrio cholerae, the bacterium behind cholera, does the opposite.", 0.4),
    Line("e9", "When there are few of them, they stick to the gut wall, and make their toxin.", 0.4),
    Line("e10", "When the crowd gets big, the same switch turns all that off. "
                "Scientists think it helps them let go, and leave.", 0.6),
    Line("e11", "And its way out of the body is the disease itself. "
                "The toxin it made earlier causes the diarrhoea that carries it out.", 1.0),
    Line("e12", "Same switch. Opposite decision.", 0.8),

    # F — jamming, and where the picture breaks
    Line("f1", "If bacteria act on a signal, can the signal be jammed?", 0.4),
    Line("f2", "It can. Some bacteria make enzymes that break the AHL's ring open. This is called quorum quenching.", 0.4),
    Line("f3", "One, from a Bacillus, was given to a bacterium that rots plants. The rot became much weaker.", 0.6),
    Line("f4", "A red seaweed from Australian waters, Delisea pulchra, makes molecules shaped like the signal. "
               "They jam the receiver.", 0.4),
    Line("f5", "And its surface stays remarkably clean of bacteria.", 0.6),
    Line("f6", "Drugs that jam the signal, instead of killing the bacteria, are being studied. "
               "None is a standard treatment yet.", 0.8),
    Line("f7", "One last thing. Bacteria don't actually count heads.", 0.4),
    Line("f8", "They sense how concentrated the signal is.", 0.4),
    Line("f9", "So a few cells in a tight space can reach the threshold. "
               "And a big crowd in open, flowing water may never reach it.", 0.5),
    Line("f10", "In one experiment, a single Staphylococcus aureus cell, sealed in a tiny droplet, "
                "switched on its quorum-sensing genes all by itself.", 0.6),
    Line("f11", "No crowd. Just a very small room.", 0.6),
    Line("f12", "The scientists think this may happen inside the body, too: "
                "when a bacterium is swallowed by an immune cell, and trapped in a tiny pocket.", 1.0),

    # W — wrap-up (zoom out to the whole board; each region lights up as it is named)
    Line("w1", "That's quorum sensing. One small molecule, building up in the dark, "
               "until a crowd of cells knows it's time.", 1.0),
]
