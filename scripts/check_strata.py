"""Phase B4: power-aware cell check for the period x anchor stratification.

Reads ``data/seed/test_cases_v3.json`` (after Codex annotation, B2).
Cross-tabs ``period`` x ``anchor_level``, computes a power analysis assuming
the pilot's 7-10% baseline ``fo_flip`` rate and target OR=2.5, then writes
``data/seed/strata_config.json`` declaring the canonical
``analysis_anchor_field``.

Decision logic
==============

Per-cell case count needed (rule of thumb at alpha=0.05, power=0.80, OR=2.5):
- baseline 5%  : ~150 / cell
- baseline 7.5%: ~100 / cell
- baseline 10% : ~80  / cell

If the 4-level stratification ``period x {0,1,2,3}`` cannot satisfy 80 cases
per cell within the 700 cap, collapse to binary
``weakly_anchored (Level 0+1) vs strongly_anchored (Level 2+3)``.

Output: ``data/seed/strata_config.json``::

    {
      "analysis_anchor_field": "anchor_level" | "anchor_binary",
      "rationale": "...",
      "cells_4level": {...},
      "cells_2level": {...},
      "min_cell_size_target": 80,
      "decided_at": "..."
    }
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CASES_PATH = ROOT / "data" / "seed" / "test_cases_v3.json"
FALLBACK_CASES_PATH = ROOT / "data" / "seed" / "test_cases_expanded.json"
OUTPUT_PATH = ROOT / "data" / "seed" / "strata_config.json"

MIN_CELL_SIZE_TARGET = 80           # at baseline 10% flip rate
EXPECTED_FLIP_RATE = 0.075          # midpoint of 7-10% pilot rate
TARGET_OR = 2.5
SAMPLE_BUDGET = 700


def _load_cases(path: Path) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        for key in ("test_cases", "cases", "candidates"):
            if isinstance(raw.get(key), list):
                return raw[key]
        for value in raw.values():
            if isinstance(value, list):
                return value
    if isinstance(raw, list):
        return raw
    raise ValueError(f"Unexpected case-file structure in {path}")


def _anchor_binary(level: Any) -> str | None:
    if level is None:
        return None
    try:
        lv = int(level)
    except (TypeError, ValueError):
        return None
    return "strongly_anchored" if lv >= 2 else "weakly_anchored"


def main() -> int:
    cases_path = DEFAULT_CASES_PATH
    if not cases_path.exists():
        if FALLBACK_CASES_PATH.exists():
            print(f"NOTE: {cases_path} not found; falling back to {FALLBACK_CASES_PATH}")
            cases_path = FALLBACK_CASES_PATH
        else:
            print(f"ERROR: no case file found ({DEFAULT_CASES_PATH} or fallback)")
            return 1

    cases = _load_cases(cases_path)
    print(f"Loaded {len(cases)} cases from {cases_path}")

    # Cross-tab period x anchor_level (4-level)
    cells_4: Counter[str] = Counter()
    cells_2: Counter[str] = Counter()
    n_missing_anchor = 0
    n_neutral = 0

    for c in cases:
        period = c.get("period")
        if period not in ("pre_cutoff", "post_cutoff"):
            continue
        direction = c.get("expected_direction", "")
        if str(direction).lower() == "neutral":
            n_neutral += 1
            continue
        anchor_level = c.get("anchor_level")
        if anchor_level is None:
            n_missing_anchor += 1
            continue
        cells_4[f"{period}/{anchor_level}"] += 1
        b = _anchor_binary(anchor_level)
        if b is not None:
            cells_2[f"{period}/{b}"] += 1

    print(f"\nDropped {n_neutral} neutral cases, {n_missing_anchor} cases with missing anchor_level")
    print(f"\n--- 4-level stratification ({MIN_CELL_SIZE_TARGET} per cell target) ---")
    for k in sorted(cells_4.keys()):
        n = cells_4[k]
        flag = "OK" if n >= MIN_CELL_SIZE_TARGET else "SHORT"
        exp_flips = n * EXPECTED_FLIP_RATE
        print(f"  {k:30s}  n={n:4d}  expected_flips={exp_flips:5.1f}  [{flag}]")

    print(f"\n--- 2-level (binary) stratification ---")
    for k in sorted(cells_2.keys()):
        n = cells_2[k]
        flag = "OK" if n >= MIN_CELL_SIZE_TARGET * 2 else "SHORT"
        exp_flips = n * EXPECTED_FLIP_RATE
        print(f"  {k:30s}  n={n:4d}  expected_flips={exp_flips:5.1f}  [{flag}]")

    # Decision rule
    n_4level_short = sum(1 for v in cells_4.values() if v < MIN_CELL_SIZE_TARGET)
    n_4level_total = len(cells_4)
    n_2level_short = sum(1 for v in cells_2.values() if v < MIN_CELL_SIZE_TARGET * 2)

    if n_4level_short == 0:
        analysis_field = "anchor_level"
        rationale = (
            f"4-level stratification has all {n_4level_total} cells >= "
            f"{MIN_CELL_SIZE_TARGET}; primary analysis uses 4-level."
        )
    elif n_2level_short == 0:
        analysis_field = "anchor_binary"
        rationale = (
            f"4-level had {n_4level_short}/{n_4level_total} short cells "
            f"(<{MIN_CELL_SIZE_TARGET}); collapsed to binary "
            f"(weakly_anchored / strongly_anchored). All 2-level cells reach target."
        )
    else:
        analysis_field = "anchor_binary"
        rationale = (
            f"4-level had {n_4level_short}/{n_4level_total} short cells; "
            f"binary still has {n_2level_short} short cells but binary is the best "
            f"available given the {SAMPLE_BUDGET}-case budget. Document as a power "
            f"limitation in PILOT_RESULTS.md."
        )

    print(f"\n=== DECISION ===")
    print(f"  analysis_anchor_field = {analysis_field!r}")
    print(f"  rationale: {rationale}")

    out = {
        "analysis_anchor_field": analysis_field,
        "rationale": rationale,
        "min_cell_size_target": MIN_CELL_SIZE_TARGET,
        "expected_flip_rate": EXPECTED_FLIP_RATE,
        "target_or": TARGET_OR,
        "sample_budget": SAMPLE_BUDGET,
        "cells_4level": dict(sorted(cells_4.items())),
        "cells_2level": dict(sorted(cells_2.items())),
        "n_neutral_dropped": n_neutral,
        "n_missing_anchor_dropped": n_missing_anchor,
        "decided_at": datetime.now().isoformat(),
        "source_cases_path": str(cases_path),
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
