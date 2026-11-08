"""Režim „motion“: animované explainer video ve stylu rozborů.

Celé video se kreslí přes PIL snímek po snímku, bez stock záběrů:

  ┌───────────────────────────────┐
  │                   [5 Ještě 5 minut]  ← značka vpravo nahoře
  │ Text scény naskakuje slovo     │  ← to, co zrovna zaznívá; akcentová slova
  │ po slově, *akcent* kurzívou    │    oranžovou kurzívou, další 2 slova šedě
  │      ┌──────────────┐ [nálepka]│
  │  (1) │  UI karta     │         │  ← plán, mobil, budík, časovač, dokument…
  │      └──────────────┘ [DOBŘE ✓]│    + číslo chyby, kroužky, razítko
  │ // poznámka mono písmem        │
  │                       maskot   │  ← volitelně assets/mascot/<nálada>.png
  └───────────────────────────────┘

Scéna = jedna věta voiceoveru. Struktura skriptu viz styles/rozbor.md.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .captions import ease_out_back
from .config import PATHS, resolve
from .markup import parse

# ---------------------------------------------------------------- barvy a písma

INK = (20, 33, 61)
CORAL = (251, 103, 32)
PAPER = (243, 239, 232)
WHITE = (255, 255, 255)
GREEN = (34, 154, 92)
RED = (226, 61, 45)

THEMES = {
    "paper": {"bg": PAPER, "text": INK, "faded": (178, 172, 163), "accent": CORAL, "card": INK,
              "card_text": WHITE, "card_muted": (150, 162, 190), "note": (128, 122, 113), "dot": (214, 207, 196)},
    "dark": {"bg": (14, 20, 37), "text": WHITE, "faded": (88, 99, 128), "accent": CORAL, "card": (33, 47, 84),
             "card_text": WHITE, "card_muted": (140, 152, 182), "note": (128, 140, 168), "dot": (36, 46, 72)},
    "coral": {"bg": CORAL, "text": WHITE, "faded": (255, 196, 160), "accent": INK, "card": INK,
              "card_text": WHITE, "card_muted": (150, 162, 190), "note": (255, 226, 205), "dot": (255, 128, 64)},
}

FONT_FILES = {
    "head": "assets/fonts/InterDisplay-SemiBold.otf",
    "accent": "assets/fonts/InstrumentSerif-Italic.ttf",
    "bold": "assets/fonts/Inter-ExtraBold.otf",
    "black": "assets/fonts/Inter-Black.otf",
    "mono": "assets/fonts/JetBrainsMono-Regular.ttf",
    "monob": "assets/fonts/JetBrainsMono-Bold.ttf",
}


@lru_cache(maxsize=64)
def F(kind: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(resolve(FONT_FILES[kind])), size)
    except OSError:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)


def tw(text: str, font) -> int:
    return int(ImageDraw.Draw(Image.new("L", (1, 1))).textlength(text, font=font))


def wrap(text: str, font, max_w: int) -> list[str]:
    lines, cur = [], ""
    for w in text.split():
        trial = f"{cur} {w}".strip()
        if cur and tw(trial, font) > max_w:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines or [""]


def ease_out(x: float) -> float:
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def shadowed(img: Image.Image, radius: int = 18, offset: int = 14, alpha: int = 90) -> Image.Image:
    pad = radius * 2 + offset
    out = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    mask = img.getchannel("A").point(lambda v: alpha if v > 0 else 0)
    sh.paste((0, 0, 0, 255), (pad, pad + offset), mask)
    out = Image.alpha_composite(out, sh.filter(ImageFilter.GaussianBlur(radius)))
    out.alpha_composite(img, (pad, pad))
    return out


def rounded(w: int, h: int, r: int, fill, outline=None, width: int = 0) -> Image.Image:
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=fill, outline=outline, width=width)
    return img


def pill(text: str, bg, fg, border=None, size: int = 38, font: str = "bold") -> Image.Image:
    f = F(font, size)
    px, py = int(size * 0.62), int(size * 0.34)
    asc, desc = f.getmetrics()
    w, h = tw(text, f) + 2 * px, asc + desc + 2 * py
    img = rounded(w, h, h // 2, bg, border, 4 if border else 0)
    ImageDraw.Draw(img).text((px, py), text, font=f, fill=fg)
    return img


# ---------------------------------------------------------------- karty (vizuály)


@dataclass
class Card:
    img: Image.Image                                     # statická podoba (RGBA, se stínem)
    anchors: list[tuple[int, int, int, int]] = field(default_factory=list)  # místa pro kroužky
    dyn: Callable[[float], Image.Image] | None = None    # animovaná podoba podle času ve scéně
    pad: int = 0                                         # okraj stínu kolem karty


def _finish(img: Image.Image, anchors=None, dyn=None) -> Card:
    """Přidá stín; kotvy i dynamické snímky posune o okraj stínu."""
    sh = shadowed(img)
    pad = (sh.width - img.width) // 2
    anchors = [(a + pad, b + pad, c + pad, d + pad) for a, b, c, d in (anchors or [])]
    wrapped = None
    if dyn:
        cache: dict = {}

        def wrapped(t: float, _dyn=dyn) -> Image.Image:
            frame, key = _dyn(t)
            if key not in cache:
                if len(cache) > 400:
                    cache.clear()
                cache[key] = shadowed(frame)
            return cache[key]
    return Card(sh, anchors, wrapped, pad)


def card_plan(p: dict, th: dict, dur: float) -> Card:
    rows = p.get("rows") or [["8:00", "Učit se"]]
    W, rh = 860, 96
    head = 96
    img = rounded(W, head + rh * len(rows) + 30, 34, th["card"])
    d = ImageDraw.Draw(img)
    d.text((40, 34), str(p.get("title", "Plán")).upper(), font=F("monob", 30), fill=CORAL)
    anchors = []
    for i, row in enumerate(rows):
        t_, task = (row + ["", ""])[:2] if isinstance(row, list) else ("", str(row))
        y = head + i * rh
        d.line([(40, y), (W - 40, y)], fill=th["card_muted"] + (90,), width=2)
        d.text((40, y + 26), str(t_), font=F("monob", 34), fill=th["card_muted"])
        task_f = F("head", 40)
        task = str(task)
        while tw(task, task_f) > W - 270 and len(task) > 4:
            task = task[:-2].rstrip() + "…"
        d.text((230, y + 22), task, font=task_f, fill=th["card_text"])
        anchors.append((222, y + 12, 236 + tw(task, task_f), y + rh - 12))
    return _finish(img, anchors)


def card_phone(p: dict, th: dict, dur: float) -> Card:
    notes = p.get("notifications") or [["Instagram", "3 nové zprávy"]]
    W, H = 640, 300 + 132 * len(notes)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bg = Image.new("RGBA", (W, H))
    g = ImageDraw.Draw(bg)
    for y in range(H):
        f = y / H
        g.line([(0, y), (W, y)], fill=(int(34 + 40 * f), int(40 + 20 * f), int(78 + 30 * f), 255))
    mask = rounded(W, H, 56, (255, 255, 255, 255)).getchannel("A")
    img.paste(bg, (0, 0), mask)
    d = ImageDraw.Draw(img)
    time_s = str(p.get("time", "23:55"))
    f = F("head", 150)
    d.text(((W - tw(time_s, f)) / 2, 40), time_s, font=f, fill=WHITE)
    date = str(p.get("date", "neděle 14. ledna"))
    d.text(((W - tw(date, F("head", 30))) / 2, 214), date, font=F("head", 30), fill=(210, 215, 235))
    anchors = []
    for i, n in enumerate(notes):
        app, text = (list(n) + ["", ""])[:2] if isinstance(n, (list, tuple)) else ("Zpráva", str(n))
        y = 280 + i * 132
        card = rounded(W - 48, 118, 28, (255, 255, 255, 228))
        cd = ImageDraw.Draw(card)
        cd.rounded_rectangle([20, 22, 64, 66], radius=12, fill=CORAL)
        cd.text((80, 18), str(app), font=F("bold", 28), fill=INK)
        cd.text(((W - 48) - 110, 22), "teď", font=F("head", 24), fill=(120, 120, 130))
        line = str(text)
        while tw(line, F("head", 30)) > W - 150 and len(line) > 4:
            line = line[:-2].rstrip() + "…"
        cd.text((80, 60), line, font=F("head", 30), fill=(40, 40, 52))
        img.alpha_composite(card, (24, y))
        anchors.append((24, y, W - 24, y + 118))
    return _finish(img, anchors)


def card_alarm(p: dict, th: dict, dur: float) -> Card:
    W, H = 820, 600
    img = rounded(W, H, 44, th["card"])
    d = ImageDraw.Draw(img)
    label = str(p.get("label", "Budík"))
    d.text((48, 44), label, font=F("mono", 30), fill=th["card_muted"])
    t_ = str(p.get("time", "23:55"))
    f = F("head", 220)
    d.text(((W - tw(t_, f)) / 2, 92), t_, font=f, fill=th["card_text"])
    btn = str(p.get("button", "Odložit"))
    bw, bh = 560, 120
    bx, by = (W - bw) // 2, 380
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=60, fill=CORAL)
    bf = F("bold", 52)
    d.text(((W - tw(btn, bf)) / 2, by + 28), btn, font=bf, fill=WHITE)
    stop = "Zastavit"
    d.text(((W - tw(stop, F("head", 30))) / 2, by + bh + 22), stop, font=F("head", 30), fill=th["card_muted"])
    return _finish(img, [(bx, by, bx + bw, by + bh)])


def card_screentime(p: dict, th: dict, dur: float) -> Card:
    apps = p.get("apps") or [["TikTok", 140], ["Instagram", 90], ["YouTube", 60]]
    W, rh = 860, 104
    H = 220 + rh * len(apps)
    img = rounded(W, H, 36, th["card"])
    d = ImageDraw.Draw(img)
    d.text((44, 38), "ČAS U OBRAZOVKY · DNES", font=F("monob", 28), fill=CORAL)
    d.text((44, 84), str(p.get("total", "6 h 12 min")), font=F("head", 84), fill=th["card_text"])
    mx = max(float(a[1]) for a in apps) or 1
    anchors = []
    for i, (name, mins) in enumerate(apps):
        y = 210 + i * rh
        d.text((44, y), str(name), font=F("head", 34), fill=th["card_text"])
        mins = float(mins)
        lbl = f"{int(mins // 60)} h {int(mins % 60)} min" if mins >= 60 else f"{int(mins)} min"
        d.text((W - 44 - tw(lbl, F("mono", 30)), y + 4), lbl, font=F("mono", 30), fill=th["card_muted"])
        bw = int((W - 88) * mins / mx)
        d.rounded_rectangle([44, y + 50, 44 + max(bw, 24), y + 74], radius=12, fill=CORAL if i == 0 else th["card_muted"])
        anchors.append((36, y - 6, W - 36, y + 82))
    return _finish(img, anchors)


def _rows_card(p: dict, th: dict, dur: float, numbered: bool) -> Card:
    items = [str(x) for x in (p.get("items") or ["Krok"])][:6]
    title = p.get("title")
    W, rh = 860, 100
    top = 100 if title else 36
    H = top + rh * len(items) + 24
    base = rounded(W, H, 34, (255, 255, 255, 255), INK, 5)
    bd = ImageDraw.Draw(base)
    if title:
        bd.text((44, 34), str(title).upper(), font=F("monob", 28), fill=CORAL)
    done = {int(i) for i in (p.get("done") or []) if str(i).lstrip("-").isdigit()}
    anchors, f = [], F("head", 40)
    for i, it in enumerate(items):
        y = top + i * rh
        while tw(it, f) > W - 200 and len(it) > 4:
            it = it[:-2].rstrip() + "…"
        anchors.append((110, y + 14, 130 + tw(it, f), y + rh - 14))

    def frame(t: float):
        shown = len(items) if not numbered else min(len(items), int(max(t - 0.15, 0) / 0.35) + 1)
        ticks = sum(1 for i in sorted(done) if t > 0.5 + 0.4 * sorted(done).index(i))
        img = base.copy()
        d = ImageDraw.Draw(img)
        for i, it in enumerate(items[:shown]):
            y = top + i * rh
            while tw(it, f) > W - 200 and len(it) > 4:
                it = it[:-2].rstrip() + "…"
            if numbered:
                d.ellipse([40, y + 20, 100, y + 80], fill=CORAL)
                n = str(i + 1)
                d.text((70 - tw(n, F("bold", 34)) / 2, y + 28), n, font=F("bold", 34), fill=WHITE)
            else:
                d.rounded_rectangle([44, y + 26, 92, y + 74], radius=10, outline=INK, width=5)
                if i in sorted(done)[:ticks]:
                    d.line([(54, y + 50), (66, y + 64), (86, y + 34)], fill=GREEN, width=8, joint="curve")
            d.text((124, y + 24), it, font=f, fill=INK)
        return img, (shown, ticks)

    return _finish(base, anchors, frame)


def card_checklist(p, th, dur):
    return _rows_card(p, th, dur, numbered=False)


def card_steps(p, th, dur):
    return _rows_card(p, th, dur, numbered=True)


def card_timer(p: dict, th: dict, dur: float) -> Card:
    S = 640
    minutes = float(p.get("minutes", 5))
    label = str(p.get("label", f"{int(minutes)} minut"))
    base = rounded(S, S + 90, 48, th["card"])

    def frame(t: float):
        q = round(t * 12) / 12
        img = base.copy()
        d = ImageDraw.Draw(img)
        box = [90, 70, S - 90, S - 110]
        d.ellipse(box, outline=th["card_muted"] + (80,), width=26)
        frac = 1 - min(q / max(dur, 0.1), 1) * 0.05
        d.arc(box, start=-90, end=-90 + 360 * frac, fill=CORAL, width=26)
        secs = int(minutes * 60 * frac)
        txt = f"{secs // 60}:{secs % 60:02d}"
        f = F("head", 130)
        d.text(((S - tw(txt, f)) / 2, (box[1] + box[3]) / 2 - 80), txt, font=f, fill=th["card_text"])
        lf = F("mono", 34)
        d.text(((S - tw(label, lf)) / 2, S - 30), label, font=lf, fill=th["card_muted"])
        return img, q

    return _finish(base, [], frame)


def card_doc(p: dict, th: dict, dur: float) -> Card:
    W, H = 720, 820
    title = str(p.get("title", "Bakalarka_final_v3.docx"))
    text = str(p.get("text", ""))
    base = rounded(W, H, 26, (255, 255, 255, 255), INK, 5)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([0, 0, W - 1, 84], radius=26, fill=(236, 232, 224), outline=INK, width=5)
    d.rectangle([5, 50, W - 6, 84], fill=(236, 232, 224))
    d.line([(0, 84), (W, 84)], fill=INK, width=5)
    d.text((36, 24), title, font=F("mono", 30), fill=INK)
    f = F("head", 38)
    lines = wrap(text, f, W - 120) if text else []

    def frame(t: float):
        chars = int(max(t - 0.3, 0) * 22)
        img = base.copy()
        dd = ImageDraw.Draw(img)
        y, left = 140, chars
        cx, cy = 60, 140
        for ln in lines:
            part = ln[:max(left, 0)]
            dd.text((60, y), part, font=f, fill=INK)
            if left > 0:
                cx, cy = 60 + tw(part, f), y
            left -= len(ln) + 1
            y += 58
        for k in range(6):
            yy = max(y, 140) + 30 + k * 58
            if yy < H - 60 and not lines:
                dd.rounded_rectangle([60, yy + 14, W - 60 - (k * 53) % 200, yy + 30], radius=8, fill=(236, 232, 224))
        if int(t * 2.2) % 2 == 0:
            dd.rectangle([cx + 4, cy + 2, cx + 9, cy + 50], fill=CORAL)
        return img, (chars, int(t * 2.2) % 2)

    return _finish(base, [], frame)


def card_stat(p: dict, th: dict, dur: float) -> Card:
    value, label = str(p.get("value", "54 %")), str(p.get("label", ""))
    f = F("head", 230)
    W = max(tw(value, f) + 120, 560)
    lf = F("head", 42)
    lines = wrap(label, lf, W - 80) if label else []
    H = 300 + 56 * len(lines)
    img = rounded(W, H, 40, th["card"])
    d = ImageDraw.Draw(img)
    d.text(((W - tw(value, f)) / 2, 10), value, font=f, fill=CORAL)
    for i, ln in enumerate(lines):
        d.text(((W - tw(ln, lf)) / 2, 270 + i * 56), ln, font=lf, fill=th["card_text"])
    return _finish(img, [(40, 30, W - 40, 270)])


def card_chat(p: dict, th: dict, dur: float) -> Card:
    W = 880
    text = str(p.get("text", "tady je můj plán, rozeberte ho!"))
    name = str(p.get("name", "ty · právě teď"))
    f = F("head", 42)
    lines = wrap(text, f, W - 200)
    H = 120 + 56 * len(lines)
    base = rounded(W, H, 34, (255, 255, 255, 255), INK, 5)
    d = ImageDraw.Draw(base)
    d.ellipse([34, 34, 114, 114], fill=(255, 226, 205), outline=CORAL, width=5)
    d.text((140, 34), name, font=F("mono", 28), fill=(130, 126, 120))

    def frame(t: float):
        chars = int(max(t - 0.25, 0) * 26)
        img = base.copy()
        dd = ImageDraw.Draw(img)
        left = chars
        for i, ln in enumerate(lines):
            dd.text((140, 78 + i * 56), ln[:max(left, 0)], font=f, fill=INK)
            left -= len(ln) + 1
        return img, min(chars, len(text) + 1)

    return _finish(base, [], frame)


def card_strike(p: dict, th: dict, dur: float) -> Card:
    old, new = str(p.get("old", "zítra")), str(p.get("new", "teď"))
    of, nf = F("head", 84), F("accent", 120)
    ol, nl = wrap(old, of, 860), wrap(new, nf, 860)
    W = max(max(tw(x, of) for x in ol), max(tw(x, nf) for x in nl)) + 120
    H = 60 + 96 * len(ol) + 70 + 120 * len(nl) + 40
    base = rounded(W, H, 40, (255, 255, 255, 255), INK, 5)

    def frame(t: float):
        q = round(t * 15) / 15
        img = base.copy()
        d = ImageDraw.Draw(img)
        y = 50
        sp = ease_out((q - 0.25) / 0.4)
        for ln in ol:
            x0 = (W - tw(ln, of)) / 2
            d.text((x0, y), ln, font=of, fill=(150, 146, 140))
            if sp > 0:
                d.line([(x0 - 10, y + 56), (x0 - 10 + (tw(ln, of) + 20) * sp, y + 50)], fill=CORAL, width=10)
            y += 96
        d.text((W / 2 - 20, y - 4), "↓", font=F("head", 60), fill=INK)
        y += 70
        if q > 0.6:
            for ln in nl:
                d.text(((W - tw(ln, nf)) / 2, y), ln, font=nf, fill=CORAL)
                y += 120
        return img, q if q < 1.2 else 1.2

    return _finish(base, [], frame)


def card_quote(p: dict, th: dict, dur: float) -> Card:
    text = str(p.get("text", ""))
    f = F("head", 60)
    lines = wrap(text, f, 760)
    W, H = 880, 200 + 76 * len(lines)
    img = rounded(W, H, 40, th["card"])
    d = ImageDraw.Draw(img)
    d.text((54, 0), "“", font=F("accent", 170), fill=CORAL)
    for i, ln in enumerate(lines):
        d.text((60, 140 + i * 76), ln, font=f, fill=th["card_text"])
    return _finish(img)


def card_cover(p: dict, th: dict, dur: float) -> Card:
    cover = Image.open(PATHS["assets"] / "cover.png").convert("RGBA")
    w = 560
    cover = cover.resize((w, int(cover.height * w / cover.width)), Image.LANCZOS)
    m = rounded(cover.width, cover.height, 18, (255, 255, 255, 255)).getchannel("A")
    out = Image.new("RGBA", cover.size, (0, 0, 0, 0))
    out.paste(cover, (0, 0), m)
    out = out.rotate(-4, resample=Image.BICUBIC, expand=True)
    return _finish(out, [(0, 0, out.width, out.height)])


def card_follow(p: dict, th: dict, dur: float) -> Card:
    W, H = 900, 520
    name = str(p.get("name", "Ještě 5 minut"))
    handle = str(p.get("handle", "@jeste5minut"))
    url = str(p.get("url", f"instagram.com/{handle.lstrip('@')}"))
    base = rounded(W, H, 34, (255, 255, 255, 255), INK, 6)
    d = ImageDraw.Draw(base)
    d.line([(0, 96), (W, 96)], fill=INK, width=5)
    for i in range(3):
        d.ellipse([34 + i * 34, 38, 56 + i * 34, 60], outline=INK, width=4)
    d.rounded_rectangle([150, 26, W - 40, 72], radius=23, outline=INK, width=4)
    d.rounded_rectangle([50, 140, 190, 280], radius=30, fill=CORAL)
    d.text((120 - tw("5", F("black", 110)) / 2, 142), "5", font=F("black", 110), fill=WHITE)
    d.text((220, 150), name, font=F("bold", 62), fill=INK)
    d.text((222, 232), handle, font=F("mono", 32), fill=(130, 126, 120))
    btn = (50, 340, 640, 460)
    bm = (680, 340, 800, 460)
    click_t = max(0.8, dur * 0.45)

    def frame(t: float):
        q = round(t * 15) / 15
        img = base.copy()
        dd = ImageDraw.Draw(img)
        chars = int(q * 30)
        dd.text((174, 32), url[:chars], font=F("mono", 28), fill=INK)
        followed = q >= click_t
        dd.rounded_rectangle(btn, radius=60, fill=INK if followed else CORAL)
        label = "Sleduješ ✓" if followed else "Sledovat"
        bf = F("bold", 54)
        dd.text(((btn[0] + btn[2]) / 2 - tw(label, bf) / 2, btn[1] + 28), label, font=bf, fill=WHITE)
        saved = q >= click_t + 0.6
        dd.rounded_rectangle(bm, radius=20, fill=(255, 196, 0) if saved else WHITE, outline=INK, width=5)
        cx = (bm[0] + bm[2]) // 2
        dd.polygon([(cx - 22, 372), (cx + 22, 372), (cx + 22, 430), (cx, 410), (cx - 22, 430)],
                   fill=INK if saved else None, outline=INK, width=5)
        # kurzor: dojede na tlačítko, klikne, pak na záložku
        if q < click_t:
            k = ease_out(q / click_t)
            x, y = 860 + (420 - 860) * k, 500 + (410 - 500) * k
        else:
            k = ease_out((q - click_t) / 0.5)
            x, y = 420 + (760 - 420) * k, 410 + (420 - 410) * k
        pressed = abs(q - click_t) < 0.12 or abs(q - click_t - 0.6) < 0.12
        s = 0.85 if pressed else 1.0
        arrow = [(0, 0), (0, 58), (15, 45), (27, 70), (38, 65), (26, 41), (46, 41)]
        dd.polygon([(x + a * s, y + b * s) for a, b in arrow], fill=WHITE, outline=INK, width=4)
        return img, (q, followed, saved) if q < click_t + 1.2 else (99, True, True)

    return _finish(base, [btn], frame)


CARDS: dict[str, Callable[[dict, dict, float], Card]] = {
    "plan": card_plan, "phone": card_phone, "alarm": card_alarm, "screentime": card_screentime,
    "checklist": card_checklist, "steps": card_steps, "timer": card_timer, "doc": card_doc,
    "stat": card_stat, "chat": card_chat, "strike": card_strike, "quote": card_quote,
    "cover": card_cover, "follow": card_follow,
}


# ---------------------------------------------------------------- pozadí a ozdoby


@lru_cache(maxsize=8)
def background(kind: str, W: int, H: int) -> Image.Image:
    th = THEMES[kind]
    img = Image.new("RGB", (W, H), th["bg"])
    d = ImageDraw.Draw(img)
    if kind == "coral":
        cx, cy, n = W / 2, H * 0.56, 22
        R = H * 1.2
        for i in range(0, n, 2):
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                       (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=(255, 122, 52))
    else:
        if kind == "dark":
            glow = Image.new("L", (W, H), 0)
            ImageDraw.Draw(glow).ellipse([W * 0.1, H * 0.62, W * 0.9, H * 1.2], fill=120)
            glow = glow.filter(ImageFilter.GaussianBlur(160))
            img = Image.composite(Image.new("RGB", (W, H), (120, 52, 24)), img, glow)
            d = ImageDraw.Draw(img)
        step = int(W / 30)
        for y in range(step // 2, H, step):
            for x in range(step // 2, W, step):
                d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=th["dot"])
    return img


@lru_cache(maxsize=4)
def brand_pill(text: str) -> Image.Image:
    f = F("bold", 30)
    w, h = tw(text, f) + 96, 60
    img = rounded(w, h, 30, INK)
    d = ImageDraw.Draw(img)
    d.ellipse([10, 10, 50, 50], fill=CORAL)
    d.text((30 - tw("5", F("black", 30)) / 2, 11), "5", font=F("black", 30), fill=WHITE)
    d.text((64, 13), text, font=f, fill=WHITE)
    return img


def stamp_img(text: str, tone: str) -> Image.Image:
    color = GREEN if tone == "good" else RED
    f = F("black", 64)
    w, h = tw(text, f) + 70, 116
    img = rounded(w, h, 18, (255, 255, 255, 235), color, 8)
    ImageDraw.Draw(img).text((35, 18), text, font=f, fill=color)
    return img.rotate(-8, resample=Image.BICUBIC, expand=True)


def badge_img(n: int) -> Image.Image:
    S = 108
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, S - 1, S - 1], fill=WHITE)
    d.ellipse([7, 7, S - 8, S - 8], fill=CORAL)
    t = str(n)
    f = F("black", 56)
    d.text(((S - tw(t, f)) / 2, 16), t, font=f, fill=WHITE)
    return img


@lru_cache(maxsize=8)
def mascot(mood: str, height: int) -> Image.Image | None:
    folder = PATHS["assets"] / "mascot"
    files = sorted(folder.glob("*.png")) if folder.is_dir() else []
    if not files:
        return None
    pick = next((f for f in files if f.stem == mood), None) or next((f for f in files if f.stem == "wave"), files[0])
    img = Image.open(pick).convert("RGBA")
    return img.resize((int(img.width * height / img.height), height), Image.LANCZOS)


def scribble(d: ImageDraw.ImageDraw, box, progress: float, seed: int, color, width: int) -> None:
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = (x1 - x0) / 2 + 26, (y1 - y0) / 2 + 20
    n = 72
    steps = int(n * 1.12 * min(progress, 1.0))
    if steps < 2:
        return
    pts = []
    for i in range(steps):
        a = -2.6 + 2 * math.pi * i / n
        r = 1 + 0.035 * math.sin(i * 0.45 + seed) + 0.02 * (i / n)
        pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
    d.line(pts, fill=color, width=width, joint="curve")


# ---------------------------------------------------------------- renderer


@dataclass
class SceneRT:
    idx: int
    start: float
    end: float
    data: dict
    theme: dict
    words: list[dict]
    card: Card | None
    card_new: bool
    accent_times: list[float]


class MotionRenderer:
    def __init__(self, script: dict, timings: dict, words: list[dict], cfg: dict, total: float):
        self.W, self.H = cfg["video"]["width"], cfg["video"]["height"]
        self.k = self.W / 1080
        self.total = total
        self.brand = script.get("brand", "Ještě 5 minut")
        self.events: list[tuple[float, str]] = []    # pro zvukové efekty
        self.scenes: list[SceneRT] = []
        beats = timings["beats"]
        prev_card, prev_vis = None, None
        for i, (sc, tb) in enumerate(zip(script["beats"], beats)):
            start = 0.0 if i == 0 else tb["start"] - 0.06
            end = beats[i + 1]["start"] - 0.06 if i + 1 < len(beats) else total
            bg = sc.get("bg", "paper") if sc.get("bg") in THEMES else "paper"
            th = THEMES[bg]
            vis = sc.get("visual") or {"type": "same"}
            card_new = True
            if vis.get("type") == "same" and prev_vis is not None:
                card_new = False
                if bg != prev_vis[1]:
                    prev_card = CARDS[prev_vis[0]["type"]](prev_vis[0], th, end - start)
                card = prev_card
            elif vis.get("type") in CARDS:
                card = CARDS[vis["type"]](vis, th, end - start)
                prev_vis = (vis, bg)
            else:
                card = None
            prev_card = card
            sw = [w for w in words if w["beat"] == i]
            acc = [w["start"] for w in sw if w["key"]]
            self.scenes.append(SceneRT(i, start, end, sc, th, sw, card, card_new, acc))
            self.events.append((start, "whoosh"))
            if card_new and card:
                self.events.append((start + 0.05, "pop"))
            if sc.get("badge"):
                self.events.append((start + 0.18, "pop"))
            for j, _ in enumerate(sc.get("stickers") or []):
                self.events.append((self._sticker_t(self.scenes[-1], j), "pop"))
            if sc.get("stamp"):
                self.events.append((self._stamp_t(self.scenes[-1]), "thud"))
            if vis.get("type") == "follow":
                self.events.append((start + max(0.8, (end - start) * 0.45), "click"))
        self._head_cache: dict = {}

    # časy ozdob ve scéně
    @staticmethod
    def _sticker_t(s: SceneRT, j: int) -> float:
        base = s.accent_times[j] if j < len(s.accent_times) else s.start + 0.35 + 0.4 * j
        return min(base, s.end - 0.3)

    @staticmethod
    def _stamp_t(s: SceneRT) -> float:
        return min(s.start + (s.end - s.start) * 0.55, s.end - 0.35)

    @staticmethod
    def _mark_t(s: SceneRT) -> float:
        return s.accent_times[0] if s.accent_times else s.start + (s.end - s.start) * 0.4

    def _scene_at(self, t: float) -> SceneRT:
        for s in self.scenes:
            if s.start <= t < s.end:
                return s
        return self.scenes[-1]

    # -------------------------------------------------------- nadpis (karaoke)

    def _head_sprite(self, text: str, accent: bool, color, size: int) -> Image.Image:
        key = (text, accent, color, size)
        if key not in self._head_cache:
            f = F("accent", int(size * 1.16)) if accent else F("head", size)
            asc, desc = F("head", size).getmetrics()
            w = tw(text, f) + 8
            img = Image.new("RGBA", (w, int((asc + desc) * 1.25)), (0, 0, 0, 0))
            dy = int(asc - f.getmetrics()[0]) if accent else 0
            ImageDraw.Draw(img).text((0, dy + 4), text, font=f, fill=color)
            self._head_cache[key] = img
        return self._head_cache[key]

    def _draw_headline(self, frame: Image.Image, s: SceneRT, t: float) -> int:
        if not s.words:
            return int(300 * self.k)
        th = s.theme
        size = int(66 * self.k)
        x0, y = int(64 * self.k), int(286 * self.k)
        max_w = self.W - 2 * x0
        while size > 44:
            lines = self._layout_head(s.words, size, max_w)
            if len(lines) <= 3:
                break
            size -= 4
        spoken = sum(1 for w in s.words if w["start"] <= t + 0.03)
        lh = int(size * 1.16)
        n = 0
        for li, line in enumerate(lines):
            x = x0
            for w in line:
                if n < spoken:
                    color = th["accent"] if w["key"] else th["text"]
                elif n < spoken + 2:
                    color = th["faded"]
                else:
                    color = None
                if color:
                    sp = self._head_sprite(w.get("full") or w["show"], w["key"], color, size)
                    frame.paste(sp, (int(x), y + li * lh - 4), sp)
                x += self._word_w(w, size) + size * 0.26
                n += 1
        return y + len(lines) * lh

    def _word_w(self, w: dict, size: int) -> int:
        f = F("accent", int(size * 1.16)) if w["key"] else F("head", size)
        return tw(w.get("full") or w["show"], f)

    def _layout_head(self, words: list[dict], size: int, max_w: int) -> list[list[dict]]:
        lines, cur, cw = [[]], 0.0, 0.0
        for w in words:
            ww = self._word_w(w, size)
            add = ww + (size * 0.26 if lines[-1] else 0)
            if lines[-1] and cw + add > max_w:
                lines.append([])
                cw, add = 0.0, ww
            lines[-1].append(w)
            cw += add
        return lines

    # -------------------------------------------------------- snímek

    def frame(self, t: float) -> np.ndarray:
        s = self._scene_at(t)
        lt = t - s.start
        frame = background(s.data.get("bg", "paper") if s.data.get("bg") in THEMES else "paper", self.W, self.H).copy()
        k = self.k

        pill_img = brand_pill(self.brand)
        frame.paste(pill_img, (self.W - pill_img.width - int(48 * k), int(196 * k)), pill_img)

        head_bottom = self._draw_headline(frame, s, t)

        has_mascot = mascot("wave", int(self.H * 0.34)) is not None
        card_box = None
        if s.card:
            card = s.card
            src = card.dyn(t - self._card_birth(s)) if card.dyn else card.img
            avail_top = max(head_bottom + int(40 * k), int(self.H * 0.27))
            avail_h = int(self.H * (0.64 if has_mascot else 0.76)) - avail_top
            # bez maskota je dole víc místa → karta smí být větší
            fit = min(1.0 if has_mascot else 1.2, (self.W * 0.9) / src.width, avail_h / src.height)
            pop = ease_out_back((t - self._card_birth(s)) / 0.32) if s.card_new or s.idx == 0 else 1.0
            sc = fit * (0.86 + 0.14 * pop)
            img = src.resize((max(1, int(src.width * sc)), max(1, int(src.height * sc))), Image.BILINEAR) if sc != 1 else src
            cx = self.W * (0.47 if has_mascot else 0.5)
            cy = avail_top + avail_h / 2 + 6 * math.sin(t * 2.1)
            x0, y0 = int(cx - img.width / 2), int(cy - img.height / 2)
            frame.paste(img, (x0, y0), img)
            card_box = (x0, y0, x0 + img.width, y0 + img.height, sc)

            d = ImageDraw.Draw(frame)
            marks = [m for m in (s.data.get("mark") or []) if isinstance(m, int) and 0 <= m < len(card.anchors)]
            mt = self._mark_t(s)
            for mi, m in enumerate(marks):
                prog = (t - mt - 0.15 * mi) / 0.4
                if prog > 0:
                    a = card.anchors[m]
                    box = (x0 + a[0] * sc, y0 + a[1] * sc, x0 + a[2] * sc, y0 + a[3] * sc)
                    scribble(d, box, prog, m + s.idx, RED if s.data.get("bg") != "coral" else WHITE, int(9 * k))

        if card_box:
            x0, y0, x1, y1, _ = card_box
            if s.data.get("badge"):
                b = badge_img(int(s.data["badge"]))
                p = ease_out_back((lt - 0.18) / 0.25)
                if p > 0:
                    b2 = b.resize((max(1, int(b.width * k * p)), max(1, int(b.height * k * p))), Image.BILINEAR)
                    frame.paste(b2, (int(x0 + 10 * k - b2.width / 2), int(y0 + 20 * k - b2.height / 2)), b2)
            for j, text in enumerate((s.data.get("stickers") or [])[:2]):
                st = self._sticker_t(s, j)
                p = ease_out_back((t - st) / 0.25)
                if p <= 0:
                    continue
                coral = j % 2 == 0
                img = pill(str(text), CORAL if coral else WHITE, WHITE if coral else INK, None if coral else INK, int(40 * k))
                img = img.rotate(-3 if j % 2 == 0 else 2, resample=Image.BICUBIC, expand=True)
                img = img.resize((max(1, int(img.width * p)), max(1, int(img.height * p))), Image.BILINEAR)
                if j == 0:
                    px, py = min(x1 - img.width + 40 * k, self.W - img.width - 24 * k), y0 - img.height * 0.55
                else:
                    px, py = max(x0 - 20 * k, 24 * k), y1 - img.height * 0.35
                frame.paste(img, (int(px), int(py)), img)
            stamp = s.data.get("stamp")
            if stamp:
                stt = self._stamp_t(s)
                if t >= stt:
                    p = min((t - stt) / 0.16, 1.0)
                    img = stamp_img(str(stamp.get("text", "DOBŘE ✓")), stamp.get("tone", "good"))
                    scale = (1.7 - 0.7 * p) * k
                    img = img.resize((int(img.width * scale), int(img.height * scale)), Image.BILINEAR)
                    if p < 1:
                        img.putalpha(img.getchannel("A").point(lambda v, p=p: int(v * p)))
                    frame.paste(img, (int(min(x1 - img.width * 0.75, self.W - img.width - 20 * k)), int(y1 - img.height * 0.7)), img)

        note = s.data.get("note")
        if note:
            note = str(note) if str(note).startswith("//") else f"// {note}"
            chars = int(max(lt - 0.2, 0) * 40)
            ny = int((card_box[3] + 60 * k) if card_box else self.H * 0.66)
            ny = min(ny, int(self.H * 0.74))
            ImageDraw.Draw(frame).text((int(64 * k), ny), note[:chars], font=F("mono", int(30 * k)), fill=s.theme["note"])

        if has_mascot:
            m = mascot(str(s.data.get("mood", "wave")), int(self.H * 0.34))
            if m is not None:
                bob = 8 * k * math.sin(t * 2.4)
                p = ease_out_back(lt / 0.3) if (s.idx == 0 or s.data.get("mood") != self.scenes[s.idx - 1].data.get("mood")) else 1
                mm = m if p >= 0.999 else m.resize((max(1, int(m.width * (0.92 + 0.08 * p))), max(1, int(m.height * (0.92 + 0.08 * p)))), Image.BILINEAR)
                frame.paste(mm, (int(self.W - mm.width - 10 * k), int(self.H - mm.height + 30 * k + bob)), mm)

        return np.asarray(frame)

    def _card_birth(self, s: SceneRT) -> float:
        """Kdy se karta objevila (u „same“ karet = začátek první scény, kde vznikla)."""
        i = s.idx
        while i > 0 and not self.scenes[i].card_new:
            i -= 1
        return self.scenes[i].start


def render_frames(script: dict, timings: dict, words: list[dict], cfg: dict, total: float, out: Path) -> list[tuple[float, str]]:
    """Vyrenderuje němé video do `out` a vrátí seznam zvukových událostí."""
    from moviepy import VideoClip

    r = MotionRenderer(script, timings, words, cfg, total)
    v = cfg["video"]
    clip = VideoClip(frame_function=r.frame, duration=total)
    clip.write_videofile(str(out), fps=v["fps"], codec="libx264", audio=False, preset=v["preset"],
                         ffmpeg_params=["-crf", str(v["crf"]), "-pix_fmt", "yuv420p"], logger="bar")
    return r.events


def preview(script: dict, cfg: dict, times: list[float], out: Path) -> None:
    """Rychlý náhled bez hlasu: vybrané snímky vedle sebe do PNG (odhad časování)."""
    from .markup import estimate_seconds

    beats, t, words = [], 0.0, []
    for i, b in enumerate(script["beats"]):
        d = max(estimate_seconds(b["text"]), 1.0)
        beats.append({"index": i, "start": t, "end": t + d})
        units = parse(b["text"])
        for j, u in enumerate(units):
            words.append({"show": u.show, "full": u.full, "key": u.key, "start": t + d * j / max(len(units), 1), "end": t + d, "beat": i, "brk": False})
        t += d + 0.15
    r = MotionRenderer(script, {"beats": beats}, words, cfg, t)
    frames = [Image.fromarray(r.frame(x)).resize((360, 640)) for x in times]
    sheet = Image.new("RGB", (360 * len(frames), 640))
    for i, f in enumerate(frames):
        sheet.paste(f, (360 * i, 0))
    sheet.save(out)
