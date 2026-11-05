#!/usr/bin/env python3
"""Tighten the voiceover: shorten the dead air between sentences, drop the
stray laugh at the very end, then apply a tiny pitch-preserving tempo change
so the reel lands on TARGET seconds. Writes build/vo_tight.wav and
build/vo_map.json (original time -> new time), used by build.py to keep
every visual cut in sync with the words."""
import json, os, re, subprocess, sys
import numpy as np
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "vo_original.mp3")
OUT = os.path.join(HERE, "build")
TARGET = 75.0
SR = 48000
GAP = 0.12                      # normal pause between sentences
LONG = {2.5: 0.32, 49.1: 0.30, 83.4: 0.30}   # beats that deserve a breath
DROP_AFTER = 86.66               # the "(laughs)" artefact after the CTA

os.makedirs(OUT, exist_ok=True)
raw = os.path.join(OUT, "vo_raw.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-ar", str(SR), "-ac", "1", raw], check=True)
sr, a = wavfile.read(raw)
a = a.astype(np.float64) / 32768
dur = len(a) / sr

log = subprocess.run(["ffmpeg", "-i", raw, "-af", "silencedetect=n=-38dB:d=0.18", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
# speech chunks = gaps between silences
chunks, cur = [], 0.0
for s, e in zip(st, en):
    if s > cur:
        chunks.append([cur, s])
    cur = e
if cur < dur:
    chunks.append([cur, dur])
chunks = [[s, min(e, DROP_AFTER)] for s, e in chunks if s < DROP_AFTER and e - s > 0.04]
POST_END = 0.0

PRE, POST = 0.03, 0.06
pieces, mapping, t_new = [], [], 0.0
fade = int(0.006 * sr)
for i, (s, e) in enumerate(chunks):
    s0, e0 = max(0, s - PRE), min(DROP_AFTER if e >= DROP_AFTER else dur, e + POST)
    seg = a[int(s0 * sr):int(e0 * sr)].copy()
    seg[:fade] *= np.linspace(0, 1, fade); seg[-fade:] *= np.linspace(1, 0, fade)
    mapping.append([s0, e0, t_new])
    pieces.append(seg); t_new += len(seg) / sr
    if i < len(chunks) - 1:
        g = GAP
        for k, v in LONG.items():
            if e0 <= k <= chunks[i + 1][0] + 0.3:
                g = v
        pieces.append(np.zeros(int(g * sr))); t_new += g
tight = np.concatenate(pieces + [np.zeros(int(0.05 * sr))])
L = len(tight) / sr
tempo = max(1.0, L / TARGET)
mid = os.path.join(OUT, "vo_gapped.wav")
wavfile.write(mid, sr, (tight * 32767).astype(np.int16))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mid, "-af",
                f"rubberband=tempo={tempo:.5f}:pitch=1:formant=preserved:transients=crisp",
                os.path.join(OUT, "vo_tight.wav")], check=True)
json.dump({"tempo": tempo, "chunks": mapping, "length": L / tempo}, open(os.path.join(OUT, "vo_map.json"), "w"), indent=1)
print(f"{len(chunks)} phrases | original {dur:.2f}s -> gaps tightened {L:.2f}s -> tempo x{tempo:.3f} -> {L/tempo:.2f}s")
