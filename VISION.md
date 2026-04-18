# VISION — A Tokenization and Optimization Framework for All African Languages

> **Founder & Inventor:** Mathew Sekanjako &nbsp;•&nbsp; **Owner:** Psalms23Wave LLC &nbsp;•&nbsp; **Project:** Alkebulan AI
> **Status:** v1 — Luganda proof delivered; generalisation roadmap active
> **License:** Apache License 2.0 (code) — see [`LICENSE`](./LICENSE) and [`NOTICE`](./NOTICE).
> *"Alkebulan AI"*, *"ABLT"*, and *"Sekan"* are trademarks of Psalms23Wave LLC ([`TRADEMARK.md`](./TRADEMARK.md)).

---

## TL;DR

ABLT v1 plus Sekan is **the first end-to-end demonstration** that a
morphologically-faithful tokenizer, combined with a numerically-
principled optimizer, can train a modern 7-billion-parameter Western
LLM on an African language without catastrophic tokenization loss,
without gradient divergence, and with lower final eval loss than the
AdamW baseline.

The result was produced on Luganda. Because the architecture factors
cleanly into a *language-specific symbolic layer* and a *language-
agnostic neural / optimization layer*, the same method transfers by
construction to the other ~800 million speakers of African languages
who are currently served by tokenizers built for English.

This document is the thesis statement for that claim.

---

## 1. The problem, stated precisely

Modern large language models are built on three components:

1. A **tokenizer** that maps raw bytes to a sequence of integer IDs.
2. A **neural architecture** (Transformer, decoder-only, etc.).
3. An **optimizer** that updates parameters given a loss gradient.

All three are trained, tuned, and empirically validated on corpora
that are **>90% English, <0.1% African**.  The practical consequence:

- Tokenizers shatter African-language words into 20–30 sub-pieces
  per sentence where English gets 8–12.  Context windows are burned,
  compute is wasted, and **the prefix–root–suffix morphology that
  carries the meaning is destroyed before the neural network ever
  sees the sentence.**
- Optimizers that rely on a recency-biased gradient moving average
  (Adam family) amplify the gradient spikes that agglutinative
  tokens produce, leading to loss plateaus, divergence, or outright
  training failure on low-resource African corpora.
- The published fine-tuning recipes that "just work" on English
  therefore **silently fail** on African languages, and the failure
  is attributed to the language ("low-resource", "hard to model")
  when it is in fact an artefact of the tokenizer and optimizer.

This is not a minor inefficiency. It is a **structural exclusion
of African languages from the modern AI stack**, concealed behind
the polite label "low-resource".

---

## 2. The hypothesis

> **H.** The tokenization and optimization problems of African
> languages are solvable by decoupling the *symbolic* knowledge of
> each language's morphology from the *statistical* sub-word model
> and the *numerical* optimization procedure, and re-designing each
> of the three layers on first principles.

If H holds, then one correctly-designed framework should deliver
competitive results across families as diverse as Bantu, Nilotic,
Cushitic, Afro-Asiatic, and Niger-Congo — because every one of those
families shares the property that drove the design (morphological
richness beyond what English-tuned subword models assume).

---

## 3. The framework — three decoupled layers

### 3.1 Layer 1 — Language-specific morphological rule layer

A symbolic, fully-transparent module that encodes a single language's
grammar:

- Noun-class system and concord prefixes (10–18 classes in Bantu,
  different prefixes for singular/plural).
- Verb affix inventory (tense, aspect, mood, negation, object-
  marker, applicative, causative, passive, reciprocal).
- Phonological rules (geminates, nasal compounds, semi-vowel
  compounds, vowel harmony, vowel-hiatus resolution).
- Loanword detector.

The layer outputs morpheme-boundary markers (`·`) inserted into the
text, which are converted to whitespace before the statistical
layer sees them. Implementation for Luganda:
[`tokenizer/ablt_tokenizer.py → EnhancedLugandaTokenizer`](./tokenizer/ablt_tokenizer.py).

**Key property:** this layer is **swap-in / swap-out**. A new
language requires only a new rule set (~a few hundred lines of
symbolic Python), not a new neural model.

### 3.2 Layer 2 — Universal statistical sub-word layer

A standard **SentencePiece Unigram** model, trained on a monolingual
corpus whose morpheme boundaries have already been exposed by
Layer 1. Because the boundaries are explicit, the Unigram MLE never
has to *guess* where a morpheme starts — it just picks an efficient
sub-word vocabulary inside each morpheme.

**Key property:** this layer is **identical** for every language.
Only its training data changes.

### 3.3 Layer 3 — Sekan numerical optimization

A new optimizer (`SekanOptimizer`) that replaces the instantaneous
gradient with a **Simpson-1/3-rule integral** of the last three
gradient snapshots per parameter:

$$
\hat{g}_t = \frac{g_{t-2} + 4\,g_{t-1} + g_t}{6}
$$

And an attention variant (`SekanAttention`) that applies the same
Simpson weighting along the key dimension of a Transformer block.

Full derivation and ablation study:
[`sekan_algorithm/FORMULA.md`](./sekan_algorithm/FORMULA.md).

**Key property:** Simpson's rule has $O(h^4)$ error versus $O(h^2)$
for trapezoidal averaging and a *symmetric* (not recency-biased)
weighting profile. Both properties are exactly what noisy long-token
gradient streams require. Language-agnostic.

---

## 4. What was proven on Luganda (v1)

| Claim | Number | Source |
|---|---:|---|
| Morpheme-boundary preservation | **100.00 %** | Validation notebook |
| Out-of-vocabulary rate | **0.00 %** | Validation notebook |
| Tokens per sentence (lower = better) | **11.4** vs 29.8 mBERT, 27.1 XLM-R | Validation notebook |
| Final eval loss (lower = better) | **4.9621** vs 5.0511 AdamW | Training log |
| Step-loss std-dev (lower = better) | **0.061** vs 0.143 AdamW | Training log |
| Divergence events (first 100 steps) | **0** vs 2 AdamW | Training log |
| Deployed artefact | `huggingface.co/Psalms23Wave/Alkebulan-AI` | Hugging Face |

Every entry in this table is backed by a runnable file in this
repository. See [`validation/METRICS.md`](./validation/METRICS.md).

**Interpretation.** On the exact same hardware (A100-SXM4-40GB),
with the exact same base model (Mistral-7B-v0.1) and the exact same
LoRA configuration (`r=8, α=32, dropout=0.1, 7 target modules`),
swapping (BPE + AdamW) for (ABLT + Sekan) turned a previously
unstable Luganda fine-tune into a stable, monotonically-converging,
lower-loss fine-tune. No other variable changed.

This is a falsifiable, reproducible empirical result.

---

## 5. Why the proof generalises

Three independent arguments support generalisation:

**(a) Structural.** Every African-language family listed below is
**more morphologically productive than English**. BPE and WordPiece
therefore mis-segment all of them for the same reason. The fix — a
symbolic morphology layer above a standard Unigram model — is
*exactly* what works for Luganda. The reason it works is not
Luganda-specific; it is a property of the architecture.

**(b) Numerical.** Sekan does not depend on any property of Luganda.
It is a pure numerical-analysis claim about the stability of
gradient averaging. It will behave identically on any language whose
gradient stream exhibits the same "long-token spike" pattern, which
is every agglutinative language.

**(c) Engineering.** Layer 1 (the language-specific module) is ~400
lines of symbolic Python for Luganda. Adding a new language is
therefore a **bounded, estimable** engineering task — not research.

---

## 6. Coverage map — what becomes possible

| Family | Representative languages | Approximate speakers |
|---|---|---:|
| Bantu (NE) | Luganda ✓, Lusoga, Runyankore, Rukiga, Rutooro | ~55 M |
| Bantu (E) | Swahili, Kikuyu, Kamba, Luhya, Chaga, Sukuma, Gikuyu | ~150 M |
| Bantu (C/S) | Kinyarwanda, Kirundi, Lingala, Kikongo, Chichewa, Shona, isiZulu, isiXhosa, Sesotho, Setswana, Tshivenda, Xitsonga | ~200 M |
| Nilotic | Acholi, Ateso, Dholuo, Maasai, Dinka, Nuer, Kalenjin | ~40 M |
| Cushitic | Somali, Oromo, Afar, Sidama | ~90 M |
| Afro-Asiatic (Ethio-Semitic) | Amharic, Tigrinya, Ge'ez (script-aware pre-tok) | ~60 M |
| Niger-Congo (West) | Bambara, Wolof, Yoruba, Igbo, Akan/Twi, Fon, Ewe | ~200 M |

**Addressable population: ~800 million** speakers whose languages
are either un-supported or *mis*-supported by the current-generation
NLP stack.

---

## 7. Why this matters beyond technical merit

A tokenizer is not a neutral object. It decides, before any neural
network sees a single weight update, what counts as a "word", what
counts as a "meaningful unit", and what counts as noise. When every
major open tokenizer treats Bantu morphology as noise, the resulting
models silently encode the claim that **African language structure
is not important enough to preserve**.

This is not acceptable as a technical state of affairs, and it is
not acceptable as a cultural one.

ABLT v1 plus Sekan is the first public piece of evidence that the
state of affairs can be changed — not by asking for politically-
motivated inclusion, but by doing the mathematical work to prove
that African-language structure is *preservable*, *learnable*, and
in fact **easier to model faithfully than English once you respect
its morphology**.

Everything needed to extend this proof to the other families
listed above is on this repository, documented, and released under
a permissive (non-commercial, attribution-preserving) license.

---

## 8. Research programme — prioritised roadmap

**v1 (shipped).** Luganda. Tokenizer, Sekan optimizer, fine-tuned
Mistral-7B deployed on Hugging Face.

**v2 (next 6 months).**
- Add rule layers for **Lusoga, Runyankore, Rukiga, Kinyarwanda,
  Swahili** (all Bantu — high structural similarity to Luganda).
- Train a single shared cross-Bantu SentencePiece vocabulary.
- Publish a standardised Bantu benchmark (5 languages × 5 tasks).
- Extend Sekan: confidence-weighted adaptive history window.

**v3 (12–18 months).**
- Non-Bantu African families: **Amharic (with Ge'ez script
  pre-tokeniser), Yoruba (with tone-mark preservation), Wolof,
  Somali**.
- Multi-rule composition for code-mixed (African-English,
  French-African) corpora — the dominant register across urban
  Africa.
- A unified entry point: `ABLT.from_pretrained("alkebulan/lg-UG")`.

**v4 (long-term).**
- Full instruction-tuned multi-lingual African LLM built on top of
  the v3 tokenizer family and Sekan.
- Public evaluation suite (tokenization, translation, QA, reasoning)
  covering every listed language.
- Peer-reviewed publication of the framework.

---

## 9. How to contribute

A new language can be added by providing, in order of importance:

1. A morphological rule file in the format of
   `EnhancedLugandaTokenizer.linguistic_features` (noun classes,
   verb affixes, phonology, loanwords).
2. A monolingual corpus of **50–200k sentences** for SentencePiece
   training.
3. Optionally, a parallel corpus (English ↔ target) for evaluation.

Everything else — the Unigram training pipeline, the Sekan optimizer,
the validation notebooks, the Hugging Face deployment scripts — is
already in this repository and works without modification.

---

## 10. Closing statement

Luganda was the first language I used to prove this framework. It
will not be the last. Every sentence in this document is either
already backed by a measurable result (§4) or a bounded, achievable
engineering step (§5, §8).

What was missing for African NLP was never the data, and it was
never the talent. What was missing was a single end-to-end proof
that the *modern* AI stack — 7-billion-parameter LLM, QLoRA
fine-tuning, deployed inference — can be made to respect African
morphology without breaking.

This repository is that proof.

---

### Citation

```bibtex
@misc{sekanjako2025alkebulan,
  title        = {Alkebulan: A Morphologically-Faithful Tokenization
                   and Simpson-Rule Optimization Framework for
                   African Languages},
  author       = {Sekanjako, Mathew},
  year         = {2025},
  howpublished = {Alkebulan AI Project, v1},
  url          = {https://huggingface.co/Psalms23Wave/Alkebulan-AI}
}
```
