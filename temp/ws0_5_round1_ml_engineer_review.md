# WS0.5 v0.2 — Round 1 Review (ML Engineer Lens)

**Reviewer**: GPT-5.5 xhigh (ML Engineer role)  
**Date**: 2026-05-19  
**Memo**: docs/DECISION_20260518_ws0_5_thales_alignment.md (v0.2)  
**Companion**: temp/ws0_5_issue_decisions.md

## TL;DR

v0.2 genuinely fixes the round-0 conceptual failures: taxonomy/versioning, replay-as-determinism, recurrence data contract, and budget ledger are all materially better. I would not send it back to draft.

However, §4-§7 still have production-risk gaps that can break the implementation: the acceptance holdout is likely underpowered for a 0.02 delta under 30-look Bonferroni, sealed holdouts are not mechanically protected from workspace-based proposers, full-CLS replay storage is underestimated by one to two orders of magnitude, and recurrence factor scope for the 350 post-cutoff controls is unclear.

## 1. Round-0 issue verification

| Round-0 Issue | v0.2 Engineering Fix | Verdict |
|---|---|---|
| #1 taxonomy | Corrects to Thales V3 13-class + Scheme A 5-super_type collapse. | solid |
| #2 Target Salience | Adds deterministic target selection, null rejection, 3-level ordinal scoring, and metadata snapshot dependency. | solid |
| #3 auto-tune validation | Replaces two-patch reused-holdout loop with 4-layer split, candidate pool, paired gate, alpha ledger, active fixture. | has_risk |
| #4 determinism | Redefines determinism as replay-from-cache with provenance. | has_risk |
| #5 closure quota gates | Adds `factor_schema.yaml`, quota report, and `check_pilot_cells.py` stub as closure conditions. | solid |
| #6 signal_profile asset | Corrects v5.5 two-pass status and adds V2-vs-v5.5 smoke comparison rule. | solid |
| #7 recurrence contract | Adds 24mo strict window, full CLS R1, alias bank, high-ambiguity confirmation, no dedup, CLS provenance. | has_risk |
| #8 budget cap | Replaces "$5/factor" with token/USD ledger and safety rails. | has_gap |
| #9 Authority status | Clarifies Authority as adjunct/covariate, not confirmatory. | solid |

Engineering read: v0.2 resolves round-0 in the memo-level sense. The remaining concerns are implementation contracts: exactly what the driver is allowed to read, cache, mutate, checkpoint, and resume.

## 2. §4 Scheme Y auto-tune — engineering gaps

### 2.1 4-layer split

**Verdict: has_risk.**

The 60/20/10/10 split is directionally right, but `acceptance_holdout=300` is not obviously compatible with `delta_min=0.02` plus `per-look alpha=0.00167`. For binary accuracy, 0.02 on 300 examples is only 6 net examples; an exact matched-pair gate at that alpha will usually need a much larger asymmetric discordance count. For entity F1, bootstrap width over 300 heterogeneous articles is also likely too wide to reliably accept a 2pp improvement.

The sealed pools are described as sealed, but not mechanically sealed. If Claude/Codex proposers are implemented as independent sub-agents with workspace access, they can read `acceptance_holdout` and `final_holdout` unless those files live outside their accessible tree or the proposers are only API calls receiving a sanitized payload. The memo should forbid workspace-based proposer agents for tuning, or require filesystem-level isolation for sealed pools.

Active rotation says "do NOT rotate acceptance/final", but it does not specify a global item-id exclusion set. The driver needs a split manifest with immutable `item_id`, `input_sha256`, and `split` fields, and every active-sampling append must assert no overlap with `acceptance_holdout`, `final_holdout`, pilot cases, or prior sealed rows.

### 2.2 4 candidates orchestration

**Verdict: has_gap.**

The memo names four candidate sources but not the orchestrator shape. For leakage control, use one deterministic driver that calls two or more proposer APIs with a minimal JSON payload. Do not run two independent repo-aware sub-agents unless sealed files are ACL-isolated outside their read scope.

The ProTeGi-style candidate should be implemented as a two-artifact flow: `diagnosis.json` from a train minibatch, then `patch.diff` conditioned only on that diagnosis plus allowed prompt sections. A single unconstrained "diagnose+fix" response is easier to log poorly and harder to audit.

The "minimal-edit 1-2 line" rule cannot be just a prompt instruction. Enforce it with a diff checker: max changed semantic lines, max added examples, allowed sections, and reject-on-violation before any dev/acceptance scoring.

The train minibatch filter is underspecified. It should be a cheap guardrail, not an aggressive ranker: fixed stratified minibatch size, schema/parse failure check, and only drop candidates that are schema-breaking or grossly worse. Otherwise a candidate that helps rare boundary cases can be killed before inner_dev sees it.

### 2.3 Ladder limited-exposure mechanics

**Verdict: has_risk.**

"Pass/fail + rounded delta to 0.01" still leaks a score surface. With 30 looks and proposer-controlled edits, rounded deltas can be used as a coarse gradient, especially if near-duplicates are allowed. The driver should dedupe by `candidate_sha`, reject near-duplicate resubmissions, and expose at most coarse buckets (`fail`, `pass_delta_min`, `pass_large`) rather than a numeric rounded delta.

If the memo keeps rounded deltas, it needs exact mechanics: private exact metric in controller logs only, public rounded value generated once per unique candidate, deterministic rounding policy, and a no-repeat rule. Otherwise repeated queries can infer more than intended.

### 2.4 Pre-registration enforcement

**Verdict: has_gap.**

Logging the manifest git SHA is not enough. The driver should require a clean manifest file at run start, copy the manifest into `data/factors/tuning_runs/<run_id>/manifest.lock.yaml`, compute a content SHA256, and abort if the on-disk manifest hash changes during the run. CI should verify that every tuning log row carries the same `run_id`, `manifest_sha256`, and `manifest_git_commit`.

The max-look policy needs a stop rule. If look 30 is reached without convergence, the run must stop; continuing under the same manifest is invalid. The next action should be one of: ship incumbent with documented plateau, open a new decision memo and new manifest, or build a new fixture with new sealed holdouts. Do not keep using the old acceptance holdout after spending all registered looks.

## 3. §5 Recurrence pipeline — engineering gaps

### 3.1 Phase R1-R5 handoff

**Verdict: has_gap.**

R1 depends on `topic_classification_v4pro.yaml` after auto-tune, but the 3000-case auto-tune fixture is also likely sampled from CLS. This is acceptable only if the fixture split manifest explicitly excludes pilot manifest cases and records overlap with the recurrence reference universe. If calibration rows can later be counted in recurrence, add a sensitivity report excluding calibration fixture IDs from recurrence counts; otherwise rare-target counts can be subtly influenced by prompt tuning on the same articles.

R4 cache key `(article_hash, target_id)` is too weak. Use `normalized_article_sha256`, `raw_article_sha256`, `target_id`, `target_alias_bank_sha`, `matched_alias_norm`, `confirm_prompt_sha`, and `model_snapshot_or_requested_model` in the key or record. Different aliases and prompt versions can otherwise reuse stale confirmations.

`ambiguity_risk: high|low` appears to be emitted by the alias-gen LLM. That is not enough for a skip-confirm decision. Add rule-based overrides: short aliases, one-character regions, common surnames, index acronyms, aliases shared by multiple targets, and any missing/low-confidence tag default to `high`, so they go through Step C.

### 3.2 24mo window + post-cutoff bucket

**Verdict: has_risk.**

The memo says R2 takes "80 pilot target entities", which implies recurrence is only for the 80 pre-cutoff cases. But §6/§8 deliverables talk about a 430-case `pilot_factor_values.parquet`. This needs to be explicit in `factor_schema.yaml`: for the 350 post-cutoff negative controls, is `historical_family_recurrence` computed, set to `NA`, or excluded from factor-bin quotas?

My engineering recommendation: mark recurrence as `not_applicable_post_cutoff` for the 350 post-cutoff controls unless a separate non-confirmatory diagnostic is required. A 24mo window for post-cutoff articles extends beyond model training cutoffs, so it is not the same memorization-proxy factor.

### 3.3 Within-super_type percentile

**Verdict: has_risk.**

With 80 pre-cutoff cases across 5 super_types, each stratum is roughly 16 cases. A percentile threshold at 0.50 is mechanically fragile: ties, one or two case swaps, and super_type imbalance can flip bins and quota checks. This is an engineering stability problem, not a request to change the construct.

v0.3 should freeze a deterministic rank method (`average`, `dense`, or explicit median-split), a tie policy, and a stability report: bootstrap or leave-one-out flip rate, plus raw count retained. If flip rate is high, the run should not silently proceed to manifest freeze without a note in `ws0_5_quota_report.json`.

## 4. §6 Replay-from-cache — engineering gaps

### 4.1 Raw responses persistence

**Verdict: has_risk.**

The storage estimate is internally inconsistent. §6 says cache every raw LLM response and includes `topic_classification_v4pro/<case_or_cls_item_id>.json`; §5 R1 requires 500K-1M full-CLS topic calls. That is not 12,000 JSON files or 35-60MB. With full prompt text duplicated per item, this can easily become multiple GB and hundreds of thousands of LFS pointers.

Per-case JSON is fine for 430 pilot cases; it is a bad default for full-CLS R1 on Windows and Git LFS. Use sharded JSONL or Parquet/Arrow shards for high-volume tasks, e.g. `topic_classification_v4pro/shard_0001.jsonl.zst` with a manifest index mapping `cls_item_id -> shard, byte_offset, raw_sha256`.

Do not store full rendered prompt text redundantly in every record for full-CLS runs. Store `prompt_sha`, `prompt_template_path`, `input_sha256`, canonical input fields, and `rendered_prompt_sha256`; keep the prompt template once. For small pilot outputs, full `prompt_sent` is acceptable.

`model_snapshot` should be nullable. Before S1, run a provider smoke test to see whether DeepSeek V4 Pro exposes a stable snapshot/fingerprint. If not, store requested model slug, response id, provider headers, request timestamp, and `model_snapshot_unavailable=true`.

### 4.2 Git LFS 60MB

**Verdict: has_risk.**

Git LFS is installed on this Windows machine, but the repo currently does not show an existing `.gitattributes` LFS rule from the checked commands. LFS is workable for a 60MB cache, but not for hundreds of thousands of tiny files or a multi-GB full-CLS raw cache.

Add a fallback artifact path: zipped or zstd-compressed cache shards with SHA256, stored outside Git LFS if quota/bandwidth is insufficient. The memo should require a preflight `git lfs env`, quota check, and cache-size estimate after a 1K-call dry run.

### 4.3 Replay script

**Verdict: has_gap.**

"Bit-identical parquet" is too strong unless pyarrow/pandas/compression/library versions are pinned and writer options are fixed. Prefer a canonical table content hash: sorted rows, fixed schema, normalized nulls, and SHA256 over a deterministic serialization. If bit-level parquet identity is still desired, pin pyarrow version and write options explicitly.

Missing or corrupt cache entries should hard-fail for confirmatory replay. A diagnostic `--allow-missing` mode can exist, but it must write a separate incomplete artifact and never update `pilot_factor_values.parquet`.

## 5. §7 Budget accounting — engineering gaps

### 5.1 LedgerEntry orchestration

**Verdict: has_gap.**

Appending one JSONL row per API call is fine; fsyncing every row is not. Use a single ledger writer queue with buffered flush every N rows or seconds, plus a checkpoint on clean shutdown/hard halt. For full-CLS R1, this matters more than the 60K-call auto-tune loop.

Pricing should be fetched at run start and snapshotted into the ledger header, not fetched per call. If a run spans multiple days or a known pricing boundary, refresh at most daily and record a new pricing epoch. The driver should still compute cost from actual token counts returned by the API.

The safety rails mention "halt, require user resume" but no resume state. The driver needs `run_state.json` or sqlite: current phase, cursor, in-flight request ids, accepted prompt sha, alpha spent, budget totals, cache shard offsets, and manifest hash. On hard halt, finish or cancel in-flight calls deterministically, checkpoint, then require `--resume <run_id>`.

### 5.2 Pre-registered estimates

**Verdict: has_risk.**

Uniform `expected_input_tokens_per_item: 3000` is not credible across topic classification, entity extraction, signal_profile, and R4 confirm. The entity prompt is long; topic classification is much shorter; signal_profile sits between them. Bad estimates weaken safety rails and can either over-throttle cheap phases or fail to catch runaway expensive phases.

Use a dry-run token estimator per task: sample 100 representative items, render prompts, compute p50/p95 input/output token estimates, and write task-specific values into the manifest. `expected_items_total` should be formula-derived from rounds, candidate counts, minibatch size, inner_dev ranking count, acceptance looks, pilot cases, full-CLS item count, and expected high-ambiguity Step C rate.

## 6. New risks introduced by v0.2

- The acceptance gate may be too conservative to accept true 2pp improvements, causing false plateau and wasted tuning loops.
- "Codex proposer" can leak sealed holdouts if implemented as a workspace-aware sub-agent rather than an API-only proposer.
- Full-CLS R1 makes replay/cache storage far larger than the §6 12K-response / 60MB estimate.
- The 430-case factor table vs 80-case recurrence target scope is ambiguous, especially for post-cutoff negative controls.
- Git LFS with many small JSON files is a Windows performance and quota risk.
- R4 ambiguity skipping can create false recurrence matches if the alias-gen LLM mislabels an alias as low risk.

## 7. Critical issues

### Issue E-1: acceptance_holdout=300 is underpowered for 0.02 deltas (major)

**问题**: The manifest sets `acceptance_holdout=300`, `delta_min=0.02`, and `per-look alpha=0.00167`. That combination is likely unable to accept many real 2pp improvements, especially for McNemar-style binary gates and entity F1 bootstrap gates.

**建议修法**: Add an MDE preflight to the manifest. Either enlarge acceptance_holdout, increase `delta_min`, relax the statistical gate for tuning acceptance while preserving final_holdout reporting, or use a larger pooled acceptance bank with capped looks.

**可 paste 文本**:
```markdown
**Acceptance-holdout MDE preflight.** Before running Scheme Y, the driver computes a task-specific minimum detectable effect for the registered `acceptance_holdout_n`, metric, and `per_look_alpha`. If the registered design cannot reliably detect `delta_min`, the run must not start. The manifest must be revised by one of: increasing `acceptance_holdout_n`, increasing `delta_min`, changing the acceptance test schedule, or documenting that the gate is conservative and may terminate by plateau. The MDE report is stored at `data/factors/tuning_runs/<run_id>/mde_report.json`.
```

### Issue E-2: sealed holdouts are not mechanically sealed from proposers (major)

**问题**: v0.2 says sealed pools are sealed, but a repo-aware Codex/Claude sub-agent could read the same files from the workspace. This defeats the limited-exposure design even if the prompt never includes holdout rows.

**建议修法**: Define proposers as API-only calls that receive sanitized train payloads, or place sealed pools outside the proposer filesystem/ACL scope. Add driver assertions and run logs proving that proposer inputs contain only `train_visible` artifacts.

**可 paste 文本**:
```markdown
**Proposer isolation rule.** Scheme Y proposers are not allowed to run as workspace-aware agents with access to fixture files. The tuning controller is the only process that can read `inner_dev`, `acceptance_holdout`, and `final_holdout`. Proposers receive only sanitized `train_visible` error summaries through an API payload. If workspace agents are used, sealed split files must live outside their readable filesystem scope, and the run log must record the exact proposer payload SHA for each candidate.
```

### Issue E-3: candidate generator constraints are underspecified (minor)

**问题**: ProTeGi and minimal-edit candidates are named but not enforced. Without diff limits and two-step diagnostic logging, the loop can produce unreviewable prompt mutations.

**建议修法**: Add candidate schemas, diff validators, and train-filter rules before inner_dev scoring.

**可 paste 文本**:
```markdown
**Candidate contract.** Every candidate writes `candidate.yaml` with `source`, `base_prompt_sha`, `changed_sections`, `diff_sha`, and `rationale`. `protegi_style` writes a separate `diagnosis.json` before generating a patch. `minimal_edit` is accepted only if a diff checker confirms no more than two semantic prompt lines changed and no schema/output-key changes occurred. The train-minibatch filter may reject schema-breaking candidates or gross regressions only; ranking is reserved for `inner_dev`.
```

### Issue E-4: manifest immutability and max-look exhaustion are not enforced (major)

**问题**: "Manifest git SHA logged" does not prevent mid-run edits, uncommitted local modifications, or silently extending past 30 looks.

**建议修法**: Lock a manifest copy per run, hash-check it during execution, and define legal outcomes at max-look exhaustion.

**可 paste 文本**:
```markdown
**Manifest lock.** At run start, `ws0_5_auto_tune_loop.py` copies the manifest to `data/factors/tuning_runs/<run_id>/manifest.lock.yaml`, records `manifest_sha256`, and aborts if the source manifest has uncommitted changes or if its hash changes during the run. All tuning log rows must carry the same `run_id` and `manifest_sha256`. If `max_acceptance_looks` is exhausted, the run stops; continuing requires a new decision memo and a new manifest, not an extension of the existing run.
```

### Issue E-5: recurrence factor scope for post-cutoff controls is ambiguous (major)

**问题**: §5 computes recurrence for 80 pilot targets, while §6 deliverables imply a 430-case factor table. The 350 post-cutoff controls should not silently receive the same recurrence factor if their 24mo window extends beyond model cutoffs.

**建议修法**: Freeze scope in `factor_schema.yaml`: recurrence is confirmatory for pre-cutoff cases; post-cutoff cases get `not_applicable_post_cutoff` unless a separate diagnostic is explicitly added.

**可 paste 文本**:
```markdown
**Recurrence applicability.** `historical_family_recurrence` is computed for the 80 pre-cutoff pilot cases used in confirmatory factor-bin analyses. For the 350 post-cutoff negative-control cases, the field is set to `null` with `missing_reason="not_applicable_post_cutoff"` and is excluded from recurrence bin quotas, unless a later memo defines a non-confirmatory diagnostic recurrence measure. This avoids mixing a training-exposure proxy with reference windows that extend beyond model training cutoffs.
```

### Issue E-6: alias ambiguity and R4 cache keys are too loose (major)

**问题**: LLM-generated `ambiguity_risk=low` can incorrectly skip confirmation, and `(article_hash, target_id)` does not include alias bank, matched alias, or prompt version.

**建议修法**: Add conservative rule-based ambiguity overrides and a versioned cache key.

**可 paste 文本**:
```markdown
**Entity-confirm cache and ambiguity fallback.** Alias `ambiguity_risk` is LLM-proposed but rule-overridden: short aliases, one-character regions, common surnames, market/index acronyms, aliases shared across targets, and missing/low-confidence tags default to `high`. R4 cache keys include `normalized_article_sha256`, `raw_article_sha256`, `target_id`, `matched_alias_norm`, `target_alias_bank_sha`, `confirm_prompt_sha`, and requested/model snapshot metadata. Confirm results are invalidated when the alias bank or confirm prompt changes.
```

### Issue E-7: within-super_type percentile needs deterministic tie/stability policy (major)

**问题**: With about 16 cases per super_type, percentile bins are fragile. Ties and one-case changes can flip `high_recurrence` and break quota expectations.

**建议修法**: Keep the construct, but freeze rank/tie mechanics and emit a stability report.

**可 paste 文本**:
```markdown
**Recurrence bin stability.** The recurrence percentile implementation must specify the rank method, tie policy, and null handling in `factor_schema.yaml`. `ws0_5_quota_report.json` includes a stability block with leave-one-out or bootstrap bin-flip rates per super_type. Raw `recurrence_count` and continuous `recurrence_pct_within_super_type` are always stored. If bin-flip instability is high, manifest freeze requires an explicit note rather than silent acceptance.
```

### Issue E-8: replay cache storage is inconsistent with full-CLS R1 (major)

**问题**: §6 estimates 12K raw responses and 35-60MB, but §5 R1 requires 500K-1M full-CLS topic calls if every raw response is cached. The current per-item JSON + full prompt design will not fit the stated LFS plan.

**建议修法**: Split cache policy by volume. Use per-case JSON only for pilot-scale tasks; use compressed sharded JSONL/Parquet for full-CLS R1, or explicitly declare the parsed CLS index as the reproducibility source with an external raw-cache artifact.

**可 paste 文本**:
```markdown
**Raw-cache scope and storage tiers.** Pilot-scale responses may be stored as per-case JSON. Full-CLS topic-classification responses must be stored as compressed shards, not one JSON file per item: `data/factors/raw_llm_responses/topic_classification_v4pro/shard_*.jsonl.zst` plus an index manifest mapping `cls_item_id` to shard location and response SHA. The storage estimate must include full-CLS R1 separately. If raw full-CLS responses are too large for Git LFS, `cls_event_type_index.parquet` is treated as the committed source-of-truth and the raw response archive is stored as an external checksum-locked artifact.
```

### Issue E-9: replay reproducibility should be content-hash based, with hard fail on missing cache (major)

**问题**: Bit-identical parquet is fragile across pyarrow/pandas versions. Missing cache behavior is not specified.

**建议修法**: Pin writer versions if bit identity is required, but make canonical row-content hash the primary reproducibility check. Hard-fail on missing/corrupt cache for confirmatory replay.

**可 paste 文本**:
```markdown
**Replay verification.** `scripts/replay_factor_values.py` verifies replay by computing a canonical table hash over sorted rows, fixed schema, normalized nulls, and factor values. If bit-identical parquet is required, the script pins pyarrow version and writer options. Confirmatory replay hard-fails on any missing, corrupt, duplicate, or hash-mismatched raw response. A separate `--allow-missing` diagnostic mode may write incomplete artifacts, but it cannot overwrite `pilot_factor_values.parquet`.
```

### Issue E-10: budget safety rails need task-specific estimates and resumable checkpoints (major)

**问题**: Uniform 3000-token estimates make rails unreliable, and "halt, require user resume" is not implementable without run state.

**建议修法**: Generate per-task token estimates from rendered prompt dry runs and add a checkpoint/resume contract to the driver.

**可 paste 文本**:
```markdown
**Budget estimation and resume contract.** Each task manifest stores token estimates from a 100-item rendered-prompt dry run: p50/p95 input tokens, p50/p95 output tokens, and formula-derived item counts by phase. The driver writes `run_state.json` or sqlite checkpoints with phase cursor, accepted prompt SHA, alpha spent, budget totals, raw-cache shard offsets, and in-flight request ids. On hard-limit halt, the driver checkpoints and exits; resumption requires `--resume <run_id>` and verifies the same manifest SHA before issuing new calls.
```

## 8. Strengths to preserve

- The 13-class V3 correction and Scheme A collapse are now implementable and compatible with downstream quota logic.
- Target Salience is no longer conflated with Thales `salience=core`; the selection/scoring rule is much closer to a real manifest-time pipeline.
- Scheme Y is the right governance direction: train/inner/accept/final split, alpha ledger, and final_holdout-at-end are all worth preserving.
- Recurrence now has an actual R1-R5 pipeline instead of a handwave around `(entity, event_type, window)`.
- Replay-from-cache is the correct determinism model for closed APIs; only the storage/replay mechanics need tightening.
- Budget accounting moved from a brittle dollar cap to a ledger with live rails, which is the right production posture.

## 9. Final verdict

**Verdict**: MAJOR-REVISIONS-NEEDED

This is not `RETURN-TO-DRAFT`: v0.2's architecture is salvageable and substantially better than v0.1. The required v0.3 edits are mostly 1-2 engineering-day memo patches plus driver-contract constraints, not a 1-2 week redesign.

**修订后需 re-review 的 section**: §4.1-§4.3, §5.2-§5.5, §6.1-§6.4, §7.1-§7.2.

**建议下一步**:

Patch v0.3 by adding the MDE preflight, proposer/holdout isolation rule, manifest lock, recurrence applicability rule for post-cutoff controls, versioned R4 cache key, full-CLS raw-cache storage tier, replay content-hash verification, and budget checkpoint/resume contract. Then do a narrow re-review only on §4-§7.
