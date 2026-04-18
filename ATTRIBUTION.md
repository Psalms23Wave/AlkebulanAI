# Attribution & Citation Guide

> Every fork, paper, blog post, model, product, or presentation that
> uses Alkebulan AI, ABLT, or the Sekan algorithm must credit the
> originator. This page tells you exactly how.

**Originator:** Mathew Sekanjako
**Entity:** Psalms23Wave LLC — [www.psalms23wave.com](https://www.psalms23wave.com)
**Year:** 2025
**License:** Apache License 2.0 (code) — see [`LICENSE`](./LICENSE) and [`NOTICE`](./NOTICE)

---

## 1. The minimum requirement (enforced by law)

Under Apache License 2.0 §4(c) and §4(d), any redistribution or
derivative work **must** preserve:

1. The contents of the [`LICENSE`](./LICENSE) file.
2. The contents of the [`NOTICE`](./NOTICE) file — reproduced in at
   least one of: a NOTICE file in your distribution, your
   documentation, or within a UI your software displays.

This is not optional. It is the legal attribution floor.

---

## 2. Academic citation (BibTeX)

### The framework as a whole

```bibtex
@misc{sekanjako2025alkebulan,
  title        = {Alkebulan AI: A Morphologically-Faithful Tokenization
                   and Simpson-Rule Optimization Framework for African
                   Languages},
  author       = {Sekanjako, Mathew},
  year         = {2025},
  organization = {Psalms23Wave LLC},
  url          = {https://www.psalms23wave.com},
  note         = {Released open-source under Apache License 2.0}
}
```

### The Sekan algorithm specifically

```bibtex
@misc{sekanjako2025sekan,
  title        = {Sekan: A Simpson-Rule-Based Adaptive Optimizer for
                   Low-Resource African Language Modelling},
  author       = {Sekanjako, Mathew},
  year         = {2025},
  organization = {Psalms23Wave LLC},
  url          = {https://huggingface.co/Psalms23Wave/Alkebulan-AI},
  note         = {Released as part of the Alkebulan AI project,
                   Apache License 2.0}
}
```

### The ABLT tokenizer specifically

```bibtex
@misc{sekanjako2025ablt,
  title        = {ABLT v1: The Alkebulan Bantu-Luganda Tokenizer —
                   A Morphologically-Aware Two-Stage Tokenizer for
                   Bantu Languages},
  author       = {Sekanjako, Mathew},
  year         = {2025},
  organization = {Psalms23Wave LLC},
  url          = {https://huggingface.co/Psalms23Wave/Alkebulan-AI},
  note         = {Released as part of the Alkebulan AI project,
                   Apache License 2.0}
}
```

---

## 3. Inline credit (for blog posts, slides, docs)

### Minimal one-liner
> Built on **Alkebulan AI** — ABLT tokenizer and Sekan optimizer,
> invented by Mathew Sekanjako (Psalms23Wave LLC).

### One-paragraph credit
> This project uses **Alkebulan AI**, an open-source tokenization and
> optimization framework for African languages. Alkebulan AI, the ABLT
> tokenizer, and the Sekan algorithm were invented and developed by
> **Mathew Sekanjako** and released through **Psalms23Wave LLC**
> ([psalms23wave.com](https://www.psalms23wave.com)) under the Apache
> License 2.0.

---

## 4. Badges for READMEs

Copy any of the following into your project's README:

**Built on Alkebulan AI**
```markdown
[![Built on Alkebulan AI](https://img.shields.io/badge/built%20on-Alkebulan%20AI-000?style=flat-square)](https://www.psalms23wave.com)
```

**Powered by Sekan**
```markdown
[![Powered by Sekan](https://img.shields.io/badge/powered%20by-Sekan-1f6feb?style=flat-square)](https://www.psalms23wave.com)
```

**ABLT-compatible**
```markdown
[![ABLT-compatible](https://img.shields.io/badge/tokenizer-ABLT--compatible-2e7d32?style=flat-square)](https://www.psalms23wave.com)
```

---

## 5. When you extend the project (new languages, new features)

If you add a new African language, a new optimizer variant, or a new
research contribution on top of this project — we welcome that, and
it is exactly the point of open-sourcing it. Please do both:

1. **Keep the NOTICE file intact** (legal requirement).
2. **Add a line to [`CONTRIBUTORS.md`](./CONTRIBUTORS.md)** with your
   name, GitHub handle, and a one-line description of what you
   contributed — submitted as a pull request. The founder
   (Mathew Sekanjako) will merge it.
3. **Cite the originator in any paper or publication** using one of
   the BibTeX blocks above.
4. **Preserve the core framework name.** The Marks policy
   ([`TRADEMARK.md`](./TRADEMARK.md)) means your extension should be
   named like *"Alkebulan AI Swahili rule-pack"* or *"Sekan-AdamW
   hybrid"* — not *"Alkebulan AI 2"*.

---

## 6. Commercial or proprietary use

If you are a company that wants to use this project in a proprietary
context — for example embedding the tokenizer in a closed-source
product, distributing it under a different license, or removing the
attribution requirements — please see [`COMMERCIAL.md`](./COMMERCIAL.md)
and contact Psalms23Wave LLC for a commercial license.

---

## 7. A personal note from the founder

This project was born from the observation that tokenizers shipped by
the world's leading AI labs silently mis-segment African languages
and the machine-learning community had largely accepted that as
"just how low-resource languages are." I didn't.

The ABLT tokenizer and the Sekan optimizer took months of mathematical
work, linguistic study, and training on RunPod and Colab. I am
releasing all of it under Apache 2.0 so that **the African AI
industry has a real foundation to build on** — so that the next
tokenizer for Swahili, Yoruba, or Amharic does not have to start
from scratch, and so that African engineers and researchers can
train AI agents, translation systems, and language models for the
African context without being blocked at the tokenizer step.

If you extend this work, please give credit where it is due — not
out of vanity, but so that the origin of the research can be traced,
the methodology can be checked, and the momentum can keep building
in the open.

— **Mathew Sekanjako**
  Founder, Psalms23Wave LLC
  [www.psalms23wave.com](https://www.psalms23wave.com)
