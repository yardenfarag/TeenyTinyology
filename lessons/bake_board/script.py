"""Board bake: a few seconds of a whiteboard lesson to choose the writing tool (hand / marker / none)."""
from engine.voice import Line

SCRIPT = [
    Line("l1", "Most bacteria come in one of three basic shapes.", 0.5),
    Line("l2", "Round ones are called cocci, from the Greek word for berry.", 0.5),
    Line("l3", "Rods are bacilli.", 0.4),
    Line("l4", "And spirals... are spirilla.", 0.8),
    Line("l5", "Not the most imaginative names. But you'll never forget them.", 1.0),
]
