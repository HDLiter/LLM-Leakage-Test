"""Verify the smoke-test output has all the new fields from Phase B."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "results" / "_smoke_test.json"

d = json.loads(PATH.read_text(encoding="utf-8"))
meta = d["meta"]
cases = d["cases"]

print(f"Smoke test n_cases: {len(cases)}")
print(f"pipeline_version: {meta.get('pipeline_version')}")
print()

print("=== Bug 2 fix: meta surface ===")
for k in ("n_total_cases", "n_cf_failed_by_type", "cf_failed_by_stratum",
          "n_total_by_stratum", "n_scored_by_task_x_stratum"):
    val = meta.get(k)
    if val is None:
        print(f"  MISSING: {k}")
    else:
        print(f"  {k}: {val}")

print()
print("=== Bug 3 fix: per-case metrics fields ===")
c0 = cases[0]
print(f"  case_id: {c0['case_id']}")
print(f"  cpt_mode (Bug 5): {c0.get('cpt_mode')}")
m = c0.get("metrics", {})
expected_keys = (
    "fo_flip_direct", "fo_flip_direct_strict", "fo_flip_direct_hedged",
    "fo_flip_direct_label", "fo_flip_impact", "fo_flip_impact_strict",
    "fo_flip_impact_hedged", "fo_flip_impact_label",
)
for k in expected_keys:
    if k in m:
        print(f"  {k}: {m[k]}")
    else:
        print(f"  MISSING: {k}")

print()
print("=== Bug 5 fix: cpt_mode distribution across all 10 cases ===")
from collections import Counter
print(" ", dict(Counter(c.get("cpt_mode") for c in cases)))

# Per case label distribution for fo_flip_direct
print()
print("=== Per-case label distribution (direct/impact) ===")
print("  direct labels:", dict(Counter(
    c.get("metrics", {}).get("fo_flip_direct_label") for c in cases
)))
print("  impact labels:", dict(Counter(
    c.get("metrics", {}).get("fo_flip_impact_label") for c in cases
)))

# CF failure rate
print()
print("=== Bug 1 verification: CF failure rate ===")
for cf in ("sr_direction", "sr_fund_impact", "neutral_paraphrase"):
    n = meta.get("n_cf_failed_by_type", {}).get(cf, 0)
    print(f"  {cf}: {n}/{len(cases)} ({100*n/len(cases):.1f}%)")
