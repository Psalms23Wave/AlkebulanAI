# Copyright 2025-2026 Mathew Sekanjako and Psalms23Wave LLC
# SPDX-License-Identifier: Apache-2.0
"""Luganda grammar tables used to find the meaningful parts of a word.

These tables are Mathew Sekanjako's, carried over unchanged from version 1
(``tokenizer/ablt_tokenizer.py`` in the Alkebulan AI repository).
"""

from __future__ import annotations

NOUN_CLASSES: dict[str, dict[str, list[str]]] = {
    "class_1": {
        "singular_prefixes": ["omu", "mu", "omw", "mw"],
        "plural_prefixes": ["aba", "ba", "ab", "b"],
    },
    "class_2": {
        "singular_prefixes": ["omu", "mu", "omw", "mw"],
        "plural_prefixes": ["emi", "mi", "emy", "my"],
    },
    "class_3": {
        "singular_prefixes": ["eri", "ri", "e", "li", "ery", "ly", "ama", "ma", "am"],
        "plural_prefixes": ["ama", "ma", "am", "ga", "ag"],
    },
    "class_4": {
        "singular_prefixes": ["eki", "ki", "eky", "ky", "ech"],
        "plural_prefixes": ["ebi", "bi", "eby", "by"],
    },
    "class_5": {
        "singular_prefixes": ["aka", "ka", "ak"],
        "plural_prefixes": ["obu", "bu", "obw", "bw"],
    },
    "class_6": {
        "singular_prefixes": ["olu", "lu", "olw", "lw"],
        "plural_prefixes": ["en", "n", "enn", "em", "emm", "ez"],
    },
    "class_7": {
        "singular_prefixes": ["ogu", "gu", "ogw", "gw"],
        "plural_prefixes": ["aga", "ga", "ag", "g"],
    },
    "class_8": {
        "singular_prefixes": ["oku", "ku", "okw", "kw"],
        "plural_prefixes": ["ama", "ma", "am"],
    },
    "class_9": {"singular_prefixes": ["otu", "tu", "otw", "tw"], "plural_prefixes": []},
    "class_10": {
        "singular_prefixes": ["e", "en", "em", "eny"],
        "plural_prefixes": ["e", "en", "em", "eny"],
    },
}

VERB_PREFIXES: list[str] = [
    "n", "o", "a", "tu", "mu", "ba", "li", "ku", "na", "naa", "ki", "bi", "ga", "zi", "ya", "wa", "te", "si",
    "lu", "ka", "bu", "gu", "teba", "siba", "aba", "baa", "gaa", "yaa", "taa", "tee",
]  # fmt: skip

VERB_EXTENSIONS: list[str] = [
    "wa", "ibwa", "iwa", "ebwa", "era", "ira", "esa", "eka", "iza", "eza", "ulwa", "uka", "ula", "isa",
    "eddwa", "iddwa", "izibwa", "erera", "irira", "isiza", "ikiriza", "ukiriza", "ulula", "agana", "aŋŋa",
    "isana", "dde", "awo", "anga", "idira", "ingira", "zalira", "nga", "aganya",
]  # fmt: skip

NEGATION_PREFIXES: list[str] = ["te", "t", "si", "s", "tee", "ta"]

TENSE_MARKERS: dict[str, list[str]] = {
    "past": ["a", "dde", "zze", "ye"],
    "present": ["a", "e", "o"],
    "future": ["naa", "li", "jja"],
    "ongoing": ["kyaa", "nga"],
}

LOANWORDS: list[str] = [
    "gavumenti", "poliisi", "sikaala", "disitulikiti", "pulayimale", "paalamenti", "pulojekiti", "bbayibuli",
    "kompyuta", "kalenda",
]  # fmt: skip

# Every noun-class prefix, longest first, so the longest match is tried first.
NOUN_PREFIXES_LONGEST_FIRST: tuple[str, ...] = tuple(
    sorted(
        {
            prefix
            for forms in NOUN_CLASSES.values()
            for prefixes in forms.values()
            for prefix in prefixes
        },
        key=lambda prefix: (-len(prefix), prefix),
    )
)
VERB_EXTENSIONS_LONGEST_FIRST: tuple[str, ...] = tuple(
    sorted(VERB_EXTENSIONS, key=lambda ext: (-len(ext), ext))
)
