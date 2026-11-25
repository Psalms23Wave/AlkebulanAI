# ABLT

ABLT is the Alkebulan Bantu-Luganda Tokenizer, version 2.1. It cuts Luganda words where
their meaning changes, using the grammar of the language, and then lets a statistical
tokenizer (SentencePiece) cut the rest.

Built by Mathew Sekanjako ([sekanjakomathew.com](https://www.sekanjakomathew.com),
[LinkedIn](https://www.linkedin.com/in/sekanjako-mathew/)), Psalms23Wave LLC, as part of
Alkebulan AI.

## Install

```bash
pip install ablt
```

It needs only `sentencepiece`. The trained Luganda model is inside the package.

## Use

```bash
ablt --cuts "Abanoonyiboobubudamu beetaaga obuyambi."
# Aba|noonyi|bo|obu|budamu b|eetaaga obu|yambi.
```

The sentence means "Refugees need help." Each `|` is a cut at a grammar boundary. The
first word is two words written as one, *abanoonyi* (seekers) and *b'obubudamu* (of refuge),
and ABLT cuts it into the people + seek + of + the noun marker + refuge.

### More examples

| Sentence | Meaning | How ABLT cuts it |
|---|---|---|
| Abanoonyiboobubudamu beetaaga obuyambi. | Refugees need help. | `Aba\|noonyi\|bo\|obu\|budamu b\|eetaaga obu\|yambi.` |
| Abanoonyiboobubudamu basaba obuyambi. | Refugees ask for help. | `Aba\|noonyi\|bo\|obu\|budamu ba\|saba obu\|yambi.` |
| Abanoonyiboobubudamu baagala obuyambi. | Refugees want help. | `Aba\|noonyi\|bo\|obu\|budamu ba\|agala obu\|yambi.` |
| Tuyambe abanoonyiboobubudamu. | Let us help refugees. | `Tu\|yambe aba\|noonyi\|bo\|obu\|budamu.` |

Each of these gives back the exact sentence when decoded.

### In Python

```python
from ablt import ABLT

tokenizer = ABLT()
text = "Abanoonyiboobubudamu beetaaga obuyambi."

tokenizer.tokenize(text)
# ['▁Abaǀ', '▁noonyiǀ', '▁boǀ', '▁obuǀ', '▁budamu', '▁bǀ', '▁eetaaga', '▁obuǀ', '▁yambi', '.']

ids = tokenizer.encode(text)
tokenizer.decode(ids) == text
# True   (decoding gives back exactly the text that went in)

tokenizer.show_cuts("tebasobola kusoma")
# 'te|ba|sobola ku|soma'

tokenizer.morphemes("tebasobola")
# ['te', 'ba', 'sobola']
```

### From the terminal

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

Run `python packages/ablt/tools/evaluate.py` and `python packages/ablt/tools/evaluate_rules.py`
to reproduce these.

| Test | ABLT 2.1 | ABLT 2.0 | Plain SentencePiece, same text and size |
|---|---|---|---|
| Cuts fall on grammar boundaries, 83 Luganda words (F1) | 99.5% | 91.7% | 41.3% |
| Words cut fully correctly | 98.8% | 86.7% | 18.1% |
| Pieces per word, 7,060 sentences of MasakhaNER 2.0 Luganda | 2.21 | 2.20 | 1.94 |
| Decoding gives back the exact text, 13,542 sentences | 13,542 of 13,542 | 13,542 of 13,542 | |

The plain tokenizer is a check built for this comparison: it is trained on the same text
with the same settings and has no grammar rules. It makes fewer pieces because it leaves
most words whole, where ABLT cuts them at the grammar.

On the same MasakhaNER sentences, the tokenizers of two general models make 2.69 pieces per
word (Qwen2.5) and 2.89 (GPT-2).

### Checks on data the rules were not written from

The 83 words were in view while version 2.1 was built, so the rules were also checked on
two public sets. Each set was split in two, the rules were tuned on one half, and the
numbers below come from the other half.

| Check | ABLT 2.1 | ABLT 2.0 |
|---|---|---|
| UniMorph Luganda, 1,526 forms of 45 verbs: a cut falls exactly where the root begins | 60.6% | 7.8% |
| The same forms: a cut falls inside the listed verb | 11.2% | 21.5% |
| MasakhaPOS Luganda test set, 240 numbers: cut differently from 2.0 | 0 | |
| The same set, 2,308 nouns: cut differently from 2.0 | 6 (0.3%) | |
| Words in the 83-word list that were right in 2.0 and are wrong in 2.1 | 0 | |

The six nouns are verb forms and verb-built words that the taggers marked as nouns
(`Agamba`, `bikozesebwa`), and the joined word `abanoonyiboobubudamu`.

## What changed in version 2.1

A word is now cut in as many places as its grammar shows.

| Word | Version 2.0 | Version 2.1 |
|---|---|---|
| alisoma (he or she will read) | `alisoma` | `a + li + soma` |
| tebasobola (they cannot) | `tebasobola` | `te + ba + sobola` |
| okusomesa (to teach) | `oku + somesa` | `oku + som + esa` |
| agenda (he or she goes) | `ag + enda` | `a + genda` |
| abanoonyiboobubudamu (refugees) | `aba + noonyiboobubudamu` | `aba + noonyi + bo + obu + budamu` |
| abantu (people) | `aba + ntu` | `aba + ntu` |

ABLT makes one of these new cuts only when it has evidence for it:

- The verb prefixes (subject, tense, negative) come from the documented tables of Luganda
  grammar.
- The root must be one of 732 verb roots seen at least five times after `oku-` in the
  training text.
- Passive, applied and causative endings (`-ibwa`, `-ebwa`, `-ira`, `-era`, `-isa`, `-esa`)
  are cut only when the shorter root is also in that list.
- Counting words (`abiri`, `asatu`) and "of" and "my" forms (`kyange`, `waffe`) are never
  read as verbs.
- A word without that evidence is cut exactly as version 2.0 cut it. The version 1 and 2.0
  grammar tables are unchanged.

Version 2.0 is still inside the package: `ABLT(version="2.0")` gives its rules and its model.

## What changed from version 1

| | Version 1 | Version 2 |
|---|---|---|
| Decoding gives back the exact text | about 3% of sentences | every sentence tested |
| Words that start with a capital letter | not cut | cut like any other word |
| Names and acronyms in the middle of a sentence | cut by the rules | left whole |
| Forced short pieces | yes, 3.82 pieces per word | none, 2.20 pieces per word |
| A root after a prefix | a different piece from the root alone | the same piece |
| Text is rewritten before tokenizing | yes (spaces added round punctuation) | no |

## Limits

- The answer key has 83 words. It needs checking and extending by Luganda speakers.
- About four verb forms in ten are still not cut into subject, tense and root, because the
  root is not among the 732 seen in the training text.
- Object markers (`a-ki-soma`, he reads it), modified stems (`nkoze`) and the first-person
  forms that change shape (`ndikola`) are not cut yet.
- A name at the very start of a sentence is treated as an ordinary word and may be cut.
- It has been tested on Luganda only. Other Bantu languages need their own rule tables.
- These tests show where ABLT cuts. Whether those cuts make a trained model learn better,
  or from less text, is still being tested.

## Training text and credit

The bundled model was trained on 58,346 unique lines of Luganda text (see `DATA.md` in the
Alkebulan AI repository). Most of that text comes from the SALT dataset by Sunbird AI,
released under CC BY-SA 4.0. One line in ten was held back and used only for testing.

## Rebuilding the model

```bash
python packages/ablt/tools/build_lexicon.py     # the word lists the rules check against
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
