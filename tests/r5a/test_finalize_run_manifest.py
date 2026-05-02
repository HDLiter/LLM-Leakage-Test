"""Unit tests for scripts/ws1_finalize_run_manifest.py.

Per R2 Tier-0 Block F.35 (v3 simplified). Covers Block C hardening:
mode-aware 8-clause confirmatory hard-fail (decision #1), exposure-
horizon JSON validation, traces-dir validation, hidden-state subset
hash, quality_gate_thresholds key cleanup, sampling-config hash,
split-tier roster fields.

All tests use `tmp_path` and call `main()` after monkeypatching
`sys.argv`.
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

finalize = importlib.import_module("scripts.ws1_finalize_run_manifest")


# ----------------------------------------------------------------------
# Fixture builders
# ----------------------------------------------------------------------


_FLEET_DICT = {
    "fleet_version": "test-v1",
    "models": {
        "qwen2.5-7b": {
            "family": "qwen",
            "access": "white_box",
            "provider": "vllm",
            "cutoff_date": "2023-10-31",
            "cutoff_source": "vendor_stated",
            "tokenizer_family": "qwen",
            "hf_repo": "Qwen/Qwen2.5-7B-Instruct-AWQ",
            "quant_scheme": "AWQ-INT4",
            "tokenizer_sha": "a" * 64,
            "hf_commit_sha": "a" * 40,
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
            "cutoff_source": "operator_inferred",
            "tokenizer_family": "qwen3",
            "hf_repo": "Qwen/Qwen3-8B-AWQ",
            "quant_scheme": "AWQ-INT4",
            "tokenizer_sha": "b" * 64,
            "hf_commit_sha": "b" * 40,
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
            "cutoff_source": "community_paraphrase",
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
        }
    ],
}


_RUNTIME_DICT = {
    "runtime": {
        "timeout_seconds": 60,
        "retry_max": 3,
        "seed": 1234,
        "cache_enabled": True,
        "runstate_db": "data/run_state/test.sqlite",
    },
    "providers": {
        "vllm": {
            "max_concurrency": 16,
        },
        "deepseek": {
            "max_concurrency": 20,
        },
    },
}


def _write(tmp_path: Path, name: str, content: str | dict | list) -> Path:
    p = tmp_path / name
    if isinstance(content, str):
        p.write_text(content, encoding="utf-8")
    elif name.endswith((".yaml", ".yml")):
        p.write_text(yaml.safe_dump(content), encoding="utf-8")
    else:
        p.write_text(json.dumps(content), encoding="utf-8")
    return p


def _build_happy_fixture(tmp_path: Path) -> dict[str, Path]:
    """All 8 clauses satisfied. Returns a dict of paths/values to feed
    to the finalizer CLI."""
    fleet_path = _write(tmp_path, "fleet.yaml", _FLEET_DICT)
    runtime_path = _write(tmp_path, "runtime.yaml", _RUNTIME_DICT)

    article_manifest = _write(
        tmp_path, "article_manifest.json",
        [{"case_id": "c1", "text": "x", "target": "t", "target_type": "company",
          "publish_date": "2024-01-01", "event_type": "earnings",
          "host_category": "policy"}],
    )

    sampling_config = _write(tmp_path, "sampling.yaml", {"strategy": "stratified"})

    # exposure_horizon JSON: keys must equal P_logprob roster (qwen2.5-7b, qwen3-8b)
    exposure_horizon = _write(
        tmp_path, "horizon.json",
        {
            "summary": {
                "qwen2.5-7b": {
                    "horizon_observed": "2023-10-31",
                    "horizon_ci_lower": "2023-09-30",
                    "horizon_ci_upper": "2023-11-30",
                    "horizon_ci_width_months": 2,
                    "notes": "ok",
                },
                "qwen3-8b": {
                    "horizon_observed": None,
                    "notes": "rejected",
                },
            }
        },
    )

    # Traces dir with both expected models
    traces_dir = tmp_path / "traces"
    traces_dir.mkdir()
    (traces_dir / "qwen2.5-7b__pilot.parquet").write_bytes(b"PAR1")
    (traces_dir / "qwen3-8b__pilot.parquet").write_bytes(b"PAR1")

    # Hidden states with 30 cases per model (matches production default
    # for `_hidden_state_subset_hash`), identical case set per model.
    hs_dir = tmp_path / "hidden_states"
    hs_dir.mkdir()
    for i in range(30):
        case = f"case_{i:03d}"
        for mid in ("qwen2.5-7b", "qwen3-8b"):
            (hs_dir / f"{case}__{mid}.safetensors").write_bytes(b"HS")

    launch_env = _write(
        tmp_path, "launch_env.json",
        {"CUDA_VISIBLE_DEVICES": "0", "VLLM_VERSION": "0.9.0"},
    )

    output = tmp_path / "manifest.json"

    return {
        "fleet": fleet_path,
        "runtime": runtime_path,
        "article_manifest": article_manifest,
        "sampling_config": sampling_config,
        "exposure_horizon": exposure_horizon,
        "traces_dir": traces_dir,
        "hidden_states_dir": hs_dir,
        "launch_env": launch_env,
        "output": output,
    }


def _run_finalize(monkeypatch, fixture: dict[str, Path], **overrides) -> None:
    """Invoke `finalize.main()` against the fixture. Override individual
    args via kwargs (`mode='dev'` => add --allow-tbd; `omit=set()` to
    drop specific args). Returns None on success; pytest.raises catches
    SystemExit at the call site.
    """
    omit: set[str] = overrides.pop("omit", set())
    extra: list[str] = overrides.pop("extra", [])
    digest = overrides.pop("vllm_image_digest", "sha256:" + "f" * 64)
    gpu_dtype = overrides.pop("gpu_dtype", "bf16")
    args = [
        "ws1_finalize_run_manifest.py",
        "--fleet", str(fixture["fleet"]),
        "--runtime", str(fixture["runtime"]),
        "--article-manifest", str(fixture["article_manifest"]),
        "--sampling-config", str(fixture["sampling_config"]),
        "--traces-dir", str(fixture["traces_dir"]),
        "--exposure-horizon", str(fixture["exposure_horizon"]),
        "--hidden-states-dir", str(fixture["hidden_states_dir"]),
        "--launch-env", str(fixture["launch_env"]),
        "--output", str(fixture["output"]),
        "--run-id", "run-test",
    ]
    if "vllm_image_digest" not in omit and digest is not None:
        args.extend(["--vllm-image-digest", digest])
    if "gpu_dtype" not in omit and gpu_dtype is not None:
        args.extend(["--gpu-dtype", gpu_dtype])
    if "allow_tbd" in overrides and overrides["allow_tbd"]:
        args.append("--allow-tbd")
    args.extend(extra)
    monkeypatch.setattr(sys, "argv", args)
    finalize.main()


# ----------------------------------------------------------------------
# 8-clause hard-fail framework — 2 collapsed integration tests
# ----------------------------------------------------------------------


def test_finalize_confirmatory_lists_all_clause_violations(tmp_path: Path, monkeypatch):
    """Build a fixture that simultaneously violates every clause the
    multi-line `_confirmatory_hard_fail` framework owns and verify each
    failed clause is reported with its `[clause N]` prefix in a single
    SystemExit message.

    Notes on coverage: clauses 5 (exposure_horizon roster) and 6
    (traces-dir roster) are normally short-circuited inside
    `_read_exposure_horizon` and `_validate_traces_dir` BEFORE the
    framework runs, so they never reach the multi-line collector via
    `main()`. Helper-level coverage of those two short-circuits lives in
    `test_validate_traces_dir_confirmatory_lists_missing_and_extras` and
    `test_read_exposure_horizon_invalid_date_raises_in_confirmatory`.
    Here we exercise the six framework-owned clauses (1, 2, 3, 4, 7, 8)
    plus the sampling-config gate, all of which must coexist in one
    multi-line SystemExit per Decision #1's collect-and-report contract.
    """
    fixture = _build_happy_fixture(tmp_path)

    # Clause 1: force git_commit_sha to return all-zero.
    monkeypatch.setattr(finalize, "_git_commit_sha", lambda: "0" * 40)

    # Clauses 3 + 4: TBD on a P_logprob white-box and on a black-box.
    fleet_dict = json.loads(json.dumps(_FLEET_DICT))  # deep copy
    fleet_dict["models"]["qwen2.5-7b"]["tokenizer_sha"] = "<TBD>"
    fleet_dict["models"]["deepseek-v3"]["api_model_name"] = "<TBD>"
    fixture["fleet"].write_text(yaml.safe_dump(fleet_dict), encoding="utf-8")

    # Clause 7: launch_env missing CUDA_VISIBLE_DEVICES.
    fixture["launch_env"].write_text(
        json.dumps({"VLLM_VERSION": "0.9.0"}), encoding="utf-8"
    )

    with pytest.raises(SystemExit) as exc:
        _run_finalize(
            monkeypatch,
            fixture,
            # Clause 2: missing --vllm-image-digest.
            # Clause 8: missing --gpu-dtype.
            omit={"vllm_image_digest", "gpu_dtype"},
        )
    msg = str(exc.value)
    for n in (1, 2, 3, 4, 7, 8):
        assert f"[clause {n}]" in msg, f"missing [clause {n}] in: {msg}"
    # Multi-line: at least one newline between failures.
    assert msg.count("\n") >= 5


def test_finalize_confirmatory_happy_path_all_clauses_satisfied(tmp_path: Path, monkeypatch):
    fixture = _build_happy_fixture(tmp_path)
    # git_commit_sha must look real for clause 1.
    monkeypatch.setattr(finalize, "_git_commit_sha", lambda: "f" * 40)
    _run_finalize(monkeypatch, fixture)
    payload = json.loads(fixture["output"].read_text(encoding="utf-8"))
    assert payload["mode"] == "confirmatory"
    # Manifest reloads via Pydantic.
    from src.r5a.contracts import RunManifest

    RunManifest.model_validate(payload)


# ----------------------------------------------------------------------
# Mode behavior
# ----------------------------------------------------------------------


def test_finalize_dev_mode_skips_hard_fail(tmp_path: Path, monkeypatch):
    fixture = _build_happy_fixture(tmp_path)
    # Same simultaneous violations as integration #1, but --allow-tbd.
    monkeypatch.setattr(finalize, "_git_commit_sha", lambda: "0" * 40)
    fleet_dict = json.loads(json.dumps(_FLEET_DICT))
    fleet_dict["models"]["qwen2.5-7b"]["tokenizer_sha"] = "<TBD>"
    fleet_dict["models"]["deepseek-v3"]["api_model_name"] = "<TBD>"
    fixture["fleet"].write_text(yaml.safe_dump(fleet_dict), encoding="utf-8")
    # exposure_horizon partial (qwen3-8b missing) — dev tolerates.
    fixture["exposure_horizon"].write_text(
        json.dumps(
            {
                "summary": {
                    "qwen2.5-7b": {"horizon_observed": "2023-10-31", "notes": "ok"}
                }
            }
        ),
        encoding="utf-8",
    )
    (fixture["traces_dir"] / "qwen3-8b__pilot.parquet").unlink()
    fixture["launch_env"].write_text(json.dumps({}), encoding="utf-8")

    _run_finalize(
        monkeypatch,
        fixture,
        omit={"vllm_image_digest", "gpu_dtype"},
        allow_tbd=True,
    )
    payload = json.loads(fixture["output"].read_text(encoding="utf-8"))
    assert payload["mode"] == "dev"


# ----------------------------------------------------------------------
# Helper-level unit tests
# ----------------------------------------------------------------------


def test_validate_traces_dir_dev_tolerates_partial(tmp_path: Path):
    traces = tmp_path / "traces"
    traces.mkdir()
    (traces / "qwen2.5-7b__pilot.parquet").write_bytes(b"x")
    out = finalize._validate_traces_dir(
        traces, ["qwen2.5-7b", "qwen3-8b"], mode="dev"
    )
    assert "qwen2.5-7b" in out
    assert "qwen3-8b" not in out


def test_validate_traces_dir_confirmatory_lists_missing_and_extras(tmp_path: Path):
    traces = tmp_path / "traces"
    traces.mkdir()
    (traces / "qwen2.5-7b__pilot.parquet").write_bytes(b"x")
    (traces / "stranger__pilot.parquet").write_bytes(b"x")
    with pytest.raises(SystemExit) as exc:
        finalize._validate_traces_dir(
            traces, ["qwen2.5-7b", "qwen3-8b"], mode="confirmatory"
        )
    msg = str(exc.value)
    assert "missing:" in msg
    assert "qwen3-8b" in msg
    assert "stranger" in msg


def test_read_exposure_horizon_invalid_date_raises_in_confirmatory(tmp_path: Path):
    from src.r5a.fleet import load_fleet

    fleet_path = _write(tmp_path, "fleet.yaml", _FLEET_DICT)
    fleet = load_fleet(fleet_path)
    horizon_path = _write(
        tmp_path, "horizon.json",
        {
            "summary": {
                "qwen2.5-7b": {"horizon_observed": "not-a-date", "notes": "ok"},
                "qwen3-8b": {"horizon_observed": None, "notes": "rejected"},
            }
        },
    )
    with pytest.raises(SystemExit) as exc:
        finalize._read_exposure_horizon(horizon_path, fleet, mode="confirmatory")
    assert "qwen2.5-7b" in str(exc.value)


# ----------------------------------------------------------------------
# Hidden-state hash fixture
# ----------------------------------------------------------------------


def test_finalize_hidden_state_subset_hash_fixture_two_models(tmp_path: Path):
    hs_dir = tmp_path / "hs"
    hs_dir.mkdir()
    cases = [f"case_{i:03d}" for i in range(30)]
    for case in cases:
        for mid in ("m1", "m2"):
            (hs_dir / f"{case}__{mid}.safetensors").write_bytes(b"HS")
    h, n = finalize._hidden_state_subset_hash(
        hs_dir, ["m1", "m2"], expected_case_count=30, mode="confirmatory"
    )
    assert n == 30
    assert h is not None and len(h) == 64
    # Hash must be stable across runs.
    h2, _ = finalize._hidden_state_subset_hash(
        hs_dir, ["m1", "m2"], expected_case_count=30, mode="confirmatory"
    )
    assert h == h2


# ----------------------------------------------------------------------
# Threshold dict + roster + sampling-config
# ----------------------------------------------------------------------


def test_finalize_quality_gate_thresholds_actual_fleet():
    out = finalize._quality_gate_thresholds(n_p_predict=14, n_p_logprob=12)
    expected_keys = {
        "e_extract_main_text_promotion_n_p_predict",
        "e_extract_main_text_threshold",
        "e_extract_confirmatory_promotion_n_p_predict",
        "e_extract_confirmatory_threshold",
        "e_or_e_noop_informational_n_p_predict",
        "e_or_e_noop_informational_threshold",
    }
    assert set(out) == expected_keys
    # No legacy `e_fo_*` keys; no WS6 keys; no realized-N keys.
    for k in out:
        assert not k.startswith("e_fo_")
        assert not k.startswith("ws6_")
        assert "realized_n" not in k
    assert out["e_extract_main_text_promotion_n_p_predict"] == 14
    assert out["e_extract_main_text_threshold"] == finalize._one_third_minimum(14)
    assert out["e_extract_confirmatory_threshold"] == finalize._strict_majority(14)
    assert out["e_or_e_noop_informational_threshold"] == finalize._strict_majority(14)


def test_finalize_roster_fields_match_fleet(tmp_path: Path, monkeypatch):
    fixture = _build_happy_fixture(tmp_path)
    monkeypatch.setattr(finalize, "_git_commit_sha", lambda: "f" * 40)
    _run_finalize(monkeypatch, fixture)
    payload = json.loads(fixture["output"].read_text(encoding="utf-8"))
    from src.r5a.fleet import load_fleet

    fleet = load_fleet(fixture["fleet"])
    assert payload["fleet_p_predict_eligible"] == fleet.p_predict_eligible_ids()
    assert payload["fleet_p_logprob_eligible"] == fleet.p_logprob_eligible_ids()


def test_finalize_sampling_config_hash_separate_from_article(tmp_path: Path, monkeypatch):
    fixture = _build_happy_fixture(tmp_path)
    monkeypatch.setattr(finalize, "_git_commit_sha", lambda: "f" * 40)
    _run_finalize(monkeypatch, fixture)
    payload = json.loads(fixture["output"].read_text(encoding="utf-8"))
    assert payload["sampling_config_hash"] != payload["article_manifest_hash"]
    # Sampling-config hash is the SHA-256 of the sampling YAML file.
    assert payload["sampling_config_hash"] == finalize._sha256_file(fixture["sampling_config"])
