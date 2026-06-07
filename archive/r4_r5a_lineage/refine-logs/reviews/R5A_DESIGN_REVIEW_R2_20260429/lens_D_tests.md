---
title: Lens D — Test coverage and quality
date: 2026-04-29
review_id: R5A_DESIGN_REVIEW_R2_20260429
lens: D_tests
codex_thread_id: codex-local-20260429-lens-d
status: complete
---

# Lens D Verdict

The Tier-0 tests are useful smoke/contract coverage, but they are not yet a preregistration-grade test surface. The largest gap is that all three operational scripts added to close reproducibility and power-planning risks have zero tests. Those scripts are exactly where a silent bad manifest, bad YAML patch, or wrong planning anchor would survive.

The current tests mostly verify that expected happy-path objects can be built and that the main validators reject representative failures. They do not consistently pin exact field sets, JSON serialization semantics, exact CI outputs, CLI behavior, or edge-case invariants.

## High-risk untested paths (must add before pre-registration)

- `scripts/ws1_pin_fleet.py`: zero tests for the textual YAML patcher. Current code also silently ignores unknown `--pin-json` model IDs because `main()` iterates only `fleet.models` and never checks `overrides.keys() - fleet.models.keys()`.
- `scripts/ws1_finalize_run_manifest.py`: zero tests for the actual cloud-spend write path: `model_dump(mode="json")`, `json.dumps`, file write, read back, `RunManifest.model_validate`.
- `scripts/simulate_phase8_power.py`: zero tests for statistical anchors, including the PCSG SE anchor around `0.071`.
- `RunManifest` JSON date/null semantics: dates are constructed in memory, but the JSON path is not exercised.
- `LogProbTrace` integrity validators: direct rejection tests are missing for `prefix_token_count > article_token_count` and `top_alternative_logprobs` outer-length mismatch.

## Brittle / flaky test risks

- The cutoff tests are deterministic: synthetic data seeds are fixed and `detect_cutoff()` has a fixed default bootstrap seed. I do not see hidden cross-run randomness likely to flake in CI.
- The clean-step cutoff fixture has large safety margins. In the current run it returns CI width `0`, drop CI approximately `1.960..2.007`, and `p_drop_gt_005 = 1.0`, so `n_bootstrap=200` is not a practical flake risk there.
- `test_detect_cutoff_rejects_high_noise_wide_ci` is a soft rejection test. For the current fixture it rejects with CI width `8` and drop CI lower about `-0.565`, but the sampled point estimate is already wrong-direction (`drop_magnitude ~= -0.217`) despite the nominal true step. That means the test does not isolate "wide CI despite true step"; it mostly proves that this particular noisy sample is rejected.

## Findings A.1-A.15 (existing test quality)

1. `test_run_manifest_field_coverage()` does not truly pin the field set. Current `RunManifest` fields are:
   `run_id`, `created_at`, `git_commit_sha`, `fleet_config_hash`, `runtime_config_hash`, `sampling_config_hash`, `prompt_versions`, `model_fingerprints`, `white_box_checkpoint_shas`, `runtime_caps`, `seed_policy`, `runstate_db_path`, `runstate_db_hash`, `article_manifest_hash`, `perturbation_manifest_hash`, `audit_manifest_hash`, `tokenizer_shas`, `vllm_image_digest`, `gpu_dtype`, `launch_env`, `cutoff_observed`, `cutoff_date_yaml`, `quant_scheme`, `pcsg_pair_registry_hash`, `hidden_state_subset_hash`, `quality_gate_thresholds`. There is no current drift versus `REQUIRED_FIELDS`, but the test only checks `REQUIRED_FIELDS - fields`; future extra fields would pass.
2. `test_run_manifest_extra_forbid()` exercises `extra="forbid"` today, but it could pass spuriously because it only expects any `ValidationError`. If `_baseline_kwargs()` becomes invalid for another reason, or a future required field is added, the test can pass without proving the extra key was rejected.
3. The run-manifest tests do not exercise the production JSON path used by `ws1_finalize_run_manifest.py`: `manifest.model_dump(mode="json")`, `json.dumps`, `json.loads`, then `RunManifest.model_validate`.
4. `cutoff_observed: dict[str, date | None]` is not explicitly JSON round-tripped. The test constructs `date(2023, 10, 31)` and `None` in memory, then asserts only in-memory values.
5. The fleet rejection tests for unknown member, duplicate pair ID, and non-`p_logprob` member do assert message content. The role-shape tests (`temporal` with `members`, `capacity` without `members`) use bare `pytest.raises(Exception)` and could pass on unrelated validation failures.
6. Empty `pcsg_pairs` is not covered. There is no test that `capacity_pairs()` and `temporal_pairs()` return empty lists or that the registry hash is well-defined for `[]`.
7. Two capacity pairs that reference the same member set are not covered. The current validator permits this; if duplicate capacity sets would double-count analysis rows, it needs a failing test and implementation change.
8. `pcsg_pair_registry_hash()` is not tested across noisy YAML formatting. The current test writes the same Python dict twice; it does not prove comments, spacing, indentation style, or pair order are irrelevant.
9. `test_detect_cutoff_accepts_clean_step()` does not assert exact CI bounds. It asserts CI fields are populated and threshold-compliant.
10. The exact boundary where `n_months == 2 * min_side - 1` is not covered. The current "too few months" test uses `8` months with `min_side=6`; the boundary is `11`.
11. The bootstrap-invalid guard is not covered. Public data cannot naturally produce empty bootstrap months once the point fit passed, so this path likely needs monkeypatch coverage of `_bootstrap_kappa()`.
12. The `aggregator` parameter is not exercised. All current calls use the default `median`.
13. The clean `noise_sd=0.05` acceptance test is bootstrap-stable under current fixed seeds and has wide margins. It is not flaky in practice, but it also does not pin exact CI behavior.
14. I did not find randomness-dependent assertions that should vary across CI runs. The only wall-clock use is `datetime.now()` in manifest fixtures, with no exact-time assertion.
15. The high-noise rejection fixture is mathematically weak as a detector-quality test. With `pre=-1.0`, `post=-1.3`, `noise_sd=0.5`, `n_per_month=8`, and seed `7`, the detector rejects, but the observed point fit is already wrong-direction. This is acceptable as a rejection smoke test, not as evidence the CI rule behaves correctly around a known true step.

## Findings B.16-B.20 (coverage gaps)

16. `scripts/ws1_pin_fleet.py` needs direct tests before use on a confirmatory fleet. Required coverage: patch one model's `<TBD>` values and leave others alone; reject unknown `--pin-json` model IDs; prove `--check` is read-only; validate patched YAML with `load_fleet`; prove `pcsg_pair_registry_hash()` is invariant when only `models:` keys change; prove idempotency on a second run. The unknown-override case currently appears to fail the desired contract.
17. `scripts/ws1_finalize_run_manifest.py` needs tests for the placeholder gate and `--allow-tbd`, the realized quality thresholds for the actual fleet (`8/14`, `5/14`, `7/12`), manifest write/read/validate round-trip, and `_hidden_state_subset_hash()` against a fixture directory.
18. `scripts/simulate_phase8_power.py` needs tests for `_se_pcsg_pair(2048, 2, 0.98, 4.5) ~= 0.071`, sensible CMMD SE monotonicity/inflation behavior, and `_wy_power()` at known anchor points.
19. `ModelConfig.participates_in_p_predict()` and `participates_in_p_logprob()` are only indirectly tested through eligibility-list methods. Add direct predicate tests for full-operator white-box, P_logprob-only white-box, and black-box P_predict-only entries.
20. `LogProbTrace` validator paths are not directly covered for `prefix_token_count > article_token_count` or `top_alternative_logprobs` outer-length mismatch. Existing tests cover valid serialization and backend alignment behavior, not these contract validators.

## Findings C.21-C.22 (runner ergonomics)

21. Root-level `conftest.py` globally inserts the repo root into `sys.path`. That makes `pytest tests/r5a` ergonomic, but it can mask packaging/import-path bugs because tests import `src.r5a.*` without installing the package. A `tests/conftest.py` would scope the side effect to tests; a `pyproject.toml` or editable install would be cleaner still. A collect-only check from repo root reports `rootdir: D:\GitRepos\LLM-Leakage-Test`; from `D:\GitRepos` with an absolute test path, pytest reports `rootdir: D:\GitRepos` but still collects the repo tests and loads the repo `conftest.py`.
22. `test_fleet_config.py` does not rely on cwd for the fleet path. `Path(__file__).resolve().parents[2]` resolves from `tests/r5a/test_fleet_config.py` to the repository root, then `config/fleet/r5a_fleet.yaml`.

## Suggested test additions (concrete, copy-pasteable test outlines)

```python
def test_run_manifest_exact_field_set():
    expected = REQUIRED_FIELDS
    actual = set(RunManifest.model_fields)
    assert actual == expected
```

```python
def test_run_manifest_extra_forbid_specific_error():
    bad = {**_baseline_kwargs(), "this_field_does_not_exist": "oops"}
    with pytest.raises(ValidationError) as exc_info:
        RunManifest.model_validate(bad)
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("this_field_does_not_exist",) for e in errors)
    assert any(e["type"] == "extra_forbidden" for e in errors)
```

```python
def test_run_manifest_json_roundtrip_preserves_cutoff_dates():
    manifest = RunManifest(**_baseline_kwargs(), cutoff_observed={"a": date(2023, 10, 31), "b": None})
    payload = manifest.model_dump(mode="json")
    encoded = json.dumps(payload, sort_keys=True)
    loaded = RunManifest.model_validate(json.loads(encoded))
    assert payload["cutoff_observed"] == {"a": "2023-10-31", "b": None}
    assert loaded.cutoff_observed == {"a": date(2023, 10, 31), "b": None}
```

```python
def test_pcsg_pairs_empty_lists_and_hash(tmp_path):
    payload = _base_yaml()
    payload["pcsg_pairs"] = []
    fleet = _write_and_load(tmp_path, payload)
    assert fleet.temporal_pairs() == []
    assert fleet.capacity_pairs() == []
    assert len(fleet.pcsg_pair_registry_hash()) == 64
```

```python
def test_capacity_pair_duplicate_member_set_rejected(tmp_path):
    payload = _base_yaml()
    members = ["qwen2.5-7b", "qwen3-8b"]
    payload["pcsg_pairs"] = [
        {"id": "cap_a", "role": "capacity", "members": members, "tokenizer_compat": "x", "max_token_id_inclusive": 10},
        {"id": "cap_b", "role": "capacity", "members": list(reversed(members)), "tokenizer_compat": "x", "max_token_id_inclusive": 10},
    ]
    with pytest.raises(ValidationError, match="duplicate.*capacity"):
        _write_and_load(tmp_path, payload)
```

```python
def test_pcsg_registry_hash_ignores_yaml_formatting(tmp_path):
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    a.write_text(YAML_WITH_COMMENTS_AND_BLOCK_LISTS, encoding="utf-8")
    b.write_text(SAME_PAIRS_DIFFERENT_SPACING_AND_ORDER, encoding="utf-8")
    assert load_fleet(a).pcsg_pair_registry_hash() == load_fleet(b).pcsg_pair_registry_hash()
```

```python
def test_role_shape_validation_messages(tmp_path):
    payload = _base_yaml()
    payload["pcsg_pairs"][0]["members"] = ["qwen2.5-7b", "qwen3-8b"]
    with pytest.raises(ValidationError, match="must not declare 'members'"):
        _write_and_load(tmp_path, payload)
```

```python
def test_detect_cutoff_clean_step_exact_ci_bounds():
    by_month = _make_step_series(24, 11, -1.0, -3.0, 20, 0.05, seed=42)
    est = detect_cutoff(by_month, model_id="qwen2.5-7b", n_bootstrap=200)
    assert est.cutoff_ci_lower == date(2023, 12, 31)
    assert est.cutoff_ci_upper == date(2023, 12, 31)
    assert est.cutoff_ci_width_months == 0
    assert est.drop_ci_lower == pytest.approx(1.9596, abs=1e-3)
```

```python
def test_detect_cutoff_min_side_exact_boundary_rejected():
    by_month = _make_step_series(11, 5, -1.0, -2.0, 3, 0.01, seed=1)
    est = detect_cutoff(by_month, model_id="m", min_side=6)
    assert est.cutoff_observed is None
    assert est.kappa_hat_index is None
    assert "need at least 12" in est.notes
```

```python
def test_detect_cutoff_bootstrap_invalid_guard(monkeypatch):
    by_month = _make_step_series(12, 5, -1.0, -2.0, 5, 0.01, seed=1)
    monkeypatch.setattr(cutoff_probe, "_bootstrap_kappa", lambda *a, **k: (np.full(100, -1), np.zeros(100)))
    est = cutoff_probe.detect_cutoff(by_month, model_id="m", n_bootstrap=100)
    assert est.cutoff_observed is None
    assert est.drop_ci_lower is None
    assert "bootstrap valid in 0/100" in est.notes
```

```python
def test_detect_cutoff_aggregator_mean_vs_median():
    by_month = _make_step_series(14, 6, -1.0, -2.0, 7, 0.01, seed=1)
    by_month["2023-07"].extend([5.0, 5.0, 5.0])
    med = detect_cutoff(by_month, model_id="m", aggregator=median, n_bootstrap=100)
    avg = detect_cutoff(by_month, model_id="m", aggregator=mean, n_bootstrap=100)
    assert med.kappa_hat_index == 6
    assert avg.kappa_hat_index == 6
    assert med.drop_magnitude != pytest.approx(avg.drop_magnitude, abs=1e-3)
```

```python
def test_detect_cutoff_high_noise_rejection_is_pinned():
    by_month = _make_step_series(20, 9, -1.0, -1.3, 8, 0.5, seed=7)
    est = detect_cutoff(by_month, model_id="qwen2.5-7b", n_bootstrap=300, max_ci_width_months=3)
    assert est.cutoff_ci_width_months == 8
    assert est.drop_ci_lower == pytest.approx(-0.5653, abs=1e-3)
    assert est.cutoff_observed is None
```

```python
def test_patch_model_block_pins_only_target_model():
    text = FLEET_YAML_WITH_TWO_TBD_MODELS
    out, changes = _patch_model_block(text, "qwen2.5-7b", hf_commit_sha="hf1", tokenizer_sha="tok1")
    assert 'tokenizer_sha: "tok1"' in out
    assert 'hf_commit_sha: "hf1"' in out
    assert out.count("tokenizer_sha: <TBD>") == 1
    assert changes == ["qwen2.5-7b.tokenizer_sha: <TBD> -> tok1", "qwen2.5-7b.hf_commit_sha: <TBD> -> hf1"]
```

```python
def test_pin_json_unknown_model_is_rejected(tmp_path):
    fleet = tmp_path / "fleet.yaml"
    pin_json = tmp_path / "pins.json"
    fleet.write_text(MINIMAL_FLEET_YAML, encoding="utf-8")
    pin_json.write_text(json.dumps({"not-in-fleet": {"hf_commit_sha": "x"}}), encoding="utf-8")
    result = subprocess.run([sys.executable, "scripts/ws1_pin_fleet.py", "--fleet", str(fleet), "--pin-json", str(pin_json)], capture_output=True, text=True)
    assert result.returncode != 0
    assert "not-in-fleet" in result.stderr + result.stdout
```

```python
def test_pin_fleet_check_mode_does_not_write(tmp_path):
    fleet = tmp_path / "fleet.yaml"
    fleet.write_text(MINIMAL_FLEET_YAML, encoding="utf-8")
    before = fleet.read_text(encoding="utf-8")
    subprocess.run([sys.executable, "scripts/ws1_pin_fleet.py", "--fleet", str(fleet), "--check"], check=True)
    assert fleet.read_text(encoding="utf-8") == before
```

```python
def test_pin_fleet_validates_hash_invariant_and_idempotency(tmp_path):
    fleet_path = tmp_path / "fleet.yaml"
    fleet_path.write_text(MINIMAL_FLEET_YAML, encoding="utf-8")
    before_hash = load_fleet(fleet_path).pcsg_pair_registry_hash()
    run_pin_script(fleet_path, {"qwen2.5-7b": {"hf_commit_sha": "hf1", "tokenizer_sha": "tok1"}})
    once = fleet_path.read_text(encoding="utf-8")
    assert load_fleet(fleet_path).pcsg_pair_registry_hash() == before_hash
    run_pin_script(fleet_path, {"qwen2.5-7b": {"hf_commit_sha": "hf1", "tokenizer_sha": "tok1"}})
    assert fleet_path.read_text(encoding="utf-8") == once
```

```python
def test_finalize_quality_gate_thresholds_actual_fleet():
    fleet = load_fleet("config/fleet/r5a_fleet.yaml")
    thresholds = _quality_gate_thresholds(len(fleet.p_predict_eligible_ids()), len(fleet.p_logprob_eligible_ids()))
    assert thresholds["e_extract_confirmatory_promotion_n_p_predict"] == 14
    assert thresholds["e_extract_confirmatory_threshold"] == 8
    assert thresholds["e_extract_main_text_threshold"] == 5
    assert thresholds["ws6_mechanistic_n_white_box"] == 12
    assert thresholds["ws6_mechanistic_threshold"] == 7
```

```python
def test_finalize_hidden_state_subset_hash_fixture(tmp_path):
    model_dir = tmp_path / "hidden" / "qwen2.5-7b"
    model_dir.mkdir(parents=True)
    for case_id in ["case_b", "case_a", "case_c"]:
        (model_dir / f"{case_id}.safetensors").write_bytes(b"x")
    got, n = _hidden_state_subset_hash(tmp_path / "hidden")
    expected = hashlib.sha256("case_a\ncase_b\ncase_c".encode("utf-8")).hexdigest()
    assert (got, n) == (expected, 3)
```

```python
def test_finalize_manifest_file_roundtrip(tmp_path):
    out = tmp_path / "run_manifest.json"
    run_finalize_script_with_minimal_inputs(out, allow_tbd=True)
    payload = json.loads(out.read_text(encoding="utf-8"))
    manifest = RunManifest.model_validate(payload)
    assert manifest.pcsg_pair_registry_hash
    assert payload["cutoff_date_yaml"]
```

```python
def test_finalize_rejects_tbd_without_allow_tbd(tmp_path):
    out = tmp_path / "run_manifest.json"
    result = run_finalize_script_with_minimal_inputs(out, allow_tbd=False, check=False)
    assert result.returncode != 0
    assert "`<TBD>` placeholders" in result.stderr + result.stdout
```

```python
def test_phase8_pcsg_se_anchor():
    se = _se_pcsg_pair(n_case=2048, n_pairs=2, eligibility=0.98, sigma_pair_residual=4.5)
    assert se == pytest.approx(0.0710, abs=5e-4)
```

```python
def test_phase8_cmmd_se_shape():
    base = _se_with_family_intercepts(2560, 14, 1.0, 0.35, 0.20, 4)
    inflated = _se_with_family_intercepts(2560, 14, 1.0, 0.35 * 1.35, 0.20 * 1.35, 4)
    fewer_cases = _se_with_family_intercepts(430, 14, 1.0, 0.35, 0.20, 4)
    assert inflated > base
    assert fewer_cases >= base
```

```python
def test_phase8_wy_power_anchor_points():
    assert _wy_power(0.0, 1.0, z_wy=2.8) == pytest.approx(0.005110, abs=1e-6)
    assert _wy_power(0.2, 0.071, z_wy=2.8) == pytest.approx(0.5067, abs=1e-3)
    assert _wy_power(0.3, 0.071, z_wy=2.8) == pytest.approx(0.9230, abs=1e-3)
```

```python
def test_model_participation_predicates_direct(tmp_path):
    fleet = _write_and_load(tmp_path, payload_with_white_box_black_box_and_logprob_only())
    assert fleet.get("qwen2.5-7b").participates_in_p_predict()
    assert fleet.get("qwen2.5-7b").participates_in_p_logprob()
    assert not fleet.get("llama-3-8b-instruct").participates_in_p_predict()
    assert fleet.get("llama-3-8b-instruct").participates_in_p_logprob()
    assert not fleet.get("deepseek-v3").participates_in_p_logprob()
```

```python
def test_logprob_trace_rejects_prefix_longer_than_article():
    kwargs = valid_trace_kwargs(article_token_count=3, raw_token_ids=[1, 2, 3], token_logprobs=[-1, -2, -3])
    kwargs["prefix_token_count"] = 4
    with pytest.raises(ValidationError, match="prefix_token_count"):
        LogProbTrace(**kwargs)
```

```python
def test_logprob_trace_rejects_top_alt_outer_length_mismatch():
    kwargs = valid_trace_kwargs(article_token_count=3, raw_token_ids=[1, 2, 3], token_logprobs=[-1, -2, -3])
    kwargs["top_alternative_logprobs"] = [[-1.5], [-2.5]]
    kwargs["top_logprobs_k"] = 1
    with pytest.raises(ValidationError, match="top_alternative_logprobs"):
        LogProbTrace(**kwargs)
```

## Confidence

High. I read the requested test diff, the current implementation files, the unchanged existing tests, the root `conftest.py`, and the actual fleet YAML. I also ran pytest collection from repo root and from a parent cwd, and computed the current cutoff fixture outputs and power-simulation anchors without modifying source or tests.
