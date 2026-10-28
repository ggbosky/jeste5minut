// Vygeneruje OG obrázek (1200×630) a ikony z HTML šablon.
// Použití: npm run og   (potřebuje Playwright: npm i -D playwright && npx playwright install chromium)
import { createRequire } from 'node:module';
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const root = fileURLToPath(new URL('..', import.meta.url));
const css = `
*{margin:0;box-sizing:border-box}
body{width:1200px;height:630px;background:#fff;color:#14213D;font-family:-apple-system,'SF Pro Display','Segoe UI',Inter,Roboto,Arial,sans-serif;overflow:hidden;position:relative}
`;

const og = `<!doctype html><html><head><meta charset="utf-8"><style>${css}
.wrap{position:absolute;left:96px;top:0;bottom:0;width:620px;display:flex;flex-direction:column;justify-content:center}
h1{font-size:104px;font-weight:700;letter-spacing:-.035em;line-height:1}
h2{font-size:44px;font-weight:600;letter-spacing:-.02em;margin-top:18px}
p{font-size:28px;color:#5b6478;margin-top:28px}
.book{position:absolute;right:120px;top:95px;width:300px;height:420px;perspective:1600px}
.cover{height:100%;border-radius:5px 12px 12px 5px;background:#14213D;color:#fff;padding:32px;display:flex;flex-direction:column;justify-content:flex-end;transform:rotateY(-14deg) rotateX(4deg);box-shadow:inset 6px 0 0 rgba(255,255,255,.08),inset 9px 0 0 rgba(0,0,0,.25),30px 40px 60px -24px rgba(20,33,61,.45)}
.rule{position:absolute;top:32px;left:32px;width:42px;height:5px;border-radius:3px;background:#FF5A36}
.t{font-size:40px;font-weight:700;letter-spacing:-.03em;line-height:1.02}
.s{font-size:17px;opacity:.75;margin-top:10px}
</style></head><body>
<div class="wrap"><h1>Ještě 5 minut</h1><h2>Jak přestat odkládat učení.</h2><p>E-book pro vysokoškoláky · 70 stran · PDF</p></div>
<div class="book"><div class="cover"><span class="rule"></span><div class="t">Ještě 5 minut</div><div class="s">Jak přestat odkládat učení</div></div></div>
</body></html>`;

const icon = (size) => `<!doctype html><html><head><meta charset="utf-8"><style>${css}
body{width:${size}px;height:${size}px;background:#14213D;display:grid;place-items:center}
span{font-weight:700;font-size:${size * 0.7}px;line-height:1;color:#fff;letter-spacing:-.04em}
</style></head><body><span>5</span></body></html>`;

const browser = await chromium.launch();
async function shot(html, w, h, out) {
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  await page.setContent(html, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: `${root}public/${out}` });
  await page.close();
}
await shot(og, 1200, 630, 'og.png');
await shot(icon(180), 180, 180, 'apple-touch-icon.png');
await shot(icon(192), 192, 192, 'icon-192.png');
await shot(icon(512), 512, 512, 'icon-512.png');
await shot(icon(32), 32, 32, 'favicon-32.png');
await browser.close();

// favicon.ico = PNG zabalené v ICO kontejneru
const png = readFileSync(`${root}public/favicon-32.png`);
const header = Buffer.alloc(22);
header.writeUInt16LE(0, 0);
header.writeUInt16LE(1, 2);
header.writeUInt16LE(1, 4);
header.writeUInt8(32, 6);
header.writeUInt8(32, 7);
header.writeUInt16LE(1, 10);
header.writeUInt16LE(32, 12);
header.writeUInt32LE(png.length, 14);
header.writeUInt32LE(22, 18);
writeFileSync(`${root}public/favicon.ico`, Buffer.concat([header, png]));
console.log('OG obrázek a ikony hotové → public/');
