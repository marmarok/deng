# Şapka düzeltici ölçümü (14.10.2026)

**Araç:** `metin/sapka.py`, sözlüğü `metin/sapka-sozluk.tsv.gz` (2 MB). Sözlük `metin/sapka_sozluk_yap.py` ile kurulur. Kaynaklar:
- Common Voice kmr cümleleri: 17 bin cümle, CC0, 10 kat ağırlık.
- Kürtçe Vikipedi: 63 bin madde. Yalnızca kelime sayıları alındı, metin alınmadı.

**Nasıl çalışıyor:**
- Her kelimenin olası yazılışları bir ağ kurar.
- İki kelimelik dizilerin sayıları bütün cümleyi birlikte tartar.
- Sözlükte olmayan kelime "bilinen kök + ek" diye ayrılır: "dikandarên", "dikandar" ile "-ên"e ayrılır.
- Türkçe ı ve ü de düzeltilir.

**Sınav:** Common Voice cümlelerinin %10'u sözlüğe sokulmadı (1.699 cümle, 11.050 kelime). Bu cümlelerin şapkaları silindi, araç geri koymaya çalıştı.

| | Doğru kelime |
|---|---|
| Şapkasız bırakılsa | %60,8 |
| Düzeltmeden sonra | **%95,9** |
| Şapkalı kelimelerin geri gelmesi | %92,9 |
| Kısa şapkasız cümlede (40 harften az) | %92,2 |

**Doğru metni bozuyor mu?** Şapka kullanan metinde 1.699 cümlenin 16'sında bir kelime değişti.
- **Çoğu, Common Voice'taki gerçek yazım hatalarının düzeltilmesi:**
  - sere xwe → serê xwe
  - nişan → nîşan
  - disa → dîsa
  - biminin → bimînin
  - aşitiye → aşitiyê
  - serokwezir → serokwezîr
- **Yanlışları:**
  - zanin → zanîn: "hûn zanin" konuşma dilinde "di-"siz fiil, araç onu mastar sandı.
  - nealiqim → nealiqîm: "-im" eki yanlışlıkla "-îm" oldu.
  - bilançoya → bîlançoya.
  - nexweşe → nexweşê: doğrusu "nexweş e".

**Kalan hatalar:** Şapkasız metindeki hataların üçte biri, iki yazılışı da doğru olan kelimelerde: we/wê, te/tê, ji/jî, de/dê. "Nimêjên we" de "nimêjên wê" de doğru bir cümle; hangisi olduğunu ancak anlam söyler. İki kelimelik dizi buna yetmez.

**Kullanım kuralı:**
- Eğitim metni (Common Voice, FLEURS, editör yazıları) derlem olarak "sapkali" kipte geçirilir. Bu kipte bilinen yazılışlara dokunulmaz.
- Şapkasız yazılmış dış metinler "sapkasiz" kipte geçirilir. Güveni düşük çıkan kelimeler düzeltme sayfasında renkli gösterilir.

**Sonra iyileşebilecekler:**
- c/ç, s/ş karışması: İngilizce klavye. Türkçe klavyede ç ve ş olduğu için şimdilik dışarıda.
- Üç kelimelik dizi.
- Editörlerin düzelttiği yazılarla sözlüğün büyümesi.
