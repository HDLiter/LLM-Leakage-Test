"""Score functions for `LogProbTrace` artifacts.

Every metric here reads only saved trace data — no model reruns, per
plan §5.2 step 6. The functions are deliberately pure (numpy + lists,
no I/O) so they can be unit-tested without GPU or vLLM.

Authority:
- plans/phase7-pilot-implementation.md §§5.2, 8.1A
- refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md §1 (E_CTS, E_PCSG)
- config/prompts/R5A_OPERATOR_SCHEMA.md §4.4

Naming:
- `compute_mink_pct`  Min-K%             — base bottom-K% logprob mean
- `compute_mink_pp`   Min-K%++           — position-normalized variant
- `compute_cts`       Calibrated Tail     — frequency-calibrated (stub)
                      Surprise (E_CTS feeder)
- `compute_pcsg`      Paired Cutoff       — late-vs-early logprob delta
                      Surprise Gap (E_PCSG)
"""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np

from ..contracts import LogProbTrace


# ---------------------------------------------------------------------------
# Min-K% (basic)
# ---------------------------------------------------------------------------


def compute_mink_pct(
    token_logprobs: Sequence[float], k_pct: float = 20.0
) -> float:
    """Mean logprob over the bottom-`k_pct`% of tokens.

    Lower (more negative) = the text contains more surprising tokens,
    which is the literature anchor for tail-surprise familiarity
    (Shi et al. Min-K% Prob, ICLR 2024). Returned in raw nats; callers
    that prefer a positive "surprise" magnitude should negate.
    """

    if not token_logprobs:
        raise ValueError("token_logprobs is empty")
    if not (0.0 < k_pct <= 100.0):
        raise ValueError(f"k_pct must be in (0, 100], got {k_pct}")

    arr = np.asarray(token_logprobs, dtype=np.float64)
    if not np.all(np.isfinite(arr)):
        raise ValueError("token_logprobs contains non-finite values")

    n = arr.size
    cutoff = max(1, math.ceil(n * k_pct / 100.0))
    bottom = np.partition(arr, cutoff - 1)[:cutoff]
    return float(np.mean(bottom))


# ---------------------------------------------------------------------------
# Min-K%++ (position-normalized; uses top-K alternative logprobs as a
# variance proxy, since vLLM only exposes top-K not full vocab)
# ---------------------------------------------------------------------------


def compute_mink_pp(
    token_logprobs: Sequence[float],
    top_logprobs: Sequence[Sequence[float]],
    k_pct: float = 20.0,
) -> float:
    """Position-normalized Min-K%++ approximation.

    For each token position `i`, treat the top-K alternative logprobs as
    a coarse sample of that position's vocabulary distribution; compute
    `mu_i`, `sigma_i` from them, and z-score the realized token logprob:

        z_i = (logprob_i - mu_i) / sigma_i

    Then average the bottom `k_pct`% z-scores. Approximates the
    Zhang et al. Min-K%++ (ICLR 2025) construction; the real metric
    requires full-vocab logits, which vLLM does not expose.
    """

    if len(token_logprobs) != len(top_logprobs):
        raise ValueError(
            f"token_logprobs/top_logprobs length mismatch: "
            f"{len(token_logprobs)} vs {len(top_logprobs)}"
        )
    if not token_logprobs:
        raise ValueError("token_logprobs is empty")

    z_scores = []
    for lp, top in zip(token_logprobs, top_logprobs, strict=True):
        if not top:
            continue  # cannot normalize without alternatives
        sample = np.asarray(top, dtype=np.float64)
        mu = sample.mean()
        sigma = sample.std(ddof=0)
        if sigma == 0.0:
            continue  # degenerate distribution; skip rather than divide by zero
        z_scores.append((lp - mu) / sigma)

    if not z_scores:
        raise ValueError(
            "no usable positions for Min-K%++ "
            "(all top_logprobs were empty or degenerate)"
        )

    arr = np.asarray(z_scores, dtype=np.float64)
    n = arr.size
    cutoff = max(1, math.ceil(n * k_pct / 100.0))
    bottom = np.partition(arr, cutoff - 1)[:cutoff]
    return float(np.mean(bottom))


# ---------------------------------------------------------------------------
# Calibrated Tail Surprise (E_CTS)
# ---------------------------------------------------------------------------


def compute_cts(
    trace: LogProbTrace,
    frequency_table: dict[int, float] | None,
) -> float:
    """Frequency-calibrated tail surprise.

    `frequency_table` is a mapping `token_id -> log p_unigram(token_id)`
    estimated from the CLS source corpus. CTS subtracts the unigram
    surprise from each token's model logprob before taking the bottom-K%
    mean, removing trivially-rare-character effects that inflate Min-K%.

    The frequency table is produced by WS0.5 / WS3 once the pilot
    manifest is frozen. Until then this function raises
    ``NotImplementedError``; callers should fall back to
    ``compute_mink_pct`` for pre-WS3 sanity checks.
    """

    if frequency_table is None:
        raise NotImplementedError(
            "compute_cts requires the corpus frequency table from WS3; "
            "use compute_mink_pct for pre-WS3 traces"
        )

    if len(trace.token_logprobs) != len(trace.raw_token_ids):
        raise ValueError(
            "trace token_logprobs and raw_token_ids have different lengths"
        )

    calibrated = []
    for tok_id, lp in zip(trace.raw_token_ids, trace.token_logprobs, strict=True):
        baseline = frequency_table.get(tok_id)
        if baseline is None:
            continue
        calibrated.append(lp - baseline)

    if not calibrated:
        raise ValueError(
            "frequency_table covered zero tokens in the trace; "
            "table likely built against a different tokenizer"
        )

    return compute_mink_pct(calibrated)


# ---------------------------------------------------------------------------
# Paired Cutoff Surprise Gap (E_PCSG)
# ---------------------------------------------------------------------------


def compute_pcsg(trace_late: LogProbTrace, trace_early: LogProbTrace) -> float:
    """Mean logprob difference (late - early) over the article.

    Plan §8.1A defines E_PCSG as paired logprob gap on tokenizer-matched
    temporal pairs. The two traces MUST come from the same tokenizer SHA
    (and therefore the same token IDs, same length) — otherwise the
    contrast is uninterpretable. We refuse to compute on mismatched
    inputs rather than silently aligning.
    """

    if trace_late.case_id != trace_early.case_id:
        raise ValueError(
            f"case_id mismatch: late={trace_late.case_id}, "
            f"early={trace_early.case_id}"
        )
    if trace_late.tokenizer_sha != trace_early.tokenizer_sha:
        raise ValueError(
            "tokenizer_sha mismatch — E_PCSG requires identical tokenizer; "
            f"late={trace_late.tokenizer_sha[:12]}..., "
            f"early={trace_early.tokenizer_sha[:12]}..."
        )
    if trace_late.raw_token_ids != trace_early.raw_token_ids:
        raise ValueError(
            "token IDs differ between paired traces despite tokenizer match; "
            "this should never happen — check for input-text drift or "
            "tokenizer config divergence"
        )

    late = np.asarray(trace_late.token_logprobs, dtype=np.float64)
    early = np.asarray(trace_early.token_logprobs, dtype=np.float64)
    return float(np.mean(late - early))


__all__ = [
    "compute_cts",
    "compute_mink_pct",
    "compute_mink_pp",
    "compute_pcsg",
]
