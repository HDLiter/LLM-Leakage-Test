"""Quick statistical analysis of D2 results.

E1 (deep-floating-lake plan): primary inference is now Mantel-Haenszel
stratified on the canonical anchor field stored in
``data/seed/strata_config.json``. Per-stratum Fisher tests + pooled MH OR
+ Breslow-Day homogeneity are reported. Raw period-only Fisher is kept
for backward comparison.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats
from statsmodels.stats.contingency_tables import StratifiedTable, Table2x2

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RESULTS_PATH = ROOT / "data" / "results" / "diagnostic_2_results.json"
STRATA_CONFIG_PATH = ROOT / "data" / "seed" / "strata_config.json"

_parser = argparse.ArgumentParser()
_parser.add_argument("--input", type=Path, default=DEFAULT_RESULTS_PATH,
                     help="Path to results JSON (default: diagnostic_2_results.json)")
_args = _parser.parse_args()
RESULTS_PATH = _args.input

with open(RESULTS_PATH, "r", encoding="utf-8") as f:
    d = json.load(f)
cases = d["cases"]

# Detect stale data: if new amber-mirror-lattice keys are missing, warn loudly
# and fall back to legacy key names so the script doesn't produce misleading
# zero/empty output.
_sample_metrics = cases[0].get("metrics", {}) if cases else {}
_HAS_NEW_KEYS = "fo_flip_direct_strict" in _sample_metrics
if not _HAS_NEW_KEYS:
    print("WARNING: results file lacks amber-mirror-lattice keys "
          "(fo_flip_*_strict/_hedged/_label, cpt_mode).", file=sys.stderr)
    print("WARNING: falling back to legacy fo_flip_direct/impact keys. "
          "Hedged variants will be SKIPPED.", file=sys.stderr)
    print("WARNING: re-run with --input data/results/diagnostic_2_results.rescored_v2.json "
          "for rescored data, or run Phase D for fresh results.", file=sys.stderr)

# Read canonical anchor field; default to anchor_level if no config file yet.
if STRATA_CONFIG_PATH.exists():
    strata_cfg = json.loads(STRATA_CONFIG_PATH.read_text(encoding="utf-8"))
    anchor_field = strata_cfg.get("analysis_anchor_field", "anchor_level")
else:
    anchor_field = "anchor_level"
print(f"Using anchor stratum field: {anchor_field!r}")

print("=== STATISTICAL TESTS ===")

# 1. CFLS Temporal Split
print("\n--- CFLS Temporal Split (Mann-Whitney U) ---")
for k in ["cfls_direct", "cfls_impact"]:
    pre = [c["metrics"][k] for c in cases if c["period"] == "pre_cutoff" and c["metrics"].get(k) is not None]
    post = [c["metrics"][k] for c in cases if c["period"] == "post_cutoff" and c["metrics"].get(k) is not None]
    if pre and post:
        u, p = stats.mannwhitneyu(pre, post, alternative="two-sided")
        r = u / (len(pre) * len(post))
        print(f"{k}: pre(n={len(pre)})={np.mean(pre):.3f} vs post(n={len(post)})={np.mean(post):.3f}")
        print(f"  U={u:.1f}, p={p:.4f}, effect_size_r={r:.3f}")

# 2. CFLS Rarity
print("\n--- CFLS by Rarity (Kruskal-Wallis) ---")
for k in ["cfls_direct", "cfls_impact"]:
    groups = {}
    for rarity in ["rare", "medium", "common"]:
        vals = [c["metrics"][k] for c in cases if c["rarity_estimate"] == rarity and c["metrics"].get(k) is not None]
        if vals:
            groups[rarity] = vals
    if len(groups) >= 2:
        H, p = stats.kruskal(*groups.values())
        print(f"{k}: H={H:.3f}, p={p:.4f}")
        for r, v in groups.items():
            print(f"  {r}: mean={np.mean(v):.3f}, n={len(v)}")

# 3. CPT Temporal Split
# Bug 3 fix: report both strict and hedged variants side by side. Strict
# matches the legacy bool (only opposite-polarity flips count); hedged adds
# "ORIG non-neutral, FO neutral" cases which the strict definition silently
# undercounted as memorization-direction signal.
print("\n--- CPT Temporal Split (Fisher exact) ---")
if _HAS_NEW_KEYS:
    FO_FLIP_VARIANTS = [
        ("fo_flip_direct_strict", "direct (strict)"),
        ("fo_flip_direct_hedged", "direct (hedged)"),
        ("fo_flip_impact_strict", "impact (strict)"),
        ("fo_flip_impact_hedged", "impact (hedged)"),
    ]
else:
    FO_FLIP_VARIANTS = [
        ("fo_flip_direct", "direct (legacy)"),
        ("fo_flip_impact", "impact (legacy)"),
    ]
for k, label in FO_FLIP_VARIANTS:
    pre_flip = sum(1 for c in cases if c["period"] == "pre_cutoff" and c["metrics"].get(k) is True)
    pre_total = sum(1 for c in cases if c["period"] == "pre_cutoff" and c["metrics"].get(k) is not None)
    post_flip = sum(1 for c in cases if c["period"] == "post_cutoff" and c["metrics"].get(k) is True)
    post_total = sum(1 for c in cases if c["period"] == "post_cutoff" and c["metrics"].get(k) is not None)
    if pre_total and post_total:
        odds, p = stats.fisher_exact([[pre_flip, pre_total - pre_flip], [post_flip, post_total - post_flip]])
        print(f"{label}:")
        print(f"  pre: {pre_flip}/{pre_total} ({pre_flip/pre_total:.1%})")
        print(f"  post: {post_flip}/{post_total} ({post_flip/post_total:.1%})")
        print(f"  Fisher: OR={odds:.3f}, p={p:.4f}")
    elif pre_total or post_total:
        print(f"{label}: skipped (pre_total={pre_total}, post_total={post_total})")

# 4. Cross-task CFLS correlation
print("\n--- Cross-task CFLS correlation ---")
paired = [
    (c["metrics"]["cfls_direct"], c["metrics"]["cfls_impact"])
    for c in cases
    if c["metrics"].get("cfls_direct") is not None and c["metrics"].get("cfls_impact") is not None
]
if paired:
    x, y = zip(*paired)
    rho, p = stats.spearmanr(x, y)
    print(f"Spearman rho={rho:.3f}, p={p:.4f}, n={len(paired)}")

# 5. Mantel-Haenszel stratified by anchor field
#    Primary inference for the temporal CPT effect: pooled OR + per-stratum
#    Fisher + Breslow-Day homogeneity. Cases with skipped/llm_failed CPT are
#    excluded automatically by the `is not None` filter.

def _mh_table_for_metric(metric_key: str):
    """Build a list of 2x2 tables (period x flip) per stratum for one metric."""
    stratum_tables: dict[str, dict[str, int]] = {}
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
        flip_label = "flip" if v else "noflip"
        stratum_tables.setdefault(s_str, {
            "pre_cutoff/flip": 0, "pre_cutoff/noflip": 0,
            "post_cutoff/flip": 0, "post_cutoff/noflip": 0,
        })
        stratum_tables[s_str][f"{period}/{flip_label}"] += 1

    arrays = []
    for s in sorted(stratum_tables.keys()):
        counts = stratum_tables[s]
        arr = np.array([
            [counts["pre_cutoff/flip"], counts["pre_cutoff/noflip"]],
            [counts["post_cutoff/flip"], counts["post_cutoff/noflip"]],
        ])
        arrays.append((s, arr))

    valid = [arr for _, arr in arrays
             if arr.sum(axis=0).min() > 0 and arr.sum(axis=1).min() > 0]
    if not valid:
        return None, arrays
    return StratifiedTable(valid), arrays


# 5b. CPT split by probe modality (Bug 5 fix)
# Pre and post arms are NOT clean apples-to-apples on probe shape:
#   - llm_negated: only pre cases with a real known_outcome (~115/606)
#   - generic_post_cutoff: ALL post + pre cases without a known_outcome (~491/606)
# This block reports flip rates within each cpt_mode so the reader can see
# the within-modality pattern next to the period split above.
print("\n--- CPT flip rate by probe modality (cpt_mode) ---")
from collections import Counter
cpt_mode_counts = Counter(c.get("cpt_mode") for c in cases)
print(f"  cpt_mode distribution: {dict(cpt_mode_counts)}")
for k, label in FO_FLIP_VARIANTS:
    print(f"  {label}:")
    for mode in sorted({c.get("cpt_mode") for c in cases} - {None}):
        bucket = [c for c in cases if c.get("cpt_mode") == mode]
        flip = sum(1 for c in bucket if c["metrics"].get(k) is True)
        total = sum(1 for c in bucket if c["metrics"].get(k) is not None)
        if total:
            print(f"    {mode:24s}  {flip}/{total} ({flip/total:.1%})")
        else:
            print(f"    {mode:24s}  no data")

print(f"\n--- Mantel-Haenszel stratified by {anchor_field} ---")
# Bug 3 fix: report both strict (legacy bool) and hedged (strict ∪ neutral
# retreat) variants for each task. Strict reproduces the v3 baseline; hedged
# adds the cases the strict definition undercounted.
_MH_KEYS = ([k for k, _ in FO_FLIP_VARIANTS] if _HAS_NEW_KEYS
            else ["fo_flip_direct", "fo_flip_impact"])
for k in _MH_KEYS:
    print(f"\n{k}:")
    mh, arrays = _mh_table_for_metric(k)
    stratum_ors = []
    for s, arr in arrays:
        n_total = int(arr.sum())
        try:
            t = Table2x2(arr)
            stratum_or = float(t.oddsratio)
            stratum_ors.append(stratum_or)
        except Exception:
            stratum_or = float("nan")
        try:
            _o, p_fisher = stats.fisher_exact(arr.tolist())
        except Exception:
            p_fisher = float("nan")
        pre_n = int(arr[0, 0] + arr[0, 1])
        post_n = int(arr[1, 0] + arr[1, 1])
        print(f"  stratum={s:8s}  n={n_total:4d}  "
              f"pre={int(arr[0,0])}/{pre_n}  post={int(arr[1,0])}/{post_n}  "
              f"OR={stratum_or:.3f}  Fisher_p={p_fisher:.4f}")

    if mh is not None:
        try:
            mh_or = float(mh.oddsratio_pooled)
            mh_test = mh.test_null_odds()
            mh_p = float(mh_test.pvalue)
            mh_z = float(mh_test.statistic)
            print(f"  POOLED MH:  OR={mh_or:.3f}  z={mh_z:.3f}  p={mh_p:.4f}")
            # Sanity check: pooled MH OR should sit within stratum OR range
            finite_ors = [o for o in stratum_ors if np.isfinite(o)]
            if finite_ors:
                lo, hi = min(finite_ors), max(finite_ors)
                in_range = lo <= mh_or <= hi
                marker = "OK" if in_range else "WARN"
                print(f"  Range check ({marker}): pooled {mh_or:.3f} vs stratum range [{lo:.3f}, {hi:.3f}]")
        except Exception as exc:
            print(f"  POOLED MH: failed ({exc})")
        try:
            bd = mh.test_equal_odds()
            print(f"  Breslow-Day homogeneity: stat={float(bd.statistic):.3f}  p={float(bd.pvalue):.4f}")
        except Exception as exc:
            print(f"  Breslow-Day homogeneity: failed ({exc})")
