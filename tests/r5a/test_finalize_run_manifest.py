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
import re
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


def _write_parquet(path: Path, n_rows: int) -> Path:
    """Write a tiny 1-column parquet with `n_rows` rows.

    Used by finalizer fixtures to satisfy the row-count gate
    (Tier-R2-0 PR1 step 4 / S5: pilot trace row count must equal
    article-manifest entry count, per model).
    """
    import pyarrow as pa
    import pyarrow.parquet as pq

    table = pa.table({"case_id": [f"case_{i:03d}" for i in range(n_rows)]})
    pq.write_table(table, str(path))
    return path


def _build_runstate_db(
    path: Path,
    *,
    statuses: list[str] | None = None,
    table_name: str = "request_runstate",
) -> Path:
    """Construct a minimal runstate sqlite with one row per status.

    Used by finalizer fixtures to satisfy / violate the runstate
    confirmatory clause (Tier-R2-0 PR1 step 7 / MED-2 / S2 forward-
    declared RUNSTATE_TABLE_NAME contract). When ``statuses`` is None,
    seeds two ``success`` rows so the gate passes; pass ``["pending"]``
    or ``["retryable"]`` to violate.
    """
    import sqlite3

    if statuses is None:
        statuses = ["success", "success"]
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(str(path))
    try:
        with conn:
            conn.execute(
                f"CREATE TABLE {table_name} ("
                "case_id TEXT, model_id TEXT, status TEXT)"
            )
            for i, st in enumerate(statuses):
                conn.execute(
                    f"INSERT INTO {table_name} (case_id, model_id, status) "
                    "VALUES (?, ?, ?)",
                    (f"c{i}", "qwen2.5-7b", st),
                )
    finally:
        conn.close()
    return path


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
            },
            # Path-E source-JSON shape gate (Tier-R2-0 PR1 step 5):
            # trace_shas roster must equal P_logprob fleet, values are
            # 64-hex SHA-256; probe_set_sha256 same shape.
            "trace_shas": {
                "qwen2.5-7b": "a" * 64,
                "qwen3-8b": "b" * 64,
            },
            "probe_set_sha256": "c" * 64,
        },
    )

    # Traces dir with both expected models. Row count must match the
    # 1-entry article manifest above (Tier-R2-0 PR1 row-count gate).
    traces_dir = tmp_path / "traces"
    traces_dir.mkdir()
    _write_parquet(traces_dir / "qwen2.5-7b__pilot.parquet", n_rows=1)
    _write_parquet(traces_dir / "qwen3-8b__pilot.parquet", n_rows=1)

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

    runstate_db = _build_runstate_db(tmp_path / "runstate.db")

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
        "runstate_db": runstate_db,
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
        "--launch-env", str(fixture["launch_env"]),
        "--runstate-db", str(fixture["runstate_db"]),
        "--output", str(fixture["output"]),
        "--run-id", "run-test",
    ]
    if "hidden_states_dir" not in omit:
        args.extend(["--hidden-states-dir", str(fixture["hidden_states_dir"])])
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
# 11-clause hard-fail framework — 2 collapsed integration tests
# ----------------------------------------------------------------------


def test_finalize_confirmatory_lists_all_clause_violations(tmp_path: Path, monkeypatch):
    """Build a fixture that simultaneously violates every clause the
    multi-line `_confirmatory_hard_fail` framework owns and verify each
    failed clause is reported with its `[clause N]` prefix in a single
    SystemExit message.

    Notes on coverage: clauses 6 (exposure_horizon roster) and 7
    (traces-dir roster) are normally short-circuited inside
    `_read_exposure_horizon` and `_validate_traces_dir` BEFORE the
    framework runs, so they never reach the multi-line collector via
    `main()`. Helper-level coverage of those two short-circuits lives in
    `test_validate_traces_dir_confirmatory_lists_missing_and_extras` and
    `test_read_exposure_horizon_invalid_date_raises_in_confirmatory`.
    Here we exercise the nine framework-owned clauses (1, 2, 3, 4, 5,
    8, 9, 10, 11), all of which must coexist in one multi-line
    SystemExit per Decision #1's collect-and-report contract.
    """
    fixture = _build_happy_fixture(tmp_path)

    # Clause 1: force git_commit_sha to return all-zero.
    monkeypatch.setattr(finalize, "_git_commit_sha", lambda: "0" * 40)

    # Clause 3: --sampling-config points at a non-existent path.
    fixture["sampling_config"].unlink()

    # Clauses 4 + 5: TBD on a P_logprob white-box and on a black-box.
    fleet_dict = json.loads(json.dumps(_FLEET_DICT))  # deep copy
    fleet_dict["models"]["qwen2.5-7b"]["tokenizer_sha"] = "<TBD>"
    fleet_dict["models"]["deepseek-v3"]["api_model_name"] = "<TBD>"
    fixture["fleet"].write_text(yaml.safe_dump(fleet_dict), encoding="utf-8")

    # Clause 8: launch_env missing CUDA_VISIBLE_DEVICES.
    fixture["launch_env"].write_text(
        json.dumps({"VLLM_VERSION": "0.9.0"}), encoding="utf-8"
    )

    # Clause 11: runstate.db has an orphan retryable row.
    _build_runstate_db(fixture["runstate_db"], statuses=["retryable"])

    with pytest.raises(SystemExit) as exc:
        _run_finalize(
            monkeypatch,
            fixture,
            # Clause 2: missing --vllm-image-digest.
            # Clause 9: missing --gpu-dtype.
            # Clause 10: missing --hidden-states-dir.
            omit={"vllm_image_digest", "gpu_dtype", "hidden_states_dir"},
        )
    msg = str(exc.value)
    for n in (1, 2, 3, 4, 5, 8, 9, 10, 11):
        assert f"[clause {n}]" in msg, f"missing [clause {n}] in: {msg}"
    # Multi-line: at least one newline between failures.
    assert msg.count("\n") >= 8


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
    # exposure_horizon partial (qwen3-8b missing summary) — dev tolerates,
    # but the Path-E shape gate (PR1 step 5) still requires trace_shas /
    # probe_set_sha256 with the full P_logprob roster regardless of mode.
    fixture["exposure_horizon"].write_text(
        json.dumps(
            {
                "summary": {
                    "qwen2.5-7b": {"horizon_observed": "2023-10-31", "notes": "ok"}
                },
                "trace_shas": {
                    "qwen2.5-7b": "a" * 64,
                    "qwen3-8b": "b" * 64,
                },
                "probe_set_sha256": "c" * 64,
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
            },
            "trace_shas": {
                "qwen2.5-7b": "a" * 64,
                "qwen3-8b": "b" * 64,
            },
            "probe_set_sha256": "c" * 64,
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


# ----------------------------------------------------------------------
# Analyzer -> finalizer end-to-end (Tier-R2-0 PR1 step 16 / MED-7)
# ----------------------------------------------------------------------


def _build_logprob_trace_parquet(
    path: Path, case_ids: list[str], model_id: str
) -> Path:
    """Write a minimal but real LogProbTrace parquet for one model.

    The shape is what `read_traces_parquet` consumes via `_row_to_trace`
    (see src/r5a/operators/p_logprob.py); short SHAs are tolerated here
    because LogProbTrace itself does not run the fleet-side pattern
    validator.
    """
    from datetime import datetime, timezone

    from src.r5a.contracts import LogProbTrace, RequestFingerprint, SeedSupport
    from src.r5a.operators.p_logprob import write_traces_parquet

    traces = []
    for cid in case_ids:
        traces.append(
            LogProbTrace(
                case_id=cid,
                model_id=model_id,
                tokenizer_family="qwen",
                tokenizer_sha="tok-x",
                hf_commit_sha="hf-x",
                quant_scheme="AWQ-INT4",
                article_token_count=4,
                raw_token_ids=[101, 102, 103, 104],
                token_logprobs=[-1.0, -1.5, -2.0, -2.5],
                thinking_mode="off",
                backend="vllm_completion",
                fingerprint=RequestFingerprint(
                    provider="vllm",
                    model_id=model_id,
                    ts=datetime.now(timezone.utc),
                    seed_supported=SeedSupport.YES,
                ),
            )
        )
    write_traces_parquet(traces, path)
    return path


def _e2e_fixture(tmp_path: Path) -> dict[str, Path]:
    """Build a fixture for the analyzer -> finalizer end-to-end test.

    Differs from `_build_happy_fixture` in two ways:
    - the article manifest doubles as the analyzer's `--probe-set`,
    - per-model trace parquets are real LogProbTrace files (not 1-row
      `case_id` placeholders) so the analyzer can read them.
    """
    fleet_path = _write(tmp_path, "fleet.yaml", _FLEET_DICT)
    runtime_path = _write(tmp_path, "runtime.yaml", _RUNTIME_DICT)

    case_ids = [f"c{i:02d}" for i in range(6)]
    article_records = [
        {
            "case_id": cid,
            "text": "x",
            "target": "t",
            "target_type": "company",
            "publish_date": "2024-01-01",
            "event_type": "earnings",
            "host_category": "policy",
        }
        for cid in case_ids
    ]
    article_manifest = _write(tmp_path, "article_manifest.json", article_records)
    sampling_config = _write(tmp_path, "sampling.yaml", {"strategy": "stratified"})

    traces_dir = tmp_path / "traces"
    traces_dir.mkdir()
    for mid in ("qwen2.5-7b", "qwen3-8b"):
        _build_logprob_trace_parquet(
            traces_dir / f"{mid}__pilot.parquet", case_ids, mid
        )

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
    runstate_db = _build_runstate_db(tmp_path / "runstate.db")
    horizon_path = tmp_path / "horizon.json"
    output = tmp_path / "manifest.json"

    return {
        "fleet": fleet_path,
        "runtime": runtime_path,
        "article_manifest": article_manifest,
        "sampling_config": sampling_config,
        "traces_dir": traces_dir,
        "hidden_states_dir": hs_dir,
        "launch_env": launch_env,
        "runstate_db": runstate_db,
        "exposure_horizon": horizon_path,
        "output": output,
    }


def _run_analyzer(monkeypatch, fixture: dict[str, Path]) -> None:
    """Invoke `run_exposure_horizon_analysis.main()` against the fixture."""
    analyzer = importlib.import_module("scripts.run_exposure_horizon_analysis")
    args = [
        "run_exposure_horizon_analysis.py",
        "--fleet", str(fixture["fleet"]),
        "--probe-set", str(fixture["article_manifest"]),
        "--traces-dir", str(fixture["traces_dir"]),
        "--trace-pattern", "{model}__pilot.parquet",
        "--output", str(fixture["exposure_horizon"]),
    ]
    monkeypatch.setattr(sys, "argv", args)
    rc = analyzer.main()
    assert rc == 0


def test_analyzer_finalizer_e2e_pins_path_e_provenance(tmp_path: Path, monkeypatch):
    """End-to-end: run the analyzer, feed its JSON to the finalizer,
    and assert the manifest's `exposure_horizon_source_sha256` equals
    the analyzer file's SHA-256 and that per-model `pilot_trace_shas`
    equal the on-disk parquet SHA-256s (Tier-R2-0 PR1 step 16; tightened
    equality assertions per IMPLEMENTATION_NOTE.md v3 / v4).
    """
    fixture = _e2e_fixture(tmp_path)
    monkeypatch.setattr(finalize, "_git_commit_sha", lambda: "f" * 40)

    _run_analyzer(monkeypatch, fixture)
    horizon_sha = finalize._sha256_file(fixture["exposure_horizon"])
    per_model_shas = {
        mid: finalize._sha256_file(
            fixture["traces_dir"] / f"{mid}__pilot.parquet"
        )
        for mid in ("qwen2.5-7b", "qwen3-8b")
    }

    _run_finalize(monkeypatch, fixture)
    payload = json.loads(fixture["output"].read_text(encoding="utf-8"))

    assert payload["exposure_horizon_source_sha256"] == horizon_sha
    assert payload["pilot_trace_shas"] == per_model_shas


def test_finalizer_rejects_analyzer_json_missing_trace_shas(tmp_path: Path, monkeypatch):
    """Negative test for the Path-E source-JSON shape gate (Tier-R2-0
    PR1 step 5): mutate the analyzer output to drop `trace_shas`,
    confirm the finalizer raises with a clear shape-verification
    message.
    """
    fixture = _e2e_fixture(tmp_path)
    monkeypatch.setattr(finalize, "_git_commit_sha", lambda: "f" * 40)
    _run_analyzer(monkeypatch, fixture)

    payload = json.loads(fixture["exposure_horizon"].read_text(encoding="utf-8"))
    payload.pop("trace_shas")
    fixture["exposure_horizon"].write_text(
        json.dumps(payload), encoding="utf-8"
    )

    with pytest.raises(SystemExit) as exc:
        _run_finalize(monkeypatch, fixture)
    msg = str(exc.value)
    assert "Path-E source JSON shape verification failed" in msg
    assert "trace_shas" in msg


def test_finalizer_rejects_analyzer_json_missing_probe_set_sha(tmp_path: Path, monkeypatch):
    """Mirror of the trace_shas negative: drop `probe_set_sha256`."""
    fixture = _e2e_fixture(tmp_path)
    monkeypatch.setattr(finalize, "_git_commit_sha", lambda: "f" * 40)
    _run_analyzer(monkeypatch, fixture)

    payload = json.loads(fixture["exposure_horizon"].read_text(encoding="utf-8"))
    payload.pop("probe_set_sha256")
    fixture["exposure_horizon"].write_text(
        json.dumps(payload), encoding="utf-8"
    )

    with pytest.raises(SystemExit) as exc:
        _run_finalize(monkeypatch, fixture)
    msg = str(exc.value)
    assert "probe_set_sha256" in msg


# ----------------------------------------------------------------------
# Path-E shape negatives (4 trace_shas + 2 probe_set_sha256)
# ----------------------------------------------------------------------


def _shape_fixture_for_validate(tmp_path: Path):
    from src.r5a.fleet import load_fleet

    fleet_path = _write(tmp_path, "fleet.yaml", _FLEET_DICT)
    return load_fleet(fleet_path), tmp_path / "horizon.json"


def _good_payload() -> dict:
    return {
        "summary": {
            "qwen2.5-7b": {"horizon_observed": "2023-10-31", "notes": "ok"},
            "qwen3-8b": {"horizon_observed": None, "notes": "rejected"},
        },
        "trace_shas": {
            "qwen2.5-7b": "a" * 64,
            "qwen3-8b": "b" * 64,
        },
        "probe_set_sha256": "c" * 64,
    }


def test_shape_gate_trace_shas_empty_dict(tmp_path: Path):
    fleet, path = _shape_fixture_for_validate(tmp_path)
    payload = _good_payload()
    payload["trace_shas"] = {}
    with pytest.raises(SystemExit) as exc:
        finalize._validate_exposure_horizon_payload(payload, path, fleet)
    assert "roster does not match" in str(exc.value)


def test_shape_gate_trace_shas_non_hex_value(tmp_path: Path):
    fleet, path = _shape_fixture_for_validate(tmp_path)
    payload = _good_payload()
    payload["trace_shas"]["qwen2.5-7b"] = "not-a-sha"
    with pytest.raises(SystemExit) as exc:
        finalize._validate_exposure_horizon_payload(payload, path, fleet)
    assert "lower-hex" in str(exc.value)


def test_shape_gate_trace_shas_roster_mismatch(tmp_path: Path):
    fleet, path = _shape_fixture_for_validate(tmp_path)
    payload = _good_payload()
    payload["trace_shas"] = {"stranger-7b": "a" * 64, "qwen3-8b": "b" * 64}
    with pytest.raises(SystemExit) as exc:
        finalize._validate_exposure_horizon_payload(payload, path, fleet)
    msg = str(exc.value)
    assert "roster does not match" in msg
    assert "stranger-7b" in msg


def test_shape_gate_probe_set_sha_non_hex(tmp_path: Path):
    fleet, path = _shape_fixture_for_validate(tmp_path)
    payload = _good_payload()
    payload["probe_set_sha256"] = "still-not-hex"
    with pytest.raises(SystemExit) as exc:
        finalize._validate_exposure_horizon_payload(payload, path, fleet)
    assert "probe_set_sha256" in str(exc.value)


# ----------------------------------------------------------------------
# Schema-strict horizon_observed key parse (#4 A / step 6)
# ----------------------------------------------------------------------


def test_read_exposure_horizon_missing_key_raises(tmp_path: Path):
    from src.r5a.fleet import load_fleet

    fleet_path = _write(tmp_path, "fleet.yaml", _FLEET_DICT)
    fleet = load_fleet(fleet_path)
    horizon_path = _write(
        tmp_path, "horizon.json",
        {
            "summary": {
                # `horizon_observed` is missing — distinct from null.
                "qwen2.5-7b": {"notes": "fitter never wrote the key"},
                "qwen3-8b": {"horizon_observed": None, "notes": "ok"},
            },
            "trace_shas": {
                "qwen2.5-7b": "a" * 64,
                "qwen3-8b": "b" * 64,
            },
            "probe_set_sha256": "c" * 64,
        },
    )
    with pytest.raises(SystemExit) as exc:
        finalize._read_exposure_horizon(horizon_path, fleet, mode="confirmatory")
    msg = str(exc.value)
    assert "horizon_observed" in msg
    assert "qwen2.5-7b" in msg


# ----------------------------------------------------------------------
# Pilot parquet row-count gate (#9 E / step 4)
# ----------------------------------------------------------------------


def test_validate_traces_dir_zero_byte_parquet_fails(tmp_path: Path):
    traces = tmp_path / "traces"
    traces.mkdir()
    (traces / "qwen2.5-7b__pilot.parquet").write_bytes(b"")
    _write_parquet(traces / "qwen3-8b__pilot.parquet", n_rows=1)
    with pytest.raises(SystemExit) as exc:
        finalize._validate_traces_dir(
            traces,
            ["qwen2.5-7b", "qwen3-8b"],
            mode="confirmatory",
            expected_n_articles=1,
        )
    assert "row count" in str(exc.value)
    assert "qwen2.5-7b" in str(exc.value)


def test_validate_traces_dir_wrong_row_count_fails(tmp_path: Path):
    traces = tmp_path / "traces"
    traces.mkdir()
    _write_parquet(traces / "qwen2.5-7b__pilot.parquet", n_rows=3)
    _write_parquet(traces / "qwen3-8b__pilot.parquet", n_rows=5)
    with pytest.raises(SystemExit) as exc:
        finalize._validate_traces_dir(
            traces,
            ["qwen2.5-7b", "qwen3-8b"],
            mode="confirmatory",
            expected_n_articles=5,
        )
    msg = str(exc.value)
    assert "row count 3" in msg
    assert "expected 5" in msg


# ----------------------------------------------------------------------
# Hidden-states + runstate clauses (helper-isolated)
# ----------------------------------------------------------------------


def test_confirmatory_hard_fail_hidden_states_dir_absent(tmp_path: Path, monkeypatch):
    fixture = _build_happy_fixture(tmp_path)
    monkeypatch.setattr(finalize, "_git_commit_sha", lambda: "f" * 40)
    with pytest.raises(SystemExit) as exc:
        _run_finalize(monkeypatch, fixture, omit={"hidden_states_dir"})
    assert "[clause 10]" in str(exc.value)
    assert "--hidden-states-dir" in str(exc.value)


def test_confirmatory_hard_fail_runstate_orphan_pending(tmp_path: Path, monkeypatch):
    fixture = _build_happy_fixture(tmp_path)
    monkeypatch.setattr(finalize, "_git_commit_sha", lambda: "f" * 40)
    _build_runstate_db(fixture["runstate_db"], statuses=["pending", "success"])
    with pytest.raises(SystemExit) as exc:
        _run_finalize(monkeypatch, fixture)
    msg = str(exc.value)
    assert "[clause 11]" in msg
    assert "orphan" in msg


# ----------------------------------------------------------------------
# Clause-number uniqueness (LOW-3 / step 7)
# ----------------------------------------------------------------------


def test_confirmatory_hard_fail_clause_numbers_are_dense_and_complete():
    """Static guard: the set of `[clause N]` numbers used in the
    production `_confirmatory_hard_fail` body is exactly the dense
    sequence {1..max}. Catches both a future copy/paste collision
    where one number serves two distinct gates (LOW-3 regression) and
    a renumbering gap that would silently retire a clause without
    updating the docstring count. Multiple literal occurrences of the
    SAME clause number are expected (e.g., one `[clause 4]` per
    placeholder field) and not penalized.
    """
    finalize_path = finalize.__file__
    assert finalize_path is not None
    src = Path(finalize_path).read_text(encoding="utf-8")
    body = src.split("def _confirmatory_hard_fail")[1].split("\ndef ")[0]
    matches = [int(n) for n in re.findall(r"\[clause (\d+)\]", body)]
    assert matches, "no [clause N] strings found in _confirmatory_hard_fail"
    seen = set(matches)
    assert seen == set(range(1, max(seen) + 1)), (
        f"clause-number set {sorted(seen)} is not the dense sequence "
        f"1..{max(seen)}; check _confirmatory_hard_fail for gaps "
        "(retired clause not removed from docstring count) or duplicates "
        "across distinct gates (LOW-3 regression)."
    )


# ----------------------------------------------------------------------
# RunManifest round-trip (PR1 step 3 fields populated)
# ----------------------------------------------------------------------


def test_run_manifest_round_trip_new_fields(tmp_path: Path, monkeypatch):
    fixture = _build_happy_fixture(tmp_path)
    monkeypatch.setattr(finalize, "_git_commit_sha", lambda: "f" * 40)
    _run_finalize(monkeypatch, fixture)
    payload = json.loads(fixture["output"].read_text(encoding="utf-8"))
    assert "exposure_horizon_source_sha256" in payload
    assert payload["exposure_horizon_source_sha256"] == finalize._sha256_file(
        fixture["exposure_horizon"]
    )
    assert payload["pilot_trace_shas"] == {
        "qwen2.5-7b": finalize._sha256_file(
            fixture["traces_dir"] / "qwen2.5-7b__pilot.parquet"
        ),
        "qwen3-8b": finalize._sha256_file(
            fixture["traces_dir"] / "qwen3-8b__pilot.parquet"
        ),
    }
    # Round-trip through the schema validator.
    from src.r5a.contracts import RunManifest

    manifest = RunManifest.model_validate(payload)
    assert manifest.exposure_horizon_source_sha256 == payload[
        "exposure_horizon_source_sha256"
    ]
    assert manifest.pilot_trace_shas == payload["pilot_trace_shas"]
