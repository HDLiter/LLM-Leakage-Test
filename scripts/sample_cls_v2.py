"""V2 sampling: much stricter pre-filtering to avoid Codex rejections.
Target: 200 candidates → expect ~60-70 annotated cases after Codex review.
"""

import json
import os
import random
from pathlib import Path
from collections import Counter

CLS_DIR = Path("D:/GitRepos/Thales/datasets/cls_telegraph_raw")
OUTPUT = Path("D:/GitRepos/LLM-Leakage-Test/data/seed/expansion_candidates_v2.json")

random.seed(2026)


def load_day(filepath: Path) -> list[dict]:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("items", [])


def is_single_event_a_share(item: dict) -> bool:
    """Strict filter: single-event A-share news with clear market catalyst."""
    content = item.get("content", "")
    title = item.get("title", "")
    text = title + content

    # Length: not too short (telegrams) or too long (roundups)
    if len(content) < 120 or len(content) > 800:
        return False

    # REJECT multi-event roundups
    roundup_signals = [
        "你需要知道的", "新闻精选", "热点复盘", "盘后总结",
        "隔夜全球", "早间必读", "新闻联播", "避雷针",
        "盘中快评", "主线快评", "热点轮动",
        "美股收盘", "美股盘前", "欧股收盘",
        "；", "；",  # multiple semicolons = multi-event
    ]
    if any(sig in text for sig in roundup_signals):
        return False
    # Count semicolons - roundups often have 3+
    if text.count("；") >= 2 or text.count(";") >= 2:
        return False

    # REJECT pure data summaries
    data_signals = [
        "北向资金今日净", "主力资金监控", "龙虎榜",
        "融资融券", "两市成交", "ETF规模",
        "限售股解禁", "停复牌", "涨停复盘", "跌停复盘",
        "基金规模", "申购额",
    ]
    if any(sig in text for sig in data_signals):
        return False

    # REJECT foreign-only news
    foreign_only = [
        "美联储", "欧央行", "英国央行", "日本央行", "瑞士央行",
        "波音", "苹果公司", "特斯拉公司", "英伟达",
    ]
    # Only reject if no A-share connection mentioned
    a_share_anchors = [
        "A股", "沪指", "深成指", "创业板", "科创板", "北交所",
        "板块", "概念股", "产业链", "受益", "利好", "利空",
        "SZ", "SH", "BJ",  # stock codes
    ]
    if any(f in text for f in foreign_only) and not any(a in text for a in a_share_anchors):
        return False

    # MUST have at least one A-share anchor
    if not any(a in text for a in a_share_anchors):
        # Check for specific company announcements (stock codes)
        import re
        if not re.search(r'\(\d{6}\.\w{2}\)', text):
            return False

    # REJECT generic commentary / opinions
    opinion_signals = [
        "券商表示", "分析师认为", "机构预计", "策略观点",
        "投行", "评级", "目标价",
        "业绩说明会", "互动平台",
    ]
    if sum(1 for sig in opinion_signals if sig in text) >= 2:
        return False

    # REJECT routine small announcements
    routine_signals = [
        "监事减持", "0.0", "实用新型专利",
    ]
    if any(sig in text for sig in routine_signals):
        return False

    return True


def classify_rarity(item: dict) -> str:
    content = item.get("content", "")
    title = item.get("title", "")
    text = title + content

    # High-frequency templates
    common_patterns = [
        "降准", "降息", "LPR", "MLF", "逆回购", "存款准备金",
        "GDP", "CPI", "PMI", "社融", "M2",
        "季报", "年报", "业绩预告", "业绩快报",
    ]
    common_count = sum(1 for p in common_patterns if p in text)

    # Rare / idiosyncratic
    rare_patterns = [
        "造假", "违规", "立案", "处罚", "退市", "ST",
        "爆雷", "暴雷", "违约", "破产", "重整",
        "事故", "召回", "安全事件", "数据泄露",
        "制裁", "禁令", "出口管制", "实体清单",
        "首次", "突破", "创纪录", "历史新高", "历史新低",
        "并购", "收购", "重组", "借壳",
        "暴跌", "暴涨", "涨停", "跌停",
        "调查", "问询", "警示",
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


def sample():
    all_files = sorted([f for f in os.listdir(CLS_DIR) if f.endswith(".json") and f[0].isdigit()])
    post_cutoff_files = [f for f in all_files if f >= "2025-10"]
    pre_cutoff_files = [f for f in all_files if f < "2025-10"]

    print(f"Files: {len(pre_cutoff_files)} pre-cutoff, {len(post_cutoff_files)} post-cutoff")

    # ── Post-cutoff: scan ALL days ──
    post_items = []
    for fname in post_cutoff_files:
        for it in load_day(CLS_DIR / fname):
            if is_single_event_a_share(it):
                it["_rarity"] = classify_rarity(it)
                it["_file"] = fname
                it["_period"] = "post_cutoff"
                post_items.append(it)

    print(f"\nPost-cutoff candidates after strict filter: {len(post_items)}")
    print(f"  Rarity: {Counter(c['_rarity'] for c in post_items)}")

    # Sample 70 post-cutoff
    post_rare = [c for c in post_items if c["_rarity"] == "rare"]
    post_med = [c for c in post_items if c["_rarity"] == "medium"]
    post_com = [c for c in post_items if c["_rarity"] == "common"]
    sampled_post = []
    sampled_post.extend(random.sample(post_rare, min(30, len(post_rare))))
    sampled_post.extend(random.sample(post_med, min(25, len(post_med))))
    sampled_post.extend(random.sample(post_com, min(15, len(post_com))))

    # ── Pre-cutoff: scan every 5th day ──
    pre_items_rare = []
    pre_items_med = []
    pre_sample_files = pre_cutoff_files[::5]
    print(f"\nScanning {len(pre_sample_files)} pre-cutoff days...")

    for fname in pre_sample_files:
        for it in load_day(CLS_DIR / fname):
            if is_single_event_a_share(it):
                rarity = classify_rarity(it)
                it["_rarity"] = rarity
                it["_file"] = fname
                it["_period"] = "pre_cutoff"
                if rarity == "rare":
                    pre_items_rare.append(it)
                elif rarity == "medium":
                    pre_items_med.append(it)

    print(f"Pre-cutoff rare: {len(pre_items_rare)}, medium: {len(pre_items_med)}")

    sampled_pre_rare = random.sample(pre_items_rare, min(70, len(pre_items_rare)))
    sampled_pre_med = random.sample(pre_items_med, min(30, len(pre_items_med)))

    # ── Combine ──
    all_sampled = sampled_post + sampled_pre_rare + sampled_pre_med
    random.shuffle(all_sampled)

    output = []
    for i, it in enumerate(all_sampled):
        output.append({
            "candidate_id": f"v2_{i+1:03d}",
            "title": it.get("title", ""),
            "content": it.get("content", ""),
            "publish_time": it.get("time", ""),
            "source_file": it["_file"],
            "period": it["_period"],
            "rarity_estimate": it["_rarity"],
            "cls_id": it.get("id", ""),
        })

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump({"candidates": output, "count": len(output)}, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"Total candidates: {len(output)}")
    periods = Counter(c["period"] for c in output)
    rarities = Counter(c["rarity_estimate"] for c in output)
    print(f"  By period: {dict(periods)}")
    print(f"  By rarity: {dict(rarities)}")
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    sample()
