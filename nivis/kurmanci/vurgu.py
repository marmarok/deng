"""Stress of a Kurmanji word and sentence, by the rules of Tan (T78-80, T340) and Karabax (K27-28, K321-322).

A hypothesis, not a fact: Bedirxan and MacKenzie both warn that stress is irregular and the material thin (T80). Every
rule below names its source, pivan/vurgu-olcum.md tests them on speech. Rules marked S31a were changed by that test:
speech refuted the book. Where the books differ and speech did not decide (preverb infinitive, free bi-) the code keeps one
choice and says so: the choice can be flipped by a constant.

  word_stress("hatin", kind="inf")   -> final  (T79: to come)
  word_stress("hatin", kind="past")  -> first  (T79: they came)
"""
from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ses import VOWELS, lower, phones, syllable_of, syllables  # noqa: E402
import fiil  # noqa: E402

# Words without stress of their own in the phrase. T79: -ek, -ê, -a do not move stress; the clitics lean on their host.
PREPOSITIONS = {"bi", "di", "ji", "li", "bo", "ba", "bê", "gel", "heta", "wek", "wekî", "weke", "mîna", "bin", "ber", "ser", "nav", "dû", "pey"}
POSTPOSITIONS = {"de", "re", "ve", "da", "ra"}
LINKERS = {"ê", "a", "ên", "yê", "ya", "yên", "î", "e", "ye", "ne", "in", "im", "me", "yî", "û", "jî", "ku", "ka", "ma", "dê", "an", "yan", "lê", "ta", "hem"}
WEAK_PRONOUNS = {"ez", "tu", "ew", "ev", "em", "hûn", "min", "te", "wî", "wê", "me", "we", "wan", "vî", "vê", "van", "xwe", "hev", "pê", "jê", "lê", "tê"}
CLITICS = PREPOSITIONS | POSTPOSITIONS | LINKERS | WEAK_PRONOUNS

# Words that end in a vowel of their own, not a case ending. Stem-final stress already falls on that vowel.
OWN_FINAL_VOWEL = set("""bira çira çiya dîsa wiha wisa niha hêja ava bila heta hema gava dema zana hêdî êdî
xwedê heftê heştê dê rê pê sê kê çê jê lê tê hê nêzê pirê stêrê divê riha
amerîka ewropa almanya rûsya tirkiye sûriye iraq îran afrîka asya conega
""".split())

# -ek that builds a word instead of marking one (T69, T99): the ending is part of the stem, so the default final stress holds.
OWN_EK = set("berek çilek dizek kulek birek tirek fisek silek piştek serek xurek badek pêçek jîrek zîrek gelek hinek".split())

OWN_FROM_CORPUS = set()


def _own_vowel_words():
    """Words whose last a or ê belongs to the word: the bare stem is never seen in text (veri/kendi-unlu.txt)."""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "veri", "kendi-unlu.txt")
    return set(open(p, encoding="utf8").read().split()) if os.path.exists(p) else {""}


# First-syllable words (K27).
INITIAL = {"îro", "nîvro", "êvar", "îsal", "îşev", "heke", "hêdî"}

PLURAL_STRESSED = ("ên", "an")     # T79, K28
TRANSPARENT = ("ekî", "ekê", "ek", "ê", "a")  # T79, K28: stress stays on the stem. S31a: -ekî too, against K28, in all three sources
FINAL_STRESSED = ("eke", "inan", "ine")

# Where the books part (K28 marks stem stress in `bibînin`, T80 gives bi- the stress): T's rule for a free-standing
# form, K's after a word that governs the subjunctive. S31a left this open: the sources disagree.
SUBJ_GOVERNORS = {"ku", "divê", "bila", "dikare", "dikarim", "dikarin", "dikarî", "nikare", "nikarim", "nikarin", "nikarî", "ê", "dê", "yê", "wê", "xwezî", "heke", "ger", "eger"}
PREVERB_INFINITIVE_STRESS = "preverb"  # K28 (vegotin) against T79's plain final rule, which lists no preverb verb. S31a: too few words to decide
SYLLABIC_ENDINGS = ("in", "im")  # S31a: dikarin leads on the ending, dikare on the stem


@dataclass
class Word:
    text: str
    syllables: list
    stress: tuple  # indices of stressed syllables; empty for clitics
    rule: str
    kind: str = ""

    @property
    def marked(self) -> str:
        """The word with ˈ before each stressed syllable."""
        return "".join(("ˈ" if i in self.stress else "") + s for i, s in enumerate(self.syllables))

    @property
    def ipa(self) -> str:
        return phones(self.text, self.stress)


def _at(word: str, offset: int) -> int:
    return syllable_of(word, offset)


def _last_vowel(word: str, start: int, end: int) -> int:
    for i in range(end - 1, start - 1, -1):
        if word[i] in VOWELS:
            return i
    return start


def verb_stress(p: fiil.Parse, after: str = "") -> tuple[tuple, str]:
    """Stress of a parsed verb form. Priority: negation, preverb, mood prefix, stem (T79-80)."""
    w = p.word
    if p.kind == "inf":
        if p.preverb and PREVERB_INFINITIVE_STRESS == "preverb":
            return (_at(w, 0),), "K28 preverb"
        return (len(syllables(w)) - 1,), "T79 infinitive final"
    at_mood = len(p.preverb)
    if p.mood in ("na", "ni", "ne", "me", "nedi"):
        return (_at(w, at_mood),), "T79 negation"
    if p.preverb:
        return (_at(w, 0),), "T80 preverb"
    if p.mood == "di":  # S31a: T80 gives di- the stress, but it is the weakest syllable in all three sources
        stem_vowel = any(c in VOWELS for c in p.stem)
        if p.ending in SYLLABIC_ENDINGS or not stem_vowel:
            return (len(syllables(w)) - 1,), "S31a di- final"
        return (_at(w, _last_vowel(w, p.stem_at, p.stem_at + len(p.stem))),), "S31a di- stem"
    if p.mood == "bi":
        if p.kind == "past":  # T80 table: bihátama, bigeriyáma
            return (_at(w, _last_vowel(w, p.stem_at, p.stem_at + len(p.stem))),), "T80 past wish, stem"
        if after in SUBJ_GOVERNORS:
            return (_at(w, _last_vowel(w, p.stem_at, p.stem_at + len(p.stem))),), "K28 governed subjunctive, stem"
        return (_at(w, 0),), "T80 bi-"
    return (_at(w, _last_vowel(w, p.stem_at, p.stem_at + len(p.stem))),), "T80 stem"


def noun_stress(w: str, known=None) -> tuple[tuple, str]:
    if not OWN_FROM_CORPUS:
        OWN_FROM_CORPUS.update(_own_vowel_words())
    if w in OWN_FROM_CORPUS:
        return (len(syllables(w)) - 1,), "default"
    syl = syllables(w)
    last = len(syl) - 1
    if w in INITIAL:
        return (0,), "K27 initial"
    if w in OWN_FINAL_VOWEL or w in OWN_EK or len(syl) == 1:
        return (last,), "default"
    for suf in FINAL_STRESSED:
        if w.endswith(suf) and len(w) > len(suf) + 2 and (known is None or w[: -len(suf)] in known):
            return (last,), "K28 -ekî"
    for suf in PLURAL_STRESSED:
        if w.endswith(suf) and len(w) > len(suf) + 1 and (known is None or w[: -len(suf)] in known):
            return (last,), "T79 plural"
    if w.endswith(("iya", "iyê", "iyan", "iyên")) and len(syl) > 2:  # partî -> partiya: the y-glide hides the stem's î (K26)
        tail = 2 if w.endswith(("iyan", "iyên")) else 1
        return (last - tail + (1 if tail == 2 else 0),), "K26 î stem"
    for suf in TRANSPARENT:  # most unknown words are nouns with a case ending, so a word in neither list is stripped
        if w.endswith(suf) and len(w) > len(suf) + 1:
            stem = w[: -len(suf)]
            stem = stem[:-1] if stem.endswith("y") else stem
            return (_at(w, _last_vowel(w, 0, len(stem))),), "T79 transparent ending"
    return (last,), "T78 final"


def participle(p: fiil.Parse, w: str) -> tuple[tuple, str]:
    """T80: two syllables final, longer forms on the stem (kuştî but kelándî)."""
    if len(syllables(w)) == 2:
        return (1,), "T80 participle"
    return (_at(w, _last_vowel(w, p.stem_at, p.stem_at + len(p.stem))),), "T80 participle"


LEX = None


def lexicon(words=None) -> fiil.Lexicon:
    global LEX
    if LEX is None or words is not None:
        LEX = fiil.Lexicon(words if words is not None else fiil.corpus_words())
    return LEX


def word_stress(text: str, kind: str = "", after: str = "", before: str = "", known=None) -> Word:
    """Stress of one word. kind forces a reading: 'inf', 'past', 'noun', 'participle'; else the word is parsed."""
    w = lower(text)
    syl = syllables(w)
    if not syl:
        return Word(text, [text], (), "empty")
    if not kind and w in CLITICS:
        return Word(text, syl, (), "clitic", "clitic")
    p = None if kind == "noun" else fiil.parse(w, lexicon())
    if kind == "noun" or p is None:
        s, r = noun_stress(w, known)
        return Word(text, syl, s, r, "noun")
    if kind == "participle":
        s, r = participle(p, w)
        return Word(text, syl, s, r, kind)
    if p.kind == "past" and p.regular and p.ending == "in" and not p.mood and not p.preverb:  # şewitandin: not in the table, read as the table's verbs are
        p = fiil.Parse(w, p.verb, "inf", "", "", w, "")
    if kind == "inf" or (p.kind == "inf" and not kind and not reads_finite(w, after, before)):
        q = fiil.Parse(w, p.verb, "inf", p.preverb, "", p.stem, "")
        s, r = verb_stress(q)
        return Word(text, syl, s, r, "inf")
    if p.kind == "inf":  # a bare -in form read as third person plural past
        q = fiil.Parse(w, p.verb, "past", p.preverb, "", p.verb.past, "in")
        s, r = verb_stress(q)
        return Word(text, syl, s, r, "past")
    s, r = verb_stress(p, after)
    return Word(text, syl, s, r, p.kind)


PASSIVE_AUX = re.compile(r"^(ne|na|di|nedi|bi)?(hat|hati|hatin|hatibû|hatibûn|hatiye|hatine|tê|tên|bê|bên|nayê|nayên|neyê|neyên|dihat|dihatin|were|werin"
                         r"|da|dan|daye|dane|dide|didin|bide|bidin|nade|nadin|neda|nedan|dida|didan|dabû|dabûn|dest)$")


def reads_finite(word: str, after: str, before: str) -> bool:
    """Is a bare -in form a past third person plural, not the infinitive?

    The infinitive stands bare mostly after the auxiliaries of the passive and causative (K237-242, T292-294): hat kirin,
    dide çêkirin; after a preposition it is a noun; with an ending it is not bare at all. Elsewhere, at the close of a
    clause, the -in form is the verb (T79).
    """
    if not word.endswith(("in", "ûn", "an", "în")):
        return False
    if PASSIVE_AUX.match(after or ""):
        return False
    if after in PREPOSITIONS:
        return False
    return before in ("", ".", ",", ";", ":", "?", "!", "û")


WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)?", re.UNICODE)


def sentence(text: str, known=None) -> list[Word]:
    """Stress for each word of a sentence. Neighbours decide what one word alone cannot."""
    spans = [(m.group(0), m.start(), m.end()) for m in WORD.finditer(text)]
    out = []
    for i, (w, a, b) in enumerate(spans):
        prev = lower(spans[i - 1][0]) if i else ""
        gap = text[b: spans[i + 1][1]] if i + 1 < len(spans) else "."
        nxt = lower(spans[i + 1][0]) if i + 1 < len(spans) else ""
        before = gap.strip()[:1] if gap.strip() else nxt
        out.append(word_stress(w, after=prev, before=before if gap.strip() else nxt, known=known))
    return out


def mark(text: str, known=None, sign: str = "ˈ") -> str:
    """Copy of the text with the sign before each stressed vowel. One stress per word; clitics stay bare."""
    res, last = [], 0
    words = sentence(text, known)
    for m, wd in zip(WORD.finditer(text), words):
        res.append(text[last: m.start()])
        res.append(_insert(m.group(0), wd, sign))
        last = m.end()
    res.append(text[last:])
    return "".join(res)


def _insert(raw: str, wd: Word, sign: str) -> str:
    if not wd.stress:
        return raw
    i = wd.stress[0]
    off = sum(len(s) for s in wd.syllables[:i])
    syl = wd.syllables[i]
    v = next((k for k, c in enumerate(syl) if c in VOWELS), 0)
    at = off + v
    return raw[:at] + sign + raw[at:]
