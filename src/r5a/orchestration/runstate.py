"""SQLite writer for Phase 7 request-level runstate.

The finalizer only reads `RUNSTATE_TABLE_NAME` and requires that no rows
remain `pending` or `retryable`. This module owns the write side: create
the table, validate rows through `RunStateRow`, and enforce the small
state machine needed by a single-operator orchestrator.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from ..contracts import (
    RUNSTATE_TABLE_NAME,
    RequestStatus,
    RunStateRow,
)

TERMINAL_STATUSES = {
    RequestStatus.SUCCESS,
    RequestStatus.TERMINAL_SKIPPED,
}


class RunStateTransitionError(RuntimeError):
    """Raised when a runstate transition violates the writer contract."""


def _adapt_datetime(value: object) -> str | None:
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()  # type: ignore[no-any-return]
    return str(value)


def _fingerprint_json(row: RunStateRow) -> str | None:
    if row.fingerprint is None:
        return None
    payload = row.fingerprint.model_dump(mode="json")
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _row_to_sql(row: RunStateRow) -> dict[str, Any]:
    fp = row.fingerprint
    return {
        "request_id": row.request_id,
        "case_id": row.case_id,
        "model_id": row.model_id,
        "operator": row.operator.value,
        "perturbation_variant": row.perturbation_variant.value,
        "status": row.status.value,
        "retry_count": row.retry_count,
        "fingerprint": _fingerprint_json(row),
        "response_id": row.response_id,
        "ts_start": row.ts_start.isoformat(),
        "ts_end": _adapt_datetime(row.ts_end),
        "seed_requested": fp.seed_requested if fp is not None else None,
        "seed_supported": fp.seed_supported.value if fp is not None else None,
        "seed_effective": (
            None
            if fp is None or fp.seed_effective is None
            else int(fp.seed_effective)
        ),
    }


def _status_from_db(value: str) -> RequestStatus:
    try:
        return RequestStatus(value)
    except ValueError as exc:
        raise RunStateTransitionError(
            f"existing runstate row has invalid status {value!r}"
        ) from exc


class RunStateWriter:
    """Create and update `request_runstate` rows keyed by `request_id`.

    Allowed transitions:
    - new request: `pending` only;
    - in-flight request: `pending`/`retryable` may move to
      `pending`, `retryable`, `success`, or `terminal_skipped`;
    - terminal rows are immutable. Rewriting a terminal row with a
      different status, or with different row content, is an error.
    """

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)

    def init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {RUNSTATE_TABLE_NAME} (
                    request_id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL,
                    model_id TEXT NOT NULL,
                    operator TEXT NOT NULL,
                    perturbation_variant TEXT NOT NULL,
                    status TEXT NOT NULL,
                    retry_count INTEGER NOT NULL,
                    fingerprint TEXT,
                    response_id TEXT,
                    ts_start TEXT NOT NULL,
                    ts_end TEXT,
                    seed_requested INTEGER,
                    seed_supported TEXT,
                    seed_effective INTEGER
                )
                """
            )

    def write(self, row: RunStateRow | dict[str, Any]) -> RunStateRow:
        try:
            validated = (
                row if isinstance(row, RunStateRow) else RunStateRow.model_validate(row)
            )
        except ValidationError:
            raise

        self.init_db()
        sql_row = _row_to_sql(validated)
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            with conn:
                existing = conn.execute(
                    f"SELECT * FROM {RUNSTATE_TABLE_NAME} WHERE request_id = ?",
                    (validated.request_id,),
                ).fetchone()
                self._validate_transition(existing, validated, sql_row)
                conn.execute(
                    f"""
                    INSERT INTO {RUNSTATE_TABLE_NAME} (
                        request_id, case_id, model_id, operator,
                        perturbation_variant, status, retry_count,
                        fingerprint, response_id, ts_start, ts_end,
                        seed_requested, seed_supported, seed_effective
                    )
                    VALUES (
                        :request_id, :case_id, :model_id, :operator,
                        :perturbation_variant, :status, :retry_count,
                        :fingerprint, :response_id, :ts_start, :ts_end,
                        :seed_requested, :seed_supported, :seed_effective
                    )
                    ON CONFLICT(request_id) DO UPDATE SET
                        case_id = excluded.case_id,
                        model_id = excluded.model_id,
                        operator = excluded.operator,
                        perturbation_variant = excluded.perturbation_variant,
                        status = excluded.status,
                        retry_count = excluded.retry_count,
                        fingerprint = excluded.fingerprint,
                        response_id = excluded.response_id,
                        ts_start = excluded.ts_start,
                        ts_end = excluded.ts_end,
                        seed_requested = excluded.seed_requested,
                        seed_supported = excluded.seed_supported,
                        seed_effective = excluded.seed_effective
                    """,
                    sql_row,
                )
        return validated

    def _validate_transition(
        self,
        existing: sqlite3.Row | None,
        incoming: RunStateRow,
        incoming_sql: dict[str, Any],
    ) -> None:
        if existing is None:
            if incoming.status is not RequestStatus.PENDING:
                raise RunStateTransitionError(
                    "first runstate write for a request must be pending; "
                    f"got {incoming.status.value!r} for {incoming.request_id}"
                )
            return

        current_status = _status_from_db(str(existing["status"]))
        if current_status in TERMINAL_STATUSES:
            existing_payload = {key: existing[key] for key in incoming_sql}
            if existing_payload != incoming_sql:
                raise RunStateTransitionError(
                    "terminal runstate rows are immutable; "
                    f"request_id={incoming.request_id} already ended as "
                    f"{current_status.value!r}"
                )
            return

        if incoming.status in TERMINAL_STATUSES and current_status not in {
            RequestStatus.PENDING,
            RequestStatus.RETRYABLE,
        }:
            raise RunStateTransitionError(
                "terminal runstate write requires a started request; "
                f"current status is {current_status.value!r}"
            )


def init_runstate_db(db_path: str | Path) -> None:
    RunStateWriter(db_path).init_db()


def write_runstate_row(
    db_path: str | Path, row: RunStateRow | dict[str, Any]
) -> RunStateRow:
    return RunStateWriter(db_path).write(row)


__all__ = [
    "RunStateTransitionError",
    "RunStateWriter",
    "init_runstate_db",
    "write_runstate_row",
]
