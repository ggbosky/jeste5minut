"""Finální zvuk: hlas + jemné „swoosh“ efekty na střizích + volitelná hudba.

Hudba se automaticky ztlumí, když se mluví (sidechain ducking), a celé se to
znormalizuje na −14 LUFS (doporučená hlasitost pro TikTok, Reels i Shorts).
"""

from __future__ import annotations

import random
from pathlib import Path

import numpy as np

from .config import PATHS
from .utils import ffmpeg, save_wav

AUDIO_EXT = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"}


def _bandpass(x: np.ndarray, sr: int, lo: float, hi: float) -> np.ndarray:
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    spec[(freqs < lo) | (freqs > hi)] = 0
    return np.fft.irfft(spec, n=len(x)).astype(np.float32)


def _whoosh(sr: int, rng: np.random.Generator) -> np.ndarray:
    n = int(0.32 * sr)
    noise = rng.standard_normal(n).astype(np.float32)
    x = _bandpass(noise, sr, 400, 5000)
    t = np.linspace(0, 1, n, dtype=np.float32)
    env = np.where(t < 0.6, (t / 0.6) ** 2, ((1 - t) / 0.4) ** 1.5)
    x *= env
    return x / (np.max(np.abs(x)) + 1e-9)


def _tick(sr: int) -> np.ndarray:
    n = int(0.05 * sr)
    t = np.arange(n) / sr
    return (np.sin(2 * np.pi * 1600 * t) * np.exp(-t * 90)).astype(np.float32)


def build_sfx(cut_times: list[float], key_times: list[float], total: float, cfg: dict, path: Path) -> None:
    a = cfg["audio"]
    sr = int(a["sample_rate"])
    out = np.zeros(int(total * sr) + sr, dtype=np.float32)
    rng = np.random.default_rng(7)
    if a["whoosh"]:
        for t in cut_times:
            w = _whoosh(sr, rng) * float(a["whoosh_gain"])
            s = int((t - 0.2) * sr)
            if s < 0:
                w, s = w[-s:], 0
            out[s:s + len(w)] += w[: len(out) - s]
    if a["keyword_tick"]:
        tk = _tick(sr) * 0.08
        for t in key_times:
            s = int(t * sr)
            out[s:s + len(tk)] += tk[: len(out) - s]
    save_wav(path, out[: int(total * sr)], sr)


def pick_music(rng: random.Random) -> Path | None:
    folder = PATHS["music"]
    tracks = sorted(p for p in folder.glob("*") if p.suffix.lower() in AUDIO_EXT) if folder.is_dir() else []
    return rng.choice(tracks) if tracks else None


def mix(voice: Path, sfx: Path, music: Path | None, total: float, cfg: dict, out: Path) -> None:
    a = cfg["audio"]
    sr = str(a["sample_rate"])
    inputs = ["-i", str(voice), "-i", str(sfx)]
    voice_chain = (f"[0:a]aresample={sr},highpass=f=70,"
                   "acompressor=threshold=0.125:ratio=3:attack=5:release=90:makeup=1.5,"
                   f"apad=whole_dur={total:.3f}[v]")
    if music:
        inputs += ["-stream_loop", "-1", "-i", str(music)]
        fc = (f"{voice_chain};[v]asplit[v1][vsc];"
              f"[2:a]aresample={sr},aformat=channel_layouts=mono,volume={a['music_volume']},"
              f"atrim=0:{total:.3f},afade=t=out:st={max(total - 1.2, 0):.3f}:d=1.2[m0];"
              "[m0][vsc]sidechaincompress=threshold=0.04:ratio=6:attack=15:release=350[m];"
              "[v1][1:a][m]amix=inputs=3:normalize=0:duration=first,")
    else:
        fc = f"{voice_chain};[v][1:a]amix=inputs=2:normalize=0:duration=first,"
    fc += f"loudnorm=I={a['loudness']}:TP=-1.5:LRA=11,aresample={sr}[out]"
    ffmpeg(*inputs, "-filter_complex", fc, "-map", "[out]", "-t", f"{total:.3f}", "-ac", "2", "-ar", sr, str(out))
