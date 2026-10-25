# K10 three-ear vote (team, CPU only). Ears on every VOA train segment of team/deng-voa-kurmanji-v1:
#   CTC  = Omnilingual CTC 1B v2 (team k7-redraft, all 46,201; dataset team/deng-voa-k7-redraft rows-ctc.jsonl)
#   LLM  = norm1, our trained ear (k7-redraft, 31,768 of them; redraft.jsonl "text")
#   WH   = Whisper-kmr (this account's k9-whisper, rows-whisper-*.jsonl)
# Each segment gets the three pairwise disagreements (CER after one shared plain normaliser) and a label choice:
#   if LLM exists and agrees with CTC or WH within th -> LLM text; else if WH agrees with CTC within th -> WH text.
# Kept hours are reported for th = 0.05 / 0.10 / 0.15; the threshold for training is chosen from these numbers, not
# here. Output: labels-v4.jsonl (audio, file, dur, ctc, llm, wh, d_llm_ctc, d_llm_wh, d_wh_ctc), stats.json.
import os, re, json, glob, time, hashlib, subprocess, unicodedata
from collections import Counter
START = time.time()
DEADLINE_S = 2 * 3600
W = "/kaggle/working"
STATS = {}
def save(key, val):
    STATS[key] = val; json.dump(STATS, open(f"{W}/stats.json", "w"), indent=1, ensure_ascii=False)
    print("STAT", key, json.dumps(val, ensure_ascii=False)[:300], flush=True)
subprocess.run("pip install -q rapidfuzz", shell=True, timeout=900)
from rapidfuzz.distance import Levenshtein
def norm(t):
    t = unicodedata.normalize("NFC", (t or "").lower().replace("’", "").replace("'", ""))
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", re.sub(r"[—–‐-]", " ", t))).strip()
def d(a, b):
    if a is None or b is None: return None
    return round(Levenshtein.distance(a, b) / max(1, len(b)), 4)

# the k7-redraft order, rebuilt exactly as in k9 (ids s00000..)
MAN = glob.glob("/kaggle/input/**/manifest.jsonl", recursive=True)[0]
rows = [json.loads(l) for l in open(MAN)]
pick = [r for r in rows if r["split"] == "train"]
h = lambda r: hashlib.md5(r["file"].encode()).hexdigest()
pick.sort(key=lambda r: (h(r), r["start"]))
ins = [{"id": f"s{i:05d}", "r": r, "dur": r["end"] - r["start"]} for i, r in enumerate(pick) if r["end"] - r["start"] <= 39.5]
ins = [x for i in range(0, len(ins), 400) for x in sorted(ins[i:i + 400], key=lambda r: -r["dur"])]
save("order", {"segments": len(ins), "matches_k7": len(ins) == 46201})

def load(pattern, key="hyp"):
    out = {}
    for f in glob.glob(f"/kaggle/input/**/{pattern}", recursive=True):
        for l in open(f):
            r = json.loads(l); out[r["id"]] = r[key]
    return out
ctc = load("rows-ctc.jsonl"); wh = load("rows-whisper-*.jsonl")
red = {}
for f in glob.glob("/kaggle/input/**/redraft.jsonl", recursive=True):
    for l in open(f): r = json.loads(l); red[r["audio"]] = r["text"]
save("ears", {"ctc": len(ctc), "llm": len(red), "whisper": len(wh)})

kept = {th: Counter() for th in (0.05, 0.10, 0.15)}
n = 0
with open(f"{W}/labels-v4.jsonl", "w") as f:
    for x in ins:
        if time.time() - START > DEADLINE_S - 600: save("stopped_at_deadline", n); break
        c = norm(ctc.get(x["id"])) if x["id"] in ctc else None
        l = red.get(x["r"]["audio"])
        w = norm(wh.get(x["id"])) if x["id"] in wh else None
        row = {"id": x["id"], "audio": x["r"]["audio"], "file": x["r"]["file"], "dur": round(x["dur"], 2), "ctc": c, "llm": l, "wh": w,
               "d_llm_ctc": d(c, l), "d_llm_wh": d(w, l), "d_wh_ctc": d(c, w)}
        f.write(json.dumps(row, ensure_ascii=False) + "\n"); n += 1
        for th, k in kept.items():
            if l and ((row["d_llm_ctc"] is not None and row["d_llm_ctc"] <= th) or (row["d_llm_wh"] is not None and row["d_llm_wh"] <= th)):
                k["llm"] += x["dur"]
            elif w and row["d_wh_ctc"] is not None and row["d_wh_ctc"] <= th:
                k["whisper"] += x["dur"]
save("rows", n)
save("kept_hours", {str(th): {k: round(v / 3600, 1) for k, v in c.items()} | {"total": round(sum(c.values()) / 3600, 1)} for th, c in kept.items()})
save("elapsed_min", round((time.time() - START) / 60, 1))
print("DONE", flush=True)
