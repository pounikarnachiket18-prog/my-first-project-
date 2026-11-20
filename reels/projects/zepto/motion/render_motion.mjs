#!/usr/bin/env node
/**
 * Renders the full composition (index.html: base footage frames inside a camera rig + GSAP motion
 * graphics) frame by frame with Playwright, then encodes it with the base audio + synthesized SFX.
 * Needs build/frames/%05d.jpg (ffmpeg -i build/zepto-base.mp4 -q:v 3 build/frames/%05d.jpg).
 *
 *   node render_motion.mjs --preview 8.5,18,40,63,92   # composited stills -> build/motion-preview.jpg
 *   node render_motion.mjs                              # full -> ../../../output/zepto-reel-motion.mp4
 */
import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { createRequire } from "node:module";

const { chromium } = createRequire(import.meta.url)("playwright");
const HERE = path.dirname(fileURLToPath(import.meta.url));
const PROJ = path.dirname(HERE);
const REELS = path.dirname(path.dirname(PROJ));
const BUILD = path.join(PROJ, "build");
const BASE = path.join(BUILD, "zepto-base.mp4");
const OUT = process.env.OUT || path.join(REELS, "output", "zepto-reel-motion.mp4");
const args = process.argv.slice(2);
const previewIdx = args.indexOf("--preview");

const timeline = JSON.parse(fs.readFileSync(path.join(BUILD, "timeline.json"), "utf8"));
const browser = await chromium.launch({ args: ["--force-color-profile=srgb", "--disable-lcd-text"] });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
await page.addInitScript((t) => (window.TIMELINE = t), timeline);
page.on("pageerror", (e) => console.error("[page error]", e.message));
await page.goto(pathToFileURL(path.join(HERE, "index.html")).href);
await page.evaluate(() => window.REEL_READY);
const meta = await page.evaluate(() => ({ fps: REEL.fps, duration: REEL.duration, cues: REEL.cues }));
const frameSrc = (f) => `../build/frames/${String(f + 1).padStart(5, "0")}.jpg`;
const seek = (t) => page.evaluate(async ([t, src]) => { await REEL.frame(src); REEL.seek(t); },
  [t, frameSrc(Math.min(Math.round(t * meta.fps), Math.round(meta.duration * meta.fps) - 1))]);
const shot = () => page.screenshot({ type: "jpeg", quality: 93, animations: "disabled" });
console.log(`motion layer: ${meta.duration.toFixed(1)}s @${meta.fps}fps, ${meta.cues.length} sfx cues`);

if (previewIdx !== -1) {
  const times = String(args[previewIdx + 1] || "8.5,18,40,63,92").split(",").map(Number);
  const tiles = [];
  for (const [i, t] of times.entries()) {
    await seek(t);
    const comp = path.join(BUILD, `pv_${i}.jpg`), small = path.join(BUILD, `pv_s${i}.jpg`);
    fs.writeFileSync(comp, await shot());
    spawnSync("ffmpeg", ["-v", "error", "-y", "-i", comp, "-vf", "scale=432:768", small]);
    tiles.push(small);
  }
  const inputs = tiles.flatMap((p) => ["-i", p]);
  spawnSync("ffmpeg", ["-v", "error", "-y", ...inputs, "-filter_complex", `hstack=${tiles.length}`, path.join(BUILD, "motion-preview.jpg")]);
  console.log("preview -> build/motion-preview.jpg");
  await browser.close();
  process.exit(0);
}

// ---- SFX bed from the layer's cues
const cuesPath = path.join(BUILD, "motion.cues.json"), sfxWav = path.join(BUILD, "motion.sfx.wav");
fs.writeFileSync(cuesPath, JSON.stringify(meta.cues));
spawnSync("python3", [path.join(REELS, "tools", "sfx.py"), "mix", cuesPath, sfxWav, String(meta.duration)], { stdio: "inherit" });

// ---- composite: base video + piped transparent frames + sfx
const total = Math.round(meta.duration * meta.fps);
const ff = spawn("ffmpeg", ["-v", "error", "-y", "-i", BASE,
  "-f", "image2pipe", "-vcodec", "mjpeg", "-framerate", String(meta.fps), "-i", "-", "-i", sfxWav,
  "-filter_complex",
  "[1:v]format=yuv420p[v];" +
  "[2:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.7[s];" +
  "[0:a][s]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[a]",
  "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high",
  "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart",
  "-t", meta.duration.toFixed(3), OUT], { stdio: ["pipe", "inherit", "inherit"] });

const t0 = Date.now();
for (let f = 0; f < total; f++) {
  await seek(f / meta.fps);
  const buf = await shot();
  if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
  if (f % 60 === 0) process.stdout.write(`\r  frame ${f}/${total} (${((f / (Date.now() - t0)) * 1000).toFixed(1)} fps)   `);
}
ff.stdin.end();
await new Promise((r) => ff.on("close", r));
await browser.close();
console.log(`\ndone in ${((Date.now() - t0) / 1000).toFixed(0)}s -> ${OUT}`);
