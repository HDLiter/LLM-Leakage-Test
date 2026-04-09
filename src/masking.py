"""Masking utilities for leakage mitigation.

Provides rule-based masking (year, entity, numbers, sector) and
LLM-assisted counterfactual generation.
"""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, Any

from .models import CounterfactualVariant, MaskingConfig, VariantType
from .prompts import counterfactual_generator_prompt, llm_masking_prompt, counterfactual_validation_prompt

if TYPE_CHECKING:
    from .llm_client import LLMClient


COUNTERFACTUAL_TEMPLATE_ID_BY_VARIANT: dict[VariantType, str] = {
    VariantType.SEMANTIC_REVERSAL: "semantic_reversal",
    VariantType.PROVENANCE_SWAP: "provenance_swap",
    VariantType.NOVELTY_TOGGLE: "novelty_toggle",
    VariantType.NEUTRAL_PARAPHRASE: "neutral_paraphrase",
    VariantType.SHAM_EDITS: "sham_edits",
}


def _coerce_variant_type(variant_type: VariantType | str) -> VariantType | None:
    """Normalise a variant type to the enum when possible."""
    if isinstance(variant_type, VariantType):
        return variant_type
    try:
        return VariantType(variant_type)
    except ValueError:
        return None


def resolve_counterfactual_template_id(
    variant_type: VariantType | str,
) -> str | None:
    """Return the YAML template id for a template-backed variant type."""
    variant = _coerce_variant_type(variant_type)
    if variant is None:
        return None
    return COUNTERFACTUAL_TEMPLATE_ID_BY_VARIANT.get(variant)


# ── Rule-based masking ──────────────────────────────────────────

def mask_year(text: str) -> str:
    """Replace 4-digit years (2000-2029) with [YEAR].

    Ported from Thales contracts/common.py:554-619 logic.
    """
    return re.sub(r"(20[0-2]\d)年", "[YEAR]年", text)


def mask_entity(text: str, entities: list[str] | None = None) -> str:
    """Replace known entities with [ENTITY_N] placeholders.

    If entities list is provided, replace those specifically.
    Otherwise apply heuristic patterns for Chinese financial entities.
    """
    if entities:
        for i, ent in enumerate(entities, 1):
            text = text.replace(ent, f"[实体{i}]")
        return text

    # Heuristic: common suffixes for Chinese orgs/companies
    patterns = [
        r"[\u4e00-\u9fff]{2,10}(?:银行|证券|基金|保险|集团|公司|委员会|研究院|交易所)",
        r"[\u4e00-\u9fff]{2,6}(?:部|局|办|院|会)",
    ]
    counter = 0
    for pat in patterns:
        def _replace(m: re.Match) -> str:
            nonlocal counter
            counter += 1
            return f"[实体{counter}]"
        text = re.sub(pat, _replace, text)
    return text


def mask_numbers(text: str) -> str:
    """Replace numeric values with [NUM], preserving year references."""
    # First protect years
    protected = re.sub(r"(20[0-2]\d)年", r"__YEAR_\1__", text)
    # Replace percentages
    protected = re.sub(r"\d+\.?\d*%", "[NUM]%", protected)
    # Replace currency amounts
    protected = re.sub(r"\d+\.?\d*(?:万亿|亿|万|元|美元|港元)", "[NUM]", protected)
    # Replace standalone numbers (3+ digits to avoid replacing single-digit ordinals)
    protected = re.sub(r"\b\d{3,}\b", "[NUM]", protected)
    # Restore years
    protected = re.sub(r"__YEAR_(\d{4})__", r"\1年", protected)
    return protected


def mask_sector(text: str, sector: str | None = None) -> str:
    """Replace sector/industry references with [SECTOR]."""
    sectors = [
        "银行", "保险", "证券", "房地产", "科技", "医药", "新能源",
        "消费", "教育", "互联网", "半导体", "汽车", "钢铁", "煤炭",
        "有色金属", "农业", "军工", "传媒", "电力", "化工",
        "AI", "白酒", "光伏", "锂电", "CXO", "制造",
    ]
    if sector:
        text = text.replace(sector, "[板块]")
    for s in sectors:
        text = text.replace(s, "[板块]")
    return text


def apply_masking(text: str, config: MaskingConfig, entities: list[str] | None = None, client: "LLMClient | None" = None) -> str:
    """Apply all configured masks to text.

    When mask_mode='llm' and a client is provided, uses LLM-based natural
    masking. Otherwise falls back to rule-based masking.
    """
    if config.mask_mode == "llm" and client is not None:
        return llm_mask(client, text, config)

    result = text
    if config.mask_year:
        result = mask_year(result)
    if config.mask_entity:
        result = mask_entity(result, entities)
    if config.mask_numbers:
        result = mask_numbers(result)
    if config.mask_sector:
        result = mask_sector(result)
    return result


# ── LLM-based masking ─────────────────────────────────────────

def llm_mask(client: "LLMClient", text: str, config: MaskingConfig) -> str:
    """Use LLM to naturally anonymise text along configured dimensions."""
    dimensions = []
    if config.mask_year:
        dimensions.append("year")
    if config.mask_entity:
        dimensions.append("entity")
    if config.mask_numbers:
        dimensions.append("numbers")
    if config.mask_sector:
        dimensions.append("sector")

    if not dimensions:
        return text

    system, user = llm_masking_prompt(text, dimensions)
    response = client.chat(system, user)
    return response.raw_response.strip()


# ── Counterfactual validation ─────────────────────────────────

def extract_json_robust(text: str) -> dict | None:
    """Extract the first top-level JSON object from text, handling nested braces."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_string = False
    i = start
    while i < len(text):
        ch = text[i]
        if in_string:
            if ch == "\\" :
                i += 2  # skip escaped char entirely
                continue
            if ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        return None
        i += 1
    return None


def validate_counterfactual(
    client: "LLMClient",
    original: str,
    variant: str,
    variant_type: str,
) -> dict:
    """Use LLM-as-judge to check counterfactual variant quality.

    Returns dict with keys: pass (bool), reason (str), scores (dict).
    """
    system, user = counterfactual_validation_prompt(original, variant, variant_type)
    response = client.chat(system, user)

    result = extract_json_robust(response.raw_response)
    if not result or "pass" not in result:
        return {"pass": False, "reason": "Failed to parse validation response", "scores": {}}
    # Normalise the pass field (could be string "true"/"false")
    if isinstance(result.get("pass"), str):
        result["pass"] = result["pass"].lower() == "true"
    return result


# ── LLM-assisted counterfactual generation ──────────────────────

def _parse_json_object(text: str, context: str) -> dict[str, Any]:
    """Parse a JSON object, tolerating wrapped prose around the JSON."""
    raw = text.strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = extract_json_robust(raw)

    if parsed is None:
        snippet = raw[:200].replace("\n", " ")
        raise ValueError(f"Could not parse JSON object from {context}: {snippet!r}")
    if not isinstance(parsed, dict):
        raise ValueError(
            f"Expected {context} to return a JSON object, got {type(parsed).__name__}"
        )
    return parsed


def _counterfactual_variant_from_template_result(
    original_case_id: str,
    variant_type: VariantType,
    parsed: dict[str, Any],
    modification_description: str = "",
) -> CounterfactualVariant:
    """Convert structured template output into the legacy variant model."""
    rewritten = str(parsed["rewritten_article"]).strip()
    lines = rewritten.split("\n", 1)

    return CounterfactualVariant(
        original_case_id=original_case_id,
        variant_type=variant_type,
        modified_title=lines[0].strip(),
        modified_content=lines[1].strip() if len(lines) > 1 else lines[0].strip(),
        modification_description=modification_description or f"template {variant_type.value}",
    )


def generate_counterfactual_from_template(
    article: str,
    template_id: str,
    client: "LLMClient",
    prompts_dir: str = "config/prompts",
    **kwargs,
) -> dict[str, Any]:
    """Generate a structured counterfactual rewrite from a frozen YAML template."""
    from .prompt_loader import PromptLoader

    bypass_cache = bool(kwargs.pop("bypass_cache", False))

    loader = PromptLoader(prompts_dir=prompts_dir)
    template = loader.get_counterfactual_template(template_id)
    user_prompt = loader.render_cf_prompt(template_id, article, **kwargs)

    response = client.chat(
        template.system_prompt,
        user_prompt,
        bypass_cache=bypass_cache,
    )
    parsed = _parse_json_object(
        response.raw_response,
        context=f"counterfactual template {template_id!r}",
    )

    errors = list(loader._validator.validate_schema(template.output_schema, parsed))
    if errors:
        raise ValueError(
            f"LLM output failed validation for counterfactual template {template_id!r}: "
            + "; ".join(errors)
        )
    return parsed


def _generate_single(
    client: "LLMClient",
    news_text: str,
    original_case_id: str,
    vt: str,
) -> CounterfactualVariant:
    """Generate one counterfactual variant (no validation)."""
    system, user = counterfactual_generator_prompt(news_text, vt)
    response = client.chat(system, user, bypass_cache=False)
    modified = response.raw_response.strip()

    lines = modified.split("\n", 1)
    title = lines[0].strip()
    content = lines[1].strip() if len(lines) > 1 else title

    return CounterfactualVariant(
        original_case_id=original_case_id,
        variant_type=vt,
        modified_title=title,
        modified_content=content,
    )


def generate_counterfactual(
    client: "LLMClient",
    news_text: str,
    original_case_id: str,
    variant_type: VariantType | str,
    validate: bool = True,
    max_retries: int = 2,
    prompts_dir: str = "config/prompts",
    **template_kwargs: Any,
) -> CounterfactualVariant:
    """Generate a counterfactual variant with optional validation + retry.

    Legacy variants use LLM-as-judge validation. Template-backed variants use
    the frozen YAML prompt plus schema validation, retrying on parse/schema
    failures up to max_retries times.
    """
    variant_enum = _coerce_variant_type(variant_type)
    vt = variant_enum.value if variant_enum is not None else variant_type
    template_id = resolve_counterfactual_template_id(variant_type)

    if template_id is not None:
        if variant_enum is None:
            raise ValueError(f"Unknown template-backed variant type: {variant_type!r}")

        last_error: ValueError | None = None
        for attempt in range(max_retries + 1):
            try:
                parsed = generate_counterfactual_from_template(
                    article=news_text,
                    template_id=template_id,
                    client=client,
                    prompts_dir=prompts_dir,
                    bypass_cache=attempt > 0,
                    **template_kwargs,
                )
                return _counterfactual_variant_from_template_result(
                    original_case_id=original_case_id,
                    variant_type=variant_enum,
                    parsed=parsed,
                    modification_description=f"template {template_id} (attempt {attempt + 1})",
                )
            except ValueError as exc:
                last_error = exc

        if last_error is not None:
            raise last_error

    cf = _generate_single(client, news_text, original_case_id, vt)

    if not validate:
        return cf

    for attempt in range(max_retries):
        result = validate_counterfactual(client, news_text, cf.modified_content, vt)
        if result.get("pass", False):
            cf.modification_description = f"validated (attempt {attempt + 1})"
            return cf

        # Regenerate with cache bypass
        system, user = counterfactual_generator_prompt(news_text, vt)
        response = client.chat(system, user, bypass_cache=True)
        modified = response.raw_response.strip()
        lines = modified.split("\n", 1)
        cf = CounterfactualVariant(
            original_case_id=original_case_id,
            variant_type=vt,
            modified_title=lines[0].strip(),
            modified_content=lines[1].strip() if len(lines) > 1 else lines[0].strip(),
            modification_description=f"retry {attempt + 1}: {result.get('reason', '')}",
        )

    # Return last attempt even if not validated
    cf.modification_description = f"max retries reached ({max_retries})"
    return cf


def generate_all_counterfactuals(
    client: "LLMClient",
    news_text: str,
    case_id: str,
    validate: bool = True,
    variant_types: list[VariantType | str] | None = None,
    prompts_dir: str = "config/prompts",
    template_kwargs_by_variant: dict[VariantType | str, dict[str, Any]] | None = None,
) -> list[CounterfactualVariant]:
    """Generate configured counterfactual variants.

    Defaults to the legacy pair for backward compatibility. Template-backed
    variants can be supplied via variant_types plus template_kwargs_by_variant.
    """
    def _kwargs_for_variant(vt: VariantType | str) -> dict[str, Any]:
        if not template_kwargs_by_variant:
            return {}

        candidates: list[VariantType | str] = [vt]
        enum_value = _coerce_variant_type(vt)
        if enum_value is not None:
            candidates.extend([enum_value, enum_value.value])

        for key in candidates:
            if key in template_kwargs_by_variant:
                return dict(template_kwargs_by_variant[key])
        return {}

    if variant_types is None:
        active_variants = list(VariantType.deprecated_counterfactuals())
    else:
        active_variants = list(variant_types)
    variants = []
    for vt in active_variants:
        cf = generate_counterfactual(
            client,
            news_text,
            case_id,
            vt,
            validate=validate,
            prompts_dir=prompts_dir,
            **_kwargs_for_variant(vt),
        )
        variants.append(cf)
    return variants


def generate_counterfactuals_batch(
    client: "LLMClient",
    test_cases: list,
    validate: bool = True,
    max_workers: int | None = None,
    variant_types: list[VariantType | str] | None = None,
    prompts_dir: str = "config/prompts",
    template_kwargs_by_case: dict[str, dict[VariantType | str, dict[str, Any]]] | None = None,
) -> list[CounterfactualVariant]:
    """Generate counterfactual variants for multiple test cases concurrently.

    Each (test_case, variant_type) pair runs in a separate thread.
    The generate→validate→retry chain within each pair stays serial.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from . import DEFAULT_CONCURRENCY

    if max_workers is None:
        max_workers = DEFAULT_CONCURRENCY

    if variant_types is None:
        active_variants = list(VariantType.deprecated_counterfactuals())
    else:
        active_variants = list(variant_types)

    def _kwargs_for_case(case_id: str, vt: VariantType | str) -> dict[str, Any]:
        if not template_kwargs_by_case:
            return {}

        per_case = template_kwargs_by_case.get(case_id)
        if not per_case:
            return {}

        candidates: list[VariantType | str] = [vt]
        enum_value = _coerce_variant_type(vt)
        if enum_value is not None:
            candidates.extend([enum_value, enum_value.value])

        for key in candidates:
            if key in per_case:
                return dict(per_case[key])
        return {}

    tasks = [
        (tc, vt, _kwargs_for_case(tc.id, vt))
        for tc in test_cases
        for vt in active_variants
    ]

    results: list[tuple[int, CounterfactualVariant]] = []

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(
                generate_counterfactual,
                client,
                tc.news.content,
                tc.id,
                vt,
                validate=validate,
                prompts_dir=prompts_dir,
                **template_kwargs,
            ): idx
            for idx, (tc, vt, template_kwargs) in enumerate(tasks)
        }
        for future in as_completed(futures):
            idx = futures[future]
            results.append((idx, future.result()))

    results.sort(key=lambda x: x[0])
    return [cf for _, cf in results]


# ── False-outcome CPT ─────────────────────────────────────────────

_FALSE_OUTCOME_PHRASES_NEGATIVE = [
    "后续{target}表现低迷，市场反应冷淡",
    "此后{target}持续走弱，投资者信心不足",
    "随后{target}出现明显回调，未能延续涨势",
    "{target}后续承压下行，相关板块全面走弱",
    "市场对{target}反应偏负面，短期内持续承压",
]

_FALSE_OUTCOME_PHRASES_POSITIVE = [
    "后续{target}表现强劲，市场热情高涨",
    "此后{target}持续走强，投资者积极加仓",
    "随后{target}企稳回升，超出市场预期",
    "{target}后续获得资金追捧，涨势显著",
    "市场对{target}反应积极，短期内持续上行",
]


def _negate_outcome(known_outcome: str, target: str) -> str:
    """Produce a plausible false version of a known outcome.

    Flips directional words while keeping the structure recognisable.
    """
    import re

    text = known_outcome
    # Flip directional words
    _swaps = [
        ("大幅上涨", "大幅下跌"), ("大幅下跌", "大幅上涨"),
        ("上涨", "下跌"), ("下跌", "上涨"),
        ("涨幅", "跌幅"), ("跌幅", "涨幅"),
        ("走强", "走弱"), ("走弱", "走强"),
        ("反弹", "回调"), ("回调", "反弹"),
        ("暴涨", "暴跌"), ("暴跌", "暴涨"),
        ("利好", "利空"), ("利空", "利好"),
        ("积极", "消极"), ("消极", "积极"),
        ("乐观", "悲观"), ("悲观", "乐观"),
        ("回升", "下滑"), ("下滑", "回升"),
        ("企稳", "失守"), ("失守", "企稳"),
        ("高涨", "低迷"), ("低迷", "高涨"),
        ("加仓", "减仓"), ("减仓", "加仓"),
        ("涨停", "跌停"), ("跌停", "涨停"),
    ]
    for pos, neg in _swaps:
        text = text.replace(pos, f"__{neg}__")
    # Remove placeholder markers
    text = re.sub(r"__(.+?)__", r"\1", text)
    return text


def generate_false_outcome_cpt(
    article: str,
    known_outcome: str,
    expected_direction: str,
    target: str,
) -> tuple[str, str]:
    """Inject a plausible false-outcome hint into the article.

    Two modes:
    - **outcome-specific** (when *known_outcome* is a real description):
      negates the known outcome to create a case-specific false hint.
    - **generic** (when *known_outcome* is empty / ``unknown_post_cutoff``):
      falls back to directional templates.

    Returns ``(modified_article, cpt_mode)`` where *cpt_mode* is
    ``"outcome_specific"`` or ``"generic"``.
    """
    import random as _random

    _known = (known_outcome or "").strip()
    is_generic = not _known or _known == "unknown_post_cutoff"

    if is_generic:
        # Fallback: direction-based generic template (original behaviour)
        direction = expected_direction.strip().lower()
        if direction in ("up", "positive", "strong_positive"):
            phrases = _FALSE_OUTCOME_PHRASES_NEGATIVE
        elif direction in ("down", "negative", "strong_negative"):
            phrases = _FALSE_OUTCOME_PHRASES_POSITIVE
        else:
            phrases = _FALSE_OUTCOME_PHRASES_NEGATIVE
        phrase = _random.choice(phrases).format(target=target)
        hint = f"（注：据了解，{phrase}。）"
        return f"{article}\n{hint}", "generic"

    # Outcome-specific: negate the real known_outcome
    false_outcome = _negate_outcome(_known, target)
    hint = f"（注：据了解，{false_outcome}。）"
    return f"{article}\n{hint}", "outcome_specific"
