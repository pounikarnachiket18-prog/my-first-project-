#!/usr/bin/env node
// Downloads every slot listed in <project>/images.json from Unsplash into <project>/images/<slot>.jpg.
// Needs network access to unsplash.com and images.unsplash.com.
// Usage: node tools/fetch_images.mjs [projects/phone-enemy] [--force]
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const proj = path.resolve(ROOT, process.argv.slice(2).find((a) => !a.startsWith("--")) || "projects/phone-enemy");
const force = process.argv.includes("--force");
const manifest = JSON.parse(fs.readFileSync(path.join(proj, "images.json"), "utf8"));
const dir = path.join(proj, "images");
fs.mkdirSync(dir, { recursive: true });
let ok = 0, fail = 0;
for (const [slot, info] of Object.entries(manifest)) {
  if (slot.startsWith("_")) continue;
  const out = path.join(dir, `${slot}.jpg`);
  if (fs.existsSync(out) && !force) { console.log(`skip  ${slot} (exists)`); ok++; continue; }
  const url = `https://unsplash.com/photos/${info.id}/download?force=true&w=1600`;
  const r = spawnSync("curl", ["-sSfL", "-m", "60", "-A", "Mozilla/5.0", "-o", out, url], { encoding: "utf8" });
  const isJpeg = r.status === 0 && fs.existsSync(out) && fs.readFileSync(out).subarray(0, 2).toString("hex") === "ffd8";
  if (isJpeg) { console.log(`ok    ${slot}`); ok++; }
  else { fs.rmSync(out, { force: true }); console.log(`FAIL  ${slot}: ${(r.stderr || "not a JPEG").trim()}`); fail++; }
}
console.log(`\n${ok} ready, ${fail} failed`);
if (fail) process.exitCode = 1;
