# R-1c Target Salience — Stage 1 clean-room draft (Codex)

**Status**: Stage 1 independent conclusion, written before reading WS0.5 §3.3, WS0.5-era Target Salience proposal, R-1b whiteboard, or cross-synthesis R-1c sanity-check notes.

## Short Lock-In Candidate

My Stage 1 recommendation:

```text
Framing: CLS-measured corpus exposure proxy (C, with A-style wording discipline)
Construct: L1 entity-mention row, target mentioned anywhere in the article
Family: target_entity_id only, across all event types
Main variable: log1p(target_l1_row_count)
Window: fixed [CLS first published_at, min_fleet_model_cutoff), half-open
Tradable filter: no tradable filter for salience count
Focal article: exclude same article_id when it falls in the window
Dedup: no dedup across articles; one L1 row per (article_id, target_entity_id)
Discriminant: keep VIF >= 10 or |r| >= 0.90; fallback = target x non-case-super_type L1 complement count
Robustness: pre-commit one appendix tail-leverage sensitivity using percentile / winsorized log count; no cross-corpus slot in main design
```

The clean-room stance is deliberately simple: Target Salience should be the broad "how much this target appears in the visible CLS financial-news universe" factor. R-1b Recurrence already owns the event-family association channel. R-1c should not silently become a second recurrence metric.

---

## 1. Stance / Framing

### Candidate trade-off

- **A. CLS-internal prominence**: directly true. We can say "in CLS, this target is mentioned more." The weakness is that CLS is only one slice of model pretraining data.
- **B. General fame / public attention**: intuitively appealing, but it overclaims unless we bring in outside evidence such as search volume, page views, or other media corpora. That is not a minimal R-1c requirement.
- **C. Corpus exposure intensity, with CLS as proxy**: best fit. The quantity of interest is how often the model may have seen target-related text during pretraining. We cannot observe the full training corpus, so CLS mention volume is an observable proxy from the same domain and language.

### Main choice

Pick **C: corpus exposure intensity, proxied by CLS target exposure**, but write it with A-level honesty:

> Target Salience is the target entity's exposure intensity in the observable CLS financial-news corpus, used as a proxy for broader pretraining exposure to that entity.

This avoids two bad extremes. It does not claim CLS equals the whole web-scale training set, but it also does not demote the factor to a purely internal descriptive statistic with no link to memorization. The bridge is a proxy argument: a target that appears often in CLS is probably also more visible in finance news, reposts, investor discussions, summaries, and model-ingested Chinese web text. That bridge is plausible, not exact, and the paper should say so.

Carlini-style frequency scaling can be used only as an analogy with a guardrail: Carlini measures repetitions in the actual training data; R-1c measures repetitions in an observed domain corpus. The correct sentence is "training-data repetition increases extractability; CLS target mentions are our domain-specific proxy for that repetition," not "CLS count is training frequency."

### How this constrains the other decisions

- **Construct** should be broad exposure, not only subject rows. L1 mention fits better than L2 subject.
- **Family** should be target-only. Prominence is an entity property, not an event-family property.
- **Denominator** can be omitted because the fixed common window makes the corpus denominator constant across cases. Use count with log transform.
- **Window** should be fixed and common to the fleet, so the count is a case-level proxy and not a model-specific exposure variable.
- **Tradable filter** should not be part of salience. Fame does not require the entity to have been tradable at the mention date.
- **Discriminant check** is still required because target-only salience and target x event recurrence can be empirically correlated.
- **Robustness** should check tail leverage and proxy plausibility, not redefine the construct into a cross-corpus fame project.

### Compatibility

- **R-0**: uses an existing layer, L1. No new corpus layer. Factor is computed before operators. No dedup is allowed.
- **R-4a**: produces one continuous factor for effect-size + CI models; no family-wise correction needed for robustness labels.
- **R-1b**: stays distinguishable from the locked recurrence construct because R-1b is L2 subject + tradable + event_super_type.
- **Downstream**: gives R-1e and R-4b a simple continuous input with `log1p(0)=0`.

### R-5 sampling sanity check

This framing makes the sampling issue unavoidable: row-random sampling from news naturally over-samples entities with more news. That is not a flaw in the metric, but it means R-5 must explicitly choose whether the benchmark population is "CLS news cases as naturally distributed" or a more entity-balanced population. R-1c should not force Pool H, but it should hand R-5 a clear note: Target Salience is partly a media-coverage variable, so row-random sampling and salience are mechanically coupled.

### Downstream choice space

R-1e can still drop Salience if pilot collinearity or weak variance makes it redundant. R-5 can still choose row-random, Pool G, Pool H, or a combination. R-1c only defines the factor.

---

## 2. Construct

### Candidate trade-off

- **L1 mention**: count any `(article_id, target_entity_id)` row where the target is mentioned. Best match to "the model has seen text containing this entity." It does not care whether the target is the central subject.
- **L2 subject**: count only rows where the target is the article subject. Cleaner if we wanted "articles about the target," but narrower than exposure.
- **L3 L1 + tradable**: broad mentions plus tradability. This would require Pool D / L1 tradability extension and mixes fame with market eligibility.
- **L3 L2 + tradable**: exactly R-1b's base construct. Good for comparability, bad for discriminant validity.

### Main choice

Pick **L1 mention**, with count unit = **one L1 entity-mention row per article-target pair**.

The count should not sum `mention_count_in_article` as the main unit. If a CLS item mentions the same target five times, that is still one article-level exposure event. Intra-article mention frequency can be retained as provenance or future diagnostics, but the main Salience count should be rows, not repeated spans inside a single short wire item.

### Philosophy: same as R-1b vs separate from R-1b

I choose the **separate-from-R-1b** side.

The strongest same-construct argument is real: if both R-1b and R-1c used L2 subject + tradable, they would be measured on comparable rows, and the discriminant check would be easier to interpret. It also removes one source of variance.

But that argument makes R-1c too much like R-1b. Recurrence is "has this target had similar subject-level event histories before?" Salience is "how much target-containing text has the model likely seen?" Those are different channels. A side mention of 贵州茅台 in a sector article is not a recurrence of a specific event family, but it is still identity exposure. L1 mention is therefore the better construct for R-1c.

The price is that the R-1c/R-1b VIF comparison compares different row universes. That is acceptable because the check is empirical: do the resulting case-level values collapse into the same variable? They do not need identical construction to be tested for redundancy.

### Alternative and when to switch

Switch to **L2 subject without tradable** only if L1 extraction quality is poor enough that incidental mentions are mostly noise, or if L1 target matching creates many false positives. Do not switch to L2 subject + tradable merely to match R-1b; that would sacrifice the construct.

### Compatibility

- **R-0**: L1 is explicitly available and preserves non-tradable rows. No Pool D if we do not add tradable.
- **R-4a**: factor remains pre-operator.
- **R-1b**: intentionally different from R-1b's L2 subject + tradable reference rows.
- **B-2**: needs source layer, row unit, count unit, focal-article policy, no-dedup policy, and L1 extraction hashes.
- **Topic-classify range**: main target-only Salience does not require topic-classifying all L1 rows.

### R-5 sampling sanity check

L1 mention increases the mechanical link between salience and row-random sampling, because targets with more mentions also create more candidate cases. That is not a reason to narrow the construct; it is a note to R-5 that entity-balanced or salience-stratified sampling changes the target population.

### Downstream choice space

R-5 can cap articles per entity if it wants a less media-weighted benchmark. R-1e can decide whether this L1-based signal earns a primary slot after seeing pilot variance and collinearity.

---

## 3. Family Granularity / Event Collapse

### Candidate trade-off

- **Target only**: all mentions of the same target count together. This is the cleanest expression of entity prominence.
- **Target x complement-super_type**: counts mentions of the same target outside the case's event family. This avoids direct overlap with R-1b but makes salience event-dependent.
- **Target x all super_type with event-balance reweighting**: tries to keep all events while preventing high-frequency super-types from dominating. This is overbuilt for a first-order factor.
- **Industry or concept family**: not appropriate for target salience. It changes the construct from entity prominence to peer-group prominence.

### Main choice

Pick **target only**, across all event types:

```text
target_salience_count[case] =
  count L1 rows in fixed window
  where row.target_entity_id == case.target_entity_id
  and row.article_id != case.article_id
```

No event split in the main variable.

The reason is simple: if the question is "how visible is this target?", financial-report articles, regulatory articles, sector articles, and product articles all contribute. Excluding the case's own event super_type would make the value depend on which event type the current case happens to be, even for the same target. That is the wrong shape for a prominence factor.

### Why not complement as main

Complement-super_type is useful only as a fallback when the main target-only metric becomes empirically indistinguishable from R-1b recurrence. As the main metric it is conceptually odd: "茅台's earnings-news exposure does not count when the case is an earnings case" is not a defensible definition of prominence.

### Why not event-balanced weighting

Event-balance weighting asks reviewers to trust a custom weighting scheme before we have evidence that unweighted target count fails. It also makes the metric harder to explain. For a characterization benchmark, that is unnecessary complexity.

### Compatibility

- **R-0**: target-only can be computed from L1 after entity matching and before topic classification.
- **R-4a**: one continuous variable, zero allowed.
- **R-1b**: main family differs from `(target_entity_id, event_super_type)`, supporting discriminant validity.
- **Downstream**: R-4b gets raw count, log count, zero rate, and distribution by target and perhaps by case event type.

### R-5 sampling sanity check

Target-only salience is exactly the variable most coupled with row-random media coverage. If R-5 wants to avoid the benchmark being dominated by a few highly covered entities, Pool H entity-balanced or capped sampling is the relevant lever. R-1c should not require it, because the natural CLS population is also a legitimate population.

### Downstream choice space

If R-5 uses Pool G, R-1c recommends using this salience metric for salience strata once available, rather than using recurrence as a proxy for salience. Recurrence can remain a separate stratification axis if R-5 has enough sample budget.

---

## 4. Denominator

### Candidate trade-off

- **`log1p(count)`**: simplest and closest to frequency-scaling literature. Because the window is fixed, the corpus denominator is constant across cases.
- **Per-article share**: divides by a constant if the same fixed window is used. Adds tiny decimal scales without changing the conceptual signal.
- **Per-L1-row or all-target share**: also mostly a constant rescaling under fixed window. Useful as provenance, not as main factor.
- **Industry share**: changes the question to within-industry visibility. That may be useful elsewhere, but it is not target salience.
- **Rank / percentile**: robust to extreme tails, but loses absolute scale and weakens the frequency interpretation.

### Main choice

Pick **`log1p(target_l1_row_count)`**.

This is the most defensible main form. Count is the observable exposure proxy; `log1p` handles the heavy tail and keeps zero valid. Since the lookup window is shared across all cases, a denominator does not solve a real comparability problem. It mostly changes scaling.

The raw count should still be stored. B-2 should also store corpus-wide denominators such as number of S0 articles and number of L1 rows in the window for provenance, but they are not part of the main variable.

### Alternative and when to switch

Use a **percentile / winsorized log count appendix** if pilot distribution shows a few mega-targets dominate variance or if coefficient estimates are visibly leverage-sensitive. Do not make percentile the main metric unless raw counts are unusably skewed.

### Compatibility

- **R-0**: `log1p(0)=0` legal; no-dedup legal.
- **R-4a**: effect size + CI can use a continuous transformed predictor.
- **R-1b**: transform matches R-1b's log count but construct/family differ.
- **R-4b**: pilot can estimate variance, zero rate, tail concentration, and collinearity.

### R-5 sampling sanity check

Using counts rather than ranks preserves the natural skew that row-random sampling also reflects. That can amplify high-salience targets in the sampled frame. R-5 should decide whether it wants to preserve or balance that skew; R-1c should not hide it by using percentiles as the main metric.

### Downstream choice space

R-4b can standardize the logged value for modeling. R-1e can compare raw-log and percentile sensitivity when choosing final factors.

---

## 5. Lookup Window

### Candidate trade-off

- **Shared fixed `[corpus_start, min_cutoff)`**: common exposure slice visible to every model in the fleet. Clean case-level factor.
- **Case-relative `[T-X, case_time)`**: intuitive for "prior target fame" but bad for post-cutoff cases because it counts text later than some models' cutoffs.
- **Fixed latest cutoff**: gives more data but includes periods not visible to early-cutoff models, weakening the common-exposure interpretation.
- **Per-model window**: conceptually closer to actual exposure, but turns Salience into case x model and collides with Cutoff Exposure.

### Main choice

Pick the **same fixed half-open window as R-1b**:

```text
[CLS first published_at, min(fleet model cutoff))
```

This is conservative. It uses only the part of CLS that all fleet models could have seen. It keeps Salience as a case-level factor and makes the R-1b discriminant check cleaner.

The right endpoint should come from `config/fleet/r5a_fleet.yaml`. The start is constrained by CLS availability, roughly 2020-01.

### Alternative and when to switch

Do not switch to latest cutoff or per-model windows in R-1c. If later work wants model-specific target exposure, that is a different factor, closer to Cutoff Exposure. A window-length appendix can be used to check stability, but not to redefine the main factor.

### Compatibility

- **R-0**: fixed window is allowed.
- **R-4a**: case-level factor remains independent of operators.
- **R-1b**: same window supports direct collinearity checks.
- **Downstream**: R-4b can compute one distribution for all cases rather than a case x model matrix.

### R-5 sampling sanity check

The fixed early window means a target's salience is measured before mid-2024 even for 2025-2026 cases. For targets whose media coverage changed sharply after mid-2024, row-random sampling may include many new cases whose salience is intentionally still "common pre-min-cutoff exposure." R-5 should be aware of this but should not change the window in sampling.

### Downstream choice space

R-1a remains responsible for model cutoff timing. R-1c should not absorb that role.

---

## 6. Tradable Filter

### Candidate trade-off

- **Add tradable filter**: aligns more closely with R-1b and market-outcome availability, but it makes salience depend on whether the entity was tradable when mentioned.
- **No tradable filter**: matches prominence/exposure. A model can see text about an entity before listing, during suspension, or in non-tradable contexts.
- **Mixed numerator/denominator filter**: hard to explain and not needed if main metric is count.

### Main choice

Pick **no tradable filter** for Target Salience.

Prominence and tradability are orthogonal. The fact that an entity was not tradable on a historical mention date does not make that mention disappear from model pretraining. Adding a tradable filter would also require extending L1 with point-in-time tradability if we keep the L1 construct, triggering Pool D for a filter that does not serve the salience claim.

Benchmark cases themselves still come from L3 base view, so the focal case target is tradable at event time. This decision only affects historical reference rows used to estimate salience.

### Construct consistency vs claim fit

The "same ruler as R-1b" argument is weaker here than it looks. R-1b uses tradability because it is an outcome-leakage proxy: if a target was not tradable, there may be no clean market outcome. R-1c does not need that condition. For salience, the better ruler is "does the model see target-containing text?" not "could this mention have had a tradable outcome?"

The VIF interpretation becomes "are these two final case-level variables redundant?", not "were they counted from identical rows?" That is still the right discriminant question.

### Alternative and when to switch

Switch to L2 subject + tradable only if R-1e decides Target Salience must be a market-outcome exposure factor rather than an entity-exposure factor. That would be a framing change, not a minor implementation tweak.

### Compatibility

- **R-0**: L1/L2 retain non-tradable rows as objects; L3 filters only benchmark subjects.
- **Pool D**: not triggered in main R-1c because no L1 tradability filter is needed.
- **R-1b**: explicitly different from R-1b's tradable-filtered recurrence.
- **B-2**: provenance should record `tradable_filter = none_for_salience_reference_rows`.

### R-5 sampling sanity check

No tradable filter may increase salience for entities with pre-listing or non-tradable coverage. That is a feature under the exposure framing. R-5 should not interpret salience as "tradable-market attention"; it is broader "financial-news identity exposure."

### Downstream choice space

R-5 still samples from tradable benchmark cases. R-1c does not require sampling non-tradable focal cases.

---

## 7. R-1b Discriminant Check Boundary

### Threshold

Keep the standing threshold:

```text
VIF >= 10 or |r| >= 0.90
```

Do not tighten it. Salience and recurrence both come from CLS counts and will naturally correlate for famous targets. A moderate correlation is expected and not a design failure. The threshold should catch near-duplication, not punish related but distinct constructs.

Do not loosen it either. If a target-only salience metric is almost identical to target x event recurrence in the observed sample, the benchmark should not pretend it has two independent factors.

### Main comparison

Compare:

```text
R1c main: log1p(target_l1_row_count)
R1b locked: log1p_recurrence_count
```

The R-1b input is the locked L2 subject + tradable + `(target_entity_id, event_super_type)` count.

### Fallback metric

If the threshold triggers, switch R-1c to a **complement-family salience fallback**:

```text
fallback_salience_count[case] =
  count L1 rows in the same fixed window
  where row.target_entity_id == case.target_entity_id
  and row.article_id != case.article_id
  and row.event_super_type != case.event_super_type

fallback_target_salience = log1p(fallback_salience_count)
```

This fallback keeps the salience construct broad and L1-based, but removes the case's own event super_type from the count. It is less intuitive than target-only, so it should not be main by default. It is still more interpretable than residualizing salience against recurrence, because residuals depend on the sampled dataset and are hard to reproduce as a standalone factor.

If the fallback still violates the threshold, stop patching. R-1e should treat Target Salience and Recurrence as empirically redundant and choose one or demote one.

### Compatibility

- **R-0**: fallback needs `event_super_type` on L1 rows, so it may require expanding topic-classify scope to L1 target rows in the fixed window. That is a conditional implementation cost, not a main-design cost.
- **R-4a**: fallback is still a pre-operator factor.
- **R-1b**: explicitly honors the standing discriminant routine.
- **B-2**: provenance must record both the main metric and whether fallback activated.

### R-5 sampling sanity check

The discriminant check must be run on the actual analysis frame or pilot frame, not only the full corpus, because sampling can change correlation. Entity-balanced sampling can reduce salience/recurrence coupling; row-random sampling can increase it.

### Downstream choice space

R-1e decides what to do if both main and fallback are redundant. R-1d is not involved.

---

## 8. Robustness / Appendix Candidates

### Candidate trade-off

- **Zero pre-committed slots**: cleanest, but R-1c's count metric is likely heavy-tailed, so some tail check is useful.
- **Share-vs-count**: not very informative under a fixed common window because denominator is constant.
- **Cross-corpus signal**: only mandatory if we choose general fame framing. We did not.
- **Window-length sensitivity**: useful but can become a mini design grid.
- **Tail-leverage sensitivity**: directly addresses the main statistical risk of salience counts: a few mega-visible targets may drive the coefficient.

### Main choice

Pre-commit **one appendix robustness slot**:

```text
Appendix tail-leverage sensitivity:
  re-run the R-1c coefficient using either
  (a) percentile rank of target_l1_row_count within targets, or
  (b) winsorized log1p count at predeclared tails,
  with the exact choice fixed by B-2/R-4b before pilot analysis.
```

This is not a second main metric. It asks a narrow question: does the salience effect survive when the very top of the target-count distribution cannot dominate the fit?

Do **not** pre-commit a cross-corpus fame slot. It would make R-1c depend on outside data quality and coverage. A future paper or optional appendix can correlate CLS salience with Baidu/Wiki/other-media signals if those data are easy, but the main benchmark should not require them.

Do **not** pre-commit share-vs-count as a headline robustness. With a fixed corpus window, share is mostly a rescaled count.

### Compatibility

- **R-0/R-4a**: appendix label is allowed; no family-wise multiplicity correction required.
- **R-1b**: discriminant fallback is separate from this robustness slot.
- **R-4b**: can include the appendix metric in power/variance diagnostics if needed, but primary power should use the main log count unless R-1e selects otherwise.

### R-5 sampling sanity check

Tail-leverage sensitivity is also a sampling sanity check. If row-random sampling gives many observations from a few high-salience targets, the appendix can show whether the coefficient is merely a mega-target effect. It does not replace R-5's decision about entity balancing.

### Downstream choice space

R-4b chooses exact standardization / winsor cutoffs before main analysis. R-1e decides whether the main R-1c metric enters primary after pilot effect size, variance, and collinearity are known.

---

## B-2 Schema Content Needs From Stage 1

R-1c should ask B-2 to record, at minimum:

- `source_layer = L1_entity_mention`
- `row_unit = [article_id, target_entity_id]`
- `count_unit = L1_entity_mention_row`
- `target_family_key = [target_entity_id]`
- `main_reference_rows_filter = target_entity_id match; no tradable filter; fixed window; exclude same article_id`
- `window = [cls_corpus_first_published_at, min_fleet_model_cutoff)`, half-open
- `fleet_cutoff_manifest_hash`
- `focal_article_policy = exclude_same_article_id`
- `dedup_policy = no_dedup_across_articles; one row per article-target; do not sum mention_count_in_article in main`
- `zero_policy = keep_zero_log1p_zero`
- `transform = log1p`
- `denominator = none_for_main; corpus totals stored for provenance only`
- `tradable_filter = none_for_salience_reference_rows`
- `pool_d_required = false`
- `topic_classify_required_for_main = false`
- `topic_classify_required_for_fallback = true_if_discriminant_fallback_activated`
- `fallback_policy = complement_super_type_l1_count if VIF/correlation threshold triggers`
- `tail_sensitivity_metric = percentile_or_winsorized_log_count appendix`

## Stage 1 Final Recommendation

R-1c should define Target Salience as an L1, target-only, no-tradable, fixed-window, log-count exposure proxy. It should not inherit R-1b's L2 subject + tradable construct because that would collapse a prominence channel into an event-recurrence channel. The main design is intentionally minimal; the only guards are the standing R-1b discriminant check and one appendix tail-leverage sensitivity.
