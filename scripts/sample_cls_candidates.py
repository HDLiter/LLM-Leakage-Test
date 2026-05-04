"""Sample candidate events from CLS telegraph corpus for test case expansion.

Sampling strategy:
1. Post-cutoff events (2025-10+): ~35 candidates for temporal split diagnostic
2. Pre-cutoff rare/idiosyncratic events (2020-2025): ~35 candidates for rarity diagnostic
3. Pre-cutoff medium-frequency events: ~15 candidates to balance memorization_likelihood

Output: candidates JSON for Codex annotation.
"""

import json
import os
import random
from pathlib import Path
from collections import Counter

REPO_ROOT = Path(__file__).resolve().parents[1]
CLS_DIR = REPO_ROOT / "data" / "cls_telegraph_raw"
OUTPUT = REPO_ROOT / "data" / "seed" / "expansion_candidates.json"

random.seed(42)


def load_day(filepath: Path) -> list[dict]:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("items", [])


def is_substantive_a_share(item: dict) -> bool:
    """Filter for substantive A-share-relevant news."""
    content = item.get("content", "")
    title = item.get("title", "")
    text = title + content

    # Length filter
    if len(content) < 100:
        return False

    # Must be China/A-share relevant (broad filter)
    china_keywords = [
        "A股", "沪指", "深成指", "创业板", "上证", "深证", "科创板",
        "央行", "证监会", "发改委", "财政部", "国务院", "银保监",
        "降准", "降息", "LPR", "MLF", "逆回购", "国债",
        "板块", "涨停", "跌停", "市值", "股价", "净利润",
        "并购", "重组", "增发", "回购", "减持", "增持",
        "IPO", "ST", "退市", "停牌", "复牌",
        "基金", "社保", "北向", "外资", "融资融券",
        "产能", "营收", "业绩", "季报", "年报", "预告",
    ]
    if not any(kw in text for kw in china_keywords):
        return False

    # Exclude pure price tickers and very short telegraphs
    if text.startswith("【快讯】") and len(content) < 150:
        return False

    return True


def classify_rarity(item: dict) -> str:
    """Rough rarity classification based on content patterns."""
    content = item.get("content", "")
    title = item.get("title", "")
    text = title + content

    # High-frequency / common templates (policy, standard macro)
    common_patterns = [
        "降准", "降息", "LPR", "MLF", "逆回购", "存款准备金",
        "GDP", "CPI", "PMI", "社融", "M2",
        "季报", "年报", "业绩预告", "业绩快报",
        "北向资金", "融资融券", "两市成交",
    ]
    common_count = sum(1 for p in common_patterns if p in text)

    # Rare / idiosyncratic patterns
    rare_patterns = [
        "造假", "违规", "立案", "处罚", "退市", "ST",
        "爆雷", "暴雷", "违约", "破产", "重整",
        "事故", "召回", "安全", "泄露",
        "制裁", "禁令", "出口管制",
        "首次", "突破", "创新", "独家",
        "黑天鹅", "意外",
    ]
    rare_count = sum(1 for p in rare_patterns if p in text)

    if rare_count >= 2:
        return "rare"
    elif rare_count == 1 and common_count <= 1:
        return "rare"
    elif common_count >= 2:
        return "common"
    else:
        return "medium"


def sample_candidates():
    all_files = sorted([f for f in os.listdir(CLS_DIR) if f.endswith(".json") and f[0].isdigit()])

    post_cutoff_files = [f for f in all_files if f >= "2025-10"]
    pre_cutoff_files = [f for f in all_files if f < "2025-10"]

    print(f"Total files: {len(all_files)}")
    print(f"Pre-cutoff: {len(pre_cutoff_files)}, Post-cutoff: {len(post_cutoff_files)}")

    # ── 1. Post-cutoff candidates ──
    post_candidates = []
    for fname in post_cutoff_files:
        items = load_day(CLS_DIR / fname)
        for it in items:
            if is_substantive_a_share(it):
                it["_rarity"] = classify_rarity(it)
                it["_source_file"] = fname
                it["_period"] = "post_cutoff"
                post_candidates.append(it)

    print(f"\nPost-cutoff A-share items: {len(post_candidates)}")
    rarity_dist = Counter(c["_rarity"] for c in post_candidates)
    print(f"  Rarity distribution: {dict(rarity_dist)}")

    # Sample diverse post-cutoff: prefer rare/medium, spread across dates
    post_rare = [c for c in post_candidates if c["_rarity"] == "rare"]
    post_medium = [c for c in post_candidates if c["_rarity"] == "medium"]
    post_common = [c for c in post_candidates if c["_rarity"] == "common"]

    sampled_post = []
    sampled_post.extend(random.sample(post_rare, min(15, len(post_rare))))
    sampled_post.extend(random.sample(post_medium, min(12, len(post_medium))))
    sampled_post.extend(random.sample(post_common, min(8, len(post_common))))
    print(f"  Sampled post-cutoff: {len(sampled_post)}")

    # ── 2. Pre-cutoff rare/idiosyncratic candidates ──
    # Sample from spread of years
    pre_rare_candidates = []
    pre_medium_candidates = []

    # Sample 1 day per week to keep it manageable
    pre_sample_files = pre_cutoff_files[::7]  # every 7th day
    print(f"\nScanning {len(pre_sample_files)} pre-cutoff days (1 per week)...")

    for fname in pre_sample_files:
        items = load_day(CLS_DIR / fname)
        for it in items:
            if is_substantive_a_share(it):
                rarity = classify_rarity(it)
                it["_rarity"] = rarity
                it["_source_file"] = fname
                it["_period"] = "pre_cutoff"
                if rarity == "rare":
                    pre_rare_candidates.append(it)
                elif rarity == "medium":
                    pre_medium_candidates.append(it)

    print(f"Pre-cutoff rare items found: {len(pre_rare_candidates)}")
    print(f"Pre-cutoff medium items found: {len(pre_medium_candidates)}")

    # Sample pre-cutoff rare: spread across years
    sampled_pre_rare = random.sample(pre_rare_candidates, min(35, len(pre_rare_candidates)))

    # Sample pre-cutoff medium
    sampled_pre_medium = random.sample(pre_medium_candidates, min(15, len(pre_medium_candidates)))

    print(f"  Sampled pre-cutoff rare: {len(sampled_pre_rare)}")
    print(f"  Sampled pre-cutoff medium: {len(sampled_pre_medium)}")

    # ── Combine ──
    all_sampled = sampled_post + sampled_pre_rare + sampled_pre_medium

    # Clean up for output
    output_candidates = []
    for i, item in enumerate(all_sampled):
        output_candidates.append({
            "candidate_id": f"cand_{i+1:03d}",
            "title": item.get("title", ""),
            "content": item.get("content", ""),
            "publish_time": item.get("time", ""),
            "source_file": item["_source_file"],
            "period": item["_period"],
            "rarity_estimate": item["_rarity"],
            "cls_id": item.get("id", ""),
        })

    # Save
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump({"candidates": output_candidates, "count": len(output_candidates)}, f,
                  ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"Total candidates saved: {len(output_candidates)}")
    print(f"  Post-cutoff: {sum(1 for c in output_candidates if c['period']=='post_cutoff')}")
    print(f"  Pre-cutoff rare: {sum(1 for c in output_candidates if c['period']=='pre_cutoff' and c['rarity_estimate']=='rare')}")
    print(f"  Pre-cutoff medium: {sum(1 for c in output_candidates if c['period']=='pre_cutoff' and c['rarity_estimate']=='medium')}")
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    sample_candidates()
