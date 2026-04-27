"""vLLM completion-endpoint backend for `P_logprob`.

Per plan §5.2, the backend MUST hit the **completion** endpoint
(not chat) and request `echo=True, max_tokens=0, logprobs=True,
top_logprobs=5`. Chat endpoints add a chat template wrapping that
contaminates the per-token logprobs we score.

The backend issues two calls per article:
  1. `POST /v1/tokenize` — to obtain the integer token IDs (vLLM's
     completion response only returns string tokens, not IDs);
  2. `POST /v1/completions` with echo — to obtain the per-token
     logprob trace.

We refuse to construct a `LogProbTrace` if the two responses disagree
on token count beyond a one-token BOS/EOS allowance, since the trace
would be unusable for downstream paired analysis.

Network policy follows project memory `feedback_codex_mcp.md` /
`infra_capabilities.md`: `trust_env=False`, `proxy=None`. The caller
should set `NO_PROXY=localhost,127.0.0.1,host.docker.internal` in the
environment before launching the script.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import httpx

from ..contracts import (
    LogProbTrace,
    RequestFingerprint,
    SeedSupport,
)


_TOKEN_COUNT_TOLERANCE = 1  # one BOS/EOS difference is allowed; logged in the trace


class VLLMBackendError(RuntimeError):
    """Raised when vLLM returns malformed or inconsistent data."""


class VLLMLogprobBackend:
    """Async vLLM completion client that returns `LogProbTrace` records.

    Constructor inputs come from the resolved fleet `ModelConfig` and the
    runtime config; the backend itself does not load YAML.

    Args:
        base_url: e.g. ``http://localhost:8000`` (no trailing ``/v1``).
        served_model_name: the string vLLM was launched with via
            ``--served-model-name``; this is what /v1/models lists.
        model_id: our fleet model_id (used in trace records).
        tokenizer_family: from fleet config; for record-keeping.
        tokenizer_sha: pinned tokenizer commit SHA; recorded in trace.
        hf_commit_sha: pinned model commit SHA; recorded in trace.
        timeout_seconds: per-request timeout.
        max_retries: simple count-based retry for transient 5xx / I/O errors.
        top_logprobs: how many alternative tokens to request per position.
            Plan §5.2 fixes this at 5.
    """

    def __init__(
        self,
        *,
        base_url: str,
        served_model_name: str,
        model_id: str,
        tokenizer_family: str,
        tokenizer_sha: str,
        hf_commit_sha: str,
        timeout_seconds: int = 120,
        max_retries: int = 3,
        top_logprobs: int = 5,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.served_model_name = served_model_name
        self.model_id = model_id
        self.tokenizer_family = tokenizer_family
        self.tokenizer_sha = tokenizer_sha
        self.hf_commit_sha = hf_commit_sha
        self.max_retries = max_retries
        self.top_logprobs = top_logprobs
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout_seconds,
            trust_env=False,
            # httpx accepts None to disable proxies entirely
            proxy=None,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "VLLMLogprobBackend":
        return self

    async def __aexit__(self, *args: object) -> None:
        del args
        await self.aclose()

    # ------------------------------------------------------------------ probes

    async def list_models(self) -> list[str]:
        """Sanity probe; returns the model IDs vLLM is currently serving."""
        resp = await self._client.get("/v1/models")
        resp.raise_for_status()
        data = resp.json().get("data", [])
        return [row["id"] for row in data]

    # ---------------------------------------------------------------- the call

    async def trace(self, *, case_id: str, article_text: str) -> LogProbTrace:
        """Compute one `LogProbTrace` for `article_text` on this model."""

        token_ids = await self._tokenize(article_text)
        completion = await self._echo_completion(article_text)

        logprobs_obj = completion.get("choices", [{}])[0].get("logprobs") or {}
        token_logprobs = logprobs_obj.get("token_logprobs") or []

        # vLLM returns None for the first token (no left context); drop
        # leading Nones and any (rare) interior Nones to keep arrays aligned.
        cleaned: list[float] = []
        kept_indices: list[int] = []
        for i, lp in enumerate(token_logprobs):
            if lp is None:
                continue
            cleaned.append(float(lp))
            kept_indices.append(i)

        if not cleaned:
            raise VLLMBackendError(
                f"completion returned no usable logprobs for case {case_id}"
            )

        # Align raw_token_ids to the kept positions. /tokenize returns the
        # full token list; vLLM completion's logprobs.tokens has the same
        # length within tolerance.
        completion_tokens = logprobs_obj.get("tokens") or []
        n_completion = len(completion_tokens)
        n_tokenize = len(token_ids)
        if abs(n_completion - n_tokenize) > _TOKEN_COUNT_TOLERANCE:
            raise VLLMBackendError(
                f"token count mismatch beyond ±{_TOKEN_COUNT_TOLERANCE}: "
                f"/tokenize={n_tokenize}, completion={n_completion}"
            )

        # Map kept_indices (into the completion array) onto raw_token_ids
        # (from /tokenize). When counts differ by 1, assume the discrepancy
        # is a leading or trailing BOS/EOS that vLLM added on the
        # completion path; trim the longer side from the front.
        head_drop = max(0, n_completion - n_tokenize)
        ids_aligned: list[int] = []
        for idx in kept_indices:
            tok_idx = idx - head_drop
            if 0 <= tok_idx < n_tokenize:
                ids_aligned.append(int(token_ids[tok_idx]))
            else:
                # the kept position fell outside the /tokenize range;
                # placeholder so list lengths stay equal
                ids_aligned.append(-1)

        if len(ids_aligned) != len(cleaned):
            raise VLLMBackendError(
                "internal alignment error between token IDs and logprobs"
            )

        fingerprint = RequestFingerprint(
            provider="vllm",
            model_id=self.model_id,
            system_fingerprint=completion.get("system_fingerprint"),
            response_id=completion.get("id"),
            route_hint=None,
            ts=datetime.now(timezone.utc),
            seed_requested=None,
            seed_supported=SeedSupport.YES,
            seed_effective=None,
        )

        return LogProbTrace(
            case_id=case_id,
            model_id=self.model_id,
            tokenizer_family=self.tokenizer_family,
            tokenizer_sha=self.tokenizer_sha,
            hf_commit_sha=self.hf_commit_sha,
            article_token_count=len(cleaned),
            raw_token_ids=ids_aligned,
            token_logprobs=cleaned,
            thinking_mode="off",
            backend="vllm_completion",
            fingerprint=fingerprint,
        )

    # ------------------------------------------------------------- HTTP helpers

    async def _tokenize(self, text: str) -> list[int]:
        payload = {"model": self.served_model_name, "prompt": text}
        data = await self._post_with_retry("/v1/tokenize", payload)
        tokens = data.get("tokens")
        if not isinstance(tokens, list) or not tokens:
            raise VLLMBackendError(f"/v1/tokenize returned no tokens: {data!r}")
        return [int(t) for t in tokens]

    async def _echo_completion(self, text: str) -> dict:
        payload = {
            "model": self.served_model_name,
            "prompt": text,
            "echo": True,
            "max_tokens": 0,
            "temperature": 0.0,
            "logprobs": self.top_logprobs,
        }
        return await self._post_with_retry("/v1/completions", payload)

    async def _post_with_retry(self, path: str, payload: dict) -> dict:
        last_err: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                resp = await self._client.post(path, json=payload)
                if resp.status_code >= 500:
                    last_err = httpx.HTTPStatusError(
                        f"server error {resp.status_code}",
                        request=resp.request,
                        response=resp,
                    )
                else:
                    resp.raise_for_status()
                    return resp.json()
            except (httpx.TransportError, httpx.HTTPStatusError) as exc:
                last_err = exc
            # exponential backoff: 1s, 2s, 4s ...
            await asyncio.sleep(2.0 ** attempt)

        assert last_err is not None
        raise VLLMBackendError(
            f"POST {path} failed after {self.max_retries} attempts: {last_err}"
        ) from last_err


__all__ = ["VLLMBackendError", "VLLMLogprobBackend"]
