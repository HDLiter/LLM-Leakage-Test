"""Tests for the Phase 7 runstate SQLite writer."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.r5a.contracts import (
    RUNSTATE_TABLE_NAME,
    OperatorId,
    PerturbationVariant,
    RequestFingerprint,
    RequestStatus,
    RunStateRow,
    SeedSupport,
)
from src.r5a.orchestration.runstate import (
    RunStateTransitionError,
    RunStateWriter,
)


def _fingerprint(model_id: str = "qwen2.5-7b") -> RequestFingerprint:
    return RequestFingerprint(
        provider="vllm",
        model_id=model_id,
        system_fingerprint="sf-test",
        response_id="resp-test",
        route_hint="unit",
        ts=datetime(2026, 5, 3, 12, 0, 0, tzinfo=timezone.utc),
        seed_requested=20260417,
        seed_supported=SeedSupport.YES,
        seed_effective=True,
    )


def _row(
    *,
    request_id: str | None = None,
    status: RequestStatus = RequestStatus.PENDING,
    retry_count: int = 0,
    ts_end: datetime | None = None,
) -> RunStateRow:
    return RunStateRow(
        request_id=request_id or str(uuid.uuid4()),
        case_id="case_001",
        model_id="qwen2.5-7b",
        operator=OperatorId.P_PREDICT,
        perturbation_variant=PerturbationVariant.BASELINE,
        status=status,
        retry_count=retry_count,
        fingerprint=_fingerprint(),
        response_id="resp-test",
        ts_start=datetime(2026, 5, 3, 12, 0, 0, tzinfo=timezone.utc),
        ts_end=ts_end,
    )


def _columns(db_path: Path) -> set[str]:
    with sqlite3.connect(str(db_path)) as conn:
        return {
            str(row[1])
            for row in conn.execute(f"PRAGMA table_info({RUNSTATE_TABLE_NAME})")
        }


def _fetch_one(db_path: Path, request_id: str) -> sqlite3.Row:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        f"SELECT * FROM {RUNSTATE_TABLE_NAME} WHERE request_id = ?",
        (request_id,),
    ).fetchone()
    conn.close()
    assert row is not None
    return row


def test_db_init_is_idempotent(tmp_path: Path):
    db = tmp_path / "runstate.db"
    writer = RunStateWriter(db)
    writer.init_db()
    writer.init_db()
    assert db.exists()
    assert RUNSTATE_TABLE_NAME in {
        row[0]
        for row in sqlite3.connect(str(db)).execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }


def test_pending_then_success_updates_row(tmp_path: Path):
    db = tmp_path / "runstate.db"
    writer = RunStateWriter(db)
    rid = str(uuid.uuid4())

    writer.write(_row(request_id=rid, status=RequestStatus.PENDING))
    writer.write(
        _row(
            request_id=rid,
            status=RequestStatus.SUCCESS,
            retry_count=1,
            ts_end=datetime(2026, 5, 3, 12, 1, 0, tzinfo=timezone.utc),
        )
    )

    row = _fetch_one(db, rid)
    assert row["status"] == "success"
    assert row["retry_count"] == 1
    assert row["ts_end"] == "2026-05-03T12:01:00+00:00"


def test_terminal_rewrite_to_different_terminal_status_raises(tmp_path: Path):
    db = tmp_path / "runstate.db"
    writer = RunStateWriter(db)
    rid = str(uuid.uuid4())

    writer.write(_row(request_id=rid, status=RequestStatus.PENDING))
    writer.write(
        _row(
            request_id=rid,
            status=RequestStatus.SUCCESS,
            ts_end=datetime(2026, 5, 3, 12, 1, 0, tzinfo=timezone.utc),
        )
    )

    with pytest.raises(RunStateTransitionError, match="terminal"):
        writer.write(
            _row(
                request_id=rid,
                status=RequestStatus.TERMINAL_SKIPPED,
                ts_end=datetime(2026, 5, 3, 12, 2, 0, tzinfo=timezone.utc),
            )
        )


def test_terminal_without_pending_predecessor_raises(tmp_path: Path):
    writer = RunStateWriter(tmp_path / "runstate.db")
    with pytest.raises(RunStateTransitionError, match="first runstate write"):
        writer.write(
            _row(
                status=RequestStatus.SUCCESS,
                ts_end=datetime(2026, 5, 3, 12, 1, 0, tzinfo=timezone.utc),
            )
        )


def test_created_schema_matches_runstate_contract_plus_seed_triplet(tmp_path: Path):
    db = tmp_path / "runstate.db"
    RunStateWriter(db).init_db()
    expected = set(RunStateRow.model_fields) | {
        "seed_requested",
        "seed_supported",
        "seed_effective",
    }
    assert _columns(db) == expected


def test_raw_sql_round_trip_values_match(tmp_path: Path):
    db = tmp_path / "runstate.db"
    writer = RunStateWriter(db)
    rid = str(uuid.uuid4())
    src = _row(request_id=rid, status=RequestStatus.PENDING)
    writer.write(src)
    row = _fetch_one(db, rid)

    assert row["request_id"] == src.request_id
    assert row["case_id"] == src.case_id
    assert row["model_id"] == src.model_id
    assert row["operator"] == src.operator.value
    assert row["perturbation_variant"] == src.perturbation_variant.value
    assert row["status"] == src.status.value
    assert row["retry_count"] == src.retry_count
    assert row["response_id"] == src.response_id
    assert row["ts_start"] == src.ts_start.isoformat()
    assert row["ts_end"] is None
    assert row["seed_requested"] == 20260417
    assert row["seed_supported"] == "yes"
    assert row["seed_effective"] == 1

    fingerprint = json.loads(row["fingerprint"])
    assert fingerprint["provider"] == "vllm"
    assert fingerprint["model_id"] == "qwen2.5-7b"
    assert fingerprint["seed_requested"] == 20260417
