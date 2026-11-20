"""Yawn reel: build 1080x1920 segments (watermark removed), hook with slow-mo setup + freeze on the yawn."""
import json, subprocess, glob, os

U = "/root/.claude/uploads/9ca7125a-0452-5229-bcb4-0726d588cfe8"
src = lambda i: glob.glob(f"{U}/{i}-*.mp4")[0]
DELOGO = "delogo=x=569:y=1129:w=62:h=62"
SC = "scale=1080:1920:flags=lanczos,fps=30,format=yuv420p"
os.makedirs("seg", exist_ok=True)

def run(a): subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *a], check=True)
def enc(out): return ["-an", "-c:v", "libx264", "-crf", "15", "-preset", "fast", out]
def dur(p): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))

# ---- Clip 1 (hook): slow-mo setup, the yawn opening, a freeze on the widest yawn, then the turn to the door
h = src("5d3da5a5")
run(["-t", "0.62", "-i", h, "-vf", f"{DELOGO},minterpolate=fps=60:mi_mode=mci,setpts=2.5*PTS,{SC}", *enc("seg/h1a.mp4")])
run(["-ss", "0.62", "-t", "0.28", "-i", h, "-vf", f"{DELOGO},{SC}", *enc("seg/h1b.mp4")])
run(["-ss", "0.90", "-i", h, "-frames:v", "1", "-vf", f"{DELOGO},scale=1080:1920:flags=lanczos", "seg/freeze.png"])
FREEZE = 1.35
run(["-loop", "1", "-framerate", "30", "-t", f"{FREEZE}", "-i", "seg/freeze.png", "-vf", "format=yuv420p", *enc("seg/h1c.mp4")])
run(["-ss", "0.90", "-t", "0.27", "-i", h, "-vf", f"{DELOGO},{SC}", *enc("seg/h1d.mp4")])
parts = ["h1a", "h1b", "h1c", "h1d"]
open("seg/h1.txt", "w").write("".join(f"file '{os.path.abspath('seg/'+p+'.mp4')}'\n" for p in parts))
run(["-f", "concat", "-safe", "0", "-i", "seg/h1.txt", "-c", "copy", "seg/01.mp4"])
hook = {p: dur(f"seg/{p}.mp4") for p in parts}

# ---- Clip 2 (family at the door): full length
run(["-i", src("a075d47b"), "-vf", f"{DELOGO},{SC}", *enc("seg/02.mp4")])

# ---- Clips 3..13
rest = [("80f21f8b", 1.0), ("bcc4d367", 1.1), ("9ac90f99", 1.1), ("8ca8235d", 1.1), ("75cee86f", 1.1), ("55e6cc7d", 1.1),
        ("3c8a9a9d", 1.1), ("97562e28", 1.1), ("dfcd49d9", 1.1), ("aaa22ef6", 1.1), ("ef7d5143", 1.1)]
for k, (cid, sp) in enumerate(rest, start=3):
    run(["-ss", "0.3", "-i", src(cid), "-vf", f"{DELOGO},setpts=(PTS-STARTPTS)/{sp},{SC}", *enc(f"seg/{k:02d}.mp4")])

# ---- end card base (14): dark lavender gradient, the motion graphics draw everything on top
END = 3.6
run(["-f", "lavfi", "-i", f"gradients=s=1080x1920:c0=0x2a1b3d:c1=0x5b3f7a:x0=540:y0=0:x1=540:y1=1920:d={END}:r=30,format=yuv420p",
     "-t", f"{END}", *enc("seg/14.mp4")])

N = 14
d = [dur(f"seg/{i:02d}.mp4") for i in range(1, N + 1)]
st = [0.0]
for x in d[:-1]: st.append(st[-1] + x)
tl = {"starts": st, "durs": d, "dur": st[-1] + d[-1], "freeze_at": hook["h1a"] + hook["h1b"], "freeze": hook["h1c"],
      "yawn1": hook["h1a"] + 0.05}
json.dump(tl, open("timeline.json", "w"), indent=1)
print([round(x, 2) for x in st], round(tl["dur"], 2), "freeze at", round(tl["freeze_at"], 2))
