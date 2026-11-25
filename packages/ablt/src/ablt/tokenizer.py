# Copyright 2025-2026 Mathew Sekanjako and Psalms23Wave LLC
# SPDX-License-Identifier: Apache-2.0
"""ABLT: the Alkebulan Bantu-Luganda Tokenizer."""

from __future__ import annotations

import json
from importlib import resources
from pathlib import Path

import sentencepiece as spm

from .segmenter import Splitter, cut, show_cuts, single_cut, split_word

LATEST = "2.1"
# Each version is a set of cutting rules and the model trained on text cut by those rules.
BUNDLED: dict[str, tuple[str, Splitter]] = {
    "2.1": ("ablt-luganda-v2.1", split_word),  # several cuts in a word
    "2.0": ("ablt-luganda-v2", single_cut),  # one cut in a word
}
WORD_START = "▁"
JOIN_MARK = "ǀ"
JOIN_TOKEN = "<join>"


class ABLT:
    """A Luganda tokenizer that cuts words by grammar first, then by statistics.

    >>> tokenizer = ABLT()
    >>> tokenizer.tokenize("abantu basoma ebitabo")
    ['▁abaǀ', '▁ntu', '▁baǀ', '▁soma', '▁ebiǀ', '▁tabo']
    >>> tokenizer.decode(tokenizer.encode("Abantu basoma ebitabo."))
    'Abantu basoma ebitabo.'

    ``ABLT(version="2.0")`` gives the earlier rules (one cut in a word) and their model,
    so results made with version 2.0 can be repeated.

    A piece that ends with ``ǀ`` is joined to the piece after it: ``▁abaǀ`` then
    ``▁ntu`` is the one word ``abantu``. Roots such as ``▁ntu`` and ``▁soma`` are
    the same piece whether they stand alone or follow a prefix.

    Piece numbers: ``0 .. base_size - 1`` are the SentencePiece pieces, the next
    block are the same pieces in their joined form, and the last number is a
    spare join token used only when a joined form was never seen in training.
    """

    def __init__(
        self,
        model_path: str | Path | None = None,
        joiners_path: str | Path | None = None,
        version: str = LATEST,
    ) -> None:
        if version not in BUNDLED:
            raise ValueError(f"unknown version {version!r}; choose from {sorted(BUNDLED)}")
        self.version = version
        name, self._splitter = BUNDLED[version]
        if model_path is None:
            package = resources.files("ablt") / "models"
            with resources.as_file(package / f"{name}.model") as bundled:
                self._processor = spm.SentencePieceProcessor(model_file=str(bundled))
            joiners = json.loads((package / f"{name}.joiners.json").read_text(encoding="utf-8"))
        else:
            self._processor = spm.SentencePieceProcessor(model_file=str(model_path))
            joiners_file = (
                Path(joiners_path) if joiners_path else Path(model_path).with_suffix(".joiners.json")
            )
            joiners = json.loads(joiners_file.read_text(encoding="utf-8"))
        self.base_size = self._processor.get_piece_size()
        self._joiner_base_ids = [self._processor.piece_to_id(piece) for piece in joiners]
        self._joined_id = {base: self.base_size + i for i, base in enumerate(self._joiner_base_ids)}
        self.join_token_id = self.base_size + len(self._joiner_base_ids)

    @property
    def vocab_size(self) -> int:
        return self.join_token_id + 1

    def __len__(self) -> int:
        return self.vocab_size

    def morphemes(self, word: str) -> list[str]:
        """The grammar parts of one word, for example ``['oku', 'soma']``."""
        return self._splitter(word)

    def show_cuts(self, text: str) -> str:
        """The text with ``|`` at every grammar cut, for reading."""
        return show_cuts(text, splitter=self._splitter)

    def encode(self, text: str) -> list[int]:
        """Piece numbers for a text. ``decode`` gives the exact text back."""
        chunks = cut(text, self._splitter)
        ids: list[int] = []
        for index, chunk_ids in enumerate(self._processor.encode(chunks, out_type=int)):
            if index < len(chunks) - 1 and chunk_ids:
                joined = self._joined_id.get(chunk_ids[-1])
                never_seen = joined is None
                chunk_ids = [*chunk_ids, self.join_token_id] if never_seen else [*chunk_ids[:-1], joined]
            elif index < len(chunks) - 1:
                chunk_ids = [self.join_token_id]
            ids.extend(chunk_ids)
        return ids

    def encode_batch(self, texts: list[str]) -> list[list[int]]:
        return [self.encode(text) for text in texts]

    def decode(self, ids: list[int]) -> str:
        """The original text, from piece numbers."""
        text, segment = [], []
        for index in ids:
            if index < self.base_size:
                segment.append(index)
                continue
            if index != self.join_token_id:
                segment.append(self._joiner_base_ids[index - self.base_size])
            text.append(self._processor.decode(segment))
            segment = []
        text.append(self._processor.decode(segment))
        return "".join(text)

    def id_to_piece(self, index: int) -> str:
        if index < self.base_size:
            return self._processor.id_to_piece(index)
        if index == self.join_token_id:
            return JOIN_TOKEN
        return self._processor.id_to_piece(self._joiner_base_ids[index - self.base_size]) + JOIN_MARK

    def tokenize(self, text: str) -> list[str]:
        """The pieces the model will see, as text."""
        return [self.id_to_piece(index) for index in self.encode(text)]

    @staticmethod
    def piece_text(piece: str) -> str:
        """A piece without its word-start and join marks."""
        return piece.replace(WORD_START, "").replace(JOIN_MARK, "")

    def __repr__(self) -> str:
        return f"ABLT(version={self.version!r}, vocab_size={self.vocab_size}, base_size={self.base_size})"
