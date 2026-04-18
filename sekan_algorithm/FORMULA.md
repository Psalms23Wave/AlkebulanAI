# The Sekan Algorithm — Mathematical Formulation

> A Simpson-rule-based adaptive optimizer and attention re-weighter designed
> for low-resource, morphologically-rich African languages.
>
> **Author:** Mathew Sekanjako (inventor)
> **Owner:** Psalms23Wave LLC — [psalms23wave.com](https://www.psalms23wave.com)
> **Project:** Alkebulan AI
> **License:** Apache License 2.0 (code) — see [`../LICENSE`](../LICENSE) and [`../NOTICE`](../NOTICE).
> *"Sekan"* is a trademark of Psalms23Wave LLC; see [`../TRADEMARK.md`](../TRADEMARK.md).
> **Status:** Empirically validated on Mistral-7B + LoRA fine-tuning for Luganda

---

## 1. Why Sekan exists — the problem

When I first tried to fine-tune a modern LLM (Mistral-7B) on Luganda, every
standard recipe failed in the same three ways:

1. **Tokenizer mis-segmentation.** Public tokenizers (BPE, mBERT, XLM-R,
   SentencePiece trained on the web) are fit on Western, predominantly
   English corpora. When applied to agglutinative Bantu words such as
   `Abanoonyiboobubudamu` ("refugees"), they produce arbitrary sub-word
   splits that destroy the prefix–root–suffix structure that *carries* the
   meaning. The model sees noise rather than signal.
2. **Gradient volatility.** Bantu language tokens are long and carry
   bursts of morphological information. Training on them produces
   gradient vectors whose magnitude spikes unpredictably step-to-step,
   derailing any optimizer that reacts to the *latest* gradient.
3. **Attention dilution.** Over a long agglutinated word, standard
   softmax attention spreads its probability mass thinly. The model
   cannot decide which morpheme is "the verb root" versus
   "the passive-perfect suffix".

Adam-family optimizers solve (2) partially using exponential moving
averages, but EMAs are geometrically biased toward the most recent
gradients — the very gradients that spike most. I needed an average
that was **geometrically weighted toward the centre** of the window, not
toward the end.

Numerical analysis already solves this: it is called **Simpson's 1/3
rule**. I adapted it into an optimizer, and later into an attention
re-weighter. I named the method **Sekan**.

---

## 2. Simpson's 1/3 Rule — the building block

Simpson's 1/3 rule approximates a definite integral by fitting a
parabola through three equally-spaced samples:

$$
\int_{a}^{b} f(x)\, dx \;\approx\; \frac{h}{3}\Big[f(x_0) + 4 f(x_1) + f(x_2)\Big]
\qquad h = \frac{b-a}{2}
$$

For $n$ samples (even number of sub-intervals), the **composite**
Simpson's 1/3 rule is:

$$
\int_{a}^{b} f(x)\, dx \;\approx\;
\frac{h}{3}\Big[ f(x_0) + f(x_n) + 4\!\!\sum_{i \text{ odd}}\!\! f(x_i) + 2\!\!\sum_{i \text{ even}}\!\! f(x_i) \Big]
$$

The error term is $O(h^4)$, which is why Simpson outperforms the
trapezoidal rule by orders of magnitude on smooth functions.

---

## 3. Sekan — gradient update rule

Treat the stream of gradient snapshots $\{g_{t-(n-1)},\dots, g_{t-1}, g_t\}$
as discrete samples of an (unknown) continuous gradient function
$g(\tau)$.  The *true* descent direction is the mean of $g(\tau)$ over
the window — i.e. its integral divided by the window length.  Sekan
estimates this integral via composite Simpson's rule.

### 3.1 Three-sample Sekan (default)

$$
\boxed{\;\hat{g}_t \;=\; \dfrac{g_{t-2} + 4\,g_{t-1} + g_t}{6}\;}
$$

The parameter update is then:

$$
\theta_{t+1} = \theta_t - \eta\, \hat{g}_t
$$

- $g_{t-1}$ (the mid-point sample) receives **weight 4**.
- End-points receive **weight 1** each.
- Divisor $6 = 1 + 4 + 1$ keeps $\hat{g}_t$ on the same scale as any
  single $g_i$.

### 3.2 General $n$-sample Sekan (odd $n \geq 3$)

$$
\hat{g}_t \;=\; \frac{1}{W}\left[g_0 + g_{n-1} + 4\!\!\sum_{i\,\text{odd}}\!\! g_i + 2\!\!\sum_{i\,\text{even}}\!\! g_i\right]
$$

with normalisation $W = 2 + 4\lfloor(n-1)/2\rfloor + 2(\lfloor(n-1)/2\rfloor - 1)$,
so that $\hat{g}_t$ remains a proper weighted *average*, not an
(integral-scale) sum. If $n$ is even, the oldest sample is dropped to
restore odd parity.

### 3.3 With weight decay

$$
\theta_{t+1} = \theta_t - \eta\,\big(\hat{g}_t + \lambda\,\theta_t\big)
$$

Decoupled L2 (following AdamW's convention) — applied **after**
Simpson integration, not inside the running window.

---

## 4. Why this helps — the three intuitions

### 4.1 Geometric centring beats recency bias
Adam-family EMAs are of the form $\bar{g}_t = \beta \bar{g}_{t-1} + (1-\beta)g_t$.
Expanding this recurrence, the most recent gradient contributes with weight
$(1-\beta) \approx 0.1$ while the 10th-most-recent contributes only
$(1-\beta)\beta^9 \approx 0.035$ — a **monotonically decaying** influence
profile. Sekan instead produces a **symmetric, bowl-shaped** weight profile
(1, 4, 1) whose peak is in the middle of the window. Transient spikes on
the latest gradient are damped rather than amplified. This matches the
empirical gradient behaviour of long Bantu tokens, where spikes typically
occur at the boundaries of a morphological unit and the centre of the
unit carries the stable signal.

### 4.2 Provably 4th-order accurate
Simpson's 1/3 rule has $O(h^4)$ global error on smooth integrands,
whereas trapezoidal averaging (the closest classical analogue) is
only $O(h^2)$. In gradient terms, Sekan's estimate of the true
descent direction is one order of magnitude more accurate per step
when the underlying gradient trajectory is locally smooth.

### 4.3 Parameter-free stability
Sekan exposes exactly two hyper-parameters: `lr` and `history_size`.
There is no $\beta_1$, $\beta_2$, $\epsilon$ tuning dance. Three is
the minimum Simpson window (one parabola), and in practice
`history_size=3` works from the first step. This is crucial in
low-resource contexts where practitioners cannot afford massive HPO
sweeps.

---

## 5. Sekan-Attention (bonus application)

The same Simpson weighting can be applied across the sequence
dimension of an attention head. Given query/key matrices
$Q, K \in \mathbb{R}^{T \times d_k}$, the standard score matrix is

$$
S = \frac{QK^\top}{\sqrt{d_k}} \in \mathbb{R}^{T\times T}.
$$

Define the **Simpson weight vector** along the key axis as
$\mathbf{w} = (w_0, w_1, \dots, w_{T-1})$ where

$$
w_i = \begin{cases} 1 & i = 0 \text{ or } i = T-1 \\ 4 & i \text{ odd} \\ 2 & i \text{ even}, 0 < i < T-1 \end{cases}
$$

normalised so that $\sum_i w_i = T$ (preserves expected attention mass).
Sekan-Attention computes

$$
\widetilde{S}_{ij} = S_{ij} \cdot w_j,\qquad
A = \operatorname{softmax}\big(\widetilde{S}\big),\qquad
Z = A V.
$$

This sharpens attention towards the Simpson-weighted *interior* of a
token sequence, which for agglutinated Bantu words is precisely where
the root morpheme lives. The implementation is in
[`sekan.py`](./sekan.py) under `SekanAttention`.

---

## 6. Reference implementation

A ready-to-use PyTorch optimizer lives alongside this document:

```python
from sekan_algorithm.sekan import SekanOptimizer

optimizer = SekanOptimizer(
    model.parameters(),
    lr=2e-5,          # training LR for LoRA fine-tuning
    history_size=3,   # one Simpson parabola
    weight_decay=0.01,
)

for batch in dataloader:
    loss = model(**batch).loss
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
```

The entire Sekan update (after backward) is ~30 lines of Python;
the fully-commented version is in `sekan.py`.

---

## 7. What Sekan solves (TL;DR)

| Problem | Classical fix | What Sekan does |
|---|---|---|
| Gradient spikes on long Bantu tokens | Clip gradients at a magnitude threshold | Softly averages them away with a 4× weight on the *middle* of the window |
| Unstable early training on small corpora | Very small LR, many warmup steps | Damps variance from step 1 via Simpson integration; no warmup needed |
| EMAs biased toward latest noisy gradients | Adam $\beta_2 = 0.999$ | Symmetric 1/4/1 Simpson profile — noise at the ends cancels by construction |
| Attention dilution across agglutinated word | None in standard Transformer | `SekanAttention` sharpens to the interior morpheme |
| Hyper-parameter tuning in a low-resource setting | Costly HPO sweeps | Two knobs only: `lr`, `history_size` |

---

## 8. Empirical validation

See `validation/METRICS.md` for the full benchmark table. Highlights:

- **Tokenizer (ABLT):** 100% morpheme-boundary preservation, 0% OOV on a
  99-sentence stratified Luganda validation set.
- **Optimizer (Sekan):** used to fine-tune Mistral-7B + QLoRA on Luganda;
  eval loss dropped monotonically from 5.0136 (step 200) to 4.9621
  (step 600) and onward. No training instability, no divergence.

---

## 9. Citation

If you use Sekan in your work, please cite it as:

```bibtex
@misc{sekanjako2025sekan,
  title        = {Sekan: A Simpson-Rule-Based Adaptive Optimizer for
                   Low-Resource African Language Modelling},
  author       = {Sekanjako, Mathew},
  year         = {2025},
  howpublished = {Alkebulan AI Project},
  url          = {https://huggingface.co/Psalms23Wave/Alkebulan-AI}
}
```
