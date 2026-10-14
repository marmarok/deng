import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hazirla import hazirla, sayi

def test_sayilar():
    assert sayi(0) == "sifir"
    assert sayi(15) == "panzdeh"
    assert sayi(21) == "bîst û yek"
    assert sayi(100) == "sed"
    assert sayi(250) == "du sed û pêncî"
    assert sayi(1000) == "hezar"
    assert sayi(1986) == "hezar û neh sed û heştê û şeş"
    assert sayi(2026) == "du hezar û bîst û şeş"
    assert sayi(1_000_000) == "yek milyon"

def test_cumleler():
    assert hazirla("Ez di sala 1986'an de ji dayik bûm.") == "Ez di sala hezar û neh sed û heştê û şeşan de ji dayik bûm."
    assert hazirla("Li gundê me 1.250 kes dijîn.") == "Li gundê me hezar û du sed û pêncî kes dijîn."
    assert hazirla("Otobus di saet 7:30'an de rê dikeve.") == "Otobus di saet heft û nîvan de rê dikeve."
    assert hazirla("%50 erzan e.") == "ji sedî pêncî erzan e."
    assert hazirla("Sêv, hirmî hwd.") == "Sêv, hirmî her wekî din."
    assert hazirla("Ew 2 sal in.") == "Ew du sal in."

def test_sapka():
    from hazirla import hazirla_ayrintili
    import sapka
    if not os.path.exists(sapka.SOZLUK_YOLU):
        return
    assert hazirla("Tu ji kudere yi? Ez ji Merdine me.") == "Tu ji kuderê yî? Ez ji Mêrdînê me."
    assert hazirla("Em ê sibe herin bajer, li wir hevalen me hene.") == "Em ê sibe herin bajêr, li wir hevalên me hene."
    assert hazirla("Dıkım, nızanım.") == "Dikim, nizanim."
    # şapkasını kendisi koyan yazara dokunulmaz
    assert hazirla("Ez û tu jî bi hev re diçin malê.") == "Ez û tu jî bi hev re diçin malê."
    # sayı ile birlikte
    assert hazirla("Ez 3 sal li Merdine mam.") == "Ez sê sal li Mêrdînê mam."
    metin, degisen = hazirla_ayrintili("Navê min Azad e, ez ji Botane me.")
    assert metin == "Navê min Azad e, ez ji Botanê me."
    assert ("Botane", "Botanê") in [(e, y) for e, y, _ in degisen]
    # kapatılabilir
    assert hazirla("Ez ji Merdine me.", sapka_duzelt=False) == "Ez ji Merdine me."


if __name__ == "__main__":
    test_sayilar(); test_cumleler(); test_sapka(); print("hepsi geçti")
