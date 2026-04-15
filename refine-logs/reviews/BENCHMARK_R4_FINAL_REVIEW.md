# BENCHMARK R4 — Cold Reader Review (post-closure)
**Date:** 2026-04-13
**Reviewer:** Codex (senior NLP/ML researcher, no prior R1-R4 context)
**Reasoning effort:** xhigh
**Inputs:** BENCHMARK_R4_FINAL_SYNTHESIS.md + docs/DECISION_20260413_mvp_direction.md v4
**Purpose:** Outside-in critique to catch what deeply-engaged participants stopped seeing

---

## 1. Comprehensibility check

Partly. From the documents alone, I can infer that FinMem-Bench is intended to study memorization on Chinese financial news text from CLS, using case-level factors that are hypothesized to make memorization more or less likely. But I still cannot state the benchmark's primary dependent variable in one clean sentence, because R4 locks factor design before R5 defines the memorization detector layer. The docs alternate between "benchmark," "audit substrate," "factor taxonomy," and "future empirical paper," which leaves the core object slightly unstable.

What is clear:
- The unit is an event-cluster-derived canonical CLS article.
- The benchmark is meant for LLM memorization analysis, not generic forecasting.
- Decision 5 is clean: measure on the exact CLS text, not substituted public-domain text.

What remains unclear or under-explained:
- Who the benchmark is for. The intended reader oscillates between EMNLP memorization reviewers and finance/audit readers. The "venue drift" concern is acknowledged, but the document never settles the audience.
- What exactly a "factor" is. Some are case attributes, some are case×model attributes (`cutoff_gap_days`), some are sampling-design choices (`Event Phase`), and some are controls (`Text Length`).
- Why several factors were selected. Propagation, Cutoff, and Template are reasonably motivated. Session Timing, Target Scope, Structured Event Type, and Disclosure Regime are not justified at the same level.
- Several project-internal terms are cold-reader hostile: `CLS`, `Thales`, `alpha-bridge`, `档位 2 偏 1`, `CMMD`, `MIA`, `Min-K%`, `canonical`, `prior_family_count_365d`.

Cold-reader verdict: the project is understandable at the 70% level, but not yet at the "I could explain this benchmark to a reviewer in two sentences" level.

## 2. Internal consistency check

The synthesis and v4 mostly agree on the big picture. The real problem is that v4 still contains several stale pre-R4 or v3-era statements that were not updated.

Main inconsistencies:
- `Decisions locked in v3` is stale. D13 still says `3-5` interaction pairs, while Principle P4 says `5-7`. D14 still says a `50-case` anchor experiment, while Principle P3 now says `150`.
- Decision 3 / Decision 6 / Open Tracks still say canonical selection is deferred to the Thales-joint track. Principle P2 later says the Event Phase rule **replaces** the old canonical rule and is binding. Both cannot be true.
- `What R4 can assume` still says `~1,000–1,500` clusters total. Later the document says the working reference is `3,200 gross`, `~2,560 scorable`.
- `What R4 should produce` still says `4–6 candidate factors`. The actual output is a 12-factor shortlist.
- The closure language overstates completion. "R4 closed with no blockers" is too strong when exact factor algorithms for several shortlisted factors are explicitly deferred.

So: no fatal synthesis-v4 contradiction, but v4 needs a cleanup pass. Right now it reads like a living document with old instructions left in place after the decision changed.

## 3. Construct validity stress test

1. **Propagation Intensity**: The name overclaims. The operationalization mixes two different constructs: same-event burst duplication (`cluster_size`) and historical event-family recurrence (`prior_family_count_365d`). That is not one thing. The robustness companion `surface_template_recurrence` is closer to surface reuse than "propagation."

2. **Cutoff Exposure**: Reasonable idea, but the measure is cutoff timing, not exposure. Exposure is a latent inclusion probability. A signed day-gap is only a proxy, and it is model-specific. This should be framed as a case×model variable, not a pure case factor.

3. **Anchor Strength**: At present this is not a validated factor; it is a contest between three proxies. Reliability-based rubric selection is not construct validation. You may pick the easiest rubric to agree on, not the rubric that best measures anchorability.

4. **Entity Salience**: This is two constructs under one label: target prominence and competing-entity distraction. Those are not the same mechanism. Bundling them as one "factor" muddies interpretation.

5. **Target Scope**: This is a coarse entity-class label, not a mechanism. Its hypothesized effect seems to run through prominence, tradability, and disclosure norms, all of which appear elsewhere.

6. **Structured Event Type**: As written, this is a taxonomy, not a factor with a directional hypothesis. Unless categories are tied to a mechanism, this functions more like a stratifier than an explanatory construct.

7. **Disclosure Regime**: Potentially useful, but likely measures source provenance and institutional writing style as much as anything else. It also overlaps heavily with Event Type and Event Phase.

8. **Template Rigidity**: The metric measures surface similarity to prior texts, not "rigidity" in any strong linguistic sense. It may be driven by outlet boilerplate, repeated named entities, or standard finance phrasing.

9. **Tradability Tier**: Plausible as an extra-corpus proxy for market prominence, but the path to memorization is indirect. Since it is only defined for company targets, it behaves more like a subset covariate than a benchmark-wide factor.

10. **Session Timing**: The mechanism is weakly argued. It clearly matters for markets. It is not yet convincing that it matters for memorization except through other variables like urgency, disclosure regime, or propagation.

11. **Text Length**: Fine as a control. No major construct problem if it stays explicitly a nuisance variable.

12. **Event Phase**: Interpretation is contaminated by design. Once you randomly assign a target phase and sample by it, the observed phase distribution is partly imposed by the benchmark, not merely measured from the world.

Overall construct problem: the shortlist collapses into three latent blocs more than the documents admit.
- Repetition/surface reuse: Propagation, Template Rigidity, Reprint.
- Prominence/attention: Entity Salience, Target Scope, Tradability.
- Institutional stage/source: Event Type, Disclosure Regime, Event Phase, Session Timing.

That is not automatically bad. It is bad if the paper later presents these as many independent axes of evidence.

## 4. Methodology principles audit

**P1: Extra-corpus signal principle**

Not clearly satisfied from the active 12-factor shortlist. Clear extra-corpus factor: `Tradability Tier`. Arguable extra-corpus factor: `Cutoff Exposure`, if model-cutoff metadata counts. Reserve-only extra-corpus candidate: `Reprint Status`. But `prior_family_count_365d` is corpus-internal as written, not extra-corpus. This principle needs an explicit per-factor audit table or it is not checkable.

**P2: Event Phase two-stage sampling**

Not operationally complete. Missing pieces:
- Is phase assignment uniform over the four phases?
- What happens statistically when no article matches the assigned phase?
- Are rejected clusters resampled, or does the target population become "clusters containing the assigned phase"?
- How are ambiguous articles labeled?
- What are the tie-breakers for simultaneous earliest items?
- If phase availability correlates with event type or prominence, how is that selection bias handled?

This rule is promising, but not yet executable.

**P3: Anchor outcome-blind experiment**

Defensible as a pilot reliability screen, not yet as a definitive construct-selection protocol. The main issues:
- `n=150` may be enough for rough screening, but the claimed `±0.05` CI width is asserted, not demonstrated.
- The decision rule should compare **paired bootstrap differences in α**, not just separate α values with a hard `0.05` heuristic.
- One human rater is too thin if the experiment is supposed to support validity claims rather than internal triage.
- High agreement does not prove the rubric measures anchor strength.

**P4: Interaction menu**

This closes the omission loophole, not the analytic-flexibility loophole. You can still vary detector, model, horizon, coding, subset definition, and effect summary. Also, one listed item is not a clean 2×2 interaction at all: `target_salience × propagation_intensity | target_salience=low` is a subgroup diagnostic.

**P5: Detector-dependent factors are R5 territory**

Conceptually clean, operationally leaky. Several current factors already depend on unresolved model or pipeline choices, and R5 will add detector-specific fields anyway. The boundary is good as a planning fiction, but it is not a hard wall.

## 5. Risks audit

**R1: Shared annotation dependence**

Mitigation is not sufficient. A dependency graph and ontology freeze are good hygiene. The cluster-free robustness score helps for one repetition-related variable. It does not solve the deeper problem that multiple major factors still inherit the same clustering/entity/event-type backbone. The document is declaring mitigation earlier than the evidence supports.

**R2: Major-entity prominence correlation bloc**

Current mitigation is weak. Joint modeling is disclosure, not resolution. If the prominence bloc is strong, coefficients become unstable and interpretations become conditional and fragile. The tail-entity diagnostic is a useful addition, but it is not enough to separate propagation from prominence on its own.

**R3: Anchor operationalization must be outcome-blind**

This is the best-handled of the three risks. The outcome-blind rule genuinely reduces a major p-hacking channel. But it still does not establish construct validity, and the one-human design is thin. So: partially mitigated, not solved.

## 6. Unstated assumptions

- The CLS version of the text is a meaningful proxy for what the target models actually saw during training.
- Article timestamps and model cutoff dates are accurate enough to support Cutoff Exposure and Session Timing without large misclassification.
- The deferred Thales clustering/entity pipeline will be stable and high-quality enough that downstream factor analyses are trustworthy.
- One canonical article can stand in for event-level exposure without losing the key memorization signal.
- Different detector families and model access regimes will still support one coherent "memorization benchmark" narrative rather than fragmented detector-specific stories.

## 7. R5 readiness

R5 can start only in a limited sense. It can start as a detector landscape and feasibility round. It cannot yet start as a clean final-lock round.

What is ready:
- Survey detector families.
- Decide white-box vs black-box framing.
- Check model availability for CMMD.
- Define which detectors can run on raw CLS text now.

What is not ready:
- Final factor-detector mapping for Thales-dependent factors.
- Strong prioritization of time-aware detectors while D2/D4 remain unresolved.
- FinMem-NoOp design, which still needs generation rules and QA logic.
- Clean benchmark-wide treatment of case×model variables like Cutoff Exposure.

My recommendation: explicitly split R5 into `R5A conceptual shortlist` and `R5B executable shortlist after dependency gates`.

## 8. The biggest single risk

The single most likely failure mode is **construct collapse into a prominence/repetition proxy benchmark**.

In plain terms: the benchmark may end up "showing" that memorization is stronger for high-propagation, salient, tradable, templated cases and interpret that as multiple converging factors. But those may all be manifestations of one latent thing: high-profile, repeatedly worded coverage of major firms in a small finance-news ecosystem. If detector outputs rise on that bloc, the benchmark could end up validating sensitivity to prominence, boilerplate, and corpus reuse rather than memorization per se. That is the most dangerous failure because it would produce a clean-looking empirical story that is substantively wrong.

## 9. Concrete revision proposals

1. Replace the current high-level opening in v4 with one sentence that defines the dependent variable: "FinMem-Bench evaluates whether memorization detectors assign higher memorization scores to CLS financial texts with hypothesized exposure or recallability features, at the case or case×model level." Because right now the benchmark's target construct is never stated cleanly.

2. Replace the stale `What R4 should produce` section with post-R4 language describing the actual 12-factor outcome. Because it still reads like a pre-R4 instruction sheet.

3. Replace D13 and D14 in `Decisions locked in v3` with the v4 values: `5–7` interaction pairs and a `150-case` anchor study. Because the current table contradicts Principles P3 and P4.

4. Replace remaining statements that canonical selection is deferred to Thales with: "P2 fixes the selection rule; Thales only operationalizes phase labeling, tie-breakers, and QC." Because the document currently both defers and fixes the same rule.

5. Replace `Propagation Intensity = log(1+cluster_size)+log(1+prior_family_count_365d)` as the primary factor with two primary stored variables, `event_burst` and `historical_family_recurrence`, and treat the composite as a secondary summary only. Because the current sum conflates two constructs.

6. Replace `Entity Salience` as a single factor with two explicitly named fields, `Target Prominence` and `Competing-Entity Prominence`. Because the current label hides two different mechanisms.

7. Replace the P1 prose rule with a one-row-per-factor audit table containing `construct`, `mechanism`, `CLS-internal / extra-corpus / case×model`, `Thales-dependent?`, and `expected direction`. Because P1 is currently not auditable from the text.

8. Replace P2 with a full algorithm that specifies assignment distribution, random seed, ambiguous-label rule, tie-breakers, no-match handling, and whether inverse-probability weighting is required. Because the current rule creates informative missingness and is not operationally complete.

9. Replace the P3 decision rule `if max pairwise α difference exceeds 0.05` with a paired-bootstrap comparison of α differences, randomized rubric order, and either two human raters or an explicit statement that the study is only a pilot reliability screen. Because the current uncertainty claim is too confident for the stated design.

10. Replace `Template Rigidity` with `Surface Similarity to Prior Texts`, and replace `Cutoff Exposure` with `Case×model cutoff timing` unless you can justify a genuine exposure model. Because both current names overclaim what is actually measured.

11. Replace `R4 status: CLOSED` / `no blockers` with `R4 conceptually closed; execution gates remain for Thales algorithms, model cutoff metadata, and point-in-time design`. Because the current closure language is premature.
