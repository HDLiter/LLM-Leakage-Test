"""Fleet config validation tests.

Per SYNTHESIS Coh#5 / Tier-0 #6: load_fleet must reject pcsg_pairs that
reference unknown models, declare duplicate pair ids, or point to a
non-P_logprob-eligible model. Also covers DECISION_20260429_llama_addition
§2.2 split-tier fleet (P_logprob-only models with `p_predict: null`).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from src.r5a.fleet import FleetConfig, load_fleet


REPO_ROOT = Path(__file__).resolve().parents[2]
FLEET_YAML = REPO_ROOT / "config" / "fleet" / "r5a_fleet.yaml"


def _base_yaml() -> dict:
    return {
        "fleet_version": "test-v1",
        "models": {
            "qwen2.5-7b": {
                "family": "qwen",
                "access": "white_box",
                "provider": "vllm",
                "cutoff_date": "2023-10-31",
                "tokenizer_family": "qwen",
                "hf_repo": "Qwen/Qwen2.5-7B-Instruct-AWQ",
                "quant_scheme": "AWQ-INT4",
                "p_logprob": {
                    "thinking_control": "default_off",
                    "prompt_overlay_policy": "none",
                    "route_lock_required": "hf_commit_sha",
                    "echo_supported": True,
                },
                "p_predict": {
                    "thinking_control": "default_deployed",
                    "prompt_overlay_policy": "baseline_only",
                },
            },
            "qwen3-8b": {
                "family": "qwen",
                "access": "white_box",
                "provider": "vllm",
                "cutoff_date": "2025-01-31",
                "tokenizer_family": "qwen3",
                "hf_repo": "Qwen/Qwen3-8B-AWQ",
                "quant_scheme": "AWQ-INT4",
                "p_logprob": {
                    "thinking_control": "append_no_think_sentinel",
                    "prompt_overlay_policy": "none",
                    "route_lock_required": "hf_commit_sha",
                    "echo_supported": True,
                },
                "p_predict": {
                    "thinking_control": "default_deployed",
                    "prompt_overlay_policy": "baseline_only",
                },
            },
            "deepseek-v3": {
                "family": "deepseek",
                "access": "black_box",
                "provider": "deepseek",
                "api_model_name": "deepseek-chat",
                "cutoff_date": "2024-07-31",
                "p_predict": {
                    "thinking_control": "default_deployed",
                    "prompt_overlay_policy": "baseline_only",
                    "route_lock_required": "provider_model_id",
                },
            },
        },
        "pcsg_pairs": [
            {
                "id": "temporal_qwen_cross_version",
                "role": "temporal",
                "early": "qwen2.5-7b",
                "late": "qwen3-8b",
                "tokenizer_compat": "qwen2_class",
                "max_token_id_inclusive": 151664,
            },
        ],
    }


def _write_and_load(tmp_path: Path, payload: dict) -> FleetConfig:
    p = tmp_path / "fleet.yaml"
    p.write_text(yaml.safe_dump(payload), encoding="utf-8")
    return load_fleet(p)


def test_loads_existing_repo_fleet():
    fleet = load_fleet(FLEET_YAML)
    assert fleet.fleet_version.startswith("r5a-")
    assert "qwen2.5-7b" in fleet.models
    assert len(fleet.temporal_pairs()) >= 1


def test_pcsg_pair_validator_rejects_unknown_member(tmp_path: Path):
    payload = _base_yaml()
    payload["pcsg_pairs"][0]["late"] = "model-that-does-not-exist"
    with pytest.raises(Exception) as exc_info:
        _write_and_load(tmp_path, payload)
    assert "unknown model" in str(exc_info.value).lower()


def test_pcsg_pair_validator_rejects_duplicate_id(tmp_path: Path):
    payload = _base_yaml()
    payload["pcsg_pairs"].append(dict(payload["pcsg_pairs"][0]))
    with pytest.raises(Exception) as exc_info:
        _write_and_load(tmp_path, payload)
    assert "duplicate" in str(exc_info.value).lower()


def test_pcsg_pair_validator_rejects_temporal_with_members(tmp_path: Path):
    payload = _base_yaml()
    payload["pcsg_pairs"][0]["members"] = ["qwen2.5-7b", "qwen3-8b"]
    with pytest.raises(Exception):
        _write_and_load(tmp_path, payload)


def test_pcsg_pair_validator_rejects_capacity_without_members(tmp_path: Path):
    payload = _base_yaml()
    payload["pcsg_pairs"] = [
        {
            "id": "capacity_only",
            "role": "capacity",
            "tokenizer_compat": "qwen2_class",
            "max_token_id_inclusive": 151664,
        }
    ]
    with pytest.raises(Exception):
        _write_and_load(tmp_path, payload)


def test_pcsg_pair_validator_rejects_black_box_member(tmp_path: Path):
    payload = _base_yaml()
    # deepseek-v3 is black-box, has no p_logprob block — must not be
    # accepted as a PCSG temporal-pair member.
    payload["pcsg_pairs"][0]["late"] = "deepseek-v3"
    with pytest.raises(Exception) as exc_info:
        _write_and_load(tmp_path, payload)
    assert "p_logprob" in str(exc_info.value).lower()


def test_p_logprob_only_model_supported(tmp_path: Path):
    """DECISION_20260429_llama_addition §2.2: a white-box model with
    `p_predict: null` (P_logprob-only role) must load without error and
    must be excluded from p_predict_eligible_ids."""
    payload = _base_yaml()
    payload["models"]["llama-3-8b-instruct"] = {
        "family": "llama",
        "access": "white_box",
        "provider": "vllm",
        "cutoff_date": "2023-03-01",
        "cutoff_source": "vendor_stated",
        "tokenizer_family": "llama3",
        "hf_repo": "meta-llama/Meta-Llama-3-8B-Instruct",
        "quant_scheme": "bf16",
        "p_logprob": {
            "thinking_control": "default_off",
            "prompt_overlay_policy": "none",
            "route_lock_required": "hf_commit_sha",
            "echo_supported": True,
        },
        # NOTE: no p_predict block; should be allowed as Optional now.
    }
    fleet = _write_and_load(tmp_path, payload)
    assert "llama-3-8b-instruct" in fleet.white_box_ids()
    assert "llama-3-8b-instruct" in fleet.p_logprob_eligible_ids()
    assert "llama-3-8b-instruct" not in fleet.p_predict_eligible_ids()


def test_pcsg_pair_registry_hash_stable(tmp_path: Path):
    fleet1 = _write_and_load(tmp_path, _base_yaml())
    fleet2 = _write_and_load(tmp_path, _base_yaml())
    assert fleet1.pcsg_pair_registry_hash() == fleet2.pcsg_pair_registry_hash()


def test_pcsg_pair_registry_hash_changes_on_pair_edit(tmp_path: Path):
    fleet1 = _write_and_load(tmp_path, _base_yaml())
    payload = _base_yaml()
    payload["pcsg_pairs"][0]["max_token_id_inclusive"] = 151000
    fleet2 = _write_and_load(tmp_path, payload)
    assert fleet1.pcsg_pair_registry_hash() != fleet2.pcsg_pair_registry_hash()
