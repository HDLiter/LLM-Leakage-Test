"""Fleet config loader.

Resolves `config/fleet/r5a_fleet.yaml` into typed per-model records.
This file is the *single source of truth* for per-model and per-operator
behavior (thinking control, route lock, echo support, fallback policy);
adapters must read from these records rather than re-deriving them.

Authority: plans/phase7-pilot-implementation.md §§5.1, 10.1, 14.2 (`A05`).
"""

from __future__ import annotations

import hashlib
from datetime import date
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

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
    api_model_name: str | None = None  # explicit string passed to the provider
    tokenizer_family: str | None = None
    tokenizer_sha: str | None = None
    hf_commit_sha: str | None = None
    p_logprob: PLogprobModelConfig | None = None
    p_predict: PPredictModelConfig

    def is_white_box(self) -> bool:
        return self.access is AccessTier.WHITE_BOX


class FleetConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fleet_version: str
    models: dict[str, ModelConfig]
    raw_yaml_sha256: str = Field(default="")  # populated by `load_fleet`

    def get(self, model_id: str) -> ModelConfig:
        if model_id not in self.models:
            raise KeyError(f"model_id {model_id!r} not in fleet {self.fleet_version}")
        return self.models[model_id]

    def white_box_ids(self) -> list[str]:
        return [mid for mid, m in self.models.items() if m.is_white_box()]

    def black_box_ids(self) -> list[str]:
        return [mid for mid, m in self.models.items() if not m.is_white_box()]


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
    "PLogprobModelConfig",
    "PPredictModelConfig",
    "load_fleet",
]
