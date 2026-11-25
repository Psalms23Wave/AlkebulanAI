# Copyright 2025-2026 Mathew Sekanjako and Psalms23Wave LLC
# SPDX-License-Identifier: Apache-2.0
"""Score the packaged tokenizer and print the numbers quoted in the README.

Run from the repository root, after ``train_model.py``:

    python packages/ablt/tools/evaluate.py

It measures three things: whether cuts fall on grammar boundaries (the answer
key in ``tests/data``), how many pieces a word becomes on real text
(MasakhaNER Luganda, if it has been downloaded for the tokenizer tax test),
and whether decoding gives back exactly the text that was encoded.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path
from statistics import mean

import sentencepiece as spm

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parents[1]
sys.path.insert(0, str(PACKAGE_ROOT / "src"))
from ablt import ABLT  # noqa: E402

GOLD_FILE = PACKAGE_ROOT / "tests" / "data" / "gold_luganda_morphemes.txt"
WORK_DIR = PACKAGE_ROOT / "tools" / "work"
MASAKHANER = REPO_ROOT / "experiments" / "tokenizer_tax" / "data"
MASAKHANER_FILES = (
    "masakhaner2_lug_train.txt",
    "masakhaner2_lug_dev.txt",
    "masakhaner2_lug_test.txt",
)
RESULTS_FILE = PACKAGE_ROOT / "tools" / "evaluation_results.json"

Pieces = Callable[[str], list[str]]


def read_gold() -> list[tuple[str, set[int], set[int]]]:
    """Each word with the cut positions that are required and those that are optional."""
    entries = []
    for line in GOLD_FILE.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            continue
        for item in line.split():
            word, required, optional = "", set(), set()
            for character in item:
                if character == "|":
                    required.add(len(word))
                elif character == "~":
                    optional.add(len(word))
                else:
                    word += character
            entries.append((word, required, optional))
    return entries


def cut_positions(pieces: list[str], word: str) -> set[int] | None:
    """Where the pieces divide the word, or None if they do not spell the word."""
    positions, length = set(), 0
    for piece in pieces:
        text = ABLT.piece_text(piece)
        if not text:
            continue
        if length:
            positions.add(length)
        length += len(text)
    return positions if length == len(word) else None


def boundary_scores(pieces_for: Pieces, capitalise: bool = False) -> dict:
    found = needed = proposed = correct = perfect = unusable = 0
    gold = read_gold()
    for word, required, optional in gold:
        shown = word.capitalize() if capitalise else word
        positions = cut_positions(pieces_for(shown), word)
        needed += len(required)
        if positions is None:
            unusable += 1
            continue
        found += len(positions & required)
        proposed += len(positions - optional)
        correct += len((positions - optional) & required)
        perfect += required <= positions and not (positions - required - optional)
    recall = found / needed
    precision = correct / proposed if proposed else 0.0
    f1 = 2 * recall * precision / (recall + precision) if recall + precision else 0.0
    return {
        "f1_percent": round(100 * f1, 1),
        "recall_percent": round(100 * recall, 1),
        "precision_percent": round(100 * precision, 1),
        "words_fully_correct_percent": round(100 * perfect / len(gold), 1),
        "words": len(gold),
        "unusable": unusable,
    }


def read_conll(files: tuple[str, ...]) -> list[str]:
    sentences, words = [], []
    for name in files:
        for line in (MASAKHANER / name).read_text(encoding="utf-8").splitlines():
            if line.strip():
                words.append(line.split()[0])
            elif words:
                sentences.append(" ".join(words))
                words = []
        if words:
            sentences.append(" ".join(words))
            words = []
    return sentences


def pieces_per_word(pieces_for: Pieces, sentences: list[str]) -> float:
    return round(mean(len(pieces_for(s)) / len(s.split()) for s in sentences if s.split()), 3)


def main() -> None:
    tokenizer = ABLT()
    earlier = ABLT(version="2.0")
    plain = spm.SentencePieceProcessor(model_file=str(WORK_DIR / "plain_check.model"))
    systems: dict[str, Pieces] = {
        f"ABLT version {tokenizer.version}": tokenizer.tokenize,
        f"ABLT version {earlier.version}": earlier.tokenize,
        "plain SentencePiece, same text and size (check)": lambda text: plain.encode(text, out_type=str),
    }
    results: dict = {
        "vocab_size": tokenizer.vocab_size,
        "base_size": tokenizer.base_size,
        "systems": {},
    }

    held_out = (WORK_DIR / "held_out.txt").read_text(encoding="utf-8").splitlines()
    texts = {"held-out lines": held_out}
    if all((MASAKHANER / name).exists() for name in MASAKHANER_FILES):
        texts["MasakhaNER 2.0 Luganda"] = read_conll(MASAKHANER_FILES)

    for name, pieces_for in systems.items():
        row = {
            "cuts_on_grammar_boundaries": boundary_scores(pieces_for),
            "same_with_a_capital_letter": boundary_scores(pieces_for, capitalise=True),
            "pieces_per_word": {label: pieces_per_word(pieces_for, lines) for label, lines in texts.items()},
        }
        results["systems"][name] = row
        print(f"\n{name}")
        print(f"  cuts on grammar boundaries (F1): {row['cuts_on_grammar_boundaries']['f1_percent']}%")
        print(f"  the same words with a capital:   {row['same_with_a_capital_letter']['f1_percent']}%")
        fully_correct = row["cuts_on_grammar_boundaries"]["words_fully_correct_percent"]
        print(f"  words cut fully correctly:       {fully_correct}%")
        for label, value in row["pieces_per_word"].items():
            print(f"  pieces per word, {label}: {value}")

    exact = {}
    for version in (tokenizer, earlier):
        for label, lines in texts.items():
            same = sum(version.decode(version.encode(line)) == line for line in lines)
            exact[f"{version.version}, {label}"] = {"exact": same, "of": len(lines)}
            print(
                f"\ndecode gives back the exact text, version {version.version}, {label}: "
                f"{same} of {len(lines)}"
            )
    results["exact_round_trip"] = exact
    RESULTS_FILE.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
