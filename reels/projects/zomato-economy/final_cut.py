#!/usr/bin/env python3
"""Final cut: the user's meme hook first, then the reel sped up to 65 s.

The hook ends in a blackout (the ball hits the chandelier, lights go out).
The reel opens on a dark background, so it fades up out of that blackout with
a short light flicker and a "power coming back on" sound, instead of a hard
cut. The hook's letterbox bars are replaced by a blurred, darkened fill.

  python3 final_cut.py   ->  ../../output/zomato-economy-final.mp4
(needs build/video1080.mp4 and build/mix.wav from `build.py --hd` / `audio.py`)
"""
import json, os, subprocess
import numpy as np
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "output", "zomato-economy-final.mp4"))
HOOK = os.path.join(HERE, "media", "intro_hook.mp4")
REEL_V, REEL_A = os.path.join(BUILD, "video1080.mp4"), os.path.join(BUILD, "mix.wav")
REEL_LEN, TARGET = 80.3, 65.0
SPEED = REEL_LEN / TARGET          # whole reel sped up, nothing cut (pitch kept)
XF_AT, XF = 2.90, 0.35             # crossfade starts in the hook's blackout
HOOK_CROP = "720:636:0:322"        # picture area inside the hook's black bars
SR = 48000


def run(cmd):
    subprocess.run(cmd, check=True)


def power_on():
    """Electrical flicker: a rising mains hum, two relay clicks, a soft thump."""
    n = int(0.7 * SR); t = np.arange(n) / SR
    hum = sum(np.sin(2 * np.pi * 50 * k * t) / k for k in (1, 2, 3, 4, 6))
    env = np.clip(t / 0.45, 0, 1) ** 2 * np.clip((0.7 - t) / 0.2, 0, 1)
    x = hum * env * 0.25
    rng = np.random.default_rng(3)
    for c in (0.10, 0.17, 0.28):
        i = int(c * SR); m = int(0.012 * SR)
        x[i:i + m] += rng.standard_normal(m) * np.exp(-np.arange(m) / (0.002 * SR)) * 0.6
    th = np.sin(2 * np.pi * 70 * t) * np.exp(-np.clip(t - 0.30, 0, None) * 18) * (t >= 0.30) * 0.5
    x = np.tanh((x + th) * 1.5) * 0.7
    return np.stack([x, x], 1)


def main():
    # ---- audio: hook (lifted to reel level) + reel sped up + power-on, then -14 LUFS
    pw = os.path.join(BUILD, "power_on.wav")
    wavfile.write(pw, SR, (power_on() * 32767).astype(np.int16))
    raw = os.path.join(BUILD, "final_mix_raw.wav")
    d_ms = int(XF_AT * 1000)
    run(["ffmpeg", "-v", "error", "-y", "-i", HOOK, "-i", REEL_A, "-i", pw, "-filter_complex",
         f"[0:a]aresample={SR},volume=7.5dB,afade=t=out:st={XF_AT + 0.05}:d=0.35[h];"
         f"[1:a]rubberband=tempo={SPEED:.6f}:pitch=1:formant=preserved:transients=crisp,"
         f"adelay={d_ms}|{d_ms}[r];"
         f"[2:a]adelay={d_ms - 120}|{d_ms - 120},volume=0.8[p];"
         f"[h][r][p]amix=inputs=3:normalize=0:duration=longest", "-ar", str(SR), raw])
    meas = subprocess.run(["ffmpeg", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.2:LRA=9:print_format=json",
                           "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
    mix = os.path.join(BUILD, "final_mix.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af",
         f"loudnorm=I=-14:TP=-1.2:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
         f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true",
         "-ar", str(SR), mix])

    # ---- picture: blurred-fill hook -> fade up (with a flicker) into the sped-up reel
    total = XF_AT + TARGET
    vf = (
        f"[0:v]crop={HOOK_CROP},split[a][b];"
        "[a]scale=-2:1920,crop=1080:1920,boxblur=28:2,eq=brightness=-0.10:saturation=0.85[bg];"
        "[b]scale=1080:-2:flags=lanczos,cas=0.35[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2-60,fps=30,format=yuv420p,setsar=1,settb=AVTB[hook];"
        f"[1:v]setpts=PTS/{SPEED:.6f},fps=30,"
        "eq=brightness='if(between(t,0.10,0.17),-0.22,if(between(t,0.24,0.28),-0.12,0))':eval=frame,"
        "format=yuv420p,setsar=1,settb=AVTB[reel];"
        f"[hook][reel]xfade=transition=fade:duration={XF}:offset={XF_AT}[v]"
    )
    run(["ffmpeg", "-v", "error", "-y", "-i", HOOK, "-i", REEL_V, "-i", mix, "-filter_complex", vf,
         "-map", "[v]", "-map", "2:a", "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "19",
         "-maxrate", "16M", "-bufsize", "32M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
         "-movflags", "+faststart", OUT])
    print("final ->", OUT, f"({total:.2f}s)")


if __name__ == "__main__":
    main()
