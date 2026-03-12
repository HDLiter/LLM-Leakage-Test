"""High-level experiment runners with concurrent API calls."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import DEFAULT_CONCURRENCY
from .masking import apply_masking
from .models import MaskingConfig, TestCase, CounterfactualVariant, LLMResponse
from .prompts import scoring_prompt, llm_masking_prompt

if TYPE_CHECKING:
    from .llm_client import LLMClient


def _mask_texts_concurrent(
    client: "LLMClient",
    config: MaskingConfig,
    test_cases: list[TestCase],
    variant_map: dict[str, dict],
    max_concurrency: int = DEFAULT_CONCURRENCY,
) -> tuple[dict[int, str], dict[tuple[int, str], str]]:
    """Apply masking to all texts, using concurrent LLM calls when mask_mode='llm'.

    Returns:
        (masked_orig, masked_cf) where:
            masked_orig: {tc_index: masked_text}
            masked_cf:   {(tc_index, variant_type): masked_text}
    """
    masked_orig: dict[int, str] = {}
    masked_cf: dict[tuple[int, str], str] = {}

    if config.mask_mode == "llm":
        texts_to_mask = []
        text_indices: list[tuple[str, int, str | None]] = []
        for i, tc in enumerate(test_cases):
            texts_to_mask.append(tc.news.content)
            text_indices.append(("orig", i, None))
            for vt_name, variant in variant_map.get(tc.id, {}).items():
                texts_to_mask.append(variant.modified_content)
                text_indices.append(("cf", i, vt_name))

        dimensions = []
        if config.mask_year: dimensions.append("year")
        if config.mask_entity: dimensions.append("entity")
        if config.mask_numbers: dimensions.append("numbers")
        if config.mask_sector: dimensions.append("sector")

        if dimensions:
            mask_prompts = [llm_masking_prompt(t, dimensions) for t in texts_to_mask]
            mask_responses = client.batch_chat_concurrent(mask_prompts, max_concurrency=max_concurrency)
            for (typ, tc_idx, vt_name), resp in zip(text_indices, mask_responses):
                if typ == "orig":
                    masked_orig[tc_idx] = resp.raw_response.strip()
                else:
                    masked_cf[(tc_idx, vt_name)] = resp.raw_response.strip()
        else:
            for i, tc in enumerate(test_cases):
                masked_orig[i] = tc.news.content
                for vt_name in variant_map.get(tc.id, {}):
                    masked_cf[(i, vt_name)] = variant_map[tc.id][vt_name].modified_content
    else:
        for i, tc in enumerate(test_cases):
            masked_orig[i] = apply_masking(tc.news.content, config, tc.key_entities)
            for vt_name, variant in variant_map.get(tc.id, {}).items():
                masked_cf[(i, vt_name)] = apply_masking(variant.modified_content, config, tc.key_entities)

    return masked_orig, masked_cf


def run_counterfactual_attack(
    client: "LLMClient",
    config: MaskingConfig,
    test_cases: list[TestCase],
    variant_map: dict[str, dict],
    output_format: str = "5-bin",
    max_concurrency: int = DEFAULT_CONCURRENCY,
) -> tuple[list[LLMResponse], list[LLMResponse], list[tuple]]:
    """Run counterfactual attack for one strategy config.

    Returns:
        (orig_responses, cf_responses, task_meta) where task_meta is a list of
        (TestCase, variant_type_name) tuples aligned with the responses.
    """
    masked_orig, masked_cf = _mask_texts_concurrent(
        client, config, test_cases, variant_map, max_concurrency
    )

    tasks: list[tuple[TestCase, str, str, str, str, str]] = []
    for i, tc in enumerate(test_cases):
        sys_orig, usr_orig = scoring_prompt(masked_orig[i], config, output_format)
        for vt_name in variant_map.get(tc.id, {}):
            sys_cf, usr_cf = scoring_prompt(masked_cf[(i, vt_name)], config, output_format)
            tasks.append((tc, vt_name, sys_orig, usr_orig, sys_cf, usr_cf))

    orig_prompts = [(t[2], t[3]) for t in tasks]
    cf_prompts = [(t[4], t[5]) for t in tasks]
    all_prompts = orig_prompts + cf_prompts

    all_responses = client.batch_chat_concurrent(all_prompts, max_concurrency=max_concurrency)
    orig_responses = all_responses[:len(tasks)]
    cf_responses = all_responses[len(tasks):]
    task_meta = [(t[0], t[1]) for t in tasks]

    return orig_responses, cf_responses, task_meta


def run_scoring_batch(
    client: "LLMClient",
    config: MaskingConfig,
    texts: list[str],
    output_format: str = "5-bin",
    max_concurrency: int = DEFAULT_CONCURRENCY,
) -> list[LLMResponse]:
    """Score a list of texts with the given config, concurrently.

    Useful for placebo tests, single-pass scoring, etc.
    """
    prompts = [scoring_prompt(t, config, output_format) for t in texts]
    return client.batch_chat_concurrent(prompts, max_concurrency=max_concurrency)
