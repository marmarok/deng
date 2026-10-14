# K2 ön sınav: Kürtçe kulak adaylarını aynı sesler üzerinde ölçer.
# Sınav setleri: FLEURS-Kobani test (okuma, Kobanê ağzı) ve Common Voice 27 test (okuma, karışık ağız).
# Asıl karar Botan sohbet setinde verilecek; bu ön sınav temel modeli daraltır.
# Adaylar: Omnilingual CTC 300M/1B/3B ve LLM 1B/3B (Apache 2.0, temel model olabilir);
# Kürtçe Whisper (lisans yazılı değil) ve MMS-1B (ticari değil) yalnızca kıyas için.
import os, sys, json, subprocess, random, time, glob, io, csv, unicodedata, re, shutil
def sh(c): print("$", c, flush=True); return subprocess.run(c, shell=True)
W = "/kaggle/working"; T = "/kaggle/temp"; os.makedirs(T, exist_ok=True)
SES = f"{T}/ses"; os.makedirs(SES, exist_ok=True)
SAYI = 500
random.seed(14)
BASLA = time.time()
SINIR = 6 * 3600  # haftalık kart süresi sınırlı; 5. koşu sonuçsuz kesildi (14.10), sonuç kaydı için pay

METIN = os.path.dirname(glob.glob("/kaggle/input/**/hazirla.py", recursive=True)[0])
CV_GIRDI = os.path.dirname(glob.glob("/kaggle/input/**/bilgi.json", recursive=True)[0])
print("girdiler:", METIN, CV_GIRDI, flush=True)
sys.path.insert(0, METIN)
from hazirla import hazirla_ayrintili

sh("pip install -q jiwer soundfile")
import soundfile as sf, numpy as np, jiwer

# ---------- sınav setleri ----------
liste = []
# FLEURS-Kobani test
import urllib.request, pyarrow.parquet as pq
for i in range(2):
    yol = f"{T}/fleurs{i}.parquet"
    urllib.request.urlretrieve(f"https://huggingface.co/api/datasets/aranemini/northern-kurdish-fleurs/parquet/default/test/{i}.parquet", yol)
satirlar = []
for i in range(2):
    satirlar += pq.read_table(f"{T}/fleurs{i}.parquet").to_pylist()
print("FLEURS test satırı:", len(satirlar), flush=True)
random.shuffle(satirlar)
for n, r in enumerate(satirlar[:SAYI]):
    dalga, oran = sf.read(io.BytesIO(r["audio"]["bytes"]), dtype="float32")
    if dalga.ndim > 1: dalga = dalga.mean(1)
    yol = f"{SES}/f{n:04d}.wav"
    if oran != 16000:
        import librosa; dalga = librosa.resample(dalga, orig_sr=oran, target_sr=16000)
    sf.write(yol, dalga, 16000)
    liste.append({"id": f"f{n:04d}", "set": "fleurs", "yol": yol, "ref": r["kurdish"], "konusmaci": str(r.get("speaker_id")), "sure": len(dalga) / 16000})

# Common Voice 27 test: konuşmacı başına en çok 4 klip
bilgi = json.load(open(f"{CV_GIRDI}/bilgi.json"))
kok = f"{CV_GIRDI}/{bilgi['kok']}"
cv = list(csv.DictReader(open(f"{kok}/test.tsv"), delimiter="\t", quoting=csv.QUOTE_NONE))
random.shuffle(cv)
say = {}
secilen = []
for r in cv:
    if say.get(r["client_id"], 0) >= 4: continue
    say[r["client_id"]] = say.get(r["client_id"], 0) + 1
    secilen.append(r)
    if len(secilen) == SAYI: break
for n, r in enumerate(secilen):
    yol = f"{SES}/c{n:04d}.wav"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"{kok}/clips/{r['path']}", "-ac", "1", "-ar", "16000", yol], check=True)
    liste.append({"id": f"c{n:04d}", "set": "cv", "yol": yol, "ref": r["sentence"], "konusmaci": r["client_id"][:12], "sure": sf.info(yol).duration})
liste = [x for x in liste if 0.5 < x["sure"] < 39]
json.dump(liste, open(f"{T}/liste.json", "w"), ensure_ascii=False)
print("sınav:", {s: (sum(x["set"] == s for x in liste), round(sum(x["sure"] for x in liste if x["set"] == s) / 60, 1)) for s in ("fleurs", "cv")}, "dakika", flush=True)

# ---------- puanlama ----------
def duz(t, sapka_kipi=None):
    """Sayıları kelimeye çevirir, küçük harf, noktalamasız. sapka_kipi verilirse şapka da düzeltilir."""
    t = unicodedata.normalize("NFC", t or "")
    t = hazirla_ayrintili(t, sapka_kipi=sapka_kipi, sapka_duzelt=sapka_kipi is not None)[0]
    t = t.lower().replace("’", "'")
    t = re.sub(r"[^\w\s']", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t
def sapkasiz(t): return t.translate(str.maketrans("êîû", "eiu"))
REF = {x["id"]: duz(x["ref"], "sapkali") for x in liste}

def puanla(ad, hip):
    sonuc = {"model": ad}
    for s in ("fleurs", "cv"):
        ids = [x["id"] for x in liste if x["set"] == s and REF[x["id"]]]
        r = [REF[i] for i in ids]
        h = [duz(hip.get(i, "")) or "-" for i in ids]
        hs = [duz(hip.get(i, ""), "sapkali") or "-" for i in ids]
        sonuc[s] = {
            "wer": round(100 * jiwer.wer(r, h), 2),
            "cer": round(100 * jiwer.cer(r, h), 2),
            "cer_sapkasiz": round(100 * jiwer.cer([sapkasiz(x) for x in r], [sapkasiz(x) for x in h]), 2),
            "wer_sapka_duzeltilmis": round(100 * jiwer.wer(r, hs), 2),
        }
    print("SONUÇ", json.dumps(sonuc, ensure_ascii=False), flush=True)
    return sonuc

sonuclar = []
def kaydet(ad, hip, sure):
    s = puanla(ad, hip); s["sure_dk"] = round(sure / 60, 1); sonuclar.append(s)
    with open(f"{W}/hipotezler.jsonl", "a") as f:
        for x in liste:
            f.write(json.dumps({"model": ad, "id": x["id"], "set": x["set"], "ref": x["ref"], "hip": hip.get(x["id"], "")}, ensure_ascii=False) + "\n")
    json.dump(sonuclar, open(f"{W}/sonuc.json", "w"), ensure_ascii=False, indent=1)

# ---------- Omnilingual (Python 3.12 ortamında) ----------
sh("pip install -q uv")
OMNI = f"{T}/omni"
sh(f"UV_PYTHON_DOWNLOADS=automatic uv venv --managed-python -p 3.12 {OMNI} && {OMNI}/bin/python --version && uv pip install --python {OMNI}/bin/python -q omnilingual-asr torch==2.8.0 torchaudio==2.8.0 soundfile 'numpy<2' 'pyarrow==20.0.0' 2>&1 | tail -20")
sh(f"{OMNI}/bin/python -c 'import torch, numpy, pyarrow, omnilingual_asr; print(\"omni ortamı tamam\", torch.__version__, numpy.__version__, pyarrow.__version__)'")
open(f"{T}/omni_calis.py", "w").write(r'''
import sys, json, torch, time
from omnilingual_asr.models.inference.pipeline import ASRInferencePipeline
kart, cikti = sys.argv[1], sys.argv[2]
liste = json.load(open("/kaggle/temp/liste.json"))
p = ASRInferencePipeline(model_card=kart, device="cuda", dtype=torch.float16)
llm = "LLM" in kart
hip = {}
B = 4 if llm else 16
for i in range(0, len(liste), B):
    parca = liste[i:i + B]
    kw = {"lang": ["kmr_Latn"] * len(parca)} if llm else {}
    for x, t in zip(parca, p.transcribe([x["yol"] for x in parca], batch_size=B, **kw)):
        hip[x["id"]] = t
    if i % 200 == 0: print(kart, i, flush=True)
json.dump(hip, open(cikti, "w"), ensure_ascii=False)
print("bellek tepe GB", round(torch.cuda.max_memory_allocated() / 1e9, 1))
''')
# CTC 300M temel ölçümü K3'te yapıldı (aynı setler); burada yok. Ucuzdan pahalıya.
for kart in ["omniASR_CTC_1B_v2", "omniASR_LLM_1B_v2", "omniASR_CTC_3B_v2", "omniASR_LLM_3B_v2"]:
    t0 = time.time(); cikti = f"{T}/{kart}.json"
    kalan = SINIR - (t0 - BASLA)
    if kalan < 1200: print("SÜRE YETMEDİ, atlandı:", kart, flush=True); continue
    try:
        subprocess.run(f"{OMNI}/bin/python {T}/omni_calis.py {kart} {cikti} 2>&1 | grep -v Warning | tail -15",
                       shell=True, timeout=kalan - 600)
    except subprocess.TimeoutExpired:
        print("SÜRE SINIRI, yarıda kesildi:", kart, flush=True); subprocess.run("pkill -f omni_calis.py", shell=True)
    if os.path.exists(cikti):
        kaydet(kart, json.load(open(cikti)), time.time() - t0)
    else:
        print("BAŞARISIZ", kart, flush=True)
    for d in glob.glob(os.path.expanduser("~/.cache/fairseq2/assets/*")): shutil.rmtree(d, ignore_errors=True)

# ---------- yalnızca kıyas: Kürtçe Whisper ve MMS ----------
import torch
from transformers import pipeline as hf_pipeline, Wav2Vec2ForCTC, AutoProcessor
def dosyalar(): return [x["yol"] for x in liste]
WHISPER_OLC = False  # 14.10 3. koşuda ölçüldü: FLEURS WER 38,4 / CER 13,1; CV WER 3,4 (CV ile eğitilmiş olabilir)
try:
    if not WHISPER_OLC: raise RuntimeError("atlandı")
    t0 = time.time()
    torch.cuda.empty_cache()
    asr = hf_pipeline("automatic-speech-recognition", model="aranemini/whisper-v3-large-northern-kurdish", torch_dtype=torch.float16, device=0, chunk_length_s=30)
    hip = {}
    for x, o in zip(liste, asr(dosyalar(), batch_size=2)):
        hip[x["id"]] = o["text"]
    kaydet("kurtce-whisper (yalnız kıyas)", hip, time.time() - t0)
    del asr; torch.cuda.empty_cache()
except Exception as e:
    print("Whisper hata:", repr(e)[:500], flush=True)
MMS_OLC = False  # 14.10 ilk koşuda ölçüldü: FLEURS WER 43,0 / CER 12,0; CV WER 28,3 / CER 6,3
if MMS_OLC:
  try:
      t0 = time.time()
      proc = AutoProcessor.from_pretrained("facebook/mms-1b-all", target_lang="kmr-script_latin")
      m = Wav2Vec2ForCTC.from_pretrained("facebook/mms-1b-all", target_lang="kmr-script_latin", ignore_mismatched_sizes=True).to("cuda").half().eval()
      hip = {}
      for x in liste:
          d, _ = sf.read(x["yol"], dtype="float32")
          g = proc(d, sampling_rate=16000, return_tensors="pt").input_values.to("cuda").half()
          with torch.no_grad():
              hip[x["id"]] = proc.decode(m(g).logits[0].argmax(-1))
      kaydet("mms-1b (yalnız kıyas)", hip, time.time() - t0)
  except Exception as e:
      print("MMS hata:", repr(e)[:500], flush=True)
print("BİTTİ", flush=True)
