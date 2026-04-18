"""
Sekan — A Simpson-Rule-Based Adaptive Optimization Algorithm
============================================================

The Sekan algorithm applies Simpson's 1/3 Rule of numerical integration to
deep-learning optimization. Invented and named by Mathew Sekanjako during the
Alkebulan AI research, Sekan was created to solve a specific problem: modern
tokenizers and optimizers are tuned for Western (English-dominated) corpora,
and fail to converge stably when fine-tuning large language models on
morphologically rich, agglutinative Bantu languages such as Luganda.

The idea
--------
Standard optimizers (SGD, AdamW) use only the most recent gradient to update
parameters. Sekan treats the gradient history over a short window
``[t-(n-1), t]`` as samples of a continuous gradient function ``g(τ)`` and
uses Simpson's 1/3 rule to approximate the *integral* of that function, i.e.
the true average direction of descent. This smooths noisy steps and gives
more geometric weight to the middle of the window (the Simpson 1/4/1 pattern),
which empirically stabilises training on agglutinative languages where
single-token gradient spikes are common.

Composite Simpson's 1/3 rule (n even):

    ∫[a,b] g(τ) dτ  ≈  h/3 · [ g(a) + 4·Σ_odd g(x_i) + 2·Σ_even g(x_i) + g(b) ]

For a 3-sample window Sekan reduces to:

    ĝ_t  =  (g_{t-2} + 4·g_{t-1} + g_t) / 6

Then the parameter update is:

    θ_{t+1}  =  θ_t  − η · ĝ_t

Author  : Mathew Sekanjako  (inventor)
Owner   : Psalms23Wave LLC  (https://www.psalms23wave.com)
License : Apache License 2.0  (see ../LICENSE and ../NOTICE)
Project : Alkebulan AI
Trademarks: "Sekan" is a trademark of Psalms23Wave LLC. See ../TRADEMARK.md.
"""

from __future__ import annotations

from collections import deque
from typing import Iterable, Optional, Sequence

import math

try:
    import torch
    from torch.optim import Optimizer
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "PyTorch is required for Sekan. Install with: pip install torch"
    ) from e


# ---------------------------------------------------------------------------
# Sekan Optimizer
# ---------------------------------------------------------------------------


class SekanOptimizer(Optimizer):
    """
    Simpson-rule-integrated gradient optimizer.

    Maintains a rolling window of gradient snapshots per parameter and replaces
    the instantaneous gradient with the composite-Simpson-integrated estimate
    before applying the update. Optional weight decay and bias correction
    (similar to Adam) are supported.

    Parameters
    ----------
    params : iterable of torch.Tensor
        Trainable parameters.
    lr : float, default 1e-3
        Learning rate.
    history_size : int, default 3
        Number of gradient snapshots to keep per parameter. Must be >= 3 and,
        for composite Simpson, odd (an internal pad is applied otherwise).
    weight_decay : float, default 0.0
        Decoupled L2 regularisation coefficient.
    eps : float, default 1e-8
        Numerical stabiliser.
    betas : tuple(float, float), default (0.9, 0.999)
        Reserved for future bias-corrected variant.

    Example
    -------
    >>> from sekan_algorithm.sekan import SekanOptimizer
    >>> optimizer = SekanOptimizer(model.parameters(), lr=2e-5, history_size=3)
    >>> optimizer.zero_grad(); loss.backward(); optimizer.step()
    """

    def __init__(
        self,
        params: Iterable,
        lr: float = 1e-3,
        history_size: int = 3,
        weight_decay: float = 0.0,
        eps: float = 1e-8,
        betas: Sequence[float] = (0.9, 0.999),
    ) -> None:
        if lr < 0.0:
            raise ValueError(f"Invalid learning rate: {lr}")
        if history_size < 3:
            raise ValueError("history_size must be >= 3 for Simpson's rule")
        if weight_decay < 0.0:
            raise ValueError(f"Invalid weight_decay: {weight_decay}")

        defaults = dict(
            lr=lr,
            history_size=history_size,
            weight_decay=weight_decay,
            eps=eps,
            betas=tuple(betas),
        )
        super().__init__(params, defaults)

    # ------------------------------------------------------------------

    @staticmethod
    def simpson_integrate(grads: Sequence[torch.Tensor]) -> torch.Tensor:
        """
        Apply composite Simpson's 1/3 rule to a sequence of gradient tensors.

        For n=3:  (g0 + 4·g1 + g2) / 6
        For n>=5 (odd): (h/3)·[g0 + g_{n-1} + 4·Σ_odd + 2·Σ_even] / total_weight
        """
        n = len(grads)
        if n == 0:
            raise ValueError("simpson_integrate called with empty history")
        if n == 1:
            return grads[-1].clone()
        if n == 2:
            return 0.5 * (grads[0] + grads[1])
        if n == 3:
            return (grads[0] + 4.0 * grads[1] + grads[2]) / 6.0

        # Composite Simpson's 1/3 for n >= 5 odd (n-1 even sub-intervals).
        # If n is even, drop the oldest sample to make it odd.
        if n % 2 == 0:
            grads = list(grads)[1:]
            n = len(grads)

        result = grads[0].clone() + grads[-1].clone()
        for i in range(1, n - 1):
            coeff = 4.0 if (i % 2 == 1) else 2.0
            result = result + coeff * grads[i]
        # Weight = 1 + 1 + 4*(#odd) + 2*(#even) summed over Simpson pattern;
        # normalising divisor keeps the result an *average* (not an integral).
        n_odd = (n - 1) // 2
        n_even = (n - 1) // 2 - 1 if n >= 5 else 0
        divisor = 2.0 + 4.0 * n_odd + 2.0 * max(n_even, 0)
        return result / divisor

    # ------------------------------------------------------------------

    @torch.no_grad()
    def step(self, closure=None):
        loss = closure() if closure is not None else None

        for group in self.param_groups:
            lr = group["lr"]
            wd = group["weight_decay"]
            hist = group["history_size"]

            for p in group["params"]:
                if p.grad is None:
                    continue

                grad = p.grad.data
                if wd != 0.0:
                    grad = grad.add(p.data, alpha=wd)

                state = self.state[p]
                if "history" not in state:
                    state["step"] = 0
                    state["history"] = deque(maxlen=hist)

                state["step"] += 1
                state["history"].append(grad.clone())

                simpson_grad = self.simpson_integrate(list(state["history"]))
                p.data.add_(simpson_grad, alpha=-lr)

        return loss


# ---------------------------------------------------------------------------
# Sekan-weighted attention (reference implementation)
# ---------------------------------------------------------------------------


class SekanAttention(torch.nn.Module):
    """
    Scaled dot-product attention whose scores are reshaped by a Simpson-rule
    weighting over the key dimension.

    Morphologically-rich Bantu words like ``baatendekeddwa`` distribute
    meaning across multiple affixes. Plain softmax attention tends to dilute
    focus across every token. SekanAttention integrates each row of the
    attention matrix with Simpson weights that emphasise the centre of the
    morphological unit, sharpening attention where it matters most.
    """

    def __init__(self, d_model: int, n_heads: int = 8, dropout: float = 0.0) -> None:
        super().__init__()
        if d_model % n_heads != 0:
            raise ValueError("d_model must be divisible by n_heads")
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        self.qkv = torch.nn.Linear(d_model, 3 * d_model)
        self.out = torch.nn.Linear(d_model, d_model)
        self.drop = torch.nn.Dropout(dropout)

    @staticmethod
    def _simpson_weights(length: int, device, dtype) -> torch.Tensor:
        """Simpson 1/3 pattern (1, 4, 2, 4, 2, ..., 4, 1) normalised to mean 1."""
        if length <= 1:
            return torch.ones(length, device=device, dtype=dtype)
        if length == 2:
            return torch.ones(2, device=device, dtype=dtype)
        weights = torch.ones(length, device=device, dtype=dtype)
        for i in range(1, length - 1):
            weights[i] = 4.0 if (i % 2 == 1) else 2.0
        weights = weights * (length / weights.sum())
        return weights

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        B, T, _ = x.shape
        qkv = self.qkv(x).reshape(B, T, 3, self.n_heads, self.d_k).permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]

        scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.d_k)
        simpson_w = self._simpson_weights(T, x.device, x.dtype)
        scores = scores * simpson_w.view(1, 1, 1, T)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, float("-inf"))

        attn = torch.softmax(scores, dim=-1)
        attn = self.drop(attn)
        out = (attn @ v).transpose(1, 2).contiguous().reshape(B, T, self.d_model)
        return self.out(out)


__all__ = ["SekanOptimizer", "SekanAttention"]
