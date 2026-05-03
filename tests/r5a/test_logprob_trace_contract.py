"""Contract tests for LogProbTrace closure fields."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from scripts import ws1_finalize_run_manifest as finalize
from src.r5a.contracts import LogProbTrace, RequestFingerprint, SeedSupport
from src.r5a.operators.p_logprob import read_traces_parquet, write_traces_parquet


def _trace(
    *,
    top_logprobs: list[list[float]] | None = None,
    hidden_states_uri: str | None = None,
) -> LogProbTrace:
    return LogProbTrace(
        case_id="case_001",
        model_id="qwen2.5-7b",
        tokenizer_family="qwen",
        tokenizer_sha="tok-x",
        hf_commit_sha="hf-x",
        quant_scheme="AWQ-INT4",
        weight_dtype="int4",
        vllm_image_digest="sha256:" + "a" * 64,
        article_token_count=3,
        raw_token_ids=[101, 102, 103],
        token_logprobs=[-1.0, -2.0, -3.0],
        top_logprobs=top_logprobs,
        top_logprobs_k=2 if top_logprobs is not None else 0,
        hidden_states_uri=hidden_states_uri,
        thinking_mode="off",
        backend="vllm_completion",
        fingerprint=RequestFingerprint(
            provider="vllm",
            model_id="qwen2.5-7b",
            ts=datetime(2026, 5, 3, 12, 0, 0, tzinfo=timezone.utc),
            seed_supported=SeedSupport.YES,
        ),
    )


def test_pydantic_round_trip_all_closure_fields_populated():
    src = _trace(
        top_logprobs=[[-0.5, -1.5], [-1.5, -2.5], [-2.5, -3.5]],
        hidden_states_uri="data/pilot/hidden_states/case_001.safetensors",
    )
    payload = src.model_dump(mode="json")
    loaded = LogProbTrace.model_validate(payload)
    assert loaded.quant_scheme == "AWQ-INT4"
    assert loaded.weight_dtype == "int4"
    assert loaded.vllm_image_digest.startswith("sha256:")
    assert loaded.top_logprobs == src.top_logprobs
    assert loaded.hidden_states_uri == src.hidden_states_uri


def test_pydantic_round_trip_optional_fields_none():
    src = _trace(top_logprobs=None, hidden_states_uri=None)
    payload = src.model_dump(mode="json")
    loaded = LogProbTrace.model_validate(payload)
    assert loaded.top_logprobs is None
    assert loaded.hidden_states_uri is None


def test_parquet_round_trip_closure_fields(tmp_path: Path):
    src = [
        _trace(
            top_logprobs=[[-0.5, -1.5], [-1.5, -2.5], [-2.5, -3.5]],
            hidden_states_uri="data/pilot/hidden_states/case_001.safetensors",
        )
    ]
    path = tmp_path / "trace.parquet"
    write_traces_parquet(src, path)
    loaded = read_traces_parquet(path)
    assert len(loaded) == 1
    assert loaded[0].weight_dtype == "int4"
    assert loaded[0].vllm_image_digest == src[0].vllm_image_digest
    assert loaded[0].top_logprobs == src[0].top_logprobs
    assert loaded[0].hidden_states_uri == src[0].hidden_states_uri


def test_finalize_gate_fails_when_required_trace_field_missing(tmp_path: Path):
    traces_dir = tmp_path / "traces"
    traces_dir.mkdir()
    pq.write_table(
        pa.table(
            {
                "case_id": ["case_001"],
                "quant_scheme": ["AWQ-INT4"],
                # weight_dtype intentionally missing
                "vllm_image_digest": ["sha256:" + "a" * 64],
            }
        ),
        traces_dir / "qwen2.5-7b__pilot.parquet",
    )
    with pytest.raises(SystemExit, match="LogProbTrace contract"):
        finalize._validate_traces_dir(
            traces_dir,
            ["qwen2.5-7b"],
            mode="confirmatory",
            expected_n_articles=1,
        )


def test_finalize_gate_allows_optional_trace_fields_missing(tmp_path: Path):
    traces_dir = tmp_path / "traces"
    traces_dir.mkdir()
    pq.write_table(
        pa.table(
            {
                "case_id": ["case_001"],
                "quant_scheme": ["AWQ-INT4"],
                "weight_dtype": ["int4"],
                "vllm_image_digest": ["sha256:" + "a" * 64],
                # top_logprobs and hidden_states_uri intentionally absent
            }
        ),
        traces_dir / "qwen2.5-7b__pilot.parquet",
    )
    out = finalize._validate_traces_dir(
        traces_dir,
        ["qwen2.5-7b"],
        mode="confirmatory",
        expected_n_articles=1,
    )
    assert "qwen2.5-7b" in out
