"""Şapka düzeltici: şapkası unutulmuş ê, î, û harflerini geri koyar; Türkçe ı ve ü'yü de düzeltir.

Aynı kelime iki türlü yazılırsa ('ji' ve 'jî', 'te' ve 'tê', 'di' ve 'dî') model ikisini ayrı
öğrenir; ses yanlış okur, kulak yanlış yazar. Bu yüzden eğitim metni önce buradan geçer.

Nasıl çalışır: her kelimenin olası yazılışları bir ağ kurar; iki kelimelik dizilerin sayıları
(Common Voice ve Kürtçe Vikipedi'den) bütün cümleyi birlikte tartar. 'ji te re' gibi zincirler
tek tek değil, birlikte çözülür. Sözlükte hiç olmayan kelime bilinen kök + ek diye ayrılır.

Üç kip:
  sapkali   yazar şapka kullanıyor: bildiğimiz yazılışlara dokunulmaz, yalnızca sözlükte
            olmayan şapkasız yazılışlar düzeltilir
  sapkasiz  hiç şapka yok: her kelime yeniden tartılır
  dikkatli  kısa ve şapkasız, belli değil: yazılış zaten bir kelimeyse ancak öteki çok daha
            olasıysa değişir
Kip verilmezse metne bakılarak seçilir. Bir derlemin bütünü için kipi elle vermek daha iyidir.

Emin olunmayan seçimler `guven` ile döner; düzeltme sayfası bunları renkli gösterir.

Kullanım:  python3 sapka.py "Ez ji te hez dikim, tu ji bi min re we?"
"""
from __future__ import annotations

import gzip
import math
import os
import re
import sys
import unicodedata

SAPKA = set("êîû")
TURKCE = set("ıüīūé")
ANAHTAR = str.maketrans({"ê": "e", "î": "i", "û": "u", "ı": "i", "ü": "u", "ī": "i", "ū": "u", "é": "e"})
KELIME = re.compile(r"[^\W\d_]+")
CUMLE_ARASI = re.compile(r"[.!?…;:\n]")
SOZLUK_YOLU = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sapka-sozluk.tsv.gz")
if not os.path.exists(SOZLUK_YOLU):  # Kaggle veri seti .gz dosyasını açarak saklıyor
    SOZLUK_YOLU = SOZLUK_YOLU[:-3]

SAPKALI_ESIK = 0.02   # Kürtçe metinde harflerin ~%8'i şapkalı; %2'nin üstü şapka kullanıyor demek
KISA = 40             # bundan az harfli şapkasız metinde yazarın alışkanlığı belli değil
ALFA = 1.0            # yumuşatma
ADAY_ORAN = 0.005     # en sık yazılışın bu oranından az görülen yazılış aday sayılmaz
DIKKATLI_PAY = 20.0   # dikkatli kipte yazılmış hâlin öne geçme payı (kat)
BILINEN_PAY = 0.05    # şapkalı kipte yazılış, aynı anahtarın en az bu payını tutuyorsa dokunulmaz


def anahtar(kelime: str) -> str:
    return kelime.lower().translate(ANAHTAR)


def cumlelere_bol(metin: str) -> list[str]:
    return [c for c in re.split(r"(?<=[.!?…;:])\s+|\n+", metin) if c.strip()]


def _lse(xs):
    m = max(xs)
    return m + math.log(sum(math.exp(x - m) for x in xs))


class Sozluk:
    def __init__(self, yol: str = SOZLUK_YOLU):
        self.tek: dict[str, int] = {}
        self.adaylar: dict[str, list[str]] = {}
        self.ikili: dict[tuple[str, str], int] = {}
        self.saklanan: dict[str, int] = {}
        self.ekler: dict[str, dict[str, int]] = {}
        self.onekler: dict[str, dict[str, int]] = {}
        self.cumle = 1
        acici = gzip.open if yol.endswith(".gz") else open
        with acici(yol, "rt", encoding="utf-8") as f:
            for satir in f:
                if satir.startswith("#"):
                    continue
                tur, kelime, sonraki, sayi = satir.rstrip("\n").split("\t")
                n = int(sayi)
                if tur == "k":
                    self.tek[kelime] = n
                    self.adaylar.setdefault(anahtar(kelime), []).append(kelime)
                elif tur == "b":
                    self.ikili[(kelime, sonraki)] = n
                    self.saklanan[kelime] = self.saklanan.get(kelime, 0) + n
                elif tur == "n":
                    self.cumle = n
                elif tur == "e":
                    self.ekler.setdefault(anahtar(kelime), {})[kelime] = n
                elif tur == "o":
                    self.onekler.setdefault(anahtar(kelime), {})[kelime] = n
        self.toplam = sum(self.tek.values()) + self.cumle

    def p_tek(self, w: str) -> float:
        if w == "</s>":
            return self.cumle / self.toplam
        return (self.tek.get(w, 0) + 0.5) / self.toplam

    def gecis(self, h: str, w: str) -> float:
        """log P(w | h): saklanan ikiliden ya da, yoksa, saklanmayan pay × kelimenin sıklığı."""
        nh = self.cumle if h == "<s>" else self.tek.get(h)
        if not nh:
            return math.log(self.p_tek(w))
        n = self.ikili.get((h, w))
        if n:
            return math.log(n / (nh + ALFA))
        kalan = max(nh - self.saklanan.get(h, 0), 0)
        return math.log((kalan + ALFA) / (nh + ALFA)) + math.log(self.p_tek(w))


_sozluk: Sozluk | None = None


def sozluk() -> Sozluk:
    global _sozluk
    if _sozluk is None:
        _sozluk = Sozluk()
    return _sozluk


def kip(metin: str) -> str:
    harf = [c for c in metin.lower() if c.isalpha()]
    oran = sum(c in SAPKA for c in harf) / len(harf) if harf else 0
    if oran >= SAPKALI_ESIK or (oran > 0 and len(harf) < KISA):
        return "sapkali"
    return "dikkatli" if len(harf) < KISA else "sapkasiz"


def _bicim(ornek: str, kelime: str) -> str:
    """Büyük harf düzenini korur."""
    if ornek.isupper() and len(ornek) > 1:
        return kelime.upper()
    if ornek[:1].isupper():
        return kelime[:1].upper() + kelime[1:]
    return kelime


def _en_iyi(sz: Sozluk, a: str):
    ks = sz.adaylar.get(a)
    if not ks:
        return None
    k = max(ks, key=lambda c: sz.tek[c])
    return k, sz.tek[k] / sum(sz.tek[c] for c in ks)


def _parcala(sz: Sozluk, a: str):
    """Sözlükte olmayan kelime: bilinen kök + ek (ya da önek + kök) diye ayırmayı dener.

    'bêmalan' = 'bê' + 'malan', 'dikandarên' = 'dikandar' + 'ên'. Döner: (yazılış, güven) ya da None.
    """
    en = None
    for L in range(1, 6):
        if len(a) - L < 3:
            break
        for kok, parca, birlestir in ((_en_iyi(sz, a[:-L]), sz.ekler.get(a[-L:]), lambda k, e: k + e),
                                      (_en_iyi(sz, a[L:]), sz.onekler.get(a[:L]), lambda k, e: e + k)):
            if kok and parca:
                ek = max(parca, key=parca.get)
                pay = parca[ek] / sum(parca.values())
                p = math.log(sz.tek[kok[0]]) + math.log(pay)
                if en is None or p > en[0]:
                    en = (p, birlestir(kok[0], ek), min(0.75, kok[1] * pay))
    return (en[1], en[2]) if en else None


def _adaylar(sz: Sozluk, alt: str, kipi: str):
    """Bir kelimenin olası yazılışları: [(yazılış, ek puan)], ve tek seçenekse güveni."""
    a = anahtar(alt)
    turkce = any(c in TURKCE for c in alt)
    if not turkce and any(c in SAPKA for c in alt):
        return [(alt, 0.0)], None  # yazar şapkayı kendisi koymuş
    ks = sz.adaylar.get(a)
    if not ks:
        if kipi == "sapkali" and not turkce:
            return [(alt, 0.0)], None
        tahmin = _parcala(sz, a)
        if tahmin:
            return [(tahmin[0], 0.0)], tahmin[1]
        return [(a if turkce else alt, 0.0)], (0.6 if turkce else None)
    if kipi == "sapkali" and not turkce:
        if max(sz.tek[c] for c in ks) < 5:
            return [(alt, 0.0)], None
        if alt in sz.tek and sz.tek[alt] >= BILINEN_PAY * sum(sz.tek[c] for c in ks):
            return [(alt, 0.0)], None  # yazarın seçtiği yazılış yaygın: dokunma
    if kipi in ("dikkatli", "sapkali") and not turkce and alt in ks:
        return [(k, math.log(DIKKATLI_PAY) if k == alt else 0.0) for k in ks], None
    if len(ks) == 1:
        return [(ks[0], 0.0)], (0.95 if sz.tek[ks[0]] >= 20 else 0.8)
    return [(k, 0.0) for k in ks], None


def _coz(sz: Sozluk, kafes):
    """İleri-geri hesap: her konumda her yazılışın olasılığı. kafes: [[(yazılış, ek puan)], ...]"""
    n = len(kafes)
    ileri = []
    for i, adaylar in enumerate(kafes):
        satir = []
        for w, e in adaylar:
            if i == 0:
                satir.append(sz.gecis("<s>", w) + e)
            else:
                satir.append(_lse([ileri[i - 1][j] + sz.gecis(h, w) for j, (h, _) in enumerate(kafes[i - 1])]) + e)
        ileri.append(satir)
    geri = [None] * n
    geri[n - 1] = [sz.gecis(w, "</s>") for w, _ in kafes[n - 1]]
    for i in range(n - 2, -1, -1):
        geri[i] = [_lse([sz.gecis(w, v) + ev + geri[i + 1][j] for j, (v, ev) in enumerate(kafes[i + 1])])
                   for w, _ in kafes[i]]
    z = _lse([ileri[n - 1][j] + geri[n - 1][j] for j in range(len(kafes[n - 1]))])
    return [[math.exp(ileri[i][j] + geri[i][j] - z) for j in range(len(kafes[i]))] for i in range(n)]


def duzelt(metin: str, sz: Sozluk | None = None, kipi: str | None = None):
    """Metni düzeltir. Döner: (yeni metin, [(eski, yeni, güven), ...]).

    Listede değişen kelimeler ve iki yazılışı da olası olan kelimeler bulunur.
    güven: seçilen yazılışın olasılığı (0–1). 1'e yakınsa kesin, 0,5'e yakınsa yazı tura.
    """
    sz = sz or sozluk()
    t = unicodedata.normalize("NFC", metin)
    kipi = kipi or kip(t)
    parcalar = list(KELIME.finditer(t))
    secimler: list[tuple[str, float | None]] = []
    # cümle cümle çöz: noktalama cümleyi böler
    bas = 0
    for i in range(len(parcalar) + 1):
        son_mu = i == len(parcalar) or (i > 0 and CUMLE_ARASI.search(t[parcalar[i - 1].end():parcalar[i].start()]))
        if not son_mu or i == bas:
            continue
        kafes, tekler = [], []
        for m in parcalar[bas:i]:
            adaylar, guven = _adaylar(sz, m.group().lower(), kipi)
            kafes.append(adaylar)
            tekler.append(guven)
        olasilik = _coz(sz, kafes)
        for adaylar, p, g in zip(kafes, olasilik, tekler):
            j = max(range(len(adaylar)), key=lambda j: p[j])
            secimler.append((adaylar[j][0], g if len(adaylar) == 1 else p[j]))
        bas = i
    degisen = []
    cikti, son = [], 0
    for m, (secilen, guven) in zip(parcalar, secimler):
        eski = m.group()
        yeni = eski if secilen == eski.lower() else _bicim(eski, secilen)
        if guven is not None and (yeni != eski or guven < 0.9):
            degisen.append((eski, yeni, round(guven, 3)))
        cikti.append(t[son:m.start()])
        cikti.append(yeni)
        son = m.end()
    cikti.append(t[son:])
    return "".join(cikti), degisen


if __name__ == "__main__":
    for satir in (sys.argv[1:] or sys.stdin.read().splitlines()):
        yeni, degisen = duzelt(satir)
        print(yeni)
        for eski, y, g in degisen:
            print(f"   {eski} → {y}  (güven {g:.2f})")
