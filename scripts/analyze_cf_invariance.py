"""Decompose CFLS into cf_invariance / para_invariance 4-cell analysis."""
import json
import numpy as np
from collections import Counter

with open("data/results/diagnostic_2_results.json", "r", encoding="utf-8") as f:
    d = json.load(f)
cases = d["cases"]

for task_key in ["direct_prediction.base", "decomposed_impact.base"]:
    print(f"\n{'='*60}")
    print(f"Task: {task_key}")
    print(f"{'='*60}")

    records = []
    for c in cases:
        cfls_data = c["tasks"].get(task_key, {}).get("cfls", {})
        ci = cfls_data.get("cf_invariance")
        pi = cfls_data.get("para_invariance")
        cfls = cfls_data.get("cfls")
        if ci is None or pi is None:
            continue
        records.append({
            "case_id": c["case_id"],
            "cf_inv": ci,
            "para_inv": pi,
            "cfls": cfls,
            "period": c.get("period", "?"),
            "rarity": c.get("rarity_estimate", "?"),
            "memo": c.get("memorization_likelihood", "?"),
            "per_slot": cfls_data.get("per_slot", {}),
        })

    print(f"Total scored: {len(records)}")
    if not records:
        print("  (no scored records, skipping)\n")
        continue

    # 4-cell analysis
    red_flag = [r for r in records if r["cf_inv"] == 1.0 and r["para_inv"] < 1.0]
    global_inv = [r for r in records if r["cf_inv"] == 1.0 and r["para_inv"] == 1.0]
    healthy = [r for r in records if r["cf_inv"] < 1.0 and r["para_inv"] == 1.0]
    unstable = [r for r in records if r["cf_inv"] < 1.0 and r["para_inv"] < 1.0]

    print(f"\n4-CELL BREAKDOWN:")
    print(f"  RED FLAG  (cf=1, para<1): {len(red_flag):3d} ({len(red_flag)/len(records):.1%}) ← strongest memorization candidates")
    print(f"  GLOBAL_INV(cf=1, para=1): {len(global_inv):3d} ({len(global_inv)/len(records):.1%}) ← model ignores everything")
    print(f"  HEALTHY   (cf<1, para=1): {len(healthy):3d} ({len(healthy)/len(records):.1%}) ← good: follows reversal, stable on paraphrase")
    print(f"  UNSTABLE  (cf<1, para<1): {len(unstable):3d} ({len(unstable)/len(records):.1%}) ← general instability")

    # cf_invariance distribution
    ci_vals = [r["cf_inv"] for r in records]
    print(f"\ncf_invariance: mean={np.mean(ci_vals):.3f}, values={dict(sorted(Counter(ci_vals).items()))}")

    # Red flag cases detail
    if red_flag:
        print(f"\nRED FLAG CASES (model ignores reversal but responds to paraphrase):")
        for r in red_flag[:10]:
            print(f"  {r['case_id']}: cf_inv={r['cf_inv']}, para_inv={r['para_inv']}, "
                  f"period={r['period']}, rarity={r['rarity']}, memo={r['memo']}")
            for slot, sv in r["per_slot"].items():
                print(f"    {slot}: orig={sv['orig']} → cf={sv['cf']} / para={sv['para']}")

    # Global invariance cases
    if global_inv:
        print(f"\nGLOBAL INVARIANCE CASES (same answer on everything):")
        for r in global_inv[:10]:
            print(f"  {r['case_id']}: period={r['period']}, rarity={r['rarity']}, memo={r['memo']}")
            for slot, sv in r["per_slot"].items():
                print(f"    {slot}: orig={sv['orig']} → cf={sv['cf']} / para={sv['para']}")

    # By period
    print(f"\nBY PERIOD:")
    for period in ["pre_cutoff", "post_cutoff"]:
        sub = [r for r in records if r["period"] == period]
        if not sub:
            continue
        rf = sum(1 for r in sub if r["cf_inv"] == 1.0 and r["para_inv"] < 1.0)
        gi = sum(1 for r in sub if r["cf_inv"] == 1.0 and r["para_inv"] == 1.0)
        h = sum(1 for r in sub if r["cf_inv"] < 1.0 and r["para_inv"] == 1.0)
        u = sum(1 for r in sub if r["cf_inv"] < 1.0 and r["para_inv"] < 1.0)
        print(f"  {period} (n={len(sub)}): RED={rf} GLOBAL={gi} HEALTHY={h} UNSTABLE={u}")

    # By rarity
    print(f"\nBY RARITY:")
    for rarity in ["rare", "medium", "common"]:
        sub = [r for r in records if r["rarity"] == rarity]
        if not sub:
            continue
        rf = sum(1 for r in sub if r["cf_inv"] == 1.0 and r["para_inv"] < 1.0)
        gi = sum(1 for r in sub if r["cf_inv"] == 1.0 and r["para_inv"] == 1.0)
        h = sum(1 for r in sub if r["cf_inv"] < 1.0 and r["para_inv"] == 1.0)
        u = sum(1 for r in sub if r["cf_inv"] < 1.0 and r["para_inv"] < 1.0)
        ci_mean = np.mean([r["cf_inv"] for r in sub])
        print(f"  {rarity} (n={len(sub)}): RED={rf} GLOBAL={gi} HEALTHY={h} UNSTABLE={u} | cf_inv_mean={ci_mean:.3f}")
