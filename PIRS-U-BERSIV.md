# Pirs û bersiv

*Türkçe: [SSS.md](SSS.md) · English: [FAQ.md](FAQ.md) · Nûkirina dawî: 18ê Cotmeha 2026an*

Ev pirs ji wan pirsên ku birêvebirê projeyê heta niha pirsîne û ji yên ku kesê li projeyê dinêre dikare bipirse hatine berhevkirin. Hemû hejmar ji pelên pîvanan hatine girtin (`pivan/`, `dane/`, `DEFTER.md`). Heke hejmarek xelet an kêm be, ji kerema xwe li GitHubê di beşa "Issues" de binivîsin.

## Proje

**1. Deng çi ye?**
Projeyeke vekirî ye ku ji bo kurdî du modelên hişê çêkirî fêrî kurdî dike.
- **Guh:** Axaftina kurdî guhdarî dike û dinivîse. Armanc ew e ku sohbeteke asayî fêm bike.
- **Deng:** Nivîsê bi kurdî dixwîne. Armanc dengekî ewqas xwezayî ye ku guhdarekî kurd nikaribe wî ji dengê mirovan cuda bike.

**2. Çima pêwîst e?**
Ji bo zimanên mezin ev amûr hene; ji bo kurdî tune ne an jî gelek qels in. Dengên makîneyê yên îroyîn kurdî bi devê biyaniyan dixwînin: giranî li cihê xelet dikeve, pirs wek hevoka asayî tê gotin. Di kurdî de giranî û awaz wateyê hildigirin. Ji ber vê yekê em wan ji roja yekem ve dipîvin.

**3. Kî projeyê dimeşîne? Kî kodê dinivîse?**
- **Birêvebirê projeyê:** Kurdî zimanê wî yê dayikê ye. Ew ne bernameçêker e û berê qet modeleke hişê çêkirî perwerde nekiribû. Biryar û berpirsiyarî yên wî ne.
- **Kod, pîvan û hesab:** Ji aliyê Claude ve tên kirin. Claude hişê çêkirî yê şîrketa Anthropic e.
- **Ekîb:** Du hevalên ekîbê bi hesabên xwe yên Kaggle hêza komputerê didin.

Em vê yekê vekirî dibêjin. Tiştê girîng ne ew e ku kî kodê dinivîse; tiştê girîng ew e ku encam tê pîvandin û her kes dikare wê bibîne.

**4. Mirov dikare ji kod û hejmarên ku hişê çêkirî nivîsîne bawer bike?**
Divê mirov bi çavên girtî bawer neke. Ji ber vê yekê:
- Her hejmar ji pelekî pîvanê tê.
- Kod vekirî ye; kesê bixwaze dikare heman karî dîsa bimeşîne.
- Xeletî tên nivîsîn. Mînak: rêjeya awaza pirsan pêşî ji komeke 15 hevokan wek %87 hatibû nivîsîn. Di koma tevahî de %66 derket û li her derê hate rastkirin.

Kontrola rastîn guhdariya kesên ku kurdî zimanê wan ê dayikê ye (binêre pirsa 25an).

**5. Armanc çi ye? Kengî diqede?**
- **Serkeftin:** Guhdarên kurd nikaribin bibêjin ka deng mirov e an makîne. Guh jî sohbetê di 100 tîpan de herî zêde bi 5 xeletiyan binivîse.
- **Dem:** Texmîna me heta salên 2027 û 2028an e. Ev texmîn e; di dawiya her qonaxê de em dipîvin û rast dikin.

**6. Kîjan kurdî?**
- **Zimanê sereke:** Kurmanciya standard e, yanî zimanê nivîs, pirtûk û nûçeyan. Deng bi xwe bi vî zimanî diaxive.
- **Guh:** Divê hemû devokan fêm bike.
- **Devok:** Herêma her tomarê tê nîşankirin. Komên devokan ji zimanzanan hatine girtin: Öpengin û Haig (2014), pênc herêm. Gava ku deng bi kurdiya standard xwezayî bibe, dê bi devokan jî biaxive.

**7. Soranî, zazakî an zimanên din?**
Niha tenê kurmancî. Em dixwazin pêşî zimanekî baş bikin. Yên din dê gava ekîb û dane mezin bibin werin nîqaşkirin.

## Çawa dixebite

**8. Guh çawa fêr dibe?**
Em modeleke bingehîn a amade digirin û dengê kurdî bi nivîsa wê ya rast nîşanî wê didin.
- **Modela bingehîn:** Omnilingual ASR ya Meta (1 milyar parametre, lîsansa Apache 2.0). Zêdeyî 1.600 zimanan dizane, lê di kurdî de qels e.
- **Daneya kurdî:** Nêzîkî 61 saet tomarên kurdî bi nivîsên wan, ji Common Voice û FLEURSê.
- **Fêrbûn:** Model hîn dibe ku ferqa di navbera nivîsa xwe û nivîsa rast de biçûk bike.

**9. Deng çawa fêr dibe?**
- **Modela bingehîn:** VoxCPM2 (Apache 2.0). Tirkî û erebî dizane, kurdî nizane.
- **Perwerde:** Bi perwerdeyeke sivik (LoRA) em xwendina kurdî didin hînkirin.
- **Pîvan:** Piştî her ceribandinê deng bi du awayan tê pîvandin:
  - **Zelalî:** Guhekî din ê makîneyê wê dinivîse.
  - **Awaz:** Pîvera awazê dinêre ka pirs wek pirsê tên gotin an na.

**10. Hesab li ku tên kirin?**
- **Kaggle:** Li ser kartên grafîkê yên belaş ên Googleê. Ji bo her hesabî di hefteyê de nêzîkî 30 saet.
- **Her kar li hesabekî:** Guh, deng û rêzika daneyan li hesabên cuda dimeşin; hesab tevlihev nabin.
- **Defter:** DEFTER.md dinivîse ka her kar li ku hatiye kirin: karta grafîkê, pêvajoker, Claude bi xwe an Mac.

**11. Çiqas pere hatiye xerckirin?**
Heta niha qet. Her xerc bi erêkirina birêvebirê projeyê ve girêdayî ye.

**12. Parçeker çi ye? Divê ji bo kurdî were guhertin?**
- **Çi dike:** Model nivîsê ne wek tîp an peyv, wek perçeyên biçûk dibîne. Amûra ku nivîsê dike perçe jê re parçeker tê gotin.
- **Di guh de:** Parçeker hemû tîpên kurdî nas dike; tîpeke nenas tune.
- **Di deng de:** Peyveke kurdî bi navînî dibe 2,83 perçe; di îngilîzî de ev 1,35 e, di tirkî de 4,18. ê, î, û, ç û ş perçeyên cuda ne.
- **Biryar:** Niha em wê naguherînin. Heke parçeker were guhertin, divê model hevberên peyvan ji nû ve hîn bibe; bi qasî daneya me ev xeternak e. Ceribandina parçekerê ji bo Kanûnê hatiye plankirin.

**13. Di kurdî de ji tîpan zêdetir deng hene?**
Erê. Di alfabeyê de 31 tîp hene, lê zimanzan zêdetir dengan dihejmêrin:
- **Bi bêhn û bê bêhn:** p, t, k û ç her yek bi du awayan.
- **Du r û du l.**
- **Dengên din:** ḧ, ʿ, ẍ, ŋ û xʷ.

Çavkanî: Samî Tan; Barzo Omar Mahmoud (2016). Guh bi rênivîsa standard dinivîse. Deng van cudahiyan ji tomaran dibihîze û hîn dibe. Paşê dê qateke bilêvkirinê ya cuda were ceribandin. Hûragahî: `pivan/dengen-kurdi.md`.

**14. Giranî û awaz çawa tên pîvandin?**
- **Koma awazê:** 257 hevok. Cureyên wê: cotên hevoka asayî û pirsê, pirsên bi peyva pirsê, pirsên "gelo" û "ma", ferman, gazî, hest, diyalog û yên din. Ev hevok qet nakevin perwerdeyê.
- **Pîvera awazê:** Li xêza bilindiya dengê her xwendinê dinêre û biryar dide ka wek pirsê ye an na.
- **Kêmasiya pîverê:** Di xwendinên mirovan de %69ê pirsan û %89ê hevokên asayî rast nas dike. Ji ber vê yekê dadwerê rastîn guhê mirov e.

## Dane

**15. Kîjan dane tên bikaranîn?**

| Çavkanî | Lîsans | Çiqas | Rewş |
|---|---|---|---|
| Common Voice 27 (kurmancî) | CC0 | 44.549 beş, 49,8 saet | ✅ ketiye perwerdeya guh |
| FLEURS (kurmancî) | CC BY 4.0 | 3.556 beş, 11,7 saet | ✅ ketiye perwerdeya guh |
| Arşîva Dengê Amerîka | Malê giştî (tenê yên ku VOA bi xwe çêkirine) | ~2.700 tomar, ~1.020 saet | ⬜ li dorê ye (pêşî kontrola zimên) |

Lîsteya tevahî: `dane/`.

**16. Hûn çawa dizanin ku tomarek bi rastî kurdî ye?**
- **Common Voice û FLEURS:** Jixwe kurdî ne. Di Common Voice de her tomar ji aliyê dilxwazên din ve tê guhdarîkirin û pejirandin.
- **Dengê Amerîka:** Di arşîvê de dibe ku mêvanên bi tirkî, erebî an îngilîzî diaxivin û muzîk hebin. Ji ber vê yekê divê her beş ji du kontrolan derbas bibe:
  - **Naskirina zimên ji dengê:** MMS-LID.
  - **Naskirina zimên ji nivîsê:** GlotLID.
- **Sînor:** Bi tomarên ku em dizanin kurdî ne tê diyarkirin.
- **Kontrola mirovan:** Kesekî ku kurdî zimanê wî yê dayikê ye, mînakên ji yên derbasbûyî û yên mayî guhdarî dike.

Qaîdeyên tevahî: `dane/qaideyen-ketina-perwerdeye.json`.

**17. Ez çawa dikarim bizanim ku we bi rastî ev tomar bi kar anîne û ji xwe çênekirine?**
- **Navê her tomarê:** Navê her tomara ku hatiye bikaranîn di `dane/` de nivîsî ye. Navên Common Voice û FLEURSê di pelên wan ên vekirî de dikarin werin dîtin.
- **Dengê Amerîka:** Girêdana malperê û dirêjiya her tomarê dê di lîsteyê de be. Hûn dikarin lê bitikînin û dirêjiyê berhev bikin.
- **Hûn bi xwe jî dikarin kontrol bikin:** Kod û encam vekirî ne; hûn dikarin karekî dîsa bimeşînin û heman hejmarê bistînin.

**18. Çiqas dane pêwîst e? Ji ku derê tê?**
- **Ji bo deng:** Rêbera modela bingehîn ji bo zimanekî nû zêdeyî 500 saet dengê paqij pêşniyar dike. Îro 61,5 saet di perwerdeyê de ne.
- **Çavkanî:**
  - Dengê Amerîka (~1.020 saet, li benda kontrolê ye)
  - radyo, podkast û pirtûkên dengî yên ku me destûr ji wan xwestiye (name hatine şandin, li benda destûra nivîskî ne)
  - xwendin û sohbetên dilxwazan

**19. Tomar li gorî kalîteyê tên dabeşkirin?**
Erê, çar çîn hene. Her beş bixweber tê pîvandin: deng û qerebalix, dengê telefonê, muzîk. Cureyê tomarê (stûdyo, telefon, radyo, YouTube, qehwexane…) jî tê nivîsîn.

| Çîn | Çi | Guh | Deng |
|---|---|---|---|
| A | Kalîteya stûdyoyê | ✅ | ✅ |
| B | Tomara paqij | ✅ | ✅ |
| C | Dengê telefonê an odeyê | ✅ | ❌ |
| D | Bi qerebalix an muzîk | ✅ | ❌ |

- **Çima guh hemûyan digire:** Tomarên xirab wî ji jiyana rastîn re amade dikin.
- **Çima deng tenê A û B digire:** Modela deng qerebalixê jî teqlîd dike.

**20. Hûn "tomarên pirsan" çawa hildibijêrin?**
- **Ji nivîsê:** Di Common Voice de hevoka ku hatiye xwendin bi tomarê re nivîsî ye. Heke bi "?" biqede, wek pirs tê hejmartin.
- **Cureyê pirsê:** Heke peyveke pirsê hebe (çi, kî, kengî, çawa…), pirsa bi peyva pirsê ye; heke tune be, pirsa erê/na ye. Vê yekê qaîdeyeke sabît diyar dike, ne modeleke zimên.
- **Ji dengê:** Hin xwendevan pirsê wek hevoka asayî dixwînin. Pîvera awazê wan derdixe.

**21. Mafê telîfê û destûr çawa ne?**
- **Lîsans:** Tenê daneyên bi lîsansa vekirî an malê giştî tên bikaranîn.
- **Dengê Amerîka:** Tenê tiştên ku VOA bi xwe çêkirine malê giştî ne. Yên AP, Reuters û AFPê ne wisa ne, ji ber vê yekê beşa vîdyoyan li derve ye.
- **Çavkaniyên bi destûr:** Destûr divê bi destnivîsê, bi dîrok û îmze be. Bi rêyeke duyem tê piştrastkirin.

**22. Hevokên ezmûnê dikevin perwerdeyê?**
Na. Komên ezmûnê kilîtkirî ne; kod hevoka ezmûnê ya ku bixwaze bikeve perwerdeyê red dike. Modela ku hevokên ezmûnê berê dîtibin, encameke derew dide.

## Encam

**23. Guh çiqas baş e? CER û WER çi ne?**
- **CER:** Di 100 tîpan de çend tîp xelet in.
- **WER:** Di 100 peyvan de çend peyv xelet in.

Guhê herî baş, 18ê Cotmehê 2026:

| Ezmûn | Modela bingehîn | Guhê me |
|---|---|---|
| WER di heman 500 beşan de | %29,3 | **%24,3** |
| Hemû 999 beş | — | CER %7,1 · WER %24,2 |
| Common Voice | — | WER %13,4 |
| FLEURS | — | WER %27,4 |

Armanc di sohbetê de di 100 tîpan de herî zêde 5 xeletî ye. Em hîn di rê de ne.

**24. Rewşa deng çawa ye?**
- **Awaz:** Di ceribandina dawî de (257 hevok) %70ê pirsan wek pirsê hatin gotin. Di xwendinên mirovan de ev %69 e.
- **Zelalî:** Hîn têr nake; di 100 tîpan de nêzîkî 16 xeletî.
- **Çareya sereke:** Bêtir dengê kurdî yê paqij.

**25. Kî encamên ezmûnê dixwîne? Ew rastiyê nîşan didin?**
- **Kî encamê derdixe:** Ne mirov, hesabek. Nivîsa guh tîp bi tîp bi nivîsa rast a çavkaniyê re tê berhevkirin.
- **Kengî ewle ye:** Ji bo berhevkirina modelan bi hev re, ji ber ku ezmûn û pîvan her heman in.
- **Çima ne rastiya mutleq e:**
  - Cudahiyên rênivîsê jî wek xeletî tên hejmartin.
  - Dibe ku di nivîsên çavkaniyê bi xwe de jî xeletî hebin.
  - Ezmûn axaftina xwendinê ye, ne sohbet e.
- **Çare:** Kesên ku kurdî zimanê wan ê dayikê ye guhdarî dikin. Li ser rûpeleke kontrolê, hevokên ezmûnê yek bi yek tên pejirandin. Rûpeleke guhdariyê jî tê amadekirin:
  - **Guh:** 50 beş.
  - **Deng:** 30 hevok. Her hevok bi xwendina mirovekî re jî, bi rêzeke tevlihev, tê guhdarîkirin.

**26. "Nayê cudakirin" dê çawa were pîvandin?**
- **Guhdar:** 30–50 guhdar ji herêmên cuda, bêyî ku bizanin kîjan kîjan e, xwendina mirov û makîneyê ya heman nivîsê guhdarî dikin.
- **Serkeftin:** Guhdar herî zêde di %55ê caran de mirov dizanin (avêtina pereyekî %50 e).
- **Sê ezmûn:** hevokên kurt, paragrafên dirêj û sohbet.

## Beşdarbûn

**27. Ji bo beşdarbûnê zanîna kodê pêwîst e?**
Na. Ji bo piraniya karan kurdî û telefonek bes e. Dilxwazên ku kodê dizanin jî dikarin beşdar bibin.

**28. Hesabê Claude pêwîst e?**
Na. Karên hişê çêkirî ji aliyê projeyê ve tên kirin; beşdar guhdarî dikin, dixwînin, rast dikin û tomar dikin.

**29. Kîjan kar hene?**

| Kar | Çi dike | Ked |
|---|---|---|
| Edîtorê zimên | Nivîsa makîneyê rast dike; qaîdeyên giranî û bilêvkirinê dinivîse | Di hefteyê de 2–3 saet |
| Guhdar | Dengan guhdarî dike û dibêje kîjan xwezayî ye | Di du hefteyan de 15 deqe |
| Xwediyê deng | Bi dengê xwe hevokan dixwîne (jinek û mêrek tên bijartin) | Di dema tomarê de, di hefteyê de 4–6 saet |
| Çavkanî û destûr | Radyo, podkast û pirtûkên kurdî dibîne; destûr dixwaze | Di hefteyê de 1–2 saet |
| Axêverê devokê | Carekê 10–15 deqe bi devoka xwe diaxive | Carekê |
| Bernameçêker (ne mecbûrî) | Kod, pîvan, amûr | Çiqas bixwaze |

**30. Kî dikare beşdar bibe, kî nikare?**
- **Kî dikare:** Her kesê ku bi kurdî diaxive. Ji bo edîtoriyê xwendin û nivîsîna kurdî ya baş pêwîst e.
- **Sînor:**
  - Kesên ji 18 salî biçûktir tenê bi destûra nivîskî ya malbata xwe dikarin dengê xwe tomar bikin.
  - Kesê ku dengê xwe dide, peymaneke nivîskî îmze dike.
  - Bê destûra xwediyê wan, tomarên kesên din nayên şandin.

**31. Ez çawa beşdar dibim?**
1. Li GitHubê li projeyê binêrin: github.com/marmarok/deng
2. Bi rêya Tirşikê an di beşa "Issues" a GitHubê de binivîsin. Van binivîsin:
   - nav an nasnav
   - kîjan kar
   - bajar û navçeya ku lê mezin bûne
   - di hefteyê de çend saet
3. Hûn karekî biçûk ê ceribandinê dikin: rastkirina 10 hevokan, an 15 deqe guhdarî.
4. Heke hûn dengê xwe bidin, hûn peymaneke nivîskî îmze dikin.

**32. Heke ez dengê xwe bidim, çi dibe? Mafê min çi ye?**
- **Peyman:** Dengê we bi peymaneke nivîskî tê girtin; ji bo çi were bikaranîn di wê de nivîsî ye.
- **Tomar li ku dimînin:** Tomar tenê di hesabê veşartî yê birêvebirê projeyê de tên xebitandin; naçin hesabekî din.
- **Vegirtina destûrê:** Heke hûn destûra xwe vegerînin, tomara we nakeve modelên paşê.
- **Kopîkirin:** Gava model were belavkirin, kopîkirina dengê kesên din dê girtî be.

**33. Agahiyên min ên kesane tên weşandin?**
Na. Li ser rûpelên vekirî tenê navê ku hûn destûr didin xuya dike. Berî her weşanê kontrola agahiyên kesane tê kirin.

**34. GitHub çi ye?**
Malperek e ku kod, plan û encam lê vekirî tên parastin.
- **Ji bo xwendinê:** Hesab ne pêwîst e.
- **Ji bo pirs û pêşniyaran:** Hesabekî belaş bes e; beşa "Issues" ji bo vê ye.
- **Li vir çi heye:**
  - **README:** kurteya projeyê
  - **DEFTER:** rojnivîska karan bi dîrok
  - **dane:** lîsteya hemû daneyan
  - **pivan:** encamên pîvanan
  - **awaz:** hevokên awazê
  - **kod:** vekirî

**35. Bi pere ye? Heke dahat çêbibe çi dibe?**
Beşdarbûn bi dilxwazî û belaş e. Navê beşdaran di lîsteya "Keda wan heye" de tê nivîsîn û ew modelê belaş bi kar tînin. Heke rojekê dahat çêbibe, para beşdaran berê bi nivîskî tê diyarkirin.

**36. Model ya kê ye? Lîsansa wê çi ye?**
- **Kod:** Vekirî ye, bi lîsansa MIT.
- **Lîsansa modelê:** Hîn nehatiye biryardan. Biryar dê vekirî were ragihandin.

**37. Zekayên sûnî yên belaş tên bikaranîn?**
- **Sînorê karanînê:** Mafê karanîna Claude sînorkirî ye, ji ber vê yekê hin kar li amûrên din tên belavkirin.
- **Nûkirinên rojane:** Bi skrîptên hêsan tên kirin.
- **Karên nivîsa kurdî:** Gemini ya belaş a Googleê tê fikirîn, tenê bi daneyên vekirî.
- **Modelên herêmî:** Di kurdî de qels in, ji ber vê yekê nayên bikaranîn.

## Ewlehî û xeter

**38. Heke hişê çêkirî tiştan ji xwe çêbike, çi dibe?**
- **Hejmar ji ku tên:** Her hejmar bi pelekî pîvanê ve girêdayî ye. Encameke ku di pelekî de tune be nayê gotin.
- **Tiştên nenas:** Tiştên ku nayên zanîn wek "texmîn" tên nivîsîn.
- **Mînakên kurdî:** Di mînakên kurdî de xetera çêkirinê heye, ji ber vê yekê kesekî ku kurdî zimanê wî yê dayikê ye kontrol dike. Mînak: cotê "ker/kerr" carekê wek mînakeke xelet hatibû nivîsîn; hate rastkirin.

**39. Heke xeletî çêbibe, çawa tê rastkirin?**
- **Tomar:** Xeletî bi dîrok di DEFTERê de tê nivîsîn.
- **Planên kevn:** Nayên jêbirin, diçin arşîvê.
- **Hûn jî dikarin ragihînin:** Gava hûn xeletiyekê bibînin, di beşa "Issues" de binivîsin.

**40. Deng dikare bi awayekî xirab were bikaranîn (dengê sexte)?**
Ev xetereyeke rastîn e.
- **Di belavkirinê de:** Kopîkirina dengê kesên din dê girtî be. Danîna mohreke veşartî di nav deng de tê fikirîn.
- **Di perwerdeyê de:** Tenê tomarên bi destûr tên bikaranîn.

**41. Heke proje di nîvê rê de bimîne, çi dibe?**
- **Belge:** Her biryar û her pîvan nivîsî ye; heke kesek biçe jî kar ji serî dest pê nake.
- **Kod:** Vekirî ye, kesê bixwaze dikare bidomîne.
- **Her qonax bi serê xwe tiştekî dihêle:** Mînak, guhê îroyîn jî ji modela bingehîn baştir e.
