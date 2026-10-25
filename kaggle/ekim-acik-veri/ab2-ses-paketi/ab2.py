# AB2 voice package list (team, CPU only). The label half of the pre-registered voice rule
# (veri/egitime-giris-kurallari.md 5), joined to ab1's audio half:
#   audio half (team/deng-ab1-speakers, spk.jsonl): quality A or B, 3-20 s, a single speaker, speaker cluster id;
#   label half (team/deng-k10-uc-kulak, labels-v4.jsonl): three-ear agreement <= 0.05 (stricter than the ear's
#     0.10): the LLM text if it agrees with CTC or Whisper within 0.05, else the Whisper text if it agrees with CTC;
#   speaker share: no speaker above 10% of the voice hours (per-speaker cap found by bisection, as in ab1); inside a
#     speaker, quality A first, then the closest agreement.
# Punctuation and the ambiguous-question filter run at the start of the voice trial, not here.
# Output (/kaggle/working): voice-v1.jsonl (audio, shard, file, start, end, dur, quality, spk, text, ear, agree), stats.json.
import os, json, glob, time
from collections import defaultdict
START = time.time()
DEADLINE_S = 1 * 3600
W = "/kaggle/working"
STATS = {}
def save(key, val):
    STATS[key] = val; json.dump(STATS, open(f"{W}/stats.json", "w"), indent=1, ensure_ascii=False)
    print("STAT", key, json.dumps(val, ensure_ascii=False)[:300], flush=True)
TH = 0.05
spk = {}
for l in open(glob.glob("/kaggle/input/**/spk.jsonl", recursive=True)[0]):
    r = json.loads(l)
    if r.get("single") and r.get("spk") and r.get("quality") in ("A", "B") and 3 <= r["dur"] <= 20: spk[r["audio"]] = r
save("audio_half", {"segments": len(spk), "hours": round(sum(r["dur"] for r in spk.values()) / 3600, 2)})
lab, n = {}, 0
for l in open(glob.glob("/kaggle/input/**/labels-v4.jsonl", recursive=True)[0]):
    if time.time() - START > DEADLINE_S - 600: save("stopped_at_deadline", n); break
    r = json.loads(l); n += 1
    if r["audio"] not in spk: continue
    pick = None
    if r.get("llm"):
        ds = [x for x in (r.get("d_llm_ctc"), r.get("d_llm_wh")) if x is not None]
        if ds and min(ds) <= TH: pick = ("llm", r["llm"], min(ds))
    if pick is None and r.get("wh") and r.get("d_wh_ctc") is not None and r["d_wh_ctc"] <= TH: pick = ("wh", r["wh"], r["d_wh_ctc"])
    if pick: lab[r["audio"]] = pick
save("label_half", {"rows_read": n, "agree_le_0.05": len(lab), "hours": round(sum(spk[a]["dur"] for a in lab) / 3600, 2)})
by = defaultdict(list)
for a, (ear, text, ag) in lab.items(): by[spk[a]["spk"]].append((spk[a], ear, text, ag))
h = {s: sum(x[0]["dur"] for x in v) / 3600 for s, v in by.items()}
lo, hi = 0.0, max(h.values()) if h else 0.0
for _ in range(60):
    c = (lo + hi) / 2
    if c <= 0.1 * sum(min(v, c) for v in h.values()): lo = c
    else: hi = c
out, per = [], {}
for s, v in by.items():
    v.sort(key=lambda x: (x[0]["quality"] != "A", x[3])); acc = 0.0
    for r, ear, text, ag in v:
        if acc + r["dur"] / 3600 > lo + 1e-9: break
        out.append({k: r.get(k) for k in ("audio", "shard", "file", "start", "end", "dur", "quality", "spk")} | {"text": text, "ear": ear, "agree": ag}); acc += r["dur"] / 3600
    per[s] = round(acc, 3)
with open(f"{W}/voice-v1.jsonl", "w") as f:
    for r in out: f.write(json.dumps(r, ensure_ascii=False) + "\n")
tot = sum(r["dur"] for r in out) / 3600
top = sorted(per.items(), key=lambda x: -x[1])[:10]
save("voice_package", {"segments": len(out), "hours": round(tot, 2), "speakers": len(per), "cap_per_speaker_h": round(lo, 3),
                       "max_share": round(top[0][1] / tot, 3) if tot else None, "top10": top,
                       "by_quality_h": {q: round(sum(r["dur"] for r in out if r["quality"] == q) / 3600, 2) for q in ("A", "B")},
                       "by_ear": {e: sum(1 for r in out if r["ear"] == e) for e in ("llm", "wh")}})
save("elapsed_min", round((time.time() - START) / 60, 1))
print("DONE", flush=True)
