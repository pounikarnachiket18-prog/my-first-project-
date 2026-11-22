// Builds mock-plan/Zero-to-Hero-Mock-Plan.pdf (A4, print-friendly) from the timetable data below.
// Run: node mock-plan/build-pdf.js
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const LEVELS = [
  { id: 0, name: "Starting line", short: "Start", c: "#4a5868", dates: "Sun 22 Nov" },
  { id: 1, name: "SBI Clerk Prelims", c: "#25704f", dates: "23 – 29 Nov",
    pattern: [["Paper", "100 Q · 60 min"], ["Sections", "English 30 · Numerical 35 · Reasoning 35"], ["Timer", "20 min per section"]],
    target: "Starting score → 75+ / 100",
    why: "Easiest paper in the family. Builds calculation speed and the basic puzzle types everything else rests on." },
  { id: 2, name: "IBPS Clerk", c: "#2a62a3", dates: "30 Nov – 6 Dec",
    pattern: [["Prelims", "100 Q · 60 min"], ["Mains", "190 Q · 160 min"], ["Mains split", "GA 50 · English 40 · Reasoning & Computer 50 · Quant 50"]],
    target: "Prelims 78+ · Mains 90+ / 200",
    why: "Same prelims you just practised, plus your first mains. General Awareness and computer aptitude enter here." },
  { id: 3, name: "IBPS PO", c: "#6b43a6", dates: "7 – 13 Dec",
    pattern: [["Prelims", "100 Q · 60 min"], ["Mains", "about 155 Q · 3 hr objective"], ["Descriptive", "Essay + letter · 30 min"]],
    target: "Prelims 60+ · Mains 75+ / 200",
    why: "Harder puzzles, data interpretation as its own section, and descriptive writing for the first time." },
  { id: 4, name: "SBI PO", c: "#a54d26", dates: "14 – 20 Dec",
    pattern: [["Prelims", "100 Q · 60 min"], ["Mains", "objective · 3 hr"], ["Descriptive", "Essay + letter · 30 min"]],
    target: "Prelims 55+ · Mains 70+ / 200",
    why: "Toughest bank paper. Lower raw scores are normal here; judge yourself by percentile in your test series." },
  { id: 5, name: "SBI Clerk Mains", c: "#1b7878", dates: "21 – 24 Dec",
    pattern: [["Mains", "190 Q · 160 min"], ["Split", "GA 50/35m · English 40/35m · Quant 50/45m · Reasoning & CA 50/45m"]],
    target: "100+ / 200",
    why: "After PO-level papers, clerk mains feels fast. Use that to push attempts and lock in GA before RBI." },
  { id: 6, name: "RBI Grade B Phase 2", c: "#80600f", dates: "25 – 31 Dec",
    pattern: [["Paper I", "Economic & Social Issues · 100 marks · 120 min"], ["Paper II", "English (Writing) · 100 marks · 90 min"], ["Paper III", "Finance & Management · 100 marks · 120 min"], ["I & III", "half objective (30 min), half descriptive (90 min)"]],
    target: "Finish all three papers in time; 50%+ in the objective parts",
    why: "A different exam: syllabus-heavy, with typed descriptive answers. This week is your introduction, not the finish line." }
];

// A quote and a question to ask yourself, per level. Unattributed lines are written for this plan.
const MOTIVATION = {
  0: { q: "Your first score is your starting point, not your limit.", by: "", ask: "What score am I starting from, and can I look at it honestly without getting discouraged?" },
  1: { q: "We are what we repeatedly do. Excellence, then, is not an act, but a habit.", by: "Will Durant", ask: "Which five calculation shortcuts did I make automatic this week?" },
  2: { q: "You have a right to your actions, but never to their fruits.", by: "Bhagavad Gita, 2.47", ask: "Did I attempt every section of the mains, or did one section eat my time?" },
  3: { q: "A mock score is a report on yesterday's preparation, not a verdict on tomorrow's exam.", by: "", ask: "Am I skipping the right questions, or only the ones that look hard?" },
  4: { q: "Fall seven times, stand up eight.", by: "Japanese proverb", ask: "When one section went badly, did I recover in the next one?" },
  5: { q: "The best time to plant a tree was twenty years ago. The second best time is now.", by: "Proverb", ask: "How many more questions am I attempting than in Level 2, at the same accuracy?" },
  6: { q: "Take up one idea. Make that one idea your life. Think of it, dream of it, live on that idea.", by: "Swami Vivekananda", ask: "Can I explain each ESI and F&M topic in 200 words without my notes?" }
};

const DAYS = [
  { d: "2026-11-22", L: 0, m: [["p", "SBI Clerk Pre · Mock 1", 100, "Starting score, taken cold"]],
    plan: [["Work", "No preparation before this mock. Two hours of analysis after it."], ["Set up", "Error log notebook (date, mock, section, topic, tag A/B/C/D, fix). Read the SBI Clerk syllabus once."], ["GA", "Start a 6-month current affairs capsule (May – Oct 2026)."]] },
  { d: "2026-11-23", L: 1, m: [],
    plan: [["Sectionals", "Quant ×2, Reasoning ×2, English ×2 (20 min each)."], ["Drill", "Simplification & approximation (40 Qs, daily from now on), number series, inequality."], ["GA", "Current affairs, last week."]] },
  { d: "2026-11-24", L: 1, m: [["p", "SBI Clerk Pre · Mock 2", 100]],
    plan: [["Drill", "Puzzles and seating: linear, circular, floor (6 sets)."], ["GA", "RBI functions and monetary policy tools (repo, CRR, SLR, OMO)."]] },
  { d: "2026-11-25", L: 1, m: [["p", "SBI Clerk Pre · Mock 3", 100]],
    plan: [["Drill", "Arithmetic: percentage, ratio, profit & loss, SI/CI (30 Qs)."], ["English", "2 reading comprehensions daily from today."], ["GA", "Current affairs."]] },
  { d: "2026-11-26", L: 1, m: [["p", "SBI Clerk Pre · Mock 4", 100, "Morning"], ["p", "SBI Clerk Pre · Mock 5", 100, "Afternoon"]],
    plan: [["Work", "Double mock day. Analysis only, no new topics."], ["GA", "15 minutes, light."]] },
  { d: "2026-11-27", L: 1, m: [],
    plan: [["Repair", "6 sectionals on your two weakest sections."], ["Drill", "Data interpretation (table, bar, pie: 4 sets), syllogism, coding-decoding."], ["GA", "Current affairs."]] },
  { d: "2026-11-28", L: 1, m: [["p", "SBI Clerk Pre · Mock 6", 100]],
    plan: [["Drill", "Re-solve every A and C question in the error log."], ["English", "Para jumbles, fillers, error spotting."], ["GA", "Weekly current affairs quiz."]] },
  { d: "2026-11-29", L: 1, m: [["p", "SBI Clerk Pre · Mock 7", 100], ["p", "SBI Clerk Pre · Mock 8", 100, "Back to back, exam-day practice"]],
    plan: [["Review", "Level 1 review: compare with Mock 1. Target 75+. Below 65? Repeat the 25 and 27 Nov drills in Level 2's free slots."]] },

  { d: "2026-11-30", L: 2, m: [["p", "IBPS Clerk Pre · Mock 1", 100]],
    plan: [["Learn", "Computer awareness basics: memory, networking, shortcuts, MS Office (1 hr)."], ["GA", "Banking awareness: types of banks, accounts, KYC, NPAs."]] },
  { d: "2026-12-01", L: 2, m: [["m", "IBPS Clerk Mains · Mock 1", 200, "Your first mains"]],
    plan: [["Work", "First full mains. In analysis, note minutes spent per section against 35/35/45/45."], ["GA", "Write every missed GA question into the GA notebook."]] },
  { d: "2026-12-02", L: 2, m: [["p", "IBPS Clerk Pre · Mock 2", 100]],
    plan: [["Sectionals", "Mains-level Reasoning (tougher puzzles, input-output) ×1, Mains Quant (caselet DI, arithmetic) ×1."], ["English", "Cloze test, error spotting."]] },
  { d: "2026-12-03", L: 2, m: [["p", "IBPS Clerk Pre · Mock 3", 100], ["p", "IBPS Clerk Pre · Mock 4", 100]],
    plan: [["GA", "Static GK: capitals and currencies, bank headquarters and taglines, national parks."]] },
  { d: "2026-12-04", L: 2, m: [["m", "IBPS Clerk Mains · Mock 2", 200]],
    plan: [["Work", "Fix the time split you noted on 1 Dec. Attempt GA first: it takes the least time."], ["GA", "Current affairs."]] },
  { d: "2026-12-05", L: 2, m: [["p", "IBPS Clerk Pre · Mock 5", 100]],
    plan: [["Sectionals", "GA 50 Q in 35 min ×2, computer aptitude 20 Q."], ["Drill", "Error log re-solve."]] },
  { d: "2026-12-06", L: 2, m: [["m", "IBPS Clerk Mains · Mock 3", 200]],
    plan: [["Review", "Level 2 review: Prelims 78+, Mains 90+ / 200 with every section attempted."]] },

  { d: "2026-12-07", L: 3, m: [["p", "IBPS PO Pre · Mock 1", 100]],
    plan: [["Descriptive", "Learn the formal letter and essay formats. Write 1 letter (150 words)."], ["Drill", "DI: missing data, caselets."]] },
  { d: "2026-12-08", L: 3, m: [["p", "IBPS PO Pre · Mock 2", 100], ["p", "IBPS PO Pre · Mock 3", 100]],
    plan: [["Drill", "Harder puzzles (box, scheduling with two variables), quadratic equations."]] },
  { d: "2026-12-09", L: 3, m: [["m", "IBPS PO Mains · Mock 1", 200, "+30 min descriptive"]],
    plan: [["Work", "First PO mains. Write the descriptive right after, as in the real exam."], ["GA", "Current affairs."]] },
  { d: "2026-12-10", L: 3, m: [["p", "IBPS PO Pre · Mock 4", 100]],
    plan: [["Sectionals", "Reasoning & Computer (data sufficiency, coded inequality, critical reasoning), Data Analysis (45 min)."], ["English", "Word usage, paragraph summary, connectors."]] },
  { d: "2026-12-11", L: 3, m: [["m", "IBPS PO Mains · Mock 2", 200, "+30 min descriptive"]],
    plan: [["GA", "Write every missed GA question into the GA notebook."]] },
  { d: "2026-12-12", L: 3, m: [["p", "IBPS PO Pre · Mock 5", 100]],
    plan: [["GA", "Economy: inflation, GDP, fiscal deficit terms, latest RBI policy decisions."], ["Descriptive", "2 essays, 15 minutes each, typed."]] },
  { d: "2026-12-13", L: 3, m: [["m", "IBPS PO Mains · Mock 3", 200, "+30 min descriptive"]],
    plan: [["Review", "Level 3 review: Prelims 60+, Mains 75+ / 200."]] },

  { d: "2026-12-14", L: 4, m: [["p", "SBI PO Pre · Mock 1", 100]],
    plan: [["Drill", "High-level DI: radar charts, arithmetic DI, DI with conditions."]] },
  { d: "2026-12-15", L: 4, m: [["p", "SBI PO Pre · Mock 2", 100], ["p", "SBI PO Pre · Mock 3", 100]],
    plan: [["English", "Inference-based reading comprehension, vocabulary in context."]] },
  { d: "2026-12-16", L: 4, m: [["m", "SBI PO Mains · Mock 1", 200, "+30 min descriptive"]],
    plan: [["Work", "Letter + essay in 30 minutes after the objective paper."], ["GA", "Current affairs."]] },
  { d: "2026-12-17", L: 4, m: [["p", "SBI PO Pre · Mock 4", 100]],
    plan: [["Sectionals", "Reasoning & Computer (50 min), Data Analysis & Interpretation (45 min)."]] },
  { d: "2026-12-18", L: 4, m: [["m", "SBI PO Mains · Mock 2", 200, "+30 min descriptive"]],
    plan: [["GA", "Write every missed GA question into the GA notebook."]] },
  { d: "2026-12-19", L: 4, m: [["p", "SBI PO Pre · Mock 5", 100]],
    plan: [["GA", "Economy and banking: Union Budget, government schemes, RBI reports, financial terms."], ["Descriptive", "2 pieces, typed and timed."]] },
  { d: "2026-12-20", L: 4, m: [["m", "SBI PO Mains · Mock 3", 200, "+30 min descriptive"]],
    plan: [["Review", "Level 4 review: Prelims 55+, Mains 70+ / 200. Compare percentiles, not raw scores, with Level 3."]] },

  { d: "2026-12-21", L: 5, m: [["m", "SBI Clerk Mains · Mock 1", 200]],
    plan: [["Work", "After PO papers this should feel faster. Push attempts, keep accuracy above 80%."]] },
  { d: "2026-12-22", L: 5, m: [],
    plan: [["Sectionals", "All four at mains timers: GA 50/35m, English 40/35m, Quant 50/45m, Reasoning & CA 50/45m."], ["GA", "6-month current affairs rapid revision."]] },
  { d: "2026-12-23", L: 5, m: [["m", "SBI Clerk Mains · Mock 2", 200]],
    plan: [["GA", "Banking awareness revision from the GA notebook."]] },
  { d: "2026-12-24", L: 5, m: [["m", "SBI Clerk Mains · Mock 3", 200]],
    plan: [["Review", "Bank exams wrap-up: target 100+ / 200. List your 10 most repeated errors on one page. Read the RBI Grade B Phase 2 syllabus tonight."]] },

  { d: "2026-12-25", L: 6, m: [],
    plan: [["Learn", "ESI and Finance & Management syllabus walk-through. Notes from the Economic Survey and Budget highlights."], ["Sectionals", "ESI objective, 30 Q."], ["Descriptive", "2 answers of about 200 words each."]] },
  { d: "2026-12-26", L: 6, m: [["r", "RBI Paper II · English · Mock 1", 100, "Essay, précis, comprehension · 90 min, typed"]],
    plan: [["Read", "F&M: financial system, markets and regulators."]] },
  { d: "2026-12-27", L: 6, m: [["r", "RBI Paper I · ESI · Mock 1", 100, "120 min"]],
    plan: [["Work", "Compare your answers with the model answers line by line: structure, data points, word count."]] },
  { d: "2026-12-28", L: 6, m: [["r", "RBI Paper III · F&M · Mock 1", 100, "120 min"]],
    plan: [["Read", "Management: motivation and leadership theories, corporate governance."]] },
  { d: "2026-12-29", L: 6, m: [],
    plan: [["Descriptive", "Answer-writing drill: 6 ESI + 6 F&M answers, timed."], ["English", "1 précis + 1 essay, typed."], ["Sectionals", "ESI and F&M objective, 30 Q each."]] },
  { d: "2026-12-30", L: 6, m: [["r", "RBI Paper I · ESI · Mock 2", 100], ["r", "RBI Paper II · English · Mock 2", 100], ["r", "RBI Paper III · F&M · Mock 2", 100]],
    plan: [["Work", "Full Phase 2 practice day. The real exam runs all three papers on one day, so build that stamina here."]] },
  { d: "2026-12-31", L: 6, m: [["p", "SBI Clerk Pre · Hero mock", 100, "Same level as your 22 Nov start"]],
    plan: [["Review", "Hero test: put this score next to Mock 1. Review the whole error log and plan January 2027 around your weakest level."]] }
];

const WD = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MO = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const dt = (iso) => { const [y, m, d] = iso.split("-").map(Number); return new Date(y, m - 1, d); };
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

function quote(lv, cls = "") {
  const m = MOTIVATION[lv];
  return `<figure class="quote ${cls}"><blockquote>${esc(m.q)}</blockquote>${m.by ? `<figcaption>${esc(m.by)}</figcaption>` : ""}</figure>`;
}

function dayRows(days) {
  return days.map((x) => {
    const d = dt(x.d);
    const mocks = x.m.length
      ? x.m.map((mk) => `<div class="mk"><div class="mk-name">${esc(mk[1])}${mk[3] ? `<span>${esc(mk[3])}</span>` : ""}</div><div class="write"><i></i> / ${mk[2]}</div></div>`).join("")
      : `<div class="nomk">No full mock. Sectionals and concepts.</div>`;
    const plan = x.plan.map((p) => `<p class="${p[0] === "Review" ? "rv" : ""}"><b>${esc(p[0])}</b> ${esc(p[1])}</p>`).join("");
    return `<tr><td class="date"><span class="dn">${d.getDate()} ${MO[d.getMonth()]}</span><span class="wd">${WD[d.getDay()]}</span></td><td class="mocks">${mocks}</td><td class="plan">${plan}</td><td class="tick"><span class="box"></span></td></tr>`;
  }).join("");
}

function levelSection(ids, title) {
  const lvls = ids.map((i) => LEVELS[i]);
  const main = lvls[lvls.length - 1];
  const days = DAYS.filter((x) => ids.includes(x.L));
  const n = days.reduce((a, x) => a + x.m.length, 0);
  const mot = MOTIVATION[main.id];
  return `<section class="level" style="--c:${main.c}">
    <header class="lv-head">
      <div><p class="eyebrow">${main.id ? "Level " + main.id : ""} · ${esc(ids.length > 1 ? "22 – 29 Nov" : main.dates)} · ${n} full mocks</p><h2>${esc(title || main.name)}</h2></div>
      ${main.target ? `<p class="target"><span>Target</span>${esc(main.target)}</p>` : ""}
    </header>
    <div class="band">${quote(main.id)}<div class="ask"><p class="eyebrow">Answer at the end of this level</p><p class="askq">${esc(mot.ask)}</p><div class="lines"><i></i></div></div></div>
    <table class="days"><thead><tr><th>Date</th><th>Full mocks (write your score)</th><th>Plan for the day</th><th>Done</th></tr></thead><tbody>${dayRows(days)}</tbody></table>
  </section>`;
}

// Score tracker rows
let n = 0;
const trackerRows = DAYS.flatMap((x) => x.m.map((mk) => {
  n++;
  const d = dt(x.d);
  return `<tr><td class="num">${n}</td><td class="num">${d.getDate()} ${MO[d.getMonth()]}</td><td>${esc(mk[1])}</td><td class="blank num">/ ${mk[2]}</td><td class="blank"></td><td class="blank"></td><td class="blank"></td></tr>`;
})).join("");

// Count table
const countRows = LEVELS.map((L) => {
  const days = DAYS.filter((x) => x.L === L.id);
  const c = { p: 0, m: 0, r: 0 };
  days.forEach((x) => x.m.forEach((mk) => c[mk[0]]++));
  return { name: (L.id ? "L" + L.id + " · " : "") + L.name, dates: L.dates, days: days.length, ...c };
});
const tot = countRows.reduce((a, r) => ({ days: a.days + r.days, p: a.p + r.p, m: a.m + r.m, r: a.r + r.r }), { days: 0, p: 0, m: 0, r: 0 });

const ladderCards = LEVELS.slice(1).map((L) => `<article class="rung" style="--c:${L.c}">
  <div class="rung-top"><span class="lvl">Level ${L.id}</span><span>${esc(L.dates)}</span></div>
  <h3>${esc(L.name)}</h3>
  <dl>${L.pattern.map((r) => `<dt>${esc(r[0])}</dt><dd>${esc(r[1])}</dd>`).join("")}<dt>Target</dt><dd><b>${esc(L.target)}</b></dd></dl>
  <p class="why">${esc(L.why)}</p></article>`).join("");

const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Zero to Hero Mock Plan</title>
<style>
@page { size: A4; margin: 16mm 15mm 18mm; }
:root { --ink:#121c28; --muted:#4e5b6a; --line:#cfd7e0; --soft:#eef2f6; --accent:#1c56c4; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin:0; font-family: Inter, "Liberation Sans", Arial, sans-serif; color: var(--ink); font-size: 10.5pt; line-height: 1.45; }
h1,h2,h3 { font-family: "Inter Display", Inter, sans-serif; margin:0; line-height:1.15; }
p { margin:0; }
.eyebrow { font-size: 7.8pt; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); font-weight: 600; }
.num, .mono { font-family: "JetBrains Mono", "DejaVu Sans Mono", monospace; font-variant-numeric: tabular-nums; }
.page { break-after: page; }

/* Cover */
.cover { min-height: 255mm; display: flex; flex-direction: column; gap: 9mm; }
.cover-band { background: #142a4f; color: #fff; border-radius: 4mm; padding: 14mm 12mm 12mm; display:grid; gap: 5mm; }
.cover-band .eyebrow { color: #b9c9e6; }
.cover h1 { font-size: 38pt; font-weight: 800; letter-spacing: -.02em; }
.cover .sub { font-size: 12.5pt; color: #dbe4f3; max-width: 150mm; }
.climb { display:flex; flex-wrap: wrap; gap: 2mm; margin-top: 2mm; }
.climb span { font-size: 8.6pt; font-weight: 600; padding: 1.2mm 2.6mm; border-radius: 1.5mm; background: rgba(255,255,255,.12); }
.climb span b { color: #ffd27a; margin-right: 1.2mm; }
.stats { display:grid; grid-template-columns: repeat(4, 1fr); gap: 4mm; }
.stat { border: 1px solid var(--line); border-radius: 2.5mm; padding: 4mm; }
.stat b { display:block; font-family: "JetBrains Mono", monospace; font-size: 22pt; }
.stat span { color: var(--muted); font-size: 9pt; }
.quote { margin: 0; padding: 5mm 6mm; border-left: 1.4mm solid var(--c, var(--accent)); background: var(--soft); border-radius: 0 2mm 2mm 0; }
.quote blockquote { margin:0; font-family: "Inter Display", Inter, sans-serif; font-size: 13.5pt; font-weight: 600; line-height: 1.35; }
.quote figcaption { margin-top: 2mm; color: var(--muted); font-size: 9pt; }
.quote figcaption::before { content: "— "; }
.quote.big blockquote { font-size: 17pt; }
.how h3 { font-size: 13pt; margin-bottom: 3mm; }
.how ol { margin:0; padding-left: 5mm; display:grid; gap: 2mm; font-size: 10.5pt; }
.tags { display:grid; grid-template-columns: repeat(4,1fr); gap: 3mm; margin-top: 3mm; }
.tags div { border:1px solid var(--line); border-radius: 2mm; padding: 2.5mm 3mm; font-size: 9pt; }
.tags b { display:block; font-family: "JetBrains Mono", monospace; font-size: 13pt; color: var(--accent); }

/* Ladder */
.sec-head { display:grid; gap: 1.5mm; margin-bottom: 5mm; }
.sec-head h2 { font-size: 20pt; }
.sec-head p.lede { color: var(--muted); max-width: 165mm; }
.ladder { display:grid; grid-template-columns: 1fr 1fr; gap: 4mm; }
.rung { border:1px solid var(--line); border-top: 1.4mm solid var(--c); border-radius: 2mm; padding: 4mm; display:grid; gap: 2mm; break-inside: avoid; }
.rung-top { display:flex; justify-content: space-between; font-size: 8.5pt; color: var(--muted); }
.rung .lvl { color: var(--c); font-weight: 700; text-transform: uppercase; letter-spacing: .08em; }
.rung h3 { font-size: 13pt; }
.rung dl { margin:0; display:grid; grid-template-columns: auto 1fr; gap: 1mm 3mm; font-size: 9.3pt; }
.rung dt { color: var(--muted); }
.rung dd { margin:0; }
.rung .why { font-size: 9pt; color: var(--muted); }
.note { font-size: 8.8pt; color: var(--muted); margin-top: 4mm; }

/* Routines */
.routines { display:grid; grid-template-columns: 1fr 1fr 1fr; gap: 4mm; }
.routine { border:1px solid var(--line); border-radius: 2mm; padding: 4mm; }
.routine h3 { font-size: 11.5pt; margin-bottom: 2.5mm; }
.routine ol { list-style:none; margin:0; padding:0; display:grid; gap: 2mm; font-size: 9pt; }
.routine li span { display:block; font-family: "JetBrains Mono", monospace; font-size: 8pt; color: var(--muted); }
.rules { display:grid; grid-template-columns: 1fr 1fr; gap: 6mm; margin-top: 6mm; }
.rules h3 { font-size: 11.5pt; margin-bottom: 2mm; }
.rules ul { margin:0; padding-left: 4.5mm; display:grid; gap: 1.5mm; font-size: 9.6pt; }

/* Level pages */
.level { break-before: page; display:grid; gap: 3.5mm; }
.band { display:grid; grid-template-columns: 1.15fr 1fr; gap: 4mm; }
.band .quote blockquote { font-size: 11.5pt; }
.band .quote { padding: 3.5mm 4.5mm; }
.lv-head { display:flex; justify-content: space-between; align-items: end; gap: 6mm; border-bottom: 1.2mm solid var(--c); padding-bottom: 3mm; }
.lv-head .eyebrow { color: var(--c); }
.lv-head h2 { font-size: 22pt; letter-spacing: -.01em; }
.target { text-align: right; font-weight: 700; font-size: 10.5pt; max-width: 75mm; }
.target span { display:block; font-size: 7.8pt; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); font-weight: 600; }
table.days { width:100%; border-collapse: collapse; }
table.days th { text-align:left; font-size: 7.8pt; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); padding: 2mm 2.5mm; border-bottom: 1px solid var(--ink); }
table.days td { vertical-align: top; padding: 2.3mm 2.5mm; border-bottom: 1px solid var(--line); }
table.days tr { break-inside: avoid; }
td.date { width: 17mm; }
.dn { display:block; font-family: "JetBrains Mono", monospace; font-weight: 700; font-size: 11pt; white-space: nowrap; }
.wd { display:block; font-size: 8pt; text-transform: uppercase; letter-spacing: .1em; color: var(--muted); }
td.mocks { width: 76mm; }
.mk { display:flex; justify-content: space-between; align-items: center; gap: 2mm; border: 1px solid var(--line); border-left: 1mm solid var(--c); border-radius: 1.2mm; padding: 1.5mm 2.5mm; margin-bottom: 1.5mm; }
.mk:last-child { margin-bottom: 0; }
.mk-name { flex: 1 1 auto; min-width: 0; font-weight: 600; font-size: 9.3pt; }
.mk-name span { display:block; font-weight: 400; color: var(--muted); font-size: 8.2pt; }
.write { flex: none; white-space: nowrap; font-size: 8.4pt; color: var(--muted); display:flex; align-items: end; gap: 1.5mm; }
.write i { display:inline-block; width: 10mm; border-bottom: 1px solid #8a96a3; height: 4mm; }
.nomk { font-size: 9pt; color: var(--muted); border: 1px dashed var(--line); border-radius: 1.2mm; padding: 1.8mm 2.5mm; }
td.plan p { font-size: 9.6pt; margin-bottom: 1.2mm; }
td.plan p:last-child { margin-bottom: 0; }
td.plan b { font-size: 7.6pt; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); margin-right: 1mm; }
td.plan p.rv { font-weight: 600; }
td.plan p.rv b { color: var(--c); }
td.tick { width: 12mm; text-align: center; }
.box { display:inline-block; width: 5.5mm; height: 5.5mm; border: 1.3px solid #6b7785; border-radius: 1mm; }
.ask { border: 1px solid var(--line); border-radius: 2mm; padding: 3.5mm 4mm; break-inside: avoid; }
.askq { font-weight: 600; font-size: 10.5pt; margin-top: 1mm; }
.lines i { display:block; border-bottom: 1px solid var(--line); height: 8mm; }

/* Tracker */
.tracker { break-before: page; }
table.grid { width: 100%; border-collapse: collapse; font-size: 9.2pt; }
table.grid th { text-align:left; font-size: 7.6pt; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); padding: 2mm; border-bottom: 1px solid var(--ink); }
table.grid td { padding: 2.2mm 2mm; border-bottom: 1px solid var(--line); }
table.grid tr { break-inside: avoid; }
table.grid td.blank { border-left: 1px solid var(--line); }
table.grid td.num { white-space: nowrap; }
table.grid thead { display: table-header-group; }
table.count td, table.count th { padding: 2.5mm 3mm; }
table.count td.r, table.count th.r { text-align: right; font-family: "JetBrains Mono", monospace; }
table.count tr.total td { font-weight: 700; border-top: 1px solid var(--ink); }

.finale { break-before: page; display:grid; gap: 5mm; }
.finale .reflect { display:grid; gap: 4mm; }
.finale .reflect div { border:1px solid var(--line); border-radius: 2mm; padding: 3mm 4mm; break-inside: avoid; }
.finale .reflect p { font-weight: 600; }
</style></head><body>

<section class="page cover">
  <div class="cover-band">
    <p class="eyebrow">Banking mock plan · 22 Nov → 31 Dec 2026</p>
    <h1>Zero to Hero<br>Mock Plan</h1>
    <p class="sub">Six levels, one exam family at a time, each harder than the last. Every full mock is followed by an analysis block at least as long as the mock itself.</p>
    <div class="climb">${LEVELS.slice(1).map((L) => `<span><b>${L.id}</b>${esc(L.name)}</span>`).join("")}</div>
  </div>
  <div class="stats">
    <div class="stat"><b>40</b><span>days</span></div>
    <div class="stat"><b>${tot.p}</b><span>prelims mocks</span></div>
    <div class="stat"><b>${tot.m}</b><span>bank mains mocks</span></div>
    <div class="stat"><b>${tot.r}</b><span>RBI Phase 2 papers</span></div>
  </div>
  <figure class="quote big"><blockquote>Arise, awake, and stop not till the goal is reached.</blockquote><figcaption>Swami Vivekananda</figcaption></figure>
  <div class="how">
    <h3>How to use this plan</h3>
    <ol>
      <li>Print it, or keep it open beside your test series. Each level has its own pages with a box to tick for every day.</li>
      <li>Write your score next to every mock on the day you take it, then copy it into the score tracker at the back.</li>
      <li>Tag every wrong or skipped question in your error log with one of the four letters below.</li>
      <li>On each level's last day, answer the question at the bottom of that level's page before you move up.</li>
    </ol>
    <div class="tags">
      <div><b>A</b>Concept gap: learn the topic again</div>
      <div><b>B</b>Knew it, too slow: drill for speed</div>
      <div><b>C</b>Silly mistake: slow down on that type</div>
      <div><b>D</b>Should have skipped: fix question selection</div>
    </div>
  </div>
</section>

<section class="page">
  <div class="sec-head"><p class="eyebrow">The ladder</p><h2>Six levels, in this order</h2><p class="lede">You climb from the easiest prelims to the hardest descriptive paper. Each level reuses what the last one built and adds one new demand.</p></div>
  <div class="ladder">${ladderCards}</div>
  <p class="note">Patterns are from the most recent notifications. Banks change section sizes most years, so check your test series is on the latest pattern before Levels 3 and 4.</p>
</section>

<section class="page">
  <div class="sec-head"><p class="eyebrow">How a day runs</p><h2>Three kinds of day</h2><p class="lede">Built for about 9 study hours. Every day in the timetable is one of these. Mains mocks sit in the 9 to 12 slot because that is when most real exam shifts run.</p></div>
  <div class="routines">
    <div class="routine"><h3>Prelims mock day</h3><ol>
      <li><span>06:30–07:00</span>Warm-up: 15 simplification Qs + 1 puzzle</li>
      <li><span>07:00–08:00</span>Full mock, sectional timers on, phone in another room</li>
      <li><span>08:20–10:20</span>Analysis: re-solve every wrong and skipped Q without a timer, log each one</li>
      <li><span>10:30–12:30</span>Drill the weakest topic from today's analysis</li>
      <li><span>14:00–15:00</span>Current affairs + banking awareness</li>
      <li><span>15:00–17:30</span>Second mock or sectionals for the day, then analysis</li>
      <li><span>20:30–21:00</span>Error log revision + 20 new words</li></ol></div>
    <div class="routine"><h3>Mains mock day</h3><ol>
      <li><span>06:30–07:30</span>Light revision only, nothing new</li>
      <li><span>09:00–12:00</span>Full mains mock (+30 min descriptive on PO days)</li>
      <li><span>12:00–13:00</span>Lunch away from screens</li>
      <li><span>13:00–16:00</span>Section-by-section analysis. Missed GA facts go in the GA notebook</li>
      <li><span>16:30–18:00</span>Two sectionals on the weakest mains section</li>
      <li><span>20:00–21:00</span>Current affairs + error log</li></ol></div>
    <div class="routine"><h3>Build or repair day</h3><ol>
      <li><span>07:00–09:00</span>Concept learning for the topics listed</li>
      <li><span>09:15–12:30</span>Sectionals at real timers, analysed after each one</li>
      <li><span>14:00–16:00</span>Re-solve the week's error log</li>
      <li><span>16:00–17:00</span>Current affairs + static GK</li>
      <li><span>17:30–19:00</span>Topic drill or descriptive writing</li>
      <li><span>20:30–21:00</span>Plan tomorrow from the error log</li></ol></div>
  </div>
  <div class="rules">
    <div><h3>Analysis rules</h3><ul>
      <li>Analysis takes at least as long as the mock: 1 hr mock, 2 hr analysis; 3 hr mains, 3 hr analysis.</li>
      <li>If prelims accuracy is below 85%, attempt fewer questions next mock, not more. Each wrong answer costs 0.25 marks.</li>
      <li>Track per mock: score, attempts, accuracy %, minutes per section, and percentile if your series shows one.</li></ul></div>
    <div><h3>If you only have 4 hours a day</h3><ul>
      <li>Do only the first mock listed each day and its analysis. Skip the second mock and the drills.</li>
      <li>Never skip a mains mock or a level's review day.</li>
      <li>Move current affairs to your commute: 30 minutes of a daily quiz or capsule.</li>
      <li>Use one test series per level so difficulty stays comparable.</li></ul></div>
  </div>
</section>

${levelSection([0, 1], "Start + SBI Clerk Prelims").replace('class="eyebrow"> · 22 – 29 Nov', 'class="eyebrow">Start + Level 1 · 22 – 29 Nov')}
${levelSection([2])}
${levelSection([3])}
${levelSection([4])}
${levelSection([5])}
${levelSection([6])}

<section class="tracker">
  <div class="sec-head"><p class="eyebrow">Score tracker</p><h2>All ${n} full mocks</h2><p class="lede">Copy each score here the same day. Accuracy = correct ÷ attempted. In the last column, write the one thing you will do differently next mock.</p></div>
  <table class="grid"><thead><tr><th>#</th><th>Date</th><th>Mock</th><th>Score</th><th>Attempts</th><th>Accuracy</th><th style="width:52mm">One fix for next time</th></tr></thead><tbody>${trackerRows}</tbody></table>
</section>

<section class="finale">
  <div class="sec-head"><p class="eyebrow">The count</p><h2>Mocks per level</h2></div>
  <table class="grid count"><thead><tr><th>Level</th><th>Dates</th><th class="r">Days</th><th class="r">Prelims</th><th class="r">Mains</th><th class="r">RBI papers</th><th class="r">Total</th></tr></thead><tbody>
  ${countRows.map((r) => `<tr><td>${esc(r.name)}</td><td>${esc(r.dates)}</td><td class="r">${r.days}</td><td class="r">${r.p}</td><td class="r">${r.m}</td><td class="r">${r.r}</td><td class="r">${r.p + r.m + r.r}</td></tr>`).join("")}
  <tr class="total"><td>Total</td><td>22 Nov – 31 Dec</td><td class="r">${tot.days}</td><td class="r">${tot.p}</td><td class="r">${tot.m}</td><td class="r">${tot.r}</td><td class="r">${tot.p + tot.m + tot.r}</td></tr></tbody></table>
  <figure class="quote big" style="--c:#80600f"><blockquote>Forty days ago you took a mock cold. On 31 December you take it as a different candidate.</blockquote></figure>
  <div class="reflect">
    <p class="eyebrow">On 31 December, answer these</p>
    <div><p>Mock 1 score: ______ / 100 &nbsp;&nbsp; Hero mock score: ______ / 100. What changed most?</p><div class="lines"><i></i></div></div>
    <div><p>Which level felt hardest, and which one should January 2027 start from?</p><div class="lines"><i></i></div></div>
    <div><p>Which error tag (A, B, C or D) showed up most, and what will I do about it?</p><div class="lines"><i></i></div></div>
  </div>
</section>
</body></html>`;

(async () => {
  const outHtml = path.join(__dirname, "print.html");
  const outPdf = path.join(__dirname, "Zero-to-Hero-Mock-Plan.pdf");
  fs.writeFileSync(outHtml, html);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto("file://" + outHtml, { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({
    path: outPdf, format: "A4", printBackground: true, preferCSSPageSize: true,
    displayHeaderFooter: true, headerTemplate: "<span></span>",
    footerTemplate: '<div style="width:100%;font-family:Inter,Arial,sans-serif;font-size:7.5pt;color:#6b7785;padding:0 15mm;display:flex;justify-content:space-between"><span>Zero to Hero Mock Plan · 22 Nov – 31 Dec 2026</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>'
  });
  await browser.close();
  console.log("Wrote", outPdf);
})();
