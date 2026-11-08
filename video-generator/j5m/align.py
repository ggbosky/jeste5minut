"""Časování slov pro kinetické titulky.

Každý beat má přesný začátek a konec (víme ho ze syntézy). Uvnitř beatu:
  estimate  rozloží slova podle počtu slabik a interpunkce (rychlé, offline, bez modelu)
  whisper   faster-whisper (lokálně, open-source) přepíše audio beatu s časy slov
            a ty se namapují na slova skriptu → titulky sedí na milisekundy
  auto      whisper, když je nainstalovaný, jinak estimate
"""

from __future__ import annotations

import difflib
from pathlib import Path

from .config import PATHS
from .markup import Unit, normalize, parse, pause_weight, syllables
from .utils import load_audio, log, warn

_whisper_model = None


def _estimate(units: list[Unit], start: float, end: float) -> list[float]:
    weights = []
    for u in units:
        words = u.say_words
        w = sum(syllables(x) for x in words) + sum(pause_weight(x) for x in words[:-1])
        weights.append((max(w, 1.0), pause_weight(words[-1]) if words else 0.0))
    total = sum(w + p for w, p in weights[:-1]) + weights[-1][0] if weights else 1.0
    dur = max(end - start, 0.05)
    starts, acc = [], 0.0
    for w, p in weights:
        starts.append(start + dur * acc / total)
        acc += w + p
    return starts


def _load_whisper(size: str):
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel

        log(f"Načítám faster-whisper „{size}“ (poprvé se stáhne)…")
        _whisper_model = WhisperModel(size, device="auto", compute_type="int8",
                                      download_root=str(PATHS["models"] / "whisper"))
    return _whisper_model


def _whisper(units: list[Unit], wav: Path, start: float, end: float, size: str) -> list[float]:
    model = _load_whisper(size)
    script_words, owner = [], []
    for ui, u in enumerate(units):
        for w in u.say_words:
            script_words.append(normalize(w))
            owner.append(ui)
    audio = load_audio(wav, 16000)   # numpy místo cesty: nezávisí na verzi PyAV
    segments, _ = model.transcribe(audio, language="cs", word_timestamps=True, beam_size=5,
                                   initial_prompt=" ".join(u.say for u in units), vad_filter=False)
    heard = [(normalize(w.word), w.start) for seg in segments for w in (seg.words or [])]
    heard = [(w, t) for w, t in heard if w]

    word_t: list[float | None] = [None] * len(script_words)
    sm = difflib.SequenceMatcher(a=script_words, b=[w for w, _ in heard], autojunk=False)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            word_t[blk.a + k] = start + heard[blk.b + k][1]
    # přibližná shoda pro slova, která Whisper napsal jinak (skloňování, překlepy)
    for op, a0, a1, b0, b1 in sm.get_opcodes():
        if op == "replace" and (a1 - a0) == (b1 - b0):
            for k in range(a1 - a0):
                if difflib.SequenceMatcher(a=script_words[a0 + k], b=heard[b0 + k][0]).ratio() > 0.6:
                    word_t[a0 + k] = start + heard[b0 + k][1]

    est = _estimate(units, start, end)
    unit_t: list[float | None] = [None] * len(units)
    for wi, ui in enumerate(owner):
        if unit_t[ui] is None and word_t[wi] is not None:
            unit_t[ui] = word_t[wi]
    matched = sum(t is not None for t in unit_t)
    if matched < max(2, len(units) // 3):
        return est
    # díry doplň interpolací mezi známými body (tvar z odhadu)
    known = [(i, t) for i, t in enumerate(unit_t) if t is not None]
    out = []
    for i in range(len(units)):
        if unit_t[i] is not None:
            out.append(unit_t[i])
            continue
        prev = max((k for k in known if k[0] < i), default=None, key=lambda k: k[0])
        nxt = min((k for k in known if k[0] > i), default=None, key=lambda k: k[0])
        if prev and nxt:
            f = (est[i] - est[prev[0]]) / max(est[nxt[0]] - est[prev[0]], 1e-6)
            out.append(prev[1] + f * (nxt[1] - prev[1]))
        elif prev:
            out.append(prev[1] + (est[i] - est[prev[0]]))
        elif nxt:
            out.append(max(start, nxt[1] - (est[nxt[0]] - est[i])))
        else:
            out.append(est[i])
    # monotónnost
    for i in range(1, len(out)):
        out[i] = max(out[i], out[i - 1] + 0.04)
    return [min(t, end - 0.03) for t in out]


def align(script: dict, timings: dict, audio_dir: Path, method: str = "auto", whisper_size: str = "small") -> list[dict]:
    """Vrátí seznam slov: {"show","key","start","end","beat"} na časové ose videa."""
    use_whisper = method == "whisper"
    if method == "auto":
        try:
            import faster_whisper  # noqa: F401
            use_whisper = not timings["backend"].startswith("dummy")
        except ImportError:
            use_whisper = False

    words: list[dict] = []
    for beat, tb in zip(script["beats"], timings["beats"]):
        units = parse(beat["text"])
        if not units:
            continue
        starts = None
        if use_whisper:
            try:
                starts = _whisper(units, audio_dir / tb["file"], tb["start"], tb["end"], whisper_size)
            except Exception as e:  # noqa: BLE001
                warn(f"Whisper zarovnání selhalo ({e}), používám odhad.")
                use_whisper = False
        if starts is None:
            starts = _estimate(units, tb["start"], tb["end"])
        for k, (u, s) in enumerate(zip(units, starts)):
            e = starts[k + 1] if k + 1 < len(starts) else tb["end"]
            words.append({"show": u.show, "full": u.full or u.show, "key": u.key, "start": round(s, 3), "end": round(e, 3),
                          "beat": tb["index"], "brk": pause_weight(u.say_words[-1]) > 0})
    return words
