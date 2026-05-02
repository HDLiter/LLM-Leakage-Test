---
title: Tier-R2-0 Implementation Plan — Cloud-Spend Gate Closure + Bundled Renames
date: 2026-04-30
target_commit: 8350d9e (branch main)
review_inputs:
  - refine-logs/reviews/R5A_DESIGN_REVIEW_R2_20260429/SYNTHESIS.md
  - refine-logs/reviews/R5A_DESIGN_REVIEW_R2_20260429/DECISIONS.md
  - refine-logs/reviews/R5A_DESIGN_REVIEW_R2_20260429/lens_{A,B,C,D,E}_*.md
plan_review_inputs:
  - .scratch/codex_prompts_plan_review/SYNTHESIS.md (cross-lens plan review, 5 Codex xhigh threads)
  - .scratch/codex_prompts_plan_review/REPORT_{sequencing,scope,file_accuracy,tests,risk}.md
status: post-review v3 (post-simplification pass); single operator; one consolidated commit
estimated_time: 5-7 hours (after simplification cuts; v2 was 9-13 hr)
shell_environment: Git Bash (Windows). Where commands are PowerShell-incompatible the plan flags it inline; default to Git Bash unless told otherwise.
simplification_inputs:
  - .scratch/simplification_proposal.md (first-principles pass; 5 cuts approved + 2 withdrawn + 7 open Qs resolved)
---

# Summary

Tier-R2-0 closes the cloud-spend gate on the implementation side by hardening the
three operational scripts that the WS1 cloud Stage 0/1 sign-off depends on
(`ws1_pin_fleet.py`, `ws1_finalize_run_manifest.py`, `ws1_run_logprob.py`),
fixing the wrong-analysis-unit bug in the planning power calculator
(`simulate_phase8_power.py`), and bundling two contract-level renames
(`cutoff_observed` → `exposure_horizon_observed`; `PerturbationVariant.C_FO` →
`C_CO`, plus the source-side `E_FO` → `E_OR` sweep across modified files) that
touch `src/r5a/contracts.py` so the file is opened only once.
Exit criteria: (a) `pytest tests/r5a -q` all green; (b)
`python scripts/smoke_phase7.py --check-config` reports clean
12 white-box / 4 black-box / 14 P_predict / 12 P_logprob / 2 confirmatory PCSG
pairs without warnings; (c) `python scripts/ws1_run_logprob.py --help` shows
`--exposure-horizon-probe` instead of `--cutoff-probe`; (d) one consolidated
commit on `main` and pushed to `origin/main`. After this commit lands, only
user-side actions (HF Meta license click-through; CLS post-2026-02 corpus
extraction) remain before WS1 cloud Stage 0 commit.

**This is post-review v3 (post-simplification pass).** v2 was reviewed by
5 parallel Codex `xhigh` threads. v3 then ran a first-principles
simplification pass against the actual single-operator + pre-cloud-spend +
paper-driven threat model and absorbed 5 approved cuts:

- **C.1**: Step B.23 keeps only `tempfile + os.replace` atomic rename;
  cross-platform file-locking primitive + sentinel `.lock` + stale-lock
  recovery + Codex MCP design-help escalation cut (single-operator manual
  pinner has no concurrency).
- **C.2**: Block F test density 50-56 → ~25-30. F.35's 9 per-clause hard-fail
  tests collapse into 1 multi-clause integration test + 1 happy-path test
  (better tests the multi-line-collection contract from Decision #1).
- **C.3**: Step C.16 (canonical-JSON `_hash_strings`) cut; case_id is
  programmatically generated ASCII identifiers, no newline collision risk.
- **C.4**: Step C.14 realized-N keys cut; clause #6 already enforces
  realized == eligible in confirmatory mode, dev-mode is marked by
  `mode="dev"` field.
- **C.5**: Step C.18 (two decision-#11 memo edits) pushed to Tier-R2-1
  Block G doc sweep (those memo files are heavily edited there for other
  reasons).
- **Q4**: Step B.25 (post-patch equality assertion) cut + F.34 #10;
  pin-field domain is hex-only, the YAML round-trip-quirk scenario is
  structurally impossible.
- **Q7**: F.39 `test_pcsg_pairs_empty_lists_and_hash` cut; production
  path never hits empty pcsg_pairs.

C.6 (output-key rename push) and C.7 (subprocess mandate cut) were
withdrawn after walkthrough exposed two anti-patterns: (1) "no downstream
consumer" doesn't imply "deferring is cheaper" — bundling at the open file
wins; (2) when the plan already says what you'd recommend, your "cut" is
no-op rewording. v2's prior amendments (Block C reordering, Block B/C
"validate after each substep" advice removal, Step D.10 `.gitignore`,
extended `E_FO`→`E_OR` source-side sweep, `gpu_dtype` clause 8, Windows
hazard flags, soft/mid/hard rollback tiers) all survive into v3. Full
trail in `.scratch/codex_prompts_plan_review/SYNTHESIS.md` (v2 review)
and `.scratch/simplification_proposal.md` (v3 simplification).

# Step 0 — Pre-flight

**Shell**: Git Bash. The plan uses bash idioms (HEREDOC, `grep`, `git ... |
grep`) throughout; running these in PowerShell will syntax-error or silently
behave differently. PowerShell equivalents are noted inline only where
unavoidable.

Before starting any sub-step (Git Bash):

```bash
git status                              # working tree clean except untracked .scratch/
git rev-parse HEAD                      # must equal 8350d9e2bcf9eec3e6388b8c8c20004cb5eb1bf2
git branch --show-current               # main
conda activate rag_finance              # idempotent: re-run even if already active
python -c "import sys; print(sys.executable)"   # must include 'rag_finance' in path
pytest tests/r5a -q                     # baseline: all green at 8350d9e
```

Acceptance: all six commands pass; baseline pytest is green so any later red
is attributable to this batch.

**Partially-done batch detection**: if `pytest tests/r5a -q` is RED at
baseline OR `git status` shows modified Tier-R2-0 files (anything under
`src/r5a/`, `scripts/`, or `tests/r5a/`), a previous attempt of this batch
was started but not committed. Two options:
1. Resume that attempt by reading the modified files and locating the last
   completed step. Risky if you don't remember exactly where you stopped.
2. Discard everything and restart cleanly: `git restore --source=HEAD
   --staged --worktree -- src/ scripts/ tests/ && git clean -fd src/
   scripts/ tests/`. Safer.

If anything other than `.scratch/` is modified or untracked, stop and pick
one of the two before starting — Tier-R2-0 is one consolidated commit and
stray work would either contaminate it or be lost on rollback.

---

# Block A — Contracts + Fleet (~1.5-2 hr)

**Bundling rationale**: `src/r5a/contracts.py` is touched here for new fields
(decisions #1, #2), tightening (R2-U1), and two renames (decisions #5, #10);
opening the file once is cleaner than three passes. The PCSG validator
extension (`fleet.py`) and the matching test contract update belong with the
schema change so the test surface tracks the schema.

## Step A.1 — RunManifest schema additions, tightening, and renames

**⚠ ATOMIC PAIR**: A.1 must be paired with A.3 — between A.1 and A.3 the contract
test will be RED because the schema has changed but the test fixture still
uses the old names. Do not run pytest between A.1 and A.3. They are one logical
change.

**⚠ ATOMIC PAIR (separate)**: After A.1, the finalizer's RunManifest
constructor (in `scripts/ws1_finalize_run_manifest.py:373`) still uses
`cutoff_observed=...` keyword, so the script will runtime-error until C.10
+ C.12 land. Either pair A.1 with the C.10 constructor edit (Step C.10
sub-step 4 in the new ordering) as part of the same atomic change, or accept
that `python scripts/ws1_finalize_run_manifest.py` is broken until Block C
completes (Block A test green is sufficient gating).

**File:** `src/r5a/contracts.py`

Edits, in source order:

| Lines (current) | Change | Source decision |
|---|---|---|
| 42 | `C_FO = "c_fo"` → `C_CO = "c_co"` (rename enum identifier and value string) | Decision #10 |
| 154 | Update `PerturbationArtifact` docstring: `"Output of C_FO / C_NoOp generators"` → `"Output of C_CO / C_NoOp generators"` | Decision #10 |
| 386-414 (RunManifest docstring) | Add a "2026-04-30 R2 amendments" paragraph cross-referencing R5A_DESIGN_REVIEW_R2_20260429/DECISIONS.md (decisions #1, #2, #5, #11) | Decision #1, #2, #5, #11 |
| 446 | `cutoff_observed: dict[str, date \| None]` → `exposure_horizon_observed: dict[str, date \| None]` (field rename + matching docstring text) | Decision #5 |
| 449 | `pcsg_pair_registry_hash: str \| None = None` → `pcsg_pair_registry_hash: str` (no default; required field) | R2-U1 |
| New (after 451) | Add `mode: Literal["confirmatory", "dev"] = "confirmatory"` | Decision #1 |
| New (after `mode`) | Add `fleet_p_predict_eligible: list[str] = Field(default_factory=list)` | Decision #2 |
| New | Add `fleet_p_logprob_eligible: list[str] = Field(default_factory=list)` | Decision #2 |

**Acceptance criterion**: file imports cleanly (`python -c "from src.r5a.contracts import RunManifest, PerturbationVariant; assert PerturbationVariant.C_CO.value == 'c_co'"`); `RunManifest.model_fields` is a superset of the prior fields with `cutoff_observed` removed and `exposure_horizon_observed`, `mode`, `fleet_p_predict_eligible`, `fleet_p_logprob_eligible` added; `pcsg_pair_registry_hash` annotation no longer accepts `None`. Test contract is RED; that is expected — proceed to A.3.

**Notes**: do NOT rename `cutoff_date_yaml` (decision #5 explicitly excludes it; that field mirrors the operator-declared YAML value and `cutoff` is the correct word there). The `quant_scheme: dict[str, str]` field is unchanged. `quality_gate_thresholds` keeps its current `dict[str, int]` typing — Block C drops the WS6 keys at the population site, not the schema level.

## Step A.2 — Fleet PCSG validator: reject duplicate members and self-pairs

**File:** `src/r5a/fleet.py:163-212` (the `_validate_pcsg_pairs` `model_validator`)

Add at the end of each role branch (before the `for ref in refs:` loop), insert
a uniqueness check:

```python
if len(set(refs)) != len(refs):
    raise ValueError(
        f"PCSG pair {pair.id!r} has duplicate members in {refs!r}; "
        "members must be distinct"
    )
```

This catches both `temporal` self-pairs (`early == late`) and `capacity` pairs
with `members: [x, x]`. Place it inside each branch (after the `refs = ...`
assignment but before the resolution loop) so the error message can name the
pair.

**Acceptance criterion**: a fleet YAML with `members: [qwen2.5-7b, qwen2.5-7b]`
or with `early: qwen2.5-7b, late: qwen2.5-7b` raises `ValidationError` matching
`duplicate members`. Existing valid fleet YAML (`config/fleet/r5a_fleet.yaml`)
continues to load.

**Reference**: R2-U2 (Lens A major #2).

## Step A.3 — Update RunManifest contract test

**File:** `tests/r5a/test_run_manifest_contract.py`

Edits:

1. **Lines 19-50 `REQUIRED_FIELDS`**: remove `"cutoff_observed"`; add
   `"exposure_horizon_observed"`, `"mode"`, `"fleet_p_predict_eligible"`,
   `"fleet_p_logprob_eligible"`.

2. **Line 82-86 `test_run_manifest_extra_forbid`**: tighten per Lens D suggested
   outline §"test_run_manifest_extra_forbid_specific_error" (R2-U12). Replace
   with:

   ```python
   def test_run_manifest_extra_forbid():
       bad = {**_baseline_kwargs(), "this_field_does_not_exist": "oops"}
       with pytest.raises(ValidationError) as exc_info:
           RunManifest.model_validate(bad)
       errs = exc_info.value.errors()
       assert any(e["loc"] == ("this_field_does_not_exist",) for e in errs)
       assert any(e["type"] == "extra_forbidden" for e in errs)
   ```

3. **Lines 89-101 `test_run_manifest_minimum_construction`**: rename assertion
   on `manifest.cutoff_observed == {}` → `manifest.exposure_horizon_observed == {}`;
   change `assert manifest.pcsg_pair_registry_hash is None` to a positive
   construction (the field is now required `str`); add assertions on the new
   fields:

   ```python
   assert manifest.mode == "confirmatory"
   assert manifest.fleet_p_predict_eligible == []
   assert manifest.fleet_p_logprob_eligible == []
   ```

   And update `_baseline_kwargs()` (lines 53-68) to provide
   `pcsg_pair_registry_hash="p" * 64` so a baseline manifest constructs without
   `ValidationError`.

4. **Lines 104-124 `test_run_manifest_full_population`**: rename
   `cutoff_observed=...` keyword arg to `exposure_horizon_observed=...`; assert
   on the renamed attribute; add `mode="confirmatory"` and
   `fleet_p_predict_eligible=[...]`, `fleet_p_logprob_eligible=[...]` keyword
   args with realistic values (e.g., `["qwen2.5-7b", "deepseek-v3"]`,
   `["qwen2.5-7b"]`).

5. Add a new test `test_run_manifest_field_set_pinned` per Lens D suggested
   outline (the `assert actual == expected` form, not just subset):

   ```python
   def test_run_manifest_field_set_pinned():
       assert set(RunManifest.model_fields) == REQUIRED_FIELDS
   ```

   This catches future drift in either direction (a missing field OR an
   un-pinned new field).

6. Add a new test `test_run_manifest_json_roundtrip_preserves_horizon_dates`
   per Lens D suggested outline (replaces `cutoff_observed` with
   `exposure_horizon_observed` in the construction):

   ```python
   def test_run_manifest_json_roundtrip_preserves_horizon_dates():
       m = RunManifest(
           **_baseline_kwargs(),
           exposure_horizon_observed={"a": date(2023, 10, 31), "b": None},
       )
       payload = m.model_dump(mode="json")
       reloaded = RunManifest.model_validate(json.loads(json.dumps(payload, sort_keys=True)))
       assert payload["exposure_horizon_observed"] == {"a": "2023-10-31", "b": None}
       assert reloaded.exposure_horizon_observed == {"a": date(2023, 10, 31), "b": None}
   ```

   (Add `import json` and `from datetime import date` at the top.)

**Acceptance criterion**: `pytest tests/r5a/test_run_manifest_contract.py -q` is
green after Step A.1 + A.3. If red, ALL Block A code edits are wrong; do not
proceed past Block A.

## Step A.4 — Extend `tests/r5a/test_fleet_config.py` with self-pair / duplicate-member tests

**File:** `tests/r5a/test_fleet_config.py`

Append three tests after line 190:

1. `test_pcsg_capacity_pair_rejects_duplicate_members` — capacity pair with
   `members: ["qwen2.5-7b", "qwen2.5-7b"]` raises with `"duplicate members"`
   in message. Modify `_base_yaml()` to include the necessary capacity context
   or reuse the existing temporal pair structure.
2. `test_pcsg_temporal_pair_rejects_self_pair` — temporal pair with
   `early: "qwen2.5-7b", late: "qwen2.5-7b"` raises with `"duplicate members"`.
3. `test_model_participation_predicates_direct` — per Lens D suggested outline
   B.19. Build a fleet with one full-operator white-box, one P_logprob-only
   white-box, one black-box; assert each predicate
   (`participates_in_p_predict`, `participates_in_p_logprob`) returns the
   expected boolean for each model.

Also tighten existing role-shape tests at lines 120-138 (R2-U on Lens D #5):
replace `pytest.raises(Exception)` with
`pytest.raises(ValidationError, match="must not declare 'members'")` for the
temporal-with-members case, and similar for capacity-without-members.

**Acceptance criterion**: `pytest tests/r5a/test_fleet_config.py -q` green;
five of the seven existing tests still match their assertions, two role-shape
tests now use specific message matchers.

## Step A.5 — `E_FO` → `E_OR` source-side comment / docstring sweep (decision #10 source-side)

DECISIONS.md decision #10 calls for a "full enum rename" (`E_FO` → `E_OR`,
`C_FO` → `C_CO`). A.1 covered the `PerturbationVariant` enum. This step covers
the `E_FO` references in code/comments/docstrings of files that are already
modified by Tier-R2-0 (so we open them only once). Plan / memo / fixture /
WS3-spec body sweep remains Tier-R2-1.

**Files and edits**:

1. `src/r5a/fleet.py:70` — comment "P_predict-driven estimands (E_CMMD, E_FO, E_NoOp, E_extract)" → "(E_CMMD, E_OR, E_NoOp, E_extract)".
2. `src/r5a/fleet.py:123` — same comment in `p_predict_eligible_ids` docstring; rename `E_FO` → `E_OR`.
3. `src/r5a/estimands/__init__.py:4` — module docstring "E_FO, E_NoOp are populated in WS4/WS5..." → "E_OR, E_NoOp are populated in WS4/WS5...".
4. `config/fleet/r5a_fleet.yaml` (header comment near line 29 if present, otherwise wherever `E_FO` appears in the YAML comments) — rename to `E_OR`.

**Note**: `scripts/ws1_finalize_run_manifest.py` and `scripts/simulate_phase8_power.py` also have `E_FO` references — those are addressed in Step C.14 (threshold dict keys) and Step E.30 (output JSON row label) respectively, where the file is being touched anyway.

**Acceptance criterion**: `grep -rn 'E_FO\|e_fo' src/r5a/ src/r5a/estimands/ src/r5a/fleet.py config/fleet/` returns zero hits (in modified files). `grep -rn '"c_fo"\|C_FO' src/ scripts/ tests/` returns zero hits.

**Reference**: Decision #10 source-side; Lens 3 (file_accuracy) finding "Missing rename sites — C_FO / E_FO".

---

# Block D — Path E rename (~1 hr; do early to decouple Block C)

**Bundling rationale**: doing the Path E rename right after Block A means
Block C (finalizer hardening) can be written against the new
`exposure_horizon_observed` field name and the new `data/pilot/exposure_horizon/`
default. Doing it after Block C would force a second pass through the
finalizer.

## Step D.5 — Rename analysis module file and its dataclass / function names

1. **`git mv src/r5a/analysis/cutoff_probe.py src/r5a/analysis/exposure_horizon.py`**
2. Inside the renamed file (now `exposure_horizon.py`):
   - Rename `class CutoffEstimate` → `class ExposureHorizonEstimate`.
   - Rename fields: `cutoff_observed` → `horizon_observed`,
     `cutoff_ci_lower` → `horizon_ci_lower`, `cutoff_ci_upper` →
     `horizon_ci_upper`, `cutoff_ci_width_months` →
     `horizon_ci_width_months`. The `drop_*`, `kappa_hat_index`,
     `n_months`, `n_articles`, `notes`, `model_id`, `p_drop_gt_005` fields
     keep their current names (they describe the observed familiarity drop or
     are meta-data, not the cutoff date).
   - Rename `def detect_cutoff(...)` → `def detect_exposure_horizon(...)`.
   - Update the module docstring's first paragraph: replace
     "Path-E empirical cutoff probe" with
     "Path-E empirical exposure-horizon probe" and refresh the §2.4 reference
     to point to DECISIONS.md decision #5 with `2026-04-30` date.

**Acceptance criterion**: `python -c "from src.r5a.analysis.exposure_horizon import detect_exposure_horizon, ExposureHorizonEstimate"` succeeds; `from src.r5a.analysis.cutoff_probe import detect_cutoff` raises `ModuleNotFoundError`.

## Step D.6 — Rename test file and update imports

**⚠ ATOMIC PAIR with D.5**: between `git mv` of the analysis module and updating the test file's imports, full pytest is RED because `test_cutoff_probe.py` imports the now-removed module. Don't run pytest between D.5 and D.6.

1. **`git mv tests/r5a/test_cutoff_probe.py tests/r5a/test_exposure_horizon.py`**
2. Inside the renamed test file:
   - `from src.r5a.analysis.cutoff_probe import detect_cutoff, month_stratified_mink`
     → `from src.r5a.analysis.exposure_horizon import detect_exposure_horizon, month_stratified_mink`
   - All `detect_cutoff(...)` calls → `detect_exposure_horizon(...)` (line 100, 131, 152, 164, 171, 187 — verify with grep).
   - All `est.cutoff_observed` / `est.cutoff_ci_*` → `est.horizon_observed` / `est.horizon_ci_*` accesses.
   - Function names: rename `test_detect_cutoff_*` → `test_detect_exposure_horizon_*` (six tests).
   - Module docstring lines 1, 5 (any `cutoff_probe` references): update to `exposure_horizon`.

**Acceptance criterion**: `pytest tests/r5a/test_exposure_horizon.py -q` green
(7 tests pass with the new names against the renamed module).

## Step D.7 — Rename Path E analysis script + update its defaults and field names

1. **`git mv scripts/run_cutoff_probe_analysis.py scripts/run_exposure_horizon_analysis.py`**
2. Inside the renamed script:
   - Imports: `from src.r5a.analysis.cutoff_probe import detect_cutoff, month_stratified_mink`
     → `from src.r5a.analysis.exposure_horizon import detect_exposure_horizon, month_stratified_mink`
   - Module docstring: update path references and the reference to
     SYNTHESIS / DECISION memo (point to DECISIONS.md §"Decision #5").
   - **Line 47-48 `--probe-set` default**: `data/pilot/cutoff_probe/probe_set_monthly60_36mo.json`
     → `data/pilot/exposure_horizon/probe_set_monthly60_36mo.json`.
   - **Line 53-55 `--traces-dir` default**: `data/pilot/logprob_traces` →
     `data/pilot/exposure_horizon/traces` (closes R2-C1; the runner already
     writes to `data/pilot/cutoff_probe/traces/`, so this is a coordinated
     dir-rename + default-fix).
   - **Line 58-65 `--output` default**: `data/pilot/cutoff_probe/cutoff_observed.json`
     → `data/pilot/exposure_horizon/horizon_observed.json`.
   - **Line 67-69 `--trace-pattern` default**: `{model}__cutoff_probe.parquet`
     → `{model}__exposure_horizon.parquet` (matches Step D.8 below).
   - **Line 102-105 `--drop-threshold`**: keep value but rename the JSON
     output field per below (Lens A minor #3 + R2-C1 follow-on).
   - **Line 158-177 `summary[model_id]` dict**: rename JSON keys
     `cutoff_observed` → `horizon_observed`, `cutoff_ci_lower` →
     `horizon_ci_lower`, `cutoff_ci_upper` → `horizon_ci_upper`,
     `cutoff_ci_width_months` → `horizon_ci_width_months`. Rename
     `p_drop_gt_005` → `p_drop_gt_threshold` (Lens A minor #3; threshold-neutral
     output naming since the threshold is configurable).
   - **Add R2-C2 #1**: in the output dict (line 186-198), include per-trace
     SHA256 + probe-set hash. Concretely:
     ```python
     "trace_shas": {model_id: hashlib.sha256(path.read_bytes()).hexdigest() for ... },
     "probe_set_sha256": hashlib.sha256(args.probe_set.read_bytes()).hexdigest(),
     ```
     Add `import hashlib` if missing. Insert before `args.output.write_text`.
   - **Add R2-C1 follow-on (validate models against fleet)**: at the top of
     `main()`, after `targets = _resolve_models(args)`, validate that every
     resolved `model_id` is in `fleet.p_logprob_eligible_ids()`. Load the
     fleet via `from src.r5a.fleet import load_fleet` with a new
     `--fleet config/fleet/r5a_fleet.yaml` argparse option. Reject extras
     with `SystemExit`.

**Acceptance criterion**: `python scripts/run_exposure_horizon_analysis.py --help` parses; the renamed script is the only consumer; `python scripts/run_cutoff_probe_analysis.py --help` fails with `No such file` (Bash) / similar (PowerShell). The script enforces fleet membership for the analyzed model list.

## Step D.8 — Rename Path E CLI flags in `scripts/ws1_run_logprob.py`

**File:** `scripts/ws1_run_logprob.py`

Edits:

1. **Module docstring lines 20-29**: replace `--cutoff-probe` references with
   `--exposure-horizon-probe`; replace `data/pilot/cutoff_probe/traces/` with
   `data/pilot/exposure_horizon/traces/`; replace "Path E empirical cutoff
   probe" with "Path E empirical exposure-horizon probe"; remove "SYNTHESIS
   Tier-0 #5" reference and replace with DECISIONS.md decision #5.
2. **Line 142-151 `--cutoff-probe` argument**: rename arg name to
   `--exposure-horizon-probe`; update `args.cutoff_probe` references throughout
   to `args.exposure_horizon_probe` (occurrences at lines 218, 221, 266, 286,
   etc.).
3. **Line 164-167 `--cutoff-probe-fixture`**: rename to
   `--exposure-horizon-fixture`. Default path:
   `data/pilot/cutoff_probe/probe_set_monthly60_36mo.json` →
   `data/pilot/exposure_horizon/probe_set_monthly60_36mo.json`.
4. **Line 174-177 `--cutoff-probe-output-dir`**: rename to
   `--exposure-horizon-output-dir`. Default path:
   `data/pilot/cutoff_probe/traces` → `data/pilot/exposure_horizon/traces`.
5. **Line 282-295 `_resolve_output_paths` `mode_tag`**: rename
   `mode_tag = "cutoff_probe"` → `mode_tag = "exposure_horizon"` (this is what
   makes the output filename `*__exposure_horizon.parquet`, matching Step D.7's
   `--trace-pattern` default).
6. **Line 221 `mode_label`**: rename `--cutoff-probe` to `--exposure-horizon-probe`.

**Acceptance criterion**: `python scripts/ws1_run_logprob.py --help` shows
`--exposure-horizon-probe`, `--exposure-horizon-fixture`,
`--exposure-horizon-output-dir`; does NOT show `--cutoff-probe`. Mutually
exclusive group still requires one of `--smoke / --pilot / --exposure-horizon-probe`.

## Step D.9 — Update `scripts/build_cutoff_probe_set.py` to write to renamed dir

**File:** `scripts/build_cutoff_probe_set.py`

Conservative edit (per Tier-R2-0 scope; do NOT rename the script file itself —
that's Tier-R2-1 doc-side cleanup):

1. **Module docstring line 7**: update path reference
   `Knee detection + cutoff_observed extraction happens in scripts/run_cutoff_probe_analysis.py`
   → `Knee detection + exposure-horizon extraction happens in scripts/run_exposure_horizon_analysis.py`.
2. **Default output path** (search for `data/pilot/cutoff_probe`): update to
   `data/pilot/exposure_horizon` so that a fresh run lands in the renamed dir.

**Acceptance criterion**: `python scripts/build_cutoff_probe_set.py --help`
shows the renamed default path; the file's own name is unchanged (not in
Tier-R2-0 scope).

## Step D.10 — Update `.gitignore` for renamed Path E data dir

**File:** `.gitignore`

Edits:

1. Search for `data/pilot/cutoff_probe` entries; rename them all to
   `data/pilot/exposure_horizon`. If the file ignored `data/pilot/cutoff_probe/`
   (either with or without trailing slash, and possibly multiple variants),
   replace with `data/pilot/exposure_horizon/`.
2. If `data/pilot/cutoff_probe/` is NOT in `.gitignore` but the runner has
   already written there at any point, the operator should `git status` to
   see if any files in the old dir are tracked; if so, `git rm -r --cached
   data/pilot/cutoff_probe/` and let the new ignore line take over.

**Acceptance criterion**: `grep cutoff_probe .gitignore` returns no matches; `grep exposure_horizon .gitignore` returns at least one match.

**Reason**: per Lens 1 (sequencing) C-1 finding — without this update, `git
add -A` in Step 44 risks staging large generated Path E artifacts in the
renamed dir.

---

# Block C — Finalizer hardening (~1.5-2 hr; HIGH-RISK SURFACE; v3 reduced from v2 2-2.5 hr after C.14 / C.16 / C.18 cuts)

**Risk flag**: this block has the highest regression risk in Tier-R2-0. The
finalizer is the one artifact joining "fleet + traces + Path E + provenance".
Many gates are added; over-restriction breaks dev/smoke finalization;
under-restriction reopens the cloud-spend gate.

**Execution model**: the helper sub-steps (C.10 traces-dir, C.11 horizon JSON)
come first because the framework sub-step (C.12 mode + 7-clause hard-fail)
calls them. Validation strategy: at end of each sub-step, run any test
files that ALREADY exist (Step F.35 doesn't exist until Block F lands —
do NOT try to run it mid-Block-C). When all of Block C is done, run
`pytest tests/r5a -q` against the existing test surface; expected partial
green state is documented in the per-step "Acceptance criterion" lines.
The full Block F coverage validates the new code at Block G.

## Step C.10 — Validate `--traces-dir` against P_logprob fleet (clause 6 helper)

**File:** `scripts/ws1_finalize_run_manifest.py`

This is the **first** sub-step of Block C — it produces the `traces` mapping
that C.12's hard-fail framework will consume.

Edits:

1. **Add helper** `_validate_traces_dir(traces_dir: Path, expected_models: list[str], *, mode: Literal["confirmatory", "dev"]) -> dict[str, str]`:
   - Returns mapping `model_id -> trace_path` for the realized set.
   - In `mode == "dev"`: tolerate missing dir or partial coverage; return whatever is present.
   - In `mode == "confirmatory"`:
     - Iterate `expected_models`; for each, check `traces_dir / f"{model_id}__pilot.parquet"` exists. If missing, append to error list.
     - Glob `traces_dir/*__pilot.parquet`; reject any parquet whose `model_id` (filename prefix before `__pilot`) is not in `expected_models`.
     - If error list is non-empty: raise `SystemExit` with a multi-line message listing all missing AND all unexpected files.
2. **In `main()`**: read `--traces-dir` (currently declared but unused around line 73-77). Pass `fleet.p_logprob_eligible_ids()` as `expected_models` and the new `mode` variable (added in C.12 — for now read it as `"dev" if args.allow_tbd else "confirmatory"` directly). Store the returned dict as `traces` for downstream use.
3. **Compute trace SHAs**: for each realized trace parquet in the returned dict, compute SHA-256 (use existing `_sha256_file` with 64 KB chunks). Plumb the realized set length into Step C.14's realized-N alongside eligible-N.

**Acceptance criterion**: with `--allow-tbd` (dev), missing `--traces-dir` is tolerated. Without `--allow-tbd` (confirmatory), a partial / empty dir raises `SystemExit` with the missing model list. The `traces` local in `main()` is populated.

**Reference**: R2-C2 #1 trace coverage; Lens A critical #2.

## Step C.11 — Validate exposure-horizon JSON against P_logprob fleet (clause 5 helper)

**File:** `scripts/ws1_finalize_run_manifest.py`

This is the **second** sub-step — it produces the `exposure_horizon` mapping
that C.12 consumes.

Edits:

1. **Rename CLI arg** `--cutoff-observed` (line 78) → `--exposure-horizon`. Local variable `args.cutoff_observed` → `args.exposure_horizon`.
2. **Rename helper** `_read_cutoff_observed` (line 142-163) → `_read_exposure_horizon`. Update its signature to also take `fleet` and `mode` parameters. Update its docstring.
3. **Inside the renamed helper** (current line 147-162): iterate the JSON `summary` dict keys; rename the read field from `co = row.get("cutoff_observed")` to `co = row.get("horizon_observed")`. Change the `Date.fromisoformat(co)` branch's silent `None` fallback (line 160-162) to raise `SystemExit(f"invalid horizon date {co!r} for {model_id}")` in confirmatory mode (R2-C2 #2). In dev mode keep the current `None` fallback.
4. **Add fleet-key validation**: after building `out`, in `mode == "confirmatory"`, raise `SystemExit` if `set(out.keys()) != set(fleet.p_logprob_eligible_ids())` listing extras AND missing.
5. **Update finalizer's top-of-file docstring** (lines 14, 34, 39): update the example paths from `data/pilot/cutoff_probe/cutoff_observed.json` to `data/pilot/exposure_horizon/horizon_observed.json` (Lens 3 file_accuracy finding: documentation drift).
6. **In `main()`**: rename local `cutoff_observed` → `exposure_horizon`. Pass to the renamed helper. Store the returned dict for downstream use.

**Acceptance criterion**: confirmatory finalize fails when `--exposure-horizon` JSON has a non-fleet model key, missing model key, or invalid date string. Dev mode tolerates partial JSON.

**Reference**: R2-C1 (Path E composition), R2-C2 #2 (silent date drop), decision #5 (rename).

## Step C.12 — Add `mode`-aware confirmatory hard-fail framework (decision #1)

**File:** `scripts/ws1_finalize_run_manifest.py`

This is the **third** sub-step of Block C — by now C.10 has produced
`traces` and C.11 has produced `exposure_horizon` for the framework to
consume.

Edits:

1. **Line 105-110 `--allow-tbd` argparse**: keep the flag as-is; update help text to document it sets `mode="dev"`.
2. **In `main()`** (after `args = parse_args()` and the existing fleet/runtime loading): compute `mode: Literal["confirmatory", "dev"] = "dev" if args.allow_tbd else "confirmatory"`. Pass this through to the `RunManifest(...)` constructor at the bottom.
3. **Implement `_confirmatory_hard_fail(args, fleet, traces, exposure_horizon, launch_env, sampling_config) -> None`** which raises `SystemExit` with a multi-line error message listing every failed clause. **Each failed clause MUST be prefixed with `[clause N]`** (N = 1..8) on its own line in the SystemExit message. This format is required for (a) unambiguous test assertion in F.35 #1 (substring "git" or "trace" would risk coincidental matches; "[clause 3]" cannot collide), and (b) operator readability when the finalizer rejects a real run. Example multi-line error:

   ```
   fleet not ready for confirmatory finalize:
     [clause 1] git_commit_sha is all-zero (run from a non-git checkout?)
     [clause 3] tokenizer_sha is "<TBD>" for qwen2.5-7b — run scripts/ws1_pin_fleet.py
     [clause 8] --gpu-dtype is required in confirmatory mode
   ```

   Eight clauses (decision #1's seven plus `gpu_dtype` per Lens A major #8 / plan §10.4):
   - **Clause 1**: `_git_commit_sha()` MUST NOT return `"0" * 40`. Modify `_git_commit_sha()` (line 114-121) to detect the failure case and raise from inside the helper when called in confirmatory mode (cleanest: add a `mode` parameter; or split into `_git_commit_sha_strict()` for confirmatory).
   - **Clause 2**: `args.vllm_image_digest` matches regex `^sha256:[0-9a-f]{64}$`. Add helper `_validate_image_digest(digest: str)` that raises if mismatch. Make `--vllm-image-digest` required when mode is confirmatory.
   - **Clause 3**: every `fleet.p_logprob_eligible_ids()` model is present in both `tokenizer_shas` (built from fleet YAML pinned values) and `white_box_checkpoint_shas`, both non-empty and not equal to `<TBD>`.
   - **Clause 4**: every `fleet.black_box_ids()` model has `api_model_name` non-empty and not `<TBD>`.
   - **Clause 5**: `set(exposure_horizon.keys()) == set(fleet.p_logprob_eligible_ids())`. Already enforced inside `_read_exposure_horizon` (Step C.11) — this clause is satisfied as a consequence; record in the hard-fail report for completeness.
   - **Clause 6**: `traces` dict (returned by Step C.10's `_validate_traces_dir`) has every `fleet.p_logprob_eligible_ids()` model mapped to a real trace path. Already enforced inside `_validate_traces_dir` — same as clause 5, this is satisfied as a consequence.
   - **Clause 7**: `launch_env` dict contains both `CUDA_VISIBLE_DEVICES` and `VLLM_VERSION` keys.
   - **Clause 8 (added per Lens A major #8 + plan §10.4)**: `args.gpu_dtype` is non-empty and non-`<TBD>` (e.g., `"bf16"`, `"fp16"`). Make `--gpu-dtype` required when mode is confirmatory.

   Call `_confirmatory_hard_fail(...)` once after all input loading and after C.10 + C.11 helpers have produced `traces` and `exposure_horizon`. Skip the call when `mode == "dev"`.

4. **In RunManifest construction (line 352-379)**: add `mode=mode` and rename `cutoff_observed=cutoff_observed` → `exposure_horizon_observed=exposure_horizon`. Use the local variable names produced by C.10 and C.11.

**Acceptance criterion**: passing `--allow-tbd` yields a manifest with `mode="dev"` and skips the 8-clause check. Running without `--allow-tbd` against a fleet/inputs with any failure raises `SystemExit` with a multi-line message listing every failed clause. Test outline at Step F.35 #1 (multi-clause integration test directly verifies the multi-line collection contract).

**Reference**: Decision #1; R2-C2 (multiple finalizer gaps); Lens A critical #2 + major #8.

## Step C.13 — Hidden-state subset hash: hash frozen JSON, not filesystem order

**File:** `scripts/ws1_finalize_run_manifest.py`

Edits:

1. **Replace `_hidden_state_subset_hash` (line 166-185)** entirely. New
   signature:
   ```python
   def _hidden_state_subset_hash(
       hidden_states_dir: Path,
       expected_models: list[str],
       expected_case_count: int = 30,
       *,
       mode: Literal["confirmatory", "dev"],
   ) -> tuple[str | None, int]:
       """Hash the WS6 hidden-state subset.

       On-disk layout `{hidden_states_dir}/{case_id}__{model_id}.safetensors`
       is COUPLED to `OfflineHFBackend._save_hidden_states`
       (`src/r5a/backends/offline_hf.py` line ~260). If the layout
       convention is ever updated, both this function AND the backend
       writer MUST change together — F.35 #7 fixture is constructed
       directly (does not exercise the backend) and will not catch
       drift between writer and reader.
       """
   ```
   New logic (per Lens C C.17 + decision #1 clause):
   - If dir missing or empty AND mode=dev: return `(None, 0)`.
   - If dir missing or empty AND mode=confirmatory: raise `SystemExit`.
   - Probe each model in `expected_models`. The on-disk layout per
     `OfflineHFBackend._save_hidden_states` is flat
     `{case_id}__{model_id}.safetensors` under the dir. For each model,
     glob `{hidden_states_dir}/*__{model_id}.safetensors`, extract
     `case_id` from the leading filename token.
   - Verify: every model has exactly `expected_case_count` cases AND every
     model has the same case set. In confirmatory mode, raise `SystemExit`
     listing per-model missing case_ids.
   - Hash: `_hash_strings(sorted(case_ids))` (the existing `\n`-join helper; v3 keeps it per simplification C.3 — case_id values are programmatically generated ASCII identifiers without newlines).

2. **In `main()` (line 294-300)**: pass `fleet.p_logprob_eligible_ids()` as `expected_models` and `mode` from the variable computed in Step C.12.

**Acceptance criterion**: smoke run with a fixture dir holding the expected_models with `expected_case_count` cases each returns a stable hash; missing model or case_count mismatch raises in confirmatory mode; the same partial dir returns `(None, 0)` in dev mode (Step F.35 #7 covers fixture).

**Note for Step F.35 fixture authors**: the test should pass `expected_models=["m1", "m2"]` and a `expected_case_count` matching the fixture, NOT the production 12-model / 30-case values — the fixture controls what `expected_models` is for the test invocation.

**Reference**: R2-C2 #3, Lens C C.17, Lens A critical #4.

## Step C.14 — Drop ws6 keys + rename `e_fo_*` keys to `e_or_*`

**File:** `scripts/ws1_finalize_run_manifest.py`

**v3 simplification**: realized-N keys cut per `.scratch/simplification_proposal.md` C.4. Confirmatory hard-fail clause #6 already enforces realized == eligible at the framework level; dev mode is marked by `mode="dev"` field. Recording realized-N alongside eligible-N is structural redundancy — plan v2 itself acknowledged in sub-step 5 that "if not yet derivable, set equal to eligible". Function signature stays at `(n_p_predict, n_p_logprob)` two arguments.

Edits:

1. **`_quality_gate_thresholds` (line 196-217)**: keep the existing 2-argument signature. Output dict keys (final, after ws6 drop + e_fo→e_or rename):
   - `e_extract_main_text_promotion_n_p_predict`
   - `e_extract_main_text_threshold` (`_one_third_minimum(n_p_predict)`)
   - `e_extract_confirmatory_promotion_n_p_predict`
   - `e_extract_confirmatory_threshold` (`_strict_majority(n_p_predict)`)
   - `e_or_e_noop_informational_n_p_predict` (renamed from `e_fo_e_noop_*` per decision #10 source-side)
   - `e_or_e_noop_informational_threshold` (renamed from `e_fo_e_noop_*`)
2. **Drop ws6 fields** per decision #11: remove `ws6_mechanistic_n_white_box` and `ws6_mechanistic_threshold` from the returned dict.
3. **Rename `e_fo_e_noop_*` keys to `e_or_e_noop_*`** per decision #10 source-side. The old keys `e_fo_e_noop_informational_n_p_predict` and `e_fo_e_noop_informational_threshold` MUST NOT appear in the output. Update the in-code comment "Behavioral E_FO / E_NoOp gate condition 3 has been REMOVED" → "Behavioral E_OR / E_NoOp gate condition 3 has been REMOVED" (line 211).
4. **Module docstring `--perturbation-manifest` line 17**: rename `(optional) C_FO/C_NoOp output manifest` → `(optional) C_CO/C_NoOp output manifest` per decision #10.

**Acceptance criterion**: a partial hidden-state dir or partial traces dir is rejected at clauses 5/6 before manifest construction; ws6 keys do NOT appear in the output dict; **no key in the dict starts with `e_fo_`**; final dict has exactly 6 keys (3 gates × 2 entries each: promotion-N + threshold).

**Reference**: Lens C C.19 (mooted by C.4 cut); decision #11; decision #10 source-side; v3 simplification C.4.

## Step C.15 — Replace article-manifest hash misuse for `sampling_config_hash`

**File:** `scripts/ws1_finalize_run_manifest.py`

Edits:

1. **Add CLI arg** `--sampling-config` (default `config/pilot_sampling.yaml`).
2. **Hash the file**: `sampling_config_hash = _sha256_file(Path(args.sampling_config))`.
3. **At RunManifest construction (line 358)**: replace
   `sampling_config_hash=article_manifest_hash` with
   `sampling_config_hash=sampling_config_hash`.
4. **Confirmatory clause**: in `_confirmatory_hard_fail`, refuse if the
   sampling config file does not exist.

**Acceptance criterion**: `sampling_config_hash != article_manifest_hash` for
real run; missing sampling config raises in confirmatory mode.

**Reference**: R2-C2 #5, Lens A major #7.

## Step C.16 — [CUT v3]

**v3 simplification (cut per `.scratch/simplification_proposal.md` C.3)**: the canonical-JSON `_hash_strings` rewrite defended against case_id values containing `\n` causing hash collision. case_id is programmatically generated as `cls_<YYYY>_<MM>_<DD>_<seq>`-style ASCII identifiers with no whitespace; the collision input domain doesn't exist in this project. Keep the existing `"\n".join(sorted(items))` form. F.35 #17 (newline-collision test) also cut.

## Step C.17 — Populate split-tier roster fields (decision #2)

**File:** `scripts/ws1_finalize_run_manifest.py`

Edits:

1. **At RunManifest construction (line 352-379)**, populate:
   - `fleet_p_predict_eligible=fleet.p_predict_eligible_ids()`
   - `fleet_p_logprob_eligible=fleet.p_logprob_eligible_ids()`
   - `mode=mode` (from Step C.12)
2. **Update finalizer's stdout summary (line 388-396)**: print the realized roster lengths and the new `mode` so the operator sees what was recorded.

**Acceptance criterion**: a finalized manifest's two roster fields exactly match `fleet.p_predict_eligible_ids()` / `fleet.p_logprob_eligible_ids()`; the `mode` field equals `"confirmatory"` for non-`--allow-tbd` runs.

## Step C.18 — [CUT v3, pushed to Tier-R2-1]

**v3 simplification (cut per `.scratch/simplification_proposal.md` C.5)**: pushed to Tier-R2-1 Block G doc sweep. Both memo files (`docs/DECISION_20260429_llama_addition.md`, `docs/DECISION_20260427_pcsg_redefinition.md`) are heavily edited in Tier-R2-1 Block G for other reasons (cross-link headers, stale "10 white-box" residue, related_docs front-matter, §3.x text fixes). Bundling these two edits there is strictly cheaper than re-opening the files in Tier-R2-0 just for this. Tier-R2-0 commit no longer touches `docs/DECISION_20260427_*` or `docs/DECISION_20260429_llama_addition*`.

**Tier-R2-1 picks up** (DECISIONS.md §G.6 + §G.7 already enumerate these):
- `docs/DECISION_20260429_llama_addition.md` §2.6 WS6 row rewrite
- `docs/DECISION_20260427_pcsg_redefinition.md` §2.5 supersession note

Both edit bodies retained verbatim in `.scratch/simplification_proposal.md` C.5.

---

# Block B — Pin-fleet hardening (~1-1.5 hr; HIGH-RISK SURFACE; v3 reduced from v2 2-3 hr after B.23 lock cut + B.25 cut)

**Risk flag**: file locking + atomic rename + scalar serialization is
fiddly. Many of these edits change error semantics (`SystemExit` instead of
silent skip), which can break dev workflows.

**Validation strategy**: do NOT try to run `test_pin_fleet.py` mid-block —
that file is created in Step F.34. Instead: at end of each substep, run a
quick manual smoke (`python scripts/ws1_pin_fleet.py --check --fleet
config/fleet/r5a_fleet.yaml` against the actual fleet YAML) to catch obvious
breakage. Full unit-test coverage runs at Block G after F.34 is written.

## Step B.18 — Replace `_git_blob_sha1` with `_sha256_file_content`

**File:** `scripts/ws1_pin_fleet.py`

Edits:

1. **Replace `_git_blob_sha1` (line 120-131)** with `_sha256_file_content`:
   ```python
   def _sha256_file_content(content: bytes) -> str:
       """SHA-256 of `tokenizer.json` byte content as resolved at load time.

       Matches HF cache `blobs/<hash>` filename for LFS-tracked tokenizers
       but NOT for git-tracked ones (HF uses git-blob SHA1 for non-LFS).
       Do NOT use this value as a cache lookup key.
       """
       return hashlib.sha256(content).hexdigest()
   ```
2. **Update call site at `_discover_from_cache` line 186**:
   `tok_sha = _git_blob_sha1(content)` → `tok_sha = _sha256_file_content(content)`.
3. **Update module docstring (line 19-23)**: replace the line
   "tokenizer SHA is computed as the git-blob SHA1 of `tokenizer.json`
   (matches HF's own blob-store filename, but works on Windows where the
   blobs/ symlinks become real files)." with the language from DECISIONS.md
   decision #4 (LFS vs non-LFS divergence is intentional; field defined as
   "content-as-loaded SHA-256", not "cache lookup key").
4. **Update `src/r5a/contracts.py:RunManifest.tokenizer_shas` docstring**
   (or add inline comment at lines 437-439) per DECISIONS.md decision #4.
5. **Update `config/fleet/r5a_fleet.yaml` header comment** with the language
   from decision #4 (point at the line documenting `tokenizer_sha` semantics
   if any; otherwise add a short header block above the `models:` section).

**Acceptance criterion**: `python -c "from scripts.ws1_pin_fleet import _sha256_file_content; print(_sha256_file_content(b'abc'))"` outputs the expected SHA-256 (`ba7816bf...`).

## Step B.19 — Reject unknown `--pin-json` model IDs

**File:** `scripts/ws1_pin_fleet.py`

Edits:

1. **In `main()` after loading overrides (line 288-290)**, validate:
   ```python
   if overrides:
       unknown = set(overrides) - set(fleet.models)
       if unknown:
           raise SystemExit(
               f"--pin-json contains model IDs not in fleet: {sorted(unknown)}; "
               "check config/fleet/r5a_fleet.yaml `models:` keys"
           )
   ```

**Acceptance criterion**: a `--pin-json` with `{"not-in-fleet": {...}}`
exits non-zero with the unknown ID in stderr.

**Reference**: Lens D B.16, R2-C5 #8.

## Step B.20 — Make `--vllm-image-digest` required + format-validated for non-`--check`

**File:** `scripts/ws1_pin_fleet.py`

Edits:

1. **Argparse line 96-101**: change `required=False` to `required=False`
   conceptually (kept for `--check`), but add a runtime check:
   ```python
   if not args.check:
       if not args.vllm_image_digest:
           raise SystemExit("--vllm-image-digest is required for non-check pinning runs")
       if not re.match(r"^sha256:[0-9a-f]{64}$", args.vllm_image_digest):
           raise SystemExit(
               f"--vllm-image-digest must match sha256:<64-hex>; got {args.vllm_image_digest!r}"
           )
   ```
2. Update `--vllm-image-digest` help text: clarify required for non-check.

**Acceptance criterion**: `python scripts/ws1_pin_fleet.py --fleet ... --check`
without digest succeeds; without `--check` and without digest fails;
`--vllm-image-digest <TBD>` fails the regex.

**Reference**: R2-U3, Lens A major #6, R2-C5 #7.

## Step B.21 — Patch quoted `<TBD>` placeholders

**File:** `scripts/ws1_pin_fleet.py`

Edits:

1. **In `_patch_model_block` line 252-253**: change the placeholder check to
   accept both unquoted and quoted forms:
   ```python
   if current == PLACEHOLDER or current == f'"{PLACEHOLDER}"' or current == new_value:
       if current == new_value:
           continue
       # ... existing replacement
   ```

**Acceptance criterion**: a fleet YAML with `tokenizer_sha: "<TBD>"` is patched
on first pinner run.

**Reference**: R2-C5 #4, Lens C silent #1.

## Step B.22 — Idempotent fleet_version bump

**File:** `scripts/ws1_pin_fleet.py`

Edits:

1. **In `main()` lines 332-344**: track whether any field actually changed
   (any element of `all_changes` other than the existing-skip messages).
   Compute `any_field_changed = bool([c for c in all_changes if "->" in c and not c.startswith("fleet_version:") and "SKIP" not in c])`.
2. Only auto-bump (apply `+pinned-<UTC>` suffix) when `any_field_changed` is
   `True` OR `args.bump_version` is explicit. Otherwise, leave fleet_version
   unchanged and emit a log line: `"fleet_version: no field changes; not bumped"`.

**Acceptance criterion**: re-running the pinner with the same `--pin-json` on
an already-pinned fleet leaves the file byte-identical (Step F.34 #4
idempotency test).

**Reference**: R2-C5 #5, Lens C silent #2.

## Step B.23 — Atomic rename for fleet YAML and pinning log

**File:** `scripts/ws1_pin_fleet.py`

**v3 simplification (cut per `.scratch/simplification_proposal.md` C.1)**: cross-platform file locking + sentinel `.lock` + retry-with-backoff + stale-lock recovery message + Codex MCP design escalation all cut. The lock defended against concurrent pinner invocations; the pinner is fired once manually after `huggingface-cli download` completes on the AutoDL instance, with no scheduler / daemon / parallel CI / second operator. Concurrency scenario doesn't exist in this threat model. Atomic rename via `tempfile + os.replace` is preserved because `out_path.write_text(...)` is non-atomic on Windows under crash — that defense IS real.

Edits:

1. **Add helpers** `_atomic_write_text(path, text)` and `_atomic_write_json(path, payload)`:
   - Write to `path.with_suffix(path.suffix + ".tmp")`.
   - `os.fsync` on the file descriptor.
   - `os.replace(tmp, path)` for atomic rename (works on both POSIX and Windows for same-directory replacement).
   - On any exception during write, attempt to delete the `.tmp` file in `finally`.
2. **Replace `out_path.write_text(...)` (line 365)** with `_atomic_write_text(out_path, yaml_text)`.
3. **Replace `log_path.write_text(...)` (line 390-393)** with `_atomic_write_json(log_path, prior)`.
4. **Transactional ordering note**: the fleet write and log append are NOT a single transaction. If the process crashes between the fleet write and log append, the fleet has new pins but the log has no entry. Document this in the function docstring: "log append is best-effort post-fleet; if you see fleet changes without a corresponding log entry, the operator must add an entry manually." Single-operator pilot is unlikely to hit this; documentation is for forensic clarity.

**Acceptance criterion**: successful run leaves no `.tmp` residue in either target dir. Steady-state single-operator path is unchanged. (No lock-related tests; F.34 #13 / #14 cut per C.1.)

**Reference**: R2-C5 #6 (atomic-rename portion only); Lens C A.7; v3 simplification C.1.

## Step B.24 — Refuse multi-snapshot HF cache without explicit `--revision`

**File:** `scripts/ws1_pin_fleet.py`

Edits:

1. **Add CLI arg** `--revision` (per-model, accepted as repeated
   `--revision MODEL_ID=COMMIT_SHA` or as a JSON map; simpler form: extend
   `--pin-json` to also accept a `"revision": "..."` key per model and use it
   as the snapshot disambiguator).
2. **In `_pick_snapshot` line 152-161**: if `len(candidates) > 1` and no
   explicit revision was passed for this model, raise `SystemExit` with a
   message naming the conflicting snapshot dirs and the model ID. If explicit
   revision was passed, look up `repo_dir/snapshots/<commit_sha>/`; raise if
   that path doesn't exist.

**Acceptance criterion**: a cache dir with two snapshots fails fast with a
clear error when no `--revision` is given; passing the right revision succeeds.

**Reference**: R2-C5 #2, Lens A major #5, Lens C A.10.

## Step B.25 — [CUT v3]

**v3 simplification (cut per `.scratch/simplification_proposal.md` Q4)**: pin-field domain is hex-only (SHA-1 `hf_commit_sha`, SHA-256 `tokenizer_sha`); no YAML special characters can occur in pin values, so the round-trip-quirk scenario is structurally impossible. Existing defenses cover residual risk: Pydantic re-validation (lines 346-362, already present) catches malformed YAML; F.34 #4 idempotency test catches any round-trip drift transitively. F.34 #10 (post-patch equality test) also cut. If a future pin field domain expands to non-hex values, add B.25 then.

## Step B.26 — Respect `HF_HUB_CACHE` env var

**File:** `scripts/ws1_pin_fleet.py`

Edits:

1. **In `_default_hf_cache` (line 134-143)**: check `HF_HUB_CACHE` env var
   first (it's the canonical user-set cache root), then `HF_HOME / "hub"`,
   then `~/.cache/huggingface/hub`:
   ```python
   def _default_hf_cache() -> Path | None:
       for env_name in ("HF_HUB_CACHE",):
           v = os.environ.get(env_name)
           if v:
               candidate = Path(v)
               if candidate.exists():
                   return candidate
       hf_home = os.environ.get("HF_HOME")
       if hf_home:
           ...
       # existing fallback
   ```

**Acceptance criterion**: with `HF_HUB_CACHE=/path/to/cache`, the discovery
returns that path before consulting `HF_HOME` or `~/.cache`.

**Reference**: Lens C A.9.

## Step B.27 — Refuse corrupt pinning log (no silent reset)

**File:** `scripts/ws1_pin_fleet.py`

Edits:

1. **In `main()` line 383-388**: when reading the existing log, replace the
   silent `prior = []` fallback with `SystemExit`:
   ```python
   if log_path.exists():
       try:
           prior = json.loads(log_path.read_text(encoding="utf-8"))
       except json.JSONDecodeError as exc:
           raise SystemExit(
               f"existing pinning log {log_path} is corrupt: {exc!r}; "
               "operator must inspect and either fix or move it aside"
           )
       if not isinstance(prior, list):
           raise SystemExit(
               f"existing pinning log {log_path} is not a JSON array; "
               "operator must inspect and either fix or move it aside"
           )
   ```

**Acceptance criterion**: a corrupt or non-list log file raises clearly
instead of silently truncating provenance history.

**Reference**: Lens C A.6, Lens C silent #3.

## Step B.28 — Tighten `_check_pinning_for_pilot` in `ws1_run_logprob.py`

**File:** `scripts/ws1_run_logprob.py`

Edits:

1. **In `_check_pinning_for_pilot` line 209-241**: extend the `bad` list to
   include `tokenizer_family` and `quant_scheme`:
   ```python
   if cfg.tokenizer_family is None or cfg.tokenizer_family == placeholders:
       bad.append("tokenizer_family")
   if cfg.quant_scheme is None or cfg.quant_scheme == placeholders:
       bad.append("quant_scheme")
   ```
2. **Update digest format check (line 235)**: replace the truthiness check with
   the regex check from Step B.20:
   ```python
   import re
   if not args.vllm_image_digest or not re.match(
       r"^sha256:[0-9a-f]{64}$", args.vllm_image_digest
   ):
       raise SystemExit(...)
   ```

**Acceptance criterion**: `--pilot` or `--exposure-horizon-probe` against a
fleet entry missing `tokenizer_family` raises with the missing field listed.

**Reference**: R2-U3, R2-U4, Lens A major #3-#4.

---

# Block E — Power calculator rename + bug fix (~1 hr)

## Step E.29 — Rename script and update docstring (+ `E_FO` → `E_OR` source-side sweep)

**File:** `scripts/simulate_phase8_power.py` → `scripts/planning_power_calculator.py`

1. **`git mv scripts/simulate_phase8_power.py scripts/planning_power_calculator.py`**
2. **Top-of-file module docstring**: rewrite per DECISIONS.md decision #3:
   - First paragraph: "This is a closed-form planner for design-time scenario sweep, NOT the §8.8 simulation. For prereg-grade power claims see the §8.8 MC simulator (deferred to post-pilot; needs pilot `hat(beta)` + `hat(Sigma)` to calibrate)."
   - Cross-reference: DECISIONS.md decision #3, plan §8.8.
3. **Module docstring `E_FO` references** (lines 7, 217 in the original file): rename `E_FO` → `E_OR` per decision #10 source-side. Specifically: `"14 P_predict-eligible models (E_CMMD / E_FO / E_NoOp)"` → `"14 P_predict-eligible models (E_CMMD / E_OR / E_NoOp)"`; `--n-case-main-total` help text `"E_CMMD / E_FO / E_NoOp"` → `"E_CMMD / E_OR / E_NoOp"`.

## Step E.30 — Fix `E_CMMD` analysis-unit bug (case-level closed-form SE)

**File:** `scripts/planning_power_calculator.py` (newly renamed)

**Per Lens 2 (scope) D-5 decision**: this step uses **closed-form case-level
SE**, NOT a literal Monte-Carlo case-cluster bootstrap. The bootstrap-named
implementation is deferred to the §8.8 post-pilot MC simulator (which has
its own future file). DECISIONS.md decision #3 allows closed-form for
design-time scenario sweep "if its output unit is correct"; this step fixes
the unit (case-level, not model+family+case).

Edits:

1. **In `_simulate_estimand_powers` E_CMMD branch (line 272-313)**: replace `_se_with_family_intercepts(...)` calls with a closed-form case-level SE:
   - `E_CMMD` is fleet-aggregated case-level (per plan §8.2 / §8.1A).
   - Approximate SE: `sigma_case_aggregate / sqrt(n_case)`, where `sigma_case_aggregate ≈ sigma_within * cmmd_inflation` (the model/family multiplier is conceptually folded into a case-level residual SD; default `1.0`, scaled by `cmmd_inflation` grid).
   - Concretely (with the explanatory docstring per D-5):
     ```python
     for cmmd_inflation in args.cmmd_inflation:
         # Case-level SE under iid-case assumption. This is the analytic
         # limit of a case-cluster bootstrap when within-case correlation
         # is absorbed by fleet-aggregation: E_CMMD averages over 14
         # P_predict models per case BEFORE the regression, so the
         # residual lives at case level. For non-iid or heavy-tailed
         # pilot residuals, the §8.8 post-pilot MC simulator runs an
         # actual case-cluster bootstrap; this planning calculator stays
         # closed-form by design (DECISIONS.md decision #3 "two-tool
         # model"; PENDING.md tracks the post-pilot MC implementation).
         sigma_case_aggregate = 1.0 * cmmd_inflation
         se_pilot = sigma_case_aggregate / math.sqrt(args.n_case_pilot + args.n_case_bl2_post)
         se_main = sigma_case_aggregate / math.sqrt(args.n_case_main_total)
         rows.append({...})
     ```
   - Update emitted row dict: drop the `n_models` and `n_families` keys (they no longer apply to E_CMMD); retain `cmmd_inflation` so the sweep remains interpretable.

2. **`E_FO_E_NoOp_beta_cutoff` label rename** (decision #10 source-side): the row label string at line 387 (and any other estimand label line referencing `E_FO`) is renamed:
   - `"estimand": "E_FO_E_NoOp_beta_cutoff"` → `"estimand": "E_OR_E_NoOp_beta_cutoff"` (line 387 of the renamed file).
   - In-code comment line 355 `"# E_FO / E_NoOp: pooled over 14 P_predict models..."` → `"# E_OR / E_NoOp: pooled over 14 P_predict models..."`.
   - This changes the output JSON's `rows[*].estimand` value for that row class. No downstream consumer reads this key yet (pre-cloud-spend), so the rename is safe.

## Step E.31 — Remove cosmetic MC SE fields

**File:** `scripts/planning_power_calculator.py`

Edits:

1. **Delete the entire post-loop block at line 404-415** (the `for r in rows:`
   block that adds `power_*_mc_se` and `power_*_ci95_*` keys).
2. **Delete the `_ = rng.standard_normal(1)` filler (line 415)**.
3. **Delete the unused `np.random.default_rng(args.seed)` (line 266)** and the
   `--seed` arg if not used elsewhere; or keep `--seed` as informational and
   simply delete the `rng = ...` assignment.

**Acceptance criterion**: output JSON rows no longer contain `*_mc_se` or
`*_ci95_*` keys.

## Step E.32 — Decide `--b-outer` fate

**File:** `scripts/planning_power_calculator.py`

1. **Argparse line 193-199**: keep `--b-outer` for now but update help text:
   `"informational only; closed-form planner does not run a Monte Carlo loop"`.
   Decision #3 says removing it is acceptable; keeping it with corrected help
   is the lower-risk option in Tier-R2-0 (minimizes breakage of any caller).
2. **In the output `config` dict (line 425-440)**: remove `b_outer` to avoid
   suggesting MC was run.

## Step E.33 — Add planning-power PENDING marker (decision #3)

**File:** `PENDING.md`

Edits (small Tier-R2-0 doc-side touch; the larger doc sweep is Tier-R2-1):

1. Add a one-line entry under Active items: "Phase 8 MC simulation — needed
   before PREREG_STAGE1; must be calibrated from pilot `hat(beta)` and
   `hat(Sigma)`. See plans/phase7-pilot-implementation.md §8.8 (Tier-R2-1
   adds the two-tool model paragraph)." Plan §8.8 paragraph itself is
   Tier-R2-1.

**Acceptance criterion**: `python scripts/planning_power_calculator.py --output /tmp/planning.json` runs to completion; `python scripts/simulate_phase8_power.py --help` fails with `No such file`.

---

# Block F — Tests (~1.5-2 hr; v3 reduced from v2 3-4 hr after test density 50-56 → ~25-30)

Per Lens D §B.16-B.20 + suggested outlines, originally expanded by Lens 4 (test
adequacy) findings to close 22 hardening surfaces. **v3 simplification then
cut roughly half the Lens-4-driven additions** per `.scratch/simplification_proposal.md`
C.2 + Q1-Q7: F.34 14 → 9 (cut lock + HF_HUB_CACHE + post-patch + merged digest);
F.35 23 → 10 (8-clause per-clause tests collapsed to 1 multi-clause integration
+ 1 happy-path; redundant edge cases dropped); F.36 unchanged (5); F.37 unchanged
(2); F.38 simplified mutational sentinel to 5-line source-inspection (1);
F.39 6 → 1 (kept only the detector numerical anchor; empty-pcsg-pairs cut).
Total new tests: ~50-56 → ~28 (28 in Block F: 9+10+5+2+1+1=28; plus 5 in
Block A: 2 contract + 3 fleet validator = 33 net new tests at the file level,
or ~28 if we count per-test-function additions to existing files).

**General test-style guidance** (per Lens 4 + Lens 5 findings):
- **Prefer import-based tests over `subprocess.run`**. `subprocess.run` is reserved for genuine end-to-end smoke; for unit assertions on internal helpers, import them directly (e.g., `from scripts.ws1_pin_fleet import _patch_model_block, main`) or run `main()` after `monkeypatch.setattr(sys, "argv", [...])`. Subprocess tests are flaky on Windows due to cwd / quoting / path separators.
- **All file I/O in tests uses `tmp_path` fixture**, never `/tmp`, never the real `config/fleet/r5a_fleet.yaml`, never `data/pilot/.fleet_pinning_log.json`. Real-path mutations during tests pollute the working tree.
- **Each new test should fail meaningfully** if the corresponding hardening regresses (Lens 4 "Conceptually Weak Tests" — every test must have a tight assertion, not a permissive one).

## Step F.34 — Write `tests/r5a/test_pin_fleet.py` (NEW)

**File (new):** `tests/r5a/test_pin_fleet.py`

**Fixtures required** (write a small `conftest.py`-style helper at top of file):
- `MINIMAL_FLEET_YAML` constant: a 2-model fleet (one white-box with `<TBD>` placeholders, one black-box) plus one PCSG temporal pair, ~30 lines.
- `_run_pin_fleet_cli(tmp_path, *args, **env)`: helper that calls `main()` after `monkeypatch.setattr(sys, "argv", ["ws1_pin_fleet.py", ...args])`. Returns `(returncode, stdout, stderr)`. Use `capsys` for stdout/stderr capture, `pytest.raises(SystemExit)` for non-zero exit.
- `MOCK_HF_CACHE` factory: builds a `tmp_path/hf_cache/models--<owner>--<repo>/snapshots/<sha>/tokenizer.json` layout for tests that exercise discovery.

Tests (v3 simplified per `.scratch/simplification_proposal.md` C.2 + Q1 + Q4; 14 → 9):

1. `test_patch_model_block_pins_only_target_model` — Lens D verbatim. Uses `_patch_model_block` import directly (NOT subprocess).
2. `test_pin_json_unknown_model_is_rejected` — uses `_run_pin_fleet_cli` (import-based); covers Step B.19. Pin-json with `{"not-in-fleet": {"hf_commit_sha": "x"}}` → `SystemExit` containing `"not-in-fleet"`.
3. `test_pin_fleet_check_mode_does_not_write` — `--check` against a TBD fleet leaves the file byte-identical.
4. `test_pin_fleet_validates_hash_invariant_and_idempotency` — Step B.22; second pin run with same input is byte-identical to first run output. (Transitively guards round-trip drift, replaces cut B.25 #10.)
5. `test_pin_fleet_quoted_tbd_is_patched` — Step B.21; `tokenizer_sha: "<TBD>"` (quoted) is replaced on first run.
6. `test_pin_fleet_sha256_file_content` — Step B.18; `_sha256_file_content(b"abc")` equals the known SHA-256 (`ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`).
7. `test_pin_fleet_image_digest_validation` — Step B.20; parameterized over (a) non-`--check` without `--vllm-image-digest` → SystemExit, (b) `--vllm-image-digest <TBD>` → SystemExit (regex), (c) `--vllm-image-digest sha256:short` → SystemExit (regex requires 64 hex). (Merged from v2 #7 + #8.)
8. `test_pin_fleet_multi_snapshot_rejected_without_revision` — Step B.24; HF cache fixture with two snapshot subdirs and no `--revision`, raises `SystemExit` mentioning the model ID. (Per Q1: AutoDL bring-up may produce multiple snapshots after retries; without B.24 the pinner silently picks newest, a real silent-wrong-result hazard.)
9. `test_pin_fleet_corrupt_log_rejected` — Step B.27; pre-create `data/pilot/.fleet_pinning_log.json` with invalid JSON or with a non-list root, raises `SystemExit` instead of silently truncating.

**v3 cuts**:
- v2 #10 `test_pin_fleet_post_patch_equality_assert` — cut per Q4 (B.25 cut; hex-only pin domain).
- v2 #11 `test_pin_fleet_hf_hub_cache_env_var_precedence` — cut per C.2 (B.26 is a 1-line code change; near-zero regression risk).
- v2 #13 `test_pin_fleet_lock_pre_existing_blocks_run` — cut per C.1 (lock mechanism cut).
- v2 #14 `test_pin_fleet_atomic_write_replaces_target_no_tmp_residue` — cut per C.1 (tests stdlib `os.replace`; trivial value).

**Acceptance criterion**: `pytest tests/r5a/test_pin_fleet.py -q` green; 9 tests pass.

## Step F.35 — Write `tests/r5a/test_finalize_run_manifest.py` (NEW)

**File (new):** `tests/r5a/test_finalize_run_manifest.py`

**Fixtures required**:
- `MINIMAL_RUN_FIXTURE(tmp_path)`: builds a tmp_path-scoped directory containing a small fleet YAML, runtime YAML, article manifest JSON, exposure_horizon JSON, traces dir with `.parquet` files matching the fleet's p_logprob members, hidden-states dir with flat `{case_id}__{model_id}.safetensors` layout, sampling config YAML, launch_env JSON. Return paths.
- `_run_finalize_cli(tmp_path, mode, **overrides)`: helper that calls `main()` via `monkeypatch.setattr(sys, "argv", [...])` against the fixture; allows overriding individual paths or omitting fields.

Tests (v3 simplified per `.scratch/simplification_proposal.md` C.2 + C.3 + C.4 + Q2; 23 → 10):

**8-clause hard-fail framework (collapse: 9 per-clause tests → 2 multi-clause tests)**:

The collapse tests directly verify the Decision #1 contract that the framework must "raise `SystemExit` with a multi-line error message listing every failed clause" (i.e., collect-and-report, not fail-fast). Per-clause tests in v2 verified each clause individually but did NOT verify the multi-line collection behavior.

1. `test_finalize_confirmatory_lists_all_clause_violations` — build a fixture that simultaneously violates all 8 clauses (zero git SHA via monkeypatch, missing `--vllm-image-digest`, `<TBD>` tokenizer_sha on one P_logprob model, `<TBD>` api_model_name on one black-box, exposure_horizon JSON with one missing model + one extra model, traces dir missing one model's parquet, launch_env JSON missing `CUDA_VISIBLE_DEVICES`, missing `--gpu-dtype`). Run finalizer in confirmatory mode. Assert `SystemExit` raised AND error message contains the literal prefix substrings `"[clause 1]"` through `"[clause 8]"` (one per failed clause). The `[clause N]` format is enforced by `_confirmatory_hard_fail` in Step C.12 — using clause numbers (rather than substring keywords like `"git"` or `"trace"`) prevents coincidental substring matches in unrelated parts of the error message and keeps the assertion list trivially correct as clauses are added/removed.
2. `test_finalize_confirmatory_happy_path_all_clauses_satisfied` — build a fixture that satisfies all 8 clauses; run finalizer in confirmatory mode; assert manifest file is written, `mode == "confirmatory"`, all required fields populated; reload JSON and validate via `RunManifest.model_validate`.

**Mode behavior**:

3. `test_finalize_dev_mode_skips_hard_fail` — `--allow-tbd` against the same fixture as #1 (8 simultaneous violations) → succeeds with `mode="dev"`. Manifest written with placeholders preserved.

**Helper-level unit tests (per Q2 keep — covers paths integration test doesn't reach)**:

4. `test_validate_traces_dir_dev_tolerates_partial` — Step C.10; dev mode with missing parquet returns the partial mapping without raising. (Integration test only exercises confirmatory; this guards dev-mode helper behavior.)
5. `test_validate_traces_dir_confirmatory_lists_missing_and_extras` — Step C.10; confirmatory mode raises listing BOTH missing and unexpected files. (Integration asserts clause 6 fires; this asserts the "missing AND extras" granularity in the message.)
6. `test_read_exposure_horizon_invalid_date_raises_in_confirmatory` — Step C.11; horizon JSON with `"horizon_observed": "not-a-date"` raises `SystemExit` mentioning the `model_id`. (Integration triggers clause 5 via key mismatch only; this covers the invalid-date sub-path.)

**Hidden-state hash fixture**:

7. `test_finalize_hidden_state_subset_hash_fixture_two_models` — Step C.13; build flat-layout fixture with 2 models × 30 cases; assert canonical-JSON hash; assert `expected_models=["m1", "m2"]` parameter is honored (not `fleet.p_logprob_eligible_ids()`).

**Threshold dict + roster + sampling-config**:

8. `test_finalize_quality_gate_thresholds_actual_fleet` — assert all 6 expected keys present AND have expected values (eligible 14, 12; thresholds via `_one_third_minimum(14)`, `_strict_majority(14)`, `_strict_majority(14)`); assert `ws6_mechanistic_*` NOT present; assert keys starting with `e_or_` (NOT `e_fo_`) present; assert no `*_realized_n_p_predict` keys (per C.4).
9. `test_finalize_roster_fields_match_fleet` — Step C.17; finalized manifest's `fleet_p_predict_eligible` and `fleet_p_logprob_eligible` exactly equal `fleet.p_predict_eligible_ids()` and `fleet.p_logprob_eligible_ids()`.
10. `test_finalize_sampling_config_hash_separate_from_article` — Step C.15; manifest's `sampling_config_hash != article_manifest_hash`.

**v3 cuts**:
- v2 #1-#9 per-clause hard-fail tests → collapsed into v3 #1+#2 per C.2 (multi-line collection contract from Decision #1 is now directly tested; v2's per-clause tests didn't verify collection).
- v2 #11 `test_finalize_rejects_tbd_without_allow_tbd` — redundant with v3 #1 (covered by clause-3 substring).
- v2 #16 `test_finalize_hidden_state_subset_hash_rejects_partial_in_confirmatory` — covered by v3 #1's all-clauses fixture transitively.
- v2 #17 `test_finalize_canonical_json_hash_distinct_for_newline` — cut per C.3 (case_id has no newlines).
- v2 #19 `test_finalize_quality_gate_thresholds_realized_keys_present` — cut per C.4 (realized-N keys removed).
- v2 #22 `test_finalize_manifest_file_roundtrip_confirmatory` — covered by v3 #2 (happy-path roundtrip is part of the integration test).
- v2 #23 `test_finalize_manifest_file_roundtrip_dev` — redundant with v3 #3.

**Acceptance criterion**: `pytest tests/r5a/test_finalize_run_manifest.py -q` green; 10 tests pass; the test file's import surface is `from scripts.ws1_finalize_run_manifest import ...` (NOT subprocess for the unit tests).

## Step F.36 — Write `tests/r5a/test_planning_power_calculator.py` (NEW)

**File (new):** `tests/r5a/test_planning_power_calculator.py`

**Note**: ALL paths use `tmp_path`; `/tmp/planning.json` is forbidden (Lens 4 + Lens 5 portability finding).

Tests (per Lens D B.18 + suggested outlines + Lens 4 expansions):

1. `test_pcsg_se_anchor` — Lens D outline:
   ```python
   from scripts.planning_power_calculator import _se_pcsg_pair
   assert _se_pcsg_pair(2048, 2, 0.98, 4.5) == pytest.approx(0.0710, abs=5e-4)
   ```
2. `test_cmmd_se_case_level_after_fix` — Step E.30 (Lens 4 weak-test fix; renamed from `_after_fix` per Lens 4 naming nit). Direct numerical check:
   ```python
   from scripts.planning_power_calculator import _simulate_estimand_powers
   import argparse
   args = argparse.Namespace(
       n_case_pilot=80, n_case_bl2_post=350, n_case_main_total=2560,
       cmmd_inflation=[1.0], effects=[0.20], scenarios=["unweighted_pilot"],
       family_states=["S20"], pcsg_eligibility=[0.98], n_case_main_pre=2048,
   )
   rows = _simulate_estimand_powers(args)
   cmmd_rows = [r for r in rows if r["estimand"] == "E_CMMD_beta_cutoff"]
   # SE_pilot uses n=430 (80+350); SE_main uses n=2560.
   # SE = sigma_case_aggregate / sqrt(n) with sigma=1.0
   se_pilot_expected = 1.0 / (430 ** 0.5)
   se_main_expected = 1.0 / (2560 ** 0.5)
   assert cmmd_rows[0]["se_pilot"] == pytest.approx(se_pilot_expected, abs=1e-4)
   assert cmmd_rows[0]["se_main"] == pytest.approx(se_main_expected, abs=1e-4)
   # Ratio of SEs scales as sqrt(n_pilot / n_main):
   assert cmmd_rows[0]["se_pilot"] / cmmd_rows[0]["se_main"] == pytest.approx((2560/430)**0.5, abs=0.01)
   ```
3. `test_wy_power_anchor_points` — Lens D outline verbatim:
   ```python
   from scripts.planning_power_calculator import _wy_power
   assert _wy_power(0.0, 1.0, z_wy=2.8) == pytest.approx(0.005110, abs=1e-6)
   assert _wy_power(0.2, 0.071, z_wy=2.8) == pytest.approx(0.5067, abs=1e-3)
   assert _wy_power(0.3, 0.071, z_wy=2.8) == pytest.approx(0.9230, abs=1e-3)
   ```
4. `test_no_mc_se_in_output_rows` — Step E.31; uses `tmp_path` (NOT `/tmp`) for output:
   ```python
   import json, sys
   def test_no_mc_se_in_output_rows(tmp_path, monkeypatch):
       output = tmp_path / "planning.json"
       monkeypatch.setattr(sys, "argv", ["planning_power_calculator.py", "--output", str(output)])
       from scripts.planning_power_calculator import main
       main()
       data = json.loads(output.read_text())
       for row in data["rows"]:
           assert "power_pilot_mc_se" not in row
           assert "power_main_mc_se" not in row
           assert "power_pilot_ci95_low" not in row
   ```
5. `test_estimand_label_renamed_to_e_or` — decision #10 source-side; Step E.30 sub-step 2:
   ```python
   rows = _simulate_estimand_powers(args)
   labels = {r["estimand"] for r in rows}
   assert "E_OR_E_NoOp_beta_cutoff" in labels
   assert "E_FO_E_NoOp_beta_cutoff" not in labels
   ```

**Acceptance criterion**: `pytest tests/r5a/test_planning_power_calculator.py -q` green; 5 tests pass; no `/tmp` references in the test file.

## Step F.37 — Extend `tests/r5a/test_logprob_metrics.py` with LogProbTrace validators

**File:** `tests/r5a/test_logprob_metrics.py` (existing — extend)

Add two tests per Lens D outlines (B.20):

1. `test_logprob_trace_rejects_prefix_longer_than_article` — verbatim outline.
2. `test_logprob_trace_rejects_top_alt_outer_length_mismatch` — verbatim
   outline.

If the existing test file does not have a `valid_trace_kwargs(...)` helper,
add a small helper that returns a baseline kwargs dict consistent with
`LogProbTrace`'s required fields.

**Acceptance criterion**: both added tests pass; no existing test in this
file regresses.

## Step F.38 — Add PCSG hash payload coverage test in `test_fleet_config.py`

**File:** `tests/r5a/test_fleet_config.py` (existing — extend)

**v3 simplification (per `.scratch/simplification_proposal.md` C.2 F.38)**: replace v2's mutational sentinel loop with a direct source-inspection check. The drift we want to catch is: "if `PCSGPair` gains a new field, `pcsg_pair_registry_hash()` must be updated to include it in the canonical payload." Source inspection catches this directly without per-field type handling.

```python
def test_pcsg_pair_registry_hash_payload_field_coverage():
    """If PCSGPair declares a new field, pcsg_pair_registry_hash() must
    update the canonical-payload dict in src/r5a/fleet.py to include it.
    """
    import inspect
    from src.r5a.fleet import FleetConfig, PCSGPair
    src = inspect.getsource(FleetConfig.pcsg_pair_registry_hash)
    for field in PCSGPair.model_fields:
        assert f'"{field}"' in src, (
            f"PCSGPair.{field!r} declared but not in canonical hash "
            f"payload — update FleetConfig.pcsg_pair_registry_hash()."
        )
```

**Acceptance criterion**: `pytest tests/r5a/test_fleet_config.py::test_pcsg_pair_registry_hash_payload_field_coverage -q` green. Adding a new field to `PCSGPair` without updating `pcsg_pair_registry_hash()` makes this test red with the field name in the failure message.

## Step F.39 — Add detector numerical anchor in `test_exposure_horizon.py`

**File:** `tests/r5a/test_exposure_horizon.py` (renamed from `test_cutoff_probe.py` in Step D.6)

**v3 simplification (per `.scratch/simplification_proposal.md` C.2 F.39 + Q7; 6 → 1)**: the 7 renamed existing tests in test_exposure_horizon.py already cover the detector's happy path, edge inputs, and rejection logic. The Lens D outlines are "if you want extra rigor, here are some" — not Tier-R2-0 hardening of new code. Keep one numerical anchor; drop the rest.

Test to add (after the renamed existing tests):

1. `test_detect_exposure_horizon_clean_step_exact_ci_bounds` — Lens D outline; asserts EXACT CI bound dates and approximate `drop_ci_lower` for a clean-step fixture. Replaces the loose acceptance assertion in the renamed file. This is the numerical anchor for the piecewise-WLS detector after the rename.

**v3 cuts (Lens D outlines deferred / dropped)**:
- v2 #2 `test_detect_exposure_horizon_min_side_exact_boundary_rejected` — boundary case the detector handles fine; no in-flight regression risk.
- v2 #3 `test_detect_exposure_horizon_bootstrap_invalid_guard` — defers paper-time rigor for a not-yet-cloud-spent detector.
- v2 #4 `test_detect_exposure_horizon_aggregator_mean_vs_median` — covered by the renamed existing tests' aggregator usage.
- v2 #5 `test_detect_exposure_horizon_high_noise_rejection_pinned` — the renamed `test_detect_high_noise_rejects` (existing) covers the rejection path; pinning exact `drop_ci_lower` is paper-time work.
- v2 #6 `test_pcsg_pairs_empty_lists_and_hash` (in test_fleet_config.py) — cut per Q7 (production path never hits empty pcsg_pairs; helper behavior on empty input is stdlib-stable).

**Acceptance criterion**: `pytest tests/r5a/test_exposure_horizon.py -q` green; 1 new test passes alongside the 7 renamed existing tests.

**Reference**: Lens D `Suggested test additions`; v3 simplification C.2 F.39 + Q7.

---

# Block G — Validation (~30 min)

**Shell**: Git Bash (the `grep` invocations below are bash). PowerShell
equivalents shown inline where the operator might prefer them.

## Step G.40 — Run the full r5a test suite

```bash
pytest tests/r5a -q
```

**Acceptance criterion**: every test passes (black-on-green tally). If any fail, regress to the relevant block and fix before continuing. Do NOT commit yet.

## Step G.41 — Run the smoke configuration check

```bash
python scripts/smoke_phase7.py --check-config
```

**Acceptance criterion**: output reports `white_box (12)`, `black_box (4)`, `p_predict_eligible (14)`, `p_logprob_eligible (12)`, `pcsg.temporal_pairs (2): temporal_qwen_cross_version, temporal_llama_cross_version`, with NO warnings on stderr. If a warning fires, the fleet YAML drift was not addressed; investigate before committing.

(Note: `smoke_phase7.py` returning success while emitting warnings is R2-U5 / Lens A minor #4 — known cleanup item, NOT in Tier-R2-0 scope. The validation expectation is that no warning fires given a healthy fleet.)

## Step G.42 — Confirm renamed CLI surface

Git Bash:

```bash
python scripts/ws1_run_logprob.py --help | grep -E "exposure-horizon|cutoff-probe"
python scripts/ws1_finalize_run_manifest.py --help | grep -E "exposure-horizon|cutoff-observed"
python scripts/run_exposure_horizon_analysis.py --help
python scripts/planning_power_calculator.py --help
```

PowerShell equivalent (operator's choice):

```powershell
python scripts/ws1_run_logprob.py --help | Select-String -Pattern 'exposure-horizon|cutoff-probe'
python scripts/ws1_finalize_run_manifest.py --help | Select-String -Pattern 'exposure-horizon|cutoff-observed'
python scripts/run_exposure_horizon_analysis.py --help
python scripts/planning_power_calculator.py --help
```

**Acceptance criterion**: first command shows `--exposure-horizon-probe`, `--exposure-horizon-fixture`, `--exposure-horizon-output-dir`; does NOT show `--cutoff-probe`. Second command shows `--exposure-horizon`; does NOT show `--cutoff-observed`. Third + fourth commands print help text (no `No such file` error).

## Step G.43 — End-to-end sanity smoke (recommended, ~5 min)

Per Lens 1 (sequencing) "G validation under-coverage": the three commands above don't smoke-touch B.24 / B.26 / B.27 / D.7 hardening surfaces. Quick sanity:

```bash
# B.20: pin_fleet without --check requires digest
python scripts/ws1_pin_fleet.py --fleet config/fleet/r5a_fleet.yaml 2>&1 | grep -i "vllm-image-digest"
# Expect: error message referencing --vllm-image-digest required

# B.20: pin_fleet --check without digest succeeds
python scripts/ws1_pin_fleet.py --fleet config/fleet/r5a_fleet.yaml --check
# Expect: prints changes (probably empty if already pinned), exit 0

# D.7: analysis script shows renamed defaults
python scripts/run_exposure_horizon_analysis.py --help | grep -E "exposure_horizon|horizon_observed"
# Expect: at least 2 matches showing the renamed default paths
```

**Acceptance criterion**: each command above exits as expected. No need to fully execute the production pipeline; this is a quick "smoke for the renamed and hardened CLI surfaces".

---

# Step 44 — Stage and commit

After Block G is fully green, stage the consolidated changes and commit
exactly once.

**Step 44a — Save the commit message to a file** (avoids Bash HEREDOC
portability issues; works equally well in Git Bash and PowerShell):

Write the following content to `.scratch/commit_msg_tier_r2_0.txt`:

```
R2 Tier-0 patch: cloud-spend gate closure + bundled renames

Sources: refine-logs/reviews/R5A_DESIGN_REVIEW_R2_20260429/
  - SYNTHESIS.md (R2-C1..R2-C6 cross-lens + R2-U1..R2-U18 single-lens)
  - DECISIONS.md (12 user-confirmed resolutions + Tier-R2-0/R2-1 breakdown)
  - .scratch/codex_prompts_plan_review/SYNTHESIS.md (post-plan review)

Decisions implemented (full rationale in DECISIONS.md;
v3 simplification cuts in .scratch/simplification_proposal.md):
  #1 mode field + 8-clause confirmatory hard-fail (added gpu_dtype
     per Lens A major #8)
  #2 fleet_p_predict_eligible / fleet_p_logprob_eligible roster fields
  #3 simulate_phase8_power.py -> planning_power_calculator.py;
     E_CMMD case-level closed-form SE fix (case-cluster bootstrap
     deferred to post-pilot MC simulator per "two-tool model");
     cosmetic MC SE removed
  #4 tokenizer_sha = SHA-256 of file content (replaces git-blob SHA1)
  #5 cutoff_observed -> exposure_horizon_observed (full code rename;
     doc sweep is Tier-R2-1)
  #10 enum rename PerturbationVariant.C_FO -> C_CO; source-side
      E_FO -> E_OR sweep across modified files (manifest threshold
      dict keys + power calc estimand label + comments / docstrings);
      doc / WS3 spec body sweep is Tier-R2-1
  #11 drop ws6 fields from quality_gate_thresholds; two memo cleanup
      edits (DECISION_20260429_llama_addition.md §2.6 +
      DECISION_20260427_pcsg_redefinition.md §2.5) pushed to Tier-R2-1
      Block G doc sweep per simplification C.5

v3 simplification cuts (versus v2):
  - B.23 file locking + sentinel .lock + Codex MCP escalation cut
    (single-operator manual pinner, no concurrency)
  - B.25 post-patch equality assertion cut (pin domain is hex-only)
  - C.16 canonical-JSON _hash_strings cut (case_id has no newlines)
  - C.14 realized-N keys cut (clause #6 enforces realized==eligible)
  - C.18 two memo edits pushed to Tier-R2-1 doc sweep
  - F-block test density 50-56 -> ~25-30 (per-clause hard-fail
    collapsed to multi-clause integration; redundant edge-case
    tests dropped)

Files (renames via git mv preserve history):
  src/r5a/contracts.py, src/r5a/fleet.py, src/r5a/estimands/__init__.py,
  src/r5a/analysis/{cutoff_probe.py -> exposure_horizon.py},
  scripts/{ws1_pin_fleet, ws1_finalize_run_manifest, ws1_run_logprob,
    build_cutoff_probe_set,
    run_cutoff_probe_analysis -> run_exposure_horizon_analysis,
    simulate_phase8_power -> planning_power_calculator}.py,
  tests/r5a/{test_cutoff_probe.py -> test_exposure_horizon.py,
    test_run_manifest_contract.py, test_fleet_config.py,
    test_logprob_metrics.py,
    test_pin_fleet.py [new],
    test_finalize_run_manifest.py [new],
    test_planning_power_calculator.py [new]},
  config/fleet/r5a_fleet.yaml, .gitignore, PENDING.md

(v3: docs/DECISION_20260427_pcsg_redefinition.md and
docs/DECISION_20260429_llama_addition.md no longer touched in
Tier-R2-0; their edits are bundled into the larger Tier-R2-1 doc
sweep instead.)

After this commit lands, cloud-spend gate is closed on the
implementation side; only HF Meta license click-through and CLS
post-2026-02 corpus extraction remain (user-side, tracked in
PENDING.md).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

**Step 44b — Stage and commit** (works in both Git Bash and PowerShell):

```
git add -A     # acceptable here: only Tier-R2-0 changes + .scratch/ exclusion
git status     # review the file list against the Tier-R2-0 scope before committing
git commit -F .scratch/commit_msg_tier_r2_0.txt
git status     # working tree clean except .scratch/
```

**Acceptance criterion**: `git log -1 --format=%H` returns a new commit SHA on top of `8350d9e`; `git log -1 --format=%B` shows the full message; pre-commit hooks (currently none configured at HEAD) did not fire and reject. The `.scratch/commit_msg_tier_r2_0.txt` file remains in `.scratch/` (untracked) for forensic reference.

**If the commit fails** (e.g., a future pre-commit hook rejects): per project CLAUDE.md, do NOT amend. Fix the issue, re-stage, create a NEW commit with the same message.

---

# Step 45 — Push to origin

After the commit lands locally and `git status` is clean:

```bash
git push origin main
```

**Acceptance criterion**: push succeeds; remote SHA matches local; no force
push needed (Tier-R2-0 is a fast-forward from `8350d9e`).

---

# Risks to watch

| # | Risk | Why | Mitigation |
|---|---|---|---|
| 1 | **Finalizer over-restriction** breaks dev/smoke runs | Block C adds an 8-clause hard-fail; if any fires inappropriately for `--allow-tbd` mode, smoke finalization breaks | Each clause MUST be guarded by `mode == "confirmatory"`. F.35 has the multi-clause integration test (Step F.35 #1) + happy-path (#2) + dev-mode-skip (#3). Run `pytest tests/r5a/test_finalize_run_manifest.py -q` at end of Block C + Block F. |
| 2 | [CUT v3] | — | — Lock mechanism cut per simplification C.1; only atomic rename via `tempfile + os.replace` retained, which is stdlib-level and doesn't need its own risk entry. |
| 3 | **Path E rename has cross-cutting surface** in 8 Python files + 3 config/data dirs + `.gitignore` | A missed reference leaves the script suite inconsistent; missing `.gitignore` rename risks staging large generated artifacts | After each step in Block D, run `grep -rn "cutoff_observed\|cutoff_probe" src/ scripts/ tests/ config/ .gitignore`. The `cutoff_date` and `cutoff_source` fleet YAML fields are intentionally NOT renamed (decision #5). Step D.10 covers `.gitignore` per Lens 1 finding. |
| 4 | **Enum string-value rename** (`"c_fo"` → `"c_co"`, output dict key `e_fo_*` → `e_or_*`, JSON row label `"E_FO_E_NoOp_*"` → `"E_OR_E_NoOp_*"`) | Pickled / persisted artifacts holding the old literal would fail Pydantic validation or downstream key lookup | Tier-R2-0 is pre-cloud-spend (no committed fixtures use these values). Confirm before commit: `grep -rn '"c_fo"\|e_fo_e_noop\|E_FO_E_NoOp' . --exclude-dir=.scratch --exclude-dir=refine-logs --exclude-dir=archive --exclude-dir=docs --exclude-dir=plans` returns zero hits in modified files. Hits in `refine-logs/`, `archive/`, `docs/`, `plans/` are Tier-R2-1 doc sweep territory. (v3 note: full scope retained per C.6 withdrawal — bundling now is cheaper than push to R2-1 because files are open in Block C/E anyway.) |
| 5 | **`pcsg_pair_registry_hash` tightened from `str \| None` to `str`** | Existing dev manifests with `pcsg_pair_registry_hash=None` will fail to load | Contract test pin (Step A.3) catches this. No checked-in run manifest exists; the only risk is in-flight artifacts on the operator's disk that must be re-finalized after Tier-R2-0. |
| 6 | **Default trace dir mismatch between runner (D.8) and analyzer (D.7)** would silently re-open R2-C1 | If an operator updates D.7 to the new dir but skips D.8 (or vice versa), `--exposure-horizon-probe` writes to one place and the analyzer reads the other → "no traces matched" | Block G smoke step (G.42 + G.43) checks both `--help` outputs include the renamed paths; Block D acceptance criteria explicitly enforce path-string equality. |
| 7 | **PowerShell vs Git Bash invocation mismatch** (Lens 5 finding) | Step 0 / G / 44 originally used Bash idioms (`grep`, HEREDOC) that fail in PowerShell. Plan now uses Git Bash by default with PowerShell equivalents inline. | Operator must use Git Bash for all sub-steps unless told otherwise. Step 44 uses `git commit -F file` to avoid HEREDOC entirely (Lens 5 finding P11). |
| 8 | **Test coverage during transition**: A.1 → A.3, A.1 → C.12, D.5 → D.6 are RED windows where pytest fails mid-batch (Lens 1 finding) | Looks alarming if the operator runs pytest at the wrong moment | Plan now flags each transition as an "atomic pair" with explicit "do NOT run pytest between these substeps" notes. The transitions resolve at the matching pair-end; full Block A green is required before proceeding to Block D, etc. |
| 9 | **Subprocess-based tests on Windows** (Lens 4 + Lens 5 finding) | `subprocess.run([sys.executable, ...])` tests can be flaky due to cwd / quoting / path separators / `/tmp` portability in some environments | Plan uses `tmp_path` fixture for all test I/O and prefers import-based tests (`monkeypatch.setattr(sys, "argv", ...)` + `main()`) over subprocess. Subprocess reserved for genuine end-to-end smoke. (v3 note: this operator's Git Bash environment has not exhibited the flakiness in practice; mandate kept anyway because import-based tests are also faster + diagnostically better.) |
| 10 | [CUT v3] | — | — Lock mechanism cut per C.1; stale `.lock` scenario doesn't exist when there is no `.lock`. |
| 11 | [CUT v3] | — | — Codex MCP escalation for B.23 cut per C.1; lock design no longer needed. |
| 12 | [CUT v3] | — | — C.18 cut per simplification C.5; memo edits pushed to Tier-R2-1, no scope-creep risk in Tier-R2-0 commit. |

---

# Rollback plan

Tier-R2-0 is one consolidated commit on top of `8350d9e`. Three rollback
tiers, depending on where the operator stopped (per Lens 5 P12 finding —
the original blanket `git checkout -- .` was unsafe after `git mv`):

## Tier 1 — Soft rollback (no `git mv` yet, only file edits)

If only `Edit`-style file modifications have been made (no renames staged
via `git mv`), and only specific files need reverting:

```bash
# Revert specific files to HEAD (pre-batch state)
git checkout -- src/r5a/contracts.py src/r5a/fleet.py
git checkout -- tests/r5a/test_run_manifest_contract.py
# etc., per the failing block's file list
```

Safe at any point in Block A or Block B (no renames), or after any single
`Edit` substep elsewhere.

## Tier 2 — Mid rollback (renames staged, but no commit yet)

Once `git mv` has run (Block D Step D.5, D.6, D.7 OR Block E Step E.29),
plain `git checkout -- .` does NOT undo the staged rename. Use:

```bash
# Undo all staged changes (including renames) AND working-tree edits, restore from HEAD
git restore --source=HEAD --staged --worktree -- src/ scripts/ tests/ config/ .gitignore PENDING.md docs/
# Then delete any newly created untracked test files Block F may have produced
git clean -fd -- tests/r5a/test_pin_fleet.py tests/r5a/test_finalize_run_manifest.py tests/r5a/test_planning_power_calculator.py
git status     # should now show only .scratch/ as untracked
```

`.scratch/` is preserved by both `git restore` and `git clean -- <paths>`
(the explicit path arguments scope the clean to non-scratch dirs).

## Tier 3 — Hard rollback (post-commit)

If validation Block G fails AFTER the commit (operator error — Step 44 should
not run unless G is fully green) OR a regression is found post-push:

```bash
git reset --hard 8350d9e        # working tree exactly at pre-Tier-R2-0
git status                       # confirm only .scratch/ is untracked
```

`git reset --hard` correctly undoes `git mv` (renames are tracked as
delete+add at the index level) and removes newly created tracked files.
Untracked files in `.scratch/` are preserved.

If the commit was already pushed:
1. Per project CLAUDE.md "always create NEW commits rather than amending":
   open a follow-up commit with the fix; do NOT force-push the
   Tier-R2-0 commit.
2. The follow-up commit is a Tier-R2-0 hotfix, NOT a Tier-R2-1 doc
   sweep — they are tracked separately by design.

## Selective per-block rollback

If F.34 passes but F.35 fails, the operator can selectively revert only
F.35's new file:

```bash
git restore --source=HEAD --staged --worktree -- tests/r5a/test_finalize_run_manifest.py
# OR if the file was only ever untracked (Block F is creating new files):
git clean -fd -- tests/r5a/test_finalize_run_manifest.py
```

Then restart F.35 alone. Tier 1 / Tier 2 boundaries also apply at this
level — once the file has been added (untracked → existing in working tree),
treat it as Tier 2 territory.

---

# Out of scope (Tier-R2-1, follow-on)

For reference; do NOT implement in this batch:

- **Doc body sweeps** (Lens 2 confirms these are correctly Tier-R2-1; v3 adds C.18 + output-key items per simplification):
  - `PENDING.md` body — reorganize Recently-closed / Active / Tier-1 entries (Step E.33 adds ONE line; the rest is Tier-R2-1).
  - `plans/phase7-pilot-implementation.md` residue — `pilot_100_cases` references, "9-model" / "5 white-box" residue, S16a/S16b/S12 retired-state residue, demotion-risk language, plan §8.8 two-tool model paragraph (decision #3 doc-side), plan §8.1A capacity-curve formula spec (decision #9), plan §8.2 `E_OR` analysis spec (decision #10).
  - `plans/ws1-cloud-execution.md` — Stage 1.5 mini-audit gate insertion (decision #7), Stage 2.7 hidden-state count update, Stage 2.8 GREEN/YELLOW/RED revision, budget cap update.
  - `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md` — Llama amendment, `E_PCSG` two-pair definition, `E_FO/E_OR` rename, P_logprob roster 10→12.
  - `refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md` + `docs/TIMELINE.md` — supersession banners.
  - Decision memo body fixes:
    - `docs/DECISION_20260429_llama_addition.md` §2.6 WS6 row rewrite (per simplification C.5; was C.18 Edit 1 in v2).
    - `docs/DECISION_20260427_pcsg_redefinition.md` §2.5 supersession note (per simplification C.5; was C.18 Edit 2 in v2).
    - Cross-link `related_docs` headers, stale "10 white-box" residue in §3.x, etc.

- **New analysis scripts**:
  - `scripts/ws1_quant_calibration_audit.py` (decision #7 — Stage 1.5 mini-audit gate + Stage 2.8 conditional)
  - `scripts/run_exposure_horizon_placebo.py` (decision #8 B — date-shuffle placebo, 0 GPU)
  - `src/r5a/analysis/capacity_curve.py` + `scripts/run_capacity_curve_analysis.py` (decision #9 — mixed model with `family` fixed effect, B=2000 case-cluster bootstrap, 4 raw slopes + 2 leakage contrasts)
  - Tests for each new script

- **New living documents**:
  - `docs/PAPER_CAVEATS.md` creation (decision #12 — five-section caveat tracker with current draft language)

- **WS3 spec update** (decision #10 Level 2):
  - `plans/phase7-pilot-implementation.md` §5.4 — extend `C_CO` perturbation to BL2 350 post-cutoff cases as nonmember control
  - Plan §8.2 — add `E_OR ~ cutoff_exposure + factor + cutoff_exposure:factor + (1|model) + (1|case)` model with primary contrast pre-post difference

- **PREREG_STAGE1 multiplicity rule writeup** (decision #6):
  - Capacity curve BH-FDR q=0.10
  - WS6 cluster permutation
  - Reserve estimands descriptive-only with promotion rule

- **Decision #8 conditional Chinese non-financial corpus** (decision #8 A):
  - Triggered only if Llama differential calibration fails or placebo replicates accept; requires separate decision memo to choose corpus source

- **Optional capacity curve caller / test**:
  - Caller in `scripts/run_capacity_curve_analysis.py` (drives the decision-#9 analysis)
  - Tests with synthetic data verifying slope-recovery

These land in separate commits per DECISIONS.md §"Notes for the Implementation Planner" #7. Recommended order for Tier-R2-1: Block G (doc sweep) light items first, then H (new scripts) + I (PAPER_CAVEATS) + J (Tier-1 docs) per DECISIONS.md.
