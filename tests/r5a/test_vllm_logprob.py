"""Mocked-httpx tests for the vLLM logprob backend.

Locks in the strict-alignment guarantees we promised in the WS0+WS1
review fix batch:

- token-count mismatch between /v1/tokenize and /v1/completions raises
- interior `None` logprob (i.e. anywhere except position 0) raises
- HTTP 400/422 fail fast (no retry)
- HTTP 429 / 5xx are retried up to `max_retries`
- vLLM builds that expose tokenization at /tokenize are supported
"""

from __future__ import annotations

import httpx
import pytest

from src.r5a.backends.vllm_logprob import VLLMBackendError, VLLMLogprobBackend


def _make_backend(handler) -> VLLMLogprobBackend:
    backend = VLLMLogprobBackend(
        base_url="http://test",
        served_model_name="qwen2.5-7b",
        model_id="qwen2.5-7b",
        tokenizer_family="qwen",
        tokenizer_sha="tok-x",
        hf_commit_sha="hf-x",
        quant_scheme="AWQ-INT4",
        timeout_seconds=5,
        max_retries=2,
        top_logprobs=3,
    )
    transport = httpx.MockTransport(handler)
    # Replace the httpx client with one using the mock transport
    backend._client = httpx.AsyncClient(  # noqa: SLF001
        base_url="http://test",
        transport=transport,
        timeout=5,
    )
    return backend


def _ok_completion(token_logprobs, top_logprobs):
    return httpx.Response(
        200,
        json={
            "id": "cmpl-test",
            "choices": [
                {
                    "logprobs": {
                        "tokens": ["t" + str(i) for i in range(len(token_logprobs))],
                        "token_logprobs": token_logprobs,
                        "top_logprobs": top_logprobs,
                    }
                }
            ],
        },
    )


def _ok_tokenize(token_ids):
    return httpx.Response(
        200,
        json={"count": len(token_ids), "tokens": token_ids},
    )


@pytest.mark.asyncio
async def test_count_mismatch_raises():
    """If /v1/completions returns more or fewer logprobs than the IDs we
    sent in, the backend must refuse rather than silently realign."""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/v1/tokenize"):
            return _ok_tokenize([10, 20, 30, 40])
        # Completion returns logprobs for only 3 positions instead of 4
        return _ok_completion([None, -1.0, -2.0], [None, {"a": -1.0}, {"a": -2.0}])

    backend = _make_backend(handler)
    try:
        with pytest.raises(VLLMBackendError, match="length"):
            await backend.trace(case_id="c1", article_text="...")
    finally:
        await backend.aclose()


@pytest.mark.asyncio
async def test_interior_none_raises():
    """`None` in the middle of token_logprobs is a backend pathology."""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/v1/tokenize"):
            return _ok_tokenize([10, 20, 30, 40])
        # 4 logprobs; position 2 is None (interior — not the leading)
        return _ok_completion(
            [None, -1.0, None, -3.0],
            [None, {"a": -1.0}, {"a": -2.0}, {"a": -3.0}],
        )

    backend = _make_backend(handler)
    try:
        with pytest.raises(VLLMBackendError, match="interior None"):
            await backend.trace(case_id="c1", article_text="...")
    finally:
        await backend.aclose()


@pytest.mark.asyncio
async def test_4xx_does_not_retry():
    """A 422 from /v1/tokenize means our request shape is wrong; do
    NOT retry."""
    call_count = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        call_count["n"] += 1
        return httpx.Response(422, json={"error": "bad payload"})

    backend = _make_backend(handler)
    try:
        with pytest.raises(VLLMBackendError, match="non-retryable"):
            await backend.trace(case_id="c1", article_text="...")
    finally:
        await backend.aclose()
    assert call_count["n"] == 1, "4xx must not be retried"


@pytest.mark.asyncio
async def test_tokenize_404_falls_back_to_unversioned_route():
    """vLLM 0.10.x exposes /tokenize, while completions remain under
    /v1/completions. Route absence should not block the trace path."""

    seen_paths: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_paths.append(request.url.path)
        if request.url.path.endswith("/v1/tokenize"):
            return httpx.Response(404, json={"detail": "Not Found"})
        if request.url.path.endswith("/tokenize"):
            return _ok_tokenize([10, 20, 30, 40])
        return _ok_completion(
            [None, -1.0, -2.0, -3.0],
            [None, {"a": -1.0}, {"a": -2.0}, {"a": -3.0}],
        )

    backend = _make_backend(handler)
    try:
        trace = await backend.trace(case_id="c1", article_text="...")
    finally:
        await backend.aclose()

    assert seen_paths[:2] == ["/v1/tokenize", "/tokenize"]
    assert seen_paths[-1] == "/v1/completions"
    assert trace.raw_token_ids == [20, 30, 40]


@pytest.mark.asyncio
async def test_429_is_retried():
    """Transient 429 should be retried up to max_retries."""
    call_count = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        call_count["n"] += 1
        return httpx.Response(429, json={"error": "rate limited"})

    backend = _make_backend(handler)
    try:
        with pytest.raises(VLLMBackendError, match="transient retries"):
            # Make backoff effectively zero so the test runs fast
            backend.max_retries = 2
            await backend.trace(case_id="c1", article_text="...")
    finally:
        await backend.aclose()
    assert call_count["n"] == 2, "expected exactly max_retries (2) attempts"


@pytest.mark.asyncio
async def test_happy_path_strict_alignment():
    """Healthy 200 path produces a LogProbTrace with first None dropped
    and remaining token_ids/logprobs aligned 1:1."""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/v1/tokenize"):
            return _ok_tokenize([10, 20, 30, 40])
        return _ok_completion(
            [None, -1.0, -2.0, -3.0],
            [
                None,
                {"a": -1.5, "b": -1.7, "c": -1.9},
                {"a": -2.5, "b": -2.7, "c": -2.9},
                {"a": -3.5, "b": -3.7, "c": -3.9},
            ],
        )

    backend = _make_backend(handler)
    try:
        trace = await backend.trace(case_id="c1", article_text="...")
    finally:
        await backend.aclose()

    assert trace.article_token_count == 3  # first None dropped
    assert trace.raw_token_ids == [20, 30, 40]
    assert trace.token_logprobs == [-1.0, -2.0, -3.0]
    assert trace.top_logprobs_k == 3
    # top alternatives sorted descending
    assert trace.top_alternative_logprobs[0] == sorted(
        [-1.5, -1.7, -1.9], reverse=True
    )
    assert trace.quant_scheme == "AWQ-INT4"


@pytest.mark.asyncio
async def test_top_logprobs_are_trimmed_to_declared_k():
    """Some vLLM builds include the selected token plus K alternatives in
    top_logprobs. Persist no more than the declared top_logprobs_k."""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/v1/tokenize"):
            return _ok_tokenize([10, 20, 30, 40])
        return _ok_completion(
            [None, -1.0, -2.0, -3.0],
            [
                None,
                {"a": -1.5, "b": -1.7, "c": -1.9, "d": -2.1},
                {"a": -2.5, "b": -2.7, "c": -2.9, "d": -3.1},
                {"a": -3.5, "b": -3.7, "c": -3.9, "d": -4.1},
            ],
        )

    backend = _make_backend(handler)
    try:
        trace = await backend.trace(case_id="c1", article_text="...")
    finally:
        await backend.aclose()

    assert trace.top_logprobs_k == 3
    assert all(len(row) == 3 for row in trace.top_alternative_logprobs)
