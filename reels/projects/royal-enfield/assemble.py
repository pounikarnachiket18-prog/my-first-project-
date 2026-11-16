import json, subprocess
tl = json.load(open("timeline.json"))
starts, DUR, END = tl["starts"], tl["dur"], tl["end"]
N = 15
ends = starts[1:] + [DUR]

inputs = []
for i in range(1, N + 1):
    inputs += ["-i", f"seg/{i:02d}.mp4"]
ov = [f"ov/cap{i:02d}.png" for i in range(1, N + 1)] + ["ov/title.png", "ov/logo.png", "ov/disc.png", "ov/banner.png"]
for p in ov:
    inputs += ["-loop", "1", "-framerate", "30", "-t", f"{DUR:.3f}", "-i", p]
inputs += ["-i", "soundtrack.wav"]

f = [f"[{N-1}:v]tpad=stop_mode=clone:stop_duration=1.8[last]",
     "".join(f"[{i}:v]" for i in range(N - 1)) + f"[last]concat=n={N}:v=1:a=0,setsar=1[b0]"]
cur = "b0"
def over(idx, a, b, label):
    global cur
    f.append(f"[{cur}][{idx}:v]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[{label}]")
    cur = label

over(N + 0, 0.05, 2.38, "c0")                 # "Gali ka asli DON"
over(N + N + 2, 0.05, 2.38, "ds")             # silencer joke
over(N + N, 2.42, 3.85, "tt")                 # freeze frame: RUKO... British thi
for i in range(1, N):
    over(N + i, starts[i] + 0.15, ends[i] - 0.04, f"c{i}")
over(N + N + 1, 0.0, DUR, "lg")               # logo covers generator watermark
over(N + N + 3, starts[14] + 1.8, DUR, "bn")  # follow banner
f.append(f"[{cur}]format=yuv420p[v]")

subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(f),
                "-map", "[v]", "-map", f"{N+len(ov)}:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                "-r", "30", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                "-t", f"{DUR:.3f}", "royal_enfield_reel.mp4"], check=True)
print("done")
