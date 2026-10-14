# Ezgi hakemi için eğri çıkarma (yalnızca CPU): ses modellerinin ezgi denemesi kayıtlarında cümle sonu perde eğrisi.
# Kaynaklar: durak0-cita (VoxCPM2, Anadil, MMS; eğitimsiz) ve deneme1-fleurs (VoxCPM2 + LoRA, FLEURS ile).
# Eğri, ezgi-olcum defterindeki son_ezgi ile birebir aynı yöntemle çıkar (hakem onunla ayarlandı).
import os, glob, json, subprocess
subprocess.run("pip install -q silero-vad librosa soundfile", shell=True)
import numpy as np, torch, librosa
from silero_vad import load_silero_vad, get_speech_timestamps
ORAN = 16000; ADIM = 160
vad = load_silero_vad()
def oku(yol):
    ham = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", yol, "-ac", "1", "-ar", str(ORAN), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(ham, dtype=np.float32).copy()
def egri(d):
    b = get_speech_timestamps(torch.from_numpy(d), vad, sampling_rate=ORAN)
    if not b: return None
    d = d[b[0]["start"]: b[-1]["end"]]
    f0, ses, _ = librosa.pyin(d, fmin=60, fmax=500, sr=ORAN, frame_length=1024, hop_length=ADIM)
    f0 = np.where(ses, f0, np.nan)
    if np.sum(~np.isnan(f0)) < 30: return None
    st = 12 * np.log2(f0 / np.nanmedian(f0))
    son = np.where(~np.isnan(st))[0][-1]
    return [None if np.isnan(v) else round(float(v), 2) for v in st[max(0, son - 99): son + 1]]
cikti = []
for yol in sorted(glob.glob("/kaggle/input/**/*.wav", recursive=True)):
    parca = yol.split("/")
    model = "voxcpm2-lora-fleurs" if "deneme1" in yol else parca[-2]
    if model == "ses": model = "voxcpm2-lora-fleurs"
    try: e = egri(oku(yol))
    except Exception as x: e = None; print("hata", yol, x)
    cikti.append({"model": model, "dosya": parca[-1], "yol": yol, "egri": e})
    print(model, parca[-1], "tamam" if e else "boş", flush=True)
with open("/kaggle/working/egriler.jsonl", "w") as f:
    for c in cikti: f.write(json.dumps(c, ensure_ascii=False) + "\n")
print("BİTTİ", len(cikti))
