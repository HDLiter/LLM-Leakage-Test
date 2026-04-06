from __future__ import annotations

import json
import os
import sys
from copy import deepcopy
from datetime import datetime, UTC
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
import yaml

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.llm_client import LLMClient
from src.masking import extract_json_robust, generate_counterfactual_from_template
from src.metrics import excess_invariance
from src.news_loader import load_test_cases
from src.prompt_loader import PromptLoader


TASK_IDS = [
    "direct_prediction.base",
    "direct_prediction.matched",
    "sentiment_classification.base",
    "sentiment_classification.matched",
    "decomposed_authority.base",
    "decomposed_authority.matched",
    "decomposed_novelty.base",
    "decomposed_novelty.matched",
    "decomposed_impact.base",
    "decomposed_impact.matched",
    "sham_decomposition.control",
]

RESULTS_PATH = ROOT / "data" / "results" / "smoke_test_prompts.json"
SETTINGS_PATH = ROOT / "config" / "settings.yaml"
ENV_PATH = ROOT / ".env"
PROMPTS_DIR = ROOT / "config" / "prompts"
TEST_CASES_PATH = ROOT / "data" / "seed" / "test_cases.json"


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_env_file(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        return env

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip().strip("\"'")
    return env


def article_text(test_case: Any) -> str:
    title = test_case.news.title.strip()
    content = test_case.news.content.strip()
    return f"{title}\n{content}" if title else content


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def json_preview(payload: Any, limit: int = 80) -> str:
    if payload is None:
        return ""
    return truncate(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        limit,
    )


def select_diverse_articles(test_cases: list[Any], limit: int = 3) -> list[Any]:
    category_order = ["policy", "corporate", "industry", "macro"]
    by_category: dict[str, list[Any]] = {}
    for test_case in test_cases:
        category = str(getattr(test_case.news.category, "value", test_case.news.category))
        by_category.setdefault(category, []).append(test_case)

    selected: list[Any] = []
    selected_ids: set[str] = set()
    used_directions: set[str] = set()

    for category in category_order:
        candidates = by_category.get(category, [])
        if not candidates:
            continue

        choice = next(
            (
                test_case
                for test_case in candidates
                if test_case.id not in selected_ids
                and str(
                    getattr(
                        test_case.expected_direction,
                        "value",
                        test_case.expected_direction,
                    )
                )
                not in used_directions
            ),
            None,
        )
        if choice is None:
            choice = next(
                (test_case for test_case in candidates if test_case.id not in selected_ids),
                None,
            )
        if choice is None:
            continue

        selected.append(choice)
        selected_ids.add(choice.id)
        used_directions.add(
            str(getattr(choice.expected_direction, "value", choice.expected_direction))
        )
        if len(selected) >= limit:
            return selected

    remaining = [test_case for test_case in test_cases if test_case.id not in selected_ids]
    remaining.sort(
        key=lambda test_case: (
            str(getattr(test_case.news.category, "value", test_case.news.category))
            in {str(getattr(item.news.category, "value", item.news.category)) for item in selected},
            str(
                getattr(
                    test_case.expected_direction,
                    "value",
                    test_case.expected_direction,
                )
            )
            in used_directions,
        )
    )

    for test_case in remaining:
        selected.append(test_case)
        if len(selected) >= limit:
            break

    return selected


def parse_json_object(text: str, context: str) -> dict[str, Any]:
    raw = text.strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = extract_json_robust(raw)

    if parsed is None:
        snippet = truncate(raw.replace("\n", " "), 200)
        raise ValueError(f"Could not parse JSON object from {context}: {snippet!r}")
    if not isinstance(parsed, dict):
        raise ValueError(
            f"Expected {context} to return a JSON object, got {type(parsed).__name__}"
        )
    return parsed


def configure_no_proxy(base_url: str) -> str:
    host = urlparse(base_url).hostname or ""
    entries = ["localhost", "127.0.0.1"]
    if host:
        entries.append(host)
        if host.endswith(".deepseek.com"):
            entries.append("deepseek.com")
    no_proxy = ",".join(dict.fromkeys(entries))
    os.environ["NO_PROXY"] = no_proxy
    os.environ["no_proxy"] = no_proxy
    return no_proxy


def build_client(settings: dict[str, Any], env_values: dict[str, str]) -> tuple[LLMClient, dict[str, Any]]:
    llm_config = settings.get("llm", {})
    experiment_config = settings.get("experiment", {})

    base_url = (
        env_values.get("DEEPSEEK_BASE_URL")
        or env_values.get("DEEPSEEK_API_BASE")
        or str(llm_config.get("base_url", "https://api.deepseek.com/v1"))
    )
    api_key = env_values.get("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key:
        raise RuntimeError(f"DEEPSEEK_API_KEY is missing from {ENV_PATH}")

    no_proxy = configure_no_proxy(base_url)

    client = LLMClient(
        base_url=base_url,
        model=str(llm_config.get("model", "deepseek-chat")),
        temperature=0.0,
        max_tokens=int(llm_config.get("max_tokens", 2048)),
        api_key=api_key,
        enable_cache=bool(experiment_config.get("cache_results", True)),
    )
    client._client.close()
    client._client = httpx.Client(timeout=120.0, proxy=None, trust_env=False)

    metadata = {
        "base_url": base_url,
        "model": client.model,
        "temperature": client.temperature,
        "max_tokens": client.max_tokens,
        "no_proxy": no_proxy,
    }
    return client, metadata


def run_task_safe(
    client: LLMClient,
    loader: PromptLoader,
    task_id: str,
    article: str,
    article_id: str,
    target: str = "",
    target_type: str = "",
) -> dict[str, Any]:
    prompt = loader.get_task_prompt(task_id)
    result: dict[str, Any] = {
        "article_id": article_id,
        "task_id": task_id,
        "task_family": prompt.task_family,
        "variant": prompt.variant,
        "raw_response": None,
        "parsed_output": None,
        "resolved_output": None,
        "valid": False,
        "validation_errors": [],
        "api_error": None,
        "parse_error": None,
        "prompt_hash": None,
        "input_tokens": None,
        "output_tokens": None,
    }

    try:
        render_kwargs: dict[str, str] = {}
        if target:
            render_kwargs["target"] = target
        if target_type:
            render_kwargs["target_type"] = target_type
        user_prompt = loader.render_user_prompt(task_id, article, **render_kwargs)
        response = client.chat(prompt.system_prompt, user_prompt)
        result["raw_response"] = response.raw_response
        result["prompt_hash"] = response.prompt_hash
        result["input_tokens"] = response.input_tokens
        result["output_tokens"] = response.output_tokens
    except Exception as exc:  # noqa: BLE001
        message = f"{type(exc).__name__}: {exc}"
        result["api_error"] = message
        result["validation_errors"] = [message]
        print(f"[ERROR] {article_id} | {task_id} | API call failed: {message}")
        return result

    try:
        parsed = parse_json_object(str(result["raw_response"]), context=f"task {task_id!r}")
        result["parsed_output"] = parsed
    except Exception as exc:  # noqa: BLE001
        message = f"{type(exc).__name__}: {exc}"
        result["parse_error"] = message
        result["validation_errors"] = [message]
        print(f"[ERROR] {article_id} | {task_id} | JSON parse failed: {message}")
        return result

    resolved = loader.resolve_slots(task_id, result["parsed_output"])
    result["resolved_output"] = resolved

    errors = loader.validate_output(task_id, result["parsed_output"])
    result["validation_errors"] = errors
    result["valid"] = not errors
    if errors:
        print(f"[WARN] {article_id} | {task_id} | Validation failed: {'; '.join(errors)}")

    return result


def print_summary_table(results: list[dict[str, Any]]) -> None:
    rows: list[list[str]] = []
    for result in results:
        display_payload = result["resolved_output"] or result["parsed_output"]
        rows.append(
            [
                str(result["article_id"]),
                str(result["task_id"]),
                "yes" if result["valid"] else "no",
                json_preview(display_payload, limit=80),
                truncate("; ".join(result["validation_errors"]), 160),
            ]
        )

    headers = [
        "article_id",
        "task_id",
        "valid",
        "parsed_output",
        "validation_errors",
    ]
    widths = [
        max(len(headers[idx]), *(len(row[idx]) for row in rows))
        for idx in range(len(headers))
    ]

    def render_row(values: list[str]) -> str:
        return " | ".join(value.ljust(widths[idx]) for idx, value in enumerate(values))

    separator = "-+-".join("-" * width for width in widths)
    print("\nSmoke test summary")
    print(render_row(headers))
    print(separator)
    for row in rows:
        print(render_row(row))


def save_results(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def flip_direction(label: str) -> str:
    mapping = {"up": "down", "down": "up"}
    if label not in mapping:
        raise ValueError(f"semantic_reversal requires up/down, got {label!r}")
    return mapping[label]


def shorten_span_value(value: str, max_length: int = 80) -> str:
    if len(value) <= max_length:
        return value
    if max_length <= 3:
        return value[:max_length]
    return value[: max_length - 3] + "..."


def repaired_counterfactual_payload(
    loader: PromptLoader,
    template_id: str,
    payload: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    repaired = deepcopy(payload)
    for span in repaired.get("changed_spans", []):
        if not isinstance(span, dict):
            continue
        for key in ("from", "to"):
            value = span.get(key)
            if isinstance(value, str):
                span[key] = shorten_span_value(value, max_length=80)

    template = loader.get_counterfactual_template(template_id)
    errors = list(loader._validator.validate_schema(template.output_schema, repaired))
    return repaired, errors


def generate_counterfactual_with_repair(
    client: LLMClient,
    loader: PromptLoader,
    template_id: str,
    article: str,
    bypass_cache: bool = False,
    **kwargs: Any,
) -> tuple[dict[str, Any], bool]:
    template = loader.get_counterfactual_template(template_id)
    user_prompt = loader.render_cf_prompt(template_id, article, **kwargs)
    response = client.chat(template.system_prompt, user_prompt, bypass_cache=bypass_cache)
    parsed = parse_json_object(
        response.raw_response,
        context=f"counterfactual template {template_id!r}",
    )
    errors = list(loader._validator.validate_schema(template.output_schema, parsed))
    if not errors:
        return parsed, False

    only_changed_span_length_errors = all(
        error.startswith("root.changed_spans")
        and "expected length <= 80" in error
        for error in errors
    )
    if not only_changed_span_length_errors:
        raise ValueError(
            f"LLM output failed validation for counterfactual template {template_id!r}: "
            + "; ".join(errors)
        )

    repaired, repaired_errors = repaired_counterfactual_payload(
        loader=loader,
        template_id=template_id,
        payload=parsed,
    )
    if repaired_errors:
        raise ValueError(
            f"Counterfactual repair failed for template {template_id!r}: "
            + "; ".join(repaired_errors)
        )
    return repaired, True


def generate_counterfactual_template_safe(
    client: LLMClient,
    loader: PromptLoader,
    template_id: str,
    article: str,
    max_attempts: int = 3,
    **kwargs: Any,
) -> tuple[dict[str, Any] | None, list[str], bool]:
    errors: list[str] = []
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
            return payload, errors, False
        except Exception as exc:  # noqa: BLE001
            message = f"attempt {attempt}: {type(exc).__name__}: {exc}"
            errors.append(message)
            print(f"[WARN] counterfactual {template_id} | {message}")
            try:
                payload, repaired = generate_counterfactual_with_repair(
                    client=client,
                    loader=loader,
                    template_id=template_id,
                    article=article,
                    bypass_cache=True,
                    **kwargs,
                )
                if repaired:
                    repair_message = (
                        f"attempt {attempt}: repaired overlong changed_spans "
                        f"for {template_id}"
                    )
                    errors.append(repair_message)
                    print(f"[WARN] counterfactual {template_id} | {repair_message}")
                return payload, errors, repaired
            except Exception as repair_exc:  # noqa: BLE001
                repair_message = (
                    f"attempt {attempt}: repair failed: "
                    f"{type(repair_exc).__name__}: {repair_exc}"
                )
                errors.append(repair_message)
                print(f"[WARN] counterfactual {template_id} | {repair_message}")
    return None, errors, False


def run_counterfactual_check(
    client: LLMClient,
    loader: PromptLoader,
    test_case: Any,
) -> dict[str, Any]:
    task_id = "direct_prediction.base"
    original_label = str(
        getattr(test_case.expected_direction, "value", test_case.expected_direction)
    )
    if original_label == "neutral":
        raise ValueError(
            f"Counterfactual smoke test needs a non-neutral seed label, got {test_case.id}"
        )
    target_label = flip_direction(original_label)
    original_article = article_text(test_case)

    print(
        f"\nCounterfactual smoke test: {test_case.id} | {task_id} | "
        f"{original_label} -> {target_label}"
    )

    target = getattr(test_case, "target", "")
    target_type = getattr(test_case, "target_type", "")

    semantic_reversal, semantic_errors, semantic_repaired = generate_counterfactual_template_safe(
        client=client,
        loader=loader,
        template_id="semantic_reversal",
        article=original_article,
        original_label=original_label,
        target_label=target_label,
        target_field="direction",
        target=target,
        target_type=target_type,
    )
    neutral_paraphrase, paraphrase_errors, paraphrase_repaired = generate_counterfactual_template_safe(
        client=client,
        loader=loader,
        template_id="neutral_paraphrase",
        article=original_article,
        target=target,
        target_type=target_type,
    )

    if semantic_reversal is None or neutral_paraphrase is None:
        print("Excess invariance: unavailable")
        return {
            "article_id": test_case.id,
            "news_id": test_case.news.id,
            "task_id": task_id,
            "original_label": original_label,
            "target_label": target_label,
            "semantic_reversal": semantic_reversal,
            "neutral_paraphrase": neutral_paraphrase,
            "semantic_reversal_errors": semantic_errors,
            "neutral_paraphrase_errors": paraphrase_errors,
            "semantic_reversal_repaired": semantic_repaired,
            "neutral_paraphrase_repaired": paraphrase_repaired,
            "original_task_result": None,
            "reversed_task_result": None,
            "paraphrase_task_result": None,
            "excess_invariance": None,
        }

    original_result = run_task_safe(
        client=client,
        loader=loader,
        task_id=task_id,
        article=original_article,
        article_id=test_case.id,
        target=target,
        target_type=target_type,
    )
    reversed_result = run_task_safe(
        client=client,
        loader=loader,
        task_id=task_id,
        article=str(semantic_reversal["rewritten_article"]),
        article_id=f"{test_case.id}:semantic_reversal",
        target=target,
        target_type=target_type,
    )
    paraphrase_result = run_task_safe(
        client=client,
        loader=loader,
        task_id=task_id,
        article=str(neutral_paraphrase["rewritten_article"]),
        article_id=f"{test_case.id}:neutral_paraphrase",
        target=target,
        target_type=target_type,
    )

    original_payload = original_result["resolved_output"] or original_result["parsed_output"]
    reversed_payload = reversed_result["resolved_output"] or reversed_result["parsed_output"]
    paraphrase_payload = (
        paraphrase_result["resolved_output"] or paraphrase_result["parsed_output"]
    )

    invariance_value: float | None = None
    if all(
        isinstance(payload, dict)
        for payload in (original_payload, reversed_payload, paraphrase_payload)
    ):
        invariance_value = excess_invariance(
            orig_response=original_payload,
            cf_response=reversed_payload,
            para_response=paraphrase_payload,
        )

    print(f"Original output:   {json_preview(original_payload, limit=120)}")
    print(f"Reversed output:   {json_preview(reversed_payload, limit=120)}")
    print(f"Paraphrase output: {json_preview(paraphrase_payload, limit=120)}")
    if invariance_value is None:
        print("Excess invariance: unavailable")
    else:
        print(f"Excess invariance: {invariance_value:.4f}")

    return {
        "article_id": test_case.id,
        "news_id": test_case.news.id,
        "task_id": task_id,
        "original_label": original_label,
        "target_label": target_label,
        "semantic_reversal": semantic_reversal,
        "neutral_paraphrase": neutral_paraphrase,
        "semantic_reversal_errors": semantic_errors,
        "neutral_paraphrase_errors": paraphrase_errors,
        "semantic_reversal_repaired": semantic_repaired,
        "neutral_paraphrase_repaired": paraphrase_repaired,
        "original_task_result": original_result,
        "reversed_task_result": reversed_result,
        "paraphrase_task_result": paraphrase_result,
        "excess_invariance": invariance_value,
    }


def main() -> int:
    settings = load_yaml(SETTINGS_PATH)
    env_values = load_env_file(ENV_PATH)
    loader = PromptLoader(prompts_dir=str(PROMPTS_DIR))
    client, client_metadata = build_client(settings=settings, env_values=env_values)

    try:
        all_test_cases = load_test_cases(TEST_CASES_PATH)
        selected_cases = select_diverse_articles(all_test_cases, limit=3)

        print("Selected articles")
        for test_case in selected_cases:
            category = str(getattr(test_case.news.category, "value", test_case.news.category))
            direction = str(
                getattr(test_case.expected_direction, "value", test_case.expected_direction)
            )
            print(f"- {test_case.id} | {category} | {direction} | {test_case.news.title}")

        results_payload: dict[str, Any] = {
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "settings_path": str(SETTINGS_PATH.relative_to(ROOT)),
            "env_path": str(ENV_PATH.relative_to(ROOT)),
            "test_cases_path": str(TEST_CASES_PATH.relative_to(ROOT)),
            "results_path": str(RESULTS_PATH.relative_to(ROOT)),
            "client": client_metadata,
            "task_ids": TASK_IDS,
            "selected_articles": [
                {
                    "article_id": test_case.id,
                    "news_id": test_case.news.id,
                    "title": test_case.news.title,
                    "category": str(
                        getattr(test_case.news.category, "value", test_case.news.category)
                    ),
                    "expected_direction": str(
                        getattr(
                            test_case.expected_direction,
                            "value",
                            test_case.expected_direction,
                        )
                    ),
                    "memorization_likelihood": test_case.memorization_likelihood,
                }
                for test_case in selected_cases
            ],
            "results": [],
            "counterfactual_check": None,
        }

        for test_case in selected_cases:
            current_article = article_text(test_case)
            for task_id in TASK_IDS:
                task_result = run_task_safe(
                    client=client,
                    loader=loader,
                    task_id=task_id,
                    article=current_article,
                    article_id=test_case.id,
                    target=getattr(test_case, "target", ""),
                    target_type=getattr(test_case, "target_type", ""),
                )
                task_result.update(
                    {
                        "news_id": test_case.news.id,
                        "title": test_case.news.title,
                        "category": str(
                            getattr(test_case.news.category, "value", test_case.news.category)
                        ),
                    }
                )
                results_payload["results"].append(task_result)

        print_summary_table(results_payload["results"])
        save_results(RESULTS_PATH, results_payload)

        cf_case = next(
            (
                test_case
                for test_case in selected_cases
                if str(
                    getattr(
                        test_case.expected_direction,
                        "value",
                        test_case.expected_direction,
                    )
                )
                in {"up", "down"}
            ),
            selected_cases[0],
        )
        results_payload["counterfactual_check"] = run_counterfactual_check(
            client=client,
            loader=loader,
            test_case=cf_case,
        )

        save_results(RESULTS_PATH, results_payload)
        print(f"\nSaved full results to {RESULTS_PATH}")
        return 0
    finally:
        client._client.close()


if __name__ == "__main__":
    raise SystemExit(main())
