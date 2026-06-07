---
role: Editor / narrative and venue-fit
lens: R5A Step 1 detector brainstorm
thread_id: 019d914b-2d18-7c40-9113-00183a9c8e21
model_reasoning_effort: xhigh
generated: 2026-04-15
---

## SR/FO Counterfactual Pair
**Concept:** A paired counterfactual detector that rewrites the case to reverse its decisive financial implication or injects a conflicting outcome cue, then measures whether the model follows the edited evidence or falls back to stored event memory. In paper voice: this tests whether apparent knowledge is anchored in the case text or in memorized post hoc outcomes.

**Mechanism family:** counterfactual perturbation. **Access requirement:** either.

**Narrative fit rationale:** This is the cleanest detector for the paper’s spine because it directly operationalizes `Anchor Strength` while staying legible to both EMNLP and finance readers. It supports the central claim that memorization is not just “old news is easier,” but that detector behavior depends on how crisply an event is anchored and how the model handles evidence conflict. It also helps differentiate FinMem-Bench from `Profit Mirage`, `Look-Ahead-Bench`, and `LiveTradeBench`, which are benchmark-level leakage or PiT-evaluation papers rather than controlled semantic-conflict detectors. If you keep SR and FO in one family, the paper stays focused; if you split them into two headline detectors, the narrative starts to look like a perturbation suite.

**Factor relevance:** `Cutoff Exposure:` I expect the SR/FO gap to widen for negative `cutoff_gap_days`, because memorized outcomes should make models resist edited evidence. `Propagation Intensity:` Repeated event families should strengthen latent priors and modestly increase counterfactual resistance. `Anchor Strength:` This should be the detector’s strongest moderator, because crisp anchors create the sharpest conflict between article evidence and memorized traces. `Entity Salience:` High target salience should amplify the effect, while high non-target salience may add competing retrieval paths and blur it. `Disclosure Regime:` Formal disclosures should sharpen the detector because they encode discrete factual states with less interpretive slack than commentary. `Session Timing:` Post-close and pre-open items should be more diagnostic than intraday flashes because they are more likely to package a complete outcome narrative.

**Bloc diversification:** Primary target is **Bloc 0** with a direct bridge to the non-bloc `Anchor Strength` spine factor; good diversification, not another Bloc 1 detector.

**Construct-validity paper framing:** Following [Freiesleben 2026](https://arxiv.org/abs/2603.15121), I would frame the SR/FO gap as one nomological indicator of evidence-conflict sensitivity under suspected memorization, not as the memorization construct itself. Because perturbation methods can also pick up edit awkwardness or task fragility, cross-detector agreement should be reported only as descriptive robustness, consistent with [Meeus et al. 2024](https://arxiv.org/abs/2406.17975).

**Related-work differentiation:** This departs from MemGuard-Alpha’s MCS+CMMD stack by testing semantic evidence conflict directly rather than inferring membership from an ensemble of score heuristics.

**Reviewer-accessibility score:** 5/5. **Paper real-estate cost:** 1 example figure, about 2 Methods paragraphs, 1 Results paragraph.

**Detector-level stratification fields (P5):** `text_reversibility_score`; `entity_anonymization_sensitivity`.

**Thales dependency:** partial.

**Key citations:** [Profit Mirage / Li et al. 2025](https://arxiv.org/abs/2510.07920); [Wongchamcharoen & Glasserman 2025](https://arxiv.org/abs/2511.14214); [Freiesleben 2026](https://arxiv.org/abs/2603.15121); [Meeus et al. 2024](https://arxiv.org/abs/2406.17975).

**Risks / caveats:** If edit quality is uneven, reviewers can dismiss the effect as rewrite artifact; you need reversibility scoring and a restrained claim.

## FinMem-NoOp
**Concept:** Insert an irrelevant-but-plausible clause into the CLS item and measure how much the detector score or downstream prediction moves. In paper voice: this tests whether memorization behaves like brittle template matching that is distractible by finance-plausible clutter.

**Mechanism family:** counterfactual perturbation. **Access requirement:** either.

**Narrative fit rationale:** This is the best detector for the paper’s `Entity Salience` story because it gives the target-vs-distractor split a concrete behavioral readout. It also stays squarely in EMNLP territory: controlled perturbation, robustness to irrelevant additions, and evidence-vs-memory interference. For finance readers, the mechanism is still readable because the distractor is another plausible market clause, not an abstract NLP mutation. This is genuine novelty relative to MemGuard-Alpha and gives FinMem-Bench a detector that reviewers can remember after a 9-page read.

**Factor relevance:** `Cutoff Exposure:` I expect moderate positive sensitivity, with pre-cutoff cases more vulnerable if the model is retrieving a familiar shell rather than reasoning from evidence. `Propagation Intensity:` Repeated templates should make plausible clutter easier to absorb, so the NoOp effect should increase modestly. `Anchor Strength:` Strong anchors should reduce NoOp sensitivity if the model is actually tracking the decisive fact. `Entity Salience:` This should be the detector’s strongest moderator, especially when `max_non_target_entity_salience` is high. `Disclosure Regime:` Commentary should show larger NoOp effects than formal disclosures because it leaves more room for distractor assimilation. `Session Timing:` Intraday items should be most NoOp-sensitive because they are noisier, more partial, and more entity-dense.

**Bloc diversification:** Primary target is **Bloc 2** with secondary spillover to **Bloc 3**; very useful antidote to Bloc 1 collapse.

**Construct-validity paper framing:** Following [Xiao et al. 2023](https://aclanthology.org/2023.emnlp-main.676/) and [Kearns 2026](https://arxiv.org/abs/2602.15532), I would explicitly treat NoOp sensitivity as a detector with its own method bias, not a direct latent readout. Any correlation with salience variables is evidence to be explained within a broader nomological network, not construct validation by correlation.

**Related-work differentiation:** MemGuard-Alpha has no distraction-style probe tied to competing-entity salience; this gives FinMem-Bench a distinct detector-family contribution.

**Reviewer-accessibility score:** 5/5. **Paper real-estate cost:** 1 schematic/example, about 2-3 Methods paragraphs, 1 Results paragraph.

**Detector-level stratification fields (P5):** `distractor_plausibility_band`; `entity_anonymization_sensitivity`.

**Thales dependency:** partial.

**Key citations:** [Mirzadeh et al. 2024](https://arxiv.org/abs/2410.05229); [Wu et al. 2025](https://arxiv.org/abs/2511.15364); [Kong et al. 2026](https://arxiv.org/abs/2602.14233); [Xiao et al. 2023](https://aclanthology.org/2023.emnlp-main.676/).

**Risks / caveats:** The detector lives or dies on the definition of “irrelevant but plausible”; if that becomes LLM-magic instead of rule-bound design, reviewers will treat it as ad hoc.

## CMMD
**Concept:** Measure cross-model disagreement over the same case across a dated model fleet, using disagreement as a temporal-exposure signal rather than a pure accuracy signal. In paper voice: when model cutoffs differ, disagreement can reveal where memorization opportunity is temporally structured.

**Mechanism family:** cross-model disagreement. **Access requirement:** either.

**Narrative fit rationale:** This is the most natural detector for `Cutoff Exposure`, and it lets the paper use the full mixed fleet instead of shrinking the main text to white-box models. It also helps reviewers see why the finance substrate matters: dated events plus dated checkpoints create a rare opportunity for interpretable temporal contrasts. The overlap with MemGuard-Alpha is real, so this should be a secondary pillar rather than the paper’s identity. Its value is not novelty of detector invention, but stronger factor-controlled interpretation in Chinese CLS.

**Factor relevance:** `Cutoff Exposure:` This should be the strongest effect by construction, with disagreement peaking where case timing straddles model-specific knowledge boundaries. `Propagation Intensity:` I expect an inverted-U pattern, with moderate-to-high propagation amplifying disagreement near the boundary but very universal events collapsing disagreement once all models have seen them. `Anchor Strength:` Strong anchors should increase disagreement because later models can converge on memorized specifics while earlier models cannot. `Entity Salience:` High target salience should sharpen disagreement when the named entity-event pair is known to some models but not others. `Disclosure Regime:` Formal disclosures should yield cleaner cutoff-linked disagreement because they provide canonical facts that later-cutoff models can share. `Session Timing:` Post-close and pre-open items should be most diagnostic because they align with standardized release routines that later models may have ingested as complete packages.

**Bloc diversification:** Primary target is **Bloc 0**; this is the main temporal counterweight to repetition-heavy detectors.

**Construct-validity paper framing:** Following [Freiesleben 2026](https://arxiv.org/abs/2603.15121), CMMD should be framed as one theoretically motivated indicator of cutoff-linked exposure, not as an empirical validator of the bloc structure. Per [Perlitz et al. 2024](https://arxiv.org/abs/2407.13696), agreement with other detectors is descriptive robustness only, because agreement itself is method-sensitive.

**Related-work differentiation:** This is the one deliberate overlap with MemGuard-Alpha, but FinMem-Bench extends it to Chinese CLS with pre-registered factor cuts and stronger construct-validity discipline.

**Reviewer-accessibility score:** 4/5. **Paper real-estate cost:** 1 figure, about 2 Methods paragraphs, 1-2 Results paragraphs.

**Detector-level stratification fields (P5):** `cross_model_agreement_score`; `entity_anonymization_sensitivity`.

**Thales dependency:** no.

**Key citations:** [MemGuard-Alpha / Roy & Roy 2026](https://arxiv.org/abs/2603.26797); [Chen et al. 2026](https://arxiv.org/abs/2603.21658); [Kong et al. 2026](https://arxiv.org/abs/2602.14233); [Perlitz et al. 2024](https://arxiv.org/abs/2407.13696).

**Risks / caveats:** Reproducibility burden is high; without pinned checkpoints and provider routing locks, reviewers will discount the result.

## Min-K%++
**Concept:** Use the least-likely token tail of a case to estimate whether the text looks unusually familiar to the model. In paper voice: this is the single best white-box “seen text” baseline for direct memorization-style detection without an opaque ensemble.

**Mechanism family:** surface-form sensitivity. **Access requirement:** white-box.

**Narrative fit rationale:** This is the one surface-form detector I would keep, not the beginning of a family. It supports the spine through `Cutoff Exposure` and `Propagation Intensity`, gives EMNLP reviewers a recognizable memorization baseline, and distinguishes FinMem-Bench from finance papers that only study downstream leakage or backtests. But it is exactly the kind of detector that can collapse the paper into “mostly Bloc 1,” so it should be positioned as corroborative white-box evidence, not as the benchmark’s main identity.

**Factor relevance:** `Cutoff Exposure:` I expect a strong pre/post boundary effect once the gray band is excluded. `Propagation Intensity:` This should be strongly positive, because repeated formulations compress the hard-token tail. `Anchor Strength:` Distinctive anchors should moderately increase the signal by creating a narrower rare-token signature. `Entity Salience:` High target salience should increase the score, while strong non-target salience may dilute it by adding unpredictable tokens. `Disclosure Regime:` Formal disclosures should score higher than commentary because boilerplate and canonical factual phrasing reduce tail uncertainty. `Session Timing:` Expect only a mild post-close/pre-open premium, likely mediated by more standardized release text.

**Bloc diversification:** Primary target is **Bloc 1**; yes, this risks the “FinMem only detects propagation” headline if you add more neighboring detectors.

**Construct-validity paper framing:** Following [Cronbach & Meehl 1955](https://psychclassics.yorku.ca/Cronbach/construct.htm) and [Xiao et al. 2023](https://aclanthology.org/2023.emnlp-main.676/), Min-K%++ should be presented as one operationalization of suspected exposure, not a privileged measure of memorization itself. Any convergence with other detectors should be reported descriptively, not as latent-construct validation, especially given method-sensitivity concerns from [Perlitz et al. 2024](https://arxiv.org/abs/2407.13696).

**Related-work differentiation:** This deviates from MemGuard-Alpha’s 5-MIA ensemble by replacing a learned stack with a single interpretable white-box detector.

**Reviewer-accessibility score:** 4/5. **Paper real-estate cost:** 0-1 compact figure, about 2 Methods paragraphs, 1 Results paragraph.

**Detector-level stratification fields (P5):** `logprob_tail_length`; `entity_anonymization_sensitivity`.

**Thales dependency:** no.

**Key citations:** [Zhang et al. 2024](https://arxiv.org/abs/2404.02936); [Kong et al. 2026](https://arxiv.org/abs/2602.14233); [Chen et al. 2025 survey](https://aclanthology.org/2025.emnlp-main.511/); [Xiao et al. 2023](https://aclanthology.org/2023.emnlp-main.676/).

**Risks / caveats:** White-box only, repetition-adjacent, and easy to over-interpret; if paired with several MIA-like methods, the paper drifts toward detector arcana.

## Targeted Span Extraction
**Concept:** Probe whether models can reproduce exact or near-exact CLS spans when prompted with case anchors or partial context. In paper voice: this supplies hard-edge evidence of verbatim or near-verbatim retention even when softer detectors are ambiguous.

**Mechanism family:** extraction-verbatim. **Access requirement:** either.

**Narrative fit rationale:** This is the best hard-edge companion detector, not the benchmark’s centerpiece. It gives the paper one unmistakable memorization anchor that finance and NLP reviewers both understand immediately: exact reuse is qualitatively different from “the model kind of knew the event.” It also differentiates FinMem-Bench from `Profit Mirage`, `Look-Ahead-Bench`, and `LiveTradeBench`, none of which give verbatim-style detector evidence. The cost is space: extraction wants examples, caveats, and a narrower claim.

**Factor relevance:** `Cutoff Exposure:` Exact extractability should drop sharply once cases are clearly post-cutoff. `Propagation Intensity:` Repeated clusters and recurrent event families should strongly increase extractable phrasing. `Anchor Strength:` Distinctive anchors should act as retrieval keys and materially increase extractability. `Entity Salience:` High target salience should raise extractability, while heavy non-target salience may either help via extra cues or hurt via competition. `Disclosure Regime:` Formal disclosures should be more extractable because they contain schema-like, repeatedly syndicated phrasing. `Session Timing:` Post-close and pre-open items should be somewhat more extractable because they more often arrive as clean official text packages.

**Bloc diversification:** Primary target is **Bloc 1** with some Bloc 0 spillover; do not pair this with too many other repetition-heavy detectors.

**Construct-validity paper framing:** Following [Cronbach & Meehl 1955](https://psychclassics.yorku.ca/Cronbach/construct.htm), extraction should be framed as evidence about one corner of the memorization nomological network, namely verbatim retention, not the construct in full. Because extraction rates depend heavily on prompting and elicitation strategy, agreement with other detectors should be treated as descriptive triangulation rather than validation, echoing [Meeus et al. 2024](https://arxiv.org/abs/2406.17975).

**Related-work differentiation:** MemGuard-Alpha does not provide direct verbatim-style evidence; this adds a qualitatively different detector family rather than another ensemble component.

**Reviewer-accessibility score:** 5/5. **Paper real-estate cost:** 1 example table/figure, about 2 Methods paragraphs, 1 Results paragraph.

**Detector-level stratification fields (P5):** `extractable_span_density`; `entity_anonymization_sensitivity`.

**Thales dependency:** no.

**Key citations:** [Carlini et al. 2020](https://arxiv.org/abs/2012.07805); [Nasr et al. 2023](https://arxiv.org/abs/2311.17035); [Wu et al. 2025](https://arxiv.org/abs/2511.15364); [Cronbach & Meehl 1955](https://psychclassics.yorku.ca/Cronbach/construct.htm).

**Risks / caveats:** Sparse hits can make the detector look underpowered, and too much extraction detail can turn the paper into a different paper.

## RAVEN Novelty Gap
**Concept:** Measure how novel a model’s output is relative to cluster- and corpus-neighbor baselines, using low novelty as a sign that the model may be reproducing familiar local structure rather than composing freely. In paper voice: this bridges memorization detection and generated-text behavior without requiring direct extraction.

**Mechanism family:** hybrid. **Access requirement:** either.

**Narrative fit rationale:** This is the optional EMNLP-facing detector. It helps if you want one detector that speaks the language of text generation and output behavior rather than only token scores or fleet disagreement. It is useful for related-work positioning because it pulls FinMem-Bench toward mainstream evaluation discourse and away from pure finance leakage. But it is not needed if the page budget is tight, and it can blur into `Template Rigidity` unless carefully separated.

**Factor relevance:** `Cutoff Exposure:` I expect lower novelty primarily in clearly pre-cutoff cases. `Propagation Intensity:` This should be strongly negative for novelty, because repeated event families and rigid templates encourage low-novelty reuse. `Anchor Strength:` Strong anchors should lower novelty by stabilizing copied local structure. `Entity Salience:` High target salience should reduce novelty when canonical entity-event phrasing is reproduced, while strong non-target salience may force more recombination. `Disclosure Regime:` Formal disclosures should be least novel because the acceptable wording band is narrow and repeated. `Session Timing:` Pre-open and post-close releases should show lower novelty than intraday items because the text is more packaged and standardized.

**Bloc diversification:** Primary target is **Bloc 1**; use only if you do not already have several repetition-adjacent detectors in the main text.

**Construct-validity paper framing:** Following [Xiao et al. 2023](https://aclanthology.org/2023.emnlp-main.676/) and [Perlitz et al. 2024](https://arxiv.org/abs/2407.13696), novelty should be framed as a fallible measurement instrument with corpus- and method-specific error. Agreement with other detectors is useful descriptive triangulation, not evidence that all are measuring one validated latent memorization construct.

**Related-work differentiation:** This adds an output-behavior lens that MemGuard-Alpha’s MCS+CMMD pipeline does not have.

**Reviewer-accessibility score:** 4/5. **Paper real-estate cost:** 1 figure, about 2-3 Methods paragraphs, 1 Results paragraph.

**Detector-level stratification fields (P5):** `local_novelty_gap`; `entity_anonymization_sensitivity`.

**Thales dependency:** partial.

**Key citations:** [McCoy et al. / RAVEN](https://aclanthology.org/2023.tacl-1.38/); [Kong et al. 2026](https://arxiv.org/abs/2602.14233); [Freiesleben 2026](https://arxiv.org/abs/2603.15121); [Perlitz et al. 2024](https://arxiv.org/abs/2407.13696).

**Risks / caveats:** Reviewers may see this as partially overlapping with Template Rigidity unless you show that output novelty is not just another surface-recurrence score.

**Top 3 Picks By Narrative Centrality**
1. `SR/FO Counterfactual Pair`: best single detector family for the spine because it makes `Anchor Strength` real and keeps the claim mechanism-level rather than purely temporal.
2. `FinMem-NoOp`: best detector for the target-vs-distractor story and the strongest hedge against the paper collapsing into repetition-only measurement.
3. `CMMD`: best temporal detector for the full fleet and the cleanest way to show why dated checkpoints matter on this substrate.

`Min-K%++` is the first add if the paper can support a fourth main detector. `Extraction` and `RAVEN` are competing fifth-slot options, not both.

**Detector Shortlist CEILING**
The hard ceiling for a 9-page paper is **5 detectors**, and the healthier main-text number is **4**. Beyond that, the paper stops reading as a factor-controlled benchmark and starts reading as a detector zoo: each detector needs at least method definition, mechanism framing, one factor-pattern figure or paragraph, and related-work positioning. My editorial recommendation is `SR/FO`, `FinMem-NoOp`, `CMMD`, and `Min-K%++` in the main text, plus **either** `Extraction` **or** `RAVEN` as the optional fifth detector depending on whether you want harder evidence or more EMNLP-style output analysis.

**Mirror vs Deviate From MemGuard-Alpha’s 5-MIA Ensemble**
**Deviate.** Mirroring the 5-MIA-plus-logistic-regression stack is the fastest route to novelty loss and the slowest route to a readable 9-page paper. It also drags the paper directly into the identification skepticism emphasized by [Meeus et al. 2024](https://arxiv.org/abs/2406.17975). FinMem-Bench’s distinct contribution is factor-controlled detector interpretation on a Chinese financial substrate with explicit construct-validity discipline, not “MemGuard-Alpha but Chinese.”

**Ensemble vs Independent Reporting**
The main paper should report **independent detectors in a matrix**, not one learned ensemble. Your estimand family is factor × detector interaction; an ensemble destroys precisely the interpretability that makes the benchmark publishable. If you want a synthesis number, keep it descriptive and secondary: a z-scored average or sign-consistency summary in the appendix is fine, but the main text should remain detector-wise.

**Methods-Section Draft Paragraph**
> Following construct-validity guidance from [Cronbach and Meehl (1955)](https://psychclassics.yorku.ca/Cronbach/construct.htm) and recent LLM benchmark methodology ([Xiao et al., 2023](https://aclanthology.org/2023.emnlp-main.676/); [Freiesleben, 2026](https://arxiv.org/abs/2603.15121)), we treat detector-factor correlations as evidence to be explained rather than self-interpreting proof of a latent memorization construct. Accordingly, FinMem-Bench reports theory-led per-factor estimates for each detector, descriptive bloc-level summaries, and alternative decomposition stress tests, while avoiding claims that the proposed 4-bloc organization has itself been empirically validated. Because benchmark agreement is sensitive to benchmark design, model subset, and aggregation choice ([Perlitz et al., 2024](https://arxiv.org/abs/2407.13696)), cross-detector convergence is reported as robustness information, not as construct validation.

**Any Question The Editor Wants Quant / NLP / Stats To Answer Before R5A Step 2**
- Can `SR/FO` and `FinMem-NoOp` be implemented with rule-bound, auditable generation quality on Chinese CLS, or do they require enough LLM editing that a new method-bias layer dominates?
- For `FO`, do you have enough `known_outcome` coverage to avoid the generic-template degradation already seen in pilot notes?
- Can `CMMD` be frozen reproducibly at the checkpoint/provider level before paper-writing, or does it need to be demoted from central to confirmatory?
- If `Min-K%++` only runs on the 3 white-box models, can Stats present it cleanly as corroborative evidence rather than forcing a misleading full-fleet comparison?
- If `Disclosure Regime` is replaced by Thales `Modality`, which of the shortlisted detector-factor arguments survive unchanged, and which need to be rewritten?
