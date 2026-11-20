"""Yawn reel soundtrack: all synthesized. Writes soundtrack.wav and events.json (times used by the graphics)."""
import os, sys, json
import numpy as np
from scipy import signal
from scipy.io import wavfile

sys.path.insert(0, "/home/user/my-first-project-/reels/tools")
import sfx as S
import yawnvox as V
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


# ---------------- extra sounds
def braam(d=2.2):
    t = T(d); x = np.zeros_like(t)
    for f in (41.2, 55, 82.4, 110):
        x += signal.sawtooth(2 * np.pi * f * t * (1 + 0.004 * np.sin(2 * np.pi * 3 * t)))
    x = lp(x, 900) * np.minimum(1, t / 0.04) * np.exp(-t * 1.3)
    sub = np.sin(2 * np.pi * 36 * t) * np.exp(-t * 1.8)
    return nrm(np.tanh(x * 1.5 + sub * 1.2))
def door_bang(): t = T(0.6); return nrm(np.sin(2 * np.pi * (70 + 90 * np.exp(-t * 30)) * t) * np.exp(-t * 8) + lp(rng.normal(size=len(t)), 2500) * np.exp(-t * 25))
def meow():
    t = T(0.7); f0 = 650 + 350 * np.sin(np.pi * t / 0.7); ph = 2 * np.pi * np.cumsum(f0) / SR
    s_ = sum(np.sin(h * ph) / h for h in range(1, 8)); v = bp(s_, 700, 2600) * np.sin(np.pi * t / 0.7) ** 1.5; return nrm(v)
def woof():
    out = []
    for _ in range(2):
        t = T(0.18); f0 = 260 * np.exp(-t * 3); ph = 2 * np.pi * np.cumsum(f0) / SR
        s_ = sum(np.sin(h * ph) / h for h in range(1, 10)) + 0.5 * rng.normal(size=len(t))
        out.append(bp(s_, 300, 2200) * np.exp(-t * 14)); out.append(np.zeros(int(SR * 0.08)))
    return nrm(np.concatenate(out))
def knock():
    t = T(0.08); k = lp(rng.normal(size=len(t)), 1800) * np.exp(-t * 70) + np.sin(2 * np.pi * 180 * t) * np.exp(-t * 50)
    return nrm(np.concatenate([k, np.zeros(int(SR * 0.12)), k]))
def crack():
    t = T(0.5); x = hp(rng.normal(size=len(t)), 2500) * np.exp(-t * 9)
    for i in range(12):
        j = int(rng.random() * len(t) * 0.6); x[j:j + 300] += hp(rng.normal(size=300), 4000)[: len(x) - j] * 1.5
    return nrm(x)
def shimmer(d=1.6):
    out = np.zeros(int(SR * d))
    for i in range(24):
        m = [84, 86, 88, 91, 93, 96][i % 6]; p = pizz(hz(m), 0.6, 0.3); j = int(i * d / 24 * SR * 0.8); out[j:j + len(p)] += p[: len(out) - j]
    return nrm(out)

# ---------------- timeline
B, SS = tl["beats"], tl["S"]
F, FL, Y1 = B["freeze_at"], B["freeze"], B["yawn1"]
def DD(name): return D[tl["names"].index(name)]
ev = {"mouths": []}
# hook
put(M, shehnai([67, 69, 71, 72, 71, 69, 71, 72], 0.21), 0.05, 0.45)
put(L, scratch(), F, 0.8); put(L, lib("hit"), F + 0.02, 0.35); put(L, trombone(), F + 0.2, 0.6)
# door: tiptoe + Dadi + chorus
for k in range(14):
    tt = SS["door"] + 0.1 + k * 0.27
    if tt < SS["stage"] - 0.5: put(M, pizz(hz([62, 65, 62, 69, 67, 65, 62, 60][k % 8]), 0.2, 0.6), tt, 0.35)
# stage: drumroll -> BRAAAM title + ta-da
put(L, drumroll(1.1), SS["stage"] + 0.05, 0.45); put(L, braam(), B["title"] - 0.05, 0.75); put(L, cymbal(), B["title"], 0.3); put(M, tada(), B["title"], 0.4)
put(L, click(), SS["train"] - 0.35, 0.5)
# train
for tt in np.arange(SS["train"], SS["teacher"] - 0.1, 0.42): put(L, clack(), tt, 0.28)
put(L, horn(), SS["train"] + 0.15, 0.25)
# teacher
put(L, lib("hit"), B["ruler"], 0.7); put(L, boing(), B["teacher_yawn"] + 0.8, 0.45)
# hero: slow whoosh + BRAAAM, yawn, goons
put(L, lib("whoosh_long"), SS["hero"] + 0.05, 0.4); put(L, braam(1.6), B["glasses"] - 0.1, 0.6)
# stadium
put(L, crowd(DD("stadium")), SS["stadium"], 0.35)
# umpire
put(L, crowd(DD("umpire")) * np.linspace(1.3, 0.4, int(SR * DD("umpire"))), SS["umpire"], 0.3)
put(L, lib("riser_short"), B["finger"] - 0.6, 0.35)
put(L, trombone()[: int(SR * 0.7)], B["umpire_yawn"] + 0.3, 0.35)
# lab
for k in range(40): put(L, bubble(), SS["lab"] + rng.random() * DD("lab"), 0.18)
put(L, stamp(), B["stamp"], 0.85)
# AC
put(L, sizzle(1.3), SS["ac"] + 0.05, 0.25); put(L, lib("whoosh_long"), B["ice"] - 0.2, 0.45); put(L, chime(), B["ice"], 0.4)
# copy
for k in range(4): put(L, beep(), SS["copy"] + 0.3 + k * 0.3, 0.25)
put(L, click(), B["button"], 0.8); put(L, lib("hit"), B["button"], 0.3); put(L, boing(), B["button"] + 0.1, 0.4)
# office
put(L, whistle(1.5), B["cook"], 0.3); put(L, lib("pop"), B["burst"], 0.7); put(L, lib("whoosh_long"), B["burst"] + 0.2, 0.3)
# dinner
for k in range(6): put(L, pizz(hz(96 + (k % 2) * 3), 0.3, 0.2), SS["dinner"] + 0.15 + k * 0.17, 0.12)
put(L, boing(), B["stranger"], 0.45)
# night
put(L, crickets(DD("night")), SS["night"], 0.12); put(L, lib("ding"), SS["night"] + 1.2, 0.25)
# mummy
put(L, door_bang(), SS["mummy"] + 0.05, 0.7); put(L, lib("hit"), B["oye"], 0.4)
put(L, meow(), B["mummy_yawn"] + 0.9, 0.45)
put(L, click(), B["switch"], 0.7)
# zoom
put(L, dingdong(), SS["zoom"] + 0.15, 0.4)
# dog & chimps
put(L, woof(), B["dog_yawn"] - 0.25, 0.45)
# squish: whoosh in, glass thud + crack, knock knock
put(L, lib("whoosh_long"), B["impact"] - 0.8, 0.5); put(L, stamp(), B["impact"], 0.6); put(L, crack(), B["impact"], 0.55); put(L, knock(), B["impact"] + 0.7, 0.6)
# callback: shehnai reprise + duo yawn
put(M, shehnai([72, 71, 69, 71, 72], 0.24), SS["callback"] + 0.1, 0.35)
# pass it on: split shimmer + BRAAAM finale, follow tap
put(L, shimmer(1.8), B["split"] - 0.1, 0.5); put(L, lib("whoosh_long"), B["split"], 0.4); put(L, braam(2.4), B["split"] + 0.9, 0.55)
put(L, cymbal(), B["split"] + 0.9, 0.25)
put(L, click(), B["follow"] + 0.55, 0.8); put(L, lib("ding"), B["follow"] + 0.6, 0.45)
# whooshes + gulps on cuts
mouth_end = {"door", "stage", "train", "teacher", "hero", "stadium", "umpire", "zoom", "dog", "callback"}   # clip ends inside a mouth / black
for k in range(1, len(st)):
    put(L, lib("whoosh"), st[k] - 0.14, 0.32)
    if tl["names"][k - 1] in mouth_end or k == 1: put(L, gulp(), st[k] - 0.05, 0.5); ev["mouths"].append(st[k])

# ---------------- music bed: playful pizzicato + bassoon from the title to the finale
bpm = 112; beat = 60 / bpm
prog = [(60, [64, 67, 72]), (55, [62, 67, 71]), (57, [64, 69, 72]), (53, [65, 69, 72])]
t = B["title"]; b = 0
while t < B["split"] + 0.8:
    root, ch = prog[(b // 4) % 4]
    g = 0.55 if SS["callback"] <= t < SS["pass"] else 1.0
    put(M, bassoon(hz(root - 12 if b % 2 == 0 else root - 5), beat * 0.9), t, 0.2 * g)
    if b % 2 == 1: put(M, pizz(hz(ch[(b // 2) % 3] + 12), 0.25, 0.8), t, 0.16 * g)
    put(M, pizz(hz(ch[b % 3] + 12), 0.2, 0.6), t + beat / 2, 0.1 * g)
    t += beat; b += 1
put(M, tada(), B["split"] + 0.9, 0.5)

# ---------------- YAWNS (realistic source-filter voices), one or more in every scene, music ducks under them
Yb = np.zeros(n); _seed = [100]
def YW(t, kind, g=0.9, length=1.0):
    _seed[0] += 1
    y, onset = V.yawn(kind, length, seed=_seed[0]); put(Yb, y, t - onset, g)
def chorus(t0, kinds, gap, g, length=0.8):
    for i, kd in enumerate(kinds): YW(t0 + i * gap, kd, g, length)
YW(Y1, "man", 1.0); YW(Y1 + 0.3, "woman", 0.55, 0.7)                                  # dulha + dulhan
YW(B["dadi"], "dadi", 1.0); chorus(B["dadi"] + 0.35, ["man", "woman", "man", "woman", "kid"], 0.14, 0.4)   # Dadi + khandaan
YW(B["title"] + 0.9, "mascot", 0.6, 0.8)                                                # the villain itself
YW(SS["train"] + 0.35, "woman", 0.9); chorus(SS["train"] + 0.9, ["man", "woman", "man", "kid", "man", "woman"], 0.32, 0.38, 0.75)
YW(B["teacher_yawn"], "woman", 1.0); chorus(B["teacher_yawn"] + 0.6, ["kid", "kid"], 0.25, 0.35, 0.7)
YW(B["hero_yawn"], "man", 1.0, 1.1); chorus(B["hero_yawn"] + 0.4, ["man", "man", "man", "man"], 0.15, 0.32, 0.8)
chorus(SS["stadium"] + 0.5, ["man", "woman", "man", "kid", "woman", "man", "man", "woman", "kid", "man", "woman", "man"], 0.11, 0.24, 0.9)
YW(SS["stadium"] + 0.3, "man", 0.8)
YW(B["appeal"] + 0.1, "man", 0.6, 0.8); YW(B["umpire_yawn"], "man", 1.0, 1.1); chorus(B["umpire_yawn"] + 0.4, ["man", "man"], 0.2, 0.35, 0.7)
YW(SS["lab"] + 0.25, "man", 0.95, 1.1)
YW(B["ice"] - 0.35, "mascot", 0.7, 0.9)
YW(SS["copy"] + 0.45, "man", 0.75, 0.9)
YW(B["burst"] + 0.05, "man", 1.0, 1.1)
chorus(SS["dinner"] + 0.35, ["dadi", "man", "woman", "kid"], 0.38, 0.7, 0.75)
YW(B["night_yawn"], "man", 0.95)
YW(B["mummy_yawn"], "woman", 1.0); YW(B["mummy_yawn"] + 0.45, "kid", 0.6, 0.8); YW(B["mummy_yawn"] + 0.95, "dog", 0.35, 0.6)
YW(SS["zoom"] + 0.6, "man", 0.8); chorus(SS["zoom"] + 1.0, ["woman", "man", "kid", "woman", "man", "dadi", "man", "woman"], 0.2, 0.32, 0.7)
YW(SS["dog"] + 0.2, "man", 0.8); YW(B["dog_yawn"], "dog", 0.85); YW(B["chimps"], "chimp", 0.6); YW(B["chimps"] + 0.35, "chimp", 0.55)
YW(B["impact"] + 0.9, "mascot", 0.6, 0.8)
YW(B["couple_yawn"], "man", 1.0); YW(B["couple_yawn"] + 0.1, "woman", 0.75)
chorus(B["split"] - 0.2, ["mascot"] * 6, 0.15, 0.3, 0.6)
# duck music + effects slightly under every yawn so the yawns are clearly heard
env = np.abs(Yb); env = signal.lfilter([0.002], [1, -0.998], env); env = env / (env.max() or 1)
duck = 1 - 0.55 * np.clip(env * 3, 0, 1)
M *= duck; L *= (1 - 0.3 * np.clip(env * 3, 0, 1))
L += Yb * 1.15

mix = np.tanh((L * 0.95 + M * 0.85) * 1.1)
mix = mix / np.max(np.abs(mix)) * 0.89
fo = int(SR * 0.6); mix[-fo:] *= np.linspace(1, 0, fo)
wavfile.write("soundtrack.wav", SR, (np.stack([mix, mix], 1) * 32767).astype(np.int16))
json.dump(ev, open("events.json", "w"), indent=1)
print("soundtrack", round(DUR, 2), "mouth cuts", len(ev["mouths"]))
