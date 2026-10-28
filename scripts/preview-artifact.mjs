// Sestaví jednosouborový náhled webu (pro Claude artifact): PREVIEW=1 build + vložení všech skriptů do HTML.
// Použití: npm run preview:artifact  → dist-preview/artifact.html
import { rolldown } from 'rolldown';
import { readFileSync, writeFileSync, rmSync } from 'node:fs';
import { execSync } from 'node:child_process';

execSync('npx astro build', { stdio: 'inherit', env: { ...process.env, PREVIEW: '1' } });

const dir = 'dist-preview';
let html = readFileSync(`${dir}/index.html`, 'utf8');

// všechny skripty stránky → jeden modul (sdílené moduly jako analytics/timer jen jednou)
const scripts = [...html.matchAll(/<script type="module" src="\/(_astro\/[^"]+)"><\/script>/g)];
const entry = `${dir}/__entry.js`;
writeFileSync(entry, scripts.map(([, src]) => `import './${src}';`).join('\n'));
const bundle = await rolldown({ input: entry });
const { output } = await bundle.generate({ format: 'esm', minify: true });
rmSync(entry);
const code = output[0].code.replace(/<\/script/g, '<\\/script');
for (const [tag] of scripts) html = html.replace(tag, '');
html = html.replace('</body>', () => `<script type="module">${code}</script></body>`);

// odkazy na soubory, které v náhledu nejsou
html = html.replace(/<link rel="(icon|apple-touch-icon|manifest|sitemap)"[^>]*>/g, '');

// video a poster hera vložit přímo (náhled nemůže načítat soubory zvenku)
const mime = { webm: 'video/webm', mp4: 'video/mp4', webp: 'image/webp' };
html = html.replace(/\/video\/[\w-]+\.(webm|mp4|webp)/g, (path, ext) => `data:${mime[ext]};base64,${readFileSync(`${dir}${path}`).toString('base64')}`);

// v galerii artifactů stačí jméno webu
html = html.replace(/<title>[^<]*<\/title>/, '<title>Ještě 5 minut</title>');

// artifact si dokument obalí sám → jen obsah <head> a <body>
const head = html.match(/<head>([\s\S]*)<\/head>/)[1];
const body = html.match(/<body[^>]*>([\s\S]*)<\/body>/)[1];
const page = `${head}\n${body}`;

writeFileSync(`${dir}/artifact.html`, page);
console.log(`hotovo → ${dir}/artifact.html (${Math.round(page.length / 1024)} kB, ${scripts.length} skriptů vloženo)`);
