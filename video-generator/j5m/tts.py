"""Lokální text-to-speech. Žádné API, žádné klíče – všechno běží na tvém CPU/GPU.

Backendy:
  xtts   Coqui XTTS-v2 (balíček `coqui-tts`). Nejpřirozenější čeština, umí
         naklonovat hlas z krátké nahrávky (audio/voices/*.wav).
         POZOR: licence modelu je Coqui Public Model License = jen NEkomerční
         použití. Viz README, sekce „Licence hlasu“.
  piper  Piper (balíček `piper-tts`), český hlas cs_CZ-jirka-medium.
         Rychlý i na slabém CPU, licence MIT. Méně přirozený než XTTS.
  dummy  Ticho odhadnuté délky – jen pro test střihu bez modelů.

Kokoro-82M tu záměrně není: češtinu nepodporuje (umí EN, ES, FR, HI, IT, JA, PT, ZH).
"""

from __future__ import annotations

import os
import wave
from pathlib import Path

import numpy as np

from .config import PATHS
from .markup import estimate_seconds, spoken_text
from .utils import load_audio, log, save_wav, short_hash, trim_silence, warn, write_json

PIPER_BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main"


class TTSBackend:
    name = "base"
    sample_rate = 24000

    def synth(self, text: str) -> np.ndarray:  # float32 mono
        raise NotImplementedError

    def cache_key(self) -> str:
        return self.name


# ---------------------------------------------------------------- XTTS-v2


class XTTSBackend(TTSBackend):
    name = "xtts"

    def __init__(self, cfg: dict):
        if os.environ.get("COQUI_TOS_AGREED") != "1":
            raise SystemExit(
                "XTTS-v2 je pod licencí Coqui Public Model License (jen nekomerční použití).\n"
                "Přečti si ji: https://coqui.ai/cpml.txt — pokud souhlasíš, nastav COQUI_TOS_AGREED=1.\n"
                "Pro komerční videa použij raději --tts piper (MIT). Viz README → Licence hlasu."
            )
        try:
            import torch
            from TTS.api import TTS
        except ImportError as e:
            raise SystemExit(f"Chybí balíček coqui-tts / torch ({e}). Spusť: pip install -r requirements.txt")

        x = cfg["tts"]["xtts"]
        self.language = cfg["tts"]["language"]
        self.speed = float(x["speed"])
        self.temperature = float(x["temperature"])
        self.seed = int(x["seed"])
        self.torch = torch
        device = "cuda" if torch.cuda.is_available() else ("mps" if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available() else "cpu")
        log(f"Načítám XTTS-v2 na {device} (poprvé se stáhne ~1,8 GB)…")
        self.tts = TTS(x["model"]).to(device)
        self.sample_rate = int(self.tts.synthesizer.output_sample_rate)

        refs = sorted(p for p in PATHS["voices"].glob("*") if p.suffix.lower() in {".wav", ".mp3", ".flac", ".m4a", ".ogg"})
        self.speaker_wav = [str(p) for p in self._prepare_refs(refs)] or None
        self.speaker = None if self.speaker_wav else x["speaker"]
        if self.speaker_wav:
            log(f"Klonuju hlas z {len(refs)} nahrávek v audio/voices/")
        else:
            warn(f"V audio/voices/ není žádná nahrávka – používám vestavěný hlas „{self.speaker}“ "
                 "(česky zní s cizím přízvukem; nahraj vlastní hlas, viz README).")
        self._key = short_hash(x["model"], str(self.speaker_wav or self.speaker), str(self.speed), str(self.temperature), str(self.seed))

    @staticmethod
    def _prepare_refs(refs: list[Path]) -> list[Path]:
        """Nahrávky z mobilu (m4a, mp3, stereo…) → mono WAV 22 kHz, který XTTS načte bez potíží."""
        from .utils import ffmpeg

        out_dir = PATHS["models"] / "xtts_refs"
        out_dir.mkdir(parents=True, exist_ok=True)
        out = []
        for p in refs:
            target = out_dir / f"{p.stem}-{short_hash(p.name, str(p.stat().st_mtime), n=6)}.wav"
            if not target.exists():
                ffmpeg("-i", str(p), "-ac", "1", "-ar", "22050", "-af", "highpass=f=60,loudnorm=I=-20", str(target))
            out.append(target)
        return out

    def synth(self, text: str) -> np.ndarray:
        self.torch.manual_seed(self.seed)
        wav = self.tts.tts(
            text=text, language=self.language, speaker_wav=self.speaker_wav, speaker=self.speaker,
            speed=self.speed, temperature=self.temperature, split_sentences=True,
        )
        return np.asarray(wav, dtype=np.float32)

    def cache_key(self) -> str:
        return f"xtts-{self._key}"


# ---------------------------------------------------------------- Piper


def ensure_piper_voice(voice: str) -> Path:
    """Stáhne hlas Piperu (onnx + json) do models/piper/, pokud tam ještě není."""
    import requests

    folder = PATHS["models"] / "piper"
    folder.mkdir(parents=True, exist_ok=True)
    onnx = folder / f"{voice}.onnx"
    lang, name, quality = voice.split("-", 2)
    family = lang.split("_")[0]
    for fname in (f"{voice}.onnx", f"{voice}.onnx.json"):
        target = folder / fname
        if target.exists() and target.stat().st_size > 0:
            continue
        url = f"{PIPER_BASE}/{family}/{lang}/{name}/{quality}/{fname}"
        log(f"Stahuju {fname} …")
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            tmp = target.with_suffix(target.suffix + ".part")
            with open(tmp, "wb") as f:
                for chunk in r.iter_content(1 << 20):
                    f.write(chunk)
            tmp.rename(target)
    return onnx


class PiperBackend(TTSBackend):
    name = "piper"

    def __init__(self, cfg: dict):
        try:
            from piper import PiperVoice
        except ImportError:
            raise SystemExit("Chybí balíček piper-tts. Spusť: pip install piper-tts")
        p = cfg["tts"]["piper"]
        model = ensure_piper_voice(p["voice"])
        self.voice = PiperVoice.load(str(model))
        self.sample_rate = int(self.voice.config.sample_rate)
        self.params = dict(length_scale=p["length_scale"], noise_scale=p["noise_scale"], noise_w_scale=p["noise_w"])
        self._key = short_hash(p["voice"], str(sorted(self.params.items())))

    def synth(self, text: str) -> np.ndarray:
        import io

        from piper import SynthesisConfig

        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            self.voice.synthesize_wav(text, w, syn_config=SynthesisConfig(**self.params))
        buf.seek(0)
        with wave.open(buf, "rb") as r:
            pcm = np.frombuffer(r.readframes(r.getnframes()), dtype=np.int16)
        return pcm.astype(np.float32) / 32768.0

    def cache_key(self) -> str:
        return f"piper-{self._key}"


# ---------------------------------------------------------------- Dummy


class DummyBackend(TTSBackend):
    name = "dummy"
    sample_rate = 24000

    def synth(self, text: str) -> np.ndarray:
        n = int(estimate_seconds(text) * self.sample_rate)
        return np.zeros(max(n, self.sample_rate // 2), dtype=np.float32)


def make_backend(name: str, cfg: dict) -> TTSBackend:
    return {"xtts": XTTSBackend, "piper": PiperBackend, "dummy": lambda c: DummyBackend()}[name](cfg)


# ---------------------------------------------------------------- celý skript


def prepare_text(text: str) -> str:
    """Mluvená verze věty + drobné úpravy, aby TTS nečetl nesmysly."""
    t = spoken_text(text)
    t = t.replace("–", ",").replace(" - ", ", ")
    return " ".join(t.split())


def synthesize_script(script: dict, backend: TTSBackend, cfg: dict, out_dir: Path) -> dict:
    """Namluví každý beat zvlášť, ořízne ticho a poskládá voice.wav s časy beatů.

    Vrací timings: {"sample_rate", "duration", "beats": [{"start","end","file","text"}]}.
    Beaty se cachují podle textu a nastavení hlasu – změníš jednu větu, přegeneruje se jen ta.
    """
    sr = int(cfg["audio"]["sample_rate"])
    gap = float(cfg["tts"]["gap"])
    out_dir.mkdir(parents=True, exist_ok=True)
    key = backend.cache_key()

    pieces, beats_meta, t = [], [], 0.0
    for i, beat in enumerate(script["beats"]):
        text = prepare_text(beat["text"])
        f = out_dir / f"beat{i:02d}-{short_hash(key, text, n=8)}.wav"
        if not f.exists():
            log(f"[{backend.name}] {i + 1}/{len(script['beats'])}: {text}")
            raw = backend.synth(text)
            raw = trim_silence(raw, backend.sample_rate) if backend.name != "dummy" else raw
            save_wav(f, raw, backend.sample_rate)
        audio = load_audio(f, sr)
        start = t
        pieces.append(audio)
        t += len(audio) / sr
        beats_meta.append({"index": i, "start": round(start, 4), "end": round(t, 4), "file": f.name, "text": beat["text"]})
        pause = gap * (1.6 if beat.get("role") in ("hook", "punch") else 1.0)
        if i < len(script["beats"]) - 1:
            pieces.append(np.zeros(int(pause * sr), dtype=np.float32))
            t += pause

    voice = np.concatenate(pieces) if pieces else np.zeros(sr, dtype=np.float32)
    peak = float(np.max(np.abs(voice))) or 1.0
    voice = voice * (0.89 / peak) if peak > 0.89 else voice
    save_wav(out_dir / "voice.wav", voice, sr)
    timings = {"backend": key, "sample_rate": sr, "duration": round(len(voice) / sr, 4), "beats": beats_meta}
    write_json(out_dir / "timings.json", timings)
    # úklid starých verzí beatů
    keep = {b["file"] for b in beats_meta}
    for old in out_dir.glob("beat*.wav"):
        if old.name not in keep:
            old.unlink()
    return timings
