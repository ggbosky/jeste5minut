"""B-roll: odkud se berou záběry pod mluvené slovo.

Pořadí zdrojů pro každý střih:
  1. video/library/<tag>/   vlastní záběry (nejautentičtější – natoč si je mobilem)
  2. video/cache/pexels/<tag>/   už stažené klipy z Pexels
  3. Pexels API (zdarma, potřebuje PEXELS_API_KEY) – stáhne a uloží do cache
  4. libovolný jiný klip z knihovny/cache
  5. generovaná grafická karta v barvách značky (funguje vždycky, i offline)

Tag „cover“ = obálka e-booku pod závěrečnou výzvou (assets/cover.png).
"""

from __future__ import annotations

import os
import random
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .config import PATHS, resolve
from .content import BROLL_TAGS
from .utils import log, probe_duration, read_json, warn, write_json

VIDEO_EXT = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
PEXELS_URL = "https://api.pexels.com/videos/search"


@dataclass
class Source:
    path: Path
    kind: str          # "video" | "image"
    duration: float = 0.0


def _files(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.iterdir() if p.suffix.lower() in VIDEO_EXT | IMAGE_EXT and not p.name.startswith("."))


class BrollLibrary:
    def __init__(self, cfg: dict, rng: random.Random, allow_pexels: bool = True):
        self.cfg = cfg
        self.rng = rng
        self.key = os.environ.get("PEXELS_API_KEY", "").strip()
        self.pexels = allow_pexels and cfg["broll"]["pexels"] and bool(self.key)
        self.used: set[Path] = set()
        self._durations: dict[Path, float] = {}
        self._fetched: set[str] = set()
        self.cards_dir = PATHS["cache"] / "cards"

    # ------------------------------------------------------------ výběr

    def _candidates(self, tag: str) -> list[Path]:
        return _files(PATHS["library"] / tag) + _files(PATHS["cache"] / "pexels" / tag)

    def _all(self) -> list[Path]:
        out: list[Path] = []
        for base in (PATHS["library"], PATHS["cache"] / "pexels"):
            if base.is_dir():
                for d in base.iterdir():
                    if d.is_dir():
                        out += _files(d)
        return out

    def _source(self, p: Path) -> Source:
        if p.suffix.lower() in IMAGE_EXT:
            return Source(p, "image")
        if p not in self._durations:
            self._durations[p] = probe_duration(p)
        return Source(p, "video", self._durations[p])

    def _choose(self, paths: list[Path]) -> Path | None:
        if not paths:
            return None
        fresh = [p for p in paths if p not in self.used]
        p = self.rng.choice(fresh or paths)
        self.used.add(p)
        return p

    def pick(self, tags: list[str], cut_index: int, chapter: int) -> Source:
        tags = [t for t in tags if t] or ["desk"]
        if "cover" in tags and self.cfg["video"]["cta_visual"] == "cover":
            return Source(self.cover_card(), "image")
        tags = [t for t in tags if t != "cover"] or ["desk", "notes", "library"]
        order = tags[:]
        self.rng.shuffle(order)
        for tag in order:
            p = self._choose([c for c in self._candidates(tag) if c not in self.used])
            if p:
                return self._source(p)
        if self.pexels:
            for tag in order:
                if tag in self._fetched:
                    continue
                self.fetch_tag(tag, self.cfg["broll"]["per_tag"])
                p = self._choose([c for c in self._candidates(tag) if c not in self.used])
                if p:
                    return self._source(p)
        p = self._choose(self._candidates(order[0])) or self._choose(self._all())
        if p:
            return self._source(p)
        return Source(self.brand_card(cut_index, chapter), "image")

    # ------------------------------------------------------------ Pexels

    def fetch_tag(self, tag: str, count: int) -> int:
        """Stáhne až `count` portrétních klipů pro tag do video/cache/pexels/<tag>/."""
        import requests

        self._fetched.add(tag)
        if not self.key:
            warn("PEXELS_API_KEY není nastavený – Pexels přeskakuju.")
            return 0
        query = BROLL_TAGS.get(tag, tag.replace("_", " "))
        folder = PATHS["cache"] / "pexels" / tag
        folder.mkdir(parents=True, exist_ok=True)
        credits_path = folder / "credits.json"
        credits = read_json(credits_path) if credits_path.exists() else {}
        have = len(_files(folder))
        if have >= count:
            return 0
        try:
            r = requests.get(PEXELS_URL, headers={"Authorization": self.key},
                             params={"query": query, "orientation": "portrait", "size": "medium", "per_page": 30},
                             timeout=30)
            r.raise_for_status()
            videos = r.json().get("videos", [])
        except Exception as e:  # noqa: BLE001
            warn(f"Pexels hledání „{query}“ selhalo: {e}")
            return 0
        got = 0
        for v in videos:
            if have + got >= count:
                break
            if str(v["id"]) in credits or v.get("duration", 0) < 4:
                continue
            files = [f for f in v.get("video_files", []) if f.get("file_type") == "video/mp4" and f.get("height") and f.get("width")]
            portrait = [f for f in files if f["height"] > f["width"] and f["height"] >= 1280]
            if not portrait:
                continue
            best = min(portrait, key=lambda f: abs(f["height"] - 1920))
            target = folder / f"pexels-{v['id']}.mp4"
            try:
                log(f"Pexels ↓ {tag}: {v.get('url', v['id'])}")
                with requests.get(best["link"], stream=True, timeout=120) as dl:
                    dl.raise_for_status()
                    tmp = target.with_suffix(".part")
                    with open(tmp, "wb") as f:
                        for chunk in dl.iter_content(1 << 20):
                            f.write(chunk)
                    tmp.rename(target)
            except Exception as e:  # noqa: BLE001
                warn(f"Stažení {v['id']} selhalo: {e}")
                continue
            credits[str(v["id"])] = {"url": v.get("url"), "author": v.get("user", {}).get("name"),
                                     "author_url": v.get("user", {}).get("url"), "query": query}
            got += 1
        write_json(credits_path, credits)
        return got

    # ------------------------------------------------------------ grafické karty (fallback)

    def brand_card(self, index: int, chapter: int) -> Path:
        """Abstraktní karta v barvách značky. Pohyb, zrno a střih jí dodá render."""
        self.cards_dir.mkdir(parents=True, exist_ok=True)
        variant = index % 3
        path = self.cards_dir / f"card-{chapter}-{variant}.png"
        if path.exists():
            return path
        W, H = self.cfg["video"]["width"], self.cfg["video"]["height"]
        palettes = [((20, 33, 61), (36, 51, 90), (251, 103, 32)),
                    ((36, 51, 90), (20, 33, 61), (46, 196, 182)),
                    ((14, 22, 42), (20, 33, 61), (251, 103, 32))]
        top, bottom, accent = palettes[variant]
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        for y in range(H):
            f = y / H
            d.line([(0, y), (W, y)], fill=tuple(int(top[i] * (1 - f) + bottom[i] * f) for i in range(3)))
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        try:
            big = ImageFont.truetype(str(resolve(self.cfg["captions"]["font"])), int(H * 0.55))
        except OSError:
            big = ImageFont.load_default(int(H * 0.55))
        glyph = ["5", f"0{chapter}", "23:55"][variant]
        if variant == 2:
            big = big.font_variant(size=int(W * 0.34))
        bx = ld.textbbox((0, 0), glyph, font=big)
        gx = [W * 0.38, W * 0.05, (W - (bx[2] - bx[0])) / 2][variant]
        gy = [H * 0.12, H * 0.22, H * 0.30][variant]
        ld.text((gx, gy), glyph, font=big, fill=accent + (38,))
        img = Image.alpha_composite(img.convert("RGBA"), layer.filter(ImageFilter.GaussianBlur(2))).convert("RGB")
        img.save(path)
        return path

    def cover_card(self) -> Path:
        """Obálka e-booku nakloněná na tmavém pozadí – produktový záběr pro CTA."""
        self.cards_dir.mkdir(parents=True, exist_ok=True)
        path = self.cards_dir / "cover-card.png"
        cover = PATHS["assets"] / "cover.png"
        if path.exists() and path.stat().st_mtime >= cover.stat().st_mtime:
            return path
        W, H = self.cfg["video"]["width"], self.cfg["video"]["height"]
        bg = Image.open(cover).convert("RGB").resize((W, H)).filter(ImageFilter.GaussianBlur(40))
        bg = Image.blend(bg, Image.new("RGB", (W, H), (14, 22, 42)), 0.45)
        c = Image.open(cover).convert("RGBA")
        cw = int(W * 0.58)
        c = c.resize((cw, int(c.height * cw / c.width)), Image.LANCZOS)
        shadow = Image.new("RGBA", (c.width + 120, c.height + 120), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rectangle([60, 80, 60 + c.width, 80 + c.height], fill=(0, 0, 0, 170))
        shadow = shadow.filter(ImageFilter.GaussianBlur(30))
        shadow.alpha_composite(c, (60, 60))
        shadow = shadow.rotate(-4, resample=Image.BICUBIC, expand=True)
        bg = bg.convert("RGBA")
        bg.alpha_composite(shadow, ((W - shadow.width) // 2, int(H * 0.43 - shadow.height / 2)))
        bg.convert("RGB").save(path)
        return path


def prefetch(cfg: dict, tags: list[str] | None, per_tag: int) -> None:
    lib = BrollLibrary(cfg, random.Random(0))
    if not lib.key:
        raise SystemExit("Nastav PEXELS_API_KEY (klíč je zdarma na https://www.pexels.com/api/).")
    for tag in tags or list(BROLL_TAGS):
        n = lib.fetch_tag(tag, per_tag)
        log(f"{tag}: +{n} klipů")
