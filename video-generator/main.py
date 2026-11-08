#!/usr/bin/env python3
"""Ještě 5 minut – generátor krátkých videí (TikTok / Reels / Shorts).

Příklady:
  python main.py setup                         # kontrola ffmpeg + stažení českého hlasu Piper
  python main.py scripts --chapter 2 --count 2 # vygeneruje skripty do scripts/
  python main.py list                          # přehled skriptů a hotových videí
  python main.py render scripts/k02-pov-ab12cd.json
  python main.py batch --limit 5               # vyrenderuje všechno, co ještě nemá video
  python main.py broll --per-tag 6             # předem stáhne B-roll z Pexels

Podrobnosti v README.md.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from j5m import config as config_mod  # noqa: E402
from j5m.config import PATHS  # noqa: E402
from j5m.utils import log, read_json, warn  # noqa: E402


def _chapters(arg: str | None) -> list[int]:
    if not arg or arg == "all":
        return list(range(1, 9))
    return [int(x) for x in arg.split(",")]


def cmd_setup(args, cfg) -> None:
    ok = True
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool):
            log(f"{tool}: OK")
        else:
            warn(f"{tool} chybí – nainstaluj ffmpeg (viz README)")
            ok = False
    for mod, what in (("moviepy", "střih"), ("PIL", "titulky"), ("piper", "hlas Piper"),
                      ("TTS", "hlas XTTS-v2 (coqui-tts)"), ("torch", "PyTorch pro XTTS"),
                      ("faster_whisper", "přesné časování titulků")):
        try:
            __import__(mod)
            log(f"{what}: OK")
        except ImportError:
            warn(f"{what}: chybí modul {mod}")
    try:
        from j5m.tts import ensure_piper_voice

        p = ensure_piper_voice(cfg["tts"]["piper"]["voice"])
        log(f"Piper hlas: {p.name}")
    except Exception as e:  # noqa: BLE001
        warn(f"Piper hlas se nepodařilo stáhnout: {e}")
    import os

    log("PEXELS_API_KEY: " + ("nastaven" if os.environ.get("PEXELS_API_KEY") else "není (použije se vlastní knihovna / grafické karty)"))
    voices = list(PATHS["voices"].glob("*.wav"))
    log(f"Referenční nahrávky hlasu pro XTTS: {len(voices)}")
    for d in ("scripts", "audio", "video", "output", "library"):
        PATHS[d].mkdir(parents=True, exist_ok=True)
    if not ok:
        sys.exit(1)


def cmd_scripts(args, cfg) -> None:
    from j5m import scripter

    if args.engine:
        cfg["scripter"]["engine"] = args.engine
    formats = scripter.FORMATS if args.format == "all" else args.format.split(",")
    paths = scripter.batch(cfg, _chapters(args.chapter), formats, args.count, args.length, args.seed)
    log(f"Hotovo: {len(paths)} nových skriptů ve {PATHS['scripts']}")


def cmd_list(args, cfg) -> None:
    from j5m.markup import strip_markup

    scripts = sorted(PATHS["scripts"].glob("*.json"))
    if not scripts:
        print("Žádné skripty. Spusť: python main.py scripts")
        return
    for p in scripts:
        s = read_json(p)
        done = "✔" if (PATHS["output"] / f"{s['id']}.mp4").exists() else " "
        mode = "motion" if s.get("mode") == "motion" else "broll "
        print(f"{done} {s['id']:<24} {mode} ~{s.get('est_seconds', 0):>4} s  {strip_markup(s['beats'][0]['text'])}")


def cmd_show(args, cfg) -> None:
    from j5m.markup import strip_markup

    s = read_json(args.script)
    print(f"{s['id']} · kapitola {s['chapter']} ({s.get('chapter_title', '')}) · {s['format']} · ~{s.get('est_seconds', '?')} s\n")
    for b in s["beats"]:
        if s.get("mode") == "motion":
            extra = "".join(f" #{b['badge']}" for _ in [0] if b.get("badge"))
            print(f"  [{b.get('bg', 'paper'):<5} {b['visual']['type']:<10}{extra}] {strip_markup(b['text'])}")
        else:
            print(f"  [{'/'.join(b['broll'])}] {strip_markup(b['text'])}")
    print("\n" + s["caption"])


def cmd_write(args, cfg) -> None:
    from j5m import llm

    if args.model:
        cfg["llm"]["model"] = args.model
    if args.provider:
        cfg["llm"]["provider"] = args.provider
    brief = args.brief
    if args.brief_file:
        brief = Path(args.brief_file).read_text(encoding="utf-8")
    made = []
    for i in range(args.count):
        episode = args.episode + i if args.episode else None
        try:
            script = llm.write(args.format, args.chapter, cfg, brief, episode, args.refine or None)
        except llm.LLMError as e:
            raise SystemExit(f"! {e}")
        path = llm.save(script)
        made.append(path)
        log(f"{path.name}  (~{script['est_seconds']} s)  „{script['title']}“")
        cmd_show(argparse.Namespace(script=str(path)), cfg)
    if args.render:
        args.scripts = [str(p) for p in made]
        args.keep = False
        args.style = None
        args.draft = False
        args.no_pexels = False
        cmd_render(args, cfg)


def cmd_preview(args, cfg) -> None:
    from j5m.motion import preview

    s = read_json(args.script)
    if s.get("mode") != "motion":
        raise SystemExit("Náhled umí jen skripty v režimu motion (z příkazu write nebo styles/examples).")
    out = Path(args.out or (PATHS["output"] / f"{s['id']}-nahled.png"))
    n = len(s["beats"])
    from j5m.markup import estimate_seconds

    t, times = 0.0, []
    for b in s["beats"]:
        d = max(estimate_seconds(b["text"]), 1.0)
        times.append(t + d * 0.85)
        t += d + 0.15
    preview(s, cfg, times[:n], out)
    log(f"Náhled → {out}")


def cmd_voice(args, cfg) -> None:
    from j5m.tts import make_backend, synthesize_script

    s = read_json(args.script)
    backend = make_backend(args.tts or cfg["tts"]["backend"], cfg)
    t = synthesize_script(s, backend, cfg, PATHS["audio"] / s["id"])
    log(f"{PATHS['audio'] / s['id'] / 'voice.wav'}  ({t['duration']:.1f} s)")


def _apply_draft(cfg) -> None:
    cfg["video"].update({"width": 540, "height": 960, "preset": "veryfast", "crf": 23})


def cmd_render(args, cfg) -> None:
    from j5m.render import render

    if args.draft:
        _apply_draft(cfg)
    if args.style:
        cfg["captions"]["style"] = args.style
    for script in args.scripts:
        render(Path(script), cfg, args.tts, args.align, allow_pexels=not args.no_pexels, keep=args.keep)


def cmd_batch(args, cfg) -> None:
    from j5m.render import render

    if args.draft:
        _apply_draft(cfg)
    todo = [p for p in sorted(PATHS["scripts"].glob("*.json"))
            if args.force or not (PATHS["output"] / f"{read_json(p)['id']}.mp4").exists()]
    if args.chapter:
        chs = set(_chapters(args.chapter))
        todo = [p for p in todo if read_json(p)["chapter"] in chs]
    todo = todo[: args.limit] if args.limit else todo
    log(f"K vyrenderování: {len(todo)}")
    for i, p in enumerate(todo, 1):
        log(f"=== {i}/{len(todo)}: {p.name}")
        try:
            render(p, cfg, args.tts, args.align, allow_pexels=not args.no_pexels)
        except Exception as e:  # noqa: BLE001
            warn(f"{p.name} selhal: {e}")


def cmd_broll(args, cfg) -> None:
    from j5m.broll import prefetch

    prefetch(cfg, args.tags.split(",") if args.tags else None, args.per_tag)


def main() -> None:
    ap = argparse.ArgumentParser(description="Ještě 5 minut – lokální generátor krátkých videí")
    ap.add_argument("--config", help="cesta ke config.toml (výchozí: video-generator/config.toml)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("setup", help="zkontroluje závislosti a stáhne český hlas Piper")

    p = sub.add_parser("scripts", help="vygeneruje skripty z kapitol e-booku")
    p.add_argument("--chapter", default="all", help="1–8, víc čárkou (2,5) nebo all")
    p.add_argument("--format", default="all", help="pov,myth,mistake,list,challenge nebo all")
    p.add_argument("--count", type=int, default=1, help="kolik skriptů na kapitolu × formát")
    p.add_argument("--length", default="medium", choices=["short", "medium", "long"])
    p.add_argument("--engine", choices=["template", "ollama"], help="přepíše scripter.engine z configu")
    p.add_argument("--seed", type=int)

    p = sub.add_parser("write", help="jazykový model napíše animované video ve stylu rozborů")
    p.add_argument("--format", default="rozbor", choices=["rozbor", "tip", "mytus", "pov"])
    p.add_argument("--chapter", type=int, default=1, help="kapitola e-booku 1–8")
    p.add_argument("--brief", help="skutečný podklad k rozboru (např. plán od sledujícího)")
    p.add_argument("--brief-file", help="brief ze souboru")
    p.add_argument("--episode", type=int, help="číslo dílu série (ROZBOR #N)")
    p.add_argument("--count", type=int, default=1)
    p.add_argument("--refine", action="store_true", help="druhé kolo: věty přepsat přirozeněji")
    p.add_argument("--model", help="např. gemma3:12b, qwen3:14b")
    p.add_argument("--provider", choices=["ollama", "openai"])
    p.add_argument("--render", action="store_true", help="hned i vyrenderovat")
    p.add_argument("--tts", choices=["xtts", "piper", "dummy"])
    p.add_argument("--align", choices=["auto", "whisper", "estimate"])

    p = sub.add_parser("preview", help="rychlý náhled motion skriptu jako obrázek (bez hlasu)")
    p.add_argument("script")
    p.add_argument("--out")

    sub.add_parser("list", help="přehled skriptů (✔ = video hotové)")

    p = sub.add_parser("show", help="vypíše skript čitelně")
    p.add_argument("script")

    p = sub.add_parser("voice", help="jen namluví skript (audio/<id>/voice.wav)")
    p.add_argument("script")
    p.add_argument("--tts", choices=["xtts", "piper", "dummy"])

    for name, hlp in (("render", "vyrenderuje jeden nebo víc skriptů"), ("batch", "vyrenderuje všechny skripty bez videa")):
        p = sub.add_parser(name, help=hlp)
        if name == "render":
            p.add_argument("scripts", nargs="+")
            p.add_argument("--keep", action="store_true", help="nemazat mezisoubory ve video/work/")
            p.add_argument("--style", choices=["pop", "highlight"], help="styl titulků")
        else:
            p.add_argument("--limit", type=int)
            p.add_argument("--chapter")
            p.add_argument("--force", action="store_true", help="přerenderovat i hotová videa")
        p.add_argument("--tts", choices=["xtts", "piper", "dummy"])
        p.add_argument("--align", choices=["auto", "whisper", "estimate"])
        p.add_argument("--no-pexels", action="store_true", help="nestahovat nic z Pexels")
        p.add_argument("--draft", action="store_true", help="rychlý náhled v 540×960")

    p = sub.add_parser("broll", help="předem stáhne B-roll z Pexels do video/cache/")
    p.add_argument("--tags", help="seznam tagů čárkou (výchozí: všechny)")
    p.add_argument("--per-tag", type=int, default=6)

    args = ap.parse_args()
    cfg = config_mod.load(args.config)
    {"setup": cmd_setup, "scripts": cmd_scripts, "write": cmd_write, "preview": cmd_preview, "list": cmd_list, "show": cmd_show, "voice": cmd_voice,
     "render": cmd_render, "batch": cmd_batch, "broll": cmd_broll}[args.cmd](args, cfg)


if __name__ == "__main__":
    main()
