---
role: NLP / methodology
lens: R5A Step 1 detector brainstorm
thread_id: 019d914a-0dde-7120-a1a7-3c3b991899c9
model_reasoning_effort: xhigh
generated: 2026-04-15
---

Primary recommendation from the NLP lens: keep detectors **independent** in R5A Step 1. If you later build an operational composite, it should be secondary and explicitly downstream of detector-specific validity evidence, not the basis of the construct claim.

## CMMD
**Name** Cross-Model Memorization Disagreement.

**Concept** Compare the same CLS case across the six-model fleet and score whether disagreement lines up with known cutoff ordering rather than generic model weakness. The detector is strongest when post-cutoff models converge on a detail that pre-cutoff models systematically miss or hedge.

**Mechanism family** Cross-model.

**Access requirement** Either; supports **all 6 fleet members**.

**Construct-validity rationale** This is the cleanest candidate measure of **cutoff-conditioned familiarity** because the mechanism is externally anchored by known model cutoffs rather than inferred from a single model's confidence. In a nomological-network framing, I would expect strong convergence with Cutoff Exposure and with a separate chronology-gating probe, but only partial convergence with surface-form detectors; if CMMD simply collapses onto Template Rigidity, that is evidence against the intended construct, not for it. Criterion-related evidence is especially strong if disagreement exhibits a changepoint near the benchmark cutoff and if the sign of disagreement tracks model chronology. Main failure modes are construct-irrelevant variance from architecture/instruction-tuning differences, uneven Chinese financial competence, and hosted-model decoding idiosyncrasies; this is why Cronbach-Meehl/Xiao/Freiesleben-style interpretation should treat cross-detector agreement as one piece of evidence, not validation by correlation alone.

**Factor relevance** Cutoff Exposure: very strong positive, the primary signal. Propagation Intensity: `event_burst` moderate positive because highly exposed events should sharpen post-cutoff agreement; `historical_family_recurrence` moderate positive but partly generic-schema leakage. Template Rigidity: moderate positive, but too much signal here would indicate surface collapse. Entity Salience: `target_salience` moderate positive; `max_non_target_entity_salience` likely raises spurious disagreement via distraction, so treat as confound. Anchor Strength: strong positive because exact anchors should create sharper pre/post-cutoff separation. Disclosure Regime: plausible moderate positive for formal disclosures through wider diffusion and more canonical reporting, but this is mechanism-only, not literature-backed. Session Timing: weak-to-moderate, with a plausible market-attention path, but no direct memorization-benchmark precedent.

**Bloc diversification** Primary bloc target: **0**.

**Ensemble compatibility** **Independent reporting**. CMMD is interpretable because the source of variation is known; folding it into an MCS-style ensemble would obscure the very mechanism that makes it valuable.

**Detector-level stratification fields (P5)** `cutoff_rank_slope`; `agreement_crossover_index`. **EAS applies**: mask target entities and, separately, non-target entities, then measure delta in disagreement; this is useful for testing whether disagreement is driven by company-name familiarity versus event content.

**Thales dependency** Raw CLS text works immediately; gains from Thales cluster IDs, entity normalization, and event labels for cleaner stratification.

**Compute budget estimate** Roughly `3,200 x 6 = 19,200` generations or scored responses; moderate API budget; low local GPU cost.

**Key citations** [Roy & Roy 2026 / MemGuard-Alpha](https://arxiv.org/abs/2603.26797); [Cronbach & Meehl 1955](https://psychclassics.yorku.ca/Cronbach/construct.htm); [Xiao et al. 2023](https://aclanthology.org/2023.emnlp-main.676/); [Freiesleben 2026](https://arxiv.org/abs/2603.15121); [Perlitz et al. 2024](https://arxiv.org/abs/2407.13696).

**Meeus 2024 SoK impact** N/A.

## FinMem-NoOp
**Name** FinMem-NoOp.

**Concept** Insert one irrelevant-but-plausible financial clause into the CLS item and measure whether the detector score or model judgment changes when it should not. This is a negative-control perturbation aimed at separating event understanding from susceptibility to salient but non-causal finance surface material.

**Mechanism family** Counterfactual.

**Access requirement** Either; supports **all 6 fleet members**.

**Construct-validity rationale** FinMem-NoOp is the strongest counterfactual **negative control** in the slate. It is not a pure memorization measure; it is a measure of **construct-irrelevant context sensitivity**, which is exactly why it is valuable for FinMem-Bench's legitimacy. In MTMM terms, I would expect convergence with competing-entity distraction effects and with partial-input attentiveness failures, but only weak convergence with verbatim extraction. If a detector changes sharply under NoOp insertions, the benchmark can argue that the detector is partly loading on spurious contextual salience rather than the intended memorization construct; that is classic Cronbach-Meehl/Xiao validity work.

**Factor relevance** Cutoff Exposure: weak or ambiguous, not a primary target. Propagation Intensity: `event_burst` weak; `historical_family_recurrence` moderate positive because familiar schemas invite spurious clause assimilation. Template Rigidity: moderate positive. Entity Salience: `target_salience` likely negative or weakly negative because strong target anchoring should resist the NoOp; `max_non_target_entity_salience` should be strongly positive via the Glasserman-Lin distraction path. Anchor Strength: weakly negative because stronger anchors should stabilize the response. Disclosure Regime: plausible lower sensitivity for formal disclosures because regulated text is more target-focused, but this is mechanism-only. Session Timing: plausible weak positive for intraday/noisy contexts, with no direct literature support.

**Bloc diversification** Primary bloc target: **2**.

**Ensemble compatibility** **Independent reporting**. Use it as a falsification/robustness detector, not as one more score inside a black-box ensemble.

**Detector-level stratification fields (P5)** `noop_sensitivity_score`; `competing_clause_entity_type`. **EAS applies strongly**: compare NoOp sensitivity before/after target masking and before/after non-target masking; the two deltas should be kept separate because they test different distraction channels.

**FinMem-NoOp specifics** Recommendation: **rule-based first, LLM-validated second**. Generate the inserted clause from a same-window CLS item with a different normalized target entity, different cluster ID, and no causal entailment to the base case; then use a lightweight validation step to reject leakage or accidental relevance. "Novel vs copied" should be checked with a RAVEN-style overlap view on rationales: robust behavior keeps the decision stable and does not start echoing the inserted clause's local n-grams.

**Thales dependency** Needs Thales outputs for high-validity generation: entity normalization, cluster IDs, and ideally event-type labels. Can run degraded without Thales, but validity drops sharply.

**Compute budget estimate** Around `3,200 x 6 x 2 = 38,400` prompt evaluations plus clause-generation overhead; moderate API cost.

**Key citations** [GSM-Symbolic](https://arxiv.org/abs/2410.05229); [RAVEN](https://aclanthology.org/2023.tacl-1.38/); [Elazar et al. 2024 / CAT](https://aclanthology.org/2024.findings-emnlp.205/); [Cronbach & Meehl 1955](https://psychclassics.yorku.ca/Cronbach/construct.htm); [Xiao et al. 2023](https://aclanthology.org/2023.emnlp-main.676/).

**Meeus 2024 SoK impact** N/A.

## False Outcome (FO)
**Name** False Outcome probe.

**Concept** Keep the event shell intact but replace the critical outcome slot with a specific false value or false state, then test whether the model still behaves as if the original outcome were present. FO targets slot-level anchoring more directly than SR.

**Mechanism family** Counterfactual.

**Access requirement** Either; supports **all 6 fleet members**.

**Construct-validity rationale** FO is a candidate measure of **outcome-slot anchoring under near-constant surface form**. The mechanism is traceable: if the model has memorized a particular company-event-outcome association, a false slot in the same shell should be resisted or corrected disproportionately often. In a nomological network, FO should converge with Anchor Strength and exact-span extractability more than with NoOp sensitivity; if it converges only with Template Rigidity, it is probably just another surface detector. Failure modes are accidental truth of the injected false outcome, event-type asymmetry, and rewrite awkwardness; that means Editor-side lexical control matters as much as Stats-side calibration.

**Factor relevance** Cutoff Exposure: strong positive. Propagation Intensity: `event_burst` moderate positive; `historical_family_recurrence` strong positive because reusable shells invite slot-completion from prior patterns. Template Rigidity: strong positive. Entity Salience: `target_salience` moderate positive; `max_non_target_entity_salience` positive as a distraction confound. Anchor Strength: very strong positive, the key pairing. Disclosure Regime: plausible strong positive for formal disclosures because exact slots and numbers are canonical, but this is mechanism-level only. Session Timing: weak, with only a soft hypothesis that post-close disclosures will be more slot-stable.

**Bloc diversification** Primary bloc target: **1**, with an explicit construct-collapse risk: if FO correlates almost perfectly with Min-K-style scores, it is not adding enough new construct coverage.

**Ensemble compatibility** **Independent reporting**. If SR is also retained, FO and SR should be reported as a paired counterfactual family, not counted as two interchangeable "votes."

**Detector-level stratification fields (P5)** `false_outcome_acceptance_rate`; `slot_anchor_gap`. **EAS applies**: mask entities and re-run FO; useful for testing whether slot anchoring survives when company identity is removed.

**FinMem-NoOp specifics** Generation should be mostly **rule-based** off Thales event types plus slot schemas, with an LLM only used to smooth fluency and a validator to reject accidentally true or entailment-preserving edits. RAVEN-style novelty can check whether the model is copying the memorized original slot completion instead of adapting to the edited input.

**Thales dependency** Needs Thales event-type labels and entity normalization for high-quality slot editing.

**Compute budget estimate** Around `38,400` scored prompts for a single-pass six-model run.

**Key citations** [Yu et al. 2023](https://aclanthology.org/2023.emnlp-main.615/); [Counterfactual Memorization in Neural Language Models](https://arxiv.org/abs/2112.12938); [Cronbach & Meehl 1955](https://psychclassics.yorku.ca/Cronbach/construct.htm); [Freiesleben 2026](https://arxiv.org/abs/2603.15121).

**Meeus 2024 SoK impact** N/A.

## Semantic Reversal (SR)
**Name** Semantic Reversal probe.

**Concept** Minimally reverse the financially material direction or polarity of the CLS item and test whether the model/detector updates accordingly. SR asks whether the system is following the edited semantics or clinging to a cached original event script.

**Mechanism family** Counterfactual.

**Access requirement** Either; supports **all 6 fleet members**.

**Construct-validity rationale** SR is a candidate measure of **counterfactual overwrite resistance**. It is especially useful because it holds much of the lexical shell fixed while changing truth conditions, so it is a stronger discriminant against mere surface familiarity than Min-K-style methods. In MTMM terms, I would expect convergence with Cutoff Exposure and Anchor Strength, partial convergence with FO, and weaker convergence with NoOp. Main failure modes are unnatural reversals, unequal antonym availability across event types, and lexical artifacts that make some reversals easier than others.

**Factor relevance** Cutoff Exposure: strong positive. Propagation Intensity: `event_burst` moderate positive; `historical_family_recurrence` moderate positive through schema persistence. Template Rigidity: moderate positive, but if this becomes dominant SR has collapsed back to surface sensitivity. Entity Salience: `target_salience` moderate positive; `max_non_target_entity_salience` likely increases false persistence through distraction. Anchor Strength: strong positive. Disclosure Regime: plausible moderate positive for formal disclosures because regulated outcomes create stronger prior scripts, but no direct precedent. Session Timing: weak, with no real literature support.

**Bloc diversification** Primary bloc target: **0**.

**Ensemble compatibility** **Independent reporting**. Keep distinct from FO because SR tests polarity overwrite, FO tests slot anchoring.

**Detector-level stratification fields (P5)** `reversal_flip_rate`; `reversal_margin`. **EAS applies**: entity masking can reveal whether reversal failures are driven by company identity versus event semantics.

**FinMem-NoOp specifics** Use **rule-based antonym/event-operator maps** keyed by event type, with LLM-assisted cleanup only after the edit is structurally fixed. RAVEN-style overlap can be used on rationales to detect cases where the model simply reproduces the original cached continuation.

**Thales dependency** Needs Thales event-type labels for reliable reversal dictionaries; degraded operation without Thales is possible but much noisier.

**Compute budget estimate** Roughly `38,400` scored prompts for one six-model pass.

**Key citations** [Yu et al. 2023](https://aclanthology.org/2023.emnlp-main.615/); [Counterfactual Memorization in Neural Language Models](https://arxiv.org/abs/2112.12938); [Cronbach & Meehl 1955](https://psychclassics.yorku.ca/Cronbach/construct.htm); [Xiao et al. 2023](https://aclanthology.org/2023.emnlp-main.676/).

**Meeus 2024 SoK impact** N/A.

## Extractable Span Recovery (ESR)
**Name** Extractable Span Recovery.

**Concept** Mask a critical span such as ticker, amount, regulator, date, counterparty, or outcome phrase and test whether the model can recover it from partial context across multiple prompts/samples. This is a narrow detector for extractable memorization.

**Mechanism family** Extraction.

**Access requirement** Either; supports **all 6 fleet members**, though hosted aligned models should be treated as secondary because refusals and guardrails will depress yield.

**Construct-validity rationale** ESR measures the most defensible narrow construct in the set: **extractable/verbatim-or-near-verbatim recall of specific case content**. It is underinclusive for memorization in general, but that is a feature for construct validity because the failure mode is obvious. Convergent evidence should come from Anchor Strength, Cutoff Exposure, and FO; discriminant evidence should be weak correlation with NoOp. Failure modes are prompt sensitivity, alignment refusals, and the fact that some recovered spans may come from public schema completion rather than case memory.

**Factor relevance** Cutoff Exposure: very strong positive. Propagation Intensity: `event_burst` strong positive; `historical_family_recurrence` moderate positive when the slot itself recurs. Template Rigidity: moderate positive. Entity Salience: `target_salience` strong positive; `max_non_target_entity_salience` should usually hurt target-span recovery through cue competition. Anchor Strength: very strong positive. Disclosure Regime: plausible positive for formal disclosures because exact slots are stable, but no benchmark-literature precedent. Session Timing: weak positive at most.

**Bloc diversification** Primary bloc target: **1**, with explicit collapse risk flagged; ESR is valuable because it measures **extractability**, not just likelihood, but it still lives close to the repetition/surface bloc.

**Ensemble compatibility** **Independent reporting**. ESR is best used as a criterion-style detector showing that some cases are not merely "high scoring" but actually recoverable.

**Detector-level stratification fields (P5)** `extractable_span_density`; `recovery_consistency`. **EAS applies only conditionally**: use it when the extracted span is not the masked entity itself; otherwise anonymization destroys the task and becomes tautological.

**Thales dependency** Can run on raw CLS text; gains from entity normalization and event labels when selecting spans.

**Compute budget estimate** Expensive: with 3 prompt variants and 3 samples, roughly `3,200 x 6 x 9 = 172,800` generations.

**Key citations** [Carlini et al. 2020](https://arxiv.org/abs/2012.07805); [Nasr et al. 2023](https://arxiv.org/abs/2311.17035); [Zhou et al. 2023](https://arxiv.org/abs/2308.15727); [Cronbach & Meehl 1955](https://psychclassics.yorku.ca/Cronbach/construct.htm).

**Meeus 2024 SoK impact** N/A.

## As-of Date Gating (ADG)
**Name** As-of Date Gating.

**Concept** Ask the same model to answer under explicit "as of" dates before and after the event and score whether it properly withholds or changes knowledge across the boundary. This is a temporal conditioning detector rather than a disagreement detector.

**Mechanism family** Temporal-cutoff-conditional.

**Access requirement** Either; supports **all 6 fleet members**.

**Construct-validity rationale** ADG is a candidate measure of **temporal gating of recalled knowledge**. It is valuable because it tests a different mechanism from CMMD: not cross-model cutoff structure, but within-model compliance with chronology. In a nomological network, it should converge with Cutoff Exposure and partially with CMMD, but it should diverge from ESR and Min-K where those detectors react to familiarity even when the prompt explicitly says the knowledge should not yet be available. Failure modes are chronology reasoning weakness and instruction-following variance; Wongchamcharoen-Glasserman makes this failure mode very concrete, which is good for interpretability.

**Factor relevance** Cutoff Exposure: very strong positive. Propagation Intensity: `event_burst` and `historical_family_recurrence` weak-to-moderate positive because famous repeated events may "bleed through" chronology gates. Template Rigidity: weak positive. Entity Salience: `target_salience` moderate positive because famous entities make leakage harder to suppress; `max_non_target_entity_salience` adds chronology confusion. Anchor Strength: moderate positive. Disclosure Regime: plausible positive because formal disclosures have crisp publication dates, but this is mechanism-level only. Session Timing: the strongest secondary pairing here, because pre_open/intraday/post_close boundaries create real chronology ambiguity.

**Bloc diversification** Primary bloc target: **0**.

**Ensemble compatibility** **Independent reporting**. ADG should be interpreted alongside CMMD, not fused with it.

**Detector-level stratification fields (P5)** `asof_violation_rate`; `cutoff_changepoint_days`. **EAS applies** but is lower priority; masking can test whether chronology failures are company-name driven.

**Thales dependency** Raw CLS text works immediately; session labels improve analysis.

**Compute budget estimate** About `38,400` prompt evaluations for before/after gating across six models.

**Key citations** [Dated Data](https://arxiv.org/abs/2403.12958); [Do LLMs Understand Chronology?](https://arxiv.org/abs/2511.14214); [Merchant & Levy 2025](https://arxiv.org/abs/2512.06607); [Cronbach & Meehl 1955](https://psychclassics.yorku.ca/Cronbach/construct.htm).

**Meeus 2024 SoK impact** N/A.

## Calibrated Tail Surprise (CTS)
**Name** Calibrated Tail Surprise.

**Concept** Use Min-K%++-style tail likelihood, but calibrate it with divergence-based token-frequency correction so common Chinese boilerplate does not automatically look memorized. This is the one surface baseline I would keep.

**Mechanism family** Surface-form / MIA-adjacent.

**Access requirement** **White-box** in current project reality; supports **Qwen 2.5-7B-Instruct, GLM-4-9B-0414, Qwen3-14B**.

**Construct-validity rationale** CTS is a candidate measure of **surface-conditioned distributional familiarity**, not membership in the strong legal/privacy sense. That distinction matters. Its value is as a transparent, narrow baseline that should converge with Template Rigidity and repetition factors, while diverging from CMMD/NoOp if those are really measuring different mechanisms. Failure modes are serious and well known: construct underrepresentation for semantic memorization, construct-irrelevant variance from tokenization and common boilerplate, and post-hoc MIA identification problems if one overinterprets the score as "training-data membership."

**Factor relevance** Cutoff Exposure: strong positive. Propagation Intensity: `event_burst` strong positive; `historical_family_recurrence` strong positive but partly construct-irrelevant because generic templates inflate familiarity. Template Rigidity: very strong positive, by design. Entity Salience: `target_salience` mild-to-moderate positive; `max_non_target_entity_salience` can also raise the score spuriously through familiar co-mentioned entities. Anchor Strength: moderate positive. Disclosure Regime: plausible weak positive for formal disclosures via boilerplate reuse, but this is mechanism-only. Session Timing: very weak, no direct literature support.

**Bloc diversification** Primary bloc target: **1**, with explicit construct-collapse risk. This detector is useful only if it is the **only** surface-heavy baseline or at most one of two.

**Ensemble compatibility** **Independent reporting only**. Do not use as the backbone of an MCS-style ensemble in Step 1.

**Detector-level stratification fields (P5)** `calibrated_tail_score`; `tail_mass_k`. **EAS applies**: replace entities with placeholders and measure delta score; this is useful, but tokenization changes in Chinese placeholders can themselves move the score, so compare against matched placeholder controls.

**Thales dependency** Can run degraded without Thales; gains from entity normalization and cluster metadata for analysis.

**Compute budget estimate** Cheap relative to extraction: about `3,200 x 3 = 9,600` logprob passes for one run on the local white-box models.

**Key citations** [Min-K%](https://arxiv.org/abs/2310.16789); [Min-K%++](https://arxiv.org/abs/2404.02936); [PatentMIA / divergence calibration](https://arxiv.org/abs/2409.14781); [Meeus et al. 2024](https://arxiv.org/abs/2406.17975); [Xiao et al. 2023](https://aclanthology.org/2023.emnlp-main.676/).

**Meeus 2024 SoK impact** High. The NLP-lens reply is not to "defeat" Meeus, but to **accept the restriction**: CTS should be framed as a surface-familiarity baseline, not a validated membership estimator. No shadow-model ensemble, no strong membership language, and no primary claim resting on CTS alone.

**NLP-Lens Synthesis**
**Top 3 construct-validity picks**
- **1. CMMD** because the nomological argument is strongest: the mechanism is externally indexed by model chronology, predicted relations are directional, and failure modes are interpretable.
- **2. FinMem-NoOp** because it gives the cleanest negative-control evidence against construct-irrelevant context sensitivity, especially the competing-entity distraction path.
- **3. Extractable Span Recovery** because it captures a narrow but exceptionally traceable construct; it is underinclusive, but that underinclusiveness is analytically honest.

**Gaps if only NLP-lens candidates are used**
- The five mechanism families are covered, but **surface-form is intentionally under-covered**; that is a feature, not a bug, given the collapse risk.
- Quant/Stats should contribute thresholding policy, uncertainty estimation, missingness handling for refusals, MTMM analysis, and one-factor-collapse stress tests.
- Editor should contribute rewrite naturalness controls for SR/FO/NoOp and a style-preservation protocol for CLS telegraph edits.

**FinMem-NoOp design answer**
- Recommendation: **rule-based generation with LLM validation**, not free-form LLM generation.
- Concrete rule: insert one same-window clause from a different normalized entity, different cluster, and non-entailing event; keep clause length and CLS style controlled.
- Fallback: LLM-assisted generation only for cases where rule-based retrieval fails, plus automatic rejection checks for leakage, entailment, and target overlap.

**Entity-Anonymization Sensitivity answer**
- Yes, include EAS as a **detector-level field**, but split it into `target-mask delta` and `non-target-mask delta`; a single blended EAS score is too coarse.
- Strongly applicable: CMMD, FinMem-NoOp, FO, SR, CTS, ADG.
- Conditionally applicable: ESR only when the extracted span is not the masked entity.
- Main risks: Chinese placeholder tokenization artifacts, accidental task destruction, and conflating target salience with competitor distraction.

**Questions for Quant / Stats / Editor before Step 2**
- Quant/Stats: Are detector outputs staying continuous, or will Step 2 force thresholds? Thresholding too early will throw away validity signal.
- Quant/Stats: Will the case×model structure of Cutoff Exposure be modeled explicitly as repeated measures, or flattened into per-case summaries?
- Editor: What is the acceptance protocol for SR/FO rewrite naturalness by event type, and who owns the antonym/slot lexicon?
- Editor: For NoOp, what maximum clause length and discourse-position constraints preserve CLS style without making the edit trivially ignorable?
