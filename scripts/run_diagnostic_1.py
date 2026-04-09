"""Run Diagnostic 1: QA memorization probes + verbatim completion probes."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.llm_client import LLMClient
from src.masking import extract_json_robust
from src.prompts import memorization_probe_prompt

SETTINGS_PATH = ROOT / "config" / "settings.yaml"
ENV_PATH = ROOT / ".env"
DEFAULT_PROBES_PATH = ROOT / "data" / "seed" / "memorization_probes.json"
DEFAULT_CASES_PATH = ROOT / "data" / "seed" / "test_cases_expanded.json"
DEFAULT_OUTPUT_PATH = ROOT / "data" / "results" / "diagnostic_1_results.json"
DEFAULT_MAX_CONCURRENCY = 20
PREFIX_LENGTH = 80
EXACT_MATCH_WINDOW = 100

COMPLETION_SYSTEM = (
    "你是一个新闻续写助手。请根据开头直接续写，不要添加任何解释或评论。"
)
COMPLETION_USER_TEMPLATE = "请续写以下新闻文本的后续内容：\n\n{prefix}"

JUDGE_SYSTEM = (
    "你是一个严格的问答评分裁判。"
    "请根据问题、模型回答、标准答案和容差进行评分。"
    "评分只能是 1.0、0.5 或 0.0。"
    "只输出 JSON：{\"score\": 1.0|0.5|0.0, \"reason\": \"...\"}"
)


def load_json(path: Path) -> Any:
    """Load JSON from disk."""
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    tmp_path.replace(path)


def mean(values: list[float]) -> float:
    """Return the arithmetic mean, or 0.0 for empty input."""
    return sum(values) / len(values) if values else 0.0


def parse_json_object(text: str) -> dict[str, Any] | None:
    """Parse a JSON object, tolerating prose or code fences around it."""
    raw = text.strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = extract_json_robust(raw)

    if not isinstance(parsed, dict):
        return None
    return parsed


def coerce_float(value: Any) -> float | None:
    """Coerce a value into a float when possible."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = re.search(r"-?\d+(?:\.\d+)?", value)
        if match:
            return float(match.group(0))
    return None


def normalize_score(value: Any) -> float:
    """Map a judge score to the allowed set {0.0, 0.5, 1.0}."""
    score = coerce_float(value)
    if score is None:
        return 0.0
    return min((0.0, 0.5, 1.0), key=lambda candidate: abs(candidate - score))


def configure_no_proxy(base_url: str) -> None:
    """Ensure the DeepSeek host bypasses any local proxy settings."""
    host = urlparse(base_url).hostname or ""
    existing = []
    for key in ("NO_PROXY", "no_proxy"):
        existing.extend(
            item.strip()
            for item in os.getenv(key, "").split(",")
            if item.strip()
        )

    merged: list[str] = []
    for item in [*existing, "localhost", "127.0.0.1", host]:
        if item and item not in merged:
            merged.append(item)

    os.environ["NO_PROXY"] = ",".join(merged)
    os.environ["no_proxy"] = os.environ["NO_PROXY"]


def build_client() -> LLMClient:
    """Build an LLMClient from config/settings.yaml and .env."""
    load_dotenv(ENV_PATH)
    settings = yaml.safe_load(SETTINGS_PATH.read_text(encoding="utf-8")) or {}
    llm_config = settings.get("llm", {})

    base_url = (
        os.getenv("DEEPSEEK_BASE_URL")
        or os.getenv("DEEPSEEK_API_BASE")
        or str(llm_config.get("base_url", "https://api.deepseek.com/v1"))
    )
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(f"DEEPSEEK_API_KEY not found in {ENV_PATH} or environment")

    configure_no_proxy(base_url)

    client = LLMClient(
        base_url=base_url,
        model=str(llm_config.get("model", "deepseek-chat")),
        temperature=float(llm_config.get("temperature", 0.0)),
        max_tokens=int(llm_config.get("max_tokens", 2048)),
        api_key=api_key,
        enable_cache=bool(settings.get("experiment", {}).get("cache_results", True)),
    )
    client._client.close()
    client._client = httpx.Client(timeout=120.0, proxy=None, trust_env=False)
    return client


def load_qa_probes(path: Path) -> list[dict[str, Any]]:
    """Load memorization probes from JSON."""
    raw = load_json(path)
    if isinstance(raw, dict):
        probes = raw.get("probes", [])
    else:
        probes = raw
    if not isinstance(probes, list):
        raise ValueError(f"Unexpected QA probe payload in {path}")
    return probes


def load_test_cases(path: Path) -> list[dict[str, Any]]:
    """Load expanded test cases from JSON."""
    raw = load_json(path)
    if isinstance(raw, dict):
        cases = raw.get("test_cases", [])
    else:
        cases = raw
    if not isinstance(cases, list):
        raise ValueError(f"Unexpected test-case payload in {path}")
    return cases


def parse_probe_response(raw_response: str) -> tuple[str, float | None]:
    """Parse the QA probe response JSON."""
    parsed = parse_json_object(raw_response)
    if parsed is None:
        return raw_response.strip(), None

    answer = str(parsed.get("answer", "")).strip()
    if not answer:
        answer = raw_response.strip()

    confidence = coerce_float(parsed.get("confidence"))
    if confidence is not None:
        confidence = max(0.0, min(100.0, confidence))
    return answer, confidence


def build_judge_prompt(
    question: str,
    model_answer: str,
    ground_truth: str,
    tolerance: str,
) -> tuple[str, str]:
    """Build the LLM-as-judge prompt for QA scoring."""
    tolerance_text = tolerance.strip() or "无明确容差"
    user = (
        f"问题：{question}\n"
        f"模型回答：{model_answer}\n"
        f"标准答案：{ground_truth}\n"
        f"容差：{tolerance_text}\n\n"
        "评分规则：\n"
        "1. 完全正确或在容差范围内，记 1.0。\n"
        "2. 部分正确、方向正确但明显不精确，记 0.5。\n"
        "3. 错误、无关、回避作答或与标准答案明显冲突，记 0.0。\n\n"
        "输出 JSON：{\"score\": 1.0|0.5|0.0, \"reason\": \"...\"}"
    )
    return JUDGE_SYSTEM, user


def parse_judge_response(raw_response: str) -> tuple[float, str]:
    """Parse the judge JSON output."""
    parsed = parse_json_object(raw_response)
    if parsed is None:
        return 0.0, "Failed to parse judge response as JSON."
    score = normalize_score(parsed.get("score"))
    reason = str(parsed.get("reason", "")).strip()
    return score, reason


def run_qa_probes(
    client: LLMClient,
    probes: list[dict[str, Any]],
    max_concurrency: int,
    bypass_cache: bool = False,
) -> dict[str, Any]:
    """Run QA memorization probes and judge them."""
    probe_prompts = [memorization_probe_prompt(str(probe["question"])) for probe in probes]
    probe_responses = client.batch_chat_concurrent(
        probe_prompts,
        max_concurrency=max_concurrency,
        bypass_cache=bypass_cache,
    )

    parsed_answers: list[dict[str, Any]] = []
    judge_prompts: list[tuple[str, str]] = []
    for probe, response in zip(probes, probe_responses):
        model_answer, confidence = parse_probe_response(response.raw_response)
        parsed_answers.append(
            {
                "probe_id": str(probe["id"]),
                "probe_type": str(probe["probe_type"]),
                "question": str(probe["question"]),
                "model_answer": model_answer,
                "ground_truth": str(probe["ground_truth"]),
                "confidence": confidence,
                "tolerance": str(probe.get("tolerance", "")),
            }
        )
        judge_prompts.append(
            build_judge_prompt(
                question=str(probe["question"]),
                model_answer=model_answer,
                ground_truth=str(probe["ground_truth"]),
                tolerance=str(probe.get("tolerance", "")),
            )
        )

    judge_responses = client.batch_chat_concurrent(
        judge_prompts,
        max_concurrency=max_concurrency,
        bypass_cache=bypass_cache,
    )

    details: list[dict[str, Any]] = []
    scores_by_type: dict[str, list[float]] = defaultdict(list)
    all_scores: list[float] = []

    for parsed_answer, judge_response in zip(parsed_answers, judge_responses):
        score, judge_reason = parse_judge_response(judge_response.raw_response)
        detail = {
            "probe_id": parsed_answer["probe_id"],
            "probe_type": parsed_answer["probe_type"],
            "question": parsed_answer["question"],
            "model_answer": parsed_answer["model_answer"],
            "ground_truth": parsed_answer["ground_truth"],
            "score": score,
            "confidence": parsed_answer["confidence"],
            "judge_reason": judge_reason,
        }
        details.append(detail)
        scores_by_type[parsed_answer["probe_type"]].append(score)
        all_scores.append(score)

    return {
        "overall_score": mean(all_scores),
        "by_probe_type": {
            probe_type: mean(type_scores)
            for probe_type, type_scores in sorted(scores_by_type.items())
        },
        "details": details,
    }


def lcs_length(left: str, right: str) -> int:
    """Compute the longest common subsequence length."""
    if not left or not right:
        return 0

    if len(right) > len(left):
        left, right = right, left

    previous = [0] * (len(right) + 1)
    for left_char in left:
        current = [0]
        for index, right_char in enumerate(right, start=1):
            if left_char == right_char:
                current.append(previous[index - 1] + 1)
            else:
                current.append(max(previous[index], current[-1]))
        previous = current
    return previous[-1]


def rouge_l_score(prediction: str, reference: str) -> float:
    """Compute a simple ROUGE-L F1 score based on character-level LCS."""
    if not prediction or not reference:
        return 0.0

    lcs = lcs_length(prediction, reference)
    precision = lcs / len(prediction)
    recall = lcs / len(reference)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def exact_match_ratio(
    prediction: str,
    reference: str,
    window: int = EXACT_MATCH_WINDOW,
) -> float:
    """Compute position-wise exact-match ratio over the first N characters."""
    compare_len = min(window, len(reference))
    if compare_len == 0:
        return 0.0

    matches = 0
    for index in range(compare_len):
        if index < len(prediction) and prediction[index] == reference[index]:
            matches += 1
    return matches / compare_len


def build_completion_prompt(prefix: str) -> tuple[str, str]:
    """Build the verbatim completion prompt."""
    return COMPLETION_SYSTEM, COMPLETION_USER_TEMPLATE.format(prefix=prefix)


def run_verbatim_completion(
    client: LLMClient,
    test_cases: list[dict[str, Any]],
    max_concurrency: int,
    bypass_cache: bool = False,
) -> dict[str, Any]:
    """Run verbatim completion probes and compute similarity scores."""
    completion_inputs: list[dict[str, Any]] = []
    prompts: list[tuple[str, str]] = []

    for case in test_cases:
        news = case.get("news", {})
        content = str(news.get("content", "")).strip()
        prefix = content[:PREFIX_LENGTH]
        actual_continuation = content[PREFIX_LENGTH:]
        rarity = str(case.get("rarity_estimate") or case.get("rarity") or "unknown")
        completion_inputs.append(
            {
                "case_id": str(case["id"]),
                "prefix": prefix,
                "actual_continuation": actual_continuation,
                "period": str(case.get("period", "unknown")),
                "rarity": rarity,
            }
        )
        prompts.append(build_completion_prompt(prefix))

    completion_responses = client.batch_chat_concurrent(
        prompts,
        max_concurrency=max_concurrency,
        bypass_cache=bypass_cache,
    )

    details: list[dict[str, Any]] = []
    rouge_by_period: dict[str, list[float]] = defaultdict(list)
    rouge_by_rarity: dict[str, list[float]] = defaultdict(list)
    overall_rouges: list[float] = []

    for case_input, response in zip(completion_inputs, completion_responses):
        model_completion = response.raw_response.strip()
        actual_continuation = case_input["actual_continuation"]
        rouge_l = rouge_l_score(model_completion, actual_continuation)
        exact_ratio = exact_match_ratio(model_completion, actual_continuation)

        detail = {
            "case_id": case_input["case_id"],
            "prefix": case_input["prefix"],
            "model_completion": model_completion,
            "actual_continuation": actual_continuation,
            "rouge_l": rouge_l,
            "exact_match_ratio": exact_ratio,
            "period": case_input["period"],
            "rarity": case_input["rarity"],
        }
        details.append(detail)
        rouge_by_period[case_input["period"]].append(rouge_l)
        rouge_by_rarity[case_input["rarity"]].append(rouge_l)
        overall_rouges.append(rouge_l)

    by_period = {
        key: mean(rouge_by_period.get(key, []))
        for key in ("pre_cutoff", "post_cutoff")
    }
    by_rarity = {
        key: mean(rouge_by_rarity.get(key, []))
        for key in ("rare", "medium", "common")
    }

    return {
        "overall_rouge_l": mean(overall_rouges),
        "by_period": by_period,
        "by_rarity": by_rarity,
        "details": details,
    }


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Run Diagnostic 1: QA memorization + verbatim completion probes.",
    )
    parser.add_argument(
        "--probes",
        type=Path,
        default=DEFAULT_PROBES_PATH,
        help="Path to memorization_probes.json",
    )
    parser.add_argument(
        "--cases",
        type=Path,
        default=DEFAULT_CASES_PATH,
        help="Path to test_cases_expanded.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Where to save diagnostic results",
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=DEFAULT_MAX_CONCURRENCY,
        help="Max concurrent API requests (default: 20)",
    )
    parser.add_argument(
        "--bypass-cache",
        action="store_true",
        help="Skip cache lookups and force fresh API calls",
    )
    return parser.parse_args()


def main() -> int:
    """Run both parts of Diagnostic 1 and save results."""
    args = parse_args()
    max_concurrency = max(1, min(args.max_concurrency, DEFAULT_MAX_CONCURRENCY))

    probes = load_qa_probes(args.probes)
    test_cases = load_test_cases(args.cases)

    print(f"Loaded {len(probes)} QA probes from {args.probes}")
    print(f"Loaded {len(test_cases)} completion cases from {args.cases}")
    print(f"Using max concurrency = {max_concurrency}")

    client = build_client()
    try:
        print("Running QA memorization probes...")
        qa_results = run_qa_probes(
            client=client,
            probes=probes,
            max_concurrency=max_concurrency,
            bypass_cache=args.bypass_cache,
        )
        print(
            f"QA probes complete. Overall score = {qa_results['overall_score']:.4f}"
        )

        print("Running verbatim completion probes...")
        completion_results = run_verbatim_completion(
            client=client,
            test_cases=test_cases,
            max_concurrency=max_concurrency,
            bypass_cache=args.bypass_cache,
        )
        print(
            "Verbatim completion complete. "
            f"Overall ROUGE-L = {completion_results['overall_rouge_l']:.4f}"
        )

        payload = {
            "qa_probes": qa_results,
            "verbatim_completion": completion_results,
        }
        atomic_write_json(args.output, payload)
        print(f"Results saved to {args.output}")
        return 0
    finally:
        client._client.close()


if __name__ == "__main__":
    raise SystemExit(main())
