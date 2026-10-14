# Ezgi hakemini ses modellerinin ezgi denemesi kayıtlarına uygular.
# Kullanım: python3 hakem_uygula.py egriler.jsonl cumleler.json hakem-agirlik.json
import json, sys, collections, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hakem import Hakem, ozellik
egriler = [json.loads(l) for l in open(sys.argv[1])]
cumle = {c["no"].zfill(2): c for c in json.load(open(sys.argv[2]))}
h = Hakem(json.load(open(sys.argv[3]))["w"])
say = collections.defaultdict(lambda: {"soru": [0, 0], "düz": [0, 0], "bos": 0})
ayrinti = []
for e in egriler:
    no = e["dosya"].split(".")[0].zfill(2)
    c = cumle.get(no)
    if not c: continue
    tur = "soru" if c["cumle"].strip().endswith("?") else "düz"
    x = ozellik(e["egri"]) if e["egri"] else None
    if not x: say[e["model"]]["bos"] += 1; continue
    p = h.p(x)
    dogru = (p >= 0.5) == (tur == "soru")
    say[e["model"]][tur][0] += dogru; say[e["model"]][tur][1] += 1
    ayrinti.append({"model": e["model"], "no": no, "cumle": c["cumle"], "tur": tur, "p_soru": round(p, 2), "son15": round(x[0], 1), "tepe60": round(x[1], 1)})
for m, s in sorted(say.items()):
    print(f"{m:22s} soruyu soru gibi: {s['soru'][0]}/{s['soru'][1]}   düzü düz gibi: {s['düz'][0]}/{s['düz'][1]}   ölçülemeyen: {s['bos']}")
json.dump(ayrinti, open("hakem-ayrinti.json", "w"), ensure_ascii=False, indent=1)
