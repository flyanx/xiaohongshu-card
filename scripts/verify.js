// 6 页卡片截图 + 溢出/图加载验证
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 800 } });
  await page.goto('file:///F:/WorkBuddy/2026-08-10-11-02-28/plasmid-card/index.html');
  await page.waitForTimeout(500);

  const n = await page.locator('.card').count();
  let allOk = true;
  for (let i = 0; i < n; i++) {
    const el = page.locator('.card').nth(i);
    const info = await el.evaluate(el => {
      const er = el.getBoundingClientRect();
      const boxH = el.clientHeight;
      let deepest = 0;
      el.querySelectorAll('.flowbar,.c-h1,.c-block,.step-block,.fig,.fig-cap,.c-tags,.cover-blocks,.cover-main,.cover-foot').forEach(c => {
        const b = c.getBoundingClientRect().bottom - er.top;
        if (b > deepest) deepest = b;
      });
      const imgs = [...el.querySelectorAll('img')].map(im => im.complete && im.naturalWidth > 0);
      return { deepest: Math.round(deepest), fill: Math.round(deepest / boxH * 100), imgOk: imgs.every(x => x) };
    });
    const ok = info.fill >= 80 && info.fill <= 100 && info.imgOk;
    if (!ok) allOk = false;
    console.log(`card-${i + 1}.png 填充=${info.fill}% ${ok ? '✅' : '❌'}`);
    await el.screenshot({ path: `F:/WorkBuddy/2026-08-10-11-02-28/plasmid-card/card-${i + 1}.png` });
  }
  await browser.close();
  process.exit(allOk ? 0 : 2);
})();
