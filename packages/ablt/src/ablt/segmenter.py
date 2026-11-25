# Copyright 2025-2026 Mathew Sekanjako and Psalms23Wave LLC
# SPDX-License-Identifier: Apache-2.0
"""Cut Luganda text at grammar boundaries without changing a single character.

Version 2.1 cuts a word in as many places as its grammar shows:

    tebasobola   ->  te | ba | sobola        (not + they + be able)
    alisoma      ->  a | li | soma           (he or she + will + read)
    okusomesa    ->  oku | som | esa         (to + read + make: to teach)

It does this only on evidence. The prefixes must come from the documented tables in
``rules.py`` and the root must be in the list of roots seen in the training text
(``ablt.lexicon``). When that evidence is missing, the word is cut exactly as version 2.0
cut it, by ``single_cut``.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from functools import lru_cache

from . import lexicon
from .rules import (
    EXTENSIONS_CUT_FROM_A_KNOWN_ROOT,
    LOANWORDS,
    NEGATIVE_BEFORE_SUBJECT,
    NEGATIVE_WITH_PERSON,
    NOUN_PREFIXES_BEFORE_A_NOUN_ROOT,
    NOUN_PREFIXES_LONGEST_FIRST,
    NUMERAL_ROOTS,
    OF_BEFORE_A_VOWEL,
    OF_FORMS,
    POSSESSIVE_ENDINGS,
    SUBJECT_MARKERS,
    SUBJECT_WITH_PAST,
    TENSE_MARKERS_BEFORE_ROOT,
    TENSE_ONLY_AFTER,
    VERB_EXTENSIONS_LONGEST_FIRST,
    WORDS_LEFT_WHOLE,
)

SHORTEST_WORD_TO_CUT = 4
SHORTEST_JOINED_WORD = 13
SHORTEST_ROOT_BEFORE_AN_EXTENSION = 3
# A word is a run of letters. An apostrophe ends it, as in version 1, so the
# "ng" of ng'ombe is never cut.
WORD = re.compile(r"[^\W\d_]+")
ENDS_A_SENTENCE = re.compile(r"[.!?][\"')\]]*\s*$")
VOWELS = "aeiou"

Splitter = Callable[[str], list[str]]


def is_loanword(word: str) -> bool:
    """True for the listed loanwords, which are left whole (the same test as version 1)."""
    lower = word.lower()
    return any(loan in lower or lower in loan for loan in LOANWORDS)


def single_cut(word: str) -> list[str]:
    """The version 2.0 rule, unchanged: at most one cut in a word.

    The longest noun-class prefix if there is one, otherwise the longest verb extension at
    the end. Capital letters are ignored, so ``Abantu`` is cut the same way as ``abantu``.
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


def _verb_prefix_chains() -> list[tuple[str, ...]]:
    """Every allowed run of verb prefixes: [negative] subject [tense], longest first."""
    chains: set[tuple[str, ...]] = set()
    for negative in ("", NEGATIVE_BEFORE_SUBJECT):
        for subject in (*SUBJECT_MARKERS, *SUBJECT_WITH_PAST):
            tenses = ("",) if subject in SUBJECT_WITH_PAST else ("", *TENSE_MARKERS_BEFORE_ROOT)
            for tense in tenses:
                chains.add(tuple(piece for piece in (negative, subject, tense) if piece))
    for negative in NEGATIVE_WITH_PERSON:
        for tense in ("", *TENSE_MARKERS_BEFORE_ROOT):
            chains.add(tuple(piece for piece in (negative, tense) if piece))

    def allowed(chain: tuple[str, ...]) -> bool:
        return all(
            index > 0 and chain[index - 1] == TENSE_ONLY_AFTER[piece]
            for index, piece in enumerate(chain)
            if piece in TENSE_ONLY_AFTER
        )

    return sorted((c for c in chains if allowed(c)), key=lambda c: (-len("".join(c)), c))


VERB_PREFIX_CHAINS = _verb_prefix_chains()


def _is_a_number_or_an_of_form(lower: str) -> bool:
    """Counting words and "of", "my", "our" forms: closed classes that are never verbs."""
    if any(lower.endswith(root) and len(lower) - len(root) <= 3 for root in NUMERAL_ROOTS):
        return True
    if lower in OF_FORMS or (lower[0] in "aeo" and lower[1:] in OF_FORMS):
        return True
    return any(
        lower.startswith(form[:-1]) and lower[len(form) - 1 :] in POSSESSIVE_ENDINGS for form in OF_FORMS
    )


def _has_the_shape_of_a_class_9_or_5_noun(lower: str) -> bool:
    """e + nasal + consonant (ensi, embwa) or e + doubled consonant (ebbula, essira)."""
    if lower[0] != "e" or len(lower) <= 3:
        return False
    return (lower[1] in "nm" and lower[2] not in VOWELS) or lower[1] == lower[2]


def _root_parts(root: str) -> list[str]:
    """A root, cut before a passive, applied or causative ending when the shorter root is known."""
    known = lexicon.verb_roots()
    for extension in EXTENSIONS_CUT_FROM_A_KNOWN_ROOT:
        base = root[: -len(extension)]
        if (
            root.endswith(extension)
            and len(base) >= SHORTEST_ROOT_BEFORE_AN_EXTENSION
            and base + "a" in known
        ):
            return [base, extension]
    return [root]


@lru_cache(maxsize=65536)
def _verb_parts(lower: str) -> tuple[str, ...] | None:
    """[negative] subject [tense] root [extension], if the root is known. The longest root wins."""
    if _has_the_shape_of_a_class_9_or_5_noun(lower):
        return None
    known = lexicon.verb_roots()
    best: tuple[tuple[str, ...], str] | None = None
    for chain in VERB_PREFIX_CHAINS:
        prefix = "".join(chain)
        if lower.startswith(prefix):
            root = lower[len(prefix) :]
            if root in known and (best is None or len(root) > len(best[1])):
                best = (chain, root)
    return (*best[0], *_root_parts(best[1])) if best else None


@lru_cache(maxsize=65536)
def _joined_words(lower: str) -> tuple[int, int] | None:
    """Two common words written as one with "of" between them.

    ``abanoonyiboobubudamu`` is ``abanoonyi`` + ``bo`` + ``obubudamu``: "of" (b') before a
    vowel, with that vowel written long. Returns the lengths of the first word and of the
    joining piece.
    """
    common = lexicon.common_words()
    for first_length in range(5, len(lower) - 6):
        first, rest = lower[:first_length], lower[first_length:]
        if first not in common:
            continue
        for of in OF_BEFORE_A_VOWEL:
            if rest.startswith(of) and len(rest) > len(of) + 5:
                vowel, second = rest[len(of)], rest[len(of) + 1 :]
                if vowel in VOWELS and second[0] == vowel and second in common:
                    return first_length, len(of) + 1
    return None


def _as_written(word: str, lower_parts: tuple[str, ...] | list[str]) -> list[str]:
    """The parts with the letters of the word itself, so capitals are kept."""
    parts, position = [], 0
    for part in lower_parts:
        parts.append(word[position : position + len(part)])
        position += len(part)
    return parts


def _one_word(word: str) -> list[str]:
    lower = word.lower()
    if lower in WORDS_LEFT_WHOLE:
        return [word]
    before = single_cut(word)
    if len(word) < SHORTEST_WORD_TO_CUT or is_loanword(word) or _is_a_number_or_an_of_form(lower):
        return before
    if lower.startswith(("oku", "okw")):
        # "to ...": version 2.0 already cuts after oku-. Cut the root again if it carries an extension.
        if len(before) == 2 and before[1].lower() in lexicon.verb_roots():
            return _as_written(word, [before[0], *_root_parts(before[1].lower())])
        return before
    kept_as_a_noun = (
        len(before) == 2
        and len(before[0]) >= 3
        and before[0].lower() in NOUN_PREFIXES_BEFORE_A_NOUN_ROOT
        and before[1].lower() in lexicon.noun_roots()
    )
    if kept_as_a_noun:
        return before
    verb = _verb_parts(lower)
    return _as_written(word, verb) if verb else before


def split_word(word: str) -> list[str]:
    """The parts of one word, in order. Joined together they give the word back.

    >>> split_word("tebasobola")
    ['te', 'ba', 'sobola']
    >>> split_word("abantu")
    ['aba', 'ntu']
    """
    joined = _joined_words(word.lower()) if len(word) >= SHORTEST_JOINED_WORD else None
    if joined is None:
        return _one_word(word)
    first, joining = joined
    return [*_one_word(word[:first]), word[first : first + joining], *_one_word(word[first + joining :])]


def looks_like_a_name(word: str, starts_sentence: bool) -> bool:
    """Acronyms, and capitalised words in the middle of a sentence, are treated as names."""
    if len(word) > 1 and word.isupper():
        return True
    return word[0].isupper() and not starts_sentence


def cut(text: str, splitter: Splitter = split_word) -> list[str]:
    """Split a text into chunks at the grammar boundaries inside its words.

    ``"".join(cut(text)) == text`` always: nothing is added, removed or changed.
    Every chunk after the first starts in the middle of a word. Names (see
    ``looks_like_a_name``) are left whole. ``splitter=single_cut`` gives the version 2.0 cuts.

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
        for part in splitter(word)[:-1]:
            position += len(part)
            chunks.append(text[chunk_start:position])
            chunk_start = position
    chunks.append(text[chunk_start:])
    return chunks


def show_cuts(text: str, mark: str = "|", splitter: Splitter = split_word) -> str:
    """The text with a visible mark at every cut, for reading: ``Aba|ntu``."""
    return mark.join(cut(text, splitter))
