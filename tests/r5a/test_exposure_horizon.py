"""Unit tests for src.r5a.analysis.exposure_horizon.

Updated 2026-04-29 (Tier-0 #3): the threshold-only knee detector was
replaced by piecewise-WLS + bootstrap CI. The point-estimate side of
the API is retained (kappa_hat_index, drop_magnitude) but with new
semantics; CI fields and acceptance rules are new.

Renamed 2026-04-30 (R2 DECISIONS.md decision #5): the Path-E knee
detector and its outputs were renamed from `cutoff` to
`exposure_horizon`. The detector function is now
`detect_exposure_horizon` and its result type is
`ExposureHorizonEstimate`.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

import numpy as np
import pytest

from src.r5a.analysis.exposure_horizon import (
    detect_exposure_horizon,
    month_stratified_mink,
)
from src.r5a.contracts import LogProbTrace, RequestFingerprint, SeedSupport


def _trace(case_id: str, logprobs: list[float]) -> LogProbTrace:
    return LogProbTrace(
        case_id=case_id,
        model_id="qwen2.5-7b",
        tokenizer_family="qwen",
        tokenizer_sha="tok-x",
        hf_commit_sha="hf-x",
        quant_scheme="AWQ-INT4",
        article_token_count=len(logprobs),
        raw_token_ids=list(range(100, 100 + len(logprobs))),
        token_logprobs=logprobs,
        thinking_mode="off",
        backend="vllm_completion",
        fingerprint=RequestFingerprint(
            provider="vllm",
            model_id="qwen2.5-7b",
            ts=datetime.now(timezone.utc),
            seed_supported=SeedSupport.YES,
        ),
    )


def _make_step_series(
    n_months: int,
    knee_after_index: int,
    pre_score: float,
    post_score: float,
    n_per_month: int,
    noise_sd: float,
    seed: int,
    start_year: int = 2023,
    start_month: int = 1,
) -> dict[str, list[float]]:
    """Build a `by_month` dict with a clean step at `knee_after_index`
    (so months {0..knee_after_index} are pre, the rest are post)."""
    rng = np.random.default_rng(seed)
    by_month: dict[str, list[float]] = {}
    for i in range(n_months):
        # absolute year/month from offset
        y = start_year + (start_month - 1 + i) // 12
        m = (start_month - 1 + i) % 12 + 1
        ym = f"{y:04d}-{m:02d}"
        center = pre_score if i <= knee_after_index else post_score
        noise = rng.normal(0.0, noise_sd, size=n_per_month)
        by_month[ym] = (center + noise).tolist()
    return by_month


def test_month_stratified_mink_returns_expected_per_article_scores():
    """MED-6 / Tier-R2-0 PR2 step 6: numerical anchor for the
    `month_stratified_mink` aggregator. Existing tests only checked
    month-key membership and per-month counts, which would also pass if
    the function returned arbitrary numeric values (or, for example,
    accidentally returned mean-logprob instead of bottom-k% mean).

    Construction: four 5-token traces with hand-chosen logprobs and
    `k_pct=40.0`, so the per-article Min-K% reduces to the mean of the
    two most-negative tokens (cutoff = ceil(5 * 0.4) = 2). The
    expected per-article scores are therefore deterministic and have
    no floating-point round-off slack worth speaking of:

        c1 [-1, -2, -3, -4, -5]            -> mean(-5, -4) = -4.5
        c2 [-2, -2, -2, -2, -2]            -> mean(-2, -2) = -2.0
        c3 [-1, -1, -10, -10, -1]          -> mean(-10, -10) = -10.0
        c4 [-3, -7, -1, -5, -2]            -> mean(-7, -5) = -6.0
    """
    traces = [
        _trace("c1", [-1.0, -2.0, -3.0, -4.0, -5.0]),
        _trace("c2", [-2.0, -2.0, -2.0, -2.0, -2.0]),
        _trace("c3", [-1.0, -1.0, -10.0, -10.0, -1.0]),
        _trace("c4", [-3.0, -7.0, -1.0, -5.0, -2.0]),
    ]
    publish_dates = {
        "c1": date(2024, 1, 10),
        "c2": date(2024, 1, 20),
        "c3": date(2024, 2, 1),
        "c4": date(2024, 2, 28),
    }
    by_month = month_stratified_mink(traces, publish_dates, k_pct=40.0)
    assert sorted(by_month.keys()) == ["2024-01", "2024-02"]
    assert by_month["2024-01"] == pytest.approx([-4.5, -2.0])
    assert by_month["2024-02"] == pytest.approx([-10.0, -6.0])


def test_month_stratified_groups_by_yyyy_mm():
    traces = [
        _trace("c1", [-1.0] * 5),
        _trace("c2", [-2.0] * 5),
        _trace("c3", [-3.0] * 5),
    ]
    publish_dates = {
        "c1": date(2024, 1, 15),
        "c2": date(2024, 1, 28),
        "c3": date(2024, 2, 5),
    }
    by_month = month_stratified_mink(traces, publish_dates, k_pct=100.0)
    assert set(by_month.keys()) == {"2024-01", "2024-02"}
    assert len(by_month["2024-01"]) == 2
    assert len(by_month["2024-02"]) == 1


def test_detect_exposure_horizon_accepts_clean_step():
    """24 months with a clean -1 → -3 step at month 11 (so horizon =
    2023-12). Drop = 2.0, well above threshold; CI should be tight."""
    by_month = _make_step_series(
        n_months=24,
        knee_after_index=11,
        pre_score=-1.0,
        post_score=-3.0,
        n_per_month=20,
        noise_sd=0.05,
        seed=42,
    )
    est = detect_exposure_horizon(
        by_month,
        model_id="qwen2.5-7b",
        n_bootstrap=200,  # keep tests fast
    )
    assert est.horizon_observed is not None, est.notes
    # Horizon month is the LAST pre-cutoff month → 2023-12
    assert est.horizon_observed.year == 2023
    assert est.horizon_observed.month == 12
    assert est.kappa_hat_index == 11
    # Drop magnitude is positive (pre - post) — ~2.0 with noise wiggle
    assert est.drop_magnitude == pytest.approx(2.0, abs=0.15)
    # Bootstrap CIs populated
    assert est.horizon_ci_width_months is not None
    assert est.horizon_ci_width_months <= 3
    assert est.drop_ci_lower is not None and est.drop_ci_lower > 0.05
    assert est.p_drop_gt_005 is not None and est.p_drop_gt_005 > 0.95


def test_detect_exposure_horizon_rejects_flat_series():
    """No drop → fit returns δ ≈ 0; drop CI lower bound below 0.05;
    horizon_observed must be None."""
    by_month = _make_step_series(
        n_months=18,
        knee_after_index=8,
        pre_score=-1.5,
        post_score=-1.5,
        n_per_month=15,
        noise_sd=0.05,
        seed=123,
    )
    est = detect_exposure_horizon(by_month, model_id="qwen2.5-7b", n_bootstrap=200)
    assert est.horizon_observed is None
    assert "rejected" in est.notes
    assert est.drop_magnitude == pytest.approx(0.0, abs=0.05)


def test_detect_exposure_horizon_rejects_high_noise_wide_ci():
    """Even with a true step, very high month-level noise should give a
    wide CI; horizon_observed must be None per max_ci_width_months=3
    rule."""
    # SD = 0.5 with a step of 0.3 → most bootstrap draws will move κ̂
    # by many months. n_per_month=8 (typical pilot density).
    by_month = _make_step_series(
        n_months=20,
        knee_after_index=9,
        pre_score=-1.0,
        post_score=-1.3,
        n_per_month=8,
        noise_sd=0.5,
        seed=7,
    )
    est = detect_exposure_horizon(
        by_month,
        model_id="qwen2.5-7b",
        n_bootstrap=300,
        max_ci_width_months=3,
    )
    assert est.horizon_observed is None
    assert "CI width" in est.notes or "drop CI lower" in est.notes


def test_detect_exposure_horizon_too_few_months():
    by_month = {f"2024-{i + 1:02d}": [-1.0, -1.1] for i in range(8)}
    est = detect_exposure_horizon(by_month, model_id="qwen2.5-7b", min_side=6)
    assert est.horizon_observed is None
    assert est.kappa_hat_index is None
    assert "too few months" in est.notes


def test_detect_exposure_horizon_no_data():
    est = detect_exposure_horizon({}, model_id="qwen2.5-7b")
    assert est.horizon_observed is None
    assert est.n_months == 0
    assert est.notes == "no data"


def test_detect_exposure_horizon_records_n_articles():
    by_month = _make_step_series(
        n_months=14,
        knee_after_index=6,
        pre_score=-0.8,
        post_score=-2.0,
        n_per_month=10,
        noise_sd=0.05,
        seed=2,
    )
    est = detect_exposure_horizon(by_month, model_id="qwen2.5-7b", n_bootstrap=150)
    assert est.n_months == 14
    assert est.n_articles == 14 * 10


def test_detect_exposure_horizon_clean_step_exact_ci_bounds():
    """Numerical anchor for the piecewise-WLS detector after the rename.

    A clean -1 → -3 step over 24 months at month 11 (so horizon is
    2023-12) with low noise should produce a tight CI that brackets
    the true breakpoint within ±1 month and an `drop_ci_lower`
    comfortably above the 0.05 threshold.
    """
    by_month = _make_step_series(
        n_months=24,
        knee_after_index=11,
        pre_score=-1.0,
        post_score=-3.0,
        n_per_month=20,
        noise_sd=0.05,
        seed=42,
    )
    est = detect_exposure_horizon(
        by_month, model_id="qwen2.5-7b", n_bootstrap=300
    )
    assert est.horizon_observed is not None, est.notes
    assert est.horizon_observed.year == 2023
    assert est.horizon_observed.month == 12
    # CI must be tight (≤ 3 months) and contain December 2023.
    assert est.horizon_ci_width_months is not None
    assert est.horizon_ci_width_months <= 3
    assert est.horizon_ci_lower is not None
    assert est.horizon_ci_upper is not None
    assert est.horizon_ci_lower <= date(2023, 12, 31) <= est.horizon_ci_upper
    # Drop CI lower bound MUST exceed the default 0.05 threshold by a
    # large margin (true δ ≈ 2.0).
    assert est.drop_ci_lower is not None and est.drop_ci_lower > 1.5
