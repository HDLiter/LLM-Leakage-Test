"""Unit tests for src.r5a.analysis.logprob_metrics."""

from __future__ import annotations

import math
from datetime import datetime, timezone

import pytest

from src.r5a.analysis.logprob_metrics import (
    compute_cts,
    compute_mink_pct,
    compute_mink_pp,
    compute_pcsg,
    compute_pcsg_capacity_curve,
)
from src.r5a.contracts import LogProbTrace, RequestFingerprint, SeedSupport


# ---------------------------------------------------------------------------
# compute_mink_pct
# ---------------------------------------------------------------------------


def test_mink_pct_basic():
    # logprobs: -1, -2, -3, -4, -5  (5 tokens)
    # bottom 20% = 1 token => -5.0
    # bottom 40% = 2 tokens => mean(-5, -4) = -4.5
    logprobs = [-1.0, -2.0, -3.0, -4.0, -5.0]
    assert compute_mink_pct(logprobs, k_pct=20.0) == -5.0
    assert compute_mink_pct(logprobs, k_pct=40.0) == pytest.approx(-4.5)


def test_mink_pct_unsorted_input_handled():
    logprobs = [-3.0, -1.0, -5.0, -2.0, -4.0]  # same set, shuffled
    assert compute_mink_pct(logprobs, k_pct=20.0) == -5.0


def test_mink_pct_at_least_one_token():
    # 100 tokens, k=0.5% would round down to 0 — must round up to 1
    logprobs = [-(i + 1) for i in range(100)]
    assert compute_mink_pct(logprobs, k_pct=0.5) == -100.0


def test_mink_pct_rejects_empty():
    with pytest.raises(ValueError, match="empty"):
        compute_mink_pct([])


def test_mink_pct_rejects_bad_k():
    with pytest.raises(ValueError, match="k_pct"):
        compute_mink_pct([-1.0, -2.0], k_pct=0.0)
    with pytest.raises(ValueError, match="k_pct"):
        compute_mink_pct([-1.0, -2.0], k_pct=120.0)


def test_mink_pct_rejects_nonfinite():
    with pytest.raises(ValueError, match="non-finite"):
        compute_mink_pct([-1.0, math.nan, -3.0])


# ---------------------------------------------------------------------------
# compute_mink_pp
# ---------------------------------------------------------------------------


def test_mink_pp_position_normalization():
    # two positions, top-K=2 alternatives each
    # position 0: realized=-2, alts=[-1, -3]  -> mu=-2, sigma=1, z=0
    # position 1: realized=-5, alts=[-4, -6]  -> mu=-5, sigma=1, z=0
    # bottom-50% of [0, 0] => mean = 0
    out = compute_mink_pp(
        token_logprobs=[-2.0, -5.0],
        top_logprobs=[[-1.0, -3.0], [-4.0, -6.0]],
        k_pct=50.0,
    )
    assert out == pytest.approx(0.0)


def test_mink_pp_low_z_is_more_surprising():
    # Realized token is far below the alternative distribution
    out = compute_mink_pp(
        token_logprobs=[-10.0],
        top_logprobs=[[-1.0, -2.0]],  # mu=-1.5, sigma=0.5
        k_pct=100.0,
    )
    assert out < 0  # z = (-10 - -1.5)/0.5 = -17


def test_mink_pp_skips_degenerate_positions():
    # position 1 has zero variance among alternatives -> skipped
    out = compute_mink_pp(
        token_logprobs=[-2.0, -5.0],
        top_logprobs=[[-1.0, -3.0], [-5.0, -5.0]],
        k_pct=100.0,
    )
    # only position 0 contributes; z = ( -2 - -2 ) / 1 = 0
    assert out == pytest.approx(0.0)


def test_mink_pp_length_mismatch():
    with pytest.raises(ValueError, match="length mismatch"):
        compute_mink_pp([-1.0, -2.0], [[-0.5, -1.5]])


# ---------------------------------------------------------------------------
# compute_pcsg
# ---------------------------------------------------------------------------


def _make_trace(
    *,
    case_id: str = "v3_h_001",
    model_id: str = "qwen2.5-7b",
    tokenizer_sha: str = "tok-abc",
    raw_token_ids: list[int] | None = None,
    token_logprobs: list[float] | None = None,
) -> LogProbTrace:
    if raw_token_ids is None:
        raw_token_ids = [101, 202, 303, 404]
    if token_logprobs is None:
        token_logprobs = [-1.0, -2.0, -3.0, -4.0]
    return LogProbTrace(
        case_id=case_id,
        model_id=model_id,
        tokenizer_family="qwen",
        tokenizer_sha=tokenizer_sha,
        hf_commit_sha="hf-xyz",
        quant_scheme="AWQ-INT4",
        article_token_count=len(token_logprobs),
        raw_token_ids=raw_token_ids,
        token_logprobs=token_logprobs,
        thinking_mode="off",
        backend="vllm_completion",
        fingerprint=RequestFingerprint(
            provider="vllm",
            model_id=model_id,
            ts=datetime.now(timezone.utc),
            seed_supported=SeedSupport.YES,
        ),
    )


def test_pcsg_paired_gap():
    early = _make_trace(model_id="qwen2.5-7b")
    late = _make_trace(
        model_id="qwen2.5-14b",
        token_logprobs=[-0.5, -1.0, -2.5, -3.5],  # uniformly higher
    )
    gap = compute_pcsg(trace_late=late, trace_early=early)
    # mean( (-0.5,-1.0,-2.5,-3.5) - (-1,-2,-3,-4) ) = mean(0.5, 1, 0.5, 0.5) = 0.625
    assert gap == pytest.approx(0.625)


def test_pcsg_allows_cross_version_tokenizer_sha():
    # 2026-04-27 amendment: tokenizer SHAs may differ across pair members
    # (Qwen2.5 vs Qwen3) provided token IDs match position-by-position
    # within the declared vocab intersection.
    early = _make_trace(tokenizer_sha="qwen25-sha")
    late = _make_trace(tokenizer_sha="qwen3-sha")
    out = compute_pcsg(trace_late=late, trace_early=early)
    assert out == 0.0  # identical logprobs in fixture


def test_pcsg_rejects_token_above_intersection_ceiling():
    # Probe article tokenized to an extension token (151665+) cannot be
    # cross-version-paired; PCSG must refuse.
    early = _make_trace(raw_token_ids=[101, 202, 303, 404])
    late = _make_trace(raw_token_ids=[101, 202, 303, 404])
    # base call passes
    out = compute_pcsg(trace_late=late, trace_early=early, max_token_id_inclusive=500)
    assert out == 0.0
    # but if any ID exceeds the ceiling, raise
    early_bad = _make_trace(raw_token_ids=[101, 202, 303, 151667])
    late_bad = _make_trace(raw_token_ids=[101, 202, 303, 151667])
    with pytest.raises(ValueError, match="vocab-intersection violation"):
        compute_pcsg(
            trace_late=late_bad,
            trace_early=early_bad,
            max_token_id_inclusive=151664,
        )


def test_pcsg_rejects_case_id_mismatch():
    early = _make_trace(case_id="v3_h_001")
    late = _make_trace(case_id="v3_h_002")
    with pytest.raises(ValueError, match="case_id mismatch"):
        compute_pcsg(trace_late=late, trace_early=early)


def test_pcsg_rejects_token_id_drift():
    early = _make_trace(raw_token_ids=[1, 2, 3, 4])
    late = _make_trace(raw_token_ids=[1, 2, 3, 5])
    with pytest.raises(ValueError, match="token IDs differ"):
        compute_pcsg(trace_late=late, trace_early=early)


# ---------------------------------------------------------------------------
# compute_cts
# ---------------------------------------------------------------------------


def test_cts_without_freq_table_raises():
    trace = _make_trace()
    with pytest.raises(NotImplementedError, match="frequency table"):
        compute_cts(trace, frequency_table=None)


def test_cts_with_freq_table_subtracts_baseline():
    # token logprobs = [-1, -2, -3, -4]; baseline = [-0.5, -0.5, -0.5, -0.5]
    # calibrated = [-0.5, -1.5, -2.5, -3.5]
    # bottom 25% (1 token) = -3.5
    trace = _make_trace()
    freq = {101: -0.5, 202: -0.5, 303: -0.5, 404: -0.5}
    out = compute_cts(trace, frequency_table=freq)
    assert out == pytest.approx(-3.5)


def test_cts_rejects_zero_overlap_freq_table():
    trace = _make_trace()
    with pytest.raises(ValueError, match="zero tokens"):
        compute_cts(trace, frequency_table={9999: -0.1})


# ---------------------------------------------------------------------------
# compute_pcsg_capacity_curve (added 2026-04-27)
# ---------------------------------------------------------------------------


def test_capacity_curve_basic():
    # Two cases × three model sizes within Qwen2.5 family.
    # mean_logprob hand-set so the regression has a non-trivial slope.
    rows = compute_pcsg_capacity_curve(
        traces_by_case_and_model={
            ("c1", "qwen2.5-3b"): _make_trace(case_id="c1", model_id="qwen2.5-3b", token_logprobs=[-3.0, -3.0, -3.0, -3.0]),
            ("c1", "qwen2.5-7b"): _make_trace(case_id="c1", model_id="qwen2.5-7b", token_logprobs=[-2.0, -2.0, -2.0, -2.0]),
            ("c1", "qwen2.5-14b"): _make_trace(case_id="c1", model_id="qwen2.5-14b", token_logprobs=[-1.5, -1.5, -1.5, -1.5]),
            ("c2", "qwen2.5-3b"): _make_trace(case_id="c2", model_id="qwen2.5-3b", token_logprobs=[-2.5, -2.5, -2.5, -2.5]),
            ("c2", "qwen2.5-7b"): _make_trace(case_id="c2", model_id="qwen2.5-7b", token_logprobs=[-1.8, -1.8, -1.8, -1.8]),
            ("c2", "qwen2.5-14b"): _make_trace(case_id="c2", model_id="qwen2.5-14b", token_logprobs=[-1.2, -1.2, -1.2, -1.2]),
        },
        params_by_model={
            "qwen2.5-3b": 3_000_000_000,
            "qwen2.5-7b": 7_000_000_000,
            "qwen2.5-14b": 14_000_000_000,
        },
    )
    assert len(rows) == 6
    # log2(params) and mean_logprob should both be present and positive log scale
    for r in rows:
        assert r["log2_params"] > 30  # billions span this region
        assert r["mean_logprob"] < 0  # logprobs are negative


def test_capacity_curve_skips_ineligible_under_intersection():
    rows = compute_pcsg_capacity_curve(
        traces_by_case_and_model={
            ("c1", "qwen2.5-7b"): _make_trace(
                case_id="c1", raw_token_ids=[100, 200, 300, 400]
            ),
            ("c1", "qwen3-8b"): _make_trace(
                case_id="c1", raw_token_ids=[100, 200, 300, 151667]  # extension
            ),
        },
        params_by_model={"qwen2.5-7b": 7_000_000_000, "qwen3-8b": 8_000_000_000},
        max_token_id_inclusive=151664,
    )
    # Only the qwen2.5-7b row survives the intersection guard
    assert len(rows) == 1
    assert rows[0]["model_id"] == "qwen2.5-7b"


def test_capacity_curve_rejects_missing_params():
    with pytest.raises(ValueError, match="params_by_model is missing"):
        compute_pcsg_capacity_curve(
            traces_by_case_and_model={
                ("c1", "qwen2.5-3b"): _make_trace(),
            },
            params_by_model={},  # empty
        )
