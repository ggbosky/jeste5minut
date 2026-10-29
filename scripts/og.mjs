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

// logo projektu (public/logo.svg) vložené jako data URI
const logo = `data:image/svg+xml;base64,${readFileSync(`${root}public/logo.svg`).toString('base64')}`;

const og = `<!doctype html><html><head><meta charset="utf-8"><style>${css}
.wrap{position:absolute;left:96px;top:0;bottom:0;width:640px;display:flex;flex-direction:column;justify-content:center}
h1{font-size:112px;font-weight:800;letter-spacing:-.04em;line-height:.95}
h1 span{color:#FB6720}
h2{font-size:42px;font-weight:600;letter-spacing:-.02em;margin-top:26px}
p{font-size:26px;color:#5b6478;margin-top:22px}
.mark{position:absolute;right:110px;top:50%;height:440px;transform:translateY(-50%)}
</style></head><body>
<div class="wrap"><h1>Začnu<br><span>teď.</span></h1><h2>Přestaň se učit noc před zkouškou.</h2><p>Ještě 5 minut · e-book pro vysokoškoláky</p></div>
<img class="mark" src="${logo}" alt="">
</body></html>`;

const icon = (size) => `<!doctype html><html><head><meta charset="utf-8"><style>${css}
body{width:${size}px;height:${size}px;background:#fff;display:grid;place-items:center}
img{height:${Math.round(size * 0.74)}px}
</style></head><body><img src="${logo}" alt=""></body></html>`;

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
