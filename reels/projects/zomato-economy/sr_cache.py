#!/usr/bin/env python3
"""AI-upscale every clip once (Real-ESRGAN animevideov3, CPU via ncnn) to
1440x2560 so the 4K render has real detail. 20% of a Lanczos resize is mixed
back in to keep the paper texture. Output: media_sr/<clip>.mp4 (+ feast.png).
Resumable: clips already done are skipped."""
import glob, os, subprocess, sys, time
import numpy as np, ncnn
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA, OUT = os.path.join(HERE, "media"), os.path.join(HERE, "media_sr")
OW, OH = 1440, 2560
MIX = 0.80
os.makedirs(OUT, exist_ok=True)


def net(scale):
    n = ncnn.Net(); n.opt.num_threads = os.cpu_count(); n.opt.use_vulkan_compute = False
    base = os.path.join(HERE, "models", f"realesr-animevideov3-x{scale}")
    n.load_param(base + ".param"); n.load_model(base + ".bin")
    return n


NETS = {}
def upscale(rgb):
    h, w = rgb.shape[:2]
    scale = 2 if w >= 700 else 4
    if scale not in NETS:
        NETS[scale] = net(scale)
    a = np.ascontiguousarray(rgb.astype(np.float32).transpose(2, 0, 1) / 255.0)
    ex = NETS[scale].create_extractor(); ex.input("data", ncnn.Mat(a)); _, o = ex.extract("output")
    sr = np.clip(np.array(o).transpose(1, 2, 0) * 255 + 0.5, 0, 255).astype(np.uint8)
    im = Image.fromarray(sr)
    if im.size != (OW, OH):
        im = im.resize((OW, OH), Image.LANCZOS)
    lz = Image.fromarray(rgb).resize((OW, OH), Image.LANCZOS)
    return np.asarray(Image.blend(lz, im, MIX))


def do_clip(path):
    name = os.path.splitext(os.path.basename(path))[0]
    dst = os.path.join(OUT, name + ".mp4")
    if os.path.exists(dst):
        return
    w, h = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                    "stream=width,height", "-of", "csv=p=0", path],
                                   capture_output=True, text=True).stdout.strip().split(","))
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    tmp = dst + ".part.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}",
                            "-r", "24", "-i", "-", "-c:v", "libx264", "-preset", "fast", "-crf", "11",
                            "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    n, t0 = 0, time.time()
    while True:
        buf = dec.stdout.read(w * h * 3)
        if len(buf) < w * h * 3:
            break
        enc.stdin.write(upscale(np.frombuffer(buf, np.uint8).reshape(h, w, 3)).tobytes()); n += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    os.rename(tmp, dst)
    print(f"{name}: {n} frames in {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    img = os.path.join(OUT, "feast.png")
    if not os.path.exists(img):
        src = np.asarray(Image.open(os.path.join(MEDIA, "feast.jpg")).convert("RGB"))
        NETS[4] = NETS.get(4) or net(4)
        a = np.ascontiguousarray(src.astype(np.float32).transpose(2, 0, 1) / 255.0)
        ex = NETS[4].create_extractor(); ex.input("data", ncnn.Mat(a)); _, o = ex.extract("output")
        sr = Image.fromarray(np.clip(np.array(o).transpose(1, 2, 0) * 255 + 0.5, 0, 255).astype(np.uint8))
        lz = Image.fromarray(src).resize(sr.size, Image.LANCZOS)
        Image.blend(lz, sr, MIX).save(img); print("feast.png done", flush=True)
    clips = sorted(p for p in glob.glob(os.path.join(MEDIA, "*.mp4")) if "unused" not in p)
    for p in clips:
        do_clip(p)
    print("ALL DONE", flush=True)
