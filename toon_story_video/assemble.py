"""Join rendered frames, burn word-by-word captions, add narration + music.

python assemble.py <build_dir> <output.mp4> [--mood-shift shot_id] [--mood-back shot_id]
"""
import argparse
import glob
import json
import os
import subprocess

import numpy as np
import soundfile as sf

ap = argparse.ArgumentParser()
ap.add_argument("build")
ap.add_argument("out")
ap.add_argument("--mood-shift", default="", help="shot id where the music turns minor")
ap.add_argument("--mood-back", default="", help="shot id where the music resolves")
a = ap.parse_args()

T = json.load(open(os.path.join(a.build, "timing.json")))
FPS, total = T["fps"], T["frames"] / T["fps"]


# ------------------------------------------------------------- captions
def ts(t):
    h, m = int(t // 3600), int(t % 3600 // 60)
    return f"{h}:{m:02d}:{t % 60:05.2f}"


ass = """[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV
Style: cap,Inter ExtraBold,50,&H00FFFFFF,&H00000000,&H80000000,1,1,4,1,2,40,40,330

[Events]
Format: Layer, Start, End, Style, Text
"""
for sh in T["shots"]:
    for c in sh["captions"]:
        ass += f"Dialogue: 0,{ts(c['start'])},{ts(c['end'])},cap,{c['text']}\n"
open(os.path.join(a.build, "captions.ass"), "w").write(ass)


# ---------------------------------------------------------------- music
def start_of(sid):
    for sh in T["shots"]:
        if sh["id"] == sid:
            return sh["start_frame"] / FPS
    return None


def music(sr=44100, bpm=104):
    """Light plucked backing track; minor between mood-shift and mood-back."""
    n = int(total * sr) + sr
    out = np.zeros(n, dtype=np.float32)
    beat = 60 / bpm
    major = [(0, 4, 7), (9, 12, 16), (5, 9, 12), (7, 11, 14)]      # C Am F G
    minor = [(9, 12, 16), (5, 8, 12), (2, 5, 9), (4, 8, 11)]       # Am Fm Dm E
    t1, t2 = start_of(a.mood_shift) or 1e9, start_of(a.mood_back) or 1e9

    def pluck(freq, t, dur, amp):
        i0 = int(t * sr)
        k = np.arange(int(dur * sr)) / sr
        w = (np.sin(2 * np.pi * freq * k) + 0.35 * np.sin(4 * np.pi * freq * k)) * np.exp(-k * 5.5)
        w[:60] *= np.linspace(0, 1, 60)
        seg = out[i0:i0 + len(w)]
        seg += (amp * w[:len(seg)]).astype(np.float32)

    b = 0
    while b * beat < total:
        t = b * beat
        prog = minor if t1 <= t < t2 else major
        chord = prog[(b // 4) % 4]
        root = 130.81 * 2 ** (chord[0] / 12)
        if b % 4 == 0:
            pluck(root / 2, t, 1.6, 0.5)
        note = chord[(b % 4) % 3] + (12 if b % 4 == 3 else 0)
        pluck(261.63 * 2 ** (note / 12), t, 0.9, 0.28)
        pluck(261.63 * 2 ** (chord[(b + 1) % 3] / 12), t + beat / 2, 0.7, 0.16)
        b += 1
    out = out[:int(total * sr)]
    fade = int(1.5 * sr)
    out[-fade:] *= np.linspace(1, 0, fade)
    return out / max(1e-6, np.abs(out).max()), sr


m, sr = music()
sf.write(os.path.join(a.build, "music.wav"), m, sr)

# ---------------------------------------------------------------- video
lst = os.path.join(a.build, "frames.txt")
frames = sorted(glob.glob(os.path.join(a.build, "frames", "*", "*.png")))
assert len(frames) == T["frames"], f"{len(frames)} frames rendered, {T['frames']} expected"
with open(lst, "w") as f:
    for p in frames:
        f.write(f"file '{p}'\nduration {1 / FPS:.6f}\n")
subprocess.run([
    "ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-r", str(FPS), "-i", lst,
    "-i", os.path.join(a.build, "narration.wav"), "-i", os.path.join(a.build, "music.wav"),
    "-filter_complex",
    f"[0:v]scale=720:1280:flags=lanczos,ass={os.path.join(a.build, 'captions.ass')},format=yuv420p[v];"
    "[1:a]volume=1.6[n];[2:a]volume=0.16[m];[n][m]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]",
    "-map", "[v]", "-map", "[a]", "-r", str(FPS), "-c:v", "libx264", "-crf", "18", "-preset", "medium",
    "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.3f}", "-movflags", "+faststart", a.out,
], check=True)
print("wrote", a.out)
