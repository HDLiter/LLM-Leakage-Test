"""Phase C — rescore fo_flip on the cached diagnostic_2_results.json.

This script rebuilds the per-case `metrics.fo_flip_*` block from the cached
`tasks[task_id].responses[].parsed_output` dicts using the new
`_detect_fo_flip` semantics from `src/metrics.py`. It does NOT issue any API
calls and does NOT mutate `data/results/diagnostic_2_results.json`.

Outputs:
    1. `data/results/diagnostic_2_results.rescored_v2.json` — a new file with
       the rescored fields injected into each case's `metrics` block. The
       legacy `fo_flip_direct/impact` keys are kept (now equal to
       `_strict`) so older scripts still work.
    2. Stdout: side-by-side comparison of strict / hedged / union counts
       (matches `scripts/_audit_bug3.py`'s tables) plus stratified MH OR
       under both definitions.

Decision aid: if hedged-version pooled MH OR for `fo_flip_direct_hedged`
crosses 1.0 (pre > post), the v3 null is dead and Phase D becomes optional.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any

import numpy as np
from statsmodels.stats.contingency_tables import StratifiedTable, Table2x2

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.metrics import (
    _detect_fo_flip,
    fo_flip_label_to_hedged,
    fo_flip_label_to_strict,
)

INPUT_PATH = ROOT / "data" / "results" / "diagnostic_2_results.json"
OUTPUT_PATH = ROOT / "data" / "results" / "diagnostic_2_results.rescored_v2.json"
STRATA_CONFIG_PATH = ROOT / "data" / "seed" / "strata_config.json"

PILOT_TASKS = ["direct_prediction.base", "decomposed_impact.base"]
TASK_TO_FIELD = {
    "direct_prediction.base": "direction",
    "decomposed_impact.base": "fund_impact",
}


def _norm_direction(value: Any) -> str:
    if value is None:
        return ""
    if hasattr(value, "value"):
        value = value.value
    return str(value).strip().lower()


def rescore_case(case: dict[str, Any]) -> dict[str, Any]:
    """Return a deep copy of the case with rescored fo_flip fields injected."""
    new_case = deepcopy(case)
    metrics = new_case.setdefault("metrics", {})
    expected = _norm_direction(case.get("expected_direction"))

    for task_id in PILOT_TASKS:
        task_block = new_case.get("tasks", {}).get(task_id, {})
        responses = task_block.get("responses", {}) or {}
        orig_resp = responses.get("original", {}) or {}
        fo_resp = responses.get("false_outcome_cpt", {}) or {}

        orig_parsed = (
            orig_resp.get("parsed_output") if orig_resp.get("valid") else None
        )
        fo_parsed = fo_resp.get("parsed_output") if fo_resp.get("valid") else None
        target_field = TASK_TO_FIELD[task_id]

        label: str | None = None
        if isinstance(orig_parsed, dict) and isinstance(fo_parsed, dict):
            label = _detect_fo_flip(
                orig=orig_parsed,
                cf_false_outcome=fo_parsed,
                expected_direction=expected,
                target_field=target_field,
            )
        strict = fo_flip_label_to_strict(label)
        hedged = fo_flip_label_to_hedged(label)

        suffix = "direct" if task_id == "direct_prediction.base" else "impact"
        # Legacy alias mirrors strict so existing scripts still work.
        metrics[f"fo_flip_{suffix}"] = strict
        metrics[f"fo_flip_{suffix}_strict"] = strict
        metrics[f"fo_flip_{suffix}_hedged"] = hedged
        metrics[f"fo_flip_{suffix}_label"] = label

        # Also patch the per-task cfls block for completeness.
        cfls_block = task_block.setdefault("cfls", {})
        cfls_block["false_outcome_flip"] = strict
        cfls_block["false_outcome_flip_strict"] = strict
        cfls_block["false_outcome_flip_hedged"] = hedged
        cfls_block["false_outcome_flip_label"] = label

    return new_case


def _mh_for(cases: list[dict[str, Any]], metric_key: str, anchor_field: str
            ) -> dict[str, Any]:
    """Pooled MH OR + per-stratum table for one metric."""
    strata: dict[str, dict[str, int]] = {}
    for c in cases:
        period = c.get("period")
        if period not in ("pre_cutoff", "post_cutoff"):
            continue
        v = c.get("metrics", {}).get(metric_key)
        if v is None:
            continue
        s = c.get(anchor_field)
        if s is None:
            continue
        s_str = str(s)
        flip = bool(v)
        cell = strata.setdefault(s_str, {
            "pre_flip": 0, "pre_noflip": 0,
            "post_flip": 0, "post_noflip": 0,
        })
        if period == "pre_cutoff":
            cell["pre_flip" if flip else "pre_noflip"] += 1
        else:
            cell["post_flip" if flip else "post_noflip"] += 1

    arrays: list[np.ndarray] = []
    per_stratum: dict[str, dict[str, Any]] = {}
    for s_str in sorted(strata):
        c = strata[s_str]
        arr = np.array([
            [c["pre_flip"], c["pre_noflip"]],
            [c["post_flip"], c["post_noflip"]],
        ])
        try:
            t = Table2x2(arr)
            stratum_or = float(t.oddsratio)
        except Exception:
            stratum_or = float("nan")
        per_stratum[s_str] = {
            "n": int(arr.sum()),
            "pre_flip": c["pre_flip"], "pre_total": c["pre_flip"] + c["pre_noflip"],
            "post_flip": c["post_flip"], "post_total": c["post_flip"] + c["post_noflip"],
            "or": stratum_or,
        }
        if arr.sum(axis=0).min() > 0 and arr.sum(axis=1).min() > 0:
            arrays.append(arr)

    pooled_or = None
    p_value = None
    bd_p = None
    if arrays:
        try:
            mh = StratifiedTable(arrays)
            pooled_or = float(mh.oddsratio_pooled)
            test = mh.test_null_odds()
            p_value = float(test.pvalue)
            bd = mh.test_equal_odds()
            bd_p = float(bd.pvalue)
        except Exception as exc:
            print(f"  WARN: MH failed for {metric_key}: {exc}")
    return {
        "per_stratum": per_stratum,
        "pooled_or": pooled_or,
        "p_value": p_value,
        "breslow_day_p": bd_p,
    }


def main() -> int:
    if not INPUT_PATH.exists():
        print(f"ERROR: {INPUT_PATH} not found")
        return 1

    raw = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    cases = raw.get("cases", [])
    print(f"Loaded {len(cases)} cases from {INPUT_PATH.name}")

    rescored_cases = [rescore_case(c) for c in cases]

    # ── Side-by-side label counts ──────────────────────────────
    print()
    print("=== Rescored fo_flip label counts ===")
    for task_id in PILOT_TASKS:
        suffix = "direct" if task_id == "direct_prediction.base" else "impact"
        labels = [c["metrics"].get(f"fo_flip_{suffix}_label") for c in rescored_cases]
        cnt = Counter(labels)
        print(f"  {task_id}:")
        print(f"    strict_flip : {cnt.get('strict_flip', 0)}")
        print(f"    hedged_flip : {cnt.get('hedged_flip', 0)}")
        print(f"    no_flip     : {cnt.get('no_flip', 0)}")
        print(f"    None (undef): {cnt.get(None, 0)}")
        union = cnt.get("strict_flip", 0) + cnt.get("hedged_flip", 0)
        print(f"    union       : {union}")

    # ── Pooled MH under each variant ───────────────────────────
    anchor_field = "anchor_binary"
    if STRATA_CONFIG_PATH.exists():
        cfg = json.loads(STRATA_CONFIG_PATH.read_text(encoding="utf-8"))
        anchor_field = cfg.get("analysis_anchor_field", "anchor_binary")

    print()
    print(f"=== Mantel-Haenszel stratified by {anchor_field} ===")
    summary: dict[str, Any] = {}
    for variant in [
        "fo_flip_direct_strict",
        "fo_flip_direct_hedged",
        "fo_flip_impact_strict",
        "fo_flip_impact_hedged",
    ]:
        block = _mh_for(rescored_cases, variant, anchor_field)
        summary[variant] = block
        print(f"\n  {variant}:")
        for s, row in block["per_stratum"].items():
            print(f"    stratum={s:18s}  n={row['n']:4d}  "
                  f"pre={row['pre_flip']}/{row['pre_total']}  "
                  f"post={row['post_flip']}/{row['post_total']}  "
                  f"OR={row['or']:.3f}")
        print(f"    POOLED MH: OR={block['pooled_or']}  p={block['p_value']}  "
              f"BD_p={block['breslow_day_p']}")

    # ── Decision aid ───────────────────────────────────────────
    print()
    print("=== Decision aid ===")
    direct_strict_or = summary["fo_flip_direct_strict"]["pooled_or"]
    direct_hedged_or = summary["fo_flip_direct_hedged"]["pooled_or"]
    impact_strict_or = summary["fo_flip_impact_strict"]["pooled_or"]
    impact_hedged_or = summary["fo_flip_impact_hedged"]["pooled_or"]
    print(f"  direct strict OR = {direct_strict_or}")
    print(f"  direct hedged OR = {direct_hedged_or}")
    print(f"  impact strict OR = {impact_strict_or}")
    print(f"  impact hedged OR = {impact_hedged_or}")
    flipped_direct = (
        direct_strict_or is not None and direct_hedged_or is not None
        and (direct_strict_or < 1.0) != (direct_hedged_or < 1.0)
    )
    flipped_impact = (
        impact_strict_or is not None and impact_hedged_or is not None
        and (impact_strict_or < 1.0) != (impact_hedged_or < 1.0)
    )
    if flipped_direct or flipped_impact:
        which = []
        if flipped_direct:
            which.append("direct")
        if flipped_impact:
            which.append("impact")
        print(f"  → Direction inverts under hedged definition for: {', '.join(which)}")
        print(f"    The v3 null may be dead. Skip Phase D and write up Phase 4.")
    else:
        print("  → Hedged definition does NOT invert direction. Continue to Phase D")
        print("    for the cleanest re-run with all bug fixes.")

    # ── Write the rescored JSON (cases + summary; not the full payload) ──
    rescored_payload = {
        "meta": {
            "rescored_from": str(INPUT_PATH),
            "rescored_by": "scripts/rescore_fo_flip.py",
            "anchor_field": anchor_field,
            "n_cases": len(rescored_cases),
            "note": (
                "Rescored fo_flip variants from cached parsed_output. "
                "Strict mirrors the v3 baseline (only opposite-polarity flips); "
                "hedged adds 'ORIG non-neutral, FO neutral' cases."
            ),
        },
        "cases": rescored_cases,
        "mh_summary": summary,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(rescored_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nWrote {OUTPUT_PATH.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
