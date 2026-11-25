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

# ABLT: Alkebulan Bantu-Luganda Tokenizer, version 2.1

A tokenizer for Luganda that cuts words where their meaning changes, using the grammar of
the language, before a statistical tokenizer (SentencePiece) takes over.

Built by Mathew Sekanjako ([sekanjakomathew.com](https://www.sekanjakomathew.com)),
Psalms23Wave LLC, as part of Alkebulan AI.

- Code and full guide: [github.com/Psalms23Wave/AlkebulanAI](https://github.com/Psalms23Wave/AlkebulanAI)
- Package: [pypi.org/project/ablt](https://pypi.org/project/ablt/)

## Use

```bash
pip install ablt

ablt --cuts "Abanoonyiboobubudamu beetaaga obuyambi."
# Aba|noonyi|bo|obu|budamu b|eetaaga obu|yambi.
```

The sentence means "Refugees need help." Each `|` is a cut at a grammar boundary. The
first word is two words written as one, *abanoonyi* (seekers) and *b'obubudamu* (of refuge),
and ABLT cuts it into the people + seek + of + the noun marker + refuge.

### More examples

| Sentence | Meaning | How ABLT cuts it |
|---|---|---|
| Abanoonyiboobubudamu beetaaga obuyambi. | Refugees need help. | `Aba|noonyi|bo|obu|budamu b|eetaaga obu|yambi.` |
| Abanoonyiboobubudamu basaba obuyambi. | Refugees ask for help. | `Aba|noonyi|bo|obu|budamu ba|saba obu|yambi.` |
| Abanoonyiboobubudamu baagala obuyambi. | Refugees want help. | `Aba|noonyi|bo|obu|budamu ba|agala obu|yambi.` |
| Tuyambe abanoonyiboobubudamu. | Let us help refugees. | `Tu|yambe aba|noonyi|bo|obu|budamu.` |

Each of these gives back the exact sentence when decoded.

```python
from ablt import ABLT

tokenizer = ABLT()
text = "Abanoonyiboobubudamu beetaaga obuyambi."

ids = tokenizer.encode(text)
tokenizer.decode(ids) == text
# True   (decoding gives back exactly the text that went in)

tokenizer.morphemes("tebasobola")
# ['te', 'ba', 'sobola']
```

The package includes the model files on this page, so `pip install ablt` is enough.

## Reading the pieces

- A piece that starts with `▁` begins a new word.
- A piece that ends with `ǀ` is joined to the piece after it. `▁abaǀ` followed by `▁ntu` is
  the single word `abantu`.
- A root is the same piece wherever it appears. `▁ntu` is the same piece in `abantu`,
  `omuntu` and `ekintu`, so a model learns each root once.

## What was measured

| Test | ABLT 2.1 | ABLT 2.0 | Plain SentencePiece, same text and size |
|---|---|---|---|
| Cuts fall on grammar boundaries, 83 Luganda words (F1) | 99.5% | 91.7% | 41.3% |
| Words cut fully correctly | 98.8% | 86.7% | 18.1% |
| Pieces per word, 7,060 sentences of MasakhaNER 2.0 Luganda | 2.21 | 2.20 | 1.94 |
| Decoding gives back the exact text, 13,542 sentences | 13,542 of 13,542 | 13,542 of 13,542 | |

The plain tokenizer is a check with no grammar rules. It makes fewer pieces because it
leaves most words whole, where ABLT cuts them at the grammar.

Version 2.1 was also checked on data its rules were not written from. On 1,526 forms of 45
verbs from UniMorph Luganda, a cut falls exactly where the root begins in 60.6% of forms
(7.8% in 2.0). On the MasakhaPOS Luganda test set, none of 240 numbers and 6 of 2,308 nouns
are cut differently from 2.0. The scripts are in the GitHub repository under
`packages/ablt/tools/`.

## What changed in version 2.1

A word is now cut in as many places as its grammar shows: `alisoma` is `a + li + soma`,
`tebasobola` is `te + ba + sobola`, `okusomesa` is `oku + som + esa`, and
`abanoonyiboobubudamu` (refugees) is `aba + noonyi + bo + obu + budamu`. ABLT makes these
cuts only when the prefixes are documented in Luganda grammar and the root was seen in the
training text. Every other word is cut as in 2.0. `ABLT(version="2.0")` still gives the earlier version.

## Limits

- The answer list has 83 words. It needs checking and extending by Luganda speakers.
- About four verb forms in ten are still not cut into subject, tense and root.
- Object markers, modified stems (`nkoze`) and forms such as `ndikola` are not cut yet.
- A name at the very start of a sentence is treated as an ordinary word and may be cut.
- It has been tested on Luganda only. Other Bantu languages need their own rule tables.
- These tests show where ABLT cuts. Whether those cuts make a trained model learn better,
  or from less text, is still being tested.

## Files

| File | What it is |
|---|---|
| `ablt-luganda-v2.1.model` | version 2.1: the trained SentencePiece model (unigram, 6,000 pieces) |
| `ablt-luganda-v2.1.joiners.json` | version 2.1: the pieces that can be joined to the next piece |
| `ablt-luganda-v2.model`, `ablt-luganda-v2.joiners.json` | version 2.0 |
| `SHA256SUMS` | fingerprints of the files above |

Vocabulary size: 6,962 in version 2.1 (6,000 pieces, 961 joined pieces, 1 join token);
6,981 in version 2.0.

## Training text and credit

The model was trained on 58,346 unique lines of Luganda text. Most of that text comes from
the [SALT](https://github.com/SunbirdAI/salt) dataset by Sunbird AI, released under
CC BY-SA 4.0. One line in ten was held back and used only for testing.

## Licence and credit

Copyright (c) 2025-2026 Mathew Sekanjako and Psalms23Wave LLC. Apache License 2.0. Keep the
`NOTICE` file with any copy or derived work.

ABLT™, Sekan™ and Alkebulan AI™ are trademarks of Psalms23Wave LLC.

Contact: [psalms23wave.com/contact](https://www.psalms23wave.com/contact)
