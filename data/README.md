<!--
Copyright (c) 2025 Mathew Sekanjako and Psalms23Wave LLC.
Licensed under the Apache License, Version 2.0.
-->

# `data/` — Luganda Corpora for ABLT v1

This folder contains the Luganda text corpora used to **train and
validate** the Alkebulan Bantu Language Tokenizer (ABLT) v1 and the
Sekan-optimised Mistral fine-tune.

All files were collected from **publicly-accessible Luganda text
sources**, then cleaned, normalised, de-duplicated, and preprocessed
by Mathew Sekanjako as part of the original research.

---

## Files

| File | What it is | Approx. size |
|---|---|---|
| `cleaned_luganda_corpus.csv` | Primary monolingual Luganda corpus after cleaning and deduplication. Used to train the SentencePiece Unigram model. | ~108k sentences |
| `luganda-approx50k.csv`      | A parallel English↔Luganda subset used for fine-tuning and evaluation. | ~50k pairs |
| `luganda_preprocessed.txt`   | Flattened plain-text version of the monolingual corpus after morphological pre-segmentation. This is what is fed into SentencePiece. | — |
| `MergedTok.txt`              | The merged tokenisation training input (pre-segmenter output for the full corpus). | — |

---

## Provenance

The text was **aggregated from multiple publicly-available Luganda
sources** on the open web — community-contributed Luganda content,
openly-hosted parallel translation pairs, and educational material.
Every file went through the following pipeline before it was added:

1. **Language filtering** — non-Luganda lines removed.
2. **Normalisation** — Unicode normalisation, casing, stripping
   non-linguistic artefacts (HTML, excess whitespace, URLs).
3. **Deduplication** — exact-match and near-duplicate removal.
4. **Morphological pre-segmentation** — Luganda-specific rules
   (noun-class prefixes, verb templates, geminates) applied before
   subword training. See `tokenizer/ablt_tokenizer.py` and
   `notebooks/01_ABLT_Tokenizer_Training.ipynb` for the full pipeline.

No personal, medical, financial, or otherwise sensitive data was
knowingly included. The corpora are intended as **general-domain
Luganda text**.

---

## Licence & intended use

These corpora are released together with the Alkebulan AI project
under the same top-level licence of this repository —
**Apache License 2.0** — **for the purpose of research, education,
and the development of tokenisers and language models for Luganda
and other Bantu languages.**

We believe that to the best of our knowledge all underlying sources
were publicly accessible at the time of collection. However, because
the text is aggregated from many upstream contributors and web
sources, we can **not guarantee the copyright status of every
individual line**. We therefore recommend that downstream users:

- Treat these corpora as **research-grade**, not production-licensed.
- Re-derive or re-license the data before using it in a commercial
  product where clean provenance is contractually required.
- Credit the Alkebulan AI project if you use this release as-is.

---

## Takedown / correction policy

If you are the copyright holder of a specific piece of text that
appears in these files and you would like it removed, or if you
want attribution added, please notify us via:

> **[psalms23wave.com/contact](https://www.psalms23wave.com/contact)**
>
> **Subject:** *"Data takedown / correction — Alkebulan AI"*

In your message, please include:

- Which file the text appears in (`cleaned_luganda_corpus.csv`, etc.).
- A pointer to the exact row / sentence / fragment.
- Proof of ownership or authorisation.

We commit to reviewing every request and acting on valid takedowns
within a **reasonable time**. A corrected dataset will be re-released
in the next version.

---

## Citation

If you use these corpora in academic work, please cite:

```bibtex
@software{alkebulan_ablt_2025_data,
  author    = {Sekanjako, Mathew},
  title     = {Alkebulan Bantu Language Tokenizer v1 — Luganda research corpora},
  year      = {2025},
  publisher = {Psalms23Wave LLC},
  url       = {https://github.com/Psalms23Wave/AlkebulanAI}
}
```

See [`../ATTRIBUTION.md`](../ATTRIBUTION.md) for the full project
citation.

---

© 2025 Mathew Sekanjako and Psalms23Wave LLC. Released under the
Apache License 2.0 in conjunction with the Alkebulan AI project.
