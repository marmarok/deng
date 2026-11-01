# S31: Kürtçe harf dizisi ve vurgu işareti (ÖN KAYIT, 31.10 akşam; sonuçtan önce yazıldı)


## Neden: ölçülen durum
- **Kulak:** harf harf çalışıyor (10.288 belirteç, Kürtçe harflerin hepsi var, `ˈ ʰ · ẍ` de var). Değişiklik gerekmiyor.
- **Ses:** VoxCPM2'nin metin yolu BPE: 73.440 parça, başka diller için kurulmuş, Kürtçe yok. 8.000 Orient kesitinde 3.334 ayrı parça, bunların 1.629'u en çok 5 kez görülüyor. Sözcükleri anlamsız yerlerden kesiyor (`hatin → ▁h|atin`, `dixwazim → ▁d|ix|w|az|im`). `w` 537 parçaya, `c` 2.253 parçaya dağılmış; `xw` tek parça olarak hiç yok. Gömmeler donuk olduğu için LoRA bütün bu parçaları tek tek öğrenmek zorunda.
- Yeni dizi aynı kesitlerde **35 ayrı belirteç** kullanıyor (41'lik alfabenin), cümle başına 94,2 yerine 215,3 belirteç (2,29 kat uzun; ses bu uzunluğun yanında kısa kaldığı için adım süresi ölçülecek).

## Değişen tek şey: metin yolu
- **Kol a:** ses başına bir belirteç: 31 harf, `xw` tek ses (K22, kitapların tek pevdengi), boşluk, noktalama. Donuk gömmelerin üstünde küçük, eğitilen bir tablo (41 satır, adı `lora_` içerir, LoRA ile kaydedilir). Modelin kendi sözlüğüne ve ağırlıklarına dokunulmaz: `xw` ve vurgu işareti kullanılmayan `<reserved_N>` yuvalarında.
- **Kol b:** a + vurgulu ünlünün önünde işaret (`nivis/kurmanci/vurgu.py`, iki kitabın kuralları, S31a ile sınanmış hali).
- Geri kalan her şey S28: aynı 7.586 özel okur kesiti, `hazirla`, LoRA r32, öğrenme hızı, tohum 11, 1.500 adım, sıfırdan başlangıç. **Karşılaştırma S28'le:** yeniden eğitmeye gerek yok, sayıları aynı cümlelerde S29'un koşusunda ölçüldü.
- İki kol aynı anda iki kartta. Ses bir izinli okurun sesini taklit eder: **ekip içinde kalır, yayımlanmaz.**

## Ölçüm koşusu
60 adım iki kolda, 3 + 4 cümle okuma, çift ölçümü. Bakılan: tablo eğitilip kaydediliyor mu, geri yükleniyor mu, adım süresi (uzayan metin), kart belleği, okuma süresi. Tam koşu yalnız ölçülen sayılarla planlanır (`measure.json`).

## Ölçüm (tam koşu)
- 257 cümlelik ezgi seti, 10 ilerleme cümlesi, S27'nin üç cümlesi, tohum 1, s4 uzunluk bekçisi. Hakemler aynı: kulak U3, ezgi hakemi.
- **S28'in karşılık sayıları (S29 koşusu):** harf 4,84 · soru gibi %47,6 · düz gibi %85,1 · ilerleme 14,37 · S27 0,92.
- **Vurgu çiftleri (bilgi, kilitli değil):** `nivis/kurmanci/veri/vurgu-ciftleri.tsv`: aynı fiil, cümlenin son sözcüğü, iki okuyuş: `Wan kar kirin.` (kökte) / `Kar hat kirin.` (son hecede). 13 çift, ikisi önekli (kitaplar ayrılıyor). Üç ses okur: a, b, S28.
- Çift göstergesi D: mastardaki (son − ilk) P farkı eksi geçmişteki (son − ilk) P farkı. Doğru yönde D > 0. Hesap `nivis/kurmanci/vurgu_olcum.py`.

## Kabul (önceden)
1. **Harf dizisi tuttu:** en iyi kolun harf hatası ≤ 5,34 (S28 + 0,5) **ve** soru ≥ %42,6 **ve** düz ≥ %80,1 → bundan sonraki bütün ses eğitimleri bu metin yolundan gider.
2. **Vurgu işareti tuttu:** 1. şart b kolunda sağlanıyor **ve** önceksiz 11 çiftin en az 8'inde D > 0 **ve** D'nin ortancası a ve S28'inkinin en az iki katı → vurgu işareti kalır, dinleyicilere kör çift dinletilir, son söz onun kulağının.
3. **Harf dizisi geride ama eğri düşüyor:** harf hatası > 5,34, kayıp 1.500. adımda hâlâ iniyor → aynı kol 2.500 adıma uzatılır (S32). Harf harf okumak, BPE'nin hazır bildiği parçaları sıfırdan öğreniyor; bu mümkün olan bir sonuç.
4. **Geride ve eğri düz:** ses öğretmeni S28 kalır, metin yolu geri alınmaz ama üretime girmez, sebep aranır.
- Doğallığa insan kulağı karar verir; bu ölçüm yalnız "anlaşılıyor mu, ezgi doğru mu, vurgu istenen yere gidiyor mu" sorularını cevaplar.

## Sonuç (01.11 sabah)
Eğitim iki kolda 1.500 adımı bitirdi (13,3 ve 14,0 sn/adım, 6,15 sa). Okuma 63,4 dk. Tablo ağırlıklara kaydedildi (41 × 2.048). Kayıp eğrisi üç seste de aynı (son bölüm a 0,80, b 0,83, S28 0,84).

| Ölçü (düşük harf hatası iyi) | S28 | a: harf dizisi | b: + vurgu işareti | Eşik |
|---|---|---|---|---|
| Harf hatası, ezgi seti | 4,84 | **3,40** | 4,66 | ≤ 5,34 |
| İlerleme cümleleri | 14,37 | **8,73** | 10,42 | |
| Soru soru gibi | %47,6 | **%31,2** | %34,9 | ≥ %42,6 |
| Düz düz gibi | %85,1 | %83,4 | %79,7 | ≥ %80,1 |
| Soru/düz ayrımı (AUC, sonradan hesaplandı) | 0,70 | 0,61 | 0,62 | |
| Çift göstergesi D: doğru yön, ortanca | 5/5, +0,38 | 3/7, −0,13 | 2/5, −0,09 | 8/11 ve iki kat |

S27'nin üç cümlesi (a 11,01, b 2,75) çok az cümle, karar için kullanılmadı.

## Karar
- **Vurgu işareti tutmadı (kural 2):** 1. şart b kolunda sağlanmadı, çiftlerde yön de yok. İşaret harf hatasını da artırdı. Çıkarıldı. Sınır: 11 çiftin yalnız 5'i iki okuyuşta da ölçülebildi, bu yüzden "işaret vurguyu taşıyamaz" değil, "bu koşuda taşımadı" denir.
- **Harf dizisi:** kural 1 soru ezgisinde düştü, varsayılan olmadı. Kural 3 ve 4 de uymuyor, çünkü harf hatası geride değil, önde. **Bu durum ön kayıtta yoktu:** a kolu %30 daha net okuyor ama soruyu daha az soru gibi okuyor. Eşikler sonradan gevşetilmedi.
- **Üretimde S28 kalır.** Metin yolu ve a kolu saklanır, kayıp yok (cikti/lora-a/`).

## Neden olabilir (ölçülmedi)
Sorudaki kayıp eşik kayması değil, gerçek ayrım kaybı: AUC 0,70'ten 0,61'e indi. Olası sebep: `?` işareti 94 belirteç yerine 215 belirteç içinde kalıyor ve eğitim okumalarında soru az. Doğrulanmadı.
