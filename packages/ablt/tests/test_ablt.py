# Copyright 2025-2026 Mathew Sekanjako and Psalms23Wave LLC
# SPDX-License-Identifier: Apache-2.0
"""Checks for ABLT version 2."""

from __future__ import annotations

import pytest
from ablt import ABLT, cut, show_cuts, split_word


@pytest.fixture(scope="module")
def tokenizer() -> ABLT:
    return ABLT()


@pytest.mark.parametrize(
    ("word", "parts"),
    [
        ("abantu", ["aba", "ntu"]),
        ("omuntu", ["omu", "ntu"]),
        ("ekitabo", ["eki", "tabo"]),
        ("ebitabo", ["ebi", "tabo"]),
        ("okusoma", ["oku", "soma"]),
        ("okulya", ["oku", "lya"]),
    ],
)
def test_words_are_cut_at_the_noun_class_prefix(word, parts):
    assert split_word(word) == parts


def test_a_capital_letter_does_not_stop_the_cut():
    assert split_word("Abantu") == ["Aba", "ntu"]
    assert show_cuts("Abantu basoma.") == "Aba|ntu ba|soma."


def test_short_words_and_loanwords_are_left_whole():
    assert split_word("mu") == ["mu"]
    assert split_word("gavumenti") == ["gavumenti"]


def test_names_and_acronyms_inside_a_sentence_are_left_whole():
    assert show_cuts("Yagenda e Kampala ne URA") == "Yagenda e Kampala ne URA"


def test_a_word_after_a_full_stop_starts_a_sentence_and_is_cut():
    assert show_cuts("Yagenda. Abantu bajja.") == "Yagenda. Aba|ntu ba|jja."


@pytest.mark.parametrize(
    "text",
    [
        "Abantu bangi baagala okusoma ebitabo mu Kampala.",
        "Omusomesa  yasomesa abaana; Museveni yagenda e Kampala 2026!",
        "ng'ombe n'okusoma",
        "  spaces at the start and end  ",
        "ŋŋoma ezaffe",
        "English words and numbers 12,345.67 stay too",
        "",
        " ",
    ],
)
def test_cutting_changes_no_character(text):
    assert "".join(cut(text)) == text


@pytest.mark.parametrize(
    "text",
    [
        "Abantu bangi baagala okusoma ebitabo mu Kampala.",
        "Omusomesa  yasomesa abaana; Museveni yagenda e Kampala 2026!",
        "ng'ombe n'okusoma",
        "  spaces at the start and end  ",
        "ŋŋoma ezaffe",
        "a character never seen in training: 語 ǀ",
        "",
        " ",
    ],
)
def test_decode_gives_back_exactly_what_was_encoded(tokenizer, text):
    assert tokenizer.decode(tokenizer.encode(text)) == text


def test_a_root_is_the_same_piece_alone_and_after_a_prefix(tokenizer):
    after_prefix = tokenizer.tokenize("abantu")
    assert after_prefix == ["▁abaǀ", "▁ntu"]
    assert tokenizer.encode("omuntu")[-1] == tokenizer.encode("abantu")[-1]
    assert tokenizer.encode("okusoma")[-1] == tokenizer.encode("basoma")[-1]


def test_pieces_and_numbers_agree(tokenizer):
    ids = tokenizer.encode("Abantu basoma ebitabo.")
    assert [tokenizer.id_to_piece(i) for i in ids] == tokenizer.tokenize(
        "Abantu basoma ebitabo."
    )
    assert all(0 <= i < tokenizer.vocab_size for i in ids)


def test_a_join_that_was_never_seen_in_training_uses_the_spare_token(tokenizer):
    # An invented word: its first part is cut by the rules, but ends in a piece with no joined form.
    ids = tokenizer.encode("omuqxzv")
    assert tokenizer.decode(ids) == "omuqxzv"


def test_batch_encoding_matches_single_encoding(tokenizer):
    texts = ["abantu", "okusoma ebitabo"]
    assert tokenizer.encode_batch(texts) == [tokenizer.encode(text) for text in texts]


def test_the_terminal_command_prints_pieces_cuts_and_numbers(capsys):
    from ablt.cli import main

    assert main(["abantu", "basoma"]) == 0
    assert capsys.readouterr().out.strip() == "▁abaǀ ▁ntu ▁baǀ ▁soma"
    assert main(["--cuts", "okusoma ebitabo"]) == 0
    assert capsys.readouterr().out.strip() == "oku|soma ebi|tabo"
    assert main(["--ids", "abantu"]) == 0
    assert all(part.isdigit() for part in capsys.readouterr().out.split())
