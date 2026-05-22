# WS0.5 v0.2 — Round 1 Review (Statistician Lens)

**Reviewer**: GPT-5.5 xhigh (Statistician role)
**Date**: 2026-05-19
**Memo**: docs/DECISION_20260518_ws0_5_thales_alignment.md (v0.2)

## TL;DR

**Verdict: MAJOR-REVISIONS-NEEDED.** v0.2 materially fixes the three round-0 statistical errors: it drops independent bootstrap-CI non-overlap, adds a limited-exposure acceptance layer plus sealed final holdout, and introduces an alpha ledger. However, §4 is not yet statistically signable because `delta_min = 0.02` is far below the MDE implied by `n=300` and `alpha=0.00167`, the alpha family is ambiguous across three task manifests, and the recurrence binarization in §5 is unstable with only ~16 cases per super_type.

The main repair is not to reject Scheme Y. Keep Scheme Y, but patch the pre-registration manifest so it distinguishes practical-effect thresholds from detectable-effect thresholds, defines alpha spending across tasks and looks, keeps population-estimator holdouts stratified/random, and replaces the within-super_type median split with a stability-checked or full-frame rank rule.

## 1. Round-0 statistical errors — fix verification

| Round-0 Issue | v0.2 Fix | Verdict | Notes |
|---|---|---|---|
| Bootstrap CI non-overlap (wrong for paired) | paired tests | correct with clarification | §4.1 now names McNemar/binomial matched-pair for top-1 and paired bootstrap/permutation for F1. This fixes the central paired-data error, but the F1 rule must specify whether bootstrap CI is descriptive or part of an AND gate. |
| K-rotation insufficient | Ladder limited-exposure + sealed final_holdout | partial-correct | §4.1 final_holdout is sealed and touched once, so the official reported metric is protected. The acceptance_holdout is still reused adaptively and returns rounded deltas; this is a pragmatic Ladder adaptation, not a formal reusable-holdout guarantee. |
| No alpha spending | Bonferroni 0.05/30 | partial | Bonferroni is valid under arbitrary dependence among valid tests, so independence is not the issue. The remaining issue is family scope: 30 looks per task vs across all three tasks is not specified, and the per-look alpha creates a power/MDE mismatch. |

## 2. Paired statistical tests

### 2.1 McNemar for top-1 acc

**Verdict: correct, but under-powered as specified.** For binary per-example top-1 correctness, exact McNemar is the right primary paired test; the "binomial matched-pair" wording is essentially the exact McNemar test on discordant pairs, so v0.3 should avoid implying two separate tests. Cite: §4.1 acceptance gate, lines naming "McNemar exact + binomial matched-pair."

Power caveat: McNemar tests imbalance in discordant pairs (`b` = candidate-only correct, `c` = incumbent-only correct). If `b ≈ c`, even many changed predictions produce little net accuracy gain and power is low; that is statistically appropriate for an accuracy-improvement gate. A paired permutation/randomization test over per-example signed correctness deltas is a good robustness alternative because it generalizes cleanly to partial-credit or non-binary scores, but it is not required for plain top-1.

Patch needed: specify one-sided superiority vs two-sided. For an acceptance gate, a pre-registered one-sided exact binomial test on discordants is defensible; a two-sided test is more conservative and worsens power.

### 2.2 Paired bootstrap + paired permutation for F1

**Verdict: partial.** "Paired bootstrap diff CI + paired permutation test" is the right family of tools, but §4.1 does not state whether both must pass, either may pass, or one is only for reporting. OR is wrong for a gate; AND is conservative and may be unnecessarily low-power. The clean rule is: paired permutation/randomization p-value is the hypothesis gate, paired cluster bootstrap CI is reported for uncertainty and may be used as a secondary estimation check.

The F1 estimand also needs definition. If entity F1 is micro-averaged over all entity instances, the effective information may exceed 300 articles but must still be bootstrapped by article/case cluster to preserve pairing. If it is macro-averaged over entity types or target families, rare-type cells can be tiny; bootstrap percentile intervals over sparse cells will be unstable and should not gate acceptance without minimum cell counts or stratified/shrinkage handling.

Recommended v0.3 rule: primary entity gate = micro-F1 or core-entity recall/F1 at article-cluster level; macro/type-level F1 reported as diagnostic only unless each gated stratum meets a pre-registered minimum count.

### 2.3 alpha spending choice

**Verdict: partial.** Bonferroni `0.05/30` is conservative and valid for FWER if each look's p-value is valid; it does not assume independent looks. The harder problem is adaptive reuse of the same acceptance_holdout: prior pass/fail and rounded delta feedback can shape later hypotheses, so the p-values are not formally protected by independence arguments. The sealed final_holdout solves official reporting, but not the "accepted prompt was lucky on acceptance_holdout" risk.

Sequential alpha-spending functions (Pocock, O'Brien-Fleming, Lan-DeMets) are acceptable alternatives, but note that those are designed for accumulating data, not repeated new hypotheses on the same fixed holdout. For this setting, a simple pre-assigned online FWER ledger is enough; Bonferroni is acceptable but low-power. Holm-Bonferroni is useful only when a fixed family of p-values is available; with one finalist per round it adds little. FDR/BH is inappropriate for acceptance because a single false accepted prompt is harmful; reserve FDR for exploratory reporting, not gates.

Patch needed: define alpha family across the three tasks. If each of topic/entity/signal_profile gets 30 looks at alpha 0.05, familywise false-accept risk across tasks is approximately `1 - 0.95^3 = 0.143`. Either state that alpha is task-local and not a cross-task scientific claim, or allocate a global prompt-tuning alpha across tasks.

### 2.4 delta_min calibration

**Verdict: wrong as an MDE claim; acceptable only as a practical-effect floor.** `delta_min = 0.02` is much smaller than what the proposed acceptance test can detect at `alpha = 0.00167`.

Exact McNemar intuition:

| Holdout n | Best-case exact one-sided p < 0.00167 requires | Minimum significant delta in best case |
|---:|---|---:|
| 80 | `b=10, c=0` | 0.125 |
| 300 | `b=10, c=0` | 0.033 |
| 600 | `b=10, c=0` | 0.0167 |

At `n=300`, a 2pp gain is only `b-c=6`; even the extreme `b=6,c=0` gives p≈0.0156, far above 0.00167. Approximate 80% power MDE for a one-sided paired test is `MDE ≈ (z_alpha + z_0.80) * sqrt(q/n)`, where `q=b+c` discordance rate. For `n=300`, MDE is about 0.049 at `q=0.05`, 0.069 at `q=0.10`, and 0.098 at `q=0.20`. For `n=80`, it is about 0.094, 0.134, and 0.189 over the same q values.

Therefore v0.3 must not present 0.02 as detectable on 80 or 300 cases. Options: enlarge acceptance_holdout, use a less stringent alpha allocation, raise task-specific `delta_min` to the detectable range, or state explicitly that 0.02 is a minimum meaningful effect while the statistical gate will only pass larger observed gains.

Different tasks should use different thresholds. Topic top-1 and modality top-1 are bounded binary accuracy metrics with paired-discordance MDE. Entity F1 has cluster/bootstrap uncertainty and may need a higher delta if macro-F1 or rare entities are primary.

## 3. Active fixture + rotation statistical properties

The sealed final_holdout is the strongest improvement in v0.2. If it is truly evaluated once and never used to tune prompts, it fully avoids adaptive-holdout contamination for the official final metric. From the Generic Holdout view, final_holdout should ideally answer only the final threshold question plus report a one-time CI; no result should feed back into prompt changes.

The acceptance_holdout is a weaker point. §4.1 says it returns pass/fail plus rounded delta and uses "threshold_converged: acceptance metric ≥ target_threshold." A stricter Generic Holdout/Ladder version would expose only binary answers to pre-registered predicates: `(candidate beats incumbent by delta_min with p < alpha_i)` and `(candidate/incumbent is above target_threshold)`. The controller may log exact metrics internally, but proposers should not see rounded deltas, and the memo should say exact acceptance scores are not used to tune future patch content.

Active sampling is appropriate for train_visible. It is risky for inner_dev if inner_dev is treated as a population estimator: 25% disagreement + 20% hotspot deliberately over-represents hard/boundary cases. That can rank patches by challenge-set performance rather than deployment-distribution performance. Acceptance_holdout and final_holdout should be independently stratified random samples from the target evaluation distribution, not active-sampled.

Cross-rotation comparability is under-specified. Because train+inner_dev are refreshed with active samples, score changes across rotations combine prompt improvement, sampling noise, and distribution shift. Add an anchor fixture: a fixed, stratified random development panel used only for non-gating trend monitoring or incumbent sanity checks. It should not be final_holdout and should not spend acceptance alpha unless used as an acceptance gate.

## 4. Target Salience non-redundancy rules

The §3.3.3 rule is directionally right but too marginal. Spearman `|rho| < 0.50` between Target Salience and Recurrence checks only marginal monotone association. In the actual mixed-effects analysis, the relevant diagnostics are partial/residual correlations controlling for super_type/host category, event date or cutoff window, and target family where appropriate.

VIF `< 3` is an OLS fixed-design diagnostic. For a mixed-effects model, v0.3 should compute VIF/GVIF on the scaled fixed-effect design matrix, condition number of the centered/scaled design, and singularity/convergence diagnostics for random effects. The memo should not imply that an ordinary OLS VIF alone validates the mixed model.

Timing must be explicit. The check cannot be meaningfully "pre-manifest" before sampling and factor computation. Correct timing is: after candidate sampling and factor value computation, before pilot manifest freeze and before any main analysis or prompt tuning uses those factor values.

Finally, all four confirmatory factors require a pairwise screen. There are six pairs among Cutoff Exposure, Historical Family Recurrence, Target Salience, and Template Rigidity. Must-pass/resample should apply to modifiable same-level factor redundancies, especially Target Salience × Recurrence, Target Salience × Template Rigidity, and Recurrence × Template Rigidity. Cutoff Exposure correlations should be must-report and, if high, trigger date-stratified rebalance or explicit model adjustment rather than silent resampling.

## 5. Recurrence operationalization

### 5.1 Within-super_type percentile statistics

**Verdict: major instability risk.** With 80 pre-cutoff cases and 5 super_types, the expected cell is ~16 cases. Percentile ranks then move in ~6.25-point steps before ties; a one- or two-case count change can flip a case around the 0.50 cutpoint. Alias expansion, entity-confirm uncertainty, and topic classification noise can all move counts enough to change the binary factor.

Within-super_type ranking also only decorrelates from super_type in expectation. With ties, unequal super_type sample sizes, and active/quota sampling, the binary factor can still be imbalanced by super_type.

Recommended repair: compute recurrence percentiles on the full eligible pre-cutoff sampling frame or a larger frozen candidate pool, not only on the final 80. Freeze super_type-specific cutpoints before final manifest selection. Add a tie rule, a bootstrap or perturbation stability score for the recurrence bin, and require near-cutpoint cases to be flagged or avoided during sampling if they threaten `n_eff`.

If a binary confirmatory factor is mandatory, the primary bin should be "stable high" vs "stable low" from the full-frame within-super_type distribution; store continuous `log1p(recurrence_count)` and `recurrence_pct_within_super_type` for sensitivity.

### 5.2 Base rate confound: absolute vs within-type

The construct-statistical issue is real: if CLS base-rate differences across event types reflect true training exposure, absolute recurrence count is the cleaner memorization proxy. If base-rate differences mainly reflect CLS/editorial coverage imbalance or sampling policy, within-super_type normalization is a cleaner conditional recurrence factor.

The statistically honest solution is not to choose post hoc. v0.3 should pre-register interpretation rules:

- both within-type and absolute significant with same sign: robust recurrence/exposure evidence;
- within-type significant, absolute not: conditional within-family repetition, not broad exposure density;
- absolute significant, within-type not: exposure density is dominated by event-type/base-rate differences;
- signs disagree or one is unstable: treat recurrence evidence as unresolved and emphasize sensitivity.

This keeps the primary factor aligned with multicollinearity control while preventing the appendix sensitivity from silently becoming the real result.

## 6. Pre-registration manifest rigor

The manifest currently looks task-local (`factor_task: topic_classification`) but uses `alpha_total: 0.05` and `max_acceptance_looks: 30` without saying whether that is per task or across topic/entity/signal_profile. This is the most important manifest ambiguity. Define one of:

- `alpha_family: per_task_prompt_tuning`, with 0.05 per task and no cross-task FWER claim;
- `alpha_family: all_prompt_tuning_tasks`, with 0.05 across all three tasks, e.g. `0.05 / 90` if each has 30 looks;
- task-weighted allocation, e.g. 0.02 topic, 0.02 entity, 0.01 signal_profile, with per-look ledgers inside each task.

The rotation cap also needs reconciliation. `K=5` and `rotations=4` imply at most 20 rounds and, with one finalist per round, at most 20 acceptance looks. Pre-registering 30 looks while capping at 20 is conservative but confusing. Either set max looks to 20 or explain the extra 10 looks are for restart/smoke/exception paths and still spend alpha.

Plateau must count failed looks. A finalist submitted to acceptance_holdout spends one alpha look whether it passes or fails. A candidate dropped during train or inner_dev filtering does not spend alpha. A rotation with no submitted finalist should count for operational plateau but not for alpha unless an acceptance query was made.

Replicability patch: the tuning log should store for every possible look: look index, task, rotation, round, candidate ID, whether acceptance_holdout was queried, alpha_i, p-value, observed delta, pass/fail, and cumulative alpha spent.

## 7. Critical statistical issues

### Issue S-1: `delta_min = 0.02` is below acceptance-gate MDE (major)

**问题**: §4.1 sets `delta_min = 0.02` while also requiring `p < 0.00167` on n=300 acceptance_holdout. For top-1 accuracy, 2pp is not detectable under the proposed McNemar gate; at n=300, even the best-case exact significant delta is 3.3pp, and realistic 80% power MDE is closer to 5-10pp depending on discordance.

**建议修法**: Separate `delta_min_practical` from `delta_detectable_planning`. Keep 0.02 only as a minimum practical floor, and pre-register task-specific detectable thresholds or larger acceptance sample sizes.

**可 paste 文本**:
```markdown
**Effect-size and power calibration.** `delta_min` is a practical-effect floor, not a claim that the loop can detect a 2pp gain. For each task, the manifest records an MDE calculation under the planned acceptance_holdout size, alpha schedule, and expected discordance/cluster variance. A candidate is accepted only if it passes both the practical-effect floor and the statistical gate; v0.3 does not describe 0.02 as detectable unless the MDE calculation supports it. For top-1 metrics, the default detectable planning range at n=300 and alpha=0.00167 is approximately 5-10pp depending on discordance.
```

### Issue S-2: Alpha family across three tasks is ambiguous (major)

**问题**: §4.2 defines a manifest per `factor_task` with `alpha_total: 0.05` and `max_acceptance_looks: 30`. If repeated for topic, entity, and signal_profile, cross-task false-accept risk is not 0.05. If instead 30 looks is global across all three tasks, the manifest must allocate looks and alpha across tasks.

**建议修法**: Add `alpha_family_scope` and task-level allocation before any loop runs.

**可 paste 文本**:
```yaml
alpha_family_scope: all_ws0_5_prompt_tuning_tasks
alpha_total_family: 0.05
task_alpha_allocation:
  topic_classification: 0.0167
  entity_extraction: 0.0167
  signal_profile: 0.0166
max_acceptance_looks_by_task:
  topic_classification: 30
  entity_extraction: 30
  signal_profile: 30
per_look_alpha_rule: "task_alpha / max_acceptance_looks_by_task[task]"
look_counting_rule: "every acceptance_holdout query spends one look, pass or fail; train/inner_dev filtering does not"
```

### Issue S-3: F1 acceptance test is underspecified (major)

**问题**: §4.1 says "paired bootstrap diff CI + paired permutation test" for F1 but does not define the gate relation, averaging scheme, bootstrap unit, or rare-cell policy. This can create either double-testing or an OR gate that inflates type-I error.

**建议修法**: Use paired permutation p-value as the gate; use article-cluster bootstrap CI for uncertainty reporting; define micro/macro F1 and minimum stratum counts.

**可 paste 文本**:
```markdown
For entity metrics, the primary acceptance gate uses a paired permutation/randomization test on the pre-registered primary metric, resampling/permuting at the article fixture unit. The paired cluster bootstrap difference CI is reported for uncertainty and is not an independent OR gate. Primary entity F1 is micro-averaged over core entities unless the task manifest explicitly declares a macro average and verifies minimum per-stratum counts; rare-type macro scores are diagnostic unless their stratum counts meet the manifest threshold.
```

### Issue S-4: Active-sampled inner_dev is a biased ranking estimator (major)

**问题**: The 40/25/20/15 active recipe is useful for training but not for unbiased performance estimation. If inner_dev is active-sampled like train_visible, patch ranking can optimize for disagreement/hotspot cases rather than the target distribution, and rotation-to-rotation scores are not comparable.

**建议修法**: Keep train_visible active; keep acceptance/final stratified random; add a fixed anchor_dev or split inner_dev into random_dev plus challenge_dev.

**可 paste 文本**:
```markdown
Active sampling is applied to `train_visible` and to a labeled `challenge_dev` diagnostic slice only. Population-estimator sets (`acceptance_holdout`, `final_holdout`, and any score used for threshold claims) are independently stratified random samples from the target evaluation distribution. Candidate ranking may use both `random_inner_dev` and `challenge_dev`, but the manifest records the weighting rule. Cross-rotation trend plots use a fixed `anchor_dev` that is never used for final threshold reporting.
```

### Issue S-5: Within-super_type median recurrence split is unstable at ~16 cases/type (major)

**问题**: §5.2 computes percentile rank within the same super_type pilot cases and cuts at 0.50. With ~16 cases per super_type, ranks are coarse and a small alias/topic/count perturbation flips cases near the median. This threatens factor reliability and the `min cell >= 15` matrix.

**建议修法**: Compute ranks/cutpoints on the full eligible sampling frame or a larger frozen candidate pool; add tie/stability rules; avoid near-cutpoint cases where possible.

**可 paste 文本**:
```markdown
Historical Family Recurrence percentiles are computed within super_type on the frozen eligible pre-cutoff sampling frame, not only on the final 80-case manifest. The manifest freezes the super_type-specific cutpoints, tie policy, and a bin-stability diagnostic from count/alias perturbation or bootstrap resampling. Cases whose recurrence bin is unstable near the 0.50 cutpoint are flagged; the sampler preferentially selects stable high/low cases while preserving the Section 6.3/6.4 quota rules.
```

### Issue S-6: Non-redundancy diagnostics are marginal and incomplete (major)

**问题**: §3.3.3 and §5.4 use marginal Spearman and OLS-style VIF, mostly focused on Target Salience × Recurrence. The mixed-effects design needs partial/residual diagnostics and all six confirmatory factor pairs.

**建议修法**: Add a post-factor/pre-manifest discriminant diagnostic block with pairwise, partial, and design-matrix checks.

**可 paste 文本**:
```markdown
After factor values are computed and before pilot manifest freeze, WS0.5 emits a discriminant-diagnostics report over all six pairs among Cutoff Exposure, Historical Family Recurrence, Target Salience, and Template Rigidity. The report includes marginal Spearman correlations, partial/residual correlations controlling for super_type/host category and event-date window where applicable, scaled fixed-effect design VIF/GVIF, condition number, and mixed-model singularity/convergence diagnostics. `|rho| > 0.65` or equivalent partial redundancy triggers resampling/rebinning or a signed decision memo before freeze.
```

### Issue S-7: Acceptance_holdout feedback is still too score-like (minor-to-major)

**问题**: §4.1 returns rounded delta to proposers and uses acceptance metric for threshold convergence. This is much better than exact scores, but Generic Holdout's stricter principle is binary "good enough" answers, not a repeated rounded score surface.

**建议修法**: Hide rounded deltas from candidate proposers; log exact/rounded metrics internally only; expose binary predicates.

**可 paste 文本**:
```markdown
The acceptance_holdout oracle returns only binary predicate outcomes to prompt proposers: `accepted_vs_incumbent` and, when queried, `above_target_threshold`. Rounded deltas and exact p-values are written to the private tuning log for audit but are not shown to candidate-generating agents and are not used as textual feedback for subsequent patches.
```

### Issue S-8: §11 risk text still references the old bootstrap gate (minor)

**问题**: R-W05-1 says "Scheme Y bootstrap CI gate catches," which is stale and conflicts with the paired-test correction in §4.

**建议修法**: Replace "bootstrap CI gate" with "paired acceptance gate."

**可 paste 文本**:
```markdown
| R-W05-1 | V4 Pro behavior diverges materially from deepseek-chat → starting prompts regress | Scheme Y paired acceptance gate plus train/inner_dev diagnostics catches; if 50% baseline drop in round 1, halt and reconsider |
```

## 8. Statistical strengths to preserve

- The sealed final_holdout evaluated once at the end is the right answer for the official reported threshold metric.
- The move from independent CI non-overlap to paired tests is a real statistical upgrade and aligns with NLP paired-eval practice.
- One finalist per round hitting acceptance_holdout is a good multiplicity/holdout-exposure constraint; preserve this cap.
- Pre-registration manifest + alpha-spent ledger is the right governance object; it just needs sharper family and look-counting definitions.
- Storing absolute recurrence count as sensitivity is important; keep it and pre-register interpretation rules rather than switching post hoc.

## 9. Final verdict

**Verdict**: MAJOR-REVISIONS-NEEDED

**修订后需 re-review section**: §3.3.3, §4.1, §4.2, §5.2, §5.4, §5.5, §11 R-W05-1/R-W05-3/R-W05-8.

Minimum v0.3 bar: MDE-calibrated `delta_min` language, explicit alpha family across tasks, F1 gate definition, random/active fixture separation, recurrence stability rule, and complete mixed-model discriminant diagnostics.
