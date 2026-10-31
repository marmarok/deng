# Qata zimanê kurmancî

Ev qat qaîdeyên du pirtûkên rêzimana kurmancî dike kod: dengên zimên, hece, lêker û giranî. Ji bo guh û dengê me tê bikaranîn. Nivîsa pirtûkan li vir nîne.

| Pel | Çi dike |
|---|---|
| `ses.py` | Tîp, deng, hece, IPA. `xw` yek deng e. |
| `fiil.py` | Lêker: du reh, pêşgir, paşgir. |
| `vurgu.py` | Giranî di peyv û hevokê de. `hátin` (ew hatin) û `hatín` (rader) ji hev cuda dike. |
| `kanonik.py` | Ji bo her peyvê yek şêweya nivîsê: cudahiya rastnivîsê wek xeletiya guh nayê jimartin. |
| `hata_turu.py` | Xeletiyên guh li gorî cureyê wan dabeş dike. |
| `kmr_token.py` | Ji bo deng rêzek nîşanan: her deng yek nîşan, `xw` yek, nîşana giraniyê bijarte ye. |
| `vurgu_olcum.py`, `olc_worker.py` | Qaîdeyên giraniyê li ser axaftina rastîn dipîve. |

Qaîdeyên giraniyê hîpotez in. Pirtûk bi xwe jî dibêjin ku ev mijar hîn ne xelas e. Ji ber vê yekê her qaîde li ser dengê rastîn tê pîvan û encam di `pivan/` de ye.

## English

This layer turns the rules of two Kurmanji grammars into code: sounds, syllables, verbs and stress. Our ear and voice use it. The books' text is not here.

The stress rules are a hypothesis: the grammars themselves warn that the subject is unsettled, so every rule is tested on real speech and the result goes to `pivan/`.

```bash
python3 nivis/kurmanci/test_kurmanci.py
python3 nivis/kurmanci/kmr_token.py "Ew duh hatin, lê hatin ne hêsan bû."
```
