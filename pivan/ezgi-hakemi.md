# Ezgi hakemi: ilk sürüm ve Deneme 1'in yeniden ölçümü

*14 Ekim 2026 gecesi. Kayıt hattının A adımı. Hakem: `ezgi/hakem.py`, ağırlıklar `ezgi/hakem-agirlik.json`. Eğriler: `kaggle/ezgi-hakem` (yalnızca CPU, kart hakkı harcamaz).*

## Hakem nasıl çalışıyor

Cümlenin son saniyesindeki perde eğrisine bakar. Eğri konuşmacının kendi ortanca perdesine göre yarım ses (st) cinsindendir. İki ölçü kullanır:
- **son15:** Son 150 ms'in ortalama perdesi: cümle dipte mi bitiyor?
- **tepe60:** Son 600 ms'in en yüksek perdesi: sona yakın tepe var mı?

Bu iki ölçüden "soru gibi söylenmiş olma" olasılığını hesaplar. Hesap düz cümleyle evet/hayır sorusunu ayıran basit bir formül (lojistik bağlanım): ağırlıklar −0,75, +0,15 ve +0,35. Formül Common Voice 27'nin Kurmancî okuma kayıtlarıyla ayarlandı:
- 144 düz cümle
- 286 evet/hayır sorusu (yalnızca ezgiyle ya da "gelo/ma" ile)
- Her konuşmacıdan en çok 3 kayıt

**Sınama:** Hakemi ayarlarken görmediği konuşmacılarda sınadım: konuşmacılar beş gruba bölündü, her seferinde biri ayarın dışında tutuldu.

| | Doğru |
|---|---|
| Düz cümleyi "düz" buluyor | 128/144 = **%89** |
| Soruyu "soru gibi" buluyor | 196/286 = **%69** |

**Soruların üçte biri neden kaçıyor:** Common Voice okurlarının yaklaşık üçte biri soruyu zaten düz cümle gibi okumuş (bkz. `soru-ezgisi-cv.md`). Bu yüzden insan kaydında da %69 bir tavan. Soru sözcüklü sorularda ("çi, kengî, çawa") bu oran %63.

## Ses modellerinin ezgi denemesi (60 cümle: 15 soru, 45 düz)

| Model | Soru, soru gibi | Düz, düz gibi | Ölçülemeyen |
|---|---|---|---|
| **İnsan (CV okuması, yukarıdaki sınama)** | **%69** | **%89** | — |
| MMS (ticari değil, yalnız kıyas) | 2/15 (%13) | 42/45 (%93) | 0 |
| Anadil | 6/14 (%43) | 33/41 (%80) | 5 |
| VoxCPM2, eğitimsiz | 8/15 (%53) | 27/43 (%63) | 2 |
| **VoxCPM2 + LoRA, FLEURS ile (Deneme 1)** | **7/15 (%47)** | **41/45 (%91)** | 0 |

**Okuma:**
- **Eski ölçü Deneme 1'i olduğundan kötü göstermiş.** Eski ölçü "soruların yalnızca %27'si yükseliyor" diyordu; yeni hakeme göre soruların %47'si soru gibi. Yine de insanın %69'unun epey altında.
- **Eğitim düz cümleyi düzeltmiş, soruyu düzeltmemiş.** Eğitimsiz VoxCPM2 düz cümlelerin üçte birini yanlış ezgiyle bitiriyordu (%63); FLEURS'la eğitilince %91'e çıktı, insan düzeyine geldi. Sorularda kazanç yok. Sebep büyük olasılıkla veri: FLEURS haber cümlesi okuması, içinde neredeyse hiç soru yok.
- **Hangi sorular düşüyor (Deneme 1):**
  - **Doğru ezgi:** Kısa evet/hayır soruları ("Tu hatî?", "Ew birçî ye?"), "ma" soruları ve diyalog soruları.
  - **Düz cümle gibi düşenler:**
    - uzun evet/hayır soruları ("Çavên we vekirî ne?", "Tu serpêhatiya fîl û şêr dizanî?")
    - "gelo" soruları
    - soru sözcüklü soruların hepsi ("kengî, çawa, çend")
  - **İnsanla kıyas:** Common Voice okurları soru sözcüklü sorularda da çoğunlukla yükseliyor (%63).
- **Sayılar küçük:** 15 soruluk denemede bir sorunun farkı 7 puan. Bu sonuçlar yön gösterir, kesin yargı vermez. 340 cümlelik tam ezgi seti bu yüzden gerekli.

## Ne demek, ne yapılacak

1. **Ses modeline soru öğretmek için soru dolu doğal konuşma gerekiyor.** Skeçler, söyleşiler, sohbet podcastleri tam bu yüzden değerli; okuma verisi bunu vermiyor. İzin verilirse ezgi öğrenimine öncelikle soru içeren parçalar girer.
2. **Hakem sınırlı.** Yalnızca cümle sonunu ölçüyor. Vurgunun yeri, cümle içi ezgi ve duygu henüz yok. Ayrıca okuma kaydıyla ayarlandı; doğal sohbette yeniden ayarlanmalı. Bunu doğal sohbet kayıtları yapacak.
3. **Hakemin kendisi de sınanacak.** Dinleyicilerin "soru gibi mi?" yargısıyla karşılaştıracağım. Bunun için Kürtçe dinleme sayfası kurulacak; arayüz yazıları ana dili konuşanlarca onaylanır.
4. **Her ses modeli denemesinden sonra bu tablo yeniden çıkar.** Ezgi seti büyüdükçe sayılar sağlamlaşır.
