---
name: new-character
description: Design and add a permanent TeenyTinyology cast member (name, look, personality, code module, model sheet) with owner approval. Use when a story needs a creature that is not in the cast yet.
---

# New TeenyTinyology character

1. **Research the real animal** — body plan, proportions, colours, how it moves, life stages needed for stories.
   Note 3–5 visual must-haves (e.g. ants: elbowed antennae, three body parts, petiole node).
2. **Propose to the owner**: a short cute name in the cast's style (Mochi, Pip, Peanut, Noodle, Plum →
   Biscuit, Toffee, Bean, Poppy, Button, Kiwi, …), species, a palette (3–4 hex colours that don't clash with
   the existing cast), and a one-line personality. Make sure it is an original design, not a lookalike of
   any existing cartoon character. Wait for approval of the name.
3. **Write `characters/<name>.py`** following the existing modules:
   - module docstring: NAME, look, personality, `draw(...)` signature and pose parameters;
   - draw everything through the `Style` methods (`st.part`, `st.ellipse`, `st.limb`, `st.eye`, `st.blush`,
     `st.smile`, `st.shadow`, `st.line`) so it works in cute / real / illustrated;
   - in `st.realistic` mode switch to correct anatomy and drop cartoon faces;
   - expose helpers other scenes need (`to_world`, mouth/tip points, life-stage functions);
   - built-in life: blink, breathe/idle, a walk or move cycle via a `phase` parameter.
4. **Add it to `characters/model_sheet.py`** (`CELLS`), render the sheet, check it at full size, fix, and
   show the owner the sheet (copy to the T3 workspace).
5. **Record it** in the cast table in `CLAUDE.md` once approved. Names are permanent from then on.
