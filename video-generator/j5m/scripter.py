"""Scripter: skládá krátké skripty (15–45 s) z obsahu e-booku.

Dva režimy:
  template – deterministické skládání z content.py (výchozí, žádný model)
  ollama   – lokální LLM přes Ollamu (http://localhost:11434), výstup se
             validuje a když selže, použije se šablona.

Formáty:
  pov        POV háček → scénka → proč to tak je → řešení → pointa → CTA
  myth       mýtus → vysvětlení → řešení → CTA
  mistake    největší chyba → proč → co místo toho → CTA
  list       „3 věci…“ → tři body → CTA
  challenge  „Dej mi 5 minut“ → úkol z kapitoly krok za krokem → CTA
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from . import content
from .config import PATHS
from .markup import estimate_seconds, strip_markup
from .utils import log, short_hash, warn, write_json

FORMATS = ["pov", "myth", "mistake", "list", "challenge"]

LENGTHS = {
    "short": (15.0, 25.0),
    "medium": (24.0, 35.0),
    "long": (33.0, 45.0),
}


# ---------------------------------------------------------------- pomocné


def _lower_first(text: str) -> str:
    for i, ch in enumerate(text):
        if ch in "*[":
            continue
        if ch.isalpha():
            nxt = text[i + 1] if i + 1 < len(text) else ""
            if nxt.isupper():          # zkratka (POV) – nech být
                return text
            return text[:i] + ch.lower() + text[i + 1:]
        return text
    return text


FILLER_POOLS = {
    "scene": (["Upřímně,", "Hele,"], []),
    "insight": (["Upřímně,"], ["Víš co?"]),
    "fix": (["Hele,"], ["A teď pozor."]),
}


NO_FILLER_START = ("A ", "*A ", "Ne ", "Místo", "Nejde", "Nezvládneš", "Zbývají", "*Ne")


def _add_filler(beat: dict, role: str, rng: random.Random) -> bool:
    first_sentence = beat["text"].split(".")[0]
    if beat["text"].startswith(NO_FILLER_START) or "?" in first_sentence:
        return False
    lower, alone = FILLER_POOLS.get(role, ([], []))
    pool = [("lower", f) for f in lower] + [("alone", f) for f in alone]
    if not pool:
        return False
    kind, filler = rng.choice(pool)
    if kind == "lower":
        beat["text"] = f"{filler} {_lower_first(beat['text'])}"
    else:
        beat["text"] = f"{filler} {beat['text']}"
    return True


def _beat(line: dict, role: str) -> dict:
    return {"text": line["text"], "broll": list(line["broll"]), "role": role}


def _cta(ch: dict, rng: random.Random) -> dict:
    line = rng.choice(content.CTAS)
    text = line["text"].replace("{ord_say}", content.ORDINALS[ch["id"]]).replace("{ord_show}", f"{ch['id']}.")
    return {"text": text, "broll": ["cover"], "role": "cta"}


# ---------------------------------------------------------------- formáty


def _plan(fmt: str, ch: dict, rng: random.Random) -> list[tuple[dict, bool]]:
    """Vrátí [(beat, povinný?)]. Nepovinné beaty se přidávají/ubírají podle délky."""
    pick = rng.choice
    def sample(seq: list, k: int) -> list:
        """Náhodný výběr, ale v pořadí z e-booku (vysvětlení na sebe navazují)."""
        idx = sorted(rng.sample(range(len(seq)), min(k, len(seq))))
        return [seq[i] for i in idx]

    if fmt == "pov":
        insights = sample(ch["insights"], 2)
        fixes = sample(ch["fixes"], 2)
        return [
            (_beat(pick(ch["pov_hooks"]), "hook"), True),
            (_beat(pick(ch["scenes"]), "scene"), False),
            (_beat(insights[0], "insight"), True),
            (_beat(insights[1], "insight"), False) if len(insights) > 1 else None,
            (_beat(fixes[0], "fix"), True),
            (_beat(fixes[1], "fix"), False) if len(fixes) > 1 else None,
            (_beat(pick(ch["punches"]), "punch"), True),
        ]
    if fmt == "myth":
        insights = sample(ch["insights"], 2)
        fixes = sample(ch["fixes"], 2)
        return [
            (_beat(pick(ch["myth_hooks"]), "hook"), True),
            (_beat(insights[0], "insight"), True),
            (_beat(insights[1], "insight"), False) if len(insights) > 1 else None,
            (_beat(fixes[0], "fix"), True),
            (_beat(fixes[1], "fix"), False) if len(fixes) > 1 else None,
            (_beat(pick(ch["punches"]), "punch"), False),
        ]
    if fmt == "mistake":
        fixes = sample(ch["fixes"], 2)
        return [
            (_beat(pick(ch["mistake_hooks"]), "hook"), True),
            (_beat(pick(ch["scenes"]), "scene"), False),
            (_beat(pick(ch["insights"]), "insight"), True),
            (_beat(fixes[0], "fix"), True),
            (_beat(fixes[1], "fix"), False) if len(fixes) > 1 else None,
            (_beat(pick(ch["punches"]), "punch"), False),
        ]
    if fmt == "list":
        return [
            (_beat(ch["list_hook"], "hook"), True),
            *[(_beat(item, "item"), True) for item in ch["list_items"]],
            (_beat(pick(ch["punches"]), "punch"), False),
        ]
    if fmt == "challenge":
        return [
            (_beat(pick(content.CHALLENGE_HOOKS), "hook"), True),
            (_beat(ch["task_intro"], "intro"), True),
            *[(_beat(step, "step"), True) for step in ch["task_steps"]],
            (_beat(pick(ch["punches"]), "punch"), False),
        ]
    raise ValueError(f"Neznámý formát {fmt}. Možnosti: {', '.join(FORMATS)}")


def _fit_length(plan: list, cta: dict, lo: float, hi: float) -> list[dict]:
    plan = [p for p in plan if p]
    included = [True] * len(plan)
    # začni jen s povinnými, pak přidávej nepovinné, dokud nejsme v rozsahu
    optional = [i for i, (_, req) in enumerate(plan) if not req]
    for i in optional:
        included[i] = False

    def total() -> float:
        beats = [b for (b, _), inc in zip(plan, included) if inc] + [cta]
        return sum(estimate_seconds(b["text"]) for b in beats) + 0.2 * len(beats)

    for i in optional:
        if total() >= lo:
            break
        included[i] = True
        if total() > hi:
            included[i] = False
    return [b for (b, _), inc in zip(plan, included) if inc] + [cta]


# ---------------------------------------------------------------- veřejné API


def generate(chapter_id: int, fmt: str, length: str = "medium", seed: int | None = None,
             filler_rate: float = 0.35) -> dict:
    ch = content.chapter(chapter_id)
    seed = seed if seed is not None else random.randrange(1_000_000)
    rng = random.Random(f"{chapter_id}-{fmt}-{seed}")
    lo, hi = LENGTHS[length]

    beats = _fit_length(_plan(fmt, ch, rng), _cta(ch, rng), lo, hi)

    # mluvené vsuvky – max 2 na video, ne do háčku, výčtu ani CTA
    added = 0
    for b in beats:
        if added >= 2:
            break
        if b["role"] in FILLER_POOLS and rng.random() < filler_rate:
            added += _add_filler(b, b["role"], rng)

    return _finish(ch, fmt, beats, seed, engine="template")


def _finish(ch: dict, fmt: str, beats: list[dict], seed, engine: str) -> dict:
    est = sum(estimate_seconds(b["text"]) for b in beats) + 0.2 * len(beats)
    sid = f"k{ch['id']:02d}-{fmt}-{short_hash(*(b['text'] for b in beats), n=6)}"
    hook_plain = strip_markup(beats[0]["text"])
    tags = content.BASE_HASHTAGS + ch["hashtags"]
    caption = f"{ch['headline']} 👇\n\n{hook_plain}\n\n" + " ".join(f"#{t}" for t in dict.fromkeys(tags))
    return {
        "id": sid,
        "chapter": ch["id"],
        "chapter_title": ch["title"],
        "format": fmt,
        "engine": engine,
        "seed": seed,
        "hook_text": ch["headline"],
        "cta_text": content.CTA_STICKER,
        "beats": beats,
        "est_seconds": round(est, 1),
        "caption": caption,
    }


# ---------------------------------------------------------------- Ollama (volitelné)


def _ollama_prompt(ch: dict, fmt: str, length: str) -> str:
    lo, hi = LENGTHS[length]
    material = {k: [strip_markup(x["text"]) for x in ch[k]] for k in ("scenes", "insights", "fixes", "task_steps", "punches")}
    return f"""Jsi scenárista krátkých videí (TikTok/Reels) pro české vysokoškoláky.
Napiš skript k videu na téma kapitoly „{ch['title']}“ z e-booku „Ještě 5 minut“.
Formát: {fmt}. Délka mluveného textu: {lo:.0f}–{hi:.0f} sekund (cca {int(lo*2.6)}–{int(hi*2.6)} slov).

Pravidla:
- Tykej, mluv jako student/ka, krátké věty, hovorová čeština je OK (např. „dobrý“, „jinej“), ale nepřeháněj.
- První věta je háček, který trefí bolest diváka do 2 sekund.
- Žádné vymyšlené statistiky, výzkumy, recenze ani příběhy „mně to pomohlo“. Jen to, co je v podkladech.
- Klíčová slova (1 na větu) obal hvězdičkami: *takhle*.
- Čísla piš jako [vyslovení|zobrazení], např. [pět|5].
- Nepiš závěrečnou výzvu ke koupi, tu doplním sám.
- Ke každé větě vyber 1–2 tagy záběrů z: {', '.join(content.BROLL_TAGS)}.

Podklady z kapitoly (JSON): {json.dumps(material, ensure_ascii=False)}

Odpověz POUZE JSONem: {{"beats": [{{"text": "...", "broll": ["tag"]}}, ...]}}"""


def generate_ollama(chapter_id: int, fmt: str, length: str, cfg: dict, seed: int | None = None) -> dict:
    import requests

    ch = content.chapter(chapter_id)
    sc = cfg["scripter"]
    try:
        r = requests.post(
            f"{sc['ollama_url'].rstrip('/')}/api/generate",
            json={"model": sc["ollama_model"], "prompt": _ollama_prompt(ch, fmt, length),
                  "format": "json", "stream": False, "options": {"temperature": 0.8}},
            timeout=180,
        )
        r.raise_for_status()
        data = json.loads(r.json()["response"])
        beats = []
        for b in data.get("beats", []):
            text = str(b.get("text", "")).strip()
            if not text:
                continue
            tags = [t for t in b.get("broll", []) if t in content.BROLL_TAGS] or ["desk"]
            beats.append({"text": text, "broll": tags, "role": "llm"})
        if len(beats) < 3:
            raise ValueError("model vrátil málo vět")
        beats[0]["role"] = "hook"
        beats.append(_cta(ch, random.Random(seed)))
        return _finish(ch, fmt, beats, seed, engine=f"ollama:{sc['ollama_model']}")
    except Exception as e:  # noqa: BLE001
        warn(f"Ollama selhala ({e}); používám šablonu.")
        return generate(chapter_id, fmt, length, seed, sc["filler_rate"])


def save(script: dict, folder: Path | None = None) -> Path:
    folder = folder or PATHS["scripts"]
    path = folder / f"{script['id']}.json"
    write_json(path, script)
    return path


def batch(cfg: dict, chapters: list[int], formats: list[str], count: int, length: str,
          seed: int | None = None) -> list[Path]:
    """Vygeneruje `count` skriptů pro každou kombinaci kapitola × formát (bez duplicit)."""
    out: list[Path] = []
    base = seed if seed is not None else random.randrange(1_000_000)
    for chap in chapters:
        for fmt in formats:
            made, attempt = 0, 0
            while made < count and attempt < count * 8:
                s = base + attempt
                attempt += 1
                if cfg["scripter"]["engine"] == "ollama":
                    script = generate_ollama(chap, fmt, length, cfg, s)
                else:
                    script = generate(chap, fmt, length, s, cfg["scripter"]["filler_rate"])
                path = PATHS["scripts"] / f"{script['id']}.json"
                if path.exists():
                    continue
                save(script)
                out.append(path)
                made += 1
                log(f"{path.name}  (~{script['est_seconds']} s)  {strip_markup(script['beats'][0]['text'])}")
    return out
