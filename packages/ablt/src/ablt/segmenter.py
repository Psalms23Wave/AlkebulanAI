# Copyright 2025-2026 Mathew Sekanjako and Psalms23Wave LLC
# SPDX-License-Identifier: Apache-2.0
"""Cut Luganda text at grammar boundaries without changing a single character."""

from __future__ import annotations

import re

from .rules import LOANWORDS, NOUN_PREFIXES_LONGEST_FIRST, VERB_EXTENSIONS_LONGEST_FIRST

SHORTEST_WORD_TO_CUT = 4
# A word is a run of letters. An apostrophe ends it, as in version 1, so the
# "ng" of ng'ombe is never cut.
WORD = re.compile(r"[^\W\d_]+")
ENDS_A_SENTENCE = re.compile(r"[.!?][\"')\]]*\s*$")


def is_loanword(word: str) -> bool:
    """True for the listed loanwords, which are left whole (the same test as version 1)."""
    lower = word.lower()
    return any(loan in lower or lower in loan for loan in LOANWORDS)


def split_word(word: str) -> list[str]:
    """The parts of one word, in order. Joined together they give the word back.

    This is the version 1 rule: the longest noun-class prefix if there is one,
    otherwise the longest verb extension at the end. Version 2 matches without
    regard to capital letters, so ``Abantu`` is cut the same way as ``abantu``.
    """
    if len(word) < SHORTEST_WORD_TO_CUT or is_loanword(word):
        return [word]
    lower = word.lower()
    for prefix in NOUN_PREFIXES_LONGEST_FIRST:
        if lower.startswith(prefix) and len(word) > len(prefix) + 1:
            return [word[: len(prefix)], word[len(prefix) :]]
    for extension in VERB_EXTENSIONS_LONGEST_FIRST:
        if lower.endswith(extension) and len(word) > len(extension) + 1:
            return [word[: -len(extension)], word[-len(extension) :]]
    return [word]


def looks_like_a_name(word: str, starts_sentence: bool) -> bool:
    """Acronyms, and capitalised words in the middle of a sentence, are treated as names."""
    if len(word) > 1 and word.isupper():
        return True
    return word[0].isupper() and not starts_sentence


def cut(text: str) -> list[str]:
    """Split a text into chunks at the grammar boundaries inside its words.

    ``"".join(cut(text)) == text`` always: nothing is added, removed or changed.
    Every chunk after the first starts in the middle of a word. Names (see
    ``looks_like_a_name``) are left whole.

    >>> cut("Abantu basoma ebitabo.")
    ['Aba', 'ntu ba', 'soma ebi', 'tabo.']
    """
    chunks, chunk_start = [], 0
    for match in WORD.finditer(text):
        word = match.group()
        before = text[: match.start()]
        starts_sentence = not before.strip() or bool(ENDS_A_SENTENCE.search(before))
        if looks_like_a_name(word, starts_sentence):
            continue
        position = match.start()
        for part in split_word(word)[:-1]:
            position += len(part)
            chunks.append(text[chunk_start:position])
            chunk_start = position
    chunks.append(text[chunk_start:])
    return chunks


def show_cuts(text: str, mark: str = "|") -> str:
    """The text with a visible mark at every cut, for reading: ``Aba|ntu``."""
    return mark.join(cut(text))
