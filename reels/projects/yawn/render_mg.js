// Renders mg_yw.html frame by frame; PNG frames to stdout, or preview PNGs with --preview dir t1 t2 ...
const { chromium } = require('playwright'); const fs = require('fs'), path = require('path'); const dir = __dirname;
const tl = JSON.parse(fs.readFileSync(path.join(dir, 'timeline.json'))), ev = JSON.parse(fs.readFileSync(path.join(dir, 'events.json')));
const s = tl.starts;
const data = { ...tl, events: ev,
  tags: [[3, '📍 Mumbai Local'], [4, '📍 Classroom'], [5, '📍 Stadium'], [6, '🔬 Myth vs Science'], [7, '🧠 Theory #1'], [8, '🧠 Why it spreads'],
         [9, '💼 Office meeting'], [10, '🍛 Family dinner'], [11, '🌙 2:00 AM'], [12, '💻 Online meeting']],
  infected: [[tl.yawn1, 2], [s[1] + 2.2, 9], [s[3] + .5, 47], [s[4] + 1.1, 83], [s[5] + .6, 50083], [s[6] + .2, 50084], [ev.burst, 50085], [s[10] + .5, 50089], [s[11] + 1.9, 50090], [s[12] + .9, 50102]],
};
(async () => {
  const a = process.argv.slice(2), prev = a[0] === '--preview' ? a[1] : null;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(dir, 'mg_yw.html'));
  const logo = 'data:image/png;base64,' + fs.readFileSync(path.join(dir, 'logo_m.png')).toString('base64');
  await p.evaluate(async ([d, logo]) => { await document.fonts.ready; const im = new Image(); im.src = logo; await im.decode(); d.logo = im; window.setData(d); }, [data, logo]);
  const el = await p.$('canvas');
  if (prev) { fs.mkdirSync(prev, { recursive: true }); for (const t of a.slice(2).map(Number)) { await p.evaluate(t => window.render(t), t); await el.screenshot({ path: path.join(prev, `mg_${t.toFixed(2)}.png`), omitBackground: true }); } }
  else { const n = Math.round(tl.dur * 30); for (let f = 0; f < n; f++) { await p.evaluate(t => window.render(t), f / 30); const buf = await el.screenshot({ omitBackground: true, type: 'png' }); if (!process.stdout.write(buf)) await new Promise(r => process.stdout.once('drain', r)); } }
  await b.close();
})();
