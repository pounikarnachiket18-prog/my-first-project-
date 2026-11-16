"""Builds the credit-card reel soundtrack: an original synthesized music bed + SFX cues."""
import sys, json
import numpy as np
from scipy.io import wavfile

sys.path.insert(0, "/home/user/my-first-project-/reels/tools")
import sfx as S  # synthesized SFX library (no samples, no licensing issues)
import os
S.SFX_DIR = os.path.abspath("sfx")

SR = S.SR
CLIP0 = 4.0
CLIP = 3.6666667
N = 19
TAIL = 1.8
DUR = CLIP0 + CLIP * (N - 1) + TAIL
starts = [0.0] + [CLIP0 + CLIP * k for k in range(N - 1)]


# ------------------------------------------------------------ music bed
def note(f, dur, kind="pluck"):
    t = np.arange(int(SR * dur)) / SR
    if kind == "pluck":
        x = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.12 * np.sin(2 * np.pi * 3 * f * t))
        x *= np.exp(-t * 7)
    elif kind == "bass":
        x = np.sin(2 * np.pi * f * t) + 0.2 * np.sin(2 * np.pi * 2 * f * t)
        x *= np.minimum(1, t * 60) * np.exp(-t * 2.2)
    else:  # pad
        x = sum(np.sin(2 * np.pi * f * d * t) for d in (1, 1.003, 0.997)) / 3
        x *= np.minimum(1, t * 3) * np.minimum(1, (dur - t) * 3)
    return x


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


bpm = 100
beat = 60 / bpm
n = int(SR * DUR)
mus = np.zeros(n)
# C - G - Am - F, one bar each
prog = [(60, [60, 64, 67, 72]), (55, [59, 62, 67, 71]), (57, [57, 60, 64, 69]), (53, [57, 60, 65, 69])]
bar = 4 * beat
t = 0.0
b = 0
while t < DUR:
    root, ch = prog[b % 4]
    i = int(t * SR)

    def add(x, at, g):
        j = int(at * SR)
        if j >= n:
            return
        k = min(n, j + len(x))
        mus[j:k] += x[: k - j] * g

    add(note(hz(root - 12), bar, "bass"), t, 0.35)
    add(note(hz(root - 12), beat * 1.5, "bass"), t + 2.5 * beat, 0.25)
    add(note(hz(ch[0]), bar, "pad") , t, 0.06)
    add(note(hz(ch[2]), bar, "pad"), t, 0.05)
    arp = [0, 1, 2, 3, 2, 1, 2, 3]
    for s in range(8):
        add(note(hz(ch[arp[s]] + 12), beat * 0.9), t + s * beat / 2, 0.16 if s % 2 == 0 else 0.11)
    for q in range(4):  # soft kick + shaker
        kt = np.arange(int(SR * 0.25)) / SR
        kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 14)
        add(kick, t + q * beat, 0.45 if q % 2 == 0 else 0.3)
        sh = S.highpass(np.random.default_rng(q + b).normal(size=int(SR * 0.05)), 6000) * np.exp(-np.arange(int(SR * 0.05)) / SR * 80)
        add(sh, t + q * beat + beat / 2, 0.12)
    t += bar
    b += 1

mus = S.reverb(mus, decay=1.0, mix=0.18)[:n]
mus = mus / np.max(np.abs(mus)) * 0.9
fi = int(SR * 0.3); mus[:fi] *= np.linspace(0, 1, fi)
fo = int(SR * 1.5); mus[-fo:] *= np.linspace(1, 0, fo)
music = np.stack([mus, mus], 1) * 0.22  # bed level

# ------------------------------------------------------------ SFX cues (clip-relative times)
C = {
    1: [(0.0, "riser_short", .5), (0.1, "boom", .55), (0.3, "hit", .4), (3.4, "pop", .5)],
    2: [(1.0, "pop_high", .5), (1.6, "tick", .5), (1.9, "tick", .5)],
    3: [(0.2, "hit", .6), (1.6, "glitch", .25)],
    4: [(1.0, "ding", .5), (1.6, "pop_high", .4), (1.8, "pop_high", .4), (2.0, "pop_high", .4), (3.0, "swish", .5)],
    5: [(1.1, "swish", .5), (1.35, "swish", .45), (1.6, "swish", .45), (2.6, "pop", .55)],
    6: [(0.4, "counter", .5), (0.7, "counter", .5), (1.0, "counter", .5), (1.3, "counter", .5), (3.0, "boom", .6)],
    7: [(0.8, "pop", .45), (1.15, "pop", .45), (1.5, "pop_high", .45), (1.85, "pop_high", .45), (2.9, "boom", .45)],
    8: [(0.2, "hit", .45), (1.8, "swish", .5), (2.2, "pop_low", .6)],
    9: [(0.6, "whoosh_long", .5), (1.8, "pop_high", .45), (2.2, "pop_high", .4)],
    10: [(1.0, "pop", .55), (1.4, "ding", .35), (2.4, "swish", .45)],
    11: [(0.4, "buzz", .25), (1.6, "pop_low", .5)] + [(1.9 + 0.22 * k, "tick", .45) for k in range(6)],
    12: [(0.9, "ding", .35), (1.2, "ding", .3), (1.5, "ding", .3), (2.0, "tick", .4), (2.6, "riser_short", .4)],
    13: [(0.3, "buzz", .3), (0.7, "buzz", .3), (1.3, "pop", .55), (2.6, "riser_short", .4)],
    14: [(0.6, "pop_low", .5), (1.2, "riser", .45), (3.1, "boom", .55)],
    15: [(0.8, "swish", .4), (1.6, "counter", .45), (1.9, "counter", .45), (2.9, "glitch", .3)],
    16: [(0.5, "heartbeat", .5), (2.8, "pop_low", .4)],
    17: [(0.6, "riser_short", .45), (1.6, "ding", .5), (2.2, "pop_high", .4), (2.5, "pop_high", .4)],
    18: [(1.1, "pop_high", .55), (1.7, "pop_high", .55), (2.3, "pop_high", .55), (2.5, "ding", .35)],
    19: [(1.4, "hit", .45), (1.8, "boom", .4), (3.6, "whoosh", .45), (3.9, "ding", .45)],
}
cues = []
for k in range(1, N + 1):
    if k > 1:
        cues.append({"t": max(0, starts[k - 1] - 0.12), "sfx": "whoosh", "gain": 0.35})
    for (dt, name, g) in C[k]:
        cues.append({"t": starts[k - 1] + dt, "sfx": name, "gain": g})

bus = np.zeros((n, 2))
cache = {}
for c in cues:
    if c["sfx"] not in cache:
        cache[c["sfx"]] = S.load(c["sfx"])
    s = cache[c["sfx"]] * c["gain"]
    i = int(SR * c["t"])
    j = min(n, i + len(s))
    if i < n:
        bus[i:j] += s[: j - i]

mix = np.tanh((bus * 0.8 + music) * 1.05)
mix = mix / np.max(np.abs(mix)) * 0.89
fo = int(SR * 0.6); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
wavfile.write("soundtrack.wav", SR, (mix * 32767).astype(np.int16))
json.dump({"dur": DUR, "starts": starts}, open("timeline.json", "w"))
print("soundtrack", round(DUR, 2), "s,", len(cues), "cues")
