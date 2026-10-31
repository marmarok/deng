"""Kurmanji verbs: two stems, prefixes and endings (K143-286, T203-300).

parse(word) finds a finite form or an infinitive. Stems come from veri/fiil.tsv (T203-245, K284) and from the regular
classes -andin, -în and -an, confirmed against the corpus word list when one is given.
"""
from __future__ import annotations

import csv
import gzip
import os
from dataclasses import dataclass

from ses import VOWELS

HERE = os.path.dirname(os.path.abspath(__file__))
PREVERBS = ("hil", "wer", "der", "ver", "ra", "da", "ve", "rû", "ro", "çê", "pê", "lê", "jê", "tê", "ser")
MOODS = ("nedi", "di", "na", "ni", "ne", "bi", "me")  # T58-60: nedi = ne + di, past progressive

# Endings after a consonant and after a vowel (K158-192, T258-276).
PRES_C = ("im", "î", "e", "in", "ime", "iye", "ine")
PRES_V = ("m", "yî", "î", "e", "n", "", "me", "ne", "ye")
PAST_C = ("", "im", "î", "in", "e", "ime", "iye", "ine", "ibûm", "ibûyî", "ibû", "ibûn", "ibûme", "ibûye", "ibûne", "ibim",
          "ibî", "ibe", "ibin", "ibûma", "ibûya", "ibûna", "ibûyayî", "a", "ama", "ayî", "ana", "iya", "iyana", "iyame")
PAST_V = ("", "m", "yî", "n", "me", "ye", "ne", "bûm", "bûyî", "bû", "bûn", "bûme", "bûye", "bûne", "bim", "bî", "be", "bin",
          "bûma", "bûya", "bûna", "bûyayî", "ma", "yayî", "ya", "na")


IRREALIS = ("a", "ama", "ayî", "ana", "iya", "iyana", "ma", "yayî", "ya", "na")


@dataclass
class Verb:
    inf: str
    past: str
    pres: str
    transitive: bool | None = None


@dataclass
class Parse:
    word: str
    verb: Verb
    kind: str  # "inf", "present", "past", "subj", "imp", "participle"
    preverb: str
    mood: str
    stem: str
    ending: str
    regular: bool = False  # found by class rule, not in the table

    @property
    def stem_at(self) -> int:
        return len(self.preverb) + len(self.mood)


def corpus_words(min_count: int = 2) -> set[str]:
    """Word forms seen in our text pool (sapka-sozluk.tsv.gz). Regular stems must be attested to count."""
    path = os.path.join(os.path.dirname(HERE), "sapka-sozluk.tsv")  # Kaggle unpacks the .gz of a dataset
    out = set()
    for p, opener in ((path + ".gz", gzip.open), (path, open)):
        if os.path.exists(p):
            with opener(p, "rt", encoding="utf8") as f:
                for line in f:
                    a = line.rstrip("\n").split("\t")
                    if a[0] == "k" and len(a) >= 4 and int(a[3]) >= min_count:
                        out.add(a[1])
            break
    return out


def load_table() -> list[Verb]:
    out = []
    with open(os.path.join(HERE, "veri", "fiil.tsv"), encoding="utf8") as f:
        for r in csv.DictReader((l for l in f if not l.startswith("#")), delimiter="\t"):
            out.append(Verb(r["rader"], r["bori"], r["niha"], {"T": True, "I": False}.get(r["ger"])))
    return out


class Lexicon:
    def __init__(self, words=None):
        self.past: dict[str, list[Verb]] = {}
        self.pres: dict[str, list[Verb]] = {}
        self.inf: dict[str, Verb] = {}
        self.words = words  # optional set of attested forms, used to confirm regular stems
        for v in load_table():
            self.add(v)

    def add(self, v: Verb):
        self.inf[v.inf] = v
        self.past.setdefault(v.past, []).append(v)
        if v.pres:
            self.pres.setdefault(v.pres, []).append(v)

    def regular(self, stem: str, present: bool):
        """Regular class verbs for a stem the table does not hold (K276, K285, T240-244)."""
        if len(stem) < 3 or self.words is None or stem.startswith(("di", "bi", "na", "ne")):
            return None  # a stem that opens like a mood prefix is the prefix plus a shorter stem
        if present:
            if stem.endswith("în") and len(stem) > 4:
                root = stem[:-2]
                if root + "andin" in self.words or root + "and" in self.words:
                    return Verb(root + "andin", root + "and", stem, True)
            if stem + "în" in self.words or stem + "iya" in self.words:
                return Verb(stem + "în", stem + "î", stem, None)
            if stem + "an" in self.words and stem + "a" in self.words:
                return Verb(stem + "an", stem + "a", stem, None)
            return None
        if stem.endswith("and") and stem + "in" in self.words:
            root = stem[:-3]
            return Verb(stem + "in", stem, root + "în", True)
        if stem.endswith(("iya", "î")) and not stem.endswith("andî"):  # kurdî, sûriya: a noun passes the -în test, only a present form proves a verb
            root = stem[:-3] if stem.endswith("iya") else stem[:-1]
            if root and any(f"{m}{root}{e}" in self.words for m in ("di", "na") for e in ("e", "in", "im")):
                return Verb(root + "în", stem, root, None)
        return None


def _endings(stem: str, table_c, table_v):
    return table_v if stem[-1:] in VOWELS else table_c


SPECIAL = {  # hatin and anîn lose the h of hê and hîn: tê, bê, nayê, tîne, bîne, nayîne (K155, T44, T226)
    "tê": ("present", "", "t", "ê"), "têm": ("present", "", "t", "êm"), "têyî": ("present", "", "t", "êyî"), "tên": ("present", "", "t", "ên"),
    "bê": ("subj", "", "b", "ê"), "bêm": ("subj", "", "b", "êm"), "bêyî": ("subj", "", "b", "êyî"), "bên": ("subj", "", "b", "ên"),
    "nayê": ("present", "na", "y", "ê"), "nayêm": ("present", "na", "y", "êm"), "nayî": ("present", "na", "y", "î"), "nayên": ("present", "na", "y", "ên"),
    "neyê": ("subj", "ne", "y", "ê"), "neyên": ("subj", "ne", "y", "ên"), "neyêm": ("subj", "ne", "y", "êm"),
    "werim": ("subj", "", "wer", "im"), "werî": ("subj", "", "wer", "î"), "were": ("subj", "", "wer", "e"), "werin": ("subj", "", "wer", "in"),
    "tînim": ("present", "", "tîn", "im"), "tînî": ("present", "", "tîn", "î"), "tîne": ("present", "", "tîn", "e"), "tînin": ("present", "", "tîn", "in"),
    "bînim": ("subj", "", "bîn", "im"), "bînî": ("subj", "", "bîn", "î"), "bîne": ("subj", "", "bîn", "e"), "bînin": ("subj", "", "bîn", "in"),
    "nayînim": ("present", "na", "yîn", "im"), "nayîne": ("present", "na", "yîn", "e"), "nayînin": ("present", "na", "yîn", "in"),
}
_HATIN = Verb("hatin", "hat", "ê", False)
_ANIN = Verb("anîn", "anî", "în", True)


def parse(word: str, lex: Lexicon) -> Parse | None:
    if word in lex.inf:
        return Parse(word, lex.inf[word], "inf", "", "", word, "")
    if word in SPECIAL:
        kind, mood, stem, end = SPECIAL[word]
        return Parse(word, _HATIN if stem in ("t", "b", "y") else _ANIN, kind, "", mood, stem, end)
    best = None
    for pv in ("",) + PREVERBS:
        if pv and not word.startswith(pv):
            continue
        rest = word[len(pv):]
        if pv and rest in lex.inf:  # vegotin, rakirin, derketin
            return Parse(word, lex.inf[rest], "inf", pv, "", rest, "")
        for md in ("",) + MOODS:
            if md and not rest.startswith(md):
                continue
            body = rest[len(md):]
            for cut in range(len(body), 0, -1):
                stem, end = body[:cut], body[cut:]
                c = _try_present(word, pv, md, stem, end, lex) or _try_past(word, pv, md, stem, end, lex)
                if c and (best is None or _rank(c) > _rank(best)):
                    best = c
    return best


def _rank(p: Parse):
    return (not p.regular, bool(p.mood), bool(p.preverb), len(p.stem))


def _try_present(word, pv, md, stem, end, lex):
    if md not in ("di", "na", "ni", "bi", "ne", "me") and not pv:
        return None
    vs = lex.pres.get(stem)
    regular = vs is None
    if vs is None and pv and not md:  # vexwim is in the table; derbasî, serokî must not pass as prefix + stem
        return None
    if vs is None:
        v = lex.regular(stem, True)
        vs = [v] if v else None
    if not vs or end not in _endings(stem, PRES_C, PRES_V):
        return None
    if md == "ni" and stem not in ("kar", "kan", "zan"):  # T266: only zanîn and karîn take ni-
        return None
    kind = "present" if md in ("di", "na", "ni") else "subj"
    return Parse(word, vs[0], kind, pv, md, stem, end, regular)


def _try_past(word, pv, md, stem, end, lex):
    vs = lex.past.get(stem)
    regular = vs is None
    if vs is None:
        v = lex.regular(stem, False)
        vs = [v] if v else None
    if not vs or end not in _endings(stem, PAST_C, PAST_V):
        return None
    if md in ("di", "nedi", "bi", "ne", "") or pv:
        if not md and not pv and end == "" and len(stem) < 2:
            return None
        if not md and not pv and end in IRREALIS:  # rêjîma, jiyana: the wish forms always carry bi- or ne- (K190, T268)
            return None
        return Parse(word, vs[0], "past", pv, md, stem, end, regular)
    return None
