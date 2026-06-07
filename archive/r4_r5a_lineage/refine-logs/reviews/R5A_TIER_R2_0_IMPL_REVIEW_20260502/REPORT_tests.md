# Lens B — Test adequacy

## Cold-read first impressions
The weakest tests are the ones whose names claim integration or invariants but only assert local symptoms: pin-fleet idempotency checks byte equality after two runs without asserting the first run actually pinned anything, and finalizer "all clauses" coverage exercises only the clauses that survive earlier helper short-circuits. Several fixtures are synthetic enough to miss producer/consumer drift: exposure-horizon JSON is hand-built rather than produced by the analyzer, hidden-state files are dummy names rather than backend output, and actual fleet cardinalities are mostly replaced by constants.

## Novel findings
[HIGH] `test_pin_fleet_validates_hash_invariant_and_idempotency` would still pass if the CLI ignored the valid `--pin-json` override entirely: it records bytes after run 1, runs again with the same explicit bump, and only asserts `first == second`, with no assertion that `<TBD>` was replaced, the requested SHAs landed, or the version changed. tests/r5a/test_pin_fleet.py:161, tests/r5a/test_pin_fleet.py:179

[HIGH] Malformed pin override SHAs are untested and appear structurally admissible: the pinner only rejects unknown model IDs, then passes arbitrary `hf_commit_sha` / `tokenizer_sha` strings into the patcher; `ModelConfig` types both as plain `str | None`, and finalizer clause 3 only rejects placeholders. scripts/ws1_pin_fleet.py:397, scripts/ws1_pin_fleet.py:421, src/r5a/fleet.py:64, scripts/ws1_finalize_run_manifest.py:480

[MED] `month_stratified_mink` can regress around score computation without failing tests: the only direct test asserts grouped month keys and counts, not the Min-K% values, while detector tests bypass `LogProbTrace` conversion by feeding synthetic `by_month` dicts directly. tests/r5a/test_exposure_horizon.py:88, tests/r5a/test_exposure_horizon.py:94

[MED] Analyzer-to-finalizer JSON contract is not tested end-to-end. The analyzer writes `summary[*].horizon_observed` and related keys, but finalizer tests use a hand-built JSON fixture, so a producer key drift would not be caught by the current finalizer or detector tests. scripts/run_exposure_horizon_analysis.py:186, tests/r5a/test_finalize_run_manifest.py:156

[MED] Hidden-state validation only has a happy-path synthetic filename fixture. The production code itself notes the fixture does not exercise the backend writer, and there are no negative tests for missing models, mismatched case sets, or writer/reader layout drift. scripts/ws1_finalize_run_manifest.py:302, tests/r5a/test_finalize_run_manifest.py:402, src/r5a/backends/offline_hf.py:260

[LOW] The "no MC SE in output rows" test checks only two of the four old CI key names: it would miss reintroduction of `power_pilot_ci95_high` or `power_main_ci95_low`. tests/r5a/test_planning_power_calculator.py:74

[MED] Actual fleet cardinalities are not pinned by tests. The finalizer threshold test calls `_quality_gate_thresholds(n_p_predict=14, n_p_logprob=12)` directly, while the existing repo-fleet smoke test only checks one model and `len(temporal_pairs()) >= 1`; a fleet roster regression could move thresholds without failing this suite. tests/r5a/test_finalize_run_manifest.py:426, tests/r5a/test_fleet_config.py:98

## Anchored findings
[MED] F.35 does not really cover the regression "the 8-clause framework degrades to fail-fast" for clauses 5/6. The integration test only asserts clauses `(1, 2, 3, 4, 7, 8)`, traces clause 6 is covered by a helper that raises before `_confirmatory_hard_fail`, and clause 5's helper test covers invalid date parsing rather than roster mismatch. tests/r5a/test_finalize_run_manifest.py:291, tests/r5a/test_finalize_run_manifest.py:363, tests/r5a/test_finalize_run_manifest.py:378, scripts/ws1_finalize_run_manifest.py:275

[MED] F.34 idempotency does not detect default timestamp auto-bump drift because both runs pass the same explicit `--bump-version`. A regression that always auto-bumps the default timestamp path would be masked by this test. tests/r5a/test_pin_fleet.py:166, tests/r5a/test_pin_fleet.py:175, scripts/ws1_pin_fleet.py:465

[LOW] F.36 numerical anchors are not a concern. Independent calculation matches the test anchors: `_se_pcsg_pair(2048, 2, 0.98, 4.5) ≈ 0.071027`, `_wy_power(0.2, 0.071, 2.8) ≈ 0.506742`, and `_wy_power(0.3, 0.071, 2.8) ≈ 0.922972`. tests/r5a/test_planning_power_calculator.py:26, tests/r5a/test_planning_power_calculator.py:59

[LOW] F.38's source-inspection test is brittle. It requires every `PCSGPair` field name to appear as a double-quoted literal in `FleetConfig.pcsg_pair_registry_hash`; a correct refactor using `model_dump`, a helper constant, or generated field coverage could fail this test despite preserving behavior. tests/r5a/test_fleet_config.py:221, src/r5a/fleet.py:148

[MED] B.24 explicit-revision happy path is untested. The suite verifies multi-snapshot rejection without `revision`, but not that `revision` selects the intended snapshot and hashes that snapshot's tokenizer. tests/r5a/test_pin_fleet.py:227, scripts/ws1_pin_fleet.py:196

[MED] C.12 sampling-config-missing is not tested alone. `_run_finalize` always includes `--sampling-config`, and the sampling test only verifies a successful hash; the confirmatory missing-file collection path is uncovered. tests/r5a/test_finalize_run_manifest.py:225, tests/r5a/test_finalize_run_manifest.py:460, scripts/ws1_finalize_run_manifest.py:543

[MED] Mock fixtures deviate from production structure in ways that matter for pinner coverage: the pin-fleet fixture has one white-box model and `pcsg_pairs: []`, so tests do not expose accidental cross-white-box block edits or PCSG/comment preservation drift in the real fleet shape. tests/r5a/test_pin_fleet.py:30

## Meta
[MED] The anchors focus on individual helper behavior, but the larger missing lens is artifact-contract coverage across CLIs: `ws1_run_logprob` output naming, `run_exposure_horizon_analysis` JSON, and `ws1_finalize_run_manifest` ingestion are tested as isolated assumptions rather than one producer/consumer chain. scripts/ws1_run_logprob.py:295, scripts/run_exposure_horizon_analysis.py:214, scripts/ws1_finalize_run_manifest.py:587
