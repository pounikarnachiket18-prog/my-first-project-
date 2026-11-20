"""Yawn reel (20 clips): build 1080x1920 segments (watermark removed) + timeline with story-beat times."""
import json, subprocess, glob, os

U = "/root/.claude/uploads/9ca7125a-0452-5229-bcb4-0726d588cfe8"
src = lambda i: glob.glob(f"{U}/{i}-*.mp4")[0]
DELOGO = "delogo=x=569:y=1129:w=62:h=62"
SC = "scale=1080:1920:flags=lanczos,fps=30,format=yuv420p"
os.makedirs("seg", exist_ok=True)
for f in glob.glob("seg/*.mp4"): os.remove(f)
def run(a): subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *a], check=True)
def enc(out): return ["-an", "-c:v", "libx264", "-crf", "15", "-preset", "fast", out]
def dur(p): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))

# clip 1: hook (slow-mo setup -> yawn -> freeze -> turn)
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
hk = {p: dur(f"seg/{p}.mp4") for p in parts}

# clip 2: family at the door (full)
run(["-i", src("a075d47b"), "-vf", f"{DELOGO},{SC}", *enc("seg/02.mp4")])

# clips 3..20: (id, speed, extra hold at end)
CL = [("stage", "80f21f8b", 1.0, 0), ("train", "bcc4d367", 1.15, 0), ("teacher", "9ac90f99", 1.15, 0), ("hero", "24297194", 1.1, 0),
      ("stadium", "8ca8235d", 1.15, 0), ("umpire", "a42120d8", 1.15, 0), ("lab", "75cee86f", 1.15, 0), ("ac", "55e6cc7d", 1.15, 0),
      ("copy", "3c8a9a9d", 1.15, 0), ("office", "97562e28", 1.15, 0), ("dinner", "dfcd49d9", 1.15, 0), ("night", "aaa22ef6", 1.2, 0),
      ("mummy", "ad7e6e5c", 1.15, 0), ("zoom", "ef7d5143", 1.2, 0), ("dog", "d1a5df19", 1.15, 0), ("squish", "ac391af5", 1.1, 0),
      ("callback", "d8d072de", 1.15, 0), ("pass", "978b14c9", 1.0, 3.0)]
speed = {"hook": 1.0, "door": 1.0}
for k, (name, cid, sp, hold) in enumerate(CL, start=3):
    vf = f"{DELOGO},setpts=(PTS-STARTPTS)/{sp},{SC}" + (f",tpad=stop_mode=clone:stop_duration={hold}" if hold else "")
    run(["-ss", "0.3", "-i", src(cid), "-vf", vf, *enc(f"seg/{k:02d}.mp4")])
    speed[name] = sp

names = ["hook", "door"] + [c[0] for c in CL]
N = len(names)
d = [dur(f"seg/{i:02d}.mp4") for i in range(1, N + 1)]
st = [0.0]
for x in d[:-1]: st.append(st[-1] + x)
S = dict(zip(names, st)); Dn = dict(zip(names, d))
def at(name, src_t):             # map a time in the source clip to the reel timeline
    if name == "door": return S[name] + src_t
    return S[name] + (src_t - 0.3) / speed[name]
def frac(name, f): return S[name] + Dn[name] * f

beats = {
    "yawn1": hk["h1a"] + 0.05, "freeze_at": hk["h1a"] + hk["h1b"], "freeze": hk["h1c"],
    "dadi": at("door", 1.9), "title": at("stage", 1.5),
    "ruler": at("teacher", 0.9), "teacher_yawn": at("teacher", 1.6),
    "glasses": at("hero", 1.2), "hero_yawn": at("hero", 1.6),
    "appeal": at("umpire", 0.5), "finger": at("umpire", 1.8), "umpire_yawn": at("umpire", 3.1),
    "stamp": frac("lab", 0.66), "ice": frac("ac", 0.5), "button": frac("copy", 0.42),
    "cook": frac("office", 0.25), "burst": frac("office", 0.72), "stranger": frac("dinner", 0.66),
    "night_yawn": frac("night", 0.55), "oye": at("mummy", 0.5), "mummy_yawn": at("mummy", 1.7), "switch": at("mummy", 3.6),
    "dog_yawn": at("dog", 1.4), "chimps": at("dog", 2.6), "impact": at("squish", 2.3), "couple_yawn": at("callback", 3.0),
    "split": at("pass", 2.6), "follow": S["pass"] + (4.032 - 0.3) + 0.25,
}
tl = {"names": names, "starts": st, "durs": d, "dur": st[-1] + d[-1], "S": S, "beats": beats}
json.dump(tl, open("timeline.json", "w"), indent=1)
print({k: round(v, 2) for k, v in S.items()}, "total", round(tl["dur"], 2))
