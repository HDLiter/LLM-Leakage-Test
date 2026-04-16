---
role: NLP / methodology
lens: R5A Step 2 detector-pool review
generated: 2026-04-15
author: Codex
inputs:
  - refine-logs/reviews/R5A_STEP1/R5A_STEP1_SYNTHESIS.md
  - refine-logs/reviews/R5A_STEP1/R5A_DEFAULTS.md
  - refine-logs/reviews/R5A_STEP1/nlp_lens.md
  - refine-logs/reviews/R5A_TEMPORAL_CUE/R5A_TEMPORAL_CUE_SYNTHESIS.md
  - refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_REVIEW_R2_SYNTHESIS.md
---

# R5A Step 2 - NLP / Methodology Review

My Step 1 priors largely survive, but with two important updates after the temporal-cue and fleet sessions: (1) D4 should now be treated as one temporal-gating family slot with D4b primary and D4a diagnostic, and (2) the fleet redesign materially improves the construct validity of D1/D2/D3 by adding same-cutoff and size-falsification contrasts. The biggest remaining measurement risk is still Chinese edit admissibility for the counterfactual family.

### 1. Tension Rulings (T1-T7)

**T1. EAD standalone vs field only - MODIFY.**  
I do not endorse the default's implicit symmetry between the two roles. At collection time, yes, compute both the standalone D7 protocol and detector-level masking deltas. At the construct level, however, EAD is field-first and detector-second. The same masking intervention should not be counted twice as if it were two independent traits. From a Cronbach-Meehl / MTMM perspective, the masking method is shared method variance unless the standalone D7 output shows non-redundant moderation structure relative to the field form. My position is: keep target-mask and non-target-mask deltas everywhere they are admissible; promote D7 as a standalone reserve detector only if pilot data show it is not just a repackaging of those fields.

**T2. SR/FO paired vs separate - AGREE.**  
One detector slot with two preserved sub-measurements is the right structure. SR and FO do not test the same thing: SR is polarity-overwrite resistance, FO is slot-anchor persistence. Their expected nomological relations differ, so collapsing them to one scalar too early would erase validity evidence. But counting them as two headline detectors would overstate family breadth and make the paper look like a perturbation suite. Keep them together in one family slot and report their divergences explicitly.

**T3. PCSG standalone vs fold into Min-K++ - MODIFY.**  
I do not support treating D2 as a fully separate main-text detector by default. Stats is right that the paired contrast has a stronger identification story than raw D3, and the fleet review strengthens that further via same-tokenizer temporal pairs and same-cutoff falsification. But D2 and D3 still share the same basic surface/logprob method family. From a construct-validity lens, that is one trait family with two readouts, not two independent traits. Keep D2 in the active pool, but as a surface-family sub-measurement or reserve unless it demonstrates clear discriminant value beyond D3.

**T4. ADG - MODIFY.**  
The opening default deferred D4; the temporal session resolved the right shape. I support one D4 family slot with D4b (misdirection) primary and D4a (contradiction) secondary/diagnostic. This preserves the construct I argued for in Step 1: within-model temporal gating is not the same as CMMD's cross-model chronology signal. D4b is the cleaner estimand because it isolates temporal gate compliance rather than instruction-hierarchy conflict. D4a remains useful only as a diagnostic with a matched-date control.

**T5. Extraction main text vs reserve - AGREE.**  
I still support main-text inclusion, but only in the narrowed role already proposed in the defaults: corroborative hard-edge evidence, not an omnibus statistical workhorse. D8's underinclusiveness is a validity strength. It gives the paper at least one detector whose failure mode is obvious and whose positive cases are maximally interpretable. If yield is genuinely trivial in pilot, demotion is fine, but the current default is methodologically sound.

**T6. Debias Delta - AGREE.**  
Drop it. It is mitigation-first, not measurement-first, and its construct is too entangled with intervention efficacy to justify detector status when the temporal family already contains D1, D2/D3, and D4. Keeping it would add engineering burden without improving the nomological network.

**T7. RAVEN - AGREE.**  
Drop it as a standalone detector. Novelty-gap behavior is too easy to collapse into Template Rigidity, stylistic novelty, or alignment behavior. If RAVEN-style overlap checks are useful, use them as QC diagnostics inside D5/D6 editing pipelines, not as an independent detector claim.

### 2. Per-Detector Verdicts

**D1 CMMD - KEEP.**  
The default success condition is the right one: cutoff-ordered disagreement should appear on likely-leakage cases and disappear on clearly post-cutoff placebo cases. The stated failure mode is also right: architecture/capability drift can masquerade as chronology. The fleet review improves this detector substantially because the GLM-4-9B <-> GPT-4.1 same-cutoff pair and the Qwen size-falsification pair give concrete discriminant checks. D1 remains the strongest main-text detector.

**D2 PCSG - RESHAPE.**  
The success condition in the defaults is correct, especially the requirement that the gap survive placebo and model-pair changes. The failure mode is also correctly identified as baseline miscalibration. My reshape is architectural, not eliminative: D2 should live as a secondary readout within the surface family, or as a reserve detector, until it proves that it is not just D3 with better normalization. Strong identification does not by itself make it a separate construct.

**D3 Min-K++ / CTS - KEEP.**  
The defaults frame this correctly: success is reduced dependence on Template Rigidity after calibration, and failure is collapse into boilerplate familiarity. I would keep one surface detector in the main text precisely because it gives the rest of the pool a discriminant baseline. The Meeus restriction still stands: D3 is a surface-familiarity baseline, not a validated membership estimator. Thinking-off and same-tokenizer pairing from the fleet review are essential, not optional.

**D4 ADG - RESHAPE.**  
The defaults held D4 out, so the temporal session supersedes that omission. Keep D4 as one family slot, with D4b primary and D4a diagnostic. Success for D4b is a clean within-model temporal-gating effect that cannot be reduced to generic instruction-following; failure is exactly that confound, especially for D4a. D4 should stay in the pool because without it there is no within-model Bloc 0 detector.

**D5 SR/FO - KEEP.**  
The default success condition is exactly the admissibility criterion: Chinese perturbations must be natural, locally controlled, and target-clean on audit. The dominant failure mode is also exactly right: if the edits read as malformed CLS Chinese, the detector measures edit rejection rather than memorization. Keep D5 as one detector slot with SR and FO reported separately. Do not collapse to a single CFI scalar unless pilot data show not just high correlation, but loss of differential moderation by Cutoff Exposure vs Anchor Strength.

**D6 NoOp - RESHAPE.**  
I agree with the default success condition and dominant failure mode. The reason I still reshape it is conceptual: D6 is best understood as a negative-control companion inside the counterfactual family, not as a co-equal headline detector. It is indispensable for validity if the clause bank is admissible, but inadmissible if target irrelevance cannot be shown. My recommendation is to keep the measure, but present it as the family's falsification arm and demote it automatically if the rule-based clause bank or audit pass rate fails.

**D7 EAD - RESHAPE.**  
The default success condition is the right one: target-mask and non-target-mask deltas must be separable, and masking should not just proxy information destruction. The failure mode is also correctly stated. My reshape is to make D7 field-first and reserve-standalone, with matched placeholder controls to guard against Chinese tokenization artifacts. This detector is valuable because it decomposes identity-cue dependence, but its cleanest contribution is as a cross-detector validity probe.

**D8 Extraction - KEEP.**  
The default success condition fits the detector's real role: a few percent exact or near-exact recovery is enough if it yields concrete, inspectable cases. The stated failure mode is also right: refusal and paraphrase behavior can zero out the detector without proving absence of memorization. Keep D8 in the main text as a criterion-style hard-edge anchor, with refusal rates reported explicitly and no attempt to make it carry the main confirmatory burden.

**D12 Schema-Completion - RESHAPE.**  
The default success condition and failure mode are well chosen, but D12 is not ready as written. It should be recast around whichever Bloc 3 label space survives freeze, ideally Event Type plus Modality-style schema families rather than the current binary Disclosure Regime placeholder. Keep it only as an exploratory reserve probe unless it shows partial independence from D3. Otherwise it is just another way of measuring formal-boilerplate familiarity.

### 3. D11 Temporal Dose-Response

**RESHAPE.**  
D11 should remain a temporal sensitivity protocol, not a standalone detector. I agree with the temporal session consensus on that point.

**Primary backend:** D1 CMMD. This is the cleanest test of the interaction between a text-side retrieval key and a model-side cutoff opportunity.  
**Optional secondary backend:** D5-FO, exploratory only. FO is a better second choice than Min-K++ because it tests whether temporal-anchor removal changes resistance to a controlled semantic edit rather than merely changing token surprisal. I would not add a second backend until CMMD shows signal.

**Non-temporal deletion control requirement:** absolute must-have. The control edit should be matched on character length, syntactic role, and discourse position, and should be human-audited as non-temporal and non-event-defining. If temporal deletion and matched non-temporal deletion move detector scores equally, there is no temporal-anchor claim. I would also require an adjunct-type coverage audit before any confirmatory use; if removable temporal cues are too sparse, D11 stays observational/exploratory.

### 4. Bloc 3 Coverage

**Option 3 + D12.**  
I would not accept the gap outright. Pure interaction-menu coverage is the necessary baseline, but by itself it is weak for the very bloc already identified as the most under-powered and internally correlated. At the same time, I would not promote a raw D12 to main text while the Bloc 3 label space is still unstable. The right compromise is:

1. Use Option 3 as the guaranteed baseline for all retained detectors.
2. Keep a reshaped D12 as an exploratory reserve probe.
3. Define D12 against the frozen Bloc 3 ontology, preferably Modality/Event Type schema families rather than the current Disclosure Regime placeholder.

From a construct-validity perspective, this avoids both extremes: no silent acceptance of a source-bloc hole, but no premature commitment to a detector whose trait definition is still moving.

### 5. Pool Architecture

**Architecture A.**  
This is the better fit to the actual measurement structure. Several current "detectors" are not independent traits:

- D2 and D3 are one surface/logprob family with two readouts.
- D4a and D4b are one temporal-gating family.
- D5 and D6 are one counterfactual family with positive and negative-control arms.
- D7 is primarily a field layered onto other detectors.
- D11 is a protocol, not a detector.

Architecture B would encourage false independence and double-counting of method variance. Architecture A lets the paper stay within 4-5 headline slots without pretending that every operationalization is a new construct. My preferred slot structure is:

1. Cross-model temporal disagreement: D1
2. Surface familiarity family: D3 primary, D2 secondary
3. Within-model temporal gating: D4b primary, D4a diagnostic
4. Counterfactual family: D5 primary, D6 negative control, D7 field overlays
5. Extraction: D8

### 6. Open Questions

**Q1. Minimum Chinese counterfactual-edit audit standard.**  
The admissibility floor is not "looks plausible." It needs four checks: natural CLS style, preservation of all non-target propositions, correctness of the intended target change, and absence of accidental truth/entailment leakage. I would require event-type-stratified audit, not a pooled average only, because Chinese editability is highly event-type dependent. A detector family that cannot clear roughly 85% audited pass rate on the editable subset should not be used as contamination evidence.

**Q2. Can NoOp be rule-based with explicit proofs of target irrelevance?**  
Yes, but "proof" here means auditable exclusion logic, not formal proof. A NoOp clause is admissible only if it is retrieved from the same time window, linked to a different normalized entity, from a different event cluster, and screened for non-entailment against the base article. The clause should carry provenance metadata so failures are traceable. If this retrieval-and-screening path cannot cover a large majority of pilot cases, D6 should be reserve-only or dropped.

**Q3. Who owns SR/FO rewrite naturalness and the antonym/slot lexicon?**  
Joint ownership. NLP should own the event-type-specific edit grammar: which slots are editable, which operators are reversible, which event types are ineligible, and what counts as semantic preservation. Editor should own the CLS style rubric and final pass/fail review standard. The acceptance protocol should be two-stage: deterministic edit script first, then fluency repair only within the allowed edit envelope, then human audit. If a clean operator or slot ontology does not exist for an event type, skip that case rather than force an LLM rewrite.

**Q4. NoOp clause length and discourse-position constraints.**  
Use a single medial clause, comma-bounded where possible, roughly 8-16 Chinese characters excluding entity strings and numerals, and never more than about 20-25% of the article body. Do not place it in sentence-initial lead position, headline position, or terminal takeaway position. Very short CLS flashes should simply be marked ineligible for NoOp. The goal is "visible but not structurally dominant."

**Q5. If Disclosure Regime is replaced by Modality, what survives?**  
Most detector-factor arguments survive if they are rewritten from binary provenance language to schema/formality language. D3, D8, and a reshaped D12 arguably get stronger under Modality because the textual schema distinctions are richer. D5-FO and D6 also survive, but the wording should shift from "formal disclosure vs commentary" to "tight-schema modalities vs interpretive modalities." D1 and D4 are more weakly tied to Bloc 3; any source-type claims there should remain exploratory. D7 is largely orthogonal.

**Q6. Known-outcome coverage for FO.**  
From an NLP lens, FO should be restricted to event types with a clean slot ontology and verifiable gold outcomes. If those conditions hold only for a subset, that is acceptable; FO then becomes a narrower but cleaner detector. Broad but noisy coverage is the worse trade-off.

**Q7. Continuous outputs vs thresholds.**  
Keep detector outputs continuous through the main validity analysis. Thresholds are acceptable only for descriptive illustrations or operational appendix summaries. Early binarization throws away the very variance needed for nomological-network testing.

**Q8. Case x model structure vs flattened summaries.**  
The case x model structure should be modeled explicitly. Flattening too early erases the mechanism for D1, D2, D3, D4, and D11. From a validity lens, repeated-measures structure is part of the construct, not a nuisance to average away.

**Q10. Can Thales produce deterministic spans, masks, and counterfactual edits with auditable pass rates?**  
Partially. My current answer, based on project docs rather than the uncurated Thales logs, is:

- Deterministic target spans: probably yes for explicit company, regulator, ticker, and named-person mentions once normalization rules are frozen.
- Deterministic competitor spans: yes at the named-entity level, weaker for implied or discourse-level competitors.
- Deterministic placebo masks: yes, if masking is defined over frozen span classes with matched placeholder controls.
- Deterministic counterfactual edits: no, not end-to-end in fluent Chinese CLS. What is realistic is deterministic proposal generation plus auditable validation and selective fluency repair.

So the right promise is not "fully deterministic edits." It is "deterministic edit templates and span contracts, plus auditable pass rates with explicit rejection reasons." That is enough for R5A conceptual closure, but the counterfactual family remains an R5B execution risk until the Thales track is actually frozen.

**Questions I would leave primarily to other lenses:** Q9, Q11, Q12 are mainly Quant / Stats / Editor.

### 7. Proposed Main-Text Shortlist

Under **Architecture A**, my preferred main-text shortlist is five family slots:

1. **D1 CMMD.** Strongest primary detector; best externally anchored chronology construct.
2. **Surface family: D3 CTS as the primary readout, with D2 PCSG retained only as a paired secondary readout if placebo-stable.** This gives one surface baseline without letting the paper collapse into a logprob story.
3. **D4 ADG family: D4b primary, D4a diagnostic.** Necessary to keep within-model temporal gating distinct from cross-model chronology.
4. **Counterfactual family: D5 SR/FO as the main positive probe, D6 NoOp as the negative-control arm, D7 EAD as field overlays rather than a co-equal slot.** This is where the richest construct-validity evidence lives if edit quality is admissible.
5. **D8 Extraction.** Narrow but maximally interpretable hard-edge anchor.

**Reserve detectors:**

1. **D7 EAD standalone.** Promote only if the standalone signal is clearly non-redundant relative to the field form.
2. **D12 Schema-Completion.** Promote only if Bloc 3 labels freeze and the detector shows partial independence from D3.

If the paper is forced down to four headline slots, I would compress the surface family to D3-only and keep D2 in reserve.

### 8. Blocking Issues

These are the Step 2 issues that would block a clean R5A closure for me:

1. **No frozen admissibility gate for Chinese counterfactual edits.** If D5/D6/D7 stay in the pool, Step 2 needs to write down the audit rubric, pass threshold, and automatic demotion rule for failed edit quality. Without that, the counterfactual family is not a defined construct.
2. **No explicit hierarchy for EAD.** If D7 is left in a vague "both" state without field-first vs standalone-reserve clarification, the project risks double-counting one masking method as two detectors.
3. **D11 retained without the non-temporal deletion control and adjunct-type coverage audit.** Without those, D11 measures generic content deletion, not temporal-anchor dependence.
4. **D12 promoted before Bloc 3 ontology freeze.** A Schema-Completion detector cannot target a moving construct. If D12 stays reserve-only, this is not a blocker; if it is promoted, it is.
5. **No commitment to continuous outputs and explicit case x model handling.** This is partly a Stats implementation issue, but it is also a validity issue. Thresholding or flattening too early would materially damage the detector constructs.

Execution dependencies such as checkpoint pinning and full Thales integration are R5B gates, not R5A conceptual blockers, as long as the shortlist records the fallback assumptions above.
