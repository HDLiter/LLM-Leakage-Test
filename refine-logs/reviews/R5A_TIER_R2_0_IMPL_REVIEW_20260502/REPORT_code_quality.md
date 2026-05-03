# Lens D — Code quality / Python idioms / hidden bugs

## Cold-read first impressions
The pinner is doing a lot of semantic work with text regexes, but the riskiest smell is not the inline lambda; it is quote/state normalization after the script writes quoted SHA values itself.

The finalizer's confirmatory mode reads like a hard-fail collector, but parts of the pipeline still fail before the collector runs, so the "show all clauses" contract is only partially true. I also stopped on hidden-state handling: the validator is strict only after a directory is supplied, while confirmatory `main()` can omit the argument entirely.

The planning calculator is mostly straightforward closed-form code. Its row schema is intentionally heterogeneous, but there is some rename residue around `fo_eligibility` after the E_OR rename.

## Novel findings
[HIGH] `scripts/ws1_finalize_run_manifest.py:614` Confirmatory finalization can omit `--hidden-states-dir` and still write a manifest with `hidden_state_subset_hash=None`. The strict `_hidden_state_subset_hash(..., mode="confirmatory")` path only runs under `if args.hidden_states_dir` at `scripts/ws1_finalize_run_manifest.py:615`, and the manifest records the unchecked `hs_hash` at `scripts/ws1_finalize_run_manifest.py:709`.

[MED] `scripts/ws1_finalize_run_manifest.py:588` The end-to-end hard-fail collector is bypassed for clause 5 and clause 6 failures. `_read_exposure_horizon` can raise before `_confirmatory_hard_fail` runs, `_validate_traces_dir` can do the same at `scripts/ws1_finalize_run_manifest.py:610`, and the collector is only called later at `scripts/ws1_finalize_run_manifest.py:674`.

[LOW] `scripts/ws1_pin_fleet.py:347` The pinner misclassifies its own quoted SHA output as a conflicting pre-existing value on rerun. `current` includes surrounding quotes, `current == new_value` at `scripts/ws1_pin_fleet.py:353` cannot match the value the script wrote at `scripts/ws1_pin_fleet.py:355`, so normal idempotent reruns produce `SKIP (already pinned...)` conflict messages.

[MED] `config/prompts/R5A_OPERATOR_SCHEMA.md:26` The current authoritative prompt schema still names `C_FO` / `E_FO`, while the code enum is now `C_CO` at `src/r5a/contracts.py:42` and the planning output labels E_OR. The table entry at `config/prompts/R5A_OPERATOR_SCHEMA.md:158` still maps `E_FO` to `C_FO`, which can drive stale artifact names into the new contract surface.

[LOW] `scripts/planning_power_calculator.py:392` The planning output row for `"E_OR_E_NoOp_beta_cutoff"` still emits `fo_eligibility`, with the loop variable also named `fo_eligibility` at `scripts/planning_power_calculator.py:358`. This is rename residue in a JSON-facing key.

## Anchored findings
No finding: `_patch_model_block`'s `field_re` lambda does not close over the loop variable; it takes `key` as an argument at `scripts/ws1_pin_fleet.py:331` and is called immediately with the current key at `scripts/ws1_pin_fleet.py:344`.

No finding: CRLF handling in the model-field regex is okay. The code strips only `\n` at `scripts/ws1_pin_fleet.py:340`, but the trailing `\r` is captured by the suffix group in the regex at `scripts/ws1_pin_fleet.py:332` and preserved when the replacement appends `\n` at `scripts/ws1_pin_fleet.py:356`.

No finding: `_atomic_write_text` avoids the classic Windows `NamedTemporaryFile` lock pitfall. The `mkstemp` fd is wrapped and closed before `os.replace` at `scripts/ws1_pin_fleet.py:265` and `scripts/ws1_pin_fleet.py:269`.

No finding: placeholder handling for `api_model_name=None` versus `"<TBD>"` is functionally consistent. Both are in `placeholder_set` at `scripts/ws1_finalize_run_manifest.py:480`, and black-box failures use the same clause-4 message path at `scripts/ws1_finalize_run_manifest.py:498`.

No finding on the specific hidden-state canonicalization anchor: expected-model case-set mismatches are caught by count and missing-canonical checks at `scripts/ws1_finalize_run_manifest.py:350` and `scripts/ws1_finalize_run_manifest.py:354`. The stronger issue is the omitted-argument path reported above.

No finding: I did not find a consumer parser that assumes `n_models` / `n_families` exist on every planning row. The only in-repo checks around the calculator are tests that accept the E_CMMD omission at `tests/r5a/test_planning_power_calculator.py:54`.

No actionable finding: broad `except Exception` uses in the touched code are cleanup or revalidation wrappers, not swallowed critical failures. The broadest new one re-raises as `SystemExit` before writing the fleet at `scripts/ws1_pin_fleet.py:486`.

No finding: no mutable default arguments surfaced in the changed Python paths; model container defaults use `Field(default_factory=...)`, e.g. `src/r5a/contracts.py:474`.

## Meta
The anchor list underweights contract drift outside Python modules. The stale `config/prompts/R5A_OPERATOR_SCHEMA.md` references are more likely to create future artifact incompatibility than the lambda/CRLF concerns. Tests pass locally: `87 passed in 3.25s`.
