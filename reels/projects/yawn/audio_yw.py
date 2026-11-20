"""Yawn reel soundtrack: all synthesized. Writes soundtrack.wav and events.json (times used by the graphics)."""
import os, sys, json
import numpy as np
from scipy import signal
from scipy.io import wavfile

sys.path.insert(0, "/home/user/my-first-project-/reels/tools")
import sfx as S
S.SFX_DIR = os.path.abspath("sfx"); os.makedirs(S.SFX_DIR, exist_ok=True)

SR = 48000
rng = np.random.default_rng(5)
tl = json.load(open("timeline.json"))
st, D, DUR = tl["starts"], tl["durs"], tl["dur"]
n = int(SR * DUR)
L = np.zeros(n); M = np.zeros(n)

def T(d): return np.arange(int(SR * d)) / SR
def lp(x, f, o=4): return signal.sosfilt(signal.butter(o, f, "low", fs=SR, output="sos"), x)
def hp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, "high", fs=SR, output="sos"), x)
def bp(x, a, b, o=2): return signal.sosfilt(signal.butter(o, [a, b], "band", fs=SR, output="sos"), x)
def nrm(x): return x / (np.max(np.abs(x)) or 1)
def put(bus, x, t, g=1.0):
    i = int(t * SR)
    if i >= n: return
    if i < 0: x = x[-i:]; i = 0
    j = min(n, i + len(x)); bus[i:j] += x[: j - i] * g
def lib(name): return S.load(name)[:, 0]

# ---------------- voices & instruments
def yawn(d=1.3, f0a=220, f0b=150, breath=0.5):
    """Cartoon yawn: rising-falling glottal tone through vowel formants gliding 'aa' -> 'oh', plus breath."""
    t = T(d); k = t / d
    f0 = f0a * (1 + 0.15 * np.sin(np.pi * np.minimum(k * 1.6, 1))) * (1 - k) + f0b * k
    ph = 2 * np.pi * np.cumsum(f0) / SR
    src = sum(np.sin(h * ph) / h for h in range(1, 18))
    half = len(t) // 2
    a = bp(src, 650, 1300) + 0.5 * bp(src, 2300, 3000)
    o = bp(src, 380, 900) + 0.3 * bp(src, 2200, 2700)
    w = np.clip((k - 0.35) / 0.4, 0, 1)
    v = a * (1 - w) + o * w
    br = bp(rng.normal(size=len(t)), 500, 4000) * breath
    env = np.minimum(1, t / 0.35) * np.minimum(1, (d - t) / 0.5) ** 1.5
    return nrm((v + br * 0.6) * env)

def shehnai(notes, dur=0.32):
    out = []
    for m in notes:
        f = 440 * 2 ** ((m - 69) / 12); t = T(dur)
        vib = 1 + 0.012 * np.sin(2 * np.pi * 5.5 * t)
        ph = 2 * np.pi * np.cumsum(f * vib) / SR
        x = signal.sawtooth(ph) + 0.4 * np.sin(2 * ph)
        x = bp(x, 700, 3800) * np.minimum(1, t / 0.04) * np.minimum(1, (dur - t) / 0.06)
        out.append(x)
    return nrm(np.concatenate(out))

def trombone():                     # wah-wah-waaah
    out = []
    for f, d in [(233, 0.32), (220, 0.32), (208, 0.32), (196, 0.9)]:
        t = T(d); vib = 1 + (0.03 * np.sin(2 * np.pi * 6 * t) if d > 0.5 else 0)
        ph = 2 * np.pi * np.cumsum(f * vib) / SR
        x = signal.sawtooth(ph); wah = 0.5 + 0.5 * np.sin(2 * np.pi * (1 / d) * t - np.pi / 2)
        x = lp(x, 900) * (0.4 + 0.6 * wah) * np.minimum(1, t / 0.03) * np.minimum(1, (d - t) / 0.08)
        out.append(x)
    return nrm(np.concatenate(out))

def scratch():
    t = T(0.5); x = rng.normal(size=len(t)); out = np.zeros_like(x); seg = len(t) // 3
    for k, (a, b) in enumerate([(300, 3000), (3000, 400), (400, 2500)]):
        s_ = x[k * seg:(k + 1) * seg]; out[k * seg:(k + 1) * seg] = S.bandpass_sweep(s_, a, b, q=3, steps=24)[: len(s_)]
    return nrm(out * np.exp(-t * 2.5))

def pizz(f, d=0.25, b=1.0):
    t = T(d); x = np.sin(2 * np.pi * f * t) + 0.5 * b * np.sin(4 * np.pi * f * t) + 0.2 * np.sin(6 * np.pi * f * t)
    return x * np.exp(-t * 14)

def bassoon(f, d):
    t = T(d); x = signal.square(2 * np.pi * f * t, 0.3); return lp(x, 700) * np.minimum(1, t / 0.02) * np.exp(-t * 4)

def hz(m): return 440 * 2 ** ((m - 69) / 12)

def drumroll(d=1.0):
    x = np.zeros(int(SR * d))
    for k in range(int(d * 28)):
        i = int(k / 28 * SR); hit = bp(rng.normal(size=1800), 150, 2500) * np.exp(-np.arange(1800) / 260)
        x[i:i + 1800] += hit[: len(x) - i] * (0.4 + 0.6 * k / (d * 28))
    return nrm(x)

def cymbal(): t = T(1.6); return nrm(hp(rng.normal(size=len(t)), 5000) * np.exp(-t * 2.2))
def tada():
    out = np.zeros(int(SR * 1.2))
    for m in (60, 64, 67, 72):
        p = pizz(hz(m), 1.1, 1.2) * 0.6 + bassoon(hz(m - 12), 1.1) * 0.3
        out[:len(p)] += p
    return nrm(out)
def clack():
    t = T(0.06); c = hp(rng.normal(size=len(t)), 800) * np.exp(-t * 90)
    gap = np.zeros(int(SR * 0.09)); return nrm(np.concatenate([c, gap, c * 0.8]))
def horn(): t = T(0.9); x = (signal.square(2 * np.pi * 311 * t) + signal.square(2 * np.pi * 370 * t)); return nrm(lp(x, 1500) * np.minimum(1, t / 0.05) * np.minimum(1, (0.9 - t) / 0.1))
def crowd(d): x = lp(rng.normal(size=int(SR * d)), 1800); t = T(d); return nrm(x * np.minimum(1, t / 0.8) * np.minimum(1, (d - t) / 0.6))
def bubble():
    t = T(0.09); f = 500 + rng.random() * 900; return np.sin(2 * np.pi * (f + 2500 * t) * t) * np.exp(-t * 40)
def stamp():
    t = T(0.5); x = np.sin(2 * np.pi * (60 + 120 * np.exp(-t * 40)) * t) * np.exp(-t * 9) + lp(rng.normal(size=len(t)), 1200) * np.exp(-t * 30)
    return nrm(np.tanh(x * 2.5))
def sizzle(d): return nrm(hp(rng.normal(size=int(SR * d)), 3500) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * T(d))))
def chime():
    out = np.zeros(int(SR * 1.2))
    for i, m in enumerate((84, 88, 91, 96)):
        p = pizz(hz(m), 1.0, 0.3) * 0.5; j = int(i * 0.08 * SR); out[j:j + len(p)] += p[: len(out) - j]
    return nrm(out)
def click(): t = T(0.05); return nrm(hp(rng.normal(size=len(t)), 2000) * np.exp(-t * 120))
def boing():
    t = T(0.6); f = 180 + 120 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 4); return nrm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4))
def beep(): t = T(0.12); return np.sin(2 * np.pi * 1400 * t) * np.minimum(1, (0.12 - t) / 0.02)
def whistle(d=1.4):
    t = T(d); f = 1800 + 900 * t / d; x = np.sin(2 * np.pi * np.cumsum(f * (1 + 0.01 * np.sin(2 * np.pi * 7 * t))) / SR)
    return nrm((x + 0.4 * hp(rng.normal(size=len(t)), 3000)) * np.minimum(1, t / 0.3))
def crickets(d):
    x = np.zeros(int(SR * d))
    for k in range(int(d * 6)):
        i = int(k / 6 * SR + rng.random() * 2000); tt = T(0.12); c = np.sin(2 * np.pi * 4700 * tt) * (np.sin(2 * np.pi * 45 * tt) > 0) * np.exp(-tt * 10)
        x[i:i + len(c)] += c[: len(x) - i]
    return nrm(x)
def dingdong():
    a = pizz(hz(79), 0.5, 0.4); b = pizz(hz(76), 0.8, 0.4); return nrm(np.concatenate([a[: int(SR * 0.22)], b]))
def gulp():
    t = T(0.35); x = np.sin(2 * np.pi * (300 * np.exp(-t * 6) + 60) * t) * np.exp(-t * 7); return nrm(x)

# ---------------- timeline
F, FL = tl["freeze_at"], tl["freeze"]
Y1 = tl["yawn1"]
ev = {"yawns": [], "mouths": []}

# hook 1: shehnai setup, dulha yawn, freeze with scratch + trombone
sh = shehnai([67, 69, 71, 72, 71, 69, 71, 72], 0.21); put(M, sh, 0.05, 0.45)
put(L, yawn(1.1, 150, 95, 0.4), Y1 - 0.05, 0.9); ev["yawns"].append(Y1)
put(L, yawn(0.7, 300, 230, 0.4), Y1 + 0.25, 0.4)
put(L, scratch(), F, 0.8); put(L, lib("hit"), F + 0.02, 0.35)
put(L, trombone(), F + 0.2, 0.6)
# hook 2: sneaky tiptoe, Dadi yawn, family chorus
for k in range(14):
    tt = st[1] + 0.1 + k * 0.27
    if tt < st[2] - 0.5: put(M, pizz(hz([62, 65, 62, 69, 67, 65, 62, 60][k % 8]), 0.2, 0.6), tt, 0.35)
put(L, yawn(1.2, 260, 190, 0.6), st[1] + 1.9, 0.85); ev["yawns"].append(st[1] + 1.9)
for i, (a, b) in enumerate([(140, 95), (230, 170), (180, 130), (300, 220)]):
    put(L, yawn(0.9, a, b, 0.5), st[1] + 2.2 + i * 0.12, 0.35)
# stage: drumroll + cymbal + ta-da
put(L, drumroll(1.1), st[2] + 0.05, 0.45); put(L, cymbal(), st[2] + 1.2, 0.35); put(M, tada(), st[2] + 1.2, 0.55)
put(L, click(), st[2] + D[2] - 0.35, 0.5)
# train
for tt in np.arange(st[3], st[4] - 0.1, 0.42): put(L, clack(), tt, 0.28)
put(L, horn(), st[3] + 0.15, 0.25)
for i in range(5): put(L, yawn(0.8, 200 + 40 * (i % 3), 150, 0.5), st[3] + 0.5 + i * 0.45, 0.35)
# teacher
put(L, lib("hit"), st[4] + 0.55, 0.7); put(L, yawn(1.1, 280, 200, 0.5), st[4] + 1.1, 0.75); ev["yawns"].append(st[4] + 1.1)
put(L, boing(), st[4] + 1.9, 0.45)
# stadium
put(L, crowd(D[5]), st[5], 0.35)
for i in range(10): put(L, yawn(1.0, 120 + rng.random() * 200, 100, 0.6), st[5] + 0.6 + i * 0.12, 0.16)
# lab
for k in range(40): put(L, bubble(), st[6] + rng.random() * D[6], 0.18)
put(L, yawn(1.1, 140, 100, 0.5), st[6] + 0.15, 0.7)
STAMP = st[6] + D[6] * 0.66; put(L, stamp(), STAMP, 0.85); ev["stamp"] = STAMP
# AC brain
put(L, sizzle(1.3), st[7] + 0.05, 0.25)
ICE = st[7] + D[7] * 0.5; put(L, lib("whoosh_long"), ICE - 0.2, 0.45); put(L, chime(), ICE, 0.4); ev["ice"] = ICE
# copy button
for k in range(4): put(L, beep(), st[8] + 0.3 + k * 0.3, 0.25)
BTN = st[8] + D[8] * 0.42; put(L, click(), BTN, 0.8); put(L, lib("hit"), BTN, 0.3); put(L, boing(), BTN + 0.1, 0.4); ev["button"] = BTN
# office
COOK = st[9] + D[9] * 0.25; put(L, whistle(1.5), COOK, 0.3)
BURST = st[9] + D[9] * 0.72; put(L, lib("pop"), BURST, 0.7); put(L, yawn(1.1, 150, 100, 0.5), BURST, 0.8); ev["burst"] = BURST
put(L, lib("whoosh_long"), BURST + 0.2, 0.3)
# dinner
for k in range(6): put(L, pizz(hz(96 + (k % 2) * 3), 0.3, 0.2), st[10] + 0.15 + k * 0.17, 0.12)
for i, (a, b) in enumerate([(260, 190), (150, 100), (240, 180), (330, 260)]): put(L, yawn(0.7, a, b, 0.4), st[10] + 0.4 + i * 0.38, 0.45)
put(L, boing(), st[10] + D[10] * 0.68, 0.45)
# night
put(L, crickets(D[11]), st[11], 0.12); put(L, lib("ding"), st[11] + 1.4, 0.25)
put(L, yawn(1.2, 150, 100, 0.6), st[11] + D[11] * 0.55, 0.7); ev["yawns"].append(st[11] + D[11] * 0.55)
# zoom
put(L, dingdong(), st[12] + 0.15, 0.4)
for i in range(8): put(L, yawn(0.6, 150 + (i * 37) % 180, 110, 0.4), st[12] + 0.9 + i * 0.22, 0.22)
# mouth dives + transitions
mouth_cuts = [1, 2, 3, 4, 5, 6, 12, 13]           # clips that end inside a mouth / on black
for k in range(1, len(st)):
    put(L, lib("whoosh"), st[k] - 0.14, 0.32)
    if k in mouth_cuts: put(L, gulp(), st[k] - 0.05, 0.5); ev["mouths"].append(st[k])
# end card
E = st[13]
put(M, tada(), E + 0.2, 0.5); put(L, cymbal(), E + 0.2, 0.25)
FOLLOW = E + 1.6; put(L, click(), FOLLOW + 0.55, 0.8); put(L, lib("ding"), FOLLOW + 0.6, 0.45); put(L, lib("boom"), FOLLOW + 0.6, 0.25)
ev["follow"] = FOLLOW; ev["end"] = E

# ---------------- music bed (playful pizzicato + bassoon), from the stage to the end card
bpm = 112; beat = 60 / bpm
prog = [(60, [64, 67, 72]), (55, [62, 67, 71]), (57, [64, 69, 72]), (53, [65, 69, 72])]
t = st[2] + 1.2; b = 0
while t < E - 0.1:
    root, ch = prog[(b // 4) % 4]
    put(M, bassoon(hz(root - 12 if b % 2 == 0 else root - 5), beat * 0.9), t, 0.2)
    if b % 2 == 1: put(M, pizz(hz(ch[(b // 2) % 3] + 12), 0.25, 0.8), t, 0.16)
    put(M, pizz(hz(ch[b % 3] + 12), 0.2, 0.6), t + beat / 2, 0.1)
    t += beat; b += 1

mix = np.tanh((L * 0.95 + M * 0.85) * 1.1)
mix = mix / np.max(np.abs(mix)) * 0.89
fo = int(SR * 0.5); mix[-fo:] *= np.linspace(1, 0, fo)
wavfile.write("soundtrack.wav", SR, (np.stack([mix, mix], 1) * 32767).astype(np.int16))
json.dump(ev, open("events.json", "w"), indent=1)
print("soundtrack", round(DUR, 2), ev)
