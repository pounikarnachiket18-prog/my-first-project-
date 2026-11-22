// Builds mock-plan/Mock-Timetable.pdf: one printable A4 page, one mock per day, 24 Nov - 20 Dec 2026.
// Quant, Reasoning and English only. Run: node mock-plan/build-timetable.js
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

// [exam, days, colour, light tint, total marks, time]
const STAGES = [
  ["SBI Clerk Prelims", 2, "#00a63e", "#e3f8ea", 100, "60 min"],
  ["IBPS PO Prelims", 4, "#1e6bff", "#e7efff", 100, "60 min"],
  ["SBI PO Prelims", 4, "#8b2cf5", "#f1e8ff", 100, "60 min"],
  ["SBI Clerk Mains", 4, "#ff2d87", "#ffe6f1", 150, "125 min"],
  ["SBI PO Mains", 5, "#ff7300", "#ffefe0", 160, "140 min"],
  ["RBI Grade B Ph 1", 8, "#e0a800", "#fff6d8", 120, "95 min"]
];

const WD = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MO = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const start = new Date(2026, 10, 24);

const days = [];
STAGES.forEach(([exam, n, c, t, total, time]) => {
  for (let k = 1; k <= n; k++) days.push({ exam, mock: k, c, t, total, time });
});

let range = [];
const rows = days.map((d, i) => {
  const dt = new Date(start.getFullYear(), start.getMonth(), start.getDate() + i);
  const label = `${dt.getDate()} ${MO[dt.getMonth()]}`;
  if (d.mock === 1) range.push(label);
  return `<tr style="--c:${d.c};--t:${d.t}">
    <td class="day">${i + 1}</td>
    <td class="date"><b>${label}</b><span>${WD[dt.getDay()]}</span></td>
    <td class="exam"><span class="dot"></span>${d.exam}</td>
    <td class="mock">Mock ${d.mock}</td>
    <td class="time">${d.time}</td>
    <td class="w"></td><td class="w"></td><td class="w"></td>
    <td class="w tot"><span>/ ${d.total}</span></td>
    <td class="done"><span></span></td></tr>`;
}).join("");

const end = new Date(start.getFullYear(), start.getMonth(), start.getDate() + days.length - 1);
const strip = STAGES.map(([exam, n, c], i) => {
  const from = days.findIndex((d) => d.exam === exam) + 1;
  return `<div style="--c:${c}"><b>${exam}</b><span>Day ${from}${n > 1 ? "–" + (from + n - 1) : ""} · ${n} mocks</span></div>`;
}).join("");

const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Mock Timetable</title>
<style>
@page { size: A4; margin: 10mm 10mm 10mm; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font-family: Inter, "Liberation Sans", Arial, sans-serif; color: #111827; font-size: 10pt; }
h1 { white-space: nowrap; font-family: "Inter Display", Inter, sans-serif; font-size: 20pt; font-weight: 900; margin: 0; letter-spacing: -.01em; }
.top { display: flex; justify-content: space-between; align-items: end; border-bottom: 2px solid #111827; padding-bottom: 2mm; }
.top p { font-size: 9.4pt; font-weight: 600; text-align: right; }
.top p span { display: inline-block; color: #fff; font-weight: 800; padding: .4mm 2mm; border-radius: 1mm; margin-left: 1mm; }
.quote { margin-top: 3mm; background: #111827; color: #fff; border-radius: 1.6mm; padding: 2.6mm 5mm; border-left: 2.4mm solid #ff2d87; }
.quote p { font-family: "Inter Display", Inter, sans-serif; font-weight: 900; font-size: 13pt; line-height: 1.22; letter-spacing: -.005em; }
.strip { display: grid; grid-template-columns: repeat(6, 1fr); gap: 1.6mm; margin: 3mm 0; }
.strip div { border-top: 1.6mm solid var(--c); background: #f6f7f9; border-radius: 0 0 1.2mm 1.2mm; padding: 1.4mm 2mm; }
.strip b { display: block; font-size: 8pt; white-space: nowrap; }
.strip span { font-size: 7.6pt; color: #4b5563; }
table { width: 100%; border-collapse: collapse; table-layout: fixed; }
th { white-space: nowrap; font-size: 7pt; letter-spacing: .04em; text-transform: uppercase; text-align: left; padding: 1.6mm 1.6mm; border-bottom: 1.6px solid #111827; color: #374151; }
th.sub { text-align: center; }
td { white-space: nowrap; border-bottom: 1px solid #c9d0d9; padding: 0 1.6mm; height: 7.35mm; vertical-align: middle; }
tr td:first-child { border-left: 1.8mm solid var(--c); }
td.day { font-family: "JetBrains Mono", monospace; font-weight: 800; font-size: 12pt; text-align: center; background: var(--t); }
td.date b { font-family: "JetBrains Mono", monospace; font-size: 9.2pt; }
td.date span { font-size: 7.6pt; color: #4b5563; text-transform: uppercase; margin-left: 1.5mm; letter-spacing: .06em; }
td.exam { font-weight: 700; font-size: 9.2pt; }
.dot { display: inline-block; width: 2.6mm; height: 2.6mm; border-radius: 50%; background: var(--c); margin-right: 1.8mm; vertical-align: 0; }
td.mock { font-weight: 700; }
td.time { color: #4b5563; font-size: 8.8pt; }
td.w { border-left: 1px solid #c9d0d9; }
td.tot { text-align: right; font-family: "JetBrains Mono", monospace; color: #4b5563; font-size: 8.6pt; background: var(--t); }
td.done { text-align: center; border-left: 1px solid #c9d0d9; }
td.done span { display: inline-block; width: 4.4mm; height: 4.4mm; border: 1.4px solid #4b5563; border-radius: .8mm; }
tr.stage td { border-top: 1.6px solid #111827; }
.foot { display: flex; justify-content: space-between; font-size: 7.6pt; color: #4b5563; margin-top: 2.5mm; }
</style></head><body>
  <div class="top">
    <h1>Mock Timetable</h1>
    <p>${start.getDate()} Nov – ${end.getDate()} Dec 2026 · ${days.length} days · one mock a day
      <span style="background:#1e6bff">Quant</span><span style="background:#ff2d87">Reasoning</span><span style="background:#00a63e">English</span></p>
  </div>
  <div class="quote"><p>“The exam doesn’t care how tired you were. Every mock you skip is a seat you hand to someone else.”</p></div>
  <div class="strip">${strip}</div>
  <table>
    <colgroup><col style="width:9mm"><col style="width:25mm"><col style="width:41mm"><col style="width:16mm"><col style="width:16mm"><col><col><col><col style="width:18mm"><col style="width:11mm"></colgroup>
    <thead><tr><th>Day</th><th>Date</th><th>Exam</th><th>Mock</th><th>Time</th><th class="sub">Quant</th><th class="sub">Reasoning</th><th class="sub">English</th><th class="sub">Total</th><th class="sub">Done</th></tr></thead>
    <tbody>${rows}</tbody>
  </table>
  <p class="foot"><span>Mains and RBI mocks: attempt the Quant, Reasoning and English sections only. Total marks are for those three sections.</span><span>Mock Timetable · 2026</span></p>
</body></html>`;

(async () => {
  const outHtml = path.join(__dirname, "timetable.html");
  const outPdf = path.join(__dirname, "Mock-Timetable.pdf");
  // Mark the first row of each new exam so it gets a heavier rule.
  let first = new Set(STAGES.map((s) => days.findIndex((d) => d.exam === s[0])).filter((i) => i > 0));
  let k = -1;
  const marked = html.replace(/<tr style="--c/g, (m) => { k++; return first.has(k) ? '<tr class="stage" style="--c' : m; });
  fs.writeFileSync(outHtml, marked);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto("file://" + outHtml, { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: outPdf, format: "A4", printBackground: true, preferCSSPageSize: true });
  await browser.close();
  fs.unlinkSync(outHtml);
  console.log("Wrote", outPdf, "·", days.length, "days");
})();
