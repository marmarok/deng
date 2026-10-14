# Deng: guh û dengê kurdî

**Kurdî (Kurmancî)** · [English](#english)

Projeyeke vekirî ye û du armancên wê hene:

1. **Guh:** Modeleke ku axaftineke rojane ya kurdî fêm dike û dinivîse.
2. **Deng:** Dengekî kurdî yê ewqasî xwezayî ku axêverekî zikmakî nikaribe ferq bike ka mirov e an makîne ye.

Di kurdî de giranî û awaz her tişt e. Ji ber vê yekê em pêşî awazê dipîvin.

### Heta niha

- **Guh:** Me modelên vekirî li ser kurmancî ceriband (FLEURS û Common Voice). Bingeha guh **Omnilingual LLM-ASR 1B** e (Apache 2.0): bêyî perwerdeyê, li ser FLEURS ji 100 peyvan 31 xelet. Perwerdeya wê dest pê kiriye.
- **Hakemê awazê:** Amûreke ku awaza dawiya hevokê dipîve û dibêje "pirs e an hevoka asayî ye". Dengên makîneyê yên îroyîn pirsên erê/na di kêmtirî nîvê de rast dibêjin; xwendevanên mirov di %69 de.
- **Koma hevokên awazê:** 257 hevok, 14 cure (pirs, ferman, gazî, hest, diyalog…). Piraniya wan ji Common Voice in (CC0). Ev hevok qet nakevin perwerdeyê.

### Pel

| Peldank | Çi tê de ye |
|---|---|
| `kaggle/` | Ceribandin û perwerdeya guh li ser Kaggle (K2 ceribandin, K3 CTC, K4 LLM 1B) |
| `ezgi/` | Hakemê awazê û koma hevokan |
| `kulak/` | Nivîsandina reşnivîsê: LLM 1B nivîsê dide, CTC wextê peyvan |
| `metin/` | Amadekirina nivîsê (hejmar, şapka ê/î/û) |
| `olcumler/` | Encamên pîvanan (bi tirkî) |

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

Results are in `olcumler/` (in Turkish). Code is MIT-licensed. No third-party recordings are included.
