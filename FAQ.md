# Frequently asked questions

*Kurdî: [PIRS-U-BERSIV.md](PIRS-U-BERSIV.md) · Türkçe: [SSS.md](SSS.md) · Last updated: 18 October 2026*

These questions come from what the project lead has asked so far and from what someone looking at the project is likely to ask. Every number comes from the measurement files (`pivan/`, `dane/`, `DEFTER.md`). If a number is wrong or missing, please open an Issue on GitHub.

## The project

**1. What is Deng?**
An open project building two AI models for Kurdish:
- **The ear:** listens to Kurdish speech and writes it down. The goal is to understand an ordinary conversation.
- **The voice:** reads text aloud in Kurdish. The goal is a voice so natural that a native Kurdish listener cannot tell it from a person.

**2. Why is it needed?**
Large languages have these tools; Kurdish has none, or very weak ones. Today's machine voices read Kurdish with a foreign accent: stress falls in the wrong place and questions sound like statements. In Kurdish, stress and intonation carry meaning, so we measure them from day one.

**3. Who runs it? Who writes the code?**
- **The project lead:** A native Kurdish speaker who is not a programmer and had never trained an AI model before. Decisions and responsibility are theirs.
- **Code, measurements and calculations:** Written by Claude, an AI made by Anthropic.
- **The team:** Two teammates give computing time through their own Kaggle accounts.

We say this openly. What matters is not who writes the code, but that every result is measured and visible to everyone.

**4. Can you trust code and numbers written by an AI?**
Not blindly. That is why:
- Every number comes from a result file.
- The code is open, so anyone can run the same job again.
- Mistakes are recorded. For example, a question-intonation score was first reported as 87% from a 15-sentence set. On the full set it was 66%, and it was corrected everywhere.

The real check is native speakers listening (see question 25).

**5. What is the goal? When will it be done?**
- **Definition of success:** Native Kurdish listeners cannot tell whether the voice is a person or a machine, and the ear writes conversation with at most 5 errors per 100 letters.
- **Timeline:** Our estimate runs into 2027 and 2028. This is an estimate; we measure and adjust at the end of every stage.

**6. Which Kurdish?**
- **Main language:** Standard Kurmanji, the language of writing, books and news. The voice speaks it by default.
- **The ear:** Should understand every dialect.
- **Dialects:** Every recording is labelled with its region. The dialect groups come from linguists: Öpengin and Haig (2014), five regions. The voice will speak dialects once the standard voice sounds natural.

**7. What about Sorani, Zazaki or other languages?**
Kurmanji only for now. We want to do one language well first. The others can be discussed once the team and the data grow.

## How it works

**8. How does the ear learn?**
We take an existing base model and show it Kurdish audio with the correct text.
- **Base model:** Meta's Omnilingual ASR (1 billion parameters, Apache 2.0). It knows over 1,600 languages but is weak in Kurdish.
- **Kurdish data:** About 61 hours of Kurdish recordings with their text, from Common Voice and FLEURS.
- **Learning:** The model learns to shrink the gap between what it writes and the correct text.

**9. How does the voice learn?**
- **Base model:** VoxCPM2 (Apache 2.0). It knows Turkish and Arabic, but not Kurdish.
- **Training:** A light training method (LoRA) teaches it to read Kurdish.
- **Measurement:** After each trial the voice is measured in two ways:
  - **Intelligibility:** Another machine ear transcribes it.
  - **Intonation:** An intonation judge checks whether questions sound like questions.

**10. Where does the computing happen?**
- **Kaggle:** On Google's free graphics cards, about 30 hours a week per account.
- **One job per account:** The ear, the voice and the data pipeline each run on their own account, and the accounts are never mixed.
- **The log:** DEFTER.md records where each job ran: graphics card, processor, Claude itself, or the Mac.

**11. How much money has been spent?**
Zero so far. Any spending needs the project lead's approval.

**12. What is a tokenizer? Should it be adapted to Kurdish?**
- **What it does:** A model does not see text as letters or words but as small pieces. The tool that cuts text into those pieces is the tokenizer.
- **The ear:** Its tokenizer knows every Kurdish letter; none are unknown.
- **The voice:** A Kurdish word becomes 2.83 pieces on average, compared with 1.35 for English and 4.18 for Turkish. ê, î, û, ç and ş are separate pieces.
- **Decision:** No change for now. A new tokenizer would force the model to relearn its word mappings, which is risky with our amount of data. A tokenizer trial is planned for December.

**13. Does Kurdish have more sounds than letters?**
Yes. The alphabet has 31 letters, but linguists count more sounds:
- **Aspirated and unaspirated consonants:** p, t, k and ç each have two forms.
- **Two r sounds and two l sounds.**
- **Other sounds:** ḧ, ʿ, ẍ, ŋ and xʷ.

Sources: Samî Tan; Barzo Omar Mahmoud (2016). The ear writes standard spelling. The voice learns these differences by hearing them in recordings. A separate pronunciation layer will be tried later. Details: `pivan/dengen-kurdi.md`.

**14. How are stress and intonation measured?**
- **Intonation set:** 257 sentences. Types include statement/question pairs, wh-questions, gelo and ma questions, commands, calls, emotions, dialogue and more. These sentences never enter training.
- **Intonation judge:** Looks at the pitch curve of each reading and decides whether it sounds like a question.
- **The judge's limits:** It recognises 69% of the questions and 89% of the statements in human readings. That is why the real judge is the human ear.

## Data

**15. What data is used?**

| Source | Licence | Amount | Status |
|---|---|---|---|
| Common Voice 27 (Kurmanji) | CC0 | 44,549 clips, 49.8 h | ✅ in ear training |
| FLEURS (Kurmanji) | CC BY 4.0 | 3,556 clips, 11.7 h | ✅ in ear training |
| Voice of America archive | Public domain (only material VOA produced itself) | ~2,700 recordings, ~1,020 h | ⬜ waiting (language check first) |

Full list: `dane/`.

**16. How do you know a recording is really Kurdish?**
- **Common Voice and FLEURS:** Already Kurdish. In Common Voice, other volunteers listen to and approve each recording.
- **Voice of America:** The archive may contain guests speaking Turkish, Arabic or English, and music. So every segment must pass two checks:
  - **Language ID from the audio:** MMS-LID.
  - **Language ID from the draft text:** GlotLID.
- **Threshold:** Set with recordings known to be Kurdish.
- **Human check:** A native speaker listens to samples of accepted and rejected segments.

Full rules: `dane/qaideyen-ketina-perwerdeye.json`.

**17. How can I know you really used these recordings and did not make them up?**
- **Every recording is named:** Every recording used is named in `dane/`. Common Voice and FLEURS names can be looked up in their own open files.
- **Voice of America:** The list will include each recording's web address and length, so you can open it and compare the length.
- **You can check it yourself:** Code and results are open; you can rerun a job and get the same number.

**18. How much data is needed, and where will it come from?**
- **The voice:** The base model's guide recommends more than 500 hours of clean audio for a new language. Today 61.5 hours are in training.
- **Sources:**
  - Voice of America (~1,020 h, waiting for checks)
  - radio, podcasts and audiobooks we asked permission for (letters sent, waiting for written permission)
  - readings and conversations from volunteers

**19. Are recordings sorted by quality?**
Yes, into four classes. Each segment is measured automatically: noise, telephone sound, music. The recording type (studio, phone, radio, YouTube, café…) is also stored.

| Class | What | Ear | Voice |
|---|---|---|---|
| A | Studio quality | ✅ | ✅ |
| B | Clean recording | ✅ | ✅ |
| C | Telephone or room sound | ✅ | ❌ |
| D | Noisy or with music | ✅ | ❌ |

- **Why the ear takes all of them:** Bad recordings prepare it for real life.
- **Why the voice takes only A and B:** A voice model copies the noise too.

**20. How do you choose "question recordings"?**
- **From the text:** In Common Voice the sentence that was read is stored with the recording. If it ends with "?", it counts as a question.
- **Question type:** If it has a question word (çi, kî, kengî, çawa…), it is a wh-question; otherwise it is a yes/no question. A fixed rule decides this, not a language model.
- **From the audio:** Some readers read questions flat. The intonation judge filters those out.

**21. What about copyright and permission?**
- **Licence:** Only openly licensed or public-domain data is used.
- **Voice of America:** Only material VOA produced itself is public domain. AP, Reuters and AFP material is not, so the video section is left out.
- **Permitted sources:** The permission must be handwritten, dated and signed, and it is confirmed through a second channel.

**22. Do test sentences go into training?**
No. Test sets are locked, and the code refuses any test sentence that tries to enter training. A model that has seen the test sentences gives a false score.

## Results

**23. How good is the ear? What are CER and WER?**
- **CER:** How many letters in 100 are wrong.
- **WER:** How many words in 100 are wrong.

Best ear, 18 October 2026:

| Test | Base model | Our ear |
|---|---|---|
| WER on the same 500 clips | 29.3% | **24.3%** |
| All 999 clips | — | CER 7.1% · WER 24.2% |
| Common Voice | — | WER 13.4% |
| FLEURS | — | WER 27.4% |

The goal is at most 5 errors per 100 letters in conversation. We are not there yet.

**24. How is the voice doing?**
- **Intonation:** In the latest trial (257 sentences), 70% of questions sounded like questions. In human readings the figure is 69%.
- **Intelligibility:** Not good enough yet, about 16 errors per 100 letters.
- **The real fix:** More clean Kurdish audio.

**25. Who reads the test results? Do they show the truth?**
- **Who produces the score:** A calculation, not a person. What the ear wrote is compared letter by letter with the correct text from the source.
- **When it is reliable:** For comparing models with each other, because the test and the measure stay the same.
- **Why it is not absolute truth:**
  - Spelling differences count as errors.
  - The source texts can contain mistakes themselves.
  - The tests are read speech, not conversation.
- **The fix:** Native speakers listen. On a check page they approve test sentences one by one. A listening page is also being built:
  - **The ear:** 50 clips.
  - **The voice:** 30 sentences. Each is also played with a human reading of the same sentence, in shuffled order.

**26. How will "indistinguishable" be measured?**
- **Listeners:** 30–50 listeners from different regions hear human and machine readings of the same text without knowing which is which.
- **Success:** Listeners pick the human at most 55% of the time (a coin flip is 50%).
- **Three tests:** short sentences, long paragraphs and conversation.

## Joining

**27. Do I need to know how to code?**
No. Most tasks only need Kurdish and a phone. Volunteers who code are welcome too.

**28. Do I need a Claude account?**
No. The project runs the AI side; participants listen, read, correct and record.

**29. What tasks are there?**

| Task | What | Time |
|---|---|---|
| Language editor | Corrects what the machine wrote; writes stress and pronunciation rules | 2–3 h a week |
| Listener | Listens and says which sounds natural | 15 min every two weeks |
| Voice owner | Reads sentences in their own voice (one woman, one man) | 4–6 h a week during recording |
| Sources and permissions | Finds Kurdish radio, podcasts and books; asks for permission | 1–2 h a week |
| Dialect speaker | Speaks once for 10–15 min in their dialect | Once |
| Programmer (optional) | Code, measurement, tools | As much as they like |

**30. Who can join, and who cannot?**
- **Who can join:** Anyone who speaks Kurdish. Editors need good Kurdish reading and writing.
- **Limits:**
  - People under 18 can record only with written permission from their family.
  - Anyone who gives their voice signs a written agreement.
  - Other people's recordings cannot be sent without their owner's permission.

**31. How do I join?**
1. Look at the project on GitHub: github.com/marmarok/deng
2. Write through Tirşik or a GitHub Issue. Include:
   - your name or nickname
   - which task
   - the town where you grew up
   - hours per week
3. You do a small trial task: correct 10 sentences, or listen for 15 minutes.
4. If you give your voice, you sign a written agreement.

**32. What happens if I give my voice? What are my rights?**
- **Agreement:** Your voice is taken under a written agreement that says what it will be used for.
- **Storage:** Recordings are processed only in the project lead's private account and never go to another account.
- **Withdrawing:** If you withdraw your permission, your recording stays out of later models.
- **Copying:** When the model is released, copying other people's voices will be switched off.

**33. Will my personal information be published?**
No. Public pages show only the name you allow. Every publication is checked for personal information first.

**34. What is GitHub?**
A website where code, plans and results are kept in the open.
- **To read:** No account is needed.
- **For questions and suggestions:** A free account is enough; that is what "Issues" is for.
- **What is here:**
  - **README:** a summary of the project
  - **DEFTER:** a dated work log
  - **dane:** the list of all data
  - **pivan:** measurement results
  - **awaz:** the intonation sentences
  - **code:** open

**35. Is it paid? What if it earns money?**
Taking part is voluntary and unpaid. Participants are listed by name in "Keda wan heye" and use the model for free. If it ever earns money, participants' share is set in writing in advance.

**36. Who owns the model? What licence?**
- **Code:** Open, under the MIT licence.
- **Model licence:** Not decided yet. The decision will be announced openly.

**37. Are free AI tools used?**
- **Usage limit:** Claude's usage is limited, so some work is moved to other tools.
- **Routine updates:** Done with simple scripts.
- **Kurdish text work:** Google's free Gemini is being considered, for open data only.
- **Local models:** Weak in Kurdish, so they are not used.

## Trust and risks

**38. What if the AI makes things up?**
- **Where numbers come from:** Every number is tied to a result file. If a result is not in a file, it is not claimed.
- **Unknowns:** Unknown things are labelled as estimates.
- **Kurdish examples:** These can be made up by mistake, so a native speaker checks them. For example, "ker/kerr" was once given as the wrong kind of example, and it was corrected.

**39. How are mistakes fixed?**
- **Record:** The mistake is written in DEFTER with a date.
- **Old plans:** They are archived, never deleted.
- **You can report one too:** If you see a mistake, open an Issue.

**40. Could the voice be misused (fake voices)?**
This is a real risk.
- **At release:** Copying other people's voices will be switched off. A hidden watermark in the audio is being considered.
- **In training:** Only recordings with permission are used.

**41. What if the project stops halfway?**
- **Documents:** Every decision and measurement is written down, so nothing starts from scratch if someone leaves.
- **Code:** Open, so anyone can continue.
- **Each stage leaves something usable on its own:** For example, even today's ear is better than the base model.
