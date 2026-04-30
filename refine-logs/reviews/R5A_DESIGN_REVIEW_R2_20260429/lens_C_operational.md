---
title: Lens C — Operational robustness
date: 2026-04-29
review_id: R5A_DESIGN_REVIEW_R2_20260429
lens: C_operational
codex_thread_id: codex-local-20260429-r2-lens-c
status: complete
---

# Lens C Verdict

Commit `208ef06` closes the big Round 1 shape problems: there is now a fleet pinner, a manifest finalizer, a PCSG registry hash, and a separate cutoff-probe mode. I would still block WS1 cloud Stage 0/Stage 1 sign-off until the pinning and finalization paths are hardened. The remaining failures are not style issues; they can produce a pinned-looking fleet or RunManifest whose provenance does not actually correspond to the artifacts on disk.

## Block-cloud-spend issues

1. **Fleet pin values are written as raw YAML double-quoted strings without scalar escaping or post-parse equality checks.** `--pin-json` values containing backslash escapes can parse to a different value than the operator supplied while still passing Pydantic validation (`scripts/ws1_pin_fleet.py:237-258`, `scripts/ws1_pin_fleet.py:353-357`). This is a silent provenance corruption path.
2. **HF cache discovery can select the wrong snapshot and can compute the wrong tokenizer content ID for LFS-backed tokenizer files.** Multiple snapshots are resolved by directory mtime (`scripts/ws1_pin_fleet.py:152-161`), and tokenizer SHA is always computed as Git blob SHA1 (`scripts/ws1_pin_fleet.py:120-131`). Hugging Face's cache uses Git SHA for Git files and SHA256 for LFS files, so this assumption is not portable for all `tokenizer.json` files: <https://huggingface.co/docs/huggingface_hub/v0.21.4/en/package_reference/file_download>.
3. **RunManifest finalization does not bind the manifest to realized trace artifacts.** `--traces-dir` is declared (`scripts/ws1_finalize_run_manifest.py:73-77`) but not scanned for model coverage, trace hashes, per-trace Docker digest, or realized N before thresholds are computed from the eligible fleet (`scripts/ws1_finalize_run_manifest.py:302-304`). A manifest can therefore record 14/12 denominators even if only a subset actually ran.
4. **Path E provenance is not cryptographically linked to the manifest.** `ws1_run_logprob.py --cutoff-probe` requires `--vllm-image-digest` (`scripts/ws1_run_logprob.py:209-241`) and traces carry the digest field (`src/r5a/operators/p_logprob.py:127-138`), but `run_cutoff_probe_analysis.py` writes only summary/diagnostics/config (`scripts/run_cutoff_probe_analysis.py:186-198`) and the finalizer copies only dates (`scripts/ws1_finalize_run_manifest.py:278-283`, `scripts/ws1_finalize_run_manifest.py:373`). Regenerated `cutoff_observed.json` can silently detach from the trace/digest set that produced it.
5. **Hidden-state subset hashing is not reliable as implemented.** The finalizer assumes `<hidden_states_dir>/<model_id>/<case_id>.safetensors` and hashes the first model directory returned by the filesystem (`scripts/ws1_finalize_run_manifest.py:166-185`). The offline HF backend writes flat files named `{case_id}__{model_id}.safetensors` under the configured directory (`src/r5a/backends/offline_hf.py:246-260`), and the cloud plan invokes `ws1_run_logprob.py` with a non-existent `--hidden-states-subset` argument, no required run mode, no `--extract-hidden-states`, and `--output-dir` instead of `--hidden-states-dir` (`plans/ws1-cloud-execution.md:227-232`; actual CLI has `--extract-hidden-states`/`--hidden-states-dir`, `scripts/ws1_run_logprob.py:121-128`, and a required mode group at `scripts/ws1_run_logprob.py:131-151`). This can yield no hidden-state artifacts, `None`, a filesystem-order-dependent hash, or a hash of the wrong subset.
6. **A Git failure creates a reproducible-looking all-zero commit.** `_git_commit_sha()` returns `"0" * 40` on failure (`scripts/ws1_finalize_run_manifest.py:114-121`). For confirmatory manifests, this should be a hard refusal unless the operator passes an explicit dev-mode override.

## Silent-corruption risks (medium severity)

1. Quoted placeholders (`tokenizer_sha: "<TBD>"`) are not patched because the textual current value is `"\"<TBD>\""`, not `<TBD>` (`scripts/ws1_pin_fleet.py:237-253`). The fleet still parses, so re-validation does not catch it.
2. A second pinner run with the same pins does not rewrite fields, but it still appends another `+pinned-<UTC>` suffix by default (`scripts/ws1_pin_fleet.py:332-340`). The fleet version can grow through re-runs without any provenance change.
3. Corrupt pinning logs are silently replaced with a fresh empty history (`scripts/ws1_pin_fleet.py:383-392`). A valid non-list JSON file also crashes at `.append()` after parsing. Neither behavior is acceptable for a provenance log.
4. The pinner and pinning log use plain read-modify-write with no lock or atomic rename (`scripts/ws1_pin_fleet.py:364-365`, `scripts/ws1_pin_fleet.py:383-392`). Concurrent operators can lose each other's fleet pins or log entries.
5. `_hash_strings()` joins sorted strings with newline delimiters (`scripts/ws1_finalize_run_manifest.py:136-139`) while `ArticleRecord.case_id` is unconstrained text (`src/r5a/contracts.py:88-100`). A newline in a future `case_id` can collide or alter subset hashes.
6. `--allow-tbd` manifests can still contain placeholder SHA strings, and missing `None` SHA fields are omitted from the dictionaries (`scripts/ws1_finalize_run_manifest.py:249-265`, `scripts/ws1_finalize_run_manifest.py:306-315`). That is okay for dev only, but should be visibly non-confirmatory.
7. A future PCSG pair field can become hash-insensitive if `PCSGPair` is extended and `pcsg_pair_registry_hash()` is not updated (`src/r5a/fleet.py:83-99`, `src/r5a/fleet.py:140-161`). Current tests do not assert hash payload field coverage (`tests/r5a/test_fleet_config.py:179-190`).

## Cleanup-tier observations

1. `_MODEL_HEADER_RE` matches all current model IDs, including dotted and hyphenated IDs (`scripts/ws1_pin_fleet.py:195`; fleet examples at `config/fleet/r5a_fleet.yaml:41`, `config/fleet/r5a_fleet.yaml:205`, `config/fleet/r5a_fleet.yaml:250`, `config/fleet/r5a_fleet.yaml:270`, `config/fleet/r5a_fleet.yaml:293`, `config/fleet/r5a_fleet.yaml:329`). The escaped hyphen does not need to be moved to the end of the character class.
2. The block-boundary logic works on today's YAML and does not round-trip the `pcsg_pairs:` block (`scripts/ws1_pin_fleet.py:217-232`; `pcsg_pairs:` starts at `config/fleet/r5a_fleet.yaml:352`).
3. `Path.home() / ".cache/huggingface/hub"` is a reasonable Windows and root-AutoDL default (`scripts/ws1_pin_fleet.py:134-143`), but the script should also respect `HF_HUB_CACHE` for operators who configured Hugging Face explicitly.
4. I did not find code that still consumes only `__smoke.parquet` or `__pilot.parquet` and would miss `__cutoff_probe.parquet`. The remaining hard-coded references are docs/comments or pilot-only paths.

## Findings A.1-A.11 (YAML patcher)

### A.1 Model header regex

`_MODEL_HEADER_RE = re.compile(r"^  ([A-Za-z0-9_.\-]+):\s*(?:#.*)?$")` matches every current fleet key I checked:

- `qwen2.5-1.5b` (`config/fleet/r5a_fleet.yaml:41`)
- `qwen3-32b` (`config/fleet/r5a_fleet.yaml:205`)
- `llama-3.1-8b-instruct` (`config/fleet/r5a_fleet.yaml:250`)
- `glm-4-9b` (`config/fleet/r5a_fleet.yaml:270`)
- `deepseek-v3-0324` (`config/fleet/r5a_fleet.yaml:293`)
- `claude-sonnet-4.6` (`config/fleet/r5a_fleet.yaml:329`)

Inside a Python character class, `.` is literal and `\-` is a literal hyphen. It does not need to be at the end. The limitation is intentional: future model IDs containing `/`, `:`, `@`, or spaces would not match and would be skipped.

### A.2 Model block boundary detection

The current fleet layout is safe under the two boundary heuristics (`scripts/ws1_pin_fleet.py:217-232`):

- First model after `models:`: `qwen2.5-1.5b` starts at line 41; the patch span begins at line 42 and ends when `qwen2.5-3b` appears at line 61. Blank lines and section comments before it are ignored.
- Block separator comments: two-space section comments such as `# ---- White-box: Qwen3...` at line 141 and `# ---- White-box: Llama...` at line 225 are ignored as comments. If they appear after a model starts, they are technically included in the previous model span until the next real header, but `field_re` only matches exact four-space field lines, so they are not modified.
- Last model to `pcsg_pairs:`: for `claude-sonnet-4.6`, the scan ignores the top-level PCSG comment banner at lines 341-351 and stops at the top-level `pcsg_pairs:` key on line 352.
- Two-space-indented commented-out field: a line like `  # tokenizer_sha: <TBD>` would not end the block because `line.lstrip().startswith("#")` is true. It also would not be patched. A four-space commented field like `    # tokenizer_sha: <TBD>` also does not match `field_re`.
- Two consecutive TBD-bearing models with a blank line between them: blank lines do not end a block; the next non-comment two-space model header does. Current adjacent examples (`qwen2.5-1.5b` -> `qwen2.5-3b`) behave correctly.

This part is operationally acceptable for the current hand-authored YAML. It is not a general YAML parser, but the tradeoff is explicit and reasonable.

### A.3 `field_re` capture behavior

The regex is `^(    {key}:\s*)(\S+.*?)(\s*(?:#.*)?)$` (`scripts/ws1_pin_fleet.py:237-239`).

It captures bare current values and preserves trailing whitespace/comments. For example, `tokenizer_sha: abcdef   # comment` captures value `abcdef` and suffix `   # comment`.

The failure case is quoted placeholders. `tokenizer_sha: "<TBD>"` captures the value including quotes, so `current == PLACEHOLDER` is false (`scripts/ws1_pin_fleet.py:252-253`). The pinner records `SKIP (already pinned to '"<TBD>"')` and leaves the placeholder in place. The patched YAML still parses, so the re-validation step does not catch this.

### A.4 Quoting policy and input sanitization

The pinner writes `"{new_value}"` directly (`scripts/ws1_pin_fleet.py:256-259`). There is no input validation for `hf_commit_sha`, `tokenizer_sha`, `vllm_image_digest`, or `--bump-version`.

Malformed double quotes usually fail YAML parsing before write, so the fleet file remains unchanged. The silent case is backslash escape semantics: a JSON pin value like `abc\\ndef` is written as `"abc\ndef"` in YAML double-quoted syntax and parses back as a string containing an actual newline. `abc\\x41def` parses as `abcAdef`. Pydantic accepts both as strings, so the post-parse validation passes while the stored provenance differs from the operator-supplied JSON.

Hardening should use YAML/JSON scalar escaping and then assert that the parsed `FleetConfig` field equals the exact requested value. Also restrict expected pins to safe patterns such as full hex commit/hash strings or `sha256:<hex>` where applicable.

### A.5 Idempotency and fleet version re-run safety

Field-level idempotency is only partial. After the first run, values are quoted in text. On the second run, `current` is `"sha"` rather than `sha`, so the code enters the "already pinned to ..." skip branch (`scripts/ws1_pin_fleet.py:252-265`). It does not rewrite the line, which is fine, but the log message is misleading.

The fleet version is not idempotent. Unless `--bump-version` is supplied, every non-check run appends a fresh `+pinned-<UTC>` suffix to the current fleet version (`scripts/ws1_pin_fleet.py:332-340`). Running twice can create `r5a-v2.1-2026-04-29+pinned-T1+pinned-T2` with no actual pin changes. That is provenance churn and should be treated as a bug.

### A.6 Pinning log append behavior

The log append path silently discards invalid JSON history (`scripts/ws1_pin_fleet.py:383-392`). For a provenance log, corrupt history should be quarantined or the script should refuse to proceed. Silent reset makes later audit trails look cleaner than reality.

Also, only `json.JSONDecodeError` is handled. A valid JSON object such as `{}` parses successfully, then `.append()` fails. The code should validate that the parsed log is a list before appending.

### A.7 Race condition

There is no file locking or atomic write around either the fleet YAML or pinning log (`scripts/ws1_pin_fleet.py:364-365`, `scripts/ws1_pin_fleet.py:383-392`).

Realistic failure: operator A discovers and patches Qwen entries, operator B discovers and patches Llama entries, both read the original fleet with placeholders, and the last writer wins. The final YAML can revert the other operator's pins to `<TBD>`, while each operator's local stdout/log claims success. The same lost-update pattern applies to `.fleet_pinning_log.json`.

Use a process lock, write to a temp file, fsync, atomic rename, and compare the pre-write hash to the hash read at startup.

### A.8 Re-validation coverage

`FleetConfig.model_validate(_normalize_models(parsed))` catches malformed YAML and schema violations (`scripts/ws1_pin_fleet.py:346-357`). It does not catch:

- quoted placeholders left unmodified;
- semantic changes caused by YAML double-quote escapes;
- wrong-but-schema-valid values;
- patching the wrong field in the right block, if a future field name collides;
- stale PCSG semantics, because the PCSG hash is not recomputed/compared in this script.

The pinner should compare parsed post-patch values for every requested model/key against the exact requested pins before writing.

### A.9 `_default_hf_cache()` discovery

`$HF_HOME/hub` then `Path.home() / ".cache" / "huggingface" / "hub"` is correct for the common Linux root case (`/root/.cache/huggingface/hub`) and typical Windows `%USERPROFILE%\.cache\huggingface\hub` resolution (`scripts/ws1_pin_fleet.py:134-143`).

The missing operational case is `HF_HUB_CACHE`, which many Hugging Face users set directly. If the operator used that env var, auto-discovery returns `None` and the pinner falls back to "NO PINNING" unless `--hf-cache` is supplied.

### A.10 `_pick_snapshot()` selection

Choosing `max(snapshot_dirs, key=mtime)` is not a reliable provenance rule (`scripts/ws1_pin_fleet.py:152-161`). Snapshot directory mtime can reflect extraction/copy/cache maintenance timing, not the revision used by the run. If multiple snapshots exist, the script should either:

- refuse and require `--pin-json` or `--revision`;
- read the relevant `refs/<branch>` entry when the operator explicitly wants a branch ref;
- inspect the actual path passed to vLLM/offline HF and derive the commit from that path.

For confirmatory use, "most recently touched snapshot" is not a safe synonym for "the checkpoint used by this run."

### A.11 Git-blob SHA1 portability

`_git_blob_sha1()` correctly computes Git blob SHA1 (`scripts/ws1_pin_fleet.py:120-131`). The portability claim is overbroad. Hugging Face cache blob names are Git SHA for regular Git files and SHA256 for Git LFS files. Large `tokenizer.json` files can be LFS-backed, so the computed value may not match the cache blob filename or server ETag.

This is still a deterministic internal fingerprint if R5A defines `tokenizer_sha` as "Git blob SHA1 of tokenizer.json bytes." But the docstring and operator expectation should not claim it matches HF's cache filename for all repos. If the goal is HF provenance, obtain the Hub metadata ETag or read the symlink target/blob name and record which hash convention was used.

## Findings B.12-B.15 (PCSG hash invariance)

### B.12 Canonical form and future field sensitivity

The current hash payload includes all current `PCSGPair` fields and includes `None` values as JSON `null` (`src/r5a/fleet.py:148-160`). That is acceptable: temporal pairs carry `members: null`, and capacity pairs carry `early: null`, `late: null`.

The future-field risk is real. `PCSGPair` forbids extra fields today (`src/r5a/fleet.py:83-99`), so a new YAML field cannot silently enter without a schema change. But once the schema is extended, nothing forces `pcsg_pair_registry_hash()` to include the new field. Current tests only check stability and one edit to `max_token_id_inclusive` (`tests/r5a/test_fleet_config.py:179-190`).

Add a test that compares the hash payload keys against `PCSGPair.model_fields`, or build the payload from `p.model_dump(mode="json")` with explicit exclusions only when justified.

### B.13 Stability across YAML reformatting

Field reordering within a pair and blank-line/comment changes do not affect the hash because the hash is computed from parsed Pydantic objects, sorted by pair ID, then JSON-dumped with `sort_keys=True` and tight separators (`src/r5a/fleet.py:148-161`). I verified this with an in-memory reorder of the first pair.

This means the pinner's comment about preserving PCSG byte order is conservative but slightly misleading: preserving comments/order is good for human review, but the implemented registry hash is semantic/canonical, not byte-for-byte YAML.

### B.14 Stability across singleton model additions

Adding a singleton model that is not referenced by `pcsg_pairs` does not change `pcsg_pair_registry_hash()`, because only `self.pcsg_pairs` are included in the payload (`src/r5a/fleet.py:148-159`). I verified this by adding a copy of `glm-4-9b` in memory and recomputing the hash.

This is the desired behavior for the RunManifest split between whole-fleet hash and PCSG registry hash.

### B.15 Correct invalidation on pair edits

Changing `max_token_id_inclusive` from `151664` to `151665` changes the hash. This is covered by the existing unit test, which mutates the field and asserts inequality (`tests/r5a/test_fleet_config.py:185-190`).

## Findings C.16-C.20 (RunManifest finalizer)

### C.16 `_hash_strings()` delimiter collision

`_hash_strings()` hashes `"\n".join(sorted(items))` (`scripts/ws1_finalize_run_manifest.py:136-139`). There is no upstream validation preventing newline-bearing `case_id` values in `ArticleRecord` (`src/r5a/contracts.py:88-100`).

That creates avoidable ambiguity. Hash the JSON array of sorted strings with `json.dumps(..., separators=(",", ":"), ensure_ascii=False)` instead, or validate `case_id` against a safe filename/id pattern at ingestion.

### C.17 Hidden-state subset hash uses the first model and filesystem order

The prompt's concern is correct. The finalizer iterates `hidden_states_dir.iterdir()`, uses the first directory with any `.safetensors`, then breaks (`scripts/ws1_finalize_run_manifest.py:175-182`). Filesystem iteration order is not a contract. If one model is missing cases or an incomplete temp directory exists, the hash can vary across reruns for the same intended 30-case subset.

There is also a stronger current mismatch: the finalizer expects a per-model subdirectory layout (`scripts/ws1_finalize_run_manifest.py:166-170`), while `OfflineHFBackend._save_hidden_states()` writes flat filenames containing both case and model (`src/r5a/backends/offline_hf.py:246-260`). The cloud plan asks for `--hidden-states-subset`, but `ws1_run_logprob.py` does not define that argument; it defines `--hidden-states-dir` and requires `--extract-hidden-states` plus one of `--smoke`, `--pilot`, or `--cutoff-probe` (`plans/ws1-cloud-execution.md:227-232`, `scripts/ws1_run_logprob.py:121-151`).

The plan says `hidden_state_subset_hash` should be the hash of the WS6 subset selection JSON (`plans/phase7-pilot-implementation.md:1126`). The finalizer should hash that JSON or a canonical case-id list from it, then separately verify that every expected model wrote exactly that case set.

### C.18 `_git_commit_sha()` all-zero fallback

Returning forty zeros on Git failure (`scripts/ws1_finalize_run_manifest.py:114-121`) makes a confirmatory manifest look structurally valid while losing the most important source-code provenance. The unit-test baseline uses zeros (`tests/r5a/test_run_manifest_contract.py:53-68`), but that should not normalize the value operationally.

For confirmatory finalization, fail hard if Git is unavailable or the repo is not readable. If dev workflows need this, gate it behind an explicit `--allow-unversioned` or `--git-commit-sha` override.

### C.19 Quality-gate thresholds use eligible fleet N, not realized N

`n_p_predict` and `n_p_logprob` come from the fleet config (`scripts/ws1_finalize_run_manifest.py:302-304`). The finalizer does not inspect `--traces-dir`, cutoff-probe traces, or P_predict outputs to compute realized model coverage.

If a provider goes down and only 13/14 P_predict models execute, the manifest still records thresholds for 14. If one white-box fails Path E, the manifest still records thresholds for 12 P_logprob models. This is exactly the kind of mismatch the RunManifest is supposed to prevent.

The manifest should record both eligible and realized model sets/Ns, fail confirmatory finalization on missing required artifacts unless an explicit partial-run mode is selected, and derive any realized thresholds from the artifact set actually present.

### C.20 SHA dictionaries and `--allow-tbd`

The prompt's specific claim is slightly off: `<TBD>` is truthy, so `tokenizer_shas` and `white_box_checkpoint_shas` include placeholder strings when `--allow-tbd` is used (`scripts/ws1_finalize_run_manifest.py:306-315`). They do not drop `<TBD>`.

The real risks are:

- `None`/empty fields are silently omitted from the dictionaries;
- `--allow-tbd` can emit a manifest carrying placeholder SHA strings;
- there is no coverage assertion that every white-box model appears in both dictionaries in confirmatory mode.

Because the default mode rejects placeholders before manifest construction (`scripts/ws1_finalize_run_manifest.py:249-265`), this is mainly a dev-mode footgun, not a confirmatory-mode blocker.

## Findings D.21-D.22 (Path E pinning interplay)

### D.21 Cutoff-probe digest linkage

`--cutoff-probe` now refuses to run without `--vllm-image-digest` (`scripts/ws1_run_logprob.py:209-241`), and that digest can be written into each trace via the backend construction (`scripts/ws1_run_logprob.py:311-321`). That part is good.

The weak link is after scoring. `cutoff_observed.json` does not include:

- hashes of the cutoff-probe trace Parquets;
- the per-trace Docker digest set;
- the probe-set hash;
- the `ws1_run_logprob.py` command or fleet hash used to score the traces.

The finalizer also does not compute or record a hash of `cutoff_observed.json`; it only parses dates (`scripts/ws1_finalize_run_manifest.py:278-283`, `scripts/ws1_finalize_run_manifest.py:373`). The pinning log records a Docker digest if supplied, but `--vllm-image-digest` is optional in the pinner (`scripts/ws1_pin_fleet.py:97-100`, `scripts/ws1_pin_fleet.py:375-381`) and the log is not joined to the cutoff output.

So if Path E is rerun or `cutoff_observed.json` is overwritten, the manifest can cite the new dates while the pinning log cites an older or missing Docker digest. The hardening is to have the finalizer read cutoff-probe traces, verify one digest/fleet/pin set, hash every trace plus the probe JSON plus `cutoff_observed.json`, and write those hashes into the manifest.

### D.22 Hard-coded smoke/pilot filenames

I found no code path that still only recognizes `__smoke.parquet` or `__pilot.parquet` and would miss `__cutoff_probe.parquet`.

Relevant code now sets the cutoff-probe output suffix explicitly (`scripts/ws1_run_logprob.py:280-295`), and `run_cutoff_probe_analysis.py` defaults to `{model}__cutoff_probe.parquet` (`scripts/run_cutoff_probe_analysis.py:67-69`). Remaining `__pilot.parquet` references are pilot-specific docs/examples such as finalizer docstring text (`scripts/ws1_finalize_run_manifest.py:13`) and cloud-plan calibration examples (`plans/ws1-cloud-execution.md:335-336`).

## Recommended hardening before WS1 cloud Stage 0 commit

1. Replace raw YAML scalar insertion with a real scalar serializer or JSON-compatible escaping; support quoted `<TBD>`; validate pins with strict patterns; after re-parse, assert exact equality for every requested field.
2. Make `ws1_pin_fleet.py` single-writer safe: lock fleet/log files, write temp + atomic rename, compare pre-write hash, and refuse corrupt/non-list pinning logs unless the operator explicitly starts a new log.
3. Make version bump idempotent: if no field changed, do not bump by default; if a bump is desired, require an explicit `--bump-version`.
4. For HF discovery, respect `HF_HUB_CACHE`, refuse ambiguous multiple snapshots unless an explicit revision is supplied, and record the tokenizer hash convention (`git_blob_sha1` vs Hub ETag/SHA256).
5. Add a PCSG hash payload coverage test tied to `PCSGPair.model_fields`.
6. Change `hidden_state_subset_hash` to hash the frozen subset JSON from `plans/phase7-pilot-implementation.md:1126`; verify every expected white-box model produced exactly that set; fix the CLI/layout mismatch in the cloud plan and runner.
7. Make `ws1_finalize_run_manifest.py` consume trace directories: compute main and cutoff trace hashes, realized model sets/Ns, per-trace digest sets, and coverage errors. Record eligible-vs-realized N separately.
8. Hard-fail confirmatory finalization on Git failure, missing vLLM digest, missing trace artifacts, placeholder SHAs, or cutoff outputs not backed by trace hashes.
9. Hash string lists as canonical JSON arrays, not newline-joined text.
10. Add an artifact retention manifest covering pilot traces, cutoff probe set/traces/output, hidden-state archives, pinning log, runtime DB, and final RunManifest.

## Confidence

High for the code-path findings: I inspected the actual commit at `208ef06`, walked the current fleet YAML block structure, and ran in-memory checks for header matching, field capture, idempotent patch behavior, and PCSG hash invariance. Medium for HF cache details because I did not inspect a local Hugging Face cache for these exact model repos; the finding is based on the script's assumptions plus official Hugging Face cache/ETag documentation.
