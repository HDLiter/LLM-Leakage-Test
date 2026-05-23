# WS0.5 pass2 infra drift review: E-6 / E-8 / E-9 / E-10

Scope: only the design-agnostic infra themes E-6, E-8, E-9, E-10 in
`docs/DECISION_20260518_ws0_5_thales_alignment.md` v0.4.

Decision sources checked:

- `.scratch/ws0_5_decision_log.md` source-tagged decisions.
- `refine-logs/reviews/WS0_5_DESIGN/ws0_5_issue_decisions.md`.
- Round-1 / round-2 ML-engineer review sections for E-6/E-8/E-9/E-10.
- `refine-logs/reviews/WS0_5_DESIGN/entity_disambig_methods_20260520.md`.
- `related papers/notes/Entity Linking and Disambiguation.md`.

Summary: 8 must-fix, 1 wording.

## E-6 — entity extraction / disambiguation pipeline

### Must-fix

#### E6-M1 — §5.3 re-admits LLM disambiguation into the main count path

Location: `docs/DECISION_20260518_ws0_5_thales_alignment.md:746-757`

Problem: §5.3 says LLM disambiguation can "enter the main path" if it beats the
deterministic Phase-R4 rule. That contradicts the final E-6 decision: Phase R4 is
deterministic, no LLM in the count path, and LLM use is a one-off user-reviewed
augmentation smoke. The decision log says Phase R4 is "deterministic evidence-tier
disambiguation (no LLM in the count path)" and "LLM only for offline audit"
(`.scratch/ws0_5_decision_log.md:83-85`). The methods review's minimum
recommendation is also explicit: "LLM 不参与主路径" and accepted outputs must be
written back to a versioned rule/alias table (`entity_disambig_methods_20260520.md:386-393`).

Why this is drift: v0.4 continued review removed the old LLM per-match-confirm
critical path. The prose now accidentally preserves a conditional version of that
old path.

Suggested edit: keep LLM disambiguation as a diagnostic smoke only. If the smoke
finds deterministic false negatives, the remedy is to add user-reviewed aliases,
cue rules, or audit notes to the versioned alias/rule table, then rerun the
deterministic R4. Do not allow per-match LLM yes/no calls in the confirmatory main
path. If any LLM adjudication is retained, label it sensitivity / audit, not the
main factor count.

### Wording

#### E6-W1 — "salient entity" in Phase R3 can be misread as a salience-tier filter

Location: `docs/DECISION_20260518_ws0_5_thales_alignment.md:673-676`

Problem: Phase R3 filters for "a salient entity whose normalized surface matches
a target alias." Elsewhere the memo says recurrence and Target Salience consume
`(value, type)` from T2, while `salience=core` is only the candidate pool for the
global admissibility pre-filter (`docs/...:217-220`). The current wording could
lead implementation to require `salience=core` for recurrence / Target Salience
matching, which is not the stated decision.

Suggested edit: replace "a salient entity" with "an extracted entity surface
(`value`, `type`; no `salience=core` requirement here)". Keep `salience=core`
only in the §3.3.1 admissibility pre-filter.

## E-8 — replay cache

### Must-fix

#### E8-M1 — Tier-A JSONL is overstated as independently replaying the full pilot factor table

Location: `docs/DECISION_20260518_ws0_5_thales_alignment.md:816-820`

Problem: Tier A is described as making `pilot_factor_values.parquet`
"independently replayable by anyone with the repo." But §6.3 says replay reads
both Tier A and the Tier-B SQLite (`docs/...:868-870`), and closure condition #6
requires replay from "Tier-A pilot JSONL + Tier-B SQLite cache + frozen code SHAs"
(`docs/...:1055`). Since Tier B is git-ignored and backed up privately, repo-only
replay is not true for any factor path depending on full-CLS or auto-tune cache
state.

Why this is drift: the final E-8 decision is two storage objects, with Tier B as
the full-CLS + auto-tune cache and private Kaggle backup
(`.scratch/ws0_5_decision_log.md:90-103`). The current sentence reads like the
earlier "small raw cache in repo" design.

Suggested edit: narrow the sentence. Example: "Committing Tier A keeps the
pilot-scale direct LLM responses auditable from the repo; full replay of
`pilot_factor_values.parquet` requires Tier B SQLite restored from the private
backup, or else uses only the committed derived artifacts for hash audit."

#### E8-M2 — SQLite lookup key is underspecified / wrong for auto-tune and multi-prompt cache entries

Location: `docs/DECISION_20260518_ws0_5_thales_alignment.md:821-826`

Problem: the memo says the primary key is `cls_item_id` / `case_id`. That cannot
serve as the cache identity for Tier B because Tier B includes both full-CLS and
auto-tune responses (`.scratch/ws0_5_decision_log.md:97`), and the same item can
be called under different `task`, `phase`, prompt template SHA, rendered prompt
SHA, model slug, and decoding params. An id-only `insert-or-ignore` risks treating
different calls as completed and silently reusing stale responses.

Why this is drift / ambiguity: E-8 decided "SQLite-as-cache+index+resume", but
the current prose collapses "completed ids for a fixed final run" into "cache
lookup identity". Those are different indexes.

Suggested edit: define a composite cache key, for example
`(task, phase, item_id, input_sha256, rendered_prompt_sha256, requested_model_slug,
decoding_params_sha, model_snapshot_or_run_epoch)`. Then define a separate resume
view for fixed final phases that selects completed `item_id`s for the current
task/phase/prompt key.

#### E8-M3 — §6.4 says reproducibility travels without Tier B, conflicting with hard-fail replay

Location: `docs/DECISION_20260518_ws0_5_thales_alignment.md:906-910`

Problem: §6.4 says Tier B is regenerable, does not travel with the repo, and
"reproducibility travels through the committed artifacts ... plus sha-locks."
That undercuts §6.1/§6.3's replay-from-cache contract and E-9's hard-fail on
missing cache. It also conflicts with closure #11, which requires Tier-B backup
and sha in provenance (`docs/...:1060`).

Why this is drift: E-8 did replace LFS with private external backup, but it did
not turn Tier B into an optional artifact for confirmatory replay. E-9 confirms
hard-fail-on-missing-cache (`.scratch/ws0_5_decision_log.md:105-108`).

Suggested edit: distinguish artifact audit from raw-response replay. Example:
"The committed artifacts carry the signed output and canonical hashes. A full
confirmatory replay requires the Tier-B SQLite restored from the private backup;
if Tier B is unavailable, replay must fail or run only in explicit diagnostic /
hash-audit mode."

## E-9 — replay reproducibility

### Must-fix

#### E9-M1 — duplicate handling is incorrectly dismissed as structurally impossible

Location: `docs/DECISION_20260518_ws0_5_thales_alignment.md:893-895`

Problem: §6.3 says duplicates are structurally impossible because Tier-B SQLite
has a primary key. But replay reads both Tier A JSONL and Tier B SQLite
(`docs/...:868-870`), and Tier A is a plain committed JSONL. A duplicated Tier-A
record is not structurally impossible. Round-2 E-9 also kept duplicate as a
hard-fail condition alongside missing/corrupt/hash-mismatched cache entries
(`ws0_5_round2_ml_engineer_review.md:119-125`).

Suggested edit: say confirmatory replay hard-fails on missing, corrupt,
duplicate, or hash-mismatched raw responses across both stores. SQLite can
prevent Tier-B duplicate keys, but the replay script must validate Tier-A
uniqueness over the same logical cache key.

#### E9-M2 — `source_raw_response: derived` is too weak for count-based factors

Location: `docs/DECISION_20260518_ws0_5_thales_alignment.md:850-856`

Problem: for count-based factors, provenance allows only `"derived"`. That is
too vague for the replay decision. Issue #4 required per-cell SHA-chain
provenance from raw cache + frozen code (`ws0_5_issue_decisions.md:94-104`), and
E-9 now makes `canonical_table_hash` the reproducibility guarantee. For recurrence
and Target Salience, "derived" must still identify the upstream artifacts:
`cls_event_type_index.parquet`, `target_aliases.json`, AKShare snapshot, R4
rule/code SHA, and the Tier-B cache / Kaggle backup hash where applicable.

Suggested edit: replace the single `"derived"` option with a structured
`derived_from` block for count factors, including artifact paths and hashes:
`cls_event_type_index_hash`, `target_aliases_hash`,
`akshare_master_snapshot_hash`, `disambiguation_rule_sha`, `tier_b_cache_sha`,
and `canonical_table_hash`.

## E-10 — budget ledger / metered client

### Must-fix

#### E10-M1 — checkpoint stores only total USD, but the budget report requires full meter state

Location: `docs/DECISION_20260518_ws0_5_thales_alignment.md:962-988`

Problem: §7.2 says `budget_summary.py` reports per-task and overall USD/tokens,
breakdown by phase, and comparison to expected spend. §7.3's checkpoint only
stores `budget_totals_USD`, then says the meter restarts from that scalar after
resume. Because E-10 removed the separate JSONL ledger and buffered writer
(`.scratch/ws0_5_decision_log.md:112-117`), this loses the per-task/phase token
state needed for the report after a crash or hard-rail halt.

Why this is drift / ambiguity: the final E-10 decision is "one metered client";
that can work, but only if the meter state itself is persisted. A scalar USD
checkpoint is a residue of the old "budget total only" mental model.

Suggested edit: checkpoint the meter state, not only `budget_totals_USD`. Add
`meter_totals_by_task_phase` with `tokens_in`, `tokens_out`, `usd`, pricing
snapshot id/date, and last-updated timestamp. `budget_summary.py` should read the
final persisted meter state and optionally cross-check tokens from the SQLite
cache.

#### E10-M2 — the `src/` metered client is decided but absent from deliverables / closure

Location: `docs/DECISION_20260518_ws0_5_thales_alignment.md:930-937`,
`docs/...:1014-1022`, `docs/...:1050-1063`

Problem: §7.1 and the decision log both say the budget subsystem is one metered
DeepSeek client in `src/` (`.scratch/ws0_5_decision_log.md:112-117`). But §8
deliverables list only scripts and data outputs; there is no `src/...` client
artifact, and §9 closure conditions require only `budget_summary_report.md`.

Why this is drift: the prose decision names the client as the actual subsystem,
while the deliverables / closure make only the report visible. Implementation
could satisfy closure by producing a summary script without the metered client
that all calls must pass through.

Suggested edit: add the concrete client module to §8 and §9. Example:
`src/ws0_5/metered_deepseek_client.py` (or the repo's actual package path), with
the contract that all WS0.5 V4 Pro calls route through it and that it persists
meter snapshots compatible with §7.3 and §7.2.

