"""Royal Enfield soundtrack v2 (motion-graphics cut). Reads timeline2.json, writes soundtrack2.wav
and beats.json (thump times, used by the on-screen heartbeat line). Everything is synthesized."""
import os, sys, json
import numpy as np
from scipy import signal
from scipy.io import wavfile

sys.path.insert(0, "/home/user/my-first-project-/reels/tools")
import sfx as S
S.SFX_DIR = os.path.abspath("sfx"); os.makedirs(S.SFX_DIR, exist_ok=True)

SR = 48000
rng = np.random.default_rng(11)
tl = json.load(open("timeline2.json"))
starts, DUR = tl["starts"], tl["dur"]
FZ, FL = tl["freeze_at"], tl["freeze"]
N = len(starts)
END = DUR - 2.4
n = int(SR * DUR)
L = np.zeros(n); M = np.zeros(n)
beats = []


def T(d): return np.arange(int(SR * d)) / SR
def lp(x, f, o=4): return signal.sosfilt(signal.butter(o, f, "low", fs=SR, output="sos"), x)
def hp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, "high", fs=SR, output="sos"), x)
def bp(x, a, b, o=2): return signal.sosfilt(signal.butter(o, [a, b], "band", fs=SR, output="sos"), x)
def nrm(x): return x / (np.max(np.abs(x)) or 1)


def put(bus, x, t, g=1.0):
    i = int(t * SR)
    if i >= n or i + len(x) <= 0: return
    if i < 0: x = x[-i:]; i = 0
    j = min(n, i + len(x)); bus[i:j] += x[: j - i] * g


def dug(f=48, d=0.22):
    t = T(d)
    body = np.sin(2 * np.pi * (f + 40 * np.exp(-t * 35)) * t) * np.exp(-t * 16)
    bark = lp(rng.normal(size=len(t)), 900) * np.exp(-t * 28) * 0.6
    return nrm(np.tanh((body + bark) * 2.2))


def pataka():
    t = T(0.35)
    crack = hp(rng.normal(size=len(t)), 1500) * np.exp(-t * 60)
    boom = np.sin(2 * np.pi * (90 + 200 * np.exp(-t * 50)) * t) * np.exp(-t * 18)
    return nrm(np.tanh((crack * 1.4 + boom) * 2))


def rev(d=1.6, f0=30, f1=75):
    t = T(d); f = np.linspace(f0, f1, len(t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = lp((np.sin(ph) > 0.6).astype(float) + 0.3 * rng.normal(size=len(t)), 700)
    return nrm(x * np.minimum(1, t * 4) * np.minimum(1, (d - t) * 3))


def scratch():
    t = T(0.55); x = rng.normal(size=len(t)); out = np.zeros_like(x); seg = len(t) // 3
    for k, (a, b) in enumerate([(300, 3000), (3000, 400), (400, 2500)]):
        s = x[k * seg:(k + 1) * seg]
        out[k * seg:(k + 1) * seg] = S.bandpass_sweep(s, a, b, q=3, steps=24)[: len(s)]
    return nrm(out * np.exp(-t * 2.5))


def kickstart():
    t = T(0.12); clk = hp(rng.normal(size=len(t)), 2500) * np.exp(-t * 80)
    x = np.concatenate([clk, np.zeros(int(SR * 0.15)), clk * 0.7, np.zeros(int(SR * 0.08))])
    return np.concatenate([nrm(x), rev(1.3, 25, 95) * 0.9])


def rain(d):
    x = lp(rng.normal(size=int(SR * d)), 5000) * 0.25; drops = np.zeros_like(x)
    for _ in range(int(d * 40)):
        i = rng.integers(0, len(x) - 2000)
        drops[i:i + 2000] += hp(rng.normal(size=2000), 3000) * np.exp(-np.arange(2000) / 150) * 0.5
    return nrm(x + drops)


def clang():
    t = T(1.8); x = np.zeros_like(t)
    for f, a, dcy in [(180, 1, 2.5), (437, .6, 3.5), (811, .45, 4.5), (1290, .3, 6), (2150, .2, 8)]:
        x += a * np.sin(2 * np.pi * f * t) * np.exp(-t * dcy)
    return nrm(x + hp(rng.normal(size=len(t)), 1500) * np.exp(-t * 40) * 0.8)


def plink():
    t = T(0.6); return nrm(np.sin(2 * np.pi * (1800 - 600 * np.exp(-t * 20)) * t) * np.exp(-t * 9))


def stamp():
    t = T(0.5)
    x = np.sin(2 * np.pi * (60 + 120 * np.exp(-t * 40)) * t) * np.exp(-t * 9) + lp(rng.normal(size=len(t)), 1200) * np.exp(-t * 30)
    return nrm(np.tanh(x * 2.5))


def scribble(d=0.6):
    x = bp(rng.normal(size=int(SR * d)), 2500, 7000)
    t = T(d); env = (0.5 + 0.5 * np.sin(2 * np.pi * 9 * t)) * np.minimum(1, t * 20) * np.minimum(1, (d - t) * 10)
    return nrm(x * env)


def key():
    t = T(0.05); return nrm(hp(rng.normal(size=len(t)), 2000) * np.exp(-t * 120))


def tap():
    t = T(0.12); return nrm(np.sin(2 * np.pi * 900 * t) * np.exp(-t * 60) + hp(rng.normal(size=len(t)), 3000) * np.exp(-t * 90) * 0.5)


def hz(m): return 440 * 2 ** ((m - 69) / 12)
def pluck(f, d, b=1.0):
    t = T(d); x = np.sin(2 * np.pi * f * t) + 0.4 * b * np.sin(4 * np.pi * f * t) + 0.15 * b * np.sin(6 * np.pi * f * t)
    return x * np.exp(-t * 6)
def pad(f, d):
    t = T(d); x = sum(np.sin(2 * np.pi * f * k * t) for k in (1, 1.004, 0.996)) / 3
    return x * np.minimum(1, t * 2) * np.minimum(1, (d - t) * 2)


# ---------------- Hook 1: patakas, freeze (record scratch + stamp + scribble), idle thump
for tt in np.arange(0.0, FZ - 0.05, 0.14):
    put(L, dug(52, 0.15), tt, 0.55)
put(L, rev(FZ, 40, 85), 0.0, 0.35)
PAT = [0.25, 0.62, 0.95, 1.3, 1.62, 2.05, 2.25]
for tt in PAT: put(L, pataka(), tt, 0.75)
put(L, scratch(), FZ, 0.8)
put(L, stamp(), FZ + 0.12, 0.8)
put(L, scribble(0.7), FZ + 0.55, 0.35)
put(L, S.load("pop")[:, 0], FZ + 1.25, 0.4)
for tt in np.arange(FZ + FL + 0.05, starts[1] - 0.1, 0.32):
    put(L, dug(46, 0.2), tt, 0.4)

# ---------------- Hook 2 + 3: gramophone (slows), rain, clang, teardrop
mel = [72, 74, 76, 79, 77, 76, 74, 72, 74, 76, 74, 72, 71, 72]
glen = starts[3] - starts[1]
gram = np.zeros(int(SR * glen)); tt = 0.0
split = starts[2] - starts[1]
for m in mel:
    slow = 1.0 if tt < split else 1 + (tt - split) * 0.18
    x = pluck(hz(m) / slow ** 0.3, 0.42 * slow)
    i = int(tt * SR)
    if i >= len(gram) - 10: break
    j = min(len(gram), i + len(x)); gram[i:j] += x[: j - i]
    for c in (m - 12, m - 8):
        x2 = pad(hz(c), 0.42 * slow) * 0.25; j2 = min(len(gram), i + len(x2)); gram[i:j2] += x2[: j2 - i]
    tt += 0.42 * slow
gram = bp(gram, 300, 3200); crackle = np.zeros_like(gram)
for _ in range(900):
    i = rng.integers(0, len(gram) - 200); crackle[i:i + 200] += hp(rng.normal(size=200), 2000) * np.exp(-np.arange(200) / 30)
put(M, (nrm(gram) + crackle * 0.06) * np.linspace(1, 0, len(gram)) ** 0.6, starts[1], 0.5)
r = rain(starts[3] - starts[2] + 0.3); r *= np.linspace(0.2, 1, len(r)); put(L, r, starts[2] - 0.3, 0.22)
d3 = starts[3] - starts[2]
put(L, clang(), starts[2] + d3 * 0.42, 0.6)
put(L, plink(), starts[2] + d3 * 0.72, 0.45)

# ---------------- heartbeat
def beat_pairs(t0, t1, bpm, g=0.6):
    p = 60 / bpm; t = t0
    while t < t1:
        put(L, dug(48), t, g); put(L, dug(44), t + 0.18, g * 0.75); beats.append(round(t, 3)); t += p

put(L, dug(50, 0.35), starts[3] + 0.05, 0.9); beats.append(round(starts[3] + 0.05, 3))
beat_pairs(starts[3] + 0.8, starts[8], 72, 0.45)
beat_pairs(starts[8], starts[9], 52, 0.4)
put(L, S.load("glitch")[:, 0], starts[8] + 1.2, 0.25)
flat_at = starts[9] + 1.6
beat_pairs(starts[9], flat_at, 38, 0.32)
KICK = starts[10] + 0.5
put(L, kickstart(), KICK, 0.85)
beat_pairs(KICK + 1.5, END, 96, 0.38)

# ---------------- music bed
def section(t0, t1, prog, bpm, gain, bright=1.0):
    beat = 60 / bpm; bar = 4 * beat; t = t0; b = 0
    while t < t1:
        root, ch = prog[b % len(prog)]; d = min(bar, t1 - t)
        put(M, pad(hz(root - 12), d), t, 0.18 * gain); put(M, pad(hz(ch[1]), d), t, 0.06 * gain)
        for s in range(8):
            ts = t + s * beat / 2
            if ts < t1: put(M, pluck(hz(ch[[0, 1, 2, 3, 2, 1, 2, 3][s]] + 12), beat * 0.9, bright), ts, (0.12 if s % 2 else 0.17) * gain)
        t += bar; b += 1

major = [(62, [62, 66, 69, 74]), (57, [61, 64, 69, 73]), (59, [59, 62, 66, 71]), (55, [59, 62, 67, 71])]
minor = [(57, [57, 60, 64, 69]), (53, [57, 60, 65, 69])]
up = [(62, [62, 66, 69, 74]), (59, [59, 62, 66, 71]), (55, [59, 62, 67, 71]), (57, [61, 64, 69, 73])]
section(starts[3], starts[8], major, 90, 0.8, 0.8)
section(starts[8], flat_at, minor, 70, 0.55, 0.5)
section(KICK + 0.9, DUR - 0.2, up, 104, 1.0, 1.2)

# ---------------- transitions + motion-graphics accents
for k in range(1, N):
    if k in (1, 2, 10): continue
    put(L, S.load("whoosh")[:, 0], starts[k] - 0.12, 0.32)
TAGS = [1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 13]          # clips that get a location/date tag
for k in TAGS:
    for q in range(9): put(L, key(), starts[k] + 0.35 + q * 0.045, 0.18)
for q in range(22): put(L, S.load("counter")[:, 0], starts[13] + 0.6 + q * 0.07, 0.22)   # counter roll
put(L, S.load("ding")[:, 0], starts[13] + 2.2, 0.35)
for k in (12, 14):
    for dt in (2.2, 2.6, 3.0): put(L, S.load("swish")[:, 0], starts[k] + dt, 0.25)
put(L, S.load("hit")[:, 0], starts[11] + 1.5, 0.4)
put(L, S.load("pop_high")[:, 0], KICK + 0.35, 0.45)     # VROOOM sticker
FOLLOW = END + 0.6
put(L, tap(), FOLLOW + 0.55, 0.7); put(L, S.load("ding")[:, 0], FOLLOW + 0.62, 0.45)
put(L, S.load("boom")[:, 0], FOLLOW + 0.6, 0.3)

mix = np.tanh((L * 0.9 + M * 0.9) * 1.1)
mix = mix / np.max(np.abs(mix)) * 0.89
fo = int(SR * 0.6); mix[-fo:] *= np.linspace(1, 0, fo)
wavfile.write("soundtrack2.wav", SR, (np.stack([mix, mix], 1) * 32767).astype(np.int16))
json.dump({"beats": beats, "flat_at": flat_at, "kick": KICK, "patakas": PAT, "follow": FOLLOW, "end_vo": END},
          open("beats.json", "w"))
print("soundtrack2", round(DUR, 2), "beats", len(beats))
