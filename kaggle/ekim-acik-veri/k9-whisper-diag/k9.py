# K9 third ear (team, 2xT4): Whisper large-v3 fine-tuned on Northern Kurdish (aranemini/whisper-v3-large-northern-
# kurdish, public) over the public VOA set team/deng-voa-kurmanji-v1. the k7-redraft gave every train segment a
# CTC draft but the norm1 LLM pass ran out of time on 14,433 of 46,201 segments; a third, independent model family lets
# those be kept by CTC/Whisper agreement and turns the rest into a three-ear vote.
# The segment order is rebuilt exactly as in k7-redraft (same manifest, same hash sort), so ids match its rows; the
# rows the LLM pass never reached are ins[0::2][18120:] and ins[1::2][13648:] (k7-redraft stats, 19.10) and go first.
# Also checks the Whisper scorer in a pinned venv: the s9 scoring step segfaulted right after loading this model.
# MODE "diag": 300 missing + 100 covered segments per GPU, measures speed and agreement with the VOA label.
# MODE "full": every train segment, missing ones first; rows written as they go (rows-whisper-<gpu>.jsonl).
import os, re, sys, json, glob, time, signal, tarfile, hashlib, threading, subprocess
from collections import defaultdict, Counter
MODE = "diag"
START = time.time()
DEADLINE_S = 2 * 3600
STOP = START + DEADLINE_S - 15 * 60
W = "/kaggle/working"; T = "/kaggle/temp"; SEG = f"{T}/seg"; os.makedirs(SEG, exist_ok=True)
LLM_DONE = (18120, 13648)
STATS, LOCK = {}, threading.Lock()
def left(): return DEADLINE_S - (time.time() - START)
def save(key, val):
    with LOCK:
        STATS[key] = val; json.dump(STATS, open(f"{W}/stats.json", "w"), indent=1, ensure_ascii=False)
    print("STAT", key, json.dumps(val, ensure_ascii=False)[:300], flush=True)
def run(cmd, limit, log=None):
    limit = max(60, min(limit, left() - 120)); t0 = time.time()
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

# ---------- the k7-redraft order ----------
MAN = [f for f in glob.glob("/kaggle/input/**/manifest.jsonl", recursive=True)][0]; ROOT = os.path.dirname(MAN)
rows = [json.loads(l) for l in open(MAN)]
pick = [r for r in rows if r["split"] == "train"]
h = lambda r: hashlib.md5(r["file"].encode()).hexdigest()
pick.sort(key=lambda r: (h(r), r["start"]))
# k7-redraft kept a segment only if its audio was extracted and it was <= 39.5 s; the shard members are all present
ins = [{"id": f"s{i:05d}", "r": r, "dur": r["end"] - r["start"]} for i, r in enumerate(pick) if r["end"] - r["start"] <= 39.5]
ins = [x for i in range(0, len(ins), 400) for x in sorted(ins[i:i + 400], key=lambda r: -r["dur"])]
missing = ins[0::2][LLM_DONE[0]:] + ins[1::2][LLM_DONE[1]:]
miss_ids = {x["id"] for x in missing}
covered = [x for x in ins if x["id"] not in miss_ids]
save("order", {"segments": len(ins), "matches_k7": len(ins) == 46201, "missing": len(missing), "missing_h": round(sum(x["dur"] for x in missing) / 3600, 1)})
if MODE == "diag":
    work = missing[:600] + covered[:200]
else:
    work = missing + covered
want = defaultdict(set)
for x in work: want[x["r"]["shard"]].add(x["r"]["audio"])
for sh, names in want.items():
    if left() < 30 * 60: break
    with tarfile.open(f"{ROOT}/{sh}") as t:
        for m in t.getmembers():
            if m.name in names: t.extract(m, SEG)
work = [x for x in work if os.path.exists(f"{SEG}/{x['r']['audio']}")]
for g in (0, 1):
    with open(f"{T}/in-{g}.jsonl", "w") as f:
        for x in work[g::2]:
            f.write(json.dumps({"id": x["id"], "path": f"{SEG}/{x['r']['audio']}", "dur": x["dur"], "label": x["r"]["text"],
                                "missing": x["id"] in miss_ids}, ensure_ascii=False) + "\n")
save("work", {"segments": len(work), "hours": round(sum(x["dur"] for x in work) / 3600, 2)})

# ---------- pinned venv (the system image moved to python 3.13; the s9 scorer segfaulted there) ----------
run("pip install -q uv", 600)
VENV = f"{T}/wh"; PY = f"{VENV}/bin/python"
code, sec = run(f"UV_PYTHON_DOWNLOADS=automatic uv venv --managed-python -p 3.12 {VENV} && uv pip install --python {PY} -q "
                f"torch==2.5.1 transformers==4.46.3 accelerate==1.1.1 soundfile librosa 'numpy<2'", 1500)
save("env", {"exit": code, "seconds": sec})
open(f"{T}/worker.py", "w").write(r'''
import sys, json, time, faulthandler, torch, numpy as np, soundfile as sf, librosa
faulthandler.enable()
from transformers import pipeline
src, out, stop_at, bs = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4])
rows = [json.loads(l) for l in open(src)]
t0 = time.time()
asr = pipeline("automatic-speech-recognition", model="aranemini/whisper-v3-large-northern-kurdish", torch_dtype=torch.float16,
               device=0, chunk_length_s=30)
load_s = time.time() - t0
def audio(p):
    d, sr = sf.read(p, dtype="float32", always_2d=False)
    if d.ndim > 1: d = d.mean(axis=1)
    if sr != 16000: d = librosa.resample(d, orig_sr=sr, target_sr=16000)
    return {"raw": d, "sampling_rate": 16000}
secs, t1, n = 0.0, time.time(), 0
def meta(done):
    json.dump({"batch": bs, "load_s": round(load_s, 1), "audio_s": round(secs, 1), "wall_s": round(time.time() - t1, 1), "rows": n,
               "of": len(rows), "finished": done, "peak_gb": round(torch.cuda.max_memory_allocated() / 1e9, 2)}, open(out + ".meta.json", "w"))
with open(out, "w") as f:
    for i in range(0, len(rows), bs):
        if time.time() > stop_at: break
        b = rows[i:i + bs]
        try: got = list(zip(b, asr([audio(r["path"]) for r in b], batch_size=bs, generate_kwargs={"task": "transcribe"})))
        except Exception as ex:
            print("BATCH_FAILED", i, repr(ex)[:200], flush=True); got = []
            for r in b:
                try: got += list(zip([r], asr([audio(r["path"])], batch_size=1, generate_kwargs={"task": "transcribe"})))
                except Exception as ex2: print("CLIP_SKIPPED", r["id"], repr(ex2)[:120], flush=True)
        for r, h in got:
            f.write(json.dumps({"id": r["id"], "hyp": h["text"].strip()}, ensure_ascii=False) + "\n"); secs += r["dur"]; n += 1
        f.flush()
        if (i // bs) % 10 == 0: meta(False)
meta(n == len(rows))
print("WORKER_DONE", n, flush=True)
''')
def chain(g):
    code, sec = run(f"CUDA_VISIBLE_DEVICES={g} {PY} {T}/worker.py {T}/in-{g}.jsonl {W}/rows-whisper-{g}.jsonl {STOP} 16",
                    STOP - time.time() + 300, log=f"{W}/worker-{g}.log")
    save(f"pass_{g}", {"exit": code, "seconds": sec})
threads = [threading.Thread(target=chain, args=(g,), daemon=True) for g in (0, 1)]
for t in threads: t.start()
for t in threads: t.join(timeout=max(60, left() - 8 * 60))
for g in (0, 1):
    mp = f"{W}/rows-whisper-{g}.jsonl.meta.json"
    if os.path.exists(mp): save(f"meta_{g}", json.load(open(mp)))

# ---------- agreement with the VOA label (plain normaliser; the three-ear merge uses Omnilingual's later) ----------
def norm(t): return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", (t or "").lower())).strip()
def ed(a, b):
    d = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        p, d[0] = d[0], i
        for j, y in enumerate(b, 1): p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (x != y))
    return d[-1]
lab = {}
for g in (0, 1):
    for l in open(f"{T}/in-{g}.jsonl"): r = json.loads(l); lab[r["id"]] = r
cer = defaultdict(list)
for g in (0, 1):
    f = f"{W}/rows-whisper-{g}.jsonl"
    if not os.path.exists(f): continue
    for l in open(f):
        r = json.loads(l); x = lab[r["id"]]; a, b = norm(x["label"]), norm(r["hyp"])
        if a: cer["missing" if x["missing"] else "covered"].append(ed(b, a) / len(a))
save("cer_vs_label", {k: {"n": len(v), "median": round(sorted(v)[len(v) // 2], 3), "share_le_0.10": round(sum(c <= 0.10 for c in v) / len(v), 3)}
                      for k, v in cer.items() if v})
save("elapsed_h", round((time.time() - START) / 3600, 2))
print("DONE", flush=True)
