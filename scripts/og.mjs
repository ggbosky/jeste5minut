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
@font-face{font-family:SG;font-weight:700;src:url(${font('@fontsource/space-grotesk/files/space-grotesk-latin-700-normal.woff2')})}
@font-face{font-family:SG;font-weight:700;src:url(${font('@fontsource/space-grotesk/files/space-grotesk-latin-ext-700-normal.woff2')});unicode-range:U+0100-02BA}
@font-face{font-family:SM;font-weight:400;src:url(${font('@fontsource/space-mono/files/space-mono-latin-400-normal.woff2')})}
@font-face{font-family:SM;font-weight:400;src:url(${font('@fontsource/space-mono/files/space-mono-latin-ext-400-normal.woff2')});unicode-range:U+0100-02BA}
*{margin:0;box-sizing:border-box}
body{width:1200px;height:630px;background:#FAF7F0;color:#14213D;font-family:SG;overflow:hidden;position:relative}
.five{display:inline-grid;place-items:center;padding:0 .08em;font-family:SM;font-weight:700;background:#FF5A36;border:6px solid #14213D;border-radius:.14em;box-shadow:.06em .06em 0 #14213D;transform:rotate(-4deg);line-height:.95}
`;

const og = `<!doctype html><html><head><meta charset="utf-8"><style>${css}
.wrap{position:absolute;inset:0;padding:64px 72px;display:flex;flex-direction:column}
.kicker{font-family:SM;font-size:24px;letter-spacing:.08em;text-transform:uppercase;display:flex;gap:14px;align-items:center}
.kicker:before{content:'';width:18px;height:18px;border-radius:99px;background:#FF5A36;box-shadow:0 0 0 3px #14213D}
h1{font-size:168px;line-height:.9;letter-spacing:-.045em;margin-top:34px}
h2{font-size:74px;line-height:1;letter-spacing:-.035em;margin-top:18px}
s{position:relative;text-decoration:none}s:after{content:'';position:absolute;left:-4px;right:-4px;top:52%;height:5px;background:#FF5A36;transform:rotate(-4deg)}
.alarm{position:absolute;right:64px;bottom:60px;width:330px;background:#14213D;color:#FAF7F0;border:5px solid #14213D;border-radius:36px;padding:26px 28px;box-shadow:14px 14px 0 #FFD23F,14px 14px 0 5px #14213D;transform:rotate(3deg)}
.time{font-size:104px;letter-spacing:-.05em;text-align:center;line-height:1}
.btn{margin-top:18px;background:#FF5A36;color:#14213D;border:4px solid #FAF7F0;border-radius:99px;text-align:center;font-size:32px;padding:18px 0;box-shadow:6px 6px 0 #FAF7F0}
.ticks{position:absolute;left:72px;right:72px;bottom:0;height:26px;background:repeating-linear-gradient(90deg,#14213D 0 3px,transparent 3px 16px) bottom/100% 12px no-repeat,repeating-linear-gradient(90deg,#14213D 0 4px,transparent 4px 80px) bottom/100% 26px no-repeat}
</style></head><body><div class="wrap">
<div class="kicker">E-book pro studenty · začni <s>zítra</s> teď</div>
<h1>Ještě <span class="five">5</span> minut.</h1>
<h2>A pak už fakt začneš.</h2>
</div>
<div class="alarm"><div class="time">23:55</div><div class="btn">Odložit (5 min)</div></div>
<div class="ticks"></div>
</body></html>`;

const icon = (size) => `<!doctype html><html><head><meta charset="utf-8"><style>${css}
body{width:${size}px;height:${size}px;background:#FF5A36;display:grid;place-items:center}
span{font-family:SM;font-weight:700;font-size:${size * 0.78}px;line-height:1;color:#14213D;transform:translateY(-2%)}
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
