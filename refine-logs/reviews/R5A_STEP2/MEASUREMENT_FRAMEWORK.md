---
title: R5A — Four-layer measurement framework
stage: R5A Step 2, framework revision (post-user-review)
date: 2026-04-15
status: USER-REVIEWED — terminology locked, most open items closed, P_schema open for next session
author: Claude Code orchestrator + user design input
supersedes: The implicit "detector pool" framing used in R5A Step 1, R5A_DEFAULTS.md, and R5A_STEP2_SYNTHESIS.md
decisions_made:
  - "L1-L4 terminology locked: Factor / Perturbation / Operator / Estimand"
  - "E_CTS confirmatory: YES (literature anchor)"
  - "E_EAD_t confirmatory: NO (exploratory; core narrative is benchmark+factors, not identity-keyed memory)"
  - "P_schema: OPEN for next-session multi-agent discussion (expanded scope: continuation, cloze, QA)"
  - "C_anon redesigned as multi-level dose-response perturbation (L0-L4 gradient)"
  - "Companion entity replacement dataset noted as potential future contribution"
---

# R5A — Four-layer measurement framework

## 0. Why this document exists

R5A Step 1 and Step 2 discussed 10+ "detectors" and 7 design tensions. Many of those tensions turned out to be category errors: they arose from conflating **how we transform the text** (e.g., entity anonymization) with **how we compute a score** (e.g., Min-K++ logprob) with **what quantity we actually analyze** (e.g., the paired cutoff gap).

This document introduces a four-layer framework that separates these concerns explicitly. Under this framework:

- Several Step 2 tensions dissolve (T1 EAD, T2 SR/FO pairing, D11 status).
- The engineering scope becomes clearer: only 3-4 atomic scoring functions need to be built; complexity lives in text transformations and analytical combinations.
- The paper's methods section gains a clean expository structure: factors → perturbations → operators → estimands.

The framework does **not** change what we measure — it changes how we name, organize, and reason about the measurements.

---

## 1. The four layers

| Layer | Name | Definition | Input → Output |
|---|---|---|---|
| **L1** | **Factor** | A label assigned to each case in the corpus, used for stratification and interaction analysis | corpus case → categorical or numeric label |
| **L2** | **Perturbation** | A controlled transformation applied to the case text (or prompt), producing a variant that differs from the original in exactly one targeted dimension | original text → variant text (+ a derived secondary factor recording the case's eligibility for this perturbation) |
| **L3** | **Operator** | An atomic scoring function that takes (text, model) and returns a numeric score | (text, model) → score |
| **L4** | **Estimand** | An analytically meaningful quantity derived by combining operator scores across perturbation variants, model pairs, or fleet-wide patterns. Estimands are the objects that enter the statistical model. | {operator scores under specified conditions} → analytical indicator |

### Key relationships

- **Factors (L1)** classify the data. They never generate new text or compute scores.
- **Perturbations (L2)** generate text variants. They do not compute scores — they produce inputs for operators. Each perturbation **derives a secondary factor** (the case's eligibility or suitability for that perturbation).
- **Operators (L3)** are stateless scoring functions. They do not know about perturbations, factors, or experimental design. They take a text and a model and return a number.
- **Estimands (L4)** are where experimental design lives. An estimand defines **which operator**, on **which text variants** (original vs perturbation), across **which models** (single, paired, fleet-wide), and **what comparison** (difference, ratio, slope, disagreement pattern).

A useful test for layer assignment: if you can describe the concept without mentioning any specific model or any specific text transformation, it is probably a factor. If you can describe it without mentioning any specific model, it is probably a perturbation. If you can describe it without mentioning any perturbation or model comparison, it is probably an operator. If describing it requires specifying both an operator and a comparison strategy, it is an estimand.

---

## 2. L1 — Factors

### Primary factors (from corpus metadata, frozen in v6.2)

| Bloc | Factor | Type |
|---|---|---|
| **0 — Temporal exposure** | Cutoff Exposure | case × model (continuous) |
| **0 — Temporal exposure** | Temporal Anchor Recoverability | case-level (categorical, 3-bin) |
| **1 — Repetition / surface reuse** | Propagation Intensity: event_burst | case-level (continuous) |
| **1 — Repetition / surface reuse** | Propagation Intensity: historical_family_recurrence | case-level (continuous) |
| **1 — Repetition / surface reuse** | Template Rigidity | case-level (continuous) |
| **2 — Prominence / attention** | Entity Salience: target | case-level (ordinal) |
| **2 — Prominence / attention** | Entity Salience: non-target (max) | case-level (ordinal) |
| **2 — Prominence / attention** | Target Scope | case-level (categorical) |
| **2 — Prominence / attention** | Tradability Tier | case-level (ordinal) |
| **3 — Institutional stage / source** | Structured Event Type | case-level (categorical) |
| **3 — Institutional stage / source** | Disclosure Regime / Modality | case-level (categorical, unfrozen) |
| **3 — Institutional stage / source** | Event Phase | case-level (categorical) |
| **3 — Institutional stage / source** | Session Timing | case-level (categorical) |

Note: Temporal Anchor Recoverability was added in the R5A temporal-cue session as a secondary Bloc 0 factor. It is both a primary factor (observable from text annotation) and a perturbation eligibility indicator for C_temporal.

### Secondary factors (derived from perturbation eligibility)

Each perturbation in L2 implies a secondary factor that records whether a given case is eligible for that perturbation and how well the perturbation can be applied. These are not independent constructs — they are by-products of perturbation engineering.

| Perturbation | Derived secondary factor | Meaning |
|---|---|---|
| C_SR | Text Reversibility Score | How cleanly can the article's polarity be reversed? |
| C_FO | Known Outcome Availability | Does the article contain a verifiable, replaceable outcome slot? |
| C_NoOp | NoOp Eligibility | Is the article structurally suitable for clause insertion? (length, discourse structure) |
| C_anon | Entity Span Quality | How clean are the entity annotations? Does anonymization destroy economic meaning? |
| C_temporal | Temporal Anchor Recoverability | Does the article contain removable (adjunct-type) temporal cues? (Also a primary factor) |

---

## 3. L2 — Perturbations

Each perturbation is a controlled text transformation with a specific design intent, an admissibility gate, and a derived secondary factor.

| ID | Perturbation | Operation | Design intent | Admissibility gate | Derived factor |
|---|---|---|---|---|---|
| **C_anon** | Entity anonymization | Replace target and/or non-target entities with type-preserving placeholders | Isolate identity-keyed memory from event-content memory | Masking must not destroy the economic proposition; matched placeholder controls for tokenization artifacts | Entity Span Quality |
| **C_SR** | Semantic polarity reversal | Minimally reverse the financially material direction (bullish ↔ bearish) while holding the event shell fixed | Test whether the model follows edited semantics or clings to cached polarity | Rule-based antonym/operator maps per event type; ≥ 85% human-audit pass rate; event types without clean reversals are ineligible | Text Reversibility |
| **C_FO** | False outcome slot replacement | Replace the critical outcome value (number, status, verdict) with a specific false value while keeping setup, timing, and entities fixed | Test whether the model ignores visible counterfactual evidence in favor of memorized outcome slots | Rule-based slot schema per event type; restricted to cases with verified known outcomes; ≥ 85% audit pass rate | Known Outcome Availability |
| **C_NoOp** | Irrelevant clause insertion | Insert one rule-generated, irrelevant-but-plausible CLS clause (same time window, different entity, different cluster, non-entailing) | Test whether memorization manifests as brittle template matching distractible by finance-plausible clutter | Deterministic clause bank with auditable target-irrelevance proofs; ~8-16 Chinese characters; medial position only; ≥ 85% audit pass rate | NoOp Eligibility |
| **C_temporal** | Temporal cue degradation | Progressively remove temporal anchors (2-3 dose levels: full → weakened → absent) | Test whether memorization signals depend on retrievable time anchors as lookup keys | Length-matched non-temporal deletion control mandatory; adjunct-type coverage ≥ 50% of corpus required | Temporal Anchor Recoverability |
| **C_ADG** | As-of date prompt manipulation | Modify the system/user prompt to include an "as of" date before or after the event (D4b: no text temporal cues available; D4a: text cues present and potentially contradictory) | Test whether the model respects prompt-level temporal gating when text provides no/contradictory time anchors | Matched-date control (as-of date = event date) required for D4a | — (prompt-level, not text-level) |

### C_anon multi-level dose-response design (added post-user-review)

C_anon is redesigned from a binary perturbation (mask / don't mask) to a **multi-level information-stripping gradient**, analogous to C_temporal's dose levels. Each level retains progressively less identifying information:

| Level | Replacement example (贵州茅台) | Information retained | Information stripped |
|---|---|---|---|
| **L0** | 贵州茅台 (600519.SH) | Everything | Nothing |
| **L1** | 某知名白酒上市企业 | Industry + scale + listed status | Specific identity |
| **L2** | 某食品饮料企业 | Broad industry | Sub-industry + scale |
| **L3** | 某上市公司 | Listed status | Industry + scale |
| **L4** | 某公司 | Is a company | All characteristics |

**Analytical value**: The gradient reveals **at what granularity** the model's prediction shifts. If prediction changes sharply at L1 (specific identity removed, category preserved), memorization is identity-keyed. If it only changes at L3-L4, the model uses category-level priors, not entity-specific memory.

**Companion dataset potential**: A **Chinese Financial Entity Replacement Dataset** providing multi-level replacement schemes for all entities in the CLS corpus could be released alongside the benchmark. This dataset would serve broader Chinese financial NLP research (robustness testing, anonymization studies, entity-prior analysis).

**Pilot approach**: For the initial R5A pilot, implement L0 vs L4 (full anonymization) as the simplified binary version. Expand to the full gradient in the main run if the binary version shows signal.

### Perturbation quality protocol

All text-level perturbations (C_SR, C_FO, C_NoOp, C_temporal, C_anon) share a common quality protocol:

1. **Generation**: rule-based first, LLM-assisted fluency repair only within the allowed edit envelope.
2. **Audit**: human audit on four dimensions — natural CLS style, target-local edit only, economic consistency outside the edited slot, no unintended cues introduced.
3. **Pass threshold**: ≥ 85% overall, no event type below 75%.
4. **Demotion rule**: any perturbation that fails the audit gate is automatically excluded from confirmatory estimands. The operator and the estimand definition survive; only the perturbation's confirmatory status is revoked.

---

## 4. L3 — Operators

The entire R5A pool uses only **3 operators** (+ 1 candidate):

| ID | Operator | Computation | Access | Fleet coverage | Cost per case×model |
|---|---|---|---|---|---|
| **P_logprob** | Token tail surprise | Compute token-level log probabilities; score = calibrated mean of bottom-K% tokens (Min-K++/CTS) | White-box (logprobs required) | 5 models (Qwen2.5-7B, Qwen2.5-14B, Qwen3-8B, Qwen3-14B, GLM-4-9B) | 1 forward pass |
| **P_predict** | Standardized prediction | Present the article with a frozen task prompt; record the model's sentiment/direction/alpha prediction and associated confidence/logit | Black-box sufficient | Full fleet (9 models) | 1 API call |

**Design note on P_predict (user insight, 2026-04-15):** P_predict's baseline output may not be strongly discriminative on its own — most models can produce reasonable predictions on CLS news. Its real value is as the **carrier for perturbation-based estimands**: the prediction baseline alone is uninteresting, but the *delta* between baseline and perturbed variants (C_anon, C_SR, C_FO, C_NoOp, C_temporal) is where memorization evidence lives. This is the key reframing that motivated the four-layer framework: what Step 2 lenses called "detectors" (SR/FO, NoOp, EAD) are actually perturbations applied to this single core operator.
| **P_extract** | Masked span completion | Mask critical spans (numbers, entities, outcome phrases) in the article's latter half; prompt the model to continue/complete; score exact and fuzzy match against the ground truth | Black-box sufficient | Full fleet (9 models) | 1-3 API calls (multiple prompt variants) |
| **P_schema** | Schema completion (candidate) | Present the opening of a CLS wire (schema-type prefix); score the model's completion for fidelity to real CLS continuations | Black-box sufficient | Full fleet (9 models) | 1 API call |

### Notes on operators

- **P_logprob** must run with thinking mode OFF across all white-box models (per fleet review consensus). Thinking mode changes token probability distributions in ways that confound tail-surprise scores.
- **P_predict** uses each model's default deployed mode (thinking ON where that is standard). The frozen prompt schema in `config/prompts/` defines the standardized task.
- **P_extract** is inherently sparse — most cases will yield no exact match on most models, especially aligned models that paraphrase rather than quote.
- **P_schema** is a candidate operator for Bloc 3 coverage. Its inclusion depends on whether it shows partial independence from P_logprob on the same cases.

---

## 5. L4 — Estimands

Estimands are the analytical quantities that enter the statistical model. Each estimand is defined by specifying (a) which operator, (b) which perturbation variants are compared, (c) across which models or model pairs, and (d) what comparison operation produces the final score.

### 5.1 Surface family (P_logprob)

| ID | Estimand | Formula | Old ID | Analytical meaning |
|---|---|---|---|---|
| **E_CTS** | Calibrated Tail Surprise | P_logprob(text, m) with frequency calibration | D3 | Absolute surface familiarity of the text to model m. Baseline for all other logprob-based estimands. |
| **E_PCSG** | Paired Cutoff Surprise Gap | P_logprob(text, m_late) − P_logprob(text, m_early), within same-tokenizer model pairs | D2 | Cutoff-driven familiarity increment. The paired contrast differences out case difficulty, leaving temporal-exposure signal. |

**Relationship**: E_CTS and E_PCSG share the same operator (P_logprob) and the same raw data (logprob traces). E_PCSG is computed from E_CTS values on model pairs. They test different hypotheses: E_CTS tests absolute familiarity; E_PCSG tests whether familiarity tracks the cutoff boundary.

### 5.2 Cross-model family (P_predict, no perturbation)

| ID | Estimand | Formula | Old ID | Analytical meaning |
|---|---|---|---|---|
| **E_CMMD** | Cross-Model Memorization Disagreement | Cutoff-monotone disagreement pattern across the full fleet on P_predict outputs | D1 | Whether models that had temporal access to the event converge on predictions that earlier-cutoff models systematically miss. |

**Note**: E_CMMD is the only behavioral estimand that requires **no perturbation**. It exploits the fleet's natural cutoff structure as a quasi-experiment.

### 5.3 Perturbation-based family (P_predict + perturbations)

All of these share the same operator (P_predict) and follow the same logic: run P_predict on the original text and on the perturbed variant, then compare.

| ID | Estimand | Formula | Old ID | Perturbation | Analytical meaning |
|---|---|---|---|---|---|
| **E_FO** | False Outcome Resistance | P_predict(original, m) − P_predict(C_FO(text), m) | D5-FO | C_FO | Does the model ignore visible counterfactual evidence? High delta = slot-anchor memorization. |
| **E_SR** | Semantic Reversal Resistance | P_predict(original, m) − P_predict(C_SR(text), m) | D5-SR | C_SR | Does the model resist polarity reversal? High delta = cached directional conclusion. |
| **E_NoOp** | NoOp Sensitivity | P_predict(original, m) − P_predict(C_NoOp(text), m) | D6 | C_NoOp | Does irrelevant clutter change the prediction? High sensitivity = brittle template matching. |
| **E_EAD_t** | Target Entity Dependency | P_predict(original, m) − P_predict(C_anon_target(text), m) | D7-target | C_anon (target) | How much does the prediction depend on knowing the target's identity? |
| **E_EAD_nt** | Non-target Entity Distraction | P_predict(original, m) − P_predict(C_anon_nontarget(text), m) | D7-nontarget | C_anon (non-target) | How much does competing-entity identity distract the prediction? |
| **E_ADG** | Temporal Gate Compliance | P_predict(text, prompt_after) − P_predict(text, prompt_before), on cases where text temporal cues are masked | D4b | C_ADG + C_temporal | Does the model properly withhold knowledge when the prompt says "as of" a date before the event? |
| **E_ADG_conflict** | ADG Contradiction Mode | P_predict(text_with_cues, prompt_conflicting_date) response pattern | D4a | C_ADG | Diagnostic only: how does the model resolve prompt-date vs text-date conflicts? |

### 5.4 Temporal sensitivity (meta-estimand)

| ID | Estimand | Formula | Old ID | Analytical meaning |
|---|---|---|---|---|
| **E_TDR** | Temporal Dose-Response | Slope of E_CMMD (or E_FO) across C_temporal dose levels | D11 | Does the memorization signal decay as temporal anchors are progressively removed? A positive slope = the signal partially depends on time-cue-mediated retrieval, not just generic event familiarity. |

**Note**: E_TDR is a **second-order estimand** — it measures how another estimand (E_CMMD) changes under a perturbation (C_temporal). It is a sensitivity analysis, not a standalone measurement.

### 5.5 Extraction family (P_extract)

| ID | Estimand | Formula | Old ID | Analytical meaning |
|---|---|---|---|---|
| **E_extract** | Extraction Hit Rate | P_extract(masked_text, m) — exact/fuzzy match rate per case×model | D8 | Can the model recover hidden CLS spans verbatim? Hard-edge evidence of memorization that is qualitatively different from behavioral indicators. |

### 5.6 Schema family (P_schema, candidate)

| ID | Estimand | Formula | Old ID | Analytical meaning |
|---|---|---|---|---|
| **E_schema** | Schema Completion Fidelity | P_schema(prefix, m) scored against real CLS continuation, stratified by institutional schema type | D12 | Does the model complete institutional templates (regulatory, corporate-filing, analyst) with higher fidelity than free-form types? Candidate for Bloc 3 coverage. |

---

## 6. Mapping: old detector pool → new framework

| Old ID | Old name | L2 Perturbation | L3 Operator | L4 Estimand(s) | What changed |
|---|---|---|---|---|---|
| D1 | CMMD | — | P_predict | E_CMMD | Reframed as estimand on P_predict with no perturbation |
| D2 | PCSG | — | P_logprob | E_PCSG | Reframed as estimand (paired difference) on P_logprob |
| D3 | Min-K++/CTS | — | P_logprob | E_CTS | Reframed as baseline estimand on P_logprob |
| D4a | ADG contradiction | C_ADG | P_predict | E_ADG_conflict | Reframed as perturbation + estimand; diagnostic only |
| D4b | ADG misdirection | C_ADG + C_temporal | P_predict | E_ADG | Reframed as perturbation + estimand |
| D5-SR | Semantic Reversal | C_SR | P_predict | E_SR | **No longer a "detector"** — it is a perturbation applied to P_predict |
| D5-FO | False Outcome | C_FO | P_predict | E_FO | **No longer a "detector"** — it is a perturbation applied to P_predict |
| D6 | FinMem-NoOp | C_NoOp | P_predict | E_NoOp | **No longer a "detector"** — it is a perturbation applied to P_predict |
| D7 | EAD | C_anon | P_predict (or any) | E_EAD_t, E_EAD_nt | **No longer a "detector"** — it is a perturbation. T1 tension dissolved. |
| D8 | Extraction | — (masking is internal) | P_extract | E_extract | Reframed as separate operator + estimand |
| D9 | RAVEN | — | — | — | Dropped (Step 2 unanimous) |
| D10 | Debias Delta | — | — | — | Dropped (Step 2 unanimous) |
| D11 | Temporal Dose-Response | C_temporal | P_predict via E_CMMD | E_TDR | Reframed as second-order estimand (sensitivity protocol) |
| D12 | Schema-Completion | — | P_schema | E_schema | Reframed as separate operator + estimand; candidate status |

---

## 7. What the framework resolves

### Tensions dissolved

| Tension | Old framing | New framing | Resolution |
|---|---|---|---|
| **T1 (EAD standalone vs field)** | Is D7 a standalone detector or a cross-detector field? | C_anon is a perturbation; E_EAD_t and E_EAD_nt are estimands. They are not a separate operator. | Dissolved. No "standalone vs field" choice needed. C_anon is applied; the resulting deltas are estimands that can be analyzed alongside other P_predict estimands. |
| **T2 (SR/FO one detector or two)** | Are SR and FO one detector slot or two? | C_SR and C_FO are two perturbations. E_SR and E_FO are two estimands. They share P_predict. | Dissolved. There is no "detector slot" to count. Both estimands exist; both enter the analysis; the question of "one or two" was a category error. |
| **D11 status** | Is D11 a detector, a protocol, or a field? | E_TDR is a second-order estimand (sensitivity analysis on E_CMMD across C_temporal levels). | Dissolved. E_TDR is naturally secondary/exploratory — it is a sensitivity check, not a primary measurement. |
| **D6 "detector or not"** | Is NoOp a real detector or just a robustness check? | C_NoOp is a perturbation; E_NoOp is an estimand. Its analytical status depends on C_NoOp's quality gate, not on whether it "counts" as a detector. | Reframed. The question is no longer "detector slot?" but "does this perturbation pass its admissibility gate?" |

### Tensions that remain (but are clearer)

| Remaining question | New framing |
|---|---|
| **E_PCSG confirmatory status** | E_CTS and E_PCSG share P_logprob. Both are estimands. Should both spend confirmatory alpha, or only E_PCSG (the better-identified one)? This is a pure multiplicity question. |
| **E_NoOp confirmatory status** | Conditional on C_NoOp passing its quality gate. If yes, E_NoOp is confirmatory. If no, E_NoOp is exploratory. Binary decision, quality-gated. |
| **E_ADG main text vs reserve** | E_ADG requires both C_ADG and C_temporal. Is the incremental information over E_CMMD (which also targets Bloc 0 without any perturbation) worth the page budget? |
| **E_extract main text vs reserve** | P_extract is a separate operator with its own power characteristics. Is the hit rate high enough for confirmatory use? Pilot-dependent. |
| **E_schema inclusion** | P_schema is a candidate operator. Is it partially independent from P_logprob? Pilot-dependent. |
| **Bloc 3 coverage** | Interaction-menu stratification is the baseline. E_schema is the upgrade option, but only after Bloc 3 ontology freezes. |

---

## 8. Engineering implications

### Operator pipeline is simple

Only 3-4 operators need to be implemented as software:

1. **P_logprob pipeline**: one forward pass per (text, model) on 5 white-box models. Batch-friendly. Run once; reuse traces for both E_CTS and E_PCSG.
2. **P_predict pipeline**: one API call per (text, model) on 9 models. This is the workhorse — it serves E_CMMD and all perturbation-based estimands.
3. **P_extract pipeline**: 1-3 API calls per (text, model) on 9 models. Independent from P_predict.
4. **P_schema pipeline** (candidate): one API call per (prefix, model) on 9 models. Independent.

### Perturbation generation is the real engineering effort

The hard work is in L2, not L3. Each perturbation needs:
- A rule-based generation pipeline (Thales-dependent for some)
- Human audit with the 4-dimension quality protocol
- Eligibility labels (secondary factors) for every case

### Compute budget restructured

Under the old framing, compute was estimated per "detector." Under the new framing:

| Component | Calls | Notes |
|---|---|---|
| P_logprob baseline (all cases × 5 WB models) | ~12,800 forward passes | Run once; serves E_CTS + E_PCSG |
| P_predict baseline (all cases × 9 models) | ~23,040 API calls | Run once; serves E_CMMD |
| P_predict × each perturbation variant × 9 models | ~23,040 per perturbation | C_anon (×2 mask types), C_SR, C_FO, C_NoOp, C_temporal (×2-3 dose levels), C_ADG (×2 prompt dates) |
| P_extract (all cases × 9 models × 1-3 prompts) | ~23,040 to ~69,120 | Independent run |
| **Total P_predict calls** (baseline + ~8-10 perturbation variants) | **~210,000-250,000** | Dominant cost |

This makes it clear that **P_predict is the bottleneck** and perturbation count is the cost driver. Adding a perturbation adds ~23K calls; adding an operator adds ~12-23K calls.

---

## 9. Confirmatory vs exploratory partition (revised)

Under the new framework, the confirmatory/exploratory partition applies to **estimands**, not "detectors."

### Proposed confirmatory estimands

| Estimand | Operator | Perturbation | Core factors tested (4 per estimand) |
|---|---|---|---|
| **E_CMMD** | P_predict | — | Cutoff Exposure, Historical Family Recurrence, Target Salience, Template Rigidity |
| **E_PCSG** | P_logprob | — | same 4 |
| **E_CTS** | P_logprob | — | same 4 |
| **E_FO** | P_predict | C_FO | same 4 (conditional on C_FO quality gate) |
| **E_NoOp** | P_predict | C_NoOp | same 4 (conditional on C_NoOp quality gate) |

**Total confirmatory coefficients**: 5 estimands × 4 factors = **20** (unchanged from Step 2 Stats recommendation).

### Proposed exploratory estimands

| Estimand | Reason for exploratory status |
|---|---|
| E_SR | Secondary to E_FO within the counterfactual perturbation family |
| E_EAD_t, E_EAD_nt | Perturbation-derived; informative but not independent constructs |
| E_ADG | Reserve; incremental over E_CMMD not yet demonstrated |
| E_TDR | Second-order estimand; sensitivity analysis |
| E_extract | Sparse hits; insufficient power for confirmatory factor interactions |
| E_schema | Candidate operator; independence from P_logprob unverified |

---

## 10. Paper presentation under the framework

The four-layer framework maps naturally to a methods section structure:

### Methods section outline

1. **Corpus and factor schema** (L1)
   - 2,560 cases, 13 factors across 4 blocs
   - Factor definitions, annotation protocol, inter-annotator agreement

2. **Perturbation protocol** (L2)
   - 6 perturbations with design intent, generation rules, and quality gates
   - Audit results: pass rates per perturbation × event type

3. **Operators** (L3)
   - P_logprob: Min-K++/CTS on 5 white-box models (thinking OFF)
   - P_predict: standardized prediction on 9-model fleet (default mode)
   - P_extract: masked span completion on 9-model fleet

4. **Estimands and statistical model** (L4)
   - 5 confirmatory estimands with pre-registered factor interactions
   - Exploratory estimands with shrinkage
   - Multiplicity control: Westfall-Young stepdown max-T on the 20-coefficient confirmatory family

### Display budget (Editor recommendation, updated)

- **Table 1**: Four-layer framework overview (factor, perturbation, operator, estimand mapping)
- **Table 2**: Fleet composition with design pairings
- **Figure 1**: Main estimand × factor results matrix (5 confirmatory estimands × 4 factors)
- **Figure 2**: Temporal panel (E_CMMD + E_TDR sensitivity)
- **Figure 3**: Perturbation panel (E_FO / E_NoOp qualitative examples)

---

## 11. Naming conventions

The user noted that the working names may need revision. Candidate terminology for the paper:

| Layer | Chinese | English | Rationale |
|---|---|---|---|
| L1 | 因子 | **Factor** | Standard in experimental design and psychometrics |
| L2 | 控制条件 | **Perturbation** | Standard in NLP robustness literature (GSM-Symbolic, counterfactual evaluation) |
| L3 | 算子 | **Operator** | Maps directly from the Chinese 算子; denotes a function mapping (text, model) → score without implying a specific mechanism |
| L4 | 测评 | **Estimand** | Standard in causal inference; precisely denotes "the quantity you intend to estimate" |

**Locked after user review (2026-04-15).**

---

## 12. Open items — status after user review

### 12.1 E_CTS confirmatory — CLOSED ✅

**Decision**: E_CTS is **confirmatory**. Min-K++/CTS is a well-established method (ICLR 2024/2025) that appears across multiple memorization papers. Keeping it confirmatory provides a literature anchor, reviewer familiarity, and enables direct comparison with E_PCSG to demonstrate the paired-contrast improvement. Marginal cost is zero (reuses P_logprob traces).

### 12.2 E_EAD_t confirmatory — CLOSED ✅

**Decision**: E_EAD_t is **exploratory**. The paper's core narrative is about the benchmark architecture and factor-driven analysis, not about identity-keyed memory specifically. E_EAD_t will still be computed, reported with effect sizes, and visualized — but it will not spend confirmatory alpha. This keeps the confirmatory budget at 20 coefficients (5 estimands × 4 factors).

Note: C_anon is redesigned as a **multi-level dose-response perturbation** (see §3 addendum below). The single E_EAD_t delta is replaced conceptually by an information-stripping gradient (L0 original → L1 detailed category → L2 coarse category → L3 minimal → L4 full anonymization). This gradient analysis is naturally exploratory and is a richer contribution than a single binary delta.

### 12.3 P_schema — OPEN 🔓 (for next-session discussion)

**Status**: open for multi-agent discussion in the next session.

**User observation**: P_schema is more interesting than originally framed. The concept is not limited to prefix-continuation; it encompasses multiple operator variants:

| Variant | Operation | What it tests |
|---|---|---|
| **Continuation** | Give a CLS wire prefix; model continues | Does the model know how this type of news typically unfolds? |
| **Cloze / fill-in-the-blank** | Mask specific slots (numbers, entities, outcomes) within a complete article; model fills | Can the model recover specific facts from structural context? |
| **QA conversion** | Convert the news article into question-answer pairs; model answers | Does the model "know" the content in a different representational format? |

These are potentially distinct operators (each defines a different (text, model) → score function), not just variants of one operator. The next session should discuss:

1. Whether any of these adds non-redundant information beyond P_logprob and P_predict.
2. Whether any of these is particularly suited to Bloc 3 coverage (institutional-schema differentiation).
3. Whether the engineering cost of an additional operator is justified given the current paper scope.
4. Whether this is better positioned as a contribution for this paper or for a follow-up.

### 12.4 Framework terminology — CLOSED ✅

**Decision**: The four-layer naming is locked:

| Layer | Chinese | English |
|---|---|---|
| L1 | 因子 | **Factor** |
| L2 | 控制条件 | **Perturbation** |
| L3 | 算子 | **Operator** |
| L4 | 测评 | **Estimand** |

---

## 13. Artifacts

This document supersedes the implicit "detector pool" framing in:
- `R5A_STEP1_SYNTHESIS.md` §1 detector matrix
- `R5A_DEFAULTS.md` §2-§5 tension positions and detector evaluations
- `R5A_STEP2_SYNTHESIS.md` §2-§4 verdict matrix and shortlist

The mapping table in §6 provides the translation key between old and new terminology.
