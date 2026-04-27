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
# Paired Cutoff Surprise Gap (E_PCSG) — registry-driven (2026-04-27)
# ---------------------------------------------------------------------------


def _eligible_for_pair(trace: LogProbTrace, max_token_id_inclusive: int) -> bool:
    """Vocab-intersection eligibility check for cross-version PCSG pairs.

    The 2026-04-27 PCSG redefinition allows pairs whose tokenizer
    classes match but vocabs differ in extension tokens (e.g. Qwen2.5
    vs Qwen3). Articles whose tokenization triggers any token ID above
    the pair-declared ceiling break alignment and must be excluded.
    """
    if not trace.raw_token_ids:
        return False
    return max(trace.raw_token_ids) <= max_token_id_inclusive


def compute_pcsg(
    trace_late: LogProbTrace,
    trace_early: LogProbTrace,
    *,
    max_token_id_inclusive: int | None = None,
) -> float:
    """Mean logprob difference (late - early) over a PCSG pair.

    Plan §8.1A + 2026-04-27 amendment (`docs/DECISION_20260427_pcsg_redefinition.md`):
    - Same `case_id` (paired observation).
    - Both traces' `raw_token_ids` must satisfy the pair's
      `max_token_id_inclusive` rule (vocab intersection).
    - Token IDs must match position-by-position (this is a hard
      tokenization-alignment requirement, not just shared vocab).
    - The two tokenizer SHAs may differ (cross-version pair) AS LONG AS
      both share the same tokenizer class — checked at the YAML
      `tokenizer_compat` level by the operator before this is called.

    Returns the mean of `(logprob_late - logprob_early)` over matched
    tokens. Positive values mean the late model is more familiar.
    """

    if trace_late.case_id != trace_early.case_id:
        raise ValueError(
            f"case_id mismatch: late={trace_late.case_id}, "
            f"early={trace_early.case_id}"
        )

    if max_token_id_inclusive is not None:
        for label, trace in (("late", trace_late), ("early", trace_early)):
            if not _eligible_for_pair(trace, max_token_id_inclusive):
                raise ValueError(
                    f"trace {label}.case_id={trace.case_id!r} contains a "
                    f"token ID > {max_token_id_inclusive}; ineligible for "
                    f"this PCSG pair (vocab-intersection violation)"
                )

    if trace_late.raw_token_ids != trace_early.raw_token_ids:
        raise ValueError(
            "token IDs differ between paired traces; cross-version pairs "
            "still require position-aligned IDs in the intersection vocab. "
            "Check for input-text drift or tokenizer-class divergence."
        )

    late = np.asarray(trace_late.token_logprobs, dtype=np.float64)
    early = np.asarray(trace_early.token_logprobs, dtype=np.float64)
    return float(np.mean(late - early))


def compute_pcsg_capacity_curve(
    traces_by_case_and_model: dict[tuple[str, str], LogProbTrace],
    params_by_model: dict[str, int],
    *,
    max_token_id_inclusive: int | None = None,
) -> list[dict[str, float | str | int]]:
    """One-row-per-(case, model) tidy table for capacity-curve regression.

    Inputs:
      - `traces_by_case_and_model[(case_id, model_id)]` -> LogProbTrace
      - `params_by_model[model_id]` -> total parameter count (e.g. 1.5e9, 7e9)

    Output: list of dicts with keys
      `case_id, model_id, params, log2_params, mean_logprob`.
    Use this output to fit `mean_logprob ~ β · log2(params) + ε` as
    OLS or a mixed-effects regression with case_id as random intercept.

    Cutoff is held fixed *across the input* (caller is responsible for
    only including same-cutoff models in the regression — typically one
    model family at a time).
    """

    if not traces_by_case_and_model:
        return []

    rows: list[dict[str, float | str | int]] = []
    for (case_id, model_id), trace in traces_by_case_and_model.items():
        if model_id not in params_by_model:
            raise ValueError(f"params_by_model is missing entry for {model_id!r}")
        if (
            max_token_id_inclusive is not None
            and not _eligible_for_pair(trace, max_token_id_inclusive)
        ):
            continue  # skip ineligible cases for this curve
        params = int(params_by_model[model_id])
        if params <= 0:
            raise ValueError(f"non-positive params for {model_id!r}: {params}")
        mean_lp = float(np.mean(trace.token_logprobs))
        rows.append(
            {
                "case_id": case_id,
                "model_id": model_id,
                "params": params,
                "log2_params": math.log2(params),
                "mean_logprob": mean_lp,
            }
        )

    return rows


__all__ = [
    "compute_cts",
    "compute_mink_pct",
    "compute_mink_pp",
    "compute_pcsg",
    "compute_pcsg_capacity_curve",
]
