# Training data

The training text is not kept in this repository. The trained tokenizer model is inside the
package (`packages/ablt/`), so nothing here is needed to use ABLT.

## What the models were trained on

| Text | Source | Licence |
|---|---|---|
| Luganda sentences, the largest part | [SALT](https://github.com/SunbirdAI/salt), by Sunbird AI | CC BY-SA 4.0 |
| Luganda Bible-style text | public Luganda Bible text | |
| Other Luganda sentences gathered for the project in 2025 | | |

The ABLT version 2 model was trained on 58,346 unique lines of this text. One line in ten
(6,482 lines) was held back and used only for testing.

Version 1 also used a Luganda word list and sound table from
[MARY TTS](https://github.com/marytts/marytts), by DFKI (LGPL v3), as reference material.

## How to rebuild the model

1. Gather Luganda text, one sentence per line, into `data/MergedTok.txt`. SALT is the
   place to start.
2. Run `python packages/ablt/tools/train_model.py`. It removes duplicate lines, holds back
   one line in ten, cuts the rest by grammar, and trains SentencePiece (unigram, 6,000
   pieces).
3. Run `python packages/ablt/tools/evaluate.py` to score the result.

A different collection of text will give a slightly different model. The answer list used
to score the cuts is in `packages/ablt/tests/data/`.

## Earlier versions

These files were in this repository from April to November 2026 and can be found in its
history.
