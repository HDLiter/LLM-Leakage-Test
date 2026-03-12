"""Masking utilities for leakage mitigation.

Provides rule-based masking (year, entity, numbers, sector) and
LLM-assisted counterfactual generation.
"""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING

from .models import CounterfactualVariant, MaskingConfig, VariantType
from .prompts import counterfactual_generator_prompt, llm_masking_prompt, counterfactual_validation_prompt

if TYPE_CHECKING:
    from .llm_client import LLMClient


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

    # Parse JSON from response
    match = re.search(r'\{[^{}]*"pass"[^{}]*\}', response.raw_response, re.DOTALL)
    if not match:
        return {"pass": False, "reason": "Failed to parse validation response", "scores": {}}
    try:
        result = json.loads(match.group())
        # Normalise the pass field (could be string "true"/"false")
        if isinstance(result.get("pass"), str):
            result["pass"] = result["pass"].lower() == "true"
        return result
    except (json.JSONDecodeError, KeyError):
        return {"pass": False, "reason": "JSON parse error", "scores": {}}


# ── LLM-assisted counterfactual generation ──────────────────────

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
) -> CounterfactualVariant:
    """Generate a counterfactual variant with optional validation + retry.

    When validate=True, uses LLM-as-judge to check quality. If the variant
    fails validation, regenerates (bypass_cache) up to max_retries times.
    """
    vt = variant_type.value if isinstance(variant_type, VariantType) else variant_type

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
) -> list[CounterfactualVariant]:
    """Generate all three types of counterfactual variants."""
    variants = []
    for vt in VariantType:
        cf = generate_counterfactual(client, news_text, case_id, vt, validate=validate)
        variants.append(cf)
    return variants
