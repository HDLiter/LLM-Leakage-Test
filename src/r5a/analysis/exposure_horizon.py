"""Path-E empirical exposure-horizon probe — analysis helpers.

Per `refine-logs/reviews/R5A_DESIGN_REVIEW_R2_20260429/DECISIONS.md`
decision #5 (rename of `cutoff_observed` → `exposure_horizon_observed`,
2026-04-30) and the original detector spec in
`docs/DECISION_20260427_pcsg_redefinition.md` §2.4 + Tier-0 #3
remediation in `refine-logs/reviews/R5A_DESIGN_REVIEW_20260427/SYNTHESIS.md`
(C1 / Statistical §3): take a temporally-stratified Min-K%++ score and
locate the breakpoint where the model's familiarity drops off sharply.
The breakpoint is the model's empirical training-data exposure horizon.

Method (replaces 2026-04-27 threshold-only detection per SYNTHESIS C1
remediation; threshold-only had 21-59% false-positive rate under
realistic monthly noise).

For each model:

  1. Fit a piecewise-linear-with-step model by WLS, parameterized by a
     breakpoint index κ ∈ {0, ..., n_months-1}. The breakpoint sits
     between months κ and κ+1, so months {0..κ} are "pre" and months
     {κ+1..n-1} are "post":

         score_t = α + γ·t + δ·I(t > κ) + λ·max(0, t - κ) + ε_t

     where t is month index (0..n-1) and weights are inverse variance
     (article count per month divided by within-month variance).

  2. Grid-search κ over indices with at least `min_side = 6` months
     on each side and pick the κ̂ minimising weighted sum of squares.

  3. Case-bootstrap: resample articles WITHIN each month with replacement,
     recompute per-month aggregator, refit κ̂ + δ̂ over the same grid.
     Repeat `B = 2000` times.

  4. Report κ̂, δ̂, 95% CIs, P(δ > drop_threshold) from bootstrap,
     and CI widths.

  5. Accept `horizon_observed = months_sorted[κ̂]` only if both:
       * horizon CI width ≤ 3 months, AND
       * drop CI lower bound > 0.05
     Otherwise mark horizon uncertain (horizon_observed = None) — the
     downstream §8.2 mixed model uses `cutoff_date_yaml` and simulates
     exposure misclassification per DECISION_20260427 §3.2 readback.

This module stays pure-numpy + stdlib; no statsmodels dependency.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date
from statistics import median
from typing import Callable

import numpy as np

from ..contracts import LogProbTrace
from .logprob_metrics import compute_mink_pct


@dataclass(frozen=True)
class ExposureHorizonEstimate:
    """Path E knee-detection result.

    `horizon_observed` is `None` when the run failed the acceptance rule
    (CI width > 3 months OR drop CI lower bound <= 0.05). Downstream code
    must treat `horizon_observed=None` as "exposure horizon uncertain"
    and fall back to `cutoff_date_yaml` for analysis.
    """

    model_id: str
    horizon_observed: date | None
    horizon_ci_lower: date | None
    horizon_ci_upper: date | None
    horizon_ci_width_months: int | None
    drop_magnitude: float  # δ̂ point estimate (positive = expected direction)
    drop_ci_lower: float | None
    drop_ci_upper: float | None
    p_drop_gt_threshold: float | None  # bootstrap fraction with δ > drop_threshold
    n_months: int
    n_articles: int
    kappa_hat_index: int | None  # κ̂ in 0..n_months-1 (last pre-cutoff month)
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


def _month_str_to_last_day(ym: str) -> date:
    """Return the last day of `YYYY-MM`."""
    y, m = (int(x) for x in ym.split("-"))
    if m == 12:
        return date(y, 12, 31)
    from datetime import timedelta

    return date(y, m + 1, 1) - timedelta(days=1)


def _piecewise_wls_fit(
    t: np.ndarray,
    y: np.ndarray,
    w: np.ndarray,
    kappa: float,
) -> tuple[np.ndarray, float]:
    """Fit `y ~ α + γ·t + δ·I(t > κ) + λ·max(0, t - κ)` by WLS.

    Returns `(beta, wss)`. `beta = [α, γ, δ, λ]`. `wss` is the weighted
    sum of squared residuals; np.inf on singular design.
    """
    n = t.size
    X = np.column_stack(
        [
            np.ones(n),
            t,
            (t > kappa).astype(np.float64),
            np.maximum(0.0, t - kappa),
        ]
    )
    Wy = w * y
    WX = w[:, None] * X
    XtWX = X.T @ WX
    XtWy = X.T @ Wy
    try:
        beta = np.linalg.solve(XtWX, XtWy)
    except np.linalg.LinAlgError:
        return np.zeros(4), float("inf")
    resid = y - X @ beta
    wss = float(np.sum(w * resid * resid))
    return beta, wss


def _grid_search_kappa(
    t: np.ndarray,
    y: np.ndarray,
    w: np.ndarray,
    *,
    min_side: int,
) -> tuple[int, float, np.ndarray]:
    """Grid-search the integer breakpoint index κ ∈ {min_side-1, ...,
    n - min_side - 1}. Return `(kappa_hat, wss_min, beta_hat)`.

    The breakpoint convention: κ is the *last pre-cutoff* month index;
    months {0..κ} are pre, months {κ+1..n-1} are post.
    """
    n = t.size
    lo = min_side - 1
    hi = n - min_side - 1
    if hi < lo:
        return -1, float("inf"), np.zeros(4)
    best_k = lo
    best_wss = float("inf")
    best_beta = np.zeros(4)
    for k in range(lo, hi + 1):
        beta, wss = _piecewise_wls_fit(t, y, w, kappa=float(k) + 0.5)
        if wss < best_wss:
            best_wss = wss
            best_k = k
            best_beta = beta
    return best_k, best_wss, best_beta


def _aggregate(
    by_month: dict[str, list[float]],
    months_sorted: list[str],
    aggregator: Callable[[Sequence[float]], float],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return `(t, y, w)` for the WLS fit.

    `y[i]` is the per-month aggregate score, `w[i]` is `n_articles_i /
    var_i` (inverse variance, weighted by article count). Months with
    n=1 fall back to mean-of-pooled variance to avoid division by zero.
    """
    n = len(months_sorted)
    t = np.arange(n, dtype=np.float64)
    y = np.zeros(n, dtype=np.float64)
    counts = np.zeros(n, dtype=np.float64)
    variances = np.zeros(n, dtype=np.float64)
    pooled = []
    for i, m in enumerate(months_sorted):
        scores = by_month[m]
        counts[i] = len(scores)
        if scores:
            y[i] = float(aggregator(scores))
            if len(scores) >= 2:
                variances[i] = float(np.var(scores, ddof=1))
                pooled.extend(scores)
            else:
                variances[i] = float("nan")
        else:
            y[i] = float("nan")
            variances[i] = float("nan")
    if not pooled or all(np.isnan(variances)):
        pooled_var = 1.0
    else:
        pooled_var = max(float(np.var(pooled, ddof=1)), 1e-9)
    # fill singletons / zero-var with pooled variance to keep weights finite
    for i in range(n):
        if not np.isfinite(variances[i]) or variances[i] <= 0.0:
            variances[i] = pooled_var
    w = counts / variances
    return t, y, w


def _bootstrap_kappa(
    by_month: dict[str, list[float]],
    months_sorted: list[str],
    aggregator: Callable[[Sequence[float]], float],
    *,
    min_side: int,
    n_bootstrap: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Case-bootstrap κ̂ and δ̂. Return `(kappas, drops)` with shape
    `(n_bootstrap,)` each. Resample articles WITHIN month with
    replacement, recompute aggregator, refit grid κ.
    """
    kappas = np.empty(n_bootstrap, dtype=np.int64)
    drops = np.empty(n_bootstrap, dtype=np.float64)
    n = len(months_sorted)
    pre_drawn = {m: np.asarray(by_month[m], dtype=np.float64) for m in months_sorted}
    for b in range(n_bootstrap):
        # Resample articles within each month
        boot_by_month: dict[str, list[float]] = {}
        for m in months_sorted:
            arr = pre_drawn[m]
            if arr.size == 0:
                boot_by_month[m] = []
                continue
            idx = rng.integers(0, arr.size, size=arr.size)
            boot_by_month[m] = arr[idx].tolist()
        # Refit
        if any(len(boot_by_month[m]) == 0 for m in months_sorted):
            kappas[b] = -1
            drops[b] = 0.0
            continue
        t, y, w = _aggregate(boot_by_month, months_sorted, aggregator)
        # Replace any NaN aggregate with the global mean (rare with
        # bootstrap when month has at least 1 article)
        if not np.all(np.isfinite(y)):
            mask = np.isfinite(y)
            if not mask.any():
                kappas[b] = -1
                drops[b] = 0.0
                continue
            y[~mask] = float(y[mask].mean())
        k, _wss, beta = _grid_search_kappa(t, y, w, min_side=min_side)
        if k < 0:
            kappas[b] = -1
            drops[b] = 0.0
            continue
        kappas[b] = k
        # Drop in the desired direction = pre - post = -δ; we report
        # the positive "drop" magnitude. β = [α, γ, δ, λ]; δ is the
        # step at the breakpoint, post minus pre. So drop = -δ.
        drops[b] = float(-beta[2])
    return kappas, drops


def detect_exposure_horizon(
    by_month: dict[str, list[float]],
    *,
    model_id: str,
    aggregator: Callable[[Sequence[float]], float] = median,
    min_side: int = 6,
    n_bootstrap: int = 2000,
    drop_threshold: float = 0.05,
    max_ci_width_months: int = 3,
    seed: int = 20260417,
) -> ExposureHorizonEstimate:
    """Piecewise-WLS knee detection with bootstrap CI.

    Returns an `ExposureHorizonEstimate` with `horizon_observed` populated
    only when CI width <= `max_ci_width_months` AND drop CI lower bound
    > `drop_threshold`. All other CI / point-estimate fields are
    populated whenever a fit was possible (so callers can publish the
    uncertain estimate as a caveat).
    """
    months_sorted = sorted(by_month)
    if not months_sorted:
        return ExposureHorizonEstimate(
            model_id=model_id,
            horizon_observed=None,
            horizon_ci_lower=None,
            horizon_ci_upper=None,
            horizon_ci_width_months=None,
            drop_magnitude=0.0,
            drop_ci_lower=None,
            drop_ci_upper=None,
            p_drop_gt_threshold=None,
            n_months=0,
            n_articles=0,
            kappa_hat_index=None,
            notes="no data",
        )

    n_months = len(months_sorted)
    n_articles = sum(len(by_month[m]) for m in months_sorted)
    if n_months < 2 * min_side:
        return ExposureHorizonEstimate(
            model_id=model_id,
            horizon_observed=None,
            horizon_ci_lower=None,
            horizon_ci_upper=None,
            horizon_ci_width_months=None,
            drop_magnitude=0.0,
            drop_ci_lower=None,
            drop_ci_upper=None,
            p_drop_gt_threshold=None,
            n_months=n_months,
            n_articles=n_articles,
            kappa_hat_index=None,
            notes=(
                f"too few months ({n_months}) for piecewise fit with "
                f"min_side={min_side}; need at least {2 * min_side}"
            ),
        )

    t, y, w = _aggregate(by_month, months_sorted, aggregator)
    if not np.all(np.isfinite(y)):
        return ExposureHorizonEstimate(
            model_id=model_id,
            horizon_observed=None,
            horizon_ci_lower=None,
            horizon_ci_upper=None,
            horizon_ci_width_months=None,
            drop_magnitude=0.0,
            drop_ci_lower=None,
            drop_ci_upper=None,
            p_drop_gt_threshold=None,
            n_months=n_months,
            n_articles=n_articles,
            kappa_hat_index=None,
            notes="some months had no articles; refusing to impute for point fit",
        )

    kappa_hat, _wss, beta_hat = _grid_search_kappa(t, y, w, min_side=min_side)
    if kappa_hat < 0:
        return ExposureHorizonEstimate(
            model_id=model_id,
            horizon_observed=None,
            horizon_ci_lower=None,
            horizon_ci_upper=None,
            horizon_ci_width_months=None,
            drop_magnitude=0.0,
            drop_ci_lower=None,
            drop_ci_upper=None,
            p_drop_gt_threshold=None,
            n_months=n_months,
            n_articles=n_articles,
            kappa_hat_index=None,
            notes="grid search produced no admissible κ",
        )

    drop_hat = float(-beta_hat[2])

    rng = np.random.default_rng(seed)
    kappa_boots, drop_boots = _bootstrap_kappa(
        by_month,
        months_sorted,
        aggregator,
        min_side=min_side,
        n_bootstrap=n_bootstrap,
        rng=rng,
    )
    valid = kappa_boots >= 0
    if valid.sum() < max(50, n_bootstrap // 20):
        return ExposureHorizonEstimate(
            model_id=model_id,
            horizon_observed=None,
            horizon_ci_lower=None,
            horizon_ci_upper=None,
            horizon_ci_width_months=None,
            drop_magnitude=drop_hat,
            drop_ci_lower=None,
            drop_ci_upper=None,
            p_drop_gt_threshold=None,
            n_months=n_months,
            n_articles=n_articles,
            kappa_hat_index=int(kappa_hat),
            notes=(
                f"bootstrap valid in {int(valid.sum())}/{n_bootstrap} replicates; "
                "too unstable to publish CIs"
            ),
        )

    kappa_v = kappa_boots[valid]
    drop_v = drop_boots[valid]
    k_lo = int(np.percentile(kappa_v, 2.5))
    k_hi = int(np.percentile(kappa_v, 97.5))
    drop_lo = float(np.percentile(drop_v, 2.5))
    drop_hi = float(np.percentile(drop_v, 97.5))
    p_drop = float(np.mean(drop_v > drop_threshold))
    ci_width = k_hi - k_lo

    horizon_lower = _month_str_to_last_day(months_sorted[max(0, k_lo)])
    horizon_upper = _month_str_to_last_day(
        months_sorted[min(n_months - 1, k_hi)]
    )
    kappa_date = _month_str_to_last_day(months_sorted[int(kappa_hat)])

    accept = (ci_width <= max_ci_width_months) and (drop_lo > drop_threshold)
    if accept:
        return ExposureHorizonEstimate(
            model_id=model_id,
            horizon_observed=kappa_date,
            horizon_ci_lower=horizon_lower,
            horizon_ci_upper=horizon_upper,
            horizon_ci_width_months=ci_width,
            drop_magnitude=drop_hat,
            drop_ci_lower=drop_lo,
            drop_ci_upper=drop_hi,
            p_drop_gt_threshold=p_drop,
            n_months=n_months,
            n_articles=n_articles,
            kappa_hat_index=int(kappa_hat),
            notes="ok",
        )
    reasons: list[str] = []
    if ci_width > max_ci_width_months:
        reasons.append(
            f"CI width {ci_width} months > {max_ci_width_months}"
        )
    if drop_lo <= drop_threshold:
        reasons.append(
            f"drop CI lower {drop_lo:.4f} <= {drop_threshold}"
        )
    return ExposureHorizonEstimate(
        model_id=model_id,
        horizon_observed=None,
        horizon_ci_lower=horizon_lower,
        horizon_ci_upper=horizon_upper,
        horizon_ci_width_months=ci_width,
        drop_magnitude=drop_hat,
        drop_ci_lower=drop_lo,
        drop_ci_upper=drop_hi,
        p_drop_gt_threshold=p_drop,
        n_months=n_months,
        n_articles=n_articles,
        kappa_hat_index=int(kappa_hat),
        notes="rejected: " + "; ".join(reasons),
    )


__all__ = [
    "ExposureHorizonEstimate",
    "detect_exposure_horizon",
    "month_stratified_mink",
]
