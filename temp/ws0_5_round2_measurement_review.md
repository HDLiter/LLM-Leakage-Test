# WS0.5 v0.3 — Round 2 Review (Measurement / Construct Validity Lens)

**Reviewer**: GPT-5.5 xhigh (Measurement role)
**Date**: 2026-05-19
**Memo**: docs/DECISION_20260518_ws0_5_thales_alignment.md (v0.3)
**Round-1 review verified against**: temp/ws0_5_round1_measurement_review.md

## TL;DR

v0.3 resolves the five round-1 measurement issues at the construct-claim level. The memo now makes Target Salience a selected-market-target reach composite, treats recurrence as CLS recurrence density rather than observed training exposure, preserves construct-nearer recurrence sensitivities, and keeps Authority as a conditioned adjunct/covariate.

I do not see a new construct-integrity blocker. The remaining risks are paper-language guardrails: do not let `relative_recurrence_within_super_type_high` read as an absolute exposure dose, do not interpret `target_validity_low` as substantively low target exposure, and document `model_cutoff` provenance in the factor schema/manifest.

## 1. Issue-by-issue verification (C-1 to C-5)

| Issue | Status (patched / partial / unaddressed) | Notes |
|---|---|---|
| C-1 Target Salience composite + veto | patched | §3.3 now narrows the construct to a selected-market-target reach composite; `context_gate=0` becomes `target_validity_low=true` and `ordinal_reported=NA`, not low exposure. Raw reach components are retained. |
| C-2 recurrence pre-case vs model-visible | patched | §5.1 renames the primary to `pre_case_cls_family_recurrence`, explicitly calls it CLS recurrence density, and adds case × model `recurrence_count_visible_to_model` censored at `min(T, model_cutoff[model_id])`. |
| C-3 within-super_type weakens dose | patched | §5.2 and §5.5 frame the primary binary label as relative recurrence within event family, not absolute exposure dose; `log1p_recurrence_count` and absolute-count sensitivity are retained with interpretation rules. |
| C-4 no-dedup CLS editorial | patched | §5.1 and §5.2 keep no-dedup primary but add `recurrence_count_clustered`, `recurrence_count_first_per_day`, and `duplicate_ratio` to separate feed duplication from broad recurrence. |
| C-5 v5.5 Authority conditioning | patched | §3.4 states that if v5.5 wins, Authority is conditional on predicted Modality and cannot be treated as an independently measured Bloc 3 dimension. |

## 2. Detailed verification

### C-1: Target Salience composite + centrality veto

Round-1 concern: v0.2 measured a product of target reach, tradability/scope, and text-local target validity, while claiming something close to target training exposure. The specific blocker was that `context_gate=0` forced high-reach but weak-context targets into the low ordinal category.

v0.3 fixes the construct claim. §3.3 now says Target Salience is a **selected-market-target reach composite**, proxying expected pretraining exposure to the forecastable target, not pure cross-corpus fame independent of tradability, scope, or target-selection validity.

v0.3 also fixes the veto semantics. §3.3.2 defines:

```text
target_validity_low = (context_gate == 0)
ordinal_admitted = static_reach-derived 1/2/3
ordinal_reported = ordinal_admitted if not target_validity_low else NA
```

That is the measurement distinction round-1 asked for. A weak article-target fit is now a quality/validity flag, not evidence that the target has low global reach.

The raw component preservation patch is present. §3.3 records `listed_flag`, `index_membership`, `market_cap_bucket`, `scope_class`, and `target_family` as factor-table fields for sensitivity checks. §9 also makes those fields part of the required `factor_schema.yaml` closure condition.

The remaining paper-writing requirement is simple: the paper should use names like "selected forecast-target reach" or "selected-market-target reach composite." It should not shorten this to pure "target fame" or "target exposure" without the forecastable-target qualifier.

Status: **patched**.

### C-2: Pre-case recurrence vs model-visible recurrence

Round-1 concern: the v0.2 recurrence count used `[T - 24mo, T)`, which can include articles after an older model's training cutoff. That is a valid pre-case corpus-density measure, but not directly model-visible training exposure.

v0.3 fixes the primary label and interpretation. §5.1 defines the primary variable as `pre_case_cls_family_recurrence` and states that it is a **CLS recurrence density** measure proxying model training-exposure intensity. It explicitly says it is not identical to model-visible training recurrence.

The requested model-cutoff-censored sensitivity is present:

```text
recurrence_count_visible_to_model[case_id, model_id] =
  COUNT(matched_articles where date in [T - 24mo, min(T, model_cutoff[model_id])))
```

This addresses the construct mismatch because the sensitivity is case × model, while the primary remains case-level for the confirmatory factor matrix.

The `model_cutoff` data source is reasonable at memo level. §2.4 already treats `model_cutoff` as an input to Cutoff Exposure from the manifest, and §5.1 reuses that same model-level field. Measurement-side, that is the right source of provenance: the recurrence sensitivity should inherit the exact observed/asserted cutoff used for Cutoff Exposure, not introduce a second cutoff source.

One paper/schema guardrail remains: if any model cutoff is approximate or provider-asserted rather than directly observed, call the field "manifest-cutoff-censored" or "declared-cutoff-censored" in methods. This is a wording/provenance note, not a construct blocker.

Status: **patched**.

### C-3: Within-super_type percentile vs exposure dose

Round-1 concern: within-super_type percentile is defensible for separating recurrence from event-family base rates, but it is weaker than absolute count for the latent "times seen" construct.

v0.3 resolves this by changing the construct language, not by pretending the percentile is dose. §5.2 names the confirmatory binary label `relative_recurrence_within_super_type_high` and annotates it as "unusually recurrent for this event family, NOT absolute exposure dose."

The construct-nearer sensitivity fields are retained. §5.1 and §5.2 store `log1p_recurrence_count`; §5.2 also stores `absolute_high_recurrence` and pre-registers interpretation rules for cases where within-type and absolute/log recurrence agree or diverge.

The primary choice is still weaker than an absolute dose if the paper's headline claim is "training exposure intensity." But v0.3 no longer makes that overclaim. The primary now supports a narrower claim: conditional recurrence relative to comparable event family.

The §5.5 "provisional designation" is also appropriate. It says the final lock occurs after S4 diagnostics, and that instability or high redundancy can trigger a mechanical switch to absolute/log count with a signed addendum. That gives the design a defensible measurement escape hatch without reopening the whole architecture now.

Status: **patched**.

### C-4: No-dedup CLS count and editorial/feed repetition

Round-1 concern: no-dedup recurrence is constructively plausible as exposure density, but without deduped sensitivity it can be attacked as measuring CLS feed mechanics.

v0.3 keeps the no-dedup primary while narrowing its interpretation. §5.1 says the primary is within-CLS no-dedup recurrence density, not an observed global training-corpus duplication count.

The requested sensitivity fields are present:

```text
recurrence_count_clustered
recurrence_count_first_per_day
duplicate_ratio
```

These fields let the paper separate "many distinct similar events" from "same story repeated in the feed." That was the key construct-validity repair.

This is paper-ready as long as the methods section keeps the same wording: raw no-dedup CLS recurrence is a proxy corpus-density measure, not direct evidence about the full pretraining mixture.

Status: **patched**.

### C-5: v5.5 Authority conditioning on Modality

Round-1 concern: if v5.5 wins, Authority is measured downstream of predicted Modality. It should not be interpreted as an independently measured source-credibility dimension.

v0.3 adds the needed caveat in §3.4. It says that under v5.5 two-pass, Authority is conditional on predicted Modality, is descriptive adjunct/covariate only, and any future confirmatory or interaction use requires independent authority operationalization.

This directly answers the round-1 issue. It also keeps Authority aligned with the frozen design: not one of the four confirmatory factors, not a restored extra-corpus P1 signal, and not a separately measured Bloc 3 construct under v5.5.

Status: **patched**.

## 3. New construct risks introduced by v0.3

No new measurement-side blocker found.

`relative_recurrence_within_super_type_high` as primary does make the recurrence claim narrower. That is acceptable because v0.3 explicitly frames it as relative recurrence within event family and stores absolute/log sensitivities. The paper must not collapse this back into "high exposure dose" language.

`target_validity_low` is now construct-cleaner than the v0.2 veto. The field should be treated as a validity/missingness/quality status in analysis tables, not as a fourth or hidden low-salience category. v0.3's `ordinal_reported=NA` rule is clear enough.

`recurrence_count_visible_to_model` depends on `model_cutoff[model_id]`. This is appropriate because Cutoff Exposure already depends on the same manifest cutoff. The factor schema should record whether each cutoff is observed, provider-declared, or researcher-imputed; if imputed, the sensitivity is still useful but should not be marketed as exact model visibility.

The recurrence family now has multiple related manifestations: case-level CLS density, relative within-family high/low, log absolute count, clustered count, first-per-day count, and model-visible count. This is not a validity problem if the confirmatory/sensitivity distinction stays explicit. It would become a problem only if the paper selectively interprets whichever version is favorable after seeing results.

The target construct remains intentionally composite: reach, tradability, scope, and forecast-target eligibility move together. v0.3 now names that composite honestly and preserves components, so the residual confounding is a limitation rather than a design flaw.

## 4. Final verdict

**Verdict**: APPROVE

**修订后需 re-review section**: None.

**建议下一步**: Proceed to user sign-off / S1 implementation with two writing-time guardrails carried forward into `factor_schema.yaml` and the paper methods: label Target Salience as selected-market-target reach, and label the recurrence primary as relative within-family CLS recurrence rather than absolute exposure dose.
