"""Unit tests for batch_chat_concurrent failure_isolated mode (C0).

Goal: a single bad prompt must not poison the rest of the batch when
failure_isolated=True. Each prompt index is preserved, and failures surface as
BaseException objects.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.llm_client import LLMClient
from src.models import LLMResponse


def _build_client() -> LLMClient:
    return LLMClient(
        base_url="https://example.invalid/v1",
        model="test-model",
        api_key="dummy",
        enable_cache=False,
    )


async def _fake_single_factory(failing_indices: set[int]):
    """Return an async fn that mimics _async_single, failing for given indices."""
    counter = {"i": 0}

    async def _fake_single(client, semaphore, system, user, bypass_cache=False, max_retries=5):
        idx = counter["i"]
        counter["i"] += 1
        if idx in failing_indices:
            raise RuntimeError(f"injected failure at {idx}")
        return LLMResponse(
            model="test-model",
            prompt_hash=f"hash_{idx}",
            raw_response=f"response_{idx}",
            reasoning=f"response_{idx}",
            input_tokens=1,
            output_tokens=1,
            logprobs=None,
        )

    return _fake_single


def test_failure_isolated_returns_exceptions_at_stable_indices():
    client = _build_client()
    prompts = [(f"sys_{i}", f"user_{i}") for i in range(5)]
    failing_indices = {1, 3}

    fake = asyncio.run(_fake_single_factory(failing_indices))
    with patch.object(LLMClient, "_async_single", new=fake):
        results = client.batch_chat_concurrent(
            prompts, max_concurrency=2, failure_isolated=True
        )

    assert len(results) == 5
    for i, r in enumerate(results):
        if i in failing_indices:
            assert isinstance(r, BaseException), f"index {i} should be Exception, got {type(r)}"
            assert "injected failure" in str(r)
        else:
            assert isinstance(r, LLMResponse), f"index {i} should be LLMResponse, got {type(r)}"
            assert r.raw_response == f"response_{i}"


def test_legacy_mode_propagates_first_failure():
    client = _build_client()
    prompts = [(f"sys_{i}", f"user_{i}") for i in range(3)]

    fake = asyncio.run(_fake_single_factory({0}))
    with patch.object(LLMClient, "_async_single", new=fake):
        with pytest.raises(RuntimeError, match="injected failure"):
            client.batch_chat_concurrent(
                prompts, max_concurrency=2, failure_isolated=False
            )


def test_failure_isolated_all_pass_returns_homogeneous_responses():
    client = _build_client()
    prompts = [(f"sys_{i}", f"user_{i}") for i in range(4)]

    fake = asyncio.run(_fake_single_factory(set()))
    with patch.object(LLMClient, "_async_single", new=fake):
        results = client.batch_chat_concurrent(
            prompts, max_concurrency=2, failure_isolated=True
        )

    assert len(results) == 4
    assert all(isinstance(r, LLMResponse) for r in results)
