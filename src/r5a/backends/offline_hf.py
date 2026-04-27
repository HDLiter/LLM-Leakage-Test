"""Offline HuggingFace forward-pass fallback for `P_logprob`.

Used when a vLLM endpoint cannot expose prompt-side `echo=True`
logprobs cleanly. The known case is GLM-4-9B (plan §5.2 R2 risk).
The fallback runs `transformers.AutoModelForCausalLM.from_pretrained`
on the same checkpoint SHA the vLLM container would have loaded, so
the run manifest still pins identical model provenance.

Stage 0 caveat: the local development machine does **not** have
`torch` or `transformers` installed (rag_finance env is API-side).
Imports are therefore lazy: importing this module is safe and never
touches torch; calling `OfflineHFBackend(...)` triggers the heavy
imports and will raise `ImportError` locally. Cloud machines launched
by `scripts/ws1_provision_autodl.sh --with-torch` install both
packages into the runtime venv before this code runs.

WS6 hooks: when constructed with `extract_hidden_states=True` and a
`hidden_states_dir`, the backend saves per-layer hidden state tensors
to `.safetensors` files alongside each trace and records the URI in
`LogProbTrace.hidden_states_uri`.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from ..contracts import LogProbTrace, RequestFingerprint, SeedSupport


class OfflineHFBackendError(RuntimeError):
    """Raised when the HF fallback cannot produce a usable trace."""


class OfflineHFBackend:
    """Synchronous CPU/GPU forward-pass logprob backend.

    Args mirror `VLLMLogprobBackend` so the operator can swap backends
    without changing call sites.

    Args:
        model_path: local path or HF repo id; must match `hf_commit_sha`.
        model_id: fleet model_id, used in trace records.
        tokenizer_family / tokenizer_sha / hf_commit_sha: pinning fields.
        quant_scheme: e.g. ``"fp16"`` or ``"AWQ-INT4"``; recorded into trace.
        weight_dtype: e.g. ``"float16"``; recorded.
        device: ``"cuda"`` (default) or ``"cpu"``.
        torch_dtype: ``"float16"`` (default), ``"bfloat16"``, or ``"float32"``.
        top_logprobs: how many alternative-token logprobs to record per
            position. With full vocab access we can compute these exactly
            (unlike the vLLM backend's top-K sample).
        extract_hidden_states: if True, capture per-layer hidden states.
        hidden_states_dir: directory to write `.safetensors` files; required
            when `extract_hidden_states=True`.
    """

    def __init__(
        self,
        *,
        model_path: str,
        model_id: str,
        tokenizer_family: str,
        tokenizer_sha: str,
        hf_commit_sha: str,
        quant_scheme: str,
        weight_dtype: str | None = None,
        device: str = "cuda",
        torch_dtype: str = "float16",
        top_logprobs: int = 5,
        extract_hidden_states: bool = False,
        hidden_states_dir: str | Path | None = None,
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

        if extract_hidden_states and hidden_states_dir is None:
            raise ValueError(
                "extract_hidden_states=True requires hidden_states_dir"
            )

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
        self.quant_scheme = quant_scheme
        self.weight_dtype = weight_dtype or torch_dtype
        self.device = device
        self.torch_dtype = torch_dtype
        self.top_logprobs = top_logprobs
        self.extract_hidden_states = extract_hidden_states
        self.hidden_states_dir = (
            Path(hidden_states_dir) if hidden_states_dir is not None else None
        )

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

        # Pre-compute the prefix-token count (BOS / [gMASK] / etc.).
        # Some tokenizers add per-call special tokens, others don't.
        # Use a known-empty-prefix probe; the difference is the prefix.
        with_special = self._tokenizer("", add_special_tokens=True)["input_ids"]
        without_special = self._tokenizer("", add_special_tokens=False)[
            "input_ids"
        ]
        self.prefix_token_count = max(
            0, len(with_special) - len(without_special)
        )

    def close(self) -> None:
        """Free GPU memory; safe to call multiple times."""
        torch = self._torch
        try:
            del self._model
        except AttributeError:
            pass
        try:
            del self._tokenizer
        except AttributeError:
            pass
        if hasattr(torch, "cuda") and torch.cuda.is_available():
            torch.cuda.empty_cache()
        # Hint the GC; safe even if model already released.
        import gc

        gc.collect()

    def trace(self, *, case_id: str, article_text: str) -> LogProbTrace:
        torch = self._torch
        encoded = self._tokenizer(
            article_text,
            return_tensors="pt",
            add_special_tokens=True,
        )
        input_ids = encoded["input_ids"].to(self._model.device)

        if input_ids.numel() < 2:
            raise OfflineHFBackendError(
                f"article {case_id} encodes to <2 tokens; cannot score"
            )

        forward_kwargs = dict(input_ids=input_ids, use_cache=False)
        if self.extract_hidden_states:
            forward_kwargs["output_hidden_states"] = True

        with torch.inference_mode():
            outputs = self._model(**forward_kwargs)
            logits = outputs.logits  # (1, T, V)
            log_probs = torch.log_softmax(logits, dim=-1)

        # The logprob of token i (i >= 1) is conditioned on tokens 0..i-1
        # and read from the model's prediction at position i-1. The first
        # token has no preceding context, so we skip it (matches vLLM's
        # echo=True behavior of returning None for token 0).
        targets = input_ids[0, 1:]
        gathered = (
            log_probs[0, :-1].gather(dim=-1, index=targets.unsqueeze(-1)).squeeze(-1)
        )
        token_logprobs = [float(x) for x in gathered.detach().cpu().tolist()]
        raw_token_ids = [int(x) for x in targets.detach().cpu().tolist()]

        # Top-K alternatives at each scored position. Full-vocab access
        # means we get the exact top-K (unlike vLLM's API approximation).
        top_alts: list[list[float]] = []
        if self.top_logprobs > 0:
            topk = log_probs[0, :-1].topk(
                k=min(self.top_logprobs, log_probs.shape[-1]), dim=-1
            )
            topk_vals = topk.values.detach().cpu().tolist()
            for row in topk_vals:
                top_alts.append([float(v) for v in row])

        if len(token_logprobs) != len(raw_token_ids):
            raise OfflineHFBackendError(
                "internal length mismatch between targets and logprobs"
            )

        # Optional hidden-state save (WS6 prep).
        hidden_uri: str | None = None
        if self.extract_hidden_states and outputs.hidden_states is not None:
            hidden_uri = self._save_hidden_states(case_id, outputs.hidden_states)

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

        # `prefix_token_count` for the *output* arrays: we already dropped
        # position 0, so any BOS at position 0 is gone. Remaining special
        # tokens (e.g. GLM's `<sop>` at position 1) get reported via
        # `prefix_token_count - 1` — but only if we still have some left.
        prefix_after_drop = max(0, self.prefix_token_count - 1)

        return LogProbTrace(
            case_id=case_id,
            model_id=self.model_id,
            tokenizer_family=self.tokenizer_family,
            tokenizer_sha=self.tokenizer_sha,
            hf_commit_sha=self.hf_commit_sha,
            quant_scheme=self.quant_scheme,
            weight_dtype=self.weight_dtype,
            vllm_image_digest=None,  # not applicable to HF backend
            article_token_count=len(token_logprobs),
            raw_token_ids=raw_token_ids,
            token_logprobs=token_logprobs,
            top_alternative_logprobs=top_alts,
            top_logprobs_k=self.top_logprobs,
            prefix_token_count=prefix_after_drop,
            hidden_states_uri=hidden_uri,
            thinking_mode="off",
            backend="offline_hf",
            fingerprint=fingerprint,
        )

    def _save_hidden_states(self, case_id: str, hidden_states) -> str:
        """Persist per-layer hidden states to `.safetensors` and return
        the URI written into the trace. Layout: keys ``layer_0`` .. ``layer_N``,
        each a tensor of shape `(seq_len, hidden_dim)`."""
        try:
            from safetensors.torch import save_file
        except ImportError as exc:  # pragma: no cover
            raise OfflineHFBackendError(
                "extract_hidden_states=True requires `safetensors` in the "
                "runtime environment"
            ) from exc

        assert self.hidden_states_dir is not None
        self.hidden_states_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.hidden_states_dir / f"{case_id}__{self.model_id}.safetensors"

        tensors = {}
        # `hidden_states` is a tuple of (n_layers + 1) tensors of shape
        # (1, seq_len, hidden_dim) — embeddings + each layer's output.
        for idx, hs in enumerate(hidden_states):
            tensors[f"layer_{idx}"] = hs[0].detach().to("cpu").contiguous()
        save_file(tensors, str(out_path))
        return str(out_path)


__all__ = ["OfflineHFBackend", "OfflineHFBackendError"]
