# Ezgi hakemi: cümle sonu perde eğrisinden "soru gibi mi söylenmiş?" puanı.
# Girdi: son 1 saniyenin eğrisi (10 ms'lik kareler, konuşmacının ortanca perdesine göre yarım ses; sesiz kare None).
# Ölçüler (Common Voice'ta bulundu, 14.10): Kürtçe evet/hayır sorusunda perde sona ~0,3 sn kala tepe yapar
# ve dibe düşmez; düz cümlede son saniyede ~3 yarım ses iner. Eski ölçü ("son 150 ms öncekinden yüksek mi")
# bu tepeyi kaçırıyordu.
import json, math, random, sys

def ozellik(egri):
    """(son15, tepe60): son 150 ms'in ortalaması ve son 600 ms'in tepesi, yarım ses."""
    e = [v for v in egri if v is not None]
    if len(egri) < 30: return None
    son = [v for v in egri[-15:] if v is not None]
    tepe = [v for v in egri[-60:] if v is not None]
    if len(son) < 4 or len(tepe) < 10: return None
    return (sum(son) / len(son), max(tepe))

class Hakem:
    """Lojistik: p(soru) = 1 / (1 + exp(-(w0 + w1*son15 + w2*tepe60)))."""
    def __init__(self, w=(0.0, 0.0, 0.0)): self.w = list(w)
    def p(self, x):
        z = self.w[0] + self.w[1] * x[0] + self.w[2] * x[1]
        return 1 / (1 + math.exp(-max(-30, min(30, z))))
    def egit(self, X, y, adim=4000, oran=0.05, l2=1e-3):
        # sınıflar eşit ağırlıklı: soru örneği düzden iki kat fazla, eşik ona kaymasın
        n = len(X); n1 = sum(y); n0 = n - n1
        a = {1: n / (2 * n1), 0: n / (2 * n0)}
        for _ in range(adim):
            g = [0.0, 0.0, 0.0]
            for x, t in zip(X, y):
                d = (self.p(x) - t) * a[t]
                g[0] += d; g[1] += d * x[0]; g[2] += d * x[1]
            for i in range(3): self.w[i] -= oran * (g[i] / n + (l2 * self.w[i] if i else 0))
        return self

def yukle(yol):
    satir = [json.loads(l) for l in open(yol)]
    return [(r, ozellik(r["egri"])) for r in satir if ozellik(r["egri"])]

if __name__ == "__main__":
    veri = yukle(sys.argv[1])
    SORU = ("soru: yalnızca ezgi", "soru: gelo/ma")
    ayar = [(r, x) for r, x in veri if r["tur"] == "düz" or r["tur"] in SORU]
    # konuşmacıya göre 5 katlı çapraz sınama (aynı konuşmacı hem eğitimde hem sınamada olmasın)
    kisiler = sorted({r["konusmaci"] for r, _ in ayar}); random.Random(1).shuffle(kisiler)
    kat = {k: i % 5 for i, k in enumerate(kisiler)}
    dogru = {"düz": [0, 0], "soru": [0, 0]}
    for f in range(5):
        egt = [(x, 1 if r["tur"] in SORU else 0) for r, x in ayar if kat[r["konusmaci"]] != f]
        h = Hakem().egit([x for x, _ in egt], [t for _, t in egt])
        for r, x in ayar:
            if kat[r["konusmaci"]] != f: continue
            sinif = "soru" if r["tur"] in SORU else "düz"
            tahmin = "soru" if h.p(x) >= 0.5 else "düz"
            dogru[sinif][0] += tahmin == sinif; dogru[sinif][1] += 1
    print("çapraz sınama (konuşmacıya göre):", {k: f"{a}/{b} = {a/b:.0%}" for k, (a, b) in dogru.items()})
    h = Hakem().egit([x for _, x in ayar], [1 if r["tur"] in SORU else 0 for r, _ in ayar])
    print("ağırlıklar:", [round(v, 3) for v in h.w])
    for tur in ("düz", "soru: yalnızca ezgi", "soru: gelo/ma", "soru: soru sözcüklü"):
        ps = [h.p(x) for r, x in veri if r["tur"] == tur]
        print(f"{tur:22s} soru gibi: {sum(p >= 0.5 for p in ps)}/{len(ps)} = {sum(p >= 0.5 for p in ps)/len(ps):.0%}")
    json.dump({"w": h.w, "aciklama": "p(soru)=sigmoid(w0+w1*son15+w2*tepe60); CV 27 kmr okuma kaydıyla ayarlandı (düz vs evet/hayır sorusu)"},
              open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
