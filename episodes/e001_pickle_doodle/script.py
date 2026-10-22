"""Episode 001 narration, v4 (judge fixes: wandering, Later, grow up). v2 (livelier rewrite, read by Miles). v1 is kept in script_v1_remi.py.
Pauses are seconds of silence after each line."""
from engine.voice import Line

SCRIPT = [
    Line("pickle", "This is Pickle. She's a cricket...", 0.35),
    Line("hook", "and she's about to do something no cricket should ever do.", 0.9),
    Line("pixie1", "This is Pixie. She's a mayfly.", 0.4),
    Line("pixie2", "She grew up underwater, in a pond. Now, at the very end of her short life, she's landed on the shore.", 0.8),
    Line("doodle1", "And this is Doodle. A horsehair worm, no bigger than a speck...", 0.35),
    Line("doodle2", "hiding inside Pixie. Waiting.", 1.0),
    Line("eat", "Pickle finds Pixie... and gobbles her up. Doodle included.", 1.0),
    Line("grow1", "Inside Pickle, Doodle grows. Quietly. Week after week.", 0.45, take=1),  # take 0 paused after "Inside"
    Line("grow2", "Until he's several times longer than she is, wound up tight inside her body.", 1.0),
    Line("problem1", "There's just one problem.", 0.5),
    Line("problem2", "Doodle needs water to find a mate. And Pickle? Pickle lives on land.", 1.0),
    Line("drawn", "So something strange happens. Pickle starts wandering... restless... until she finds the water.", 0.45),
    Line("how", "Is Doodle steering her? Scientists think so... but how he does it is still a mystery.", 0.9),
    Line("splash", "", 1.3, sfx="splash"),  # owner prefers a real splash sound to the narrator saying it
    Line("escape", "In the water, Doodle slides out of Pickle, and swims off to find a mate.", 0.9),
    Line("survive", "And Pickle? If she can scramble back to dry land... she can actually survive.", 1.1),
    Line("cycle1", "Later, a new batch of worm eggs hatches in the pond.", 0.45),
    Line("cycle2", "The tiny larvae get swallowed by young insects, like Pixie once was.", 0.45),
    Line("cycle3", "They grow up, fly to land... and wait for the next hungry cricket.", 1.2),
]

# Sound effects anchored to the narration: (line id, word in that line or None = line start, effect, gain, offset s).
# Used by both the narration preview and the final video, so the timing is identical.
SFX = [
    ("pickle", "Pickle", "sparkle", 0.10, 0.0),
    ("hook", "never", "pop", 0.12, 0.3),
    ("pixie1", "Pixie", "sparkle", 0.10, 0.0),
    ("pixie2", "underwater", "bubbles", 0.10, 0.0),
    ("pixie2", "landed", "pop", 0.10, 0.0),
    ("doodle1", "Doodle", "shimmer", 0.08, 0.0),
    ("doodle1", "speck", "blip", 0.12, 0.0),
    ("eat", "gobbles", "crunch", 0.24, 0.0),
    ("eat", "gobbles", "crunch", 0.20, 0.25),
    ("eat", "gobbles", "crunch", 0.18, 0.5),
    ("eat", "included", "gulp", 0.35, 0.0),
    ("grow1", "grows", "riser", 0.06, 0.0),
    ("grow2", "several", "whoosh", 0.18, -0.1),
    ("grow2", "wound", "whoosh", 0.16, 0.0),
    ("problem1", None, "pop", 0.12, 0.0),
    ("problem2", "water", "bubbles", 0.10, 0.0),
    ("how", "steering", "pop", 0.18, 0.0),
    ("how", "mystery", "shimmer", 0.07, 0.0),
    ("splash", None, "boing", 0.16, -1.05),  # take-off of the (slower) jump
    ("escape", "slides", "slurp", 0.12, 0.0),
    ("escape", "swims", "bubbles", 0.14, 0.0),
    ("survive", "scramble", "ruffle", 0.15, 0.0),
    ("survive", "survive", "sparkle", 0.12, 0.0),
    ("cycle1", "hatches", "bubbles", 0.12, 0.0),
    ("cycle2", "swallowed", "gulp", 0.2, 0.0),
    ("cycle3", "fly", "flap", 0.05, 0.0),
    ("cycle3", "cricket", "sparkle", 0.1, 0.3),
]
