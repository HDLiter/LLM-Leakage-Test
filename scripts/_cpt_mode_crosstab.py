"""Compute period × cpt_mode cross-table for impact_hedged."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
d = json.loads((ROOT / "data/results/diagnostic_2_results.json").read_text(encoding="utf-8"))
cases = d["cases"]

for suffix in ("direct", "impact"):
    key = f"fo_flip_{suffix}_hedged"
    print(f"=== {key} by period × cpt_mode ===")
    for period in ("pre_cutoff", "post_cutoff"):
        for mode in ("llm_negated", "generic_post_cutoff"):
            bucket = [c for c in cases if c.get("period") == period and c.get("cpt_mode") == mode]
            flip = sum(1 for c in bucket if c["metrics"].get(key) is True)
            total = sum(1 for c in bucket if c["metrics"].get(key) is not None)
            if total:
                print(f"  {period:12s} / {mode:24s}: {flip:3d}/{total:3d} ({100*flip/total:5.1f}%)")
            else:
                print(f"  {period:12s} / {mode:24s}: no cases")
    print()
