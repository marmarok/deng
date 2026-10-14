# Kulağın taslağı: uzun bir sesi parçalara böler, CTC kulağıyla yazar, her kelimeye zaman ve güven verir.
# Çıktı düzeltme sayfasının (rastkirin/index.html) okuduğu biçimdedir:
#   {"parcalar": [{"bas", "son", "kelimeler": [{"w", "bas", "son", "guven"}]}]}
# Omnilingual ortamında (Python 3.12) çalışır. Kullanım:
#   python taslak.py <ctc_kart> <ctc_agirlik.pt|-> <cikti_klasoru> ses1 ses2 ...
#   DENG_LLM=omniASR_LLM_1B_v2 ile: yazıyı dil bilgili kulak (LLM) yazar, kelime zamanlarını CTC kulağı hizalar
#   (14.10 temel kulak kararı). Güven = CTC'nin o kelimeyi duyduğu olasılık; LLM'in yazdığı kelime ile CTC'nin
#   duyduğu farklıysa kelime "fark" diye işaretlenir (uydurma ya da standartlaştırma adayı).
import sys, os, json, math
import numpy as np, torch, soundfile as sf

ORAN = 16000
ADIM = 320          # wav2vec2 kare adımı: 20 ms
EN_UZUN = 30.0      # parça üst sınırı (model 40 sn'ye kadar alır)

def ses_oku(yol):
    try:
        d, o = sf.read(yol, dtype="float32")
    except Exception:
        import subprocess
        ham = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", yol, "-ac", "1", "-ar", str(ORAN), "-f", "f32le", "-"],
                             capture_output=True, check=True).stdout
        return np.frombuffer(ham, dtype=np.float32).copy()
    if d.ndim > 1: d = d.mean(1)
    if o != ORAN:
        import torchaudio.functional as F
        d = F.resample(torch.from_numpy(d), o, ORAN).numpy()
    return d

_vad = None
def konusma_parcalari(d):
    """Silero VAD ile konuşma bölgeleri; uzun bölgeler en sessiz yerden bölünür, kısa boşluklar birleşir."""
    global _vad
    if _vad is None:
        from silero_vad import load_silero_vad, get_speech_timestamps
        _vad = (load_silero_vad(), get_speech_timestamps)
    model, zaman = _vad
    bolgeler = zaman(torch.from_numpy(d), model, sampling_rate=ORAN, min_silence_duration_ms=300, speech_pad_ms=150)
    parcalar = []
    for b in bolgeler:
        s, e = b["start"], b["end"]
        if parcalar and s - parcalar[-1][1] < 0.3 * ORAN and e - parcalar[-1][0] < EN_UZUN * ORAN:
            parcalar[-1][1] = e
        else:
            parcalar.append([s, e])
    sonuc = []
    for s, e in parcalar:
        while e - s > EN_UZUN * ORAN:
            # son 10 saniyede en düşük enerjili 100 ms'den böl
            ara = d[s + int((EN_UZUN - 10) * ORAN): s + int(EN_UZUN * ORAN)]
            k = ADIM * 5
            enerji = [float(np.mean(ara[i:i + k] ** 2)) for i in range(0, len(ara) - k, k)]
            kes = s + int((EN_UZUN - 10) * ORAN) + k * int(np.argmin(enerji)) + k // 2
            sonuc.append((s, kes)); s = kes
        sonuc.append((s, e))
    return sonuc

class Kulak:
    def __init__(self, kart, agirlik="-", device="cuda"):
        from omnilingual_asr.models.inference.pipeline import ASRInferencePipeline
        self.p = ASRInferencePipeline(model_card=kart, device=device, dtype=torch.float16)
        if agirlik != "-":
            sd = torch.load(agirlik, map_location="cpu", weights_only=False)
            while isinstance(sd, dict) and "model" in sd and isinstance(sd["model"], dict): sd = sd["model"]
            eksik, _ = self.p.model.load_state_dict({k.removeprefix("module."): v for k, v in sd.items()}, strict=False)
            assert not eksik, eksik[:5]
            self.p.model.half()
        self.p.model.eval()
        self.dev = device
        self._parca = {}
        enc = self.p.token_encoder
        a = enc("a").tolist()
        self._on = a[-1] if a else None
        ab = enc("a b").tolist()
        self.bosluk = [i for i in ab if i not in a and i not in enc("b").tolist()]

    def parca(self, i):
        """Bir belirtecin yazısı (ön ekle çözülüp farkı alınarak: boşluklar kaybolmasın)."""
        if i not in self._parca:
            dec = self.p.token_decoder
            onlu = dec(torch.tensor([self._on, i])) if self._on is not None else dec(torch.tensor([i]))
            self._parca[i] = onlu[len(dec(torch.tensor([self._on]))):] if self._on is not None else onlu
        return self._parca[i]

    @torch.no_grad()
    def olasiliklar(self, dalga):
        from fairseq2.nn.batch_layout import BatchLayout
        x = torch.from_numpy(dalga).float()
        x = (x - x.mean()) / (x.std() + 1e-5)
        x = x.unsqueeze(0).to(self.dev, torch.float16)
        lay = BatchLayout(x.shape, seq_lens=[x.shape[1]], device=x.device)
        logits, bl = self.p.model(x, lay)
        return torch.log_softmax(logits[0, : bl.seq_lens[0]].float(), -1).cpu()

    def yaz(self, dalga, kaydir=0.0):
        """Açgözlü CTC çözümü; kelime zamanları karelerden, güven harf karelerinin olasılık ortalamasından."""
        lp = self.olasiliklar(dalga)
        enb, ids = lp.max(-1)
        bos = 0  # CTC boş belirteci omniASR'de 0 (pad ile aynı); aşağıda doğrulanır
        kelimeler, harfler, onceki = [], [], -1
        def kapat():
            if harfler:
                w = "".join(h[0] for h in harfler).strip()
                if w:
                    g = float(np.exp(np.mean([h[3] for h in harfler])))
                    kelimeler.append({"w": w, "bas": round(kaydir + harfler[0][1], 2),
                                      "son": round(kaydir + harfler[-1][2], 2), "guven": round(g, 3)})
            harfler.clear()
        for t, (i, l) in enumerate(zip(ids.tolist(), enb.tolist())):
            if i == onceki and harfler and i != bos:
                harfler[-1][2] = (t + 1) * ADIM / ORAN; harfler[-1][3] = min(harfler[-1][3], l)
                continue
            onceki = i
            if i == bos: continue
            if i in self.bosluk:
                kapat(); continue
            harfler.append([self.parca(i), t * ADIM / ORAN, (t + 1) * ADIM / ORAN, l])
        kapat()
        return kelimeler

    def llm_yukle(self, kart, lang="kmr_Latn"):
        from omnilingual_asr.models.inference.pipeline import ASRInferencePipeline
        self.llm = ASRInferencePipeline(model_card=kart, device=self.dev, dtype=torch.float16)
        self.lang = lang
        enc = self.p.token_encoder
        self._ek = set(enc("").tolist())  # boş metinde de çıkan özel belirteçler (başlangıç/bitiş)
        self._unk = self.p.tokenizer.vocab_info.unk_idx

    def llm_yaz(self, parcalar):
        """Parçaları (dalga dizileri) LLM ile yazar; geçici wav dosyası üstünden (pipeline dosya yolu alır)."""
        import tempfile
        yollar = []
        with tempfile.TemporaryDirectory() as g:
            for i, d in enumerate(parcalar):
                y = f"{g}/{i}.wav"; sf.write(y, d, ORAN); yollar.append(y)
            return self.llm.transcribe(yollar, lang=[self.lang] * len(yollar), batch_size=4)

    def hizala(self, dalga, metin, kaydir=0.0):
        """LLM'in yazdığı metni CTC olasılıklarına zorla hizalar (torchaudio forced_align); kelime zamanı ve güveni verir."""
        import torchaudio.functional as AF, difflib
        lp = self.olasiliklar(dalga)
        ids = [i for i in self.p.token_encoder(metin).tolist() if i not in self._ek and i != self._unk]
        if not ids or len(ids) > lp.shape[0]:
            return None
        hiza, puan = AF.forced_align(lp.unsqueeze(0), torch.tensor([ids], dtype=torch.int32), blank=0)
        araliklar = AF.merge_tokens(hiza[0], puan[0].exp())
        kelimeler, harf = [], []
        def kapat():
            if harf:
                w = "".join(self.parca(a.token) for a in harf).strip()
                if w:
                    g = float(np.mean([a.score for a in harf]))
                    kelimeler.append({"w": w, "bas": round(kaydir + harf[0].start * ADIM / ORAN, 2),
                                      "son": round(kaydir + harf[-1].end * ADIM / ORAN, 2), "guven": round(g, 3)})
            harf.clear()
        for a in araliklar:
            if a.token in self.bosluk: kapat()
            else: harf.append(a)
        kapat()
        # CTC'nin kendi duyduğu kelimelerle karşılaştır: eşleşmeyen LLM kelimeleri "fark"
        ctc = [k["w"].lower() for k in self.yaz(dalga, kaydir)]
        llm = [k["w"].lower().strip(".,?!:;\"'") for k in kelimeler]
        es = difflib.SequenceMatcher(a=llm, b=ctc, autojunk=False)
        eslesen = set()
        for blok in es.get_matching_blocks():
            eslesen.update(range(blok.a, blok.a + blok.size))
        for i, k in enumerate(kelimeler):
            if i not in eslesen: k["fark"] = True
        return kelimeler

    def taslak(self, yol):
        d = ses_oku(yol)
        parcalar = []
        bolgeler = konusma_parcalari(d)
        metinler = self.llm_yaz([d[s:e] for s, e in bolgeler]) if getattr(self, "llm", None) else [None] * len(bolgeler)
        for (s, e), m in zip(bolgeler, metinler):
            k = self.hizala(d[s:e], m, s / ORAN) if m else None
            if k is None: k = self.yaz(d[s:e], s / ORAN)  # LLM yoksa ya da hizalama olmadıysa: CTC'nin kendi yazısı
            if k: parcalar.append({"bas": round(s / ORAN, 2), "son": round(e / ORAN, 2), "kelimeler": k})
        return {"ses": os.path.basename(yol), "sure": round(len(d) / ORAN, 2), "parcalar": parcalar}

if __name__ == "__main__":
    kart, agirlik, cikti = sys.argv[1:4]
    os.makedirs(cikti, exist_ok=True)
    k = Kulak(kart, agirlik)
    if os.environ.get("DENG_LLM"): k.llm_yukle(os.environ["DENG_LLM"])
    print("boşluk belirteci:", k.bosluk, "boş:", k.p.tokenizer.vocab_info.pad_idx, flush=True)
    for yol in sys.argv[4:]:
        t = k.taslak(yol)
        ad = os.path.splitext(os.path.basename(yol))[0]
        json.dump(t, open(f"{cikti}/{ad}.json", "w"), ensure_ascii=False)
        n = sum(len(p["kelimeler"]) for p in t["parcalar"])
        dusuk = sum(w["guven"] < 0.5 for p in t["parcalar"] for w in p["kelimeler"])
        fark = sum(bool(w.get("fark")) for p in t["parcalar"] for w in p["kelimeler"])
        print(ad, "süre", t["sure"], "kelime", n, "düşük güven", dusuk, "LLM-CTC farkı", fark, flush=True)
