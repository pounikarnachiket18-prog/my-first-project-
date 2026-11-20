"""Yawn reel composite (20 clips): camera moves + whip blur + grade + graphics + logo + soundtrack."""
import json, subprocess, os
tl = json.load(open("timeline.json")); ev = json.load(open("events.json"))
s, d, DUR, S, B = tl["starts"], tl["durs"], tl["dur"], tl["S"], tl["beats"]; N = len(s)
open("concat.txt", "w").write("".join(f"file '{os.path.abspath(f'seg/{i:02d}.mp4')}'\n" for i in range(1, N + 1)))
T = "ld(0)"
def imp(ti, amp, k): return f"{amp}*exp(-({T}-{ti:.3f})*{k})*gte({T},{ti:.3f})"
punch, shake = [], []
def hit(t, p, sh=0, k=7): punch.append(imp(t, p, k)); (shake.append((t, sh)) if sh else None)
hit(B["yawn1"], .03, 0, 6); hit(B["freeze_at"], .10, 18, 3.5); hit(B["dadi"], .04)
hit(B["title"], .06, 14, 5); hit(B["ruler"], .035, 12, 8); hit(B["teacher_yawn"], .03)
hit(B["glasses"], .03, 0, 4); hit(B["hero_yawn"], .05, 10, 6)
hit(B["appeal"], .03, 8); hit(B["umpire_yawn"], .05, 12, 6)
hit(B["stamp"], .05, 16); hit(B["ice"], .03, 0, 6); hit(B["button"], .04, 10, 8); hit(B["burst"], .06, 18, 6)
hit(B["oye"], .04, 12, 8); hit(B["mummy_yawn"], .03)
hit(B["dog_yawn"], .03); hit(B["impact"], .09, 26, 5); hit(B["couple_yawn"], .04)
hit(B["split"] + .9, .06, 14, 4); hit(B["follow"] + .55, .03, 0, 8)
push = [f"0.06*({T}-{s[k]:.3f})/{d[k]:.3f}*between({T},{s[k]:.3f},{s[k] + d[k]:.3f})" for k in range(N)]
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
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{DUR:.3f}", "yawn_reel_full.mp4"], stdin=mg.stdout, check=True)
mg.wait(); print("done")
