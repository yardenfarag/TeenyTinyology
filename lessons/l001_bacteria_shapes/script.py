"""L001 — The shapes of bacteria. Narrator: Miles. Every claim is sourced in facts.md.

Line ids are grouped by board region (plan.md): a basic shapes · b cocci together · c rods · d curves ·
e odd ones · f why shape matters · w wrap-up.
"""
from engine.voice import Line

SCRIPT = [
    # A — the basic shapes (hook)
    Line("a1", "Almost every bacterium is a single cell.", 0.4),
    Line("a2", "Most are about a micrometre across. Far too small to see.", 0.5),
    Line("a3", "And yet, under a microscope, they come in more shapes than you'd think.", 0.7),
    Line("a4", "Long before DNA tests, the microscope was all there was. "
               "And even today, a lab's first clue is the shape of the cells.", 0.7),
    Line("a5", "Round cells are cocci. From the Greek kokkos: a grain, or a berry.", 0.6),
    Line("a6", "Rod-shaped cells are bacilli. Latin for a little rod.", 0.5),
    Line("a7", "And then there are the spirals.", 0.7),
    Line("a8", "But a bacterium rarely stays alone for long.", 0.8),

    # B — cocci that stay together
    Line("b1", "Bacteria multiply by splitting in two. And sometimes, the two halves don't let go.", 0.6),
    Line("b2", "Split once and stay joined, and you get a pair. A diplococcus. Diplo means double.", 0.5),
    Line("b3", "Keep splitting in the same direction, and the pairs become chains: streptococci.", 0.4),
    Line("b4", "Streptos is Greek for pliant, or twisted. Like a chain.", 0.5),
    Line("b5", "Streptococcus pyogenes is one of these. It gives you strep throat. "
               "And, rarely, the flesh-eating infection.", 0.9),
    Line("b6", "Split in two directions, and you get a square of four. A tetrad.", 0.4),
    Line("b7", "Three directions, and you get a little package, up to a cube of eight. A sarcina.", 0.5),
    Line("b8", "And split in a new direction each time... and you get a bunch of grapes.", 0.4),
    Line("b9", "Staphylococcus. Staphyle is Greek for a bunch of grapes.", 0.5),
    Line("b10", "Which makes Staphylococcus aureus the golden grape-bunch berry.", 0.5),
    Line("b12", "It's a common cause of skin infections. And it lives quietly up the nose of about one person in four.", 0.5, take=1),
    Line("b13", "Possibly yours.", 1.0),
    Line("b14", "So the name often tells you the shape. Cocco, the berry. Strepto, the chain. Staphylo, the grapes.", 0.9),

    # C — rods
    Line("c1", "Rods form groups too. In chains, they're streptobacilli.", 0.5),
    Line("c2", "Corynebacterium snaps when it divides, instead of splitting cleanly. "
               "So its rods end up side by side, like a fence... or at angles, in Vs and Ys.", 0.7),
    Line("c3", "Some rods have quite a career.", 0.4),
    Line("c4", "Clostridium botulinum makes botulinum toxin. The most lethal biological toxin known.", 0.6),
    Line("c5", "In tiny, purified doses, it's also Botox. People pay to have it injected into their faces.", 1.0),
    Line("c6", "Between the round and the rod sits the coccobacillus: a rod so short, it's almost round.", 0.5),
    Line("c7", "Haemophilus influenzae is one. It was first described in the 1890s, by a scientist who thought it caused the flu.", 0.4),
    Line("c8", "It doesn't. Flu is caused by a virus. The name stuck anyway.", 0.8),
    Line("c9", "Yersinia pestis is another one. Small, plump, and the cause of the Black Death.", 0.4),
    Line("c10", "In the mid-1300s, it killed at least a third of Europe.", 1.0),

    # D — curves
    Line("d1", "Now, the curves.", 0.4),
    Line("d2", "A vibrio is a curved rod. A comma.", 0.4),
    Line("d3", "Its name comes from the Latin for vibrate, because it looks like it's vibrating as it swims.", 0.4),
    Line("d4", "Vibrio cholerae causes cholera. This little comma has ended a great many sentences.", 1.0, take=1),
    Line("d5", "Even now, it's thought to kill tens of thousands of people a year.", 0.8),
    Line("d6", "A spirillum is a thick, stiff spiral, with tufts of flagella at each end.", 0.5),
    Line("d7", "And a spirochete is a thin, flexible corkscrew, with a trick: its flagella are inside the cell.", 0.5),
    Line("d8", "In open water, spirochetes are slowpokes. In thick, gel-like places, they do better than you'd expect.", 0.5),
    Line("d9", "Treponema pallidum, which causes syphilis, is one. So is Borrelia, which ticks carry, "
               "and which causes Lyme disease.", 0.8),

    # E — the odd ones
    Line("e1", "And then there are the odd ones.", 0.5),
    Line("e2", "Streptomyces grows as branching threads, like a tiny fungus.", 0.4),
    Line("e3", "It makes geosmin: the earthy smell of soil after rain. "
               "And more than two-thirds of the useful antibiotics that come from nature.", 0.6),
    Line("e4", "Some bacteria are shaped like flat, six-pointed stars. They are called Allostella.", 0.5),
    Line("e5", "Caulobacter grows a stalk, with glue on the end. One of the strongest natural glues known.", 0.4),
    Line("e6", "When it divides, one daughter swims away. The other stays stuck.", 0.6),
    Line("e7", "Mycoplasma has no cell wall at all. So it has no fixed shape.", 0.5),
    Line("e8", "And some bacteria are giants.", 0.4),
    Line("e9", "Thiomargarita magnifica, described in 2022, grows to about a centimetre long. "
               "A single bacterium you can see with your own eyes.", 0.7),
    Line("e10", "One last shape is a trap.", 0.4),
    Line("e11", "Haloquadratum is a flat, square cell from very salty water. "
                "And it is not a bacterium at all. It's an archaeon.", 0.9),

    # F — why shape matters
    Line("f1", "So why have a shape at all?", 0.5),
    Line("f2", "First, something has to hold it. That's the cell wall: a tough mesh around the cell.", 0.4),
    Line("f3", "Take the wall away, and the cell goes round, or shapeless. Just like Mycoplasma.", 0.6),
    Line("f4", "Second, food. A bacterium feeds through its surface, and small cells have a lot of surface for their size. "
               "That's one big reason bacteria stay small.", 0.5, take=1),
    Line("f5", "Growing into long threads adds even more surface to feed through.", 0.6),
    Line("f6", "Third, getting around. Helicobacter pylori lives in the mucus of the stomach. "
               "Its spiral cells swim a little faster there than straight ones.", 0.5),
    Line("f7", "And scientists think shape also helps bacteria stick to things, and avoid being eaten.", 0.8),

    # W — wrap-up (zoom out to the whole board)
    Line("w1", "Spheres, rods, commas, corkscrews, stars, and giants. Every one of them, a single cell.", 0.7),
]
