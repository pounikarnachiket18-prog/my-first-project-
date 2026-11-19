"""Composite the motion-graphics layer over the Royal Enfield reel.

Inputs : ../../../output/royal-enfield-reel.mp4            (base picture)
         ../../../output/royal-enfield-reel-voiceover.mp4  (voiceover mix, used as the audio bed)
         frames/%05d.png                                   (from render_mg.cjs)
Output : ../../../output/royal-enfield-reel-mg.mp4

Adds camera punch-zooms on cuts, shake on hits, a sepia flashback (England clips),
black & white on the freeze frame, grain + vignette, and an SFX layer synced to the graphics.
"""
import os, subprocess, sys
import numpy as np
from scipy import signal
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
REELS = os.path.abspath(os.path.join(HERE, "../../.."))
sys.path.insert(0, os.path.join(REELS, "tools"))
import sfx as SX
SX.SFX_DIR = os.path.join(REELS, "sfx"); os.makedirs(SX.SFX_DIR, exist_ok=True)

BASE = os.path.join(REELS, "output/royal-enfield-reel.mp4")
VO = os.path.join(REELS, "output/royal-enfield-reel-voiceover.mp4")
OUT = os.path.join(REELS, "output/royal-enfield-reel-mg.mp4")
TMP = os.path.join(HERE, "tmp"); os.makedirs(TMP, exist_ok=True)

H1, CL, N = 5.4333333, 3.4666667, 15
S = [0.0] + [H1 + CL * (k - 1) for k in range(1, N)]
END = S[-1] + CL
DUR = 55.8
FREEZE0, FREEZE1 = 2.40, 3.85
STAMP_CLIPS = [1, 2, 3, 6, 7, 8, 9, 10, 11, 12]
TEARS = [3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14]

# ------------------------------------------------------------------ audio
SR = 48000
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", VO, "-vn", "-ac", "2", "-ar", str(SR), os.path.join(TMP, "bed.wav")], check=True)
_, bed = wavfile.read(os.path.join(TMP, "bed.wav"))
bed = bed.astype(np.float64) / 32768
n = len(bed)
fx = np.zeros((n, 2))
rng = np.random.default_rng(7)


def put(x, t, g):
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    i = int(t * SR)
    if i >= n: return
    j = min(n, i + len(x)); fx[i:j] += x[: j - i] * g


def paper(d=0.32):
    """Paper rip: crackly band-passed noise with a fast swell."""
    t = np.arange(int(SR * d)) / SR
    x = rng.normal(size=len(t)) * (rng.random(len(t)) < 0.35)
    x = signal.sosfilt(signal.butter(2, [900, 7000], "band", fs=SR, output="sos"), x)
    env = np.minimum(1, t / 0.05) * np.exp(-np.maximum(0, t - 0.12) * 14)
    x *= env
    return x / np.max(np.abs(x))


L = SX.load
put(L("shutter"), S[1] - 0.05, 0.25)
for k in TEARS:
    put(paper(), S[k] - 0.2, 0.32)
for k in STAMP_CLIPS:
    put(L("hit"), S[k] + 0.44, 0.28)
# freeze
put(L("hit"), FREEZE0, 0.35); put(L("glitch"), 2.85, 0.2); put(L("pop"), 3.05, 0.25)
put(L("pop_high"), FREEZE1 + 0.35, 0.18); put(L("pop_high"), FREEZE1 + 0.47, 0.18)
# specials
put(L("boom"), S[2] + 1.5, 0.22)
put(L("pop"), S[3] + 0.25, 0.28); put(L("pop"), S[3] + 0.33, 0.22); put(L("swish"), S[3] + 0.3, 0.2)
for i in range(10): put(L("tick"), S[5] + 0.6 + i * 0.1, 0.1)
put(L("ding"), S[5] + 1.65, 0.28); put(L("swish"), S[5] + 1.9, 0.15)
put(L("swish"), S[6] + 0.3, 0.22)
put(L("whoosh"), S[7] + 0.45, 0.22)
put(L("swish"), S[8] + 0.2, 0.18); put(L("buzz"), S[8] + 1.7, 0.12)
put(L("whoosh_down"), S[9] + 0.4, 0.28); put(L("hit"), S[9] + 1.55, 0.28)
for i in range(13): put(L("tick"), S[10] + 1.2 + i * 0.1, 0.08)
put(L("ding"), S[10] + 2.55, 0.3)
for i in range(5): put(L("pop_low"), S[11] + 0.25 + i * 0.07, 0.12)
put(L("whoosh"), S[11] + 1.3, 0.25)
put(L("swish"), S[12] + 0.2, 0.18); put(L("pop"), S[12] + 1.95, 0.22); put(L("ding"), S[12] + 2.25, 0.26)
for t in np.arange(S[13] + 0.3, S[13] + 1.5, 0.07): put(L("counter"), t, 0.06)
put(L("hit"), S[13] + 1.5, 0.28)
for t in np.arange(S[13] + 1.55, S[13] + 2.3, 0.08): put(L("counter"), t, 0.05)
for i in range(5): put(L("pop_high"), S[14] + 0.35 + i * 0.16, 0.16)
put(L("pop"), S[14] + 1.72, 0.32)
for m in range(4): put(L("tick"), S[14] + 1.72 + 0.35 + m * 0.9, 0.14)

mix = bed + fx
mix = np.tanh(mix * 1.05) / np.tanh(1.05)
wavfile.write(os.path.join(TMP, "mix.wav"), SR, (np.clip(mix, -1, 1) * 32767).astype(np.int16))

# ------------------------------------------------------------------ picture
punches = [(S[k], 0.03 if k in (1, 2) else 0.05, 0.35) for k in range(1, N)]
punches += [(FREEZE0, 0.10, 0.4), (S[2] + 1.5, 0.04, 0.3), (S[10] + 0.6, 0.04, 0.35), (S[11] + 1.6, 0.035, 0.3), (S[13] + 1.5, 0.03, 0.3)]
shakes = [(FREEZE0, 0.45, 14), (S[2] + 1.5, 0.4, 12), (S[10] + 0.6, 0.5, 12), (S[11] + 1.6, 0.25, 8)]

zt = ["1"]
for a, amp, d in punches:
    zt.append(f"{amp}*between(t,{a:.3f},{a+d:.3f})*pow(1-(t-{a:.3f})/{d},2)")
for a, d, A in shakes:
    zt.append(f"0.035*between(t,{a:.3f},{a+d:.3f})")
Z = "+".join(zt)
sx = "+".join(f"{A}*sin(t*71)*between(t,{a:.3f},{a+d:.3f})*(1-(t-{a:.3f})/{d})" for a, d, A in shakes)
sy = "+".join(f"{A}*cos(t*53)*between(t,{a:.3f},{a+d:.3f})*(1-(t-{a:.3f})/{d})" for a, d, A in shakes)

sepia = ".575:.538:.132:0:.244:.780:.118:0:.190:.374:.392"
fg = (
    f"[0:v]scale=w='trunc(1080*({Z})/2)*2':h='trunc(1920*({Z})/2)*2':eval=frame:flags=bicubic,"
    f"crop=1080:1920:'clip((in_w-1080)/2+{sx},0,in_w-1080)':'clip((in_h-1920)/2+{sy},0,in_h-1920)',"
    f"colorchannelmixer={sepia}:enable='between(t,{S[1]:.3f},{S[3]:.3f})',"
    f"hue=s=0:enable='between(t,{FREEZE0},{FREEZE1})',eq=contrast=1.25:enable='between(t,{FREEZE0},{FREEZE1})',"
    f"vignette=angle=PI/5,format=yuv420p[b];"
    f"[1:v]format=rgba[o];[b][o]overlay=0:0:format=auto,noise=alls=4:allf=t,format=yuv420p[v]"
)
open(os.path.join(TMP, "graph.txt"), "w").write(fg)
subprocess.run([
    "ffmpeg", "-v", "error", "-stats", "-y", "-i", BASE, "-framerate", "30", "-i", os.path.join(HERE, "frames/%05d.png"),
    "-i", os.path.join(TMP, "mix.wav"), "-filter_complex_script", os.path.join(TMP, "graph.txt"),
    "-map", "[v]", "-map", "2:a", "-af", "loudnorm=I=-15:TP=-1.5:LRA=11", "-ar", "48000",
    "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "11M", "-bufsize", "22M", "-r", "30", "-c:a", "aac", "-b:a", "192k",
    "-movflags", "+faststart", "-t", f"{DUR}", OUT], check=True)
print("->", OUT)
