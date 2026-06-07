---
title: Lens A — Functional correctness of Tier-0 implementation
date: 2026-04-29
review_id: R5A_DESIGN_REVIEW_R2_20260429
lens: A_functional
codex_thread_id: codex-local-review
status: complete
---

# Lens A Verdict

Not functionally correct for cloud spend yet. The strict-majority math resolves correctly for the realized fleet, but Path E is not wired end-to-end by default and the RunManifest finalizer can emit a manifest even when required trace, cutoff, hidden-state, and split-tier provenance is missing or corrupt.

## Critical bugs (block re-launch / cloud spend)

1. **Path E cutoff-probe defaults do not compose end-to-end.**

   `scripts/ws1_run_logprob.py` writes cutoff-probe traces to `data/pilot/cutoff_probe/traces`:

   ```python
   # scripts/ws1_run_logprob.py:286-293
   if args.cutoff_probe:
       out_dir = Path(args.cutoff_probe_output_dir)
       mode_tag = "cutoff_probe"
   ...
   final_path = out_dir / f"{model_id}__{mode_tag}.parquet"
   ```

   But `scripts/run_cutoff_probe_analysis.py` still scans `data/pilot/logprob_traces` by default:

   ```python
   # scripts/run_cutoff_probe_analysis.py:51-55
   p.add_argument(
       "--traces-dir",
       type=Path,
       default=REPO_ROOT / "data" / "pilot" / "logprob_traces",
   )
   ```

   Reproduction: run any model with `--cutoff-probe` using defaults, then run `python scripts/run_cutoff_probe_analysis.py` using defaults. The analysis prints `no trace files matched; nothing to do` because it scans the pilot trace directory, not the cutoff-probe trace directory.

   Exact fix: change the analysis default to `REPO_ROOT / "data" / "pilot" / "cutoff_probe" / "traces"` and add a test that `ws1_run_logprob --cutoff-probe` default output path is the same path consumed by `run_cutoff_probe_analysis.py`.

2. **RunManifest closure is incomplete: the finalizer accepts missing main traces and does not validate cutoff coverage.**

   The finalizer declares `--traces-dir` but never reads it:

   ```python
   # scripts/ws1_finalize_run_manifest.py:73-77
   p.add_argument(
       "--traces-dir",
       default="data/pilot/logprob_traces",
       help="directory of per-model trace parquet files",
   )
   ```

   There is no later reference to `args.traces_dir`. A manifest can be finalized with no `P_logprob` trace files at all, so the script does not actually join "fleet + traces + Path E + hashes" as required by SYNTHESIS Tier-0 #4.

   The cutoff join is also not guarded. `_read_cutoff_observed()` accepts whatever model keys appear in the JSON and never checks them against `fleet.p_logprob_eligible_ids()`:

   ```python
   # scripts/ws1_finalize_run_manifest.py:147-154
   for model_id, row in summary.items():
       co = row.get("cutoff_observed")
       ...
       out[model_id] = Date.fromisoformat(co)
   ```

   Edge-case outcomes:
   - Extra model in `--cutoff-observed` JSON: accepted into `RunManifest.cutoff_observed`.
   - Missing P_logprob-eligible model: silently omitted.
   - No `--cutoff-observed` passed: manifest writes `cutoff_observed={}`.
   - Invalid cutoff date: silently converted to `None` at lines 160-162.

   Exact fix: fail unless the cutoff JSON key set exactly equals the P_logprob-eligible white-box set, allowing `None` only for rejected-with-CI entries emitted by the analysis. Invalid ISO dates should raise `SystemExit`, not become `None`. Also hash and validate the expected trace parquet set from `--traces-dir`.

3. **RunManifest is still missing split-tier roster fields required by the Llama decision.**

   `docs/DECISION_20260429_llama_addition.md` §3.2 requires:
   - `fleet_white_box: list[str]`
   - `fleet_p_predict_eligible: list[str]`
   - `pcsg_pair_registry_hash`

   `RunManifest` has `pcsg_pair_registry_hash`, but not the two split-tier rosters:

   ```python
   # src/r5a/contracts.py:446-451
   cutoff_observed: dict[str, date | None] = Field(default_factory=dict)
   cutoff_date_yaml: dict[str, date] = Field(default_factory=dict)
   quant_scheme: dict[str, str] = Field(default_factory=dict)
   pcsg_pair_registry_hash: str | None = None
   hidden_state_subset_hash: str | None = None
   quality_gate_thresholds: dict[str, int] = Field(default_factory=dict)
   ```

   Without the rosters, downstream readers cannot tell from the manifest which 12 models formed the P_logprob/WS6 denominator and which 14 formed the P_predict denominator. The finalizer computes the counts at lines 302-304 but only records thresholds, not the actual membership.

   Exact fix: add `fleet_white_box: list[str]`, `fleet_p_predict_eligible: list[str]`, and preferably `fleet_p_logprob_eligible: list[str]`; populate them from `fleet.white_box_ids()`, `fleet.p_predict_eligible_ids()`, and `fleet.p_logprob_eligible_ids()`.

4. **Hidden-state extraction completeness is not enforced.**

   If `--hidden-states-dir` exists but is empty, `_hidden_state_subset_hash()` returns `(None, 0)` and the finalizer still writes the manifest:

   ```python
   # scripts/ws1_finalize_run_manifest.py:173-185
   if not hidden_states_dir.exists():
       return None, 0
   ...
   if not case_ids:
       return None, 0
   ```

   It also hashes the first model directory with any `.safetensors` files and stops:

   ```python
   # scripts/ws1_finalize_run_manifest.py:176-182
   for model_dir in hidden_states_dir.iterdir():
       ...
       if case_ids:
           break  # Use the first model's set; subset is supposed to be identical
   ```

   This does not prove the 30-case subset exists for all 12 P_logprob-eligible white-box models, nor that all models share the same case IDs. Since WS6 hidden states are explicitly pre-computed during the cloud run, accepting an empty or partial directory can require another rental.

   Exact fix: when `--hidden-states-dir` is supplied for a non-dev finalization, require 12 model subdirectories, exactly the expected 30 case IDs in each, and identical case sets across models. Add an explicit `--allow-missing-hidden-states` dev flag if smoke finalization needs to bypass this.

## Major issues (fix before next batch)

1. **`pcsg_pair_registry_hash` is optional even though the decision requires a string.** In `src/r5a/contracts.py:449`, `pcsg_pair_registry_hash: str | None = None` weakens DECISION_20260427 §3.2. The finalizer populates it, but the schema allows a manifest with no pair registry hash. Make it `str` for confirmatory manifests or add a separate dev manifest type.

2. **The PCSG validator accepts duplicate members and self-pairs.** In `src/r5a/fleet.py:185-195`, temporal refs are `[early, late]` and capacity refs are `list(pair.members)`, but there is no uniqueness check. A capacity pair with `members: [qwen2.5-7b, qwen2.5-7b]` passes; a temporal pair with `early == late` passes. Add `if len(set(refs)) != len(refs): raise ValueError(...)`.

3. **Pinning checks allow placeholder or malformed Docker digests.** `scripts/ws1_run_logprob.py:235` only checks truthiness:

   ```python
   if not args.vllm_image_digest:
       raise SystemExit(...)
   ```

   Passing `--vllm-image-digest <TBD>` succeeds. The finalizer also accepts `None` or `<TBD>` at `scripts/ws1_finalize_run_manifest.py:370`. Require a value matching `^sha256:[0-9a-f]{64}$` or document and validate the exact digest format produced by the operator command.

4. **White-box pinning validation does not require `tokenizer_family` or `quant_scheme`.** `_check_pinning_for_pilot()` only checks `tokenizer_sha` and `hf_commit_sha` at `scripts/ws1_run_logprob.py:223-227`. `_build_backend()` then silently substitutes `""` for missing tokenizer family and `"fp16"` for missing quant scheme at lines 332-335. That would let a bad white-box fleet entry produce traces with false precision/tokenizer provenance. Enforce non-null `tokenizer_family` and `quant_scheme` for every P_logprob-eligible model.

5. **The HF cache auto-discovery can pin the wrong snapshot when multiple snapshots are cached.** `scripts/ws1_pin_fleet.py:152-161` chooses the newest snapshot by directory mtime. That is not necessarily the revision used by `huggingface-cli download`, nor the checkpoint loaded by vLLM. Prefer `refs/main` when the operator requested the default branch, accept an explicit `--revision` per model, or fail on multiple snapshots unless `--pin-json` disambiguates.

6. **The pinner says the vLLM digest is required, but the CLI makes it optional.** `scripts/ws1_pin_fleet.py:96-100` declares `required=False`. This weakens the run provenance log at `scripts/ws1_pin_fleet.py:375-380`. Make it required for non-`--check`, and reject `<TBD>` there too.

7. **`sampling_config_hash` is populated with the article manifest hash.** In `scripts/ws1_finalize_run_manifest.py:358`, `sampling_config_hash=article_manifest_hash`. The repo has `config/pilot_sampling.yaml`; this should be a separate `--sampling-config` input hashed independently. As written, sampling-policy drift is invisible if the frozen article manifest happens to be unchanged.

8. **The finalizer does not require `--vllm-image-digest`, `--gpu-dtype`, or `--launch-env` for confirmatory runs.** These are operational provenance fields from plan §10.4. The schema and finalizer currently allow all three to be absent. Keep an explicit dev bypass if needed, but the default finalizer path should fail for missing operational provenance.

9. **`run_cutoff_probe_analysis.py` does not validate analyzed models against the fleet.** Even after the default directory is fixed, explicit `--models` or stray trace files can produce a cutoff JSON with non-fleet keys. This should be rejected before output or caught by the finalizer; preferably both.

## Minor issues (cleanup-tier)

1. `scripts/ws1_run_logprob.py:159-160` still defaults `--pilot-articles` to `data/pilot/manifests/pilot_100_articles.json`, but the current plan and sampling config use the 430-case pilot (`pilot_430_articles.json` / `pilot_430_cases.json`). The cloud plan passes an explicit path, so this is not the main blocker, but the default is stale.

2. `scripts/ws1_run_logprob.py:425-431` writes `trace_summary(pending)`, so after a resume the summary describes only traces written in the current process, not the consolidated parquet. The final parquet path is correct; the summary is misleading for resumed cutoff-probe or pilot runs.

3. `scripts/run_cutoff_probe_analysis.py` always emits `p_drop_gt_005` even when `--drop-threshold` is not `0.05`. Either make the output key threshold-neutral (`p_drop_gt_threshold`) or freeze the threshold and remove the CLI override.

4. `scripts/smoke_phase7.py:81-99` prints warnings for wrong fleet counts or missing temporal pairs but returns success under `--check-config`. If this smoke check is intended as a gate, convert those warnings into non-zero exit status.

5. `scripts/ws1_pin_fleet.py` only patches unquoted `<TBD>` placeholders. A YAML line like `tokenizer_sha: "<TBD>"` would be treated as already pinned and skipped. Current fleet YAML uses unquoted placeholders, so this is cleanup-tier.

## Findings file-by-file

### src/r5a/contracts.py

Safe:
- The six added fields from DECISION_20260427 / gate-removal are present: `cutoff_observed`, `cutoff_date_yaml`, `quant_scheme`, `pcsg_pair_registry_hash`, `hidden_state_subset_hash`, `quality_gate_thresholds`.
- The four operational provenance fields are present: `tokenizer_shas`, `vllm_image_digest`, `gpu_dtype`, `launch_env`.
- `extra="forbid"` is retained at `src/r5a/contracts.py:416`.
- `model_dump(mode="json")` in the finalizer preserves `date | None` correctly by serializing dates to ISO strings and `None` to JSON null.

Not safe:
- Missing `fleet_white_box` and `fleet_p_predict_eligible` from DECISION_20260429_llama_addition §3.2.
- `pcsg_pair_registry_hash` is typed as optional (`str | None`) at line 449 even though DECISION_20260427 §3.2 requires `str`.
- Operational fields are all optional/default-empty, so the schema alone does not prevent a confirmatory manifest with no Docker digest, no dtype, and no launch environment.

### src/r5a/fleet.py

Safe:
- `ModelConfig.p_predict` is now optional at `src/r5a/fleet.py:71`, which correctly supports Llama P_logprob-only entries.
- `p_predict_eligible_ids()` and `p_logprob_eligible_ids()` produce the correct realized denominators for the current fleet: 14 P_predict-eligible and 12 P_logprob-eligible.
- The validator rejects unknown PCSG references, duplicate pair IDs, black-box PCSG members, temporal pairs with `members`, and capacity pairs without members.
- `pcsg_pair_registry_hash()` canonicalizes the pair block rather than hashing the whole YAML.

Not safe:
- Duplicate `members` within a capacity pair and `early == late` temporal pairs pass validation. This directly affects E_PCSG_capacity_curve and temporal PCSG correctness.

### scripts/ws1_pin_fleet.py

Safe:
- The model-header regex at `scripts/ws1_pin_fleet.py:195` handles the actual model IDs (`qwen2.5-1.5b`, `llama-3.1-8b-instruct`, etc.).
- The block-end heuristic at lines 217-232 correctly stops at either the next two-space model header or the top-level `pcsg_pairs:` key in the current YAML layout.
- The script re-validates the patched YAML before writing.

Not safe:
- Multi-snapshot HF caches are resolved by mtime, not by requested revision or `refs/main`; this can pin the wrong commit.
- `--vllm-image-digest` is optional and unvalidated despite being part of the provenance story.
- YAML and pinning log writes are read-modify-write without a file lock; concurrent pinner invocations can lose changes.

### scripts/ws1_finalize_run_manifest.py

Safe:
- Strict-majority math is correct:
  - `_one_third_minimum(14) = 5`
  - `_strict_majority(14) = 8`
  - `_strict_majority(12) = 7`
- For the current fleet, `quality_gate_thresholds` records 5/14 for E_extract main-text promotion, 8/14 for E_extract confirmatory promotion, and 7/12 for WS6 informational/mechanistic denominator.
- Black-box `<TBD>` placeholders are caught when `--allow-tbd` is not set (`gpt-5.1.api_model_name`, `claude-sonnet-4.6.api_model_name` in the current YAML).
- `--allow-tbd` does let smoke/dev manifest finalization through; no later Pydantic check re-blocks those placeholders.

Not safe:
- `--traces-dir` is unused; no main trace validation or hashing occurs.
- `cutoff_observed` JSON keys are not checked against the fleet; unknown models are accepted and missing models are omitted.
- Invalid cutoff date strings are silently converted to `None`.
- Empty or partial hidden-state directories are accepted.
- `sampling_config_hash` is the article manifest hash, not the sampling config hash.
- `vllm_image_digest`, `gpu_dtype`, and `launch_env` are not required.

### scripts/ws1_run_logprob.py

Safe:
- `--cutoff-probe` uses its own mode tag and chunk directory, so cutoff-probe chunks do not collide with smoke or pilot chunks.
- Chunk resume still works for cutoff-probe mode at the parquet level because `existing_case_ids(chunks_dir)` and `consolidate_chunks(chunks_dir, final_path)` use the mode-specific directory.
- Invoking `--cutoff-probe` on a white-box model with `p_logprob: null` fails before scoring: `_decide_backend()` raises `has no p_logprob block`.

Not safe:
- The cutoff-probe output default disagrees with the analysis default.
- `--vllm-image-digest <TBD>` passes because only truthiness is checked.
- Missing `tokenizer_family` and `quant_scheme` are silently filled with `""` / `"fp16"`.
- `--pilot-articles` default is stale (`pilot_100_articles.json`).
- Resume summaries cover only newly written traces, not all consolidated traces.

### scripts/run_cutoff_probe_analysis.py

Safe:
- It is wired to the new `detect_cutoff()` piecewise-WLS API and writes CI fields needed by the finalizer.
- The trace filename pattern now expects `{model}__cutoff_probe.parquet`.

Not safe:
- Default `--traces-dir` still points to `data/pilot/logprob_traces`, so the new cutoff-probe mode fails with default CLI settings.
- It does not validate the model list against the fleet.
- The probability field name is hard-coded to `p_drop_gt_005` even though the threshold is configurable.

### scripts/smoke_phase7.py

Safe:
- Fleet count reporting is updated for the split-tier design: 12 white-box, 4 black-box, 14 P_predict, 12 P_logprob.
- It reports both temporal PCSG pair IDs.

Not safe:
- Count/pair mismatches are warnings only. That is acceptable if this script is only informational, but not if `--check-config` is intended to gate cloud spend.

## Cross-cutting observations

- **Threshold math:** Correct. With the realized fleet, `N_p_predict = 14` and `N_p_logprob = 12`; the implementation yields `ceil(14/3)=5`, `14//2+1=8`, and `12//2+1=7`, matching DECISION_20260429_gate_removal §2.6 and DECISION_20260429_llama_addition §2.6.

- **Path E flow:** Not shippable with defaults because runner output and analysis input directories disagree. The finalizer also does not enforce one accepted-or-rejected cutoff entry per P_logprob-eligible model.

- **Pydantic validation bypass:** I found no `model_construct` bypass. `RunManifest(...)` validates with `extra="forbid"`, and `model_dump(mode="json")` is safe for dates. The problem is not bypass; it is that the schema permits missing required provenance and lacks the split-tier roster fields.

- **Concurrency/races:** The YAML patcher and pinning log use read-modify-write without locks. The trace chunk path is safe only if one process owns a given `(model_id, mode)` chunk directory; two concurrent runs of the same model/mode can race and corrupt resume assumptions.

- **Cross-platform:** The code mostly uses `Path` and explicit UTF-8. HF cache symlink resolution is reasonable on Windows and Linux, but snapshot selection by mtime is not a cross-platform guarantee of the loaded revision.

- **YAML patcher structure:** The regex and block-end heuristic match the current YAML. It finds two-space model headers and stops before top-level `pcsg_pairs:`, so it will not accidentally patch the PCSG registry under the current structure.

## Confidence

High on the seven requested files and the specified edge cases. I read the design memos, inspected the full `3b0408c..208ef06` diff for the requested files, checked current fleet counts and threshold values with a no-write Python probe, and traced the cutoff-probe/finalizer paths end-to-end. I did not run the full pytest suite because the review request was read-mostly and asked that only the report be written.
