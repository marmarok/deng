# K7 redraft, full pass (2xT4). Recipe pre-registered (veri/egitime-giris-kurallari.json, ear_training) and
# measured in k7-redraft-diag (19.10): every VOA train segment of the public set team/deng-voa-kurmanji-v1 is
# rewritten by the best ear (k5-norm1, step_2500) and by Omnilingual CTC 1B v2; agreement = CER(norm1, CTC).
# Diag numbers at agreement <= 0.10: 45% of train hours kept; page-matched WER of the kept part 21.0% (rule: tighten
# to 0.05 only if > 25%, so 0.10 holds); the three Sorani files from the native-speaker audit kept only 16%.
# Segments are ordered by file hash (chunks of 400, each sorted by duration), so a pass cut by the deadline is a random
# subset. Output: rows-ctc.jsonl, rows-llm-*.jsonl (written as they go), redraft.jsonl (merged, with agreement).
import os, re, sys, json, glob, time, types, random, signal, tarfile, threading, subprocess
from collections import defaultdict, Counter
START = time.time()
DEADLINE_S = 8 * 3600
STOP = START + DEADLINE_S - 20 * 60
W = "/kaggle/working"; T = "/kaggle/temp"; SEG = f"{T}/seg"; os.makedirs(SEG, exist_ok=True)
SORANI_FILES = {  # kept only for the 'sorani_file' flag
    "hevpeyvin-5617222.mp3", "mevan-u-mijar-3975621.m4a", "hevpeyvin-2839731.mp3"}
STATS, LOCK = {}, threading.Lock()
def left(): return DEADLINE_S - (time.time() - START)
def save(key, val):
    with LOCK:
        STATS[key] = val; json.dump(STATS, open(f"{W}/stats.json", "w"), indent=1, ensure_ascii=False)
    print("STAT", key, json.dumps(val, ensure_ascii=False)[:300], flush=True)
def run(cmd, limit, log=None):
    """Run a shell command in its own process group; kill the whole group on timeout. Returns (code, seconds)."""
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


# ---------- sample from the public set ----------
MAN = [f for f in glob.glob("/kaggle/input/**/manifest.jsonl", recursive=True)][0]; ROOT = os.path.dirname(MAN)
rows = [json.loads(l) for l in open(MAN)]
import hashlib
pick = [r for r in rows if r["split"] == "train"]
h = lambda r: hashlib.md5(r["file"].encode()).hexdigest()
pick.sort(key=lambda r: (h(r), r["start"]))
want = defaultdict(set)
for r in pick: want[r["shard"]].add(r["audio"])
for sh, names in want.items():
    with tarfile.open(f"{ROOT}/{sh}") as t:
        for m in t.getmembers():
            if m.name in names: t.extract(m, SEG)
inp = []
for i, r in enumerate(pick):
    p = f"{SEG}/{r['audio']}"
    if os.path.exists(p) and r["end"] - r["start"] <= 39.5:
        inp.append({"id": f"s{i:05d}", "path": p, "dur": r["end"] - r["start"], "split": r["split"], "file": r["file"], "label": r["text"],
                    "sorani_file": r["file"] in SORANI_FILES})
inp = [x for i in range(0, len(inp), 400) for x in sorted(inp[i:i + 400], key=lambda r: -r["dur"])]
with open(f"{T}/in.jsonl", "w") as f:
    for r in inp: f.write(json.dumps(r, ensure_ascii=False) + "\n")
save("sample", {"segments": len(inp), "hours": round(sum(r["dur"] for r in inp) / 3600, 2), "by": dict(Counter(r["split"] + ("-sorani" if r["sorani_file"] else "") for r in inp))})

# ---------- Omnilingual env; norm1 model card ----------
run("pip install -q uv", 600)
OMNI = f"{T}/omni"; PY = f"{OMNI}/bin/python"
code, sec = run(f"UV_PYTHON_DOWNLOADS=automatic uv venv --managed-python -p 3.12 {OMNI} && uv pip install --python {PY} -q omnilingual-asr torch==2.8.0 torchaudio==2.8.0 soundfile 'numpy<2' 'pyarrow==20.0.0' rapidfuzz", 1500)
save("env", {"exit": code, "seconds": sec})
run(f"cd {T} && git clone -q --depth 1 https://github.com/facebookresearch/omnilingual-asr.git oa", 300)
SP = glob.glob(f"{OMNI}/lib/python3.12/site-packages")[0]
ck = os.path.dirname((glob.glob("/kaggle/input/**/deng-k5-norm1/**/ckpt/pp_00", recursive=True) or glob.glob("/kaggle/input/**/ckpt/pp_00", recursive=True))[0])
open(f"{SP}/omnilingual_asr/cards/models/deng_norm1.yaml", "w").write(
    f"name: deng_norm1\nmodel_family: wav2vec2_llama\nmodel_arch: 1b_v2\ncheckpoint: {ck}\ntokenizer_ref: omniASR_tokenizer_written_v2\n")
save("norm1_ckpt", ck)
LLM, CTC = "deng_norm1", "omniASR_CTC_1B_v2"
open(f"{T}/worker.py", "w").write(r'''
import sys, json, time, faulthandler, torch
faulthandler.enable()
from omnilingual_asr.models.inference.pipeline import ASRInferencePipeline
card, src, out, stop_at, bs = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), int(sys.argv[5])
rows = [json.loads(l) for l in open(src)]
t0 = time.time(); p = ASRInferencePipeline(model_card=card, device="cuda", dtype=torch.float16); load_s = time.time() - t0
kw = (lambda n: {"lang": ["kmr_Latn"] * n}) if ("LLM" in card or "norm1" in card) else (lambda n: {})
audio, t1, n = 0.0, time.time(), 0
def meta(done):
    json.dump({"card": card, "batch": bs, "load_s": round(load_s, 1), "audio_s": round(audio, 1), "wall_s": round(time.time() - t1, 1),
               "rows": n, "of": len(rows), "finished": done, "peak_gb": round(torch.cuda.max_memory_allocated() / 1e9, 2)}, open(out + ".meta.json", "w"))
with open(out, "w") as f:
    for i in range(0, len(rows), bs):
        if time.time() > stop_at: break
        b = rows[i:i + bs]
        try: got = list(zip(b, p.transcribe([r["path"] for r in b], batch_size=bs, **kw(len(b)))))
        except Exception as ex:  # one bad clip must not kill the pass: retry this batch clip by clip, skip what still fails
            print("BATCH_FAILED", i, repr(ex)[:200], flush=True); got = []
            for r in b:
                try: got += list(zip([r], p.transcribe([r["path"]], batch_size=1, **kw(1))))
                except Exception as ex2: print("CLIP_SKIPPED", r["id"], repr(ex2)[:120], flush=True)
        for r, h in got:
            f.write(json.dumps({"id": r["id"], "hyp": h}, ensure_ascii=False) + "\n"); audio += r["dur"]; n += 1
        f.flush()
        if (i // bs) % 20 == 0: meta(False)
meta(n == len(rows))
print("WORKER_DONE", n, flush=True)
''')

# CTC 1B (fast) over everything on GPU 1, then its share of the LLM; GPU 0 runs the LLM over the even rows.
ins = [json.loads(l) for l in open(f"{T}/in.jsonl")]
for g in (0, 1):
    with open(f"{T}/llm-in-{g}.jsonl", "w") as f:
        for r in ins[g::2]: f.write(json.dumps(r, ensure_ascii=False) + "\n")
def chain(g):
    if g == 1:
        code, sec = run(f"CUDA_VISIBLE_DEVICES=1 {PY} {T}/worker.py {CTC} {T}/in.jsonl {W}/rows-ctc.jsonl {STOP - 2 * 3600} 16", STOP - 2 * 3600 - time.time() + 300, log=f"{W}/worker-ctc.log")
        save("pass_ctc", {"exit": code, "seconds": sec})
    code, sec = run(f"CUDA_VISIBLE_DEVICES={g} {PY} {T}/worker.py {LLM} {T}/llm-in-{g}.jsonl {W}/rows-llm-{g}.jsonl {STOP} 4", STOP - time.time() + 300, log=f"{W}/worker-llm-{g}.log")
    save(f"pass_llm_{g}", {"exit": code, "seconds": sec})
threads = [threading.Thread(target=chain, args=(g,), daemon=True) for g in (0, 1)]
for t in threads: t.start()
for t in threads: t.join(timeout=max(60, left() - 10 * 60))
for name in ("rows-ctc", "rows-llm-0", "rows-llm-1"):
    mp = f"{W}/{name}.jsonl.meta.json"
    if os.path.exists(mp): save(f"meta_{name}", json.load(open(mp)))

# ---------- merge (pure python; the Omnilingual venv has the normalizer, the system python does not need it) ----------
try:
    sys.path.insert(0, f"{T}/oa/workflows/dataprep")
    try: import unidecode  # only needed for rm_diacritics, which is off for Kurdish
    except ImportError: sys.modules["unidecode"] = types.SimpleNamespace(unidecode=lambda x: x)
    from text_tools import text_normalize
    def norm(t):
        t = text_normalize(t or "", "kmr", remove_numbers=False)
        return re.sub(r"\s+", " ", re.sub(r"[—–‐-]", " ", t).replace("'", "")).strip()
    save("normalizer", "omnilingual text_normalize")
except Exception as ex:
    def norm(t): return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", (t or "").lower())).strip()
    save("normalizer", f"fallback ({repr(ex)[:120]})")
run("pip install -q rapidfuzz", 600)
try:
    from rapidfuzz.distance import Levenshtein
    def ed(a, b): return Levenshtein.distance(a, b)
except ImportError: Levenshtein = None
def ed_py(a, b):
    d = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        p, d[0] = d[0], i
        for j, y in enumerate(b, 1): p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (x != y))
    return d[-1]
if Levenshtein is None: ed = ed_py
hyp = lambda f: {json.loads(l)["id"]: json.loads(l)["hyp"] for l in open(f)} if os.path.exists(f) else {}
ctc = hyp(f"{W}/rows-ctc.jsonl"); llm = {**hyp(f"{W}/rows-llm-0.jsonl"), **hyp(f"{W}/rows-llm-1.jsonl")}
kept = Counter(); n = 0
with open(f"{W}/redraft.jsonl", "w") as f:
    for r in ins:
        if r["id"] not in ctc or r["id"] not in llm: continue
        a, c = norm(llm[r["id"]]), norm(ctc[r["id"]]); ag = ed(a, c) / max(1, len(a)) if a else 1.0
        f.write(json.dumps({"audio": os.path.basename(r["path"]), "file": r["file"], "dur": round(r["dur"], 2), "text": a, "ctc": c,
                            "agree": round(ag, 4)}, ensure_ascii=False) + "\n"); n += 1
        for th in (0.05, 0.10, 0.15): kept[str(th)] += r["dur"] * (ag <= th)
save("merged", {"segments": n, "hours": round(sum(r["dur"] for r in ins if r["id"] in ctc and r["id"] in llm) / 3600, 1),
                "kept_hours": {k: round(v / 3600, 1) for k, v in kept.items()}})
save("elapsed_h", round((time.time() - START) / 3600, 2))
print("DONE", flush=True)
