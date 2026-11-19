#!/usr/bin/env python3
"""
Seamless joiner for AI clips (Google Flow / Veo, Kling, Runway, Luma).

Clips made with first/last-frame chaining *almost* match at every join, but the
model drifts slightly: colour and brightness shift, a small zoom, a jitter. This
tool makes every join invisible:

  1. Normalises every clip to 1080x1920 @ 30 fps (same crop, no zoom jumps).
  2. Measures each join (similarity of clip A's last frame and clip B's first frame).
  3. Colour-matches the start of clip B to the end of clip A, fading the correction
     out over --match seconds so nobody notices.
  4. Cross-blends the last/first --fade frames, so tiny jitter never shows.
  5. Optional speed-fit (--durations) that keeps the first and last --keep frames at
     normal speed and compresses only the middle. Never trim the ends of a chained
     clip, because the ends are the joins.
  6. Prints a join report (before/after) and writes the joined silent video.

Usage
  python3 tools/seamless.py lastframe clip.mp4 [out.png]       # exact last frame, to use as the next first frame
  python3 tools/seamless.py check  c01.mp4 c02.mp4 ...           # join report only
  python3 tools/seamless.py join   out.mp4 c01.mp4 c02.mp4 ... [--fade 3] [--match 1.0]
                                   [--durations 4.2,4,4,...] [--keep 8]

The output has no audio; add the voiceover and SFX afterwards as with the other reels.
"""
import json
import subprocess
import sys

import numpy as np
from scipy.ndimage import uniform_filter

W, H, FPS = 1080, 1920, 30
VF = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},format=rgb24"
FRAME_BYTES = W * H * 3


def probe_frames(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    return max(1, round(float(json.loads(out)["format"]["duration"]) * FPS))


def frames(path):
    """Yield normalised RGB frames (H, W, 3) uint8."""
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", VF, "-f", "rawvideo", "-"],
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    try:
        while True:
            buf = p.stdout.read(FRAME_BYTES)
            if len(buf) < FRAME_BYTES:
                break
            yield np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    finally:
        p.stdout.close()
        p.kill()
        p.wait()


def first_frame(path):
    return next(frames(path))


def last_frame(path):
    p = subprocess.run(["ffmpeg", "-v", "error", "-sseof", "-0.5", "-i", path, "-vf", VF, "-f", "rawvideo", "-"],
                       capture_output=True, check=True)
    n = len(p.stdout) // FRAME_BYTES
    return np.frombuffer(p.stdout[(n - 1) * FRAME_BYTES:n * FRAME_BYTES], np.uint8).reshape(H, W, 3)


def ssim(a, b):
    """Grayscale SSIM on a 4x-downsampled copy (1.0 = identical)."""
    g = lambda x: (x[::4, ::4].astype(np.float64) @ [0.299, 0.587, 0.114])
    x, y = g(a), g(b)
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    mx, my = uniform_filter(x, 7), uniform_filter(y, 7)
    vx = uniform_filter(x * x, 7) - mx * mx
    vy = uniform_filter(y * y, 7) - my * my
    cxy = uniform_filter(x * y, 7) - mx * my
    s = ((2 * mx * my + c1) * (2 * cxy + c2)) / ((mx * mx + my * my + c1) * (vx + vy + c2))
    return float(s.mean())


def stats(img):
    f = img.reshape(-1, 3).astype(np.float64)
    return f.mean(0), f.std(0) + 1e-6


def color_fix(img, src, dst, w):
    """Move img's colour stats from src toward dst with weight w (0..1)."""
    if w <= 0:
        return img
    (ms, ss), (md, sd) = src, dst
    f = img.astype(np.float32)
    fixed = (f - ms) * (sd / ss) + md
    return np.clip(f + w * (fixed - f), 0, 255).astype(np.uint8)


def verdict(s):
    return "perfect" if s >= 0.97 else "good" if s >= 0.90 else "visible" if s >= 0.75 else "BAD: re-generate"


def report(paths):
    print(f"{'join':<24}{'similarity':>11}  verdict")
    rows = []
    for a, b in zip(paths, paths[1:]):
        la, fb = last_frame(a), first_frame(b)
        s0 = ssim(la, fb)
        s1 = ssim(la, color_fix(fb, stats(fb), stats(la), 1.0))
        rows.append((a, b, s0, s1))
        name = f"{a.split('/')[-1]} -> {b.split('/')[-1]}"
        print(f"{name:<24}{s0:>11.3f}  {verdict(s0)}   (after colour match: {s1:.3f} {verdict(s1)})")
    return rows


def index_map(n_src, n_out, keep):
    """Monotonic frame map: first/last `keep` frames 1:1, middle compressed or stretched."""
    if n_out >= n_src or n_src <= 2 * keep or n_out <= 2 * keep:
        return list(range(n_src))
    mid_src, mid_out = n_src - 2 * keep, n_out - 2 * keep
    mid = [keep + int(i * mid_src / mid_out) for i in range(mid_out)]
    return list(range(keep)) + mid + list(range(n_src - keep, n_src))


def join(out, paths, fade=3, match=1.0, durations=None, keep=8):
    rows = report(paths)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
                            "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    tail = []          # last `fade` frames of the previous clip, held back for blending
    total = 0
    for ci, path in enumerate(paths):
        n_src = probe_frames(path)
        n_out = round(durations[ci] * FPS) if durations and ci < len(durations) else n_src
        imap = index_map(n_src, n_out, keep)
        prev_stats = stats(last_frame(paths[ci - 1])) if ci else None
        cur_stats = stats(first_frame(path)) if ci else None
        match_n = max(1, int(match * FPS))
        out_frames, counts = [], {}
        for i in imap:
            counts[i] = counts.get(i, 0) + 1
        k = 0
        for si, fr in enumerate(frames(path)):
            for _ in range(counts.get(si, 0)):
                if ci and match > 0:
                    fr2 = color_fix(fr, cur_stats, prev_stats, max(0.0, 1 - k / match_n))
                else:
                    fr2 = fr
                if ci and k < len(tail):                       # cross-blend over the join
                    a = (k + 1) / (len(tail) + 1)
                    fr2 = (tail[k].astype(np.float32) * (1 - a) + fr2.astype(np.float32) * a).astype(np.uint8)
                out_frames.append(fr2)
                k += 1
                # stream everything except the frames we must hold back for the next join
                while len(out_frames) > fade:
                    enc.stdin.write(out_frames.pop(0).tobytes())
                    total += 1
        tail = out_frames[-fade:] if fade and ci < len(paths) - 1 else []
        if not tail:
            for fr in out_frames:
                enc.stdin.write(fr.tobytes())
                total += 1
        elif len(out_frames) > fade:
            for fr in out_frames[:-fade]:
                enc.stdin.write(fr.tobytes())
                total += 1
    enc.stdin.close()
    enc.wait()
    print(f"done -> {out}  ({total} frames, {total / FPS:.1f}s, joins blended over {fade} frames)")
    return rows


def main(argv):
    if len(argv) < 2 or argv[0] not in {"lastframe", "check", "join"}:
        print(__doc__)
        return 1
    cmd, rest = argv[0], argv[1:]
    opts, args = {}, []
    it = iter(rest)
    for a in it:
        if a.startswith("--"):
            opts[a[2:]] = next(it)
        else:
            args.append(a)
    if cmd == "lastframe":
        out = args[1] if len(args) > 1 else args[0].rsplit(".", 1)[0] + "-LAST.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.5", "-i", args[0], "-update", "1",
                        "-q:v", "1", out], check=True)
        print(f"last frame -> {out}  (upload this as the FIRST frame of the next clip)")
    elif cmd == "check":
        report(args)
    else:
        durs = [float(x) for x in opts["durations"].split(",")] if "durations" in opts else None
        join(args[0], args[1:], fade=int(opts.get("fade", 3)), match=float(opts.get("match", 1.0)),
             durations=durs, keep=int(opts.get("keep", 8)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
