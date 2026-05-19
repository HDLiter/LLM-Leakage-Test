# WS0.5 v0.2 — Round 1 Review (Measurement / Construct Validity Lens)

**Reviewer**: GPT-5.5 xhigh (Measurement role)
**Date**: 2026-05-19
**Memo**: docs/DECISION_20260518_ws0_5_thales_alignment.md (v0.2)

## TL;DR

**Verdict: MAJOR-REVISIONS-NEEDED.** v0.2 is no longer under-specified: Target Salience, Historical Family Recurrence, and Bloc 3 status now have operational rules. The remaining problem is construct integrity: Target Salience currently measures a composite of target fame, tradability/scope, and article-centrality validity, while Historical Family Recurrence measures CLS recurrence before the case date rather than model-visible recurrence before each model cutoff.

These are fixable without reopening the R5A 4-factor architecture. The memo needs narrower construct claims, explicit sensitivity fields, and two measurement patches: split target-validity gating from target exposure scoring, and record model-cutoff-censored recurrence alongside the case-date count.

## 1. Target Salience construct integrity (§3.3)

### 1.1 Selection rule (tradable-only + centrality)

**Verdict: acceptable for P_predict manifest construction, weaker for the training-exposure construct.**

The tradable-only pool solves an operator problem: `P_predict` needs a financial target that can sensibly receive a direction/alpha label. But this is not the same as selecting the entity with the largest expected training exposure. Macro/policy actors, regulators, countries, and official bodies may be high-exposure targets in pretrained corpora; v0.2 rejects many of these when no tradable company/sector/index/ETF/commodity is available. For policy news, the selected sector/index target may be a market proxy for the article, not the true high-exposure source entity.

Centrality-first selection is article-faithful, which is good for target validity. The measurement caveat is that "article protagonist" and "cross-corpus training exposure" are not identical. A blue-chip company appearing as a non-central body mention can have higher global training exposure than a small IPO company that is central in its own announcement. The selection rule therefore defines **eligible forecast target salience**, not general target exposure.

Suggested memo patch: rename the construct claim from "cross-corpus training exposure to the target" to "cross-corpus exposure proxy for the selected forecastable market target." This narrower language is defensible.

### 1.2 static_reach 量级

**Verdict: face-valid at the high end, coarse and heterogeneous at the middle/low boundary.**

`static_reach = 3` has strong face validity: SSE50/CSI300/top-cap names, broad indices, and nationally dominant sectors are plausibly much more represented across financial news, filings, encyclopedic pages, market data, and commentary.

`static_reach = 2` is a wide bin. "普通 listed", CSI500, major unlisted firms, recognized sectors, and specific ETF/index products can differ by orders of magnitude in mention frequency. The ordinal step from 2 to 3 is not guaranteed to represent a stable exposure ratio; it is a rank category.

`static_reach = 1` is also mixed. Small-cap listed companies, unlisted local firms, narrow products, and local institutions do not share the same likely training exposure. If the pilot has only about 16 low cases, binary collapse will make the low side especially heterogeneous.

Patch: store the raw components that generated `static_reach` (`listed_flag`, `index_membership`, `market_cap_bucket`, `scope_class`, `target_family`) and report known-groups ordering. Do not imply interval-scale dose from 1/2/3.

### 1.3 context_gate as veto

**Verdict: major construct creep.**

The memo says text-local signals are only a gate, not the main salience signal. That helps, but the current formula still makes `context_gate` a veto: `context_gate = 0` forces `ordinal = 1` regardless of `static_reach`. This changes the measured construct from target exposure to **target exposure × article-centrality/selection confidence**.

That product is not wrong as a manifest-quality rule, but it is not pure training exposure. A small IPO company that is headline/core with `static_reach = 1` and an SSE50 company that appears weakly with `static_reach = 3, context_gate = 0` both become low. The first likely has low training exposure; the second likely has high global target exposure but weak article fit. They fail for different reasons and should not be made measurement-equivalent.

Patch: split `context_gate` into a target-validity/quality field. Recommended rule:

- `context_gate = 0` should trigger exclusion, adjudication, or `target_validity_low = true`, not automatic low exposure.
- `target_salience_ordinal` should be driven by `static_reach` once a target is admissible.
- If v0.2 keeps the veto, paper language must call the factor "validated target salience" or "forecast-target salience", not "target training exposure."

### 1.4 Tradability + Scope absorbed

**Verdict: major confounding risk.**

Tradability and salience are different constructs. Tradability is a discrete market-structure property; salience/fame is an ordinal prominence property. Scope is yet another property: broad market, sector, firm, local product, institution. Absorbing them into `static_reach` is pragmatic for the 20-coefficient budget, but any high-vs-low Target Salience contrast will vary famousness, tradability, and scope together.

This does not force separate confirmatory factors. It does require honest construct labeling. The factor is not "famousness" alone; it is a **market-reach composite**. The memo should preserve component fields for sensitivity and should not claim the Target Salience coefficient isolates salience from tradability/scope.

## 2. Historical Family Recurrence construct integrity (§5)

### 2.1 Case-date vs model-cutoff misalignment

**Verdict: major measurement error against the stated construct.**

The construct claim is "how often the model probably saw similar patterns during training." The current count is case-level: CLS articles in `[T - 24 months, T)`. That is a valid **pre-case CLS recurrence density** measure. It is not necessarily a valid model-visible training exposure measure.

For a case dated 2024-03-15 and a model cutoff around 2023-10, the current window includes roughly five months of CLS items the model could not have seen. This is not a small conceptual issue, because Cutoff Exposure is already model-specific in the R5A design. A case-level recurrence count can overstate exposure for older-cutoff models and understate the distinction between pretraining-visible and merely pre-event recurrence.

Patch: keep the case-level count if needed for the confirmatory matrix, but add a model-specific sensitivity field:

`recurrence_count_visible_to_model = count([T - 24mo, min(T, model_cutoff_observed_or_asserted)))`

If the main factor remains case-level, rename it to `pre_case_cls_family_recurrence` and state that it is a proxy for corpus recurrence density, not a direct observed training count.

### 2.2 Within-super_type percentile vs absolute count

**Verdict: acceptable as a multicollinearity control, weak as the primary exposure dose.**

Within-super_type percentile removes base-rate dominance by event family. That is useful if the paper wants recurrence to be separable from Event Type / super_type. But it also discards absolute magnitude. A very common issuer_quant family with 24 matched prior items and a moderate issuer_quant family with 8 matched prior items can both be above-median or below-median within the same slice, while their plausible exposure ratio is 3:1.

This matters because the latent construct is "times / intensity seen during training." Absolute count is closer to that construct than percentile rank. Percentile rank is closer to "unusually recurrent for this event family."

Patch: define the primary label explicitly as `relative_recurrence_within_super_type`. Store and report `log1p(recurrence_count)` as the construct-nearer continuous sensitivity. If S4 later permits, consider using absolute count with super_type adjustment rather than percentile as the primary analysis field.

### 2.3 No dedup as construct choice

**Verdict: defensible but under-defended.**

The no-dedup choice has a coherent rationale: repeated media items can reflect repeated exposure in training corpora. However, the recurrence source is a single CLS mirror. CLS-internal repetitions can reflect CLS editorial practices, feed formatting, or follow-up conventions, not necessarily cross-corpus global duplication. Cross-source duplication through Xinhua, CCTV, exchange filings, company announcements, and other outlets is a different phenomenon from within-CLS re-post density.

No-dedup should therefore be framed as measuring **CLS recurrence density**, not global corpus recurrence. The paper should also retain a deduped or clustered sensitivity count: unique event clusters, first-per-day count, or duplicate ratio. This would let the authors distinguish "many distinct similar events" from "one story reprinted many times."

## 3. Bloc 3 — Modality + Authority

### 3.1 Conceptual overlap

**Verdict: acceptable if Authority remains a covariate/adjunct, risky if interpreted as independent.**

Modality and Authority are not identical constructs. Modality asks how information is disseminated; Authority asks what source class is being traced. But in financial news, they are strongly coupled: OFFICIAL_ANNOUNCEMENT and REGULATORY_FILING nearly imply OFFICIAL or CORPORATE authority, while RUMOR often implies UNKNOWN or low authority.

v0.2 is correct that Authority is not one of the four confirmatory factors and not in the frozen Bloc 3 interaction menu. The conceptual issue is that making Modality confirmatory and Authority a covariate is a design-budget decision, not proof that the two are construct-independent. Paper language should say Authority is used to describe or adjust the Modality landscape, not that it isolates a separate source-credibility dimension.

### 3.2 Two-pass v5.5 vs single-pass V2 measurement implications

**Verdict: v5.5 improves authority accuracy but weakens measurement independence.**

In v5.5, Authority is conditioned on predicted Modality. That is reasonable for annotation accuracy, but it makes the measured Authority value partly downstream of the Modality measurement. If both variables enter an interaction or regression as if independently observed case attributes, the model is using two partly coupled measurements.

Because Authority is non-confirmatory, this is not a blocker. The memo should add a warning: if v5.5 wins, Authority cannot be interpreted as independently measured from Modality. If Authority later becomes analytically important, use an independent authority pass, publisher metadata, or KG lookup.

## 4. 4-factor independence — conceptual

The four confirmatory factors are defensible as dimensions of the same latent exposure construct:

- Cutoff Exposure = temporal availability
- Historical Family Recurrence = recurrence of similar entity/event patterns
- Target Salience = prominence/reach of the selected target
- Template Rigidity = surface/schema repetition

They are not conceptually orthogonal. High-salience targets tend to appear in more articles, which raises recurrence. Highly recurrent event families often have stable templates, which raises Template Rigidity. This overlap is not just a statistical nuisance; it is part of the causal story of training exposure.

Do not redesign the confirmatory matrix in WS0.5. The patch is rhetorical and diagnostic: call these "four exposure-relevant dimensions" rather than "independent factors," and treat Spearman/VIF checks as discriminant diagnostics, not as conceptual proof. A future paper can discuss whether Recurrence + Template Rigidity form a repetition super-factor, but that is outside this memo.

## 5. Paper reviewer attack vectors

| Reviewer question | v0.2 defense strength | Suggested patch |
|---|---|---|
| "Your Target Salience high/low cases differ in importance, news volume, market visibility, tradability, and article centrality. How do you isolate training exposure?" | weak | Narrow the claim to "selected market-target reach composite"; split target validity gate from salience; preserve raw static-reach components; add salience × recurrence cross-tab. |
| "Historical Family Recurrence uses CLS-internal counts. Why should CLS recurrence equal model training exposure?" | acceptable but incomplete | Call it CLS recurrence density; add deduped/clustered sensitivity; state CLS is a proxy corpus, not the true training corpus. |
| "Your 24-month pre-case window includes articles after some model cutoffs. How can those be training exposure?" | weak | Add model-cutoff-censored recurrence sensitivity and avoid saying the primary count is directly model-visible. |
| "Within-super_type percentile throws away absolute frequency. Isn't 24 prior items more exposure than 8?" | weak | Keep percentile only as relative recurrence; report log absolute count and decide at S4 whether absolute count should be primary. |
| "Authority and Modality are collinear. Why is one confirmatory and the other only a covariate?" | acceptable | Say this follows the frozen Bloc 3 inventory and page/alpha budget, not construct independence; Authority is an adjunct descriptor. |
| "If v5.5 Authority is conditioned on predicted Modality, are these independent measurements?" | acceptable for covariate use, weak for interaction claims | Add a caveat that v5.5 Authority is conditioned and should not be interpreted as independent; use independent/metadata Authority if elevated later. |

## 6. Critical construct issues

### Issue C-1: Target Salience is a market-reach composite with a centrality veto (major)

**问题**: `static_reach` mixes famousness, tradability, and scope; `context_gate = 0` then forces high-reach weak-context targets into low salience. This measures validated forecast-target reach, not pure cross-corpus training exposure.

**建议**: Split target validity from salience. Use `context_gate` for exclusion/adjudication/quality flag, and let `static_reach` define salience after admissibility. If retaining the formula, rename the construct and preserve raw components.

**可 paste 文本**:

> Target Salience is operationalized as a selected-market-target reach composite. It is intended to proxy expected pretraining exposure to the forecastable target, not to isolate fame independently from tradability, scope, or target-selection validity. `context_gate` is a target-validity safeguard; cases with weak target validity are flagged or excluded rather than interpreted as substantively low-exposure targets. Component fields used to derive `static_reach` are retained for sensitivity checks.

### Issue C-2: Historical Family Recurrence is pre-case, not necessarily model-visible (major)

**问题**: `[T - 24mo, T)` can include CLS items after an older model's cutoff. This directly conflicts with the claim "the model probably saw similar patterns during training."

**建议**: Add model-cutoff-censored recurrence as sensitivity or case×model auxiliary field. Rename primary count if it remains case-level.

**可 paste 文本**:

> The primary recurrence variable is a case-level pre-case CLS recurrence density measure. Because model cutoffs differ, it is not identical to model-visible training recurrence. We therefore store `recurrence_count_visible_to_model`, censoring the upper bound at `min(case_time, model_cutoff)`, and use it as a sensitivity check for cutoff-sensitive estimands.

### Issue C-3: Within-super_type percentile weakens the exposure-dose construct (major)

**问题**: Percentile binning protects against super_type base rates but suppresses absolute count differences that are closer to the latent "times seen" construct.

**建议**: Treat percentile as relative recurrence. Store `recurrence_count`, `log1p_recurrence_count`, and percentile. At S4, decide whether absolute/log count with super_type adjustment is a better primary field.

**可 paste 文本**:

> The within-super_type percentile should be interpreted as relative recurrence within event family, not as an absolute exposure dose. Absolute recurrence count and `log1p(count)` are retained because they are construct-nearer measures of repetition intensity; percentile binning is used only to reduce event-family base-rate dominance.

### Issue C-4: No-dedup raw CLS count may index CLS editorial repetition (minor/major)

**问题**: Raw count plausibly captures exposure density, but within-CLS repetition is not the same as cross-corpus repetition. Without a deduped sensitivity field, a reviewer can argue the factor measures CLS feed mechanics.

**建议**: Keep no-dedup primary if desired, but add event-cluster or first-per-day sensitivity and report duplicate ratio.

**可 paste 文本**:

> We intentionally retain raw CLS recurrence because repeated feed items can contribute to exposure density. To distinguish broad recurrence from feed-level duplication, we also store a deduped/clustered recurrence sensitivity and a duplicate-ratio field. The main paper interprets the raw measure as CLS recurrence density, not as an observed global training-corpus count.

### Issue C-5: v5.5 Authority is conditioned on Modality (minor)

**问题**: If v5.5 wins, Authority is not independently measured from Modality. This matters if both are later used as if they were separate constructs.

**建议**: Add a caveat and keep Authority non-confirmatory unless remeasured independently.

**可 paste 文本**:

> Under the v5.5 two-pass architecture, Authority is conditioned on the predicted Modality label. Authority is therefore treated as an adjunct/covariate for descriptive adjustment, not as an independently measured Bloc 3 factor. Any future elevation of Authority requires independent text inference, publisher metadata, or KG-based operationalization.

## 7. Construct strengths to preserve

- v0.2 correctly stops treating Thales `salience=core` as Target Salience itself; it now uses it only as target-selection input.
- Rejecting null or semantically broken `P_predict` targets is good measurement hygiene, as long as the resulting target universe is described narrowly.
- `static_reach = 3` has strong face validity for high expected exposure.
- Recurrence now has a reproducible reference window, entity matching plan, provenance requirement, and stored absolute-count sensitivity.
- Authority's status is now aligned with the frozen shortlist: adjunct/covariate, not a new confirmatory factor and not a restored P1 signal.
- The memo appropriately treats Spearman/VIF as pre-manifest diagnostics; this should be preserved but not overstated as conceptual independence.

## 8. Final verdict

**MAJOR-REVISIONS-NEEDED.**

This is not a return-to-draft. The v0.2 architecture can stand, and the four-factor confirmatory matrix does not need to be reopened in WS0.5. The required changes are construct-level patches:

1. Narrow Target Salience to a selected-market-target reach composite, or split `context_gate` from the exposure score.
2. Add model-cutoff-censored recurrence and stop calling the case-date count directly model-visible.
3. Preserve absolute/log recurrence as construct-nearer sensitivity, with within-super_type percentile framed as relative recurrence.
4. Add explicit Bloc 3 language that Modality/Authority are correlated, and v5.5 Authority is conditioned on Modality.

After these patches, the memo should be approvable from a measurement/construct-validity lens.
