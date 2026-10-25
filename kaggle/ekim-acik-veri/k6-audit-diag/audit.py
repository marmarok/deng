# K6 language gate, human audit clips (team, CPU). Pre-registered in veri/egitime-giris-kurallari.json:
# audio threshold picked by the rule = 0.2 (control-kmr recall 0.96; tur/arb/eng false accept 0.0), text = GlotLID top-1.
# From k6-lid-diag rows (interview + guest sections only; video is out of the public scope) draw 20 segments the gate
# accepts and 20 it rejects, cut each to a short mp3 and shuffle them, so the listener does not know which is which.
# Outputs: clips/<n>.mp3, listen.jsonl (n, duration, no labels), key.jsonl (n -> id, accepted, mms_top, p).
import os, json, glob, time, random, signal, subprocess
START = time.time()
DEADLINE_S = 3600
W = "/kaggle/working"; os.makedirs(f"{W}/clips", exist_ok=True)
TH = 0.2
rows = [json.loads(l) for l in open(glob.glob("/kaggle/input/**/deng-k6-lid-diag/**/rows.jsonl", recursive=True)[0] if glob.glob("/kaggle/input/**/deng-k6-lid-diag/**/rows.jsonl", recursive=True) else glob.glob("/kaggle/input/**/rows.jsonl", recursive=True)[0])]
paths = {}
for f in glob.glob("/kaggle/input/**/items.jsonl", recursive=True):
    root = os.path.join(os.path.dirname(f), "audio")
    for l in open(f):
        x = json.loads(l); p = f"{root}/{x['file']}"
        if os.path.exists(p): paths[x["file"]] = p
voa = [r for r in rows if r["section"] in ("hevpeyvin", "mevan-u-mijar") and r["file"] in paths]
ok = lambda r: r["mms_kmr_p"] >= TH and r["glot_top"] == "kmr_Latn"
rng = random.Random(18)
pick = []
for sec in ("hevpeyvin", "mevan-u-mijar"):
    for want in (True, False):
        pool = [r for r in voa if r["section"] == sec and ok(r) == want]
        pick += rng.sample(pool, min(10, len(pool)))
rng.shuffle(pick)
key, listen = [], []
for n, r in enumerate(pick, 1):
    if time.time() - START > DEADLINE_S - 600: break
    dur = min(r["dur"], 15.0)
    try:
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(r["start"]), "-t", str(dur), "-i", paths[r["file"]],
                        "-ac", "1", "-ar", "22050", "-b:a", "48k", f"{W}/clips/{n:02d}.mp3"], timeout=300, check=True)
    except Exception as ex:
        print("cut failed", r["id"], repr(ex)[:200], flush=True); continue
    listen.append({"n": n, "dur": round(dur, 1)})
    key.append({"n": n, "id": r["id"], "section": r["section"], "file": r["file"], "start": r["start"], "accepted": ok(r),
                "mms_top": r["mms_top"], "mms_kmr_p": r["mms_kmr_p"], "glot_top": r["glot_top"], "draft": r["text"]})
with open(f"{W}/listen.jsonl", "w") as f:
    for x in listen: f.write(json.dumps(x) + "\n")
with open(f"{W}/key.jsonl", "w") as f:
    for x in key: f.write(json.dumps(x, ensure_ascii=False) + "\n")
print("DONE", len(listen), "clips", round(time.time() - START), "s", flush=True)
