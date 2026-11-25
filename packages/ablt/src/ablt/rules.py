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
        {prefix for forms in NOUN_CLASSES.values() for prefixes in forms.values() for prefix in prefixes},
        key=lambda prefix: (-len(prefix), prefix),
    )
)
VERB_EXTENSIONS_LONGEST_FIRST: tuple[str, ...] = tuple(
    sorted(VERB_EXTENSIONS, key=lambda ext: (-len(ext), ext))
)

# ---------------------------------------------------------------------------------------
# Added in version 2.1. Everything above is unchanged.
#
# The tables below are the closed sets of the Luganda verb, as documented in published
# grammar (subject markers, tense markers and negatives as tabulated in "Luganda",
# Wikipedia, read 24 November 2026; see docs/research/2026-11-24-luganda-verb-grammar-sources.md
# in the Alkebulan AI project). They say what a verb prefix may look like. A cut is made
# only when the root that follows is also found in the training text (ablt.lexicon).
# ---------------------------------------------------------------------------------------

# Subject markers: persons, then noun classes. Longer forms are tried first.
SUBJECT_MARKERS: tuple[str, ...] = (
    "tu", "mu", "ba", "gu", "gi", "zi", "ki", "bi", "li", "ga", "ka", "bu", "lu", "ku", "n", "o", "a", "e",
)  # fmt: skip

# A person's subject marker written together with past -a-: twa-kola, ya-kola.
SUBJECT_WITH_PAST: tuple[str, ...] = ("twa", "mwa", "nna", "wa", "ya")

# Tense markers that stand between the subject marker and the root.
TENSE_MARKERS_BEFORE_ROOT: tuple[str, ...] = ("naa", "noo", "nee", "nna", "kya", "li", "a")
# The near future is -naa-, but -noo- after o- (you) and -nee- after e- (class 9).
TENSE_ONLY_AFTER: dict[str, str] = {"noo": "o", "nee": "e"}

# te- before a subject marker; si-, to-, ta- already say who (I, you, he or she).
NEGATIVE_BEFORE_SUBJECT: str = "te"
NEGATIVE_WITH_PERSON: tuple[str, ...] = ("si", "to", "ta")

# Passive, applied and causative endings, each with the final vowel.
EXTENSIONS_CUT_FROM_A_KNOWN_ROOT: tuple[str, ...] = ("ibwa", "ebwa", "ira", "era", "isa", "esa")

# Counting words 1 to 5 agree with their noun (babiri, asatu, ataano). They are not verbs.
NUMERAL_ROOTS: tuple[str, ...] = ("mu", "biri", "bbiri", "satu", "ssatu", "na", "nnya", "taano", "ttaano")

# "Of" for each noun class, and the endings that make "my", "your", "our" from it.
OF_FORMS: tuple[str, ...] = (
    "wa", "ba", "gwa", "gya", "ya", "za", "kya", "bya", "lya", "ga", "ka", "bwa", "lwa", "kwa", "twa",
)  # fmt: skip
POSSESSIVE_ENDINGS: tuple[str, ...] = (
    "ange", "o", "e", "affe", "ammwe", "aabwe", "abwe", "aago", "aazo", "aalyo", "aakyo", "aabyo",
)  # fmt: skip

# "Of" before a word that starts with a vowel, when two words are written as one:
# abanoonyi + b' + obubudamu is written abanoonyiboobubudamu.
OF_BEFORE_A_VOWEL: tuple[str, ...] = (
    "lw", "ly", "ky", "by", "bw", "gw", "tw", "kw", "gy", "b", "w", "y", "z", "g", "k", "l",
)  # fmt: skip

# Noun-class prefixes that begin with a vowel. A word cut by one of these, whose remainder
# is a known noun root, stays a noun.
NOUN_PREFIXES_BEFORE_A_NOUN_ROOT: tuple[str, ...] = (
    "aba", "omu", "emi", "ama", "eki", "ebi", "aka", "obu", "olu", "ogu", "aga", "otu", "eri", "oku",
    "omw", "emy", "eky", "eby", "obw", "olw", "ogw", "okw", "otw", "ery", "en", "em", "ab", "ak", "ag",
    "am", "ol", "og", "ez",
)  # fmt: skip

# Words tagged as conjunctions in MasakhaPOS Luganda that the verb rules would misread.
WORDS_LEFT_WHOLE: frozenset[str] = frozenset({"wabula"})
