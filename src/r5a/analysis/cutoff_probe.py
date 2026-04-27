"""Path-E empirical cutoff probe — analysis helpers.

Per `docs/DECISION_20260427_pcsg_redefinition.md` §2.4: take a
temporally-stratified Min-K% score, compute the month-vs-score curve
per model, and locate the "knee" where the model's familiarity drops
off sharply. The knee is interpreted as the model's empirical
training-data horizon.

Method (intentionally minimal — we don't need a state-of-the-art
change-point detector for a sanity check):

  1. For each (model, month) bucket, take the median Min-K% (per
     `compute_mink_pct`) across articles in that bucket.
  2. Smooth the resulting time series with a 3-month moving median to
     suppress single-month outliers (financial-news volume varies).
  3. Brute-force search every candidate breakpoint position; pick the
     one that maximizes the difference between left-side and right-side
     mean scores AND has a left-side mean >= a small epsilon larger
     than the right-side mean (so the inflection direction matches the
     "model knows pre-cutoff better" prior). Return the breakpoint's
     month as `cutoff_observed`, plus the magnitude of the drop.

The function is deterministic given input scores and tolerates missing
months (skipped from the smoothed series).
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from statistics import median
from typing import NamedTuple

import numpy as np

from ..contracts import LogProbTrace
from .logprob_metrics import compute_mink_pct


class CutoffEstimate(NamedTuple):
    model_id: str
    cutoff_observed: date | None  # None when knee detection is inconclusive
    pre_score_mean: float
    post_score_mean: float
    drop_magnitude: float  # pre - post (positive = expected direction)
    n_months: int
    knee_index: int | None
    notes: str


def month_stratified_mink(
    traces: Iterable[LogProbTrace],
    publish_dates: dict[str, date],
    *,
    k_pct: float = 20.0,
) -> dict[str, list[float]]:
    """Group traces by `YYYY-MM` (extracted from publish_dates[case_id])
    and return Min-K% scores per month. Each month's list contains one
    score per article. Lower (more negative) = more surprising = less
    familiar."""
    by_month: dict[str, list[float]] = {}
    for trace in traces:
        pd = publish_dates.get(trace.case_id)
        if pd is None:
            continue
        if not trace.token_logprobs:
            continue
        ym = f"{pd.year:04d}-{pd.month:02d}"
        score = compute_mink_pct(trace.token_logprobs, k_pct=k_pct)
        by_month.setdefault(ym, []).append(score)
    return by_month


def _moving_median(series: list[float], window: int) -> list[float]:
    if window <= 1:
        return list(series)
    half = window // 2
    out: list[float] = []
    for i in range(len(series)):
        lo = max(0, i - half)
        hi = min(len(series), i + half + 1)
        out.append(median(series[lo:hi]))
    return out


def _knee_at_breakpoint(smoothed: list[float], min_left: int = 3, min_right: int = 3):
    """Pick the breakpoint position k that maximizes
    `mean(smoothed[:k]) - mean(smoothed[k:])`, subject to having at least
    `min_left` and `min_right` observations on each side."""
    n = len(smoothed)
    if n < min_left + min_right:
        return None, 0.0, 0.0, 0.0
    arr = np.asarray(smoothed, dtype=np.float64)
    best_k: int | None = None
    best_drop = -np.inf
    best_left = 0.0
    best_right = 0.0
    for k in range(min_left, n - min_right + 1):
        left = float(arr[:k].mean())
        right = float(arr[k:].mean())
        drop = left - right
        if drop > best_drop:
            best_drop = drop
            best_k = k
            best_left = left
            best_right = right
    return best_k, best_drop, best_left, best_right


def detect_cutoff(
    by_month: dict[str, list[float]],
    *,
    model_id: str,
    smoothing_window: int = 3,
    min_drop_magnitude: float = 0.05,
    aggregator=median,
) -> CutoffEstimate:
    """Knee-detect on month-aggregated scores. Returns a `CutoffEstimate`.

    Inputs:
      - `by_month["YYYY-MM"]` -> list of Min-K% scores
    """
    months_sorted = sorted(by_month)
    if not months_sorted:
        return CutoffEstimate(
            model_id=model_id,
            cutoff_observed=None,
            pre_score_mean=float("nan"),
            post_score_mean=float("nan"),
            drop_magnitude=0.0,
            n_months=0,
            knee_index=None,
            notes="no data",
        )

    # Min-K% returns negative values (logprobs); we treat HIGHER (less
    # negative) as "more familiar" so the pre-cutoff side should have
    # higher scores.
    series = [float(aggregator(by_month[m])) for m in months_sorted]
    smoothed = _moving_median(series, window=smoothing_window)

    knee_k, drop, left, right = _knee_at_breakpoint(smoothed)
    if knee_k is None:
        return CutoffEstimate(
            model_id=model_id,
            cutoff_observed=None,
            pre_score_mean=float("nan"),
            post_score_mean=float("nan"),
            drop_magnitude=0.0,
            n_months=len(months_sorted),
            knee_index=None,
            notes="too few months to compute knee",
        )

    if drop < min_drop_magnitude:
        return CutoffEstimate(
            model_id=model_id,
            cutoff_observed=None,
            pre_score_mean=left,
            post_score_mean=right,
            drop_magnitude=drop,
            n_months=len(months_sorted),
            knee_index=knee_k,
            notes=(
                f"drop={drop:.3f} < min_drop_magnitude={min_drop_magnitude:.3f}; "
                "no robust knee"
            ),
        )

    # Convert breakpoint index to a calendar date: the cutoff is the
    # last month BEFORE the inflection (right-side scores reflect
    # post-cutoff behavior).
    cutoff_month_str = months_sorted[knee_k - 1]
    y, m = (int(x) for x in cutoff_month_str.split("-"))
    # Use the last day of that month as the cutoff date.
    if m == 12:
        last = date(y, 12, 31)
    else:
        first_of_next = date(y, m + 1, 1)
        last = date(first_of_next.year, first_of_next.month, 1)
        last = date(last.year, last.month, 1).replace(day=1)
        # last day of m: subtract 1 day from first of next month
        from datetime import timedelta

        last = first_of_next - timedelta(days=1)
    return CutoffEstimate(
        model_id=model_id,
        cutoff_observed=last,
        pre_score_mean=left,
        post_score_mean=right,
        drop_magnitude=drop,
        n_months=len(months_sorted),
        knee_index=knee_k,
        notes="ok",
    )


__all__ = [
    "CutoffEstimate",
    "detect_cutoff",
    "month_stratified_mink",
]
