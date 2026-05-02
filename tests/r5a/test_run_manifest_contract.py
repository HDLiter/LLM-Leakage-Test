"""Pin RunManifest field set per DECISION_20260427 §3.2 +
DECISION_20260429_gate_removal §2.6 + DECISION_20260429_llama_addition §3.2 +
2026-04-30 R2 amendments
(refine-logs/reviews/R5A_DESIGN_REVIEW_R2_20260429/DECISIONS.md
decisions #1, #2, #5, #11).

A confirmatory cloud run with a manifest missing any of these fields is
non-reproducible (Tier-0 SYNTHESIS C7). The contract test fails loudly
if a future refactor drops one or removes `extra='forbid'`.
"""

from __future__ import annotations

import json
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
    # DECISION_20260427 §3.2 four-field set; cutoff_observed renamed to
    # exposure_horizon_observed by R2 decision #5
    "exposure_horizon_observed",
    "cutoff_date_yaml",
    "quant_scheme",
    "pcsg_pair_registry_hash",
    # DECISION_20260429 additions
    "hidden_state_subset_hash",
    "quality_gate_thresholds",
    # 2026-04-30 R2 additions (decisions #1, #2)
    "mode",
    "fleet_p_predict_eligible",
    "fleet_p_logprob_eligible",
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
        pcsg_pair_registry_hash="p" * 64,
    )


def test_run_manifest_field_coverage():
    fields = set(RunManifest.model_fields.keys())
    missing = REQUIRED_FIELDS - fields
    assert not missing, (
        f"RunManifest is missing required fields: {sorted(missing)}. "
        "These were pinned by DECISION_20260427 §3.2 / "
        "DECISION_20260429_gate_removal §2.6 / "
        "DECISION_20260429_llama_addition §3.2 / R2 DECISIONS.md."
    )


def test_run_manifest_field_set_pinned():
    """Two-way drift guard: catches both missing fields and un-pinned new
    fields. If a new field is added without updating REQUIRED_FIELDS, this
    test fails so the contract review is forced to happen.
    """
    assert set(RunManifest.model_fields) == REQUIRED_FIELDS


def test_run_manifest_extra_forbid():
    bad = {**_baseline_kwargs(), "this_field_does_not_exist": "oops"}
    with pytest.raises(ValidationError) as exc_info:
        RunManifest.model_validate(bad)
    errs = exc_info.value.errors()
    assert any(e["loc"] == ("this_field_does_not_exist",) for e in errs)
    assert any(e["type"] == "extra_forbidden" for e in errs)


def test_run_manifest_minimum_construction():
    manifest = RunManifest(**_baseline_kwargs())
    # The 6 new fields default to empty containers / None.
    assert manifest.exposure_horizon_observed == {}
    assert manifest.cutoff_date_yaml == {}
    assert manifest.quant_scheme == {}
    assert manifest.pcsg_pair_registry_hash == "p" * 64
    assert manifest.hidden_state_subset_hash is None
    assert manifest.quality_gate_thresholds == {}
    assert manifest.tokenizer_shas == {}
    assert manifest.vllm_image_digest is None
    assert manifest.gpu_dtype is None
    assert manifest.launch_env == {}
    # R2 additions
    assert manifest.mode == "confirmatory"
    assert manifest.fleet_p_predict_eligible == []
    assert manifest.fleet_p_logprob_eligible == []


def test_run_manifest_full_population():
    manifest = RunManifest(
        **_baseline_kwargs(),
        tokenizer_shas={"qwen2.5-7b": "tok-sha-1"},
        vllm_image_digest="sha256:deadbeef",
        gpu_dtype="bf16",
        launch_env={"CUDA_VISIBLE_DEVICES": "0", "VLLM_USE_V1": "1"},
        exposure_horizon_observed={"qwen2.5-7b": date(2023, 10, 31), "glm-4-9b": None},
        cutoff_date_yaml={"qwen2.5-7b": date(2023, 10, 31)},
        quant_scheme={"qwen2.5-7b": "AWQ-INT4", "glm-4-9b": "fp16"},
        hidden_state_subset_hash="h" * 64,
        quality_gate_thresholds={
            "e_extract_main_text": 5,
            "e_extract_confirmatory": 8,
        },
        mode="confirmatory",
        fleet_p_predict_eligible=["qwen2.5-7b", "deepseek-v3"],
        fleet_p_logprob_eligible=["qwen2.5-7b"],
    )
    assert manifest.exposure_horizon_observed["glm-4-9b"] is None
    assert manifest.quant_scheme["qwen2.5-7b"] == "AWQ-INT4"
    assert manifest.quality_gate_thresholds["e_extract_main_text"] == 5
    assert manifest.gpu_dtype == "bf16"
    assert manifest.mode == "confirmatory"
    assert manifest.fleet_p_predict_eligible == ["qwen2.5-7b", "deepseek-v3"]
    assert manifest.fleet_p_logprob_eligible == ["qwen2.5-7b"]


def test_run_manifest_json_roundtrip_preserves_horizon_dates():
    m = RunManifest(
        **_baseline_kwargs(),
        exposure_horizon_observed={"a": date(2023, 10, 31), "b": None},
    )
    payload = m.model_dump(mode="json")
    reloaded = RunManifest.model_validate(json.loads(json.dumps(payload, sort_keys=True)))
    assert payload["exposure_horizon_observed"] == {"a": "2023-10-31", "b": None}
    assert reloaded.exposure_horizon_observed == {"a": date(2023, 10, 31), "b": None}
