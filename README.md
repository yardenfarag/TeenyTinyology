# Teenyology

*Teeny creatures. Big stories.* Calm, cute, accurate educational shorts (TikTok / YouTube Shorts) about tiny
creatures, all generated in code: illustrated vector art (pycairo), original music and sound effects (numpy),
and narration (ElevenLabs).

- **Series bible and rules:** [`CLAUDE.md`](CLAUDE.md)
- **Lessons from the video judge:** [`docs/judge-lessons.md`](docs/judge-lessons.md)
- **Workflows:** `.claude/skills/new-episode`, `.claude/skills/new-character`, `.claude/agents/video-judge.md`

## Setup
```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
copy .env.example .env      # then put your ELEVENLABS_API_KEY in .env
```

## Make things
```
.venv/Scripts/python -m engine.preview episodes.e001_pickle_doodle.script preview.mp3      # narration preview
.venv/Scripts/python -m episodes.e001_pickle_doodle.episode render --style illustrated     # full video
.venv/Scripts/python -m characters.model_sheet sheet.png --only pickle,pixie               # character sheet
```
