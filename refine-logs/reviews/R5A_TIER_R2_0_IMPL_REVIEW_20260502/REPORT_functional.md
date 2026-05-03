# Lens A — Functional correctness (plan-vs-code consistency)

## Cold-read first impressions
The commit broadly lands the intended schema/CLI renames and the pinner/finalizer hardening, and `pytest tests/r5a -q` is green. The most fragile area is still `scripts/ws1_finalize_run_manifest.py`: it is now the cloud-spend gate, but some inputs are optional or helper-validated before the aggregate confirmatory collector runs.

The surprising part in the cold read is that hidden-state validation is strict only after `--hidden-states-dir` is supplied; omitting the flag leaves `hidden_state_subset_hash=None` even in confirmatory mode. The exposure-horizon reader also validates roster keys but not row schema strongly enough, so a stale pre-rename JSON can be accepted as "all horizons rejected." The trace directory is checked for coverage, but the plan's trace-content hash step does not appear to land in the manifest path.

## Novel findings
[HIGH] Confirmatory finalization can omit WS6 hidden states entirely. `hs_hash` starts as `(None, 0)`, `_hidden_state_subset_hash()` is called only when `args.hidden_states_dir` is truthy, and the manifest then records `hidden_state_subset_hash=hs_hash`; there is no confirmatory clause requiring the flag or rejecting the omitted directory. This allows a confirmatory manifest with no 12-model × 30-case hidden-state subset. `scripts/ws1_finalize_run_manifest.py:614`, `scripts/ws1_finalize_run_manifest.py:615`, `scripts/ws1_finalize_run_manifest.py:709`

[HIGH] A stale or malformed exposure-horizon JSON row can silently become a rejected horizon. `_read_exposure_horizon()` uses `row.get("horizon_observed")` and treats `None` as a valid rejected horizon, so an old analyzer output using `cutoff_observed` instead of `horizon_observed`, or a row missing the field, passes confirmatory validation as long as the model keys match. `scripts/ws1_finalize_run_manifest.py:254`, `scripts/ws1_finalize_run_manifest.py:255`, `scripts/ws1_finalize_run_manifest.py:256`

## Anchored findings
[HIGH] The confirmatory hard-fail path does not preserve the collect-and-report contract for clauses 5 and 6. `_validate_traces_dir()` raises immediately on missing/extra pilot traces, and `_read_exposure_horizon()` raises immediately on invalid dates or roster mismatch, both before `_confirmatory_hard_fail()` runs. That means normal clause-5/6 failures are not reported with `[clause 5]` / `[clause 6]` alongside other failures. `scripts/ws1_finalize_run_manifest.py:219`, `scripts/ws1_finalize_run_manifest.py:267`, `scripts/ws1_finalize_run_manifest.py:280`, `scripts/ws1_finalize_run_manifest.py:674`

[MED] Step C.10's trace SHA computation is not implemented in the finalizer path. The code validates `--traces-dir` and keeps only `model_id -> path`, then constructs `RunManifest` without hashing the realized pilot parquet files or recording those hashes. This leaves the manifest unable to bind the main trace contents even though C.10 explicitly called for per-trace SHA-256 computation. `scripts/ws1_finalize_run_manifest.py:610`, `scripts/ws1_finalize_run_manifest.py:684`

[LOW] The sampling-config existence failure is reported as `[clause 2]`, duplicating the vLLM image-digest clause rather than being a distinct or clearly mapped confirmatory condition. This weakens the required bracketed clause format as an operator/test contract. `scripts/ws1_finalize_run_manifest.py:540`, `scripts/ws1_finalize_run_manifest.py:543`, `scripts/ws1_finalize_run_manifest.py:545`

No finding: `_confirmatory_hard_fail()` itself contains clauses 1 through 8 with bracket prefixes for the checks it owns; the reachability/collection defect above is in the helper call ordering.

No finding: `_hidden_state_subset_hash(expected_case_count=30)` matches the documented 30-case Stage 2.7 subset; the correctness issue is that the production caller can skip the helper entirely.

No finding: `_atomic_write_text()` / `_atomic_write_json()` use same-directory temp files, file flush/fsync before `os.replace`, and `os.replace` is the right atomic replacement primitive on Windows for this scope. No `[CUT v3]` lock/sentinel implementation was found.

No finding: I did not find accidental implementation of the named `[CUT v3]` items: no file-lock/sentinel lock, no B.25 equality assertion, no canonical-JSON `_hash_strings`, no realized-N threshold keys, and no C.18 memo edits.

## Meta
The anchor list is directionally right, but it underweights the "optional argument bypass" class. For this finalizer, the highest-risk failures are not only bad helper internals; they are required artifacts that remain optional at the CLI layer and therefore never enter the confirmatory validation path.
