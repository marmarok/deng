"""Kurmanji text tokens for the VoxCPM2 voice.

Measured on 31.10 (pivan/kurmanci-token.md): the stock tokenizer is a BPE built for 30 other languages. It cuts our words
at places that mean nothing (hatin -> ▁h|atin), spreads w over 537 pieces and uses 12,047 pieces for Kurmanji. Its
embeddings are frozen, so LoRA has to learn all of those. This tokenizer gives one token per sound:

  31 letters, each one always the same token
  xw as one token, the compound sound of both grammars (K22, T35)
  an optional stress sign before the stressed vowel (vurgu.py)
  space and the punctuation that changes how a sentence is read

It adds to the model: the checkpoint's vocabulary and weights do not change. xw and the stress sign live in two of the 976
unused <reserved_N> tokens. A small trainable table, one row per token used here, sits on top of the frozen embeddings.
"""
from __future__ import annotations

import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ses  # noqa: E402
import vurgu  # noqa: E402

SPACE = "▁"
TOKEN_STRESS = "<reserved_900>"
TOKEN_XW = "<reserved_901>"
PUNCT = ".,?!:;-"
FOLD = {"–": "-", "—": "-", "…": "...", "“": "", "”": "", "‘": "", "’": "", "«": "", "»": "", '"': "", "'": "", "(": "", ")": ""}
FOREIGN = {"ü": "û", "ö": "o", "ğ": "g", "é": "ê", "ä": "e", "â": "a", "à": "a", "á": "a", "è": "e", "ô": "o", "ñ": "n"}
SIGN = "ˈ"


def symbols(text: str, stress: bool = True, known=None) -> list[str]:
    """Text as a list of token names. Use it on text already prepared by hazirla()."""
    t = unicodedata.normalize("NFC", text)
    t = "".join(FOLD.get(c, c) for c in t)
    if stress:
        t = vurgu.mark(t, known, SIGN)
    t = ses.lower(t)
    out: list[str] = []
    i = 0
    while i < len(t):
        c = t[i]
        if t.startswith("xw", i):
            out.append(TOKEN_XW)
            i += 2
            continue
        i += 1
        if c == SIGN:
            out.append(TOKEN_STRESS)
        elif c in ses.LETTERS:
            out.append(c)
        elif c.isspace():
            if out and out[-1] != SPACE:
                out.append(SPACE)
        elif c in PUNCT:
            out.append(c)
        elif FOREIGN.get(c):
            out.append(FOREIGN[c])
    while out and out[-1] == SPACE:
        out.pop()
    return out


def alphabet() -> list[str]:
    """Every token this tokenizer can give, in a fixed order: the rows of the trainable table."""
    return list(ses.LETTERS) + [TOKEN_XW, TOKEN_STRESS, SPACE] + list(PUNCT)


class KurmanjiTokenizer:
    """Stands in for VoxCPM's text tokenizer: called with a string, gives token ids."""

    def __init__(self, base, stress: bool = True):
        self.base = base
        self.stress = stress
        vocab = base.tokenizer.get_vocab() if hasattr(base, "tokenizer") else base.get_vocab()
        self.ids = {s: vocab[s] for s in alphabet()}

    def __call__(self, text: str, **kwargs) -> list[int]:
        return [self.ids[s] for s in symbols(text, self.stress)]

    def tokenize(self, text: str, **kwargs) -> list[str]:
        return symbols(text, self.stress)


def install(model, stress: bool = True) -> KurmanjiTokenizer:
    """Give a VoxCPM2 model this tokenizer and the trainable table on top of its frozen embeddings.

    The table's name holds "lora_", so VoxCPM's own save_checkpoint keeps it with the LoRA weights and load_lora_weights
    brings it back by name. The frozen embedding table is not touched: rows are added to its output by a forward hook,
    which also runs where the model embeds text at reading time. Rows start at zero, except xw and the stress sign: their
    reserved rows were never trained. xw starts as the mean of x and w (K22: one sound built from the two), the stress sign
    keeps its reserved vector unless that vector is near zero, then it starts as a random vector of a letter's length.
    """
    import torch

    tok = KurmanjiTokenizer(model.text_tokenizer, stress)
    lm = model.base_lm
    emb = lm.embed_tokens
    device = emb.weight.device
    names = alphabet()
    ids = torch.tensor([tok.ids[s] for s in names], device=device)
    with torch.no_grad():
        base = emb.weight[ids].float()
        delta = torch.zeros_like(base)
        at = {s: i for i, s in enumerate(names)}
        delta[at[TOKEN_XW]] = (base[at["x"]] + base[at["w"]]) / 2 - base[at[TOKEN_XW]]
        letters = base[[at[s] for s in ses.LETTERS]].norm(dim=1)
        norm = base[at[TOKEN_STRESS]].norm()
        if norm < 0.1 * letters.mean():
            g = torch.Generator(device="cpu").manual_seed(900)
            v = torch.randn(base.shape[1], generator=g).to(device)
            delta[at[TOKEN_STRESS]] = v / v.norm() * letters.mean()
    print("text table:", {"rows": len(names), "dim": base.shape[1], "letter_norm": round(letters.mean().item(), 3),
                          "stress_row_norm": round(norm.item(), 3), "xw_row_norm": round(base[at[TOKEN_XW]].norm().item(), 3)}, flush=True)
    lookup = torch.full((emb.weight.shape[0],), -1, dtype=torch.long, device=device)
    lookup[ids] = torch.arange(len(names), device=device)
    lm.register_buffer("text_delta_lookup", lookup, persistent=False)
    lm.register_parameter("lora_text_delta", torch.nn.Parameter(delta))

    def add_rows(_module, args, out):
        row = lm.text_delta_lookup[args[0]]
        return out + (row >= 0).unsqueeze(-1).to(out.dtype) * lm.lora_text_delta[row.clamp(min=0)].to(out.dtype)

    emb.register_forward_hook(add_rows)
    model.text_tokenizer = tok
    return tok


def describe(text: str, stress: bool = True) -> str:
    return " ".join({TOKEN_STRESS: "ˈ", TOKEN_XW: "xw"}.get(s, s) for s in symbols(text, stress))


if __name__ == "__main__":
    for line in sys.argv[1:] or ["Ez dixwazim pirtûkekê bixwînim.", "Ew duh hatin, lê hatin ne hêsan bû."]:
        print(describe(line))
        print(re.sub(r"\s+", " ", vurgu.mark(line)))
