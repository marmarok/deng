# S13 naturalness score backfill (team, 1xT4 is enough). UTMOS22 strong (SpeechMOS, MIT), the automatic naturalness
# score the single-speaker trials (s12) now report, run on this account's earlier voice outputs: s9-d2pub (seeds 11-12,
# 6 x 257 wav) and s11-temiz-ses (seeds 11-12, 6 x 257 wav). Human anchor: 200 FLEURS-Kobani test recordings (read speech,
# public). Same model and settings as s12, so all voice arms can be compared on one more axis. Output: utmos.json, rows.jsonl.
import os, io, json, glob, time, signal, subprocess
START = time.time()
DEADLINE_S = 2 * 3600
STOP = START + DEADLINE_S - 10 * 60
W = "/kaggle/working"; T = "/kaggle/temp"; os.makedirs(T, exist_ok=True)
def left(): return DEADLINE_S - (time.time() - START)
def run(cmd, limit, log=None):
    limit = max(60, min(limit, left() - 120)); t0 = time.time()
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
dirs = sorted(glob.glob("/kaggle/input/**/audio-t*-s[0-9]", recursive=True))
jobs = []
for d in dirs:
    src = "s11" if "s11-temiz-ses" in d else "s9b" if "s9-d2pub" in d else "other"
    jobs.append({"tag": f"{src}:{os.path.basename(d)[len('audio-'):]}", "dir": d})
json.dump(jobs, open(f"{T}/jobs.json", "w"))
print("dirs", len(dirs), [j["tag"] for j in jobs], flush=True)
run("pip install -q uv", 600)
VENV = f"{T}/u"; PY = f"{VENV}/bin/python"
code, sec = run(f"UV_PYTHON_DOWNLOADS=automatic uv venv --managed-python -p 3.12 {VENV} && uv pip install --python {PY} -q "
                f"torch==2.5.1 torchaudio==2.5.1 librosa soundfile pandas pyarrow huggingface_hub 'numpy<2'", 1500)
open(f"{T}/score.py", "w").write(r'''
import os, io, sys, json, glob, time, torch, librosa, soundfile as sf, pandas as pd
from huggingface_hub import hf_hub_download
jobs, W, stop_at = json.load(open(sys.argv[1])), sys.argv[2], float(sys.argv[3])
m = torch.hub.load("tarepan/SpeechMOS:v1.2.0", "utmos22_strong", trust_repo=True).eval().to("cuda")
def mos(d):
    if d is None or len(d) < 8000: return None
    with torch.no_grad(): return round(float(m(torch.from_numpy(d).float().unsqueeze(0).to("cuda"), 16000).item()), 3)
out, rows = {}, open(f"{W}/rows.jsonl", "w")
for j in jobs:
    vals = []
    for p in sorted(glob.glob(j["dir"] + "/*.wav")):
        if time.time() > stop_at: break
        d, sr = sf.read(p, dtype="float32", always_2d=False)
        if d.ndim > 1: d = d.mean(axis=1)
        if sr != 16000: d = librosa.resample(d, orig_sr=sr, target_sr=16000)
        v = mos(d)
        if v is not None: vals.append(v); rows.write(json.dumps({"tag": j["tag"], "file": os.path.basename(p), "utmos": v}) + "\n")
    out[j["tag"]] = {"n": len(vals), "utmos_mean": round(sum(vals) / max(1, len(vals)), 3)}
    json.dump(out, open(f"{W}/utmos.json", "w"), indent=1); rows.flush()
vals = []
import urllib.request
for k in range(2):  # the parquet API paths k5-prep2 uses (measured 18.10)
    pq = f"{W}/../temp/fleurs-test-{k}.parquet"
    open(pq, "wb").write(urllib.request.urlopen(f"https://huggingface.co/api/datasets/aranemini/northern-kurdish-fleurs/parquet/default/test/{k}.parquet", timeout=300).read())
    for _, r in pd.read_parquet(pq).iterrows():
        if len(vals) >= 200 or time.time() > stop_at: break
        d, sr = sf.read(io.BytesIO(r["audio"]["bytes"]), dtype="float32", always_2d=False)
        if d.ndim > 1: d = d.mean(axis=1)
        if sr != 16000: d = librosa.resample(d, orig_sr=sr, target_sr=16000)
        v = mos(d)
        if v is not None: vals.append(v)
out["human:fleurs_test"] = {"n": len(vals), "utmos_mean": round(sum(vals) / max(1, len(vals)), 3)}
json.dump(out, open(f"{W}/utmos.json", "w"), indent=1)
print("UTMOS_DONE", flush=True)
''')
code2, sec2 = run(f"CUDA_VISIBLE_DEVICES=0 {PY} {T}/score.py {T}/jobs.json {W} {STOP}", STOP - time.time() + 60, log=f"{W}/score.log")
json.dump({"env": [code, sec], "score": [code2, sec2], "elapsed_min": round((time.time() - START) / 60, 1)}, open(f"{W}/stats.json", "w"))
print("DONE", flush=True)
