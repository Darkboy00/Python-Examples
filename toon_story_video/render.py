"""Render shots with Blender (bpy, Cycles on CPU).

python render.py <shots_module> <build_dir> [--still] [--only a,b] [--scale 0.5]
                 [--samples 12] [--part i/k]

--still renders only the middle frame of each shot (fast preview).
--part i/k renders every k-th shot starting at i (run several in parallel).
Already-rendered frames are skipped, so an interrupted run can be resumed.
"""
import argparse
import importlib
import json
import os
import time

import bpy

import toonkit

ap = argparse.ArgumentParser()
ap.add_argument("module")
ap.add_argument("build")
ap.add_argument("--still", action="store_true")
ap.add_argument("--at", type=float, default=0.5, help="position of the still within the shot")
ap.add_argument("--only", default="")
ap.add_argument("--scale", type=float, default=1.0)
ap.add_argument("--samples", type=int, default=5)
ap.add_argument("--threads", type=int, default=0)
ap.add_argument("--part", default="0/1")
a = ap.parse_args()

shots = importlib.import_module(a.module)
timing = json.load(open(os.path.join(a.build, "timing.json")))
only = set(filter(None, a.only.split(",")))
pi, pk = map(int, a.part.split("/"))

for idx, sh in enumerate(timing["shots"]):
    sid, n = sh["id"], sh["frames"]
    if (only and sid not in only) or idx % pk != pi:
        continue
    t0 = time.time()
    s = toonkit.reset(int(720 * a.scale), int(1280 * a.scale), a.samples)
    if a.threads:
        s.render.threads_mode = "FIXED"
        s.render.threads = a.threads
    toonkit.SHOT.update(frames=n, seed=idx * 100)
    getattr(shots, "shot_" + sid)(n)
    s.frame_start, s.frame_end = 1, n
    if a.still:
        s.frame_set(max(1, int(n * a.at)))
        s.render.filepath = os.path.join(a.build, "stills", f"{idx:02d}_{sid}.png")
        bpy.ops.render.render(write_still=True)
    else:
        out = os.path.join(a.build, "frames", f"{idx:02d}_{sid}")
        os.makedirs(out, exist_ok=True)
        for f in range(1, n + 1):
            path = os.path.join(out, f"{f:04d}.png")
            if os.path.exists(path):
                continue
            s.frame_set(f)
            s.render.filepath = path
            bpy.ops.render.render(write_still=True)
    print(f"[{idx:02d}] {sid}: {n} frames, {time.time() - t0:.1f}s", flush=True)
