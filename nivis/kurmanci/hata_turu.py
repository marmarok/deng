#!/usr/bin/env python3
"""Sort an ear's word errors by what kind of error they are, so the next step goes where the errors are.

  python3 nivis/kurmanci/hata_turu.py nbest-0.jsonl nbest-1.jsonl

Input rows hold ref and cands (top first). Classes (T344-355, K26, K42):
  circumflex   only ê/e, î/i, û/u differ
  spelling     a variant the books call one word (w/v, u/i, doubled letters, iy/îy, h inside)
  spacing      words joined or split (ezê/ez ê, hevdu/hev du)
  ending       same stem, another inflection ending
  prefix       same stem, another verb prefix
  near         at most a quarter of the letters differ
  other        a different word; missing       the ear wrote nothing; extra       the ear added a word
"""
import collections
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ses  # noqa: E402

ENDINGS = sorted("ê a î an ên ek ekê ekî eke in ine inan im e ye me ne iye yê ya yên o ino".split(), key=len, reverse=True)
PREFIXES = ("nedi", "di", "bi", "na", "ne", "ni", "me")
FOLD = str.maketrans({"ê": "e", "î": "i", "û": "u"})


def norm(t):
    t = unicodedata.normalize("NFC", ses.lower(t or "")).replace("’", "").replace("'", "")
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", t)).strip()


def align(a, b):
    """Word alignment by edit distance: yields (ref word or None, hyp word or None)."""
    n, m = len(a), len(b)
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        d[i][0] = i
    for j in range(m + 1):
        d[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] != b[j - 1]))
    out, i, j = [], n, m
    while i or j:
        if i and j and d[i][j] == d[i - 1][j - 1] + (a[i - 1] != b[j - 1]):
            out.append((a[i - 1], b[j - 1])); i -= 1; j -= 1
        elif i and d[i][j] == d[i - 1][j] + 1:
            out.append((a[i - 1], None)); i -= 1
        else:
            out.append((None, b[j - 1])); j -= 1
    return out[::-1]


def edit(a, b):
    p = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        c = [i]
        for j, y in enumerate(b, 1):
            c.append(min(p[j] + 1, c[-1] + 1, p[j - 1] + (x != y)))
        p = c
    return p[-1]


def skeleton(w):
    """Spelling variants fall together here (T347-355)."""
    w = w.translate(FOLD).replace("w", "v").replace("iy", "i").replace("h", "")
    w = re.sub(r"(.)\1", r"\1", w)
    return w.replace("u", "i")


def stem(w):
    for e in ENDINGS:
        if w.endswith(e) and len(w) - len(e) >= 3:
            return w[: -len(e)]
    return w


def unprefixed(w):
    for p in PREFIXES:
        if w.startswith(p) and len(w) - len(p) >= 2:
            return w[len(p):]
    return w


def classify(r, h):
    if r.translate(FOLD) == h.translate(FOLD):
        return "circumflex"
    if skeleton(r) == skeleton(h):
        return "spelling"
    if stem(r) == stem(h) or skeleton(stem(r)) == skeleton(stem(h)):
        return "ending"
    if unprefixed(r) == unprefixed(h):
        return "prefix"
    return "near" if edit(r, h) <= max(1, len(r) // 4) else "other"


def merge_spacing(pairs):
    """Two aligned slots that spell one word: count one spacing error, not two errors."""
    out, i = [], 0
    while i < len(pairs):
        a, b = pairs[i]
        if i + 1 < len(pairs):
            c, d = pairs[i + 1]
            if a and c and b and d is None and a + c == b or a and c is None and b and d and False:
                out.append(("spacing", a + " " + c, b)); i += 2; continue
            if a and c is None and b and d and a == b + d:
                out.append(("spacing", a, b + " " + d)); i += 2; continue
            if a and b is None and c and d and a + c == d:
                out.append(("spacing", a + " " + c, d)); i += 2; continue
            if a is None and b and c and d and c == b + d:
                out.append(("spacing", c, b + " " + d)); i += 2; continue
        out.append((None, a, b)); i += 1
    return out


def analyse(rows):
    total = 0
    count = collections.Counter()
    ex = collections.defaultdict(collections.Counter)
    for row in rows:
        ref, hyp = norm(row["ref"]).split(), norm(row["cands"][0]).split()
        total += len(ref)
        for tag, r, h in merge_spacing(align(ref, hyp)):
            if tag:
                c = tag
            elif r == h:
                continue
            elif r is None:
                c = "extra"
            elif h is None:
                c = "missing"
            else:
                c = classify(r, h)
            count[c] += 1
            ex[c][f"{r} > {h}"] += 1
    return total, count, ex


def main(paths):
    rows = []
    for p in paths:
        with open(p, encoding="utf8") as f:
            rows += [json.loads(l) for l in f]
    groups = {"all": rows}
    for r in rows:
        groups.setdefault(r.get("set", "?"), []).append(r)
    for name, sel in groups.items():
        total, count, ex = analyse(sel)
        errs = sum(count.values())
        print(f"\n{name}: {len(sel)} clips, {total} words, {errs} error events, {100 * errs / total:.2f} per 100 words")
        for c, n in count.most_common():
            print(f"  {c:11s} {n:5d}  {100 * n / errs:5.1f}%  {100 * n / total:5.2f} points   e.g. {[k for k, _ in ex[c].most_common(7)]}")


if __name__ == "__main__":
    main(sys.argv[1:])
