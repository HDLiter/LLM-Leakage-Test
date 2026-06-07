# Lens C — Operational / cloud-spend safety

## Cold-read first impressions
The new gates mostly prove that expected filenames and roster keys exist; they do not prove that the files are readable, complete, current, or tied to the article/probe manifests that supposedly produced them.

The finalizer is the highest-risk step: it writes the trusted manifest after checking fleet placeholders, trace roster names, exposure-horizon keys, launch env, digest format, dtype, and sampling-config existence. The pinner is better about atomic writes, but pin-value validation is still mostly "non-placeholder".

Path-E now has separate file suffixes and directories, which reduces pilot/probe crossing. However, the analyzer emits useful provenance hashes that the finalizer discards before writing the RunManifest.

## Novel findings
[HIGH] Path-E provenance is detached from the RunManifest: `run_exposure_horizon_analysis.py` computes `trace_shas` and `probe_set_sha256`, but `ws1_finalize_run_manifest.py` reads only `summary[*].horizon_observed` and writes only `exposure_horizon_observed`, so a stale or regenerated horizon JSON with the same model keys can land as trusted without the trace/probe hashes that produced it. Cite: `scripts/run_exposure_horizon_analysis.py:214`, `scripts/run_exposure_horizon_analysis.py:217`, `scripts/ws1_finalize_run_manifest.py:250`, `scripts/ws1_finalize_run_manifest.py:705`.

[HIGH] Confirmatory finalization can omit hidden states entirely: `--hidden-states-dir` defaults to `None`, the hash helper is called only if the arg is present, and the manifest is then constructed with `hidden_state_subset_hash=None`. Cite: `scripts/ws1_finalize_run_manifest.py:106`, `scripts/ws1_finalize_run_manifest.py:614`, `scripts/ws1_finalize_run_manifest.py:709`.

[HIGH] Model pin values are not format-validated or coherence-checked: `hf_commit_sha` / `tokenizer_sha` are plain optional strings, `--pin-json` values flow into the patcher, and the confirmatory hard-fail only rejects `None`, empty, or `<TBD>`. A malformed commit string, or an override `hf_commit_sha` that disagrees with a `revision` used to read the tokenizer, can still become manifest provenance. Cite: `src/r5a/fleet.py:63`, `scripts/ws1_pin_fleet.py:421`, `scripts/ws1_pin_fleet.py:426`, `scripts/ws1_finalize_run_manifest.py:480`, `scripts/ws1_finalize_run_manifest.py:484`.

[MED] Path-E trace/probe mismatches can silently shrink the analysis set: `month_stratified_mink()` skips any trace whose `case_id` is absent from the probe fixture, and the analyzer proceeds to emit a summary without checking that all trace rows matched the fixture. Cite: `src/r5a/analysis/exposure_horizon.py:97`, `src/r5a/analysis/exposure_horizon.py:99`, `scripts/run_exposure_horizon_analysis.py:174`, `scripts/run_exposure_horizon_analysis.py:186`.

[MED] Confirmatory manifests can be written without runstate lineage: the finalizer hashes `runstate_db` only if the path exists and has no hard-fail clause for missing or non-terminal runstate state. Cite: `scripts/ws1_finalize_run_manifest.py:667`, `scripts/ws1_finalize_run_manifest.py:671`, `scripts/ws1_finalize_run_manifest.py:674`.

## Anchored findings
[HIGH] Corrupted HF cache is not rejected when files exist: the pinner trusts the snapshot directory name as `hf_commit_sha` and hashes whatever bytes are in `tokenizer.json`; it does not parse tokenizer JSON or validate snapshot SHA format. Cite: `scripts/ws1_pin_fleet.py:233`, `scripts/ws1_pin_fleet.py:237`, `scripts/ws1_pin_fleet.py:242`.

[HIGH] Half-written, corrupt, stale, or wrong-row-count pilot parquet can pass finalization: `_validate_traces_dir()` only globs `*__pilot.parquet` and maps filenames to model IDs; `_confirmatory_hard_fail()` only compares the resulting keys to the fleet roster. Cite: `scripts/ws1_finalize_run_manifest.py:206`, `scripts/ws1_finalize_run_manifest.py:229`, `scripts/ws1_finalize_run_manifest.py:515`.

[MED] Partial horizon JSON can pass if every roster key is present but rows are incomplete: missing `horizon_observed` is treated the same as an accepted rejected horizon (`None`), and confirmatory validation then checks only key coverage. Cite: `scripts/ws1_finalize_run_manifest.py:254`, `scripts/ws1_finalize_run_manifest.py:255`, `scripts/ws1_finalize_run_manifest.py:275`.

[LOW] Wrong vLLM image digest format is rejected in the pinner and finalizer; this anchor is not a silent-pass concern. Cite: `scripts/ws1_pin_fleet.py:385`, `scripts/ws1_finalize_run_manifest.py:472`.

[LOW] A mistyped `--allow_tbd` does not skip confirmatory mode because argparse defines only `--allow-tbd`; unknown flags are rejected before manifest construction. Cite: `scripts/ws1_finalize_run_manifest.py:137`, `scripts/ws1_finalize_run_manifest.py:146`.

[LOW] Missing `--sampling-config` in confirmatory mode does not land with `sampling_config_hash=""`; the empty hash is staged, but `_confirmatory_hard_fail()` rejects before `RunManifest(...)`. Dev mode can still land `""` with `mode="dev"`. Cite: `scripts/ws1_finalize_run_manifest.py:567`, `scripts/ws1_finalize_run_manifest.py:575`, `scripts/ws1_finalize_run_manifest.py:543`.

[MED] `HF_HUB_CACHE` is silently ignored when set to a nonexistent path, and discovery falls through to `HF_HOME` / default cache. That can pin from a different cache than the operator explicitly configured. Cite: `scripts/ws1_pin_fleet.py:152`, `scripts/ws1_pin_fleet.py:156`, `scripts/ws1_pin_fleet.py:158`.

[LOW] The Path-E and pilot parquet suffixes do not cross in the finalizer: finalizer reads `*__pilot.parquet`; the Path-E analyzer defaults to `{model}__exposure_horizon.parquet`. Pointing finalizer at the exposure-horizon trace dir should fail missing-pilot traces, not silently mix them. Cite: `scripts/ws1_finalize_run_manifest.py:206`, `scripts/run_exposure_horizon_analysis.py:78`.

[MED] Final RunManifest writes are non-atomic: unlike the pinner, the finalizer writes JSON directly with `Path.write_text()`, so a killed rerun can leave a partial file or leave a previous valid-looking manifest in place if death happens before replacement. Cite: `scripts/ws1_finalize_run_manifest.py:716`, `scripts/ws1_finalize_run_manifest.py:719`.

[LOW] The legacy ignore line can mask future accidental writes to the old Path-E location because it ignores the whole `data/pilot/cutoff_probe/` subtree, not just known pre-rename generated files. Cite: `.gitignore:35`, `.gitignore:37`.

## Meta
[MED] The anchor list focuses on "does the finalizer reject?" but the larger operational gap is artifact binding: the manifest rarely binds trusted fields to content hashes, case coverage, trace metadata, or runstate lineage. The implementation plan even called for trace SHA computation, but the current finalizer never records trace hashes. Cite: `plans/tier-r2-0-implementation.md:503`, `scripts/ws1_finalize_run_manifest.py:684`.
