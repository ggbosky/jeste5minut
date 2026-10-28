# Ještě 5 minut – web

One-page obchod pro e-book „Ještě 5 minut“. Astro (statický web) + Tailwind CSS 4, vanilla JS bez knihoven (animace nadpisu, najíždění sekcí, formulář, lišta cookies). Systémové písmo, žádné fonty ke stažení.

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
| **Všechny texty** (nadpisy, FAQ, recenze, právní stránky…) | `src/content/cs.ts` |
| **Ceny** (Kč, €, launch cena) | `site.config.ts` → `pricing` |
| **Odkazy na checkout** (SimpleShop) | `site.config.ts` → `pricing.basic.checkoutUrl`, `pricing.bundle.checkoutUrl` |
| **E-mailový formulář** (endpoint, formát, názvy polí) | `site.config.ts` → `email` |
| **Analytika** (Plausible / GA4 / vypnuto) | `site.config.ts` → `analytics` |
| **Kontakt, IČO, sociální sítě** | `site.config.ts` → `contact`, `socials` |
| Doména (canonical, sitemap, OG) | `site.config.ts` → `site.url` a `public/robots.txt` |
| Barvy, písmo | `src/styles/global.css` → `@theme` |

V textech funguje mini-syntaxe: `**tučně**`, `[odkaz](/url)`. Jednopísmenné předložky se automaticky nezlomí na konec řádku.

Když skončí launch cena, nastav `pricing.basic.launch = null` – zmizí přeškrtnutá cena i štítek a všude se ukáže běžná cena.

### Placeholdery, které musíš vyplnit před spuštěním

- `{{CHECKOUT_URL_BASIC}}`, `{{CHECKOUT_URL_BUNDLE}}` – URL produktů ze SimpleShopu
- `{{EMAIL_ENDPOINT}}` – viz níže
- `contact` v `site.config.ts` (firma, IČO, adresa)
- Recenze (`testimonials` v `cs.ts`, označené `TODO: real testimonials`) – až budou skutečné, nastav `placeholder: false`
- Záruka (`guarantee`) – ověř, že znění odpovídá tomu, co opravdu nabízíš
- Právní stránky (`legal`) – šablony, nech je zkontrolovat

Hodnoty můžeš místo úpravy souboru nastavit i jako proměnné prostředí na hostingu (viz `.env.example`): `PUBLIC_CHECKOUT_URL_BASIC`, `PUBLIC_CHECKOUT_URL_BUNDLE`, `PUBLIC_EMAIL_ENDPOINT`.

## E-mailový formulář (SOS karta)

Veškeré odesílání je v jedné funkci: `src/lib/subscribe.ts`. Posílá `POST` na `email.endpoint` s poli `email`, `name` (nepovinné), `gdpr_consent` a `source` (`sos-karta`). Názvy polí změníš v `site.config.ts → email.fields`, formát (JSON / form-urlencoded) v `email.format`.

**Nikdy nedávej do konfigurace API klíč** – kód běží v prohlížeči. Možnosti:

- **MailerLite / Ecomail embedded formulář**: vezmi z jejich formuláře `action` URL, nastav `format: 'form'` a názvy polí podle jejich formuláře.
- **Vlastní serverless funkce** (Netlify Functions / Vercel): funkce přijme JSON a s API klíčem v proměnné prostředí zavolá API Ecomailu / MailerLite.

Dokud endpoint není nastavený, formulář ve `npm run dev` jen předstírá úspěch (vypíše data do konzole), v produkci ukáže chybu.

## Analytika a cookies

Ve výchozím stavu se **nic nenačítá**, dokud návštěvník neklikne na „Povolit statistiky“ (lišta se ukáže po 2,5 s, volba se uloží do `localStorage`, změnit jde odkazem v patičce). Nastavení: `site.config.ts → analytics`. `provider: null` vypne analytiku i lištu. Vlastní události (klik na checkout, odeslaný lead) se posílají přes `track()` v `src/lib/analytics.ts`.

## Deploy

**Vercel**: Import repozitáře → framework „Astro“ se pozná sám → Deploy. (Build `npm run build`, výstup `dist`.)
**Netlify**: Add new site → Import from Git → build `npm run build`, publish directory `dist`.

U obou nastav Node 22 (respektují `.nvmrc`) a případně proměnné prostředí výše. Cache hlavičky pro `/_astro/*` jsou v `vercel.json` a `public/_headers`.

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
site.config.ts         ceny, checkout, e-mail, analytika, kontakty
src/content/           texty (cs.ts) + typ pro jazykové verze
src/components/        jedna sekce = jeden soubor
src/layouts/           Base (SEO, schema.org, fonty), Legal
src/lib/               subscribe, analytics, rich (mini-syntaxe), format
src/pages/             index, obchodní podmínky, GDPR, reklamační řád, 404
scripts/               generátor OG obrázku, screenshoty
docs/DESIGN.md         historie designových rozhodnutí
```

## Výkon a přístupnost

Lighthouse (lokálně, produkční build): mobil **100 / 100 / 100 / 100**, desktop **100 / 100 / 100 / 100** (výkon / přístupnost / best practices / SEO). Písmo je systémové (SF na Applu, Segoe UI na Windows, Roboto na Androidu), takže se nestahují žádné fonty. CSS je inline, sekce pod ohybem mají `content-visibility: auto`. Všechny animace respektují `prefers-reduced-motion` (zobrazí se rovnou finální stav) a bez JS je veškerý obsah vidět; formulář i FAQ jdou ovládat klávesnicí.
