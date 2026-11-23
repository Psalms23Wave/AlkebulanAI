# Copyright (c) 2025-2026 Mathew Sekanjako and Psalms23Wave LLC
# SPDX-License-Identifier: Apache-2.0
"""
ABLT — Alkebulan Bantu-Luganda Tokenizer (v1)
=============================================

A morphologically-aware subword tokenizer purpose-built for Luganda and other
Bantu languages. Combines a rule-based morphology pre-segmenter with a
SentencePiece Unigram model trained on a 108k-sentence Luganda corpus.

Author  : Mathew Sekanjako  (HF: Psalms23Wave)
Owner   : Psalms23Wave LLC  (https://www.psalms23wave.com)
License : Apache License 2.0  (see ../LICENSE and ../NOTICE)
Project : Alkebulan AI
Trademarks: "Alkebulan AI", "ABLT", "Sekan" — Psalms23Wave LLC.
            See ../TRADEMARK.md. Apache-2.0 does NOT grant trademark rights.

Quick use:

    from ablt_tokenizer import ABLT
    tok = ABLT.from_pretrained("tokenizer/")
    ids    = tok.encode("Abantu balina okuyiga oluganda.")
    pieces = tok.tokenize("Abantu balina okuyiga oluganda.")
    text   = tok.decode(ids)
"""

from __future__ import annotations

import os
import pickle
import re
from typing import Dict, List, Optional

try:
    import sentencepiece as spm
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "sentencepiece is required. Install with: pip install sentencepiece"
    ) from e


# ---------------------------------------------------------------------------
# Linguistic resource manager
# ---------------------------------------------------------------------------


class EnhancedLugandaTokenizer:
    """
    Rule-based morphological pre-segmenter for Luganda.

    Knows the full Luganda noun-class system, verb affixes, tense/negation
    markers, phonological compounds, and common loanwords. Used upstream of
    the SentencePiece model to expose morpheme boundaries.
    """

    def __init__(self) -> None:
        self.linguistic_features: Dict = {
            "noun_classes": {
                "class_1":  {"singular_prefixes": ["omu", "mu", "omw", "mw"],
                             "plural_prefixes":   ["aba", "ba", "ab", "b"]},
                "class_2":  {"singular_prefixes": ["omu", "mu", "omw", "mw"],
                             "plural_prefixes":   ["emi", "mi", "emy", "my"]},
                "class_3":  {"singular_prefixes": ["eri", "ri", "e", "li", "ery", "ly", "ama", "ma", "am"],
                             "plural_prefixes":   ["ama", "ma", "am", "ga", "ag"]},
                "class_4":  {"singular_prefixes": ["eki", "ki", "eky", "ky", "ech"],
                             "plural_prefixes":   ["ebi", "bi", "eby", "by"]},
                "class_5":  {"singular_prefixes": ["aka", "ka", "ak"],
                             "plural_prefixes":   ["obu", "bu", "obw", "bw"]},
                "class_6":  {"singular_prefixes": ["olu", "lu", "olw", "lw"],
                             "plural_prefixes":   ["en", "n", "enn", "em", "emm", "ez"]},
                "class_7":  {"singular_prefixes": ["ogu", "gu", "ogw", "gw"],
                             "plural_prefixes":   ["aga", "ga", "ag", "g"]},
                "class_8":  {"singular_prefixes": ["oku", "ku", "okw", "kw"],
                             "plural_prefixes":   ["ama", "ma", "am"]},
                "class_9":  {"singular_prefixes": ["otu", "tu", "otw", "tw"],
                             "plural_prefixes":   []},
                "class_10": {"singular_prefixes": ["e", "en", "em", "eny"],
                             "plural_prefixes":   ["e", "en", "em", "eny"]},
            },
            "verb_prefixes": [
                "n", "o", "a", "tu", "mu", "ba",
                "li", "ku", "na", "naa", "ki",
                "bi", "ga", "zi",
                "ya", "wa", "te", "si",
                "lu", "ka", "bu", "gu",
                "teba", "siba", "aba", "baa", "gaa", "yaa", "taa", "tee",
            ],
            "verb_extensions": [
                "wa", "ibwa", "iwa", "ebwa", "era", "ira", "esa", "eka",
                "iza", "eza", "ulwa", "uka", "ula", "isa",
                "eddwa", "iddwa", "izibwa", "erera", "irira", "isiza",
                "ikiriza", "ukiriza", "ulula", "agana", "aŋŋa", "isana",
                "dde", "awo", "anga", "idira", "ingira", "zalira",
                "nga", "aganya",
            ],
            "negation_prefixes": ["te", "t", "si", "s", "tee", "ta"],
            "tense_markers": {
                "past":    ["a", "dde", "zze", "ye"],
                "present": ["a", "e", "o"],
                "future":  ["naa", "li", "jja"],
                "ongoing": ["kyaa", "nga"],
            },
            "semi_vowel_compounds": [
                "pw", "bw", "tw", "dw", "cw", "jw", "kw", "gw", "sw", "zw",
                "mw", "nw", "nyw", "ŋw", "lw", "rw",
                "py", "by", "ty", "dy", "ky", "gy", "my", "ny", "ly", "ry",
            ],
            "nasal_compounds": [
                "mp", "mb", "nt", "nd", "nc", "nj", "nk", "ng",
                "nf", "nv", "ns", "nz",
            ],
            "geminates": [
                "mm", "nn", "jj", "pp", "tt", "kk", "bb", "dd", "gg",
                "ff", "ss", "zz",
            ],
            "loanwords": [
                "gavumenti", "poliisi", "sikaala", "disitulikiti", "pulayimale",
                "paalamenti", "pulojekiti", "bbayibuli", "kompyuta", "kalenda",
            ],
        }

        self.phonological_rules = {
            "vowel_lengthening":       True,
            "consonant_gemination":    True,
            "vowel_harmony":           True,
            "vowel_hiatus_resolution": True,
            "tone_patterns":           ["level", "falling"],
        }

    @staticmethod
    def is_vowel(ch: str) -> bool:
        return ch.lower() in "aeiouāēīōū"

    def is_loanword(self, word: str) -> bool:
        lw = word.lower()
        return any(x in lw or lw in x for x in self.linguistic_features["loanwords"])

    def adaptive_morphological_segmentation(self, word: str) -> str:
        """Insert a mid-dot ('·') at likely morpheme boundaries."""
        if len(word) <= 3 or self.is_loanword(word):
            return word

        for prefix in sorted(
            {p for cls in self.linguistic_features["noun_classes"].values()
             for pt in ("singular_prefixes", "plural_prefixes") for p in cls[pt]},
            key=len, reverse=True,
        ):
            if word.startswith(prefix) and len(word) > len(prefix) + 1:
                return f"{prefix}·{word[len(prefix):]}"

        for suffix in sorted(self.linguistic_features["verb_extensions"],
                             key=len, reverse=True):
            if word.endswith(suffix) and len(word) > len(suffix) + 1:
                return f"{word[:-len(suffix)]}·{suffix}"

        return word

    def tokenize(self, text: str) -> str:
        text = re.sub(r"([.,!?;:'])", r" \1 ", text)
        out = []
        for w in text.split():
            if w in ".,!?;:'":
                out.append(w)
            else:
                out.append(self.adaptive_morphological_segmentation(w))
        return " ".join(out)


# ---------------------------------------------------------------------------
# ABLT — Public tokenizer class
# ---------------------------------------------------------------------------


class ABLT:
    """
    Alkebulan Bantu-Luganda Tokenizer.

    Pipeline:  raw text  ->  morphological segmenter  ->  SentencePiece Unigram
    """

    DEFAULT_SPM = "luganda_spm.model"
    DEFAULT_PICKLE = "ablt_v1_tokenizer.pkl"

    SPECIAL_TOKENS = {
        "unk": "<unk>",
        "bos": "<s>",
        "eos": "</s>",
    }

    def __init__(self, sp_model_path: str):
        if not os.path.exists(sp_model_path):
            raise FileNotFoundError(f"SentencePiece model not found at: {sp_model_path}")
        self.sp = spm.SentencePieceProcessor()
        self.sp.load(sp_model_path)
        self.morph = EnhancedLugandaTokenizer()

    # ---- factory constructors --------------------------------------------

    @classmethod
    def from_pretrained(cls, path: str) -> "ABLT":
        """
        Load ABLT from a directory containing `luganda_spm.model`
        (and optionally `ablt_v1_tokenizer.pkl`).
        """
        if os.path.isdir(path):
            model_path = os.path.join(path, cls.DEFAULT_SPM)
        else:
            model_path = path
        return cls(model_path)

    @classmethod
    def from_pickle(cls, pickle_path: str) -> "ABLT":
        with open(pickle_path, "rb") as f:
            data = pickle.load(f)
        base = os.path.dirname(os.path.abspath(pickle_path)) or "."
        spm_path = data.get("model_path", cls.DEFAULT_SPM)
        if not os.path.isabs(spm_path):
            spm_path = os.path.join(base, spm_path)
        return cls(spm_path)

    @classmethod
    def load(cls, path: str) -> "ABLT":
        """
        Convenience loader matching the notebook API.

        Accepts either a pickle path (``ablt_tokenizer.pkl``) or a directory
        containing ``luganda_spm.model``.
        """
        if os.path.isdir(path):
            return cls.from_pretrained(path)
        if path.endswith(".pkl"):
            return cls.from_pickle(path)
        return cls(path)

    # ---- core API --------------------------------------------------------

    @property
    def vocab_size(self) -> int:
        return self.sp.get_piece_size()

    def _preprocess(self, text: str) -> str:
        return self.morph.tokenize(text).replace("·", " ")

    def tokenize(self, text: str) -> List[str]:
        """Return subword pieces (with SentencePiece '▁' word-start marker)."""
        return self.sp.encode_as_pieces(self._preprocess(text))

    def tokenize_text(self, text: str) -> List[str]:
        """Alias for :meth:`tokenize` — matches the notebook API."""
        return self.tokenize(text)

    def encode(self, text: str, add_special_tokens: bool = False) -> List[int]:
        """Return token ids."""
        ids = self.sp.encode(self._preprocess(text), out_type=int)
        if add_special_tokens:
            ids = [self.sp.bos_id()] + ids + [self.sp.eos_id()]
        return ids

    def decode(self, ids: List[int]) -> str:
        clean = [i for i in ids if 0 <= i < self.vocab_size]
        return self.sp.decode(clean)

    def get_tokens_with_importance(self, text: str) -> List[tuple]:
        """
        Return a list of (piece, importance_score) pairs.

        Pieces that match a known morphological prefix or suffix receive
        a boosted importance weight. Useful for attention-weighting or
        downstream analysis.
        """
        pieces = self.tokenize(text)
        known_affixes = set()
        for cls in self.morph.linguistic_features["noun_classes"].values():
            known_affixes.update(cls["singular_prefixes"])
            known_affixes.update(cls["plural_prefixes"])
        known_affixes.update(self.morph.linguistic_features["verb_extensions"])
        known_affixes.update(self.morph.linguistic_features["verb_prefixes"])
        weights = []
        for p in pieces:
            clean = p.lstrip("▁")
            if clean in known_affixes:
                weights.append((p, 2.0))
            elif len(clean) >= 3:
                weights.append((p, 0.5))
            else:
                weights.append((p, 0.2 if clean in ".,!?;:'" else 0.5))
        return weights

    def __repr__(self) -> str:
        return f"ABLT(vocab_size={self.vocab_size}, morpheme_aware=True)"


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------


def _demo() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    tok = ABLT.from_pretrained(here)
    samples = [
        "Abantu balina okuyiga oluganda.",
        "Abanoonyiboobubudamu bonna baasabiddwa beewandiise ewa ssentebe.",
        "Abalimi baatendekeddwa okukola emirimu egy'obutale.",
        "ekinaataagulwataagulwanga",
        "Webale nnyo ssebo.",
    ]
    print(f"Loaded: {tok}")
    for s in samples:
        pieces = tok.tokenize(s)
        ids = tok.encode(s)
        print(f"\nInput : {s}")
        print(f"Pieces: {pieces}")
        print(f"IDs   : {ids}")
        print(f"Count : {len(pieces)}")


if __name__ == "__main__":
    _demo()
