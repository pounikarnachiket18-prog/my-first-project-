"""Royal Enfield reel soundtrack: synthesized Bullet thump, patakas, scratch, kick-start,
rain, gate clang, gramophone tune and a music bed. Everything is generated (no samples)."""
import os, sys, json
import numpy as np
from scipy import signal
from scipy.io import wavfile

sys.path.insert(0, "/home/user/my-first-project-/reels/tools")
import sfx as S
S.SFX_DIR = os.path.abspath("sfx"); os.makedirs(S.SFX_DIR, exist_ok=True)

SR = 48000
rng = np.random.default_rng(11)
H1 = 5.4333333
CL = 3.4666667
N = 15
starts = [0.0] + [H1 + CL * k for k in range(N - 1)]
END = starts[-1] + CL
DUR = END + 1.8
n = int(SR * DUR)
L = np.zeros(n)          # sfx bus (mono, panned later)
M = np.zeros(n)          # music bus


def T(d): return np.arange(int(SR * d)) / SR
def lp(x, f, o=4): return signal.sosfilt(signal.butter(o, f, "low", fs=SR, output="sos"), x)
def hp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, "high", fs=SR, output="sos"), x)
def bp(x, a, b, o=2): return signal.sosfilt(signal.butter(o, [a, b], "band", fs=SR, output="sos"), x)


def put(bus, x, t, g=1.0):
    i = int(t * SR)
    if i >= n or i + len(x) <= 0: return
    j = min(n, i + len(x)); bus[i:j] += x[: j - i] * g


# ---------------------------------------------------------------- sounds
def dug(f=48, d=0.22):
    t = T(d)
    body = np.sin(2 * np.pi * (f + 40 * np.exp(-t * 35)) * t) * np.exp(-t * 16)
    bark = lp(rng.normal(size=len(t)), 900) * np.exp(-t * 28) * 0.6
    x = np.tanh((body + bark) * 2.2)
    return x / np.max(np.abs(x))


def pataka():
    t = T(0.35)
    crack = hp(rng.normal(size=len(t)), 1500) * np.exp(-t * 60)
    boom = np.sin(2 * np.pi * (90 + 200 * np.exp(-t * 50)) * t) * np.exp(-t * 18)
    x = np.tanh((crack * 1.4 + boom) * 2)
    return x / np.max(np.abs(x))


def rev(d=1.6, f0=30, f1=75):
    t = T(d); f = np.linspace(f0, f1, len(t)) ** 1.0
    ph = 2 * np.pi * np.cumsum(f) / SR
    pulse = (np.sin(ph) > 0.6).astype(float)
    x = lp(pulse + 0.3 * rng.normal(size=len(t)), 700) * np.minimum(1, t * 4) * np.minimum(1, (d - t) * 3)
    return x / np.max(np.abs(x))


def scratch():
    t = T(0.55); x = rng.normal(size=len(t))
    out = np.zeros_like(x); seg = len(t) // 3
    for k, (a, b) in enumerate([(300, 3000), (3000, 400), (400, 2500)]):
        s = x[k * seg:(k + 1) * seg]
        out[k * seg:(k + 1) * seg] = S.bandpass_sweep(s, a, b, q=3, steps=24)[: len(s)]
    out *= np.exp(-t * 2.5)
    return out / np.max(np.abs(out))


def kickstart():
    t = T(0.12); clk = hp(rng.normal(size=len(t)), 2500) * np.exp(-t * 80)
    x = np.concatenate([clk, np.zeros(int(SR * 0.15)), clk * 0.7, np.zeros(int(SR * 0.08))])
    return np.concatenate([x / np.max(np.abs(x)), rev(1.3, 25, 95) * 0.9])


def rain(d):
    x = lp(rng.normal(size=int(SR * d)), 5000) * 0.25
    drops = np.zeros_like(x)
    for _ in range(int(d * 40)):
        i = rng.integers(0, len(x) - 2000)
        drops[i:i + 2000] += hp(rng.normal(size=2000), 3000) * np.exp(-np.arange(2000) / 150) * 0.5
    y = x + drops
    return y / np.max(np.abs(y))


def clang():
    t = T(1.8); x = np.zeros_like(t)
    for f, a, dcy in [(180, 1, 2.5), (437, .6, 3.5), (811, .45, 4.5), (1290, .3, 6), (2150, .2, 8)]:
        x += a * np.sin(2 * np.pi * f * t) * np.exp(-t * dcy)
    x += hp(rng.normal(size=len(t)), 1500) * np.exp(-t * 40) * 0.8
    return x / np.max(np.abs(x))


def plink():
    t = T(0.6)
    x = np.sin(2 * np.pi * (1800 - 600 * np.exp(-t * 20)) * t) * np.exp(-t * 9)
    return x / np.max(np.abs(x))


def hz(m): return 440 * 2 ** ((m - 69) / 12)


def pluck(f, d, bright=1.0):
    t = T(d)
    x = np.sin(2 * np.pi * f * t) + 0.4 * bright * np.sin(4 * np.pi * f * t) + 0.15 * bright * np.sin(6 * np.pi * f * t)
    return x * np.exp(-t * 6)


def pad(f, d):
    t = T(d)
    x = sum(np.sin(2 * np.pi * f * k * t) for k in (1, 1.004, 0.996)) / 3
    return x * np.minimum(1, t * 2) * np.minimum(1, (d - t) * 2)


# ---------------------------------------------------------------- Hook 1 (0 - 5.43)
for k, tt in enumerate(np.arange(0.0, 2.35, 0.14)):
    put(L, dug(52, 0.15), tt, 0.55)
put(L, rev(2.3, 40, 85), 0.0, 0.35)
for tt in (0.25, 0.62, 0.95, 1.3, 1.62, 2.05, 2.25):
    put(L, pataka(), tt, 0.75)
put(L, scratch(), 2.4, 0.8)                     # freeze frame 2.4 - 3.8
put(L, S.load("boom")[:, 0], 2.45, 0.45)
for tt in np.arange(3.85, H1 - 0.1, 0.32):        # idle thump after freeze
    put(L, dug(46, 0.2), tt, 0.4)

# ---------------------------------------------------------------- Hook 2 + 3: gramophone, rain, clang, tear
mel = [72, 74, 76, 79, 77, 76, 74, 72, 74, 76, 74, 72, 71, 72]
gram = np.zeros(int(SR * 7.2))
tt = 0.0
for k, m in enumerate(mel):
    d = 0.5
    slow = 1.0 if tt < 3.6 else 1 + (tt - 3.6) * 0.18      # tune slows & detunes in Hook 3
    x = pluck(hz(m) / slow ** 0.3, d * slow)
    if int(tt * SR) >= len(gram) - 10: break
    i = int(tt * SR); j = min(len(gram), i + len(x)); gram[i:j] += x[: j - i]
    for c in (m - 12, m - 8):
        x2 = pad(hz(c), d * slow) * 0.25
        j2 = min(len(gram), i + len(x2)); gram[i:j2] += x2[: j2 - i]
    tt += d * slow
gram = bp(gram, 300, 3200)
crackle = np.zeros_like(gram)
for _ in range(900):
    i = rng.integers(0, len(gram) - 200)
    crackle[i:i + 200] += hp(rng.normal(size=200), 2000) * np.exp(-np.arange(200) / 30)
g = gram / np.max(np.abs(gram)) + crackle * 0.06
fade = np.linspace(1, 0, len(g)) ** 0.6
put(M, g * fade, starts[1], 0.55)
r = rain(4.0); r *= np.linspace(0.2, 1, len(r))
put(L, r, starts[2] - 0.3, 0.22)
put(L, clang(), starts[2] + 1.5, 0.6)
put(L, plink(), starts[2] + 2.55, 0.45)

# ---------------------------------------------------------------- heartbeat thump through the story
def beat_pairs(t0, t1, bpm, g=0.6):
    p = 60 / bpm; t = t0
    while t < t1:
        put(L, dug(48), t, g); put(L, dug(44), t + 0.18, g * 0.75); t += p

put(L, dug(50, 0.35), starts[3] + 0.05, 0.9)               # single DUG on the medallion
beat_pairs(starts[3] + 0.8, starts[8], 72, 0.5)            # heyday
beat_pairs(starts[8], starts[9], 52, 0.45)                 # rivals: heartbeat slows
put(L, S.load("glitch")[:, 0], starts[8] + 1.4, 0.25)      # sputter
beat_pairs(starts[9], starts[9] + 1.9, 38, 0.35)           # decline: last beats, then silence
put(L, kickstart(), starts[10] + 0.6, 0.85)                # comeback
beat_pairs(starts[10] + 2.2, END, 96, 0.42)

# ---------------------------------------------------------------- music bed
def section(t0, t1, prog, bpm, gain, bright=1.0):
    beat = 60 / bpm; bar = 4 * beat; t = t0; b = 0
    while t < t1:
        root, ch = prog[b % len(prog)]
        d = min(bar, t1 - t)
        put(M, pad(hz(root - 12), d), t, 0.18 * gain)
        put(M, pad(hz(ch[1]), d), t, 0.06 * gain)
        for s in range(8):
            ts = t + s * beat / 2
            if ts < t1:
                put(M, pluck(hz(ch[[0, 1, 2, 3, 2, 1, 2, 3][s]] + 12), beat * 0.9, bright), ts, (0.12 if s % 2 else 0.17) * gain)
        t += bar; b += 1

major = [(62, [62, 66, 69, 74]), (57, [61, 64, 69, 73]), (59, [59, 62, 66, 71]), (55, [59, 62, 67, 71])]
minor = [(57, [57, 60, 64, 69]), (53, [57, 60, 65, 69])]
up = [(62, [62, 66, 69, 74]), (59, [59, 62, 66, 71]), (55, [59, 62, 67, 71]), (57, [61, 64, 69, 73])]
section(starts[3], starts[8], major, 90, 0.8, 0.8)
section(starts[8], starts[9] + 1.9, minor, 70, 0.55, 0.5)
section(starts[10] + 1.2, DUR - 0.2, up, 104, 1.0, 1.2)

# ---------------------------------------------------------------- transitions & accents
for k in range(1, N):
    if k in (1, 2, 10):  # Hook2/Hook3 are slow memory cuts; clip 10 enters on silence
        continue
    put(L, S.load("whoosh")[:, 0], starts[k] - 0.12, 0.3)
put(L, S.load("ding")[:, 0], starts[13] + 1.9, 0.35)       # pie chart
for k in (12, 14):                                           # smoke rings
    for dt in (2.2, 2.6, 3.0):
        put(L, S.load("swish")[:, 0], starts[k] + dt, 0.3)
put(L, S.load("hit")[:, 0], starts[11] + 1.6, 0.4)          # scissors cut
put(L, S.load("boom")[:, 0], END + 0.1, 0.4)                 # banner
put(L, S.load("ding")[:, 0], END + 0.2, 0.4)

mix = L * 0.9 + M * 0.9
mix = np.tanh(mix * 1.1)
mix = mix / np.max(np.abs(mix)) * 0.89
fo = int(SR * 0.6); mix[-fo:] *= np.linspace(1, 0, fo)
st = np.stack([mix, mix], 1)
wavfile.write("soundtrack.wav", SR, (st * 32767).astype(np.int16))
json.dump({"dur": DUR, "starts": starts, "end": END}, open("timeline.json", "w"))
print("soundtrack", round(DUR, 2))
