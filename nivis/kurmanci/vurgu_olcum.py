"""Do the stress rules of vurgu.py hold on speech? Prepares the words for olc_worker.py and reads what it measured.

Rule of thumb from the phonetics of stress: length, pitch, loudness and the share of energy above 500 Hz all rise on a
stressed vowel, none of them alone proves it, and every one of them also rises before a pause. So a table here always
compares like with like: the same word shape and the same place in the phrase, one rule against the other reading.
"""
from __future__ import annotations

import collections
import glob
import gzip
import json
import math
import os
import re
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ses  # noqa: E402
import vurgu  # noqa: E402

ALIGN = str.maketrans({"ç": "c", "ê": "e", "î": "i", "ş": "s", "û": "u"})
ALIGN_OK = re.compile(r"^[a-z']+$")


def clip_words(text: str, known=None) -> list[dict]:
    """The words of a clip with what the rules say about each: input of olc_worker.py."""
    spans = list(vurgu.WORD.finditer(text))
    out = []
    for i, (m, w) in enumerate(zip(spans, vurgu.sentence(text, known))):
        low = ses.lower(m.group(0))
        end = spans[i + 1].start() if i + 1 < len(spans) else len(text)
        vowels, at = [], 0
        for syl in w.syllables:
            vowels.append(next((at + k for k, c in enumerate(syl) if c in ses.VOWELS), None))
            at += len(syl)
        a = low.translate(ALIGN)
        ok = at == len(low) and bool(ALIGN_OK.match(a))
        out.append({"w": low, "a": a if ok else re.sub(r"[^a-z']", "", a), "ok": ok, "k": w.kind, "r": w.rule, "s": list(w.stress),
                    "vi": vowels, "p": text[m.end(): end].strip()[:1]})
    return out


def clips_of(paths):
    for p in paths:
        with (gzip.open(p, "rt", encoding="utf8") if p.endswith(".gz") else open(p, encoding="utf8")) as f:
            for line in f:
                yield json.loads(line)


def _stats(values):
    v = [x for x in values if x is not None]
    if len(v) < 2:
        return None
    sd = st.pstdev(v)
    return (st.fmean(v), sd) if sd > 0 else None


def _z(x, s):
    return None if x is None or s is None else (x - s[0]) / s[1]


def measured(clips):
    """One row per word with two or more measured vowels: the score P of each syllable.

    Each cue is measured against the same vowel in this source, because vowels differ by nature: `a` is louder and longer
    than `i`, whatever the stress. Pitch, loudness and the share above 500 Hz are first taken relative to the clip. P is the
    mean of the four z scores. A vowel the aligner placed with low confidence is dropped.
    """
    clips = list(clips)
    bases, pools = [], collections.defaultdict(lambda: ([], [], [], []))
    for c in clips:
        vs = [v for w in c["words"] for v in w["v"]]
        base = {i: _stats([v[i] for v in vs]) for i in (3, 5, 6)}
        bases.append(base)
        for v in vs:
            pool = pools[(c.get("src"), v[1])]
            if v[2] >= 20:
                pool[0].append(v[2])
            for j, i in enumerate((3, 5, 6), 1):
                if v[i] is not None and base[i] is not None:
                    pool[j].append(v[i] - base[i][0])
    norm = {k: [_stats(x) for x in pool] for k, pool in pools.items()}
    for c, base in zip(clips, bases):
        n = len(c["words"])
        for at, w in enumerate(c["words"]):
            row = {}
            for v in w["v"]:
                if v[7] < 0.1 or v[2] < 20:
                    continue
                st_ = norm[(c.get("src"), v[1])]
                z = [_z(v[2], st_[0])] + [None if v[i] is None or base[i] is None else _z(v[i] - base[i][0], st_[j]) for j, i in enumerate((3, 5, 6), 1)]
                if sum(x is not None for x in z) >= 3:
                    row[v[0]] = z
            if len(row) >= 2 and len(row) == len(w["v"]):
                zs = [row[i] for i in sorted(row)]
                yield {"id": c["id"], "src": c.get("src"), "w": w["w"], "k": w["k"], "r": w["r"], "s": w["s"], "n": len(w["v"]), "Z": zs,
                       "P": [st.fmean(x for x in z if x is not None) for z in zs], "final": bool(w["p"]) or at == n - 1, "prev": c["words"][at - 1]["w"] if at else ""}


def mean_ci(values):
    v = list(values)
    if len(v) < 2:
        return (st.fmean(v) if v else float("nan")), float("nan"), len(v)
    return st.fmean(v), 1.96 * st.stdev(v) / math.sqrt(len(v)), len(v)


def cues(rows, a=0, b=-1):
    """Syllable b minus syllable a, cue by cue: length, pitch, loudness, energy share."""
    out = []
    for i in range(4):
        v = [r["Z"][b][i] - r["Z"][a][i] for r in rows if r["Z"][b][i] is not None and r["Z"][a][i] is not None]
        out.append(st.fmean(v) if v else float("nan"))
    return "  ".join(f"{name}{x:+.2f}" for name, x in zip(("len", "f0", "dB", "hi"), out))


def line(name, rows, a=0, b=-1):
    rows = list(rows)
    m, ci, n = mean_ci(r["P"][b] - r["P"][a] for r in rows)
    return f"  {name:52s} n={n:6d}  {m:+.3f} ± {ci:.3f}   {cues(rows, a, b) if n else ''}"


PASSIVE = {"hat", "hatin", "tê", "tên", "bê", "bên", "hatiye", "hatine", "hatibû", "dihat", "nayê", "nayên", "neyê"}


def report(rows):
    """The tables of pivan/vurgu-olcum.md, one source at a time. Above zero: the later syllable leads."""
    for src in sorted({r["src"] for r in rows}):
        sel = [r for r in rows if r["src"] == src]
        print(f"\n=== {src}: {len(sel)} words with 2+ measured vowels")
        for pos, name in ((False, "inside the phrase"), (True, "before a pause")):
            two = [r for r in sel if r["n"] == 2 and r["final"] is pos]
            print(f"-- two syllables, {name}: last - first")
            print(line("1. past -in, stem stress (T79)", (r for r in two if r["k"] == "past" and r["w"].endswith("in") and r["s"] == [0])))
            print(line("1. infinitive after hat/tê/bê, final (T79)", (r for r in two if r["k"] == "inf" and r["prev"] in PASSIVE)))
            print(line("1. infinitive elsewhere, final", (r for r in two if r["k"] == "inf" and r["prev"] not in PASSIVE)))
            print(line("2. noun -ê/-a/-ek, stem stress (T79)", (r for r in two if r["r"] == "T79 transparent ending")))
            print(line("2. noun -an/-ên, final (T79)", (r for r in two if r["r"] == "T79 plural")))
            print(line("2. noun, bare, final (T78)", (r for r in two if r["r"] == "T78 final")))
            print(line("3. di- present, prefix stress (T80)", (r for r in two if r["r"] == "T80 di-")))
            print(line("3. negative, prefix stress (T79)", (r for r in two if r["r"] == "T79 negation")))
            print(line("3. bi- free, prefix stress (T80)", (r for r in two if r["r"] == "T80 bi-")))
            print(line("3. bi- after a governor (K28), stem", (r for r in two if r["r"] == "K28 governed subjunctive, stem")))
        three = [r for r in sel if r["n"] == 3 and not r["final"]]
        print("-- three syllables inside the phrase: P2 - P1 and P3 - P1")
        for name, test in (("4. preverb infinitive (K28 first, T79 last)", lambda r: r["r"] == "K28 preverb"),
                           ("4. plain infinitive, final", lambda r: r["k"] == "inf" and r["r"].startswith("T79")),
                           ("3. di- present", lambda r: r["r"] == "T80 di-"),
                           ("5. bi- free (T80 first)", lambda r: r["r"] == "T80 bi-"),
                           ("5. bi- after a governor (K28 stem)", lambda r: r["r"] == "K28 governed subjunctive, stem"),
                           ("5. preverb finite (T80 first)", lambda r: r["r"] == "T80 preverb"),
                           ("6. -iya, -iyê (K26)", lambda r: r["r"] == "K26 î stem"),
                           ("6. -ekî (K28 last)", lambda r: r["r"] == "K28 -ekî"),
                           ("2. noun -ê/-a/-ek", lambda r: r["r"] == "T79 transparent ending"),
                           ("2. noun -an/-ên", lambda r: r["r"] == "T79 plural")):
            print(line(name + " P2-P1", (r for r in three if test(r)), 0, 1))
            print(line(name + " P3-P1", (r for r in three if test(r)), 0, 2))
        print("-- same verb, past against infinitive, last - first, both before a pause")
        verbs = collections.defaultdict(lambda: [[], []])
        for r in sel:
            if r["n"] == 2 and r["final"] and r["w"].endswith("in"):
                d = r["P"][-1] - r["P"][0]
                if r["k"] == "past" and r["s"] == [0]:
                    verbs[r["w"]][0].append(d)
                elif r["k"] == "inf" and r["prev"] in PASSIVE:
                    verbs[r["w"]][1].append(d)
        for w, (a, b) in sorted(verbs.items(), key=lambda kv: -min(len(kv[1][0]), len(kv[1][1])))[:12]:
            if a and b:
                print(f"  {w:14s} past n={len(a):4d} {st.fmean(a):+.3f}   infinitive n={len(b):4d} {st.fmean(b):+.3f}   D {st.fmean(b) - st.fmean(a):+.3f}")


def pair_index(path):
    """Stress pairs read by the voices: D = (last - first) in the infinitive minus (last - first) in the past."""
    clips = list(clips_of([path]))
    out = collections.defaultdict(dict)
    for r in (x for x in measured(clips) if x["final"]):
        tag, no = r["id"].rsplit("-", 1)
        no = int(no)
        out[tag].setdefault((no - 3000) // 2, {})[(no - 3000) % 2] = r["P"][-1] - r["P"][0]
    res = {}
    for tag, pairs in out.items():
        d = {k: v[1] - v[0] for k, v in pairs.items() if 0 in v and 1 in v}
        plain = [v for k, v in d.items() if k <= 11]
        res[tag] = {"pairs": len(d), "right_direction": sum(v > 0 for v in plain), "plain": len(plain), "median_D": round(st.median(plain), 3) if plain else None,
                    "by_pair": {k: round(v, 2) for k, v in sorted(d.items())}}
    return res


if __name__ == "__main__":
    report(list(measured(clips_of(sys.argv[1:] or glob.glob("pivan/vurgu-sonuc/*.jsonl.gz")))))
