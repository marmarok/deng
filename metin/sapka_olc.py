"""Şapka düzelticiyi ölçer. Common Voice cümlelerinin ~%10'u sözlüğe girmez; bu cümlelerin
şapkaları silinir, düzeltici geri koymaya çalışır. Ayrıca doğru cümleleri bozuyor mu, bakılır.

Kullanım:  python3 sapka_olc.py <validated_sentences.tsv> <vikipedi.txt>
"""
import hashlib
import io
import os
import sys
import tempfile

import sapka
from sapka_sozluk_yap import cv_cumleleri, kur


def sinav_mi(cumle):
    return hashlib.md5(cumle.encode()).digest()[0] < 26  # ~%10


def sil(metin):
    return metin.translate(str.maketrans("êîûÊÎÛ", "eiuEIU"))


def dogru_orani(sinav, sz, kipi):
    dogru = toplam = sapkali = sapkali_dogru = 0
    for c in sinav:
        yeni, _ = sapka.duzelt(sil(c), sz, kipi)
        for a, t in zip(sapka.KELIME.findall(c), sapka.KELIME.findall(yeni)):
            toplam += 1
            dogru += a == t
            if any(h in a.lower() for h in "êîû"):
                sapkali += 1
                sapkali_dogru += a == t
    return dogru / toplam, sapkali_dogru / max(sapkali, 1), toplam


def sozluk_kur(egitim, viki_yolu):
    tampon = io.StringIO()
    kur(egitim, viki_yolu, tampon.write)
    yol = os.path.join(tempfile.gettempdir(), "sapka-olc.tsv")
    with open(yol, "w", encoding="utf-8") as f:
        f.write(tampon.getvalue())
    return sapka.Sozluk(yol)


def main(cv_yolu, viki_yolu):
    cv = cv_cumleleri(cv_yolu)
    sinav = [c for c in cv if sinav_mi(c)]
    sz = sozluk_kur([c for c in cv if not sinav_mi(c)], viki_yolu)

    ham = sum(a == sil(a) for c in sinav for a in sapka.KELIME.findall(c))
    oran, sapkali, toplam = dogru_orani(sinav, sz, "sapkasiz")
    print(f"sınav: {len(sinav)} cümle, {toplam} kelime")
    print(f"şapkasız bırakılsa doğru kelime:        %{100 * ham / toplam:.1f}")
    print(f"düzeltmeden sonra doğru kelime:          %{100 * oran:.1f}")
    print(f"şapkalı kelimelerin geri gelme oranı:    %{100 * sapkali:.1f}")
    kisa = [c for c in sinav if sapka.kip(sil(c)) == "dikkatli" and sil(c) != c]
    oran_k, _, _ = dogru_orani(kisa, sz, None)
    print(f"kısa şapkasız cümlede (kendi kipiyle):   %{100 * oran_k:.1f} ({len(kisa)} cümle)")
    for kipi in ("sapkali", None):
        bozulan = sum(sapka.duzelt(c, sz, kipi)[0] != unicodedata_nfc(c) for c in sinav)
        print(f"doğru cümlede değişen ({kipi or 'kendi kipi'}): {bozulan} / {len(sinav)}")


def unicodedata_nfc(c):
    import unicodedata
    return unicodedata.normalize("NFC", c)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
