# Küçük Türkçe sesler, benzerleri ve Farsça modeller: bize dersler (16–17.11.2026)

**Tek cümleyle:** iki küçük Türkçe ses de **VoxCPM2'nin öğrencisi**; yani bizim Kürtçe sesimizin (S28–S34) üstüne
kurulduğu aynı büyük modelden çıkmışlar. Durak 7'nin ("küçük ve hızlı ses") yolu komşu dilde iki ayrı ekipçe yürünmüş ve
ayrıntısıyla yazılmış. Bugün bizi durduran küçük modelin tarifi değil, **öğretmenimizin hâlâ yeterince iyi olmaması.**

## Kaynaklar (bu oturumda okunanlar)

| Ne | Nerede | Not |
|---|---|---|
| EMA Lightning (8,6M parametre, 34 MB, kadın ses) | [model sayfası](https://huggingface.co/canberkkkkkk/ema-lightning), [kod](https://github.com/canberk7/ema-lightning) | Apache 2.0. Yalnız çalıştırma kodu; eğitim tarifi sayfada birkaç cümle. |
| Antalia-2 Mini (7,62M, 30,5 MB, erkek ses) | [teknik rapor](https://arxiv.org/abs/2611.13811), [model sayfası](https://huggingface.co/cloud0day3/antalia-mini) | Apache 2.0. **Düzeltme (17.11, paket açılıp okundu):** eğitim hesabının kendisi pakette açık; aşağıda "Kod denetimi". Kapalı olan eğitim döngüsü, üretim betikleri ve veri. |
| Alania-2 (488M, ses kopyalama; ağırlık kapalı) | [rapor](https://arxiv.org/abs/2611.13845) | Aynı ekibin büyük modeli. Veri hattı ve normalleştirici dersleri burada. |
| Açık yapay Türkçe ses verisi | [alania-synthetic-speech-tr](https://huggingface.co/datasets/cloud0day3/alania-synthetic-speech-tr) | 1,66M satır, 2.750 tasarlanmış ses, CC BY. Satır başına kalite alanları. |
| Türkçe sınav tablosu (15 sistem) | [benchmark](https://speech.patientdesk.ai/en/benchmarks) | Freya-TR-Eval, 495 cümle. |
| Video (iki modelin kıyası) | altyazısı okundu | 495 cümle + 43 cümlelik "şantiye sınavı". |
| VoxCPM2'ye LoRA, Kmerce ve Korece | [arXiv 2606.26618](https://arxiv.org/abs/2606.26618) | Bizimle aynı yöntem, başka az kaynaklı dil. |
| ManaTTS (Farsça, 86 sa tek ses, CC0) | [arXiv 2409.07259](https://arxiv.org/abs/2409.07259) | Uzun kaydı metne hizalama hattı açık (MIT). |
| ParsVoice (Farsça, 2.200 sa, 1.815 konuşmacı) | [arXiv 2510.10774](https://arxiv.org/abs/2510.10774) | Metinsiz sesli kitaptan külliyat. |
| Farsça Piper + bağlama bakan ön yüz | [arXiv 2512.08006](https://arxiv.org/abs/2512.08006) | Ezafe ve eş yazılılar. |

Okunmadan, bilgiden yazılanlar ayrıca işaretlendi ("okunmadı").

## İki küçük model yan yana

| | EMA Lightning | Antalia-2 Mini |
|---|---|---|
| Öğretmen | VoxCPM2, yazıyla tarif edilmiş ses (gerçek kişi yok) | VoxCPM2, 9 adaydan seçilmiş tek yapay örnek ses |
| Eğitim sesi | ~1.000 sa, tek ses | ~1.790 sa (1.582 uzun + 207 kısa), 1,36M kesit, %97,4'ü süzgeçten geçti |
| Giriş | harf (fonem yok), önce yazıdan söze çevirici | 47 simge: harf + noktalama (fonem yok, rakam yok) |
| Gövde | ConvNeXt + dikkat metin kodlayıcı, süre kestirici, 6 DiT bloğu, HiFi-GAN türü çözücü | 3 ConvNeXt + 1 dikkat, süre kestirici (MAS'tan öğrenir), 5 DiT bloğu, Vocos türü çözücü |
| Hızlandırma | DMD2 damıtma: 32 geçiş → 4 adım | kısayol tutarlılığı: 8 adım (4 adım belirgin kötü: 1,17'ye karşı 0,97) |
| Harcanan | yazılmamış | üretim 8 kartta 23 sa; eğitim 159 kart-saat (yayımlanan soy 114,5) |
| Sınav (aynı hakem) | kelime hatası %1,04 | %1,09 (fark ölçüm payının içinde) |
| Öğretmenin kendisi | | %0,92 |

Videonun kendi ölçümü: 3.911 kelimede EMA 13, Antalia 25 hata (düz metin); rakamlı ve birimli 43 cümlede Antalia 66,
EMA 38 puan (106 üzerinden). Yani düz metinde EMA, **yazıdan söze çeviride Antalia** iyi; ikisi de birimlerde düşüyor
(`m³/h`, `±`, `kW`).

## Dersler, bizim işimize göre sıralı

### A. Bugün uygulananlar (öğretmen aşamasındayız)

**1. Öğrenci öğretmenin kusurunu aynen alır; kusur satır ölçüsünden kaçar.**
Antalia'nın öğretmeni cümle başındaki `ö`'yü %26 doğru okuyordu (öbür harflerde %94). Bozuk satırların **%82'si** "satırın
tümünde harf hatası ≤ %10" süzgecinden geçti, öğrenci kusuru öğrendi (12 ilk sözcüğün 5'i doğru). Çözümleri yama: cümlenin
başına gizli "ee, " söyletip kesmek. Kendileri "veride düzeltilmedi" diyor.
- **Bizde ölçüldü (bugün, `olcumler/metin-yolu/bas_harf.py`):** ilk sözcüğü yanlış duyulan kesitlerin **%60–63'ü** aynı
  %10'luk satır süzgecinden geçiyor (S28, S34, kol a, kol b; dördünde de aynı oran). İlk sözcük yanlışı: S28 %27,2 · S34
  %12,2 · kol a %7,5 · kol b %5,1. Zayıf açılış harfleri dört seste de aynı: **`î` (9 kesitin 5–6'sı) ve `q` (3–5'i)**; ama
  her biri yalnız 3 cümle × 3 okuma, yani bu bir işaret, ölçüm değil. Sayılar kulağın kendi hatasını da içerir (üst sınır).
- **Kural (Durak 7 ön koşulu):** yapay külliyat süzgecinde satır ölçüsünün yanına **ilk sözcük kapısı** konur; açılış
  harfi başına en az 30 cümlelik bir baş sınavı yazılır; öğretmen o sınavı geçmeden damıtma başlamaz.

**2. Yazıdan söze çevirici kaliteyi modelden çok belirliyor.**
Alania-2'de aynı model ham metinle %66,7, çeviriciyle %6,4 kelime hatası veriyor. Anadili denetimi 134 okunuşun 16'sını
değiştirdi. Videoda en büyük puan farkı da buradan (telefon numarası, `DN50`, parantez).
- **Bizde denendi:** `metin/hazirla.py` sayı, tarih, saat, yüzde ve ekleri okuyor. 21 zor örnekte eksikler: birimler
  (`m³/h`, `kW`, `mm`, `kg`, `°C`, `km/h` olduğu gibi kalıyor), `±` ve eksi işareti, aralık (`12-15`), kesir (`1/2`), para
  simgesi (`$`, `TL`), harf harf okunan kısaltmalar (`TRT`), kod (`DN50`, `5G` → "pêncG"), sıra noktası (`3.`), telefon
  numarası (öbek öbek yüzlü okunuyor, parantez kalıyor), adres. `ji %15` → "ji ji sedî panzdeh".
- **Yapılmadı, nedeni:** Kürtçe karşılıklar (birim adları, "pile" mi "derece" mi) editör onayı ister; `hazirla.py`
  eğitim metnini de ürettiği için değişiklik metin biçimine dokunur (Kural 1). Sıradaki iş olarak yazıldı.

**3. Süzgeç eşikleri ve hizalama yöntemleri (veri hattına).**
- Yapay ya da gerçek kesit için ortak kapılar: harf hatası ≤ %5–10, **7–25 harf/sn konuşma hızı**, konuşmacı benzerliği
  ≥ 0,45, perde bandı, UTMOS ≥ 2,5–2,8, DNSMOS ≥ 2,4, müzik ayıklama. Alania gerçek seste 9.216 sa'ten 1.772 sa tuttu.
- ManaTTS: uzun kayıt + bilinen metin için beş kulak birden; en uzun yazının %80'inden kısa olan atılır; metinde aralık
  araması, tutmazsa atlamalı arama; harf hatası ≤ 0,05 "yüksek", ≤ 0,2 "orta". 66.172 kesitin %98'i kabul.
- ParsVoice: kesit sınırını **yazı aynı kaldıkça kırp**; yarım cümleyi sınıflayıcıyla bul ve uzat. Veri ölçeği etkisi:
  120 sa → kelime hatası 42,9 · 530 sa → 20,1 · 2.200 sa → 17,8.
- Gürültü: konuşmanın 12 dB altındaki arka ses modele sözcüklerin %29–49'unu atlatıyor.

**4. Ölçüm dürüstlüğü.**
Tek okumanın oynaması ±0,13 puan; 31 karşılaştırmanın 17'si tek okumaya dayanıyor ve çoğu oynamanın içinde. Ayar aynı
sınav cümlelerinde yapılınca sonuç iyimser çıkıyor. Süzen kulakla puanlayan kulak aynıysa hata görünmez. Çıkış filtresi
kulakla seçildi ve otomatik puanı düşürdü. Kmerce çalışmasında kayıp eğrisi rank 128'i, **dinleyiciler rank 64'ü** seçti.
- **Bizde:** üç okuma ve kör dinleme zaten kural. Ek: ezgi setinde çok karar verdik; S35 ön kaydında **hiç bakılmamış
  saklı bir cümle seti** ayrılır.

**5. Öğretmenin uyarlama ayarı.**
Kmerce (3,3 sa veri): rank 64, MOS 3,85 → 4,23; rank 8 anlamlı değil. Zaten iyi olan Korecede uyarlama kötüleştirdi.
Ayarları: α = 2 × rank, hedef yalnız dikkat katmanları (dil modeli + DiT), 10.000 adım, hız 1e-4.
- **Bizde:** S34 rank 32, α = 32, dil modeli + DiT, hız 1e-4. **Rank 64 ve α = 2r S35'te bir kol adayı** (ön kayıtla).

**6. Baş ve ikiz ses yamaları (okuma tarafı, eğitim gerekmez).**
Gizli ön ek + kesme; aynı iki sesin ikincisini 1,3 kat uzatmak ("o olumsuz" tek ses duyuluyordu).
- **Bizde:** sorularda başa hece ekleniyor (64 sorunun 13'ü); Kürtçede ikiz ses `rr` ve sözcük sınırında (`min nan`).
  Bir sonraki okuma sınavına iki ölçüm eklenir: gizli ön ekli okuma ve ikiz seslerin duyulma oranı.

**7. Büyük modelden (Alania-2) notlar.**
1,24 milyarlık model sıfırdan 54 bin adımda metni sese hizalayamadı, 488 milyonluk hizaladı. Eğitim sesinin %90'ı yapay.
Ses kopyalamada "devam ettirme" kipi sözcüklerin %21,9'unu atladı, "yalnız örnek" kipi %1,7. Üslup talimatı sesli
okundu; kısa İngilizce etikete çevrilince düzeldi. Parçaları birbirine bağlayarak okutmak benzerliği düşürdü, bırakıldı.

### B. Durak 7'de (küçük ses) uygulanacaklar

**8. Tarif belli:** tek ses, 1.000–1.800 saat yapay okuma, 7–9 milyon parametre, **harf girişi** (bizim harf yolu v3 ile
aynı fikir), süre kestirici, küçük akış eşleme gövdesi, hafif çözücü. Adım azaltmada 4 adım için damıtma (DMD2) gerekir;
kısayol yöntemiyle 8 adımda kalınır.

**9. Maliyet yol haritasında iyimser yazılmış.** Antalia: üretim 8 büyük kartta 23 saat, eğitim 159 kart-saat. Kiralık
fiyatla kabaca birkaç yüz dolar (tahmin; fiyat bakılmadı); yol haritası 30–60 $ diyordu. Ücretsiz Kaggle kartıyla eğitim
haftalar sürer. **Düzeltme (17.11):** Antalia'nın paketinde eğitim hesabı açık (aşağıda "Kod denetimi"); eksik olan birkaç yüz satırlık eğitim
döngüsü ve hizalama işlevi. EMA'da yalnız çalıştırma kodu var. Durak 7 Antalia'nın açık koduyla başlayabilir.

**10. Çözücü üretilmiş sesle ince ayarlanmalı.** Gerçek mel ile eğitilen çözücü üretilen mel'de bozuldu; üretilen mel ile
ince ayar kelime hatasını %3,89'dan %1,75'e indirdi.

**11. Sessiz hata örneği.** Bir önbellek ayarı ilk 6.000 adımda gövdeye hiç gradyan vermedi; başka bir ayar belirtiyi
gizlemişti. Bizim "önce kayıp eğrisine bak" kuralının aynısı; küçük model eğitiminde ilk adımlarda gradyan büyüklüğü
günlüğe yazılır.

**12. İşe yaramayanlar (denemeyelim):** kısa kesitle ek ince ayar, kusurlu satırları atıp yeniden ince ayar, 16 adım,
her sözcük arasını uzatmak, sıcaklık oynamaları.

**13. Yapay ses, gerçek kişi yok.** İki ekip de rıza sorununu böyle aşmış; Antalia "benzerlik denetlenmedi" diye not
düşüyor. Durak 4 ("kendi seslerimiz") için ikinci bir seçenek: yazıyla tarif edilmiş ses + bizim Kürtçe uyarlama.

### C. Farsça modeller

Tek bir karşılaştırmalı sıralama bulunamadı; her çalışma kendi dinleyicileriyle ölçmüş.

| Model | Temel | Veri | Sonuç (kendi ölçümü) | Lisans |
|---|---|---|---|---|
| ManaTTS Tacotron2 | Tacotron2 + HiFi-GAN | 86 sa tek ses | MOS 3,76 (doğal ses 4,01) | CC0 veri, MIT kod |
| XTTSv2 + ParsVoice | XTTSv2, 2.500 Farsça belirteç eklendi | 2.200 sa | MOS 3,60; konuşmacı benzerliği %80 | ticari değil |
| Piper + bağlamlı ön yüz | Piper (VITS, 15–20M) | ManaTTS | MOS 2,41 → **3,14 yalnız ön yüzle**; ezafe 19,6 → 90,1; eş yazılı %43,9 → %77,7 | açık |
| Matcha-TTS (Khadijah), GlowTTS (Kamtera) | | | MOS 2,54 ve 1,30 | açık |
| Chatterbox Persian, MOSS-TTS LoRA, Pocket TTS Farsi v2, MMS-TTS | | | sayfalarında puan yok (okunmadı) | çoğu ticari değil |

**Farsçanın dersi:** asıl dert yazıda olmayan sesler (ezafe, kısa ünlüler, eş yazılılar). Modeli değiştirmeden yalnız ön
yüzü düzeltmek MOS'u 0,7 puan artırmış. Kurmancî Latin yazısı bunların çoğunu yazıyor; bizdeki karşılığı **soluklu ve
soluksuz sesler, titrek `r`, vurgu.** Çözüm sınıfı aynı (bağlama bakan hafif ön yüz, sözlük) ve 16.11 dersimizle
uyuşuyor: işaret eğitim sesiyle örtüşmüyorsa öğrenilmez. Soranî (Arap harfli) açıldığında Farsça ön yüz çalışmaları
doğrudan örnek.

### D. Benzer küçük modeller (Türkçe sınav tablosundan)

Piper (16M) kelime hatası %3,41 · MMS-TTS (36M) %6,38 · Coqui GlowTTS (28M) %10,93 · XTTS-v2 (470M) %3,67. Yani aynı
boyuttaki eski tarifler 3–10 kat daha çok hata yapıyor; farkı yaratan mimari değil, **çok iyi bir öğretmenden gelen çok
temiz ve çok fazla tek ses.**

## Kod denetimi (17.11.2026; iki paket indirilip okundu, çalıştırılmadı)

16.11'de "eğitim kodu iki modelde de kapalı" yazmıştım; bunu ekiplerin kendi cümlesinden almıştım, paketi açmamıştım.
Paketler açılınca tablo değişti:

| | EMA Lightning ([depo](https://github.com/canberk7/ema-lightning), `68f54a1`) | Antalia-2 Mini (paket 1.0.1) |
|---|---|---|
| Boyut | ~1.100 satır | ~3.100 satır |
| Model yapısı | açık, `model.py` 247 satır: harf kodlayıcı, süre kestirici, pencereli Gauss hizalayıcı, 6 DiT bloğu | açık, `model.py` 268 satır |
| **Eğitim hesabı (kayıplar)** | **yok**; yalnız çalıştırma | **var**: `AcousticModel.forward` hizalamayı (MAS), ön kestirim, süre, akış eşleme ve kısayol kayıplarını hesaplıyor |
| Çözücü eğitimi | yok | ayırt ediciler ve GAN kayıpları `vocoder.py` içinde |
| Eksik olan | damıtma (DMD2), süre eğitimi, veri üretimi | `mas.py` (Glow-TTS ve Matcha-TTS'te açık olan hizalama işlevi), eğitim döngüsü, veri üretim betikleri, veri |
| Yazıdan söze çevirici | ayrı açık paket (normalizer-tr) | pakette, 776 satır: telefon, aralık, para, birim, kısaltma, adres, ek uyumu |
| Lisans | Apache 2.0 | Apache 2.0 |

**Sonuç:** Antalia'nın açık koduna bir hizalama işlevi ve birkaç yüz satırlık eğitim döngüsü eklenirse küçük Kürtçe ses
aynı kodla eğitilebilir; simge tablosu 47 simgeden bizim harf yolumuza çevrilir. Çeviricisinin yapısı `hazirla.py`
eksikleri için hazır bir örnek (Türkçe kuralları değil, bölümleri).

## Bizim sıra (bu belgeden çıkan işler)

1. Baş sınavı: açılış harfi başına ≥ 30 cümle; öğretmenin baş kusurlarını say (`bas_harf.py` hazır).
2. `hazirla.py` eksikleri: birim, işaret, aralık, kesir, kısaltma, telefon; karşılıklar editör onayıyla (INCELE).
3. S35 ön kaydına: saklı cümle seti; rank 64 ve α = 2r kolu; gizli ön ek ve ikiz ses ölçümü.
4. Veri hattına: konuşma hızı kapısı, çok kulaklı hizalama, yazı sabitken sınır kırpma (`MODEL-ISTEKLERI.md`).
5. Durak 7: ön koşul (öğretmen baş sınavını geçer, harf hatası Türkçe öğretmene yaklaşır), maliyet düzeltmesi, tarif
   seçimi (kritik nokta 9).
