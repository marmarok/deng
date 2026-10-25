# AB1 speaker map for the VOA voice package (team, CPU only). Pre-registered voice rule (veri/egitime-giris-kurallari.md 5):
#   quality A or B, a single speaker, 3-20 s, two-ear agreement <= 0.05, no speaker above 10% of the voice data.
# This job does the audio half; the label half needs the three-ear vote (team k10) and is joined afterwards.
# For every train segment of team/deng-voa-kurmanji-v1 with quality A/B and 3-20 s:
#   - ECAPA speaker embeddings (speechbrain/spkrec-ecapa-voxceleb, Apache 2.0) of 2 s windows (2 s hop, last window
#     aligned to the end); the segment embedding is the normalised mean of its windows;
#   - single speaker: sim_min = min cosine(window, segment) >= TH_SINGLE;
#   - speaker id: average-linkage clustering (cosine) of the single-speaker segments, cut at TH_SAME.
# Both thresholds are fixed on Common Voice (public CV24 copy, speaker = client_id[:16]) before any VOA number is seen:
#   TH_SINGLE = 5th percentile of sim_min on joins of two clips of the SAME speaker (6-12 s, like VOA segments);
#               the share of joins of two DIFFERENT speakers it catches is reported;
#   TH_SAME   = equal-error cosine between same-speaker and different-speaker clip pairs.
# Output (/kaggle/working): spk.jsonl, emb.npy + emb-ids.json, calib.json, stats.json, worker.log.
import os, io, csv, sys, json, glob, time, random, signal, tarfile, subprocess, urllib.request
from collections import defaultdict
START = time.time()
DEADLINE_S = 6 * 3600
STOP_AT = START + DEADLINE_S - 20 * 60
W = "/kaggle/working"; T = "/kaggle/temp"; os.makedirs(T, exist_ok=True)
STATS = {}
def left(): return STOP_AT - time.time()
def save(key, val):
    STATS[key] = val; json.dump(STATS, open(f"{W}/stats.json", "w"), indent=1, ensure_ascii=False)
    print("STAT", key, json.dumps(val, ensure_ascii=False)[:300], flush=True)
def run(cmd, limit, log=None):
    limit = max(60, min(limit, left())); t0 = time.time()
    print("$", cmd[:300], f"(limit {limit/60:.0f} min)", flush=True)
    out = open(log, "w") if log else None
    p = subprocess.Popen(cmd, shell=True, start_new_session=True, stdout=out or None, stderr=subprocess.STDOUT if out else None)
    try: code = p.wait(timeout=limit)
    except subprocess.TimeoutExpired:
        for sig in (signal.SIGTERM, signal.SIGKILL):
            try: os.killpg(p.pid, sig)
            except ProcessLookupError: pass
            try: p.wait(timeout=60); break
            except subprocess.TimeoutExpired: pass
        code = "timeout"
    if out: out.close()
    return code, round(time.time() - t0, 1)

# ---------- VOA segments ----------
MAN = glob.glob("/kaggle/input/**/manifest.jsonl", recursive=True)[0]; ROOT = os.path.dirname(MAN)
voa = [r for r in map(json.loads, open(MAN)) if r["split"] == "train" and r.get("quality") in ("A", "B") and 3 <= r["end"] - r["start"] <= 20]
save("voa_segments", {"n": len(voa), "hours": round(sum(r["end"] - r["start"] for r in voa) / 3600, 2), "files": len({r["file"] for r in voa})})
with open(f"{T}/voa.jsonl", "w") as f:
    for r in voa: f.write(json.dumps({k: r[k] for k in ("audio", "shard", "file", "start", "end", "quality")}) + "\n")

# ---------- Common Voice calibration clips (public CV24 copy) ----------
HF = "https://huggingface.co/datasets/SECT19N/Preprocessed-CVS-24-KMR/resolve/main"
by_spk, gender = defaultdict(list), {}
for r in csv.DictReader(io.StringIO(urllib.request.urlopen(f"{HF}/validated.tsv", timeout=300).read().decode("utf8")), delimiter="\t", quoting=csv.QUOTE_NONE):
    s = r["client_id"][:16]; by_spk[s].append(os.path.basename(r["path"]).rsplit(".", 1)[0]); gender.setdefault(s, r.get("gender") or "")
rng = random.Random(21)
spks = rng.sample(sorted(s for s, v in by_spk.items() if len(v) >= 6), 150)
want = {}
for s in spks:
    for stem in rng.sample(sorted(by_spk[s]), 4): want[stem] = s
def fetch_full(url, path, tries=10):
    """Download with resume until the file has the server's full size (a 7.6 GB download was cut at 5.7 GB on 19.10)."""
    size = int(urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=120).headers.get("Content-Length") or 0)
    for _ in range(tries):
        subprocess.run(["curl", "-sL", "-C", "-", "--retry", "5", "-o", path, url], timeout=3600)
        have = os.path.getsize(path) if os.path.exists(path) else 0
        if size and have >= size: return have
        time.sleep(10)
    raise SystemExit(f"download incomplete: {have} of {size} bytes")
TGZ = f"{T}/cv24.tar.gz"; t0 = time.time()
fetch_full(f"{HF}/Common_Voice_Kurmanji_Kurdish_Processed_Audio.tar.gz", TGZ)
os.makedirs(f"{T}/cv", exist_ok=True); got = 0
with tarfile.open(TGZ, "r|gz") as tf:
    for m in tf:
        stem = os.path.basename(m.name).rsplit(".", 1)[0]
        if m.isfile() and stem in want:
            open(f"{T}/cv/{stem}.wav", "wb").write(tf.extractfile(m).read()); got += 1
os.remove(TGZ)
json.dump({"clips": {k: v for k, v in want.items() if os.path.exists(f"{T}/cv/{k}.wav")}, "gender": {s: gender[s] for s in spks}}, open(f"{T}/cv.json", "w"))
save("cv", {"speakers": len(spks), "clips_wanted": len(want), "found": got, "minutes": round((time.time() - t0) / 60, 1)})

# ---------- pinned CPU environment ----------
run("pip install -q uv", 600)
VENV = f"{T}/sb"; PY = f"{VENV}/bin/python"
code, sec = run(f"UV_PYTHON_DOWNLOADS=automatic uv venv --managed-python -p 3.12 {VENV} && "
                f"uv pip install --python {PY} -q --index-url https://download.pytorch.org/whl/cpu torch==2.5.1 torchaudio==2.5.1 && "
                f"uv pip install --python {PY} -q speechbrain==1.0.3 huggingface_hub==0.25.2 soundfile scipy 'numpy<2'", 1500)
if code != 0:  # the CPU wheel index failed: the default (CUDA) wheels run on CPU too
    code, sec = run(f"uv pip install --python {PY} -q torch==2.5.1 torchaudio==2.5.1 speechbrain==1.0.3 huggingface_hub==0.25.2 soundfile scipy 'numpy<2'", 1500)
save("env", {"exit": code, "seconds": sec})

open(f"{T}/worker.py", "w").write(r'''
import os, io, sys, json, time, random, tarfile
from collections import defaultdict
import numpy as np, soundfile as sf, torch
W, T, ROOT, STOP_AT = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
torch.set_num_threads(os.cpu_count() or 4)
from huggingface_hub import snapshot_download
from speechbrain.inference.speaker import EncoderClassifier
def log(*a): print(time.strftime("%H:%M:%S"), *a, flush=True)
mdir = snapshot_download("speechbrain/spkrec-ecapa-voxceleb", local_dir=f"{T}/ecapa")
try: enc = EncoderClassifier.from_hparams(source=mdir, savedir=f"{T}/ecapa-run", overrides={"pretrained_path": mdir}, run_opts={"device": "cpu"})
except Exception as ex:
    log("local load failed, loading from the hub:", repr(ex)[:200])
    enc = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir=f"{T}/ecapa-hub", run_opts={"device": "cpu"})
RATE = 16000; WIN = 2 * RATE
def mono(d, sr):
    if d.ndim > 1: d = d.mean(1)
    if sr != RATE:
        import torchaudio.functional as F
        d = F.resample(torch.from_numpy(d).float(), sr, RATE).numpy()
    return d.astype(np.float32)
def trim(d, top_db=35):
    n = len(d) // 400
    if n < 2: return d
    e = (d[:n * 400].reshape(n, 400) ** 2).mean(1); keep = np.where(e >= e.max() * 10 ** (-top_db / 10))[0]
    return d[keep[0] * 400:(keep[-1] + 1) * 400]
def windows(d):
    if len(d) <= WIN: return [np.pad(d, (0, WIN - len(d)))]
    starts = list(range(0, len(d) - WIN + 1, WIN))
    if len(d) - (starts[-1] + WIN) > RATE // 2: starts.append(len(d) - WIN)
    return [d[s:s + WIN] for s in starts]
def embed(wavs):
    """wavs: list of 1-D arrays -> list of (segment embedding, sim_min, sim_ends, n_windows)."""
    ws, own = [], []
    for i, d in enumerate(wavs):
        for w in windows(trim(d)): ws.append(w); own.append(i)
    es = []
    for i in range(0, len(ws), 64):
        with torch.no_grad(): e = enc.encode_batch(torch.from_numpy(np.stack(ws[i:i + 64]))).squeeze(1).numpy()
        es.append(e / np.linalg.norm(e, axis=1, keepdims=True))
    es = np.concatenate(es); own = np.array(own); out = []
    for i in range(len(wavs)):
        e = es[own == i]; m = e.mean(0); m = m / np.linalg.norm(m)
        out.append((m, float((e @ m).min()), float(e[0] @ e[-1]), len(e)))
    return out

# ---- 1) calibration on Common Voice ----
cv = json.load(open(f"{T}/cv.json")); clips = cv["clips"]; gender = cv["gender"]
by = defaultdict(list)
for stem, s in sorted(clips.items()): by[s].append(stem)
by = {s: v for s, v in by.items() if len(v) == 4}
aud = {stem: mono(*sf.read(f"{T}/cv/{stem}.wav", dtype="float32")) for v in by.values() for stem in v}
gap = np.zeros(RATE // 4, dtype=np.float32)
join = lambda a, b: np.concatenate([trim(aud[a]), gap, trim(aud[b])])
spk = sorted(by); rng = random.Random(22)
same = [join(by[s][0], by[s][1]) for s in spk] + [join(by[s][2], by[s][3]) for s in spk]
pairs = []
for g in sorted({gender.get(s, "") for s in spk}):
    grp = [s for s in spk if gender.get(s, "") == g]; rng.shuffle(grp)
    pairs += [(grp[i], grp[i + 1]) for i in range(0, len(grp) - 1, 2)]
rest = list(spk); rng.shuffle(rest)
pairs += [(rest[i], rest[-1 - i]) for i in range(len(rest) // 2) if rest[i] != rest[-1 - i]]
diff = [join(by[a][0], by[b][2]) for a, b in pairs] + [join(by[b][1], by[a][3]) for a, b in pairs]
t0 = time.time()
s_same = [x[1] for x in embed(same)]; s_diff = [x[1] for x in embed(diff)]
clip = {stem: x[0] for stem, x in zip(list(aud), embed(list(aud.values())))}
cv_audio_s = (sum(len(d) for d in same + diff) + sum(len(d) for d in aud.values())) / RATE
log("calibration embedded", round(cv_audio_s / 60, 1), "min of audio in", round(time.time() - t0, 1), "s")
TH_SINGLE = float(np.percentile(s_same, 5))
same_cos = [float(clip[v[i]] @ clip[v[j]]) for v in by.values() for i, j in ((0, 1), (2, 3), (0, 2), (1, 3))]
diff_cos = []
for _ in range(4000):
    a, b = rng.sample(spk, 2); diff_cos.append(float(clip[rng.choice(by[a])] @ clip[rng.choice(by[b])]))
grid = np.linspace(-0.2, 1.0, 1201)
far = np.array([np.mean(np.array(diff_cos) >= t) for t in grid]); frr = np.array([np.mean(np.array(same_cos) < t) for t in grid])
k = int(np.argmin(np.abs(far - frr))); TH_SAME = float(grid[k])
pct = lambda v: {p: round(float(np.percentile(v, p)), 3) for p in (1, 5, 25, 50, 75, 95)}
calib = {"TH_SINGLE": round(TH_SINGLE, 4), "TH_SAME": round(TH_SAME, 4), "eer": round(float((far[k] + frr[k]) / 2), 4),
         "single_test": {"same_joins": len(s_same), "diff_joins": len(s_diff), "same_pass": round(float(np.mean(np.array(s_same) >= TH_SINGLE)), 3),
                         "diff_caught": round(float(np.mean(np.array(s_diff) < TH_SINGLE)), 3), "sim_min_same": pct(s_same), "sim_min_diff": pct(s_diff)},
         "pair_test": {"same_pairs": len(same_cos), "diff_pairs": len(diff_cos), "cos_same": pct(same_cos), "cos_diff": pct(diff_cos)},
         "speed_x_realtime": round(cv_audio_s / max(1e-6, time.time() - t0), 1)}
json.dump(calib, open(f"{W}/calib.json", "w"), indent=1)
log("CALIB", json.dumps(calib)[:400])

# ---- 2) VOA segments, shard by shard ----
rows = [json.loads(l) for l in open(f"{T}/voa.jsonl")]
by_shard = defaultdict(dict)
for r in rows: by_shard[r["shard"]][r["audio"]] = r
out = open(f"{W}/spk-raw.jsonl", "w"); embs, ids = [], []; done = 0; t0 = time.time(); stopped = False
for sh in sorted(by_shard):
    if time.time() > STOP_AT: stopped = True; break
    need = by_shard[sh]; buf = []
    with tarfile.open(os.path.join(ROOT, sh)) as tf:
        for m in tf:
            if m.name not in need: continue
            d, sr = sf.read(io.BytesIO(tf.extractfile(m).read()), dtype="float32"); buf.append((need[m.name], mono(d, sr)))
            if len(buf) == 200 or (buf and time.time() > STOP_AT):
                for (r, _), (e, smin, sends, nw) in zip(buf, embed([d for _, d in buf])):
                    out.write(json.dumps({**r, "dur": round(r["end"] - r["start"], 2), "n_win": nw, "sim_min": round(smin, 4), "sim_ends": round(sends, 4),
                                          "single": smin >= TH_SINGLE}) + "\n")
                    embs.append(e.astype(np.float32)); ids.append(r["audio"])
                done += len(buf); buf = []; out.flush()
                el = time.time() - t0; log(f"{done}/{len(rows)} segments, {el / 60:.1f} min, eta {el / done * (len(rows) - done) / 60:.0f} min")
                if time.time() > STOP_AT: stopped = True; break
    for (r, _), (e, smin, sends, nw) in zip(buf, embed([d for _, d in buf]) if buf else []):
        out.write(json.dumps({**r, "dur": round(r["end"] - r["start"], 2), "n_win": nw, "sim_min": round(smin, 4), "sim_ends": round(sends, 4),
                              "single": smin >= TH_SINGLE}) + "\n")
        embs.append(e.astype(np.float32)); ids.append(r["audio"])
    done += len(buf); out.flush()
    np.save(f"{W}/emb.npy", np.stack(embs)); json.dump(ids, open(f"{W}/emb-ids.json", "w"))
    if stopped: break
out.close()
json.dump({"embedded": done, "of": len(rows), "stopped_at_deadline": stopped, "minutes": round((time.time() - t0) / 60, 1)}, open(f"{W}/embed-done.json", "w"))
log("WORKER_DONE", done, "of", len(rows))
''')
code, sec = run(f"{PY} {T}/worker.py {W} {T} {ROOT} {STOP_AT - 25 * 60}", left() - 20 * 60, log=f"{W}/worker.log")
save("worker", {"exit": code, "seconds": sec})
for f in ("calib.json", "embed-done.json"):
    if os.path.exists(f"{W}/{f}"): save(f.split(".")[0], json.load(open(f"{W}/{f}")))

# ---------- speaker clusters on the single-speaker segments ----------
open(f"{T}/cluster.py", "w").write(r'''
import sys, json
from collections import defaultdict
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
W = sys.argv[1]
calib = json.load(open(f"{W}/calib.json")); th = calib["TH_SAME"]
rows = [json.loads(l) for l in open(f"{W}/spk-raw.jsonl")]
E = np.load(f"{W}/emb.npy"); ids = json.load(open(f"{W}/emb-ids.json")); pos = {a: i for i, a in enumerate(ids)}
rows = [r for r in rows if r["audio"] in pos]
single = [r for r in rows if r["single"]]
X = E[[pos[r["audio"]] for r in single]].astype(np.float64)
lab = fcluster(linkage(X, method="average", metric="cosine"), t=1 - th, criterion="distance") if len(X) > 1 else np.ones(len(X), int)
hours, files = defaultdict(float), defaultdict(set)
for r, c in zip(single, lab): hours[c] += r["dur"] / 3600; files[c].add(r["file"])
order = sorted(hours, key=lambda c: -hours[c]); name = {c: f"v{i + 1:04d}" for i, c in enumerate(order)}
spk_of = {r["audio"]: name[c] for r, c in zip(single, lab)}
with open(f"{W}/spk.jsonl", "w") as f:
    for r in rows: f.write(json.dumps({**r, "spk": spk_of.get(r["audio"])}) + "\n")
h = np.array([hours[c] for c in order]); total = float(h.sum())
lo, hi = 0.0, float(h.max()) if len(h) else 0.0  # 10% cap: largest c with c <= 0.1 * sum(min(h, c))
for _ in range(60):
    c = (lo + hi) / 2
    if c <= 0.1 * float(np.minimum(h, c).sum()): lo = c
    else: hi = c
capped = float(np.minimum(h, lo).sum()) if len(h) else 0.0
res = {"segments": len(rows), "hours": round(sum(r["dur"] for r in rows) / 3600, 2), "single": len(single), "single_hours": round(total, 2),
       "by_quality_single_hours": {q: round(sum(r["dur"] for r in single if r["quality"] == q) / 3600, 2) for q in ("A", "B")},
       "clusters": len(order), "clusters_over_0.5h": int((h >= 0.5).sum()),
       "top20": [{"spk": name[c], "hours": round(hours[c], 2), "share": round(hours[c] / total, 3), "files": len(files[c])} for c in order[:20]],
       "cap10_hours_upper_bound": round(capped, 2), "cap10_per_speaker_h": round(lo, 3),
       "sim_min_voa": {p: round(float(np.percentile([r["sim_min"] for r in rows], p)), 3) for p in (1, 5, 25, 50, 75, 95)}}
json.dump(res, open(f"{W}/clusters.json", "w"), indent=1)
print("CLUSTERS", json.dumps(res)[:600], flush=True)
''')
code, sec = run(f"{PY} {T}/cluster.py {W}", 1800, log=f"{W}/cluster.log")
save("cluster", {"exit": code, "seconds": sec})
if os.path.exists(f"{W}/clusters.json"): save("clusters", json.load(open(f"{W}/clusters.json")))
save("elapsed_h", round((time.time() - START) / 3600, 2))
print("DONE", flush=True)
