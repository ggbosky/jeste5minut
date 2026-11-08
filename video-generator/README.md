# Ještě 5 minut – generátor videí

Lokální aplikace v Pythonu, která z obsahu e-booku **„Ještě 5 minut“** automaticky vyrobí krátká vertikální videa (1080×1920, 15–45 s) pro TikTok, Instagram Reels a YouTube Shorts.

**Bez placených API.** Skripty, hlas, časování titulků i střih běží na tvém počítači na open-source nástrojích. Jediná síťová služba je volitelná: Pexels (stock videa zdarma, potřebuje bezplatný klíč).

```
skript (JSON) ──► hlas (XTTS-v2 / Piper) ──► časy slov (Whisper / odhad)
      ──► jump cuty z B-rollu po 2–4 s (ffmpeg) ──► kinetické titulky (PIL + moviepy)
      ──► mix hlasu, swooshů a hudby na −14 LUFS ──► output/<id>.mp4 + popisek
```

---

## 1. Instalace

Potřebuješ **Python 3.10–3.13** (doporučeno 3.11 nebo 3.12) a **ffmpeg**.

```bash
# ffmpeg
sudo apt install ffmpeg          # Ubuntu / Debian
brew install ffmpeg              # macOS
winget install Gyan.FFmpeg       # Windows
```

```bash
cd video-generator
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

**Plná instalace** (XTTS-v2 + Piper + Whisper, ~3 GB s PyTorch):

```bash
pip install -r requirements.txt
```

Máš NVIDIA kartu? Nainstaluj nejdřív PyTorch s CUDA podle [pytorch.org](https://pytorch.org/get-started/locally/) a teprve pak `requirements.txt`. XTTS na GPU je zhruba 10× rychlejší než na CPU.

**Lehká instalace** (jen Piper, bez PyTorch – funguje i na slabém notebooku):

```bash
pip install -r requirements-lite.txt
```

Kontrola a stažení českého hlasu Piper (~60 MB):

```bash
python main.py setup
```

---

## 2. Rychlý start

```bash
python main.py scripts --chapter 2 --format pov --count 3     # 3 skripty ke kapitole 2
python main.py list                                           # přehled skriptů
python main.py show scripts/k02-pov-xxxxxx.json               # přečti si skript
python main.py render scripts/k02-pov-xxxxxx.json --tts piper # vyrenderuj video
```

Hotové video najdeš v `output/k02-pov-xxxxxx.mp4` a vedle něj `.txt` s popiskem a hashtagy.

Rychlý náhled střihu bez čekání na hlas (ticho místo řeči, 540×960):

```bash
python main.py render scripts/k02-pov-xxxxxx.json --tts dummy --draft
```

Všechno najednou:

```bash
python main.py scripts --count 2            # 8 kapitol × 5 formátů × 2 = 80 skriptů
python main.py batch --limit 10             # vyrenderuje prvních 10, které ještě nemají video
```

---

## 3. Struktura projektu

```
video-generator/
├── main.py                 CLI (setup, scripts, list, show, voice, render, batch, broll)
├── requirements.txt        plná instalace (torch, transformers, coqui-tts, moviepy, …)
├── requirements-lite.txt   bez PyTorch (jen Piper)
├── config.example.toml     zkopíruj jako config.toml a uprav
├── j5m/
│   ├── content.py          obsah e-booku: 8 kapitol, bolesti, řešení, úkoly, CTA
│   ├── scripter.py         skládá skripty (šablony nebo lokální LLM přes Ollamu)
│   ├── markup.py           mini-syntaxe *klíčové slovo* a [vyslovení|zobrazení]
│   ├── tts.py              lokální hlas: XTTS-v2, Piper, dummy
│   ├── align.py            časování slov (faster-whisper nebo odhad podle slabik)
│   ├── broll.py            vlastní záběry, Pexels, grafické karty, obálka e-booku
│   ├── captions.py         kinetická typografie (PIL)
│   ├── audio_mix.py        swooshe, hudba s duckingem, loudness −14 LUFS
│   └── render.py           celý pipeline
├── scripts/                vygenerované skripty (JSON) – 40 ukázkových je v repu
├── audio/
│   ├── voices/             TVOJE nahrávky hlasu pro klonování (XTTS)
│   ├── music/              volitelná hudba na pozadí
│   └── <id>/               vygenerované audio každého videa (věty, voice.wav, mix.wav)
├── video/
│   ├── library/<tag>/      TVOJE vlastní B-roll záběry
│   ├── cache/              stažené klipy z Pexels, grafické karty
│   └── work/<id>/          mezisoubory renderu (po dokončení se mažou)
├── output/                 hotová videa + popisky
├── assets/                 písmo Inter (OFL), obálka e-booku
└── models/                 stažené modely (Piper, Whisper)
```

---

## 4. Obsahový modul (Scripter)

`j5m/content.py` obsahuje rozebraný e-book: ke každé z 8 kapitol (Proč odkládáme, Pravidlo pěti minut, Mobil, Zkouškové, Bakalářská práce, Perfekcionismus, Když to nevyjde, Tvůj plán) háčky, scénky, vysvětlení, řešení, úkol na 5 minut a pointy. Texty jsou psané pro mluvené slovo, tykají, používají hovorovou češtinu („dobrý“, „jinej“, „tejden“) a Scripter do nich náhodně vkládá vsuvky („Hele,“ „Upřímně,“ „Víš co?“).

### Formáty

| Formát | Stavba |
| --- | --- |
| `pov` | „POV: …“ → scénka → proč to tak je → řešení → pointa → CTA |
| `myth` | „Myslíš si, že… Nejsi.“ → vysvětlení → řešení → CTA |
| `mistake` | „Největší chyba?…“ → proč → co místo toho → CTA |
| `list` | „3 věci…“ → tři body → CTA |
| `challenge` | „Dej mi 5 minut.“ → úkol z kapitoly krok po kroku → CTA |

```bash
python main.py scripts --chapter 1,4 --format list,challenge --count 2 --length short
```

`--length`: `short` (15–25 s), `medium` (24–35 s, výchozí), `long` (33–45 s). Délka se odhaduje podle počtu slabik.

### Mini-syntaxe ve skriptech

Skripty jsou obyčejné JSON soubory – klidně je ručně uprav nebo napiš vlastní.

```json
{ "text": "Dej mi [pět|5] minut. To je *celý trik*.", "broll": ["timer", "desk"] }
```

- `*celý trik*` – klíčová slova: v titulcích větší a v oranžové barvě značky.
- `[pět|5]` – hlas řekne „pět“, titulek ukáže „5“. Hodí se pro čísla a zkratky (`[íbuku|e-booku]`, `[v devět|v 9:00]`).
- `broll` – tagy záběrů pod větou (seznam v `content.py → BROLL_TAGS`).

### Volitelně: lokální LLM přes Ollamu

Pokud máš [Ollamu](https://ollama.com) (open-source, běží lokálně), Scripter může nechat skripty psát model nad podklady z kapitoly:

```bash
ollama pull llama3.1:8b
python main.py scripts --engine ollama --chapter 3 --count 5
```

Výstup se validuje (tagy, struktura); když model selže, použije se šablona. Prompt modelu zakazuje vymyšlené statistiky a falešné recenze. Vždy si skript přečti (`python main.py show …`), než ho pustíš ven.

---

## 5. Hlas – lokální TTS bez API

| Backend | Kvalita češtiny | Rychlost | Licence | Kdy použít |
| --- | --- | --- | --- | --- |
| `xtts` – Coqui XTTS-v2 | nejlepší, klonuje hlas | GPU rychlé, CPU ~1–3× reálný čas | **jen nekomerční** (CPML) | testy, nekomerční obsah |
| `piper` – cs_CZ-jirka-medium | dobrá, trochu „čtená“ | velmi rychlé i na CPU | MIT (hlas: dataset CC0) | komerční videa, slabší PC |
| `dummy` | ticho | okamžité | – | ladění střihu |

**Proč ne Kokoro-82M:** Kokoro češtinu nepodporuje (umí angličtinu, španělštinu, francouzštinu, hindštinu, italštinu, japonštinu, portugalštinu a čínštinu). Česky by četl s nesrozumitelnou výslovností, proto tu není.

### Jak se audio generuje

1. Každá věta (beat) skriptu se namluví zvlášť. Výsledek se uloží jako `audio/<id>/beatNN-<hash>.wav`. Změníš jednu větu, přegeneruje se jen ta.
2. Ořízne se ticho na začátku a konci každé věty.
3. Věty se poskládají s krátkými pauzami (`tts.gap`, delší po háčku a pointě) do `voice.wav` (48 kHz). Do `timings.json` se zapíše přesný začátek a konec každé věty.
4. Čísla a zkratky se čtou podle `[vyslovení|zobrazení]`, takže TTS nikdy nečte „5“ ani „e-book“ po svém.

### XTTS-v2 s vlastním hlasem (doporučeno)

1. Nahraj 10–30 s svého hlasu do `audio/voices/` (návod je v `audio/voices/README.md`). Formát nevadí, převede se sám.
2. Přečti si licenci modelu a pokud souhlasíš, potvrď ji proměnnou prostředí:
   ```bash
   export COQUI_TOS_AGREED=1
   ```
3. Spusť render:
   ```bash
   python main.py render scripts/k01-pov-xxxxxx.json --tts xtts
   ```
   Poprvé se stáhne model (~1,8 GB) do `~/.local/share/tts/`. Pak už všechno běží offline.

Ladění v `config.toml → [tts.xtts]`: `speed` (1.0–1.15 je pro sociální sítě ideál), `temperature` (0.6–0.8). Bez vlastní nahrávky se použije vestavěný hlas, který ale česky zní s cizím přízvukem.

### ⚠️ Licence hlasu – čti před prvním komerčním videem

- **XTTS-v2** je pod [Coqui Public Model License](https://coqui.ai/cpml.txt), která povoluje **jen nekomerční použití**. Videa, která prodávají e-book, jsou komerční. Firma Coqui skončila, takže komerční licenci si už koupit nejde. Pro reklamní videa proto používej **Piper** (`--tts piper` nebo `backend = "piper"` v `config.toml`), nebo věty namluv sám/sama (viz bod 9).
- **Piper cs_CZ-jirka-medium**: repozitář hlasů je pod MIT, dataset hlasu CC0. Hlas je doladěný z anglického modelu „lessac“. Pokud to s komercí myslíš vážně, projdi si `MODEL_CARD` u obou modelů.
- **Klonování hlasu:** klonuj jen svůj hlas, nebo hlas člověka, který ti k tomu dal výslovný souhlas.

### Označení AI obsahu

Syntetický hlas, který zní jako skutečný člověk, je realistický AI obsah. **TikTok vyžaduje, aby byl takový obsah označený** (přepínač „Obsah vytvořený AI“ při nahrávání). YouTube a Instagram mají podobná pravidla pro realistický syntetický obsah. Zapni štítek a ušetříš si stažení videa nebo omezení dosahu. Připomínka je i v `.txt` souboru u každého videa.

---

## 6. Střih a vizuál („Real Cut“)

### Jump cuty každé 2–4 s

`plan_cuts` rozseká časovou osu na střihy dlouhé `min_cut`–`max_cut` sekund. Střih padne přednostně na hranici věty, jinak těsně před slovo. Každý druhý střih je přiblížený (`punch_in` = 1.14×). V asi třetině případů pokračuje stejný záběr, jen s jiným přiblížením, což je typický „jump cut“ z CapCutu.

Každý střih zpracuje ffmpeg:
- ořez na 9:16 a jemný „handheld“ pohyb (`shake_px`), aby záběr nevypadal staticky,
- barevný grade (`warm` / `neutral` / `cold`),
- filmové zrno (`grain`) a vinětace – stock videa tak působí míň „sterilně“,
- statické obrázky (karty, obálka) dostanou pomalý zoom.

Při závěrečné výzvě (CTA) se ukáže nakloněná obálka e-booku (`assets/cover.png`) s oranžovým štítkem „Odkaz na e-book je v biu“.

### Odkud se berou záběry (B-roll)

Pro každý střih se zkouší v tomto pořadí:

1. **`video/library/<tag>/`** – tvoje vlastní záběry. Působí nejvěrohodněji. Stačí 10–20 klipů natočených mobilem (studovna, notebook v noci, ruka píše poznámky, mobil displejem dolů…).
2. **`video/cache/pexels/<tag>/`** – už stažené klipy z Pexels.
3. **Pexels API** – zdarma, ale potřebuje klíč. Zaregistruj se na [pexels.com/api](https://www.pexels.com/api/) a pak:
   ```bash
   export PEXELS_API_KEY=tvuj_klic
   python main.py broll --per-tag 6        # předem stáhne ~6 klipů ke každému tagu
   ```
   Stahují se jen vertikální videa (≥ 1280 px na výšku) a ukládá se autor a odkaz (`credits.json`). [Licence Pexels](https://www.pexels.com/license/) povoluje komerční použití bez nutnosti uvádět autora, nesmíš ale prodávat samotné klipy ani naznačovat, že lidé na záběrech tvůj produkt doporučují.
4. Jakýkoli jiný klip z knihovny.
5. **Grafická karta v barvách značky** (navy + oranžová, obří „5“ / „0X“ / „23:55“). Funguje vždycky, i offline.

Bez Pexels: `--no-pexels`.

### Kinetická typografie

Titulky se kreslí přes PIL snímek po snímku (moviepy `transform`) a vypálí se do videa:

- **`pop`** (výchozí): slova naskakují přesně ve chvíli, kdy zazní, s krátkým „přestřelením“ velikosti (ease-out-back). Klíčová slova jsou o 14 % větší a v oranžové.
- **`highlight`**: celá „stránka“ titulku je vidět a právě vyslovené slovo má oranžový rámeček.
- Na „stránce“ jsou nejvýš 3 slova. Nová stránka začíná u interpunkce, nové věty nebo klíčového slova, takže každé klíčové slovo dostane vlastní „úder“.
- Písmo Inter Black s tmavým obrysem a měkkým stínem, pozice ve 60 % výšky (mimo UI TikToku dole a vpravo).
- V prvních ~3 s je nahoře bílý štítek s nadpisem kapitoly (jako textový štítek v TikToku).

Časy slov počítá **faster-whisper** (lokální Whisper): přepíše audio každé věty, slova namapuje na skript a nesrovnalosti doplní interpolací. Bez Whisperu (`--align estimate`) se slova rozloží podle slabik a interpunkce. Protože známe přesný začátek a konec každé věty, funguje i odhad slušně.

### Zvuk

- Hlas: high-pass, jemná komprese.
- „Swoosh“ na každém střihu, generovaný lokálně ze šumu (`audio.whoosh`).
- Hudba z `audio/music/` (volitelná) se automaticky ztiší, když se mluví (sidechain ducking), a na konci se stáhne.
- Výsledek se normalizuje na **−14 LUFS** (hlasitost, se kterou počítají TikTok, Reels i Shorts).

---

## 7. Jak probíhá finální render

`python main.py render scripts/<id>.json` udělá postupně:

1. **Hlas** → `audio/<id>/voice.wav` + `timings.json` (věty, které už jsou namluvené, se přeskočí).
2. **Časy slov** → `audio/<id>/words.json`.
3. **Plán střihů** → 2–4 s úseky, ke každému tagy záběrů z dané věty.
4. **Střihy** → `video/work/<id>/cutNNN.mp4` (ffmpeg: ořez, punch-in, pohyb, grade, zrno) → spojení do `base.mp4`.
5. **Zvuk** → swooshe (`sfx.wav`) + hlas + hudba → `mix.wav` (−14 LUFS).
6. **Titulky** → moviepy projde `base.mp4` snímek po snímku a PIL do něj vykreslí titulky, štítek s háčkem a CTA (`captioned.mp4`, H.264, CRF 18).
7. **Mux** → video + AAC 192 kb/s, `+faststart` → **`output/<id>.mp4`** a `output/<id>.txt` (popisek, hashtagy, zdroje záběrů).

Mezisoubory ve `video/work/` se po úspěchu smažou (`--keep` je nechá).

Orientační časy pro 30s video na běžném CPU: Piper ~2 s, Whisper ~10 s, střihy ~20 s, titulky a enkódování ~60 s. XTTS na CPU přidá 1–2 minuty, na GPU ~10 s.

---

## 8. Konfigurace

```bash
cp config.example.toml config.toml
```

Uprav jen to, co chceš změnit. Všechny volby s komentáři jsou v `j5m/config.py → DEFAULTS`. Nejčastější:

| Volba | Co dělá |
| --- | --- |
| `tts.backend` | `xtts` / `piper` / `dummy` |
| `captions.style` | `pop` / `highlight` |
| `captions.font` | vlastní písmo (TTF/OTF s češtinou), např. Montserrat ExtraBold |
| `captions.uppercase` | titulky verzálkami |
| `video.min_cut`, `video.max_cut` | délka střihů |
| `video.grade`, `video.grain` | barevnost a zrno |
| `video.cta_visual` | `cover` (obálka) nebo `broll` |
| `audio.music_volume` | hlasitost hudby pod hlasem |

---

## 9. Tipy, aby videa nepůsobila „vyrobeně“

- **Vlastní záběry > stock.** I 15 krátkých klipů z mobilu (tvoje skripta, tvůj stůl, tvoje knihovna) udělá víc než stovka stock videí.
- **Vlastní hlas.** Naklonovaný vlastní hlas, nebo rovnou namluvené `voice.wav`, zní nejlíp. Postup: `python main.py voice …`, nahraď věty ve složce `audio/<id>/` vlastní nahrávkou se stejným názvem a pusť `render`.
- **Háček do 2 sekund.** Nejvíc záleží na první větě. Projdi si skripty přes `show` a slabé háčky přepiš.
- **Žádné vymyšlené recenze, čísla ani „mně to změnilo život“.** Všechno ve skriptech vychází z e-booku a tak to má zůstat.
- **Testuj formáty.** Vyrenderuj všech 5 formátů pro jednu kapitolu, publikuj je a podle dosahu zjisti, co tvému publiku sedí.

---

## 10. Řešení problémů

| Problém | Řešení |
| --- | --- |
| `Chybí ffmpeg` | Nainstaluj ffmpeg (bod 1) a ověř `ffmpeg -version`. |
| XTTS hlásí licenci | Nastav `COQUI_TOS_AGREED=1` (jen pokud s licencí souhlasíš) nebo použij `--tts piper`. |
| XTTS: chyba při načítání nahrávky | `pip install "coqui-tts[codec]"` (torchcodec). Nahrávky se převádějí do `models/xtts_refs/`. |
| XTTS je pomalý | Použij GPU, nebo Piper. Věty se cachují, takže druhý render je rychlý. |
| Titulky jdou mimo řeč | Nainstaluj `faster-whisper` (`--align whisper`); pro přesnější časy nastav `align.whisper_model = "medium"`. |
| Pexels nic nestahuje | Zkontroluj `PEXELS_API_KEY`. Bez klíče se použijí vlastní záběry nebo karty. |
| Chci jiné písmo | Dej TTF/OTF do `assets/fonts/` a nastav `captions.font`. Písmo musí umět českou diakritiku. |
