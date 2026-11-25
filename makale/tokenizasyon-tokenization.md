# Deng Tokenization Article

23 November 2026 · Deng Project, working draft

**Letters, not pieces: Kurmanji Kurdish text units for speech recognition and synthesis on frozen multilingual models**

## Abstract

**Background.** Kurmanji Kurdish is a low-resource language written in a near-phonemic Latin alphabet whose spelling leaves stress, aspiration and the trill unwritten. Adapting large multilingual speech models to it puts the text interface at the centre: the units a voice reads and a recogniser writes.

**Methods.** We measured how the byte-pair vocabulary of a 2-billion-parameter multilingual text-to-speech model (VoxCPM2) segments Kurmanji. We then replaced it with a 41-symbol character path, installed through existing and reserved tokens and a trainable residual embedding table, with versioned and fingerprinted text formats. Voices were trained with LoRA on a 33.5-hour single-reader audiobook in pre-registered comparisons, and judged by a recogniser, a prosody classifier, acoustic stress measures and blind listening. For the recogniser (Omnilingual ASR), we studied the label conventions and spelling around its 9,812-character inventory.

**Results.** The stock tokenizer used 3,334 distinct pieces on Kurmanji, almost half of them seen five times or fewer. At equal training, letters cut letter error from 3.62 to 2.61 per 100 letters (paired difference −1.01 [−1.51, −0.53]). The gain was largest for letters Kurmanji reads differently (*c* 32.3% → 5.1%) and cost 24% more GPU time; question–statement separation was unchanged (0.683 against 0.680). Writing *xw* as two letters cut its error from 7.2% to 0.5%, and a leading word boundary cut first-word errors in statements from 8.5% to 3.2%. Stress marks on vowels reached the voice but did not move stress (C = −0.025 [−0.095, +0.039]). The rule-based marks matched the reader's most prominent vowel in only 58% of two-syllable words, against a chance level of 50%. For the recogniser, matching the base model's label convention turned a loss against the base model into a gain, and inconsistent reference spelling accounted for about 1.9 points of word error.

**Conclusions.** For a language absent from a frozen multilingual voice, letters with learned corrections beat subword pieces. New symbols must start from trained embeddings, and prosodic marks must agree with the training audio. We close with a practitioner's guide for users, builders and teams starting from scratch.

**Keywords:** Kurmanji Kurdish; tokenization; text-to-speech; speech recognition; low-resource languages; character-level models; lexical stress.

## Türkçe özet (sade dil)

**Bir cümlede:** Ses modelimize Kürtçeyi hazır parçalarla değil harf harf okutmak sesi belirgin biçimde netleştirdi. Vurgu işaretleri ise işe yaramadı, çünkü kitapların vurgu kuralları okurun gerçek vurgusuyla neredeyse hiç örtüşmüyordu.

**Sorun neydi?** Bir yapay zekâ modeli metni doğrudan okumaz. Önce metni küçük parçalara böler (*tokenizasyon*: metni modelin tanıdığı birimlere ayırma) ve her parçanın modelin içinde bir sayısal karşılığı vardır (*gömme* ya da *embedding*). Ses modelimizin (VoxCPM2) parça sözlüğü (*BPE*: sık geçen harf öbeklerinden kurulan hazır sözlük) Kürtçe hiç görmemiş 30 dil için kurulmuş. Bu sözlük Kürtçe sözcükleri anlamsız yerlerden kesiyor: *dixwazim* "d | ix | w | az | im" oluyor ve tek ses olan *xw* ikiye bölünüyor. Kürtçe metinde 3.334 ayrı parça çıktı, bunların yarıya yakını beş kezden az görülüyordu. Model bu parçaların her birinin Kürtçede nasıl okunduğunu tek bir okurun 33,5 saatlik kaydından öğrenmek zorundaydı.

**Ne yaptık?** Parçaları harflerle değiştirdik. Kürtçenin 31 harfinin her biri modelde tek bir birim oldu; yanına boşluk ve yedi noktalama işareti geldi. Modelin kendi ağırlıklarına (*ağırlık*: modelin öğrendiği sayılar) dokunmadık. Her harfe yalnız küçük bir düzeltme satırı ekledik ve bunu eğittik. Eğitim yöntemi *LoRA*: büyük modeli dondurup üstüne küçük, öğrenilebilir ekler takmak. Her denemenin kuralını sonuç gelmeden önce yazdık (*ön kayıt*), sonradan eşik değiştirmedik.

**Ne bulduk?**
- **Ses netleşti.** Aynı eğitim miktarında 100 harfte yanlış duyulan harf sayısı (*harf hatası*) 3,62'den 2,61'e indi; bir tur daha eğitince 1,72–2,04'e. Bu, projenin şimdiye kadarki en net sesi.
- **Kazanç tam Kürtçeye özgü harflerde.** Eski yolda *c* harfinin %32'si yanlış okunuyordu (ç ya da k gibi), harf yolunda %5'i. *x* %23'ten %4'e, *q* %11'den %3,5'e indi.
- **Bedeli küçük.** Harf dizisi 2,3 kat uzun olduğu için eğitim adımı %37–45 yavaşladı; toplam ekran kartı süresi yaklaşık dörtte bir arttı.
- ***xw* iki harfle yazılınca düzeldi.** Ona ayrı bir birim vermiştik; model onu hiç öğrenmedi ve *xwedê*'yi *wedê* diye okudu (%7,2 hata). *x* ve *w* diye yazınca hata %0,5'e indi.
- **Cümlenin ilk sözcüğü.** İlk sözcüğün önüne de bir boşluk birimi koyunca düz cümlelerde ilk sözcük hatası %8,5'ten %3,2'ye indi.
- **Soru ezgisi değişmedi.** Harf yolu soruyu düz cümleden ayırmada eski yol kadar iyi (0,683'e 0,680). Sorularda geride kalmamızın sebebi metin yolu değil veri: okurun 7.586 kesitinde yalnız 73 soru var.

**Ne işe yaramadı ve neden?** Vurgu işaretleri. Kurmancîde aynı yazılan sözcük vurguyla ayrılabilir: *hátin* "geldiler", *hatín* "gelmek". Vurgulu ünlüye bir işaret ekledik. İşaret modele ulaştı ama vurguyu yerinden oynatmadı. Sebebini sonra bulduk: kitapların kuralıyla konan işaret, okurun seste gerçekten öne çıkardığı heceyle iki heceli sözcüklerde yalnız %58 örtüşüyordu (yazı tura %50). Model, seste karşılığı olmayan bir işareti öğrenemezdi. Ders: bir işareti öğretmeden önce sesle ne kadar örtüştüğünü say. İyi haber de var: ses, aynı yazılan iki sözcüğü cümledeki yerinden zaten kendisi ayırıyor.

**Gizli sesler.** Yazının göstermediği soluklu ve soluksuz *ç, k, p, t* ayrımını okurun kendi sesinde ölçtük (*VOT*: patlamadan ünlünün başlamasına kadar geçen süre). Okur bu ayrımı *k*'de kesin, *p*'de büyük olasılıkla yapıyor (aradaki fark 22–24,5 milisaniye). *t*'de bu ölçüyle gösterilemedi. 51 sözcüklük ilk ölçülmüş liste çıktı.

**Kulak tarafı.** Kulak modelimizin (Omnilingual ASR) harf listesi Kürtçenin bütün harflerini zaten içeriyor (9.812 karakter); oraya dokunmak gerekmedi. Önemli olan yazı alışkanlıklarıydı. Eğitim yazısını modelin alıştığı biçime (küçük harf, noktalamasız) çevirince kulak ilk kez hazır modeli geçti. Tek bir yazım alışkanlığı (*sûrîyê* / *sûriyê*) yayın sınavında 5 puanlık kaybın çoğunu açıklıyordu. Sınav metinlerinin kendi yazım tutarsızlığı yaklaşık 1,9 puan hata ekliyor. Kalan hatalar ünlülerde ve sözcük sınırlarında; bunlar bağlamla çözülür.

**Zayıf yanlarımız.** Bütün sesler tek okurun tek kitabından eğitildi; sohbet diline ve başka ağızlara genellenip genellenmediğini bilmiyoruz. Netliği kendi kulağımız ölçüyor, kulağın kendi hataları sayılara karışıyor. Kör dinlemeyi yalnız üç kişi bitirdi; bu yalnız yön gösterir. Fonem (ses birimi) girdisi ve Kürtçeye özel parça sözlüğüyle karşılaştırma yapmadık.

**Sırada ne var?** Soru ve doğal konuşma içeren veri; okurun gerçek vurgusundan çıkan işaretler ve kabinde aynı cümlenin iki ayrı vurguyla okunduğu kayıtlar; soru başındaki işaretin sınanması; ağız etiketi; kulak için büyük Kürtçe metinle bağlam desteği.

**Makale kimin için?** Üç okur için adım adım bir rehber içeriyor: modellerimizi kullanacaklar, bizim üstümüze inşa edecekler ve başka bir dil için sıfırdan başlayacaklar. Her biri için kod örnekleri ve kontrol listeleri var.

**Küçük sözlük.** *Tokenizasyon*: metni modelin okuyacağı birimlere bölmek. *BPE*: sık geçen harf öbeklerinden kurulan hazır parça sözlüğü. *Gömme (embedding)*: her birimin modelin içindeki sayısal karşılığı. *LoRA*: büyük modeli dondurup küçük ekler eğitme yöntemi. *Harf hatası (CER)*: 100 harfte yanlış duyulan harf. *Sözcük hatası (WER)*: 100 sözcükte yanlış yazılan sözcük. *Ayırt etme (separation)*: sorunun düz cümleden ne kadar iyi ayrıldığı; 0,5 şans, 1 kusursuz. *Ön kayıt*: denemenin karar kuralını sonuç gelmeden yazmak. *Güven aralığı*: köşeli parantezdeki iki sayı; gerçek farkın büyük olasılıkla bu aralıkta olduğunu söyler.

## 1 Introduction

The Deng project builds two models for Kurmanji Kurdish: an "ear" that understands ordinary Kurmanji conversation and a "voice" whose Kurmanji a native speaker could not tell from their own. Kurmanji is spoken by millions, mostly in Turkey, Syria, Iraq and Iran and in the diaspora, yet it has little transcribed speech. In it, stress and intonation decide meaning: *hátin* 'they came' and *hatín* 'to come' are written alike, and a question is often marked by intonation alone. The project runs on volunteers' time and free cloud GPUs, so both models are adapted from large multilingual models rather than trained from scratch.

Adaptation puts the text interface in the centre. A recogniser writes text in units its decoder knows; a TTS model reads text in units its embedding table knows. The voice's backbone, VoxCPM2, supports 30 languages and Kurdish is not one of them (Zhou et al., 2025). Its byte-pair vocabulary of 73,440 pieces cuts Kurmanji words where no morpheme boundary exists: *dixwazim* 'I want' becomes `▁d|ix|w|az|im`, splitting the single sound /xʷ/ in two. On 8,000 Kurmanji segments the stock tokenizer used 3,334 distinct pieces, and almost half of them occurred five times or fewer. Under low-rank adaptation the embeddings stay frozen, so the voice would have to learn the Kurmanji sound of each of those pieces from 33.5 hours of one reader.

We replaced the pieces with letters. Our character path gives each of the 31 Kurmanji letters one token, adds a word boundary and seven punctuation marks, and installs them on the frozen model through tokens it already has and a small trainable table of corrections. Around this core we built versioned text formats with fingerprints, so that a voice is always read with the sequence it was trained on. We then tested each design choice in controlled, pre-registered runs (S31–S34 b). We also tested stress marks and measured the hidden aspiration contrast in the reader's own voice. For the ear, whose multilingual base model already writes characters, we studied the label conventions and spelling around its units.

This paper makes seven contributions.

1. **A measured diagnosis and a fix.** We measure what a stock multilingual TTS tokenizer does to Kurmanji. We then show how to install a 41-symbol character path without changing a single weight or vocabulary entry of the checkpoint, using reserved tokens and a residual embedding table (Section 5).
2. **Letters beat pieces at equal training.** Letter error fell from 3.62 to 2.61 per 100 letters (paired difference −1.01 [−1.51, −0.53]), and to 1.72–2.04 after one more epoch. The gain is concentrated in the letters whose Kurmanji value differs from other languages: *c* 32.3% → 5.1%, *x* 23.1% → 3.7%. Separation of questions from statements was preserved (0.683 against 0.680) (Section 7).
3. **A negative result with its cause.** Stress marks placed on the vowel reached the voice but did not move the stress (C = −0.025 [−0.095, +0.039]). The rule-based marks matched the reader's most prominent vowel in 58% of two-syllable words, where chance is 50%, so the audio could not teach them (Section 7.6).
4. **What a residual table learns.** Independent trainings agree on the corrections for the letters whose sound differs, while rows that start from nothing do not learn. This gives a rule for adding any new symbol: start it from the letter it modifies (Section 7.7).
5. **Kurmanji-specific design results.** Writing *xw* as two letters cut its error from 7.2% to 0.5%. A leading word boundary cut first-word errors in statements from 8.5% to 3.2%. We also report the question head and acronym spelling. In the reader's own speech, aspirated and plain k and p differ by 22–24.5 ms, giving a first measured lexicon of hidden sounds (Sections 7.4, 7.5, 7.8).
6. **For the ear, conventions matter more than units.** Matching the base model's label convention turned a recogniser that was worse than its base into one that was better. Inconsistent spelling in the test references accounts for about 1.9 points of word error (Section 7.9).
7. **A practitioner's guide.** Steps, code and checklists for three readers: users of our models, builders on our path, and teams starting from scratch in another language, together with safeguards against the silent failures we met (Sections 8.6 and 11).

Section 2 explains why Kurmanji needs its own tokenization. Sections 3 and 4 review the tokenization literature and the experience of neighbouring languages. Section 5 describes our text paths, Section 6 the experiments and Section 7 the results. Sections 8 to 10 discuss them, state their limits and set out future work. Section 11 is the guide, and Section 12 concludes.

## 2 Why Kurmanji needs its own tokenization

Kurmanji is written in a Latin alphabet that is close to one letter per sound, so letters are a natural unit for speech. Its spelling, however, leaves out exactly what a voice must get right: stress, aspiration and the trill. Its grammar puts meaning into short endings and clitics, and the language reaches a model through few, noisy and dialectally varied texts. This section sets out these properties and what each means for a tokenizer. Grammar facts are cited by page from two reference grammars, Tan (2011, "T") and Karabax (2013, "K"); `metin/rezimana/KITAP-NOTLARI.md` holds our page-by-page notes on both.

### 2.1 An almost phonemic alphabet

Kurmanji (Northern Kurdish) uses a Latin alphabet of 31 letters standardised in the 1930s. The grammars count one further unit, the compound sound *xw* /xʷ/, as in *xwarin* 'to eat' (K22; T34–35). There are eight vowels, five long (a ê î o û) and three short (e i u), and 23 consonants (K22–23; T34). Sorani, the other main Kurdish standard, is written in an Arabic-based alphabet. Both writing systems represent vowels explicitly (Esmaili & Salavati, 2013). For a TTS model this is good news: a letter predicts its sound far better than in English, where graphemes still beat phonemes for recognition (Irie et al., 2019).

Three letters behave differently from the languages a multilingual model has mostly seen. *c* is /dʒ/, *x* is /x/, and *q* is the uvular /q/. The circumflex letters ê, î and û are separate phonemes, not accented variants: *we* 'you (pl.)' and *wê* 'her', *kur* 'son' and *kûr* 'deep'. Our measurements show that a stock BPE path reads *c* as ç or k and *x* as "ks" (Section 7.2), which is the expected failure for letters whose value differs across languages.

### 2.2 What the spelling does not write

Four contrasts that speakers hear are absent from the page.

- **Aspiration.** Each of ç, k, p and t stands for an aspirated and a plain stop. Tan's second edition treats the difference as phonemic because it separates words (T38–39): *kar*, *ker* and *ter* are each two different words written alike (K35; T76). Tan concludes that the alphabet is therefore not fully phonetic, and that the contrast should be marked in textbooks and dictionaries but not in everyday writing (T40).
- **Tap and trill r.** The r is phonemic: *pir* 'bridge' and *pir* (also written *pirr*) 'many' are told apart by it (T40, T76). The trill is written as `rr` only where the writer chooses to; T41 recommends doing so only to separate homographs. Besides their vowel, *kirin* 'to do' and *kirîn* 'to buy' differ in both the r and the k (T32).
- **Pharyngeals.** ḧ and ʿ, and ẍ in Arabic loans, are heard in native words too (*hesin*, *hewr* ~ *ʿewr*), but they distinguish no words and are not written (T39–40).
- **Stress.** Stress is not written, and it distinguishes verb forms: *hatín* 'to come' against *hátin* 'they came'. The same holds for *gotin*, *ketin*, *birin*, *girtin* and many others (T79).

The spelling also differs from speech in regular ways. Similar consonants at a morpheme boundary merge (*rind* + *-tir* → [rintir]; *serokkomar* → [serokomar], T44–46), vowels meet and fuse in verb forms (*diavêje* → [davêje], T43), and long vowels shorten before y and w (T46–48). A character-level voice has to learn these from audio, as a human reader does. A lexicon or phoneme layer would have to encode them explicitly.

### 2.3 Endings that carry the grammar

Kurmanji marks grammar mostly with short suffixes and clitics, many of them a single vowel.

- **Izafe.** Nouns link to their modifiers with *-ê* (masculine), *-a* (feminine) and *-ên* (plural), with a *-y-* after vowels (*maseya*, *deriyê*) (K41). Chains are common (*hespê kalê mîrê eşîrê* 'the horse of the old man of the emir of the tribe', K47). The two izafe letters a and ê are skewed in Kurmanji letter frequencies because of this role (Esmaili & Salavati, 2013). Unlike Persian, whose script usually leaves the ezafe unwritten (Doostmohammadi et al., 2020), Kurmanji writes it.
- **Case and gender.** The oblique case is *-ê* (feminine), *-î* (masculine) and *-an* (plural) (K42); masculine nouns may also change their stem vowel (*bajar* → *bajêr*, K43). Gender is visible only in the endings, so *kara me* 'our kid goat' and *karê me* 'our work' differ by one letter (T76). The indefinite article has its own forms (*-ek*, *-ekî*, *-eke*, *-ine*, K54).
- **Clitics written apart.** Person markers of the copula are written as separate words (*ez hozan im*, *tu hozan î*) and carry no stress (K106). Prepositions fuse with pronouns (*bi* + *hev* = *pev*, *di* + *ê* = *tê*, K74–75).
- **Verb morphology.** Verbs have a present and a past stem; *di-* marks the present, *bi-* the subjunctive and imperative, *na-*, *ne-* and *me-* negation, and these prefixes sit between a preverb and the stem (*vedixwînim* 'I invite', *venaxwînim* 'I do not invite', K156, K174). Light verbs such as *kirin* 'do', *bûn* 'be', *dan* 'give' and *girtin* 'take' form compound verbs. The nominal part is written apart when the verb is conjugated and joined in the infinitive used as a noun (*dest pê dike* but *destpêkirin*, T369; K274–279). The passive uses *hatin* 'come' and the causative *dan* or *-andin* (K237–243).

For a subword vocabulary learned on other languages, this means that the most informative parts of a Kurmanji word are its least protected. A BPE merge may swallow the *-ê* of an izafe into one piece in one word and leave it alone in another. The character path writes every ending the same way in every word. For the ear, compound verbs and postpositions explain why word boundaries are a fifth of its errors (*pê re* / *pêre*, Section 7.9): the boundary is a spelling convention that speech does not mark.

### 2.4 Ergativity and spoken grammar

In the past tense of transitive verbs, Kurmanji is ergative. The agent takes the oblique case and the verb agrees with the object: *Min tu dîtî* 'I saw you', *Te ez dîtim* 'you saw me' (K159–161). Sorani has lost the oblique pronouns and uses pronominal enclitics instead (Esmaili & Salavati, 2013). In speech, especially where Turkish is strong, the alignment weakens. Speakers say *Ez nan xwarim* with a nominative agent, or a "double oblique" *Min wî dît* that the written standard does not accept (T81–83). Educated writers also break verb agreement (T109–110).

This matters less for the voice than for the ear and for text preparation. A text normaliser for Kurmanji must not "correct" grammar, because a transcript should say what the speaker said, and written text is not always the gold standard.

### 2.5 Stress and intonation

Word stress falls by default on the last syllable of nouns, adjectives and infinitives. The endings *-ek*, *-ê* and *-a* leave it on the stem, while plural *-ên* and *-an* take it (T78–79; K27–28). Conjugated verbs are stressed on the last syllable of the stem, which is why *hátin* and *hatín* differ. Negation, preverbs and mood prefixes take the stress (T79–80). The grammars themselves warn that stress is irregular and the evidence thin, so these rules are a hypothesis to test in speech (T80). We did test them (Section 7.6).

Above the word, focus falls on the word or phrase the speaker stresses (T340). A question without a question word is made by intonation alone; *gelo*, *ma* and *qey* reinforce it (T305). In writing, the question mark is a question's only trace (T377), and it stands at the end of the sentence, far from the start where the voice begins.

### 2.6 One standard, many dialects

Kurmanji is spoken across Turkey, Syria, Iraq, Iran and the diaspora, and its regional variation is only beginning to be classified (Öpengin & Haig, 2014). The grammars note regular alternations: *v*/*w* in some south-eastern dialects (*av* → *aw*, T51), fronted *û* in some regions (T49–50), and variant pairs such as *mirov*/*merov* and *wiha*/*weha* (T347–352). Tan also records a generational effect of Turkish: young speakers struggle to keep ê apart from e (*ter*/*têr*, *şer*/*şêr*) and pronounce u and û as Turkish u and ü (T52).

Our principle, fixed on 18 October 2026, is that the written target is standard Kurmanji and the dialect is a separate label. Writing the same word in two dialect spellings would split what the voice learns for that word into two halves.

### 2.7 Spelling in the wild

Kurmanji text on the web is written mostly on Turkish and English keyboards. Circumflexes go missing, Turkish ı, İ and ü appear, and quotation marks and apostrophes vary. Capital i is dotless in Kurmanji (`I`), so a dotted `İ` in a text is a trace of Turkish keyboards or of optical character recognition (T368). A circumflex-restoration tool we built shows the scale. Of 11,050 words in held-out crowd-sourced sentences, only 60.8% are correct when the circumflexes are stripped, and restoration brings this back to 95.9%. About a third of the remaining errors are word pairs where both spellings are real words (*we*/*wê*, *te*/*tê*, *ji*/*jî*, *de*/*dê*) and only meaning decides. Kurdish lacks a unified orthography, which a Kurdish tokenizer must handle (Ahmadi, 2020a).

### 2.8 More than one script

Kurdish is a bi-standard language: Sorani in an Arabic-based alphabet, Kurmanji in a Latin one (Esmaili & Salavati, 2013). Kurmanji is also written in a Perso-Arabic script, for example on news websites in Iraqi Kurdistan, and no corpus of that variant existed until it was crawled for script-normalisation research (Ahmadi & Anastasopoulos, 2023). Transliteration between the two alphabets is ambiguous: one Arabic-based letter maps to two Latin letters for *u*/*w*, *y*/*î* and *e*/*h* (Esmaili & Salavati, 2013). Our voice reads Latin-script text only. The path breaks Arabic-script characters into word boundaries and counts them rather than guessing a transliteration.

### 2.9 Few resources

Kurdish has 20–30 million speakers (as summarised by Esmaili & Salavati, 2013), yet it is still a low-resource language for speech. The voice's backbone supports 30 languages, and Kurdish is not one of them (Section 5.1). Our ear's human-transcribed Kurmanji speech amounts to 61.5 hours from two public corpora; FLEURS provides about 12 hours per language (Conneau et al., 2023). The voice has one permissioned audiobook of 33.5 hours with one reader. A vocabulary learned elsewhere therefore meets Kurmanji with pieces it has rarely seen, and the data are too small to relearn them one by one (Section 5.2).

### 2.10 Summary: what a Kurmanji tokenizer must respect

| Property | Consequence for text units | What Deng does |
| --- | --- | --- |
| Near one-to-one letters and sounds | letters are a sound-level unit | one token per letter (Section 5.3) |
| c, x, q, ê, î, û differ from other languages | foreign pieces carry foreign sounds | a trainable correction per letter (Section 5.4) |
| *xw* is one sound in two letters | a new token needs a trained start | written as x + w (Sections 5.5, 7.5) |
| Aspiration, trill and stress unwritten | text alone cannot say which word is meant | context; marks only with a lexicon (Sections 5.6, 5.7) |
| One-letter endings carry the grammar | pieces must not cut endings arbitrarily | characters keep every ending identical |
| Question marked only at the end | the voice learns the question too late | question head at the start (Section 5.3) |
| Dialects vary in spelling | two spellings split learning | standard spelling plus a dialect label |
| Keyboard and OCR noise | foreign letters and missing circumflexes | folding, foreign-letter map, circumflex restoration |
| Arabic-script Kurmanji exists | silent mis-transliteration | break and count unknown characters |
| Little data | rare pieces are not learned | 35 frequent symbols instead of 3,334 pieces |

## 3 Related work

Over the last decade, tokenization research moved from fixed subword vocabularies to two other lines of work. One measures what those vocabularies cost in each language. The other builds models that read characters, bytes or learned patches. Speech research meanwhile built its own discrete units for audio. Table 1 lists the most-cited works in these lines with their citation counts in OpenAlex, retrieved on 23 November 2026 through its public API. Counts include preprint versions where OpenAlex merged them and are a rough guide to influence, not to quality.

**Table 1.** Most-cited tokenization and speech-unit works discussed here (OpenAlex, 23 November 2026).

| Area | Work | Year | What it introduced or showed | Citations |
| --- | --- | --- | --- | --- |
| Subword vocabularies | Sennrich, Haddow & Birch | 2016 | BPE for open-vocabulary translation | 10,260 |
| Subword vocabularies | Wu et al. (GNMT) | 2016 | WordPiece at production scale | 9,435 |
| Subword vocabularies | Kudo & Richardson (SentencePiece) | 2018 | language-independent training from raw sentences | 5,414 |
| Subword vocabularies | Kudo | 2018 | unigram LM segmentation, subword regularisation | 1,844 |
| Subword vocabularies | Gage | 1994 | byte-pair encoding as data compression | 1,665 |
| Subword vocabularies | Schuster & Nakajima | 2012 | WordPiece, built for Japanese and Korean voice search | 1,380 |
| Subword vocabularies | Bostrom & Durrett | 2020 | unigram LM aligns better with morphology than BPE | 457 |
| Subword vocabularies | Provilkov et al. (BPE-dropout) | 2020 | stochastic BPE segmentation | 441 |
| Subword vocabularies | Creutz & Lagus (Morfessor) | 2007 | unsupervised morpheme segmentation | 405 |
| Cost across languages | Rust et al. | 2021 | fertility, continued words, monolingual tokenizers | 666 |
| Cost across languages | Petrov et al. | 2023 | up to 15-fold length differences between languages | 504 |
| Cost across languages | Mielke et al. | 2021 | survey of open-vocabulary modelling | 391 |
| Cost across languages | Ahia et al. | 2023 | tokenization and the price of commercial APIs | 327 |
| Cost across languages | Ali et al. | 2024 | tokenizer choice in LLM training | 183 |
| Cost across languages | Zouhar et al. | 2023 | Rényi efficiency as a tokenizer measure | 131 |
| Characters, bytes, patches | Xue et al. (ByT5) | 2022 | byte-to-byte pre-trained models | 939 |
| Characters, bytes, patches | Lee, Cho & Hofmann | 2017 | fully character-level translation | 497 |
| Characters, bytes, patches | Clark et al. (CANINE) | 2022 | tokenization-free encoder with downsampling | 432 |
| Characters, bytes, patches | Yu et al. (MEGABYTE) | 2023 | multiscale patches over bytes | 233 |
| Characters, bytes, patches | Tay et al. (Charformer) | 2022 | gradient-based subword tokenization | 204 |
| Characters, bytes, patches | Pagnoni et al. (BLT) | 2024 | entropy-based byte patches at LLM scale | 145 |
| Vocabulary adaptation | Hu et al. (LoRA) | 2022 | low-rank adaptation of frozen models | 24,655 |
| Vocabulary adaptation | Gal et al. (textual inversion) | 2023 | new "words" in a frozen model's embedding space | 2,545 |
| Vocabulary adaptation | Pfeiffer et al. | 2021 | adapting multilingual models to unseen scripts | 179 |
| Vocabulary adaptation | Minixhofer et al. (WECHSEL) | 2022 | initialising new subword embeddings | 165 |
| Vocabulary adaptation | Dobler & de Melo (FOCUS) | 2023 | new tokens as combinations of overlapping ones | 107 |
| Speech units | Graves et al. (CTC) | 2006 | alignment-free training on label sequences | 7,914 |
| Speech units | Hsu et al. (HuBERT) | 2021 | clustered hidden units as prediction targets | 6,045 |
| Speech units | Baevski et al. (wav2vec 2.0) | 2020 | self-supervised speech with quantised targets | 5,919 |
| Speech units | Zeghidour et al. (SoundStream) | 2021 | neural codec with residual vector quantisation | 1,816 |
| Speech units | Défossez et al. (EnCodec) | 2023 | streaming high-fidelity neural codec | 1,793 |
| Speech units | Wang et al. (VALL-E) | 2023 | TTS as language modelling over codec tokens | 1,399 |
| Speech units | Borsos et al. (AudioLM) | 2023 | semantic plus acoustic tokens for audio generation | 1,271 |
| Speech units | Lakhotia et al. (GSLM) | 2021 | spoken language modelling over discrete units | 532 |
| Speech units | Zhou et al. (VoxCPM) | 2025 | TTS without discrete audio tokens | 80 |

### 3.1 Subword vocabularies

Byte-pair encoding began as a compression method that repeatedly replaces the most frequent pair of bytes with a new symbol (Gage, 1994). Sennrich et al. (2016) used it to give translation models an open vocabulary, and it is now the default tokenizer of most large language models. WordPiece was introduced for Japanese and Korean voice search (Schuster & Nakajima, 2012), so subword segmentation and speech were connected from the start. It reached production translation in GNMT (Wu et al., 2016). Kudo (2018) proposed a unigram language-model segmentation and trained on several sampled segmentations of each sentence. The gains were largest in low-resource and out-of-domain settings. BPE-dropout brought the same idea to BPE and improved translation by up to 2.3 BLEU (Provilkov et al., 2020). SentencePiece trains these models directly on raw sentences, with whitespace represented by the `▁` symbol (Kudo & Richardson, 2018); our character path keeps that symbol as its word boundary. Bostrom & Durrett (2020) found that unigram segmentation recovers units closer to morphology than BPE's greedy merges and matches or beats BPE downstream. Morphology-aware segmentation has its own line of work, from unsupervised Morfessor (Creutz & Lagus, 2007) to supervised segmenters for Arabic (Section 4).

All these methods learn a vocabulary from text in the languages of interest. Our problem is different: the vocabulary was fixed by someone else, without Kurmanji, and the embeddings are frozen.

### 3.2 What a vocabulary costs each language

Rust et al. (2021) introduced two simple measures: *fertility*, the average number of subwords per word, and the *proportion of continued words*, words split into at least two pieces. They found that multilingual BERT over-segments Arabic, Finnish, Korean, Russian and Turkish. Replacing its tokenizer with a monolingual one improved results for almost every task and language they tested, an effect as large as that of pre-training data size. Petrov et al. (2023) measured the same text across languages and found tokenized lengths differing up to 15-fold, with over 4-fold differences even for character- and byte-level models. Ahia et al. (2023) showed that speakers of many of 22 languages pay more for commercial models and get poorer results. Zouhar et al. (2023) proposed an information-theoretic measure of how efficiently a tokenizer uses its channel, and Ali et al. (2024) showed that the tokenizer choice matters in large-model training. Mielke et al. (2021) survey the whole space between words and characters.

These studies measure cost in length, money and downstream accuracy. In TTS, a further cost appears: the voice must learn what each piece *sounds* like. A piece seen five times teaches little about pronunciation, whatever its compression value. Section 5.2 measures this for Kurmanji.

### 3.3 Reading characters, bytes and patches

A parallel line removes the fixed vocabulary. Lee et al. (2017) translated character sequences without explicit segmentation, using convolution and pooling to shorten the input. CANINE reads characters without a vocabulary and downsamples them before a deep transformer; it beat a comparable mBERT by 2.8 F1 on TyDi QA with 28% fewer parameters (Clark et al., 2022). ByT5 showed that byte-level models are "significantly more robust to noise" and "perform better on tasks that are sensitive to spelling and pronunciation", at the cost of longer sequences (Xue et al., 2022). Charformer learns latent subwords from characters with a gradient-based block (Tay et al., 2022). MEGABYTE splits byte sequences into patches with a local and a global model (Yu et al., 2023). The Byte Latent Transformer sets patch boundaries by the entropy of the next byte and matches tokenization-based models at scale (Pagnoni et al., 2024).

Two findings from this line matter here. Character and byte models gain where spelling and pronunciation matter and where text is noisy, which describes Kurmanji TTS input well. They pay in sequence length, and Section 7.1 measures that price for our voice (+37–45% step time).

### 3.4 Teaching a frozen model new units

When a model is adapted to a language it did not see, its vocabulary can be extended, replaced or reused. WECHSEL replaces the tokenizer and initialises each new embedding from semantically similar source subwords (Minixhofer et al., 2022). FOCUS builds new token embeddings as sparse combinations of tokens shared with the old vocabulary (Dobler & de Melo, 2023). Pfeiffer et al. (2021) adapt multilingual models to unseen scripts through matrix factorisation. AraBERT kept about 4,000 unused tokens in its 64,000-entry vocabulary for later pre-training (Antoun et al., 2020); our voice uses 10 of the 976 reserved slots of its backbone in the same spirit. Textual inversion learns a new "word" in the embedding space of a frozen text-to-image model from three to five images (Gal et al., 2023). LoRA adapts frozen weights through trainable low-rank updates (Hu et al., 2022).

This literature agrees that a new embedding needs a good starting point. Our tables add a measurement from speech (Section 7.7). In a run of our size, a row that starts from nothing does not learn, while a correction on top of a trained letter does.

### 3.5 Text as input and output of speech models

End-to-end TTS has read characters since Tacotron 2, which maps character embeddings to mel spectrograms (Shen et al., 2018). Byte input and output worked across many languages for both recognition and synthesis (Li et al., 2019). For attention-based recognisers, graphemes and word-pieces consistently outperformed phonemes on 100 to 960 hours of English (Irie et al., 2019), even though English spelling is far less regular than Kurmanji's. Prosody can be controlled through learned tokens without labels, as global style tokens did (Wang et al., 2018), but explicit lexical stress marks in the input are less studied. Massively multilingual recognisers settle the output alphabet by construction. Omnilingual ASR takes the union of all characters in its training data (Omnilingual ASR team, 2025). Whisper (Radford et al., 2023) and the massively multilingual wav2vec 2.0 models (Pratap et al., 2024) are the other common starting points for Kurmanji recognition.

### 3.6 Tokens for audio

On the audio side, discrete units are now standard. CTC made alignment-free training on label sequences possible (Graves et al., 2006). wav2vec 2.0 learned speech representations against quantised targets (Baevski et al., 2020), and HuBERT predicted clustered hidden units of masked regions (Hsu et al., 2021). Neural codecs such as SoundStream (Zeghidour et al., 2021) and EnCodec (Défossez et al., 2023) quantise audio with residual vector quantisers. Generative spoken language modelling trains language models on such units without text (Lakhotia et al., 2021). AudioLM combines semantic and acoustic tokens (Borsos et al., 2023), and VALL-E treats TTS as language modelling over codec tokens, trained on 60,000 hours of English (Wang et al., 2023). VoxCPM argues that discrete tokens trade expressivity for stability, and models speech with semi-discrete residual representations planned by a text-semantic language model and rendered by local diffusion (Zhou et al., 2025).

Our voice therefore takes no tokens from an external speech codec. The one tokenizer we can change is on the text side, which is the subject of this paper.

**Gap.** None of the works above studies the text interface of a frozen multilingual TTS model for a language outside its training languages. None measures, letter by letter, what such a model learns when each symbol receives a trainable correction, and none tests stress marks on that interface against the speaker's measured prominence.

## 4 Lessons from neighbouring languages

Kurmanji's relatives and neighbours have each solved part of its problem. Three lessons transfer. Normalise the script before choosing units. Let morphology shape the units of text models when data are plentiful, but keep speech close to the letters. Make what the script hides explicit only from a source that is known to be right. This section reviews Sorani, Zazaki, Persian, Turkish and Arabic in that light and closes with a table of what Deng took from each.

### 4.1 Sorani (Central Kurdish)

Sorani is written in an Arabic-based alphabet whose mapping to Kurmanji's Latin letters is ambiguous: one Arabic-based letter stands for both *u* and *w*, another for *y* and *î*, a third for *e* and *h*. Transliteration therefore needs context (Esmaili & Salavati, 2013). Its grammar also differs in ways that matter for segmentation. Sorani has largely given up the case system that Kurmanji keeps, expresses past-tense agents with pronominal enclitics instead of oblique pronouns, and has a definite suffix *-aka* that Kurmanji lacks (Esmaili & Salavati, 2013).

Kurdish text processing has taken script and dialect diversity as its central problem. The Kurdish Language Processing Toolkit provides preprocessing, stemming, tokenization, lemmatisation and transliteration (Ahmadi, 2020b). A tokenizer for both Sorani and Kurmanji, built on a lexicon and a morphological analyser, outperformed unsupervised methods on an annotated set. It addressed what its author identified as the two obstacles: morphological complexity and the lack of a unified orthography (Ahmadi, 2020a). The AsoSoft corpus of 188 million Sorani tokens was normalised before release (Veisi et al., 2020). Speech work followed the same order: a Central Kurdish recogniser with its own speech corpus and pronunciation lexicon (Veisi et al., 2022), a rule-based grapheme-to-phoneme converter built on Optimality Theory (Mahmudi & Veisi, 2021), and end-to-end TTS (Ahmad & Rashid, 2024).

**What transfers.** Normalisation is a first-class step, not a cleaning afterthought; Deng's path normalises Unicode, keyboard letters and punctuation before anything else (Section 5.3). Kurmanji in Arabic script needs a transliterator before our path can read it, and the ambiguous letters mean that transliteration must use context. Sorani also shows that even a script that writes its vowels needed a pronunciation layer for speech. Kurmanji's own hidden layer is narrower but real: stress, aspiration and the trill (Section 2.2).

### 4.2 Zazaki and Gorani

Zazaki is a separate Iranian language whose speakers live alongside Kurmanji speakers. Its written resources are small: a news corpus gathered for the Zaza–Gorani family holds over 1.6 million Zazaki and 194,000 Gorani word tokens (Ahmadi, 2020c). Zazaki is written in a Latin alphabet close to Kurmanji's, so letter-level units do not separate the two. Our data pipeline therefore scores every audio window for language, with a separate Zazaki probability, before it can enter Kurmanji training. One mixed-language channel still let through 69 windows that may be Zazaki, an open data-quality item.

**What transfers.** For a tokenizer shared by close languages, the language label belongs to the segment, not to the channel or the file, and a neighbour language never enters Kurmanji data unlabelled.

### 4.3 Persian

Persian is written in an Arabic-based script that usually leaves the ezafe, the linker between a noun and its modifiers, unwritten. Recognising it is a task of its own, on which transformer models reached the best results (Doostmohammadi et al., 2020). Persian grapheme-to-phoneme conversion must detect the ezafe, disambiguate homographs and handle unseen words (Rahmati & Sameti, 2024). On the text side, ParsBERT trained a 100,000-entry WordPiece vocabulary on normalised Persian text and outperformed multilingual BERT on every task it tested (Farahani et al., 2021).

**What transfers.** What the script hides must be predicted from context or supplied by a lexicon. Kurmanji writes its izafe (*-ê*, *-a*, *-ên*) and its vowels, so its hidden information is limited to stress, aspiration and the trill. The Persian experience also shows that context models can recover such information well when the training text is large. Our voice has 33.5 hours of one reader, which is not large.

### 4.4 Turkish

Turkish is agglutinative and written in a transparent Latin alphabet. It is also the source of the keyboard that most Kurmanji in Turkey is typed on (Section 2.7). Multilingual BERT over-segments it (Rust et al., 2021). BERTurk trained Turkish-specific vocabularies of 32,000 and 128,000 entries on 35 GB of text (Schweter, 2020). The most controlled comparison pre-trained the same model with five tokenizers (Toraman et al., 2023). A morphology-level tokenizer came within 0.01–0.02 F1 of BPE and WordPiece on most tasks, larger vocabularies helped morphological and word-level tokenizers more than the standard ones, and the byte-level tokenizer performed worst for Turkish in most tasks.

**What transfers.** For a text language model of a morphologically rich language, a language-specific subword vocabulary is the main gain, and morphology-aware units are competitive. For speech, the balance shifts. Characters are what a voice pronounces, byte and character models are stronger on spelling- and pronunciation-sensitive tasks (Xue et al., 2022), and our voice could not relearn thousands of foreign pieces from 33 hours (Section 5.2). Deng therefore uses characters for the voice. A morphology-aware vocabulary remains an option for a future Kurmanji text model.

### 4.5 Arabic

Arabic is the best-studied case of morphology-aware tokenization. AraBERT first splits words into stems, prefixes and suffixes with the Farasa segmenter (Abdelali et al., 2016), so that a word with and without its article no longer needs two vocabulary entries. It then trains a unigram SentencePiece vocabulary of about 60,000 units. The final vocabulary of 64,000 entries keeps about 4,000 unused tokens for later pre-training (Antoun et al., 2020). A comparison of tokenizers for Arabic text classification found no single best choice: the answer depended on the dataset size, the task and how much morphology the data contained (Alyafeai et al., 2023).

For speech, Arabic script leaves short vowels unwritten unless diacritics are added. TTS models trained on diacritised text are generally better, but with 1,000 and 4,000 hours instead of 100, larger data compensate for missing diacritics to a significant degree (Musleh et al., 2026).

**What transfers.** Explicit marking of hidden information pays most when data are small, and our data are small. The Arabic case also assumes that the diacritics are correct. Our stress experiment shows what happens when they are not: marks that matched the speaker's most prominent vowel in only 58% of two-syllable words (chance 50%) taught nothing (Section 7.6). Reserving unused vocabulary slots, as AraBERT did, is what made our installation possible without touching the checkpoint (Section 5.4).

### 4.6 Kurmanji speech recognition

Few Kurmanji recognisers are documented. Fine-tuning Whisper on about 68 hours of validated Northern Kurdish speech reached a word error rate of 10.5% and a character error rate of 5.7% on a specialised test set (Abdullah et al., 2024). A dependency treebank exists for Kurmanji text (Gökırmak & Tyers, 2017). Our ear's numbers in Section 7.9 come from different test sets and cannot be compared with those figures directly.

### 4.7 What Deng took from each

| Language | What was done there | What it showed | What Deng took |
| --- | --- | --- | --- |
| Sorani | normalisation, transliteration, lexicon-based tokenization, G2P | script and dialect diversity is the core problem | normalisation first; transliteration left as future work |
| Zazaki | small corpora in a similar Latin script | letters do not separate close languages | language label per segment, never per channel |
| Persian | ezafe recognition, G2P with ezafe detection | hidden morphology must be predicted or listed | Kurmanji writes izafe; hidden layer limited to stress, aspiration, trill |
| Turkish | language-specific and morphology-level vocabularies | morphology-aware units compete for text models; bytes lose | characters for speech; morphology for a future text model |
| Arabic | morphological pre-segmentation, reserved tokens, diacritised TTS input | marking hidden vowels helps most when data are small | reserved slots for new symbols; marks only from a trusted source |

## 5 The Deng text paths

Deng uses two different text interfaces. The voice reads a sequence of 41 character-level symbols that we install on top of a frozen multilingual text-to-speech (TTS) model. The ear writes characters from a 9,812-symbol inventory that its base model already had. This section describes both in full, in the order a sentence travels through them.

### 5.1 Two models, two interfaces

The **voice** is VoxCPM2, a 2-billion-parameter, Apache-2.0 TTS model built on the MiniCPM-4 language model ([model card](https://huggingface.co/openbmb/VoxCPM2)). Its authors call it "tokenizer-free" because it does not depend on a pre-trained speech tokenizer: a text-semantic language model, a residual acoustic model and a local diffusion decoder are trained end-to-end, with a differentiable quantisation bottleneck instead of a discrete codec (Zhou et al., 2025). The text side is not tokenizer-free: text enters through the backbone's byte-pair-encoding (BPE) vocabulary. The model card lists 30 supported languages; Kurdish is not among them. The language model runs at 6.25 steps per second, so one step carries 0.16 s of audio. We adapt the model with LoRA (Hu et al., 2022): rank 32, alpha 32, no dropout, on the query, key, value and output projections of both the language model and the diffusion transformer.

The **ear** is the LLM-ASR variant of Omnilingual ASR with a 1B-parameter encoder (`omniASR_LLM_1B_v2`, about 2.3 billion parameters with its decoder): a wav2vec 2.0 encoder followed by a language-model decoder (Omnilingual ASR team, 2025). It was chosen on 14 October 2026 after seven off-the-shelf recognisers were scored on the same two Kurmanji read-speech sets (Section 6.4). Its output units are characters. The paper builds "a character-based tokenizer by taking the union of all characters across the entire ASR dataset", cleaned of punctuation and of characters seen fewer than five times, giving 9,812 symbols. Our training logs show the same number (`target_vocab_size: 9812`); the model's full vocabulary has 10,288 entries.

*[Figure 3 — diagram, drawn in the online document: the voice's six-step text path with its load-time guard, and the ear's five steps.]*

**Figure 3.** The voice reads Kurmanji through a new character path installed on its frozen embeddings; the ear keeps its base model's character outputs, and only its training labels and scoring changed.

### 5.2 What the stock BPE does to Kurmanji

We measured the voice's stock tokenizer on 8,000 transcribed segments of Kurmanji television speech before changing anything (31 October 2026). The vocabulary has 73,440 pieces. Kurmanji text used 3,334 distinct pieces, and 1,629 of them occurred at most five times. Words are cut where no morpheme boundary exists: *hatin* 'to come / they came' becomes `▁h|atin`, and *dixwazim* 'I want' becomes `▁d|ix|w|az|im`, which splits the single sound /xʷ/. The letter *w* appeared inside 537 different pieces and *c* inside 2,253. The digraph *xw* never appeared as one piece.

Under LoRA the embedding table stays frozen. Every one of those 3,334 pieces therefore keeps an embedding learned for other languages, and the adapters must learn, piece by piece, what each one sounds like in Kurmanji. Almost half of them occurred five times or fewer in those 8,000 segments. The character path replaces them with 35 symbols that the backbone already knows as single characters. The price is length: the same segments need 215.3 character tokens per sentence instead of 94.2 BPE pieces, 2.29 times as many.

### 5.3 The character path

The path is implemented in `metin/kurmanci/kmr_token.py` (538 lines). It turns prepared text into a list of symbol names and then into token ids. Numbers, times and dates are spelled out as Kurmanji words by the text preparer before this step.

| Rows | Symbols | Note |
| --- | --- | --- |
| 31 | a b c ç d e ê f g h i î j k l m n o p q r s ş t u û v w x y z | the Kurmanji Latin alphabet; each letter is always the same token |
| 1 | `xw` as one token | slot `<reserved_901>`; used by formats s31, s31-stress, s32 and v2 |
| 1 | stress sign `ˈ` | slot `<reserved_900>`; used only by format s31-stress |
| 1 | `▁` word boundary | the backbone's own space piece |
| 7 | `. , ? ! : ; -` | punctuation that changes how a sentence is read |
| 8 (v4 only) | stressed a e ê i î o u û | slots `<reserved_910>`–`<reserved_917>`; no rows of their own (Section 5.6) |

Every saved table has exactly 41 rows, and a row is found by its position, so the order of the alphabet is fixed by a test. New symbols may only be added at the end, with a new table size.

A sentence passes through ten steps. Steps 7 to 10 depend on the format version (Section 5.5).

1. **Unicode NFC.** Decomposed and composed forms of ê, î, û, ç, ş become the same code point.
2. **Acronyms** (v2 and later). A capitalised name of two to five letters without a vowel is written with the Kurmanji letter names, as a reader says it: *TV* → *teve*, *TV'yê* → *teveyê*, *SMSê* → *semesê*. Names with a vowel (*UNESCO*) are read as words; Roman numerals are left alone. On the 7,586 training segments the rule changed 209 texts; the text moved closer to what our ear heard in the recording in 199 and further away in 6, where the reader skipped the name.
3. **Typographic folding.** Curly and angle quotes, apostrophes and brackets are removed; dashes become `-`; `…` becomes `...`; Arabic `؟ ، ؛` become `? , ;`; soft hyphens and zero-width characters disappear.
4. **Kurmanji lower case.** `İ`, `I` and `ı` all become `i`; plain `str.lower()` would turn `İ` into two code points.
5. **Foreign letters.** Letters from Turkish keyboards and other orthographies are mapped to the Kurmanji letter they are read as (ü→û, é→ê, ö→o, ğ→g, ẍ→x, ḧ→h, ł→l). Any other letter with a diacritic is reduced to its base letter (ř→r).
6. **Unknown characters break the word.** A character the path cannot say (a slash, a digit the preparer missed, another script) becomes a word boundary and is counted in a `dropped` counter that every run prints. An earlier version glued the two sides together (`kesekê/kesekî` → `kesekêkesekî`); this happened in 7 of 7,586 training texts.
7. **Question head** (s32 and later). A question also opens with `?`, so the voice knows from its first sound that a question is coming, not only from one token at the far end. Format s32 puts `?` directly before the first letter; v2 and later make it a word of its own (`? ▁`). End marks that stand together (`...?`, `?!`) close one sentence.
8. **Lead boundary** (v2 and later). Every text opens with `▁`, so the first word starts like every other word.
9. **xw** (v3 and later). The digraph is written as its two letters, `x` `w`.
10. **Stress marks** (v4 only). A stressed vowel is replaced by its marked token at the same position (Section 5.6).

The output for one sentence in the current standard format (v3) is:

```text
Tu kengî hatî? Min li TV'yê dît.
▁ ? ▁ t u ▁ k e n g î ▁ h a t î ? ▁ m i n ▁ l i ▁ t e v e y ê ▁ d î t .
```

### 5.4 Installing the path without touching the checkpoint

The path adds to the model and changes none of its weights or vocabulary entries. Its symbols map to tokens the backbone already has: the 31 letters, `▁` and punctuation exist as single-character pieces, and the new symbols live in reserved slots that the backbone never trained. VoxCPM2's tokenizer has 976 such unused `<reserved_N>` tokens. Their embeddings are almost zero (norm 0.0002, against a mean letter norm of 1.93).

On top of the frozen embedding matrix E we add a trainable residual table Δ with one row per symbol (41 × 2,048). A forward hook on the embedding layer adds Δ to the output, so the same correction applies during training and at reading time:

```latex
\mathbf{e}(t) = \mathbf{E}[t] + \boldsymbol{\Delta}[r(t)], \qquad r(t) \in \{1,\dots,41\}
```

Three implementation choices matter.

- **Saving by name.** The table's parameter name contains `lora_`, so VoxCPM's own checkpoint code saves it with the LoRA weights and its loader restores it by name. Nothing new is needed to ship a voice.
- **Initial values.** Rows start at zero, so on the first step every letter reads exactly as the backbone would read it. Two rows are exceptions because their slots were never trained: `xw` starts at the mean of the embeddings of x and w (one sound built from the two), and the stress sign starts as a fixed random direction one tenth of a letter's length. Format s31-stress had started it at a full letter's length; Section 7.6 shows why that was changed.
- **No silent fallback.** The replacement tokenizer deliberately has no attribute forwarding to the original BPE tokenizer. A caller that asks for `encode` or `tokenize` gets the character path or an error, never BPE pieces that would run without complaint.

### 5.5 Format versions, fingerprints and fail-loud loading

Trained weights read correctly only with the token sequence they were trained on, and nothing fails when the two differ. The 12 November audit found that no file recorded which options a voice had been trained with; reading S32 b without its question head would have produced a worse voice and no error. Since then every way of writing the sequence has a name, and names with trained weights are frozen.

| Format | Date | Options | Trained by | Status |
| --- | --- | --- | --- | --- |
| v4 | 14 Nov 2026 | v3 + stressed-vowel tokens, half of the rule marks kept | S34 b | frozen; not the standard (no stress control, Section 7.6) |
| v3 | 13 Nov 2026 | v2 + `xw` written as two letters | S34, S34 a | frozen; **standard for voice training** |
| v2 | 12 Nov 2026 | question head as a word, lead `▁`, acronyms spelled | never | replaced by v3 before S34 |
| s32 | 1 Nov 2026 | `?` directly before a question's first letter | S32 b | frozen |
| s31-stress | 31 Oct 2026 | rule-based stress sign before the stressed vowel | S31 b | frozen; stress sign removed afterwards |
| s31 | 31 Oct 2026 | letters, `xw` unit, space, punctuation | S31 a, S32 a | frozen |

A training run writes the format next to its weights in `text_path.json`. The file for the current standard voice reads:

```json
{"format": "v3", "options": {"qhead": "word", "lead": true, "acronyms": true, "xw": "letters"}, "rows": 41}
```

A reading run takes the format from that file. Loading fails, rather than warns, when the file is missing and no format is named explicitly; when it names a format the code does not have; when the stored options or row count differ from the code's; or, for v4, when the marks table has a different layout or gain. After loading, `table_check()` measures how far each row has moved from its initial value and stops the reading if fewer than 15 of the 41 rows have moved. This catches the case the 12 November audit found in VoxCPM's loader: a key the loader does not find is skipped without a message, so an unfilled table would read with untrained letters.

Each frozen format is also locked by a fingerprint: a hash of its token sequences over the 7,586 training texts and the 267 test sentences, checked by the test suite. The v3 training fingerprint is `e979ce904540dd71` and the v4 one `50449359213f7105`. The S34 a/b training job refused to start unless both fingerprints and the SHA-256 of its starting weights matched the copies on the coordinating machine.

### 5.6 Stress: rules, marks and policies

Kurmanji spelling does not mark stress, and stress distinguishes words: *hatin* is stressed on the last syllable as an infinitive ('to come') and on the first as a past form ('they came'). `metin/kurmanci/vurgu.py` assigns stress from two reference grammars, with each rule naming its source page. It treats prepositions, postpositions, linkers and weak pronouns as clitics without stress of their own; parses verb forms (negation, preverb, mood prefixes *di-* and *bi-*, stem, personal ending) with a lexicon-backed verb analyser; keeps nominal stress on the stem before the inflectional endings *-ê*, *-a*, *-ek*, *-ekî*; and moves it onto plural *-an* and *-ên*. A bare *-in* form is read as a past verb when it closes a clause, and as an infinitive after a passive or causative auxiliary or a preposition. The two grammars are Tan (2011) and Karabax (2013). Before any voice training, the rules were tested on 39,182 words of speech from three sources: the training audiobook, crowd-sourced read sentences and a small corpus of natural narratives (Section 7.6). Two book rules were refuted and changed: the mood prefix *di-* does not take the stress, and *-ekî* leaves it on the stem. The rules now reproduce 125 of the grammars' 130 worked examples; four of the five misses are deliberate, words where the recordings contradicted the books.

Format s31-stress wrote the stress as a separate sign token before the stressed vowel. Format v4 instead puts stress on the letter it belongs to. A stressed vowel is a token of its own (a reserved slot), and its embedding is built from parts that are already trained:

```latex
\mathbf{e}(\acute{v}) = \mathbf{E}[v] + \boldsymbol{\Delta}[r(v)] + g\,\mathbf{M}_{\text{stress}}, \qquad g = 4
```

Here v is the unmarked vowel and M is an eight-row marks table, of which only the first row is used. The marked vowel shares its letter's row, so marking does not split what ê has learned into two, and the sequence keeps its length. The stress row starts at zero, so a marked text reads exactly like an unmarked one on the first step, and an unmarked v3 voice loads into v4 unchanged; we checked bit-for-bit equality in half precision on the real tables. The gain g = 4 gives the new row four times the effective learning step without touching the optimizer. That value is a design choice, not a measurement.

The sentence *Ew duh hatin, lê hatin ne hêsan bû* ('They came yesterday, but coming was not easy') shows the rule telling the two *hatin* apart. With every rule mark shown, v4 writes it as:

```text
▁ e w ▁ d ˈu h ▁ h ˈa t i n , ▁ l ê ▁ h a t ˈi n ▁ n e ▁ h ê s ˈa n ▁ b ˈû .
```

Training texts keep half of the rule's marks, chosen per word by a keyed hash of the text, so every machine and every run sees the same marks. The voice should learn that a mark means stress and still read unmarked words. At reading time a policy decides which marks a text gets: `all`, `none`, or `train`, the training share. A stress sign typed by the writer (*hˈatin*, *hatˈin*) always wins over the rule for that word.

### 5.7 Sounds the spelling hides

The alphabet writes one letter for several contrasts. Aspirated and plain ç, k, p, t are phonemic; tap and trill r are phonemic, and the trill is written `rr` only where the writer chooses to; pharyngeal ḧ and ʿ and the Arabic-loan ẍ are not phonemic and are usually not written. The marks table leaves seven empty rows and reserved slots from 920 upward for these contrasts. None of them is used yet, because a mark can only be trained when a lexicon says which word has which sound. A first lexicon was measured from the training reader's own voice (Section 7.8); it gives 50 measured entries for k and p and none for t and ç.

### 5.8 Reading-time safeguards

VoxCPM stops a reading and retries when it has produced more than 6.0 audio steps per text token, a threshold set for BPE pieces. The character path gives 2.29 times as many tokens for the same text, so the same safety net sits at 6.0 / 2.29 ≈ 2.6. Measured speech on the character path takes 0.46 steps per token (0.073 s), 0.9 at the 95th percentile and at most 1.0 on the shortest sentences. Our own length guard protects the evaluation readings; the production value 2.6 is recorded in the code.

### 5.9 The ear's units

The ear keeps the base model's character inventory. No character in any training label of the K5, U5 or U8 runs was unknown to it, and the inventory also contains ˈ, ʰ, · and ẍ. We changed the labels, not the units:

- **The base model's convention.** Training labels follow the base model's own text normaliser for Kurmanji: lower case, no punctuation, digits kept as written, apostrophes and dashes removed. The first runs kept capitals and punctuation; Section 7.9 shows what that cost.
- **Standard spelling.** Inside a word, *îy* before a vowel is written *iy* (*sûrîyê* → *sûriyê*), the standard spelling the project targets.
- **Two scores.** The official word error rate uses frozen references and one simple normaliser. A second score, "999 single spelling v2", passes both reference and hypothesis through `kanonik_v2()`. It merges spelling variants the grammars treat as one word, Turkish-keyboard letters, and rare circumflex spellings of words longer than three letters. It never changes a circumflex in a word's last two letters, because those carry case and linker endings (*hatinê* ≠ *hatine*).

The ear's alphabet already matched Kurmanji, so there was nothing to gain from a new inventory. Its measured errors are in vowels and word boundaries, which need context rather than new symbols (Section 7.9).

## 6 Experimental setup

Every voice comparison in this paper changes one thing at a time on the same data, and every decision rule was written down before the result was read. This section gives the data, the training recipe, the runs, the evaluation measures and the statistics.

### 6.1 Data

**Voice.** All voices are trained on one permissioned audiobook read by a single professional reader. Book text and audio were matched at the text level, so each segment carries the printed sentence it contains. A fixed selection rule keeps 7,586 of 19,440 segments (33.52 h from 34 files): segments of 2–20 s that end a sentence, contain no digits, match a recogniser's transcript within a character error rate of 8%, and share no sentence with any test set. The same rule produces the same list in every run. The text is long, formal prose with 1.45 million letters. Only 73 segments (19.9 min) end with a question mark. Because every voice trained on it imitates one person's voice, the voices stay inside the project and are not published.

**Ear.** The ear's human-transcribed training data are the Kurmanji portions of Common Voice (Ardila et al., 2020) and FLEURS (Conneau et al., 2023), 61.5 h in total. Later runs add public-domain broadcast news and open-licensed television speech, labelled by our own recognisers and kept only where two recognisers disagree on at most 10% of the words. The production ear, U3, has seen about 78 h of audio.

### 6.2 Voice training recipe

All voices share one recipe: VoxCPM2 with LoRA of rank 32 on the language model and the diffusion transformer, learning rate 10⁻⁴, 100 warm-up steps, cosine decay and seed 11, trained on free 16 GB T4 GPUs with four segments per GPU per step. Table 2 lists the runs. The text path is the only difference within each comparison pair.

**Table 2.** Voice runs. Epochs are passes over the 7,586 segments.

| Run | Text format | Starts from | GPUs | Steps | Epochs | Change tested |
| --- | --- | --- | --- | --- | --- | --- |
| S28 | stock BPE | base model | 1 | 1,500 | 0.79 | baseline voice |
| S31 a | s31 | base model | 1 | 1,500 | 0.79 | character path vs S28 |
| S31 b | s31-stress | base model | 1 | 1,500 | 0.79 | + stress sign token |
| S32 a | s31 | S31 a | 1 | 800 | +0.42 | questions repeated to ~20% of the list |
| S32 b | s32 | S31 a | 1 | 800 | +0.42 | + question head |
| S33 | stock BPE | base model | 2 | 1,960 | 2.06 | S28 recipe, longer |
| S34 | v3 | base model | 2 | 1,680 | 1.77 | character path vs S33 |
| S34 a | v3 | S34 | 1 | 1,722 | +0.91 | control arm |
| S34 b | v4 | S34 | 1 | 1,722 | +0.91 | + stress marks on vowels |

Three comparisons carry the paper. S31 a against S28 and S34 against S33 test the character path against the stock BPE path at equal training; S34 had slightly less training than S33 (1.77 against 2.06 epochs). S34 b against S34 a tests stress marks from the same starting weights. S32 b was also read once with a leading `▁` that it had never seen in training ("S32 b + lead"), to test whether the lead boundary helps without training.

### 6.3 Evaluation

**Test sentences.** The prosody test set has 257 sentences in 14 categories: statement–question pairs, wh-questions, *gelo*/*ma* questions, negation, imperatives, vocatives and exclamations, focus, long sentences and lists, numbers and dates, names and loanwords, emotion, dialogue, difficult sounds, and words whose meaning changes with stress. 65 of them are questions. Most are crowd-sourced sentences released under CC0. The set is locked by code and never enters training. Ten "progress" sentences outside the book's style, locked on 28 October 2026, test generalisation. Each voice reads every sentence once in each of three seed sets, so S34 produced 810 clips.

**Intelligibility.** Our production ear (U3) transcribes every clip, and the letter error rate (character error rate, CER) is computed against the input text. This makes the ear the judge. Its own errors therefore enter every number: on recordings of the human reader it writes ê as e 1,005 times in 4,000 segments. Its output also differs from the reference in ways that are not reading errors: digits for spelled numbers, spaces and circumflexes. Removing those three artefacts lowers S32 b from 3.14 to 2.23 and S28 from 4.84 to 3.39 without changing the ranking. We report the uncorrected numbers throughout. The letter error rate is broken down by the position of the word in the sentence (first, middle, last) and by letter. For each letter we report the share of its occurrences that the ear did not write as that letter, next to the same share on recordings of the human reader.

**Question prosody.** A prosody judge scores each clip from the last second of its pitch contour, in semitones relative to the speaker's median. It uses two features, the mean pitch of the last 150 ms and the highest pitch of the last 600 ms, in a logistic regression trained on 144 statements and 286 yes/no questions read by Common Voice speakers. On speakers held out from training it labels 89% of statements as statements and 69% of questions as questions. The 69% is close to a human ceiling, because about a third of the crowd-sourced readers read questions with falling, statement-like pitch. We report three numbers: the *question share* (questions judged question-like), the *statement share*, and a threshold-free *separation*, the probability that a random question scores higher than a random statement (the area under the ROC curve).

**Stress contrast.** For the stress experiments, forced alignment (the MMS aligner in torchaudio) locates each vowel, and Praat measures four cues of prominence: duration, pitch, intensity and the share of energy above 500 Hz. Each cue is z-scored against vowels of the same quality, and their mean P is the vowel's prominence. The test uses 13 verbs whose infinitive and past forms are spelled alike, each in two sentence frames (26 sentences), with the verb last. For a voice reading the verb with a typed mark on its first or on its last syllable, the contrast is

```latex
C = \left(P_{\text{last}} - P_{\text{first}} \mid \text{mark last}\right) - \left(P_{\text{last}} - P_{\text{first}} \mid \text{mark first}\right)
```

computed on the same voice, sentence and seed. C > 0 means the mark moves the stress. The same tool applied to unmarked readings of infinitive and past frames gives D, the contrast a voice makes on its own from context.

**Statistics.** Differences between voices are paired by sentence. When a voice has three readings, its readings are averaged per sentence first. Intervals are 95% percentile intervals from 5,000 bootstrap resamples of sentences. Two voices' question shares, each averaged over three readings, are treated as indistinguishable when they differ by less than 11.9 points, the band measured for that difference.

**Human listening.** In a blind test, listeners heard 30 sentences in each of five conditions: a human recording and four voices (S28, S34, S34 a, S34 b). They marked each of the 150 clips as human or machine and rated its naturalness from 1 to 5. The pre-registration says that with fewer than five listeners the result shows a direction and decides nothing. Three listeners have completed it.

**Pre-registration.** Each run had a written plan with its decision rules and thresholds before training started (`olcumler/*.md`). Thresholds were never relaxed after a result. Where a result fell outside every case the plan foresaw, we say so in Section 7.

### 6.4 Ear experiments

The ear's base model was chosen by scoring seven off-the-shelf recognisers on 499 FLEURS and 500 Common Voice sentences (the "999" set): the CTC and LLM variants of Omnilingual ASR at several sizes, a massively multilingual wav2vec 2.0 model (Pratap et al., 2024) and a Kurdish fine-tune of Whisper (Radford et al., 2023). The LLM 1B variant won: word error rate (WER) 31.4 and CER 9.1 on FLEURS, WER 16.4 and CER 4.1 on Common Voice. The 3B variant, twice as large, was only slightly better on FLEURS (WER 30.8). The massively multilingual wav2vec 2.0 model scored WER 43.0 on FLEURS. The Whisper fine-tune reached WER 3.4 on Common Voice but 38.4 on FLEURS, a gap consistent with having seen Common Voice in training; its licence is also unstated, so it served only as a reference.

Ear training updates the speech encoder and keeps the language-model decoder frozen. Three experiments bear on output units and text conventions: K5, which changed the label convention; U1 and U2, which changed one spelling habit in the labels; and K13/K14, which re-ranked beam candidates with an n-gram model of written Kurmanji. Ears are scored on the 999 set, on 153 segments of broadcast news, on 214 segments of a permissioned conversational podcast, and on 150 segments of everyday conversation whose references were still machine drafts.

## 7 Results

At equal training, reading Kurmanji letter by letter made the voice clearer than reading BPE pieces: letter error fell from 3.62 to 2.61, and to 1.72–2.04 after one more epoch. The same change did not bring back question intonation, and stress marks reached the model without moving the stress. All numbers below were read from the result files of the runs (`olcumler/metin-yolu/konum.json`, `harf.json`, `vurgu_c.json`, `kaggle/*/cikti/result.json`).

### 7.1 Letters against pieces

The character path won both equal-training comparisons. With 0.79 epochs each, S31 a read the test set at 3.40 letter errors per 100 letters against S28's 4.84. It also read the out-of-style progress sentences better (8.73 against 14.37). With about two epochs, S34 read at 2.61 against S33's 3.62. The sentence-paired difference was −1.01 [−1.51, −0.53], although S34 had seen 14% less audio. Longer training alone had already helped the stock path, by −1.14 [−1.54, −0.76] from S28 to S33. The character path added a further gain of the same size on top. Against S28, S34 was better by −2.15 [−2.72, −1.58]. One more epoch from S34's weights brought S34 a to 2.04 (−0.57 [−0.89, −0.26]), and the v4 arm read at 1.72 without marks. These two are the clearest voices the project has trained.

*[Figure 1 — chart in the online document: letter error against epochs; stock BPE S28 4.76 → S33 3.62; character path S31 a 3.40 → S34 2.61 → S34 a 2.04; v4 arm read without marks S34 b 1.72. Source: olcumler/metin-yolu/konum.json, means of three readings (S31 a: one reading).]*

**Figure 1.** Both paths improve with training, but at every amount of training the character path reads more clearly; S33 and S34 are the equal-training pair.

Training loss did not predict any of this. S34 ended at 0.828 and S33 at 0.822, and the two S34 continuation arms ended within 0.0001 of each other. The loss measures how well the model predicts audio latents. Intelligibility had to be measured separately, by listening machines and people.

The progress sentences gave no sign of over-fitting to the book. S34 read them at 7.89 against S33's 7.13, far from the pre-registered alarm level of 12.13.

The gain has a compute price. Longer text sequences made each training step slower: 13.29 s for S31 a against 9.69 s for S28 on one GPU (+37%), and 14.82 s for S34 against 10.2 s for S33 on two GPUs (+45%). Peak GPU memory rose from 10.2 GB (S28) to 12.4–13.0 GB (S31 a) and 13.1 GB (S34), still inside a free 16 GB T4.

### 7.2 Where the gain lies

**By position.** The gain sits in the middle and at the end of the sentence. Averaged over three readings, the last word's error fell from 5.17 (S28) and 4.31 (S33) to 2.47 (S34). Middle words fell from 3.78 and 2.68 to 2.19. The first word was the exception, treated in Section 7.4.

*[Figure 2 — chart in the online document: letter error (%) by word position for S33 / S34 / S34 a — first word of statements 8.45 / 3.21 / 2.15; first word of questions 5.01 / 10.75 / 5.74; middle words 2.68 / 2.19 / 1.77; last word 4.31 / 2.47 / 2.59. Source: konum.json, means of three readings.]*

**Figure 2.** Error by the word's place in the sentence. The character path lowered errors in middle and last words; its trained lead boundary fixed first words of statements, while first words of questions recovered only after one more epoch.

**By letter.** The gain is largest for exactly the letters whose Kurmanji value differs from their value in the languages the backbone knows (Table 3). The stock path read *c* as ç or k (11 times each), the Kurmanji /dʒ/ being read with foreign values. It read *x* as s, z or k, as if it were "ks", and *q* as k. On the character path these errors approached the level the ear itself shows on the human reader. *q* came close to that level for the first time (3.5% against 2.4%). No letter got clearly worse; the largest increase was *d*, +0.8 points.

**Table 3.** Share (%) of each letter's occurrences in the test readings that the ear did not write as that letter, three readings per voice. The reader column applies the same count to 4,000 segments of the human reader; segment boundaries there are approximate, so its levels are inflated and show the ear's own confusions rather than a floor.

| Letter | Count | S28 (BPE) | S33 (BPE) | S32 b (char.) | S34 (char. v3) | Human reader |
| --- | --- | --- | --- | --- | --- | --- |
| c | 99 | 29.3 | 32.3 | 7.1 | **5.1** | 4.6 |
| x | 108 | 34.3 | 23.1 | 9.3 | **3.7** | 2.5 |
| j | 321 | 12.8 | 11.2 | 2.5 | **1.6** | 2.7 |
| q | 141 | 14.9 | 10.6 | 9.2 | **3.5** | 2.4 |
| g | 234 | 4.7 | 3.0 | 0.9 | **0.4** | 2.7 |
| w | 336 | 6.8 | 2.7 | 0.6 | **0.6** | 2.5 |
| e | 2,721 | 5.1 | 3.9 | 2.1 | **1.6** | 4.6 |
| i | 2,256 | 7.1 | 4.9 | 3.1 | **2.5** | 5.1 |
| ê | 1,140 | 9.2 | 6.1 | 6.4 | **5.5** | 6.1 |
| u | 270 | 6.7 | 8.9 | 6.3 | 7.0 | 15.2 |
| xw | 222 | 6.3 | 2.3 | 7.2 | **0.5** | 5.2 |

Two letters did not improve because the errors are the ear's, not the voice's. The ear writes ê as e 1,005 times on the human reader, and u is its weakest letter on human speech (15%, mostly written as i or û). These are targets for the ear (Section 9).

### 7.3 Question intonation

The character path lost question intonation in its first two versions and recovered most of it at equal training (Table 4).

**Table 4.** Prosody judge results, three readings unless marked. Question share: questions judged question-like. Statement share: statements judged statement-like. Separation: the probability that a question scores above a statement.

| Voice | Text path | Question share (%) | Statement share (%) | Separation |
| --- | --- | --- | --- | --- |
| S28 | stock BPE | 47.4 | 84.3 | 0.708 |
| S33 | stock BPE | 48.1 | 80.7 | 0.680 |
| S31 a (one reading) | character | 31.2 | 83.4 | 0.612 |
| S32 b | character + question head | 34.0 | 86.0 | 0.630 |
| S34 | character v3 | 38.9 | 87.0 | 0.683 |
| S34 b, unmarked | character v4 | 38.9 | 85.3 | 0.657 |

S31 a's loss was a real loss of discrimination: separation fell from 0.70 to 0.61. Repeating the book's 73 question segments 26 times, so that they made up about a fifth of the training list (S32 a), did not help (27.4%). Adding the question head (S32 b) helped clarity but not intonation (34.0% over three readings).

At equal training the picture changed. S34 separates questions from statements as well as S33 does (0.683 against 0.680). Its lower question share is a shift of the decision point, not a loss of information. It calls 20.8% of all test sentences questions, against S33's 28.2%, so it scores more statements correctly (87.0% against 80.7%). The means of the two shares are close (62.9 against 64.4). Under the pre-registered rule, S34's question share of 38.9% stayed inside the band (threshold 36.2%), and the character path became the standard. The three readings of S34 ranged from 32.3% to 45.2%, so one reading alone would have fallen below the threshold.

The shortfall appears in every question type (S33 against S34): questions marked only by intonation 51.5 against 37.5, wh-questions 51.7 against 41.2, and questions with *ma* or *gelo* 42.3 against 36.6. The intonation-only type has only 10–11 sentences in the set. The question-mark row of the table learned no consistent direction across runs (cosine −0.03 between S34 and S31 a). The training text has one question in a hundred segments, and earlier crowd-sourced question recordings raised the question share by 5.6 points but worsened letter error by 4.35 points through microphone and speaker mismatch (S29). We read this as a data problem that the text path cannot solve.

### 7.4 The first word

On the early character path the first word was where the error stayed. In S31 a every word except the first followed a `▁`, and the first followed nothing. First-word error did not fall (S28 8.0%, S31 a 9.8%). For first words of one or two letters, such as *tu*, *ez* and *ma*, it more than doubled (8.3% to 19.0%). The ear also heard an extra sound before the first word in 21 sentences of S31 a, against 6 for S28.

Two fixes were tested. The question head of S32 b gives the first word of a question something to follow. With the same starting weights and data, questions' first-word error fell from 11.0% (S32 a) to 4.0% (S32 b), a difference of −7.0 [−12.3, −2.5]. Statements did not change. A lead `▁` added at reading time to a voice never trained with it (S32 b + lead) did not help statements significantly (−1.60 [−4.07, +0.49]) and hurt questions (+4.27 [+0.64, +8.51]).

Trained from the start (S34, format v3), the lead boundary worked for statements: their first-word error fell from 8.5% (S33) to 3.2%, a difference of −5.25 [−7.30, −3.15]. Questions moved the other way (+5.74 [−0.51, +12.64]); the interval includes zero but the direction is bad. In the first reading, the ear heard a different first word in 13 of the 64 questions. In 9 of them a short syllable (*em*, *hem*, *na*) had been added in front. The likely cause is the `? ▁` word at the start of a question, which the voice sometimes pronounces. This has not been tested yet; reading the same weights without the question word would test it cheaply. One more epoch of training largely removed the problem: averaged over three readings, the first word of questions was misheard at 10.75% in S34, 5.74% in S34 a and 3.79% in S34 b read without marks, against 5.01% for S33.

### 7.5 The digraph xw

A dedicated token for *xw* was the one design that failed outright. Its slot had never been trained. Its row started at the mean of x and w and stayed there (cosine 0.997 between two independent trainings). S32 b said *xw* as a bare w or a bare x (*xwedê* → *wedê*): 7.2% of its 222 occurrences were misheard, against 2.3% on the stock path. On the human reader the ear often writes *xw* as x (166 times) but almost never as w (4 times), so the w-readings came from the voice. Format v3 writes the sound with its two letters, each of which has a trained embedding and a moving row. In S34 the error fell to 0.5%, one occurrence in 222, under the pre-registered threshold of 4%.

### 7.6 Stress

**Do the grammars' rules hold in speech?** Before any voice saw a stress mark, we measured 39,182 words in three sources: 31,452 words in the training audiobook, 5,393 in crowd-sourced read sentences and 2,337 in natural narratives (8.4 h of audio). A rule counted only if both main sources had at least 30 words. Three rules were confirmed: plural *-an*/*-ên* take the stress while *-ê*, *-a*, *-ek* leave it on the stem; negation prefixes take it; and *-iya*/*-iyê* do not move it to the end. Two were refuted: the mood prefix *di-* does not take the stress (its syllable was the weakest in all three sources), and *-ekî* leaves the stress on the stem. Three stayed open: infinitive against past *-in* forms, preverb infinitives, and the subjunctive prefix *bi-*. The default final stress of plain nouns was weakly supported (+0.16 and +0.05).

**A sign token does not carry stress (S31 b).** Adding the stress sign before each stressed vowel raised letter error from 3.40 to 4.66, and the sign did not move stress in the verb pairs (right direction in 2 of 5 measurable pairs, median −0.09; S28 reading naturally: 5 of 5, +0.38). The sign's row had started as a random vector of a full letter's length. After 1,500 steps it had moved 0.13 from that start, while x had moved 0.38. Every stressed vowel was therefore read behind a strong vector that meant nothing.

**A feature on the vowel reaches the model but does not move stress (S34 b).** Table 5 gives the main measure. Moving a typed mark from the first to the last syllable of the final verb did not move the stress. The two readings did differ in all 78 pairs, so the mark is seen and not followed. The measure is not blind: on unmarked control readings it finds the contrast the voice already makes between infinitive and past from context (D = +0.40, right direction for 9 of 11 verbs). The stress row grew to a length of 0.48, about twice a letter's row, yet the two arms' loss curves agree to the fourth decimal (0.8063 and 0.8064). Marks did not hurt clarity: marked minus control −0.26 [−0.47, −0.06], unmarked minus control −0.32 [−0.53, −0.11], marked minus unmarked +0.06 [−0.08, +0.20]. Under the pre-registered rule, v3 stayed the standard.

**Table 5.** Stress contrast measures (P units; 95% bootstrap intervals over sentences).

| Measure | Value | 95% interval | Note |
| --- | --- | --- | --- |
| C, mark moved first → last (S34 b) | −0.025 | [−0.095, +0.039] | 23 sentences, 11 positive (48%) |
| Noise floor, seed changed only (S34 a) | −0.007 | [−0.231, +0.232] | no marks |
| D, infinitive vs past from context (S34 a) | +0.40 | [+0.08, +0.84] | 9 of 11 verbs in the right direction |
| D on S28 (S31 test, median) | +0.38 | not computed | 5 of 5 measurable pairs in the right direction |

**Why the marks failed.** The re-analysis of 16 November found the cause in the teaching signal, not the mechanism. For every word in a quarter of the training segments we took the vowel with the highest prominence P and compared it with the vowel the rules mark (Table 6). The rules point at the reader's most prominent vowel little more often than chance. The reader is consistent, not noisy: in 95 frequent two-syllable word forms (at least 25 occurrences each), 82% of a form's tokens peak on the same vowel, where coin flips with the same counts would give 57%. The rules match that habitual vowel in 53 of the 95 forms (56%). The disagreements are systematic. *gelek* 'many' peaks on its first syllable 96% of the time, *dema* 'when' 96% and *gorî* 'according to' 76%, where the rules say final. *mirov* 'person' (82%), *eger* 'if' (97%) and *divê* 'must' (95%) peak on the final syllable, as the rules say. The voice could not learn "a mark means prominence here" because in its training audio the marks and the prominence were barely related.

**Table 6.** How often the rule-marked vowel is the most prominent vowel of a word, in sentence-internal words of the training audio.

| Vowels in the word | Words | Rule = most prominent | Chance |
| --- | --- | --- | --- |
| 2 | 10,733 | 58.2% | 50% |
| 3 | 9,048 | 44.5% | 33% |
| 4 | 4,461 | 42.5% | 25% |

A heard-mark labelling is drafted. Each cue is first corrected for position, because P rises before a pause and falls along the word. A vowel is marked only if it beats the next vowel by at least 0.5 P. On the quarter sample, 32.6% of multi-vowel words received a mark, spread evenly over syllables (50% / 50% in two-syllable words), so the voice cannot guess the mark from position. The marks are also largely a property of the word: 92% of the marked tokens of 71 frequent forms fall on the same vowel. This lowers the chance that heard marks will teach more than the spelling already does; Section 10 returns to it.

### 7.7 What the residual table learns

Five measurements of the trained tables explain why letters work and new symbols do not.

1. **The backbone's letters are not arranged by sound.** Frozen embeddings of Kurmanji vowel pairs are nearly orthogonal (cosine e–ê 0.12, i–î 0.08, u–û 0.04, c–ç 0.12, k–q 0.11; the closest pair is a–e at 0.32; mean over all letter pairs 0.09). Training does not pull one letter toward another: no row's direction resembles another letter by more than 0.3, and the shared direction of all rows carries only 2.3% of the table's energy. A good starting value for a new symbol cannot be borrowed from its neighbour in sound.
2. **The table learns the same thing every time where Kurmanji differs.** Two arms trained separately on the same data moved x, e, ê, ç, î, û and c in the same direction (cosine 0.82–0.91; mean over all rows 0.67). Between S34 and S31 a, two separate trainings with different formats and GPU counts, agreement was highest for q (0.77), ê (0.70), i (0.68), ş (0.65), x (0.64) and î (0.60), and lowest for letters whose sound needs no correction: l 0.09, s, z and f 0.15, k 0.18, m 0.21.
3. **Corrections are small.** A row moves about 10% of a letter's length (0.20 against 1.93). The largest moves are q 0.35, u 0.34, ê 0.30, x 0.29 and j 0.27.
4. **Rows that start from nothing do not learn.** The stress sign moved 0.13 from a random start in 1,500 steps, and the *xw* row stayed at its initial mean. Both slots had never been trained.
5. **No ready stress direction exists.** If the backbone had learned accented vowels as stressed vowels, the differences á − a, é − e, í − i would point the same way. They agree no more (mean cosine 0.16) than capital-letter or grave-accent differences do (0.09–0.22 and 0.11–0.27), and barely more than unrelated letter differences (0.04–0.12).

### 7.8 Sounds the spelling hides

The aspiration study asked whether the training reader makes the plain/aspirated contrast that the spelling hides. If so, a lexicon for future marks could come from the reader's own recordings. We measured voice onset time (VOT) on every word-initial ç, k, p and t followed by a vowel in the 7,586 segments. Of 40,772 tokens, 35,141 (86%) passed quality filters. On a synthetic Hindi voice, where the contrast is written, the same code found medians of 9/67 ms (p), 12/55 (t), 23/80 (k) and 54/96 (ç) for plain/aspirated stops, so the method sees the contrast where it exists.

**Table 7.** Reader's VOT: words the grammars call aspirated minus words they call plain (median difference, 95% interval), split-half reliability, and the pre-registered two-cluster test.

| | ç | k | p | t |
| --- | --- | --- | --- | --- |
| Aspirated − plain (ms) | 26.5 [16.5, 32] | **22 [20, 23]** | **24.5 [20, 28]** | 2 [−2, 4] |
| Tokens (aspirated / plain) | 92 / 219 | 1,196 / 1,771 | 80 / 979 | 1,137 / 165 |
| Split-half reliability | 0.988 | 0.988 | 0.979 | 0.972 |
| Two clusters (BIC gain > 10, Ashman D ≥ 2, minority ≥ 15%) | no | no | no (D 1.99) | no |

The reader makes the contrast for k and probably for p. For k the grammars' plain words measure 16–26 ms (*keç* 16, *kir* 22, *kur* 25) and their aspirated words 37–61 ms (*kurd* 38, *kar* 46, *ked* 61), with no overlap. For t the books' two groups did not separate (2 ms). For ç the difference rests on one word family and disappears after pauses (3.5 ms). Words did not fall into two clean clusters: 19 of 51 frequent k-words lie between the two groups. The result is "partial" under the pre-registered rule. 51 words received a class (23 k-words and 28 p-words), 50 of them new, so the lexicon grew from 30 to 80 entries. They cover 51 of the 192 frequent words. No embedding row was added, because the same mechanism had just failed for stress.

### 7.9 The ear: units, labels and spelling

**Label convention mattered more than units.** The first ear trainings (K5, links 1–3) kept capitals, punctuation and spelled-out numbers in the labels, while the base model had been trained on lower-case text without punctuation. With the decoder frozen, the encoder could not learn sentence-initial capitals. 243 of 500 outputs began with a wrong "E", and the trained ear was worse than the untrained base model: CER 10.00 and WER 29.27 against 8.89 and 29.25, scored the same way. Changing the labels to the base model's convention reversed this; the same run also shrank the shuffle window to fit host memory. CER fell to 7.88 and WER to 26.37, the first ear better than its base model. The ear lineage that followed (norm1) reached CER 7.08 and WER 24.2 on the 999 set.

**One spelling habit cost most of five points.** The permissioned conversational podcast's transcripts write *îy* before a vowel inside words. An ear trained with them (U1) wrote *sûrîyê* for standard *sûriyê* and scored WER 25.37 on broadcast news, 5.2 points worse than the base model's 20.15. Counting the two spellings as equal shrank the gap to 0.7 points. Rewriting that one habit in the labels (U2) brought WER to 21.39.

**The remaining errors need context, not symbols.** On 1,000 test sentences, U8 scores WER 24.2; ignoring circumflexes gives 21.5 and also dropping words with digits 21.2. Of the error fragments, 34% are substitutions (mostly vowels: e↔a, e↔i, ê↔î), 18% word-boundary errors, 17% deletions, 15% insertions and 15% circumflexes. The most frequent single errors are î→i (294), an extra space (202), a missing space (148) and i→î (105). Whether a short i is written, whether î or i is meant, and whether a postposition is joined (*pê re* / *pêre*) depend on the word and the sentence. The consonants, where the alphabet maps one letter to one sound, are heard well.

**Part of the error is the references' own spelling.** Scoring references and hypotheses both through `kanonik_v2()` lowers U8 from 24.17 to 22.27 (Common Voice 13.39 → 13.10, FLEURS 27.36 → 24.97) and U5 from 24.02 to 22.12. Forgiving all word-boundary differences as well would give 19.84. The ranking of systems did not change. Inconsistent reference spelling is worth about 1.9 points; the rest is the model.

**Re-ranking does not help.** An n-gram model of written Kurmanji preferred the correct candidate 76–78% of the time on read and broadcast speech but only 38% on conversation. Among U3's five beam candidates, two were distinct on average. A perfect chooser would gain at most 0.7 points, and the n-gram model gained 0.1–0.2. The ear's errors are shared by all its candidates.

### 7.10 Human listening

Three listeners have completed the blind test (450 clips). By the pre-registered rule this shows a direction and decides nothing. The direction is human > S34 ≈ S34 a ≈ S34 b > S28 (Table 8). The character-path voice S34 was rated more natural than the stock-path S28 by +0.57 [+0.31, +0.81]. Its gap to the human recordings was +0.38 [−0.00, +0.73], at the edge of significance.

**Table 8.** Blind listening, three listeners, 30 sentences per condition. "Machine" share: clips judged machine-made. Naturalness: mean of 1–5 ratings; weighted by each listener's skill at telling human from machine in the last column.

| Condition | "Machine" (%) | Naturalness | Skill-weighted |
| --- | --- | --- | --- |
| Human recording | 37 | 3.81 | 3.53 |
| S34 (character v3) | 49 | 3.43 | 3.07 |
| S34 a (character v3, +1 epoch) | 53 | 3.46 | 3.04 |
| S34 b (character v4, unmarked) | 54 | 3.47 | 2.99 |
| S28 (stock BPE) | 64 | 2.87 | 2.32 |

This comparison is confounded: S28 differs from S34 in its text path and also had less than half the training (0.79 against 1.77 epochs). The stock-path voice with equal training, S33, was not in the test. The listener with the best discrimination judged 88% of machine clips as machine and also called 53% of human clips machine. The human clips were formal, announcer-style readings, which that listener described as flat and emotionless. The machine voices were mistaken for human in 12% of that listener's judgements. They are not yet close to a human speaker.

## 8 Discussion

Three results reach beyond Kurmanji. A frozen multilingual voice learns a new language faster through letters it already has than through pieces it must relearn. A new symbol learns only if it starts from a trained one. A text mark teaches only what the audio already contains.

### 8.1 Why letters beat pieces here

Studies of tokenizer cost measure length, price and downstream accuracy (Rust et al., 2021; Petrov et al., 2023; Ahia et al., 2023). For a voice, the cost that matters is how much audio each unit needs before it is pronounced right. The stock BPE gave Kurmanji 3,334 pieces, half of them seen five times or fewer in 8,000 segments, each with an embedding learned for other languages. The character path gives 35 symbols. Each needs only a small correction, about a tenth of a letter's length, and independent trainings agree on the corrections where Kurmanji differs from other languages (q, ê, i, x, î, c). The gains landed exactly on those letters. This fits ByT5's finding that character and byte models do better on spelling- and pronunciation-sensitive tasks (Xue et al., 2022). The character path did more with less: S34 saw 14% less audio than S33 and read more clearly.

Why not train a Kurmanji BPE instead? Under LoRA, new pieces would need new embedding rows, and our tables show that a row starting from nothing does not learn in a run of this size (Section 7.7). The initialisation literature makes the same point for text models: new embeddings need a starting point taken from trained ones (Minixhofer et al., 2022; Dobler & de Melo, 2023). A Kurmanji subword vocabulary with embeddings built from its letters, or with full fine-tuning on far more audio, might do better. We have not tested it.

The price is sequence length. Steps took 37–45% longer, and the reading safeguard had to be rescaled. On free GPUs this was affordable. Counted in GPU hours, S34 used about a quarter more than S33 (13.9 against 11.2) and gained 1.01 points. S33 had used 2.8 times the GPU hours of S28 for a gain of 1.14.

### 8.2 What the intonation result means

The early character voices lost real information about questions: separation fell from 0.70 to 0.61. At equal training the loss disappeared (0.683 against 0.680), and what remained was a shift of the decision point. S34 calls fewer sentences questions overall. Question share alone would have hidden this distinction, which is why we now report separation next to it. The text path is not what limits question intonation. The data are: 73 questions in 7,586 segments. The only other questions available, crowd-sourced recordings, improved intonation by 5.6 points while costing 4.35 points of clarity. The question head illustrates a trade-off. It helped first words of questions when added to a voice trained on it. In the S34 format, where the head is a word of its own, it may be pronounced as an extra syllable, an effect that one more epoch of training largely removed.

### 8.3 What the stress result means

The v4 mechanism did what it was built to do. Marks reached the voice (every pair of readings differed), did not harm clarity, and could be loaded onto an unmarked voice without changing it. It did not move stress, because the teaching signal was wrong. Rule marks fell on the reader's most prominent vowel in 58% of two-syllable words, little more than chance. A voice cannot learn "a mark means prominence here" from audio in which marks and prominence are barely related. The reader, by contrast, is consistent (82% per frequent word form). A lexicon of heard marks would therefore be learnable, but 92% of such marks are a property of the word, which the voice can already infer from the spelling. What a mark could add is control over rare words and deliberate contrasts. The voice already separates *hátin* from *hatín* by context (D = +0.40).

The general lesson applies to any symbolic prosody input, from stress dictionaries to phrase-boundary labels: before teaching a mark, count how often it agrees with the audio it will be trained on. The Arabic diacritics result points the same way. Marks help small-data TTS (Musleh et al., 2026), but only when they are right.

### 8.4 Sounds the spelling hides

The reader makes the aspiration contrast for k and probably for p, with 22–24.5 ms between the grammars' two groups. For t the contrast could not be shown with this measure, and for ç the measure does not work. A voice trained on one reader picks up the contrast in frequent words without any mark. Marks would be needed for rare words, for other speakers and for dialects, and a lexicon for them now exists for 51 words. Writing the contrast into the text before such a lexicon is complete would repeat the stress experiment's mistake.

### 8.5 The ear

The ear's units were right from the start. Its base model's 9,812 characters cover every Kurmanji letter (Omnilingual ASR team, 2025). What mattered was the text convention around the units: lower case and no punctuation as the base model expected, and one spelling per word. Its remaining errors are vowels (î/i, e/a, ê/î) and word boundaries. They depend on knowing the word and the sentence, not on the alphabet, and rescoring a near-identical beam cannot fix them. This mirrors a result for English, where graphemes and word-pieces beat phonemes once enough data and context are available (Irie et al., 2019). For Kurmanji, the regular consonant spelling already pays off: consonants are where the ear is accurate.

### 8.6 Silent failures

Many of our failures produced no error message. VoxCPM's loader skipped a table it did not find. A voice could be read with options other than the ones it was trained with. A missing lexicon file changed the stress marks. A forwarding method would have handed callers BPE pieces again. An expired certificate on a model server left an ear job that "succeeded" without transcribing a single clip. The countermeasures are cheap, and we recommend them to anyone adapting a frozen model: named formats with frozen fingerprints, a format file next to the weights, a post-load check that the table moved, no fallback to the old tokenizer, and a count of clips actually heard in every result.

## 9 Limitations

We list the limits of this study in order of how much they could change its conclusions.

1. **One reader, one book.** Every voice was trained on 33.5 hours of one professional reader reading formal prose. The results may not hold for conversational speech, other speakers or dialects. The voices imitate a permissioned reader and cannot be published, which limits independent replication of the voice results.
2. **Machines as judges.** Intelligibility is measured by our own ear, whose confusions (ê/e, u/û) inflate absolute error rates. The prosody judge was trained on crowd-sourced read sentences, has a ceiling of about 69% on human questions and looks only at the last second of a sentence. Differences in question share below 11.9 points cannot be told apart, and only 10–11 test questions are marked by intonation alone.
3. **A small listening test.** Three listeners completed it, and by pre-registration that shows a direction only. The human references were formal readings, and the stock-path voice in the test (S28) also had less than half the training of S34.
4. **Missing baselines.** We did not compare against phoneme input, a Kurmanji-trained subword vocabulary, or full fine-tuning of the embeddings. All voices use LoRA of rank 32. Larger budgets might change the ranking.
5. **The stress tests are small.** The contrast measure rests on 13 verbs in two frames (23 measurable sentences). Its prominence score combines four cues and is not stress itself, and forced alignment misplaces word boundaries by 29–40 ms. The heard-mark labels are a draft.
6. **Training variance.** Each training ran once. Arms trained from the same start drifted 0.3 points apart, which bounds how small a difference we can trust.
7. **The ear's comparisons.** The K5 label change was made together with a smaller shuffle window. The conversation references are partly machine drafts. Whether the base model's training data overlap the public test sets is unknown.
8. **Scripts and dialects.** The voice reads Latin script only, and dialect labels are not yet used by it. Some Zazaki may have leaked into Kurmanji data through one channel.
9. **Exceptions to our own gate.** Our submission gate asks for an expected gain of at least twice the measured half-width. Two runs were launched under documented exceptions: for S34 the expected gain was smaller than that, and for S34 a/b the half-width of the new measure was not yet known. The S34 exception paid off.
10. **AI-assisted development.** Much of the code and analysis was written by AI assistants under human direction. Tests, fingerprints and pre-registration reduce, but do not exclude, unnoticed errors.

## 10 Future work

Ranked by the gain we expect from each, given what this study measured:

1. **Questions and conversation in the voice's data.** Intonation is limited by data, not by the text path. The next voice training adds question-rich, naturally spoken material in the standard format v3.
2. **Stress marks from the speaker.** Mark the vowel the reader actually stresses (the drafted heard-mark labels), and record minimal pairs in which the same text is read with stress in two places. Such pairs are the cleanest possible teacher for a mark.
3. **Test the question word.** Read S34 without its leading `? ▁` to see whether it causes the added first syllable. If it does, try a separate start-of-question token whose row starts from the question mark's.
4. **Complete the hidden-sound lexicon.** Add a second cue (burst energy or onset pitch) for t and ç, and dictionaries that mark aspiration. Add marks to the text only with a pre-registration, and start every new row from the letter it modifies.
5. **Dialect and speaker labels.** A dialect token at the start of the text, initialised at zero so that an unknown dialect reads as standard, and a multi-speaker voice of the project's own.
6. **Context for the ear.** Decode with a language model trained on large Kurmanji text, write rules or a lexicon for short i and word boundaries, extend the single-spelling score with a human-curated lexicon, and add e/ê and u/û minimal pairs to the ear's test.
7. **Arabic-script Kurmanji.** Context-aware transliteration into the Latin standard, in the manner of script normalisation for bilingual communities (Ahmadi & Anastasopoulos, 2023).
8. **Missing baselines.** A Kurmanji subword vocabulary with embeddings built from its letters, phoneme input from the IPA table in `ses.py`, and a measurement of Kurmanji fertility in other widely used tokenizers.
9. **A Kurmanji text model.** For text-only tasks, a morphology-aware vocabulary in the manner of the Turkish and Arabic results (Toraman et al., 2023; Antoun et al., 2020).
10. **A decisive listening test.** At least five listeners, with conversational human references, as the pre-registration requires.

## 11 A practitioner's guide

This section is written for three readers: those who will use the Deng voice and ear, those who will build on our text path, and those who will start a similar project for another language. Code paths are relative to the project repository.

### 11.1 Using our models

**Preparing text for the voice.** The voice reads standard Kurmanji in Latin script. Before reading, pass the text through the preparer, which spells out numbers, times and dates, applies the standard spelling and restores missing circumflexes:

```python
import sys; sys.path[:0] = ["metin", "metin/kurmanci"]
from hazirla import hazirla
text = hazirla("Ez ê saet 9:30 bêm.")             # -> "Ez ê saet neh û nîv bêm."
text = hazirla(raw, sapka_kipi="sapkasiz")        # text typed without circumflexes
```

Write questions with a question mark; the path adds the question head itself. Acronyms are spelled by the path (*TV* → *teve*). Do not feed Arabic-script text: transliterate it first. Symbols such as `/`, `+` or `=` break the word and are counted, not read.

**Loading a voice.** Always take the format from the file next to the weights, and install the path before loading the weights:

```python
import json, os
from voxcpm import VoxCPM
from voxcpm.model.voxcpm2 import LoRAConfig
import kmr_token

folder = "path/to/lora"                                   # holds lora_weights.safetensors, text_path.json
lw = f"{folder}/lora_weights.safetensors"
lc = json.load(open(f"{folder}/lora_config.json"))["lora_config"]
m = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False,
                           lora_config=LoRAConfig(**lc), lora_weights_path=lw)
fmt = kmr_token.load_format(folder)                       # raises if the weights do not say
tok = kmr_token.install(m.tts_model, fmt=fmt)             # before load_lora, once
loaded, skipped = m.load_lora(lw)
assert "base_lm.lora_text_delta" in loaded                # the letter table was found
kmr_token.table_check(m.tts_model)                        # raises if the table never moved
wav = m.generate(text=text)                               # 48 kHz
print(tok.dropped)                                        # characters the path could not say
```

For production retries, scale VoxCPM's bad-case ratio to the longer sequences: `kmr_token.BADCASE_RATIO` is 2.6 instead of 6.0.

**Stress marks.** Only a v4 voice understands them. A typed `ˈ` before a vowel (*hˈatin*, *hatˈin*) overrides the rule for that word, and `install(..., policy="none")` or `"all"` chooses the rule's marks at reading time. Our measurements show that marks do not yet move stress (Section 7.6), so do not rely on them.

**Using the ear.** Its output is lower-case, unpunctuated, standard Kurmanji. It sometimes writes numbers as digits. When you compare transcripts or compute error rates, normalise both sides with the same function, and report which one you used:

```python
from kanonik import kanonik_v2                            # metin/kurmanci/kanonik.py
score_ref, score_hyp = kanonik_v2(reference), kanonik_v2(hypothesis)
```

**Checklist for users**

- [ ] The text is Latin-script Kurmanji; anything else has been transliterated.
- [ ] `hazirla()` was applied.
- [ ] The format came from `text_path.json`, never typed by hand.
- [ ] `install()` ran before `load_lora()`, and `table_check()` passed.
- [ ] `tok.dropped` is empty, or every dropped character is understood.
- [ ] Ear scores on both sides use the same normaliser.

### 11.2 Building on our text path

**Never change a format that has trained weights.** Add a new name to `FORMATS`, write its fingerprint test over the 7,586 training texts and 267 test sentences, and let training write it with `save_format()`. Old voices keep reading with their own names.

**Adding a symbol.** There are two ways, and the choice decides where the new row starts.

- *A new letter-like symbol* goes at the end of `alphabet()`, which changes the table size (41 rows today). Start its row from trained parts, for example the mean of the letters it is made of, never from a random vector: in our runs a random row moved 0.13 in 1,500 steps and the voice read worse (Section 7.6).
- *A feature on an existing letter* (stress, aspiration, trill) is a mark. It uses one of the seven free rows of the marks table and a reserved slot from 920 upward, and its row starts at zero, so the marked letter reads exactly as the plain letter on the first step. Marks are appended to `MARKS`, never reordered, because saved tables find rows by position. The current code accepts only the stress mark, so a new mark needs the same small extension that v4 added.

**Before teaching any mark, measure its agreement with the audio.** Count how often the mark falls where the training speaker actually realises the feature, as `olcumler/metin-yolu/heard_vs_rule.py` does for stress. Our rule marks agreed with the reader's prominence in 58% of two-syllable words, and the voice learned nothing from them.

**Continuing from our voices.** A v3 voice loads into v4 unchanged, because the marks table starts at zero. To continue training, start from S34 (v3) or S34 a; the S34 b weights are frozen to format v4.

**Evaluating a change.** Use the locked test sentences, three seed sets, sentence-paired bootstrap intervals, letter error by position and by letter, separation next to question share, and the number of clips actually heard. Write the decision rule before the run.

**Checklist for builders**

- [ ] A new format name; existing entries untouched; fingerprints added and passing.
- [ ] New rows start from trained embeddings, or at zero as a mark on a letter.
- [ ] Mark–audio agreement measured before training.
- [ ] An equal-training baseline and a written decision rule.
- [ ] A short diagnostic run first, for step time, memory and table movement.
- [ ] `text_path.json` written by training and read by every reader.

### 11.3 Starting from scratch for another language

The procedure below is what we would do again for another low-resource language with a frozen multilingual TTS model.

1. **Measure the stock tokenizer on your language first.** Count distinct pieces, the share seen five times or fewer, fertility and the proportion of continued words (Rust et al., 2021). Check whether your key digraphs ever form one piece:

    ```python
    from collections import Counter
    pieces, words = Counter(), 0
    for line in open("corpus.txt", encoding="utf8"):
        pieces.update(tokenizer.tokenize(line))
        words += len(line.split())
    rare = sum(1 for n in pieces.values() if n <= 5)
    print(len(pieces), rare, sum(pieces.values()) / words)   # distinct, rare, fertility
    ```

2. **Check that every letter exists as a single token** and count the backbone's unused reserved tokens. Our path needed all 31 letters, the space piece and seven punctuation marks to exist, plus 10 reserved slots.
3. **Choose the unit.** With a near-phonemic orthography and tens of hours of audio, use characters with a residual table on the frozen embeddings, as below. With a deep orthography, consider phonemes. With much more audio or full fine-tuning, a language-specific subword vocabulary initialised from existing embeddings becomes an option (Minixhofer et al., 2022; Dobler & de Melo, 2023).

    ```python
    import torch
    ids = torch.tensor([vocab[s] for s in symbols])                    # existing single-character tokens
    delta = torch.nn.Parameter(torch.zeros(len(symbols), emb.weight.shape[1]))
    row_of = torch.full((emb.num_embeddings,), -1, dtype=torch.long)
    row_of[ids] = torch.arange(len(symbols))

    def add_rows(module, args, out):                                   # forward hook on the embedding
        rows = row_of[args[0]]
        return out + (rows >= 0).unsqueeze(-1) * delta[rows.clamp(min=0)]

    emb.register_forward_hook(add_rows)                                # name delta "lora_..." to save it
    ```

4. **Write one-sound digraphs with their letters** unless the new token can start from trained parts.
5. **Mark the sentence edges.** Open every text with the word boundary so the first word looks like the others, and test a question head at the start of questions.
6. **Spell what readers say.** Acronyms as letter names, numbers as words, one standard spelling, and the dialect as a separate label.
7. **Add prosodic marks only from measured agreement** with your training audio, and start their rows at zero on the letter they modify.
8. **Make silent failures loud.** Name and freeze formats, fingerprint them, write the format next to the weights, check after loading that the table moved, and give the new tokenizer no fallback to the old one.
9. **Evaluate per letter and per position,** with an automatic judge and human listeners. Report separation as well as rates, and pre-register the decision rules.
10. **For speech recognition, keep the base model's output units and label convention,** standardise the spelling of the labels, and report a second score with a canonical spelling to measure how much error the references themselves contribute.

**Checklist for a new project**

- [ ] Stock tokenizer measured: pieces, rare pieces, fertility, digraphs.
- [ ] Every letter a single existing token; reserved slots counted.
- [ ] Unit chosen from orthography depth and data size.
- [ ] Edges marked; acronyms and numbers spelled; one standard spelling.
- [ ] Marks only with measured audio agreement.
- [ ] Formats named, fingerprinted, written and checked.
- [ ] Per-letter and per-position evaluation; human listening; pre-registration.

## 12 Conclusion

For a language that a frozen multilingual TTS model has never seen, the text interface is a cheap and decisive lever. Replacing 3,334 foreign subword pieces with 35 Kurmanji letters and a small learned correction per letter made the voice clearer at equal training (letter error 3.62 → 2.61). The gain came mostly on the letters Kurmanji reads differently, and it cost about a quarter more GPU time. The same interface could not teach stress from rules the speaker did not follow, and question intonation turned out to be a data problem, not a tokenization problem. For the ear, the base model's character units were already right; label conventions and consistent spelling decided the outcome.

Four principles carry over to other low-resource languages. Measure the stock tokenizer before training. Build new symbols on embeddings the model has already trained. Mark only what the training audio confirms. Make every text format explicit, and make every mismatch fail loudly.

## Declarations

**Data availability.** The crowd-sourced Kurmanji speech corpora used here (Common Voice and FLEURS) are public. The open-licensed and public-domain Kurmanji audio used in later ear runs is released by the project as an open dataset, with per-source licence information. The audiobook that trains the voice and the conversational podcast used for one ear test were made available by their rights holders for this project only. They cannot be redistributed, and voices trained on them are not published. The tokenizer and evaluation code (`kmr_token.py`, `vurgu.py`, `ses.py`, `kanonik.py`, `hazirla.py`), its tests and the measurement files cited in this paper are kept in the project repository and are available from the project on request.

**Ethics.** The voices studied here imitate one reader who gave permission for this use. They are kept within the project team and are not released. The permissions forbid copying any speaker's voice and publishing the recordings, and the project is building a voice of its own that resembles no real speaker. Listening-test participants volunteered; this paper reports their answers without names.

**Competing interests.** The project team declares no competing interests.

**Funding.** No external funding. Training and evaluation ran on the free GPU quotas of a public notebook service.

**Author contributions.** The Deng project team set the goals, obtained the data permissions, listened to and judged the voices, and approved every decision. Design, code, experiments, analyses and this text were produced with AI assistance under the team's direction (see below).

**Use of AI tools.** Most of the code, analyses and text reported here were drafted by AI assistants (Claude family models) working under the direction of the project team. Every number in the paper was read from the project's result files. Literature claims were checked against the cited sources, and citation counts were retrieved from OpenAlex on 23 November 2026. The team remains responsible for the content.

**Acknowledgements.** We thank the rights holders who allowed their recordings to be used, and the volunteers who listened.

## References

Abdelali, A., Darwish, K., Durrani, N., & Mubarak, H. (2016). Farasa: A fast and furious segmenter for Arabic. In *Proceedings of NAACL-HLT 2016: Demonstrations*. https://doi.org/10.18653/v1/N16-3003

Abdullah, A. A., Tabibian, S., Veisi, H., Mahmudi, A., et al. (2024). End-to-end transformer-based automatic speech recognition for Northern Kurdish: A pioneering approach. arXiv:2410.16330. https://doi.org/10.48550/arXiv.2410.16330

Ahia, O., Kumar, S., Gonen, H., Kasai, J., Mortensen, D. R., Smith, N. A., & Tsvetkov, Y. (2023). Do all languages cost the same? Tokenization in the era of commercial language models. In *Proceedings of EMNLP 2023*. https://doi.org/10.18653/v1/2023.emnlp-main.614

Ahmad, H. A., & Rashid, T. A. (2024). Central Kurdish text-to-speech synthesis with novel end-to-end transformer training. *Algorithms*, 17(7), 292. https://doi.org/10.3390/a17070292

Ahmadi, S. (2020a). A tokenization system for the Kurdish language. In *Proceedings of the 7th Workshop on NLP for Similar Languages, Varieties and Dialects (VarDial 2020)*, 114–127.

Ahmadi, S. (2020b). KLPT – Kurdish Language Processing Toolkit. In *Proceedings of the Second Workshop for NLP Open Source Software (NLP-OSS)*. https://doi.org/10.18653/v1/2020.nlposs-1.11

Ahmadi, S. (2020c). Building a corpus for the Zaza–Gorani language family. In *Proceedings of the 7th Workshop on NLP for Similar Languages, Varieties and Dialects (VarDial 2020)*, 70–78.

Ahmadi, S., & Anastasopoulos, A. (2023). Script normalization for unconventional writing of under-resourced languages in bilingual communities. In *Proceedings of ACL 2023*. https://doi.org/10.18653/v1/2023.acl-long.809

Ali, M., Fromm, M., Thellmann, K., Rutmann, R., et al. (2024). Tokenizer choice for LLM training: Negligible or crucial? In *Findings of NAACL 2024*. https://doi.org/10.18653/v1/2024.findings-naacl.247

Alyafeai, Z., Al-shaibani, M. S., Ghaleb, M., & Ahmad, I. (2023). Evaluating various tokenizers for Arabic text classification. *Neural Processing Letters*. https://doi.org/10.1007/s11063-022-10990-8

Antoun, W., Baly, F., & Hajj, H. (2020). AraBERT: Transformer-based model for Arabic language understanding. In *Proceedings of the 4th Workshop on Open-Source Arabic Corpora and Processing Tools (OSACT)*. arXiv:2003.00104.

Ardila, R., Branson, M., Davis, K., Henretty, M., et al. (2020). Common Voice: A massively-multilingual speech corpus. In *Proceedings of LREC 2020*. arXiv:1912.06670.

Baevski, A., Zhou, Y., Mohamed, A., & Auli, M. (2020). wav2vec 2.0: A framework for self-supervised learning of speech representations. In *Advances in Neural Information Processing Systems 33*.

Borsos, Z., Marinier, R., Vincent, D., Kharitonov, E., et al. (2023). AudioLM: A language modeling approach to audio generation. *IEEE/ACM Transactions on Audio, Speech, and Language Processing*. https://doi.org/10.1109/TASLP.2023.3288409

Bostrom, K., & Durrett, G. (2020). Byte pair encoding is suboptimal for language model pretraining. In *Findings of EMNLP 2020*. https://doi.org/10.18653/v1/2020.findings-emnlp.414

Clark, J. H., Garrette, D., Turc, I., & Wieting, J. (2022). CANINE: Pre-training an efficient tokenization-free encoder for language representation. *Transactions of the Association for Computational Linguistics*, 10. https://doi.org/10.1162/tacl_a_00448

Conneau, A., Ma, M., Khanuja, S., Zhang, Y., et al. (2023). FLEURS: Few-shot learning evaluation of universal representations of speech. In *IEEE Spoken Language Technology Workshop (SLT 2022)*. https://doi.org/10.1109/SLT54892.2023.10023141

Creutz, M., & Lagus, K. (2007). Unsupervised models for morpheme segmentation and morphology learning. *ACM Transactions on Speech and Language Processing*, 4(1). https://doi.org/10.1145/1187415.1187418

Défossez, A., Copet, J., Synnaeve, G., & Adi, Y. (2023). High fidelity neural audio compression. *Transactions on Machine Learning Research*. arXiv:2210.13438.

Dobler, K., & de Melo, G. (2023). FOCUS: Effective embedding initialization for monolingual specialization of multilingual models. In *Proceedings of EMNLP 2023*. https://doi.org/10.18653/v1/2023.emnlp-main.829

Doostmohammadi, E., Nassajian, M., & Rahimi, A. (2020). Persian ezafe recognition using transformers and its role in part-of-speech tagging. In *Findings of EMNLP 2020*. https://doi.org/10.18653/v1/2020.findings-emnlp.86

Esmaili, K. S., & Salavati, S. (2013). Sorani Kurdish versus Kurmanji Kurdish: An empirical comparison. In *Proceedings of ACL 2013 (Volume 2: Short Papers)*.

Farahani, M., Gharachorloo, M., Farahani, M., & Manthouri, M. (2021). ParsBERT: Transformer-based model for Persian language understanding. *Neural Processing Letters*. https://doi.org/10.1007/s11063-021-10528-4

Gage, P. (1994). A new algorithm for data compression. *The C Users Journal*, 12(2).

Gal, R., Alaluf, Y., Atzmon, Y., Patashnik, O., et al. (2023). An image is worth one word: Personalizing text-to-image generation using textual inversion. In *ICLR 2023*. arXiv:2208.01618.

Gökırmak, M., & Tyers, F. M. (2017). A dependency treebank for Kurmanji Kurdish. In *Proceedings of the Fourth International Conference on Dependency Linguistics (Depling 2017)*.

Graves, A., Fernández, S., Gomez, F., & Schmidhuber, J. (2006). Connectionist temporal classification: Labelling unsegmented sequence data with recurrent neural networks. In *Proceedings of ICML 2006*. https://doi.org/10.1145/1143844.1143891

Hsu, W.-N., Bolte, B., Tsai, Y.-H. H., Lakhotia, K., et al. (2021). HuBERT: Self-supervised speech representation learning by masked prediction of hidden units. *IEEE/ACM Transactions on Audio, Speech, and Language Processing*. https://doi.org/10.1109/TASLP.2021.3122291

Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., et al. (2022). LoRA: Low-rank adaptation of large language models. In *ICLR 2022*. arXiv:2106.09685.

Irie, K., Prabhavalkar, R., Kannan, A., Bruguier, A., et al. (2019). On the choice of modeling unit for sequence-to-sequence speech recognition. In *Proceedings of Interspeech 2019*. https://doi.org/10.21437/Interspeech.2019-2277

Karabax, A. (2013). *Rêzimana Kurdî ya Kurmancî, bi hîndarî*. 343 pp.

Kudo, T. (2018). Subword regularization: Improving neural network translation models with multiple subword candidates. In *Proceedings of ACL 2018*. https://doi.org/10.18653/v1/P18-1007

Kudo, T., & Richardson, J. (2018). SentencePiece: A simple and language independent subword tokenizer and detokenizer for neural text processing. In *Proceedings of EMNLP 2018: System Demonstrations*. https://doi.org/10.18653/v1/D18-2012

Lakhotia, K., Kharitonov, E., Hsu, W.-N., Adi, Y., et al. (2021). On generative spoken language modeling from raw audio. *Transactions of the Association for Computational Linguistics*, 9. https://doi.org/10.1162/tacl_a_00430

Lee, J., Cho, K., & Hofmann, T. (2017). Fully character-level neural machine translation without explicit segmentation. *Transactions of the Association for Computational Linguistics*, 5. https://doi.org/10.1162/tacl_a_00067

Li, B., Zhang, Y., Sainath, T. N., Wu, Y., et al. (2019). Bytes are all you need: End-to-end multilingual speech recognition and synthesis with bytes. In *Proceedings of ICASSP 2019*. https://doi.org/10.1109/ICASSP.2019.8682674

Mahmudi, A., & Veisi, H. (2021). Automated grapheme-to-phoneme conversion for Central Kurdish based on optimality theory. *Computer Speech & Language*, 70, 101222. https://doi.org/10.1016/j.csl.2021.101222

Mielke, S. J., Alyafeai, Z., Salesky, E., Raffel, C., et al. (2021). Between words and characters: A brief history of open-vocabulary modeling and tokenization in NLP. arXiv:2112.10508.

Minixhofer, B., Paischer, F., & Rekabsaz, N. (2022). WECHSEL: Effective initialization of subword embeddings for cross-lingual transfer of monolingual language models. In *Proceedings of NAACL 2022*. https://doi.org/10.18653/v1/2022.naacl-main.293

Musleh, A., Zhang, Y., & Darwish, K. (2026). More data, fewer diacritics: Scaling Arabic TTS. arXiv:2603.01622.

Omnilingual ASR team: Keren, G., Kozhevnikov, A., Meng, Y., Ropers, C., et al. (2025). Omnilingual ASR: Open-source multilingual speech recognition for 1600+ languages. arXiv:2511.09690. https://doi.org/10.48550/arXiv.2511.09690

Öpengin, E., & Haig, G. (2014). Regional variation in Kurmanji: A preliminary classification of dialects. *Kurdish Studies*, 2(2), 143–176. https://doi.org/10.33182/ks.v2i2.399

Pagnoni, A., Pasunuru, R., Rodriguez, P., Nguyen, J., et al. (2024). Byte latent transformer: Patches scale better than tokens. arXiv:2412.09871.

Petrov, A., La Malfa, E., Torr, P. H. S., & Bibi, A. (2023). Language model tokenizers introduce unfairness between languages. In *Advances in Neural Information Processing Systems 36*. arXiv:2305.15425.

Pfeiffer, J., Vulić, I., Gurevych, I., & Ruder, S. (2021). UNKs everywhere: Adapting multilingual language models to new scripts. In *Proceedings of EMNLP 2021*. https://doi.org/10.18653/v1/2021.emnlp-main.800

Pratap, V., Tjandra, A., Shi, B., Tomasello, P., et al. (2024). Scaling speech technology to 1,000+ languages. *Journal of Machine Learning Research*, 25. arXiv:2305.13516.

Provilkov, I., Emelianenko, D., & Voita, E. (2020). BPE-dropout: Simple and effective subword regularization. In *Proceedings of ACL 2020*. https://doi.org/10.18653/v1/2020.acl-main.170

Radford, A., Kim, J. W., Xu, T., Brockman, G., et al. (2023). Robust speech recognition via large-scale weak supervision. In *Proceedings of ICML 2023*. arXiv:2212.04356.

Rahmati, E., & Sameti, H. (2024). GE2PE: Persian end-to-end grapheme-to-phoneme conversion. In *Findings of EMNLP 2024*. https://doi.org/10.18653/v1/2024.findings-emnlp.196

Rust, P., Pfeiffer, J., Vulić, I., Ruder, S., & Gurevych, I. (2021). How good is your tokenizer? On the monolingual performance of multilingual language models. In *Proceedings of ACL-IJCNLP 2021*. https://doi.org/10.18653/v1/2021.acl-long.243

Schuster, M., & Nakajima, K. (2012). Japanese and Korean voice search. In *Proceedings of ICASSP 2012*. https://doi.org/10.1109/ICASSP.2012.6289079

Schweter, S. (2020). BERTurk – BERT models for Turkish (version 1.0.0). Zenodo. https://doi.org/10.5281/zenodo.3770924

Sennrich, R., Haddow, B., & Birch, A. (2016). Neural machine translation of rare words with subword units. In *Proceedings of ACL 2016*. https://doi.org/10.18653/v1/P16-1162

Shen, J., Pang, R., Weiss, R. J., Schuster, M., et al. (2018). Natural TTS synthesis by conditioning WaveNet on mel spectrogram predictions. In *Proceedings of ICASSP 2018*. https://doi.org/10.1109/ICASSP.2018.8461368

Tan, S. (2011). *Rêzimana Kurmancî* (expanded edition). Istanbul. 400 pp.

Tay, Y., Tran, V. Q., Ruder, S., Gupta, J. P., et al. (2022). Charformer: Fast character transformers via gradient-based subword tokenization. In *ICLR 2022*. arXiv:2106.12672.

Toraman, Ç., Yılmaz, E. H., Şahinuç, F., & Ozcelik, O. (2023). Impact of tokenization on language models: An analysis for Turkish. *ACM Transactions on Asian and Low-Resource Language Information Processing*. https://doi.org/10.1145/3578707

Veisi, H., Mohammadamini, M., & Hosseini, H. (2020). Toward Kurdish language processing: Experiments in collecting and processing the AsoSoft text corpus. *Digital Scholarship in the Humanities*. https://doi.org/10.1093/llc/fqy074

Veisi, H., Hosseini, H., Mohammadamini, M., Fathy, W., et al. (2022). Jira: A Central Kurdish speech recognition system, designing and building speech corpus and pronunciation lexicon. *Language Resources and Evaluation*. https://doi.org/10.1007/s10579-022-09594-4

Wang, C., Chen, S., Wu, Y., Zhang, Z., et al. (2023). Neural codec language models are zero-shot text to speech synthesizers. arXiv:2301.02111.

Wang, Y., Stanton, D., Zhang, Y., Skerry-Ryan, R. J., et al. (2018). Style tokens: Unsupervised style modeling, control and transfer in end-to-end speech synthesis. In *Proceedings of ICML 2018*. arXiv:1803.09017.

Wu, Y., Schuster, M., Chen, Z., Le, Q. V., et al. (2016). Google's neural machine translation system: Bridging the gap between human and machine translation. arXiv:1609.08144.

Xue, L., Barua, A., Constant, N., Al-Rfou, R., et al. (2022). ByT5: Towards a token-free future with pre-trained byte-to-byte models. *Transactions of the Association for Computational Linguistics*, 10. https://doi.org/10.1162/tacl_a_00461

Yu, L., Simig, D., Flaherty, C., Aghajanyan, A., et al. (2023). MEGABYTE: Predicting million-byte sequences with multiscale transformers. In *Advances in Neural Information Processing Systems 36*. arXiv:2305.07185.

Zeghidour, N., Luebs, A., Omran, A., Skoglund, J., & Tagliasacchi, M. (2021). SoundStream: An end-to-end neural audio codec. *IEEE/ACM Transactions on Audio, Speech, and Language Processing*. https://doi.org/10.1109/TASLP.2021.3129994

Zhou, Y., Zeng, G., Liu, X., Li, X., et al. (2025). VoxCPM: Tokenizer-free TTS for context-aware speech generation and true-to-life voice cloning. arXiv:2509.24650. https://doi.org/10.48550/arXiv.2509.24650

Zouhar, V., Meister, C., Gastaldi, J. L., Du, L., et al. (2023). Tokenization and the noiseless channel. In *Proceedings of ACL 2023*. https://doi.org/10.18653/v1/2023.acl-long.284

VoxCPM2 model card (2025). Hugging Face, model `openbmb/VoxCPM2`. https://huggingface.co/openbmb/VoxCPM2 (accessed 23 November 2026).

## Appendices

### Appendix A. The 41-row symbol inventory

Rows are found by position, so this order is part of every saved table. The sound values are the usual IPA values recorded in `ses.py`; where a letter covers two phonemes, the aspirated or tapped member is listed.

| Rows | Symbols in order | Sound values |
| --- | --- | --- |
| 0–7 | a b c ç d e ê f | ɑː b dʒ tʃʰ d ɛ eː f |
| 8–15 | g h i î j k l m | g h ɪ iː ʒ kʰ l m |
| 16–23 | n o p q r s ş t | n oː pʰ q ɾ s ʃ tʰ |
| 24–30 | u û v w x y z | ʊ uː v w x j z |
| 31 | `xw` (slot `<reserved_901>`) | xʷ |
| 32 | stress sign `ˈ` (slot `<reserved_900>`) | — |
| 33 | `▁` word boundary | — |
| 34–40 | `. , ? ! : ; -` | — |

Format v4 adds eight marked vowels in slots `<reserved_910>`–`<reserved_917>`, in alphabet order (a e ê i î o u û). They have no rows of their own: each reads its vowel's frozen embedding and row plus four times the stress row.

### Appendix B. Format fingerprints

Each fingerprint is the first 16 hexadecimal digits of a SHA-256 over every token sequence of a text set, one sequence per line with symbols joined by U+001F (`test_kurmanci.py`). A change in the code, the stress rules or their data files that alters any token moves the fingerprint and fails the test.

| Format | 267 test sentences | 7,586 training texts | Trained weights |
| --- | --- | --- | --- |
| s31 | `54dc269134e30242` | `42b59bc9728ec9a1` | S31 a, S32 a |
| s31-stress | `5936abf9f12f5f36` | `18a0171d0c52fecd` | S31 b |
| s32 | `87e000d03e5ff022` | `78c7b2b834056191` | S32 b |
| v2 | `3f6662e97d586aff` | `e6ec6b9cada9cb2c` | none |
| v3 | `adff7f06e7eaf578` | `e979ce904540dd71` | S34, S34 a |
| v4 | `20bc6e3a4d3e0329` | `50449359213f7105` | S34 b |

### Appendix C. Reproducing the measurements

All commands run from the project root. The voice runs themselves need the permissioned audio and are not reproducible outside the project. Every number derived from their outputs can be recomputed from the stored result files.

| What | Command or location |
| --- | --- |
| Tokenizer tests, fingerprints, stress rules on the grammars' examples | `python3 metin/kurmanci/test_kurmanci.py` |
| Tokens of any sentence in each format | `python3 metin/kurmanci/kmr_token.py "Tu kengî hatî?"` |
| Letter error by position, question share, separation | `python3 olcumler/metin-yolu/konum.py --json` → `konum.json` |
| Letter error by letter and confusions | `python3 olcumler/metin-yolu/harf.py` → `harf.json` |
| Stress contrast C and D | `python3 olcumler/metin-yolu/vurgu_c.py` → `vurgu_c.json` |
| Rule marks against heard prominence | `python3 olcumler/metin-yolu/heard_vs_rule.py .` |
| Aspiration (VOT) analysis | `python3 olcumler/gizli-sesler/vot_analysis.py kaggle/aspiration-vot-{a,b,c}/cikti` |
| Ear scores with single spelling v2 | `python3 olcumler/sinav-yazim-v2/score_v2.py` |
| Training and reading jobs | `kaggle/s31-kurmanci-token`, `kaggle/s32-soru`, `kaggle/s33-voice-2gpu`, `kaggle/s34-voice-v2`, `kaggle/s34ab-stress`, `kaggle/s34-oku`, `kaggle/s34ab-oku` |
| Pre-registrations and results | `olcumler/kurmanci-token.md`, `s32-soru.md`, `metin-yolu-denetim-12kasim.md`, `embedding-kurmanci-denetim-13kasim.md`, `s34-ses-harf-yolu-v2.md`, `embedding-fable-denetim-14kasim.md`, `s34ab-vurgu-ozelligi.md`, `vurgu-olcum.md`, `gizli-sesler-soluk-olcumu.md` |
