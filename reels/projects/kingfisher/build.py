#!/usr/bin/env python3
"""
Kingfisher Airlines - The Rise and Fall (75 s Hinglish reel + 4 s logo outro).

Takes the 4-second AI animation clips in clips/, retimes each piece onto its
5-second voiceover beat (motion-interpolated slow motion, 30 fps), upscales to
1080x1920, burns in captions and mixes a synthesized sound bed.

  python3 projects/kingfisher/build.py            # full render -> output/kingfisher.mp4
  python3 projects/kingfisher/build.py --fresh    # re-render every piece (after editing PIECES)
  python3 projects/kingfisher/build.py --vo path/to/voiceover.wav   # adds VO, ducks the bed

Run from the reels/ folder.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REELS = os.path.dirname(os.path.dirname(HERE))
CLIPS = os.path.join(HERE, "clips")
WORK = os.path.join(HERE, "work")
OUT = os.path.join(REELS, "output")
W, H, FPS = 1080, 1920, 30

# ------------------------------------------------------------------ EDIT PLAN
# (clip, src_in, src_out, target_seconds). Pieces play back to back.
END = 4.032
PIECES = [
    ("02", 0.0, END, 5.0),   # 0:00 plane over India map      - hook
    ("03", 0.0, END, 5.0),   # 0:05 airport                   - 2005 entry
    ("04", 0.0, 3.0, 5.0),   # 0:10 luxury cabin              - premium seats
    ("04", 3.0, END, 2.0),   # 0:15 gold coin                 - Mallya's vision
    ("05", 0.0, 1.0, 3.0),   #      coin "1"
    ("05", 1.0, 3.0, 5.0),   # 0:20 Air Deccan merges         - 2007 acquisition
    ("05", 3.0, END, 2.0),   # 0:25 routes across India       - aircraft, routes badhe
    ("06", 0.0, 2.0, 3.0),   #      growth arrow + costs      - expenses
    ("06", 2.0, END, 5.0),   # 0:30 DEBT stacks, "!"          - karz
    ("07", 0.0, END, 5.0),   # 0:35 cancellations, unpaid salary
    ("08", 0.0, 2.0, 5.0),   # 0:40 stamp, 20 October 2012    - DGCA suspension
    ("08", 2.0, END, 5.0),   # 0:45 grounded plane, curtain   - zameen par
    ("09", 0.0, END, 5.0),   # 0:50 scales collapse           - licence expired
    ("10", 0.0, END, 5.0),   # 0:55 empire cracks + shrinks   - failure story
    ("11", 0.0, 2.0, 5.0),   # 1:00 "?" + tower               - the lesson?
    ("11", 2.0, END, 5.0),   # 1:05 tower gets a foundation   - financial discipline
    ("12", 0.0, END, 5.0),   # 1:10 seed -> rooted tree       - tikaye rakhna
]
OUTRO = ("outro-logo", 0.0, END)  # landscape logo, real time, on a blurred backdrop

# ------------------------------------------------------------------ CAPTIONS
# (start, end, text). {Y}..{/Y} = yellow highlight.
LINES = [
    "Ek waqt tha… jab Kingfisher sirf ek airline nahi, balki {Y}luxury ki pehchaan{/Y} thi.",
    "{Y}2005{/Y} mein, Kingfisher Airlines ne Indian skies mein ek naya dream lekar entry ki.",
    "Premium seats, stylish cabin crew aur {Y}royal hospitality{/Y}… flying ka experience hi badal gaya.",
    "Lekin founder {Y}Vijay Mallya{/Y} ka vision sirf luxury tak limited nahi tha.",
    "{Y}2007{/Y} mein, {Y}Air Deccan{/Y} ke acquisition ke saath Kingfisher ka empire aur bada ho gaya.",
    "Aircraft badhe, routes badhe… lekin expansion ke saath {Y}expenses{/Y} bhi badhne lage.",
    "{Y}Karz{/Y} badhta gaya, financial pressure badhta gaya… aur situation mushkil hoti gayi.",
    "Salaries delay hone lagi, flights cancel hone lagi… aur passengers ka {Y}bharosa{/Y} tootne laga.",
    "Phir aaya {Y}20 October 2012{/Y}… DGCA ne Kingfisher ka flying permit suspend kar diya.",
    "Jo airline kabhi aasman mein apni shaan dikhati thi… uske aircraft ab {Y}zameen par{/Y} khade the.",
    "{Y}December 2012{/Y} ke end tak, Kingfisher ka flying licence bhi expire ho gaya… aur kabhi renew nahi hua.",
    "Ek glamorous airline… jo kabhi success ki misaal thi, ab {Y}business failure{/Y} ki kahaani ban chuki thi.",
    "Lekin is poori kahaani se sabse bada {Y}lesson{/Y} kya milta hai?",
    "Sirf bade sapne dekhna kaafi nahi… growth ke saath {Y}financial discipline{/Y} bhi zaroori hai.",
    "Kyunki empire banana mushkil hai… lekin use {Y}tikaye rakhna{/Y} usse bhi zyada mushkil.",
]
BEAT = 5.0

# ------------------------------------------------------------------ SOUND
CUES = [
    {"t": 0.0, "sfx": "pad", "gain": 0.22, "dur": 10},
    {"t": 9.5, "sfx": "pad", "gain": 0.22, "dur": 10.5},
    {"t": 0.15, "sfx": "whoosh_long", "gain": 0.55},
    {"t": 5.0, "sfx": "whoosh", "gain": 0.45},
    {"t": 10.0, "sfx": "swish", "gain": 0.4},
    {"t": 15.0, "sfx": "ding", "gain": 0.35},
    {"t": 20.0, "sfx": "whoosh", "gain": 0.5},
    {"t": 22.0, "sfx": "pop", "gain": 0.4},
    {"t": 25.0, "sfx": "riser", "gain": 0.35},
    {"t": 24.0, "sfx": "drone", "gain": 0.3, "dur": 30},
    {"t": 53.0, "sfx": "drone", "gain": 0.3, "dur": 8},
    {"t": 30.0, "sfx": "hit", "gain": 0.55},
    {"t": 34.0, "sfx": "buzz", "gain": 0.3},
    {"t": 35.0, "sfx": "glitch", "gain": 0.35},
    {"t": 38.0, "sfx": "heartbeat", "gain": 0.4},
    {"t": 40.0, "sfx": "riser_short", "gain": 0.3},
    {"t": 41.5, "sfx": "shutter", "gain": 0.6},
    {"t": 42.6, "sfx": "boom", "gain": 0.7},
    {"t": 48.5, "sfx": "whoosh_down", "gain": 0.45},
    {"t": 50.0, "sfx": "hit", "gain": 0.4},
    {"t": 55.0, "sfx": "glitch", "gain": 0.3},
    {"t": 58.5, "sfx": "whoosh_down", "gain": 0.4},
    {"t": 60.0, "sfx": "tick", "gain": 0.4},
    {"t": 60.5, "sfx": "pad", "gain": 0.22, "dur": 10},
    {"t": 70.0, "sfx": "pad", "gain": 0.24, "dur": 9},
    {"t": 62.5, "sfx": "pop_low", "gain": 0.35},
    {"t": 66.0, "sfx": "pop", "gain": 0.35},
    {"t": 70.0, "sfx": "swish", "gain": 0.35},
    {"t": 75.0, "sfx": "whoosh_long", "gain": 0.5},
    {"t": 75.8, "sfx": "ding", "gain": 0.4},
]


def run(cmd):
    print("+", " ".join(cmd[:6]), "...")
    subprocess.run(cmd, check=True)


def render_piece(i, clip, a, b, dur):
    out = os.path.join(WORK, f"p{i:02d}.mp4")
    if os.path.exists(out) and "--fresh" not in sys.argv:
        return out  # cached; pass --fresh after changing PIECES
    k = dur / (b - a)
    vf = (
        f"trim=start={a}:end={b},setpts=PTS-STARTPTS,setpts={k:.5f}*PTS,"
        f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,"
        f"scale={W}:{H}:flags=lanczos,unsharp=5:5:0.7:5:5:0.0,setsar=1,"
        f"tpad=stop_mode=clone:stop_duration=1,trim=duration={dur},fps={FPS}"
    )
    run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(CLIPS, clip + ".mp4"),
         "-vf", vf, "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
         "-pix_fmt", "yuv420p", out])
    return out


def render_outro(i):
    clip, a, b = OUTRO
    out = os.path.join(WORK, f"p{i:02d}.mp4")
    fc = (
        f"[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS,fps={FPS},split[x][y];"
        f"[x]scale=-2:{H},crop={W}:{H},boxblur=30:2,eq=brightness=-0.04[bg];"
        f"[y]scale={W}:-2:flags=lanczos,unsharp=5:5:0.7[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[v]"
    )
    run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(CLIPS, clip + ".mp4"),
         "-filter_complex", fc, "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "16",
         "-pix_fmt", "yuv420p", out])
    return out


def ts(t, srt=False):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    if srt:
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)):03d}"
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def write_captions():
    ass = os.path.join(WORK, "captions.ass")
    srt = os.path.join(OUT, "kingfisher.srt")
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter,62,&H00FFFFFF,&H00FFFFFF,&H00101010,&H96000000,1,0,0,0,100,100,2,0,1,4,3,2,90,90,330,1
Style: Title,Inter,76,&H00FFFFFF,&H00FFFFFF,&H001A1AC8,&H00000000,1,0,0,0,100,100,2,0,1,7,0,8,60,60,190,1
Style: Sub,Inter,46,&H0000D7FF,&H00FFFFFF,&H00101010,&H00000000,1,0,0,0,100,100,6,0,1,4,0,8,60,60,290,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev, srt_lines = [], []
    for n, line in enumerate(LINES):
        t0, t1 = n * BEAT + 0.15, (n + 1) * BEAT - 0.1
        txt = line.replace("{Y}", r"{\c&H00D7FF&}").replace("{/Y}", r"{\c&HFFFFFF&}")
        ev.append(f"Dialogue: 0,{ts(t0)},{ts(t1)},Cap,,0,0,0,,{{\\fad(150,120)}}{txt}")
        plain = line.replace("{Y}", "").replace("{/Y}", "")
        srt_lines.append(f"{n + 1}\n{ts(t0, True)} --> {ts(t1, True)}\n{plain}\n")
    ev.append(r"Dialogue: 1,0:00:00.20,0:00:04.60,Title,,0,0,0,,{\fad(250,300)}KINGFISHER AIRLINES")
    ev.append(r"Dialogue: 1,0:00:00.50,0:00:04.60,Sub,,0,0,0,,{\fad(300,300)}THE RISE AND FALL")
    with open(ass, "w", encoding="utf-8") as f:
        f.write(head + "\n".join(ev) + "\n")
    with open(srt, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))
    return ass


def main():
    vo = sys.argv[sys.argv.index("--vo") + 1] if "--vo" in sys.argv else None
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)

    parts = [render_piece(i, *p) for i, p in enumerate(PIECES)]
    parts.append(render_outro(len(PIECES)))
    total = sum(p[3] for p in PIECES) + (OUTRO[2] - OUTRO[1])

    lst = os.path.join(WORK, "list.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    silent = os.path.join(WORK, "silent.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
         "-c", "copy", silent])

    cues = os.path.join(WORK, "cues.json")
    with open(cues, "w") as f:
        json.dump(CUES, f)
    bed = os.path.join(WORK, "bed.wav")
    run([sys.executable, os.path.join(REELS, "tools", "sfx.py"), "mix", cues, bed, f"{total:.3f}"])

    ass = write_captions()
    out = os.path.join(OUT, "kingfisher.mp4" if vo else "kingfisher-draft.mp4")
    if vo:
        af = ("[1:a]volume=0.55[bed];[2:a]aformat=channel_layouts=stereo,volume=1.0,asplit[v1][v2];"
              "[bed][v1]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[duck];"
              "[duck][v2]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
        inputs = ["-i", silent, "-i", bed, "-i", vo]
    else:
        af = "[1:a]loudnorm=I=-16:TP=-1.5[a]"
        inputs = ["-i", silent, "-i", bed]
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", af,
         "-vf", f"subtitles={ass}", "-map", "0:v", "-map", "[a]",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{total:.3f}",
         "-movflags", "+faststart", out])
    print(f"done -> {out} ({total:.2f}s)")


if __name__ == "__main__":
    main()
