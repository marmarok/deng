"""Sınav kilidi: sınav setlerindeki cümleler hiçbir eğitime girmez.

Ezgi seti ve Botan sınav seti modelin ne kadar iyi olduğunu ölçer. Model bu cümleleri eğitimde
duyarsa ölçüm şişer ve kendimizi kandırırız. Her eğitim listesi bu süzgeçten geçer.

Kullanım:  from kilit import kilitli_mi;  [x for x in liste if not kilitli_mi(x["metin"])]
"""
import csv
import glob
import os
import re
import unicodedata

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def anahtar(metin: str) -> str:
    t = unicodedata.normalize("NFC", metin).lower()
    t = t.translate(str.maketrans("êîû", "eiu"))
    return re.sub(r"[^\w]+", " ", t).strip()


def _yukle():
    k = set()
    burasi = os.path.dirname(os.path.abspath(__file__))
    yollar = set()
    for kok in (KOK, burasi):  # projede bir üst klasör, Kaggle veri setinde aynı klasör
        yollar |= set(glob.glob(os.path.join(kok, "ezgi", "ezgi-seti.tsv")) + glob.glob(os.path.join(kok, "sinav", "*.tsv")))
    for yol in sorted(yollar):
        with open(yol, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                if r.get("cumle"):
                    k.add(anahtar(r["cumle"]))
    return k


KILITLI = _yukle()


def kilitli_mi(metin: str) -> bool:
    return anahtar(metin) in KILITLI
