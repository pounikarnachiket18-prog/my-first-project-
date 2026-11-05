"""Shared timing for the reel.

All cut / cue times in build.py and audio.py are written on the 75 s
voiceover grid (vo_tight.wav). PAUSES opens short gaps in the voiceover for
the spoken meme sounds; sh() moves any time on the old grid to the final reel.
"""
PAUSES = [  # (time on the 75 s grid, seconds of silence inserted)
    (9.93, 0.70),   # "...Zomato kitna kamata hai?"  -> "huh?"
    (31.72, 0.65),  # "...platform fees"               -> screaming cat
    (52.83, 0.85),  # "...operations me bhi kharcha"  -> sobbing
    (60.58, 1.10),  # "11,445 crore rupaye"            -> scream
]
VO_END = 75.0     # voiceover length on the old grid
TAIL = 2.0        # brand card hold after the last word (echo meme)


def sh(t):
    """Old-grid time -> final reel time."""
    return t + sum(p for a, p in PAUSES if t >= a - 1e-6)


def pause_at(i):
    """Final reel time where pause i starts."""
    a, _ = PAUSES[i]
    return a + sum(p for b, p in PAUSES[:i])


END = round(sh(VO_END) + TAIL, 3)
