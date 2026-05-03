"""Minimal black-box provider slug smoke.

This script is intentionally tiny and explicit: it sends one low-token
request per black-box fleet member to prove that authentication, routing,
and model slugs are live before a real pilot run. It does not touch
white-box/HF downloads, GPU, cache, or runstate.

DeepSeek is always checked against the official DeepSeek API. OpenAI and
Anthropic use official provider keys when present; otherwise they fall
back to OpenRouter when `OPENROUTER_API_KEY` is available.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import httpx
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.r5a.fleet import FleetConfig, ModelConfig, load_fleet  # noqa: E402


OPENROUTER_MODEL_IDS = {
    "gpt-4.1": "openai/gpt-4.1",
    "gpt-5.1": "openai/gpt-5.1",
    "claude-sonnet-4.6": "anthropic/claude-sonnet-4.6",
}


@dataclass(frozen=True)
class ProbePlan:
    model_id: str
    provider: str
    route: str
    route_model: str
    env_var: str


@dataclass(frozen=True)
class ProbeResult:
    plan: ProbePlan
    ok: bool
    status_code: int | None
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke black-box provider slugs")
    parser.add_argument(
        "--fleet",
        default="config/fleet/r5a_fleet.yaml",
        help="fleet YAML path",
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="dotenv file with provider API keys",
    )
    parser.add_argument(
        "--model",
        action="append",
        dest="models",
        help="limit to a fleet model id; repeatable",
    )
    parser.add_argument(
        "--catalog-only",
        action="store_true",
        help="check route catalogs only; do not call completions/messages",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=16,
        help=(
            "completion token cap for each probe; 16 is the lowest value "
            "accepted by OpenRouter's OpenAI/Azure route"
        ),
    )
    parser.add_argument(
        "--timeout-s",
        type=float,
        default=60.0,
        help="HTTP timeout in seconds",
    )
    return parser.parse_args()


def load_env(path: str | Path) -> dict[str, str]:
    env_path = Path(path)
    if env_path.exists():
        load_dotenv(env_path, override=False)
    return dict(os.environ)


def build_probe_plan(
    fleet: FleetConfig,
    env: Mapping[str, str],
    selected_models: set[str] | None = None,
) -> list[ProbePlan]:
    plans: list[ProbePlan] = []
    for model_id in fleet.black_box_ids():
        if selected_models is not None and model_id not in selected_models:
            continue
        model = fleet.get(model_id)
        plans.append(_plan_for_model(model_id, model, env))
    return plans


def _plan_for_model(
    model_id: str,
    model: ModelConfig,
    env: Mapping[str, str],
) -> ProbePlan:
    if not model.api_model_name:
        raise ValueError(f"{model_id}: missing api_model_name")

    if model.provider == "deepseek":
        return ProbePlan(
            model_id=model_id,
            provider=model.provider,
            route="deepseek_official",
            route_model=model.api_model_name,
            env_var="DEEPSEEK_API_KEY",
        )

    if model.provider == "openai":
        if env.get("OPENAI_API_KEY"):
            return ProbePlan(
                model_id=model_id,
                provider=model.provider,
                route="openai_official",
                route_model=model.api_model_name,
                env_var="OPENAI_API_KEY",
            )
        return _openrouter_plan(model_id, model)

    if model.provider == "anthropic":
        if env.get("ANTHROPIC_API_KEY"):
            return ProbePlan(
                model_id=model_id,
                provider=model.provider,
                route="anthropic_official",
                route_model=model.api_model_name,
                env_var="ANTHROPIC_API_KEY",
            )
        return _openrouter_plan(model_id, model)

    raise ValueError(f"{model_id}: unsupported provider {model.provider!r}")


def _openrouter_plan(model_id: str, model: ModelConfig) -> ProbePlan:
    if model_id not in OPENROUTER_MODEL_IDS:
        raise ValueError(
            f"{model_id}: no OpenRouter fallback mapping for provider "
            f"{model.provider!r}"
        )
    return ProbePlan(
        model_id=model_id,
        provider=model.provider,
        route="openrouter",
        route_model=OPENROUTER_MODEL_IDS[model_id],
        env_var="OPENROUTER_API_KEY",
    )


def catalog_check(
    client: httpx.Client,
    plans: list[ProbePlan],
    env: Mapping[str, str],
) -> list[ProbeResult]:
    results: list[ProbeResult] = []

    deepseek_plans = [p for p in plans if p.route == "deepseek_official"]
    if deepseek_plans:
        results.extend(_deepseek_catalog_check(client, deepseek_plans, env))

    openrouter_plans = [p for p in plans if p.route == "openrouter"]
    if openrouter_plans:
        results.extend(_openrouter_catalog_check(client, openrouter_plans, env))

    official_without_catalog = [
        p for p in plans if p.route in {"openai_official", "anthropic_official"}
    ]
    for plan in official_without_catalog:
        results.append(ProbeResult(plan, True, None, "no catalog precheck"))

    return results


def completion_check(
    client: httpx.Client,
    plans: list[ProbePlan],
    env: Mapping[str, str],
    max_tokens: int,
) -> list[ProbeResult]:
    results: list[ProbeResult] = []
    for plan in plans:
        if not env.get(plan.env_var):
            results.append(
                ProbeResult(
                    plan,
                    False,
                    None,
                    f"missing env var {plan.env_var}",
                )
            )
            continue
        if plan.route == "deepseek_official":
            results.append(_openai_compatible_completion(client, plan, env, max_tokens))
        elif plan.route == "openai_official":
            results.append(_openai_official_completion(client, plan, env, max_tokens))
        elif plan.route == "anthropic_official":
            results.append(_anthropic_official_completion(client, plan, env, max_tokens))
        elif plan.route == "openrouter":
            results.append(_openrouter_completion(client, plan, env, max_tokens))
        else:
            results.append(ProbeResult(plan, False, None, f"unknown route {plan.route}"))
    return results


def _deepseek_catalog_check(
    client: httpx.Client,
    plans: list[ProbePlan],
    env: Mapping[str, str],
) -> list[ProbeResult]:
    api_key = env.get("DEEPSEEK_API_KEY")
    if not api_key:
        return [
            ProbeResult(plan, False, None, "missing env var DEEPSEEK_API_KEY")
            for plan in plans
        ]
    headers = {"Authorization": f"Bearer {api_key}"}
    response = client.get("https://api.deepseek.com/v1/models", headers=headers)
    body = _body_snippet(response)
    if response.status_code != 200:
        return [
            ProbeResult(plan, False, response.status_code, body)
            for plan in plans
        ]
    ids = {item.get("id") for item in response.json().get("data", [])}
    results = []
    for plan in plans:
        ok = plan.route_model in ids
        detail = "catalog contains model" if ok else f"catalog missing {plan.route_model}"
        results.append(ProbeResult(plan, ok, response.status_code, detail))
    return results


def _openrouter_catalog_check(
    client: httpx.Client,
    plans: list[ProbePlan],
    env: Mapping[str, str],
) -> list[ProbeResult]:
    headers = {}
    if env.get("OPENROUTER_API_KEY"):
        headers["Authorization"] = f"Bearer {env['OPENROUTER_API_KEY']}"
    response = client.get("https://openrouter.ai/api/v1/models", headers=headers)
    body = _body_snippet(response)
    if response.status_code != 200:
        return [
            ProbeResult(plan, False, response.status_code, body)
            for plan in plans
        ]
    ids = {item.get("id") for item in response.json().get("data", [])}
    results = []
    for plan in plans:
        ok = plan.route_model in ids
        detail = "catalog contains model" if ok else f"catalog missing {plan.route_model}"
        results.append(ProbeResult(plan, ok, response.status_code, detail))
    return results


def _openai_compatible_completion(
    client: httpx.Client,
    plan: ProbePlan,
    env: Mapping[str, str],
    max_tokens: int,
) -> ProbeResult:
    headers = {"Authorization": f"Bearer {env[plan.env_var]}"}
    response = client.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers=headers,
        json=_chat_payload(plan.route_model, max_tokens),
    )
    return _completion_result(plan, response)


def _openai_official_completion(
    client: httpx.Client,
    plan: ProbePlan,
    env: Mapping[str, str],
    max_tokens: int,
) -> ProbeResult:
    headers = {"Authorization": f"Bearer {env[plan.env_var]}"}
    response = client.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=_chat_payload(plan.route_model, max_tokens),
    )
    return _completion_result(plan, response)


def _anthropic_official_completion(
    client: httpx.Client,
    plan: ProbePlan,
    env: Mapping[str, str],
    max_tokens: int,
) -> ProbeResult:
    headers = {
        "x-api-key": env[plan.env_var],
        "anthropic-version": "2023-06-01",
    }
    response = client.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json={
            "model": plan.route_model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": "Reply with OK."}],
        },
    )
    return _completion_result(plan, response)


def _openrouter_completion(
    client: httpx.Client,
    plan: ProbePlan,
    env: Mapping[str, str],
    max_tokens: int,
) -> ProbeResult:
    headers = {
        "Authorization": f"Bearer {env[plan.env_var]}",
        "HTTP-Referer": "https://local.invalid/llm-leakage-test",
        "X-Title": "LLM-Leakage-Test provider smoke",
    }
    response = client.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=_chat_payload(plan.route_model, max_tokens),
    )
    return _completion_result(plan, response)


def _chat_payload(model: str, max_tokens: int) -> dict[str, object]:
    return {
        "model": model,
        "messages": [{"role": "user", "content": "Reply with OK."}],
        "max_tokens": max_tokens,
        "stream": False,
    }


def _completion_result(plan: ProbePlan, response: httpx.Response) -> ProbeResult:
    if 200 <= response.status_code < 300:
        return ProbeResult(plan, True, response.status_code, "completion accepted")
    return ProbeResult(plan, False, response.status_code, _body_snippet(response))


def _body_snippet(response: httpx.Response, limit: int = 500) -> str:
    text = response.text.replace("\n", " ").strip()
    return text[:limit] if text else "<empty response>"


def print_plan(plans: list[ProbePlan]) -> None:
    print("== route plan ==")
    for plan in plans:
        print(
            f"{plan.model_id}: provider={plan.provider} route={plan.route} "
            f"model={plan.route_model} key={plan.env_var}"
        )


def print_results(title: str, results: list[ProbeResult]) -> None:
    print(f"\n== {title} ==")
    for result in results:
        marker = "OK" if result.ok else "FAIL"
        status = f" HTTP {result.status_code}" if result.status_code is not None else ""
        print(
            f"[{marker}] {result.plan.model_id} via {result.plan.route}"
            f" ({result.plan.route_model}){status}: {result.detail}"
        )


def main() -> int:
    args = parse_args()
    env = load_env(args.env_file)
    fleet = load_fleet(args.fleet)
    selected = set(args.models) if args.models else None
    plans = build_probe_plan(fleet, env, selected)
    if not plans:
        print("no black-box models selected", file=sys.stderr)
        return 2

    print_plan(plans)
    with httpx.Client(timeout=args.timeout_s, trust_env=False) as client:
        catalog_results = catalog_check(client, plans, env)
        print_results("catalog checks", catalog_results)
        if not all(result.ok for result in catalog_results):
            return 1
        if args.catalog_only:
            return 0
        completion_results = completion_check(client, plans, env, args.max_tokens)
        print_results("completion checks", completion_results)
        return 0 if all(result.ok for result in completion_results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
