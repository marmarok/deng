# K6 measurement (team, 2xT4): can a second, different model certify the base LLM 1B drafts of the VOA archive?
# Text anchoring (k6-align-diag, 18.10) labelled only 0.34 h of 207 h: interview pages are summaries, not transcripts.
# Plan B is agreement filtering: transcribe the same segments with Omnilingual CTC models (non-autoregressive, a
# different decoder, so their errors are only partly shared with the LLM) and keep the segments where both agree.
# This run measures, on a ~3 h random sample of drafted VOA audio (interviews and guest talks, the drafted sections):
#   - CTC 1B v2 (GPU 0) and CTC 3B v2 (GPU 1): speed on a T4 (x real time), load time, peak memory;
#   - agreement = character error rate between the normalized LLM draft and each CTC output: hours per bin and section;
#   - calibration against known references: FLEURS-Kobani test (read speech, public) and the 111 VOA segments whose
#     article text matched in k6-align-diag (biased toward easy segments). For each agreement threshold: how much is
#     accepted, and how wrong the LLM text of the accepted part really is. The base LLM 1B also transcribes FLEURS test
#     (half per GPU) for this.
# Outputs: stats.json (rewritten after every stage), rows-*.jsonl (hypotheses per segment), examples.jsonl.
# Safety: one deadline (3 h) checked in every loop; every subprocess and network read has a timeout.
import os, re, sys, io, json, glob, time, types, random, shutil, signal, socket, threading, subprocess, urllib.request
from collections import defaultdict
import soundfile as sf
import pyarrow.parquet as pq
socket.setdefaulttimeout(120)  # every network read times out
START = time.time()
DEADLINE_S = 3 * 3600
PREP_STOP = START + 75 * 60              # CPU preparation must be done by then
CTC_STOP = START + DEADLINE_S - 50 * 60  # CTC passes stop here; the LLM calibration pass follows
LLM_STOP = START + DEADLINE_S - 15 * 60  # every GPU pass stops here; leaves time for scoring
W = "/kaggle/working"; T = "/kaggle/temp"; SEG = f"{T}/seg"
os.makedirs(SEG, exist_ok=True)
SAMPLE_HOURS = {"hevpeyvin": 2.2, "mevan-u-mijar": 0.8}
CTC = {0: ("omniASR_CTC_1B_v2", 16), 1: ("omniASR_CTC_3B_v2", 4)}  # card, batch (3B ran out of memory at 16 in K2)
LLM = "omniASR_LLM_1B_v2"
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

# ---------- CPU preparation (thread): FLEURS test, matched VOA segments, random VOA sample ----------
lists = {}
def wav16(src, dst):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-ac", "1", "-ar", "16000", dst], timeout=900, check=True)
def cut(src, segs, prefix):
    """Decode one archive file once, write each segment as a 16 kHz mono wav. Returns (segment, path, seconds)."""
    stem = re.sub(r"[^\w.-]", "_", os.path.basename(src)).rsplit(".", 1)[0]; wav = f"{T}/{stem}.wav"
    try:
        wav16(src, wav); data, rate = sf.read(wav, dtype="int16")
    except Exception as ex:
        with LOCK: STATS.setdefault("bad_files", []).append([os.path.basename(src), repr(ex)[:150]])
        return []
    finally:
        if os.path.exists(wav): os.remove(wav)
    out = []
    for s in sorted(segs, key=lambda s: s["start"]):
        a, b = int(s["start"] * rate), min(int(s["end"] * rate), len(data))
        if b - a < rate: continue
        p = f"{SEG}/{prefix}-{stem}-{int(s['start'] * 100):08d}.wav"
        sf.write(p, data[a:b], rate); out.append((s, p, (b - a) / rate))
    return out
def prepare():
    ctx = {}
    def inputs():
        paths = {}
        for f in glob.glob("/kaggle/input/**/items.jsonl", recursive=True):
            root = os.path.join(os.path.dirname(f), "audio")
            for l in open(f):
                x = json.loads(l); p = f"{root}/{x['file']}"
                if os.path.exists(p): paths[x["file"]] = p
        drafts = {}
        for f in sorted(glob.glob("/kaggle/input/**/draft-*.jsonl", recursive=True)):
            for l in open(f):
                try: r = json.loads(l)
                except json.JSONDecodeError: continue
                drafts[(r["file"], r["start"])] = r  # a file cut by a worker crash appears twice; the last row wins
        by_file = defaultdict(list)
        for r in drafts.values():
            if r["file"] in paths and r["end"] - r["start"] >= 1.0: by_file[r["file"]].append(r)
        sec_hours = defaultdict(float)
        for r in drafts.values(): sec_hours[r.get("section", "?")] += (r["end"] - r["start"]) / 3600
        save("inputs", {"archive_files": len(paths), "drafted_files": len(by_file), "draft_segments": len(drafts),
                        "draft_hours_by_section": {k: round(v, 1) for k, v in sorted(sec_hours.items())}})
        ctx["paths"], ctx["by_file"] = paths, by_file
    def fleurs():
        # FLEURS-Kobani test (public, CC BY): read speech with references
        rows = []
        urls = json.load(urllib.request.urlopen("https://huggingface.co/api/datasets/aranemini/northern-kurdish-fleurs/parquet/default/test", timeout=60))
        for i, u in enumerate(urls):
            pq_path = f"{T}/fleurs-test-{i}.parquet"
            with urllib.request.urlopen(u, timeout=120) as r, open(pq_path, "wb") as f: shutil.copyfileobj(r, f)
            for x in pq.read_table(pq_path, columns=["audio", "kurdish"]).to_pylist():
                if time.time() > PREP_STOP: break
                data, rate = sf.read(io.BytesIO(x["audio"]["bytes"]), dtype="float32")
                if data.ndim > 1: data = data.mean(1)
                p = f"{SEG}/f{len(rows):04d}.wav"
                if rate != 16000:
                    sf.write(p + ".src.wav", data, rate); wav16(p + ".src.wav", p); os.remove(p + ".src.wav")
                else: sf.write(p, data, 16000)
                rows.append({"id": f"f{len(rows):04d}", "path": p, "dur": round(len(data) / rate, 2), "ref": x["kurdish"]})
            os.remove(pq_path)
        lists["fleurs"] = rows
        save("prep_fleurs", {"clips": len(rows), "hours": round(sum(r["dur"] for r in rows) / 3600, 2)})
    def aligned():
        paths = ctx["paths"]
        # the VOA segments whose article text matched (label written by a person, LLM draft known)
        groups = defaultdict(list)
        for f in glob.glob("/kaggle/input/**/selected.jsonl", recursive=True):
            for l in open(f): s = json.loads(l); groups[s["file"]].append(s)
        rows = []
        for file, segs in sorted(groups.items()):
            if time.time() > PREP_STOP or file not in paths: continue
            for s, p, dur in cut(paths[file], segs, "a"):
                rows.append({"id": f"a{len(rows):04d}", "path": p, "dur": round(dur, 2), "ref": s["label"], "llm": s["hyp"],
                             "file": file, "section": s["section"]})
        lists["aligned"] = rows
        save("prep_aligned", {"segments": len(rows), "hours": round(sum(r["dur"] for r in rows) / 3600, 2)})
    def sample():
        paths, by_file = ctx["paths"], ctx["by_file"]
        # random drafted files per section until the target hours are reached
        rng = random.Random(6); rows = []; got = defaultdict(float); nfiles = defaultdict(int)
        for sec, hours in SAMPLE_HOURS.items():
            files = sorted(f for f, rs in by_file.items() if rs[0].get("section") == sec); rng.shuffle(files)
            for file in files:
                if got[sec] >= hours * 3600 or time.time() > PREP_STOP: break
                nfiles[sec] += 1
                for s, p, dur in cut(paths[file], by_file[file], "s"):
                    rows.append({"id": f"s{len(rows):05d}", "path": p, "dur": round(dur, 2), "llm": s["hyp"], "file": file,
                                 "section": sec, "start": s["start"], "end": s["end"]})
                    got[sec] += dur
        lists["sample"] = rows
        save("prep_sample", {"segments": len(rows), "files": dict(nfiles), "hours": {k: round(v / 3600, 2) for k, v in got.items()},
                             "minutes": round((time.time() - START) / 60, 1)})
    # the sample is the point of this run, so it goes right after the inputs; each stage fails on its own
    for name, fn in (("inputs", inputs), ("sample", sample), ("aligned", aligned), ("fleurs", fleurs)):
        try: fn()
        except Exception as ex: save(f"prep_error_{name}", repr(ex)[:500])
    lists["done"] = True
threading.Thread(target=prepare, daemon=True).start()

# ---------- Omnilingual env (Python 3.12, same pins as K5/G2), normalizer source ----------
run("pip install -q uv", 600)
OMNI = f"{T}/omni"; PY = f"{OMNI}/bin/python"
code, sec = run(f"UV_PYTHON_DOWNLOADS=automatic uv venv --managed-python -p 3.12 {OMNI} && uv pip install --python {PY} -q omnilingual-asr torch==2.8.0 torchaudio==2.8.0 soundfile 'numpy<2' 'pyarrow==20.0.0'", 1500)
save("env", {"exit": code, "seconds": sec})
run(f"cd {T} && git clone -q --depth 1 https://github.com/facebookresearch/omnilingual-asr.git oa", 300)

# ---------- each model downloaded once, one after another (two loaders at once collided in g2-diag) ----------
open(f"{T}/warm.py", "w").write("import sys, torch\nfrom omnilingual_asr.models.inference.pipeline import ASRInferencePipeline\n"
                                "ASRInferencePipeline(model_card=sys.argv[1], device='cuda', dtype=torch.float16)\nprint('WARM_OK', flush=True)\n")
warm = {}
for card in (CTC[0][0], CTC[1][0], LLM):
    code, sec = run(f"CUDA_VISIBLE_DEVICES=0 {PY} {T}/warm.py {card}", 30 * 60, log=f"{W}/warm-{card}.log")
    warm[card] = {"exit": code, "seconds": sec}
    save("warm", warm)
while not lists.get("done") and time.time() < PREP_STOP + 5 * 60: time.sleep(10)

# ---------- GPU passes: GPU g runs its CTC model over FLEURS + matched + sample, then the LLM over FLEURS[g::2] ----------
open(f"{T}/worker.py", "w").write(r'''
import sys, json, time, faulthandler, torch
faulthandler.enable()
from omnilingual_asr.models.inference.pipeline import ASRInferencePipeline
card, src, out, stop_at, bs = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), int(sys.argv[5])
rows = [json.loads(l) for l in open(src)]
t0 = time.time(); p = ASRInferencePipeline(model_card=card, device="cuda", dtype=torch.float16); load_s = time.time() - t0
kw = (lambda n: {"lang": ["kmr_Latn"] * n}) if "LLM" in card else (lambda n: {})
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
def write(name, rows):
    with open(f"{T}/{name}.jsonl", "w") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
MAX_DUR = 39.5  # the inference pipeline refuses audio over 40 s (agree-diag v1 died on the first batch)
fits = lambda xs: [r for r in xs if r["dur"] <= MAX_DUR]
save("dropped_over_40s", {k: sum(1 for r in lists.get(k, []) if r["dur"] > MAX_DUR) for k in ("fleurs", "aligned", "sample")})
fl, al, sm = fits(lists.get("fleurs", [])), fits(lists.get("aligned", [])), fits(lists.get("sample", []))
by_dur = lambda xs: sorted(xs, key=lambda r: -r["dur"])  # less padding per batch
write("ctc-in", by_dur(fl) + by_dur(al) + by_dur(sm))
for g in (0, 1): write(f"llm-in-{g}", by_dur(fl[g::2]))
def chain(g):
    card, bs = CTC[g]
    for attempt_bs in (bs, max(1, bs // 4)):  # one retry with a smaller batch if the first try died early (e.g. out of memory)
        code, sec = run(f"CUDA_VISIBLE_DEVICES={g} {PY} {T}/worker.py {card} {T}/ctc-in.jsonl {W}/rows-{card}.jsonl {CTC_STOP} {attempt_bs}",
                        CTC_STOP - time.time() + 300, log=f"{W}/worker-{g}-ctc.log")
        done = sum(1 for _ in open(f"{W}/rows-{card}.jsonl")) if os.path.exists(f"{W}/rows-{card}.jsonl") else 0
        save(f"pass_{card}", {"exit": code, "seconds": sec, "rows": done, "batch": attempt_bs})
        if code == 0 or done >= 50 or time.time() > CTC_STOP - 20 * 60: break
    code, sec = run(f"CUDA_VISIBLE_DEVICES={g} {PY} {T}/worker.py {LLM} {T}/llm-in-{g}.jsonl {W}/rows-{LLM}-{g}.jsonl {LLM_STOP} 4",
                    LLM_STOP - time.time() + 300, log=f"{W}/worker-{g}-llm.log")
    save(f"pass_{LLM}_{g}", {"exit": code, "seconds": sec})
threads = [threading.Thread(target=chain, args=(g,), daemon=True) for g in (0, 1)]
for t in threads: t.start()
for t in threads: t.join(timeout=max(60, left() - 10 * 60))

# ---------- scoring ----------
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
try:
    from rapidfuzz.distance import Levenshtein
    def ed(a, b): return Levenshtein.distance(a, b)
except ImportError:
    def ed(a, b):
        d = list(range(len(b) + 1))
        for i, x in enumerate(a, 1):
            prev, d[0] = d[0], i
            for j, y in enumerate(b, 1): prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (x != y))
        return d[-1]
def hyps(path_glob):
    out = {}
    for f in glob.glob(path_glob):
        for l in open(f):
            try: r = json.loads(l); out[r["id"]] = norm(r["hyp"])
            except (json.JSONDecodeError, KeyError): pass
    return out
H1, H3 = hyps(f"{W}/rows-{CTC[0][0]}.jsonl"), hyps(f"{W}/rows-{CTC[1][0]}.jsonl")
HL = hyps(f"{W}/rows-{LLM}-*.jsonl")
def rate(ref, hyp): return ed(ref, hyp) / max(1, len(ref))
speed = {}
for f in glob.glob(f"{W}/rows-*.jsonl.meta.json"):
    m = json.load(open(f)); m["x_real_time"] = round(m["audio_s"] / max(1.0, m["wall_s"]), 1); speed[re.sub(r"^rows-|\.jsonl\.meta\.json$", "", os.path.basename(f))] = m
save("speed", speed)

# VOA sample: agreement of each CTC output with the LLM draft, hours per bin and section, yield per threshold
BINS = [0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 9.0]
def bin_of(x): return next((f"<={b:.2f}" for b in BINS[:-1] if x <= b), ">0.30")
agree = {"ctc1b": defaultdict(lambda: defaultdict(float)), "ctc3b": defaultdict(lambda: defaultdict(float))}
yield_h = defaultdict(lambda: defaultdict(float)); total_h = defaultdict(float); examples = []
for r in sm:
    L = norm(r["llm"]); h = r["dur"] / 3600; sec = r["section"]
    a1 = rate(L, H1[r["id"]]) if r["id"] in H1 else None; a3 = rate(L, H3[r["id"]]) if r["id"] in H3 else None
    if a1 is None: continue  # CTC 1B did not reach this segment
    total_h[sec] += h; total_h["all"] += h
    agree["ctc1b"][sec][bin_of(a1)] += h
    if a3 is not None: agree["ctc3b"][sec][bin_of(a3)] += h
    for t in (0.05, 0.10, 0.15):
        for key, ok in ((f"ctc1b<={t}", a1 <= t), (f"ctc3b<={t}", a3 is not None and a3 <= t),
                        (f"both<={t}", a3 is not None and a1 <= t and a3 <= t)):
            if ok: yield_h[key][sec] += h; yield_h[key]["all"] += h
    if len(examples) < 80 and random.random() < 0.15:
        examples.append({"kind": "voa", "file": r["file"], "start": r["start"], "llm": L, "ctc1b": H1.get(r["id"]), "ctc3b": H3.get(r["id"]),
                         "agree_1b": round(a1, 3), "agree_3b": None if a3 is None else round(a3, 3)})
save("voa_sample", {"hours_scored": {k: round(v, 2) for k, v in total_h.items()},
                    "agreement_hours": {m: {s: {b: round(v, 2) for b, v in sorted(d.items())} for s, d in x.items()} for m, x in agree.items()},
                    "accepted_hours": {k: {s: round(v, 2) for s, v in d.items()} for k, d in sorted(yield_h.items())},
                    "accepted_share": {k: round(d["all"] / max(1e-9, total_h["all"]), 3) for k, d in sorted(yield_h.items())}})

# calibration: true error of the LLM text among clips accepted at each threshold
def calibrate(rows, llm_of, name):
    out = {}; base = []
    for r in rows:
        ref = norm(r["ref"]); L = llm_of(r)
        if not ref or L is None or r["id"] not in H1: continue
        base.append((r, ref, L, rate(L, H1[r["id"]]), rate(L, H3[r["id"]]) if r["id"] in H3 else None))
    if not base: return save(f"calib_{name}", {"clips": 0})
    def score(sel):
        c = sum(ed(ref, L) for _, ref, L, _, _ in sel) / max(1, sum(len(ref) for _, ref, _, _, _ in sel))
        w = sum(ed(ref.split(), L.split()) for _, ref, L, _, _ in sel) / max(1, sum(len(ref.split()) for _, ref, _, _, _ in sel))
        return {"clips": len(sel), "share_hours": round(sum(r["dur"] for r, *_ in sel) / max(1e-9, sum(r["dur"] for r, *_ in base)), 3),
                "llm_cer": round(100 * c, 2), "llm_wer": round(100 * w, 2)}
    out["all"] = score(base)
    for model in ("ctc1b", "ctc3b", "both"):
        for t in (0.02, 0.05, 0.10, 0.15, 0.20):
            sel = [x for x in base if (model == "ctc1b" and x[3] <= t) or (model == "ctc3b" and x[4] is not None and x[4] <= t)
                   or (model == "both" and x[4] is not None and x[3] <= t and x[4] <= t)]
            if sel: out[f"{model}<={t}"] = score(sel)
    for key, H in (("ctc1b_alone", H1), ("ctc3b_alone", H3)):
        sel = [(r, ref, H[r["id"]]) for r, ref, *_ in base if r["id"] in H]
        if sel: out[key] = {"cer": round(100 * sum(ed(ref, h) for _, ref, h in sel) / max(1, sum(len(ref) for _, ref, _ in sel)), 2), "clips": len(sel)}
    save(f"calib_{name}", out)
    for r, ref, L, a1, a3 in base[:20]:
        examples.append({"kind": name, "ref": ref, "llm": L, "ctc1b": H1.get(r["id"]), "ctc3b": H3.get(r["id"]), "agree_1b": round(a1, 3)})
calibrate(fl, lambda r: HL.get(r["id"]), "fleurs")
calibrate(al, lambda r: norm(r["llm"]), "voa_matched")
with open(f"{W}/examples.jsonl", "w") as f:
    for e in examples: f.write(json.dumps(e, ensure_ascii=False) + "\n")
save("elapsed_h", round((time.time() - START) / 3600, 2))
print("DONE", flush=True)
