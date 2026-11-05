#!/usr/bin/env python3
"""
Zomato Economy reel: assembles the user's clips on the Hindi voiceover.

  python3 vo.py      # tighten the voiceover to 75s  -> build/vo_tight.wav
  python3 audio.py   # music bed + sound design + mix -> build/mix.wav
  python3 build.py   # picture + final mux           -> ../../output/zomato-economy.mp4
  python3 build.py --preview   # contact sheet only   -> ../../output/zomato-economy-contact.jpg

Every cut is placed on the tightened voiceover (times below are in seconds of
the final reel). Clean paper banners cover the AI-generated titles that were
wrong for this story ("Doomscrolling", the "Vox" logo, garbled numbers).
"""
import os, subprocess, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.join(HERE, "media")
BUILD = os.path.join(HERE, "build")
OUTDIR = os.path.abspath(os.path.join(HERE, "..", "..", "output"))
FONT_BIG = os.path.join(HERE, "fonts", "Anton-Regular.ttf")
FONT_SUB = os.path.join(HERE, "fonts", "Oswald-Bold.ttf")
W, H, FPS = 1080, 1920, 30
END = 75.7
S = 3.0  # source clips are 360x640 -> 1080x1920

INK = (29, 24, 22)
RED = (158, 24, 30)
PAPER = (238, 229, 211)
rng = np.random.default_rng(11)


# ------------------------------------------------------------------ overlays
def _paper(w, h):
    base = np.zeros((h, w, 3), np.float32) + PAPER
    base += rng.normal(0, 5, (h, w, 1))
    fib = cv2.GaussianBlur(rng.normal(0, 14, (h, w)).astype(np.float32), (0, 0), 6)
    base += fib[..., None]
    return np.clip(base, 0, 255).astype(np.uint8)


def banner(line1, line2=None, h=300, cover_h=None, accent=None):
    """Full-width torn-paper strip that sits at the top of the frame."""
    cover_h = cover_h or h
    total = cover_h + 70
    img = Image.new("RGBA", (W, total), (0, 0, 0, 0))
    # torn bottom edge
    xs = np.arange(0, W + 18, 18)
    ys = cover_h + rng.uniform(-14, 14, len(xs))
    poly = [(0, 0), (W, 0)] + [(int(x), int(y)) for x, y in zip(xs[::-1], ys[::-1])]
    mask = Image.new("L", (W, total), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    shadow = Image.new("RGBA", (W, total), (0, 0, 0, 0))
    sm = mask.copy().filter(ImageFilter.GaussianBlur(14))
    shadow.putalpha(sm.point(lambda v: int(v * 0.45)))
    shadow = Image.composite(shadow, shadow, sm)
    img.alpha_composite(shadow, (0, 14))
    paper = Image.fromarray(_paper(W, total)).convert("RGBA")
    paper.putalpha(mask)
    img.alpha_composite(paper)
    d = ImageDraw.Draw(img)
    # thin double rule like the clips' editorial headers
    d.line([(60, cover_h - 46), (W - 60, cover_h - 46)], fill=INK, width=3)
    d.line([(60, cover_h - 38), (W - 60, cover_h - 38)], fill=INK, width=1)
    f1 = ImageFont.truetype(FONT_BIG, 10)
    size = 150
    while size > 40:
        f1 = ImageFont.truetype(FONT_BIG, size)
        if d.textlength(line1, font=f1) <= W - 120:
            break
        size -= 4
    asc = f1.getbbox(line1)
    block = (asc[3] - asc[1]) + (70 if line2 else 0)
    top = max(24, (cover_h - 50 - block) // 2) - asc[1]
    # line1, with an optional red accent word
    x = (W - d.textlength(line1, font=f1)) / 2
    if accent and accent in line1:
        pre, post = line1.split(accent, 1)
        for part, col in ((pre, INK), (accent, RED), (post, INK)):
            d.text((x, top), part, font=f1, fill=col)
            x += d.textlength(part, font=f1)
    else:
        d.text((x, top), line1, font=f1, fill=INK)
    if line2:
        f2 = ImageFont.truetype(FONT_SUB, 48)
        y2 = top + asc[3] + 14
        tw = d.textlength(line2, font=f2)
        d.rectangle([(W - tw) / 2 - 18, y2 - 2, (W + tw) / 2 + 18, y2 + 62], fill=RED)
        d.text(((W - tw) / 2, y2), line2, font=f2, fill=PAPER)
    return np.array(img)


def tag(text, size=64, angle=0.0, pad=(34, 16), color=RED, fg=PAPER, font=FONT_SUB):
    f = ImageFont.truetype(font, size)
    tw = int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(text, font=f))
    bb = f.getbbox(text)
    w, h = tw + pad[0] * 2, (bb[3] - bb[1]) + pad[1] * 2
    img = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([30, 36, 30 + w, 36 + h], fill=(0, 0, 0, 120))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    d = ImageDraw.Draw(img)
    d.rectangle([30, 30, 30 + w, 30 + h], fill=color)
    d.text((30 + pad[0], 30 + pad[1] - bb[1]), text, font=f, fill=fg)
    if angle:
        img = img.rotate(angle, resample=Image.BICUBIC, expand=True)
    return np.array(img)


def card_patch():
    """Covers 'PREMIUM VISUAL JOURNALISM / GROWTH TRAJECTORY' on the 3,879 card
    (frame at src 3.6s) with a clean caption on matching paper."""
    w, h = 1000, 440
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    paper = Image.fromarray(_paper(w, h)).convert("RGBA")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rectangle([40, 30, w - 40, h - 30], fill=255)
    paper.putalpha(m.filter(ImageFilter.GaussianBlur(3)))
    img.alpha_composite(paper)
    t = Image.fromarray(tag("FOOD DELIVERY  ·  Q2 FY27", 66, 0))
    img.alpha_composite(t, ((w - t.width) // 2, (h - t.height) // 2))
    return np.array(img.rotate(4.5, resample=Image.BICUBIC, expand=False))


_logo_cache = {}
def logo_badge(d):
    """The user's round red M logo as a small badge (cream ring + soft shadow)."""
    d = int(round(d))
    if d in _logo_cache:
        return _logo_cache[d]
    src = Image.open(os.path.join(MEDIA, "logo_source.png")).convert("RGB")
    cx, cy, r = 1193.5, 833.5, 833.5
    k = 4  # supersample
    D = d * k
    disc = src.crop((int(cx - r), int(cy - r), int(cx + r), int(cy + r))).resize((D, D), Image.LANCZOS)
    pad = int(D * 0.16)
    canvas = Image.new("RGBA", (D + 2 * pad, D + 2 * pad), (0, 0, 0, 0))
    m = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(m).ellipse([pad, pad + int(D * 0.05), pad + D, pad + D + int(D * 0.05)], fill=150)
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 255)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(D * 0.05)).point(lambda v: int(v * 0.7)))
    canvas.alpha_composite(sh)
    ring = int(D * 0.045)
    ImageDraw.Draw(canvas).ellipse([pad, pad, pad + D, pad + D], fill=PAPER + (255,))
    inner = D - 2 * ring
    dm = Image.new("L", (inner, inner), 0)
    ImageDraw.Draw(dm).ellipse([0, 0, inner - 1, inner - 1], fill=255)
    disc = disc.resize((inner, inner), Image.LANCZOS).convert("RGBA"); disc.putalpha(dm)
    canvas.alpha_composite(disc, (pad + ring, pad + ring))
    out = canvas.resize((canvas.width // k, canvas.height // k), Image.LANCZOS)
    _logo_cache[d] = np.array(out)
    return _logo_cache[d]


# Gemini/Veo sparkle position (relative to the frame) and its size
SPARK_VIDEO = (0.8319, 0.9053, 0.066)  # x, y, badge diameter as fraction of width
SPARK_IMAGE = (0.8743, 0.9295, 0.068)


def watermark_cover(ct=0.0, spark=SPARK_VIDEO, w=W, h=H):
    x, y, dfr = spark
    x = (x - ct / 2) / (1 - ct)
    y = (y - ct) / (1 - ct)
    d = dfr * w / (1 - ct)
    b = logo_badge(d)
    return (b, x * w - b.shape[1] / 2, y * h - b.shape[0] / 2 + 0.01 * d, None, "static")


# ------------------------------------------------------------------ timeline
# t = start in the reel; clip = media/<clip>.mp4; src = in-point; sp = speed
# ct = crop fraction from top (zoom anchored to the bottom)
# ov = overlays: (rgba, x, y, appear_at_reel_time or None=static, mode)
def T(name, t, src=0.0, sp=1.0, **kw):
    return dict(kind="clip", clip=name, t=t, src=src, sp=sp, **kw)


OV = {}
def overlays():
    OV["eco"] = banner("THE ZOMATO ECOSYSTEM", "CUSTOMER  ·  RESTAURANT  ·  DELIVERY", cover_h=300, accent="ZOMATO")
    OV["commission"] = banner("COMMISSION", "ON EVERY ORDER", cover_h=330, accent="COMMISSION")
    OV["customers"] = banner("NEW CUSTOMERS", "+ MORE ORDERS", cover_h=300, accent="NEW")
    OV["profit"] = banner("NOT ALL OF IT IS PROFIT", None, cover_h=300, accent="PROFIT")
    OV["costs"] = banner("WHERE THE MONEY GOES", None, cover_h=200, accent="MONEY")
    OV["nov"] = banner("NET ORDER VALUE", "FOOD DELIVERY  ·  Q2 FY27", cover_h=540, accent="NET ORDER")
    OV["rev"] = banner("ADJUSTED REVENUE", None, cover_h=250, accent="REVENUE")
    OV["ebitda"] = tag("ADJUSTED EBITDA", 70, 0)
    OV["q2"] = tag("Q2  ·  FY27", 76, 0, color=PAPER, fg=INK)
    OV["patch"] = card_patch()


def timeline():
    o = OV
    return [
        T("hook_zomato", 0.00, 0.20, 1.60, ct=0.12, punch=False),
        T("order_500", 2.33, 0.00, 0.88),
        T("hook_zomato", 6.93, 4.00, 1.00, ct=0.12),
        dict(kind="image", img="feast.jpg", t=9.93, kb=(1.0, 1.13, -0.02, 0.06)),
        T("chef", 13.54, 0.90, 1.00),
        T("ecosystem_phone", 14.78, 0.00, 1.00, ov=[(o["eco"], 0, 0, None, "static")]),
        T("ecosystem_circle", 16.90, 1.50, 1.00),
        T("owner_orders", 19.36, 0.00, 1.00, ov=[(o["commission"], 0, 0, 20.30, "drop")]),
        T("owner_commission", 23.30, 2.40, 0.82, ov=[(o["customers"], 0, 0, None, "static")]),
        T("mumbai_rider", 25.25, 0.00, 0.93),
        T("checkout", 27.30, 0.00, 1.00),
        T("rider_night_receipt", 29.20, 5.30, 1.00),
        T("hidden_cost", 31.72, 0.00, 0.86),
        T("ads", 34.05, 0.00, 1.03),
        T("gold", 37.90, 0.00, 0.85),
        T("rider_night_receipt", 42.62, 0.00, 0.80),
        T("coins_jar", 44.61, 0.00, 1.00, ov=[(o["profit"], 0, 0, 45.80, "drop")]),
        T("expenses", 48.29, 0.00, 0.88, ov=[(o["costs"], 0, 0, None, "static")]),
        T("rider_night_receipt", 52.83, 1.60, 1.00, ov=[(o["q2"], 70, 1450, 53.00, "slap")]),
        T("map_11445", 55.00, 0.00, 0.62, ov=[(o["nov"], 0, 0, None, "static")]),
        T("map_11445", 57.95, 3.00, 1.00, drift=1.05, ov=[(o["nov"], 0, 0, None, "static")]),
        T("bars_3879", 60.58, 1.45, 0.65, ov=[(o["rev"], 0, 0, 60.62, "drop")]),
        dict(kind="still", clip="bars_3879", t=61.88, src=3.60, zoom=(1.0, 1.07),
             ov=[(o["patch"], 30, 1190, None, "static"), (o["rev"], 0, 0, None, "screen")]),
        T("bar_627", 63.78, 0.60, 1.00, ov=[(o["ebitda"], None, 300, 63.90, "slap")]),
        T("door_gift", 67.00, 1.90, 0.93, ct=0.03),
        T("gift_open", 69.26, 1.75, 0.78),
        T("brand_card", 72.13, 0.55, 1.00, xfade=0.22, punch=False),
    ]


# ------------------------------------------------------------------ decoding
def decode(clip, src, sp, nframes, ct=0.0, single=False):
    path = os.path.join(MEDIA, clip + ".mp4")
    src_dur = nframes / FPS * sp + 0.25
    crop = f"crop=iw*{1-ct:.4f}:ih*{1-ct:.4f}:iw*{ct/2:.4f}:ih*{ct:.4f}," if ct else ""
    fr = "fps=30" if sp >= 0.95 else "framerate=fps=30:interp_start=0:interp_end=255:scene=100"
    vf = (f"setpts=(PTS-STARTPTS)/{sp},{fr},hqdn3d=1.0:1.0:2.5:2.5,{crop}"
          f"scale={W}:{H}:flags=lanczos,cas=0.42,format=rgb24")
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{src:.3f}", "-i", path, "-t", f"{src_dur:.3f}",
           "-vf", vf, "-an", "-f", "rawvideo", "-"]
    if single:
        cmd[cmd.index("-t") + 1] = "0.2"
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    fr_ = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    if single:
        return [fr_[0]] * nframes
    out = list(fr_[:nframes])
    while len(out) < nframes:  # hold the last frame (freeze) if the clip runs out
        out.append(out[-1])
    return out


def load_image(name, nframes, kb):
    z0, z1, dx, dy = kb
    im = Image.open(os.path.join(MEDIA, name)).convert("RGB")
    big = im.resize((int(W * 1.2), int(W * 1.2 * im.height / im.width)), Image.LANCZOS)
    big = np.array(big.filter(ImageFilter.UnsharpMask(1.2, 60, 2)))
    bh, bw = big.shape[:2]
    b, x, y, _, _ = watermark_cover(0.0, SPARK_IMAGE, bw, bh)
    big = composite(big, b, x, y)
    frames = []
    for i in range(nframes):
        p = i / max(1, nframes - 1)
        e = p * p * (3 - 2 * p)
        z = z0 + (z1 - z0) * e
        s_ = max(W / bw, H / bh) * z  # cover the frame at zoom z
        cx = bw / 2 + dx * bw * (e - 0.5)
        cy = bh / 2 + dy * bh * (e - 0.5)
        M = np.float32([[s_, 0, W / 2 - s_ * cx], [0, s_, H / 2 - s_ * cy]])
        frames.append(cv2.warpAffine(big, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT))
    return frames


# ------------------------------------------------------------------ effects
def ease_out(p):
    return 1 - (1 - p) ** 3


def back_out(p, s=1.6):
    p -= 1
    return p * p * ((s + 1) * p + s) + 1


def zoom(frame, z, anchor=(0.5, 0.5)):
    if abs(z - 1) < 1e-4:
        return frame
    ax, ay = W * anchor[0], H * anchor[1]
    M = np.float32([[z, 0, ax - z * ax], [0, z, ay - z * ay]])
    return cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def composite(frame, rgba, x, y, alpha=1.0, scale=1.0):
    if scale != 1.0:
        rgba = cv2.resize(rgba, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    h, w = rgba.shape[:2]
    FH, FW = frame.shape[:2]
    x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(0, x), max(0, y), min(FW, x + w), min(FH, y + h)
    if x0 >= x1 or y0 >= y1:
        return frame
    sub = rgba[y0 - y:y1 - y, x0 - x:x1 - x]
    a = sub[..., 3:4].astype(np.float32) / 255 * alpha
    roi = frame[y0:y1, x0:x1].astype(np.float32)
    frame[y0:y1, x0:x1] = (roi * (1 - a) + sub[..., :3] * a).astype(np.uint8)
    return frame


def apply_overlays(frame, ovs, t):
    for rgba, x, y, at, mode in ovs or []:
        h, w = rgba.shape[:2]
        if x is None:
            x = (W - w) // 2
        if at is None or mode in ("static", "screen"):
            composite(frame, rgba, x, y)
            continue
        if t < at:
            continue
        p = min(1.0, (t - at) / 0.30)
        if mode == "drop":
            composite(frame, rgba, x, y - (1 - back_out(p)) * (h + 40))
        elif mode == "slap":
            sc = 1.0 + 0.45 * (1 - ease_out(p))
            nw, nh = w * sc, h * sc
            composite(frame, rgba, x - (nw - w) / 2, y - (nh - h) / 2, alpha=min(1, p * 3), scale=sc)
    return frame


_vig = None
def finish(frame, i):
    global _vig
    if _vig is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
        _vig = (1 - 0.28 * np.clip(r - 0.55, 0, 1) ** 1.6)[..., None].astype(np.float32)
    f = frame.astype(np.float32) * _vig
    g = np.random.default_rng(i).normal(0, 4.2, (H // 2, W // 2, 1)).astype(np.float32)
    f += cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    return np.clip(f, 0, 255).astype(np.uint8)


# ------------------------------------------------------------------ render
def segment_frames(seg, nframes):
    if seg["kind"] == "image":
        return load_image(seg["img"], nframes, seg["kb"])
    if seg["kind"] == "still":
        base = decode(seg["clip"], seg["src"], 1.0, 1, single=True)[0].copy()
        # overlays belong to the card, so they zoom with it
        base = apply_overlays(base, [v for v in seg.get("ov") or [] if v[4] != "screen"], 0)
        z0, z1 = seg["zoom"]
        out = []
        for i in range(nframes):
            p = ease_out(i / max(1, nframes - 1))
            out.append(zoom(base, z0 + (z1 - z0) * p, (0.45, 0.45)))
        return out
    return decode(seg["clip"], seg["src"], seg["sp"], nframes, seg.get("ct", 0.0))


def render(preview=False, only=None):
    overlays()
    segs = timeline()
    for s in segs:  # the user's logo badge over the Gemini sparkle, on every clip
        if s["kind"] in ("clip", "still"):
            s["ov"] = [watermark_cover(s.get("ct", 0.0))] + list(s.get("ov") or [])
    os.makedirs(OUTDIR, exist_ok=True)
    total = int(round(END * FPS))
    starts = [int(round(s["t"] * FPS)) for s in segs] + [total]
    if preview:
        picks = sorted(set(int(x) for x in np.linspace(0, total - 1, 30)))
    out_path = os.path.join(BUILD, "video.mp4")
    enc = None
    if not preview:
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                                "-preset", "slow", "-crf", "19", "-maxrate", "16M", "-bufsize", "32M",
                                "-pix_fmt", "yuv420p", out_path],
                               stdin=subprocess.PIPE)
    thumbs, prev_tail = [], None
    fi = 0
    if only:
        want = [int(round(t * FPS)) for t in only]
        shots = []
        for k, seg in enumerate(segs):
            n = starts[k + 1] - starts[k]
            hits = [w for w in want if starts[k] <= w < starts[k + 1]]
            if not hits:
                continue
            frames = segment_frames(seg, n)
            for w in hits:
                j = w - starts[k]; t = w / FPS
                fr = frames[j].copy()
                if seg["kind"] != "still":
                    fr = apply_overlays(fr, seg.get("ov"), t)
                else:
                    fr = apply_overlays(fr, [v for v in seg["ov"] if v[4] == "screen"], t)
                shots.append(cv2.resize(finish(fr, w), (540, 960), interpolation=cv2.INTER_AREA))
        p = os.path.join(BUILD, "check.jpg")
        Image.fromarray(np.hstack(shots)).save(p, quality=90); print("check ->", p)
        return
    for k, seg in enumerate(segs):
        n = starts[k + 1] - starts[k]
        frames = segment_frames(seg, n)
        xf = int(round(seg.get("xfade", 0) * FPS))
        for j, fr in enumerate(frames):
            t = (starts[k] + j) / FPS
            fr = fr.copy()
            if seg["kind"] != "still":
                fr = apply_overlays(fr, seg.get("ov"), t)
            else:  # screen-fixed overlays on a zooming still
                fr = apply_overlays(fr, [v for v in seg["ov"] if v[4] == "screen"], t)
            if seg.get("drift"):
                fr = zoom(fr, 1.0 + (seg["drift"] - 1.0) * ease_out(j / max(1, n - 1)), (0.5, 0.45))
            if seg.get("punch", True) and seg["kind"] != "still" and j < 6:
                fr = zoom(fr, 1.0 + 0.055 * (1 - ease_out(j / 6)))
            if xf and j < xf and prev_tail is not None:
                a = (j + 1) / (xf + 1)
                fr = (fr.astype(np.float32) * a + prev_tail.astype(np.float32) * (1 - a)).astype(np.uint8)
            fr = finish(fr, fi)
            if preview:
                if fi in picks:
                    thumbs.append(cv2.resize(fr, (270, 480), interpolation=cv2.INTER_AREA))
            else:
                enc.stdin.write(fr.tobytes())
            fi += 1
        prev_tail = frames[-1]
        print(f"  [{k+1:2d}/{len(segs)}] {seg['t']:6.2f}s  {seg.get('clip', seg.get('img'))}", flush=True)
    if preview:
        rows = [np.hstack(thumbs[i:i + 10]) for i in range(0, 30, 10)]
        sheet = np.vstack(rows)
        p = os.path.join(OUTDIR, "zomato-economy-contact.jpg")
        Image.fromarray(sheet).save(p, quality=88)
        print("contact sheet ->", p)
        return
    enc.stdin.close(); enc.wait()
    mix = os.path.join(BUILD, "mix.wav")
    final = os.path.join(OUTDIR, "zomato-economy.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out_path, "-i", mix, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest",
                    "-movflags", "+faststart", final], check=True)
    print("final ->", final)


if __name__ == "__main__":
    only = None
    if "--frames" in sys.argv:
        only = [float(x) for x in sys.argv[sys.argv.index("--frames") + 1].split(",")]
    render(preview="--preview" in sys.argv, only=only)
