# Toon story video generator

Builds a ~1 minute vertical (720x1280) narrated story short entirely from code:
toy-like 3D scenes with black outlines rendered in Blender, a synthesized
narrator, word-by-word captions and a generated backing track.

## Files

| File | Role |
|---|---|
| `story_chess.py` | The script: one `(shot_id, narration, pause)` entry per shot |
| `shots_chess.py` | One `shot_<id>(n)` function per shot that builds and animates the scene |
| `toonkit.py` | Reusable Blender helpers: materials, outlines, characters, text, lights, camera |
| `narrate.py` | Narration audio (Kokoro TTS) plus shot lengths and caption timings |
| `render.py` | Renders the shots with Cycles on CPU (resumable, `--still` for previews) |
| `assemble.py` | Joins frames, burns captions, mixes narration and music with ffmpeg |

## Requirements

`pip install bpy kokoro-onnx soundfile numpy`, `ffmpeg` with libass, the Inter
and Carlito fonts, and the Kokoro model files `kokoro-v1.0.onnx` and
`voices-v1.0.bin` from the kokoro-onnx GitHub releases.

## Usage

```bash
B=build
python narrate.py story_chess $B kokoro-v1.0.onnx voices-v1.0.bin
python render.py shots_chess $B --still --scale 0.5      # quick preview stills
python render.py shots_chess $B --scale 0.75 --samples 8 # full render (~3 s/frame on 4 cores)
python assemble.py $B chess.mp4 --mood-shift poster --mood-back study_wide
```

## Making a new story

Copy `story_chess.py` and `shots_chess.py`, write the new narration lines, and
write one `shot_<id>(n)` function per line using the `toonkit` helpers. Shot
lengths follow the narration automatically.
