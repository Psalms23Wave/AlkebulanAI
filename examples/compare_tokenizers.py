"""
Tokenizer Comparison Benchmark
==============================

Reproduces the headline finding of the ABLT validation notebook: ABLT
preserves Bantu morpheme boundaries (prefix, root, suffix) while Western-
trained tokenizers like mBERT and XLM-R split them arbitrarily.

Requires:
    pip install sentencepiece transformers

Run from the repository root:

    python examples/compare_tokenizers.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from tokenizer.ablt_tokenizer import ABLT  # noqa: E402


def main() -> None:
    samples = [
        "Abantu balina okuyiga oluganda.",
        "Buvunaanyizibwa bwa gavumenti okusomesa abantu baayo ku bulwadde.",
        "Abanoonyiboobubudamu bonna baasabiddwa beewandiise ewa ssentebe.",
        "Abalimi baatendekeddwa okukola emirimu egy'obutale.",
    ]

    ablt = ABLT.from_pretrained(os.path.join(ROOT, "tokenizer"))

    try:
        from transformers import AutoTokenizer
    except ImportError:
        print("transformers not installed. Running ABLT-only view.")
        AutoTokenizer = None

    mbert = xlmr = None
    if AutoTokenizer is not None:
        print("Loading mBERT and XLM-R for comparison...")
        mbert = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")
        xlmr = AutoTokenizer.from_pretrained("xlm-roberta-base")

    for s in samples:
        print("\n" + "=" * 78)
        print(f"Luganda: {s}")
        print("-" * 78)
        ablt_p = ablt.tokenize(s)
        print(f"ABLT  ({len(ablt_p):3d}): {ablt_p}")
        if mbert is not None:
            m = mbert.tokenize(s)
            print(f"mBERT ({len(m):3d}): {m}")
        if xlmr is not None:
            x = xlmr.tokenize(s)
            print(f"XLM-R ({len(x):3d}): {x}")


if __name__ == "__main__":
    main()
