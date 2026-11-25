# Copyright 2025-2026 Mathew Sekanjako and Psalms23Wave LLC
# SPDX-License-Identifier: Apache-2.0
"""Check the cutting rules against data they were not written from.

Run from the repository root:

    python packages/ablt/tools/evaluate_rules.py

Three checks compare version 2.1 (``split_word``) with version 2.0 (``single_cut``):

1. The 83-word answer list: which words are cut fully right, and whether any word that was
   right in 2.0 is now wrong.
2. UniMorph Luganda (verb forms with their lemma): is there a cut exactly where the root
   begins, and is the root left whole? The verbs are split in two halves by a fixed seed;
   the rules were tuned on the first half and are reported on the second.
3. MasakhaPOS Luganda (words tagged noun, verb, number ...): the new rules are for verbs, so
   words with other tags should be cut as before. Tuned on train and dev, reported on test.

Neither set is part of the package. Download them first:

    experiments/tokenizer_tax/data/unimorph/lug
        https://raw.githubusercontent.com/unimorph/lug/master/lug          (CC BY-SA 3.0)
    experiments/tokenizer_tax/data/masakhapos/lug_{train,dev,test}.txt
        https://github.com/masakhane-io/masakhane-pos/tree/main/data/lug
"""

from __future__ import annotations

import json
import random
import sys
from collections import Counter
from collections.abc import Callable
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parents[1]
sys.path.insert(0, str(PACKAGE_ROOT / "src"))
from ablt import single_cut, split_word  # noqa: E402

GOLD_FILE = PACKAGE_ROOT / "tests" / "data" / "gold_luganda_morphemes.txt"
DATA = REPO_ROOT / "experiments" / "tokenizer_tax" / "data"
UNIMORPH = DATA / "unimorph" / "lug"
MASAKHAPOS = DATA / "masakhapos"
RESULTS_FILE = PACKAGE_ROOT / "tools" / "rules_evaluation_results.json"
VERB_HALVES_SEED = 0
KINDS = {"VERB": "verbs", "AUX": "verbs", "NOUN": "nouns", "NUM": "numbers"}

Splitter = Callable[[str], list[str]]
VERSIONS: dict[str, Splitter] = {"2.0": single_cut, "2.1": split_word}


def cut_positions(parts: list[str]) -> set[int]:
    positions, length = set(), 0
    for part in parts[:-1]:
        length += len(part)
        positions.add(length)
    return positions


def answer_list() -> dict:
    words_right: dict[str, set[str]] = {version: set() for version in VERSIONS}
    total = 0
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
            total += 1
            for version, splitter in VERSIONS.items():
                cuts = cut_positions(splitter(word))
                if required <= cuts and not (cuts - required - optional):
                    words_right[version].add(item)
    return {
        "words": total,
        "fully_right": {version: len(items) for version, items in words_right.items()},
        "right_in_2.0_wrong_in_2.1": sorted(words_right["2.0"] - words_right["2.1"]),
        "still_wrong_in_2.1": sorted(
            item
            for line in GOLD_FILE.read_text(encoding="utf-8").splitlines()
            if not line.startswith("#")
            for item in line.split()
            if item not in words_right["2.1"]
        ),
    }


def verb_forms() -> dict:
    rows = [
        line.split("\t")
        for line in UNIMORPH.read_text(encoding="utf-8").splitlines()
        if line.count("\t") == 2
    ]
    lemmas = sorted({lemma for lemma, _, _ in rows})
    random.Random(VERB_HALVES_SEED).shuffle(lemmas)
    halves = {"tuned_on": set(lemmas[: len(lemmas) // 2]), "reported_on": set(lemmas[len(lemmas) // 2 :])}
    result = {}
    for name, half in halves.items():
        # Forms that end in the lemma itself, so the place where the root begins is known.
        forms = [
            (lemma, form)
            for lemma, form, _ in rows
            if lemma in half and form != lemma and form.endswith(lemma) and len(form) >= 4
        ]
        scores = {}
        for version, splitter in VERSIONS.items():
            found = inside = 0
            for lemma, form in forms:
                cuts, root_start = cut_positions(splitter(form)), len(form) - len(lemma)
                found += root_start in cuts
                inside += any(position > root_start for position in cuts)
            scores[version] = {
                "root_boundary_found_percent": round(100 * found / len(forms), 1),
                "cut_inside_the_lemma_percent": round(100 * inside / len(forms), 1),
            }
        result[name] = {"verbs": len(half), "forms": len(forms), **scores}
    return result


def tagged_words(files: tuple[str, ...]) -> list[tuple[str, str]]:
    words = []
    for name in files:
        for line in (MASAKHAPOS / f"lug_{name}.txt").read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[0].isalpha() and len(parts[0]) >= 4 and parts[1] != "PROPN":
                words.append((parts[0], parts[1]))
    return words


def words_changed() -> dict:
    result = {}
    for name, files in (("tuned_on", ("train", "dev")), ("reported_on", ("test",))):
        total: Counter[str] = Counter()
        changed: Counter[str] = Counter()
        examples: dict[str, set[str]] = {}
        for word, tag in tagged_words(files):
            kind = KINDS.get(tag, "other words")
            total[kind] += 1
            before, after = single_cut(word), split_word(word)
            if before != after:
                changed[kind] += 1
                examples.setdefault(kind, set()).add(f"{word}: {'|'.join(before)} -> {'|'.join(after)}")
        result[name] = {
            kind: {
                "words": total[kind],
                "cut_differently_from_2.0": changed[kind],
                "percent": round(100 * changed[kind] / total[kind], 1),
                "which": sorted(examples.get(kind, ()))[:40] if kind != "verbs" else [],
            }
            for kind in ("verbs", "nouns", "numbers", "other words")
        }
    return result


def main() -> None:
    results = {"answer_list": answer_list()}
    if UNIMORPH.exists():
        results["verb_forms_unimorph"] = verb_forms()
    if (MASAKHAPOS / "lug_test.txt").exists():
        results["tagged_words_masakhapos"] = words_changed()
    RESULTS_FILE.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    gold = results["answer_list"]
    print(f"answer list: {gold['fully_right']} of {gold['words']} words fully right")
    print(f"  right in 2.0 but wrong in 2.1: {gold['right_in_2.0_wrong_in_2.1'] or 'none'}")
    for name, half in results.get("verb_forms_unimorph", {}).items():
        print(f"verb forms, {name} ({half['forms']} forms of {half['verbs']} verbs):")
        for version in VERSIONS:
            print(f"  {version}: {half[version]}")
    for name, kinds in results.get("tagged_words_masakhapos", {}).items():
        print(f"tagged words, {name}:")
        for kind, row in kinds.items():
            print(
                f"  {kind}: {row['cut_differently_from_2.0']} of {row['words']} "
                f"cut differently ({row['percent']}%)"
            )
    print(f"written to {RESULTS_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
