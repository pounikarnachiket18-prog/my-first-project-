const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.setContent(`<html><body style="margin:0;width:1080px;height:1920px;background:transparent">
  <div style="position:absolute;left:170px;width:745px;top:985px;height:210px;display:flex;flex-direction:column;align-items:center;justify-content:center;transform:rotate(-1.5deg);font-family:Inter;text-align:center">
    <div style="font:900 74px Inter;color:#C62828;letter-spacing:1px;text-shadow:0 2px 0 rgba(90,40,10,.25)">Oh! Wow…</div>
    <div style="font:900 82px Inter;color:#4E2A12;letter-spacing:2px;text-shadow:0 2px 0 rgba(90,40,10,.25)">DREAM BIKE!</div>
  </div></body></html>`);
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: 'ov/bannertext.png', omitBackground: true }); await b.close();
})();
