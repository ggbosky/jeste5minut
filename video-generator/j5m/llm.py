"""Jazykový model, který píše skripty animovaných videí (režim „motion“).

Model běží lokálně, zdarma a bez API klíčů:
  ollama   https://ollama.com – nejjednodušší (`ollama pull gemma3:12b`)
  openai   libovolný server s OpenAI-kompatibilním API na tvém PC:
           LM Studio, llama.cpp server, vLLM, Jan… (výchozí http://localhost:1234/v1)

Co dostane model:
  1. stylový profil  styles/rozbor.md        (jak videa vypadají a znějí)
  2. katalog vizuálů                          (co umí renderer nakreslit)
  3. ukázky          styles/examples/*.json  (few-shot: hotové skripty jako vzor)
  4. podklady z kapitoly e-booku + volitelný brief (např. plán, který ti poslal sledující)

Výstup se zvaliduje a opraví (neznámé vizuály, chybějící konec, moc dlouhé video…).
Když JSON nedává smysl, model dostane chybu a zkusí to znovu.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from . import content
from .config import ROOT
from .markup import estimate_seconds, strip_markup
from .utils import log, short_hash, warn

STYLE_DIR = ROOT / "styles"
FORMATS = ["rozbor", "tip", "mytus", "pov"]
BGS = ["paper", "dark", "coral"]
MOODS = ["wave", "think", "happy", "surprised", "wink"]

VISUALS = {
    "plan": 'rozvrh/plán: {"title": str, "rows": [[den nebo čas, úkol], …3–5 řádků]}',
    "phone": 'zamčený mobil s notifikacemi: {"time": "23:55", "notifications": [[aplikace, text], …1–3]}',
    "alarm": 'budík s tlačítkem: {"time": "7:00", "label": str, "button": "Odložit"}',
    "screentime": 'čas u obrazovky: {"total": "6 h 12 min", "apps": [[název, minuty], …2–4]}',
    "checklist": 'zaškrtávací seznam: {"title": str, "items": [str, …2–4], "done": [indexy zaškrtnutých]}',
    "steps": 'číslované kroky: {"title": str, "items": [str, …2–4]}',
    "timer": 'odpočet: {"minutes": 5, "label": str}',
    "doc": 'dokument (seminárka, bakalářka): {"title": "Bakalarka_final.docx", "text": str nebo ""}',
    "stat": 'velké číslo: {"value": "8 h", "label": str}  (jen čísla z briefu nebo e-booku!)',
    "chat": 'komentář pod videem: {"name": "ty · právě teď", "text": str}',
    "strike": 'přeškrtnutí: {"old": str, "new": str}',
    "quote": 'věta na kartě: {"text": str}',
    "cover": 'obálka e-booku: {}',
    "follow": 'karta profilu s tlačítkem Sledovat: {}',
    "same": 'stejná karta jako v minulé scéně: {}',
}

SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "caption": {"type": "string"},
        "scenes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "bg": {"type": "string", "enum": BGS},
                    "mood": {"type": "string", "enum": MOODS},
                    "visual": {
                        "type": "object",
                        "properties": {"type": {"type": "string", "enum": list(VISUALS)}},
                        "required": ["type"],
                    },
                    "badge": {"type": "integer"},
                    "stickers": {"type": "array", "items": {"type": "string"}},
                    "mark": {"type": "array", "items": {"type": "integer"}},
                    "stamp": {"type": "object", "properties": {"text": {"type": "string"}, "tone": {"type": "string", "enum": ["good", "bad"]}}},
                    "note": {"type": "string"},
                },
                "required": ["text", "bg", "visual"],
            },
        },
    },
    "required": ["title", "caption", "scenes"],
}

FOLLOW_SCENE = {"text": "*Ulož* si to a *sleduj*, ať ti nic *neuteče*!", "bg": "paper", "mood": "wink",
                "visual": {"type": "follow"}}


# ---------------------------------------------------------------- klient


class LLMError(RuntimeError):
    pass


def chat(messages: list[dict], cfg: dict, schema: dict | None = None) -> str:
    import requests

    c = cfg["llm"]
    provider = c["provider"]
    try:
        if provider == "ollama":
            r = requests.post(f"{c['url'].rstrip('/')}/api/chat", timeout=c["timeout"], json={
                "model": c["model"], "messages": messages, "stream": False,
                "format": schema or "json",
                "options": {"temperature": c["temperature"], "num_ctx": c["num_ctx"]},
            })
            r.raise_for_status()
            return r.json()["message"]["content"]
        if provider == "openai":
            headers = {}
            key = os.environ.get("LLM_API_KEY")
            if key:
                headers["Authorization"] = f"Bearer {key}"
            r = requests.post(f"{c['openai_url'].rstrip('/')}/chat/completions", headers=headers, timeout=c["timeout"], json={
                "model": c["model"], "messages": messages, "temperature": c["temperature"],
                "response_format": {"type": "json_object"},
            })
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
    except requests.ConnectionError as e:
        where = c["url"] if provider == "ollama" else c["openai_url"]
        raise LLMError(f"Jazykový model neběží na {where}. Spusť Ollamu (`ollama serve`) nebo LM Studio. ({e})")
    except requests.HTTPError as e:
        body = e.response.text[:300] if e.response is not None else ""
        if "not found" in body.lower():
            raise LLMError(f"Model {c['model']} není stažený. Spusť: ollama pull {c['model']}")
        raise LLMError(f"Chyba jazykového modelu: {e} {body}")
    raise LLMError(f"Neznámý llm.provider „{provider}“ (ollama | openai)")


def _json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            return json.loads(m.group(0))
        raise


# ---------------------------------------------------------------- prompt


def _material(ch: dict) -> str:
    def plain(key):
        return [strip_markup(x["text"]) for x in ch.get(key, [])]

    return json.dumps({
        "kapitola": f"{ch['id']}. {ch['title']}",
        "o_čem": ch["headline"],
        "situace_studentů": plain("scenes") + plain("pov_hooks"),
        "proč_to_tak_je": plain("insights"),
        "co_dělat": plain("fixes") + plain("list_items"),
        "úkol_na_5_minut": [strip_markup(ch["task_intro"]["text"])] + plain("task_steps"),
        "pointy": plain("punches"),
    }, ensure_ascii=False, indent=1)


def _examples() -> list[tuple[str, str]]:
    out = []
    for p in sorted((STYLE_DIR / "examples").glob("*.json")):
        ex = json.loads(p.read_text(encoding="utf-8"))
        req = f"Formát: {ex['format']}. Kapitola: {ex['chapter']}."
        body = {"title": ex["title"], "caption": ex.get("caption", ex["title"]),
                "scenes": ex["beats"]}
        out.append((req, json.dumps(body, ensure_ascii=False)))
    return out


def build_messages(fmt: str, ch: dict, brief: str | None, episode: int | None, cfg: dict) -> list[dict]:
    style = (STYLE_DIR / cfg["llm"]["style"]).read_text(encoding="utf-8")
    catalog = "\n".join(f"- {k}: {v}" for k, v in VISUALS.items())
    brand = cfg["brand"]
    system = f"""Jsi scenárista a motion designer krátkých vertikálních videí pro Instagram Reels a TikTok.
Píšeš česky pro vysokoškoláky. Propaguješ e-book „{brand['name']}“ (praktický průvodce proti odkládání učení
a bakalářky, 8 kapitol po 5 minutách, každá končí úkolem). Profil na sítích: {brand['handle']}.

{style}

## Katalog vizuálů (pole „visual“, jiné typy renderer neumí)
{catalog}

## Výstup
Vrať POUZE JSON objekt:
{{"title": krátký název videa,
  "caption": popisek pod video (1–2 věty + otázka do komentářů + 3–5 hashtagů bez diakritiky),
  "scenes": [{{"text", "bg", "mood", "visual", "badge" (0 = žádný), "stickers", "mark", "stamp" ({{}} = žádné), "note"}}]}}
"""
    msgs = [{"role": "system", "content": system}]
    for req, ans in _examples():
        msgs += [{"role": "user", "content": req}, {"role": "assistant", "content": ans}]
    task = [f"Formát: {fmt}. Kapitola: {ch['id']}."]
    if fmt == "rozbor":
        n = episode or 1
        task.append(f"Je to díl série: nálepka „ROZBOR #{n}“, poznámka „série rozborů · díl {n}“, "
                    f"ve výzvě do komentářů „rozbor #{n + 1} = tvůj …“.")
    if brief:
        task.append(f"BRIEF (skutečný podklad, rozebírej přesně tohle, nic si nevymýšlej):\n{brief.strip()}")
    else:
        task.append("Brief není: rozebírej typický případ a mluv o něm jako o typickém, ne skutečném.")
    task.append(f"Podklady z e-booku:\n{_material(ch)}")
    task.append("Napiš nový skript. Nepřebírej věty z ukázek doslova – ukázky jsou jen vzor stylu.")
    msgs.append({"role": "user", "content": "\n\n".join(task)})
    return msgs


# ---------------------------------------------------------------- validace


def _as_list(v) -> list:
    if isinstance(v, list):
        return v
    if isinstance(v, str) and v.strip():
        return [x.strip() for x in re.split(r"[;\n]", v) if x.strip()]
    return []


def _clean_visual(v: dict, first: bool, scene_text: str) -> dict:
    if not isinstance(v, dict) or v.get("type") not in VISUALS:
        return {"type": "quote", "text": strip_markup(scene_text)}
    t = v["type"]
    if t == "same" and first:
        return {"type": "quote", "text": strip_markup(scene_text)}
    if t in ("plan",):
        rows = [r if isinstance(r, list) else str(r).split(" ", 1) for r in _as_list(v.get("rows"))][:6]
        v["rows"] = [[str(x) for x in (list(r) + ["", ""])[:2]] for r in rows] or [["Po", "Učit se"]]
    if t == "phone":
        v["notifications"] = [list(map(str, (list(n) if isinstance(n, list) else ["Zpráva", n]) + [""]))[:2]
                              for n in _as_list(v.get("notifications"))][:3] or [["Instagram", "nová zpráva"]]
    if t == "screentime":
        apps = []
        for a in _as_list(v.get("apps"))[:4]:
            try:
                apps.append([str(a[0]), float(re.sub(r"[^\d.]", "", str(a[1])) or 30)])
            except (IndexError, TypeError):
                continue
        v["apps"] = apps or [["TikTok", 120], ["Instagram", 80]]
    if t in ("checklist", "steps"):
        v["items"] = [str(x) for x in _as_list(v.get("items"))][:5] or ["Krok"]
        v["done"] = [int(x) for x in _as_list(v.get("done")) if str(x).isdigit()]
    if t == "timer":
        try:
            v["minutes"] = float(v.get("minutes", 5))
        except (TypeError, ValueError):
            v["minutes"] = 5
    return v


def validate(data: dict, cfg: dict) -> tuple[list[dict], list[str]]:
    """Vrátí (opravené scény, seznam problémů k nahlášení modelu)."""
    problems: list[str] = []
    scenes = data.get("scenes") if isinstance(data, dict) else None
    if not isinstance(scenes, list) or not scenes:
        return [], ["Chybí pole „scenes“."]
    out = []
    for i, s in enumerate(scenes):
        if not isinstance(s, dict) or not str(s.get("text", "")).strip():
            continue
        text = " ".join(str(s["text"]).split())
        if text.count("*") % 2:
            text = text.replace("*", "")
        sc = {"text": text,
              "bg": s.get("bg") if s.get("bg") in BGS else "paper",
              "mood": s.get("mood") if s.get("mood") in MOODS else "wave",
              "visual": _clean_visual(s.get("visual"), not out, text)}
        try:
            b = int(s.get("badge") or 0)
            if 1 <= b <= 9:
                sc["badge"] = b
        except (TypeError, ValueError):
            pass
        st = [str(x)[:30] for x in _as_list(s.get("stickers")) if str(x).strip()][:2]
        if st:
            sc["stickers"] = st
        mk = [int(x) for x in _as_list(s.get("mark")) if str(x).lstrip("-").isdigit()]
        if mk:
            sc["mark"] = mk
        stamp = s.get("stamp")
        if isinstance(stamp, dict) and str(stamp.get("text", "")).strip():
            tone = stamp.get("tone") if stamp.get("tone") in ("good", "bad") else ("bad" if "✗" in stamp["text"] or "CHYB" in stamp["text"].upper() else "good")
            sc["stamp"] = {"text": str(stamp["text"])[:14], "tone": tone}
        note = str(s.get("note") or "").strip().lstrip("/ ")
        if note:
            sc["note"] = note[:44]
        if len(text.split()) > 16:
            problems.append(f"Scéna {i + 1} má {len(text.split())} slov, max je 12.")
        out.append(sc)

    if out and out[-1]["visual"]["type"] != "follow":
        out.append(dict(FOLLOW_SCENE))
    brand = cfg["brand"]
    for sc in out:
        if sc["visual"]["type"] == "follow":
            sc["visual"].setdefault("name", brand["name"])
            sc["visual"].setdefault("handle", brand["handle"])

    secs = sum(estimate_seconds(s["text"]) for s in out) / cfg["tts"]["motion_speed"] + 0.1 * len(out)
    if len(out) < 5:
        problems.append(f"Jen {len(out)} scén, potřebuju 7–10.")
    if secs > 34:
        problems.append(f"Video by mělo ~{secs:.0f} s, max je 28 s. Zkrať věty nebo uber scénu.")
    return out, problems


# ---------------------------------------------------------------- hlavní funkce


def write(fmt: str, chapter_id: int, cfg: dict, brief: str | None = None, episode: int | None = None,
          refine: bool | None = None) -> dict:
    if fmt not in FORMATS:
        raise ValueError(f"Formát {fmt}? Možnosti: {', '.join(FORMATS)}")
    ch = content.chapter(chapter_id)
    msgs = build_messages(fmt, ch, brief, episode, cfg)
    log(f"Píšu skript ({cfg['llm']['provider']}: {cfg['llm']['model']}) – formát {fmt}, kapitola {chapter_id}…")

    scenes, data = [], {}
    for attempt in range(1, int(cfg["llm"]["retries"]) + 2):
        raw = chat(msgs, cfg, SCHEMA)
        try:
            data = _json(raw)
        except json.JSONDecodeError as e:
            problems = [f"Neplatný JSON: {e}"]
            scenes = []
        else:
            scenes, problems = validate(data, cfg)
        if scenes and not problems:
            break
        if attempt > int(cfg["llm"]["retries"]):
            if not scenes:
                raise LLMError("Model nevrátil použitelný skript ani po opravách. Zkus jiný model nebo to spusť znovu.")
            warn("Skript má drobné vady, ukládám ho i tak: " + " ".join(problems))
            break
        warn(f"Pokus {attempt}: {' '.join(problems)} → posílám modelu k opravě")
        msgs += [{"role": "assistant", "content": raw},
                 {"role": "user", "content": "Oprav tohle a vrať celý JSON znovu: " + " ".join(problems)}]

    if refine if refine is not None else cfg["llm"]["refine"]:
        scenes = _refine(scenes, cfg)

    tags = ["vysoka", "student", "jeste5minut"] + ch["hashtags"]
    caption = str(data.get("caption") or ch["headline"]).strip()
    if "#" not in caption:
        caption += "\n\n" + " ".join(f"#{t}" for t in dict.fromkeys(tags))
    sid = f"{fmt}-k{chapter_id:02d}-{short_hash(*(s['text'] for s in scenes), n=6)}"
    return {
        "id": sid, "mode": "motion", "format": fmt, "chapter": chapter_id, "chapter_title": ch["title"],
        "title": str(data.get("title") or ch["headline"]), "brand": cfg["brand"]["name"],
        "engine": f"{cfg['llm']['provider']}:{cfg['llm']['model']}", "episode": episode,
        "brief": brief or None, "caption": caption, "beats": scenes,
        "est_seconds": round(sum(estimate_seconds(s["text"]) for s in scenes) / cfg["tts"]["motion_speed"], 1),
    }


def _refine(scenes: list[dict], cfg: dict) -> list[dict]:
    """Druhé kolo: model přepíše jen texty, aby zněly víc jako mluvená řeč."""
    texts = [s["text"] for s in scenes]
    msgs = [
        {"role": "system", "content": "Jsi editor mluveného slova pro krátká videa. Píšeš přirozenou češtinou 20letého studenta."},
        {"role": "user", "content": (
            "Uprav tyhle věty voiceoveru, aby zněly přirozeně nahlas: kratší, údernější, bez knižních obratů. "
            "Zachovej význam, pořadí, počet vět, hvězdičky *akcent* i závorky [vyslovení|zobrazení]. "
            "Nic nepřidávej. Vrať JSON {\"texts\": [...]} se stejným počtem položek.\n\n"
            + json.dumps(texts, ensure_ascii=False))},
    ]
    try:
        new = _json(chat(msgs, cfg, {"type": "object", "properties": {"texts": {"type": "array", "items": {"type": "string"}}}, "required": ["texts"]}))["texts"]
    except Exception as e:  # noqa: BLE001
        warn(f"Doladění textů selhalo ({e}), nechávám původní.")
        return scenes
    if len(new) != len(scenes):
        warn("Doladění vrátilo jiný počet vět, nechávám původní.")
        return scenes
    for s, t in zip(scenes, new):
        t = " ".join(str(t).split())
        if t and t.count("*") % 2 == 0 and len(t.split()) <= 16:
            s["text"] = t
    return scenes


def save(script: dict) -> Path:
    from .config import PATHS
    from .utils import write_json

    path = PATHS["scripts"] / f"{script['id']}.json"
    write_json(path, script)
    return path
