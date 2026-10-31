// Sestaví Shopify téma (shopify/theme) a zabalí ho do ZIPu pro nahrání do Shopify.
// Použití: npm run theme  → dist-shopify/jeste5minut-theme.zip
//
// 1) výchozí obsah hlavní stránky (templates/index.json) a lišty se vygeneruje z src/content/cs.ts
// 2) CSS: Tailwind (třídy z .liquid souborů) + tokeny ze src/styles/global.css + shopify/extra.css
// 3) video, poster, OG obrázek a ikony se zkopírují z public/
import { execSync } from 'node:child_process';
import { copyFileSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { cs } from '../src/content/cs.ts';
import { pricing } from '../site.config.ts';
import { nbsp } from '../src/lib/rich.ts';

const root = new URL('..', import.meta.url).pathname;
const theme = `${root}shopify/theme`;
const json = (file, data) => writeFileSync(`${theme}/${file}`, JSON.stringify(data, null, 2) + '\n');

// mini-syntaxe (**tučně**, [odkaz](url)) → HTML, které Shopify povolí v inline_richtext
const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const inline = (s) =>
  nbsp(esc(s))
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\[(.+?)\]\(([^)\s]+)\)/g, '<a href="$2">$1</a>');
const text = (s) => nbsp(s.replace(/\*\*(.+?)\*\*/g, '$1'));

// ---------- 1) obsah ----------
const blocks = (items, make) => {
  const out = {};
  items.forEach((item, i) => (out[`b${i + 1}`] = make(item, i)));
  return { blocks: out, block_order: Object.keys(out) };
};

const { hero, learn, contents, pricing: price, faq, nav } = cs;
const discount = pricing.basic.launch ? Math.round((1 - pricing.basic.launch / pricing.basic.regular) * 100) : 0;
const czk = (n) => `${n} Kč`;

json('templates/index.json', {
  sections: {
    hero: {
      type: 'j5-hero',
      settings: {
        lead: hero.lead,
        excuses: hero.excuses.map(text).join(', '),
        now: hero.now,
        subtitle: inline(hero.subtitle),
        video_label: hero.videoLabel,
        price: czk(pricing.basic.launch ?? pricing.basic.regular),
        compare_price: pricing.basic.launch ? czk(pricing.basic.regular) : '',
        discount,
        discount_label: hero.discountLabel,
        button_label: hero.buy,
        button_anchor: '#cena',
        note: hero.ctaNote,
        guarantee: hero.trust[0] ?? '',
      },
      ...blocks(hero.points, (p) => ({ type: 'point', settings: { text: inline(p) } })),
    },
    learn: {
      type: 'j5-learn',
      settings: { title: inline(learn.title), intro: inline(learn.intro), before_label: learn.beforeLabel },
      ...blocks(learn.items, (it) => ({ type: 'change', settings: { after: inline(it.after), before: text(it.before) } })),
    },
    contents: {
      type: 'j5-contents',
      settings: { title: inline(contents.title), intro: inline(contents.intro), anchor: 'obsah' },
      ...blocks(contents.chapters, (ch) => ({ type: 'chapter', settings: { title: text(ch.title), text: inline(ch.text) } })),
    },
    pricing: {
      type: 'j5-pricing',
      settings: { title: inline(price.title), regular_label: price.regularLabel, anchor: 'cena' },
      ...blocks(['basic', 'bundle'], (key) => ({
        type: 'product',
        settings: {
          title: price.plans[key].name,
          features: price.plans[key].features.map(text).join('\n'),
          button_label: price.plans[key].cta,
          featured: key === 'bundle',
          label: price.popular,
        },
      })),
    },
    faq: {
      type: 'j5-faq',
      settings: { title: inline(faq.title), anchor: 'faq' },
      ...blocks(faq.items, (it) => ({ type: 'question', settings: { question: text(it.q), answer: `<p>${inline(it.a)}</p>` } })),
    },
  },
  order: ['hero', 'learn', 'contents', 'pricing', 'faq'],
});

json('sections/header-group.json', {
  type: 'header',
  name: 'Lišta nahoře',
  sections: {
    header: {
      type: 'header',
      settings: { cta_label: nav.cta, cta_anchor: '#cena' },
      ...blocks(nav.links, (l) => ({ type: 'link', settings: { label: l.label, anchor: l.href } })),
    },
  },
  order: ['header'],
});

// ---------- 2) assets ----------
const copy = (from, to = from.split('/').pop()) => copyFileSync(`${root}public/${from}`, `${theme}/assets/${to}`);
['video/hero.webm', 'video/hero.mp4', 'video/hero-poster.webp', 'og.png', 'favicon.svg', 'apple-touch-icon.png'].forEach((f) => copy(f));

// ---------- 3) CSS ----------
const global = readFileSync(`${root}src/styles/global.css`, 'utf8')
  .replace("@import 'tailwindcss';", '')
  // tokeny potřebují i styly sekcí ({% stylesheet %}), které Tailwind nevidí
  .replace('@theme {', '@theme static {');
const input = `${root}shopify/.tailwind-input.css`;
writeFileSync(
  input,
  `@import 'tailwindcss' source(none);\n@source './theme';\n${global}\n${readFileSync(`${root}shopify/extra.css`, 'utf8')}`,
);
execSync(`npx @tailwindcss/cli -i ${input} -o ${theme}/assets/theme.css --minify`, { stdio: 'inherit', cwd: root });
rmSync(input);

// ---------- 4) ZIP ----------
const out = `${root}dist-shopify`;
mkdirSync(out, { recursive: true });
rmSync(`${out}/jeste5minut-theme.zip`, { force: true });
execSync(`zip -qr ${out}/jeste5minut-theme.zip layout config locales sections snippets templates assets`, { cwd: theme });
console.log(`hotovo → dist-shopify/jeste5minut-theme.zip`);
