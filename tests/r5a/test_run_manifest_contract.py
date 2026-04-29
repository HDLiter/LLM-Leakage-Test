"""Pin RunManifest field set per DECISION_20260427 §3.2 +
DECISION_20260429_gate_removal §2.6 + DECISION_20260429_llama_addition §3.2.

A confirmatory cloud run with a manifest missing any of these fields is
non-reproducible (Tier-0 SYNTHESIS C7). The contract test fails loudly
if a future refactor drops one or removes `extra='forbid'`.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError

from src.r5a.contracts import RunManifest


REQUIRED_FIELDS = {
    # base provenance set
    "run_id",
    "created_at",
    "git_commit_sha",
    "fleet_config_hash",
    "runtime_config_hash",
    "sampling_config_hash",
    "prompt_versions",
    "model_fingerprints",
    "white_box_checkpoint_shas",
    "runtime_caps",
    "seed_policy",
    "runstate_db_path",
    "runstate_db_hash",
    "article_manifest_hash",
    "perturbation_manifest_hash",
    "audit_manifest_hash",
    # plan §10.1 operational provenance (added 2026-04-29)
    "tokenizer_shas",
    "vllm_image_digest",
    "gpu_dtype",
    "launch_env",
    # DECISION_20260427 §3.2 four-field set
    "cutoff_observed",
    "cutoff_date_yaml",
    "quant_scheme",
    "pcsg_pair_registry_hash",
    # DECISION_20260429 additions
    "hidden_state_subset_hash",
    "quality_gate_thresholds",
}


def _baseline_kwargs() -> dict:
    return dict(
        run_id="run-test",
        created_at=datetime.now(timezone.utc),
        git_commit_sha="0" * 40,
        fleet_config_hash="f" * 64,
        runtime_config_hash="r" * 64,
        sampling_config_hash="s" * 64,
        prompt_versions={"p_predict": "v1"},
        model_fingerprints={"qwen2.5-7b": {"system_fingerprint": "fp"}},
        white_box_checkpoint_shas={"qwen2.5-7b": "abcd1234"},
        runtime_caps={"vllm": 16},
        seed_policy={"strategy": "fixed", "seed": 1234},
        runstate_db_path="data/run_state/test.sqlite",
        article_manifest_hash="a" * 64,
    )


def test_run_manifest_field_coverage():
    fields = set(RunManifest.model_fields.keys())
    missing = REQUIRED_FIELDS - fields
    assert not missing, (
        f"RunManifest is missing required fields: {sorted(missing)}. "
        "These were pinned by DECISION_20260427 §3.2 / "
        "DECISION_20260429_gate_removal §2.6 / "
        "DECISION_20260429_llama_addition §3.2."
    )


def test_run_manifest_extra_forbid():
    # extra="forbid" must remain to catch silent typos in finalizer code.
    bad = {**_baseline_kwargs(), "this_field_does_not_exist": "oops"}
    with pytest.raises(ValidationError):
        RunManifest.model_validate(bad)


def test_run_manifest_minimum_construction():
    manifest = RunManifest(**_baseline_kwargs())
    # The 6 new fields default to empty containers / None.
    assert manifest.cutoff_observed == {}
    assert manifest.cutoff_date_yaml == {}
    assert manifest.quant_scheme == {}
    assert manifest.pcsg_pair_registry_hash is None
    assert manifest.hidden_state_subset_hash is None
    assert manifest.quality_gate_thresholds == {}
    assert manifest.tokenizer_shas == {}
    assert manifest.vllm_image_digest is None
    assert manifest.gpu_dtype is None
    assert manifest.launch_env == {}


def test_run_manifest_full_population():
    manifest = RunManifest(
        **_baseline_kwargs(),
        tokenizer_shas={"qwen2.5-7b": "tok-sha-1"},
        vllm_image_digest="sha256:deadbeef",
        gpu_dtype="bf16",
        launch_env={"CUDA_VISIBLE_DEVICES": "0", "VLLM_USE_V1": "1"},
        cutoff_observed={"qwen2.5-7b": date(2023, 10, 31), "glm-4-9b": None},
        cutoff_date_yaml={"qwen2.5-7b": date(2023, 10, 31)},
        quant_scheme={"qwen2.5-7b": "AWQ-INT4", "glm-4-9b": "fp16"},
        pcsg_pair_registry_hash="p" * 64,
        hidden_state_subset_hash="h" * 64,
        quality_gate_thresholds={
            "e_extract_main_text": 5,
            "e_extract_confirmatory": 8,
        },
    )
    assert manifest.cutoff_observed["glm-4-9b"] is None
    assert manifest.quant_scheme["qwen2.5-7b"] == "AWQ-INT4"
    assert manifest.quality_gate_thresholds["e_extract_main_text"] == 5
    assert manifest.gpu_dtype == "bf16"
