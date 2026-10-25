# V3 open VOA labels v4 (team, CPU only; public notebook, its output is the release). Rebuilds the label file of the
# public set team/deng-voa-kurmanji-v1 from the three-ear vote (team/deng-k10-uc-kulak, labels-v4.jsonl);
# the audio shards are not rebuilt (same audio names as v1). One row per VOA train segment:
#   text = the ear rule (veri/egitime-giris-kurallari.md 4): the LLM text if it agrees with CTC or Whisper within 0.10,
#          else the Whisper text if it agrees with CTC within 0.10, else empty (no label);
#   all three ear texts and the three pairwise disagreements stay in the row, so a user can choose another threshold.
# VOA-produced audio is public domain (credited as in v1); the labels are machine drafts, not human transcripts (README).
# Output (/kaggle/working): labels-v4.jsonl, README.md, stats.json.
import os, json, glob, time
START = time.time()
DEADLINE_S = 1 * 3600
W = "/kaggle/working"
STATS = {}
def save(key, val):
    STATS[key] = val; json.dump(STATS, open(f"{W}/stats.json", "w"), indent=1, ensure_ascii=False)
    print("STAT", key, json.dumps(val, ensure_ascii=False)[:300], flush=True)
TH = 0.10
man = {}
for l in open(glob.glob("/kaggle/input/**/manifest.jsonl", recursive=True)[0]):
    r = json.loads(l); man[r["audio"]] = r
save("manifest", len(man))
n = lab = 0; hours = 0.0; by_ear = {"llm": 0, "wh": 0, "none": 0}
with open(f"{W}/labels-v4.jsonl", "w") as f:
    for l in open(glob.glob("/kaggle/input/**/labels-v4.jsonl", recursive=True)[0]):
        if time.time() - START > DEADLINE_S - 600: save("stopped_at_deadline", n); break
        r = json.loads(l); m = man.get(r["audio"], {})
        text, ear = "", "none"
        ds = [x for x in (r.get("d_llm_ctc"), r.get("d_llm_wh")) if x is not None]
        if r.get("llm") and ds and min(ds) <= TH: text, ear = r["llm"], "llm"
        elif r.get("wh") and r.get("d_wh_ctc") is not None and r["d_wh_ctc"] <= TH: text, ear = r["wh"], "wh"
        row = {"audio": r["audio"], "shard": m.get("shard"), "file": r["file"], "start": m.get("start"), "end": m.get("end"), "dur": r["dur"],
               "quality": m.get("quality"), "text": text, "ear": ear,
               "llm": r.get("llm"), "whisper": r.get("wh"), "ctc": r.get("ctc"),
               "d_llm_ctc": r.get("d_llm_ctc"), "d_llm_whisper": r.get("d_llm_wh"), "d_whisper_ctc": r.get("d_wh_ctc")}
        f.write(json.dumps(row, ensure_ascii=False) + "\n"); n += 1; by_ear[ear] += 1
        if text: lab += 1; hours += r["dur"]
save("labels", {"rows": n, "labelled": lab, "labelled_hours": round(hours / 3600, 1), "by_ear": by_ear, "threshold": TH})
open(f"{W}/README.md", "w").write(f"""# Deng: Dengê Amerîka Kurmancî, nîşan v4 · labels v4

**Kurdî.** Ev pel nîşanên (nivîsên) beşên perwerdeyê yên komkirina `team/deng-voa-kurmanji-v1` in. Deng ne hatine guhertin.
Nivîs ji aliyê sê guhên makîneyê ve hatine nivîsandin (modela me, Whisper û CTC); heke du guh nêzîkî hev bin (ferqa tîpan
≤ {TH}) nivîs tê girtin. Ev nivîsên makîneyê ne, ne yên mirovan: xelet hene. Stûnên `llm`, `whisper`, `ctc` û ferqên wan di
her rêzê de hene, da ku hûn sînorekî din hilbijêrin.

**English.** Labels for the train segments of `team/deng-voa-kurmanji-v1` (audio unchanged; join on `audio`).
Text comes from a vote of three machine ears (our Omnilingual-based model, Whisper-kmr, Omnilingual CTC 1B): kept when two
ears agree within a character error rate of {TH}; otherwise `text` is empty. These are machine drafts, not human
transcripts. Every row keeps all three ear texts and their pairwise disagreements so you can choose another threshold.

- rows: {n} · labelled: {lab} ({round(hours / 3600, 1)} h) · by ear: {by_ear}
- Audio: courtesy of Voice of America (dengeamerika.com); VOA-produced material is public domain. Code and rules: github.com/marmarok/deng
""")
save("elapsed_min", round((time.time() - START) / 60, 1))
print("DONE", flush=True)
