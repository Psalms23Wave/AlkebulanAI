# Copyright 2025-2026 Mathew Sekanjako and Psalms23Wave LLC
# SPDX-License-Identifier: Apache-2.0
"""Checks for ABLT."""

from __future__ import annotations

import pytest
from ablt import ABLT, cut, lexicon, show_cuts, single_cut, split_word


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
    assert show_cuts("Ya|genda e Kampala ne URA".replace("|", "")) == "Ya|genda e Kampala ne URA"


def test_a_word_after_a_full_stop_starts_a_sentence_and_is_cut():
    assert show_cuts("Yagenda. Abantu bajja.") == "Ya|genda. Aba|ntu ba|jja."


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
    assert [tokenizer.id_to_piece(i) for i in ids] == tokenizer.tokenize("Abantu basoma ebitabo.")
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


# ---- version 2.1: several cuts in a word, on evidence ----


@pytest.mark.parametrize(
    ("word", "parts"),
    [
        ("alisoma", ["a", "li", "soma"]),  # he or she + will + read
        ("tebasobola", ["te", "ba", "sobola"]),  # not + they + be able
        ("tetulisoma", ["te", "tu", "li", "soma"]),  # not + we + will + read
        ("sisoma", ["si", "soma"]),  # I do not + read
        ("yagamba", ["ya", "gamba"]),  # he or she (past) + say
        ("akola", ["a", "kola"]),
        ("agenda", ["a", "genda"]),
    ],
)
def test_a_verb_is_cut_into_subject_tense_and_root(word, parts):
    assert split_word(word) == parts


@pytest.mark.parametrize(
    ("word", "parts"),
    [
        ("okusomesa", ["oku", "som", "esa"]),  # to + read + make: to teach
        ("basomesa", ["ba", "som", "esa"]),
        ("tukolera", ["tu", "kol", "era"]),
        ("kikolebwa", ["ki", "kol", "ebwa"]),
    ],
)
def test_an_extension_is_cut_when_the_shorter_root_is_known(word, parts):
    assert split_word(word) == parts


def test_two_words_written_as_one_are_cut_at_the_join():
    assert split_word("Abanoonyiboobubudamu") == ["Aba", "noonyi", "bo", "obu", "budamu"]
    assert "".join(split_word("Abanoonyiboobubudamu")) == "Abanoonyiboobubudamu"


@pytest.mark.parametrize("word", ["abiri", "asatu", "ataano", "babiri", "ebiri", "bataano"])
def test_counting_words_are_not_read_as_verbs(word):
    assert split_word(word) == single_cut(word)


@pytest.mark.parametrize("word", ["kyange", "waffe", "baabwe", "ogwa", "lwa"])
def test_of_and_my_forms_are_not_read_as_verbs(word):
    assert split_word(word) == single_cut(word)


@pytest.mark.parametrize(
    "word",
    [
        "abantu",
        "omuntu",
        "ekitabo",
        "ebitabo",
        "amazzi",
        "enguudo",
        "ensalo",
        "ekyama",
        "abavubuka",
        "omusomesa",
    ],
)
def test_nouns_are_cut_as_in_version_2_0(word):
    assert split_word(word) == single_cut(word)


def test_a_verb_whose_root_is_not_in_the_list_is_cut_as_in_version_2_0():
    assert "qxzvqa" not in lexicon.verb_roots()
    assert split_word("baqxzvqa") == single_cut("baqxzvqa")


def test_the_conjunction_wabula_is_left_whole():
    assert split_word("wabula") == ["wabula"]
    assert split_word("Wabula") == ["Wabula"]


def test_single_cut_is_the_version_2_0_rule():
    assert single_cut("alisoma") == ["alisoma"]
    assert single_cut("abantu") == ["aba", "ntu"]
    assert single_cut("okusomesa") == ["oku", "somesa"]


@pytest.mark.parametrize(
    "word",
    [
        "Abantu",
        "TEBASOBOLA",
        "Okusomesa",
        "alisoma",
        "Abanoonyiboobubudamu",
        "wabula",
        "ŋŋenda",
        "abiri",
        "x",
        "",
    ],
)
def test_the_parts_always_spell_the_word(word):
    assert "".join(split_word(word)) == word
    assert "".join(single_cut(word)) == word


def test_the_lexicon_is_built_and_roots_are_seen_often_enough():
    roots = lexicon.verb_roots()
    assert {"soma", "kola", "genda", "sobola"} <= set(roots)
    assert min(roots.values()) >= 5
    assert "ntu" in lexicon.noun_roots()
    assert {"abanoonyi", "obubudamu"} <= lexicon.common_words()


def test_version_2_0_is_still_available_and_unchanged():
    old = ABLT(version="2.0")
    assert old.vocab_size == 6981
    assert old.tokenize("Tebasobola kusoma") == ["▁Teba", "sobola", "▁kuǀ", "▁soma"]
    assert old.show_cuts("alisoma okusomesa") == "alisoma oku|somesa"
    assert old.decode(old.encode("Abanoonyiboobubudamu bajja.")) == "Abanoonyiboobubudamu bajja."


def test_an_unknown_version_is_refused():
    with pytest.raises(ValueError):
        ABLT(version="9.9")


def test_version_2_1_gives_back_the_exact_text(tokenizer):
    text = "Abanoonyiboobubudamu tebasobola kusoma; naye alisoma enkya, ku ssaawa 3:00!"
    assert tokenizer.version == "2.1"
    assert tokenizer.decode(tokenizer.encode(text)) == text
    assert tokenizer.tokenize("alisoma") == ["▁aǀ", "▁liǀ", "▁soma"]
