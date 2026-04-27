"""Build the WS1 30-case smoke fixture from `data/seed/test_cases_v3.json`.

Composition (deterministic, reproducible with fixed seed):

| bucket                        | count |
|-------------------------------|-------|
| pre-cutoff × policy           | 6     |
| pre-cutoff × corporate        | 6     |
| pre-cutoff × industry         | 6     |
| pre-cutoff × macro            | 6     |
| post-cutoff (any category)    | 6     |
| **total**                     | 30    |

Output: `data/pilot/fixtures/smoke_30.json` — a JSON array where each
element is a flattened `ArticleRecord`-shaped dict (case_id, text,
target, target_type, publish_date, event_type, host_category, metadata).

The fixture is small enough that the WS1 smoke gate (per-model)
finishes in ~15 minutes on A6000.
"""

from __future__ import annotations

import json
import random
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.r5a.contracts import ArticleRecord, HostCategory  # noqa: E402

SEED = 20260426
TARGET_PER_PRE_CATEGORY = 6
POST_CUTOFF_TARGET = 6


def _parse_publish_date(raw: str) -> date:
    head = raw.replace("T", " ").split(" ")[0]
    return date.fromisoformat(head)


def build_fixture(seed_path: Path, out_path: Path) -> list[ArticleRecord]:
    raw = json.loads(seed_path.read_text(encoding="utf-8"))
    cases = raw["test_cases"]

    by_bucket: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for c in cases:
        period = c.get("period")
        if period not in ("pre_cutoff", "post_cutoff"):
            continue
        category = c["news"]["category"]
        by_bucket[(period, category)].append(c)

    rng = random.Random(SEED)
    selected: list[dict] = []

    # pre-cutoff: 6 per category, sorted by id for stability
    for category in ("policy", "corporate", "industry", "macro"):
        pool = sorted(by_bucket[("pre_cutoff", category)], key=lambda c: c["id"])
        if len(pool) < TARGET_PER_PRE_CATEGORY:
            raise RuntimeError(
                f"only {len(pool)} pre_cutoff x {category} cases in seed; "
                f"need >= {TARGET_PER_PRE_CATEGORY}"
            )
        selected.extend(rng.sample(pool, TARGET_PER_PRE_CATEGORY))

    # post-cutoff: 6 across all categories, balanced where possible
    post_pool: list[dict] = []
    for category in ("policy", "corporate", "industry", "macro"):
        post_pool.extend(by_bucket[("post_cutoff", category)])
    post_pool.sort(key=lambda c: c["id"])
    if len(post_pool) < POST_CUTOFF_TARGET:
        raise RuntimeError(
            f"only {len(post_pool)} post_cutoff cases in seed; "
            f"need >= {POST_CUTOFF_TARGET}"
        )
    selected.extend(rng.sample(post_pool, POST_CUTOFF_TARGET))

    records = [_to_article_record(c) for c in selected]
    _write(records, out_path)
    return records


def _to_article_record(case: dict) -> ArticleRecord:
    news = case["news"]
    category = news["category"]
    return ArticleRecord(
        case_id=case["id"],
        text=news["content"],
        target=case.get("target") or "未指定",
        target_type=case.get("target_type") or "other",
        publish_date=_parse_publish_date(news["publish_time"]),
        event_type=case.get("subcategory") or "tbd",
        host_category=HostCategory(category),
        metadata={
            "title": news.get("title"),
            "publish_time": news.get("publish_time"),
            "period": case.get("period"),
            "key_entities": case.get("key_entities"),
            "key_numbers": case.get("key_numbers"),
            "rubric_version": case.get("rubric_version"),
        },
    )


def _write(records: list[ArticleRecord], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = [r.model_dump(mode="json") for r in records]
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> int:
    seed_path = REPO_ROOT / "data" / "seed" / "test_cases_v3.json"
    out_path = REPO_ROOT / "data" / "pilot" / "fixtures" / "smoke_30.json"
    if not seed_path.exists():
        print(f"seed file not found: {seed_path}", file=sys.stderr)
        return 2

    records = build_fixture(seed_path, out_path)
    by_period: dict[str, int] = defaultdict(int)
    by_category: dict[str, int] = defaultdict(int)
    for r in records:
        meta = r.metadata or {}
        by_period[meta.get("period", "unknown")] += 1
        by_category[r.host_category.value] += 1

    print(f"wrote {len(records)} cases to {out_path}")
    print("by period:  ", dict(by_period))
    print("by category:", dict(by_category))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
