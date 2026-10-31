"""Tests of the Kurmanji language layer. Run: python3 nivis/kurmanci/test_kurmanci.py"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fiil  # noqa: E402
import ses  # noqa: E402
import vurgu  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def gold():
    path = os.path.join(HERE, "veri", "vurgu_altin.tsv")  # the books' own examples: kept out of the public repository
    if not os.path.exists(path):
        return
    with open(path, encoding="utf8") as f:
        yield from csv.DictReader((l for l in f if not l.startswith("#")), delimiter="\t")


def stressed_syllable(marked):
    w = marked.replace("'", "")
    return w, ses.syllable_of(w, marked.index("'"))


KIND = {"part": "participle", "noun": "noun", "inf": "inf", "past": "past"}


def test_gold():
    ok, bad = 0, []
    for r in gold():
        w, want = stressed_syllable(r["word"])
        got = vurgu.word_stress(w, kind=KIND.get(r["kind"], ""))
        if got.stress and got.stress[0] == want:
            ok += 1
        else:
            bad.append((r["word"], r["source"], got.marked, got.rule))
    total = ok + len(bad)
    if not total:
        print("gold stress: list not in this repository, skipped")
        return
    print(f"gold stress: {ok}/{total}")
    for b in bad:
        print("  miss", b)
    assert ok / total >= 0.95, (ok, total)


SYL = {  # K27, T53
    "ajalnas": "a-jal-nas", "berdewam": "ber-de-wam", "derhêner": "der-hê-ner", "aborînas": "a-bo-rî-nas",
    "bernamzedî": "ber-nam-ze-dî", "ceribandin": "ce-ri-ban-din", "pirzimanîtî": "pir-zi-ma-nî-tî",
    "welatparêzî": "we-lat-pa-rê-zî", "ronayîparêzî": "ro-na-yî-pa-rê-zî", "zerzewatfiroşî": "zer-ze-wat-fi-ro-şî",
    "rabûn": "ra-bûn", "şakirin": "şa-ki-rin", "derxistin": "der-xis-tin", "hilgerandin": "hil-ge-ran-din",
    "gulan": "gu-lan", "heval": "he-val", "hevkar": "hev-kar", "hogir": "ho-gir", "bêje": "bê-je", "tevger": "tev-ger",
    "cengawer": "cen-ga-wer", "dilbirîn": "dil-bi-rîn", "qemirandin": "qe-mi-ran-din", "hilbijartin": "hil-bi-jar-tin",
    "dixwazim": "di-xwa-zim", "xwendin": "xwen-din", "stran": "stran", "bang": "bang", "stêrk": "stêrk",
}


def test_syllables():
    bad = [(w, want, "-".join(ses.syllables(w))) for w, want in SYL.items() if "-".join(ses.syllables(w)) != want]
    print(f"syllables: {len(SYL) - len(bad)}/{len(SYL)}", bad)
    assert not bad


def test_spoken():
    # T44-46, T43, T344
    pairs = {"serokkomar": "serokomar", "dewlemendtir": "dewlementir", "bilindtir": "bilintir", "destmal": "desmal",
             "yekkîte": "yekîte", "biaxive": "baxive", "diavêje": "davêje", "naaxive": "naxive", "naajo": "najo"}
    bad = [(a, b, ses.spoken(a)) for a, b in pairs.items() if ses.spoken(a) != b]
    print(f"spoken forms: {len(pairs) - len(bad)}/{len(pairs)}", bad)
    assert not bad


def test_lower():
    assert ses.lower("KIRIN İRAQ Î") == "kirin iraq î"


def test_verbs():
    lex = vurgu.lexicon()
    want = {"dixwazim": ("xwaz", "present"), "naçim": ("ç", "present"), "biçe": ("ç", "subj"), "vedixwim": ("xw", "present"),
            "dikin": ("k", "present"), "hatiye": ("hat", "past"), "ketibû": ("ket", "past"), "nekiribû": ("kir", "past"),
            "dibêje": ("bêj", "present"), "venexwarin": ("xwar", "past"), "tê": ("t", "present"), "nayê": ("y", "present")}
    bad = []
    for w, (stem, kind) in want.items():
        p = fiil.parse(w, lex)
        if not p or p.stem != stem or p.kind != kind:
            bad.append((w, p and (p.stem, p.kind)))
    print(f"verbs: {len(want) - len(bad)}/{len(want)}", bad)
    assert not bad


def test_homographs():
    """The same spelling with stress in two places (T79, T80). This is what plain text cannot show the voice."""
    assert vurgu.word_stress("hatin", kind="inf").marked == "ha" + "ˈtin"
    assert vurgu.word_stress("hatin", kind="past").marked == "ˈha" + "tin"
    assert vurgu.mark("Ew duh hatin.").endswith("hˈatin.")
    assert vurgu.mark("Ev mal hat kirin.").endswith("kirˈin.")
    print("homographs ok:", vurgu.mark("Ew duh hatin."), "/", vurgu.mark("Ev mal hat kirin."))


def test_sentence_mark():
    for s in ["Zozan duh berî bavê xwe ji malê derket.", "Ez dixwazim pirtûkekê bixwînim.", "Keçikê av venexwar."]:
        print(" ", vurgu.mark(s))


if __name__ == "__main__":
    test_syllables()
    test_spoken()
    test_lower()
    test_verbs()
    test_homographs()
    test_sentence_mark()
    test_gold()
    print("all passed")
