# K6 language gate, measurement (team, CPU only: the GPU version waited >1 h in the queue): how much of the drafted VOA Kurdish archive is not Kurdish speech?
# The VOA archive comes from the Kurdish service, but interviews can contain Turkish/Arabic/English guests, voice-overs
# and music, and the drafts were written with the decoder told "kmr_Latn". Nothing from VOA enters training before this
# gate. Two independent checks per segment:
#   - audio: MMS-LID (facebook/mms-lid-4017, wav2vec2 classifier over 4017 languages), top label and P(kmr);
#   - text: GlotLID v3 (fastText) on the LLM draft, top label and P(kmr_Latn).
# Controls with known language (FLEURS test via the HF parquet API): Kurmanji (aranemini/northern-kurdish-fleurs) as the
# positive control, Turkish / Arabic / English (google/fleurs) as negatives. They show what each check gets wrong.
# Outputs: stats.json (rewritten after every stage), rows.jsonl (one line per segment), rejected-examples.jsonl.
# Safety: one deadline checked in every loop; every subprocess and network read has a timeout.
import os, re, io, json, glob, time, random, shutil, signal, socket, subprocess, urllib.request
from collections import defaultdict, Counter
socket.setdefaulttimeout(120)  # every network read times out
START = time.time()
DEADLINE_S = 3 * 3600
STOP_AT = START + DEADLINE_S - 15 * 60
W = "/kaggle/working"; T = "/kaggle/temp"; SEG = f"{T}/seg"
os.makedirs(SEG, exist_ok=True)
SAMPLE_PER_SECTION = 150
CONTROLS = {"kmr": ("aranemini/northern-kurdish-fleurs", "default", "test", "audio"),
            "tur": ("google/fleurs", "tr_tr", "test", "audio"),
            "arb": ("google/fleurs", "ar_eg", "test", "audio"),
            "eng": ("google/fleurs", "en_us", "test", "audio")}
CONTROL_CLIPS = 40
STATS = {}
def left(): return STOP_AT - time.time()
def save(key, val):
    STATS[key] = val; json.dump(STATS, open(f"{W}/stats.json", "w"), indent=1, ensure_ascii=False)
    print("STAT", key, json.dumps(val, ensure_ascii=False)[:300], flush=True)
def run(cmd, limit):
    limit = max(60, min(limit, left())); t0 = time.time()
    print("$", cmd[:300], flush=True)
    p = subprocess.Popen(cmd, shell=True, start_new_session=True)
    try: code = p.wait(timeout=limit)
    except subprocess.TimeoutExpired:
        for sig in (signal.SIGTERM, signal.SIGKILL):
            try: os.killpg(p.pid, sig)
            except ProcessLookupError: pass
            try: p.wait(timeout=60); break
            except subprocess.TimeoutExpired: pass
        code = "timeout"
    return code, round(time.time() - t0, 1)

code, sec = run("pip install -q fasttext-wheel", 900)
save("env", {"exit": code, "seconds": sec})
import numpy as np, soundfile as sf, torch, pyarrow.parquet as pq

def wav16(src, dst):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-ac", "1", "-ar", "16000", dst], timeout=900, check=True)


# ---------- inventory for the public data list: every VOA item and how much of it was drafted ----------
try:
    inv_items = {}
    for f in glob.glob("/kaggle/input/**/items.jsonl", recursive=True):
        for l in open(f):
            x = json.loads(l); inv_items[x["file"]] = {k: x.get(k) for k in ("file", "section", "url", "title", "date", "duration")}
    seen = {}
    for f in sorted(glob.glob("/kaggle/input/**/draft-*.jsonl", recursive=True)):
        for l in open(f):
            try: r = json.loads(l)
            except json.JSONDecodeError: continue
            seen[(r["file"], r["start"])] = r["end"] - r["start"]
    drafted = defaultdict(float)
    for (file, _), d in seen.items(): drafted[file] += d
    with open(f"{W}/inventory.jsonl", "w") as f:
        for x in sorted(inv_items.values(), key=lambda x: x.get("date") or ""):
            x["drafted_s"] = round(drafted.get(x["file"], 0.0), 1); f.write(json.dumps(x, ensure_ascii=False) + "\n")
    save("inventory", {"items": len(inv_items), "hours": round(sum((x.get("duration") or 0) for x in inv_items.values()) / 3600, 1),
                       "drafted_hours": round(sum(drafted.values()) / 3600, 1)})
except Exception as ex:
    save("inventory_error", repr(ex)[:300])

# ---------- VOA sample: random drafted files per section, a few segments per file ----------
rows = []
try:
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
            drafts[(r["file"], r["start"])] = r
    by_sec = defaultdict(lambda: defaultdict(list))
    for r in drafts.values():
        if r["file"] in paths and 1.0 <= r["end"] - r["start"] <= 39.5: by_sec[r.get("section", "?")][r["file"]].append(r)
    save("inputs", {"archive_files": len(paths), "draft_segments": len(drafts),
                    "files_by_section": {s: len(fs) for s, fs in by_sec.items()}})
    rng = random.Random(7)
    for sec, files in sorted(by_sec.items()):
        names = sorted(files); rng.shuffle(names); got = 0
        for name in names:
            if got >= SAMPLE_PER_SECTION or left() < 70 * 60: break
            segs = files[name]; pick = rng.sample(segs, min(4, len(segs)))  # few per file: spread over many files
            stem = re.sub(r"[^\w.-]", "_", name).rsplit(".", 1)[0]; wav = f"{T}/{stem}.wav"
            try:
                wav16(paths[name], wav); data, rate = sf.read(wav, dtype="float32")
            except Exception as ex:
                STATS.setdefault("bad_files", []).append([name, repr(ex)[:120]]); continue
            finally:
                if os.path.exists(wav): os.remove(wav)
            for s in pick:
                a, b = int(s["start"] * rate), min(int(s["end"] * rate), len(data))
                if b - a < rate: continue
                rows.append({"id": f"v{len(rows):05d}", "kind": "voa", "section": sec, "file": name, "start": s["start"],
                             "dur": round((b - a) / rate, 2), "text": s.get("hyp", ""), "audio": data[a:b]})
                got += 1
    save("prep_voa", {"segments": len(rows), "by_section": dict(Counter(r["section"] for r in rows)),
                      "minutes": round((time.time() - START) / 60, 1)})
except Exception as ex:
    save("prep_voa_error", repr(ex)[:500])

# ---------- controls with known language (each source fails on its own) ----------
for lang, (repo, cfg, split, col) in CONTROLS.items():
    try:
        urls = json.load(urllib.request.urlopen(f"https://huggingface.co/api/datasets/{repo}/parquet/{cfg}/{split}", timeout=60))
        n = 0
        for i, u in enumerate(urls):
            if n >= CONTROL_CLIPS or left() < 60 * 60: break
            pq_path = f"{T}/ctl-{lang}-{i}.parquet"
            with urllib.request.urlopen(u, timeout=300) as r, open(pq_path, "wb") as f: shutil.copyfileobj(r, f)
            tab = pq.read_table(pq_path, columns=[col])
            for x in tab.to_pylist():
                if n >= CONTROL_CLIPS: break
                data, rate = sf.read(io.BytesIO(x[col]["bytes"]), dtype="float32")
                if data.ndim > 1: data = data.mean(1)
                if rate != 16000:
                    p = f"{T}/ctl.wav"; sf.write(p, data, rate); wav16(p, p + ".16.wav"); data, rate = sf.read(p + ".16.wav", dtype="float32")
                rows.append({"id": f"c-{lang}-{n:03d}", "kind": "control", "section": f"control-{lang}", "lang": lang,
                             "dur": round(len(data) / 16000, 2), "text": "", "audio": data[: 39 * 16000]})
                n += 1
            os.remove(pq_path)
        save(f"prep_control_{lang}", n)
    except Exception as ex:
        save(f"prep_control_{lang}_error", repr(ex)[:300])

# rows in a fixed random order, so a run cut by the deadline still covers every section and control evenly
random.Random(11).shuffle(rows)
# ---------- audio check: MMS-LID ----------
from transformers import AutoFeatureExtractor, Wav2Vec2ForSequenceClassification
t0 = time.time()
fe = AutoFeatureExtractor.from_pretrained("facebook/mms-lid-4017")
model = Wav2Vec2ForSequenceClassification.from_pretrained("facebook/mms-lid-4017").eval(); torch.set_num_threads(os.cpu_count() or 4)
labels = model.config.id2label
inv = {v: k for k, v in labels.items()}
save("mms", {"load_s": round(time.time() - t0, 1), "labels": len(labels),
             "has": {c: c in inv for c in ("kmr", "ckb", "kur", "tur", "arb", "ara", "eng", "pes", "zza", "diq")}})
KMR = inv.get("kmr")
t0, audio_s = time.time(), 0.0
for r in rows:
    if left() < 20 * 60: break
    x = fe(r["audio"][: 20 * 16000], sampling_rate=16000, return_tensors="pt").input_values  # first 20 s is enough for the language
    with torch.no_grad(): p = torch.softmax(model(x).logits[0].float(), -1)
    top = int(p.argmax()); r["mms_top"] = labels[top]; r["mms_top_p"] = round(float(p[top]), 3)
    r["mms_kmr_p"] = round(float(p[KMR]), 3) if KMR is not None else None
    audio_s += r["dur"]
save("mms_speed", {"rows": sum("mms_top" in r for r in rows), "x_real_time": round(audio_s / max(1, time.time() - t0), 1)})
del model

# ---------- text check: GlotLID on the draft ----------
try:
    import fasttext
    from huggingface_hub import hf_hub_download
    glot = fasttext.load_model(hf_hub_download("cis-lmu/glotlid", "model.bin"))
    for r in rows:
        t = re.sub(r"\s+", " ", r["text"]).strip()
        if not t: continue
        try: lab, pr = glot.predict(t, k=3)
        except ValueError:  # fasttext + numpy 2: predict() fails on np.array(copy=False); call the C++ binding directly
            pairs = glot.f.predict(t + "\n", 3, 0.0, "strict"); pr = [a for a, _ in pairs]; lab = [b for _, b in pairs]
        r["glot_top"] = lab[0].replace("__label__", ""); r["glot_top_p"] = round(float(pr[0]), 3)
        r["glot_kmr_p"] = round(float(dict(zip(lab, pr)).get("__label__kmr_Latn", 0.0)), 3)
    save("glot", "ok")
except Exception as ex:
    save("glot_error", repr(ex)[:300])

# ---------- scoring ----------
for r in rows: r.pop("audio", None)
with open(f"{W}/rows.jsonl", "w") as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
def kurdish_audio(r, th): return r.get("mms_kmr_p") is not None and r["mms_kmr_p"] >= th
ctl = {}
for lang in CONTROLS:
    xs = [r for r in rows if r.get("lang") == lang and "mms_top" in r]
    if xs: ctl[lang] = {"clips": len(xs), "top_label": Counter(r["mms_top"] for r in xs).most_common(4),
                        "kmr_p>=0.5": round(sum(kurdish_audio(r, 0.5) for r in xs) / len(xs), 3),
                        "kmr_p>=0.2": round(sum(kurdish_audio(r, 0.2) for r in xs) / len(xs), 3)}
save("controls", ctl)
voa = [r for r in rows if r["kind"] == "voa" and "mms_top" in r]
by = {}
for sec in sorted({r["section"] for r in voa}):
    xs = [r for r in voa if r["section"] == sec]; h = sum(r["dur"] for r in xs) or 1
    share = lambda f: round(sum(r["dur"] for r in xs if f(r)) / h, 3)
    by[sec] = {"segments": len(xs), "hours": round(h / 3600, 2),
               "audio_top_labels": Counter(r["mms_top"] for r in xs).most_common(6),
               "audio_not_kmr@0.5": share(lambda r: not kurdish_audio(r, 0.5)),
               "audio_not_kmr@0.2": share(lambda r: not kurdish_audio(r, 0.2)),
               "text_not_kmr": share(lambda r: r.get("glot_top") not in (None, "kmr_Latn")),
               "both_not_kmr": share(lambda r: not kurdish_audio(r, 0.5) and r.get("glot_top") not in (None, "kmr_Latn")),
               "text_top_labels": Counter(r.get("glot_top") for r in xs).most_common(6)}
save("voa_by_section", by)
with open(f"{W}/rejected-examples.jsonl", "w") as f:
    for r in sorted(voa, key=lambda r: r.get("mms_kmr_p") or 0)[:80]:
        f.write(json.dumps({k: r.get(k) for k in ("id", "section", "file", "start", "dur", "mms_top", "mms_top_p", "mms_kmr_p",
                                                   "glot_top", "glot_kmr_p", "text")}, ensure_ascii=False) + "\n")
save("elapsed_h", round((time.time() - START) / 3600, 2))
print("DONE", flush=True)
