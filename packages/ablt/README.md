# ABLT

**Alkebulan Bantu-Luganda Tokenizer, version 2.** A tokenizer for Luganda that cuts words
where their meaning changes, using the grammar of the language, before a statistical
tokenizer (SentencePiece) takes over.

Built by Mathew Sekanjako ([sekanjakomathew.com](https://www.sekanjakomathew.com),
[LinkedIn](https://www.linkedin.com/in/sekanjako-mathew/)), Psalms23Wave LLC, as part of
Alkebulan AI.

## Install

```bash
pip install "git+https://github.com/Psalms23Wave/AlkebulanAI#subdirectory=packages/ablt"
```

It needs only `sentencepiece`. The trained Luganda model is inside the package.

## Use

```python
from ablt import ABLT

tokenizer = ABLT()

tokenizer.tokenize("Abantu basoma ebitabo.")
# ['▁Abaǀ', '▁ntu', '▁baǀ', '▁soma', '▁ebiǀ', '▁tabo', '.']

ids = tokenizer.encode("Abantu basoma ebitabo.")
tokenizer.decode(ids)
# 'Abantu basoma ebitabo.'   (exactly the text that went in)

tokenizer.show_cuts("okusoma ebitabo")
# 'oku|soma ebi|tabo'

tokenizer.morphemes("okusoma")
# ['oku', 'soma']
```

### From the terminal, with no Python to write

```bash
ablt "Abantu baagala okusoma ebitabo."
# ▁Abaǀ ▁ntu ▁baǀ ▁agala ▁okuǀ ▁soma ▁ebiǀ ▁tabo .

ablt --cuts "Abantu baagala okusoma ebitabo."
# Aba|ntu ba|agala oku|soma ebi|tabo.

ablt --ids "Abantu baagala okusoma ebitabo."      # piece numbers
ablt < story.txt                                   # a whole file, line by line
```

### Reading the pieces

- A piece that starts with `▁` begins a new word.
- A piece that ends with `ǀ` is joined to the piece after it. `▁abaǀ` followed by `▁ntu` is
  the single word `abantu`.
- A root is the same piece wherever it appears. `▁ntu` is the same piece in `abantu`,
  `omuntu` and `ekintu`, and `▁soma` is the same piece in `okusoma` and `basoma`, so a model
  learns each root once.

## What was measured

Run `python packages/ablt/tools/evaluate.py` to reproduce these.

| Test | ABLT version 2 | Plain SentencePiece trained on the same text, same size |
|---|---|---|
| Cuts fall on grammar boundaries, 83 Luganda words (F1) | 91.7% | 41.3% |
| The same words written with a capital letter | 93.3% | 72.7% |
| Words cut fully correctly | 86.7% | 18.1% |
| Pieces per word, 7,060 sentences of MasakhaNER 2.0 Luganda | 2.20 | 1.94 |
| Decoding gives back the exact text, 13,542 sentences | 13,542 of 13,542 | |

The plain tokenizer is a check built for this comparison: it is trained on the same text
with the same settings and has no grammar rules. It makes fewer pieces because it leaves
most words whole. ABLT cuts on purpose, at the grammar.

On the same MasakhaNER sentences, the tokenizers of two general models make 2.69 pieces per
word (Qwen2.5) and 2.89 (GPT-2).

## What changed from version 1

| | Version 1 | Version 2 |
|---|---|---|
| Decoding gives back the exact text | about 3% of sentences | every sentence tested |
| Words that start with a capital letter | not cut | cut like any other word |
| Names and acronyms in the middle of a sentence | cut by the rules | left whole |
| Forced short pieces | yes, 3.82 pieces per word | none, 2.20 pieces per word |
| A root after a prefix | a different piece from the root alone | the same piece |
| Text is rewritten before tokenizing | yes (spaces added round punctuation) | no |

The grammar rules themselves are the version 1 rules, unchanged: the longest noun-class
prefix, otherwise the longest verb extension. Each word is cut in at most one place.

## Limits

- The answer key has 83 words. It needs checking and extending by Luganda speakers.
- Each word is cut once. `alisoma` becomes `ali|soma`, where a full analysis is
  `a|li|soma`.
- A name at the very start of a sentence is treated as an ordinary word and may be cut.
- It has been tested on Luganda only. Other Bantu languages need their own rule tables.
- It is shown to cut words at grammar boundaries. Whether that makes a trained model learn
  better, or from less text, has not been tested yet.

## Training text and credit

The bundled model was trained on 58,346 unique lines of Luganda text (see `DATA.md` in the
Alkebulan AI repository). Most of that text comes from the SALT dataset by Sunbird AI,
released under CC BY-SA 4.0. One line in ten was held back and used only for testing.

## Rebuilding the model

```bash
python packages/ablt/tools/train_model.py    # trains and writes the bundled model
python packages/ablt/tools/evaluate.py       # prints the table above
python -m pytest packages/ablt/tests -q
```

## Licence and credit

Copyright 2025-2026 Mathew Sekanjako and Psalms23Wave LLC. Licensed under the Apache License,
version 2.0 (see `LICENSE`). Anyone who shares this work, changed or unchanged, must keep the
copyright notices and the `NOTICE` file, and must say what they changed.

ABLT™, Sekan™ and Alkebulan AI™ are trademarks of Psalms23Wave LLC. The licence does not
give permission to use these names for other products. The project's full terms are in
`LICENSING.md`, `TRADEMARK.md` and `COMMERCIAL.md` in the Alkebulan AI repository.

To cite it, see `CITATION.cff`.
