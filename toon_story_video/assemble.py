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
        pop = r"{\fscx72\fscy72\t(0,90,\fscx100\fscy100)}"  # each chunk pops in
        ass += f"Dialogue: 0,{ts(c['start'])},{ts(c['end'])},cap,{pop}{c['text']}\n"
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


# -------------------------------------------------------- sound effects
def band(x, sr, lo, hi):
    f = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / sr)
    f[(fr < lo) | (fr > hi)] = 0
    return np.fft.irfft(f, len(x))


def effect(name, sr, rnd):
    def t(d):
        return np.arange(int(d * sr)) / sr
    if name == "whoosh":
        k = t(0.38)
        return 0.5 * band(rnd.standard_normal(len(k)), sr, 300, 3200) * np.sin(np.pi * k / 0.38) ** 2
    if name == "slide":
        k = t(0.3)
        return 0.3 * band(rnd.standard_normal(len(k)), sr, 900, 4500) * np.sin(np.pi * k / 0.3) ** 2
    if name == "thud":
        k = t(0.3)
        w = np.sin(2 * np.pi * (50 * k + 20 * (1 - np.exp(-k * 30)) / 30 * 2)) * np.exp(-k * 14)
        click = band(rnd.standard_normal(len(k)), sr, 800, 5000) * np.exp(-k * 90) * 0.5
        return 0.9 * (w + click)
    if name == "boom":
        k = t(1.0)
        return 0.9 * (np.sin(2 * np.pi * 52 * k) * np.exp(-k * 4)
                      + 0.3 * band(rnd.standard_normal(len(k)), sr, 40, 300) * np.exp(-k * 6))
    if name == "ding":
        k = t(0.8)
        return 0.4 * (np.sin(2 * np.pi * 1568 * k) + 0.4 * np.sin(2 * np.pi * 3136 * k)
                      + 0.15 * np.sin(2 * np.pi * 4704 * k)) * np.exp(-k * 6)
    if name == "pop":
        k = t(0.09)
        return 0.6 * np.sin(2 * np.pi * (400 * k + 2800 * k * k)) * np.sin(np.pi * k / 0.09)
    if name == "shine":
        k = t(0.5)
        out = np.zeros(len(k))
        for i, fq in enumerate((2093, 2637, 3136)):
            d = int(i * 0.05 * sr)
            kk = k[:len(k) - d]
            out[d:] += 0.22 * np.sin(2 * np.pi * fq * kk) * np.exp(-kk * 9)
        return out
    if name == "scribble":
        k = t(0.6)
        env = np.abs(np.sin(2 * np.pi * 8 * k + rnd.uniform(0, 3))) ** 2 * np.sin(np.pi * k / 0.6)
        return 0.22 * band(rnd.standard_normal(len(k)), sr, 2500, 8000) * env
    raise ValueError(name)


def sfx_track(sr=44100):
    rnd = np.random.default_rng(1)
    out = np.zeros(int(total * sr) + sr, dtype=np.float32)
    for when, name in T.get("sfx", []):
        w = effect(name, sr, rnd).astype(np.float32)
        w[:40] *= np.linspace(0, 1, 40)
        w[-200:] *= np.linspace(1, 0, 200)
        i = int(when * sr)
        out[i:i + len(w)] += w[:len(out) - i]
    return out[:int(total * sr)], sr


fx, sr = sfx_track()
sf.write(os.path.join(a.build, "sfx.wav"), fx, sr)

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
    "-i", os.path.join(a.build, "sfx.wav"),
    "-filter_complex",
    f"[0:v]scale=720:1280:flags=lanczos,ass={os.path.join(a.build, 'captions.ass')},format=yuv420p[v];"
    "[1:a]volume=1.6[n];[2:a]volume=0.15[m];[3:a]volume=0.5[x];"
    "[n][m][x]amix=inputs=3:normalize=0,alimiter=limit=0.95[a]",
    "-map", "[v]", "-map", "[a]", "-r", str(FPS), "-c:v", "libx264", "-crf", "18", "-preset", "medium",
    "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.3f}", "-movflags", "+faststart", a.out,
], check=True)
print("wrote", a.out)
