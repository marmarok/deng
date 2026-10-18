# Sık sorulan sorular

*Kurdî: [PIRS-U-BERSIV.md](PIRS-U-BERSIV.md) · English: [FAQ.md](FAQ.md) · Son güncelleme: 18 Ekim 2026*

Bu sorular, projeyi yürüten kişinin bugüne kadar sorduğu sorulardan ve projeye bakan birinin sorabileceği sorulardan derlendi. Bütün sayılar ölçüm dosyalarından alındı (`pivan/`, `dane/`, `DEFTER.md`). Bir sayı yanlışsa ya da eksikse, lütfen GitHub'da "Issues" bölümüne yazın.

## Proje

**1. Deng nedir?**
Kürtçe için iki yapay zekâ modeli yapan açık bir proje.
- **Kulak:** Kürtçe konuşmayı dinleyip yazıya geçiren model. Hedefi sıradan bir sohbeti anlamak.
- **Ses:** Yazıyı Kürtçe okuyan model. Hedefi, ana dili Kürtçe olan bir dinleyicinin insan sesinden ayırt edemeyeceği kadar doğal olmak.

**2. Neden gerekli?**
Büyük diller için bu araçlar var, Kürtçe için yok ya da çok zayıf. Bugünkü makine sesleri Kürtçeyi yabancı ağzıyla okuyor: vurgu yanlış düşüyor, soru düz cümle gibi söyleniyor. Kürtçede vurgu ve ezgi anlamı taşıdığı için bunları ilk günden ölçüyoruz.

**3. Projeyi kim yürütüyor? Kodu kim yazıyor?**
- **Proje yürütücüsü:** Ana dili Kürtçe olan biri. Yazılımcı değil ve daha önce hiç yapay zekâ modeli eğitmedi. Kararlar ve sorumluluk onun.
- **Kodu, ölçümleri ve hesapları:** Claude yazıyor. Claude, Anthropic şirketinin yapay zekâsı.
- **Ekip:** İki ekip arkadaşı kendi Kaggle hesaplarıyla bilgisayar gücü veriyor.

Bunu açıkça söylüyoruz. Önemli olan kodu kimin yazdığı değil, sonucun ölçülmesi ve herkesin görebilmesi.

**4. Bir yapay zekânın yazdığı koda ve sayılara güvenilir mi?**
Körü körüne güvenilmemeli. Bu yüzden:
- Her sayı bir ölçüm dosyasından gelir.
- Kod açıktır; isteyen aynı işi yeniden çalıştırabilir.
- Hatalar yazılı tutulur. Örneğin bir soru ezgisi oranı önce 15 cümlelik küçük bir setten %87 diye yazılmıştı. Tam sette %66 çıktı ve her yerde düzeltildi.

Asıl denetim ana dili Kürtçe olan insanların dinlemesi (bkz. 25. soru).

**5. Hedef ne? Ne zaman biter?**
- **Başarı tanımı:** Ana dili Kürtçe olan dinleyiciler sesin insan mı makine mi olduğunu ayırt edemesin. Kulak da sohbeti 100 harfte en çok 5 hatayla yazsın.
- **Süre:** Tahminimiz 2027 ve 2028'e kadar sürmesi. Bu bir tahmin; her aşamanın sonunda ölçüp düzeltiyoruz.

**6. Hangi Kürtçe?**
- **Ana dil:** Standart Kürtçe (Kurmancî), yani yazı, kitap ve haber dili. Ses varsayılan olarak böyle konuşur.
- **Kulak:** Her ağzı anlamalı.
- **Ağızlar:** Her kaydın yöresi etiketlenir. Ağız grupları dilbilimcilerin sınıflandırmasından alınır: Öpengin ve Haig (2014), beş bölge. Ses, standart dil doğallaşınca ağızlarla da konuşacak.

**7. Soranî, Zazaca ya da başka diller ne olacak?**
Şimdilik yalnız Kurmancî. Önce bir dili iyi yapmak istiyoruz. Diğerleri ekip ve veri büyüyünce konuşulur.

## Nasıl çalışıyor

**8. Kulak nasıl öğreniyor?**
Hazır bir temel model alıyoruz ve ona Kürtçe ses ile doğru yazısını gösteriyoruz.
- **Temel model:** Meta'nın Omnilingual ASR modeli (1 milyar parametre, Apache 2.0 lisansı). 1.600'den fazla dil biliyor ama Kürtçede zayıf.
- **Kürtçe veri:** Common Voice ve FLEURS'tan yaklaşık 61 saatlik Kürtçe kayıt ve doğru yazıları.
- **Öğrenme:** Model kendi yazdığıyla doğru yazı arasındaki farkı küçültmeyi öğreniyor.

**9. Ses nasıl öğreniyor?**
- **Temel model:** VoxCPM2 (Apache 2.0). Türkçe ve Arapça biliyor, Kürtçe bilmiyor.
- **Eğitim:** Hafif eğitimle (LoRA) Kürtçe okumayı öğretiyoruz.
- **Ölçüm:** Her denemeden sonra ses iki yolla ölçülüyor:
  - **Anlaşılırlık:** Başka bir makine kulağı yazdıklarını yazıya geçiriyor.
  - **Ezgi:** Ezgi ölçeri soruların soru gibi söylenip söylenmediğine bakıyor.

**10. Hesaplar nerede yapılıyor?**
- **Kaggle:** Google'ın ücretsiz ekran kartlarında yapılıyor. Her hesaba haftada yaklaşık 30 saat düşüyor.
- **Hesap başına işler:** Kulak, ses ve veri hattı ayrı hesaplarda yürür ve hesaplar birbirine karışmaz.
- **Defter:** DEFTER.md her işin nerede yapıldığını yazar: ekran kartı mı, işlemci mi, Claude'un kendisi mi, Mac mi.

**11. Ne kadar para harcandı?**
Bugüne kadar sıfır. Her harcama proje yürütücüsünün onayına bağlı.

**12. Bölücü (tokenizer) nedir? Kürtçeye uyarlanmalı mı?**
- **Ne yapar:** Model yazıyı harf ya da sözcük olarak değil, küçük parçalar halinde görür. Bu parçaları ayıran araca bölücü denir.
- **Kulakta:** Bölücü her Kürtçe harfi tanıyor; tanımadığı harf yok.
- **Seste:** Kürtçe bir sözcük ortalama 2,83 parçaya bölünüyor; İngilizcede bu sayı 1,35, Türkçede 4,18. ê, î, û, ç ve ş ayrı parçalar.
- **Karar:** Şimdilik değiştirmiyoruz. Bölücü değişirse model sözcük karşılıklarını baştan öğrenmek zorunda kalır, bu da bizim veri miktarımızla riskli. Bölücü denemesi Aralık'a planlı.

**13. Kürtçede harflerden fazla ses var mı?**
Evet. Alfabede 31 harf var ama dilbilimciler daha fazla ses sayıyor:
- **Soluklu ve soluksuz ünsüzler:** p, t, k ve ç'nin her birinin iki biçimi var.
- **İki r ve iki l.**
- **Diğer sesler:** ḧ, ʿ, ẍ, ŋ ve xʷ.

Kaynaklar: Samî Tan ve Barzo Omar Mahmoud (2016). Kulak standart yazımla yazar. Ses bu ayrımları kayıtlardan duyarak öğrenir. İleride ayrı bir okunuş katmanı denenecek. Ayrıntı: `pivan/dengen-kurdi.md`.

**14. Vurgu ve ezgi nasıl ölçülüyor?**
- **Ezgi seti:** 257 cümle. Türleri: düz/soru çiftleri, soru sözcüklü sorular, gelo ve ma soruları, emir, seslenme, duygu, diyalog ve diğerleri. Bu cümleler hiçbir zaman eğitime girmez.
- **Ezgi ölçeri:** Her okunuşun perde eğrisine bakar ve "soru gibi mi" diye karar verir.
- **Ölçerin kusuru:** İnsan okumalarındaki soruların %69'unu, düz cümlelerin %89'unu doğru tanıyor. Bu yüzden asıl hakem insan kulağı.

## Veri

**15. Hangi veriler kullanılıyor?**

| Kaynak | Lisans | Miktar | Durum |
|---|---|---|---|
| Common Voice 27 (Kurmancî) | CC0 | 44.549 parça, 49,8 saat | ✅ kulak eğitimine girdi |
| FLEURS (Kurmancî) | CC BY 4.0 | 3.556 parça, 11,7 saat | ✅ kulak eğitimine girdi |
| Dengê Amerîka arşivi | Kamu malı (yalnız VOA'nın kendi ürettiği) | ~2.700 kayıt, ~1.020 saat | ⬜ sırada (önce dil denetimi) |

Tam liste: `dane/`.

**16. Bir kaydın gerçekten Kürtçe olduğunu nasıl anlıyorsunuz?**
- **Common Voice ve FLEURS:** Zaten Kürtçe. Common Voice'ta her kaydı başka gönüllüler dinleyip onaylıyor.
- **Dengê Amerîka:** Arşivde Türkçe, Arapça ya da İngilizce konuşan konuk ve müzik olabilir. Bu yüzden her kesit iki denetimden geçmeli:
  - **Sesten dil tanıma:** MMS-LID.
  - **Yazıdan dil tanıma:** GlotLID.
- **Eşik:** Bilinen Kürtçe kayıtlarla ayarlanır.
- **İnsan denetimi:** Ana dili Kürtçe biri, geçen ve kalan kesitlerden örnek dinler.

Kuralların tamamı: `dane/qaideyen-ketina-perwerdeye.json`.

**17. Sesleri gerçekten aldığınızı, uydurmadığınızı nasıl bilebilirim?**
- **Her kaydın adı:** Kullanılan her kaydın adı `dane/` klasöründe yazılı. Common Voice ve FLEURS adları o verilerin kendi açık dosyalarında aranıp bulunabilir.
- **Dengê Amerîka:** Her kaydın sitedeki adresi ve süresi listede olacak. Tıklayıp aynı kaydı dinleyebilir, süreleri karşılaştırabilirsiniz.
- **Doğrulama:** Kod ve ölçüm sonuçları açık; aynı işi yeniden çalıştırıp aynı sayıyı alabilirsiniz.

**18. Ne kadar veri gerekiyor? Nereden gelecek?**
- **Ses:** Temel modelin kılavuzu yeni bir dil için 500 saatten fazla temiz ses öneriyor. Bugün eğitimde 61,5 saat var.
- **Kaynaklar:**
  - Dengê Amerîka (~1.020 saat, kontrol bekliyor)
  - izin istenen radyo, podcast ve sesli kitaplar (mektuplar gönderildi, yazılı izin bekleniyor)
  - gönüllülerin okumaları ve sohbet kayıtları

**19. Kayıtlar kaliteye göre ayrılıyor mu?**
Evet, dört sınıf var. Her kesit otomatik ölçülür: gürültü, telefon sesi mi, müzik var mı. Ayrıca kayıt türü (stüdyo, telefon, radyo, YouTube, kafe…) yazılır.

| Sınıf | Ne | Kulak | Ses |
|---|---|---|---|
| A | Stüdyo kalitesi | ✅ | ✅ |
| B | Temiz kayıt | ✅ | ✅ |
| C | Telefon ya da oda sesi | ✅ | ❌ |
| D | Gürültülü ya da müzikli | ✅ | ❌ |

- **Kulak hepsini neden alıyor:** Kötü kayıtlar onu gerçek hayata hazırlar.
- **Ses neden yalnız A ve B alıyor:** Ses modeli gürültüyü de taklit eder.

**20. "Soru kayıtlarını" nasıl seçiyorsunuz?**
- **Yazıdan:** Common Voice'ta okunan cümle veride yazılı. "?" ile bitiyorsa soru sayılır.
- **Soru türü:** Soru sözcüğü (çi, kî, kengî, çawa…) varsa soru sözcüklü sorudur, yoksa evet/hayır sorusudur. Bunu sabit bir kural ayırır, dil modeli değil.
- **Sesten:** Bazı okuyucular soruyu düz okuyor. Ezgi ölçeri bunları eler.

**21. Telif ve izin nasıl?**
- **Lisans:** Yalnız açık lisanslı ya da kamu malı veri kullanılıyor.
- **Dengê Amerîka:** Yalnız VOA'nın kendi ürettiği malzeme kamu malı. AP, Reuters ve AFP malzemesi değil, bu yüzden video bölümü dışarıda.
- **İzinli kaynaklar:** İzin yazılı, el yazısıyla ve imzalı olmalı. İkinci bir yoldan doğrulanır.

**22. Sınav cümleleri eğitime giriyor mu?**
Hayır. Sınav setleri kilitli; kod, eğitime girmeye çalışan bir sınav cümlesini reddeder. Bir model sınav cümlesini önceden görürse puanı yalan söyler.

## Sonuçlar

**23. Kulak ne kadar iyi? CER ve WER nedir?**
- **CER:** 100 harfte kaç harfin yanlış olduğu.
- **WER:** 100 sözcükte kaç sözcüğün yanlış olduğu.

18 Ekim 2026, en iyi kulak:

| Sınav | Temel model | Bizim kulak |
|---|---|---|
| Aynı 500 kesitte WER | %29,3 | **%24,3** |
| 999 kesitin tamamı | — | CER %7,1 · WER %24,2 |
| Common Voice | — | WER %13,4 |
| FLEURS | — | WER %27,4 |

Hedef sohbette 100 harfte en çok 5 hata. Daha yoldayız.

**24. Ses ne durumda?**
- **Ezgi:** Son denemede (257 cümle) soruların %70'i soru gibi söylendi. İnsan okumalarında bu oran %69.
- **Anlaşılırlık:** Henüz yetmiyor; 100 harfte yaklaşık 16 hata.
- **Asıl çözüm:** Daha çok temiz Kürtçe ses.

**25. Sınav sonucunu kim okuyor? Gerçeği gösteriyor mu?**
- **Puanı kim çıkarıyor:** İnsan değil, bir hesap. Kulağın yazdığı, kaynağın doğru metniyle harf harf karşılaştırılıyor.
- **Ne zaman güvenilir:** Modelleri birbiriyle kıyaslamak için güvenilir, çünkü aynı sınav ve aynı ölçü kullanılıyor.
- **Mutlak doğru değil:**
  - Yazım farkları da hata sayılıyor.
  - Kaynak metinlerin kendisinde hata olabiliyor.
  - Sınav okuma konuşmasıdır, sohbet değil.
- **Çözüm:** Ana dili Kürtçe insanlar dinler. Kontrol sayfasında sınav cümleleri tek tek onaylanır. Ayrıca bir dinleme sayfası kuruluyor.
  - **Kulak:** 50 kesit.
  - **Ses:** 30 cümle. Her cümle bir de insan sesiyle, karışık sırada dinletilir.

**26. "Ayırt edilemez" nasıl ölçülecek?**
- **Dinleyiciler:** Farklı bölgelerden 30–50 dinleyici, aynı metnin insan ve makine okumasını bilmeden dinler.
- **Başarı ölçütü:** Dinleyicilerin insanı bilme oranı en çok %55 (yazı tura %50).
- **Üç sınav:** kısa cümle, uzun paragraf ve karşılıklı konuşma.

## Katılım

**27. Katılmak için kod bilmek gerekiyor mu?**
Hayır. İşlerin çoğu için Kürtçe ve bir telefon yeter. Kod bilen gönüllüler de isterse katılabilir.

**28. Claude hesabı gerekiyor mu?**
Hayır. Yapay zekâ işlerini proje yürütür; katılanlar dinler, okur, düzeltir, kayıt yapar.

**29. Hangi işler var?**

| İş | Ne yapar | Emek |
|---|---|---|
| Dil editörü | Makinenin yazdığını düzeltir, vurgu ve okunuş kurallarını yazar | Haftada 2–3 saat |
| Dinleyici | Sesleri dinleyip hangisinin doğal olduğunu söyler | İki haftada 15 dakika |
| Ses sahibi | Kendi sesiyle cümle okur (bir kadın, bir erkek seçilir) | Kayıt döneminde haftada 4–6 saat |
| Kaynak ve izin | Kürtçe radyo, podcast ve kitap bulur, izin ister | Haftada 1–2 saat |
| Ağız konuşmacısı | Kendi ağzıyla bir kez 10–15 dakika konuşur | Bir kez |
| Yazılımcı (isteğe bağlı) | Kod, ölçüm, araç | İstediği kadar |

**30. Kimler katılabilir, kimler katılamaz?**
- **Kimler katılabilir:** Kürtçe konuşan herkes. Editörlük için iyi Kürtçe okuma-yazma gerekir.
- **Sınırlar:**
  - 18 yaşından küçükler ancak ailesinin yazılı izniyle kayıt verebilir.
  - Sesini veren kişi yazılı bir sözleşme imzalar.
  - Başkasının kaydı, sahibinin izni olmadan gönderilemez.

**31. Nasıl katılırım?**
1. GitHub'da projeye bakın: github.com/marmarok/deng
2. Tirşik'ten ya da GitHub "Issues" bölümünden yazın. Şunları belirtin:
   - ad ya da takma ad
   - hangi iş
   - büyüdüğünüz il ve ilçe
   - haftada kaç saat
3. Küçük bir deneme işi yaparsınız: 10 cümle düzeltmek ya da 15 dakika dinlemek.
4. Ses verecekseniz yazılı sözleşme imzalarsınız.

**32. Sesimi verirsem ne olur? Hakkım ne olur?**
- **Sözleşme:** Sesiniz yazılı bir sözleşmeyle alınır; ne için kullanılacağı orada yazar.
- **Kayıtların saklanması:** Kayıtlar yalnız proje yürütücüsünün gizli hesabında işlenir, başka hesaba gitmez.
- **İznin geri alınması:** İzninizi geri alırsanız kaydınız sonraki modellere girmez.
- **Kopyalama:** Model yayınlanırken başkasının sesini kopyalama özelliği kapatılır.

**33. Kişisel bilgilerim yayımlanır mı?**
Hayır. Açık sayfalarda yalnız izin verdiğiniz ad görünür. Her yayından önce kişisel bilgi taraması yapılır.

**34. GitHub nedir?**
Kodun, planın ve sonuçların açıkça saklandığı bir site.
- **Okumak için:** Hesap gerekmez.
- **Soru ve öneri için:** Ücretsiz bir hesap yeter; "Issues" bölümü bunun için.
- **Burada neler var:**
  - **README:** projenin özeti
  - **DEFTER:** tarihli iş günlüğü
  - **dane:** bütün verilerin listesi
  - **pivan:** ölçüm sonuçları
  - **awaz:** ezgi cümleleri
  - **kod:** açık

**35. Ücret var mı? Para kazanılırsa ne olur?**
Katılım gönüllü ve ücretsiz. Katılanların adı "Keda wan heye" listesine yazılır ve modeli ücretsiz kullanırlar. Bir gün gelir olursa katılanların payı önceden yazılı olarak belirlenir.

**36. Model kimin olacak? Lisansı ne?**
- **Kod:** Açık, MIT lisansı.
- **Modelin lisansı:** Henüz kararlaştırılmadı. Karar açıkça duyurulacak.

**37. Ücretsiz yapay zekâlar kullanılıyor mu?**
- **Kullanım sınırı:** Claude'un kullanım hakkı sınırlı, bu yüzden bazı işler başka araçlara bölünüyor.
- **Rutin güncellemeler:** Basit betiklerle yapılıyor.
- **Kürtçe metin işleri:** Yalnız açık verilerle Google'ın ücretsiz Gemini'si düşünülüyor.
- **Yerel modeller:** Kürtçede zayıf olduğu için kullanılmıyor.

## Güven ve riskler

**38. Yapay zekâ uydurursa ne olur?**
- **Sayıların kaynağı:** Her sayı bir ölçüm dosyasına bağlı. Bir sonuç dosyada yoksa söylenmez.
- **Bilinmeyenler:** Bilinmeyen şeyler "tahmin" diye yazılır.
- **Kürtçe örnekler:** Kürtçe örneklerde uydurma riski var. Bu yüzden ana dili Kürtçe olan biri kontrol eder. Örneğin "ker/kerr" çifti yanlış örnek olarak yazılmıştı; düzeltildi.

**39. Hata olursa nasıl düzeltilir?**
- **Kayıt:** Hata DEFTER'e tarihle yazılır.
- **Eski planlar:** Silinmez, arşive kaldırılır.
- **Siz de bildirebilirsiniz:** Bir hata gördüğünüzde "Issues" bölümüne yazın.

**40. Ses kötüye kullanılabilir mi (sahte ses)?**
Bu gerçek bir risk.
- **Yayında:** Başkasının sesini kopyalama özelliği kapalı olacak. Sese gizli bir damga eklemek düşünülüyor.
- **Eğitimde:** Yalnız izinli kayıtlar kullanılır.

**41. Proje yarıda kalırsa ne olur?**
- **Belgeler:** Her karar ve her ölçüm yazılı; biri ayrılsa da iş baştan başlamaz.
- **Kod:** Açık, isteyen devam ettirebilir.
- **Her aşama kendi başına bir şey bırakır:** Örneğin bugünkü kulak bile temel modelden daha iyi.
