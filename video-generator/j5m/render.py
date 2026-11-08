"""Video pipeline: skript → hlas → časy slov → jump cuty z B-rollu → titulky → mix → MP4.

Kroky:
  1. TTS namluví každý beat zvlášť (audio/<id>/)
  2. align spočítá čas každého slova
  3. plan_cuts rozseká časovou osu na střihy po 2–4 s (preferuje hranice vět)
  4. ffmpeg připraví každý střih: ořez na 9:16, punch-in, jemný „handheld“
     pohyb, barevný grade, zrno, vinětace  (video/work/<id>/)
  5. moviepy vypálí kinetické titulky snímek po snímku
  6. ffmpeg smíchá hlas + efekty + hudbu a uloží output/<id>.mp4
"""

from __future__ import annotations

import random
import shutil
from pathlib import Path

from . import align as align_mod
from . import audio_mix
from .broll import BrollLibrary, Source
from .captions import CaptionRenderer
from .config import PATHS
from .markup import strip_markup
from .tts import make_backend, synthesize_script
from .utils import ffmpeg, log, read_json, require_ffmpeg, write_json

GRADES = {
    "warm": "eq=contrast=1.06:saturation=1.06:gamma=0.98,colorbalance=rs=0.04:gs=0.01:bs=-0.04:rm=0.02:bm=-0.02",
    "neutral": "eq=contrast=1.04:saturation=1.03",
    "cold": "eq=contrast=1.06:saturation=0.96,colorbalance=rs=-0.02:bs=0.04:bm=0.02",
}


# ---------------------------------------------------------------- střihy


def plan_cuts(timings: dict, words: list[dict], script: dict, total: float, cfg: dict, rng: random.Random) -> list[dict]:
    v = cfg["video"]
    fps = v["fps"]
    lo, hi = float(v["min_cut"]), float(v["max_cut"])
    snap = lambda t: round(t * fps) / fps  # noqa: E731

    beat_starts = [b["start"] for b in timings["beats"][1:]]
    word_starts = [w["start"] for w in words]
    beats = timings["beats"]

    segments = [(0.0, total)]
    cta_from = None
    if v["cta_visual"] == "cover" and script["beats"][-1].get("role") == "cta" and len(beats) > 1:
        cta_from = snap(beats[-1]["start"] - 0.05)
        segments = [(0.0, cta_from), (cta_from, total)]

    cuts: list[dict] = []
    for a, b in segments:
        if a == cta_from:
            cuts.append({"start": a, "end": snap(b), "tags": ["cover"]})
            continue
        t = a
        while b - t > hi:
            target = t + rng.uniform(lo, hi)
            cands = [x for x in beat_starts + word_starts if t + lo <= x <= t + hi and b - x >= lo]
            if cands:
                x = min(cands, key=lambda c: abs(c - target) - (0.6 if c in beat_starts else 0.0))
            else:
                x = min(target, b - lo)
            x = snap(x - 0.04)        # střih těsně před slovem působí přirozeně
            if x <= t:
                x = snap(t + lo)
            cuts.append({"start": t, "end": x})
            t = x
        cuts.append({"start": t, "end": snap(b)})

    for c in cuts:
        if "tags" in c:
            continue
        mid = (c["start"] + c["end"]) / 2
        beat_i = next((i for i, bb in enumerate(beats) if bb["start"] <= mid <= bb["end"] + 0.3), len(beats) - 1)
        c["tags"] = script["beats"][beat_i].get("broll") or ["desk"]
    return cuts


def _post_chain(cfg: dict) -> str:
    v = cfg["video"]
    chain = [GRADES.get(v["grade"], GRADES["neutral"])]
    if v["grain"]:
        chain.append(f"noise=alls={int(v['grain'])}:allf=t")
    if v["vignette"]:
        chain.append("vignette=angle=PI/5")
    chain += ["setsar=1", "format=yuv420p"]
    return ",".join(chain)


def _even(x: float) -> int:
    return int(x) // 2 * 2


def render_cut(src: Source, offset: float, dur: float, zoom: float, idx: int, cfg: dict, out: Path, rng: random.Random) -> None:
    v = cfg["video"]
    W, H, fps = v["width"], v["height"], v["fps"]
    frames = max(1, round(dur * fps))
    enc = ["-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-r", str(fps), "-frames:v", str(frames)]
    post = _post_chain(cfg)

    if src.kind == "image":
        rate = rng.uniform(0.0006, 0.0011) * (30 / fps)
        vf = (f"scale={_even(W * 1.25)}:{_even(H * 1.25)}:force_original_aspect_ratio=increase,"
              f"crop={_even(W * 1.25)}:{_even(H * 1.25)},"
              f"zoompan=z='1+{rate:.5f}*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={fps},{post}")
        ffmpeg("-loop", "1", "-framerate", str(fps), "-i", str(src.path), "-vf", vf, *enc, str(out))
        return

    A = int(v["shake_px"] * W / 1080)
    z = max(zoom, 1.0 + 3 * A / W + 0.01)
    sw, sh = _even(W * z), _even(H * z)
    ph1, ph2 = rng.uniform(0, 6.28), rng.uniform(0, 6.28)
    vf = (f"fps={fps},scale={sw}:{sh}:force_original_aspect_ratio=increase:flags=bicubic,"
          f"crop={W}:{H}:x='(iw-ow)/2+{A}*sin(2*PI*t*0.71+{ph1:.2f})+{A / 2:.1f}*sin(2*PI*t*1.9)':"
          f"y='(ih-oh)/2+{A}*sin(2*PI*t*0.53+{ph2:.2f})',{post}")
    ffmpeg("-stream_loop", "-1", "-ss", f"{offset:.3f}", "-i", str(src.path), "-vf", vf, *enc, str(out))


def build_base(cuts: list[dict], cfg: dict, chapter: int, work: Path, rng: random.Random, allow_pexels: bool) -> list[str]:
    lib = BrollLibrary(cfg, rng, allow_pexels)
    punch = float(cfg["video"]["punch_in"])
    files, used = [], []
    prev: dict | None = None
    for i, c in enumerate(cuts):
        dur = c["end"] - c["start"]
        reuse = (prev is not None and prev["src"].kind == "video" and "cover" not in c["tags"]
                 and set(c["tags"]) & set(prev["tags"]) and rng.random() < 0.35
                 and prev["offset"] + prev["dur"] + dur < prev["src"].duration)
        if reuse:   # klasický jump cut: stejný záběr, pokračuje dál, ale přiblížený/oddálený
            src, offset = prev["src"], prev["offset"] + prev["dur"]
            zoom = 1.0 if prev["zoom"] > 1.05 else punch
        else:
            src = lib.pick(c["tags"], i, chapter)
            offset = rng.uniform(0, max(0.0, src.duration - dur - 0.2)) if src.kind == "video" else 0.0
            zoom = punch if (i % 2 == 1 and rng.random() < 0.7) else 1.0
        out = work / f"cut{i:03d}.mp4"
        render_cut(src, offset, dur, zoom, i, cfg, out, rng)
        files.append(out)
        used.append(str(src.path))
        prev = {"src": src, "offset": offset, "dur": dur, "zoom": zoom, "tags": c["tags"]}
        log(f"střih {i + 1}/{len(cuts)}  {dur:4.2f} s  {'/'.join(c['tags'])} ← {src.path.name}{' (jump cut)' if reuse else ''}")

    listing = work / "cuts.txt"
    listing.write_text("".join(f"file '{f.name}'\n" for f in files))
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(work / "base.mp4"))
    return used


# ---------------------------------------------------------------- hlavní funkce


def render(script_path: Path, cfg: dict, tts_name: str | None = None, align_method: str | None = None,
           allow_pexels: bool = True, keep: bool = False, out_path: Path | None = None) -> Path:
    from moviepy import VideoFileClip

    require_ffmpeg()
    script = read_json(script_path)
    sid = script["id"]
    rng = random.Random(sid)
    audio_dir = PATHS["audio"] / sid
    work = PATHS["video"] / "work" / sid
    work.mkdir(parents=True, exist_ok=True)
    PATHS["output"].mkdir(parents=True, exist_ok=True)
    out_path = out_path or PATHS["output"] / f"{sid}.mp4"

    # 1) hlas
    backend = make_backend(tts_name or cfg["tts"]["backend"], cfg)
    timings = synthesize_script(script, backend, cfg, audio_dir)
    total = timings["duration"] + float(cfg["video"]["tail"]) + (0.8 if script.get("mode") == "motion" else 0.0)
    log(f"Hlas hotový: {timings['duration']:.1f} s")

    # 2) časy slov
    words = align_mod.align(script, timings, audio_dir, align_method or cfg["align"]["method"], cfg["align"]["whisper_model"])
    write_json(audio_dir / "words.json", words)

    v = cfg["video"]
    silent = work / "captioned.mp4"
    sfx = audio_dir / "sfx.wav"
    used: list[str] = []
    if script.get("mode") == "motion":
        # 3–6) motion graphics: celé video se kreslí snímek po snímku
        from .motion import render_frames

        events = render_frames(script, timings, words, cfg, total, silent)
        audio_mix.build_sfx(events, total, cfg, sfx)
    else:
        # 3+4) střihy a B-roll
        cuts = plan_cuts(timings, words, script, total, cfg, rng)
        used = build_base(cuts, cfg, script["chapter"], work, rng, allow_pexels)
        audio_mix.build_sfx([(c["start"], "whoosh") for c in cuts[1:]] + [(w["start"], "tick") for w in words if w["key"]],
                            total, cfg, sfx)

    # 5) zvuk
    music = audio_mix.pick_music(rng)
    if music:
        log(f"Hudba: {music.name}")
    mix_path = audio_dir / "mix.wav"
    audio_mix.mix(audio_dir / "voice.wav", sfx, music, total, cfg, mix_path)

    # 6) titulky (moviepy, snímek po snímku) + mux
    if script.get("mode") != "motion":
        cta_start = timings["beats"][-1]["start"] if script["beats"][-1].get("role") == "cta" else None
        cap = CaptionRenderer(words, cfg, total, script.get("hook_text"), script.get("cta_text"), cta_start)
        with VideoFileClip(str(work / "base.mp4"), audio=False) as base:
            clip = base.transform(lambda gf, t: cap.draw(gf(t), t)).with_duration(min(base.duration, total))
            clip.write_videofile(str(silent), fps=v["fps"], codec="libx264", audio=False, preset=v["preset"],
                                 ffmpeg_params=["-crf", str(v["crf"]), "-pix_fmt", "yuv420p"], logger="bar")
    ffmpeg("-i", str(silent), "-i", str(mix_path), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out_path))

    _write_post(script, out_path, used, backend.name)
    if not keep:
        shutil.rmtree(work, ignore_errors=True)
    log(f"Hotovo → {out_path}")
    return out_path


def _write_post(script: dict, out_path: Path, used: list[str], tts_name: str) -> None:
    """Popisek k příspěvku + zdroje záběrů vedle videa."""
    credits = []
    for p in sorted(set(used)):
        path = Path(p)
        cred_file = path.parent / "credits.json"
        if path.name.startswith("pexels-") and cred_file.exists():
            meta = read_json(cred_file).get(path.stem.removeprefix("pexels-"), {})
            if meta:
                credits.append(f"- Pexels: {meta.get('author')} – {meta.get('url')}")
    lines = [
        script.get("caption") or script.get("title", ""),
        "",
        "---",
        "Pozn. pro zveřejnění (nekopírovat do popisku):",
        f"- Hlas je syntetický ({tts_name}). TikTok vyžaduje u realistického AI obsahu štítek „Obsah vytvořený AI“ – zapni ho;"
        " u Reels a Shorts se řiď aktuálními pravidly platformy.",
        "- Skript: " + " / ".join(strip_markup(b["text"]) for b in script["beats"]),
    ]
    if credits:
        lines += ["- Záběry (Pexels licence, uvedení autora není povinné, ale je fajn):", *credits]
    out_path.with_suffix(".txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
