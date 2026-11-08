"""Mini-syntaxe skriptů.

  *klíčové slovo*   → zvýrazněné v titulcích (může přes víc slov)
  [řekni|ukaž]      → hlas vysloví „řekni“, titulek ukáže „ukaž“; např. [pět|5]

parse() vrací seznam jednotek (Unit). Jedna jednotka = jedno „slovo“ titulku.
Může ale obsahovat víc mluvených slov ([Dny čtrnáct až dvanáct|Dny 14–12]).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

VOWELS = set("aeiouyáéíóúůýě")


@dataclass
class Unit:
    say: str     # co vysloví TTS (včetně interpunkce)
    show: str    # co se ukáže v titulku (bez zbytečné interpunkce)
    key: bool    # klíčové slovo

    @property
    def say_words(self) -> list[str]:
        return self.say.split()


def _clean_show(text: str) -> str:
    text = text.replace("„", "").replace("“", "").replace('"', "")
    text = text.strip()
    # čárky, středníky, dvojtečky a tečky na konci slova pryč (ale „2.1“ / „2.“ nech)
    while text and text[-1] in ",;:" :
        text = text[:-1]
    if text.endswith(".") and len(text) > 1 and not text[-2].isdigit():
        text = text.rstrip(".")
    return text


def parse(text: str) -> list[Unit]:
    units: list[Unit] = []
    say, show, key_hit = [], [], False
    key = False
    i = 0

    def flush():
        nonlocal say, show, key_hit
        s = "".join(say).strip()
        if s:
            units.append(Unit(say=s, show=_clean_show("".join(show)), key=key_hit))
        say, show, key_hit = [], [], False

    while i < len(text):
        c = text[i]
        if c == "*":
            key = not key
            i += 1
            continue
        if c == "[":
            end = text.index("]", i)
            body = text[i + 1:end]
            s_part, _, d_part = body.partition("|")
            say.append(s_part)
            show.append(d_part if d_part else s_part)
            key_hit = key_hit or key
            i = end + 1
            continue
        if c.isspace():
            flush()
            i += 1
            continue
        say.append(c)
        show.append(c)
        if c.isalnum():
            key_hit = key_hit or key
        i += 1
    flush()
    return units


def say_text(units: list[Unit]) -> str:
    return " ".join(u.say for u in units)


def show_text(units: list[Unit]) -> str:
    return " ".join(u.show for u in units)


def strip_markup(text: str) -> str:
    """Text pro lidi (popisky, náhledy): ukaž verzi titulku, bez hvězdiček."""
    text = re.sub(r"\[([^|\]]*)\|([^\]]*)\]", r"\2", text)
    return text.replace("*", "")


def spoken_text(text: str) -> str:
    """Text pro TTS: mluvená verze, bez hvězdiček."""
    text = re.sub(r"\[([^|\]]*)\|([^\]]*)\]", r"\1", text)
    return text.replace("*", "")


def syllables(word: str) -> int:
    """Hrubý odhad slabik v češtině (samohlásky + slabikotvorné r/l)."""
    w = word.lower()
    n = sum(1 for ch in w if ch in VOWELS)
    if n == 0:
        n = 1 if any(ch.isalpha() for ch in w) else 0
    return max(n, 1) if any(ch.isalnum() for ch in w) else 0


def pause_weight(word: str) -> float:
    """Pauza po slově v „slabikách“ – podle interpunkce."""
    w = word.rstrip("*]“\"")
    if not w:
        return 0.0
    if w[-1] in ".!?":
        return 1.6
    if w[-1] in ",;:–-":
        return 0.8
    return 0.0


def normalize(word: str) -> str:
    """Pro porovnání se slovy z Whisperu: malá písmena, bez diakritiky a interpunkce."""
    w = unicodedata.normalize("NFKD", word.lower())
    w = "".join(ch for ch in w if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]", "", w)


def estimate_seconds(text: str, syll_per_sec: float = 5.6) -> float:
    words = spoken_text(text).split()
    syl = sum(syllables(w) + pause_weight(w) for w in words)
    return syl / syll_per_sec
