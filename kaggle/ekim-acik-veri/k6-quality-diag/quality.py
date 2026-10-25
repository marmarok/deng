# K6 quality classes, measurement (team, 1 GPU). Pre-registered classes (veri/egitime-giris-kurallari.json, quality):
# A: OVRL >= 3.3, SIG >= 3.5, wideband, no music; B: OVRL >= 3.0, wideband, no music; C: narrowband or OVRL 2.5-3.0;
# D: OVRL < 2.5 or music. This run measures the three checks on a random sample of 400 VOA segments (interview + guest,
# from k6-lid-full rows) to learn the speed of each and the class shares before the full pass:
#   - DNSMOS P.835 (Microsoft DNS-Challenge sig_bak_ovr.onnx, 9.01 s windows, 1 s hop, mean), SIG/BAK/OVRL;
#   - bandwidth: share of power above 4 kHz in the 16 kHz signal (telephone audio has almost none);
#   - music: AST AudioSet classifier (MIT/ast-finetuned-audioset-10-10-0.4593), score of the "Music" label.
# Outputs: rows.jsonl (per segment), stats.json. One deadline; every subprocess and download has a timeout.
import os, re, json, glob, time, random, socket, subprocess, urllib.request
socket.setdefaulttimeout(120)
START = time.time()
DEADLINE_S = 5400
STOP_AT = START + DEADLINE_S - 10 * 60
W = "/kaggle/working"; T = "/kaggle/temp"; os.makedirs(T, exist_ok=True)
STATS = {}
def left(): return STOP_AT - time.time()
def save(k, v):
    STATS[k] = v; json.dump(STATS, open(f"{W}/stats.json", "w"), indent=1); print("STAT", k, json.dumps(v)[:300], flush=True)
p = subprocess.run("pip install -q onnxruntime-gpu", shell=True, timeout=900); save("env", p.returncode)
import numpy as np, soundfile as sf, torch, onnxruntime as ort
rows = [json.loads(l) for l in open([f for f in glob.glob("/kaggle/input/**/rows.jsonl", recursive=True) if "lid-full" in f][0])]
paths = {}
for f in glob.glob("/kaggle/input/**/items.jsonl", recursive=True):
    root = os.path.join(os.path.dirname(f), "audio")
    for l in open(f):
        x = json.loads(l); q = f"{root}/{x['file']}"
        if os.path.exists(q): paths[x["file"]] = q
rng = random.Random(19); sample = rng.sample([r for r in rows if r["file"] in paths], 400)
save("sample", {"rows_total": len(rows), "sample": len(sample)})
def seg16(r):
    out = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(r["start"]), "-t", str(r["end"] - r["start"]), "-i", paths[r["file"]],
                          "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, timeout=300, check=True).stdout
    return np.frombuffer(out, dtype=np.float32).copy()
t0 = time.time()
for r in sample: r["audio"] = seg16(r)
save("decode_s", round(time.time() - t0, 1))
# ---------- DNSMOS P.835 ----------
onnx = f"{T}/sig_bak_ovr.onnx"
urllib.request.urlretrieve("https://github.com/microsoft/DNS-Challenge/raw/master/DNSMOS/DNSMOS/sig_bak_ovr.onnx", onnx)
sess = ort.InferenceSession(onnx, providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
p_ovr = np.poly1d([-0.06766283, 1.11546468, 0.04602535]); p_sig = np.poly1d([-0.08397278, 1.22083953, 0.0052439]); p_bak = np.poly1d([-0.13166888, 1.60915514, -0.39604546])
L = int(9.01 * 16000)
t0 = time.time()
for r in sample:
    a = r["audio"]
    while len(a) < L: a = np.concatenate([a, a])
    starts = range(0, len(a) - L + 1, 16000)
    s = np.array([sess.run(None, {"input_1": a[i:i + L][None, :].astype(np.float32)})[0][0] for i in starts])
    sig, bak, ovr = s.mean(0)
    r["sig"], r["bak"], r["ovrl"] = round(float(p_sig(sig)), 2), round(float(p_bak(bak)), 2), round(float(p_ovr(ovr)), 2)
save("dnsmos_s", round(time.time() - t0, 1))
# ---------- bandwidth ----------
for r in sample:
    f = np.abs(np.fft.rfft(r["audio"])) ** 2; fr = np.fft.rfftfreq(len(r["audio"]), 1 / 16000)
    r["hf_share"] = round(float(f[fr >= 4000].sum() / max(1e-12, f[fr >= 100].sum())), 5)
# ---------- music ----------
from transformers import pipeline
clf = pipeline("audio-classification", model="MIT/ast-finetuned-audioset-10-10-0.4593", device=0, top_k=None)
t0 = time.time()
for r in sample:
    out = clf({"raw": r["audio"][:16000 * 10], "sampling_rate": 16000})
    d = {x["label"]: x["score"] for x in out}
    r["music"] = round(float(d.get("Music", 0.0)), 3); r["speech"] = round(float(d.get("Speech", 0.0)), 3)
save("music_s", round(time.time() - t0, 1))
hours = sum(r["end"] - r["start"] for r in sample) / 3600
save("speed_x_real_time", {"dnsmos": round(hours * 3600 / max(1, STATS["dnsmos_s"]), 1), "music": round(hours * 3600 / max(1, STATS["music_s"]), 1),
                           "decode": round(hours * 3600 / max(1, STATS["decode_s"]), 1)})
with open(f"{W}/rows.jsonl", "w") as f:
    for r in sample:
        r.pop("audio"); f.write(json.dumps(r, ensure_ascii=False) + "\n")
def dist(key, cuts):
    v = sorted(r[key] for r in sample); return {f"p{q}": v[int(q / 100 * (len(v) - 1))] for q in cuts}
save("dist", {k: dist(k, (5, 25, 50, 75, 95)) for k in ("ovrl", "sig", "bak", "hf_share", "music")})
for hf in (0.001, 0.003, 0.01):
    for mu in (0.3, 0.5):
        wide = lambda r: r["hf_share"] >= hf; mus = lambda r: r["music"] >= mu
        def cls(r):
            if r["ovrl"] < 2.5 or mus(r): return "D"
            if not wide(r) or r["ovrl"] < 3.0: return "C"
            if r["ovrl"] >= 3.3 and r["sig"] >= 3.5: return "A"
            return "B"
        from collections import Counter
        c = Counter(cls(r) for r in sample)
        save(f"classes_hf{hf}_music{mu}", {k: round(c[k] / len(sample), 3) for k in "ABCD"})
save("elapsed_min", round((time.time() - START) / 60, 1))
print("DONE", flush=True)
