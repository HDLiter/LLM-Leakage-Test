# Lens F — Role-rotation wildcard

## Roles selected
Selected **the cloud operator**, **the post-pilot analyst**, and **the data-recovery operator**. These are the most load-bearing because this commit hardens the midnight WS1 pin/finalize path, changes what the manifest preserves for later reproduction, and claims safer crash/recovery behavior around final artifacts.

## Findings by role

### Role 1: the cloud operator
[HIGH] `scripts/ws1_pin_fleet.py` can exit nonzero on a corrupt pinning log after already mutating the fleet YAML. The fleet is written at `scripts/ws1_pin_fleet.py:492`-`scripts/ws1_pin_fleet.py:493`, but the existing log is only parsed afterward at `scripts/ws1_pin_fleet.py:511`-`scripts/ws1_pin_fleet.py:518`; the operator sees a "corrupt log" failure while the fleet may already be changed.

[MED] The finalizer advertises a single multi-clause hard-fail framework, but roster checks still short-circuit before `_confirmatory_hard_fail` runs. Exposure-horizon roster mismatch raises at `scripts/ws1_finalize_run_manifest.py:275`-`scripts/ws1_finalize_run_manifest.py:288`, trace roster mismatch raises at `scripts/ws1_finalize_run_manifest.py:217`-`scripts/ws1_finalize_run_manifest.py:227`, and the collector is only called later at `scripts/ws1_finalize_run_manifest.py:674`-`scripts/ws1_finalize_run_manifest.py:682`.

[LOW] The hard-fail output reuses `[clause 2]` for a missing sampling config, even though clause 2 is already the vLLM image digest gate. The digest clause is at `scripts/ws1_finalize_run_manifest.py:466`-`scripts/ws1_finalize_run_manifest.py:476`, while the sampling-config failure is also emitted as `[clause 2]` at `scripts/ws1_finalize_run_manifest.py:540`-`scripts/ws1_finalize_run_manifest.py:548`.

### Role 2: the post-pilot analyst
[HIGH] The manifest validates the pilot trace roster but does not preserve trace file hashes or paths, so `run_manifest.json` plus git SHA is not enough to identify the exact main LogProbTrace inputs. The trace map is produced at `scripts/ws1_finalize_run_manifest.py:610`-`scripts/ws1_finalize_run_manifest.py:612` and used only in the hard-fail call at `scripts/ws1_finalize_run_manifest.py:674`-`scripts/ws1_finalize_run_manifest.py:682`; the `RunManifest` construction at `scripts/ws1_finalize_run_manifest.py:684`-`scripts/ws1_finalize_run_manifest.py:714` records no trace digest field.

[HIGH] The exposure-horizon analyzer writes source identity into its own JSON, but the final manifest drops that provenance and keeps only the derived horizon dates. `trace_shas` and `probe_set_sha256` are emitted at `scripts/run_exposure_horizon_analysis.py:214`-`scripts/run_exposure_horizon_analysis.py:218`, while the finalizer reads only summary lines at `scripts/ws1_finalize_run_manifest.py:587`-`scripts/ws1_finalize_run_manifest.py:594` and stores only `exposure_horizon_observed` at `scripts/ws1_finalize_run_manifest.py:705`.

[MED] Confirmatory manifests can be written with `hidden_state_subset_hash=null` if `--hidden-states-dir` is omitted. The hash is computed only inside the optional branch at `scripts/ws1_finalize_run_manifest.py:614`-`scripts/ws1_finalize_run_manifest.py:620`, `_confirmatory_hard_fail` does not receive or check that state at `scripts/ws1_finalize_run_manifest.py:674`-`scripts/ws1_finalize_run_manifest.py:682`, and the manifest writes the possibly-null value at `scripts/ws1_finalize_run_manifest.py:709`.

### Role 3: the data-recovery operator
[MED] Final manifest writes are not crash-safe and reruns are not naturally idempotent. A new `run_id` and `created_at` are generated at `scripts/ws1_finalize_run_manifest.py:684`-`scripts/ws1_finalize_run_manifest.py:686`, then the manifest is written directly with `write_text` at `scripts/ws1_finalize_run_manifest.py:716`-`scripts/ws1_finalize_run_manifest.py:722`; a crash mid-write can leave a partial JSON, and a rerun without `--run-id` creates a different manifest identity.

[MED] Pinning logs can claim requested values as `models_pinned` even when the YAML patcher skipped a conflicting already-pinned field. Conflicts are only appended as `SKIP` changes at `scripts/ws1_pin_fleet.py:358`-`scripts/ws1_pin_fleet.py:362`, but `pinned_records` is populated regardless at `scripts/ws1_pin_fleet.py:443`-`scripts/ws1_pin_fleet.py:447` and then written into the log at `scripts/ws1_pin_fleet.py:502`-`scripts/ws1_pin_fleet.py:508`.

## Cross-role patterns
The main structural pattern is that several paths validate or derive from artifacts without preserving enough artifact identity in the durable manifest. This shows up for pilot traces, exposure-horizon source traces/probe set, and hidden states.

A second pattern is write ordering: `ws1_pin_fleet.py` protects the YAML write itself but not the fleet+log transaction, while `ws1_finalize_run_manifest.py` writes the final JSON non-atomically.

## Meta
The role list fits this commit. The most load-bearing missing lens is not another persona, but an explicit "artifact bundle auditor" role focused on whether every manifest-derived value names the raw artifact that produced it.
