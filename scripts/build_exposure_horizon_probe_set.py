"""Build the Path-E exposure-horizon probe set from local CLS raw data.

The probe is month-stratified: 60 eligible articles per month across
2023-01..2025-12 by default. Source files are the Thales CLS raw daily
JSON shards (`YYYY-MM-DD.json`). The script never calls model APIs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_CLS_ROOT = Path(r"D:\GitRepos\Thales\datasets\cls_telegraph_raw")
DEFAULT_OUT = (
    REPO_ROOT
    / "data"
    / "pilot"
    / "exposure_horizon"
    / "probe_set_monthly60_36mo.json"
)
DEFAULT_SEED = 20260417
DEFAULT_ARTICLES_PER_MONTH = 60
DEFAULT_START_MONTH = "2023-01"
DEFAULT_END_MONTH = "2025-12"
DEFAULT_MIN_BODY_CHARS = 50
HOST_CATEGORIES = {"policy", "corporate", "industry", "macro"}
UNRELIABLE_CATEGORY_VALUES = {"", "all", "unknown", "none", "null"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the Path-E monthly exposure-horizon probe set"
    )
    parser.add_argument("--cls-root", type=Path, default=DEFAULT_CLS_ROOT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--articles-per-month", type=int, default=DEFAULT_ARTICLES_PER_MONTH
    )
    parser.add_argument("--start-month", default=DEFAULT_START_MONTH)
    parser.add_argument("--end-month", default=DEFAULT_END_MONTH)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--min-body-chars", type=int, default=DEFAULT_MIN_BODY_CHARS)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print monthly counts without writing the JSON output",
    )
    return parser.parse_args()


def iter_months(start_month: str, end_month: str) -> list[str]:
    start_y, start_m = (int(part) for part in start_month.split("-"))
    end_y, end_m = (int(part) for part in end_month.split("-"))
    out: list[str] = []
    y, m = start_y, start_m
    while (y, m) <= (end_y, end_m):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m > 12:
            y += 1
            m = 1
    return out


def _month_files(cls_root: Path, month: str) -> list[Path]:
    return sorted(cls_root.glob(f"{month}-*.json"))


def _load_items(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"skip {path.name}: failed to parse JSON ({exc})", file=sys.stderr)
        return []
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        items = payload.get("items", [])
        if isinstance(items, list):
            return [x for x in items if isinstance(x, dict)]
    return []


def _parse_ts(item: dict[str, Any], fallback_month: str) -> str:
    raw = item.get("time") or item.get("ts") or item.get("timestamp")
    if isinstance(raw, (int, float)):
        try:
            return datetime.fromtimestamp(int(raw), tz=timezone.utc).isoformat()
        except (OSError, OverflowError, ValueError):
            return f"{fallback_month}-01T00:00:00+00:00"
    if isinstance(raw, str) and raw.strip():
        text = raw.strip().replace(" ", "T")
        if len(text) == 10:
            text += "T00:00:00"
        return text
    return f"{fallback_month}-01T00:00:00+00:00"


def _normalize_category(raw: Any) -> str:
    value = str(raw or "").strip().lower()
    if value in HOST_CATEGORIES:
        return value
    return value or "unknown"


def _stable_id(item: dict[str, Any], headline: str, body: str, ts: str) -> str:
    raw_id = item.get("id") or item.get("article_id") or item.get("uuid")
    if raw_id is not None and str(raw_id).strip():
        return f"cls_{raw_id}"
    digest = hashlib.sha256(
        f"{headline}\n{ts}\n{body}".encode("utf-8")
    ).hexdigest()[:16]
    return f"cls_{digest}"


def _to_article(
    item: dict[str, Any],
    *,
    month: str,
    min_body_chars: int,
) -> dict[str, Any] | None:
    headline = str(item.get("headline") or item.get("title") or "").strip()
    body = str(item.get("body") or item.get("content") or "").strip()
    if not body or len(body) < min_body_chars:
        return None
    ts = _parse_ts(item, month)
    category = _normalize_category(item.get("category"))
    return {
        "id": _stable_id(item, headline, body, ts),
        "month": month,
        "category": category,
        "headline": headline,
        "body": body,
        "ts": ts,
        "source": item.get("source"),
        "source_id": item.get("id"),
    }


def _category_reliable(eligible: list[dict[str, Any]]) -> bool:
    values = {
        str(row["category"]).lower()
        for row in eligible
        if str(row.get("category", "")).lower() not in UNRELIABLE_CATEGORY_VALUES
    }
    return len(values) >= 2


def _sample_uniform(
    eligible: list[dict[str, Any]], n: int, rng: random.Random
) -> list[dict[str, Any]]:
    if len(eligible) <= n:
        return list(eligible)
    return rng.sample(eligible, n)


def _sample_category_uniform(
    eligible: list[dict[str, Any]], n: int, rng: random.Random
) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in eligible:
        buckets[str(row["category"])].append(row)

    categories = sorted(buckets)
    shuffled_categories = list(categories)
    rng.shuffle(shuffled_categories)
    base = n // len(categories)
    remainder = n % len(categories)
    quota = {
        cat: base + (1 if cat in set(shuffled_categories[:remainder]) else 0)
        for cat in categories
    }

    selected: list[dict[str, Any]] = []
    leftovers: list[dict[str, Any]] = []
    for cat in categories:
        rows = list(buckets[cat])
        rng.shuffle(rows)
        take = min(quota[cat], len(rows))
        selected.extend(rows[:take])
        leftovers.extend(rows[take:])

    if len(selected) < n and leftovers:
        selected.extend(_sample_uniform(leftovers, n - len(selected), rng))
    rng.shuffle(selected)
    return selected[:n]


def _eligible_for_month(
    cls_root: Path, month: str, min_body_chars: int
) -> list[dict[str, Any]]:
    seen_headlines: set[str] = set()
    eligible: list[dict[str, Any]] = []
    for path in _month_files(cls_root, month):
        for item in _load_items(path):
            article = _to_article(item, month=month, min_body_chars=min_body_chars)
            if article is None:
                continue
            headline_key = str(article["headline"]).strip()
            if headline_key in seen_headlines:
                continue
            seen_headlines.add(headline_key)
            eligible.append(article)
    return eligible


def build_probe_set(
    *,
    cls_root: Path,
    out_path: Path,
    articles_per_month: int,
    start_month: str,
    end_month: str,
    seed: int,
    min_body_chars: int,
) -> dict[str, Any]:
    rng = random.Random(seed)
    months = iter_months(start_month, end_month)
    articles: list[dict[str, Any]] = []
    monthly_realized: list[dict[str, Any]] = []
    reliable_months = 0
    categories_seen: set[str] = set()

    for month in months:
        eligible = _eligible_for_month(cls_root, month, min_body_chars)
        reliable = _category_reliable(eligible)
        if reliable:
            reliable_months += 1
            sample = _sample_category_uniform(eligible, articles_per_month, rng)
        else:
            sample = _sample_uniform(eligible, articles_per_month, rng)

        articles.extend(sample)
        categories_seen.update(str(row["category"]) for row in eligible)
        monthly_realized.append(
            {
                "month": month,
                "n": len(sample),
                "n_eligible_pool": len(eligible),
                "scheme": "category-uniform" if reliable else "uniform",
            }
        )
        if len(sample) < articles_per_month:
            print(
                f"{month}: only {len(sample)} eligible articles "
                f"(target {articles_per_month})",
                file=sys.stderr,
            )

    scheme = "category-uniform" if reliable_months == len(months) else "uniform"
    created = date.today().strftime("%Y%m%d")
    return {
        "probe_set_id": f"monthly60_36mo_{seed}_{created}",
        "config": {
            "cls_root": str(cls_root),
            "out": str(out_path),
            "articles_per_month": articles_per_month,
            "start_month": start_month,
            "end_month": end_month,
            "seed": seed,
            "min_body_chars": min_body_chars,
        },
        "stratification": {
            "scheme": scheme,
            "categories": sorted(
                c for c in categories_seen if c.lower() not in UNRELIABLE_CATEGORY_VALUES
            ),
        },
        "monthly_realized": monthly_realized,
        "articles": articles,
    }


def main() -> int:
    args = parse_args()
    if args.articles_per_month <= 0:
        raise SystemExit("--articles-per-month must be positive")
    if args.min_body_chars < 0:
        raise SystemExit("--min-body-chars must be non-negative")
    if not args.cls_root.is_dir():
        raise SystemExit(f"--cls-root does not exist or is not a directory: {args.cls_root}")

    payload = build_probe_set(
        cls_root=args.cls_root,
        out_path=args.out,
        articles_per_month=args.articles_per_month,
        start_month=args.start_month,
        end_month=args.end_month,
        seed=args.seed,
        min_body_chars=args.min_body_chars,
    )

    print("monthly realized counts:")
    for row in payload["monthly_realized"]:
        print(
            f"  {row['month']}: n={row['n']} "
            f"eligible={row['n_eligible_pool']} scheme={row['scheme']}"
        )
    print(f"total articles: {len(payload['articles'])}")

    if args.dry_run:
        print("dry-run: no output written")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
