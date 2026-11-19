#!/usr/bin/env python3
"""Builds the papercraft shots for the ATM reel (all except s02, which is the AI master shot).
Run from reels/:  python3 projects/atm-kaise/scenes.py [s05 s07 ...]
"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
from papercraft import *  # noqa

M = mascot_img(os.path.join(HERE, "assets", "mascot.png"))
OUT = os.path.join(HERE, "images")
W, H = PW, PH
FLOOR = 1620   # where most things stand; captions sit below ~1500 (in 1080x1920 space ~1300)


def desk_room(p, wall=C.mustard, floor=C.wood, y=FLOOR):
    p.gradient(tuple(min(255, c + 18) for c in wall), wall, 0, y)
    p.gradient(floor, C.wood_dk, y, H)
    p.rect(-20, y - 20, W + 20, y + 30, C.wood_dk, depth=1.2)


def s01():
    p = Paper(seed=11)
    p.gradient(C.night, C.night2, 0, 1500)
    p.gradient((70, 70, 80), (40, 40, 48), 1500, H)
    stars(p, 40, 700)
    p.ellipse(1040, 260, 85, 85, (250, 236, 190), depth=0.4)
    p.glow(1040, 260, 260, (250, 236, 190), 0.25)
    # far skyline
    for i, (x, w, h, col) in enumerate([(-40, 260, 900, (66, 82, 128)), (200, 220, 1100, (78, 92, 140)), (900, 260, 1000, (70, 86, 132)), (1120, 220, 820, (60, 76, 122))]):
        building(p, x, 1500, w, h, col, lit=0.45, seed=i, cols=3, depth=0.6)
    # bank in the middle
    bank(p, 600, 1520, 560, 760, color=C.kraft_lt, trim=C.kraft)
    p.glow(600, 1300, 300, C.window, 0.25)
    # ATM kiosk on the right
    p.rect(955, 1080, 1225, 1530, C.cream, depth=1.2)
    p.rect(935, 1030, 1245, 1120, C.orange, depth=1.0)
    p.text(1090, 1075, "ATM", 70, C.cream, depth=0.4)
    p.rect(995, 1160, 1185, 1500, (255, 205, 120), depth=0.3, bevel=False)
    p.glow(1090, 1330, 260, (255, 190, 100), 0.45)
    p.rect(1040, 1240, 1140, 1490, C.grey_lt, r=8, depth=0.8)
    p.rect(1055, 1260, 1125, 1320, (120, 205, 210), r=4, depth=0.2)
    # street
    p.rect(-20, 1520, W + 20, 1600, C.grey, depth=1.0)
    for x in range(40, W, 220):
        p.rect(x, 1880, x + 120, 1900, (230, 220, 190), depth=0.3)
    p.rect(-20, 2150, W + 20, H + 20, C.grey_dk, depth=1.0)
    for x in (120, 1150):
        p.rect(x - 8, 1050, x + 8, 1560, C.black, depth=0.6)
        p.ellipse(x, 1040, 40, 30, C.window, depth=0.3)
        p.glow(x, 1060, 160, C.window, 0.4)
    p.light(0.5, 0.55, warm=(255, 190, 110), strength=0.5, vignette=0.5)
    p.save(f"{OUT}/s01.png")


def s03():
    p = Paper(seed=13)
    p.gradient((70, 90, 110), (40, 50, 64))
    p.glow(640, 700, 700, (255, 200, 120), 0.35)
    atm(p, 560, 260, 860, 1700, screen=("ENTER YOUR PIN", "•  •  •  •"), keypad=True)
    p.image(M, 1020, 1560, 640, flip=True, rot=-6)
    p.light(0.45, 0.4, strength=0.4)
    p.save(f"{OUT}/s03.png")


def s04():
    p = Paper(seed=14)
    p.gradient((40, 110, 120), (16, 46, 56))
    p.glow(640, 900, 800, (120, 230, 220), 0.4)
    # floating envelope
    ex0, ey0, ex1, ey1 = 260, 640, 1020, 1160
    p.rect(ex0, ey0, ex1, ey1, C.paper, r=14, depth=2.2)
    p.poly([(ex0, ey0 + 6), (640, 930), (ex1, ey0 + 6)], (232, 226, 212), 0.6)
    p.text(640, 1060, "* * * *", 90, C.grey_dk, depth=0.3)
    # padlock
    p.ring(640, 820, 120, 38, C.grey_lt, depth=1.4)
    p.rect(500, 820, 780, 1050, C.gold, r=30, depth=1.8)
    p.ellipse(640, 915, 30, 30, (120, 80, 10), depth=0.2)
    p.rect(628, 920, 652, 990, (120, 80, 10), r=8, depth=0.2)
    p.glow(640, 930, 300, C.gold_lt, 0.25)
    p.light(0.5, 0.4, warm=(180, 255, 240), strength=0.3)
    p.save(f"{OUT}/s04.png")


def s05():
    p = Paper(seed=15)
    p.gradient(C.kraft_lt, C.kraft)
    cx, cy = 640, 980
    banks = []
    for i in range(8):
        a = -math.pi / 2 + i * math.pi / 4
        banks.append((cx + math.cos(a) * 470, cy + math.sin(a) * 560))
    cols = [C.sky_dk, C.brick, C.teal, C.orange, C.navy, C.green_dk, C.mustard, C.red]
    for (x, y) in banks:   # strings first (under the buildings)
        p.curve((cx, cy), (x, y), 40, (110, 70, 40), 7, 0.5)
    for i, (x, y) in enumerate(banks):
        p.rect(x - 95, y - 70, x + 95, y + 80, cols[i], depth=1.0)
        p.poly([(x - 115, y - 70), (x, y - 140), (x + 115, y - 70)], cols[i], 1.0)
        p.rect(x - 80, y - 40, x + 80, y - 5, C.cream, depth=0.3)
        p.text(x, y - 22, "BANK", 30, (70, 50, 30), kind="serif", depth=0.1)
        for k in range(3):
            p.rect(x - 70 + k * 55, y + 10, x - 40 + k * 55, y + 70, C.white, depth=0.3)
    # glowing signals along strings
    for i, (x, y) in enumerate(banks):
        t = 0.35 + 0.08 * (i % 3)
        sx, sy = cx + (x - cx) * t, cy + (y - cy) * t + math.sin(t * math.pi) * 40
        p.glow(sx, sy, 60, (255, 240, 150), 0.8)
        p.ellipse(sx, sy, 12, 12, (255, 248, 200), 0.2, bevel=False)
    # exchange in the centre
    p.rect(cx - 210, cy - 200, cx + 210, cy + 230, C.green_dk, r=14, depth=2.0)
    p.rect(cx - 170, cy - 150, cx + 170, cy - 20, C.cream, r=10, depth=0.5)
    p.text(cx, cy - 85, "NFS", 110, C.green_dk, depth=0.5)
    p.text(cx, cy + 40, "NPCI", 46, C.cream, depth=0.3)
    for k in range(4):
        p.ellipse(cx - 120 + k * 80, cy + 140, 22, 22, C.window, 0.3)
        p.glow(cx - 120 + k * 80, cy + 140, 50, C.window, 0.5)
    p.glow(cx, cy, 500, (255, 230, 160), 0.2)
    p.light(0.5, 0.4, strength=0.3)
    p.save(f"{OUT}/s05.png")


def s06():
    p = Paper(seed=16)
    desk_room(p, wall=(214, 186, 140))
    shelves(p, 80, 220, 1200, 820)
    x, y, k = p.image(M, 560, FLOOR + 60, 980, rot=4)
    # magnifying glass over the card face (lower part)
    gx, gy = 760, 1060
    p.line([(gx + 120, gy + 120), (gx + 300, gy + 330)], C.wood_dk, 44, 1.2)
    p.ring(gx, gy, 190, 34, C.wood, depth=1.4)
    p.ellipse(gx, gy, 158, 158, (210, 235, 245), depth=0.2, bevel=False, opacity=0.55)
    p.text(gx, gy - 10, "6080 12", 70, C.gold, kind="mono", depth=0.4)
    p.text(gx, gy + 70, "•••• ••••", 44, C.cream, kind="mono", depth=0.2)
    p.glow(gx, gy, 230, (255, 230, 140), 0.25)
    p.light(0.5, 0.4, strength=0.4)
    p.save(f"{OUT}/s06.png")


def s07():
    p = Paper(seed=17)
    desk_room(p, wall=C.sky)
    p.rect(120, 220, 560, 560, C.cream, r=8, depth=1.0)          # wall chart
    for i in range(4):
        p.rect(170 + i * 95, 500 - (i + 1) * 60, 230 + i * 95, 500, [C.teal, C.mustard, C.brick, C.green][i], depth=0.3)
    p.ellipse(1020, 360, 110, 110, C.white, depth=1.0)          # clock
    p.line([(1020, 360), (1020, 290)], C.black, 10, 0.2); p.line([(1020, 360), (1070, 380)], C.black, 10, 0.2)
    person(p, 470, 1340, 760)
    p.rect(80, 1150, 1000, 1240, C.wood, depth=1.6)              # desk top
    p.rect(120, 1240, 960, FLOOR, C.wood_dk, depth=1.2)
    # clipboard
    p.rect(420, 700, 800, 1180, C.wood, r=16, depth=1.8)
    p.rect(450, 740, 770, 1160, C.white, r=6, depth=0.4)
    p.rect(560, 690, 660, 740, C.grey_dk, r=8, depth=0.5)
    for i, lbl in enumerate(["PIN", "BALANCE", "LIMIT"]):
        yy = 830 + i * 115
        p.rect(475, yy - 32, 540, yy + 32, C.cream, r=6, depth=0.3)
        check(p, 508, yy, 70)
        p.text(560, yy, lbl, 46, C.navy, anchor="lm", depth=0.2)
    p.image(M, 1080, FLOOR - 10, 620, flip=True, rot=-5)
    p.light(0.45, 0.35, strength=0.35)
    p.save(f"{OUT}/s07.png")


def s08():
    p = Paper(seed=18)
    desk_room(p, wall=(226, 200, 150))
    p.image(M, 1020, 980, 560, rot=8)
    # paper form
    p.poly([(150, 820), (1000, 760), (1060, 1560), (210, 1620)], C.paper, depth=1.8)
    for i in range(7):
        y = 930 + i * 80
        p.line([(250, y + 10 - i * 4), (900, y - 30 - i * 4)], C.grey_lt, 8, 0.05)
    # APPROVED stamp mark
    p.rect(300, 1120, 960, 1340, C.green, r=26, depth=0.1, bevel=False, opacity=0.9)
    p.rect(320, 1140, 940, 1320, C.paper, r=20, depth=0.0, bevel=False)
    p.text(630, 1230, "APPROVED", 128, C.green, depth=0.05, bevel=False)
    # rubber stamp coming down
    p.rect(470, 560, 790, 640, C.grey_dk, r=10, depth=1.6)
    p.rect(560, 330, 700, 560, C.red, r=20, depth=1.6)
    p.ellipse(630, 320, 110, 70, C.red, depth=1.6)
    for i, (x, y, c) in enumerate([(220, 700, C.mustard), (1000, 640, C.sky_dk), (300, 520, C.brick), (930, 480, C.green), (180, 1000, C.orange), (1080, 1100, C.mustard)]):
        p.rect(x, y, x + 40, y + 22, c, depth=0.6)
    p.light(0.5, 0.4, strength=0.35)
    p.save(f"{OUT}/s08.png")


def s09():
    p = Paper(seed=19)
    p.gradient((90, 70, 56), (44, 34, 30))
    p.glow(640, 700, 700, (255, 190, 110), 0.4)
    atm(p, 640, 150, 900, 1500, screen=("PLEASE COLLECT", "YOUR CASH"), keypad=True, cash=True)
    for i, rot in enumerate((-14, -5, 6, 15)):
        note(p, 600 + i * 40, 1440 + i * 26, 360, color=(176, 160, 132), rot=rot)
    x, y, k = p.image(M, 640, 2150, 700)
    p.light(0.5, 0.45, strength=0.4)
    p.save(f"{OUT}/s09.png")


def s10():
    p = Paper(seed=20)
    p.gradient(C.sky, (200, 230, 240), 0, 1500)
    for x, y, s in ((220, 300, 1.0), (900, 220, 1.3), (640, 480, 0.8)):
        for dx, r in ((-60, 60), (0, 85), (70, 65)):
            p.ellipse(x + dx * s, y, r * s, r * s * 0.8, C.white, depth=0.5)
    p.gradient((190, 180, 160), (150, 140, 124), 1500, H)
    bank(p, 230, 1530, 420, 820, color=(150, 190, 230), trim=C.sky_dk)
    bank(p, 1060, 1530, 420, 820, color=(246, 186, 130), trim=C.orange)
    p.rect(-20, 1520, W + 20, 1580, C.grey_lt, depth=1.0)
    # dashed path of the coin
    for i in range(9):
        t = i / 8
        p.ellipse(330 + t * 620, 900 - math.sin(t * math.pi) * 200, 9, 9, C.cream, 0.2)
    coin(p, 650, 900, 150, depth=1.8)
    p.image(M, 650, 1780, 720)
    p.light(0.5, 0.4, strength=0.3)
    p.save(f"{OUT}/s10.png")


def s11():
    p = Paper(seed=21)
    desk_room(p, wall=C.sky)
    # desk calendar
    cx0, cy0, cx1, cy1 = 140, 380, 900, 1480
    p.poly([(cx0 + 40, cy1), (cx0 + 120, cy0 + 60), (cx1 - 120, cy0 + 60), (cx1 - 40, cy1)], C.wood_dk, depth=1.6)
    p.rect(cx0, cy0, cx1, cy1 - 40, C.paper, r=10, depth=1.8)
    p.rect(cx0, cy0, cx1, cy0 + 170, C.red, r=10, depth=0.6)
    for i in range(6):
        p.ring(cx0 + 90 + i * 115, cy0 + 10, 26, 10, C.grey_dk, depth=0.4)
    p.text((cx0 + cx1) / 2, cy0 + 95, "FREE / MONTH", 66, C.cream, depth=0.3)
    nums = list(range(1, 29))
    for i, n in enumerate(nums):
        r, c = divmod(i, 7)
        x = cx0 + 70 + c * 100; y = cy0 + 260 + r * 150
        col = C.navy
        if n in (3, 5):
            p.ring(x, y, 56, 12, C.red, depth=0.5)
            col = C.red
        p.text(x, y, str(n), 48, col, depth=0.15)
    p.text(cx0 + 70 + 2 * 100, cy0 + 260 + 4 * 150 - 20, "metro", 34, C.red, depth=0.1)
    p.text(cx0 + 70 + 4 * 100, cy0 + 260 + 4 * 150 - 20, "others", 34, C.red, depth=0.1)
    p.image(M, 1060, FLOOR + 40, 760, flip=True, rot=-4)
    p.light(0.45, 0.35, strength=0.35)
    p.save(f"{OUT}/s11.png")


def s12():
    p = Paper(seed=22)
    desk_room(p, wall=(236, 196, 150))
    for x, y, s in ((170, 300, 120), (1080, 260, 150), (230, 900, 90), (1100, 860, 110), (640, 180, 80)):
        p.text(x, y, "₹", s, C.red, depth=1.2)
    p.image(shocked(M), 640, FLOOR - 40, 860)
    # long receipt curling to the floor
    pts = [(560, 1180), (720, 1180), (760, 1500), (860, 1800), (1040, 2050), (1180, 2060), (1000, 1760), (900, 1480), (880, 1180)]
    p.poly([(560, 1140), (720, 1140), (760, 1520), (900, 1820), (1110, 2080), (1000, 2120), (790, 1860), (650, 1540)], C.white, depth=1.6)
    for i in range(8):
        y = 1200 + i * 110
        x = 620 + i * 48
        p.text(x + 40, y, "₹23", 36, C.red if i % 2 == 0 else C.grey_dk, depth=0.05, rot=-18, bevel=False)
    p.light(0.5, 0.4, strength=0.35)
    p.save(f"{OUT}/s12.png")


def s13():
    p = Paper(seed=23)
    p.gradient((86, 60, 60), (40, 30, 34))
    p.glow(520, 600, 600, (255, 120, 100), 0.3)
    atm(p, 470, 200, 820, 1500, screen=("TRANSACTION", "FAILED"), screen_col=(240, 130, 120), text_col=(90, 10, 10))
    cross(p, 470, 492, 56, C.red)
    # calendar: 5 days
    p.rect(900, 330, 1220, 650, C.paper, r=12, depth=1.6)
    p.rect(900, 330, 1220, 420, C.red, r=12, depth=0.5)
    p.text(1060, 375, "T + 5", 54, C.cream, depth=0.2)
    p.text(1060, 540, "5", 160, C.navy, depth=0.4)
    p.text(1060, 760, "DIN", 70, C.cream, depth=0.6)
    coin(p, 1060, 960, 110, depth=1.4)
    p.text(1060, 1140, "₹100/din", 56, C.gold_lt, depth=0.6)
    p.image(worried(M), 1000, 1900, 640, flip=True, rot=-3)
    p.light(0.45, 0.4, strength=0.3)
    p.save(f"{OUT}/s13.png")


def s14():
    p = Paper(seed=24)
    desk_room(p, wall=C.mustard)
    p.rect(120, 240, 520, 640, C.sky, depth=1.0)       # window
    p.rect(140, 260, 500, 620, (190, 226, 244), depth=0.2, bevel=False)
    p.rect(310, 260, 330, 620, C.cream, depth=0.3); p.rect(140, 430, 500, 450, C.cream, depth=0.3)
    p.rect(-20, 1300, W + 20, 1390, C.wood, depth=1.6)  # desk
    p.rect(-20, 1390, W + 20, FLOOR + 400, C.wood_dk, depth=1.0)
    for i, (h, col) in enumerate([(220, C.brick), (180, C.teal), (250, C.navy), (200, C.mustard)]):
        p.rect(90 + i * 62, 1300 - h, 140 + i * 62, 1300, col, r=4, depth=0.7)
    p.rect(1010, 1160, 1120, 1300, C.red, r=12, depth=0.8)                  # pencil cup
    for i, col in enumerate((C.mustard, C.sky_dk, C.green)):
        p.rect(1025 + i * 30, 1020 + i * 20, 1043 + i * 30, 1170, col, depth=0.5)
    plant(p, 1150, 1300, 0.9)
    p.image(with_sunglasses(M), 640, 1345, 900)
    p.light(0.5, 0.35, strength=0.45)
    p.save(f"{OUT}/s14.png")


ALL = {k: v for k, v in globals().items() if k.startswith("s") and k[1:].isdigit()}
if __name__ == "__main__":
    want = sys.argv[1:] or sorted(ALL)
    for k in want:
        ALL[k]()
        print("built", k)
