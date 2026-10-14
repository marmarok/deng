# K2 ön sınav ve temel kulak seçimi

*14 Ekim 2026. Kritik nokta 3. Seçim bu belgede. Sayılar K2'nin 6. koşusunun `sonuc.json` dosyasıyla doğrulandı (14.10 20:36); hipotezler `kaggle/k2-kulak-sinavi/cikti/kosu6/`.*

## Sınav

- **FLEURS-Kobani test:** 499 cümle, 107 dakika. Okuma; Kobanê ağzı.
- **Common Voice 27 test:** 500 cümle, 39 dakika. Okuma; karışık ağızlar.
- **Değerlendirme:** İki yazı da aynı metin hazırlayıcıdan geçirildi (şapka, noktalama, büyük harf).
- **Kart:** Kaggle T4, 16 GB.

## Sonuçlar

| Model | Parametre | FLEURS WER | FLEURS CER | CV WER | CV CER | Hız (T4) | Tek T4'te eğitim |
|---|---|---|---|---|---|---|---|
| Omnilingual CTC 300M v2 | 0,33 milyar | 48,1 | 13,2 | 42,2 | 13,5 | çok hızlı | Sığıyor (K3'te eğitiliyor) |
| Omnilingual CTC 1B v2 | 0,98 milyar | 37,3 | 10,4 | 29,0 | 9,3 | 146 dakikalık ses 3 dakikadan kısa sürede, gerçek zamanın en az 50 katı | Sığmaz; iki kartla paylaştırınca sığar |
| **Omnilingual LLM 1B v2** | **2,28 milyar** | **31,4** | **9,1** | **16,4** | **4,1** | ~47 dakika, gerçek zamanın ~3 katı (4'lü toplu; bellek 7,4 GB, toplu büyütülebilir) | **Sığmaz:** tam eğitim ~36 GB ister |
| Omnilingual CTC 3B v2 | 3,08 milyar | — | — | — | — | 16'lık toplulukta bellek taştı; küçük toplulukla yeniden ölçülecek | Sığmaz |
| Omnilingual LLM 3B v2 | 4,38 milyar | 30,8 | 8,8 | 15,6 | 3,9 | ~52 dakika (bellek 11,6 GB) | Sığmaz |
| MMS-1B (yalnız kıyas, ticari değil) | 1 milyar | 43,0 | 12,0 | 28,3 | 6,3 | hızlı | — |
| Kürtçe Whisper (yalnız kıyas, lisansı yok) | 1,5 milyar | 38,4 | 13,1 | 3,4 | 3,7 | ~45 dakika | — |

**Okuma notları:**
- **Hakem test FLEURS:** Common Voice cümleleri sınırlı bir metin kümesinden geliyor. Omnilingual'ın ve Kürtçe Whisper'ın eğitim verisinde Common Voice var ya da olabilir; bu yüzden CV sonuçları şişkin olabilir. Kürtçe Whisper'ın 3,4'ü büyük olasılıkla bundan. Hakem test bu nedenle FLEURS.
- **FLEURS'ta LLM 1B'nin farkı:** En yakın açık adaydan (CTC 1B) 100 kelimede 6 kelime daha az hata yapıyor (37 yerine 31). Kürtçe Whisper'dan 7 kelime daha az.
- **Yayımlanmış en iyi sonuçla kıyas:** Plana yazdığımız en iyi Kürtçe sonuç, Whisper large-v3'ün ~68 saatle eğitilmiş hali: CV'de 100 harfte 5,7 hata. LLM 1B hiç eğitilmeden CV'de 4,1. Yukarıdaki CV şerhi burada da geçerli.
- **Ölçülmeyenler:** Bunlar okuma kaydı. Doğal sohbette hepsi daha çok hata yapacak. Asıl sınav Botan sohbet seti.

## Hata türleri (FLEURS ve CV, 999 cümle)

- **Uydurma yok:** LLM modellerinde sesten çok uzun ya da boş çıktı, anlamsız tekrar görülmedi. Tekrar gibi görünen birkaç cümle, "802.11a, 802.11b…" gibi gerçekten tekrar eden sayılardı.
- **Türkçeye kayma yok:** Türkçe harf (ı, ğ, ö, ü) yalnızca "Erdoğan" adında çıktı; bu doğru.
- **LLM 1B'nin CTC 1B'den kötü olduğu cümleler:** Çoğu sayı ("1963an", "802.11g"). LLM sayıyı kelimeyle yazıyor. Metin hazırlayıcımız sayıları kelimeye çevirdiği için ana tabloda bu hata sayılmıyor; ama "neh sed" yerine "nahsad" gibi yazım farkları kalıyor.
- **Hataların çoğu yer değiştirme:** FLEURS'ta yanlış kelimelerin büyük kısmı tek harf ya da yazım alışkanlığı farkı. Örnekler: "alîyê" ile "aliyê", "rawestîyan" ile "rawestiyan", "Fransiz" ile "fransîz". FLEURS'un kendi yazımı standart yazımdan biraz farklı. Gerçek hata oranı tablodakinden düşük. Bu yazım farkları metin biçimi kurallarında ayrıca ele alınacak (kritik nokta 1).

## Seçim

**Temel kulak: Omnilingual LLM 1B v2.** Kürtçe kulağımız bunun üstüne eğitilecek.

**Neden:**
1. **En az hata:** İki sınav setinde de en az hatayı yapıyor; hakem testte (FLEURS) farkı açık.
2. **Anlamdan yararlanıyor:** Projenin temel sorusunun cevabı bu. Yazarken önceki kelimelere bakan bir dil modeli var. Şapkalı harfler ve kelime sınırları gibi Kürtçe yazım ayrıntılarında bu belirgin fark yarattı: CV'de 100 harfte 4 hata, CTC 1B'de 9.
3. **Dil etiketi alıyor (kmr_Latn):** Kürtçe konuşulduğunu bilerek yazıyor. Türkçe ya da Soranî karışması azalır.
4. **Lisansı açık:** Omnilingual'ın kodu ve modelleri Apache 2.0 (projenin README'si). Temel model kuralına uyuyor.
5. **Eğitebileceğimiz en büyük model:** 3B ve 7B'nin eğitimi bizim kartlarımıza hiç sığmaz.

**Yanında yardımcı kulak: Omnilingual CTC.** Önce K3'te eğitilen 300M; gerekirse 1B. Üç işi var:
- **Zaman:** Her kelimenin hangi saniyede söylendiğini verir. LLM bunu vermez. Vurgu ve ezgi ölçümü, düzeltme sayfası ve ses verisi bu zamanlara dayanır.
- **Hızlı tarama:** Dengê Amerîka'nın ~289 saatini LLM 1B ile yazmak T4'te tahminen ~90 kart saati tutar, CTC ile birkaç saat. Bu yüzden düzen şöyle olur:
  - CTC her şeyin taslağını çıkarır.
  - LLM 1B, CTC'nin emin olmadığı parçaları yeniden yazar.
  - Botan sohbet kayıtları ve sınav setleri ise baştan LLM 1B ile yazılır: düzeltecek yer yarı yarıya azalır.
- **Yedek:** LLM 1B'nin eğitimi tıkanırsa ya da Botan sohbetinde kötü çıkarsa temel CTC'ye döner.

**LLM 3B (ölçüldü):** LLM 1B'den yalnızca biraz iyi: FLEURS'ta 100 kelimede yarım kelime, 100 harfte çeyrek harf. İki kat büyük olduğu halde fark bu kadar. Demek ki bizi model boyu değil, Kürtçe veri ve eğitim sınırlıyor. 3B'yi "öğretmen" olarak kullanmaya da gerek yok. Hızları da neredeyse aynı (52 ve 49 dakika), çünkü yazma süresini iki modelde de aynı boydaki dil kısmı belirliyor.

## Bu seçimi bozacak ölçümler

1. **Botan sohbet seti:** LLM 1B, eğitilmiş CTC'den kötü yazarsa.
2. **Uydurma ve "düzeltme":** Dil modelli kulaklar gürültüde cümle uydurabilir ya da Botan ağzındaki bir sözü standart biçime çevirebilir. Bizim yazıya geçirme kuralımız ise "söylendiği gibi" (kayıt hattı kararı 2). Bunu doğal kayıtta ayrıca sayacağım: kaç kelime söylenenden farklı, standart biçime çevrilmiş?
3. **Eğitimin sığması:** LLM 1B'nin eğitimi hiçbir yolla sığmaz ya da çok pahalı olursa.

## Bu seçimin getirdiği iş: eğitim nerede, nasıl? (Kritik nokta 4)

LLM 1B'nin tam eğitimi yaklaşık 36 GB bellek ister; bir T4'te 16 GB var. Üç yol var:

| Yol | Nasıl | Artısı | Eksisi |
|---|---|---|---|
| A. Kaggle, iki T4 | Modelin yazı kısmı (dil modeli) dondurulur, ses kısmı iki karta paylaştırılarak eğitilir | Ücretsiz | Bellek sınırda, yavaş; önce sığma denemesi gerek |
| B. Kaggle, hafif eğitim (LoRA) | Modelin yalnızca küçük ek katmanları eğitilir | Ücretsiz, tek karta sığar | Tarif kodunu biraz değiştirmek gerekir; kazanç tam eğitimden az olabilir |
| C. Kiralık A100 (80 GB) | Tam eğitim | En iyi ve en hızlı yol | Saatlik ücret var; hesap ve harcama proje sahibinin onayıyla |

**Sıra:**
1. K2 bitince iki kartı sınarım.
2. Kısa bir sığma denemesi yaparım: birkaç adım, eğitim değil.
3. Sonucu ve önerimi "Kritik nokta 4" diye proje sahibine yazarım.
4. Asıl eğitim o zaman başlar.

K3'te CTC 300M'in eğitimi sürüyor ve durdurulmayacak. Hem yardımcı kulak olacak hem de eğitimin kulağa ne kadar kazandırdığını gösterecek.

## Değişen işler

- **`kulak/taslak.py`:** Yazıyı LLM 1B'den alacak, kelime zamanlarını CTC ile hizalayacak.
- **Dengê Amerîka taslakları:** Önce CTC, sonra emin olunmayan yerlerde LLM 1B.
- **Sonraki ölçümler:** CTC 3B küçük toplulukla yeniden ölçülür (yalnızca kıyas için; LLM 3B ölçüldü).
- **Hız:** LLM 1B'nin topluluğu büyütülerek hızı yeniden ölçülür.
