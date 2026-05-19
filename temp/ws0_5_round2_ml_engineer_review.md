# WS0.5 v0.3 — Round 2 Review (ML Engineer Lens)

**Reviewer**: GPT-5.5 xhigh (ML Engineer role)  
**Date**: 2026-05-19  
**Memo**: docs/DECISION_20260518_ws0_5_thales_alignment.md (v0.3)  
**Round-1 review verified against**: temp/ws0_5_round1_ml_engineer_review.md

## TL;DR

v0.3 materially addresses the round-1 ML engineering blockers: sealed proposer isolation, manifest locking, post-cutoff recurrence nulling, replay-cache storage tiers, canonical replay hashing, and resumable budget rails are now specified well enough to implement.

I would not send this to a full round-3. Two narrow memo patches remain: make the MDE preflight estimator computable before candidates exist, and remove `request_id` from the R4 cache lookup key.

## 1. Issue-by-issue verification (E-1 to E-10)

| Issue | Status (patched / partial / unaddressed) | Notes |
|---|---|---|
| E-1 acceptance_holdout MDE | partial | Correctly splits practical floor from detectable MDE and writes `mde_report.json`; preflight still says it estimates paired discordance `q` from current prompt only, which is not implementable for candidate-vs-incumbent McNemar planning. |
| E-2 sealed holdout isolation | patched | Proposers are API-only, workspace-aware agents are forbidden, allowed/forbidden payloads are enumerated, binary predicate feedback replaces rounded deltas. |
| E-3 candidate contract | patched | `candidate.yaml`, ProTeGi `diagnosis.json`/`patch.diff`, minimal-edit diff validation, and non-ranking train guardrail are now explicit. |
| E-4 manifest immutability + max-look stop | patched | Per-run `manifest.lock.yaml`, content SHA, clean source manifest requirement, CI log invariant, and max-look exhaustion actions are specified. |
| E-5 post-cutoff recurrence scope | patched | 350 post-cutoff controls get `null` + `missing_reason="not_applicable_post_cutoff"` and are excluded from recurrence bin quotas. |
| E-6 alias ambiguity + R4 cache key | partial | Ambiguity overrides are good; cache key mostly fixed, but `model_snapshot_or_request_id` is wrong as a lookup key because `request_id` exists only after a new provider call. |
| E-7 recurrence ranks + stability | patched | Full eligible pre-cutoff frame, frozen cutpoints, rank/tie fields, LOO/bootstrap bin-flip report, and raw/log counts are specified. |
| E-8 replay cache storage | patched | Pilot JSON vs full-CLS sharded JSONL.zst tiers, shard index, no full rendered prompt duplication for high-volume tiers, LFS preflight, and external artifact fallback are now covered. |
| E-9 replay reproducibility | patched | Primary replay check is `canonical_table_hash`; confirmatory replay hard-fails on missing/corrupt/duplicate/hash-mismatched cache; partial mode cannot overwrite final parquet. |
| E-10 budget + resume | patched | Per-task dry-run token estimator, buffered ledger writer, daily pricing epochs, checkpointed `run_state.json`, and `--resume <run_id>` drift checks are specified. |

## 2. Detailed verification

### E-1: acceptance_holdout MDE

v0.3 patch: §4.1 lines 487-495 now separates `delta_min_practical` from `delta_detectable_planning` and explicitly says 0.02 is not claimed detectable at n=300 + alpha schedule. Lines 497-513 add an MDE preflight, write `mde_report.json`, document conservative-gate behavior, and stop if MDE exceeds 0.10.

Verdict: partial.

The core round-1 problem is mostly fixed: v0.3 will no longer pretend a 2pp effect is detectable under an extremely conservative repeated-look gate. The remaining problem is engineering implementability: line 498 says "Sample 200 representative items × current prompt → estimate discordance rate q." For a paired acceptance gate, `q` is the candidate-vs-incumbent discordance rate; it cannot be observed from the current prompt alone before candidate generation.

Follow-up text:

```markdown
For top-1 acceptance gates, MDE preflight does not estimate paired discordance `q`
from the incumbent prompt alone. The manifest must declare the planning method:
either (a) a conservative q-grid such as q ∈ {0.05, 0.10, 0.20} with reported
MDE at each point, (b) q estimated from prior tuning/smoke candidates on
`random_inner_dev`, or (c) a task-specific historical q prior. `mde_report.json`
records the method and must not label incumbent-only error rate as paired
candidate/incumbent discordance.
```

### E-2: sealed holdout isolation

v0.3 patch: §4.1 lines 438-445 define proposers as API-only with sanitized train payloads, forbid workspace-aware sub-agent proposers, and log `payload_sha`. Lines 521-530 expose only binary predicates to proposers and reject duplicate/near-duplicate failed candidates. §4.2 lines 633-653 mirrors the same contract in manifest form.

Verdict: patched.

This addresses both leakage vectors from round 1: sealed files are no longer accessible to repo-aware proposer agents, and rounded-delta score surfaces are no longer exposed as optimizer feedback.

### E-3: candidate generator constraints

v0.3 patch: §4.1 lines 447-461 define `candidate.yaml`, require ProTeGi to emit `diagnosis.json` before `patch.diff`, and enforce minimal-edit candidates with a diff validator. Lines 463-470 make the train minibatch filter a guardrail rather than a ranker.

Verdict: patched.

The contract is now auditable enough for implementation. I do not need a deeper prompt-mutation DSL in this memo; the named artifacts and reject-before-scoring validator are the critical pieces.

### E-4: manifest immutability and max-look exhaustion

v0.3 patch: §4.1 lines 539-548 define legal max-look exhaustion outcomes. Lines 550-557 add the per-run manifest copy, clean source requirement, content SHA, git commit, abort-on-hash-change behavior, and CI invariant. §4.2 lines 655-665 repeats this in the manifest.

Verdict: patched.

This closes the round-1 gap. The driver can now prove that a tuning run used one manifest and stopped when the registered look budget was spent.

### E-5: recurrence factor scope for post-cutoff controls

v0.3 patch: §5.1 lines 706-713 explicitly set post-cutoff controls to `pre_case_cls_family_recurrence = null`, `missing_reason = "not_applicable_post_cutoff"`, and exclude them from recurrence high/low quotas. Closure condition 7 also requires this missing-value policy in `factor_schema.yaml`.

Verdict: patched.

This is exactly the requested resolution. The 430-case factor table can exist without silently giving the 350 post-cutoff controls a non-comparable training-exposure proxy.

### E-6: alias ambiguity and R4 cache keys

v0.3 patch: §5.2 lines 760-770 add conservative rule-based overrides for short aliases, one-character regions, common surnames, shared acronyms, target alias overlap, and missing/low-confidence ambiguity tags. Lines 777-785 add a versioned cache key with article hashes, target id, matched alias, alias-bank SHA, confirm-prompt SHA, and model metadata.

Verdict: partial.

The ambiguity fallback is patched. The cache key is almost patched, but `model_snapshot_or_request_id` is not a valid lookup component. If the provider does not expose a stable snapshot, `request_id` is only known after issuing the API request; using it in the key makes cache hits impossible for the very case where caching matters most.

Follow-up text:

```markdown
R4 cache lookup keys must be computable before any provider call. The key includes
`normalized_article_sha256`, `raw_article_sha256`, `target_id`,
`matched_alias_norm`, `target_alias_bank_sha`, `confirm_prompt_sha`,
`requested_model_slug`, decoding-params SHA, and provider snapshot/fingerprint
if available. If no snapshot is exposed, use `requested_model_slug` plus the
run's model/pricing epoch as the lookup identity; store `response_id` and
provider headers as provenance fields, not cache-key fields.
```

### E-7: within-super_type percentile tie/stability policy

v0.3 patch: §5.2 lines 802-824 compute recurrence ranks/cutpoints on the full eligible pre-cutoff sampling frame, freeze cutpoints before final manifest selection, specify rank/tie fields, write LOO/bootstrap bin-flip rates into `ws0_5_quota_report.json`, and require a signed note if instability is high.

Verdict: patched.

This resolves the engineering stability problem from round 1. I am not re-opening the measurement question of percentile vs absolute count; v0.3 also stores raw/log/clustered sensitivity fields, which is enough for this lens.

### E-8: replay cache storage for full-CLS R1

v0.3 patch: §6.1 lines 896-962 split raw responses into tier A pilot per-case JSON, tier B full-CLS compressed sharded JSONL.zst with `shard_index.parquet`, and tier C auto-tune shards. Lines 964-970 make `model_snapshot` nullable. §6.4 lines 1041-1058 add a 0.7-1.5GB estimate, LFS preflight, and external artifact fallback.

Verdict: patched.

The v0.2 "12K JSON / 60MB" inconsistency is gone. The high-volume path avoids hundreds of thousands of tiny files and does not duplicate full rendered prompt text per record.

### E-9: replay reproducibility and missing-cache behavior

v0.3 patch: §6.3 lines 998-1016 makes canonical row-content hash the primary reproducibility check and records `canonical_table_hash` in provenance. Lines 1018-1023 hard-fail confirmatory replay on missing/corrupt/duplicate/hash-mismatched raw response, while diagnostic partial replay writes a separate artifact.

Verdict: patched.

This is the right determinism contract for closed-model pipelines. It avoids brittle parquet byte identity while still making replay failures non-silent.

### E-10: budget estimates, buffered ledger, checkpoint/resume

v0.3 patch: §7.1 lines 1078-1099 add per-task 100-item token-estimator dry runs and formula-derived item totals. Lines 1101-1120 add buffered ledger writes and daily pricing epochs. §7.4 lines 1147-1185 adds `run_state.json`/sqlite, final checkpoint behavior, and `--resume <run_id>` drift checks.

Verdict: patched.

The budget rail is now implementable rather than paper-only. The ledger design should handle full-CLS throughput without fsync-per-row overhead, and resume can verify manifest/prompt drift before issuing new calls.

## 3. New risks introduced by v0.3

1. **MDE preflight q-estimation ambiguity**: the new preflight fixes the original detectability claim, but its current wording implies paired discordance can be estimated from the incumbent prompt alone. This is a small but real implementation bug; fix with the E-1 follow-up text above.

2. **R4 request-id cache-key fallback**: adding `request_id` into the cache key over-corrects versioning. It is good provenance, but bad cache identity. Move `response_id` out of the lookup key and into the stored record; fix with the E-6 follow-up text above.

3. **Non-blocking cleanup: fixture-growth wording**: §4.1 defines a fixed 3000-item, 7-way split with only 150 reserve rows, while §4.3 says each active rotation appends ~500 additional items. Before implementation, clarify whether 3000 is the initial seed fixture or the total capped fixture after growth. I do not treat this as a verdict blocker because sealed evaluation pools and manifest locking are already clear.

## 4. Final verdict

**Verdict**: APPROVE-WITH-MINOR-PATCHES

**修订后需 re-review section**: No full round-3 needed. Only spot-check §4.1 MDE preflight wording and §5.2 R4 cache-key wording after the two text patches.

**建议下一步**: Apply the two small memo patches above, then proceed to user sign-off / S1 implementation prep. The remaining engineering surface is implementation QA, not decision-memo redesign.
