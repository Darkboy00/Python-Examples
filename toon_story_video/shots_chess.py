"""Scenes for 'The Worst Chess Player'. Each shot_<id>(n) builds a full
scene animated over n frames (the length comes from the narration)."""
import math
import random

import bmesh

from toonkit import (arc, bob, box, camera, character, cyl, empty, hand_world, key, lamp, mat,
                     show, sky, sph, sun, talk, text, torus, walk, wipe, world, _finish)

HERO = dict(coat="#3f8f86", hat="cap", hat_col="#8a5a3c", glasses=True, bowtie="#c8473f")
PEOPLE = [
    dict(coat="#d9793f", hair="short", hair_col="#3b2a20"),
    dict(coat="#6a7fd1", hat="beanie", hat_col="#c8473f"),
    dict(coat="#c9a23a", hair="long", hair_col="#7a3f22", scarf="#c8473f"),
    dict(coat="#8d5fb0", hat="fedora", hat_col="#4a4a55"),
    dict(coat="#5aa66a", hair="short", hair_col="#d8c27a", scarf="#e2b33c"),
    dict(coat="#c45a7a", hair="bun", hair_col="#2f2f38"),
    dict(coat="#4f8fb8", hat="cap", hat_col="#2f3f5a"),
]
GRANNY = dict(coat="#9a6fc0", hair="bun", hair_col="#c9c9d2", glasses=True, scarf="#f1e6c8")
KID = dict(coat="#e2b33c", hat="beanie", hat_col="#4f8fb8", s=0.62)
CREAM, DARK = "#f1e6c8", "#3b3340"
INK = "#1d2a6b"
PAPER, BILL = "#f7f1dc", "#c2e2b4"


# ------------------------------------------------------------------ props
def pawn(loc, m, parent=None):
    r = empty(loc, parent)
    cyl(0.028, 0.012, (0, 0, 0.006), m, ol=0.004, parent=r)
    cyl(0.02, 0.05, (0, 0, 0.037), m, r2=0.008, ol=0.004, parent=r)
    sph(0.02, (0, 0, 0.072), m, ol=0.004, parent=r, seg=16)
    return r


def king(loc, m, parent=None):
    r = empty(loc, parent)
    cyl(0.034, 0.014, (0, 0, 0.007), m, ol=0.004, parent=r)
    cyl(0.026, 0.1, (0, 0, 0.064), m, r2=0.015, ol=0.004, parent=r)
    sph(0.026, (0, 0, 0.125), m, ol=0.004, parent=r, seg=16)
    box((0.012, 0.012, 0.05), (0, 0, 0.165), m, ol=0.004, parent=r)
    box((0.04, 0.012, 0.012), (0, 0, 0.17), m, ol=0.004, parent=r)
    return r


def board_squares(size, loc, parent=None, a=CREAM, b="#7a5a48", n=8):
    bm = bmesh.new()
    q = size / n
    for i in range(n):
        for j in range(n):
            x, y = -size / 2 + i * q, -size / 2 + j * q
            f = bm.faces.new([bm.verts.new(p) for p in ((x, y, 0), (x + q, y, 0), (x + q, y + q, 0), (x, y + q, 0))])
            f.material_index = (i + j) % 2
    ob = _finish("squares", bm, mat(b), loc, (0, 0, 0), (1, 1, 1), False, False, 0, parent)
    ob.data.materials.append(mat(a))
    return ob


def chess_table(loc=(0, 0, 0), pieces=True, top="#cfc8ba", clock=True):
    r = empty(loc)
    r.scale = (1.3, 1.3, 1.0)
    cyl(0.09, 0.57, (0, 0, 0.285), top, parent=r)
    cyl(0.25, 0.04, (0, 0, 0.02), top, parent=r)
    box((0.8, 0.8, 0.06), (0, 0, 0.6), top, bevel=0.012, parent=r)
    box((0.54, 0.54, 0.02), (0, 0, 0.64), "#5a3f30", ol=0.006, parent=r)
    board_squares(0.5, (0, 0, 0.651), r)
    if pieces:
        q = 0.0625
        for i, j, m in [(-3, 1, CREAM), (-2, -2, CREAM), (-3, -3, CREAM), (-1, 3, CREAM),
                        (2, 0, DARK), (3, 2, DARK), (1, -2, DARK), (3, -1, DARK), (2, 3, DARK), (0, 1, DARK)]:
            pawn(((i - 0.5) * q, (j - 0.5) * q, 0.652), mat(m), r)
    if clock:
        box((0.2, 0.07, 0.1), (0, 0.345, 0.68), "#8a5a3c", bevel=0.008, ol=0.005, parent=r)
        for sx in (-1, 1):
            cyl(0.036, 0.01, (sx * 0.05, 0.306, 0.68), "#f7f1dc", rot=(90, 0, 0), ol=False, parent=r)
            box((0.004, 0.004, 0.028), (sx * 0.05, 0.3, 0.688), "#141414", rot=(0, 30 * sx, 0), ol=False, parent=r)
            cyl(0.012, 0.03, (sx * 0.05, 0.345, 0.74), "#c9c9d2", ol=0.004, parent=r)
    for sx in (-1, 1):
        cyl(0.15, 0.22, (sx * 0.66, 0, 0.11), "#a9744a", parent=r)
    return r


def dollar(loc, rotz=0, note=False, s=1.0, parent=None):
    """A one-dollar bill lying flat. Returns (root, [note line objects])."""
    r = empty(loc, parent)
    r.rotation_euler[2] = math.radians(rotz)
    r.scale = (s, s, s)
    box((0.36, 0.16, 0.004), (0, 0, 0.002), "#a9d49a", ol=0.004, parent=r)
    box((0.335, 0.135, 0.002), (0, 0, 0.005), "#6fa663", ol=False, parent=r)
    box((0.315, 0.115, 0.002), (0, 0, 0.006), BILL, ol=False, parent=r)
    for sx in (-1, 1):
        for sy in (-1, 1):
            text("1", 0.036, (sx * 0.135, sy * 0.036, 0.008), "#3f7a3a", rot=(0, 0, 0), parent=r)
    lines = []
    if note:
        for i, t in enumerate(("Good game.", "Play me again.")):
            lines.append(text(t, 0.037, (0, 0.022 - i * 0.044, 0.009), INK, rot=(0, 0, 0), font="hand", parent=r))
    else:
        sph(1.0, (0, 0, 0.006), "#8fc07f", scale=(0.05, 0.05, 0.002), ol=False, parent=r)
        text("1", 0.07, (0, 0, 0.009), "#3f7a3a", rot=(0, 0, 0), parent=r)
    return r, lines


def pen_hand(pen_col="#e2b33c"):
    hand = sph(0.07, (0, 0, 0), "#f4f1ea", ol=0.008)
    pen = cyl(0.008, 0.22, (0, 0, 0), pen_col, ol=0.004)
    pen.parent = hand
    pen.location = (-0.035, 0.03, -0.01)
    pen.rotation_euler = (math.radians(-55), math.radians(30), 0)
    return hand


def tree(loc, s=1.0, canopy="#4fa35a", ol=0.025):
    r = empty(loc)
    r.scale = (s, s, s)
    cyl(0.14, 1.5, (0, 0, 0.75), "#7a5536", r2=0.1, parent=r, ol=ol and 0.02)
    return [sph(rr, p, canopy, parent=r, ol=ol) for rr, p in
            ((0.95, (0, 0, 2.2)), (0.7, (-0.7, 0.1, 1.9)), (0.7, (0.7, -0.1, 1.95)), (0.6, (0.1, 0, 3.0)))]


def cloud(loc, s=1.0):
    r = empty(loc)
    r.scale = (s, s, s)
    m = mat("#ffffff", emit=0.35)
    for rr, p in ((1.0, (0, 0, 0)), (0.75, (-1.0, 0, -0.15)), (0.8, (1.0, 0, -0.1)), (0.55, (1.8, 0, -0.3)),
                  (0.5, (-1.7, 0, -0.3))):
        o = sph(rr, p, m, scale=(1, 0.5, 0.75), ol=False, parent=r, seg=16)
        o.visible_shadow = False
    return r


def bush(loc, s=1.0, c="#3f9550"):
    r = empty(loc)
    r.scale = (s, s, s)
    for rr, p in ((0.4, (0, 0, 0.3)), (0.3, (-0.4, 0, 0.22)), (0.32, (0.4, 0.05, 0.24))):
        sph(rr, p, c, parent=r, ol=0.02, seg=16)


def flowers(cx, cy, n=7, seed=1, spread=0.7):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y = cx + rnd.uniform(-spread, spread), cy + rnd.uniform(-spread, spread) * 0.6
        cyl(0.008, 0.16, (x, y, 0.08), "#3f7a3a", ol=False, seg=6)
        sph(0.045, (x, y, 0.18), rnd.choice(("#f2d14a", "#ef7f7a", "#ffffff", "#c58be0")), ol=0.006, seg=10)


def pigeon(loc, rotz=0):
    r = empty(loc)
    r.rotation_euler[2] = math.radians(rotz)
    sph(1.0, (0, 0, 0.07), "#9aa0b0", scale=(0.06, 0.1, 0.06), ol=0.006, parent=r, seg=12)
    h = sph(0.04, (0, -0.08, 0.13), "#7f8698", ol=0.006, parent=r, seg=12)
    cyl(0.012, 0.03, (0, -0.125, 0.13), "#e2a33c", r2=0.0, rot=(90, 0, 0), ol=False, parent=r, seg=6)
    return r, h


def chalkboard(number, loc=(0, 0, 0)):
    r = empty(loc)
    for sx in (-1, 1):
        box((0.06, 0.06, 1.55), (sx * 0.47, 0.02, 0.76), "#a9744a", parent=r, rot=(-6, 0, 0))
    box((1.0, 0.06, 1.3), (0, 0, 0.85), "#a9744a", bevel=0.01, parent=r, rot=(-6, 0, 0))
    box((0.86, 0.02, 1.16), (0, -0.035, 0.85), "#2f5d4a", ol=False, parent=r, rot=(-6, 0, 0))
    chalk = mat("#f3f1e6", emit=0.15)
    text("GAMES LOST", 0.105, (0, -0.07, 1.26), chalk, rot=(84, 0, 0), parent=r)
    box((0.62, 0.01, 0.012), (0, -0.065, 1.15), chalk, ol=False, parent=r, rot=(-6, 0, 0))
    num = text(str(number), 0.42, (0, -0.06, 0.8), chalk, rot=(84, 0, 0), font="black", parent=r)
    box((0.5, 0.01, 0.012), (0, -0.04, 0.5), chalk, ol=False, parent=r, rot=(-6, 0, 0))
    # tally marks along the bottom and a chalk tray
    for i in range(number // 100 * 5):
        box((0.008, 0.008, 0.07), (-0.3 + i * 0.045 + (i // 5) * 0.03, -0.03, 0.4), chalk,
            rot=(-6, 30 if i % 5 == 4 else 0, 0), ol=False, parent=r)
    box((0.9, 0.08, 0.025), (0, -0.07, 0.24), "#8a5a3c", ol=0.006, parent=r)
    cyl(0.012, 0.07, (0.2, -0.08, 0.265), "#f3f1e6", rot=(0, 90, 0), ol=False, parent=r, seg=8)
    return r, num


def trophy(loc, parent=None):
    r = empty(loc, parent)
    g = mat("#f0bf3a", rough=0.35)
    cyl(0.16, 0.06, (0, 0, 0.03), "#3b3340", parent=r)
    cyl(0.11, 0.05, (0, 0, 0.085), g, parent=r)
    cyl(0.03, 0.16, (0, 0, 0.19), g, parent=r)
    sph(0.045, (0, 0, 0.2), g, parent=r, ol=0.006, seg=16)
    cyl(0.07, 0.3, (0, 0, 0.42), g, r2=0.2, parent=r)
    for sx in (-1, 1):
        arc(0.1, -80 if sx > 0 else 100, 80 if sx > 0 else 260, 0.016, (sx * 0.16, 0, 0.43), "#f0bf3a", parent=r)
    return r


def sparkle(loc, f, size=0.12, n=None):
    """A four-point glint that pops at frame f."""
    r = empty(loc)
    m = mat("#ffffff", emit=6)
    for rz in (0, 90):
        o = box((size, 0.004, size * 0.12), (0, 0, 0), m, rot=(0, rz, 0), ol=False, parent=r)
        o.visible_shadow = False
    key(r, max(1, f - 4), scale=0.001)
    key(r, f, scale=1.0, rot=(0, 0, 0))
    key(r, f + 5, scale=0.001, rot=(0, 45, 0))
    return r


def pedestal(plaque=True):
    cyl(0.45, 1.0, (0, 0, 0.5), "#51468a")
    cyl(0.5, 0.05, (0, 0, 0.025), "#3a3166")
    cyl(0.55, 0.06, (0, 0, 1.03), "#a8323a")
    if plaque:
        box((0.62, 0.04, 0.24), (0, -0.46, 0.62), "#f0bf3a", ol=0.01)
        text("$50,000", 0.13, (0, -0.49, 0.62), "#2b2455", font="black")
    for sx in (-1, 1):
        cyl(0.035, 0.9, (sx * 1.0, -0.3, 0.45), mat("#f0bf3a", rough=0.4), ol=0.008)
        sph(0.06, (sx * 1.0, -0.3, 0.93), mat("#f0bf3a", rough=0.4), ol=0.008, seg=12)
        cyl(0.11, 0.03, (sx * 1.0, -0.3, 0.015), mat("#f0bf3a", rough=0.4), ol=0.008)


# ------------------------------------------------------------------- sets
def park(ground="#8fcf6e", canopy="#4fa35a", trees=True, extras=True):
    sky("#8fd0ee", "#e8f6f4", 1.0)
    sun(3.0, rot=(48, 0, 32))
    box((90, 90, 0.1), (0, 0, -0.05), ground, ol=False)
    cyl(2.9, 0.02, (0, 0, -0.004), "#d8c9a8", ol=False, seg=48)
    cyl(2.7, 0.02, (0, 0, 0.0), "#ecdfc6", ol=False, seg=48)
    box((60, 1.7, 0.02), (0, 4.2, 0), "#ecdfc6", ol=False)
    out = []
    if trees:
        for p, s in (((-2.6, 2.6, 0), 1.25), ((3.1, 3.4, 0), 1.0), ((-4.8, 7, 0), 1.3), ((5.4, 8, 0), 1.4),
                     ((0.6, 9, 0), 1.1), ((-8, 10, 0), 1.5), ((9, 11, 0), 1.3)):
            out += tree(p, s, canopy)
    for i, (x, w, h, c) in enumerate(((-13, 5, 6, "#e7b8a0"), (-7.5, 5, 8, "#a8c7dd"), (-2, 5, 6.5, "#efd58a"),
                                      (3.5, 5, 9, "#d9a6c4"), (9, 5, 7, "#b5d6a8"), (14.5, 5, 8, "#e7b8a0"))):
        box((w, 3, h), (x, 18, h / 2), c, ol=0.04)
        box((w + 0.4, 3.3, 0.35), (x, 18, h + 0.17), "#8a5a4a", ol=0.04)
        box((1.0, 0.1, 1.7), (x, 16.47, 0.85), "#7a5536", ol=False)
        box((2.6, 0.5, 0.12), (x, 16.3, 1.95), ("#c8473f", "#f1e6c8")[i % 2], ol=False)
        for wx in (-1.3, 0, 1.3):
            for wz in range(3, int(h), 2):
                box((0.8, 0.1, 1.0), (x + wx, 16.47, wz), "#f7f1dc", ol=False)
                box((0.66, 0.1, 0.86), (x + wx, 16.44, wz), "#5f7f9a", ol=False)
    for x, y, z, s in ((-5, 30, 9.5, 1.6), (4, 30, 11, 1.3), (11, 30, 8.5, 1.1), (-13, 30, 11.5, 1.2)):
        cloud((x, y, z), s)
    # low fence behind the path
    for x in range(-14, 15, 1):
        box((0.08, 0.08, 0.5), (x, 5.4, 0.25), "#f7f1dc", ol=False)
    for z in (0.2, 0.4):
        box((30, 0.04, 0.06), (0, 5.4, z), "#f7f1dc", ol=False)
    if extras:
        for x, y, s in ((-3.6, 4.9, 1.0), (-1.2, 5.0, 0.8), (1.9, 5.0, 0.9), (4.4, 4.8, 1.1)):
            bush((x, y, 0), s)
        flowers(-2.4, 1.0, 7, 1)
        flowers(2.9, 0.4, 6, 2)
        flowers(1.3, 2.9, 6, 3)
        # lamp posts, bench, bin
        for x, y in ((2.2, 1.5), (-3.4, 3.4)):
            cyl(0.08, 0.2, (x, y, 0.1), "#3b4a44", ol=0.015)
            cyl(0.045, 2.6, (x, y, 1.3), "#3b4a44", ol=0.015)
            cyl(0.2, 0.1, (x, y, 2.86), "#3b4a44", r2=0.05, ol=0.015)
            sph(0.17, (x, y, 2.68), "#fff3c4", ol=0.015)
        box((1.4, 0.4, 0.06), (-1.9, 1.6, 0.42), "#a9744a", bevel=0.01)
        box((1.4, 0.06, 0.4), (-1.9, 1.8, 0.75), "#a9744a", bevel=0.01)
        for sx in (-0.55, 0.55):
            box((0.06, 0.36, 0.42), (-1.9 + sx, 1.6, 0.21), "#3b4a44")
        cyl(0.2, 0.55, (1.5, 2.0, 0.275), "#4f8f6a", r2=0.23, ol=0.015)
    return out


def tiles(n=12, q=1.0, a="#6b4a5e", b="#77546a"):
    return board_squares(n * q, (0, 0, 0.001), a=a, b=b, n=n)


def hall(banner=True, crowd=True):
    world("#2b2455", 0.55)
    sun(0.7, rot=(55, 0, -25), hexstr="#b9b4ff")
    box((24, 24, 0.1), (0, 0, -0.05), "#6b4a5e", ol=False)
    tiles(14)
    box((24, 0.2, 9), (0, 6, 4.5), "#3f3672", ol=False)
    box((24, 0.3, 1.0), (0, 5.9, 0.5), "#2e2757", ol=False)
    box((24, 0.32, 0.08), (0, 5.9, 1.02), "#51468a", ol=False)
    for x in (-4.2, 4.2):
        box((0.5, 0.5, 9), (x, 5.8, 4.5), "#51468a", ol=0.03)
    for x in (-2.6, 2.6):
        box((1.3, 0.06, 1.8), (x, 5.88, 2.3), "#2e2757", ol=False)
        box((1.1, 0.06, 1.6), (x, 5.85, 2.3), "#4a4190", ol=False)
        k = king((x, 5.8, 1.75), mat("#f0bf3a"))
        k.scale = (5, 1, 5)
    if banner:
        box((5.0, 0.06, 1.3), (0, 5.8, 3.9), "#a8323a", ol=0.03)
        text("CITY CHESS\nCHAMPIONSHIP", 0.42, (0, 5.74, 3.9), mat("#f0bf3a", emit=0.3), font="black", spacing=0.9)
    # bunting
    cols = ("#f0bf3a", "#c8473f", "#5aa66a", "#6a7fd1", "#f1e6c8")
    for i in range(17):
        x = -4 + i * 0.5
        z = 4.95 + 0.35 * ((x / 4) ** 2)
        cyl(0.16, 0.3, (x, 5.4, z - 0.15), cols[i % 5], r2=0.0, rot=(180, 0, 0), ol=False, seg=3)
    for x in (-2.2, 0, 2.2):
        cyl(0.012, 1.6, (x, 2.2, 4.4), "#141414", ol=False)
        cyl(0.3, 0.18, (x, 2.2, 3.6), "#f0bf3a", r2=0.08, ol=0.015)
        sph(0.1, (x, 2.2, 3.5), mat("#fff0c0", emit=8), ol=False)
        lamp((x, 2.2, 3.3), 260)
    lamp((0.5, -3.0, 3.2), 900, "#ffe9c4", radius=0.6)
    if crowd:  # faceless audience along the back wall
        rnd = random.Random(5)
        for i in range(13):
            x = -3.9 + i * 0.65 + rnd.uniform(-0.1, 0.1)
            c = rnd.choice(("#51468a", "#5b4f96", "#463c80", "#62569e"))
            sph(1.0, (x, 5.2, 1.0), c, scale=(0.24, 0.2, 0.42), ol=False, seg=12)
            sph(0.27, (x, 5.2, 1.62 + rnd.uniform(-0.05, 0.05)), "#6a5fa6", ol=False, seg=12)


def study():
    world("#241f4a", 0.45)
    sun(0.5, rot=(50, 0, -30), hexstr="#b9b4ff")
    box((16, 16, 0.1), (0, 0, -0.05), "#553a58", ol=False)
    cyl(1.9, 0.01, (0, -0.2, 0.004), "#a8323a", ol=False, seg=40)
    cyl(1.6, 0.01, (0, -0.2, 0.008), "#c45a4a", ol=False, seg=40)
    box((16, 0.2, 7), (0, 1.7, 3.5), "#4a3f7a", ol=False)
    box((16, 0.25, 0.9), (0, 1.62, 0.45), "#3a3166", ol=False)
    for x in range(-8, 9):  # wallpaper stripes
        box((0.06, 0.02, 6), (x * 0.5 + 0.25, 1.595, 3.9), "#51468a", ol=False)
    # window with moon, stars and curtains
    box((1.0, 0.1, 1.3), (-1.15, 1.6, 2.15), "#f1e6c8", ol=0.02)
    box((0.86, 0.1, 1.16), (-1.15, 1.56, 2.15), mat("#27306e", emit=0.6), ol=False)
    sph(0.16, (-1.0, 1.52, 2.4), mat("#fff6cf", emit=4), scale=(1, 0.2, 1), ol=False)
    for sx, sz in ((-1.4, 2.5), (-1.3, 1.9), (-0.9, 1.85), (-1.45, 2.15)):
        sph(0.02, (sx, 1.52, sz), mat("#ffffff", emit=5), ol=False, seg=8)
    box((0.04, 0.1, 1.16), (-1.15, 1.5, 2.15), "#f1e6c8", ol=False)
    box((0.86, 0.1, 0.04), (-1.15, 1.5, 2.15), "#f1e6c8", ol=False)
    for sx in (-1, 1):
        box((0.26, 0.08, 1.55), (-1.15 + sx * 0.6, 1.46, 2.1), "#c8473f", bevel=0.03, ol=0.012)
    cyl(0.02, 1.7, (-1.15, 1.46, 2.9), "#8a5a3c", rot=(0, 90, 0), ol=0.008)
    lamp((0.2, -2.6, 2.6), 420, "#cfc4ff", radius=0.6)


def desk(lamp_on=True):
    box((1.9, 0.8, 0.07), (0, 0, 0.72), "#a9744a", bevel=0.012)
    box((1.7, 0.04, 0.3), (0, -0.36, 0.53), "#8a5a3c", ol=0.008)
    for sx in (-0.5, 0.5):
        sph(0.025, (sx, -0.39, 0.55), "#f0bf3a", ol=False, seg=8)
    for sx in (-0.85, 0.85):
        for sy in (-0.32, 0.32):
            box((0.07, 0.07, 0.7), (sx, sy, 0.35), "#8a5a3c")
    cyl(0.1, 0.03, (0.72, 0.15, 0.77), "#3b4a44")
    cyl(0.015, 0.4, (0.72, 0.15, 0.97), "#3b4a44", ol=False)
    cyl(0.07, 0.16, (0.66, 0.1, 1.2), "#e2b33c", r2=0.17, rot=(25, -35, 0), ol=0.012)
    # mug and pencil cup
    cyl(0.05, 0.1, (-0.3, 0.22, 0.805), "#f4f1ea", ol=0.008)
    cyl(0.045, 0.1, (0.36, 0.26, 0.805), "#6a7fd1", ol=0.008)
    for i, c in enumerate(("#e2b33c", "#c8473f", "#5aa66a")):
        cyl(0.007, 0.16, (0.34 + i * 0.02, 0.26, 0.9), c, rot=(8 * (i - 1), 6, 0), ol=False, seg=6)
    if lamp_on:
        lamp((0.5, -0.05, 1.12), 110, "#ffd58a", radius=0.08)


def notebook_wall(y=1.5, x0=-2.0, x1=2.0, z0=0.25, rows=7):
    rnd = random.Random(7)
    cols = ("#c8473f", "#3f8f86", "#e2b33c", "#6a7fd1", "#d9793f", "#8d5fb0", "#5aa66a", "#4f8fb8")
    box((x1 - x0 + 0.2, 0.34, 0.08), ((x0 + x1) / 2, y, z0 - 0.04), "#8a5a3c", ol=0.015)
    for r in range(rows):
        z = z0 + r * 0.5
        box((x1 - x0 + 0.2, 0.34, 0.05), ((x0 + x1) / 2, y, z + 0.45), "#8a5a3c", ol=0.015)
        x = x0
        while x < x1 - 0.06:
            w = rnd.choice((0.06, 0.07, 0.08, 0.09))
            h = rnd.uniform(0.33, 0.41)
            tilt = rnd.choice((0, 0, 0, 0, 4))
            box((w, 0.24, h), (x + w / 2, y - 0.02, z + h / 2), rnd.choice(cols), rot=(0, tilt, 0), ol=0.006)
            box((w * 0.7, 0.01, 0.07), (x + w / 2, y - 0.142, z + h * 0.62), "#f4f1ea", rot=(0, tilt, 0), ol=False)
            x += w + 0.012
    for sx in (x0 - 0.1, x1 + 0.1):
        box((0.06, 0.34, rows * 0.5 + 0.1), (sx, y, z0 + rows * 0.25), "#8a5a3c", ol=0.015)


# ----------------------------------------------------------------- helpers
def seat(side, **kw):
    """Seat a character at the chess table; side -1 = left, +1 = right."""
    return character(loc=(side * 0.86, 0, 0), rotz=-side * 62, sit=True, **kw)


def reach(c, hand, f, point):
    key(hand, f, loc=hand_world(c, hand, point))


def laugh(c, n, phase=0):
    bob(c.root, n, amp=0.035, period=6, phase=phase)
    talk(c, 1 + phase, n)


def game(n, opp, opp_mouth="smile", hero_mouth="flat"):
    chess_table()
    h = seat(-1, mouth=hero_mouth, **HERO)
    o = seat(1, mouth=opp_mouth, **opp)
    reach(h, h.handR, 1, (-0.47, -0.26, 0.7))
    reach(h, h.handL, 1, (-0.5, 0.28, 0.7))
    reach(o, o.handL, 1, (0.47, -0.26, 0.7))
    reach(o, o.handR, 1, (0.5, 0.28, 0.7))
    return h, o


# ------------------------------------------------------------------- shots
def shot_park_wide(n):
    park()
    h, o = game(n, PEOPLE[0])
    w1 = character(loc=(-2.4, 1.5, 0), rotz=75, mouth="smile", **PEOPLE[1])
    walk(w1, 1, int(n * 0.55), (-2.4, 1.5, 0), (-0.55, 1.5, 0))
    key(w1.root, int(n * 0.55), rot=(0, 0, 75))
    key(w1.root, int(n * 0.72), rot=(0, 0, 8))
    w2 = character(loc=(0.8, 1.7, 0), rotz=-10, mouth="smile", **PEOPLE[2])
    bob(w2.root, n, 0.015, 16, phase=1)
    for i, (x, y, rz) in enumerate(((-1.6, -0.9, 200), (1.9, -0.6, 140), (2.3, -1.2, 100))):
        p, head = pigeon((x, y, 0), rz)
        for f in range(4 + i * 5, n, 14):
            key(head, f, loc=(0, -0.08, 0.13))
            key(head, f + 3, loc=(0, -0.1, 0.05))
            key(head, f + 6, loc=(0, -0.08, 0.13))
    # the opponent makes the winning move, the hero's head drops
    pw = pawn((0.2, -0.12, 0.652), mat(DARK))
    a, b = int(n * 0.3), int(n * 0.5)
    reach(o, o.handL, a, (0.2, -0.12, 0.8))
    reach(o, o.handL, b, (-0.02, -0.06, 0.8))
    reach(o, o.handL, int(n * 0.75), (0.47, -0.26, 0.7))
    key(pw, a, loc=(0.2, -0.12, 0.652))
    key(pw, (a + b) // 2, loc=(0.09, -0.09, 0.74))
    key(pw, b, loc=(-0.02, -0.06, 0.652))
    key(h.head, int(n * 0.5), rot=(0, 0, 0))
    key(h.head, int(n * 0.75), rot=(16, 0, 0))
    camera([(1, (0.5, -6.6, 2.4), (0, 0.3, 1.25)), (n, (0.0, -5.2, 1.7), (-0.05, 0, 1.0))], lens=48)


def shot_king_falls(n):
    park()
    h, o = game(n, PEOPLE[0])
    k = king((-0.09, -0.03, 0.652), mat(CREAM))
    key(k, 3, rot=(0, 0, 0))
    key(k, 9, rot=(12, 88, 0))
    key(k, 12, rot=(12, 78, 0))
    key(k, 15, rot=(12, 88, 0))
    key(k, 22, rot=(30, 88, 0))
    reach(o, o.handL, 1, (0.02, -0.03, 0.84))
    reach(o, o.handL, 3, (-0.02, -0.03, 0.84))
    reach(o, o.handL, 10, (0.36, -0.2, 0.75))
    camera([(1, (0.0, -1.25, 1.02), (-0.03, 0, 0.7)), (n, (0.0, -1.1, 0.98), (-0.03, 0, 0.7))], lens=55, fstop=2.0)


def shot_pay_dollar(n):
    park()
    h, o = game(n, PEOPLE[0], hero_mouth="smile")
    d, _ = dollar((-0.3, -0.24, 0.665), rotz=8)
    a, b = int(n * 0.2), int(n * 0.65)
    key(d, a, loc=(-0.3, -0.24, 0.665))
    key(d, b, loc=(0.12, -0.24, 0.665))
    reach(h, h.handR, a, (-0.5, -0.24, 0.72))
    reach(h, h.handR, b, (-0.08, -0.24, 0.72))
    reach(h, h.handR, n, (-0.45, -0.24, 0.72))
    reach(o, o.handL, b, (0.47, -0.26, 0.7))
    reach(o, o.handL, n, (0.3, -0.24, 0.72))
    key(h.head, a, rot=(0, 0, 0))
    key(h.head, (a + b) // 2, rot=(10, 0, 0))
    key(h.head, b, rot=(0, 0, 0))
    camera([(1, (1.3, -3.7, 1.8), (-0.35, 0, 0.98)), (n, (1.1, -3.2, 1.65), (-0.35, 0, 0.95))], lens=50, fstop=4.0)


def _bill_close(n, base, f_lines, hand=True):
    """Top-down close-up of the bill; each handwritten line is revealed
    left-to-right over its (start, end) frame range."""
    box((3, 3, 0.05), (0, 0, -0.025), base, ol=False)
    d, lines = dollar((0, 0, 0), rotz=14, note=True, s=1.0)
    hd = pen_hand() if hand else None
    ca, sa = math.cos(math.radians(14)), math.sin(math.radians(14))
    if hd:
        key(hd, 1, loc=(0.3, -0.3, 0.14))
    for i, (f0, f1) in enumerate(f_lines):
        y = 0.022 - i * 0.044
        wipe(d, -0.15, 0.15, y, 0.044, 0.0125, BILL, f0, f1)
        if hd:
            for f, lx in ((f0, -0.13), (f1, 0.13)):
                key(hd, f, loc=(lx * ca - y * sa + 0.085, lx * sa + y * ca - 0.1, 0.1))
    if hd:
        key(hd, min(n, f_lines[-1][1] + 8), loc=(0.32, -0.25, 0.16))
    camera([(1, (0.0, -0.2, 1.2), (0, 0.0, 0)), (n, (0.0, -0.17, 1.0), (0, 0.0, 0))], lens=50)
    return d


def shot_bill_note(n):
    sky("#8fd0ee", "#e8f6f4", 1.0)
    sun(3.0, rot=(35, 0, 30))
    _bill_close(n, "#cfc8ba", ((int(n * 0.5), int(n * 0.68)), (int(n * 0.7), int(n * 0.94))))
    board_squares(0.5, (-0.15, 0.42, 0.012))
    box((0.54, 0.54, 0.02), (-0.15, 0.42, 0.0), "#5a3f30", ol=0.006)
    pawn((0.02, 0.23, 0.012), mat(DARK))
    pawn((-0.2, 0.3, 0.012), mat(CREAM))
    k = king((0.24, 0.3, 0.02), mat(CREAM))
    k.rotation_euler = (0.3, 1.5, 0.8)


def shot_notice(n):
    park(trees=True)
    for sx in (-1, 1):
        cyl(0.05, 1.9, (sx * 0.55, 0.2, 0.95), "#8a5a3c")
    box((1.35, 0.08, 1.0), (0, 0.2, 1.45), "#a9744a", bevel=0.012)
    box((1.5, 0.2, 0.06), (0, 0.2, 2.0), "#8a5a3c", bevel=0.01)
    box((0.86, 0.02, 0.84), (0, 0.14, 1.45), PAPER, rot=(0, -3, 0), ol=0.006)
    for sx in (-1, 1):
        sph(0.02, (sx * 0.38, 0.12, 1.83), "#c8473f", ol=False, seg=8)
    text("WORST\nPLAYER\nIN THE CITY", 0.125, (0, 0.12, 1.61), "#b8322a", rot=(90, -3, 0), font="black", spacing=0.9)
    sph(0.1, (0, 0.11, 1.2), "#f4f1ea", scale=(1, 0.2, 1), ol=0.006)
    sph(0.105, (0, 0.105, 1.25), "#8a5a3c", scale=(1, 0.2, 0.5), ol=False)
    for sx in (-1, 1):
        sph(0.014, (sx * 0.035, 0.085, 1.19), "#141414", ol=False)
        torus(0.03, 0.004, (sx * 0.035, 0.085, 1.19), mat("#2a2a2a"), rot=(90, 0, 0))
    a = character(loc=(-0.78, -0.55, 0), rotz=25, mouth="open", **PEOPLE[3])
    b = character(loc=(0.78, -0.5, 0), rotz=-25, mouth="open", **PEOPLE[4])
    laugh(a, n)
    laugh(b, n, 1)
    key(b.handL, 1, loc=(-0.34, -0.1, 0.8))
    key(b.handL, 10, loc=(-0.5, -0.3, 1.2))
    key(a.handR, 1, loc=(0.2, -0.24, 0.85))
    key(a.handL, 1, loc=(-0.2, -0.24, 0.85))
    camera([(1, (0, -5.2, 1.5), (0, 0, 1.2)), (n, (0, -4.4, 1.45), (0, 0, 1.22))], lens=50)


def _beaten_by(n, opp, kid=False):
    park()
    chess_table()
    h = seat(-1, mouth="smile", **HERO)
    kw = dict(opp)
    s = kw.pop("s", 1.0)
    z0 = 0.22 if kid else 0
    o = character(loc=(0.86, 0, z0), rotz=-62, sit=not kid, mouth="open", s=s, **kw)
    d, _ = dollar((-0.25, -0.24, 0.665), rotz=8)
    key(d, 1, loc=(-0.25, -0.24, 0.665))
    key(d, int(n * 0.6), loc=(0.14, -0.24, 0.665))
    reach(h, h.handR, 1, (-0.46, -0.24, 0.72))
    reach(h, h.handR, int(n * 0.6), (-0.07, -0.24, 0.72))
    reach(h, h.handL, 1, (-0.5, 0.28, 0.7))
    k = king((-0.09, 0.02, 0.652), mat(CREAM))
    k.rotation_euler = (0.2, 1.5, 0)
    # winner throws both hands up and bounces
    top = 1.9 if kid else 1.5
    for hand, sx in ((o.handL, -1), (o.handR, 1)):
        key(hand, 1, loc=(sx * 0.34, -0.05, 0.6))
        key(hand, 7, loc=(sx * 0.42, -0.02, top))
        for f in range(11, n + 4, 4):
            key(hand, f, loc=(sx * (0.42 + 0.05 * (f % 8 == 3)), -0.02, top - 0.08 * (f % 8 == 3)))
    f, up = 1, False
    while f <= n + 5:
        key(o.root, f, loc=(0.86, 0, z0 + (0.16 if kid else 0.04) * up))
        f, up = f + 5, not up
    talk(o, 1, n)
    camera([(1, (-2.5, -3.3, 1.75), (0.3, 0, 1.02)), (n, (-2.2, -2.9, 1.6), (0.35, 0, 1.02))], lens=45)


def shot_kid(n):
    _beaten_by(n, KID, kid=True)


def shot_granny(n):
    _beaten_by(n, GRANNY)


def shot_queue(n):
    park()
    h, o = game(n, PEOPLE[5])
    a = int(n * 0.35)
    for i in range(7):
        kw = PEOPLE[(i + 1) % len(PEOPLE)]
        p0 = (1.6 + 0.22 * i, 0.75 + 0.85 * i, 0)
        p1 = (1.5 + 0.22 * i, 0.4 + 0.85 * i, 0)
        c = character(loc=p0, rotz=22, mouth="smile", **kw)
        walk(c, a + i * 2, a + i * 2 + 12, p0, p1)
        if i % 2 == 0:
            d, _ = dollar((0, 0, 0), s=0.0)
    camera([(1, (-0.6, -4.2, 1.6), (0.3, 0.2, 1.0)), (n, (-1.9, -4.6, 3.3), (1.4, 2.6, 0.9))], lens=42)


def shot_seasons(n):
    box((90, 90, 0.1), (0, 0, -0.05), "#8fcf6e", ol=False)
    snow = box((90, 90, 0.1), (0, 0, -0.045), "#f2f6fa", ol=False)
    sky("#8fd0ee", "#e8f6f4", 1.0)
    sun(3.0, rot=(48, 0, 32))
    cyl(2.7, 0.02, (0, 0, -0.005), "#ecdfc6", ol=False, seg=48)
    for x, y, z, s in ((-3, 30, 10.5, 1.4), (5, 30, 12, 1.2)):
        cloud((x, y, z), s)
    a, b = n // 3, 2 * n // 3
    rnd = random.Random(4)
    for colr, f0, f1 in (("#4fa35a", 1, a), ("#e08a3a", a, b), ("#f2f6fa", b, n + 1)):
        parts = tree((-2.3, 3.2, 0), 1.35, colr) + tree((2.6, 4.2, 0), 1.2, colr)
        if colr == "#e08a3a":  # falling leaves
            for i in range(14):
                x, y = rnd.uniform(-2.5, 2.5), rnd.uniform(-1, 2.5)
                lf = sph(0.05, (x, y, 3), rnd.choice(("#e08a3a", "#c8473f", "#f2d14a")), scale=(1, 0.3, 0.6),
                         ol=False, seg=8)
                key(lf, a, loc=(x, y, rnd.uniform(1.5, 3.2)), rot=(0, 0, 0))
                key(lf, b, loc=(x + rnd.uniform(-0.4, 0.4), y, rnd.uniform(0.1, 1.2)), rot=(200, 150, 90))
                parts.append(lf)
        if colr == "#f2f6fa":  # snowfall
            for i in range(40):
                x, y = rnd.uniform(-3, 3), rnd.uniform(-2, 3)
                fl = sph(0.03, (x, y, 3), mat("#ffffff", emit=0.5), ol=False, seg=6)
                z = rnd.uniform(0.5, 4)
                key(fl, b, loc=(x, y, z))
                key(fl, n + 1, loc=(x + 0.1, y, z - 0.8))
                parts.append(fl)
        for p in parts:
            show(p, 1, f0 == 1)
            if f0 > 1:
                show(p, f0, True)
            if f1 <= n:
                show(p, f1, False)
    show(snow, 1, False)
    show(snow, b, True)
    chess_table()
    h = seat(-1, **HERO)
    reach(h, h.handR, 1, (-0.47, -0.26, 0.7))
    reach(h, h.handL, 1, (-0.5, 0.28, 0.7))
    for i, (kw, f0, f1) in enumerate(((PEOPLE[0], 1, a), (PEOPLE[2], a, b), (PEOPLE[6], b, n + 1))):
        o = seat(1, mouth="smile", **kw)
        reach(o, o.handL, 1, (0.47, -0.26, 0.7))
        show(o.root, 1, f0 == 1)
        if f0 > 1:
            show(o.root, f0, True)
        if f1 <= n:
            show(o.root, f1, False)
    camera([(1, (0.2, -6.4, 2.0), (0.0, 0.3, 1.7)), (n, (0.2, -6.0, 2.0), (0.0, 0.3, 1.7))], lens=45)


def _chalk(n, number, dist):
    park(extras=False)
    r, num = chalkboard(number)
    key(num, 1, scale=0.6)
    key(num, 5, scale=1.12)
    key(num, 8, scale=1.0)
    rnd = random.Random(number)
    for i in range(8):  # puff of chalk dust
        d = sph(0.03, (0, -0.12, 0.8), mat("#f3f1e6", emit=0.3), ol=False, seg=6)
        d.visible_shadow = False
        key(d, 2, loc=(0, -0.12, 0.8), scale=1.0)
        key(d, 12, loc=(rnd.uniform(-0.45, 0.45), -0.2, 0.8 + rnd.uniform(-0.35, 0.35)), scale=0.01)
    camera([(1, (0, -dist, 1.0), (0, 0, 0.85)), (n, (0, -dist + 0.15, 1.0), (0, 0, 0.85))], lens=50, fstop=2.8)


def shot_board_100(n):
    _chalk(n, 100, 3.3)


def shot_board_200(n):
    _chalk(n, 200, 3.0)


def shot_board_300(n):
    _chalk(n, 300, 2.7)


def shot_poster(n):
    world("#2b2455", 0.6)
    sun(0.8, rot=(55, 0, -25), hexstr="#b9b4ff")
    box((12, 0.2, 9), (0, 0.2, 4.5), "#4a3f7a", ol=False)
    box((12, 12, 0.1), (0, -5.9, -0.05), "#3a3166", ol=False)
    for i in range(22):  # brick courses
        box((12, 0.02, 0.025), (0, 0.095, 0.2 + i * 0.3), "#3f3672", ol=False)
        for j in range(-8, 9):
            box((0.025, 0.02, 0.3), (j * 0.7 + (0.35 if i % 2 else 0), 0.095, 0.35 + i * 0.3), "#3f3672", ol=False)
    box((1.5, 0.03, 2.3), (0, 0.07, 1.6), "#f7ecd0", rot=(0, 2, 0), ol=0.012)
    box((1.36, 0.03, 0.55), (0, 0.05, 2.42), "#a8323a", rot=(0, 2, 0), ol=False)
    text("CITY CHESS", 0.2, (0, 0.03, 2.42), "#f7ecd0", rot=(90, 2, 0), font="black")
    text("CHAMPIONSHIP", 0.155, (0, 0.03, 1.98), "#2b2455", rot=(90, 2, 0), font="black")
    k = king((0, -0.05, 1.0), mat("#2b2455"))
    k.scale = (4.0, 1.2, 4.0)
    text("ONE WINNER", 0.11, (0, 0.03, 0.72), "#a8323a", rot=(90, 2, 0), font="bold")
    for sx, sz in ((-0.68, 2.68), (0.68, 2.72), (-0.72, 0.5), (0.66, 0.52)):
        box((0.22, 0.02, 0.08), (sx, 0.04, sz), "#e2d9b8", rot=(0, 40 * (1 if sx * (sz - 1.6) > 0 else -1), 0), ol=False)
    # street lamp lighting the poster
    cyl(0.04, 3.4, (1.25, -0.25, 1.7), "#2a2a3a", ol=0.012)
    cyl(0.2, 0.14, (1.25, -0.25, 3.4), "#2a2a3a", r2=0.06, ol=0.012)
    sph(0.13, (1.25, -0.25, 3.26), mat("#fff0c0", emit=10), ol=False)
    lamp((0.8, -1.2, 3.0), 420, "#ffe2a8", radius=0.3)
    camera([(1, (0.3, -4.9, 1.75), (0, 0, 1.6)), (n, (0, -3.6, 1.65), (0, 0, 1.6))], lens=50)


def shot_trophy(n):
    hall(banner=False)
    pedestal()
    t = trophy((0, 0, 1.06))
    t.scale = (1.7, 1.7, 1.7)
    lamp((0.8, -1.4, 2.6), 300, "#fff0c0", radius=0.2)
    key(t, 1, rot=(0, 0, -25))
    key(t, n, rot=(0, 0, 25))
    for i, (p, fr) in enumerate((((0.3, -0.36, 2.0), 0.25), ((-0.28, -0.36, 1.75), 0.5), ((0.1, -0.3, 1.45), 0.75))):
        sparkle(p, int(n * fr), 0.2)
    camera([(1, (-0.5, -3.9, 1.5), (0, 0, 1.25)), (n, (0.4, -3.2, 1.45), (0, 0, 1.3))], lens=50, fstop=2.8)


def shot_signup(n):
    world("#2b2455", 0.6)
    lamp((0.4, -0.5, 1.2), 160, "#ffe2a8", radius=0.2)
    box((3, 3, 0.05), (0, 0, -0.025), "#8a5a3c", ol=False)
    for y in (-0.5, 0.1, 0.7):
        box((3, 0.006, 0.002), (0, y, 0.001), "#7a4e34", ol=False)
    box((0.5, 0.68, 0.012), (0, 0, 0.006), "#6a4a34", ol=0.006)
    box((0.44, 0.6, 0.004), (0, -0.01, 0.014), PAPER, ol=False)
    box((0.16, 0.05, 0.02), (0, 0.31, 0.02), "#9aa0a8", ol=0.004)
    text("SIGN UP", 0.058, (0, 0.21, 0.018), "#a8323a", rot=(0, 0, 0), font="black")
    names = ("M. Okafor", "T. Lindqvist", "R. Banerjee", "P. Castellano")
    for i, nm in enumerate(names):
        text(nm, 0.04, (-0.19, 0.12 - i * 0.075, 0.018), "#55506a", rot=(0, 0, 0), font="hand", align="LEFT")
        box((0.4, 0.002, 0.001), (0, 0.095 - i * 0.075, 0.017), "#b9b2a0", ol=False)
    y = 0.12 - 4 * 0.075
    box((0.4, 0.002, 0.001), (0, y - 0.025, 0.017), "#b9b2a0", ol=False)
    text("Walter", 0.05, (-0.19, y, 0.018), INK, rot=(0, 0, 0), font="hand", align="LEFT")
    f0, f1 = int(n * 0.15), int(n * 0.6)
    wipe(None, -0.2, 0.0, y + 0.003, 0.05, 0.0205, PAPER, f0, f1)
    hand = pen_hand()
    key(hand, 1, loc=(-0.2, y - 0.1, 0.14))
    key(hand, f0, loc=(-0.14, y - 0.07, 0.1))
    key(hand, f1, loc=(0.03, y - 0.07, 0.1))
    key(hand, n, loc=(0.22, y - 0.16, 0.16))
    camera([(1, (0, -0.4, 1.3), (0, -0.02, 0)), (n, (0, -0.38, 1.16), (0, -0.04, 0))], lens=50)


def shot_laugh(n):
    hall()
    spots = ((-0.95, 0.5, 14), (-0.3, 0.9, 5), (0.4, 0.8, -6), (1.0, 0.45, -16))
    for i, (x, y, rz) in enumerate(spots):
        c = character(loc=(x, y, 0), rotz=rz, mouth="open", **PEOPLE[i])
        laugh(c, n, i)
        key(c.handL, 1, loc=(-0.12, -0.24, 0.85))
        key(c.handR, 1, loc=(0.12, -0.24, 0.85))
        if i == 3:
            key(c.handL, 1, loc=(-0.3, -0.2, 0.9))
            key(c.handL, 9, loc=(-0.5, -0.4, 1.25))
        for f in range(1, n + 10, 10):
            key(c.head, f, rot=(-14 if (f // 10 + i) % 2 else 6, 0, 0))
    k = character(loc=(0.05, -0.1, 0), mouth="open", **{**KID})
    laugh(k, n, 1)
    key(k.handR, 1, loc=(0.4, -0.3, 1.2))
    camera([(1, (0, -4.0, 1.35), (0, 0.4, 1.15)), (n, (0, -3.5, 1.3), (0, 0.4, 1.15))], lens=50)


def shot_round_one(n):
    hall()
    chess_table()
    h = seat(-1, mouth="flat", brows=-14, **HERO)
    o = seat(1, mouth="smile", **PEOPLE[3])
    reach(o, o.handL, 1, (0.47, -0.26, 0.7))
    reach(o, o.handR, 1, (0.5, 0.28, 0.7))
    reach(h, h.handL, 1, (-0.5, 0.28, 0.7))
    q = king((-0.16, -0.1, 0.652), mat(CREAM))
    a, b = int(n * 0.3), int(n * 0.5)
    key(q, a, loc=(-0.16, -0.1, 0.652))
    key(q, b - 3, loc=(0.03, -0.03, 0.8))
    key(q, b, loc=(0.09, -0.03, 0.652))
    reach(h, h.handR, 1, (-0.47, -0.26, 0.72))
    reach(h, h.handR, a, (-0.16, -0.1, 0.82))
    reach(h, h.handR, b - 3, (0.03, -0.03, 0.97))
    reach(h, h.handR, b, (0.09, -0.03, 0.82))
    reach(h, h.handR, n, (-0.45, -0.26, 0.74))
    # pieces jump when the king lands
    for x, y, m in ((0.2, 0.1, DARK), (0.25, -0.15, DARK), (-0.2, 0.15, CREAM)):
        p = pawn((x, y, 0.652), mat(m))
        key(p, b, loc=(x, y, 0.652))
        key(p, b + 3, loc=(x, y, 0.71))
        key(p, b + 6, loc=(x, y, 0.652))
    sparkle((0.09, -0.2, 0.8), b + 1, 0.3)
    camera([(1, (1.2, -3.3, 1.6), (-0.4, 0, 0.98)), (n, (1.0, -2.7, 1.45), (-0.4, 0, 0.98))], lens=50, fstop=4.0)


def shot_shock(n):
    hall()
    chess_table()
    o = character(loc=(0, 0.9, 0), sit=True, mouth="open", brows=16, **PEOPLE[3])
    key(o.handL, 1, loc=(-0.32, -0.3, 0.72))
    key(o.handR, 1, loc=(0.32, -0.3, 0.72))
    key(o.handL, 12, loc=(-0.36, -0.12, 1.3))
    key(o.handR, 12, loc=(0.36, -0.12, 1.3))
    k = king((0.05, 0.12, 0.652), mat(DARK))
    key(k, 4, rot=(0, 0, 0))
    key(k, 10, rot=(10, 88, 0))
    key(o.head, 1, scale=1.0)
    key(o.head, 8, scale=1.14)
    key(o.head, 14, scale=1.05)
    for f in range(16, n + 4, 4):
        key(o.head, f, rot=(0, 0, 4 if f % 8 else -4))
    camera([(1, (0, -2.0, 1.3), (0, 0.6, 1.1)), (n, (0, -1.45, 1.25), (0, 0.6, 1.12))], lens=50, fstop=2.8)


def shot_tally(n):
    hall(banner=False, crowd=False)
    box((2.0, 0.1, 2.9), (0, 3.0, 1.9), "#1f1b3a", ol=0.03)
    box((2.2, 0.14, 0.12), (0, 3.0, 3.4), "#f0bf3a", ol=0.012)
    gold = mat("#f0bf3a", emit=0.5)
    text("WALTER", 0.3, (0, 2.94, 3.0), gold, font="black")
    box((1.6, 0.02, 0.02), (0, 2.94, 2.74), gold, ol=False)
    for i in range(5):
        z = 2.45 - i * 0.37
        text(f"ROUND {i + 1}", 0.17, (-0.82, 2.94, z), mat("#f4f1ea", emit=0.3), align="LEFT")
        w = text("WIN", 0.19, (0.5, 2.94, z), mat("#6fe08a", emit=0.8), font="black")
        f = 1 if i == 0 else int(n * (0.08 + 0.2 * i))
        show(w, 1, i == 0)
        if i:
            show(w, f, True)
            key(w, f, scale=1.6)
            key(w, f + 4, scale=1.0)
    lamp((0, 0.5, 2.6), 300, "#ffe9c4", radius=0.4)
    camera([(1, (0.2, -2.6, 2.2), (0, 3, 2.3)), (n, (0, -2.1, 1.95), (0, 3, 2.0))], lens=50)


def shot_hall_row(n):
    hall()
    for i in range(4):
        y = i * 1.9
        chess_table((0.5, y, 0), pieces=False, clock=i < 2)
        o = character(loc=(1.36, y, 0), rotz=-62, sit=True, mouth="frown" if i % 2 else "open",
                      brows=14, **PEOPLE[(i + 3) % 7])
        key(o.handL, 1, loc=(-0.3, -0.3, 0.7))
        key(o.handR, 1, loc=(0.3, -0.3, 0.7))
        k = king((0.55, y - 0.05, 0.66), mat(DARK))
        k.rotation_euler = (0.3 * i, 1.5, 0.5 * i)
        king((0.42, y + 0.05, 0.652), mat(CREAM))
    h = character(loc=(-0.75, 1.4, 0), rotz=0, mouth="smile", **HERO)
    walk(h, 1, n, (-0.75, 1.6, 0), (-0.75, -1.0, 0), step=6)
    camera([(1, (-0.9, -4.6, 1.8), (0.3, 1.2, 0.95)), (n, (-0.5, -3.6, 1.6), (0.3, 1.2, 0.95))], lens=40)


def _hero_at_desk(mouth="flat"):
    study()
    desk()
    h = character(loc=(0, 0.5, 0), sit=True, mouth=mouth, **HERO)
    box((0.42, 0.3, 0.02), (0, -0.05, 0.765), PAPER, ol=0.006)
    box((0.004, 0.3, 0.004), (0, -0.05, 0.777), "#b9b2a0", ol=False)
    for i, c in enumerate(("#c8473f", "#6a7fd1", "#e2b33c", "#5aa66a")):
        box((0.3, 0.22, 0.045), (-0.65, 0.08, 0.78 + i * 0.047), c, rot=(0, 0, 8 * i - 10), ol=0.006)
    return h


def shot_study_wide(n):
    h = _hero_at_desk()
    notebook_wall(y=1.5, x0=0.2, x1=2.4, z0=0.9, rows=4)
    key(h.handL, 1, loc=(-0.2, -0.5, 0.86))
    pen = cyl(0.008, 0.2, (0, 0, 0), "#e2b33c", ol=0.004)
    pen.parent = h.handR
    pen.location = (-0.03, -0.02, 0.03)
    pen.rotation_euler = (math.radians(35), math.radians(25), 0)
    for i, f in enumerate(range(1, n + 5, 5)):
        key(h.handR, f, loc=(0.06 + 0.07 * (i % 2), -0.52 - 0.01 * (i % 3), 0.86))
    key(h.head, 1, rot=(18, 0, 0))
    camera([(1, (-0.4, -4.4, 1.9), (0.1, 0.3, 1.25)), (n, (-0.1, -3.2, 1.55), (0.05, 0.3, 1.15))], lens=50)


def shot_notebook(n):
    world("#241f4a", 0.5)
    lamp((0.35, 0.25, 0.7), 60, "#ffd58a", radius=0.1)
    box((3, 3, 0.05), (0, 0, -0.025), "#a9744a", ol=False)
    box((0.5, 0.66, 0.02), (0, 0, 0.01), "#c8473f", ol=0.006)
    box((0.46, 0.62, 0.004), (0, 0, 0.022), PAPER, ol=False)
    text("Opponent No. 147", 0.036, (0, 0.265, 0.026), INK, rot=(0, 0, 0), font="hand")
    box((0.3, 0.002, 0.001), (0, 0.24, 0.025), INK, ol=False)
    board_squares(0.2, (0, 0.115, 0.026), a=PAPER, b="#9aa0b8")
    box((0.206, 0.206, 0.001), (0, 0.115, 0.0245), INK, ol=False)
    for i, j, m in ((1, 2, DARK), (-2, -1, DARK), (2, -3, "#c8473f"), (-1, 3, DARK), (0, 0, "#c8473f")):
        sph(0.009, (0.0125 + i * 0.025, 0.1275 + j * 0.025, 0.028), m, scale=(1, 1, 0.3), ol=False)
    moves = ("1. e4  e5      opens the same way", "2. Nf3  Nc6   always the knight",
             "3. Bc4  h6?   wastes a move here", "4. d4  ...       panics under pressure",
             "5. trades queens early. every time.")
    hand = pen_hand()
    for i, mv in enumerate(moves):
        y = -0.03 - i * 0.052
        text(mv, 0.027, (-0.205, y, 0.026), INK, rot=(0, 0, 0), font="hand", align="LEFT")
        box((0.42, 0.0015, 0.001), (0, y - 0.018, 0.0245), "#c9c2b0", ol=False)
        f0, f1 = int(n * (0.06 + 0.17 * i)), int(n * (0.06 + 0.17 * (i + 1)))
        wipe(None, -0.215, 0.215, y + 0.002, 0.036, 0.0285, PAPER, f0 + 1, f1 - 2)
        key(hand, f0 + 1, loc=(-0.15, y - 0.07, 0.1))
        key(hand, f1 - 2, loc=(0.26, y - 0.07, 0.1))
    camera([(1, (0, -0.42, 1.36), (0, 0.0, 0)), (n, (0, -0.4, 1.22), (0, -0.02, 0))], lens=50)


def shot_shelves(n):
    world("#241f4a", 0.5)
    sun(0.5, rot=(50, 0, -30), hexstr="#b9b4ff")
    box((16, 16, 0.1), (0, 0, -0.05), "#553a58", ol=False)
    box((16, 0.2, 9), (0, 1.75, 4.5), "#4a3f7a", ol=False)
    notebook_wall(y=1.5, x0=-1.7, x1=1.7, z0=0.2, rows=8)
    lamp((0.6, -1.5, 2.4), 500, "#ffd58a", radius=0.4)
    lamp((-1.2, -2.5, 1.2), 250, "#cfc4ff", radius=0.5)
    h = character(loc=(-1.1, 0.75, 0), rotz=90, **HERO)
    walk(h, 1, n, (-1.3, 0.75, 0), (0.5, 0.75, 0), step=7, swing=24)
    camera([(1, (0.3, -1.0, 2.2), (0.3, 1.5, 2.3)), (n, (0, -5.4, 2.1), (0, 1.5, 2.0))], lens=45)


def shot_hero_face(n):
    h = _hero_at_desk(mouth="smile")
    notebook_wall(y=1.5, x0=0.2, x1=2.4, z0=0.9, rows=4)
    key(h.handL, 1, loc=(-0.2, -0.5, 0.86))
    key(h.handR, 1, loc=(0.2, -0.5, 0.86))
    a, b = int(n * 0.45), int(n * 0.6)
    key(h.head, 1, rot=(14, 0, 0))
    key(h.head, a, rot=(14, 0, 0))
    key(h.head, b, rot=(0, 0, 0))
    # he pushes his glasses up and raises his brows
    key(h.handR, b, loc=(0.2, -0.5, 0.86))
    key(h.handR, b + 8, loc=(0.2, -0.36, 1.3))
    key(h.handR, b + 16, loc=(0.2, -0.36, 1.3))
    key(h.handR, b + 26, loc=(0.2, -0.5, 0.86))
    for br in h.brows:
        z = br.location[2]
        key(br, b, loc=(br.location[0], br.location[1], z))
        key(br, b + 8, loc=(br.location[0], br.location[1], z + 0.035))
    camera([(1, (0.1, -2.0, 1.45), (0, 0.4, 1.22)), (n, (0, -1.55, 1.38), (0, 0.45, 1.22))], lens=50, fstop=2.0)


def shot_last_dollar(n):
    hall()
    pedestal()
    dollar((0, -0.05, 1.062), rotz=14, note=True, s=1.25)
    lamp((0.6, -1.2, 2.6), 300, "#fff0c0", radius=0.2)
    for i, (x, y) in enumerate(((-1.25, 1.3), (-0.5, 1.7), (0.45, 1.75), (1.2, 1.25))):
        c = character(loc=(x, y, 0), rotz=-x * 12, mouth="open" if i % 2 else "frown", brows=14, **PEOPLE[i + 2])
        for f in range(1 + i * 3, n + 12, 12):
            key(c.head, f, rot=(10, 0, 5 if (f // 12) % 2 else -5))
    camera([(1, (0, -4.2, 1.7), (0, 0.3, 1.2)), (n, (0, -1.9, 1.75), (0, 0, 1.06))], lens=50, fstop=2.8)


def shot_last_note(n):
    world("#2b2455", 0.6)
    lamp((0.3, -0.3, 0.9), 90, "#fff0c0", radius=0.15)
    _bill_close(n, "#a8323a", ((2, int(n * 0.16)), (int(n * 0.18), int(n * 0.42))), hand=False)
