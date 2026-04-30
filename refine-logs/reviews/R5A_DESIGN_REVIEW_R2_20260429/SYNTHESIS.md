---
title: R5A Design Review Round 2 — Cross-Lens Synthesis
date: 2026-04-29
review_id: R5A_DESIGN_REVIEW_R2_20260429
inputs:
  - lens_A_functional.md (Codex thread 019dd941-5969-76f2-a0c6-e6bf4f422dd8)
  - lens_B_statistics.md (Codex thread 019dd941-fb8b-78e0-bcf2-abfd501dd2b9)
  - lens_C_operational.md (Codex thread 019dd941-98d4-7b40-a85f-6458669bed25)
  - lens_D_tests.md (Codex thread 019dd941-938b-7301-9ab0-12f2c4ff9348)
  - lens_E_doc_coherence.md (Codex thread 019dd941-b8a5-78a0-94fe-4bba3d29f0a4)
status: Round 2 complete — ready for Tier-0 patch batch + Tier-1 work
target_commit: 208ef06
---

# Round 2 Synthesis

This synthesis merges 5 parallel Codex MCP `xhigh` lens reviews of the
2026-04-29 Tier-0 implementation batch (commit `208ef06`). All five
lenses ran independently; convergent findings (§2) carry higher
confidence because they replicate across orthogonal review framings.

## 1. Per-Lens Verdicts

| Lens | Verdict |
|---|---|
| **A. Functional correctness** | **Not shippable.** 4 critical bugs, 9 major issues. Strict-majority math is correct but Path E is broken end-to-end on default flags and the RunManifest finalizer accepts incomplete provenance. |
| **B. Statistical & numerical** | **Path E sound, power sim wrong.** Piecewise-WLS faithfully implements the Round 1 sketch (1 minor CI rounding bug); `simulate_phase8_power.py` is a closed-form calculator misnamed as the §8.8 simulation, and applies wrong analysis unit to E_CMMD (yields ~9% power vs the 87-99% Round 1 expected). |
| **C. Operational robustness** | **Block WS1 cloud sign-off.** 6 silent-corruption-or-divergence paths (raw YAML scalar insertion, mtime-based snapshot picking, Git-blob SHA1 wrong for LFS tokenizers, manifest not bound to traces, all-zero git fallback, hidden-state hash bound to filesystem order); 7 medium-severity risks. |
| **D. Test coverage** | **Smoke-grade, not prereg-grade.** 3 operational scripts have zero tests; the actual cloud-spend JSON-roundtrip path is never exercised; one happy-path bug in `ws1_pin_fleet.py` (silently ignores unknown `--pin-json` model IDs); `test_run_manifest_extra_forbid` and the high-noise rejection test pass spuriously. |
| **E. Plan/doc coherence** | **Not yet prereg-coherent.** Many active specs still speak in the 9-model / 5-WB / 100-case language; `R5A_FROZEN_SHORTLIST.md` lacks the Llama amendment and still defines `E_PCSG` as Qwen-only; gate removal partly propagated; ≥6 Tier-1 items still open and not tracked in `PENDING.md`. |

**One-line bottom line**: Round 2 finds the Tier-0 *shape* is right but
the *contracts and joins are loose*. The fleet pinner can produce a
"pinned"-looking YAML that does not match what ran; the RunManifest
finalizer can emit a "valid" manifest with no actual trace coverage; and
the power simulation is a planning calculator labeled as the §8.8
simulation. Fixing these is one focused patch batch (3-5 hours), not
another full design cycle.

---

## 2. Cross-Lens Convergent Critical Findings

These are issues flagged by ≥2 lenses, treated as Round 2's primary
findings.

### R2-C1. Path E does not compose end-to-end on default flags
**Flagged by:** A (critical #1), C (D.21 weak link), E (cleanup batch)

`scripts/ws1_run_logprob.py --cutoff-probe` writes to `data/pilot/cutoff_probe/traces/` but `scripts/run_cutoff_probe_analysis.py` defaults `--traces-dir` to `data/pilot/logprob_traces/`. Reproduction: run any model with `--cutoff-probe` then run the analysis script, both with default args → "no trace files matched; nothing to do".

Compounding: cutoff_observed.json is not cryptographically linked to the trace artifacts that produced it (no per-trace hashes, no probe-set hash, no Docker digest set in the JSON). The finalizer copies dates from the JSON but does not verify the traces still exist or match.

**Fix**: change analysis default to `data/pilot/cutoff_probe/traces/`; have `run_cutoff_probe_analysis.py` write trace SHAs and probe-set hash into its output JSON; have the finalizer hash that JSON.

**Severity**: block-cloud-spend.

---

### R2-C2. RunManifest finalizer accepts incomplete provenance
**Flagged by:** A (critical #2 + major #7,#8), C (block #3, C.16-C.20), D (no roundtrip test), E (drift to memo)

Multiple converging gaps in `scripts/ws1_finalize_run_manifest.py`:

1. `--traces-dir` is declared but never read — manifest can be finalized with zero `P_logprob` trace files.
2. `_read_cutoff_observed()` does not validate the JSON model-key set against `fleet.p_logprob_eligible_ids()` — extras accepted, missing silently omitted, invalid dates silently `None`.
3. `_hidden_state_subset_hash()` accepts an empty dir (returns `None, 0` and continues), uses filesystem-order first model, and assumes a per-model directory layout that contradicts what `OfflineHFBackend._save_hidden_states` actually writes (`{case_id}__{model_id}.safetensors` flat layout).
4. `_git_commit_sha()` falls back to `"0" * 40` silently — confirmatory manifests can ship with zero git commit SHA.
5. `sampling_config_hash` is mistakenly populated from the article-manifest hash, not from `config/pilot_sampling.yaml`. Sampling-policy drift is invisible.
6. `--vllm-image-digest`, `--gpu-dtype`, `--launch-env` are not required even outside `--allow-tbd` mode.
7. Quality-gate thresholds use the *eligible* fleet N (14, 12), not the *realized* set actually present in `--traces-dir`. If a provider went down and 13/14 ran, the manifest still records `8/14`.

**Fix**: hard-fail confirmatory finalization (not `--allow-tbd`) on missing traces, missing cutoff entries, missing operational provenance, all-zero git SHA. Hash the trace parquet set. Record both eligible-N and realized-N. Hash the sampling config separately.

**Severity**: block-cloud-spend.

---

### R2-C3. RunManifest is missing the Llama-decision split-tier roster fields
**Flagged by:** A (critical #3), E (memo→code drift)

`docs/DECISION_20260429_llama_addition.md` §3.2 explicitly requires:
- `fleet_white_box: list[str]` (currently 12)
- `fleet_p_predict_eligible: list[str]` (currently 14)

Neither is in `src/r5a/contracts.py:RunManifest`, neither is in `tests/r5a/test_run_manifest_contract.py:REQUIRED_FIELDS`, even though both files claim to incorporate that decision. The `quality_gate_thresholds` dict records *counts* but not *membership* — readers cannot tell from the manifest which 12 models formed the P_logprob denominator if the fleet later changes.

**Fix**: add the two list fields plus `fleet_p_logprob_eligible: list[str]`; populate from the helper methods; update tests.

**Severity**: block-cloud-spend (memo binding violation).

---

### R2-C4. Power simulation is a closed-form calculator mislabeled as §8.8
**Flagged by:** B (critical #1, #2, #3), D (zero tests on the script)

`scripts/simulate_phase8_power.py` does not implement `plan §8.8` ("Simulate `B = 2000` main-run datasets... refit planned models on each replicate... Westfall-Young in each replicate"). It computes closed-form SEs and fakes a "MC SE" via `sqrt(p(1-p)/B)` over a deterministic estimate. `--b-outer` is informational and unused.

Worse, the E_CMMD branch applies model + family random-intercept SE over 14 P_predict models, but plan §8.2 / §8.1A define E_CMMD as a fleet-aggregated case-level score with case-cluster bootstrap inference. The implemented formula gives ~9% main-run power at β=0.20 vs the Round 1 "87-99%" expected under the correct unit.

**Fix**: either (a) rename to `scripts/planning_power_calculator.py` and explicitly mark it as a coarse closed-form planner, OR (b) actually implement the §8.8 simulation. For E_CMMD specifically, replace the random-intercept formula with case-cluster bootstrap on the fleet-aggregated score. Remove the cosmetic MC-SE noise.

**Severity**: fix-before-pre-registration (cloud run can proceed; planning power claims must be correct before prereg).

---

### R2-C5. Fleet pinner has multiple silent-corruption paths
**Flagged by:** A (major #5, #6), C (block #1, #2, A.5-A.10), D (high-risk untested)

Five distinct concerns in `scripts/ws1_pin_fleet.py`:

1. **Raw YAML scalar insertion** (C block #1): `--pin-json` values are written as `f'"{value}"'` without scalar escaping. A value with backslash escapes will parse to a different string than supplied while still passing `FleetConfig.model_validate`. Round-trip equality is never asserted.
2. **HF cache mtime selection** (A major #5, C A.10): `_pick_snapshot()` picks `max(mtime)` from multiple snapshots. Mtime reflects extraction/copy timing, not the revision actually loaded by vLLM.
3. **Git-blob SHA1 vs HF LFS** (C A.11): for LFS-backed `tokenizer.json` files the HF cache uses SHA256, not git-blob SHA1. The current code's claim "matches HF's blob-store filename" is wrong for some models.
4. **Quoted `<TBD>` not patched** (C silent #1): `tokenizer_sha: "<TBD>"` (quoted) reads as `"<TBD>"` not `<TBD>`, so the placeholder check fails and the field is left as a placeholder.
5. **Idempotency bug** (C silent #2): re-running with no changes still appends `+pinned-<UTC>` to fleet_version, producing version churn without provenance change.
6. **No file locking** (C block #1, A.7): concurrent operators can lose pins; the pinning log appender silently drops corrupt history.
7. **`--vllm-image-digest` is optional and unvalidated** (A major #6, C medium): claimed required by docstring but `required=False` in argparse.
8. **Unknown `--pin-json` model IDs silently ignored** (D high-risk): `main()` iterates `fleet.models`, never checks `overrides.keys() - fleet.models.keys()`. Operator typo = silent no-op.

**Fix**: use a real YAML scalar serializer; assert exact post-parse equality for every requested pin; refuse multiple snapshots without `--revision`; document tokenizer hash convention; reject quoted placeholders explicitly; idempotent version bump (only on real changes); file locking + atomic rename; reject unknown override keys with `SystemExit`.

**Severity**: block-cloud-spend.

---

### R2-C6. Documentation has not caught up with implementation
**Flagged by:** E (entire report), A (cleanup), D (PCSG hash payload coverage)

Numerous active-spec stale references:
- `PENDING.md:16` says "10 white-box entries" (should be 12); `PENDING.md:23-26` lists `LogProbTrace` closure as active (now done).
- `plans/phase7-pilot-implementation.md` has many residual `pilot_100_cases`, "9-model", "5 white-box", `S16a/S16b/S12`, demotion-risk language despite §7.1A being correct.
- `R5A_FROZEN_SHORTLIST.md` lacks the Llama amendment, defines `E_PCSG` as Qwen-only, lists 10 white-box for P_logprob.
- `MEASUREMENT_FRAMEWORK.md` and `docs/TIMELINE.md` use 5-WB / 9-model assumptions despite being listed as active authority.
- `plans/ws1-cloud-execution.md:209` says "ALL 10 white-box" for hidden-state alignment; should be 12.
- `plans/ws1-cloud-execution.md:334` calls `scripts/ws1_quant_calibration_audit.py` which does not exist.

The PCSG registry hash also has no payload-coverage test: a future field added to `PCSGPair` could become silently hash-insensitive.

**Severity**: must-fix-before-prereg (not blocking cloud spend, but blocks prereg coherence).

---

## 3. Single-Lens Findings (Important)

| ID | Lens | Finding | Severity |
|---|---|---|---|
| R2-U1 | A major #1 | `pcsg_pair_registry_hash` is `str \| None` even though DECISION_20260427 §3.2 requires `str` | fix-before-prereg |
| R2-U2 | A major #2 | PCSG validator accepts duplicate members and self-pairs (`early == late` or `members: [x, x]`) | fix-before-prereg |
| R2-U3 | A major #3 | `--vllm-image-digest <TBD>` passes the truthiness check; no format validation | fix-before-cloud |
| R2-U4 | A major #4 | `_check_pinning_for_pilot` doesn't require `tokenizer_family` or `quant_scheme` non-null; backend silently substitutes `""` and `"fp16"` | fix-before-cloud |
| R2-U5 | A minor #4 | `smoke_phase7.py` returns success even when the fleet count warnings fire; not a hard gate | cleanup |
| R2-U6 | B A.7 | Path E CI rounding: `int()` floors both endpoints; should be `floor` lower / `ceil` upper | minor numerical issue |
| R2-U7 | B A.9 | If all WLS candidates are singular, `_grid_search_kappa` returns the lower grid bound with zero β instead of `-1` (and the acceptance rule then rejects, but the rejected point estimate looks like a real knee in the report) | cleanup |
| R2-U8 | B A.11 | Detector is much better than threshold under iid article noise but still vulnerable to month-level shocks (1/20 false-positive in Codex's small simulation) — Adversarial A2 not fully closed | fix-before-prereg via Tier-1 #14 |
| R2-U9 | B B.4 | `reweighted_phase8 = 0.85×` heuristic is invented; plan §8.8 specifies composition reweighting, not a fixed multiplier | fix-before-prereg |
| R2-U10 | C medium #5 | `_hash_strings` uses `\n` join; if any future `case_id` contains a newline, hashes collide silently | fix-before-prereg |
| R2-U11 | C medium #7, D coverage | PCSG hash payload field coverage has no test — future `PCSGPair` field can become silently hash-insensitive | add test |
| R2-U12 | D test #2 | `test_run_manifest_extra_forbid` only expects "any ValidationError" — could pass spuriously if `_baseline_kwargs` becomes invalid for an unrelated reason; should pin `errors[].type == "extra_forbidden"` | fix test |
| R2-U13 | D test #15 | `test_detect_cutoff_rejects_high_noise_wide_ci` rejects, but the point estimate is wrong-direction; doesn't isolate "wide-CI-despite-true-step" semantics | fix test |
| R2-U14 | D ergonomics | `conftest.py` at repo root injects sys.path globally; could mask import-path bugs. Move to `tests/conftest.py` or use editable install | cleanup |
| R2-U15 | E #20 | Exploratory multiplicity rule (BH-FDR q=0.10 vs descriptive-only) still not chosen | fix-before-prereg |
| R2-U16 | E Tier-1 #15 | `cutoff_observed` not renamed to `exposure_horizon_observed`; rename decision still pending | fix-before-prereg or revoke |
| R2-U17 | E Tier-2 tracking | No paper-day caveat tracker file or PENDING entry for the 5 Round 1 Tier-2 caveats | fix-before-prereg |
| R2-U18 | E gate residue | `docs/DECISION_20260429_llama_addition.md:202-206` rescales a "WS6 mechanistic trigger" to 7/12, contradicting `gate_removal §2.4` (trigger removed). One memo overrides the other; readers can't tell | clarify |

---

## 4. What This Means for the Original SYNTHESIS Tier Buckets

| Round 1 Tier-0 item | Status post-208ef06 |
|---|---|
| #1 RunManifest schema closure | **PARTIAL** — fields present, but missing 2 split-tier rosters (R2-C3) and several fields are too permissive (R2-C2, R2-U1) |
| #2 fleet-pin writer | **PARTIAL** — writer exists, but raw-scalar insertion + mtime snapshot picking + LFS-incorrect tokenizer SHA + non-idempotent version bump (R2-C5) |
| #3 piecewise-WLS knee detector | **DONE** with one minor numerical bug (R2-U6) and one open robustness concern (R2-U8) |
| #4 RunManifest finalizer | **PARTIAL** — finalizer exists but doesn't actually finalize (R2-C2) |
| #5 distinct Path E run mode | **PARTIAL** — runner is correct but analysis default doesn't match (R2-C1) |
| #6 pcsg_pairs validator | **PARTIAL** — validator exists but accepts duplicate members and self-pairs (R2-U2) |
| #10 power-sim rewrite | **NOT DONE as advertised** — script implemented as closed-form calculator, mislabeled, with wrong E_CMMD unit (R2-C4) |

| Round 1 Tier-1 item | Status |
|---|---|
| #11 2nd PCSG temporal pair (Llama) | **DONE** |
| #12 C_FO sycophancy controls + rename | **NOT STARTED** |
| #13 AWQ-vs-fp16 audit | **PARTIAL** — design only; `scripts/ws1_quant_calibration_audit.py` does not exist |
| #14 Path E negative-control corpus | **NOT STARTED** |
| #15 cutoff provenance Methods + rename | **PARTIAL** |
| #16 E_PCSG_capacity_curve analysis spec | **NOT STARTED** |
| #17 WS6 conditional exit-gate supersession | **PARTIAL** — fixed in §13 but residue in 0429_llama §2.6 and 0427 memo §2.5 |
| #18 sweep stale fleet-count refs | **PARTIAL** — main plan partly done, frozen shortlist + measurement framework + timeline + PENDING still old |
| #19 retire S16a/S16b/S12 explicitly | **PARTIAL** — §7.1A correct, residue in §7.2 / §8.8 / risk register |
| #20 exploratory multiplicity rule | **NOT STARTED** |

---

## 5. Recommended Remediation — Round 2 Patch Batch

### Tier R2-0 — BLOCK CLOUD SPEND (must fix before any GPU rental)

1. **[Code]** Fix `run_cutoff_probe_analysis.py` default `--traces-dir` to `data/pilot/cutoff_probe/traces/`; have it record per-trace SHAs + probe-set hash into output JSON. **(R2-C1)**

2. **[Code]** Harden `ws1_finalize_run_manifest.py`: read `--traces-dir`; assert cutoff JSON keys = P_logprob-eligible set; reject invalid date strings; reject empty/partial hidden-state dirs; require non-zero git SHA / vllm digest / dtype / launch env in confirmatory mode; switch `sampling_config_hash` to actually hash the sampling config; record realized-N alongside eligible-N. **(R2-C2)**

3. **[Code]** Add `fleet_white_box`, `fleet_p_predict_eligible`, `fleet_p_logprob_eligible` fields to `RunManifest`; populate from finalizer; update `REQUIRED_FIELDS` in test. Tighten `pcsg_pair_registry_hash` to required `str`. **(R2-C3, R2-U1)**

4. **[Code]** Harden `ws1_pin_fleet.py`: reject unknown `--pin-json` model IDs with `SystemExit`; use a YAML scalar serializer (or assert exact `FleetConfig` field equality post-parse for every patched key); refuse multi-snapshot HF caches without explicit `--revision`; document tokenizer hash convention (and switch to HF Hub ETag if available); patch quoted `<TBD>`; idempotent fleet_version bump (only on real changes); file locking + atomic rename; require `--vllm-image-digest` (validate `^sha256:[0-9a-f]{64}$`). **(R2-C5)**

5. **[Code]** Add PCSG validator rejection for duplicate `members` and self-pairs (`early == late`). **(R2-U2)**

6. **[Code]** Tighten `_check_pinning_for_pilot` to require non-null `tokenizer_family` and `quant_scheme`. Validate `--vllm-image-digest` format. **(R2-U3, R2-U4)**

7. **[Code]** Either rename `simulate_phase8_power.py` to a planning-calculator script and remove cosmetic MC SE, OR replace with an actual §8.8 Monte Carlo simulation. Fix E_CMMD analysis unit (case-level fleet-aggregated, case-cluster bootstrap). **(R2-C4)**

8. **[Tests]** Add tests for the operational scripts per Lens D §B.16-B.20 + suggested outlines (≥10 new tests):
   - `ws1_pin_fleet.py`: target-only patching, unknown-key rejection, idempotency, hash invariance, `--check` no-write
   - `ws1_finalize_run_manifest.py`: `--allow-tbd` gate behavior, threshold math against actual fleet, JSON roundtrip, hidden-state hash fixture
   - `simulate_phase8_power.py`: PCSG SE anchor, CMMD SE shape, WY power anchor points
   - `ModelConfig.participates_in_*()` direct predicate tests
   - `LogProbTrace` validator rejection paths
   - PCSG hash payload coverage test (R2-U11)

### Tier R2-1 — MUST FIX BEFORE PRE-REGISTRATION

9. **[Doc sweep]** Per Lens E §"recommended doc-cleanup batch":
   - `R5A_FROZEN_SHORTLIST.md`: Llama amendment to header + body; E_PCSG → 2 temporal pairs; P_logprob → 12 white-box.
   - `phase7-pilot-implementation.md`: sweep `pilot_100_cases`, "5 white-box" / "9-model", `S16a/S16b/S12` residue (§7.2, §8.8, §13 risk register, §14.2 banner).
   - `ws1-cloud-execution.md:209`: 10 → 12 white-box for WS6 alignment.
   - `MEASUREMENT_FRAMEWORK.md` + `docs/TIMELINE.md`: supersession banners or active updates.
   - `PENDING.md`: close `LogProbTrace`; update WS1 provenance to 12; add Tier-1 entries for #12/#13/#14/#15/#16/#20.

10. **[Decision]** Resolve `cutoff_observed` → `exposure_horizon_observed` rename: either do it (cascades through code/tests/manifest/decision-memos), or revoke. **(R2-U16)**

11. **[Decision]** Choose exploratory multiplicity rule (BH-FDR q=0.10 vs descriptive-only). **(R2-U15)**

12. **[Code]** Decide AWQ-vs-fp16 audit fate: implement `scripts/ws1_quant_calibration_audit.py` OR mark Stage 2.8 as design-pending in WS1 plan. **(Tier-1 #13)**

13. **[Code/Doc]** Path E negative-control corpus (Tier-1 #14) — Codex's small simulation showed month-level shocks can still produce false positives, so this is no longer just paper hygiene. Either ship the Chinese non-financial corpus or run a topic-shuffled placebo knee test. **(R2-U8)**

14. **[Code]** Tier-1 #16 (capacity-curve analysis spec): add the model formula to plan §8.1A/§8.2 and implement a basic version in `src/r5a/analysis/`.

15. **[Doc]** C_FO sycophancy controls + rename E_FO (Tier-1 #12) — design memo + WS3 amendment. Relevant for the WS3 implementation phase that follows Tier-0.

16. **[Doc]** Add `docs/PAPER_CAVEATS.md` for Round 1 Tier-2 caveats #21-#25. **(R2-U17)**

### Tier R2-2 — CLEANUP / NICE-TO-HAVE

17. Path E CI endpoint rounding: floor lower / ceil upper (R2-U6).
18. `_grid_search_kappa` return `-1` when all candidates singular (R2-U7).
19. `_hash_strings` switch to canonical JSON array (R2-U10).
20. Move `conftest.py` to `tests/conftest.py` or add `pyproject.toml` (R2-U14).
21. Tighten `test_run_manifest_extra_forbid` and the high-noise rejection test (R2-U12, R2-U13).
22. `smoke_phase7.py` warning → exit-status decision (R2-U5).

---

## 6. Recommendation on Cloud-Spend Gate

**Recommend: do NOT initiate WS1 cloud Stage 1 yet.**

The Tier-R2-0 list (items 1-8 above) is roughly a 4-6 hour focused
patch batch — much smaller than the original Tier-0 implementation
batch — but addresses exactly the silent-corruption and
contract-looseness issues that would make a confirmatory run
non-reproducible.

After Tier-R2-0 lands, the path is:
1. Local `pytest tests/r5a -q` + the new tests must all pass.
2. The user clicks through HF Meta licenses (still pending; PENDING.md).
3. The user kicks off CLS post-2026-02 corpus extraction (still pending; PENDING.md).
4. WS1 cloud Stage 0 commit (Stage 0 sign-off in `ws1-cloud-execution.md` §8 still pending).
5. Stage 1 instance provisioning.
6. Stage 2 per-model loop.

Tier-R2-1 (items 9-16 in §5) can land in parallel during cloud spend or
between Stage 2 and pre-registration freeze; they do not block the
cloud run as long as Tier-R2-0 is closed.

---

## 7. Provenance

All 5 lens reports were produced by independent Codex MCP `xhigh`
reasoning calls dispatched in parallel via separate sub-agents. Each
Codex thread had no knowledge of other lenses. Convergent findings
(§2) carry higher confidence; single-lens findings (§3) reflect each
lens's specialty area.

Codex thread IDs are recorded in the YAML frontmatter for re-engagement.

Wall-clock dispatch: 5 sub-agents launched in parallel, longest at ~561s
(Lens E), all five completed within the 600s sub-agent watchdog limit.
No fallback to manual codex-CLI execution was needed.
