"""Generate (and cache) the narration, print line timings."""
import os
from engine.voice import narrate
from episodes.e001_pickle_doodle.script import SCRIPT

HERE = os.path.dirname(os.path.abspath(__file__))
track, cues, caps, end = narrate(SCRIPT, os.path.join(HERE, "voice_cache"))
for c in cues.values():
    print(f"{c.id:8s} {c.start:6.2f} -> {c.end:6.2f}  {' '.join(w for w, _, _ in c.words)}")
print("end", round(end, 2), "captions", len(caps))
