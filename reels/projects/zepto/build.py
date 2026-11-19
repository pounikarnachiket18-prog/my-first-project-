#!/usr/bin/env python3
"""
Zepto reel ("4 Jebein", Kodak papercraft style): assembles the 20 Google Flow clips.

  python3 build.py                      # full reel  -> ../../output/zepto-reel.mp4
  python3 build.py --preview            # contact sheet -> ../../output/zepto-reel-contact.jpg
  python3 build.py --vo voiceover.mp3   # add the Devika voiceover; clip audio ducks under it

What it does:
  * puts the clips in story order (CLIPS below), upscales to 1080x1920 @ 30 fps
  * joins them: a 1-frame cut where the frames already match (chained clips), a short
    dissolve where the framing jumps (older, unchained clips)
  * burns in Hinglish captions (white, *yellow* and ~red~ keywords, black outline), the hook
    title, the Follow card, and the red M badge over the Flow mark
  * keeps Veo's own sound effects, cross-faded at every join, loudness-normalised to -14 LUFS
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))           # reels/
OUT = os.path.join(ROOT, "output")
BUILD = os.path.join(HERE, "build")
UP = "/root/.claude/uploads/5a555800-107d-5555-b24c-10c07abace7e"
W, H, FPS = 1080, 1920, 30
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FONT_SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
LOGO = os.path.join(ROOT, "assets", "mindset-mode-logo-80.png")
YELLOW, RED, WHITE = (255, 212, 59), (255, 72, 72), (255, 255, 255)
CUT, DIS = 1 / FPS, 0.22                                 # join types (seconds of overlap)

# (label, source file, join INTO this clip from the previous one, captions)
# caption = (start fraction, end fraction, text, y-centre); *word* = yellow, ~word~ = red
CLIPS = [
    ("hook",       "b734d0ac-771940358_1795116909552955", None, []),      # first clip: no text at all
    ("promise",    "0db13558-9470849_1795116908144005", DIS, [
        (0.00, 1.00, "Kaise? *End mein* bataunga… Zepto *asal mein* kya bechta hai", 1360)]),
    ("rise",       "cfb5f02f-387929739_1795116906777838", DIS, [
        (0.00, 1.00, "*2021.* Do *19 saal* ke Stanford dropouts", 1360)]),
    ("N1 fail",    "1db613eb-231502608_1795118526316863", CUT, [
        (0.00, 1.00, "Pehla startup: *KiranaKart*… ~FAIL~", 1360)]),
    ("N2 funding", "0f3b5031-723486032_1795118524781925", CUT, [
        (0.00, 1.00, "Phir bhi haar nahi maani… *$60 million* funding (2021)", 1360)]),
    ("shop",       "0f0d9749-239524509_1795116905390086", DIS, [
        (0.00, 1.00, "Raaz: *DARK STORE*… jismein aap ghus nahi sakte", 1360)]),
    ("map",        "fed4280a-796862173_1795116903804963", DIS, [
        (0.00, 1.00, "India mein *1,100+* dark stores", 1360)]),
    ("N3 kirana",  "802e08be-695772254_1795118522884158", CUT, [
        (0.00, 1.00, "Kirana: ~line, intezaar~ · Dark store: *sirf picking*", 1360)]),
    ("stopwatch",  "3c837718-703922780_1795116902219156", DIS, [
        (0.00, 1.00, "Order aaya → *stopwatch on* → bag band", 1360)]),
    ("rider",      "89b3b9f3-302227672_1795116900694348", DIS, [
        (0.00, 1.00, "Rider? *Pehle se gate pe* ready", 1360)]),
    ("jeb1",       "a4516bfa-320406275_1795116940802940", DIS, [
        (0.00, 0.45, "Zepto ki *4 JEBEIN*", 1360),
        (0.45, 1.00, "*Jeb #1:* har product pe margin", 1360)]),
    ("jeb2",       "524fddad-717354845_1795116939568583", DIS, [
        (0.00, 1.00, "*Jeb #2:* handling + delivery + ~small cart fee~", 1360)]),
    ("jeb3+4",     "f73a9f82-724014891_1795116938295663", DIS, [
        (0.00, 0.62, "*Jeb #3:* jo sabse upar dikhe… ~usne paise diye~", 1360),
        (0.62, 1.00, "*Jeb #4:* Zepto Pass", 1360)]),
    ("N4 kharche", "c8016b1f-980878916_1795118521227697", CUT, [
        (0.00, 1.00, "Par kharche: rider, rent, discount, ads… ~paisa jaata hai~", 1360)]),
    ("race",       "608088a1-442585578_1795116936847030", DIS, [
        (0.00, 1.00, "4 jebein bhari… phir bhi ~KHAALI?~ Blinkit, Instamart se *race*", 1360)]),
    ("proof",      "6a408ba9-54435359_1795116935403400", DIS, [
        (0.00, 1.00, "FY25: sales *₹9,669 Cr* · loss ~₹3,367 Cr~ ~▲177%~", 1165)]),
    ("aadat",      "e9cfd376-366271477_1795116933985262", DIS, [
        (0.00, 0.45, "Asli product? Grocery nahi…", 1360),
        (0.45, 1.00, "*AADAT*", 1360)]),
    ("N5 tips",    "067a4f12-1020945089_1795118519239902", CUT, [
        (0.00, 0.34, "Tip 1: checkout pe *har fee dekho*", 1360),
        (0.34, 0.67, "Tip 2: sabse upar wala… *compare karo*", 1360),
        (0.67, 1.00, "Tip 3: Pass tabhi, *jab hafte mein 2-3 order*", 1360)]),
    ("N6 profit",  "628a79eb-315997369_1795118517470785", CUT, [
        (0.00, 1.00, "Zepto kabhi *PROFIT* karega? Comment: *HAAN* ya ~NAA~", 1360)]),
    ("N7 cta",     "602035bf-835875456_1795118515416488", CUT, [
        (0.00, 1.00, "Bhejo us dost ko jo *1 Maggi* ke liye bhi Zepto karta hai", 1470)]),
]


def probe(path):
    """Duration of the VIDEO stream (the container/audio can be a few ms longer)."""
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration",
                          "-of", "json", path], capture_output=True, text=True, check=True).stdout
    return float(json.loads(out)["streams"][0]["duration"])


def parse(text):
    """'a *b* ~c~' -> [(word, colour), ...]"""
    words = []
    colour = WHITE
    for raw in text.split(" "):
        w = raw
        if w.startswith("*"):
            colour, w = YELLOW, w[1:]
        elif w.startswith("~"):
            colour, w = RED, w[1:]
        end = w.endswith("*") or w.endswith("~")
        # closing marker may be followed by punctuation, e.g. *crore*?
        for mk in "*~":
            if mk in w:
                end, w = True, w.replace(mk, "")
        words.append((w, colour))
        if end:
            colour = WHITE
    return words


def caption_png(text, y, path, size=66, max_w=940):
    font = ImageFont.truetype(FONT, size)
    words = parse(text)
    space = font.getlength(" ")
    lines, cur, cur_w = [], [], 0
    for w, c in words:
        ww = font.getlength(w)
        if cur and cur_w + space + ww > max_w:
            lines.append((cur, cur_w))
            cur, cur_w = [], 0
        cur_w = cur_w + (space if cur else 0) + ww
        cur.append((w, c, ww))
    lines.append((cur, cur_w))
    lh = int(size * 1.18)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    top = y - (lh * len(lines)) // 2
    for i, (line, lw) in enumerate(lines):
        x = (W - lw) / 2
        for w, c, ww in line:
            d.text((x + 3, top + i * lh + 5), w, font=font, fill=(0, 0, 0, 150))       # soft drop shadow
            d.text((x, top + i * lh), w, font=font, fill=c, stroke_width=7, stroke_fill=(0, 0, 0, 255))
            x += ww + space
    img.save(path)


def title_png(path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    big = ImageFont.truetype(FONT, 150)
    small = ImageFont.truetype(FONT, 76)
    for txt, f, y, c in (("ZEPTO", big, 190, YELLOW), ("10 min delivery…", small, 365, WHITE),
                         ("phir bhi LOSS?", small, 455, RED)):
        x = (W - f.getlength(txt)) / 2
        d.text((x + 4, y + 6), txt, font=f, fill=(0, 0, 0, 150))
        d.text((x, y), txt, font=f, fill=c, stroke_width=9, stroke_fill=(0, 0, 0, 255))
    img.save(path)


def follow_png(path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    box = (190, 1130, 890, 1330)
    d.rounded_rectangle((box[0] + 6, box[1] + 10, box[2] + 6, box[3] + 10), 36, fill=(0, 0, 0, 90))
    d.rounded_rectangle(box, 36, fill=(250, 244, 228, 245), outline=(60, 40, 20, 255), width=4)
    f1, f2 = ImageFont.truetype(FONT, 58), ImageFont.truetype(FONT_SEMI, 36)
    for txt, f, y, c in (("Follow", f2, 1158, (80, 60, 40)), ("@mindset_mode_co", f1, 1205, (40, 20, 70)),
                         ("for more money secrets", f2, 1278, (80, 60, 40))):
        d.text(((W - f.getlength(txt)) / 2, y), txt, font=f, fill=c)
    img.save(path)


def badge_png(path, size=104):
    logo = Image.open(LOGO).convert("RGBA").resize((size, size), Image.LANCZOS)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.alpha_composite(logo, (900 - size // 2, 1736 - size // 2))     # centred on the Flow mark
    img.save(path)


def timeline():
    """Start time of every clip in the joined video, and total length."""
    starts, acc = [], 0.0
    for i, (_, src, join, _) in enumerate(CLIPS):
        dur = probe(f"{UP}/{src}.mp4")
        start = 0.0 if i == 0 else acc - join
        starts.append((start, dur))
        acc = start + dur
    return starts, acc


# ---------------------------------------------------------------- voiceover sync
VO_LINES = os.path.join(HERE, "audio", "vo_lines.json")   # line start times in the 1.5x voiceover
VO_LEAD = 0.0         # keep the voiceover from its very first sample (only sped up 1.5x)
TAIL = 1.3            # seconds of picture after the last word
F_MIN, F_MAX = 0.75, 1.5   # clip speed limits: 0.75 = 1.33x faster, 1.5 = slow-motion (24 -> 30 fps)
HOLD_AT = {"N2 funding": 0.45, "N3 kirana": 0.5, "proof": 0.5, "N5 tips": 0.72}   # where a long line pauses


def vo_timeline():
    """Clip start times that follow the voiceover lines (one line per clip)."""
    with open(VO_LINES) as f:
        j = json.load(f)
    vs = j["starts"]
    starts = [0.0] + [t - VO_LEAD - 0.1 for t in vs[1:]]
    total = j["end"] - VO_LEAD + TAIL
    segs = []
    for i in range(len(CLIPS)):
        nxt_join = CLIPS[i + 1][2] if i + 1 < len(CLIPS) else 0
        end = starts[i + 1] + nxt_join if i + 1 < len(CLIPS) else total
        segs.append((starts[i], end - starts[i]))
    return segs, total


def make_segment(i, length, path):
    """Fit clip i to `length` seconds: speed change within limits, then trim or a gentle Ken Burns hold."""
    label, src, _, _ = CLIPS[i]
    inp = f"{UP}/{src}.mp4"
    L = probe(inp)
    f = min(max(length / L, F_MIN), F_MAX)
    played = L * f
    hold = max(0.0, length - played)
    norm = f"scale={W}:{H}:flags=lanczos,fps={FPS},format=yuv420p,setsar=1"
    tempo = max(0.5, min(2.0, 1 / f))
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", inp]
    if hold > 0.05:
        h = HOLD_AT.get(label, 0.6) * L
        still = os.path.join(BUILD, f"hold{i:02d}.png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{h:.3f}", "-i", inp, "-frames:v", "1", still], check=True)
        nk = max(2, round(hold * FPS))
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{hold:.3f}", "-i", still]
        g = (f"[0:v]trim=0:{h:.3f},setpts=(PTS-STARTPTS)*{f:.4f},{norm}[A];"
             f"[0:v]trim={h:.3f},setpts=(PTS-STARTPTS)*{f:.4f},{norm}[B];"
             f"[1:v]scale={2 * W}:{2 * H}:flags=lanczos,zoompan=z='1+0.05*sin(PI*on/{nk})':"
             f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},format=yuv420p,setsar=1[K];"
             f"[A][K][B]concat=n=3:v=1:a=0,trim=0:{length:.4f},setpts=PTS-STARTPTS[v];")
    else:
        g = f"[0:v]setpts=PTS*{f:.4f},{norm},trim=0:{length:.4f},setpts=PTS-STARTPTS[v];"
    g += (f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,atempo={tempo:.4f},"
          f"apad,atrim=0:{length:.4f},asetpts=PTS-STARTPTS[a]")
    cmd += ["-filter_complex", g, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "fast", "-crf", "14",
            "-c:a", "pcm_s16le", "-t", f"{length:.4f}", path]
    subprocess.run(cmd, check=True)
    note = f"speed x{1 / f:.2f}" + (f", hold {hold:.1f}s" if hold > 0.05 else "") + \
           (f", trimmed {played - length:.1f}s" if played - length > 0.05 else "")
    print(f"  seg {i + 1:2d} {label:<11} {length:5.2f}s  ({note})")


def build(out, vo=None, preview=False, base=False):
    """base=True: clips + audio only (no burned-in text); writes build/timeline.json for motion/."""
    os.makedirs(BUILD, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    if vo:
        starts, total = vo_timeline()
        srcs = []
        for i, (_, length) in enumerate(starts):
            p = os.path.join(BUILD, f"seg_{CLIPS[i][1][:8]}_{length:.3f}.mkv")
            if not os.path.exists(p):
                make_segment(i, length, p)
            srcs.append(p)
    else:
        starts, total = timeline()
        srcs = [f"{UP}/{src}.mp4" for _, src, _, _ in CLIPS]

    if base:
        tl = {"total": total, "fps": FPS, "clips": []}
        for i, (label, src, join, caps) in enumerate(CLIPS):
            s, d = starts[i]
            nxt = starts[i + 1][0] if i + 1 < len(CLIPS) else total
            tl["clips"].append({"label": label, "start": s, "end": nxt, "join": "cut" if join == CUT else
                                ("dissolve" if join else None), "captions": [list(c) for c in caps]})
        with open(os.path.join(BUILD, "timeline.json"), "w") as f:
            json.dump(tl, f, indent=1, ensure_ascii=False)

    # ---- overlay images
    overlays = []                                                    # (png, t0, t1)
    # no title or caption on the first clip
    for i, (label, _, _, caps) in enumerate(CLIPS):
        s, dur = starts[i]
        nxt = starts[i + 1][0] if i + 1 < len(CLIPS) else total
        span = nxt - s
        for k, (a, b, text, y) in enumerate(caps):
            p = os.path.join(BUILD, f"cap{i:02d}_{k}.png")
            caption_png(text, y, p)
            overlays.append((p, s + a * span + (0.12 if a == 0 else 0), s + b * span - 0.04))
    s_last = starts[-1][0]
    follow = os.path.join(BUILD, "follow.png"); follow_png(follow); overlays.append((follow, s_last + 0.4, total))
    badge = os.path.join(BUILD, "badge.png"); badge_png(badge); overlays.append((badge, 0.0, total))
    if base:
        overlays = []

    # ---- ffmpeg graph
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for s in srcs:
        cmd += ["-i", s]
    n = len(CLIPS)
    for png, _, _ in overlays:
        cmd += ["-i", png]
    if vo:
        cmd += ["-ss", f"{VO_LEAD:.3f}", "-i", vo]
    g = []
    for i in range(n):
        vd = starts[i][1]
        g.append(f"[{i}:v]scale={W}:{H}:flags=lanczos,fps={FPS},format=yuv420p,setsar=1,settb=AVTB[v{i}]")
        g.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{vd:.4f},asetpts=PTS-STARTPTS[a{i}]")
    vprev, aprev = "v0", "a0"
    for i in range(1, n):
        d = CLIPS[i][2]
        off = starts[i][0]
        g.append(f"[{vprev}][v{i}]xfade=transition=fade:duration={d:.4f}:offset={off:.4f}[vx{i}]")
        g.append(f"[{aprev}][a{i}]acrossfade=d={d:.4f}:c1=tri:c2=tri[ax{i}]")
        vprev, aprev = f"vx{i}", f"ax{i}"
    for k, (_, t0, t1) in enumerate(overlays):
        g.append(f"[{vprev}][{n + k}:v]overlay=0:0:enable='between(t,{t0:.3f},{t1:.3f})'[o{k}]")
        vprev = f"o{k}"
    g.append(f"[{vprev}]format=yuv420p[vout]")
    if vo:
        vi = n + len(overlays)
        g.append(f"[{vi}:a]aformat=sample_rates=48000:channel_layouts=stereo,loudnorm=I=-16:TP=-1.5:LRA=7,apad,asplit=2[vo][sc]")
        g.append(f"[{aprev}]apad,atrim=0:{total:.3f},volume=0.4[bed]")
        g.append("[bed][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[duck]")
        g.append(f"[duck][vo]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9,apad,atrim=0:{total:.3f}[aout]")
    else:
        g.append(f"[{aprev}]loudnorm=I=-14:TP=-1.5:LRA=9,apad,atrim=0:{total:.3f}[aout]")

    graph = os.path.join(BUILD, "graph.txt")
    with open(graph, "w") as f:
        f.write(";\n".join(g))
    cmd += ["-filter_complex_script", graph, "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-t", f"{total:.3f}", out]
    print(f"{n} clips, {len(overlays)} overlays, {total:.1f}s -> {out}")
    subprocess.run(cmd, check=True)

    if not base:
        sheet = out.rsplit(".", 1)[0] + "-contact.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out, "-vf",
                        f"fps=24/{total:.2f},scale=216:384,tile=6x4:padding=4:color=gray", "-frames:v", "1", sheet],
                       check=True)
        print(f"contact sheet -> {sheet}")
    # caption timing table for checking
    for (label, _, _, _), (s, d) in zip(CLIPS, starts):
        print(f"  {s:6.2f}s  {label}")


if __name__ == "__main__":
    a = sys.argv[1:]
    vo = a[a.index("--vo") + 1] if "--vo" in a else None
    if "--base" in a:
        build(os.path.join(BUILD, "zepto-base.mp4"), vo=vo, base=True)
    else:
        build(os.path.join(OUT, "zepto-reel.mp4" if not vo else "zepto-reel-voiceover.mp4"), vo=vo,
              preview="--preview" in a)
