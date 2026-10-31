#!/usr/bin/env node
/**
 * Reels Studio renderer.
 *
 * Renders an HTML/GSAP composition frame-by-frame with Playwright (Chromium),
 * pipes frames into ffmpeg, mixes the composition's sound cues with tools/sfx.py
 * and muxes everything into an Instagram-ready MP4 (1080x1920, H.264, AAC).
 *
 * Composition contract (in the page):
 *   window.REEL = { width, height, fps, duration, cues: [{t, sfx, gain}], seek(t) }
 *   window.REEL_READY = Promise resolved when fonts/images are loaded.
 *
 * Usage:
 *   node tools/render.mjs projects/phone-enemy            # full render
 *   node tools/render.mjs projects/phone-enemy --preview  # contact sheet of stills
 *   node tools/render.mjs projects/phone-enemy --from 6 --to 10   # partial render
 */
import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { createRequire } from "node:module";

// Use a local playwright if installed, else the machine's global one (via NODE_PATH).
const { chromium } = createRequire(import.meta.url)("playwright");

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const args = process.argv.slice(2);
const flag = (n, d) => {
  const i = args.indexOf(`--${n}`);
  return i === -1 ? d : args[i + 1] && !args[i + 1].startsWith("--") ? args[i + 1] : true;
};
const projectDir = path.resolve(ROOT, args.find((a) => !a.startsWith("--") && !/^\d/.test(a)) || "projects/phone-enemy");
const name = path.basename(projectDir);
const outDir = path.join(ROOT, "output");
fs.mkdirSync(outDir, { recursive: true });

const imagesDir = path.join(projectDir, "images");
const available = fs.existsSync(imagesDir)
  ? fs.readdirSync(imagesDir).filter((f) => /\.(jpe?g|png|webp)$/i.test(f))
  : [];

const browser = await chromium.launch({ args: ["--force-color-profile=srgb", "--disable-lcd-text"] });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
await page.addInitScript((imgs) => (window.AVAILABLE_IMAGES = imgs), available);
page.on("pageerror", (e) => console.error("[page error]", e.message));
page.on("console", (m) => m.type() === "error" && console.error("[console]", m.text()));
await page.goto(pathToFileURL(path.join(projectDir, "index.html")).href);
await page.evaluate(() => window.REEL_READY);
const meta = await page.evaluate(() => ({
  fps: REEL.fps, duration: REEL.duration, cues: REEL.cues, width: REEL.width, height: REEL.height,
}));
console.log(`[${name}] ${meta.width}x${meta.height} @${meta.fps}fps, ${meta.duration}s, ${meta.cues.length} sound cues, ${available.length} photos`);

const seek = (t) => page.evaluate((t) => REEL.seek(t), t);
const shot = () => page.screenshot({ type: "png", animations: "disabled" });

// ---------------------------------------------------------------- preview mode
if (flag("preview")) {
  const times = String(flag("times", "")).split(",").filter(Boolean).map(Number);
  const ts = times.length ? times : Array.from({ length: 16 }, (_, i) => +(0.3 + (i * (meta.duration - 0.6)) / 15).toFixed(2));
  const dir = path.join(outDir, `${name}-preview`);
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });
  for (const [i, t] of ts.entries()) {
    await seek(t);
    fs.writeFileSync(path.join(dir, `${String(i).padStart(2, "0")}_${t.toFixed(2)}s.png`), await shot());
  }
  const cols = 4;
  spawnSync("ffmpeg", ["-v", "error", "-y", "-pattern_type", "glob", "-i", path.join(dir, "*.png"),
    "-vf", `scale=270:480,tile=${cols}x${Math.ceil(ts.length / cols)}:padding=6:color=gray`, "-frames:v", "1",
    path.join(outDir, `${name}-contact.jpg`)], { stdio: "inherit" });
  console.log(`preview -> ${dir} and output/${name}-contact.jpg`);
  await browser.close();
  process.exit(0);
}

// ---------------------------------------------------------------- full render
const from = Number(flag("from", 0));
const to = Math.min(Number(flag("to", meta.duration)), meta.duration);
const total = Math.round((to - from) * meta.fps);
const silent = path.join(outDir, `${name}.video.mp4`);
const ff = spawn("ffmpeg", ["-v", "error", "-y", "-f", "image2pipe", "-framerate", String(meta.fps), "-i", "-",
  "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-profile:v", "high",
  "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", silent], { stdio: ["pipe", "inherit", "inherit"] });

const t0 = Date.now();
for (let f = 0; f < total; f++) {
  await seek(from + f / meta.fps);
  const buf = await shot();
  if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
  if (f % 30 === 0) process.stdout.write(`\r  frame ${f}/${total}  (${((f / (Date.now() - t0)) * 1000).toFixed(1)} fps)   `);
}
ff.stdin.end();
await new Promise((r) => ff.on("close", r));
await browser.close();
console.log(`\n  video encoded in ${((Date.now() - t0) / 1000).toFixed(0)}s`);

// ---------------------------------------------------------------- audio
const cuesPath = path.join(outDir, `${name}.cues.json`);
const wavPath = path.join(outDir, `${name}.sfx.wav`);
const shifted = meta.cues.filter((c) => c.t >= from - 3 && c.t < to).map((c) => ({ ...c, t: c.t - from }))
  .filter((c) => c.t >= 0);
fs.writeFileSync(cuesPath, JSON.stringify(shifted, null, 1));
spawnSync("python3", [path.join(ROOT, "tools/sfx.py"), "mix", cuesPath, wavPath, String(to - from)], { stdio: "inherit" });

const final = path.join(outDir, `${name}.mp4`);
spawnSync("ffmpeg", ["-v", "error", "-y", "-i", silent, "-i", wavPath, "-map", "0:v", "-map", "1:a",
  "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest", "-movflags", "+faststart", final], { stdio: "inherit" });
fs.rmSync(silent);
console.log(`done -> ${final}`);
