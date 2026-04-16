---
title: R5A Frozen Conceptual Shortlist
stage: R5A Step 2 closure
date: 2026-04-16
status: FROZEN — conceptual scope locked; implementation scope determined at pilot
author: Claude Code orchestrator + user design input
supersedes: R5A_STEP2_SYNTHESIS.md §3 shortlist, MEASUREMENT_FRAMEWORK.md §9 partition
depends_on: MEASUREMENT_FRAMEWORK.md (four-layer framework definitions)
session_decisions:
  - "P_schema: Continuation RESERVE (pilot-gated appendix), Cloze DEFER, QA DEFER"
  - "E_TDR: redefined as mixed-model interaction term (cutoff × dose), not standalone estimand"
  - "E_NoOp: 3-condition quality gate for confirmatory status"
  - "E_ADG: 3-trigger promotion rule for reserve → main-text exploratory"
  - "E_extract: 2-tier promotion rule (hit rate thresholds)"
  - "Bloc 3 coverage: interaction-menu stratification sufficient; no additional operator needed"
  - "Construct validity strategy: multi-signal convergence + Qwen CPT causal anchor"
  - "English expansion: conditional stretch goal, 5-trigger evaluation after Chinese pilot"
---

# R5A Frozen Conceptual Shortlist

## 0. Scope of this document

This document freezes the **conceptual measurement scope** of the R5A benchmark. It defines what we measure, not how we implement it. Implementation decisions (prompt wording, scoring thresholds, batch sizes) are deferred to pilot.

**Frozen** means: no estimand can be added to or removed from the confirmatory family without a new review cycle. Exploratory and reserve items can be promoted via their stated decision rules, but not ad hoc.

---

## 1. Confirmatory estimands (5 × 4 factors = 20 coefficients)

Multiplicity control: Westfall-Young stepdown max-T across the 20-coefficient family.

| Estimand | Operator | Perturbation | What it measures | Conditional? |
|---|---|---|---|---|
| **E_CMMD** | P_predict | — | Cutoff-monotone fleet disagreement on sentiment/alpha predictions | No |
| **E_PCSG** | P_logprob | — | Paired cutoff surprise gap (late-model − early-model logprob, same tokenizer) | No |
| **E_CTS** | P_logprob | — | Calibrated tail surprise (Min-K++/CTS absolute familiarity) | No |
| **E_FO** | P_predict | C_FO | False outcome resistance: does the model ignore visible counterfactual evidence? | Yes — C_FO quality gate |
| **E_NoOp** | P_predict | C_NoOp | NoOp sensitivity: does irrelevant clutter change the prediction? | Yes — C_NoOp quality gate |

### 4 core factors (each estimand tested against all 4)

| Bloc | Factor | Type |
|---|---|---|
| 0 — Temporal exposure | Cutoff Exposure | case × model (continuous) |
| 1 — Repetition | Historical Family Recurrence | case-level (continuous) |
| 2 — Prominence | Target Salience (Entity Salience: target) | case-level (ordinal) |
| 1 — Repetition | Template Rigidity | case-level (continuous) |

### E_CTS + E_PCSG co-presence rationale

Both share P_logprob traces (zero marginal cost). E_CTS provides literature anchor (Min-K++, ICLR 2024/2025). E_PCSG provides the better-identified paired contrast. Pre-registered interpretation: report as progressive narrative ("absolute → paired"), not independent discoveries.

---

## 2. Quality-gated confirmatory conditions

### E_FO quality gate (C_FO perturbation)

| # | Condition | Threshold |
|---|---|---|
| 1 | Human audit pass rate (natural CLS style, target-local edit, economic consistency, no unintended cues) | Overall ≥ 85%, no event type below 75% |
| 2 | Eligible case coverage (cases with verified known outcomes / total pre-cutoff) | ≥ 60% of pre-cutoff cases |
| 3 | Baseline delta non-degeneracy | mean \|delta\| > 0 on ≥ 5/9 models |

**If any condition fails**: E_FO demoted to exploratory. Confirmatory family shrinks to 4 estimands × 4 factors = 16 coefficients.

### E_NoOp quality gate (C_NoOp perturbation)

| # | Condition | Threshold |
|---|---|---|
| 1 | Human audit pass rate (insertion naturalness + target irrelevance) | Overall ≥ 85%, no event type below 75% |
| 2 | Eligible case coverage | ≥ 60% of pre-cutoff cases |
| 3 | Baseline delta non-degeneracy | mean \|delta\| > 0 on ≥ 5/9 models |

**If any condition fails**: E_NoOp demoted to exploratory. Same shrinkage rule.

**Neither E_SR nor any other estimand auto-backfills** a demoted confirmatory slot.

---

## 3. Exploratory estimands

| Estimand | Operator | Perturbation | Status | Notes |
|---|---|---|---|---|
| **E_SR** | P_predict | C_SR | Exploratory | Secondary to E_FO within counterfactual family |
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

### E_ADG: reserve → main-text exploratory

**Trigger** (any 1 of 3 sufficient):

| # | Trigger | Logic |
|---|---|---|
| 1 | E_CMMD signal weak in pilot (effect size d < 0.2 across fleet) | Bloc 0 primary channel fails; need within-model temporal gating evidence |
| 2 | E_FO or E_NoOp demoted from confirmatory (quality gate failure) | Confirmatory vacancy; E_ADG is closest Bloc 0 candidate |
| 3 | E_TDR interaction term shows strong temporal-cue dependency (p < 0.05 in pilot) | Time anchors are key mediator; E_ADG's prompt-level gating becomes causally important |

**Default if no trigger**: stays in reserve, reported in appendix with effect size + CI.

### E_extract: reserve → main-text exploratory or confirmatory

| Tier | Condition | Promotion to |
|---|---|---|
| Main-text exploratory | Pilot exact+fuzzy hit rate ≥ 5% on ≥ 3/9 models | Main text, marginal effects only (no factor interactions) + qualitative case gallery |
| Confirmatory | Hit rate ≥ 15% on ≥ 5/9 models AND partial corr with E_CTS < 0.5 | Confirmatory family (→ 24 coefficients). Expected unlikely. |
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

| ID | Operator | Access | Fleet | Status |
|---|---|---|---|---|
| P_logprob | Token tail surprise (Min-K++/CTS) | White-box | 5 models | Confirmed |
| P_predict | Standardized sentiment/alpha prediction | Black-box sufficient | 9 models | Confirmed |
| P_extract | Masked span completion | Black-box sufficient | 9 models | Confirmed |
| P_schema | CLS prefix continuation | Black-box sufficient | 9 models | Candidate (reserve) |

### Perturbations (6 confirmed)

| ID | Perturbation | Design | Status |
|---|---|---|---|
| C_anon | Entity anonymization | Multi-level dose-response (L0-L4 gradient); pilot uses L0 vs L4 binary | Confirmed |
| C_SR | Semantic polarity reversal | Rule-based antonym/operator maps per event type | Confirmed |
| C_FO | False outcome slot replacement | Rule-based slot schema per event type; known-outcome cases only | Confirmed |
| C_NoOp | Irrelevant clause insertion | Deterministic clause bank; 8-16 chars; medial position | Confirmed |
| C_temporal | Temporal cue degradation | 2-3 dose levels; length-matched non-temporal deletion control mandatory | Confirmed |
| C_ADG | As-of date prompt manipulation | D4b (no text cues) primary; D4a (conflicting cues) diagnostic | Confirmed |

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

## 11. Document lineage

```
R5A_DEFAULTS.md (Step 1 opening positions)
  → R5A_STEP1_SYNTHESIS.md (Step 1 pool)
    → {quant,nlp,stats,editor}_lens.md (Step 2 lenses)
      → R5A_STEP2_SYNTHESIS.md (Step 2 convergence)
        → MEASUREMENT_FRAMEWORK.md (four-layer reframe)
          → R5A_FROZEN_SHORTLIST.md (this document)  ← AUTHORITATIVE
```

All prior documents are superseded for scope decisions. MEASUREMENT_FRAMEWORK.md remains authoritative for framework definitions and terminology.
