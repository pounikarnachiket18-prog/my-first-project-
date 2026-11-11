#!/usr/bin/env python3
"""
Builds two graphics for the 9:16 Kingfisher reel (run from this folder):

  clips/logo-card.mp4   4 s, 1080x1920, 24 fps ending card. Starts on the TREE clip's
                        exact last frame (the yellow leaf), opens into cream paper, then the
                        round M logo pops in with "MINDSET MODE | INDIA |" and the tagline.
  title.png             transparent 1080x1920 "KINGFISHER" title shown in the first second.
"""
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, N = 1080, 1920, 24, 96
CREAM = (240, 236, 218)
RED = (205, 38, 40)
NAVY = (29, 42, 68)
TEAL = (116, 190, 204)
F_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
F_BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
F_SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
F_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
rng = np.random.default_rng(3)


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def back_out(x, s=1.7):
    x = min(max(x, 0.0), 1.0) - 1
    return x * x * ((s + 1) * x + s) + 1


def prog(f, a, b):
    return min(max((f - a) / (b - a), 0.0), 1.0)


def paper():
    """Cream paper with fine grain, light fibres and a soft vignette."""
    base = np.ones((H, W, 3)) * np.array(CREAM, float)
    grain = rng.normal(0, 3.2, (H, W, 1))
    blotch = np.asarray(Image.fromarray(rng.integers(0, 255, (H // 24, W // 24), dtype=np.uint8))
                        .resize((W, H), Image.BICUBIC), float)[..., None]
    img = base + grain + (blotch - 128) * 0.035
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2)
    img *= (1 - 0.10 * np.clip(d, 0, 1) ** 2)[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")


def shadow_of(layer, blur=14, off=(0, 10), alpha=0.35):
    a = layer.split()[-1].filter(ImageFilter.GaussianBlur(blur))
    sh = Image.new("RGBA", layer.size, (40, 30, 20, 0))
    sh.putalpha(a.point(lambda v: int(v * alpha)))
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    out.alpha_composite(sh, off)
    return out


def text_layer(text, font, fill, tracking=0):
    """Full-canvas transparent layer with centred text (optional letter spacing)."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    widths = [d.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    return lay, d, total, widths


def draw_centered(text, font, fill, y, tracking=0):
    lay, d, total, widths = text_layer(text, font, fill, tracking)
    x = (W - total) / 2
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=font, fill=fill, anchor="ls")
        x += w + tracking
    return lay


def place(canvas, layer, alpha=1.0, dy=0.0, with_shadow=True):
    if alpha <= 0:
        return
    lay = layer
    if dy:
        moved = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        moved.alpha_composite(lay, (0, int(dy)))
        lay = moved
    if alpha < 1:
        lay = lay.copy()
        lay.putalpha(lay.split()[-1].point(lambda v: int(v * alpha)))
    if with_shadow:
        canvas.alpha_composite(shadow_of(lay, blur=10, off=(0, 6), alpha=0.28))
    canvas.alpha_composite(lay)


def leaf_frame():
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(HERE, "clips", "tree.mp4"),
                          "-vf", f"select=eq(n\\,95),scale={W}:{H}:flags=lanczos", "-frames:v", "1",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return Image.frombytes("RGB", (W, H), out).convert("RGBA")


def logo_card():
    first = leaf_frame()
    bg = paper()
    logo_src = Image.open(os.path.join(HERE, "watermark.png")).convert("RGBA")
    t_mindset = draw_centered("MINDSET MODE", ImageFont.truetype(F_SERIF, 106), NAVY, 1135, tracking=3)
    t_india = draw_centered("|  INDIA  |", ImageFont.truetype(F_BOLD, 82), RED, 1262, tracking=6)
    t_tag = draw_centered("STORIES BEHIND THE EMPIRE.", ImageFont.truetype(F_SEMI, 40), NAVY, 1395, tracking=5)
    rule = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(rule).rectangle((W / 2 - 230, 1318, W / 2 + 230, 1323), fill=TEAL + (255,))

    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{N / FPS}",
                           "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-shortest", os.path.join(HERE, "clips", "logo-card.mp4")],
                          stdin=subprocess.PIPE)
    diag = (W ** 2 + H ** 2) ** 0.5 / 2
    for f in range(N):
        canvas = bg.copy()
        # 1) iris: cream paper opens out of the yellow leaf (paper-cut edge with a shadow)
        r = diag * ease_out(prog(f, 4, 26))
        if r < diag:
            mask = Image.new("L", (W, H), 255)
            ImageDraw.Draw(mask).ellipse((W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r), fill=0)
            top = first.copy()
            top.putalpha(mask)
            canvas.alpha_composite(shadow_of(top, blur=16, off=(0, 0), alpha=0.45))
            canvas.alpha_composite(top)
        # 2) round logo pops in
        s = back_out(prog(f, 16, 32))
        if s > 0.01:
            size = max(2, int(390 * s))
            lg = logo_src.resize((size, size), Image.LANCZOS)
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            lay.alpha_composite(lg, (int(W / 2 - size / 2), int(760 - size / 2)))
            canvas.alpha_composite(shadow_of(lay, blur=18, off=(0, 14), alpha=0.35))
            canvas.alpha_composite(lay)
        # 3) titles rise in one after another
        for layer, a, b in ((t_mindset, 28, 42), (t_india, 36, 50), (rule, 44, 56), (t_tag, 46, 60)):
            p = ease_out(prog(f, a, b))
            place(canvas, layer, alpha=p, dy=(1 - p) * 40, with_shadow=layer is not rule)
        ff.stdin.write(canvas.convert("RGB").tobytes())
    ff.stdin.close()
    ff.wait()
    print("wrote clips/logo-card.mp4")


def title():
    font = ImageFont.truetype(F_BLACK, 150)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    txt, y = "KINGFISHER", 560
    tw = d.textlength(txt, font=font)
    while tw > W - 90:
        font = ImageFont.truetype(F_BLACK, font.size - 4)
        tw = d.textlength(txt, font=font)
    d.text((W / 2, y), txt, font=font, fill=RED + (255,), anchor="ms",
           stroke_width=12, stroke_fill=(255, 250, 238, 255))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(shadow_of(lay, blur=14, off=(0, 12), alpha=0.40))
    out.alpha_composite(lay)
    out.save(os.path.join(HERE, "title.png"))
    print("wrote title.png", font.size)


if __name__ == "__main__":
    title()
    logo_card()
