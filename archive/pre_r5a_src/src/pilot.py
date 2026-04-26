"""E_pilot: 50-100 case hard pilot for CFLS validation.

Validates three things:
1. Template comparability -- same semantic_reversal template on direct_prediction
   vs decomposed_impact produces comparable CFLS scores.
2. Effect shape -- non-binary gradient in shortcut susceptibility.
3. Scoring pipeline -- CFLS + evidence intrusion runs end-to-end.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, TYPE_CHECKING
from urllib.parse import urlparse

import httpx

from .masking import generate_false_outcome_cpt
from .metrics import batch_cfls, cfls_per_case, detect_evidence_intrusion
from .news_loader import load_test_cases
from .prompt_loader import PromptLoader

if TYPE_CHECKING:
    from .llm_client import LLMClient
    from .models import TestCase

ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = ROOT / "config" / "prompts"
SETTINGS_PATH = ROOT / "config" / "settings.yaml"
ENV_PATH = ROOT / ".env"

# Tasks used in the pilot comparison
PILOT_TASKS = ["direct_prediction.base", "decomposed_impact.base", "decomposed_authority.matched"]

# Map expected_direction -> label for direct_prediction
_DIRECTION_LABELS = {"up": "up", "down": "down", "neutral": "neutral"}

# Map expected_direction -> plausible fund_impact label
_DIRECTION_TO_IMPACT = {
    "up": "positive",
    "down": "negative",
    "neutral": "neutral",
}

# Flip maps
_FLIP_DIRECTION = {"up": "down", "down": "up"}
_FLIP_IMPACT = {
    "positive": "negative",
    "strong_positive": "strong_negative",
    "negative": "positive",
    "strong_negative": "strong_positive",
    "neutral": "neutral",
}


def _task_reversal_key(family: str) -> str:
    """Map a task family to its semantic-reversal condition key."""
    if family == "decomposed_impact":
        return "sr_fund_impact"
    # direct_prediction + decomposed_authority both use direction reversal
    return "sr_direction"


def _task_target_field(family: str) -> str:
    """Map a task family to the slot checked by _detect_fo_flip."""
    if family == "direct_prediction":
        return "direction"
    if family == "decomposed_impact":
        return "fund_impact"
    # authority + others: check all slots (empty = check all)
    return ""


def _flip_label(label: str, field: str) -> str:
    if field == "direction":
        return _FLIP_DIRECTION.get(label, label)
    return _FLIP_IMPACT.get(label, label)


def _article_text(tc: "TestCase") -> str:
    title = tc.news.title.strip()
    content = tc.news.content.strip()
    return f"{title}\n{content}" if title else content


def _safe_json_parse(raw: str) -> dict | None:
    from .masking import extract_json_robust

    try:
        parsed = json.loads(raw.strip())
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return extract_json_robust(raw)


# ── Batch helpers (Phase C1: 3-phase batching) ──────────────────────────────


def _batch_with_retry(
    client: "LLMClient",
    prompts: list[tuple[str, str]],
    validators: list | None = None,  # list of Callable[[LLMResponse], bool]
    max_concurrency: int = 20,
    max_retry_passes: int = 2,
) -> list[Any]:
    """Run a batch with per-prompt retry passes.

    Algorithm:
        - Pass 0: full batch via batch_chat_concurrent(failure_isolated=True)
        - For each retry pass (up to ``max_retry_passes``):
            - collect indices that are still BaseException OR fail validator
            - re-issue just those prompts with bypass_cache=True
            - patch results back into the same indices
        - Return the final ``list`` (length == len(prompts)). Entries are
          either an LLMResponse or BaseException.

    Stable indices are preserved across retries.
    """
    n = len(prompts)
    if n == 0:
        return []

    def _is_failed(idx: int, res: Any) -> bool:
        if isinstance(res, BaseException):
            return True
        if validators is not None and validators[idx] is not None:
            try:
                return not validators[idx](res)
            except Exception:
                return True
        return False

    # Pass 0
    results: list[Any] = list(
        client.batch_chat_concurrent(
            prompts,
            max_concurrency=max_concurrency,
            failure_isolated=True,
        )
    )

    for _ in range(max_retry_passes):
        failed_idx = [i for i in range(n) if _is_failed(i, results[i])]
        if not failed_idx:
            break
        retry_prompts = [prompts[i] for i in failed_idx]
        retry_results = list(
            client.batch_chat_concurrent(
                retry_prompts,
                max_concurrency=max_concurrency,
                bypass_cache=True,
                failure_isolated=True,
            )
        )
        for j, idx in enumerate(failed_idx):
            results[idx] = retry_results[j]

    return results


def _parse_cf_payload(
    response: Any,
    loader: PromptLoader,
    template_id: str,
    target: str,
) -> dict[str, Any] | None:
    """Parse + validate a CF response. Returns payload dict or None."""
    if isinstance(response, BaseException):
        return None
    from .masking import _parse_json_object

    try:
        parsed = _parse_json_object(
            response.raw_response, context=f"cf {template_id}"
        )
    except Exception:
        return None
    template = loader.get_counterfactual_template(template_id)
    errors = list(loader._validator.validate_schema(template.output_schema, parsed))
    if errors:
        return None
    if target:
        echo = parsed.get("target_echo", "")
        if echo and echo.strip() != target.strip():
            return None
    return parsed


def _build_cf_validator(
    loader: PromptLoader,
    template_id: str,
    target: str,
):
    """Return a validator that checks a CF response is parseable + schema-clean + target-correct."""
    def _validate(response: Any) -> bool:
        return _parse_cf_payload(response, loader, template_id, target) is not None
    return _validate


def prepare_cf_batch(
    client: "LLMClient",
    loader: PromptLoader,
    test_cases: list["TestCase"],
    max_concurrency: int = 20,
) -> dict[tuple[str, str], dict[str, Any] | None]:
    """Generate all SR + NP counterfactuals across all cases in one batch.

    Returns ``{(case_id, cf_type): payload | None}``. ``cf_type`` is one of
    ``sr_direction``, ``sr_fund_impact``, ``neutral_paraphrase``. The CF is
    skipped (omitted from the dict) when the source case has no flippable
    label (e.g., ``expected_direction == "neutral"`` for sr_direction).
    """
    # Step 1: collect prompt specs
    specs: list[dict[str, Any]] = []
    prompts: list[tuple[str, str]] = []

    for tc in test_cases:
        article = _article_text(tc)
        direction = getattr(tc.expected_direction, "value", tc.expected_direction)
        target = tc.target
        target_type = tc.target_type

        # sr_direction
        orig_dir = _DIRECTION_LABELS.get(direction, direction)
        flip_dir = _flip_label(orig_dir, "direction")
        if orig_dir != flip_dir:
            template = loader.get_counterfactual_template("semantic_reversal")
            user = loader.render_cf_prompt(
                "semantic_reversal", article,
                original_label=orig_dir, target_label=flip_dir,
                target_field="direction",
                target=target, target_type=target_type,
            )
            specs.append({
                "case_id": tc.id, "cf_type": "sr_direction",
                "template_id": "semantic_reversal", "target": target,
            })
            prompts.append((template.system_prompt, user))

        # sr_fund_impact
        orig_imp = _DIRECTION_TO_IMPACT.get(direction, "neutral")
        flip_imp = _flip_label(orig_imp, "fund_impact")
        if orig_imp != flip_imp:
            template = loader.get_counterfactual_template("semantic_reversal")
            user = loader.render_cf_prompt(
                "semantic_reversal", article,
                original_label=orig_imp, target_label=flip_imp,
                target_field="fund_impact",
                target=target, target_type=target_type,
            )
            specs.append({
                "case_id": tc.id, "cf_type": "sr_fund_impact",
                "template_id": "semantic_reversal", "target": target,
            })
            prompts.append((template.system_prompt, user))

        # neutral_paraphrase (always present)
        template = loader.get_counterfactual_template("neutral_paraphrase")
        user = loader.render_cf_prompt(
            "neutral_paraphrase", article,
            target=target, target_type=target_type,
        )
        specs.append({
            "case_id": tc.id, "cf_type": "neutral_paraphrase",
            "template_id": "neutral_paraphrase", "target": target,
        })
        prompts.append((template.system_prompt, user))

    # Step 2: validators
    validators = [
        _build_cf_validator(loader, s["template_id"], s["target"])
        for s in specs
    ]

    # Step 3: batch with retry
    print(f"  prepare_cf_batch: {len(prompts)} prompts across {len(test_cases)} cases")
    results = _batch_with_retry(
        client, prompts, validators=validators,
        max_concurrency=max_concurrency, max_retry_passes=2,
    )

    # Step 4: parse each into payload dict
    out: dict[tuple[str, str], dict[str, Any] | None] = {}
    n_failed = 0
    for spec, res in zip(specs, results):
        payload = _parse_cf_payload(res, loader, spec["template_id"], spec["target"])
        out[(spec["case_id"], spec["cf_type"])] = payload
        if payload is None:
            n_failed += 1
    print(f"  prepare_cf_batch: {n_failed} failed after {2} retry passes")
    return out


def prepare_fo_cpt_batch(
    client: "LLMClient",
    test_cases: list["TestCase"],
    max_concurrency: int = 20,
    fo_override: dict[str, str] | None = None,
) -> dict[str, tuple[str | None, str]]:
    """Compute false-outcome CPT articles for all cases.

    Pre-cutoff (with real ``known_outcome``): LLM-only negation, batched + retry.
    Post-cutoff / unknown: directional generic template (no API call).
    When ``fo_override`` is provided (``{case_id: false_outcome_text}``),
    those cases use the override text instead of on-the-fly generation.
    Returns ``{case_id: (modified_article_or_None, cpt_mode)}``.
    """
    from .masking import (
        _NEGATE_OUTCOME_PROMPT_SYSTEM,
        _NEGATE_OUTCOME_PROMPT_USER,
        _FALSE_OUTCOME_PHRASES_NEGATIVE,
        _FALSE_OUTCOME_PHRASES_POSITIVE,
        check_negation_polarity_flipped,
    )
    import random as _random

    out: dict[str, tuple[str | None, str]] = {}
    llm_specs: list[dict[str, Any]] = []
    llm_prompts: list[tuple[str, str]] = []

    for tc in test_cases:
        # B0.5: Use override text if provided for this case
        if fo_override and tc.id in fo_override:
            article = _article_text(tc)
            fo_text = fo_override[tc.id]
            hint = f"（注：据了解，{fo_text}。）"
            out[tc.id] = (f"{article}\n{hint}", "fo_override")
            continue

        known = (tc.known_outcome or "").strip()
        is_generic = not known or known == "unknown_post_cutoff"
        article = _article_text(tc)
        direction = getattr(tc.expected_direction, "value", tc.expected_direction)
        target = tc.target

        if is_generic:
            # Post-cutoff path: directional template, no API call.
            d = direction.strip().lower()
            if d in ("up", "positive", "strong_positive"):
                phrases = _FALSE_OUTCOME_PHRASES_NEGATIVE
            elif d in ("down", "negative", "strong_negative"):
                phrases = _FALSE_OUTCOME_PHRASES_POSITIVE
            else:
                phrases = _FALSE_OUTCOME_PHRASES_NEGATIVE
            phrase = _random.choice(phrases).format(target=target)
            hint = f"（注：据了解，{phrase}。）"
            out[tc.id] = (f"{article}\n{hint}", "generic_post_cutoff")
        else:
            llm_specs.append({
                "case_id": tc.id, "article": article, "known": known,
            })
            llm_prompts.append((
                _NEGATE_OUTCOME_PROMPT_SYSTEM,
                _NEGATE_OUTCOME_PROMPT_USER.format(known_outcome=known),
            ))

    if not llm_prompts:
        return out

    def _validate_negation(spec: dict[str, Any]):
        known = spec["known"]
        def _v(resp: Any) -> bool:
            if isinstance(resp, BaseException):
                return False
            text = resp.raw_response.strip()
            if not (text and text != known and len(text) < len(known) * 3):
                return False
            # Bug 4 fix: cheap polarity check on the LLM negation.
            return check_negation_polarity_flipped(known, text)
        return _v

    validators = [_validate_negation(s) for s in llm_specs]

    print(f"  prepare_fo_cpt_batch: {len(llm_prompts)} LLM-negation prompts (pre-cutoff)")
    results = _batch_with_retry(
        client, llm_prompts, validators=validators,
        max_concurrency=max_concurrency, max_retry_passes=2,
    )

    n_failed = 0
    for spec, res in zip(llm_specs, results):
        if isinstance(res, BaseException):
            out[spec["case_id"]] = (None, "llm_failed")
            n_failed += 1
            continue
        text = res.raw_response.strip()
        if not text or text == spec["known"] or len(text) >= len(spec["known"]) * 3:
            out[spec["case_id"]] = (None, "llm_failed")
            n_failed += 1
            continue
        # Bug 4 fix: cheap polarity check on the LLM negation.
        if not check_negation_polarity_flipped(spec["known"], text):
            out[spec["case_id"]] = (None, "llm_failed")
            n_failed += 1
            continue
        hint = f"（注：据了解，{text}。）"
        out[spec["case_id"]] = (f"{spec['article']}\n{hint}", "llm_negated")

    if n_failed:
        n_total_pre = len(llm_specs)
        pct = 100.0 * n_failed / n_total_pre
        print(f"  prepare_fo_cpt_batch: {n_failed}/{n_total_pre} ({pct:.1f}%) marked llm_failed")
    return out


def assemble_conditions(
    test_cases: list["TestCase"],
    cf_payloads: dict[tuple[str, str], dict[str, Any] | None],
    fo_results: dict[str, tuple[str | None, str]],
) -> dict[str, dict[str, dict[str, Any]]]:
    """Assemble per-case condition dicts (matching prepare_conditions output)."""
    conditions_per_case: dict[str, dict[str, dict[str, Any]]] = {}
    for tc in test_cases:
        article = _article_text(tc)
        conds: dict[str, dict[str, Any]] = {
            "original": {"article": article, "cf_payload": None, "source": "original"},
        }

        # sr_direction
        if (tc.id, "sr_direction") in cf_payloads:
            payload = cf_payloads[(tc.id, "sr_direction")]
            conds["sr_direction"] = {
                "article": payload["rewritten_article"] if payload else None,
                "cf_payload": payload,
                "source": "semantic_reversal:direction",
                "failed": payload is None,
            }
        else:
            conds["sr_direction"] = {
                "article": None, "cf_payload": None,
                "source": "semantic_reversal:direction:skipped_neutral",
                "failed": True,
            }

        # sr_fund_impact
        if (tc.id, "sr_fund_impact") in cf_payloads:
            payload = cf_payloads[(tc.id, "sr_fund_impact")]
            conds["sr_fund_impact"] = {
                "article": payload["rewritten_article"] if payload else None,
                "cf_payload": payload,
                "source": "semantic_reversal:fund_impact",
                "failed": payload is None,
            }
        else:
            conds["sr_fund_impact"] = {
                "article": None, "cf_payload": None,
                "source": "semantic_reversal:fund_impact:skipped_neutral",
                "failed": True,
            }

        # neutral_paraphrase
        np_payload = cf_payloads.get((tc.id, "neutral_paraphrase"))
        conds["neutral_paraphrase"] = {
            "article": np_payload["rewritten_article"] if np_payload else None,
            "cf_payload": np_payload,
            "source": "neutral_paraphrase",
            "failed": np_payload is None,
        }

        # false_outcome_cpt
        fo_article, cpt_mode = fo_results.get(tc.id, (None, "llm_failed"))
        conds["false_outcome_cpt"] = {
            "article": fo_article,
            "cf_payload": None,
            "source": "false_outcome_cpt",
            "cpt_mode": cpt_mode,
            "failed": fo_article is None,
        }

        conditions_per_case[tc.id] = conds
    return conditions_per_case


def run_tasks_batch(
    client: "LLMClient",
    loader: PromptLoader,
    test_cases: list["TestCase"],
    conditions_per_case: dict[str, dict[str, dict[str, Any]]],
    max_concurrency: int = 20,
) -> dict[str, dict[str, dict[str, dict[str, Any]]]]:
    """Run all (case × task × condition) prompts in one batch with retries.

    Returns ``{case_id: {task_id: {cond_name: response_dict}}}`` where each
    response_dict matches the legacy ``_batch_run_tasks`` shape (raw_response,
    parsed_output, valid, validation_errors, input_tokens, output_tokens) plus
    a ``skipped`` flag for skipped CF conditions.
    """
    # Step 1: collect (case_id, task_id, cond_name) -> prompt
    specs: list[dict[str, Any]] = []
    prompts: list[tuple[str, str]] = []

    for tc in test_cases:
        target = tc.target
        target_type = tc.target_type
        conds = conditions_per_case[tc.id]

        for task_id in PILOT_TASKS:
            family = task_id.split(".")[0]
            reversal_key = _task_reversal_key(family)
            condition_map = {
                "original": conds["original"],
                "semantic_reversal": conds[reversal_key],
                "neutral_paraphrase": conds["neutral_paraphrase"],
                "false_outcome_cpt": conds["false_outcome_cpt"],
            }
            for cond_name, cond in condition_map.items():
                if cond.get("failed") and cond_name != "original":
                    continue
                article = cond["article"]
                if article is None:
                    continue
                prompt = loader.get_task_prompt(task_id)
                user = loader.render_user_prompt(
                    task_id, article, target=target, target_type=target_type,
                )
                specs.append({
                    "case_id": tc.id, "task_id": task_id, "cond_name": cond_name,
                    "target": target,
                })
                prompts.append((prompt.system_prompt, user))

    print(f"  run_tasks_batch: {len(prompts)} task prompts across {len(test_cases)} cases")

    def _validate_task(spec: dict[str, Any]):
        task_id = spec["task_id"]
        target = spec["target"]
        def _v(resp: Any) -> bool:
            if isinstance(resp, BaseException):
                return False
            parsed = _safe_json_parse(resp.raw_response)
            if parsed is None:
                return False
            errs = loader.validate_output(task_id, parsed)
            if errs:
                return False
            if target and isinstance(parsed, dict):
                echo = parsed.get("target_echo", "")
                if echo and echo.strip() != target.strip():
                    return False
            return True
        return _v

    validators = [_validate_task(s) for s in specs]
    results = _batch_with_retry(
        client, prompts, validators=validators,
        max_concurrency=max_concurrency, max_retry_passes=2,
    )

    # Step 2: build output structure with all conditions present per task
    out: dict[str, dict[str, dict[str, dict[str, Any]]]] = {}
    for tc in test_cases:
        out[tc.id] = {tid: {} for tid in PILOT_TASKS}
        # Pre-fill skipped slots so downstream can iterate uniformly
        for task_id in PILOT_TASKS:
            family = task_id.split(".")[0]
            reversal_key = _task_reversal_key(family)
            cond_failed = {
                "semantic_reversal": conditions_per_case[tc.id][reversal_key].get("failed", False),
                "neutral_paraphrase": conditions_per_case[tc.id]["neutral_paraphrase"].get("failed", False),
                "false_outcome_cpt": conditions_per_case[tc.id]["false_outcome_cpt"].get("failed", False),
            }
            for cond_name in ("original", "semantic_reversal", "neutral_paraphrase", "false_outcome_cpt"):
                if cond_name != "original" and cond_failed.get(cond_name):
                    out[tc.id][task_id][cond_name] = {
                        "raw_response": None,
                        "parsed_output": None,
                        "valid": False,
                        "validation_errors": ["upstream_cf_failed"],
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "skipped": True,
                    }

    # Step 3: fill in actual results
    for spec, res in zip(specs, results):
        case_id = spec["case_id"]
        task_id = spec["task_id"]
        cond_name = spec["cond_name"]
        target = spec["target"]

        if isinstance(res, BaseException):
            out[case_id][task_id][cond_name] = {
                "raw_response": None,
                "parsed_output": None,
                "valid": False,
                "validation_errors": [f"Batch API error: {type(res).__name__}: {res}"],
                "input_tokens": 0,
                "output_tokens": 0,
            }
            continue

        parsed = _safe_json_parse(res.raw_response)
        validation_errors: list[str] = []
        if parsed is not None:
            validation_errors = loader.validate_output(task_id, parsed)
            if target and isinstance(parsed, dict):
                echo = parsed.get("target_echo", "")
                if echo and echo.strip() != target.strip():
                    validation_errors.append(
                        f"target_echo mismatch: expected '{target}', got '{echo}'"
                    )
        out[case_id][task_id][cond_name] = {
            "raw_response": res.raw_response,
            "parsed_output": parsed,
            "valid": parsed is not None and not validation_errors,
            "validation_errors": validation_errors,
            "input_tokens": res.input_tokens,
            "output_tokens": res.output_tokens,
        }

    # Confirm every case has every (task, cond) slot filled
    for tc in test_cases:
        for task_id in PILOT_TASKS:
            for cond_name in ("original", "semantic_reversal", "neutral_paraphrase", "false_outcome_cpt"):
                out[tc.id][task_id].setdefault(cond_name, {
                    "raw_response": None,
                    "parsed_output": None,
                    "valid": False,
                    "validation_errors": ["missing_after_batch"],
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "skipped": True,
                })

    return out


def score_case_from_batches(
    tc: "TestCase",
    conditions: dict[str, dict[str, Any]],
    task_responses: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, Any]:
    """Pure-CPU scoring step. Mirrors run_single_case scoring logic but takes
    pre-batched responses instead of issuing API calls.
    """
    target = tc.target
    target_type = tc.target_type
    article = _article_text(tc)

    task_results: dict[str, dict[str, Any]] = {}

    for task_id in PILOT_TASKS:
        family = task_id.split(".")[0]
        reversal_key = _task_reversal_key(family)
        sr_failed = conditions[reversal_key].get("failed", False)
        np_failed = conditions["neutral_paraphrase"].get("failed", False)

        responses = task_responses[task_id]
        fo_response = responses["false_outcome_cpt"]
        fo_parsed = fo_response.get("parsed_output") if fo_response.get("valid") else None
        orig_parsed_for_fo = (
            (responses["original"].get("parsed_output") or {})
            if responses["original"].get("valid") else None
        )
        direction_val = getattr(tc.expected_direction, "value", tc.expected_direction)
        target_field = _task_target_field(family)

        fo_flip_label: str | None = None
        fo_any_change: bool | None = None
        if orig_parsed_for_fo and fo_parsed:
            from .metrics import _detect_fo_flip, _detect_fo_any_change
            fo_flip_label = _detect_fo_flip(
                orig=orig_parsed_for_fo,
                cf_false_outcome=fo_parsed,
                expected_direction=direction_val,
                target_field=target_field,
            )
            fo_any_change = _detect_fo_any_change(
                orig=orig_parsed_for_fo,
                cf_false_outcome=fo_parsed,
            )
        from .metrics import fo_flip_label_to_strict, fo_flip_label_to_hedged
        fo_flip_strict = fo_flip_label_to_strict(fo_flip_label)
        fo_flip_hedged = fo_flip_label_to_hedged(fo_flip_label)

        core_valid = all(
            responses[k].get("valid", False)
            for k in ("original", "semantic_reversal", "neutral_paraphrase")
            if not responses[k].get("skipped")
        )
        if sr_failed or np_failed or not core_valid:
            fail_reason = "cf_generation_failed" if (sr_failed or np_failed) else "task_output_invalid"
            cfls_result = {
                "cfls": None,
                "mode": fail_reason,
                "cf_invariance": None,
                "para_invariance": None,
                "per_slot": {},
                "false_outcome_flip": fo_flip_strict,
                "false_outcome_flip_strict": fo_flip_strict,
                "false_outcome_flip_hedged": fo_flip_hedged,
                "false_outcome_flip_label": fo_flip_label,
                "fo_any_change": fo_any_change,
                "task_id": task_id,
            }
        else:
            orig_parsed = responses["original"]["parsed_output"] or {}
            sr_parsed = responses["semantic_reversal"]["parsed_output"] or {}
            np_parsed = responses["neutral_paraphrase"]["parsed_output"] or {}
            cfls_result = cfls_per_case(
                orig=orig_parsed,
                cf_reversal=sr_parsed,
                para=np_parsed,
                cf_false_outcome=fo_parsed,
                task_id=task_id,
                expected_direction=direction_val,
                reversal_target_field=target_field,
            )
            # Override with the canonical _detect_fo_flip values; cfls_per_case
            # has its own duplicate logic that we ignore for v3.
            cfls_result["false_outcome_flip"] = fo_flip_strict
            cfls_result["false_outcome_flip_strict"] = fo_flip_strict
            cfls_result["false_outcome_flip_hedged"] = fo_flip_hedged
            cfls_result["false_outcome_flip_label"] = fo_flip_label
            cfls_result["fo_any_change"] = fo_any_change

        intrusion = detect_evidence_intrusion(
            article=article,
            response=responses["original"]["raw_response"],
            known_outcome=tc.known_outcome,
            outcome_date=tc.outcome_date,
        )

        task_results[task_id] = {
            "responses": responses,
            "cfls": cfls_result,
            "evidence_intrusion": intrusion,
        }

    direct_cfls = task_results["direct_prediction.base"]["cfls"]
    impact_cfls = task_results["decomposed_impact.base"]["cfls"]
    authority_cfls = task_results["decomposed_authority.matched"]["cfls"]
    fo_condition = conditions.get("false_outcome_cpt", {})
    return {
        "case_id": tc.id,
        "target": target,
        "target_type": target_type,
        "expected_direction": getattr(tc.expected_direction, "value", tc.expected_direction),
        "memorization_likelihood": getattr(tc, "memorization_likelihood", None),
        "category": getattr(tc.news.category, "value", tc.news.category),
        "cpt_mode": fo_condition.get("cpt_mode"),  # Bug 5 fix: persist probe modality
        "tasks": task_results,
        "metrics": {
            "cfls_direct": direct_cfls["cfls"],
            "cfls_impact": impact_cfls["cfls"],
            "cfls_authority": authority_cfls["cfls"],
            # Legacy aliases (strict semantics) — kept so older scripts that
            # read fo_flip_direct/impact continue to work without change.
            "fo_flip_direct": direct_cfls.get("false_outcome_flip_strict"),
            "fo_flip_impact": impact_cfls.get("false_outcome_flip_strict"),
            # New explicit variants from the Bug 3 fix.
            "fo_flip_direct_strict": direct_cfls.get("false_outcome_flip_strict"),
            "fo_flip_direct_hedged": direct_cfls.get("false_outcome_flip_hedged"),
            "fo_flip_direct_label":  direct_cfls.get("false_outcome_flip_label"),
            "fo_flip_impact_strict": impact_cfls.get("false_outcome_flip_strict"),
            "fo_flip_impact_hedged": impact_cfls.get("false_outcome_flip_hedged"),
            "fo_flip_impact_label":  impact_cfls.get("false_outcome_flip_label"),
            # Authority: non-directional task — fo_any_change is the primary metric
            "fo_flip_authority_label": authority_cfls.get("false_outcome_flip_label"),
            "fo_any_change_authority": authority_cfls.get("fo_any_change"),
            "intrusion_direct": task_results["direct_prediction.base"]["evidence_intrusion"]["detected"],
            "intrusion_impact": task_results["decomposed_impact.base"]["evidence_intrusion"]["detected"],
            "intrusion_authority": task_results["decomposed_authority.matched"]["evidence_intrusion"]["detected"],
        },
    }


def run_chunk_batched(
    client: "LLMClient",
    loader: PromptLoader,
    test_cases: list["TestCase"],
    max_concurrency: int = 20,
    fo_override: dict[str, str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Run a chunk of cases through Phase 1-4 batching.

    Returns ``(case_results, errors)``. ``errors`` is a list of
    ``{case_id, stage, reason}`` dicts for any per-case failures
    encountered (currently used for cases that crash during scoring).
    """
    if not test_cases:
        return [], []

    # Phase 1: CF generation
    print(f"\n[batch] Phase 1: CF generation ({len(test_cases)} cases)")
    cf_payloads = prepare_cf_batch(client, loader, test_cases, max_concurrency)

    # Phase 2: FO CPT (LLM negation for pre-cutoff, generic for post-cutoff)
    print(f"[batch] Phase 2: FO CPT ({len(test_cases)} cases)")
    fo_results = prepare_fo_cpt_batch(client, test_cases, max_concurrency, fo_override=fo_override)

    # Assemble per-case conditions from phase 1 + 2
    conditions_per_case = assemble_conditions(test_cases, cf_payloads, fo_results)

    # Phase 3: task execution
    print(f"[batch] Phase 3: task execution")
    task_responses = run_tasks_batch(
        client, loader, test_cases, conditions_per_case, max_concurrency,
    )

    # Phase 4: scoring (CPU)
    print(f"[batch] Phase 4: scoring")
    case_results: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for tc in test_cases:
        try:
            cr = score_case_from_batches(
                tc, conditions_per_case[tc.id], task_responses[tc.id],
            )
            case_results.append(cr)
        except Exception as exc:
            errors.append({
                "case_id": tc.id,
                "stage": "scoring",
                "reason": f"{type(exc).__name__}: {exc}",
            })

    return case_results, errors


def _generate_cf_safe(
    client: "LLMClient",
    _loader: PromptLoader,
    template_id: str,
    article: str,
    max_attempts: int = 3,
    **kwargs: Any,
) -> dict[str, Any] | None:
    """Generate a counterfactual with retry, return parsed payload or None."""
    from .masking import generate_counterfactual_from_template

    target = kwargs.get("target", "")
    for attempt in range(1, max_attempts + 1):
        try:
            payload = generate_counterfactual_from_template(
                article=article,
                template_id=template_id,
                client=client,
                prompts_dir=str(PROMPTS_DIR),
                bypass_cache=attempt > 1,
                **kwargs,
            )
            # Validate target_echo on CF rewrite
            if target and isinstance(payload, dict):
                echo = payload.get("target_echo", "")
                if echo and echo.strip() != target.strip():
                    raise ValueError(
                        f"CF target_echo mismatch: expected '{target}', got '{echo}'"
                    )
            return payload
        except Exception as exc:
            print(f"  [WARN] CF {template_id} attempt {attempt}: {exc}")
    return None


def prepare_conditions(
    client: "LLMClient",
    loader: PromptLoader,
    tc: "TestCase",
) -> dict[str, dict[str, Any]]:
    """Generate all article conditions for a single test case.

    Returns dict with keys: original, sr_direction, sr_fund_impact,
    neutral_paraphrase, false_outcome_cpt.
    Each value has: article (str), cf_payload (dict|None), source (str).
    """
    article = _article_text(tc)
    direction = getattr(tc.expected_direction, "value", tc.expected_direction)
    target = tc.target
    target_type = tc.target_type

    conditions: dict[str, dict[str, Any]] = {
        "original": {"article": article, "cf_payload": None, "source": "original"},
    }

    # Semantic reversal for direction (direct_prediction)
    orig_direction = _DIRECTION_LABELS.get(direction, direction)
    flipped_direction = _flip_label(orig_direction, "direction")
    if orig_direction != flipped_direction:
        sr_dir = _generate_cf_safe(
            client, loader, "semantic_reversal", article,
            original_label=orig_direction,
            target_label=flipped_direction,
            target_field="direction",
            target=target,
            target_type=target_type,
        )
        conditions["sr_direction"] = {
            "article": sr_dir["rewritten_article"] if sr_dir else None,
            "cf_payload": sr_dir,
            "source": "semantic_reversal:direction",
            "failed": sr_dir is None,
        }
    else:
        conditions["sr_direction"] = {
            "article": None,
            "cf_payload": None,
            "source": "semantic_reversal:direction:skipped_neutral",
            "failed": True,
        }

    # Semantic reversal for fund_impact (decomposed_impact)
    orig_impact = _DIRECTION_TO_IMPACT.get(direction, "neutral")
    flipped_impact = _flip_label(orig_impact, "fund_impact")
    if orig_impact != flipped_impact:
        sr_impact = _generate_cf_safe(
            client, loader, "semantic_reversal", article,
            original_label=orig_impact,
            target_label=flipped_impact,
            target_field="fund_impact",
            target=target,
            target_type=target_type,
        )
        conditions["sr_fund_impact"] = {
            "article": sr_impact["rewritten_article"] if sr_impact else None,
            "cf_payload": sr_impact,
            "source": "semantic_reversal:fund_impact",
            "failed": sr_impact is None,
        }
    else:
        conditions["sr_fund_impact"] = {
            "article": None,
            "cf_payload": None,
            "source": "semantic_reversal:fund_impact:skipped_neutral",
            "failed": True,
        }

    # Neutral paraphrase (shared across tasks)
    np_payload = _generate_cf_safe(
        client, loader, "neutral_paraphrase", article,
        target=target,
        target_type=target_type,
    )
    conditions["neutral_paraphrase"] = {
        "article": np_payload["rewritten_article"] if np_payload else None,
        "cf_payload": np_payload,
        "source": "neutral_paraphrase",
        "failed": np_payload is None,
    }

    # False-outcome CPT (LLM-based negation for pre-cutoff, generic for post-cutoff)
    fo_article, cpt_mode = generate_false_outcome_cpt(
        article=article,
        known_outcome=tc.known_outcome,
        expected_direction=direction,
        target=target,
        client=client,
    )
    conditions["false_outcome_cpt"] = {
        "article": fo_article,
        "cf_payload": None,
        "source": "false_outcome_cpt",
        "cpt_mode": cpt_mode,
        # Mark failed=True so run_single_case skips task execution for this
        # condition. Pre-cutoff llm_failed cases get None article -- excluded
        # from CPT analysis with a missingness footnote in E1/E2.
        "failed": fo_article is None,
    }

    return conditions


def _batch_run_tasks(
    client: "LLMClient",
    loader: PromptLoader,
    jobs: list[tuple[str, str, str, str]],
    max_concurrency: int = 20,
) -> list[dict[str, Any]]:
    """Run multiple task prompts concurrently.

    Each job is (task_id, article, target, target_type).
    Returns list of result dicts in the same order as jobs.
    """
    # Build prompts
    prompt_pairs: list[tuple[str, str]] = []
    task_ids: list[str] = []
    targets: list[str] = []
    for task_id, article, target, target_type in jobs:
        prompt = loader.get_task_prompt(task_id)
        user_prompt = loader.render_user_prompt(
            task_id, article, target=target, target_type=target_type,
        )
        prompt_pairs.append((prompt.system_prompt, user_prompt))
        task_ids.append(task_id)
        targets.append(target)

    # Batch call
    try:
        responses = client.batch_chat_concurrent(
            prompt_pairs, max_concurrency=max_concurrency,
        )
    except Exception as exc:
        # If batch fails entirely, return error for all
        return [{
            "raw_response": None,
            "parsed_output": None,
            "valid": False,
            "validation_errors": [f"Batch API error: {type(exc).__name__}: {exc}"],
            "input_tokens": 0,
            "output_tokens": 0,
        }] * len(jobs)

    # Parse and validate each response
    results: list[dict[str, Any]] = []
    for resp, task_id, target in zip(responses, task_ids, targets):
        parsed = _safe_json_parse(resp.raw_response)
        validation_errors: list[str] = []
        if parsed is not None:
            validation_errors = loader.validate_output(task_id, parsed)
            if target and isinstance(parsed, dict):
                echo = parsed.get("target_echo", "")
                if echo and echo.strip() != target.strip():
                    validation_errors.append(
                        f"target_echo mismatch: expected '{target}', got '{echo}'"
                    )
        results.append({
            "raw_response": resp.raw_response,
            "parsed_output": parsed,
            "valid": parsed is not None and not validation_errors,
            "validation_errors": validation_errors,
            "input_tokens": resp.input_tokens,
            "output_tokens": resp.output_tokens,
        })
    return results


def run_single_case(
    client: "LLMClient",
    loader: PromptLoader,
    tc: "TestCase",
    conditions: dict[str, dict[str, Any]],
    max_concurrency: int = 20,
) -> dict[str, Any]:
    """Run both pilot tasks on all conditions for one test case (concurrent)."""
    target = tc.target
    target_type = tc.target_type
    article = _article_text(tc)

    # Build all jobs across tasks and conditions
    job_keys: list[tuple[str, str]] = []  # (task_id, cond_name)
    jobs: list[tuple[str, str, str, str]] = []  # (task_id, article, target, target_type)
    skipped: dict[tuple[str, str], bool] = {}

    for task_id in PILOT_TASKS:
        family = task_id.split(".")[0]
        reversal_key = _task_reversal_key(family)
        condition_map = {
            "original": conditions["original"],
            "semantic_reversal": conditions[reversal_key],
            "neutral_paraphrase": conditions["neutral_paraphrase"],
            "false_outcome_cpt": conditions["false_outcome_cpt"],
        }
        for cond_name, cond in condition_map.items():
            key = (task_id, cond_name)
            if cond.get("failed") and cond_name != "original":
                skipped[key] = True
                continue
            job_keys.append(key)
            jobs.append((task_id, cond["article"], target, target_type))

    # Run all non-skipped jobs concurrently
    batch_results = _batch_run_tasks(client, loader, jobs, max_concurrency)

    # Reassemble responses by (task_id, cond_name)
    result_iter = iter(batch_results)
    all_responses: dict[tuple[str, str], dict[str, Any]] = {}
    for key in job_keys:
        all_responses[key] = next(result_iter)
    for key in skipped:
        all_responses[key] = {
            "raw_response": None,
            "parsed_output": None,
            "input_tokens": 0,
            "output_tokens": 0,
            "skipped": True,
        }

    task_results: dict[str, dict[str, Any]] = {}

    for task_id in PILOT_TASKS:
        family = task_id.split(".")[0]
        reversal_key = _task_reversal_key(family)

        sr_failed = conditions[reversal_key].get("failed", False)
        np_failed = conditions["neutral_paraphrase"].get("failed", False)

        responses = {
            cond_name: all_responses[(task_id, cond_name)]
            for cond_name in ("original", "semantic_reversal", "neutral_paraphrase", "false_outcome_cpt")
        }

        # ── FO flip: score independently of SR/NP success (H3 fix) ──
        fo_response = responses["false_outcome_cpt"]
        fo_parsed = fo_response["parsed_output"] if fo_response.get("valid") else None
        orig_parsed_for_fo = (responses["original"].get("parsed_output") or {}) if responses["original"].get("valid") else None
        direction_val = getattr(tc.expected_direction, "value", tc.expected_direction)
        target_field = _task_target_field(family)

        # Compute fo_flip whenever original + CPT are both valid
        fo_flip_label: str | None = None
        fo_any_change: bool | None = None
        if orig_parsed_for_fo and fo_parsed:
            from .metrics import _detect_fo_flip, _detect_fo_any_change
            fo_flip_label = _detect_fo_flip(
                orig=orig_parsed_for_fo,
                cf_false_outcome=fo_parsed,
                expected_direction=direction_val,
                target_field=target_field,
            )
            fo_any_change = _detect_fo_any_change(
                orig=orig_parsed_for_fo,
                cf_false_outcome=fo_parsed,
            )
        from .metrics import fo_flip_label_to_strict, fo_flip_label_to_hedged
        fo_flip_strict = fo_flip_label_to_strict(fo_flip_label)
        fo_flip_hedged = fo_flip_label_to_hedged(fo_flip_label)

        # ── CFLS: requires SR + NP + original all valid ──
        core_valid = all(
            responses[k].get("valid", False)
            for k in ("original", "semantic_reversal", "neutral_paraphrase")
            if not responses[k].get("skipped")
        )
        if sr_failed or np_failed or not core_valid:
            fail_reason = "cf_generation_failed" if (sr_failed or np_failed) else "task_output_invalid"
            cfls_result = {
                "cfls": None,
                "mode": fail_reason,
                "cf_invariance": None,
                "para_invariance": None,
                "per_slot": {},
                "false_outcome_flip": fo_flip_strict,  # H3: scored independently
                "false_outcome_flip_strict": fo_flip_strict,
                "false_outcome_flip_hedged": fo_flip_hedged,
                "false_outcome_flip_label": fo_flip_label,
                "fo_any_change": fo_any_change,
                "task_id": task_id,
            }
        else:
            orig_parsed = responses["original"]["parsed_output"] or {}
            sr_parsed = responses["semantic_reversal"]["parsed_output"] or {}
            np_parsed = responses["neutral_paraphrase"]["parsed_output"] or {}

            cfls_result = cfls_per_case(
                orig=orig_parsed,
                cf_reversal=sr_parsed,
                para=np_parsed,
                cf_false_outcome=fo_parsed,
                task_id=task_id,
                expected_direction=direction_val,
                reversal_target_field=target_field,
            )
            # Override fo_flip with independently computed value
            cfls_result["false_outcome_flip"] = fo_flip_strict
            cfls_result["false_outcome_flip_strict"] = fo_flip_strict
            cfls_result["false_outcome_flip_hedged"] = fo_flip_hedged
            cfls_result["false_outcome_flip_label"] = fo_flip_label
            cfls_result["fo_any_change"] = fo_any_change

        # Evidence intrusion on original response
        intrusion = detect_evidence_intrusion(
            article=article,
            response=responses["original"]["raw_response"],
            known_outcome=tc.known_outcome,
            outcome_date=tc.outcome_date,
        )

        task_results[task_id] = {
            "responses": responses,
            "cfls": cfls_result,
            "evidence_intrusion": intrusion,
        }

    direct_cfls = task_results["direct_prediction.base"]["cfls"]
    impact_cfls = task_results["decomposed_impact.base"]["cfls"]
    authority_cfls = task_results["decomposed_authority.matched"]["cfls"]
    fo_condition = conditions.get("false_outcome_cpt", {})
    return {
        "case_id": tc.id,
        "target": target,
        "target_type": target_type,
        "expected_direction": getattr(tc.expected_direction, "value", tc.expected_direction),
        "memorization_likelihood": tc.memorization_likelihood,
        "category": getattr(tc.news.category, "value", tc.news.category),
        "cpt_mode": fo_condition.get("cpt_mode"),  # Bug 5 fix: persist probe modality
        "tasks": task_results,
        "metrics": {
            "cfls_direct": direct_cfls["cfls"],
            "cfls_impact": impact_cfls["cfls"],
            "cfls_authority": authority_cfls["cfls"],
            "fo_flip_direct": direct_cfls.get("false_outcome_flip_strict"),
            "fo_flip_impact": impact_cfls.get("false_outcome_flip_strict"),
            "fo_flip_direct_strict": direct_cfls.get("false_outcome_flip_strict"),
            "fo_flip_direct_hedged": direct_cfls.get("false_outcome_flip_hedged"),
            "fo_flip_direct_label":  direct_cfls.get("false_outcome_flip_label"),
            "fo_flip_impact_strict": impact_cfls.get("false_outcome_flip_strict"),
            "fo_flip_impact_hedged": impact_cfls.get("false_outcome_flip_hedged"),
            "fo_flip_impact_label":  impact_cfls.get("false_outcome_flip_label"),
            "fo_flip_authority_label": authority_cfls.get("false_outcome_flip_label"),
            "fo_any_change_authority": authority_cfls.get("fo_any_change"),
            "intrusion_direct": task_results["direct_prediction.base"]["evidence_intrusion"]["detected"],
            "intrusion_impact": task_results["decomposed_impact.base"]["evidence_intrusion"]["detected"],
            "intrusion_authority": task_results["decomposed_authority.matched"]["evidence_intrusion"]["detected"],
        },
    }


def _atomic_write(path: Path, data: dict[str, Any]) -> None:
    """Write JSON atomically via temp file + rename to prevent corruption."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(path)


def _incremental_save(
    output_path: Path,
    case_results: list[dict[str, Any]],
    n_total: int,
    seed: int,
) -> None:
    """Save partial results so progress isn't lost on crash."""
    partial = {
        "meta": {
            "experiment": "E_pilot",
            "n_cases_completed": len(case_results),
            "n_cases_total": n_total,
            "timestamp": datetime.now(UTC).isoformat(),
            "seed": seed,
            "partial": True,
        },
        "cases": case_results,
    }
    _atomic_write(output_path, partial)


def run_pilot(
    client: "LLMClient",
    loader: PromptLoader,
    test_cases: list["TestCase"],
    output_path: Path,
    seed: int = 42,
) -> dict[str, Any]:
    """Run the full E_pilot experiment."""
    random.seed(seed)
    n = len(test_cases)
    print(f"E_pilot: running {n} cases across {len(PILOT_TASKS)} tasks")

    all_case_results: list[dict[str, Any]] = []

    for i, tc in enumerate(test_cases, 1):
        direction = getattr(tc.expected_direction, "value", tc.expected_direction)
        print(f"\n[{i}/{n}] {tc.id} | {tc.target} ({tc.target_type}) | {direction}")

        try:
            # Phase A: generate conditions
            print("  Generating counterfactual conditions...")
            conditions = prepare_conditions(client, loader, tc)
            for cond_name, cond in conditions.items():
                if cond_name in ("original", "false_outcome_cpt"):
                    status = "OK"
                elif cond.get("failed"):
                    status = "FAILED"
                else:
                    status = "OK"
                print(f"    {cond_name}: {status}")

            # Phase B: run tasks
            print("  Running tasks...")
            case_result = run_single_case(client, loader, tc, conditions)
            all_case_results.append(case_result)

            cfls_d = case_result["metrics"]["cfls_direct"]
            cfls_i = case_result["metrics"]["cfls_impact"]
            d_str = f"{cfls_d:.2f}" if cfls_d is not None else "N/A"
            i_str = f"{cfls_i:.2f}" if cfls_i is not None else "N/A"
            print(f"  CFLS: direct={d_str}, impact={i_str}")
        except Exception as exc:
            print(f"  [ERROR] Case {tc.id} failed: {type(exc).__name__}: {exc}")

        # Incremental save every 5 completed cases
        if len(all_case_results) > 0 and len(all_case_results) % 5 == 0:
            _incremental_save(output_path, all_case_results, n, seed)

    # Phase C: aggregate (filter out cases with failed CF generation)
    print("\nAggregating results...")
    all_cfls_entries = []
    for cr in all_case_results:
        for task_id in PILOT_TASKS:
            cfls_data = cr["tasks"][task_id]["cfls"]
            if cfls_data.get("cfls") is not None:
                # Tag with case_id for paired correlation
                cfls_data["case_id"] = cr["case_id"]
                all_cfls_entries.append(cfls_data)

    aggregated = batch_cfls(all_cfls_entries)

    # Always clear positional correlation — we recompute by case_id pairing below
    aggregated["correlation"] = None

    # Compute case-id-paired cross-task correlation
    if len(PILOT_TASKS) == 2:
        paired: dict[str, dict[str, float]] = {}
        for cr in all_case_results:
            cid = cr["case_id"]
            scores = {}
            for tid in PILOT_TASKS:
                s = cr["tasks"][tid]["cfls"].get("cfls")
                if s is not None:
                    scores[tid] = s
            if len(scores) == 2:
                paired[cid] = scores
        if len(paired) > 1:
            import numpy as _np
            s1 = [v[PILOT_TASKS[0]] for v in paired.values()]
            s2 = [v[PILOT_TASKS[1]] for v in paired.values()]
            corr = _np.corrcoef(s1, s2)[0, 1]
            aggregated["correlation"] = None if _np.isnan(corr) else float(corr)
            aggregated["correlation_n_paired"] = len(paired)

    # Build output
    output = {
        "meta": {
            "experiment": "E_pilot",
            "n_cases": n,
            "tasks": PILOT_TASKS,
            "timestamp": datetime.now(UTC).isoformat(),
            "seed": seed,
        },
        "cases": all_case_results,
        "aggregated": aggregated,
    }

    # Save
    _atomic_write(output_path, output)
    print(f"\nResults saved to {output_path}")

    # Summary
    by_task = aggregated.get("by_task", {})
    for task_id, stats in by_task.items():
        print(f"  {task_id}: mean_cfls={stats['mean']:.3f} std={stats['std']:.3f} "
              f"positive_rate={stats['positive_rate']:.1%}")

    if aggregated.get("correlation") is not None:
        print(f"  Cross-task correlation: {aggregated['correlation']:.3f}")

    return output


def _build_client(
    settings_path: Path | None = None,
    model: str | None = None,
    base_url: str | None = None,
    api_key_env: str | None = None,
) -> "LLMClient":
    """Build LLMClient from settings with optional CLI overrides.

    Priority (highest first): explicit arguments > settings YAML > .env > env vars.
    """
    import yaml

    from .llm_client import LLMClient

    settings_file = settings_path or SETTINGS_PATH
    settings = yaml.safe_load(settings_file.read_text(encoding="utf-8"))
    env_values = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env_values[k.strip()] = v.strip().strip("\"'")

    llm_config = settings.get("llm", {})

    # --- Resolve base_url ---
    resolved_base_url = base_url or str(
        llm_config.get("base_url")
        or env_values.get("DEEPSEEK_BASE_URL")
        or env_values.get("DEEPSEEK_API_BASE")
        or "https://api.deepseek.com/v1"
    )

    # --- Resolve API key ---
    # api_key_env overrides the default env var name to look up
    key_env_name = api_key_env or str(llm_config.get("api_key_env", "DEEPSEEK_API_KEY"))
    api_key = env_values.get(key_env_name) or os.getenv(key_env_name, "")
    # For local vLLM, any non-empty key works (convention: "EMPTY")
    if not api_key and llm_config.get("provider") == "qwen":
        api_key = "EMPTY"
    if not api_key:
        print(f"ERROR: {key_env_name} not found in {ENV_PATH} or environment")
        sys.exit(1)

    # --- Resolve model ---
    resolved_model = model or str(llm_config.get("model", "deepseek-chat"))

    # --- Configure NO_PROXY ---
    host = urlparse(resolved_base_url).hostname or ""
    entries = ["localhost", "127.0.0.1"]
    if host:
        entries.append(host)
    os.environ["NO_PROXY"] = ",".join(dict.fromkeys(entries))
    os.environ["no_proxy"] = os.environ["NO_PROXY"]

    # --- Optional sampling parameters ---
    top_p = llm_config.get("top_p")  # None = not sent
    repetition_penalty = llm_config.get("repetition_penalty")  # None = not sent
    request_logprobs = bool(llm_config.get("request_logprobs", False))

    client = LLMClient(
        base_url=resolved_base_url,
        model=resolved_model,
        temperature=float(llm_config.get("temperature", 0.0)),
        max_tokens=int(llm_config.get("max_tokens", 2048)),
        api_key=api_key,
        enable_cache=True,
        request_logprobs=request_logprobs,
        top_p=top_p,
        repetition_penalty=repetition_penalty,
    )
    # Reset httpx client without proxy
    client._client.close()
    client._client = httpx.Client(timeout=120.0, proxy=None, trust_env=False)
    return client


def main() -> int:
    parser = argparse.ArgumentParser(description="E_pilot: CFLS validation pilot")
    parser.add_argument("--n-cases", type=int, default=0, help="Limit number of cases (0=all)")
    parser.add_argument("--output", type=str, default="data/results/pilot_results.json")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    client = _build_client()
    loader = PromptLoader(prompts_dir=str(PROMPTS_DIR))
    test_cases = load_test_cases(ROOT / "data" / "seed" / "test_cases.json")

    # Filter to non-neutral cases for the pilot (need direction to flip)
    eligible = [
        tc for tc in test_cases
        if getattr(tc.expected_direction, "value", tc.expected_direction) in ("up", "down")
        and tc.target  # must have target annotation
    ]
    print(f"Eligible cases (non-neutral, annotated): {len(eligible)} / {len(test_cases)}")

    if args.n_cases > 0:
        eligible = eligible[: args.n_cases]

    try:
        run_pilot(
            client=client,
            loader=loader,
            test_cases=eligible,
            output_path=ROOT / args.output,
            seed=args.seed,
        )
        return 0
    finally:
        client._client.close()


if __name__ == "__main__":
    raise SystemExit(main())
