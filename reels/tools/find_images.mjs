#!/usr/bin/env node
// Search Openverse for free images (CC0 / public domain by default: no credit needed) and download them.
// Usage: node tools/find_images.mjs "city night" [--count 6] [--out downloads/images] [--tall|--wide|--square] [--commercial]
//   --commercial  also allow CC BY / BY-SA images (credit required; lines are written to credits.txt)
import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
const opt = (name, def) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : def; };
const query = args.filter((a, i) => !a.startsWith("--") && !["--count", "--out"].includes(args[i - 1])).join(" ");
if (!query) { console.error('Usage: node tools/find_images.mjs "search words" [--count 6] [--out dir] [--tall|--wide|--square] [--commercial]'); process.exit(1); }
const count = Math.min(+opt("--count", 6) || 6, 20);
const outDir = path.resolve(opt("--out", path.join("downloads", query.replace(/[^a-z0-9]+/gi, "-").toLowerCase())));
const aspect = ["tall", "wide", "square"].find((a) => args.includes("--" + a));

const u = new URL("https://api.openverse.org/v1/images/");
u.searchParams.set("q", query); u.searchParams.set("page_size", String(count)); u.searchParams.set("mature", "false");
if (args.includes("--commercial")) u.searchParams.set("license_type", "commercial"); else u.searchParams.set("license", "cc0,pdm");
if (aspect) u.searchParams.set("aspect_ratio", aspect);

const res = await fetch(u, { headers: { "User-Agent": "reels-studio/1.0" } });
if (!res.ok) { console.error(`Openverse returned ${res.status}${res.status === 429 ? " (rate limited, try again in a minute)" : ""}`); process.exit(1); }
const { results } = await res.json();
if (!results.length) { console.log("No results. Try simpler words or --commercial."); process.exit(0); }
fs.mkdirSync(outDir, { recursive: true });
const credits = [];
let n = 0;
for (const r of results) {
  const urls = [r.url, `https://api.openverse.org/v1/images/${r.id}/thumb/?full_size=true&compressed=false`];
  let saved = null;
  for (const url of urls) {
    try {
      const im = await fetch(url, { headers: { "User-Agent": "reels-studio/1.0" }, redirect: "follow" });
      const type = im.headers.get("content-type") || "";
      if (!im.ok || !type.startsWith("image/")) continue;
      const ext = type.includes("png") ? "png" : type.includes("webp") ? "webp" : "jpg";
      saved = path.join(outDir, `${String(++n).padStart(2, "0")}-${(r.title || "image").replace(/[^a-z0-9]+/gi, "-").toLowerCase().slice(0, 40)}.${ext}`);
      fs.writeFileSync(saved, Buffer.from(await im.arrayBuffer()));
      break;
    } catch {}
  }
  if (!saved) { console.log(`FAIL  ${r.title}`); continue; }
  const free = ["cc0", "pdm"].includes(r.license);
  console.log(`ok    ${path.relative(process.cwd(), saved)}  [${r.license.toUpperCase()}${free ? ", no credit needed" : ", CREDIT REQUIRED"}]`);
  credits.push(`${path.basename(saved)}\t${r.license.toUpperCase()} ${r.license_version || ""}\t${r.attribution || r.title}\t${r.foreign_landing_url}`);
}
fs.writeFileSync(path.join(outDir, "credits.txt"), credits.join("\n") + "\n");
console.log(`\nSaved ${credits.length} images + credits.txt to ${path.relative(process.cwd(), outDir) || "."}`);
