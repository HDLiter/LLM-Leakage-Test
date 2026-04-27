"""Roundtrip tests for `LogProbTrace` Parquet persistence."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.r5a.contracts import LogProbTrace, RequestFingerprint, SeedSupport
from src.r5a.operators.p_logprob import (
    read_traces_parquet,
    trace_summary,
    write_traces_parquet,
)


def _trace(
    *,
    case_id: str,
    model_id: str = "qwen2.5-7b",
    response_id: str | None = "resp-1",
) -> LogProbTrace:
    return LogProbTrace(
        case_id=case_id,
        model_id=model_id,
        tokenizer_family="qwen",
        tokenizer_sha="tok-abcdef",
        hf_commit_sha="hf-123456",
        article_token_count=3,
        raw_token_ids=[10, 20, 30],
        token_logprobs=[-1.5, -2.25, -0.75],
        thinking_mode="off",
        backend="vllm_completion",
        fingerprint=RequestFingerprint(
            provider="vllm",
            model_id=model_id,
            system_fingerprint="sf-xyz",
            response_id=response_id,
            route_hint="auto",
            ts=datetime(2026, 4, 26, 12, 0, 0, tzinfo=timezone.utc),
            seed_requested=42,
            seed_supported=SeedSupport.YES,
            seed_effective=True,
        ),
    )


def test_parquet_roundtrip_single(tmp_path: Path):
    src = [_trace(case_id="case_A")]
    out = tmp_path / "qwen2.5-7b.parquet"
    write_traces_parquet(src, out)
    assert out.exists()
    loaded = read_traces_parquet(out)
    assert len(loaded) == 1
    a = src[0]
    b = loaded[0]
    assert a.case_id == b.case_id
    assert a.raw_token_ids == b.raw_token_ids
    assert a.token_logprobs == pytest.approx(b.token_logprobs)
    assert a.fingerprint.response_id == b.fingerprint.response_id
    assert a.fingerprint.seed_supported == b.fingerprint.seed_supported


def test_parquet_roundtrip_many(tmp_path: Path):
    src = [_trace(case_id=f"case_{i}", response_id=f"r-{i}") for i in range(5)]
    out = tmp_path / "many.parquet"
    write_traces_parquet(src, out)
    loaded = read_traces_parquet(out)
    assert [t.case_id for t in loaded] == [t.case_id for t in src]
    assert [t.fingerprint.response_id for t in loaded] == [
        t.fingerprint.response_id for t in src
    ]


def test_parquet_handles_null_optional_fields(tmp_path: Path):
    src = [_trace(case_id="case_A", response_id=None)]
    out = tmp_path / "with_nulls.parquet"
    write_traces_parquet(src, out)
    loaded = read_traces_parquet(out)
    assert loaded[0].fingerprint.response_id is None


def test_write_rejects_empty(tmp_path: Path):
    with pytest.raises(ValueError, match="no traces"):
        write_traces_parquet([], tmp_path / "x.parquet")


def test_trace_summary_aggregates_per_model():
    a = _trace(case_id="c1", model_id="qwen2.5-7b")
    b = _trace(case_id="c2", model_id="qwen2.5-7b")
    c = _trace(case_id="c3", model_id="qwen2.5-14b")
    summary = trace_summary([a, b, c])
    assert summary["n"] == 3
    assert set(summary["by_model"].keys()) == {"qwen2.5-7b", "qwen2.5-14b"}
    assert summary["by_model"]["qwen2.5-7b"]["n"] == 2
    assert summary["by_model"]["qwen2.5-7b"]["thinking_off_pct"] == 100.0
    assert summary["by_model"]["qwen2.5-14b"]["n"] == 1
