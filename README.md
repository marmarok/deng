# Deng: guh û dengê kurdî

**Kurdî (Kurmancî)** · [English](#english)

**Pirs û bersiv:** [Kurdî](PIRS-U-BERSIV.md) · [Türkçe](SSS.md) · [English](FAQ.md)

Projeyeke vekirî ye û du armancên wê hene:

1. **Guh:** Modeleke ku axaftineke rojane ya kurdî fêm dike û dinivîse.
2. **Deng:** Dengekî kurdî yê ewqasî xwezayî ku axêverekî zikmakî nikaribe ferq bike ka mirov e an makîne ye.

Di kurdî de giranî û awaz her tişt e. Ji ber vê yekê em pêşî awazê dipîvin.

### Heta niha

- **Guh:** Bingeh **Omnilingual LLM-ASR 1B** e (Meta, Apache 2.0). Li ser heman 500 beşan guhê me cara yekem ji modela bingehîn çêtir derket: xeletiya peyvan %29,3 → %26,4. Perwerdeya tam didome.
- **Dane:** Ji arşîva Dengê Amerîka ~1.020 saet axaftin hatin berhevkirin (malê giştî). Berî perwerdeyê, her beş dê bi modeleke nasîna zimên bê kontrolkirin.
- **Deng:** VoxCPM2 (Apache 2.0) kurdî hîn dibe. Di ceribandina dawî de, li ser 257 hevokan, pirs bi qasî xwendevanên mirov rast in (%70; mirov %69); zelalî hîn tê baştirkirin.
- **Pîvera awazê:** Amûreke ku awaza dawiya hevokê dipîve û dibêje "pirs e an hevoka asayî ye".
- **Koma hevokên awazê:** 257 hevok, 14 cure. Ev hevok qet nakevin perwerdeyê.

Her gav bi dîrok, bi cihê ku lê hatiye kirin û bi encamê xwe di **[DEFTER.md](DEFTER.md)** de ye. Tiştên li dorê jî li wir in.

### Beşdar bibe

Ji bo piraniya karan kod ne pêwîst e; kurdî û telefonek bes e.

- **Edîtorê zimên:** Nivîsa makîneyê rast dike, qaîdeyên giranî û bilêvkirinê dinivîse.
- **Guhdar:** Dengan guhdarî dike û dibêje kîjan xwezayî ye. 15 deqe di du hefteyan de.
- **Xwediyê deng:** Bi dengê xwe dixwîne, bi peymaneke nivîskî.
- **Çavkanî û destûr:** Tomarên kurdî dibîne û destûrê dixwaze.
- **Bernameçêker:** Ne mecbûrî ye.

Ji bo pirs û pêşniyaran beşa **Issues** heye. Ji bo vê hesabekî belaş ê GitHubê bes e. Agahiyên kesane li vir nayên weşandin.

### Pel

| Peldank | Çi tê de ye |
|---|---|
| `kaggle/` | Ceribandin û perwerdeya guh li ser Kaggle (K2 ceribandin, K3 CTC, K4 LLM 1B) |
| `awaz/` | Pîvera awazê û koma hevokan |
| `guh/` | Nivîsandina reşnivîsê: LLM 1B nivîsê dide, CTC wextê peyvan |
| `nivis/` | Amadekirina nivîsê (hejmar, şapka ê/î/û) |
| `pivan/` | Encamên pîvanan (bi tirkî), di nav de dengên ku alfabe nîşan nade |
| `dane/` | Lîsteya hemû tomaran: kîjan ketiye perwerdeyê, kîjan li dorê ye |
| `DEFTER.md` | Hemû gav û yên li dorê |

Lîsans: MIT (kod). Daneyên kesên din li vir nînin.

---

## English

An open project with two goals for **Kurdish (Kurmanji)**:

1. **Ear:** a speech recognizer that understands everyday conversational Kurdish.
2. **Voice:** a Kurdish voice so natural that native speakers cannot tell it from a human.

In Kurdish, stress and intonation carry meaning, so prosody is measured first.

### So far

- **Speech recognition:** We benchmarked open models on Kurmanji (FLEURS and Common Voice).
  - The chosen base is Meta's **Omnilingual LLM-ASR 1B** (Apache 2.0). Zero-shot it gets 31.4% WER and 9.1% CER on FLEURS, and 16.4% WER and 4.1% CER on Common Voice 27.
  - Fine-tuning on free Kaggle T4s is running: the audio encoder is trained and the language model is frozen.
- **Intonation judge:** A small logistic model on the final pitch contour that tells yes/no questions from statements.
  - On human Common Voice reads, it rates 89% of statements and 69% of questions as such.
  - Current TTS models get question intonation right less than half the time.
- **Prosody test set:** 257 sentences in 14 types, mostly from Common Voice (CC0). These sentences are locked and never used for training.

Results are in `pivan/` (in Turkish). Code is MIT-licensed. No third-party recordings are included.
