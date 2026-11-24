"""Synthesize narration per shot, derive shot lengths and caption timings.

Usage: python narrate.py <story_module> <build_dir> <kokoro.onnx> <voices.bin>
Writes <build_dir>/narration.wav and <build_dir>/timing.json

Caption timing: the pauses the voice makes at punctuation are detected in the
audio and used as anchors; inside each clause, time is shared out by phoneme
count. That keeps captions close to the spoken words without a speech aligner.
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
PUNCT = re.compile(r"[.,:!?]$")


def trim(x, sr, thresh=0.01, keep=0.03):
    idx = np.where(np.abs(x) > thresh)[0]
    if len(idx) == 0:
        return x
    a = max(0, idx[0] - int(keep * sr))
    b = min(len(x), idx[-1] + int(keep * sr))
    return x[a:b]


def pauses(x, sr, min_len=0.09):
    """Silent stretches inside the clip as (start, end) seconds, longest first."""
    hop = int(0.01 * sr)
    rms = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop, hop)])
    quiet = rms < 0.035 * rms.max()
    out, i = [], 0
    while i < len(quiet):
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]:
                j += 1
            if i > 0 and j < len(quiet) and (j - i) * 0.01 >= min_len:
                out.append((i * 0.01, j * 0.01))
            i = j
        else:
            i += 1
    return sorted(out, key=lambda p: p[0] - p[1])


def chunks(words):
    """Group words into 1-3 word caption chunks, breaking at punctuation."""
    out, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) == 3 or PUNCT.search(w) or sum(map(len, cur)) > 11:
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

    def weight(txt):
        try:
            ph = k.tokenizer.phonemize(txt, "en-gb")
        except Exception:
            ph = txt
        return len(re.sub(r"[\sˈˌː.,:!?]", "", ph)) + 1.0

    audio, timing, sfx, frame, sr, anchored = [], [], [], 0, 24000, 0
    for sid, line, pause in story.SHOTS:
        x, sr = k.create(line, voice=story.VOICE, speed=story.SPEED, lang="en-gb")
        x = trim(np.asarray(x, dtype=np.float32), sr)
        dur = len(x) / sr
        n = int(round((dur + pause) * FPS))
        total = int(round(n / FPS * sr))
        buf = np.zeros(total, dtype=np.float32)
        buf[:min(len(x), total)] = x[:total]
        audio.append(buf)
        t0 = frame / FPS

        # clauses = runs of caption chunks ending at punctuation
        cks = chunks(line.split())
        clauses, cur = [], []
        for c in cks:
            cur.append(c)
            if PUNCT.search(c[-1]):
                clauses.append(cur)
                cur = []
        if cur:
            clauses.append(cur)
        gaps = sorted(pauses(x, sr)[:len(clauses) - 1])
        if len(gaps) == len(clauses) - 1:
            anchored += 1
            starts = [0.0] + [g[1] for g in gaps]
            ends = [g[0] for g in gaps] + [dur]
        else:  # could not find every pause: share the whole clip out by weight
            w = [sum(weight(" ".join(c)) for c in cl) + 3 for cl in clauses]
            acc = np.cumsum([0] + w) / sum(w) * dur
            starts, ends = list(acc[:-1]), list(acc[1:])
        caps = []
        for cl, a, b in zip(clauses, starts, ends):
            w = [weight(" ".join(c)) for c in cl]
            acc = np.cumsum([0] + w) / sum(w) * (b - a) + a
            for c, s0 in zip(cl, acc[:-1]):
                caps.append({"text": " ".join(c), "start": round(t0 + float(s0), 3)})
        for c, nxt in zip(caps, caps[1:] + [None]):
            c["end"] = nxt["start"] if nxt else round(min(t0 + dur + 0.15, t0 + n / FPS), 3)
        timing.append({"id": sid, "frames": n, "start_frame": frame, "speech": round(dur, 3), "captions": caps})
        for pos, name in getattr(story, "SFX", {}).get(sid, []):
            sfx.append([round(t0 + pos * n / FPS, 3), name])
        frame += n
    sf.write(os.path.join(build, "narration.wav"), np.concatenate(audio), sr)
    json.dump({"fps": FPS, "frames": frame, "shots": timing, "sfx": sfx},
              open(os.path.join(build, "timing.json"), "w"), indent=1)
    print(f"{len(timing)} shots, {frame} frames, {frame / FPS:.1f}s, pauses anchored in {anchored} shots")


if __name__ == "__main__":
    main()
