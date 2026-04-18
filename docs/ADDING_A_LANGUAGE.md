# Adding a New African Language to Alkebulan AI

This is the **headline contribution path** for the project. If you
ship a working rule pack for a new African language, you
single-handedly unlock modern NLP for every speaker of that
language. This document tells you exactly how.

**Estimated effort:** 2–6 weeks for a fluent speaker with basic
Python; 1–3 months for a non-speaker working with a reference
grammar and native-speaker consultant.

---

## Table of contents

1. [What "adding a language" means here](#what-adding-a-language-means-here)
2. [Prerequisites](#prerequisites)
3. [Step 1 — File layout](#step-1--file-layout)
4. [Step 2 — Write the rule pack](#step-2--write-the-rule-pack)
5. [Step 3 — Assemble a training corpus](#step-3--assemble-a-training-corpus)
6. [Step 4 — Train the SentencePiece model](#step-4--train-the-sentencepiece-model)
7. [Step 5 — Write the validation notebook](#step-5--write-the-validation-notebook)
8. [Step 6 — Quality gates](#step-6--quality-gates)
9. [Step 7 — Submit](#step-7--submit)
10. [Template: minimal language rule pack](#template-minimal-language-rule-pack)

---

## What "adding a language" means here

Because the ABLT architecture factors cleanly into
**(a) language-specific symbolic rules** and
**(b) a universal statistical sub-word layer** and
**(c) a language-agnostic optimization layer (Sekan)**,
adding a new language is overwhelmingly a matter of writing
(a). You are **not** training a new neural network. You are
**not** redesigning the tokenizer algorithm. You are describing
your language's morphology cleanly enough that the existing
pipeline can do its job.

Concretely, for each new language you produce:

1. A **rule pack** (Python file) describing the language's
   morphology: noun classes, verb affixes, phonology, loanwords.
2. A **training corpus** of 50k–200k sentences of monolingual
   text.
3. A **SentencePiece model** trained on that corpus after
   pre-segmentation.
4. A **validation notebook** reproducing the three headline
   metrics.

That is it.

---

## Prerequisites

Required:

- Python 3.9+.
- Ability to read the existing Luganda rule pack in
  [`tokenizer/ablt_tokenizer.py → EnhancedLugandaTokenizer`](../tokenizer/ablt_tokenizer.py).
- Ability to consult (or be) a native speaker of the target
  language for validation.
- At least one reference grammar or published morphological
  description of the target language.

Strongly recommended:

- A small parallel corpus (English ↔ target) for sanity-checking
  tokenization output.
- Access to Google Colab (free tier is enough) or any machine
  with 16 GB RAM for SentencePiece training.

---

## Step 1 — File layout

Create these files (replace `xx` with the ISO 639 code of your
language — `sw` for Swahili, `rw` for Kinyarwanda, `am` for
Amharic, `yo` for Yoruba, etc.):

```
tokenizer/
  languages/
    __init__.py
    xx.py                          ← YOUR RULE PACK
  models/
    xx_spm.model                   ← trained SentencePiece (Step 4)
    xx_spm.vocab

data/
  xx/
    corpus.txt                     ← training text (Step 3)
    LICENSE.md                     ← upstream licenses / sources

notebooks/
  xx/
    train_xx_tokenizer.ipynb       ← reproduces Step 4
    validate_xx_tokenizer.ipynb    ← reproduces Step 5
```

The existing Luganda artefacts already live in
`tokenizer/luganda_spm.model` and `tokenizer/ablt_v1_tokenizer.pkl`
at the top level; new languages go under the `languages/` and
`models/` sub-directories.

---

## Step 2 — Write the rule pack

Open [`tokenizer/ablt_tokenizer.py`](../tokenizer/ablt_tokenizer.py)
and study the `EnhancedLugandaTokenizer` class. Your job is to
write an analogous class for your language.

### 2.1 Required linguistic knowledge

Have the following ready before you start typing:

| Field | What you need |
|---|---|
| **Noun class system** | Every prefix for every class, singular and plural (for Bantu languages; other families may call this "gender" or "class" differently) |
| **Verb prefixes** | Subject markers (I, you, he, we…), object markers, relativiser |
| **Verb extensions / suffixes** | Applicative, causative, passive, reciprocal, stative, perfective, habitual, negative |
| **Tense/aspect markers** | Past, present, future, ongoing; any tonal distinctions |
| **Negation** | Prefix and suffix patterns |
| **Phonological compounds** | Nasal-consonant, semi-vowel, and any language-specific diphthongs |
| **Geminates** | Doubled consonants that are phonemic |
| **Loanwords** | Common borrowed nouns (often from English, Arabic, or a colonial language), recognised by shape rather than morphology |

For **non-Bantu** languages (Cushitic, Afro-Asiatic, Nilotic,
Niger-Congo West), replace "noun class" with the relevant
analogous feature (e.g. Amharic verb conjugation templates,
Yoruba tone patterns, Somali gender/case inflection).

### 2.2 Minimal skeleton

See [the template at the end of this document](#template-minimal-language-rule-pack).

### 2.3 Language-specific extension hooks

If your language has features outside Luganda's rule set — e.g.
Yoruba tone marks, Amharic Ge'ez script, Somali template
morphology — override the relevant methods:

- `adaptive_morphological_segmentation(word)` — insert `·` at
  morpheme boundaries.
- `tokenize(text)` — pre-tokenise punctuation and call
  `adaptive_morphological_segmentation` per token.
- For Ge'ez / Tifinagh / other non-Latin scripts, add a
  `_normalise_script(text)` method and call it at the top of
  `tokenize`.

---

## Step 3 — Assemble a training corpus

Target **50k–200k sentences** of monolingual text in the target
language. Sources that have worked well:

| Source | Notes |
|---|---|
| **OPUS** (Bible, JW300, ParaCrawl) | Broad parallel + monolingual coverage. Check individual sub-corpus licenses. |
| **Wikipedia dumps** | Excellent for standard orthography. Use `wikiextractor`. |
| **OSCAR / Common Crawl** | Good scale, variable quality. Strong filtering required. |
| **African language NLP community datasets** (Masakhane, Lanfrica) | Usually the highest quality for African languages. |
| **Native-speaker hand-curated text** | Gold for low-resource languages — consider transcribing radio, YouTube captions, books. |

**Cleaning checklist** before training SentencePiece:

- [ ] UTF-8 normalise (NFC or NFKC — be consistent).
- [ ] Strip HTML / Markdown / wiki syntax.
- [ ] Remove duplicate lines.
- [ ] Remove lines < 3 words or > 200 words.
- [ ] Filter out non-target-language lines with a language ID
      classifier (fastText `lid.176` works well).
- [ ] Drop lines with >30% non-alphabetic characters.

Save the cleaned corpus to `data/xx/corpus.txt`, one sentence per
line. Record the sources and licenses in `data/xx/LICENSE.md`.

---

## Step 4 — Train the SentencePiece model

Use the notebook template in
[`notebooks/xx/train_xx_tokenizer.ipynb`](../notebooks) (copy from
[`notebooks/01_ABLT_Tokenizer_Training.ipynb`](../notebooks/01_ABLT_Tokenizer_Training.ipynb)).

The core step:

```python
import sentencepiece as spm
from tokenizer.languages.xx import EnhancedXxTokenizer

morph = EnhancedXxTokenizer()

with open("data/xx/corpus.txt", "r", encoding="utf-8") as f:
    raw = f.readlines()

with open("data/xx/corpus_presegmented.txt", "w", encoding="utf-8") as f:
    for line in raw:
        f.write(morph.tokenize(line).replace("·", " ") + "\n")

spm.SentencePieceTrainer.train(
    input="data/xx/corpus_presegmented.txt",
    model_prefix="tokenizer/models/xx_spm",
    model_type="unigram",
    vocab_size=8000,              # 5k–10k works well; tune to your corpus
    character_coverage=0.9995,
    normalization_rule_name="nfkc",
)
```

Keep `model_type="unigram"`. Do **not** switch to BPE —
Unigram composes better with the symbolic pre-segmenter.

---

## Step 5 — Write the validation notebook

Copy
[`notebooks/02_ABLT_Tokenizer_Validation.ipynb`](../notebooks/02_ABLT_Tokenizer_Validation.ipynb)
and adapt it. The notebook **must** compute and display, at minimum:

1. **Morpheme-boundary preservation rate** vs. a gold set of at
   least 50 hand-labelled sentences.
2. **Out-of-vocabulary (OOV) rate** on a held-out test set.
3. **Average tokens per sentence**, compared against `mBERT`
   (`bert-base-multilingual-cased`) and `XLM-R`
   (`xlm-roberta-base`).

Include **at least 5 qualitative tokenization examples** showing
how your rule pack recovers morphemes vs. how mBERT / XLM-R
shatter them.

---

## Step 6 — Quality gates

Before submitting a pull request, verify:

- [ ] `python examples/quickstart.py --lang xx` (or the equivalent)
      loads your tokenizer without error.
- [ ] Your validation notebook reports:
  - Morpheme preservation **≥ 85%** (we target 95%+ for merge).
  - OOV rate **≤ 5%** on the validation split.
  - Average tokens/sentence **at most 1.5×** the mBERT number
    on the same set (lower is better).
- [ ] At least one native speaker has reviewed your rule pack
      and signed off on the noun-class / verb-affix tables.
- [ ] `data/xx/LICENSE.md` lists all upstream sources and
      confirms that redistribution is permitted.
- [ ] You have added yourself as Language Steward in
      [`MAINTAINERS.md`](../MAINTAINERS.md).
- [ ] You have added yourself to
      [`CONTRIBUTORS.md`](../CONTRIBUTORS.md).

---

## Step 7 — Submit

Open a pull request titled:

```
feat(xx): add <Language Name> tokenizer rule pack
```

Include in the PR body:

- Link to your training notebook output.
- Link to your validation notebook output with all three metrics.
- A brief note on any linguistic decisions or trade-offs.
- A statement confirming native-speaker review.
- The CLA acceptance line (see [`CONTRIBUTING.md`](../CONTRIBUTING.md)).

A Maintainer will review within ~7 days. Expect one round of
revisions. Then your language becomes part of Alkebulan AI.

---

## Template: minimal language rule pack

Save as `tokenizer/languages/xx.py` (replace `xx` and
`EnhancedXxTokenizer` with your language code / class name):

```python
"""
Rule pack for <Language Name> (<ISO code>).
Language family: <family>.
Steward: <your name> (<your github handle>).
"""

from __future__ import annotations
from typing import Dict
from ..ablt_tokenizer import EnhancedLugandaTokenizer


class EnhancedXxTokenizer(EnhancedLugandaTokenizer):
    """Morphological pre-segmenter for <Language Name>."""

    def __init__(self) -> None:
        self.linguistic_features: Dict = {
            "noun_classes": {
                # Replace with your language's actual class system.
                # "class_1": {"singular_prefixes": [...], "plural_prefixes": [...]},
            },
            "verb_prefixes": [
                # Subject and object markers.
            ],
            "verb_extensions": [
                # Applicative, causative, passive, reciprocal, etc.
            ],
            "negation_prefixes": [],
            "tense_markers": {
                "past": [],
                "present": [],
                "future": [],
                "ongoing": [],
            },
            "semi_vowel_compounds": [],
            "nasal_compounds": [],
            "geminates": [],
            "loanwords": [],
        }

        self.phonological_rules = {
            "vowel_lengthening":       True,
            "consonant_gemination":    True,
            "vowel_harmony":           False,  # set True if language has vowel harmony
            "vowel_hiatus_resolution": True,
            "tone_patterns":           [],
        }
```

Then register it so users can do
`ABLT.from_pretrained("alkebulan/xx-<region>")`. The registration
scaffolding will be added in v2 — for v1, instantiate directly.

---

## Questions?

- Technical: open a GitHub issue tagged `new-language`.
- Linguistic: cc the current Luganda steward / founder on the
  issue for a first-look review.
- Strategic (grants, paid work, partnerships): reach out via
  [psalms23wave.com/contact](https://www.psalms23wave.com/contact).

Welcome to the project. The African AI industry needs what you
are about to ship.

— Mathew Sekanjako, Founder, Psalms23Wave LLC
