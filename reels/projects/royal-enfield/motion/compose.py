"""Final composite: concat segments -> camera moves (push-in, zoom punches, shake) -> whip blur on cuts ->
grade + grain -> motion-graphics layer (piped PNG frames) -> logo -> soundtrack + ducked voiceover."""
import json, subprocess, os

tl = json.load(open("timeline2.json")); bt = json.load(open("beats.json"))
s, d, DUR = tl["starts"], tl["durs"], tl["dur"]
N = len(s)
open("concat2.txt", "w").write("".join(f"file '{os.path.abspath(f'seg2/{i:02d}.mp4')}'\n" for i in range(1, N + 1)))

T = "ld(0)"
def imp(ti, amp, k):            # decaying impulse starting at ti
    return f"{amp}*exp(-({T}-{ti:.3f})*{k})*gte({T},{ti:.3f})"

punch, shake = [], []
for p in bt["patakas"]:
    punch.append(imp(p, 0.025, 9)); shake.append((p, 9))
FZ = tl["freeze_at"]
punch.append(imp(FZ, 0.12, 4)); shake.append((FZ, 24))
clang = s[2] + (s[3] - s[2]) * 0.42
punch.append(imp(clang, 0.02, 8)); shake.append((clang, 10))
punch.append(imp(s[3] + 0.05, 0.05, 6))
for b in bt["beats"]:
    if s[3] + 0.5 < b < s[8]: punch.append(imp(b, 0.012, 14))
K = bt["kick"] + 0.3
punch.append(imp(K, 0.08, 5)); shake.append((K, 20))
punch.append(imp(s[11] + 1.5, 0.03, 8)); shake.append((s[11] + 1.5, 8))
punch.append(imp(bt["follow"] + 0.55, 0.03, 8))
push = [f"0.05*({T}-{s[k]:.3f})/{d[k]:.3f}*between({T},{s[k]:.3f},{s[k] + d[k]:.3f})" for k in range(N)]
Z = "1.04+" + "+".join(push + punch)
SX = "+".join(f"{a}*exp(-({T}-{ti:.3f})*10)*sin(({T}-{ti:.3f})*71)*gte({T},{ti:.3f})" for ti, a in shake)
SY = "+".join(f"{a}*exp(-({T}-{ti:.3f})*10)*cos(({T}-{ti:.3f})*59)*gte({T},{ti:.3f})" for ti, a in shake)
pre = "st(0,on/30);"
zp = (f"zoompan=z='{pre}{Z}':x='{pre}clip(iw/2-iw/zoom/2+({SX})*iw/1080,0,iw-iw/zoom)':"
      f"y='{pre}clip(ih/2-ih/zoom/2+({SY})*ih/1920,0,ih-ih/zoom)':d=1:s=1080x1920:fps=30")
cuts = "+".join(f"between(t,{s[k]-0.05:.3f},{s[k]+0.06:.3f})" for k in range(1, N))
fx = (f"[0:v]scale=1350:2400:flags=lanczos,{zp},avgblur=sizeX=26:sizeY=1:enable='{cuts}',"
      f"eq=contrast=1.05:saturation=1.06,vignette=angle=PI/5,unsharp=5:5:0.35,noise=alls=6:allf=t,format=yuv420p[base]")
fc = ";".join([
    fx,
    "[1:v]format=rgba[mg]",
    "[base][mg]overlay=0:0:format=auto[v1]",
    "[v1][2:v]overlay=860:1700[v2]",
    "[v2]format=yuv420p[v]",
    "[4:a]adelay=2400|2400,aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-1.5:LRA=7,asplit=2[vo][sc]",
    "[3:a]volume=0.6[bed]",
    "[bed][sc]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=350[duck]",
    "[duck][vo]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]",
])
open("fc.txt", "w").write(fc)
mg = subprocess.Popen(["node", "render_mg.js"], stdout=subprocess.PIPE)
cmd = ["ffmpeg", "-v", "error", "-y",
       "-f", "concat", "-safe", "0", "-i", "concat2.txt",
       "-f", "image2pipe", "-framerate", "30", "-c:v", "png", "-i", "-",
       "-i", "logo_m.png", "-i", "soundtrack2.wav", "-i", "vo_fit.wav",
       "-filter_complex_script", "fc.txt", "-map", "[v]", "-map", "[a]",
       "-c:v", "libx264", "-preset", "medium", "-b:v", "9M", "-maxrate", "13M", "-bufsize", "18M", "-profile:v", "high", "-r", "30",
       "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{DUR:.3f}", "royal_enfield_mg.mp4"]
subprocess.run(cmd, stdin=mg.stdout, check=True)
mg.wait()
print("done")
