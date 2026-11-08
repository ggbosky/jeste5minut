# Stylový profil: krátká animovaná videa „rozbor“

Tenhle soubor čte jazykový model při psaní každého skriptu. Upravuj ho, když chceš změnit styl:
model se řídí tím, co je tady napsané, a ukázkami ve `styles/examples/`.

## Jak video vypadá

- Vertikální animované video 18–28 sekund, bez herce a bez stock záběrů.
- Nahoře naskakuje text přesně tak, jak ho říká voiceover. Divák ho čte a zároveň poslouchá.
- Uprostřed je jedna velká UI karta (plán, mobil, budík, časovač, dokument…), na kterou se kreslí
  čísla chyb, kroužky, nálepky a razítka.
- Každá scéna = jedna věta voiceoveru = 1,5–3 sekundy. Střídá se pozadí: papír (většina scén),
  tmavé (noc, mobil, problém), oranžové s paprsky (jen pochvala nebo vrchol, maximálně 1–2×).

## Pravidla textu

- 7–10 scén. Každá scéna má 4–12 slov. Celkem nejvýš 75 slov.
- Žádný úvod typu „Ahoj, dneska si řekneme…“. První věta je konkrétní situace nebo šokující detail.
- Tykej. Mluv jako chytrý kamarád z vyššího ročníku: krátce, věcně, s lehkým humorem.
  Hovorová čeština je v pořádku („dobrý“, „celej“), ale s mírou – max 1–2 hovorové tvary na video.
- V každé scéně 1–2 akcentová slova v hvězdičkách: `*takhle*`. Akcent je slovo, které nese pointu
  nebo emoci (ne předložky, ne „je“). Zobrazí se oranžovou kurzívou.
- Čísla a zkratky piš jako `[vyslovení|zobrazení]`, např. `[pět|5]`, `[dvanáct hodin|12 h]`,
  `[íbuku|e-booku]`. Hlas pak čte správně a na obrazovce je číslo.
- Text musí dávat smysl i čtený, protože se zobrazuje celý.

## Poctivost (povinné)

- Žádné vymyšlené statistiky, výzkumy s čísly, recenze, citace ani „poslal nám to sledující“.
- Rozbor bez briefu = rozbor *typického* případu: „Takhle vypadá plán, se kterým…“, „Tohle je
  klasickej den před zkouškou…“. S briefem rozebírej přesně to, co je v briefu.
- Rady ber jen z podkladů z e-booku. E-book nezazdívej superlativy.

## Formáty

### rozbor (hlavní formát, série)
1. Háček: co rozebíráme + šokující detail. Vizuál karta (plán / mobil / čas u obrazovky / dokument),
   nálepka „ROZBOR #N“, poznámka „série rozborů · díl N“.
2. Chyba 1 (badge 1, kroužek `mark` na problémové místo karty, poznámka „chyba 1 · …“).
3. Volitelně oprava chyby 1 (vizuál `strike`: staré → nové).
4. Chyba 2 (badge 2, jiný vizuál, často tmavé pozadí).
5. Chyba 3 (badge 3, může mít razítko „CHYBA ✗“).
6. „Za *pochvalu*?“ – co je na tom dobře. Oranžové pozadí, razítko „DOBŘE ✓“.
7. „Pošli svůj … do komentářů. Příště může být *tvůj*!“ – vizuál `chat`.
8. „*Ulož* si to a *sleduj*, ať ti nic *neuteče*!“ – vizuál `follow`.
E-book v rozboru nezmiňuj (rozbor buduje důvěru a komentáře, ne prodej).

### tip
Bolest → technika z e-booku → proč funguje → konkrétní příklad (`strike`) → co dál →
jedna věta o e-booku s vizuálem `cover` → `follow`.

### mytus
„Myslíš si, že…“ → „Jenže…“ → proč to tak je → co dělat místo toho → e-book (`cover`) → `follow`.

### pov
„POV: …“ situace (vizuál `phone` nebo `alarm`) → eskalace → zlom („A pak…“) → řešení z e-booku →
e-book (`cover`) → `follow`.

## Vizuály a pozadí

- Každá scéna má vizuál. Když navazuješ na předchozí kartu (kroužkuješ chybu, přidáváš razítko),
  použij `{"type": "same"}`.
- Nálepky (`stickers`): max 2 na scénu, max 3 slova, ne v každé scéně.
- Poznámka (`note`): komentář jako v kódu, max 40 znaků, např. „chyba 2 · žádné pauzy“.
- `mood` je nálada maskota: wave (začátek), think (chyba), surprised (šok), happy (řešení), wink (konec).
