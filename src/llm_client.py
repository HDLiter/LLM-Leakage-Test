"""DeepSeek OpenAI-compatible client with caching, retry, and async concurrency."""

from __future__ import annotations

import asyncio
from . import DEFAULT_CONCURRENCY
import hashlib
import json
import os
import time
from pathlib import Path
from collections.abc import Sequence
from typing import Any, Literal, cast, overload

import httpx
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .models import LLMResponse

load_dotenv()

_CACHE_DIR = Path(__file__).parent.parent / "data" / "cache"


class LLMClient:
    """Synchronous DeepSeek client via OpenAI-compatible API."""

    def __init__(
        self,
        base_url: str = "https://api.deepseek.com/v1",
        model: str = "deepseek-chat",
        temperature: float = 0.0,
        max_tokens: int = 2048,
        api_key: str | None = None,
        cache_dir: Path | None = None,
        enable_cache: bool = True,
        request_logprobs: bool = False,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.cache_dir = cache_dir or _CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.enable_cache = enable_cache
        self.request_logprobs = request_logprobs
        self._client = httpx.Client(timeout=120.0)

    def _cache_key(self, messages: list[dict]) -> str:
        raw = json.dumps(
            {"model": self.model, "temperature": self.temperature, "messages": messages},
            sort_keys=True, ensure_ascii=False,
        )
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def _load_cache(self, key: str) -> dict | None:
        path = self.cache_dir / f"{key}.json"
        if self.enable_cache and path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return None

    def _save_cache(self, key: str, data: dict, messages: list[dict] | None = None) -> None:
        if self.enable_cache:
            if messages is not None:
                data["messages"] = messages
            path = self.cache_dir / f"{key}.json"
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=4, max=60),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.ConnectError)),
    )
    def _raw_chat(self, messages: list[dict]) -> dict:
        body: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if self.request_logprobs:
            body["logprobs"] = True
            body["top_logprobs"] = 5
        resp = self._client.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json=body,
        )
        resp.raise_for_status()
        return resp.json()

    def chat(
        self,
        system: str,
        user: str,
        bypass_cache: bool = False,
    ) -> LLMResponse:
        """Send a chat request and return a parsed LLMResponse."""
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        cache_key = self._cache_key(messages)

        if not bypass_cache:
            cached = self._load_cache(cache_key)
            if cached:
                return LLMResponse(**cached["parsed"])

        raw = self._raw_chat(messages)
        choice = raw["choices"][0]
        content = choice["message"]["content"]
        usage = raw.get("usage", {})

        logprobs_data = None
        if self.request_logprobs and choice.get("logprobs"):
            logprobs_data = choice["logprobs"].get("content", [])

        parsed = LLMResponse(
            model=self.model,
            prompt_hash=cache_key,
            raw_response=content,
            reasoning=content,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            logprobs=logprobs_data,
        )

        self._save_cache(cache_key, {"raw": raw, "parsed": parsed.model_dump()}, messages=messages)
        return parsed

    def batch_chat(
        self,
        prompts: list[tuple[str, str]],
        delay: float = 0.5,
    ) -> list[LLMResponse]:
        """Send multiple (system, user) prompts sequentially with delay."""
        results = []
        for system, user in prompts:
            results.append(self.chat(system, user))
            time.sleep(delay)
        return results

    # ── 异步并发接口 ──────────────────────────────────────────────

    def _build_body(self, messages: list[dict]) -> dict:
        body: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if self.request_logprobs:
            body["logprobs"] = True
            body["top_logprobs"] = 5
        return body

    def _parse_raw(self, raw: dict, cache_key: str) -> LLMResponse:
        choice = raw["choices"][0]
        content = choice["message"]["content"]
        usage = raw.get("usage", {})
        logprobs_data = None
        if self.request_logprobs and choice.get("logprobs"):
            logprobs_data = choice["logprobs"].get("content", [])
        return LLMResponse(
            model=self.model,
            prompt_hash=cache_key,
            raw_response=content,
            reasoning=content,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            logprobs=logprobs_data,
        )

    async def _async_single(
        self,
        client: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        system: str,
        user: str,
        bypass_cache: bool = False,
        max_retries: int = 5,
    ) -> LLMResponse:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        cache_key = self._cache_key(messages)

        if not bypass_cache:
            cached = self._load_cache(cache_key)
            if cached:
                return LLMResponse(**cached["parsed"])

        last_exc = None
        for attempt in range(max_retries):
            try:
                async with semaphore:
                    resp = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        json=self._build_body(messages),
                    )
                    resp.raise_for_status()
                    raw = resp.json()
            except (httpx.HTTPStatusError, httpx.ConnectError) as e:
                last_exc = e
                wait = min(60, 4 * (2 ** attempt))
                await asyncio.sleep(wait)
                continue
            break
        else:
            raise last_exc  # type: ignore[misc]

        parsed = self._parse_raw(raw, cache_key)
        self._save_cache(cache_key, {"raw": raw, "parsed": parsed.model_dump()}, messages=messages)
        return parsed

    async def _batch_chat_async(
        self,
        prompts: list[tuple[str, str]],
        max_concurrency: int,
        bypass_cache: bool,
        failure_isolated: bool = False,
    ) -> list[LLMResponse | BaseException]:
        semaphore = asyncio.Semaphore(max_concurrency)
        async with httpx.AsyncClient(timeout=120.0) as client:
            tasks = [
                self._async_single(client, semaphore, s, u, bypass_cache)
                for s, u in prompts
            ]
            if failure_isolated:
                # Per-prompt isolation: failed prompts surface as Exception
                # at the same index instead of killing the whole batch.
                return list(await asyncio.gather(*tasks, return_exceptions=True))
            # Legacy behavior: first failure raises, kills the batch.
            return list(await asyncio.gather(*tasks))

    @overload
    def batch_chat_concurrent(
        self,
        prompts: list[tuple[str, str]],
        max_concurrency: int = ...,
        bypass_cache: bool = ...,
        *,
        failure_isolated: Literal[False] = ...,
    ) -> list[LLMResponse]: ...

    @overload
    def batch_chat_concurrent(
        self,
        prompts: list[tuple[str, str]],
        max_concurrency: int = ...,
        bypass_cache: bool = ...,
        *,
        failure_isolated: Literal[True],
    ) -> list[LLMResponse | BaseException]: ...

    def batch_chat_concurrent(
        self,
        prompts: list[tuple[str, str]],
        max_concurrency: int = DEFAULT_CONCURRENCY,
        bypass_cache: bool = False,
        *,
        failure_isolated: bool = False,
    ) -> Sequence[LLMResponse | BaseException]:
        """Send multiple prompts concurrently via asyncio.

        Args:
            prompts: list of (system, user) tuples.
            max_concurrency: max parallel requests (default DEFAULT_CONCURRENCY).
            bypass_cache: skip cache lookup if True.
            failure_isolated: when True, failures from individual prompts are
                returned as BaseException objects at their stable index instead
                of propagating and killing the batch. The caller is responsible
                for checking each entry's type. Default False preserves the
                legacy "first error raises" behavior.

        Returns:
            list in the same order as prompts. When ``failure_isolated=False``
            (default) every entry is an ``LLMResponse`` (any failure will have
            already raised). When ``failure_isolated=True`` failed entries are
            ``BaseException`` objects at their stable index.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Inside Jupyter or already-running event loop: use nest_asyncio
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(
                self._batch_chat_async(
                    prompts, max_concurrency, bypass_cache, failure_isolated
                )
            )
        return asyncio.run(
            self._batch_chat_async(
                prompts, max_concurrency, bypass_cache, failure_isolated
            )
        )
