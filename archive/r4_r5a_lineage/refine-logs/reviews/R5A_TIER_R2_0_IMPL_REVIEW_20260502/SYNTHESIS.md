# Cross-lens synthesis — Tier-R2-0 implementation review (HEAD `349efab`)

Date: 2026-05-02. Reports: A=functional, B=tests, C=operational, D=code_quality, E=coherence, F=role_rotation.

This document only categorizes and cross-references findings; it does **not** prescribe fixes. Each entry cites the originating REPORT(s); follow citations to the lens reports for full context. Severity tags are taken from the lens that flagged the finding; where lenses disagree, the higher severity is recorded and the disagreement is listed under § Conflicts.

---

## § Novel findings (the load-bearing section)

Sorted by severity. Tagged `[novel]`. Lens F is novel by design (no anchor questions).

### HIGH
- **Confirmatory finalization can omit `--hidden-states-dir` and silently write `hidden_state_subset_hash=None`** — A-Novel#1, C-Novel#2, D-Novel#1, F-Role2#3. `scripts/ws1_finalize_run_manifest.py:106, 614, 615, 709`. Four-lens consensus; no clause forces the flag. `[novel]`
- **Path-E provenance detached from RunManifest**: analyzer emits `trace_shas` + `probe_set_sha256`, finalizer reads only the derived `horizon_observed` and discards both — C-Novel#1, F-Role2#1, F-Role2#2 (and overlaps with anchored A-A2 and C-Meta below). `scripts/run_exposure_horizon_analysis.py:214, 217`; `scripts/ws1_finalize_run_manifest.py:250, 587-594, 705`. `[novel]`
- **Stale or malformed exposure-horizon JSON silently becomes a "rejected horizon"**: `_read_exposure_horizon()` treats missing `horizon_observed` as `None`-rejected — A-Novel#2. `scripts/ws1_finalize_run_manifest.py:254-256`. `[novel]`
- **Model pin SHAs are not format/coherence-validated end-to-end** — B-Novel#2, C-Novel#3. Pinner only rejects unknown model IDs; `ModelConfig` types both as `str | None`; finalizer clause 3 only rejects placeholders. `scripts/ws1_pin_fleet.py:397, 421, 426`; `src/r5a/fleet.py:63-64`; `scripts/ws1_finalize_run_manifest.py:480, 484`. `[novel]`
- **`test_pin_fleet_validates_hash_invariant_and_idempotency` is tautological**: only asserts byte-equality between two runs, would still pass if `--pin-json` were ignored — B-Novel#1. `tests/r5a/test_pin_fleet.py:161, 179`. `[novel]`
- **`PENDING.md` instructs operator to compute git-blob SHA for `tokenizer.json`**, conflicting with decision-#4 SHA-256 content-hash semantics enforced elsewhere — E-Novel#1. `PENDING.md:24` vs `config/fleet/r5a_fleet.yaml:35`, `scripts/ws1_pin_fleet.py:23`, `src/r5a/contracts.py:458`. `[novel]`
- **Pinner mutates fleet YAML *before* parsing the existing pinning log**: a corrupt log raises after the fleet has already been changed — F-Role1#1. `scripts/ws1_pin_fleet.py:492-493` vs `:511-518`. `[novel]`

### MED
- **Confirmatory hard-fail collector is bypassed for clauses 5/6** (helpers `_validate_traces_dir` and `_read_exposure_horizon` raise before `_confirmatory_hard_fail` runs) — D-Novel#2, F-Role1#2 (also confirms anchored A-A1 / B-A1 below). `scripts/ws1_finalize_run_manifest.py:217-227, 275-288, 588, 610, 674`. `[novel]`
- **`month_stratified_mink` score regressions are not caught by tests** (only month-key/count assertions; detector tests bypass `LogProbTrace` conversion) — B-Novel#3. `tests/r5a/test_exposure_horizon.py:88, 94`. `[novel]`
- **Analyzer→finalizer JSON contract has no end-to-end test**: finalizer tests use a hand-built fixture, so producer key drift is invisible — B-Novel#4. `scripts/run_exposure_horizon_analysis.py:186`; `tests/r5a/test_finalize_run_manifest.py:156`. `[novel]`
- **Hidden-state validation has only a happy-path synthetic-filename fixture** — B-Novel#5. `scripts/ws1_finalize_run_manifest.py:302`; `tests/r5a/test_finalize_run_manifest.py:402`; `src/r5a/backends/offline_hf.py:260`. `[novel]`
- **Real fleet cardinalities are not pinned by tests**: thresholds called with hard constants (`n_p_predict=14, n_p_logprob=12`); fleet smoke test only checks `len(temporal_pairs()) >= 1` — B-Novel#7. `tests/r5a/test_finalize_run_manifest.py:426`; `tests/r5a/test_fleet_config.py:98`. `[novel]`
- **Path-E trace/probe mismatches silently shrink the analysis set**: `month_stratified_mink()` skips traces whose `case_id` is missing from probe fixture without warning — C-Novel#4. `src/r5a/analysis/exposure_horizon.py:97, 99`; `scripts/run_exposure_horizon_analysis.py:174, 186`. `[novel]`
- **Confirmatory manifests can be written without runstate lineage** (no hard-fail clause for missing/non-terminal runstate) — C-Novel#5. `scripts/ws1_finalize_run_manifest.py:667, 671, 674`. `[novel]`
- **`config/prompts/R5A_OPERATOR_SCHEMA.md` still uses `C_FO`/`E_FO`** while code enum is `C_CO` and planning labels are `E_OR` — D-Novel#4. `config/prompts/R5A_OPERATOR_SCHEMA.md:26, 158`; `src/r5a/contracts.py:42`. `[novel]`
- **`LogProbTrace` docstring claims `top_alternative_token_ids` but schema persists only logprobs** — E-Novel#3. `src/r5a/contracts.py:236, 265, 268`. `[novel]`
- **`ExposureHorizonEstimate.p_drop_gt_005` field name implies fixed 0.05 but `detect_exposure_horizon` accepts configurable `drop_threshold`** — E-Novel#4. `src/r5a/analysis/exposure_horizon.py:79, 286, 412`. `[novel]`
- **Pinner docstring says log append is "best-effort" but implementation raises on corrupt/non-array logs after the fleet write** — E-Novel#5. `scripts/ws1_pin_fleet.py:42, 493, 515`. `[novel]`
- **`planning_power_calculator.py` emits `fo_eligibility` on the `E_OR_E_NoOp_beta_cutoff` row** — D-Novel#5 (LOW), E-Novel#2 (MED). `scripts/planning_power_calculator.py:355, 358, 392`. `[novel]`
- **Pinning log records requested values as `pinned_records` even when the patcher SKIP'd a conflict** — F-Role3#2. `scripts/ws1_pin_fleet.py:358-362, 443-447, 502-508`. `[novel]`
- **Final manifest write is non-atomic + non-idempotent**: new `run_id`/`created_at` per run, direct `Path.write_text` (no temp+replace) — F-Role3#1 (overlaps anchored C-A9 below). `scripts/ws1_finalize_run_manifest.py:684-686, 716-722`. `[novel]`

### LOW
- **Pinner self-misclassifies its own quoted SHA as a conflicting pre-existing value on rerun**: `current` includes surrounding quotes so equality with the new value never matches — D-Novel#3. `scripts/ws1_pin_fleet.py:347, 353, 355`. `[novel]`
- **MC SE row test only checks 2 of 4 retired CI key names**: would miss reintroduction of `power_pilot_ci95_high` / `power_main_ci95_low` — B-Novel#6. `tests/r5a/test_planning_power_calculator.py:74`. `[novel]`

---

## § Anchored findings

Verification results for the kickoff anchor questions. Tagged `[anchored]`. "Cleared" = reviewer rejected the anchor as not-a-real-concern.

### HIGH
- **Clauses 5/6 violate the collect-and-report contract** (helpers raise before the unified collector). Verified by A-Anchored#1, B-Anchored#1, and reinforced by D-Novel#2 / F-Role1#2 above. `scripts/ws1_finalize_run_manifest.py:219, 267, 280, 674`; `tests/r5a/test_finalize_run_manifest.py:291, 363, 378`. `[anchored]`
- **Corrupted HF cache passes pinning**: snapshot directory name trusted as `hf_commit_sha`; tokenizer JSON not parsed; SHA format not validated — C-Anchored#1. `scripts/ws1_pin_fleet.py:233, 237, 242`. `[anchored]`
- **Half-written / corrupt / stale / wrong-row-count pilot parquet passes finalization**: `_validate_traces_dir()` only globs filenames, hard-fail only checks roster keys — C-Anchored#2. `scripts/ws1_finalize_run_manifest.py:206, 229, 515`. `[anchored]`
- **`RunManifest` docstring still describes the schema as `cutoff_observed` / `cutoff_date_yaml`** after the actual rename to `exposure_horizon_observed` — E-Anchored#5. `src/r5a/contracts.py:390, 392, 396, 474`. `[anchored]`

### MED
- **C.10 per-trace SHA-256 computation is not implemented in finalizer**: trace map keeps only `model_id → path`; no hashes recorded — A-Anchored#2 (also Lens F's "trace identity not preserved"). `scripts/ws1_finalize_run_manifest.py:610, 684`. `[anchored]`
- **Partial horizon JSON passes if every roster key is present but rows are incomplete** (missing `horizon_observed` ≡ rejected) — C-Anchored#3 (overlaps A-Novel#2). `scripts/ws1_finalize_run_manifest.py:254, 255, 275`. `[anchored]`
- **`HF_HUB_CACHE` is silently ignored when set to a nonexistent path** — C-Anchored#7. `scripts/ws1_pin_fleet.py:152, 156, 158`. `[anchored]`
- **Final RunManifest writes are non-atomic** (unlike pinner, no temp+replace) — C-Anchored#9 (also F-Role3#1 above). `scripts/ws1_finalize_run_manifest.py:716, 719`. `[anchored]`
- **F.35 collapsed integration test does not really gate clause-5/6 fail-fast regression**: only asserts clauses (1,2,3,4,7,8); helper test for clause 5 covers date parsing rather than roster mismatch — B-Anchored#1. `tests/r5a/test_finalize_run_manifest.py:291, 363, 378`. `[anchored]`
- **F.34 idempotency test masks default-timestamp auto-bump drift**: both runs pass the same explicit `--bump-version` — B-Anchored#2. `tests/r5a/test_pin_fleet.py:166, 175`; `scripts/ws1_pin_fleet.py:465`. `[anchored]`
- **B.24 explicit-revision happy path is untested** (only the multi-snapshot rejection path) — B-Anchored#5. `tests/r5a/test_pin_fleet.py:227`; `scripts/ws1_pin_fleet.py:196`. `[anchored]`
- **C.12 sampling-config-missing is not tested alone** (`_run_finalize` always passes `--sampling-config`) — B-Anchored#6. `tests/r5a/test_finalize_run_manifest.py:225, 460`; `scripts/ws1_finalize_run_manifest.py:543`. `[anchored]`
- **Mock pin-fleet fixture has only one white-box model and `pcsg_pairs: []`**, missing real fleet shape — B-Anchored#7. `tests/r5a/test_pin_fleet.py:30`. `[anchored]`
- **`build_cutoff_probe_set.py` docstring says 24mo/1,440 articles vs default 36mo/2,160** — E-Anchored#1. `scripts/build_cutoff_probe_set.py:4, 52`; `scripts/run_exposure_horizon_analysis.py:15`. `[anchored]`
- **`--drop-threshold` help text claims "reported alongside" but the threshold also gates accept/reject** — E-Anchored#2. `scripts/run_exposure_horizon_analysis.py:119, 122`; `src/r5a/analysis/exposure_horizon.py:292, 421`. `[anchored]`
- **Finalizer CLI `--help` not self-contained for confirmatory requirements** (`--exposure-horizon`, `--vllm-image-digest`, `--gpu-dtype` lack help text) — E-Anchored#3. `scripts/ws1_finalize_run_manifest.py:105, 116, 117, 468, 533`. `[anchored]`
- **`ws1_run_logprob.py --vllm-image-digest` help omits the `sha256:<64-hex>` requirement** — E-Anchored#4. `scripts/ws1_run_logprob.py:103, 214, 247`. `[anchored]`
- **Stale `cutoff_probe/` path remains in modified PENDING guidance** despite rename to `data/pilot/exposure_horizon/` — E-Anchored#6. `PENDING.md:37`; `scripts/build_cutoff_probe_set.py:45`. `[anchored]`

### LOW
- **`[clause 2]` is reused for the sampling-config existence failure**, duplicating the vLLM image-digest clause — A-Anchored#3, F-Role1#3. `scripts/ws1_finalize_run_manifest.py:466-476, 540-548`. `[anchored]`
- **F.38 source-inspection test is brittle**: requires every `PCSGPair` field name to appear as a quoted string literal in `FleetConfig.pcsg_pair_registry_hash` — B-Anchored#4. `tests/r5a/test_fleet_config.py:221`; `src/r5a/fleet.py:148`. `[anchored]`
- **`.gitignore` legacy line ignores the whole `data/pilot/cutoff_probe/` subtree** — could mask future writes — C-Anchored#10. `.gitignore:35, 37`. `[anchored]`
- **PENDING.md "Last updated" date predates the new Phase-8-MC entry** — E-Anchored#7. `PENDING.md:9, 15`. `[anchored]`

### Cleared anchors (verified as not-a-concern; recorded for audit)
- F.36 numerical anchors `_se_pcsg_pair(2048, 2, 0.98, 4.5) ≈ 0.071027`, `_wy_power(0.2, 0.071, 2.8) ≈ 0.506742`, `_wy_power(0.3, 0.071, 2.8) ≈ 0.922972` independently verified — B-Anchored#3 (cleared).
- Wrong vLLM image digest format **is** rejected by both pinner and finalizer — C-Anchored#4 (cleared).
- `--allow_tbd` typo **is** rejected by argparse — C-Anchored#5 (cleared).
- Confirmatory mode does **not** allow `sampling_config_hash=""` to land — C-Anchored#6 (cleared; dev-mode caveat noted).
- Path-E and pilot parquet suffixes do **not** cross in the finalizer — C-Anchored#8 (cleared).
- `_patch_model_block` lambda closure is fine — D anchored (cleared).
- CRLF handling in field regex is correct — D anchored (cleared).
- `_atomic_write_text` avoids the Windows `NamedTemporaryFile` lock pitfall — D anchored (cleared).
- Placeholder `None` vs `"<TBD>"` are functionally consistent — D anchored (cleared).
- Hidden-state canonical case-set mismatch is caught by count + missing-canonical checks (the *omitted-arg* path is the real concern, listed above as HIGH novel) — D anchored (cleared).
- No consumer parser depends on `n_models`/`n_families` being present on every planning row — D anchored (cleared).
- No problematic broad `except Exception` in changed paths — D anchored (cleared).
- No mutable-default-arg pitfalls in changed paths — D anchored (cleared).
- `C_FO` → `C_CO` rename is consistent across `audit/__init__.py`, `perturbations/__init__.py`, fleet header, and `PerturbationArtifact` — E anchored (cleared); the conflict is in `R5A_OPERATOR_SCHEMA.md` (D-Novel#4) and `PENDING.md` (E-Novel#1).
- Tokenizer-SHA decision-#4 wording is internally consistent across `contracts.py`, `r5a_fleet.yaml`, and pinner docstring — E anchored (cleared).
- 8 clauses are present inside `_confirmatory_hard_fail()` itself; the contract violation is the *call ordering* relative to helpers — A anchored (cleared on the helper-internal anchor; reframed as the HIGH finding above).
- No `[CUT v3]` step accidentally implemented (no file-lock/sentinel, no B.25 equality assert, no canonical-JSON `_hash_strings`, no realized-N threshold keys, no C.18 memo edits) — A anchored (cleared).

---

## § Severity buckets

Each finding is `[anchored]` or `[novel]`. CRIT is reserved for "must fix before cloud spend".

### CRIT
- *(none)*

### HIGH
1. `[novel]` Hidden-state subset hash can be `None` in confirmatory mode — A-N1 / C-N2 / D-N1 / F-Role2#3.
2. `[novel]` Path-E provenance (`trace_shas`, `probe_set_sha256`) detached from RunManifest — C-N1 / F-Role2#1+2.
3. `[novel]` Stale/malformed exposure-horizon JSON treated as rejected horizon — A-N2.
4. `[novel]` Model pin SHA values not format/coherence-validated — B-N2 / C-N3.
5. `[novel]` Pin-fleet idempotency test is tautological — B-N1.
6. `[novel]` `PENDING.md` operator instruction conflicts with decision-#4 (git-blob SHA vs SHA-256 content-hash) — E-N1.
7. `[novel]` Pinner mutates fleet before parsing existing pinning log — F-Role1#1.
8. `[anchored]` Clauses 5/6 violate collect-and-report contract — A-A1 / B-A1 (also reinforced by D-N2 / F-Role1#2).
9. `[anchored]` Corrupted HF cache passes pinning (no SHA-format / tokenizer-content validation) — C-A1.
10. `[anchored]` Half-written / corrupt pilot parquet passes finalization — C-A2.
11. `[anchored]` `RunManifest` docstring still describes `cutoff_observed` schema — E-A5.

### MED
12. `[novel]` Hard-fail collector bypassed for clauses 5/6 — D-N2 / F-Role1#2 (overlaps anchored #8).
13. `[novel]` `month_stratified_mink` score regressions not caught by tests — B-N3.
14. `[novel]` Analyzer→finalizer JSON contract has no e2e test — B-N4.
15. `[novel]` Hidden-state validation tests are happy-path-only — B-N5.
16. `[novel]` Real fleet cardinalities not pinned by tests — B-N7.
17. `[novel]` Path-E trace/probe mismatches silently shrink analysis set — C-N4.
18. `[novel]` No runstate lineage clause in confirmatory mode — C-N5.
19. `[novel]` `R5A_OPERATOR_SCHEMA.md` still uses `C_FO`/`E_FO` — D-N4.
20. `[novel]` `LogProbTrace` docstring vs schema mismatch on `top_alternative_token_ids` — E-N3.
21. `[novel]` `p_drop_gt_005` field name vs configurable threshold — E-N4.
22. `[novel]` Pinner docstring claims log-append is "best-effort" but raises — E-N5.
23. `[novel]` `planning_power_calculator` emits `fo_eligibility` on E_OR row — D-N5 / E-N2.
24. `[novel]` Pinning log records SKIP'd records as pinned — F-Role3#2.
25. `[novel]` Final manifest write non-atomic / non-idempotent — F-Role3#1 (overlaps anchored #28).
26. `[anchored]` C.10 trace SHA computation not implemented — A-A2.
27. `[anchored]` Partial horizon JSON passes if rows incomplete — C-A3.
28. `[anchored]` `HF_HUB_CACHE` silently ignored if dir missing — C-A7.
29. `[anchored]` Final RunManifest write non-atomic — C-A9.
30. `[anchored]` F.35 collapsed integration test misses clause-5/6 fail-fast regression — B-A1.
31. `[anchored]` F.34 idempotency masks default-timestamp drift — B-A2.
32. `[anchored]` B.24 explicit-revision happy path untested — B-A5.
33. `[anchored]` C.12 sampling-config-missing not tested in isolation — B-A6.
34. `[anchored]` Pin-fleet mock fixture missing white-box / PCSG shape — B-A7.
35. `[anchored]` `build_cutoff_probe_set.py` docstring 24mo/1.4k vs default 36mo/2.1k — E-A1.
36. `[anchored]` `--drop-threshold` help misleading — E-A2.
37. `[anchored]` Finalizer CLI `--help` missing for confirmatory requirements — E-A3.
38. `[anchored]` `ws1_run_logprob` `--vllm-image-digest` help incomplete — E-A4.
39. `[anchored]` Stale `cutoff_probe/` path in PENDING — E-A6.

### LOW
40. `[novel]` Pinner self-misclassifies own quoted SHA as conflict — D-N3.
41. `[novel]` MC SE row test only checks 2 of 4 retired keys — B-N6.
42. `[anchored]` `[clause 2]` reused for sampling-config — A-A3 / F-Role1#3.
43. `[anchored]` F.38 source-inspection brittle — B-A4.
44. `[anchored]` `.gitignore` legacy line subtree-wide — C-A10.
45. `[anchored]` PENDING "Last updated" predates new entry — E-A7.

---

## § Agreements across lenses (≥ 2 lenses)

Each agreement makes a finding more load-bearing — these are the structural threads worth flagging first.

| # | Theme | Lenses | Severity (consensus) |
|---|---|---|---|
| 1 | **Hidden-state subset hash can be `None` because `--hidden-states-dir` is optional** | A, C, D, F | HIGH novel |
| 2 | **Clauses 5/6 violate collect-and-report contract (helpers raise before `_confirmatory_hard_fail`)** | A, B, D, F | HIGH (anchored on A/B; reinforced novel on D/F) |
| 3 | **Path-E provenance / trace SHA missing from RunManifest** (analyzer emits `trace_shas`+`probe_set_sha256`; finalizer drops them; C.10 plan step unimplemented) | A (anchored), C, F | HIGH novel + MED anchored |
| 4 | **`[clause 2]` label collision (vLLM image digest + sampling-config)** | A, F | LOW anchored |
| 5 | **Final RunManifest write is non-atomic + non-idempotent** | C, F | MED |
| 6 | **Malformed pin SHA values are admissible (no format gate, only placeholder gate)** | B, C | HIGH novel |
| 7 | **`fo_eligibility` JSON-key residue on E_OR row** | D, E | MED novel (D=LOW, E=MED — see Conflicts) |
| 8 | **Stale or partial exposure-horizon JSON silently passes** | A (novel), C (anchored) | HIGH novel + MED anchored |
| 9 | **`C_FO`/`E_FO` rename incomplete in non-Python surfaces** (`R5A_OPERATOR_SCHEMA.md`, `PENDING.md`, `planning_power_calculator` JSON labels) | D, E | MED + HIGH (PENDING.md) novel |

Findings hit by 4 lenses (#1, #2) are the strongest structural signals.

---

## § Conflicts across lenses

Findings where lenses disagreed:

- **Severity disagreement on `fo_eligibility` JSON-key residue (#7 above):** Lens D rated it LOW (rename residue, no consumer breakage shown), Lens E rated it MED (JSON-key surface stability matters for downstream). Synthesis recorded as MED to preserve the higher-severity reading; triage may want to read both reports.
- **No substantive contradictions otherwise.** Several anchors that one lens cleared (e.g. C-A6 on sampling-config-missing in confirmatory mode) and another lens partly cleared at a different layer (e.g. B-A6 on test coverage of that same path) are complementary, not contradictory.

---

## § Meta-findings (proposed kickoff reframes)

Each lens flagged whether the kickoff anchor list itself was pointed in the right direction. **These are not actions — they are observations the synthesis surfaces for triage.**

- **Lens A (functional)**: Anchor list underweights the **"optional CLI argument bypass"** class. Highest-risk failures are required artifacts left optional at the CLI layer (e.g. `--hidden-states-dir`) that never enter the confirmatory validation path, not bad helper internals.
- **Lens B (tests)**: Anchors focus on individual helper behavior; missing **artifact-contract coverage across the CLI chain** — `ws1_run_logprob` output naming → `run_exposure_horizon_analysis` JSON → `ws1_finalize_run_manifest` ingestion are tested as isolated assumptions rather than one producer/consumer chain.
- **Lens C (operational)** [MED]: Anchor frame "does the finalizer reject?" misses the deeper gap of **artifact binding** — the manifest rarely binds trusted fields to content hashes, case coverage, trace metadata, or runstate lineage. The plan's C.10 trace-SHA step is unimplemented.
- **Lens D (code quality)**: Anchor list underweights **contract drift outside Python modules** — `config/prompts/R5A_OPERATOR_SCHEMA.md` references are more likely to cause future artifact incompatibility than the lambda/CRLF concerns the kickoff prioritized.
- **Lens E (coherence)**: Anchor list underweights two doc surfaces that **behave like APIs** — generated JSON field names (e.g. `fo_eligibility`, `p_drop_gt_005`) and `PENDING.md` operational instructions for the cloud operator. Those surfaces are where the most consequential cold-read issues actually appeared.
- **Lens F (role-rotation)**: Role list fits this commit; the most load-bearing missing lens is not another persona but an explicit **"artifact bundle auditor"** role — does every manifest-derived value name the raw artifact that produced it?

**Convergent meta theme**: five of the six lenses (A, B, C, D, E in one form, F in another) flag the same structural gap from different angles — *artifact identity / contract surface is under-specified at the manifest and operator-doc boundary*. This is itself a synthesis-level signal worth triaging.

---

## Counts

- Novel findings: ~26 (A=2, B=7, C=5, D=5, E=5; plus all 8 of Lens F counted as novel by design = ~34 total).
- Anchored findings (excluding cleared): ~22 (A=3, B=7, C=6, E=6).
- Cleared anchors: ~16 (B=1, C=4, D=8, E=2, A=2 implicit).
- Severity distribution (deduplicated by underlying issue): CRIT=0, HIGH=11, MED=28, LOW=6.
- Novel-vs-anchored ratio (after dedup): roughly 55% novel / 45% anchored — anti-anchoring framing did surface substantive open-ended findings.
- Multi-lens agreements: 9 themes; two themes have 4-lens consensus.
