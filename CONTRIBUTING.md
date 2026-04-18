# Contributing to Alkebulan AI

Thank you for considering a contribution — this project exists
specifically **to be built on**. Every new African language, every
sharper tokenization rule, every Sekan improvement moves the mission
forward: giving Africa a real foundation for modern AI.

This document tells you what to do, in what order, and what you are
agreeing to when you open a pull request.

---

## Table of contents

1. [The simple rules](#the-simple-rules)
2. [Contributor License Agreement (CLA)](#contributor-license-agreement-cla)
3. [What kinds of contributions we want](#what-kinds-of-contributions-we-want)
4. [How to set up your environment](#how-to-set-up-your-environment)
5. [Coding standards](#coding-standards)
6. [Adding a new African language](#adding-a-new-african-language)
7. [Submitting a pull request](#submitting-a-pull-request)
8. [Review process](#review-process)
9. [Getting added to CONTRIBUTORS.md](#getting-added-to-contributorsmd)
10. [Code of Conduct](#code-of-conduct)

---

## The simple rules

1. **Preserve the NOTICE file.** This is a legal requirement of
   Apache 2.0 §4(d). Do not edit it without approval.
2. **One logical change per pull request.** Don't mix a bug fix with
   a new language rule pack.
3. **Every code change needs tests or a reproducible notebook cell.**
4. **Every substantive change needs a docs update.**
5. **Be respectful, concise, and receptive to feedback.** See
   [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md).
6. **By submitting a PR you accept the CLA.** See next section.

---

## Contributor License Agreement (CLA)

**Every contributor** must agree to the terms of [`CLA.md`](./CLA.md)
before their first contribution is merged.

You agree to the CLA by adding the following line as the **last line
of your first pull request description** (not the commit, the PR):

```
I have read and agree to the terms of the Alkebulan AI CLA.md.
```

In short, the CLA says you:

- certify that your contribution is your own work;
- grant Psalms23Wave LLC a perpetual, worldwide, royalty-free
  license to use, modify, distribute, and re-license your
  contribution under Apache 2.0 and, at Psalms23Wave LLC's
  discretion, other terms (e.g., commercial licenses);
- acknowledge that Psalms23Wave LLC and Mathew Sekanjako retain
  authorship attribution for the project as a whole, including
  the Marks ("Alkebulan AI", "ABLT", "Sekan").

The CLA does **not** transfer ownership of your contribution away
from you — you still own it. It just gives the project the rights it
needs to keep functioning as a single coherent thing.

---

## What kinds of contributions we want

Ordered by priority:

### Top priority
- **New-language morphology rule packs.** Follow
  [`docs/ADDING_A_LANGUAGE.md`](./docs/ADDING_A_LANGUAGE.md).
  Currently wanted: **Swahili, Kinyarwanda, Lusoga, Runyankore,
  Kikuyu, Lingala, Shona, isiZulu, Amharic, Yoruba, Wolof, Somali**.
- **Benchmark datasets for existing languages.** A clean,
  stratified validation set with gold morpheme boundaries.
- **Sekan algorithm research.** Ablations, new variants, theoretical
  analysis — open an issue first to discuss.

### High priority
- Bug fixes in `tokenizer/ablt_tokenizer.py` or
  `sekan_algorithm/sekan.py`.
- Performance improvements that preserve correctness.
- More comprehensive tests / reproducible notebooks.
- Documentation improvements, typo fixes, translation of
  docs into African languages.

### Welcome but lower priority
- New example scripts.
- CI / tooling improvements.
- Integration adapters (e.g., tokenizer compatibility with
  Hugging Face `tokenizers` fast interface).

### Please check first by opening an issue
- Major refactors of the public API.
- New dependencies.
- New sub-packages.
- Anything that changes the semantics of `ABLT.tokenize` / `ABLT.encode`.

---

## How to set up your environment

```bash
git clone <your-fork-url> AlkebulanAI
cd AlkebulanAI
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run the built-in smoke test
python examples/quickstart.py
```

Python 3.9+ is required. PyTorch is only needed for the Sekan
optimizer / attention module; the tokenizer alone works with just
`sentencepiece`.

---

## Coding standards

- **Style:** [PEP 8](https://peps.python.org/pep-0008/), enforced by
  `ruff` + `black` (recommended, not required).
- **Type hints:** Use them on all new public functions and methods.
- **Docstrings:** Public classes/functions need a short docstring.
  Use reStructuredText or Google style — be consistent with
  surrounding code.
- **Imports:** standard library first, third-party second, local
  third. No wildcard imports.
- **No new runtime dependencies** without discussion.
- **No files > 1 MB** in the main branch except under `data/` and
  `tokenizer/` (model artefacts).

---

## Adding a new African language

This is the headline contribution we want. The full playbook is in:

> **[`docs/ADDING_A_LANGUAGE.md`](./docs/ADDING_A_LANGUAGE.md)**

Summary:

1. Create a rule file: `tokenizer/languages/{lang_code}.py` that
   subclasses `EnhancedLugandaTokenizer` and overrides
   `linguistic_features` and `phonological_rules` for your language.
2. Provide a monolingual corpus of **50k–200k sentences** (CC-licensed
   source preferred) under `data/{lang_code}/`.
3. Train a SentencePiece model using the existing pipeline; save to
   `tokenizer/models/{lang_code}_spm.model`.
4. Add a validation notebook under
   `notebooks/{lang_code}/validate_{lang_code}_tokenizer.ipynb`
   reproducing the three headline metrics: morpheme preservation,
   OOV rate, avg tokens/sentence.
5. Add yourself to [`CONTRIBUTORS.md`](./CONTRIBUTORS.md).

Maintainers will review for linguistic accuracy (we may loop in a
native speaker) and merge.

---

## Submitting a pull request

1. **Fork** the repo and create a feature branch:
   `feat/swahili-rules`, `fix/token-id-bug`, etc.
2. **Make focused commits** with clear messages.
   Prefer `feat(swahili): add class 1-18 noun prefixes` over
   `updates`.
3. **Keep your branch up-to-date** with `main` via rebase or merge.
4. **Open a pull request** against `main` with:
   - A clear title.
   - A description of what / why / how.
   - Screenshots or notebook outputs where relevant.
   - The CLA line (see above) as the last line of the PR body —
     required for your first PR.
5. Wait for CI (if configured) and maintainer review.

---

## Review process

- First response from a maintainer: usually **within 7 days**.
- We may ask for changes. Engage with the feedback and push more
  commits to the same branch — the PR updates automatically.
- Final approval and merge is by **Mathew Sekanjako** (project
  founder) or a designated maintainer listed in
  [`MAINTAINERS.md`](./MAINTAINERS.md).
- Merging uses **squash-and-merge** to keep the history clean.

---

## Getting added to CONTRIBUTORS.md

When your first contribution is merged, add yourself to
[`CONTRIBUTORS.md`](./CONTRIBUTORS.md) as part of that PR (or the
reviewer will add you). Format:

```markdown
- **Your Name** ([@github-handle](https://github.com/github-handle)) —
  *what you contributed* (short, one line)
```

---

## Code of Conduct

By participating in this project you agree to abide by
[`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md). Reports of unacceptable
behaviour can be sent privately via
[psalms23wave.com/contact](https://www.psalms23wave.com/contact)
(subject: *"Code of Conduct report"*).

---

## Questions?

- **Bug / feature discussion:** open a GitHub issue.
- **Security issue:** see [`SECURITY.md`](./SECURITY.md) — do NOT
  open a public issue.
- **Commercial / trademark / licensing:** see
  [`COMMERCIAL.md`](./COMMERCIAL.md) / [`TRADEMARK.md`](./TRADEMARK.md).
- **Anything else:** [psalms23wave.com/contact](https://www.psalms23wave.com/contact).

Thank you for helping build the foundation of African AI.

— Mathew Sekanjako, Founder, Psalms23Wave LLC
