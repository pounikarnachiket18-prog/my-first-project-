"""Yawn reel composite: camera moves + whip blur + grade + motion-graphics layer + logo + soundtrack."""
import json, subprocess, os
tl = json.load(open("timeline.json")); ev = json.load(open("events.json"))
s, d, DUR = tl["starts"], tl["durs"], tl["dur"]; N = len(s)
open("concat.txt", "w").write("".join(f"file '{os.path.abspath(f'seg/{i:02d}.mp4')}'\n" for i in range(1, N + 1)))
T = "ld(0)"
def imp(ti, amp, k): return f"{amp}*exp(-({T}-{ti:.3f})*{k})*gte({T},{ti:.3f})"
punch, shake = [], []
FZ = tl["freeze_at"]
punch.append(imp(tl["yawn1"], 0.03, 6)); punch.append(imp(FZ, 0.10, 3.5)); shake.append((FZ, 18))
punch.append(imp(s[1] + 1.9, 0.04, 6))
punch.append(imp(s[2] + 1.2, 0.04, 6))
punch.append(imp(s[4] + 0.55, 0.035, 8)); shake.append((s[4] + 0.55, 12))
punch.append(imp(ev["stamp"], 0.05, 7)); shake.append((ev["stamp"], 16))
punch.append(imp(ev["ice"], 0.03, 6))
punch.append(imp(ev["button"], 0.04, 8)); shake.append((ev["button"], 10))
punch.append(imp(ev["burst"], 0.06, 6)); shake.append((ev["burst"], 18))
punch.append(imp(ev["follow"] + 0.55, 0.03, 8))
push = []
for k in range(N - 1):
    push.append(f"0.06*({T}-{s[k]:.3f})/{d[k]:.3f}*between({T},{s[k]:.3f},{s[k] + d[k]:.3f})")
Z = "1.04+" + "+".join(push + punch)
SX = "+".join(f"{a}*exp(-({T}-{ti:.3f})*10)*sin(({T}-{ti:.3f})*71)*gte({T},{ti:.3f})" for ti, a in shake)
SY = "+".join(f"{a}*exp(-({T}-{ti:.3f})*10)*cos(({T}-{ti:.3f})*59)*gte({T},{ti:.3f})" for ti, a in shake)
pre = "st(0,on/30);"
zp = (f"zoompan=z='{pre}{Z}':x='{pre}clip(iw/2-iw/zoom/2+({SX})*iw/1080,0,iw-iw/zoom)':"
      f"y='{pre}clip(ih/2-ih/zoom/2+({SY})*ih/1920,0,ih-ih/zoom)':d=1:s=1080x1920:fps=30")
cuts = "+".join(f"between(t,{s[k]-0.05:.3f},{s[k]+0.06:.3f})" for k in range(1, N))
fx = (f"[0:v]scale=1350:2400:flags=lanczos,{zp},avgblur=sizeX=24:sizeY=1:enable='{cuts}',"
      f"eq=contrast=1.04:saturation=1.07,vignette=angle=PI/6,unsharp=5:5:0.3,noise=alls=4:allf=t,format=yuv420p[base]")
fc = ";".join([fx, "[1:v]format=rgba[mg]", "[base][mg]overlay=0:0:format=auto[v1]", "[v1][2:v]overlay=860:1700[v2]", "[v2]format=yuv420p[v]",
               "[3:a]loudnorm=I=-15:TP=-1.5:LRA=9[a]"])
open("fc.txt", "w").write(fc)
mg = subprocess.Popen(["node", "render_mg.js"], stdout=subprocess.PIPE)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "concat.txt",
                "-f", "image2pipe", "-framerate", "30", "-c:v", "png", "-i", "-", "-i", "logo_m.png", "-i", "soundtrack.wav",
                "-filter_complex_script", "fc.txt", "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-preset", "medium", "-b:v", "9M", "-maxrate", "13M", "-bufsize", "18M", "-profile:v", "high", "-r", "30",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{DUR:.3f}", "yawn_reel.mp4"], stdin=mg.stdout, check=True)
mg.wait(); print("done")
