#!/usr/bin/env python3
"""
Papercraft-mascot reel assembler (house style, see reels/STYLE.md).

Takes a project folder with shots.json + one image (or clip) per shot and builds a
1080x1920 / 30 fps reel with:
  * a slow camera move on every shot (push / pan / zoom-through into the next shot),
  * the hook title at the top (yellow line + white lines),
  * bottom captions with [y]yellow[/y] and [r]red[/r] keywords, black outline,
  * the red "M" logo bottom-right,
  * voiceover (vo.mp3 / vo.wav in the project, optional) over a soft music bed + SFX.

Usage (from reels/):
  python3 tools/paper_reel.py projects/atm-kaise              # final -> output/atm-kaise.mp4
  python3 tools/paper_reel.py projects/atm-kaise --preview    # contact sheet -> output/atm-kaise-contact.jpg

Shot durations: if the project has vo.* the shots share the VO length in proportion to
caption length; `"dur": 3.5` on a shot overrides that. Without VO it's ~0.36 s per word.
Shots can use images/<id>.(jpg|png|webp), clips/<id>.mp4, or a "media" list mixing clip
segments (with in/out and slow-mo speed, e.g. from library/) and images.
"""
import json, math, os, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reel_fx import FX, fx_cues

W, H, FPS = 1080, 1920, 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIRS = ["/usr/share/fonts/opentype/inter", "/usr/share/fonts/truetype/dejavu"]
YELLOW, RED, WHITE = (255, 214, 10), (255, 59, 48), (255, 255, 255)
XFADE = 0.25      # cross-dissolve between shots (s)
ZOOM_T = 0.45     # length of the zoom-through at the end of a "zoom" shot (s)


def font(size, weight="ExtraBold"):
    for d in FONT_DIRS:
        for name in (f"Inter-{weight}.otf", f"InterDisplay-{weight}.otf", "Inter-Bold.otf", "DejaVuSans-Bold.ttf"):
            p = os.path.join(d, name)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()


# ------------------------------------------------------------------ captions
def parse_spans(text):
    """'a [y]b[/y] c [r]d[/r]' -> [(word, colour), ...]"""
    out, colour = [], WHITE
    for tok in re.split(r"(\[/?[yr]\])", text):
        if tok in ("[y]", "[r]"):
            colour = YELLOW if tok == "[y]" else RED
        elif tok in ("[/y]", "[/r]"):
            colour = WHITE
        else:
            for w in tok.split():
                out.append((w, colour))
    return out


def wrap(words, f, max_w):
    lines, cur = [], []
    space = f.getlength(" ")
    for w, c in words:
        test = sum(f.getlength(x) for x, _ in cur) + space * len(cur) + f.getlength(w)
        if cur and test > max_w:
            lines.append(cur)
            cur = []
        cur.append((w, c))
    if cur:
        lines.append(cur)
    return lines


def text_block(words, size, max_w, line_gap=1.12, stroke=None):
    """RGBA image of centred multi-colour text with a black outline + soft shadow."""
    f = font(size)
    stroke = stroke or max(3, size // 11)
    lines = wrap(words, f, max_w)
    lh = int(size * line_gap)
    pad = stroke * 4
    img = Image.new("RGBA", (max_w + pad * 2, lh * len(lines) + pad * 2), (0, 0, 0, 0))
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(img), ImageDraw.Draw(shadow)
    space = f.getlength(" ")
    for i, line in enumerate(lines):
        lw = sum(f.getlength(w) for w, _ in line) + space * (len(line) - 1)
        x = pad + (max_w - lw) / 2
        y = pad + i * lh
        for w, c in line:
            ds.text((x + 2, y + size * 0.08), w, font=f, fill=(0, 0, 0, 170), stroke_width=stroke + 2, stroke_fill=(0, 0, 0, 170))
            d.text((x, y), w, font=f, fill=c, stroke_width=stroke, stroke_fill=(0, 0, 0))
            x += f.getlength(w) + space
    shadow = shadow.filter(ImageFilter.GaussianBlur(size * 0.12))
    return Image.alpha_composite(shadow, img)


def logo():
    s = 78
    img = Image.new("RGBA", (s + 12, s + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((8, 10, s + 8, s + 10), fill=(0, 0, 0, 90))
    d.ellipse((6, 6, s + 6, s + 6), fill=(229, 25, 36), outline=(255, 255, 255), width=3)
    f = font(44)
    d.text((6 + s / 2, 6 + s / 2 + 1), "M", font=f, fill="white", anchor="mm")
    return img


# ------------------------------------------------------------------ shots
# A shot plays a sequence of media items, e.g.
#   "media": [{"clip": "library/card-mascot/atm-cash-out.mp4", "in": 0.8, "out": 3.2, "speed": 0.6},
#             {"image": "s08"}]
# Clip items take their natural length ((out-in)/speed); image items share the rest of the shot.
# Without "media", the shot uses clips/<id>.mp4 or images/<id>.* (placeholder if neither exists).
ITEM_FADE = 0.2


def load_still(proj, sid):
    for ext in ("jpg", "jpeg", "png", "webp"):
        p = os.path.join(proj, "images", f"{sid}.{ext}")
        if os.path.exists(p):
            im = Image.open(p).convert("RGB")
            scale = max(W * 1.18 / im.width, H * 1.18 / im.height)   # headroom for camera moves
            return im.resize((math.ceil(im.width * scale), math.ceil(im.height * scale)), Image.LANCZOS), True
    im = Image.new("RGB", (int(W * 1.18), int(H * 1.18)), (176, 132, 84))
    ImageDraw.Draw(im).text((im.width / 2, im.height / 2), f"{sid}\n(add images/{sid}.jpg)", font=font(64), fill=(60, 35, 15), anchor="mm", align="center")
    return im, False


def prep_clip(src, t_in=0.0, t_out=None, speed=1.0):
    """Trim / slow / interpolate / scale a clip to 1080x1920@30 once and cache it."""
    import hashlib
    t_out = t_out if t_out is not None else float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                                                               capture_output=True, text=True).stdout)
    key = hashlib.md5(f"{os.path.abspath(src)}|{os.path.getmtime(src)}|{t_in}|{t_out}|{speed}".encode()).hexdigest()[:12]
    cache = os.path.join(ROOT, "output", "cache")
    os.makedirs(cache, exist_ok=True)
    out = os.path.join(cache, f"{os.path.splitext(os.path.basename(src))[0]}-{key}.mp4")
    if not os.path.exists(out):
        vf = f"setpts=PTS/{speed},"
        vf += f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1," if speed < 0.95 else f"fps={FPS},"
        vf += f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t_in), "-t", str(t_out - t_in), "-i", src, "-vf", vf, "-an",
                        "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", out + ".tmp.mp4"], check=True)
        os.replace(out + ".tmp.mp4", out)
    n = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames",
                            "-of", "csv=p=0", out], capture_output=True, text=True).stdout.strip() or 0)
    return out, n


class ClipStream:
    """Sequential frame reader for a prepared clip; random access re-seeks; holds the last frame."""
    def __init__(self, path, n):
        self.path, self.n, self.proc, self.pos, self.cur, self.last = path, n, None, -1, None, None

    def _open(self, start):
        if self.proc:
            self.proc.kill()
        self.proc = subprocess.Popen(["ffmpeg", "-v", "quiet", "-ss", f"{start / FPS:.4f}", "-i", self.path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.pos = start - 1

    def frame(self, i):
        i = max(0, min(i, self.n - 1))
        if i == self.pos and self.cur is not None:
            return self.cur
        if self.last is not None and i == self.n - 1:
            return self.last
        if self.proc is None or i < self.pos or i > self.pos + 45:
            self._open(i)
        while self.pos < i:
            buf = self.proc.stdout.read(W * H * 3)
            if len(buf) < W * H * 3:
                self.n = self.pos + 1
                return self.cur if self.cur is not None else Image.new("RGB", (W, H))
            self.pos += 1
            self.cur = Image.frombytes("RGB", (W, H), buf)
        if i == self.n - 1:
            self.last = self.cur
        return self.cur


def build_items(proj, shot, dur):
    """-> list of dicts {kind, t0, t1, data} in shot-local time."""
    spec = shot.get("media")
    if not spec:
        clip = os.path.join(proj, "clips", f"{shot['id']}.mp4")
        spec = [{"clip": os.path.relpath(clip, ROOT)}] if os.path.exists(clip) else [{"image": shot["id"]}]
    items = []
    for m in spec:
        if "clip" in m:
            path, n = prep_clip(os.path.join(ROOT, m["clip"]), m.get("in", 0.0), m.get("out"), m.get("speed", 1.0))
            items.append({"kind": "clip", "len": n / FPS, "data": ClipStream(path, n), "ok": True})
        else:
            im, ok = load_still(proj, m["image"])
            items.append({"kind": "image", "len": None, "data": im, "ok": ok, "min": m.get("min", 1.2)})
    clip_len = sum(it["len"] for it in items if it["kind"] == "clip")
    imgs = [it for it in items if it["kind"] == "image"]
    if imgs:
        need = sum(it["min"] for it in imgs)
        k = min(1.0, max(0.0, dur - need) / clip_len) if clip_len else 1.0
        for it in items:
            if it["kind"] == "clip":
                it["len"] *= k            # trims clip playback if the shot is short
        rest = (dur - clip_len * k) / len(imgs)
        for it in imgs:
            it["len"] = rest
    t = 0.0
    for it in items:
        it["t0"], it["t1"] = t, t + it["len"]
        t = it["t1"]
    items[-1]["t1"] = max(items[-1]["t1"], dur)  # last item holds to the end of the shot
    return items


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def crop_zoom(im, z, cx=0.5, cy=0.5):
    base = max(W / im.width, H / im.height)
    cw, ch = W / (base * z), H / (base * z)
    x0 = min(max(cx * im.width - cw / 2, 0), im.width - cw)
    y0 = min(max(cy * im.height - ch / 2, 0), im.height - ch)
    return im.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


def item_frame(it, lt, move, idx):
    """Frame of one media item at shot-local time lt, with its own camera move."""
    k = (lt - it["t0"]) / max(it["t1"] - it["t0"], 1e-6)
    if it["kind"] == "clip":
        f = it["data"].frame(int(round((lt - it["t0"]) * FPS)))
        return crop_zoom(f, 1.0 + 0.05 * k) if k > 0 else f
    im = it["data"]
    if move == "pan":
        dirn = -1 if idx % 2 else 1
        return crop_zoom(im, 1.12, 0.5 + dirn * (k - 0.5) * 0.12, 0.5)
    return crop_zoom(im, 1.0 + 0.09 * k, 0.5, 0.48)


def shot_frame(items, lt, dur, move, idx):
    j = next((n for n, it in enumerate(items) if lt < it["t1"]), len(items) - 1)
    img = item_frame(items[j], lt, move, idx)
    if j > 0 and lt - items[j]["t0"] < ITEM_FADE:
        prev = item_frame(items[j - 1], items[j - 1]["t1"] - 1e-3, move, idx)
        img = Image.blend(prev, img, ease((lt - items[j]["t0"]) / ITEM_FADE))
    if move == "zoom" and lt > dur - ZOOM_T:   # zoom-through into the next shot
        z = 1 + 1.6 * ease((lt - (dur - ZOOM_T)) / ZOOM_T) ** 2
        img = crop_zoom(img, z, 0.5, 0.48)
    return img


# ------------------------------------------------------------------ main
def main():
    args = sys.argv[1:]
    proj = os.path.abspath(os.path.join(ROOT, next(a for a in args if not a.startswith("--"))))
    name = os.path.basename(proj)
    preview = "--preview" in args
    cfg = json.load(open(os.path.join(proj, "shots.json")))
    shots = cfg["shots"]
    out_dir = os.path.join(ROOT, "output")
    os.makedirs(out_dir, exist_ok=True)

    vo = next((os.path.join(proj, f) for f in ("vo.mp3", "vo.wav", "vo.m4a") if os.path.exists(os.path.join(proj, f))), None)
    words = [len(parse_spans(s["caption"])) for s in shots]
    if vo:
        vo_len = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", vo],
                                      capture_output=True, text=True).stdout)
        fixed = sum(s.get("dur", 0) for s in shots)
        free_words = sum(w for s, w in zip(shots, words) if "dur" not in s) or 1
        per_word = max(vo_len + 0.6 - fixed, 1) / free_words
    else:
        per_word = 0.36
    durs = [s.get("dur", max(2.6, w * per_word)) for s, w in zip(shots, words)]
    starts = np.concatenate([[0], np.cumsum(durs)])
    total = float(starts[-1])
    print(f"[{name}] {len(shots)} shots, {total:.1f}s, VO: {os.path.basename(vo) if vo else 'none (music + SFX only)'}")

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(4) as ex:   # clip prep (slow-mo interpolation) runs in parallel
        sources = list(ex.map(lambda a: build_items(proj, a[0], a[1]), zip(shots, durs)))
    have = sum(1 for its in sources if all(it["ok"] for it in its))
    print(f"  media found for {have}/{len(shots)} shots ({sum(it['kind'] == 'clip' for its in sources for it in its)} clip segments)")

    caps = [text_block(parse_spans(s["caption"]), 58, 920) for s in shots]
    t_cfg = cfg.get("title")
    title = None
    if t_cfg:
        y = text_block([(w, YELLOW) for w in t_cfg["yellow"].split()], 140, 980, stroke=8)
        wl = [text_block([(w, WHITE) for w in line.split()], 92, 980, stroke=7) for line in t_cfg["white"].split("\n")]
        title = Image.new("RGBA", (max(i.width for i in [y] + wl), y.height + sum(i.height for i in wl) - 40 * len(wl)), (0, 0, 0, 0))
        title.alpha_composite(y, ((title.width - y.width) // 2, 0))
        yy = y.height - 40
        for i in wl:
            title.alpha_composite(i, ((title.width - i.width) // 2, yy))
            yy += i.height - 40
    lg = logo()
    MG = FX()
    vignette = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vignette)
    for i in range(60):  # darken the bottom third gently so captions read
        a = int(150 * (i / 60) ** 1.6)
        vd.rectangle((0, int(H * 0.55 + i * (H * 0.45 / 60)), W, H), fill=a)
    vignette = vignette.filter(ImageFilter.GaussianBlur(40))
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    shade.putalpha(vignette)

    def frame_at(t):
        i = int(np.searchsorted(starts, t, side="right") - 1)
        i = min(max(i, 0), len(shots) - 1)
        lt = t - starts[i]
        img = shot_frame(sources[i], lt, durs[i], shots[i].get("move", "push"), i)
        # cross-dissolve from the previous shot (skip after a zoom-through: that's a hard match cut)
        if i > 0 and lt < XFADE and shots[i - 1].get("move") != "zoom":
            prev = shot_frame(sources[i - 1], durs[i - 1] - 1e-3, durs[i - 1], shots[i - 1].get("move", "push"), i - 1)
            img = Image.blend(prev, img, ease(lt / XFADE))
        frame = img.convert("RGBA")
        frame.alpha_composite(shade)
        fx = shots[i].get("fx", [])
        if fx:
            dx, dy, fl = MG.offset(fx, lt)
            if dx or dy:
                big = frame.resize((int(W * 1.05), int(H * 1.05)), Image.BILINEAR)
                ox, oy = int((big.width - W) / 2 - dx), int((big.height - H) / 2 - dy)
                frame = big.crop((ox, oy, ox + W, oy + H))
            MG.draw(frame, fx, lt, durs[i])
            if fl:
                frame.alpha_composite(Image.new("RGBA", (W, H), (255, 248, 230, int(255 * fl))))
        # caption: quick pop-in
        cap = caps[i]
        k = ease(lt / 0.14)
        if k < 1:
            cap = cap.resize((max(1, int(cap.width * (0.92 + 0.08 * k))), max(1, int(cap.height * (0.92 + 0.08 * k)))), Image.BILINEAR)
            a = cap.getchannel("A").point(lambda v: int(v * k))
            cap.putalpha(a)
        cy = 1330 - cap.height // 2 + caps[i].height // 2 - 60
        frame.alpha_composite(cap, ((W - cap.width) // 2, int(cy)))
        if title and t < t_cfg.get("until", 4):
            ta = 1.0 if t < t_cfg["until"] - 0.25 else max(0.0, (t_cfg["until"] - t) / 0.25)
            ti = title.copy()
            if ta < 1:
                ti.putalpha(ti.getchannel("A").point(lambda v: int(v * ta)))
            frame.alpha_composite(ti, ((W - ti.width) // 2, 190))
        frame.alpha_composite(lg, (W - lg.width - 60, H - lg.height - 150))
        return frame.convert("RGB")

    if preview:
        pdir = os.path.join(out_dir, f"{name}-preview")
        os.makedirs(pdir, exist_ok=True)
        for f in os.listdir(pdir):
            os.remove(os.path.join(pdir, f))
        for i in range(len(shots)):
            t = starts[i] + min(durs[i] * 0.55, durs[i] - ZOOM_T - 0.05)
            frame_at(t).save(os.path.join(pdir, f"{i:02d}_{t:05.2f}s.png"))
        cols = 5
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-pattern_type", "glob", "-i", os.path.join(pdir, "*.png"),
                        "-vf", f"scale=270:480,tile={cols}x{math.ceil(len(shots) / cols)}:padding=6:color=gray",
                        "-frames:v", "1", os.path.join(out_dir, f"{name}-contact.jpg")], check=True)
        print(f"preview -> output/{name}-contact.jpg")
        return

    silent = os.path.join(out_dir, f"{name}.video.mp4")
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-profile:v", "high", silent],
                          stdin=subprocess.PIPE)
    n = int(round(total * FPS))
    for f in range(n):
        ff.stdin.write(frame_at(f / FPS).tobytes())
        if f % 60 == 0:
            print(f"\r  frame {f}/{n}", end="", flush=True)
    ff.stdin.close()
    ff.wait()
    print()

    # ---- audio: music bed + SFX on cuts, then the VO on top
    cues = [{"t": 0, "sfx": "pad", "gain": 0.35, "dur": total}, {"t": 0, "sfx": "drone", "gain": 0.12, "dur": total}]
    beat = 60 / 100
    for k in range(int(total / beat)):
        cues.append({"t": round(k * beat, 3), "sfx": "pop_low" if k % 2 == 0 else "tick", "gain": 0.07 if k % 2 == 0 else 0.04})
    for i, s in enumerate(shots):
        t0 = float(starts[i])
        if i:
            cues.append({"t": max(0, t0 - 0.05), "sfx": "swish", "gain": 0.28})
        cues.append({"t": t0 + 0.02, "sfx": "pop", "gain": 0.22})
        if s.get("move") == "zoom":
            cues.append({"t": t0 + durs[i] - ZOOM_T - 0.05, "sfx": "whoosh", "gain": 0.45})
        if "₹" in s["caption"]:
            cues.append({"t": t0 + 0.4, "sfx": "ding", "gain": 0.25})
    for i, s in enumerate(shots):
        cues += fx_cues(s.get("fx", []), float(starts[i]))
    cues_p = os.path.join(out_dir, f"{name}.cues.json")
    bed = os.path.join(out_dir, f"{name}.sfx.wav")
    json.dump(sorted(cues, key=lambda c: c["t"]), open(cues_p, "w"))
    subprocess.run([sys.executable, os.path.join(ROOT, "tools/sfx.py"), "mix", cues_p, bed, str(total)], check=True)
    final = os.path.join(out_dir, f"{name}.mp4")
    if vo:  # music ducks under the voice
        cmd =["ffmpeg", "-v", "error", "-y", "-i", silent, "-i", bed, "-i", vo, "-filter_complex",
               "[2:a]adelay=300|300[v];[v]asplit[v1][v2];[1:a]volume=0.6[m];[m][v1]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=350[d];[d][v2]amix=inputs=2:normalize=0[a]",
               "-map", "0:v", "-map", "[a]"]
    else:
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", silent, "-i", bed, "-map", "0:v", "-map", "1:a"]
    cmd += ["-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-t", f"{total:.3f}", "-movflags", "+faststart", final]
    subprocess.run(cmd, check=True)
    os.remove(silent)
    print(f"done -> {final}")


if __name__ == "__main__":
    main()
