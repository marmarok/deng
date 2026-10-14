# Durak 0: ilk ölçümler

*13 Ekim 2026*

## 1. Kaggle'ın ücretsiz kartı yetiyor mu?

Kart: Tesla T4, 15,6 GB.

| Ölçüm | Sonuç |
|---|---|
| Hazır modelle ses üretmek | 5,7 GB bellek. Gerçek zamandan 2,2 kat yavaş |
| Hafif eğitim (LoRA), ilk deneme | Bellek taştı |
| Hafif eğitim, düzeltmeden sonra | 8,3 GB bellek, adım başına 1,2 saniye |

- **Taşmanın sebebi:** Eğitim betiği modelin donmuş kısmını gereğinden iki kat büyük tutuyordu.
- **Hesap:** 95 saatlik açık Kürtçe verinin bir turu yaklaşık 16 GPU saati sürüyor. Kaggle'ın haftalık ücretsiz süresiyle bu, haftada yaklaşık iki tur demek.
- **Sonuç:** Hafif eğitim parasız yapılabiliyor.

## 2. Çıta: mevcut modeller ezgi setini nasıl okuyor?

Ezgi setindeki 60 cümle üç modele okutuldu. Her okuma Kürtçe Whisper'la yeniden yazıya çevrildi; aşağıdaki "harf hatası" bu yazıyı asıl metinle karşılaştırıyor.

| Model | Harf hatası | Not |
|---|---|---|
| VoxCPM2, eğitimsiz | %20 | Kürtçeyi bilmiyor; yabancı aksanla okuyor |
| **Anadil** (VoxCPM2 üzerine Kürtçe LoRA, MIT) | **%3,7** | Çok net. Hataların neredeyse hepsi sayılarda: "1986", "250", "7:30" yanlış okunuyor |
| MMS (Meta, ticari kullanıma kapalı, yalnızca kıyas için) | %7,2 | |
| *Gerçek insan kaydı (FLEURS), yazıya çeviricinin kendi hatası* | *%13,9* | *Uzun ve zor cümleler. Yazıya çevirici de yanılıyor; bu sayılar yalnızca kendi aralarında kıyaslanmalı* |

### Ezgi: asıl açık burada

Kelimeleri aynı olan düz ve soru cümlesi çiftlerinde (ezgi setinde 1–8) cümle sonundaki ses perdesi ölçüldü. Kürtçede bu tür sorularda soru olduğunu yalnızca ezgi gösterir; sonda sesin yükselmesi beklenir.

| Cümle | Anadil | VoxCPM2 | MMS |
|---|---|---|---|
| 2 Tu hatî? | ölçülemedi | **+4,8** ↑ | −4,1 |
| 4 Ew birçî ye? | −5,1 | 0 | −10,5 |
| 6 Çavên we vekirî ne? | −5,8 | **+3,3** ↑ | −0,9 |
| 8 Tu serpêhatiya fîl û şêr dizanî? | +0,4 | +0,6 | −7,3 |

Sayılar son hecedeki perde değişimini yarım ton olarak gösteriyor; artı yükseliş, eksi iniş demek.

- **Anadil:** Kelimeleri çok iyi söylüyor, ama ezgisiz sorularda sesi yükseltmiyor. Kürt bir dinleyici bunları büyük olasılıkla düz cümle gibi duyar.
- **VoxCPM2:** Eğitimsizken soruda sesi biraz yükseltiyor. Bunu büyük ihtimalle Türkçe ve İngilizce bilgisinden getiriyor. Anadil'in eğitimi bu yeteneği silmiş görünüyor.
- **Kaba bir ölçü:** Bu ölçüm otomatik ve kaba. Son karar kulakla verilir; ana dili konuşan biri dinleyip doğrulamalı.

## Bundan çıkanlar

1. **Doğru telaffuz zor kısım değil.** Anadil bunu tek konuşmacılı veriyle büyük ölçüde başarmış. Doğal Kürtçe ile makine sesi arasındaki fark büyük ihtimalle ezgide.
2. **Sayılar:** Metin hazırlayıcı (sayıları Kürtçe yazıya çeviren kural seti) şart. Durak 3'teki plan doğru.
3. **Soru ezgisi:** Eğitim verisinde soru ezgisi bol ve doğru olmalı. Ezgi seti ve tercih eğitimi tam bu açığı kapatmak için.
4. **Lisans:** Anadil MIT lisanslı, başlangıç noktası olarak kullanılabilir. Ama verisinin nereden geldiği bilinmiyor; kendi modelimizin temeline koymadan önce sorulmalı.

Dosyalar: `kaggle/durak0-*/cikti/`. Her modelin 60 sesi ve tek tek okunuşlar `ayrinti.json` dosyasında.

## 3. Açık veri hangi yöreden? (13.10)

**Common Voice 27.0 Kürtçe (CC0):** 77,5 saat onaylı kayıt, 540 konuşmacı.
- Konuşmacıların 515'i yöresini yazmamış; bu, kayıtların %95'i demek.
- Yöre yazılan kayıtlar toplam yaklaşık 3,5 saat:
  - Mardin, Diyarbakır, Batman: 1,7 saat. Bunların hepsi tek bir kişinin kaydı.
  - Kalan yerler 0,1–0,5 saatlik parçalar: Mardin, Serhat, Kars, Torî/Botî, Afrin, Badinan ve "standart" diyenler.
- Kayıtların %30'unu üç erkek okumuş: 8,5, 7,6 ve 7 saat.
- Cinsiyete göre: erkek 54,7 saat, kadın 11,2 saat, belirtilmemiş 11,6 saat.

**FLEURS-Kobani:** Kobanê Üniversitesi'nde kaydedildi. Konuşmacıların yöresi yazmıyor.

**Yöreyi bulmanın yolu:** En çok kaydı olan yaklaşık 20 konuşmacı verinin büyük kısmını taşıyor. Her birinden 30 saniyelik birer örnek dinletip yöresini kulakla etiketlemek mümkün. Bunu ancak ana dili Kürtçe olan biri yapabilir: dil editörleri.

## 4. Deneme 1: VoxCPM2'ye FLEURS ile hafif eğitim (13 Ekim)

**Ne yapıldı:**
- Kaggle'ın ücretsiz T4 kartında LoRA eğitimi yapıldı.
- Veri FLEURS-Kobani'den alındı: 2.822 parça, 8,2 saat.
- Eğitim 2 tur, 1.411 adım sürdü; yaklaşık 2 saat 20 dakika.
- Metinler eğitimden önce `metin/hazirla.py` ile hazırlandı.

**Harf hatası:**

| Model | Bütün set | Sayısız cümleler |
|---|---|---|
| VoxCPM2, eğitimsiz | %20,3 | |
| **Deneme 1** | **%9,2** | **%5,0** |
| Anadil | %3,7 | |
| MMS | %7,2 | |

- Sekiz saatlik okuma verisiyle iki tur, hatayı yarıdan fazla düşürdü.
- Anadil hâlâ daha iyi. Onun ne kadar veriyle eğitildiği bilinmiyor.
- **Sayılar artık doğru okunuyor.** Anadil'in yanlış okuduğu "1986", "7:30" ve "1.250", metin hazırlayıcı sayesinde kelimeyle doğru söyleniyor; örneğin "hezar û neh sed û heştê û şeşan". Yine de bütün setteki %9,2'nin yüksek çıkmasının sebebi ölçüm: çıkan ses rakamlı asıl metinle karşılaştırılıyor. Sonraki ölçümde hazırlanmış metinle karşılaştırılacak. Gerçek hata %5'e yakın.

**Ezgi:**

| | Soruda yükselen | Düz cümlede inen |
|---|---|---|
| VoxCPM2, eğitimsiz | %33 | %61 |
| Anadil | %23 | %91 |
| MMS | %13 | %85 |
| **Deneme 1** | **%27** | **%97** |

- Düz cümlenin sonunda ses neredeyse her zaman iniyor. Bu iyi.
- Sorularda ses yine çoğunlukla yükselmiyor.
- Soru sözcüklü sorularda ("kengî", "çawa") inmek Kürtçede de doğal olabilir. Asıl önemli olan evet/hayır soruları.
- Evet/hayır sorularının yarısı (6'da 3) yükseliyor: 2 (+5,0), 4 (+1,5) ve 15 (+5,3). Anadil'de bu sayı 3'te 1'di.

**Bundan çıkanlar:**
- Okuma verisi telaffuzu hızla öğretiyor. Kalan doğallık açığını kapatmak için asıl veri doğal konuşma olmalı.
- Soru ezgisi okuma verisinden gelmiyor: FLEURS'te soru cümlesi neredeyse yok. Bu, 13 Ekim'deki "doğal konuşma" kararını destekliyor.
- **Sonraki deneme:** Common Voice'un altın sınıfı eklenecek. Her soru cümlesi için ayrı bir sayaç tutulacak.
- **Kulakla dinlenmeli:** Bu ölçüm otomatik ve kaba; son kararı kulak verir.
