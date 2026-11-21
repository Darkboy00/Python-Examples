"""Synthesize narration per shot, derive shot lengths and caption timings.

Usage: python narrate.py <story_module> <build_dir> <kokoro.onnx> <voices.bin>
Writes <build_dir>/narration.wav and <build_dir>/timing.json
"""
import importlib
import json
import os
import re
import sys

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

FPS = 24


def trim(x, sr, thresh=0.01, keep=0.03):
    idx = np.where(np.abs(x) > thresh)[0]
    if len(idx) == 0:
        return x
    a = max(0, idx[0] - int(keep * sr))
    b = min(len(x), idx[-1] + int(keep * sr))
    return x[a:b]


def chunks(words):
    """Group words into 1-3 word caption chunks, breaking at punctuation."""
    out, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) == 3 or re.search(r"[.,:!?]$", w) or sum(map(len, cur)) > 11:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def main():
    story = importlib.import_module(sys.argv[1])
    build, model, voices = sys.argv[2:5]
    os.makedirs(build, exist_ok=True)
    k = Kokoro(model, voices)
    audio, timing, frame, sr = [], [], 0, 24000
    for sid, line, pause in story.SHOTS:
        x, sr = k.create(line, voice=story.VOICE, speed=story.SPEED, lang="en-gb")
        x = trim(np.asarray(x, dtype=np.float32), sr)
        dur = len(x) / sr
        n = int(round((dur + pause) * FPS))
        total = int(round(n / FPS * sr))
        buf = np.zeros(total, dtype=np.float32)
        buf[:min(len(x), total)] = x[:total]
        audio.append(buf)
        # caption timings: spread chunks over the spoken part by letter count
        t0 = frame / FPS
        cks = chunks(line.split())
        weights = [sum(len(re.sub(r"\W", "", w)) + 1.5 for w in c) + (2 if re.search(r"[.,:!?]$", c[-1]) else 0)
                   for c in cks]
        tot, acc, caps = sum(weights), 0.0, []
        for c, w in zip(cks, weights):
            caps.append({"text": " ".join(c), "start": round(t0 + dur * acc / tot, 3),
                         "end": round(t0 + dur * (acc + w) / tot, 3)})
            acc += w
        timing.append({"id": sid, "frames": n, "start_frame": frame, "speech": round(dur, 3), "captions": caps})
        frame += n
    sf.write(os.path.join(build, "narration.wav"), np.concatenate(audio), sr)
    json.dump({"fps": FPS, "frames": frame, "shots": timing}, open(os.path.join(build, "timing.json"), "w"), indent=1)
    print(f"{len(timing)} shots, {frame} frames, {frame / FPS:.1f}s")


if __name__ == "__main__":
    main()
