"""Pomocné funkce: ffmpeg, audio I/O, logování."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np


def log(msg: str) -> None:
    print(f"› {msg}", flush=True)


def warn(msg: str) -> None:
    print(f"! {msg}", file=sys.stderr, flush=True)


def require_ffmpeg() -> None:
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            raise SystemExit(f"Chybí {tool}. Nainstaluj ffmpeg (viz README) a zkus to znovu.")


def run(cmd: list[str], quiet: bool = True) -> None:
    res = subprocess.run(cmd, capture_output=quiet, text=True)
    if res.returncode != 0:
        tail = (res.stderr or "")[-2000:]
        raise RuntimeError(f"Příkaz selhal: {' '.join(cmd[:6])} …\n{tail}")


def ffmpeg(*args: str) -> None:
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args])


def probe_duration(path: Path | str) -> float:
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(json.loads(res.stdout)["format"]["duration"])
    except Exception:
        return 0.0


def load_audio(path: Path | str, sr: int) -> np.ndarray:
    """Libovolný audio soubor → mono float32 v daném sample rate (přes ffmpeg)."""
    res = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(sr), "-"],
        capture_output=True,
    )
    if res.returncode != 0:
        raise RuntimeError(f"Nejde načíst audio {path}: {res.stderr.decode()[-500:]}")
    return np.frombuffer(res.stdout, dtype=np.float32).copy()


def save_wav(path: Path | str, audio: np.ndarray, sr: int) -> None:
    audio = np.clip(audio, -1.0, 1.0)
    pcm = (audio * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def trim_silence(audio: np.ndarray, sr: int, threshold_db: float = -42.0, pad: float = 0.03) -> np.ndarray:
    """Ořízne ticho na začátku a konci (TTS ho tam často nechává)."""
    if audio.size == 0:
        return audio
    win = max(1, int(sr * 0.01))
    n = len(audio) // win
    if n == 0:
        return audio
    frames = audio[: n * win].reshape(n, win)
    rms = np.sqrt(np.mean(frames ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms + 1e-12)
    loud = np.where(db > threshold_db)[0]
    if loud.size == 0:
        return audio
    start = max(0, loud[0] * win - int(pad * sr))
    end = min(len(audio), (loud[-1] + 1) * win + int(pad * sr))
    return audio[start:end]


def short_hash(*parts: str, n: int = 10) -> str:
    h = hashlib.sha1("␟".join(parts).encode("utf-8")).hexdigest()
    return h[:n]


def read_json(path: Path | str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path | str, data) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def hex_to_rgb(color: str) -> tuple[int, int, int]:
    c = color.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
