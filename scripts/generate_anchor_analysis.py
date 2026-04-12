import json
import re
from collections import Counter, defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = REPO_ROOT / "data/seed/cases_for_anchor_analysis.json"
OUTPUT_PATH = REPO_ROOT / "data/seed/anchor_analysis.json"


LEVELS = {
    "tc_001": 3,
    "tc_002": 3,
    "tc_003": 3,
    "tc_004": 3,
    "tc_005": 3,
    "tc_006": 3,
    "tc_007": 3,
    "tc_008": 3,
    "tc_009": 3,
    "tc_010": 3,
    "tc_011": 3,
    "tc_012": 3,
    "tc_013": 3,
    "tc_014": 3,
    "tc_015": 2,
    "tc_016": 3,
    "tc_017": 3,
    "tc_018": 3,
    "tc_019": 2,
    "tc_020": 2,
    "tc_021": 2,
    "tc_022": 2,
    "tc_023": 3,
    "tc_024": 3,
    "tc_025": 1,
    "tc_026": 3,
    "tc_027": 3,
    "tc_028": 3,
    "tc_029": 3,
    "tc_030": 3,
    "tc_031": 3,
    "tc_032": 3,
    "tc_033": 3,
    "tc_034": 1,
    "tc_035": 1,
    "tc_036": 3,
    "tc_037": 3,
    "tc_038": 1,
    "tc_039": 1,
    "tc_040": 3,
    "tc_041": 3,
    "tc_042": 3,
    "exp_101": 2,
    "exp_102": 2,
    "exp_103": 2,
    "exp_104": 1,
    "exp_105": 2,
    "exp_106": 3,
    "exp_107": 1,
    "exp_108": 2,
    "exp_109": 2,
    "exp_110": 2,
    "exp_111": 1,
    "exp_112": 2,
    "exp_113": 2,
    "exp_114": 1,
    "exp_115": 1,
    "exp_116": 1,
    "exp_117": 1,
    "exp_118": 1,
    "exp_119": 2,
    "exp_120": 2,
    "exp_121": 2,
    "exp_122": 1,
    "exp_123": 2,
    "exp_124": 1,
    "exp_125": 1,
    "exp_126": 2,
    "exp_127": 2,
    "exp_128": 2,
    "exp_129": 2,
    "exp_130": 1,
    "exp_144": 1,
    "exp_145": 1,
    "exp_146": 1,
    "exp_147": 1,
    "exp_148": 2,
    "exp_149": 2,
    "exp_150": 2,
    "exp_151": 1,
    "exp_152": 3,
    "exp_153": 1,
    "exp_154": 1,
    "exp_155": 2,
    "exp_156": 2,
    "exp_157": 2,
    "exp_158": 2,
    "exp_159": 2,
    "exp_160": 1,
    "exp_161": 2,
    "exp_162": 2,
    "exp_163": 2,
    "exp_164": 3,
    "exp_165": 1,
    "exp_166": 2,
    "exp_167": 2,
    "exp_168": 2,
    "exp_169": 1,
    "exp_170": 2,
    "exp_171": 1,
    "exp_172": 1,
    "exp_173": 2,
    "exp_174": 2,
    "exp_175": 2,
    "exp_176": 2,
    "exp_177": 2,
    "exp_178": 2,
    "exp_179": 1,
    "exp_180": 1,
    "exp_181": 3,
    "exp_182": 1,
    "exp_183": 2,
    "exp_184": 2,
    "exp_185": 1,
    "exp_186": 2,
    "exp_187": 2,
    "exp_188": 2,
    "exp_189": 1,
    "exp_190": 0,
    "exp_191": 1,
    "exp_192": 1,
    "exp_193": 1,
    "exp_194": 2,
    "exp_195": 0,
    "exp_196": 2,
    "exp_197": 2,
    "exp_198": 1,
    "exp_199": 2,
    "exp_200": 1,
    "exp_201": 2,
    "exp_202": 2,
    "exp_203": 1,
    "exp_204": 2,
    "exp_205": 1,
    "exp_206": 3,
    "exp_207": 1,
    "exp_208": 3,
    "exp_209": 2,
    "exp_210": 1,
    "exp_211": 2,
    "exp_212": 1,
    "exp_213": 2,
    "exp_214": 2,
    "exp_215": 1,
    "exp_216": 2,
    "exp_217": 2,
    "exp_218": 2,
    "exp_219": 0,
    "exp_220": 0,
    "exp_221": 2,
    "exp_222": 1,
    "exp_223": 2,
    "exp_224": 2,
    "exp_225": 2,
    "exp_226": 1,
    "exp_230": 2,
    "exp_231": 1,
    "exp_232": 1,
    "exp_233": 1,
    "exp_234": 2,
    "exp_235": 1,
    "exp_236": 2,
    "exp_237": 2,
    "exp_238": 1,
    "exp_239": 1,
    "exp_240": 1,
    "exp_241": 3,
    "exp_242": 2,
    "exp_243": 2,
    "exp_244": 2,
    "exp_245": 1,
    "exp_246": 2,
    "exp_247": 2,
    "exp_248": 2,
    "exp_249": 1,
    "exp_250": 1,
    "exp_251": 1,
    "exp_252": 3,
    "exp_253": 2,
    "exp_254": 1,
    "exp_255": 1,
    "exp_256": 2,
    "exp_257": 1,
    "exp_258": 2,
    "exp_259": 2,
    "exp_260": 2,
    "exp_261": 1,
    "exp_262": 1,
    "exp_263": 1,
    "exp_264": 2,
    "exp_265": 1,
    "exp_266": 2,
}


RATIONAL_OVERRIDE = {
    "tc_015": "policy target plus sector narrative narrows the time window, but this remains theme-level rather than one singular event",
    "tc_019": "named company and quarter-specific earnings point to a specific filing, but quarterly loss reports are routine",
    "tc_020": "named company and quarter-specific earnings point to a specific filing, but quarterly results are routine",
    "tc_021": "specific corporate restructuring plan is identifiable, but it is still a routine enterprise announcement type",
    "tc_022": "specific corporate integration step narrows it to one announcement, but brand integration is a routine company event",
    "tc_025": "retrospective commentary references a known merger, but the article itself is a broad look-back rather than one unique event",
    "tc_034": "industry pricing collapse is a broad trend and could describe multiple adjacent weeks or months",
    "tc_035": "sector weakness and inventory commentary are recurring and not tied to one unique headline event",
    "tc_038": "commodity price-threshold commentary is trend-like and can recur across nearby trading sessions",
    "tc_039": "high-dividend bank rotation is a recurring market style rather than one distinct headline event",
    "exp_104": "daily market-theme commentary is recurring and not uniquely tied to one real-world event",
    "exp_107": "intraday sentiment commentary is recurring and only weakly anchored to a specific event",
    "exp_111": "ETF marketing plus broad cycle commentary is generic and could fit many adjacent periods",
    "exp_114": "multi-company earnings roundup points to a reporting season, not one uniquely identifiable event",
    "exp_115": "ETF marketing plus broad market outlook is generic and not tied to one specific event",
    "exp_117": "ETF flow/scale commentary is recurring marketing copy rather than a unique event",
    "exp_118": "daily market close commentary is recurring and not tied to one singular headline event",
    "exp_122": "industry temperature-check coverage is broad trend commentary rather than one specific event",
    "exp_124": "earnings-season roundup narrows the period but not one unique headline event",
    "exp_130": "ETF flow/scale commentary is recurring marketing copy rather than a unique event",
    "exp_144": "daily recap format is recurring; even with examples, it is not anchored to one distinct headline event",
    "exp_146": "earnings-preview roundup narrows the reporting window but not one singular event",
    "exp_147": "industry forecast language is generic and could fit multiple adjacent quarters",
    "exp_151": "recurring pre-open market roundup gives weak day-level cues but not a distinct headline event",
    "exp_153": "broker strategy note is generic and not tied to one unique real-world event",
    "exp_154": "research commentary about AI as a technology wave is broad and recurring",
    "exp_160": "intraday board-strength commentary is recurring and only weakly anchored",
    "exp_165": "industry forecast/report language is generic and not linked to one singular event",
    "exp_169": "daily market-theme commentary is recurring and not uniquely tied to one event",
    "exp_171": "limit-up analysis is a recurring market column rather than one distinct real-world event",
    "exp_172": "broad market-structure commentary is trend-level and not a single unique event",
    "exp_179": "ETF product commentary is recurring and weakly anchored",
    "exp_180": "industry price-trend coverage is broad and could match multiple nearby periods",
    "exp_182": "fund-marketing language around a broad industry theme is generic and not one unique event",
    "exp_185": "ETF marketing plus broad allocation advice is recurring and only weakly anchored",
    "exp_189": "sell-side allocation advice is generic strategy commentary rather than one distinct event",
    "exp_190": "recurring schedule template with multiple calendar items rather than a single real-world event",
    "exp_191": "annual market roundup is period-specific but still a broad summary rather than one singular event",
    "exp_192": "sector-move copy is generic and could fit many trading sessions",
    "exp_193": "daily market-theme commentary is recurring and not uniquely tied to one event",
    "exp_195": "recurring schedule template with multiple calendar items rather than a single real-world event",
    "exp_200": "ETF/sector-move copy is recurring and weakly anchored",
    "exp_203": "limit-up analysis is a recurring market column rather than one distinct real-world event",
    "exp_205": "company strategy comments are broad and could fit many adjacent periods",
    "exp_207": "liquidity outlook for a holiday week is a recurring calendar-style analysis rather than one singular event",
    "exp_210": "broad dividend-trend coverage is a recurring market theme rather than one distinct event",
    "exp_212": "earnings-season roundup narrows the reporting window but not one unique headline event",
    "exp_215": "yearly market statistics and IPO rush commentary summarize a period rather than one event",
    "exp_219": "recurring schedule template with multiple calendar items rather than a single real-world event",
    "exp_220": "recurring schedule template with multiple calendar items rather than a single real-world event",
    "exp_222": "ETF turnover plus broad market rebound language is recurring and weakly anchored",
    "exp_226": "ETF/market-move copy is recurring and not tied to one singular event",
    "exp_231": "recurring pre-open market roundup gives weak day-level cues but not a distinct headline event",
    "exp_232": "ETF product commentary is recurring and weakly anchored",
    "exp_233": "market-theme column is recurring and only weakly tied to a singular real-world event",
    "exp_235": "daily market-theme commentary is recurring and not uniquely tied to one event",
    "exp_238": "editorial-style market commentary is broad and not anchored to one specific event",
    "exp_239": "ETF product commentary is recurring and weakly anchored",
    "exp_240": "daily market close commentary is recurring and not tied to one singular headline event",
    "exp_245": "sector-move copy is generic and could fit many trading sessions",
    "exp_249": "yearly dividend statistic is period-specific but still a broad summary rather than one unique event",
    "exp_250": "ETF flow/sector heat copy is recurring and weakly anchored",
    "exp_251": "sector-move copy is generic and could fit many trading sessions",
    "exp_254": "daily market-theme commentary is recurring and only weakly anchored",
    "exp_255": "commodity price-trend coverage is broad and could match multiple nearby periods",
    "exp_257": "ETF marketing plus broad market outlook is generic and not tied to one specific event",
    "exp_261": "daily market-theme commentary is recurring and not uniquely tied to one event",
    "exp_262": "shipment forecast language is generic and could fit multiple adjacent periods",
    "exp_263": "daily recap format is recurring; even with examples, it is not anchored to one distinct headline event",
    "exp_265": "broker survey roundup summarizes a period rather than one singular event",
}


DATE_RE = re.compile(r"\d{4}年\d{1,2}月\d{1,2}日|\d{4}年\d{1,2}月")
DOC_RE = re.compile(r"《[^》]{2,60}》|“[^”]{2,60}”|\"[^\"]{2,60}\"|'[^']{2,60}'")
NUM_RE = re.compile(
    r"\d[\d\.,]*(?:\s*-\s*\d[\d\.,]*)?\s*"
    r"(?:万亿元|亿元|亿美元|万元|万股|%|个百分点|个基点|只|家|架|吨|GWh|Wh/kg|亿台|万台|台|板)"
)
BAD_DOC_CUES = {"《科创板日报》"}


def dedupe_keep_order(items):
    seen = set()
    result = []
    for item in items:
        value = re.sub(r"\s+", " ", item).strip()
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def short_fragment(text, limit=28):
    text = re.sub(r"\s+", " ", text).strip(" ，。；;:")
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def title_cues(title):
    cues = []
    for sep in ("：", ":"):
        if sep in title:
            left, right = title.split(sep, 1)
            cues.extend([left.strip(), short_fragment(right)])
            return dedupe_keep_order(cues)
    if "，" in title:
        left, right = title.split("，", 1)
        cues.extend([left.strip(), short_fragment(right)])
    else:
        cues.append(short_fragment(title))
    return dedupe_keep_order(cues)


def extract_cues(case):
    title = case["title"]
    preview = case["content_preview"]
    combined = f"{title} {preview}"
    cues = []

    cues.extend(DATE_RE.findall(combined))
    cues.extend(
        match.strip("“”\"'")
        for match in DOC_RE.findall(combined)
        if match.strip("“”\"'") not in BAD_DOC_CUES
    )
    cues.extend(title_cues(title))

    for match in NUM_RE.findall(preview):
        compact = match.replace(" ", "")
        if DATE_RE.fullmatch(compact):
            continue
        cues.append(compact)

    if len(cues) < 2:
        plain_preview = re.sub(r"^【[^】]+】", "", preview).strip()
        for chunk in re.split(r"[。；;]", plain_preview):
            chunk = chunk.strip()
            if len(chunk) >= 8:
                cues.append(short_fragment(chunk))
                break

    return dedupe_keep_order(cues)[:3]


def generic_rationale(case, level):
    title = case["title"]
    preview = case["content_preview"]

    if case["id"] in RATIONAL_OVERRIDE:
        return RATIONAL_OVERRIDE[case["id"]]

    if level == 0:
        return "recurring template or schedule copy rather than a single distinct real-world event"

    if level == 1:
        if any(
            token in title
            for token in (
                "市场主线",
                "收评",
                "快评",
                "行情回顾",
                "涨停分析",
                "竞价看龙头",
                "ETF",
                "板块",
                "概念股",
                "指数",
                "投资机会",
            )
        ):
            return "recurring market or sector commentary; weakly tied to any single real-world event"
        return "industry trend or roundup language is generic and could fit multiple adjacent periods"

    if level == 2:
        if any(
            token in title + preview
            for token in (
                "减持",
                "辞职",
                "回购",
                "激励计划",
                "认购",
                "收购",
                "出售",
                "增资",
                "设立",
                "签订",
                "订单",
                "合同",
                "临床试验",
                "注册证书",
                "拟",
                "公告称",
            )
        ):
            return "named entity plus a concrete announcement narrows this to a specific filing, but the event type is routine"
        return "specific company or institution action narrows it to a period or filing, but lacks a singular headline-level anchor"

    if DATE_RE.search(preview) or DATE_RE.search(title):
        return "exact date plus named entities/details make this a uniquely identifiable event"
    return "distinctive named event or milestone is specific enough to identify a single real-world occurrence"


def main():
    cases = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    if len(cases) != 192:
        raise ValueError(f"Expected 192 cases, found {len(cases)}")

    case_ids = [case["id"] for case in cases]
    missing = [case_id for case_id in case_ids if case_id not in LEVELS]
    extra = sorted(set(LEVELS) - set(case_ids))
    if missing or extra:
        raise ValueError(f"Coverage mismatch. Missing={missing} Extra={extra}")

    analyses = []
    level_counter = Counter()
    period_counter = defaultdict(Counter)

    for case in cases:
        level = LEVELS[case["id"]]
        analyses.append(
            {
                "id": case["id"],
                "anchor_level": level,
                "anchor_cues": extract_cues(case),
                "rationale": generic_rationale(case, level),
            }
        )
        level_counter[level] += 1
        period_counter[case["period"]][level] += 1

    output = {
        "analysis": analyses,
        "summary": {
            "level_3": level_counter[3],
            "level_2": level_counter[2],
            "level_1": level_counter[1],
            "level_0": level_counter[0],
            "by_period": {
                "pre_cutoff": {str(level): period_counter["pre_cutoff"][level] for level in (3, 2, 1, 0)},
                "post_cutoff": {str(level): period_counter["post_cutoff"][level] for level in (3, 2, 1, 0)},
            },
        },
    }

    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {len(analyses)} analyses to {OUTPUT_PATH}")
    print(json.dumps(output["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
