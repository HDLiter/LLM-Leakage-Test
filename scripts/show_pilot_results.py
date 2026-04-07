"""Display E_pilot results summary."""
import json
import numpy as np
from pathlib import Path

d = json.loads(Path("data/results/pilot_results.json").read_text(encoding="utf-8"))
cases = d["cases"]
agg = d["aggregated"]

print("=== E_PILOT RESULTS ===")
print(f"Total cases: {len(cases)}")
print()

for tid, stats in agg["by_task"].items():
    print(f"{tid}:")
    print(f"  mean={stats['mean']:.3f}  std={stats['std']:.3f}  median={stats['median']:.3f}")
    print(f"  positive_rate={stats['positive_rate']:.1%}  n={stats['count']}")

print(f"\nCorrelation: {agg.get('correlation')}")
print(f"Correlation n_paired: {agg.get('correlation_n_paired')}")

fo_d = [c["metrics"]["fo_flip_direct"] for c in cases if c["metrics"]["fo_flip_direct"] is not None]
fo_i = [c["metrics"]["fo_flip_impact"] for c in cases if c["metrics"]["fo_flip_impact"] is not None]
print(f"\nFalse-outcome flip:")
print(f"  direct: {sum(fo_d)}/{len(fo_d)} ({sum(fo_d)/len(fo_d):.1%})")
print(f"  impact: {sum(fo_i)}/{len(fo_i)} ({sum(fo_i)/len(fo_i):.1%})")

ei_d = sum(1 for c in cases if c["metrics"]["intrusion_direct"])
ei_i = sum(1 for c in cases if c["metrics"]["intrusion_impact"])
print(f"\nEvidence intrusion detected:")
print(f"  direct: {ei_d}/{len(cases)}")
print(f"  impact: {ei_i}/{len(cases)}")

print("\n--- CFLS by target_type ---")
for tt in ["company", "sector", "index"]:
    subset = [c for c in cases if c["target_type"] == tt]
    d_scores = [c["metrics"]["cfls_direct"] for c in subset if c["metrics"]["cfls_direct"] is not None]
    i_scores = [c["metrics"]["cfls_impact"] for c in subset if c["metrics"]["cfls_impact"] is not None]
    if d_scores:
        print(f"  {tt} (n={len(subset)}): direct={np.mean(d_scores):.3f}  impact={np.mean(i_scores):.3f}")

print("\n--- CFLS by memorization_likelihood ---")
for ml in ["high", "medium", "low"]:
    subset = [c for c in cases if c["memorization_likelihood"] == ml]
    d_scores = [c["metrics"]["cfls_direct"] for c in subset if c["metrics"]["cfls_direct"] is not None]
    i_scores = [c["metrics"]["cfls_impact"] for c in subset if c["metrics"]["cfls_impact"] is not None]
    if d_scores:
        print(f"  {ml} (n={len(subset)}): direct={np.mean(d_scores):.3f}  impact={np.mean(i_scores):.3f}")

print("\n--- CFLS by category ---")
for cat in ["policy", "corporate", "industry", "macro"]:
    subset = [c for c in cases if c["category"] == cat]
    d_scores = [c["metrics"]["cfls_direct"] for c in subset if c["metrics"]["cfls_direct"] is not None]
    i_scores = [c["metrics"]["cfls_impact"] for c in subset if c["metrics"]["cfls_impact"] is not None]
    if d_scores:
        print(f"  {cat} (n={len(subset)}): direct={np.mean(d_scores):.3f}  impact={np.mean(i_scores):.3f}")
