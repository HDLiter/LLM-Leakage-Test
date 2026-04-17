# Review: amber G2b

## Scope

Method used for this review:

1. Read `docs/BUG_AUDIT_amber.md`, especially the audit summary table and each bug's quoted code location/mechanism.
2. Inspected pre-fix code from `87f0211` only, to derive fixes without reading the implementation diff first.
3. Read `git log --oneline 87f0211..HEAD` and `git show 4421da2`.
4. Compared the independently derived fixes against the actual implementation in `4421da2`.

`git log --oneline 87f0211..HEAD` contains a single commit:

- `4421da2 amber-mirror-lattice: Phase A audit + Phase B bug fixes (5 bugs)`

Bottom line: the implementation is directionally consistent with the audit and mostly matches the fix shape I would have chosen independently. The two places where I would call out residual weakness are Bug 4's permissive polarity validator and Bug 5's analysis surfacing, which is good but not fully maximal.

## Summary Table

| Bug | Independent best fix | Actual fix | Match | Assessment |
|---|---|---|---|---|
| 1. `changed_spans` `maxLength: 200` | Remove the cap from shared schema | Removed both caps from shared schema | Exact | Correct minimal fix |
| 2. `cfls=None` reporting/dropout visibility | Do not change aggregation math; surface denominators and CF failure counts in output/meta | Added `n_total_cases`, `n_cf_failed_by_type`, `cf_failed_by_stratum`, `n_total_by_stratum`, `n_scored_by_task_x_stratum` | Strong match | Better than minimal |
| 3. neutral retreat scored as no-flip | Prefer enum (`strict_flip` / `hedged_flip` / `no_flip`) with legacy projection | Implemented enum + strict/hedged projections + legacy aliases | Exact to preferred variant | Best variant of the reasonable options |
| 4. no polarity check on LLM-negated FO | Shared polarity validator on both single and batched paths; retry/fallback policy is a design choice | Added shared token-based validator on both paths; also removed regex/generic fallback for pre-known cases | Partial-plus | Mechanism addressed, but validator is heuristic and deliberately permissive |
| 5. probe modality confounded with `known_outcome_available` | Minimum acceptable fix: persist `cpt_mode` and report analysis by mode; principled fix would be uniform/2x2 design | Persisted `cpt_mode`, added `quick_stats.py` mode block, and purified pre-known path to LLM-only-or-fail | Strong match | Good Phase B fix; underlying design confound is surfaced, not eliminated |

## Bug 1

### Mechanism

The audit mechanism is correct. In `87f0211`, `counterfactual_rewrite_v1` in `config/prompts/counterfactual_templates.yaml` capped `changed_spans[*].from` and `.to` at 200 chars. Because `semantic_reversal` and `neutral_paraphrase` both used that shared schema, legitimate whole-sentence rewrites could fail schema validation and get dropped upstream.

### Independent derivation

Minimal fix:

- Remove `maxLength` from both `changed_spans[*].from` and `.to` in the shared schema.

Reasonable variants:

- Raise the cap to a large value, such as 1000 or 4000, instead of removing it.
- Keep the cap but change the prompt/parser so large rewrites must be split into multiple shorter spans.
- Make `changed_spans` advisory-only and stop validating length there.

Trade-offs:

- Removing the cap is the cheapest and most robust fix because `changed_spans` is audit metadata, not a model-facing control channel.
- Raising the cap retains some guardrail but still guesses at a length threshold and can fail again on outliers.
- Span-splitting or weaker validation adds complexity for little gain.

### Actual fix

`4421da2` removes both `maxLength: 200` constraints from the shared schema.

### Comparison

- Consistency: exact match.
- Better side: actual fix equals the best minimal fix.
- Different problem?: no. It fixes the exact mechanism named in the audit.
- New risk?: only the obvious one that very long `changed_spans` strings are now allowed, but that risk is low and acceptable because downstream logic does not depend on this field's bounded size.

Assessment: correct.

## Bug 2

### Mechanism

The audit downgrade is right. In `87f0211`, `aggregate_case_results` filtered out `cfls is None` before taking means, but the JSON already retained the main denominators. The real problem was visibility/readability of the dropout structure, especially by stratum.

### Independent derivation

Minimal fix:

- Do not change the aggregation formula.
- Add machine-readable denominator and CF-failure surfaces to the output `meta` block.

Reasonable variants:

- Only update markdown/report tables.
- Add overall `n_total_cases`, `n_scored_by_task`, and per-CF-type failure counts.
- Add a full per-stratum missingness summary so `n_scored / n_total` can be reconstructed for each cell.

Trade-offs:

- Markdown-only is cheapest but not machine-readable.
- Overall counts help, but still hide the stratum pattern that mattered in the audit.
- Per-stratum counts are slightly more code, but actually solve the reporting problem.

### Actual fix

`4421da2` adds `compute_cf_failure_summary()` in `scripts/run_diagnostic_2.py` and emits:

- `n_total_cases`
- `n_cf_failed_by_type`
- `cf_failed_by_stratum`
- `n_total_by_stratum`
- `n_scored_by_task_x_stratum`

### Comparison

- Consistency: strong match.
- Better side: actual fix is better than my minimum because it includes both total and stratified missingness surfaces.
- Different problem?: no. It directly addresses the downgraded reporting mechanism.
- New risk?: minor naming ambiguity only. `n_total_cases` is `len(case_results)`, so if there are run-time case errors the field is "completed cases", not "eligible cases". That is not wrong, but the name is slightly broader than the value.

Assessment: good and slightly stronger than required.

## Bug 3

### Mechanism

The audit mechanism is correct. In `87f0211`, `_detect_fo_flip()` returned `False` for `orig non-neutral -> fo neutral`, which systematically missed hedged retreats. The live v3 path scored FO flip through `_detect_fo_flip()`, so this was a real scoring bug.

### Independent derivation

Minimal fix:

- Expand live-path FO-flip scoring so `orig non-neutral -> fo neutral` counts as influenced, not resisted.

Reasonable variants:

- Keep a bool API and redefine `True` as `strict OR hedged`.
- Return an enum such as `strict_flip`, `hedged_flip`, `no_flip`, `undefined`, then project to bools where needed.
- Replace the current logic with an ordinal distance-to-expected score.

Trade-offs:

- Bool-union is smallest code change but throws away the distinction the audit found important.
- Enum is the best balance: it preserves legacy strict behavior while exposing the hedged signal explicitly.
- Ordinal scoring is more principled but much larger in scope.

I would independently choose the enum variant, plus backward-compatible strict projections.

### Actual fix

`4421da2` does exactly that:

- `_detect_fo_flip()` in `src/metrics.py` now returns `strict_flip`, `hedged_flip`, `no_flip`, or `None`.
- `fo_flip_label_to_strict()` and `fo_flip_label_to_hedged()` project the label to strict and hedged bools.
- `src/pilot.py` persists strict, hedged, and label fields while keeping legacy `fo_flip_direct` / `fo_flip_impact` aliases on strict semantics.

### Comparison

- Consistency: exact to my preferred variant.
- Better side: actual fix is the best reasonable variant.
- Different problem?: no. It fixes the exact audit mechanism.
- New risk?: one residual cleanup item remains. `cfls_per_case()` in `src/metrics.py` still contains the old duplicate bool logic internally, although the v3 pipeline continues to override it with the canonical `_detect_fo_flip()` result. That is not a live-path regression, but it is dead-code drift that could confuse a future caller.

Assessment: very good. If I were doing a small follow-up, I would delete or refactor the stale duplicate logic inside `cfls_per_case()`.

## Bug 4

### Mechanism

The audit mechanism is correct. In `87f0211`, both `src/masking.py::generate_false_outcome_cpt()` and the batched validator path accepted any non-empty, non-identical, length-bounded LLM output as a valid negation. That allowed same-polarity, off-topic, or vague rewrites to be planted as supposed false outcomes.

### Independent derivation

Minimal fix:

- Introduce a shared polarity validator and apply it on both the single-call and batched paths before accepting an LLM-negated outcome.

Reasonable variants:

- Token/regex polarity validator.
- Task-schema or parser-based validator.
- LLM-as-judge polarity validator.
- Hybrid: cheap lexical check first, semantic judge only on ambiguous cases.

Retry/fallback variants:

- If validation fails, retry the LLM and then fall back to regex/generic.
- If validation fails, retry the LLM and then mark the CPT as missing rather than falling back to a different modality.

Trade-offs:

- Token-based validation is cheap and deterministic, but misses paraphrases and subtle semantics.
- LLM judgment is semantically stronger but costs more and adds another source of noise.
- Falling back preserves coverage but can contaminate probe modality.
- Failing closed preserves modality purity but increases missingness.

My independent preference would be:

- shared validator on both paths
- cheap lexical check is acceptable for Phase B
- fail closed rather than falling back if probe-modality purity is now a design goal

### Actual fix

`4421da2` adds `check_negation_polarity_flipped()` in `src/masking.py` and uses it in both:

- `generate_false_outcome_cpt()`
- `prepare_fo_cpt_batch()` in `src/pilot.py`

It also changes the pre-known path to `LLM-only or llm_failed`, removing regex/generic fallback for those cases.

### Comparison

- Consistency: partial-plus, but in the good direction.
- Better side: on fallback policy, I think the actual fix made the stronger and cleaner design choice. Once Bug 5 is acknowledged, "missing data is better than cross-modality contamination" is a defensible rule.
- Different problem?: no. It fixes the audit mechanism and also tightens an adjacent modality-purity issue.
- New risk?: yes, but explicit and acceptable.

New risks and residuals:

- The validator is heuristic, not semantic. `check_negation_polarity_flipped()` is deliberately permissive: if either side is `neutral` or `mixed`, it returns `True`. That means some vague or off-direction LLM outputs can still pass.
- Removing fallback creates selective `llm_failed` missingness on pre-known cases. I think that trade-off is acceptable, but it should be tracked as missingness, not silently ignored.

Assessment: good Phase B fix, but it is a guardrail rather than a full semantic guarantee.

## Bug 5

### Mechanism

The audit mechanism is correct in its revised form. The split was not truly pre vs post; it was driven by `known_outcome_available`. That means the pre arm itself was mixed, and any pre/post headline was partly an apples-to-mixed comparison.

### Independent derivation

There are really two fix layers here:

- Analysis-layer minimum: persist `cpt_mode` per case and make analysis/reporting show the probe modality explicitly.
- Experimental-design fix: make modality uniform across arms, or run a 2x2 design where each case gets both probes.

Reasonable variants:

- Persist `cpt_mode` only.
- Persist `cpt_mode` and add a mode-aware analysis arm.
- Force one modality for all future cases, likely generic for everyone.
- Use a richer generic probe to narrow the gap.
- Run the principled 2x2 design.

Trade-offs:

- Persisting `cpt_mode` is the cheapest acceptable Phase B fix because it stops the confound from remaining hidden.
- Forcing generic everywhere restores symmetry but throws away information from pre-known cases.
- A richer generic probe narrows but does not eliminate the modality gap.
- A 2x2 design is the cleanest answer but materially more expensive.

My independent Phase B choice would be:

- persist `cpt_mode`
- add a mode-aware analysis arm
- avoid introducing extra fallback modalities inside the pre-known path

### Actual fix

`4421da2` does three relevant things:

- Persists `cpt_mode` at the top level of each case result in `src/pilot.py`.
- Adds a `cpt_mode` block in `scripts/quick_stats.py`.
- Purifies the pre-known path to `llm_negated` or `llm_failed`, removing regex/generic fallback there.

### Comparison

- Consistency: strong match.
- Better side: the no-fallback purification is a good addition because it removes an extra hidden modality split inside the pre-known branch.
- Different problem?: no. It addresses the same audit mechanism, plus an adjacent mode-purity problem.
- New risk?: one moderate residual limitation remains.

Residual limitation:

- `quick_stats.py` surfaces `cpt_mode` distribution and overall flip rates by mode, but it does not build a true `period × cpt_mode` comparison table. That means the cleanest within-modality comparison still is not fully first-class in the shipped quick analysis.

That said, the important threshold is crossed: the confound is no longer hidden. `cpt_mode` is persisted in the case payload, and the analysis script now visibly reminds the reader that probe modality exists.

Assessment: acceptable Phase B fix, though a follow-up `period × cpt_mode` table would make it stronger.

## Cross-Bug Notes

### What the implementation got right

- It did not "fix around" the audit. The live mechanisms named by the audit are the ones it actually changed.
- Bug 3 was fixed using the best-compatible design: enum classification plus strict compatibility fields.
- Bug 4 and Bug 5 were treated together in a sensible way: adding a validator while also preferring missingness over hidden modality fallback.
- Bug 2 was handled as reporting, not by changing the scoring math.

### Residual risks worth noting

- `src/metrics.py::cfls_per_case()` still contains the stale duplicate FO-flip bool logic. The live v3 pipeline overrides it, so this is not a current scoring mismatch, but it is cleanup debt.
- `src/masking.py::check_negation_polarity_flipped()` is intentionally cheap and permissive. It reduces the risk substantially, but it does not prove semantic inversion.
- `scripts/quick_stats.py` now acknowledges `cpt_mode`, but it still stops short of a full `period × cpt_mode` analysis table.
- The checked-in `data/results/diagnostic_2_results.json` predates `4421da2`, so the repository artifact does not yet reflect the new output fields. That is an operational note, not a code-level rejection reason.

## Verdict

I would not ask for a redesign before merging this.

Reasons:

- Bug 1 is fixed exactly.
- Bug 2 is fixed at the correct layer and with more visibility than strictly required.
- Bug 3 is fixed using the strongest reasonable variant and preserves backward compatibility.
- Bug 4 fixes the real acceptance-hole on both code paths, even though the validator is heuristic.
- Bug 5 does not eliminate the experimental confound, but it does the right Phase B thing: it surfaces the confound and avoids making it worse through silent fallback mixing.

The remaining issues are follow-up quality items, not evidence that the audited mechanisms were missed.

Verdict: PASS
