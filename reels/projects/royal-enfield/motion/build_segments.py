"""Retime every clip to its voiceover line and build 1080x1920 segments (watermark removed)."""
import json, subprocess, glob, os

U = "/root/.claude/uploads/9ca7125a-0452-5229-bcb4-0726d588cfe8"
VO0 = 2.4                       # voiceover starts on the freeze frame
TAIL = 2.4                      # hold after the last line for the follow-button animation
vo = json.load(open("vo_lines.json"))
seg = vo["seg"]
order = ["de47c5d4", "90a5527e", "03b3356b", "29bf4cb5", "fd1fbd12", "cc864d2c", "90a7eae8",
         "ad66de14", "9a9650ac", "06a8e1ad", "70a4db48", "278d0ea2", "b8b38520", "74b8f4ea", "4f54f9f2"]
grade = {8: "fade", 9: "fade", 11: "pop", 12: "pop", 13: "pop", 14: "pop"}
N = len(order)
starts = [0.0] + [VO0 + seg[k][0] for k in range(1, N)]
end = VO0 + vo["vo_total"] + TAIL
durs = [starts[k + 1] - starts[k] for k in range(N - 1)] + [end - starts[-1]]
FREEZE_AT = 2.4
TAIL1 = 4.032 - FREEZE_AT
freeze = durs[0] - FREEZE_AT - TAIL1

src = lambda i: glob.glob(f"{U}/{i}-*.mp4")[0]
DELOGO = "delogo=x=569:y=1129:w=62:h=62"
SC = "scale=1080:1920:flags=lanczos,fps=30,format=yuv420p"
G = {"fade": ",eq=saturation=0.55:contrast=0.95:brightness=-0.02", "pop": ",eq=saturation=1.18:contrast=1.04", None: ""}
os.makedirs("seg2", exist_ok=True)

def run(args):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *args], check=True)

# Hook 1: play to the freeze point, hold a frozen frame, then play the tail
h = src(order[0])
run(["-t", f"{FREEZE_AT}", "-i", h, "-an", "-vf", f"{DELOGO},{SC}", "-c:v", "libx264", "-crf", "15", "-preset", "fast", "seg2/h1a.mp4"])
run(["-ss", f"{FREEZE_AT}", "-i", h, "-frames:v", "1", "-vf", f"{DELOGO},scale=1080:1920:flags=lanczos", "seg2/freeze.png"])
run(["-loop", "1", "-framerate", "30", "-t", f"{freeze:.3f}", "-i", "seg2/freeze.png", "-vf", "eq=saturation=0.7:contrast=1.1,format=yuv420p",
     "-c:v", "libx264", "-crf", "15", "-preset", "fast", "seg2/h1b.mp4"])
run(["-ss", f"{FREEZE_AT}", "-i", h, "-an", "-vf", f"{DELOGO},{SC}", "-c:v", "libx264", "-crf", "15", "-preset", "fast", "seg2/h1c.mp4"])
open("seg2/h1.txt", "w").write("".join(f"file '{os.path.abspath('seg2/'+p)}'\n" for p in ("h1a.mp4", "h1b.mp4", "h1c.mp4")))
run(["-f", "concat", "-safe", "0", "-i", "seg2/h1.txt", "-c", "copy", "seg2/01.mp4"])

AV = 4.032 - 0.3                 # usable source length after trimming the repeated first frames
for k in range(1, N):
    tgt = durs[k]
    s = max(0.62, min(1.25, tgt / AV))           # setpts factor: <1 speeds up, >1 slows down
    hold = max(0.0, tgt - AV * s) + 0.1
    vf = f"{DELOGO},setpts=(PTS-STARTPTS)*{s:.4f},{SC}{G[grade.get(k)]},tpad=stop_mode=clone:stop_duration={hold:.3f}"
    run(["-ss", "0.3", "-i", src(order[k]), "-an", "-vf", vf, "-t", f"{tgt:.3f}", "-c:v", "libx264", "-crf", "15", "-preset", "fast", f"seg2/{k+1:02d}.mp4"])
    print(k + 1, order[k], f"target {tgt:.2f}s  speed x{1/s:.2f}  hold {hold-0.1:.2f}s")

line_starts = [VO0 + a for a, b in seg]
line_ends = [VO0 + b for a, b in seg]
json.dump({"starts": starts, "durs": durs, "end": end, "dur": end, "freeze_at": FREEZE_AT, "freeze": freeze,
           "line_starts": line_starts, "line_ends": line_ends, "vo0": VO0}, open("timeline2.json", "w"), indent=1)
print("total", round(end, 2), "freeze", round(freeze, 2))
