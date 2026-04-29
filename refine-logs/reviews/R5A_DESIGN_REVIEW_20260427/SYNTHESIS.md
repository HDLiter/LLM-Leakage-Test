---
title: R5A Design Review (Round 1) — Cross-Lens Synthesis
date: 2026-04-27
review_id: R5A_DESIGN_REVIEW_20260427
inputs:
  - construct_validity_lens.md (Codex thread 019dcf1b-512a, 7905 B)
  - statistical_power_lens.md (Codex thread 019dcf1b-ea5e, 8561 B)
  - adversarial_reviewer_lens.md (Codex thread 019dcf1c-7413, 10330 B)
  - operational_validity_lens.md (Codex thread 019dcf1d-13b8, 12883 B)
  - plan_doc_coherence_lens.md (Codex thread 019dcf1d-ecf1, 7412 B)
status: Round 1 complete — pending user confirmation to launch Round 2 code review
---

# R5A Design Review — Round 1 Synthesis

This synthesis merges 5 parallel Codex MCP lens reviews of the R5A
benchmark following the 2026-04-27 PCSG redefinition + fleet expansion
(5 → 10 white-box). Each lens was an independent Codex `xhigh` reasoning
call; no lens saw any other lens.

## 1. Per-Lens Verdicts

| Lens | Codex verdict on overall design |
|---|---|
| **Construct Validity** | Partially sound. E_PCSG, capacity curve, Path E, C_FO are each *"partially sound"*; AWQ-vs-fp16 cross-family E_CTS pooling is *"unsound for raw pooled fleet-level"*. 3 load-bearing assumptions need pre-registration defenses. |
| **Statistical Power** | Mixed. Family-size of 20 still correct; PCSG eligibility actually ~98% (better than feared); but **§8.8 power sim still says N_model=9** (wrong post-expansion); WS6 denominator is `6/10` not `5/9`; **BL2 TOST at n=20 is mathematically impossible**. |
| **Adversarial Reviewer** | Reject-leaning if submitted as-is. 3 attacks have *no defense* (A3 quantization pooling, A5 day-precision, A8 sycophancy). 4 attacks have *partial defense* (A1, A2, A7, A9, A10). Top-3 paper-killers: A1 PCSG cross-version, A2 Path E knee artifact, A8 C_FO ↔ sycophancy. |
| **Operational Validity** | Multiple block-cloud-spend issues. No fleet-pin writer; RunManifest missing 4 fields from DECISION §3.2; no Path E → RunManifest joiner; stale `1,440` references; CLS corpus disclosure unresolved. |
| **Plan-Doc Coherence** | 12 inconsistencies, mostly **must-fix-before-prereg**. RunManifest is a code-doc-decision triple miss. Quality-gate denominator should be `ceil(5/9 · N)` = `8/14`, not fixed `5`. E_PCSG_capacity_curve has zero analysis-spec coverage. |

**One-line bottom line**: Round 1 surfaces issues that **block cloud spend until fixed** (provenance pinning, RunManifest closure, Path E knee detector, BL2 TOST), and a separate set that must close before pre-registration (denominator policy, capacity-curve spec, sycophancy controls, cross-version PCSG defense). Cloud GO is not yet defensible.

---

## 2. Cross-Lens Convergent Critical Issues

These are issues flagged by ≥2 lenses, and treated as Round 1's primary findings.

### C1. Path E knee detection method is too weak to anchor confirmatory analysis
**Flagged by:** Construct (§3), Statistical (§3), Adversarial (A2), Operational (§6)
- Construct: month-vs-Min-K knee may be Chinese news regime / topic / template drift, not training-cutoff.
- Statistical: `min_drop_magnitude=0.05` threshold has **21-59% false-positive rate** under realistic noise; ±1-month localization only 20-47%; cannot enter §8.2 as a "known" covariate.
- Adversarial A2: "Knee detection is just financial-cycle detection dressed up as cutoff inference" — partial defense.
- Operational: Path E currently uses `--smoke` flag and writes to smoke-trace path; downstream mixed model has no joiner from `cutoff_observed.json` into RunManifest.

**Resolution path:**
1. Replace threshold detection with **piecewise linear / change-in-level WLS regression with grid-searched knee + case-bootstrap CI** (Statistical §3 sketch).
2. Accept `cutoff_observed` only if CI width ≤ 3 months AND lower CI for drop > 0.05; otherwise mark cutoff uncertain and simulate exposure misclassification.
3. Add **topic/category/source/template/numeric-density covariates** and require knee to persist within matched topic strata (Construct §3).
4. Add **negative-control corpus** (matched Chinese non-financial news from same months, OR topic-shuffled placebo knee) to falsify regime-shift attack (Adversarial A2).
5. Implement `scripts/ws1_finalize_run_manifest.py` joining Path E output into RunManifest (Operational §6).

**Severity:** **block-cloud-spend** (cannot run confirmatory mixed model with current detector).

---

### C2. PCSG cross-version is conflated with Qwen2.5 → Qwen3 recipe drift
**Flagged by:** Construct (§1), Adversarial (A1), Statistical (§5 indirectly via pair-count reduction)
- Construct: token alignment ≠ causal attribution. Design admits PCSG also reflects pretraining-recipe / data-composition drift.
- Adversarial A1 ("most threatening attack"): "A higher logprob on 2024 CLS articles could mean Qwen3 is a better Chinese financial-news model, not Qwen3 saw the article." Partial defense only.
- Statistical: 1-pair design vs original 2-pair gives SE inflation **1.41×** (with 98% eligibility); main-run β₃ interaction power drops to 20-86% depending on effect size.

**Resolution path:**
1. Add a **second confirmatory-quality temporal pair**: ideally Llama-3-8B vs Llama-3.1-8B (vendor-stated 9-month gap, same tokenizer/size/density). Acknowledged Chinese-coverage tradeoff per OSS landscape scan.
2. If Llama not feasible, add **Qwen2-7B vs Qwen2.5-7B bridge** with empirical cutoff probe verifying the gap.
3. Pre-register **DiD calibration**: common-pre-cutoff articles → Qwen3-vs-Qwen2.5 baseline fluency; between-cutoff articles → excess familiarity; post-cutoff BL2 → near zero.
4. State E_PCSG explicitly as "Qwen cross-version exposure-correlated contrast", not "causal cutoff estimator". Make causal language conditional on same-cutoff falsification ratio < 0.5 (per existing §8.6A).

**Severity:** **fix-before-pre-registration** (cloud run can produce traces; analysis interpretation must be locked down).

---

### C3. AWQ-INT4 vs fp16 cross-family E_CTS pooling is unsound
**Flagged by:** Construct (§5), Adversarial (A3 — *"no defense"*)
- Construct: Min-K%++ is a bottom-tail statistic; AWQ perturbs the tail non-uniformly; `quant_scheme` field labels but doesn't remove the bias. AWQ paper shows ~0.02 nats/token PPL shifts on average; tail amplification unmeasured on R5A.
- Adversarial A3: "GLM's fp16 scores and Qwen's INT4 scores are not on the same measurement scale. A `quant_scheme` label documents the confound but does not remove it."

**Resolution path:**
1. **Do not pool raw E_CTS across AWQ and fp16** as a cutoff estimand. Calibrate within model.
2. Include **model random effects** in the E_CTS mixed model (already in §8.2 form, but interpretation must reflect this).
3. Run **AWQ-vs-fp16 rescoring audit** on a stratified Qwen subset (rescore Qwen2.5-7B in fp16/bf16 vs AWQ on the R5A corpus) to estimate `delta_min_k = AWQ - fp16` directly.
4. Optionally restrict confirmatory CTS to quantization-homogeneous Qwen models; report GLM separately.

**Severity:** **fix-before-pre-registration** (otherwise Adversarial A3 is unanswered).

---

### C4. C_FO behavioral override is conflated with sycophancy / instruction-following
**Flagged by:** Construct (§4), Adversarial (A8 — *"no defense"*)
- Construct: E_FO measures "non-compliance to visible false outcome" — can arise from memorized truth, instruction-following, truthfulness tuning, refusal style, OR sycophancy. WS6 cites Wang et al. 2025, but Wang is *sycophancy mechanism*; importing it does not isolate memorization.
- Adversarial A8: "If the model resists, that may be truthfulness prior, calibration, or refusal — no control separates memory from sycophancy."

**Resolution path:**
1. Add **nonmember C_FO controls**: post-cutoff events, fabricated CLS-style articles with no real-world outcome, low-salience events.
2. Add **instruction-framing variation**: "use only the article" vs neutral vs user-opinion framing — estimates sycophancy/instruction-following susceptibility separately from cutoff exposure.
3. **Rename E_FO** as "counterfactual outcome resistance" (not "memorization override").
4. **Reframe WS6** as exploratory discriminative analysis (memorization vs sycophancy mechanism), not "memorization localization". Update DECISION_20260427 §2.5 and the WS6 PREREG_STAGE2 prediction language accordingly.

**Severity:** **fix-before-pre-registration**.

---

### C5. Cutoff provenance is mostly operator-asserted; paper claims must be honest
**Flagged by:** Construct (§3 silent assumption), Adversarial (A4 — partial defense), Operational (§1)
- Only Claude Sonnet 4.6 has `vendor_stated`. 13/14 models are `community_paraphrase` or `operator_inferred`.
- Adversarial A4: circularity risk (Path E "validates" the experimenter's own guessed timestamps).
- Operational §1: needs explicit Methods sentence.

**Resolution path:**
1. Adopt Operational §1's Methods sentence verbatim or close (already drafted by Codex).
2. Rename `cutoff_observed` → `exposure_horizon_observed` (Adversarial A4 suggestion); reserve "vendor cutoff recovery" language for Claude only.
3. Publish a `cutoff_source` table in §Methods.
4. Treat Path E output as **empirical familiarity horizon**, not training cutoff.

**Severity:** **fix-before-pre-registration**.

---

### C6. WS6 / E_FO quality-gate denominator is inconsistent across docs
**Flagged by:** Statistical (§4), Plan-Doc Coherence (§1)
- Statistical: WS6 needs hidden states → white-box only → denominator = 10 → threshold = `6/10` (preserves the original 55.6% rate). Black-box can't contribute.
- Coherence: scalable rule `ceil(5/9 · N)`. For E_FO behavioral (14-eligible fleet) → `8/14`. For WS6 mechanistic (10 white-box) → `6/10`. R5A_FROZEN_SHORTLIST §2/§3, plan §13, DECISION §2.5, PENDING.md all currently disagree.

**Resolution path:**
- **Two denominators, two gates.** Behavioral E_FO/E_NoOp gate condition 3 = `ceil(5/9·14) = 8/14` (because P_predict runs on all 14 models). WS6 mechanistic trigger = `ceil(5/9·10) = 6/10` (because hidden-state extraction is white-box only). Document the distinction explicitly.
- Update: R5A_FROZEN_SHORTLIST §2 (gate condition 3), §3 (E_FO_mech), §4 (E_extract reserve thresholds — also use `ceil(...·14)`), plan §7.1 quality-gate table, plan §13 item 6, DECISION_20260427 §2.5, PENDING.md WS6 entry (currently says wrong `5/14`).

**Severity:** **must-fix-before-prereg**.

---

### C7. RunManifest schema is a code-doc-decision triple miss
**Flagged by:** Operational (§5), Plan-Doc Coherence (§6, §7)
Both lenses independently confirm `src/r5a/contracts.py RunManifest` is missing all four fields DECISION_20260427 §3.2 requires:
- `cutoff_observed: dict[str, date]`
- `cutoff_date_yaml: dict[str, date]`
- `quant_scheme: dict[str, str]`
- `pcsg_pair_registry_hash: str`

Plus, plan §10.4 RunManifest field list does not list any of them. Plus §10.1 operational provenance fields (tokenizer SHAs, vLLM image tag/digest, GPU dtype, launch env) also missing from Pydantic.

**Resolution path:**
1. Update `src/r5a/contracts.py RunManifest` to include all 4 + §10.1 operational fields.
2. Update plan §10.4 enumerated list to match.
3. Add `tests/r5a/test_run_manifest_contract.py` asserting field-set coverage AND `extra="forbid"`.
4. Compute `pcsg_pair_registry_hash` from canonicalized `pcsg_pairs` block, not whole-YAML hash.

**Severity:** **block-cloud-spend** (a confirmatory run without these fields is non-reproducible).

---

### C8. Stale fleet-count references throughout plan + signed memo
**Flagged by:** Operational (§9), Plan-Doc Coherence (§8, §10, §11, §12)
- Plan §1 scope, §5.2 deliverables, §5.2 exit, §6.4, §8.1A/§8.2 estimand units, §11.2 runtime estimates, §13 exit-gate item 3, §14.2 YAML example all still say "5 white-box / 9-model".
- WS1 plan sign-off says "5 models" trace failure rate.
- DECISION_20260426 interface memo (signed) lists old 5+4 fleet + old PCSG pairs — needs supersession banner.
- PENDING.md still has `1,440` Path E count and wrong `5/14` WS6 denominator.

**Resolution path:** systematic find-and-replace pass before pre-registration, with explicit superseded-text banners on signed historical memos (don't rewrite signed history).

**Severity:** **must-fix-before-prereg**.

---

## 3. Single-Lens Findings (Important But Not Convergent)

| ID | Lens | Finding | Severity |
|---|---|---|---|
| U1 | Statistical §7 | **BL2 TOST at n_post=20 is mathematically impossible** to satisfy. Even at true effect = 0, P(95% CI ⊂ ±0.15) ≈ 0%. Need ≥350 post-cutoff cases for 60% TOST power, ≥700 for 96%. | **block** Phase 8 automatic GO |
| U2 | Statistical §1 | Plan §8.8 power simulation still says `N_model=9`; needs rewrite for 14/10/1-pair design with PCSG eligibility ~98% and model-family random intercepts. | block-cloud-spend (sim only, not GPU) |
| U3 | Statistical §2 | E_PCSG_capacity_curve OLS at 4-5 model points: required slope for p<0.05 is 0.32 (Qwen2.5) / 0.70 (Qwen3) logprob units per doubling — **descriptive only at pilot**. | ship-with-caveat |
| U4 | Statistical §6 | Need separate exploratory family multiplicity rule: BH-FDR q=0.10 OR descriptive-only effect sizes. | ship-with-caveat |
| U5 | Operational §3 | Hidden-state storage estimate **25-100 GB** (vs 20 GB plan estimate) for 256-1k tokens/article. Per-trace `.safetensors` is OK; package as `.tar.zst` per model + SHA256 manifest for transfer. | fix-before-paper |
| U6 | Operational §3 | WS6 hidden-state extraction is **offline_hf only** in CLI; Stage 2 runs are vLLM. Path E + main pilot would not produce hidden states. | block-cloud-spend if WS6 prep mandatory |
| U7 | Operational §6 | Path E currently uses `--smoke` flag → output files named as smoke traces, not separate Path E run. | block-cloud-spend |
| U8 | Operational §8 | CLS corpus redistribution / Data Availability disclosure unresolved. Probe set is 2.48 MB but copyrighted. | fix-before-prereg (disclosure) |
| U9 | Coherence §3 | E_PCSG_capacity_curve has **zero analysis spec** in plan §8.1A/§8.2. Codex sketched: `mean_logprob ~ log2(params) * cutoff_exposure + family + family:log2(params) + (1+log2(params)|case_id)`, family-specific slopes via case-cluster bootstrap. | must-fix-before-prereg |
| U10 | Coherence §4 | Plan §13 exit gate omits any WS6 condition. Add as **conditional non-blocking gate**: "if triggered, hidden-state coverage verified; else explicitly deferred in go/no-go memo". | must-fix-before-prereg |
| U11 | Coherence §5 | `pcsg_pairs` registry has no FleetConfig validator — `early`/`late`/`members` references not checked against `models:` keys. | must-fix-before-prereg |
| U12 | Adversarial A6 | Capacity curve novelty ≈ 0 — Carlini scaling is established. Frame as diagnostic replication, not contribution. | concedable caveat |
| U13 | Adversarial A7 | Domain-lock to Chinese financial news. Title/abstract must scope. | concedable caveat |
| U14 | Adversarial A9 | Fleet 71% Qwen → split claims into "Qwen white-box temporal evidence" vs "black-box behavioral corroboration". | concedable caveat |
| U15 | Adversarial A5 | 60 articles/month cannot give day-level precision. Down-claim to month-level horizons OR add adaptive dense resampling around candidate knees. | fix-before-prereg |

---

## 4. Methodology Decision Table

What needs a **decision now** (before Round 2 / cloud spend) vs what can land in pre-registration:

| Item | Decide now (block cloud) | Decide at prereg | Concede in paper |
|---|:---:|:---:|:---:|
| Path E knee detector method | ✓ | | |
| RunManifest schema closure | ✓ | | |
| WS1 fleet-pin writer | ✓ | | |
| Path E → RunManifest integration | ✓ | | |
| Path E `--smoke` flag fix | ✓ | | |
| BL2 TOST n_post fix or rule change | ✓ | | |
| Quality-gate denominator policy | ✓ | | |
| WS6 hidden-state CLI path (vLLM vs offline_hf) | ✓ | | |
| Add 2nd PCSG temporal pair | | ✓ | |
| C_FO sycophancy controls + rename | | ✓ | |
| AWQ-vs-fp16 rescoring audit | | ✓ | |
| Path E negative-control corpus | | ✓ | |
| Cutoff Methods disclosure sentence | | ✓ | |
| Capacity-curve descriptive framing | | ✓ | |
| Exploratory multiplicity rule | | ✓ | |
| Stale 5-white-box references | | ✓ | |
| WS6 conditional exit-gate item | | ✓ | |
| Fleet Qwen-heavy claim scoping | | | ✓ |
| Domain-lock to Chinese fin-news | | | ✓ |
| Capacity-curve "no novelty" framing | | | ✓ |
| Hidden-state reproducibility burden | | | ✓ (publish manifests) |

---

## 5. Prioritized Remediation Checklist

### Tier 0 — BLOCK CLOUD SPEND (must complete before any GPU rental)

1. **[Code]** `src/r5a/contracts.py` — extend `RunManifest` with `cutoff_observed`, `cutoff_date_yaml`, `quant_scheme`, `pcsg_pair_registry_hash`, plus tokenizer SHA / vLLM image digest / GPU dtype / launch env from §10.1. Add `tests/r5a/test_run_manifest_contract.py`. **(Op#5, Coh#6/7)**

2. **[Code]** `scripts/ws1_pin_fleet.py` — automated writer that resolves HF model commit, tokenizer file hashes, Docker digest, quant scheme, launch args; writes pinned fleet copy + RunManifest seed. Extend `_check_pinning_for_pilot` in `ws1_run_logprob.py` to reject any `<TBD>` and require `--vllm-image-digest`. **(Op#2)**

3. **[Code]** `src/r5a/analysis/cutoff_probe.py` — replace threshold detection with piecewise WLS + case-bootstrap CI per Statistical §3 sketch. Reject `cutoff_observed` if CI width > 3 months. **(C1, Stats#3)**

4. **[Code]** `scripts/ws1_finalize_run_manifest.py` — joins pinned fleet + main traces + Path E output + `pcsg_pairs` hash + Docker digest + artifact hashes into one RunManifest. **(Op#6)**

5. **[Code]** Fix Path E to write to a distinct `data/pilot/cutoff_probe/traces/` path (not via `--smoke`). Either add `--cutoff-probe` mode to `ws1_run_logprob.py` or create a dedicated `scripts/ws1_run_cutoff_probe.py`. **(Op#7)**

6. **[Code]** `src/r5a/fleet.py` — validate `pcsg_pairs` referential integrity (every `early`/`late`/`members` resolves to `models:` key; pair ids unique; white-box/P_logprob eligibility). Add `tests/r5a/test_fleet_config.py`. **(Coh#5)**

7. **[Decision]** Quality-gate denominator policy: adopt `ceil(5/9 · N)` rule. Behavioral E_FO/E_NoOp use `8/14`; WS6 mechanistic uses `6/10`. Update R5A_FROZEN_SHORTLIST §2/§3/§4, plan §7.1/§13, DECISION_20260427 §2.5, PENDING.md. **(Stats#4, Coh#1)**

8. **[Decision]** WS6 hidden-state CLI path. Either: (a) add hidden-state hook to vLLM backend, OR (b) run a separate offline_hf pass on the 30-article subset post-pilot. Pick one and document GPU cost delta. **(Op#3)**

9. **[Decision/Code]** BL2 rule. Either: (a) increase `n_post` to ≥350 (likely needs corpus expansion), OR (b) rewrite the §13 GO criterion as a two-stage rule (n=20 for falsification screen + adaptive expansion if `|d_hat| ≤ 0.10`), OR (c) widen SESOI and explicitly defend it. As-written, automatic GO is mathematically impossible. **(Stats#7)**

10. **[Code/Doc]** Power simulation `scripts/simulate_phase8_power.py` and plan §8.8: change `N_model=9` to actual 14/10/1-pair design with PCSG eligibility ~98% and model-family random intercepts. **(Stats#1)**

### Tier 1 — MUST FIX BEFORE PRE-REGISTRATION

11. Add 2nd PCSG temporal pair (Llama-3 family preferred; Qwen2-vs-2.5 bridge fallback). DiD calibration written into PREREG_STAGE1. **(C2)**

12. C_FO sycophancy controls: nonmember controls + instruction-framing variants. Rename E_FO → "counterfactual outcome resistance". Reframe WS6 prediction as discriminative (memorization vs sycophancy), not localization. **(C4)**

13. AWQ-vs-fp16 rescoring audit on Qwen subset; restrict confirmatory CTS to quantization-homogeneous models OR report GLM separately. **(C3)**

14. Path E negative control: matched Chinese non-financial corpus from same months OR topic-shuffled placebo knee test. Knee must survive category/date-window adjustment. **(C1, Adv A2)**

15. Cutoff provenance Methods sentence + table; rename `cutoff_observed` → `exposure_horizon_observed`. **(C5)**

16. Add E_PCSG_capacity_curve analysis spec to plan §8.1A/§8.2 (model formula per Coh#3 sketch; case-cluster bootstrap). **(Coh#3, U9)**

17. Add WS6 conditional exit-gate item to plan §13. **(Coh#4, U10)**

18. Sweep all stale "5 white-box" / "9-model" / "1,440" references in plan + WS1 plan + DECISION_20260427 (§2.4 implementation bullet) + PENDING.md. Add supersession banner to DECISION_20260426 (don't rewrite signed history). **(Op#9, Coh#8/10)**

19. Stage 2 family states §7.1A: explicitly state PCSG-eligibility-failure → new decision memo, not silent demotion. **(Coh#2)**

20. Exploratory multiplicity rule (BH-FDR q=0.10 vs descriptive-only) — pick one and lock in PREREG_STAGE1. **(Stats#6)**

### Tier 2 — PAPER-DAY CAVEATS (acceptable concessions)

21. Title/abstract: "Chinese financial news" scope explicit. **(Adv A7)**
22. Capacity curve: framed as diagnostic replication of Carlini scaling, not novel contribution. **(Adv A6)**
23. Fleet Qwen-heavy: split claims into "Qwen white-box temporal evidence" vs "black-box behavioral corroboration". **(Adv A9)**
24. WS6 reproducibility: publish exact tokenizer/model SHAs + Docker digest + case IDs + artifact schema + recomputation script. **(Adv A10)**
25. Day-precision: explicitly down-claim to month-level exposure horizons. **(Adv A5, U15)**

---

## 6. Recommendation on Round 2

**Recommend: launch Round 2 (code review) AFTER deciding Tier-0 items 7-9** (denominator policy, WS6 CLI path, BL2 rule).

Rationale:
- Round 2's "P0 fix verification" lens (Lens A) needs to know the denominator policy + WS6 CLI decision to evaluate whether the existing `compute_pcsg`, `compute_pcsg_capacity_curve`, `extract_hidden_states` code paths actually meet the gates they target.
- Tier-0 items 1-6 (RunManifest, fleet-pin writer, knee detector, Path E joiner, distinct Path E run, pcsg_pairs validator) are *new code work* that Round 2 should evaluate post-implementation, not pre-implementation.
- Tier-0 item 10 (power sim rewrite) is independent.

Suggested sequence:
1. User confirms denominator + WS6 CLI + BL2 decisions (Tier-0 items 7-9).
2. Implement Tier-0 items 1-6 + 10 (estimated ~1-2 days).
3. Launch Round 2 code review on the new state.

Alternative: launch Round 2 now as an audit of *current* code (commit 332bd99). Round 2 will then explicitly cover the new code in a Round 2.5 after implementation.

---

## 7. Provenance

All 5 lens reports were produced by independent Codex MCP `xhigh` reasoning calls dispatched in parallel. Each Codex thread had no knowledge of other lenses. Convergent findings (§2) carry higher confidence because they replicate across orthogonal review framings (measurement / statistics / adversarial / engineering / editorial). Single-lens findings (§3) are not less valid but represent each lens's specialty area.

Codex thread IDs are recorded in the YAML frontmatter for re-engagement.
