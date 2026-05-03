"""Tests for scripts/build_exposure_horizon_probe_set.py."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.build_exposure_horizon_probe_set import build_probe_set


def _write_day(root: Path, day: str, items: list[dict]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / f"{day}.json").write_text(
        json.dumps({"date": day, "items": items}, ensure_ascii=False),
        encoding="utf-8",
    )


def _item(
    idx: int,
    *,
    title: str | None = None,
    body: str | None = None,
    category: str = "all",
    day: str = "2023-01-01",
) -> dict:
    return {
        "id": idx,
        "title": title or f"headline {idx}",
        "content": ("body " + str(idx) + " " + "x" * 80) if body is None else body,
        "time": f"{day} 09:30:00",
        "timestamp": 1672536600 + idx,
        "category": category,
        "source": "fixture",
    }


def _build(root: Path, **overrides):
    args = {
        "cls_root": root,
        "out_path": root / "out.json",
        "articles_per_month": 3,
        "start_month": "2023-01",
        "end_month": "2023-02",
        "seed": 20260417,
        "min_body_chars": 50,
    }
    args.update(overrides)
    return build_probe_set(**args)


def test_seeded_run_is_deterministic(tmp_path: Path):
    for month in ("2023-01", "2023-02"):
        day = f"{month}-01"
        _write_day(
            tmp_path,
            day,
            [_item(i + (0 if month == "2023-01" else 100), day=day) for i in range(8)],
        )

    a = _build(tmp_path)
    b = _build(tmp_path)
    assert [row["id"] for row in a["articles"]] == [
        row["id"] for row in b["articles"]
    ]


def test_per_month_count_enforced(tmp_path: Path):
    for month in ("2023-01", "2023-02"):
        day = f"{month}-01"
        _write_day(
            tmp_path,
            day,
            [_item(i + (0 if month == "2023-01" else 100), day=day) for i in range(6)],
        )
    payload = _build(tmp_path, articles_per_month=4)
    assert [row["n"] for row in payload["monthly_realized"]] == [4, 4]
    assert len(payload["articles"]) == 8


def test_empty_and_too_short_body_filter(tmp_path: Path):
    _write_day(
        tmp_path,
        "2023-01-01",
        [
            _item(1, body=""),
            _item(2, body="short"),
            _item(3, body="x" * 60),
        ],
    )
    payload = _build(
        tmp_path,
        articles_per_month=5,
        start_month="2023-01",
        end_month="2023-01",
        min_body_chars=50,
    )
    assert payload["monthly_realized"][0]["n"] == 1
    assert payload["articles"][0]["id"] == "cls_3"


def test_duplicate_headline_filter_within_month(tmp_path: Path):
    _write_day(
        tmp_path,
        "2023-01-01",
        [
            _item(1, title="dup", body="x" * 60),
            _item(2, title="dup", body="y" * 60),
            _item(3, title="unique", body="z" * 60),
        ],
    )
    payload = _build(
        tmp_path,
        articles_per_month=5,
        start_month="2023-01",
        end_month="2023-01",
    )
    assert payload["monthly_realized"][0]["n_eligible_pool"] == 2
    assert {row["headline"] for row in payload["articles"]} == {"dup", "unique"}


def test_underfilled_month_logs_and_records_realized_count(
    tmp_path: Path, capsys
):
    _write_day(tmp_path, "2023-01-01", [_item(1), _item(2)])
    payload = _build(
        tmp_path,
        articles_per_month=5,
        start_month="2023-01",
        end_month="2023-01",
    )
    captured = capsys.readouterr()
    assert "only 2 eligible articles" in captured.err
    assert payload["monthly_realized"][0]["n"] == 2
    assert payload["monthly_realized"][0]["n_eligible_pool"] == 2


def test_category_uniform_when_categories_reliable(tmp_path: Path):
    _write_day(
        tmp_path,
        "2023-01-01",
        [
            _item(1, category="policy"),
            _item(2, category="policy"),
            _item(3, category="corporate"),
            _item(4, category="corporate"),
            _item(5, category="macro"),
            _item(6, category="macro"),
        ],
    )
    payload = _build(
        tmp_path,
        articles_per_month=3,
        start_month="2023-01",
        end_month="2023-01",
    )
    assert payload["stratification"]["scheme"] == "category-uniform"
    assert payload["monthly_realized"][0]["scheme"] == "category-uniform"
    assert len({row["category"] for row in payload["articles"]}) == 3
