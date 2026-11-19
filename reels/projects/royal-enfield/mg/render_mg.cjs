// Renders the motion-graphics layer (mg/index.html) to transparent PNG frames.
//   node render_mg.js                 -> mg/frames/00000.png ... (all frames, 3 parallel pages)
//   node render_mg.js --times 1,2.5   -> mg/preview/<t>.png overlay stills only
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const dir = __dirname;
const args = process.argv.slice(2);
const ti = args.indexOf('--times');
const times = ti >= 0 ? args[ti + 1].split(',').map(Number) : null;
const WORKERS = 3;

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => console.error('[page error]', e.message));
  await page.goto('file://' + path.join(dir, 'index.html'));
  await page.evaluate(() => window.MG_READY);
  return page;
}

(async () => {
  const browser = await chromium.launch({ args: ['--force-color-profile=srgb', '--disable-lcd-text'] });
  if (times) {
    const out = path.join(dir, 'preview');
    fs.mkdirSync(out, { recursive: true });
    const page = await openPage(browser);
    for (const t of times) {
      await page.evaluate(([t, f]) => MG.render(t, f), [t, Math.round(t * 30)]);
      await page.screenshot({ path: path.join(out, `${t.toFixed(2)}.png`), omitBackground: true });
    }
    await browser.close();
    return;
  }
  const out = path.join(dir, 'frames');
  fs.mkdirSync(out, { recursive: true });
  const probe = await openPage(browser);
  const dur = await probe.evaluate(() => MG.duration);
  await probe.close();
  const total = Math.round(55.8 * 30); // base reel is 55.8 s = 1674 frames
  console.log('frames', total, 'mg duration', dur.toFixed(3));
  let next = 0, done = 0;
  const t0 = Date.now();
  await Promise.all([...Array(WORKERS)].map(async () => {
    const page = await openPage(browser);
    while (next < total) {
      const f = next++;
      await page.evaluate(([t, f]) => MG.render(t, f), [f / 30, f]);
      await page.screenshot({ path: path.join(out, String(f).padStart(5, '0') + '.png'), omitBackground: true });
      if (++done % 100 === 0) console.log(done, 'frames', ((Date.now() - t0) / 1000).toFixed(0) + 's');
    }
  }));
  await browser.close();
  console.log('done', total);
})();
