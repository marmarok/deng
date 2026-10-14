# K4 sığma denemesi (eğitim DEĞİL): Omnilingual LLM 1B v2'nin eğitimi iki T4'e sığıyor mu?
# Her düzen birkaç adım koşar; ölçülen: başladı mı, adım süresi, kart başına tepe bellek.
# Düzenler:
#   ses: ses kısmı (kodlayıcı) eğitilir, dil kısmı (Llama çözücü) donuk  -> küçük yama gerekir
#   dil: dil kısmı eğitilir, ses kısmı donuk                              -> tarifte hazır (freeze_encoder_for_n_steps)
#   tam: hepsi eğitilir                                                    -> hesapla ~18 GB/kart, taşması bekleniyor
# Veri: Common Voice eğitim bölümünden 400 klip (CC0); yalnızca sınama için.
# 2. koşu (14.10): 1. koşuda 'stack' sarmalama tüm kodlayıcıyı/çözücüyü bir anda topladığı için bellek taştı.
#   Şimdi: katman katman sarmalama, katman katman yeniden hesaplama (yama), tam eğitimde ana belleğe aktarma (yama).
# 3. koşu (14.10): 2. koşuda 'ses' düzeni çalıştı (3,8 sn/adım, 14,4 GB/kart). Tam eğitim ana belleği taşırdı (31 GB).
#   Şimdi bütün zincir: FLEURS'un uzun klipleriyle bellek payı, 30 adım + kayıt, kaydı tek süreçte geri yükleyip yazdırma.
#   Ayrıca 'dil' düzeni: kodlayıcı sarmalamadan ÖNCE dondurulur (2. koşuda sonradan dondurma 1. sırada düştü).
import os, sys, json, subprocess, time, glob, re, threading, random
def sh(c): print("$", c, flush=True); return subprocess.run(c, shell=True)
W = "/kaggle/working"; T = "/kaggle/temp"; os.makedirs(T, exist_ok=True)
BASLA = time.time(); SURE = 2.5 * 3600
MODEL = "omniASR_LLM_1B_v2"
sh("nvidia-smi -L")

CV_GIRDI = os.path.dirname(glob.glob("/kaggle/input/**/bilgi.json", recursive=True)[0])
bilgi = json.load(open(f"{CV_GIRDI}/bilgi.json")); kok = f"{CV_GIRDI}/{bilgi['kok']}"
egitim = [json.loads(l) for l in open(glob.glob("/kaggle/input/**/cv-egitim.jsonl", recursive=True)[0])]
random.Random(5).shuffle(egitim)
sh("pip install -q soundfile")
import soundfile as sf
from concurrent.futures import ThreadPoolExecutor
VERI = f"{T}/veri"; os.makedirs(f"{VERI}/ses", exist_ok=True)
def cevir(x):
    hedef = f"{VERI}/ses/{x['yol'].rsplit('.', 1)[0]}.flac"
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"{kok}/clips/{x['yol']}", "-ac", "1", "-ar", "16000", hedef])
    return None if r.returncode else (os.path.relpath(hedef, f"{VERI}/ses"), sf.info(hedef).frames, x["metin"])
with ThreadPoolExecutor(8) as h:
    ornek = [s for s in h.map(cevir, egitim[:440]) if s]
def manifest(ad, rr):
    with open(f"{VERI}/{ad}.tsv", "w") as a, open(f"{VERI}/{ad}.wrd", "w") as b:
        a.write(f"{VERI}/ses\n")
        for yol, uz, m in rr: a.write(f"{yol}\t{uz}\n"); b.write(re.sub(r"\s+", " ", m).strip() + "\n")
import io, urllib.request, pyarrow.parquet as pq, numpy as np
def fleurs(bolum, n):
    yol = f"{T}/fl-{bolum}.parquet"
    urllib.request.urlretrieve(f"https://huggingface.co/api/datasets/aranemini/northern-kurdish-fleurs/parquet/default/{bolum}/0.parquet", yol)
    cikti = []
    for i, r in enumerate(pq.read_table(yol).to_pylist()[:n]):
        d, o = sf.read(io.BytesIO(r["audio"]["bytes"]), dtype="float32")
        if d.ndim > 1: d = d.mean(1)
        if o != 16000:
            import librosa; d = librosa.resample(d, orig_sr=o, target_sr=16000)
        ad = f"fl-{bolum}-{i:04d}.flac"; sf.write(f"{VERI}/ses/{ad}", d, 16000)
        cikti.append((ad, len(d), r["kurdish"]))
    return cikti
fl_egt = [x for x in fleurs("train", 260) if x[1] <= 320_000]
fl_dog = fleurs("validation", 20)
karisik = ornek[:200] + fl_egt
random.Random(9).shuffle(karisik)
manifest("train", karisik); manifest("dev", ornek[400:])
print("veri:", len(karisik), "klip; FLEURS uzunluk sn (ort/en çok):", round(np.mean([x[1] for x in fl_egt]) / 16000, 1), round(max(x[1] for x in fl_egt) / 16000, 1), flush=True)

sh("pip install -q uv")
OMNI = f"{T}/omni"; PY = f"{OMNI}/bin/python"
sh(f"UV_PYTHON_DOWNLOADS=automatic uv venv --managed-python -p 3.12 {OMNI} && uv pip install --python {PY} -q omnilingual-asr torch==2.8.0 torchaudio==2.8.0 soundfile tensorboard 'numpy<2' 'pyarrow==20.0.0' 2>&1 | tail -5")
SP = glob.glob(f"{OMNI}/lib/python3.12/site-packages")[0]
open(f"{SP}/omnilingual_asr/cards/datasets/deng_sigma.yaml", "w").write(
    f"name: deng_sigma\ndataset_family: manifest_asr_dataset\ndataset_config:\n  data: {VERI}\ntokenizer_ref: omniASR_tokenizer_written_v2\n")

# Yama 1: LLM modeli eğitimde her örnekte "lang" ister; manifest biçimi vermiyor -> hepsi kmr_Latn.
ms = f"{SP}/omnilingual_asr/datasets/storage/manifest_storage.py"
s = open(ms).read(); eski = 'return {**example, "audio": example["audio"]["data"]}'
assert eski in s, "manifest yaması tutmadı"
open(ms, "w").write(s.replace(eski, 'return {"lang": "kmr_Latn", **example, "audio": example["audio"]["data"]}'))

sh(f"cd {T} && git clone -q --depth 1 https://github.com/facebookresearch/omnilingual-asr.git kod")
# Yama 3: wav2vec2_llama ailesi katman katman yeniden hesaplamayı (activation checkpointing) tanımıyor -> tanıt.
oi = f"{SP}/omnilingual_asr/__init__.py"
s3 = open(oi).read(); e3 = "        fsdp_applier=apply_fsdp_to_wav2vec2_llama,\n"
assert e3 in s3, "AC yaması tutmadı"
s3 = s3.replace(e3, e3 + "        layerwise_ac_applier=_deng_ac,\n", 1)
s3 = s3.replace("def _register_models(", """def _deng_ac(model, every_nth_layer):
    from fairseq2.models.utils.ac import apply_layerwise_ac
    apply_layerwise_ac(model.encoder.layers, every_nth_layer)
    apply_layerwise_ac(model.llama_decoder.layers, every_nth_layer)
    return model


def _register_models(""", 1)
open(oi, "w").write(s3)
# Yama 4: DENG_OFFLOAD=1 ise FSDP1 parametreleri ve eğimleri ana belleğe (CPU) aktarır; iyileştirici adımı CPU'da.
f1 = f"{SP}/fairseq2/nn/fsdp/fsdp1.py"
s4 = open(f1).read(); e4 = "    if not cpu_offload:\n        cpu_offload_ = None\n    else:\n        cpu_offload_ = CPUOffload()\n"
assert e4 in s4, "aktarma yaması tutmadı"
open(f1, "w").write(s4.replace(e4, "    import os as _os\n    if not (cpu_offload or _os.environ.get(\"DENG_OFFLOAD\") == \"1\"):\n        cpu_offload_ = None\n    else:\n        cpu_offload_ = CPUOffload(offload_params=True)\n", 1))
# Yama 2: DENG_DONDUR=dil ise çözücü (dil kısmı) baştan dondurulur.
rp = f"{T}/kod/workflows/recipes/wav2vec2/asr/recipe.py"
s = open(rp).read(); eski = "        freeze_parameters(asr_module.encoder_frontend.feature_extractor)\n"
assert eski in s, "tarif yaması tutmadı"
open(rp, "w").write(s.replace(eski, eski + '''        import os as _os
        if _os.environ.get("DENG_DONDUR") == "dil":
            for _ad in ("llama_decoder", "text_frontend", "final_proj", "lang_embeddings"):
                if getattr(asr_module, _ad, None) is not None:
                    freeze_parameters(getattr(asr_module, _ad))
            log.info("DENG: dil kismi donduruldu")
        if _os.environ.get("DENG_DONDUR") == "ses":
            for _ad in ("encoder_frontend", "encoder", "masker"):
                if getattr(asr_module, _ad, None) is not None:
                    freeze_parameters(getattr(asr_module, _ad))
            log.info("DENG: ses kismi donduruldu")
''', 1))

def ayar(eleman, ac, adim=15, kayit=False, kip="auto", tur="torch.float16"):
    uzun = min(320_000, eleman)
    return f"""
model:
  name: "{MODEL}"
dataset:
  name: "deng_sigma"
  train_split: "train"
  valid_split: null
  storage_mode: "MANIFEST"
  task_mode: "ASR"
  manifest_storage_config:
    read_text: true
  asr_task_config:
    min_audio_len: 16_000
    max_audio_len: {uzun}
    max_num_elements: {eleman}
    batch_shuffle_window: 1
    normalize_audio: true
    example_shuffle_window: 400
tokenizer:
  name: "omniASR_tokenizer_written_v2"
optimizer:
  config:
    lr: 5e-05
trainer:
  data_parallelism: "fsdp"
  fsdp:
    granularity: "layer"
    version: "v1"
    fp32_reduce: false
  activation_checkpointing:
    mode: "{'layerwise' if ac else 'off'}"
  freeze_encoder_for_n_steps: 0
  mixed_precision:
    mode: "{kip}"
    dtype: "{tur}"
  grad_accumulation:
    num_batches: 1
common:
  metric_recorders:
    tensorboard:
      enabled: false
regime:
  num_steps: {adim}
  validate_every_n_steps: 100000
  checkpoint_every_n_steps: {adim if kayit else 100000}
  checkpoint_after_n_steps: 0
  publish_metrics_every_n_steps: 1
  save_model_only: true
  keep_last_n_checkpoints: 1
"""

def kartlar_bos(bekle=120):
    t = time.time()
    while time.time() - t < bekle:
        o = subprocess.run("nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits", shell=True, capture_output=True, text=True).stdout.split()
        if all(int(v) < 1000 for v in o[:2]): return True
        time.sleep(3)
    print("uyarı: kartlar boşalmadı", o, flush=True); return False

tepe = [0, 0]; adim_zaman = {}; dur = threading.Event()
def izle(gunluk):
    konum = 0
    while not dur.is_set():
        try:
            o = subprocess.run("nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits", shell=True, capture_output=True, text=True).stdout.split()
            for i, v in enumerate(o[:2]): tepe[i] = max(tepe[i], int(v))
            with open(gunluk, errors="replace") as f:
                f.seek(konum); yeni = f.read(); konum = f.tell()
            for a in re.findall(r"[Ss]tep (\d+)", yeni):
                adim_zaman.setdefault(int(a), time.time())
        except Exception: pass
        time.sleep(1)

sonuclar = []
def dene(duzen, eleman, ac, offload=False, adim=15, kayit=False, kip="auto", tur="torch.float16"):
    kalan = SURE - (time.time() - BASLA)
    if kalan < 900: print("süre yetmedi:", duzen, flush=True); return None
    kartlar_bos()
    etiket = f"{duzen}-{eleman}-{'ac' if ac else 'acsiz'}{'-aktarim' if offload else ''}"
    cikti = f"{T}/c-{etiket}"; sh(f"rm -rf {cikti}")
    open(f"{T}/ayar.yaml", "w").write(ayar(eleman, ac, adim, kayit, kip, tur))
    gunluk = f"{W}/gunluk-{etiket}.log"; open(gunluk, "w").close()
    env = dict(os.environ, DENG_DONDUR={"ses": "dil", "dil": "ses"}.get(duzen, ""), DENG_OFFLOAD="1" if offload else "0",
               PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True")
    tepe[0] = tepe[1] = 0; adim_zaman.clear(); dur.clear()
    th = threading.Thread(target=izle, args=(gunluk,), daemon=True); th.start()
    t0 = time.time()
    with open(gunluk, "a") as g:
        p = subprocess.Popen(f"cd {T}/kod && {OMNI}/bin/torchrun --standalone --nproc_per_node=2 --log-dir {W}/sira-{etiket} --tee 3 -m workflows.recipes.wav2vec2.asr {cikti} --config-file {T}/ayar.yaml",
                             shell=True, stdout=g, stderr=subprocess.STDOUT, env=env)
        try: p.wait(timeout=min(1500, kalan - 600))
        except subprocess.TimeoutExpired: p.terminate(); p.wait()
    time.sleep(2); dur.set(); th.join()
    metin = open(gunluk, errors="replace").read()
    r = {"etiket": etiket, "cikis": p.returncode, "son_adim": max(adim_zaman) if adim_zaman else 0,
         "bellek_tasti": "out of memory" in metin.lower(), "tepe_mb": list(tepe), "sure_sn": round(time.time() - t0)}
    a = sorted(adim_zaman)
    if len(a) >= 4:  # ilk iki adım ısınma; sonrakilerden ölç
        r["sn_adim"] = round((adim_zaman[a[-1]] - adim_zaman[a[2]]) / (a[-1] - a[2]), 1)
    kayip = re.findall(r"[Ll]oss: ([0-9.]+|nan|inf)", metin)
    r["kayip"] = kayip[:3] + kayip[-3:]
    r["hata"] = [l.strip() for l in metin.splitlines() if ("Error" in l or "error" in l) and "Warning" not in l][-4:]
    print("DENEME", json.dumps(r, ensure_ascii=False), flush=True)
    print("\n".join([l for l in metin.splitlines() if "Warning" not in l and "warn(" not in l][-20:]), flush=True)
    r["cikti"] = cikti
    sonuclar.append(r); json.dump(sonuclar, open(f"{W}/sigma.json", "w"), ensure_ascii=False, indent=1)
    return r

def iyi(r): return r and r["son_adim"] >= 5 and not r["bellek_tasti"]

# 1) Ses kısmı, uzun FLEURS klipleriyle, 30 adım + kayıt
r = dene("ses", 320_000, ac=True, adim=30, kayit=True)
if not iyi(r): r = dene("ses", 256_000, ac=True, adim=30, kayit=True)

# 2) Kaydı tek süreçte geri yükle, 20 FLEURS doğrulama klibini yazdır; temel modelle kıyasla
def yukle_dene(r):
    adimlar = sorted(glob.glob(f"{r['cikti']}/checkpoints/step_*/model"))
    print("kayıtlar:", adimlar, flush=True)
    if not adimlar: return {"basari": False, "neden": "kayıt yok"}
    sh(f"ls -la {adimlar[-1]}/pp_00/tp_00/")
    open(f"{SP}/omnilingual_asr/cards/models/deng_k4_deneme.yaml", "w").write(
        f"name: deng_k4_deneme\nmodel_family: wav2vec2_llama\nmodel_arch: 1b_v2\ncheckpoint: {adimlar[-1]}\ntokenizer_ref: omniASR_tokenizer_written_v2\n")
    json.dump([{"yol": f"{VERI}/ses/{a}", "ref": m} for a, _, m in fl_dog], open(f"{T}/yukle-liste.json", "w"), ensure_ascii=False)
    open(f"{T}/yukle.py", "w").write(r"""
import json, sys, torch
from omnilingual_asr.models.inference.pipeline import ASRInferencePipeline
liste = json.load(open("/kaggle/temp/yukle-liste.json")); cikti = {}
for kart in ("deng_k4_deneme", "omniASR_LLM_1B_v2"):
    p = ASRInferencePipeline(model_card=kart, device="cuda", dtype=torch.float16)
    cikti[kart] = p.transcribe([x["yol"] for x in liste], lang=["kmr_Latn"] * len(liste), batch_size=4)
    del p; torch.cuda.empty_cache()
json.dump({"liste": liste, "hip": cikti}, open("/kaggle/working/yukle-sonuc.json", "w"), ensure_ascii=False, indent=1)
print("YÜKLEME TAMAM")
""")
    kartlar_bos()
    sh(f"cd {T} && CUDA_VISIBLE_DEVICES=0 {PY} {T}/yukle.py 2>&1 | grep -v Warning | tail -25")
    if not os.path.exists(f"{W}/yukle-sonuc.json"): return {"basari": False, "neden": "yükleme ya da yazma düştü"}
    sonuc = json.load(open(f"{W}/yukle-sonuc.json"))
    sh("pip install -q jiwer"); import jiwer, unicodedata
    def duz(t): t = unicodedata.normalize("NFC", t or "").lower(); return re.sub(r"\s+", " ", re.sub(r"[^\w\s']", " ", t)).strip()
    refs = [duz(x["ref"]) for x in sonuc["liste"]]
    cer = {k: round(100 * jiwer.cer(refs, [duz(h) or "-" for h in v]), 2) for k, v in sonuc["hip"].items()}
    print("YÜKLEME CER:", cer, flush=True)
    return {"basari": True, "cer": cer}
y = yukle_dene(r) if iyi(r) else {"basari": False, "neden": "eğitim olmadı"}
sonuclar.append({"yukleme": y}); json.dump(sonuclar, open(f"{W}/sigma.json", "w"), ensure_ascii=False, indent=1)

# 3) Dil kısmı: kodlayıcı sarmalamadan önce donuk
dene("dil", 320_000, ac=True, adim=10)
print("BİTTİ", round((time.time() - BASLA) / 60), "dk", flush=True)
