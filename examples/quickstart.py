"""
ABLT Quickstart
===============

Minimal example showing how to load the Alkebulan Bantu-Luganda Tokenizer
and tokenize Luganda text.

Run from the repository root:

    python examples/quickstart.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from tokenizer.ablt_tokenizer import ABLT  # noqa: E402


def main() -> None:
    tokenizer_dir = os.path.join(ROOT, "tokenizer")
    tok = ABLT.from_pretrained(tokenizer_dir)
    print(f"Loaded {tok}\n")

    samples = [
        "Abantu balina okuyiga oluganda.",
        "Abanoonyiboobubudamu bonna baasabiddwa beewandiise ewa ssentebe.",
        "Abalimi baatendekeddwa okukola emirimu egy'obutale.",
        "ekinaataagulwataagulwanga",
        "Webale nnyo ssebo.",
    ]

    for text in samples:
        pieces = tok.tokenize(text)
        ids = tok.encode(text)
        round_trip = tok.decode(ids)
        importance = tok.get_tokens_with_importance(text)

        print(f"Input     : {text}")
        print(f"Pieces    : {pieces}")
        print(f"Count     : {len(pieces)}")
        print(f"IDs       : {ids}")
        print(f"Decoded   : {round_trip}")
        print(f"Importance: {importance[:8]}{'...' if len(importance) > 8 else ''}")
        print("-" * 70)


if __name__ == "__main__":
    main()
