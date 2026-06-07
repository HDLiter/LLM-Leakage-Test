---
title: R5A Frozen Conceptual Shortlist
stage: R5A Step 2 closure
status: FROZEN — conceptual scope locked; implementation scope determined at pilot
author: Claude Code orchestrator + user design input
depends_on: MEASUREMENT_FRAMEWORK.md (four-layer framework definitions)
---

# R5A Frozen Conceptual Shortlist

## 0. Scope of this document

This document freezes the **conceptual measurement scope** of the R5A benchmark. It defines what we measure, not how we implement it. Implementation decisions (prompt wording, scoring thresholds, batch sizes) are deferred to pilot.

**Frozen** means: no estimand can be added to or removed from the primary family without a new review cycle. Exploratory and reserve items can be promoted via their stated decision rules, but not ad hoc.

---

## 1. Primary estimands (candidate pool)

Per the R-4a framework audit (`refine-logs/reviews/REOPEN_R1_R6/R4_methodology_audit/`),
no family-wise multiplicity correction is applied: effect sizes + 95% CIs are
reported per-estimand from mixed-model clustered-robust SE. The final primary
family size and composition are determined at R-1/R-2/R-6 + pilot data; the
inventory below is the candidate pool, not a locked count.

| Estimand | Operator | Perturbation | What it measures |
|---|---|---|---|
| **E_PCSG** | P_logprob | — | Paired cutoff surprise gap on the **cross-version Qwen pair `(qwen2.5-7B, qwen3-8B)`**, restricted to articles whose tokens stay in the Qwen2Tokenizer base vocab (`max_token_id ≤ 151664`). See PCSG note below. |
| **E_CTS** | P_logprob | — | Calibrated tail surprise (Min-K++/CTS absolute familiarity) |
| **E_NoOp** | P_predict | C_NoOp | NoOp sensitivity: does irrelevant clutter change the prediction? |

E_CMMD (cross-model cutoff-monotone disagreement) was CUT at R-4 construct
validity, decision D5 (`refine-logs/reviews/REOPEN_R1_R6/R4_methodology_audit/R4_construct_validity_decisions.md`).

E_FO (false-outcome resistance) and its C_FO perturbation were DROPPED at R-6
close (2026-06-06). The case-result-memory target E_FO chased is now carried by
counterfactual perturbation × pre/post-cutoff × salience slicing; the
counterfactual-family backbone choice is deferred to R-2
(`refine-logs/reviews/REOPEN_R1_R6/R6_pred_target_cfo/R6_DECISIONS.md`).

> **PCSG anchoring.** The same-tokenizer same-cutoff pairs `(qwen2.5-7B, qwen2.5-14B)` and `(qwen3-8B, qwen3-14B)` do not provide a cutoff-exposure differential — they share cutoff dates within-pair. PCSG is therefore anchored on the cross-version Qwen pair, which (i) shares the `Qwen2Tokenizer` class with byte-identical core vocab `0..151664`, (ii) differs in cutoff (both endpoints operator-asserted, subject to Path-E empirical probe), and (iii) keeps the same dense topology and instruct paradigm. The same-cutoff within-version pairs are repurposed as the `E_PCSG_capacity_curve` exploratory estimand (§3) measuring capacity-mediated memorization (Carlini 2021/2022). See `docs/DECISION_20260427_pcsg_redefinition.md`.

### 4 core factors (each estimand tested against all 4)

| Bloc | Factor | Type |
|---|---|---|
| 0 — Temporal exposure | Cutoff Exposure | case × model (continuous) |
| 1 — Repetition | Historical Family Recurrence | case-level (continuous) |
| 2 — Prominence | Target Salience (Entity Salience: target) | case-level (ordinal) |
| 1 — Repetition | Template Rigidity | case-level (continuous) |

### E_CTS + E_PCSG co-presence rationale

Both share P_logprob traces (zero marginal cost). E_CTS provides literature anchor (Min-K++, ICLR 2024/2025). E_PCSG provides the better-identified paired contrast. Interpretation: report as progressive narrative ("absolute → paired"), not independent discoveries.

The cross-version PCSG anchoring preserves this rationale. The cross-version pair shares the same `Qwen2Tokenizer` class and the analysis restricts to common-vocab articles, so paired identification holds. The cost is one new caveat: E_PCSG now also reflects pretraining-recipe / training-data-composition differences between Qwen2.5 and Qwen3 in addition to cutoff exposure, which we control for through `E_PCSG_capacity_curve` and the Path-E empirical cutoff probe.

---

## 2. Data-quality requirements for E_NoOp

The data-quality check is a per-artifact audit on individual perturbation
items, not a gate on aggregate estimand behavior. E_NoOp is unconditional
primary.

### E_NoOp data-quality requirements (C_NoOp perturbation)

| # | Requirement | Threshold | Role |
|---|---|---|---|
| 1 | Per-artifact human audit (natural CLS style, target-local edit, economic consistency, no unintended cues) | Overall ≥ 85%, no event type below 75% | **Gate** — items failing audit are removed from the eligible pool before analysis |
| 2 | Eligible case coverage (insertion-eligible cases / total) | Reported per perturbation × event type; coverage below 60% becomes a methods-section caveat | **Descriptive only — not a gate** |

**If condition 1 fails for an entire event type**: that event type is
excluded from analysis with an audit-quality caveat; the estimand
remains in the primary family on the surviving event types.
Failure does NOT demote the estimand.

**Estimand readiness failure** (separate from gates): if PCSG
common-vocab eligibility or NoOp insertion eligibility collapses to fewer
than `n_eff = 15` cells per the Section 6.4 matrix, treat as an
estimand-implementation failure and open a new decision memo before scope
freeze. This is not the same as a gate; it is a data-availability check.

---

## 3. Exploratory estimands

| Estimand | Operator | Perturbation | Status | Notes |
|---|---|---|---|---|
| **E_PCSG_capacity_curve** | P_logprob | — | Exploratory | log₂(params)-regression of paired logprob delta within-version (cutoff held fixed). Carlini-style capacity-memorization scaling. Members: Qwen2.5 `[1.5B, 3B, 7B, 14B, 32B]` (5 points) and Qwen3 `[4B, 8B, 14B, 32B]` (4 points). Reuses the same `LogProbTrace` artifacts as E_PCSG and E_CTS. |
| **E_SR** | P_predict | C_SR | Exploratory | Semantic-reversal resistance within counterfactual family |
| **E_EAD_t** | P_predict | C_anon (target) | Exploratory | Identity-keyed memory; C_anon multi-level gradient (L0-L4) enables dose-response analysis |
| **E_EAD_nt** | P_predict | C_anon (non-target) | Exploratory | Competing-entity distraction |
| **E_ADG** | P_predict | C_ADG + C_temporal | Reserve (see §4) | Temporal gate compliance |
| **E_ADG_conflict** | P_predict | C_ADG | Diagnostic only | Prompt-date vs text-date conflict resolution pattern; never enters statistical model |
| **E_TDR** | — | C_temporal | Not a standalone estimand | Redefined as cutoff × dose interaction term in mixed-effects model (see §5) |
| **E_extract** | P_extract | — | Reserve (see §4) | Masked span completion hit rate |
| **E_schema_cont** | P_schema | — | Reserve (see §4) | CLS prefix continuation fidelity; appendix only |

All exploratory estimands reported with: effect sizes, simultaneous CIs, hierarchical shrinkage across model × factor cells. They support convergent/discriminant validity arguments but do not spend confirmatory alpha.

---

## 4. Reserve promotion rules

> **Note.** All "K/N models" thresholds in this section use the
> **strict-majority denominator rule** from
> `docs/DECISION_20260429_gate_removal.md` §2.6:
> - "majority" thresholds → `K = ⌊N/2⌋ + 1`
> - "one-third" thresholds → `K = ⌈N/3⌉`
> where N is the operator-eligible fleet size at run time. The current
> 16-model split-tier fleet (12 white-box + 4 black-box; 14 P_predict-eligible)
> is the single source of truth in `config/fleet/r5a_fleet.yaml`.

### E_ADG: reserve → main-text exploratory

**Trigger** (any 1 of 2 sufficient):

| # | Trigger | Logic |
|---|---|---|
| 1 | Bloc 0 temporal channel weak in pilot (effect size d < 0.2 across fleet) | Need within-model temporal gating evidence |
| 2 | E_TDR interaction term shows strong temporal-cue dependency (p < 0.05 in pilot) | Time anchors are key mediator; E_ADG's prompt-level gating becomes causally important |

**Default if no trigger**: stays in reserve, reported in appendix with effect size + CI.

### E_extract: reserve → main-text exploratory or confirmatory

| Tier | Condition | Promotion to |
|---|---|---|
| Main-text exploratory | Pilot exact+fuzzy hit rate ≥ 5% on `≥ ⌈N/3⌉ = 5/14` models | Main text, marginal effects only (no factor interactions) + qualitative case gallery |
| Primary | Hit rate ≥ 15% on `≥ ⌊N/2⌋+1 = 8/14` models AND partial corr with E_CTS < 0.5 | Primary family. Expected unlikely. |
| Demoted | Hit rate < 5% on all models | Qualitative case gallery only, no quantitative estimand |

### E_schema_cont: reserve → appendix exploratory

Stats 4-criterion gate (all must hold on pilot):
1. max|corr(resid(S_schema), resid(E_j))| < 0.70 after residualizing Bloc 0-2 factors
2. Incremental out-of-fold R² ≥ 0.05 over all existing estimands
3. Reliability ≥ 0.70 and scorable coverage ≥ 75% of eligible cases
4. At least one Bloc 3 interaction sign-stable in ≥ 80% bootstrap resamples

**If gate fails**: dropped entirely from R5A. Deferred to follow-up paper.

---

## 5. E_TDR redefinition (locked)

E_TDR is **not a standalone estimand**. It is an interaction term in the mixed-effects model:

```
Y(i, m, d) = β₀ + β₁·cutoff(i,m) + β₂·dose(d) + β₃·cutoff(i,m)×dose(d)
             + γ·factors(i) + u_i + v_m + ε(i,m,d)
```

Where:
- Y = P_predict output (prediction correctness/confidence) at dose level d
- cutoff(i,m) = whether model m's cutoff is after case i's event date
- dose(d) = C_temporal degradation level (0=full, 1=weakened, 2=absent)
- **β₃ = E_TDR** = does the cutoff advantage shrink when temporal cues are removed?

**Parallel white-box validation**: same interaction structure on P_logprob with E_PCSG as backend. Convergent evidence if both β₃ terms are directionally consistent.

**Paper presentation**: one paragraph + one panel in the temporal figure. Sensitivity analysis, not headline finding.

---

## 6. Deferred items

### P_schema family → follow-up paper

| Variant | Verdict | Rationale |
|---|---|---|
| Continuation | RESERVE (appendix, pilot-gated via §4) | 3/4 lenses endorse as lowest-cost reserve; only variant retained in R5A |
| Cloze | DEFER | Subsumed by P_extract (3/4 lenses flagged overlap) |
| QA conversion | DEFER | Conceptually non-redundant (NLP lens) but engineering cost + scope risk outweigh |

**Follow-up paper framing**: "Schema-Level Memorization and Format Transfer in Chinese Financial LLMs" — covers continuation, cloze, QA as unified thesis on representational format and institutional template familiarity.

### English expansion → conditional stretch goal

5 trigger conditions (≥3 must hold to justify expansion). Evaluation point: after Chinese pilot results. See project memory `project_english_expansion.md` for full conditions.

---

## 7. Operators and perturbations (final inventory)

### Operators (3 confirmed + 1 candidate)

Fleet = 16-model split-tier: 12 white-box (10 full-operator [5 Qwen2.5 + 4 Qwen3
+ 1 GLM] + 2 Llama P_logprob-only) + 4 black-box; 14 P_predict-eligible,
12 P_logprob-eligible. Single source of truth: `config/fleet/r5a_fleet.yaml`.

| ID | Operator | Access | Fleet | Status |
|---|---|---|---|---|
| P_logprob | Token tail surprise (Min-K++/CTS) + cross-version PCSG + capacity curve | White-box | **12 models** (10 full-operator + 2 Llama logprob-only) | Confirmed |
| P_predict | Standardized sentiment/alpha prediction | Black-box sufficient | **14 models** (10 white-box full-operator + 4 black-box) | Confirmed |
| P_extract | Masked span completion | Black-box sufficient | **14 models** | Confirmed; also reused for Path-E empirical cutoff probe |
| P_schema | CLS prefix continuation | Black-box sufficient | **14 models** | Candidate (reserve) |

### Perturbations (5 confirmed)

| ID | Perturbation | Design | Status |
|---|---|---|---|
| C_anon | Entity anonymization | Multi-level dose-response (L0-L4 gradient); pilot uses L0 vs L4 binary | Confirmed |
| C_SR | Semantic polarity reversal | Rule-based antonym/operator maps per event type | Confirmed |
| C_NoOp | Irrelevant clause insertion | Deterministic clause bank; 8-16 chars; medial position | Confirmed |
| C_temporal | Temporal cue degradation | 2-3 dose levels; length-matched non-temporal deletion control mandatory | Confirmed |
| C_ADG | As-of date prompt manipulation | D4b (no text cues) primary; D4a (conflicting cues) diagnostic | Confirmed |

C_FO (false-outcome slot replacement) was DROPPED at R-6 close (2026-06-06); the
case-result-memory target is now carried by counterfactual perturbation ×
pre/post-cutoff × salience slicing, backbone choice deferred to R-2
(`refine-logs/reviews/REOPEN_R1_R6/R6_pred_target_cfo/R6_DECISIONS.md`).

---

## 8. Bloc 3 coverage

**Baseline (sufficient for R5A)**: Interaction-menu stratification — confirmatory estimands × Bloc 3 factors (Structured Event Type, Disclosure Regime/Modality, Event Phase, Session Timing).

**Upgrade path**: E_schema_cont (if pilot gate passes) provides additional institutional-template differentiation. If not, interaction-menu is the final Bloc 3 story.

---

## 9. Challenger + Cold Reader action items

### From Challenger pass (Claude cross-check, 2026-04-16)

| ID | Issue | Severity | Action | Phase |
|---|---|---|---|---|
| A1 | E_CTS/E_PCSG co-presence | Medium | Pre-register progressive narrative interpretation | Pre-registration |
| A2 | E_TDR formula | High | **Resolved** — redefined as mixed-model interaction term (§5) | Done |
| A3 | Quality-gated confirmatory vs pre-registration | Medium | Two-stage adaptive pre-registration protocol | Pre-registration |
| B1 | P_predict delta alternative explanations | High | model_capability covariate + limitations Caveat 1 | Analysis + paper |
| B2 | Perturbation eligibility power bottleneck | Medium | Pilot effective sample-size matrix (min cell ≥ 15) | Pilot |
| B3 | Explicit memory reference flag | Low | `explicit_memory_reference` flag in P_predict output parser | Implementation |
| B4 | API caching compresses delta | Low | Randomize seed / confirm cache policy | Implementation |
| C1 | Confirmatory estimands highly correlated | Medium | Pilot pairwise correlation matrix; regroup if r > 0.8 | Pilot |
| C2 | Fleet cutoff assumption | High | Assumption 1 + falsification pair + cutoff-monotone (not causal) language | Paper |
| C3 | P_predict ceiling/floor effects | Medium | Baseline confidence covariate / mid-range sensitivity check | Analysis |

### From Cold Reader pass (Codex Reviewer 2, 2026-04-16)

| ID | Issue | Severity | Action | Phase |
|---|---|---|---|---|
| F1 | Construct validity | Fatal → mitigated | Multi-signal convergence narrative + Qwen CPT causal anchor | Paper core |
| F2 | Overclaiming | Fatal → mitigated | Title: "Characterizing" not "Decomposing"; descriptive language throughout | Paper |
| F3 | Same-cutoff pair logic | Major | Downgrade to "consistency check"; list what it can/cannot exclude | Paper |
| F4 | Black-box API instability | Major | Version pinning + API fingerprint + Caveat | Implementation + paper |
| M1 | Framework = bureaucracy? | Major | Justify with tension dissolution table (§7 of MEASUREMENT_FRAMEWORK.md) | Paper |
| M2 | Power analysis needed | Major | Formal power analysis at pilot | Pilot |
| M3 | Perturbations not single-dimension | Major | 4-dimension audit protocol + honest discussion | Paper |
| M4 | Fleet heterogeneity | Major | White-box confirmatory + black-box exploratory split in reporting | Paper |
| BL1 | Missing: simple baselines (cutoff/frequency/prominence predictors) | High | Include as ablation | Analysis |
| BL2 | Missing: post-cutoff negative control | High | Include post-cutoff articles where models should NOT show signal | Data + analysis |
| BL3 | Missing: non-financial Chinese news negative control | Medium | Include if corpus available | Data |
| BL4 | Missing: human perturbation quality validation data | High | Report audit pass rates per perturbation × event type | Paper |

---

## 10. What this document does NOT freeze

- Prompt wording (frozen separately in `config/prompts/`)
- Scoring thresholds and implementations
- Fleet model versions (locked at experiment time)
- Corpus case selection (2,560 target; sampling strategy TBD)
- Factor annotation protocol details
- Compute budget allocation
- Paper section structure (guided by MEASUREMENT_FRAMEWORK.md §10, not binding)

---

This document is authoritative for conceptual scope decisions.
`MEASUREMENT_FRAMEWORK.md` remains authoritative for framework definitions and terminology.
