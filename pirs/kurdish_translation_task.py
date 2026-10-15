# Kaggle Benchmarks task: Northern Kurdish (Latin script) translation, both directions.
# Data: 100 sentence pairs sampled from the FLEURS Northern Kurdish validation split
# (aranemini/northern-kurdish-fleurs, CC BY 4.0). Score: chrF (0-100) against the reference.
from collections import Counter

import pandas as pd
import kaggle_benchmarks as kbench

DATA_URL = "https://raw.githubusercontent.com/marmarok/deng/main/pirs/fleurs-dev-100.csv"
data = pd.read_csv(DATA_URL)


def chrf(hyp: str, ref: str, n: int = 6, beta: float = 2.0) -> float:
    """Character n-gram F-score (chrF, Popovic 2015), whitespace removed, 0-100."""
    hyp, ref = "".join(hyp.split()), "".join(ref.split())
    precisions, recalls = [], []
    for k in range(1, n + 1):
        h = Counter(hyp[i:i + k] for i in range(len(hyp) - k + 1))
        r = Counter(ref[i:i + k] for i in range(len(ref) - k + 1))
        if not h or not r:
            continue
        overlap = sum((h & r).values())
        precisions.append(overlap / sum(h.values()))
        recalls.append(overlap / sum(r.values()))
    if not precisions:
        return 0.0
    p, r = sum(precisions) / len(precisions), sum(recalls) / len(recalls)
    if p + r == 0:
        return 0.0
    return 100 * (1 + beta**2) * p * r / (beta**2 * p + r)


def clean(text: str) -> str:
    """Keep the first non-empty line; drop quotes the model may wrap around it."""
    for line in text.strip().splitlines():
        line = line.strip().strip('"').strip()
        if line:
            return line
    return ""


@kbench.task(name="kurdish_northern_en_to_ku")
def en_to_ku(llm, english: str, kurdish: str) -> float:
    reply = llm.prompt(
        "Translate the following English sentence into Northern Kurdish (Kurmanji) "
        "written in the Latin (Hawar) alphabet, as a native speaker would write it. "
        "Reply with the translation only.\n\n" + english
    )
    return chrf(clean(reply), kurdish)


@kbench.task(name="kurdish_northern_ku_to_en")
def ku_to_en(llm, english: str, kurdish: str) -> float:
    reply = llm.prompt(
        "Translate the following Northern Kurdish (Kurmanji) sentence into English. "
        "Reply with the translation only.\n\n" + kurdish
    )
    return chrf(clean(reply), english)


for task in (en_to_ku, ku_to_en):
    runs = task.evaluate(llm=[kbench.llm], evaluation_data=data[["english", "kurdish"]],
                         on_failure="continue", max_attempts=3)
    scores = runs.completed_runs.as_dataframe()["result"]
    print(task.name, "chrF mean:", round(scores.mean(), 2), "n:", len(scores))
