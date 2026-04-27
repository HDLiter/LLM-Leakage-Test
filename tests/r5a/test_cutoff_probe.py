"""Unit tests for src.r5a.analysis.cutoff_probe."""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from src.r5a.analysis.cutoff_probe import (
    detect_cutoff,
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


def test_detect_cutoff_finds_clear_drop():
    # 12 months: first 6 strong (high logprobs / low surprise),
    # last 6 weak. Knee should fall around index 6.
    by_month = {}
    for i in range(12):
        ym = f"2024-{i + 1:02d}"
        score = -1.0 if i < 6 else -3.0  # negative; higher = more familiar
        by_month[ym] = [score] * 5
    est = detect_cutoff(by_month, model_id="qwen2.5-7b", min_drop_magnitude=0.5)
    assert est.cutoff_observed is not None
    assert est.knee_index == 6
    # Cutoff falls in the LAST month before the knee (=2024-06)
    assert est.cutoff_observed.year == 2024
    assert est.cutoff_observed.month == 6
    assert est.drop_magnitude == pytest.approx(2.0)


def test_detect_cutoff_returns_none_on_flat_series():
    # No monotone drop -> no robust knee
    by_month = {f"2024-{i + 1:02d}": [-1.5] * 5 for i in range(8)}
    est = detect_cutoff(by_month, model_id="qwen2.5-7b", min_drop_magnitude=0.1)
    assert est.cutoff_observed is None
    assert est.knee_index is not None  # the algorithm picked a tie-break index
    assert est.drop_magnitude == pytest.approx(0.0, abs=1e-9)


def test_detect_cutoff_too_few_months():
    by_month = {f"2024-0{i + 1}": [-1.0] for i in range(3)}
    est = detect_cutoff(by_month, model_id="qwen2.5-7b")
    assert est.cutoff_observed is None
    assert est.knee_index is None
    assert "too few months" in est.notes


def test_detect_cutoff_no_data():
    est = detect_cutoff({}, model_id="qwen2.5-7b")
    assert est.cutoff_observed is None
    assert est.n_months == 0
