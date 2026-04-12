"""Phase A3: compute frequency_class for each case via BM25 over CLS corpus.

How a case gets classified
==========================

1. Build a BM25 query from ``title`` + ``key_entities`` (jieba search tokens).
2. Score the query against the pre-built BM25 index (data/cache/cls_bm25_index.pkl).
3. Restrict to hits whose ``doc_date`` is strictly before the case's
   ``publish_time`` -- frequency is an exposure-proxy, must not include the
   article itself.
4. Dedupe near-duplicate hits into event clusters. A cluster requires ALL of:
     - title-token Jaccard >= 0.7  (jieba tokens, set-based)
     - at least one shared key entity from the case's key_entities
     - same day or +/- 3 days
   This is intentionally tighter than v2 to avoid over-merging distinct events
   that happen to share a date or template.
5. ``cluster_count`` = number of distinct event clusters (not raw hits).
6. Compare cluster_count against fixed corpus-level reference thresholds
   (calibrated once on a 50-case calibration set, then frozen) to assign
   ``frequency_class in {high, medium, low}``.

Calibration
===========

The first time the script is run with no thresholds file, it picks 50
random eligible cases, computes their cluster counts, takes the 33rd and
67th percentiles as the low/high cutoffs, and writes the thresholds to
``data/cache/frequency_thresholds_v1.json``. Subsequent runs reload these
thresholds verbatim -- they MUST NOT be re-derived from the current sample,
because that would defeat the "fixed corpus-level reference" guarantee.

Output
======

``data/seed/frequency_analysis.json``::

    {
      "thresholds": {"low_max": int, "high_min": int, "basis": "calibration_set_v1"},
      "by_case": {
        case_id: {
          "cluster_count": int,
          "frequency_class": "high"|"medium"|"low",
          "top_clusters": [{"title": str, "entity": str, "date": str}],
          "n_raw_hits": int
        }
      }
    }
"""

from __future__ import annotations

import argparse
import heapq
import json
import pickle
import random
from datetime import datetime
from pathlib import Path
from typing import Any

import jieba

ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "data" / "cache" / "cls_bm25_index.pkl"
THRESHOLDS_PATH = ROOT / "data" / "cache" / "frequency_thresholds_v1.json"
DEFAULT_CASES_PATH = ROOT / "data" / "seed" / "test_cases_v3.json"
DEFAULT_OUTPUT_PATH = ROOT / "data" / "seed" / "frequency_analysis.json"
FALLBACK_CASES_PATH = ROOT / "data" / "seed" / "test_cases_expanded.json"

TOP_N_HITS = 100          # initial BM25 candidate pool per query
JACCARD_THRESHOLD = 0.7    # cluster title similarity gate
DATE_WINDOW_DAYS = 3       # cluster date proximity gate
CALIBRATION_N = 50         # calibration sample size
CALIBRATION_SEED = 2026


def _tokenize(text: str) -> list[str]:
    return [tok for tok in jieba.cut_for_search(text.lower()) if tok.strip()]


# Per-title-token cache. Doc titles repeat across cases (same hits surface in
# multiple queries) so memoizing the jieba pass cuts per-case time substantially.
_TITLE_TOKEN_CACHE: dict[str, frozenset[str]] = {}


def _normalized_title_tokens(title: str) -> frozenset[str]:
    cached = _TITLE_TOKEN_CACHE.get(title)
    if cached is not None:
        return cached
    toks = frozenset(tok for tok in jieba.cut_for_search(title) if len(tok.strip()) >= 2)
    _TITLE_TOKEN_CACHE[title] = toks
    return toks


def _jaccard(a, b) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _parse_publish_date(publish_time: str) -> datetime | None:
    if not publish_time:
        return None
    pt = publish_time.strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(pt, fmt)
        except ValueError:
            continue
    if "T" in pt:
        try:
            return datetime.strptime(pt.split("T")[0], "%Y-%m-%d")
        except ValueError:
            return None
    return None


def _date_diff_days(a: datetime, b: datetime) -> int:
    return abs((a.date() - b.date()).days)


def load_index(index_path: Path) -> dict[str, Any]:
    print(f"Loading BM25 index from {index_path}...")
    with open(index_path, "rb") as f:
        return pickle.load(f)


def load_cases(cases_path: Path) -> list[dict[str, Any]]:
    raw = json.loads(cases_path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        for key in ("test_cases", "cases"):
            if isinstance(raw.get(key), list):
                return raw[key]
        for value in raw.values():
            if isinstance(value, list):
                return value
    if isinstance(raw, list):
        return raw
    raise ValueError(f"Unexpected case-file structure in {cases_path}")


def query_bm25_with_dedup(
    bm_index: Any,
    doc_dates: list[str],
    doc_titles: list[str],
    case: dict[str, Any],
    top_n: int = TOP_N_HITS,
) -> tuple[int, list[dict[str, Any]], int]:
    """Run a BM25 query for one case and return ``(cluster_count, top_clusters, n_raw_hits)``.

    The query is the case title plus key_entities. Hits are restricted to
    docs strictly before the case's publish_time and clustered with the
    title-jaccard / shared-entity / +/- 3-day rule.
    """
    title = (case.get("news") or {}).get("title", "") or case.get("title", "") or ""
    entities = case.get("key_entities") or []
    if isinstance(entities, str):
        entities = [entities]
    query_str = f"{title} {' '.join(entities)}".strip()
    if not query_str:
        return 0, [], 0

    publish_time = (case.get("news") or {}).get("publish_time", "") or case.get("publish_time", "") or ""
    pub_dt = _parse_publish_date(publish_time)

    q_tokens = _tokenize(query_str)
    if not q_tokens:
        return 0, [], 0

    scores = bm_index.get_scores(q_tokens)
    # Top-N by score: numpy argpartition is fastest for top-K of a 1M array.
    import numpy as _np
    if not isinstance(scores, _np.ndarray):
        scores = _np.asarray(scores)
    if len(scores) <= top_n:
        top_idx = list(_np.argsort(-scores))
    else:
        unsorted_top = _np.argpartition(-scores, top_n)[:top_n]
        # Sort just the top-N by score descending
        top_idx = list(unsorted_top[_np.argsort(-scores[unsorted_top])])

    # Filter to dates strictly before publish_time
    pre_hits: list[tuple[int, datetime, set[str], str]] = []
    for idx in top_idx:
        if scores[idx] <= 0:
            continue
        d_str = doc_dates[idx]
        try:
            d = datetime.strptime(d_str, "%Y-%m-%d")
        except ValueError:
            continue
        if pub_dt is not None and d.date() >= pub_dt.date():
            continue
        title_tokens = _normalized_title_tokens(doc_titles[idx])
        pre_hits.append((idx, d, title_tokens, doc_titles[idx]))

    n_raw_hits = len(pre_hits)
    if not pre_hits:
        return 0, [], 0

    # Cluster: a hit joins an existing cluster only if title-jaccard >= 0.7
    # AND shares >=1 entity AND date within window. Since we don't have
    # cluster-level entities, the entity check is "case key_entities appears
    # in the cluster title text" -- a coarse proxy.
    case_entity_tokens: list[str] = [str(e) for e in entities if e]

    def _shares_entity(doc_title: str) -> bool:
        if not case_entity_tokens:
            # When the case has no entities, the entity gate is impossible to
            # satisfy. Fall back to "every hit is its own cluster", which is
            # the most conservative interpretation (no merging at all).
            return False
        return any(ent and ent in doc_title for ent in case_entity_tokens)

    clusters: list[dict[str, Any]] = []
    for _idx, d, t_tokens, title_str in pre_hits:
        merged = False
        for cluster in clusters:
            jacc = _jaccard(t_tokens, cluster["title_tokens"])
            if jacc < JACCARD_THRESHOLD:
                continue
            if _date_diff_days(d, cluster["date"]) > DATE_WINDOW_DAYS:
                continue
            if not (_shares_entity(title_str) and _shares_entity(cluster["title"])):
                continue
            merged = True
            break
        if not merged:
            clusters.append({
                "title": title_str,
                "title_tokens": t_tokens,
                "date": d,
                "entity": next((e for e in case_entity_tokens if e in title_str), ""),
            })

    cluster_count = len(clusters)
    top_clusters_serializable = [
        {"title": c["title"][:80], "entity": c["entity"], "date": c["date"].strftime("%Y-%m-%d")}
        for c in clusters[:5]
    ]
    return cluster_count, top_clusters_serializable, n_raw_hits


def calibrate_thresholds(
    bm_index: Any,
    doc_dates: list[str],
    doc_titles: list[str],
    cases: list[dict[str, Any]],
    n_calibration: int = CALIBRATION_N,
    seed: int = CALIBRATION_SEED,
) -> dict[str, Any]:
    """Pick a 50-case sample, compute cluster counts, take p33 / p67 cutoffs."""
    eligible = [c for c in cases if c.get("key_entities")]
    if len(eligible) < n_calibration:
        print(f"  WARNING: only {len(eligible)} cases have key_entities; using all of them for calibration")
        sample = eligible
    else:
        rng = random.Random(seed)
        sample = rng.sample(eligible, n_calibration)

    print(f"Calibrating thresholds on {len(sample)} cases...")
    counts: list[int] = []
    for i, case in enumerate(sample, 1):
        cluster_count, _, _ = query_bm25_with_dedup(
            bm_index, doc_dates, doc_titles, case
        )
        counts.append(cluster_count)
        if i % 10 == 0:
            print(f"  calibrated {i}/{len(sample)}: latest cluster_count={cluster_count}")

    counts.sort()
    if not counts:
        raise RuntimeError("calibration produced empty count list")
    n = len(counts)
    p33 = counts[max(0, int(n * 0.33) - 1)]
    p67 = counts[max(0, int(n * 0.67) - 1)]
    # Ensure low_max < high_min so the medium band is non-empty
    if p67 <= p33:
        p67 = p33 + 1
    thresholds = {
        "low_max": int(p33),
        "high_min": int(p67),
        "basis": "calibration_set_v1",
        "n_calibration": n,
        "calibration_seed": seed,
        "calibration_count_distribution": counts,
        "frozen_at": datetime.now().isoformat(),
    }
    print(f"Thresholds: low_max={p33}  high_min={p67}  (n={n})")
    return thresholds


def classify(cluster_count: int, thresholds: dict[str, Any]) -> str:
    if cluster_count <= thresholds["low_max"]:
        return "low"
    if cluster_count >= thresholds["high_min"]:
        return "high"
    return "medium"


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute frequency_class for cases via BM25.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH,
                        help="Path to cases JSON (default: data/seed/test_cases_v3.json)")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH,
                        help="Where to write frequency_analysis.json")
    parser.add_argument("--index", type=Path, default=INDEX_PATH,
                        help="Path to pickled BM25 index")
    parser.add_argument("--recalibrate", action="store_true",
                        help="Force re-calibration of thresholds even if cached")
    args = parser.parse_args()

    if not args.cases.exists():
        if FALLBACK_CASES_PATH.exists():
            print(f"NOTE: {args.cases} not found; falling back to {FALLBACK_CASES_PATH}")
            args.cases = FALLBACK_CASES_PATH
        else:
            print(f"ERROR: cases file not found: {args.cases}")
            return 1

    if not args.index.exists():
        print(f"ERROR: BM25 index not found: {args.index}")
        return 1

    payload = load_index(args.index)
    bm_index = payload["index"]
    doc_dates = payload["doc_dates"]
    doc_titles = payload["doc_titles"]
    print(f"  Index: {payload['n_docs']:,} docs | cutoff={payload['corpus_cutoff']}")

    cases = load_cases(args.cases)
    print(f"Loaded {len(cases)} cases from {args.cases}")

    # Load or calibrate thresholds
    if THRESHOLDS_PATH.exists() and not args.recalibrate:
        thresholds = json.loads(THRESHOLDS_PATH.read_text(encoding="utf-8"))
        print(f"Loaded thresholds from {THRESHOLDS_PATH}: low_max={thresholds['low_max']}  high_min={thresholds['high_min']}")
    else:
        thresholds = calibrate_thresholds(bm_index, doc_dates, doc_titles, cases)
        THRESHOLDS_PATH.parent.mkdir(parents=True, exist_ok=True)
        THRESHOLDS_PATH.write_text(json.dumps(thresholds, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote calibrated thresholds to {THRESHOLDS_PATH}")

    # Classify all cases
    by_case: dict[str, dict[str, Any]] = {}
    class_counts = {"low": 0, "medium": 0, "high": 0}
    print(f"\nClassifying {len(cases)} cases...", flush=True)
    import time as _time
    t0 = _time.time()
    for i, case in enumerate(cases, 1):
        case_id = case.get("id") or case.get("candidate_id") or f"idx_{i}"
        cluster_count, top_clusters, n_raw = query_bm25_with_dedup(
            bm_index, doc_dates, doc_titles, case
        )
        freq = classify(cluster_count, thresholds)
        class_counts[freq] += 1
        by_case[case_id] = {
            "cluster_count": cluster_count,
            "frequency_class": freq,
            "top_clusters": top_clusters,
            "n_raw_hits": n_raw,
        }
        if i % 25 == 0:
            elapsed = _time.time() - t0
            rate = i / elapsed
            eta = (len(cases) - i) / rate
            print(f"  {i}/{len(cases)} done | rate={rate:.1f}/s | eta={eta:.0f}s", flush=True)

    output_payload = {
        "thresholds": thresholds,
        "n_cases": len(cases),
        "n_by_class": class_counts,
        "config": {
            "top_n_hits": TOP_N_HITS,
            "jaccard_threshold": JACCARD_THRESHOLD,
            "date_window_days": DATE_WINDOW_DAYS,
        },
        "by_case": by_case,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nDistribution: {class_counts}")
    print(f"Output: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
