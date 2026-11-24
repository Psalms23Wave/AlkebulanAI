---
license: apache-2.0
language:
  - lg
library_name: ablt
tags:
  - tokenizer
  - luganda
  - bantu
  - african-languages
  - morphology
  - sentencepiece
---

# ABLT: Alkebulan Bantu-Luganda Tokenizer, version 2

A tokenizer for Luganda that cuts words where their meaning changes, using the grammar of
the language, before a statistical tokenizer (SentencePiece) takes over.

Built by Mathew Sekanjako ([sekanjakomathew.com](https://www.sekanjakomathew.com)),
Psalms23Wave LLC, as part of Alkebulan AI.

- Code and full guide: [github.com/Psalms23Wave/AlkebulanAI](https://github.com/Psalms23Wave/AlkebulanAI)
- Package: [pypi.org/project/ablt](https://pypi.org/project/ablt/)

## Use

```bash
pip install ablt

ablt --cuts "Abantu baagala okusoma ebitabo."
# Aba|ntu ba|agala oku|soma ebi|tabo.
```

```python
from ablt import ABLT

tokenizer = ABLT()

tokenizer.tokenize("Abantu basoma ebitabo.")
# ['▁Abaǀ', '▁ntu', '▁baǀ', '▁soma', '▁ebiǀ', '▁tabo', '.']

ids = tokenizer.encode("Abantu basoma ebitabo.")
tokenizer.decode(ids)
# 'Abantu basoma ebitabo.'   (exactly the text that went in)
```

The package carries the model files on this page inside it, so `pip install ablt` is all
that is needed.

## Reading the pieces

- A piece that starts with `▁` begins a new word.
- A piece that ends with `ǀ` is joined to the piece after it. `▁abaǀ` followed by `▁ntu` is
  the single word `abantu`.
- A root is the same piece wherever it appears. `▁ntu` is the same piece in `abantu`,
  `omuntu` and `ekintu`, so a model learns each root once.

## What was measured

| Test | ABLT version 2 | Plain SentencePiece trained on the same text, same size |
|---|---|---|
| Cuts fall on grammar boundaries, 83 Luganda words (F1) | 91.7% | 41.3% |
| The same words written with a capital letter | 93.3% | 72.7% |
| Pieces per word, 7,060 sentences of MasakhaNER 2.0 Luganda | 2.20 | 1.94 |
| Decoding gives back the exact text, 13,542 sentences | 13,542 of 13,542 | |

The plain tokenizer is a check with no grammar rules. It makes fewer pieces because it
leaves most words whole; ABLT cuts on purpose, at the grammar. The scripts that produce
these numbers are in the GitHub repository under `packages/ablt/tools/`.

## Limits

- The answer list has 83 words. It needs checking and extending by Luganda speakers.
- Each word is cut once. `alisoma` becomes `ali|soma`, where a full analysis is `a|li|soma`.
- A name at the very start of a sentence is treated as an ordinary word and may be cut.
- Tested on Luganda only. Other Bantu languages need their own rule tables.
- It is shown to cut words at grammar boundaries. Whether that makes a trained model learn
  better, or from less text, has not been tested yet.

## Files

| File | What it is |
|---|---|
| `ablt-luganda-v2.model` | the trained SentencePiece model (unigram, 6,000 pieces) |
| `ablt-luganda-v2.joiners.json` | the pieces that can be joined to the next piece |
| `SHA256SUMS` | fingerprints of the two files above |

Vocabulary size: 6,981 (6,000 pieces, 980 joined pieces, 1 join token).

## Training text and credit

The model was trained on 58,346 unique lines of Luganda text. Most of that text comes from
the [SALT](https://github.com/SunbirdAI/salt) dataset by Sunbird AI, released under
CC BY-SA 4.0. One line in ten was held back and used only for testing.

## Licence and credit

Copyright (c) 2025-2026 Mathew Sekanjako and Psalms23Wave LLC. Apache License 2.0. Keep the
`NOTICE` file with any copy or derived work.

ABLT™, Sekan™ and Alkebulan AI™ are trademarks of Psalms23Wave LLC.

Contact: [psalms23wave.com/contact](https://www.psalms23wave.com/contact)
