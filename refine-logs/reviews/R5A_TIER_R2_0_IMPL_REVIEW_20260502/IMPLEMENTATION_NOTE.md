# Implementation note v4 — Tier-R2-0 review fixes

**Revision history**: v1 → codex review (`IMPLEMENTATION_NOTE_REVIEW.md`, 1 CRIT + 5 HIGH + 8 MED + 3 LOW). v2 closed 13/19 with 6 partial + 4 novel concerns + plan-of-record conflict (`IMPLEMENTATION_NOTE_REVIEW_v2.md`). v3 closed most v2 concerns + introduced 4 novel (`IMPLEMENTATION_NOTE_REVIEW_v3.md`); codex verdict on v3: "sufficient to start, not sufficient to complete PR1" because S2 runstate-writer absent at HEAD + ledger-ownership timing impossible. v4 (current): closes S2 via **forward-declared `RUNSTATE_TABLE_NAME` contract** (no runstate writer needed at HEAD; orchestration conforms when Phase 7 lands); fixes ledger-ownership timing + adds `TRIAGE_LOG.md` to all 4 PR file lists; resolves PR3a sequencing self-contradiction; cleans stale "PR3" naming; splits row-count from e2e in dep tree; adds Q2/S2 to decision dependencies; tightens S2 sqlite read-only open; adds `probe_set_sha256` negative tests; rewrites S5 snippet with inline list-shape assertion.

Maps the 45 triaged findings in `TRIAGE_LOG.md` to a concrete execution roadmap. **This note is a roadmap, not a plan**: it specifies bundling, ordering, dependencies, settled decisions, and remaining open questions; the implementing session decides exact code.

## Plan-of-record supersession (codex v2 HIGH)

`plans/tier-r2-0-implementation.md` (frontmatter `target_commit: 8350d9e`, "single consolidated commit", `status: post-review v3`) describes the **implementation that landed as `349efab`**. As of HEAD `349efab`, that plan's execution-mode sections are **historical**:

- `target_commit: 8350d9e` is no longer the target; it is the parent of `349efab`. Treat it as the start-of-work reference, not as a rollback fallback.
- The "one consolidated commit" cadence (frontmatter L12) applied to landing `349efab` and is no longer in force.
- Rollback instructions like `git reset --hard 8350d9e` are not safe (would discard `349efab`'s history). New work uses standard PR-revert if needed.
- Plan steps A.1..G.43 (skipping `[CUT v3]`) are landed; review confirmed no `[CUT v3]` step accidentally implemented.

What remains valid in the plan: the **design / acceptance criteria sections** (e.g. plan §10.1 forbidding `<TBD>` in confirmatory; the per-step acceptance criteria; the [CUT v3] catalogue) — those are decision context, not execution mode. This note v3 cites those sections where they constrain v3's instructions.

A brief "v3 supersedes execution mode of plan" note belongs in the plan frontmatter once PR1 lands; the implementer should add it as a `status:` line update in PR1 (low-cost, high-clarity).

## Pre-flight invariants

- HEAD = `349efab` (R2 Tier-0 patch landed; pushed to origin/main).
- Baseline: `pytest tests/r5a -q` → 87 passed; `python scripts/smoke_phase7.py --check-config` → green (12 wb / 4 bb / 14 P_predict / 12 P_logprob / 2 PCSG temporal pairs).
- Memory captured: `feedback_review_triage_priority.md`, `feedback_doc_for_llm_context.md`.
- All 45 findings disposed in `TRIAGE_LOG.md` (40 actionable + 5 closed-by-HIGH).

## Cloud-spend release gate (user decision)

**Cloud spend is unblocked only after PR1 + PR2 + PR3a + PR3b have all merged to `main` and CI is green.** PR1 closes the production data correctness gates; PR2 prevents regression; PR3a + PR3b together land a clean schema (no rename debt) for the cloud session. The user's principle: schema must be fully clean before any GPU-billed run starts.

This means: PR-by-PR sequencing matters for development order (each PR must be testable in isolation), but the cloud-spend release gate is the joint condition.

## Settled decisions (formerly Q1, Q5)

These were `Open Qs` in v2; user's recommendations were ratified during v3-prep, so they are now in-body instructions, not stop points.

### S1 (was Q1): `<TBD>` placeholder under Pydantic SHA validator

**Settled**: pattern allows `<TBD>` literal. Apply:
- `hf_commit_sha: Annotated[str, Field(pattern=r"^([a-f0-9]{40}|<TBD>)$")] | None = None`
- `tokenizer_sha: Annotated[str, Field(pattern=r"^([a-f0-9]{64}|<TBD>)$")] | None = None`

`<TBD>` is documented in `plans/tier-r2-0-implementation.md` §10.1 as the canonical placeholder, so admitting it preserves the unpinned-fleet-loadable invariant. Confirmatory hard-fail clause 3 already rejects `<TBD>` (it's in `placeholder_set`), so the manifest gate is unaffected.

### S5 (was Q5): expected pilot row count source

**Settled**: read article manifest entry count, with inline list-shape assertion.

`scripts/ws1_finalize_run_manifest.py:564-565` already reads `args.article_manifest` and hashes it. Extend that read to also count rows. **Use shape-asserting form** (do NOT shortcut to `len(json.loads(...))` which would silently return dict-key count if the file is a dict):

```python
manifest_payload = json.loads(article_manifest_path.read_text(encoding="utf-8"))
if not isinstance(manifest_payload, list):
    raise SystemExit(
        f"--article-manifest {article_manifest_path} is not a JSON list "
        f"(got {type(manifest_payload).__name__}); expected list of ArticleRecord-shaped entries."
    )
expected_n_articles = len(manifest_payload)
```

This count becomes the per-model row-count target for the new gate (PR1 step 4).

**Documented invariant** (add to module docstring of `scripts/ws1_finalize_run_manifest.py`): pilot trace row count must equal article manifest entry count, per model.

If at implementation time pilot Parquet row-count semantics differ (e.g., multiple rows per case), implementer **stops and escalates to user** — but expected behavior at HEAD is one-row-per-case.

## Bundling strategy

Four PRs: **PR1 (schema+gates), PR2 (tests), PR3a (docs/CLI), PR3b (renames)**. Strict ordering rules:
- **PR1 first**, no dependencies.
- **PR2 after PR1** (PR2 tests new gates from PR1).
- **PR3b after PR2** (PR2 adds tests referencing fields PR3b renames; if PR3b shipped first, PR2's renamed-field tests would be wrong).
- **PR3a anytime after PR1** — independent code-wise from PR2/PR3b. May land between PR1 and PR2, in parallel with PR2, or after PR3b — implementer's choice based on scheduling.

(Resolves v3's PR3a self-contradiction per codex v3 MED.)

### PR1 — Schema + gates (production data correctness)

Findings: #1 B, #3 D, #4 A, #5 A, #6 D residual, #7 D, **#9 E (full: row-count + SHA)**, MED-1, MED-2, MED-3, MED-4, MED-5, MED-7 (e2e linkage test promoted from v1 PR2), LOW-1, LOW-3, plus #2 D's docstring honesty patch.

Files touched (representative): `scripts/ws1_finalize_run_manifest.py`, `scripts/ws1_pin_fleet.py`, `scripts/run_exposure_horizon_analysis.py`, `src/r5a/contracts.py`, `src/r5a/fleet.py`, `src/r5a/analysis/exposure_horizon.py`, `plans/tier-r2-0-implementation.md` (frontmatter status update only), `refine-logs/reviews/R5A_TIER_R2_0_IMPL_REVIEW_20260502/TRIAGE_LOG.md` (closing-PR back-references), plus a new shared util module (atomic write).

Sequencing within PR1 (matters because changes interact):

1. Extract `_atomic_write_text` to shared util module (e.g. `src/r5a/io_utils.py`) → both pinner and finalizer import it. Required before MED-3.

2. Add Pydantic SHA pattern validators (#7 D) per S1 settled decision. **Side effect**: existing fleet YAML and `MINIMAL_FLEET_YAML` fixture must satisfy the pattern. With S1 admitting `<TBD>`, the unpinned fleet still loads; valid 40/64-hex SHAs also pass; bad SHAs are rejected. Test fixtures using shorthand SHAs (e.g. `"sha_a"`) must be updated — handled in PR2 fixture upgrade (MED-13).

3. Schema additions to `RunManifest`:
   - `exposure_horizon_source_sha256: str | None = None` (#3 D) — typed `| None` for dev/`--allow-tbd` mode where `--exposure-horizon` is omitted; confirmatory-mode hard-fail rejects `None`.
   - `pilot_trace_shas: dict[str, str] = Field(default_factory=dict)` (#9 E SHA half).

4. **Pilot parquet content gate (#9 E row-count half — codex v1 CRIT)**: in `_validate_traces_dir()` (or a sibling helper called from `main()` before `_confirmatory_hard_fail`), open each `*__pilot.parquet` via `pyarrow.parquet.read_metadata()` (no full read); assert row count == `expected_n_articles` (per S5 settled). Mismatch → SystemExit with `[clause N]` (treat as additional confirmatory clause). 0-byte files surface as parquet-open errors → wrapped into the same clause message.

5. **Path-E source-JSON shape verification (codex v1 HIGH #4 + v2 MED — tightened in v3)**: in `_read_exposure_horizon` (or its caller), verify the analyzer JSON payload satisfies all of:
   - `trace_shas` key present, value is `dict[str, str]`, every value matches `^[a-f0-9]{64}$`, every value non-empty.
   - `probe_set_sha256` key present, value matches `^[a-f0-9]{64}$`, non-empty.
   - `trace_shas` keys equal the fleet P_logprob roster set (model-id alignment).
   Missing key, empty value, malformed hex, or roster mismatch → SystemExit with the relevant clause message. Closes the "stale source JSON without analyzer provenance binds anyway" hole at value-shape level, not just key-presence.

6. Schema-strict parse in `_read_exposure_horizon` (#4 A): `if "horizon_observed" not in row: raise SystemExit`. Also closes C-A3 transitively.

7. Add new clauses to `_confirmatory_hard_fail`:
   - **Hidden-states-dir presence** (#1 B): confirmatory mode + `args.hidden_states_dir is None` → fail.
   - **Runstate lineage** (MED-2) per S2 below: open `runstate_db` SQLite, query terminal-state criterion, fail on orphan rows.
   - Renumber all clauses end-to-end so each check has a unique `[clause N]` (LOW-3 closure of duplicate `[clause 2]`). Sampling-config-existence becomes its own clause number, distinct from vLLM image digest.
   - **Add a unit test asserting clause numbers are unique** in the production hard-fail body (CI gate against future duplicate-numbering regressions). Addresses codex MED that LOW-3 was not testable in PR1.

8. Reorder pinner: log existence + JSON parseability check moved before fleet write (#5 A).

9. Pinner self-misclassification fix (LOW-1): strip quotes before equality check.

10. Pinning log field name: existing log key is `models_pinned` (codex v1 MED). Split semantics: `models_pinned` (only actually-changed entries) and `models_skipped` (conflicts where `_patch_model_block` SKIP'd). Update both producer and any reader/test.

11. HF cache env-var honoring (MED-4): `HF_HUB_CACHE` explicitly set + dir missing → raise; only fall back to `HF_HOME` / default when env var unset.

12. tokenizer.json `json.loads()` validation (#6 D residual).

13. Path-E case-coverage assert (MED-1).

14. Atomic finalizer write (MED-3) using the shared util from step 1.

15. `_confirmatory_hard_fail` docstring honesty patch (#2 D): document that helper-internal validation short-circuits before the collector runs in the default call path. **Use clause-name references, not clause numbers** (numbers shifted after step 7 renumbering — codex v1 MED). E.g. "the exposure-horizon-roster check and trace-roster check are normally enforced inside `_read_exposure_horizon` / `_validate_traces_dir`".

16. Analyzer→finalizer end-to-end test (MED-7 promoted from v1 PR2): tiny fixture, run analyzer CLI → feed JSON to finalizer CLI; **assertions tightened in v3** (codex v2 MED):
    - `RunManifest.exposure_horizon_source_sha256 == _sha256_file(analyzer_output_path)` (equality, not just non-null).
    - For every fleet P_logprob model `m`: `RunManifest.pilot_trace_shas[m] == _sha256_file(traces_dir / f"{m}__pilot.parquet")` (equality per model, not just population).
    - Source JSON shape verification (step 5) actually fired on a malformed fixture in a separate negative test.

17. Frontmatter update to `plans/tier-r2-0-implementation.md`: append `superseded-by: refine-logs/reviews/R5A_TIER_R2_0_IMPL_REVIEW_20260502/IMPLEMENTATION_NOTE.md (post-349efab review fixes)` line. One-line edit, signals to future readers that the plan's execution mode is historical.

Tests in PR1: existing 87 must still pass. **New tests required** (this is what proves the gate fires, per codex DoD HIGH):
- `RunManifest` round-trip with new fields populated.
- Confirmatory hard-fail with new clauses (hidden-states-dir absent → fail; runstate orphan-pending → fail).
- Schema-strict JSON parse (missing `horizon_observed` key → fail).
- Path-E source-JSON shape verification (6 negative cases: 4 for `trace_shas` — missing key, empty dict, non-hex value, roster mismatch; 2 for `probe_set_sha256` — missing key, non-hex value).
- Pilot parquet row-count gate (0-byte parquet → fail; wrong-N parquet → fail).
- Pinner reorder: corrupt log present → fleet bytes unchanged after script exits.
- Atomic write helper (kill mid-write simulation; temp file cleanup).
- Analyzer→finalizer e2e (step 16) with tightened equality assertions.
- Clause-number uniqueness assertion (step 7 unit test).

### S2 (was Q2): runstate terminal-state — fully settled via forward-declared contract

**Confirmed at HEAD**: no runstate writer exists. `Get-ChildItem -Recurse -Include *.py` finds no `runstate*.py`, no `orchestrat*.py`, no `init_*.py`; `Grep -i "CREATE TABLE.*runstate|CREATE TABLE.*request"` returns nothing. Only `RunStateRow` Pydantic class at `src/r5a/contracts.py:365-378` exists.

Schema and semantics (sourced from `plans/phase7-pilot-implementation.md:451-488` and `src/r5a/contracts.py:51-55`, `:365-378`):
- DB path: `data/pilot/runstate.db`; CLI override `--runstate-db`; default from `runtime.runstate_db` (`config/runtime/r5a_runtime.yaml`).
- `status` column values from `RequestStatus` enum: `pending`, `success`, `retryable`, `terminal_skipped`.
- **Terminal-state criterion** (per plan §5.5A exit criteria L488): a request is terminal iff `status NOT IN ('pending', 'retryable')`.

**Forward-declared contract** (lets PR1 ship MED-2 without depending on the runstate writer): in PR1 step 7, implementer adds to `src/r5a/contracts.py` near `RunStateRow`:
```python
RUNSTATE_TABLE_NAME: Final[str] = "request_runstate"
"""SQLite table name for the runstate DB. Phase 7 orchestration writer (forthcoming)
must create the table by this name with columns matching `RunStateRow` fields plus
the seed-triplet columns (`seed_requested`, `seed_supported`, `seed_effective`) per
plans/phase7-pilot-implementation.md §5.5A."""
```

**Confirmatory clause logic** (PR1 step 7 hard-fail clause):
```python
import sqlite3
rs_path = Path(args.runstate_db or runtime.runstate_db)
try:
    conn = sqlite3.connect(
        f"file:{rs_path}?mode=ro&immutable=1", uri=True
    )
except sqlite3.OperationalError:
    failures.append(
        f"[clause N] runstate.db at {rs_path} not initialized; orchestration must run before confirmatory finalize."
    )
else:
    with conn:
        cur = conn.execute(
            f"SELECT COUNT(*), GROUP_CONCAT(case_id || ':' || model_id, '; ') "
            f"FROM {RUNSTATE_TABLE_NAME} WHERE status IN ('pending', 'retryable')"
        )
        count, sample = cur.fetchone()
    if count > 0:
        truncated = (sample or "")[:200] + ("..." if sample and len(sample) > 200 else "")
        failures.append(
            f"[clause N] runstate has {count} orphan pending/retryable rows: {truncated}"
        )
```

Read-only `mode=ro&immutable=1` ensures `sqlite3.connect` does not silently create a missing DB (codex v3 MED).

**Out-of-scope dependency, surfaced as PENDING**: Phase 7 orchestration writer is a separate deliverable. Until it lands and runs at least once, every confirmatory finalize will hit the "not initialized" clause. This is intentional — confirmatory finalize without pilot data has nothing to finalize. Add to `PENDING.md` (as part of PR3a #8 B PENDING split): "Phase 7 orchestration writer for `data/pilot/runstate.db` — must create table `request_runstate` with `RunStateRow`-shaped columns; blocks confirmatory cloud spend".

### PR2 — Test coverage (CI/dev gate hardening)

**Goal**: prevent regressions on PR1's hardened gates. No production code changes; pure test additions and rewrites.

Findings: #10 B, MED-6, MED-8 through MED-13, LOW-2, LOW-4. (MED-7 e2e moved to PR1.)

Files touched: `tests/r5a/*.py` (fixture upgrade + new tests), `refine-logs/reviews/R5A_TIER_R2_0_IMPL_REVIEW_20260502/TRIAGE_LOG.md` (closing-PR back-references).

Sequencing within PR2:
1. Upgrade `MINIMAL_FLEET_YAML` fixture (MED-13): ≥2 white-box + ≥1 black-box + ≥1 pcsg_pair, valid 40/64-hex SHAs (or `<TBD>` per S1). Cascades to all tests using it.
2. Pin-fleet test split (#10 B): `test_pin_fleet_replaces_tbd_with_override` (asserts `<TBD>` removed, override SHAs landed, version bumped) + `test_pin_fleet_is_idempotent` (current byte-equality check).
3. Default-timestamp auto-bump test (MED-10).
4. Explicit-revision happy path (MED-11).
5. Sampling-config-missing in isolation (MED-12).
6. `month_stratified_mink` numerical anchor (MED-6).
7. Hidden-state negative tests (MED-8): missing model dir, mismatched case set, wrong filename layout. (Confirmatory-without-`--hidden-states-dir` test already in PR1 step 7 unit tests.)
8. Real-fleet cardinality sentinel (MED-9): asserts `(14, 12, 2)` triple. Test comment must reference `docs/DECISION_20260429_llama_addition.md` so the next operator knows what governs the change. Will need updating when Llama joins fleet — that's the point.
9. F.38 brittle source-inspection → behavior-based (LOW-4).
10. `power_pilot_ci95_high` / `power_main_ci95_low` absence asserts (LOW-2).

Tests added: ~10-12 new tests. Baseline becomes "PR1-baseline + PR2-additions" (don't hard-code "87" or any specific count anywhere — use relative language; codex v1 LOW).

### PR3a — Doc / CLI sweep (Python-script-touching, no test additions)

**Label correction (codex v2 MED)**: PR3a touches Python scripts and CLI help surfaces — it is doc-content-only, not non-Python. No test additions, but Python files are edited.

Findings: #8 B (PENDING split), #11 B (RunManifest docstring rewrite), MED-14, MED-15, MED-17, MED-19, MED-20, MED-21, MED-22, MED-23, LOW-5, LOW-6.

Files touched: `PENDING.md`, `src/r5a/contracts.py`, `config/prompts/R5A_OPERATOR_SCHEMA.md`, `scripts/build_cutoff_probe_set.py`, `scripts/ws1_pin_fleet.py`, `scripts/run_exposure_horizon_analysis.py`, `scripts/ws1_run_logprob.py`, `scripts/ws1_finalize_run_manifest.py`, `.gitignore`, `refine-logs/reviews/R5A_TIER_R2_0_IMPL_REVIEW_20260502/TRIAGE_LOG.md` (closing-PR back-references).

**Pre-edit checks** (codex v1 MED):
- Before deleting `.gitignore:35-37` (LOW-5): inspect old `data/pilot/cutoff_probe/` subtree for any artifacts that would become tracked (e.g. `data/pilot/cutoff_probe/probe_set_monthly60_36mo.json` referenced in `PENDING.md:37`). `git status` after the deletion change must not surface unwanted files; if any do, decide per-file (delete, move, or scope ignore narrower).
- After `_confirmatory_hard_fail` clause renumbering in PR1: re-grep all docstrings, `--help` text, and tests for clause-number references; PR3a CLI-help sweep should reflect post-renumber state, not v1.

No test additions. Smoke: relative test count green; `--help` text manually inspected; `git status` before commit confirms no inadvertently-tracked previously-ignored files.

### PR3b — Consumer-facing renames

Findings: MED-16 (`fo_eligibility` → `or_eligibility`), MED-18 (`p_drop_gt_005` → `p_drop_gt_threshold`).

**Sequencing**: lands after PR2 (PR2 introduces tests that reference the renamed fields). PR3b's diff covers PR2's test surface plus the original rename surface.

Files touched (representative): `src/r5a/analysis/exposure_horizon.py`, `scripts/run_exposure_horizon_analysis.py`, `scripts/planning_power_calculator.py`, `tests/r5a/test_exposure_horizon.py`, plus any PR2-introduced tests, plus `refine-logs/reviews/R5A_TIER_R2_0_IMPL_REVIEW_20260502/TRIAGE_LOG.md` (closing-PR back-references). Notebook references — discovered by the grep sweep below — also touched if any.

Pre-rename grep sweep (must complete before any rename). Use **PowerShell-native** syntax since this is Windows + PowerShell (codex v1 LOW):

```powershell
Get-ChildItem -Recurse -Include *.py,*.ipynb,*.md,*.txt | Select-String -Pattern "fo_eligibility"
Get-ChildItem -Recurse -Include *.py,*.ipynb,*.md,*.txt | Select-String -Pattern "p_drop_gt_005"
```

(Or use the Grep tool directly; it's ripgrep-backed and OS-agnostic.) Specifically check `notebooks/` directory (Phase 7-9 notebooks may read these JSON keys).

Then rename + sync all readers in one atomic commit. **Rename surface is not pure-consumer**:
- `p_drop_gt_005` is a Pydantic field at `src/r5a/analysis/exposure_horizon.py:79`; renaming changes serialized JSON.
- Reader at `scripts/run_exposure_horizon_analysis.py:200` and tests at `tests/r5a/test_exposure_horizon.py` need sync.
- After PR2, additional tests will reference these names; PR3b's diff includes them too.

If outside-repo references exist (Thales-side code reading R5A JSON outputs), defer the rename or coordinate.

## Dependency closure tree

### Code dependencies
```
PR1 (schema + gates, includes e2e linkage test + plan frontmatter status update)
 ├── #7 D (Pydantic validator) ──→ PR2 fixture upgrade (MED-13) requires valid SHAs (or <TBD> per S1)
 ├── #3 D (source_sha256) + e2e test (step 16) verify SHA-equality linkage
 ├── #9 E SHA half (pilot_trace_shas) → e2e test (step 16) verifies per-model equality
 ├── #9 E row-count half → separate row-count tests + manual DoD (NOT covered by e2e)
 ├── #1 B (hidden-states clause) ─→ PR2 negative tests (MED-8) verify clause fires
 ├── MED-2 (runstate clause via RUNSTATE_TABLE_NAME contract) ─┐
 ├── LOW-3 (renumber clauses) ────────────────────────────────┴ all together; same numbering domain
 │                                                              (uniqueness test asserted in PR1 step 7)
 ├── PR1 step 5 Path-E shape verification → 6 negative tests (4 for trace_shas + 2 for probe_set_sha256)
 └── PR1 step 15 docstring patch ─→ uses clause names not numbers (post-renumber-safe)

PR2 (tests) — depends on PR1
PR3a (docs/CLI) — independent code-wise; can land anywhere after PR1; pre-edit checks required
PR3b (renames) — depends on PR2 (test surface includes renamed fields after PR2)
```

### Decision dependencies (block PR1 progress until parent / implementer resolves)
```
S1 (TBD validator)        ─ SETTLED in body  ─→ PR1 step 2
S5 (expected N source)    ─ SETTLED in body  ─→ PR1 step 4
S2 (runstate contract)    ─ SETTLED in body  ─→ PR1 step 7
                            via forward-declared RUNSTATE_TABLE_NAME;
                            no runstate writer dependency at HEAD
Q3 (fleet cardinality drift) ─ open, scoped to PR2 step 8 test comment
Q4 (PR3b notebook coverage)  ─ open, scoped to PR3b grep sweep
```

After v4: no decision dependencies block PR1 start or completion.

## Open questions remaining

Q1 (TBD validator), Q2 (runstate), Q5 (expected N source) — **all settled in body** as S1, S2, S5 above. v4 closes Q2 via forward-declared `RUNSTATE_TABLE_NAME` contract; no runstate writer needed at HEAD for PR1 to ship.

The remaining open items are **specific implementation-level edges** that don't block PR1 start or completion:

**Q3 (PR2 step 8, MED-9): fleet cardinality drift handling.**
Test asserts `(14, 12, 2)` based on current HEAD. PENDING.md flags Llama-3 / Llama-3.1 additions to P_logprob, which will move the (14, 12) numbers. Sentinel test should fail loudly when fleet roster changes — that's the point. Test comment + commit message must reference `docs/DECISION_20260429_llama_addition.md`.

**Q4 (PR3b grep sweep): notebook coverage.**
`fo_eligibility` and `p_drop_gt_005` may appear in `.ipynb` cells, README files, decision docs, or downstream Thales-side code. Sweep must include `.ipynb`, `.md`, `.txt`. If outside-repo references exist (Thales repo reads R5A JSON outputs), defer the rename or coordinate.

## Risks before execution

- PR1 will temporarily break tests during sequencing (e.g., adding Pydantic validator before updating fixture — fixture lives in PR2 but PR1 may need a working interim). Implement in a single PR + use a working branch; don't push until green.
- Schema additions to `RunManifest` (`exposure_horizon_source_sha256`, `pilot_trace_shas`) bump the schema version implicitly. Check if there's a `schema_version` field that needs bumping.
- The 87-test baseline is the regression detector. If a test fails after a change unrelated to that test's domain, stop and investigate before pressing on.
- S2 runstate writer is **confirmed absent at HEAD**; PR1 closes the gate via forward-declared `RUNSTATE_TABLE_NAME` contract. Confirmatory finalize will hit `[clause N] runstate.db not initialized` until Phase 7 orchestration ships and runs. This is intentional — Phase 7 is a separate deliverable, tracked in PENDING.md.
- PR3b rename surface includes PR2 tests; merge PR3b only after PR2 is green on `main`.
- `.gitignore` LOW-5 deletion may surface previously-ignored Path-E artifacts; pre-deletion `git status` check required.

## Cross-PR ledger ownership (codex v2 MED + v3 HIGH)

Each PR's author updates `TRIAGE_LOG.md` **in the PR's final commit before merge**, using:
- PR description: a `Closes findings: <list>` line.
- TRIAGE_LOG.md row update: per-row `Closing PR` annotation pointing at the PR number (e.g. `PR #42`). The PR number is known once the PR is opened; **no merge SHA needed** (resolves the v3 timing impossibility — merge SHA doesn't exist before merge, and a back-fill commit defeats atomic linkage).

`TRIAGE_LOG.md` is included in each PR's representative file list above (PR1 / PR2 / PR3a / PR3b).

If a PR is rebased / squashed during merge such that the PR # ↔ commit SHA pairing changes, the per-row annotation still resolves via PR # alone (GitHub keeps merged-PR URLs stable).

## Out of scope

- WS6 cluster permutation (separate workstream, blocked on hidden-state fix in #1 B but doesn't go in these PRs).
- HF Meta license click-through and CLS post-2026-02 corpus extraction (user-side actions tracked in PENDING.md).
- Anything from `[CUT v3]` plan steps; review confirmed none accidentally landed.
- Outside-repo (Thales-side) references to R5A JSON keys; if PR3b grep finds any, surface to user before renaming.

## Definition of done

- All four PRs (PR1, PR2, PR3a, PR3b) merged to `main` with CI green.
- PR1-baseline + PR2-additions test count, all green (no hard-coded count).
- `python scripts/smoke_phase7.py --check-config` still reports 12 wb / 4 bb / 14 P_predict / 12 P_logprob / 2 PCSG temporal pairs (sentinel doesn't drift unexpectedly).
- **Manual verification of #9 row-count gate** (smoke does not exercise this): construct a 0-byte `*__pilot.parquet`, run finalizer, verify it rejects with the expected clause message. Documented in PR1 description.
- **Manual verification of Path-E source-JSON shape gate**: construct two analyzer JSON variants — one missing `trace_shas`, one missing `probe_set_sha256` — run finalizer on each, verify both rejected with the relevant clause messages. Documented in PR1 description.
- **Manual verification of e2e equality assertions**: run analyzer + finalizer end-to-end on a small fixture; verify `RunManifest.exposure_horizon_source_sha256` and per-model `pilot_trace_shas` values equal the on-disk file SHAs. Documented in PR1 description.
- `TRIAGE_LOG.md` has each finding's closing-PR back-reference filled in; each PR author updates the log atomically with that PR's last commit (per Cross-PR ledger ownership above).
- `PENDING.md` reflects current state (Phase 8 MC, Llama license, CLS access, post-rename schema) and not stale Tier-R2-0 items.
- `plans/tier-r2-0-implementation.md` frontmatter has `superseded-by:` line pointing at this note (PR1 step 17).
- **Cloud-spend release gate**: All four PRs merged + DoD verified above. Only then start any GPU-billed run.

## Closing-PR back-reference ledger (TRIAGE_LOG ownership)

| PR | Findings closed |
|---|---|
| PR1 | #1 B, #2 D, #3 D, #4 A, #5 A, #6 D, #7 D, #9 E (full), MED-1, MED-2, MED-3, MED-4, MED-5, MED-7 (e2e moved here), LOW-1, LOW-3 |
| PR2 | #10 B, MED-6, MED-8, MED-9, MED-10, MED-11, MED-12, MED-13, LOW-2, LOW-4 |
| PR3a | #8 B, #11 B, MED-14, MED-15, MED-17, MED-19, MED-20, MED-21, MED-22, MED-23, LOW-5, LOW-6 |
| PR3b | MED-16, MED-18 |

Ledger ownership: each PR's author updates `TRIAGE_LOG.md` in the same commit as the PR's last code change.
