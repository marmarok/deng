"""Metin hazırlayıcı: Kürtçe metni eğitime ve seslendirmeye hazırlar.

1. Şapkası unutulmuş ê, î, û harflerini geri koyar (sapka.py).
2. Sayı, saat, tarih, yüzde ve kısaltmaları sesli okunacak kelimelere çevirir.
   Ses modeli rakamı değil kelimeyi okur; kulak da kelimeyi yazmayı öğrenir.

Kullanım:  python3 hazirla.py "Ez di sala 1986'an de ji dayik bûm."
Emin olunmayan seçimler `INCELE` listesinde; dil editörleri onaylayana kadar taslaktır.
"""
from __future__ import annotations

import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sapka  # noqa: E402

BIRLER = ["sifir", "yek", "du", "sê", "çar", "pênc", "şeş", "heft", "heşt", "neh"]
ON_LAR = {10: "deh", 11: "yanzdeh", 12: "dwanzdeh", 13: "sêzdeh", 14: "çardeh",
          15: "panzdeh", 16: "şanzdeh", 17: "hivdeh", 18: "hejdeh", 19: "nozdeh"}
ONLAR = {20: "bîst", 30: "sî", 40: "çil", 50: "pêncî", 60: "şêst", 70: "heftê",
         80: "heştê", 90: "nod"}
BUYUK = [(10**9, "milyar"), (10**6, "milyon"), (1000, "hezar")]

MEHAN = ["kanûna paşîn", "sibat", "adar", "nîsan", "gulan", "hezîran", "tîrmeh",
         "tebax", "îlon", "cotmeh", "mijdar", "kanûna pêşîn"]

KURTE = {  # kısaltma (noktasız) -> açılımı
    "hwd": "her wekî din",
    "Dr": "doktor",
    "Prof": "profesor",
}

# Dil editörlerinin onaylaması gereken seçimler (Botan ağzı için de kontrol edilecek)
INCELE = [
    "11–19: yanzdeh/yazdeh, dwanzdeh/diwanzdeh, hivdeh/hevdeh — yazı dili biçimi seçildi",
    "Ondalık: '2,5' -> 'du xal pênc' (xal = virgül/nokta); '2,5' için 'du û nîv' daha doğal olabilir",
    "Saat: ':30' -> 'û nîv', ':15' -> 'û çaryek', ':45' -> 'kêm çaryek' (bir sonraki saat), diğerleri 'û N deqe'",
    "Tarih: '13.10.2026' -> 'sêzdehê cotmeha du hezar û bîst û şeşan'",
    "Sıra sayısı: '3em' -> 'sêyem', '1em' -> 'yekem'",
    "Ek: rakamdan sonra kesme işaretli ek ('1986'an') son kelimeye eklenir; ünlüyle bitiyorsa araya 'y' girer",
]


def sayi(n: int) -> str:
    """Tam sayıyı Kürtçe kelimeye çevirir: 1986 -> 'hezar û neh sed û heştê û şeş'."""
    if n < 0:
        return "kêm " + sayi(-n)
    if n < 10:
        return BIRLER[n]
    if n < 20:
        return ON_LAR[n]
    if n < 100:
        on, bir = divmod(n, 10)
        return ONLAR[on * 10] + ("" if bir == 0 else " û " + BIRLER[bir])
    if n < 1000:
        yuz, kalan = divmod(n, 100)
        bas = "sed" if yuz == 1 else BIRLER[yuz] + " sed"
        return bas + ("" if kalan == 0 else " û " + sayi(kalan))
    for deger, ad in BUYUK:
        if n >= deger:
            kat, kalan = divmod(n, deger)
            bas = ad if (kat == 1 and deger == 1000) else sayi(kat) + " " + ad
            return bas + ("" if kalan == 0 else " û " + sayi(kalan))
    raise ValueError(n)


def ek_ekle(kelime: str, ek: str) -> str:
    """'şeş' + 'an' -> 'şeşan'; 'du' + 'an' -> 'duyan'."""
    if not ek:
        return kelime
    if kelime[-1] in "aeêiîouû" and ek[0] in "aeêiîouû":
        return kelime + "y" + ek
    return kelime + ek


def sira(n: int) -> str:
    """Sıra sayısı: 1 -> yekem, 2 -> duyem, 20 -> bîstem."""
    return ek_ekle(sayi(n), "em")


def saat(h: int, m: int) -> str:
    if m == 0:
        return sayi(h)
    if m == 30:
        return sayi(h) + " û nîv"
    if m == 15:
        return sayi(h) + " û çaryek"
    if m == 45:
        return sayi(h % 12 + 1) + " kêm çaryek"
    return sayi(h) + " û " + sayi(m) + " deqe"


def _tam(s: str) -> int:
    return int(s.replace(".", ""))


def hazirla(metin: str, sapka_kipi: str | None = None, sapka_duzelt: bool = True) -> str:
    """sapka_kipi: 'sapkali', 'sapkasiz', 'dikkatli' ya da None (metne bakılarak seçilir)."""
    return hazirla_ayrintili(metin, sapka_kipi, sapka_duzelt)[0]


def hazirla_ayrintili(metin: str, sapka_kipi: str | None = None, sapka_duzelt: bool = True):
    """Döner: (hazır metin, şapka değişiklikleri [(eski, yeni, güven)])."""
    t = unicodedata.normalize("NFC", metin)
    degisen = []
    if sapka_duzelt and os.path.exists(sapka.SOZLUK_YOLU):
        t, degisen = sapka.duzelt(t, kipi=sapka_kipi)
    return _sayilar(t), degisen


def _sayilar(t: str) -> str:
    for k, v in KURTE.items():
        # kısaltmanın noktası cümle sonundaysa korunur (ezgi için önemli)
        t = re.sub(r"(?<!\w)" + re.escape(k) + r"\.(?=\s*$)", v + ".", t)
        t = re.sub(r"(?<!\w)" + re.escape(k) + r"\.?(?!\w)", v, t)

    # Tarih: 13.10.2026 veya 13/10/2026
    def tarih(m):
        g, a, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if not (1 <= a <= 12 and 1 <= g <= 31):
            return m.group(0)
        return f"{ek_ekle(sayi(g), 'ê')} {ek_ekle(MEHAN[a - 1], 'a')} {ek_ekle(sayi(y), 'an')}"
    t = re.sub(r"\b(\d{1,2})[./](\d{1,2})[./](\d{4})\b", tarih, t)

    # Saat: 7:30 (ardından isteğe bağlı 'an gibi ek)
    def saat_r(m):
        h, mi, ek = int(m.group(1)), int(m.group(2)), m.group(3) or ""
        if h > 24 or mi > 59:
            return m.group(0)
        return ek_ekle(saat(h, mi), ek)
    t = re.sub(r"\b(\d{1,2}):(\d{2})(?:['’](\w+))?", saat_r, t)

    # Yüzde: %50 veya % 50
    t = re.sub(r"%\s?(\d+)", lambda m: "ji sedî " + sayi(int(m.group(1))), t)

    # Sıra sayısı: 3em, 3emîn, 3'em
    t = re.sub(r"\b(\d+)['’]?(emîn|em)\b", lambda m: ek_ekle(sira(int(m.group(1))), m.group(2)[2:]), t)

    # Ondalık: 2,5
    t = re.sub(r"\b(\d+),(\d+)\b",
               lambda m: sayi(int(m.group(1))) + " xal " + " ".join(BIRLER[int(c)] for c in m.group(2)), t)

    # Tam sayı (binlik noktalı olabilir) + isteğe bağlı kesme işaretli ek
    def tam(m):
        return ek_ekle(sayi(_tam(m.group(1))), m.group(2) or "")
    t = re.sub(r"\b(\d{1,3}(?:\.\d{3})+|\d+)(?:['’](\w+))?", tam, t)
    return re.sub(r"\s+", " ", t).strip()


if __name__ == "__main__":
    for satir in (sys.argv[1:] or sys.stdin.read().splitlines()):
        print(hazirla(satir))
