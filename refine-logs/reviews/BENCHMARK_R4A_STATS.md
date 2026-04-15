# BENCHMARK R4 Step 1 — Stats Factor Brainstorm
**Date:** 2026-04-13
**Reviewer:** Codex (senior econometrician)
**Reasoning effort:** xhigh
**Source:** docs/DECISION_20260413_mvp_direction.md v2
**Prior rounds:** BENCHMARK_R1/R2/R3_STATS.md

---

I am filtering candidate factors through one criterion only: can they generate a clean, executable, event-cluster-level contrast at `N = 1,000-1,500` without pretending the MVP has subgroup power it does not have. My standing anchor remains `N_floor ≈ 852 scorable clusters` for one balanced 2-group contrast at `OR = 1.95`. With `15-20%` loss, `1,500` gross cases implies about `1,275-1,200` scorable; `1,000` gross implies about `850-800` scorable. The immediate consequence is simple: balanced binary factors are the only serious confirmatory candidates. Three-level factors are marginal even at `1,500`, and 2x2 interactions are exploratory only. At `OR = 1.5`, I would not call any of the secondary heterogeneity factors confirmatory at MVP scale.

Useful power anchors for what follows:

- Balanced 2-bin contrast: `852` scorable total required. With `1,500` gross and `20%` loss, `600 vs 600` scorable is feasible.
- `70/30` split: information efficiency is `4p(1-p) = 0.84`, so required total rises to about `852 / 0.84 = 1,014` scorable.
- `75/25` split: efficiency `0.75`, so required total is about `1,136` scorable.
- `80/20` split: efficiency `0.64`, so required total is about `1,331` scorable, which already strains `1,500` gross once loss is applied.
- Terciles, comparing top vs bottom only: at `1,500` gross and `20%` loss, each extreme bin has about `400` scorable cases, so `400 + 400 = 800`, below the `852` floor before any multiplicity correction.

### Factor: Model-cutoff exposure opportunity
**Concept**: Whether the cluster first appeared before or after a model-specific pretraining cutoff, using first availability as the exposure-opportunity proxy.  
**Identification strategy**: Between-cluster binary partition, estimated separately by target model; this is the cleanest MVP treatment-like contrast.  
**Statistical meaning (Decision 10)**: Treatment proxy. It does not identify `tau_nat`, but it is a pre-specified exposure-opportunity partition with direct interpretive value.  
**Operationalization**: Define `pre_cutoff_m = 1[first_seen_time <= cutoff_m]`, using cluster `first_seen_time`, not canonical article time. If only the date is known, compare on Beijing calendar date. Cutoff date must be fixed externally per model before confirmatory runs.  
**Number of levels + expected distribution**: 2 levels. Natural corpus share may land around `60/40` or `70/30`; if this is confirmatory, the curated core should actively avoid worse than `70/30`.  
**Power at 1500 cases, OR=1.95 baseline**: Strong. At `50/50`, `1,500` gross and `20%` loss gives `600 vs 600` scorable. Even at `70/30`, required total is about `1,014` scorable, so `1,200` remains adequate. At `1,000` gross, however, a `70/30` split becomes marginal.  
**Confounders**: Calendar drift in event mix, target type, market regime, cluster size, source style changes over time. These must be adjusted or balanced.  
**Predicted effect direction**: Pre-cutoff cases should show higher memorization-risk scores than post-cutoff cases.  
**Failure modes**: Cutoff uncertainty, timestamp ambiguity, or an `80/20` natural split. If minority share drops to `20%`, this is no longer safely confirmatory without quota balancing.  
**Framing support**: Both.

### Factor: Pre-cutoff age relative to the cutoff
**Concept**: Among pre-cutoff items only, recency to the cutoff captures how fresh or stale the exposure opportunity was.  
**Identification strategy**: Between-cluster dose contrast within the pre-cutoff subset; this is cleaner than mixing pre and post when the question is temporal decay.  
**Statistical meaning (Decision 10)**: Secondary treatment-intensity proxy. It is not causal, but it tests a monotone exposure-opportunity story.  
**Operationalization**: Compute `days_to_cutoff_m = cutoff_m - first_seen_time`. Primary rule: binary `near_pre = 1[0 <= days_to_cutoff <= 365]` vs `far_pre = 1[days_to_cutoff > 365]`. A 3-bin version such as `0-180 / 181-730 / >730` can be stored but should be exploratory only.  
**Number of levels + expected distribution**: 2 for serious use. Within pre-cutoff cases, natural share is likely skewed, perhaps `30/70` or worse unless the core sample is engineered.  
**Power at 1500 cases, OR=1.95 baseline**: Marginal unless sampled intentionally. Example: if overall pre-cutoff share is `70%` and near/far within pre is `30/70`, then `1,500` gross yields about `315/735` raw cases, or `252 vs 588` scorable after `20%` loss, only `840` total. That misses the `852` floor. I would not make this primary unless the curated core deliberately balances the two bins.  
**Confounders**: Secular shifts in target composition, reporting style, sector mix, and any evolving corpus ingestion policy.  
**Predicted effect direction**: More recent pre-cutoff items should show stronger memorization-risk signals than older pre-cutoff items.  
**Failure modes**: Cutoff mis-specification, severe skew, or temporal bunching near recent years.  
**Framing support**: Both.

### Factor: Duplication or propagation intensity
**Concept**: Cluster size measures how widely an event text propagated through near-duplicate rewrites, which is a plausible exposure-intensity proxy.  
**Identification strategy**: Between-cluster partition on `duplicate_cluster_size`.  
**Statistical meaning (Decision 10)**: Treatment proxy or effect modifier. Statistically, this is one of the few cluster-native variables with direct meaning and no reliance on subjective annotation.  
**Operationalization**: Primary binary rule should be simple and stable: `singleton = 1[duplicate_cluster_size = 1]` vs `duplicated = 1[duplicate_cluster_size >= 2]`. If the frozen corpus is too imbalanced, a median split is acceptable under the Decision 9 rule-locking posture. Store a 3-bin version for exploratory use only.  
**Number of levels + expected distribution**: 2 primary; 3 exploratory. A `singleton` vs `duplicated` split is likely around `50/50` to `60/40`, but the exact share depends on clustering aggressiveness.  
**Power at 1500 cases, OR=1.95 baseline**: Feasible as a primary binary contrast. At `60/40`, required total is about `852 / 0.96 = 887` scorable, easily within `1,200`. By contrast, a tercile comparison is weak: with `1,500` gross and `20%` loss, top vs bottom terciles give only `400 + 400 = 800` scorable.  
**Confounders**: Reprint status, event family, target type, and time period. More important events are more duplicated, so this is not cleanly separable from salience.  
**Predicted effect direction**: Larger duplicate clusters should have higher memorization-risk scores than singletons.  
**Failure modes**: Over-merged clusters, noisy deduplication, or an extreme right tail with very few high-size clusters.  
**Framing support**: Both.

### Factor: Reprint status
**Concept**: Whether the CLS article is effectively a retransmission of an official or public-domain source.  
**Identification strategy**: Between-cluster binary partition or covariate adjustment.  
**Statistical meaning (Decision 10)**: Secondary exposure proxy. Reprints plausibly increase corpus spread and reduce lexical novelty, both of which matter for memorization-risk analysis.  
**Operationalization**: Use the stored boolean `is_reprint`. Keep `public_source_type` only for descriptive breakdown unless sample size is unexpectedly large. Any `unknown` cases from the matching pipeline should be kept out of the confirmatory reprint contrast.  
**Number of levels + expected distribution**: 2 levels, but likely uneven; I would expect something like `15-35%` reprints depending on the slice.  
**Power at 1500 cases, OR=1.95 baseline**: Only conditionally viable. If prevalence is `30%`, required total is about `1,014` scorable and the factor is workable. If prevalence is `20%`, required total jumps to about `1,331`, which exceeds `1,500` gross after ordinary loss. Therefore I would not pre-register this as confirmatory until the frozen corpus proves the minority share is at least roughly `30%`.  
**Confounders**: Target type, event family, policy announcements, cluster size, and text length.  
**Predicted effect direction**: Reprints should exhibit higher memorization-risk scores than non-reprint original news narratives.  
**Failure modes**: Sparse positive class or brittle similarity matching.  
**Framing support**: Both.

### Factor: Target scope or instrument type
**Concept**: Whether the case targets a single company or a broader basket, sector, or index.  
**Identification strategy**: Between-cluster stratified comparison; also a mandatory control because outcome-generation rules differ by target scope.  
**Statistical meaning (Decision 10)**: Stratification variable and control. This is less a substantive treatment than a guardrail against pooling incomparable units.  
**Operationalization**: Collapse frozen `target_type` to a primary binary split: `company` vs `non_company_basket_or_index`. Keep finer classes only descriptively unless the minority share proves large enough. Any mixed-target cases need a deterministic assignment rule or should be excluded from target-scope contrasts.  
**Number of levels + expected distribution**: 2 primary. I expect `company` to dominate, plausibly `70-85%`.  
**Power at 1500 cases, OR=1.95 baseline**: Usually not strong enough for a headlining confirmatory contrast unless the minority share is protected by design. At `75/25`, required total is about `1,136` scorable, so `1,500` gross can barely support one such comparison. At `85/15`, required total is about `1,671`, so it fails. My recommendation is to treat this primarily as a stratifier and control, not a main factor.  
**Confounders**: Event family, reprint status, label quality, and benchmark construction differences in the outcome layer.  
**Predicted effect direction**: My prior is that single-company items may show sharper memorization-risk contrasts because the entity mapping is cleaner, but this is exploratory, not something I would build the paper around.  
**Failure modes**: Thin non-company bucket and interpretation drift if heterogeneous target types are pooled too aggressively.  
**Framing support**: Both.

### Factor: Event family
**Concept**: Broad event mechanism category, not fine-grained topic labeling.  
**Identification strategy**: Between-cluster stratification.  
**Statistical meaning (Decision 10)**: Stratification variable. It matters because firm-specific, industry, and macro-policy news differ in dependence structure, textual templating, and plausible exposure pathways.  
**Operationalization**: Freeze a coarse 3-bin codebook only: `firm_specific`, `sector_or_industry`, `macro_or_policy`. No 5- or 6-way event taxonomy in the MVP confirmatory layer. Multi-label cases need a dominant-family rule or a `mixed` flag excluded from the contrast.  
**Number of levels + expected distribution**: 3 levels; likely `50-60%` firm-specific, `15-25%` sector/industry, `20-30%` macro/policy.  
**Power at 1500 cases, OR=1.95 baseline**: Not confirmatory as a 3-level factor. Even in an optimistic equal-third world, top vs bottom comparisons produce only about `800` scorable cases after `20%` loss. Use it as a control or descriptive table, or collapse to `firm_specific` vs `non_firm` if a binary contrast is later required.  
**Confounders**: Target type, reprint status, cluster size, and time period.  
**Predicted effect direction**: Ambiguous ex ante. Firm-specific news may be more entity-repeatable; macro-policy news may be more widely disseminated. That ambiguity is exactly why this is secondary.  
**Failure modes**: Poor annotation agreement or too many mixed cases.  
**Framing support**: Both.

### Factor: Text length
**Concept**: CLS text length is mechanically relevant to both detector behavior and model response, regardless of economic content.  
**Identification strategy**: Between-cluster covariate adjustment or balanced median split.  
**Statistical meaning (Decision 10)**: Nuisance control. It has genuine statistical meaning because many memorization detectors and prompt outputs are length-sensitive.  
**Operationalization**: Compute token count on the exact CLS measurement text using a frozen tokenizer rule. Primary use should be continuous adjustment; if a discrete factor is needed, use a median split on the frozen corpus.  
**Number of levels + expected distribution**: 2 bins if discretized; balanced by construction under a median split.  
**Power at 1500 cases, OR=1.95 baseline**: Easily powerable as a balanced binary partition, but I would not spend confirmatory alpha on it. It belongs in adjustment sets and robustness tables, not in the paper's main claim.  
**Confounders**: Reprint status, event family, target type, and canonical-selection rule.  
**Predicted effect direction**: Sign is ambiguous. Longer text can increase overlap opportunity but also dilute concentrated memorized spans.  
**Failure modes**: Tokenizer drift across models. Freeze one operational rule and hold it fixed.  
**Framing support**: Substrate.

### Factor: Outcome label quality
**Concept**: Whether the realized outcome label was computed under clean market-data conditions or under degraded timing/tradability/history conditions.  
**Identification strategy**: Robustness stratum and exclusion-control, not a substantive heterogeneity axis.  
**Statistical meaning (Decision 10)**: Measurement-quality control on the dependent variable. This is statistically important even if it is not theoretically glamorous.  
**Operationalization**: Use the eventual rule-based `label_quality` field and collapse it to `high` vs `degraded_or_borderline` for MVP use. This field must remain mechanical and non-LLM.  
**Number of levels + expected distribution**: 2 levels, probably very uneven, likely `80-90%` high quality.  
**Power at 1500 cases, OR=1.95 baseline**: Not a primary factor. At `85/15`, required total is about `1,671` scorable, which exceeds feasible MVP scale. Treat it as a restriction or sensitivity split only.  
**Confounders**: IPO status, trading halts, timestamp precision, target type, and benchmark availability.  
**Predicted effect direction**: Any real signal should attenuate in degraded-label cases because outcome misclassification adds noise.  
**Failure modes**: Too many quality levels or overly generous degradation flags. Collapse aggressively.  
**Framing support**: Substrate.

### Factor: Temporal by propagation interaction
**Concept**: Whether the pre/post cutoff contrast is stronger for duplicated clusters than for singletons.  
**Identification strategy**: Between-cluster 2x2 interaction on `pre_cutoff` and `duplicated`.  
**Statistical meaning (Decision 10)**: Effect-modification test. This is one of the few interactions with a coherent mechanistic interpretation.  
**Operationalization**: Cross Factor 1 with Factor 3 using binary coding only. Analyze as a single interaction term or as a pre-specified difference-in-differences style contrast. No 3x3 grids.  
**Number of levels + expected distribution**: 4 cells. Natural cell counts will depend heavily on sampling design.  
**Power at 1500 cases, OR=1.95 baseline**: Explicitly underpowered for confirmatory use. Even with a perfect `25/25/25/25` split, `1,500` gross and `20%` loss leaves about `300` scorable per cell. A within-stratum comparison is then `300 vs 300 = 600`, well below the `852` floor, and interaction terms require more information than that. This belongs in exploratory modeling only.  
**Confounders**: Reprint status, event family, and any time-varying change in cluster formation.  
**Predicted effect direction**: The pre-cutoff premium should be strongest in duplicated clusters if duplication is a genuine exposure-intensity proxy.  
**Failure modes**: Thin cells, especially if either pre/post or duplication is skewed.  
**Framing support**: Both.

## Primary vs secondary factor recommendation

For confirmatory pre-registration, I would keep the list narrow and binary:

1. **PRIMARY**: `pre_cutoff` vs `post_cutoff`. This is the closest thing to a treatment-like contrast and the easiest to power.
2. **PRIMARY**: `singleton` vs `duplicated` cluster. This is the cleanest cluster-native exposure-intensity proxy.
3. **PRIMARY, but as a control/stratifier rather than a headline hypothesis**: `target_scope` collapsed to `company` vs `non_company`, only if the curated core guarantees the minority bin is at least about `25%`; otherwise move it down one tier.
4. **PRIMARY CONTROL**: text length as a frozen adjustment variable, not a main hypothesis. If you insist on four confirmatory pre-registered fields, I would rather spend the fourth slot on a mandatory control than on an underpowered substantive split.

I would label the following **EXPLORATORY**:

1. `pre_cutoff_age` within pre-cutoff only.
2. `reprint_status`, conditional on adequate prevalence.
3. `temporal x propagation` interaction.

I would label the following **DESCRIPTIVE ONLY / ROBUSTNESS**:

1. `event_family` as a 3-level taxonomy.
2. `label_quality` slices.
3. Any finer `target_type`, sector, or market-cap tier breakdown.

On explicit non-recommendations: I would not make market-cap tier primary in the MVP because it is company-only, requires point-in-time mapping discipline, and tends to create thin cells once crossed with target scope. I would not make sector or 5-way event taxonomies primary because `1,500` is not enough for credible multi-cell confirmatory claims. I would also not pre-register any factor whose minority share lands below about `20-25%` in the frozen corpus unless the core sample is intentionally balanced to rescue it.
