# Copyright 2025-2026 Mathew Sekanjako and Psalms23Wave LLC
# SPDX-License-Identifier: Apache-2.0
"""Word lists built from the training text. The rules check a cut against them.

``tools/build_lexicon.py`` writes the three files. Nothing here is a rule: these lists are
the evidence a rule asks for before it cuts.
"""

from __future__ import annotations

from functools import lru_cache
from importlib import resources


def _lines(name: str) -> list[str]:
    text = (resources.files("ablt") / "lexicon" / name).read_text(encoding="utf-8")
    return [line for line in text.splitlines() if line and not line.startswith("#")]


@lru_cache(maxsize=1)
def verb_roots() -> dict[str, int]:
    """Each root seen after ``oku-`` in the training text, with how often it was seen."""
    return {root: int(count) for root, count in (line.split("\t") for line in _lines("verb_roots.tsv"))}


@lru_cache(maxsize=1)
def noun_roots() -> frozenset[str]:
    """Word endings seen after two or more different noun-class prefixes."""
    return frozenset(_lines("noun_roots.txt"))


@lru_cache(maxsize=1)
def common_words() -> frozenset[str]:
    """Words of five letters or more seen at least three times."""
    return frozenset(_lines("words.txt"))
