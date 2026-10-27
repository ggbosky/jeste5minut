// Screenshoty webu ve 3 šířkách. Použití: npm run build && npm run preview  (v jiném okně) → npm run shots
// Volitelně: node scripts/screenshots.mjs http://localhost:4321 [výstupní složka] [selector]
import { createRequire } from 'node:module';
import { mkdirSync } from 'node:fs';

const base = process.argv[2] || 'http://localhost:4321';
const out = process.argv[3] || 'shots';
const only = process.argv[4];
const widths = [375, 768, 1440];
mkdirSync(out, { recursive: true });
// Playwright není v dependencies (velký). Nainstaluj: npm i -D playwright && npx playwright install chromium
const { chromium } = createRequire(import.meta.url)('playwright');

const browser = await chromium.launch();
for (const w of widths) {
  const page = await browser.newPage({ viewport: { width: w, height: w < 800 ? 812 : 900 }, deviceScaleFactor: 1 });
  await page.goto(base, { waitUntil: 'networkidle' });
  // projet stránku, aby se spustily reveal animace
  await page.evaluate(async () => {
    for (let y = 0; y < document.body.scrollHeight; y += 400) {
      window.scrollTo(0, y);
      await new Promise((r) => setTimeout(r, 60));
    }
    window.scrollTo(0, 0);
    document.querySelectorAll('[data-reveal]').forEach((el) => el.classList.add('is-in'));
    // full-page screenshot nescrolluje → vynutit vykreslení sekcí s content-visibility
    const s = document.createElement('style');
    s.textContent = '.cv-host > section { content-visibility: visible !important } #cookie-consent, [data-mini-timer] { display: none !important }';
    document.head.appendChild(s);
  });
  await page.waitForTimeout(1200);
  if (only) {
    await page.locator(only).first().screenshot({ path: `${out}/${w}-${only.replace(/\W/g, '')}.png` });
  } else {
    await page.screenshot({ path: `${out}/${w}-fold.png` });
    await page.screenshot({ path: `${out}/${w}-full.png`, fullPage: true });
  }
  await page.close();
}
await browser.close();
console.log('hotovo →', out);
