# Round 1 Summary — Pilot Results Discussion

**Date:** 2026-04-06
**Agents:** Quant, NLP, Stats, Editor (all Codex, independent, no cross-visibility)

---

## Convergent Points (3+ agents agree)

### C1. CFLS is not measuring memorization in this setup (4/4 agree)
- **Quant:** CFLS shows the model is a text-conditioned event-to-direction mapper — "pipeline-safe-ish, alpha-unproven"
- **NLP:** "Construct drift" — CFLS measures counterfactual grounding sensitivity, not memorization. Weak convergent validity with actual leakage metrics.
- **Stats:** Non-identification — two DGPs (low memo + genuine reading, high memo + bidirectional generalization) produce the same CFLS. Violated exclusion restriction and monotonicity.
- **Editor:** CFLS failure is the paper's real story, not a disappointing null result.

### C2. Bidirectional generalization confound is real and generalizable (4/4 agree)
- **Quant:** Problem for measurement, but feature for trading robustness
- **NLP:** Known NLP issue — relates to shortcut learning (Geirhos 2020), annotation artifacts (Gururangan 2018)
- **Stats:** Classic omitted variable bias — bidirectional coverage B_i drives both high input sensitivity AND high memorization potential, creating negative bias in CFLS → memorization estimand
- **Editor:** Potentially a real contribution if elevated to formal threat-to-validity argument using the DAG

### C3. False-Outcome CPT is more promising than CFLS (4/4 agree)
- **Quant:** 14-17% flip rate is economically meaningful; model's knowledge channel exists but is secondary
- **NLP:** Additive conflict probe > replacement probe; reflects hybrid regime of parametric priors + context grounding; fits knowledge-conflict literature
- **Stats:** BUT needs proper null — testing against 0 is inappropriate; need negative controls (placebo conditions) to estimate baseline suggestibility
- **Editor:** Pivot CPT to primary metric, CFLS as diagnostic showing why reversal sensitivity is insufficient

### C4. Evidence intrusion heuristic is non-contributory (4/4 agree)
- **NLP:** Replace with claim-level source attribution (KaLMA-style)
- **Editor:** 0/36 reads as insensitive heuristic, not a finding; demote or redesign

### C5. The 1000-case benchmark needs fundamental redesign (4/4 agree)
- **Quant:** Prioritize rare, asymmetric, high-impact events; use corpus frequency as formal 3-dimensional covariate
- **NLP:** Split into 3 metric families (membership/exposure, context-conflict, source intrusion); estimate generic predictability baseline and residualize
- **Stats:** Pre-register estimands, adjustment set, minimum cell counts, negative/positive controls; use multilevel GLMM
- **Editor:** Design around identifiability, not just coverage; include low-memorization stratum; demonstrate metric discrimination

### C6. Cross-task r=0.10 reflects different constructs, not just noise (3/4 agree, Stats adds nuance)
- **Quant:** Tasks don't fail the same way — useful for gated ensemble in XGBoost
- **NLP:** Convergent-validity warning — direct_prediction measures fast schema retrieval, decomposed_impact measures multi-step causal decomposition
- **Stats:** Caution — at n=35, 95% CI is [-0.24, 0.42]; range restriction from floor effect likely attenuates; "pilot cannot establish convergent validity" is the correct conclusion
- **Editor:** (Implicit agreement through scope concerns)

---

## Divergent Points

### D1. Should the paper's core RQ change?
- **Editor (strong):** YES — shift from "task design shapes leakage" to "task design shapes observability of leakage" or "task design interacts with measurement validity"
- **NLP (mild):** Agrees CFLS measures something different, but doesn't explicitly propose RQ change
- **Quant:** Doesn't address paper framing directly — focuses on production implications
- **Stats:** Doesn't address narrative — focuses on inference protocol

### D2. How much to narrow the paper's scope?
- **Editor:** Strongly advocates narrowing — demote/remove XGBoost downstream section, simplify to benchmark + methodology paper
- **Quant:** Wants MORE scope — add direct economic validation (IC, hit rate, decile spread)
- **NLP/Stats:** Don't explicitly address scope, but NLP's 3-metric-family proposal is already ambitious

### D3. Venue strategy implications
- **Editor:** EMNLP still best, but needs framing as evaluation/benchmark paper; expand to 3+ model families
- **Quant:** Implicitly favors finance application angle
- **NLP/Stats:** Not addressed

### D4. Is 14-17% CPT flip rate "memorization" or "suggestibility"?
- **Quant:** Interprets as "knowledge channel exists but is secondary" — model tries to reconcile conflicting cues
- **NLP:** Interprets as knowledge conflict with hedging — fits Fakepedia literature
- **Stats:** Warns we cannot distinguish memorization from generic suggestibility without proper negative controls
- **Editor:** Warns reviewers will raise exactly this objection

---

## New Questions Raised

1. **Stats:** What is the proper null for CPT flip rate? Need negative controls (placebo conditions) before interpreting 14-17%.
2. **NLP:** Should CFLS be renamed/reframed as a "counterfactual grounding sensitivity" metric rather than a leakage metric?
3. **Editor:** Can the bidirectional confound be shown to be a general evaluation problem beyond finance?
4. **Quant:** Does the LLM feature beat a rules-based baseline on the medium/low-frequency bucket? If not, the leakage question is secondary.
5. **Stats:** Is the medium > high memorization CFLS pattern an artifact of Simpson's paradox (category composition confound)?
6. **Editor:** Should the paper expand to 3+ model families even at pilot stage?

---

## Convergence Assessment

**CONVERGED on:**
- C1–C5: Core findings interpretation, CFLS invalidity, CPT promise, benchmark redesign principles

**REQUIRES Challenger review on:**
- D1: Whether to pivot the core RQ (Editor is strong, others haven't weighed in)
- D2: Scope narrowing vs. expanding (Editor vs. Quant tension)
- D4: Whether CPT measures memorization or suggestibility (substantive, unresolved)
- New question #1: Proper null for CPT

**Status:** Proceed to Round 1.5 (Challenger)
