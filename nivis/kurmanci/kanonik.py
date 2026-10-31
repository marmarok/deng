"""One written form for one word, for scoring and for future training labels.

Nothing here touches hazirla.py, the locked exams or the official scores. The official score stays what it is; this gives
a second number that does not count a spelling difference as a hearing error.

Rules (K25-26, T41, T45, T347-355, T369-370): spelling variants the grammars name as one word take the form they prefer.
"""
from __future__ import annotations

import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ses  # noqa: E402

VOWEL = "aeêiîouû"
# T347-355: the form the grammars keep, against the variants that spread. Only cases the books settle.
VARIANTS = {
    "arîkar": "alîkar", "arîkarî": "alîkarî", "şikeştin": "şikestin", "merov": "mirov", "merovan": "mirovan",
    "merovên": "mirovên", "weha": "wiha", "herweha": "herwiha", "wesa": "wisa", "herwesa": "herwisa", "wenda": "winda",
    "tejî": "tijî", "çel": "çil", "livîn": "nivîn", "limêj": "nimêj", "hefdeh": "hevdeh", "cîh": "cih", "mîh": "mih",
    "rîh": "rih", "sîh": "sih", "doh": "duh", "gellek": "gelek", "pirr": "pir", "kû": "ku", "ko": "ku", "tirkiye": "tirkiye",
    "xerab": "xirab", "cûda": "cuda", "şunda": "şûnda", "aniha": "niha", "anha": "niha", "niho": "niha",
}
# T369-370: written apart, whatever the writer's habit.
SPLIT = {
    "herkes": "her kes", "hertişt": "her tişt", "herdem": "her dem", "hertim": "her tim", "herroj": "her roj", "herdu": "her du",
    "herçend": "her çend", "herçi": "her çi", "tukes": "tu kes", "tutişt": "tu tişt", "evqas": "ev qas", "ewqas": "ew qas", "çiqas": "çi qas",
    "hemûkes": "hemû kes", "hinkes": "hin kes", "anjî": "an jî", "yanjî": "yan jî", "pircaran": "pir caran", "hincaran": "hin caran",
    "jibo": "ji bo", "jiber": "ji ber", "lêbelê": "lê belê", "lebelê": "lê belê", "lêbele": "lê belê",
}
_IY = re.compile(r"î(?=y[" + VOWEL + "])")
_DOUBLE = re.compile(r"([bcçdfgjklmnpqsştvxz])\1")


def word(w: str) -> str:
    w = _IY.sub("i", w)  # K26: gundiyê, not gundîyê
    w = _DOUBLE.sub(r"\1", w)  # T45: no written gemination in native words
    return VARIANTS.get(w, w)


def kanonik(text: str) -> str:
    """Lower case, no punctuation, one form per word."""
    t = unicodedata.normalize("NFC", ses.lower(text or "")).replace("’", "").replace("'", "")
    t = re.sub(r"[^\w\s]", " ", t)
    out = []
    for w in t.split():
        w = SPLIT.get(w, w)
        out.extend(word(x) for x in w.split())
    return " ".join(out)
