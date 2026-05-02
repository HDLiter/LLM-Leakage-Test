"""Fleet config loader.

Resolves `config/fleet/r5a_fleet.yaml` into typed per-model records.
This file is the *single source of truth* for per-model and per-operator
behavior (thinking control, route lock, echo support, fallback policy);
adapters must read from these records rather than re-deriving them.

Authority: plans/phase7-pilot-implementation.md §§5.1, 10.1, 14.2 (`A05`).
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .contracts import AccessTier


class PLogprobModelConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    thinking_control: Literal[
        "default_off",
        "system_message_toggle",
        "append_no_think_sentinel",
    ]
    prompt_overlay_policy: Literal["none"]
    route_lock_required: Literal["hf_commit_sha"]
    echo_supported: bool
    fallback: Literal["offline_hf_scorer"] | None = None


class PPredictModelConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    thinking_control: Literal["default_deployed", "extended_thinking_off"]
    prompt_overlay_policy: Literal["baseline_only"]
    route_lock_required: Literal["hf_commit_sha", "provider_model_id"] | None = None


class ModelConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_id: str
    family: str
    access: AccessTier
    provider: str
    cutoff_date: date
    cutoff_source: Literal[
        "vendor_stated",
        "community_paraphrase",
        "operator_inferred",
    ] = "operator_inferred"
    api_model_name: str | None = None  # explicit string passed to the provider
    hf_repo: str | None = None  # for white-box; resolved by huggingface-cli download
    quant_scheme: Literal["fp16", "bf16", "fp32", "AWQ-INT4", "GPTQ-INT4"] | None = None
    tokenizer_family: str | None = None
    tokenizer_sha: str | None = None
    hf_commit_sha: str | None = None
    p_logprob: PLogprobModelConfig | None = None
    # `p_predict` is Optional to express the P_logprob-only role
    # (DECISION_20260429_llama_addition §2.2): Llama-3 / Llama-3.1
    # entries omit `p_predict:` and are therefore excluded from
    # P_predict-driven estimands (E_CMMD, E_OR, E_NoOp, E_extract).
    p_predict: PPredictModelConfig | None = None

    def is_white_box(self) -> bool:
        return self.access is AccessTier.WHITE_BOX

    def participates_in_p_predict(self) -> bool:
        return self.p_predict is not None

    def participates_in_p_logprob(self) -> bool:
        return self.is_white_box() and self.p_logprob is not None


class PCSGPair(BaseModel):
    """One pair declaration for the PCSG analysis layer.

    `temporal` pairs identify cutoff-exposure differential (primary
    confirmatory PCSG signal). `capacity` pairs hold cutoff fixed and
    vary parameter count (exploratory PCSG_capacity_curve).
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    role: Literal["temporal", "capacity"]
    early: str | None = None  # required for `role=temporal`
    late: str | None = None   # required for `role=temporal`
    members: list[str] | None = None  # required for `role=capacity`
    tokenizer_compat: str  # e.g. "qwen2_class" — backend-validated label
    max_token_id_inclusive: int  # any article tokenizing to ID > this is rejected


class FleetConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fleet_version: str
    models: dict[str, ModelConfig]
    pcsg_pairs: list[PCSGPair] = Field(default_factory=list)
    raw_yaml_sha256: str = Field(default="")  # populated by `load_fleet`

    def get(self, model_id: str) -> ModelConfig:
        if model_id not in self.models:
            raise KeyError(f"model_id {model_id!r} not in fleet {self.fleet_version}")
        return self.models[model_id]

    def white_box_ids(self) -> list[str]:
        return [mid for mid, m in self.models.items() if m.is_white_box()]

    def black_box_ids(self) -> list[str]:
        return [mid for mid, m in self.models.items() if not m.is_white_box()]

    def p_predict_eligible_ids(self) -> list[str]:
        """Models that participate in P_predict (and therefore in
        P_predict-derived estimands E_CMMD / E_OR / E_NoOp / E_extract).

        Per DECISION_20260429_llama_addition §2.2 Llama is `p_predict:
        null` and therefore excluded.
        """
        return [mid for mid, m in self.models.items() if m.participates_in_p_predict()]

    def p_logprob_eligible_ids(self) -> list[str]:
        """White-box models that produce token logprobs."""
        return [mid for mid, m in self.models.items() if m.participates_in_p_logprob()]

    def temporal_pairs(self) -> list[PCSGPair]:
        return [p for p in self.pcsg_pairs if p.role == "temporal"]

    def capacity_pairs(self) -> list[PCSGPair]:
        return [p for p in self.pcsg_pairs if p.role == "capacity"]

    def pcsg_pair_registry_hash(self) -> str:
        """SHA256 of the canonicalized `pcsg_pairs` block.

        Pinning the pair registry separately from the whole-fleet hash
        means RunManifest can detect pair-set drift even if a non-pair
        edit (e.g. retiring a stale `<TBD>` placeholder) changed
        `fleet_config_hash`. Used by RunManifest.pcsg_pair_registry_hash.
        """
        canonical = [
            {
                "id": p.id,
                "role": p.role,
                "early": p.early,
                "late": p.late,
                "members": p.members,
                "tokenizer_compat": p.tokenizer_compat,
                "max_token_id_inclusive": p.max_token_id_inclusive,
            }
            for p in sorted(self.pcsg_pairs, key=lambda x: x.id)
        ]
        payload = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @model_validator(mode="after")
    def _validate_pcsg_pairs(self) -> "FleetConfig":
        """Per SYNTHESIS Coh#5 / Tier-0 #6: every `early`/`late`/`members`
        reference must resolve to a `models:` key, pair ids must be
        unique, and temporal pairs must point to P_logprob-eligible
        white-box models.
        """
        seen: set[str] = set()
        for pair in self.pcsg_pairs:
            if pair.id in seen:
                raise ValueError(f"duplicate PCSG pair id: {pair.id!r}")
            seen.add(pair.id)

            if pair.role == "temporal":
                if not pair.early or not pair.late:
                    raise ValueError(
                        f"PCSG temporal pair {pair.id!r} requires both 'early' and 'late'"
                    )
                if pair.members:
                    raise ValueError(
                        f"PCSG temporal pair {pair.id!r} must not declare 'members'"
                    )
                refs = [pair.early, pair.late]
            elif pair.role == "capacity":
                if pair.early or pair.late:
                    raise ValueError(
                        f"PCSG capacity pair {pair.id!r} must not declare 'early'/'late'"
                    )
                if not pair.members or len(pair.members) < 2:
                    raise ValueError(
                        f"PCSG capacity pair {pair.id!r} requires >=2 members"
                    )
                refs = list(pair.members)
            else:
                raise ValueError(f"PCSG pair {pair.id!r} has unknown role {pair.role!r}")

            if len(set(refs)) != len(refs):
                raise ValueError(
                    f"PCSG pair {pair.id!r} has duplicate members in {refs!r}; "
                    "members must be distinct"
                )

            for ref in refs:
                if ref not in self.models:
                    raise ValueError(
                        f"PCSG pair {pair.id!r} references unknown model {ref!r}; "
                        f"check `models:` keys in fleet YAML"
                    )
                m = self.models[ref]
                if not m.participates_in_p_logprob():
                    raise ValueError(
                        f"PCSG pair {pair.id!r} member {ref!r} is not P_logprob-eligible "
                        "(must be white-box with a `p_logprob:` block)"
                    )

        return self


def _normalize_models(raw: dict) -> dict:
    models = raw.get("models", {})
    normalized = {}
    for mid, body in models.items():
        body = dict(body)
        body.setdefault("model_id", mid)
        normalized[mid] = body
    return {**raw, "models": normalized}


def load_fleet(path: str | Path) -> FleetConfig:
    path = Path(path)
    raw_bytes = path.read_bytes()
    parsed = yaml.safe_load(raw_bytes)
    parsed = _normalize_models(parsed)
    config = FleetConfig.model_validate(parsed)
    config = config.model_copy(
        update={"raw_yaml_sha256": hashlib.sha256(raw_bytes).hexdigest()}
    )
    return config


__all__ = [
    "FleetConfig",
    "ModelConfig",
    "PCSGPair",
    "PLogprobModelConfig",
    "PPredictModelConfig",
    "load_fleet",
]
