"""Kinetická typografie: titulky slovo po slově, vypálené do videa přes PIL.

Styl „pop“: slova naskakují přesně ve chvíli, kdy zazní (s lehkým
přestřelením velikosti jako v CapCutu), klíčová slova jsou větší a v barvě.
Styl „highlight“: celá „stránka“ titulku je vidět, aktivní slovo má barevný
rámeček.

Navíc:
  hook box    bílý štítek s nadpisem v prvních sekundách (jako TikTok text)
  CTA štítek  oranžový „sticker“ při závěrečné výzvě
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .config import resolve
from .utils import hex_to_rgb

INK = (20, 33, 61)


def ease_out_back(x: float) -> float:
    x = min(max(x, 0.0), 1.0)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def pop_scale(age: float, dur: float = 0.16, start: float = 0.6) -> float:
    return start + (1 - start) * ease_out_back(age / dur)


@lru_cache(maxsize=16)
def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(resolve(path)), size)
    except OSError:
        for fallback in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVuSans-Bold.ttf", "arialbd.ttf"):
            try:
                return ImageFont.truetype(fallback, size)
            except OSError:
                continue
        return ImageFont.load_default(size)


@dataclass
class WordSprite:
    img: Image.Image
    w: int            # šířka textu (bez okrajů pro stín)
    h: int
    ox: int           # posun textu uvnitř obrázku
    oy: int


@dataclass
class Page:
    words: list[int]
    start: float
    end: float
    layout: list[tuple[int, float, float]] = field(default_factory=list)  # (word idx, cx, cy)


class CaptionRenderer:
    def __init__(self, words: list[dict], cfg: dict, duration: float, hook_text: str | None,
                 cta_text: str | None, cta_start: float | None):
        self.c = cfg["captions"]
        self.W, self.H = cfg["video"]["width"], cfg["video"]["height"]
        self.k = self.W / 1080.0     # škálování pro jiná rozlišení
        self.words = words
        self.duration = duration
        self.size = int(self.c["font_size"] * self.k)
        self.key_size = int(self.size * self.c["keyword_scale"])
        self.color = hex_to_rgb(self.c["color"])
        self.key_color = hex_to_rgb(self.c["keyword_color"])
        self.stroke_color = hex_to_rgb(self.c["stroke_color"])
        self.stroke = int(self.c["stroke"] * self.k)
        self._sprites: dict = {}
        self.cta_start = cta_start
        self.pages = self._paginate()
        for p in self.pages:
            self._layout(p)

        self.hook_img = self._label(hook_text, (255, 255, 255), INK, 0.0) if (hook_text and self.c["hook_box"]) else None
        self.cta_img = self._label(cta_text, self.key_color, (255, 255, 255), -3.0) if (cta_text and self.c["cta_sticker"]) else None

    # ------------------------------------------------------------ stránky

    def _paginate(self) -> list[Page]:
        pages: list[Page] = []
        cur: list[int] = []
        chars = 0
        maxw, maxc = int(self.c["max_words"]), int(self.c["max_chars"])

        def close():
            nonlocal cur, chars
            if cur:
                pages.append(Page(words=cur, start=self.words[cur[0]]["start"], end=0.0))
            cur, chars = [], 0

        for i, w in enumerate(self.words):
            prev = self.words[i - 1] if i else None
            new_beat = prev is not None and prev["beat"] != w["beat"]
            punct = bool(prev and prev.get("brk"))
            # klíčové slovo dostane vlastní „úder“: nezačne v plné stránce
            key_break = w["key"] and not (prev and prev["key"]) and len(cur) >= 2
            if cur and (new_beat or punct or key_break or len(cur) >= maxw or chars + len(w["show"]) > maxc):
                close()
            cur.append(i)
            chars += len(w["show"]) + 1
        close()

        for n, p in enumerate(pages):
            last = self.words[p.words[-1]]
            nxt = pages[n + 1].start if n + 1 < len(pages) else self.duration
            p.end = min(nxt, last["end"] + 0.45)
        return pages

    # ------------------------------------------------------------ sprity

    def _sprite(self, text: str, size: int, color: tuple, stroke: bool = True) -> WordSprite:
        key = (text, size, color, stroke)
        if key in self._sprites:
            return self._sprites[key]
        font = _font(self.c["font"], size)
        sw = self.stroke if stroke else 0
        probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        x0, y0, x1, y1 = probe.textbbox((0, 0), text, font=font, stroke_width=sw)
        tw, th = x1 - x0, y1 - y0
        pad = int(24 * self.k)
        img = Image.new("RGBA", (tw + 2 * pad, th + 2 * pad), (0, 0, 0, 0))
        ox, oy = pad - x0, pad - y0
        if self.c["shadow"] and stroke:
            sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
            ImageDraw.Draw(sh).text((ox, oy + int(7 * self.k)), text, font=font, fill=(0, 0, 0, 150),
                                    stroke_width=sw, stroke_fill=(0, 0, 0, 150))
            img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(9 * self.k)))
        ImageDraw.Draw(img).text((ox, oy), text, font=font, fill=color + (255,),
                                 stroke_width=sw, stroke_fill=self.stroke_color + (255,))
        sp = WordSprite(img=img, w=tw, h=th, ox=pad, oy=pad)
        self._sprites[key] = sp
        return sp

    def _word_style(self, w: dict, active: bool = False) -> tuple[str, int, tuple]:
        text = w["show"].upper() if self.c["uppercase"] else w["show"]
        size = self.key_size if w["key"] else self.size
        color = self.key_color if w["key"] else self.color
        if self.c["style"] == "highlight" and active:
            color = (255, 255, 255)
        return text, size, color

    def _layout(self, page: Page) -> None:
        max_w = 0.80 * self.W
        space = 0.27 * self.size
        line_h = 1.08 * self.size
        lines: list[list[tuple[int, int]]] = [[]]
        cur_w = 0.0
        for wi in page.words:
            text, size, color = self._word_style(self.words[wi])
            sp = self._sprite(text, size, color)
            add = sp.w + (space if lines[-1] else 0)
            if lines[-1] and cur_w + add > max_w:
                lines.append([])
                cur_w, add = 0.0, sp.w
            lines[-1].append((wi, sp.w))
            cur_w += add
        total_h = line_h * len(lines)
        in_cta = self.cta_start is not None and page.start >= self.cta_start - 0.01
        y = self.c.get("cta_y", self.c["y"]) if in_cta else self.c["y"]
        cy0 = y * self.H - total_h / 2 + line_h / 2
        page.layout = []
        for li, line in enumerate(lines):
            lw = sum(w for _, w in line) + space * (len(line) - 1)
            x = (self.W - lw) / 2
            for wi, w in line:
                page.layout.append((wi, x + w / 2, cy0 + li * line_h))
                x += w + space

    def _label(self, text: str, bg: tuple, fg: tuple, angle: float) -> Image.Image:
        font = _font(self.c["hook_font"], int(56 * self.k))
        max_w = int(0.78 * self.W)
        probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        words, lines, cur = text.split(), [], ""
        for w in words:
            trial = f"{cur} {w}".strip()
            if probe.textlength(trial, font=font) > max_w and cur:
                lines.append(cur)
                cur = w
            else:
                cur = trial
        lines.append(cur)
        asc, desc = font.getmetrics()
        lh = int((asc + desc) * 1.05)
        tw = int(max(probe.textlength(l, font=font) for l in lines))
        px, py = int(34 * self.k), int(22 * self.k)
        box = Image.new("RGBA", (tw + 2 * px, lh * len(lines) + 2 * py), (0, 0, 0, 0))
        d = ImageDraw.Draw(box)
        d.rounded_rectangle([0, 0, box.width - 1, box.height - 1], radius=int(22 * self.k), fill=bg + (255,))
        for i, l in enumerate(lines):
            lw = probe.textlength(l, font=font)
            d.text(((box.width - lw) / 2, py + i * lh), l, font=font, fill=fg + (255,))
        pad = int(30 * self.k)
        canvas = Image.new("RGBA", (box.width + 2 * pad, box.height + 2 * pad), (0, 0, 0, 0))
        shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rounded_rectangle([pad, pad + 8, pad + box.width, pad + box.height + 8],
                                                 radius=int(22 * self.k), fill=(0, 0, 0, 110))
        canvas = Image.alpha_composite(canvas, shadow.filter(ImageFilter.GaussianBlur(12)))
        canvas.alpha_composite(box, (pad, pad))
        if angle:
            canvas = canvas.rotate(angle, resample=Image.BICUBIC, expand=True)
        return canvas

    # ------------------------------------------------------------ kreslení

    @staticmethod
    def _paste(frame: Image.Image, img: Image.Image, cx: float, cy: float, scale: float = 1.0, alpha: float = 1.0) -> None:
        if scale != 1.0:
            img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.BILINEAR)
        if alpha < 1.0:
            a = img.getchannel("A").point(lambda v: int(v * alpha))
            img = img.copy()
            img.putalpha(a)
        frame.paste(img, (int(cx - img.width / 2), int(cy - img.height / 2)), img)

    def _active_page(self, t: float) -> Page | None:
        for p in self.pages:
            if p.start <= t < p.end:
                return p
        return None

    def draw(self, frame_arr: np.ndarray, t: float) -> np.ndarray:
        frame = Image.fromarray(frame_arr)

        # hook box nahoře
        if self.hook_img is not None and t < self.c["hook_seconds"]:
            fade = min(1.0, (self.c["hook_seconds"] - t) / 0.25)
            self._paste(frame, self.hook_img, self.W / 2, 0.17 * self.H, pop_scale(t, 0.22, 0.7), fade)

        # CTA štítek
        if self.cta_img is not None and self.cta_start is not None and t >= self.cta_start:
            self._paste(frame, self.cta_img, self.W / 2, 0.15 * self.H, pop_scale(t - self.cta_start, 0.2, 0.5))

        page = self._active_page(t)
        if page is not None:
            style = self.c["style"]
            for wi, cx, cy in page.layout:
                w = self.words[wi]
                if style == "pop":
                    if t < w["start"]:
                        continue
                    age = t - w["start"]
                    scale = pop_scale(age, 0.15, 0.55 if w["key"] else 0.7)
                    lift = (1 - ease_out_back(age / 0.15)) * 16 * self.k
                    text, size, color = self._word_style(w)
                    sp = self._sprite(text, size, color)
                    self._paste(frame, sp.img, cx, cy + lift, scale)
                else:  # highlight
                    active = w["start"] <= t < w["end"]
                    text, size, color = self._word_style(w, active)
                    sp = self._sprite(text, size, color)
                    if active:
                        d = ImageDraw.Draw(frame)
                        px, py = 16 * self.k, 6 * self.k
                        d.rounded_rectangle([cx - sp.w / 2 - px, cy - sp.h / 2 - py, cx + sp.w / 2 + px, cy + sp.h / 2 + py],
                                            radius=int(14 * self.k), fill=self.key_color)
                    scale = pop_scale(t - w["start"], 0.12, 0.85) if active else 1.0
                    self._paste(frame, sp.img, cx, cy, scale)

        if self.c["progress_bar"]:
            d = ImageDraw.Draw(frame)
            d.rectangle([0, 0, int(self.W * t / max(self.duration, 0.01)), int(8 * self.k)], fill=self.key_color)

        return np.asarray(frame)
