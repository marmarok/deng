"""Kurmanji sound system: letters, syllables and phones.

Rules and page numbers come from two grammars of Kurmanji (K = Karabax, T = Tan).
The alphabet has 31 letters plus the compound sound xw (K22, T35). Spelling hides four things the sound keeps
apart: aspirated and plain c, k, p, t, tap and trill r (T38-40). Those need a lexicon, see ceput.py; nothing here guesses.
"""
from __future__ import annotations

import re
import unicodedata

LONG_VOWELS = "aêîoû"
SHORT_VOWELS = "eiu"
VOWELS = LONG_VOWELS + SHORT_VOWELS
CONSONANTS = "bcçdfghjklmnpqrsştvwxyz"
LETTERS = "abcçdeêfghiîjklmnopqrsştuûvwxyz"

# T32, read from the page image. Where the sign splits in two, the first one is the aspirated or tapped value.
IPA = {
    "a": "ɑ", "b": "b", "c": "dʒ", "ç": "tʃʰ", "d": "d", "e": "ɜ", "ê": "ɘ", "f": "f", "g": "g", "h": "h", "i": "ɨ",
    "î": "ɪ", "j": "ʒ", "k": "kʰ", "l": "l", "m": "m", "n": "n", "o": "o", "p": "pʰ", "q": "q", "r": "ɾ", "s": "s",
    "ş": "ʃ", "t": "tʰ", "u": "œ", "û": "u", "v": "v", "w": "w", "x": "x", "y": "j", "z": "z", "xw": "xʷ",
}
PLAIN_STOPS = {"ç": "tʃˤ", "k": "kˤ", "p": "pˤ", "t": "tˤ"}  # T32: the unaspirated member of each pair
TRILL = "r"

ONSET_CLUSTERS = ("str", "st", "şk", "sp", "sk", "şt", "xw")  # K27, T52-53; kept whole at the start of a word
_UPPER = {"İ": "i", "I": "i", "ı": "i"}  # T368: capital i has no dot; dotted forms are Turkish keyboards and OCR


def lower(text: str) -> str:
    """Kurmanji lower case; str.lower() alone turns İ into two code points."""
    text = unicodedata.normalize("NFC", text)
    return "".join(_UPPER.get(c, c.lower()) for c in text)


def is_vowel(c: str) -> bool:
    return c in VOWELS


def units(word: str) -> list[str]:
    """Letters, with xw as one unit (K22, T35). In xw + vowel the w never starts a syllable of its own."""
    out, i = [], 0
    while i < len(word):
        if word.startswith("xw", i):
            out.append("xw")
            i += 2
        else:
            out.append(word[i])
            i += 1
    return out


def syllables(word: str) -> list[str]:
    """Split a lower-case word into syllables (K27, T53).

    One consonant between vowels opens the next syllable, two are shared out, three leave two behind. Vowels side by
    side stay apart: they only meet in verb forms and loans (K26, T44). Clusters may only open a word.
    """
    u = units(word)
    nuclei = [i for i, x in enumerate(u) if x in VOWELS]
    if not nuclei:
        return [word] if word else []
    cuts = []
    for a, b in zip(nuclei, nuclei[1:]):
        gap = b - a - 1
        if gap <= 1:
            cuts.append(a + 1)
        elif gap == 2:
            cuts.append(a + 2)
        else:
            cuts.append(b - 1)
    cuts = [0] + cuts + [len(u)]
    return ["".join(u[x:y]) for x, y in zip(cuts, cuts[1:])]


def syllable_of(word: str, offset: int) -> int:
    """Index of the syllable that holds the character at offset."""
    n = 0
    for i, s in enumerate(syllables(word)):
        n += len(s)
        if offset < n:
            return i
    return max(0, len(syllables(word)) - 1)


# Sound changes at the joins of a word. T44-46: the same or a near sound is not said twice, whatever the spelling keeps.
_NEAR = {("d", "t"): "t", ("t", "d"): "d", ("t", "t"): "t", ("d", "d"): "d", ("k", "k"): "k", ("g", "k"): "k",
         ("s", "s"): "s", ("ş", "ş"): "ş", ("n", "n"): "n", ("r", "r"): "r", ("l", "l"): "l", ("h", "h"): "h",
         ("m", "m"): "m", ("b", "b"): "b", ("v", "v"): "v", ("z", "z"): "z"}


def spoken(word: str) -> str:
    """The word as it is said, still in letters.

    serokkomar -> serokomar, rindtir -> rintir, dewlemendtir -> dewlementir, destmal -> desmal (T44-46);
    diavêje -> davêje, biaxive -> baxive, naaxive -> naxive, naajo -> najo (T43, T344); gundiyê -> gundîyê (K26).
    """
    w = word
    w = re.sub(r"ndt", "nt", w)
    w = re.sub(r"stt|stm", lambda m: "st" if m.group(0) == "stt" else "sm", w)
    w = re.sub(r"(?<=[" + VOWELS + r"])([bcçdfgjklmnpqrsştvwxz])\1", r"\1", w) if "rr" not in w else w
    if w.startswith(("bia", "dia", "nia")) and len(w) > 4:
        w = w[0] + w[2:]
    elif w.startswith("naa"):
        w = "na" + w[3:]
    return w


def phones(word: str, stress: tuple[int, ...] = ()) -> str:
    """IPA of a lower-case word, with ˈ before a stressed syllable. Aspiration and r follow the default in IPA."""
    w = spoken(word)
    syl = syllables(w)
    out = []
    for i, s in enumerate(syl):
        mark = "ˈ" if i in stress else ""
        p = "".join(IPA.get(x, x) for x in units(s))
        out.append(mark + p)
    return ".".join(out)
