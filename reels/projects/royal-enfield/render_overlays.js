// Renders transparent 1080x1920 PNG overlays (captions, title, logo, follow banner).
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const dir = __dirname;
const data = JSON.parse(fs.readFileSync(path.join(dir, 'captions.json'), 'utf8'));
const out = path.join(dir, 'ov');
fs.mkdirSync(out, { recursive: true });

const css = `
  html,body{margin:0;width:1080px;height:1920px;background:transparent;overflow:hidden}
  body{font-family:'Inter';font-weight:800;color:#fff}
  .t{position:absolute;left:70px;right:70px;text-align:center;letter-spacing:-0.5px;
     -webkit-text-stroke:7px #111;paint-order:stroke fill;
     text-shadow:0 5px 0 #111,0 8px 18px rgba(0,0,0,.45)}
  .cap{top:1340px;left:110px;right:110px;font-size:44px;line-height:1.2}
  .title{top:700px;font-size:70px;line-height:1.1;font-weight:900}
  .title y{font-size:104px}
  y{color:#FFD21F} r{color:#FF3B30}
  .logo{position:absolute;left:858px;top:1700px;width:76px;height:76px;border-radius:50%;
        background:#E0262F;display:flex;align-items:center;justify-content:center;
        font:900 38px Inter;color:#fff;box-shadow:0 3px 8px rgba(0,0,0,.35)}
  .disc{position:absolute;left:80px;right:80px;top:1520px;text-align:center;font:700 24px Inter;
        color:#fff;opacity:.9;text-shadow:0 2px 4px rgba(0,0,0,.8)}
  .banner{position:absolute;left:190px;width:700px;top:880px;padding:34px 20px;text-align:center;
          background:#F4E9D2;border-radius:14px;box-shadow:0 10px 30px rgba(0,0,0,.35);
          border:4px solid #d9c7a2;color:#2a2a2a;font:800 54px Inter}
  .banner small{display:block;font:600 30px Inter;margin-top:6px;color:#555}
`;

async function shot(page, html, file) {
  await page.setContent(`<html><head><style>${css}</style></head><body>${html}</body></html>`);
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(out, file), omitBackground: true });
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  for (let i = 0; i < data.clips.length; i++) {
    const n = String(i + 1).padStart(2, '0');
    await shot(page, `<div class="t cap">${data.clips[i]}</div>`, `cap${n}.png`);
  }
  await shot(page, `<div class="t title">${data.title}</div>`, 'title.png');
  await shot(page, `<div class="logo">M</div>`, 'logo.png');
  await shot(page, `<div class="disc">${data.disclaimer}</div>`, 'disc.png');
  await shot(page, `<div class="banner">Follow ${data.handle}<small>for more business stories</small></div>`, 'banner.png');
  await browser.close();
  console.log('overlays done');
})();
