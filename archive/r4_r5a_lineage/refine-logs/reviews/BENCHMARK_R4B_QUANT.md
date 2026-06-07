# BENCHMARK R4 Step 2 — Quant Shortlist Review
**Date:** 2026-04-13
**Reviewer:** Codex (senior quantitative researcher)
**Reasoning effort:** xhigh
**Source:** 12-factor shortlist (post-Step 1 + user integration)
**Prior rounds:** BENCHMARK_R1/R2/R3_QUANT.md + BENCHMARK_R4A_QUANT.md
**Scope constraint:** No algorithmic specification for event-clustering or entity-annotation factors

---

**Per-Factor Verdicts**

Net judgment: `10 GO`, `2 CONCERN`, `0 BLOCK`. The shortlist is viable from the quant side and still preserves the alpha-bridge, provided the paper is explicit about which factors are primitive versus derived from shared annotation layers.

1. **Propagation Intensity — GO.** This is a stronger exposure construct than pure cluster size because it combines within-event spread with recurrence of the same event family across time. That is closer to a pretraining-opportunity story than a single-burst story, but the two subcomponents should be reported transparently.

2. **Cutoff Exposure — GO.** Signed continuous distance to cutoff is the right object, and excluding a gray band around zero is a legitimate noise-control step rather than sample gaming. This remains one of the cleanest bridge factors because it maps directly to model observability.

3. **Anchor Strength — CONCERN.** The mechanism is valid, but the primary operationalization is still unsettled, so confirmatory interpretation is not fully locked yet. The proposed 50-case comparison is acceptable if the choice rule is frozen before any leakage outcomes are examined.

4. **Entity Salience — GO.** Keeping `target_salience` separate from `max_non_target_entity_salience` is economically coherent because they encode different mechanisms: direct prominence versus competing-attention or piggyback effects. Collapsing them would lose signal.

5. **Target Scope — GO.** This is a necessary stratifier, not a cosmetic one. Company and non-company targets sit on different dissemination and monetization channels, so the bridge to market-linked memorization would be blurred without this split.

6. **Tradability Tier — GO.** As a company-only factor, this remains one of the strongest corpus-external proxies for broad market attention and likely training-set exposure. Conditioning it on `target_type=company` is cleaner than manufacturing a meaningless value for non-company cases.

7. **Structured Event Type — GO.** Fine-grained event structure matters because leakage opportunity is not homogeneous across event families. The user is right to reject a coarse 3-bin compression if the study is trying to preserve economic mechanism rather than just reduce dimensions.

8. **Disclosure Regime — GO.** Formal disclosures and commentary/secondary pieces move through different institutional pipelines and have different standardization properties. That gives this factor real mechanism content beyond surface text differences.

9. **Template Rigidity — CONCERN.** This is a legitimate production-process factor because rigid templates create repeated surface forms, but it is more exposed than most factors to venue mix and era drift. It should be presented as a text-production channel, not over-read as pure memorization propensity.

10. **Event Phase — GO.** With the two-stage sampling rule, phase becomes a genuine exposure dimension instead of an artifact of "earliest article wins." That fixes the main degeneracy concern and makes cross-phase interpretation defensible.

11. **Session Timing — GO.** Timing has a plausible market-attention and processing mechanism, especially for market-relevant targets, and the timestamp precision makes it operationally credible. It is also conceptually distinct from phase and disclosure regime.

12. **Text Length — GO.** As control-only, this is exactly where length belongs. It absorbs the mechanical fact that longer items offer more opportunities for anchors and entities without pretending length is itself a substantive causal story.

**New-Idea Positions**

1. **Extra-corpus signal principle — SUPPORT.** This belongs in the pre-commit rationale. Internal CLS frequencies are still useful, but corpus-external signals are valuable precisely because they are less hostage to CLS collection mechanics and therefore better for the bridge-to-training-distribution argument.

2. **Event Phase two-stage sampling — SUPPORT.** This is the right correction. If phase is meant to be studied, the sampling rule cannot mechanically collapse the sample into the earliest phase.

3. **Anchor operationalization empirical selection — REVISE.** The experiment is a good idea, but the decision rule must be fully pre-committed and outcome-blind. Otherwise the study will look like it optimized the factor definition after seeing downstream behavior.

4. **Pre-registered interaction menu — SUPPORT.** This is a disciplined compromise between rigidity and flexibility. It gives room for economically motivated interaction analysis without letting interaction search contaminate confirmatory claims.

5. **Detector-dependent factors belong in R5 — SUPPORT.** Agreed. Detector-coupled features are properties of the evaluation architecture, not the corpus/event mechanism, so folding them into R4 would mix levels of analysis and reduce portability across detector families.

**C1 / C2 / C3**

**C1. Propagation Intensity: one factor or coupled pair?**
At the theory level, it is one factor: exposure opportunity generated by propagation. At the measurement level, it is a composite with two linked subcomponents: contemporaneous spread (`cluster_size`) and historical recurrence (`prior_family_count_365d`). I would not present `prior_family_count` as a separate standalone factor, because that would blur the distinction between event-family identity and event-family recurrence. In the paper and pre-registration, present `Propagation Intensity` as a primary composite factor, but require component-level reporting so readers can see whether the signal is coming from burst size, historical repetition, or both. Also make the dependency explicit: the historical term is downstream of the event-family annotation layer.

**C2. Tradability Tier as a company-only factor: serious limitation or minor inconvenience?**
Minor inconvenience, not a serious limitation. For the alpha-bridge story, that conditionality is actually a feature: tradability is economically meaningful for firms and not meaningful for non-company targets, so restricting it to the company subset preserves validity instead of diluting it. A company subset of roughly 1,050 to 1,275 cases is usually large enough that a coarse tradability partition is still credible unless the realized split is extremely skewed. The bigger point is conceptual: this factor is about within-company heterogeneity, not universal coverage.

**C3. Does large non-target salience have distinct economic meaning?**
Yes. A prominent non-target co-mention can change memorization through a different channel than target salience alone. It can create a piggyback effect, where a less prominent target rides on the dissemination footprint of a much larger firm, regulator, index constituent, or counterpart. It can also create an attention-diversion effect, where the article is broadly propagated but the target-specific details are less likely to be retained because the narrative center of gravity sits elsewhere. Those are distinct hypotheses, and both are economically meaningful.

**Biggest New Risk**

The single biggest new risk is **shared-annotation dependence masquerading as multi-factor evidence**. Several factors that look separate on paper now lean on the same latent event/entity annotation backbone: Structured Event Type, the historical component of Propagation Intensity, Event Phase, and to some extent disclosure-oriented distinctions. If that upstream annotation layer is noisy, drifting, or conceptually tilted, the errors will be correlated across multiple downstream factors. The danger is not just attenuation; it is false convergence, where the paper appears to find several aligned mechanisms but is partly rediscovering the same annotation architecture from different angles. The pre-registration should therefore distinguish primitive annotations from derived factors and acknowledge the dependency graph explicitly.
