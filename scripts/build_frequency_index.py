"""Build a BM25 frequency index over the CLS telegraph corpus.

The index serves Phase A3 (compute_frequency.py) as the exposure proxy: how
many times an event-shaped query appears in the model's potential training
slice. We cap the index at the model's training cutoff (2025-09-30) so that
post-cutoff items, which the model never saw, are excluded from the corpus.

Output: data/cache/cls_bm25_index.pkl with
    {
        "index":            BM25Okapi,
        "doc_ids":          list[str],   # "<file>:<item_id>"
        "doc_dates":        list[str],   # "YYYY-MM-DD" from filename
        "doc_titles":       list[str],   # for sanity check / dedup join
        "tokenizer_version": "jieba_<ver>",
        "build_timestamp":  ISO-8601,
        "corpus_cutoff":    "YYYY-MM-DD",
        "n_docs":           int,
    }
"""

from __future__ import annotations

import json
import pickle
import time
from datetime import datetime, UTC
from pathlib import Path

import jieba
from rank_bm25 import BM25Okapi

# ── Configuration ────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[1]
CLS_DIR = REPO_ROOT / "data" / "cls_telegraph_raw"
OUTPUT = REPO_ROOT / "data" / "cache" / "cls_bm25_index.pkl"
CORPUS_CUTOFF = "2025-09-30"  # last day inclusive (DeepSeek-chat training cutoff)
MIN_CONTENT_LEN = 30          # drop ultra-short stub items
SANITY_QUERIES = ["央行降准", "证监会", "宁德时代"]


def _load_day(filepath: Path) -> list[dict]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f).get("items", [])
    except (json.JSONDecodeError, OSError):
        return []


def _file_date(fname: str) -> str:
    """Extract YYYY-MM-DD from a filename like '2024-06-15.json'."""
    return fname[:10]


def _tokenize(text: str) -> list[str]:
    """Jieba search-mode tokenization, lowercased, with whitespace stripped."""
    return [tok for tok in jieba.cut_for_search(text.lower()) if tok.strip()]


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    all_files = sorted(
        f for f in CLS_DIR.iterdir()
        if f.suffix == ".json" and f.name[0].isdigit()
    )
    in_window = [f for f in all_files if _file_date(f.name) <= CORPUS_CUTOFF]
    print(f"Files in CLS dir: {len(all_files)}")
    print(f"Files <= {CORPUS_CUTOFF}: {len(in_window)}")

    doc_tokens: list[list[str]] = []
    doc_ids: list[str] = []
    doc_dates: list[str] = []
    doc_titles: list[str] = []
    seen_keys: set[tuple[str, str]] = set()  # (date, item_id) dedup
    n_total_items = 0
    n_short = 0
    n_dup = 0

    t0 = time.time()
    for i, fpath in enumerate(in_window, 1):
        date = _file_date(fpath.name)
        items = _load_day(fpath)
        for it in items:
            n_total_items += 1
            content = (it.get("content") or "").strip()
            title = (it.get("title") or "").strip()
            if len(content) + len(title) < MIN_CONTENT_LEN:
                n_short += 1
                continue
            item_id = str(it.get("id", ""))
            key = (date, item_id)
            if item_id and key in seen_keys:
                n_dup += 1
                continue
            seen_keys.add(key)
            text = f"{title} {content}"
            tokens = _tokenize(text)
            if not tokens:
                n_short += 1
                continue
            doc_tokens.append(tokens)
            doc_ids.append(f"{date}:{item_id}" if item_id else f"{date}:idx{len(doc_ids)}")
            doc_dates.append(date)
            doc_titles.append(title or content[:40])

        if i % 200 == 0:
            elapsed = time.time() - t0
            print(f"  {i}/{len(in_window)} files | docs={len(doc_tokens):,} | {elapsed:.1f}s")

    print()
    print(f"Read {n_total_items:,} items, kept {len(doc_tokens):,}")
    print(f"  dropped (too short): {n_short:,}")
    print(f"  dropped (duplicate id): {n_dup:,}")

    print(f"\nBuilding BM25Okapi index over {len(doc_tokens):,} docs...")
    t1 = time.time()
    bm25 = BM25Okapi(doc_tokens)
    print(f"  built in {time.time() - t1:.1f}s")

    payload = {
        "index": bm25,
        "doc_ids": doc_ids,
        "doc_dates": doc_dates,
        "doc_titles": doc_titles,
        "tokenizer_version": f"jieba_{getattr(jieba, '__version__', 'unknown')}",
        "build_timestamp": datetime.now(UTC).isoformat(),
        "corpus_cutoff": CORPUS_CUTOFF,
        "n_docs": len(doc_tokens),
    }

    print(f"\nPickling to {OUTPUT}...")
    t2 = time.time()
    with open(OUTPUT, "wb") as f:
        pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)
    size_mb = OUTPUT.stat().st_size / (1024 * 1024)
    print(f"  wrote {size_mb:.1f} MB in {time.time() - t2:.1f}s")
    if size_mb > 1500:
        print(f"  WARNING: index exceeds 1.5 GB target ({size_mb:.0f} MB)")

    # ── Sanity check: top-5 hits for canonical queries ──────────────────────
    print(f"\nSanity check (top-5 hits for canonical queries):")
    for query in SANITY_QUERIES:
        q_tokens = _tokenize(query)
        scores = bm25.get_scores(q_tokens)
        top_idx = sorted(range(len(scores)), key=lambda i: -scores[i])[:5]
        print(f"\n  Query: {query!r}  (tokens={q_tokens})")
        for rank, idx in enumerate(top_idx, 1):
            print(f"    {rank}. [{doc_dates[idx]}] score={scores[idx]:.2f} {doc_titles[idx][:60]}")

    print(f"\nTotal wall time: {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
