---
title: R5A Round 2 — User Decision Resolution + Tier-R2-0/R2-1 Implementation Brief
date: 2026-04-30
review_id: R5A_DESIGN_REVIEW_R2_20260429
status: 12 / 12 decisions confirmed; ready for implementation planning
purpose: hand-off document for ultraplan session — sufficient context to design a complete implementation plan without seeing the originating conversation
lifecycle: temporary scaffolding for the 2026-04-30 planning session; delete after Tier-R2-0 + R2-1 implementation lands
companion_files:
  - SYNTHESIS.md (cross-lens synthesis, contains R2-Cn convergent findings + R2-Un single-lens findings + Tier-R2-0/R2-1/R2-2 lists)
  - lens_A_functional.md
  - lens_B_statistics.md
  - lens_C_operational.md
  - lens_D_tests.md
  - lens_E_doc_coherence.md
---

# Context

This document records the user's resolutions of all 12 substantive decisions surfaced by the Round 2 design review of the R5A Tier-0 implementation batch (commit `208ef06` on `main`). The Round 2 review itself produced 5 independent Codex MCP `xhigh` lens reports and a cross-lens SYNTHESIS at `refine-logs/reviews/R5A_DESIGN_REVIEW_R2_20260429/SYNTHESIS.md`.

The SYNTHESIS identified 6 cross-lens convergent issues (R2-C1..R2-C6), 18 single-lens findings (R2-U1..R2-U18), and grouped remediation into Tier-R2-0 (block cloud spend), Tier-R2-1 (must fix before pre-registration), and Tier-R2-2 (cleanup-tier).

The 12 decisions in this document resolve the *substantive* design questions raised by the SYNTHESIS — meaning where multiple legitimate options exist and the user's judgment was needed. Mechanical implementation work (e.g., "fix this bug per the lens spec") was not subject to user decision and is rolled into the implementation breakdown.

## Required reading for the planner

Before designing the implementation plan, the planner should read:

| File | Purpose |
|---|---|
| `refine-logs/reviews/R5A_DESIGN_REVIEW_R2_20260429/SYNTHESIS.md` | full convergent + single-lens findings + tier list |
| `refine-logs/reviews/R5A_DESIGN_REVIEW_R2_20260429/lens_A_functional.md` | functional bugs in commit 208ef06 |
| `refine-logs/reviews/R5A_DESIGN_REVIEW_R2_20260429/lens_B_statistics.md` | math/stat issues; piecewise-WLS sound but power sim mislabeled |
| `refine-logs/reviews/R5A_DESIGN_REVIEW_R2_20260429/lens_C_operational.md` | YAML patcher / hash invariance / finalizer hardening |
| `refine-logs/reviews/R5A_DESIGN_REVIEW_R2_20260429/lens_D_tests.md` | test coverage gaps; concrete test outlines for new tests |
| `refine-logs/reviews/R5A_DESIGN_REVIEW_R2_20260429/lens_E_doc_coherence.md` | doc drift; Tier-1 status |
| `docs/DECISION_20260427_pcsg_redefinition.md` | original PCSG + Path E + RunManifest spec |
| `docs/DECISION_20260429_gate_removal.md` | gate removal + strict-majority denominator + WS6 unconditional |
| `docs/DECISION_20260429_llama_addition.md` | split-tier fleet (P_logprob-only Llama) + 2nd PCSG pair |
| `plans/phase7-pilot-implementation.md` | pilot plan; §7.1A, §8.1A, §8.2, §8.8, §10.4, §13 most relevant |
| `plans/ws1-cloud-execution.md` | WS1 cloud staging (will gain Stage 1.5) |
| `PENDING.md` | active cross-session items |
| `R5A_FROZEN_SHORTLIST.md` (under refine-logs/reviews/R5A_STEP2/) | confirmatory family scope; needs Llama amendment |

For working tree state: target commit is `208ef06`, branch `main`, both already pushed to `origin/main`.

# 12 Decisions — Final Confirmed Form

| # | Topic | Resolution |
|---|---|---|
| 1 | `--allow-tbd` policy | A — keep flag; add `mode: confirmatory \| dev` field to RunManifest; 7-clause hard-fail in confirmatory mode |
| 2 | RunManifest fleet roster fields | C — add 2 eligible fields (`fleet_p_predict_eligible`, `fleet_p_logprob_eligible`); no realized fields; partial-run prevented via decision #1 hard-fail; rerun is the recovery path |
| 3 | Power simulation rename vs MC | A — rename to planning calculator; fix E_CMMD analysis-unit bug (case-cluster bootstrap); remove cosmetic MC SE; full §8.8 Monte Carlo deferred to post-pilot work |
| 4 | tokenizer_sha contract | B — SHA-256 of file content as loaded; replaces git-blob SHA1; clearly NOT claimed to match HF blob filename |
| 5 | `cutoff_observed` rename | A — full rename to `exposure_horizon_observed` across code, CLI, directories, docs, decision memos |
| 6 | Exploratory multiplicity rule | C — mixed: capacity curve BH-FDR q=0.10; WS6 cluster permutation; reserve estimands descriptive-only with promotion rule |
| 7 | AWQ-vs-fp16 audit | Stage 1.5 mini-audit gate (M3 grid: 5 model × 2 precision = 10 runs) + Stage 2.8 conditional (GREEN/YELLOW/RED) |
| 8 | Path E negative control | B mandatory (date-shuffle placebo, 0 GPU) + A conditional (Chinese non-financial corpus, only triggers if placebo fails or Llama calibration wide) |
| 9 | Capacity curve formula | B — mixed model with `family` as fixed effect (2 levels) + 3-way interaction; B=2000 case-cluster bootstrap; report 4 raw slopes (Carlini replication) + 2 leakage contrasts (the inferential claim) |
| 10 | E_FO sycophancy controls | Level 2 + full enum rename (`E_FO`→`E_OR`, `C_FO`→`C_CO`); BL2 350 post-cutoff cases serve as nonmember control; framing variants reserved for Phase 8 |
| 11 | WS6 trigger contradiction | gate_removal §2.4 wins; WS6 is unconditional; drop `ws6_mechanistic_*` fields from manifest; supersession notes in 3 docs |
| 12 | Tier-2 caveat tracking | C — `docs/PAPER_CAVEATS.md` (living, with current draft language for each caveat) + PENDING.md one-line index pointer |

# Per-Decision Detail

Each decision below records: (a) the problem the SYNTHESIS surfaced, (b) the resolution chosen, (c) key sub-decisions, (d) rationale highlights, (e) implementation impact.

## Decision #1 — `--allow-tbd` policy

**Problem (R2-C2 + Lens A severity #2 + Lens C block #3)**: `scripts/ws1_finalize_run_manifest.py --allow-tbd` lets dev/smoke runs through with placeholder provenance, but produces a manifest that is structurally indistinguishable from a confirmatory manifest. Downstream readers cannot tell whether the artifact is publication-grade.

**Resolution**: Option A — retain `--allow-tbd` but add a `mode: Literal["confirmatory", "dev"]` field to `RunManifest` (Pydantic, `extra="forbid"`). Default mode is `confirmatory`; passing `--allow-tbd` sets `mode="dev"` and enables the relaxed gate.

**Confirmatory hard-fail clause (7 items)**:
1. `git_commit_sha != "0" * 40`
2. `vllm_image_digest` matches regex `^sha256:[0-9a-f]{64}$`
3. Every P_logprob-eligible white-box model is present in both `tokenizer_shas` and `white_box_checkpoint_shas`, both non-empty and non-`<TBD>`
4. Every black-box `api_model_name` non-empty and non-`<TBD>`
5. `cutoff_observed` keys (after rename, `exposure_horizon_observed`) equal `fleet.p_logprob_eligible_ids()`
6. `--traces-dir` exists and contains exactly one `*__pilot.parquet` per P_logprob-eligible model
7. `launch_env` contains at minimum `CUDA_VISIBLE_DEVICES`, `VLLM_VERSION` (or platform-equivalent)

**Rationale**: writing the mode into the manifest itself (not just a CLI flag) means downstream analysis tooling can refuse to consume `mode="dev"` manifests for confirmatory work. Schema-level forcing is more robust than relying on filename conventions or operator memory.

**Implementation**: in `src/r5a/contracts.py` (`mode` field) + `scripts/ws1_finalize_run_manifest.py` (CLI gates the mode + the 7 clauses).

## Decision #2 — RunManifest fleet roster fields

**Problem (R2-C3 + Lens A severity #3)**: `docs/DECISION_20260429_llama_addition.md` §3.2 literally requires `fleet_white_box: list[str]` and `fleet_p_predict_eligible: list[str]`. Neither is in the current `RunManifest`. Lens A flagged this as memo binding violation. Lens C C.19 also flagged a related but distinct concern: `quality_gate_thresholds` records *eligible* N (e.g., 14, 12) but the script doesn't validate against *realized* N (which models actually produced traces).

**Resolution**: Option C (refined) — add 2 `eligible` fields to `RunManifest`:
- `fleet_p_predict_eligible: list[str]` (currently 14)
- `fleet_p_logprob_eligible: list[str]` (currently 12)

**Skip** `fleet_white_box` (it's derivable as `fleet_p_logprob_eligible ∪ {Llama models in YAML with access:white_box}`). Memo authors can be retro-corrected via supersession note.

**No realized fields**. Partial-run handling is via *prevention*, not *recording*: decision #1 confirmatory hard-fail clause #6 ("every P_logprob-eligible model has a complete trace parquet") refuses to finalize partial states. Recovery is via `ws1_run_logprob.py` resume + finalizer-rerun, producing a single coherent manifest.

**Rationale highlights**: User correctly observed that "rerun is equivalent to original run" for confirmatory pilots — vendor model fingerprints are captured per request via `RequestFingerprint`, cache_key is content-deterministic, and the finalizer runs once at the end of all reruns producing one manifest. The rare unrecoverable case (vendor sunsets a model mid-experiment) triggers a decision memo and re-pin, not a partial manifest.

**Implementation**: contracts.py field additions + finalizer populates from `fleet.p_predict_eligible_ids()` / `fleet.p_logprob_eligible_ids()` + test contract update.

## Decision #3 — Power sim rename vs MC

**Problem (R2-C4 + Lens B critical #1, #2)**: `scripts/simulate_phase8_power.py` is a closed-form calculator labeled as the §8.8 Monte Carlo simulation. Two distinct issues:
1. **Naming/semantics**: docstring + `--b-outer` flag suggest MC, code is closed-form. `mc_se = sqrt(p(1-p)/B)` is statistical theater on a deterministic estimate.
2. **E_CMMD analysis unit bug**: applies model + family random-intercept SE formula, but plan §8.2/§8.1A defines E_CMMD as fleet-aggregated case-level score with case-cluster bootstrap. Result: 9% main-run power vs Round 1 expected 87-99% — actively misleading 10× error.

**Resolution**: Option A — rename + fix.
- Rename `scripts/simulate_phase8_power.py` → `scripts/planning_power_calculator.py`
- Fix E_CMMD branch to use case-level fleet-aggregated score with case-cluster bootstrap (no model/family random intercepts)
- Remove `mc_se` cosmetic and 95% CI stubs
- Docstring: "this is a closed-form planner for design-time scenario sweep, NOT the §8.8 simulation; for prereg-grade power claims see §8.8 MC simulator (deferred to post-pilot)"
- Plan §8.8: add a "two-tool model" paragraph documenting the closed-form planner vs the future MC simulator, and the timing rationale (MC needs pilot `hat(β)` + `hat(Σ)` to calibrate)
- PENDING.md: add "Phase 8 MC simulation — needed before PREREG_STAGE1, must be calibrated from pilot output"

**Rationale**: real MC simulation requires pilot data (per §8.8: `hat(β)` from pilot estimates, `hat(Σ)` from pilot covariance, eligibility/missingness masks observed in pilot). Doing MC now would be feeding placeholder priors. The closed-form planner remains useful for design-time scenario sweeps if its output unit is correct.

**Implementation**: 1 hr code change + ~30 min docstring/plan/PENDING updates.

## Decision #4 — tokenizer_sha contract

**Problem (Lens C A.11)**: current `_git_blob_sha1` in `scripts/ws1_pin_fleet.py` claims to "match HF cache `blobs/<sha>` filename". This is wrong for LFS-tracked files — HF uses SHA256 for LFS, git-blob SHA1 for non-LFS. Most tokenizer.json files in our fleet (Qwen 7-11 MB, Llama 17 MB, GLM 17 MB) are LFS-tracked.

**Resolution**: Option B — `tokenizer_sha = SHA-256 of tokenizer.json byte content as loaded`.

**Documentation in 3 places**:
- `config/fleet/r5a_fleet.yaml` header comment: "SHA-256 of `tokenizer.json` byte content as resolved at load time. Matches HF cache `blobs/<hash>` filename for LFS-tracked tokenizers but NOT for git-tracked ones; do not use as a cache lookup key."
- `scripts/ws1_pin_fleet.py` `_sha256_file_content` docstring: explain LFS vs non-LFS divergence is intentional; field defined as "content-as-loaded SHA-256", not "cache lookup key"
- `src/r5a/contracts.py` `RunManifest.tokenizer_shas` docstring: "SHA-256 of `tokenizer.json` byte content as loaded by the backend at run time. Used to detect tokenizer drift across runs; not a HF cache filename."

**Rationale**: SHA-256 is robust across LFS/non-LFS, content-addressed, doesn't require API calls (unlike HF Hub ETag option), and pairs cleanly with `hf_commit_sha` (commit pins snapshot, sha256 pins file).

**Implementation**: ~30 min in `ws1_pin_fleet.py` (rename function + update call sites) + 3 docstring updates.

## Decision #5 — `cutoff_observed` full rename

**Problem (Lens E Tier-1 #15 PARTIAL)**: Round 1 SYNTHESIS C5 + Adversarial A4 said "cutoff_observed" linguistically over-claims a training-cutoff measurement; Path E actually measures empirical *familiarity drop horizon*, only equal to cutoff for `vendor_stated` models (currently only Claude + 2 Llama).

**Resolution**: Option A — full rename to `exposure_horizon_observed` across all surfaces.

**Scope**:
- `src/r5a/contracts.py`: `RunManifest.cutoff_observed` → `exposure_horizon_observed`
- `src/r5a/analysis/cutoff_probe.py` → `src/r5a/analysis/exposure_horizon.py` (file rename)
- `CutoffEstimate` → `ExposureHorizonEstimate`; `cutoff_*` fields → `horizon_*`; `detect_cutoff()` → `detect_exposure_horizon()`
- `tests/r5a/test_cutoff_probe.py` → `test_exposure_horizon.py`
- `scripts/ws1_run_logprob.py` CLI flag: `--cutoff-probe` → `--exposure-horizon-probe`; arg `--cutoff-probe-fixture` → `--exposure-horizon-fixture`; `--cutoff-probe-output-dir` → `--exposure-horizon-output-dir`
- `scripts/run_cutoff_probe_analysis.py` → `scripts/run_exposure_horizon_analysis.py`
- `data/pilot/cutoff_probe/` → `data/pilot/exposure_horizon/`
- All decision memos / plans / PENDING / R5A_FROZEN_SHORTLIST term sweep
- Round 1 review files (signed history): supersession banner only, do not rewrite body

**Do NOT rename**:
- Fleet YAML `cutoff_date` + `cutoff_source` fields (these are operator-declared values, vendor_stated cases ARE cutoffs — original name correct)
- `RunManifest.cutoff_date_yaml` (verbatim mirror of YAML value)

**Llama special case**: Path E output for Llama is technically `exposure_horizon_observed` (it's the same measurement); paper Methods has a separate paragraph explaining "for vendor_stated models, this horizon serves as a cutoff recovery calibration check" — the calibration claim is the value, not the field name.

**Rationale highlights (user-stated)**: "AI-assisted projects: misleading names mislead future dev agents more than they mislead human reviewers — confabulation risk in LLM context." This reasoning extends to decision #10 enum rename.

**Implementation**: ~3-4 hr (grep/rename + test rerun + 3 decision memo body updates).

## Decision #6 — Exploratory multiplicity rule

**Problem (Lens E Tier-1 #20 NOT STARTED)**: Confirmatory family (5 estimands × 4 factors = 20 coefficients) goes through Westfall-Young stepdown max-T (FWER α=0.05). The exploratory family rule has not been chosen.

**Resolution**: Option C — mixed strategy, each exploratory family gets its own correction matched to its structure.

**Three rules**:

1. **`E_PCSG_capacity_curve`** (BH-FDR q=0.10):
   - Family size: 2 (Qwen2.5 slope, Qwen3 slope)
   - Tests: the 2 leakage contrasts from decision #9 (β_pre - β_post per family)
   - BH on m=2 is essentially no adjustment (q=0.10 thresholds = {0.05, 0.10})

2. **WS6 mechanistic** (cluster permutation):
   - Family size: ~30 layers × 3 metrics × 12 models ≈ 1080 tests
   - Layer-adjacent test correlation is strong; BH-FDR is overly conservative
   - Cluster permutation is the literature standard (Wang et al. 2025 use it)
   - Implementation: `mne.stats.permutation_cluster_1samp_test` or scipy permutation_test

3. **Reserve estimands** (`E_extract`, `E_ADG`, `E_schema_cont`) — descriptive-only:
   - No multiple comparison correction; report effect size + simultaneous bootstrap CI; no p-values, no significance claims
   - If R5A_FROZEN_SHORTLIST §4 promotion rule fires, the estimand is promoted to confirmatory family (governed by WY then)

**Rationale**: A one-size-fits-all (BH everywhere) would be drowned by WS6's 1080-test family. Descriptive-only everywhere would surrender capacity curve's planned inferential claim and WS6's mechanistic localization claim. Each family's structure motivates a different appropriate method.

**Implementation**: ~2 hr in PREREG_STAGE1 draft (paper planning) — no immediate code work; the analysis scripts implementing each rule come in decisions #9 (capacity curve) + WS6 implementation work (separate workstream).

## Decision #7 — AWQ-vs-fp16 audit (Stage 1.5 + Stage 2.8)

**Problem (R2-U18 + Lens E Tier-1 #13 PARTIAL)**: Round 1 Adversarial A3 (no defense) — AWQ-INT4 vs fp16 cross-precision pooling for E_CTS is unsound; `quant_scheme` label documents but doesn't remove confound. Original plan had a Stage 2.8 audit (Qwen2.5-7B only, post-pilot). User asked: could audit results change AWQ vs bf16 architectural choice? Answer: yes, scenarios 3-4 (catastrophic distortion or size heterogeneity), but post-pilot timing is too late — $40+ AWQ traces already on disk.

**Resolution**: Add Stage 1.5 mini-audit gate **before** Stage 2 full pilot, expand Stage 2.8 conditionally based on gate outcome.

**Stage 1.5 — mini-audit gate (M3 grid)**:
Models × precisions = 5 × 2 = 10 runs:
- Qwen2.5-{1.5B, 7B, 32B} × {AWQ, bf16}
- Qwen3-{4B, 32B} × {AWQ, bf16}

Sample: 60-100 articles per run from cutoff probe set (1-2 months).
Time: ~3 hours GPU. Cost: ~¥24 ≈ $3.3.

**Gate rule**:
```
delta_max = max over audited (model, precision-pair) of |mean(MinK%++(AWQ) - MinK%++(bf16))|
delta_se_max = max of stderr per cell

if delta_max < 0.05 nats AND all delta_se < 0.02:
    → GREEN: proceed Stage 2 with all-AWQ pilot;
             paper reports "audited at gate; no material distortion"

if 0.05 ≤ delta_max < 0.10 nats:
    → YELLOW: proceed Stage 2 with all-AWQ;
             commit to publishing corrected_E_CTS (subtract per-article delta) as primary;
             original AWQ E_CTS supplementary;
             Stage 2.8 expands (see below)

if delta_max ≥ 0.10 nats OR per-model heteroscedasticity (tail variance ratio > 2× over middle):
    → RED: stop pre-pilot; tear down; trigger decision memo
           (options: full bf16 pilot ~$80-120; restrict E_CTS to homogeneous-precision subset; demote E_CTS to exploratory)
```

**Stage 2.8 — full audit, conditional**:

| Gate | Stage 2.8 form | GPU time | Cost |
|---|---|---|---|
| GREEN | Qwen2.5-7B {AWQ, bf16} × 430 pilot cases (paper figure) | ~3 hr | $3.3 |
| YELLOW | All 9 AWQ Qwen models in bf16 × 430 cases (per-article correction) | ~20 hr | ~$22 |
| RED | does not happen (cloud session torn down at Stage 1.5) |

**Budget impact**:
- GREEN: total $40 (within $45 cap)
- YELLOW: total ~$58 (exceeds $45 cap; triggers budget-extension decision memo — design feature, not bug)
- RED: only $5 spent on Stage 1.5 + bring-up before tear down

**Stage placement (cloud plan)**:
```
Stage 0     local
Stage 1     AutoDL bring-up
Stage 1.5   Mini-audit gate (M3, ~2 hr)
            ↓ GREEN/YELLOW
            ↓ RED → tear down + replan
Stage 2     Per-model pilot loop (~10 hr)
Stage 2.5   Path E (~3 hr)
Stage 2.7   Hidden states (~6 hr)
Stage 2.8   Full audit (form per gate; ~3-20 hr)
Stage 3     Local re-derivation
Stage 4     Teardown
```

**Sub-decisions**:
- correction application policy: option (b) — audit script outputs delta_quant table; downstream E_CTS analysis decides whether to apply; both raw and corrected paths reported in paper

**Implementation**:
- `scripts/ws1_quant_calibration_audit.py` (new) — handles both mini-audit input (M3 grid traces) and full audit input (430-case traces); computes per-cell delta_quant + summary; writes `data/pilot/analysis/quant_calibration_<scope>.parquet`
- WS1 plan updates: insert Stage 1.5 + revise Stage 2.8 description for conditional form
- Cost estimates updated in plan §11.2

Time: ~5-6 hr (script + tests + plan doc)

## Decision #8 — Path E negative control

**Problem (R2-U8 + Lens E Tier-1 #14 NOT STARTED)**: Round 1 Adversarial A2 — knee detection could detect Chinese financial regime shift dressed as cutoff. Round 2 Lens B A.11 confirmed: new piecewise-WLS detector has near-zero FPR under iid article noise but ~5% FPR under month-level shocks. Llama differential calibration provides partial defense (9-month differential can't be regime shift since both Llama models see same regime), but doesn't defend the absolute knee position for non-vendor models.

**Resolution**: B mandatory + A conditional.

**B (date-shuffle placebo) — mandatory, 0 GPU**:
- New script `scripts/run_exposure_horizon_placebo.py`
- Reads existing Stage 2.5 traces (12 models × 2160 articles)
- Shuffle `publish_date` across years (preserves monthly seasonality, destroys cutoff signal)
- Re-run `detect_exposure_horizon()` on shuffled data
- 5 replicates (B=5)
- Expected: 0/5 produce accepted horizon (CI > 3 months OR drop CI ≤ 0.05); if any replicate accepts, detector has non-trivial false positive rate
- Paper reports: "0/5 placebo replicates produced accepted exposure horizon"

**A (Chinese non-financial corpus) — conditional**:
Triggers if any of:
1. Llama differential calibration: `|ExposureHorizon(llama-3.1) - ExposureHorizon(llama-3)|` outside [6, 12] months OR CI width > 4 months
2. Placebo (B): >= 1/5 replicate produces accepted horizon
3. PREREG_STAGE1 reviewer requests it

If triggered, separate decision memo decides corpus source (Renmin/Xinhua archive scraping, Wikipedia Chinese, CLUENER-class corpora, Common Crawl Chinese subset). Cost: 5-10 hr corpus engineering + ~$3.5 cloud GPU for non-financial Path E + ~1 hr analysis. Not committed to a specific source now.

**Rationale**: B is free defense against detector over-confidence on the project's own corpus. A is the strong cross-corpus defense but expensive in data engineering; defer to "when needed".

**Implementation**: ~1 hr placebo script + paper-prereg language for the conditional A trigger.

## Decision #9 — Capacity curve formula

**Problem (Lens E Tier-1 #16 NOT STARTED)**: `E_PCSG_capacity_curve` is exploratory (per decision #6 rule: BH-FDR q=0.10 over 2 tests). The model formula was sketched in Round 1 SYNTHESIS U9 but not implemented or pre-registered.

**Resolution**: Option B — mixed model with `family` as fixed effect (only 2 levels — Qwen2.5, Qwen3 — doesn't justify random effect), 3-way interaction.

**Formula**:
```
mean_logprob_ij ~ log2(params)_j * family_j * cutoff_exposure_i
                  + (1 + log2(params)_j | case_id_i)
```
- `i` indexes case (article); `j` indexes model
- `cutoff_exposure_i ∈ {pre, post}`: pre-cutoff (potentially memorizable) vs post-cutoff (BL2 cases, not memorizable)
- `(1 + log2(params) | case_id)`: per-case random intercept and random slope
- `family * log2(params)`: family-specific slopes via fixed-effect interaction (Qwen2.5 != Qwen3 baseline + slope)
- `cutoff_exposure * log2(params)`: pre vs post slope difference (the leakage signal)

**Estimation**: `statsmodels.mixedlm` (avoid R reticulate dependency).

**Inference**: case-cluster bootstrap, B = 2000 replicates.

**Reported quantities**:
- 4 raw slopes (descriptive, Carlini replication):
  - β_qwen2.5_pre, β_qwen2.5_post, β_qwen3_pre, β_qwen3_post
  - Each with 95% CI (BCa preferred)
- 2 leakage contrasts (inferential, the pre-prereg p-values per decision #6):
  - p1 = β_qwen2.5_pre - β_qwen2.5_post
  - p2 = β_qwen3_pre - β_qwen3_post
  - BH-FDR q=0.10 over m=2

**Sub-decisions**:
- Q9a: B = 2000 (Round 1 standard)
- Q9b: report both raw slopes (Carlini replication, supplementary table) and leakage contrasts (main paper claim)

**Implementation**: ~5 hr (`src/r5a/analysis/capacity_curve.py` new module + tests + plan §8.1A formula spec).

## Decision #10 — E_FO sycophancy controls + rename

**Problem (Lens E Tier-1 #12 NOT STARTED)**: Round 1 Adversarial A8 (no defense) — E_FO measures "non-compliance to false outcome" but this could come from memorized truth (intended), instruction-following, truthfulness RLHF, refusal style, OR sycophancy mechanism. Without controls, paper claim "we measured memorization override" is unsupported.

**Resolution**: Level 2 with full enum rename.

**Three components**:

1. **Full rename** (parallel to decision #5):
   - `E_FO` → `E_OR` (counterfactual outcome resistance)
   - `C_FO` → `C_CO` (counterfactual outcome perturbation)
   - `PerturbationVariant.C_FO` → `C_CO` enum identifier
   - Sweep through code, contracts, decision memos, plans, fixtures, R5A_FROZEN_SHORTLIST
   - Same scope discipline as decision #5

2. **BL2 nonmember control via existing 350 post-cutoff cases**:
   - WS3 specification: `C_CO` perturbation applied to all 430 cases (80 pre-cutoff + 350 post-cutoff), not just pre-cutoff
   - Pre-cutoff: model might know real outcome → measures "resistance with truth memory available"
   - Post-cutoff: model cannot know real outcome → measures "resistance baseline (instruction-following / sycophancy / RLHF)"
   - Memorization-attributable signal: `E_OR(pre-cutoff) - E_OR(post-cutoff)`
   - Plan §8.2 adds new estimand model: `E_OR ~ cutoff_exposure + factor + cutoff_exposure:factor + (1|model) + (1|case)`; primary contrast is the pre-post difference

3. **Phase 8 framing variants reserved**:
   - 3 instruction-framing variants ("use only article" / neutral / "user wants confirmation") cost ~$60 + double audit work
   - Pilot stage doesn't include them; PREREG_STAGE2 reserves them as Phase 8 exploration to disentangle sycophancy from instruction-following residual after BL2 has answered the main "is it memorization or not" question

**Rationale**: BL2 already provides the cleanest possible nonmember control — same corpus, same pipeline, just cutoff-side different. Cost-free leverage. Framing variants are second-order disentanglement that can wait. Full enum rename matches decision #5's "avoid future-agent confabulation" reasoning.

**Implementation**: ~6-8 hr (rename + WS3 spec update + plan §8.2 estimand spec + decision memo + R5A_FROZEN_SHORTLIST amendment).

## Decision #11 — WS6 trigger contradiction

**Problem (R2-U18)**: Two same-day decision memos contradict on whether WS6 has a trigger:
- `docs/DECISION_20260429_gate_removal.md` §2.4: "WS6 is unconditional. WS6 is no longer conditional on E_FO clearing a behavioral trigger."
- `docs/DECISION_20260429_llama_addition.md` §2.6: "WS6 mechanistic trigger (over white-box N): N = 12 → ⌊12/2⌋+1 = 7/12. Was 6/10 before Llama; now 7/12 because Llama contributes hidden states."

The Llama memo author copied the threshold-rescaling table format from gate_removal §2.6 without noticing gate_removal §2.4 had eliminated the WS6 trigger entirely.

**Resolution**: gate_removal §2.4 wins. WS6 is unconditional. Drop manifest fields.

**Three cleanup actions**:

1. **`docs/DECISION_20260429_llama_addition.md` §2.6** — replace the WS6 row:
   > WS6 mechanistic analysis is **unconditional** per `docs/DECISION_20260429_gate_removal.md` §2.4. There is no behavioral trigger for WS6 — adding Llama hidden-state extraction (12 white-box) does not introduce or rescale a trigger threshold. (Earlier draft of this memo retained a 7/12 line copied from the threshold-rescaling table; it is superseded.)

2. **`scripts/ws1_finalize_run_manifest.py` `_quality_gate_thresholds()`** — drop both fields:
   - Delete `ws6_mechanistic_n_white_box`
   - Delete `ws6_mechanistic_threshold`
   - Updated test contract: `quality_gate_thresholds` dict only contains the 4 E_extract entries (`e_extract_main_text_*`, `e_extract_confirmatory_*`)

3. **`docs/DECISION_20260427_pcsg_redefinition.md` §2.5** — add supersession note:
   > **Superseded 2026-04-29**: per `docs/DECISION_20260429_gate_removal.md` §2.4, WS6 is now unconditional. The "conditional on E_FO threshold" language in this memo was the original 2026-04-27 design; it no longer applies.

**Rationale**: deleting (not renaming) the manifest fields prevents future agents from confabulating "WS6 has a threshold". If WS6 paper-time analysis wants to make a "majority of white-box models show X" claim, that's a paper-time analysis declaration, not something the manifest pre-commits.

**Implementation**: ~1.5 hr (3 doc edits + manifest field removal + test update).

## Decision #12 — Tier-2 paper-day caveat tracking

**Problem (R2-U17)**: Round 1 SYNTHESIS Tier-2 listed 5 caveats the paper Methods/Discussion must acknowledge (domain scope, capacity curve framing, Qwen-heavy fleet, reproducibility burden, day-precision down-claim). No tracker exists; Round 1 SYNTHESIS would have to be re-read at paper-writing time, which won't happen reliably for a single-operator project.

**Resolution**: Option C — `docs/PAPER_CAVEATS.md` (living document, with current draft language) + PENDING.md one-line index pointer.

**File structure** (initial 5 sections):
1. **Domain scope**: "Our findings characterize LLM training-data leakage in **Chinese financial news**..."
2. **Capacity curve framing**: "Following Carlini et al. (2022), we report capacity curves as a **diagnostic replication**; the new methodological contribution is the cross-cutoff differential PCSG signal..."
3. **Qwen-heavy fleet**: "Confirmatory white-box temporal evidence rests on Qwen2.5/Qwen3 cross-version PCSG and Llama vendor-cutoff calibration; GLM and black-box API fleet provides behavioral corroboration only..."
4. **Reproducibility burden**: "All artifacts (RunManifest, fleet pinning log, hidden-state subset manifest, Docker digest) published; replication requires HF gated-repo access for Llama..."
5. **Month-level horizon precision**: "We report empirical exposure horizons at **month-level granularity** with bootstrap CIs; absolute precision finer than month-level is not claimed. Placebo control (date-shuffled, X/5 replicates produced accepted horizon) and Llama vendor-stated calibration..."

Each section has: source, why-it-matters, draft language, evidence basis, status (`pending` / `drafted in §X` / `resolved`).

**Sub-decisions**:
- Q12a: living document — Round 2 may add caveats (e.g., Lens B A.11 month-level shock vulnerability is a candidate caveat conditioned on placebo + Llama calibration outcomes), pilot results may add more
- Q12b: write current draft language now — paper-time picking from current language is faster than reconstructing from memory
- Q12c: include conditional caveats — caveat #5 explicitly depends on Stage 1.5 audit + B placebo outcomes; record dependency now

**Rationale**: PENDING.md is a one-line index; caveat content needs prose (draft language + evidence). Separate file scales without bloating the index. Single PENDING.md entry preserves discoverability.

**Implementation**: ~1 hr (write the file + add PENDING entry).

# Implementation Breakdown

## Tier-R2-0 — Cloud-Spend Blockers + Bundled Renames (~8-11 hr)

Tier-R2-0 closes the cloud-spend gate on the implementation side. After completion, only user-side actions (HF Meta license, CLS post-2026-02 corpus extraction) remain before WS1 cloud Stage 1.

Bundling renames into Tier-R2-0 because `src/r5a/contracts.py` is heavily modified here anyway; touching the file once for all field changes (additions + renames + deletions) is cleaner than two passes.

### Block A — Contracts + fleet (~1.5-2 hr)

1. `src/r5a/contracts.py`:
   - Add `mode: Literal["confirmatory", "dev"]` field (decision #1)
   - Add `fleet_p_predict_eligible: list[str]`, `fleet_p_logprob_eligible: list[str]` (decision #2)
   - Tighten `pcsg_pair_registry_hash` from `str | None` to `str` (R2-U1)
   - Rename `cutoff_observed: dict[str, date | None]` → `exposure_horizon_observed: dict[str, date | None]` (decision #5)
   - Rename `PerturbationVariant.C_FO` → `C_CO` (decision #10)
   - Drop ws6 fields from default `quality_gate_thresholds` typing (decision #11; the dict still accepts arbitrary str keys but the docstring removes the WS6 examples)
   - Update RunManifest docstring with R2 references

2. `src/r5a/fleet.py`:
   - Extend PCSG validator to reject:
     - duplicate members within a capacity pair (`members: [x, x]`)
     - self-pairs (temporal `early == late`)  (R2-U2)
   - Require non-null `tokenizer_family` and `quant_scheme` for white-box `ModelConfig` entries (R2-U4)

3. `tests/r5a/test_run_manifest_contract.py`:
   - Update `REQUIRED_FIELDS` set (add `mode`, `fleet_p_predict_eligible`, `fleet_p_logprob_eligible`; rename `cutoff_observed` → `exposure_horizon_observed`)
   - Pin `extra_forbidden` error type, not just any `ValidationError` (R2-U12)

4. `tests/r5a/test_fleet_config.py`:
   - Add tests for duplicate-member capacity pair rejection
   - Add tests for self-pair temporal pair rejection
   - Add direct `participates_in_p_predict()` / `participates_in_p_logprob()` predicate tests (R2-U on Lens D #19)

### Block B — Pin fleet hardening (~2-3 hr)

`scripts/ws1_pin_fleet.py`:
1. `_git_blob_sha1` → `_sha256_file_content` (decision #4)
2. Reject unknown `--pin-json` model IDs with `SystemExit` (R2-C5 #8)
3. Validate `--vllm-image-digest` format `^sha256:[0-9a-f]{64}$`; make required for non-`--check` (R2-C5 #7)
4. Patch quoted `<TBD>` (handle `tokenizer_sha: "<TBD>"` form) (R2-C5 #4)
5. Idempotent fleet_version bump — only append `+pinned-<UTC>` if any field actually changed (R2-C5 #5)
6. File locking + atomic rename (write to `<path>.tmp`, fsync, atomic rename to target; same for `.fleet_pinning_log.json`) (R2-C5 #6)
7. Multi-snapshot HF cache: refuse without explicit `--revision` per model (or `--pin-json` disambiguating) (R2-C5 #2)
8. Post-patch validation: assert exact equality of every patched field against the requested pin value (R2-C5 #1)
9. Respect `HF_HUB_CACHE` env var in cache discovery (Lens C A.9)
10. Don't silently delete corrupt pinning log — refuse and require operator action (Lens C silent #3)

### Block C — Finalizer hardening (~1.5-2 hr)

`scripts/ws1_finalize_run_manifest.py`:
1. Read `--traces-dir`; assert exactly one `*__pilot.parquet` per `fleet.p_logprob_eligible_ids()` (decision #1 hard-fail clause #6)
2. Validate cutoff JSON keys against `fleet.p_logprob_eligible_ids()`; fail on extras or missing entries (R2-C2 #2)
3. Reject invalid cutoff date strings as `SystemExit` (don't silently convert to `None`) (R2-C2 #2)
4. Reject empty/partial hidden-state directory (require all 12 models × full 30-case subset; or mode=dev) (R2-C2 #3)
5. Implement decision #1 7-clause hard-fail in confirmatory mode
6. Compute `sampling_config_hash` from `config/pilot_sampling.yaml` (NEW `--sampling-config` arg), not from article manifest (R2-C2 #5)
7. Drop ws6 fields from `_quality_gate_thresholds()` (decision #11)
8. Populate `fleet_p_predict_eligible` / `fleet_p_logprob_eligible` (decision #2)
9. Replace `_hash_strings("\n".join(sorted(items)))` with canonical JSON array hashing (R2-U10)
10. Make `_hidden_state_subset_hash()` hash the frozen subset JSON, not derive from filesystem order (Lens C C.17)
11. `--vllm-image-digest`, `--gpu-dtype`, `--launch-env` required in confirmatory mode (decision #1 + R2-C2 #6)
12. `_git_commit_sha` fails hard (no all-zero fallback) in confirmatory mode (R2-C2 #4)

### Block D — Path E default fix + rename (~30 min)

1. `scripts/run_cutoff_probe_analysis.py` → `scripts/run_exposure_horizon_analysis.py` (decision #5)
2. Default `--traces-dir` → `data/pilot/exposure_horizon/traces/` (R2-C1)
3. Validate analyzed model list against fleet (R2-C1 follow-on)
4. Output JSON includes per-trace SHA256 + probe-set hash (R2-C2 #1)
5. Output field name: rename hard-coded `p_drop_gt_005` → threshold-neutral `p_drop_gt_threshold` (Lens A minor #3)
6. Update CLI flags: `--cutoff-probe` references → `--exposure-horizon-probe`

### Block E — Power calculator rename + bug fix (~1 hr)

1. `scripts/simulate_phase8_power.py` → `scripts/planning_power_calculator.py` (decision #3)
2. Fix E_CMMD branch: replace `_se_with_family_intercepts` with case-cluster bootstrap on case-level fleet-aggregated score (R2-C4 #2)
3. Remove `mc_se` cosmetic fields from output rows (R2-C4 #3)
4. `--b-outer` either remove or actually drive case-cluster bootstrap iterations
5. Update top docstring with two-tool model + post-pilot MC pointer
6. Plan §8.8 add "two-tool model" paragraph
7. PENDING.md add Phase 8 MC simulation entry

### Block F — Tests (~1.5-2 hr)

Per Lens D §B.16-B.20 + suggested outlines, add (full list — implementer should batch):

1. `tests/r5a/test_pin_fleet.py` (new):
   - patch single model leaves others alone
   - reject unknown `--pin-json` model ID
   - `--check` mode does not write
   - patched YAML still validates via `load_fleet`
   - `pcsg_pair_registry_hash()` invariant when only `models:` keys change
   - idempotency on second run with same pins

2. `tests/r5a/test_finalize_run_manifest.py` (new):
   - `--allow-tbd` gate behavior (mode=dev manifest accepted; mode=confirmatory rejects placeholders)
   - quality-gate thresholds against actual fleet (assert 5/14, 8/14; no WS6 entries)
   - JSON roundtrip preservation
   - hidden-state subset hash on fixture directory

3. `tests/r5a/test_planning_power_calculator.py` (new):
   - PCSG SE anchor: `_se_pcsg_pair(2048, 2, 0.98, 4.5) ≈ 0.071`
   - CMMD SE shape (monotonicity, inflation behavior)
   - WY power anchor points

4. `tests/r5a/test_logprob_metrics.py` (extend or new):
   - `LogProbTrace` validator: rejects `prefix_token_count > article_token_count`
   - `LogProbTrace` validator: rejects `top_alternative_logprobs` outer-length mismatch

5. `tests/r5a/test_fleet_config.py` (extend):
   - PCSG hash payload coverage test (uses `PCSGPair.model_fields` to ensure hash stays sensitive to all fields) (R2-U11)
   - Tighten role-shape rejection tests to assert specific error messages

6. `tests/r5a/test_exposure_horizon.py` (renamed from test_cutoff_probe.py):
   - Tighten `test_detect_cutoff_rejects_high_noise_wide_ci` to actually isolate "wide CI despite true step" (currently rejects with wrong-direction point fit) (R2-U13)
   - Add CI-bound exact-value test (Lens D suggested outline)
   - Add bootstrap-invalid-replicate guard test
   - Add aggregator-mean-vs-median test
   - Add min_side exact-boundary test

### Block G — Validation (~30 min)

- `pytest tests/r5a -q` (all green)
- `python scripts/smoke_phase7.py --check-config` (clean output, fleet 12+4 / 14 P_predict / 12 P_logprob / 2 confirmatory PCSG pairs)
- One-line manual check: `--exposure-horizon-probe` flag parses + `--allow-tbd` mode field present in manifest

### Tier-R2-0 commit message structure

```
R2 Tier-0 patch: cloud-spend gate closure + bundled renames

Sources: refine-logs/reviews/R5A_DESIGN_REVIEW_R2_20260429/
  - SYNTHESIS.md (12 cross-lens findings R2-C1..R2-C6 + R2-U1..R2-U18)
  - DECISIONS.md (12 user-confirmed resolutions + Tier-R2-0/R2-1 breakdown)

Decisions implemented (full list and rationale in DECISIONS.md):
  #1 mode field + 7-clause confirmatory hard-fail
  #2 2 eligible roster fields; partial-run via rerun
  #3 power calc rename + E_CMMD case-cluster bootstrap fix
  #4 tokenizer_sha = SHA-256 of file content
  #5 cutoff_observed → exposure_horizon_observed (full rename)
  #10 enum rename E_FO→E_OR, C_FO→C_CO (contracts side; doc + WS3 spec
       in Tier-R2-1)
  #11 drop ws6 fields from quality_gate_thresholds; doc cleanup in
       Tier-R2-1

Files: contracts, fleet, ws1_pin_fleet, ws1_finalize_run_manifest,
ws1_run_logprob, run_exposure_horizon_analysis, planning_power_calculator,
test_*

After this commit lands, cloud-spend gate is closed on the
implementation side; only HF Meta license click-through and CLS
post-2026-02 corpus extraction remain (user-side, tracked in
PENDING.md).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

## Tier-R2-1 — Doc Cleanup + Tier-1 Implementation (~12-15 hr)

Tier-R2-1 doesn't block cloud spend; can run in parallel during cloud Stage 1+ or after. Recommended order: G (doc sweep) + I (PAPER_CAVEATS) light items first, then H (new scripts) + J (Tier-1 docs).

### Block G — Doc sweep (~3-4 hr)

1. `PENDING.md`:
   - Move `WS1 — LogProbTrace contract closure` to Recently closed (fields landed in 208ef06)
   - Update `WS1 — model/tokenizer/image provenance pinning` to "12 P_logprob-eligible white-box entries"
   - Add Tier-1 entries for: #12 sycophancy controls (decision #10 spec), #13 audit script (decision #7), #14 negative-control corpus (decision #8 conditional A), #15 cutoff rename status (now decision #5), #16 capacity-curve spec (decision #9), #20 multiplicity rule (decision #6), Phase 8 MC simulation (decision #3)
   - Add `docs/PAPER_CAVEATS.md` index pointer (decision #12)

2. `R5A_FROZEN_SHORTLIST.md` (under refine-logs/reviews/R5A_STEP2/):
   - Amendments header: add `docs/DECISION_20260429_llama_addition.md`
   - Body: update `E_PCSG` definition to two confirmatory temporal pairs (Qwen + Llama)
   - Body: P_logprob roster 10 → 12 white-box (or describe as derivable from fleet YAML)
   - Body: `E_FO` / `C_FO` → `E_OR` / `C_CO` (decision #10)

3. `plans/phase7-pilot-implementation.md`:
   - Sweep `pilot_100_cases` / `N=100` → `pilot_430_cases` / `N=430` references (lines flagged in Lens E)
   - Sweep `S16a/S16b/S12` residue (§7.2, §8.8, §13 risk register, §14.2 banner)
   - Sweep "9-model" / "5 white-box" residue (lines flagged in Lens E)
   - §7.1A demotion-risk language: explicitly state retired
   - §8.1A: add capacity curve formula spec from decision #9
   - §8.2: add `E_OR` analysis spec from decision #10
   - §8.8: add two-tool model paragraph (closed-form planner vs MC simulator)
   - Plan §10.4: update field types to match contracts.py exactly (e.g., `cutoff_observed: dict[str, date | None]` was missing the `| None`)

4. `plans/ws1-cloud-execution.md`:
   - Insert Stage 1.5 mini-audit gate description (decision #7)
   - Update Stage 2.7 hidden-state count 10 → 12 white-box
   - Revise Stage 2.8 description: GREEN/YELLOW/RED conditional forms
   - Update Stage 3 to consume both AWQ and (conditionally) bf16 traces
   - Update budget cap and per-stage cost lines
   - Sign-off checklist: add Stage 1.5 gate result, mini-audit fixture commit, conditional Stage 2.8 outcome

5. `refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md` and `docs/TIMELINE.md`:
   - Add 2026-04-29 supersession banner referencing the three Tier-0 decision memos + R2 SYNTHESIS

6. `docs/DECISION_20260427_pcsg_redefinition.md`:
   - Front matter: add `related_docs` cross-links to `gate_removal` and `llama_addition`
   - §2.5 add supersession note (decision #11)
   - §2.4: stale `1,440` references already mostly fixed; spot-check
   - Stale "10 white-box" residue in §3.2 / §3.3

7. `docs/DECISION_20260429_gate_removal.md`:
   - Front matter: add `related_docs` cross-link to `llama_addition`
   - §2.6: stale "future Llama decision" language → "Llama added 2026-04-29; see llama_addition memo"
   - §3.2: stale "10 white-box" → "12 white-box per llama_addition §3.4"

8. `docs/DECISION_20260429_llama_addition.md`:
   - §2.6: rewrite per decision #11 (no WS6 trigger)

### Block H — New scripts (~5-6 hr)

1. `scripts/ws1_quant_calibration_audit.py` (decision #7):
   - Read AWQ traces + bf16 traces (M3 mini-audit grid OR full Stage 2.8 grid)
   - Compute per-cell `delta_quant = MinK%++(AWQ) - MinK%++(bf16)`
   - Output `data/pilot/analysis/quant_calibration_<scope>.parquet` with per-article rows
   - Implement gate decision rule (GREEN/YELLOW/RED with thresholds)
   - Implement correction rule (subtract delta if YELLOW)
   - CLI: `--mode {gate, full}`, `--awq-traces`, `--bf16-traces`, `--output`
   - Tests: synthetic AWQ + bf16 input, verify delta + gate logic

2. `scripts/run_exposure_horizon_placebo.py` (decision #8 B):
   - Read existing Stage 2.5 traces (12 models × 2160 articles)
   - 5 replicates: shuffle `publish_date` across years, re-run `detect_exposure_horizon()`
   - Report: per-replicate accept/reject + summary fraction
   - Output: `data/pilot/analysis/exposure_horizon_placebo.json`
   - Tests: synthetic shuffled fixtures, verify rejection rate

3. `src/r5a/analysis/capacity_curve.py` (decision #9):
   - Mixed model: `mean_logprob ~ log2(params) * family * cutoff_exposure + (1 + log2(params) | case_id)`
   - Use `statsmodels.mixedlm`
   - Case-cluster bootstrap (B=2000): resample case_ids with replacement, refit, extract slope contrasts
   - Output: 4 raw slopes + 2 leakage contrasts, each with 95% BCa CI
   - Caller in `scripts/run_capacity_curve_analysis.py`
   - Tests: synthetic data with known slope, verify recovery

### Block I — PAPER_CAVEATS.md draft (~1 hr)

Create `docs/PAPER_CAVEATS.md` with the 5 sections per decision #12 spec. Include current draft language for each, source attribution, evidence pointers, and `Status: pending`.

### Block J — Tier-1 doc items (~2-3 hr)

1. WS3 specification update (decision #10):
   - `plans/phase7-pilot-implementation.md` §5.4 (or wherever WS3 is specified)
   - Add: `C_CO` perturbation applied to BL2 350 post-cutoff cases as nonmember control
   - Add: audit protocol extends to nonmember cases (same kappa requirements)

2. PREREG_STAGE1 multiplicity rule writeup (decision #6):
   - New file or section in plan §8.2/§8.8
   - Three rules: capacity curve BH-FDR q=0.10; WS6 cluster permutation; reserves descriptive-only with promotion
   - Each rule cites its literature anchor (BH 1995; permutation Maris-Oostenveld 2007 / Wang 2025; promotion R5A_FROZEN_SHORTLIST §4)

3. WS6 reframe (Tier-1 #12 residue):
   - Plan §5.5 (WS6 spec) language: "memorization localization" → "discriminative mechanism analysis: memorization vs sycophancy"
   - Decision memos: add note that WS6 framework accommodates both memorization and sycophancy mechanism interpretations of hidden-state evidence

# State-of-the-World Summary

After Tier-R2-0 + R2-1 land:

- ✅ Cloud-spend gate closed (implementation side)
- ✅ All 6 Round 2 cross-lens convergent issues addressed
- ✅ All 18 Round 2 single-lens findings resolved (most via Tier-R2-0; some Tier-R2-1)
- ✅ All 9 outstanding Round 1 Tier-1 items addressed (#12-#20)
- ✅ Decision memo cross-references coherent
- ✅ Doc surface aligned with split-tier 16/12/14 fleet
- ✅ PAPER_CAVEATS.md exists for paper-day handoff
- ⏳ Awaits user-side actions: HF Meta license click-through + CLS post-2026-02 corpus extraction (PENDING.md tracks both)
- ⏳ After user actions complete, WS1 cloud Stage 0 commit → Stage 1 instance provisioning → Stage 1.5 gate → Stage 2 pilot

The deferred items (post-pilot work, not blocking pre-registration):
- Phase 8 MC simulation implementation (decision #3) — requires pilot data
- Capacity curve analysis on real pilot data (decision #9) — implementation exists post Tier-R2-1, runs on pilot output
- Stage 2.8 expansion if YELLOW gate (decision #7) — runs in cloud, not before
- Path E negative-control corpus A (decision #8) — only if conditional triggers
- Phase 8 framing variants (decision #10 Level 3) — Phase 8 only

# Notes for the Implementation Planner

1. **Treat decisions as fixed inputs**. All 12 are user-confirmed. Plan against the resolutions, not the original options.

2. **Bundling philosophy**: Tier-R2-0 deliberately bundles renames (decisions #5, #10) with the contracts hardening (decisions #1, #2, #11) because `src/r5a/contracts.py` is heavily modified there. Two passes would be wasteful.

3. **Single-operator constraint**: project is single-operator. The plan should be executable as a sequence by one person, not parallelized work for a team. Block A → B → C → ... ordering matters.

4. **Existing test structure**: tests sit at `tests/r5a/test_*.py`; new tests should follow that convention. `conftest.py` at repo root provides sys.path setup; new test files inherit it automatically.

5. **Codex MCP usage in implementation**: per project CLAUDE.md, Codex MCP is for *thinking* (design, review, analysis), not *executing* (writing files, running commands). Tier-R2-0 is mostly mechanical implementation work; Codex is unlikely to be needed. If a sub-task does need design help (e.g., capacity curve mixed model formulation in `src/r5a/analysis/capacity_curve.py`), Codex MCP with `xhigh` reasoning is appropriate.

6. **Watchdog awareness**: sub-agents have a hard 600s watchdog. Tier-R2-0 blocks A through F should each fit in well under 600s of model time when delegated. Tier-R2-1 blocks G and H involve multiple files and may exceed; consider whether to keep them in main thread vs delegate piecewise.

7. **Commit cadence**:
   - Tier-R2-0: one consolidated commit at the end (after all 6 blocks + validation pass)
   - Tier-R2-1: separate commits per block (G, H, I, J) — these are independent enough that bundling them obscures attribution

8. **Test-first vs test-last**: for the new scripts in Tier-R2-1 H, write tests alongside implementation (the Codex Lens D suggested outlines are detailed enough that they can drive TDD). For Tier-R2-0 hardening, tests validate the hardening — write them after the code change.

9. **Risk surface**: highest-risk-of-regression areas are
   - finalizer hardening (Block C) — many gates added, easy to over-restrict
   - pin_fleet hardening (Block B) — file locking + atomic rename + scalar serialization is fiddly
   - Path E rename (Block D + scattered) — touches CLI, directory, file names; integration test should explicitly verify end-to-end run pattern after rename

10. **Verification command**: after Tier-R2-0 lands, the user expects this exact verification:
    ```bash
    pytest tests/r5a -q                          # all green
    python scripts/smoke_phase7.py --check-config  # clean fleet report
    python scripts/ws1_run_logprob.py --help     # --exposure-horizon-probe flag present
    ```
