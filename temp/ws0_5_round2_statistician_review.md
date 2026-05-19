# WS0.5 v0.3 — Round 2 Review (Statistician Lens)

**Reviewer**: GPT-5.5 xhigh (Statistician role)
**Date**: 2026-05-19
**Memo**: docs/DECISION_20260518_ws0_5_thales_alignment.md (v0.3)
**Round-1 review verified against**: temp/ws0_5_round1_statistician_review.md

## TL;DR

v0.3 correctly fixes 7/8 statistician issues and mostly fixes S-1. The remaining S-1 gap is narrow: after S-2's global alpha allocation, per-look alpha is now about 0.000556, so the MDE preflight must explicitly compute/report MDE under that alpha and cannot pretend to estimate paired discordance from the incumbent prompt alone.

**Verdict: APPROVE-WITH-MINOR-PATCHES.** No issue remains unaddressed, and I see no new critical statistical risk, but §4.1 should receive a small MDE-preflight wording patch before sign-off.

## 1. Issue-by-issue verification (S-1 to S-8)

| Issue | Status (patched / partial / unaddressed) | Notes |
|---|---|---|
| S-1 delta_min MDE | partial | Correctly splits `delta_min_practical` from `delta_detectable_planning` and adds `mde_report.json`; minor patch needed because paired discordance/cluster variance must be pre-registered as a grid or historical assumption, not estimated from current prompt alone. |
| S-2 alpha family scope | patched | §4.2 now scopes alpha across all three WS0.5 prompt-tuning tasks with per-task allocations and look-counting rule. |
| S-3 F1 gate | patched | §4.1 makes paired permutation the primary gate and cluster bootstrap CI descriptive; micro-F1 article cluster unit is defined. |
| S-4 active/random fixture separation | patched | §4.1 separates active `train_visible`/`challenge_dev` from stratified-random `random_inner_dev`/`acceptance_holdout`/`final_holdout`/`anchor_dev`. |
| S-5 recurrence bin stability | patched | §5.2 moves ranks to the full eligible pre-cutoff frame, adds tie/rank policy, stores continuous sensitivities, and emits bin-stability report. |
| S-6 non-redundancy diagnostics | patched | §3.3.3 now covers all six confirmatory pairs, partial/residual correlations, GVIF, condition number, and mixed-model singularity/convergence timing. |
| S-7 acceptance feedback surface | patched | §4.1 exposes binary predicates only; rounded deltas and exact scores are private logs. |
| S-8 §11 risk text | patched | R-W05-1 now says "paired acceptance gate" and references McNemar / paired permutation. |

## 2. Detailed verification

### S-1: `delta_min = 0.02` below acceptance-gate MDE

**Status: partial, minor.**

v0.3 makes the core conceptual correction I asked for:

- `delta_min_practical` is a practical-effect floor, not a detectability claim.
- `delta_detectable_planning` is populated by MDE preflight.
- The MDE report records observed/planned quantities and can stop the run if MDE is too large.
- §4.1 explicitly says v0.3 does not claim 2pp is detectable at n=300.

This is enough to remove the v0.2 major flaw. The remaining issue is narrower but real. §4.1 says the preflight samples "200 representative items × current prompt" to estimate discordance rate `q` for a paired top-1 test. For McNemar, `q = b + c` is the candidate-vs-incumbent discordance rate; it is not identifiable from the incumbent/current prompt alone. Similarly, entity F1 paired SD is a candidate-vs-incumbent quantity.

Required minor patch:

```markdown
If no prior candidate-vs-incumbent discordance estimate exists, the MDE preflight reports a pre-registered sensitivity grid, e.g. q ∈ {0.05, 0.10, 0.20} for top-1 metrics, and an analogous paired-SD grid for F1. Empirical q/paired-SD from accepted/rejected candidates is appended after the first acceptance look, but the run-start go/no-go verdict is based on the pre-registered grid and the actual per-look alpha after cross-task allocation. The report must show per_look_alpha ≈ 0.000556 under `alpha_family_scope: all_ws0_5_prompt_tuning_tasks`.
```

With that wording, S-1 is signable. Without it, the preflight can be implemented in an under-specified way even though the memo's intent is correct.

### S-2: Alpha family scope across three tasks

**Status: patched.**

v0.3 resolves the ambiguity. §4.2 now defines:

- `alpha_family_scope: all_ws0_5_prompt_tuning_tasks`
- `alpha_total_family: 0.05`
- task allocation 0.0167 / 0.0167 / 0.0166
- 30 looks per task
- per-look alpha rule
- look-counting rule: every acceptance-holdout query spends alpha, pass or fail

This controls familywise false acceptance across the three tuning tasks. It is conservative, but statistically valid.

The cost of this repair is power: per-look alpha is now about `0.0167 / 30 = 0.000556`, not v0.2's 0.00167. That is not a blocker because S-1's MDE preflight is explicitly tied to the per-task alpha schedule. It does mean the MDE report is now mandatory, not decorative.

### S-3: F1 acceptance gate underspecified

**Status: patched.**

v0.3 removes the OR/AND ambiguity:

- F1-style metric gate = paired permutation/randomization test.
- Cluster bootstrap CI = descriptive uncertainty only.
- Unit = article fixture cluster.
- Primary averaging = micro-F1 over core entities unless the manifest explicitly declares macro-F1 and verifies minimum stratum counts.
- Rare-stratum macro scores are diagnostic only.

This is the right statistical shape for paired NLP entity evaluation. No follow-up required from statistician lens.

### S-4: Active-sampled inner_dev biased as population estimator

**Status: patched.**

v0.3 changes the split into:

- active: `train_visible`, `challenge_dev`
- stratified random: `random_inner_dev`, `acceptance_holdout`, `final_holdout`, `anchor_dev`
- `challenge_dev` is diagnostic; `random_inner_dev` is the unbiased ranking sample
- acceptance/final/anchor do not rotate
- split manifest carries immutable item IDs and overlap assertions

This solves the statistical concern. The design now separates adversarial learning material from population-estimator material.

### S-5: Within-super_type median recurrence split instability

**Status: patched.**

v0.3 makes the recurrence bin statistically more defensible:

- ranks/cutpoints computed on the full eligible pre-cutoff sampling frame, not only the final 80 pre-cutoff cases
- `recurrence_pct_within_super_type` is a full-frame percentile
- primary binary label is renamed/framed as `relative_recurrence_within_super_type_high`
- bin-stability report includes leave-one-out and bootstrap bin-flip rates
- unstable near-cutpoint cases are flagged and avoided where quotas allow
- absolute/log/clustered recurrence sensitivities are stored and interpretation rules are pre-registered

Minor editorial note, not a blocker: `recurrence_rank_method = "average"` and `recurrence_tie_break = "secondary order: log1p_count desc"` are redundant because tied raw counts have tied `log1p_count`. The final implementation can either keep average ranks only or define a genuinely independent secondary key. This does not undermine the statistical fix because the stability report is the real safeguard.

One useful non-blocking addition would be to include `frame_n_by_super_type` and cutpoint counts in `ws0_5_quota_report.json`; the current text implies but does not explicitly name that field.

### S-6: Non-redundancy diagnostics marginal/incomplete

**Status: patched.**

§3.3.3 now states the diagnostic report covers all six pairs among:

- Cutoff Exposure
- Historical Family Recurrence
- Target Salience
- Template Rigidity

It includes marginal Spearman, partial/residual correlations controlling for super_type/host/date where applicable, scaled fixed-effect GVIF, condition number, and mixed-model singularity/convergence. Timing is now correct: after sampling and factor computation, before pilot manifest freeze and before main analysis.

This resolves the round-1 issue.

### S-7: Acceptance_holdout feedback too score-like

**Status: patched.**

v0.3 removes rounded delta feedback from proposers. Proposers now see only:

- `fail`
- `pass_delta_min`
- `pass_above_target_threshold`

Exact metrics, rounded deltas, p-values, and per-example breakdowns are private audit logs. Candidate dedupe and near-duplicate rejection are also specified. This is the desired limited-exposure behavior.

### S-8: §11 stale "bootstrap CI gate" risk text

**Status: patched.**

R-W05-1 now says:

> Scheme Y paired acceptance gate (one-sided exact McNemar / paired permutation per §4.1)

This aligns §11 with the corrected paired-eval design.

## 3. New statistical risks introduced by v0.3

### 3.1 Cross-task alpha allocation makes the acceptance gate even lower-power

v0.3's global family scope is statistically correct, but it lowers per-look alpha from 0.00167-style task-local Bonferroni to approximately `0.000556`.

Implication:

- Best-case exact McNemar significance at n=300 needs roughly 11 one-sided wins and zero losses, i.e. about 3.7pp net gain in the most favorable case.
- Realistic 80% power MDE can be closer to 6-11pp depending on discordance.
- Entity F1 can be wider if article-level paired variance is high.

This is not a critical flaw because §4.1 explicitly routes this through MDE preflight and allows plateau to be interpreted as a power issue. The minor S-1 patch above is needed so that the MDE report cannot understate this risk.

### 3.2 Seven-way fixture split does not itself weaken acceptance n, but makes preflight essential

The split now has 7 buckets and still keeps `acceptance_holdout = 300` and `final_holdout = 300`. This is acceptable. The extra `challenge_dev`, `anchor_dev`, and `reserve` buckets improve governance rather than hurting inference, as long as there is no overlap and only acceptance queries spend alpha.

The statistical caveat is that some tasks, especially entity F1, may have effective information below 300 article clusters if core entities are sparse. v0.3 handles this by cluster-unit F1 testing and MDE preflight. No further memo-level redesign is required.

### 3.3 Recurrence full-frame ranks depend on frame construction

Moving percentile ranks to the full eligible pre-cutoff frame is the right fix. The only residual risk is if the eligible frame is thin or uneven in a super_type. This is manageable through the existing bin-stability block; adding frame sizes to the quota report would make the audit cleaner.

### 3.4 No new multiplicity family fragmentation

The alpha family is no longer too fragmented. It is one family across all WS0.5 prompt-tuning tasks. Discriminant diagnostics and recurrence sensitivity analyses are not being used as confirmatory accept/reject tests for prompt tuning, so they do not require inclusion in the Scheme Y alpha family.

## 4. Final verdict

**Verdict**: APPROVE-WITH-MINOR-PATCHES

**修订后需 re-review section**: §4.1 MDE preflight only. No full statistician re-review needed if the patch explicitly reports the post-allocation per-look alpha and uses a pre-registered discordance / paired-SD grid when empirical candidate-vs-incumbent variance is unavailable.

**建议下一步**: Apply the S-1 wording patch above, then let WS0.5 proceed to implementation with `mde_report.json`, `ws0_5_quota_report.json`, and `ws0_5_discriminant_report.json` treated as required sign-off artifacts.
