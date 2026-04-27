"""`P_logprob` operator: orchestrates trace collection across articles.

Backends (`VLLMLogprobBackend`, `OfflineHFBackend`) handle a single
article each; the operator runs many through one backend with bounded
concurrency, validates invariants, and persists the result.

Plan §5.2 step 6 mandates that downstream metric computation works
*from saved traces*, never re-runs the model. This module is therefore
the source of truth for on-disk trace format.
"""

from __future__ import annotations

import asyncio
import inspect
import json
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any, Protocol

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from ..contracts import (
    ArticleRecord,
    LogProbTrace,
    RequestFingerprint,
    SeedSupport,
)


# ---------------------------------------------------------------------------
# Backend protocol
# ---------------------------------------------------------------------------


class _LogprobBackend(Protocol):
    """Structural contract every WS1 backend must satisfy."""

    model_id: str
    tokenizer_sha: str

    def trace(  # pragma: no cover  (Protocol)
        self, *, case_id: str, article_text: str
    ) -> LogProbTrace | Awaitable[LogProbTrace]: ...


# ---------------------------------------------------------------------------
# Operator
# ---------------------------------------------------------------------------


class PLogprobOperator:
    """Run `trace()` over a batch of articles with bounded concurrency.

    Args:
        backend: any object with a `trace(case_id, article_text)` method
            (sync or async). Async backends respect `max_concurrency`;
            sync backends are forced sequential because GPU forward
            passes are not safe across threads sharing one model object.
        max_concurrency: ceiling for in-flight async traces. Should not
            exceed the matching provider's runtime cap (vLLM: 16 per
            project memory).
    """

    def __init__(self, backend: _LogprobBackend, *, max_concurrency: int = 8) -> None:
        self.backend = backend
        self.max_concurrency = max(1, max_concurrency)
        self._is_async = inspect.iscoroutinefunction(backend.trace)

    async def compute(
        self,
        articles: list[ArticleRecord],
        *,
        progress: Callable[[int, int], None] | None = None,
    ) -> list[LogProbTrace]:
        if self._is_async:
            return await self._compute_async(articles, progress)
        return await self._compute_sync(articles, progress)

    async def _compute_async(
        self,
        articles: list[ArticleRecord],
        progress: Callable[[int, int], None] | None,
    ) -> list[LogProbTrace]:
        sem = asyncio.Semaphore(self.max_concurrency)
        results: list[LogProbTrace | None] = [None] * len(articles)

        async def go(idx: int, article: ArticleRecord) -> None:
            async with sem:
                trace = await self.backend.trace(  # type: ignore[misc]
                    case_id=article.case_id,
                    article_text=article.text,
                )
                results[idx] = trace
                if progress is not None:
                    progress(sum(r is not None for r in results), len(articles))

        await asyncio.gather(*(go(i, a) for i, a in enumerate(articles)))
        return [r for r in results if r is not None]

    async def _compute_sync(
        self,
        articles: list[ArticleRecord],
        progress: Callable[[int, int], None] | None,
    ) -> list[LogProbTrace]:
        results: list[LogProbTrace] = []
        for i, article in enumerate(articles):
            trace = await asyncio.to_thread(
                self.backend.trace,
                case_id=article.case_id,
                article_text=article.text,
            )
            results.append(trace)
            if progress is not None:
                progress(i + 1, len(articles))
        return results


# ---------------------------------------------------------------------------
# Parquet persistence
# ---------------------------------------------------------------------------


_PARQUET_SCHEMA = pa.schema(
    [
        ("case_id", pa.string()),
        ("model_id", pa.string()),
        ("tokenizer_family", pa.string()),
        ("tokenizer_sha", pa.string()),
        ("hf_commit_sha", pa.string()),
        ("article_token_count", pa.int32()),
        ("raw_token_ids", pa.list_(pa.int64())),
        ("token_logprobs", pa.list_(pa.float64())),
        ("thinking_mode", pa.string()),
        ("backend", pa.string()),
        # fingerprint fields, flattened
        ("fp_provider", pa.string()),
        ("fp_model_id", pa.string()),
        ("fp_system_fingerprint", pa.string()),
        ("fp_response_id", pa.string()),
        ("fp_route_hint", pa.string()),
        ("fp_ts", pa.timestamp("us", tz="UTC")),
        ("fp_seed_requested", pa.int64()),
        ("fp_seed_supported", pa.string()),
        ("fp_seed_effective", pa.bool_()),
    ]
)


def _trace_to_row(trace: LogProbTrace) -> dict[str, Any]:
    fp = trace.fingerprint
    return {
        "case_id": trace.case_id,
        "model_id": trace.model_id,
        "tokenizer_family": trace.tokenizer_family,
        "tokenizer_sha": trace.tokenizer_sha,
        "hf_commit_sha": trace.hf_commit_sha,
        "article_token_count": trace.article_token_count,
        "raw_token_ids": trace.raw_token_ids,
        "token_logprobs": trace.token_logprobs,
        "thinking_mode": trace.thinking_mode,
        "backend": trace.backend,
        "fp_provider": fp.provider,
        "fp_model_id": fp.model_id,
        "fp_system_fingerprint": fp.system_fingerprint,
        "fp_response_id": fp.response_id,
        "fp_route_hint": fp.route_hint,
        "fp_ts": fp.ts,
        "fp_seed_requested": fp.seed_requested,
        "fp_seed_supported": fp.seed_supported.value,
        "fp_seed_effective": fp.seed_effective,
    }


def _scrub_nan(value: Any) -> Any:
    """Pandas turns None in nullable columns into float NaN on read.
    Convert NaN back to None so Pydantic's stricter validators accept it."""
    if isinstance(value, float) and value != value:  # NaN check
        return None
    return value


def _row_to_trace(row: dict[str, Any]) -> LogProbTrace:
    fingerprint = RequestFingerprint(
        provider=row["fp_provider"],
        model_id=row["fp_model_id"],
        system_fingerprint=_scrub_nan(row["fp_system_fingerprint"]),
        response_id=_scrub_nan(row["fp_response_id"]),
        route_hint=_scrub_nan(row["fp_route_hint"]),
        ts=row["fp_ts"],
        seed_requested=_scrub_nan(row["fp_seed_requested"]),
        seed_supported=SeedSupport(row["fp_seed_supported"]),
        seed_effective=_scrub_nan(row["fp_seed_effective"]),
    )
    return LogProbTrace(
        case_id=row["case_id"],
        model_id=row["model_id"],
        tokenizer_family=row["tokenizer_family"],
        tokenizer_sha=row["tokenizer_sha"],
        hf_commit_sha=row["hf_commit_sha"],
        article_token_count=int(row["article_token_count"]),
        raw_token_ids=list(row["raw_token_ids"]),
        token_logprobs=list(row["token_logprobs"]),
        thinking_mode=row["thinking_mode"],
        backend=row["backend"],
        fingerprint=fingerprint,
    )


def write_traces_parquet(traces: list[LogProbTrace], path: str | Path) -> None:
    """Atomically write a batch of traces to Parquet.

    Writes to a temp file in the target directory, then renames over
    the destination. Existing files are overwritten; the operator
    expects one Parquet file per (model_id) per pilot run.
    """

    if not traces:
        raise ValueError("write_traces_parquet: no traces provided")

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    rows = [_trace_to_row(t) for t in traces]
    table = pa.Table.from_pylist(rows, schema=_PARQUET_SCHEMA)
    tmp = target.with_suffix(target.suffix + ".tmp")
    pq.write_table(table, tmp)
    tmp.replace(target)


def read_traces_parquet(path: str | Path) -> list[LogProbTrace]:
    """Reverse of `write_traces_parquet`."""

    df = pd.read_parquet(path)
    return [_row_to_trace(row) for row in df.to_dict(orient="records")]


# ---------------------------------------------------------------------------
# Run summary helpers
# ---------------------------------------------------------------------------


def trace_summary(traces: list[LogProbTrace]) -> dict[str, Any]:
    """Produce a small JSON-friendly summary for the run manifest /
    QC report. Keeps the heavy data on disk."""

    if not traces:
        return {"n": 0}

    by_model = {}
    for t in traces:
        bucket = by_model.setdefault(t.model_id, [])
        bucket.append(t)

    out: dict[str, Any] = {"n": len(traces), "by_model": {}}
    for model_id, ts in by_model.items():
        thinking_off = sum(1 for t in ts if t.thinking_mode == "off")
        token_counts = [t.article_token_count for t in ts]
        out["by_model"][model_id] = {
            "n": len(ts),
            "tokenizer_sha": ts[0].tokenizer_sha,
            "hf_commit_sha": ts[0].hf_commit_sha,
            "backend": ts[0].backend,
            "thinking_off_pct": 100.0 * thinking_off / len(ts),
            "tokens_min": min(token_counts),
            "tokens_max": max(token_counts),
            "tokens_mean": sum(token_counts) / len(token_counts),
        }
    return out


def write_summary_json(summary: dict[str, Any], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )


__all__ = [
    "PLogprobOperator",
    "read_traces_parquet",
    "trace_summary",
    "write_summary_json",
    "write_traces_parquet",
]
