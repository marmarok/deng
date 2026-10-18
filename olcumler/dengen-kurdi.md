# Kürtçenin sesleri: alfabenin göstermedikleri

*18 Ekim 2026. Proje yürütücüsünün sorusu üzerine: "Kürtçede ses sayısı harf sayısından fazla. Model bu sesleri nasıl öğreniyor?" Kaynaklar Kürt dilbilimcilerin çalışmaları; kaynak listesi en altta.*

## Kısa sonuç

- **Alfabe:** Hawar alfabesinde 31 harf var: 8 ünlü, 23 ünsüz.
- **Bedirxan:** 31 temel ses olduğunu, bu yüzden 31 harf olduğunu söyler.
- **Samî Tan (Gazete Duvar):**
  - Alfabe tam fonetik değil, ve bu bir sorun da değil.
  - Ama sözlüklerde, öğretimde ve harf çevirisinde bütün seslerin gösterildiği bir fonetik yazım gerekir.
  - Arapçadan gelen bazı sesler de doğru söyleyiş için gösterilmeli.
- **Barzo Omar Mahmoud (Mardin Artuklu, 2016, yüksek lisans tezi):**
  - Bütün ağızlarla birlikte 46 ses sayıyor; bunlardan 34'ünü ayrı ses birimi (fonem) sayıyor.
  - Önerdiği yeni fonemler: soluksuz /k/ (soluklu /k/'nin karşısında) ve titrek /r/ (çarpmalı /r/'nin karşısında).
  - Durak ünsüzlerinde üçlü ayrım görüyor: ötümlü, soluklu, soluksuz.

## Alfabenin göstermediği sesler

| Ses | Simge (IPA) | Bugün nasıl yazılıyor | Örnek | Ne kadar önemli |
|---|---|---|---|---|
| Soluklu ve soluksuz p | pʰ / p | ikisi de **p** | — | Anlam ayırır |
| Soluklu ve soluksuz t | tʰ / t | ikisi de **t** | — | Anlam ayırır |
| Soluklu ve soluksuz k | kʰ / k | ikisi de **k** | — | Anlam ayırır |
| Soluklu ve soluksuz ç | t͡ʃʰ / t͡ʃ | ikisi de **ç** | — | Anlam ayırır |
| Çarpmalı ve titrek r | ɾ / r | **r**; titrek bazen **rr** | *ker* / *kerr* | Birkaç sözcükte anlam ayırır |
| Düz ve kalın l | l / ɫ | ikisi de **l** | — | Birkaç sözcükte; kaynaklar tartışıyor |
| Gırtlaktan h (ayn'lı h) | ħ | **h**; bazı yazarlar **ḧ** | *heft / ḧeft* | Ağza göre değişir |
| Ayn | ʕ | **'** ya da hiç yazılmaz | *'erd*, *'ewr* | Arapça kökenli sözcüklerde |
| Ğ benzeri x | ɣ | **x**; bazı yazarlar **ẍ** | *ẍerîb* | Samî Tan'a göre ayrı fonem değil |
| Genizden n | ŋ | **n** (k/g önünde) | *deng*, *reng* | Kendiliğinden; harf gerekmez |
| Yuvarlak x | xʷ | **xw** (iki harf) | *xwe*, *xwarin* | Yazıda var |
| Kısa i'nin kalın türü | ɨ | **i** | *dims* | Kendiliğinden |
| Vurgu ve ezgi | — | hiç yazılmaz | *Tu hatî.* / *Tu hatî?* | Anlam taşır |

**Notlar:**
- **Soluklu ve soluksuz örnekleri:** Bunları uydurmamak için boş bıraktım. Dil editörü verecek, ya da aşağıdaki yöntemle ölçülecek.
- **Soluksuz seslerin niteliği:** Kaynaklar soluksuz p, t, k ve ç'nin hafif boğazdan (yutaksı) çıktığını da söylüyor.
- **Sovyet dönemi Kürtçe yazılar:** Kiril ve 1929 Latin alfabeleri soluksuz sesleri ayrı imle gösteriyordu. Kurdoyev'in sözlüğü bunun örneği. Bu bilgi kaynakla doğrulanacak; doğrulanırsa böyle bir sözlük okunuş listesinin hazır kaynağı olabilir.

## Model bu sesleri nasıl öğreniyor?

- **Kulak (yazıya geçirme):**
  - Kulak yazı üretir. Yazıda pʰ ile p ikisi de "p" olduğu için kulağın bu ayrımı yazması gerekmez; sesi duyup doğru sözcüğü yazması yeter.
  - Bu yüzden kulak için sorun değil. Kulağın sözlüğünde bütün Kürtçe harfler var; bunu ölçtük, eksik harf yok.
  - Tek küçük kayıp: etiketlerden kesme işaretini (') atıyoruz, bu yüzden *'erd* gibi yazımlardaki ayn imi gidiyor.
- **Ses (seslendirme):**
  - Ses modeli yazıyı alıp konuşur. "kal" yazısında k'nin soluklu mu soluksuz mu olduğunu yazıdan bilemez.
  - Bunu kayıtlardan öğrenir: aynı sözcüğü yüzlerce kez duyunca o sözcüğün söylenişini ezberler.
  - Zayıf yerleri:
    - az geçen sözcükler;
    - aynı yazılıp farklı söylenen sözcükler. Bunlarda anlamı cümleden çıkarmak zorunda.

## Önerim: okunuş katmanı

- **Fikir:** Yazının yanına modelin göreceği gizli bir okunuş işareti eklemek (örneğin k ile kʰ ayrı). İnsanlar yine normal yazar; işareti metin hazırlayıcı ekler.
- **Okunuş listesi kayıtlardan kendiliğinden çıkarılabilir:**
  - Soluklu seste dudak ya da dil açıldıktan sonra ses tellerinin titremesi gecikir (VOT, ses başlama gecikmesi). Bu gecikme ölçülebilir.
  - Hizalayıcımız her sözcüğün kayıttaki yerini zaten buluyor.
  - Yüzlerce saatte her sözcüğün p, t, k ve ç'si ölçülür, sözcük sözcük "soluklu mu, soluksuz mu" listesi çıkar.
  - Dil editörü bu listeyi denetler.
- **Durum:** Bu fikir henüz ölçülmedi.
  - Önce küçük bir deneme: 50 sözcükte otomatik ölçüm ile editörün kulağı karşılaştırılacak.
  - Sonra seslendirmede işaretli ve işaretsiz iki model kıyaslanacak.

## Tokenizasyon: yazıyı parçalara bölme

- **Biz bölmüyoruz:** Her model kendi bölücüsüyle (tokenizer) gelir; biz onu değiştirmeden kullanıyoruz. Bizim yaptığımız, yazıyı modele vermeden önce hazırlamak:
  - sayıları yazıya çevirmek;
  - şapkaları (ê, î, û) düzeltmek;
  - harfleri tek biçime getirmek;
  - kulak için küçük harf ve noktalamasız yazmak.
- **Kulak (Omnilingual):** Bölücüsünde bütün Kürtçe harfler var; eksik harf sayısı 0 olarak ölçüldü. Yazıyı küçük parçalarla üretiyor.
- **Ses (VoxCPM2), 18.10'da ölçüldü:**

  | Dil | Sözcük başına parça |
  |---|---|
  | İngilizce | 1,35 |
  | Kürtçe | 2,83 |
  | Türkçe | 4,18 |

  - Kürtçe sözcükler büyük ölçüde harf harf bölünüyor; ê, î, û, ç, ş her biri ayrı parça.
  - Örnek: *Ez ê sibê biçim bajêr* → `E z ê s ib ê bi ç im b aj ê r`
- **Her dilin bölme mantığı farklı mı?**
  - Evet. Bölücüler çoğunlukla İngilizce ve Çince yazıdan öğrenildiği için o dillerde sözcükleri bütün tutar, Kürtçede ise küçük parçalara böler.
  - Metin üreten dil modellerinde bu ciddi bir fark yaratır: daha pahalıdır ve sözcük bilgisi zayıflar.
- **Seslendirmede durum farklı:**
  - Harf harf girdi zaten yaygın bir yöntemdir.
  - Kürtçenin yazımı büyük ölçüde okunduğu gibidir; bu yüzden harf düzeyi Kürtçe için kötü bir seçim değil.
- **Bedeli:** Dizi uzar, eğitim biraz yavaşlar ve model sözcüğü bütün olarak "tanımakta" zorlanabilir.
- **Kürtçeye özel yeni bir bölücü gerekir mi?**
  - Şimdilik hayır. Yeni bölücü, modelin öğrendiği sözcük bilgisini sıfırlar ve çok veri ister.
  - Daha ucuz ve ölçülebilir iki deneme var:
    1. Okunuş katmanı (yukarıda).
    2. Sık geçen Kürtçe eklerin ve sözcüklerin bölücüye eklenmesi; kazanç ezgi setinde ölçülür.
  - Kazanç ölçülmeden değişiklik yapılmaz.

## Kaynaklar

- Samî Tan, *Kullandığımız Kürt alfabesi fonetik bir alfabe mi?* Gazete Duvar. https://www.gazeteduvar.com.tr/kullandigimiz-kurt-alfabesi-fonetik-bir-alfabe-mi-haber-1703632
- Barzo Omar Mahmoud (2016), *Şîrovekirineke dengsazî û fonolojî di Kurdiya Kurmancî de*, Mardin Artuklu Üniversitesi, yüksek lisans tezi. https://gcris.artuklu.edu.tr/entities/publication/c6558ef7-8383-45d0-8738-2fe4d387a93e
- Celadet Bedirxan ve Roger Lescot, *Kürt Dilbilgisi (Kurmanci Lehçesi)*. Samî Tan'ın makalesinde aktarıldığı kadarıyla kullanıldı.
- Genel tablo için: https://en.wikipedia.org/wiki/Kurdish_phonology
