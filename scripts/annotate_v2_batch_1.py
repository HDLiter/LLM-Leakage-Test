from __future__ import annotations

import json
import time as time_module
from datetime import datetime, time
from pathlib import Path
from typing import Any

import akshare as ak
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
BATCH_PATH = ROOT / "data" / "seed" / "v2_batch_1.json"
FULL_PATH = ROOT / "data" / "seed" / "expansion_candidates_v2.json"
OUTPUT_PATH = ROOT / "data" / "seed" / "v2_annotated_1.json"


KEPT: list[dict[str, Any]] = [
    {
        "candidate_id": "v2_001",
        "category": "corporate",
        "sector": "医疗器械/医疗冷链",
        "key_entities": ["海尔生物", "奇君投资", "简式权益变动报告书"],
        "key_numbers": ["1585.72万股", "5.00%", "2020年2月28日-2021年9月22日"],
        "expected_direction": "down",
        "subcategory": "股东减持",
        "memorization_likelihood": "low",
        "target": "海尔生物",
        "target_type": "company",
        "proxy_kind": "company",
        "proxy_symbol": "sh688139",
    },
    {
        "candidate_id": "v2_004",
        "category": "policy",
        "sector": "低空经济/人工智能",
        "key_entities": ["国家发展改革委", "肖渭明", "人工智能+", "低空经济"],
        "key_numbers": ["2025-2026中国经济年会"],
        "expected_direction": "up",
        "subcategory": "产业政策表态",
        "memorization_likelihood": "medium",
        "target": "低空经济板块",
        "target_type": "sector",
    },
    {
        "candidate_id": "v2_005",
        "category": "corporate",
        "sector": "家居装饰",
        "key_entities": ["联翔股份", "彭小红", "周红芳"],
        "key_numbers": ["第三届董事会", "第三届董事会审计委员会第十次会议"],
        "expected_direction": "neutral",
        "subcategory": "高管变更",
        "memorization_likelihood": "low",
        "target": "联翔股份",
        "target_type": "company",
        "proxy_kind": "company",
        "proxy_symbol": "sh603272",
    },
    {
        "candidate_id": "v2_006",
        "category": "industry",
        "sector": "科技成长/算力芯片",
        "key_entities": ["科创50", "工业富联", "海光信息", "寒武纪"],
        "key_numbers": ["2连板", "20CM涨停"],
        "expected_direction": "up",
        "subcategory": "科技主线强化",
        "memorization_likelihood": "medium",
        "target": "科创50指数",
        "target_type": "index",
        "proxy_kind": "index",
        "proxy_symbol": "sh000688",
        "same_day": True,
    },
    {
        "candidate_id": "v2_007",
        "category": "corporate",
        "sector": "数字营销/AI应用",
        "key_entities": ["利欧股份", "广告素材审核智能体", "多模态内容"],
        "key_numbers": ["9天6板"],
        "expected_direction": "up",
        "subcategory": "AI应用能力披露",
        "memorization_likelihood": "medium",
        "target": "利欧股份",
        "target_type": "company",
    },
    {
        "candidate_id": "v2_008",
        "category": "corporate",
        "sector": "ST重整/装饰工程",
        "key_entities": ["*ST建艺", "珠海正方集团"],
        "key_numbers": ["14亿元", "889.67万元", "4亿元"],
        "expected_direction": "up",
        "subcategory": "控股股东债务豁免与资产赠与",
        "memorization_likelihood": "medium",
        "target": "*ST建艺",
        "target_type": "company",
    },
    {
        "candidate_id": "v2_009",
        "category": "industry",
        "sector": "AI应用/短线情绪",
        "key_entities": ["DeepSeek概念", "杭钢股份"],
        "key_numbers": ["炸板率近40%"],
        "expected_direction": "down",
        "subcategory": "题材退潮",
        "memorization_likelihood": "low",
        "target": "杭钢股份",
        "target_type": "company",
        "proxy_kind": "company",
        "proxy_symbol": "sh600126",
        "same_day": True,
    },
    {
        "candidate_id": "v2_010",
        "category": "corporate",
        "sector": "新能源汽车",
        "key_entities": ["长安汽车", "深蓝汽车", "重庆产交所"],
        "key_numbers": ["61.22亿元", "31.22亿元"],
        "expected_direction": "up",
        "subcategory": "子公司增资扩股",
        "memorization_likelihood": "medium",
        "target": "长安汽车",
        "target_type": "company",
    },
    {
        "candidate_id": "v2_011",
        "category": "corporate",
        "sector": "精细化工",
        "key_entities": ["元利科技", "山东抱一科技有限公司"],
        "key_numbers": ["500万元"],
        "expected_direction": "neutral",
        "subcategory": "设立全资子公司",
        "memorization_likelihood": "low",
        "target": "元利科技",
        "target_type": "company",
    },
    {
        "candidate_id": "v2_012",
        "category": "corporate",
        "sector": "光学材料/激光晶体",
        "key_entities": ["腾景科技", "合肥众波", "YVO4产品"],
        "key_numbers": ["8760.60万元"],
        "expected_direction": "up",
        "subcategory": "大额订单",
        "memorization_likelihood": "low",
        "target": "腾景科技",
        "target_type": "company",
    },
    {
        "candidate_id": "v2_013",
        "category": "industry",
        "sector": "半导体芯片",
        "key_entities": ["中国银河证券", "存储芯片", "国产替代"],
        "key_numbers": ["中证半导体材料设备主题指数下跌1.0%"],
        "expected_direction": "up",
        "subcategory": "赛道景气研判",
        "memorization_likelihood": "medium",
        "target": "科创芯片指数",
        "target_type": "index",
    },
    {
        "candidate_id": "v2_014",
        "category": "corporate",
        "sector": "智能按摩/消费电子",
        "key_entities": ["倍轻松", "科创板IPO"],
        "key_numbers": ["1541万股", "25.00%", "6164万股"],
        "expected_direction": "up",
        "subcategory": "IPO发行安排",
        "memorization_likelihood": "low",
        "target": "倍轻松",
        "target_type": "company",
        "proxy_kind": "company",
        "proxy_symbol": "sh688793",
    },
    {
        "candidate_id": "v2_015",
        "category": "corporate",
        "sector": "5G通信设备",
        "key_entities": ["中国联通", "中兴通讯", "联发科技", "FAST"],
        "key_numbers": ["3.5GHz+2.1GHz", "3GPP R16"],
        "expected_direction": "up",
        "subcategory": "商用验证进展",
        "memorization_likelihood": "low",
        "target": "中兴通讯",
        "target_type": "company",
        "proxy_kind": "company",
        "proxy_symbol": "sz000063",
        "same_day": True,
    },
    {
        "candidate_id": "v2_016",
        "category": "industry",
        "sector": "AI业绩预增",
        "key_entities": ["Wind", "A股上市公司", "AI"],
        "key_numbers": ["451家", "156家预喜", "42家同比增幅下限超100%"],
        "expected_direction": "up",
        "subcategory": "业绩预告景气",
        "memorization_likelihood": "medium",
        "target": "AI业绩预增板块",
        "target_type": "sector",
    },
    {
        "candidate_id": "v2_018",
        "category": "macro",
        "sector": "A股宽基",
        "key_entities": ["华西证券", "中证A500指数"],
        "key_numbers": ["中证A500指数下跌0.5%"],
        "expected_direction": "up",
        "subcategory": "宽基看多观点",
        "memorization_likelihood": "medium",
        "target": "中证A500指数",
        "target_type": "index",
    },
    {
        "candidate_id": "v2_019",
        "category": "industry",
        "sector": "光刻胶",
        "key_entities": ["晶瑞电材", "国风新材", "武汉太紫微光电"],
        "key_numbers": ["120nm", "20CM涨停"],
        "expected_direction": "up",
        "subcategory": "国产光刻胶催化",
        "memorization_likelihood": "low",
        "target": "晶瑞电材",
        "target_type": "company",
        "proxy_kind": "company",
        "proxy_symbol": "sz300655",
        "same_day": True,
    },
    {
        "candidate_id": "v2_025",
        "category": "industry",
        "sector": "红利资产",
        "key_entities": ["恒生红利低波ETF易方达", "中证红利指数"],
        "key_numbers": ["80亿元", "约2000万份"],
        "expected_direction": "up",
        "subcategory": "红利资金流入",
        "memorization_likelihood": "medium",
        "target": "红利股板块",
        "target_type": "sector",
    },
    {
        "candidate_id": "v2_026",
        "category": "macro",
        "sector": "成长风格/创业板",
        "key_entities": ["创业板指", "科创50指数", "机器人", "算力"],
        "key_numbers": ["-3.82%", "超4700只个股下跌", "1.87万亿"],
        "expected_direction": "down",
        "subcategory": "指数大跌",
        "memorization_likelihood": "medium",
        "target": "创业板指",
        "target_type": "index",
        "proxy_kind": "index",
        "proxy_symbol": "sz399006",
        "same_day": True,
    },
    {
        "candidate_id": "v2_027",
        "category": "corporate",
        "sector": "医药",
        "key_entities": ["卫信康", "西藏中卫诚康药业", "国家药监局"],
        "key_numbers": ["利多卡因丁卡因乳膏", "临床试验批准通知书"],
        "expected_direction": "up",
        "subcategory": "药物临床获批",
        "memorization_likelihood": "low",
        "target": "卫信康",
        "target_type": "company",
    },
    {
        "candidate_id": "v2_028",
        "category": "policy",
        "sector": "科创板生物医药",
        "key_entities": ["上交所", "科创板八条", "三友医疗", "美迪西"],
        "key_numbers": ["并购重组具体措施"],
        "expected_direction": "up",
        "subcategory": "科创板并购重组政策推进",
        "memorization_likelihood": "medium",
        "target": "科创生物指数",
        "target_type": "index",
        "proxy_kind": "index",
        "proxy_symbol": "sh000683",
    },
    {
        "candidate_id": "v2_029",
        "category": "corporate",
        "sector": "半导体设备",
        "key_entities": ["深科达", "限制性股票激励计划", "激励对象"],
        "key_numbers": ["264.74万股", "105人", "12.50元/股", "3.27%"],
        "expected_direction": "up",
        "subcategory": "股权激励计划",
        "memorization_likelihood": "low",
        "target": "深科达",
        "target_type": "company",
        "proxy_kind": "company",
        "proxy_symbol": "sh688328",
    },
    {
        "candidate_id": "v2_031",
        "category": "industry",
        "sector": "冰雪经济",
        "key_entities": ["冰雪经济", "冰雪假", "滑雪装备"],
        "key_numbers": ["板块最高涨幅近30%", "覆盖全国80%的滑雪场"],
        "expected_direction": "up",
        "subcategory": "季节性景气升温",
        "memorization_likelihood": "medium",
        "target": "冰雪经济板块",
        "target_type": "sector",
    },
    {
        "candidate_id": "v2_032",
        "category": "industry",
        "sector": "AI智能体",
        "key_entities": ["南兴股份", "ChatGPT Agent", "OpenAI"],
        "key_numbers": ["一字涨停"],
        "expected_direction": "up",
        "subcategory": "海外大模型产品催化",
        "memorization_likelihood": "medium",
        "target": "南兴股份",
        "target_type": "company",
        "proxy_kind": "company",
        "proxy_symbol": "sz002757",
        "same_day": True,
    },
    {
        "candidate_id": "v2_033",
        "category": "industry",
        "sector": "科创板",
        "key_entities": ["科创板", "Wind", "人工智能", "生物医药"],
        "key_numbers": ["超260家", "105家报喜", "超50家减亏"],
        "expected_direction": "up",
        "subcategory": "业绩预告密集披露",
        "memorization_likelihood": "medium",
        "target": "科创50指数",
        "target_type": "index",
    },
    {
        "candidate_id": "v2_034",
        "category": "industry",
        "sector": "工程机械",
        "key_entities": ["建设机械", "上海证券", "设备更新政策"],
        "key_numbers": ["涨停"],
        "expected_direction": "up",
        "subcategory": "行业景气修复预期",
        "memorization_likelihood": "low",
        "target": "建设机械",
        "target_type": "company",
        "proxy_kind": "company",
        "proxy_symbol": "sh600984",
        "same_day": True,
    },
    {
        "candidate_id": "v2_036",
        "category": "corporate",
        "sector": "智慧交通",
        "key_entities": ["千方科技", "吴司韵", "孙大勇"],
        "key_numbers": ["第六届董事会"],
        "expected_direction": "neutral",
        "subcategory": "董事变更",
        "memorization_likelihood": "low",
        "target": "千方科技",
        "target_type": "company",
    },
    {
        "candidate_id": "v2_037",
        "category": "corporate",
        "sector": "PCB",
        "key_entities": ["奥士康", "回购股份方案"],
        "key_numbers": ["53.35元/股", "39.40元/股"],
        "expected_direction": "up",
        "subcategory": "回购价格上限上调",
        "memorization_likelihood": "low",
        "target": "奥士康",
        "target_type": "company",
        "proxy_kind": "company",
        "proxy_symbol": "sz002913",
    },
    {
        "candidate_id": "v2_039",
        "category": "corporate",
        "sector": "两轮车",
        "key_entities": ["爱玛科技", "限制性股票激励计划"],
        "key_numbers": ["706万股", "1.75%", "20.23元/股"],
        "expected_direction": "up",
        "subcategory": "股权激励计划",
        "memorization_likelihood": "low",
        "target": "爱玛科技",
        "target_type": "company",
        "proxy_kind": "company",
        "proxy_symbol": "sh603529",
    },
    {
        "candidate_id": "v2_040",
        "category": "corporate",
        "sector": "造纸",
        "key_entities": ["青山纸业", "上交所交易系统", "集中竞价回购"],
        "key_numbers": ["2725万股", "1.1818%", "5413.50万元", "2.04元/股", "1.88元/股"],
        "expected_direction": "up",
        "subcategory": "回购进展",
        "memorization_likelihood": "low",
        "target": "青山纸业",
        "target_type": "company",
        "proxy_kind": "company",
        "proxy_symbol": "sh600103",
    },
    {
        "candidate_id": "v2_042",
        "category": "industry",
        "sector": "红利资产",
        "key_entities": ["恒生红利低波ETF", "中国银河证券", "中证红利指数"],
        "key_numbers": ["7.6亿元", "30亿元"],
        "expected_direction": "up",
        "subcategory": "红利资金净流入",
        "memorization_likelihood": "low",
        "target": "中证红利指数",
        "target_type": "index",
        "proxy_kind": "index",
        "proxy_symbol": "sh000922",
        "same_day": True,
    },
]


SKIPPED = [
    {"id": "v2_002", "reason": "外交会见表述过于宽泛，缺少可明确映射的A股单一目标。"},
    {"id": "v2_003", "reason": "投资日历属于例行事件汇总，不是独立新闻催化。"},
    {"id": "v2_017", "reason": "支付宝搜索人才新闻主要对应未上市主体，对A股缺少直接交易标的。"},
    {"id": "v2_020", "reason": "海外厂商对特斯拉供货与提价传闻，A股映射链条过长且缺少直接目标。"},
    {"id": "v2_021", "reason": "盘后人气股点评覆盖多个容量股和短线题材，不是单一交易事件。"},
    {"id": "v2_022", "reason": "IPO终止数量属于统计汇总，缺少单点催化和明确可交易目标。"},
    {"id": "v2_023", "reason": "午后资金流向与高标情绪混合点评，单一目标不清晰。"},
    {"id": "v2_024", "reason": "券商行业观点属于前瞻性研报表态，缺少单一可验证事件触发点。"},
    {"id": "v2_030", "reason": "海外行业销量预测未指向具体A股公司，交易映射偏弱。"},
    {"id": "v2_035", "reason": "机器人与深海科技两条主线混合点评，不是单一新闻事件。"},
    {"id": "v2_038", "reason": "涨停分析属于盘后结果复盘，缺少原始事件催化。"},
    {"id": "v2_041", "reason": "英伟达海外产品发布对A股仅存在间接映射，缺少直接目标。"},
    {"id": "v2_043", "reason": "美股抵押REITs飙升属于海外市场新闻，对A股没有明确直接目标。"},
]


COMPANY_CACHE: dict[tuple[str, str, str], pd.DataFrame] = {}
INDEX_CACHE: dict[str, pd.DataFrame] = {}


def load_candidates() -> dict[str, dict[str, Any]]:
    payload = json.loads(FULL_PATH.read_text(encoding="utf-8"))
    return {item["candidate_id"]: item for item in payload["candidates"]}


def parse_dt(text: str) -> datetime:
    return datetime.strptime(text, "%Y-%m-%d %H:%M:%S")


def percent(value: float) -> str:
    rounded = round(value, 1)
    return f"{rounded:+.1f}%"


def fetch_company_history(symbol: str, publish_dt: datetime) -> pd.DataFrame:
    start = publish_dt.replace(day=1)
    start_text = (start - pd.Timedelta(days=40)).strftime("%Y%m%d")
    end_text = (publish_dt + pd.Timedelta(days=90)).strftime("%Y%m%d")
    cache_key = (symbol, start_text, end_text)
    if cache_key not in COMPANY_CACHE:
        df = None
        for attempt in range(5):
            try:
                df = ak.stock_zh_a_hist_tx(symbol=symbol, start_date=start_text, end_date=end_text, adjust="qfq")
                break
            except Exception:
                if attempt == 4:
                    raise
                time_module.sleep(2 * (attempt + 1))
        assert df is not None
        df["date"] = pd.to_datetime(df["date"])
        for col in ["open", "close", "high", "low", "amount"]:
            df[col] = pd.to_numeric(df[col])
        COMPANY_CACHE[cache_key] = df
    return COMPANY_CACHE[cache_key]


def fetch_index_history(symbol: str) -> pd.DataFrame:
    if symbol not in INDEX_CACHE:
        df = None
        for attempt in range(5):
            try:
                df = ak.stock_zh_index_daily_tx(symbol=symbol)
                break
            except Exception:
                if attempt == 4:
                    raise
                time_module.sleep(2 * (attempt + 1))
        assert df is not None
        df["date"] = pd.to_datetime(df["date"])
        for col in ["open", "close", "high", "low", "amount"]:
            df[col] = pd.to_numeric(df[col])
        INDEX_CACHE[symbol] = df
    return INDEX_CACHE[symbol]


def first_observable_date(publish_dt: datetime, same_day: bool) -> pd.Timestamp:
    if same_day:
        return pd.Timestamp(publish_dt.date())
    if publish_dt.time() <= time(15, 0):
        return pd.Timestamp(publish_dt.date())
    return pd.Timestamp(publish_dt.date()) + pd.Timedelta(days=1)


def actual_first_row(df: pd.DataFrame, publish_dt: datetime, same_day: bool) -> tuple[pd.Series, str]:
    threshold = first_observable_date(publish_dt, same_day)
    candidate_rows = df[df["date"] >= threshold].copy()
    if candidate_rows.empty:
        raise ValueError(f"No history found after {publish_dt} for threshold {threshold}")
    row = candidate_rows.iloc[0]
    if row["date"].date() == publish_dt.date() and same_day:
        return row, "same_day"
    if row["date"].date() == publish_dt.date():
        return row, "same_day"
    if row["date"].date() > publish_dt.date() + pd.Timedelta(days=7):
        return row, "delayed"
    return row, "next_day"


def calc_outcome(meta: dict[str, Any], publish_time: str) -> tuple[str, str]:
    publish_dt = parse_dt(publish_time)
    same_day = bool(meta.get("same_day"))
    if meta["proxy_kind"] == "company":
        df = fetch_company_history(meta["proxy_symbol"], publish_dt)
    elif meta["proxy_kind"] == "index":
        df = fetch_index_history(meta["proxy_symbol"])
    else:
        raise ValueError(f"Unsupported proxy kind: {meta['proxy_kind']}")

    row, timing = actual_first_row(df, publish_dt, same_day)
    first_idx = df.index[df["date"] == row["date"]][0]
    first_date = row["date"].strftime("%Y-%m-%d")

    if first_idx == 0:
        first_move = (row["close"] / row["open"] - 1) * 100
        base_close = row["open"]
        first_row_without_prev = True
    else:
        prev_close = df.iloc[first_idx - 1]["close"]
        first_move = (row["close"] / prev_close - 1) * 100
        base_close = prev_close
        first_row_without_prev = False

    end_idx = min(first_idx + 4, len(df) - 1)
    final_close = df.iloc[end_idx]["close"]
    cumulative_move = (final_close / base_close - 1) * 100

    if timing == "same_day":
        opening = f"消息发布当日（{first_date}）"
    elif timing == "next_day":
        opening = f"消息后首个交易日（{first_date}）"
    elif first_row_without_prev and meta["target_type"] == "company":
        opening = f"公司直到{first_date}上市后才可交易，上市首日"
    else:
        opening = f"首个可观察交易日为{first_date}，"

    target = meta["target"]
    if meta["expected_direction"] == "up":
        if first_move >= 0 and cumulative_move >= 0:
            tail = "市场按利好交易，正反馈得到延续。"
        elif first_move >= 0 and cumulative_move < 0:
            tail = "市场初始按利好交易，但持续性不足。"
        elif first_move < 0 and cumulative_move >= 0:
            tail = "资金先分歧后修复，利好在随后几个交易日发酵。"
        else:
            tail = "市场未充分认可利好逻辑，股价延续走弱。"
    elif meta["expected_direction"] == "down":
        if first_move <= 0 and cumulative_move <= 0:
            tail = "利空被直接定价，弱势延续。"
        elif first_move <= 0 and cumulative_move > 0:
            tail = "利空冲击较短，随后出现修复。"
        elif first_move > 0 and cumulative_move > 0:
            tail = "市场未按典型利空交易，反而持续走强。"
        else:
            tail = "初始反应偏钝化，但随后仍出现回落。"
    else:
        if abs(first_move) < 1.5 and abs(cumulative_move) < 3:
            tail = "市场整体反应平淡。"
        elif cumulative_move >= 0:
            tail = "事件本身偏中性，但股价仍随资金情绪走强。"
        else:
            tail = "事件本身偏中性，但股价仍随资金情绪走弱。"

    subject = target if meta["target_type"] == "index" else f"{target}收"
    text = (
        f"{opening}{subject}"
        f"{'涨' if first_move >= 0 else '跌'}{abs(round(first_move, 1)):.1f}%，"
        f"随后5个交易日累计{'上涨' if cumulative_move >= 0 else '下跌'}约{abs(round(cumulative_move, 1)):.1f}%，"
        f"{tail}"
    )
    return text, first_date


def build_test_case(seq: int, meta: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    period = source["period"]
    if period == "post_cutoff":
        known_outcome = "unknown_post_cutoff"
        outcome_date = "unknown"
    else:
        known_outcome, outcome_date = calc_outcome(meta, source["publish_time"])

    return {
        "id": f"exp_{seq:03d}",
        "news": {
            "id": str(source["cls_id"]),
            "title": source["title"],
            "content": source["content"],
            "publish_time": source["publish_time"],
            "category": meta["category"],
            "source": "cls_telegraph",
        },
        "known_outcome": known_outcome,
        "outcome_date": outcome_date,
        "sector": meta["sector"],
        "key_entities": meta["key_entities"],
        "key_numbers": meta["key_numbers"],
        "expected_direction": meta["expected_direction"],
        "subcategory": meta["subcategory"],
        "memorization_likelihood": meta["memorization_likelihood"],
        "target": meta["target"],
        "target_type": meta["target_type"],
        "period": period,
        "rarity_estimate": source["rarity_estimate"],
    }


def main() -> None:
    full_map = load_candidates()
    test_cases = []
    for offset, meta in enumerate(KEPT, start=101):
        candidate_id = meta["candidate_id"]
        source = full_map[candidate_id]
        test_cases.append(build_test_case(offset, meta, source))

    output = {"test_cases": test_cases, "skipped": SKIPPED}
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(test_cases)} test cases to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
