# L002 — Quorum sensing

Working title: **"How bacteria sense a crowd"** (was "count themselves": the lesson itself says they do not count). About 5 minutes (owner OK, 2026-11-11).

## Objective
After this lesson you can:
- explain how a bacterium "knows" how many of its kind are around: every cell releases a small signal molecule
  (an **autoinducer**), and only when the crowd is dense enough does the signal reach a **threshold** that
  switches genes on;
- trace the classic circuit (**LuxI** makes the signal, **LuxR** catches it, the genes switch on, and the cell
  makes even more signal);
- give two examples of what bacteria do with it (glowing inside a squid; attacking, or leaving, a host), and
  say why blocking the signal interests medicine.

**Lesson type:** mechanism. One persistent diagram (a cell with its circuit) that the later steps reuse,
with a short story at the start (the glowing squid) as the hook.

## Steps
| # | Question it answers | What the viewer learns |
|---|---|---|
| 1 | How does a squid hide its shadow on a moonlit night? | Hook: the Hawaiian bobtail squid glows from below to erase its shadow; the light is made by bacteria (*Vibrio fischeri*, now *Aliivibrio fischeri*). They only glow when there are lots of them. **The real question:** how does a single cell know it's in a crowd? |
| 2 | How can a cell sense a crowd? | Each cell leaks a little signal. Few cells: it drifts away. Many cells, in a closed space: it builds up. Past a **threshold**, every cell switches on together. Board: a graph of signal vs. number of cells with a threshold line. Define **quorum** (Latin "of whom": the minimum number of members needed for a vote to count) and **autoinducer** |
| 3 | What does the circuit look like? | One cell, drawn large: **LuxI** makes the signal (an AHL, a small fatty molecule that passes through the membrane); **LuxR** waits inside; when enough signal is around, LuxR grabs it and switches on the light genes, *and* more LuxI. A loop: that's the "auto" in autoinducer. Back to the squid: in the open sea, dark; packed in the light organ, they glow. Every dawn the squid vents most of them; the rest regrow by nightfall |
| 4 | Do all bacteria speak the same language? | No. Different bacteria use different signals: *Vibrio* and *Pseudomonas* use small fatty molecules (AHLs); *Staphylococcus* and *Streptococcus* (the grapes and the chains from L001) use short chains of amino acids, tiny protein fragments. And one signal (**AI-2**) is made by many different species, so scientists think it may work as a shared, cross-species signal (hedged). No "Gram-negative/positive" wording (owner, 2026-11-11: Gram staining hasn't been taught yet) |
| 5 | What do bacteria use it for? | **Attack:** *Pseudomonas aeruginosa* keeps quiet while it's few, then switches on toxins and builds a **biofilm** once there are enough (dark humour: "patience is a virulence factor"). **Leave:** *Vibrio cholerae* does the opposite: at high numbers it switches its toxin *off*, lets go of the gut wall, and heads out (callback to L001's comma). Same switch, opposite decision |
| 6 | Can the signal be jammed, and where does the "counting" picture break? | **Quorum quenching:** some bacteria make enzymes that cut up AHLs; a red seaweed (*Delisea pulchra*) makes molecules that block the signal. Drugs that jam the signal instead of killing the bacteria are being studied, not yet in use (hedged). **Where the metaphor breaks:** bacteria don't count heads, they sense concentration. A small group in a tight space, or even one cell trapped in a tiny pocket, can cross the threshold |
| — | Wrap | zoom out to the whole board; each region lights up as it's named; outro logo over the faded board |

## The final board (6 regions, 3 × 2 frames: board 5760 × 2160)
```
 ┌──────────────────────┬──────────────────────┬──────────────────────┐
 │ A  The glowing squid │ B  Sensing a crowd   │ C  The circuit       │
 │ (logo, then erased)  │ few cells / many     │ one big cell:        │
 │ squid, moon, no      │ cells, signal dots;  │ LuxI → AHL → LuxR →  │
 │ shadow; "how does a  │ graph with a         │ light genes + more   │
 │ cell know?"          │ threshold line;      │ LuxI (loop arrow);   │
 │                      │ "quorum" etymology   │ squid: dark sea vs   │
 │                      │                      │ glowing light organ  │
 ├──────────────────────┼──────────────────────┼──────────────────────┤
 │ F  Jamming + limits  │ E  Attack, or leave  │ D  Languages         │
 │ enzyme cutting AHL;  │ Pseudomonas: quiet → │ Vibrio, Pseudomonas: │
 │ seaweed blocker;     │ toxins + biofilm;    │ AHL · Staph, Strep:  │
 │                      │                      │ peptides             │
 │ "concentration, not  │ V. cholerae: toxin   │ AI-2 : many species  │
 │ headcount" (one cell │ OFF, lets go, leaves │ (shared word?)       │
 │ in a tiny pocket)    │                      │                      │
 └──────────────────────┴──────────────────────┴──────────────────────┘
```
- Each region gets a section title (`b.title`) in navy with a gold underline, then marker drawings with labels
  beside them. Colours: blue for cells, gold for the signal molecules (they're the star of the lesson, and gold
  lets them read as "glowing"), green for "switched on", red for toxins and "switched off".
- **The signal dots are the throughline:** the same gold dots appear in every region (drifting away in B,
  crossing the membrane in C, three different shapes in D, flooding the biofilm in E, being cut in F).
- **Camera route:** A → B → C (pan right), C → D (straight down), D → E → F (pan left), then zoom out to the
  whole board. Every move goes between neighbouring regions.
- **Eraser:** the logo is wiped off region A before the squid is drawn. In B, the "few cells" sketch is not
  erased; "many cells" is drawn beside it so the contrast stays on the board.
- **Bridge to L001:** *Vibrio cholerae* is "the comma" from the shapes lesson; *Vibrio fischeri* is its glowing
  cousin.
- **Humour (dark and dry), candidates, each to be sourced:**
  - step 1: the squid's bacteria pay rent in light; every dawn the squid evicts most of them anyway.
  - step 5: *Pseudomonas* waits until there are enough of them before it attacks: "patience, it turns out, is a
    virulence factor".
  - step 5: *Vibrio cholerae* uses its crowd to decide when to leave, and its way out of the body is the disease
    itself (said calmly, about the microbe, never about patients).
  - step 6: the seaweed that has been jamming bacteria for millions of years before we thought of it (needs care:
    only if a source supports the "long before us" framing).
  The script will use the strongest two or three.

## To verify in `facts.md` (before the script)
- *V. fischeri* → *Aliivibrio fischeri* rename (and which name Wikipedia uses), the bobtail squid's
  counter-illumination, the daily venting (the share expelled at dawn), how fast the rest regrow.
- The history: autoinduction found in luminous marine bacteria around 1970 (Nealson, Platt, Hastings); the term
  "quorum sensing" coined in 1994 (Fuqua, Winans, Greenberg).
- Etymology of *quorum*.
- LuxI / LuxR / AHL roles; AHLs diffusing through the membrane; the positive-feedback loop.
- AHLs in *Vibrio* / *Pseudomonas* vs peptide signals in *Staphylococcus* (agr) / *Streptococcus*; AI-2 and
  LuxS; how firmly "interspecies signal" is established (hedge).
- *P. aeruginosa*: which virulence factors and biofilm steps are QS-controlled.
- *V. cholerae*: toxin and biofilm genes repressed at high density; detachment and exit.
- Quorum quenching: AHL lactonases (e.g. *Bacillus* AiiA); *Delisea pulchra* furanones; the status of QS-blocking
  drugs (clinical trials? none approved?).
- "Concentration, not headcount": diffusion/efficiency sensing (Redfield 2002); single-cell quorum sensing in a
  confined space (*Staphylococcus aureus*, Carnes et al. 2010).
