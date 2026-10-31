# Ještě 5 minut – web

One-page obchod pro e-book „Ještě 5 minut“. Astro (statický web) + Tailwind CSS 4, vanilla JS bez knihoven (animace nadpisu, najíždění sekcí, formulář). Systémové písmo, žádné fonty ke stažení.

## Spuštění

Potřebuješ Node.js **22.22+** (`.nvmrc`).

```bash
npm install
npm run dev       # vývoj → http://localhost:4321
npm run build     # produkční build do dist/
npm run preview   # náhled produkčního buildu
npm run check     # kontrola typů (třeba po úpravě textů)
```

## Kde co změnit

| Co | Kde |
| --- | --- |
| **Všechny texty** (nadpisy, FAQ…) | `src/content/cs.ts` |
| **Ceny** (Kč, €, launch cena) | `site.config.ts` → `pricing` |
| **Odkazy na checkout** (např. Shopify `/cart/VARIANT_ID:1`) | `site.config.ts` → `pricing.basic.checkoutUrl`, `pricing.bundle.checkoutUrl` |
| **E-mailový formulář** (endpoint, formát, názvy polí) | `site.config.ts` → `email` |
| **Analytika** (Plausible / vypnuto) | `site.config.ts` → `analytics` |
| **Adresa Shopify obchodu** (patička odkazuje na jeho zásady) | `site.config.ts` → `shop.url` |
| Doména (canonical, sitemap, OG) | `site.config.ts` → `site.url` a `public/robots.txt` |
| Barvy, písmo | `src/styles/global.css` → `@theme` |

V textech funguje mini-syntaxe: `**tučně**`, `[odkaz](/url)`. Jednopísmenné předložky se automaticky nezlomí na konec řádku.

Když skončí launch cena, nastav `pricing.basic.launch = null` – zmizí přeškrtnutá cena i štítek a všude se ukáže běžná cena.

### Placeholdery, které musíš vyplnit před spuštěním

- `{{CHECKOUT_URL_BASIC}}`, `{{CHECKOUT_URL_BUNDLE}}` – odkazy do pokladny (Shopify: `https://obchod.cz/cart/VARIANT_ID:1`)
- `{{EMAIL_ENDPOINT}}` – viz níže
- `{{SHOPIFY_URL}}` – adresa Shopify obchodu (odkazy na obchodní podmínky, ochranu údajů, vrácení peněz a kontakt)
- Záruka „14 dní na vrácení peněz“ (`hero.trust`) – ověř, že odpovídá tvým zásadám vrácení peněz v Shopify

Hodnoty můžeš místo úpravy souboru nastavit i jako proměnné prostředí na hostingu (viz `.env.example`): `PUBLIC_CHECKOUT_URL_BASIC`, `PUBLIC_CHECKOUT_URL_BUNDLE`, `PUBLIC_EMAIL_ENDPOINT`, `PUBLIC_SHOP_URL`.

## E-mailový formulář (SOS karta)

> Sekce se SOS kartou je zatím **vypnutá**. Zapneš ji v `src/pages/index.astro` přidáním `<LeadSection />` (komponenta i formulář jsou připravené).

Veškeré odesílání je v jedné funkci: `src/lib/subscribe.ts`. Posílá `POST` na `email.endpoint` s poli `email`, `name` (nepovinné), `gdpr_consent` a `source` (`sos-karta`). Názvy polí změníš v `site.config.ts → email.fields`, formát (JSON / form-urlencoded) v `email.format`.

**Nikdy nedávej do konfigurace API klíč** – kód běží v prohlížeči. Možnosti:

- **MailerLite / Ecomail embedded formulář**: vezmi z jejich formuláře `action` URL, nastav `format: 'form'` a názvy polí podle jejich formuláře.
- **Vlastní serverless funkce** (Netlify Functions / Vercel): funkce přijme JSON a s API klíčem v proměnné prostředí zavolá API Ecomailu / MailerLite.

Dokud endpoint není nastavený, formulář ve `npm run dev` jen předstírá úspěch (vypíše data do konzole), v produkci ukáže chybu.

## Analytika

Plausible (bez cookies, takže web nepotřebuje cookie lištu). Nastavení: `site.config.ts → analytics`, `provider: null` analytiku vypne. Vlastní události (klik na checkout) posílá `track()` v `src/lib/analytics.ts`. Právní stránky a kontaktní údaje web nemá – patička odkazuje na zásady napsané v Shopify.

## Shopify téma (Liquid)

Stejný web jako Shopify téma je ve složce `shopify/theme`. ZIP pro nahrání sestavíš:

```bash
npm run theme   # → dist-shopify/jeste5minut-theme.zip
```

Nahrání: Shopify admin → **Online Store → Themes → Add theme → Upload zip file** → u nového tématu **Customize**.

- **Produkty** – sekce „Cena / produkty“: v každém bloku vyber produkt, napiš body (jeden na řádek) a text tlačítka. Cena a přeškrtnutá cena se berou z produktu (Price / Compare-at price). Tlačítko přidá produkt do košíku a pošle zákazníka rovnou do pokladny. Blok bez vybraného produktu se na webu neukáže.
- **Cena v heru** – v sekci „Hero s videem“ vyber produkt, jinak se použije text z nastavení.
- **Video** – v heru můžeš nahrát vlastní, jinak se použije `assets/hero.mp4` z tématu.
- **Patička** – odkazy na zásady se berou automaticky z **Nastavení → Zásady** (obchodní podmínky, ochrana údajů, vrácení peněz, kontaktní údaje…).
- **Texty** – všechno jde upravit v editoru tématu. Výchozí obsah se při `npm run theme` generuje z `src/content/cs.ts` (`templates/index.json`, `sections/header-group.json`), CSS z Tailwindu a `src/styles/global.css` (+ `shopify/extra.css`).

## Logo

Logo projektu je v `public/logo.svg` (oranžová „5“ jako ciferník, #FB6720 + ručičky #4D4D4D). Na webu ho vykresluje `src/components/Logo.astro`, favicon je `public/favicon.svg`. Oranžová webu (`--color-coral` v `src/styles/global.css`) odpovídá barvě loga.

## Deploy

**Vercel**: [vercel.com/new](https://vercel.com/new) → Import Git Repository → `ggbosky/jeste5minut` → framework „Astro“ se pozná sám → Deploy. (Build `npm run build`, výstup `dist`.) Každý další push do produkční větve se nasadí automaticky.
**Netlify**: Add new site → Import from Git → build `npm run build`, publish directory `dist`.

U obou nastav Node 22 (respektují `.nvmrc`) a případně proměnné prostředí výše. Cache hlavičky pro `/_astro/*` jsou v `vercel.json` a `public/_headers`.

## Video v hero

Video v pozadí je v `public/video/` (`hero.webm`, `hero.mp4` a první snímek `hero-poster.webp`). Hraje bez zvuku ve smyčce. Kdo má v zařízení vypnuté animace, uvidí jen první snímek. Výměna videa (potřebuješ ffmpeg):

```bash
ffmpeg -i nove.mp4 -an -vf "scale=1280:-2" -c:v libx264 -crf 27 -preset slow -movflags +faststart public/video/hero.mp4
ffmpeg -i nove.mp4 -an -vf "scale=1280:-2" -c:v libvpx-vp9 -b:v 0 -crf 40 public/video/hero.webm
ffmpeg -ss 0.2 -i nove.mp4 -frames:v 1 -vf "scale=1280:-2" -quality 70 public/video/hero-poster.webp
```

## OG obrázek a ikony

`public/og.png` (1200×630), favicony a ikony do manifestu jsou už vygenerované. Po změně názvu nebo hlavního claimu je přegeneruješ:

```bash
npm i -D playwright && npx playwright install chromium
npm run og
```

Šablona je přímo v `scripts/og.mjs`. Screenshoty webu ve 375 / 768 / 1440 px udělá `npm run shots` (při běžícím `npm run preview`).

## Náhled jako jeden soubor

`npm run preview:artifact` vytvoří `dist-preview/artifact.html` – celý web v jednom HTML (fonty i skripty vložené). Hodí se pro sdílení náhledu tam, kde nejde nahrát celá složka. Odkazy na právní stránky v něm nevedou nikam, na skutečný hosting nasazuj normální `npm run build`.

## Slovenská verze (později)

1. Zkopíruj `src/content/cs.ts` → `src/content/sk.ts`, přejmenuj export na `sk` a přelož texty (TypeScript ohlídá, že nic nechybí – typ `SiteContent`).
2. Přidej `sk` do `locales` v `src/content/index.ts`.
3. Vytvoř stránky `src/pages/sk/…`, které volají `getContent('sk')` (komponenty teď berou `getContent()` bez parametru – stačí jim locale předat jako prop).

## Struktura

```
site.config.ts         ceny, checkout, e-mail, analytika, adresa Shopify
src/content/           texty (cs.ts) + typ pro jazykové verze
src/components/        jedna sekce = jeden soubor
src/layouts/           Base (SEO, schema.org)
src/lib/               subscribe, analytics, rich (mini-syntaxe), format
src/pages/             index, 404
shopify/theme/         Shopify téma (Liquid) – npm run theme
scripts/shopify-theme.mjs  sestavení a ZIP tématu
scripts/               generátor OG obrázku, screenshoty
docs/DESIGN.md         historie designových rozhodnutí
```

## Výkon a přístupnost

Lighthouse (lokálně, produkční build): mobil **100 / 100 / 100 / 100**, desktop **100 / 100 / 100 / 100** (výkon / přístupnost / best practices / SEO). Písmo je systémové (SF na Applu, Segoe UI na Windows, Roboto na Androidu), takže se nestahují žádné fonty. CSS je inline, sekce pod ohybem mají `content-visibility: auto`. Všechny animace respektují `prefers-reduced-motion` (zobrazí se rovnou finální stav) a bez JS je veškerý obsah vidět; formulář i FAQ jdou ovládat klávesnicí.
