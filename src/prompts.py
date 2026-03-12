"""Prompt templates for leakage detection experiments."""

from __future__ import annotations

from .models import MaskingConfig, OutputFormat


# ── System prompts ──────────────────────────────────────────────

ROLE_PLAY_SYSTEM = (
    "你是一位专业的金融分析师，仅根据提供的新闻文本进行分析。"
    "你不具备任何关于新闻发布后市场走势的知识。"
    "你的分析必须完全基于新闻文本中明确提到的信息。"
    "禁止引用任何新闻文本中未出现的事实、数据或事件。"
)

COT_FORCED_INSTRUCTION = (
    "\n\n【归因要求】你的推理过程中，每一个论点都必须引用新闻原文中的具体语句作为依据。"
    "格式：[依据: \"原文引用\"] → 推断。"
    "如果某个论点无法在原文中找到依据，必须标注 [无依据] 并降低该论点的权重。"
)

EXTRACTION_CONSTRAINT = (
    "\n\n【维度约束】请仅从以下维度评估新闻影响，不要引入其他维度：\n"
    "1. 政策方向性（利好/利空/中性）\n"
    "2. 影响范围（个股/板块/大盘）\n"
    "3. 时效性（短期/中期/长期）\n"
    "4. 确定性（已落地/预期中/不确定）"
)


# ── Output format instructions ──────────────────────────────────

OUTPUT_INSTRUCTIONS: dict[str, str] = {
    "binary": (
        "\n\n请仅输出 JSON：{\"direction\": \"up\" 或 \"down\", \"reasoning\": \"...\"}"
    ),
    "scalar": (
        "\n\n请输出 JSON：{\"score\": <-1.0到1.0的浮点数，负=利空，正=利好>, \"reasoning\": \"...\"}"
    ),
    "5-bin": (
        "\n\n请输出 JSON，给出五档概率分布（整数，求和=100）：\n"
        "{\"strong_bear\": <0-100>, \"weak_bear\": <0-100>, \"neutral\": <0-100>, "
        "\"weak_bull\": <0-100>, \"strong_bull\": <0-100>, \"reasoning\": \"...\"}"
    ),
    "free-text": (
        "\n\n请用中文自由文本分析该新闻对市场的影响，包括方向判断和理由。"
    ),
}


# ── Scoring prompt builder ──────────────────────────────────────

def scoring_prompt(
    news_text: str,
    config: MaskingConfig,
    output_format: OutputFormat | str = OutputFormat.FIVE_BIN,
) -> tuple[str, str]:
    """Build (system_prompt, user_prompt) for news scoring.

    Returns:
        (system_message, user_message)
    """
    fmt = output_format.value if isinstance(output_format, OutputFormat) else output_format

    # System
    system = ROLE_PLAY_SYSTEM if config.role_play else "你是一位金融分析师。"
    if config.cot_forced:
        system += COT_FORCED_INSTRUCTION
    if config.extraction_constraint:
        system += EXTRACTION_CONSTRAINT

    # User
    user = f"请分析以下新闻对A股市场的影响：\n\n{news_text}"
    user += OUTPUT_INSTRUCTIONS.get(fmt, OUTPUT_INSTRUCTIONS["5-bin"])

    return system, user


# ── Counterfactual generator prompt ─────────────────────────────

def counterfactual_generator_prompt(news_text: str, variant_type: str) -> tuple[str, str]:
    """Prompt DeepSeek to generate a counterfactual variant."""
    system = "你是一个金融新闻改写专家。请严格按照要求修改新闻，保持语言风格一致。仅输出修改后的新闻文本，不要添加任何解释。"

    instructions = {
        "reverse_outcome": (
            "请将以下新闻中的核心结论/影响方向反转。"
            "例如：利好→利空，上涨→下跌，扩张→收缩，放松→收紧。"
            "保持其他细节（日期、实体、数字）不变。"
        ),
        "swap_entity": (
            "请对以下新闻进行全面的实体替换，使其无法被识别为特定真实事件：\n"
            "1. 将所有机构名、人名、公司名替换为虚构但合理的名称\n"
            '2. 将专有政策名称替换为虚构的政策名称（如"双减政策"→"优学计划"，"活跃资本市场"→"振兴产业基金"）\n'
            "3. 将行业特征词和专有术语替换为同类但不同的表述\n"
            "4. 确保替换后的新闻读起来像一篇全新的、无法与任何真实事件对应的新闻\n"
            "保持新闻的逻辑结构和论述方向不变。"
        ),
        "alter_numbers": (
            "请修改以下新闻中的数量信息，使其与原文有明显差异：\n"
            "1. 如果新闻包含具体数字（百分比、金额等），将其替换为合理但不同的数字（变化幅度30%-100%），年份除外\n"
            '2. 如果新闻缺少可改数字，则修改程度词和幅度词（如"大幅"→"小幅"，"严禁"→"限制"，"全面"→"部分"，"显著"→"略微"）\n'
            '3. 调整频率词（如"持续"→"偶尔"，"多次"→"首次"）\n'
            "确保修改后的新闻在数量感知上与原文有明显区别。保持新闻结构不变。"
        ),
    }

    user = f"{instructions.get(variant_type, instructions['reverse_outcome'])}\n\n原文：\n{news_text}"
    return system, user


# ── Memorization probe prompt ───────────────────────────────────

def memorization_probe_prompt(question: str) -> tuple[str, str]:
    """Direct factual question to test memorization."""
    system = "请根据你的知识回答以下关于A股市场的问题。如果不确定，请说明。请用JSON格式回答：{\"answer\": \"...\", \"confidence\": <0-100>}"
    return system, question


# ── Timeliness judge prompt ─────────────────────────────────────

def timeliness_judge_prompt(news_date: str, response_text: str) -> tuple[str, str]:
    """Judge whether a response contains future information."""
    system = (
        "你是一个时间线审查员。你的任务是检查一段分析文本中是否包含了"
        "新闻发布日期之后才可能知道的信息（即未来信息泄露）。"
    )
    user = (
        f"新闻发布日期：{news_date}\n\n"
        f"以下是对该新闻的分析文本：\n{response_text}\n\n"
        "请检查分析中是否引用了发布日期之后的事件、数据或结果。\n"
        "输出 JSON：{\"has_future_info\": true/false, \"evidence\": [\"...\"], \"severity\": \"none\"/\"minor\"/\"major\"}"
    )
    return system, user


# ── LLM-based masking prompt ──────────────────────────────────

def llm_masking_prompt(text: str, dimensions: list[str]) -> tuple[str, str]:
    """Build prompt for LLM-based natural masking.

    Instead of mechanical [ENTITY] placeholders, the LLM rewrites the text
    so that masked dimensions are naturally anonymised while preserving
    readability and analytical value.
    """
    system = (
        "你是一个金融文本匿名化专家。你的任务是改写新闻文本，使指定维度的信息被自然地模糊化，"
        "但保持文本的可读性和分析价值。改写后的文本应该读起来像一篇正常的新闻，而不是充满占位符。"
        "仅输出改写后的文本，不要添加任何解释。"
    )

    dim_instructions = {
        "year": '将具体年份替换为模糊时间表述（如"近期"、"此前"、"某年"），不要保留可推断具体年份的上下文线索。',
        "entity": '将机构名、人名、公司名替换为同类泛称（如"某大型银行"、"一位高层官员"），同时模糊化与该实体强关联的专有政策名称或项目名称。',
        "numbers": '将具体数字替换为模糊程度词（如"大幅"、"数百亿"、"约X%"），保持量级感但去除精确值。',
        "sector": '将具体行业/板块名称替换为泛化描述（如"某周期性行业"、"一个新兴领域"）。',
    }

    active = [dim_instructions[d] for d in dimensions if d in dim_instructions]
    if not active:
        return system, text

    user = "请按以下要求改写新闻文本：\n\n"
    for i, inst in enumerate(active, 1):
        user += f"{i}. {inst}\n"
    user += f"\n原文：\n{text}"

    return system, user


# ── Counterfactual validation prompt ──────────────────────────

def counterfactual_validation_prompt(
    original: str, variant: str, variant_type: str,
) -> tuple[str, str]:
    """LLM-as-judge prompt to validate counterfactual variant quality."""
    system = (
        "你是一个反事实文本质量评估专家。请评估变体文本相对于原文的修改质量。"
        "输出 JSON：{\"pass\": true/false, \"reason\": \"...\", \"scores\": "
        "{\"entity_anonymity\": <0-10>, \"numeric_change\": <0-10>, \"semantic_shift\": <0-10>}}"
    )

    type_criteria = {
        "reverse_outcome": (
            "评估标准：核心结论方向是否被有效反转？"
            "语义方向应与原文相反（利好↔利空）。semantic_shift >= 7 为合格。"
        ),
        "swap_entity": (
            "评估标准：\n"
            "1. 实体可识别性：替换后能否通过机构名、政策名、行业特征词识别出原始事件？entity_anonymity >= 7 为合格。\n"
            "2. 不仅要替换机构名，还要替换专有政策名称和行业特征词。"
        ),
        "alter_numbers": (
            "评估标准：\n"
            "1. 数字/程度词是否有明显变化？numeric_change >= 6 为合格。\n"
            "2. 如果原文无具体数字，程度词和幅度词是否被有效调整？\n"
            "3. 变体不应与原文几乎相同。"
        ),
    }

    user = (
        f"变体类型：{variant_type}\n"
        f"{type_criteria.get(variant_type, '')}\n\n"
        f"原文：\n{original}\n\n"
        f"变体：\n{variant}"
    )
    return system, user
