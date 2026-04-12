"""V3 sampling: two-funnel (high-anchor + low-anchor) candidates for D2 expansion.

Why two funnels: the v2 strict filter rejects roundups, ETF marketing, and
template content -- which is exactly the Level 0/1 material we need to ground
the anchor stratification. So we run two independent funnels in parallel and
merge them at the end.

Outputs:
    data/seed/expansion_candidates_v3.json
        {
          "candidates":  [{candidate_id, funnel, period, ...}],
          "rejection_log": {funnel: {rule: count}},
          "n_high_anchor": int,
          "n_low_anchor":  int,
          "config":        {...}
        }
"""

from __future__ import annotations

import json
import random
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import jieba

# ── Configuration ────────────────────────────────────────────────────────────
CLS_DIR = Path("D:/GitRepos/Thales/datasets/cls_telegraph_raw")
OUTPUT = Path("D:/GitRepos/LLM-Leakage-Test/data/seed/expansion_candidates_v3.json")
EXISTING_CASES = Path("D:/GitRepos/LLM-Leakage-Test/data/seed/test_cases_expanded.json")

CUTOFF_DATE = "2025-10"  # files >= this are post-cutoff
TARGET_HIGH_PER_PERIOD = 125  # 125 pre + 125 post = 250 high-anchor total
TARGET_LOW_PER_PERIOD = 125   # 125 pre + 125 post = 250 low-anchor total

PRE_FILE_STRIDE = 5  # scan every Nth pre-cutoff day to keep runtime sane
SEED = 2026

# ── A-share anchors (used by both funnels for relevance) ─────────────────────
A_SHARE_ANCHORS = [
    "A股", "沪指", "深成指", "创业板", "科创板", "北交所", "上证",
    "板块", "概念股", "产业链", "受益", "利好", "利空",
    "SZ", "SH", "BJ",
]
STOCK_CODE_RE = re.compile(r"\(\d{6}\.\w{2}\)")

# ── High-anchor positive boosts (date / document patterns) ───────────────────
FULL_DATE_RE = re.compile(r"\d{4}年\d{1,2}月\d{1,2}日")
DOCUMENT_TITLE_RE = re.compile(r"《[^》]{6,}》")
NAMED_INSTITUTION_RE = re.compile(
    r"(中国人民银行|证监会|银保监会|国资委|国务院|发改委|财政部|"
    r"工信部|商务部|外汇局|央行|国新办|交易所|沪深交易所|"
    r"国务院国有资产监督管理委员会)"
)

# ── Filter rule signatures (kept here for both funnels & rejection logging) ──
ROUNDUP_SIGNALS = [
    "你需要知道的", "新闻精选", "热点复盘", "盘后总结",
    "隔夜全球", "早间必读", "新闻联播", "避雷针",
    "盘中快评", "主线快评", "热点轮动",
    "美股收盘", "美股盘前", "欧股收盘",
]
DATA_SIGNALS = [
    "北向资金今日净", "主力资金监控", "龙虎榜",
    "融资融券", "两市成交", "ETF规模",
    "限售股解禁", "停复牌", "涨停复盘", "跌停复盘",
    "基金规模", "申购额",
]
FOREIGN_ONLY = [
    "美联储", "欧央行", "英国央行", "日本央行", "瑞士央行",
    "波音", "苹果公司", "特斯拉公司", "英伟达",
]
OPINION_SIGNALS = [
    "券商表示", "分析师认为", "机构预计", "策略观点",
    "投行", "评级", "目标价",
    "业绩说明会", "互动平台",
]
ROUTINE_SIGNALS = [
    "监事减持", "0.0", "实用新型专利",
]

# Low-anchor positive signals (we WANT these for the low funnel)
LOW_ANCHOR_TEMPLATES = [
    "ETF", "指数基金", "宽基", "Smart Beta",
    "板块轮动", "热点切换", "结构性行情",
    "全市场策略", "行业配置", "主题投资",
    "今日两市", "今日A股", "盘面回顾", "盘面综述",
]


# ── Helpers ──────────────────────────────────────────────────────────────────
def _load_day(filepath: Path) -> list[dict]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f).get("items", [])
    except (json.JSONDecodeError, OSError):
        return []


def _file_date(fname: str) -> str:
    return fname[:10]


def _has_a_share_relevance(text: str) -> bool:
    if any(a in text for a in A_SHARE_ANCHORS):
        return True
    if STOCK_CODE_RE.search(text):
        return True
    return False


def _normalized_title_tokens(title: str) -> set[str]:
    """Tokenize title with jieba and drop pure punctuation/single-char tokens."""
    return {tok for tok in jieba.cut_for_search(title) if len(tok.strip()) >= 2}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


# ── High-anchor funnel filter ────────────────────────────────────────────────
def high_anchor_filter(item: dict, reject_log: dict[str, int]) -> bool:
    """Strict v2 filter + positive boost: must show date/document/institution cues."""
    content = item.get("content", "") or ""
    title = item.get("title", "") or ""
    text = title + content

    if len(content) < 120 or len(content) > 800:
        reject_log["length"] += 1
        return False
    if any(sig in text for sig in ROUNDUP_SIGNALS):
        reject_log["roundup"] += 1
        return False
    if text.count("；") >= 2 or text.count(";") >= 2:
        reject_log["multi_semicolon"] += 1
        return False
    if any(sig in text for sig in DATA_SIGNALS):
        reject_log["data_summary"] += 1
        return False
    if any(f in text for f in FOREIGN_ONLY) and not _has_a_share_relevance(text):
        reject_log["foreign_only"] += 1
        return False
    if not _has_a_share_relevance(text):
        reject_log["no_a_share"] += 1
        return False
    if sum(1 for sig in OPINION_SIGNALS if sig in text) >= 2:
        reject_log["pure_opinion"] += 1
        return False
    if any(sig in text for sig in ROUTINE_SIGNALS):
        reject_log["routine"] += 1
        return False

    # POSITIVE BOOST: must have at least one strong-anchor cue
    has_full_date = bool(FULL_DATE_RE.search(text))
    has_doc_title = bool(DOCUMENT_TITLE_RE.search(text))
    has_named_inst = bool(NAMED_INSTITUTION_RE.search(text))
    if not (has_full_date or has_doc_title or has_named_inst):
        reject_log["no_anchor_cue"] += 1
        return False

    return True


# ── Low-anchor funnel filter ─────────────────────────────────────────────────
def low_anchor_filter(item: dict, reject_log: dict[str, int]) -> bool:
    """Relaxed filter to keep roundups / ETF marketing / generic summaries."""
    content = item.get("content", "") or ""
    title = item.get("title", "") or ""
    text = title + content

    if len(content) < 80 or len(content) > 1200:
        reject_log["length"] += 1
        return False

    # Reject items that are *too* fact-heavy for "low anchor" — if they have
    # the high-anchor cues, send them to the high funnel only.
    if FULL_DATE_RE.search(text) or DOCUMENT_TITLE_RE.search(text):
        reject_log["has_high_anchor_cue"] += 1
        return False

    # Must still be A-share relevant (otherwise it's not in the study scope)
    if not _has_a_share_relevance(text):
        reject_log["no_a_share"] += 1
        return False

    # Reject obvious data dumps (those are not the "low anchor" we want either)
    if any(sig in text for sig in DATA_SIGNALS):
        reject_log["data_summary"] += 1
        return False

    # Reject foreign-only items
    if any(f in text for f in FOREIGN_ONLY) and not _has_a_share_relevance(text):
        reject_log["foreign_only"] += 1
        return False

    # POSITIVE for low anchor: roundup OR ETF/strategy template OR opinion-heavy
    has_roundup = any(sig in text for sig in ROUNDUP_SIGNALS)
    has_template = any(sig in text for sig in LOW_ANCHOR_TEMPLATES)
    has_opinion = sum(1 for sig in OPINION_SIGNALS if sig in text) >= 2
    if not (has_roundup or has_template or has_opinion):
        reject_log["no_low_anchor_cue"] += 1
        return False

    return True


# ── Event-level dedup (title-jaccard within a date window) ───────────────────
def event_level_dedup(
    items: list[dict],
    title_threshold: float = 0.65,
    date_window_days: int = 3,
) -> list[dict]:
    """Cluster near-duplicate events by title similarity within a date window.

    For each candidate, compare against earlier kept candidates with date
    within +/- date_window_days. If title-token Jaccard >= threshold, drop.
    """
    items_with_tokens = []
    for it in items:
        title = it.get("title", "") or ""
        tokens = _normalized_title_tokens(title)
        date_str = _file_date(it["_file"])
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        items_with_tokens.append((date, tokens, it))

    # Sort by date so earlier items have priority
    items_with_tokens.sort(key=lambda x: x[0])

    kept: list[tuple[Any, set[str], dict]] = []
    by_date: dict[Any, list[int]] = defaultdict(list)  # date -> kept indices

    for date, tokens, it in items_with_tokens:
        is_dup = False
        # Check against kept items within +/- window days
        for d_offset in range(-date_window_days, date_window_days + 1):
            check_date = date + timedelta(days=d_offset)
            for k_idx in by_date.get(check_date, []):
                if _jaccard(tokens, kept[k_idx][1]) >= title_threshold:
                    is_dup = True
                    break
            if is_dup:
                break
        if not is_dup:
            by_date[date].append(len(kept))
            kept.append((date, tokens, it))

    return [k[2] for k in kept]


def dedup_against_existing(items: list[dict], existing_titles: list[str]) -> list[dict]:
    """Drop items whose title is jaccard-similar to any existing case title."""
    existing_token_sets = [_normalized_title_tokens(t) for t in existing_titles]
    out = []
    for it in items:
        toks = _normalized_title_tokens(it.get("title", "") or "")
        if any(_jaccard(toks, e) >= 0.6 for e in existing_token_sets):
            continue
        out.append(it)
    return out


# ── Funnel runner ────────────────────────────────────────────────────────────
def run_funnel(
    funnel_name: str,
    filter_fn,
    pre_files: list[Path],
    post_files: list[Path],
    pre_target: int,
    post_target: int,
    rng: random.Random,
) -> tuple[list[dict], dict[str, int]]:
    reject_log: dict[str, int] = Counter()

    # ── Post-cutoff: scan ALL post days ──
    post_items = []
    for fpath in post_files:
        for it in _load_day(fpath):
            if filter_fn(it, reject_log):
                it["_file"] = fpath.name
                it["_period"] = "post_cutoff"
                post_items.append(it)
    print(f"  [{funnel_name}] post-cutoff candidates after filter: {len(post_items)}")

    # ── Pre-cutoff: scan strided pre days ──
    pre_items = []
    for fpath in pre_files:
        for it in _load_day(fpath):
            if filter_fn(it, reject_log):
                it["_file"] = fpath.name
                it["_period"] = "pre_cutoff"
                pre_items.append(it)
    print(f"  [{funnel_name}] pre-cutoff candidates after filter: {len(pre_items)}")

    # ── Dedup within funnel ──
    post_items = event_level_dedup(post_items)
    pre_items = event_level_dedup(pre_items)
    print(f"  [{funnel_name}] after event-level dedup: pre={len(pre_items)} post={len(post_items)}")

    # ── Sample to targets ──
    rng.shuffle(post_items)
    rng.shuffle(pre_items)
    sampled_post = post_items[:post_target]
    sampled_pre = pre_items[:pre_target]
    print(f"  [{funnel_name}] sampled: pre={len(sampled_pre)} post={len(sampled_post)}")

    return sampled_pre + sampled_post, dict(reject_log)


# ── Main ─────────────────────────────────────────────────────────────────────
def main() -> int:
    rng = random.Random(SEED)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    all_files = sorted(
        f for f in CLS_DIR.iterdir()
        if f.suffix == ".json" and f.name[0].isdigit()
    )
    pre_files_all = [f for f in all_files if _file_date(f.name) < CUTOFF_DATE]
    post_files = [f for f in all_files if _file_date(f.name) >= CUTOFF_DATE]
    pre_files_strided = pre_files_all[::PRE_FILE_STRIDE]
    print(f"CLS files: {len(all_files)} total | pre={len(pre_files_all)} (strided={len(pre_files_strided)}) | post={len(post_files)}")

    # ── Load existing case titles for cross-batch dedup ──
    existing = json.loads(EXISTING_CASES.read_text(encoding="utf-8"))
    existing_titles = [c["news"]["title"] for c in existing.get("test_cases", [])]
    print(f"Existing test cases (will dedupe against): {len(existing_titles)}")

    # ── Run high-anchor funnel ──
    print("\n=== HIGH-ANCHOR FUNNEL ===")
    high_items, high_reject = run_funnel(
        "high_anchor", high_anchor_filter,
        pre_files_strided, post_files,
        TARGET_HIGH_PER_PERIOD, TARGET_HIGH_PER_PERIOD, rng,
    )

    # ── Run low-anchor funnel ──
    print("\n=== LOW-ANCHOR FUNNEL ===")
    low_items, low_reject = run_funnel(
        "low_anchor", low_anchor_filter,
        pre_files_strided, post_files,
        TARGET_LOW_PER_PERIOD, TARGET_LOW_PER_PERIOD, rng,
    )

    # ── Cross-funnel + cross-existing dedup ──
    print("\n=== DEDUP ===")
    high_items = dedup_against_existing(high_items, existing_titles)
    low_items = dedup_against_existing(low_items, existing_titles)
    print(f"After dedup vs existing 192 cases: high={len(high_items)} low={len(low_items)}")

    # Then dedup low against high (high wins for any near-duplicate)
    high_titles = [it.get("title", "") for it in high_items]
    low_items = dedup_against_existing(low_items, high_titles)
    print(f"After dedup low vs high: low={len(low_items)}")

    # ── Tag with funnel + candidate_id ──
    candidates: list[dict] = []
    for it in high_items:
        candidates.append({
            "candidate_id": f"v3_h_{len(candidates)+1:03d}",
            "funnel": "high_anchor",
            "title": it.get("title", ""),
            "content": it.get("content", ""),
            "publish_time": it.get("time", ""),
            "source_file": it["_file"],
            "period": it["_period"],
            "cls_id": it.get("id", ""),
        })
    n_high_only = len(candidates)
    for it in low_items:
        candidates.append({
            "candidate_id": f"v3_l_{len(candidates) - n_high_only + 1:03d}",
            "funnel": "low_anchor",
            "title": it.get("title", ""),
            "content": it.get("content", ""),
            "publish_time": it.get("time", ""),
            "source_file": it["_file"],
            "period": it["_period"],
            "cls_id": it.get("id", ""),
        })
    rng.shuffle(candidates)

    # ── Final stats ──
    by_funnel = Counter(c["funnel"] for c in candidates)
    by_period = Counter(c["period"] for c in candidates)
    by_funnel_period = Counter((c["funnel"], c["period"]) for c in candidates)

    payload = {
        "candidates": candidates,
        "rejection_log": {
            "high_anchor": high_reject,
            "low_anchor": low_reject,
        },
        "n_high_anchor": by_funnel.get("high_anchor", 0),
        "n_low_anchor": by_funnel.get("low_anchor", 0),
        "by_funnel_period": {f"{k[0]}/{k[1]}": v for k, v in by_funnel_period.items()},
        "config": {
            "cutoff_date": CUTOFF_DATE,
            "target_high_per_period": TARGET_HIGH_PER_PERIOD,
            "target_low_per_period": TARGET_LOW_PER_PERIOD,
            "pre_file_stride": PRE_FILE_STRIDE,
            "seed": SEED,
            "dedup_jaccard_threshold": 0.65,
            "dedup_date_window_days": 3,
        },
    }

    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"Total candidates: {len(candidates)}")
    print(f"  By funnel: {dict(by_funnel)}")
    print(f"  By period: {dict(by_period)}")
    print(f"  By (funnel,period): {dict(by_funnel_period)}")
    print(f"\nRejection log:")
    for funnel_name, log in (("high_anchor", high_reject), ("low_anchor", low_reject)):
        print(f"  [{funnel_name}]")
        for rule, count in sorted(log.items(), key=lambda x: -x[1]):
            print(f"    {rule:25s} {count:>6,}")
    print(f"\nOutput: {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
