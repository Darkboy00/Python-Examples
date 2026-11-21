"""Scenes for 'The Worst Chess Player'. Each shot_<id>(n) builds a full
scene animated over n frames (the length comes from the narration)."""
import math
import random

import bmesh

from toonkit import (arc, bob, box, camera, character, cyl, empty, hand_world, key, lamp, mat,
                     show, sph, sun, text, torus, world, _finish)

HERO = dict(coat="#3f8f86", hat="cap", hat_col="#8a5a3c", glasses=True, bowtie="#c8473f")
PEOPLE = [
    dict(coat="#d9793f", hair="short", hair_col="#3b2a20"),
    dict(coat="#6a7fd1", hat="beanie", hat_col="#c8473f"),
    dict(coat="#c9a23a", hair="long", hair_col="#7a3f22"),
    dict(coat="#8d5fb0", hat="fedora", hat_col="#4a4a55"),
    dict(coat="#5aa66a", hair="short", hair_col="#d8c27a"),
    dict(coat="#c45a7a", hair="bun", hair_col="#2f2f38"),
    dict(coat="#4f8fb8", hat="cap", hat_col="#2f3f5a"),
]
GRANNY = dict(coat="#9a6fc0", hair="bun", hair_col="#c9c9d2", glasses=True)
KID = dict(coat="#e2b33c", hat="beanie", hat_col="#4f8fb8", s=0.62)
CREAM, DARK = "#f1e6c8", "#3b3340"
INK = "#1d2a6b"


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


def board_squares(size, loc, parent=None, a=CREAM, b="#7a5a48"):
    bm = bmesh.new()
    q = size / 8
    for i in range(8):
        for j in range(8):
            x, y = -size / 2 + i * q, -size / 2 + j * q
            f = bm.faces.new([bm.verts.new(p) for p in ((x, y, 0), (x + q, y, 0), (x + q, y + q, 0), (x, y + q, 0))])
            f.material_index = (i + j) % 2
    ob = _finish("squares", bm, mat(b), loc, (0, 0, 0), (1, 1, 1), False, False, 0, parent)
    ob.data.materials.append(mat(a))
    return ob


def chess_table(loc=(0, 0, 0), pieces=True, top="#cfc8ba"):
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
    box((0.315, 0.115, 0.002), (0, 0, 0.006), "#c2e2b4", ol=False, parent=r)
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


def tree(loc, s=1.0, canopy="#4fa35a"):
    r = empty(loc)
    r.scale = (s, s, s)
    cyl(0.14, 1.5, (0, 0, 0.75), "#7a5536", r2=0.1, parent=r, ol=0.02)
    return [sph(rr, p, canopy, parent=r, ol=0.025) for rr, p in
            ((0.95, (0, 0, 2.2)), (0.7, (-0.7, 0.1, 1.9)), (0.7, (0.7, -0.1, 1.95)), (0.6, (0.1, 0, 3.0)))]


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
    return r, num


def trophy(loc, parent=None):
    r = empty(loc, parent)
    g = mat("#f0bf3a", rough=0.35)
    cyl(0.16, 0.06, (0, 0, 0.03), "#3b3340", parent=r)
    cyl(0.11, 0.05, (0, 0, 0.085), g, parent=r)
    cyl(0.03, 0.16, (0, 0, 0.19), g, parent=r)
    cyl(0.07, 0.3, (0, 0, 0.42), g, r2=0.2, parent=r)
    for sx in (-1, 1):
        arc(0.1, -80 if sx > 0 else 100, 80 if sx > 0 else 260, 0.016, (sx * 0.16, 0, 0.43), "#f0bf3a", parent=r)
    return r


# ------------------------------------------------------------------- sets
def park(ground="#8fcf6e", canopy="#4fa35a", trees=True):
    world("#c4e6ef", 1.0)
    sun(3.0, rot=(48, 0, 32))
    box((90, 90, 0.1), (0, 0, -0.05), ground, ol=False)
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
        for wx in (-1.3, 0, 1.3):
            for wz in range(2, int(h), 2):
                box((0.7, 0.1, 0.9), (x + wx, 16.47, wz), "#5f7f9a", ol=False)
    # lamp post and bench
    cyl(0.05, 2.6, (2.2, 1.5, 1.3), "#3b4a44", ol=0.015)
    sph(0.18, (2.2, 1.5, 2.7), "#fff3c4", ol=0.015)
    box((1.4, 0.4, 0.06), (-1.9, 1.6, 0.42), "#a9744a", bevel=0.01)
    box((1.4, 0.06, 0.4), (-1.9, 1.8, 0.75), "#a9744a", bevel=0.01)
    for sx in (-0.55, 0.55):
        box((0.06, 0.36, 0.42), (-1.9 + sx, 1.6, 0.21), "#3b4a44")
    return out


def hall(banner=True):
    world("#2b2455", 0.55)
    sun(0.7, rot=(55, 0, -25), hexstr="#b9b4ff")
    box((24, 24, 0.1), (0, 0, -0.05), "#6b4a5e", ol=False)
    box((24, 0.2, 9), (0, 6, 4.5), "#3f3672", ol=False)
    box((24, 0.3, 1.0), (0, 5.9, 0.5), "#2e2757", ol=False)
    for x in (-4.2, 4.2):
        box((0.5, 0.5, 9), (x, 5.8, 4.5), "#51468a", ol=0.03)
    if banner:
        box((5.0, 0.06, 1.3), (0, 5.8, 3.6), "#a8323a", ol=0.03)
        text("CITY CHESS\nCHAMPIONSHIP", 0.42, (0, 5.74, 3.6), mat("#f0bf3a", emit=0.3), font="black", spacing=0.9)
    for x in (-2.2, 0, 2.2):
        cyl(0.012, 1.6, (x, 2.2, 4.4), "#141414", ol=False)
        cyl(0.3, 0.18, (x, 2.2, 3.6), "#f0bf3a", r2=0.08, ol=0.015)
        sph(0.1, (x, 2.2, 3.5), mat("#fff0c0", emit=8), ol=False)
        lamp((x, 2.2, 3.3), 260)
    lamp((0.5, -3.0, 3.2), 900, "#ffe9c4", radius=0.6)


def study():
    world("#241f4a", 0.45)
    sun(0.5, rot=(50, 0, -30), hexstr="#b9b4ff")
    box((16, 16, 0.1), (0, 0, -0.05), "#553a58", ol=False)
    box((16, 0.2, 7), (0, 1.7, 3.5), "#4a3f7a", ol=False)
    box((16, 0.25, 0.9), (0, 1.62, 0.45), "#3a3166", ol=False)
    # window with moon
    box((1.0, 0.1, 1.3), (-1.15, 1.6, 2.15), "#f1e6c8", ol=0.02)
    box((0.86, 0.1, 1.16), (-1.15, 1.56, 2.15), mat("#27306e", emit=0.6), ol=False)
    sph(0.16, (-1.0, 1.52, 2.4), mat("#fff6cf", emit=4), scale=(1, 0.2, 1), ol=False)
    box((0.04, 0.1, 1.16), (-1.15, 1.5, 2.15), "#f1e6c8", ol=False)
    box((0.86, 0.1, 0.04), (-1.15, 1.5, 2.15), "#f1e6c8", ol=False)
    lamp((0.2, -2.6, 2.6), 420, "#cfc4ff", radius=0.6)


def desk(lamp_on=True):
    box((1.9, 0.8, 0.07), (0, 0, 0.72), "#a9744a", bevel=0.012)
    for sx in (-0.85, 0.85):
        for sy in (-0.32, 0.32):
            box((0.07, 0.07, 0.7), (sx, sy, 0.35), "#8a5a3c")
    cyl(0.1, 0.03, (0.72, 0.15, 0.77), "#3b4a44")
    cyl(0.015, 0.4, (0.72, 0.15, 0.97), "#3b4a44", ol=False)
    cyl(0.07, 0.16, (0.66, 0.1, 1.2), "#e2b33c", r2=0.17, rot=(25, -35, 0), ol=0.012)
    if lamp_on:
        lamp((0.5, -0.05, 1.12), 110, "#ffd58a", radius=0.08)


def notebook_wall(y=1.5, x0=-2.0, x1=2.0, z0=0.25, rows=7):
    random.seed(7)
    cols = ("#c8473f", "#3f8f86", "#e2b33c", "#6a7fd1", "#d9793f", "#8d5fb0", "#5aa66a", "#4f8fb8")
    box((x1 - x0 + 0.2, 0.34, 0.08), ((x0 + x1) / 2, y, z0 - 0.04), "#8a5a3c", ol=0.015)
    for r in range(rows):
        z = z0 + r * 0.5
        box((x1 - x0 + 0.2, 0.34, 0.05), ((x0 + x1) / 2, y, z + 0.45), "#8a5a3c", ol=0.015)
        x = x0
        while x < x1 - 0.06:
            w = random.choice((0.06, 0.07, 0.08, 0.09))
            h = random.uniform(0.33, 0.41)
            tilt = random.choice((0, 0, 0, 0, 4))
            box((w, 0.24, h), (x + w / 2, y - 0.02, z + h / 2), random.choice(cols), rot=(0, tilt, 0), ol=0.006)
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
    w1 = character(loc=(-0.5, 1.5, 0), rotz=8, mouth="smile", **PEOPLE[1])
    w2 = character(loc=(0.75, 1.7, 0), rotz=-10, mouth="smile", **PEOPLE[2])
    bob(w1.root, n, 0.015, 16)
    bob(w2.root, n, 0.015, 16, phase=1)
    reach(o, o.handL, int(n * 0.35), (0.25, -0.1, 0.78))
    reach(o, o.handL, int(n * 0.55), (0.05, -0.05, 0.8))
    reach(o, o.handL, int(n * 0.75), (0.47, -0.26, 0.7))
    key(h.head, int(n * 0.55), rot=(0, 0, 0))
    key(h.head, int(n * 0.8), rot=(12, 0, 0))
    camera([(1, (0.5, -6.4, 2.3), (0, 0.3, 1.25)), (n, (0.1, -4.3, 1.5), (0, 0, 0.95))], lens=50)


def shot_king_falls(n):
    park()
    h, o = game(n, PEOPLE[0])
    k = king((-0.09, -0.03, 0.652), mat(CREAM))
    key(k, 3, rot=(0, 0, 0))
    key(k, 9, rot=(12, 88, 0))
    key(k, 12, rot=(12, 80, 0))
    key(k, 15, rot=(12, 88, 0))
    reach(o, o.handL, 1, (0.02, -0.03, 0.82))
    reach(o, o.handL, 8, (0.3, -0.15, 0.75))
    camera([(1, (0.0, -1.25, 1.02), (-0.03, 0, 0.7)), (n, (0.0, -1.1, 0.98), (-0.03, 0, 0.7))], lens=55, fstop=2.0)


def shot_pay_dollar(n):
    park()
    h, o = game(n, PEOPLE[0])
    d, _ = dollar((-0.3, -0.24, 0.665), rotz=8)
    a, b = int(n * 0.2), int(n * 0.7)
    key(d, a, loc=(-0.3, -0.24, 0.665))
    key(d, b, loc=(0.12, -0.24, 0.665))
    reach(h, h.handR, a, (-0.5, -0.24, 0.72))
    reach(h, h.handR, b, (-0.08, -0.24, 0.72))
    reach(h, h.handR, n, (-0.45, -0.24, 0.72))
    camera([(1, (1.3, -3.7, 1.8), (-0.35, 0, 0.98)), (n, (1.1, -3.2, 1.65), (-0.35, 0, 0.95))], lens=50, fstop=4.0)


def _bill_close(n, base, first):
    """Top-down close-up of the bill; the two handwritten lines appear at `first`."""
    box((3, 3, 0.05), (0, 0, -0.025), base, ol=False)
    d, lines = dollar((0, 0, 0), rotz=14, note=True, s=1.0)
    for i, ln in enumerate(lines):
        show(ln, 1, False)
        show(ln, int(n * (first + 0.14 * i)), True)
    camera([(1, (0.0, -0.2, 1.2), (0, 0.0, 0)), (n, (0.0, -0.17, 1.0), (0, 0.0, 0))], lens=50)
    return d


def shot_bill_note(n):
    world("#c4e6ef", 1.0)
    sun(3.0, rot=(35, 0, 30))
    _bill_close(n, "#cfc8ba", 0.6)
    board_squares(0.5, (-0.15, 0.42, 0.012))
    box((0.54, 0.54, 0.02), (-0.15, 0.42, 0.0), "#5a3f30", ol=0.006)
    pawn((0.02, 0.23, 0.012), mat(DARK))
    cyl(0.009, 0.2, (0.2, -0.2, 0.012), "#e2b33c", rot=(90, 0, 62), ol=0.004)


def shot_notice(n):
    park(trees=True)
    for sx in (-1, 1):
        cyl(0.05, 1.9, (sx * 0.55, 0.2, 0.95), "#8a5a3c")
    box((1.35, 0.08, 1.0), (0, 0.2, 1.45), "#a9744a", bevel=0.012)
    box((0.86, 0.02, 0.84), (0, 0.14, 1.45), "#f7f1dc", rot=(0, -3, 0), ol=0.006)
    text("WORST\nPLAYER\nIN THE CITY", 0.125, (0, 0.12, 1.61), "#b8322a", rot=(90, -3, 0), font="black", spacing=0.9)
    sph(0.1, (0, 0.11, 1.2), "#f4f1ea", scale=(1, 0.2, 1), ol=0.006)
    sph(0.105, (0, 0.105, 1.25), "#8a5a3c", scale=(1, 0.2, 0.5), ol=False)
    for sx in (-1, 1):
        sph(0.014, (sx * 0.035, 0.085, 1.19), "#141414", ol=False)
    a = character(loc=(-0.78, -0.55, 0), rotz=25, mouth="open", **PEOPLE[3])
    b = character(loc=(0.78, -0.5, 0), rotz=-25, mouth="open", **PEOPLE[4])
    laugh(a, n)
    laugh(b, n, 1)
    key(b.handL, 1, loc=(-0.45, -0.25, 1.15))
    camera([(1, (0, -5.2, 1.5), (0, 0, 1.2)), (n, (0, -4.4, 1.45), (0, 0, 1.22))], lens=50)


def _beaten_by(n, opp, kid=False):
    park()
    chess_table()
    h = seat(-1, mouth="smile", **HERO)
    kw = dict(opp)
    s = kw.pop("s", 1.0)
    o = character(loc=(0.86, 0, 0.26 if kid else 0), rotz=-62, sit=not kid, mouth="open", s=s, **kw)
    d, _ = dollar((-0.25, -0.24, 0.665), rotz=8)
    key(d, 1, loc=(-0.25, -0.24, 0.665))
    key(d, int(n * 0.6), loc=(0.14, -0.24, 0.665))
    reach(h, h.handR, 1, (-0.46, -0.24, 0.72))
    reach(h, h.handR, int(n * 0.6), (-0.07, -0.24, 0.72))
    reach(h, h.handL, 1, (-0.5, 0.28, 0.7))
    k = king((-0.09, 0.02, 0.652), mat(CREAM))
    k.rotation_euler = (0.2, 1.5, 0)
    # winner throws both hands up
    for hand, sx in ((o.handL, -1), (o.handR, 1)):
        key(hand, 1, loc=(sx * 0.34, -0.05, 0.6))
        key(hand, 7, loc=(sx * 0.42, -0.02, 1.75 if not kid else 1.9))
    bob(o.root, n, 0.04, 8)
    camera([(1, (-1.4, -3.9, 1.7), (0.25, 0, 1.0)), (n, (-1.2, -3.4, 1.55), (0.3, 0, 1.0))], lens=50)


def shot_kid(n):
    _beaten_by(n, KID, kid=True)


def shot_granny(n):
    _beaten_by(n, GRANNY)


def shot_queue(n):
    park()
    h, o = game(n, PEOPLE[5])
    for i in range(7):
        kw = PEOPLE[(i + 1) % len(PEOPLE)]
        c = character(loc=(1.5 + 0.22 * i, 0.5 + 0.85 * i, 0), rotz=22, mouth="smile", **kw)
        bob(c.root, n, 0.02, 12 + (i % 3) * 2, phase=i)
    camera([(1, (-0.6, -4.2, 1.6), (0.3, 0.2, 1.0)), (n, (-1.9, -4.6, 3.3), (1.4, 2.6, 0.9))], lens=42)


def shot_seasons(n):
    box((90, 90, 0.1), (0, 0, -0.05), "#8fcf6e", ol=False)
    snow = box((90, 90, 0.1), (0, 0, -0.045), "#f2f6fa", ol=False)
    world("#c4e6ef", 1.0)
    sun(3.0, rot=(48, 0, 32))
    cyl(2.7, 0.02, (0, 0, -0.005), "#ecdfc6", ol=False, seg=48)
    a, b = n // 3, 2 * n // 3
    for colr, f0, f1 in (("#4fa35a", 1, a), ("#e08a3a", a, b), ("#f2f6fa", b, n + 1)):
        parts = tree((-2.3, 3.2, 0), 1.35, colr) + tree((2.6, 4.2, 0), 1.2, colr)
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
    park()
    r, num = chalkboard(number)
    key(num, 1, scale=0.7)
    key(num, 5, scale=1.08)
    key(num, 8, scale=1.0)
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
    box((1.5, 0.03, 2.3), (0, 0.08, 1.6), "#f7ecd0", rot=(0, 2, 0), ol=0.012)
    box((1.36, 0.03, 0.55), (0, 0.06, 2.42), "#a8323a", rot=(0, 2, 0), ol=False)
    text("CITY CHESS", 0.2, (0, 0.03, 2.42), "#f7ecd0", rot=(90, 2, 0), font="black")
    text("CHAMPIONSHIP", 0.155, (0, 0.03, 1.98), "#2b2455", rot=(90, 2, 0), font="black")
    k = king((0, -0.05, 1.0), mat("#2b2455"))
    k.scale = (4.0, 1.2, 4.0)
    text("ONE WINNER", 0.11, (0, 0.03, 0.72), "#a8323a", rot=(90, 2, 0), font="bold")
    lamp((0.6, -1.6, 2.9), 420, "#ffe2a8", radius=0.3)
    camera([(1, (0.3, -4.6, 1.75), (0, 0, 1.6)), (n, (0, -3.5, 1.65), (0, 0, 1.6))], lens=50)


def shot_trophy(n):
    hall(banner=False)
    cyl(0.45, 1.0, (0, 0, 0.5), "#51468a")
    cyl(0.55, 0.06, (0, 0, 1.03), "#a8323a")
    t = trophy((0, 0, 1.06))
    t.scale = (1.7, 1.7, 1.7)
    box((0.62, 0.04, 0.24), (0, -0.46, 0.62), "#f0bf3a", ol=0.01)
    text("$50,000", 0.13, (0, -0.49, 0.62), "#2b2455", font="black")
    lamp((0.8, -1.4, 2.6), 300, "#fff0c0", radius=0.2)
    key(t, 1, rot=(0, 0, -25))
    key(t, n, rot=(0, 0, 25))
    camera([(1, (-0.5, -3.6, 1.5), (0, 0, 1.2)), (n, (0.4, -3.0, 1.45), (0, 0, 1.25))], lens=50, fstop=2.8)


def shot_signup(n):
    world("#2b2455", 0.6)
    lamp((0.4, -0.5, 1.2), 160, "#ffe2a8", radius=0.2)
    box((3, 3, 0.05), (0, 0, -0.025), "#8a5a3c", ol=False)
    box((0.5, 0.68, 0.012), (0, 0, 0.006), "#6a4a34", ol=0.006)
    box((0.44, 0.6, 0.004), (0, -0.01, 0.014), "#f7f1dc", ol=False)
    box((0.16, 0.05, 0.02), (0, 0.31, 0.02), "#9aa0a8", ol=0.004)
    text("SIGN UP", 0.058, (0, 0.21, 0.018), "#a8323a", rot=(0, 0, 0), font="black")
    names = ("M. Okafor", "T. Lindqvist", "R. Banerjee", "P. Castellano")
    for i, nm in enumerate(names):
        text(nm, 0.04, (-0.19, 0.12 - i * 0.075, 0.018), "#55506a", rot=(0, 0, 0), font="hand", align="LEFT")
        box((0.4, 0.002, 0.001), (0, 0.095 - i * 0.075, 0.017), "#b9b2a0", ol=False)
    y = 0.12 - 4 * 0.075
    box((0.4, 0.002, 0.001), (0, y - 0.025, 0.017), "#b9b2a0", ol=False)
    nm = text("Walter", 0.05, (-0.19, y, 0.018), INK, rot=(0, 0, 0), font="hand", align="LEFT")
    show(nm, 1, False)
    show(nm, int(n * 0.45), True)
    hand = sph(0.07, (0, 0, 0), "#f4f1ea", ol=0.008)
    pen = cyl(0.008, 0.22, (0, 0, 0), "#e2b33c", ol=0.004)
    pen.parent = hand
    pen.location = (-0.035, 0.03, -0.01)
    pen.rotation_euler = (math.radians(-55), math.radians(30), 0)
    key(hand, 1, loc=(-0.1, y - 0.06, 0.1))
    key(hand, int(n * 0.45), loc=(0.02, y - 0.06, 0.1))
    key(hand, n, loc=(0.2, y - 0.14, 0.14))
    camera([(1, (0, -0.4, 1.3), (0, -0.02, 0)), (n, (0, -0.38, 1.16), (0, -0.04, 0))], lens=50)


def shot_laugh(n):
    hall()
    spots = ((-0.95, 0.5, 14), (-0.3, 0.9, 5), (0.4, 0.8, -6), (1.0, 0.45, -16))
    for i, (x, y, rz) in enumerate(spots):
        c = character(loc=(x, y, 0), rotz=rz, mouth="open", **PEOPLE[i])
        laugh(c, n, i)
        key(c.handL, 1, loc=(-0.12, -0.24, 0.85))
        key(c.handR, 1, loc=(0.12, -0.24, 0.85))
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
    key(q, b - 3, loc=(0.03, -0.03, 0.76))
    key(q, b, loc=(0.09, -0.03, 0.652))
    reach(h, h.handR, 1, (-0.47, -0.26, 0.72))
    reach(h, h.handR, a, (-0.16, -0.1, 0.82))
    reach(h, h.handR, b - 3, (0.03, -0.03, 0.93))
    reach(h, h.handR, b, (0.09, -0.03, 0.82))
    reach(h, h.handR, n, (-0.45, -0.26, 0.74))
    camera([(1, (1.2, -3.3, 1.6), (-0.4, 0, 0.98)), (n, (1.0, -2.7, 1.45), (-0.4, 0, 0.98))], lens=50, fstop=4.0)


def shot_shock(n):
    hall()
    chess_table()
    o = character(loc=(0, 0.9, 0), sit=True, mouth="open", brows=16, **PEOPLE[3])
    key(o.handL, 1, loc=(-0.32, -0.3, 0.72))
    key(o.handR, 1, loc=(0.32, -0.3, 0.72))
    k = king((0.05, 0.12, 0.652), mat(DARK))
    key(k, 4, rot=(0, 0, 0))
    key(k, 10, rot=(10, 88, 0))
    key(o.head, 1, scale=1.0)
    key(o.head, 8, scale=1.12)
    key(o.head, 14, scale=1.05)
    camera([(1, (0, -2.0, 1.3), (0, 0.6, 1.1)), (n, (0, -1.45, 1.25), (0, 0.6, 1.12))], lens=50, fstop=2.8)


def shot_tally(n):
    hall(banner=False)
    box((2.0, 0.1, 2.9), (0, 3.0, 1.9), "#1f1b3a", ol=0.03)
    gold = mat("#f0bf3a", emit=0.5)
    text("WALTER", 0.3, (0, 2.94, 3.0), gold, font="black")
    box((1.6, 0.02, 0.02), (0, 2.94, 2.74), gold, ol=False)
    rows = 5
    for i in range(rows):
        z = 2.45 - i * 0.37
        text(f"ROUND {i + 1}", 0.17, (-0.82, 2.94, z), mat("#f4f1ea", emit=0.3), align="LEFT")
        w = text("WIN", 0.19, (0.5, 2.94, z), mat("#6fe08a", emit=0.8), font="black")
        show(w, 1, i == 0)
        if i:
            show(w, int(n * (0.08 + 0.2 * i)), True)
    lamp((0, 0.5, 2.6), 300, "#ffe9c4", radius=0.4)
    camera([(1, (0.2, -2.6, 2.2), (0, 3, 2.3)), (n, (0, -2.1, 1.95), (0, 3, 2.0))], lens=50)


def shot_hall_row(n):
    hall()
    for i in range(4):
        y = i * 1.9
        t = chess_table((0.5, y, 0), pieces=False)
        o = character(loc=(1.36, y, 0), rotz=-62, sit=True, mouth="frown" if i % 2 else "open",
                      brows=14, **PEOPLE[(i + 3) % 7])
        key(o.handL, 1, loc=(-0.3, -0.3, 0.7))
        key(o.handR, 1, loc=(0.3, -0.3, 0.7))
        k = king((0.55, y - 0.05, 0.66), mat(DARK))
        k.rotation_euler = (0.3 * i, 1.5, 0.5 * i)
        king((0.42, y + 0.05, 0.652), mat(CREAM))
    h = character(loc=(-0.75, -0.6, 0), rotz=-20, mouth="smile", **HERO)
    key(h.root, 1, loc=(-0.75, -0.6, 0))
    key(h.root, n, loc=(-0.75, -1.2, 0))
    bob(h.head, n, 0.02, 8)
    camera([(1, (-0.9, -4.6, 1.8), (0.3, 1.2, 0.95)), (n, (-0.5, -3.6, 1.6), (0.3, 1.2, 0.95))], lens=40)


def _hero_at_desk(mouth="flat"):
    study()
    desk()
    h = character(loc=(0, 0.5, 0), sit=True, mouth=mouth, **HERO)
    box((0.42, 0.3, 0.02), (0, -0.05, 0.765), "#f7f1dc", ol=0.006)
    box((0.004, 0.3, 0.004), (0, -0.05, 0.777), "#b9b2a0", ol=False)
    for i, c in enumerate(("#c8473f", "#6a7fd1", "#e2b33c", "#5aa66a")):
        box((0.3, 0.22, 0.045), (-0.65, 0.08, 0.78 + i * 0.047), c, rot=(0, 0, 8 * i - 10), ol=0.006)
    return h


def shot_study_wide(n):
    h = _hero_at_desk()
    notebook_wall(y=1.5, x0=0.2, x1=2.4, z0=0.9, rows=4)
    key(h.handL, 1, loc=(-0.2, -0.5, 0.86))
    for i, f in enumerate(range(1, n + 8, 8)):
        key(h.handR, f, loc=(0.1 + 0.05 * (i % 2), -0.52, 0.86))
    key(h.head, 1, rot=(18, 0, 0))
    camera([(1, (-0.4, -4.4, 1.9), (0.1, 0.3, 1.25)), (n, (-0.1, -3.2, 1.55), (0.05, 0.3, 1.15))], lens=50)


def shot_notebook(n):
    world("#241f4a", 0.5)
    lamp((0.35, 0.25, 0.7), 60, "#ffd58a", radius=0.1)
    box((3, 3, 0.05), (0, 0, -0.025), "#a9744a", ol=False)
    box((0.5, 0.66, 0.02), (0, 0, 0.01), "#c8473f", ol=0.006)
    box((0.46, 0.62, 0.004), (0, 0, 0.022), "#f7f1dc", ol=False)
    text("Opponent No. 147", 0.036, (0, 0.265, 0.026), INK, rot=(0, 0, 0), font="hand")
    box((0.3, 0.002, 0.001), (0, 0.24, 0.025), INK, ol=False)
    board_squares(0.2, (0, 0.115, 0.026), a="#f7f1dc", b="#9aa0b8")
    box((0.206, 0.206, 0.001), (0, 0.115, 0.0245), INK, ol=False)
    for i, j, m in ((1, 2, DARK), (-2, -1, DARK), (2, -3, "#c8473f"), (-1, 3, DARK), (0, 0, "#c8473f")):
        sph(0.009, (0.0125 + i * 0.025, 0.1275 + j * 0.025, 0.028), m, scale=(1, 1, 0.3), ol=False)
    moves = ("1. e4  e5      opens the same way", "2. Nf3  Nc6   always the knight",
             "3. Bc4  h6?   wastes a move here", "4. d4  ...       panics under pressure",
             "5. trades queens early. every time.")
    hand = sph(0.07, (0, 0, 0), "#f4f1ea", ol=0.008)
    pen = cyl(0.008, 0.22, (0, 0, 0), "#e2b33c", ol=0.004)
    pen.parent = hand
    pen.location = (-0.035, 0.03, -0.01)
    pen.rotation_euler = (math.radians(-55), math.radians(30), 0)
    for i, mv in enumerate(moves):
        y = -0.03 - i * 0.052
        t = text(mv, 0.027, (-0.205, y, 0.026), INK, rot=(0, 0, 0), font="hand", align="LEFT")
        f0, f1 = int(n * (0.08 + 0.17 * i)), int(n * (0.08 + 0.17 * (i + 1)))
        show(t, 1, False)
        show(t, f1, True)
        key(hand, f0 + 1, loc=(-0.15, y - 0.06, 0.1))
        key(hand, f1, loc=(0.2, y - 0.06, 0.1))
    camera([(1, (0, -0.42, 1.36), (0, 0.0, 0)), (n, (0, -0.4, 1.22), (0, -0.02, 0))], lens=50)


def shot_shelves(n):
    world("#241f4a", 0.5)
    sun(0.5, rot=(50, 0, -30), hexstr="#b9b4ff")
    box((16, 16, 0.1), (0, 0, -0.05), "#553a58", ol=False)
    box((16, 0.2, 9), (0, 1.75, 4.5), "#4a3f7a", ol=False)
    notebook_wall(y=1.5, x0=-1.7, x1=1.7, z0=0.2, rows=8)
    lamp((0.6, -1.5, 2.4), 500, "#ffd58a", radius=0.4)
    lamp((-1.2, -2.5, 1.2), 250, "#cfc4ff", radius=0.5)
    h = character(loc=(-0.55, 0.4, 0), rotz=180, **HERO)
    key(h.handR, 1, loc=(0.36, -0.25, 1.5))
    camera([(1, (0.3, -1.0, 2.2), (0.3, 1.5, 2.3)), (n, (0, -5.4, 2.1), (0, 1.5, 2.0))], lens=45)


def shot_hero_face(n):
    h = _hero_at_desk(mouth="smile")
    notebook_wall(y=1.5, x0=0.2, x1=2.4, z0=0.9, rows=4)
    key(h.handL, 1, loc=(-0.2, -0.5, 0.86))
    key(h.handR, 1, loc=(0.2, -0.5, 0.86))
    key(h.head, 1, rot=(14, 0, 0))
    key(h.head, int(n * 0.45), rot=(14, 0, 0))
    key(h.head, int(n * 0.6), rot=(0, 0, 0))
    camera([(1, (0.1, -2.0, 1.45), (0, 0.4, 1.22)), (n, (0, -1.55, 1.38), (0, 0.45, 1.22))], lens=50, fstop=2.0)


def shot_last_dollar(n):
    hall()
    cyl(0.45, 1.0, (0, 0, 0.5), "#51468a")
    cyl(0.55, 0.06, (0, 0, 1.03), "#a8323a")
    box((0.62, 0.04, 0.24), (0, -0.46, 0.62), "#f0bf3a", ol=0.01)
    text("$50,000", 0.13, (0, -0.49, 0.62), "#2b2455", font="black")
    dollar((0, -0.05, 1.062), rotz=14, note=True, s=1.25)
    lamp((0.6, -1.2, 2.6), 300, "#fff0c0", radius=0.2)
    for i, (x, y) in enumerate(((-1.25, 1.3), (-0.5, 1.7), (0.45, 1.75), (1.2, 1.25))):
        c = character(loc=(x, y, 0), rotz=-x * 12, mouth="open" if i % 2 else "frown", brows=14, **PEOPLE[i + 2])
    camera([(1, (0, -4.2, 1.7), (0, 0.3, 1.2)), (n, (0, -1.9, 1.75), (0, 0, 1.06))], lens=50, fstop=2.8)


def shot_last_note(n):
    world("#2b2455", 0.6)
    lamp((0.3, -0.3, 0.9), 90, "#fff0c0", radius=0.15)
    _bill_close(n, "#a8323a", 0.06)
