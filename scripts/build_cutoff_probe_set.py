"""Build the Path-E temporally-stratified exposure-horizon probe set from CLS raw.

Per `docs/DECISION_20260427_pcsg_redefinition.md` §2.4: 60 articles per
month × 36 months across 2023-01..2025-12 (≈2,160 articles total).
Output is a smoke-fixture-shaped JSON of `ArticleRecord` dicts, runnable
through `scripts/ws1_run_logprob.py --smoke --fixture <output>` to obtain
LogProbTraces. Knee detection + exposure-horizon extraction happens in
`scripts/run_exposure_horizon_analysis.py`.

The CLS source layout (per project memory `infra_capabilities.md` and
the Thales companion repo) is daily-partitioned JSON:

    <CLS_RAW>/YYYY-MM-DD.json
        {"date": "...", "items": [{"id", "title", "content", "time",
                                    "timestamp", "category", ...}]}

Articles are sampled with a fixed seed for reproducibility. We require
non-empty content with at least `min_chars` Chinese characters, and
exclude headlines that are obvious promo / non-news (heuristic: skip
items whose category is `all` AND content is shorter than `min_chars`).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.r5a.contracts import ArticleRecord, HostCategory  # noqa: E402

DEFAULT_SOURCE = Path(r"D:\GitRepos\Thales\datasets\cls_telegraph_raw")
DEFAULT_OUTPUT = (
    REPO_ROOT
    / "data"
    / "pilot"
    / "exposure_horizon"
    / "probe_set_monthly60_36mo.json"
)
DEFAULT_SEED = 20260427
DEFAULT_PER_MONTH = 60
DEFAULT_MIN_CHARS = 80
DEFAULT_START = "2023-01"  # inclusive
DEFAULT_END = "2025-12"  # inclusive — 36 months total at 60/month = 2,160 cases


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Build Path-E exposure-horizon probe set"
    )
    p.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    p.add_argument("--start", default=DEFAULT_START, help="YYYY-MM inclusive")
    p.add_argument("--end", default=DEFAULT_END, help="YYYY-MM inclusive")
    p.add_argument("--per-month", type=int, default=DEFAULT_PER_MONTH)
    p.add_argument("--min-chars", type=int, default=DEFAULT_MIN_CHARS)
    p.add_argument("--seed", type=int, default=DEFAULT_SEED)
    return p.parse_args()


def _iter_months(start: str, end: str):
    start_y, start_m = (int(x) for x in start.split("-"))
    end_y, end_m = (int(x) for x in end.split("-"))
    y, m = start_y, start_m
    while (y, m) <= (end_y, end_m):
        yield (y, m)
        m += 1
        if m > 12:
            m = 1
            y += 1


def _month_files(source: Path, year: int, month: int) -> list[Path]:
    pattern = f"{year:04d}-{month:02d}-*.json"
    return sorted(source.glob(pattern))


def _parse_publish_date(raw: str) -> date:
    head = raw.replace("T", " ").split(" ")[0]
    return date.fromisoformat(head)


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _category_to_host(category: str) -> HostCategory:
    """CLS uses a flat 'all' tag for most items; we don't have a clean
    category split here. Default everyone to corporate; a future CLS
    classifier (Thales WS0.5) can refine."""
    if category in {"policy", "corporate", "industry", "macro"}:
        return HostCategory(category)
    return HostCategory.CORPORATE


def _load_items(path: Path) -> list[dict]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"  skip {path.name}: parse failed ({exc})", file=sys.stderr)
        return []
    items = payload.get("items") or []
    if not isinstance(items, list):
        return []
    return items


def _to_record(item: dict) -> ArticleRecord | None:
    content = item.get("content") or ""
    title = item.get("title") or ""
    text = content if len(content) >= len(title) else title
    if not text:
        return None
    pub_time = item.get("time") or item.get("timestamp")
    if isinstance(pub_time, (int, float)):
        try:
            pd = datetime.fromtimestamp(int(pub_time)).date()
        except (OSError, OverflowError, ValueError):
            return None
    elif isinstance(pub_time, str):
        try:
            pd = _parse_publish_date(pub_time)
        except ValueError:
            return None
    else:
        return None
    return ArticleRecord(
        case_id=f"cls_{item.get('id')}",
        text=text,
        target=title or "未指定",
        target_type="other",
        publish_date=pd,
        event_type="cutoff_probe",  # uniform tag — Path E doesn't need event taxonomy
        host_category=_category_to_host(item.get("category") or ""),
        metadata={
            "title": title,
            "publish_time": item.get("time"),
            "source_id": item.get("id"),
            "category_raw": item.get("category"),
            "text_sha256": _hash(text),
        },
    )


def main() -> int:
    args = parse_args()
    if not args.source.is_dir():
        print(
            f"FATAL: CLS source directory not found: {args.source}\n"
            f"  pass --source <path> if you copied CLS to a different location.",
            file=sys.stderr,
        )
        return 2

    rng = random.Random(args.seed)
    selected: list[ArticleRecord] = []
    monthly_counts: dict[str, int] = defaultdict(int)
    skipped_short = 0

    for year, month in _iter_months(args.start, args.end):
        ym = f"{year:04d}-{month:02d}"
        files = _month_files(args.source, year, month)
        if not files:
            print(f"  {ym}: no files", file=sys.stderr)
            continue
        # collect all eligible items in the month
        bucket: list[ArticleRecord] = []
        for f in files:
            for item in _load_items(f):
                rec = _to_record(item)
                if rec is None:
                    continue
                if len(rec.text) < args.min_chars:
                    skipped_short += 1
                    continue
                bucket.append(rec)
        if len(bucket) < args.per_month:
            print(
                f"  {ym}: only {len(bucket)} eligible articles, need "
                f"{args.per_month}; taking all",
                file=sys.stderr,
            )
            sample = bucket
        else:
            sample = rng.sample(bucket, args.per_month)
        selected.extend(sample)
        monthly_counts[ym] = len(sample)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = [r.model_dump(mode="json") for r in selected]
    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"wrote {len(selected)} articles to {args.output}")
    print(f"skipped {skipped_short} articles below min_chars={args.min_chars}")
    print("monthly counts:")
    for ym in sorted(monthly_counts):
        print(f"  {ym}: {monthly_counts[ym]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
