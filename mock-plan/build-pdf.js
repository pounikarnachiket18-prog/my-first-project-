// Builds mock-plan/Zero-to-Hero-Mock-Plan.pdf: three landscape A4 pages, bright colours.
// Quant, Reasoning and English only (no GA, no descriptive). Route: four prelims, two mains, then RBI Grade B Phase 1.
// Page 1 = cover, seven levels, daily routine. Pages 2-3 = day-wise plan, Day 1-20 and Day 21-40.
// Run: node mock-plan/build-pdf.js
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const L = {
  0: { name: "Start", short: "Start", c: "#5b6b7d", tint: "#eef1f5", on: "#ffffff" },
  1: { name: "SBI Clerk Prelims", short: "SBI Clerk Pre", c: "#00b140", tint: "#e2f9e9", on: "#ffffff",
       days: "Day 2–7 · 23–28 Nov", pattern: ["100 Q · 60 min", "Quant 35 · Reasoning 35 · English 30", "20 min per section"], target: "75+ / 100",
       quote: "We are what we repeatedly do. Excellence, then, is not an act, but a habit.", by: "Will Durant",
       ask: "Which five calculation shortcuts did I make automatic?" },
  2: { name: "IBPS Clerk Prelims", short: "IBPS Clerk Pre", c: "#00b8d9", tint: "#e0f7fb", on: "#ffffff",
       days: "Day 8–12 · 29 Nov–3 Dec", pattern: ["100 Q · 60 min", "Quant 35 · Reasoning 35 · English 30", "Tougher puzzles than SBI Clerk"], target: "78+ / 100",
       quote: "You have a right to your actions, but never to their fruits.", by: "Bhagavad Gita 2.47",
       ask: "Is any puzzle taking me more than 5 minutes?" },
  3: { name: "IBPS PO Prelims", short: "IBPS PO Pre", c: "#1e6bff", tint: "#e6efff", on: "#ffffff",
       days: "Day 13–17 · 4–8 Dec", pattern: ["100 Q · 60 min", "Quant 35 · Reasoning 35 · English 30", "DI and two-variable puzzles"], target: "60+ / 100",
       quote: "A mock score is a report on yesterday's preparation, not a verdict on tomorrow's exam.", by: "",
       ask: "Am I skipping the right questions, or only the ones that look hard?" },
  4: { name: "SBI PO Prelims", short: "SBI PO Pre", c: "#8b2cf5", tint: "#f1e7ff", on: "#ffffff",
       days: "Day 18–22 · 9–13 Dec", pattern: ["100 Q · 60 min", "Quant · Reasoning · English", "Hardest prelims in the family"], target: "55+ / 100",
       quote: "Fall seven times, stand up eight.", by: "Japanese proverb",
       ask: "When one section went badly, did I recover in the next one?" },
  5: { name: "SBI Clerk Mains", short: "SBI Clerk Mains", c: "#ff2d87", tint: "#ffe5f0", on: "#ffffff",
       days: "Day 23–28 · 14–19 Dec", pattern: ["Reasoning 50 Q · 45 min", "Quant 50 Q · 45 min", "English 40 Q · 35 min"], target: "85+ / 150",
       quote: "The best time to plant a tree was twenty years ago. The second best time is now.", by: "Proverb",
       ask: "Did I give each of the three sections its full time?" },
  6: { name: "SBI PO Mains", short: "SBI PO Mains", c: "#ff7300", tint: "#ffeedd", on: "#ffffff",
       days: "Day 29–33 · 20–24 Dec", pattern: ["Reasoning & Computer", "Data Analysis & Interpretation", "English · about 2½ hr in all"], target: "65+ / 160",
       quote: "Speed is accuracy, repeated until it feels easy.", by: "",
       ask: "Which DI sets did I start that I should have skipped?" },
  7: { name: "RBI Grade B Phase 1", short: "RBI Gr B Ph 1", c: "#ffbf00", tint: "#fff5d6", on: "#2b2100",
       days: "Day 34–40 · 25–31 Dec", pattern: ["Reasoning 60 Q · 45 min", "Quant 30 Q · 25 min", "English 30 Q · 25 min"], target: "70+ / 120",
       quote: "Arise, awake, and stop not till the goal is reached.", by: "Swami Vivekananda",
       ask: "Am I spending my 45 Reasoning minutes on puzzles I can finish?" }
};

const DOUBLE = ["info", "Double mock day. Re-solve every wrong and skipped question from both mocks."];
// [iso date, level, [[mock, max]], quant, reasoning, english, note]
// A note replaces the three subject cells for that day (review, double-mock or repair days).
const DAYS = [
  ["2026-11-22", 0, [["Pre 1 (cold)", 100]], "Squares to 30, cubes to 20, tables to 20.", "List the puzzle types you skipped.", "List the question types that cost marks."],
  ["2026-11-23", 1, [], "Simplification & approximation: 40 Qs.", "Inequality + syllogism: 30 Qs.", "Reading comprehension ×2."],
  ["2026-11-24", 1, [["Pre 2", 100]], "Number series: 25 Qs.", "Linear & circular seating: 6 sets.", "Error spotting: 20 Qs."],
  ["2026-11-25", 1, [["Pre 3", 100]], "Percentage, ratio, profit & loss: 30 Qs.", "Floor & box puzzles: 5 sets.", "Fillers + cloze test: 2 sets."],
  ["2026-11-26", 1, [["Pre 4", 100], ["Pre 5", 100]], "", "", "", DOUBLE],
  ["2026-11-27", 1, [], "Quant sectional ×2 + DI: table, bar, pie.", "Reasoning sectional ×2 + coding-decoding.", "English sectional ×2 + para jumbles."],
  ["2026-11-28", 1, [["Pre 6", 100], ["Pre 7", 100]], "", "", "", ["review", "Level 1 review. Compare with Day 1. Target 75+ / 100."]],
  ["2026-11-29", 2, [["Pre 1", 100]], "Quadratic equations: 30 Qs.", "Month & day based puzzles: 5 sets.", "RC ×2 + 20 new words."],
  ["2026-11-30", 2, [["Pre 2", 100]], "SI/CI, time & work: 25 Qs.", "Blood relation, direction, ranking.", "Word usage + phrase replacement."],
  ["2026-12-01", 2, [["Pre 3", 100], ["Pre 4", 100]], "", "", "", DOUBLE],
  ["2026-12-02", 2, [], "Approximation speed: 40 Qs in 20 min.", "Puzzle speed: 4 sets, 5 min each.", "Cloze test + sentence improvement."],
  ["2026-12-03", 2, [["Pre 5", 100], ["Pre 6", 100]], "", "", "", ["review", "Level 2 review. Target 78+ / 100."]],
  ["2026-12-04", 3, [["Pre 1", 100]], "Caselet & missing DI: 4 sets.", "Puzzles with two variables: 5 sets.", "Inference-based RC ×2."],
  ["2026-12-05", 3, [["Pre 2", 100]], "Arithmetic word problems: 25 Qs.", "Coded inequality + syllogism (only / a few).", "Para jumbles + odd sentence out."],
  ["2026-12-06", 3, [["Pre 3", 100], ["Pre 4", 100]], "", "", "", DOUBLE],
  ["2026-12-07", 3, [], "Quant sectional ×2 (20 min each).", "Reasoning sectional ×2 (20 min each).", "English sectional ×2 (20 min each)."],
  ["2026-12-08", 3, [["Pre 5", 100], ["Pre 6", 100]], "", "", "", ["review", "Level 3 review. Target 60+ / 100."]],
  ["2026-12-09", 4, [["Pre 1", 100]], "Radar & line DI: 4 sets.", "High-level puzzles: 4 sets.", "Long-passage RC ×2."],
  ["2026-12-10", 4, [["Pre 2", 100]], "Quantity comparison: 20 Qs.", "Circular & square puzzles: 4 sets.", "Double-blank fillers + cloze."],
  ["2026-12-11", 4, [["Pre 3", 100], ["Pre 4", 100]], "", "", "", DOUBLE],
  ["2026-12-12", 4, [], "DI with conditions: 4 sets.", "Seating with unknown number of people.", "Vocabulary in context: 20 Qs."],
  ["2026-12-13", 4, [["Pre 5", 100], ["Pre 6", 100]], "", "", "", ["review", "Level 4 review. Target 55+ / 100. The prelims ladder is done; mains start tomorrow."]],
  ["2026-12-14", 5, [["Mains 1", 150]], "Analyse: arithmetic vs DI time.", "Analyse: which puzzles to skip.", "Analyse: RC accuracy."],
  ["2026-12-15", 5, [], "Quant sectional: 50 Q in 45 min.", "Reasoning sectional: 50 Q in 45 min.", "English sectional: 40 Q in 35 min."],
  ["2026-12-16", 5, [["Mains 2", 150]], "Caselet DI: 3 sets.", "Input-output + machine coding.", "Para jumbles + column-based Qs."],
  ["2026-12-17", 5, [["Mains 3", 150]], "Data sufficiency: 15 Qs.", "Computer aptitude: 20 Qs (inside Reasoning).", "Error spotting in long sentences."],
  ["2026-12-18", 5, [], "", "", "", ["info", "Repair day. Two hours on your weakest mains section, then re-solve the error log."]],
  ["2026-12-19", 5, [["Mains 4", 150]], "", "", "", ["review", "Level 5 review. Target 85+ / 150 across Reasoning, Quant and English."]],
  ["2026-12-20", 6, [["Mains 1", 160]], "Analyse: which DI to attempt first.", "Analyse: skip decisions.", "Analyse: RC accuracy."],
  ["2026-12-21", 6, [], "Data Analysis sectional: 45 min.", "Reasoning sectional: 50 min.", "English sectional: 40 min."],
  ["2026-12-22", 6, [["Mains 2", 160]], "High-level arithmetic: 20 Qs.", "Critical reasoning: 15 Qs.", "Para summary + connectors."],
  ["2026-12-23", 6, [["Mains 3", 160]], "DI with conditions: 3 sets.", "Logical reasoning + data sufficiency.", "Vocabulary + phrasal verbs."],
  ["2026-12-24", 6, [["Mains 4", 160]], "", "", "", ["review", "Level 6 review. Target 65+ / 160. List your 10 most repeated errors on one page."]],
  ["2026-12-25", 7, [["Reasoning 1", 60]], "DI with conditions: 3 sets.", "RBI-level puzzles: 3 sets.", "RC ×2."],
  ["2026-12-26", 7, [["R+Q+E 1", 120]], "Analyse: DI time.", "Analyse: minutes per puzzle.", "Analyse: RC + cloze."],
  ["2026-12-27", 7, [["R+Q+E 2", 120]], "Quantity comparison + data sufficiency.", "Skip-or-solve drill: decide in 30 seconds.", "Vocabulary + phrasal verbs."],
  ["2026-12-28", 7, [["Quant 1", 30], ["English 1", 30]], "DI-heavy practice: 4 sets.", "Logical reasoning: 15 Qs.", "Para jumbles + odd one out."],
  ["2026-12-29", 7, [["R+Q+E 3", 120]], "", "", "", ["info", "Repair day. Two hours on the weakest of the three sections, then re-solve the error log."]],
  ["2026-12-30", 7, [["R+Q+E 4", 120], ["R+Q+E 5", 120]], "", "", "", ["info", "Two attempts back to back for exam-day stamina. Target 70+ / 120."]],
  ["2026-12-31", 7, [["Hero mock", 100]], "", "", "", ["review", "Hero test: an SBI Clerk Pre mock, the same level as Day 1. Compare the two scores and plan January around your weakest section."]]
];

const WD = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MO = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const vars = (v) => `--c:${v.c};--t:${v.tint};--on:${v.on}`;

const count = { p: 0, m: 0, r: 0 };
DAYS.forEach((d) => d[2].forEach((mk) => {
  if (d[1] === 7 && !/Hero/.test(mk[0])) count.r++;
  else if (/Mains/.test(mk[0])) count.m++;
  else count.p++;
}));
const total = count.p + count.m + count.r;

function row(d, i) {
  const [isoD, lv, mocks, q, r, e, note] = d;
  const [y, m, dd] = isoD.split("-").map(Number);
  const dt = new Date(y, m - 1, dd);
  const v = L[lv];
  const mk = mocks.length
    ? mocks.map((x) => `<div class="mk"><span>${esc(x[0])}</span><span class="bl"><i></i>/${x[1]}</span></div>`).join("")
    : `<div class="nomk">${note ? "Repair day" : "Sectionals day"}</div>`;
  const subj = note
    ? `<td colspan="3" class="note ${note[0]}"><b>${note[0] === "review" ? "Review" : "Today"}</b>${esc(note[1])}</td>`
    : `<td class="q">${esc(q)}</td><td class="r">${esc(r)}</td><td class="e">${esc(e)}</td>`;
  return `<tr style="${vars(v)}"><td class="dn">${String(i + 1).padStart(2, "0")}</td>
    <td class="dt"><span>${WD[dt.getDay()]}</span> <b>${dd} ${MO[m - 1]}</b></td>
    <td class="lv"><span class="pill">${lv ? "L" + lv : "Go"}</span> <span class="ln">${esc(v.short)}</span></td>
    <td class="mks">${mk}</td>${subj}<td class="dn2"><span class="box"></span></td></tr>`;
}

function dayTable(from, to) {
  return `<table class="dw"><colgroup><col style="width:8mm"><col style="width:19.5mm"><col style="width:30mm"><col style="width:57mm"><col><col><col><col style="width:11mm"></colgroup>
  <thead><tr><th>Day</th><th>Date</th><th>Level</th><th>Mock · your score</th><th class="hq">Quant</th><th class="hr">Reasoning</th><th class="he">English</th><th>Done</th></tr></thead>
  <tbody>${DAYS.slice(from, to).map((d, k) => row(d, from + k)).join("")}</tbody></table>`;
}

const ladder = [1, 2, 3, 4, 5, 6, 7].map((k) => {
  const v = L[k];
  return `<article class="rung" style="${vars(v)}">
    <header><p class="lvl">Level ${k}<span>${esc(v.days)}</span></p><h3>${esc(v.name)}</h3></header>
    <div class="body">
      <ul class="pat">${v.pattern.map((p) => `<li>${esc(p)}</li>`).join("")}</ul>
      <p class="tg"><span>Target</span>${esc(v.target)}</p>
      <blockquote>“${esc(v.quote)}”${v.by ? `<cite>${esc(v.by)}</cite>` : ""}</blockquote>
      <p class="ask"><span>Ask yourself</span>${esc(v.ask)}</p>
    </div>
  </article>`;
}).join("") + `<article class="route">
    <p class="lvl">The route</p>
    <ol>
      <li><b>Prelims ladder</b>L1–L4 · Day 2–22<br>SBI Clerk → IBPS Clerk → IBPS PO → SBI PO</li>
      <li><b>Mains, three sections</b>L5–L6 · Day 23–33<br>SBI Clerk Mains → SBI PO Mains</li>
      <li><b>Final target</b>L7 · Day 34–40<br>RBI Grade B Phase 1</li>
    </ol>
  </article>`;

const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Zero to Hero Mock Plan</title>
<style>
@page { size: A4 landscape; margin: 9mm 10mm; }
:root { --ink:#111827; --muted:#4b5563; --line:#d4dae3;
  --pink:#ff2d87; --violet:#8b2cf5; --blue:#1e6bff; --cyan:#00b8d9; --green:#00b140; --orange:#ff7300; --yellow:#ffd60a;
  --qc:#1e6bff; --rc:#ff2d87; --ec:#00b140; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin:0; font-family: Inter, "Liberation Sans", Arial, sans-serif; color: var(--ink); font-size: 9pt; line-height: 1.33; }
h1, h2, h3 { font-family: "Inter Display", Inter, sans-serif; margin: 0; line-height: 1.1; }
p { margin: 0; }
.page { height: 192mm; overflow: hidden; display: flex; flex-direction: column; gap: 2.6mm; }
.page + .page { break-before: page; }
.foot { margin-top: auto; display: flex; justify-content: space-between; font-size: 7pt; color: var(--muted); }
.foot b { color: var(--pink); }
.pill { display: inline-block; background: var(--c); color: var(--on); font-weight: 800; font-size: 6.8pt; letter-spacing: .06em; text-transform: uppercase; padding: .3mm 1.5mm; border-radius: .9mm; }

/* Page 1 */
.cover { background: linear-gradient(105deg, var(--pink) 0%, var(--violet) 48%, var(--blue) 100%); color: #fff; border-radius: 3.5mm; padding: 3.6mm 6mm; display: grid; grid-template-columns: 1.6fr 1fr; gap: 6mm; align-items: center; }
.cover .eye { font-size: 7.2pt; letter-spacing: .14em; text-transform: uppercase; font-weight: 700; color: var(--yellow); }
.cover h1 { font-size: 21pt; font-weight: 900; letter-spacing: -.02em; margin-top: .8mm; }
.cover .sub { font-size: 8.8pt; margin-top: 1.2mm; color: #f4ecff; }
.only { display: flex; gap: 1.6mm; margin-top: 1.8mm; flex-wrap: wrap; align-items: center; font-size: 8pt; font-weight: 600; }
.only b { background: #fff; color: var(--c); font-weight: 900; padding: .5mm 2.4mm; border-radius: 1mm; font-size: 8.4pt; }
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 2mm; }
.stats div { background: rgba(255,255,255,.16); border: 1px solid rgba(255,255,255,.35); border-radius: 1.8mm; padding: 1.4mm 2.4mm; }
.stats b { display: block; font-family: "JetBrains Mono", monospace; font-size: 14pt; color: var(--yellow); }
.stats span { font-size: 7pt; line-height: 1.15; display: block; }

.ladder { display: grid; grid-template-columns: repeat(4, 1fr); gap: 2.4mm; }
.rung { border: 1.4px solid var(--c); border-radius: 2.4mm; overflow: hidden; display: flex; flex-direction: column; background: #fff; }
.rung header { background: var(--c); color: var(--on); padding: 1.5mm 3mm 1.4mm; }
.lvl { font-size: 6.8pt; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; display: flex; justify-content: space-between; }
.lvl span { letter-spacing: .02em; text-transform: none; font-weight: 600; }
.rung h3 { font-size: 11pt; font-weight: 800; margin-top: .3mm; }
.rung .body { padding: 1.3mm 3mm 1.5mm; display: flex; flex-direction: column; gap: .9mm; flex: 1; }
.pat { margin: 0; padding: 0; list-style: none; display: grid; gap: .1mm; font-size: 7.6pt; }
.pat li::before { content: "■ "; color: var(--c); font-size: 6pt; vertical-align: 1px; }
.tg { font-weight: 800; font-size: 8.6pt; }
.tg span, .ask span { display: inline; font-size: 6.4pt; letter-spacing: .12em; text-transform: uppercase; font-weight: 800; color: var(--c); filter: brightness(.8); margin-right: 1.4mm; }
.rung blockquote { margin: 0; background: var(--t); border-radius: 1.4mm; padding: 1.5mm 2.4mm; font-weight: 700; font-size: 7.6pt; line-height: 1.2; font-family: "Inter Display", Inter, sans-serif; }
.rung cite { display: block; font-style: normal; font-weight: 500; font-size: 6.8pt; color: var(--muted); margin-top: .4mm; font-family: Inter, sans-serif; }
.ask { font-weight: 600; font-size: 7.6pt; border-top: 1px dashed var(--line); padding-top: 1mm; margin-top: auto; }
.ask span { display: block; }
.route { border-radius: 2.4mm; background: linear-gradient(150deg, var(--yellow), var(--orange) 55%, var(--pink)); color: var(--ink); padding: 2.4mm 3.2mm; }
.route .lvl { color: var(--ink); }
.route ol { margin: 1.6mm 0 0; padding: 0; list-style: none; display: grid; gap: 1.6mm; font-size: 7.8pt; }
.route li { background: rgba(255,255,255,.88); border-radius: 1.4mm; padding: 1.4mm 2.2mm; line-height: 1.3; }
.route li b { display: block; font-family: "Inter Display", Inter, sans-serif; font-size: 9pt; }

.rt-head { display: flex; justify-content: space-between; align-items: baseline; gap: 4mm; }
.rt-head h3 { font-size: 10pt; font-weight: 800; }
.rt-head p { font-size: 7.4pt; color: var(--muted); }
.routine { display: grid; grid-template-columns: repeat(6, 1fr); gap: 1.6mm; }
.blk { background: var(--c); color: #fff; border-radius: 1.6mm; padding: 1.5mm 2.3mm; font-size: 7.8pt; font-weight: 600; line-height: 1.22; }
.blk b { display: block; font-family: "JetBrains Mono", monospace; font-size: 7.2pt; font-weight: 700; margin-bottom: .3mm; }
.blk.dark { color: var(--ink); }
.rules { display: grid; grid-template-columns: 1fr 1.3fr; gap: 2.4mm; }
.tags { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.6mm; }
.tags div { background: var(--c); color: #fff; border-radius: 1.6mm; padding: 1.2mm 1.8mm; display: flex; gap: 1.6mm; align-items: center; font-size: 7.4pt; font-weight: 600; line-height: 1.15; }
.tags b { font-family: "Inter Display", Inter, sans-serif; font-size: 14pt; font-weight: 900; line-height: 1; }
.never { border: 1.4px solid var(--line); border-radius: 1.6mm; padding: 1.3mm 3mm; font-size: 7.5pt; display: grid; gap: .3mm; }
.never p::before { content: "● "; color: var(--pink); font-size: 6pt; vertical-align: 1px; }

/* Pages 2-3 */
.p-head { display: flex; justify-content: space-between; align-items: center; gap: 6mm; }
.p-head h2 { font-size: 14pt; font-weight: 900; }
.p-head h2 em { font-style: normal; color: var(--pink); }
.p-head .qt { text-align: right; font-family: "Inter Display", Inter, sans-serif; font-weight: 700; font-size: 8.6pt; background: var(--yellow); padding: 1.2mm 3mm; border-radius: 1.5mm; }
table.dw { width: 100%; border-collapse: collapse; table-layout: fixed; }
table.dw thead th { text-align: left; font-size: 6.8pt; letter-spacing: .1em; text-transform: uppercase; font-weight: 800; color: var(--muted); padding: 1.1mm 1.6mm; border-bottom: 1.4px solid var(--ink); }
table.dw thead th.hq, table.dw thead th.hr, table.dw thead th.he { color: #fff; font-size: 7.6pt; border-bottom: 0; border-radius: 1.4mm 1.4mm 0 0; }
th.hq { background: var(--qc); } th.hr { background: var(--rc); } th.he { background: var(--ec); }
table.dw td { padding: .95mm 1.8mm; border-bottom: 1px solid var(--line); vertical-align: middle; font-size: 8.3pt; line-height: 1.22; }
td.dn { font-family: "JetBrains Mono", monospace; font-weight: 800; font-size: 10pt; border-left: 1.4mm solid var(--c); }
td.dt { white-space: nowrap; } td.dt b { font-family: "JetBrains Mono", monospace; font-size: 8.2pt; }
td.dt span { font-size: 6.4pt; color: var(--muted); text-transform: uppercase; letter-spacing: .08em; }
td.lv { white-space: nowrap; } td.lv .ln { font-size: 7.5pt; font-weight: 700; }
td.mks { white-space: nowrap; }
.mk { display: inline-flex; align-items: baseline; gap: 1mm; background: var(--t); border-left: .9mm solid var(--c); padding: .3mm 1.2mm; font-weight: 700; font-size: 7.4pt; }
.mk + .mk { margin-left: 1mm; }
.bl { font-family: "JetBrains Mono", monospace; font-weight: 500; font-size: 6.6pt; color: var(--muted); }
.bl i { display: inline-block; width: 5.5mm; border-bottom: 1px solid #8a96a3; height: 2.3mm; margin-right: .4mm; }
.nomk { display: inline-block; font-size: 6.9pt; color: var(--muted); border: 1px dashed var(--line); padding: .2mm 1.3mm; }
td.q { background: #f2f6ff; } td.r { background: #fff2f7; } td.e { background: #effbf3; }
td.note { background: var(--t); font-weight: 700; font-size: 8.4pt; }
td.note b { display: inline-block; font-size: 6.4pt; letter-spacing: .1em; text-transform: uppercase; background: var(--c); color: var(--on); padding: .2mm 1.5mm; border-radius: .8mm; margin-right: 2mm; vertical-align: 1px; }
td.note.info b { background: #fff; color: var(--ink); border: 1px solid var(--c); }
td.dn2 { text-align: center; }
.box { display: inline-block; width: 3.6mm; height: 3.6mm; border: 1.3px solid var(--c); border-radius: .8mm; }
.legend { font-size: 7.2pt; color: var(--muted); display: flex; gap: 5mm; flex-wrap: wrap; }
.legend b { color: var(--ink); }
.finish { background: linear-gradient(105deg, var(--pink), var(--violet)); color: #fff; border-radius: 2mm; padding: 1.8mm 4mm; display: flex; justify-content: space-between; align-items: center; gap: 6mm; font-size: 8.2pt; }
.finish b { font-family: "Inter Display", Inter, sans-serif; font-size: 9.6pt; white-space: nowrap; }
.finish .cmp { font-weight: 800; white-space: nowrap; }
.finish .cmp i { display: inline-block; width: 11mm; border-bottom: 1px solid #fff; height: 3mm; margin: 0 .6mm; }
</style></head><body>

<section class="page">
  <div class="cover">
    <div>
      <p class="eye">Banking mock plan · 22 Nov → 31 Dec 2026 · Day 1 to Day 40</p>
      <h1>Zero to Hero Mock Plan</h1>
      <div class="only">Final target RBI Grade B Phase 1 · Only <b style="--c:var(--qc)">Quant</b><b style="--c:var(--rc)">Reasoning</b><b style="--c:var(--ec)">English</b> in every mock · no GA, no descriptive</div>
    </div>
    <div class="stats"><div><b>40</b><span>days</span></div><div><b>${count.p}</b><span>prelims mocks</span></div><div><b>${count.m}</b><span>mains mocks (R+Q+E)</span></div><div><b>${count.r}</b><span>RBI Phase 1 tests</span></div></div>
  </div>

  <div class="ladder">${ladder}</div>

  <div class="rt-head"><h3>Every day has the same shape</h3><p>The Quant, Reasoning and English columns on pages 2–3 fill the three drill blocks. On mains days the mock runs 09:00–11:30.</p></div>
  <div class="routine">
    <div class="blk" style="--c:var(--violet)"><b>07:00–08:00</b>Mock or sectionals, timers on</div>
    <div class="blk" style="--c:var(--orange)"><b>08:20–10:20</b>Analysis: re-solve every wrong and skipped Q</div>
    <div class="blk" style="--c:var(--qc)"><b>10:30–12:30</b>Quant task of the day</div>
    <div class="blk" style="--c:var(--rc)"><b>14:00–16:00</b>Reasoning task of the day</div>
    <div class="blk" style="--c:var(--ec)"><b>16:30–18:00</b>English task of the day</div>
    <div class="blk dark" style="--c:var(--yellow)"><b>20:30–21:00</b>Error log + 20 new words</div>
  </div>
  <div class="rules">
    <div class="tags">
      <div style="--c:var(--pink)"><b>A</b>Concept gap</div>
      <div style="--c:var(--orange)"><b>B</b>Knew it, too slow</div>
      <div style="--c:var(--blue)"><b>C</b>Silly mistake</div>
      <div style="--c:var(--green)"><b>D</b>Should have skipped</div>
    </div>
    <div class="never">
      <p>Tag every wrong or skipped question A, B, C or D in your error log.</p>
      <p>Accuracy below 85%? Attempt fewer next mock. Each wrong answer costs 0.25.</p>
      <p>Only 4 hours a day? Do the mock, its analysis and one subject task.</p>
    </div>
  </div>
  <p class="foot"><span>Zero to Hero Mock Plan · Quant · Reasoning · English</span><span><b>Page 1 of 3</b> · The seven levels</span></p>
</section>

<section class="page">
  <div class="p-head"><h2>Day by day · <em>Day 1 – 20</em> · the prelims ladder</h2><p class="qt">“Your first score is your starting point, not your limit.”</p></div>
  ${dayTable(0, 20)}
  <p class="legend"><span><b>Pre</b> prelims mock, all three sections</span><span><b>Today</b> replaces the three tasks on double-mock and repair days</span><span>Tick the box when the day is done</span></p>
  <p class="foot"><span>Zero to Hero Mock Plan · 22 Nov – 11 Dec 2026</span><span><b>Page 2 of 3</b> · Day 1 – 20</span></p>
</section>

<section class="page">
  <div class="p-head"><h2>Day by day · <em>Day 21 – 40</em> · mains, then RBI</h2><p class="qt">“The mock you analyse teaches more than the mock you take.”</p></div>
  ${dayTable(20, 40)}
  <p class="legend"><span><b>Mains</b> Reasoning, Quant and English sections only: /150 SBI Clerk, /160 SBI PO</span><span><b>R+Q+E</b> RBI Phase 1 without GA: 95 min, /120</span></p>
  <div class="finish"><b>Finish line · Day 40</b><span class="cmp">Day 1 <i></i>/100 → Day 40 <i></i>/100</span><span>Forty days ago you took a mock cold. On Day 40 you take it as a different candidate.</span></div>
  <p class="foot"><span>Zero to Hero Mock Plan · 12 – 31 Dec 2026</span><span><b>Page 3 of 3</b> · Day 21 – 40</span></p>
</section>
</body></html>`;

(async () => {
  const outHtml = path.join(__dirname, "print.html");
  const outPdf = path.join(__dirname, "Zero-to-Hero-Mock-Plan.pdf");
  fs.writeFileSync(outHtml, html);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1047, height: 726 }); // printable width of landscape A4
  await page.emulateMedia({ media: "print" });
  await page.goto("file://" + outHtml, { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  const fit = await page.$$eval(".page", (els) => els.map((e) => {
    const r = e.getBoundingClientRect(); const f = e.querySelector(".foot").getBoundingClientRect();
    return ((f.bottom - r.top) * 25.4 / 96).toFixed(1) + "mm";
  }));
  console.log("Footer bottom per page (limit 192mm):", fit.join(", "));
  await page.pdf({ path: outPdf, landscape: true, format: "A4", printBackground: true, preferCSSPageSize: true });
  await browser.close();
  if (!process.env.KEEP) fs.unlinkSync(outHtml);
  console.log("Wrote", outPdf, "·", total, "full mocks ·", JSON.stringify(count));
})();
