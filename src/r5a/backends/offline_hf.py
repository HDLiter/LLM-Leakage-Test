"""Offline HuggingFace forward-pass fallback for `P_logprob`.

Used when a vLLM endpoint cannot expose prompt-side `echo=True`
logprobs cleanly. The known case is GLM-4-9B (plan §5.2 R2 risk).
The fallback runs `transformers.AutoModelForCausalLM.from_pretrained`
on the same checkpoint SHA the vLLM container would have loaded, so
the run manifest still pins identical model provenance.

Stage 0 caveat: the local development machine in this project does
**not** have `torch` or `transformers` installed (rag_finance env is
API-side). Imports are therefore lazy: importing this module is safe
and never touches torch; calling `OfflineHFBackend(...)` triggers the
heavy imports and will raise `ImportError` locally. Cloud machines
launched by `scripts/ws1_provision_autodl.sh` install both packages
into the runtime venv before this code runs.
"""

from __future__ import annotations

from datetime import datetime, timezone

from ..contracts import LogProbTrace, RequestFingerprint, SeedSupport


class OfflineHFBackendError(RuntimeError):
    """Raised when the HF fallback cannot produce a usable trace."""


class OfflineHFBackend:
    """Synchronous CPU/GPU forward-pass logprob backend.

    Args mirror `VLLMLogprobBackend` so the operator can swap backends
    without changing call sites.

    Args:
        model_path: local path or HF repo id; must match `hf_commit_sha`.
        model_id: our fleet model_id (used in trace records).
        tokenizer_family / tokenizer_sha / hf_commit_sha: for trace pinning.
        device: ``"cuda"`` (default) or ``"cpu"``.
        torch_dtype: ``"float16"`` (default), ``"bfloat16"``, or ``"float32"``.
            GLM-4-9B fp16 fits A6000 48 GB comfortably.
    """

    def __init__(
        self,
        *,
        model_path: str,
        model_id: str,
        tokenizer_family: str,
        tokenizer_sha: str,
        hf_commit_sha: str,
        device: str = "cuda",
        torch_dtype: str = "float16",
    ) -> None:
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "OfflineHFBackend requires `torch` and `transformers` "
                "in the runtime environment. The local rag_finance env "
                "intentionally does not have them; install on the cloud "
                "instance instead."
            ) from exc

        dtype_map = {
            "float16": torch.float16,
            "bfloat16": torch.bfloat16,
            "float32": torch.float32,
        }
        if torch_dtype not in dtype_map:
            raise ValueError(f"unsupported torch_dtype: {torch_dtype!r}")

        self.model_id = model_id
        self.tokenizer_family = tokenizer_family
        self.tokenizer_sha = tokenizer_sha
        self.hf_commit_sha = hf_commit_sha
        self.device = device
        self.torch_dtype = torch_dtype

        self._torch = torch
        self._tokenizer = AutoTokenizer.from_pretrained(
            model_path, trust_remote_code=True
        )
        self._model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=dtype_map[torch_dtype],
            device_map=device,
            trust_remote_code=True,
        )
        self._model.eval()

    def trace(self, *, case_id: str, article_text: str) -> LogProbTrace:
        torch = self._torch
        encoded = self._tokenizer(
            article_text,
            return_tensors="pt",
            add_special_tokens=False,
        )
        input_ids = encoded["input_ids"].to(self._model.device)

        with torch.inference_mode():
            outputs = self._model(input_ids=input_ids, use_cache=False)
            logits = outputs.logits  # (1, T, V)
            log_probs = torch.log_softmax(logits, dim=-1)

        # The logprob of token i (i >= 1) is conditioned on tokens 0..i-1
        # and read from the model's prediction at position i-1. The first
        # token has no preceding context, so we skip it (matches vLLM's
        # echo=True behavior of returning None for token 0).
        ids = input_ids[0]
        if ids.numel() < 2:
            raise OfflineHFBackendError(
                f"article {case_id} encodes to <2 tokens; cannot score"
            )

        targets = ids[1:]
        gathered = log_probs[0, :-1].gather(
            dim=-1, index=targets.unsqueeze(-1)
        ).squeeze(-1)
        token_logprobs = [float(x) for x in gathered.detach().cpu().tolist()]
        raw_token_ids = [int(x) for x in targets.detach().cpu().tolist()]

        if len(token_logprobs) != len(raw_token_ids):
            raise OfflineHFBackendError(
                "internal length mismatch between targets and logprobs"
            )

        fingerprint = RequestFingerprint(
            provider="offline_hf",
            model_id=self.model_id,
            system_fingerprint=f"hf:{self.hf_commit_sha[:12]}",
            response_id=None,
            route_hint=f"{self.device}:{self.torch_dtype}",
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
            article_token_count=len(token_logprobs),
            raw_token_ids=raw_token_ids,
            token_logprobs=token_logprobs,
            thinking_mode="off",
            backend="offline_hf",
            fingerprint=fingerprint,
        )


__all__ = ["OfflineHFBackend", "OfflineHFBackendError"]
