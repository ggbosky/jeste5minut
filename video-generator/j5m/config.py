"""Konfigurace: výchozí hodnoty + volitelný config.toml v kořeni video-generator/."""

from __future__ import annotations

import copy
import os
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PATHS = {
    "scripts": ROOT / "scripts",
    "audio": ROOT / "audio",
    "voices": ROOT / "audio" / "voices",
    "music": ROOT / "audio" / "music",
    "video": ROOT / "video",
    "library": ROOT / "video" / "library",
    "cache": ROOT / "video" / "cache",
    "output": ROOT / "output",
    "assets": ROOT / "assets",
    "models": ROOT / "models",
}

DEFAULTS: dict = {
    "video": {
        "width": 1080,
        "height": 1920,
        "fps": 30,
        "crf": 18,
        "preset": "medium",
        "min_cut": 2.0,          # jump cut nejdřív po 2 s
        "max_cut": 4.0,          # a nejpozději po 4 s
        "punch_in": 1.14,        # přiblížení u každého druhého střihu (CapCut „punch-in“)
        "shake_px": 5,           # jemný „z ruky“ pohyb kamery
        "grain": 7,              # filmové zrno (0 = vypnout)
        "vignette": True,
        "grade": "warm",         # warm | neutral | cold
        "tail": 0.7,             # kolik sekund nechat po posledním slově
        "cta_visual": "cover",   # cover = obálka e-booku pod závěrečnou výzvou, broll = běžný záběr
    },
    "captions": {
        "style": "pop",          # pop = slova naskakují | highlight = aktivní slovo v rámečku
        "font": "assets/fonts/Inter-Black.otf",
        "font_size": 104,
        "keyword_scale": 1.14,
        "max_words": 3,          # nejvíc slov na jedné „stránce“ titulků
        "max_chars": 18,
        "y": 0.60,               # svislá pozice středu titulků (0 = nahoře, 1 = dole)
        "cta_y": 0.76,           # při závěrečné výzvě titulky níž, ať nepřekrývají obálku
        "uppercase": False,
        "color": "#FFFFFF",
        "keyword_color": "#FB6720",   # brand coral z webu
        "stroke_color": "#0B1120",
        "stroke": 10,
        "shadow": True,
        "hook_box": True,        # bílý „nadpis“ nahoře v prvních sekundách
        "hook_seconds": 3.2,
        "hook_font": "assets/fonts/Inter-ExtraBold.otf",
        "cta_sticker": True,
        "progress_bar": False,
    },
    "tts": {
        "backend": "xtts",       # xtts | piper | dummy
        "language": "cs",
        "gap": 0.16,             # pauza mezi větami (s); krátká = svižné tempo
        "xtts": {
            "model": "tts_models/multilingual/multi-dataset/xtts_v2",
            "speaker": "Ana Florence",   # vestavěný hlas, když v audio/voices/ není vlastní nahrávka
            "speed": 1.08,
            "temperature": 0.7,
            "seed": 1234,
        },
        "piper": {
            "voice": "cs_CZ-jirka-medium",
            "length_scale": 0.92,         # < 1 = rychlejší řeč
            "noise_scale": 0.667,
            "noise_w": 0.8,
        },
    },
    "align": {
        "method": "auto",        # auto | whisper | estimate
        "whisper_model": "small",
    },
    "audio": {
        "sample_rate": 48000,
        "loudness": -14.0,       # LUFS – standard pro TikTok/Reels/Shorts
        "music_volume": 0.22,
        "whoosh": True,          # jemný „swoosh“ na střizích
        "whoosh_gain": 0.10,
        "keyword_tick": False,
    },
    "broll": {
        "pexels": True,          # stahovat z Pexels, když chybí vlastní záběry (vyžaduje PEXELS_API_KEY zdarma)
        "per_tag": 6,            # kolik klipů na tag stáhnout do cache
    },
    "scripter": {
        "engine": "template",    # template | ollama
        "ollama_model": "llama3.1:8b",
        "ollama_url": "http://localhost:11434",
        "filler_rate": 0.35,
    },
}


def _merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


def load(path: str | os.PathLike | None = None) -> dict:
    cfg = copy.deepcopy(DEFAULTS)
    p = Path(path) if path else ROOT / "config.toml"
    if p.exists():
        with open(p, "rb") as f:
            cfg = _merge(cfg, tomllib.load(f))
    return cfg


def resolve(path: str) -> Path:
    p = Path(path)
    return p if p.is_absolute() else ROOT / p
