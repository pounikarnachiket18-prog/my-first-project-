// Renders mg.html frame by frame and writes PNG frames (with alpha) to stdout, or to a folder for previews.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const dir = __dirname;
const tl = JSON.parse(fs.readFileSync(path.join(dir, 'timeline2.json')));
const bt = JSON.parse(fs.readFileSync(path.join(dir, 'beats.json')));
const s = tl.starts;
const data = {
  ...tl, ...bt,
  caps: [
    "Ek zamaane mein iske rider <y>aise</y> hote the 🎩",
    "<y>1970:</y> England mein production <r>band</r> 💔",
    "…par <y>India</y> mein ye kahani <y>zinda</y> rahi 🇮🇳",
    "Har gali, har mohalla… <y>dug-dug-dug</y> 🏍️",
    "Bullet sirf bike nahi… ek <y>rutba</y> thi 😎",
    "<y>1950s:</y> England se <y>ship</y> pe India aayi 🚢",
    "<y>Indian Army</y> ka order… Madras mein <y>Enfield India</y> bani",
    "Phir aayi <r>halki, zyada mileage</r> wali bikes…",
    "Showroom <r>khaali</r>… company <r>ghaate</r> mein 📉",
    "<y>Eicher</y> ne company sambhali… bike ko <y>theek</y> kiya 🔧",
    "Naye boss <y>Siddhartha Lal</y>: focus <y>sirf Bullet</y> pe ✂️",
    "Bike <y>nayi</y> bani… <y>Ladakh trips</y> ne sapna bana diya 🏔️",
    "Aaj <y>12 lakh+</y> bikes… <y>80+ desh</y> 🌍",
    "Aapki <y>dream</y> Royal Enfield kaunsi hai? <y>Comment karo</y> ↓"
  ],
  tags: [[1, "📍 England · 1950s"], [2, "📍 England · 1970"], [3, "📍 India"], [6, "⏪ Flashback · 1950s"], [7, "📍 Madras · 1955"],
         [8, "📍 India · 1980s–90s"], [9, "📉 1990s"], [10, "🔧 1994 · Eicher"], [11, "✂️ 2000s"], [12, "🏔️ Ladakh"], [13, "🌍 FY26"]],
  health: [[0, .6], [s[2], .05], [s[3], .55], [s[4], .7], [s[5], .75], [s[6], .5], [s[7], .65], [s[8], .35], [s[9], .08], [bt.kick + 0.3, .5], [s[11], .65], [s[12], .85], [s[13], 1], [s[14], .95]],
  years: [[0, 1950], [s[2], 1970], [s[3], 1975], [s[4], 1980], [s[5], 1985], [s[6], 1952], [s[7], 1955], [s[8], 1988], [s[9], 1993], [s[10], 1994], [s[11], 2000], [s[12], 2015], [s[13], 2026]],
};
(async () => {
  const args = process.argv.slice(2);
  const prevDir = args[0] === '--preview' ? args[1] : null;
  const times = prevDir ? args.slice(2).map(Number) : null;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.join(dir, 'mg.html'));
  const logo = 'data:image/png;base64,' + fs.readFileSync(path.join(dir, 'logo_m.png')).toString('base64');
  await page.evaluate(async ([d, logo]) => {
    await document.fonts.ready; const im = new Image(); im.src = logo; await im.decode(); d.logo = im; window.setData(d);
  }, [data, logo]);
  const el = await page.$('canvas');
  if (prevDir) {
    fs.mkdirSync(prevDir, { recursive: true });
    for (const t of times) { await page.evaluate(t => window.render(t), t); await el.screenshot({ path: path.join(prevDir, `mg_${t.toFixed(2)}.png`), omitBackground: true }); }
  } else {
    const n = Math.round(tl.dur * 30);
    for (let f = 0; f < n; f++) {
      await page.evaluate(t => window.render(t), f / 30);
      const buf = await el.screenshot({ omitBackground: true, type: 'png' });
      if (!process.stdout.write(buf)) await new Promise(r => process.stdout.once('drain', r));
      if (f % 150 === 0) process.stderr.write(`frame ${f}/${n}\n`);
    }
  }
  await browser.close();
})();
