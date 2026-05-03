## Cold-read first impressions
[HIGH] The note has a release-gate ambiguity: PR1 says “Cloud spend depends on PR1 landing” while PR3’s goal is “schema cleanliness for cloud spend” and Definition of done requires all three PRs. See `IMPLEMENTATION_NOTE.md:16-18`, `:65-68`, `:136-142`; triage says doc/rename cleanup lands “before cloud spend” at `TRIAGE_LOG.md:46-49`.

[HIGH] PR1 is labeled “close every gate-leak,” but #9’s row-count gate is not in the PR1 sequencing or tests. The note adds `pilot_trace_shas` at `IMPLEMENTATION_NOTE.md:26`, but triage #9 requires both Parquet row-count validation and SHA capture at `TRIAGE_LOG.md:15`.

[MED] The note is strong on finding-to-PR mapping, but weak on artifact identity. It adds fields, but does not consistently say which raw artifact content must be validated before the manifest can bind derived values.

[MED] The DoD requires `TRIAGE_LOG.md` to reference each closing PR, but no PR owns that edit. See `IMPLEMENTATION_NOTE.md:141` versus file lists at `:21`, `:50`, `:73`, `:80-85`.

## Novel concerns
[MED] `.gitignore` cleanup can expose an existing ignored artifact. PR3a includes LOW-5 at `IMPLEMENTATION_NOTE.md:70-73`, and triage says delete the old ignore lines at `TRIAGE_LOG.md:80`; current `.gitignore:34-37` ignores `data/pilot/cutoff_probe/`, and `PENDING.md:37` points to an existing old-path probe fixture. If the ignore is removed, that old generated JSON becomes visible to staging.

[LOW] PR3b’s grep sweep assumes GNU grep syntax, but the handoff context is Windows/PowerShell. `IMPLEMENTATION_NOTE.md:80-83` uses `grep -rn --include=...`; the plan of record explicitly warned that bash idioms fail or differ under PowerShell at `plans/tier-r2-0-implementation.md:77-80`.

[LOW] The test-count language will go stale mid-sequence. PR3a says smoke is “87 passed” at `IMPLEMENTATION_NOTE.md:75`, while PR2 adds tests at `:52-63`; after PR2, “87 passed” is no longer the expected total even if the suite is green.

## Anchored review
[CRIT] Missed implementation dependency: #9 E requires row-count validation before finalization, but PR1 never schedules it. Current finalizer only maps filenames in `_validate_traces_dir()` and never opens Parquet metadata (`scripts/ws1_finalize_run_manifest.py:177-231`); triage requires `pyarrow.parquet.read_metadata()` row-count comparison plus SHA capture (`TRIAGE_LOG.md:15`). A PR1 green merge could still accept 0-byte or wrong-N pilot traces.

[HIGH] Open question missed: “expected n_articles from fleet” is not defined in code. Fleet config has roster/cardinality metadata, not expected pilot row count (`config/fleet/r5a_fleet.yaml:1-8`); finalizer currently only hashes `--article-manifest` (`scripts/ws1_finalize_run_manifest.py:564-565`). The note needs to tell the implementer what source defines expected N for #9.

[HIGH] Runstate lineage is under-specified. Q2 says to read `src/r5a/runstate.py` or similar (`IMPLEMENTATION_NOTE.md:114-115`), but current code has only `RunStateRow` (`src/r5a/contracts.py:365-373`) and finalizer only hashes the DB if it exists (`scripts/ws1_finalize_run_manifest.py:667-672`). The plan does not define the SQLite schema/query for “terminal state,” despite the plan document requiring no orphan pending rows (`plans/phase7-pilot-implementation.md:458-488`).

[HIGH] Path-E provenance binding is incomplete as written. Triage #3 relies on binding analyzer JSON that contains `trace_shas` and `probe_set_sha256` (`TRIAGE_LOG.md:9`), but PR1 only says to store `exposure_horizon_source_sha256` and strict-parse `horizon_observed` rows (`IMPLEMENTATION_NOTE.md:26-27`). It does not require the finalizer to verify that the source JSON actually contains the analyzer provenance emitted at `scripts/run_exposure_horizon_analysis.py:214-218`.

[MED] Required-field semantics for dev mode are not answered. `exposure_horizon_source_sha256: str` is specified at `IMPLEMENTATION_NOTE.md:26`, but `--exposure-horizon` is optional today (`scripts/ws1_finalize_run_manifest.py:105`, `:587-591`). The note does not say what value a dev/`--allow-tbd` manifest gets when no exposure-horizon file exists.

[MED] Clause numbering remains a shared hazard. PR1 step 5 says add hidden-states and runstate clauses and renumber all clauses (`IMPLEMENTATION_NOTE.md:28`), but step 13 still hard-codes “clauses 5/6 short-circuit” in the docstring patch (`:36`). If new clauses are inserted before or between existing checks, that doc patch becomes stale while still closing #2 D.

[MED] LOW-3 may not actually be tested in PR1. The duplicate `[clause 2]` problem is sampling-config versus vLLM digest (`TRIAGE_LOG.md:78`; current code `scripts/ws1_finalize_run_manifest.py:466-476`, `:540-548`). PR1 says renumber all clauses, but its listed PR1 tests omit a sampling-config uniqueness check (`IMPLEMENTATION_NOTE.md:38-43`); PR2 only later adds sampling-config-missing isolation (`:57`).

[MED] PR2 is not purely independent regression coverage for PR1. The analyzer→finalizer e2e test that verifies #3 linkage is in PR2 (`IMPLEMENTATION_NOTE.md:61`), while PR1 claims to close production data correctness (`:16-18`). That means PR1 can merge as green without the test that proves the new manifest field is populated from the producer.

[MED] PR3b is not fully “independent code-wise.” The `p_drop_gt_005` rename touches code and tests, not just consumers: current dataclass field is `src/r5a/analysis/exposure_horizon.py:79`, analyzer reads it at `scripts/run_exposure_horizon_analysis.py:200`, and tests reference it at `tests/r5a/test_exposure_horizon.py:122`. If PR2 lands first, PR3b must update PR2’s expanded tests too.

[LOW] PENDING-related findings are mostly grouped correctly. #8, MED-15, and LOW-6 are all in PR3a (`IMPLEMENTATION_NOTE.md:70-73`), matching triage lines `TRIAGE_LOG.md:14`, `:63`, `:81`.

[MED] The pinning-log field name is ambiguous. The note says `pinned_records` and SKIPs into a separate field (`IMPLEMENTATION_NOTE.md:31`), but current log output key is `models_pinned` (`scripts/ws1_pin_fleet.py:502-508`). The implementer may otherwise fix the wrong surface or introduce a second synonym.

[HIGH] Definition-of-done hole: full green tests plus smoke do not prove #9 row-count closure. The DoD only lists tests and `smoke_phase7.py --check-config` cardinalities (`IMPLEMENTATION_NOTE.md:138-140`); smoke does not inspect pilot Parquet contents.

## Suggested merge sequence sanity-check
[HIGH] PR1 step 2: stop until Q1 is decided, because strict SHA validators can make unpinned fleet YAML unloadable before the pinner can run. The note identifies this at `IMPLEMENTATION_NOTE.md:24-25`, but the implementer needs the decision before touching `ModelConfig`.

[CRIT] PR1 step 3: stop and ask where #9 row-count validation goes. Adding `pilot_trace_shas` without metadata validation does not close the triaged gate-leak (`TRIAGE_LOG.md:15`).

[HIGH] PR1 step 5: stop on runstate. There is no `src/r5a/runstate.py`; “terminal state” is not discoverable from code alone.

[MED] PR1 step 13: stop after clause renumbering and re-check every doc/test reference to clause numbers, especially the “clauses 5/6” docstring language.

[MED] PR2 step 9: stop if PR1 did not already include a producer→manifest assertion for `exposure_horizon_source_sha256`; otherwise PR2 is discovering a PR1 correctness bug too late.

[MED] PR3a: stop before `.gitignore` deletion and inspect old ignored Path-E artifacts. Current ignored `data/pilot/cutoff_probe/probe_set_monthly60_36mo.json` can become untracked.

[MED] PR3b: stop before renames and decide whether PR2 has already landed, because tests added in PR2 become part of the rename surface.

## Meta
[HIGH] The 3-PR structure is workable only if the cloud-spend gate is clarified. As written, the note says PR1 alone unblocks cloud spend, but triage and DoD imply PR3a/PR3b also must land before spend. This is a parent decision, not an implementation detail.
