#!/usr/bin/env python3
"""Synthesize a two-tone airport PA chime ("ding... dong") -> audio/chime.wav."""
import os

import numpy as np
from scipy.io import wavfile

SR = 48000
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio", "chime.wav")


def bell(freq, dur=1.8):
    t = np.arange(int(SR * dur)) / SR
    # vibraphone-like: fundamental + soft overtones, fast attack, long decay
    partials = [(1.0, 1.0, 2.2), (2.0, 0.35, 3.5), (3.01, 0.12, 5.0), (4.2, 0.05, 7.0)]
    x = sum(a * np.sin(2 * np.pi * freq * m * t) * np.exp(-t * d) for m, a, d in partials)
    attack = np.minimum(1, t / 0.004)
    return x * attack


def main():
    n = int(SR * 2.6)
    bus = np.zeros(n)
    for start, f in [(0.0, 659.25), (0.55, 523.25)]:  # E5 then C5
        s = bell(f)
        i = int(SR * start)
        bus[i:i + len(s)] += s[: n - i]
    bus = bus / np.max(np.abs(bus)) * 0.6
    # light room reverb: a few decaying echoes
    wet = np.zeros_like(bus)
    for delay, g in [(0.031, 0.35), (0.067, 0.25), (0.113, 0.18), (0.171, 0.12)]:
        k = int(SR * delay)
        wet[k:] += bus[:-k] * g
    st = np.stack([bus + wet * 0.9, bus + np.roll(wet, 240) * 0.9], 1)
    st = st / np.max(np.abs(st)) * 0.7
    fade = int(SR * 0.3)
    st[-fade:] *= np.linspace(1, 0, fade)[:, None]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    wavfile.write(OUT, SR, (st * 32767).astype(np.int16))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
