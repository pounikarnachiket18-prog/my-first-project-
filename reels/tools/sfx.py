#!/usr/bin/env python3
"""
Reels Studio - synthesized sound-effect library + cue mixer.

Every sound is generated from scratch (no samples), so there are no
licensing issues and the library can be regenerated anytime.

Usage:
  python3 tools/sfx.py                      # (re)build the SFX library into sfx/
  python3 tools/sfx.py mix cues.json out.wav DURATION
      cues.json = [{"t": 1.25, "sfx": "whoosh", "gain": 0.8, "pan": 0}, ...]
"""
import json
import os
import sys

import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 48000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFX_DIR = os.path.join(ROOT, "sfx")
rng = np.random.default_rng(7)


# ---------------------------------------------------------------- helpers
def t_axis(dur):
    return np.arange(int(SR * dur)) / SR


def env_adsr(n, a=0.005, d=0.1, s=0.0, r=0.05, curve=3.0):
    """Exponential-ish envelope of length n samples."""
    out = np.zeros(n)
    A, D, R = int(a * SR), int(d * SR), int(r * SR)
    A = max(A, 1)
    out[:A] = np.linspace(0, 1, A) ** 0.5
    end_d = min(n, A + D)
    if end_d > A:
        x = np.linspace(0, 1, end_d - A)
        out[A:end_d] = s + (1 - s) * (1 - x) ** curve
    if end_d < n:
        out[end_d:] = s
    if R > 0 and s > 0:
        out[-R:] *= np.linspace(1, 0, R)
    return out


def bandpass_sweep(noise, f_start, f_end, q=2.0, steps=64):
    """Time-varying band-pass on noise (block-wise, crossfaded)."""
    n = len(noise)
    out = np.zeros(n)
    block = n // steps + 1
    freqs = np.geomspace(f_start, f_end, steps)
    win = np.hanning(block * 2)
    for i, f in enumerate(freqs):
        lo = max(20, f / (1 + 1 / q))
        hi = min(SR / 2 - 100, f * (1 + 1 / q))
        sos = signal.butter(2, [lo, hi], btype="band", fs=SR, output="sos")
        s0 = max(0, i * block - block // 2)
        s1 = min(n, s0 + block * 2)
        seg = signal.sosfilt(sos, noise[s0:s1])
        out[s0:s1] += seg * win[: s1 - s0]
    return out


def lowpass(x, f, order=4):
    return signal.sosfilt(signal.butter(order, f, btype="low", fs=SR, output="sos"), x)


def highpass(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, btype="high", fs=SR, output="sos"), x)


def norm(x, peak=0.9):
    m = np.max(np.abs(x)) or 1
    return x / m * peak


def reverb(x, decay=1.2, mix=0.25):
    """Cheap algorithmic reverb: convolve with decaying noise tail."""
    n = int(SR * decay)
    ir = rng.standard_normal(n) * np.exp(-np.linspace(0, 6, n))
    ir = lowpass(ir, 6000)
    ir /= np.sum(np.abs(ir)) / 8
    wet = signal.fftconvolve(x, ir)
    wet = np.pad(wet, (0, max(0, len(x) + n - len(wet))))[: len(x) + n]
    dry = np.concatenate([x, np.zeros(n)])
    return dry * (1 - mix) + norm(wet, np.max(np.abs(x))) * mix


def stereo(x, width=0.0):
    """Mono -> stereo with optional Haas widening."""
    d = int(0.012 * SR * width)
    l = x
    r = np.concatenate([np.zeros(d), x])[: len(x)] if d else x
    return np.stack([l, r], axis=1)


# ---------------------------------------------------------------- sounds
def whoosh(dur=0.45, f0=300, f1=5000):
    n = int(SR * dur)
    x = bandpass_sweep(rng.standard_normal(n), f0, f1, q=1.6)
    e = np.sin(np.linspace(0, np.pi, n)) ** 2.2
    return norm(reverb(x * e, 0.6, 0.2), 0.8)


def whoosh_down(dur=0.5):
    return whoosh(dur, 6000, 250)


def swish(dur=0.18):
    n = int(SR * dur)
    x = bandpass_sweep(rng.standard_normal(n), 1500, 9000, q=2.5, steps=24)
    e = np.sin(np.linspace(0, np.pi, n)) ** 3
    return norm(x * e, 0.7)


def pop(f=900):
    t = t_axis(0.12)
    freq = f * np.exp(-t * 30) + f * 0.45
    ph = 2 * np.pi * np.cumsum(freq) / SR
    x = np.sin(ph) * np.exp(-t * 45)
    click = rng.standard_normal(len(t)) * np.exp(-t * 900) * 0.3
    return norm(x + click, 0.75)


def tick():
    t = t_axis(0.04)
    x = highpass(rng.standard_normal(len(t)), 3000) * np.exp(-t * 300)
    x += np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 200) * 0.5
    return norm(x, 0.55)


def hit():
    """Cinematic impact: sub thump + noise crack + tail."""
    t = t_axis(1.6)
    freq = 140 * np.exp(-t * 18) + 42
    sub = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * 3.2)
    crack = lowpass(rng.standard_normal(len(t)), 3500) * np.exp(-t * 28)
    body = np.tanh(sub * 2.2) * 0.9 + crack * 0.6
    return norm(reverb(body, 1.4, 0.3), 0.95)


def boom():
    """Deep sub drop for the big reveal."""
    t = t_axis(2.4)
    freq = 90 * np.exp(-t * 2.5) + 30
    sub = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * 1.6)
    return norm(np.tanh(sub * 3), 0.95)


def riser(dur=1.6):
    n = int(SR * dur)
    t = np.arange(n) / SR
    noise = bandpass_sweep(rng.standard_normal(n), 400, 9000, q=3, steps=80)
    freq = np.geomspace(180, 1400, n)
    tone = signal.sawtooth(2 * np.pi * np.cumsum(freq) / SR) * 0.15
    tone = lowpass(tone, 5000)
    e = (t / dur) ** 2.5
    return norm((noise + tone) * e, 0.8)


def glitch(dur=0.35):
    n = int(SR * dur)
    x = np.zeros(n)
    i = 0
    while i < n:
        seg = int(SR * rng.uniform(0.01, 0.045))
        kind = rng.integers(0, 3)
        tt = np.arange(seg) / SR
        if kind == 0:
            s = signal.square(2 * np.pi * rng.uniform(80, 900) * tt) * 0.5
        elif kind == 1:
            s = rng.standard_normal(seg) * 0.6
        else:
            s = np.zeros(seg)
        x[i : i + seg] = s[: max(0, min(seg, n - i))]
        i += seg
    x = np.round(x * 6) / 6  # bitcrush
    return norm(highpass(x, 120), 0.6)


def ding():
    """Generic phone notification chime (original, two-tone)."""
    t = t_axis(0.9)
    a = np.sin(2 * np.pi * 1318.5 * t) * np.exp(-t * 6)
    b = np.zeros_like(t)
    off = int(0.11 * SR)
    tb = t[: len(t) - off]
    b[off:] = np.sin(2 * np.pi * 1760 * tb) * np.exp(-tb * 5)
    x = a + b + 0.25 * np.sin(2 * np.pi * 2637 * t) * np.exp(-t * 12)
    return norm(reverb(x, 0.8, 0.2), 0.6)


def buzz():
    """Phone vibration buzz."""
    t = t_axis(0.42)
    x = signal.square(2 * np.pi * 150 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 25 * t))
    x = lowpass(x, 900)
    e = np.ones_like(t)
    e[: int(0.01 * SR)] = np.linspace(0, 1, int(0.01 * SR))
    e[-int(0.04 * SR):] = np.linspace(1, 0, int(0.04 * SR))
    return norm(x * e, 0.6)


def heartbeat():
    t = t_axis(0.9)
    def thump(d):
        tt = np.clip(t - d, 0, None)
        return np.sin(2 * np.pi * 55 * tt) * np.exp(-tt * 18) * (t >= d)
    return norm(lowpass(thump(0) + 0.7 * thump(0.22), 200), 0.9)


def type_key():
    t = t_axis(0.05)
    x = highpass(rng.standard_normal(len(t)), 1800) * np.exp(-t * 160)
    return norm(x, 0.4)


def shutter():
    t = t_axis(0.18)
    a = highpass(rng.standard_normal(len(t)), 2000) * np.exp(-t * 120)
    b = np.roll(a, int(0.07 * SR)) * 0.8
    return norm(a + b, 0.6)


def counter_tick():
    t = t_axis(0.03)
    return norm(np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 260), 0.35)


def drone(dur=30.0):
    """Dark tension bed (very low in the mix)."""
    t = t_axis(dur)
    x = sum(
        np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * a
        for f, a in [(55, 1), (55.4, 0.7), (82.4, 0.35), (110.3, 0.2)]
    )
    x *= 0.75 + 0.25 * np.sin(2 * np.pi * 0.25 * t)
    air = lowpass(rng.standard_normal(len(t)), 600) * 0.15
    return norm(x + air, 0.5)


def warm_pad(dur=10.0):
    """Hopeful major pad for the turn/CTA."""
    t = t_axis(dur)
    notes = [261.63, 329.63, 392.0, 523.25]
    x = sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.003 * t) for f in notes)
    x = lowpass(x, 2500)
    e = np.minimum(1, t / 1.2) * np.minimum(1, (dur - t) / 1.5)
    return norm(reverb(x * e, 2.0, 0.35), 0.45)


LIBRARY = {
    "whoosh": whoosh,
    "whoosh_down": whoosh_down,
    "whoosh_long": lambda: whoosh(0.9, 200, 7000),
    "swish": swish,
    "pop": pop,
    "pop_low": lambda: pop(520),
    "pop_high": lambda: pop(1400),
    "tick": tick,
    "hit": hit,
    "boom": boom,
    "riser": riser,
    "riser_short": lambda: riser(0.8),
    "glitch": glitch,
    "ding": ding,
    "buzz": buzz,
    "heartbeat": heartbeat,
    "key": type_key,
    "shutter": shutter,
    "counter": counter_tick,
    "drone": drone,
    "pad": warm_pad,
}


def write(name, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1:
        x = stereo(x, 0.3)
    wavfile.write(os.path.join(SFX_DIR, f"{name}.wav"), SR, (x * 32767).astype(np.int16))


def build_library():
    os.makedirs(SFX_DIR, exist_ok=True)
    for name, fn in LIBRARY.items():
        write(name, fn())
    print(f"built {len(LIBRARY)} sounds -> {SFX_DIR}")


def load(name):
    path = os.path.join(SFX_DIR, f"{name}.wav")
    if not os.path.exists(path):
        write(name, LIBRARY[name]())
    sr, d = wavfile.read(path)
    d = d.astype(np.float64) / 32767
    if d.ndim == 1:
        d = np.stack([d, d], 1)
    return d


def mix(cues_path, out_path, duration):
    with open(cues_path) as f:
        cues = json.load(f)
    n = int(SR * float(duration))
    bus = np.zeros((n, 2))
    cache = {}
    for c in cues:
        name = c["sfx"]
        if name not in cache:
            cache[name] = load(name)
        s = cache[name] * float(c.get("gain", 1.0))
        if "dur" in c:  # trim + fade
            m = int(SR * c["dur"])
            s = s[:m].copy()
            f = min(len(s), int(SR * 0.5))
            s[-f:] *= np.linspace(1, 0, f)[:, None]
        pan = float(c.get("pan", 0))
        s = s * np.array([min(1, 1 - pan), min(1, 1 + pan)])
        i = int(SR * float(c["t"]))
        if i >= n:
            continue
        j = min(n, i + len(s))
        bus[i:j] += s[: j - i]
    # bus glue: soft-clip + normalise to about -1 dBFS peak
    bus = np.tanh(bus * 1.1)
    bus = bus / (np.max(np.abs(bus)) or 1) * 0.89
    fade = int(SR * 0.4)
    bus[-fade:] *= np.linspace(1, 0, fade)[:, None]
    wavfile.write(out_path, SR, (bus * 32767).astype(np.int16))
    print(f"mixed {len(cues)} cues -> {out_path}")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "mix":
        mix(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        build_library()
