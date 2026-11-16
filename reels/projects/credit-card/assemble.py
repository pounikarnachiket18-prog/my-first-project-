import json, subprocess
tl = json.load(open("timeline.json"))
starts, DUR = tl["starts"], tl["dur"]
N = 19
ends = starts[1:] + [DUR]

inputs = []
for i in range(1, N + 1):
    inputs += ["-i", f"seg/{i:02d}.mp4"]
ov = [f"ov/cap{i:02d}.png" for i in range(1, N + 1)] + ["ov/title.png", "ov/logo.png", "ov/disc.png", "ov/banner.png"]
for p in ov:
    inputs += ["-loop", "1", "-framerate", "30", "-t", f"{DUR:.3f}", "-i", p]
inputs += ["-i", "soundtrack.wav"]

f = []
segs = "".join(f"[{i}:v]" for i in range(N - 1))
f.append(f"[{N-1}:v]tpad=stop_mode=clone:stop_duration=1.8[last]")
f.append(f"{segs}[last]concat=n={N}:v=1:a=0,setsar=1[base0]")
cur = "base0"
k = 0
def over(idx, a, b, label):
    global cur
    f.append(f"[{cur}][{idx}:v]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[{label}]")
    cur = label
for i in range(N):
    a = starts[i] + (0.15 if i else 0.05)
    b = ends[i] - 0.04
    over(N + i, a, b, f"c{i}")
over(N + N, 0.0, starts[1] - 0.04, "tt")          # title on the opener
over(N + N + 1, 0.0, DUR, "lg")                   # logo covers the generator watermark
over(N + N + 2, starts[17] + 0.15, ends[17] - 0.04, "ds")   # disclaimer on tips clip
over(N + N + 3, starts[18] + 2.2, DUR, "bn")      # follow banner on the outro
f.append(f"[{cur}]format=yuv420p[v]")

cmd = ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(f),
       "-map", "[v]", "-map", f"{N+len(ov)}:a", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
       "-profile:v", "high", "-r", "30", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
       "-t", f"{DUR:.3f}", "credit_card_reel.mp4"]
subprocess.run(cmd, check=True)
print("done")
