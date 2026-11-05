#!/usr/bin/env python3
"""
Zomato Economy reel: assembles the user's clips on the Hindi voiceover, in 4K.

  python3 vo.py        # tighten the voiceover to 75 s       -> build/vo_tight.wav
  python3 sr_cache.py  # AI-upscale the clips once (~1 h CPU)  -> media_sr/
  python3 audio.py     # music + memes + sound design + mix    -> build/mix.wav
  python3 build.py     # picture + mux -> ../../output/zomato-economy-4k.mp4
  python3 build.py --preview           # 30-frame contact sheet
  python3 build.py --frames 12.5,61.9  # single frames -> build/check.jpg

Cut times are written on the 75 s voiceover grid and moved onto the final
reel with timing.sh(), which adds the short pauses for the spoken memes.
Every layout number is in 1080x1920 design pixels and scaled by K.
Clean paper banners cover the AI titles that were wrong for this story
("Doomscrolling", the "Vox" logo, garbled numbers); the Gemini sparkle is
covered by the Mindset Mode badge.
"""
import os, subprocess, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from timing import sh, END

HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.join(HERE, "media")
MEDIA_SR = os.path.join(HERE, "media_sr")
BUILD = os.path.join(HERE, "build")
OUTDIR = os.path.abspath(os.path.join(HERE, "..", "..", "output"))
FONT_BIG = os.path.join(HERE, "fonts", "Anton-Regular.ttf")
FONT_SUB = os.path.join(HERE, "fonts", "Oswald-Bold.ttf")
W, H, FPS = 2160, 3840, 30
K = W / 1080


def px(v):
    return int(round(v * K))


INK = (29, 24, 22)
RED = (158, 24, 30)
PAPER = (238, 229, 211)
rng = np.random.default_rng(11)


# ------------------------------------------------------------------ overlays
def _paper(w, h):
    base = np.zeros((h, w, 3), np.float32) + PAPER
    base += rng.normal(0, 5, (h, w, 1))
    fib = cv2.GaussianBlur(rng.normal(0, 14, (h, w)).astype(np.float32), (0, 0), 6 * K)
    base += fib[..., None]
    return np.clip(base, 0, 255).astype(np.uint8)


def banner(line1, line2=None, cover_h=300, accent=None):
    """Full-width torn-paper strip at the top of the frame (cover_h in design px)."""
    cover_h = px(cover_h)
    total = cover_h + px(70)
    img = Image.new("RGBA", (W, total), (0, 0, 0, 0))
    xs = np.arange(0, W + px(18), px(18))
    ys = cover_h + rng.uniform(-px(14), px(14), len(xs))
    poly = [(0, 0), (W, 0)] + [(int(x), int(y)) for x, y in zip(xs[::-1], ys[::-1])]
    mask = Image.new("L", (W, total), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    shadow = Image.new("RGBA", (W, total), (0, 0, 0, 255))
    shadow.putalpha(mask.filter(ImageFilter.GaussianBlur(px(14))).point(lambda v: int(v * 0.45)))
    img.alpha_composite(shadow, (0, px(14)))
    paper = Image.fromarray(_paper(W, total)).convert("RGBA")
    paper.putalpha(mask)
    img.alpha_composite(paper)
    d = ImageDraw.Draw(img)
    d.line([(px(60), cover_h - px(46)), (W - px(60), cover_h - px(46))], fill=INK, width=px(3))
    d.line([(px(60), cover_h - px(38)), (W - px(60), cover_h - px(38))], fill=INK, width=max(1, px(1)))
    size = px(150)
    while size > px(40):
        f1 = ImageFont.truetype(FONT_BIG, size)
        if d.textlength(line1, font=f1) <= W - px(120):
            break
        size -= px(4)
    asc = f1.getbbox(line1)
    block = (asc[3] - asc[1]) + (px(70) if line2 else 0)
    top = max(px(24), (cover_h - px(50) - block) // 2) - asc[1]
    x = (W - d.textlength(line1, font=f1)) / 2
    if accent and accent in line1:
        pre, post = line1.split(accent, 1)
        for part, col in ((pre, INK), (accent, RED), (post, INK)):
            d.text((x, top), part, font=f1, fill=col)
            x += d.textlength(part, font=f1)
    else:
        d.text((x, top), line1, font=f1, fill=INK)
    if line2:
        f2 = ImageFont.truetype(FONT_SUB, px(48))
        y2 = top + asc[3] + px(14)
        tw = d.textlength(line2, font=f2)
        d.rectangle([(W - tw) / 2 - px(18), y2 - px(2), (W + tw) / 2 + px(18), y2 + px(62)], fill=RED)
        d.text(((W - tw) / 2, y2), line2, font=f2, fill=PAPER)
    return np.array(img)


def tag(text, size=64, angle=0.0, color=RED, fg=PAPER, font=FONT_SUB):
    f = ImageFont.truetype(font, px(size))
    tw = int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(text, font=f))
    bb = f.getbbox(text)
    padx, pady, m = px(34), px(16), px(30)
    w, h = tw + padx * 2, (bb[3] - bb[1]) + pady * 2
    img = Image.new("RGBA", (w + 2 * m, h + 2 * m), (0, 0, 0, 0))
    sh_ = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh_).rectangle([m, m + px(6), m + w, m + px(6) + h], fill=(0, 0, 0, 120))
    img.alpha_composite(sh_.filter(ImageFilter.GaussianBlur(px(8))))
    d = ImageDraw.Draw(img)
    d.rectangle([m, m, m + w, m + h], fill=color)
    d.text((m + padx, m + pady - bb[1]), text, font=f, fill=fg)
    if angle:
        img = img.rotate(angle, resample=Image.BICUBIC, expand=True)
    return np.array(img)


def card_patch():
    """Covers 'PREMIUM VISUAL JOURNALISM / GROWTH TRAJECTORY' on the 3,879 card."""
    w, h = px(1000), px(440)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    paper = Image.fromarray(_paper(w, h)).convert("RGBA")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rectangle([px(40), px(30), w - px(40), h - px(30)], fill=255)
    paper.putalpha(m.filter(ImageFilter.GaussianBlur(px(3))))
    img.alpha_composite(paper)
    t = Image.fromarray(tag("FOOD DELIVERY  ·  Q2 FY27", 66))
    img.alpha_composite(t, ((w - t.width) // 2, (h - t.height) // 2))
    return np.array(img.rotate(4.5, resample=Image.BICUBIC, expand=False))


_logo_cache = {}
def logo_badge(d):
    """The user's round red M logo as a small badge (thin cream ring + soft shadow)."""
    d = int(round(d))
    if d in _logo_cache:
        return _logo_cache[d]
    src = Image.open(os.path.join(MEDIA, "logo_source.png")).convert("RGB")
    cx, cy, r = 1193.5, 833.5, 833.5
    k = 4
    D = d * k
    pad = int(D * 0.16)
    canvas = Image.new("RGBA", (D + 2 * pad, D + 2 * pad), (0, 0, 0, 0))
    m = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(m).ellipse([pad, pad + int(D * 0.05), pad + D, pad + D + int(D * 0.05)], fill=150)
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 255))
    shadow.putalpha(m.filter(ImageFilter.GaussianBlur(D * 0.05)).point(lambda v: int(v * 0.7)))
    canvas.alpha_composite(shadow)
    ring = int(D * 0.045)
    ImageDraw.Draw(canvas).ellipse([pad, pad, pad + D, pad + D], fill=PAPER + (255,))
    inner = D - 2 * ring
    dm = Image.new("L", (inner, inner), 0)
    ImageDraw.Draw(dm).ellipse([0, 0, inner - 1, inner - 1], fill=255)
    disc = src.crop((int(cx - r), int(cy - r), int(cx + r), int(cy + r))).resize((inner, inner), Image.LANCZOS)
    disc = disc.convert("RGBA"); disc.putalpha(dm)
    canvas.alpha_composite(disc, (pad + ring, pad + ring))
    _logo_cache[d] = np.array(canvas.resize((canvas.width // k, canvas.height // k), Image.LANCZOS))
    return _logo_cache[d]


# Gemini/Veo sparkle position (relative to the frame) and badge diameter (fraction of width)
SPARK_VIDEO = (0.8319, 0.9053, 0.066)
SPARK_IMAGE = (0.8743, 0.9295, 0.068)


def watermark_cover(ct=0.0, spark=SPARK_VIDEO, w=W, h=H):
    x, y, dfr = spark
    x = (x - ct / 2) / (1 - ct)
    y = (y - ct) / (1 - ct)
    d = dfr * w / (1 - ct)
    b = logo_badge(d)
    return (b, x * w - b.shape[1] / 2, y * h - b.shape[0] / 2 + 0.01 * d, None, "static")


# ------------------------------------------------------------------ timeline
def T(name, t, src=0.0, sp=1.0, **kw):
    return dict(kind="clip", clip=name, t=sh(t), src=src, sp=sp, **kw)


OV = {}
def overlays():
    OV["eco"] = banner("THE ZOMATO ECOSYSTEM", "CUSTOMER  ·  RESTAURANT  ·  DELIVERY", 300, "ZOMATO")
    OV["commission"] = banner("COMMISSION", "ON EVERY ORDER", 330, "COMMISSION")
    OV["customers"] = banner("NEW CUSTOMERS", "+ MORE ORDERS", 300, "NEW")
    OV["profit"] = banner("NOT ALL OF IT IS PROFIT", None, 300, "PROFIT")
    OV["costs"] = banner("WHERE THE MONEY GOES", None, 200, "MONEY")
    OV["nov"] = banner("NET ORDER VALUE", "FOOD DELIVERY  ·  Q2 FY27", 540, "NET ORDER")
    OV["rev"] = banner("ADJUSTED REVENUE", None, 250, "REVENUE")
    OV["ebitda"] = tag("ADJUSTED EBITDA", 70)
    OV["q2"] = tag("Q2  ·  FY27", 76, color=PAPER, fg=INK)
    OV["patch"] = card_patch()


def timeline():
    o = OV
    return [
        T("hook_zomato", 0.00, 0.20, 1.60, ct=0.12, punch=False),
        T("order_500", 2.33, 0.00, 0.88),
        T("hook_zomato", 6.93, 4.00, 1.00, ct=0.12),                 # runs on into the "huh?" pause
        dict(kind="image", img="feast", t=sh(9.93), kb=(1.0, 1.13, -0.02, 0.06)),
        T("chef", 13.54, 0.90, 1.00),
        T("ecosystem_phone", 14.78, 0.00, 1.00, ov=[(o["eco"], 0, 0, None, "static")]),
        T("ecosystem_circle", 16.90, 1.50, 1.00),
        T("owner_orders", 19.36, 0.00, 1.00, ov=[(o["commission"], 0, 0, sh(20.30), "drop")]),
        T("owner_commission", 23.30, 2.40, 0.82, ov=[(o["customers"], 0, 0, None, "static")]),
        T("mumbai_rider", 25.25, 0.00, 0.93),
        T("checkout", 27.30, 0.00, 1.00),
        T("rider_night_receipt", 29.20, 5.30, 1.00),                # + screaming-cat pause
        T("hidden_cost", 31.72, 0.00, 0.86),
        T("ads", 34.05, 0.00, 1.03),
        T("gold", 37.90, 0.00, 0.85),
        T("rider_night_receipt", 42.62, 0.00, 0.80),
        T("coins_jar", 44.61, 0.00, 1.00, ov=[(o["profit"], 0, 0, sh(45.80), "drop")]),
        T("expenses", 48.29, 0.00, 0.74, ov=[(o["costs"], 0, 0, None, "static")]),  # + sobbing pause
        T("rider_night_receipt", 52.83, 1.60, 1.00, ov=[(o["q2"], px(70), px(1450), sh(53.00), "slap")]),
        T("map_11445", 55.00, 0.00, 0.62, ov=[(o["nov"], 0, 0, None, "static")]),
        T("map_11445", 57.95, 3.00, 1.00, drift=1.06, ov=[(o["nov"], 0, 0, None, "static")]),  # + scream pause
        T("bars_3879", 60.58, 1.45, 0.65, ov=[(o["rev"], 0, 0, sh(60.62), "drop")]),
        dict(kind="still", clip="bars_3879", t=sh(61.88), src=3.60, zoom=(1.0, 1.07),
             ov=[(o["patch"], px(30), px(1190), None, "static"), (o["rev"], 0, 0, None, "screen")]),
        T("bar_627", 63.78, 0.60, 1.00, ov=[(o["ebitda"], None, px(300), sh(63.90), "slap")]),
        T("door_gift", 67.00, 1.90, 0.93, ct=0.03),
        T("gift_open", 69.26, 1.75, 0.78),
        T("brand_card", 72.13, 0.55, 1.00, xfade=0.22, punch=False, drift=1.04),
    ]


# ------------------------------------------------------------------ frame sources (streamed)
def decode(clip, src, sp, nframes, ct=0.0):
    path = os.path.join(MEDIA_SR, clip + ".mp4")
    src_dur = nframes / FPS * sp + 0.25
    crop = f"crop=iw*{1-ct:.4f}:ih*{1-ct:.4f}:iw*{ct/2:.4f}:ih*{ct:.4f}," if ct else ""
    fr = "fps=30" if sp >= 0.95 else "framerate=fps=30:interp_start=0:interp_end=255:scene=100"
    vf = f"setpts=(PTS-STARTPTS)/{sp},{fr},{crop}scale={W}:{H}:flags=lanczos,cas=0.22,format=rgb24"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{src:.3f}", "-i", path, "-t", f"{src_dur:.3f}",
                          "-vf", vf, "-an", "-f", "rawvideo", "-"], stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL)
    size, last, eof = W * H * 3, None, False
    for _ in range(nframes):
        buf = b"" if eof else p.stdout.read(size)
        if len(buf) == size:
            last = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        else:
            eof = True
        if last is None:
            raise RuntimeError(f"no frames from {clip} @ {src}")
        yield last  # holds the last frame (freeze) if the clip runs out
    p.stdout.close(); p.kill(); p.wait()


def single(clip, src):
    vf = f"scale={W}:{H}:flags=lanczos,cas=0.22,format=rgb24"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{src:.3f}", "-i", os.path.join(MEDIA_SR, clip + ".mp4"),
                          "-frames:v", "1", "-vf", vf, "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W, 3).copy()


def image_frames(name, nframes, kb):
    z0, z1, dx, dy = kb
    im = Image.open(os.path.join(MEDIA_SR, name + ".png")).convert("RGB")
    big = np.array(im.resize((int(W * 1.2), int(W * 1.2 * im.height / im.width)), Image.LANCZOS))
    bh, bw = big.shape[:2]
    b, x, y, _, _ = watermark_cover(0.0, SPARK_IMAGE, bw, bh)
    big = composite(big, b, x, y)
    for i in range(nframes):
        p = i / max(1, nframes - 1)
        e = p * p * (3 - 2 * p)
        s_ = max(W / bw, H / bh) * (z0 + (z1 - z0) * e)
        cx = bw / 2 + dx * bw * (e - 0.5)
        cy = bh / 2 + dy * bh * (e - 0.5)
        M = np.float32([[s_, 0, W / 2 - s_ * cx], [0, s_, H / 2 - s_ * cy]])
        yield cv2.warpAffine(big, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


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
            composite(frame, rgba, x, y - (1 - back_out(p)) * (h + px(40)))
        elif mode == "slap":
            sc = 1.0 + 0.45 * (1 - ease_out(p))
            nw, nh = w * sc, h * sc
            composite(frame, rgba, x - (nw - w) / 2, y - (nh - h) / 2, alpha=min(1, p * 3), scale=sc)
    return frame


_vig = None
def finish(frame, i):
    """Vignette + fine film grain (ties the different AI clips together)."""
    global _vig
    if _vig is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
        _vig = cv2.merge([(1 - 0.28 * np.clip(r - 0.55, 0, 1) ** 1.6).astype(np.float32)] * 3)
    f = cv2.multiply(frame.astype(np.float32), _vig)
    g = np.random.default_rng(i).normal(0, 4.2, (H // 3, W // 3)).astype(np.float32)
    g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)
    f = cv2.add(f, cv2.merge([g, g, g]))
    return np.clip(f, 0, 255).astype(np.uint8)


# ------------------------------------------------------------------ render
def segment_frames(seg, nframes):
    if seg["kind"] == "image":
        return image_frames(seg["img"], nframes, seg["kb"])
    if seg["kind"] == "still":
        base = single(seg["clip"], seg["src"])
        base = apply_overlays(base, [v for v in seg["ov"] if v[4] != "screen"], 0)  # stuck to the card
        z0, z1 = seg["zoom"]
        return (zoom(base, z0 + (z1 - z0) * ease_out(i / max(1, nframes - 1)), (0.45, 0.45)) for i in range(nframes))
    return decode(seg["clip"], seg["src"], seg["sp"], nframes, seg.get("ct", 0.0))


def process(seg, fr, j, n, t):
    fr = fr.copy()
    if seg["kind"] != "still":
        fr = apply_overlays(fr, seg.get("ov"), t)
    else:  # screen-fixed overlays on a zooming still
        fr = apply_overlays(fr, [v for v in seg["ov"] if v[4] == "screen"], t)
    if seg.get("drift"):
        fr = zoom(fr, 1.0 + (seg["drift"] - 1.0) * ease_out(j / max(1, n - 1)), (0.5, 0.45))
    if seg.get("punch", True) and seg["kind"] != "still" and j < 6:
        fr = zoom(fr, 1.0 + 0.055 * (1 - ease_out(j / 6)))
    return fr


def render(preview=False, only=None):
    overlays()
    segs = timeline()
    for s in segs:  # the user's logo badge over the Gemini sparkle, on every clip
        if s["kind"] in ("clip", "still"):
            s["ov"] = [watermark_cover(s.get("ct", 0.0))] + list(s.get("ov") or [])
    os.makedirs(OUTDIR, exist_ok=True)
    total = int(round(END * FPS))
    starts = [int(round(s["t"] * FPS)) for s in segs] + [total]
    if only:
        want = [int(round(t * FPS)) for t in only]
        shots = []
        for k, seg in enumerate(segs):
            n = starts[k + 1] - starts[k]
            hits = [w for w in want if starts[k] <= w < starts[k + 1]]
            if not hits:
                continue
            for j, fr in enumerate(segment_frames(seg, n)):
                w = starts[k] + j
                if w in hits:
                    shots.append(cv2.resize(finish(process(seg, fr, j, n, w / FPS), w), (540, 960),
                                            interpolation=cv2.INTER_AREA))
                if w >= max(hits):
                    break
        p = os.path.join(BUILD, "check.jpg")
        Image.fromarray(np.hstack(shots)).save(p, quality=90); print("check ->", p)
        return
    picks = set(int(x) for x in np.linspace(0, total - 1, 30)) if preview else set()
    out_path = os.path.join(BUILD, "video4k.mp4")
    enc = None
    if not preview:
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                                "-preset", "medium", "-crf", "18", "-maxrate", "45M", "-bufsize", "90M",
                                "-profile:v", "high", "-level", "5.1", "-pix_fmt", "yuv420p", out_path],
                               stdin=subprocess.PIPE)
    thumbs, prev_tail, fi = [], None, 0
    for k, seg in enumerate(segs):
        n = starts[k + 1] - starts[k]
        xf = int(round(seg.get("xfade", 0) * FPS))
        last = None
        for j, fr in enumerate(segment_frames(seg, n)):
            last = fr
            if preview and fi not in picks:
                fi += 1
                continue
            out = process(seg, fr, j, n, (starts[k] + j) / FPS)
            if xf and j < xf and prev_tail is not None:
                a = (j + 1) / (xf + 1)
                out = cv2.addWeighted(out, a, prev_tail, 1 - a, 0)
            out = finish(out, fi)
            if preview:
                thumbs.append(cv2.resize(out, (270, 480), interpolation=cv2.INTER_AREA))
            else:
                enc.stdin.write(out.tobytes())
            fi += 1
        prev_tail = process(seg, last, n - 1, n, (starts[k + 1] - 1) / FPS) if last is not None else None
        print(f"  [{k+1:2d}/{len(segs)}] {seg['t']:6.2f}s  {seg.get('clip', seg.get('img'))}", flush=True)
    if preview:
        sheet = np.vstack([np.hstack(thumbs[i:i + 10]) for i in range(0, 30, 10)])
        p = os.path.join(OUTDIR, "zomato-economy-contact.jpg")
        Image.fromarray(sheet).save(p, quality=88); print("contact sheet ->", p)
        return
    enc.stdin.close(); enc.wait()
    final = os.path.join(OUTDIR, "zomato-economy-4k.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out_path, "-i", os.path.join(BUILD, "mix.wav"),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
                    "-shortest", "-movflags", "+faststart", final], check=True)
    print("final ->", final)


if __name__ == "__main__":
    only = None
    if "--frames" in sys.argv:
        only = [float(x) for x in sys.argv[sys.argv.index("--frames") + 1].split(",")]
    render(preview="--preview" in sys.argv, only=only)
