# Copyright 2025-2026 Mathew Sekanjako and Psalms23Wave LLC
# SPDX-License-Identifier: Apache-2.0
"""Train the SentencePiece model that ships inside the package.

Run from the repository root:

    python packages/ablt/tools/train_model.py

It reads ``data/MergedTok.txt``, holds back one line in ten for testing (the
same split as the test of 2026-11-21), cuts the rest by grammar, and trains.
A plain model with no grammar is trained beside it, as a check to compare with.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import sentencepiece as spm

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parents[1]
sys.path.insert(0, str(PACKAGE_ROOT / "src"))
from ablt.segmenter import cut  # noqa: E402

CORPUS = REPO_ROOT / "data" / "MergedTok.txt"
WORK_DIR = PACKAGE_ROOT / "tools" / "work"
BUNDLED_MODEL = PACKAGE_ROOT / "src" / "ablt" / "models" / "ablt-luganda-v2.model"
BUNDLED_JOINERS = BUNDLED_MODEL.with_suffix(".joiners.json")
VOCAB_SIZE = 6000
SPLIT_SEED = 42


def split_corpus() -> tuple[list[str], list[str]]:
    """Training lines and held-out lines: unique lines, shuffled, one in ten held back."""
    text = CORPUS.read_text(encoding="utf-8", errors="replace")
    lines = sorted({line.strip() for line in text.splitlines() if line.strip()})
    random.Random(SPLIT_SEED).shuffle(lines)
    held_out_size = len(lines) // 10
    return lines[held_out_size:], lines[:held_out_size]


def train(lines: list[str], prefix: Path) -> None:
    text_file = prefix.with_suffix(".txt")
    text_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    spm.SentencePieceTrainer.train(
        input=str(text_file),
        model_prefix=str(prefix),
        vocab_size=VOCAB_SIZE,
        model_type="unigram",
        character_coverage=1.0,  # keep every character that appears, including digits
        byte_fallback=True,  # any character never seen is kept as bytes, so nothing is lost
        normalization_rule_name="identity",  # do not rewrite the text
        remove_extra_whitespaces=False,  # keep every space
        max_sentencepiece_length=16,
        split_digits=False,
        input_sentence_size=0,
        shuffle_input_sentence=False,
        minloglevel=2,
        hard_vocab_limit=False,
    )


def joining_pieces(training_lines: list[str], model: Path) -> list[str]:
    """Every piece that ends a chunk just before a cut, anywhere in the training text."""
    processor = spm.SentencePieceProcessor(model_file=str(model))
    seen: set[str] = set()
    for line in training_lines:
        chunks = cut(line)
        for pieces in processor.encode(chunks[:-1], out_type=str):
            if pieces:
                seen.add(pieces[-1])
    return sorted(seen)


def main() -> None:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    training_lines, held_out_lines = split_corpus()
    (WORK_DIR / "held_out.txt").write_text(
        "\n".join(held_out_lines) + "\n", encoding="utf-8"
    )
    # A space at each grammar cut keeps SentencePiece from joining pieces across it.
    train([" ".join(cut(line)) for line in training_lines], WORK_DIR / "grammar_first")
    train(training_lines, WORK_DIR / "plain_check")
    BUNDLED_MODEL.parent.mkdir(parents=True, exist_ok=True)
    BUNDLED_MODEL.write_bytes((WORK_DIR / "grammar_first.model").read_bytes())
    joiners = joining_pieces(training_lines, BUNDLED_MODEL)
    BUNDLED_JOINERS.write_text(
        json.dumps(joiners, ensure_ascii=False, indent=0) + "\n", encoding="utf-8"
    )
    print(f"{len(joiners)} pieces have a joined form")
    print(f"trained on {len(training_lines)} lines, held back {len(held_out_lines)}")
    print(f"model written to {BUNDLED_MODEL.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
