# Copyright 2025-2026 Mathew Sekanjako and Psalms23Wave LLC
# SPDX-License-Identifier: Apache-2.0
"""Build the word lists that the version 2.1 rules check a cut against.

Run from the repository root, before ``train_model.py``:

    python packages/ablt/tools/build_lexicon.py

Only the training lines are read (the same split as ``train_model.py``), so the held-out
lines stay unseen. Three lists are written to ``src/ablt/lexicon``:

- ``verb_roots.tsv``: what follows ``oku-`` ("to ...") in the text, with how often.
  A verb is cut into subject, tense and root only when its root is in this list.
- ``noun_roots.txt``: word endings seen after two or more different noun-class prefixes,
  such as ``ntu`` in ``omuntu``, ``abantu``, ``ekintu``. These are kept as nouns.
- ``words.txt``: words seen at least three times, used to recognise two words written as one.
"""

from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT / "src"))
sys.path.insert(0, str(PACKAGE_ROOT / "tools"))
from ablt.rules import NOUN_PREFIXES_BEFORE_A_NOUN_ROOT  # noqa: E402
from train_model import split_corpus  # noqa: E402

LEXICON_DIR = PACKAGE_ROOT / "src" / "ablt" / "lexicon"
WORD = re.compile(r"[^\W\d_]+")
SHORTEST_ROOT = 3
ROOT_SEEN_AT_LEAST = 5
NOUN_FORM_SEEN_AT_LEAST = 2
WORD_SEEN_AT_LEAST = 3
SHORTEST_LISTED_WORD = 5
CREDIT = "# Built from Luganda text that includes the SALT dataset by Sunbird AI (CC BY-SA 4.0).\n"


def count_words(lines: list[str]) -> Counter[str]:
    return Counter(word.lower() for line in lines for word in WORD.findall(line))


def verb_roots(words: Counter[str]) -> Counter[str]:
    """Roots seen after ``oku-``, or after ``okw-`` before a vowel."""
    roots: Counter[str] = Counter()
    for word, count in words.items():
        if len(word) < 6:
            continue
        if word.startswith("oku") or (word.startswith("okw") and word[3] in "aeiou"):
            roots[word[3:]] += count
    return roots


def noun_roots(words: Counter[str]) -> list[str]:
    seen_after: dict[str, set[str]] = defaultdict(set)
    for word, count in words.items():
        if count < NOUN_FORM_SEEN_AT_LEAST:
            continue
        for prefix in NOUN_PREFIXES_BEFORE_A_NOUN_ROOT:
            if word.startswith(prefix) and len(word) > len(prefix) + 1:
                seen_after[word[len(prefix) :]].add(prefix)
    return sorted(root for root, prefixes in seen_after.items() if len(prefixes) >= 2)


def main() -> None:
    training_lines, _ = split_corpus()
    words = count_words(training_lines)
    roots = verb_roots(words)
    listed_roots = {r: n for r, n in roots.items() if n >= ROOT_SEEN_AT_LEAST and len(r) >= SHORTEST_ROOT}
    nouns = noun_roots(words)
    common = sorted(w for w, n in words.items() if n >= WORD_SEEN_AT_LEAST and len(w) >= SHORTEST_LISTED_WORD)

    LEXICON_DIR.mkdir(parents=True, exist_ok=True)
    (LEXICON_DIR / "verb_roots.tsv").write_text(
        CREDIT + "".join(f"{root}\t{count}\n" for root, count in sorted(listed_roots.items())),
        encoding="utf-8",
    )
    (LEXICON_DIR / "noun_roots.txt").write_text(CREDIT + "\n".join(nouns) + "\n", encoding="utf-8")
    (LEXICON_DIR / "words.txt").write_text(CREDIT + "\n".join(common) + "\n", encoding="utf-8")
    print(f"{len(listed_roots)} verb roots, {len(nouns)} noun roots, {len(common)} common words")
    print(f"written to {LEXICON_DIR.relative_to(PACKAGE_ROOT.parents[1])}")


if __name__ == "__main__":
    main()
