"""
Motion-graphics overlays for paper_reel.py (house style: paper stickers, yellow/red accents).

Each shot in shots.json can carry "fx": [ {...}, ... ] with times in shot-local seconds.
Screen space is 1080x1920. Keep overlays above y~1200 (captions live at ~1240-1520).

Types
  sticker  {text, at:[x,y], t, size=64, bg="paper|yellow|navy|red", rot=0, until}
  counter  {from, to, prefix, suffix, decimals=0, at, t, dur=0.8, size=150, bg, label}
  stamp    {text, at, t, color="green", size=120, rot=-8}        slam + shake + flash
  timer    {to, at, t, dur, label}                                stopwatch with sweeping arc
  scramble {final, at, t, dur, size, label}                       random glyphs settling
  checks   {items:[..], at, t, gap=0.5, size=54}                  ticked list popping in
  tracker  {steps:[..], step, t=0}                                progress bar at the top
  route    {nodes:[[x,y,"label"],...], t, dur}                    line drawing + travelling packet
  pulse    {at, t, color, r=120}                                  expanding rings
  marks    {text="?", pts:[[x,y],...], t, gap=0.15, size=120}     scattered popping glyphs
  shake    {t, dur=0.3, amp=18}        flash {t, peak=0.6, dur=0.3}
Each returns sound cues via fx_cues() so pops/slams are heard.
"""
import math, random, re
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
NAVY, INK = (24, 34, 72), (24, 30, 52)
YEL, RED, GRN, WHT = (255, 205, 0), (226, 46, 40), (46, 160, 70), (255, 255, 255)
PAPER = (250, 244, 228)
BGS = {"paper": (PAPER, INK), "yellow": ((255, 210, 40), INK), "navy": (NAVY, WHT), "red": ((214, 44, 40), WHT), "green": ((40, 150, 70), WHT)}
_F = {}


def font(size, kind="sans"):
    key = (int(size), kind)
    if key not in _F:
        path = {"sans": "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf", "mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"}[kind]
        _F[key] = ImageFont.truetype(path, int(size))
    return _F[key]


def ease_out_back(x, s=1.9):
    x = min(max(x, 0), 1)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def ease(x):
    x = min(max(x, 0), 1)
    return x * x * (3 - 2 * x)


def spans(text, base):
    out, col = [], base
    for tok in re.split(r"(\[/?[yr]\])", text):
        if tok == "[y]": col = (232, 150, 0) if base == INK else YEL
        elif tok == "[r]": col = RED
        elif tok in ("[/y]", "[/r]"): col = base
        elif tok: out.append((tok, col))
    return out


def card(text, size=64, bg="paper", pad=(34, 18), kind="sans", radius=None):
    fill, ink = BGS[bg]
    f = font(size, kind)
    parts = spans(text, ink)
    tw = sum(f.getlength(s) for s, _ in parts)
    asc, desc = f.getmetrics()
    w, h = int(tw + pad[0] * 2), int(asc + desc + pad[1] * 2)
    sh = 18
    img = Image.new("RGBA", (w + sh * 2, h + sh * 2), (0, 0, 0, 0))
    shadow = Image.new("L", img.size, 0)
    r = radius if radius is not None else h // 2.6
    ImageDraw.Draw(shadow).rounded_rectangle((sh + 4, sh + 10, sh + w + 4, sh + h + 10), r, fill=150)
    shadow = shadow.filter(ImageFilter.GaussianBlur(9))
    img.paste(Image.new("RGBA", img.size, (20, 10, 0, 255)), (0, 0), shadow)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((sh, sh, sh + w, sh + h), r, fill=fill, outline=(20, 20, 30), width=5)
    x = sh + pad[0]
    for s, c in parts:
        d.text((x, sh + pad[1]), s, font=f, fill=c)
        x += f.getlength(s)
    return img


def place(frame, im, cx, cy, scale=1.0, rot=0.0, alpha=1.0):
    if scale <= 0.01 or alpha <= 0.01:
        return
    if abs(scale - 1) > 1e-3:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if rot:
        im = im.rotate(rot, Image.BICUBIC, expand=True)
    if alpha < 1:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    x, y = int(cx - im.width / 2), int(cy - im.height / 2)
    # clip to frame
    cx0, cy0 = max(0, -x), max(0, -y)
    cx1, cy1 = min(im.width, W - x), min(im.height, H - y)
    if cx1 > cx0 and cy1 > cy0:
        frame.alpha_composite(im.crop((cx0, cy0, cx1, cy1)), (x + cx0, y + cy0))


def pop(lt, t0, dur_shot, until=None, inn=0.32):
    """scale, alpha for a pop-in element; fades out at `until` or at shot end."""
    if lt < t0:
        return 0, 0
    k = (lt - t0) / inn
    s = ease_out_back(k) if k < 1 else 1.0
    end = until if until is not None else dur_shot
    a = 1.0 if lt < end - 0.15 else max(0.0, (end - lt) / 0.15)
    return s, a


class FX:
    def __init__(self):
        self.cache = {}

    def _card(self, *a, **k):
        key = (a, tuple(sorted(k.items())))
        if key not in self.cache:
            self.cache[key] = card(*a, **k)
        return self.cache[key]

    # ------------------------------------------------------------------
    def offset(self, fx, lt):
        """camera shake offset (dx, dy) and flash alpha for this frame."""
        dx = dy = 0.0
        fl = 0.0
        for e in fx:
            typ = e["type"]
            if typ in ("shake", "stamp"):
                t0 = e["t"] + (0.12 if typ == "stamp" else 0)
                dur, amp = e.get("dur", 0.3), e.get("amp", 18 if typ == "shake" else 22)
                if t0 <= lt < t0 + dur:
                    k = 1 - (lt - t0) / dur
                    rnd = random.Random(int(lt * 60))
                    dx += rnd.uniform(-amp, amp) * k; dy += rnd.uniform(-amp, amp) * k
            if typ in ("flash", "stamp"):
                t0 = e["t"] + (0.12 if typ == "stamp" else 0)
                dur, peak = e.get("dur", 0.3), e.get("peak", 0.5 if typ == "flash" else 0.35)
                if t0 <= lt < t0 + dur:
                    fl = max(fl, peak * (1 - (lt - t0) / dur))
        return dx, dy, fl

    def draw(self, frame, fx, lt, dur):
        for e in fx:
            getattr(self, "_" + e["type"], lambda *a: None)(frame, e, lt, dur)

    # ------------------------------------------------------------------ elements
    def _sticker(self, frame, e, lt, dur):
        s, a = pop(lt, e["t"], dur, e.get("until"))
        wob = math.sin((lt - e["t"]) * 5) * 1.5 if lt > e["t"] + 0.3 else 0
        place(frame, self._card(e["text"], e.get("size", 64), e.get("bg", "paper")), *e["at"], s, e.get("rot", 0) + wob, a)

    def _counter(self, frame, e, lt, dur):
        s, a = pop(lt, e["t"], dur, e.get("until"))
        if not s:
            return
        k = ease((lt - e["t"] - 0.1) / e.get("dur", 0.8))
        v = e.get("from", 0) + (e["to"] - e.get("from", 0)) * k
        txt = f"{e.get('prefix', '')}{v:.{e.get('decimals', 0)}f}{e.get('suffix', '')}"
        im = card(txt, e.get("size", 150), e.get("bg", "yellow"), pad=(44, 14))
        bump = 1 + 0.12 * math.exp(-((lt - e["t"] - 0.1 - e.get("dur", 0.8)) * 9) ** 2)
        place(frame, im, *e["at"], s * bump, e.get("rot", -3), a)
        if e.get("label"):
            place(frame, self._card(e["label"], 40, "navy"), e["at"][0], e["at"][1] + im.height * 0.62, s, e.get("rot", -3), a)

    def _stamp(self, frame, e, lt, dur):
        t0 = e["t"]
        if lt < t0:
            return
        k = (lt - t0) / 0.14
        s = 2.4 - 1.4 * ease(k) if k < 1 else 1.0
        a = min(1, k * 1.5) * (1.0 if lt < (e.get("until") or dur) - 0.15 else max(0, ((e.get("until") or dur) - lt) / 0.15))
        col = {"green": GRN, "red": RED}[e.get("color", "green")]
        key = ("stamp", e["text"], e.get("size", 120), col)
        if key not in self.cache:
            f = font(e.get("size", 120))
            tw = f.getlength(e["text"]); asc, desc = f.getmetrics()
            w, h = int(tw + 80), int(asc + desc + 50)
            im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            d.rounded_rectangle((6, 6, w - 6, h - 6), 24, outline=col + (235,), width=12)
            d.text((40, 22), e["text"], font=f, fill=col + (235,))
            grit = Image.effect_noise((w, h), 60).point(lambda v: 255 if v > 70 else 120)
            im.putalpha(Image.composite(im.getchannel("A"), Image.new("L", (w, h), 0), grit))
            self.cache[key] = im
        place(frame, self.cache[key], *e["at"], s, e.get("rot", -8), a)

    def _timer(self, frame, e, lt, dur):
        s, a = pop(lt, e["t"], dur, e.get("until"))
        if not s:
            return
        r = e.get("r", 120)
        k = ease((lt - e["t"] - 0.2) / e.get("dur", 2.0))
        im = Image.new("RGBA", (r * 2 + 60, r * 2 + 110), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        cx, cy = r + 30, r + 70
        d.ellipse((cx - r + 6, cy - r + 12, cx + r + 6, cy + r + 12), fill=(0, 0, 0, 90))
        d.rectangle((cx - 22, cy - r - 46, cx + 22, cy - r - 4), fill=(20, 20, 30)); d.rounded_rectangle((cx - 40, cy - r - 64, cx + 40, cy - r - 36), 10, fill=RED)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=PAPER, outline=(20, 20, 30), width=8)
        d.pieslice((cx - r + 18, cy - r + 18, cx + r - 18, cy + r - 18), -90, -90 + 360 * k, fill=YEL)
        ang = math.radians(-90 + 360 * k)
        d.line((cx, cy, cx + math.cos(ang) * (r - 26), cy + math.sin(ang) * (r - 26)), fill=(20, 20, 30), width=10)
        d.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), fill=RED)
        im2 = card(f"{e['to'] * k:.1f} sec", 54, "navy", pad=(26, 10))
        place(frame, im, *e["at"], s, 0, a)
        place(frame, im2, e["at"][0], e["at"][1] + r + 70, s, 0, a)

    def _scramble(self, frame, e, lt, dur):
        s, a = pop(lt, e["t"], dur, e.get("until"))
        if not s:
            return
        fin = e["final"]
        k = (lt - e["t"]) / e.get("dur", 1.4)
        rnd = random.Random(int(lt * 20))
        glyphs = "0123456789ABCDEF#@%&*"
        n_fixed = int(len(fin) * min(1, max(0, k)))
        txt = "".join(c if (i < n_fixed or c == " ") else rnd.choice(glyphs) for i, c in enumerate(fin))
        place(frame, card(txt, e.get("size", 76), "navy", pad=(30, 14), kind="mono"), *e["at"], s, 0, a)
        if e.get("label") and k >= 1:
            s2, a2 = pop(lt, e["t"] + e.get("dur", 1.4), dur, e.get("until"))
            place(frame, self._card(e["label"], 50, "yellow"), e["at"][0], e["at"][1] + 120, s2, -4, a2)

    def _checks(self, frame, e, lt, dur):
        x, y = e["at"]
        for i, it in enumerate(e["items"]):
            t0 = e["t"] + i * e.get("gap", 0.5)
            s, a = pop(lt, t0, dur, e.get("until"))
            im = self._card(it, e.get("size", 54), "paper", pad=(30, 12))
            tick = self.cache.setdefault(("tick", e.get("size", 54)), _tick(e.get("size", 54)))
            row = Image.new("RGBA", (im.width + tick.width + 10, max(im.height, tick.height)), (0, 0, 0, 0))
            row.alpha_composite(tick, (0, (row.height - tick.height) // 2)); row.alpha_composite(im, (tick.width + 10, (row.height - im.height) // 2))
            place(frame, row, x + row.width / 2, y + i * (row.height + 8), s, -2 + i * 1.5, a)

    def _tracker(self, frame, e, lt, dur):
        steps, cur = e["steps"], e["step"]
        intro = e.get("intro", False)
        k_in = ease((lt - e.get("t", 0)) / 0.35) if intro else 1.0
        y = 130 - (1 - k_in) * 220
        x0, x1 = 140, W - 140
        n = len(steps)
        xs = [x0 + i * (x1 - x0) / (n - 1) for i in range(n)]
        d = ImageDraw.Draw(frame)
        # base line + progress fill
        d.rounded_rectangle((x0, y - 9, x1, y + 9), 9, fill=(20, 20, 30, 200))
        prog_prev = (cur - 2) / (n - 1) if cur > 1 else 0
        prog = prog_prev + (((cur - 1) / (n - 1)) - prog_prev) * ease((lt - 0.15) / 0.6)
        d.rounded_rectangle((x0, y - 6, x0 + max(12, (x1 - x0) * prog), y + 6), 6, fill=YEL)
        for i, (x, lab) in enumerate(zip(xs, steps)):
            done, active = i + 1 < cur, i + 1 == cur
            r = 40 if not active else 40 + 6 * (1 + math.sin(lt * 7)) / 2
            fill = GRN if done else (YEL if active else PAPER)
            d.ellipse((x - r + 4, y - r + 8, x + r + 4, y + r + 8), fill=(0, 0, 0, 90))
            d.ellipse((x - r, y - r, x + r, y + r), fill=fill, outline=(20, 20, 30), width=6)
            f = font(36)
            d.text((x, y), "✓" if done else str(i + 1), font=font(40, "mono") if done else f, fill=WHT if done else INK, anchor="mm")
            lab_im = self._card(lab, 30, "navy" if active else "paper", pad=(16, 6))
            place(frame, lab_im, x, y + 82, 1.0 if active else 0.9, 0, 1.0 if (active or done) else 0.75)

    def _route(self, frame, e, lt, dur):
        nodes = e["nodes"]
        k = (lt - e["t"]) / e.get("dur", 1.6)
        if k < 0:
            return
        d = ImageDraw.Draw(frame)
        segs = len(nodes) - 1
        for i in range(segs):
            a_, b_ = nodes[i], nodes[i + 1]
            kk = min(1, max(0, k * segs - i))
            if kk <= 0:
                continue
            ex, ey = a_[0] + (b_[0] - a_[0]) * kk, a_[1] + (b_[1] - a_[1]) * kk
            L = math.hypot(ex - a_[0], ey - a_[1]); nd = int(L / 34)
            for j in range(nd):
                px = a_[0] + (ex - a_[0]) * j / max(nd, 1); py = a_[1] + (ey - a_[1]) * j / max(nd, 1)
                d.ellipse((px - 7, py - 7, px + 7, py + 7), fill=(255, 250, 230, 235), outline=(20, 20, 30), width=2)
        # travelling packet (loops once the path is drawn)
        if k > 0.15:
            p = ((lt - e["t"]) * 0.9) % 1.0
            seg = min(int(p * segs), segs - 1); kk = p * segs - seg
            a_, b_ = nodes[seg], nodes[seg + 1]
            px, py = a_[0] + (b_[0] - a_[0]) * kk, a_[1] + (b_[1] - a_[1]) * kk
            glow = Image.new("RGBA", (120, 120), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse((30, 30, 90, 90), fill=YEL + (200,))
            place(frame, glow.filter(ImageFilter.GaussianBlur(14)), px, py)
            d.ellipse((px - 18, py - 18, px + 18, py + 18), fill=YEL, outline=(20, 20, 30), width=4)
        for i, (x, y, lab) in enumerate(nodes):
            s, a = pop(lt, e["t"] + i * e.get("dur", 1.6) / max(segs, 1), dur, e.get("until"))
            if lab:
                place(frame, self._card(lab, 40, "yellow" if i == len(nodes) - 1 else "paper", pad=(22, 8)), x, y, s, 0, a)

    def _pulse(self, frame, e, lt, dur):
        if lt < e["t"]:
            return
        d = ImageDraw.Draw(frame)
        col = {"yellow": YEL, "green": GRN, "red": RED}.get(e.get("color", "yellow"), YEL)
        for j in range(3):
            p = ((lt - e["t"]) * 0.8 + j / 3) % 1
            r = e.get("r", 120) * (0.4 + 1.2 * p)
            al = int(220 * (1 - p))
            d.ellipse((e["at"][0] - r, e["at"][1] - r, e["at"][0] + r, e["at"][1] + r), outline=col + (al,), width=8)

    def _marks(self, frame, e, lt, dur):
        for i, (x, y) in enumerate(e["pts"]):
            s, a = pop(lt, e["t"] + i * e.get("gap", 0.15), dur, e.get("until"))
            key = ("mark", e.get("text", "?"), e.get("size", 120))
            if key not in self.cache:
                f = font(e.get("size", 120)); im = Image.new("RGBA", (int(e.get("size", 120) * 1.2),) * 2, (0, 0, 0, 0))
                ImageDraw.Draw(im).text((im.width / 2, im.height / 2), e.get("text", "?"), font=f, fill=YEL, anchor="mm", stroke_width=8, stroke_fill=(20, 20, 30))
                self.cache[key] = im
            place(frame, self.cache[key], x, y + math.sin(lt * 4 + i) * 8, s, math.sin(lt * 3 + i) * 10, a)


def _tick(size):
    s = int(size * 1.3)
    im = Image.new("RGBA", (s + 10, s + 14), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((5, 10, s + 5, s + 10), fill=(0, 0, 0, 90))
    d.ellipse((0, 0, s, s), fill=GRN, outline=(20, 20, 30), width=5)
    d.line((s * 0.27, s * 0.52, s * 0.44, s * 0.7, s * 0.75, s * 0.32), fill=WHT, width=int(s * 0.12), joint="curve")
    return im


def fx_cues(fx, t0_shot):
    cues = []
    for e in fx:
        t, typ = t0_shot + e.get("t", 0), e["type"]
        if typ in ("sticker", "marks"):
            n = len(e.get("pts", [0]))
            for i in range(n):
                cues.append({"t": t + i * e.get("gap", 0.15), "sfx": "pop_high" if typ == "marks" else "pop", "gain": 0.35})
        elif typ == "counter":
            cues.append({"t": t, "sfx": "pop", "gain": 0.4})
            for j in range(int(e.get("dur", 0.8) / 0.06)):
                cues.append({"t": t + 0.1 + j * 0.06, "sfx": "counter", "gain": 0.18})
            cues.append({"t": t + 0.1 + e.get("dur", 0.8), "sfx": "ding", "gain": 0.35})
        elif typ == "stamp":
            cues += [{"t": t + 0.1, "sfx": "hit", "gain": 0.8}, {"t": t + 0.1, "sfx": "boom", "gain": 0.35}]
        elif typ == "timer":
            for j in range(int(e.get("dur", 2.0) / 0.25)):
                cues.append({"t": t + 0.2 + j * 0.25, "sfx": "tick", "gain": 0.3})
            cues.append({"t": t + 0.2 + e.get("dur", 2.0), "sfx": "ding", "gain": 0.4})
        elif typ == "scramble":
            for j in range(int(e.get("dur", 1.4) / 0.07)):
                cues.append({"t": t + j * 0.07, "sfx": "key", "gain": 0.15})
            cues.append({"t": t + e.get("dur", 1.4), "sfx": "pop_low", "gain": 0.4})
        elif typ == "checks":
            for i in range(len(e["items"])):
                cues.append({"t": t + i * e.get("gap", 0.5), "sfx": "ding", "gain": 0.3})
        elif typ == "tracker" and e.get("intro"):
            cues.append({"t": t, "sfx": "whoosh", "gain": 0.35})
        elif typ == "tracker":
            cues.append({"t": t + 0.15, "sfx": "riser_short", "gain": 0.18})
        elif typ == "route":
            cues.append({"t": t, "sfx": "whoosh_long", "gain": 0.3})
        elif typ == "shake":
            cues.append({"t": t, "sfx": "hit", "gain": 0.5})
        elif typ == "flash":
            cues.append({"t": t, "sfx": "shutter", "gain": 0.3})
    return cues
