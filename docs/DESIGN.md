# Ještě 5 minut – design direction

## Moodboard ve slovech

- **Budík na displeji telefonu ve 23:55** – obří tlačítko „Odložit“, systémová typografie, ale přefouknutá do plakátu.
- **Gumroad / neo-brutalismus** – 3px černé linky, tvrdé offsetové stíny bez blur, ploché barevné bloky, tlačítka, která se fyzicky „zmáčknou“.
- **Švýcarský typografický plakát** – nadpisy jako hlavní vizuál (Space Grotesk 700, až ~9rem), těsný tracking, zarovnání doleva, asymetrie.
- **Studentský sešit** – zvýrazňovač přes klíčová slova, přeškrtnuté „~~zítra~~ teď“, papírová textura (grain).
- **Stopky / časovač** – Space Mono čísla, tikající dělítka sekcí, odpočet 5:00 jako motiv napříč stránkou.
- Barvy: 90 % ink (#14213D) + paper (#FAF7F0). Coral (#FF5A36) jen pro akci (CTA, snooze), mint pro „hotovo“, marker žlutá pro zvýraznění.

## 3 varianty hera

1. **„Budík“ (vybráno)** – vlevo plakátový nadpis „Ještě 5 minut. A pak už fakt začneš.“, vpravo (na mobilu pod CTA) obří karta budíku: čas 23:55, štítek „Zkouška z makra · 8:00“, gigantické tlačítko „Odložit (5 min)“. Klik → tlačítko uhne, čas se posune o 5 minut, text „Fakt? Zase?“ → „Ok, tak začneme.“ → scroll na nabídku. Screenshotovatelný moment + jasné CTA v prvních 3 sekundách.
2. **„Notifikace“** – hero jako lock screen plný notifikací (TikTok, IG, „Bakalářka.docx – naposledy upraveno před 183 dny“), které jdou swipnout; pod nimi nadpis. Vtipné, ale víc šumu a horší čitelnost CTA na mobilu.
3. **„Odpočet“** – full-bleed obří odpočet 05:00 přes celou obrazovku, nadpis uvnitř číslic. Silný plakát, ale bez interakce „odložit“, která je jádrem konceptu.

Vybrána varianta 1: nejsilněji nese koncept snooze, hlavní CTA je vidět bez scrollu a interakce je sdílitelná.

## Struktura souborů

```
site.config.ts              ← ceny, checkout URL, e-mail endpoint, analytika, sociální sítě
src/content/
  types.ts                  ← typ SiteContent (kontrakt pro cs.ts i budoucí sk.ts)
  cs.ts                     ← VŠECHNY texty webu
  index.ts                  ← getContent(locale)
src/lib/
  subscribe.ts              ← jediná funkce pro odeslání e-mailu (Ecomail / MailerLite / vlastní endpoint)
  analytics.ts              ← načtení Plausible / GA4 až po souhlasu
  format.ts                 ← formátování cen
src/components/             ← jedna sekce = jeden soubor (Hero, Quiz, Pricing, …)
src/layouts/                ← Base (SEO, fonty, schema.org), Legal (právní stránky)
src/pages/                  ← index + obchodní podmínky, GDPR, reklamační řád, 404
src/styles/global.css       ← Tailwind theme (barvy, fonty), grain, stíny, animace
scripts/og.mjs              ← vygeneruje public/og.png (1200×630) z HTML šablony
scripts/screenshots.mjs     ← screenshoty 375 / 768 / 1440 pro kontrolu
```

## Self-review (0–10)

| Kritérium | Skóre | Poznámka |
| --- | --- | --- |
| Typografie | 9 | Plakátové nadpisy Space Grotesk až 9rem, ciferník „5“ v Space Mono, Inter pro text, `text-wrap: balance/pretty`, nezlomitelné předložky. |
| Kompozice | 8.5 | Asymetrické gridy, nic není „všechno na střed“. Hero: obří nadpis vlevo + budík, který leze do nadpisu. Opraveno: ceník se zarovnal do mřížky, tablet layouty kroků, ceníku a patičky. |
| Pohyb | 8 | Snooze interakce (uhnutí, přetočení času, vibrace), stagger reveal, zvýrazňovač, škrtání, marquee, magnetická CTA, 3D kniha za kurzorem. Hero animace jen v CSS (neblokuje LCP). |
| Barvy | 9 | ~90 % ink + paper, coral jen na akci, mint = hotovo, marker = zvýraznění. Žádný coral text na světlém pozadí; kontrast AA všude (Lighthouse a11y 100). |
| Detaily | 9 | Grain, tvrdé stíny, tlačítka se „zmáčknou“, stupnice stopek mezi sekcemi, ručně psaná poznámka u budíku, rotující pečeť záruky, ukázka SOS karty. |
| Mobile UX | 9 | Mobile-first, CTA v navigaci i v heru nad ohybem, spodní lišta s časovačem a CTA, velká tap-targets, žádný horizontální scroll. |
| Jasnost konverze | 9 | Cena a CTA vidět do 3 s (nav + hero), druhé CTA na lead magnet, ceník se dvěma jasnými volbami a doporučenou variantou. |
| Čeština | 8.5 | Tykání, krátké věty, vtip bez kázání. Doporučuji ještě rychlou kontrolu rodilým copywriterem (hlavně kvíz a FAQ). |

Vědomé odchylky od zadání: místo Motion One / GSAP jsou animace v CSS + pár řádků vanilla JS (celkem ~8 kB JS) – stejný efekt, lepší Lighthouse. Astro je připnuté na 7.4.1 (7.4.2 už vyžaduje Node 22.23+).

## Revize 2 – méně „kreslené“, méně AI

Zpětná vazba: moc cartoon, divný font, čtverec budíku, celé to působí moc „AI“.

- **Typografie:** Space Grotesk / Inter / Space Mono → **Archivo** (úzký řez 800 na plakátové nadpisy, normální šířka na text) + JetBrains Mono na drobné popisky. Jedna rodina = klidnější a ucelenější.
- **Budík:** kreslená karta se žlutým stínem → realistický zamčený displej telefonu (23:55, notifikace od mamky, ze studijního systému a „čas u obrazovky“, budík s tlačítkem Odložit). Telefon při odložení zabzučí.
- **Pryč:** tvrdé posunuté stíny, 3px rámečky, natočené karty a štítky, ručně psaná poznámka, kreslené ikonky kvízu, tečky u nadpisů, rotující pečeť, grain.
- **Nově:** tenké linky, jemné stíny jen tam, kde jde o fyzický předmět (telefon, kniha, SOS karta), ploché bloky, rovný zvýrazňovač.

## Revize 3 – zjednodušení

- Budík bez makety telefonu: plochý panel s velkým časem 23:55 a tlačítkem Odložit.
- Odstraněno: pás s citáty, kvíz, malé popisky nad nadpisy, dělítka se stupnicí, platební poznámka pod ceníkem, obří odpočet v závěrečné sekci.
- Kapitoly číslované („Kapitola 1 · 5 min čtení“) místo časových značek, které působily jako audiokniha.
- Zvýrazňovač na tmavém pozadí nahrazen oranžovou barvou textu; menu má jen tenké podtržení.

## Revize 4 – čistý obchod

Zpětná vazba: texty, fonty a množství prvků pořád působí jako AI. Zvolený směr: „čistý obchod“ (jako produktová stránka Applu).

- Systémové písmo, bílé pozadí, tmavý text, oranžová jen na tlačítka.
- Sekce: hero s obálkou a cenou → Co se naučíš → Obsah → Cena → SOS karta zdarma → Časté otázky → patička.
- Texty přepsané věcně, bez vtipných nadpisů a slovních hříček.
- Odstraněno: budík, odpočet, sekce „Nejsi líný“, Jak to funguje, ukázkové recenze, samostatná záruka (je v FAQ), závěrečná výzva, ukázka SOS karty, pole „jméno“ ve formuláři.

## Revize 5 – animace a hook

Zpětná vazba: čistý obchod je lepší, ale chybí animace, silný hook a lepší hero.

- **Hero:** obří nadpis „Začnu zítra. / v pondělí. / po obědě. / večer.“ – každá výmluva se přeškrtne a nakonec zůstane oranžové „teď.“ Obálka e-booku se při scrollu narovná a přiblíží, čísla 70 a 8 se napočítají.
- **Scroll příběh** (tmavá připnutá obrazovka): při scrollu běží hodiny 20:00 → 23:55 a mění se věty typického večera před zkouškou, končí oranžovým „Ještě 5 minut.“
- **Statement:** věta, která se při scrollu rozsvěcí slovo po slově.
- Sekce najíždějí postupně (stagger). Bez JS nebo s `prefers-reduced-motion` se vše zobrazí staticky ve finálním stavu.

## Revize 6 – nic nestojí

- Scroll příběh už se nepřipíná: časy a věty se scrollují normálně s celou stránkou a každý řádek najede, až na něj dojedeš.
- Odstraněna obálka e-booku (fakta jsou jeden řádek pod cenou) a odstavec, který se rozsvěcel slovo po slově.

## Revize 7 – hero, které prodává

- Rozložení: text vlevo, vpravo ukázka dvou stránek e-booku (kapitola „Pravidlo pěti minut“ s úkolem na 5 minut + obsah). Stránky při načtení přiletí, na desktopu se při scrollu posouvají různou rychlostí.
- Pod animovaným nadpisem konkrétní slib („Přestaň se učit noc před zkouškou.“), tři přínosy, CTA s cenou v tlačítku, druhé tlačítko na SOS kartu a řádek důvěry (běžná cena, PDF hned, 14 dní na vrácení peněz).
- Logo: ciferník s vyznačeným výsekem 5 minut + název.
- CTA: „Začnu teď“ (navazuje na nadpis), „Chci e-book“, „Chci e-book i bonusy“, „Pošlete mi SOS kartu“.
- Lišta cookies se ukáže až po prvním scrollu a je kompaktní, aby nezakrývala hlavní tlačítko.

## Revize 8 – video v hero, lepší CTA

- Hero má v pozadí video ve smyčce (diář a lísteček „Done!“) s tmavým překryvem. Ukázka stránek e-booku odstraněna.
- Hlavní CTA: „Začnu teď“ + „PDF ti přijde do minuty“ + cena v tmavé pilulce + šipka; jemný lesk každých pár sekund, oranžová záře. Vedle „Nejdřív zkusit zdarma“ (malý krok, SOS karta). Pod nimi sleva −33 % proti běžné ceně, záruka 14 dní (štít) a „jednorázově, žádné předplatné“.
- Sekce s časy večera odstraněna.
- „Co se naučíš“ → „Co se změní“: karty před → po, bolest se při najetí oranžově přeškrtne, pod ní výsledek.
- Ceník: tlačítka s cenou a šipkou, u balíčku „Nejčastější volba“.

## Revize 9 – logo projektu

- Dodané logo (oranžová „5“ jako ciferník s ručičkami) v menu, patičce, faviconu, ikonách a OG obrázku. Po najetí myší se ručičky protočí.
- Oranžová webu sjednocena s logem: #FB6720.
