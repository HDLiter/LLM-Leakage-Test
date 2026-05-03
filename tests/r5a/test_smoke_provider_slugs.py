from __future__ import annotations

from scripts.smoke_provider_slugs import build_probe_plan
from src.r5a.fleet import load_fleet


def test_provider_smoke_prefers_deepseek_official_and_openrouter_fallback() -> None:
    fleet = load_fleet("config/fleet/r5a_fleet.yaml")
    env = {
        "DEEPSEEK_API_KEY": "deepseek-key",
        "OPENROUTER_API_KEY": "openrouter-key",
    }

    plans = {plan.model_id: plan for plan in build_probe_plan(fleet, env)}

    assert plans["deepseek-v4-pro"].route == "deepseek_official"
    assert plans["deepseek-v4-pro"].route_model == "deepseek-v4-pro"

    assert plans["gpt-4.1"].route == "openrouter"
    assert plans["gpt-4.1"].route_model == "openai/gpt-4.1"
    assert plans["gpt-5.1"].route == "openrouter"
    assert plans["gpt-5.1"].route_model == "openai/gpt-5.1"
    assert plans["claude-sonnet-4.6"].route == "openrouter"
    assert plans["claude-sonnet-4.6"].route_model == "anthropic/claude-sonnet-4.6"


def test_provider_smoke_prefers_official_openai_and_anthropic_keys() -> None:
    fleet = load_fleet("config/fleet/r5a_fleet.yaml")
    env = {
        "DEEPSEEK_API_KEY": "deepseek-key",
        "OPENROUTER_API_KEY": "openrouter-key",
        "OPENAI_API_KEY": "openai-key",
        "ANTHROPIC_API_KEY": "anthropic-key",
    }

    plans = {plan.model_id: plan for plan in build_probe_plan(fleet, env)}

    assert plans["gpt-4.1"].route == "openai_official"
    assert plans["gpt-4.1"].route_model == "gpt-4.1-2025-04-14"
    assert plans["gpt-5.1"].route == "openai_official"
    assert plans["gpt-5.1"].route_model == "gpt-5.1-2025-11-13"
    assert plans["claude-sonnet-4.6"].route == "anthropic_official"
    assert plans["claude-sonnet-4.6"].route_model == "claude-sonnet-4-6"
