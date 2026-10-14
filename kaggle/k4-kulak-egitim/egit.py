# K4: temel kulağın (Omnilingual LLM 1B v2, Apache 2.0) ilk eğitimi. İki T4 (Kaggle, --accelerator NvidiaTeslaT4x2).
# Veri K3 ile aynı: Common Voice 27 (CC0) + FLEURS-Kobani eğitim (CC BY); ara ölçüm FLEURS doğrulamadan 100 klip.
# Düzen (k4-sigma 3 koşuda ölçüldü): ses kısmı (kodlayıcı) eğitilir, dil kısmı (Llama çözücü) donuk;
#   FSDP katman katman, katman katman yeniden hesaplama, fp16; 320k örnek/kart; ~3,8 sn/adım, ~14,4 GB/kart.
# Tam eğitim ana belleği (31 GB) taşırdı; o yol kiralık büyük kart ister (proje kararı).
# Sonda K2 ön sınavının aynı sesleriyle (FLEURS test 499 + CV test 500) ölçülür.
import os, sys, json, subprocess, random, time, glob, io, csv, unicodedata, re, shutil
def sh(c): print("$", c, flush=True); return subprocess.run(c, shell=True)
W = "/kaggle/working"; T = "/kaggle/temp"; os.makedirs(T, exist_ok=True)
BASLA = time.time()
MODEL = "omniASR_LLM_1B_v2"
ADIM = 4000
SURE_SINIRI = 8.5 * 3600  # eğitim bu saatte biter; LLM ölçümü (~50 dk) ve kayıt için pay. Kaggle 12 saatte keser
SAYI = 500
random.seed(14)  # K2 ile aynı sınav seçimi için: sınav setinden önce başka rastgele çağrı yok

METIN = os.path.dirname(glob.glob("/kaggle/input/**/hazirla.py", recursive=True)[0])
CV_GIRDI = os.path.dirname(glob.glob("/kaggle/input/**/bilgi.json", recursive=True)[0])
print("girdiler:", METIN, CV_GIRDI, "model:", MODEL, flush=True)
sys.path.insert(0, METIN)
from hazirla import hazirla_ayrintili

sh("pip install -q jiwer soundfile")
import soundfile as sf, numpy as np, jiwer
import urllib.request, pyarrow.parquet as pq
from concurrent.futures import ThreadPoolExecutor

def fleurs_parcalari(bolum):
    adresler = json.load(urllib.request.urlopen(f"https://huggingface.co/api/datasets/aranemini/northern-kurdish-fleurs/parquet/default/{bolum}"))
    satirlar = []
    for i, a in enumerate(adresler):
        yol = f"{T}/fleurs-{bolum}{i}.parquet"
        urllib.request.urlretrieve(a, yol)
        satirlar += pq.read_table(yol).to_pylist()
    return satirlar

def wav_yaz(veri, oran, yol):
    if veri.ndim > 1: veri = veri.mean(1)
    if oran != 16000:
        import librosa; veri = librosa.resample(veri, orig_sr=oran, target_sr=16000)
    sf.write(yol, veri, 16000)
    return len(veri)

# ---------- sınav setleri (K2 ile birebir aynı seçim) ----------
SINAV = f"{T}/sinav"; os.makedirs(SINAV, exist_ok=True)
liste = []
satirlar = []
for i in range(2):
    yol = f"{T}/fleurs{i}.parquet"
    urllib.request.urlretrieve(f"https://huggingface.co/api/datasets/aranemini/northern-kurdish-fleurs/parquet/default/test/{i}.parquet", yol)
    satirlar += pq.read_table(yol).to_pylist()
random.shuffle(satirlar)
for n, r in enumerate(satirlar[:SAYI]):
    d, o = sf.read(io.BytesIO(r["audio"]["bytes"]), dtype="float32")
    yol = f"{SINAV}/f{n:04d}.wav"; uz = wav_yaz(d, o, yol)
    liste.append({"id": f"f{n:04d}", "set": "fleurs", "yol": yol, "ref": r["kurdish"], "sure": uz / 16000})
bilgi = json.load(open(f"{CV_GIRDI}/bilgi.json"))
kok = f"{CV_GIRDI}/{bilgi['kok']}"
cv = list(csv.DictReader(open(f"{kok}/test.tsv"), delimiter="\t", quoting=csv.QUOTE_NONE))
random.shuffle(cv)
say = {}; secilen = []
for r in cv:
    if say.get(r["client_id"], 0) >= 4: continue
    say[r["client_id"]] = say.get(r["client_id"], 0) + 1
    secilen.append(r)
    if len(secilen) == SAYI: break
for n, r in enumerate(secilen):
    yol = f"{SINAV}/c{n:04d}.wav"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"{kok}/clips/{r['path']}", "-ac", "1", "-ar", "16000", yol], check=True)
    liste.append({"id": f"c{n:04d}", "set": "cv", "yol": yol, "ref": r["sentence"], "sure": sf.info(yol).duration})
liste = [x for x in liste if 0.5 < x["sure"] < 39]
json.dump(liste, open(f"{T}/liste.json", "w"), ensure_ascii=False)
# K2'nin hipotez dosyası girdi olarak varsa aynı seçim olduğunu doğrula
k2 = glob.glob("/kaggle/input/**/hipotezler.jsonl", recursive=True)
if k2:
    eski = {}
    for l in open(k2[0]):
        x = json.loads(l); eski.setdefault(x["id"], x["ref"])
    fark = sum(eski.get(x["id"]) != x["ref"] for x in liste if x["id"] in eski)
    print("K2 sınavıyla fark:", fark, "/", len(liste), flush=True)
print("sınav:", len(liste), flush=True)

# ---------- eğitim verisi ----------
VERI = f"{T}/veri"; os.makedirs(f"{VERI}/ses", exist_ok=True)
egitim = [json.loads(l) for l in open(glob.glob("/kaggle/input/**/cv-egitim.jsonl", recursive=True)[0])]
def cevir(x):
    hedef = f"{VERI}/ses/{x['yol'].rsplit('.', 1)[0]}.flac"
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"{kok}/clips/{x['yol']}", "-ac", "1", "-ar", "16000", hedef])
    if r.returncode: return None
    return (os.path.relpath(hedef, f"{VERI}/ses"), sf.info(hedef).frames, x["metin"])
t0 = time.time()
with ThreadPoolExecutor(os.cpu_count() or 4) as h:
    cv_egitim = [s for s in h.map(cevir, egitim) if s]
print("CV eğitim sesi:", len(cv_egitim), "dk", round((time.time() - t0) / 60, 1), flush=True)

def fleurs_yaz(bolum):
    cikti = []
    for n, r in enumerate(fleurs_parcalari(bolum)):
        d, o = sf.read(io.BytesIO(r["audio"]["bytes"]), dtype="float32")
        ad = f"fleurs-{bolum}-{n:05d}.flac"
        uz = wav_yaz(d, o, f"{VERI}/ses/{ad}")
        cikti.append((ad, uz, hazirla_ayrintili(r["kurdish"], sapka_kipi="sapkali")[0]))
    return cikti
fl_egitim = fleurs_yaz("train")
fl_dogrulama = fleurs_yaz("validation")
print("FLEURS eğitim:", len(fl_egitim), "doğrulama:", len(fl_dogrulama), flush=True)

# ---------- Omnilingual ortamı (Python 3.12) ----------
sh("pip install -q uv")
OMNI = f"{T}/omni"
sh(f"UV_PYTHON_DOWNLOADS=automatic uv venv --managed-python -p 3.12 {OMNI} && uv pip install --python {OMNI}/bin/python -q omnilingual-asr torch==2.8.0 torchaudio==2.8.0 soundfile tensorboard 'numpy<2' 'pyarrow==20.0.0' 2>&1 | tail -20")
PY = f"{OMNI}/bin/python"
sh(f"{PY} -c 'import torch, numpy, pyarrow, omnilingual_asr; print(\"omni ortamı tamam\", torch.__version__, numpy.__version__)'")

# Tokenizer'ın bilmediği harfleri bul; eğitim yazılarından at (bilinmeyen harfli örneği eğitim zaten atar)
yazilar = [x[2] for x in cv_egitim + fl_egitim + fl_dogrulama]
json.dump(sorted(set("".join(yazilar))), open(f"{T}/harfler.json", "w"), ensure_ascii=False)
open(f"{T}/harf_yokla.py", "w").write(r'''
import json, sys
from fairseq2.data.tokenizers.hub import load_tokenizer
tok = load_tokenizer(sys.argv[1])
enc = tok.create_encoder(); unk = tok.vocab_info.unk_idx
harfler = json.load(open("/kaggle/temp/harfler.json"))
bilinmeyen = [c for c in harfler if c.strip() and unk in enc(c).tolist()]
json.dump(bilinmeyen, open("/kaggle/temp/bilinmeyen.json", "w"), ensure_ascii=False)
print("bilinmeyen harfler:", bilinmeyen)
''')
sh(f"{PY} {T}/harf_yokla.py {MODEL}")
bilinmeyen = set(json.load(open(f"{T}/bilinmeyen.json"))) if os.path.exists(f"{T}/bilinmeyen.json") else set()
def temizle(t):
    t = unicodedata.normalize("NFC", t).replace("’", "'")
    t = "".join(c for c in t if c not in bilinmeyen)
    return re.sub(r"\s+", " ", t).strip()

def manifest(ad, ornekler):
    with open(f"{VERI}/{ad}.tsv", "w") as a, open(f"{VERI}/{ad}.wrd", "w") as b:
        a.write(f"{VERI}/ses\n")
        for yol, uz, metin in ornekler:
            m = temizle(metin)
            if not m: continue
            a.write(f"{yol}\t{uz}\n"); b.write(m + "\n")
egitim_ornek = cv_egitim + fl_egitim
random.Random(3).shuffle(egitim_ornek)
# LLM tarifi 20 sn'den uzun klibi almaz (max_audio_len 320k; bellek de buna göre ölçüldü)
uzun = [x for x in egitim_ornek if x[1] > 320_000]
egitim_ornek = [x for x in egitim_ornek if x[1] <= 320_000]
print("20 sn'den uzun, dışarıda:", len(uzun), "klip,", round(sum(x[1] for x in uzun) / 16000 / 3600, 2), "saat", flush=True)
manifest("train", egitim_ornek)
dev = [x for x in fl_dogrulama if x[1] <= 320_000]
random.Random(4).shuffle(dev)
manifest("dev", dev[:100])  # ara ölçüm ışın aramasıyla yavaş: 100 klip yeter
saat = sum(x[1] for x in egitim_ornek) / 16000 / 3600
print("eğitim saati:", round(saat, 1), flush=True)



SP = glob.glob(f"{OMNI}/lib/python3.12/site-packages")[0]
open(f"{SP}/omnilingual_asr/cards/datasets/deng_kulak.yaml", "w").write(
    f"name: deng_kulak\ndataset_family: manifest_asr_dataset\ndataset_config:\n  data: {VERI}\ntokenizer_ref: omniASR_tokenizer_written_v2\n")

# ---------- yamalar (k4-sigma'da sınandı) ----------
# 1) LLM modeli eğitimde her örnekte "lang" ister; manifest biçimi vermiyor -> hepsi kmr_Latn.
ms = f"{SP}/omnilingual_asr/datasets/storage/manifest_storage.py"
s1 = open(ms).read(); e1 = 'return {**example, "audio": example["audio"]["data"]}'
assert e1 in s1, "manifest yaması tutmadı"
open(ms, "w").write(s1.replace(e1, 'return {"lang": "kmr_Latn", **example, "audio": example["audio"]["data"]}'))
# 2) wav2vec2_llama ailesine katman katman yeniden hesaplama.
oi = f"{SP}/omnilingual_asr/__init__.py"
s2 = open(oi).read(); e2 = "        fsdp_applier=apply_fsdp_to_wav2vec2_llama,\n"
assert e2 in s2, "AC yaması tutmadı"
s2 = s2.replace(e2, e2 + "        layerwise_ac_applier=_deng_ac,\n", 1).replace("def _register_models(", """def _deng_ac(model, every_nth_layer):
    from fairseq2.models.utils.ac import apply_layerwise_ac
    apply_layerwise_ac(model.encoder.layers, every_nth_layer)
    apply_layerwise_ac(model.llama_decoder.layers, every_nth_layer)
    return model


def _register_models(""", 1)
open(oi, "w").write(s2)
sh(f"cd {T} && git clone -q --depth 1 https://github.com/facebookresearch/omnilingual-asr.git kod")
# 3) Dil kısmı (çözücü, metin girişi, son katman, dil gömmesi) sarmalamadan önce donuk.
rp = f"{T}/kod/workflows/recipes/wav2vec2/asr/recipe.py"
s3 = open(rp).read(); e3 = "        freeze_parameters(asr_module.encoder_frontend.feature_extractor)\n"
assert e3 in s3, "tarif yaması tutmadı"
open(rp, "w").write(s3.replace(e3, e3 + """        for _ad in ("llama_decoder", "text_frontend", "final_proj", "lang_embeddings"):
            if getattr(asr_module, _ad, None) is not None:
                freeze_parameters(getattr(asr_module, _ad))
        log.info("DENG: dil kismi donduruldu")
""", 1))

AYAR = f"""
model:
  name: "{MODEL}"
dataset:
  name: "deng_kulak"
  train_split: "train"
  valid_split: "dev"
  storage_mode: "MANIFEST"
  task_mode: "ASR"
  manifest_storage_config:
    read_text: true
  asr_task_config:
    min_audio_len: 16_000
    max_audio_len: 320_000
    max_num_elements: 320_000
    batch_shuffle_window: 1
    normalize_audio: true
    example_shuffle_window: 5000
tokenizer:
  name: "omniASR_tokenizer_written_v2"
optimizer:
  config:
    lr: 1e-05
trainer:
  data_parallelism: "fsdp"
  fsdp:
    granularity: "layer"
    version: "v1"
    fp32_reduce: false
  activation_checkpointing:
    mode: "layerwise"
  freeze_encoder_for_n_steps: 0
  mixed_precision:
    mode: "auto"
    dtype: "torch.float16"
  grad_accumulation:
    num_batches: 2
common:
  metric_recorders:
    tensorboard:
      enabled: false
regime:
  num_steps: {ADIM}
  validate_after_n_steps: 1000
  validate_every_n_steps: 1000
  checkpoint_after_n_steps: 500
  checkpoint_every_n_steps: 500
  publish_metrics_every_n_steps: 50
  save_model_only: true
  keep_last_n_checkpoints: 2
"""
CIKTI = f"{T}/egitim"; GUNLUK = f"{W}/egitim.log"
open(f"{T}/ayar.yaml", "w").write(AYAR)
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
kalan = SURE_SINIRI - (time.time() - BASLA)
print("EĞİTİM başlıyor; süre sınırı", round(kalan / 3600, 2), "saat", flush=True)
# eğitim çıktısı dosyaya; adım/ara ölçüm/hata satırları canlı günlüğe de (Kaggle'dan izlenebilsin)
import threading
p = subprocess.Popen(f"cd {T}/kod && {OMNI}/bin/torchrun --standalone --nproc_per_node=2 --log-dir {W}/sira --tee 3 -m workflows.recipes.wav2vec2.asr {CIKTI} --config-file {T}/ayar.yaml",
                     shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
def akit():
    onemli = re.compile(r"Train Metrics|Valid|ERROR|Error|out of memory|Saving|checkpoint", re.I)
    with open(GUNLUK, "w") as g:
        for satir in p.stdout:
            g.write(satir)
            if onemli.search(satir) and "Warning" not in satir: print(satir.rstrip()[:300], flush=True)
th = threading.Thread(target=akit, daemon=True); th.start()
try:
    p.wait(timeout=max(60, kalan))
except subprocess.TimeoutExpired:
    print("süre sınırı: eğitim durduruldu", flush=True); p.terminate(); p.wait()
th.join(timeout=30)
sh("pkill -f workflows.recipes.wav2vec2.asr")
adimlar = sorted(glob.glob(f"{CIKTI}/checkpoints/step_*/model"), key=lambda y: int(re.findall(r"step_(\d+)", y)[0]))
print("eğitim çıkış", p.returncode, "kayıtlar", [re.findall(r"step_\d+", y)[0] for y in adimlar], flush=True)
sh(f"grep -a -E 'Train Metrics|Valid' {GUNLUK} | tail -6")

# ---------- ölçüm: K2 sesleri, iki kartta yarı yarıya ----------
def duz(t, sapka_kipi=None):
    t = unicodedata.normalize("NFC", t or "")
    t = hazirla_ayrintili(t, sapka_kipi=sapka_kipi, sapka_duzelt=sapka_kipi is not None)[0]
    t = t.lower().replace("’", "'")
    t = re.sub(r"[^\w\s']", " ", t)
    return re.sub(r"\s+", " ", t).strip()
def sapkasiz(t): return t.translate(str.maketrans("êîû", "eiu"))
REF = {x["id"]: duz(x["ref"], "sapkali") for x in liste}
def puanla(ad, hip):
    sonuc = {"model": ad}
    for s in ("fleurs", "cv"):
        ids = [x["id"] for x in liste if x["set"] == s and REF[x["id"]]]
        r = [REF[i] for i in ids]
        h = [duz(hip.get(i, "")) or "-" for i in ids]
        hs = [duz(hip.get(i, ""), "sapkali") or "-" for i in ids]
        sonuc[s] = {"wer": round(100 * jiwer.wer(r, h), 2), "cer": round(100 * jiwer.cer(r, h), 2),
                    "cer_sapkasiz": round(100 * jiwer.cer([sapkasiz(x) for x in r], [sapkasiz(x) for x in h]), 2),
                    "wer_sapka_duzeltilmis": round(100 * jiwer.wer(r, hs), 2)}
    print("SONUÇ", json.dumps(sonuc, ensure_ascii=False), flush=True)
    return sonuc

open(f"{T}/olc.py", "w").write(r"""
import sys, json, torch
from omnilingual_asr.models.inference.pipeline import ASRInferencePipeline
kart, bas, son, cikti, kaydet = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5] == "1"
liste = json.load(open("/kaggle/temp/liste.json"))[bas:son]
p = ASRInferencePipeline(model_card=kart, device="cuda", dtype=torch.float16)
if kaydet:  # eğitilmiş kulağı tek parça, fp16 olarak sakla (taslak ve Dengê Amerîka için)
    torch.save({k: v.half() for k, v in p.model.state_dict().items()}, "/kaggle/working/k4-kulak.pt")
hip = {}
for i in range(0, len(liste), 4):
    parca = liste[i:i + 4]
    for x, t in zip(parca, p.transcribe([x["yol"] for x in parca], lang=["kmr_Latn"] * len(parca), batch_size=4)):
        hip[x["id"]] = t
json.dump(hip, open(cikti, "w"), ensure_ascii=False)
""")
sonuclar = []
def olc(ad, kart):
    yari = len(liste) // 2
    isler = [subprocess.Popen(f"CUDA_VISIBLE_DEVICES={g} {PY} {T}/olc.py {kart} {a} {b} {T}/hip-{ad}-{g}.json {1 if (g == 0 and kart != MODEL) else 0} 2>&1 | grep -v Warning | tail -6",
                              shell=True) for g, (a, b) in enumerate([(0, yari), (yari, len(liste))])]
    for i in isler: i.wait()
    hip = {}
    for g in (0, 1):
        y = f"{T}/hip-{ad}-{g}.json"
        if not os.path.exists(y): print("BAŞARISIZ", ad, g, flush=True); return
        hip.update(json.load(open(y)))
    s = puanla(ad, hip); sonuclar.append(s)
    json.dump(sonuclar, open(f"{W}/sonuc.json", "w"), ensure_ascii=False, indent=1)
    with open(f"{W}/hipotezler.jsonl", "a") as f:
        for x in liste:
            f.write(json.dumps({"model": ad, "id": x["id"], "set": x["set"], "ref": x["ref"], "hip": hip.get(x["id"], "")}, ensure_ascii=False) + "\n")
if adimlar:
    son_adim = re.findall(r"step_(\d+)", adimlar[-1])[0]
    open(f"{SP}/omnilingual_asr/cards/models/deng_k4.yaml", "w").write(
        f"name: deng_k4\nmodel_family: wav2vec2_llama\nmodel_arch: 1b_v2\ncheckpoint: {adimlar[-1]}\ntokenizer_ref: omniASR_tokenizer_written_v2\n")
    olc("k4-" + son_adim, "deng_k4")
    if not sonuclar or not os.path.exists("/kaggle/working/k4-kulak.pt"):
        # yükleme/ölçüm tutmadıysa eğitilmiş kulak kaybolmasın: son kaydı olduğu gibi çıktıya al
        sh(f"cp -r {adimlar[-1]} /kaggle/working/k4-son-kayit && du -sh /kaggle/working/k4-son-kayit")
# temel LLM 1B K2'de ölçüldü (FLEURS 31,35 / 9,08; CV 16,36 / 4,14); süre kalırsa yeniden ölçme
json.dump({"model": MODEL, "egitim_saati": round(saat, 1), "adimlar": [re.findall(r"step_\d+", y)[0] for y in adimlar],
           "toplam_dk": round((time.time() - BASLA) / 60)}, open(f"{W}/bilgi.json", "w"), ensure_ascii=False, indent=1)
print("BİTTİ", flush=True)
