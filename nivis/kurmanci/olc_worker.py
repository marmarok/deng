#!/usr/bin/env python3
"""Find each vowel in speech and measure it. Runs on Kaggle in a small environment of its own; needs no Kurmanji code.

  python olc_worker.py <rows.json> <out.jsonl> <stop_at unix time>

Each row: {id, path, t0, dur, words}, words from vurgu_olcum.clip_words. Forced alignment (torchaudio MMS_FA) places the
letters; a letter runs from the middle of the gap before it to the middle of the gap after it, because CTC marks only the
frames it is surest of. Praat gives pitch, loudness and the share of loudness above 500 Hz for each vowel.
One line per clip, written at once, so a stopped run keeps what it measured.
"""
import json
import math
import subprocess
import sys
import time

import numpy as np
import parselmouth
import torch
import torchaudio

SR = 16000
torch.set_num_threads(1)
rows, out_path, stop_at = json.load(open(sys.argv[1])), sys.argv[2], float(sys.argv[3])
device = "cuda" if torch.cuda.is_available() else "cpu"
bundle = torchaudio.pipelines.MMS_FA
model = bundle.get_model(with_star=False).to(device).eval()
tokenizer, aligner = bundle.get_tokenizer(), bundle.get_aligner()


def decode(path):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, timeout=1800).stdout
    return np.frombuffer(raw, dtype=np.float32)


def mean_over(values, times, a, b):
    sel = values[(times >= a) & (times < b)]
    sel = sel[~np.isnan(sel)]
    return float(sel.mean()) if len(sel) else None


def peak_over(values, times, a, b):
    sel = values[(times >= a) & (times < b)]
    sel = sel[~np.isnan(sel)]
    return float(sel.max()) if len(sel) else None


def num(x, d=1):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(x, d)


def measure(d, words):
    wav = torch.from_numpy(d.copy()).unsqueeze(0).to(device)
    with torch.inference_mode():
        em, _ = model(wav)
    use = [w for w in words if w["a"]]
    spans = aligner(em[0].cpu(), tokenizer([w["a"] for w in use]))
    sec = len(d) / SR / em.shape[1]
    snd = parselmouth.Sound(d.astype(np.float64), sampling_frequency=SR)
    pitch = snd.to_pitch(time_step=0.01, pitch_floor=70, pitch_ceiling=450)
    f0 = pitch.selected_array["frequency"].astype(float)
    f0[f0 <= 0] = np.nan
    pt = pitch.xs()
    median = np.nanmedian(f0) if np.any(~np.isnan(f0)) else np.nan
    st = 12 * np.log2(f0 / median)
    inten = snd.to_intensity(minimum_pitch=75, time_step=0.01, subtract_mean=False)
    iv, it = inten.values[0], inten.xs()
    hp = parselmouth.praat.call(snd, "Filter (pass Hann band)", 500, 7900, 100).to_intensity(minimum_pitch=75, time_step=0.01, subtract_mean=False)
    hv, ht = hp.values[0], hp.xs()
    out = []
    for w, s in zip(use, spans):
        rec = {"w": w["w"], "k": w["k"], "r": w["r"], "s": w["s"], "p": w["p"], "t": [round(s[0].start * sec, 3), round(s[-1].end * sec, 3)], "v": []}
        if w["ok"] and len(s) == len(w["a"]):
            edge = [s[0].start] + [(s[j].end + s[j + 1].start) / 2 for j in range(len(s) - 1)] + [s[-1].end]
            for syl, at in enumerate(w["vi"]):
                if at is None:
                    continue
                a, b = edge[at] * sec, edge[at + 1] * sec
                db, hdb = mean_over(iv, it, a, b), mean_over(hv, ht, a, b)
                rec["v"].append([syl, w["w"][at], round((b - a) * 1000), num(mean_over(st, pt, a, b)), num(peak_over(st, pt, a, b)), num(db),
                                 num(hdb - db if db is not None and hdb is not None else None), round(float(s[at].score), 2)])
        out.append(rec)
    return out


cache_path, cache = None, None
n = done_s = 0
t0 = time.time()
with open(out_path, "w") as f:
    for r in rows:
        if time.time() > stop_at:
            print("STOP deadline", flush=True)
            break
        try:
            if r["path"] != cache_path:
                cache_path, cache = r["path"], decode(r["path"])
            d = cache[int(r["t0"] * SR): int((r["t0"] + r["dur"]) * SR)] if r["dur"] else cache
            words = measure(d, r["words"])
            f.write(json.dumps({"id": r["id"], "src": r.get("src"), "dur": round(len(d) / SR, 2), "words": words}, ensure_ascii=False) + "\n")
            f.flush()
            n += 1
            done_s += len(d) / SR
        except Exception as e:
            print("skip", r["id"], repr(e)[:160], flush=True)
        if n % 200 == 0 and n:
            print(f"clips {n}, audio {done_s / 3600:.2f} h, {done_s / (time.time() - t0):.1f} x real time", flush=True)
print("WORKER_DONE", n, round(done_s / 3600, 3), round(time.time() - t0), flush=True)
