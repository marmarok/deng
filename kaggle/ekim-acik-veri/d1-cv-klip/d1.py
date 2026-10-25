# D1 listening test v1: the 30 human Common Voice readings (public CV24 copy SECT19N, CC0) of the chosen intonation
# sentences (olcumler/dinleme-v1/secim-kurali.md). CPU only; nothing else is kept. Output: cv/<stem>.wav, info.json.
import os, json, time, tarfile, subprocess, urllib.request
START = time.time()
DEADLINE_S = 1 * 3600
W = "/kaggle/working"; T = "/kaggle/temp"; os.makedirs(f"{W}/cv", exist_ok=True); os.makedirs(T, exist_ok=True)
WANT = set(["common_voice_kmr_24842076", "common_voice_kmr_24842263", "common_voice_kmr_24845633", "common_voice_kmr_24845905", "common_voice_kmr_24847982", "common_voice_kmr_24858783", "common_voice_kmr_24870315", "common_voice_kmr_24888280", "common_voice_kmr_24895964", "common_voice_kmr_25038541", "common_voice_kmr_25068062", "common_voice_kmr_25391485", "common_voice_kmr_25487733", "common_voice_kmr_25489062", "common_voice_kmr_26017063", "common_voice_kmr_27244397", "common_voice_kmr_32075842", "common_voice_kmr_34782394", "common_voice_kmr_34816904", "common_voice_kmr_34821650", "common_voice_kmr_34845470", "common_voice_kmr_34859799", "common_voice_kmr_34905710", "common_voice_kmr_34933403", "common_voice_kmr_34972602", "common_voice_kmr_34983419", "common_voice_kmr_35131653", "common_voice_kmr_35397517", "common_voice_kmr_36442836", "common_voice_kmr_36956173"])
URL = "https://huggingface.co/datasets/SECT19N/Preprocessed-CVS-24-KMR/resolve/main/Common_Voice_Kurmanji_Kurdish_Processed_Audio.tar.gz"
size = int(urllib.request.urlopen(urllib.request.Request(URL, method="HEAD"), timeout=120).headers.get("Content-Length") or 0)
TGZ = f"{T}/cv24.tar.gz"
for _ in range(10):
    if time.time() - START > DEADLINE_S - 900: break
    subprocess.run(["curl", "-sL", "-C", "-", "--retry", "5", "-o", TGZ, URL], timeout=max(60, DEADLINE_S - 900 - (time.time() - START)))
    if size and os.path.getsize(TGZ) >= size: break
got = []
with tarfile.open(TGZ, "r|gz") as tf:
    for m in tf:
        stem = os.path.basename(m.name).rsplit(".", 1)[0]
        if m.isfile() and stem in WANT:
            open(f"{W}/cv/{stem}.wav", "wb").write(tf.extractfile(m).read()); got.append(stem)
        if len(got) == len(WANT) or time.time() - START > DEADLINE_S - 300: break
json.dump({"wanted": len(WANT), "found": len(got), "missing": sorted(WANT - set(got)), "minutes": round((time.time() - START) / 60, 1)}, open(f"{W}/info.json", "w"), indent=1)
print("DONE", len(got), flush=True)
