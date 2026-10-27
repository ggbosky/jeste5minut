// Vygeneruje OG obrázek (1200×630) a ikony z HTML šablon.
// Použití: npm run og   (potřebuje Playwright: npm i -D playwright && npx playwright install chromium)
import { createRequire } from 'node:module';
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const root = fileURLToPath(new URL('..', import.meta.url));
const font = (p) => `data:font/woff2;base64,${readFileSync(require.resolve(p)).toString('base64')}`;

const css = `
@font-face{font-family:AD;font-weight:100 900;font-stretch:62% 125%;src:url(${font('@fontsource-variable/archivo/files/archivo-latin-wdth-normal.woff2')})}
@font-face{font-family:AD;font-weight:100 900;font-stretch:62% 125%;src:url(${font('@fontsource-variable/archivo/files/archivo-latin-ext-wdth-normal.woff2')});unicode-range:U+0100-02BA}
@font-face{font-family:JB;font-weight:500;src:url(${font('@fontsource/jetbrains-mono/files/jetbrains-mono-latin-500-normal.woff2')})}
@font-face{font-family:JB;font-weight:500;src:url(${font('@fontsource/jetbrains-mono/files/jetbrains-mono-latin-ext-500-normal.woff2')});unicode-range:U+0100-02BA}
*{margin:0;box-sizing:border-box}
body{width:1200px;height:630px;background:#FAF7F0;color:#14213D;font-family:AD;overflow:hidden;position:relative}
.c{color:#FF5A36}
`;

const og = `<!doctype html><html><head><meta charset="utf-8"><style>${css}
.wrap{position:absolute;left:72px;top:64px;width:760px}
.kicker{font-family:JB;font-size:20px;letter-spacing:.1em;text-transform:uppercase;opacity:.7}
s{position:relative;text-decoration:none}s:after{content:'';position:absolute;left:-3px;right:-3px;top:52%;height:3px;background:#FF5A36}
h1{font-weight:800;font-stretch:72%;font-size:190px;line-height:.88;margin-top:30px}
h2{font-weight:800;font-stretch:72%;font-size:92px;line-height:.92;margin-top:14px}
.phone{position:absolute;right:80px;top:56px;width:270px;height:560px;border-radius:44px;background:#0c1426;padding:9px;box-shadow:0 30px 60px -20px rgba(20,33,61,.5)}
.screen{height:100%;border-radius:36px;background:radial-gradient(120% 60% at 50% 0%,#24335a 0%,transparent 70%),radial-gradient(90% 50% at 80% 100%,rgba(255,90,54,.25) 0%,transparent 70%),#14213D;color:#FAF7F0;display:flex;flex-direction:column;align-items:center;padding:56px 16px 18px;font-family:Arial,sans-serif}
.date{font-size:16px;opacity:.85}
.time{font-family:AD;font-weight:600;font-stretch:88%;font-size:84px;line-height:1}
.alarm{margin-top:auto;width:100%;background:rgba(250,247,240,.1);border-radius:22px;padding:14px}
.label{font-weight:700;font-size:15px}
.btn{margin-top:12px;background:#FF5A36;color:#14213D;border-radius:99px;text-align:center;font-weight:700;font-size:18px;padding:16px 0}
</style></head><body>
<div class="wrap">
<div class="kicker">E-book pro studenty, co začnou <s>zítra</s> teď</div>
<h1>Ještě <span class="c">5</span> minut.</h1>
<h2>A pak už fakt začneš.</h2>
</div>
<div class="phone"><div class="screen"><div class="date">úterý 14. ledna</div><div class="time">23:55</div>
<div class="alarm"><div class="label">Zkouška z makra · 8:00</div><div class="btn">Odložit (5 min)</div></div></div></div>
</body></html>`;

const icon = (size) => `<!doctype html><html><head><meta charset="utf-8"><style>${css}
body{width:${size}px;height:${size}px;background:#14213D;display:grid;place-items:center}
span{font-weight:800;font-stretch:72%;font-size:${size * 0.82}px;line-height:1;color:#FF5A36;transform:translateY(3%)}
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
