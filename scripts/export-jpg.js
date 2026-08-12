// 将 9 页卡片导出为高质量 JPG（用于自媒体发布）
const { chromium } = require('playwright');

const NAMES = [
  '01-封面', '02-五步概览', '03-引物设计', '04-载体线性化', '05-重组连接',
  '06-转化', '07-筛选测序', '08-避坑指南', '09-快速排查', '10-封底',
];

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 800 } });
  await page.goto('file:///F:/WorkBuddy/2026-08-10-11-02-28/plasmid-card/index.html');
  await page.waitForTimeout(500);

  const n = await page.locator('.card').count();
  console.log('cards:', n);
  for (let i = 0; i < n; i++) {
    const el = page.locator('.card').nth(i);
    const name = NAMES[i] || `card-${i + 1}`;
    const path = `F:/WorkBuddy/2026-08-10-11-02-28/plasmid-card/${name}.jpg`;
    await el.screenshot({ path, type: 'jpeg', quality: 95 });
    console.log('saved:', name + '.jpg');
  }
  await browser.close();
})();
