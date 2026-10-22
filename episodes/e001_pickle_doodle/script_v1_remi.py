"""Approved narration for episode 001 (owner-approved 2026-10-22). Pauses are seconds of silence after each line."""
from engine.voice import Line

SCRIPT = [
    Line("pickle", "This is Pickle. She's a cricket.", 0.8),
    Line("pixie1", "This is Pixie. She's a mayfly.", 0.5),
    Line("pixie2", "She spent her early life in a pond, and now she's flown to land at the end of her short life.", 0.8),
    Line("doodle1", "And this is Doodle, a horsehair worm.", 0.45),
    Line("doodle2", "Right now he's tiny, hidden inside Pixie.", 0.9),
    Line("eat", "When Pickle finds Pixie, she eats her, and swallows Doodle too.", 0.9),
    Line("grow1", "Inside the cricket, Doodle grows.", 0.45),
    Line("grow2", "Eventually he's several times longer than Pickle, coiled up tight inside her body.", 0.9),
    Line("water1", "But horsehair worms can only breed in water.", 0.45),
    Line("water2", "And crickets live on land.", 0.9),
    Line("drawn", "As Doodle matures, Pickle's behavior changes, and she's drawn toward water.", 0.45),
    Line("how", "Scientists are still working out exactly how.", 0.9),
    Line("escape", "Once Pickle is in the water, Doodle slips out and swims away to find a mate.", 0.9),
    Line("survive", "Pickle can survive, if she makes it back to dry land.", 1.0),
    Line("cycle1", "In the pond, the worms' eggs hatch.", 0.45),
    Line("cycle2", "Young insects, like Pixie once was, swallow the larvae.", 0.45),
    Line("cycle3", "Later they fly to land, and the cycle begins again.", 1.2),
]
