#!/usr/bin/env python3
"""Sound for the Zomato Economy reel.

- An original music bed (synthesised here, so no copyright claims):
  100 BPM, A minor, a dark "money documentary" pulse that drops out for the
  "Lekin..." turn, gets busier under the numbers, and resolves to C major on
  the brand card.
- Sound design on the cuts and reveals, using reels/tools/sfx.py plus a few
  sounds made here (coins, paper slap, doorbell, shimmer).
- The kitchen sizzle from the chef clip, and the user's dramatic sting.
- The music ducks under the voice; the mix is normalised to -14 LUFS for Reels.
Writes build/mix.wav.
"""
import json, os, subprocess, sys
import numpy as np
from scipy import signal
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "tools")))
import sfx  # noqa: E402  (the repo's synthesised SFX library)
from timing import sh, END, pause_at, PAUSES, VO_END  # noqa: E402

SR = sfx.SR
N = int(SR * END)
rng = np.random.default_rng(5)
t_all = np.arange(N) / SR


def lp(x, f, o=4):
    return signal.sosfilt(signal.butter(o, f, "low", fs=SR, output="sos"), x)


def hp(x, f, o=2):
    return signal.sosfilt(signal.butter(o, f, "high", fs=SR, output="sos"), x)


def bp(x, f0, f1, o=2):
    return signal.sosfilt(signal.butter(o, [f0, f1], "band", fs=SR, output="sos"), x)


def place(bus, x, t, gain=1.0, pan=0.0):
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    x = x * gain * np.array([min(1, 1 - pan), min(1, 1 + pan)])
    i = int(t * SR)
    if i >= len(bus):
        return
    j = min(len(bus), i + len(x))
    bus[i:j] += x[: j - i]


def load_audio(path, start=0.0, dur=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-i", path]
    if dur:
        cmd += ["-t", str(dur)]
    cmd += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)


# ---------------------------------------------------------------- music
BPM = 100
BEAT = 60 / BPM
GRID0 = 2.33                    # the beat starts on the first cut after the hook
BREAK = (sh(42.62), sh(44.61))  # "Lekin ek baat..." - drums out
BUSY = (sh(52.83), sh(67.00))   # the numbers - more drive
OUTRO = sh(72.13)               # brand card - resolve
F_AT, G_AT = sh(67.0), sh(69.26)
MEME = os.path.join(HERE, "media", "memes")
# meme music beds replace the synth bed in these windows: (file, start, src_in, length)
MEME_BEDS = [
    ("myinstants_7.mp3", sh(37.90), 0.0, sh(42.62) - sh(37.90)),          # Zomato Gold
    ("myinstants_4.mp3", sh(42.62), 0.0, pause_at(2) + 0.85 - sh(42.62)), # sad flute: not all profit
    ("myinstants_5.mp3", sh(55.00), 0.0, sh(67.00) - sh(55.00)),          # epic theme: the numbers
]

NOTE = {"A": 55.0, "F": 43.65, "C": 65.41, "G": 49.0, "E": 41.2, "D": 36.71}
CHORDS = {"Am": ("A", [0, 3, 7]), "F": ("F", [0, 4, 7]), "C": ("C", [0, 4, 7]), "G": ("G", [0, 4, 7])}
PROG = ["Am", "F", "C", "G"]


def chord_at(t):
    if t >= OUTRO:
        return "C"
    if t >= G_AT:
        return "G"
    if t >= F_AT:
        return "F"
    if t < GRID0:
        return "Am"
    bar = int((t - GRID0) // (BEAT * 4))
    return PROG[bar % 4]


def saw(f, t):
    return signal.sawtooth(2 * np.pi * f * t)


def build_music():
    L = np.zeros(N); R = np.zeros(N)
    # --- pad: per-chord blocks with crossfades
    changes = [0.0]
    t = GRID0
    while t < F_AT:
        changes.append(t); t += BEAT * 4
    changes += [F_AT, G_AT, OUTRO, END]
    changes = sorted(set(round(c, 4) for c in changes if c <= END))
    for a, b in zip(changes[:-1], changes[1:]):
        name = chord_at(a + 0.01)
        root, iv = CHORDS[name]
        f0 = NOTE[root] * 4  # octave 3/4 voicing
        i0, i1 = int(a * SR), int(min(END, b + 0.6) * SR)
        tt = np.arange(i1 - i0) / SR
        x = np.zeros_like(tt); y = np.zeros_like(tt)
        for k, s in enumerate(iv + [12]):
            f = f0 * 2 ** (s / 12)
            x += saw(f * 1.0015, tt) + 0.6 * saw(f * 0.998, tt + 0.01 * k)
            y += saw(f * 0.9985, tt) + 0.6 * saw(f * 1.002, tt + 0.013 * k)
        env = np.minimum(1, tt / 0.35) * np.clip((b + 0.6 - a - tt) / 0.6, 0, 1)
        cutoff = 900 if name != "C" else 1500
        L[i0:i1] += lp(x, cutoff) * env * 0.06
        R[i0:i1] += lp(y, cutoff) * env * 0.06
    pad = np.stack([L, R], 1)
    pad *= (0.8 + 0.2 * np.sin(2 * np.pi * 0.11 * t_all))[:, None]

    # --- bass: pumping 8ths on the chord root
    bass = np.zeros(N)
    step = BEAT / 2
    t = GRID0
    while t < OUTRO:
        if not (BREAK[0] <= t < BREAK[1]):
            f = NOTE[CHORDS[chord_at(t)][0]]
            n = int(step * SR); tt = np.arange(n) / SR
            note = np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * 2 * f * tt)
            note *= np.minimum(1, tt / 0.012) * np.exp(-tt * 5.5)
            i = int(t * SR); j = min(N, i + n)
            bass[i:j] += note[: j - i] * (0.55 if BUSY[0] <= t < BUSY[1] else 0.42)
        t += step
    bass = np.tanh(lp(bass, 260) * 1.6) * 0.5

    # --- drums
    drums = np.zeros((N, 2))
    kick_t = np.arange(int(0.3 * SR)) / SR
    kick = np.sin(2 * np.pi * np.cumsum(110 * np.exp(-kick_t * 22) + 44) / SR) * np.exp(-kick_t * 9)
    hat_t = np.arange(int(0.03 * SR)) / SR
    hat = hp(rng.standard_normal(len(hat_t)), 7000) * np.exp(-hat_t * 180)
    snare_t = np.arange(int(0.25 * SR)) / SR
    snare = bp(rng.standard_normal(len(snare_t)), 900, 5000) * np.exp(-snare_t * 22)
    snare = sfx.reverb(snare, 0.8, 0.25)
    b = 0
    t = GRID0
    while t < OUTRO:
        busy = BUSY[0] <= t < BUSY[1]
        if not (BREAK[0] <= t < BREAK[1]):
            beat_in_bar = b % 4
            if beat_in_bar in (0, 2) or busy:
                place(drums, kick, t, 0.55 if busy else 0.48)
            if busy and beat_in_bar in (1, 3):
                place(drums, snare, t, 0.16, pan=0.05)
            for s in range(4):
                g = (0.05 if s % 2 else 0.08) * (1.5 if busy else 1.0)
                place(drums, hat, t + s * BEAT / 4, g, pan=0.25 if s % 2 else -0.15)
        t += BEAT; b += 1

    # --- intro drone under the hook + outro tail
    drone = np.zeros((N, 2))
    dr = sfx.drone(3.0)
    dr = dr * np.minimum(1, np.linspace(0, 6, len(dr))) * np.minimum(1, np.linspace(3, 0, len(dr)))
    place(drone, dr, 0.0, 0.35)

    mus = pad + bass[:, None] + drums + drone
    mus /= np.sqrt(np.mean(mus[np.abs(mus).sum(1) > 1e-4] ** 2)) / 0.1  # RMS -20 dBFS
    gate = np.ones(N)
    beds = np.zeros((N, 2))
    for f, t0, src, ln in MEME_BEDS:
        a, b = int(t0 * SR), int(min(END, t0 + ln) * SR)
        ramp = int(0.25 * SR)
        gate[a:b] = 0
        gate[max(0, a - ramp):a] = np.linspace(1, 0, a - max(0, a - ramp))
        gate[b:b + ramp] = np.minimum(gate[b:b + ramp], np.linspace(0, 1, len(gate[b:b + ramp])))
        x = load_audio(os.path.join(MEME, f), src, ln + 0.3)
        x = x / (np.sqrt(np.mean(x ** 2)) + 1e-9) * 0.1                       # same RMS as the bed
        fi, fo = int(0.15 * SR), int(min(0.6, ln / 3) * SR)
        x[:fi] *= np.linspace(0, 1, fi)[:, None]
        x = x[: int(ln * SR) + fo]
        x[-fo:] *= np.linspace(1, 0, fo)[:, None]
        place(beds, x, t0, 0.9)
    mus = mus * gate[:, None] + beds
    # music fades at the very end
    f = int(1.6 * SR)
    mus[-f:] *= np.linspace(1, 0, f)[:, None] ** 1.5
    return mus


# ---------------------------------------------------------------- extra sfx
def coin(pitch=1.0):
    tt = np.arange(int(0.35 * SR)) / SR
    parts = [(2793, 1.0, 14), (4210, 0.6, 18), (5980, 0.4, 24), (7620, 0.25, 30)]
    x = sum(a * np.sin(2 * np.pi * f * pitch * tt) * np.exp(-tt * d) for f, a, d in parts)
    x += hp(rng.standard_normal(len(tt)), 4000) * np.exp(-tt * 300) * 0.4
    return sfx.norm(x, 0.5)


def slap():
    """Paper slapped onto a board."""
    tt = np.arange(int(0.25 * SR)) / SR
    x = bp(rng.standard_normal(len(tt)), 300, 4500) * np.exp(-tt * 40)
    x += np.sin(2 * np.pi * 90 * tt) * np.exp(-tt * 30) * 0.8
    return sfx.norm(sfx.reverb(x, 0.4, 0.15), 0.8)


def doorbell():
    tt = np.arange(int(1.4 * SR)) / SR
    def tone(f, d):
        u = np.clip(tt - d, 0, None)
        return (np.sin(2 * np.pi * f * u) + 0.3 * np.sin(2 * np.pi * 2.76 * f * u)) * np.exp(-u * 3.2) * (tt >= d)
    return sfx.norm(sfx.reverb(tone(659.3, 0) + tone(523.3, 0.42), 0.9, 0.2), 0.55)


def shimmer(dur=1.4):
    tt = np.arange(int(dur * SR)) / SR
    x = np.zeros_like(tt)
    for k in range(18):
        d = rng.uniform(0, dur * 0.7); f = rng.uniform(2500, 7000)
        u = np.clip(tt - d, 0, None)
        x += np.sin(2 * np.pi * f * u) * np.exp(-u * 9) * (tt >= d) * rng.uniform(0.3, 1)
    return sfx.norm(sfx.reverb(x, 1.2, 0.35), 0.45)


def build_sfx():
    bus = np.zeros((N, 2))

    def cue(x, t, gain=1.0, pan=0.0):  # cue times are on the 75 s grid
        place(bus, x, sh(t), gain, pan)
    L = {k: sfx.LIBRARY[k]() for k in ["whoosh", "whoosh_down", "whoosh_long", "swish", "pop", "pop_low",
                                        "pop_high", "hit", "boom", "riser", "riser_short", "glitch", "ding"]}
    # hook: note shatters -> ZOMATO slams
    cue(L["glitch"], 0.00, 0.35)
    cue(L["whoosh_long"], 0.55, 0.30, -0.2)
    cue(L["boom"], 2.04, 0.30)
    cue(meme("myinstants_3.mp3", 0, 1.42), 2.02, 0.55)                    # meme: bang on ZOMATO
    cue(L["hit"], 2.04, 0.35)
    cuts = [2.33, 6.93, 9.93, 13.54, 14.78, 16.90, 19.36, 23.30, 25.25, 27.30, 29.20, 31.72, 34.05,
            37.90, 44.61, 48.29, 52.83, 55.00, 60.58, 63.78, 67.00, 69.26]
    for k, c in enumerate(cuts):
        cue(L["swish"] if k % 2 else L["whoosh"], c - 0.12, 0.16, pan=0.3 if k % 2 else -0.3)
    cue(L["pop"], 2.40, 0.25)
    cue(L["hit"], 8.43, 0.30)                      # the "?" appears
    cue(L["pop_high"], 18.40, 0.25)                # zomato logo forms
    cue(slap(), 20.36, 0.55)                       # COMMISSION banner
    for k, tt in enumerate([23.45, 23.9, 24.3, 24.75]):  # coins fly
        cue(coin(1 + 0.06 * k), tt, 0.22, pan=(-0.3, 0.3)[k % 2])
    cue(L["ding"], 27.36, 0.30)                    # checkout
    for k, tt in enumerate([29.45, 29.95, 30.95]):        # receipt lines appear
        cue(L["pop_low"], tt, 0.22, pan=0.1 * k)
    for tt in [34.6, 35.4, 36.4]:                         # ad cards flip
        cue(L["swish"], tt, 0.14, pan=0.2)
    cue(shimmer(1.6), 38.0, 0.35)                  # Zomato Gold
    cue(L["riser_short"], 39.9, 0.12)
    # dramatic sting for the turn (user's meme sound; its hit lands on the cut)
    sting = load_audio(os.path.join(HERE, "media", "sting_dramatic.mp3"))
    sting = sting / (np.max(np.abs(sting)) or 1)
    cue(sting, 42.62 - 1.10, 0.42)
    for k in range(9):                                    # coins into the jar
        cue(coin(0.9 + 0.05 * (k % 3)), 44.75 + k * 0.16, 0.14, pan=rng.uniform(-0.3, 0.3))
    cue(slap(), 45.86, 0.55)                       # NOT ALL OF IT IS PROFIT
    cue(L["hit"], 45.86, 0.25)
    for k, tt in enumerate([49.43, 50.56, 51.13]):        # delivery / tech / marketing / ops
        cue(L["swish"], tt - 0.08, 0.18, pan=(-0.3, 0.3)[k % 2])
    cue(L["pop"], 53.02, 0.30)                     # Q2 FY27 tag
    cue(L["riser"], 57.95 - 1.6, 0.18)
    cue(L["hit"], 57.95, 0.55)                     # 11,445
    cue(slap(), 60.64, 0.45)                       # ADJUSTED REVENUE
    cue(L["riser_short"], 61.88 - 0.8, 0.18)
    cue(L["hit"], 61.88, 0.55)                     # 3,879
    cue(L["pop"], 63.92, 0.30)                     # EBITDA tag
    cue(L["hit"], 65.62, 0.55)                     # 627
    cue(doorbell(), 67.05, 0.32)
    cue(L["riser_short"], 69.9, 0.15)
    cue(shimmer(2.0), 70.75, 0.40)                 # gift glows
    cue(L["boom"], 72.13, 0.45)
    cue(L["pop_low"], 72.6, 0.25)                  # brand card lands
    # real sound from the chef clip: the sizzle
    sizzle = load_audio(os.path.join(HERE, "media", "chef.mp4"), 0.9, 1.3)
    sizzle = sizzle / (np.max(np.abs(sizzle)) or 1)
    fade = np.minimum(1, np.minimum(np.arange(len(sizzle)), np.arange(len(sizzle))[::-1]) / (0.12 * SR))
    cue(sizzle * fade[:, None], 13.54, 0.30)
    return bus


def meme(f, start=0.0, dur=None, fade=0.08):
    x = load_audio(os.path.join(MEME, f), start, dur)
    x = x / (np.max(np.abs(x)) or 1)
    fo = int(fade * SR)
    x[-fo:] *= np.linspace(1, 0, fo)[:, None]
    return x


def build_meme_voices():
    """Spoken / screamed memes sit in the voiceover pauses, not under words."""
    bus = np.zeros((N, 2))
    for f, t, start, dur, g in [
        ("myinstants_8.mp3", pause_at(0) + 0.03, 0.0, 0.63, 1.0),    # "huh?"
        ("myinstants_6.mp3", pause_at(1) + 0.02, 0.0, 0.62, 0.8),    # screaming cat
        ("myinstants_9.mp3", pause_at(2) + 0.02, 0.0, 1.00, 1.0),    # sobbing
        ("myinstants.mp3",   pause_at(3) + 0.00, 0.18, 1.25, 0.9),   # scream at 11,445 crore
        ("myinstants_10.mp3", sh(VO_END) + 0.05, 0.63, 1.95, 0.8),   # echo button on the brand card
    ]:
        x = meme(f, start, dur, fade=0.12)
        x = x / (np.sqrt(np.mean(x[np.abs(x).sum(1) > 1e-3] ** 2)) + 1e-9) * 0.125 * g  # ~VO loudness
        place(bus, x, t)
    return bus


# ---------------------------------------------------------------- mix
def main():
    vo = load_audio(os.path.join(BUILD, "vo_tight.wav"))
    # open the meme pauses in the voiceover
    parts, prev = [], 0
    for at, p in PAUSES:
        i = int(at * SR)
        parts += [vo[prev:i], np.zeros((int(p * SR), 2))]
        prev = i
    vo = np.vstack(parts + [vo[prev:]])
    vo = vo[:N] if len(vo) >= N else np.vstack([vo, np.zeros((N - len(vo), 2))])
    vo = hp(vo.T, 75).T
    music = build_music()
    fx = build_sfx()
    # duck the music under the voice (smooth envelope: 30 ms attack, 350 ms release)
    env = np.abs(vo[:, 0])
    a_att, a_rel = np.exp(-1 / (0.03 * SR)), np.exp(-1 / (0.35 * SR))
    from scipy.signal import lfilter
    # one-pole follower using release (dominant) then a short smoothing for attack
    e = lfilter([1 - a_rel], [1, -a_rel], env)
    e = lfilter([1 - a_att], [1, -a_att], e)
    e = e / (np.percentile(e[e > 1e-4], 90) or 1)
    duck = 1 - 0.55 * np.clip(e * 1.6, 0, 1)
    music *= duck[:, None]
    fx *= (1 - 0.3 * np.clip(e * 1.6, 0, 1))[:, None]

    def rms_db(x):
        return 20 * np.log10(np.sqrt(np.mean(x[np.abs(x).sum(1) > 1e-4] ** 2)) + 1e-12)
    vo *= 10 ** ((-18 - rms_db(vo)) / 20)
    music *= 10 ** ((-31.5 - rms_db(music)) / 20)
    fx *= 10 ** ((-29 - rms_db(fx)) / 20)
    mix = vo + music + fx + build_meme_voices()
    raw = os.path.join(BUILD, "mix_raw.wav")
    wavfile.write(raw, SR, (np.clip(mix, -1, 1) * 32767).astype(np.int16))
    # final loudness for Reels: -14 LUFS, -1 dBTP (two-pass loudnorm)
    meas = subprocess.run(["ffmpeg", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.2:LRA=9:print_format=json",
                           "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
    af = (f"loudnorm=I=-14:TP=-1.2:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", af, "-ar", str(SR),
                    os.path.join(BUILD, "mix.wav")], check=True)
    print("mix ->", os.path.join(BUILD, "mix.wav"))


if __name__ == "__main__":
    main()
