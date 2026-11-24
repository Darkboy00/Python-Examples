"""The Worst Chess Player — narration script. One entry per shot.

(shot_id, narration, pause_after_seconds). The shot_id maps to a
function `shot_<id>` in shots_chess.py.
"""
VOICE = "bm_george"
SPEED = 1.08

SHOTS = [
    ("park_wide",   "A man sat in the park, and lost at chess.", 0.15),
    ("king_falls",  "To everyone.", 0.3),
    ("pay_dollar",  "Every time he lost, he paid one dollar,", 0.1),
    ("bill_note",   "with the same words written on it: Good game. Play me again.", 0.35),
    ("notice",      "The regulars called him the worst player in the city.", 0.25),
    ("kid",         "Kids beat him.", 0.15),
    ("granny",      "Grandmothers beat him.", 0.2),
    ("queue",       "People lined up for an easy dollar.", 0.3),
    ("seasons",     "Years went by.", 0.25),
    ("board_100",   "One hundred losses.", 0.1),
    ("board_200",   "Two hundred.", 0.1),
    ("board_300",   "Three hundred.", 0.4),
    ("poster",      "Then came the City Championship.", 0.2),
    ("trophy",      "Fifty thousand dollars.", 0.25),
    ("signup",      "And he signed up.", 0.3),
    ("laugh",       "Everybody laughed.", 0.3),
    ("round_one",   "Until round one.", 0.2),
    ("shock",       "He won in twelve moves.", 0.25),
    ("tally",       "Then again. And again.", 0.15),
    ("hall_row",    "He beat every single one of them.", 0.45),
    ("study_wide",  "He never cared about the dollars.", 0.2),
    ("notebook",    "Every loss was a lesson. He wrote down every move they ever played.", 0.2),
    ("shelves",     "Three hundred notebooks. One for each opponent.", 0.3),
    ("hero_face",   "They played him once, for a dollar. He studied them for years.", 0.4),
    ("last_dollar", "And on the empty trophy stand, he left one dollar.", 0.3),
    ("last_note",   "Good game. Play me again.", 1.0),
]

# Sound effects: shot_id -> [(position in shot 0..1, effect name), ...]
SFX = {
    "king_falls": [(0.25, "thud")],
    "pay_dollar": [(0.25, "slide")],
    "bill_note": [(0.5, "scribble"), (0.7, "scribble")],
    "notice": [(0.0, "whoosh")],
    "kid": [(0.1, "pop")],
    "granny": [(0.1, "pop")],
    "queue": [(0.0, "whoosh")],
    "board_100": [(0.08, "ding")],
    "board_200": [(0.08, "ding")],
    "board_300": [(0.08, "ding")],
    "poster": [(0.0, "boom")],
    "trophy": [(0.25, "shine"), (0.5, "shine"), (0.75, "shine")],
    "signup": [(0.15, "scribble")],
    "round_one": [(0.5, "thud")],
    "shock": [(0.15, "thud")],
    "tally": [(0.28, "ding"), (0.48, "ding"), (0.68, "ding"), (0.88, "ding")],
    "study_wide": [(0.0, "whoosh")],
    "notebook": [(0.06, "scribble"), (0.23, "scribble"), (0.4, "scribble"), (0.57, "scribble"), (0.74, "scribble")],
    "shelves": [(0.0, "whoosh")],
    "last_dollar": [(0.0, "boom")],
    "last_note": [(0.02, "scribble"), (0.2, "scribble"), (0.5, "ding")],
}
