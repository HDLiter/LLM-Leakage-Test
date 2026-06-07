# BENCHMARK R4 Step 2 - NLP Shortlist Review
**Date:** 2026-04-13
**Reviewer:** Codex (senior NLP/ML researcher)
**Reasoning effort:** xhigh
**Source:** 12-factor shortlist (post-Step 1 + user integration)
**Prior rounds:** BENCHMARK_R1/R2/R3_NLP.md + BENCHMARK_R4A_NLP.md
**Scope constraint:** No algorithmic specification for event-clustering or entity-annotation factors. Template Rigidity and Exact-Span Rarity can be fully specified.

---

The shortlist is coherent and now captures multiple exposure channels rather than single-article duplication alone. My main caution is dependency coupling, especially where one annotation layer feeds multiple factors.

## 1. Per-factor verdicts

1. **Propagation Intensity — GO.** Stronger than pure cluster size because it captures both event-instance burst and historical template recurrence. Keep the composite, but report both subcomponents.
2. **Cutoff Exposure — GO.** Still the cleanest temporal contamination axis. The gray band is important because reported cutoffs are not sharp.
3. **Anchor Strength — CONCERN.** Valid construct, but the rubric will define the factor. Keep it only if the 50-case comparison is a real instrument-selection exercise.
4. **Entity Salience — GO.** The dual form is correct because target prior density and distractor competition are different mechanisms.
5. **Target Scope — GO.** Necessary partition because company and non-company targets invoke different priors and external metadata.
6. **Tradability Tier — GO.** Defensible as a conditionally defined economic covariate on company targets only.
7. **Structured Event Type — CONCERN.** Useful, but label noise here now propagates into `prior_family_count_365d`; freeze the ontology early.
8. **Disclosure Regime — GO.** Meaningful institutional-text split and not reducible to event type.
9. **Template Rigidity — GO.** One of the cleanest pure-NLP factors because it targets repeated textual shells directly.
10. **Event Phase — GO.** The two-stage sampling rule makes phase an actual design factor.
11. **Session Timing — GO.** Plausible market-structure control with little conceptual ambiguity.
12. **Text Length — GO.** Necessary nuisance control; do not over-interpret it.

## 2. Methodology inputs

- **Idea 1, extra-corpus signal principle — SUPPORT.** Write this explicitly into the rationale: external salience, tradability, and historical recurrence matter precisely because they are not CLS-internal restatements.
- **Idea 2, Event Phase two-stage sampling — SUPPORT.** Correct design, assuming phase rules are frozen before article selection.
- **Idea 3, Anchor operationalization empirical selection — SUPPORT.** Correct move; anchor strength is too underspecified to settle by argument alone.
- **Idea 4, pre-registered interaction menu — SUPPORT.** Good compromise between discipline and flexibility.
- **Idea 5, detector-dependent factors moved to R5 — SUPPORT.** Correct boundary; those are detector-coupled diagnostics, not benchmark-construction factors.

## 3. Detail resolutions

**C1. Propagation Intensity subcomponents**

`cluster_size` and `prior_family_count_365d` are related but not the same construct. The first is **intra-event burst exposure**; the second is **inter-event template recurrence**. Both feed frequency-recall at different granularities. Present them as one headline factor with two named channels, and report both parts for interpretation.

**C2. Company-subset-only Tradability Tier**

This is defensible as long as you do not pretend it has support outside company targets. The benchmark can have 12 planned factors with Factor 6 defined only on the `target_type=company` stratum. Stratify or otherwise respect support; do not impute pseudo-tradability for non-company targets.

**C3. Dual Entity Salience**

This is best treated as a **hybrid factor family**. `target_salience` is closer to corpus-prior density; `max_non_target_entity_salience` is closer to behavioral interference. Keep both. They answer different questions: target prior density versus distractor competition.

## 4. Biggest new risk

The biggest new risk is **ontology coupling**. `prior_family_count_365d` now depends on event-type annotation, so instability in the taxonomy contaminates both **Propagation Intensity** and **Structured Event Type** at once. Freeze the event-type ontology and adjudication rules before computing any history-based counts derived from it.

## 5. NLP operationalization focus

For the annotation-dependent factors, stay conceptual at this stage:

- **Propagation Intensity:** conceptually valid as burst exposure plus schema recurrence; do not finalize counting rules until event typing is frozen.
- **Event Phase:** conceptually valid under the two-stage sampling rule; definitions must distinguish phase semantics from article chronology.
- **Entity Salience:** keep the dual fields and defer canonical entity treatment to the joint Thales session.
- **Structured Event Type:** keep fine-grained types, but tie every label to a codebook definition and examples.
- **Anchor Strength:** select the rubric empirically, then freeze it.
- **Disclosure Regime:** treat as an institutional-text distinction, not a noisy proxy for event type.

For the two pure-NLP factors, I would specify them now:

**Template Rigidity**

Use one canonical text per cluster. Normalize by removing markup, collapsing whitespace, lowercasing Latin text, and replacing digit runs with `<NUM>` so dates and amounts do not dominate similarity. Represent texts with character 5-gram TF-IDF using sublinear term frequency and `min_df=3`. For each case, retrieve out-of-cluster nearest neighbors by cosine similarity and define the factor as the mean cosine to the top 5 neighbors. Higher values indicate more boilerplate phrasing. Sanity-check that rankings are not driven mainly by text length or publisher names.

**Exact-Span Rarity**

Keep this in reserve until the trigram subproject is validated, but the eventual factor can already be defined. On the canonical-text corpus, normalize lightly, extract character trigrams, discard punctuation-only and purely numeric-template trigrams, and compute cluster-level document frequency. Convert to rarity with `idf = log((N + 1) / (df + 1)) + 1`, then apply the learned trigram-quality filter to suppress boilerplate and formatting artifacts. Define the document score as the mean IDF of the top 20 informative trigrams, with a minimum-length guard so very short articles do not get unstable scores.

## 6. Anchor 50-case experiment design

Use the experiment to choose an instrument, not merely compare impressions. Sample 50 clusters by stratified random selection over the hardest dimensions: pre/post-cutoff, company/non-company target, short/long text, low/high propagation, and several event types. Present every rater the same evidence bundle: headline, lead paragraph, and minimal metadata only. Avoid full-cluster context so the rubric measures addressability from the case text.

Have three independent raters apply each rubric to all 50 cases. I recommend two model families plus one human expert. Randomize rubric order by case so later judgments are not anchored by earlier scores.

Compute:

- Krippendorff's alpha with ordinal distance for each rubric across all raters.
- Pairwise quadratic weighted kappa for transparency.
- Spearman correlation between each rubric's scores and a post-hoc consensus ranking of the same cases.
- Annotation time per case and unresolved-disagreement rate as practical burden measures.

Define **face validity** before looking at results. Here that means: uniquely indexed cases should score high, generic market-wrap/commentary cases should score low, and score differences should be explainable from visible textual anchors rather than length or background knowledge. After blind scoring, review the highest, lowest, and biggest cross-rubric disagreement cases against that definition.

Tie-break rule: highest ordinal alpha wins. If two rubrics are within 0.05 alpha, choose the one with better face-validity review. If still tied, choose the simpler rubric with lower median annotation time and clearer written guidelines.

## 7. Exact-Span Rarity subproject sketch

Phase 1: sample several thousand trigram instances across the DF spectrum, event types, and short/long documents, then label them as informative exact content, boilerplate, numeric-formatting noise, or borderline.

Phase 2: train a small classifier on local trigram context and compare it against raw IDF and a heuristic filter.

Phase 3: validate on held-out data at both trigram level and document-ranking level.

Phase 4: if the pilot succeeds, score all canonical texts and run sanity checks against text length, publisher effects, and template rigidity.

Move from pilot to full only if the learned filter clearly beats raw IDF on held-out quality and yields stable document-level rankings. If not, keep Exact-Span Rarity in reserve and report the pilot as a methods appendix.
