const { chromium } = require('playwright'); const fs = require('fs'), path = require('path'); const dir = __dirname;
const tl = JSON.parse(fs.readFileSync(path.join(dir, 'timeline.json'))), ev = JSON.parse(fs.readFileSync(path.join(dir, 'events.json')));
const S = tl.S, B = tl.beats;
const data = { ...tl, events: ev,
  tags: [['train', '📍 Mumbai Local'], ['teacher', '📍 Classroom'], ['hero', '🎬 Bollywood'], ['stadium', '📍 Stadium'], ['umpire', '🏏 Live Match'], ['lab', '🔬 Myth vs Science'],
         ['ac', '🧠 Theory #1'], ['copy', '🧠 Why it spreads'], ['office', '💼 Office meeting'], ['dinner', '🍛 Family dinner'], ['night', '🌙 1:00 AM'],
         ['mummy', '🌙 2:00 AM'], ['zoom', '💻 Online meeting'], ['dog', '🌳 Park'], ['pass', '🏙️ Poora shehar']],
  infected: [[B.yawn1, 2], [B.dadi + .3, 9], [S.train + .5, 47], [B.teacher_yawn, 83], [B.hero_yawn + .3, 91], [S.stadium + .6, 50091], [B.umpire_yawn, 50094],
             [S.lab + .2, 50095], [B.burst, 50096], [S.dinner + .5, 50100], [B.night_yawn, 50101], [B.mummy_yawn + .4, 50104], [S.zoom + .9, 50116],
             [B.dog_yawn, 50119], [B.impact, 50120], [B.couple_yawn, 50122], [B.split + .2, 1000000]],
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
