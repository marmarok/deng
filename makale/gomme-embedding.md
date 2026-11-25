# Residual Grapheme Embeddings for Northern Kurdish TTS on a Frozen Multilingual Backbone: Pre-registered Evaluation, Limitations and a Practitioner's Guide from the Deng Project

14 November 2026 · Deng Project, working draft

*Authors, affiliations, ORCID iDs and the corresponding author: to be added by the Deng team. Working draft; every number is as of 14 November 2026.*

## Abstract

Multilingual text-to-speech (TTS) models now approach human quality in the languages they were trained on, yet most languages are missing from their vocabularies. We study the first layer such a model meets, the text embedding, when a frozen 2-billion-parameter TTS model (VoxCPM2) is adapted to Northern Kurdish (Kurmanji), a Latin-script language it has never seen. Its byte-pair vocabulary (73,440 pieces) cuts Kurmanji words at meaningless points and scatters single letters over hundreds of frozen pieces. We replace it with a grapheme path that reuses the model's own single-character tokens and adds a trainable residual table (41 × 2,048 values) to the frozen embeddings, trained together with low-rank adapters. Six text formats, each fixed by token fingerprints, record the design steps: a leading boundary token, a sentence-initial question token, spelled-out acronyms, the digraph xw written as two letters, and a compositional stress feature. Every comparison was pre-registered and scored with three inference seed sets, a Kurmanji speech recogniser and a pitch-based question judge, with paired bootstrap intervals. On one narrator's audiobook (7,586 utterances, 33.5 h), the grapheme path lowered the character error rate from 3.62% to 2.61% under the same recipe (−1.01 points, 95% CI \[−1.51, −0.53\]). The largest gains came on letters whose Kurmanji value differs from neighbouring languages: c 32.3% → 5.1%, x 23.1% → 3.7%, q 10.6% → 3.5%. Geometry analyses explain the design rules: the base model's letter vectors are nearly orthogonal (mean cosine 0.09), and rows started from nothing were not learned at this scale. Question intonation stayed within the noise band (38.9% against 48.1%), and no listening test of these voices exists yet. We report every limitation and give a step-by-step guide for reuse, extension and replication.

**Keywords:** text-to-speech; Northern Kurdish; Kurmanji; low-resource languages; token embeddings; vocabulary adaptation; grapheme input; parameter-efficient fine-tuning; lexical stress; pre-registration

**Highlights**

- Stock BPE splits Kurmanji words at meaningless points over frozen embeddings
- A 41-row residual table on frozen letter embeddings cut CER from 3.62% to 2.61%
- Rows initialised from nothing were not learned; new symbols must start as letters
- Pre-registered rules, three seed sets and paired bootstrap guard every decision
- Question intonation and human naturalness remain open; all limits are reported

## 1 Introduction

In the languages they were trained on, large text-to-speech (TTS) systems now produce speech that listeners find hard to tell from recordings (Tan et al., 2024; Wang et al., 2023; Anastassiou et al., 2024; Du et al., 2024a; Chen et al., 2025). Most of these systems share one design: a language model reads text tokens from a subword vocabulary and predicts acoustic representations. VoxCPM2, the base model of this study, was trained on more than two million hours of speech in 30 languages (VoxCPM Team, 2026; Zhou et al., 2025). Kurdish is not one of them.

When such a model meets a new language, the text vocabulary becomes a bottleneck that is easy to overlook. Subword vocabularies are fitted to the training languages (Sennrich et al., 2016; Kudo and Richardson, 2018). Text in other languages is split into more pieces, rarer pieces and pieces that mean less (Rust et al., 2021; Petrov et al., 2023; Ahia et al., 2023). Parameter-efficient fine-tuning usually keeps the embedding matrix frozen (Hu et al., 2022), so the adapters deeper in the network must learn what every piece sounds like. In classification a poor segmentation costs some accuracy. In TTS every piece must finally become sound, so a piece whose value is wrong is heard.

Northern Kurdish (Kurmanji) shows the problem clearly. It is written in a Latin alphabet of 31 letters, plus the compound sound xw, which the grammars count as one unit (Thackston, 2006; Tan, 2011; Karabax, 2013). The spelling is close to the sound but leaves several contrasts unwritten: aspirated against plain ç, k, p, t, and tap against trill r. Lexical stress separates forms that are spelled alike: hatin is 'they came' with stress on the first syllable and 'to come' with stress on the last. Yes/no questions can be marked by intonation alone. The language is a dialect continuum, usually grouped into five regions (Öpengin and Haig, 2014; Haig and Öpengin, 2018). Speech technology for Kurmanji has advanced mostly on the recognition side. A fine-tuned Whisper model reaches 5.7% character error on read speech (Abdullah et al., 2024), and massively multilingual recognisers cover the language (Pratap et al., 2024; Omnilingual ASR Team, 2025). Published Kurdish TTS research concerns mainly Central Kurdish, Sorani (Ahmad and Rashid, 2024). We found no study of how the text input of a large pretrained TTS model should be adapted to Kurmanji.

The Deng project (*deng* is Kurdish for 'voice' or 'sound') has two goals. The first is a voice that native listeners cannot tell from a native speaker: they should pick the human in at most 55% of trials, with no significant difference in rated naturalness. The second is a recogniser that understands everyday conversation. The project works under three constraints. It has no budget, so it trains on free cloud GPUs (two 16 GB NVIDIA T4 cards per session, a weekly quota). It uses only permissioned or openly licensed data. Every decision that shapes later steps is pre-registered: the decision rule is written before the result is seen. This paper covers one component of the voice from end to end: the text embedding path, which we call the Deng embedding.

In brief, the stock vocabulary of 73,440 pieces cut Kurmanji words at points that mean nothing and spread single letters over hundreds of frozen pieces. We replaced it with a grapheme path that reuses the model's own single-character tokens and adds a small trainable residual table to the frozen embeddings. Small structural tokens then fixed specific failures: the first word of a sentence, the start of a question, spoken acronyms. Two attempts to add new symbols failed in instructive ways, a stress sign and a dedicated token for xw. They led to a rule about initialisation and to a compositional design for features the spelling does not show. Under the same recipe the grapheme path read 1.01 character-error points more clearly than the stock path, with the largest gains on the letters whose Kurmanji value differs from neighbouring languages. Question intonation did not improve, and no listening test of these voices has been run yet.

The paper makes six contributions:

1. **A measured diagnosis** of how a 30-language BPE vocabulary treats Kurmanji. On 8,000 utterances it used 3,334 distinct pieces, 49% of them at most five times, and spread the letter c over 2,253 pieces.
2. **The residual grapheme path:** a 41-row trainable table added to the frozen embeddings through a forward hook (83,968 parameters, about 0.004% of the model), structural tokens, and versioned text formats fixed by token fingerprints. A compositional mechanism carries stress and, later, the sounds the spelling hides.
3. **An initialisation rule** supported by three independent trials and by geometry measurements: in runs of this size, rows that start from nothing are not learned, while letters work because they correct a vector the model already trained.
4. **A pre-registered evaluation protocol** for low-resource TTS on free hardware: recogniser-based character error with a human floor, per-letter and per-position analysis, a question-intonation judge with a threshold-free discrimination score, three inference seed sets and paired bootstrap intervals.
5. **Results with their uncertainty:** −1.01 points of character error under the same recipe; xw errors from 7.2% to 0.5%; first-word errors in statements from 8.5% to 3.2%; question intonation within the noise band.
6. **An open account of weaknesses**, an improvement roadmap and a practitioner's guide for three kinds of reader: those who will use the path as it is, those who will build on it, and those who start from nothing for another language.

Section 2 reviews the most-cited embedding work of recent years and the literature closest to our problem. Section 3 describes the language and the data, Section 4 the embedding path, and Section 5 the training infrastructure. Section 6 gives the evaluation and results. Sections 7 and 8 cover weaknesses and the roadmap, Section 9 is the practitioner's guide, Section 10 treats ethics and data rights, and Section 11 concludes.

## 2 Related work

The most-cited embedding research of the last decade studies embeddings as outputs: vectors that stand for words, sentences, images or speakers and are compared with one another. The Deng embedding is something else: the input table of a generative speech model, in a language that model never saw. Only a few threads of the literature speak to that case directly. Table 1 sets out what the most-cited work does and does not teach it; Sections 2.2 to 2.7 review the closer work.

### 2.1 The most-cited embedding work and what it teaches here

We searched OpenAlex on 14 November 2026 for the most-cited works in five families: word and contextual embeddings, sentence and retrieval embeddings, multimodal and speech embeddings, tokenisation, and the training of new vectors inside frozen models. Counts are OpenAlex cited-by counts of the most-cited record of each work. Google Scholar reports higher numbers, and recent preprints are undercounted. Supplementary Table S1, in the second tab, lists every work we looked up, with its count and DOI.

**Table 1.** The most-cited embedding works, by cited-by count, and what each teaches the Deng embedding.

| Work | Venue | Cited by | Core idea | Lesson for the Deng embedding |
| --- | --- | --- | --- | --- |
| Vaswani et al. (2017), Transformer | NeurIPS | 136,382 | Token and position embeddings feed self-attention | Every text token of VoxCPM2's language model enters through one row of such a table; no later layer sees the spelling |
| Devlin et al. (2019), BERT | NAACL | 77,009 | Masked-language pretraining over a fixed WordPiece vocabulary | The vocabulary is fixed at pretraining; a language added later inherits its cuts |
| Mikolov et al. (2013a, 2013b), word2vec | arXiv; NeurIPS | 37,148; 26,128 | Vectors trained to predict context; offsets carry relations | Geometry follows the training objective. Nothing makes letters line up by sound, and in VoxCPM2 they do not (Section 6.6) |
| Pennington et al. (2014), GloVe | EMNLP | 34,805 | Factorised global co-occurrence counts | The same lesson as word2vec |
| Radford et al. (2021), CLIP | ICML | 19,271 | Contrastive alignment of two modalities | A text–speech contrastive objective could teach letter rows their sound; untested here |
| Reimers and Gurevych (2019), Sentence-BERT | EMNLP | 15,169 | Siamese fine-tuning for sentence vectors | A pretrained network adapts to a new objective with little data, as our table and adapters do |
| Hu et al. (2022), LoRA | ICLR | 14,533 | Low-rank updates to frozen weights | The adapters our table trains with; the table itself is a full-rank update on 41 rows |
| Peters et al. (2018), ELMo | NAACL | 13,416 | Contextual vectors over a character-convolution input | Character input can feed a strong model |
| Bojanowski et al. (2017), fastText | TACL | 11,074 | A word is the sum of its character n-gram vectors | Rare and unseen words need sub-word units; our path goes down to single letters |
| Conneau et al. (2020), XLM-R | ACL | 7,607 | One SentencePiece vocabulary of 250k pieces for 100 languages | Vocabulary capacity is shared; a language outside training gets what is left |
| Sennrich et al. (2016), BPE | ACL | 5,519 | Merge the most frequent symbol pairs into subwords | Merges follow frequency in the training languages, not the morphemes or sounds of a new one |
| Lester et al. (2021), prompt tuning | EMNLP | 4,980 | Train a few input vectors; freeze the model | Vectors that start from real vocabulary embeddings beat random ones; our rows behave the same way |
| Hsu et al. (2021), HuBERT; Baevski et al. (2020), wav2vec 2.0 | TASLP; NeurIPS | 3,561; 3,140 | Self-supervised speech representations | The recogniser that scores our voices descends from this family; its errors enter our metric (Section 7.1) |
| Snyder et al. (2018), x-vectors | ICASSP | 2,809 | Fixed-length speaker embeddings | Needed when the voice becomes multi-speaker, and to verify that a voice is the one that was consented to |
| Chen et al. (2024), M3-Embedding; Zhang et al. (2025), Qwen3 Embedding | Findings of ACL; arXiv | 2,253; 2,134 | Multilingual embedders built from large models and curated data | Quality follows data; for Kurmanji speech the binding constraint is also data |
| Gal et al. (2023), textual inversion | ICLR | 2,047 | Learn one new token vector with the generator frozen | A new vector needs a larger step than fine-tuned weights; the reason format v4 multiplies its mark row |
| Muennighoff et al. (2023), MTEB | EACL | 1,520 | One benchmark over 8 task types and 112 languages | Kurmanji TTS has no public benchmark; our locked exam sets could seed one |

Three lessons recur. First, an embedding's geometry reflects the objective that trained it, so one cannot assume that a TTS model's letter vectors are arranged by sound; this has to be measured. Second, the strongest results in every family come from data scale and curation; architecture tricks do not replace missing data. Third, the work that trains new vectors inside frozen models agrees that where a vector starts matters, a lesson our own trials repeated at some cost.

### 2.2 Tokenisation and its cost for unseen languages

Byte-pair encoding learns its merges from symbol frequency in the training text (Sennrich et al., 2016). SentencePiece makes tokenisation reversible and language-independent, with BPE or unigram models (Kudo and Richardson, 2018; Kudo, 2018). Either way the vocabulary is fitted to the training mix. Rust et al. (2021) showed that the quality of a multilingual model's tokenizer for a language predicts the model's performance in it, and that a dedicated tokenizer recovers part of the gap. Petrov et al. (2023) found that the same text can need up to 15 times more tokens in one language than in another; Ahia et al. (2023) showed what such differences cost the users of commercial models. Byte- and character-level models remove the vocabulary at the price of longer sequences (Xue et al., 2022; Clark et al., 2022; see Mielke et al., 2021, for a history). Speech adds a twist. In our case the stock pieces were not too many, 94 per utterance against 215 letters; they were wrong in kind. Their boundaries fell inside Kurmanji morphemes, and the sound of a letter had to be learned again in every piece that contained it.

### 2.3 Adapting vocabularies and initialising new embeddings

Artetxe et al. (2020) showed that a monolingual model transfers to a new language when only a new embedding matrix is learned and the transformer body stays frozen. This is the closest text analogue of our setting. For multilingual encoders, vocabulary augmentation and continued pretraining help low-resource languages (Chau et al., 2020; Wang et al., 2020; Ebrahimi and Kann, 2021; Imani et al., 2023), and unseen scripts need new tokens initialised from lexical overlap (Pfeiffer et al., 2021). Several methods initialise new subword rows from existing ones: as similarity-weighted means through bilingual static vectors (WECHSEL; Minixhofer et al., 2022), from overlapping tokens weighted in an auxiliary fastText space (FOCUS; Dobler and de Melo, 2023), through factorised multilingual vectors (OFA; Liu et al., 2024), or with a hypernetwork that predicts rows for any tokenizer (Minixhofer et al., 2024). Downey et al. (2023) found that simple re-initialisation from script-wise sub-distributions of the existing rows rivals FOCUS. Other work changes how rows are trained: periodic resetting makes them easier to relearn (Chen et al., 2023), a shallow aligned mini-model learns them cheaply (Marchisio et al., 2023), and staged freezing expands a vocabulary for Korean (Kim et al., 2024). Inside frozen generators, new vectors are trained as soft prompts (Lester et al., 2021; Li and Liang, 2021) or as new words (Gal et al., 2023).

Two observations frame our contribution. Every method above starts new rows from something the model already knows, and random initialisation is the weakest baseline throughout. Our trials reached the same conclusion in speech, and our geometry measurements show why the usual neighbour heuristics would not help in this TTS model: its letters are not arranged by sound. Further, none of these studies concerns the input of a speech generator, where a wrong row is heard rather than averaged away.

### 2.4 Text representations in neural TTS

Early end-to-end systems read characters (Wang et al., 2017; Shen et al., 2018); FastSpeech 2 and VITS read phonemes (Ren et al., 2021; Kim et al., 2021). Taylor and Richmond (2019) analysed how character-input models learn pronunciation. Multilingual systems share one input space: UTF-8 bytes (Li et al., 2019), shared phonemes or characters with an adversarial speaker loss (Zhang et al., 2019), encoder parameters generated from a language embedding (Nekvinda and Dušek, 2020), or raw characters for languages without a pronunciation front end (Casanova et al., 2022). For unseen languages, phonological or articulatory features let a model read a new phoneme set (Staib et al., 2020; Lux and Vu, 2022; Lux et al., 2024), and phone mapping chooses which source phonemes stand in for target ones (Do et al., 2023). Pretrained text encoders add context and prosody: BERT embeddings (Hayashi et al., 2019), joint phoneme–grapheme pretraining (Jia et al., 2021), phoneme-level BERT (Li et al., 2023), multilingual phoneme BERT (Nguyen et al., 2023), and unsupervised text pretraining for zero-shot languages (Saeki et al., 2023). Large language-model-based systems condition on phonemes (Wang et al., 2023; Shen et al., 2024; Ju et al., 2024), on characters (Chen et al., 2025) or on the BPE vocabulary of their language-model backbone (Du et al., 2024b; Zhou et al., 2025). Reusing a backbone's vocabulary brings its text knowledge for the languages it covers; for a language it does not cover, that vocabulary produces the fragmentation studied here. Rule-based grapheme-to-phoneme conversion exists for Kurmanji (Epitran's kmr-Latn; Mortensen et al., 2018), and ByT5 models convert many languages (Zhu et al., 2022). No such converter writes the contrasts Kurmanji spelling leaves out (Section 3.1).

### 2.5 Prosody, stress and homographs

Learned prosody embeddings capture style without labels (Wang et al., 2018; Skerry-Ryan et al., 2018), and explicit pitch prediction gives control (Łańcucki, 2021). Lexical stress is usually settled before the model: pronunciation dictionaries mark the stressed vowel, and homographs are resolved from context (Gorman et al., 2018). Kurmanji has neither a stress-marked pronunciation lexicon nor a homograph disambiguator. Deng's stress rules come from two grammars (Tan, 2011; Karabax, 2013) and were tested on speech before use (Section 4.7).

### 2.6 Kurdish language technology

Kurdish varieties are written in a Latin script (Kurmanji) and an Arabic-based script (Sorani), and text processing must handle both scripts and dialect variation (Hassani, 2018; Ahmadi, 2020). Static word vectors exist for Kurmanji and Sorani (Grave et al., 2018). Kurmanji speech resources are recent. Common Voice (Ardila et al., 2020) held 77.5 validated hours from 540 speakers in release 27 by our count. FLEURS-Kobani extends FLEURS (Conneau et al., 2023) to Kurmanji (Jaff and Mohammadamini, 2026), and pseudo-labelled broadcast audio supports Kurdish speech translation (Mohammadamini et al., 2025). Whisper fine-tuned on about 68 hours reaches a word error of 10.5% and a character error of 5.7% (Abdullah et al., 2024), and massively multilingual recognisers cover Kurmanji (Pratap et al., 2024; Omnilingual ASR Team, 2025). Central Kurdish has a recognition corpus and lexicon (Veisi et al., 2022) and an end-to-end TTS system rated at a mean opinion score of 3.94 (Ahmad and Rashid, 2024). MMS includes a Kurmanji TTS voice under a non-commercial licence (Pratap et al., 2024). Dialect geography and the structure of Kurmanji are described by Öpengin and Haig (2014) and Haig and Öpengin (2018), and the grammar by Thackston (2006), Tan (2011) and Karabax (2013).

### 2.7 Evaluation practice

Zero-shot TTS papers report intelligibility as the word or character error of a recogniser (e.g., Wang et al., 2023; Anastassiou et al., 2024; Chen et al., 2025), and naturalness through listening tests on a five-point scale (ITU-T, 1996) or predictors such as UTMOS (Saeki et al., 2022). Human-level quality has been defined as no significant difference from recordings in comparative listening (Tan et al., 2024). Listening tests need more listeners than they usually get (Wester et al., 2015) and careful design (Kirkland et al., 2023). Bootstrap resampling gives confidence intervals for error rates (Efron and Tibshirani, 1993; Koehn, 2004; Bisani and Ney, 2004). Training seeds and data order can move results enough to reverse a conclusion (Reimers and Gurevych, 2017; Dodge et al., 2020). Pre-registration, fixing the hypothesis and the analysis before the data are seen, limits flexible analysis (Nosek et al., 2018) and has been proposed for NLP (van Miltenburg et al., 2021). Pitch is tracked with pYIN (Mauch and Dixon, 2014), and phonetic measures come from Praat through Parselmouth (Jadoul et al., 2018).

### 2.8 Where this work stands

**Table 2.** Ways to give a pretrained TTS model text in a language it has not seen.

| Approach | Examples | Needs | Tokens per utterance | New trainable rows | Main risk | In Deng |
| --- | --- | --- | --- | --- | --- | --- |
| Keep the stock subword vocabulary; train adapters only | Most LoRA fine-tunes | Nothing | Short (94.2) | None | Pieces carry wrong or scattered sound values in frozen rows | Baseline voices S28 and S33 |
| Add new subword tokens | Chau et al. (2020); Wang et al. (2020); Kim et al. (2024) | Tokenizer training and an initialiser | Short | Thousands | New rows start far from anything the model knows | Not used |
| Phonemes through grapheme-to-phoneme conversion | Ren et al. (2021); Wang et al. (2023); Do et al. (2023) | A converter or lexicon | Medium | A phoneme table or a mapping | Hidden contrasts still need a lexicon; converter errors | Roadmap (Section 8) |
| Bytes or characters with a new table | Li et al. (2019); Xue et al. (2022) | Nothing | Long | The whole table | Every symbol is learned from scratch | Not used |
| Phonological or articulatory features | Staib et al. (2020); Lux and Vu (2022) | A feature inventory | Medium | A projection | Needs a phoneme layer first | Not used |
| Reused single-character tokens plus a residual table (this work) | Sections 4 to 6 | Every letter present as a token | Long (215.3, ×2.29) | 41, plus 8 mark rows in v4 | Longer sequences; unwritten contrasts still missing | Standard since 13 November 2026 (format v3) |

To our knowledge, after the searches above, this is the first study of the text-embedding layer of a large pretrained TTS model adapted to a language outside its vocabulary, and the first published analysis of how Kurmanji text should enter such a model.

## 3 Language and data

The Deng voice is trained on 33.5 hours of one narrator reading published Kurmanji prose, and it is judged on locked sentence sets that never enter training. This section describes the parts of Kurmanji that matter for a text path, then the corpus, the text normaliser and the exam material.

### 3.1 What Kurmanji spelling writes and what it leaves out

Kurmanji is written in a Latin alphabet of 31 letters: a b c ç d e ê f g h i î j k l m n o p q r s ş t u û v w x y z. It has eight vowels, five long (a ê î o û) and three short (e i u), and 23 consonant letters. The grammars add one compound sound, xw /xʷ/, written with two letters and counted as one unit (Tan, 2011; Karabax, 2013). The spelling is close to the sound, with the exceptions listed in Table 3.

**Table 3.** Letters whose value matters for the text path. Values follow Haig and Öpengin (2018) and Thackston (2006).

| Spelling | Value | What the spelling hides | Status in Deng |
| --- | --- | --- | --- |
| c, j, x, q | /dʒ/, /ʒ/, /x/, /q/ | Nothing; but neighbouring languages give these letters other values | The largest gains of the grapheme path (Section 6.3) |
| xw | /xʷ/ | One sound written with two letters | Written as two tokens since format v3 |
| e ê, i î, u û | /ɛ/ /eː/, /ɪ/ /iː/, /ʊ/ /uː/ | Nothing | Separate rows; the remaining ê → e confusions are mostly the recogniser's |
| ç, k, p, t | /tʃʰ/ or /tʃ/, /kʰ/ or /k/, /pʰ/ or /p/, /tʰ/ or /t/ | Aspiration is phonemic (kar, ker, ter, par each spell two words) but never written | Not represented; the mechanism is ready (Section 4.7) |
| r, rr | /ɾ/, /r/ | The trill is written rr only where the writer chooses; a word-initial r is trilled | rr is kept by the normaliser |
| h, x, vowel onset | /h/ or /ħ/, /x/ or /ɣ/, none or /ʕ/ | Not phonemic and not written | Not represented |
| l | /l/ or /ɫ/ | Dark l; not phonemic | Nothing to do |

Stress is lexical. In the grammars it falls by default on the last syllable of nouns; the plural endings -an and -ên take it, while the case endings -ê, -a and -ek leave it on the stem; negation prefixes carry it; and an infinitive is stressed on its last syllable where the past form of the same verb is stressed on its stem (Tan, 2011; Karabax, 2013). Words spelled alike therefore differ in stress: hatin 'they came' against hatin 'to come'. The grammarians themselves warn that stress is irregular and the evidence thin, so Deng tested the rules on speech before using any of them (Section 4.7).

A yes/no question can be marked by intonation alone. In Common Voice readings, the pitch of a Kurmanji yes/no question peaks about 0.3 s before the end and does not fall to the floor, while a statement falls by about three semitones over its last second. Questions that carry the particles ma or gelo need not rise, and questions with a question word often fall. The project's question judge (Section 6.1) builds on these measurements.

Kurmanji is a dialect continuum. Öpengin and Haig (2014) group it into five regions: south-eastern (Hakkari, Duhok), southern (Mardin, Batman, Hasakah), northern (Muş, Ağrı, Erzurum), south-western (Adıyaman, Antep, Afrin, Kobanê) and north-western (Maraş, Malatya, Sivas). The project targets the standard written language of books and broadcasting, and records each speaker's home region, dialect group and register as labels. Text is never respelled to match a dialect: two spellings of one word would split its row into two half-learned rows.

### 3.2 Training corpus

The voice is trained on a permissioned audiobook: one professional narrator reading published non-fiction prose in standard Kurmanji, from long archive recordings aligned to the printed books. The permission covers use inside the project. The voice imitates a real person, so neither the voice nor its training audio is published, and the source is referred to by a code name in every shared document.

Recordings were cut into sentence-length segments and matched to the printed text, and each segment's recogniser transcript was compared with the print. A segment entered training only if all of the following held: it is a whole sentence, opening with a capital and closing with sentence-final punctuation; it lasts 2 to 20 s; the recogniser's transcript differs from the print by at most 8% of characters; it contains no digits; it does not come from a test page or a duplicated archive file; and it is not one of the 254 locked exam sentences. This left **7,586 utterances, 33.5 hours and 1.45 million letters**, decoded to 16 kHz mono.

A census of the training text shows what a text path must handle. The most frequent letters are e (11.9% of letters), a (9.6%) and i (9.4%); the rarest are q (0.44%), x (0.43%) and f (0.41%), with xw at 0.57%. No letter outside the alphabet occurs: ḧ, ẍ and ł never appear. All 290 word-internal apostrophes join an abbreviation to a case suffix (as in TV’yê), and the 465 word-initial ones are quotation marks; none marks a pharyngeal. The trill is written where the authors chose to write it: pirr appears 246 times, pirraniya 51, pirranî 38, vebirrî 20 and hûrrî 12. Questions are rare. Only 73 of the 7,586 utterances end in a question mark; in the wider pool of 16,040 segments, 127 do (0.8%).

### 3.3 Text normalisation

Every text, for training and for reading, passes through the project's normaliser before tokenisation. It does three things.

1. **It restores missing circumflexes** (ê, î, û), which writers often drop. A lattice over the candidate spellings of each word is scored with bigram counts from the CC0 sentences of Common Voice (weighted ten times) and word counts from Kurdish Wikipedia; an unknown word is split into a known stem and a suffix. On 1,699 held-out sentences (11,050 words) with their circumflexes removed, word accuracy rose from 60.8% to 95.9%, and 92.9% of circumflexed words came back. On correctly spelled text it changed a word in 16 of the 1,699 sentences, mostly fixing real spelling errors. A third of the remaining errors involve pairs in which both spellings are words (we/wê, te/tê, ji/jî, de/dê), which only meaning can settle.
2. **It applies the standard spelling** îy + vowel → iy + vowel (Sûrîyê → Sûriyê). The sound is the same; a recogniser that learned the older spelling had lost points on broadcast speech.
3. **It writes numbers, times, dates, percentages and abbreviations as words.** The voice reads words, not digits: 1986 becomes hezar û neh sed û heştê û şeş. Choices the code is unsure of (for example, yanzdeh or yazdeh for eleven) are listed for language editors.

The grapheme tokenizer adds its own normalisation on top (Section 4.3). A separate canonical form, which maps spelling variants that the grammars treat as one word to a single form, serves only as a secondary score in analysis (Section 7.1).

### 3.4 Exam material

All exam sets were fixed before the experiments reported here, and none of their sentences enters training.

- **Intonation set** (257 sentences). Statement–question pairs with identical words (Tu hatî. / Tu hatî?), yes/no questions marked by intonation alone, questions with ma or gelo, questions with a question word, and short dialogue lines, drawn mostly from the CC0 sentence collection of Common Voice. About 63 questions and 143 statements are scored by the question judge in each reading. Character error is computed on the 253 sentences without numbers.
- **Progress sentences** (10). Conversational sentences far from the book domain, used to detect over-fitting to the narrator's text.
- **Three listening sentences**, read in every run for quick listening checks.
- **Stress pairs** (26). Thirteen verbs in two frames each; the final verb is read with its stress mark on the first or on the last syllable (Section 6.5).
- **Human floor.** The recogniser's errors on 4,000 of the narrator's own recorded utterances, per letter. It tells how much of a voice's error the recogniser would make on a human.

## 4 The Deng text embedding

The Deng embedding feeds VoxCPM2 one token per letter and adds a small trainable correction to the frozen embedding of each letter. This section describes the base model, the diagnosis that motivated the change, the grapheme path, the residual table, the structural tokens, the versioning that keeps weights and text in step, and the compositional marks that carry stress. Figure 1, at the end of the section, shows where each part sits.

### 4.1 Base model

VoxCPM2 is a TTS model of about 2 billion parameters built on a MiniCPM-4 language-model backbone (VoxCPM Team, 2026; MiniCPM Team, 2025). Its authors describe a hierarchical pipeline: a local encoder of audio latents, a text–semantic language model, a residual acoustic language model and a local diffusion transformer that renders acoustic detail (Zhou et al., 2025). Speech is represented by continuous latents of an audio variational autoencoder that takes 16 kHz audio and returns 48 kHz. The language model runs at 6.25 steps per second, so one step covers 0.16 s of audio. The model calls itself tokenizer-free, which refers to the absence of discrete speech tokens. Text is still tokenised, by the backbone's BPE vocabulary of 73,440 pieces, and its 2,048-dimensional embedding table stays frozen during fine-tuning. The vocabulary holds 976 unused reserved tokens. VoxCPM2 was trained on more than two million hours of speech in 30 languages, none of them Kurdish, and is released under the Apache-2.0 licence. All Deng voices are trained with the authors' own fine-tuning script (package voxcpm 2.0.3), with LoRA adapters on the language model and the diffusion transformer.

### 4.2 Diagnosis of the stock path

We tokenised 8,000 transcribed Kurmanji utterances from the project's broadcast pool with the stock tokenizer. It used 3,334 distinct pieces, 1,629 of them (49%) at most five times. It cut words at points that are neither morpheme nor syllable boundaries: hatin became ▁h|atin, and dixwazim became ▁d|ix|w|az|im. The letter w occurred inside 537 different pieces and c inside 2,253, while xw never formed a piece of its own. An utterance took 94.2 pieces on average. With the embedding table frozen, the adapters had to learn the Kurmanji value of each letter separately inside every piece that contains it, from data in which half of the pieces occur at most five times.

### 4.3 The grapheme path

The Deng tokenizer writes text as a sequence over a fixed alphabet of 41 symbols: the 31 letters, the word boundary ▁, seven punctuation marks (. , ? ! : ; -) and two legacy symbols kept so that older weights still load, a unit token for xw and a stress sign. Every letter, ▁ and every punctuation mark already exists as a single-character token in the VoxCPM2 vocabulary, so the path adds no tokens: the checkpoint's vocabulary and weights are untouched, and the two legacy symbols occupy reserved slots. On the same 8,000 utterances the path used 35 of its 41 symbols and 215.3 tokens per utterance, 2.29 times as many as the stock path.

Before mapping characters to symbols, the tokenizer applies seven steps in a fixed order:

1. Unicode NFC composition.
2. **Acronyms.** A capitalised name of two to five letters without a vowel is spelled with the Kurmanji letter names, as speakers say it: TV becomes teve and SMSê becomes semesê. A name with a vowel, such as UNESCO, is read as a word, and Roman numerals are left alone. Checked against what the recogniser heard in the narrator's 7,586 utterances, the rule changed 209 of them and moved the text closer to the speech in 199 and further away in 6, where the narrator had skipped the name.
3. **Typographic folding.** Dashes become a hyphen, an ellipsis becomes three full stops, quotation marks and brackets are removed, and Arabic punctuation (؟ ، ؛) becomes Latin.
4. **Kurmanji lower case.** İ, I and ı all become i.
5. **Foreign letters** are read as the nearest Kurmanji letter (ü → û, é → ê, ö → o, ẍ → x, ḧ → h, ł → l), or else as their base letter after Unicode decomposition (ř → r).
6. **Anything else** (a digit the normaliser missed, a slash, another script) breaks the word and is counted, never silently dropped. An earlier version glued the two sides together and turned kesekê/kesekî into one word in 7 training utterances.
7. **Whitespace** becomes a single ▁, and a trailing ▁ is removed.

The three formats used most in this paper turn the same two sentences into these sequences (v4 is shown with every mark the rules give):

```text
s32  e w ▁ d u h ▁ h a t i n , ▁ l ê ▁ h a t i n ▁ n e ▁ h ê s a n ▁ b û .
v3   ▁ e w ▁ d u h ▁ h a t i n , ▁ l ê ▁ h a t i n ▁ n e ▁ h ê s a n ▁ b û .
v4   ▁ e w ▁ d ˈu h ▁ h ˈa t i n , ▁ l ê ▁ h a t ˈi n ▁ n e ▁ h ê s ˈa n ▁ b ˈû .

s32  ? t u ▁ k e n g î ▁ h a t î ? ▁ m i n ▁ l i ▁ t v y ê ▁ d î t .
v3   ▁ ? ▁ t u ▁ k e n g î ▁ h a t î ? ▁ m i n ▁ l i ▁ t e v e y ê ▁ d î t .
```

In the first sentence ('They came yesterday, but coming was not easy') the two forms of hatin receive their stress on different syllables in v4: the past form on its stem, the infinitive on its last syllable. In the second ('When did you come? I saw it on TV'), v3 opens the question with its own question token and spells the acronym as it is said.

### 4.4 The residual table

Let E be the frozen embedding table of VoxCPM2, with rows of dimension d = 2,048, and let ρ(t) be the alphabet row of token t, or nothing if t is outside the alphabet. The trainable table Δ has 41 rows. The model sees, for every token,

```latex
\tilde{e}(t) \;=\; E_{t} \;+\; \mathbb{1}\!\left[\rho(t)\neq\varnothing\right]\,\Delta_{\rho(t)}, \qquad \Delta \in \mathbb{R}^{41\times 2048}
```

A forward hook on the embedding module adds the row to the module's output, so the same addition happens in training and whenever the model embeds text while reading; E itself is never modified. The parameter's name begins with lora\_, so VoxCPM's own checkpoint code saves it with the LoRA weights and loads it back by name. The table has 41 × 2,048 = 83,968 parameters, about 0.004% of the model.

Every letter, boundary and punctuation row starts at zero, so at step 0 the grapheme path feeds the model exactly its own single-character embeddings. The two legacy rows sit in reserved slots the model never trained, whose embeddings have a norm of 0.0002 against 1.93 for a letter. The xw row starts at (E\_x + E\_w)/2 − E\_xw, so the token begins as the mean of x and w. The stress sign starts as a fixed random direction scaled to a tenth of the mean letter norm, after an earlier start at full letter length failed (Section 6.4).

The table is trained jointly with the LoRA adapters (rank 32, α = 32, no dropout) by the same optimiser: AdamW (Loshchilov and Hutter, 2019) with a learning rate of 10⁻⁴, weight decay 0.01, 100 warm-up steps, cosine decay (Loshchilov and Hutter, 2017) and gradient clipping at 1.0. The diffusion and stop losses have weight 1.0 each. To fit a 16 GB T4 card, every frozen weight except the audio autoencoder is kept in bfloat16.

On the rows it covers, a residual table is mathematically the same as fine-tuning those rows of E. The difference is practical. The checkpoint stays untouched and only 84 thousand numbers are saved; the hook can be checked after loading (Section 4.6); and the same table can be loaded into a model that marks some of its letters (Section 4.7).

### 4.5 Structural tokens

Three small tokens fix specific failures that the error analysis exposed (Section 6.4).

- **A leading boundary.** With letters, every word except the first follows a ▁, and the first word follows nothing. Its errors did not fall when the letter path arrived, and short first words such as tu, ez and ma got worse. From format v2 on, every text opens with ▁.
- **A question head.** A question also opens with ?, so the voice knows from the first sound that it is reading a question, instead of learning it from one token at the far end of a sequence 2.29 times longer than before. Format s32 put the ? directly before the first letter; from v2 on it is a word of its own, ? ▁. End marks that stand together (...? or ?!) close a single sentence, which counts as a question when a ? is among them.
- **Spelled acronyms**, as described in Section 4.3.

The opening ? and the closing ? share one row of the table. Section 7.3 discusses what that costs.

### 4.6 Keeping weights and text in step

A trained voice reads well only with the token sequence it was trained on, and nothing fails when the two differ: the model reads a mismatched sequence without complaint, only worse. Deng therefore treats the text path like a file format.

- **Named formats.** Each way of writing the sequence has a name (Table 4). A format with trained weights is never changed; a change gets a new name.
- **Fingerprints.** For every format, the test suite holds a 64-bit hash of its tokens on the 267 exam sentences and on the 7,586 training utterances. A code change that alters a trained format's tokens fails the tests.
- **A format file next to the weights.** Every save writes text\_path.json with the format's name, its options and the table layout. A reading job takes the format from that file and refuses a file that does not match the code.
- **A table check after loading.** VoxCPM's loader skips a key it does not find and says nothing. The check fails if fewer than half of the letter rows have moved from where the table started, because then the voice would read with untrained letters.
- **No silent fallback.** The tokenizer wrapper raises an error for any method it does not define, instead of passing the call to the stock BPE tokenizer.
- **Remote checks.** Before training, a job recomputes the fingerprint of its training text on the remote machine and compares it with the local one; with format v4 it also stops if the verb lexicon that the stress rules need is missing.
- **The length safety net.** VoxCPM retries a reading that exceeds 6 audio steps per text token. With 2.29 times as many tokens this net is 2.29 times looser, so production readings use 2.6 steps per token. Measured speech takes 0.46 steps per letter token on average, 0.9 at the 95th percentile and 1.0 at most.

**Table 4.** Text formats. Fingerprints are given for the exam sentences and the training utterances.

| Format | What it writes | Trained by | Fingerprints | Status |
| --- | --- | --- | --- | --- |
| s31 | Letters; xw as one token | S31 a, S32 a | 54dc269134e30242 / 42b59bc9728ec9a1 | Frozen |
| s31-stress | s31 plus a stress sign before the stressed vowel | S31 b | 5936abf9f12f5f36 / 18a0171d0c52fecd | Frozen; failed (Section 6.4) |
| s32 | s31 plus ? before a question's first letter | S32 b | 87e000d03e5ff022 / 78c7b2b834056191 | Frozen |
| v2 | Leading ▁, question head ? ▁, spelled acronyms; xw as one token | Never trained | 3f6662e97d586aff / e6ec6b9cada9cb2c | Kept for reference |
| v3 | v2 with xw written as two letters | S34 | adff7f06e7eaf578 / e979ce904540dd71 | Standard since 13 November 2026 |
| v4 | v3 plus stress as a mark on the vowel (half of the marks kept in training, gain 4) | S34 b, running | 20bc6e3a4d3e0329 / 50449359213f7105 | Candidate (Section 6.5) |

### 4.7 Compositional marks: stress, and the sounds the spelling hides

Stress decides meaning in Kurmanji, but the spelling does not show it. The first attempt, format s31-stress, placed a sign token before each stressed vowel. The sign lengthened the sequence, stood between a vowel and its consonant, and started as a random vector of full letter length; it moved little during training and made the voice less clear without moving stress (Section 6.4). Format v4 puts stress on the vowel instead. A stressed vowel becomes one token, in one of eight reserved slots, whose embedding is built from trained parts:

```latex
\tilde{e}(\acute{v}) \;=\; E_{v} \;+\; \Delta_{\rho(v)} \;+\; g\,M_{\mathrm{stress}}, \qquad M \in \mathbb{R}^{8\times 2048},\; M_{0} = 0,\; g = 4
```

The hook reads the frozen embedding at the plain vowel's index rather than at the reserved slot, whose row is not exactly zero. The vowel's own row Δ is shared by its stressed and unstressed forms, so marking does not split what the vowel has learned. With M at zero, a marked text is bit-for-bit identical to an unmarked one in half precision; this was tested with the real S34 table and the model's real rows. Weights trained without marks therefore load into v4 unchanged, and a v4 training run starts exactly where its v3 parent ended. The sequence keeps its length. Of the eight mark rows only the first is used; the other seven are reserved for the hidden sounds, so adding them later will not change the size of a saved table.

The gain g = 4 makes the model see four times the stored row, which gives the new row four times the effective step without touching the optimiser. It follows the practice of training a new vector at a larger step than the surrounding weights (Gal et al., 2023). It is a choice, not a measurement. Its worst case is bounded: with no signal at all, the row drifts to about 5% of a letter's length in a run of S34's size.

The marks come from rules taken from two grammars (Tan, 2011; Karabax, 2013), and the rules were tested on speech before any voice used them. The test aligned 31,452 words of the book narrator, 5,393 words of Common Voice and 2,337 words of spontaneous narrative (the DoReCo release of Multi-CAST texts, CC BY; Haig et al., 2022) with MMS forced alignment (Pratap et al., 2024; Hwang et al., 2023) and measured each vowel in Praat (Jadoul et al., 2018). The score P is the mean z-score of four cues of stress, namely duration, pitch, intensity and the share of energy above 500 Hz, each normalised against the same vowel elsewhere. Comparisons always hold the word form and its position in the phrase fixed, because all four cues also rise before a pause. A rule counted only if both main sources had at least 30 words; it was confirmed if both showed the expected direction with a difference above 0.1, and refuted if both showed the opposite.

**Table 5.** The stress rules tested on speech. Differences in P are given for the book narrator, Common Voice and, in brackets, spontaneous narrative. T and K give the page of the rule in Tan (2011) and Karabax (2013).

| Rule (source) | Measured difference | Verdict |
| --- | --- | --- |
| Plural -an, -ên take stress; case endings -ê, -a, -ek leave it on the stem (T79, K28) | +0.25 / +0.27 (+0.25) for two syllables; +0.11 / +0.17 for three | Confirmed |
| Negation prefix is stressed (T79) | Last minus first: −0.31 / −0.49 (−0.61) | Confirmed |
| -iya, -iyê do not take final stress (K26) | Last minus middle: −0.26 / −0.22 (−0.40) | Confirmed |
| The di- prefix is stressed (T80) | Last minus first: +0.73 / +0.29 (+0.31); the prefix is the weakest syllable | Refuted; the rule was changed |
| -ekî takes final stress (K28) | First minus last: +0.80 / +0.86 (+0.93) | Refuted; -ekî now behaves like -ek |
| Infinitive -in is final, past -in is on the stem (T79) | +0.10 inside a phrase, +0.24 before a pause; fewer than 30 Common Voice words | Open |
| Infinitive with a preverb (K28 against T79) | 14 and 5 words | Open |
| Subjunctive bi- (T80 against K28) | +0.38 and +0.81 / +0.06 and −0.11 (about 0) | Open; the sources disagree |
| Nouns take final stress by default (T78) | +0.16 / +0.05 inside a phrase | Not confirmed; kept as the default |

In the training text (2,000 utterances, 83 thousand words) 62.7% of words carry stress; the rest lean on a neighbour (prepositions, conjunctions, weak pronouns, the copula). Marks make up 10.9% of all tokens. The rules that place them are the default final stress of nouns (18.1% of words), the transparent endings (15.6%), monosyllables (7.2%), plurals (6.2%), -iya (3.1%), verb stems (2.9%), di- forms (2.9%), bi- forms (1.8%), negation (1.3%) and preverbs (1.0%). The most frequent rule is one that speech did not confirm. For this reason a training text keeps only half of the marks the rules give, chosen by a hash of the text and the word's position, so that every machine and every run makes the same choice. The voice can then learn that a mark means stress here while still reading unmarked words. At reading time any share of the words can be marked: all of them, none, or only those the writer marked by hand. A typed ˈ always overrides the rules for its word, so a writer can choose between hˈatin and hatˈin.

The same mechanism is ready for the sounds the spelling hides: plain against aspirated ç, k, p, t, the trill, and the pharyngeals. Each would be its letter plus a mark row, in slots reserved from 920 upwards. What is missing is a lexicon saying which word has which sound; the project has a seed list of 30 words, and a row trained on so few examples would learn nothing. No format uses these marks yet.

**Figure 1** (below) traces one sentence through the path, from raw text to audio, and marks which parts are frozen and which are trained.

&#91;embedded content: Figure 1 · the Deng text path inside VoxCPM2\]

*Figure 1.* Text passes through the normaliser and the grapheme tokenizer. At the embedding layer a hook adds the trained residual row, and in format v4 a mark row, to the frozen embedding of each letter; everything after that layer is VoxCPM2 with LoRA adapters. The safeguards keep the trained rows and the token sequence in step.

## 5 Training infrastructure and reproducibility

Every Deng voice was trained and evaluated in free Kaggle sessions with two 16 GB NVIDIA T4 cards, at no monetary cost. A full training run used about 7.3 hours on two cards, roughly 1 kWh at the cards' rated 70 W. The infrastructure exists for one purpose: every run must finish, record what it did and leave results that someone else can check.

### 5.1 Compute budget and the job gate

A free account has a weekly allowance of about 30 GPU hours, a session is stopped after a fixed maximum time, and a session's output is kept only if the session ends by itself. A job stopped by hand loses its output and its log entirely, which the project learned by losing them. A job therefore reaches Kaggle only through a gate that runs eight checks and sends nothing if any of them fails:

1. The job's own deadline is at most 8 hours (3 hours for a measurement run).
2. The deadline is checked inside every long loop (each training step, each sentence read, each scoring batch), not only between stages.
3. Every subprocess wait has a timeout; a process once waited forever.
4. Every network read has a timeout; a download once hung for about 12 hours.
5. A full GPU run carries step times measured by a finished short measurement run.
6. No other version of the same job is running.
7. A GPU is requested only if the job uses one.
8. Results are written to disk while the job runs, so that the result file is valid at any moment.

A ninth rule applies to new experiments: the expected gain written in the pre-registration must be at least twice the bootstrap half-width of the main measure. A run that cannot meet it needs a dated, reasoned exception, which the gate prints at every submission. S33, S34 and S34 a/b ran under such exceptions; Section 7.4 discusses what that implies.

### 5.2 Measurement runs and planning

Every new recipe first trains for 60 steps to measure the step time and the memory, and to confirm that the table trains and is saved. The full run's length is then computed from the measured step time, never from a guess. For S34 the measurement run gave 13.54 s per step on two cards with 8 utterances per step. The plan, at 14.2 s per step, was 1,680 steps: 1.77 epochs, or about 59 hours of audio. The run took 14.82 s per step and 7.25 hours, peaked at 12.7 and 11.9 GB of card memory, and lowered the training loss from 0.996 to 0.828.

The letter path costs time. Its sequences are 2.29 times longer, and a step took 13.3 s instead of 9.9 s on one card with 4 utterances per step (S31 a against S28), and 14.8 s instead of 10.2 s on two cards with 8 (S34 against S33). Training and the reading test no longer fit in one session, so they run as separate jobs.

### 5.3 Distributed training

The two cards run as two ranks under torch.distributed, each accumulating four utterances, so one optimiser step sees eight. Each rank gets its own random seed (the base seed plus 7,919 times the rank), and the data order is reseeded at each training round. The log must show both ranks training: an earlier recipe ran on two cards but used only one, and nothing warned about it. A checkpoint is written every 150 steps, about every 24 minutes, and the newest complete one is copied out of the session while training continues, together with its format file. At the end the job reads the table back from the saved file and fails if fewer than 16 of its rows are non-zero.

### 5.4 Reading jobs

Each voice reads the 270 exam sentences three times, with three seed sets. The seed of a sentence is 1,000 plus its number, plus 100,000 times the attempt number, plus an offset for the set (0, 7,000,000 or 14,000,000). Every voice therefore draws the same noise for the same sentence, and readings are paired across voices. A reading longer than 0.12 s per character plus 1.5 s is retried up to three times and the shortest attempt is kept; the guard is the same for every voice. The audio, produced at 48 kHz, is resampled to 16 kHz for scoring. The recogniser runs on both cards in batches of four while the question judge runs on the processor.

Two failures shaped these jobs. On 11 November 2026 the TLS certificate of the file server that distributes the recogniser's tokenizer expired; one reading job finished with no character error at all, and nothing in it noticed. Jobs now retry the download eight times, record how many clips were actually heard, and wait for the server instead of weakening certificate checks. Separately, listing thousands of output files hit the platform's rate limits, so each reading now packs its audio into a single archive.

### 5.5 Inspecting weights without downloading the model

The embedding rows analysed in Section 6.6 were read from the 4.6 GB checkpoint with HTTP range requests guided by the safetensors header. One row in bfloat16 is 4 KB, so the analysis ran on a laptop with 8 GB of memory without downloading the model.

### 5.6 The voices compared

**Table 6.** The voices compared in this paper. All use the same narrator's 7,586 utterances (33.5 h) and LoRA rank 32 on the language model and the diffusion transformer. S29, which added Common Voice questions, is mentioned in the text only.

| Voice | Text path | Start | Steps × utterances per step | Data seen | Other differences |
| --- | --- | --- | --- | --- | --- |
| S28 | Stock BPE | Cold | 1,500 × 4 (one card) | 0.79 epochs, 26.5 h | Production voice until 13 November |
| S31 a | s31 | Cold | 1,500 × 4 (one card) | 0.79 epochs, 26.5 h | None |
| S31 b | s31-stress | Cold | 1,500 × 4 (one card) | 0.79 epochs, 26.5 h | Stress sign before stressed vowels |
| S32 a | s31 | S31 a | 800 × 4 (one card) | 3,200 more utterances | Questions repeated to a fifth of the list; learning rate 5 × 10⁻⁵ |
| S32 b | s32 | S31 a | 800 × 4 (one card) | 3,200 more utterances | As S32 a, plus the question head |
| S33 | Stock BPE | Cold | 1,960 × 8 (two cards) | 2.06 epochs, 68.9 h | None |
| S34 | v3 | Cold | 1,680 × 8 (two cards) | 1.77 epochs, 59.4 h | None |
| S34 a / S34 b | v3 / v4 | S34 | About 1,720 × 4 each (one card per arm) | About 0.91 more epochs per arm | Arm b adds stress marks |

S33 and S34 differ only in the text path. S34 saw 14% fewer utterances than S33 because its steps were slower; the comparison therefore slightly favours the stock path.

## 6 Evaluation and results

Under the same recipe, the grapheme path read 1.01 character-error points more clearly than the stock path, and almost all of the gain came from letters whose Kurmanji value differs from neighbouring languages. Question intonation stayed within the noise band. This section defines the measures and the statistics, then gives the main comparison, the history of the path, the pending stress test and the geometry of the table.

### 6.1 Measures

1. **Character error rate (CER).** A recogniser transcribes each reading. CER is the edit distance between the normalised reference and the transcript, both lower-cased and stripped of punctuation, divided by the reference length and pooled over the 253 number-free sentences of the intonation set. The recogniser, U3, is a 1-billion-parameter wav2vec 2.0 encoder with a language-model decoder from Omnilingual ASR (Omnilingual ASR Team, 2025), fine-tuned on about 32 hours of human-transcribed open Kurmanji speech and 32 hours of pseudo-labelled public-domain broadcast speech. On held-out data its word error is 20.1% on 153 broadcast segments and its character error 7.2% on 999 read segments. It writes standard spelling, so it cannot hear aspiration, the trill or the pharyngeals.
2. **Per-letter error.** The reference and the transcript are aligned letter by letter (Levenshtein). For each reference letter, with xw as one unit, the per-letter error is the share of its occurrences that the recogniser did not write as written, by substitution or deletion, pooled over three readings.
3. **Error by position.** The same alignment, split into the sentence's first word, last word and the words between, plus a count of sentences in which the recogniser heard sounds before the first word.
4. **Question share and statement share.** A question judge estimates from pitch alone whether a sentence was said as a question. Pitch is tracked with pYIN (60–500 Hz, 10 ms frames) over the voiced span after trimming silence (Silero VAD), in semitones relative to the utterance's median. Two features enter a logistic regression: the mean of the last 150 ms and the maximum of the last 600 ms. Its weights (−0.754, 0.150, 0.347) were fitted, class-balanced, on Common Voice readings of statements and yes/no questions. Under speaker-wise five-fold cross-validation it labels 89% of statements and 69% of yes/no questions correctly. On human readings it calls 69% of yes/no questions, 63% of questions with a question word and 89% of statements correctly, so a voice that sounds human should not be expected to reach 100%. The question share is the percentage of question sentences the judge calls questions; the statement share is the percentage of statements it calls statements.
5. **Discrimination.** The probability that a randomly chosen question scores higher than a randomly chosen statement, the area under the ROC curve (Hanley and McNeil, 1982). It does not depend on the judge's threshold. It was computed after S31 and is pre-registered from the next voice on.
6. **Over-fitting check.** CER on the 10 progress sentences, which lie outside the book domain.
7. **Stress contrast C,** defined in Section 6.5 for the stress test.

### 6.2 Statistics and decision rules

Each voice reads every sentence three times, with three seed sets. For each sentence the three readings are averaged, voices are compared sentence by sentence, and a 95% interval comes from 5,000 bootstrap resamples of sentences (seed 7). The intervals therefore include sentence sampling and inference noise. They do not include the variance between training runs, because each recipe was trained once (Section 7.4).

The question share is noisy. Three seeds of two earlier voices, read on 19 October, put the standard deviation of a single reading at 7.4 points, close to the 6.3 points that 63 coin flips would give. The 95% band for the difference of two single readings is ±20.6 points, and for the difference of two three-reading means ±11.9 points. CER is steadier: a single reading's standard deviation is 0.64 points, and the band for two single readings ±1.76 points.

Every run had a pre-registration: a dated document written before the run, with the question, the recipe, the expected effect and numbered decision rules. Results were added below the rules, thresholds were never relaxed afterwards, and every change made before the result is recorded with its date. For example, S34 was pre-registered with format v2, and the switch to v3 was written into the document before training began.

### 6.3 The main comparison

**Table 7.** Overall results. Every value is the mean of three readings. CER is in per cent; discrimination is the area under the ROC curve.

| Voice | Text path, training | CER | Progress-sentence CER | Question share | Statement share | Discrimination |
| --- | --- | --- | --- | --- | --- | --- |
| S28 | Stock, 0.79 epochs | 4.76 | 9.86 | 47.4% | 84.3% | 0.707 |
| S33 | Stock, 2.06 epochs | 3.62 | 7.13 | 48.1% | 80.7% | 0.681 |
| S32 b | Letters (s32), 0.79 epochs plus 800 steps | 3.14 | 4.13 | 34.0% | 86.0% | 0.631 |
| S34 | Letters (v3), 1.77 epochs | **2.61** | 7.89 | 38.9% | 87.0% | 0.682 |

**Table 8.** Paired differences in CER, in percentage points, with 95% bootstrap intervals over sentences. Negative is better for the first voice.

| Comparison | What differs | CER difference |
| --- | --- | --- |
| S34 − S33 | Text path only (S34 saw 14% fewer utterances) | **−1.01 \[−1.51, −0.53\]** |
| S34 − S32 b | Format v3 against s32, and recipe | −0.53 \[−1.00, −0.07\] |
| S34 − S28 | Text path and more training | −2.15 \[−2.72, −1.58\] |
| S33 − S28 | More training on the stock path | −1.14 \[−1.54, −0.76\] |
| S32 b − S28 | Letters, against a stock voice trained less | −1.62 \[−2.20, −1.04\] |
| S32 b − S33 | Letters (s32) against more training on stock | −0.48 \[−1.06, +0.07\] |

The pre-registered rules for S34 gave a clear answer. The question share (38.9%) lay inside the ±11.9 band around S33 (48.1%) and above the 36.2% threshold, so the letter path was not shelved. The CER difference lay below zero, so format v3 became the standard text path for every new voice. Progress sentences showed no over-fitting: 7.89 against 7.13, with the alarm at 12.13. Two honest qualifications follow. The three question shares of S34 were 39.1%, 32.3% and 45.2%, so one reading alone would have fallen below the threshold. And the path did not win anything on questions; it only stayed within reach.

The threshold-free view changes how the question result reads. S34 separates questions from statements exactly as well as S33 (discrimination 0.682 against 0.681); it simply calls fewer sentences of any kind questions (20.8% of all sentences against 28.2%), which also raises its statement share. The difference is a shift of the judge's operating point, not a loss of intonation. S32 b, by contrast, did lose discrimination (0.631).

**Table 9.** Question share by type of question, mean of three readings. The number of questions per type is in brackets.

| Question type | S28 | S33 | S32 b | S34 |
| --- | --- | --- | --- | --- |
| Intonation alone (10–11) | 56.2% | 51.5% | 35.5% | 37.5% |
| With a question word (28–29) | 49.4% | 51.7% | 34.5% | 41.2% |
| With ma or gelo (23) | 40.8% | 42.3% | 32.9% | 36.6% |

The deficit of the letter voices appears in every type. It is largest for questions marked by intonation alone, the type that really tests the voice, but that type has only 10 or 11 sentences per reading and cannot decide anything by itself. Questions with ma or gelo score lowest for every voice, as expected: they need not rise.

**Per letter.** Figure 2 shows the per-letter error of the stock and letter voices next to the recogniser's error on the human narrator. The largest drops from S33 to S34 are c (32.3% → 5.1%), x (23.1% → 3.7%), j (11.2% → 1.6%) and q (10.6% → 3.5%, close to the human floor of 2.4%, itself an upper bound), followed by w, g, s, e and i. No letter became clearly worse; the largest increase was d, by 0.8 points. The stock voices' errors had a foreign accent. They read c as ç, k or ş (Colemêrg, cîhan, carî), x as s, z or k, as if it were 'ks', and q as k. The remaining errors on ê (5.5%) and u (7.0%) belong largely to the recogniser: on the human narrator it writes ê as e 1,005 times and misses u 15.2% of the time. The error on f (6.3%) is the voice's own and remains.

**The compound xw.** As a dedicated token (S32 b) xw was misheard in 7.2% of its occurrences, against 2.3% for the stock path (S33). Written as two letters (S34) it was misheard once in 222 occurrences, 0.5%. The dedicated token's errors were bare w (7 cases) or bare x (3), the two halves of the sound it was supposed to join. On the human narrator the recogniser writes xw as x 166 times but as w only 4 times, so the w errors were the voice's, not the recogniser's.

**First and last words.** In statements, the first word's error fell from 8.5% (S33) to 3.2% (S34), a difference of −5.25 points \[−7.30, −3.15\]; the trained leading boundary did what the untrained one could not (Section 6.4). In questions it went the other way, +5.74 points \[−0.51, +12.64\]: not significant, but in the wrong direction. In 9 of 64 questions of the first reading, the recogniser heard a short syllable before the first word, such as em, hem or na. The most likely cause is the question token at the start, which the voice sometimes says aloud. At the other end of the sentence the letter path was clearly better: the last word's error was lower for S32 b than for S33 by 2.44 points \[−5.12, −0.60\].

### 6.4 How the path got here

The current path is the end of six steps, each pre-registered. The values below are single readings where only one existed at the time.

1. **Letters against stock pieces (S31, 31 October).** The letter voice S31 a read more clearly than the stock voice S28 (CER 3.40 against 4.84; progress sentences 8.73 against 14.37) but called fewer questions questions (31.2% against 47.6%; discrimination 0.61 against 0.70). The pre-registered rule required both, so the path was not adopted. The arm with a stress sign, S31 b, was worse on clarity (4.66) and did not move stress: the pair index, which measures whether the final verb is stressed on the intended syllable, was in the right direction in 2 of 5 measurable pairs, median −0.09, against 5 of 5 and +0.38 for S28's natural reading. Its sign row had started as a random vector as long as a letter (1.93) and had moved only 0.13 in 1,500 steps, while x moved 0.38. Every stressed vowel was read behind a strong vector that meant nothing.
2. **Questions repeated, and a question head (S32, 1 November).** Repeating the 73 question utterances to a fifth of the training list and adding a ? before the first letter raised the question share only to 33.8%. The rules declared the path frozen. The head, however, made the voice read its questions' first words much better with the same weights and data: 4.0% error against 11.0%, a difference of −7.0 points \[−12.3, −2.5\]. A re-analysis on 11 November showed that S29–S32's question decisions lay inside single-reading noise (±20.6 points), which is why every later voice was read with three seed sets. S29, which mixed in Common Voice questions from other speakers and microphones, had raised the question share by 5.6 points but worsened CER by 4.35 points \[3.05, 5.69\].
3. **The text-path audit (12 November).** Position analysis located the remaining letter errors. The first word did not improve with letters (8.0% for S28 against 9.8% for S31 a), short first words such as tu, ez and ma doubled their error (8.3% against 19.0%), and the recogniser heard extra sounds before the first word in 21 sentences of S31 a against 6 for S28. The last word improved strongly (5.26% to 1.87% from S28 to S32 b). The audit also found and fixed four tokenizer faults: acronyms spelled letter by letter but read as words, unknown characters that glued two words together, clusters of end marks that opened a question in the wrong place, and a default that switched the stress sign on. It found two silent failure modes, a format mismatch and a skipped table, that led to the safeguards of Section 4.6. Format v2 resulted. Adding the leading boundary to S32 b without training changed the first-word error of statements by only −1.60 points \[−4.07, +0.49\], so it had to be learned.
4. **The letter audit (13 November).** The per-letter analysis revealed the failure of the xw token, and format v3 replaced v2 before S34 was trained.
5. **Equal training (S34, 13 November).** The results above made v3 the standard.
6. **Stress as a mark (14 November).** Format v4 and the S34 a/b test (Section 6.5).

Part of the remaining CER is the recogniser's, not the voice's. It writes some numbers that the voice says as words in digits (38 for sî û heşt) and counts spacing and circumflex differences as errors. Removing these three effects lowers S32 b's CER from 3.14 to 2.23 and S28's from 4.84 to 3.39, without changing the order of the voices.

### 6.5 Stress as a mark: the pre-registered test (running)

S34 a/b asks whether stress given as a mark on the vowel moves the stress to the marked syllable without hurting clarity or questions. Both arms start from S34's weights and train for about 1,720 steps, one T4 card each, on the same data in the same order with the same seed. Arm a continues in format v3 as the control; arm b uses v4. The measurement run confirmed the set-up: both arms started at the same loss (0.857219), all 385 weight tensors loaded, the training-text fingerprints computed on the remote machine matched the local ones, and the stress row reached a length of 0.0395, as the model sees it, after 60 steps. The arms ran at 12.75 and 13.01 s per step in 11.9 GB.

The main measure uses the 26 stress-pair sentences. Arm b reads each one twice with the same seed, once with the final verb marked on its first syllable and once on its last. For a sentence and a seed,

```latex
C \;=\; \big(P_{\mathrm{last}} - P_{\mathrm{first}}\big)_{\text{mark on last}} \;-\; \big(P_{\mathrm{last}} - P_{\mathrm{first}}\big)_{\text{mark on first}}
```

where P is the stress score of Section 4.7. If the mark works, C > 0. The unit is the sentence, averaged over three seeds, with a bootstrap interval over sentences. Arm a reads the same sentences without marks; the same difference between two of its seeds gives the noise floor. In the narrator's natural reading the infinitive and the past form differ by about +0.38, which sets the expected size if the mark works.

The decision rules, written before the run:

1. **The mark carries stress** if C's interval lies above zero, C > 0 in at least 70% of measurable sentences, and fully marked reading is not clearly less clear than arm a (the upper end of the CER difference below +0.5). Then v4 becomes the standard, and a native listener hears blind pairs such as hˈatin and hatˈin before it is used.
2. **It carries stress but hurts clarity.** If unmarked reading in v4 is as clear as v3, v4 becomes the standard but marks are used only where a writer types them; otherwise v3 stays.
3. **It does not carry stress** (C's interval includes zero). v3 stays, v4 remains as code, and no follow-up mini-experiment is opened; stress returns only inside a larger run with a new reason, such as marks measured from speech.

Training was submitted on 14 November 2026. Its results were not available when this draft was written and will be added.

### 6.6 What the table learned: geometry

The geometry of the frozen embeddings and of the trained tables explains the design rules of Section 4.

**Table 10.** Cosine similarity between letter embeddings, in the base model and with S34's table added.

| Pair | Base model | With S34's table |
| --- | --- | --- |
| e – ê | 0.12 | 0.09 |
| i – î | 0.08 | 0.08 |
| u – û | 0.04 | 0.04 |
| c – ç | 0.12 | 0.11 |
| k – q | 0.11 | 0.07 |
| a – e (the closest pair) | 0.32 | 0.31 |
| Mean over all letter pairs | 0.09 |  |

- **Letters are not arranged by sound.** The base model's letter vectors are nearly orthogonal, and even the closest pair, a and e, has a cosine of only 0.32. Whatever the model knows about sound is built in the layers above the embedding. Training does not move a letter towards another letter: no row of the table has a cosine above 0.3 with any letter. The direction shared by all rows holds only 2.3% of the table's energy, so each row is specific to its letter. A start borrowed from a phonetic neighbour (start c near j, for instance) therefore has nothing to borrow.
- **The table corrects; it does not replace.** A row's length is on average 0.20, about a tenth of a letter's length (1.93). The longest rows belong to q (0.35), u (0.34), ê (0.30), x (0.29), j (0.27) and c (0.25): the letters whose errors fell most and the letters the recogniser finds hardest.
- **Training finds the same correction again where one is needed.** Two arms trained separately on the same data (S31 a and S31 b) moved x, e, ê, ç, î, û and c in the same direction (cosine 0.82 to 0.91; mean over all letters 0.67). Between S34 and S31 a, which differ in format, seed and number of cards, the rows still agree for q (0.77), ê (0.70), i (0.68), ş (0.65), x (0.64) and î (0.60). For letters whose value was already right, such as l (0.09), s, z and f (0.15 each), k (0.18) and m (0.21), the row is noise.
- **The question row learned no direction.** Its cosine between S34 and S31 a is −0.03. It is shared by the opening and the closing ?, and only 73 training utterances are questions.
- **Rows that start from nothing stay near where they start.** The stress sign moved 0.13 in 1,500 steps; the xw token stayed at its mean-of-parts start (cosine 0.997 between two trainings). Weight decay shrank the unused xw row by only 0.2% over 1,680 steps, so unused rows are harmless.
- **No ready direction for stress.** If the model had learned that á is a stressed a, the differences á − a, é − e, í − i, ó − o and ú − u would point the same way. Their mutual cosines range from 0.05 to 0.25 (mean 0.16), no higher than for grave accents (0.11 to 0.27) or capital letters (0.09 to 0.22), and only a little above unrelated letter differences (0.04 to 0.12). What the accented forms share is being rare, not being stressed. The stress row therefore starts at zero.
- **Reserved slots are not exactly empty.** Their rows have a norm of 0.0002, which an earlier comment in the code had rounded to zero. Format v4 bypasses them.

Together these measurements give the initialisation rule of this paper. In a run of this size, a row that starts from nothing, whether random or an average, does not get learned. A letter works because it stands on a vector the model already trained, and the table only corrects it. A new symbol should therefore start as the letter it changes, or as zero on top of that letter, so that on its first step it reads no worse than the letter alone.

**Figure 2** (below): per-letter error of the stock voices S28 and S33, the letter voices S32 b and S34, and the recogniser on the human narrator.

&#91;embedded content: Deng per-letter measurements, 13 November 2026 · 32 units, intonation set, three readings per voice\]

*Figure 2.* Grey dots: the stock path after 2.06 epochs (S33). Blue dots: the letter path after 1.77 epochs (S34). Ticks: the recogniser on the narrator's own speech, an upper bound because the narrator's segment boundaries are approximate. Letters are sorted by the stock path's error; hovering a mark shows S28 and S32 b as well.

## 7 Weaknesses and limitations

The evidence for the Deng embedding rests on one narrator, one base model, machine judges and one training run per recipe, and no human has yet listened to the letter voices under test conditions. This section lists every weakness we know of, grouped by where it sits: the measures, the data, the design, the statistics, the engineering and the reach of the conclusions. Table 11 at the end summarises them, with our own judgement of their severity and the roadmap item that answers each.

### 7.1 The measures

**No listening test of the letter voices.** The project's final criterion is blind listening by native speakers, and the letter voices (S32 b, S33, S34) are still waiting for it. A first round on two earlier voices found them 1.80 \[1.42, 2.20\] and 1.92 \[1.50, 2.32\] points below the human recordings in naturalness, on a five-point scale, from 194 answers. Only two of the four listeners finished, and they disagreed sharply on whether a clip was human: one called 3% of the machine clips human, the other 77%. Every claim about clarity in this paper is therefore a claim about what a recogniser hears.

**The recogniser is a judge with its own accent.** U3 confuses ê with e and u with û even on human speech. Half of its training labels are pseudo-labels written by an earlier recogniser. It writes standard spelling, so it cannot tell plain from aspirated stops, a tap from a trill, or h from ḧ: exactly the sounds the path does not yet represent. A voice that said a plain t where an aspirated one belongs would score as well as one that did not. Scoring artefacts add to this. The recogniser writes some numbers as digits, and spacing and circumflex differences count as errors; a canonical second score lowers CER by about 30% without changing the order of the voices.

**The question judge is crude.** It uses two pitch features of the last second and a logistic regression calibrated on read yes/no questions. On human readings it recognises only 69% of yes/no questions and 63% of questions with a question word. A question with ma or gelo may correctly stay level, yet it counts as a failure. What a human narrator would score on our own set has not been measured, so the target value of the question share is unknown. The decisive type, questions marked by intonation alone, has only 10 or 11 sentences. And the judge ignores everything except final pitch: focus, emphasis, tempo, voice quality.

**The stress measure is indirect.** P averages four acoustic cues of stress. Forced-alignment boundaries deviate from manual ones by a median of 29 to 40 ms at word edges, and vowel durations from the alignment correlate only weakly with manual ones (r = 0.22). The half-width of C, the main measure of the stress test, was not known in advance.

**Much is not measured at all:** overall naturalness, prosody beyond the end of a sentence, long-form coherence, breathing and expressiveness.

### 7.2 The data

**One narrator, one register.** All 33.5 hours come from one professional reading published prose. Whatever the table learned, it learned from that person's reading of book Kurmanji. Spontaneous and conversational speech is absent, only 73 utterances (1%) are questions, and an earlier voice trained on the same material misread short conversational sentences. One speaker also means one variety, so the dialect labels have not yet been exercised.

**The data cannot be shared.** The permission covers project use only, so no one can reproduce the voices from the same audio, and every replication must use other data.

**Small, read-style exams.** The exam sentences come mostly from Common Voice's read sentence collection. They are locked and never trained on, but they are few and belong to the written register.

**Mixing data can hurt.** Adding question recordings from other speakers and microphones (S29) raised the question share a little and worsened CER by 4.35 points. A table tuned on one narrator may interact badly with multi-speaker data.

### 7.3 The design

**The hidden contrasts are missing.** Aspiration and the trill are phonemic but unwritten. The voice learns them word by word where words are frequent and guesses elsewhere. The project's own requirement that words spelled alike but said differently, such as ker and kerr, come out right is not yet met.

**Stress rests on hypotheses.** The rules come from grammars and were only partly confirmed in speech; the most frequent rule, final stress of nouns by default, was not confirmed. Format v4 is untested at the time of writing, and its gain of 4 and its keep share of 0.5 are choices, not measurements. Known gaps in the rules were noted but not fixed without a source: vocative forms (Bavo, Hevalno) receive final stress, a negated modal such as nikarîbû is not parsed as negated, and the comparative -tir takes the stress.

**One row serves two question marks.** The opening and the closing ? share one row, which learned no consistent direction. The opening token may be the source of the syllables heard before the first word of some questions.

**One learning rate for everything.** The table trains at the adapters' learning rate. Some letters (o, s, b) still disagreed between two arms after 0.79 epochs, a sign that they were not fully trained. A separate rate was deliberately left untested so that comparisons stayed clean.

**Longer sequences cost.** With 2.29 times as many tokens, steps are 35 to 45% slower, the length safety net is looser, memory use is higher, and the base model's maximum of 8,192 tokens is reached sooner in long-form reading.

**The normaliser makes choices.** Pairs such as we and wê can only be resolved by meaning. The acronym rule made 6 of 209 texts worse. Number words such as yanzdeh or yazdeh wait for editors.

**Coupling to the base model.** The path needs every Kurmanji letter to exist as a single-character token in the base vocabulary, and it depends on VoxCPM's internals: the embedding module it hooks and the lora\_ prefix its checkpoint code saves. Another base model may lack ê, î, û, ş or ç as single tokens. The table also belongs to one voice; nothing shows that it transfers to another speaker without retraining.

### 7.4 The statistics

**One training run per recipe.** The intervals in Table 8 include sentence sampling and inference noise, not the variance between training runs. Training noise exists: two arms of S31 agreed on their rows with a mean cosine of only 0.67, and the question decisions of S29 to S32 turned out to lie within seed noise. The −1.01 difference could grow or shrink with other training seeds.

**Unequal exposure.** S34 saw 14% fewer utterances than S33, which favours the stock path. The comparison of S32 b with S28 differs in more than the text path.

**Exceptions to the project's own rule.** The gate requires the expected gain to be at least twice the half-width of the main measure. Three consecutive voice runs went ahead under dated, reasoned exceptions, because the machine measure was too coarse to see the effects expected. In one of them a naming pattern in the gate kept the rule from being applied automatically, although the exception had been filed. Rules that are bent, however openly, are weaker evidence than rules that hold.

**Many looks, few corrections.** Many letters, positions and question types were examined. The per-letter and per-position numbers are descriptive and uncorrected for multiple comparisons; only the pre-registered primary measures decided anything. Several analyses were added after the results: discrimination, the question types, the human floor per letter, and the reading of S34's question result as a shift rather than a loss. They are labelled as such. The paired bootstrap also treats sentences as independent and ignores their grouping into pairs and types.

### 7.5 Engineering and reproducibility

**Free compute is fragile.** Quotas, session limits, rate limits and silent failures shape what can be run. A job can be killed without a log, and a session stopped by hand loses everything.

**Third parties can break a run.** Model files hosted elsewhere become unreachable (an expired certificate stopped all scoring for a day). The fine-tuning script is pinned to voxcpm 2.0.3, and the patch that installs the table asserts the exact lines it replaces, so a new release fails loudly rather than silently, but it does fail.

**Not every failure is guarded.** Silent failure modes were found one at a time, after they had cost a run. Others may remain.

**Release is pending.** An open copy of the text-path package exists but has not been synchronised with the current code. The exam sentences derived from CC0 text can be released; the training audio cannot.

**Development was AI-assisted.** Most of the code and the analyses were written by an AI coding assistant under the direction of the project lead. Every number in this paper comes from a logged run, but errors of interpretation remain possible; pre-registration and independent code reviews are the project's checks against them.

### 7.6 Reach of the conclusions

One language, one base model, one narrator and one recogniser. The initialisation rule rests on three trials in one set-up. More data or more steps might teach a row that starts from nothing, and a model whose input embeddings are organised by sound would allow borrowed starts. The rule should be read as "in runs of about two epochs over 30 hours, on a frozen 2-billion-parameter model", not as a law.

**Table 11.** Summary of weaknesses. Severity is the authors' judgement of the risk to the paper's conclusions.

| Weakness | Severity | Evidence | Roadmap item (Section 8) |
| --- | --- | --- | --- |
| No listening test of the letter voices | High | Round 1 covered only earlier voices; listeners disagreed | 1 |
| One training run per recipe | High | S31 arms agree only partly; question decisions within seed noise | 2 |
| One narrator, 1% questions, read prose only | High | 73 questions; S28 misread short conversational sentences | 3 |
| Hidden contrasts not represented | Medium | Aspiration and trill are phonemic, unwritten | 5 |
| Stress rules partly unconfirmed; v4 untested | Medium | The default noun rule was not confirmed | 4 |
| Recogniser and judge limits | Medium | ê/e, u/û confusions; 69% and 63% on human questions | 6 |
| Shared ? row; syllables before questions | Medium | +5.74 points on first words of questions | 7 |
| One learning rate for table and adapters | Low | o, s, b rows disagree between arms | 8 |
| Longer sequences | Low | 35–45% slower steps; looser safety net | 9 |
| Coupling to the base model's vocabulary and internals | Low | Hook, lora\_ prefix, single-character tokens | 10 |
| Release pending | Low | Open copy not synchronised | 11 |

## 8 Improvement roadmap

The largest gains now lie outside the embedding table: in human evaluation, in data that contains questions and conversation, and in measuring training noise. Inside the table, the next steps are to finish the stress test and to give the hidden contrasts a lexicon measured from the narrator's own speech. Each item below names its motivation, the action, the measure that will decide it and its cost; the numbers match Table 11. Figure 3 places the items by expected impact and effort.

1. **Blind listening, round two.** *Why:* no human has judged the letter voices. *Action:* at least five native listeners who finish the whole test; the human side is the narrator's own pages that never entered training; each listener's answers are corrected for that listener's own rate of calling clips human. *Decision:* the project's criterion, at most 55% correct identification of the human and no significant difference in naturalness. *Cost:* a few hours per listener; the page and the clips exist.
2. **Training-noise estimate.** *Why:* every interval in this paper ignores the variance between training runs. *Action:* retrain the S33 and S34 recipes with two more training seeds each and repeat the main comparison with six runs. *Decision:* the CER difference holds if its interval, now including training noise, stays below zero. *Cost:* about 30 GPU hours, one week of one account's allowance.
3. **Questions and conversation in the data (the next voice, S35).** *Why:* questions are 1% of the training data, and the question share did not move with any text-side change. *Action:* add permissioned conversational speech and question-rich recordings, if possible from the same narrator; add intonation-only questions to the exam set; and have a human narrator read the exam set so that the question share has a human target. *Decision:* pre-registered with discrimination next to the question share. *Cost:* data collection is the bottleneck, not compute.
4. **Finish the stress test.** *Why:* stress decides meaning, and v4 is built but unproven. *Action:* complete S34 a/b and apply its five rules (Section 6.5). If the mark carries stress, play blind pairs to a native listener; if it does not, derive marks from the narrator's measured stress instead of from grammar rules and retry only inside a larger run. *Cost:* already running; the reading test takes about 3.4 hours.
5. **A lexicon for the hidden contrasts, measured from speech.** *Why:* aspiration and the trill are phonemic and unwritten. *Action:* measure voice onset time in the narrator's 33.5 hours for word-initial ç, k, p and t before a vowel. Aspirated stops run about 60 to 80 ms from release to voicing, plain ones about 10 to 25 ms. If the values of a frequent word fall into two clusters, the narrator's own speech says which words are aspirated, and those words get a mark row, at zero on its letter. If they do not, the narrator does not make the contrast and a mark would have nothing to teach, which is also a result. The trill can be approached the same way. *Cost:* processor time only.
6. **Better judges.** *Why:* the recogniser's own confusions and the judge's crudeness cap what the measures can see. *Action:* add e/ê and u/û minimal pairs to the recogniser's exam; train it with human-corrected references; report the canonical score next to CER; give the question judge the whole contour and the question type, and calibrate it on the narrator. *Cost:* moderate, mostly human correction time.
7. **The opening question token.** *Why:* syllables appear before the first word of some questions. *Action:* read S34's questions without the opening token, with the same weights and seeds, to test whether the token is being voiced. If it is, give the opening ? its own row, started as the ? row, or drop it. *Cost:* one short reading job.
8. **A learning rate for the table.** *Why:* some letter rows had not settled after 0.79 epochs. *Action:* a separate rate or a gain for the letter rows, tested by whether the rows of two runs come to agree (the cross-run cosine of Section 6.6). *Cost:* low, but it needs its own pre-registered pair of runs.
9. **Long-form safety.** *Why:* sequences are 2.29 times longer. *Action:* keep the production safety ratio at 2.6 steps per token and measure the longest paragraph a voice reads reliably within the 8,192-token limit. *Cost:* low.
10. **Portability checks.** *Why:* other teams will try the path on other models. *Action:* ship a script that checks single-character coverage of an alphabet in a new vocabulary, measures letter geometry from a few rows, and verifies that the hook and the saved table survive a save and a load. *Cost:* low.
11. **Release.** *Why:* a method that cannot be run cannot be checked. *Action:* synchronise the open package (tokenizer, tests, fingerprints, format files), release the exam sentences derived from CC0 text and the analysis scripts, and publish a model card for the method. The voice weights and the narrator's audio are never released. *Cost:* low to moderate, mostly a privacy review of every file.

Four longer-term directions follow from the related work. **Dialect tags** become useful once several speakers are in the data: a tag token at the start of a text, with its row at zero, so that an unknown tag reads as the standard language. **A phoneme path** built with Epitran and a hand-checked lexicon would show whether explicit phonemes beat letters once aspiration is known. **A prosody-aware text encoder,** a phoneme-level BERT for Kurmanji in the manner of Li et al. (2023), could give the voice the context that questions and stress need. **A text–speech contrastive objective** could teach letter rows their sound directly, which the geometry shows the base model never learned.

**Figure 3** (below) places these items by expected impact and effort.

&#91;embedded content: Figure 3 · roadmap items by impact and effort, authors' judgement\]

*Figure 3.* The four items in the upper-left quadrant cost little and decide the most: the stress test is already running, the listening page and clips exist, and the release needs mainly a privacy review. The largest lever, data with questions and conversation, also costs the most.

## 9 Practitioner's guide

This section is written for three readers: one who will use the Deng path as it is, one who will build on it, and one who starts from nothing for another language. Each part ends with the mistakes that cost the project a run.

### 9.1 Using the path as it is

You need VoxCPM2 (package voxcpm 2.0.3), the text-path package (the module kmr\_token with its companions ses, vurgu and fiil, and the normaliser), and a 16 GB card for training. Reading runs on smaller cards.

**To train a new voice,** patch VoxCPM's fine-tuning script in two places. Replace the line that takes the stock tokenizer with the Deng path, and keep the frozen weights in bfloat16:

```python
# in scripts/train_voxcpm_finetune.py, in place of:  tokenizer = base_model.text_tokenizer
import kmr_token
tokenizer = kmr_token.install(base_model, fmt="v3")   # the table exists from here on
for name, p in base_model.named_parameters():
    if not p.requires_grad and "audio_vae" not in name:
        p.data = p.data.to(torch.bfloat16)           # fits a 16 GB T4
```

Pass every text through the normaliser first. After every save, write the format next to the weights with `kmr_token.save_format(folder, "v3")`. Then read the table back from the saved file and check that its letter rows are non-zero.

**To read with a trained voice:**

```python
from voxcpm import VoxCPM
import kmr_token
from hazirla import hazirla                          # the normaliser

model = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False,
                               lora_config=cfg, lora_weights_path=weights)
fmt = kmr_token.load_format(weights_dir)             # from text_path.json; fails if missing
tok = kmr_token.install(model.tts_model, fmt=fmt)    # BEFORE the LoRA weights are loaded
loaded, skipped = model.load_lora(weights)
assert "base_lm.lora_text_delta" in loaded
kmr_token.table_check(model.tts_model)               # fails if the table was not filled
wav = model.generate(text=hazirla("Ez di sala 1986an de ji dayik bûm."))  # 1986an -> hezar û neh sed û heştê û şeşan
```

For production, set VoxCPM's retry threshold (retry\_badcase\_ratio\_threshold) to 2.6 audio steps per text token instead of 6.0. With a format that has marks (v4), choose the reading policy: "all" marks every word the rules can mark, "none" marks only what the writer typed, and a typed ˈ always wins, as in hˈatin or hatˈin.

**Mistakes that cost the project a run:**

- Calling install() after loading the LoRA weights. The loader skips the table's key without a word and the voice reads with untrained letters.
- Reading with a different format from the one the voice was trained with. Nothing fails; the voice simply reads worse.
- Calling a method of the stock tokenizer that the wrapper does not define. The Deng wrapper raises an error; a home-made wrapper that passes calls through would silently return BPE pieces.
- Running format v4 without the verb lexicon. The stress marks change silently; v4 now stops instead.

### 9.2 Building on the path

The rules below keep old voices readable while the path grows.

1. **Never change a trained format.** Give every change a new name, and freeze its fingerprints with its first training.
2. **Append, never insert.** A saved table finds a row by its position, so new symbols go at the end of the alphabet, and a new symbol needs a new table size. Mark rows are already reserved (eight, one used) so that new marks do not change the size.
3. **Start every new symbol from something trained.** A sound that modifies a letter (aspiration, the trill, a pharyngeal, stress, tone) should be a mark on that letter, with its mark row at zero. A new standalone symbol should start as the letter it is closest to in function, not as a random vector or an average. Give a new row a larger effective step, as the gain of v4 does.
4. **Keep training and reading identical at the start of a text.** The leading boundary and the question token must appear in reading exactly as in training.
5. **Measure the table after training.** Compute the cosine between the rows of two independent runs: letters whose rows agree have a real correction to learn, letters whose rows do not are already right or under-trained.
6. **For new speakers and dialects,** put the speaker or dialect into a token at the start of the text, with its row at zero, so that an unknown tag reads as the standard language. Never respell text by dialect.
7. **For another base model,** check first that every letter of the alphabet is a single-character token in its vocabulary, find the module that embeds text in both training and reading, and confirm that the model's checkpoint code saves a parameter you add. Then port the tests: fingerprints, the format file and the table check.

### 9.3 Starting from nothing for another language

The order below is the one we would follow again; it would have saved the project several runs.

1. **Measure the stock tokenizer on your own text** before training anything: the number of distinct pieces, the share seen at most five times, how many pieces each letter is spread over, the tokens per utterance, and how frequent words are cut.
2. **List what the spelling does not write.** Read at least two grammars, list the minimal pairs (for Kurmanji: kar/kar with plain or aspirated k, pir/pirr, hátin/hatín), and decide which contrasts the voice must get right.
3. **Check single-character coverage** of your alphabet in the base vocabulary. Where a letter is missing, choose the existing token closest in sound as its start and let the residual row correct it.
4. **Measure the base embedding geometry** of your letters: cosines between letters and between accent directions. It takes minutes with range requests on the checkpoint file and tells you whether borrowed starts can work.
5. **Build the normaliser first:** numbers, dates and abbreviations as words, missing diacritics restored, one standard spelling.
6. **Install a zero-initialised residual table** with a leading boundary and a question head; name and fingerprint the format; write the format file next to every checkpoint; check the table after every load.
7. **Plan compute from measurements:** a short measurement run, a deadline checked inside every loop, checkpoints copied out during training, and reading as a separate job.
8. **Evaluate in pairs and in threes:** a recogniser with its human floor, per-letter and per-position error, a question judge with a threshold-free score, three inference seed sets, paired bootstrap intervals, and decision rules written before the run. Measure training noise early.
9. **Bring in human listeners early,** with enough of them to separate the voice from the listener, and with the human side recorded under the same conditions.
10. **Add prosodic features last,** as marks on letters, and only after their rules have been checked on speech.

### 9.4 Troubleshooting

**Table 12.** Symptoms the project met, their usual cause and the first check.

| Symptom | Usual cause | First check |
| --- | --- | --- |
| Kurmanji letters read with a foreign value (c as k or ç, x as 'ks') | The table was not loaded | Run the table check; install the path before loading the weights |
| A voice reads worse after a code change, and nothing failed | Format mismatch between training and reading | Compare text\_path.json with the code; run the fingerprint tests |
| The first word is garbled, or a sound precedes it | No leading boundary in the training format | Train with v3 or later |
| A digraph is read as one of its letters | A dedicated token that started from nothing | Write the digraph with its letters |
| A new marker makes the voice less clear | The marker's row started random or too long | Start at zero on its letter, with a gain |
| An extra syllable before questions | The opening question token is voiced | Read without it; give it its own row |
| Readings cut off or run on | The length safety net was set for the stock tokens | Use 2.6 steps per token |
| The recogniser reports no error at all | The recogniser never ran | Check how many clips were heard |
| Two cards but no speed-up | One rank never trained | Look for both ranks in the log |
| Stress marks differ between machines | The verb lexicon is missing | Compare the training-text fingerprint before training |
| Question share jumps between runs | Single-reading noise (±7 points) | Read three times; report discrimination as well |

## 10 Ethics, data rights and the language community

A voice that cannot be told from a person is useful and dangerous in equal measure, and the language it speaks has a history of restriction. The project's rules follow from both facts.

**Consent and voice identity.** The voice imitates a real narrator who permitted its use inside the project. The permission does not extend to publishing the voice, so neither the voice weights nor the training audio leave the team, and this paper contains no audio. Future voices will be recorded with volunteers under written agreements that state how the recordings are used, how contributors are credited and what share they have in any revenue.

**Data rights.** Only openly licensed material and material whose rights holder agreed are used. Every permission is recorded with its date and channel, and a permission that is withdrawn removes the material from all future models. Only freely licensed raw audio is published as an open dataset; permissioned recordings, personal recordings and material under non-commercial or no-derivatives licences are never published.

**Safety of contributors and sources.** Kurdish-language publishing and broadcasting have been restricted in parts of the region (Haig and Öpengin, 2018), and some valuable sources are politically sensitive. The project refers to such sources by code names in every shared document, keeps contributors' identities out of public repositories, and screens every public file for personal information before release.

**Standard language and dialects.** Choosing standard written Kurmanji as the target risks marginalising speakers of other varieties. Three measures limit this: every recording carries labels for the speaker's home region, dialect group and register; the groups follow the dialectological literature (Öpengin and Haig, 2014) rather than the team's impressions; and dialect voices are planned once the standard voice is in place, with exam sets by dialect group to check that the recogniser serves every group.

**Misuse.** A natural Kurmanji voice could be used to impersonate people or to spread false statements in their voice. The project does not release voice weights, uses only voices whose owners consented, and treats detection and watermarking as conditions for any future release.

**The community.** Kurdish-facing material is written in Kurdish and reviewed by native speakers; listeners and language editors are volunteers from the language community, and their results are reported only in aggregate.

**Compute.** Each full training run used about 7.3 hours on two T4 cards, roughly 1 kWh.

## 11 Conclusion

The first layer of a pretrained TTS model decides how much of a new language the rest of the model can hear. For Kurmanji, VoxCPM2's 30-language BPE vocabulary cut words at meaningless points and scattered each letter over hundreds of frozen pieces. Feeding the model its own single-character tokens and learning a 41-row residual table on top of the frozen embeddings made the voice clearer by about one point of character error under the same recipe. The gain fell where it should: on c, x, j and q, the letters that neighbouring languages pronounce differently, while letters whose value was already right barely moved. The geometry of the embeddings explains the design rules we arrived at the hard way. The base model's letters are not arranged by sound, so a new symbol has nothing to borrow from a phonetic neighbour; rows that start from nothing are not learned in runs of this size; and new features such as stress therefore belong on the letter, starting at zero.

The text side did not fix question intonation, and it could not be expected to: the narrator's data holds almost no questions. The next gains will come from data with questions and conversation, from a lexicon of the contrasts the spelling hides, measured from speech, and from the two tests this paper still lacks: a blind listening test of the letter voices and an estimate of training noise. We hope the guide in Section 9 saves the next team, working on Kurmanji or on any language a large model has never seen, the runs it cost us.

## Declarations

*Items in square brackets are for the authors to complete or confirm before submission.*

**Data availability.** The narrator's recordings cannot be shared: the permission covers use inside the project only, and the voice identifies a real person. The exam sentences, which derive mostly from the CC0 sentence collection of Common Voice, the stress-pair sentences, the per-reading scores, the per-letter tables and the embedding-geometry measurements will be released with the code \[repository and licence to be named\].

**Code availability.** The text-path package (tokenizer, residual table, formats, format files, table check, tests and fingerprints), the measurement scripts and the job gate will be released under an open licence \[repository to be named\]. Voice weights will not be released.

**Author contributions (CRediT).** \[Conceptualisation, methodology, software, validation, formal analysis, data curation, writing, supervision and project administration, to be assigned by the authors.\]

**Competing interests.** \[None declared; to be confirmed by the authors.\]

**Funding.** The work received no external funding. All computation used the free tier of a public cloud notebook service.

**Acknowledgements.** We thank the narrator and the rights holders who allowed their recordings to be used, and the native-speaker listeners and language editors who volunteered their time. \[Names only with each person's written consent.\]

**Ethics.** Listening tests were run with adult volunteers who gave informed consent; no personal data are published, and listener results are reported in aggregate. \[Institutional review: to be stated by the authors.\]

**Declaration of generative AI and AI-assisted technologies.** The project's code, the experiments' analyses and the first draft of this manuscript were produced with Claude (Anthropic), an AI assistant, working under the direction of the project lead. \[The authors must review and edit the content and confirm here that they take full responsibility for it.\]

## References

Bibliographic data were checked against OpenAlex, Crossref, arXiv and publisher pages on 14 November 2026. Citation counts for the works in Table 1 and Supplementary Table S1 come from OpenAlex on the same day.

- Abdullah, A. A., Tabibian, S., Veisi, H., Mahmudi, A., & Rashid, T. (2024). End-to-end transformer-based automatic speech recognition for Northern Kurdish: A pioneering approach. arXiv:2410.16330. [doi:10.48550/arXiv.2410.16330](https://doi.org/10.48550/arXiv.2410.16330)
- Ahia, O., Kumar, S., Gonen, H., et al. (2023). Do all languages cost the same? Tokenization in the era of commercial language models. *Proceedings of EMNLP 2023*. [doi:10.18653/v1/2023.emnlp-main.614](https://doi.org/10.18653/v1/2023.emnlp-main.614)
- Ahmad, H., & Rashid, T. (2024). Central Kurdish text-to-speech synthesis with novel end-to-end transformer training. *Algorithms, 17*(7), 292. [doi:10.3390/a17070292](https://doi.org/10.3390/a17070292)
- Ahmadi, S. (2020). KLPT – Kurdish Language Processing Toolkit. *Proceedings of the Second Workshop for NLP Open Source Software*. [doi:10.18653/v1/2020.nlposs-1.11](https://doi.org/10.18653/v1/2020.nlposs-1.11)
- Anastassiou, P., Chen, J., Chen, J., et al. (2024). Seed-TTS: A family of high-quality versatile speech generation models. arXiv:2406.02430. [doi:10.48550/arXiv.2406.02430](https://doi.org/10.48550/arXiv.2406.02430)
- Ardila, R., Branson, M., Davis, K., et al. (2020). Common Voice: A massively-multilingual speech corpus. *Proceedings of LREC 2020*. [doi:10.48550/arXiv.1912.06670](https://doi.org/10.48550/arXiv.1912.06670)
- Artetxe, M., Ruder, S., & Yogatama, D. (2020). On the cross-lingual transferability of monolingual representations. *Proceedings of ACL 2020*. [doi:10.18653/v1/2020.acl-main.421](https://doi.org/10.18653/v1/2020.acl-main.421)
- Baevski, A., Zhou, H., Mohamed, A., & Auli, M. (2020). wav2vec 2.0: A framework for self-supervised learning of speech representations. *Advances in NeurIPS 33*. [doi:10.48550/arXiv.2006.11477](https://doi.org/10.48550/arXiv.2006.11477)
- Bisani, M., & Ney, H. (2004). Bootstrap estimates for confidence intervals in ASR performance evaluation. *Proceedings of ICASSP 2004*. [doi:10.1109/ICASSP.2004.1326009](https://doi.org/10.1109/ICASSP.2004.1326009)
- Bojanowski, P., Grave, E., Joulin, A., & Mikolov, T. (2017). Enriching word vectors with subword information. *Transactions of the ACL, 5*, 135–146. [doi:10.1162/tacl\_a\_00051](https://doi.org/10.1162/tacl_a_00051)
- Casanova, E., Weber, J., Shulby, C., et al. (2022). YourTTS: Towards zero-shot multi-speaker TTS and zero-shot voice conversion for everyone. *Proceedings of ICML 2022*. [doi:10.48550/arXiv.2112.02418](https://doi.org/10.48550/arXiv.2112.02418)
- Chau, E. C., Lin, L. H., & Smith, N. A. (2020). Parsing with multilingual BERT, a small corpus, and a small treebank. *Findings of EMNLP 2020*. [doi:10.18653/v1/2020.findings-emnlp.118](https://doi.org/10.18653/v1/2020.findings-emnlp.118)
- Chen, J., Xiao, S., Zhang, P., et al. (2024). M3-Embedding: Multi-linguality, multi-functionality, multi-granularity text embeddings through self-knowledge distillation. *Findings of ACL 2024*. [doi:10.18653/v1/2024.findings-acl.137](https://doi.org/10.18653/v1/2024.findings-acl.137)
- Chen, Y., Marchisio, K., Raileanu, R., et al. (2023). Improving language plasticity via pretraining with active forgetting. *Advances in NeurIPS 36*. [doi:10.48550/arXiv.2307.01163](https://doi.org/10.48550/arXiv.2307.01163)
- Chen, Y., Niu, Z., Ma, Z., et al. (2025). F5-TTS: A fairytaler that fakes fluent and faithful speech with flow matching. *Proceedings of ACL 2025*. [doi:10.18653/v1/2025.acl-long.313](https://doi.org/10.18653/v1/2025.acl-long.313)
- Clark, J. H., Garrette, D., Turc, I., & Wieting, J. (2022). CANINE: Pre-training an efficient tokenization-free encoder for language representation. *Transactions of the ACL, 10*, 73–91. [doi:10.1162/tacl\_a\_00448](https://doi.org/10.1162/tacl_a_00448)
- Conneau, A., Khandelwal, K., Goyal, N., et al. (2020). Unsupervised cross-lingual representation learning at scale. *Proceedings of ACL 2020*. [doi:10.18653/v1/2020.acl-main.747](https://doi.org/10.18653/v1/2020.acl-main.747)
- Conneau, A., Ma, M., Khanuja, S., et al. (2023). FLEURS: Few-shot learning evaluation of universal representations of speech. *Proceedings of IEEE SLT*. [doi:10.1109/SLT54892.2023.10023141](https://doi.org/10.1109/SLT54892.2023.10023141)
- Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. *Proceedings of NAACL-HLT 2019*. [doi:10.18653/v1/N19-1423](https://doi.org/10.18653/v1/N19-1423)
- Do, P., Coler, M., Dijkstra, J., & Klabbers, E. (2023). Strategies in transfer learning for low-resource speech synthesis: Phone mapping, features input, and source language selection. *Proceedings of the 12th ISCA Speech Synthesis Workshop*. [doi:10.21437/SSW.2023-4](https://doi.org/10.21437/SSW.2023-4)
- Dobler, K., & de Melo, G. (2023). FOCUS: Effective embedding initialization for monolingual specialization of multilingual models. *Proceedings of EMNLP 2023*. [doi:10.18653/v1/2023.emnlp-main.829](https://doi.org/10.18653/v1/2023.emnlp-main.829)
- Dodge, J., Ilharco, G., Schwartz, R., et al. (2020). Fine-tuning pretrained language models: Weight initializations, data orders, and early stopping. arXiv:2002.06305. [doi:10.48550/arXiv.2002.06305](https://doi.org/10.48550/arXiv.2002.06305)
- Downey, C. M., Blevins, T., Goldfine, N., & Steinert-Threlkeld, S. (2023). Embedding structure matters: Comparing methods to adapt multilingual vocabularies to new languages. *Proceedings of the 3rd Workshop on Multi-lingual Representation Learning*, 268–281. [doi:10.18653/v1/2023.mrl-1.20](https://doi.org/10.18653/v1/2023.mrl-1.20)
- Du, Z., Chen, Q., Zhang, S., et al. (2024a). CosyVoice: A scalable multilingual zero-shot text-to-speech synthesizer based on supervised semantic tokens. arXiv:2407.05407. [doi:10.48550/arXiv.2407.05407](https://doi.org/10.48550/arXiv.2407.05407)
- Du, Z., Wang, Y., Chen, Q., et al. (2024b). CosyVoice 2: Scalable streaming speech synthesis with large language models. arXiv:2412.10117. [doi:10.48550/arXiv.2412.10117](https://doi.org/10.48550/arXiv.2412.10117)
- Ebrahimi, A., & Kann, K. (2021). How to adapt your pretrained multilingual model to 1600 languages. *Proceedings of ACL-IJCNLP 2021*. [doi:10.18653/v1/2021.acl-long.351](https://doi.org/10.18653/v1/2021.acl-long.351)
- Efron, B., & Tibshirani, R. J. (1993). *An introduction to the bootstrap*. Chapman & Hall. [doi:10.1201/9780429246593](https://doi.org/10.1201/9780429246593)
- Gal, R., Alaluf, Y., Atzmon, Y., et al. (2023). An image is worth one word: Personalizing text-to-image generation using textual inversion. *Proceedings of ICLR 2023*. [doi:10.48550/arXiv.2208.01618](https://doi.org/10.48550/arXiv.2208.01618)
- Gorman, K., Mazovetskiy, G., & Nikolaev, V. (2018). Improving homograph disambiguation with supervised machine learning. *Proceedings of LREC 2018*. [doi:10.63317/26f425yehm3f](https://doi.org/10.63317/26f425yehm3f)
- Grave, E., Bojanowski, P., Gupta, P., Joulin, A., & Mikolov, T. (2018). Learning word vectors for 157 languages. *Proceedings of LREC 2018*. [doi:10.63317/2dwkd5xar3i5](https://doi.org/10.63317/2dwkd5xar3i5)
- Haig, G., & Öpengin, E. (2018). Kurmanjî Kurdish in Turkey: Structure, varieties and status. In C. Bulut (Ed.), *Linguistic minorities in Turkey and Turkic-speaking minorities of the peripheries*. Harrassowitz. [doi:10.2307/j.ctvckq4v1.12](https://doi.org/10.2307/j.ctvckq4v1.12)
- Haig, G., Vollmer, M., & Thiele, H. (2022). Northern Kurdish (Kurmanji) DoReCo dataset. In F. Seifart, L. Paschen & M. Stave (Eds.), *Language Documentation Reference Corpus (DoReCo) 1.2*. Berlin & Lyon. [doi:10.34847/nkl.ca10ez5t](https://doi.org/10.34847/nkl.ca10ez5t)
- Hanley, J. A., & McNeil, B. J. (1982). The meaning and use of the area under a receiver operating characteristic (ROC) curve. *Radiology, 143*(1), 29–36. [doi:10.1148/radiology.143.1.7063747](https://doi.org/10.1148/radiology.143.1.7063747)
- Hassani, H. (2018). BLARK for multi-dialect languages: Towards the Kurdish BLARK. *Language Resources and Evaluation, 52*. [doi:10.1007/s10579-017-9400-0](https://doi.org/10.1007/s10579-017-9400-0)
- Hayashi, T., Watanabe, S., Toda, T., et al. (2019). Pre-trained text embeddings for enhanced text-to-speech synthesis. *Proceedings of Interspeech 2019*. [doi:10.21437/Interspeech.2019-3177](https://doi.org/10.21437/Interspeech.2019-3177)
- Hsu, W.-N., Bolte, B., Tsai, Y.-H. H., et al. (2021). HuBERT: Self-supervised speech representation learning by masked prediction of hidden units. *IEEE/ACM Transactions on Audio, Speech, and Language Processing, 29*, 3451–3460. [doi:10.1109/TASLP.2021.3122291](https://doi.org/10.1109/TASLP.2021.3122291)
- Hu, E. J., Shen, Y., Wallis, P., et al. (2022). LoRA: Low-rank adaptation of large language models. *Proceedings of ICLR 2022*. [doi:10.48550/arXiv.2106.09685](https://doi.org/10.48550/arXiv.2106.09685)
- Hwang, J., Hira, M., Chen, C., et al. (2023). TorchAudio 2.1: Advancing speech recognition, self-supervised learning, and audio processing components for PyTorch. *Proceedings of IEEE ASRU 2023*. [doi:10.1109/ASRU57964.2023.10389648](https://doi.org/10.1109/ASRU57964.2023.10389648)
- Imani, A., Lin, P., Kargaran, A. H., et al. (2023). Glot500: Scaling multilingual corpora and language models to 500 languages. *Proceedings of ACL 2023*. [doi:10.18653/v1/2023.acl-long.61](https://doi.org/10.18653/v1/2023.acl-long.61)
- ITU-T (1996). *Recommendation P.800: Methods for subjective determination of transmission quality*. International Telecommunication Union.
- Jadoul, Y., Thompson, B., & de Boer, B. (2018). Introducing Parselmouth: A Python interface to Praat. *Journal of Phonetics, 71*, 1–15. [doi:10.1016/j.wocn.2018.07.001](https://doi.org/10.1016/j.wocn.2018.07.001)
- Jaff, D. Q., & Mohammadamini, M. (2026). FLEURS-Kobani: Extending FLEURS dataset for Northern Kurdish. *Proceedings of LREC 2026*. [doi:10.63317/267vdxnysvbe](https://doi.org/10.63317/267vdxnysvbe)
- Jia, Y., Zen, H., Shen, J., Zhang, Y., & Wu, Y. (2021). PnG BERT: Augmented BERT on phonemes and graphemes for neural TTS. *Proceedings of Interspeech 2021*. [doi:10.21437/Interspeech.2021-1757](https://doi.org/10.21437/Interspeech.2021-1757)
- Ju, Z., Wang, Y., Shen, K., et al. (2024). NaturalSpeech 3: Zero-shot speech synthesis with factorized codec and diffusion models. *Proceedings of ICML 2024*. [doi:10.48550/arXiv.2403.03100](https://doi.org/10.48550/arXiv.2403.03100)
- Karabax, A. (2013). *Rêzimana Kurdî ya Kurmancî, bi hîndarî* \[A Kurmanji Kurdish grammar, with exercises\].
- Kim, J., Kong, J., & Son, J. (2021). Conditional variational autoencoder with adversarial learning for end-to-end text-to-speech. *Proceedings of ICML 2021*. [doi:10.48550/arXiv.2106.06103](https://doi.org/10.48550/arXiv.2106.06103)
- Kim, S., Choi, S., & Jeong, M. (2024). Efficient and effective vocabulary expansion towards multilingual large language models. arXiv:2402.14714. [doi:10.48550/arXiv.2402.14714](https://doi.org/10.48550/arXiv.2402.14714)
- Kirkland, A., Mehta, S., Lameris, H., et al. (2023). Stuck in the MOS pit: A critical analysis of MOS test methodology in TTS evaluation. *Proceedings of the 12th ISCA Speech Synthesis Workshop*. [doi:10.21437/SSW.2023-7](https://doi.org/10.21437/SSW.2023-7)
- Koehn, P. (2004). Statistical significance tests for machine translation evaluation. *Proceedings of EMNLP 2004*. [aclanthology.org/W04-3250](https://aclanthology.org/W04-3250/)
- Kudo, T. (2018). Subword regularization: Improving neural network translation models with multiple subword candidates. *Proceedings of ACL 2018*. [doi:10.18653/v1/P18-1007](https://doi.org/10.18653/v1/P18-1007)
- Kudo, T., & Richardson, J. (2018). SentencePiece: A simple and language independent subword tokenizer and detokenizer for neural text processing. *Proceedings of EMNLP 2018: System Demonstrations*. [doi:10.18653/v1/D18-2012](https://doi.org/10.18653/v1/D18-2012)
- Łańcucki, A. (2021). FastPitch: Parallel text-to-speech with pitch prediction. *Proceedings of ICASSP 2021*. [doi:10.1109/ICASSP39728.2021.9413889](https://doi.org/10.1109/ICASSP39728.2021.9413889)
- Lester, B., Al-Rfou, R., & Constant, N. (2021). The power of scale for parameter-efficient prompt tuning. *Proceedings of EMNLP 2021*. [doi:10.18653/v1/2021.emnlp-main.243](https://doi.org/10.18653/v1/2021.emnlp-main.243)
- Li, B., Zhang, Y., Sainath, T., Wu, Y., & Chan, W. (2019). Bytes are all you need: End-to-end multilingual speech recognition and synthesis with bytes. *Proceedings of ICASSP 2019*. [doi:10.1109/ICASSP.2019.8682674](https://doi.org/10.1109/ICASSP.2019.8682674)
- Li, X. L., & Liang, P. (2021). Prefix-tuning: Optimizing continuous prompts for generation. *Proceedings of ACL-IJCNLP 2021*. [doi:10.18653/v1/2021.acl-long.353](https://doi.org/10.18653/v1/2021.acl-long.353)
- Li, Y. A., Han, C., Jiang, X., & Mesgarani, N. (2023). Phoneme-level BERT for enhanced prosody of text-to-speech with grapheme predictions. *Proceedings of ICASSP 2023*. [doi:10.1109/ICASSP49357.2023.10097074](https://doi.org/10.1109/ICASSP49357.2023.10097074)
- Liu, Y., Lin, P., Wang, M., & Schütze, H. (2024). OFA: A framework of initializing unseen subword embeddings for efficient large-scale multilingual continued pretraining. *Findings of NAACL 2024*. [doi:10.18653/v1/2024.findings-naacl.68](https://doi.org/10.18653/v1/2024.findings-naacl.68)
- Loshchilov, I., & Hutter, F. (2017). SGDR: Stochastic gradient descent with warm restarts. *Proceedings of ICLR 2017*. [doi:10.48550/arXiv.1608.03983](https://doi.org/10.48550/arXiv.1608.03983)
- Loshchilov, I., & Hutter, F. (2019). Decoupled weight decay regularization. *Proceedings of ICLR 2019*. [doi:10.48550/arXiv.1711.05101](https://doi.org/10.48550/arXiv.1711.05101)
- Lux, F., Meyer, S., Behringer, L., et al. (2024). Meta learning text-to-speech synthesis in over 7000 languages. *Proceedings of Interspeech 2024*. [doi:10.21437/Interspeech.2024-1335](https://doi.org/10.21437/Interspeech.2024-1335)
- Lux, F., & Vu, N. T. (2022). Language-agnostic meta-learning for low-resource text-to-speech with articulatory features. *Proceedings of ACL 2022*. [doi:10.18653/v1/2022.acl-long.472](https://doi.org/10.18653/v1/2022.acl-long.472)
- Marchisio, K., Lewis, P., Chen, Y., & Artetxe, M. (2023). Mini-model adaptation: Efficiently extending pretrained models to new languages via aligned shallow training. *Findings of ACL 2023*. [doi:10.18653/v1/2023.findings-acl.338](https://doi.org/10.18653/v1/2023.findings-acl.338)
- Mauch, M., & Dixon, S. (2014). pYIN: A fundamental frequency estimator using probabilistic threshold distributions. *Proceedings of ICASSP 2014*. [doi:10.1109/ICASSP.2014.6853678](https://doi.org/10.1109/ICASSP.2014.6853678)
- Mielke, S. J., Alyafeai, Z., Salesky, E., et al. (2021). Between words and characters: A brief history of open-vocabulary modeling and tokenization in NLP. arXiv:2112.10508. [doi:10.48550/arXiv.2112.10508](https://doi.org/10.48550/arXiv.2112.10508)
- Mikolov, T., Chen, K., Corrado, G., & Dean, J. (2013a). Efficient estimation of word representations in vector space. arXiv:1301.3781. [doi:10.48550/arXiv.1301.3781](https://doi.org/10.48550/arXiv.1301.3781)
- Mikolov, T., Sutskever, I., Chen, K., Corrado, G., & Dean, J. (2013b). Distributed representations of words and phrases and their compositionality. *Advances in NeurIPS 26*. [doi:10.48550/arXiv.1310.4546](https://doi.org/10.48550/arXiv.1310.4546)
- MiniCPM Team (2025). MiniCPM4: Ultra-efficient LLMs on end devices. arXiv:2506.07900. [doi:10.48550/arXiv.2506.07900](https://doi.org/10.48550/arXiv.2506.07900)
- Minixhofer, B., Paischer, F., & Rekabsaz, N. (2022). WECHSEL: Effective initialization of subword embeddings for cross-lingual transfer of monolingual language models. *Proceedings of NAACL 2022*. [doi:10.18653/v1/2022.naacl-main.293](https://doi.org/10.18653/v1/2022.naacl-main.293)
- Minixhofer, B., Ponti, E. M., & Vulić, I. (2024). Zero-shot tokenizer transfer. *Advances in NeurIPS 37*. [doi:10.48550/arXiv.2405.07883](https://doi.org/10.48550/arXiv.2405.07883)
- Mohammadamini, M., Sini, A., Tahon, M., & Laurent, A. (2025). Scaling pseudo-labeling data for end-to-end low-resource speech translation: The case of Kurdish language. *Proceedings of Interspeech 2025*. [doi:10.21437/Interspeech.2025-887](https://doi.org/10.21437/Interspeech.2025-887)
- Mortensen, D. R., Dalmia, S., & Littell, P. (2018). Epitran: Precision G2P for many languages. *Proceedings of LREC 2018*. [doi:10.63317/57n9v6em7ihu](https://doi.org/10.63317/57n9v6em7ihu)
- Muennighoff, N., Tazi, N., Magne, L., & Reimers, N. (2023). MTEB: Massive text embedding benchmark. *Proceedings of EACL 2023*. [doi:10.18653/v1/2023.eacl-main.148](https://doi.org/10.18653/v1/2023.eacl-main.148)
- Nekvinda, T., & Dušek, O. (2020). One model, many languages: Meta-learning for multilingual text-to-speech. *Proceedings of Interspeech 2020*. [doi:10.21437/Interspeech.2020-2679](https://doi.org/10.21437/Interspeech.2020-2679)
- Nguyen, L. T., Pham, T., & Nguyen, D. Q. (2023). XPhoneBERT: A pre-trained multilingual model for phoneme representations for text-to-speech. *Proceedings of Interspeech 2023*. [doi:10.21437/Interspeech.2023-444](https://doi.org/10.21437/Interspeech.2023-444)
- Nosek, B. A., Ebersole, C. R., DeHaven, A. C., & Mellor, D. T. (2018). The preregistration revolution. *Proceedings of the National Academy of Sciences, 115*(11), 2600–2606. [doi:10.1073/pnas.1708274114](https://doi.org/10.1073/pnas.1708274114)
- Omnilingual ASR Team, Keren, G., Kozhevnikov, A., Meng, Y., et al. (2025). Omnilingual ASR: Open-source multilingual speech recognition for 1600+ languages. arXiv:2511.09690. [doi:10.48550/arXiv.2511.09690](https://doi.org/10.48550/arXiv.2511.09690)
- Öpengin, E., & Haig, G. (2014). Regional variation in Kurmanji: A preliminary classification of dialects. *Kurdish Studies, 2*(2). [doi:10.33182/ks.v2i2.399](https://doi.org/10.33182/ks.v2i2.399)
- Pennington, J., Socher, R., & Manning, C. D. (2014). GloVe: Global vectors for word representation. *Proceedings of EMNLP 2014*. [doi:10.3115/v1/D14-1162](https://doi.org/10.3115/v1/D14-1162)
- Peters, M. E., Neumann, M., Iyyer, M., et al. (2018). Deep contextualized word representations. *Proceedings of NAACL-HLT 2018*. [doi:10.18653/v1/N18-1202](https://doi.org/10.18653/v1/N18-1202)
- Petrov, A., La Malfa, E., Torr, P. H. S., & Bibi, A. (2023). Language model tokenizers introduce unfairness between languages. *Advances in NeurIPS 36*. [doi:10.48550/arXiv.2305.15425](https://doi.org/10.48550/arXiv.2305.15425)
- Pfeiffer, J., Vulić, I., Gurevych, I., & Ruder, S. (2021). UNKs everywhere: Adapting multilingual language models to new scripts. *Proceedings of EMNLP 2021*. [doi:10.18653/v1/2021.emnlp-main.800](https://doi.org/10.18653/v1/2021.emnlp-main.800)
- Pratap, V., Tjandra, A., Shi, B., et al. (2024). Scaling speech technology to 1,000+ languages. *Journal of Machine Learning Research, 25*(97), 1–52. [doi:10.48550/arXiv.2305.13516](https://doi.org/10.48550/arXiv.2305.13516)
- Radford, A., Kim, J. W., Hallacy, C., et al. (2021). Learning transferable visual models from natural language supervision. *Proceedings of ICML 2021*. [doi:10.48550/arXiv.2103.00020](https://doi.org/10.48550/arXiv.2103.00020)
- Reimers, N., & Gurevych, I. (2017). Reporting score distributions makes a difference: Performance study of LSTM-networks for sequence tagging. *Proceedings of EMNLP 2017*. [doi:10.18653/v1/D17-1035](https://doi.org/10.18653/v1/D17-1035)
- Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. *Proceedings of EMNLP-IJCNLP 2019*. [doi:10.18653/v1/D19-1410](https://doi.org/10.18653/v1/D19-1410)
- Ren, Y., Hu, C., Tan, X., et al. (2021). FastSpeech 2: Fast and high-quality end-to-end text to speech. *Proceedings of ICLR 2021*. [doi:10.48550/arXiv.2006.04558](https://doi.org/10.48550/arXiv.2006.04558)
- Rust, P., Pfeiffer, J., Vulić, I., Ruder, S., & Gurevych, I. (2021). How good is your tokenizer? On the monolingual performance of multilingual language models. *Proceedings of ACL-IJCNLP 2021*. [doi:10.18653/v1/2021.acl-long.243](https://doi.org/10.18653/v1/2021.acl-long.243)
- Saeki, T., Maiti, S., Li, X., et al. (2023). Learning to speak from text: Zero-shot multilingual text-to-speech with unsupervised text pretraining. *Proceedings of IJCAI 2023*. [doi:10.24963/ijcai.2023/575](https://doi.org/10.24963/ijcai.2023/575)
- Saeki, T., Xin, D., Nakata, W., et al. (2022). UTMOS: UTokyo-SaruLab system for VoiceMOS Challenge 2022. *Proceedings of Interspeech 2022*. [doi:10.21437/Interspeech.2022-439](https://doi.org/10.21437/Interspeech.2022-439)
- Sennrich, R., Haddow, B., & Birch, A. (2016). Neural machine translation of rare words with subword units. *Proceedings of ACL 2016*. [doi:10.18653/v1/P16-1162](https://doi.org/10.18653/v1/P16-1162)
- Shen, J., Pang, R., Weiss, R. J., et al. (2018). Natural TTS synthesis by conditioning WaveNet on mel spectrogram predictions. *Proceedings of ICASSP 2018*. [doi:10.1109/ICASSP.2018.8461368](https://doi.org/10.1109/ICASSP.2018.8461368)
- Shen, K., Ju, Z., Tan, X., et al. (2024). NaturalSpeech 2: Latent diffusion models are natural and zero-shot speech and singing synthesizers. *Proceedings of ICLR 2024*. [doi:10.48550/arXiv.2304.09116](https://doi.org/10.48550/arXiv.2304.09116)
- Skerry-Ryan, R. J., Battenberg, E., Xiao, Y., et al. (2018). Towards end-to-end prosody transfer for expressive speech synthesis with Tacotron. *Proceedings of ICML 2018*. [doi:10.48550/arXiv.1803.09047](https://doi.org/10.48550/arXiv.1803.09047)
- Snyder, D., Garcia-Romero, D., Sell, G., Povey, D., & Khudanpur, S. (2018). X-vectors: Robust DNN embeddings for speaker recognition. *Proceedings of ICASSP 2018*. [doi:10.1109/ICASSP.2018.8461375](https://doi.org/10.1109/ICASSP.2018.8461375)
- Staib, M., Teh, T. H., Torresquintero, A., et al. (2020). Phonological features for 0-shot multilingual speech synthesis. *Proceedings of Interspeech 2020*. [doi:10.21437/Interspeech.2020-1821](https://doi.org/10.21437/Interspeech.2020-1821)
- Tan, S. (2011). *Rêzimana Kurmancî, çapa berfirehkirî* \[Kurmanji grammar, extended edition\]. Enstîtuya Kurdî ya Stenbolê.
- Tan, X., Chen, J., Liu, H., et al. (2024). NaturalSpeech: End-to-end text-to-speech synthesis with human-level quality. *IEEE Transactions on Pattern Analysis and Machine Intelligence*. [doi:10.1109/TPAMI.2024.3356232](https://doi.org/10.1109/TPAMI.2024.3356232)
- Taylor, J., & Richmond, K. (2019). Analysis of pronunciation learning in end-to-end speech synthesis. *Proceedings of Interspeech 2019*. [doi:10.21437/Interspeech.2019-2830](https://doi.org/10.21437/Interspeech.2019-2830)
- Thackston, W. M. (2006). *Kurmanji Kurdish: A reference grammar with selected readings*. Harvard University.
- van Miltenburg, E., van der Lee, C., & Krahmer, E. (2021). Preregistering NLP research. *Proceedings of NAACL-HLT 2021*. [doi:10.18653/v1/2021.naacl-main.51](https://doi.org/10.18653/v1/2021.naacl-main.51)
- Vaswani, A., Shazeer, N., Parmar, N., et al. (2017). Attention is all you need. *Advances in NeurIPS 30*. [doi:10.48550/arXiv.1706.03762](https://doi.org/10.48550/arXiv.1706.03762)
- Veisi, H., Hosseini, H., MohammadAmini, M., Fathy, W., & Mahmudi, A. (2022). Jira: A Central Kurdish speech recognition system, designing and building speech corpus and pronunciation lexicon. *Language Resources and Evaluation*. [doi:10.1007/s10579-022-09594-4](https://doi.org/10.1007/s10579-022-09594-4)
- VoxCPM Team (2026). VoxCPM2: Tokenizer-free TTS for multilingual speech generation, creative voice design, and true-to-life cloning \[model card\]. [huggingface.co/openbmb/VoxCPM2](https://huggingface.co/openbmb/VoxCPM2)
- Wang, C., Chen, S., Wu, Y., et al. (2023). Neural codec language models are zero-shot text to speech synthesizers. arXiv:2301.02111. [doi:10.48550/arXiv.2301.02111](https://doi.org/10.48550/arXiv.2301.02111)
- Wang, Y., Skerry-Ryan, R. J., Stanton, D., et al. (2017). Tacotron: Towards end-to-end speech synthesis. *Proceedings of Interspeech 2017*. [doi:10.21437/Interspeech.2017-1452](https://doi.org/10.21437/Interspeech.2017-1452)
- Wang, Y., Stanton, D., Zhang, Y., et al. (2018). Style tokens: Unsupervised style modeling, control and transfer in end-to-end speech synthesis. *Proceedings of ICML 2018*. [doi:10.48550/arXiv.1803.09017](https://doi.org/10.48550/arXiv.1803.09017)
- Wang, Z., K, K., Mayhew, S., & Roth, D. (2020). Extending multilingual BERT to low-resource languages. *Findings of EMNLP 2020*. [doi:10.18653/v1/2020.findings-emnlp.240](https://doi.org/10.18653/v1/2020.findings-emnlp.240)
- Wester, M., Valentini-Botinhao, C., & Henter, G. E. (2015). Are we using enough listeners? No! An empirically-supported critique of Interspeech 2014 TTS evaluations. *Proceedings of Interspeech 2015*. [doi:10.21437/Interspeech.2015-689](https://doi.org/10.21437/Interspeech.2015-689)
- Xue, L., Barua, A., Constant, N., et al. (2022). ByT5: Towards a token-free future with pre-trained byte-to-byte models. *Transactions of the ACL, 10*, 291–306. [doi:10.1162/tacl\_a\_00461](https://doi.org/10.1162/tacl_a_00461)
- Zhang, Y., Li, M., Long, D., et al. (2025). Qwen3 Embedding: Advancing text embedding and reranking through foundation models. arXiv:2506.05176. [doi:10.48550/arXiv.2506.05176](https://doi.org/10.48550/arXiv.2506.05176)
- Zhang, Y., Weiss, R. J., Zen, H., et al. (2019). Learning to speak fluently in a foreign language: Multilingual speech synthesis and cross-language voice cloning. *Proceedings of Interspeech 2019*. [doi:10.21437/Interspeech.2019-2668](https://doi.org/10.21437/Interspeech.2019-2668)
- Zhou, Y., Zeng, G., Liu, X., et al. (2025). VoxCPM: Tokenizer-free TTS for context-aware speech generation and true-to-life voice cloning. arXiv:2509.24650. [doi:10.48550/arXiv.2509.24650](https://doi.org/10.48550/arXiv.2509.24650)
- Zhu, J., Zhang, C., & Jurgens, D. (2022). ByT5 model for massively multilingual grapheme-to-phoneme conversion. *Proceedings of Interspeech 2022*. [doi:10.21437/Interspeech.2022-538](https://doi.org/10.21437/Interspeech.2022-538)
