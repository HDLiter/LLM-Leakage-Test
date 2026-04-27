"""vLLM completion-endpoint backend for `P_logprob`.

Per plan §5.2, the backend MUST hit the **completion** endpoint
(not chat) and request `echo=True, max_tokens=0, logprobs=top_k`.
Chat endpoints add a chat template wrapping that contaminates the
per-token logprobs we score.

Token-alignment strategy (rewritten 2026-04-27 after WS0+WS1 review):
  1. Call `POST /v1/tokenize` once to obtain canonical integer IDs.
  2. Call `POST /v1/completions` with `prompt=<list[int]>` (vLLM accepts
     pre-tokenized input directly), so the completion path cannot
     re-tokenize and the response logprobs align 1:1 with the IDs.
  3. The first position's `token_logprob` is `None` (no left context);
     any *interior* `None` is a backend pathology — fail the trace.
  4. We never insert sentinel placeholder IDs. If alignment is off,
     the trace is rejected.

Network policy (project memory `infra_capabilities.md`):
  `trust_env=False`, `proxy=None`. Caller should set
  `NO_PROXY=localhost,127.0.0.1,host.docker.internal` before launching.
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


# Status codes that indicate a transient condition worth retrying;
# everything else (especially 400/401/403/422) means our request
# shape is wrong and retrying just hides the real error.
_TRANSIENT_STATUS = frozenset({408, 409, 425, 429, 500, 502, 503, 504})


class VLLMBackendError(RuntimeError):
    """Raised when vLLM returns malformed or inconsistent data."""


class VLLMLogprobBackend:
    """Async vLLM completion client that returns `LogProbTrace` records.

    Constructor inputs come from the resolved fleet `ModelConfig` and
    the runtime config; the backend itself does not load YAML.

    Args:
        base_url: e.g. ``http://localhost:8000`` (no trailing ``/v1``).
        served_model_name: vLLM ``--served-model-name`` (what /v1/models lists).
        model_id: fleet model_id, used in trace records.
        tokenizer_family / tokenizer_sha / hf_commit_sha: pinning fields.
        quant_scheme: e.g. ``"AWQ-INT4"`` or ``"fp16"``; recorded into trace.
        weight_dtype: optional ``"float16"`` / ``"bfloat16"``; recorded.
        vllm_image_digest: optional Docker image SHA; recorded.
        timeout_seconds: per-HTTP-request timeout.
        max_retries: count of retries for transient failures only.
        top_logprobs: how many alternative tokens per position. Plan §5.2
            calls for 5; can be raised per Stats-lens recommendation.
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
        quant_scheme: str,
        weight_dtype: str | None = None,
        vllm_image_digest: str | None = None,
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
        self.quant_scheme = quant_scheme
        self.weight_dtype = weight_dtype
        self.vllm_image_digest = vllm_image_digest
        self.max_retries = max(1, max_retries)
        self.top_logprobs = top_logprobs
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout_seconds,
            trust_env=False,
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
        resp = await self._client.get("/v1/models")
        resp.raise_for_status()
        data = resp.json().get("data", [])
        return [row["id"] for row in data]

    # ---------------------------------------------------------------- the call

    async def trace(self, *, case_id: str, article_text: str) -> LogProbTrace:
        """Compute one `LogProbTrace` for `article_text` on this model."""

        # Step 1: canonical tokenization
        token_ids = await self._tokenize(article_text)
        if len(token_ids) < 2:
            raise VLLMBackendError(
                f"article {case_id} encodes to <2 tokens; cannot score"
            )

        # Step 2: echo completion driven by the IDs themselves
        completion = await self._echo_completion(token_ids)

        choice = completion.get("choices", [{}])[0]
        logprobs_obj = choice.get("logprobs") or {}
        token_logprobs = logprobs_obj.get("token_logprobs") or []
        top_logprobs_field = logprobs_obj.get("top_logprobs") or []

        if len(token_logprobs) != len(token_ids):
            raise VLLMBackendError(
                "vLLM /v1/completions returned a logprob list whose length "
                f"({len(token_logprobs)}) differs from the prompt token "
                f"count ({len(token_ids)}) for case {case_id}; refusing "
                "to misalign the trace"
            )

        # Strict None handling: only the first position may be None
        # (no left context for the first token). Interior None means
        # the backend hit a pathology we should not silently smooth over.
        cleaned_lp: list[float] = []
        cleaned_ids: list[int] = []
        cleaned_top: list[list[float]] = []
        for i, lp in enumerate(token_logprobs):
            if lp is None:
                if i != 0:
                    raise VLLMBackendError(
                        f"interior None logprob at position {i} for case "
                        f"{case_id} (only position 0 may be None)"
                    )
                continue  # drop the leading None
            cleaned_lp.append(float(lp))
            cleaned_ids.append(int(token_ids[i]))
            cleaned_top.append(_extract_top_alternatives(top_logprobs_field, i))

        if not cleaned_lp:
            raise VLLMBackendError(
                f"completion returned no usable logprobs for case {case_id}"
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
            quant_scheme=self.quant_scheme,
            weight_dtype=self.weight_dtype,
            vllm_image_digest=self.vllm_image_digest,
            article_token_count=len(cleaned_lp),
            raw_token_ids=cleaned_ids,
            token_logprobs=cleaned_lp,
            top_alternative_logprobs=cleaned_top,
            top_logprobs_k=self.top_logprobs,
            prefix_token_count=0,  # vLLM /tokenize default add_special_tokens behavior
            thinking_mode="off",
            backend="vllm_completion",
            fingerprint=fingerprint,
        )

    # ------------------------------------------------------------- HTTP helpers

    async def _tokenize(self, text: str) -> list[int]:
        payload = {
            "model": self.served_model_name,
            "prompt": text,
            "add_special_tokens": True,  # default; explicit for parity with offline_hf
        }
        data = await self._post_with_retry("/v1/tokenize", payload)
        tokens = data.get("tokens")
        if not isinstance(tokens, list) or not tokens:
            raise VLLMBackendError(f"/v1/tokenize returned no tokens: {data!r}")
        return [int(t) for t in tokens]

    async def _echo_completion(self, token_ids: list[int]) -> dict:
        # Pass pre-tokenized IDs as the prompt — vLLM accepts list[int]
        # natively on /v1/completions, which guarantees the response
        # logprob list aligns with the IDs we supplied.
        payload = {
            "model": self.served_model_name,
            "prompt": token_ids,
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
            except httpx.TransportError as exc:
                last_err = exc
            else:
                if resp.status_code in _TRANSIENT_STATUS:
                    last_err = httpx.HTTPStatusError(
                        f"transient {resp.status_code} on {path}: "
                        f"{resp.text[:200]}",
                        request=resp.request,
                        response=resp,
                    )
                elif 400 <= resp.status_code < 500:
                    # Permanent client error — retrying just hides the bug.
                    raise VLLMBackendError(
                        f"POST {path} failed with non-retryable "
                        f"{resp.status_code}: {resp.text[:500]}"
                    )
                else:
                    try:
                        return resp.json()
                    except ValueError as exc:
                        raise VLLMBackendError(
                            f"POST {path} returned status {resp.status_code} "
                            f"but the body is not JSON: {resp.text[:200]}"
                        ) from exc

            # Backoff before next attempt: 1s, 2s, 4s ...
            if attempt + 1 < self.max_retries:
                await asyncio.sleep(2.0**attempt)

        assert last_err is not None
        raise VLLMBackendError(
            f"POST {path} failed after {self.max_retries} transient retries: "
            f"{last_err}"
        ) from last_err


def _extract_top_alternatives(
    top_logprobs_field: list, position: int
) -> list[float]:
    """Extract a flat list of alternative-token logprobs at one position.

    vLLM returns `top_logprobs[i]` as either `None` (position 0) or a
    dict mapping token-string -> logprob. We discard the token strings
    (Min-K%++ scoring uses only the magnitudes) and keep the numeric
    values sorted descending so that downstream code can treat the
    inner list as "top-K logprobs in rank order".
    """

    if position >= len(top_logprobs_field):
        return []
    cell = top_logprobs_field[position]
    if cell is None:
        return []
    # Some vLLM versions return list[{"token": str, "logprob": float}, ...]
    # rather than dict[str, float]; handle both shapes.
    if isinstance(cell, dict):
        values = list(cell.values())
    elif isinstance(cell, list):
        values = []
        for item in cell:
            if isinstance(item, dict):
                lp = item.get("logprob")
                if lp is None:
                    continue
                values.append(lp)
            else:
                values.append(item)
    else:
        return []
    values = [float(v) for v in values if v is not None]
    values.sort(reverse=True)
    return values


__all__ = ["VLLMBackendError", "VLLMLogprobBackend"]
