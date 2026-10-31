# S31a: Kitabın vurgu kuralları gerçek seste tutuyor mu? (ÖN KAYIT, 31.10 akşam; sonuçtan önce yazıldı)


## Neden
- `nivis/kurmanci/vurgu.py` kuralları iki gramer kitabından yazdı (Tan, Karabax). Kitabın kendi örneklerinde 129/130 tutuyor, ama bu yalnız kodun kitabı doğru okuduğunu gösterir, kitabın haklı olduğunu değil. Bedirxan ve MacKenzie vurgunun düzensiz olduğunu, malzemenin az olduğunu yazıyor (T80).
- Vurguyu ses modeline öğretmeden önce kuralın konuşmada tutup tutmadığı bilinmeli. Yanlış kural sese yanlış vurgu öğretir.
- İki kitabın ayrıldığı yerler var: önekli mastar (K28 önek, T79 son hece), `bi-` dilek kipi (K28 kök, T80 `bi-`).

## Veri
- Tek okurun izinli, özel kayıtları (7.586 kesit, 33,5 sa) ve Common Voice 27 eğitim cümleleri (çok okur, kısa). Kilitli sınav cümleleri dışarıda.
- İş saate bağlı durur (2,25 sa): üç çekirdek özel okur, bir çekirdek CV, dosya sırası rastgele (tohum 31). Ne kadar ölçüldüğü sonuçta yazılır.

## Ölçü
- Harf yerleri: `torchaudio` MMS_FA zorunlu hizalama. Harf, önceki boşluğun ortasından sonraki boşluğun ortasına kadar sayılır (CTC yalnız en emin olduğu kareleri işaretler).
- Her ünlü için Praat: süre, perde (kesit medyanına göre yarım ton), ses şiddeti, 500 Hz üstü enerji payı. Vurgu fonetiğinde dördü de vurgulu ünlüde yükselir; hiçbiri tek başına kanıt değil.
- Dördü de duraktan önce de yükselir. Bu yüzden karşılaştırma hep **aynı biçim, aynı konum**: sözcüğün son hecesi ilk hecesiyle değil, aynı konumdaki öteki okuyuşla karşılaştırılır.
- Birleşik ölçü P: dört ipucunun z puanlarının ortalaması. Her ipucu aynı ünlüye göre normallenir, çünkü `a` doğası gereği `i`den uzun ve güçlüdür; perde, şiddet ve enerji payı önce kesite göre alınır. *(31.10 akşam, ana veriye bakmadan düzeltildi: DoReCo denemesinde `di-` gibi `i`li önekler haksız yere zayıf görünüyordu.)*
- **Üçüncü kaynak: DoReCo/Multi-CAST** (CC BY, Muş ve Erzurum, 2 konuşmacı, 40 dk doğal anlatı). Mac'te ölçüldü. Okuma değil konuşma olduğu için ayrı değerli, ama küçük; kabul kuralı yine özel okur + CV ile işler, DoReCo bilgi olarak yazılır.
- **Aracın sınırı:** DoReCo'nun zaman tablosuna göre sözcük sınırı ortanca 29–40 ms sapıyor, ünlü süresi uyumu zayıf (r=0,22). Tablolarda dört ipucu ayrı da yazılır.

## Sınanan kurallar
1. `-in` biçimi: geçmiş çoğul (`kirin`, kökte) ile `hat/tê/bê`'den sonraki mastar (son hecede). Beklenen: mastarın son − ilk P farkı, geçmişinkinden büyük.
2. Çekim eki saydam mı: `-ê`, `-a`, `-ek` vurguyu götürmez; `-an`, `-ên` götürür. Aynı kökte son − ilk farkı karşılaştırılır.
3. Olumsuzluk ve `di-`: vurgu önekte.
4. **Kitapların ayrıldığı yer A:** önekli mastar (`vekirin`): ilk hece mi son hece mi.
5. **Kitapların ayrıldığı yer B:** `bi-` dilek kipi: `bi-` mi kök mü.
6. `-iya`, `-iyê` (K26), `-ekî` (K28).

## Kabul (önceden)
- Bir kural yalnız iki kaynakta da (özel okur, CV), her birinde en az 30 sözcükle ölçülürse sayılır.
- **Doğrulandı:** iki kaynakta da beklenen yön, P farkı 0,1'den büyük. **Çürütüldü:** iki kaynakta da ters yön, aynı büyüklükte. Geri kalanı **açık**.
- Kitapların ayrıldığı iki yerde kazanan okuyuş `vurgu.py`'deki sabite işlenir; açık kalırsa sabit olduğu gibi durur ve kod yazısında "ölçüyle kesinleşmedi" der.
- Çürütülen kural `vurgu.py`'de düzeltilir ve S31 tam koşusu düzeltilmiş kuralla gider. Bu yüzden bu ölçüm tam koşudan önce biter.

## Sonuç (31.10 gece)
Ölçülen: özel okur 31.452 sözcük, CV 5.393 sözcük, DoReCo 2.337 sözcük (iki veya daha çok ünlüsü ölçülen). Dört işçi 2,25 saatte bitti, 8,4 saat ses. Sayı P farkı, ± %95 aralığı; önce özel okur, sonra CV, parantezde DoReCo.

| Kural | Ölçü | Sonuç |
|---|---|---|
| 1. `-in` mastar > geçmiş | iç konum +0,10; durak öncesi +0,24, CV her konumda 30'un altında | **Açık.** özel okur destekliyor (aynı fiil çifti 6/7), CV az |
| 2. `-an/-ên` son heceye, `-ê/-a/-ek` köke | iki heceli +0,25 / +0,27 (+0,25); üç heceli +0,11 / +0,17 | **Doğrulandı** |
| 3a. Olumsuzlukta vurgu önekte | son−ilk −0,31 / −0,49 (−0,61) | **Doğrulandı** |
| 3b. `di-` önekte (T80) | son−ilk +0,73 / +0,29 (+0,31); üç hecede de ilk hece en zayıf | **Çürütüldü** |
| 4. Önekli mastar (K28/T79) | 14 ve 5 sözcük | **Açık**, sözcük az |
| 5. `bi-` (T80/K28) | özel okur +0,38 ve +0,81; CV +0,06 ve −0,11; DoReCo yaklaşık 0 | **Açık**, kaynaklar ayrışıyor |
| 6a. `-iya/-iyê` (K26) | son−orta −0,26 / −0,22 (−0,40) | **Doğrulandı**: son heceye gitmiyor |
| 6b. `-ekî` son hecede (K28) | üç hecede ilk−son +0,80 / +0,86 (+0,93); `gelekî` çıkarılınca da aynı; dört hecede kök önde | **Çürütüldü**: `-ek` gibi köke bırakıyor |

## Yapılan
- `vurgu.py`: `-ekî` saydam eklere geçti. `di-` artık vurgu almıyor.
- `di-` yerine ne geldiği ön kayıtta yoktu, bu ayrıntı ölçüden türetildi: `dikarin`, `dikin` gibi `-in`, `-im` biçimlerinde son hece, `dikare` gibi biçimlerde kök (ek farkı özel okur +0,24, CV +0,37). Sınanmış değil, bulgu.
- Kitap örnekleri testi 129/130'dan 125/130'a indi. Yeni dört ıskalama (`dide`, `diçe`, `dipeyive`, `mirovekî`) bilerek: kitap söylüyor, ses söylemiyor.
- S31 tam koşusu düzeltilmiş kuralla 31.10 21:50'de gönderildi.

## Sınır
P vurgunun kendisi değil, dört ipucunun ortalaması. Ünlü süresi aracın en zayıf yanı (r=0,22). Düz isimlerin son hece kuralı (T78) iç konumda özel okur +0,16, CV +0,05: bu ölçüde kesinleşmedi, varsayılan olarak duruyor.

