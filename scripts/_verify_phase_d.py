"""Verify Phase D results: new fields, CF failure rate, fo_flip counts."""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "results" / "diagnostic_2_results.json"
OLD_PATH = ROOT / "data" / "results" / "diagnostic_2_results.v3_pre_amber.json"

d = json.loads(PATH.read_text(encoding="utf-8"))
meta = d["meta"]
cases = d["cases"]

print(f"=== Phase D verification ===")
print(f"n_cases: {len(cases)}")
print(f"pipeline_version: {meta.get('pipeline_version')}")
print(f"n_case_errors: {meta.get('n_case_errors')}")
print()

# New meta fields
print("=== Bug 2: meta surface ===")
for k in ("n_total_cases", "n_cf_failed_by_type"):
    print(f"  {k}: {meta.get(k)}")

# CF failure rate comparison
print()
print("=== Bug 1: CF failure rate ===")
cf_fail = meta.get("n_cf_failed_by_type", {})
total = len(cases)
for cf_type, n in cf_fail.items():
    print(f"  {cf_type}: {n}/{total} ({100*n/total:.1f}%)")
total_cf_prompts = total * 3
total_cf_fails = sum(cf_fail.values())
print(f"  TOTAL CF failures: {total_cf_fails}/{total_cf_prompts} ({100*total_cf_fails/total_cf_prompts:.1f}%)")

# fo_flip label distribution
print()
print("=== Bug 3: fo_flip label distribution ===")
for suffix in ("direct", "impact"):
    labels = [c["metrics"].get(f"fo_flip_{suffix}_label") for c in cases]
    cnt = Counter(labels)
    print(f"  {suffix}: {dict(cnt)}")

# fo_flip strict vs hedged rates by period
print()
print("=== Bug 3: strict vs hedged by period ===")
for suffix in ("direct", "impact"):
    for variant in ("strict", "hedged"):
        key = f"fo_flip_{suffix}_{variant}"
        pre_flip = sum(1 for c in cases if c["period"] == "pre_cutoff" and c["metrics"].get(key) is True)
        pre_total = sum(1 for c in cases if c["period"] == "pre_cutoff" and c["metrics"].get(key) is not None)
        post_flip = sum(1 for c in cases if c["period"] == "post_cutoff" and c["metrics"].get(key) is True)
        post_total = sum(1 for c in cases if c["period"] == "post_cutoff" and c["metrics"].get(key) is not None)
        print(f"  {key}: pre={pre_flip}/{pre_total} post={post_flip}/{post_total}")

# cpt_mode distribution
print()
print("=== Bug 5: cpt_mode distribution ===")
print(f"  {dict(Counter(c.get('cpt_mode') for c in cases))}")

# Compare CFLS with v3 baseline
print()
print("=== CFLS comparison (new vs v3 baseline) ===")
old_d = json.loads(OLD_PATH.read_text(encoding="utf-8"))
old_cases = old_d["cases"]
for task in ("cfls_direct", "cfls_impact"):
    new_scored = [c["metrics"][task] for c in cases if c["metrics"].get(task) is not None]
    old_scored = [c["metrics"][task] for c in old_cases if c["metrics"].get(task) is not None]
    import numpy as np
    print(f"  {task}:")
    print(f"    v3: n={len(old_scored)} mean={np.mean(old_scored):.3f}")
    print(f"    new: n={len(new_scored)} mean={np.mean(new_scored):.3f}")
    print(f"    Δn_scored: {len(new_scored) - len(old_scored)}")
