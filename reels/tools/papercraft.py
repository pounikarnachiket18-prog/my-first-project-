"""
Papercraft scene kit: draws cut-paper dioramas (layered paper pieces with grain,
bevelled cut edges and soft drop shadows) for the house reel style when no AI
image generator is available. Canvas is 1280x2276 (9:16, with headroom for the
camera moves in paper_reel.py).

    from papercraft import Paper, C
    p = Paper(); p.gradient(C.kraft, C.kraft_dk)
    p.rect(100, 1500, 1180, 1700, C.wood, depth=2)
    p.mascot(640, 1500, 700)
    p.save("images/s07.png")
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

PW, PH = 1280, 2276
SS = 2  # supersampling for clean paper edges
_FONTS = {
    "sans": ["/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    "serif": ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"],
    "mono": ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"],
}


def font(size, kind="sans"):
    for p in _FONTS[kind]:
        if os.path.exists(p):
            return ImageFont.truetype(p, int(size))
    return ImageFont.load_default()


class C:  # palette
    kraft = (200, 160, 106); kraft_dk = (150, 112, 70); kraft_lt = (222, 192, 146)
    cream = (243, 230, 204); paper = (246, 242, 232); white = (252, 250, 245)
    mustard = (233, 185, 73); gold = (226, 172, 52); gold_lt = (250, 214, 110)
    sky = (143, 201, 232); sky_dk = (92, 150, 196)
    brick = (196, 72, 58); red = (214, 52, 45); orange = (232, 116, 59)
    navy = (34, 50, 92); night = (22, 30, 62); night2 = (44, 52, 98)
    teal = (63, 143, 138); green = (76, 170, 86); green_dk = (44, 122, 60)
    grey = (150, 150, 146); grey_dk = (96, 98, 102); grey_lt = (196, 196, 190)
    wood = (156, 102, 58); wood_dk = (112, 70, 38)
    skin = (226, 178, 132); hair = (52, 38, 30); suit = (46, 52, 70); black = (28, 28, 32)
    window = (255, 214, 120)


def _noise(w, h, seed):
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    for scale, amp in ((2, 0.5), (6, 0.3), (24, 0.2)):
        small = rng.random((h // scale + 2, w // scale + 2)).astype(np.float32)
        im = Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        out += np.asarray(im, np.float32) / 255 * amp
    # paper fibres
    fib = rng.random((h, w)) > 0.9985
    fimg = Image.fromarray((fib * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    out -= np.asarray(fimg, np.float32) / 255 * 0.6
    return out


class Paper:
    def __init__(self, w=PW, h=PH, seed=7):
        self.w, self.h = w, h
        self.img = Image.new("RGBA", (w, h), (0, 0, 0, 255))
        self.grain = _noise(w, h, seed)  # ~0..1

    # ------------------------------------------------------------ core piece
    def _mask(self, draw_fn, bbox):
        x0, y0, x1, y1 = [int(v) for v in bbox]
        pad = 4
        bw, bh = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
        m = Image.new("L", (bw * SS, bh * SS), 0)
        draw_fn(ImageDraw.Draw(m), lambda x, y: ((x - x0 + pad) * SS, (y - y0 + pad) * SS), SS)
        return m.resize((bw, bh), Image.LANCZOS), (x0 - pad, y0 - pad)

    def _piece(self, mask, off, color, depth=1.0, grain=1.0, bevel=True, shadow=True, opacity=1.0):
        ox, oy = off
        if shadow and depth > 0:
            blur = 4 + 7 * depth
            sx, sy = int(3 * depth), int(6 * depth)
            pad = int(blur * 2)
            sm = Image.new("L", (mask.width + 2 * pad, mask.height + 2 * pad), 0)
            sm.paste(mask, (pad, pad))
            sm = sm.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * 0.5 * opacity))
            sh = Image.new("RGBA", sm.size, (20, 10, 0, 0)); sh.putalpha(sm)
            self._paste_clip(sh, ox - pad + sx, oy - pad + sy)
        # textured fill
        arr = np.zeros((mask.height, mask.width, 4), np.float32)
        g = self._grain_crop(ox, oy, mask.width, mask.height)
        shade = 1 + (g - 0.5) * 0.16 * grain
        if bevel:
            a = np.asarray(mask, np.float32) / 255
            sh_ = np.roll(np.roll(a, 3, 0), 3, 1)
            hi = np.clip(a - np.roll(np.roll(a, -3, 0), -3, 1), 0, 1)   # bottom-right edge -> darker
            lo = np.clip(a - sh_, 0, 1)                                    # top-left edge -> lighter
            shade = shade + lo * 0.16 - hi * 0.22
        for i in range(3):
            arr[..., i] = np.clip(color[i] * shade, 0, 255)
        arr[..., 3] = np.asarray(mask, np.float32) * opacity
        self._paste_clip(Image.fromarray(arr.astype(np.uint8), "RGBA"), ox, oy)

    def _grain_crop(self, x, y, w, h):
        out = np.full((h, w), 0.5, np.float32)
        gx0, gy0 = max(0, x), max(0, y)
        gx1, gy1 = min(self.w, x + w), min(self.h, y + h)
        if gx1 > gx0 and gy1 > gy0:
            out[gy0 - y:gy1 - y, gx0 - x:gx1 - x] = self.grain[gy0:gy1, gx0:gx1]
        return out

    def _paste_clip(self, im, x, y):
        x, y = int(x), int(y)
        cx0, cy0 = max(0, -x), max(0, -y)
        cx1, cy1 = min(im.width, self.w - x), min(im.height, self.h - y)
        if cx1 <= cx0 or cy1 <= cy0:
            return
        self.img.alpha_composite(im.crop((cx0, cy0, cx1, cy1)), (x + cx0, y + cy0))

    # ------------------------------------------------------------ primitives
    def gradient(self, top, bottom, y0=0, y1=None):
        y1 = self.h if y1 is None else y1
        t = np.linspace(0, 1, y1 - y0)[:, None, None]
        col = (np.array(top) * (1 - t) + np.array(bottom) * t)
        g = self.grain[y0:y1, :, None]
        col = np.clip(col * (1 + (g - 0.5) * 0.12), 0, 255)
        arr = np.concatenate([np.broadcast_to(col, (y1 - y0, self.w, 3)), np.full((y1 - y0, self.w, 1), 255)], 2)
        self.img.paste(Image.fromarray(arr.astype(np.uint8), "RGBA"), (0, y0))

    def rect(self, x0, y0, x1, y1, color, r=0, depth=1.0, **kw):
        m, off = self._mask(lambda d, P, s: d.rounded_rectangle((*P(x0, y0), *P(x1, y1)), radius=r * s, fill=255), (x0, y0, x1, y1))
        self._piece(m, off, color, depth, **kw)

    def ellipse(self, cx, cy, rx, ry, color, depth=1.0, **kw):
        m, off = self._mask(lambda d, P, s: d.ellipse((*P(cx - rx, cy - ry), *P(cx + rx, cy + ry)), fill=255), (cx - rx, cy - ry, cx + rx, cy + ry))
        self._piece(m, off, color, depth, **kw)

    def poly(self, pts, color, depth=1.0, **kw):
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        m, off = self._mask(lambda d, P, s: d.polygon([P(x, y) for x, y in pts], fill=255), (min(xs), min(ys), max(xs), max(ys)))
        self._piece(m, off, color, depth, **kw)

    def ring(self, cx, cy, r, width, color, depth=0.8, **kw):
        def fn(d, P, s):
            d.ellipse((*P(cx - r, cy - r), *P(cx + r, cy + r)), fill=255)
            d.ellipse((*P(cx - r + width, cy - r + width), *P(cx + r - width, cy + r - width)), fill=0)
        m, off = self._mask(fn, (cx - r, cy - r, cx + r, cy + r))
        self._piece(m, off, color, depth, **kw)

    def line(self, pts, color, width=6, depth=0.4, **kw):
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        m, off = self._mask(lambda d, P, s: d.line([P(x, y) for x, y in pts], fill=255, width=int(width * s), joint="curve"),
                            (min(xs) - width, min(ys) - width, max(xs) + width, max(ys) + width))
        self._piece(m, off, color, depth, bevel=False, **kw)

    def curve(self, a, b, sag, color, width=6, depth=0.4):
        pts = []
        for i in range(41):
            t = i / 40
            x = a[0] + (b[0] - a[0]) * t
            y = a[1] + (b[1] - a[1]) * t + math.sin(t * math.pi) * sag
            pts.append((x, y))
        self.line(pts, color, width, depth)
        return pts

    def text(self, x, y, s, size, color, kind="sans", anchor="mm", depth=0.8, rot=0, **kw):
        f = font(size, kind)
        l, t, r, b = f.getbbox(s, anchor=anchor)
        pad = size * 0.2
        bbox = (x + l - pad, y + t - pad, x + r + pad, y + b + pad)
        if rot:
            # render upright then rotate the mask
            w, h = int(r - l + 2 * pad), int(b - t + 2 * pad)
            m = Image.new("L", (w * SS, h * SS), 0)
            ImageDraw.Draw(m).text((w * SS / 2, h * SS / 2), s, font=font(size * SS, kind), fill=255, anchor="mm")
            m = m.rotate(rot, Image.BICUBIC, expand=True)
            m = m.resize((max(1, m.width // SS), max(1, m.height // SS)), Image.LANCZOS)
            self._piece(m, (int(x - m.width / 2), int(y - m.height / 2)), color, depth, **kw)
            return
        m, off = self._mask(lambda d, P, s_: d.text(P(x, y), s, font=font(size * SS, kind), fill=255, anchor=anchor), bbox)
        self._piece(m, off, color, depth, **kw)

    def glow(self, cx, cy, r, color, strength=0.6):
        g = Image.new("L", (int(r * 2), int(r * 2)), 0)
        ImageDraw.Draw(g).ellipse((r * 0.5, r * 0.5, r * 1.5, r * 1.5), fill=255)
        g = g.filter(ImageFilter.GaussianBlur(r * 0.35)).point(lambda v: int(v * strength))
        layer = Image.new("RGBA", g.size, color + (0,)); layer.putalpha(g)
        base = self.img.crop((int(cx - r), int(cy - r), int(cx + r), int(cy + r))).convert("RGB")
        add = ImageChops.add(base, ImageChops.multiply(Image.new("RGB", g.size, color), Image.merge("RGB", [g, g, g])))
        add.putalpha(255)
        self._paste_clip(add, cx - r, cy - r)

    def image(self, im, cx, bottom, height, flip=False, rot=0, depth=1.2):
        im = im.copy()
        if flip:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        k = height / im.height
        im = im.resize((max(1, int(im.width * k)), max(1, int(height))), Image.LANCZOS)
        if rot:
            im = im.rotate(rot, Image.BICUBIC, expand=True)
        x, y = int(cx - im.width / 2), int(bottom - im.height)
        a = im.getchannel("A")
        blur = 6 + 8 * depth
        pad = int(blur * 2)
        sm = Image.new("L", (im.width + 2 * pad, im.height + 2 * pad), 0); sm.paste(a, (pad, pad))
        sm = sm.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * 0.45))
        sh = Image.new("RGBA", sm.size, (20, 10, 0, 0)); sh.putalpha(sm)
        self._paste_clip(sh, x - pad + int(4 * depth), y - pad + int(8 * depth))
        self._paste_clip(im, x, y)
        return (x, y, k)

    # ------------------------------------------------------------ finishing
    def light(self, cx=0.5, cy=0.35, warm=(255, 200, 140), strength=0.35, vignette=0.45):
        yy, xx = np.mgrid[0:self.h, 0:self.w].astype(np.float32)
        d = np.sqrt(((xx / self.w - cx) * 1.0) ** 2 + ((yy / self.h - cy) * 0.6) ** 2)
        arr = np.asarray(self.img.convert("RGB"), np.float32)
        glow = np.clip(1 - d / 0.55, 0, 1)[..., None] ** 2
        arr = arr + glow * (np.array(warm) * strength * 0.35)
        vig = 1 - vignette * np.clip((d - 0.25) / 0.6, 0, 1)[..., None] ** 1.5
        arr = np.clip(arr * vig, 0, 255)
        self.img = Image.fromarray(arr.astype(np.uint8)).convert("RGBA")

    def dof(self, y_from, radius=6):
        """Soft depth of field: blur everything below/above a line (bottom foreground blur)."""
        b = self.img.filter(ImageFilter.GaussianBlur(radius))
        m = Image.new("L", (self.w, self.h), 0)
        d = ImageDraw.Draw(m)
        for i in range(120):
            d.rectangle((0, y_from + i * 3, self.w, self.h), fill=int(255 * min(1, i / 120)))
        self.img = Image.composite(b, self.img, m)

    def save(self, path):
        self.img.convert("RGB").save(path, quality=93)


# ---------------------------------------------------------------- props
def mascot_img(path):
    return Image.open(path).convert("RGBA")


def with_sunglasses(m):
    """Mascot cut-out (433x723 source) with black paper sunglasses over its eyes."""
    m = m.copy()
    k = m.width / 433
    d = ImageDraw.Draw(m)
    for cx in (151, 251):
        d.rounded_rectangle(((cx - 52) * k, (140 - 40) * k, (cx + 47) * k, (140 + 38) * k), radius=26 * k, fill=(18, 18, 22, 255))
        d.ellipse(((cx - 40) * k, (140 - 28) * k, (cx - 18) * k, (140 - 12) * k), fill=(90, 96, 120, 255))
    d.rectangle((190 * k, 122 * k, 212 * k, 136 * k), fill=(18, 18, 22, 255))
    return m


def worried(m):
    """Swap the smile for a worried mouth and slanted brows."""
    m = m.copy()
    k = m.width / 433
    d = ImageDraw.Draw(m)
    navy = (32, 52, 110, 255)
    d.ellipse((165 * k, 180 * k, 245 * k, 230 * k), fill=navy)              # hide smile
    d.arc((178 * k, 198 * k, 232 * k, 240 * k), 200, 340, fill=(20, 20, 24, 255), width=int(8 * k))
    d.line(((110 * k, 70 * k), (175 * k, 90 * k)), fill=(20, 20, 24, 255), width=int(12 * k))
    d.line(((290 * k, 70 * k), (225 * k, 90 * k)), fill=(20, 20, 24, 255), width=int(12 * k))
    return m


def shocked(m):
    m = m.copy()
    k = m.width / 433
    d = ImageDraw.Draw(m)
    d.ellipse((165 * k, 180 * k, 245 * k, 232 * k), fill=(32, 52, 110, 255))
    d.ellipse((188 * k, 186 * k, 222 * k, 232 * k), fill=(20, 18, 22, 255))
    d.ellipse((196 * k, 208 * k, 214 * k, 226 * k), fill=(210, 70, 80, 255))
    return m


def building(p, x0, y_base, w, h, color, roof=None, lit=0.6, rows=None, cols=3, seed=1, depth=1.0, win=C.window, dark=(70, 60, 60)):
    rng = np.random.default_rng(seed)
    p.rect(x0, y_base - h, x0 + w, y_base, color, depth=depth)
    if roof:
        p.rect(x0 - 12, y_base - h - 26, x0 + w + 12, y_base - h + 6, roof, depth=depth * 0.8)
    rows = rows or max(2, int(h / 150))
    ww, wh = w / (cols * 1.9), h / (rows * 2.1)
    for r in range(rows):
        for c in range(cols):
            wx = x0 + (c + 0.5) * w / cols - ww / 2
            wy = y_base - h + 40 + r * (h - 60) / rows
            p.rect(wx, wy, wx + ww, wy + wh, win if rng.random() < lit else dark, r=4, depth=0.35)


def bank(p, cx, y_base, w, h, color=C.cream, sign="BANK", trim=C.kraft_lt, depth=1.2, lit=True):
    x0, x1 = cx - w / 2, cx + w / 2
    p.rect(x0 - 30, y_base - 40, x1 + 30, y_base, trim, depth=depth)               # steps
    p.rect(x0 - 15, y_base - 70, x1 + 15, y_base - 40, trim, depth=depth)
    p.rect(x0, y_base - h * 0.78, x1, y_base - 70, color, depth=depth)              # body
    door_w = w * 0.22
    p.rect(cx - door_w / 2, y_base - h * 0.42, cx + door_w / 2, y_base - 70, C.window if lit else C.wood_dk, r=6, depth=0.5)
    n = 4
    for i in range(n):  # columns
        colx = x0 + w * (0.08 + i * 0.84 / (n - 1))
        if abs(colx - cx) < door_w * 0.6:
            continue
        p.rect(colx - w * 0.035, y_base - h * 0.74, colx + w * 0.035, y_base - 70, C.white, depth=0.7)
    p.rect(x0 - 24, y_base - h * 0.86, x1 + 24, y_base - h * 0.76, trim, depth=depth)  # frieze
    p.text(cx, y_base - h * 0.81, sign, h * 0.075, (90, 60, 30), kind="serif", depth=0.3)
    p.poly([(x0 - 40, y_base - h * 0.86), (cx, y_base - h), (x1 + 40, y_base - h * 0.86)], color, depth=depth)  # pediment


def atm(p, cx, y_top, w, h, screen=("WELCOME",), screen_col=(120, 205, 210), body=C.grey_lt, header="ATM", header_col=C.orange,
        cash=False, keypad=True, depth=1.4, text_col=(20, 60, 70)):
    x0, x1 = cx - w / 2, cx + w / 2
    p.rect(x0, y_top, x1, y_top + h, body, r=18, depth=depth)
    p.rect(x0, y_top, x1, y_top + h * 0.11, header_col, r=18, depth=0.6)
    p.text(cx, y_top + h * 0.057, header, h * 0.07, C.cream, depth=0.3)
    sx0, sy0, sx1, sy1 = x0 + w * 0.1, y_top + h * 0.15, x1 - w * 0.1, y_top + h * 0.43
    p.rect(sx0 - 10, sy0 - 10, sx1 + 10, sy1 + 10, C.grey_dk, r=10, depth=0.5)
    p.rect(sx0, sy0, sx1, sy1, screen_col, r=8, depth=0.2, bevel=False)
    p.glow((sx0 + sx1) / 2, (sy0 + sy1) / 2, (sx1 - sx0) * 0.6, screen_col, 0.35)
    for i, line in enumerate(screen):
        p.text(cx, sy0 + (sy1 - sy0) * (i + 1) / (len(screen) + 1), line, h * 0.045, text_col, depth=0.15, bevel=False)
    if keypad:
        kx0, ky0 = x0 + w * 0.12, y_top + h * 0.5
        kw, kh = w * 0.13, h * 0.055
        for r in range(4):
            for c in range(3):
                p.rect(kx0 + c * kw * 1.25, ky0 + r * kh * 1.35, kx0 + c * kw * 1.25 + kw, ky0 + r * kh * 1.35 + kh, C.white, r=8, depth=0.4)
        for i, colr in enumerate((C.red, C.mustard, C.green)):
            p.rect(kx0 + 3 * kw * 1.25, ky0 + i * kh * 1.35, kx0 + 3 * kw * 1.25 + kw * 1.3, ky0 + i * kh * 1.35 + kh, colr, r=8, depth=0.4)
    # card slot
    p.rect(x1 - w * 0.32, y_top + h * 0.5, x1 - w * 0.08, y_top + h * 0.53, C.black, r=6, depth=0.2)
    p.rect(x1 - w * 0.34, y_top + h * 0.48, x1 - w * 0.06, y_top + h * 0.495, header_col, r=4, depth=0.3)
    # cash slot
    p.rect(x0 + w * 0.2, y_top + h * 0.82, x1 - w * 0.2, y_top + h * 0.86, C.black, r=6, depth=0.2)
    return (x0, y_top, x1, y_top + h)


def note(p, cx, cy, w, color=(170, 150, 120), rot=0, label="₹500", depth=0.7):
    h = w * 0.45
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    a = math.radians(rot)
    tp = [(cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)) for x, y in pts]
    p.poly(tp, color, depth)
    inner = [(cx + x * 0.86 * math.cos(a) - y * 0.8 * math.sin(a), cy + x * 0.86 * math.sin(a) + y * 0.8 * math.cos(a)) for x, y in pts]
    p.poly(inner, tuple(min(255, c + 25) for c in color), 0.1, bevel=False)
    p.text(cx, cy, label, w * 0.2, tuple(max(0, c - 70) for c in color), depth=0.1, rot=-rot, bevel=False)


def coin(p, cx, cy, r, depth=1.0, symbol="₹"):
    p.ellipse(cx, cy + r * 0.08, r, r, C.wood, depth=depth)
    p.ellipse(cx, cy, r, r, C.gold, depth=0.3)
    p.ring(cx, cy, r * 0.86, r * 0.06, C.gold_lt, depth=0.2)
    p.text(cx, cy, symbol, r * 1.05, (150, 100, 20), depth=0.35)


def person(p, cx, y_feet, h, suit=C.suit, tie=C.red, skin=C.skin, hair=C.hair, arm_up=False, depth=1.0):
    head_r = h * 0.11
    body_top = y_feet - h * 0.78
    p.rect(cx - h * 0.1, y_feet - h * 0.36, cx - h * 0.02, y_feet, C.black, depth=depth * 0.6)   # legs
    p.rect(cx + h * 0.02, y_feet - h * 0.36, cx + h * 0.1, y_feet, C.black, depth=depth * 0.6)
    p.poly([(cx - h * 0.2, y_feet - h * 0.3), (cx - h * 0.16, body_top), (cx + h * 0.16, body_top), (cx + h * 0.2, y_feet - h * 0.3)], suit, depth)
    p.poly([(cx - h * 0.06, body_top), (cx, body_top + h * 0.18), (cx + h * 0.06, body_top)], C.white, 0.2)
    p.poly([(cx - h * 0.018, body_top + h * 0.02), (cx, body_top + h * 0.16), (cx + h * 0.018, body_top + h * 0.02)], tie, 0.2)
    if arm_up:
        p.poly([(cx + h * 0.15, body_top + h * 0.04), (cx + h * 0.34, body_top - h * 0.12), (cx + h * 0.38, body_top - h * 0.07), (cx + h * 0.18, body_top + h * 0.12)], suit, depth * 0.8)
    p.ellipse(cx, body_top - head_r * 0.95, head_r, head_r * 1.08, skin, depth)
    p.poly([(cx - head_r, body_top - head_r * 1.2), (cx - head_r * 0.7, body_top - head_r * 2.0), (cx + head_r * 0.8, body_top - head_r * 2.0),
            (cx + head_r, body_top - head_r * 1.2)], hair, 0.4)
    p.ellipse(cx - head_r * 0.38, body_top - head_r * 0.95, head_r * 0.1, head_r * 0.13, C.black, 0.1, bevel=False)
    p.ellipse(cx + head_r * 0.38, body_top - head_r * 0.95, head_r * 0.1, head_r * 0.13, C.black, 0.1, bevel=False)
    p.line([(cx - head_r * 0.3, body_top - head_r * 0.5), (cx, body_top - head_r * 0.38), (cx + head_r * 0.3, body_top - head_r * 0.5)], (120, 50, 40), head_r * 0.08, 0.05)
    return (cx, body_top)


def check(p, cx, cy, s, color=C.green, depth=0.5):
    p.line([(cx - s * 0.5, cy), (cx - s * 0.12, cy + s * 0.4), (cx + s * 0.55, cy - s * 0.45)], color, s * 0.2, depth)


def cross(p, cx, cy, s, color=C.red, depth=0.5):
    p.line([(cx - s / 2, cy - s / 2), (cx + s / 2, cy + s / 2)], color, s * 0.2, depth)
    p.line([(cx + s / 2, cy - s / 2), (cx - s / 2, cy + s / 2)], color, s * 0.2, depth)


def stars(p, n, y1, seed=3):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        x, y, r = rng.uniform(40, p.w - 40), rng.uniform(40, y1), rng.uniform(4, 10)
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            rr = r if i % 2 == 0 else r * 0.45
            pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
        p.poly(pts, (250, 230, 160), 0.15, bevel=False)


def shelves(p, x0, y0, x1, y1, seed=5):
    rng = np.random.default_rng(seed)
    p.rect(x0, y0, x1, y1, C.wood_dk, depth=0.8)
    rows = 3
    for r in range(rows):
        sy = y0 + (r + 1) * (y1 - y0) / rows
        x = x0 + 20
        while x < x1 - 60:
            bw = rng.uniform(30, 60); bh = rng.uniform(0.55, 0.85) * (y1 - y0) / rows
            col = [C.brick, C.mustard, C.sky_dk, C.teal, C.cream, C.orange][int(rng.integers(0, 6))]
            p.rect(x, sy - bh - 14, x + bw, sy - 14, col, r=4, depth=0.35)
            x += bw + rng.uniform(4, 14)
        p.rect(x0, sy - 16, x1, sy, C.wood, depth=0.5)


def plant(p, cx, y_base, s=1.0):
    p.rect(cx - 45 * s, y_base - 90 * s, cx + 45 * s, y_base, C.brick, r=10, depth=0.6)
    for a, l in ((-40, 150), (-15, 190), (10, 170), (35, 140), (-60, 110), (60, 115)):
        r = math.radians(a - 90)
        tip = (cx + math.cos(r) * l * s, y_base - 90 * s + math.sin(r) * l * s)
        p.poly([(cx - 10 * s, y_base - 88 * s), tip, (cx + 10 * s, y_base - 88 * s)], C.green_dk if a % 20 else C.green, 0.5)
