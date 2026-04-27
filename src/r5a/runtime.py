"""Runtime config loader.

Provides typed access to provider concurrency caps, proxy policy, retry,
seed defaults, and runstate-db location. Plan §10.2 mandates explicit
`trust_env=False` and `proxy=None` for DeepSeek and local vLLM.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProviderRuntime(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_concurrency: int = Field(gt=0)
    trust_env: bool = False
    proxy: str | None = None  # "none" / null / explicit URL

    @field_validator("proxy", mode="before")
    @classmethod
    def _normalize_proxy_none(cls, value: object) -> object:
        """Allow YAML `proxy: none` / `proxy: null` / `proxy: ""` to mean
        "no proxy" (Python None) so adapters can pass it directly to
        httpx without further string handling."""
        if value is None:
            return None
        if isinstance(value, str) and value.lower() in {"none", "null", ""}:
            return None
        return value


class RuntimeBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")

    seed: int
    retry_max: int = Field(ge=0)
    timeout_seconds: int = Field(gt=0)
    cache_enabled: bool
    runstate_db: str


class RuntimeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    runtime: RuntimeBlock
    providers: dict[str, ProviderRuntime]
    raw_yaml_sha256: str = ""

    def provider(self, name: str) -> ProviderRuntime:
        if name not in self.providers:
            raise KeyError(f"runtime has no provider {name!r}")
        return self.providers[name]


def load_runtime(path: str | Path) -> RuntimeConfig:
    path = Path(path)
    raw_bytes = path.read_bytes()
    parsed = yaml.safe_load(raw_bytes)
    config = RuntimeConfig.model_validate(parsed)
    config = config.model_copy(
        update={"raw_yaml_sha256": hashlib.sha256(raw_bytes).hexdigest()}
    )
    return config


__all__ = [
    "ProviderRuntime",
    "RuntimeBlock",
    "RuntimeConfig",
    "load_runtime",
]
