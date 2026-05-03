## Cold-read first impressions of v2

[HIGH] v2 is clearer than v1, but it is not execution-ready as written: PR1 has explicit hard stops on Q1, Q2, and Q5. That is honest, but it means “implementation note” still contains unresolved parent decisions. See `IMPLEMENTATION_NOTE.md:32`, `:36`, `:41`, `:183`.

[HIGH] v2 still sits awkwardly beside the plan-of-record. v2 says HEAD is `349efab` and proposes PR1/PR2/PR3a/PR3b, while `plans/tier-r2-0-implementation.md` targets `8350d9e`, one consolidated commit, and rollback to `8350d9e`. v2 does not explicitly say it supersedes those execution parts.

[MED] The cloud-spend gate is now stated cleanly: all four PRs must merge before GPU spend. That part is materially improved. See `IMPLEMENTATION_NOTE.md:14-18`, `:197-204`.

[MED] The Path-E key-presence fix is useful, but narrow. Checking that `trace_shas` and `probe_set_sha256` keys exist does not by itself prove those values are shaped, non-empty, or roster-aligned. See `IMPLEMENTATION_NOTE.md:37`, `:58`, `:201`.

## v1-concern verification table

| v1 concern (severity) | v2 closure status | Notes / cite v2 section |
|---|---|---|
| [HIGH] Cloud-spend release gate ambiguous | closed | Closed by `Cloud-spend release gate`: all PR1+PR2+PR3a+PR3b must merge and CI must be green before spend. See `IMPLEMENTATION_NOTE.md:14-18`, `:204`. |
| [CRIT] #9 row-count gate absent from PR1 | closed | PR1 now explicitly includes row-count validation via `pyarrow.parquet.read_metadata()`, PR1 tests, and manual DoD. See `IMPLEMENTATION_NOTE.md:36`, `:59`, `:200`. |
| [HIGH] Expected `n_articles` source undefined | partial | Q5 now names the problem and recommends article-manifest count, but PR1 still says “stop until Q5 decided.” See `IMPLEMENTATION_NOTE.md:36`, `:167-176`, `:183`. |
| [HIGH] Runstate terminal-state definition under-specified | partial | Q2 now acknowledges `src/r5a/runstate.py` does not exist and tells implementer not to invent semantics, but no executable terminal-state definition is provided. See `IMPLEMENTATION_NOTE.md:151-159`. |
| [HIGH] Path-E provenance binding incomplete | partial | v2 adds source JSON key-presence verification and tests, closing the exact missing-key hole. It still only says key presence, not value shape/coverage. See `IMPLEMENTATION_NOTE.md:37`, `:58`, `:201`. |
| [MED] Artifact identity weak across manifest-bound values | partial | Improved via `exposure_horizon_source_sha256`, `pilot_trace_shas`, row-count gate, key-presence gate, and e2e test. Still weakened by Q2/Q5 being open and Path-E key-only verification. See `IMPLEMENTATION_NOTE.md:33-37`, `:52`. |
| [MED] `TRIAGE_LOG.md` closing-PR ownership missing | partial | Ledger and DoD now exist, but representative file lists still omit `TRIAGE_LOG.md`, and “when each PR merges” is process-ambiguous. See `IMPLEMENTATION_NOTE.md:186`, `:202`, `:206-215`. |
| [MED] `.gitignore` cleanup may expose ignored artifacts | closed | PR3a now has explicit pre-edit check and risk note. See `IMPLEMENTATION_NOTE.md:97-99`, `:185`. |
| [LOW] PR3b grep used GNU/bash syntax in PowerShell context | closed | Replaced with PowerShell-native commands and notebook coverage note. See `IMPLEMENTATION_NOTE.md:107-115`. |
| [LOW] Hard-coded “87 passed” language would go stale after PR2 | closed | PR2 now says use relative test-count language; DoD avoids hard-coded final count. Pre-flight still records current baseline, which is fine. See `IMPLEMENTATION_NOTE.md:85`, `:198`. |
| [MED] Dev-mode semantics for new `exposure_horizon_source_sha256` missing | closed | Field is now `str \| None = None`, with confirmatory hard-fail rejecting `None`. See `IMPLEMENTATION_NOTE.md:33-35`. |
| [MED] Clause-numbering docstring could go stale | closed | v2 says use clause names, not numbers, and adds post-renumber grep. See `IMPLEMENTATION_NOTE.md:51`, `:99`, `:133`. |
| [MED] LOW-3 duplicate clause numbering not test-gated | closed | PR1 now requires a clause-number uniqueness test. See `IMPLEMENTATION_NOTE.md:42-43`, `:63`. |
| [MED] Analyzer→finalizer e2e test was too late in PR2 | closed | Moved to PR1, and PR2 notes MED-7 moved. See `IMPLEMENTATION_NOTE.md:26`, `:52`, `:69`. |
| [MED] PR3b rename surface not purely independent/code-free | closed | v2 now states `p_drop_gt_005` is a Pydantic field, names reader/test sync, and notes PR2 test surface. See `IMPLEMENTATION_NOTE.md:116-119`. |
| [MED] Pinning-log field name ambiguous | closed | v2 corrects current key to `models_pinned` and adds `models_skipped`. See `IMPLEMENTATION_NOTE.md:46`. |
| [HIGH] DoD did not prove #9 row-count closure | closed | PR1 tests now include 0-byte/wrong-N parquet failure and DoD has manual #9 verification. See `IMPLEMENTATION_NOTE.md:59`, `:200`. |
| [HIGH] Q1 strict validator could block pinner/fleet loading | partial | Q1 is now explicit with a recommendation, but remains an open stop point. See `IMPLEMENTATION_NOTE.md:32`, `:142-149`. |
| [LOW] PENDING-related grouping was already mostly correct | closed | Still grouped in PR3a and ledger. See `IMPLEMENTATION_NOTE.md:93`, `:214`. |

## Novel concerns in v2

[HIGH] v2 introduces a PR3b ordering contradiction. `Bundling strategy` says PR3a/PR3b can land in parallel with PR2 if testers do not conflict, but PR3 and the dependency tree say PR3b must land after PR2. This can cause exactly the rename/test-surface conflict v2 is trying to avoid. See `IMPLEMENTATION_NOTE.md:22`, `:89`, `:137`.

[HIGH] v2 does not resolve precedence against the plan-of-record. The plan still says `target_commit: 8350d9e`, “one consolidated commit,” and rollback via `git reset --hard 8350d9e`; v2 says HEAD `349efab` and four PRs. A fresh implementer using both can follow the wrong execution model. See `IMPLEMENTATION_NOTE.md:7-18`, `:20-22`; plan `:4`, `:12`, `:1505-1507`.

[MED] Path-E key-presence verification may be an under-fix. v2 says missing `trace_shas` or `probe_set_sha256` fails, but does not require those keys to be non-empty, 64-hex, or aligned with `summary` / fleet roster. See `IMPLEMENTATION_NOTE.md:37`, `:58`, `:201`.

[MED] The PR1 e2e wording may under-test the #9 SHA half. It only says assert `pilot_trace_shas` is “populated for every roster member,” not that values equal the actual parquet SHA-256 values. See `IMPLEMENTATION_NOTE.md:52`, `:62`.

[MED] PR3a is labeled “Pure doc/CLI sweep” and “No tests required (docs only),” but it touches Python scripts and CLI help surfaces. Manual help inspection is listed, but the “docs only” label understates the executable surface. See `IMPLEMENTATION_NOTE.md:91-101`.

[LOW] v2 says “Three-PR sequence” while enumerating PR1, PR2, PR3a, and PR3b and DoD calls them “all four PRs.” Mostly naming drift, but it can confuse ledger and merge tracking. See `IMPLEMENTATION_NOTE.md:22`, `:197`, `:210-215`.

## Drift / completeness

[MED] Dependency tree is mostly valid after moving the e2e test to PR1. The #3/#9 edge now points to PR1, and PR2 correctly removes MED-7. See `IMPLEMENTATION_NOTE.md:52`, `:69`, `:126-128`.

[MED] Dependency tree overstates what the PR1 e2e proves for #9. Row-count is separately tested, but the tree says `source_sha256, pilot_trace_shas, row-count` are verified by the e2e linkage test. The e2e description only names source hash equality and `pilot_trace_shas` population. See `IMPLEMENTATION_NOTE.md:52`, `:128`.

[LOW] Closing-PR ledger matches the body bullets. PR1, PR2, PR3a, and PR3b findings line up with their section lists. See `IMPLEMENTATION_NOTE.md:26`, `:69`, `:93`, `:105`, `:212-215`.

[HIGH] Open Q5 and PR1 step 4 line up logically, but not executably. Step 4 says stop until Q5 is decided; Q5 recommends article-manifest count but does not turn that into a settled instruction. See `IMPLEMENTATION_NOTE.md:36`, `:167-176`.

[MED] Q1/Q2/Q5 are all blocking PR1 questions, but the dependency closure tree only represents technical dependencies, not these decision dependencies. The risks section does capture the stall. See `IMPLEMENTATION_NOTE.md:123-138`, `:183`.

## Pre-execution readiness

[HIGH] The implementer can start only PR1 step 1 cold. PR1 step 2 immediately blocks on Q1 unless the recommendation is treated as already approved. That block is anticipated by v2. See `IMPLEMENTATION_NOTE.md:31-32`, `:142-149`.

[HIGH] The first unanticipated stall is the plan-of-record conflict: v2 does not tell the implementer which parts of `plans/tier-r2-0-implementation.md` are obsolete after `349efab`. The old plan’s target commit, single-commit cadence, shell assumptions, and rollback instructions are unsafe context for the new PR sequence.

[HIGH] Q2 remains the largest execution blocker inside PR1. v2 correctly says not to invent terminal-state semantics, so a competent implementer will likely have to stop and escalate if code search does not reveal a runstate writer/schema. See `IMPLEMENTATION_NOTE.md:151-159`.

[MED] Q5 is a second PR1 blocker, not just a coding detail. The note’s recommendation probably matches current `ArticleRecord` list usage, but v2 still frames it as open and tells the implementer to surface v3 if semantics differ. See `IMPLEMENTATION_NOTE.md:167-176`.

## Meta

[HIGH] v2 is now a credible review-fix roadmap, but not a complete execution brief. The remaining parent-level issue is decision authority: Q1/Q2/Q5 must either be pre-decided or explicitly delegated before PR1 can proceed without another planning interruption.
