"""Quick statistical analysis of D2 results."""
import json
import numpy as np
from scipy import stats

with open("data/results/diagnostic_2_results.json", "r", encoding="utf-8") as f:
    d = json.load(f)
cases = d["cases"]

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
print("\n--- CPT Temporal Split (Fisher exact) ---")
for k in ["fo_flip_direct", "fo_flip_impact"]:
    pre_flip = sum(1 for c in cases if c["period"] == "pre_cutoff" and c["metrics"].get(k) is True)
    pre_total = sum(1 for c in cases if c["period"] == "pre_cutoff" and c["metrics"].get(k) is not None)
    post_flip = sum(1 for c in cases if c["period"] == "post_cutoff" and c["metrics"].get(k) is True)
    post_total = sum(1 for c in cases if c["period"] == "post_cutoff" and c["metrics"].get(k) is not None)
    if pre_total and post_total:
        odds, p = stats.fisher_exact([[pre_flip, pre_total - pre_flip], [post_flip, post_total - post_flip]])
        print(f"{k}:")
        print(f"  pre: {pre_flip}/{pre_total} ({pre_flip/pre_total:.1%})")
        print(f"  post: {post_flip}/{post_total} ({post_flip/post_total:.1%})")
        print(f"  Fisher: OR={odds:.3f}, p={p:.4f}")

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

# 5. CFLS by memorization likelihood
print("\n--- CFLS by Memorization Likelihood (Kruskal-Wallis) ---")
for k in ["cfls_direct", "cfls_impact"]:
    groups = {}
    for memo in ["high", "medium", "low"]:
        vals = [c["metrics"][k] for c in cases if c["memorization_likelihood"] == memo and c["metrics"].get(k) is not None]
        if vals:
            groups[memo] = vals
    if len(groups) >= 2:
        H, p = stats.kruskal(*groups.values())
        print(f"{k}: H={H:.3f}, p={p:.4f}")
        for m, v in groups.items():
            print(f"  {m}: mean={np.mean(v):.3f}, n={len(v)}")
