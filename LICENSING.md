# Licensing Guide

> Short, plain-English version: **use the code freely (Apache 2.0),
> preserve the NOTICE file, don't put the "Alkebulan AI" / "Sekan"
> brand on your own products without asking, and if you need
> commercial terms, message us at
> [psalms23wave.com/contact](https://www.psalms23wave.com/contact).**

This page explains how the licensing of different parts of this
project fits together.

---

## The three buckets

Alkebulan AI is made of three kinds of material, each under its own
terms:

| Bucket | What's in it | License |
|---|---|---|
| **Code** | Everything in `tokenizer/`, `sekan_algorithm/`, `examples/` | **Apache License 2.0** ([`LICENSE`](./LICENSE)) |
| **Model & tokenizer artefacts** | `tokenizer/luganda_spm.model`, `tokenizer/luganda_spm.vocab`, `tokenizer/ablt_v1_tokenizer.pkl` | **Apache License 2.0** |
| **Trademarks** | The names *Alkebulan AI*, *ABLT*, *Sekan*, *Alkebulan Bantu Language Tokenizer* | **Reserved** — see [`TRADEMARK.md`](./TRADEMARK.md) |
| **Data and language resources from others** | The Luganda text in `data/`; the lexicon and allophone files in `linguistic_resources/` | **Their own licences**: SALT by Sunbird AI is CC BY-SA 4.0; the MARY TTS files by DFKI are LGPL v3 |

*Most of the text in `data/` comes from the SALT dataset by Sunbird AI,
and the files in `linguistic_resources/` come from MARY TTS by DFKI.
They are credited in [`ATTRIBUTION.md`](./ATTRIBUTION.md) and in the
[`NOTICE`](./NOTICE), and they stay under their own licences. The
Apache 2.0 licence of this project does not replace them.*

---

## What you can do under Apache 2.0 (most people)

You can, for free, without asking:

- **Use** the code and artefacts commercially or non-commercially.
- **Modify** them.
- **Distribute** your modifications.
- **Integrate** them into proprietary products.
- **Sell** products that include them.

You **must**:

- **Include a copy of the Apache 2.0 LICENSE** in any distribution.
- **Preserve the [`NOTICE`](./NOTICE) file** — this is the
  attribution clause and is legally required.
- **State if you have modified the code.**
- **Preserve copyright, patent, and trademark notices** from the
  Source form.

You **must NOT**:

- Use the Marks (*Alkebulan AI*, *ABLT*, *Sekan*, etc.) to brand
  your own product, service, or fork without written permission
  from Psalms23Wave LLC. See [`TRADEMARK.md`](./TRADEMARK.md).

---

## The NOTICE requirement, explained

Apache 2.0 §4(d) requires that any derivative work reproduces the
contents of the NOTICE file. Practically, this means:

- If you fork this repo, **keep `NOTICE` in the root**.
- If you ship a product that embeds this code, include the NOTICE
  contents in your product's "About" / "Acknowledgements" /
  "Third-party notices" section.
- If you write a paper or blog post, cite the project per
  [`ATTRIBUTION.md`](./ATTRIBUTION.md).

This is how Mathew Sekanjako's authorship of the Sekan algorithm
and the ABLT architecture is legally preserved in every downstream
use of this work.

---

## When you need a separate (commercial) license

Apache 2.0 is enough for almost everyone. Contact us via
[`COMMERCIAL.md`](./COMMERCIAL.md) if you need:

- To remove or replace the NOTICE file.
- To use the trademarked names in your product or service name.
- Private rule-pack development, enterprise support, or warranty
  coverage.
- A proprietary license compatible with a specific procurement
  requirement.

---

## When you are a contributor

When you submit a pull request, you grant Psalms23Wave LLC the
rights described in [`CLA.md`](./CLA.md). In short:

- You keep ownership of your contribution.
- You grant Psalms23Wave LLC a perpetual, worldwide license to use
  your contribution **under Apache 2.0** and, at the Company's
  discretion, **under other terms** (e.g. as part of a commercial
  license bundle sold to a third party).
- This dual licensing is what keeps the Project funded and
  sustainable.

---

## Compatibility summary

| Your context | What you need |
|---|---|
| Using the code in an internal research project | Apache 2.0 only |
| Using the code in a commercial SaaS | Apache 2.0 only (keep NOTICE) |
| Forking and rebranding under a new name (no "Alkebulan" / "Sekan") | Apache 2.0 only |
| Forking and keeping the name "Alkebulan AI" or "Sekan" | Apache 2.0 **+** written trademark license from Psalms23Wave LLC |
| Contributing back to the project | Apache 2.0 **+** accept [`CLA.md`](./CLA.md) |
| Embedding in a product that cannot ship a NOTICE file | Commercial license — see [`COMMERCIAL.md`](./COMMERCIAL.md) |
| Academic paper citing the work | Apache 2.0 + [`ATTRIBUTION.md`](./ATTRIBUTION.md) citation |

---

## Why this mix?

Because it is what the best open-source projects do:

- **Apache 2.0** — the license used by Kubernetes, TensorFlow,
  Airflow, Kafka, Mistral's base models, Meta's Llama 3, and
  Hugging Face's core libraries. Permissive, patent-granting,
  widely understood, enterprise-friendly.
- **Reserved trademarks** — the approach used by Linux®, Python®,
  Kubernetes®, Apache®, and Mozilla®. Open code, protected brand.
- **CLA** — the approach used by the Apache Software Foundation,
  Google, Meta, Microsoft, and the CNCF to keep their projects
  legally clean and sustainable.

There is no invention here. This is the battle-tested mainstream
model for a company-stewarded open-source project.

---

© 2025 Psalms23Wave LLC.
